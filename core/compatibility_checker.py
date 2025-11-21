"""
Compatibility Checker for Package Versions

Validates package version combinations against known conflicts and compatibility matrices.
Provides LTS recommendations and auto-fix suggestions.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class VersionConstraint:
    """Represents a semantic version constraint."""
    operator: str  # ^, ~, >=, <=, ==, etc.
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, version_string: str) -> "VersionConstraint":
        """Parse version string like '^18.2.0' or '>=5.0.0'."""
        # Extract operator
        match = re.match(r'^([~^>=<]+)?([\d.]+)', version_string)
        if not match:
            raise ValueError(f"Invalid version string: {version_string}")

        operator = match.group(1) or "=="
        version_parts = match.group(2).split('.')

        major = int(version_parts[0]) if len(version_parts) > 0 else 0
        minor = int(version_parts[1]) if len(version_parts) > 1 else 0
        patch = int(version_parts[2]) if len(version_parts) > 2 else 0

        return cls(operator=operator, major=major, minor=minor, patch=patch)

    def satisfies(self, other: "VersionConstraint") -> bool:
        """Check if this version satisfies the other constraint."""
        if self.operator == "^":
            # Caret: same major, >= minor.patch
            return (
                self.major == other.major and
                (self.minor > other.minor or
                 (self.minor == other.minor and self.patch >= other.patch))
            )
        elif self.operator == "~":
            # Tilde: same major.minor, >= patch
            return (
                self.major == other.major and
                self.minor == other.minor and
                self.patch >= other.patch
            )
        elif self.operator == ">=":
            return (
                self.major > other.major or
                (self.major == other.major and self.minor > other.minor) or
                (self.major == other.major and self.minor == other.minor and
                 self.patch >= other.patch)
            )
        else:  # ==
            return (
                self.major == other.major and
                self.minor == other.minor and
                self.patch == other.patch
            )


@dataclass
class CompatibilityIssue:
    """Represents a compatibility issue found."""
    severity: str  # critical, high, medium, low
    package: str
    current_version: str
    issue_description: str
    suggested_fix: dict[str, str] | None = None
    migration_url: str | None = None


class CompatibilityChecker:
    """Checks package compatibility and suggests LTS versions."""

    def __init__(self):
        self.core_dir = Path(__file__).parent
        self.lts_versions = self._load_json("lts_versions.json")
        self.breaking_changes = self._load_json("breaking_changes.json")

    def _load_json(self, filename: str) -> dict[str, Any]:
        """Load JSON configuration file."""
        path = self.core_dir / filename
        if not path.exists():
            return {}
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    def get_lts_version(self, package: str) -> str | None:
        """Get recommended LTS version for a package."""
        pkg_data = self.lts_versions.get(package)
        if not pkg_data:
            return None
        return pkg_data.get("recommended")

    def get_known_good_stack(self, stack_name: str) -> dict[str, str] | None:
        """Get a known-good version stack by name."""
        stacks = self.lts_versions.get("known_good_stacks", [])
        for stack in stacks:
            if stack_name.lower() in stack["name"].lower():
                return stack["versions"]
        return None

    def check_breaking_changes(
        self,
        package: str,
        from_version: str,
        to_version: str
    ) -> list[dict[str, Any]]:
        """Check for breaking changes between versions."""
        changes_list = self.breaking_changes.get("breaking_changes", [])

        from_major = int(from_version.split('.')[0])
        to_major = int(to_version.split('.')[0])

        relevant_changes = []
        for change in changes_list:
            if change["package"] != package:
                continue

            change_from = int(change["from_version"].split('.')[0])
            change_to = int(change["to_version"].split('.')[0])

            # Check if this breaking change affects the version range
            if change_from <= from_major < to_major <= change_to:
                relevant_changes.append(change)

        return relevant_changes

    def check_peer_dependencies(
        self,
        package: str,
        version: str,
        installed_packages: dict[str, str]
    ) -> list[CompatibilityIssue]:
        """Check if peer dependencies are satisfied."""
        issues = []

        peer_reqs = self.breaking_changes.get("peer_dependency_requirements", {})
        if package not in peer_reqs:
            return issues

        req = peer_reqs[package]
        required_peers = req.get("required_peers", [])

        for peer in required_peers:
            if peer not in installed_packages:
                issues.append(CompatibilityIssue(
                    severity="critical",
                    package=package,
                    current_version=version,
                    issue_description=f"Missing required peer dependency: {peer}",
                    suggested_fix={peer: self.get_lts_version(peer) or "latest"}
                ))

        # Check version constraints
        version_constraints = req.get("version_constraints", {})
        pkg_major = version.split('.')[0] + ".x"

        if pkg_major in version_constraints:
            constraints = version_constraints[pkg_major]
            for peer, constraint in constraints.items():
                if peer in installed_packages:
                    installed_ver = installed_packages[peer]
                    if not self._version_satisfies_constraint(installed_ver, constraint):
                        issues.append(CompatibilityIssue(
                            severity="high",
                            package=peer,
                            current_version=installed_ver,
                            issue_description=(
                                f"{package}@{version} requires {peer} {constraint}, "
                                f"but {installed_ver} is installed"
                            ),
                            suggested_fix={peer: constraint.replace('^', '').replace('~', '')}
                        ))

        return issues

    def _version_satisfies_constraint(self, version: str, constraint: str) -> bool:
        """Check if version satisfies constraint."""
        try:
            ver = VersionConstraint.parse(version)
            con = VersionConstraint.parse(constraint)
            return ver.satisfies(con)
        except Exception:
            return True  # Assume satisfied if parsing fails

    def find_conflicts(
        self,
        packages: dict[str, str]
    ) -> list[CompatibilityIssue]:
        """Find known conflicts in package combination."""
        issues = []

        conflicts = self.breaking_changes.get("conflict_resolutions", [])

        for conflict in conflicts:
            # Parse conflict description to check if it applies
            conflict_desc = conflict["conflict"]

            # Simple pattern matching for common conflicts
            if "Next.js 15" in conflict_desc and "React" in conflict_desc:
                next_ver = packages.get("next", "")
                react_ver = packages.get("react", "")

                if next_ver.startswith("15.") and react_ver.startswith("18.2"):
                    issues.append(CompatibilityIssue(
                        severity=conflict["severity"],
                        package="react",
                        current_version=react_ver,
                        issue_description=conflict["reason"],
                        suggested_fix=conflict.get("fix_versions")
                    ))

            elif "Prisma 5" in conflict_desc and "Node.js" in conflict_desc:
                prisma_ver = packages.get("prisma", "")
                if prisma_ver.startswith("5."):
                    # Would need Node.js version check here
                    # For now, just suggest the fix
                    issues.append(CompatibilityIssue(
                        severity=conflict["severity"],
                        package="prisma",
                        current_version=prisma_ver,
                        issue_description=conflict["reason"],
                        suggested_fix=conflict.get("fix_versions")
                    ))

            elif "NextAuth 5" in conflict_desc:
                nextauth_ver = packages.get("next-auth", "")
                if nextauth_ver.startswith("5."):
                    issues.append(CompatibilityIssue(
                        severity=conflict["severity"],
                        package="next-auth",
                        current_version=nextauth_ver,
                        issue_description=conflict["reason"],
                        suggested_fix=conflict.get("fix_versions")
                    ))

        return issues

    def validate_package_json(
        self,
        package_json: dict[str, Any]
    ) -> tuple[bool, list[CompatibilityIssue]]:
        """Validate entire package.json for compatibility issues."""
        issues = []

        dependencies = {
            **package_json.get("dependencies", {}),
            **package_json.get("devDependencies", {})
        }

        # Clean version strings (remove ^, ~, etc. for comparison)
        clean_deps = {
            pkg: ver.lstrip('^~>=<')
            for pkg, ver in dependencies.items()
        }

        # Check for known conflicts
        issues.extend(self.find_conflicts(clean_deps))

        # Check peer dependencies for major packages
        major_packages = ["next", "react", "prisma", "next-auth"]
        for pkg in major_packages:
            if pkg in clean_deps:
                issues.extend(
                    self.check_peer_dependencies(pkg, clean_deps[pkg], clean_deps)
                )

        is_valid = all(issue.severity != "critical" for issue in issues)

        return is_valid, issues

    def suggest_lts_versions(
        self,
        requested_packages: list[str],
        prefer_stack: str | None = None
    ) -> dict[str, str]:
        """Suggest LTS versions for requested packages."""
        if prefer_stack:
            stack = self.get_known_good_stack(prefer_stack)
            if stack:
                return {
                    pkg: stack[pkg]
                    for pkg in requested_packages
                    if pkg in stack
                }

        # Fallback to individual LTS versions
        suggestions = {}
        for pkg in requested_packages:
            lts_ver = self.get_lts_version(pkg)
            if lts_ver:
                suggestions[pkg] = lts_ver

        return suggestions


def main():
    """CLI for testing compatibility checker."""
    checker = CompatibilityChecker()

    # Example: Check a package.json
    test_package_json = {
        "dependencies": {
            "next": "15.0.0",
            "react": "18.2.0",
            "react-dom": "18.2.0",
            "prisma": "5.8.0",
            "next-auth": "4.24.5"
        }
    }

    is_valid, issues = checker.validate_package_json(test_package_json)

    print(f"Validation: {'✅ PASS' if is_valid else '❌ FAIL'}")
    print(f"\nIssues found: {len(issues)}")

    for issue in issues:
        print(f"\n[{issue.severity.upper()}] {issue.package}@{issue.current_version}")
        print(f"  {issue.issue_description}")
        if issue.suggested_fix:
            print(f"  Suggested fix: {issue.suggested_fix}")


if __name__ == "__main__":
    main()

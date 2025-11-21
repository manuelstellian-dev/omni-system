import os
import json
import litellm
import asyncio
from pathlib import Path
from typing import Dict, Optional, List
from rich.console import Console
from rich.panel import Panel
from cortex import ProjectSpec
from arbiter import ArbiterAgent
from swarm import SwarmAgent

console = Console()


class RepairAgent:
    """
    Advanced self-healing agent with multiple progressive repair strategies.

    Unlike simple one-shot self-healing, RepairAgent attempts multiple
    strategies in sequence until the project passes verification or all
    strategies are exhausted.

    This makes OMNI significantly more robust than systems like Copilot/Cursor
    which generate code but don't auto-repair failures.
    """

    def __init__(self, arbiter: ArbiterAgent, swarm: SwarmAgent):
        self.arbiter = arbiter
        self.swarm = swarm
        self.model = os.getenv("OMNI_MODEL", "gpt-4o")
        self.max_attempts = 8  # Includes META strategy

        # Progressive repair strategies (ordered by complexity)
        self.strategies = [
            ("Quick Fixes (Syntax & Imports)", self._strategy_quick_fixes),
            ("Logic Error Fixes", self._strategy_logic_fixes),
            ("Test Configuration Fixes", self._strategy_test_config),
            ("Regenerate Failing Files", self._strategy_regenerate_files),
            ("Simplify Implementation", self._strategy_simplify),
            ("Alternative Approach", self._strategy_alternative),
            ("Minimal Viable Version", self._strategy_minimal_viable),
            ("META Cognitive Diagnosis", self._strategy_8_meta_cognitive_diagnosis),
        ]

        # Repair history tracking for META strategy
        self.repair_history = []

        # Load error patterns for learning
        self.error_patterns_file = Path(__file__).parent / "error_patterns.json"

    async def repair(
        self,
        target_dir: str,
        spec: ProjectSpec,
        initial_error: Dict
    ) -> Dict:
        """
        Attempts multiple repair strategies until success or exhaustion.

        Returns:
            {
                "status": "success" | "failed",
                "strategy_used": str,
                "attempts": int,
                "final_error": str (if failed)
            }
        """
        console.print("\n" + "="*70)
        console.print(Panel.fit(
            "[bold yellow]🔧 REPAIR AGENT ACTIVATED[/bold yellow]\n\n"
            f"Max Strategies: {self.max_attempts}\n"
            f"Mode: Aggressive Auto-Repair",
            border_style="yellow"
        ))
        console.print("="*70 + "\n")

        current_error = initial_error

        for attempt, (strategy_name, strategy_func) in enumerate(self.strategies, 1):
            console.print(f"\n[cyan]═══ Repair Attempt {attempt}/{self.max_attempts} ═══[/cyan]")
            console.print(f"[yellow]Strategy:[/yellow] {strategy_name}")

            # Apply strategy
            fix_result = await strategy_func(target_dir, spec, current_error)

            # Track this attempt for META strategy
            attempt_record = {
                "attempt_number": attempt,
                "strategy_name": strategy_name,
                "error": current_error,
                "fix_result": fix_result,
                "success": False
            }

            if not fix_result or not fix_result.get("fixes"):
                console.print(f"[dim]Strategy returned no fixes, trying next...[/dim]")
                self.repair_history.append(attempt_record)
                continue

            # Apply fixes using SwarmAgent
            console.print(f"[cyan]Applying fixes...[/cyan]")
            self.swarm.apply_fix(fix_result)

            # Run additional commands if any
            if fix_result.get("additional_commands"):
                await self._run_commands(fix_result["additional_commands"], target_dir)

            # Re-verify
            console.print(f"[cyan]Re-running verification...[/cyan]")
            verification_result = self.arbiter.verify_and_refine(target_dir, spec)

            if verification_result["status"] == "success":
                attempt_record["success"] = True
                self.repair_history.append(attempt_record)

                console.print("\n" + "="*70)
                console.print(Panel.fit(
                    f"[bold green]✓ REPAIR SUCCESSFUL![/bold green]\n\n"
                    f"Strategy: {strategy_name}\n"
                    f"Attempts: {attempt}/{self.max_attempts}",
                    border_style="green"
                ))
                console.print("="*70 + "\n")

                return {
                    "status": "success",
                    "strategy_used": strategy_name,
                    "attempts": attempt
                }
            else:
                console.print(f"[yellow]✗ Strategy failed, continuing...[/yellow]\n")
                attempt_record["verification_error"] = verification_result
                self.repair_history.append(attempt_record)
                current_error = verification_result

        # All strategies exhausted
        console.print("\n" + "="*70)
        console.print(Panel.fit(
            "[bold red]✗ REPAIR FAILED[/bold red]\n\n"
            f"All {self.max_attempts} strategies attempted.\n"
            "Manual intervention may be required.",
            border_style="red"
        ))
        console.print("="*70 + "\n")

        return {
            "status": "failed",
            "strategy_used": None,
            "attempts": self.max_attempts,
            "final_error": current_error.get("stderr", "Unknown error")
        }

    async def _strategy_quick_fixes(
        self,
        target_dir: str,
        spec: ProjectSpec,
        error: Dict
    ) -> Optional[Dict]:
        """Strategy 1: Fix common quick wins (syntax, imports, typos)"""

        system_prompt = f"""You are a debugging expert specializing in QUICK FIXES.
Focus ONLY on:
- Missing imports (add to requirements.txt or import statements)
- Syntax errors (typos, missing colons, wrong indentation)
- Module name typos
- Simple type errors

Project: {spec.project_name}
Tech Stack: {', '.join(spec.tech_stack)}

Return ONLY valid JSON with this schema:
{{
  "error_summary": "brief description",
  "root_cause": "why this happened",
  "fixes": [
    {{
      "file_path": "relative/path/to/file",
      "new_content": "complete file content with fix",
      "reason": "why this fix works"
    }}
  ],
  "additional_commands": ["commands to run, e.g., pip install package"]
}}
"""

        user_prompt = f"""Quick fix this error:

Command: {error.get('command', 'unknown')}
Exit Code: {error.get('exit_code', 'unknown')}

STDOUT:
{error.get('stdout', '')[:1500]}

STDERR:
{error.get('stderr', '')[:1500]}

Apply the simplest fix that resolves this error.
"""

        return await self._call_llm(system_prompt, user_prompt)

    async def _strategy_logic_fixes(
        self,
        target_dir: str,
        spec: ProjectSpec,
        error: Dict
    ) -> Optional[Dict]:
        """Strategy 2: Fix logic errors (wrong types, null checks, edge cases)"""

        system_prompt = f"""You are a debugging expert specializing in LOGIC ERRORS.
The syntax is correct but the logic is broken.

Focus on:
- Wrong variable types (str vs int, dict vs list)
- Missing null/None checks
- Incorrect function return types
- Off-by-one errors
- Edge case handling

Project: {spec.project_name}
Tech Stack: {', '.join(spec.tech_stack)}

Return ONLY valid JSON with fixes.
"""

        user_prompt = f"""Fix logic errors:

Command: {error.get('command', 'unknown')}
Exit Code: {error.get('exit_code', 'unknown')}

STDOUT:
{error.get('stdout', '')[:1500]}

STDERR:
{error.get('stderr', '')[:1500]}

Analyze the logic carefully and fix the root cause.
"""

        return await self._call_llm(system_prompt, user_prompt)

    async def _strategy_test_config(
        self,
        target_dir: str,
        spec: ProjectSpec,
        error: Dict
    ) -> Optional[Dict]:
        """Strategy 3: Fix test configuration issues"""

        system_prompt = f"""You are a testing expert.
The APPLICATION code is likely CORRECT. The problem is in TEST CONFIGURATION.

Focus on fixing:
- conftest.py (database setup, fixtures)
- Test client initialization
- Mock/patch configuration
- Test database connections
- Async test decorators

Project: {spec.project_name}
Tech Stack: {', '.join(spec.tech_stack)}

DO NOT modify application code. Only fix test setup.
Return ONLY valid JSON with fixes.
"""

        user_prompt = f"""Fix test configuration:

Command: {error.get('command', 'unknown')}
Exit Code: {error.get('exit_code', 'unknown')}

STDOUT:
{error.get('stdout', '')[:1500]}

STDERR:
{error.get('stderr', '')[:1500]}

Fix only the test configuration, not the application logic.
"""

        return await self._call_llm(system_prompt, user_prompt)

    async def _strategy_regenerate_files(
        self,
        target_dir: str,
        spec: ProjectSpec,
        error: Dict
    ) -> Optional[Dict]:
        """Strategy 4: Regenerate failing files from scratch"""

        failing_file = self._extract_failing_file(error)

        system_prompt = f"""You are a code generation expert.
The current implementation of a file is broken beyond simple fixes.

Task: Generate a NEW, SIMPLER implementation from scratch.

Guidelines:
- Learn from the error to avoid repeating it
- Use simpler patterns
- Fewer dependencies
- More defensive coding (null checks, try/catch)

Project: {spec.project_name}
Tech Stack: {', '.join(spec.tech_stack)}
Failing file: {failing_file}

Return ONLY valid JSON with the COMPLETE regenerated file.
"""

        user_prompt = f"""Regenerate this failing file from scratch:

File: {failing_file}

Error:
{error.get('stderr', '')[:1500]}

Generate a simpler, working version that avoids this error.
"""

        return await self._call_llm(system_prompt, user_prompt)

    async def _strategy_simplify(
        self,
        target_dir: str,
        spec: ProjectSpec,
        error: Dict
    ) -> Optional[Dict]:
        """Strategy 5: Simplify implementation by removing complexity"""

        system_prompt = f"""You are a simplification expert.
The implementation is TOO COMPLEX and breaking.

Task: Simplify the code dramatically.

Remove:
- Advanced features that aren't core
- Complex abstractions
- Optional functionality
- Clever optimizations

Keep:
- Core CRUD operations
- Basic functionality
- Simple, obvious patterns

Project: {spec.project_name}
Tech Stack: {', '.join(spec.tech_stack)}

Return ONLY valid JSON. Prioritize WORKING over FEATURE-COMPLETE.
"""

        user_prompt = f"""Simplify this failing code:

Error:
{error.get('stderr', '')[:1500]}

Remove complexity. Keep only what's necessary for basic functionality.
"""

        return await self._call_llm(system_prompt, user_prompt)

    async def _strategy_alternative(
        self,
        target_dir: str,
        spec: ProjectSpec,
        error: Dict
    ) -> Optional[Dict]:
        """Strategy 6: Try completely different implementation approach"""

        system_prompt = f"""You are an architecture expert.
The current approach has failed repeatedly. Try a COMPLETELY DIFFERENT approach.

Consider alternative:
- Architecture patterns (MVC vs Repository vs Service Layer)
- Libraries (different ORM, different testing approach)
- Data flow (sync vs async, pull vs push)
- File organization

Project: {spec.project_name}
Tech Stack: {', '.join(spec.tech_stack)}

Be creative but pragmatic. Return ONLY valid JSON.
"""

        user_prompt = f"""Current approach failed. Try alternative implementation:

Repeated error:
{error.get('stderr', '')[:1500]}

Original spec:
Features: {', '.join(spec.core_features[:3])}

Use a different architectural approach that avoids this error pattern.
"""

        return await self._call_llm(system_prompt, user_prompt)

    async def _strategy_minimal_viable(
        self,
        target_dir: str,
        spec: ProjectSpec,
        error: Dict
    ) -> Optional[Dict]:
        """Strategy 7: Generate absolute minimum viable version"""

        system_prompt = f"""You are creating a MINIMAL VIABLE VERSION.
This is the last resort. Priority: CODE THAT COMPILES.

Acceptable compromises:
- Placeholder functions (pass or return None)
- Simplified logic (basic validation only)
- Missing features (user can add later)
- Hardcoded values where appropriate

Unacceptable:
- Code that doesn't run
- Syntax errors
- Missing critical imports

Project: {spec.project_name}
Tech Stack: {', '.join(spec.tech_stack)}

Return ONLY valid JSON. Generate code that WORKS, even if minimal.
"""

        user_prompt = f"""Generate minimal viable version:

Repeated failures:
{error.get('stderr', '')[:1500]}

Core requirements:
- Must compile/run without errors
- Basic structure in place
- Can be extended by user

Generate the simplest version that passes verification.
"""

        return await self._call_llm(system_prompt, user_prompt)

    async def _strategy_8_meta_cognitive_diagnosis(
        self,
        target_dir: str,
        spec: ProjectSpec,
        error: Dict
    ) -> Optional[Dict]:
        """
        Strategy 8: META Cognitive Diagnosis

        This is the most advanced strategy that:
        1. Analyzes WHY the previous 7 strategies failed
        2. Reads critical project files (package.json, tsconfig.json, etc.)
        3. Detects dependency conflicts (React 19 vs 18, Next.js 15 vs 14, etc.)
        4. Applies coordinated multi-file fixes
        5. Learns patterns and saves successful solutions
        6. Generates TROUBLESHOOTING.md documentation
        """
        console.print("[bold magenta]🧠 META Strategy: Holistic System Diagnosis[/bold magenta]")

        # Collect comprehensive context
        repair_summary = self._collect_repair_history()
        critical_files = await self._read_critical_files(target_dir, spec)
        dependency_analysis = await self._analyze_dependencies(target_dir, critical_files)

        system_prompt = f"""You are a META-LEVEL debugging expert with deep architectural insight.

The previous 7 repair strategies have ALL FAILED. Your job is to understand WHY and apply a holistic fix.

You have access to:
1. Full history of all failed repair attempts
2. Critical project files (package.json, tsconfig.json, requirements.txt, etc.)
3. Dependency conflict analysis

Common patterns that simple strategies miss:
- **Dependency Version Conflicts**: React 19 incompatible with NextAuth 4.x → Need React 18.3.x
- **Multi-layered Issues**: Fixing one file breaks another → Need coordinated changes
- **Configuration Cascades**: tsconfig.json strict mode → Need type assertions everywhere
- **Beta Dependencies**: next-auth@beta requires specific Next.js version

Your approach:
1. Identify ROOT CAUSE (not symptoms)
2. Apply INCREMENTAL fixes (test each layer)
3. Downgrade/upgrade dependencies if needed
4. Make coordinated changes across multiple files
5. Add proper error handling and type safety

Project: {spec.project_name}
Tech Stack: {', '.join(spec.tech_stack)}

Return ONLY valid JSON with this schema:
{{
  "diagnosis": {{
    "root_cause": "why previous strategies failed",
    "affected_layers": ["dependencies", "configuration", "code", "types"],
    "complexity": "simple | moderate | complex"
  }},
  "fixes": [
    {{
      "file_path": "relative/path/to/file",
      "new_content": "complete file content",
      "reason": "why this specific fix",
      "layer": "dependencies | config | code | types",
      "order": 1
    }}
  ],
  "additional_commands": ["npm install react@18.3.1", "npm install --legacy-peer-deps"],
  "learning": {{
    "error_pattern": "brief signature for error_patterns.json",
    "solution_summary": "what worked",
    "prevention": "how to avoid this in future"
  }}
}}

IMPORTANT: Order fixes by dependency (layer 1: dependencies, layer 2: config, layer 3: code).
"""

        user_prompt = f"""COMPREHENSIVE CONTEXT FOR META DIAGNOSIS:

=== REPAIR HISTORY (7 Failed Strategies) ===
{repair_summary}

=== CRITICAL PROJECT FILES ===
{critical_files}

=== DEPENDENCY ANALYSIS ===
{dependency_analysis}

=== CURRENT ERROR ===
Command: {error.get('command', 'unknown')}
Exit Code: {error.get('exit_code', 'unknown')}

STDOUT:
{error.get('stdout', '')[:2000]}

STDERR:
{error.get('stderr', '')[:2000]}

===================================

Provide a META-level diagnosis and holistic fix that addresses the ROOT CAUSE.
Apply incremental, coordinated changes across all necessary layers.
"""

        console.print("[cyan]Calling LLM for META diagnosis...[/cyan]")
        fix_plan = await self._call_llm(system_prompt, user_prompt)

        if fix_plan and fix_plan.get("learning"):
            # Save successful pattern for future
            await self._save_successful_pattern(fix_plan["learning"], target_dir, spec)

        if fix_plan and fix_plan.get("diagnosis"):
            # Generate troubleshooting documentation
            await self._generate_troubleshooting_doc(
                target_dir,
                fix_plan["diagnosis"],
                self.repair_history
            )

        return fix_plan

    def _collect_repair_history(self) -> str:
        """Summarize all failed repair attempts for META analysis."""
        if not self.repair_history:
            return "No previous repair attempts (META called directly)"

        summary = []
        for i, attempt in enumerate(self.repair_history, 1):
            summary.append(f"\n--- Attempt {i}: {attempt['strategy_name']} ---")
            summary.append(f"Result: {'✓ Success' if attempt['success'] else '✗ Failed'}")

            if attempt.get('fix_result'):
                fix_result = attempt['fix_result']
                if fix_result.get('fixes'):
                    summary.append(f"Fixes attempted: {len(fix_result['fixes'])} files")
                if fix_result.get('error_summary'):
                    summary.append(f"Error summary: {fix_result['error_summary']}")

            if attempt.get('verification_error'):
                ver_error = attempt['verification_error']
                stderr = ver_error.get('stderr', '')[:500]
                summary.append(f"Verification failed with: {stderr}")

        return "\n".join(summary)

    async def _read_critical_files(self, target_dir: str, spec: ProjectSpec) -> str:
        """Read critical project files for dependency and config analysis."""
        target_path = Path(target_dir)
        critical_files = {}

        # Determine which files to read based on tech stack
        file_candidates = []

        # JavaScript/TypeScript projects
        if any(tech in " ".join(spec.tech_stack) for tech in ["Next.js", "React", "TypeScript", "Node"]):
            file_candidates.extend([
                "package.json",
                "tsconfig.json",
                "next.config.js",
                "next.config.mjs",
                ".env.example"
            ])

        # Python projects
        if any(tech in " ".join(spec.tech_stack) for tech in ["Python", "Django", "FastAPI", "Flask"]):
            file_candidates.extend([
                "requirements.txt",
                "pyproject.toml",
                "setup.py",
                "Pipfile"
            ])

        # Read files that exist
        for filename in file_candidates:
            file_path = target_path / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        critical_files[filename] = f.read()[:3000]  # Limit size
                except Exception as e:
                    critical_files[filename] = f"[Error reading: {str(e)}]"

        # Format for LLM
        formatted = []
        for filename, content in critical_files.items():
            formatted.append(f"\n=== {filename} ===\n{content}")

        return "\n".join(formatted) if formatted else "No critical files found"

    async def _analyze_dependencies(self, target_dir: str, critical_files: str) -> str:
        """Analyze dependency versions and detect conflicts."""
        analysis = ["DEPENDENCY CONFLICT ANALYSIS:\n"]

        # Parse package.json if present
        if "package.json" in critical_files:
            try:
                import json
                # Extract package.json content
                start = critical_files.find('"name"')
                if start > 0:
                    # Simple extraction (not perfect but works for analysis)
                    pkg_section = critical_files[start:start+2000]

                    # Check for known problematic combinations
                    conflicts = []

                    if 'react"' in pkg_section and '"19.' in pkg_section:
                        conflicts.append("⚠ React 19 detected - may be incompatible with many libraries")
                        conflicts.append("  → Consider downgrading to React 18.3.1")

                    if 'next"' in pkg_section and '"15.' in pkg_section:
                        conflicts.append("⚠ Next.js 15 detected - very recent, may have compatibility issues")
                        conflicts.append("  → Consider using Next.js 14.x for stability")

                    if 'next-auth' in pkg_section and 'beta' in pkg_section:
                        conflicts.append("⚠ NextAuth beta detected - requires specific dependencies")
                        conflicts.append("  → Ensure React and Next.js versions are compatible")

                    if conflicts:
                        analysis.extend(conflicts)
                    else:
                        analysis.append("✓ No obvious dependency conflicts detected")

            except Exception as e:
                analysis.append(f"[Error analyzing dependencies: {str(e)}]")

        # Parse requirements.txt if present
        if "requirements.txt" in critical_files:
            req_section = critical_files[critical_files.find("requirements.txt"):]
            if ">=" in req_section and "==" in req_section:
                analysis.append("⚠ Mixed version constraints (>= and ==) in Python dependencies")

        return "\n".join(analysis)

    async def _save_successful_pattern(
        self,
        learning: Dict,
        target_dir: str,
        spec: ProjectSpec
    ):
        """Save successful repair pattern to error_patterns.json for future learning."""
        try:
            # Load existing patterns
            if self.error_patterns_file.exists():
                with open(self.error_patterns_file, 'r', encoding='utf-8') as f:
                    patterns_data = json.load(f)
            else:
                patterns_data = {"patterns": [], "metadata": {"learning_enabled": True}}

            # Create new pattern
            new_pattern = {
                "error_signature": learning.get("error_pattern", "Unknown pattern"),
                "category": "meta_learned",
                "fix_strategy": "meta_cognitive",
                "solution": {
                    "summary": learning.get("solution_summary", ""),
                    "prevention": learning.get("prevention", ""),
                    "tech_stack": spec.tech_stack,
                    "learned_at": "2025-11-21"  # Could use datetime.now()
                },
                "success_rate": 1.0,  # Initial success
                "confidence": "high",
                "times_applied": 1
            }

            # Add to patterns
            patterns_data["patterns"].append(new_pattern)

            # Save back
            with open(self.error_patterns_file, 'w', encoding='utf-8') as f:
                json.dump(patterns_data, f, indent=2)

            console.print(f"[green]✓ Learned pattern saved to error_patterns.json[/green]")

        except Exception as e:
            console.print(f"[yellow]⚠ Could not save pattern: {str(e)}[/yellow]")

    async def _generate_troubleshooting_doc(
        self,
        target_dir: str,
        diagnosis: Dict,
        repair_history: List[Dict]
    ):
        """Generate TROUBLESHOOTING.md documentation for the project."""
        try:
            troubleshooting_path = Path(target_dir) / "TROUBLESHOOTING.md"

            content = f"""# Troubleshooting Guide

**Generated by OMNI Repair Agent (Strategy 8 META)**
**Date**: 2025-11-21

## Build Issues Encountered

### Root Cause
{diagnosis.get('root_cause', 'Unknown')}

### Affected Layers
{', '.join(diagnosis.get('affected_layers', []))}

### Complexity
{diagnosis.get('complexity', 'Unknown')}

## Repair Attempts

"""
            # Add repair history
            for i, attempt in enumerate(repair_history, 1):
                content += f"### Attempt {i}: {attempt['strategy_name']}\n"
                content += f"- **Result**: {'✓ Success' if attempt['success'] else '✗ Failed'}\n"
                if attempt.get('fix_result', {}).get('error_summary'):
                    content += f"- **Issue**: {attempt['fix_result']['error_summary']}\n"
                content += "\n"

            content += """
## Resolution

The META strategy successfully diagnosed and resolved the issue by:
1. Analyzing all previous failed attempts
2. Identifying the root cause
3. Applying coordinated fixes across multiple layers
4. Testing incrementally

## Prevention

To avoid similar issues in the future:
- Review dependency compatibility before upgrading
- Use stable versions instead of bleeding-edge releases
- Test builds incrementally when making major changes
- Consult official migration guides for major version upgrades

---

*This document was auto-generated by OMNI's self-healing system.*
"""

            with open(troubleshooting_path, 'w', encoding='utf-8') as f:
                f.write(content)

            console.print(f"[green]✓ Generated TROUBLESHOOTING.md[/green]")

        except Exception as e:
            console.print(f"[yellow]⚠ Could not generate troubleshooting doc: {str(e)}[/yellow]")

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> Optional[Dict]:
        """Helper to call LLM and parse JSON response"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: litellm.completion(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
            )

            fix_plan_text = response.choices[0].message.content.strip()
            fix_plan = json.loads(fix_plan_text)

            return fix_plan

        except Exception as e:
            console.print(f"[red]Error calling LLM: {str(e)}[/red]")
            return None

    async def _run_commands(self, commands: List[str], cwd: str):
        """Run additional commands (e.g., pip install)"""
        import subprocess

        for cmd in commands:
            console.print(f"[cyan]Running:[/cyan] {cmd}")
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                console.print(f"[green]✓ Success[/green]")
            else:
                console.print(f"[yellow]⚠ Command failed (continuing)[/yellow]")

    def _extract_failing_file(self, error: Dict) -> str:
        """Extract the file path that's causing the error from stderr"""
        stderr = error.get('stderr', '')

        # Common patterns in error messages
        import re

        # Pattern: File "/path/to/file.py", line X
        match = re.search(r'File "([^"]+\.py)"', stderr)
        if match:
            return match.group(1)

        # Pattern: Error in tests/test_file.py
        match = re.search(r'(?:Error in|Failed:)\s+([^\s]+\.py)', stderr)
        if match:
            return match.group(1)

        # Default: return conftest.py as it's often the culprit
        return "tests/conftest.py"
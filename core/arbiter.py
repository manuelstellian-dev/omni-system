import os
import subprocess
import tempfile
import litellm
import json
from pathlib import Path
from typing import Dict, Optional
from rich.console import Console
from cortex import ProjectSpec
from compatibility_checker import CompatibilityChecker


console = Console()


class ArbiterAgent:
    def __init__(self):
        self.model = os.getenv("OMNI_MODEL", "gpt-4o")
        self.sandbox_dir = tempfile.mkdtemp(prefix="omni_sandbox_")
        self.compatibility_checker = CompatibilityChecker()
        self.build_commands = {
            "nextjs": ["npm install", "npm run build"],
            "react": ["npm install", "npm run build"],
            "typescript": ["npm install", "npx tsc --noEmit"],
            "javascript": ["npm install", "npm test"],
            "python": ["pip install -r requirements.txt", "python3 -m pytest"],
            "fastapi": ["pip install -r requirements.txt", "python3 -m pytest"],
        }

    def verify_and_refine(self, target_dir: str, spec: ProjectSpec) -> Dict:
        """
        Verifies the built project by running build/test commands.
        Now includes compatibility checking BEFORE build commands.
        If failures occur, uses LLM to generate a FIX_PLAN.
        """
        target_path = Path(target_dir).resolve()

        if not target_path.exists():
            return {
                "status": "error",
                "message": f"Target directory does not exist: {target_dir}"
            }

        console.print(f"\n[bold yellow]Arbiter: Verifying project...[/bold yellow]")
        console.print(f"[dim]Target: {target_path}[/dim]\n")

        # PHASE 1: Compatibility Check BEFORE building
        console.print("[bold cyan]Phase 1: Checking package compatibility...[/bold cyan]")
        compat_result = self.compatibility_checker.check_project(str(target_path))
        
        if compat_result["status"] == "error":
            console.print(f"[bold red]✗ Compatibility check failed[/bold red]")
            return {
                "status": "failed",
                "phase": "compatibility_check",
                "compatibility_result": compat_result
            }
        
        if compat_result.get("issues"):
            console.print(f"[yellow]⚠ Found {len(compat_result['issues'])} compatibility issues[/yellow]")
            for issue in compat_result["issues"]:
                console.print(f"  • {issue['package']}: {issue['message']}")
            
            # Return early if critical issues found
            critical_issues = [i for i in compat_result["issues"] if i.get("severity") == "critical"]
            if critical_issues:
                console.print(f"[red]✗ {len(critical_issues)} CRITICAL issues must be resolved first[/red]")
                return {
                    "status": "failed",
                    "phase": "compatibility_check",
                    "compatibility_result": compat_result,
                    "critical_issues": critical_issues
                }
        else:
            console.print("[green]✓ No compatibility issues detected[/green]\n")

        # PHASE 2: Build commands
        console.print("[bold cyan]Phase 2: Running build commands...[/bold cyan]")
        commands = self._determine_build_commands(spec)

        for command in commands:
            console.print(f"[cyan]Running:[/cyan] {command}")

            result = self._run_command(command, str(target_path))

            if result["exit_code"] != 0:
                console.print(f"[red]✗ Build failed[/red]\n")
                console.print(f"[dim]Exit code: {result['exit_code']}[/dim]")

                fix_plan = self._generate_fix_plan(
                    command=command,
                    stdout=result["stdout"],
                    stderr=result["stderr"],
                    exit_code=result["exit_code"],
                    spec=spec
                )

                return {
                    "status": "failed",
                    "command": command,
                    "exit_code": result["exit_code"],
                    "stdout": result["stdout"],
                    "stderr": result["stderr"],
                    "fix_plan": fix_plan
                }
            else:
                console.print(f"[green]✓ Success[/green]\n")

        console.print(f"[bold green]Arbiter: All verifications passed![/bold green]\n")
        return {
            "status": "success",
            "message": "All build and test commands executed successfully."
        }

    def _determine_build_commands(self, spec: ProjectSpec) -> list:
        """
        Determines which build commands to run based on tech stack.
        """
        commands = []
        tech_lower = [tech.lower() for tech in spec.tech_stack]

        if "nextjs" in tech_lower or "next.js" in tech_lower:
            commands.extend(self.build_commands.get("nextjs", []))
        elif "react" in tech_lower:
            commands.extend(self.build_commands.get("react", []))
        elif "typescript" in tech_lower:
            commands.extend(self.build_commands.get("typescript", []))
        elif "javascript" in tech_lower:
            commands.extend(self.build_commands.get("javascript", []))

        if "python" in tech_lower or "fastapi" in tech_lower:
            commands.extend(self.build_commands.get("python", []))

        if not commands:
            commands = ["echo 'No build commands configured for this stack'"]

        return commands

    def _run_command(self, command: str, cwd: str) -> Dict:
        """
        Runs a shell command and captures stdout, stderr, and exit code.
        """
        try:
            process = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=600
            )

            return {
                "exit_code": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr
            }

        except subprocess.TimeoutExpired:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": "Command timed out after 600 seconds"
            }
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e)
            }

    def _generate_fix_plan(
        self,
        command: str,
        stdout: str,
        stderr: str,
        exit_code: int,
        spec: ProjectSpec
    ) -> Dict:
        """
        Uses LLM to analyze build errors and generate a structured FIX_PLAN.
        """
        console.print("[yellow]Analyzing errors with LLM...[/yellow]")

        system_prompt = f"""You are OMNI's Arbiter - an expert debugging agent.
Your role is to analyze build/test failures and produce a STRICT JSON FIX_PLAN.

Project: {spec.project_name}
Tech Stack: {', '.join(spec.tech_stack)}
Core Features: {', '.join(spec.core_features)}

CRITICAL RULES:
1. Output ONLY valid JSON, no markdown, no explanations.
2. Analyze the error carefully and provide actionable fixes.
3. For file content: NO COMMENTS in JSON files (.json). JSON does not support comments.
4. For file content: Output raw, valid code - no explanatory comments about changes.
5. The FIX_PLAN must follow this exact schema:
{{
  "error_summary": "brief description of the error",
  "root_cause": "explanation of why this error occurred",
  "fixes": [
    {{
      "file_path": "relative/path/to/file.ext",
      "new_content": "complete corrected file content (entire file, not just changed lines)",
      "reason": "why this fix is necessary"
    }}
  ],
  "additional_commands": ["any commands to run after fixes, e.g., npm install @tanstack/react-query"]
}}
"""

        user_prompt = f"""Build command failed:
Command: {command}
Exit Code: {exit_code}

STDOUT:
{stdout[:2000]}

STDERR:
{stderr[:2000]}

Generate the FIX_PLAN JSON now:"""

        try:
            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            fix_plan_text = response.choices[0].message.content.strip()
            fix_plan = json.loads(fix_plan_text)

            console.print("[green]✓ Fix plan generated[/green]")
            return fix_plan

        except Exception as e:
            console.print(f"[red]Error generating fix plan: {str(e)}[/red]")
            return {
                "error_summary": "Failed to generate fix plan",
                "root_cause": str(e),
                "fixes": [],
                "additional_commands": []
            }

    def cleanup(self):
        """Cleans up the sandbox directory."""
        import shutil
        if os.path.exists(self.sandbox_dir):
            shutil.rmtree(self.sandbox_dir)

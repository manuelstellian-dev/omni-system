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
        self.max_attempts = 7

        # Progressive repair strategies (ordered by complexity)
        self.strategies = [
            ("Quick Fixes (Syntax & Imports)", self._strategy_quick_fixes),
            ("Logic Error Fixes", self._strategy_logic_fixes),
            ("Test Configuration Fixes", self._strategy_test_config),
            ("Regenerate Failing Files", self._strategy_regenerate_files),
            ("Simplify Implementation", self._strategy_simplify),
            ("Alternative Approach", self._strategy_alternative),
            ("Minimal Viable Version", self._strategy_minimal_viable),
        ]

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

            if not fix_result or not fix_result.get("fixes"):
                console.print(f"[dim]Strategy returned no fixes, trying next...[/dim]")
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

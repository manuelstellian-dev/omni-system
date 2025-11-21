"""
OMNI Prompt Assembler

Eliminates LLM inconsistencies by constructing highly structured, specific prompts
that enforce the 'Opinionated Excellence' standard defined in the OMNI Manifesto.

This module ensures deterministic, production-grade output by providing
comprehensive context and explicit constraints to the LLM.
"""

from pathlib import Path
from typing import List


class PromptAssembler:
    def __init__(self):
        """Initialize the PromptAssembler with the OMNI Manifesto as the core constitution."""
        self.manifesto = self._load_manifesto()

    def _load_manifesto(self) -> str:
        """Load the OMNI Manifesto from disk."""
        manifesto_path = Path(__file__).parent / "00_MANIFESTO.md"
        try:
            with open(manifesto_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return """# OMNI MANIFESTO
## CORE PHILOSOPHY
* **Opinionated Excellence:** Enforce strictest standards (TypeScript Strict, ESLint Strict).
* **Self-Healing:** Never present broken state to user.
* **No Toys:** Full, robust implementation only. No emojis, no snippets.
* **Deterministic Output:** Predictable, production-grade results.
"""

    def assemble_swarm_prompt(
        self,
        task_description: str,
        project_files: List[str],
        required_dependencies: List[str]
    ) -> str:
        """
        Assembles a complete, highly specific prompt for the Swarm Agent.

        This prompt enforces OMNI's standards by including:
        1. The manifesto as system instruction
        2. Current project context (existing files)
        3. Critical dependencies that MUST be included
        4. The specific task to execute

        Args:
            task_description: The specific task to execute (e.g., "Write the Next.js page component for /dashboard")
            project_files: List of files that already exist in the project
            required_dependencies: List of npm packages that must be added to package.json

        Returns:
            A complete, structured prompt string
        """
        prompt_sections = []

        # Section 1: System Instruction (Manifesto)
        prompt_sections.append(f"""# SYSTEM INSTRUCTION: OMNI MANIFESTO

{self.manifesto}

---

YOU ARE THE SWARM AGENT - AN EXPERT FULL-STACK ENGINEER OPERATING UNDER THESE PRINCIPLES.
YOUR OUTPUT WILL BE USED DIRECTLY IN PRODUCTION. THERE IS NO HUMAN REVIEW LOOP.
""")

        # Section 2: Current Project Context
        if project_files:
            files_list = "\n".join(f"  - {file}" for file in project_files)
            prompt_sections.append(f"""# CURRENT PROJECT CONTEXT

The following files already exist in this project:
{files_list}

DO NOT regenerate these files unless explicitly instructed.
ENSURE your implementation integrates with the existing structure.
""")
        else:
            prompt_sections.append("""# CURRENT PROJECT CONTEXT

This is a new project. You are creating the initial structure.
""")

        # Section 3: Critical Dependencies
        if required_dependencies:
            deps_list = "\n".join(f"  - {dep}" for dep in required_dependencies)
            prompt_sections.append(f"""# CRITICAL DEPENDENCIES

⚠️  MANDATORY REQUIREMENT ⚠️

ADD ALL OF THE FOLLOWING DEPENDENCIES TO THE PROJECT'S package.json BEFORE WRITING ANY CODE:
{deps_list}

IF YOU ARE GENERATING package.json, IT MUST INCLUDE ALL DEPENDENCIES LISTED ABOVE.
IF package.json ALREADY EXISTS, ENSURE THESE DEPENDENCIES ARE PRESENT.

FAILURE TO INCLUDE THESE DEPENDENCIES WILL CAUSE BUILD FAILURES.
""")

        # Section 4: Task Description
        prompt_sections.append(f"""# TASK SPECIFICATION

{task_description}

---

## EXECUTION REQUIREMENTS:

1. **Code Quality:**
   - Use TypeScript strict mode. NO `any` types.
   - Follow Next.js 15 App Router conventions if applicable.
   - Include proper error handling and validation.
   - Add descriptive comments for complex logic.

2. **File Output:**
   - Output ONLY the raw file content.
   - NO markdown code blocks (no ```typescript or similar).
   - NO explanatory text before or after the code.
   - NO comments explaining what you changed (the code itself is the deliverable).

3. **Dependencies:**
   - If generating package.json, include ALL dependencies from CRITICAL DEPENDENCIES section.
   - Use specific versions or "latest" for npm packages.
   - Ensure peer dependencies are compatible.

4. **Integration:**
   - Your code must work seamlessly with existing project files.
   - Follow consistent naming conventions with the rest of the project.
   - Import from correct paths based on project structure.

OUTPUT THE COMPLETE FILE CONTENT NOW:
""")

        return "\n\n".join(prompt_sections)

    def assemble_arbiter_fix_prompt(
        self,
        error_trace: str,
        target_file_content: str
    ) -> str:
        """
        Assembles a precise debugging prompt for the Arbiter Agent.

        This prompt is optimized for error correction with minimal changes.

        Args:
            error_trace: The complete error message/stack trace from the build
            target_file_content: The current content of the file that needs fixing

        Returns:
            A complete, structured debugging prompt
        """
        prompt_sections = []

        # Section 1: Alert
        prompt_sections.append("""# ⚠️  THE ARBITER HAS DETECTED A FAILURE ⚠️

YOU ARE OMNI'S ARBITER AGENT - THE QUALITY ASSURANCE AND SELF-HEALING SYSTEM.

YOUR MISSION: Apply the MINIMUM NECESSARY CHANGE to fix the error below.

CRITICAL CONSTRAINTS:
- Output ONLY the fixed code (complete file).
- NO markdown code blocks.
- NO explanatory text.
- NO comments about what you changed.
- Do not refactor unrelated code.
- Preserve the existing structure and style.
- For JSON files: NO COMMENTS (JSON does not support comments).
- For TypeScript files: Use modern React patterns (no JSX.Element type annotations with react-jsx).
""")

        # Section 2: Error Trace
        prompt_sections.append(f"""# BUILD ERROR TRACE:

```
{error_trace}
```

ANALYZE THIS ERROR CAREFULLY. Identify the root cause before making changes.
""")

        # Section 3: Current File Content
        prompt_sections.append(f"""# CURRENT FILE CONTENT (THAT NEEDS FIXING):

{target_file_content}

---

## COMMON ERROR PATTERNS & FIXES:

1. **Missing Dependencies:**
   - Error: "Cannot find module 'X'"
   - Fix: This is a package.json issue. Add the missing package to dependencies.

2. **TypeScript Errors:**
   - Error: "Cannot find namespace 'JSX'"
   - Fix: Remove explicit `: JSX.Element` return types (use inference with react-jsx).

3. **JSON Syntax Errors:**
   - Error: "Unexpected token" in package.json
   - Fix: Remove ALL comments from JSON (use standard JSON syntax only).

4. **Import Errors:**
   - Error: "Module not found"
   - Fix: Verify the import path matches the actual file structure.

---

APPLY THE FIX NOW. OUTPUT ONLY THE COMPLETE, CORRECTED FILE CONTENT:
""")

        return "\n\n".join(prompt_sections)

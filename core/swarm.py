import os
import litellm
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from cortex import ProjectSpec, Task
from prompt_assembler import PromptAssembler
from memory_agent import MemoryAgent


console = Console()


class SwarmAgent:
    def __init__(self, assembler: PromptAssembler = None, memory_agent: MemoryAgent = None):
        # Model configuration
        self.model = os.getenv("OMNI_MODEL", "gemini-2.5-flash")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        # Prompt assembler for structured, high-quality prompts
        self.assembler = assembler if assembler else PromptAssembler()

        # Memory agent for RAG context retrieval
        self.memory_agent = memory_agent

        self.target_dir: str = ""  # To store the target directory after construct() is called

        # Track completed tasks (for DAG execution)
        self.completed_tasks: set = set()

        self.file_templates = {
            "nextjs": ["package.json", "next.config.ts", "tsconfig.json", "src/app/page.tsx", "src/app/layout.tsx"],
            "react": ["package.json", "vite.config.ts", "tsconfig.json", "src/App.tsx", "src/main.tsx"],
            "fastapi": ["main.py", "requirements.txt", "models.py", "routes.py", "Dockerfile"],
            "express": ["package.json", "server.ts", "tsconfig.json", "routes/index.ts"],
            "python": ["main.py", "requirements.txt", "Dockerfile"],
            "docker": ["docker-compose.yml", "Dockerfile"],
            "postgresql": ["schema.sql", "init.sql"],
            "prisma": ["prisma/schema.prisma"],
            "tailwind": ["tailwind.config.ts", "postcss.config.js"],
        }

        # Dependency mapping based on tech stack
        self.dependency_map = {
            "nextjs": ["next", "react", "react-dom"],
            "next.js": ["next", "react", "react-dom"],
            "react": ["react", "react-dom"],
            "typescript": ["typescript", "@types/node", "@types/react", "@types/react-dom"],
            "prisma": ["@prisma/client", "prisma"],
            "tailwind": ["tailwindcss", "postcss", "autoprefixer"],
            "nextauth": ["next-auth"],
            "next-auth": ["next-auth"],
            "stripe": ["stripe", "@stripe/stripe-js"],
            "resend": ["resend"],
            "zod": ["zod"],
            "fastapi": ["fastapi", "uvicorn", "pydantic"],
            "postgresql": ["pg"],
            "postgres": ["pg"],
        }

    def _write_file(self, target_path: Path, file_path: str, content: str):
        """Helper to write content to a file and log the action."""
        full_path = target_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(full_path, "w") as f:
                f.write(content)
            console.print(f"[green]✓[/green] {file_path}")
        except Exception as e:
            console.print(f"[bold red]✗ Error writing {file_path}: {str(e)}[/bold red]")


    async def construct(self, spec: ProjectSpec, target_dir: str):
        """
        Constructs the entire project based on ProjectSpec using DAG-based execution.

        Executes tasks in dependency order, running independent tasks in parallel.
        Uses RAG memory to provide context for code generation.

        This method implements the Task Graph Engine with parallel execution.
        """
        self.target_dir = target_dir
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)

        # Reset completed tasks tracking
        self.completed_tasks = set()

        # Initialize memory agent if provided
        if self.memory_agent:
            await self.memory_agent.a_init(collection_name=spec.project_name)

        console.print(f"[bold green]Constructing project:[/bold green] {spec.project_name}")
        console.print(f"[bold]Target directory:[/bold] {target_path.absolute()}")
        console.print(f"[bold]Execution plan:[/bold] {len(spec.execution_plan)} tasks\n")

        # DAG-based execution loop
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            while len(self.completed_tasks) < len(spec.execution_plan):
                # Find all ready tasks (dependencies satisfied)
                ready_tasks = [
                    task for task in spec.execution_plan
                    if task.task_id not in self.completed_tasks
                    and all(dep in self.completed_tasks for dep in task.depends_on)
                ]

                if not ready_tasks:
                    # Deadlock detection: no tasks ready but not all completed
                    console.print(f"[bold red]ERROR: Circular dependency detected in execution plan![/bold red]")
                    console.print(f"Completed: {self.completed_tasks}")
                    console.print(f"Remaining: {[t.task_id for t in spec.execution_plan if t.task_id not in self.completed_tasks]}")
                    break

                # Display tasks being executed
                task_names = ", ".join([task.task_id for task in ready_tasks])
                console.print(f"\n[cyan]Executing {len(ready_tasks)} task(s) in parallel:[/cyan] {task_names}")

                # Execute ready tasks concurrently
                await asyncio.gather(*[
                    self._execute_task(task, spec, target_path, progress)
                    for task in ready_tasks
                ])

                # Mark tasks as completed
                for task in ready_tasks:
                    self.completed_tasks.add(task.task_id)
                    console.print(f"[green]✓[/green] Task complete: {task.task_id}")

        console.print(f"\n[bold green]Project construction complete![/bold green]")
        console.print(f"[dim]Tasks completed: {len(self.completed_tasks)}/{len(spec.execution_plan)}[/dim]")

    async def _execute_task(self, task: Task, spec: ProjectSpec, target_path: Path, progress: Progress):
        """
        Executes a single task from the execution plan.

        - Retrieves relevant context from Memory Agent (RAG)
        - Generates ALL files for this task in a single LLM call (per-task generation)
        - Writes files to disk
        - Adds generated code to Memory Agent for future context
        """
        task_progress = progress.add_task(f"[cyan]Task: {task.task_id}[/cyan]", total=None)

        # Retrieve relevant context from memory (if memory agent available)
        relevant_context = ""
        if self.memory_agent:
            try:
                relevant_context = await self.memory_agent.a_retrieve_context(
                    query=task.task_description,
                    n_results=5
                )
            except Exception as e:
                console.print(f"[yellow]Warning: Memory retrieval failed for {task.task_id}: {str(e)}[/yellow]")

        # Generate ALL files for this task in a single LLM call
        generated_files = await self._generate_task_files(task, spec, relevant_context)

        # Write files and add to memory
        for file_path, content in generated_files.items():
            # Write file
            self._write_file(target_path, file_path, content)

            # Add to memory for future context
            if self.memory_agent:
                try:
                    await self.memory_agent.a_add_document(
                        file_path=file_path,
                        content=content,
                        metadata={
                            "task_id": task.task_id,
                            "language": self._detect_language(file_path),
                            "file_type": self._detect_file_type(file_path)
                        }
                    )
                except Exception as e:
                    console.print(f"[yellow]Warning: Memory indexing failed for {file_path}: {str(e)}[/yellow]")

        progress.update(task_progress, completed=True)

    async def _generate_task_files(self, task: Task, spec: ProjectSpec, context: str) -> Dict[str, str]:
        """
        Generates ALL files for a task in a single LLM call.

        This per-task generation approach allows the LLM to ensure consistency
        across related files (e.g., API route + types + tests).

        Args:
            task: The task from the execution plan
            spec: Complete project specification
            context: Relevant code context from Memory Agent

        Returns:
            Dictionary mapping file_path -> file_content
        """
        # Determine required dependencies for this project
        required_dependencies = self._determine_required_dependencies(spec)

        # Build task description with file requirements
        files_list = "\n".join(f"  - {fp}" for fp in task.output_files)

        task_description = f"""Generate the complete content for ALL files in this task.

TASK: {task.task_id}
Description: {task.task_description}

Files to generate:
{files_list}

Project Information:
- Name: {spec.project_name}
- Tech Stack: {', '.join(spec.tech_stack)}
- Database Schema: {spec.database_schema}
- Core Features: {', '.join(spec.core_features)}

RELEVANT CONTEXT FROM EXISTING CODE:
{context if context else "No relevant context yet (this is a foundational task)."}

CRITICAL INSTRUCTIONS:
1. Generate ALL {len(task.output_files)} files for this task.
2. Ensure consistency across all files (shared types, imports, naming).
3. Each file must be complete and production-ready.
4. Return the output as a JSON object with this structure:
   {{
     "file_path_1": "complete file content...",
     "file_path_2": "complete file content...",
     ...
   }}
5. Do NOT include markdown code blocks in the JSON values.
6. Ensure all files work together cohesively.
"""

        # Get list of already generated files (for context)
        project_files = list(self.completed_tasks)

        # Use PromptAssembler to create structured prompt
        full_prompt = self.assembler.assemble_swarm_prompt(
            task_description=task_description,
            project_files=project_files,
            required_dependencies=required_dependencies
        )

        try:
            # Async LLM call
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.2,
                api_key=self.gemini_api_key
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            content = self._clean_llm_output(content)

            try:
                files_dict = json.loads(content)

                # Validate that all expected files are present
                expected_files = set(task.output_files)
                generated_files = set(files_dict.keys())

                if not expected_files.issubset(generated_files):
                    missing = expected_files - generated_files
                    console.print(f"[yellow]Warning: LLM did not generate all files. Missing: {missing}[/yellow]")
                    # Generate missing files individually as fallback
                    for missing_file in missing:
                        files_dict[missing_file] = self._get_fallback_content(missing_file, spec)

                return files_dict

            except json.JSONDecodeError as e:
                console.print(f"[red]Error parsing LLM response as JSON: {str(e)}[/red]")
                # Fallback: generate each file individually
                return await self._generate_files_individually(task, spec, context)

        except Exception as e:
            console.print(f"[red]Error generating task files: {str(e)}[/red]")
            # Fallback: generate each file individually
            return await self._generate_files_individually(task, spec, context)

    async def _generate_files_individually(self, task: Task, spec: ProjectSpec, context: str) -> Dict[str, str]:
        """
        Fallback method: generate files one by one if per-task generation fails.
        """
        console.print(f"[yellow]Falling back to individual file generation for {task.task_id}[/yellow]")

        files_dict = {}
        for file_path in task.output_files:
            content = await self._generate_file_content(file_path, task, spec, context)
            files_dict[file_path] = content

        return files_dict

    async def _generate_file_content(self, file_path: str, task: Task, spec: ProjectSpec, context: str) -> str:
        """
        Generates content for a single file (fallback method).
        """
        required_dependencies = self._determine_required_dependencies(spec)

        task_description = f"""Generate the complete content for: {file_path}

Task: {task.task_id}
Context: {task.task_description}

Project Information:
- Name: {spec.project_name}
- Tech Stack: {', '.join(spec.tech_stack)}
- Database Schema: {spec.database_schema}

RELEVANT CONTEXT:
{context if context else "No relevant context yet."}
"""

        full_prompt = self.assembler.assemble_swarm_prompt(
            task_description=task_description,
            project_files=list(self.completed_tasks),
            required_dependencies=required_dependencies
        )

        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.2,
                api_key=self.gemini_api_key
            )

            content = response.choices[0].message.content.strip()
            content = self._clean_llm_output(content)

            return content

        except Exception as e:
            console.print(f"[red]Error generating {file_path}: {str(e)}[/red]")
            return self._get_fallback_content(file_path, spec)

    def apply_fix(self, fix_plan: Dict[str, Any]):
        """
        Executes the self-healing plan provided by the Arbiter.

        The fix_plan is expected to be a dictionary containing 'fixes',
        where each fix specifies a 'file_path' and the 'new_content'.

        This method remains synchronous as it only writes files.
        """
        fixes: List[Dict[str, str]] = fix_plan.get("fixes", [])

        if not self.target_dir:
            console.print("[bold red]ERROR: target_dir not set. Cannot apply fixes.[/bold red]")
            return

        target_path = Path(self.target_dir)

        console.print(Panel.fit(
            f"[bold yellow]SWARM ACTIVATED FOR SELF-HEALING[/bold yellow]\n\n"
            f"Fixes to apply: {len(fixes)}",
            border_style="yellow"
        ))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            task = progress.add_task(f"Applying {len(fixes)} code fixes...", total=len(fixes))

            for fix in fixes:
                file_path = fix.get("file_path")
                new_content = fix.get("new_content")

                if not file_path or not new_content:
                    console.print(f"[bold red]Skipping malformed fix in plan.[/bold red]")
                    progress.advance(task)
                    continue

                progress.update(task, description=f"Fixing [cyan]{file_path}[/cyan]...")

                # Write the corrected content, overwriting the old file
                self._write_file(target_path, file_path, new_content)

                progress.advance(task)

        console.print("\n[bold green]✓ Swarm Fixes Applied[/bold green]\n")

    def _determine_required_dependencies(self, spec: ProjectSpec) -> List[str]:
        """
        Determines required npm/pip packages based on the tech stack.
        This ensures all necessary dependencies are included in package.json.
        """
        dependencies = set()
        tech_lower = [tech.lower() for tech in spec.tech_stack]

        # Add base dependencies based on detected technologies
        for tech in tech_lower:
            # Check direct matches first
            if tech in self.dependency_map:
                dependencies.update(self.dependency_map[tech])
            else:
                # Check substring matches for compound tech names
                for key, deps in self.dependency_map.items():
                    if key in tech or tech in key:
                        dependencies.update(deps)

        # Add TypeScript types if TypeScript is detected
        if any("typescript" in tech or "next" in tech or "react" in tech for tech in tech_lower):
            dependencies.update(["typescript", "@types/node", "@types/react", "@types/react-dom"])

        # Add ESLint for Next.js projects
        if any("next" in tech for tech in tech_lower):
            dependencies.update(["eslint", "eslint-config-next"])

        return sorted(list(dependencies))

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        lang_map = {
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
            ".py": "python",
            ".sql": "sql",
            ".prisma": "prisma",
            ".json": "json",
            ".md": "markdown",
            ".yml": "yaml",
            ".yaml": "yaml",
        }
        return lang_map.get(ext, "unknown")

    def _detect_file_type(self, file_path: str) -> str:
        """Detect file type from path patterns."""
        path_lower = file_path.lower()

        if "api" in path_lower or "route" in path_lower:
            return "api_route"
        elif "component" in path_lower or path_lower.endswith(".tsx"):
            return "component"
        elif "schema" in path_lower or "prisma" in path_lower:
            return "database_schema"
        elif "config" in path_lower:
            return "config"
        elif "test" in path_lower or "spec" in path_lower:
            return "test"
        else:
            return "source"

    def _clean_llm_output(self, content: str) -> str:
        """
        Removes markdown code blocks if LLM added them despite instructions.
        """
        lines = content.split("\n")

        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        return "\n".join(lines)

    def _get_fallback_content(self, file_path: str, spec: ProjectSpec) -> str:
        """
        Provides minimal fallback content if LLM fails.
        """
        if file_path == "README.md":
            return f"""# {spec.project_name}

## Tech Stack
{chr(10).join(f"- {tech}" for tech in spec.tech_stack)}

## Features
{chr(10).join(f"- {feature}" for feature in spec.core_features)}

## Setup
```bash
# Install dependencies
npm install # or pip install -r requirements.txt

# Run development server
npm run dev # or python main.py
```
"""
        elif file_path == ".gitignore":
            return """node_modules/
.env
.env.local
dist/
build/
__pycache__/
*.pyc
.DS_Store
.next/
.venv/
"""
        elif file_path == ".env.example":
            return """DATABASE_URL=postgresql://user:password@localhost:5432/dbname
API_KEY=your_api_key_here
NODE_ENV=development
"""
        else:
            return f"# {file_path}\n# Generated by OMNI\n"

from dotenv import load_dotenv; load_dotenv()
import typer
import os
import sys
import json
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional
from cortex import analyze_intent, ProjectSpec
from swarm import SwarmAgent
from arbiter import ArbiterAgent
from devops_agent import DevOpsAgent
from doc_engine import DocEngine
from memory_agent import MemoryAgent
from completion_agent import CompletionAgent
from repair_agent import RepairAgent

# Setup - Strict Engineering UI
console = Console()
app = typer.Typer(help="OMNI: Autonomous AI Operating Environment")

def load_manifesto():
    """Load the OMNI Manifesto from disk."""
    try:
        manifesto_path = Path(__file__).parent / "00_MANIFESTO.md"
        with open(manifesto_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        console.print("[bold red]CRITICAL:[/bold red] Manifesto not found. OMNI requires its core constitution.")
        exit(1)

# --- Utility Functions ---

def _load_spec(project_dir: Path) -> ProjectSpec | None:
    """Loads ProjectSpec from a JSON file in the project directory."""
    spec_path = project_dir / "project_spec.json"
    if not spec_path.exists():
        console.print(f"[bold red]Error:[/bold red] Project spec file not found at {spec_path}")
        return None

    try:
        with open(spec_path, 'r') as f:
            data = json.load(f)

        spec = ProjectSpec(
            project_name=data.get("project_name", "unknown"),
            tech_stack=data.get("tech_stack", []),
            core_features=data.get("core_features", []),
            database_schema=data.get("database_schema", "N/A"),
            execution_plan=data.get("execution_plan", [])
        )
        return spec
    except Exception as e:
        console.print(f"[bold red]Error loading ProjectSpec from file:[/bold red] {e}")
        return None


async def _create_async(intent: str, stack: str, deploy: bool):
    """
    Asynchronous implementation of the create command.
    Enables parallel execution and non-blocking I/O operations.

    Implements the full OMNI pipeline:
    1. Cortex: Analyze intent and create execution plan DAG
    2. Memory: Initialize vector database for context
    3. Swarm: Execute DAG-based code generation with RAG
    4. Arbiter: Verify and trigger RepairAgent if failures detected
    5. RepairAgent: Aggressive multi-strategy self-healing (7 progressive strategies)
    6. DevOps + DocEngine: Generate infrastructure and documentation (parallel)
    7. Completion Agent: Generate automated setup.sh script
    """
    manifesto = load_manifesto()

    # 1. Acknowledge Intent
    console.print(Panel.fit(f"[bold white]OMNI SEQUENCE INITIATED[/bold white]\n\nIntent: {intent}\nMode: Strict Engineering", border_style="white"))

    # 2. Initialize Cortex and analyze intent
    console.print("\n[grey50]Initializing Cortex...[/grey50]")

    try:
        spec = analyze_intent(intent)
        console.print("[green]✓ Cortex Analysis Complete[/green]\n")

        # Define target directory based on project name
        target_dir = str(Path("./build_output") / spec.project_name)
        project_dir = Path(target_dir)
        project_dir.mkdir(parents=True, exist_ok=True)

        # Save ProjectSpec to enable VERIFY command
        with open(project_dir / "project_spec.json", 'w') as f:
            json.dump(spec.model_dump(), f, indent=4)

        # 3. Display spec summary using Rich tables
        table = Table(title="Project Specification", show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="white")

        table.add_row("Project Name", spec.project_name)
        table.add_row("Tech Stack", ", ".join(spec.tech_stack))
        table.add_row("Core Features", "\n".join(f"• {feature}" for feature in spec.core_features))
        table.add_row("Database Schema", spec.database_schema[:200] + "..." if len(spec.database_schema) > 200 else spec.database_schema)
        table.add_row("Execution Plan", f"{len(spec.execution_plan)} tasks in DAG")

        console.print(table)
        console.print()

        # 4. Initialize Memory Agent (RAG)
        console.print("[grey50]Initializing Memory Agent (Vector Database)...[/grey50]")
        memory_agent = MemoryAgent()
        # Note: Memory agent will be initialized inside SwarmAgent.construct() with the collection name
        console.print("[green]✓ Memory Agent Ready[/green]\n")

        # 5. Initialize Swarm Agent with Memory
        console.print("[grey50]Initializing Swarm Agent...[/grey50]")
        agent = SwarmAgent(memory_agent=memory_agent)
        console.print("[green]✓ Swarm Agent Ready[/green]\n")

        # 6. Execute DAG-based construction with RAG context
        await agent.construct(spec, target_dir=target_dir)

        # 7. Initialize Arbiter Agent
        console.print("[grey50]Initializing Arbiter Agent...[/grey50]")
        arbiter = ArbiterAgent()
        console.print("[green]✓ Arbiter Agent Ready[/green]\n")

        # 8. Verify and refine (run in executor since arbiter is sync but blocking)
        loop = asyncio.get_event_loop()
        verification_result = await loop.run_in_executor(
            None,
            arbiter.verify_and_refine,
            target_dir,
            spec
        )

        # 9. Handle verification result
        if verification_result["status"] == "failed":
            console.print("\n" + "="*60)
            console.print(Panel.fit(
                f"[bold red]⚠ BUILD VERIFICATION FAILED ⚠[/bold red]\n\n"
                f"Error: {verification_result.get('fix_plan', {}).get('error_summary', 'Unknown error')}\n"
                f"Root Cause: {verification_result.get('fix_plan', {}).get('root_cause', 'Unknown')}",
                border_style="red"
            ))
            console.print("="*60 + "\n")

            # Initialize RepairAgent with multiple progressive strategies
            console.print("[yellow]Initializing RepairAgent (Advanced Self-Healing)...[/yellow]\n")
            repair_agent = RepairAgent(arbiter=arbiter, swarm=agent)

            # Run aggressive multi-strategy repair loop
            repair_result = await repair_agent.repair(
                target_dir=target_dir,
                spec=spec,
                initial_error=verification_result
            )

            # Update verification_result based on repair outcome
            if repair_result["status"] == "success":
                verification_result = {"status": "success", "message": "Repaired successfully"}
                console.print(f"[bold green]✓ RepairAgent succeeded with: {repair_result['strategy_used']}[/bold green]\n")
            else:
                console.print(f"[bold yellow]⚠ RepairAgent exhausted all {repair_result['attempts']} strategies[/bold yellow]")
                console.print("[yellow]Continuing with setup script generation...[/yellow]\n")

        # 10. Parallel execution: Generate Infrastructure and Documentation (after successful verification)
        if verification_result["status"] == "success":
            console.print("[grey50]Initializing DevOps Agent and Documentation Engine...[/grey50]")
            devops_agent = DevOpsAgent()
            doc_engine = DocEngine()
            console.print("[green]✓ DevOps Agent Ready[/green]")
            console.print("[green]✓ Documentation Engine Ready[/green]\n")

            # Run DevOps and DocEngine in parallel using asyncio.gather()
            await asyncio.gather(
                devops_agent.generate_iac(spec, target_dir),
                loop.run_in_executor(None, doc_engine.generate_documentation, spec, target_dir)
            )

        # 11. Generate automated setup script (The Janitor) - ALWAYS RUN
        console.print("\n[grey50]Initializing Completion Agent...[/grey50]")
        completion_agent = CompletionAgent()
        console.print("[green]✓ Completion Agent Ready[/green]\n")

        console.print("[cyan]Generating automated setup script...[/cyan]")
        setup_script = await completion_agent.a_generate_setup_script(spec, target_dir)

        # Write setup.sh to project root
        setup_script_path = Path(target_dir) / "setup.sh"
        with open(setup_script_path, 'w') as f:
            f.write(setup_script)

        # Make it executable
        import stat
        setup_script_path.chmod(setup_script_path.stat().st_mode | stat.S_IEXEC)

        console.print(f"[green]✓ Setup script generated: {setup_script_path}[/green]\n")

        # Continue with success-only sections
        if verification_result["status"] == "success":

            # 12. Handle deployment if requested
            if deploy:
                console.print("\n" + "="*60)
                console.print("[bold yellow]Initiating Production Deployment Sequence...[/bold yellow]\n")

                # TODO: Implement actual deployment wrapper (e.g., Railway CLI, Vercel CLI, or Terraform apply)
                # Placeholder for deployment logic:
                # - Build Docker image: docker build -t {spec.project_name}:latest {target_dir}
                # - Push to registry: docker push {registry}/{spec.project_name}:latest
                # - Deploy to platform: railway up / vercel deploy / terraform apply

                console.print("[dim]Deployment integration coming soon...[/dim]")
                console.print(Panel.fit(
                    f"[bold green]DEPLOYMENT READY[/bold green]\n\n"
                    f"Project: {spec.project_name}\n"
                    f"Docker image: Ready for build\n"
                    f"CI/CD: GitHub Actions configured\n"
                    f"Next Steps:\n"
                    f"  1. Push to GitHub to trigger CI/CD\n"
                    f"  2. Or run: docker-compose up (local)\n"
                    f"  3. Or deploy manually to your platform",
                    border_style="green"
                ))
                console.print("="*60 + "\n")

            # 13. Memory statistics
            try:
                memory_stats = await memory_agent.a_get_stats()
                console.print(f"[dim]Memory Indexed: {memory_stats.get('document_count', 0)} code chunks[/dim]")
            except Exception:
                pass

            # 14. Final success message
            console.print("\n" + "="*60)
            console.print(Panel.fit(
                f"[bold green]OMNI EXECUTION COMPLETE[/bold green]\n\n"
                f"Project: {spec.project_name}\n"
                f"Location: {target_dir}\n"
                f"Status: PRODUCTION READY\n"
                f"Verification: PASSED\n"
                f"Infrastructure: GENERATED\n"
                f"Documentation: COMPLETE\n"
                f"Setup Script: {target_dir}/setup.sh\n"
                f"Memory Indexed: OMNI can now scale and remember project context\n\n"
                f"[bold cyan]Next Steps:[/bold cyan]\n"
                f"  1. cd {target_dir}\n"
                f"  2. ./setup.sh\n"
                f"  3. Follow the setup script instructions",
                border_style="green"
            ))
            console.print("="*60)

        # Cleanup
        arbiter.cleanup()

    except Exception as e:
        console.print(f"\n[bold red]ERROR:[/bold red] {str(e)}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


@app.command()
def create(
    intent: str = typer.Argument(..., help="The high-level description of the project to build"),
    stack: str = typer.Option("auto", help="Force specific tech stack (e.g., 'nextjs, python')"),
    deploy: bool = typer.Option(False, help="Deploy to production immediately after build")
):
    """
    Ingests user intent and begins the architecting process.

    This command runs asynchronously to enable parallel execution of independent tasks
    and non-blocking I/O operations for LLM API calls.

    Features:
    - DAG-based task execution with parallel processing
    - RAG (Retrieval-Augmented Generation) memory for context
    - Self-healing verification loop
    - Parallel infrastructure and documentation generation
    """
    asyncio.run(_create_async(intent, stack, deploy))


@app.command()
def verify(project_name: str = typer.Argument(..., help="The name of the project to resume verification for.")):
    """
    Resumes the verification and self-healing loop for an existing project.
    """
    load_manifesto()

    console.print(Panel.fit(f"[bold white]OMNI VERIFICATION RESUMED[/bold white]\n\nProject: [bold cyan]{project_name}[/bold cyan]\nMode: Self-Healing", border_style="yellow"))

    target_dir = str(Path(__file__).parent / "build_output" / project_name)
    project_dir = Path(target_dir)

    if not project_dir.is_dir():
        console.print(f"[bold red]Error:[/bold red] Project directory not found at {project_dir.absolute()}. Please check the project name.")
        raise typer.Exit(code=1)

    spec = _load_spec(project_dir)
    if not spec:
        console.print("[bold red]Error:[/bold red] Failed to load project specification.")
        raise typer.Exit(code=1)

    # 1. Initialize Swarm Agent
    console.print("[grey50]Initializing Swarm Agent...[/grey50]")
    agent = SwarmAgent()
    agent.target_dir = target_dir
    console.print("[green]✓ Swarm Agent Ready[/green]\n")

    # 2. Initialize Arbiter Agent
    console.print("[grey50]Initializing Arbiter Agent...[/grey50]")
    arbiter = ArbiterAgent()
    console.print("[green]✓ Arbiter Agent Ready[/green]\n")

    # 3. Verify and refine
    verification_result = arbiter.verify_and_refine(target_dir, spec)

    # 4. Handle verification result
    if verification_result["status"] == "failed":
        console.print("\n" + "="*60)
        console.print(Panel.fit(
            f"[bold red]⚠ BUILD VERIFICATION FAILED ⚠[/bold red]\n\n"
            f"Error: {verification_result.get('fix_plan', {}).get('error_summary', 'Unknown error')}\n"
            f"Root Cause: {verification_result.get('fix_plan', {}).get('root_cause', 'Unknown')}",
            border_style="red"
        ))
        console.print("="*60 + "\n")

        fix_plan = verification_result.get("fix_plan")

        if fix_plan and (fix_plan.get("fixes") or fix_plan.get("additional_commands")):
            console.print("[yellow]Initiating self-healing sequence...[/yellow]\n")

            # Apply code fixes if any
            if fix_plan.get("fixes"):
                agent.apply_fix(fix_plan)

            # Run additional commands if any (e.g., npm install missing packages)
            if fix_plan.get("additional_commands"):
                import subprocess
                for cmd in fix_plan.get("additional_commands"):
                    console.print(f"[cyan]Running:[/cyan] {cmd}")
                    result = subprocess.run(cmd, shell=True, cwd=target_dir, capture_output=True, text=True)
                    if result.returncode == 0:
                        console.print(f"[green]✓ Success[/green]")
                    else:
                        console.print(f"[red]✗ Failed[/red]")

            console.print("\n[yellow]Re-running verification...[/yellow]")

            # Verify again
            verification_result = arbiter.verify_and_refine(target_dir, spec)

            if verification_result["status"] == "success":
                console.print("[bold green]✓ Self-healing successful![/bold green]\n")
            else:
                console.print("[bold red]✗ Self-healing failed. Manual intervention required.[/bold red]")
                console.print(f"[dim]Error: {verification_result.get('message', 'Unknown error')}[/dim]")
                sys.exit(1)
        else:
            console.print("[bold red]No fix plan available. Manual intervention required.[/bold red]")
            sys.exit(1)

    # 5. Final success message
    if verification_result["status"] == "success":
        console.print("\n" + "="*60)
        console.print(Panel.fit(
            f"[bold green]OMNI EXECUTION COMPLETE[/bold green]\n\n"
            f"Project: {spec.project_name}\n"
            f"Location: {target_dir}\n"
            f"Status: PRODUCTION READY\n"
            f"Verification: PASSED",
            border_style="green"
        ))
        console.print("="*60)

    # 6. Cleanup
    arbiter.cleanup()


@app.command()
def status():
    """System diagnostic check."""
    console.print("[green]System Operational. Core logic standby.[/green]")

if __name__ == "__main__":
    app()

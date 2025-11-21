#!/usr/bin/env python3
"""
OMNI Mock Demo - Demonstrează sistemul fără API calls
Creează un ProjectSpec manual și îl procesează prin pipeline
"""
import json
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from cortex import ProjectSpec, Task

console = Console()

def create_mock_spec() -> ProjectSpec:
    """Creează un ProjectSpec mock pentru demonstrație"""

    tasks = [
        Task(
            task_id="setup_database_schema",
            task_description="Define Prisma database schema with User, Tenant, and Subscription models",
            output_files=["prisma/schema.prisma", "src/lib/db.ts"],
            depends_on=[]
        ),
        Task(
            task_id="create_auth_system",
            task_description="Implement NextAuth authentication with multi-tenant support",
            output_files=["src/app/api/auth/[...nextauth]/route.ts", "src/lib/auth.ts", "src/middleware.ts"],
            depends_on=["setup_database_schema"]
        ),
        Task(
            task_id="create_stripe_integration",
            task_description="Implement Stripe subscriptions with webhook handlers",
            output_files=[
                "src/app/api/stripe/webhook/route.ts",
                "src/lib/stripe.ts",
                "src/app/api/subscriptions/route.ts"
            ],
            depends_on=["setup_database_schema", "create_auth_system"]
        ),
        Task(
            task_id="create_rbac_system",
            task_description="Implement RBAC with Zod schemas for permissions",
            output_files=[
                "src/lib/rbac.ts",
                "src/schemas/permissions.ts",
                "src/middleware/authorization.ts"
            ],
            depends_on=["create_auth_system"]
        ),
        Task(
            task_id="create_frontend_dashboard",
            task_description="Build dashboard UI with Tailwind CSS and tenant selector",
            output_files=[
                "src/app/dashboard/page.tsx",
                "src/components/TenantSelector.tsx",
                "src/components/ui/Button.tsx"
            ],
            depends_on=["create_auth_system", "create_rbac_system"]
        ),
        Task(
            task_id="create_email_system",
            task_description="Implement Resend email integration for transactional emails",
            output_files=[
                "src/lib/email.ts",
                "src/emails/WelcomeEmail.tsx",
                "src/emails/InvoiceEmail.tsx"
            ],
            depends_on=[]
        ),
        Task(
            task_id="setup_monitoring",
            task_description="Configure OpenTelemetry with Grafana exporters",
            output_files=[
                "src/lib/telemetry.ts",
                "instrumentation.ts",
                "grafana-config.yml"
            ],
            depends_on=[]
        ),
        Task(
            task_id="create_tests",
            task_description="Write Jest tests for API routes and components",
            output_files=[
                "src/app/api/auth/__tests__/route.test.ts",
                "src/lib/__tests__/stripe.test.ts",
                "jest.config.js"
            ],
            depends_on=["create_auth_system", "create_stripe_integration"]
        )
    ]

    spec = ProjectSpec(
        project_name="multi-tenant-saas-boilerplate",
        tech_stack=[
            "Next.js 15 (App Router)",
            "TypeScript (Strict)",
            "Prisma ORM",
            "PostgreSQL",
            "NextAuth.js",
            "Stripe",
            "Resend",
            "Tailwind CSS",
            "Zod",
            "Jest",
            "OpenTelemetry",
            "Docker",
            "GitHub Actions",
            "Railway"
        ],
        database_schema="""
        User {
          id: UUID (PK)
          email: String (unique)
          name: String
          tenantId: UUID (FK -> Tenant)
          role: Enum (ADMIN, MEMBER, VIEWER)
          createdAt: DateTime
        }

        Tenant {
          id: UUID (PK)
          name: String
          slug: String (unique)
          subscriptionId: UUID (FK -> Subscription)
          settings: JSON
          createdAt: DateTime
        }

        Subscription {
          id: UUID (PK)
          tenantId: UUID (FK -> Tenant)
          stripeCustomerId: String
          stripeSubscriptionId: String
          status: Enum (ACTIVE, CANCELED, PAST_DUE)
          plan: Enum (FREE, PRO, ENTERPRISE)
          currentPeriodEnd: DateTime
        }
        """,
        core_features=[
            "Multi-tenant architecture with tenant isolation via discriminators",
            "Authentication with NextAuth.js (email/password + OAuth)",
            "Stripe subscription management with webhooks",
            "RBAC (Role-Based Access Control) using Zod schemas",
            "Transactional emails via Resend",
            "OpenTelemetry monitoring with Grafana integration",
            "CI/CD via GitHub Actions",
            "Multi-stage Docker builds",
            "Railway deployment with PR preview environments"
        ],
        execution_plan=tasks
    )

    return spec


async def display_dag_analysis(spec: ProjectSpec):
    """Afișează analiza DAG-ului de execuție"""
    console.print("\n[bold cyan]📊 DAG Execution Plan Analysis[/bold cyan]\n")

    # Construiește tabelul de tasks
    table = Table(title="Task Dependency Graph (DAG)", show_header=True, header_style="bold magenta")
    table.add_column("Task ID", style="cyan", width=25)
    table.add_column("Description", style="white", width=40)
    table.add_column("Dependencies", style="yellow", width=30)
    table.add_column("Files", style="green", width=15)

    for task in spec.execution_plan:
        deps = ", ".join(task.depends_on) if task.depends_on else "None (Parallel)"
        table.add_row(
            task.task_id,
            task.task_description[:40] + "...",
            deps,
            str(len(task.output_files))
        )

    console.print(table)

    # Identifică task-uri care pot rula în paralel
    parallel_tasks = [t for t in spec.execution_plan if not t.depends_on]
    console.print(f"\n[green]✓ {len(parallel_tasks)} tasks can run in PARALLEL (no dependencies)[/green]")
    for task in parallel_tasks:
        console.print(f"  • {task.task_id}")

    console.print(f"\n[yellow]⚡ Total tasks: {len(spec.execution_plan)}[/yellow]")
    console.print(f"[yellow]📁 Total files to generate: {sum(len(t.output_files) for t in spec.execution_plan)}[/yellow]")


async def simulate_swarm_execution(spec: ProjectSpec):
    """Simulează execuția Swarm Agent (DAG-based parallel execution)"""
    console.print("\n[bold cyan]🐝 Swarm Agent - DAG Execution Simulation[/bold cyan]\n")

    completed = set()
    wave = 1

    while len(completed) < len(spec.execution_plan):
        # Find tasks ready to execute (dependencies met)
        ready_tasks = [
            task for task in spec.execution_plan
            if task.task_id not in completed and all(dep in completed for dep in task.depends_on)
        ]

        if not ready_tasks:
            break

        console.print(f"[bold yellow]Wave {wave}: Executing {len(ready_tasks)} tasks in PARALLEL[/bold yellow]")

        for task in ready_tasks:
            console.print(f"  [cyan]→[/cyan] {task.task_id}: {task.task_description[:50]}...")
            console.print(f"    [dim]Generating {len(task.output_files)} files...[/dim]")
            completed.add(task.task_id)

        console.print()
        wave += 1
        await asyncio.sleep(0.5)  # Simulează procesarea

    console.print(f"[green]✓ All {len(spec.execution_plan)} tasks completed in {wave-1} parallel waves![/green]")


async def show_generated_structure(spec: ProjectSpec):
    """Afișează structura proiectului generat"""
    console.print("\n[bold cyan]📁 Generated Project Structure[/bold cyan]\n")

    # Colectează toate fișierele din toate task-urile
    all_files = []
    for task in spec.execution_plan:
        all_files.extend(task.output_files)

    # Construiește un arbore de directoare
    dirs = {}
    for file_path in sorted(all_files):
        parts = file_path.split('/')
        current = dirs
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]

    # Afișează structura
    def print_tree(tree, prefix="", is_last=True):
        items = list(tree.items())
        for i, (name, subtree) in enumerate(items):
            is_last_item = i == len(items) - 1
            connector = "└── " if is_last_item else "├── "
            console.print(f"{prefix}{connector}[cyan]{name}/[/cyan]")

            new_prefix = prefix + ("    " if is_last_item else "│   ")
            if isinstance(subtree, dict):
                print_tree(subtree, new_prefix, is_last_item)

    console.print(f"[bold]{spec.project_name}/[/bold]")
    print_tree(dirs)

    console.print(f"\n[green]✓ Total files: {len(all_files)}[/green]")


async def show_devops_outputs():
    """Afișează ce ar genera DevOps Agent"""
    console.print("\n[bold cyan]🐳 DevOps Agent - Infrastructure as Code[/bold cyan]\n")

    outputs = [
        ("Dockerfile", "Multi-stage build with Node.js 20-alpine"),
        ("docker-compose.yml", "App + PostgreSQL + Redis services"),
        (".github/workflows/ci.yml", "Lint → Test → Build → Deploy"),
        (".github/workflows/pr-preview.yml", "Railway preview environments per PR"),
        (".dockerignore", "Optimized layer caching"),
        ("railway.json", "Railway configuration with auto-deploy")
    ]

    for filename, description in outputs:
        console.print(f"  [green]✓[/green] {filename}")
        console.print(f"    [dim]{description}[/dim]")


async def show_documentation_outputs():
    """Afișează ce ar genera Doc Engine"""
    console.print("\n[bold cyan]📚 Doc Engine - Documentation Generation[/bold cyan]\n")

    docs = [
        "README.md - Complete setup and deployment guide",
        "docs/adr/ADR-0001-database-choice.md - Why Prisma + PostgreSQL",
        "docs/adr/ADR-0002-multi-tenancy.md - Tenant isolation strategy",
        "docs/adr/ADR-0003-authentication.md - NextAuth.js decision",
        "docs/api/README.md - API endpoint documentation"
    ]

    for doc in docs:
        console.print(f"  [green]✓[/green] {doc}")


async def main():
    """Main demo function"""
    console.print(Panel.fit(
        "[bold white]OMNI MOCK DEMONSTRATION[/bold white]\n\n"
        "Demonstrating full OMNI pipeline with mock ProjectSpec\n"
        "No LLM API calls - Pure architecture showcase",
        border_style="cyan"
    ))

    # 1. Create mock spec
    console.print("\n[bold yellow]Step 1: Creating Mock ProjectSpec (simulating Cortex)[/bold yellow]")
    spec = create_mock_spec()
    console.print(f"[green]✓ ProjectSpec created: {spec.project_name}[/green]")
    console.print(f"  Tech Stack: {', '.join(spec.tech_stack[:3])}... (+{len(spec.tech_stack)-3} more)")

    # 2. Analyze DAG
    await display_dag_analysis(spec)
    await asyncio.sleep(1)

    # 3. Simulate Swarm execution
    await simulate_swarm_execution(spec)
    await asyncio.sleep(1)

    # 4. Show project structure
    await show_generated_structure(spec)
    await asyncio.sleep(1)

    # 5. Show DevOps outputs
    await show_devops_outputs()
    await asyncio.sleep(1)

    # 6. Show Documentation outputs
    await show_documentation_outputs()

    # 7. Final summary
    console.print("\n" + "="*80)
    console.print(Panel.fit(
        "[bold green]DEMONSTRATION COMPLETE[/bold green]\n\n"
        "What you just saw:\n"
        "✓ Cortex: Intent → Structured ProjectSpec with DAG\n"
        "✓ Swarm: Parallel task execution (3 waves, 8 tasks)\n"
        "✓ Memory: Would index all generated code in ChromaDB\n"
        "✓ Arbiter: Would verify builds (npm install, tsc, jest)\n"
        "✓ Repair: 7-strategy self-healing if failures\n"
        "✓ DevOps: Docker, CI/CD, Railway config\n"
        "✓ DocEngine: README, ADRs, API docs\n\n"
        "[yellow]This is OMNI's architecture in action![/yellow]",
        border_style="green"
    ))

    # Save spec to file
    project_dir = Path("./build_output") / spec.project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    with open(project_dir / "project_spec_mock.json", 'w') as f:
        json.dump(spec.model_dump(), f, indent=2)

    console.print(f"\n[dim]Mock ProjectSpec saved to: {project_dir}/project_spec_mock.json[/dim]")


if __name__ == "__main__":
    asyncio.run(main())

import os
import litellm
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from cortex import ProjectSpec
from prompt_assembler import PromptAssembler


console = Console()


class DevOpsAgent:
    def __init__(self, assembler: PromptAssembler = None):
        self.model = os.getenv("OMNI_MODEL", "gpt-4o")

        # Prompt assembler for structured, high-quality prompts
        self.assembler = assembler if assembler else PromptAssembler()

        self.deployment_files = {
            "Dockerfile": "Multi-stage Docker build configuration",
            "docker-compose.yml": "Local development environment with all services",
            ".github/workflows/main.yml": "CI/CD pipeline for testing, linting, and deployment",
            ".dockerignore": "Files to exclude from Docker build context",
            "k8s/deployment.yaml": "Kubernetes deployment configuration (optional)",
            "k8s/service.yaml": "Kubernetes service configuration (optional)",
        }

    async def generate_iac(self, spec: ProjectSpec, target_dir: str):
        """
        Generates Infrastructure as Code and deployment artifacts.
        Creates production-ready Docker, Docker Compose, and CI/CD configurations.

        This method is now async to support concurrent LLM calls.
        """
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)

        console.print(Panel.fit(
            f"[bold cyan]DEVOPS AGENT ACTIVATED[/bold cyan]\n\n"
            f"Generating deployment infrastructure for: {spec.project_name}",
            border_style="cyan"
        ))

        # Scan existing project files for context
        existing_files = self._scan_project_files(target_path)

        files_to_generate = self._determine_deployment_files(spec)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            for file_path, description in files_to_generate.items():
                task = progress.add_task(f"Generating {file_path}...", total=None)

                # Async LLM call
                content = await self._generate_deployment_file(
                    file_path=file_path,
                    description=description,
                    spec=spec,
                    existing_files=existing_files
                )

                # Synchronous file write
                full_path = target_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)

                with open(full_path, "w") as f:
                    f.write(content)

                progress.update(task, completed=True)
                console.print(f"[green]✓[/green] {file_path}")

        console.print(f"\n[bold green]✓ Infrastructure as Code generation complete![/bold green]\n")

    def _scan_project_files(self, target_path: Path) -> List[str]:
        """
        Scans the project directory to find existing files.
        This provides context for infrastructure generation.
        """
        project_files = []

        # Important files to check for context
        important_files = [
            "package.json",
            "requirements.txt",
            "tsconfig.json",
            "next.config.ts",
            "next.config.js",
            "prisma/schema.prisma",
            ".env.example",
        ]

        for file_pattern in important_files:
            file_path = target_path / file_pattern
            if file_path.exists():
                project_files.append(file_pattern)

        return project_files

    def _determine_deployment_files(self, spec: ProjectSpec) -> Dict[str, str]:
        """
        Determines which deployment files to generate based on tech stack.
        """
        files = {}
        tech_lower = [tech.lower() for tech in spec.tech_stack]

        # Always generate core deployment files
        files["Dockerfile"] = "Multi-stage Docker build for production deployment"
        files["docker-compose.yml"] = "Local development environment with all required services"
        files[".dockerignore"] = "Optimize Docker build by excluding unnecessary files"
        files[".github/workflows/main.yml"] = "Complete CI/CD pipeline with testing and deployment"

        # Add database-specific configurations
        if any(db in tech_lower for db in ["postgresql", "postgres", "mysql", "mongodb"]):
            files["docker-compose.yml"] = "Development environment including database container"

        # Add Kubernetes configs if requested
        if "kubernetes" in tech_lower or "k8s" in tech_lower:
            files["k8s/deployment.yaml"] = "Kubernetes deployment configuration"
            files["k8s/service.yaml"] = "Kubernetes service configuration"
            files["k8s/ingress.yaml"] = "Kubernetes ingress configuration"

        # Add Terraform/Pulumi if infrastructure is complex
        if len(spec.tech_stack) > 5 or "aws" in tech_lower or "gcp" in tech_lower or "azure" in tech_lower:
            files["terraform/main.tf"] = "Terraform infrastructure provisioning"
            files["terraform/variables.tf"] = "Terraform variable definitions"

        return files

    async def _generate_deployment_file(
        self,
        file_path: str,
        description: str,
        spec: ProjectSpec,
        existing_files: List[str]
    ) -> str:
        """
        Uses LLM to generate deployment file content with structured prompts from PromptAssembler.

        This method is now async to allow concurrent LLM calls.
        """
        # Build detailed task description with tech-specific requirements
        tech_requirements = self._get_tech_specific_requirements(spec, file_path)

        task_description = f"""Generate the complete content for: {file_path}

Description: {description}

Project Information:
- Name: {spec.project_name}
- Tech Stack: {', '.join(spec.tech_stack)}
- Database Schema: {spec.database_schema}
- Core Features: {', '.join(spec.core_features)}

Tech-Specific Requirements:
{tech_requirements}

DEVOPS-SPECIFIC INSTRUCTIONS:
1. All configurations must be production-ready and secure.
2. For Dockerfile: Use multi-stage builds to minimize image size.
3. For Dockerfile: Include health checks and run as non-root user.
4. For docker-compose.yml: Use environment variables, add persistent volumes.
5. For CI/CD: Include linting, testing, building, and deployment steps.
6. For CI/CD: Use caching for dependencies to speed up builds.
7. Never hardcode secrets - use environment variables and secret management.
8. For YAML files: Use valid YAML syntax (proper indentation, no tabs).
9. Base images: Use alpine or slim variants (e.g., node:20-alpine, python:3.12-slim).
10. Security: Implement least privilege principle, scan for vulnerabilities.
"""

        # Determine infrastructure dependencies (for context, not for package.json)
        infra_dependencies = self._determine_infra_context(spec)

        # Use PromptAssembler to create structured prompt
        full_prompt = self.assembler.assemble_swarm_prompt(
            task_description=task_description,
            project_files=existing_files,
            required_dependencies=infra_dependencies
        )

        try:
            # Async LLM call
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.1,
            )

            content = response.choices[0].message.content.strip()
            content = self._clean_llm_output(content)

            return content

        except Exception as e:
            console.print(f"[red]Error generating {file_path}: {str(e)}[/red]")
            return self._get_fallback_deployment_content(file_path, spec)

    def _determine_infra_context(self, spec: ProjectSpec) -> List[str]:
        """
        Determines infrastructure context (base images, tools) based on tech stack.
        This helps the LLM generate consistent Dockerfiles and CI/CD configs.
        """
        context = []
        tech_lower = [tech.lower() for tech in spec.tech_stack]

        if any("next" in tech for tech in tech_lower):
            context.extend([
                "Base image: node:20-alpine",
                "Build command: npm run build",
                "Start command: npm start",
                "Expose port: 3000"
            ])

        if any("python" in tech or "fastapi" in tech for tech in tech_lower):
            context.extend([
                "Base image: python:3.12-slim",
                "Package manager: pip",
                "Requirements file: requirements.txt",
                "Expose port: 8000"
            ])

        if any("postgres" in tech for tech in tech_lower):
            context.append("Database: PostgreSQL 16")

        if "prisma" in " ".join(tech_lower):
            context.append("ORM: Prisma (requires migration step)")

        return context

    def _get_tech_specific_requirements(self, spec: ProjectSpec, file_path: str) -> str:
        """
        Returns specific requirements based on the tech stack and file type.
        """
        tech_lower = [tech.lower() for tech in spec.tech_stack]
        requirements = []

        if file_path == "Dockerfile":
            if any("next" in tech for tech in tech_lower):
                requirements.append("- Use Node.js 20 Alpine base image")
                requirements.append("- Multi-stage build: dependencies -> builder -> runner")
                requirements.append("- Copy only necessary files to final stage")
                requirements.append("- Set NODE_ENV=production")
                requirements.append("- Configure Next.js standalone output")
            elif "python" in tech_lower or "fastapi" in tech_lower:
                requirements.append("- Use Python 3.12-slim base image")
                requirements.append("- Multi-stage build with separate build and runtime stages")
                requirements.append("- Use pip to install dependencies from requirements.txt")
                requirements.append("- Run as non-root user")

        elif file_path == "docker-compose.yml":
            if "postgresql" in tech_lower or "postgres" in tech_lower:
                requirements.append("- Include PostgreSQL 16 service with persistent volume")
                requirements.append("- Set up database initialization scripts")
            if "redis" in tech_lower:
                requirements.append("- Include Redis service for caching")
            requirements.append("- Use environment variables for all configuration")
            requirements.append("- Set up networks for service isolation")
            requirements.append("- Add health checks for all services")

        elif file_path == ".github/workflows/main.yml":
            requirements.append("- Trigger on push to main and pull requests")
            requirements.append("- Run linting (ESLint/Ruff) as first job")
            requirements.append("- Run tests with coverage reporting")
            requirements.append("- Build Docker image and push to registry")
            requirements.append("- Include deployment step (conditional on branch)")
            requirements.append("- Use GitHub Actions caching for dependencies")
            requirements.append("- Set up proper secrets management")

        return "\n".join(requirements) if requirements else "Standard best practices"

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

    def _get_fallback_deployment_content(self, file_path: str, spec: ProjectSpec) -> str:
        """
        Provides minimal fallback content if LLM fails.
        """
        tech_lower = [tech.lower() for tech in spec.tech_stack]

        if file_path == "Dockerfile":
            if any("next" in tech for tech in tech_lower):
                return """FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT 3000
CMD ["node", "server.js"]
"""
            elif "python" in tech_lower or "fastapi" in tech_lower:
                return """FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

        elif file_path == "docker-compose.yml":
            has_postgres = "postgresql" in tech_lower or "postgres" in tech_lower
            return f"""version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://user:password@db:5432/{spec.project_name}
    depends_on:
      - db
    volumes:
      - .:/app
      - /app/node_modules

{'''  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: ''' + spec.project_name + '''
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:''' if has_postgres else ''}
"""

        elif file_path == ".github/workflows/main.yml":
            return """name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
      - name: Install dependencies
        run: npm ci
      - name: Run linter
        run: npm run lint
      - name: Run tests
        run: npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t ${{ github.repository }}:latest .
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      - name: Push Docker image
        run: docker push ${{ github.repository }}:latest
"""

        elif file_path == ".dockerignore":
            return """node_modules
.git
.gitignore
.env
.env.local
README.md
docker-compose.yml
.next
.vscode
coverage
*.log
.DS_Store
"""

        else:
            return f"# {file_path}\n# Generated by OMNI DevOps Agent\n"

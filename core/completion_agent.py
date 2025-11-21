"""
OMNI Completion Agent

Generates automated setup scripts for users to run after OMNI completes project generation.
Ensures seamless transition from generated code to running application.

This agent creates intelligent, executable shell scripts that:
- Auto-detect project type (Node.js vs Python)
- Install dependencies
- Configure environment variables
- Set up databases (Prisma, Alembic, etc.)
- Run code quality tools
- Provide final execution commands
"""

import os
import asyncio
import litellm
from pathlib import Path
from rich.console import Console
from cortex import ProjectSpec


console = Console()


class CompletionAgent:
    def __init__(self):
        """Initialize the Completion Agent."""
        self.model = os.getenv("OMNI_MODEL", "gpt-4o")

    async def a_generate_setup_script(self, spec: ProjectSpec, target_dir: str) -> str:
        """
        Generates a complete, executable setup script for the user.

        This script is the final deliverable - a runnable Bash script that
        handles all setup steps from dependency installation to database migrations.

        Args:
            spec: Complete project specification
            target_dir: Absolute path to the generated project directory

        Returns:
            Raw shell script content (starting with #!/bin/bash)

        Example:
            >>> agent = CompletionAgent()
            >>> script = await agent.a_generate_setup_script(spec, "/path/to/project")
            >>> with open("setup.sh", "w") as f:
            >>>     f.write(script)
        """
        # Detect key technologies for script generation
        tech_lower = [tech.lower() for tech in spec.tech_stack]
        has_prisma = any("prisma" in tech for tech in tech_lower)
        has_postgres = any("postgres" in tech for tech in tech_lower)
        has_stripe = any("stripe" in tech for tech in tech_lower)

        prompt = f"""Generate a complete, executable Bash shell script that a user can run to set up and start this project.

Project Information:
- Name: {spec.project_name}
- Tech Stack: {', '.join(spec.tech_stack)}
- Database: {spec.database_schema[:200]}...
- Has Prisma: {has_prisma}
- Has PostgreSQL: {has_postgres}
- Has Stripe: {has_stripe}

CRITICAL REQUIREMENTS:

1. **Auto-detection**: The script must automatically detect whether this is a Node.js or Python project.

2. **Dependency Installation**:
   - For Node.js: Run 'npm install' (or detect and use pnpm/yarn if available)
   - For Python: Run 'pip install -r requirements.txt' (or poetry install if pyproject.toml exists)

3. **Environment Setup**:
   - Copy .env.example to .env
   - Provide clear instructions for required API keys (Stripe, Database URL, etc.)
   - Do NOT hardcode secrets

4. **Database Setup** (if applicable):
   - For Prisma: Run 'npx prisma generate' and 'npx prisma migrate dev --name init'
   - For Alembic: Run 'alembic upgrade head'
   - For raw SQL: Provide instructions to source schema files
   - Include PostgreSQL connection test if applicable

5. **Code Quality** (optional but recommended):
   - Run 'npx prettier --write .' for formatting (Node.js only, if time permits)
   - Run 'npm run lint' if package.json has a lint script

6. **Final Start Command**:
   - For Next.js: 'npm run dev' (typically runs on localhost:3000)
   - For FastAPI: 'uvicorn main:app --reload' (typically runs on localhost:8000)
   - For other Python: 'python main.py'

7. **Output Format**:
   - The script MUST be a valid, runnable Bash script
   - Include helpful echo messages with emojis explaining each step
   - Include error handling (set -e to exit on errors)
   - Make it idempotent where possible (e.g., check if .env exists before copying)
   - Add color to output (use tput or ANSI codes)

8. **User Experience**:
   - Clear progress indicators
   - Helpful error messages
   - Final success message with next steps
   - Include port information (e.g., "Visit http://localhost:3000")

TEMPLATE STRUCTURE:
```bash
#!/bin/bash
set -e  # Exit on error

# Colors
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo "🚀 Setting up {spec.project_name}..."
echo ""

# Change to project directory
cd "{target_dir}"

# Detect project type
if [ -f "package.json" ]; then
    echo "📦 Node.js project detected"

    # Install dependencies
    echo "Installing dependencies..."
    npm install

    # Environment setup
    if [ -f ".env.example" ] && [ ! -f ".env" ]; then
        echo "📝 Setting up environment variables..."
        cp .env.example .env
        echo "⚠️  Please edit .env and add your API keys:"
        echo "   - DATABASE_URL (PostgreSQL connection string)"
        echo "   - STRIPE_SECRET_KEY (from Stripe dashboard)"
        # ... more keys as needed
    fi

    # Database setup (Prisma example)
    if [ -f "prisma/schema.prisma" ]; then
        echo "🗄️  Setting up database..."
        npx prisma generate
        npx prisma migrate dev --name init
    fi

    echo ""
    echo "${{GREEN}}✅ Setup complete!${{NC}}"
    echo ""
    echo "Run the following command to start the development server:"
    echo "   npm run dev"
    echo ""
    echo "Then visit: http://localhost:3000"

elif [ -f "requirements.txt" ]; then
    echo "🐍 Python project detected"

    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt

    # Environment setup
    if [ -f ".env.example" ] && [ ! -f ".env" ]; then
        echo "📝 Setting up environment variables..."
        cp .env.example .env
        echo "⚠️  Please edit .env and add your configuration"
    fi

    echo ""
    echo "${{GREEN}}✅ Setup complete!${{NC}}"
    echo ""
    echo "Run the following command to start the development server:"
    echo "   uvicorn main:app --reload"
    echo ""
    echo "Then visit: http://localhost:8000"
fi
```

IMPORTANT: Output ONLY the raw shell script content. NO markdown code blocks wrapping it.
The script should start directly with #!/bin/bash
"""

        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )

            script_content = response.choices[0].message.content.strip()

            # Clean markdown code blocks if LLM added them
            script_content = self._clean_script_output(script_content)

            return script_content

        except Exception as e:
            console.print(f"[red]Error generating setup script: {str(e)}[/red]")
            return self._get_fallback_script(spec, target_dir)

    def _clean_script_output(self, content: str) -> str:
        """Remove markdown code blocks if present."""
        lines = content.split("\n")

        # Remove opening code block
        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        # Remove closing code block
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        return "\n".join(lines)

    def _get_fallback_script(self, spec: ProjectSpec, target_dir: str) -> str:
        """
        Fallback script if LLM fails.

        Generates a basic but functional setup script based on detected tech stack.
        """
        tech_lower = [tech.lower() for tech in spec.tech_stack]
        is_node = any("next" in tech or "react" in tech or "node" in tech for tech in tech_lower)
        is_python = any("python" in tech or "fastapi" in tech for tech in tech_lower)
        has_prisma = any("prisma" in tech for tech in tech_lower)

        if is_node:
            prisma_commands = ""
            if has_prisma:
                prisma_commands = """
# Database setup
if [ -f "prisma/schema.prisma" ]; then
    echo "🗄️  Setting up database..."
    npx prisma generate
    npx prisma migrate dev --name init
fi
"""

            return f"""#!/bin/bash
set -e

# Colors
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

echo "🚀 Setting up {spec.project_name}..."
echo ""

# Change to project directory
cd "{target_dir}"

echo "📦 Installing dependencies..."
npm install

# Environment setup
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    echo "📝 Setting up environment variables..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys"
fi
{prisma_commands}
echo ""
echo "${{GREEN}}✅ Setup complete!${{NC}}"
echo ""
echo "Run the following command to start the development server:"
echo "   npm run dev"
echo ""
echo "Then visit: http://localhost:3000"
"""

        elif is_python:
            return f"""#!/bin/bash
set -e

# Colors
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

echo "🚀 Setting up {spec.project_name}..."
echo ""

# Change to project directory
cd "{target_dir}"

echo "🐍 Installing dependencies..."
pip install -r requirements.txt

# Environment setup
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    echo "📝 Setting up environment variables..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your configuration"
fi

echo ""
echo "${{GREEN}}✅ Setup complete!${{NC}}"
echo ""
echo "Run the following command to start the development server:"
echo "   python main.py"
echo ""
echo "Then visit: http://localhost:8000"
"""

        else:
            return f"""#!/bin/bash
set -e

echo "🚀 Setting up {spec.project_name}..."
echo ""

cd "{target_dir}"

echo "⚠️  Please check the README.md for detailed setup instructions."
echo ""
echo "Project location: {target_dir}"
"""

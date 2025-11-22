#!/bin/bash
set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Emojis
ROCKET="🚀"
PACKAGE="📦"
WRENCH="🔧"
MEMO="📝"
DATABASE="🗄️"
WARNING="⚠️"
CHECK="✅"
ERROR="❌"
SPARKLES="✨"
GEAR="⚙️"
LIGHTBULB="💡"

echo -e "${ROCKET} ${BLUE}Setting up saas-boilerplate...${NC}"
echo ""

# Change to project directory
# The user provided this path: /home/venom/omni-system/build_output/saas-boilerplate
PROJECT_DIR="/home/venom/omni-system/build_output/saas-boilerplate"
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${ERROR} ${RED}Error: Project directory '$PROJECT_DIR' not found.${NC}"
    echo -e "${LIGHTBULB} ${YELLOW}Please ensure you run this script from the correct location or update the PROJECT_DIR variable.${NC}"
    exit 1
fi
cd "$PROJECT_DIR"
echo -e "${GEAR} Changed to project directory: ${BLUE}$PROJECT_DIR${NC}"
echo ""

# Detect project type
if [ -f "package.json" ]; then
    echo -e "${PACKAGE} ${GREEN}Node.js project detected.${NC}"

    # --- Dependency Installation ---
    echo -e "${WRENCH} Installing dependencies..."
    if [ -f "pnpm-lock.yaml" ] && command -v pnpm &> /dev/null; then
        echo -e "${BLUE}  Using pnpm...${NC}"
        pnpm install
    elif [ -f "yarn.lock" ] && command -v yarn &> /dev/null; then
        echo -e "${BLUE}  Using yarn...${NC}"
        yarn install
    elif [ -f "package.json" ]; then
        echo -e "${BLUE}  Using npm...${NC}"
        npm install
    else
        echo -e "${ERROR} ${RED}No recognized Node.js dependency file (package.json, yarn.lock, pnpm-lock.yaml) found.${NC}"
        echo -e "${LIGHTBULB} ${YELLOW}Please install dependencies manually.${NC}"
        exit 1
    fi
    echo -e "${CHECK} Dependencies installed.${NC}"
    echo ""

    # --- Environment Setup ---
    if [ -f ".env.example" ]; then
        if [ ! -f ".env" ]; then
            echo -e "${MEMO} Setting up environment variables..."
            cp .env.example .env
            echo -e "${CHECK} Copied .env.example to .env.${NC}"
            echo -e "${WARNING} ${YELLOW}Please edit .env and add your API keys and configuration:${NC}"
            echo -e "   - ${BLUE}DATABASE_URL${NC} (PostgreSQL connection string, e.g., postgresql://user:password@host:port/database)"
            echo -e "   - ${BLUE}NEXTAUTH_SECRET${NC} (A long, random string for NextAuth.js sessions)"
            echo -e "   - ${BLUE}NEXTAUTH_URL${NC} (Your application's base URL, e.g., http://localhost:3000)"
            echo -e "   - ${BLUE}STRIPE_SECRET_KEY${NC} (from Stripe dashboard)"
            echo -e "   - ${BLUE}STRIPE_WEBHOOK_SECRET${NC} (from Stripe dashboard, for webhooks)"
            echo -e "   - ${BLUE}STRIPE_PRO_PLAN_PRICE_ID${NC} (Stripe Price ID for Pro plan)"
            echo -e "   - ${BLUE}STRIPE_FREE_PLAN_PRICE_ID${NC} (Stripe Price ID for Free plan)"
            echo -e "   - ${BLUE}RESEND_API_KEY${NC} (from Resend dashboard)"
            echo -e "   - ${BLUE}EMAIL_FROM${NC} (Email address for sending emails, e.g., 'Your App <onboarding@yourapp.com>')"
            echo -e "   - ${BLUE}GITHUB_ID${NC}, ${BLUE}GITHUB_SECRET${NC} (If using GitHub OAuth with NextAuth.js)"
            echo -e "${LIGHTBULB} ${YELLOW}Remember: Do NOT hardcode secrets directly in your code.${NC}"
            echo -e "${LIGHTBULB} ${YELLOW}You might need to create a PostgreSQL database and user first.${NC}"
            echo -e "${LIGHTBULB} ${YELLOW}After updating .env, you may need to re-run this script or manually run database migrations.${NC}"
            echo ""
        else
            echo -e "${MEMO} .env file already exists. Skipping copy.${NC}"
            echo -e "${LIGHTBULB} ${YELLOW}Ensure your .env file has all necessary configurations (DATABASE_URL, Stripe keys, etc.).${NC}"
            echo ""
        fi
    else
        echo -e "${WARNING} ${YELLOW}.env.example not found. Skipping environment setup.${NC}"
        echo -e "${LIGHTBULB} ${YELLOW}Please create a .env file manually with your configuration.${NC}"
        echo ""
    fi

    # --- Database Setup (Prisma) ---
    if [ -f "prisma/schema.prisma" ]; then
        echo -e "${DATABASE} Setting up database with Prisma..."
        echo -e "${LIGHTBULB} ${YELLOW}Ensure your PostgreSQL database is running and accessible via the DATABASE_URL in your .env file.${NC}"

        # Generate Prisma client
        echo -e "${BLUE}  Running npx prisma generate...${NC}"
        npx prisma generate
        echo -e "${CHECK} Prisma client generated.${NC}"

        # Run Prisma migrations
        echo -e "${BLUE}  Running npx prisma migrate dev --name init...${NC}"
        # For a fresh setup, this should apply migrations. If schema changes are detected, it might prompt.
        npx prisma migrate dev --name init --skip-generate # --skip-generate because we just ran generate
        echo -e "${CHECK} Database migrations applied.${NC}"
    else
        echo -e "${WARNING} ${YELLOW}prisma/schema.prisma not found. Skipping Prisma database setup.${NC}"
        echo -e "${LIGHTBULB} ${YELLOW}If your project uses a different ORM or raw SQL, please set up your database manually.${NC}"
    fi
    echo ""

    # --- Code Quality (Optional) ---
    echo -e "${SPARKLES} Running code quality checks (optional)...${NC}"
    # Check for prettier script
    if grep -q '"prettier":' package.json; then
        echo -e "${BLUE}  Running npx prettier --write .${NC}"
        npx prettier --write . || echo -e "${WARNING} ${YELLOW}Prettier failed, but continuing setup.${NC}"
        echo -e "${CHECK} Code formatted with Prettier.${NC}"
    else
        echo -e "${LIGHTBULB} ${YELLOW}Prettier script not found in package.json. Skipping formatting.${NC}"
    fi

    # Check for lint script
    if grep -q '"lint":' package.json; then
        echo -e "${BLUE}  Running npm run lint...${NC}"
        npm run lint || echo -e "${WARNING} ${YELLOW}Linting failed, but continuing setup.${NC}"
        echo -e "${CHECK} Linting complete.${NC}"
    else
        echo -e "${LIGHTBULB} ${YELLOW}Lint script not found in package.json. Skipping linting.${NC}"
    fi
    echo ""

    # --- Final Start Command ---
    echo -e "${GREEN}${CHECK} Setup complete!${NC}"
    echo ""
    echo -e "${LIGHTBULB} ${YELLOW}Next steps:${NC}"
    echo -e "1. ${YELLOW}Ensure your .env file is fully configured with all required keys.${NC}"
    echo -e "2. ${YELLOW}If you updated .env, you might need to re-run 'npx prisma migrate dev' if your DATABASE_URL changed.${NC}"
    echo -e "3. ${YELLOW}Start the development server:${NC}"
    echo -e "   ${BLUE}npm run dev${NC}"
    echo ""
    echo -e "${LIGHTBULB} ${YELLOW}Then visit: ${BLUE}http://localhost:3000${NC}"

elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    echo -e "${PACKAGE} ${GREEN}Python project detected.${NC}"

    # --- Dependency Installation ---
    echo -e "${WRENCH} Installing dependencies..."
    if [ -f "pyproject.toml" ] && command -v poetry &> /dev/null; then
        echo -e "${BLUE}  Using Poetry...${NC}"
        poetry install
    elif [ -f "requirements.txt" ]; then
        echo -e "${BLUE}  Using pip...${NC}"
        pip install -r requirements.txt
    else
        echo -e "${ERROR} ${RED}No recognized Python dependency file (requirements.txt or pyproject.toml) or Poetry not installed.${NC}"
        echo -e "${LIGHTBULB} ${YELLOW}Please install dependencies manually.${NC}"
        exit 1
    fi
    echo -e "${CHECK} Dependencies installed.${NC}"
    echo ""

    # --- Environment Setup ---
    if [ -f ".env.example" ]; then
        if [ ! -f ".env" ]; then
            echo -e "${MEMO} Setting up environment variables..."
            cp .env.example .env
            echo -e "${CHECK} Copied .env.example to .env.${NC}"
            echo -e "${WARNING} ${YELLOW}Please edit .env and add your configuration.${NC}"
            echo -e "${LIGHTBULB} ${YELLOW}Remember: Do NOT hardcode secrets directly in your code.${NC}"
            echo ""
        else
            echo -e "${MEMO} .env file already exists. Skipping copy.${NC}"
            echo -e "${LIGHTBULB} ${YELLOW}Ensure your .env file has all necessary configurations.${NC}"
            echo ""
        fi
    else
        echo -e "${WARNING} ${YELLOW}.env.example not found. Skipping environment setup.${NC}"
        echo -e "${LIGHTBULB} ${YELLOW}Please create a .env file manually with your configuration.${NC}"
        echo ""
    fi

    # --- Database Setup (Generic Python) ---
    echo -e "${DATABASE} Setting up database (if applicable)...${NC}"
    echo -e "${LIGHTBULB} ${YELLOW}This is a generic Python setup. If your project uses Alembic, run 'alembic upgrade head'.${NC}"
    echo -e "${LIGHTBULB} ${YELLOW}If it uses raw SQL, source your schema files manually.${NC}"
    echo -e "${LIGHTBULB} ${YELLOW}Ensure your PostgreSQL database is running and accessible via your .env file.${NC}"
    echo ""

    # --- Final Start Command ---
    echo -e "${GREEN}${CHECK} Setup complete!${NC}"
    echo ""
    echo -e "${LIGHTBULB} ${YELLOW}Next steps:${NC}"
    echo -e "1. ${YELLOW}Ensure your .env file is fully configured.${NC}"
    echo -e "2. ${YELLOW}Start the development server:${NC}"
    echo -e "   ${BLUE}uvicorn main:app --reload${NC} (for FastAPI)"
    echo -e "   ${BLUE}python main.py${NC} (for other Python apps)"
    echo ""
    echo -e "${LIGHTBULB} ${YELLOW}Then visit: ${BLUE}http://localhost:8000${NC} (or your application's configured port)${NC}"

else
    echo -e "${ERROR} ${RED}Project type could not be automatically detected.${NC}"
    echo -e "${LIGHTBULB} ${YELLOW}Please ensure 'package.json' for Node.js or 'requirements.txt'/'pyproject.toml' for Python exists in the project root.${NC}"
    echo -e "${LIGHTBULB} ${YELLOW}You may need to set up the project manually.${NC}"
    exit 1
fi

echo ""
echo -e "${ROCKET} ${BLUE}Setup script finished.${NC}"
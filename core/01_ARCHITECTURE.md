# OMNI SYSTEM ARCHITECTURE

## 1. HIGH-LEVEL DESIGN
OMNI operates as a multi-agent system orchestrated by a central State Machine.
It utilizes a "Plan -> Execute -> Verify -> Refine" loop.

## 2. CORE COMPONENTS

### A. The Cortex (The Planner)
* **Input:** High-level user intent (e.g., "Create a SaaS for booking barbers").
* **Role:** Deconstructs intent into a deeply detailed **Technical Specification (PRD)** and a **Task Dependency Graph (DAG)**.
* **Output:** JSON Manifest describing every file, database schema, and API route needed.

### B. The Swarm (The Executors)
Specialized AI agents running in parallel (using asyncio/threads):
* **Scaffolder:** Sets up the repo structure, configs, and boilerplate.
* **Backend Engineer:** Implements API logic, DB schemas (Prisma/Drizzle), and Type definitions.
* **Frontend Engineer:** Implements UI components (Shadcn/Tailwind), State Management, and Client logic.
* **DevOps Engineer:** Generates Dockerfiles, CI/CD pipelines (GitHub Actions), and Terraform/Pulumi scripts.

### C. The Arbiter (The QA/Compiler)
* **Role:** Runs independently of the creators. It executes the code in a sandboxed environment.
* **Functions:**
    * Runs `tsc --noEmit` (Type Check).
    * Runs `npm test`.
    * Analyzes stderr output.
* **Feedback Loop:** If failure occurs, it passes the error log back to the specific Swarm Agent with a "FIX" directive.

### D. The Memory (Context)
* **Vector Database (Chroma/LanceDB):** Stores the semantic understanding of the codebase to prevent context window overflow.
* **Project Graph:** A structured representation of file dependencies (File A imports File B).

## 3. TECHNICAL STACK (SELF-BOOTSTRAP)
To build OMNI, we will use:
* **Language:** Python 3.12+ (for superior AI library support) or Rust (for raw CLI speed). *Recommendation: Python core with Rust bindings for heavy I/O.*
* **LLM Interface:** LiteLLM (for model agnosticism - Claude/Gemini/GPT).
* **Orchestration:** LangGraph or a custom State Machine.
* **Sandbox:** Docker (for safe code execution).
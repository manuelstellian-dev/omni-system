# CLAUDE.md - AI Assistant Guide for OMNI System

**Last Updated**: 2025-11-21
**Purpose**: Comprehensive guide for AI assistants working with the OMNI codebase
**Audience**: Claude, GPT-4, Gemini, and other AI coding assistants

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Development Workflow](#development-workflow)
4. [Key Conventions](#key-conventions)
5. [Agent Architecture](#agent-architecture)
6. [Common Operations](#common-operations)
7. [Testing Guidelines](#testing-guidelines)
8. [Troubleshooting](#troubleshooting)

---

## Project Overview

### What is OMNI?

OMNI is an **Autonomous AI Operating Environment** that transforms high-level user intent into production-ready applications. Unlike traditional AI coding assistants (Cursor, Aider, Windsurf), OMNI operates as "the force" rather than a "force multiplier" - it handles the complete Software Development Life Cycle (SDLC) from specification to deployment.

**Key Paradigm Shift**: From "Loop-in-the-Code" to "Loop-on-the-Spec"

### Core Philosophy (From 00_MANIFESTO.md)

- **Zero Friction**: From intent to deployment in one command. No manual configuration.
- **Opinionated Excellence**: Enforce strictest standards by default (TypeScript Strict, ESLint Strict)
- **Self-Healing**: Never present broken code to users - automatically fix build failures
- **Deterministic Output**: Same spec → same result
- **No Toys**: Full, robust implementation only - no placeholders or snippets
- **Complete SDLC**: Code + Tests + Documentation + Infrastructure + Deployment

### Technology Stack

```yaml
Language: Python 3.12+
LLM Interface: LiteLLM (model-agnostic: Gemini, GPT-4, Claude)
CLI Framework: Typer
Terminal UI: Rich
Data Validation: Pydantic v2
Vector DB: ChromaDB (for RAG memory)
Async: asyncio
Code Quality: Black, Pylint, MyPy
```

---

## Codebase Structure

### Directory Layout

```
omni-system/
├── core/                           # Main application code
│   ├── main.py                     # CLI entry point (Typer app)
│   ├── cortex.py                   # Intent analyzer (ProjectSpec generator)
│   ├── swarm.py                    # DAG-based parallel executor
│   ├── arbiter.py                  # Build verification agent
│   ├── repair_agent.py             # 7-strategy self-healing system
│   ├── memory_agent.py             # ChromaDB RAG context manager
│   ├── devops_agent.py             # Infrastructure code generator
│   ├── doc_engine.py               # Documentation generator
│   ├── completion_agent.py         # Setup script generator
│   ├── prompt_assembler.py         # Deterministic prompt builder
│   ├── error_patterns.json         # Known error database (18 patterns)
│   ├── requirements.txt            # Python dependencies
│   ├── pytest.ini                  # Test configuration
│   ├── tests/                      # Test suite
│   │   ├── unit/                   # Fast unit tests
│   │   └── integration/            # Full pipeline tests
│   ├── 00_MANIFESTO.md             # Core philosophy
│   ├── 01_ARCHITECTURE.md          # System design
│   └── 02_CAPABILITIES.md          # Feature list
├── .omni_memory/                   # ChromaDB persistent storage (gitignored)
├── build_output/                   # Generated projects (gitignored)
├── .github/                        # GitHub configuration
│   └── workflows/                  # CI/CD pipelines (if exists)
├── pyproject.toml                  # Python project config (Black, MyPy, Pytest)
├── .pre-commit-config.yaml         # Pre-commit hooks
├── .gitignore                      # Comprehensive ignore rules
├── README.md                       # User-facing documentation
├── PROJECT_OVERVIEW.md             # Detailed system documentation
├── CONTRIBUTING.md                 # Development guidelines
└── LICENSE                         # MIT License
```

### Key Files Explained

#### Core Application Files

- **main.py** (lines 1-400+): CLI entry point with Typer
  - Commands: `create`, `verify`, `status`
  - Orchestrates full OMNI pipeline (Cortex → Memory → Swarm → Arbiter → Repair → DevOps/Docs → Completion)
  - Handles async execution via `asyncio.run()`

- **cortex.py** (~200 lines): Strategic planner
  - Function: `analyze_intent(intent: str) -> ProjectSpec`
  - Uses LiteLLM to analyze user intent
  - Generates `ProjectSpec` with DAG execution plan
  - Returns: project_name, tech_stack, database_schema, core_features, execution_plan

- **swarm.py** (~650 lines): Parallel code executor
  - Core method: `async def execute_dag_with_memory(spec, project_dir, memory_agent)`
  - Implements DAG-based task execution with `asyncio.gather()`
  - Generates code with RAG context from Memory Agent
  - 3-5x faster than serial execution

- **arbiter.py** (~200 lines): QA and build verification
  - Method: `async def verify_and_refine(project_dir, spec)`
  - Runs build commands (npm install, npm build, tsc, pytest)
  - Generates FIX_PLAN if failures detected
  - Returns: success status + error details

- **repair_agent.py** (~400 lines): Advanced self-healing
  - **7 Progressive Strategies** (ordered by aggressiveness):
    1. Quick Fixes (98% success)
    2. Logic Error Fixes (85% success)
    3. Test Configuration Fixes (92% success)
    4. Regenerate Failing Files (75% success)
    5. Simplify Implementation (68% success)
    6. Alternative Approach (60% success)
    7. Minimal Viable Version (85% success)
  - Uses `error_patterns.json` for known patterns
  - Method: `async def self_heal_loop(project_dir, spec, max_attempts=7)`

- **memory_agent.py** (~250 lines): RAG context manager
  - Uses ChromaDB for semantic code search
  - Methods:
    - `async def a_add_document(file_path, content, metadata)`
    - `async def a_retrieve_context(query, n_results=5)`
  - Chunks code (500 chars, 50 char overlap)
  - Persistent storage in `.omni_memory/`

- **devops_agent.py** (~450 lines): Infrastructure generator
  - Generates: Dockerfile, docker-compose.yml, GitHub Actions CI/CD
  - Multi-stage Docker builds (security best practices)
  - Method: `async def generate_infrastructure(project_dir, spec)`

- **doc_engine.py** (~450 lines): Documentation generator
  - Generates: README.md, ADRs (Architecture Decision Records)
  - Method: `async def generate_documentation(project_dir, spec)`

- **completion_agent.py** (~270 lines): Setup script generator
  - Generates executable `setup.sh` with auto-detection
  - Method: `async def generate_setup_script(project_dir, spec)`

- **prompt_assembler.py** (~200 lines): Deterministic prompt builder
  - Enforces consistent prompt structure
  - Prevents common LLM mistakes (e.g., comments in JSON)

---

## Development Workflow

### Branch Strategy (Git Flow)

```
main (production-ready, protected)
├── develop (integration branch, protected)
│   ├── feature/your-feature-name
│   ├── fix/bug-description
│   ├── refactor/component-name
│   └── hotfix/critical-fix
```

### Commit Convention (Conventional Commits)

```bash
<type>(<scope>): <subject>

# Types:
feat:     New feature
fix:      Bug fix
docs:     Documentation changes
refactor: Code restructuring (no behavior change)
test:     Adding/updating tests
chore:    Maintenance tasks

# Examples:
feat(swarm): add adaptive concurrency limiter based on available RAM
fix(arbiter): handle timeout errors gracefully in verify_and_refine
docs(readme): add installation instructions for ChromaDB
```

### Development Process

1. **Always branch from `develop`**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make changes following code standards** (see below)

3. **Run pre-commit checks**:
   ```bash
   cd core
   black *.py                          # Format code
   pylint *.py --fail-under=8.0        # Lint (must score > 8.0)
   mypy *.py --ignore-missing-imports  # Type check
   pytest tests/unit/ -v               # Unit tests
   ```

4. **Commit with conventional format**:
   ```bash
   git commit -m "feat(swarm): add adaptive concurrency limiter"
   ```

5. **Push and create PR** (target: `develop` branch)

---

## Key Conventions

### Code Style Standards

#### Python Style (Enforced)

- **Formatter**: Black (line length: 100)
- **Linter**: Pylint (minimum score: 8.0)
- **Type Checker**: MyPy (strict mode)
- **Import Sorter**: isort (black profile)

#### Code Quality Requirements

```python
# ✅ GOOD: Type hints, docstrings, error handling
async def execute_task(
    self,
    task: Task,
    spec: ProjectSpec
) -> Dict[str, str]:
    """
    Execute a single task from the execution plan.

    Args:
        task: Task definition with ID, description, and dependencies
        spec: Complete project specification

    Returns:
        Dictionary mapping file paths to generated content

    Raises:
        MemoryError: If insufficient RAM available
        LLMError: If API call fails
    """
    try:
        context = await self.memory.retrieve_context(task.description)
        return await self._generate_files(task, spec, context)
    except Exception as e:
        console.print(f"[red]Task failed: {task.task_id}[/red]")
        raise

# ❌ BAD: No types, no docs, poor error handling
async def execute_task(self, task, spec):
    context = await self.memory.retrieve_context(task.description)
    return await self._generate_files(task, spec, context)
```

### File Naming Conventions

- Python files: `snake_case.py` (e.g., `memory_agent.py`)
- Test files: `test_*.py` (e.g., `test_swarm.py`)
- Documentation: `UPPER_CASE.md` (e.g., `README.md`, `CONTRIBUTING.md`)
- Core docs: Numbered (e.g., `00_MANIFESTO.md`, `01_ARCHITECTURE.md`)

### Environment Configuration

**Required Environment Variables** (`.env` file):

```bash
# Model Selection (LiteLLM format)
OMNI_MODEL=gemini/gemini-2.5-flash
# or: OMNI_MODEL=gpt-4o
# or: OMNI_MODEL=claude-3-5-sonnet

# API Keys (provide at least one)
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

**IMPORTANT**: `.env` is gitignored. Use `.env.example` as template.

---

## Agent Architecture

### The OMNI Pipeline (Sequential Flow)

```
USER INTENT
    ↓
1. CORTEX (Planner)
    ├─ Analyzes intent
    ├─ Creates ProjectSpec
    └─ Generates DAG execution plan
    ↓
2. MEMORY AGENT (RAG Context)
    ├─ Initializes ChromaDB
    └─ Prepares vector database
    ↓
3. SWARM AGENT (Executor)
    ├─ Executes DAG tasks in parallel
    ├─ Generates code with RAG context
    └─ Indexes generated code in Memory
    ↓
4. ARBITER AGENT (QA)
    ├─ Runs build commands (npm/tsc/pytest)
    ├─ Detects errors
    └─ Generates FIX_PLAN if failures
    ↓
5. REPAIR AGENT (Self-Healing) [if build failed]
    ├─ Applies 7 progressive strategies
    ├─ Re-runs build after each fix
    └─ Continues until success or exhaustion
    ↓
6. DEVOPS + DOC ENGINE (Parallel)
    ├─ DevOps: Dockerfile, CI/CD, docker-compose
    └─ DocEngine: README, ADRs
    ↓
7. COMPLETION AGENT
    └─ Generates setup.sh script
    ↓
OUTPUT: Production-Ready Application
```

### Agent Communication

Agents communicate via:
- **ProjectSpec**: Pydantic model passed between agents
- **File System**: Shared `build_output/{project_name}/` directory
- **Memory Agent**: Shared ChromaDB instance for context
- **Return Values**: Structured dictionaries/objects

---

## Common Operations

### Running OMNI Commands

#### 1. Create New Project

```bash
cd core
python main.py create "Create a task management SaaS with authentication"
```

**What happens**:
1. Cortex analyzes intent → generates ProjectSpec
2. Memory Agent initializes ChromaDB
3. Swarm executes DAG (parallel task execution)
4. Arbiter verifies build (runs npm install, npm build)
5. Repair Agent fixes errors (if any)
6. DevOps + DocEngine generate infrastructure & docs
7. Completion Agent generates setup.sh
8. Output: `build_output/task-management-saas/`

#### 2. Verify Existing Project

```bash
cd core
python main.py verify project-name
```

**Use case**: Resume verification for existing project in `build_output/`

#### 3. System Status Check

```bash
cd core
python main.py status
```

**Output**: Quick diagnostic check

### Working with Memory Agent

```python
from memory_agent import MemoryAgent

# Initialize
memory = MemoryAgent(persist_directory=".omni_memory")

# Add code to context
await memory.a_add_document(
    file_path="src/api/stripe/route.ts",
    content=stripe_webhook_code,
    metadata={"language": "typescript", "type": "api_route"}
)

# Retrieve relevant context
context = await memory.a_retrieve_context(
    query="Stripe webhook handler",
    n_results=5
)
```

### Adding New Agent

If you need to add a new agent:

1. Create `new_agent.py` in `core/`
2. Follow this structure:

```python
from pydantic import BaseModel
from rich.console import Console
import litellm

console = Console()

class NewAgent:
    """Description of agent's purpose."""

    def __init__(self):
        """Initialize agent with necessary dependencies."""
        pass

    async def execute(self, spec: ProjectSpec, project_dir: Path) -> Dict[str, Any]:
        """
        Main execution method.

        Args:
            spec: Complete project specification
            project_dir: Target directory for outputs

        Returns:
            Dictionary with results/status
        """
        console.print("[cyan]NewAgent executing...[/cyan]")
        # Implementation here
        return {"status": "success"}
```

3. Register in `main.py`:

```python
from new_agent import NewAgent

# In _create_async function:
new_agent = NewAgent()
result = await new_agent.execute(spec, project_dir)
```

---

## Testing Guidelines

### Test Structure

```
core/tests/
├── __init__.py
├── unit/                    # Fast, isolated tests
│   ├── test_cortex.py
│   ├── test_swarm.py
│   ├── test_arbiter.py
│   └── test_memory_agent.py
└── integration/             # Full pipeline tests
    └── test_full_pipeline.py
```

### Writing Tests

```python
import pytest
from swarm import SwarmAgent
from cortex import ProjectSpec

class TestSwarmAgent:
    @pytest.fixture
    def agent(self):
        """Create SwarmAgent instance for testing."""
        return SwarmAgent()

    @pytest.mark.asyncio
    async def test_execute_task_with_valid_input_returns_files(self, agent):
        """Test that execute_task returns file dictionary for valid input."""
        # Arrange
        task = Task(task_id="test", description="Create test file")
        spec = ProjectSpec(project_name="test-project")

        # Act
        result = await agent._execute_task(task, spec, Path("/tmp"), Mock())

        # Assert
        assert isinstance(result, dict)
        assert len(result) > 0
```

### Running Tests

```bash
cd core

# All tests
pytest tests/ -v

# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests (slower)
pytest tests/integration/ -v

# With coverage report
pytest tests/ -v --cov=. --cov-report=html

# Specific test file
pytest tests/unit/test_swarm.py -v

# Specific test function
pytest tests/unit/test_swarm.py::TestSwarmAgent::test_execute_task -v
```

### Test Requirements

- ✅ **Type hints** for all test functions
- ✅ **Descriptive names**: `test_<function>_<scenario>_<expected>`
- ✅ **Arrange-Act-Assert** pattern
- ✅ **Async tests** marked with `@pytest.mark.asyncio`
- ✅ **Unit tests**: No external API calls (use mocks)
- ✅ **Coverage**: Minimum 80%

---

## Troubleshooting

### Common Issues and Solutions

#### 1. LiteLLM API Errors

**Error**: `litellm.exceptions.AuthenticationError`

**Solution**:
```bash
# Check .env file exists
ls -la core/.env

# Verify API key is set
cat core/.env | grep API_KEY

# Test API key
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GEMINI_API_KEY'))"
```

#### 2. ChromaDB Errors

**Error**: `sqlite3.DatabaseError: database disk image is malformed`

**Solution**:
```bash
# Delete corrupted database
rm -rf core/.omni_memory

# Re-run OMNI (will recreate)
python main.py create "your intent"
```

#### 3. Build Verification Failures

**Error**: Arbiter reports build failures

**What happens automatically**:
- Repair Agent triggers with 7 progressive strategies
- Attempts fixes until success or exhaustion

**Manual intervention** (if needed):
```bash
# Navigate to generated project
cd build_output/project-name

# Manually run build
npm install
npm run build

# Check errors
cat package.json  # Verify dependencies
```

#### 4. Import Errors in Tests

**Error**: `ModuleNotFoundError: No module named 'cortex'`

**Solution**:
```bash
# Ensure you're in core/ directory
cd core

# Install in editable mode
pip install -e .

# Or add PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/ -v
```

#### 5. Memory/RAM Issues

**Error**: System crashes with many parallel tasks

**Solution**:
- Reduce concurrent task limit in `swarm.py`
- Current implementation uses `asyncio.gather()` without limit
- Consider implementing adaptive concurrency based on available RAM

---

## Best Practices for AI Assistants

### When Making Changes

1. **Read first, write second**:
   - Always read relevant files before modifying
   - Understand context and dependencies

2. **Maintain agent separation**:
   - Each agent has a specific role
   - Don't mix responsibilities (e.g., don't add code generation to Arbiter)

3. **Preserve async patterns**:
   - All I/O operations should be async
   - Use `await` for LLM calls, file operations, ChromaDB operations

4. **Update error_patterns.json**:
   - If you discover new error patterns, add them
   - Include: pattern, category, confidence, solution

5. **Follow type safety**:
   - Use Pydantic models for structured data
   - Add type hints to all functions
   - Run MyPy before committing

6. **Test your changes**:
   - Write unit tests for new functions
   - Run full test suite before PR

### When Debugging

1. **Check logs**:
   ```bash
   # Look for *.log files in core/
   ls -la core/*.log

   # Check recent logs
   tail -f core/omni.log
   ```

2. **Use Rich console for debugging**:
   ```python
   from rich.console import Console
   console = Console()
   console.print(f"[yellow]Debug: {variable}[/yellow]")
   ```

3. **Inspect ProjectSpec**:
   ```bash
   # Each project saves its spec
   cat build_output/project-name/project_spec.json | jq
   ```

### When Adding Features

1. **Document in ADR format** (for major decisions):
   ```markdown
   # ADR-XXX: Feature Name

   ## Status: Proposed/Accepted/Deprecated
   ## Context: [Why needed]
   ## Decision: [What was chosen]
   ## Rationale: [Why this choice]
   ## Consequences:
     - Positive: [Benefits]
     - Negative: [Trade-offs]
   ## Alternatives Considered: [Other options]
   ```

2. **Update CHANGELOG.md**:
   - Follow semantic versioning
   - List breaking changes prominently

3. **Update documentation**:
   - README.md (if user-facing)
   - CLAUDE.md (if architecture changed)
   - Docstrings (for public APIs)

---

## Quick Reference

### File Locations Cheat Sheet

| Need to... | File Location |
|------------|---------------|
| Modify CLI commands | `core/main.py` |
| Change intent analysis | `core/cortex.py` |
| Adjust parallel execution | `core/swarm.py` |
| Modify build verification | `core/arbiter.py` |
| Add repair strategies | `core/repair_agent.py` |
| Configure RAG context | `core/memory_agent.py` |
| Change Docker templates | `core/devops_agent.py` |
| Modify README generation | `core/doc_engine.py` |
| Update setup script logic | `core/completion_agent.py` |
| Add known error patterns | `core/error_patterns.json` |
| Configure code quality | `pyproject.toml` |
| Change test settings | `core/pytest.ini` |
| View core philosophy | `core/00_MANIFESTO.md` |
| Understand architecture | `core/01_ARCHITECTURE.md` |
| See feature list | `core/02_CAPABILITIES.md` |

### Command Cheat Sheet

```bash
# Development
cd core
black *.py                          # Format
pylint *.py --fail-under=8.0        # Lint
mypy *.py --ignore-missing-imports  # Type check
pytest tests/ -v                    # Test

# OMNI Operations
python main.py create "intent"      # Create project
python main.py verify project-name  # Verify existing
python main.py status               # Health check

# Git Operations
git checkout develop                # Switch to develop
git checkout -b feature/name        # New feature branch
git commit -m "feat(scope): msg"    # Conventional commit
git push origin feature/name        # Push feature
```

### Environment Variables

```bash
# Required
OMNI_MODEL=gemini/gemini-2.5-flash  # or gpt-4o, claude-3-5-sonnet
GEMINI_API_KEY=your_key             # or OPENAI_API_KEY, ANTHROPIC_API_KEY

# Optional
LOG_LEVEL=INFO                      # DEBUG, INFO, WARNING, ERROR
MAX_REPAIR_ATTEMPTS=7               # Number of repair strategies
```

---

## Additional Resources

### Documentation Files

- **README.md**: User-facing installation and usage guide
- **PROJECT_OVERVIEW.md**: Comprehensive system documentation
- **CONTRIBUTING.md**: Development workflow and standards
- **CHANGELOG.md**: Version history and release notes
- **core/00_MANIFESTO.md**: Core philosophy and principles
- **core/01_ARCHITECTURE.md**: System architecture design
- **core/02_CAPABILITIES.md**: Feature list and capabilities
- **core/FIXES_SUMMARY.md**: Historical fixes and lessons learned

### External Links

- **LiteLLM Docs**: https://docs.litellm.ai/
- **ChromaDB Docs**: https://docs.trychroma.com/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Typer Docs**: https://typer.tiangolo.com/
- **Rich Docs**: https://rich.readthedocs.io/

---

## Summary

This guide provides AI assistants with:

✅ Complete understanding of OMNI's architecture
✅ File locations and responsibilities
✅ Development workflow and conventions
✅ Testing guidelines and best practices
✅ Troubleshooting common issues
✅ Quick reference for common operations

**Key Principle**: OMNI is a production-ready, self-healing, autonomous AI system. Every change should maintain this standard of excellence.

---

**Last Updated**: 2025-11-21
**Maintained by**: Manuel Stellian (@manuelstellian-dev)
**License**: MIT

---

*This document is continuously updated. When making significant architectural changes, update this guide accordingly.*

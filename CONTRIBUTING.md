# Contributing to OMNI

**Welcome to OMNI - The Autonomous AI Operating Environment!**

This document outlines the development workflow and standards for contributing to OMNI.

---

## 🏗️ Project Philosophy

OMNI is not just a tool - it's a **paradigm shift** in software development. Every contribution must uphold:

- ✅ **Zero Friction** - From intent to deployment in one command
- ✅ **Opinionated Excellence** - Enforce strictest standards by default
- ✅ **Self-Healing** - Never present broken state to users
- ✅ **Production-Ready** - Every feature must be enterprise-grade

---

## 🌳 Branch Strategy

We follow **Git Flow** with strict protection rules:

```
main (production-ready, protected)
├── develop (integration branch, protected)
│   ├── feature/your-feature-name
│   ├── fix/bug-description
│   ├── refactor/component-name
│   └── hotfix/critical-fix
```

### Branch Naming Convention

- `feature/` - New features (e.g., `feature/adaptive-concurrency`)
- `fix/` - Bug fixes (e.g., `fix/memory-leak-swarm`)
- `refactor/` - Code improvements (e.g., `refactor/cortex-prompt-builder`)
- `hotfix/` - Critical production fixes (e.g., `hotfix/oom-crash`)
- `docs/` - Documentation only (e.g., `docs/update-readme`)
- `test/` - Test additions (e.g., `test/swarm-integration`)

---

## 🔄 Development Workflow

### 1. Create Feature Branch

```bash
# Always branch from develop
git checkout develop
git pull origin develop

# Create your feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow these principles:
- **Small, atomic commits** - One logical change per commit
- **Test as you go** - Write tests before or alongside code
- **Document public APIs** - Docstrings for all public methods
- **Type hints required** - Use Python type annotations

### 3. Commit with Conventional Commits

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```bash
# Format:
<type>(<scope>): <subject>

# Types:
feat:     New feature
fix:      Bug fix
docs:     Documentation changes
style:    Code formatting (no logic change)
refactor: Code restructuring (no behavior change)
test:     Adding or updating tests
chore:    Maintenance tasks
perf:     Performance improvements
ci:       CI/CD changes

# Examples:
git commit -m "feat(swarm): add adaptive concurrency limiter based on available RAM"
git commit -m "fix(arbiter): handle timeout errors gracefully in verify_and_refine"
git commit -m "docs(readme): add installation instructions for ChromaDB"
git commit -m "test(memory): add unit tests for RAG context retrieval"
git commit -m "refactor(cortex): extract DAG validation to separate method"
```

### 4. Run Pre-Commit Checks

Before pushing, ensure:

```bash
# Code formatting
cd core
black *.py

# Linting (must pass with score > 8.0)
pylint *.py --fail-under=8.0

# Type checking
mypy *.py --ignore-missing-imports

# Unit tests
pytest tests/unit/ -v

# Integration tests (if applicable)
pytest tests/integration/ -v
```

### 5. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create PR on GitHub:
# - Base: develop
# - Compare: feature/your-feature-name
# - Title: Same as commit message (e.g., "feat(swarm): add adaptive concurrency")
# - Description: Detailed explanation, screenshots, breaking changes
```

### 6. Code Review Process

- ✅ **CI must pass** - All checks green
- ✅ **At least 1 approval** required
- ✅ **No merge conflicts** - Rebase if needed
- ✅ **Tests included** - New features must have tests
- ✅ **Documentation updated** - Public API changes need docs

### 7. Merge Strategy

- **Squash and merge** for feature branches (clean history)
- **Merge commit** for hotfixes (preserve urgency context)
- **Delete branch** after merge (keep repo clean)

---

## 📏 Code Standards

### Python Style Guide

We enforce **strict standards** automatically:

- ✅ **Black** for formatting (line length: 100)
- ✅ **Pylint** for linting (minimum score: 8.0)
- ✅ **MyPy** for type checking
- ✅ **isort** for import sorting

### Code Quality Requirements

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

### Testing Requirements

- ✅ **Unit tests** for all new functions/methods
- ✅ **Integration tests** for agent interactions
- ✅ **Coverage** minimum: 80%
- ✅ **Test naming**: `test_<function>_<scenario>_<expected>`

```python
# Example test structure
import pytest
from swarm import SwarmAgent

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

---

## 🚀 CI/CD Pipeline

### Continuous Integration (on Push/PR)

1. **Linting** - Black, Pylint, MyPy
2. **Unit Tests** - Fast tests, no external dependencies
3. **Integration Tests** - Full agent pipeline tests
4. **Security Scan** - Bandit for vulnerabilities
5. **Coverage Report** - Must maintain > 80%

### Continuous Deployment (on Merge to main)

1. **Deploy to Staging** - Test environment
2. **Smoke Tests** - Basic health checks
3. **Deploy to Production** - If all green
4. **Create Release** - Semantic versioning

---

## 🐛 Bug Reports

When reporting bugs, include:

1. **OMNI version** - Git commit hash
2. **Environment** - OS, Python version, RAM
3. **Reproduction steps** - Exact commands run
4. **Expected vs Actual** - What should happen vs what did
5. **Logs** - Error traces, memory usage
6. **Minimal example** - Simplest case that reproduces bug

---

## 💡 Feature Requests

When proposing features:

1. **Problem Statement** - What pain point does this solve?
2. **Proposed Solution** - High-level design
3. **Alternatives Considered** - Why this approach?
4. **Breaking Changes** - Does it affect existing users?
5. **Implementation Plan** - Rough estimate of effort

---

## 📚 Documentation

### When to Update Docs

- ✅ New public API methods
- ✅ Changed behavior in existing features
- ✅ New CLI commands or flags
- ✅ Architecture changes
- ✅ Breaking changes

### Documentation Standards

- **Docstrings** - Google style for all public methods
- **README** - Keep installation and quick start updated
- **ADRs** - Document major architectural decisions
- **CHANGELOG** - Update for every release

---

## 🔒 Security

- ❌ **Never commit secrets** - Use `.env` files (gitignored)
- ❌ **Never commit API keys** - Use environment variables
- ✅ **Report vulnerabilities privately** - Email maintainers first
- ✅ **Run security scans** - Bandit checks automatically

---

## 📞 Getting Help

- **GitHub Issues** - For bug reports and feature requests
- **GitHub Discussions** - For questions and community support
- **Code Review** - Tag maintainers in PRs for review

---

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

---

## ⚖️ License

By contributing to OMNI, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

**Thank you for contributing to OMNI and helping revolutionize software development! 🚀**

---

*Last Updated: 2025-11-21*
*Maintainer: Manuel Stellian (@manuelstellian-dev)*

# OMNI TODO List

**Last Updated**: 2025-11-21  
**Maintainer**: Manuel Stellian (@manuelstellian-dev)

---

## 🔴 CRITICAL (Priority 1) - In Progress

### PHASE 1: LTS Package Management & Compatibility System
**Issue**: Package version conflicts, breaking changes, and incompatibilities reduce build success rate  
**Root Cause**: No version pinning, no compatibility checking, no LTS preference  
**Impact**: Build success ~30%, frequent dependency conflicts, manual fixes required  

**Branch**: `feature/lts-package-management`  
**Assignee**: @manuelstellian-dev  
**Status**: 🚧 IN PROGRESS

#### Expected Improvements
- ✅ Build success: **30% → 70%** (⬆️ +40%)
- ✅ Package conflicts: **-90%** (⬇️ dramatically reduced)
- ✅ Stability: **Enterprise-grade** 🏆
- ✅ Auto-recovery: Breaking changes detected and handled

#### Implementation Plan

##### **1. LTS Package Version Database** 
- [ ] Create `core/lts_versions.json` with LTS versions for major ecosystems:
  - **Node.js**: 18.x, 20.x (prefer 20.x)
  - **React**: 18.x (stable)
  - **Next.js**: 14.x (stable, 15.x if specified)
  - **Python**: 3.11, 3.12
  - **TypeScript**: 5.x
  - **Prisma**: 5.x
  - **Database patterns**: Known-good version combinations

##### **2. Breaking Changes Detection System**
- [ ] Create `core/breaking_changes.json` database:
  - Known breaking changes between versions
  - Migration guides (URLs to docs)
  - Severity levels (critical, high, medium)
  - Auto-fix strategies when possible

##### **3. Compatibility Matrix Engine**
- [ ] Create `core/compatibility_checker.py`:
  - Check package combinations against known conflicts
  - Validate peer dependencies
  - Suggest compatible version sets
  - Warn about untested combinations

##### **4. Auto-Downgrade Strategy**
- [ ] Implement in Arbiter Agent (`core/arbiter.py`):
  - When build fails due to version conflict → detect it
  - Look up compatible versions from matrix
  - Generate fix with downgrade to LTS/compatible versions
  - Apply fix and retry build
  - Log downgrade decision for learning

##### **5. Integration with Swarm Agent**
- [ ] Update `core/swarm.py`:
  - Before generating `package.json` → consult LTS database
  - Prefer LTS versions unless user explicitly requests specific version
  - Add version justification in generated files (comments)
  - Flag potential breaking changes in logs

#### Testing Requirements

- [ ] **Unit Tests** (`tests/unit/test_lts_versions.py`)
  - Test LTS version lookup for different ecosystems
  - Test compatibility matrix validation
  - Test breaking changes detection
  - Test version parsing and comparison

- [ ] **Unit Tests** (`tests/unit/test_compatibility_checker.py`)
  - Test known conflict detection
  - Test version suggestion logic
  - Test peer dependency validation

- [ ] **Integration Tests** (`tests/integration/test_arbiter_downgrade.py`)
  - Test auto-downgrade on version conflict
  - Test build retry after downgrade
  - Test learning from successful downgrades
  - Verify fix generation quality

#### Acceptance Criteria

- ✅ LTS versions database complete for major ecosystems
- ✅ Breaking changes database with top 20 known issues
- ✅ Compatibility checker validates package combinations
- ✅ Arbiter auto-downgrades on version conflicts
- ✅ Build success rate improves to 60-70%
- ✅ All unit tests pass with > 80% coverage
- ✅ Integration tests verify auto-recovery works
- ✅ Documentation updated with version strategy

#### Related Files

- `core/lts_versions.json` - NEW: LTS version database
- `core/breaking_changes.json` - NEW: Breaking changes database
- `core/compatibility_checker.py` - NEW: Compatibility matrix engine
- `core/arbiter.py` - MODIFY: Add auto-downgrade logic
- `core/swarm.py` - MODIFY: Integrate LTS preference
- `README.md` - UPDATE: Document version strategy

---

## 🟠 HIGH (Priority 2)

### Setup Comprehensive Test Suite

- [ ] Create test directory structure
  ```
  core/tests/
  ├── __init__.py
  ├── unit/
  │   ├── __init__.py
  │   ├── test_cortex.py
  │   ├── test_swarm.py
  │   ├── test_arbiter.py
  │   ├── test_memory_agent.py
  │   ├── test_repair_agent.py
  │   └── test_swarm_concurrency.py (NEW)
  ├── integration/
  │   ├── __init__.py
  │   ├── test_full_pipeline.py
  │   └── test_swarm_memory_safety.py (NEW)
  └── fixtures/
      └── sample_specs.py
  ```

- [ ] Write unit tests for existing agents
  - Cortex: Intent parsing, DAG validation
  - Swarm: Task execution, file generation
  - Arbiter: Build verification, fix plan generation
  - Memory: ChromaDB operations, context retrieval
  - Repair: Strategy selection, error handling

- [ ] Setup pytest configuration
  ```bash
  # core/pytest.ini
  [pytest]
  testpaths = tests
  python_files = test_*.py
  python_classes = Test*
  python_functions = test_*
  addopts = -v --cov=. --cov-report=term-missing
  ```

- [ ] Configure code coverage minimum (80%)

### Setup Pre-Commit Hooks

- [ ] Install pre-commit framework
  ```bash
  pip install pre-commit
  ```

- [ ] Create `.pre-commit-config.yaml`
  - Black formatting
  - isort import sorting
  - Pylint linting
  - MyPy type checking
  - Trailing whitespace removal

- [ ] Install hooks
  ```bash
  pre-commit install
  pre-commit run --all-files
  ```

### Document Development Workflow

- [ ] Create `.env.example` with all required variables
- [ ] Add "Development Setup" section to README
- [ ] Create CHANGELOG.md for version tracking
- [ ] Add LICENSE file (MIT recommended)

---

## 🟡 MEDIUM (Priority 3)

### Improve Error Patterns Database

- [ ] Expand `error_patterns.json` to 30+ patterns
- [ ] Add success rate tracking
- [ ] Implement pattern learning (update from successful repairs)
- [ ] Add pattern versioning

### Add More Agent Tests

- [ ] DevOps Agent: Docker/CI/CD generation tests
- [ ] Doc Engine: README/ADR generation tests
- [ ] Completion Agent: setup.sh generation tests
- [ ] Prompt Assembler: Prompt structure validation

### Performance Optimization

- [ ] Profile LLM API calls (identify bottlenecks)
- [ ] Cache frequently used prompts
- [ ] Optimize ChromaDB queries
- [ ] Add request batching where possible

### Monitoring & Observability

- [ ] Add structured logging (JSON format)
- [ ] Implement metrics collection
  - Task execution time
  - Memory usage per task
  - LLM API latency
  - Success/failure rates

- [ ] Create dashboard for monitoring
  - Grafana integration
  - Real-time progress tracking

---

## 🟢 LOW (Priority 4)

### Enhanced Documentation

- [ ] Add API documentation (Sphinx)
- [ ] Create video tutorials
- [ ] Add architecture diagrams (PlantUML/Mermaid)
- [ ] Document common troubleshooting scenarios

### Community Features

- [ ] Create CONTRIBUTORS.md
- [ ] Add CODE_OF_CONDUCT.md
- [ ] Setup GitHub Discussions
- [ ] Create issue templates
  - Bug report template
  - Feature request template
  - Question template

### Future Enhancements

- [ ] Web UI for OMNI
- [ ] VS Code extension
- [ ] Plugin system for custom agents
- [ ] Multi-project workspace support
- [ ] Cost tracking and optimization

---

## ✅ COMPLETED

### Git & CI/CD Infrastructure
- [x] Initialize Git repository
- [x] Create `.gitignore` comprehensive
- [x] Setup branch strategy (main, develop, feature/)
- [x] Create baseline commit
- [x] Create CONTRIBUTING.md with workflow
- [x] Create README.md with full documentation
- [x] Setup GitHub Actions CI pipeline
- [x] Setup GitHub Actions CD pipeline
- [x] Create TODO.md for task tracking

---

## 📋 NOTES

### Development Standards Enforced

- **Code Style**: Black (line length: 100)
- **Linting**: Pylint (minimum score: 7.0, targeting 8.0)
- **Type Checking**: MyPy (no strict optional)
- **Testing**: pytest with coverage > 80%
- **Commits**: Conventional Commits format
- **Branching**: Git Flow strategy

### Current Baseline

- **Commit**: `6f7d82a` - Initial baseline before refactoring
- **Branch**: `main` (protected, production-ready)
- **Status**: Clean working tree, CI/CD setup complete

### Next Immediate Steps

1. ✅ Commit CI/CD setup
2. 🚧 Create feature branch: `feature/adaptive-concurrency-limiter`
3. 🚧 Implement adaptive concurrency fix
4. 🚧 Write comprehensive tests
5. 🚧 Create PR for review
6. 🚧 Merge to develop after CI passes

---

**Remember**: Every change goes through feature branch → PR → CI → Review → Merge

This is **enterprise-grade development** - no shortcuts, no cowboy coding! 🎯

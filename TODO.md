# OMNI TODO List

**Last Updated**: 2025-11-21  
**Maintainer**: Manuel Stellian (@manuelstellian-dev)

---

## 🔴 CRITICAL (Priority 1) - In Progress

### Fix: Memory Overflow with Parallel Task Execution
**Issue**: System crashes (OOM Killer, exit code 137) when executing 15+ tasks concurrently  
**Root Cause**: Unlimited concurrency in `swarm.py` → all "ready" tasks execute simultaneously  
**Impact**: RAM 100%, CPU 93%, GPU 92% → System kills process  

**Branch**: `feature/adaptive-concurrency-limiter`  
**Assignee**: @manuelstellian-dev  
**Status**: 🚧 TODO (blocked by CI/CD setup completion)

#### Implementation Plan

- [ ] **Install psutil** for memory monitoring
  ```bash
  cd core
  pip install psutil
  echo "psutil>=5.9.0" >> requirements.txt
  ```

- [ ] **Add adaptive concurrency calculation** to `SwarmAgent.__init__()`
  - Calculate optimal concurrency based on available RAM
  - Formula: `available_ram_gb / 1.5` capped at 8 tasks max
  - Support ENV override: `OMNI_MAX_CONCURRENT_TASKS`

- [ ] **Implement semaphore-based limiting**
  - Add `self.semaphore = asyncio.Semaphore(max_concurrent_tasks)`
  - Create wrapper: `_execute_task_with_safety()`
  - Wrap existing `_execute_task()` with semaphore

- [ ] **Add memory monitoring during execution**
  - Check RAM usage before each task
  - Pause if memory > 85% (cooling down)
  - Auto-fallback to sequential if MemoryError

- [ ] **Add graceful degradation**
  - Try parallel first
  - Catch MemoryError → switch to serial
  - Continue execution without crash

#### Testing Requirements

- [ ] **Unit Tests** (`tests/unit/test_swarm_concurrency.py`)
  - Test concurrency calculation for different RAM levels
  - Test ENV override works correctly
  - Test semaphore actually limits concurrent tasks
  - Mock psutil to simulate memory conditions

- [ ] **Integration Tests** (`tests/integration/test_swarm_memory_safety.py`)
  - Test with small project (2-3 tasks) → should succeed
  - Test with large project (15+ tasks) → should not crash
  - Verify memory usage stays < 80%
  - Verify execution time is reasonable

#### Acceptance Criteria

- ✅ System does NOT crash with 15+ task projects
- ✅ RAM usage stays < 80% during execution
- ✅ All unit tests pass
- ✅ Integration test with large project succeeds
- ✅ Code coverage > 80% for new code
- ✅ Documentation updated (docstrings)
- ✅ README updated with new ENV variable

#### Related Files

- `core/swarm.py` - Main implementation
- `core/requirements.txt` - Add psutil
- `.env.example` - Document new ENV variable
- `README.md` - Update configuration section

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

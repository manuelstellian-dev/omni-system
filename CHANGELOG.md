# Changelog

All notable changes to OMNI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Adaptive concurrency limiter in SwarmAgent to prevent OOM crashes
- Memory monitoring with psutil integration
- Semaphore-based task limiting (1-8 concurrent tasks based on available RAM)
- Graceful degradation to sequential execution on MemoryError
- Environment variable `OMNI_MAX_CONCURRENT_TASKS` for manual override
- Comprehensive unit tests for concurrency logic
- Pre-commit hooks configuration
- MIT License
- This CHANGELOG

### Fixed
- Memory overflow crash (OOM Killer, exit code 137) when executing 15+ tasks concurrently
- System killing OMNI process due to unlimited parallelism

### Changed
- SwarmAgent now uses adaptive concurrency instead of unlimited parallel execution
- Task execution includes memory pressure monitoring

## [0.1.0] - 2025-11-21

### Added
- Initial OMNI system baseline
- Multi-agent architecture (8 core agents):
  - Cortex (strategic planner with DAG execution)
  - Swarm (parallel code executor)
  - Arbiter (QA verifier with build automation)
  - Repair Agent (7-strategy self-healing)
  - Memory Agent (RAG with ChromaDB)
  - DevOps Agent (infrastructure as code)
  - Doc Engine (documentation generator)
  - Completion Agent (setup script creator)
- DAG-based task execution with dependency resolution
- RAG memory system with ChromaDB
- 7-strategy progressive self-healing system
- Error patterns database (18 known patterns)
- GitHub Actions CI/CD pipeline
- Comprehensive documentation (README, CONTRIBUTING, PROJECT_OVERVIEW)
- Test infrastructure (pytest with 80% coverage requirement)
- Enterprise development workflow (Git Flow, Conventional Commits)

### Infrastructure
- Git repository with branch strategy (main, develop, feature/)
- GitHub Actions CI (lint, security, test, build)
- GitHub Actions CD (staging, production, releases)
- Code quality enforcement (Black, Pylint, MyPy, Bandit)
- Test directory structure (unit, integration, fixtures)
- Configuration templates (.env.example, pytest.ini)

---

## Release Notes Guidelines

### Version Number Format
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Categories
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

### Links
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)

# OMNI - Autonomous AI Operating Environment

<div align="center">

**From Intent to Production in One Command**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Contributing](#-contributing)

</div>

---

## 🎯 What is OMNI?

OMNI is an **Autonomous AI Operating Environment** that transforms high-level user intent into production-ready applications with **zero manual configuration**.

Unlike traditional AI coding assistants (Cursor, Aider, Windsurf), OMNI operates as **"the force"** rather than a "force multiplier" - it handles the complete Software Development Life Cycle (SDLC) from specification to deployment.

### Key Differentiator

Move from **"Loop-in-the-Code"** to **"Loop-on-the-Spec"**

---

## ✨ Features

### 🧠 Multi-Agent Architecture
- **Cortex** - Strategic planner (intent → execution DAG)
- **Swarm** - Parallel code executor with DAG-based task execution
- **Arbiter** - QA verifier with build automation
- **Repair Agent** - 7-strategy progressive self-healing
- **Memory Agent** - RAG context with ChromaDB
- **DevOps Agent** - Infrastructure as Code generator
- **Doc Engine** - Professional documentation generator
- **Completion Agent** - Automated setup script creation

### 🚀 Production-Ready Output
- ✅ Full codebase with tests
- ✅ Docker multi-stage builds
- ✅ GitHub Actions CI/CD
- ✅ OpenTelemetry monitoring
- ✅ Comprehensive documentation
- ✅ Executable setup scripts

### 🔧 Self-Healing System
- **7 Progressive Repair Strategies**
- **Error Pattern Database** (18+ known patterns)
- **Automatic Build Verification**
- **85%+ Success Rate** in first 3 strategies

### 📊 Performance
- **Parallel Task Execution** - 3-5x faster than serial
- **DAG-Based Orchestration** - Optimal dependency resolution
- **RAG Memory** - Context-aware code generation
- **Adaptive Concurrency** - Intelligent resource management

---

## 🏗️ Architecture

```
┌─────────────┐
│   USER      │ "Create a SaaS platform..."
└──────┬──────┘
       ▼
┌─────────────────────────────────────┐
│ CORTEX (Planner)                    │
│ - Analyzes intent                   │
│ - Creates ProjectSpec + DAG         │
└──────┬──────────────────────────────┘
       ▼
┌─────────────────────────────────────┐
│ MEMORY AGENT (RAG)                  │
│ - ChromaDB vector database          │
│ - Semantic code retrieval           │
└──────┬──────────────────────────────┘
       ▼
┌─────────────────────────────────────┐
│ SWARM AGENT (Executor)              │
│ - DAG-based parallel execution      │
│ - Generates code with RAG context   │
└──────┬──────────────────────────────┘
       ▼
┌─────────────────────────────────────┐
│ ARBITER (QA)                        │
│ - Build verification                │
│ - Error detection                   │
└──────┬──────────────────────────────┘
       ▼ (if failed)
┌─────────────────────────────────────┐
│ REPAIR AGENT (Self-Healing)         │
│ - 7 progressive strategies          │
│ - Auto-fixes until success          │
└──────┬──────────────────────────────┘
       ▼
┌─────────────────────────────────────┐
│ DEVOPS + DOC ENGINE (Parallel)      │
│ - Infrastructure as Code            │
│ - Professional documentation        │
└──────┬──────────────────────────────┘
       ▼
┌─────────────────────────────────────┐
│ COMPLETION AGENT                    │
│ - Generates setup.sh script         │
└──────┬──────────────────────────────┘
       ▼
   OUTPUT: Production-Ready App
```

---

## 📦 Installation

### Prerequisites

- Python 3.12+
- pip
- Git
- Gemini/OpenAI/Anthropic API key

### Quick Install

```bash
# Clone repository
git clone https://github.com/manuelstellian-dev/omni-system.git
cd omni-system/core

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API key:
# OMNI_MODEL=gemini/gemini-2.5-flash
# GEMINI_API_KEY=your_key_here
```

### Verify Installation

```bash
python main.py status
# Expected output: "System Operational. Core logic standby."
```

---

## 🎮 Usage

### Create a New Project

```bash
python main.py create "Create a task management SaaS with authentication"
```

### Advanced Example

```bash
python main.py create "I want a multi-tenant SaaS boilerplate with Next.js 15, \
Prisma ORM, Stripe subscriptions, NextAuth, Tailwind CSS, CI/CD via GitHub Actions, \
Docker deployment, and OpenTelemetry monitoring"
```

### Resume Verification

```bash
python main.py verify project-name
```

### Output Structure

```
build_output/your-project/
├── src/               # Application source code
├── tests/             # Unit and integration tests
├── prisma/            # Database schema
├── .github/           # CI/CD workflows
├── Dockerfile         # Multi-stage build
├── docker-compose.yml # Local development
├── README.md          # Project documentation
├── docs/adr/          # Architecture Decision Records
└── setup.sh           # Automated setup script ⭐
```

### Run the Generated Project

```bash
cd build_output/your-project
./setup.sh
# Follow the setup script instructions
```

---

## 🧪 Development

### Run Tests

```bash
cd core
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black *.py

# Lint
pylint *.py --fail-under=8.0

# Type check
mypy *.py --ignore-missing-imports
```

### Run with Debug Mode

```bash
python main.py create "your intent" --verbose
```

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| **Parallel Task Execution** | 3-5x faster than serial |
| **Memory Indexing** | ~150 code chunks per project |
| **Repair Success Rate** | 85% in first 3 strategies |
| **Error Patterns Database** | 18 known patterns |
| **Concurrency** | Adaptive (1-8 tasks based on RAM) |

---

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development workflow
- Branch strategy
- Code standards
- Testing requirements
- PR process

---

## 🗺️ Roadmap

### Phase 1: Stability (Current)
- [x] Multi-agent orchestration
- [x] DAG-based execution
- [x] Self-healing system
- [ ] Adaptive concurrency limiter
- [ ] Comprehensive test coverage

### Phase 2: Deployment
- [ ] Railway integration
- [ ] Vercel deployment
- [ ] AWS/GCP support
- [ ] One-command production deploy

### Phase 3: Intelligence
- [ ] Learning loop (RepairAgent)
- [ ] Cross-project context sharing
- [ ] Pattern recognition
- [ ] Cost optimization

### Phase 4: Collaboration
- [ ] Multi-user support
- [ ] Real-time progress tracking
- [ ] Web dashboard UI

---

## 📚 Documentation

- [Project Overview](PROJECT_OVERVIEW.md) - Complete system architecture
- [Contributing Guide](CONTRIBUTING.md) - Development workflow
- [Manifesto](core/00_MANIFESTO.md) - Core philosophy
- [Architecture](core/01_ARCHITECTURE.md) - System design
- [Capabilities](core/02_CAPABILITIES.md) - Feature list

---

## 🐛 Known Issues

See [GitHub Issues](https://github.com/manuelstellian-dev/omni-system/issues) for current bugs and feature requests.

### Critical (Being Fixed)
- [ ] Memory overflow with 15+ parallel tasks ([#1](https://github.com/manuelstellian-dev/omni-system/issues/1))

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

Built with:
- [LiteLLM](https://github.com/BerriAI/litellm) - Model-agnostic LLM interface
- [ChromaDB](https://github.com/chroma-core/chroma) - Vector database for RAG
- [Typer](https://github.com/tiangolo/typer) - CLI framework
- [Rich](https://github.com/Textualize/rich) - Terminal formatting
- [Pydantic](https://github.com/pydantic/pydantic) - Data validation

---

## 📧 Contact

**Maintainer**: Manuel Stellian ([@manuelstellian-dev](https://github.com/manuelstellian-dev))

**Project**: [github.com/manuelstellian-dev/omni-system](https://github.com/manuelstellian-dev/omni-system)

---

<div align="center">

**OMNI - Revolutionizing Software Development, One Command at a Time** 🚀

*Last Updated: 2025-11-21*

</div>

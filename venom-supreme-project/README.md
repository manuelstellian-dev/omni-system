# VENOM Supreme

**The World's First Sentient AI Terminal Orchestrator**

> Transform natural language into executable plans. Orchestrate multiple AI models. Evolve continuously. Work offline. Stay under budget.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Go Version](https://img.shields.io/badge/Go-1.22+-00ADD8?logo=go)](https://go.dev)
[![Status](https://img.shields.io/badge/Status-MVP_In_Development-yellow)]()

---

## 🌟 What is VENOM?

VENOM Supreme is not just another AI CLI. It's an **intelligent orchestration system** that understands what you want to do, plans how to do it, selects the best AI models for each step, executes the plan, learns from the results, and remembers everything.

**Instead of this:**
```bash
# Traditional approach
$ git clone https://github.com/user/repo
$ cd repo
$ npm install
$ npm test
$ npm run build
$ docker build -t app .
$ docker push app:latest
```

**You do this:**
```bash
# VENOM approach
$ venom do "deploy the app"
✓ Complete
```

VENOM:
- Understands your intent ("deploy the app")
- Generates a plan (clone → install → test → build → push)
- Selects optimal AI models for each step
- Executes everything
- Learns from the process
- Takes snapshots so you can time-travel if needed

---

## ✨ Key Features

### 🧠 **Cognitive First**
- Natural language intent parsing
- Automatic goal decomposition
- Confidence scoring with clarification
- Context-aware multi-turn conversations

### 🎯 **Intelligent Model Routing**
- Multi-objective optimization (cost, quality, latency, privacy)
- Thompson sampling for exploration/exploitation
- Automatic budget tracking and enforcement
- Support for Claude, Gemini, and local LLMs

### 💾 **Hierarchical Memory**
- Working memory (200k token context)
- Episodic memory (vector search via ChromaDB)
- Semantic memory (knowledge graph)
- Procedural memory (cached skills)
- Automatic consolidation

### ⏱️ **Time Machine**
- Automatic snapshots of all state
- Deterministic replay
- Restore to any previous point
- Diff visualization
- Causality tracking

### 🎭 **Multi-Agent Orchestration**
- Agent definitions via YAML
- Collaborative task execution
- Automatic parallelization
- Error recovery and retry

### 🛠️ **Extensible Skills**
- Built-in: git, code-exec, files, browser, embeddings
- Custom skills via plugin system
- Composite skills learned automatically
- Skill marketplace (Phase 2)

### 🔐 **Security & Privacy**
- Sandboxed execution (Docker, gVisor)
- OS-native secret management
- Audit logging
- Offline-capable (local LLMs)
- Zero-knowledge compute (Phase 2)

---

## 🚀 Quick Start

### Installation

**macOS/Linux:**
```bash
curl -sSL https://venom.dev/install.sh | sh
```

**Windows:**
```powershell
iwr https://venom.dev/install.ps1 | iex
```

**From source:**
```bash
git clone https://github.com/yourusername/venom
cd venom
make install
```

### Setup

```bash
# Initialize configuration
venom config init

# Set API keys
venom config set-key anthropic sk-ant-...
venom config set-key google ...

# Optional: Setup local LLM (offline mode)
ollama pull llama3.1:70b
venom config set models.local ollama:llama3.1
```

### Your First Command

```bash
# Ask a question
venom ask "what is 2+2"
💬 The answer is 4.

# Do something
venom do "create a Python script that prints hello world"
✓ Created: hello.py
✓ Executed: Hello, World!

# Natural conversation
venom ask "what's the capital of France"
💬 Paris

venom ask "what's its population"  # Remembers context!
💬 Approximately 2.1 million
```

---

## 📖 Usage Examples

### Simple Queries
```bash
venom ask "explain quantum computing"
venom ask "what are the best practices for API design"
venom ask "how do I optimize this SQL query: SELECT * FROM..."
```

### Code Tasks
```bash
venom do "clone https://github.com/user/repo and run tests"
venom do "refactor the auth module to use bcrypt"
venom do "add error handling to all API endpoints"
venom do "generate tests for user.go with 90% coverage"
```

### Multi-Step Workflows
```bash
venom ask "analyze my codebase and suggest improvements"

📋 Plan:
  1. Analyze file structure
  2. Check code quality
  3. Find security issues
  4. Measure test coverage
  5. Generate report

⚡ Executing (4 steps in parallel)...
✓ Complete

📊 Report:
  - 5,432 lines of code
  - Code quality: B+ (7.8/10)
  - 3 security issues found
  - Test coverage: 67%
  - Recommendations: ./improvements.md
```

### Agent-Based Workflows
```bash
# Use pre-built agents
venom agent run code-reviewer --pr 123
venom agent run security-scanner --repo ./
venom agent run test-generator --file auth.go

# Create custom agents
cat > my-agent.yml <<EOF
agent:
  name: "My Agent"
  skills: [git, code-exec]
  model: claude-opus-4.5
EOF

venom agent create --file my-agent.yml
venom agent run my-agent --task "your task here"
```

### Time Travel
```bash
# Create snapshot before risky operation
venom time snapshot --tag before-refactor

# Do something
venom do "refactor entire codebase"

# Oops, tests failed!
venom time travel --to before-refactor
✓ Restored

# Try again with different approach
venom do "refactor incrementally"
✓ Tests passing
```

### Cost Optimization
```bash
# Set budget
venom config set models.budget_daily_usd 5.00

# Check usage
venom route cost --today
📊 Used: $2.34 / $5.00
📊 Queries: 47
📊 Avg per query: $0.05

# Simulate cost before running
venom route simulate --task "complex analysis" --budget 1.00
📊 Estimated: $0.87 (within budget)
```

### Offline Mode
```bash
# Use local models (no internet required)
venom config set models.default ollama:llama3.1

venom ask "write a quicksort algorithm"
🤖 Using local model (offline)
💬 [generates code]
✓ Zero cost, 100% privacy
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│      VENOM CORE ENGINE              │
│  - Intent Understanding             │
│  - Plan Generation                  │
│  - Model Routing                    │
│  - Agent Orchestration              │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌──▼───┐  ┌──▼────┐
│Memory │  │Skills│  │ Time  │
│Cortex │  │System│  │Machine│
└───────┘  └──────┘  └───────┘
    │          │          │
┌───▼──────────▼──────────▼────┐
│     MODEL PROVIDERS           │
│  - Claude (Anthropic)         │
│  - Gemini (Google)            │
│  - Llama (Ollama/Local)       │
└───────────────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

---

## 📚 Documentation

- **[User Guide](docs/user-guide.md)** - Complete usage guide
- **[Architecture](ARCHITECTURE.md)** - System architecture
- **[API Reference](docs/api-reference.md)** - All commands and options
- **[Examples](EXAMPLES.md)** - Real-world usage examples
- **[Development](docs/development.md)** - Contributing guide
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues

---

## 🛠️ Tech Stack

- **Language:** Go 1.22+
- **CLI Framework:** Cobra + Viper
- **AI Models:** Anthropic Claude, Google Gemini, Ollama
- **Vector DB:** ChromaDB (episodic memory)
- **Cache:** Redis (procedural memory)
- **Metadata:** SQLite (local-first)
- **Execution:** Docker (sandboxing)
- **Observability:** Prometheus, OpenTelemetry

See [TECH_STACK.md](TECH_STACK.md) for complete details.

---

## 🎯 Roadmap

### ✅ Phase 0: MVP (Current - Q1 2026)
- [x] Natural language intent parsing
- [x] Multi-model support (Claude, Gemini, Ollama)
- [x] Intelligent routing (cost/quality optimization)
- [x] Memory system (working + episodic)
- [x] Core skills (git, code-exec, files)
- [x] Time machine (snapshot/restore)
- [x] Agent orchestration (basic)
- [x] Beautiful CLI UX

### 🔄 Phase 1: Intelligence (Q2 2026)
- [ ] Meta-learning (skill synthesis)
- [ ] Advanced multi-agent (swarm)
- [ ] Marketplace (plugin ecosystem)
- [ ] IDE extensions (VSCode, JetBrains)
- [ ] Web UI (optional)

### 🚀 Phase 2: Evolution (Q3 2026)
- [ ] Self-evolving agents (genetic algorithms)
- [ ] Federated learning (privacy-preserving)
- [ ] Neuromorphic execution
- [ ] Zero-knowledge compute
- [ ] Chaos engineering

### 🌟 Phase 3: Supremacy (Q4 2026)
- [ ] Predictive intent
- [ ] Causal explainability
- [ ] Global federated mesh
- [ ] Enterprise compliance (SOC2, HIPAA)

---

## 🤝 Contributing

We love contributions! Whether it's:
- 🐛 Bug reports
- 💡 Feature requests
- 📝 Documentation improvements
- 🔧 Code contributions
- 🎨 Agent templates
- 🧩 Custom skills

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📊 Metrics

### Performance Targets (MVP)
- **Intent accuracy:** >80%
- **Response latency:** <3s (cloud), <1s (local)
- **Memory recall:** >90%
- **Cost per task:** <$1.00

### Current Status (MVP Development)
- **Progress:** 65% complete
- **Target Launch:** Q1 2026
- **Test Coverage:** 73%

---

## 🌍 Community

- **GitHub:** [github.com/yourusername/venom](https://github.com/yourusername/venom)
- **Discord:** [discord.gg/venom](https://discord.gg/venom)
- **Twitter:** [@venom_ai](https://twitter.com/venom_ai)
- **Documentation:** [venom.dev/docs](https://venom.dev/docs)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- [Anthropic Claude](https://anthropic.com) - Advanced AI reasoning
- [Google Gemini](https://deepmind.google/technologies/gemini/) - Multimodal AI
- [Ollama](https://ollama.ai) - Local LLM runtime
- [Cobra](https://github.com/spf13/cobra) - CLI framework
- [ChromaDB](https://www.trychroma.com/) - Vector database

Inspired by:
- The vision of cognitive AI assistants
- The need for intelligent, autonomous development tools
- The power of human-AI collaboration

---

## ⚡ Why VENOM?

**Traditional CLIs:**
- You tell them exactly what to do
- One command = one action
- No memory, no context
- Manual orchestration
- Fixed behavior

**VENOM:**
- You tell it **what you want**
- Natural language → automated plan
- Remembers everything
- Automatic orchestration
- Learns and evolves

**It's not just faster. It's smarter.**

---

## 🚀 Get Started

```bash
# Install
curl -sSL https://venom.dev/install.sh | sh

# Setup
venom config init

# Ask
venom ask "what can you do?"

# Build
venom do "help me build something amazing"
```

---

**VENOM Supreme: The Last CLI You'll Ever Need, The First AI That Truly Understands.** 🎯

---

<p align="center">
  <strong>Star ⭐ this repo if you believe în the future of cognitive AI tools!</strong>
</p>

<p align="center">
  Made with 🧠 by developers, for developers
</p>

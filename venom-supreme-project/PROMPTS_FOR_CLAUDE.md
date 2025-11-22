# PROMPTS FOR CLAUDE CLI - VENOM Supreme
**Ready-to-Use Prompts for Each Development Phase**

---

## 🎯 HOW TO USE THIS FILE

Când lucrezi cu Claude CLI în folder-ul VENOM, copiază prompt-urile de aici pentru fiecare fază.

**Format:**
```
📋 PHASE: [Name]
🎯 GOAL: [What to achieve]
📝 PROMPT: [Copy-paste acest text la Claude]
```

---

## WEEK 1: FOUNDATION

### Day 1: Project Setup

📋 **PHASE:** Initial Project Structure
🎯 **GOAL:** Create Go project with proper structure
📝 **PROMPT:**

```
I'm building VENOM Supreme, an AI Terminal Orchestrator în Go.

Current context:
- Solo developer
- Tech stack: Go 1.22+, Cobra CLI, ChromaDB, Redis
- Target: MVP în 4 weeks
- Full blueprint available în BLUEPRINT.md

Task for today: Setup initial project structure

Please help me:
1. Initialize Go module (github.com/yourusername/venom)
2. Setup Cobra CLI framework
3. Create project structure as defined în PROJECT_STRUCTURE.md
4. Setup initial dependencies (Cobra, Viper, zerolog)
5. Create Makefile with basic targets (build, test, clean)
6. Verify: `venom --version` works

After each step, wait for my confirmation before proceeding.

Let's start with step 1.
```

---

### Day 2: Configuration System

📋 **PHASE:** Config Management
🎯 **GOAL:** Implement Viper-based configuration
📝 **PROMPT:**

```
Continuing VENOM Supreme development.

Current state:
- Project structure created ✓
- Cobra CLI works ✓

Today's goal: Configuration system (internal/config/)

Requirements (from TECH_STACK.md):
- Viper for config management
- YAML config file (~/.venom/config.yaml)
- Environment variables support
- Secrets via OS keyring (zalando/go-keyring)
- Default config generation

Please implement:
1. internal/config/config.go (Load, Save, Validate)
2. Default config structure (models, memory, security)
3. API key management (GetAPIKey, SetAPIKey via keyring)
4. `venom config init` command

Show me the code for config.go first, then I'll test it.
```

---

### Day 3: Model Adapters (Anthropic)

📋 **PHASE:** Anthropic Integration
🎯 **GOAL:** Implement Claude API adapter
📝 **PROMPT:**

```
VENOM Supreme - Day 3: Anthropic model adapter

Context:
- Config system works ✓
- Need to integrate Claude API

Task: Implement pkg/models/anthropic.go

Requirements:
- Use anthropic-sdk-go
- Unified model interface (pkg/models/interface.go)
- Support: claude-opus-4.5, claude-sonnet-4, claude-haiku-4
- Token counting
- Cost calculation (pricing în IMPLEMENTATION_ROADMAP.md)
- Streaming support (optional for MVP)

Please implement:
1. pkg/models/interface.go (ModelAdapter interface)
2. pkg/models/anthropic.go (AnthropicAdapter struct)
3. pkg/models/cost.go (calculateCost function)

Start with interface.go. Show me the code.
```

---

### Day 4: Multi-Model Support

📋 **PHASE:** Google Gemini & Ollama
🎯 **GOAL:** Complete model provider support
📝 **PROMPT:**

```
VENOM - Day 4: Complete model provider integration

Current state:
- Anthropic adapter works ✓

Today: Add Google Gemini and Ollama

Task: Implement remaining model adapters

Please create:
1. pkg/models/google.go (GoogleAdapter for Gemini)
2. pkg/models/ollama.go (OllamaAdapter for local LLMs)
3. pkg/models/factory.go (NewAdapter factory function)

All should implement the same ModelAdapter interface.

Google models: gemini-2.0-ultra, gemini-2.0-pro, gemini-2.0-flash
Ollama models: llama3.1:70b, mistral:7b, codellama:34b

Show me google.go first.
```

---

### Day 5: Intent Engine

📋 **PHASE:** Natural Language Understanding
🎯 **GOAL:** Parse user intent from natural language
📝 **PROMPT:**

```
VENOM - Day 5: Intent Engine

Context:
- All model adapters work ✓
- Can call Claude, Gemini, Ollama ✓

Today: Build intent parser (pkg/intent/)

Goal: Transform "refactor auth module" → structured Intent

Requirements (from ARCHITECTURE.md):
- Natural language parsing
- Confidence scoring (0-1)
- Goal decomposition
- Clarification when confidence <0.8

Please implement:
1. pkg/intent/parser.go (Parser struct, Parse method)
2. pkg/intent/scorer.go (ConfidenceScorer)
3. Intent struct (action, parameters, confidence, plan)

Use LLM cu structured JSON output.

Start with parser.go. Show me the implementation.
```

---

## WEEK 2: MEMORY & INTELLIGENCE

### Day 8: Vector Memory

📋 **PHASE:** ChromaDB Integration
🎯 **GOAL:** Episodic memory cu vector search
📝 **PROMPT:**

```
VENOM - Day 8: Vector Memory System

Current state:
- Week 1 complete ✓
- Intent parsing works ✓

Today: Episodic memory (pkg/memory/vector.go)

Requirements:
- ChromaDB for vector storage
- Embedding generation (via models)
- Similarity search
- Add/Search/Delete operations

ChromaDB: http://localhost:8000 (from docker-compose)

Please implement:
1. pkg/memory/vector.go (VectorStore struct)
2. Document struct (ID, Content, Metadata)
3. Methods: Add, Search, Delete
4. Embedding generation helper

Assume ChromaDB running. Show me vector.go.
```

---

### Day 9: Quantum Router

📋 **PHASE:** Intelligent Model Selection
🎯 **GOAL:** Multi-objective routing cu Thompson sampling
📝 **PROMPT:**

```
VENOM - Day 9: Quantum Router

Today: Intelligent model selection (pkg/router/)

Goal: Select optimal model bazat pe cost/quality/latency/privacy

Algorithm (from ARCHITECTURE.md):
1. Filter candidates by constraints
2. Compute Pareto frontier
3. Thompson sampling (exploration/exploitation)
4. Update statistics

Please implement:
1. pkg/router/router.go (QuantumRouter struct)
2. pkg/router/pareto.go (ComputeParetoFrontier)
3. pkg/router/thompson.go (ThompsonSample)
4. pkg/router/budget.go (BudgetTracker)

ModelCandidate struct: Provider, Model, Cost, Quality, Latency, Privacy

Start with router.go. Show me the core logic.
```

---

### Day 11: Skills Framework

📋 **PHASE:** Pluggable Skills
🎯 **GOAL:** Skills registry + built-in skills
📝 **PROMPT:**

```
VENOM - Day 11: Skills Framework

Today: Pluggable skills system (pkg/skills/)

Requirements:
- Skill interface (Name, Description, Parameters, Execute)
- Registry (register, get skills)
- Built-in skills: git, code-exec, files

Please implement:
1. pkg/skills/interface.go (Skill interface)
2. pkg/skills/registry.go (Registry struct)
3. pkg/skills/git.go (GitSkill - clone, commit, push)
4. pkg/skills/code_exec.go (CodeExecSkill - run commands)
5. pkg/skills/files.go (FilesSkill - read, write, search)

Start with interface.go and registry.go.
```

---

## WEEK 3: ORCHESTRATION

### Day 15: Multi-Agent System

📋 **PHASE:** Agent Runtime
🎯 **GOAL:** Agent lifecycle & coordination
📝 **PROMPT:**

```
VENOM - Day 15: Multi-Agent System

Current state:
- Memory system works ✓
- Skills framework ready ✓

Today: Agent orchestration (pkg/agent/)

Components needed:
- Agent struct (runtime state)
- Orchestrator (multi-agent coordination)
- Lifecycle management (create, start, stop, pause)

Agent has:
- ID, Config, Model, Skills, Memory, Router

Please implement:
1. pkg/agent/agent.go (Agent struct, Execute method)
2. pkg/agent/orchestrator.go (AgentOrchestrator)
3. pkg/agent/lifecycle.go (lifecycle methods)

Agent.Execute should:
- Parse intent
- Generate plan
- Execute plan steps
- Update memory

Show me agent.go first.
```

---

### Day 17: Time Machine

📋 **PHASE:** Snapshot & Restore
🎯 **GOAL:** Deterministic replay system
📝 **PROMPT:**

```
VENOM - Day 17: Time Machine

Today: Snapshot/restore functionality (pkg/time/)

Requirements (from ARCHITECTURE.md):
- Event-sourced architecture
- Snapshots (full state + checksum)
- Deterministic replay
- Diff computation

Please implement:
1. pkg/time/machine.go (TimeMachine struct)
2. pkg/time/snapshot.go (CreateSnapshot, Snapshot struct)
3. pkg/time/storage.go (Save, Load snapshots)
4. pkg/time/replay.go (Restore, replay events)
5. pkg/time/diff.go (ComputeDiff)

Snapshot includes:
- ID, Timestamp, AgentID, State, Checksum

Show me snapshot.go first.
```

---

### Day 19: Plan Generation

📋 **PHASE:** Automatic Planning
🎯 **GOAL:** DAG-based plan execution
📝 **PROMPT:**

```
VENOM - Day 19: Planner System

Today: Automatic plan generation (pkg/planner/)

Goal: Intent → Executable Plan cu dependencies

Plan structure:
- Steps (skill, action, params)
- DAG (dependency graph)
- Parallel execution opportunities

Please implement:
1. pkg/planner/planner.go (GeneratePlan via LLM)
2. pkg/planner/dag.go (DependencyGraph, TopologicalSort)
3. pkg/planner/optimizer.go (identify parallel steps)
4. pkg/planner/validator.go (validate plan feasibility)

GeneratePlan should:
- Use LLM to create plan from goal
- Build dependency DAG
- Optimize for parallelism
- Return executable Plan

Show me planner.go.
```

---

## WEEK 4: POLISH & LAUNCH

### Day 22: CLI UX Polish

📋 **PHASE:** Beautiful Terminal UI
🎯 **GOAL:** User-friendly CLI experience
📝 **PROMPT:**

```
VENOM - Day 22: CLI UX Improvements

Today: Polish terminal interface (internal/ui/)

Libraries:
- lipgloss (styling)
- progressbar
- survey (prompts)

Please implement:
1. internal/ui/styles.go (color schemes, formatters)
2. internal/ui/progress.go (progress bars pentru tasks)
3. internal/ui/prompts.go (interactive prompts)

Features:
- ✓ Success messages (green)
- ✗ Error messages (red)
- 💬 Info messages (blue)
- 📊 Cost/metrics formatting
- Progress bars pentru long-running tasks
- Confirmation prompts

Show me styles.go first.
```

---

### Day 24: Documentation

📋 **PHASE:** Complete Documentation
🎯 **GOAL:** User guide + API docs
📝 **PROMPT:**

```
VENOM - Day 24: Documentation

Today: Create comprehensive docs (docs/)

Please help me write:
1. docs/user-guide.md (getting started, usage, examples)
2. docs/api-reference.md (all commands, flags, options)
3. docs/troubleshooting.md (common issues, solutions)
4. README.md (project overview, quick start, features)

Structure for README:
- Project description
- Key features (bullets)
- Quick start (install, config, first command)
- Example usage
- Documentation links
- Contributing
- License

Start with README.md outline. I'll provide content for sections.
```

---

### Day 28: Release Preparation

📋 **PHASE:** Launch
🎯 **GOAL:** Build releases & publish
📝 **PROMPT:**

```
VENOM - Day 28: Release v0.1.0

Today: Prepare launch

Tasks:
1. Build binaries pentru all platforms (Linux, macOS, Windows)
2. Create GitHub release
3. Write launch announcement
4. Test installation script

Please help me:
1. Update Makefile `build-all` target (cross-compilation)
2. Create scripts/release.sh (automate release process)
3. Write CHANGELOG.md (v0.1.0 features)
4. Draft launch announcement (HackerNews, Reddit style)

Start with release.sh script. Show me the code.
```

---

## 🐛 DEBUGGING PROMPTS

### When Stuck on Bugs

📝 **PROMPT:**
```
I'm stuck on a bug în VENOM.

Component: [e.g., pkg/memory/vector.go]
Issue: [describe the problem]
Expected: [what should happen]
Actual: [what's happening]
Error message: [if any]

Code:
[paste relevant code]

What I tried:
1. [attempt 1]
2. [attempt 2]

Please help me debug this. Suggest possible causes and solutions.
```

---

### When Refactoring

📝 **PROMPT:**
```
I need to refactor [component] în VENOM.

Current implementation:
[paste code]

Issues:
- [issue 1]
- [issue 2]

Goals:
- [goal 1]
- [goal 2]

Please suggest:
1. Better architecture
2. Refactored code
3. Migration strategy (avoid breaking existing features)
```

---

### When Optimizing Performance

📝 **PROMPT:**
```
Performance issue în VENOM:

Component: [e.g., router]
Symptom: [e.g., slow model selection]
Metrics:
- Current latency: [e.g., 500ms]
- Target latency: [e.g., <50ms]

Profiling data:
[paste profiling output if available]

Please suggest:
1. Performance bottlenecks
2. Optimization strategies
3. Code improvements
```

---

## 🔄 ITERATIVE DEVELOPMENT PROMPTS

### Daily Standup Format

📝 **PROMPT:**
```
VENOM Daily Update - Day [X]

Yesterday:
- [completed task 1]
- [completed task 2]

Today's Goals:
- [task 1]
- [task 2]

Blockers:
- [blocker if any]

Current milestone: [e.g., Week 2 - Memory & Intelligence]
Progress: [X]% complete

Ready to start with: [first task]
```

---

### Code Review Request

📝 **PROMPT:**
```
Please review this VENOM code:

File: [path]
Purpose: [what it does]

Code:
[paste code]

Review for:
- Correctness
- Performance
- Go best practices
- Error handling
- Test coverage needs

Suggest improvements.
```

---

### Integration Testing

📝 **PROMPT:**
```
I need integration tests for [component].

Component: [e.g., pkg/agent/]
Dependencies: [e.g., memory, router, skills]

Scenarios to test:
1. [scenario 1]
2. [scenario 2]

Please help me:
1. Setup test fixtures
2. Write integration tests
3. Use testcontainers for dependencies (ChromaDB, Redis)

Show me test code for scenario 1.
```

---

## 📚 LEARNING PROMPTS

### When Learning New Concept

📝 **PROMPT:**
```
I need to understand [concept] for VENOM.

Context: Implementing [component]
Why needed: [reason]

Please explain:
1. What is [concept]?
2. How does it work?
3. Best practices în Go
4. Example implementation for my use case

Then help me implement it în VENOM.
```

---

### Architecture Decision

📝 **PROMPT:**
```
Architecture decision needed for VENOM:

Component: [e.g., memory system]
Options:
1. [option A] - pros: [...], cons: [...]
2. [option B] - pros: [...], cons: [...]

Constraints:
- [constraint 1]
- [constraint 2]

Which option do you recommend and why?
After deciding, help me implement it.
```

---

## 🎯 END-TO-END WORKFLOW PROMPT

📝 **ULTIMATE PROMPT (Start of Each Week):**

```
VENOM Supreme - Week [X] Kickoff

Project context:
- AI Terminal Orchestrator în Go
- Solo dev + Claude CLI collaboration
- MVP target: 4 weeks
- Current week: [X]/4

This week's goals (from IMPLEMENTATION_ROADMAP.md):
[paste week goals]

Full blueprint available în:
- BLUEPRINT.md (vision, architecture)
- TECH_STACK.md (technologies)
- PROJECT_STRUCTURE.md (file organization)
- IMPLEMENTATION_ROADMAP.md (daily tasks)

Current status:
- Completed: [previous weeks' work]
- Working: [current component]
- Blocked: [any blockers]

Today (Day [X]):
Goal: [today's goal from roadmap]
Tasks:
1. [task 1]
2. [task 2]

Let's start with task 1. Please guide me step-by-step, showing code, explaining decisions, and waiting for my confirmation before proceeding.

Ready to begin!
```

---

## 💡 PRO TIPS

### Effective Collaboration with Claude CLI

1. **Be Specific:**
   - ✅ "Implement pkg/router/quantum.go using Thompson sampling"
   - ❌ "Help me with routing"

2. **Provide Context:**
   - Always mention which file you're working on
   - Reference blueprint sections
   - Share current state

3. **Iterate:**
   - Review code before implementing
   - Test each component
   - Ask for improvements

4. **Ask for Explanations:**
   - "Why this approach?"
   - "What are the tradeoffs?"
   - "How does this scale?"

---

**COPY-PASTE THESE PROMPTS AS NEEDED! 🚀**

**Pro Tip:** Save your own prompts that work well în a `MY_PROMPTS.md` file.

# SUCCESS CRITERIA - VENOM Supreme MVP
**How We Know When We're Done**

---

## 🎯 MVP DEFINITION

**Core Statement:**
VENOM Supreme MVP is **DONE** when a solo developer can:
1. Install with one command
2. Ask questions in natural language
3. Get accurate, useful responses
4. Track costs & usage
5. Save/restore work (snapshots)
6. Works offline (with local LLMs)

---

## ✅ FEATURE CHECKLIST (Must-Have)

### Phase 0: MVP Core

#### 1. Installation & Setup ⚙️
- [ ] Single binary distribution (Linux, macOS, Windows)
- [ ] One-command install script
- [ ] Automatic config generation
- [ ] API key setup wizard
- [ ] Dependencies check (Docker optional)

**Test:**
```bash
curl -sSL https://venom.dev/install.sh | sh
venom config init
venom ask "hello world"
```

**Success:** Works în <5 minutes from zero to first response.

---

#### 2. Natural Language Interface 🗣️

- [ ] Parse natural language intents
- [ ] Confidence scoring (>0.8 threshold)
- [ ] Clarification prompts (when confidence <0.8)
- [ ] Multi-turn conversations
- [ ] Context awareness

**Test:**
```bash
venom ask "what is 2+2"
→ "The answer is 4."

venom ask "multiply that by 3"
→ "4 multiplied by 3 is 12."

venom ask "refactor the auth module"
→ "I need more information. Which repository?"
```

**Success:** 80%+ intent understanding accuracy on common tasks.

---

#### 3. Multi-Model Support 🤖

- [ ] Anthropic Claude integration
- [ ] Google Gemini integration
- [ ] Ollama local LLMs integration
- [ ] Unified model interface
- [ ] Automatic failover
- [ ] Cost tracking per model

**Test:**
```bash
venom config set models.default claude-opus-4.5
venom ask "complex reasoning task"
→ Uses Claude Opus

venom config set models.default ollama:llama3.1
venom ask "simple task"
→ Uses local Llama (offline)
```

**Success:** All 3 providers work, automatic selection based on config.

---

#### 4. Intelligent Routing 🎯

- [ ] Cost/quality tradeoff
- [ ] Budget tracking (daily limits)
- [ ] Thompson sampling (exploration/exploitation)
- [ ] Model selection explanation
- [ ] Cost estimation before execution

**Test:**
```bash
venom route simulate --task "refactor code" --budget 1.00
→ Estimated: $0.23 using claude-sonnet-4

venom ask "simple math"
→ Using claude-haiku-4 (cost-optimized: $0.0001)
```

**Success:** Intelligent model selection saves >30% cost vs always-opus.

---

#### 5. Core Skills 🛠️

- [ ] **Git:** clone, commit, push, PR creation
- [ ] **Code Execution:** run commands, scripts, tests
- [ ] **Files:** read, write, search, analyze
- [ ] **Browser:** fetch URLs, scrape data (basic)
- [ ] **Embeddings:** generate, search, similarity

**Test:**
```bash
venom do "clone https://github.com/user/repo and run tests"
→ ✓ Cloned repository
→ ✓ Ran pytest: 47 tests passed
→ Snapshot: snap-abc123
```

**Success:** All 5 core skills work reliably.

---

#### 6. Memory System 💾

- [ ] Conversation history persistence
- [ ] Vector memory (semantic search)
- [ ] Context window management (200k tokens)
- [ ] Memory consolidation (background)
- [ ] Query previous conversations

**Test:**
```bash
venom ask "clone https://github.com/user/repo"
→ ✓ Cloned

# Later...
venom memory query "what repository did I clone yesterday?"
→ "You cloned https://github.com/user/repo"
```

**Success:** Recalls context from previous sessions.

---

#### 7. Time Machine ⏱️

- [ ] Automatic snapshots (every major action)
- [ ] Manual snapshot creation
- [ ] Snapshot listing
- [ ] State restoration
- [ ] Diff visualization
- [ ] Snapshot integrity verification

**Test:**
```bash
venom do "refactor code"
→ Snapshot: snap-before-refactor

venom do "run tests"
→ ✗ Tests failed

venom time travel --to snap-before-refactor
→ ✓ Restored to previous state
```

**Success:** Can reliably restore to any previous state.

---

#### 8. Plan Generation & Execution 📋

- [ ] Automatic plan generation from intent
- [ ] Dependency resolution (DAG)
- [ ] Parallel execution (where safe)
- [ ] Step-by-step progress display
- [ ] Error recovery & retry

**Test:**
```bash
venom ask "analyze codebase and suggest refactorings"

→ 📋 Plan:
  1. Clone repository
  2. Analyze structure (parallel)
  3. Find issues (parallel)
  4. Generate suggestions
  5. Create report

→ Executing...
  ✓ Step 1 complete (2s)
  ✓ Steps 2-3 complete (5s, parallel)
  ✓ Step 4 complete (3s)
  ✓ Step 5 complete (1s)

→ Results: ./refactor-report.md
```

**Success:** Multi-step plans execute correctly with parallelization.

---

#### 9. Agent System 🎭

- [ ] Agent configuration (YAML)
- [ ] Agent creation from config
- [ ] Agent execution
- [ ] Agent persistence
- [ ] Multiple agents (basic collaboration)

**Test:**
```yaml
# my-agent.yml
agent:
  name: "Code Reviewer"
  skills: [git, code-analysis]
  model: claude-opus-4.5
```

```bash
venom agent create --file my-agent.yml
venom agent run code-reviewer --input "review PR #123"
→ ✓ Review complete: found 3 issues
```

**Success:** Custom agents work as configured.

---

#### 10. CLI UX ✨

- [ ] Beautiful terminal output (colors, formatting)
- [ ] Progress indicators
- [ ] Interactive prompts
- [ ] Helpful error messages
- [ ] Autocomplete (bash/zsh)
- [ ] Help documentation

**Test:**
```bash
venom --help
→ Clear, comprehensive help

venom ask "invalid nonsense gibberish"
→ ✗ Could not understand request.
  Did you mean:
    - venom ask "what is..."
    - venom do "action..."
```

**Success:** Professional, user-friendly CLI experience.

---

## 📊 QUANTITATIVE METRICS

### Performance Targets (MVP)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Install time** | <5 minutes | Time from curl to first response |
| **Intent accuracy** | >80% | % of correctly understood intents |
| **Response latency (cloud)** | <3s P50, <10s P99 | Time from ask to first response |
| **Response latency (local)** | <1s P50, <5s P99 | Time with Ollama |
| **Memory recall** | >90% | % of correctly retrieved memories |
| **Snapshot restore** | 100% | % of successful restores |
| **Multi-model success** | >95% | % of successful model calls |
| **Cost accuracy** | ±5% | Difference vs actual API bills |
| **Uptime (local)** | 99%+ | % time venom responds |

### Budget Targets

| Item | MVP Target |
|------|------------|
| **Cost per simple task** | <$0.01 |
| **Cost per complex task** | <$1.00 |
| **Daily budget default** | $10.00 |
| **Cost savings vs always-opus** | >30% |

### Code Quality

| Metric | Target |
|--------|--------|
| **Test coverage** | >70% |
| **Go vet** | 0 issues |
| **golangci-lint** | 0 errors |
| **Documentation** | Every public function |

---

## 🧪 ACCEPTANCE TESTS (End-to-End)

### Test 1: New User Journey
```bash
# Fresh install
curl -sSL https://venom.dev/install.sh | sh

# Setup
venom config init
venom config set-key anthropic sk-ant-...

# First question
venom ask "what is the capital of France"
→ ✓ "The capital of France is Paris."

# Follow-up (context)
venom ask "what's the population"
→ ✓ "Paris has a population of approximately 2.1 million."
```

**Success:** New user productive în <10 minutes.

---

### Test 2: Code Workflow
```bash
# Clone and analyze
venom do "clone https://github.com/user/repo and analyze it"
→ ✓ Cloned repository
→ ✓ Analysis complete
→ Findings:
  - 1,234 lines of code
  - 15 functions
  - 3 potential bugs

# Refactor
venom do "fix the bugs and run tests"
→ ✓ Applied 3 fixes
→ ✓ Tests: 23/23 passed
→ Snapshot: snap-after-fixes

# Review changes
venom time diff snap-before snap-after
→ Shows detailed diff
```

**Success:** Complex multi-step workflow completes successfully.

---

### Test 3: Offline Mode
```bash
# Disconnect network
sudo ifconfig en0 down

# Local model
venom config set models.default ollama:llama3.1

# Query (offline)
venom ask "explain recursion"
→ ✓ [Using local model]
→ ✓ Detailed explanation provided

# Restore network
sudo ifconfig en0 up
```

**Success:** Works completely offline with local LLMs.

---

### Test 4: Cost Control
```bash
# Set budget
venom config set models.budget_daily_usd 5.00

# Use expensive model
venom config set models.default claude-opus-4.5

# Multiple queries
for i in {1..100}; do
  venom ask "random question $i"
done

# Check budget
venom route cost --today
→ Used: $4.87 / $5.00
→ ⚠️  Approaching daily limit

# Next query
venom ask "one more question"
→ ⚠️  Daily budget exceeded
→ Switching to claude-haiku-4 (fallback)
```

**Success:** Budget enforcement works, automatic failover to cheaper models.

---

### Test 5: Multi-Agent Collaboration
```bash
# Create agents
venom agent create --file agents/analyzer.yml
venom agent create --file agents/fixer.yml
venom agent create --file agents/tester.yml

# Collaborative task
venom swarm create \
  --agents analyzer,fixer,tester \
  --task "find and fix all bugs"

→ 🐝 Swarm executing:
  ├─ analyzer: Found 5 bugs
  ├─ fixer: Fixed 5 bugs
  └─ tester: All tests passing

→ ✓ Collaborative task complete
```

**Success:** Multiple agents coordinate to complete task.

---

## 🚫 NON-GOALS (MVP)

**Out of Scope pentru MVP:**
- ❌ Web UI
- ❌ Federated learning
- ❌ Swarm intelligence (advanced)
- ❌ Zero-knowledge execution
- ❌ Neuromorphic execution
- ❌ Marketplace
- ❌ IDE extensions
- ❌ Mobile apps
- ❌ Multi-user/teams
- ❌ Enterprise SSO
- ❌ Cloud-hosted SaaS

**Reason:** Focus on core functionality first. These come în Phase 1-3.

---

## 📈 LAUNCH READINESS CHECKLIST

### Pre-Launch (Week 4)

- [ ] All MVP features implemented & tested
- [ ] End-to-end tests passing
- [ ] Performance benchmarks meet targets
- [ ] Documentation complete
  - [ ] README.md
  - [ ] User guide
  - [ ] API reference
  - [ ] Troubleshooting guide
- [ ] Example agents & workflows
- [ ] Video demo recorded
- [ ] Binaries built for all platforms
  - [ ] Linux (amd64, arm64)
  - [ ] macOS (amd64, arm64)
  - [ ] Windows (amd64)
- [ ] GitHub repository ready
  - [ ] Description
  - [ ] Topics/tags
  - [ ] Issue templates
  - [ ] PR template
  - [ ] Contributing guide
  - [ ] Code of conduct
- [ ] Website (simple landing page)
- [ ] Social media assets
  - [ ] Twitter/X announcement
  - [ ] HackerNews post
  - [ ] Reddit r/programming post

### Launch Day

- [ ] Create GitHub release (v0.1.0)
- [ ] Publish binaries
- [ ] Publish to package managers
  - [ ] Homebrew (macOS)
  - [ ] apt (Ubuntu/Debian)
  - [ ] Chocolatey (Windows)
- [ ] Post announcements
  - [ ] HackerNews
  - [ ] Reddit
  - [ ] Twitter/X
  - [ ] Dev.to
- [ ] Monitor feedback
- [ ] Respond to issues quickly

### First Week

- [ ] Gather user feedback
- [ ] Fix critical bugs
- [ ] Update documentation based on questions
- [ ] Plan v0.2.0 features

---

## 🎯 SUCCESS DEFINITION

**MVP is SUCCESS if within 30 days:**

### Adoption Metrics
- ✅ **100+ GitHub stars**
- ✅ **500+ downloads**
- ✅ **10+ community contributions** (issues, PRs)
- ✅ **5+ external agents** created by users

### Quality Metrics
- ✅ **<5 critical bugs** reported
- ✅ **>4.0/5.0 user satisfaction** (survey)
- ✅ **>80% task success rate** (telemetry)

### Technical Metrics
- ✅ **All acceptance tests passing**
- ✅ **Performance targets met**
- ✅ **Zero security vulnerabilities** (high/critical)

---

## 🔄 ITERATION PLAN

### If MVP succeeds → Phase 1 (Months 2-3)
- Marketplace (plugin ecosystem)
- IDE extensions (VSCode, JetBrains)
- Advanced multi-agent (swarm)
- Web UI (optional)
- Meta-learning (skill synthesis)

### If MVP struggles → Pivot
- Gather detailed user feedback
- Identify biggest pain points
- Double down on core value
- Simplify complex features
- Improve onboarding

---

## 📊 DASHBOARD (Track Progress)

```bash
# Create GitHub project board with columns:

┌─────────────────────────────────────────────────────┐
│                                                     │
│  TODO  │  IN PROGRESS  │  REVIEW  │  DONE  │  BLOCKED │
│                                                     │
│  [ ]   │     [1]       │   [2]    │  [✓]  │    [!]   │
│  [ ]   │     [1]       │   [2]    │  [✓]  │          │
│  [ ]   │               │          │  [✓]  │          │
│                                                     │
└─────────────────────────────────────────────────────┘

Progress: 47% (23/49 tasks complete)
```

**Track:**
- Tasks completed
- Bugs fixed
- Tests passing
- Performance metrics
- User feedback

---

**WHEN ALL ✅ BOXES CHECKED → MVP IS DONE! 🎉**

**Definition of Done:**
> "A solo developer can install VENOM, ask it to complete a complex coding task in natural language, and get useful results within minutes — offline or online — while staying under budget."

**That's the MVP. Everything else is Phase 1+.** 🚀

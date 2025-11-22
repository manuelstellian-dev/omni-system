# ARCHITECTURE - VENOM Supreme
**Detailed System Architecture**

---

## 🏗️ SYSTEM OVERVIEW

```
┌────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │   CLI    │  │   TUI    │  │   API    │                │
│  │  (Cobra) │  │ (Bubble) │  │  (HTTP)  │                │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                │
└───────┼────────────┼──────────────┼────────────────────────┘
        │            │              │
┌───────▼────────────▼──────────────▼────────────────────────┐
│              VENOM CORE ENGINE                             │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Intent Engine (NLU Layer)                 │    │
│  │  - Natural language parsing                       │    │
│  │  - Goal decomposition                             │    │
│  │  - Confidence scoring                             │    │
│  └────────────────────┬─────────────────────────────┘    │
│                       │                                    │
│  ┌────────────────────▼─────────────────────────────┐    │
│  │         Planner (Strategy Layer)                  │    │
│  │  - Plan generation                                │    │
│  │  - Dependency resolution (DAG)                    │    │
│  │  - Parallel optimization                          │    │
│  └────────────────────┬─────────────────────────────┘    │
│                       │                                    │
│  ┌────────────────────▼─────────────────────────────┐    │
│  │       Quantum Router (Model Selection)            │    │
│  │  - Multi-objective optimization                   │    │
│  │  - Thompson sampling                              │    │
│  │  - Budget tracking                                │    │
│  └────────────────────┬─────────────────────────────┘    │
│                       │                                    │
│  ┌────────────────────▼─────────────────────────────┐    │
│  │      Agent Orchestrator (Execution Layer)         │    │
│  │  - Agent lifecycle management                     │    │
│  │  - Multi-agent coordination                       │    │
│  │  - Task delegation                                │    │
│  └────────────────────┬─────────────────────────────┘    │
└────────────────────────┼──────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
│   Memory     │  │  Executor  │  │    Time    │
│   Cortex     │  │  Substrate │  │   Machine  │
│              │  │            │  │            │
│ ┌──────────┐ │  │ ┌────────┐ │  │ ┌────────┐ │
│ │ Working  │ │  │ │ Docker │ │  │ │Snapshot│ │
│ │  Memory  │ │  │ │Container│ │  │ │ Store  │ │
│ └──────────┘ │  │ └────────┘ │  │ └────────┘ │
│              │  │            │  │            │
│ ┌──────────┐ │  │ ┌────────┐ │  │ ┌────────┐ │
│ │ Episodic │ │  │ │ Process│ │  │ │  Diff  │ │
│ │  Memory  │ │  │ │  Exec  │ │  │ │ Engine │ │
│ │ (Vector) │ │  │ └────────┘ │  │ └────────┘ │
│ └──────────┘ │  │            │  │            │
│              │  │ ┌────────┐ │  │ ┌────────┐ │
│ ┌──────────┐ │  │ │Security│ │  │ │ Replay │ │
│ │ Semantic │ │  │ │Sandbox │ │  │ │ Engine │ │
│ │  Memory  │ │  │ └────────┘ │  │ └────────┘ │
│ │  (Graph) │ │  └────────────┘  └────────────┘
│ └──────────┘ │
│              │
│ ┌──────────┐ │
│ │Procedural│ │
│ │  Memory  │ │
│ │  (Cache) │ │
│ └──────────┘ │
└──────────────┘
        │
┌───────▼────────────────────────────────────────┐
│           SKILLS FRAMEWORK                      │
│                                                 │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │
│  │  Git   │ │  Code  │ │  Files │ │Browser │ │
│  │        │ │  Exec  │ │        │ │        │ │
│  └────────┘ └────────┘ └────────┘ └────────┘ │
│                                                 │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │
│  │Embeddi │ │  HTTP  │ │  Cloud │ │ Custom │ │
│  │  ngs   │ │  API   │ │  Ops   │ │ Skills │ │
│  └────────┘ └────────┘ └────────┘ └────────┘ │
└─────────────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────────────┐
│           MODEL PROVIDERS                       │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │  Anthropic   │  │    Google    │           │
│  │    Claude    │  │    Gemini    │           │
│  │              │  │              │           │
│  │ - Opus 4.5   │  │ - Ultra 2.0  │           │
│  │ - Sonnet 4   │  │ - Pro 2.0    │           │
│  │ - Haiku 4    │  │ - Flash 2.0  │           │
│  └──────────────┘  └──────────────┘           │
│                                                 │
│  ┌──────────────┐                              │
│  │    Ollama    │                              │
│  │  (Local LLM) │                              │
│  │              │                              │
│  │ - Llama 3.1  │                              │
│  │ - Mistral    │                              │
│  │ - CodeLlama  │                              │
│  └──────────────┘                              │
└─────────────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────────────┐
│           STORAGE LAYER                         │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ChromaDB  │  │  Redis   │  │  SQLite  │     │
│  │ Vectors  │  │  Cache   │  │   Meta   │     │
│  └──────────┘  └──────────┘  └──────────┘     │
│                                                 │
│  ┌──────────┐  ┌──────────┐                   │
│  │  Neo4j   │  │   File   │                   │
│  │  Graph   │  │  System  │                   │
│  └──────────┘  └──────────┘                   │
└─────────────────────────────────────────────────┘
```

---

## 📦 COMPONENT DETAILS

### 1. INTENT ENGINE

**Responsibility:** Transform natural language → structured plans

**Components:**
```
IntentEngine
├── NLUParser          # Natural language understanding
├── ConfidenceScorer   # Estimate understanding confidence
├── Disambiguator      # Resolve ambiguities via dialogue
└── GoalDecomposer     # Break complex goals into subgoals
```

**Data Flow:**
```
User Input
    ↓
NLUParser → Parse intent + extract parameters
    ↓
ConfidenceScorer → Score understanding (0-1)
    ↓
if confidence < 0.8:
    Disambiguator → Ask clarifying questions
    ↓
    Updated Input → Re-parse
    ↓
GoalDecomposer → Decompose into subgoals
    ↓
Structured Intent (JSON)
```

**Example:**
```json
{
  "intent": "deploy_application",
  "confidence": 0.92,
  "goals": [
    {"action": "run_tests", "priority": 1},
    {"action": "build_artifact", "priority": 2},
    {"action": "deploy_to_env", "params": {"env": "staging"}, "priority": 3}
  ]
}
```

---

### 2. PLANNER

**Responsibility:** Generate executable plans cu dependencies

**Components:**
```
Planner
├── PlanGenerator      # Create plans from intents
├── DAGBuilder         # Build dependency graph
├── Optimizer          # Optimize pentru parallelism
└── Validator          # Validate plan feasibility
```

**Algorithm:**
```
1. Generate candidate plans (LLM-based)
2. Build dependency graph (DAG)
3. Topological sort pentru ordering
4. Identify parallel opportunities
5. Validate resource requirements
6. Return optimized plan
```

**Plan Structure:**
```go
type Plan struct {
    ID       string
    Goal     string
    Steps    []Step
    DAG      *DependencyGraph
    Estimated struct {
        Duration time.Duration
        Cost     float64
    }
}

type Step struct {
    ID         string
    Skill      string
    Action     string
    Params     map[string]interface{}
    DependsOn  []string  // Step IDs
    Parallel   bool      // Can run în parallel?
}
```

---

### 3. QUANTUM ROUTER

**Responsibility:** Optimal model selection

**Algorithm: Thompson Sampling + Pareto Optimization**

```go
func SelectModel(task Task, constraints Constraints) Model {
    // 1. Filter candidates by constraints
    candidates := FilterCandidates(allModels, constraints)

    // 2. Compute Pareto frontier
    //    (multi-objective: cost, quality, latency, privacy)
    pareto := ComputeParetoFrontier(candidates)

    // 3. Thompson sampling (exploration/exploitation)
    selected := ThompsonSample(pareto, history)

    // 4. Update statistics
    UpdateHistory(selected, task)

    return selected
}
```

**Pareto Frontier:**
```
Quality
  ^
  │     ●Claude Opus (high quality, high cost)
  │
  │   ●Gemini Pro (balanced)
  │
  │ ●Claude Haiku (fast, cheap)
  │●Local Llama (privacy, low cost)
  └──────────────────────────> Cost
```

**Statistics Tracking:**
```go
type ModelStats struct {
    Model        string
    Calls        int
    Successes    int
    Failures     int
    AvgLatency   float64
    AvgCost      float64
    AvgQuality   float64  // User feedback-based
}
```

---

### 4. AGENT ORCHESTRATOR

**Responsibility:** Manage agent lifecycle & coordination

**Components:**
```
AgentOrchestrator
├── AgentRegistry      # Track active agents
├── Scheduler          # Schedule tasks
├── Coordinator        # Multi-agent coordination
└── LifecycleManager   # Start/stop/pause agents
```

**Agent States:**
```
   ┌─────────┐
   │ Created │
   └────┬────┘
        │ start()
   ┌────▼────┐
   │  Ready  │◄──┐
   └────┬────┘   │
        │ execute()  │ resume()
   ┌────▼────┐   │
   │ Running │   │
   └────┬────┘   │
        │        │
        ├───────►┤
        │ pause()│
   ┌────▼────┐   │
   │ Paused  │───┘
   └────┬────┘
        │ stop()
   ┌────▼────┐
   │ Stopped │
   └─────────┘
```

**Multi-Agent Coordination:**
```go
type Coordinator struct {
    agents map[string]*Agent
}

// Swarm execution
func (c *Coordinator) ExecuteSwarm(task Task) {
    // 1. Decompose task
    subtasks := DecomposeTask(task)

    // 2. Auction protocol (agents bid)
    assignments := c.AuctionTasks(subtasks)

    // 3. Execute în parallel
    results := c.ParallelExecute(assignments)

    // 4. Aggregate results
    return c.AggregateResults(results)
}
```

---

### 5. MEMORY CORTEX

**Hierarchical Memory System**

```
┌─────────────────────────────────────────────┐
│         WORKING MEMORY (Hot)                 │
│  - Current conversation                      │
│  - Active context (200k tokens)              │
│  - Fast access (<1ms)                        │
│  - Eviction: LRU + importance-weighted       │
└──────────────────┬──────────────────────────┘
                   │ Consolidation (async)
┌──────────────────▼──────────────────────────┐
│       EPISODIC MEMORY (Warm)                 │
│  - Conversation history                      │
│  - Vector embeddings (ChromaDB)              │
│  - Similarity search + rerank                │
│  - Access: ~20ms                             │
└──────────────────┬──────────────────────────┘
                   │ Knowledge extraction
┌──────────────────▼──────────────────────────┐
│        SEMANTIC MEMORY (Cold)                │
│  - Knowledge graph (Neo4j)                   │
│  - Entities, relations, facts                │
│  - Inference engine (Datalog)                │
│  - Access: ~50ms                             │
└──────────────────┬──────────────────────────┘
                   │ Skill compilation
┌──────────────────▼──────────────────────────┐
│       PROCEDURAL MEMORY (Instant)            │
│  - Compiled skills                           │
│  - Cached plans                              │
│  - Fast retrieval (Redis, <1ms)              │
│  - JIT optimization                          │
└─────────────────────────────────────────────┘
```

**Memory Consolidation Process:**
```go
func (mc *MemoryCortex) Consolidate() {
    // Run nightly (or configurable interval)

    // 1. Select important conversations
    important := mc.SelectImportant(threshold=0.7)

    // 2. Generate embeddings
    embeddings := mc.GenerateEmbeddings(important)

    // 3. Store în vector DB
    mc.VectorStore.Add(embeddings)

    // 4. Extract knowledge (entities, facts)
    knowledge := mc.ExtractKnowledge(important)

    // 5. Update knowledge graph
    mc.KnowledgeGraph.Update(knowledge)

    // 6. Evict old working memory
    mc.WorkingMemory.EvictOld()
}
```

---

### 6. EXECUTOR SUBSTRATE

**Layered Execution Model**

```
┌─────────────────────────────────────────┐
│        EXECUTION CONTROLLER              │
│  - Resource allocation                   │
│  - Timeout management                    │
│  - Cancellation handling                 │
└──────────────┬──────────────────────────┘
               │
      ┌────────┼────────┐
      │        │        │
┌─────▼───┐ ┌─▼────┐ ┌─▼────────┐
│ Docker  │ │Process│ │ Cloud    │
│Container│ │ Exec  │ │ Function │
│         │ │       │ │          │
│Isolated │ │Quick  │ │Scalable  │
│Secure   │ │Simple │ │Serverless│
└─────────┘ └───────┘ └──────────┘
```

**Execution Modes:**

1. **Containerized (Default):**
```go
type DockerExecutor struct {
    client *docker.Client
}

func (de *DockerExecutor) Execute(ctx context.Context, cmd Command) (*Result, error) {
    // Create container
    container := de.client.ContainerCreate(ctx, &container.Config{
        Image: "venom/sandbox:latest",
        Cmd:   cmd.Args,
        Env:   cmd.Env,
    })

    // Set resource limits
    de.client.ContainerUpdate(ctx, container.ID, &container.UpdateConfig{
        Resources: container.Resources{
            Memory:   512 * 1024 * 1024,  // 512MB
            CPUQuota: 50000,               // 50% CPU
        },
    })

    // Start
    de.client.ContainerStart(ctx, container.ID)

    // Wait + collect output
    output := de.client.ContainerLogs(ctx, container.ID)

    // Cleanup
    de.client.ContainerRemove(ctx, container.ID)

    return &Result{Output: output}, nil
}
```

2. **Process Execution (Fast Path):**
```go
type ProcessExecutor struct{}

func (pe *ProcessExecutor) Execute(ctx context.Context, cmd Command) (*Result, error) {
    c := exec.CommandContext(ctx, cmd.Binary, cmd.Args...)
    output, err := c.CombinedOutput()
    return &Result{Output: string(output)}, err
}
```

**Security Sandbox:**
```
┌───────────────────────────────┐
│      Execution Sandbox         │
│                                │
│  ┌──────────────────────────┐ │
│  │   Capabilities Drop      │ │
│  │   - CAP_SYS_ADMIN ✗      │ │
│  │   - CAP_NET_RAW ✗        │ │
│  └──────────────────────────┘ │
│                                │
│  ┌──────────────────────────┐ │
│  │   Filesystem Isolation   │ │
│  │   - Read-only rootfs     │ │
│  │   - tmpfs pentru /tmp    │ │
│  └──────────────────────────┘ │
│                                │
│  ┌──────────────────────────┐ │
│  │   Network Isolation      │ │
│  │   - No internet (default)│ │
│  │   - Allowlist-based      │ │
│  └──────────────────────────┘ │
└───────────────────────────────┘
```

---

### 7. TIME MACHINE

**Event-Sourced Architecture**

```
┌─────────────────────────────────────────┐
│         EVENT LOG (Append-Only)          │
│                                          │
│  Event 1: AgentCreated                   │
│  Event 2: IntentParsed                   │
│  Event 3: PlanGenerated                  │
│  Event 4: StepExecuted (skill=git)       │
│  Event 5: StepExecuted (skill=code-exec) │
│  Event 6: SnapshotCreated                │
│  ...                                     │
└──────────────┬───────────────────────────┘
               │
      ┌────────┼────────┐
      │        │        │
┌─────▼───┐ ┌─▼────┐ ┌─▼────────┐
│Snapshot │ │ Diff │ │  Replay  │
│ Store   │ │Engine│ │  Engine  │
└─────────┘ └──────┘ └──────────┘
```

**Snapshot Creation:**
```go
type Snapshot struct {
    ID        string
    Timestamp time.Time
    AgentID   string

    // Full state
    State     AgentState

    // Incremental (from previous snapshot)
    Delta     *StateDelta

    // Integrity
    Checksum  string
    Signature string  // Optional cryptographic signature
}

func CreateSnapshot(agent *Agent) *Snapshot {
    state := CaptureState(agent)
    delta := ComputeDelta(lastSnapshot, state)

    snap := &Snapshot{
        ID:        generateID(),
        Timestamp: time.Now(),
        State:     state,
        Delta:     delta,
        Checksum:  SHA256(state),
    }

    return snap
}
```

**Deterministic Replay:**
```go
func Replay(snapshotID string) (*Agent, error) {
    // 1. Load snapshot
    snap := LoadSnapshot(snapshotID)

    // 2. Restore agent state
    agent := RestoreAgent(snap.State)

    // 3. Replay events (if needed)
    events := LoadEventsSince(snap.Timestamp)
    for _, event := range events {
        ApplyEvent(agent, event)
    }

    // 4. Verify determinism
    if !VerifyState(agent, snap) {
        return nil, errors.New("non-deterministic replay")
    }

    return agent, nil
}
```

---

## 🔄 DATA FLOW (End-to-End)

**Example: "Refactor the auth module"**

```
1. USER INPUT
   ↓
   "Refactor the auth module and make it more secure"

2. INTENT ENGINE
   ↓
   Intent {
     action: "refactor",
     target: "auth module",
     constraint: "security",
     confidence: 0.89
   }

3. PLANNER
   ↓
   Plan {
     steps: [
       {skill: "git", action: "analyze-module"},
       {skill: "code-analysis", action: "find-vulnerabilities"},
       {skill: "refactor", action: "apply-fixes"},
       {skill: "test", action: "run-tests"}
     ]
   }

4. QUANTUM ROUTER
   ↓
   Model Selection {
     step1: gemini-flash (fast analysis),
     step2: claude-opus (security expertise),
     step3: claude-sonnet (code generation),
     step4: local-llama (simple test run)
   }

5. AGENT ORCHESTRATOR
   ↓
   Execution {
     agent1: analyze (parallel),
     agent2: find-vulns (parallel),
     agent3: refactor (sequential after 1,2),
     agent4: test (sequential after 3)
   }

6. EXECUTOR
   ↓
   Results {
     vulnerabilities: [SQL-injection, XSS],
     fixes_applied: 12,
     tests_passing: true,
     snapshot: snap-xyz
   }

7. MEMORY
   ↓
   Store {
     conversation: "refactor auth module",
     knowledge: ["auth best practices", "SQL injection fix"],
     skills: ["refactor-with-security-check"]  // learned composite
   }

8. RESPONSE TO USER
   ↓
   "✓ Refactored auth module
    - Fixed 2 SQL injection vulns
    - Fixed 1 XSS vulnerability
    - All 47 tests passing
    - Code coverage: 89% → 94%
    💾 Snapshot: snap-xyz
    💰 Cost: $0.23"
```

---

## 🔐 SECURITY ARCHITECTURE

### Defense-in-Depth Layers

```
Layer 1: INPUT VALIDATION
├── Sanitize user input
├── Validate intent parameters
└── Rate limiting

Layer 2: AUTHENTICATION & AUTHORIZATION
├── API key management (keyring)
├── Per-agent permissions
└── Approval workflows

Layer 3: EXECUTION ISOLATION
├── Sandboxed execution (Docker/gVisor)
├── Resource limits (CPU, memory, network)
└── Filesystem restrictions

Layer 4: DATA PROTECTION
├── Encryption at rest (AES-256-GCM)
├── Encryption in transit (TLS 1.3)
└── Secret redaction în logs

Layer 5: AUDIT & MONITORING
├── Append-only audit log
├── Anomaly detection
└── Compliance reporting

Layer 6: INCIDENT RESPONSE
├── Auto-kill rogue agents
├── Automatic rollback
└── Alert notifications
```

---

## ⚡ PERFORMANCE OPTIMIZATIONS

### 1. Caching Strategy

```
┌─────────────────────────────────┐
│        Cache Hierarchy           │
│                                  │
│  L1: In-Memory (Go maps)         │
│      - Hot data (<1ms)           │
│                                  │
│  L2: Redis (procedural memory)   │
│      - Warm data (~1-5ms)        │
│                                  │
│  L3: ChromaDB (episodic)         │
│      - Cold data (~20ms)         │
│                                  │
│  L4: Disk (snapshots)            │
│      - Archive (~100ms)          │
└─────────────────────────────────┘
```

### 2. Parallel Execution

```go
// Execute independent steps în parallel
func ExecutePlan(plan *Plan) {
    levels := plan.DAG.TopologicalLevels()

    for _, level := range levels {
        var wg sync.WaitGroup

        for _, step := range level {
            wg.Add(1)
            go func(s Step) {
                defer wg.Done()
                ExecuteStep(s)
            }(step)
        }

        wg.Wait()  // Wait for all parallel steps
    }
}
```

### 3. Lazy Loading

```go
// Load components only when needed
type Agent struct {
    config    *Config
    model     ModelAdapter       // nil until first use
    memory    *MemoryCortex     // nil until first use
    lazyInit  sync.Once
}

func (a *Agent) GetModel() ModelAdapter {
    a.lazyInit.Do(func() {
        a.model = InitModel(a.config)
        a.memory = InitMemory(a.config)
    })
    return a.model
}
```

---

## 📊 MONITORING & OBSERVABILITY

### Metrics Collection

```go
// Prometheus metrics
var (
    requestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "venom_request_duration_seconds",
            Buckets: []float64{.1, .5, 1, 2, 5, 10},
        },
        []string{"model", "skill"},
    )

    requestCost = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "venom_request_cost_usd",
        },
        []string{"model"},
    )

    errorRate = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "venom_errors_total",
        },
        []string{"type"},
    )
)
```

### Structured Logging

```go
log := zerolog.New(os.Stdout).With().
    Str("agent_id", agent.ID).
    Str("session_id", session.ID).
    Logger()

log.Info().
    Str("model", "claude-opus-4.5").
    Int("tokens_in", 1234).
    Int("tokens_out", 567).
    Float64("cost", 0.023).
    Dur("latency", 2*time.Second).
    Msg("model call completed")
```

---

## 🚀 DEPLOYMENT ARCHITECTURE

### Local Development

```
Developer Machine
├── venom CLI binary
├── Docker (ChromaDB, Redis)
├── Config: ~/.venom/config.yaml
└── Data: ~/.venom/data/
    ├── snapshots/
    ├── logs/
    └── cache/
```

### Production (Self-Hosted)

```
Server
├── venom service (systemd)
├── Docker Compose
│   ├── ChromaDB
│   ├── Redis
│   └── Neo4j (optional)
├── Reverse Proxy (Caddy/nginx)
└── Monitoring (Prometheus + Grafana)
```

### Cloud (Hybrid)

```
┌─────────────────────────┐
│    Local Machine        │
│  ├── venom CLI          │
│  └── Local LLMs         │
└───────────┬─────────────┘
            │ HTTPS
┌───────────▼─────────────┐
│    Cloud Service        │
│  ├── API Gateway        │
│  ├── Model Providers    │
│  │   ├── Anthropic API  │
│  │   └── Google AI API  │
│  └── Storage (optional) │
│      ├── S3/GCS         │
│      └── Managed DBs    │
└─────────────────────────┘
```

---

**ARCHITECTURE IS COMPLETE! 🏗️**

This architecture provides:
✅ Scalability (parallel execution, caching)
✅ Reliability (snapshots, error recovery)
✅ Security (sandboxing, encryption)
✅ Performance (lazy loading, hierarchical memory)
✅ Observability (metrics, logging, tracing)
✅ Extensibility (plugin architecture)

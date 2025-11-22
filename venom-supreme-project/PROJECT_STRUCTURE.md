# PROJECT STRUCTURE - VENOM Supreme
**Complete Folder & File Organization**

---

## 📁 DIRECTORY TREE (Complete MVP Structure)

```
venom/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # CI/CD pipeline
│   │   ├── release.yml               # Auto-release on tags
│   │   └── security.yml              # Security scanning
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── cmd/
│   └── venom/
│       ├── main.go                   # Entry point
│       ├── root.go                   # Root command
│       ├── agent.go                  # Agent commands
│       ├── ask.go                    # Natural language interface
│       ├── do.go                     # Action command
│       ├── memory.go                 # Memory commands
│       ├── time.go                   # Time machine commands
│       ├── config.go                 # Config commands
│       ├── route.go                  # Router commands
│       ├── skill.go                  # Skill commands
│       └── version.go                # Version command
│
├── internal/
│   ├── config/
│   │   ├── config.go                 # Config loading
│   │   ├── defaults.go               # Default values
│   │   └── validation.go             # Config validation
│   │
│   ├── logger/
│   │   ├── logger.go                 # Logging setup
│   │   └── fields.go                 # Structured fields
│   │
│   ├── ui/
│   │   ├── styles.go                 # Terminal styling
│   │   ├── prompts.go                # Interactive prompts
│   │   ├── progress.go               # Progress bars
│   │   └── table.go                  # Table rendering
│   │
│   └── version/
│       └── version.go                # Version info
│
├── pkg/
│   ├── intent/
│   │   ├── parser.go                 # Intent parsing
│   │   ├── scorer.go                 # Confidence scoring
│   │   ├── disambiguator.go          # Ambiguity resolution
│   │   └── decomposer.go             # Goal decomposition
│   │
│   ├── planner/
│   │   ├── planner.go                # Plan generation
│   │   ├── dag.go                    # Dependency graph
│   │   ├── optimizer.go              # Plan optimization
│   │   └── validator.go              # Plan validation
│   │
│   ├── router/
│   │   ├── router.go                 # Quantum router
│   │   ├── pareto.go                 # Pareto optimization
│   │   ├── thompson.go               # Thompson sampling
│   │   ├── budget.go                 # Budget tracking
│   │   └── stats.go                  # Statistics
│   │
│   ├── agent/
│   │   ├── agent.go                  # Agent runtime
│   │   ├── orchestrator.go           # Multi-agent orchestration
│   │   ├── lifecycle.go              # Lifecycle management
│   │   ├── coordinator.go            # Coordination protocols
│   │   └── registry.go               # Agent registry
│   │
│   ├── memory/
│   │   ├── memory.go                 # Memory interface
│   │   ├── working.go                # Working memory
│   │   ├── episodic.go               # Episodic memory (vector)
│   │   ├── semantic.go               # Semantic memory (graph)
│   │   ├── procedural.go             # Procedural memory (cache)
│   │   ├── consolidation.go          # Memory consolidation
│   │   └── vector.go                 # Vector store client
│   │
│   ├── executor/
│   │   ├── executor.go               # Execution interface
│   │   ├── docker.go                 # Docker executor
│   │   ├── process.go                # Process executor
│   │   ├── sandbox.go                # Sandboxing
│   │   └── resources.go              # Resource limits
│   │
│   ├── time/
│   │   ├── machine.go                # Time machine
│   │   ├── snapshot.go               # Snapshot creation
│   │   ├── storage.go                # Snapshot storage
│   │   ├── replay.go                 # Deterministic replay
│   │   ├── diff.go                   # Diff computation
│   │   └── checksum.go               # Integrity verification
│   │
│   ├── models/
│   │   ├── interface.go              # Model adapter interface
│   │   ├── anthropic.go              # Anthropic adapter
│   │   ├── google.go                 # Google adapter
│   │   ├── ollama.go                 # Ollama adapter
│   │   ├── factory.go                # Model factory
│   │   ├── tokens.go                 # Token counting
│   │   └── cost.go                   # Cost calculation
│   │
│   ├── skills/
│   │   ├── interface.go              # Skill interface
│   │   ├── registry.go               # Skill registry
│   │   ├── git.go                    # Git skill
│   │   ├── code_exec.go              # Code execution skill
│   │   ├── files.go                  # File operations skill
│   │   ├── browser.go                # Browser skill
│   │   ├── embeddings.go             # Embeddings skill
│   │   ├── http.go                   # HTTP client skill
│   │   └── composite.go              # Composite skills
│   │
│   ├── storage/
│   │   ├── chroma.go                 # ChromaDB client
│   │   ├── redis.go                  # Redis client
│   │   ├── sqlite.go                 # SQLite client
│   │   └── neo4j.go                  # Neo4j client (optional)
│   │
│   ├── security/
│   │   ├── keyring.go                # Secret management
│   │   ├── encryption.go             # Encryption utilities
│   │   ├── permissions.go            # Permission checking
│   │   └── audit.go                  # Audit logging
│   │
│   └── telemetry/
│       ├── metrics.go                # Prometheus metrics
│       ├── tracing.go                # OpenTelemetry tracing
│       └── events.go                 # Event tracking
│
├── api/                              # Optional HTTP API
│   ├── server.go                     # API server
│   ├── routes.go                     # Route definitions
│   ├── handlers/
│   │   ├── agent.go
│   │   ├── memory.go
│   │   └── time.go
│   └── middleware/
│       ├── auth.go
│       └── logging.go
│
├── examples/
│   ├── agents/
│   │   ├── code-reviewer.yml         # Code review agent
│   │   ├── refactorer.yml            # Refactoring agent
│   │   ├── tester.yml                # Testing agent
│   │   ├── security-scanner.yml      # Security scanning agent
│   │   └── doc-generator.yml         # Documentation agent
│   │
│   ├── workflows/
│   │   ├── full-stack-deploy.yml     # Complete deployment workflow
│   │   ├── pr-review.yml             # Pull request review
│   │   └── security-audit.yml        # Security audit workflow
│   │
│   └── skills/
│       └── custom-skill-example.go   # Example custom skill
│
├── scripts/
│   ├── install.sh                    # Installation script
│   ├── setup-dev.sh                  # Development setup
│   ├── build.sh                      # Build script
│   ├── release.sh                    # Release preparation
│   └── docker-compose.yml            # Dev dependencies (ChromaDB, Redis)
│
├── docs/
│   ├── user-guide.md                 # User guide
│   ├── architecture.md               # Architecture docs
│   ├── api-reference.md              # API reference
│   ├── skills-development.md         # Skill development guide
│   ├── deployment.md                 # Deployment guide
│   └── troubleshooting.md            # Troubleshooting
│
├── test/
│   ├── integration/
│   │   ├── agent_test.go
│   │   ├── memory_test.go
│   │   └── time_test.go
│   │
│   ├── e2e/
│   │   ├── full_workflow_test.go
│   │   └── multi_agent_test.go
│   │
│   └── fixtures/
│       ├── agent-configs/
│       └── test-data/
│
├── .venom/                           # User config directory (created at ~/.venom)
│   ├── config.yaml                   # User configuration
│   ├── agents/                       # User-defined agents
│   ├── skills/                       # Custom skills
│   ├── data/
│   │   ├── snapshots/                # Snapshot storage
│   │   ├── logs/                     # Audit logs
│   │   └── cache/                    # Cache directory
│   └── secrets/                      # Secrets (OS keyring)
│
├── .gitignore
├── .golangci.yml                     # Go linter config
├── go.mod
├── go.sum
├── Makefile                          # Build automation
├── Dockerfile                        # Container image
├── LICENSE                           # MIT License
└── README.md                         # Project README
```

---

## 📄 KEY FILES EXPLAINED

### Entry Point: `cmd/venom/main.go`

```go
package main

import (
    "github.com/yourusername/venom/cmd/venom/commands"
    "github.com/yourusername/venom/internal/logger"
)

func main() {
    // Initialize logger
    logger.Init()

    // Execute root command
    commands.Execute()
}
```

### Root Command: `cmd/venom/root.go`

```go
package commands

import (
    "github.com/spf13/cobra"
    "github.com/spf13/viper"
)

var rootCmd = &cobra.Command{
    Use:   "venom",
    Short: "AI Terminal Orchestrator",
    Long:  `VENOM Supreme - The world's first sentient AI terminal orchestrator`,
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        os.Exit(1)
    }
}

func init() {
    cobra.OnInitialize(initConfig)

    // Global flags
    rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default: ~/.venom/config.yaml)")
    rootCmd.PersistentFlags().BoolVar(&verbose, "verbose", false, "verbose output")

    // Add subcommands
    rootCmd.AddCommand(agentCmd)
    rootCmd.AddCommand(askCmd)
    rootCmd.AddCommand(doCmd)
    rootCmd.AddCommand(memoryCmd)
    rootCmd.AddCommand(timeCmd)
    rootCmd.AddCommand(configCmd)
}

func initConfig() {
    if cfgFile != "" {
        viper.SetConfigFile(cfgFile)
    } else {
        home, _ := os.UserHomeDir()
        viper.AddConfigPath(filepath.Join(home, ".venom"))
        viper.SetConfigName("config")
    }

    viper.AutomaticEnv()
    viper.ReadInConfig()
}
```

### Ask Command: `cmd/venom/ask.go`

```go
package commands

import (
    "context"
    "fmt"

    "github.com/spf13/cobra"
    "github.com/yourusername/venom/pkg/agent"
    "github.com/yourusername/venom/pkg/intent"
)

var askCmd = &cobra.Command{
    Use:   "ask [question]",
    Short: "Ask VENOM to do something in natural language",
    Args:  cobra.MinimumNArgs(1),
    RunE:  runAsk,
}

func runAsk(cmd *cobra.Command, args []string) error {
    ctx := context.Background()
    question := strings.Join(args, " ")

    // Load agent
    ag, err := agent.LoadDefault(ctx)
    if err != nil {
        return err
    }

    // Execute
    result, err := ag.Execute(ctx, question)
    if err != nil {
        return err
    }

    // Display result
    fmt.Println(result.Output)
    return nil
}
```

---

## 🔧 MAKEFILE (Build Automation)

```makefile
# Makefile for VENOM Supreme

.PHONY: all build test lint clean install dev

# Variables
BINARY_NAME=venom
VERSION=$(shell git describe --tags --always --dirty)
BUILD_DIR=./dist
GO=go
GOFLAGS=-ldflags "-X main.Version=$(VERSION)"

# Default target
all: test build

# Build binary
build:
	@echo "Building $(BINARY_NAME) $(VERSION)..."
	$(GO) build $(GOFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME) ./cmd/venom

# Build for all platforms
build-all:
	@echo "Building for all platforms..."
	GOOS=linux GOARCH=amd64 $(GO) build $(GOFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-linux-amd64 ./cmd/venom
	GOOS=darwin GOARCH=arm64 $(GO) build $(GOFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-darwin-arm64 ./cmd/venom
	GOOS=darwin GOARCH=amd64 $(GO) build $(GOFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-darwin-amd64 ./cmd/venom
	GOOS=windows GOARCH=amd64 $(GO) build $(GOFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-windows-amd64.exe ./cmd/venom

# Run tests
test:
	@echo "Running tests..."
	$(GO) test -v -race -coverprofile=coverage.out ./...

# Run linter
lint:
	@echo "Running linter..."
	golangci-lint run

# Clean build artifacts
clean:
	@echo "Cleaning..."
	rm -rf $(BUILD_DIR)
	rm -f coverage.out

# Install locally
install: build
	@echo "Installing to ~/bin..."
	mkdir -p ~/bin
	cp $(BUILD_DIR)/$(BINARY_NAME) ~/bin/
	@echo "✓ Installed! Add ~/bin to PATH if not already."

# Development mode (with live reload)
dev:
	@echo "Starting development mode..."
	air

# Setup development environment
setup-dev:
	@echo "Setting up development environment..."
	./scripts/setup-dev.sh

# Run dependencies (ChromaDB, Redis)
deps-up:
	docker-compose -f scripts/docker-compose.yml up -d

# Stop dependencies
deps-down:
	docker-compose -f scripts/docker-compose.yml down

# Release (for maintainers)
release:
	@echo "Creating release..."
	./scripts/release.sh
```

---

## 🐳 DOCKER COMPOSE (Development Dependencies)

```yaml
# scripts/docker-compose.yml
version: '3.8'

services:
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chromadb-data:/chroma/chroma
    environment:
      - ALLOW_RESET=true

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

  neo4j:
    image: neo4j:5
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    volumes:
      - neo4j-data:/data
    environment:
      - NEO4J_AUTH=neo4j/venompass
      - NEO4J_PLUGINS=["apoc"]

volumes:
  chromadb-data:
  redis-data:
  neo4j-data:
```

---

## 📝 CONFIG FILE TEMPLATE

```yaml
# ~/.venom/config.yaml

# Model Configuration
models:
  default: claude-opus-4.5
  budget_daily_usd: 10.00

  providers:
    - name: anthropic
      enabled: true
      models:
        - claude-opus-4.5
        - claude-sonnet-4
        - claude-haiku-4

    - name: google
      enabled: true
      models:
        - gemini-2.0-ultra
        - gemini-2.0-pro
        - gemini-2.0-flash

    - name: ollama
      enabled: true
      url: http://localhost:11434
      models:
        - llama3.1:70b
        - mistral:7b
        - codellama:34b

# Memory Configuration
memory:
  retention_days: 365

  working:
    max_tokens: 200000
    eviction_policy: lru-importance

  episodic:
    backend: chromadb
    url: http://localhost:8000
    consolidation_interval_hours: 24

  semantic:
    backend: neo4j
    url: bolt://localhost:7687
    enabled: false  # Optional

  procedural:
    backend: redis
    url: localhost:6379

# Execution Configuration
execution:
  sandbox: docker
  resource_limits:
    memory_mb: 512
    cpu_percent: 50
    timeout_seconds: 300

# Security Configuration
security:
  audit_logs: true
  audit_path: ~/.venom/data/logs/audit.log
  redact_patterns:
    - "password"
    - "api_key"
    - "secret"

# Logging Configuration
logging:
  level: info  # debug, info, warn, error
  format: json
  output: ~/.venom/data/logs/venom.log
```

---

## 🚀 SETUP SCRIPT

```bash
#!/bin/bash
# scripts/setup-dev.sh

set -e

echo "🚀 Setting up VENOM Supreme development environment..."

# Check Go version
echo "Checking Go version..."
go version

# Install tools
echo "Installing development tools..."
go install github.com/spf13/cobra-cli@latest
go install github.com/cosmtrek/air@latest
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Install dependencies
echo "Installing Go dependencies..."
go mod download

# Create config directory
echo "Creating config directory..."
mkdir -p ~/.venom/data/{snapshots,logs,cache}
mkdir -p ~/.venom/agents
mkdir -p ~/.venom/skills

# Copy default config
echo "Creating default config..."
cp examples/config/default.yaml ~/.venom/config.yaml

# Start dependencies
echo "Starting Docker dependencies..."
docker-compose -f scripts/docker-compose.yml up -d

# Wait for services
echo "Waiting for services to start..."
sleep 5

# Test connections
echo "Testing ChromaDB connection..."
curl -s http://localhost:8000/api/v1/heartbeat || echo "ChromaDB not ready"

echo "Testing Redis connection..."
redis-cli ping || echo "Redis not ready"

echo "✅ Development environment ready!"
echo ""
echo "Next steps:"
echo "  1. Set API keys:"
echo "     export VENOM_API_KEY_ANTHROPIC=sk-..."
echo "     export VENOM_API_KEY_GOOGLE=..."
echo "  2. Build: make build"
echo "  3. Run: ./dist/venom --help"
echo "  4. Dev mode: make dev"
```

---

## 📊 FILE SIZE ESTIMATES (MVP)

```
Total Lines of Code: ~15,000-20,000 LOC

Breakdown:
├── cmd/               ~1,000 LOC
├── internal/          ~2,000 LOC
├── pkg/
│   ├── intent/        ~800 LOC
│   ├── planner/       ~1,200 LOC
│   ├── router/        ~1,000 LOC
│   ├── agent/         ~2,000 LOC
│   ├── memory/        ~2,500 LOC
│   ├── executor/      ~1,500 LOC
│   ├── time/          ~1,200 LOC
│   ├── models/        ~2,000 LOC
│   ├── skills/        ~3,000 LOC
│   └── storage/       ~1,500 LOC
├── test/              ~2,000 LOC
└── examples/          ~500 LOC
```

---

**PROJECT STRUCTURE IS COMPLETE! 📁**

This structure provides:
✅ Clear separation of concerns
✅ Scalable organization
✅ Easy navigation
✅ Testability
✅ Documentation co-location

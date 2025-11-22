# EXAMPLES - VENOM Supreme
**Real-World Use Cases & Agent Configurations**

---

## 🎯 QUICK START EXAMPLES

### Example 1: Simple Question
```bash
$ venom ask "what is the factorial of 5"

🤖 Using claude-haiku-4 (fast, cost-optimized)
💬 The factorial of 5 is 120.
   Calculation: 5! = 5 × 4 × 3 × 2 × 1 = 120

📊 Cost: $0.0001 | Tokens: 12 in, 18 out | Latency: 0.3s
```

### Example 2: Multi-Turn Conversation
```bash
$ venom ask "what's the capital of France"
💬 The capital of France is Paris.

$ venom ask "what's its population"
💬 Paris has a population of approximately 2.1 million people
   in the city proper, and about 12 million in the metropolitan area.

🧠 Retrieved context from previous message
```

### Example 3: Code Execution
```bash
$ venom do "create a Python script that prints fibonacci numbers up to 100"

✓ Created: fibonacci.py
✓ Executed: python fibonacci.py

Output:
1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89

💾 Snapshot: snap-fib-123
📊 Cost: $0.015 | Model: claude-sonnet-4
```

---

## 🤖 AGENT CONFIGURATIONS

### Agent 1: Code Reviewer

```yaml
# agents/code-reviewer.yml
agent:
  id: code-reviewer.v1
  name: "Code Reviewer"
  description: "Reviews code changes and provides feedback"

  model_policy:
    primary: claude-opus-4.5  # Best for code understanding
    fallback:
      - claude-sonnet-4
    routing:
      algorithm: quality-first

  memory:
    working:
      capacity_tokens: 200000  # Large context for codebases
    episodic:
      backend: chromadb
      retention_days: 90  # Keep recent reviews

  skills:
    - git
    - code-analysis
    - test-runner
    - security-scanner

  workflow:
    steps:
      - name: "Fetch Changes"
        skill: git
        action: diff
        params:
          compare: main...feature-branch

      - name: "Analyze Code Quality"
        skill: code-analysis
        action: analyze
        parallel: true

      - name: "Security Scan"
        skill: security-scanner
        action: scan
        parallel: true

      - name: "Run Tests"
        skill: test-runner
        action: run-all

      - name: "Generate Review"
        skill: llm
        action: generate-review
        params:
          template: "pr-review"
```

**Usage:**
```bash
$ venom agent create --file agents/code-reviewer.yml
$ venom agent run code-reviewer --pr 123

🔍 Reviewing PR #123...

📋 Analysis:
  ✓ Code quality: Good
  ⚠️  Found 2 potential issues:
    1. Missing error handling in auth.go:45
    2. Inefficient query in db.go:123
  ✓ Security: No vulnerabilities
  ✓ Tests: 47/47 passing
  ✓ Coverage: 89% (+3%)

💬 Review comment posted to PR #123
📊 Cost: $0.34 | Time: 12s
```

---

### Agent 2: Refactorer

```yaml
# agents/refactorer.yml
agent:
  id: refactorer.v1
  name: "Code Refactorer"
  description: "Refactors code while maintaining tests"

  model_policy:
    primary: claude-sonnet-4
    budget_per_task_usd: 0.50

  memory:
    working:
      capacity_tokens: 150000
    procedural:
      cache_refactoring_patterns: true

  skills:
    - git
    - code-exec
    - test-runner
    - code-refactor

  safety:
    require_approval: true  # Ask before applying changes
    auto_snapshot: true     # Snapshot before changes

  workflow:
    steps:
      - name: "Analyze Codebase"
        skill: code-analysis
        action: find-smells

      - name: "Generate Refactoring Plan"
        skill: llm
        action: plan
        params:
          constraints:
            - maintain_tests
            - no_breaking_changes

      - name: "User Approval"
        skill: approval
        action: request
        params:
          show_diff: true

      - name: "Apply Refactorings"
        skill: code-refactor
        action: apply
        conditions:
          - user_approved

      - name: "Run Tests"
        skill: test-runner
        action: run-all

      - name: "Rollback if Tests Fail"
        skill: time-machine
        action: restore
        conditions:
          - tests_failed
```

**Usage:**
```bash
$ venom agent run refactorer --target ./src/auth

🔍 Analyzing ./src/auth...
📊 Found 8 refactoring opportunities:
  1. Extract method: validatePassword (15 lines → 3 lines)
  2. Remove duplication: hashPassword used 3 times
  3. Simplify conditional: login logic
  ...

📋 Refactoring Plan:
  - Estimated time: 5 minutes
  - Estimated cost: $0.23
  - Risk level: Low (all changes tested)

❓ Apply refactorings? [y/N]: y

✓ Applied 8 refactorings
✓ Tests: 47/47 passing
✓ Coverage: 87% → 91%
💾 Snapshot: snap-before-refactor-xyz

📊 Summary:
  - Lines changed: 234
  - Complexity reduced: 15%
  - Cost: $0.21
```

---

### Agent 3: Security Scanner

```yaml
# agents/security-scanner.yml
agent:
  id: security-scanner.v1
  name: "Security Scanner"
  description: "Scans code for security vulnerabilities"

  model_policy:
    primary: claude-opus-4.5  # Best security knowledge
    routing:
      privacy: prefer_local_if_sensitive

  skills:
    - git
    - security-scanner
    - code-analysis
    - dependency-checker

  workflow:
    steps:
      - name: "Static Analysis"
        skill: security-scanner
        action: sast
        params:
          rules: OWASP-Top-10

      - name: "Dependency Scan"
        skill: dependency-checker
        action: check-vulnerabilities
        parallel: true

      - name: "Secret Detection"
        skill: security-scanner
        action: detect-secrets
        parallel: true

      - name: "Generate Report"
        skill: llm
        action: generate-report
        params:
          format: markdown
          severity_threshold: medium

  alerts:
    critical_vulnerabilities:
      action: notify
      channels:
        - slack
        - email
```

**Usage:**
```bash
$ venom agent run security-scanner --repo ./

🔐 Security Scan Started...

🔍 Static Analysis:
  ⚠️  CRITICAL: SQL Injection in auth.go:123
  ⚠️  HIGH: XSS vulnerability in api.go:45
  ℹ️  MEDIUM: Weak password hashing in user.go:67

🔍 Dependency Scan:
  ⚠️  CRITICAL: lodash@4.17.15 (CVE-2020-8203)
  ⚠️  HIGH: express@4.16.0 (CVE-2022-24999)

🔍 Secret Detection:
  ⚠️  CRITICAL: AWS access key in config.js:12
  ⚠️  HIGH: Database password in .env (committed)

📋 Security Report: ./security-report.md

🚨 Found 3 CRITICAL issues - immediate action required!

📊 Cost: $0.45 | Time: 18s
```

---

### Agent 4: Test Generator

```yaml
# agents/test-generator.yml
agent:
  id: test-generator.v1
  name: "Test Generator"
  description: "Generates comprehensive test suites"

  model_policy:
    primary: claude-sonnet-4
    routing:
      prefer: balanced  # Quality + cost

  skills:
    - code-analysis
    - test-generator
    - test-runner
    - coverage-checker

  workflow:
    steps:
      - name: "Analyze Code"
        skill: code-analysis
        action: find-untested-code

      - name: "Generate Tests"
        skill: test-generator
        action: generate
        params:
          coverage_target: 90
          test_types:
            - unit
            - integration

      - name: "Run Tests"
        skill: test-runner
        action: run-all

      - name: "Check Coverage"
        skill: coverage-checker
        action: check
        params:
          threshold: 90

      - name: "Improve Tests"
        skill: test-generator
        action: improve
        conditions:
          - coverage_below_threshold
```

**Usage:**
```bash
$ venom agent run test-generator --file ./src/auth.js

🧪 Generating tests for ./src/auth.js...

📊 Current Coverage: 67%
🎯 Target Coverage: 90%

✓ Generated 12 new tests:
  - login_with_valid_credentials
  - login_with_invalid_password
  - login_with_missing_fields
  - logout_clears_session
  - password_reset_sends_email
  ...

✓ Running tests...
  ✓ 12/12 passing
  ✓ Coverage: 67% → 93%

📁 Tests saved to: ./tests/auth.test.js

📊 Cost: $0.18 | Time: 8s
```

---

### Agent 5: Documentation Generator

```yaml
# agents/doc-generator.yml
agent:
  id: doc-generator.v1
  name: "Documentation Generator"
  description: "Generates comprehensive documentation"

  model_policy:
    primary: claude-opus-4.5  # Best for writing
    routing:
      optimize_for: quality

  skills:
    - code-analysis
    - doc-generator
    - diagram-generator

  workflow:
    steps:
      - name: "Analyze Codebase"
        skill: code-analysis
        action: extract-structure

      - name: "Generate API Docs"
        skill: doc-generator
        action: api-reference

      - name: "Generate User Guide"
        skill: doc-generator
        action: user-guide
        parallel: true

      - name: "Generate Architecture Diagrams"
        skill: diagram-generator
        action: create
        params:
          types:
            - component-diagram
            - sequence-diagram
        parallel: true

      - name: "Generate README"
        skill: doc-generator
        action: readme
```

**Usage:**
```bash
$ venom agent run doc-generator --repo ./

📚 Generating documentation...

✓ API Reference: ./docs/api-reference.md (2,345 lines)
✓ User Guide: ./docs/user-guide.md (1,234 lines)
✓ Architecture: ./docs/architecture.md (567 lines)
✓ README: ./README.md (234 lines)
✓ Diagrams: ./docs/diagrams/ (3 files)

📊 Documentation coverage: 95%
📊 Cost: $1.23 | Time: 45s
```

---

## 🔄 WORKFLOW EXAMPLES

### Workflow 1: Full Development Cycle

```bash
# 1. Start new feature
$ venom time snapshot --tag before-feature

# 2. Implement feature
$ venom do "add user authentication with JWT"
✓ Implemented authentication
✓ Added JWT middleware
✓ Created tests

# 3. Review code
$ venom agent run code-reviewer --changes HEAD~1
✓ Code quality: Good
⚠️  2 suggestions

# 4. Run security scan
$ venom agent run security-scanner
✓ No vulnerabilities found

# 5. Generate docs
$ venom agent run doc-generator --files auth.go
✓ Documentation generated

# 6. Create PR
$ venom do "create PR for authentication feature"
✓ PR #456 created: https://github.com/user/repo/pull/456
```

---

### Workflow 2: Bug Fix

```bash
# 1. Describe bug
$ venom ask "users can't login, getting 500 error"

🔍 Analyzing issue...
📊 Found potential causes:
  1. Database connection timeout (auth.go:123)
  2. Missing error handling (session.go:45)

💡 Suggested fix:
  - Add timeout handling
  - Add proper error responses

❓ Apply fix? [y/N]: y

✓ Applied fix
✓ Tests added
✓ Tests passing: 48/48

💾 Snapshot: snap-bug-fix-abc

# 2. Verify fix
$ venom do "test the login endpoint"
✓ Login works correctly
✓ Error handling improved
```

---

### Workflow 3: Refactoring Legacy Code

```bash
# 1. Analyze legacy code
$ venom ask "analyze ./legacy/ and suggest improvements"

📊 Analysis of ./legacy/:
  - 5,432 lines
  - Complexity: High
  - Test coverage: 23%
  - Tech debt score: 8.2/10

💡 Suggestions:
  1. Extract 12 god classes
  2. Remove 234 lines of duplicate code
  3. Add missing error handling
  4. Increase test coverage to 80%

# 2. Create refactoring plan
$ venom agent run refactorer --target ./legacy/

📋 Refactoring Plan (4 phases):
  Phase 1: Extract classes (2 hours, $1.20)
  Phase 2: Remove duplication (1 hour, $0.60)
  Phase 3: Add error handling (30 min, $0.30)
  Phase 4: Add tests (3 hours, $1.50)

  Total: 6.5 hours, $3.60

❓ Execute Phase 1? [y/N]: y

# 3. Execute phase by phase
✓ Phase 1 complete
  - Extracted 12 classes
  - Tests: 156/156 passing
  - Coverage: 23% → 45%

💾 Snapshot: snap-phase1-xyz
```

---

### Workflow 4: Multi-Agent Collaboration

```yaml
# workflows/full-stack-deploy.yml
workflow:
  name: "Full Stack Deployment"
  description: "End-to-end deployment with all checks"

  agents:
    - code-reviewer
    - security-scanner
    - test-generator
    - doc-generator

  steps:
    - name: "Code Review"
      agent: code-reviewer
      parallel: false

    - name: "Security & Testing"
      parallel: true
      substeps:
        - agent: security-scanner
        - agent: test-generator

    - name: "Documentation"
      agent: doc-generator
      parallel: false

    - name: "Deploy"
      skill: deploy
      action: staging
      conditions:
        - code_review_passed
        - security_passed
        - tests_passed
```

**Usage:**
```bash
$ venom workflow run full-stack-deploy.yml

🚀 Workflow: Full Stack Deployment

Step 1/4: Code Review
  ✓ Code quality: Excellent
  ✓ No issues found

Step 2/4: Security & Testing (parallel)
  ✓ Security scan: No vulnerabilities
  ✓ Test generation: Coverage 95%

Step 3/4: Documentation
  ✓ Docs generated

Step 4/4: Deploy to staging
  ✓ Deployed: https://staging.example.com

✅ Workflow complete (2m 34s, $2.45)
```

---

## 💡 ADVANCED EXAMPLES

### Example: Custom Skill

```go
// skills/custom-deploy.go
package skills

import (
    "context"
    "os/exec"
)

type DeploySkill struct{}

func (d *DeploySkill) Name() string {
    return "custom-deploy"
}

func (d *DeploySkill) Execute(ctx context.Context, params map[string]interface{}) (*Result, error) {
    env := params["environment"].(string)

    cmd := exec.CommandContext(ctx, "kubectl", "apply", "-f", "deploy-"+env+".yml")
    output, err := cmd.CombinedOutput()

    return &Result{
        Success: err == nil,
        Output:  string(output),
    }, err
}
```

**Register & Use:**
```bash
$ venom skill install ./skills/custom-deploy.go
✓ Installed: custom-deploy

$ venom do "deploy to production using custom-deploy"
✓ Deployment successful
```

---

### Example: Cost Optimization

```bash
# Set aggressive cost optimization
$ venom config set models.routing.algorithm cost-first
$ venom config set models.budget_daily_usd 2.00

# Query với cost awareness
$ venom ask "explain quantum computing"

🤖 Using gemini-2.0-flash (cost-optimized: $0.0002)
💬 [Detailed explanation]

📊 Cost saved vs opus: $0.0148 (98% savings)

# Budget tracking
$ venom route cost --today
📊 Today's usage:
  - Spent: $1.23 / $2.00
  - Queries: 87
  - Avg per query: $0.014
  - Projected daily: $1.67 ✓ within budget
```

---

### Example: Offline Mode

```bash
# Setup local LLM
$ ollama pull llama3.1:70b

# Configure venom
$ venom config set models.default ollama:llama3.1

# Disconnect (airplane mode)
$ sudo ifconfig en0 down

# Use venom offline
$ venom ask "write a quicksort implementation"

🤖 Using ollama:llama3.1 (local, offline)
💬 [Generates code]

✓ No network required
✓ Zero cost
✓ 100% privacy

📊 Latency: 0.8s | Cost: $0.00
```

---

### Example: Snapshot Workflow

```bash
# Before making changes
$ venom time snapshot --tag before-experiment

# Try something risky
$ venom do "completely refactor auth system"
✓ Refactored

# Test
$ venom do "run all tests"
✗ 12/47 tests failed

# Oops, rollback!
$ venom time travel --to before-experiment
✓ Restored to snapshot: before-experiment

# Try different approach
$ venom do "refactor auth system incrementally"
✓ Refactored
✓ Tests: 47/47 passing ✓

# Compare approaches
$ venom time diff before-experiment snap-current
📊 Differences:
  - Files changed: 5 vs 3 (incremental better)
  - Tests passing: 35 vs 47 (incremental better)
```

---

## 📊 REAL-WORLD SCENARIOS

### Scenario 1: Junior Developer Onboarding
```bash
# New dev: "How do I add a feature?"
$ venom ask "how do I add a new API endpoint to this project"

💬 Based on your codebase structure:

1. Create route in routes/api.go
2. Implement handler in handlers/
3. Add tests in tests/handlers/
4. Update API docs

Example code:
[Shows code snippets]

$ venom do "generate boilerplate for /api/users endpoint"
✓ Created: routes/api.go (updated)
✓ Created: handlers/users.go
✓ Created: tests/handlers/users_test.go
```

### Scenario 2: Production Incident
```bash
# 3AM: Production down
$ venom ask "production API returns 500, check logs"

🚨 Analyzing production logs...

💡 Found issue:
  - Database connection pool exhausted
  - 50 hanging connections to PostgreSQL
  - Root cause: Missing timeout in db.go:234

🔧 Suggested fix:
  [Shows code fix]

❓ Apply fix and deploy? [y/N]: y

✓ Fix applied
✓ Tests passing
✓ Deployed to production
✓ Service restored (downtime: 4 minutes)

📊 Incident report: ./incident-2024-11-22.md
```

---

**MORE EXAMPLES:** https://venom.dev/examples

**Community Examples:** https://github.com/venom-examples

**Video Tutorials:** https://youtube.com/@venom-ai

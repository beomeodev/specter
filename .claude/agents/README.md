# SPECTER Agents Guide

This directory contains specialized agents for SPECTER projects. Agents are autonomous assistants that handle complex, multi-step tasks.

## 📋 Agent Categories

### 🏗️ Architecture & Refactoring (3 agents)

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| **code-refactor-master** | Execute comprehensive codebase refactoring | Large-scale restructuring, Constitution violations (>500 SLOC) |
| **refactor-planner** | Create strategic refactoring plans | Planning technical debt reduction, analyzing refactoring scope |
| **integration-designer** | Design integration strategies | Complex feature integrations, architectural decisions |

### 📚 Research & Documentation (3 agents)

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| **library-researcher** | Official API documentation (Context7 MCP) | Learning new library APIs, checking syntax |
| **web-research-specialist** | Community solutions & debugging | Error troubleshooting, technology comparisons |
| **doc-updater** | Sync documentation with code changes | After feature completion, before commits |

### 🐛 Debugging & Quality (3 agents)

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| **debug-helper** | Advanced error diagnosis & fixes | Runtime errors, stack trace analysis |
| **quality-gate** | Pre-commit code quality checks | Before `/fin`, CI/CD validation |
| **tag-auditor** | Validate TAG chains & traceability | Verify SPEC→TEST→CODE integrity |

### 🧪 Testing & Implementation (2 agents)

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| **tdd-implementer** | TDD RED-GREEN-REFACTOR workflow | New feature implementation with tests |
| **trust-validator** | Validate TRUST 5 principles | Code quality audits, pre-merge checks |

### 📝 Specification & Planning (3 agents)

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| **spec-builder** | Create EARS-compliant SPEC documents | Writing requirements from user stories |
| **implementation-planner** | Design implementation strategies | Planning feature architecture |
| **constitution-extractor** | Extract project constraints | Populating Constitution Section IX |

### 🔍 Exploration (1 agent)

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| **codebase-explorer** | Search & understand codebase patterns | Finding similar features, architectural exploration |

---

## 🎯 Common Use Cases

### Use Case 1: Debugging an Error

```bash
# Step 1: Search for community solutions
Task(
    subagent_type="web-research-specialist",
    prompt="Research 'RuntimeError: Event loop is closed' in pytest asyncio"
)

# Step 2: If need official docs
Task(
    subagent_type="library-researcher",
    prompt="Show me pytest-asyncio event loop configuration from official docs"
)

# Step 3: Debug in codebase
Task(
    subagent_type="debug-helper",
    prompt="Analyze stack trace and fix event loop issue in tests/"
)
```

### Use Case 2: Large Refactoring

```bash
# Step 1: Create plan
Task(
    subagent_type="refactor-planner",
    prompt="Analyze auth module and create refactoring plan - 800 lines with circular deps"
)

# Step 2: Execute refactoring
Task(
    subagent_type="code-refactor-master",
    prompt="Execute refactoring plan for auth module phase by phase"
)

# Step 3: Validate quality
Task(
    subagent_type="quality-gate",
    prompt="Run pre-commit checks on refactored code"
)
```

### Use Case 3: Implementing New Feature

```bash
# Step 1: Write specification
Task(
    subagent_type="spec-builder",
    prompt="Create EARS-compliant SPEC for user authentication feature"
)

# Step 2: Plan implementation
Task(
    subagent_type="implementation-planner",
    prompt="Design architecture for user authentication with JWT"
)

# Step 3: Implement with TDD
Task(
    subagent_type="tdd-implementer",
    prompt="Implement user authentication following the spec"
)

# Step 4: Update docs
Task(
    subagent_type="doc-updater",
    prompt="Sync documentation with new authentication feature"
)
```

### Use Case 4: Choosing Technologies

```bash
# Compare options
Task(
    subagent_type="web-research-specialist",
    prompt="Compare FastAPI vs Flask for microservices project - pros, cons, production experiences"
)

# Check official docs for winner
Task(
    subagent_type="library-researcher",
    prompt="Get FastAPI documentation on dependency injection and middleware"
)
```

---

## 🆚 Agent Comparison: Research Agents

### library-researcher vs web-research-specialist

| Aspect | library-researcher | web-research-specialist |
|--------|-------------------|------------------------|
| **Data Source** | Context7 MCP (official docs) | WebSearch (community) |
| **Model** | Haiku (fast) | Sonnet (complex synthesis) |
| **Use Case** | API usage, syntax lookup | Debugging, comparisons, known issues |
| **Output** | Code examples, API reference | Solutions, workarounds, discussions |
| **Speed** | Very fast (<10s) | Slower (30s-60s) |

**Decision tree**:
```
Is this a "how to use X API" question?
├─ YES → library-researcher
└─ NO → Is it debugging or comparison?
         ├─ YES → web-research-specialist
         └─ NO → Might not need research agent
```

**Examples**:
```
✅ library-researcher: "How to use Pydantic Field validation?"
✅ web-research-specialist: "Why is Pydantic Field validation failing?"

✅ library-researcher: "Show FastAPI BackgroundTasks examples"
✅ web-research-specialist: "FastAPI BackgroundTasks vs Celery - which to use?"
```

---

## 🔧 Agent Invocation Syntax

### Basic Invocation
```python
Task(
    subagent_type="agent-name",
    prompt="Your detailed task description"
)
```

### With Model Override (optional)
```python
Task(
    subagent_type="agent-name",
    prompt="Your task",
    model="opus"  # Override default model
)
```

### Common Patterns
```python
# Research then implement
Task(subagent_type="web-research-specialist", prompt="Research async patterns")
# ... then use findings ...
Task(subagent_type="tdd-implementer", prompt="Implement with async patterns")

# Plan then execute
Task(subagent_type="refactor-planner", prompt="Plan refactoring")
# ... review plan ...
Task(subagent_type="code-refactor-master", prompt="Execute phase 1 of plan")

# Debug then validate
Task(subagent_type="debug-helper", prompt="Fix error in auth.py")
Task(subagent_type="quality-gate", prompt="Validate fix")
```

---

## 📊 Agent Model Selection

| Model | Agents Using It | Reason |
|-------|----------------|--------|
| **Opus** | code-refactor-master, integration-designer | Complex reasoning, high-risk changes |
| **Sonnet** | refactor-planner, web-research-specialist, debug-helper, quality-gate, tdd-implementer, spec-builder, implementation-planner, trust-validator, tag-auditor, constitution-extractor, doc-updater, codebase-explorer | Balanced performance/cost |
| **Haiku** | library-researcher | Fast documentation lookup |

**Model override**: You can override default model with `model` parameter if needed.

---

## ⚡ Agent Performance Tips

### Fast Agents (<10s)
- library-researcher (Haiku, direct API calls)
- codebase-explorer (simple searches)

### Medium Agents (10-30s)
- debug-helper (analysis + suggestions)
- tag-auditor (verification)
- quality-gate (linting + tests)

### Slow Agents (30s-5min)
- web-research-specialist (multiple searches)
- code-refactor-master (file modifications)
- tdd-implementer (test + implementation cycle)

**Tip**: For long-running agents, continue working on other tasks. Agent results appear when ready.

---

## 🔗 Integration with SPECTER Workflow

### With `/ms.*` Commands

```bash
# Specification phase
/ms.specify "Feature: User authentication"
# → Creates SPEC

Task(subagent_type="spec-builder", prompt="Enhance SPEC with EARS patterns")
# → Validates/improves SPEC

# Planning phase
/ms.plan
# → Creates plan.md

Task(subagent_type="implementation-planner", prompt="Validate plan architecture")
# → Reviews plan

# Implementation phase
/ms.implement
# → Implements with TAG blocks

Task(subagent_type="tdd-implementer", prompt="Add tests for authentication")
# → TDD workflow

# Review phase
/ms.review
# → Quality checks

Task(subagent_type="quality-gate", prompt="Pre-commit validation")
# → Final checks

# Finish phase
/fin
# → Sync docs, commit, push
```

### With Hook System

Agents are invoked in hooks automatically:
- **UserPromptSubmit**: Constitution injection for sub-agents
- **PreToolUse**: Checkpoint creation before tool use
- **PostToolUse**: Post-processing after edits

---

## 📚 Further Reading

- **Agent Design Patterns**: See individual agent files for detailed workflows
- **SPECTER Workflow**: Check `CLAUDE.md` for project-wide guidelines
- **Constitution Compliance**: See `.specify/memory/constitution.md`
- **TAG System**: See `ms-workflow-tag-manager` skill

---

**Last Updated**: 2025-10-30
**Agent Count**: 15 total agents
**New in This Version**: code-refactor-master, refactor-planner, web-research-specialist

# My-Spec Agents Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-26
**Status**: Planned (Phase 4)

---

## Overview

My-Spec employs a team of 11 specialized AI agents (6 existing + 5 new) for workflow automation. Based on MoAI-ADK's proven multi-agent architecture, each agent has specific expertise and collaborates to achieve complex tasks.

**Total Agents**: 11
**Model Distribution**: Haiku 58%, Sonnet 25%, Opus 17%
**Collaboration**: Agent-to-agent delegation supported

---

## Agent Team Structure

### Existing Agents (6)

**1. codebase-explorer** (Haiku)
- **Purpose**: Find files by patterns, search code for keywords
- **Tools**: Glob, Grep, Read
- **When**: "Find similar features", "Search for API endpoints"

**2. constitution-extractor** (Haiku)
- **Purpose**: Extract project constraints from spec.md for Constitution Section IX
- **Tools**: Read, Write
- **When**: `/ms.constitution` command

**3. integration-designer** (Opus)
- **Purpose**: Design integration strategies for complex features
- **Tools**: All
- **When**: Complex architectural decisions

**4. tag-auditor** (Haiku)
- **Purpose**: Validate TAG blocks and traceability chains
- **Tools**: Grep, Read
- **When**: `/ms.analyze`, TAG validation

**5. trust-validator** (Haiku)
- **Purpose**: Validate TRUST 5 principles (Test, Readable, Unified, Secured, Trackable)
- **Tools**: Bash, Read
- **When**: `/ms.analyze`, code quality checks

**6. library-researcher** (Haiku)
- **Purpose**: Research latest library documentation via Context7 MCP
- **Tools**: Context7 MCP
- **When**: `/ms.plan`, library selection

### New Agents (5 - Phase 4)

**7. spec-builder** (Sonnet) 🆕
- **Purpose**: Create EARS-compliant specifications
- **Model**: Sonnet (deep reasoning)
- **Skills Used**: ms-foundation-ears, ms-essentials-review, ms-workflow-tag-manager
- **When**: `/ms.specify` command

**8. implementation-planner** (Opus) 🆕
- **Purpose**: Design implementation plans with library research
- **Model**: Opus (complex reasoning)
- **Collaborates With**: library-researcher, codebase-explorer
- **Skills Used**: All foundation Skills
- **When**: `/ms.plan` command

**9. tdd-implementer** (Sonnet) 🆕
- **Purpose**: RED-GREEN-REFACTOR TDD cycle implementation
- **Model**: Sonnet (code generation)
- **Skills Used**: ms-workflow-tag-manager, ms-foundation-trust
- **When**: `/ms.implement` command

**10. debug-helper** (Sonnet) 🆕
- **Purpose**: Error diagnosis and fix suggestions
- **Model**: Sonnet (complex reasoning)
- **Skills Used**: ms-essentials-debug
- **When**: Error occurs during implementation

**11. quality-gate** (Haiku) 🆕
- **Purpose**: Release validation (coverage, TRUST, linting, TAGs)
- **Model**: Haiku (fast validation)
- **Skills Used**: ms-foundation-trust, ms-workflow-tag-manager
- **When**: `/fin` command (before commit)

---

## Agent Collaboration Patterns

### Pattern 1: spec-builder Solo

```
User: /ms.specify "user authentication feature"
  ↓
spec-builder (Sonnet)
  ├─ Read user input (Korean or English)
  ├─ Apply EARS patterns (System SHALL, WHEN, WHILE, WHERE, IF)
  ├─ Translate Korean → English EARS
  ├─ Use ms-foundation-ears Skill for validation
  └─ Generate specs/*/spec.md
```

### Pattern 2: implementation-planner + library-researcher + codebase-explorer

```
User: /ms.plan
  ↓
implementation-planner (Opus)
  ├─ Read spec.md
  ├─ Delegate to library-researcher (Haiku)
  │   └─ Context7 MCP → Latest React docs
  ├─ Delegate to codebase-explorer (Haiku)
  │   └─ Ripgrep scan → Similar auth patterns
  ├─ Design TAG chain structure
  ├─ Create architecture diagram (Mermaid)
  └─ Generate plan.md
```

### Pattern 3: tdd-implementer Solo

```
User: /ms.implement
  ↓
tdd-implementer (Sonnet)
  ├─ Read plan.md and tasks.md
  ├─ RED Phase: Write failing test with @TEST:{TAG}
  ├─ GREEN Phase: Implement minimum code with @CODE:{TAG}
  ├─ REFACTOR Phase: Improve quality
  ├─ Use ms-workflow-tag-manager Skill for TAG blocks
  └─ Run tests and report results
```

### Pattern 4: quality-gate + tag-auditor + trust-validator

```
User: /fin
  ↓
quality-gate (Haiku)
  ├─ Delegate to trust-validator
  │   ├─ Check test coverage ≥85%
  │   ├─ Run linter (0 warnings)
  │   └─ Validate type safety
  ├─ Delegate to tag-auditor
  │   ├─ Scan TAG chains
  │   └─ Verify 100% traceability
  ├─ Generate validation report
  └─ Block commit IF any check fails
```

---

## Agent Personas (from MoAI-ADK)

### spec-builder Persona

- **Icon**: 🏗️
- **Job**: Requirements Engineer
- **Expertise**: EARS syntax, requirement analysis, ambiguity detection
- **Role**: SPEC document authoring specialist
- **Goal**: Create unambiguous, testable specifications
- **Mindset**: "Every requirement must answer: WHO does WHAT WHEN under WHICH conditions"
- **Decision Criteria**: Reject vague terms, enforce EARS patterns, verify testability
- **Communication Style**: Technical precision, clarifying questions
- **Specialized Area**: Korean-to-English EARS translation

### implementation-planner Persona

- **Icon**: 🎯
- **Job**: Solutions Architect
- **Expertise**: System design, library selection, TAG chain architecture
- **Role**: Implementation strategy designer
- **Goal**: Create efficient, maintainable implementation plans
- **Mindset**: "Prefer existing solutions over custom code"
- **Decision Criteria**: Simplicity-first, proven libraries, clear TAG chains
- **Communication Style**: Structured, trade-off analysis
- **Specialized Area**: Multi-agent collaboration orchestration

### tdd-implementer Persona

- **Icon**: ⚡
- **Job**: Test-Driven Developer
- **Expertise**: RED-GREEN-REFACTOR cycle, TAG auto-insertion
- **Role**: TDD implementation specialist
- **Goal**: Write tests first, implement clean code
- **Mindset**: "No code without tests"
- **Decision Criteria**: Test coverage ≥85%, TRUST compliance
- **Communication Style**: Methodical, test-focused
- **Specialized Area**: Automatic TAG block generation

---

## Usage Examples

### Example 1: Full Workflow

```bash
# Step 1: Create specification
/ms.specify "User authentication with JWT"
# → spec-builder creates specs/003-auth/spec.md

# Step 2: Design implementation
/ms.plan
# → implementation-planner creates plan.md
#   (collaborates with library-researcher for library docs)

# Step 3: Generate tasks
/ms.tasks
# → Creates tasks.md with TAG assignments

# Step 4: Implement feature
/ms.implement
# → tdd-implementer follows RED-GREEN-REFACTOR
#   (auto-inserts TAG blocks in code)

# Step 5: Update documentation
/ms.up-docs --all
# → doc-updater generates API docs from TAGs

# Step 6: Finish with quality gate
/fin
# → quality-gate validates coverage, TRUST, TAGs
#   (blocks commit if validation fails)
```

### Example 2: Error Handling

```bash
# Implementation error occurs
Error: TypeError: 'NoneType' object is not subscriptable

# debug-helper agent auto-triggered
debug-helper (Sonnet):
  ├─ Analyze stack trace
  ├─ Identify root cause: "Missing null check on user object"
  ├─ Suggest fix: "Add if user is None: return error"
  └─ Provide rollback: "git checkout {checkpoint-branch}"
```

---

## Model Distribution Strategy

**Why Different Models?**

| Model | Usage | Rationale |
|-------|-------|-----------|
| **Haiku** (58%) | Fast validation, simple tasks | Cost-efficient, fast execution |
| **Sonnet** (25%) | Code generation, error diagnosis | Balance of speed and reasoning |
| **Opus** (17%) | Complex architecture, planning | Deep reasoning for critical decisions |

**Agent Count by Model:**
- Haiku: 6-7 agents (55-64%)
- Sonnet: 3 agents (27%)
- Opus: 1-2 agents (9-18%)

---

## Implementation Status

**Phase 4 Status**: ⚪ PENDING (Not yet started)

**Timeline**:
- Week 9: spec-builder agent (7-10h)
- Week 10: implementation-planner agent (7-10h)
- Week 10-11: tdd-implementer agent (9-13h)
- Week 12: debug-helper, quality-gate agents (9-13h)

**Estimated Effort**: 33-48 hours

---

## Best Practices

### 1. Trust Agent Outputs

**Guideline**: Agent outputs are generally trusted, but review critical decisions

**Example**:
```bash
# ✅ Trust: spec-builder EARS conversion
# ⚠️ Review: implementation-planner library selection (verify versions)
# ❌ Don't trust blindly: debug-helper fix suggestions (test first)
```

### 2. Use Appropriate Model for Task

**Guideline**: Match agent model to task complexity

**Example**:
- Simple validation → Haiku (quality-gate)
- Code generation → Sonnet (tdd-implementer)
- Architecture design → Opus (implementation-planner)

### 3. Leverage Agent Collaboration

**Guideline**: Let agents delegate to specialists

**Example**:
```bash
# ✅ Good: implementation-planner delegates to library-researcher
# ❌ Bad: Manual library research before /ms.plan
```

---

## Troubleshooting

### Issue 1: Agent Not Found

**Symptom**: `/ms.specify` shows "agent not found"

**Solution**:
1. Verify agent file exists: `ls .claude/agents/spec-builder.md`
2. Check agent registered in Skills system
3. Restart Claude Code session

### Issue 2: Agent Delegation Fails

**Symptom**: implementation-planner doesn't call library-researcher

**Diagnosis**:
```bash
# Check agent collaboration logic
cat .claude/agents/implementation-planner.md
```

**Solution**:
1. Verify library-researcher agent exists
2. Check Context7 MCP server available
3. Review agent prompt for delegation logic

---

## References

- [Migration Guide](../migration/moai-integration-guide.md)
- [Skills Guide](skills-guide.md)
- [Living-Docs Guide](living-docs-guide.md)
- [MoAI-ADK Agents](https://github.com/modu-ai/moai-adk)

---

**Status**: Phase 4 Planning Complete (Implementation pending)

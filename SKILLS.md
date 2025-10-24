# Claude Code Skills - Integration with My-Spec Workflow

## Executive Summary

This document analyzes **Claude Code Skills** and proposes integration strategies for the **My-Spec workflow** (`.claude/commands/ms.*`).

**Key Finding**: Skills and Slash Commands serve different purposes and should be used complementarily.

---

## 1. What are Claude Code Skills?

### Definition

Skills are **modular, self-contained folders** containing instructions, scripts, and resources that extend Claude's capabilities.

**Key Characteristics**:
- **Auto-triggered**: Claude autonomously decides when to use a Skill based on request analysis
- **Progressive disclosure**: Only loads metadata (30-50 tokens) until needed
- **Executable code**: Can include Python/JavaScript scripts running in VM environment
- **Composable**: Multiple Skills can work together automatically

### Skills vs Slash Commands

| Aspect | Skills | Slash Commands (`/ms.*`) |
|--------|--------|--------------------------|
| **Trigger** | Auto-triggered by Claude | Explicitly invoked by user |
| **Context Loading** | Progressive (Level 1 → 2 → 3) | Immediate full load |
| **Use Case** | Repetitive tasks, domain expertise | Structured workflows, sequential steps |
| **User Control** | Implicit (Claude decides) | Explicit (user controls) |
| **Token Efficiency** | High (lazy loading) | Moderate (full prompt load) |

**Example**:
- **Skill**: User says "analyze this PDF" → Claude auto-selects PDF extraction Skill
- **Slash Command**: User types `/ms.implement` → Runs implementation workflow

---

## 2. Skills Architecture

### File Structure

**Minimal Structure**:
```
my-skill/
├── SKILL.md          # Required: Metadata + Instructions
└── [resources/]      # Optional: Scripts, docs, templates
```

**SKILL.md Format**:
```yaml
---
name: skill-name              # Required: lowercase, hyphens only, max 64 chars
description: What this skill does and when to use it  # Required: max 1024 chars
allowed-tools: [Read, Bash]   # Optional: Tool access restriction (Claude Code only)
license: MIT                  # Optional: License info
metadata:                     # Optional: Custom key-value pairs
  version: "1.0.0"
  author: "Your Name"
---

# Skill Name

[Instructions for Claude to follow]

## Usage Examples
- Example 1
- Example 2

## Guidelines
- Guideline 1
- Guideline 2
```

### Progressive Disclosure (3 Levels)

Claude loads Skills in stages to optimize context usage:

1. **Level 1 (Metadata)**: `name` + `description` (~30-50 tokens)
   - Always loaded in system prompt
   - Claude decides relevance based on this

2. **Level 2 (Instructions)**: Full `SKILL.md` content
   - Loaded when Claude determines Skill is relevant

3. **Level 3 (Resources)**: Additional files (scripts, docs)
   - Loaded on-demand during execution

**Token Efficiency**: Can have hundreds of Skills installed with minimal context penalty.

---

## 3. Skills Best Practices (from Anthropic)

### Writing Effective Skills

**DO**:
- ✅ **Be concise**: Keep SKILL.md under 500 lines (Claude is already smart)
- ✅ **Clear description**: Include specific keywords for when to use this Skill
- ✅ **Action-oriented name**: Use gerunds ("Processing PDFs", "Validating Forms")
- ✅ **Add context Claude doesn't know**: Domain rules, API schemas, specific workflows
- ✅ **Iterative development**: Use Claude to help build and test Skills

**DON'T**:
- ❌ Duplicate Claude's existing knowledge
- ❌ Vague descriptions ("Helps with Excel" → too broad)
- ❌ Over-explain common concepts
- ❌ Rely on Skills for critical deterministic tasks without validation scripts

### Freedom vs Consistency Trade-off

**High Freedom** (Natural language instructions):
- Use for: Creative tasks, complex decision-making
- Risk: Inconsistent behavior across runs

**Low Freedom** (Executable scripts):
- Use for: Database migrations, data validation, critical operations
- Benefit: Deterministic, reliable results

**Recommendation**: Critical tasks should have validation scripts that Claude executes (script output counts toward tokens, not script code).

---

## 4. Integration Strategy: Skills + My-Spec Workflow

### Current My-Spec Workflow Analysis

**Workflow Structure** (Sequential, Explicit):
```
/ms.init → /ms.specify → /ms.clarify → /ms.plan → /ms.constitution → /ms.tasks → /ms.implement → /ms.review
```

**Characteristics**:
- ✅ Well-defined stages (initialization → specification → implementation)
- ✅ Constitution-driven quality control
- ✅ TAG-based traceability (SPEC → TEST → CODE)
- ✅ Requires explicit user progression through steps

**Why Slash Commands work here**:
- Users need clear control over workflow progression
- Each step has specific prerequisites (e.g., `/ms.plan` requires `/ms.specify` first)
- Sequential execution is intentional (can't implement before planning)

### Skills Role: Workflow Assistance (Not Replacement)

**Principle**: Keep Slash Commands for workflow orchestration, use Skills for repetitive sub-tasks.

**Proposed Integration**:

| Task Type | Tool | Rationale |
|-----------|------|-----------|
| **Workflow Orchestration** | Slash Commands (`/ms.*`) | User controls progression, clear prerequisites |
| **Repetitive Validation** | Skills | Auto-triggered when Claude detects validation needs |
| **Code Quality Checks** | Skills | Auto-applied during implementation |
| **Documentation Updates** | Skills | Auto-updates Living Docs when code changes |
| **TAG Management** | Skills | Auto-inserts TAG blocks without manual prompting |

---

## 5. Recommended Skills for My-Spec

### Skill 1: Constitution Validator

**Purpose**: Automatically validate code against Constitution principles during implementation.

**File**: `.claude/skills/constitution-validator/SKILL.md`

```yaml
---
name: constitution-validator
description: Validates code implementation against My-Spec Constitution principles (EARS, TRUST, file size limits). Use when reviewing or implementing code.
allowed-tools: [Read, Grep, Bash]
---

# Constitution Validator Skill

Validates code against `.specify/memory/constitution.md` principles.

## When to Use
- After implementing code (auto-check before user review)
- When user asks "does this follow Constitution?"
- During `/ms.implement` or `/ms.review` workflows

## Validation Checklist

**Section II - Simplicity-First**:
- [ ] Files ≤500 SLOC (use `cloc` or line count)
- [ ] Functions ≤100 lines
- [ ] Complexity ≤10 per function (use complexity tools if available)

**Section IV - EARS Requirements**:
- [ ] Requirements use EARS keywords (WHEN/WHILE/WHERE/IF/SHALL)
- [ ] No forbidden phrases ("quickly", "securely", "appropriately")

**Section V - TRUST Principles**:
- [ ] Tests exist BEFORE implementation code
- [ ] Readable: Clear naming, ≤5 params, ≤4 nesting levels
- [ ] Unified: Strict typing (no `any` in TS, type hints in Python)
- [ ] Secured: Input validation, no hardcoded secrets
- [ ] Trackable: TAG blocks present

## Output Format
```
✅ Constitution Compliance Report

**PASS**: Simplicity (all files <500 SLOC)
**FAIL**: TRUST - Missing type hints in auth.py:42-67
**WARN**: EARS - Spec contains vague term "appropriately" in FR-3

Recommendations:
1. Add type hints to auth.py
2. Clarify FR-3 requirement using EARS pattern
```
```

---

### Skill 2: TAG Block Manager

**Purpose**: Automatically insert/update TAG blocks in code files.

**File**: `.claude/skills/tag-manager/SKILL.md`

```yaml
---
name: tag-manager
description: Manages TAG traceability blocks in code files (@CODE, @TEST, @SPEC chains). Use when creating or updating implementation code.
allowed-tools: [Read, Edit, Grep]
---

# TAG Block Manager Skill

Inserts and updates TAG traceability metadata in code files.

## When to Use
- After generating new code files
- When updating existing implementation
- When user asks to "add TAG blocks"

## TAG Block Format

**TypeScript/JavaScript**:
```typescript
/**
 * @CODE:AUTH-001
 * @SPEC: specs/001-auth-spec/spec.md
 * @TEST: tests/unit/auth.test.ts
 * @CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
 * @STATUS: implemented
 * @CREATED: 2025-10-23
 * @UPDATED: 2025-10-23
 */
```

**Python**:
```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-23
@UPDATED: 2025-10-23
"""
```

## Process
1. Detect file language (extension)
2. Extract TAG ID from task context
3. Find related SPEC and TEST file paths
4. Generate TAG block with current date
5. Insert at top of file (after shebang/imports if present)
6. Update @UPDATED field if TAG block exists

## Edge Cases
- If TAG already exists: Update @UPDATED date only
- If no TAG context available: Ask user for TAG ID
- If file is test file: Use @TEST instead of @CODE
```

---

### Skill 3: EARS Pattern Checker

**Purpose**: Validate requirements follow EARS standards.

**File**: `.claude/skills/ears-checker/SKILL.md`

```yaml
---
name: ears-checker
description: Validates requirements against EARS standards (WHEN/WHILE/WHERE/IF/SHALL patterns). Use when writing or reviewing specifications.
allowed-tools: [Read, Grep]
---

# EARS Pattern Checker Skill

Validates requirements against EARS (Easy Approach to Requirements Syntax) standards.

## When to Use
- During `/ms.specify` (auto-check spec.md)
- When user asks "are my requirements clear?"
- Before `/ms.plan` (validate spec quality)

## EARS Patterns

| Type | Keyword | Format |
|------|---------|--------|
| Unconditional | SHALL | System SHALL [capability] |
| Event-driven | WHEN | WHEN [event], system SHALL [action] |
| State-driven | WHILE | WHILE [state], system SHALL [action] |
| Optional | WHERE/MAY | WHERE [condition], system MAY [action] |
| Constraint | IF | IF [condition], system SHALL [constraint] |

## Forbidden Phrases
- "quickly", "securely", "well", "appropriately", "efficiently"
- Replace with specific, measurable criteria

## Validation Process
1. Scan spec.md for requirement statements
2. Check each requirement matches one of 5 EARS patterns
3. Flag forbidden vague phrases
4. Suggest EARS reformulations

## Output Format
```
📋 EARS Validation Report

**Total Requirements**: 12
**EARS Compliant**: 9
**Needs Revision**: 3

Issues:
1. FR-3: "The system should securely store passwords"
   ❌ Problem: Vague term "securely"
   ✅ Suggestion: "System SHALL hash passwords using bcrypt (cost factor ≥12) before database storage"

2. FR-7: "WHEN user logs in, display dashboard"
   ❌ Problem: Missing SHALL keyword
   ✅ Suggestion: "WHEN user logs in, system SHALL display dashboard"
```
```

---

### Skill 4: Living Docs Updater

**Purpose**: Auto-update API documentation when code changes.

**File**: `.claude/skills/living-docs-updater/SKILL.md`

```yaml
---
name: living-docs-updater
description: Automatically updates Living Documents (docs/api/) when implementation code changes. Use after modifying API endpoints or public interfaces.
allowed-tools: [Read, Write, Edit, Grep]
---

# Living Docs Updater Skill

Keeps API documentation synchronized with implementation code.

## When to Use
- After implementing/modifying API endpoints
- When public interfaces change (classes, functions, types)
- During `/ms.implement` workflow

## Process
1. Detect changed files (src/**/*.{ts,py})
2. Extract TAG ID from file header
3. Find/create corresponding doc: `docs/api/[TAG-ID].md`
4. Generate/update documentation:
   - Function signatures
   - Parameters and return types
   - Usage examples
   - Error cases
5. Add "Auto-updated" timestamp

## Documentation Template
```markdown
# [TAG-ID]: [Feature Name]

**Status**: Implemented
**Last Updated**: 2025-10-23 (Auto-updated)

## API Reference

### `functionName(param1, param2)`

**Description**: What this function does.

**Parameters**:
- `param1` (type): Description
- `param2` (type): Description

**Returns**: Return type and description

**Throws**:
- `ErrorType`: When this error occurs

**Example**:
\`\`\`typescript
const result = functionName("value1", "value2");
\`\`\`

## Related
- **SPEC**: specs/001-feature/spec.md
- **TEST**: tests/unit/feature.test.ts
- **CODE**: src/feature/module.ts
```
```

---

## 6. Skills vs Slash Commands Decision Matrix

Use this matrix to decide when to create a Skill vs Slash Command:

| Criteria | Skill | Slash Command |
|----------|-------|---------------|
| **Trigger Frequency** | Frequent, repetitive | Occasional, intentional |
| **User Awareness** | Background, automatic | Explicit, user-initiated |
| **Context Dependency** | Self-contained, reusable | Workflow-specific, sequential |
| **Prerequisites** | Minimal | Requires previous steps |
| **Scope** | Narrow, single responsibility | Broad, orchestrates multiple tasks |
| **Execution** | Auto-triggered by Claude | User types `/command` |

**Examples**:

✅ **Good Skill Candidates**:
- Constitution validation (auto-check during implementation)
- TAG block insertion (repetitive formatting)
- EARS pattern checking (auto-validation)
- Documentation updates (triggered by code changes)

❌ **Bad Skill Candidates** (Use Slash Commands Instead):
- Project initialization (`/ms.init` - one-time setup)
- Workflow orchestration (`/ms.specify → /ms.plan → /ms.implement`)
- User decision points (clarification, checklist generation)
- Multi-step processes with dependencies

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Create `.claude/skills/` directory structure
- [ ] Implement **Constitution Validator** Skill
- [ ] Test with existing codebase validation

### Phase 2: Traceability (Week 2)
- [ ] Implement **TAG Block Manager** Skill
- [ ] Integrate with `/ms.implement` workflow
- [ ] Validate auto-insertion works correctly

### Phase 3: Quality Assurance (Week 3)
- [ ] Implement **EARS Pattern Checker** Skill
- [ ] Auto-trigger during `/ms.specify`
- [ ] Test with existing specs

### Phase 4: Documentation (Week 4)
- [ ] Implement **Living Docs Updater** Skill
- [ ] Connect to `/ms.implement` completion
- [ ] Verify docs stay synchronized

### Phase 5: Optimization (Week 5-6)
- [ ] Measure token usage (Skills vs manual prompting)
- [ ] Collect user feedback
- [ ] Refine Skill descriptions for better auto-triggering
- [ ] Add executable validation scripts (Python/JS) for critical checks

---

## 8. Skills Development Best Practices (Applied to My-Spec)

### Iterative Development with Claude

**Step 1: Generate Skill with Claude**
```
"Help me create a Constitution Validator Skill that checks:
- File size limits (≤500 SLOC)
- EARS pattern usage
- TAG block presence
Generate the SKILL.md file."
```

**Step 2: Test with Separate Claude Instance**
```
"I have a Python file at src/auth.py. Validate it against Constitution."
→ Observe if Claude auto-triggers the Skill
```

**Step 3: Refine Description**
- If Claude doesn't auto-trigger: Add more specific keywords to `description`
- If Claude triggers incorrectly: Narrow scope in description

**Step 4: Add Validation Scripts**
For critical checks (file size, complexity), add executable scripts:

```python
# .claude/skills/constitution-validator/check_file_size.py
import sys
from pathlib import Path

def count_sloc(filepath):
    """Count source lines of code (excluding comments and blanks)"""
    with open(filepath) as f:
        lines = f.readlines()
    sloc = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
    return sloc

if __name__ == "__main__":
    filepath = sys.argv[1]
    sloc = count_sloc(filepath)

    if sloc > 500:
        print(f"❌ FAIL: {filepath} has {sloc} SLOC (limit: 500)")
        sys.exit(1)
    else:
        print(f"✅ PASS: {filepath} has {sloc} SLOC")
        sys.exit(0)
```

Claude can execute this script and only the output is added to context (not script code).

### Team Testing

Before deploying Skills project-wide:
1. Test with real user queries (not just developer assumptions)
2. Monitor false positives (Skill triggered incorrectly)
3. Monitor false negatives (Skill should trigger but didn't)
4. Refine `description` field based on observations

---

## 9. Integration with Existing Hooks

My-Spec already has hooks in `.claude/hooks/`:
- `constitution-injector.sh`: Injects Constitution into sub-agents
- `notify.sh`: Audio notifications for task completion

**Relationship**:
- **Hooks**: System-level automation (runs on specific events like tool calls)
- **Skills**: AI-level automation (Claude decides when to use)

**Complementary Usage**:
```
User: /ms.implement

→ Slash Command runs implementation workflow
  → Hook: constitution-injector.sh adds Constitution to context
    → Skill: tag-manager auto-inserts TAG blocks
      → Skill: living-docs-updater updates API docs
        → Skill: constitution-validator checks compliance
          → Hook: notify.sh plays completion sound
```

**No Conflicts**: Hooks and Skills operate at different layers and enhance each other.

---

## 10. Key Takeaways

### What We Learned

1. **Skills ≠ Replacement for Slash Commands**
   - Skills: Auto-triggered, repetitive tasks, background assistance
   - Slash Commands: User-controlled, workflow orchestration, sequential steps

2. **Token Efficiency is Real**
   - Progressive disclosure: Skills cost ~30-50 tokens until actually used
   - Can install hundreds of Skills without context penalty

3. **Executable Scripts > Natural Language**
   - For deterministic tasks (validation, formatting), use Python/JS scripts
   - Scripts run in VM, only output counts toward tokens

4. **Description is Critical**
   - Claude's auto-triggering depends on `description` field quality
   - Include specific keywords for when to use the Skill

### Recommended Strategy for My-Spec

**Keep Existing Workflow**:
- ✅ Slash Commands (`/ms.*`) remain the primary workflow
- ✅ User controls progression through stages

**Add Skills for Automation**:
- ✅ Constitution validation (auto-check)
- ✅ TAG block management (auto-insert)
- ✅ EARS pattern checking (auto-validate)
- ✅ Documentation updates (auto-sync)

**Result**: Best of both worlds - explicit workflow control + intelligent automation.

---

## 11. References

### Official Documentation
- [Claude Code Skills Documentation](https://docs.claude.com/ko/docs/claude-code/skills)
- [Skills Repository (anthropics/skills)](https://github.com/anthropics/skills)
- [Agent Skills Specification](https://github.com/anthropics/skills/blob/main/agent_skills_spec.md)

### My-Spec Workflow
- [Slash Commands](/.claude/commands/) - All `ms.*.md` files
- [Constitution](/.specify/memory/constitution.md) - Quality principles
- [Hooks](/.claude/hooks/) - System-level automation

### Example Skills (Anthropic)
- `artifacts-builder`: Complex HTML artifacts with React/Tailwind
- `webapp-testing`: Playwright-based local app testing
- `pdf`: PDF form field extraction
- `skill-creator`: Meta-skill for generating new Skills

---

## Appendix: Skills Directory Structure (Proposed)

```
.claude/skills/
├── constitution-validator/
│   ├── SKILL.md
│   ├── check_file_size.py
│   ├── check_complexity.py
│   └── validate_typing.py
├── tag-manager/
│   ├── SKILL.md
│   └── tag_templates.json
├── ears-checker/
│   ├── SKILL.md
│   └── patterns.yaml
└── living-docs-updater/
    ├── SKILL.md
    ├── template.md
    └── extract_api.py
```

**Next Steps**: Create these directories and implement Skills iteratively (see Roadmap).

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-23
**Author**: My-Spec Team

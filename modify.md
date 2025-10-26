# MoAI-ADK Integration 누락 사항 수정 명세서

**Feature ID**: MOAI-002
**Version**: 1.0.0
**Created**: 2025-10-26
**Status**: Draft
**Priority**: P0 (Critical)
**Type**: 기존 프로젝트 업데이트

---

## Executive Summary

System SHALL fix 12 critical issues discovered during MoAI-ADK integration verification (specs/002-moai-adk-integration). These issues include fail-open violations, missing safety features, incomplete Skills implementation, and missing agent automation that are explicitly required by spec.md but were not implemented or incorrectly implemented.

**Scope**: Bug fixes and missing feature implementation for MoAI-ADK integration
**Impact**: Workflow blocking (fail-open), safety regression (@IMMUTABLE), incomplete Spec compliance
**Verification Source**: Combined analysis from Claude Code + Codex (2025-10-26)

---

## 1. Feature Overview

### 1.1 Problem Statement

**Current Issues:**

| Issue | Severity | Impact | Spec Violation |
|-------|----------|--------|----------------|
| ms_hooks.py exits with code 1 on errors | CRITICAL | Blocks Claude Code sessions | FR-HOOKS-001~004 (fail-open) |
| @IMMUTABLE protection completely missing | CRITICAL | Safety regression, critical files unprotected | FR-HOOKS-005 (SHALL) |
| UserPromptSubmit tests missing | HIGH | TDD principle violation | Constitution Section I |
| 2 Essentials Skills missing | HIGH | Incomplete Spec compliance (7/11 Skills) | FR-SKILLS-004, FR-SKILLS-005 |
| doc-updater agent not automated | HIGH | Living-Docs broken delegation | FR-DOCS-002 (SHALL) |
| Sub-agent delegation not implemented | MEDIUM | Agent collaboration patterns missing | FR-AGENTS-001 |
| TAG integrity excludes .md files | MEDIUM | Misleading metrics (0% integrity) | Project accuracy |
| SPEC counting uses wrong format | MEDIUM | Misleading progress (0% complete) | Project accuracy |

**User Need**: Developer needs these 12 issues fixed to achieve full Spec compliance, restore safety features, and enable proper Living-Docs + agent collaboration.

### 1.2 Proposed Solution

**3-Phase Fix Strategy:**

```
Phase 1: CRITICAL Fixes (P0) - Week 1
├─ Fix fail-open violations (ms_hooks.py exit codes)
├─ Restore @IMMUTABLE protection (tags.py + ms.unlock)
└─ Add missing TDD tests (test_user_prompt_submit.py, test_immutable_protection.py)

Phase 2: HIGH Priority (P1) - Week 2-3
├─ Implement 2 missing Skills (ms-essentials-debug, ms-essentials-review)
├─ Automate doc-updater agent (FR-DOCS-002 compliance)
└─ Implement sub-agent delegation (FR-AGENTS-001 compliance)

Phase 3: MEDIUM/LOW Polish (P2-P3) - Week 4
├─ Fix TAG integrity calculation (.md file inclusion)
├─ Fix SPEC counting logic (Markdown metadata parsing)
└─ Fix .moai path references in Skills
```

---

## 2. Functional Requirements

### 2.1 CRITICAL Fixes (P0)

#### FR-FIX-001: Hook Fail-Open Exit Code Correction

**Requirement:**
WHEN ms_hooks.py encounters JSON parsing error or handler exception, system SHALL exit with code 0 (not code 1) to comply with fail-open policy.

**Acceptance Criteria:**
- `.claude/hooks/ms/ms_hooks.py` line 140 SHALL use `sys.exit(0)` after JSON error
- `.claude/hooks/ms/ms_hooks.py` line 148 SHALL use `sys.exit(0)` after handler exception
- System SHALL print error to stderr but continue Claude Code session
- System SHALL print fail-open payload: `{"continue": True, "systemMessage": None}`

**Current Code (Incorrect):**
```python
# Line 140 (JSON parse error)
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}", file=sys.stderr)
    sys.exit(1)  # ❌ WRONG - blocks Claude Code

# Line 148 (Handler exception)
except Exception as e:
    print(f"Handler error: {e}", file=sys.stderr)
    sys.exit(1)  # ❌ WRONG - blocks Claude Code
```

**Required Fix:**
```python
# Line 140 (JSON parse error)
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}", file=sys.stderr)
    print(json.dumps({"continue": True, "systemMessage": None}))
    sys.exit(0)  # ✅ CORRECT - fail-open

# Line 148 (Handler exception)
except Exception as e:
    print(f"Handler error: {e}", file=sys.stderr)
    print(json.dumps({"continue": True, "systemMessage": None}))
    sys.exit(0)  # ✅ CORRECT - fail-open
```

**Implementation Location:** `.claude/hooks/ms/ms_hooks.py`

**Test Requirements:**
- Add test case: `tests/hooks/test_ms_hooks_fail_open.py`
- Test JSON error → exit code 0
- Test handler exception → exit code 0

**Dependencies:**
- Spec reference: specs/002-moai-adk-integration/spec.md FR-HOOKS-001~004

---

#### FR-FIX-002: @IMMUTABLE TAG Protection Implementation

**Requirement:**
System SHALL implement file-level @IMMUTABLE protection as specified in FR-HOOKS-005, blocking edits to protected files and providing unlock mechanism.

**Acceptance Criteria:**

**File Creation:**
- System SHALL create `.claude/hooks/ms/core/tags.py` with functions:
  - `scan_immutable_tag(file_path: str) -> bool`: Scan file for @IMMUTABLE marker
  - `block_immutable_edit(file_path: str) -> HookResult`: Block edit with error message
- System SHALL create `.claude/commands/ms.unlock.md`: Unlock command implementation

**Protection Logic:**
- WHEN PreToolUse detects Edit/Write on file with @IMMUTABLE, system SHALL:
  1. Scan file for `@IMMUTABLE` marker using ripgrep
  2. Block operation completely (return `HookResult(continue_execution=False)`)
  3. Display error: "🚫 File protected by @IMMUTABLE. Use `/ms.unlock <file>` to edit."

**Unlock Mechanism:**
- WHEN user runs `/ms.unlock <file_path>`, system SHALL:
  1. Create Git checkpoint: `checkpoint/before-immutable-unlock-{timestamp}`
  2. Prompt for justification (minimum 10 characters)
  3. Log to `.specify/immutable_changes.log` with timestamp, file, justification, session ID
  4. Add file to session unlock list (in-memory)
  5. Display confirmation: "✅ Unlocked for this session. Restore: `git checkout {checkpoint}`"

**Session Tracking:**
- System SHALL track unlocked files in handler state (session-scoped dictionary)
- System SHALL clear unlock list when Claude Code session ends
- System SHALL re-apply protection on new session start

**Example TAG Block:**
```python
"""
@CODE:AUTH-001
@IMMUTABLE: Core authentication - security review required
@SPEC: specs/001-auth-spec/spec.md
"""
def authenticate_user(credentials: Credentials):
    # Protected implementation
```

**Implementation Locations:**
- `.claude/hooks/ms/core/tags.py` (new file)
- `.claude/hooks/ms/handlers/tool.py` (integrate scan in `handle_pre_tool_use`)
- `.claude/commands/ms.unlock.md` (new file)
- `tests/hooks/test_immutable_protection.py` (new test file)

**Test Requirements:**
- Test scan_immutable_tag detects marker
- Test block_immutable_edit prevents Edit
- Test unlock creates checkpoint
- Test unlock logs to file
- Test session-scoped unlock list

**Dependencies:**
- ripgrep installed
- Git repository initialized
- Spec reference: specs/002-moai-adk-integration/spec.md FR-HOOKS-005

**Migration Note:** This restores the protection from deleted `tag-enforcer.ts` with enhanced unlock workflow.

---

#### FR-FIX-003: UserPromptSubmit Hook Tests

**Requirement:**
System SHALL create comprehensive tests for UserPromptSubmit hook to comply with TDD principle.

**Acceptance Criteria:**
- System SHALL create `tests/hooks/test_user_prompt_submit.py` with minimum 15 test cases:
  1. Constitution injection succeeds
  2. Constitution content prepended to prompt
  3. Constitution marker `# Constitution Context (Auto-Injected)` added
  4. Constitution limited to 8000 tokens
  5. Constitution cached for session
  6. Missing Constitution triggers warning but continues (fail-open)
  7. Constitution file read error handled gracefully
  8. Empty Constitution file handled
  9. Large Constitution truncated correctly
  10. Multiple prompts reuse cached Constitution
  11. Session end clears Constitution cache
  12. Constitution injection skipped when already present
  13. Hook returns `continue_execution=True`
  14. Hook fails open on all exceptions
  15. Integration test with actual Constitution file

**Implementation Location:** `tests/hooks/test_user_prompt_submit.py` (new file)

**Test Structure:**
```python
import pytest
from handlers.user import handle_user_prompt_submit

class TestUserPromptSubmit:
    def test_constitution_injection_succeeds(self):
        # Test implementation

    def test_fail_open_on_missing_constitution(self):
        # Test implementation

    # ... 13 more tests
```

**Dependencies:**
- Existing implementation: `.claude/hooks/ms/handlers/user.py`
- Spec reference: specs/002-moai-adk-integration/spec.md FR-HOOKS-004
- AGENTS.md Section 2 (Test-First Development)

---

#### FR-FIX-004: @IMMUTABLE Protection Tests

**Requirement:**
System SHALL create comprehensive tests for @IMMUTABLE protection to verify blocking and unlock mechanism.

**Acceptance Criteria:**
- System SHALL create `tests/hooks/test_immutable_protection.py` with minimum 12 test cases:
  1. scan_immutable_tag detects @IMMUTABLE marker
  2. scan_immutable_tag returns False when no marker
  3. block_immutable_edit prevents Edit tool execution
  4. block_immutable_edit shows error message
  5. Unlock creates Git checkpoint
  6. Unlock requires justification (≥10 chars)
  7. Unlock logs to `.specify/immutable_changes.log`
  8. Unlock adds file to session list
  9. Unlocked file allows edit in same session
  10. New session re-applies protection
  11. Multiple files can be unlocked
  12. Unlock fails gracefully without Git repo

**Implementation Location:** `tests/hooks/test_immutable_protection.py` (new file)

**Test Structure:**
```python
import pytest
from core.tags import scan_immutable_tag, block_immutable_edit

class TestImmutableProtection:
    def test_scan_detects_immutable_marker(self):
        # Create temp file with @IMMUTABLE
        # Assert scan_immutable_tag returns True

    def test_unlock_creates_checkpoint(self):
        # Mock Git checkpoint creation
        # Verify checkpoint branch created

    # ... 10 more tests
```

**Dependencies:**
- Implementation: `.claude/hooks/ms/core/tags.py`
- Spec reference: specs/002-moai-adk-integration/spec.md FR-HOOKS-005

---

### 2.2 HIGH Priority Fixes (P1)

#### FR-FIX-005: ms-essentials-debug Skill Implementation

**Requirement:**
System SHALL implement `ms-essentials-debug` Skill based on MoAI-ADK's proven implementation to provide stack trace analysis and root cause identification.

**Acceptance Criteria:**
- System SHALL create `.claude/skills/ms-essentials-debug/SKILL.md` following 7-section template:
  1. Skill Metadata (name, version, model: Haiku, keywords: debug, error, stack trace)
  2. What It Does (stack trace analysis, root cause identification)
  3. When to Use (errors occur, exceptions thrown, debugging needed)
  4. How It Works (parse stack trace, identify error patterns, suggest fixes)
  5. Failure Modes (complex async errors, obfuscated traces)
  6. Best Practices (read full trace, check recent changes, verify assumptions)
  7. Examples (Python traceback, TypeScript error, async error)

**Progressive Disclosure:**
- Level 1 (Metadata): ≤100 tokens (YAML frontmatter)
- Level 2 (Instructions): 7 sections, ~300 LOC total
- Level 3 (Resources): Link to Constitution Section V (TRUST - Test-First)

**Content Requirements:**
- SHALL provide error pattern recognition (NoneType, undefined, async race conditions)
- SHALL suggest debugging steps (print statements, breakpoints, logging)
- SHALL reference Constitution debugging principles
- SHALL include Python and TypeScript examples

**Implementation Location:** `.claude/skills/ms-essentials-debug/SKILL.md` (new file)

**Reference Source:** MoAI-ADK `docs/references/moai-adk/skills/moai-essentials-debug.md`

**Dependencies:**
- Spec reference: specs/002-moai-adk-integration/spec.md FR-SKILLS-004
- Constitution Section V (TRUST principles)

---

#### FR-FIX-006: ms-essentials-review Skill Implementation

**Requirement:**
System SHALL implement `ms-essentials-review` Skill based on MoAI-ADK's proven implementation to provide code review checklist and best practices.

**Acceptance Criteria:**
- System SHALL create `.claude/skills/ms-essentials-review/SKILL.md` following 7-section template:
  1. Skill Metadata (name, version, model: Haiku, keywords: review, quality, checklist)
  2. What It Does (code review automation, quality checks, best practice validation)
  3. When to Use (before commit, after implementation, PR review)
  4. How It Works (checklist validation, pattern detection, suggestion generation)
  5. Failure Modes (subjective style issues, domain-specific patterns)
  6. Best Practices (review in small chunks, focus on logic first, then style)
  7. Examples (function review, security review, performance review)

**Review Checklist:**
- SHALL check: Code quality (readability, naming, complexity)
- SHALL check: Security (input validation, SQL injection, XSS)
- SHALL check: Performance (O(n²) loops, memory leaks, caching)
- SHALL check: Tests (coverage ≥85%, edge cases, mocking)
- SHALL check: Documentation (docstrings, comments, README)

**Content Requirements:**
- SHALL provide review checklist template
- SHALL reference Constitution principles (TRUST, OSOT, Simplicity-First)
- SHALL include Python and TypeScript review examples
- SHALL link to AGENTS.md quality standards

**Implementation Location:** `.claude/skills/ms-essentials-review/SKILL.md` (new file)

**Reference Source:** MoAI-ADK `docs/references/moai-adk/skills/moai-essentials-review.md`

**Dependencies:**
- Spec reference: specs/002-moai-adk-integration/spec.md FR-SKILLS-004
- AGENTS.md Section 6 (Code Quality Standards)

---

#### FR-FIX-007: doc-updater Agent Automation

**Requirement:**
System SHALL implement automated `doc-updater` agent to perform 3-phase document synchronization as specified in FR-DOCS-002.

**Acceptance Criteria:**

**Agent File Update:**
- System SHALL update `.claude/agents/doc-updater.md` with executable logic:
  - Phase 1: Git Diff Analysis (extract changed files, identify patterns)
  - Phase 2: Parallel Document Sync (API docs, dev daily, README)
  - Phase 3: TAG Chain Validation (scan chains, calculate integrity)

**Integration with /ms.up-docs:**
- WHEN user runs `/ms.up-docs`, system SHALL:
  1. Invoke doc-updater agent via Task tool
  2. Pass arguments: `--docs=<type>` or `--all` flag
  3. Receive sync report from agent
  4. Display results to user

**Agent Implementation:**
```markdown
# doc-updater Agent Prompt

You are the doc-updater agent (Haiku model). Your task is to synchronize Living Documents based on Git changes.

## Phase 1: Git Diff Analysis
1. Run: `git diff --cached --name-only` (staged changes)
2. OR run: `git diff HEAD~1 --name-only` (last commit)
3. Extract change patterns (new functions, modified APIs, deleted code)

## Phase 2: Parallel Document Sync
**API Docs:**
- Scan for @CODE tags: `rg '@CODE:([A-Z]+-[0-9]+)' --only-matching`
- Extract function signatures and docstrings
- Generate `docs/api/{TAG}.md` files

**Dev Daily:**
- Summarize Git diff with AI
- Append to `docs/dev_daily.md` with timestamp

**README:**
- IF major changes: Update project status, features, installation

## Phase 3: TAG Chain Validation
- Scan: `rg '@(SPEC|TEST|CODE|DOC):' -n`
- Verify complete chains: @SPEC → @TEST → @CODE → @DOC
- Calculate integrity: (Complete Chains / Total TAGs) * 100%

## Output Format
```json
{
  "sync_mode": "staged|all",
  "files_updated": ["docs/api/AUTH-001.md", "docs/dev_daily.md"],
  "tag_integrity": {"total": 25, "complete": 23, "score": 92.0},
  "duration_seconds": 8.5
}
```
```

**Implementation Location:** `.claude/agents/doc-updater.md` (update existing file)

**Test Requirements:**
- Integration test: `/ms.up-docs` delegates to agent
- Mock Git diff with sample changes
- Verify agent generates correct docs
- Test TAG chain validation accuracy

**Dependencies:**
- Spec reference: specs/002-moai-adk-integration/spec.md FR-DOCS-002
- `.claude/commands/ms.up-docs.md` (caller)
- `ms-workflow-living-docs` Skill

---

#### FR-FIX-008: Sub-Agent Delegation Logic Implementation

**Requirement:**
System SHALL implement agent collaboration patterns as specified in FR-AGENTS-001, enabling multi-agent delegation workflows.

**Acceptance Criteria:**

**Agent Collaboration Patterns:**
- System SHALL enable `implementation-planner` → `library-researcher` delegation
- System SHALL enable `implementation-planner` → `codebase-explorer` delegation
- System SHALL enable `quality-gate` → `trust-validator` delegation
- System SHALL enable `quality-gate` → `tag-auditor` delegation

**Implementation Strategy:**
- Update `.claude/agents/implementation-planner.md` with delegation logic:
```markdown
## Workflow

1. Read spec.md for requirements
2. **Delegate to library-researcher**: Get latest library docs
   - Use Task tool with subagent_type="library-researcher"
   - Pass library name and topic
3. **Delegate to codebase-explorer**: Find similar patterns
   - Use Task tool with subagent_type="codebase-explorer"
   - Pass search pattern
4. Design TAG chain structure
5. Generate plan.md
```

- Update `.claude/agents/quality-gate.md` with delegation logic:
```markdown
## Workflow

1. **Delegate to trust-validator**: Check TRUST 5 principles
   - Use Task tool with subagent_type="trust-validator"
   - Verify coverage ≥85%, linting, type safety
2. **Delegate to tag-auditor**: Validate TAG chains
   - Use Task tool with subagent_type="tag-auditor"
   - Verify 100% traceability
3. Generate validation report
4. Block commit IF any check fails
```

**Command Integration:**
- Update `/ms.plan` to invoke `implementation-planner` agent
- Update `/fin` to invoke `quality-gate` agent
- Preserve existing Task tool delegation syntax

**Implementation Locations:**
- `.claude/agents/implementation-planner.md` (update)
- `.claude/agents/quality-gate.md` (update)
- `.claude/commands/ms.plan.md` (update)
- `.claude/commands/fin.md` (update)

**Test Requirements:**
- Mock Task tool delegation
- Verify agent chain execution
- Test fallback when sub-agent unavailable

**Dependencies:**
- Spec reference: specs/002-moai-adk-integration/spec.md FR-AGENTS-001
- Claude Code Task tool

---

### 2.3 MEDIUM Priority Fixes (P2)

#### FR-FIX-009: TAG Integrity Calculation Fix

**Requirement:**
System SHALL expand TAG integrity scanning to include all file types (not just .py and .ts).

**Acceptance Criteria:**
- `.claude/hooks/ms/core/project.py` line 270 SHALL scan:
  - Markdown files: `specs/**/*.md`, `docs/**/*.md`
  - Python files: `**/*.py`
  - TypeScript files: `**/*.ts`, `**/*.tsx`
  - JavaScript files: `**/*.js`, `**/*.jsx`
  - Shell scripts: `**/*.sh`
  - Other: `**/*.go`, `**/*.rs` (if applicable)

**Current Code (Incorrect):**
```python
# Line 270
rg '@(SPEC|TEST|CODE):' --type py --type ts
```

**Required Fix:**
```python
# Scan all relevant file types
rg '@(SPEC|TEST|CODE|DOC):' \
   --type-add 'md:*.md' \
   -t md -t py -t ts -t js -t sh
```

**Implementation Location:** `.claude/hooks/ms/core/project.py` (line 270)

**Test Requirements:**
- Create test TAG in .md file
- Verify calculate_tag_integrity includes it
- Test integrity score accuracy

**Dependencies:**
- ripgrep installed

---

#### FR-FIX-010: SPEC Counting Logic Fix

**Requirement:**
System SHALL parse Markdown metadata format (not YAML frontmatter) for SPEC status counting.

**Acceptance Criteria:**
- `.claude/hooks/ms/core/project.py` line 224 SHALL recognize:
  - `**Status**: Draft`
  - `**Status**: In Progress`
  - `**Status**: Completed`

**Current Code (Incorrect):**
```python
# Line 224 - assumes YAML frontmatter
if 'status: completed' in content:
    completed_count += 1
```

**Required Fix:**
```python
# Parse Markdown metadata (case-insensitive)
import re
if re.search(r'\*\*Status\*\*:\s*completed', content, re.IGNORECASE):
    completed_count += 1
```

**Our SPEC Format:**
```markdown
**Status**: Draft
**Priority**: P0 (Critical)
```

**Implementation Location:** `.claude/hooks/ms/core/project.py` (line 224)

**Test Requirements:**
- Create test SPEC with `**Status**: Completed`
- Verify count_specs recognizes it
- Test progress percentage accuracy

---

### 2.4 LOW Priority Fixes (P3)

#### FR-FIX-011: .moai Path Reference Cleanup

**Requirement:**
System SHALL replace `.moai` path references in Skills documentation with correct My-Spec paths.

**Acceptance Criteria:**
- `.claude/skills/ms-foundation-constitution/SKILL.md` line 115 SHALL change:
  - FROM: `.moai/config.json`
  - TO: `.specify/memory/constitution.md`

**Implementation Location:** `.claude/skills/ms-foundation-constitution/SKILL.md` (line 115)

**Impact:** Documentation accuracy only (no code behavior change)

---

## 3. Implementation Plan

### Phase 1: CRITICAL Fixes (Week 1, 12-16h)

**Day 1-2: Fail-Open + @IMMUTABLE (8-10h)**
- [ ] FR-FIX-001: Fix ms_hooks.py exit codes (1h)
- [ ] FR-FIX-002: Implement tags.py + ms.unlock (4-6h)
- [ ] FR-FIX-003: Write test_user_prompt_submit.py (2h)
- [ ] FR-FIX-004: Write test_immutable_protection.py (2h)
- [ ] Run full test suite: `pytest tests/hooks/`

**Deliverables:**
- All hooks use exit(0) for fail-open
- @IMMUTABLE protection operational
- 100% test coverage for UserPromptSubmit + @IMMUTABLE

---

### Phase 2: HIGH Priority (Week 2-3, 18-24h)

**Week 2: Skills + doc-updater (12-16h)**
- [ ] FR-FIX-005: Implement ms-essentials-debug (4-6h)
- [ ] FR-FIX-006: Implement ms-essentials-review (4-6h)
- [ ] FR-FIX-007: Automate doc-updater agent (4-6h)
- [ ] Verify Skills count: 9/11 complete

**Week 3: Sub-Agent Delegation (6-8h)**
- [ ] FR-FIX-008: Update implementation-planner delegation (3-4h)
- [ ] FR-FIX-008: Update quality-gate delegation (3-4h)
- [ ] Integration test: /ms.plan → library-researcher
- [ ] Integration test: /fin → quality-gate → trust-validator

**Deliverables:**
- 11/11 Skills implemented (100%)
- Living-Docs agent automation working
- Multi-agent collaboration operational

---

### Phase 3: MEDIUM/LOW Polish (Week 4, 4-6h)

**Day 1: Metrics Fix (3-4h)**
- [ ] FR-FIX-009: Fix calculate_tag_integrity (1-2h)
- [ ] FR-FIX-010: Fix count_specs parsing (1-2h)
- [ ] Verify SessionStart dashboard accuracy

**Day 2: Documentation (1-2h)**
- [ ] FR-FIX-011: Fix .moai path references (30min)
- [ ] Update verification report (30min)
- [ ] Run final compliance check (30min)

**Deliverables:**
- Accurate TAG integrity metrics
- Accurate SPEC progress metrics
- Clean documentation (no .moai references)

---

## 4. Acceptance Criteria (Overall)

### Definition of Done

**CRITICAL (P0):**
- [ ] All hooks exit with code 0 on errors (fail-open verified)
- [ ] @IMMUTABLE protection blocks edits + unlock works
- [ ] UserPromptSubmit has ≥15 tests (100% coverage)
- [ ] @IMMUTABLE protection has ≥12 tests (100% coverage)

**HIGH (P1):**
- [ ] 11/11 Skills implemented (ms-essentials-debug, ms-essentials-review added)
- [ ] /ms.up-docs delegates to doc-updater agent
- [ ] implementation-planner → library-researcher delegation works
- [ ] quality-gate → trust-validator/tag-auditor delegation works

**MEDIUM (P2):**
- [ ] TAG integrity includes .md files (accurate metrics)
- [ ] SPEC counting recognizes Markdown metadata (accurate progress)

**LOW (P3):**
- [ ] No .moai path references in documentation

**Verification:**
- [ ] All tests pass: `pytest tests/`
- [ ] Spec compliance: 100% (12/12 issues fixed)
- [ ] No regression: Existing features still work

---

## 5. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| @IMMUTABLE breaks workflow | Medium | High | Comprehensive testing, unlock mechanism |
| Agent delegation complexity | Medium | Medium | Start with simple patterns, expand gradually |
| Test coverage insufficient | Low | Medium | Minimum 12-15 tests per feature |
| Regression in existing hooks | Low | High | Run full test suite after each change |

---

## 6. References

- **Primary Spec**: specs/002-moai-adk-integration/spec.md
- **Verification Report**: /tmp/final_comprehensive_report.md
- **Codex Analysis**: /tmp/additional_findings.md
- **Constitution**: .specify/memory/constitution.md
- **AGENTS.md**: CLAUDE.md (TDD principles)
- **MoAI-ADK Reference**: docs/references/moai-adk/

---

**Status**: Ready for Implementation
**Estimated Total Effort**: 34-46 hours over 4 weeks

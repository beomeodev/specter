# Quickstart Guide: MoAI-ADK Integration Fixes

**Branch**: `001-moai-adk-fixes` | **Date**: 2025-10-26

This guide provides manual testing procedures for each User Story implemented in the MoAI-ADK Integration Fixes feature.

---

## Prerequisites

Before testing, ensure the following are installed:

```bash
# 1. ripgrep ≥13.0 (TAG scanning, @IMMUTABLE detection)
rg --version  # Should show 13.0+
# Install: brew install ripgrep (Mac) or apt install ripgrep (Ubuntu)

# 2. Git ≥2.30 (checkpoint creation)
git --version  # Should show 2.30+

# 3. Python 3.13+ (hook system)
python --version  # Should show 3.13+

# 4. pytest (test runner)
pip install pytest pytest-cov
```

---

## User Story 1 - Safe Hook Failure Handling (Priority: P0) ✅

**Goal**: Verify hook system never blocks Claude Code sessions

### Test 1.1: JSON Parse Error Fail-Open

```bash
# Trigger JSON parse error in hook
echo '{"invalid json' | python .claude/hooks/ms/ms_hooks.py PreToolUse

# Expected output:
# - Error message to stderr with full stack trace
# - Payload: {"continue": True, "systemMessage": "..."}
# - Exit code: 0 (not 1)

# Verify exit code
echo $?  # Should be 0
```

### Test 1.2: Handler Exception Fail-Open

```bash
# Modify .claude/hooks/ms/handlers/tool.py to raise exception
# Add: raise ValueError("Test exception")
# at line 1 of handle_pre_tool_use()

# Trigger hook
python .claude/hooks/ms/ms_hooks.py PreToolUse < test_payload.json

# Expected:
# - Error printed to stderr
# - systemMessage includes "Hook error"
# - Exit code 0
# - Claude Code session continues

# Restore handlers/tool.py after test
```

### Test 1.3: Session Continuation

Start Claude Code session, trigger hook error, verify session continues normally with warning banner displayed.

---

## User Story 2 - Protected File Safety (Priority: P0) ✅

**Goal**: Verify @IMMUTABLE protection with unlock mechanism

### Test 2.1: Create Protected File

```bash
# Create test file with @IMMUTABLE marker
cat > test_protected.py <<EOF
# @IMMUTABLE - Critical authentication module
def authenticate_user(username, password):
    return True
EOF

# Verify file created
cat test_protected.py
```

### Test 2.2: Edit Blocked Until Unlock

```bash
# Attempt Edit via Claude Code (manual test)
# Use Edit tool on test_protected.py in Claude Code UI

# Expected block message:
# "🚫 File protected by @IMMUTABLE marker.
#    File: test_protected.py
#    Unlock: Run `/ms.unlock test_protected.py` to edit.
#    Reason: Critical file requires explicit unlock with audit trail."
```

### Test 2.3: Unlock File

```bash
# Run unlock command in Claude Code
/ms.unlock test_protected.py

# Enter justification when prompted:
# "Testing unlock mechanism for development"
# (Must be ≥10 chars)

# Expected output:
# "✅ File unlocked. Checkpoint: checkpoint/immutable-unlock-20251026-143000"
# "🔄 Rollback: git checkout checkpoint/immutable-unlock-20251026-143000"
```

### Test 2.4: Edit Now Allowed

```bash
# Attempt Edit again via Claude Code
# Expected: Edit proceeds normally (no block)
```

### Test 2.5: Protection Re-Applies After Session End

```bash
# End Claude Code session
# Start new Claude Code session

# Attempt Edit on test_protected.py
# Expected: Block message again (unlock cleared)
```

### Test 2.6: Verify Audit Log

```bash
# Check audit log
cat .specify/immutable_changes.log

# Expected format:
# [2025-10-26T14:30:00] File: test_protected.py | Session: session-20251026-143000 | Checkpoint: checkpoint/immutable-unlock-20251026-143000 | Justification: Testing unlock mechanism for development
```

### Test 2.7: Rollback Test

```bash
# Verify Git checkpoint created
git branch --list 'checkpoint/immutable-unlock-*'

# Expected: checkpoint/immutable-unlock-20251026-143000

# Test rollback
git checkout checkpoint/immutable-unlock-20251026-143000
# Expected: File restored to pre-unlock state
```

---

## User Story 3 - Complete Skills Ecosystem (Priority: P1) ✅

**Goal**: Verify 11/11 Skills complete with 7-section template

### Test 3.1: Count Skills

```bash
# Count Skills in .claude/skills/
find .claude/skills/ -name "SKILL.md" | wc -l

# Expected: 11 (9 existing + 2 new)
```

### Test 3.2: Verify ms-essentials-debug

```bash
# Check Skill exists
ls .claude/skills/ms-essentials-debug/SKILL.md

# Verify 7 sections present
grep -E '^## (What it does|When to use|How it works|Failure modes|Best practices|Examples)' \
  .claude/skills/ms-essentials-debug/SKILL.md | wc -l

# Expected: 6 headers (plus Metadata = 7 total)
```

### Test 3.3: Verify ms-essentials-review

```bash
# Check Skill exists
ls .claude/skills/ms-essentials-review/SKILL.md

# Verify 7 sections present
grep -E '^## (What it does|When to use|How it works|Failure modes|Best practices|Examples)' \
  .claude/skills/ms-essentials-review/SKILL.md | wc -l

# Expected: 6 headers (plus Metadata = 7 total)
```

### Test 3.4: Verify YAML Frontmatter

```bash
# Check YAML metadata in ms-essentials-debug
head -10 .claude/skills/ms-essentials-debug/SKILL.md

# Expected format:
# ---
# name: ms-essentials-debug
# version: 1.0.0
# model: all
# keywords: [debug, error-handling, stack-trace]
# ---
```

---

## User Story 4 - Automated Document Synchronization (Priority: P1) ✅

**Goal**: Verify `/ms.up-docs` delegates to doc-updater agent

### Test 4.1: Create @CODE Tags

```bash
# Create test file with @CODE tag
cat > src/test.py <<EOF
"""
@CODE:TEST-001
@SPEC: specs/001-moai-adk-fixes/spec.md
@TEST: tests/test_example.py
"""

def test_function():
    return True
EOF
```

### Test 4.2: Run Document Sync

```bash
# Run /ms.up-docs command in Claude Code
/ms.up-docs --all

# Expected:
# - doc-updater agent invoked via Task tool
# - Phase 1: Git diff analysis
# - Phase 2: Parallel document sync (API docs, dev daily, README)
# - Phase 3: TAG integrity report
# - Duration <10 seconds
```

### Test 4.3: Verify TAG Integrity Includes .md Files

```bash
# Create @SPEC tag in .md file
echo '# Feature\n\n@SPEC:TEST-002\nFeature description' > specs/001-moai-adk-fixes/test.md

# Run TAG integrity calculation
rg '@(SPEC|TEST|CODE|DOC):' -n --type-add 'md:*.md' --type md

# Expected: TEST-002 found in test.md
```

### Test 4.4: Verify SPEC Progress Parsing

```bash
# Create SPEC with Markdown metadata
cat > specs/001-moai-adk-fixes/test-spec.md <<EOF
# Feature Specification

**Status**: Completed
**Priority**: P1

## Summary
Feature description...
EOF

# Run count_specs() via SessionStart
# Expected: SPEC counted as completed (regex matches **Status**: completed)
```

---

## User Story 5 - Multi-Agent Collaboration (Priority: P1) ✅

**Goal**: Verify agent-to-agent delegation

### Test 5.1: implementation-planner Delegation

```bash
# Run /ms.plan for feature requiring external library
/ms.plan

# In spec.md, include:
# "System SHALL use JWT library for authentication"

# Expected in plan.md:
# ## Library Research Required
# 📚 **Delegation Recommendation**: library-researcher
# **Libraries to research**: jsonwebtoken
# ...
```

### Test 5.2: quality-gate Delegation

```bash
# Run /fin quality gate
/fin

# Expected:
# - quality-gate agent invoked
# - Delegates to trust-validator (TRUST 5 validation)
# - Delegates to tag-auditor (TAG chain verification)
# - Final quality report includes both validations
```

---

## User Story 6 - Accurate Project Metrics (Priority: P2) ✅

**Goal**: Verify SessionStart dashboard shows accurate metrics

### Test 6.1: TAG Integrity Score

```bash
# Create @SPEC tags in .md files
echo '@SPEC:TEST-003' > specs/001-moai-adk-fixes/test2.md

# Start new Claude Code session
# Expected SessionStart dashboard:
# TAG Integrity: 80.6% (not 0%)
# Includes TAGs from .md files
```

### Test 6.2: SPEC Progress Percentage

```bash
# Create completed SPEC
cat > specs/002-test-feature/spec.md <<EOF
# Feature Specification

**Status**: Completed

## Summary
...
EOF

# Start new Claude Code session
# Expected SessionStart dashboard:
# SPEC Progress: 50% (not 0%)
# Parses Markdown **Status**: Completed
```

---

## Full Test Suite

Run all automated tests:

```bash
# Run full test suite with coverage
pytest tests/hooks/ --cov=.claude/hooks/ms --cov-report=term-missing --cov-report=html

# Expected:
# - All tests PASS (green)
# - Coverage ≥85%
# - No CRITICAL violations
```

---

## Common Issues & Solutions

### Issue 1: ripgrep Not Found

**Symptom**: @IMMUTABLE scan fails with "rg: command not found"

**Solution**:
```bash
# Mac
brew install ripgrep

# Ubuntu/Debian
sudo apt install ripgrep

# Verify installation
rg --version
```

### Issue 2: Hook Exit Code 1

**Symptom**: Hook errors block Claude Code session

**Solution**:
- Verify `.claude/hooks/ms/ms_hooks.py` has fail-open wrapper (main() wrapped in try-except)
- Check exit code after error: `echo $?` (should be 0, not 1)
- Review implementation in T016-T019

### Issue 3: Protection Not Applied

**Symptom**: @IMMUTABLE file edits not blocked

**Solution**:
- Verify PreToolUse handler calls `scan_immutable_marker()`
- Check file contains `@IMMUTABLE` marker (case-sensitive)
- Verify ripgrep installed (`rg --version`)

### Issue 4: TAG Integrity 0%

**Symptom**: SessionStart shows 0% TAG integrity despite TAGs present

**Solution**:
- Verify ripgrep includes .md file type: `rg '@SPEC:' --type-add 'md:*.md' --type md`
- Check `core/project.py` calculate_tag_integrity() uses `--type-add 'md:*.md'`
- Review implementation in T061

### Issue 5: SPEC Progress 0%

**Symptom**: SessionStart shows 0% SPEC completion despite completed SPECs

**Solution**:
- Verify `spec.md` uses **Status**: Completed (Markdown format, not YAML)
- Check `core/project.py` count_specs() uses regex `**Status**:\s*completed`
- Review implementation in T062

---

## Success Validation Checklist

After testing all User Stories, verify:

- [ ] **SC-001**: Hook errors don't block workflows (exit code 0)
- [ ] **SC-002**: @IMMUTABLE files protected (100% blocks until unlock)
- [ ] **SC-003**: Test coverage ≥85% for hooks
- [ ] **SC-004**: 11/11 Skills complete (7-section template)
- [ ] **SC-005**: Living Documents synchronized (<10s)
- [ ] **SC-006**: Multi-agent delegation works (≥2 sub-agents)
- [ ] **SC-007**: Metrics accurate (TAG integrity and SPEC progress non-zero)
- [ ] **SC-008**: SessionStart dashboard shows accurate metrics
- [ ] **SC-009**: Audit trail complete (100% of unlocks logged)
- [ ] **SC-010**: Constitution compliance (≤500 SLOC, ≤10 complexity)

---

## Next Steps

1. Complete all manual tests above
2. Run full automated test suite
3. Verify all Success Criteria (SC-001 through SC-010)
4. Run `/fin` quality gate
5. Create pull request with test results

---

_Generated for MoAI-ADK Integration Fixes - Testing Guide_

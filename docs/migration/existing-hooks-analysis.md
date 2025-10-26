# Existing Hooks Functionality Analysis

**Date**: 2025-10-26
**Purpose**: Document existing hook implementations before migration to Python
**Status**: Pre-Migration Documentation

---

## Overview

This document analyzes the 3 existing hooks in the My-Spec project before migrating them to Python as part of the MoAI-ADK integration (Phase 0, Task T003).

---

## 1. constitution-injector.sh

**Location**: `.claude/hooks/constitution-injector.sh`
**Language**: Bash
**Trigger**: Task tool invocation
**Purpose**: Auto-inject Constitution and project context into sub-agents

### Functionality

**Detection Logic:**
- Triggers ONLY when `TOOL_NAME == "Task"`
- Detects sub-agent delegation (Task tool)

**Context Injection:**
- Reads 3 files:
  1. `.specify/memory/constitution.md` (Project Constitution)
  2. `docs/ai-context/project-structure.md` (Tech stack, file tree - if exists)
  3. `AGENTS.md` (AI instructions, coding standards)

**Injection Format:**
```markdown
## Auto-Loaded Project Context

This sub-agent has automatic access to:
- @.specify/memory/constitution.md (Project Constitution - EARS, TRUST, TAG)
- @docs/ai-context/project-structure.md (Tech stack, file tree - if exists)
- @AGENTS.md (AI instructions, coding standards)

**CRITICAL: All work must comply with Constitution Section IV (EARS) and Section V (TRUST).**

---

[Original Prompt]
```

**Output Behavior:**
- Prepends context injection to original prompt
- Outputs modified prompt to stdout

### Migration Notes

**Target Python Implementation:** `.claude/hooks/ms/handlers/user.py`

**Migration Strategy:**
1. Implement `handle_user_prompt_submit(payload: dict) -> HookResult`
2. Detect Task tool invocation: `"Task(" in prompt or "subagent_type=" in prompt`
3. Read Constitution: `Path(".specify/memory/constitution.md").read_text()`
4. Inject first 8000 tokens (MoAI-ADK pattern)
5. Cache Constitution content for session duration
6. Use Fail-open error handling (IF Constitution missing, warn but continue)

**Functional Equivalence Requirements:**
- [ ] Task tool detection works
- [ ] Constitution injection works
- [ ] Project context files injection preserved (AGENTS.md, project-structure.md)
- [ ] Prompt prepending behavior identical
- [ ] Performance <100ms (Constitution caching required)

---

## 2. tag-enforcer.ts

**Location**: `.claude/hooks/tag-enforcer.ts`
**Language**: TypeScript (Node.js)
**Trigger**: Edit, Write, MultiEdit, NotebookEdit tools
**Purpose**: Enforce TAG integrity and @IMMUTABLE protection

### Functionality

**Write Operation Detection:**
- Triggers on: `Write`, `Edit`, `MultiEdit`, `NotebookEdit`
- Extracts file path from tool_input:
  - `file_path`
  - `filePath`
  - `notebook_path`

**File Enforcement Filtering:**
- **Enforced extensions:** `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.md`, `.go`, `.rs`, `.java`, `.cpp`, `.hpp`
- **Excluded paths:**
  - Test files: `test`, `spec`, `__test__`
  - Dependencies: `node_modules`, `.git`, `dist`, `build`

**@IMMUTABLE Protection:**
- Reads original file content (IF file exists)
- Extracts new file content from tool_input
- Calls `checkImmutability(filePath, oldContent, newContent)`
- IF immutability violated:
  - Blocks operation (exit code 2)
  - Displays error message with unlock instructions
  - Output format:
    ```
    🚫 @IMMUTABLE TAG Modification Detected
    TAG {TAG_ID} is marked as @IMMUTABLE and cannot be modified.

    ✅ Recommended Actions:
    1. Create a new TAG ID for modified functionality
    2. Add @DOC marker to deprecated TAG
    3. Reference the old TAG in the new one
    ```

**TAG Chain Format Validation:**
- Detects TAG chain pattern: `CHAIN: @TYPE:ID -> @TYPE:ID -> @TYPE:ID`
- Calls `validateTAGChainFormat(chainStr)`
- **Warning only** (non-blocking)
- Outputs: `⚠️ TAG chain format warning: ...`

**Error Handling:**
- **Fail-open policy**: On error, don't block (safety first)
- Logs error to stderr
- Continues execution with success=true

### Migration Notes

**Target Python Implementation:** `.claude/hooks/ms/core/tags.py` + `.claude/hooks/ms/handlers/tool.py`

**Migration Strategy:**

**1. TAG Scanning (core/tags.py):**
```python
def scan_immutable_tag(file_path: str) -> bool:
    """Check if file contains @IMMUTABLE tag"""
    try:
        with open(file_path, "r") as f:
            content = f.read()
            return "@IMMUTABLE" in content
    except Exception:
        return False  # Fail-open
```

**2. @IMMUTABLE Blocking (handlers/tool.py in PreToolUse):**
```python
def block_immutable_edit(file_path: str) -> HookResult:
    """Block edit if @IMMUTABLE tag found"""
    if scan_immutable_tag(file_path):
        error_msg = f"""❌ IMMUTABLE TAG PROTECTION

File: {file_path}
Reason: This file contains @IMMUTABLE marker

To unlock:
1. Run: /ms.unlock {file_path}
2. Provide justification
3. Edit will be allowed for current session only
"""
        return HookResult(continue_execution=False, system_message=error_msg)

    return HookResult(continue_execution=True)
```

**3. Unlock Mechanism (new feature in Migration):**
- Create `/ms.unlock <file_path>` command
- Log unlock event to `.specify/immutable_changes.log`
- Allow editing for current session only
- Track unlocked files in memory (session-scoped)

**Functional Equivalence Requirements:**
- [ ] @IMMUTABLE detection works (ripgrep-based in Python)
- [ ] File write blocking works
- [ ] Error message displayed with unlock instructions
- [ ] Fail-open error handling preserved
- [ ] TAG chain validation (warning only) preserved
- [ ] File extension filtering identical
- [ ] Performance <100ms (PreToolUse is lightweight)

**Enhanced Features (Not in Original):**
- [ ] `/ms.unlock` command (audit trail for @IMMUTABLE changes)
- [ ] Session-scoped unlock tracking
- [ ] Git checkpoint before unlock

---

## 3. notify.sh

**Location**: `.claude/hooks/notify.sh`
**Language**: Bash
**Trigger**: Write, Edit tool completion
**Purpose**: Audio notification for task completion

### Functionality

**Sound Playback:**
- Task completion: `.claude/hooks/sounds/task-complete.mp3`
- Input needed: `.claude/hooks/sounds/input-needed.mp3`

**Trigger Conditions:**
- Task completion: `TOOL_NAME == "Write" OR "Edit"`
- Input needed: `TOOL_OUTPUT` contains "user" AND "confirm"

**Platform Support:**
- Windows/WSL: PowerShell `Media.SoundPlayer`

### Migration Notes

**Migration Decision:** **DELETE** (not migrating)

**Rationale:**
- Audio notifications are user preference, not workflow requirement
- Sound files do not exist in repository (`.claude/hooks/sounds/` missing)
- No references to this hook in documentation or commands
- Not critical to My-Spec workflow

**Action:**
- [ ] Verify sound files missing: `ls .claude/hooks/sounds/`
- [ ] Confirm no references: `rg "notify\.sh" -n`
- [ ] Delete file: `rm .claude/hooks/notify.sh`

---

## Migration Checklist

### Phase 1.3: Migrate Existing Hooks (Week 3, 8-9h)

**constitution-injector.sh → handlers/user.py (2h):**
- [ ] Implement `handle_user_prompt_submit(payload: dict) -> HookResult`
- [ ] Task tool detection logic
- [ ] Constitution reading and caching
- [ ] Prompt prepending (with context injection marker)
- [ ] Test: `tests/hooks/test_user_prompt_submit.py`
- [ ] Functional equivalence verified

**tag-enforcer.ts → core/tags.py + handlers/tool.py (4-5h):**
- [ ] Implement `scan_immutable_tag(file_path: str) -> bool`
- [ ] Implement `block_immutable_edit(file_path: str) -> HookResult`
- [ ] File extension filtering
- [ ] @IMMUTABLE detection (ripgrep-based)
- [ ] TAG chain format validation (warning only)
- [ ] Fail-open error handling
- [ ] Create `/ms.unlock` command (new feature)
- [ ] Test: `tests/hooks/test_tags.py`
- [ ] Functional equivalence verified

**notify.sh → DELETE (30min):**
- [ ] Verify sound files missing
- [ ] Confirm no references in codebase
- [ ] Delete file: `rm .claude/hooks/notify.sh`

**Update Configuration (30min):**
- [ ] Update `.claude/settings.local.json` with Python hooks
- [ ] Verify all 4 hook events configured

**Integration Testing (1h):**
- [ ] Test all 4 hook events in real Claude Code session
- [ ] Verify Constitution injection works
- [ ] Verify @IMMUTABLE protection works
- [ ] Verify checkpoint creation works (PreToolUse)
- [ ] Verify performance <100ms

---

## Functional Preservation Guarantee

**Critical Requirement:** 100% functional equivalence for:
1. **Constitution Injection**: Sub-agents receive Constitution context automatically
2. **@IMMUTABLE Protection**: File writes blocked when @IMMUTABLE tag present
3. **Fail-open Safety**: Hooks NEVER block on error (continue with warning)

**Enhanced Features (Not Breaking Changes):**
- `/ms.unlock` command (new audit trail for @IMMUTABLE changes)
- Git checkpoints (new safety feature)
- Performance logging (new observability)

---

## References

- **MoAI-ADK Hooks Reference**: `docs/references/moai-adk/.claude/hooks/alfred/`
- **Phase 1 Plan**: `specs/002-moai-adk-integration/plan.md` (Section 2.2 Phase 1)
- **Phase 1 Tasks**: `specs/002-moai-adk-integration/tasks.md` (Phase 1.3: T033-T041)

---

**Status**: ✅ Documentation Complete
**Next Step**: Proceed to Task T004 (Create directory structure)

# /ms.unlock - Unlock @IMMUTABLE Protected File

Temporarily unlocks @IMMUTABLE protected files with Git checkpoint and audit logging.

## Overview

@IMMUTABLE files are protected from accidental modification. This command allows intentional edits with proper justification and safety measures.

## Usage

```
/ms.unlock <file_path>
```

**Arguments**:
- `<file_path>`: Path to @IMMUTABLE file to unlock (absolute or relative)

**Example**:
```
/ms.unlock .specify/memory/constitution.md
```

## Execution Steps

### Step 1: Validate File Path

**Check file exists**:
```python
from pathlib import Path

file_path = args.get("file_path", "")
if not file_path:
    return "❌ Error: File path required\n\nUsage: /ms.unlock <file_path>"

file_abs_path = Path(file_path).resolve()
if not file_abs_path.exists():
    return f"❌ Error: File not found: {file_path}"
```

**Check file has @IMMUTABLE marker**:
```python
from core.immutable_protection import scan_immutable_marker

if not scan_immutable_marker(str(file_abs_path)):
    return f"ℹ️  File is not @IMMUTABLE protected: {file_path}\n\nNo unlock needed - file is editable."
```

**Check if already unlocked**:
```python
from core.immutable_protection import is_file_unlocked

if is_file_unlocked(str(file_abs_path)):
    return f"✅ File already unlocked in current session: {file_path}\n\nYou can edit this file normally."
```

### Step 2: Prompt for Justification

**Collect justification** via Claude Code AskUserQuestion:
```
Why do you need to unlock this @IMMUTABLE file?

Guidelines:
- Provide specific reason (≥10 characters)
- Examples: "Emergency production bug fix", "Constitutional amendment approved", "Feature requirement change"
- Justification will be logged to audit trail
```

**Validate justification**:
- Must be ≥10 characters
- Non-empty after stripping whitespace
- Max 3 attempts allowed

**If validation fails 3 times**:
```
❌ Unlock cancelled after 3 failed attempts

Justification must be at least 10 characters.

File remains protected: {file_path}
```

### Step 3: Execute Unlock

**Call unlock_file**:
```python
import os
from core.immutable_protection import unlock_file

result = unlock_file(
    file_path=str(file_abs_path),
    justification=user_justification,
    cwd=os.getcwd(),
)
```

**If unlock succeeds**:
```
✅ File unlocked successfully

📄 File: {file_path}
🔓 Status: Unlocked for current session
📝 Justification: {justification}
🛡️  Git Checkpoint: {checkpoint_ref}

⚠️  Important Notes:
  - Unlock is SESSION-SCOPED (lasts only until session ends)
  - Protection automatically re-applies on new session
  - All changes logged to .specify/immutable_changes.log
  - Git checkpoint created for rollback safety

You can now edit this file normally.
```

**If unlock fails**:
```
❌ Unlock failed: {error_message}

File remains protected: {file_path}

Common causes:
  - Not a Git repository (unlock requires Git for checkpoint)
  - Git not installed
  - Justification too short (<10 chars)

Please resolve the issue and try again.
```

### Step 4: Update Session State

**Unlock registry updated automatically** by `unlock_file()` function:
- File added to `UnlockRegistry` singleton
- Subsequent Edit/Write operations will pass PreToolUse check
- Unlock persists until SessionEnd event (session-scoped)

## Error Handling

### Error 1: File Not Found

**Symptom**: Specified file doesn't exist

**Message**:
```
❌ Error: File not found: path/to/file.py

Please verify the path and try again.
```

**Exit**: Return error message

### Error 2: File Not Protected

**Symptom**: File doesn't have @IMMUTABLE marker

**Message**:
```
ℹ️  File is not @IMMUTABLE protected: path/to/file.py

No unlock needed - file is editable without restrictions.
```

**Exit**: Return info message

### Error 3: Invalid Justification

**Symptom**: Justification <10 chars or empty

**Message**:
```
❌ Justification too short (minimum 10 characters)

Please provide a clear reason for unlocking this file.

Attempt 1/3
```

**Action**: Prompt again (max 3 attempts)

### Error 4: Git Repository Required

**Symptom**: unlock_file() fails due to missing Git

**Message**:
```
❌ Unlock failed: Not a Git repository

@IMMUTABLE unlock requires Git for checkpoint creation.

Please initialize Git:
  cd /workspace/project
  git init
  git add .
  git commit -m "Initial commit"
```

**Exit**: Return error with instructions

## Security & Audit

**All unlock operations logged to**:
```
.specify/immutable_changes.log
```

**Log format**:
```
[2025-10-26T14:30:00] UNLOCK
File: /workspace/project/.specify/memory/constitution.md
Justification: Emergency bug fix for production issue #1234
Checkpoint: immutable-unlock-20251026-143000
Session: claude-session-abc123
---
```

**Log rotation**: None (append-only audit trail)

**Retention**: Permanent (manually clean if needed)

## Session Lifecycle

1. **SessionStart**: UnlockRegistry is empty
2. **User runs /ms.unlock**: File added to registry
3. **During session**: File edits allowed
4. **SessionEnd**: UnlockRegistry.clear() called
5. **Next session**: Protection re-applies (must unlock again)

## Implementation Details

**Tools**: Read (validation), AskUserQuestion (justification), core.immutable_protection functions

**Dependencies**:
- ripgrep ≥13.0 (for @IMMUTABLE scanning)
- Git ≥2.30 (for checkpoint creation)

**Constraints**:
- Justification ≥10 characters
- Git repository required
- Session-scoped unlock (non-persistent)

## Related Commands

- **@IMMUTABLE marker**: Add to file to enable protection
- **PreToolUse hook**: Automatically blocks @IMMUTABLE edits
- **SessionEnd hook**: Clears unlock registry

## Notes

- Unlock is **session-scoped** (intentional design for security)
- Each new session requires re-unlock (prevents accidental edits)
- Git checkpoints created for every unlock (safe rollback)
- Audit log provides complete unlock history
- Protection re-applies automatically (no manual re-protection needed)

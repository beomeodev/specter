---
name: ms-workflow-tag-manager
description: Traceability automation skill that generates language-specific TAG blocks (Python docstrings, TypeScript JSDoc, Go comments) with complete SPEC→TEST→CODE→DOC chain metadata, ensures unique TAG ID assignment with validation using ripgrep scanning, provides automatic TAG insertion during /ms.implement workflow, supports status tracking (planned, in_progress, implemented, reviewed), and maintains temporal metadata (CREATED, UPDATED timestamps) for full requirement-to-code traceability. Use when implementing new features with /ms.implement, creating TAG blocks for code, generating traceability metadata, validating TAG ID uniqueness, or tracking implementation status
---

# Workflow: TAG Manager

## What it does

Manages TAG block lifecycle for SPECTER workflow traceability:
- Generates language-specific TAG blocks (Python, TypeScript, JavaScript)
- Creates complete @SPEC → @TEST → @CODE chains
- Ensures unique TAG ID assignment
- Provides templates for docstrings and JSDoc comments

## When to use

- During implementation (`/ms.implement` auto-invokes this Skill)
- When creating new feature files
- Adding TAG metadata to existing code
- Validating TAG chain completeness
- Generating TAG templates for manual insertion

## How it works

### TAG ID Format

**Structure**: `<DOMAIN>-<NUMBER>`

**Examples**:
- `AUTH-001`: Authentication feature #1
- `HOOKS-002`: Hooks system feature #2
- `LDOCS-003`: Living-Docs feature #3
- `SKILLS-004`: Skills system feature #4

**Domain Prefixes** (SPECTER integration):
- `HOOKS-XXX`: Hook system features
- `SKILLS-XXX`: Skills implementation
- `LDOCS-XXX`: Living-Docs system
- `AGENTS-XXX`: Sub-agents
- `INFRA-XXX`: Infrastructure tasks

**`FIX-<AREA>-XXX` (reserved — `/ms.fix` track)**: fixes with no governing
spec. Their TAG block records `@SPEC: (fix — no spec)`; the pre-commit
backstop (`scripts/check_tag_chain.py`) waives the `@SPEC` anchor for `FIX-*`
ids, requires `@TEST:FIX-…` for behavioral fixes, and accepts the literal
marker `@TEST: (presentational — no test)` for presentational ones. Never use
the `FIX-` prefix for Feature work.

### TAG Chain Structure

**Complete chain**:
```
@SPEC:TAG-ID → @TEST:TAG-ID → @CODE:TAG-ID → @DOC:TAG-ID (optional)
```

**File locations**:
- `@SPEC:TAG-ID`: In `specs/<spec-id>/spec.md`
- `@TEST:TAG-ID`: In `tests/` (test files)
- `@CODE:TAG-ID`: In `src/` or implementation files
- `@DOC:TAG-ID`: In `docs/` (optional, for API docs)

### TAG Block Templates

#### Python (Docstring)

```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

def authenticate_user(email: str, password: str) -> AuthResult:
    """Authenticates user with email and password."""
    pass
```

#### TypeScript/JavaScript (JSDoc)

```typescript
/**
 * @CODE:AUTH-001
 * @SPEC: specs/001-auth-spec/spec.md
 * @TEST: tests/unit/auth.test.ts
 * @CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
 * @STATUS: implemented
 * @CREATED: 2025-10-26
 * @UPDATED: 2025-10-26
 */
export function authenticateUser(email: string, password: string): AuthResult {
  // Implementation
}
```

#### Go (Block comment)

```go
/*
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/auth_test.go
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
*/
func AuthenticateUser(email string, password string) (*AuthResult, error) {
    // Implementation
}
```

### TAG Block Generation Algorithm

**Function signature**:
```python
def generate_tag_block(
    lang: str,
    tag_id: str,
    spec_path: str,
    test_path: str,
    status: str = "implemented",
    doc_path: str = None
) -> str:
    """
    Generates TAG block for given language.

    Args:
        lang: Language code (python, typescript, javascript, go, rust)
        tag_id: TAG ID (e.g., AUTH-001)
        spec_path: Path to spec file
        test_path: Path to test file
        status: Implementation status (implemented, in_progress, planned)
        doc_path: Optional path to documentation

    Returns:
        Formatted TAG block string
    """
```

**`@UPDATED` rule (must reflect reality, not creation time)**: `@UPDATED` is
**derived from git**, not hand-stamped. For a file already tracked, it is the
date of the file's last commit (`git log -1 --format=%cs -- <file>`); only for a
brand-new (untracked) file does it equal `@CREATED` (= today). A hand-maintained
`@UPDATED` drifts and lies (Trackable failure) — so never set it to "today" on an
edit unless the file is actually being committed today. If git derivation isn't
available at generation time, omit `@UPDATED` rather than write a false date.

**Implementation**:
```python
import subprocess
from datetime import date

def _git_last_modified(file_path: str) -> str | None:
    """Last-commit date (YYYY-MM-DD) for a tracked file, else None (new/untracked)."""
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", file_path],
        capture_output=True, text=True,
    )
    stamp = out.stdout.strip()
    return stamp or None

def generate_tag_block(lang, tag_id, spec_path, test_path, status="implemented",
                       doc_path=None, code_path=None):
    today = date.today().strftime("%Y-%m-%d")
    # @UPDATED = git last-modified for existing files; today only for new files.
    updated = (_git_last_modified(code_path) if code_path else None) or today

    chain = f"@SPEC:{tag_id} → @TEST:{tag_id} → @CODE:{tag_id}"
    if doc_path:
        chain += f" → @DOC:{tag_id}"

    content = f"""@CODE:{tag_id}
@SPEC: {spec_path}
@TEST: {test_path}
@CHAIN: {chain}
@STATUS: {status}
@CREATED: {today}
@UPDATED: {updated}"""

    if doc_path:
        content = f"""@CODE:{tag_id}
@SPEC: {spec_path}
@TEST: {test_path}
@DOC: {doc_path}
@CHAIN: {chain}
@STATUS: {status}
@CREATED: {today}
@UPDATED: {updated}"""

    # Language-specific formatting
    if lang in ["python"]:
        return f'"""\n{content}\n"""'
    elif lang in ["typescript", "javascript"]:
        return f'/**\n * ' + content.replace('\n', '\n * ') + '\n */'
    elif lang in ["go", "rust", "c", "cpp"]:
        return f'/*\n{content}\n*/'
    else:
        return f'# {content.replace(chr(10), chr(10) + "# ")}'
```

### TAG Uniqueness Validation

**Check for duplicate TAG IDs**:
```bash
# Search for TAG ID in entire codebase
rg "@(SPEC|TEST|CODE|DOC):AUTH-001" -n specs/ tests/ src/ docs/

# Count occurrences
rg "@SPEC:AUTH-001" -c specs/
```

**Validation rules**:
- Each TAG ID must be unique across the project
- Same TAG ID used in @SPEC, @TEST, @CODE forms the chain
- Duplicate @SPEC:ID or @CODE:ID indicates error

### TAG Auto-Insertion Workflow

**When `/ms.implement` runs**:

1. **Select TAG ID** from tasks.md (first uncompleted task)
2. **Read spec.md** to find @SPEC:TAG-ID reference
3. **Generate test file** with @TEST:TAG-ID block
4. **Generate code file** with @CODE:TAG-ID block
5. **Verify chain** with `rg` scan

**File placement**:
- Test files: Mirror `src/` structure in `tests/`
- Code files: Follow project structure from plan.md
- TAG blocks: Always at file/function/class level

## Inputs
- TAG ID (e.g., AUTH-001)
- Language (python, typescript, go, etc.)
- Spec file path
- Test file path
- Optional doc file path

## Outputs
- Formatted TAG block (language-specific)
- Complete @SPEC → @TEST → @CODE chain
- Validation status (unique/duplicate)
- Insertion location recommendation

## Example Usage

**Scenario**: Implement AUTH-001 authentication feature

**Step 1**: Generate TAG block for test file (Python)
```python
# Input
tag_id = "AUTH-001"
spec_path = "specs/001-auth-spec/spec.md"
test_path = "tests/unit/test_auth_service.py"

# Output
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""
```

**Step 2**: Insert at file top
```python
"""
@TEST:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@CODE: src/auth/service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

import pytest
from src.auth.service import authenticate_user

def test_authenticate_user_success():
    result = authenticate_user("test@example.com", "password123")
    assert result.success is True
```

**Step 3**: Verify TAG chain
```bash
rg "@(SPEC|TEST|CODE):AUTH-001" -n specs/ tests/ src/

# Expected output:
# specs/001-auth-spec/spec.md:15:@SPEC:AUTH-001
# tests/unit/test_auth_service.py:2:@TEST:AUTH-001
# src/auth/service.py:2:@CODE:AUTH-001
```

## TAG Status Values

| Status | Meaning | When to use |
|--------|---------|-------------|
| `planned` | Feature not yet started | During `/ms.tasks` generation |
| `in_progress` | Currently implementing | During TDD RED/GREEN phases |
| `implemented` | Code complete, tests pass | After REFACTOR phase |
| `reviewed` | Code review approved | After `/ms.review` |
| `deprecated` | No longer used | When retiring features |

## TAG Update Protocol

**When modifying tagged code**:
1. Update `@UPDATED` timestamp to current date
2. Keep `@CREATED` timestamp unchanged
3. If functionality changes significantly, consider new TAG ID
4. Update corresponding @SPEC if requirements changed

**Example**:
```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-27  ← Updated after modification
"""
```

## Integration with /ms.implement

**Automatic TAG block insertion**:

```bash
# User runs
/ms.implement

# System:
# 1. Auto-selects TAG-ID from tasks.md
# 2. Reads spec.md for @SPEC:TAG-ID
# 3. Generates test file with @TEST:TAG-ID
# 4. Generates code file with @CODE:TAG-ID
# 5. Inserts TAG blocks using this Skill
# 6. Verifies chain integrity
```

**No manual TAG creation required** - `/ms.implement` handles it automatically.

## Related Skills
- `ms-foundation-trust`: TAG chain validation (Trackable principle)

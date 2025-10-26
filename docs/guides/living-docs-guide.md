# My-Spec Living-Docs Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-26
**Status**: Planned (Phase 3)

---

## Overview

Living-Docs is a CODE-FIRST automatic documentation synchronization system that keeps docs in sync with code by scanning TAG blocks and Git diffs. No more manual documentation updates!

**Key Features:**
- 📄 **API Docs**: Auto-generated from @CODE tags and function signatures
- 📝 **Dev Daily**: Auto-updated from Git diff summaries
- 📖 **README**: Auto-updated when major changes detected
- ⚡ **Fast**: 30min → 2min (93% reduction)
- 🔗 **Traceable**: 100% TAG chain integrity validation

---

## Commands

### /ms.up-docs - Universal Document Synchronization

**Syntax:**
```bash
/ms.up-docs                # Staged changes only (default)
/ms.up-docs AUTH-001       # Specific TAG only (API docs)
/ms.up-docs --docs=api     # API docs only (staged changes)
/ms.up-docs --docs=dev     # Dev daily only (staged changes)
/ms.up-docs --docs=readme  # README only (if major changes staged)
/ms.up-docs --all          # Full regeneration (ignore staging)
```

**Staged Changes Logic:**
```bash
# Default behavior
/ms.up-docs

WHEN user runs without --all flag, system SHALL:
1. Run `git diff --cached` to detect staged changes
2. Sync only docs related to staged files
3. Generate sync report with affected TAGs

IF no staged changes exist, display warning:
⚠️ No staged changes found.
Use 'git add <files>' first or run '/ms.up-docs --all' for full sync.
```

**Example Output:**
```
🔄 Document Sync Complete

Updated Files:
  ✓ docs/api/AUTH-001.md (TAG-based generation)
  ✓ docs/dev_daily.md (Git diff summary)
  ✓ README.md (project status update)

TAG Chain Validation:
  ✓ 45 complete chains (SPEC → TEST → CODE)
  ⚠️ 2 orphaned @CODE tags (manual review needed)

Duration: 1m 47s
```

---

## doc-updater Agent

**Model**: Haiku (fast, cost-efficient)
**Purpose**: 3-phase document synchronization

### Phase 1: Git Diff Analysis (2-3min)

```bash
# Detect changes
git diff HEAD~1 --name-only

# Extract patterns
- New functions added: 5
- Modified APIs: 3
- Deleted code: 1 file

# Determine major vs minor changes
Major change indicators:
- New API endpoints
- Breaking changes
- New features
- Architecture changes
```

### Phase 2: Parallel Document Sync (5-10min)

**API Docs:**
```bash
# Scan for TAG blocks
rg '@CODE:AUTH-001' -n

# Extract function signatures
def authenticate_user(credentials: Credentials) -> User:
    """Authenticate user with JWT token"""

# Generate docs/api/AUTH-001.md
## AUTH-001: User Authentication

**Function**: `authenticate_user(credentials: Credentials) -> User`

**Purpose**: Authenticate user with JWT token

**Parameters**:
- `credentials`: User credentials (email, password)

**Returns**: Authenticated user object with JWT token

**Example**:
```python
user = authenticate_user({"email": "test@test.com", "password": "secret"})
print(user.token)  # eyJ0eXAiOiJKV1...
```
```

**Dev Daily:**
```bash
# Summarize Git diff
git diff HEAD~1 --stat

# Append to docs/dev_daily.md
## 2025-10-26

**Changes**:
- Added user authentication (AUTH-001)
- Implemented JWT token generation
- Added password hashing with bcrypt

**Files Modified**:
- `src/auth/service.py` (+120 lines)
- `tests/auth/test_service.py` (+45 lines)

**TAG**: @CODE:AUTH-001
```

**README:**
```markdown
IF major changes detected:
  Update README.md:
  - Project status (SPEC progress percentage)
  - Installation steps (new dependencies)
  - Usage examples (new features)
```

### Phase 3: TAG Chain Validation (3-5min)

```bash
# Scan all TAGs
rg '@(SPEC|TEST|CODE|DOC):' -n

# Verify complete chains
@SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001 → @DOC:AUTH-001 ✓

# Find orphaned tags
@CODE:USER-002  # Missing @SPEC and @TEST ⚠️

# Calculate integrity score
Integrity Score: 95.6% (43/45 complete chains)
```

---

## Integration with /fin and /finq

### Before Integration

```bash
/fin:  Update dev_daily.md (manual) → make ci → git commit && push
/finq: Update dev_daily.md (manual) → git commit && push (no CI)
```

### After Integration

```bash
/fin:  /ms.up-docs --docs=dev → make ci → git commit && push
/finq: /ms.up-docs --docs=dev → git commit && push (no CI)
```

**Benefits:**
- ✅ No manual dev_daily.md updates
- ✅ Consistent Git diff summaries
- ✅ Automated TAG validation before commit

---

## File Formats

### API Doc Template (docs/api/{TAG}.md)

```markdown
# {TAG}: {Feature Name}

**TAG Chain**: @SPEC:{TAG} → @TEST:{TAG} → @CODE:{TAG}

## Overview

[Function description from docstring]

## Function Signature

```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """Docstring"""
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| param1 | Type1 | [Description] |
| param2 | Type2 | [Description] |

## Returns

**Type**: ReturnType
**Description**: [Return value description]

## Example

```python
# Usage example
result = function_name(arg1, arg2)
print(result)
```

## Tests

**Test File**: tests/path/to/test_file.py
**Coverage**: 95%

## Related TAGs

- @SPEC:{TAG}: specs/path/to/spec.md
- @TEST:{TAG}: tests/path/to/test.py
```

### Dev Daily Format (docs/dev_daily.md)

```markdown
# Development Daily Log

## 2025-10-26

**Summary**: Implemented user authentication

**Changes**:
- Added user authentication (AUTH-001)
- Implemented JWT token generation
- Added password hashing with bcrypt

**Files Modified**:
- `src/auth/service.py` (+120 lines)
- `tests/auth/test_service.py` (+45 lines)

**TAG**: @CODE:AUTH-001

**Tests**: 18/18 passing

---

## 2025-10-25

[Previous day's log...]
```

---

## Usage Examples

### Example 1: Update API Docs After Implementation

```bash
# Implement feature
/ms.implement

# Stage changes
git add src/auth/service.py

# Update API docs for staged changes
/ms.up-docs --docs=api

# Verify
cat docs/api/AUTH-001.md
```

### Example 2: Daily Log Before Commit

```bash
# Make changes throughout the day
# ... code, code, code ...

# Stage all changes
git add .

# Update dev daily (auto-summarizes Git diff)
/ms.up-docs --docs=dev

# Finish with CI
/fin
```

### Example 3: Full Documentation Regeneration

```bash
# Regenerate all docs from scratch
/ms.up-docs --all

# Review changes
git diff docs/
```

---

## Deprecation: ms.update-docs

**Status**: Deprecated (Week 8)
**Replacement**: `/ms.up-docs`

**Migration**:
```bash
# Old command
/ms.update-docs

# New command
/ms.up-docs --all
```

**Timeline:**
- Week 8: Deprecation warning added
- Week 9: Command file removed
- Week 10: Documentation updated

---

## Implementation Status

**Phase 3 Status**: ⚪ PENDING (Not yet started)

**Timeline**:
- Week 7: /ms.up-docs command implementation (6-8h)
- Week 7-8: doc-updater agent implementation (9-12h)
- Week 8: /fin, /finq integration (3-5h)
- Week 8: Remove ms.update-docs (1-2h)

**Estimated Effort**: 19-27 hours

---

## Performance Targets

| Operation | Baseline | Target | Strategy |
|-----------|----------|--------|----------|
| Full regeneration | 30 minutes | 2 minutes | Haiku model, parallel sync |
| Staged changes sync | 15 minutes | 1 minute | Incremental updates only |
| TAG validation | 15 minutes | 10 seconds | Ripgrep batch scan |

---

## Best Practices

### 1. Stage Changes Before /ms.up-docs

**Guideline**: Use Git staging area to control what gets documented

```bash
# ✅ Good: Stage intentional changes
git add src/auth/service.py tests/auth/test_service.py
/ms.up-docs  # Documents only staged files

# ❌ Bad: Run without staging
/ms.up-docs  # Warning: No staged changes
```

### 2. Use --docs= Flags for Targeted Updates

**Guideline**: Update specific doc types to save time

```bash
# API docs only (after implementation)
/ms.up-docs --docs=api

# Dev daily only (before commit)
/ms.up-docs --docs=dev

# README only (after major feature)
/ms.up-docs --docs=readme
```

### 3. Validate TAG Chains Regularly

**Guideline**: Check TAG integrity before important commits

```bash
# Run full validation
/ms.up-docs --all

# Review orphaned TAGs
cat docs/tag_validation_report.md
```

---

## References

- [Migration Guide](../migration/moai-integration-guide.md)
- [Hooks Guide](hooks-guide.md)
- [Skills Guide](skills-guide.md)
- [MoAI-ADK Living-Docs](https://github.com/modu-ai/moai-adk)

---

**Status**: Phase 3 Planning Complete (Implementation pending)

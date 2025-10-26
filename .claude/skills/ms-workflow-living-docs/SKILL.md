---
name: ms-workflow-living-docs
description: Generates and syncs Living Documentation from TAG-scanned code. Use when updating docs with /ms.up-docs or syncing API documentation.
allowed-tools:
  - Read
  - Bash
  - Grep
  - Write
  - Edit
version: 1.0.0
created: 2025-10-26
---

# Workflow: Living-Docs Manager

## Skill Metadata
| Field | Value |
| ----- | ----- |
| Version | 1.0.0 |
| Created | 2025-10-26 |
| Allowed tools | Read, Bash, Grep, Write, Edit |
| Auto-load | `/ms.up-docs`, `/fin`, `/finq`, doc synchronization |
| Trigger cues | Documentation sync, API docs, TAG scanning, Living Documentation |

## What it does

Manages Living Documentation lifecycle for My-Spec workflow:
- Scans code for TAG blocks (@CODE, @TEST, @DOC references)
- Generates API documentation from TAG-annotated code
- Updates dev daily logs with Git diff summaries
- Synchronizes README with project status
- Validates TAG chain completeness (SPEC → TEST → CODE → DOC)

## When to use

- After implementing features (`/ms.up-docs` after `/ms.implement`)
- Before committing code (`/fin` or `/finq` commands)
- Syncing API documentation with code changes
- Updating project README with current status
- Validating TAG chain integrity
- Generating Living Docs reports

## How it works

### TAG Scanning Algorithm

**Scan for TAG blocks in code**:
```bash
# Find all TAG references
rg '@(SPEC|TEST|CODE|DOC):([A-Z]+-[0-9]+)' -n -or '$1:$2' specs/ tests/ src/ docs/

# Example output:
# specs/001-auth-spec/spec.md:15:SPEC:AUTH-001
# tests/unit/test_auth.py:2:TEST:AUTH-001
# src/auth/service.py:2:CODE:AUTH-001
# docs/api/AUTH-001.md:1:DOC:AUTH-001
```

**Extract TAG metadata**:
```python
import subprocess
import re

def scan_tags(cwd: str) -> list[dict]:
    """
    Scans codebase for TAG blocks and extracts metadata.

    Returns:
        List of TAG metadata dictionaries
    """
    result = subprocess.run(
        ["rg", "@(SPEC|TEST|CODE|DOC):", "-n", "-A", "5"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )

    tags = []
    for line in result.stdout.split("\n"):
        # Parse TAG ID
        match = re.search(r"@(SPEC|TEST|CODE|DOC):([A-Z]+-[0-9]+)", line)
        if match:
            tag_type, tag_id = match.groups()
            tags.append({
                "type": tag_type,
                "id": tag_id,
                "file": line.split(":")[0],
                "line": int(line.split(":")[1]),
            })

    return tags
```

### API Documentation Generation

**Generate API docs from TAG-annotated code**:

```python
def generate_api_doc(tag_id: str, code_file: str, cwd: str) -> str:
    """
    Generates API documentation for a TAG ID.

    Args:
        tag_id: TAG ID (e.g., AUTH-001)
        code_file: Path to code file
        cwd: Working directory

    Returns:
        Markdown documentation content
    """
    # Read code file
    with open(f"{cwd}/{code_file}", "r") as f:
        content = f.read()

    # Extract function signatures and docstrings
    functions = extract_functions(content)

    # Generate Markdown
    doc = f"# @DOC:{tag_id} - API Documentation\n\n"
    doc += f"@CODE: {code_file}\n\n"

    for func in functions:
        doc += f"## {func['name']}\n\n"
        doc += f"**Signature**: `{func['signature']}`\n\n"
        if func['docstring']:
            doc += f"{func['docstring']}\n\n"

    return doc
```

**Example output** (docs/api/AUTH-001.md):
```markdown
# @DOC:AUTH-001 - API Documentation

@CODE: src/auth/service.py
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py

## authenticate_user

**Signature**: `def authenticate_user(email: str, password: str) -> AuthResult`

Authenticates user with email and password.

**Args**:
- email (str): User email address
- password (str): User password

**Returns**:
- AuthResult: Authentication result with success status and optional token

**Raises**:
- ValueError: If email or password is empty
```

### Dev Daily Log Sync

**Append Git diff summary to dev daily log**:

```python
from datetime import date

def sync_dev_daily(git_diff: str, cwd: str) -> str:
    """
    Updates dev daily log with Git diff summary.

    Args:
        git_diff: Git diff output
        cwd: Working directory

    Returns:
        Updated dev daily log content
    """
    today = date.today().strftime("%Y-%m-%d")
    summary = summarize_git_diff(git_diff)

    log_entry = f"""
## {today}

### Changes Made
{summary}

### TAG Chain Updates
{scan_tag_chains(cwd)}

---
"""

    # Append to dev_daily.md
    with open(f"{cwd}/docs/dev_daily.md", "a") as f:
        f.write(log_entry)

    return log_entry
```

**Example output** (docs/dev_daily.md):
```markdown
## 2025-10-26

### Changes Made
- Implemented AUTH-001: User authentication service
- Added tests for authentication flow
- Updated API documentation

### TAG Chain Updates
- ✅ Complete: AUTH-001 (@SPEC → @TEST → @CODE → @DOC)
- ⚠️ Incomplete: AUTH-002 (@SPEC → @TEST, missing @CODE)

---
```

### README Synchronization

**Update README with current project status**:

```python
def sync_readme(major_changes: bool, cwd: str) -> str:
    """
    Updates README if major changes detected.

    Args:
        major_changes: Whether major changes occurred
        cwd: Working directory

    Returns:
        Updated README content
    """
    if not major_changes:
        return None  # Skip update for minor changes

    # Read current README
    with open(f"{cwd}/README.md", "r") as f:
        readme = f.read()

    # Update project status section
    status = get_project_status(cwd)
    updated_readme = update_section(readme, "Project Status", status)

    # Update installation/usage if needed
    # ...

    return updated_readme
```

### TAG Chain Validation

**Validate complete TAG chains**:

```python
def validate_tag_chains(cwd: str) -> dict:
    """
    Validates TAG chain completeness (SPEC → TEST → CODE → DOC).

    Returns:
        Validation report with integrity score
    """
    tags = scan_tags(cwd)

    # Group by TAG ID
    tag_groups = {}
    for tag in tags:
        tag_id = tag["id"]
        if tag_id not in tag_groups:
            tag_groups[tag_id] = {"SPEC": False, "TEST": False, "CODE": False, "DOC": False}
        tag_groups[tag_id][tag["type"]] = True

    # Calculate integrity
    complete_chains = 0
    orphaned_tags = []

    for tag_id, chain in tag_groups.items():
        # Complete chain requires SPEC + TEST + CODE (DOC optional)
        if chain["SPEC"] and chain["TEST"] and chain["CODE"]:
            complete_chains += 1
        else:
            orphaned_tags.append({
                "id": tag_id,
                "chain": chain,
                "missing": [k for k, v in chain.items() if not v and k != "DOC"]
            })

    total_chains = len(tag_groups)
    integrity_score = (complete_chains / total_chains * 100) if total_chains > 0 else 0

    return {
        "total_chains": total_chains,
        "complete_chains": complete_chains,
        "integrity_score": integrity_score,
        "orphaned_tags": orphaned_tags,
    }
```

**Example report**:
```json
{
  "total_chains": 15,
  "complete_chains": 13,
  "integrity_score": 86.7,
  "orphaned_tags": [
    {
      "id": "AUTH-002",
      "chain": {"SPEC": true, "TEST": true, "CODE": false, "DOC": false},
      "missing": ["CODE"]
    },
    {
      "id": "HOOKS-005",
      "chain": {"SPEC": true, "TEST": false, "CODE": true, "DOC": false},
      "missing": ["TEST"]
    }
  ]
}
```

## Inputs
- Codebase directory (specs/, tests/, src/, docs/)
- Git diff output (for dev daily sync)
- Document type flag (api, dev, readme, all)
- Staged changes flag (sync only staged files, or all files)

## Outputs
- Generated API documentation (docs/api/*.md)
- Updated dev daily log (docs/dev_daily.md)
- Updated README (if major changes)
- TAG chain validation report (JSON)
- Sync summary (files updated, TAG integrity score, duration)

## Example Usage Scenarios

### Scenario 1: Sync API Docs After Implementation

```bash
# After implementing AUTH-001
/ms.up-docs --docs=api

# System execution:
# 1. Scan code for @CODE:AUTH-001
# 2. Extract function signatures and docstrings
# 3. Generate docs/api/AUTH-001.md
# 4. Validate TAG chain (SPEC → TEST → CODE → DOC)
# 5. Report sync status
```

**Output**:
```json
{
  "files_updated": ["docs/api/AUTH-001.md"],
  "tag_integrity": 100.0,
  "duration_seconds": 3.2
}
```

### Scenario 2: Update Dev Daily Before Commit

```bash
# Before committing changes
/ms.up-docs --docs=dev

# System execution:
# 1. Run git diff HEAD~1 --name-only
# 2. Summarize changes (AI-generated summary)
# 3. Scan TAG chains for updates
# 4. Append to docs/dev_daily.md
# 5. Report sync status
```

**Output** (appended to docs/dev_daily.md):
```markdown
## 2025-10-26

### Changes Made
- Implemented SessionStart hook (HOOKS-001)
- Added project status display functionality
- Tests: 18/18 passing

### TAG Chain Updates
- ✅ Complete: HOOKS-001 (@SPEC → @TEST → @CODE)

---
```

### Scenario 3: Sync All Docs (Full Update)

```bash
# Full documentation sync
/ms.up-docs --all

# System execution:
# 1. Sync API docs (scan all @CODE tags)
# 2. Update dev daily (append latest changes)
# 3. Update README (if major changes detected)
# 4. Validate all TAG chains
# 5. Generate comprehensive sync report
```

**Output**:
```json
{
  "files_updated": [
    "docs/api/AUTH-001.md",
    "docs/api/HOOKS-001.md",
    "docs/dev_daily.md",
    "README.md"
  ],
  "tag_integrity": 93.3,
  "duration_seconds": 12.5
}
```

### Scenario 4: Staged Changes Only (Default)

```bash
# Sync only staged changes (default behavior)
git add src/auth/service.py tests/unit/test_auth.py
/ms.up-docs

# System execution:
# 1. Run git diff --cached (staged files only)
# 2. Scan TAGs in staged files only
# 3. Update docs for affected TAGs
# 4. Report sync status
```

**Output**:
```json
{
  "files_updated": ["docs/api/AUTH-001.md"],
  "staged_files": ["src/auth/service.py", "tests/unit/test_auth.py"],
  "tag_integrity": 100.0,
  "duration_seconds": 2.1
}
```

## Integration with /fin and /finq

**Automatic doc sync before commit**:

### /fin Workflow (with CI)
```bash
/fin

# Execution order:
# 1. /ms.up-docs --docs=dev  ← Auto-sync dev daily
# 2. make ci                  ← Run tests, linters
# 3. git add .                ← Stage all changes
# 4. git commit -m "..."      ← Commit with TAG references
# 5. git push                 ← Push to remote
```

### /finq Workflow (skip CI)
```bash
/finq

# Execution order:
# 1. /ms.up-docs --docs=dev  ← Auto-sync dev daily
# 2. git add .                ← Stage all changes
# 3. git commit -m "..."      ← Commit with TAG references
# 4. git push                 ← Push to remote
```

## Performance Optimization

**Target**: Complete doc sync in <10 minutes (even for large codebases)

**Strategies**:
1. **Parallel operations**: Scan TAGs and generate docs concurrently
2. **Incremental updates**: Only update docs for changed TAGs
3. **Caching**: Cache TAG scan results (invalidate on code changes)
4. **Batch processing**: Process multiple TAG IDs in single ripgrep scan

**Implementation**:
```python
from concurrent.futures import ThreadPoolExecutor

def sync_docs_parallel(tag_ids: list[str], cwd: str) -> list[str]:
    """Generates API docs in parallel."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(generate_api_doc, tag_id, cwd)
            for tag_id in tag_ids
        ]
        return [f.result() for f in futures]
```

## Error Handling (Fail-open)

**Principle**: Documentation sync failures should NOT block commits

**Implementation**:
```python
def sync_with_failopen(cwd: str) -> dict:
    """Syncs docs with fail-open error handling."""
    try:
        result = sync_all_docs(cwd)
        return result
    except Exception as e:
        logger.error(f"Doc sync failed: {e}")
        # Return partial result, allow commit to proceed
        return {
            "status": "PARTIAL",
            "error": str(e),
            "files_updated": [],
        }
```

## Related Skills
- `ms-workflow-tag-manager`: TAG block generation and templates
- `ms-foundation-trust`: TAG chain validation (Trackable principle)
- `moai-alfred-tag-scanning`: TAG scanning and inventory
- `moai-foundation-specs`: SPEC metadata and validation

---
description: "Synchronizes Documents"
argument-hint: "[changed feature or docs scope]"
---

# /ms.up-docs - Universal Document Synchronization

Synchronizes Living Documents with code changes based on Git staging area or specific document types.

## Overview

This command performs **document synchronization** with 3 modes:
1. **Staged changes** (default): Sync docs for files in `git diff --cached`
2. **Specific doc type**: Sync only API, dev daily, or README docs
3. **Full sync**: Sync all documents (`--all` flag)

## Usage

```bash
# Sync docs for staged changes (default)
/ms.up-docs

# Sync specific document types
/ms.up-docs --docs=api       # API documentation only
/ms.up-docs --docs=dev       # Developer daily log only
/ms.up-docs --docs=readme    # README.md only

# Full synchronization (all docs)
/ms.up-docs --all

# Skip TAG validation
/ms.up-docs --skip-tags
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--docs=<type>` | Sync specific doc type (`api`, `dev`, `readme`) | None (staged changes) |
| `--all` | Sync all documents (ignore staging) | False |
| `--skip-tags` | Skip TAG traceability warnings | False |

## Execution Steps

### Step 0: Load Constitution Context

**Auto-load project documents**:
- `.specify/memory/constitution.md` (Constitution - REQUIRED)
- `AGENTS.md` (AI instructions - if exists)

**Session read policy**: per AGENTS.md §2 — reuse files already read this session; a fresh `Read` immediately before `Edit`/`Write` is still required.

**Reference key sections**:
- Constitution Section V (TAGS: Best-Effort Traceability)
- TAG system requirements and traceability standards

### Step 1: Analyze Sync Scope

**Parse arguments**:
```
IF --docs=<type> provided:
  → Sync only specified doc type
ELSE IF --all flag provided:
  → Sync all documents
ELSE:
  → Sync docs for staged changes only (git diff --cached)
```

**Check Git staging area** (default mode):
```bash
# Get staged files
git diff --cached --name-only

# If empty and no --all flag:
⚠️ No staged changes found.

Use 'git add <files>' first or run '/ms.up-docs --all' to sync all docs.

EXIT: Code 0
```

**Determine affected docs**:
- Staged `.py` files → API docs
- Staged code files → TAG traceability warnings
- Implementation changes → dev_daily.md update
- Major features → README.md update

### Step 2: Execute Document Synchronization

**For each document type**, perform sync operations:

#### API Documentation Sync (`--docs=api`)

**Goal**: Extract function/class signatures and generate API docs

**Process**:
1. Scan for TAG blocks in code files:
   ```bash
   rg '@CODE:([A-Z]+-[0-9]+)' -n src backend frontend app lib packages --only-matching 2>/dev/null
   ```

2. For each TAG, extract:
   - Function signature
   - Docstring/JSDoc
   - Parameters and return types
   - Examples (if present)

3. Generate/update `docs/api/{TAG_ID}.md`:
   ```markdown
   # {TAG_ID}: {Function Name}

   **Location**: {file_path:line_number}
   **SPEC**: {spec_path}
   **TEST**: {test_path}

   ## Signature
   ```{language}
   {function_signature}
   ```

   ## Description
   {docstring}

   ## Parameters
   {parameters_list}

   ## Returns
   {return_type_and_description}

   ## Examples
   {code_examples}

   ## TAG Chain
   @SPEC:{TAG_ID} -> @TEST:{TAG_ID} -> @CODE:{TAG_ID}
   ```

**Output**: List of updated API doc files

#### Dev Daily Log Sync (`--docs=dev`)

**Goal**: Append a summary of the **outgoing** work to the developer daily log

**Process**:
1. Get the outgoing diff — staged + uncommitted + unpushed commits, i.e. the work
   this publish run is about (NOT `HEAD~1`, which describes the previous commit):
   ```bash
   BASE=$(git rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null || echo origin/master)
   git diff --stat "$BASE"...HEAD   # unpushed commits (e.g. the /ms.fix track)
   git diff --stat HEAD             # staged + uncommitted work
   git log --format='%h %s' "$BASE"..HEAD
   ```
   If the repo has no upstream yet, fall back to `git diff --stat HEAD` alone.

2. Summarize changes:
   - Files modified (added/changed/deleted lines)
   - Unpushed commit messages (if any)
   - TAG IDs affected

3. Append to `docs/dev_daily.md`:
   ```markdown
   ## {YYYY-MM-DD HH:MM}

   **Commit**: {commit_hash} - {commit_message}

   **Changes**:
   - {file1}: +{additions} -{deletions}
   - {file2}: +{additions} -{deletions}

   **TAGs Updated**: {TAG_IDs}

   **Summary**: {AI-generated summary of changes}

   ---
   ```

**Output**: dev_daily.md updated with timestamp

#### README Sync (`--docs=readme`)

**Goal**: Update README.md with project status and features

**Process**:
1. Scan for completed features:
   - Check `docs/prd/feature-map.progress.md` for `✅ shipped` rows — the actual
     completion source (no step ever writes `status: completed` into spec.md;
     2026-07-18 audit #32). Fall back to counting `specs/` directories when the
     ledger is absent.
   - Count total vs shipped Features

2. Update README sections:
   - **Project Status**: Features completed, test coverage, TAG integrity
   - **Features**: List of implemented features from spec.md files
   - **Installation**: Sync dependencies from pyproject.toml/package.json
   - **Usage**: Extract examples from tests

3. Preserve manual content:
   - Use `<!-- AUTO-GENERATED:START -->` and `<!-- AUTO-GENERATED:END -->` markers
   - Only update content within markers

**Output**: README.md updated

### Step 3: Report TAG Traceability (unless --skip-tags)

**Scan TAG system**:
```bash
# Find all TAGs
rg '@(SPEC|TEST|CODE|DOC):([A-Z]+-[0-9]+)' -n

# Report warnings:
# - duplicate @SPEC declarations
# - @CODE/@TEST without any @SPEC
# - broken CHAIN references
```

**TAG policy**:
- TAG integrity is best-effort by default.
- `@DOC` anchors are retired: tolerate them in legacy files, never require or
  write them.
- Multiple `@TEST:ID` occurrences are allowed for multi-file work; `@CODE:ID`
  anchors are unique per id (secondary files restate the chain on a `@CHAIN:` line
  — Constitution Section V, enforced by the pre-commit backstop).
- Do not block documentation sync on TAG warnings unless the active Constitution
  Section IX or CI explicitly promotes TAG integrity to blocking.

**Output**: TAG warning summary and traceability percentage when calculable.

### Step 4: Generate Sync Report

**Format**:
```json
{
  "sync_mode": "staged|api|dev|readme|all",
  "files_updated": [
    "docs/api/AUTH-001.md",
    "docs/dev_daily.md"
  ],
  "tag_integrity": {
    "total_tags": 25,
    "linked_tags": 23,
    "tag_warnings": 2,
    "traceability_score": 92.0
  },
  "duration_seconds": 8.5,
  "warnings": [
    "Orphan TAG: @CODE:PAY-003 (no @SPEC found)"
  ]
}
```

**Display**:
```
✅ Document sync complete

📦 Files Updated:
- docs/api/AUTH-001.md (created)
- docs/api/USER-002.md (updated)
- docs/dev_daily.md (appended)

📋 TAG Traceability: 92.0% (23/25 linked tags; warnings reported)
⚠️  Warnings:
- Orphan TAG: @CODE:PAY-003 (no @SPEC found)

⏱️ Duration: 8.5 seconds

🎯 Next Steps:
1. Review updated docs in docs/ directory
2. Fix orphan TAGs if needed
3. Publish via /ms.fin (it stages and commits by logical concern — do not make a separate docs-only commit when a fin run is next)
```

## Error Handling

### Error 1: No Git Repository

**Symptom**: Not a git repository

**Message**:
```
❌ Error: Not a git repository

/ms.up-docs requires a git repository to determine changes.

Please run 'git init' first.
```

**Exit**: Code 1

### Error 2: No Changes to Sync

**Symptom**: No staged changes and no --all flag

**Message**:
```
⚠️ No staged changes found.

Use 'git add <files>' first or run '/ms.up-docs --all' to sync all docs.
```

**Exit**: Code 0 (success - nothing to do)

### Error 3: Invalid Doc Type

**Symptom**: `--docs=invalid`

**Message**:
```
❌ Error: Invalid document type 'invalid'

Valid options: api, dev, readme

Example: /ms.up-docs --docs=api
```

**Exit**: Code 1

### Error 4: TAG Integrity Low

**Symptom**: TAG traceability has many warnings

**Message**:
```
⚠️ Warning: TAG traceability warning rate is high

15/23 TAGs have traceability warnings.

Recommendation: Run '/ms.review' to include TAG findings in the post-implementation review.

Continue anyway? (sync completed; TAG findings are warnings unless promoted by Section IX or CI)
```

**Exit**: Code 0 (warning, not error)

## Integration with SPECTER Workflow

**Called by**:
- `/ms.fin` command (before commit)
- Manual invocation when docs need sync

**Workflow position**:
```
/ms.featuremap → /ms.codex-checklist → /ms.verify → /ms.constitution → /ms.checklist → /ms.agent-verify → /ms.specify → /ms.clarify → /ms.plan → /ms.tasks → /ms.analyze → /ms.implement → /ms.review → [/ms.up-docs] → /ms.fin
                                                              ↑
                                                      (optional, but recommended)
```

**Best practices**:
1. Run `/ms.up-docs` after implementing features
2. Review docs before running `/ms.fin`
3. Use `--docs=api` for API-only updates
4. Use `--docs=dev` for daily log updates
5. Use `--all` for comprehensive sync before releases

## Document Structure

**SPECTER document tree**:
```
docs/
├── api/               # API documentation (auto-generated from @CODE TAGs)
│   ├── AUTH-001.md
│   ├── USER-002.md
│   └── ...
├── dev_daily.md       # Developer daily log (append-only)
├── architecture.md    # System architecture (manual + auto-sections)
└── guides/            # User guides (mostly manual)

README.md              # Project overview (auto-sections + manual)
CHANGELOG.md           # Change history (manual — no command updates it automatically)
```

**Auto-generated markers**:
```markdown
<!-- AUTO-GENERATED:START - DO NOT EDIT MANUALLY -->
{auto-generated content}
<!-- AUTO-GENERATED:END -->
```

## Constitution Compliance

**TRUST 5 Principles**:
- **Trackable**: Best-effort TAG validation tracks traceability
- **Readable**: Generated docs follow markdown standards
- **Unified**: Consistent doc structure across all APIs
- **Secured**: No sensitive data in auto-generated docs
- **Test-First**: Links tests to docs via @TEST TAGs

**File Size**:
- Each API doc ≤500 lines (split if larger)
- Generated content follows SPECTER formatting standards

## Performance

**Target**: Complete sync in <10 minutes

**Optimization strategies**:
1. **Staged changes mode**: Only sync affected docs (fast)
2. **Parallel processing**: Sync API docs concurrently (if >10 TAGs)
3. **Incremental updates**: Modify existing files, don't regenerate
4. **Caching**: Cache TAG scan results for duration of command

**Performance metrics**:
- Staged changes: <30 seconds (typical)
- API docs (10 TAGs): ~2 minutes
- Full sync (`--all`): <10 minutes (100 TAGs)

## Notes

- **Fail-open**: Continues even if some docs fail to sync (logs warnings)
- **Git-aware**: Respects .gitignore and doesn't sync ignored files

## Implementation Details

**Tools**: Read, Write, Edit, Bash, Grep, Glob

**Key operations**:
1. Git status/diff analysis
2. TAG extraction via ripgrep
3. Markdown generation
4. File write/update
5. TAG traceability warnings

## References

- SPECTER TAGS: `.specify/memory/constitution.md` Section V
- TAG chain rules: `/ms.implement` Step 3 and `scripts/specter/check_tag_chain.py`
- Document standards: `AGENTS.md` Section 2 (Documentation Updates)

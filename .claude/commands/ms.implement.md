---
description: "Implement feature with TAG blocks"
---

# /ms.implement - Implementation with Traceability

Implements features with automatic TAG selection and TAG block insertion.

## Overview

This command performs a **3-step process**:

1. **TAG Auto-Selection**: Scans tasks.md for first uncompleted TAG
2. **Implementation**: Runs `/speckit.implement` to generate code and tests
3. **TAG Block Insertion**: Auto-inserts traceability metadata in generated files

## Usage

```
/ms.implement
```

**No arguments required** - TAG is auto-selected from tasks.md.

**Manual TAG specification** (optional):

```
/ms.implement {TAG_ID}
```

Example:

```
/ms.implement AUTH-001
```

## Execution Steps

### Step 0: Load Project Context

**Auto-load project documents**:
- `.specify/memory/constitution.md` (Constitution - REQUIRED)
- `AGENTS.md` (AI instructions, coding standards - if exists)
- `specs/[spec-id]/spec.md` (Feature specification - REQUIRED)
- `specs/[spec-id]/plan.md` (Implementation plan - REQUIRED)
- `specs/[spec-id]/tasks.md` (Task list with TAG IDs - REQUIRED)

**IF Constitution, spec.md, plan.md, or tasks.md missing**:
- Display error: "Required files missing. Run `/ms.init`, `/ms.specify`, `/ms.plan`, and `/ms.tasks` first."
- Exit

**Reference key sections**:
- Constitution Section II (Simplicity-First Architecture - Files ≤500 SLOC, Functions ≤100 LOC)
- Constitution Section V (TRUST 5 Principles - Test-First, Readable, Unified, Secured, Trackable)
- Constitution Section IX (Project-specific constraints - **if exists**, added by `/ms.constitution`)
- AGENTS.md (coding standards, patterns to follow - if exists)

**These documents MUST guide implementation to ensure code quality and consistency.**

### Step 1: TAG Auto-Selection

**IF no TAG_ID provided as argument**:

1. Read `tasks.md`
2. Scan for uncompleted tasks: `[ ]` checkboxes
3. Extract TAG ID from first uncompleted task's `**TAG**:` line
4. Use format: `@SPEC:{TAG_ID} → @TEST:{TAG_ID} → @CODE:{TAG_ID}`

**Example**:

```markdown
## Phase 3: FR-1 Authentication

**TAG**: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001

### Implementation

-   [ ] T015 Create auth service ← First uncompleted task
-   [x] T014 Setup database
```

**Selected TAG**: `AUTH-001`

**IF TAG_ID provided as argument**:

-   Use provided TAG_ID directly
-   Skip auto-selection

**IF no uncompleted tasks found**:

```
✅ All tasks completed!

No pending TAGs found in tasks.md.
All implementation tasks are complete.
```

**EXIT**: Code 0

### Step 1.5: Context7 MCP - Latest Library Documentation (If Needed)

**⚠️ CRITICAL: Library research MUST be delegated to Gemini CLI**
- Use `mcp__cli-bridge__gemini_cli` tool
- Gemini processes documentation faster than Claude
- Claude Code orchestrates, Gemini executes

**Analyze task**: Does implementation require external libraries?

**Detection indicators**:
- Task mentions library names (FastAPI, React, Stripe, etc.)
- Integration with external services
- New third-party dependencies

**IF external library detected**:

  1. **Identify library and needed features**
  2. **Delegate to Gemini via MCP cli-bridge (background execution)**:
     ```python
     # Launch Gemini library research in background
     task_id = mcp__cli-bridge__gemini_cli(
         prompt="""Research latest API documentation for:
         - Library: fastapi
         - Topic: background tasks
         - Use Context7 MCP tools
         - Return: API usage examples and best practices
         """,
         background=True  # Returns immediately
     )

     # Claude continues with other work while Gemini researches
     # ... (e.g., read spec.md, plan.md, etc.)

     # Retrieve results when needed for implementation
     library_docs = mcp__cli-bridge__get_task_result(
         task_id=task_id,
         wait=True  # Block until completion
     )
     ```
  3. **Use latest API in implementation** (based on Gemini's research)

**ELSE**:
  → Skip (no external libraries)

**Store library docs** for use in Step 2 implementation.

### Step 2: Inject Constitution & Run Implementation

Before executing `/speckit.implement`, provide AI with Constitution constraints:

```
You are implementing code that MUST follow the project Constitution.

**Constitution**: .specify/memory/constitution.md

**CRITICAL: Read and apply these sections**:

**Section II - Simplicity-First (MANDATORY)**:
- Files ≤500 SLOC (code files only - split if larger)
- Functions ≤100 lines (extract helper functions if needed)
- Complexity ≤10 per function
- Prefer built-in tools over external dependencies

**Section V - TRUST 5 Principles (MANDATORY)**:
- **Test-First**: Write tests BEFORE implementation code
- **Readable**: Clear naming, ≤5 parameters per function, ≤4 nesting levels
- **Unified**: Strict typing (TypeScript strict mode, Python type hints)
- **Secured**: Input validation, environment variables for secrets
- **Trackable**: Code structure mirrors spec.md organization

**Refer to Constitution for detailed constraints and examples.**

Now implement TAG: {TAG_ID}
```

Execute `/speckit.implement {TAG_ID}` with Constitution-enhanced context.

This generates the core implementation files (code, tests) following Constitution principles.

### Step 3: Insert TAG Blocks

Locate generated files and insert TAG metadata.

#### 3.1 Scan Generated Files

Scan for newly created files:

-   **Code files**: `src/**/*.{ts,py}`
-   **Test files**: `tests/**/*.{ts,py}`
-   **Spec file**: From tasks.md TAG chain

#### 3.2 Insert TAG Blocks

Generate TAG blocks for each file:

```bash
generate_tag_block() {
  local lang="$1"
  local tag_id="$2"
  local spec_path="$3"
  local test_path="$4"
  local date=$(date +%Y-%m-%d)

  case "$lang" in
    ts|js|tsx|jsx)
      cat <<EOF
/**
 * @CODE:${tag_id}
 * @SPEC: ${spec_path}
 * @TEST: ${test_path}
 * @CHAIN: @SPEC:${tag_id} → @TEST:${tag_id} → @CODE:${tag_id}
 * @STATUS: implemented
 * @CREATED: ${date}
 * @UPDATED: ${date}
 */
EOF
      ;;
    py)
      cat <<EOF
"""
@CODE:${tag_id}
@SPEC: ${spec_path}
@TEST: ${test_path}
@CHAIN: @SPEC:${tag_id} → @TEST:${tag_id} → @CODE:${tag_id}
@STATUS: implemented
@CREATED: ${date}
@UPDATED: ${date}
"""
EOF
      ;;
  esac
}
```

For each generated file, insert TAG block at top using Edit tool.

### Step 3.5: Update CHANGELOG.md (Codex)

**⚠️ CRITICAL: CHANGELOG update MUST be delegated to Codex CLI**

After implementation is complete, update the project changelog with detailed change history.

**When to update**:
- New features added
- Existing functionality changed
- Bugs fixed
- Breaking changes introduced

**Delegate to Codex via MCP cli-bridge (background execution)**:

```python
# Analyze what was implemented
implemented_changes = """
- Files created: [list all new files]
- Files modified: [list all modified files]
- Features added: [describe new capabilities]
- Changes made: [describe modifications]
- Technical details: [function names, classes, patterns used]
- Rationale: [why these changes were made]
"""

# Update CHANGELOG via Codex (background execution)
changelog_task_id = mcp__cli-bridge__codex_cli(
    prompt=f"""Update docs/CHANGELOG.md with the following implementation:

{implemented_changes}

Requirements:
1. Follow Keep a Changelog format (https://keepachangelog.com/)
2. Add to [Unreleased] section
3. Use appropriate categories:
   - Added: New features
   - Changed: Changes to existing functionality
   - Deprecated: Soon-to-be removed features
   - Removed: Removed features
   - Fixed: Bug fixes
   - Security: Security improvements
4. Be specific and detailed:
   - Include file paths and function names
   - Explain WHAT changed and WHY
   - Note any breaking changes
5. Use technical language - this is for developers

Example format:
## [Unreleased] - {{date}}

### Added
- New `UserService.authenticate()` method in `src/auth/service.py`
  - Implements JWT-based authentication
  - Replaces legacy session-based auth for better scalability

### Changed
- Updated `DatabaseConnection` to use connection pooling
  - Improves performance under high load
  - Reduces connection overhead by 40%
""",
    background=True  # Returns immediately
)

# Claude continues with other tasks (e.g., TAG block insertion)
# Codex updates CHANGELOG independently in background

# Wait for CHANGELOG update completion before finishing
changelog_result = mcp__cli-bridge__get_task_result(
    task_id=changelog_task_id,
    wait=True
)
```

**CHANGELOG vs README difference**:
- **CHANGELOG**: Historical record of ALL changes (detailed, technical)
- **README**: Current state only (no change history, user-friendly)

### Step 4: Update tasks.md Checklist

**CRITICAL**: Mark completed tasks in tasks.md after successful implementation.

1. Read `specs/{SPEC_ID}/tasks.md`
2. Find tasks associated with current TAG_ID
3. Mark completed tasks with `[x]` checkbox
4. Save updated tasks.md

**Example**:

```markdown
## Phase 3: FR-1 Authentication

**TAG**: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001

### Implementation

-   [x] T015 Create auth service ← Mark as completed
-   [x] T016 Write auth tests ← Mark as completed
-   [ ] T017 Add API endpoint ← Next task
```

**This step is MANDATORY** - Without updating tasks.md, progress tracking breaks.

### Step 5: Report Output

Display summary:

```json
{
    "tag_selected": "AUTH-001",
    "auto_selected": true,
    "files_created": ["src/auth/service.ts", "tests/unit/auth.test.ts"],
    "tag_blocks_inserted": 2
}
```

Display next steps:

```
✅ Implementation completed for TAG: AUTH-001

📦 Files Created:
- src/auth/service.ts (with @CODE:AUTH-001 block)
- tests/unit/auth.test.ts (with @TEST:AUTH-001 block)

📋 Traceability:
@SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001

🎯 Next Steps:
1. Review generated code and tests
2. Run tests: npm test (or pytest)
3. **REQUIRED**: Update tasks.md checklist - mark completed tasks with [x]
4. Run `/ms.implement` again for next TAG
5. All TAG blocks auto-generated ✅
```

## TAG Block Format

**TypeScript**:

```typescript
/**
 * @CODE:AUTH-001
 * @SPEC: specs/001-auth-spec/spec.md
 * @TEST: tests/unit/auth.test.ts
 * @CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
 * @STATUS: implemented
 * @CREATED: 2025-10-09
 * @UPDATED: 2025-10-09
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
@CREATED: 2025-10-09
@UPDATED: 2025-10-09
"""
```

## Error Handling

### Error 1: No Tasks Found

**Symptom**: tasks.md doesn't exist or is empty

**Message**:

```
❌ Error: No tasks found

Expected: specs/{SPEC_ID}/tasks.md

Please run `/ms.tasks` first to generate implementation tasks.
```

**Exit**: Code 1

### Error 2: No Pending TAGs

**Symptom**: All tasks completed (all `[x]` checkboxes)

**Message**:

```
✅ All tasks completed!

No pending TAGs found in tasks.md.
All implementation is complete.
```

**Exit**: Code 0 (success)

### Error 3: TAG Not Found in tasks.md

**Symptom**: Manually specified TAG doesn't exist

**Message**:

```
❌ Error: TAG not found in tasks.md

Specified TAG: AUTH-001
Available TAGs: USER-001, PAY-001, CART-001

Please run `/ms.tasks` to verify TAG assignments or use `/ms.implement` without arguments for auto-selection.
```

**Exit**: Code 1

### Error 4: Implementation Failed

**Symptom**: `/speckit.implement` returned error

**Message**:

```
❌ Error: Implementation failed

The base `/speckit.implement` command encountered an error.
Please check the error message above and retry.
```

**Exit**: Code 1

## Next Steps

After `/ms.implement`:

1. Verify TAG blocks in generated files
2. Run tests to verify implementation
3. **REQUIRED**: Update tasks.md checklist - mark completed tasks with [x]
4. Run `/ms.implement` again to implement next TAG
5. Commit changes with TAG ID in commit message

## Notes

-   **Auto TAG selection**: No manual TAG specification needed (scans tasks.md)
-   **Manual TAG option**: Can specify TAG explicitly if needed
-   **Automatic TAG blocks**: Inserted in all generated files
-   **100% traceability**: SPEC→TEST→CODE chain complete

## Implementation Details

**Tools**: SlashCommand (/speckit.implement), Read, Edit, Write, Bash

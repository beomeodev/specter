---
description: "Implement feature with TAG blocks"
---

# /ms.implement - Implementation with Traceability

Implements features with automatic TAG selection and TAG block insertion.

## Overview

**This command is a wrapper around `/speckit.implement` with enhanced functionality.**

**Base Command**: `/speckit.implement` - TDD implementation (RED-GREEN-REFACTOR)

**Additional Features** (provided by `/ms.implement`):
- TAG auto-selection from tasks.md (first uncompleted task)
- Library documentation research via `library-researcher` agent (Haiku + Context7 MCP)
- TAG block insertion for traceability (@SPEC → @TEST → @CODE chains)
- Living Documentation sync via `doc-updater` agent (Haiku)
- tasks.md checklist auto-update

**Purpose**: Implements features with complete traceability and automatic documentation synchronization, ensuring each implementation has full TAG chain coverage and up-to-date docs.

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

### Step 1.5: Latest Library Documentation Research (If Needed)

**Analyze task**: Does implementation require external libraries?

**Detection indicators**:
- Task mentions library names (FastAPI, React, Stripe, etc.)
- Integration with external services
- New third-party dependencies

**IF external library detected**:

  1. **Identify library and needed features**
  2. **Launch library-researcher agent (background execution)**:
     ```python
     # Launch library research agent
     Task(
         subagent_type="library-researcher",
         description="Research library docs",
         prompt="""Research latest library documentation for: '$REQUIRED_LIBRARIES'

         Use Context7 MCP to fetch:
         - Latest API usage examples
         - Best practices from official docs
         - Version compatibility notes
         - Breaking changes

         Return: Libraries researched, API examples, best practices, compatibility notes"""
     )

     # Agent runs independently while Claude continues with other work
     # Results available when agent completes
     ```
  3. **Use latest API in implementation** (based on agent's research)

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

**Agent Delegation Strategy**:

`/speckit.implement` uses the **tdd-implementer** agent (Sonnet 3.5 model) for core TDD workflow:

**Primary Agent** (High-Value Work):
- **tdd-implementer** (Sonnet 3.5 model)
  - RED: Write failing tests first (test-driven approach)
  - GREEN: Implement minimum code to pass tests
  - REFACTOR: Improve code quality while keeping tests green
  - Auto-insert TAG blocks via `ms-workflow-tag-manager` skill
  - **WHY Sonnet**: TDD requires reasoning about test cases, edge cases, and refactoring strategies

**Supporting Agents** (Research & Documentation):
- **library-researcher** (Haiku 3.5) - Already completed in Step 1.5 if needed
- **doc-updater** (Haiku 3.5) - Will run in Step 3.5 for documentation sync

This generates the core implementation files (code, tests) following Constitution principles and TDD best practices.

### Step 3: Insert TAG Blocks

Locate generated files and insert TAG metadata.

#### 3.1 Scan Generated Files

Scan for newly created files:

-   **Code files**: `src/**/*.{ts,py}`, `backend/src/**/*.{ts,py}`, `frontend/src/**/*.{ts,py,vue}`
-   **Test files**: `tests/**/*.{ts,py}`, `backend/tests/**/*.{ts,py}`, `frontend/tests/**/*.{ts,py}`
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

### Step 3.5: Update Documentation (Living Docs)

**After implementation is complete**, update project documentation to reflect code changes.

**Documentation to update**:
- **dev_daily.md**: Append implementation summary with TAG IDs
- **API docs**: Auto-generate/update `docs/api/{TAG_ID}.md` if public APIs added
- **README.md**: Update if major feature completed (conditional)

**Use doc-updater agent** (delegated to `/ms.up-docs` internally):

```python
# Launch doc-updater agent for Living Documentation sync
Task(
    subagent_type="doc-updater",
    description="Sync Living Documents",
    prompt="""Update Living Documentation based on recent implementation:

    Changes:
    - Files created: {list all new files}
    - Files modified: {list all modified files}
    - TAG implemented: {TAG_ID}
    - Features added: {describe new capabilities}

    Tasks:
    1. Append to docs/dev_daily.md:
       - Implementation summary with TAG ID
       - Files changed and rationale
       - Current date/time

    2. Generate/update API docs (if public APIs added):
       - Create docs/api/{TAG_ID}.md
       - Extract function signatures and docstrings
       - Include TAG chain traceability

    3. Update README.md (if major feature):
       - Update feature list progress
       - Add to completed features section

    Follow CODE-FIRST principle:
    - Extract documentation from code comments/docstrings
    - Maintain TAG chain integrity
    - Use auto-generated markers to preserve manual content

    Return: List of docs updated, TAG integrity report"""
)

# Agent runs independently (Haiku model for speed)
# Results available when agent completes
```

**Documentation Principles** (from `doc-updater` agent):
- **CODE-FIRST**: Documentation generated from code, not maintained separately
- **Living Docs**: Real-time sync between code and documentation
- **TAG Traceability**: @SPEC → @TEST → @CODE → @DOC chain complete

**Notes**:
- **dev_daily.md**: Always updated (implementation log)
- **API docs**: Only if public APIs added/modified
- **README.md**: Only if major feature completed
- **CHANGELOG.md**: Manual updates only (not auto-generated)

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

-   **Wrapper Design**: `/ms.implement` wraps `/speckit.implement` and adds TAG + documentation features
-   **Multi-Agent Orchestration**: Coordinates tdd-implementer (Sonnet), library-researcher (Haiku), doc-updater (Haiku)
-   **Auto TAG selection**: No manual TAG specification needed (scans tasks.md)
-   **Manual TAG option**: Can specify TAG explicitly if needed
-   **Automatic TAG blocks**: Inserted in all generated files
-   **Living Documentation**: Auto-syncs code changes to docs via doc-updater agent
-   **100% traceability**: SPEC→TEST→CODE→DOC chain complete

## Implementation Details

**Architecture**: Wrapper pattern with feature enhancements

**Delegation**:
- **Core implementation** → `/speckit.implement` (TDD workflow with tdd-implementer agent)
- **Library research** → `library-researcher` agent (Context7 MCP, Haiku model)
- **Documentation sync** → `doc-updater` agent (Living Docs, Haiku model)
- **TAG block insertion** → `/ms.implement` (enhancement layer)

**Agent Usage**:
- **tdd-implementer** (Sonnet) - RED-GREEN-REFACTOR TDD cycle, core implementation
- **library-researcher** (Haiku) - Latest library docs via Context7 MCP
- **doc-updater** (Haiku) - Living Documentation synchronization

**Tools**:
- SlashCommand (`/speckit.implement`) - Delegates TDD implementation
- Task (launch agents: library-researcher, doc-updater)
- Read (tasks.md, spec.md) - TAG auto-selection and context
- Edit (generated files) - Insert TAG blocks
- Write (TAG metadata) - Create traceability chains
- Bash (ripgrep) - Scan for existing TAGs

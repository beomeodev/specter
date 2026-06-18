---
description: "Implement feature with TAG blocks"
---

# /ms.implement - Implementation with Traceability

Implements the next selected task scope with TAG block insertion.

## Overview

**This command is a wrapper around `/speckit.implement` with enhanced functionality.**

**Base Command**: `/speckit.implement` - TDD implementation (RED-GREEN-REFACTOR)

**Additional Features** (provided by `/ms.implement`):
- Scope selection from `tasks.md` with current phase as the default boundary
- Latest library documentation check when the implementation depends on current third-party APIs
- File-level TAG block insertion for best-effort traceability (`@SPEC -> @TEST -> @CODE`, `@DOC` optional)
- Documentation sync instructions via `/ms.up-docs` or direct doc updates
- `tasks.md` checklist update with read-back verification

**Purpose**: Implements the selected phase/task/TAG scope with best-effort TAG traceability, keeping implementation, tests, and docs easy to find without treating TAGS as a substitute for tests or review.

## Usage

```
/ms.implement [--mode={tdd|refactor}] [--task TNNN] [--to-end] [TAG_ID]
```

**No arguments required** - the command selects the first pending phase in `tasks.md` and targets that phase as the default implementation boundary.

**Refactor mode**:
```
/ms.implement --mode=refactor
```
*Note: In refactor mode, the narrative changes from RED-GREEN-REFACTOR to safety-net → swap → verify.*

**Scope controls** (optional):

```
/ms.implement --task T035      # single task only
/ms.implement --to-end         # all remaining tasks in tasks.md
/ms.implement AUTH-001         # all pending tasks for one TAG
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
- Constitution Section III (Test-First Implementation)
- Constitution Section IV (TRUST Review Model)
- Constitution Section V (TAGS: Best-Effort Traceability)
- Constitution Section VI (File, Architecture, And Tooling Governance - Files ≤700 SLOC, Functions ≤100 LOC)
- Constitution Section IX (Project-specific baseline established from the checked PRD Feature Map by `/ms.constitution`)
- AGENTS.md (coding standards, patterns to follow - if exists)

**These documents MUST guide implementation to ensure code quality and consistency.**

### Step 1: Scope and TAG Selection

Read `tasks.md` and select an implementation boundary before coding.

**Default behavior**:
1. Find the first phase or phase-part that contains unchecked `[ ]` tasks.
2. Target all unchecked tasks in that phase.
3. Extract every TAG chain referenced by those tasks.
4. Treat the selected phase as the next natural commit boundary.

**Explicit controls**:
- `--task TNNN`: implement only that task.
- `TAG_ID`: implement pending tasks for that TAG only.
- `--to-end`: implement all remaining unchecked tasks, only when the user clearly wants a long run.

**Example**:

```markdown
## Phase 3: FR-1 Authentication

**TAG**: @SPEC:AUTH-001 -> @TEST:AUTH-001 -> @CODE:AUTH-001

### Implementation

-   [ ] T015 Create auth service
-   [ ] T016 Write auth tests

## Phase 4: FR-2 Session Management

**TAG**: @SPEC:AUTH-002 -> @TEST:AUTH-002 -> @CODE:AUTH-002

-   [ ] T017 Create session service
```

Default selected scope: Phase 3 only, TAG `AUTH-001`.

**IF no uncompleted tasks found**:

```
✅ All tasks completed!

No pending tasks found in tasks.md.
All implementation tasks are complete.
Next step: /ms.review
```

**EXIT**: Code 0

### Step 1.5: Latest Library Documentation Research (If Needed)

**Analyze task**: Does implementation require external libraries?

**Detection indicators**:
- Task mentions library names (FastAPI, React, Stripe, etc.)
- Integration with external services
- New third-party dependencies

**IF external library detected**:

1. Identify the exact library, version constraints, and API surface needed.
2. Use available documentation tooling directly, preferring official docs or Context7 when available.
3. Record the relevant API facts in the implementation notes before coding.
4. If documentation cannot be verified and the API is unstable or high-risk, stop and surface the uncertainty instead of guessing.

**ELSE**:
  → Skip (no external libraries)

Do not claim that a `library-researcher` agent or a specific model ran unless it actually did.

### Step 2: Inject Constitution & Run Implementation

Before executing `/speckit.implement`, provide AI with Constitution constraints:

```
You are implementing code that MUST follow the project Constitution.

**Constitution**: .specify/memory/constitution.md

**CRITICAL: Read and apply these sections**:

**Section III - Test-First Implementation (MANDATORY)**:
- Define the behavior contract before coding
- Write or update the relevant test or verification case first
- Implement the smallest change that satisfies it

**Section VI - File, Architecture, And Tooling Governance (MANDATORY)**:
- Production files ≤700 SLOC; test files have no SLOC limit
- Functions target ≤100 LOC and complexity ≤10
- Prefer mature built-in/project tools over new custom implementations

**Section IV - TRUST Review Model (MANDATORY)**:
- **Test-First**: touched behavior has tests or verification cases
- **Readable**: clear naming, ≤5 parameters target, ≤4 nesting target
- **Unified**: strict typing and existing project patterns
- **Secured**: input validation, authorization checks, no secret leakage
- **Trackable**: TAGS are best-effort metadata, not a substitute for tests or review

**Change Discipline — Surgical (MANDATORY)**:
- Touch ONLY what this TAG/task requires. Every changed line traces to the task.
- Don't "improve" adjacent code, don't refactor what isn't broken, match existing style.
- Remove only orphans YOUR change created; mention (don't delete) unrelated dead code.
- (A planned refactor task is itself the request — stay surgical to that task's scope.)

**Goal-Driven**: the task's GEARS acceptance criteria are the success bar — write the test, then loop until it passes.

**Refer to Constitution Sections III, IV, V, VI, and AGENTS.md change discipline for details.**

Now implement selected scope: {SCOPE}
Selected TAGs: {TAG_IDS}
```

Execute `/speckit.implement` with Constitution-enhanced context and the selected scope.
When a single `TAG_ID` was provided, pass that TAG as the scope. Otherwise, pass
the selected phase/task list so implementation does not silently shrink back to
one task.

Implementation contract:
- In `tdd` mode: write or update the smallest relevant failing test/verification first, implement the minimum code, then refactor only inside the selected scope.
- In `refactor` mode: establish or identify the safety net first, make the mechanical or structural change, then run the relevant verification. Do not force an artificial RED when the work is audit-driven.
- Insert TAG blocks yourself in Step 3; do not rely on an automatic skill invocation.
- Keep the implementation within the selected phase/task/TAG boundary unless a blocker requires user-visible scope adjustment.

This generates or modifies the implementation files while following Constitution principles and existing project patterns.

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
  local target_path="${5:-}"

  # Determine tag type from the target file. Keep this file-level only.
  local tag_type="CODE"
  local normalized_path="${target_path//\\//}"
  local base_name="${normalized_path##*/}"
  if [[ "$normalized_path" == tests/* ]] || [[ "$normalized_path" == test/* ]] || [[ "$normalized_path" == */tests/* ]] || [[ "$normalized_path" == */test/* ]] || [[ "$normalized_path" == */__tests__/* ]] || [[ "$base_name" == *.test.* ]] || [[ "$base_name" == *.spec.* ]] || [[ "$base_name" == test_* ]] || [[ "$base_name" == *_test.* ]]; then
    tag_type="TEST"
  fi

  local date=$(date +%Y-%m-%d)
  # @UPDATED reflects git reality, not creation time. For an already-tracked
  # file use its last-commit date; for a new file it equals @CREATED (today).
  # A hand-stamped "today" on an unchanged file is a false Trackable signal.
  local updated="$date"
  if [ -n "$target_path" ]; then
    local git_date
    git_date=$(git log -1 --format=%cs -- "$target_path" 2>/dev/null)
    [ -n "$git_date" ] && updated="$git_date"
  fi

  case "$lang" in
    ts|js|tsx|jsx)
      cat <<EOF
/**
 * @${tag_type}:${tag_id}
 * @SPEC: ${spec_path}
 * @TEST: ${test_path}
 * @CHAIN: @SPEC:${tag_id} -> @TEST:${tag_id} -> @CODE:${tag_id}
 * @STATUS: implemented
 * @CREATED: ${date}
 * @UPDATED: ${updated}
 */
EOF
      ;;
    py)
      cat <<EOF
"""
@${tag_type}:${tag_id}
@SPEC: ${spec_path}
@TEST: ${test_path}
@CHAIN: @SPEC:${tag_id} -> @TEST:${tag_id} -> @CODE:${tag_id}
@STATUS: implemented
@CREATED: ${date}
@UPDATED: ${updated}
"""
EOF
      ;;
  esac
}
```

For each generated or meaningfully modified file, insert at most one file-level TAG block at the top using Edit tool. Use @CODE for implementation files and @TEST for test files. Multiple files may share the same TAG_ID. Do not add line-level @TEST tags inside individual test functions.

### Step 3.5: Update Documentation (Living Docs)

After implementation is complete, update documentation only where the code change
actually affects project knowledge.

**Documentation to update**:
- `docs/dev_daily.md`: append a concise implementation summary with TAG IDs when the project uses this log.
- API docs: create or update `docs/api/{TAG_ID}.md` only if public APIs were added or changed.
- `README.md`: update only for user-visible major feature completion.

Preferred path:
- Use `/ms.up-docs` after implementation when documentation changes are non-trivial.
- For small changes, update the exact affected docs directly.

Documentation principles:
- CODE-FIRST: derive docs from the implemented code and tests.
- Preserve manual content; use generated markers only where the repo already uses them.
- TAG traceability warnings are reported, not treated as implementation blockers unless Constitution Section IX or CI promotes them.
- Do not claim a `doc-updater` agent or a specific model ran unless it actually did.

### Step 4: Update tasks.md Checklist

**CRITICAL**: Mark completed tasks in tasks.md after successful implementation.

1. Read `specs/{SPEC_ID}/tasks.md`
2. Find every task in the selected scope
3. Mark only successfully completed tasks with `[x]` checkbox
4. Leave blocked or intentionally deferred tasks unchecked with a short note
5. Save updated tasks.md

**Example**:

```markdown
## Phase 3: FR-1 Authentication

**TAG**: @SPEC:AUTH-001 -> @TEST:AUTH-001 -> @CODE:AUTH-001

### Implementation

-   [x] T015 Create auth service ← Mark as completed
-   [x] T016 Write auth tests ← Mark as completed
-   [ ] T017 Add API endpoint ← Next task
```

**This step is MANDATORY** - Without updating tasks.md, progress tracking breaks.

#### Read-back verification (don't rely on "remembering")

After writing tasks.md, **re-read it and assert** every completed task in the
selected scope is now `[x]`. Progress lives only in these checkboxes and the next
run auto-selects the first pending scope. A missed checkoff silently repeats work.

```bash
# Fail loudly if any task that was reported complete is still unchecked after
# the update. Populate COMPLETED_TASK_IDS from the selected scope, e.g. T015 T016.
for task_id in ${COMPLETED_TASK_IDS}; do
  if grep -nE "^\s*-?\s*\[ \].*${task_id}\b" "specs/${SPEC_ID}/tasks.md"; then
    echo "❌ tasks.md read-back failed — ${task_id} is still [ ]."
    echo "   Fix the checkbox before reporting completion."
  fi
done
```

### Step 5: Report Output

Display summary:

```json
{
    "scope_selected": "Phase 3",
    "tags_selected": ["AUTH-001"],
    "auto_selected": true,
    "files_created": ["src/auth/service.ts", "tests/unit/auth.test.ts"],
    "tag_blocks_inserted": 2
}
```

Display next steps:

```
✅ Implementation completed for selected scope: Phase 3

📦 Files Created:
- src/auth/service.ts (with @CODE:AUTH-001 block)
- tests/unit/auth.test.ts (with @TEST:AUTH-001 block)

📋 Traceability:
@SPEC:AUTH-001 -> @TEST:AUTH-001 -> @CODE:AUTH-001

🎯 Next Steps:
1. Review generated code and tests
2. Confirm tasks.md was auto-updated and read-back verified
3. Run `/ms.implement` again for the next pending phase/task
4. When all tasks are complete, run `/ms.review` for code quality, Codex advisory review, and executable gates
```

## TAG Block Format

**TypeScript**:

```typescript
/**
 * @CODE:AUTH-001
 * @SPEC: specs/001-auth-spec/spec.md
 * @TEST: tests/unit/auth.test.ts
 * @CHAIN: @SPEC:AUTH-001 -> @TEST:AUTH-001 -> @CODE:AUTH-001
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
@CHAIN: @SPEC:AUTH-001 -> @TEST:AUTH-001 -> @CODE:AUTH-001
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

No pending tasks found in tasks.md.
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

1. Verify TAG blocks in generated files.
2. Verify tasks.md was marked complete by the command's mandatory read-back check.
3. Run `/ms.implement` again until no pending TAGs remain.
4. Run `/ms.review` before `/fin`; review owns Codex advisory review, tests, lint, typecheck, build, coverage, and TAG traceability reporting.

## Notes

-   **Wrapper Design**: `/ms.implement` wraps `/speckit.implement` and adds scope, TAG, checklist, and documentation discipline
-   **Default scope**: Current pending phase or phase-part, not a single isolated task
-   **Manual scope options**: `--task`, `TAG_ID`, and `--to-end` are available when needed
-   **TAG blocks**: Inserted as one file-level block in generated or meaningfully modified files
-   **Living Documentation**: Updated directly or via `/ms.up-docs` when the implementation changes project knowledge
-   **Best-effort traceability**: SPEC -> TEST -> CODE, with DOC optional and warnings reported

## Implementation Details

**Architecture**: Wrapper pattern with feature enhancements

**Execution responsibilities**:
- **Core implementation** → `/speckit.implement` with the selected scope and Constitution context
- **Library research** → direct documentation lookup when needed
- **Documentation sync** → direct doc edits or `/ms.up-docs`
- **TAG block insertion** → `/ms.implement` enhancement layer
- **Checklist progress** → update and re-read `tasks.md`

**Tools**:
- SlashCommand (`/speckit.implement`) - Runs scoped implementation
- Read (tasks.md, spec.md, plan.md) - Scope selection and context
- Edit (generated or touched files) - Insert TAG blocks and update docs/tasks
- Bash/ripgrep - Scan for TAGs, project patterns, and verification targets

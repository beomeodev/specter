---
description: "Implement feature with TAG anchors"
argument-hint: "[optional task IDs or guidance — defaults to first pending phase]"
---

# /ms.implement - Implementation with Traceability

Implements the next selected task scope with TAG anchor insertion.

## Overview

**This command is a wrapper around `/speckit-implement` with enhanced functionality.**

**Base Command**: `/speckit-implement` - TDD implementation (RED-GREEN-REFACTOR)

**Additional Features** (provided by `/ms.implement`):
- Scope selection from `tasks.md` with current phase as the default boundary
- Latest library documentation check when the implementation depends on current third-party APIs
- File-level TAG anchor insertion for best-effort traceability (`@SPEC -> @TEST -> @CODE`)
- Documentation sync instructions via `/ms.up-docs` or direct doc updates
- `tasks.md` checklist update with read-back verification

**Purpose**: Implements the selected phase/task/TAG scope with best-effort TAG traceability, keeping implementation, tests, and docs easy to find without treating TAGS as a substitute for tests or review.

## Usage

```
/ms.implement [--mode={tdd|refactor}] [--task TNNN] [--to-end] [--pbt] [TAG_ID]
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

**Property-based testing** (opt-in, decided 2026-07-07):

```
/ms.implement --pbt            # also derive property-based tests from GEARS criteria
```

With `--pbt`, invariant-shaped GEARS acceptance criteria additionally get property-based
tests (Hypothesis for Python, fast-check for TypeScript) during the TDD RED step — see the
implementation contract in Step 2. Without the flag, behavior is unchanged.

## Execution Steps

### Step 0: Load Project Context

**Auto-load project documents**:
- `.specify/memory/constitution.md` (Constitution - REQUIRED)
- `AGENTS.md` (AI instructions, coding standards - if exists)
- `specs/[spec-id]/spec.md` (Feature specification - REQUIRED)
- `specs/[spec-id]/plan.md` (Implementation plan - REQUIRED)
- `specs/[spec-id]/tasks.md` (Task list with TAG IDs - REQUIRED)

**Session read policy**: per AGENTS.md §2 — reuse files already read this session; a fresh `Read` immediately before `Edit`/`Write` is still required.

**Open the stop-gate phase** (mechanical turn-end gate; installed by `/ms.init` Step 2.7b):

```bash
[ -x .specify/scripts/bash/specter-stop-gate.sh ] && .specify/scripts/bash/specter-stop-gate.sh phase implement
```

Skip silently if the script does not exist (project initialized before Step 2.7b existed).

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

**TAG**: @SPEC:AUTH-001

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
2. Use available documentation tooling directly, preferring official docs.
3. Record the relevant API facts in the implementation notes before coding.
4. If documentation cannot be verified and the API is unstable or high-risk, stop and surface the uncertainty instead of guessing.

**ELSE**:
  → Skip (no external libraries)

Do not claim that a specific agent or model ran unless it actually did.

### Step 1.6: Design Baseline (UI Features Only)

**Analyze task**: Does this Feature's `### In scope` include a web UI surface (a page, component
tree, or dashboard)?

**IF a UI surface is in scope AND `docs/design/DESIGN.md` does not exist yet**:

1. Use the `ms-design-baseline` skill to generate `docs/design/DESIGN.md` + `tokens.css` +
   `base.css` before writing any markup/component code.
2. All UI code in this Feature reads the generated tokens; do not hardcode a color, font size, or
   spacing value that isn't already a semantic token.

**ELSE IF a UI surface is in scope AND `docs/design/DESIGN.md` already exists**:
  → Read it and reuse its tokens; do not regenerate or introduce a second design source.

**ELSE**:
  → Skip (no UI surface in this Feature)

### Step 2: Inject Constitution & Run Implementation

Before executing `/speckit-implement`, provide AI with Constitution constraints:

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

Execute `/speckit-implement` with Constitution-enhanced context and the selected scope.
When a single `TAG_ID` was provided, pass that TAG as the scope. Otherwise, pass
the selected phase/task list so implementation does not silently shrink back to
one task.

Implementation contract:
- In `tdd` mode: write or update the smallest relevant failing test/verification first, implement the minimum code, then refactor only inside the selected scope.
- In `refactor` mode: establish or identify the safety net first, make the mechanical or structural change, then run the relevant verification. Do not force an artificial RED when the work is audit-driven.
- **With `--pbt`** (property-based testing from GEARS; opt-in): during the RED step, classify
  each in-scope GEARS acceptance criterion. A criterion is **invariant-shaped** when it
  quantifies over an input class rather than an example — markers: "any/all/every valid X",
  "always/never", round-trips (encode→decode = identity), idempotence (f(f(x)) = f(x)),
  bounds/monotonicity ("shall not exceed", "shall preserve order"), and `[Error Handling]`
  clauses over a whole rejection class. For each invariant-shaped criterion, write ONE
  property-based test alongside (never instead of) the example-based test — Hypothesis for
  Python, fast-check for TypeScript, mirroring the project's existing test layout and naming.
  Rules: generators must encode the criterion's input class, not convenient toy values; when
  a property fails, add the shrunk counterexample as a permanent example-based regression
  test before fixing; example-shaped criteria ("when the user submits X, ... shall Y" with a
  concrete X) get NO property test — do not force properties where none exist. Passing
  `--pbt` IS the user's approval to add the missing dev dependency (`hypothesis` /
  `fast-check`) — same approval-by-invocation rule as `/ms.fin` git actions; still report
  the addition in Step 5. Property tests carry the same `@TEST` TAG as the criterion they
  verify.
- Insert TAG anchors yourself in Step 3; do not rely on an automatic skill invocation.
- Keep the implementation within the selected phase/task/TAG boundary unless a blocker requires user-visible scope adjustment.
- **Deviations log**: no plan survives contact with the territory intact. When an edge case in
  the actual code forces a deviation from `plan.md`, pick the conservative option, append one
  entry to `specs/{SPEC_ID}/implementation-notes.md` (`what the plan said → what was found →
  what was done instead → why`), and keep going — do not stop the run for a deviation that
  stays inside the task's scope. `/ms.review` includes this file in its report; a deviation
  that turns out to supersede a requirement routes to `/ms.expand` (requirements are only
  ever invented by the user, never patched in place).

This generates or modifies the implementation files while following Constitution principles and existing project patterns.

### Step 3: Insert TAG Anchors

TAG anchors are single comment lines, not metadata blocks. The pre-commit
backstop (`scripts/specter/check_tag_chain.py`) parses only the anchor form
`@KIND:ID`, and nothing consumes status/timestamp metadata (2026-07-11 usage
audit) — so none is written.

Insert at most one anchor line at the top of each generated or meaningfully
modified file:

- Implementation file: `# @CODE:{TAG_ID}` (Python) / `// @CODE:{TAG_ID}` (TS/JS)
- Test file: `# @TEST:{TAG_ID}` / `// @TEST:{TAG_ID}`
- The `@SPEC:{TAG_ID}` anchor already lives in `tasks.md` (written by
  `/ms.tasks`); do not restate it in code files.

Rules:

- Each `@CODE:{TAG_ID}` anchor lives in exactly one file — the backstop rejects
  duplicate `@CODE` ids. A secondary file restates the relationship on a
  `@CHAIN:` line (`@CHAIN: @SPEC:X -> @TEST:X -> @CODE:X`), which the backstop
  ignores.
- Multiple test files may share one `@TEST:{TAG_ID}`; a test file covering
  several ids carries one anchor line per id.
- Do not add line-level anchors inside individual functions.
- Legacy multi-line TAG blocks (`@SPEC:`/`@TEST:` path references, `@CHAIN`,
  `@STATUS`, `@CREATED`, `@UPDATED`) in already-tagged files remain valid — the
  backstop ignores everything except anchors. Do not rewrite them
  retroactively; new work writes bare anchors only.

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
- Do not claim a specific agent or model ran unless it actually did.

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

**TAG**: @SPEC:AUTH-001

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

## TAG Anchor Format

**TypeScript**:

```typescript
// @CODE:AUTH-001
```

**Python**:

```python
# @TEST:AUTH-001
```

One comment line per file, no metadata (see Step 3 for the rules and the
legacy-block compatibility note).

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

**Symptom**: `/speckit-implement` returned error

**Message**:

```
❌ Error: Implementation failed

The base `/speckit-implement` command encountered an error.
Please check the error message above and retry.
```

**Exit**: Code 1

## Run-State Ledger (bookkeeping, not a gate)

Append one line to `.specify/specter-run.jsonl` (create it if needed; append-only, never
rewritten — a missing/corrupt ledger never blocks this command, it only speeds up conductor
resume). Reaching this point without an unresolved in-scope blocker means `verdict` is `PASS`:

```bash
mkdir -p .specify
printf '{"ts":"%s","cycle":"feature","feature":"%s","step":"implement","verdict":"PASS","artifacts":["%s"]}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "<NNN>" "specs/<spec-id>/tasks.md" >> .specify/specter-run.jsonl
```

**Record stop-gate evidence** (this one IS gate-relevant — the Stop hook from `/ms.init`
Step 2.7b blocks turn-end without it when code changed): record the outcome of the last full
test run you **actually executed** during this command. `PASS`/`FAIL` as observed;
`UNAVAILABLE` only when the environment could not run tests at all. Never record a verdict
you did not observe.

```bash
[ -x .specify/scripts/bash/specter-stop-gate.sh ] && .specify/scripts/bash/specter-stop-gate.sh record implement <PASS|FAIL|UNAVAILABLE>
```

## Next Steps

After `/ms.implement`:

1. Verify TAG blocks in generated files.
2. Verify tasks.md was marked complete by the command's mandatory read-back check.
3. Run `/ms.implement` again until no pending TAGs remain.
4. Run `/ms.review` before `/ms.fin`; review owns Codex advisory review, tests, lint, typecheck, build, coverage, and TAG traceability reporting.

## Notes

-   **Wrapper Design**: `/ms.implement` wraps `/speckit-implement` and adds scope, TAG, checklist, and documentation discipline
-   **Default scope**: Current pending phase or phase-part, not a single isolated task
-   **Manual scope options**: `--task`, `TAG_ID`, and `--to-end` are available when needed
-   **TAG blocks**: Inserted as one file-level block in generated or meaningfully modified files
-   **Living Documentation**: Updated directly or via `/ms.up-docs` when the implementation changes project knowledge
-   **Best-effort traceability**: SPEC -> TEST -> CODE, with DOC optional and warnings reported

## Implementation Details

**Architecture**: Wrapper pattern with feature enhancements

**Execution responsibilities**:
- **Core implementation** → `/speckit-implement` with the selected scope and Constitution context
- **Library research** → direct documentation lookup when needed
- **Documentation sync** → direct doc edits or `/ms.up-docs`
- **TAG block insertion** → `/ms.implement` enhancement layer
- **Checklist progress** → update and re-read `tasks.md`

**Tools**:
- SlashCommand (`/speckit-implement`) - Runs scoped implementation
- Read (tasks.md, spec.md, plan.md) - Scope selection and context
- Edit (generated or touched files) - Insert TAG blocks and update docs/tasks
- Bash/ripgrep - Scan for TAGs, project patterns, and verification targets

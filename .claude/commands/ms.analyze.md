---
description: "Pre-implementation document consistency and drift validation"
argument-hint: "[--background] [--skip-codex] [--model MODEL] [--effort low|medium|high]"
---

# /ms.analyze - Document Consistency Gate

Validate that `spec.md`, `plan.md`, and `tasks.md` are coherent before any code
is implemented. This command is the SPECTER wrapper around `/speckit-analyze` for
pre-implementation document validation only, with an advisory Codex document
consistency pass.

Post-implementation code quality gates belong to `/ms.review`. Do not run tests,
lint, typecheck, coverage, or code-level TAG scans from this command.

## Workflow Position

```text
/ms.tasks → /ms.analyze → /ms.implement
```

## Usage

```bash
/ms.analyze
/ms.analyze --background
/ms.analyze --skip-codex
/ms.analyze --model gpt-5.4-mini --effort high
```

Codex runs in the foreground by default. Use `--background` only when the
document set is large and the user explicitly wants to resume later.

Default Codex runtime:

```text
model: gpt-5.5
effort: medium
```

## Purpose

`/ms.analyze` answers: **Are the implementation documents coherent enough to
build from?**

It validates the specification chain before implementation starts:

- Feature scope from `spec.md` is represented in `plan.md`.
- Functional requirements in `spec.md` have corresponding tasks in `tasks.md`.
- Planned files, migrations, and contracts are internally consistent.
- Constitution and AGENTS constraints are acknowledged in the plan/tasks.
- Amendments do not leave stale or contradictory requirements behind.

## GEARS Contract

- When `/ms.analyze` runs before implementation, the command shall compare
  `spec.md`, `plan.md`, and `tasks.md` for coverage, drift, and contradiction.
- When a functional requirement lacks implementation tasks, the command shall
  fail with the missing requirement ID.
- When a task has no originating requirement or plan rationale, the command shall
  fail with the orphan task ID.
- Unless `--skip-codex` is supplied, the command shall ask Codex to perform an
  advisory document consistency review and write the result to
  `specs/[spec-id]/analyze.codex.md`.
- When all documents are consistent, the command shall allow `/ms.implement` to
  proceed.

## Execution Steps

### Step 0: Load Required Artifacts

Read these files in full:

- `.specify/memory/constitution.md`
- `AGENTS.md` if it exists
- `specs/[spec-id]/spec.md`
- `specs/[spec-id]/plan.md`
- `specs/[spec-id]/tasks.md`

If any of `spec.md`, `plan.md`, or `tasks.md` is missing, stop and tell the user
which upstream command must run first.

### Step 1: Run Spec-Kit Foundation

Execute the underlying document analysis:

```text
/speckit-analyze
```

Treat `/speckit-analyze` as the foundation for document consistency only.

### Step 2: SPECTER Drift Detection

Run these additional checks:

1. **Feature Map lineage**: the spec references a Feature section from
   `docs/prd/feature-map.md`.
2. **FR coverage**: every FR in `spec.md` maps to at least one task in `tasks.md`.
3. **Task lineage**: every implementation task maps to an FR, plan step, setup
   requirement, or verification requirement.
4. **Plan coverage**: every planned component, migration, API, and test strategy
   has a corresponding task or explicit out-of-scope note.
5. **Migration consistency**: migration names and numbers match across documents.
6. **File path integrity**: existing file paths mentioned in documents exist; new
   file paths are clearly marked as new.
7. **Amendment integrity**: any superseded FR has a matching Amendment block and
   affected tasks are updated or removed.
8. **Constitution alignment**: plan/tasks acknowledge active Constitution
   constraints, including Section IX if it has been established.

### Step 3: Dual-Agent Document Consistency Review

Unless `--skip-codex` (or `--skip-agents`) is supplied, invoke both Codex and Antigravity to perform advisory document consistency reviews:

#### A. Codex Review
```text
/codex:rescue --fresh --model gpt-5.5 --effort medium <prompt>
```
Codex must read:
- `.specify/memory/constitution.md`
- `AGENTS.md` if it exists
- `docs/prd/feature-map.md`
- `docs/prd/feature-map.checklist.md`
- `docs/prd/checklists/feature-NNN.checklist.md`
- `docs/prd/checklists/feature-NNN.codex-verify.md`
- `specs/[spec-id]/spec.md`
- `specs/[spec-id]/plan.md`
- `specs/[spec-id]/tasks.md`

Codex must write:
`specs/[spec-id]/analyze.codex.md`

Codex prompt:
```text
You are performing an advisory SPECTER document consistency review.

Check spec.md, plan.md, and tasks.md against the Feature Map evidence,
Constitution, and prior checklist gates. Do not edit files except writing
specs/[spec-id]/analyze.codex.md.

Focus on:
- spec FRs missing from tasks
- tasks with no spec, plan, setup, or verification source
- plan components, migrations, APIs, or test strategies missing from tasks
- contradictions between spec, plan, and tasks
- stale or incomplete Amendment handling
- migration number, file path, or contract drift
- Feature Map commitments that no longer survive into spec/plan/tasks

Write:

# Codex Analyze Review

**Mode**: agent-document-consistency
**Result**: PASS | WARN | FAIL

## Findings

| Severity | Finding | Evidence | Required Fix |
| --- | --- | --- | --- |

## Verdict

One concise paragraph.
```

#### B. Antigravity Review
```text
/antigravity:rescue --fresh --model gemini-3.5-flash --effort medium <prompt>
```
Antigravity must read:
- `.specify/memory/constitution.md`
- `AGENTS.md` if it exists
- `docs/prd/feature-map.md`
- `docs/prd/feature-map.checklist.md`
- `docs/prd/checklists/feature-NNN.checklist.md`
- `docs/prd/checklists/feature-NNN.antigravity-verify.md`
- `specs/[spec-id]/spec.md`
- `specs/[spec-id]/plan.md`
- `specs/[spec-id]/tasks.md`

Antigravity must write:
`specs/[spec-id]/analyze.antigravity.md`

Antigravity prompt:
```text
You are performing an advisory SPECTER document consistency review using Google Antigravity.

Check spec.md, plan.md, and tasks.md against the Feature Map evidence,
Constitution, and prior checklist gates. Do not edit files except writing
specs/[spec-id]/analyze.antigravity.md.

Focus on:
- spec FRs missing from tasks
- tasks with no spec, plan, setup, or verification source
- plan components, migrations, APIs, or test strategies missing from tasks
- contradictions between spec, plan, and tasks
- stale or incomplete Amendment handling
- migration number, file path, or contract drift
- Feature Map commitments that no longer survive into spec/plan/tasks

Write:

# Antigravity Analyze Review

**Mode**: agent-document-consistency
**Result**: PASS | WARN | FAIL

## Findings

| Severity | Finding | Evidence | Required Fix |
| --- | --- | --- | --- |

## Verdict

One concise paragraph.
```

If the user supplied `--background`, add `--background` to both invocations and report that `/ms.analyze` must be rerun after both files appear. If the user supplied `--model` or `--effort`, pass those values through instead of the defaults.

#### C. Result handling for both agents:
- `PASS`: keep the SPECTER result unchanged.
- `WARN`: final `/ms.analyze` result is at least `WARN` unless Claude/SPECTER explicitly explains why every warning is a false positive.
- `FAIL`: final `/ms.analyze` result is `FAIL` unless Claude/SPECTER explicitly downgrades the finding with source evidence.
- `PENDING`: if `--background` was used and either report is missing, stop and tell the user to rerun `/ms.analyze` after both reports appear.

#### D. Convergence Policy (re-round caps)

Unbounded re-review loops burn tokens without improving the outcome (atlas F001 ran 10 Codex
rounds on one Feature). Cap automatic re-rounds:

- **Round 1**: the full dual-agent run above, over the whole document set.
- **Round 2** (only if Round 1 produced any `FAIL` finding): re-run scoped to *only* the findings
  that were `FAIL` — the prompt states each failing finding plus the fix diff/edit made in
  response; it does not ask either agent to re-review the whole document set again.
- **Round 3** is the last automatic round, and only re-checks findings still `FAIL` after Round 2.
- **Stop condition**: after Round 3, or as soon as only `WARN`-level findings remain (no `FAIL`),
  stop re-running agents automatically. Record every residual `WARN` in the Step 5 report — do
  not silently drop it — and hand the decision (proceed with warnings, or fix and rerun manually)
  to the user. Running a further round after this point requires an explicit user instruction; it
  is not something `/ms.analyze` does on its own.

### Step 4: Result Model

Use this result model:

- `PASS`: `/ms.implement` may proceed.
- `WARN`: `/ms.implement` may proceed after the user acknowledges the warning.
- `FAIL`: `/ms.implement` must not proceed.

**FAIL conditions:**

- Missing FR coverage in `tasks.md`.
- Orphan task with no spec/plan source.
- Contradictory plan/spec decisions.
- Broken migration numbering across documents.
- Missing Amendment block for superseded requirements.
- Constitution violation in plan/tasks.
- Either Codex or Antigravity `FAIL` finding that cannot be explained as a false positive.

### Step 5: Report

Display a Korean summary:

```json
{
  "document_consistency": "PASS|WARN|FAIL",
  "codex_analysis": "PASS|WARN|FAIL|SKIPPED|PENDING",
  "codex_report": "specs/{id}/analyze.codex.md",
  "antigravity_analysis": "PASS|WARN|FAIL|SKIPPED|PENDING",
  "antigravity_report": "specs/{id}/analyze.antigravity.md",
  "feature_lineage": "PASS|WARN|FAIL",
  "fr_task_coverage": "100%",
  "orphan_tasks": 0,
  "next_step": "/ms.implement"
}
```

If `PASS`:

```text
✅ 문서 일관성 검증 통과

- spec ↔ plan ↔ tasks 정합성 확인
- Feature Map lineage 확인
- Constitution alignment 확인
- Codex document consistency review 확인

🎯 다음 단계: /ms.implement
```

If `FAIL`:

```text
⛔ 문서 일관성 검증 실패

아래 항목을 수정한 뒤 /ms.analyze를 다시 실행하세요.
/ms.implement는 아직 진행하지 마세요.
```

## Relationship To Other Commands

| Command | Responsibility | Timing |
| --- | --- | --- |
| `/ms.verify` | Global PRD → Feature Map gate | Before `/ms.constitution` |
| `/ms.checklist` + `/ms.codex-verify` | Per-Feature PRD readiness gate | Before `/ms.specify` |
| `/ms.analyze` | spec ↔ plan ↔ tasks document gate plus Codex document review | Before `/ms.implement` |
| `/ms.review` | code quality + executable gates | After `/ms.implement` |

## Next Command

After `/ms.analyze` passes, run `/ms.implement`.

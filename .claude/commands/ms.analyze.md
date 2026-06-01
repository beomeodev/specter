---
description: "Pre-implementation document consistency and drift validation"
---

# /ms.analyze - Document Consistency Gate

Validate that `spec.md`, `plan.md`, and `tasks.md` are coherent before any code
is implemented. This command is the SPECTER wrapper around `/speckit.analyze` for
pre-implementation document validation only.

Post-implementation code quality gates belong to `/ms.review`. Do not run tests,
lint, typecheck, coverage, or code-level TAG scans from this command.

## Workflow Position

```text
/ms.tasks → /ms.analyze → /ms.implement
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
/speckit.analyze
```

Treat `/speckit.analyze` as the foundation for document consistency only.

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

### Step 3: Result Model

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

### Step 4: Report

Display a Korean summary:

```json
{
  "document_consistency": "PASS|WARN|FAIL",
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
| `/ms.checklist` | PRD → Feature Map gate | Before `/ms.specify` |
| `/ms.analyze` | spec ↔ plan ↔ tasks document gate | Before `/ms.implement` |
| `/ms.review` | code quality + executable gates | After `/ms.implement` |

## Next Command

After `/ms.analyze` passes, run `/ms.implement`.

---
description: "Validate PRD → Feature Map conversion before /ms.specify"
---

# /ms.checklist - Feature Map Validation Gate

Validate that the user's PRD was converted into a correct Feature Map before any
feature specification is created.

This command runs **after `/ms.featuremap` and before `/ms.specify`**. It no
longer validates `spec.md`; there is intentionally no `spec.md` prerequisite.

## Purpose

Feature Map quality is the upstream control point for the whole SPECTER pipeline.
If PRD commitments are lost, duplicated, or assigned to the wrong Feature, every
downstream `spec.md`, `plan.md`, and `tasks.md` will inherit that mistake.

`/ms.checklist` therefore works as an automated pre-spec gate:

1. Generate a PRD-to-Feature-Map checklist.
2. Run the checklist immediately.
3. Write the checklist and audit result to `docs/prd/feature-map.checklist.md`.
4. Block `/ms.specify` guidance if critical issues remain.

## Usage

```bash
/ms.checklist
```

No mode flags are required. The command has exactly one workflow position:

```text
/ms.featuremap @docs/prd/PRD.md
/ms.checklist
/ms.specify
```

## GEARS Contract

- When `/ms.checklist` runs, the command shall read the PRD and
  `docs/prd/feature-map.md` before producing any verdict.
- When a PRD commitment has no owning Feature, the command shall mark the audit
  as failed and identify the missing PRD reference.
- When a Feature Map item duplicates detailed PRD requirements instead of
  referencing PRD sections, the command shall mark the item as a correction.
- When validation completes, the command shall write both checklist items and
  pass/fail results to `docs/prd/feature-map.checklist.md`.

## Execution Steps

### Step 0: Load Required Artifacts

Read these files in full:

- `docs/prd/PRD.md` or the PRD path recorded in `docs/prd/feature-map.md`
- `docs/prd/feature-map.md`
- `.specify/memory/constitution.md` if it exists
- `AGENTS.md` if it exists

**If `docs/prd/feature-map.md` is missing**, stop:

```text
⛔ Feature Map not found.

Run this first:
  /ms.featuremap @docs/prd/PRD.md

Stopping now.
```

**If no PRD can be identified**, ask the user for the PRD path and stop. Do not
guess from memory.

### Step 1: Generate The Checklist

Create checklist items under these categories:

#### 1. PRD Coverage

- Every functional requirement, user journey, milestone, constraint, and
  non-functional requirement in the PRD has exactly one owning Feature.
- Every deferred PRD item names the later owning Feature.
- No PRD commitment is silently dropped because it is "small" or cross-cutting.

#### 2. Feature Boundaries

- Each Feature is independently implementable, mergeable, and verifiable.
- Each Feature is larger than a trivial chore but smaller than a multi-phase
  project.
- Engine/backend capabilities and UI/screen work are split when that makes each
  slice independently shippable.

#### 3. Dependency DAG

- The dependency graph has no cycle.
- Parallel Features are marked only when genuinely independent.
- The next Feature is unambiguous.

#### 4. Stub-and-Forward

- Shared foundations laid down early are explicitly marked as stubs.
- Every stub names the later Feature that activates real behavior.
- Migration numbers or shared structure ownership are pre-allocated where needed.

#### 5. Phase Completion

- Each Phase has a concrete E2E scenario.
- The Phase E2E scenario appears in the done criteria of that Phase's last
  Feature.

#### 6. Feature Section Template

- Every Feature section has the required headings:
  - `### One-line summary`
  - `### PRD references`
  - `### In scope`
  - `### Explicitly out of scope`
  - `### Key decisions`
  - `### Done criteria`
- Every out-of-scope item points to an owning Feature number.
- Done criteria are observable and end with `CI passes green`.

#### 7. Reference Discipline

- The Feature Map references PRD sections instead of copying full requirements.
- The reference priority is preserved:
  `PRD > product-principles > constitution > feature-map > dependency Feature spec`.
- The persisted Feature Map is English.

### Step 2: Run The Checklist Automatically

Evaluate every item against the PRD and Feature Map.

Use this result model:

- `PASS`: no correction needed
- `WARN`: acceptable to proceed, but the map should be improved
- `FAIL`: `/ms.specify` should not proceed until fixed

**FAIL conditions**:

- Any PRD commitment has no owning Feature.
- Any out-of-scope item lacks a destination Feature.
- The DAG contains a cycle.
- A Feature lacks required template sections.
- A Phase's final Feature lacks the Phase E2E scenario.
- The Feature Map is not in English.

### Step 3: Write The Audit File

Write the generated checklist and results to:

```text
docs/prd/feature-map.checklist.md
```

Use this structure:

```markdown
# Feature Map Checklist

**PRD**: docs/prd/PRD.md
**Feature Map**: docs/prd/feature-map.md
**Feature Map SHA256**: <sha256 of docs/prd/feature-map.md at audit time>
**Result**: PASS | WARN | FAIL
**Generated**: YYYY-MM-DD

## Summary

- PASS: N
- WARN: N
- FAIL: N

## Checklist Results

| Category | Check | Result | Evidence | Required Fix |
| --- | --- | --- | --- | --- |
| PRD Coverage | ... | PASS | PRD §... → Feature 003 | - |

## Blocking Fixes

- [ ] Feature NNN: ...

## Non-Blocking Improvements

- [ ] ...
```

### Step 4: Report The Verdict

If the result is `PASS`:

```text
✅ Feature Map checklist passed.

📄 Audit: docs/prd/feature-map.checklist.md
🎯 Next step: /ms.specify using the first eligible Feature section.
```

If the result is `WARN`:

```text
⚠️ Feature Map checklist passed with warnings.

📄 Audit: docs/prd/feature-map.checklist.md
권장 개선사항을 확인한 뒤 /ms.specify로 진행할 수 있습니다.
```

If the result is `FAIL`:

```text
⛔ Feature Map checklist failed.

📄 Audit: docs/prd/feature-map.checklist.md
아래 Blocking Fixes를 반영한 뒤 /ms.checklist를 다시 실행하세요.
/ms.specify는 아직 진행하지 마세요.
```

## Wrapper Priority And Bypass Protection

`/ms.checklist` is intentionally **not** a thin wrapper around `/speckit.checklist`.
Spec-Kit's native checklist validates an existing spec, which is too late for this
SPECTER gate. This command owns the earlier PRD-to-Feature-Map validation step.

Bypass protection:

- `/ms.checklist` must not delegate to `/speckit.checklist`.
- `/speckit.checklist` may still exist after `/ms.init`, but it is not part of
  the SPECTER happy path.
- `/ms.specify` must check `docs/prd/feature-map.checklist.md` and refuse to
  proceed when the audit is missing, failed, or stale against the current
  Feature Map SHA. This makes the checklist an actual gate, not a generated
  document the user can forget to apply.

## What This Command Does Not Do

- It does not create or validate `spec.md`.
- It does not edit the Feature Map automatically unless the user explicitly asks
  for fixes. The audit identifies required corrections first.

## Next Command

After `/ms.checklist` passes, run `/ms.specify` and paste the first eligible
Feature section from `docs/prd/feature-map.md`.

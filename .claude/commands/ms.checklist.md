---
description: "Validate PRD coverage for the global Feature Map or the next Feature cycle"
---

# /ms.checklist - Feature Map Audit Gate

Validate that the PRD set is preserved through the Feature Map before any spec is
created. The command has two modes:

- `/ms.checklist --global`: one-time global audit after `/ms.featuremap`.
- `/ms.checklist`: default per-Feature audit at the start of every DAG cycle.

This command intentionally does **not** validate `spec.md`; there is no `spec.md`
prerequisite. It exists before `/ms.specify` so PRD loss is caught before a weak
Feature section becomes a formal spec.

## Purpose

Feature Map quality is the upstream control point for the whole SPECTER pipeline.
If a PRD commitment is lost, duplicated, diluted, or assigned to the wrong
Feature, every downstream `spec.md`, `plan.md`, and `tasks.md` will inherit that
mistake.

The split is deliberate:

1. **Global audit** (`--global`) proves the whole PRD set has been mapped into the
   Feature Map once.
2. **Per-Feature audit** (default) proves the next DAG Feature is ready to become
   a spec and still reflects the PRD sections it claims to own.

## Usage

```bash
/ms.checklist --global       # run once after /ms.featuremap
/ms.checklist                # run at the start of each Feature cycle
/ms.checklist Feature 003    # optional explicit Feature target
```

Workflow position:

```text
/ms.featuremap @docs/prd/PRD.md [@docs/prd/another.md]
/ms.checklist --global
/ms.constitution

# Repeat in DAG order:
/ms.checklist
/ms.specify
/ms.clarify
/ms.plan
/ms.tasks
/ms.analyze
/ms.implement
/ms.review
```

## GEARS Contract

- When `/ms.checklist --global` runs, the command shall validate that every PRD
  commitment has exactly one owning Feature in the PRD Commitment Index.
- When `/ms.checklist` runs without `--global`, the command shall select the
  next eligible Feature from the dependency DAG unless the user names a Feature.
- When a selected Feature references PRD sections, the command shall read those
  PRD sections and verify that the Feature scope, out-of-scope list, decisions,
  and done criteria preserve the referenced commitments without overreach.
- When validation completes, the command shall write an audit file with PASS,
  WARN, or FAIL and the current Feature Map SHA256.

## Mode Selection

### `--global`: Global Feature Map Audit

Use this immediately after `/ms.featuremap` and whenever `docs/prd/feature-map.md`
changes. It writes:

```text
docs/prd/feature-map.checklist.md
```

### Default: Per-Feature Readiness Audit

Use this at the start of every Feature cycle before `/ms.specify`. It writes:

```text
docs/prd/checklists/feature-NNN.checklist.md
```

The default mode requires a passing, non-stale global audit first. If the global
audit is missing, failed, or stale, stop and tell the user to run:

```bash
/ms.checklist --global
```

## Execution Steps

### Step 0: Load Required Artifacts

Read these files in full:

- Every source PRD recorded in `docs/prd/feature-map.md` (or the PRD path list passed to `/ms.featuremap`)
- `docs/prd/feature-map.md`
- `.specify/memory/constitution.md` if it exists
- `AGENTS.md` if it exists

**If `docs/prd/feature-map.md` is missing**, stop:

```text
⛔ Feature Map not found.

Run this first:
  /ms.featuremap @docs/prd/PRD.md [@docs/prd/another.md]

Stopping now.
```

**If no complete PRD source set can be identified**, ask the user for the PRD path and stop. Do not
guess from memory.

---

## Global Audit: `/ms.checklist --global`

### Step G1: Validate Required Feature Map Structure

Check that `docs/prd/feature-map.md` contains:

- Header with every PRD source path/version.
- Usage section.
- `## PRD Commitment Index`.
- Full Feature dependency graph.
- Progress Ledger.
- All Feature sections.
- Global rules and reference priority.

### Step G2: Audit PRD Commitment Coverage

Evaluate the PRD Commitment Index against the full PRD source set:

- Every functional requirement, user journey, milestone, acceptance criterion,
  constraint, non-functional requirement, integration promise, data/migration
  promise, and explicit exclusion has an index row.
- Every index row has a source PRD, stable PRD reference, and exactly one owning Feature.
- Cross-cutting commitments have one real owner, with earlier stubs called out
  as stubs only.
- No PRD commitment is silently dropped because it is small, operational, or
  cross-cutting.
- No PRD commitment is owned by multiple Features.

### Step G3: Audit Feature Boundaries And DAG

Check:

- Each Feature is independently implementable, mergeable, and verifiable.
- Each Feature is larger than a trivial chore but smaller than a multi-phase
  project.
- Engine/backend capabilities and UI/screen work are split when that makes each
  slice independently shippable.
- The dependency graph has no cycle.
- Parallel Features are marked only when genuinely independent.
- The first eligible Feature is unambiguous.

### Step G4: Audit Stub-And-Forward And Phase Completion

Check:

- Shared foundations laid down early are explicitly marked as stubs.
- Every stub names the later Feature that activates real behavior.
- Migration numbers or shared structure ownership are pre-allocated where needed.
- Each Phase has a concrete E2E scenario.
- Each Phase E2E scenario appears in the done criteria of that Phase's last
  Feature.

### Step G5: Write The Global Audit

Write:

```text
docs/prd/feature-map.checklist.md
```

Use this structure:

```markdown
# Feature Map Global Checklist

**Mode**: global
**PRDs**: <source label → path list>
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
| PRD Coverage | ... | PASS | Product PRD §... → Feature 003 | - |

## Blocking Fixes

- [ ] Feature NNN: ...

## Non-Blocking Improvements

- [ ] ...
```

### Global FAIL Conditions

- PRD Commitment Index is missing.
- Any PRD commitment in any source PRD has no index row.
- Any index row lacks a source PRD, stable PRD reference, or owning Feature.
- Any PRD commitment has multiple owning Features.
- Any out-of-scope item lacks a destination Feature.
- The DAG contains a cycle.
- A Feature lacks required template sections.
- A Phase's final Feature lacks the Phase E2E scenario.
- The Feature Map is not in English.

---

## Per-Feature Audit: `/ms.checklist`

### Step F1: Verify Global Audit And Constitution Baseline First

Before auditing a Feature, require:

1. `docs/prd/feature-map.checklist.md` exists.
2. The global audit contains `**Mode**: global`.
3. The global audit contains `**Result**: PASS` or `**Result**: WARN`.
4. The global audit does not contain `**Result**: FAIL`.
5. The global audit's `Feature Map SHA256` matches the current
   `docs/prd/feature-map.md` SHA256.
6. `.specify/memory/constitution.md` has an established Section IX baseline from `/ms.constitution`
   or explicitly records that no durable project-specific constraints were found.

If this fails, stop:

```text
⛔ Global Feature Map audit is missing, failed, or stale.

Run this first:
  /ms.checklist --global

Fix any Blocking Fixes in docs/prd/feature-map.checklist.md, re-run the global audit,
then retry /ms.checklist for the next Feature.
```

If Section IX is not established, stop:

```text
⛔ Project Constitution baseline is not established.

Run this first:
  /ms.constitution

Then retry /ms.checklist for the next Feature.
```

### Step F2: Select The Target Feature

If the user names a Feature (`Feature 003`, `003`, or a matching Feature title),
audit that Feature.

Otherwise, select the next eligible Feature:

1. Read the dependency DAG and Progress Ledger.
2. List existing `specs/<NNN>-*` directories.
3. Pick the lowest-order Feature whose dependencies are already specified or
   shipped and which has no `specs/<NNN>-*` directory.
4. If multiple parallel Features are eligible, choose the lowest Feature number
   and report the alternatives.
5. If no Feature is eligible, report that all planned Features are already
   specified or blocked by unmet dependencies.

### Step F3: Load The Feature's PRD Evidence

For the selected Feature:

- Extract the full `## Feature NNN:` section.
- Extract its `### Source PRDs` list.
- Extract its `### PRD references` list.
- Extract every PRD Commitment Index row where `Owning Feature = Feature NNN`.
- Read all listed Source PRD documents and the referenced PRD sections in full.

If the Feature has no Source PRDs, no PRD references, or no owned commitment rows, mark FAIL.

### Step F4: Audit Feature Readiness Against The PRD

Check:

#### 1. PRD Fidelity

- Every owned commitment row is represented in `### In scope`, `### Explicitly
  out of scope`, `### Key decisions`, or `### Done criteria`.
- The Feature does not dilute PRD language into vague implementation labels.
- The Feature does not invent behavior that is absent from the PRD, product
  principles, Constitution, or dependency Feature specs.
- The Feature does not omit acceptance criteria or NFRs attached to its PRD
  references.

#### 2. Boundary Discipline

- The Feature does not absorb commitments owned by later Features.
- Deferred work is listed under `Explicitly out of scope` and points to the
  owning Feature.
- Dependencies are already satisfied or explicitly treated as stubs.
- Cross-cutting behavior is stubbed or deferred unless this Feature is the real
  owner in the Commitment Index.

#### 3. Spec-Input Completeness

- The Feature section has all required headings.
- `### In scope` names concrete deliverables, endpoints, modules, migrations,
  UI surfaces, or tests; it does not copy PRD prose wholesale.
- `### Done criteria` are observable and tied to the PRD acceptance evidence.
- The last done criterion is `CI passes green`.

### Step F5: Write The Per-Feature Audit

Create the directory if needed:

```bash
mkdir -p docs/prd/checklists
```

Write:

```text
docs/prd/checklists/feature-NNN.checklist.md
```

Use this structure:

```markdown
# Feature NNN Checklist

**Mode**: per-feature
**Feature**: Feature NNN: <name>
**PRDs**: <source label → path list>
**Feature Map**: docs/prd/feature-map.md
**Feature Map SHA256**: <sha256 of docs/prd/feature-map.md at audit time>
**Global Audit**: docs/prd/feature-map.checklist.md
**Result**: PASS | WARN | FAIL
**Generated**: YYYY-MM-DD

## PRD Evidence

| Source PRD | PRD Ref | Commitment Type | Short Label | Handling In This Feature |
| --- | --- | --- | --- | --- |
| Product PRD | §3.1 | Functional | User login | In scope |

## Checklist Results

| Category | Check | Result | Evidence | Required Fix |
| --- | --- | --- | --- | --- |
| PRD Fidelity | ... | PASS | PRD §... / Feature NNN | - |

## Blocking Fixes

- [ ] ...

## Non-Blocking Improvements

- [ ] ...
```

### Per-Feature FAIL Conditions

- The selected Feature is not the next eligible Feature and the user did not
  explicitly confirm skipping DAG order.
- The Feature has no Source PRDs.
- The Feature has no PRD references.
- The Feature has no owned PRD Commitment Index rows.
- Any owned PRD commitment is absent from scope, deferred ownership, decisions,
  or done criteria.
- Any referenced PRD acceptance criterion or NFR is absent from done criteria or
  tests.
- The Feature absorbs commitments owned by another Feature.
- An out-of-scope item lacks a destination Feature.
- Required Feature template sections are missing.
- Done criteria are not observable or do not end with `CI passes green`.

---

## Result Model

- `PASS`: no correction needed.
- `WARN`: acceptable to proceed, but the map should be improved.
- `FAIL`: `/ms.specify` must not proceed until fixed.

## Report The Verdict

If the result is `PASS`:

```text
✅ Checklist passed.

📄 Audit: <audit path>
🎯 Next step: /ms.specify using the checked Feature section.
```

If the result is `WARN`:

```text
⚠️ Checklist passed with warnings.

📄 Audit: <audit path>
권장 개선사항을 확인한 뒤 /ms.specify로 진행할 수 있습니다.
```

If the result is `FAIL`:

```text
⛔ Checklist failed.

📄 Audit: <audit path>
아래 Blocking Fixes를 반영한 뒤 /ms.checklist를 다시 실행하세요.
/ms.specify는 아직 진행하지 마세요.
```

## Wrapper Priority And Bypass Protection

`/ms.checklist` is intentionally **not** a thin wrapper around `/speckit.checklist`.
Spec-Kit's native checklist validates an existing spec, which is too late for this
SPECTER gate. This command owns PRD-to-Feature-Map validation before `spec.md`
exists.

Bypass protection:

- `/ms.checklist` must not delegate to `/speckit.checklist`.
- `/speckit.checklist` may still exist after `/ms.init`, but it is not part of
  the SPECTER happy path.
- `/ms.specify` must check both the global audit and the selected Feature audit,
  and refuse to proceed when either audit is missing, failed, or stale against
  the current Feature Map SHA.

## What This Command Does Not Do

- It does not create or validate `spec.md`.
- It does not edit the Feature Map automatically unless the user explicitly asks
  for fixes. The audit identifies required corrections first.

## Next Command

After `/ms.checklist --global` passes, run `/ms.constitution` once. Then run `/ms.checklist` for
the first eligible Feature.

After `/ms.checklist` passes for a Feature, run `/ms.specify` and paste that
checked Feature section from `docs/prd/feature-map.md`.

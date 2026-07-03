---
description: "Validate the next Feature against its PRD evidence before /ms.specify"
argument-hint: "[Feature NNN]"
---

# /ms.checklist - Per-Feature Readiness Gate

Validate that the next Feature in `docs/prd/feature-map.md` is ready to become
a `spec.md`. This command is now per-Feature only.

The old `/ms.checklist --global` flow is removed. Global Feature Map validation
is handled by:

```text
/ms.codex-checklist -> /ms.verify
```

## Purpose

The global gate proves that the whole PRD set was preserved in the Feature Map.
This command proves that one selected Feature is ready to be specified and still
reflects the PRD sections and commitment rows it claims to own.

It intentionally does **not** validate an existing `spec.md`; there is no
`spec.md` prerequisite. It exists before `/ms.specify` so weak Feature sections
are caught before they become formal specs.

## Usage

```bash
/ms.checklist
/ms.checklist Feature 003
/ms.checklist 003
```

Workflow position:

```text
/ms.featuremap @docs/prd/PRD.md [@docs/prd/another.md]
/ms.codex-checklist @docs/prd/PRD.md [@docs/prd/another.md]
/ms.verify
/ms.constitution

# Repeat in DAG order:
/ms.checklist
/ms.agent-verify
/ms.specify
/ms.clarify
/ms.plan
/ms.tasks
/ms.analyze
/ms.implement
/ms.review
```

## GEARS Contract

- When `/ms.checklist` runs without an explicit Feature, the command shall
  select the next eligible Feature from the dependency DAG unless the user names
  a Feature.
- When a selected Feature references PRD sections, the command shall read those
  PRD sections and verify that the Feature scope, out-of-scope list, decisions,
  and done criteria preserve the referenced commitments without overreach.
- When `docs/prd/codex/checklist.md` exists, the command shall use its C-IDs as
  additional evidence for the selected Feature, but the PRD text remains
  authoritative.
- When validation completes, the command shall write an audit file with PASS,
  WARN, or FAIL and the current Feature Map SHA256.

## Execution Steps

### Step 0: Load Required Artifacts

Read these files in full:

- `docs/prd/feature-map.md`
- `docs/prd/feature-map.progress.md`
- `docs/prd/feature-map.checklist.md`
- every source PRD recorded in `docs/prd/feature-map.md`
- `docs/prd/codex/checklist.md` if it exists
- `.specify/memory/constitution.md`
- `AGENTS.md` if it exists

If `--global` is supplied, refuse:

```text
⛔ /ms.checklist --global has been removed.

Use the new global flow:
  /ms.codex-checklist @docs/prd/PRD.md [@docs/prd/another.md]
  /ms.verify

Then run:
  /ms.constitution
  /ms.checklist
```

If `docs/prd/feature-map.md` is missing, stop:

```text
⛔ Feature Map not found.

Run this first:
  /ms.featuremap @docs/prd/PRD.md [@docs/prd/another.md]

Stopping now.
```

If no complete PRD source set can be identified, ask the user for the PRD path
and stop. Do not guess from memory.

### Step 1: Verify Global Gate And Constitution Baseline First

Before auditing a Feature, run the deterministic gate checker instead of manually
re-deriving these facts:

```bash
.specify/scripts/bash/specter-gate.sh
```

This mechanically checks: `docs/prd/feature-map.checklist.md` exists, is
`**Mode**: global`, its `**Result**` is `PASS` or `WARN` (not `FAIL`), its
`Feature Map SHA256` matches the current `docs/prd/feature-map.md`, and Constitution
Section IX is established. Read the JSON `overall` and `reasons[]` fields.

If `overall` is `MISSING` or `FAIL` and every `reasons[]` entry is about the global
checklist (its existence, Mode, Result, or SHA), stop:

```text
⛔ Global Feature Map verification is missing, failed, stale, or from the removed legacy flow.

Run this first:
  /ms.codex-checklist @docs/prd/PRD.md [@docs/prd/another.md]
  /ms.verify

Fix any Blocking Fixes in docs/prd/feature-map.checklist.md, then retry /ms.checklist.
```

If any `reasons[]` entry is about `constitution_section_ix_established`, stop:

```text
⛔ Project Constitution baseline is not established.

Run this first:
  /ms.constitution

Then retry /ms.checklist for the next Feature.
```

### Step 2: Select The Target Feature

If the user names a Feature (`Feature 003`, `003`, or a matching Feature title),
audit that Feature.

Otherwise, select the next eligible Feature:

1. Read the dependency DAG (`docs/prd/feature-map.md`) and the Progress Ledger
   (`docs/prd/feature-map.progress.md`).
2. List existing `specs/<NNN>-*` directories.
3. Pick the lowest-order Feature whose dependencies are already specified or
   shipped and which has no `specs/` directory of its own.
4. If multiple parallel Features are eligible, choose the lowest Feature number
   and report the alternatives.
5. If no Feature is eligible, report that all planned Features are already
   specified or blocked by unmet dependencies.

### Step 3: Load The Feature's PRD Evidence

For the selected Feature:

- Extract the full `## Feature NNN:` section.
- Extract its `### Source PRDs` list.
- Extract its `### PRD references` list.
- Extract every PRD Commitment Index row where `Owning Feature = Feature NNN`.
- Read all listed Source PRD documents and the referenced PRD sections in full.
- If `docs/prd/codex/checklist.md` exists, extract any Codex C-IDs whose PRD
  references, labels, or expected Feature Map handling correspond to this
  Feature's owned PRD rows.

If the Feature has no Source PRDs, no PRD references, or no owned commitment
rows, mark FAIL.

### Step 4: Audit Feature Readiness Against The PRD

#### 1. PRD Fidelity

- Every owned commitment row is represented in `### In scope`, `### Explicitly
  out of scope`, `### Key decisions`, or `### Done criteria`.
- Every matching Codex C-ID is represented or explicitly explained as a false
  positive or handled by another owning Feature.
- The Feature does not dilute PRD language into vague implementation labels.
- The Feature does not invent behavior that is absent from the PRD, product
  principles, Constitution, or dependency Feature specs.
- The Feature does not omit acceptance criteria or NFRs attached to its PRD
  references.
- **User-facing exposure**: every owned commitment that implies a user-visible surface (UI, CLI,
  API, notification) has a concrete `### In scope` deliverable that actually exposes it (an
  endpoint, screen, command, or message the user can reach) — not just a backend capability with
  no surface — OR an explicit `### Explicitly out of scope` row naming the Feature that owns the
  exposure. A commitment with neither is a FAIL, not a warning.

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

### Step 5: Write The Per-Feature Audit

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
**PRDs**: <source label -> path list>
**Feature Map**: docs/prd/feature-map.md
**Feature Map SHA256**: <sha256 of docs/prd/feature-map.md at audit time>
**Global Audit**: docs/prd/feature-map.checklist.md
**Codex Checklist**: docs/prd/codex/checklist.md | not available
**Result**: PASS | WARN | FAIL
**Generated**: YYYY-MM-DD

## PRD Evidence

| Source PRD | PRD Ref | Commitment Type | Short Label | Handling In This Feature |
| --- | --- | --- | --- | --- |

## Codex Checklist Evidence

| Codex ID | PRD Ref | Expected Handling | Handling In This Feature |
| --- | --- | --- | --- |

## Checklist Results

| Category | Check | Result | Evidence | Required Fix |
| --- | --- | --- | --- | --- |

## Blocking Fixes

- [ ] ...

## Non-Blocking Improvements

- [ ] ...
```

### FAIL Conditions

- The selected Feature is not the next eligible Feature and the user did not
  explicitly confirm skipping DAG order.
- The Feature has no Source PRDs.
- The Feature has no PRD references.
- The Feature has no owned PRD Commitment Index rows.
- Any owned PRD commitment is absent from scope, deferred ownership, decisions,
  or done criteria.
- Any referenced PRD acceptance criterion or NFR is absent from done criteria or
  tests.
- Any matching Codex C-ID is missing without a justified false-positive or
  destination Feature explanation.
- The Feature absorbs commitments owned by another Feature.
- An out-of-scope item lacks a destination Feature.
- Required Feature template sections are missing.
- Done criteria are not observable or do not end with `CI passes green`.
- A user-facing commitment (UI, CLI, API, notification) has no in-scope deliverable exposing it
  and no out-of-scope row naming its owning Feature.

## Result Model

- `PASS`: no correction needed.
- `WARN`: acceptable to proceed, but the map should be improved.
- `FAIL`: `/ms.specify` must not proceed until fixed.

## Report The Verdict

If the result is `PASS`:

```text
✅ Feature checklist passed.

📄 Audit: docs/prd/checklists/feature-NNN.checklist.md
🎯 Next step: /ms.agent-verify
```

If the result is `WARN`:

```text
⚠️ Feature checklist passed with warnings.

📄 Audit: docs/prd/checklists/feature-NNN.checklist.md
권장 개선사항을 확인한 뒤 /ms.agent-verify로 진행할 수 있습니다.
```

If the result is `FAIL`:

```text
⛔ Feature checklist failed.

📄 Audit: docs/prd/checklists/feature-NNN.checklist.md
아래 Blocking Fixes를 반영한 뒤 /ms.checklist를 다시 실행하세요.
/ms.specify는 아직 진행하지 마세요.
```

## Wrapper Priority And Bypass Protection

`/ms.checklist` is intentionally **not** a thin wrapper around
`/speckit-checklist`. Spec-Kit's native checklist validates an existing spec,
which is too late for this SPECTER gate. This command owns per-Feature
PRD-to-Feature validation before `spec.md` exists.

Bypass protection:

- `/ms.checklist` must not delegate to `/speckit-checklist`.
- `/speckit-checklist` may still exist after `/ms.init`, but it is not part of
  the SPECTER happy path.
- `/ms.specify` must check the global `/ms.verify` audit, the selected Feature
  audit, and the dual-agent per-Feature verification before proceeding.

## What This Command Does Not Do

- It does not create or validate `spec.md`.
- It does not edit the Feature Map automatically unless the user explicitly asks
  for fixes. The audit identifies required corrections first.
- It does not run agents. Use `/ms.agent-verify` after this command.

## Next Command

After `/ms.checklist` passes for a Feature, run `/ms.agent-verify`. After dual-agent
verification is available, run `/ms.specify` and paste the checked Feature
section from `docs/prd/feature-map.md`.

---
description: "Lightweight track for changes that do NOT introduce a new requirement — bug fixes, corrections, UI/style polish — with TDD + TAG + gate but no spec/clarify/plan/tasks ceremony."
---

# /ms.fix — Lightweight fix/polish track

For changes that **correct, adjust, or polish existing behavior or appearance**
and do **not** introduce a new requirement. Keeps the discipline that matters
(TDD where testable, a TAG for traceability, the pre-push gate) while skipping
the full SPEC→clarify→plan→tasks ceremony that doesn't fit small work.

## Step 0: The discriminator — is this really a fix?

**Use the FULL workflow (`/ms.featuremap` → `/ms.specify` → … → `/ms.implement`) instead
if the change introduces a new requirement**, i.e. ANY of:
- a new GEARS "shall" (new user-facing capability / behavior contract)
- a new endpoint, a new DB schema/migration, a new external integration

**Use `/ms.fix` if it's**: a bug fix, a correction to existing behavior, a copy/label
change, a color/style/layout polish, a refactor of existing code, a config tweak.

> If unsure: does it change *what the product promises*, or just *how correctly/nicely
> it already does it*? The former → full workflow. The latter → `/ms.fix`.

## Step 1: Size the change (decides ceremony, from existing rules)

Estimate the files this touches (Constitution: "Small units 1-2 files"; "3+ files
→ plan first"):

- **Small (1–2 files)** → go straight to Step 2 (lightweight).
- **Medium (3+ files)** → **mini-plan first** (Constitution §4.1 already mandates this):
  list (a) files to touch, (b) the change in each, (c) risks. Present it, get a
  quick confirm, THEN Step 2. No spec/tasks doc — just the mini-plan inline.

## Step 2: TDD where testable

- If the change is behavioral (logic, API, data): write/extend a failing test
  first (RED), make it pass (GREEN), refactor — using the project's own test
  runner (whatever CI uses).
- If the change is purely presentational (color, spacing, copy) and has no
  meaningful unit assertion: skip RED-GREEN, but state explicitly that it's a
  presentational change with no test, and rely on the gate + manual verify.

Stay **surgical** (Constitution Change Discipline): touch only what the fix
requires; don't refactor adjacent code.

## Step 3: TAG for traceability (closes the fix-track Trackable gap)

Fixes must still be traceable — this is what `/finq` alone skips today.

- **Correcting code that already has a TAG** → reuse that TAG; bump its
  `@UPDATED` (git-derived, per `ms-workflow-tag-manager`) and, if behavior
  changed, note it.
- **New code with no governing SPEC** → assign a **FIX-id** TAG:
  `@CODE:FIX-<area>-<NNN>` (e.g. `@CODE:FIX-UPLOADS-003`), `@SPEC: (fix — no spec)`,
  with `@TEST` if a test exists. Keep the chain block format identical to
  `/ms.implement` (see `ms-workflow-tag-manager`), `@STATUS: implemented`.

## Step 4: Lightweight docs (scale to size)

- **Always**: append a **one-line** entry to `docs/dev_daily.md` (what + why + TAG).
- **Skip** API-doc generation and README updates (those are for new features).
- For Medium (3+ files) changes, the dev_daily line should name each area touched.

## Step 5: Gate (same gate as everything else)

Run the **`local-ci`** subagent (lint → types → tests → build for affected areas;
reports pass/fail per gate, edits nothing). Fix any failure before proceeding.
This is the same pre-push gate `/fin` uses — uniformity is the point.

## Step 6: Hand off

Commit (TAG id in the message) on a `fix/<short-name>` branch, then continue with
the existing flow: `/fin` (or `/finq`) to push + open PR, then `/ms.merglease`.
Do not commit/push without user approval (Constitution §2).

## Relationship to other commands

```
새 요구사항?
 ├ 예  → /ms.featuremap → /ms.checklist → /ms.specify → /ms.clarify → /ms.plan → /ms.constitution(첫 기준 없을 때만) → /ms.tasks → /ms.analyze → /ms.implement → /ms.review → /fin → /ms.merglease
 └ 아니오 → /ms.fix (1-2 files: 경량 / 3+ files: mini-plan 먼저) → /fin|/finq → /ms.merglease
```

`/ms.fix` is the **single, uniform track for all non-requirement changes** — it
replaces the ad-hoc "skip the workflow and just `/finq`" path, so even small fixes
keep a TAG and pass the gate.

---
description: "Lightweight track for changes that do NOT introduce a new requirement — bug fixes, corrections, UI/style polish — with TDD + TAG + gate but no spec/clarify/plan/tasks ceremony."
argument-hint: "[bug or correction description]"
---

# /ms.fix — Lightweight fix/polish track

For changes that **correct, adjust, or polish existing behavior or appearance**
and do **not** introduce a new requirement. Keeps the discipline that matters
(TDD where testable, a TAG for traceability, the pre-push gate) while skipping
the full SPEC→clarify→plan→tasks ceremony that doesn't fit small work.

## Step 0: The discriminator — is this really a fix?

Three tracks, by whether the change introduces a new requirement and whether a checked PRD /
Feature Map baseline already exists:

- **No new requirement** — a bug fix, a correction to existing behavior, a copy/label change, a
  color/style/layout polish, a refactor of existing code, a config tweak → **`/ms.fix`** (this
  command). Continue below. A deploy/environment-boundary incident (SSH tunnel, reverse proxy,
  TLS, container lifecycle, secret rotation, "works locally, breaks deployed") is also a `/ms.fix`
  — use the `ms-ops-debugging` skill for the fastest-discriminating probe per failure class.
- **New requirement, and a checked baseline already exists** — a new GEARS "shall", a new
  endpoint, a new DB schema/migration, a new external integration, added to a product that
  already has a decomposed Feature Map → **`/ms.expand`**. Append the requirement to the
  existing PRD under a `## PRD Amendment N` heading and run `/ms.expand`; it decomposes only the
  delta into new Features without re-auditing the whole product.
- **New requirement, and no baseline exists yet** — the first PRD, or a change big enough to
  reshape the whole product → the full workflow starting at `/ms.pre-specter`.

> If unsure whether it's a new requirement: does it change *what the product promises*, or just
> *how correctly/nicely it already does it*? The former → `/ms.expand` (or `/ms.pre-specter` for
> a first-time/whole-product change). The latter → `/ms.fix`.

## Step 1: Size the change (decides ceremony, from existing rules)

Estimate the files this touches (AGENTS.md §7: modifying 3+ files in one task
needs user approval — the mini-plan below is how this track satisfies it):

- **Small (1–2 files)** → go straight to Step 2 (lightweight).
- **Medium (3+ files)** → **mini-plan first**:
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

**Hard-Bug Discipline** — when the cause isn't obvious after a first look, before
touching code:

1. **Reproduce + minimise**: get a red-capable command (failing test, curl script,
   CLI against a fixture) that reproduces the symptom the user actually described,
   then shrink it until every remaining element is load-bearing (removing any one
   turns it green). The minimal repro becomes the regression test.
2. **Hypothesise before instrumenting**: write 3-5 ranked, falsifiable hypotheses
   ("if X is the cause, changing Y makes it disappear") before testing any of
   them — single-hypothesis anchoring on the first plausible idea is the most
   common failure mode.
3. **One probe per prediction**: change one variable at a time; prefer a
   debugger/REPL breakpoint over logs; if logging, tag every debug line with a
   unique prefix (e.g. `[DEBUG-a4f2]`) so cleanup is one grep — never "log
   everything and grep". For performance bugs, baseline first (profiler, timing
   harness, query plan); logs are the wrong tool there.
4. **Fix at the correct seam**: write the regression test *before* the fix, at a
   seam that exercises the real bug pattern as it occurs at the call site (a
   single-caller unit test is the wrong seam if the bug needs multiple callers).
   If no correct seam exists, that itself is the finding — flag the architecture
   gap; a test at the wrong seam gives false confidence.
5. **Close out**: re-run the original un-minimised repro to confirm it no longer
   fires, strip all `[DEBUG-...]` instrumentation and throwaway harnesses, and
   record which hypothesis won in the commit message.

## Step 3: TAG for traceability (closes the fix-track Trackable gap)

Fixes must still be traceable — this is what an ungated quick-push would skip.

- **Correcting code that already has a TAG** → reuse that TAG; bump its
  `@UPDATED` (git-derived — the last commit that touched the file, never
  today's date) and, if behavior
  changed, note it.
- **New code with no governing SPEC** → assign a **FIX-id** TAG:
  `@CODE:FIX-<area>-<NNN>` (e.g. `@CODE:FIX-UPLOADS-003`), `@SPEC: (fix — no spec)`.
  Keep the chain block format identical to `/ms.implement`,
  `@STATUS: implemented`. The pre-commit backstop
  (`scripts/specter/check_tag_chain.py`) waives the `@SPEC` anchor for `FIX-*` ids but
  still requires the `@TEST` side:
  - **Behavioral fix** (Step 2 wrote/extended a test) → put the matching
    `@TEST:FIX-<area>-<NNN>` anchor in that test file.
  - **Presentational fix** (Step 2 skipped RED-GREEN) → declare it in the TAG
    block: `@TEST: (presentational — no test)`. This exact marker is what the
    backstop accepts in place of a test anchor; never use it on a behavioral
    change.

## Step 4: Lightweight docs (scale to size)

- **Always**: append a **one-line** entry to `docs/dev_daily.md` (what + why + TAG).
- **Skip** API-doc generation and README updates (those are for new features).
- For Medium (3+ files) changes, the dev_daily line should name each area touched.

## Step 5: Gate (same gate as everything else)

Run the **`local-ci`** subagent (lint → types → tests → build for affected areas;
reports pass/fail per gate, edits nothing). Fix any failure before proceeding.
This is the same gate contract `/ms.fin` enforces before publishing — uniformity
is the point.

## Step 6: Hand off

Commit (TAG id in the message) on a `fix/<short-name>` branch, then continue with
the existing flow: `/ms.fin` to push + open PR, then `/ms.merglease`. Committing
here is covered by the user's explicit `/ms.fix` invocation and the project
permission allowlist (AGENTS.md §7); ad-hoc commits outside this flow still ask.

`/ms.fix` deliberately does **not** write to `.specify/specter-run.jsonl` — the
run ledger tracks per-Feature cycle steps, and fixes are not Features. Fix-track
traceability lives in the TAG + the `docs/dev_daily.md` line (Step 4).

## Relationship to other commands

```
새 요구사항?
 ├ 예, 기존 baseline 있음 → /ms.expand → /ms.specter <새 Feature NNN>
 ├ 예, baseline 없음(최초/전면 재구성) → /ms.pre-specter → /ms.specter (Feature마다 반복)
 ├ 아직 요구사항이 아님(될지 실험/검증만) → spike 스킬 (타임박스, 머지 금지, findings note → PRD Amendment)
 └ 아니오 → /ms.fix (1-2 files: 경량 / 3+ files: mini-plan 먼저) → /ms.fin → /ms.merglease
```

`/ms.fix` is the **single, uniform track for all non-requirement changes** — it
replaces the ad-hoc "skip the workflow and just push" path, so even small fixes
keep a TAG and pass the gate.

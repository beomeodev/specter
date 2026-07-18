---
description: "Incremental PRD track — decompose a PRD amendment into new Features without re-auditing the whole product"
argument-hint: "[@docs/prd/PRD.md]"
---

# /ms.expand - Incremental PRD Expansion

Consume a new requirement appended to an **existing, already-decomposed** PRD, and extend
`docs/prd/feature-map.md` with only the new Features it requires — without regenerating the
Feature Map or re-auditing Features that were already checked.

This fills the gap between `/ms.fix` (no new requirement at all) and a full `/ms.pre-specter`
run (whole-product recomposition, re-audits every PRD). Use it when the product already has a
checked baseline and the user is adding a requirement, not starting over.

## What This Command Is Not

- It does not accept freeform or ad-hoc requirement text. The input is an **amendment appended
  to an existing PRD file**, following the heading convention below. This mirrors
  `/ms.featuremap`'s own refusal of freeform input — the PRD stays the single source of truth.
- It does not re-run `/ms.featuremap`, `/ms.codex-checklist`, or `/ms.verify` over the whole PRD
  set. It reads and audits only the newly appended amendment text.
- It does not edit or re-own any existing `## Feature NNN:` section or existing PRD Commitment
  Index row. If the amendment requires that, it stops and escalates to `/ms.pre-specter`.
- It does not weaken the Feature-Map bridge: `/ms.specify` still requires a checked Feature
  section, dual-agent verification, and Constitution Section IX, exactly as for any other
  Feature.

## Preconditions

An established baseline is required: `docs/prd/feature-map.checklist.md` must already be
`PASS`/`WARN`, and Constitution Section IX must already be established. Check with the
deterministic gate checker:

```bash
# self-heal: the runtime copy is project-local (never synced); refresh it from the synced template
install -D -m 0755 docs/templates/scripts/specter-gate.sh .specify/scripts/bash/specter-gate.sh
.specify/scripts/bash/specter-gate.sh
```

If the JSON `overall` is `MISSING` or `FAIL`, stop and point to the one-time setup instead:

```text
⛔ /ms.expand는 이미 존재하는 baseline 위에서만 동작합니다.

아직 baseline이 없습니다. 먼저 1회 PRD 셋업을 완료하세요:
  /ms.pre-specter @docs/prd/PRD.md [@docs/prd/another.md]

완료 후 PRD에 Amendment를 추가하고 /ms.expand를 다시 실행하세요.
```

## Usage

Append the new requirement to the existing PRD file under a top-level heading at the end of the
file:

```markdown
## PRD Amendment 1 — 2026-08-01

<the new requirement, in the PRD's normal prose/GEARS style>
```

Then run:

```bash
/ms.expand                          # auto-detect which PRD(s) changed
/ms.expand @docs/prd/PRD.md         # pin the amended PRD explicitly
```

## Execution Steps

### Step 0: Delta Detection + Append-Only Guard

1. Read `**Git Ref**` from `docs/prd/feature-map.checklist.md` (the commit SHA recorded at the
   last `/ms.verify` or `/ms.expand` audit). If this field is missing (an audit predating this
   field), stop and ask the user to run `/ms.verify` once to backfill it before `/ms.expand` can
   compute a delta.
2. Resolve the PRD file(s) to check: the `@`-attached path(s) if given, else every source PRD
   recorded in `docs/prd/feature-map.md`.
3. Compute the delta against the recorded Git Ref, restricted to the PRD documents themselves:
   ```bash
   git diff <recorded Git Ref> -- docs/prd/*.md ':!docs/prd/feature-map*.md' ':!docs/prd/codex/**' ':!docs/prd/checklists/**'
   ```
4. **Append-only guard**: the diff must contain **no removed or modified lines** — only added
   lines that form complete new `## PRD Amendment N — YYYY-MM-DD` sections at the end of a file.
   A mechanical check: any diff line starting with `-` (other than the `--- a/...` file header)
   means existing PRD text was changed or deleted, not purely appended.
   - If the diff contains any such removal/modification → **STOP**: this changes an existing
     commitment and is not an expansion.
     ```text
     ⛔ 기존 PRD 내용이 변경되었습니다. /ms.expand는 추가(append)만 처리합니다.

     이 변경은 기존 commitment를 바꾸므로 /ms.expand 범위가 아닙니다.
     다음 중 하나를 사용하세요:
       - 영향받는 Feature만 다시 검증: /ms.checklist <Feature NNN>
       - 전체 재구성: /ms.pre-specter @docs/prd/PRD.md [@docs/prd/another.md]

     Stopping now.
     ```
   - If the diff is empty → nothing to expand; report that and stop (no error).
5. Determine the amendment number N: the next integer after the highest `## PRD Amendment N`
   heading found in the diff, and after the highest `## Delta Reconciliation N` section already
   present in `docs/prd/feature-map.checklist.md`.
6. Extract **only** the new `## PRD Amendment N` section text for every downstream step. Do not
   re-read the full PRD.

**Session read policy**: per AGENTS.md §2 — reuse files already read this session; a fresh `Read` immediately before `Edit`/`Write` is still required.

### Step 1: Append-Only Map Extension

Decompose the amendment text into an extension of `docs/prd/feature-map.md`:

- **New PRD Commitment Index rows** for every commitment in the amendment, each with exactly one
  owning **new** Feature (decided 2026-07-18, audit #29: amendment commitments never attach to
  existing Features — an existing Feature's spec/checklist is already closed and no gate reopens
  it). Pure wording cleanups that add no testable behavior are not commitments at all — leave
  them out of the index. If unsure whether something is a commitment, it is one, and it gets a
  new Feature.
- **New `## Feature NNN:` sections**, numbered from the next free Feature number(s), written with
  the identical fixed template used by `/ms.featuremap` (Source PRDs, PRD references, In scope,
  Explicitly out of scope, Key decisions, Done criteria ending in "CI passes green").
- **DAG extensions**: add the new Feature(s) and their edges to the existing dependency graph.
  Depend on existing Features where the amendment builds on them.

Apply the same structural bars as `/ms.featuremap`:
- Single owner per commitment.
- No cycle in the extended DAG.
- Every out-of-scope item names a destination Feature.
- If a new Phase is created by this amendment, its last Feature carries the Phase's E2E scenario.

**Existing Feature sections and existing PRD Commitment Index rows are immutable in this
command.** If the amendment requires changing an existing Feature's ownership, scope, or an
existing index row, **STOP and escalate** with the same message as Step 0's guard failure — this
is not an expansion.

Write the extended `docs/prd/feature-map.md` (existing content unchanged except for the new
Commitment Index rows, new Feature sections, and DAG extension).

### Step 2: Codex Delta Checklist (Background)

Same contract as `/ms.codex-checklist`, scoped to the amendment only:

- The prompt embeds **only the extracted amendment text** inline — do not have Codex read the
  full PRD set or `docs/prd/feature-map.md`.
- IDs continue the existing C-numbering (read the highest `C###` already used in
  `docs/prd/codex/checklist.md` or any prior `checklist-delta-*.md`, and start from the next
  integer).
- Output: `docs/prd/codex/checklist-delta-N.md`, same table structure as
  `docs/prd/codex/checklist.md`.
- Execution is always background, same as `/ms.codex-checklist`.
- **This artifact is consumed at Step 3** — the delta verify joins on it; it is never
  fire-and-forget.

### Step 3: Delta Verify (Foreground)

**Join point (2026-07-18 audit #5)**: before auditing, wait for Step 2's
`docs/prd/codex/checklist-delta-N.md` to exist, non-empty, with the expected table structure —
then treat its items as audit inputs: every delta C-item must be either covered by the new
Features or explicitly dispositioned in the reconciliation section below. If the file has not
appeared, apply the `specter-agent-protocols` §3 protocol (retry once, salvage from markers);
if Codex still produced nothing, apply the §2 Degrade Rule — proceed host+Antigravity only,
cap the result at `WARN`, and record `Codex: UNAVAILABLE (<reason>)` in the reconciliation
section. (Without this join, the dual-agent guarantee silently degrades to a single agent —
and the Antigravity-unavailable degrade below would leave zero independent verifiers.)

Host + Antigravity audit, scoped to only:

(a) every amendment commitment has exactly one owning (new) Feature;
(b) the new Features do not overlap any existing Feature's ownership;
(c) the extended DAG has no cycle;
(d) every deferred/out-of-scope item in the amendment has a destination Feature.

Invoke Antigravity in the foreground, same pattern as `/ms.verify` Step 0.2, with a prompt scoped
to the amendment text, the new Feature sections, and the DAG extension only (not the whole
product). Wait for it to finish before continuing.

- **Antigravity unavailable** (after one retry): apply the Degrade Rule from
  `specter-agent-protocols` §2 — run the audit Codex-only, force the result to at most `WARN`,
  and record `Antigravity: UNAVAILABLE (<reason>)` in the reconciliation section below.

Append to `docs/prd/feature-map.checklist.md` (do not touch prior sections):

```markdown
## Delta Reconciliation N — YYYY-MM-DD

**Amendment**: PRD Amendment N (<source PRD path>)
**New Features**: Feature NNN, ...
**Antigravity**: PASS | WARN | FAIL | UNAVAILABLE (<reason>)

| Category | Check | Result | Evidence | Required Fix |
| --- | --- | --- | --- | --- |
```

Then update the top-level `**Result**` (do not downgrade an existing PASS/WARN/FAIL to something
better than what this reconciliation found — the overall Result is the worse of the prior Result
and this reconciliation's Result), and recompute:

```bash
sha256sum docs/prd/feature-map.md   # -> Feature Map SHA256
git rev-parse HEAD                  # -> Git Ref
```

Write both into the checklist header fields, exactly like `/ms.verify` Step 5.

### Step 4: Constitution Diff Check

Scan only the amendment text for durable, cross-Feature rule material (the same categories
`/ms.constitution` Step 3 promotes: product-wide roles/permissions, security/privacy/audit
rules, performance/reliability targets, cross-feature data/integration contracts, required or
forbidden technologies, differing test/lint/release requirements).

- If nothing durable is found (the common case): no-op. Do not touch Section IX.
- If durable material is found and does not conflict with existing Section IX: append it under
  the appropriate existing sub-heading (do not rewrite Section IX from scratch).
- If it conflicts with existing Section IX and cannot be resolved from the amendment text alone:
  stop and ask the user to choose, using the same rules as `/ms.constitution` Step 4. Do not
  silently pick one.

Do not promote Feature-local content (one Feature's endpoints, UI copy, migration detail) to
Section IX, exactly as `/ms.constitution` Step 3 already forbids.

### Step 5: Report (Korean) And Hand Off

```text
🧩 /ms.expand — PRD Amendment N 반영 결과

📄 확장된 Feature Map: docs/prd/feature-map.md (신규 Feature: NNN, ...)
📄 Delta 감사: docs/prd/feature-map.checklist.md (## Delta Reconciliation N)
📄 Codex delta checklist: docs/prd/codex/checklist-delta-N.md
🏛️ Constitution: 변경 없음 | Section IX에 <항목> 추가됨

상태: ✅ PASS | ⚠️ WARN | ⛔ FAIL

🎯 다음 단계: /ms.specter <새 Feature NNN>
```

If the result is `FAIL`, do not suggest `/ms.specter`; direct the user to fix the reported issues
and rerun `/ms.expand`.

## Next Command

After `/ms.expand` passes (`PASS`/`WARN`), start the per-Feature cycle on the first new Feature:

```bash
/ms.specter <new Feature NNN>
```

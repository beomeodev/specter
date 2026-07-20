---
description: "Drive one Feature through the full per-Feature cycle with clarify as the only unconditional human stop"
argument-hint: "<Feature NNN> [@docs/prd/<PRD>.md] [@docs/prd/feature-map.md] [--raise-audit-tier T2|T3]"
---

# /ms.specter - Per-Feature Cycle Conductor

Run a single Feature through the entire SPECTER per-Feature cycle automatically.
The conductor invokes each `/ms.*` step in order, reads each step's PASS / WARN /
FAIL verdict, and advances on its own. The only always-mandatory human stop is
`/ms.clarify`; `/ms.review` adds a conditional stop (explicit user ack of the
migration rollback analysis, Step 6.6b) when the Feature's diff includes
schema/data migrations. T3 residual WARNs, T3 single-reviewer environmental
degrades, destructive changes, and other explicitly high-stakes or irreversible
operations also require conditional human acknowledgment. The run ends at
`/ms.review` (publishing is left to `/ms.fin`).

`/ms.specter` does **not** replace or weaken any gate. Every underlying command
still runs in full and still writes its own audit artifact. The conductor only
reads those verdicts and decides whether to continue, collect a warning, or stop.

## What This Command Is Not

- It does not run the one-time PRD setup (`/ms.featuremap`, `/ms.featuremap-checklist`,
  `/ms.pre-verify`, `/ms.constitution`). Those must already be complete. The conductor
  covers only the repeatable per-Feature cycle.
- It does not commit, push, tag, or open a PR. The run stops at `/ms.review`.
  Publishing stays with `/ms.fin`, whose `git` actions are permission-gated.
- It does not auto-answer `/ms.clarify`. Clarification is the human's call.
- It does not pass any gate-weakening flag (e.g. `--skip-codex`). Codex and
  Antigravity verification always run.
- It does not classify or infer `audit_tier`. It reads a deterministic,
  input-hash-bound receipt and may pass only a user-requested upward override.

## Usage

**Recommended form** — the bare Feature number. The conductor resolves the Feature
Map at its conventional path (`docs/prd/feature-map.md`) and the PRDs it records,
so nothing needs to be attached:

```bash
/ms.specter 006
/ms.specter 6번 피처 진행해
```

- The Feature number is **freeform** — `006`, `6`, `Feature 006`, `006 진행해`,
  `6번 피처 돌려줘` all resolve to Feature 006. Surrounding words are ignored.
- The one hard requirement is that a resolvable Feature number is present. It
  feeds `/ms.checklist`, `/ms.verify`, and `/ms.specify`.

**`@`-attachments — only for non-conventional paths.** Attach a PRD or the
Feature Map with `@` only when it does **not** live at the conventional location
(`docs/prd/*.md`, `docs/prd/feature-map.md`):

```bash
/ms.specter @docs/prd/PRD.md @docs/prd/feature-map.md 006
```

Attaching the full PRD injects its entire content into context on **every**
invocation and every conductor restart — one audited project spent ~1.05M
tokens on this pattern across a single Feature Map. The Feature Map + each
Feature's `### PRD references` already scope exactly which PRD sections
`/ms.checklist` and `/ms.specify` need, so attaching the whole PRD file rarely
adds anything the conventional-path form doesn't already resolve on its own.

## The Cycle

```text
/ms.checklist        → per-Feature readiness gate          [local]
/ms.verify     → Codex + Antigravity, foreground     [parallel]
/ms.specify          → spec.md from the Feature section     (section injected)
/ms.clarify          → 🔴 human Q&A, then resume
/ms.plan             → plan.md + reality verification
/ms.tasks            → tasks.md + TAG IDs
/ms.analyze          → spec ↔ plan ↔ tasks consistency      [foreground]
/ms.implement        → TDD all phases                       (--to-end)
/ms.review           → adversarial code gate                [foreground]
```

## Conductor Policy (applies after every step)

- **PASS** → advance to the next step.
- **WARN** → advance, but record the warning in the run's collected-warnings list
  and surface it in the final report, but only after any receipt-required human
  acknowledgment is satisfied. Never silently discard a WARN.
- **FAIL** → stop immediately. Report the failing step, its audit file, and the
  blocking fixes. Do not continue, and do not auto-fix unless the step itself
  defines a mechanical auto-fix (see `/ms.plan` below).
- **`/ms.clarify`** → always hand control to the human. Ask the questions the
  command produces (Korean), wait for answers, apply them, then resume.
- **Step entry** → no step runs unless every earlier step in the sequence has a
  PASS/WARN ledger entry for this Feature (Step 0.5's step-order invariant). A
  conductor never skips forward silently.

This is the cycle-level expression of "autonomy only inside the control fence":
the conductor moves on its own only through mechanically valid PASS/WARN
receipts and pauses at every policy-required human boundary.

Verdicts are read **mechanically** — from `specter-gate.sh` JSON output and the
Layer-3 aggregation receipts (`specter-agent-protocols` §7), never inferred or
re-weighed from report prose. The conductor follows the script's verdict; it
does not interpret it.

## Execution Steps

### Step 0: Resolve The Feature And Preconditions

1. Parse the input. It is freeform: it may contain `@`-attached file paths and a
   Feature number, in any order.
   - **`@`-attached paths**: classify each. A path matching `*feature-map*.md` is
     the Feature Map; any other `docs/prd/*.md` is a source PRD (there may be
     several). Use these attached paths as authoritative.
   - **Feature Map fallback**: if no Feature Map was attached, use
     `docs/prd/feature-map.md`.
   - **PRD fallback**: if no PRD was attached, use the Source PRDs recorded in the
     Feature Map for the resolved Feature.
   - **Feature number**: extract the Feature identifier from anywhere in the
     remaining text. `006`, `6`, `Feature 6`, `feature-006`, `006 진행해`, and
     `6번 피처 돌려줘` all resolve to Feature 006. Ignore surrounding words
     (commands, particles, instructions). Only refuse if **no** Feature identifier
     can be found at all (e.g. `진행해` with no number); then ask which Feature to
     run. Never guess a number that is not present in the input.
2. Confirm the per-Feature cycle can start by running the deterministic gate
   checker instead of manually re-deriving these facts:
   ```bash
   # self-heal: the runtime copy is project-local (never synced); refresh it from the synced template
   install -D -m 0755 docs/templates/scripts/specter-gate.sh .specify/scripts/bash/specter-gate.sh
   .specify/scripts/bash/specter-gate.sh
   ```
   Also install and probe the synced audit-tier capability before any Feature
   station runs:
   ```bash
   install -D -m 0755 scripts/specter/classify_audit_tier.py .specify/scripts/python/classify_audit_tier.py
   install -D -m 0644 docs/templates/audit-tier-policy.json .specify/policies/audit-tier-policy.json
   python3 .specify/scripts/python/classify_audit_tier.py \
     --policy .specify/policies/audit-tier-policy.json version
   ```
   A missing half of this pair or an incompatible contract is a partial-sync
   FAIL, not a reason to assume T1. Fully legacy projects may start only through
   the documented legacy T2 compatibility path until `/ms.sync` installs both.
   This mechanically checks that the Feature Map exists, `docs/prd/feature-map.checklist.md`
   is `Result: PASS` or `WARN` and its SHA256 matches the current Feature Map, and Constitution
   Section IX is established. If the JSON `overall` field is `MISSING` or `FAIL`, stop and tell
   the user to complete the one-time PRD setup first (use `reasons[]` to explain what is
   missing):
   ```text
   ⛔ /ms.specter는 per-Feature 사이클만 자동화합니다.

   먼저 1회 PRD 셋업을 완료하세요 (한 번에: /ms.pre-specter @docs/prd/PRD.md):
     /ms.featuremap @docs/prd/PRD.md [...]
     /ms.featuremap-checklist @docs/prd/PRD.md [...]
     /ms.pre-verify
     /ms.constitution

   완료 후 다시 실행: /ms.specter <Feature NNN>
   ```
3. Read the Feature Map (the attached path, else `docs/prd/feature-map.md`) and
   extract the full `## Feature NNN:` section for the resolved Feature. Keep it
   verbatim — it is the required input for `/ms.specify` in Step 3.
4. Initialize an empty collected-warnings list for this run.
5. **Resume from the run-state ledger** (bookkeeping only — gates still come from the audit
   artifacts, never from this file). If `.specify/specter-run.jsonl` exists, read its lines
   filtered to `cycle: "feature"` and this Feature's number. The step sequence is
   `checklist → verify → specify → clarify → plan → tasks → analyze → implement → review`.
   **Legacy step alias** (pre-2026-07-19 ledgers): treat a `cycle: "feature"` entry named
   `agent-verify` as `verify`.
   Take, per step name, the **last** matching line (later entries supersede earlier ones) and
   find the first step in the sequence that has no `PASS`/`WARN` entry yet — resume the cycle
   there instead of restarting at Step 1, and announce the resume point:
   ```text
   ↩️ 이전 실행 이어서 진행: Feature NNN — <step>부터 재개 (이전 단계는 이미 PASS/WARN 기록됨)
   ```
   If the ledger is missing, unreadable, or every step already lacks a matching entry, start
   normally at Step 1 — a missing/corrupt ledger never blocks the run, it only loses the resume
   shortcut. Fail-open here means "start from the beginning", never "enter a mid-sequence step
   unverified".

   **Staleness guard on resume**: a prior `PASS`/`WARN` entry counts only while its artifact is
   still current. After computing the resume point, run the deterministic gate checker
   (`.specify/scripts/bash/specter-gate.sh <NNN>`); if it reports a stale SHA or failed artifact
   for an already-"passed" step (e.g. the checklist was rewritten after its verify entry),
   resume from that earlier step instead — a ledger entry is a bookmark, never a substitute for
   the artifact check. For freshness bindings the legacy checker does not cover, re-run the
   station's aggregation read-only: when resuming past `analyze`, run
   `.specify/scripts/bash/specter-gate.sh aggregate analyze specs/<id>` (no `--ledger`) — a
   `FAIL` receipt means `tasks.md` changed after the analyze reports were written, so the
   `analyze` entry is stale and the cycle resumes there.

   For every resume point after checklist, validate
   `.specify/audit-tiers/feature-NNN.json`. Then require the phase appropriate
   to the next station (`feature-map` for verify, `pre-implement` for analyze,
   `diff` for review). A missing/stale receipt reruns the corresponding
   deterministic classification boundary; it never falls back to T1. Compare
   `effective_tier` to all prior ledgered tier receipts and stop on any
   decrease—the classifier is the only component allowed to calculate the
   monotonic maximum.

   **Step-order invariant (no silent skips).** The same per-step last-entry-wins data enforces
   order, not just the resume shortcut: before executing any step of the sequence, every earlier
   step must already have a `PASS`/`WARN` ledger entry for this Feature. If one is missing, do
   not execute the later step — go back to the **first** missing step and run the cycle from
   there, announcing it:
   ```text
   ⚠️ 단계 순서 가드: <목표 step> 진입 전 선행 <누락 step> 기록 없음 → <누락 step>부터 실행
   ```
   When the **user explicitly asks** to start at a specific step ("plan부터"), still check the
   earlier entries; if any are missing, report exactly which and get one confirmation before
   honoring the instruction — user discretion is respected, only the conductor's *silent* skip
   is forbidden. This guard enforces order only; it never reads, weakens, or overrides any
   gate's verdict (§10 identity rule).
6. **Self-heal the exploration graph (never blocks).** If the `graphify` binary is
   available, run `graphify . --code-only --no-viz --update` (AST-only, seconds, no
   API cost) so this cycle's structural queries see the current tree. If the binary
   is missing, append `graphify: UNAVAILABLE — structural exploration falls back to
   rg/find (setup: /ms.init Step 2.9)` to the collected-warnings list and continue.
   Graph freshness is an accelerator concern, never a gate verdict — this item can
   produce a WARN, never a FAIL.
7. **State the context manifest.** After the reads above, tell the rest of the run what is
   already loaded so downstream steps don't re-read it:
   ```text
   📎 이번 세션에 이미 로드됨: constitution.md, feature-map.md §Feature NNN, <attached PRD refs>
   ```
   Every subsequent step in this cycle applies the session read policy against this manifest: if
   a file named here was already read and has not changed since (no edit, no user notice), reuse
   it instead of re-reading. The one exception is the harness's own requirement of a fresh `Read`
   immediately before `Edit`/`Write` on a file — always satisfy that even if the content is
   already in context.

### Step 1: `/ms.checklist`

Run `/ms.checklist <NNN>`. Read `docs/prd/checklists/feature-NNN.checklist.md`.

- PASS → continue.
- WARN → record the warning, continue.
- FAIL → stop. Report the audit's Blocking Fixes and tell the user to fix the
  Feature section, then rerun `/ms.specter <NNN>`.

Read the classifier receipt written by this command and add its
`effective_tier`, `reasons`, policy version/hash, and receipt hash to run state.
If the user supplied `--raise-audit-tier`, pass it only to the classifier's
upward-only interface. Never pass it as prose to an author or reviewer.

### Step 2: `/ms.verify` (foreground, parallel)

Run `/ms.verify <NNN>`. Codex and Antigravity run in the foreground in
parallel and complete before this step returns (no background polling). If
either agent fails to write its `*-verify.md` report, the underlying command
retries once and then stops; surface that failure to the user rather than
proceeding.

Read the station verdict from the Layer-3 aggregation receipt the command
produced (`specter-gate.sh aggregate verify NNN`) — not by weighing the
two reports yourself:

- Receipt verdict PASS → continue.
- Receipt verdict WARN → record it and continue only when
  `warn_ack_required` is false or `warn_ack_satisfied` is true. If required,
  pause for explicit human acknowledgment and let `/ms.verify` record it.
- Receipt verdict FAIL → stop. Report the receipt's `reasons[]` and the
  failing report's findings verbatim.

### Step 3: `/ms.specify` (inject the Feature section)

Run `/ms.specify` with the Feature section extracted in Step 0.3 pasted as the
input. The hard gates in `/ms.specify` (Feature Map present, global + per-Feature
checklists PASS/WARN, dual-agent verification present, Constitution Section IX)
are already satisfied by Steps 0–2, so the command proceeds and writes
`specs/<id>/spec.md`.

If `/ms.specify` still refuses (an unexpected gate failure), stop and report it.
Read the new spec-phase receipt and immediately adopt any higher effective tier.

### Step 4: `/ms.clarify` — 🔴 human stop

Run `/ms.clarify`. This is the one always-mandatory human interaction;
migration, T3 WARN/degrade, destructive, and high-stakes acknowledgments are
conditional stops.

- Present every clarification question the command raises, in Korean, with its
  A/B/C options.
- Wait for the user's answers. There may be several question rounds; keep going
  until all ambiguities are resolved and `spec.md` is updated.
- Then resume automatically with Step 5. Do not stop and ask the user to run the
  next command manually — the conductor continues.

If `/ms.clarify` finds no ambiguity, continue immediately.
After any spec update, read the refreshed spec-phase tier receipt and adopt an
escalation before planning.

### Step 5: `/ms.plan`

Run `/ms.plan`. This step runs its own Reality Verification, which has a built-in
distinction the conductor must honor:

- **Mechanical reality FAIL** (stale path, migration index drift, typo in an
  existing convention) → `/ms.plan` auto-fixes it and continues. Let it.
- **Design-level reality FAIL** (missing schema column/table, auth/status
  semantics differ, new dependency conflicts the baseline, requires amending a
  clarified requirement) → `/ms.plan` stops and asks the user. The conductor
  stops here too and surfaces that question. Do not auto-resolve a design-level
  mismatch.

On a clean plan → continue (record any WARN). Read the plan-phase receipt and
immediately adopt any escalation.

### Step 6: `/ms.tasks`

Run `/ms.tasks`. On success → continue. A duplicate-`@SPEC`-TAG failure is a hard
stop (mechanical fix required); report it.

### Step 7: `/ms.analyze` (foreground)

Run `/ms.analyze` (foreground default; Codex and Antigravity run inline, no
`--background`). Read its verdict.

- PASS → continue.
- WARN → record the warning and continue only after the receipt's WARN policy is
  satisfied. A T3 acknowledgment is explicit human input; collecting the
  warning for the final report is not acknowledgment.
- FAIL → stop. Report the drift / coverage gap.

### Step 8: `/ms.implement --to-end`

Run `/ms.implement --to-end`. This implements every pending phase in `tasks.md`
in one run, TDD by default. Without `--to-end` the command would stop after the
first phase, so the conductor always passes it.

If implementation hits a blocker it cannot resolve within scope (e.g. an
unverifiable unstable API), the command stops and surfaces it; the conductor
stops too.

`/ms.analyze` and `/ms.implement` both validate the pre-implementation receipt;
the conductor cannot pass a weaker tier or skip the repeat check.

### Step 9: `/ms.review` (adversarial, foreground)

Run `/ms.review`. The dual-agent review always runs in adversarial mode and the
executable code gates (lint, typecheck, tests, build) run regardless.

- PASS → continue to the final report.
- WARN → record the warning and continue only after every tier, migration, and
  high-stakes acknowledgment reported by `/ms.review` is satisfied.
- FAIL / NOT READY → stop. Report the failing gates and findings. The conductor
  does not auto-fix; fixes belong to `/ms.implement --mode=refactor` or the main
  conversation.

### Step 10: Final Report

When the run reaches the end (Step 9 PASS/WARN) or stops early, report in Korean:

```text
🛰️ /ms.specter — Feature NNN 사이클 결과

진행: checklist → verify → specify → clarify → plan → tasks → analyze → implement → review
상태: ✅ review까지 완료  |  ⛔ <단계>에서 정지

감사 등급: <effective_tier> (<Routine|Standard|High-Risk>)
정책: <policy version> / <policy hash>
분류 근거:
- <receipt reasons[] 전부>

⚠️ 수집된 경고 (WARN):
- <step>: <요약> (<audit 파일>)
- ...
(없으면 "없음")

🎯 다음 단계:
- 정상 완료 시: /ms.fin  (docs 동기화 → commit → push → PR; git 작업은 권한 승인 필요)
- 정지 시: 위 Blocking Fixes 반영 후 해당 단계부터 재개
```

Always list every collected WARN. A clean automated run with unread warnings is
exactly the silent-quality-loss failure mode this report exists to prevent.

## Stop Conditions Summary

| Where | Trigger | Conductor action |
| --- | --- | --- |
| any step | `Result: FAIL` | stop, report audit + blocking fixes |
| `/ms.clarify` | always | human Q&A, then resume |
| `/ms.review` | migration in diff (Step 6.6b) | stop, present rollback analysis, wait for explicit user ack |
| any tiered station | T3 residual WARN or one-agent degrade | stop, record receipt-bound human acknowledgment |
| any tiered station | stale/missing/incompatible receipt | stop or rerun deterministic classification; never assume T1 |
| `/ms.plan` | design-level reality FAIL | stop, surface the design question |
| `/ms.verify` | agent write failure after retry | stop, report the failing agent |
| `/ms.implement` | in-scope blocker | stop, surface the blocker |
| end of `/ms.review` | PASS/WARN | finish, recommend `/ms.fin` |

## Error Handling

- **Missing argument** → refuse; ask which Feature to run.
- **Precondition missing** (no Feature Map / global gate / Section IX) → stop with
  the one-time-setup message in Step 0.
- **Underlying command error** → stop at that step and report its raw error. Do
  not skip a failed step to keep the cycle moving.

## Next Command

After `/ms.specter` finishes at `/ms.review` with PASS/WARN, run `/ms.fin` to sync
docs, commit, push, and open the PR.

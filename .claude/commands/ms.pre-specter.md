---
description: "Drive the one-time PRD setup (featuremap → featuremap-checklist → pre-verify → constitution) as a single automated pre-Feature cycle"
argument-hint: "[@docs/prd/PRD.md] [@docs/prd/another.md]"
---

# /ms.pre-specter - One-Time PRD Setup Conductor

Run the one-time PRD setup phase as a single cycle. The conductor invokes each
`/ms.*` setup step in order, reads each step's verdict or artifact, and advances
on its own — automatically through PASS/WARN, stopping only on FAIL. It surfaces
(but never auto-resolves) the conditional questions the underlying commands
raise: the PRD-set confirmation in `/ms.featuremap` and the baseline-overwrite or
durable-rule conflict stops in `/ms.constitution`. The run ends once the
Constitution Section IX baseline is established and the per-Feature cycle is
ready to begin.

This is the **pre-Feature** counterpart to `/ms.specter`. Where `/ms.specter`
drives one Feature through `checklist → review`, `/ms.pre-specter` drives the
project through `featuremap → featuremap-checklist → pre-verify → constitution`.

`/ms.pre-specter` does **not** replace or weaken any gate. Every underlying
command still runs in full and still writes its own audit artifact. The
conductor only reads those verdicts and decides whether to continue, collect a
warning, or stop.

## What This Command Is Not

- It does not run the per-Feature cycle (`/ms.checklist`, `/ms.verify`,
  `/ms.specify`, …). That is `/ms.specter`'s job. This conductor stops once the
  one-time setup is complete and hands the first Feature to `/ms.specter`.
- It is not the track for adding a requirement to an **already-established** baseline.
  Re-running the whole PRD set regenerates the Feature Map and may overwrite existing
  decomposition (see Step 0's re-run confirmation below). For an incremental
  requirement appended to an existing PRD, use `/ms.expand` instead — it decomposes only
  the delta and never re-audits Features that were already checked.
- It does not commit, push, tag, or open a PR. `/ms.constitution` may modify
  `AGENTS.md` and `README.md` in the working tree; publishing those stays with
  `/ms.fin`, whose `git` actions are permission-gated.
- It does not auto-overwrite an existing Constitution baseline. `/ms.constitution`
  stops and asks for intent, and Step 0 confirms a re-run before regenerating.
- It does not pass any gate-weakening flag. Codex and Antigravity verification
  always run.

## Usage

**Recommended form** — the bare command. The conductor looks for likely PRDs
under `docs/prd/` and **confirms the full PRD set with the user before
proceeding**. It never guesses PRD content:

```bash
/ms.pre-specter
```

**`@`-attachments — only for non-conventional paths.** Attach a PRD with `@`
only when it does **not** live under `docs/prd/`:

```bash
/ms.pre-specter @path/outside/docs/prd/PRD.md
```

Attaching a PRD that already lives at its conventional path adds nothing the
bare form doesn't already resolve, and injects the full PRD content into
context on every conductor restart. If several PRDs already live under
`docs/prd/`, the bare form still finds and confirms all of them.

## The Cycle

```text
/ms.featuremap             → docs/prd/feature-map.md (Feature DAG)   [featuremap-author subagent]
/ms.featuremap-checklist   → docs/prd/featuremap-checklist.md       [featuremap-checklist-author subagent]
/ms.pre-verify             → docs/prd/feature-map.checklist.md (PASS/WARN/FAIL)
                             (Codex + Antigravity dual L2, foreground)
/ms.constitution           → Section IX + AGENTS.md + README         [once]
```

`/ms.featuremap` and `/ms.featuremap-checklist` both read **only the PRD set**
and are independent of each other, so their two authoring subagents may be
dispatched concurrently. `/ms.pre-verify` is the join point: it requires both
`docs/prd/feature-map.md` and `docs/prd/featuremap-checklist.md`.

## Conductor Policy (applies after every step)

- **PASS** → advance to the next step.
- **WARN** → advance, but record the warning in the run's collected-warnings list
  and surface it in the final report. Never silently discard a WARN.
- **FAIL** → stop immediately. Report the failing step, its audit file, and the
  blocking fixes. Do not continue, and do not auto-fix.
- **conditional command stop** → when an underlying command raises its own
  question (PRD-set confirmation, baseline overwrite, durable-rule conflict),
  surface it to the human and wait. Never auto-resolve it.

This is the cycle-level expression of "autonomy only inside the control fence":
the conductor moves on its own through PASS/WARN and stops on FAIL; the only human
turns are the conditional questions the underlying commands raise.

Verdicts are read **mechanically** — from `specter-gate.sh` JSON output and the
Layer-3 aggregation receipts (`specter-agent-protocols` §7), never inferred or
re-weighed from report prose. The conductor follows the script's verdict; it
does not interpret it.

## Execution Steps

### Step 0: Resolve The PRD Set And Preconditions

1. Parse the input. Classify each `@`-attached `docs/prd/*.md` path as a source
   PRD (there may be several). Use these attached paths as authoritative.
   - **PRD fallback**: if no PRD was attached, look under `docs/prd/` for likely
     PRDs and confirm the full set with the user. If none can be found or
     confirmed, stop and ask for the PRD path. Never guess PRD content.
   - If no PRD exists yet anywhere (not just unattached — genuinely not yet written),
     the `prd-authoring` skill is the recommended pre-step for co-authoring one with
     the user before running this command.
2. Detect a prior setup (re-run) with the deterministic gate checker instead of
   re-deriving the facts from prose:
   ```bash
   # self-heal: the runtime copy is project-local (never synced); refresh it from the synced template
   install -D -m 0755 docs/templates/scripts/specter-gate.sh .specify/scripts/bash/specter-gate.sh
   .specify/scripts/bash/specter-gate.sh
   ```
   If **both** `global_result_ok` **and** `constitution_section_ix_established`
   are true in its JSON output, this is a re-run that will regenerate the
   Feature Map and may overwrite durable rules. Stop and confirm intent before
   proceeding (if the script is missing — pre-`/ms.init` state — fall back to
   reading `docs/prd/feature-map.checklist.md`'s `Result` line directly):
   ```text
   ⚠️ 이미 1회 PRD 셋업이 완료된 프로젝트입니다.

   /ms.pre-specter를 다시 실행하면 Feature Map을 재생성하고, Constitution
   베이스라인 갱신을 시도합니다. 기존 분해/규칙을 덮어쓸 수 있습니다.

   계속할까요? (다시 셋업) / 취소 (개별 명령으로 일부만 갱신)
   ```
   On a fresh project (no established baseline), proceed without asking.
3. Initialize an empty collected-warnings list for this run.
4. **Resume from the run-state ledger** (bookkeeping only — gates still come from the audit
   artifacts, never from this file). If `.specify/specter-run.jsonl` exists, read its lines
   filtered to `cycle: "pre"`. The step sequence is
   `featuremap → featuremap-checklist → pre-verify → constitution`. **Legacy step aliases**
   (pre-2026-07-19 ledgers): treat `codex-checklist` as `featuremap-checklist` and a
   `cycle: "pre"` entry named `verify` as `pre-verify`. Take, per step name, the **last**
   matching line (later entries supersede earlier ones) and find the first step in the sequence
   that has no `PASS`/`WARN` entry yet (legacy `featuremap-checklist`/`codex-checklist` entries
   may record `PENDING` — treat a `PENDING` entry **with its artifact present**
   (`docs/prd/featuremap-checklist.md`, legacy `docs/prd/codex/checklist.md`, non-empty) as
   satisfied for resume purposes; a `PENDING` entry without the artifact counts as "not yet
   done") — resume the cycle there instead of restarting at Step 1, and announce the
   resume point:
   ```text
   ↩️ 이전 실행 이어서 진행: <step>부터 재개 (이전 단계는 이미 PASS/WARN 기록됨)
   ```
   If the ledger is missing, unreadable, or every step already lacks a matching entry, start
   normally at Step 1 — a missing/corrupt ledger never blocks the run, it only loses the resume
   shortcut. Fail-open here means "start from the beginning", never "enter a mid-sequence step
   unverified".

   **Staleness guard on resume**: a prior `PASS`/`WARN` entry counts only while its artifact is
   still current. After computing the resume point, run the deterministic gate checker
   (`.specify/scripts/bash/specter-gate.sh`); if it reports a stale SHA or failed artifact for
   an already-"passed" step (e.g. the Feature Map was rewritten after its verify entry), resume
   from that earlier step instead — a ledger entry is a bookmark, never a substitute for the
   artifact check.

   **Step-order invariant (no silent skips).** The same per-step last-entry-wins data enforces
   order, not just the resume shortcut: before executing any step of the sequence, every earlier
   step must already have a `PASS`/`WARN` entry (`featuremap-checklist`'s `PENDING` counts as
   satisfied when its artifact exists — same artifact rule as the resume shortcut; without the
   artifact it counts as "not yet done"). If one is missing, do not execute the later step — go back to the **first**
   missing step and run the cycle from there, announcing it:
   ```text
   ⚠️ 단계 순서 가드: <목표 step> 진입 전 선행 <누락 step> 기록 없음 → <누락 step>부터 실행
   ```
   When the user explicitly asks to start at a specific step, still check the earlier entries;
   if any are missing, report exactly which and get one confirmation before honoring the
   instruction — user discretion is respected, only the conductor's *silent* skip is forbidden.
   This guard enforces order only; it never reads, weakens, or overrides any gate's verdict
   (§10 identity rule).
5. **State the context manifest.** After the reads above, tell the rest of the run what is
   already loaded so downstream steps don't re-read it:
   ```text
   📎 이번 세션에 이미 로드됨: <attached/resolved PRD paths>
   ```
   Every subsequent step in this cycle applies the session read policy against this manifest: if
   a file named here was already read and has not changed since (no edit, no user notice), reuse
   it instead of re-reading. The one exception is the harness's own requirement of a fresh `Read`
   immediately before `Edit`/`Write` on a file — always satisfy that even if the content is
   already in context.

### Step 1: `/ms.featuremap` (decompose the PRDs)

Run `/ms.featuremap` with the resolved PRD set. It writes
`docs/prd/feature-map.md`: the PRD Commitment Index, single-owner Feature slices,
and the dependency DAG.

- If `/ms.featuremap` cannot find or confirm the PRD set, it stops and asks. The
  conductor stops too — answer the PRD question, then rerun.
- If it cannot produce a Feature Map that satisfies its own structural bars
  (every commitment owned by exactly one Feature, no DAG cycle, every Phase's
  last Feature carries an E2E scenario), it surfaces the problem. Stop and report
  it; do not proceed to verification with a malformed map.
- On a written `docs/prd/feature-map.md` → continue.

### Step 2: `/ms.featuremap-checklist` (PRD-only, isolated subagent)

Run `/ms.featuremap-checklist` with the same PRD set. It dispatches the
**featuremap-checklist-author** subagent (PRD-blind to the Feature Map); since
Step 1's featuremap-author also reads only the PRDs, the conductor may
dispatch both subagents concurrently and join here.

The conductor must ensure the artifact lands before Step 3:

- `docs/prd/featuremap-checklist.md` exists, non-empty, `**Mode**: prd-only`
  (the command's own Step 2 deterministic check).
- If the author fails after its one retry, stop and report the failure rather
  than running `/ms.pre-verify` against a missing independent baseline.

### Step 3: `/ms.pre-verify` (global gate; three-layer)

Run `/ms.pre-verify`. It runs the Layer-1 structural gate, then Codex and
Antigravity in the foreground as independent Layer-2 global auditors (each
writes its own SHA-bound verdict), then computes the canonical
`docs/prd/feature-map.checklist.md` `**Result**` mechanically via
`specter-gate.sh aggregate pre-verify`.

Read the `Result`:

- **PASS** → continue.
- **WARN** → record the warning, continue.
- **FAIL** → stop. Report the audit's blocking findings (structural defect,
  uncovered PRD commitment, ownership conflict, stale/failed agent report).
  Fix `docs/prd/feature-map.md` and rerun `/ms.pre-specter` (or rerun
  `/ms.pre-verify` directly after the fix).
- If `/ms.pre-verify` stops because `docs/prd/featuremap-checklist.md` is
  missing, return to Step 2 and ensure the baseline artifact is present, then
  retry.

### Step 4: `/ms.constitution` (establish the baseline; once)

Run `/ms.constitution`. Its hard gate (global Feature Map audit must be
PASS/WARN) is already satisfied by Step 3, so it extracts durable project-wide
constraints into Section IX and updates `AGENTS.md` and the root `README.md`.

Honor its own stops — do not auto-resolve them:

- If Section IX already contains real project rules, `/ms.constitution` stops and
  asks for explicit intent before replacing the baseline. Surface that question
  to the user.
- If a durable rule conflicts across the source PRDs / Feature Map / existing
  Constitution and cannot be resolved from the documents, it stops and asks the
  user to choose. Surface that question.

On a clean run → continue to the final report.

### Step 5: Final Report

When the run reaches the end (Step 4 complete) or stops early, report in Korean:

```text
🛰️ /ms.pre-specter — PRD 셋업 결과

진행: featuremap → featuremap-checklist → pre-verify → constitution
상태: ✅ 셋업 완료  |  ⛔ <단계>에서 정지

전역 게이트: <PASS | WARN | 미도달>

⚠️ 수집된 경고 (WARN):
- <step>: <요약> (<audit 파일>)
- ...
(없으면 "없음")

🎯 다음 단계:
- 셋업 완료 시: DAG 첫 Feature부터 per-Feature 사이클 시작
    /ms.specter @docs/prd/PRD.md @docs/prd/feature-map.md <첫 Feature NNN>
- 정지 시: 위 Blocking Fixes 반영 후 해당 단계부터 재개
```

Always list every collected WARN. A clean automated run with unread warnings is
exactly the silent-quality-loss failure mode this report exists to prevent.

## Stop Conditions Summary

| Where | Trigger | Conductor action |
| --- | --- | --- |
| `/ms.featuremap` | PRD set not found/confirmed, or malformed map | stop, surface the question / structural problem |
| `/ms.featuremap-checklist` | baseline artifact missing/invalid after the author's retry | stop, report the authoring-subagent failure |
| `/ms.pre-verify` | `Result: FAIL` (coverage / ownership / DAG / Antigravity) | stop, report audit + blocking fixes |
| `/ms.constitution` | existing baseline, or unresolved durable-rule conflict | stop, surface the intent / choice question |
| Step 0 | prior setup detected | confirm re-run intent before proceeding |

## Error Handling

- **No PRD** → refuse; ask for the PRD path. Never guess content.
- **Re-run over an established baseline** → confirm intent in Step 0 before
  regenerating the Feature Map or touching durable rules.
- **Underlying command error** → stop at that step and report its raw error. Do
  not skip a failed step to keep the cycle moving.

## Next Command

After `/ms.pre-specter` completes, the one-time setup is done. Start the
per-Feature cycle on the first eligible Feature in the DAG:

```bash
/ms.specter @docs/prd/PRD.md @docs/prd/feature-map.md <첫 Feature NNN>
```

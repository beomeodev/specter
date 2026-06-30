---
description: "Drive the one-time PRD setup (featuremap → codex-checklist → verify → constitution) as a single automated pre-Feature cycle"
argument-hint: "@docs/prd/PRD.md [@docs/prd/another.md]"
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
project through `featuremap → codex-checklist → verify → constitution`.

`/ms.pre-specter` does **not** replace or weaken any gate. Every underlying
command still runs in full and still writes its own audit artifact. The
conductor only reads those verdicts and decides whether to continue, collect a
warning, or stop.

## What This Command Is Not

- It does not run the per-Feature cycle (`/ms.checklist`, `/ms.agent-verify`,
  `/ms.specify`, …). That is `/ms.specter`'s job. This conductor stops once the
  one-time setup is complete and hands the first Feature to `/ms.specter`.
- It does not commit, push, tag, or open a PR. `/ms.constitution` may modify
  `AGENTS.md` and `README.md` in the working tree; publishing those stays with
  `/ms.fin`, whose `git` actions are permission-gated.
- It does not auto-overwrite an existing Constitution baseline. `/ms.constitution`
  stops and asks for intent, and Step 0 confirms a re-run before regenerating.
- It does not pass any gate-weakening flag. Codex and Antigravity verification
  always run.

## Usage

Attach one or more PRDs with `@`. Attaching them pins the exact source files so
the conductor (and the downstream commands) never has to guess paths.

```bash
/ms.pre-specter @docs/prd/PRD.md
/ms.pre-specter @docs/prd/product.md @docs/prd/admin.md
```

If no PRD is attached, the conductor looks for likely PRDs under `docs/prd/` and
**confirms the full PRD set with the user before proceeding**. It never guesses
PRD content.

```bash
/ms.pre-specter
```

## The Cycle

```text
/ms.featuremap        → docs/prd/feature-map.md (Feature DAG)        [generative]
/ms.codex-checklist   → docs/prd/codex/checklist.md                  [background]
/ms.verify            → docs/prd/feature-map.checklist.md (PASS/WARN/FAIL)
                        (runs Antigravity inline, foreground)
/ms.constitution      → Section IX + AGENTS.md + README              [once]
```

`/ms.featuremap` and `/ms.codex-checklist` both read **only the PRD set** and are
independent of each other, so the background Codex run may be launched
concurrently with the Feature Map decomposition. `/ms.verify` is the join point:
it requires both `docs/prd/feature-map.md` and `docs/prd/codex/checklist.md`.

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

## Execution Steps

### Step 0: Resolve The PRD Set And Preconditions

1. Parse the input. Classify each `@`-attached `docs/prd/*.md` path as a source
   PRD (there may be several). Use these attached paths as authoritative.
   - **PRD fallback**: if no PRD was attached, look under `docs/prd/` for likely
     PRDs and confirm the full set with the user. If none can be found or
     confirmed, stop and ask for the PRD path. Never guess PRD content.
2. Detect a prior setup (re-run). If **both**
   `docs/prd/feature-map.checklist.md` already reads `Result: PASS`/`WARN` **and**
   `.specify/memory/constitution.md` already has an established Section IX
   baseline, this is a re-run that will regenerate the Feature Map and may
   overwrite durable rules. Stop and confirm intent before proceeding:
   ```text
   ⚠️ 이미 1회 PRD 셋업이 완료된 프로젝트입니다.

   /ms.pre-specter를 다시 실행하면 Feature Map을 재생성하고, Constitution
   베이스라인 갱신을 시도합니다. 기존 분해/규칙을 덮어쓸 수 있습니다.

   계속할까요? (다시 셋업) / 취소 (개별 명령으로 일부만 갱신)
   ```
   On a fresh project (no established baseline), proceed without asking.
3. Initialize an empty collected-warnings list for this run.

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

### Step 2: `/ms.codex-checklist` (background, PRD-only)

Run `/ms.codex-checklist` with the same PRD set. Execution is **always
background**; do not pass `--background` and do not wait inline if the
decomposition in Step 1 is still finishing — this run reads only the PRDs.

The conductor must then ensure the artifact lands before Step 3:

- Wait for `docs/prd/codex/checklist.md` to appear.
- If the background Codex run fails to write it, the underlying command retries
  once. If it still fails, stop and report the failure rather than running
  `/ms.verify` against a missing independent baseline.

### Step 3: `/ms.verify` (global gate; Antigravity inline)

Run `/ms.verify`. It runs Google Antigravity in the foreground for an
independent global audit, then compares the source PRDs, the Codex checklist, the
Antigravity checklist, and `docs/prd/feature-map.md`, writing the canonical
global gate `docs/prd/feature-map.checklist.md` with `**Result**: PASS | WARN |
FAIL`.

Read the `Result`:

- **PASS** → continue.
- **WARN** → record the warning, continue.
- **FAIL** → stop. Report the audit's blocking findings (uncovered PRD
  commitment, ownership conflict, DAG cycle, or a missing/FAIL Antigravity
  checklist). Fix `docs/prd/feature-map.md` and rerun `/ms.pre-specter` (or rerun
  `/ms.verify` directly after the fix).
- If `/ms.verify` stops because `docs/prd/codex/checklist.md` is missing, return
  to Step 2 and ensure the Codex artifact is present, then retry.

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

진행: featuremap → codex-checklist → verify → constitution
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
| `/ms.codex-checklist` | background artifact missing after retry | stop, report the Codex write failure |
| `/ms.verify` | `Result: FAIL` (coverage / ownership / DAG / Antigravity) | stop, report audit + blocking fixes |
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

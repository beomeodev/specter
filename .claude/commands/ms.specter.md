---
description: "Drive one Feature through the full per-Feature cycle (checklist → review) with one human stop at clarify"
argument-hint: "@docs/prd/<PRD>.md @docs/prd/feature-map.md <Feature NNN>"
---

# /ms.specter - Per-Feature Cycle Conductor

Run a single Feature through the entire SPECTER per-Feature cycle automatically.
The conductor invokes each `/ms.*` step in order, reads each step's PASS / WARN /
FAIL verdict, and advances on its own. The only mandatory human stop is
`/ms.clarify`; the run ends at `/ms.review` (publishing is left to `/ms.fin`).

`/ms.specter` does **not** replace or weaken any gate. Every underlying command
still runs in full and still writes its own audit artifact. The conductor only
reads those verdicts and decides whether to continue, collect a warning, or stop.

## What This Command Is Not

- It does not run the one-time PRD setup (`/ms.featuremap`, `/ms.codex-checklist`,
  `/ms.verify`, `/ms.constitution`). Those must already be complete. The conductor
  covers only the repeatable per-Feature cycle.
- It does not commit, push, tag, or open a PR. The run stops at `/ms.review`.
  Publishing stays with `/ms.fin`, whose `git` actions are permission-gated.
- It does not auto-answer `/ms.clarify`. Clarification is the human's call.
- It does not pass any gate-weakening flag (e.g. `--skip-codex`). Codex and
  Antigravity verification always run.

## Usage

**Recommended form** — give three things: the PRD(s), the Feature Map, and the
next Feature number in order:

```bash
/ms.specter @docs/prd/PRD.md @docs/prd/feature-map.md 006
```

- Attach one or more PRDs with `@`. Attaching them pins the exact source files so
  the conductor (and the downstream commands) never has to guess paths.
- Attach the Feature Map with `@`. If omitted, the conductor falls back to
  `docs/prd/feature-map.md`.
- The Feature number is **freeform** — `006`, `6`, `Feature 006`, `006 진행해`,
  `6번 피처 돌려줘` all resolve to Feature 006. Surrounding words are ignored.

**Shorthand** — if you omit the `@`-paths, the conductor uses the conventional
locations (`docs/prd/feature-map.md` and the PRDs it records). Only the Feature
number is strictly required:

```bash
/ms.specter 006
/ms.specter 6번 피처 진행해
```

The one hard requirement is that a resolvable Feature number is present. It feeds
`/ms.checklist`, `/ms.agent-verify`, and `/ms.specify`.

## The Cycle

```text
/ms.checklist        → per-Feature readiness gate          [local]
/ms.agent-verify     → Codex + Antigravity, foreground     [parallel]
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
  and surface it in the final report. Never silently discard a WARN.
- **FAIL** → stop immediately. Report the failing step, its audit file, and the
  blocking fixes. Do not continue, and do not auto-fix unless the step itself
  defines a mechanical auto-fix (see `/ms.plan` below).
- **`/ms.clarify`** → always hand control to the human. Ask the questions the
  command produces (Korean), wait for answers, apply them, then resume.

This is the cycle-level expression of "autonomy only inside the control fence":
the conductor moves on its own, but only through PASS/WARN, and only the human
crosses the clarify boundary.

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
2. Confirm the per-Feature cycle can start. Require:
   - The Feature Map (attached path, else `docs/prd/feature-map.md`) exists.
   - `docs/prd/feature-map.checklist.md` exists with `Result: PASS` or `WARN`
     (the global gate from `/ms.verify`).
   - `.specify/memory/constitution.md` has an established Section IX baseline
     (from `/ms.constitution`).
   If any precondition is missing, stop and tell the user to complete the
   one-time PRD setup first:
   ```text
   ⛔ /ms.specter는 per-Feature 사이클만 자동화합니다.

   먼저 1회 PRD 셋업을 완료하세요:
     /ms.featuremap @docs/prd/PRD.md [...]
     /ms.codex-checklist @docs/prd/PRD.md [...]
     /ms.verify
     /ms.constitution

   완료 후 다시 실행: /ms.specter <Feature NNN>
   ```
3. Read the Feature Map (the attached path, else `docs/prd/feature-map.md`) and
   extract the full `## Feature NNN:` section for the resolved Feature. Keep it
   verbatim — it is the required input for `/ms.specify` in Step 3.
4. Initialize an empty collected-warnings list for this run.

### Step 1: `/ms.checklist`

Run `/ms.checklist <NNN>`. Read `docs/prd/checklists/feature-NNN.checklist.md`.

- PASS → continue.
- WARN → record the warning, continue.
- FAIL → stop. Report the audit's Blocking Fixes and tell the user to fix the
  Feature section, then rerun `/ms.specter <NNN>`.

### Step 2: `/ms.agent-verify` (foreground, parallel)

Run `/ms.agent-verify <NNN>`. Codex and Antigravity run in the foreground in
parallel and complete before this step returns (no background polling). If
either agent fails to write its `*-verify.md` report, the underlying command
retries once and then stops; surface that failure to the user rather than
proceeding.

Read both:
- `docs/prd/checklists/feature-NNN.codex-verify.md`
- `docs/prd/checklists/feature-NNN.antigravity-verify.md`

- Both PASS/WARN → continue (record any WARN).
- Either FAIL → stop. Report which agent failed and its findings.

### Step 3: `/ms.specify` (inject the Feature section)

Run `/ms.specify` with the Feature section extracted in Step 0.3 pasted as the
input. The hard gates in `/ms.specify` (Feature Map present, global + per-Feature
checklists PASS/WARN, dual-agent verification present, Constitution Section IX)
are already satisfied by Steps 0–2, so the command proceeds and writes
`specs/<id>/spec.md`.

If `/ms.specify` still refuses (an unexpected gate failure), stop and report it.

### Step 4: `/ms.clarify` — 🔴 human stop

Run `/ms.clarify`. This is the one mandatory human interaction.

- Present every clarification question the command raises, in Korean, with its
  A/B/C options.
- Wait for the user's answers. There may be several question rounds; keep going
  until all ambiguities are resolved and `spec.md` is updated.
- Then resume automatically with Step 5. Do not stop and ask the user to run the
  next command manually — the conductor continues.

If `/ms.clarify` finds no ambiguity, continue immediately.

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

On a clean plan → continue (record any WARN).

### Step 6: `/ms.tasks`

Run `/ms.tasks`. On success → continue. A duplicate-`@SPEC`-TAG failure is a hard
stop (mechanical fix required); report it.

### Step 7: `/ms.analyze` (foreground)

Run `/ms.analyze` (foreground default; Codex and Antigravity run inline, no
`--background`). Read its verdict.

- PASS → continue.
- WARN → record the warning, continue (a WARN here means "proceed after
  acknowledging"; the conductor's acknowledgement is recording it for the final
  report).
- FAIL → stop. Report the drift / coverage gap.

### Step 8: `/ms.implement --to-end`

Run `/ms.implement --to-end`. This implements every pending phase in `tasks.md`
in one run, TDD by default. Without `--to-end` the command would stop after the
first phase, so the conductor always passes it.

If implementation hits a blocker it cannot resolve within scope (e.g. an
unverifiable unstable API), the command stops and surfaces it; the conductor
stops too.

### Step 9: `/ms.review` (adversarial, foreground)

Run `/ms.review`. The dual-agent review always runs in adversarial mode and the
executable code gates (lint, typecheck, tests, build) run regardless.

- PASS → continue to the final report.
- WARN → record the warning, continue.
- FAIL / NOT READY → stop. Report the failing gates and findings. The conductor
  does not auto-fix; fixes belong to `/ms.implement --mode=refactor` or the main
  conversation.

### Step 10: Final Report

When the run reaches the end (Step 9 PASS/WARN) or stops early, report in Korean:

```text
🛰️ /ms.specter — Feature NNN 사이클 결과

진행: checklist → agent-verify → specify → clarify → plan → tasks → analyze → implement → review
상태: ✅ review까지 완료  |  ⛔ <단계>에서 정지

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
| `/ms.plan` | design-level reality FAIL | stop, surface the design question |
| `/ms.agent-verify` | agent write failure after retry | stop, report the failing agent |
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

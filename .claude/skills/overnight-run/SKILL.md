---
name: overnight-run
description: Run multiple independent SPECTER Features unattended overnight — evening prep (worktree per Feature via git-worktrees, cycle advanced through clarify so the only human stop is pre-spent), a detached shell driver (specter-overnight.sh) that resumes each cycle headlessly in its own worktree via `claude -p` with session-limit backoff, and a morning report. Use when the user says "밤새 돌려", "오버나이트", "자기 전에 N번 돌려놔", or asks how to run Features while away — targets MUST be DAG-independent (parallel-features eligibility).
---

# Overnight Run

Overnight execution is NOT one long session (compaction drags the summary along and
context replay compounds) — it is **the one-session-per-Feature discipline,
automated**: a detached shell driver launches a fresh headless session per Feature,
each in its own worktree, with SPECTER's machine-readable artifacts (run ledger +
gate script) as the handoff between sessions.

## The shape

```text
저녁 (사람 있음):   Feature마다 worktree 준비 + 사이클을 clarify까지 진행 (질문 답변)
밤 (드라이버):      worktree마다 claude -p 재개 → plan→tasks→analyze→implement→review
아침 (사람):        보고서 확인 → parallel-features 순서로 직렬 머지백 (fin → merglease)
```

## Preconditions (check before promising anything)

1. **Targets are DAG-independent** — run the `parallel-features` eligibility test
   (Test A + Test B). Dependent Features cannot overnight together: merging happens
   in the morning, so a dependent Feature would build against a base that doesn't
   contain its dependency.
2. **Host stays awake** — the container must survive the night (check host sleep
   settings; OrbStack containers die with the host).
3. **Headless permissions** — `claude -p` has no human to answer prompts. The
   project's allowlist must cover the cycle's operations; the driver's `CLAUDE_CMD`
   default adds `--permission-mode acceptEdits` (override via env if the project
   needs different flags).
4. Union-merge `.gitattributes` entries installed (parallel-features Section 2).

## Evening prep (interactive, this session)

For each target Feature NNN:

1. Create/enter its worktree via the `git-worktrees` skill
   (`.worktrees/feature-NNN`, branch from up-to-date master, deps installed, clean
   baseline).
2. Inside that worktree, run `/ms.specter NNN` and proceed **through clarify** —
   checklist/agent-verify/specify run automatically; the user answers the clarify
   questions; then STOP (park). The worktree's run ledger now records clarify
   PASS/WARN, which is the driver's admission ticket.
3. Repeat per Feature. User attention ≈ the clarify answers only.

## Launch (bedtime, one command)

```bash
nohup .specify/scripts/bash/specter-overnight.sh 007 008 009 \
  > /tmp/overnight-$(date +%Y%m%d).log 2>&1 &
```

Or the user just says "돌려놔" and you run exactly that for them, then report:
log path, expected report path, and that the session can be closed — the driver is
detached from it.

What the driver does per Feature (all deterministic shell, no model judgment):
verify the worktree exists and its ledger shows clarify PASS/WARN (else SKIP with
reason) → run `claude -p "/ms.specter NNN"` with the worktree as CWD → on a
session/usage-limit error, sleep 30 min and retry (bounded) → judge the outcome
from the worktree's ledger (`review` PASS/WARN = success; else record last step) →
next Feature. Failures don't stop the run — targets are independent by precondition.
Finally it writes `docs/overnight/REPORT-<date>.md` in the main repo.

## Morning

User asks "밤새 결과 보고해": read the report + each worktree's ledger tail, then
summarize — per Feature: verdict, stop point if any, collected WARNs, and the
recommended merge order. Then execute merge-back serially per `parallel-features`
Section 5 (first: fin→merglease; subsequent: rebase → local-ci re-run → fin→merglease;
cleanup each worktree only after its merge confirms).

## What this skill never does

- Merge or release anything overnight (`/ms.fin`/`/ms.merglease` stay human-triggered,
  morning-side — the conductor's own boundary at review is preserved).
- Run dependent Features in one night, or two cycles in one worktree.
- Attempt a Feature whose clarify wasn't pre-spent — the driver refuses; the fix is
  evening prep, not skipping the human stop.

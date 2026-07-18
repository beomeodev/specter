---
name: session-handoff
description: Compose the minimal paste-ready resume block when a session ends with work remaining — context threshold approaching, a Feature finished while others remain, the user declares the session over ("세션 종료", "내일 이어서", "오늘은 여기까지"), or /ms.fin publishes with unfinished Features. Enforces Diet Constraints against handoff bloat. Trigger symptoms — load this skill when you are ABOUT to write a long end-of-session summary, inline today's debugging history "so nothing is lost", or list every lesson learned in the final message.
---

<!-- Format adapted from MoAI-ADK session-handoff §Diet Constraints (6-block form reduced:
     localization tables, mode-seeding, and CLI save integration all dropped).
     Rationalization table entries come verbatim from the 2026-07-13 RED baseline run. -->

# Session Handoff — Minimum Executable Resume

A handoff block is the **next session's minimum executable context**. It is not an
audit record, not a diary, and not storage. Everything durable already has a home:
code and diffs live in git, verdicts and steps live in the run ledger
(`.specify/specter-run.jsonl`), review findings live in `docs/review/`, lessons and
decisions live in memory files. The block only carries what none of those can:
which entry point to take, how to verify the ground is still solid, and the one
action that resumes the work.

## When to fire (any of)

1. Context threshold approaching (harness compaction warnings, or the conversation
   has been summarized repeatedly).
2. `/ms.specter` finished a Feature and the Feature Map has remaining Features.
3. The user declares the session over ("세션 종료", "내일 이어서", "오늘은 여기까지").
4. `/ms.fin` created a PR and unfinished Features remain.

## The block (the only durable output of a handoff)

```text
✂──── 여기부터 복사 ────✂
<Feature/작업> <단계> 재개.
적용 교훈: <메모리/원장 참조, 최대 4줄>

전제 검증:
1) <검증 가능한 명령> → <기대 결과>   (최대 4개, 각 200자 이내)

실행: <단일 명령 또는 액션 1개>

후속: <머지 후/다음 Feature, 최대 2줄>
✂──── 여기까지 복사 ────✂
```

Output order: the fenced block → (only if you saved overflow) the file path(s),
bare, one per line → one summary sentence. Then STOP: no closing remarks, no
well-wishes, no restated caveats about what is or isn't durable — anything after
the summary sentence is bloat. If saving a file fails, the block alone suffices —
fail-open, never block session end on bookkeeping.

## Filling the four slots

- **적용 교훈 (≤ 4 lines)**: references, not prose — memory file names, ledger
  entries, report paths. A lesson worth keeping is worth a memory file; write the
  file first, then reference it here. Never teach the lesson inside the block.
- **전제 검증 (≤ 4 items, each ≤ 200 chars)**: each item is a runnable command
  with its expected result. Status narrative converts to commands:
  "14 files uncommitted" becomes `git status --porcelain | wc -l` → `14`.
  Unrecorded environment facts (a manually-exported variable, a stale config you
  worked around) are exactly what dies with the session — record them in a durable
  file NOW (repo docs or a memory file) and verify them here with a command, never
  narrate them.
- **실행 (exactly 1)**: one command or one action. If tomorrow starts with
  multi-step work, the single action is the workflow command that drives those
  steps (`/ms.fin`, `/ms.specter 008`) — the steps themselves stay in the workflow,
  not in the block.
- **후속 (≤ 2 lines)**: what comes after the 실행 action succeeds. Nothing else.

## Diet Constraints (anti-patterns — each observed in the RED baseline)

- **No history narrative.** What failed and got fixed today is already in the run
  ledger and review reports — reference, never retell. A round-1-FAIL story is
  ledger data, not handoff content.
- **No inlined decision rationale.** An abandoned-approach analysis ("why X didn't
  fit") is a decision record: save it as a memory/docs file and reference it.
  Inlining it "because the code was deleted" turns the block into the archive it
  must never be.
- **No multi-step plans.** "DO THIS FIRST" followed by commit-splitting
  sub-instructions is a plan, not a handoff. One 실행 action; the workflow command
  owns the steps.
- **No ceremonial reminders and no user-preference restatements** — CLAUDE.md,
  memory, and the rules already hold them; repeating them is pure token cost.
- **Retry residue gets deleted.** Sentences that accumulated while you iterated on
  the block do not survive to the final version.
- **Over-cap content moves to files.** The cap is the trigger to write a memory
  file, never a thing to justify exceeding.

## Rationalizations (verbatim from baseline) vs reality

| Excuse | Reality |
|---|---|
| "Expensive or impossible to reconstruct tomorrow" | Then it belongs in a durable file written NOW; the block references it. The block itself is not storage — it is pasted once and scrolls away. |
| "The reasoning is the only surviving artifact" | Make it an artifact: write the memory/docs file. Inlined text is context, not an artifact. |
| "Cheap to write, expensive to relearn" | Cheap × every future restart = expensive. Lessons live in memory; the block carries at most 4 reference lines. |
| "Include everything decision-relevant" | The next session needs an entry point, not a dossier: verify preconditions, run one action. Depth loads on demand from the referenced files. |

## Red flags — stop and re-diet if the draft has

- Numbered sections beyond the four slots of the block.
- Any paragraph explaining *why* something was done today.
- A "first do A, then B, then C" sequence anywhere.
- A lesson stated as prose instead of a file reference.
- Anything after the one summary sentence — closing remarks, well-wishes,
  restated durability caveats.
- You are about to exceed a cap and it "feels justified this time".

## Overlap rule (session-status hook)

The SessionStart hook already injects the last ledger step and the next planned
Feature (dependency-unchecked — `/ms.checklist` decides real eligibility) into
the new session. Never restate those in the block body — if the next
session must confirm them, express that as one 전제 검증 command
(e.g. `tail -n 1 .specify/specter-run.jsonl` → last step/verdict), nothing more.

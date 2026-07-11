---
name: overnight-run
description: Run prepared SPECTER Features unattended after an explicit user request for an overnight run — parallel mode for DAG-independent Features (worktree per Feature) and chain mode for dependent Features (one worktree, one branch, sequential cycles with an as-built drift check and a bounded autonomy ladder), a detached shell driver (specter-overnight.sh) resuming each cycle headlessly via claude -p with session-limit backoff, automatic per-Feature /ms.fin, opt-in /ms.merglease, and a morning report that lists every autonomous decision. Use ONLY when the user explicitly requests an overnight/unattended run — "밤새 돌려", "오버나이트", "overnight", "자기 전에 N개 돌려놔" — the elevated autonomy comes from that explicit invocation, never from the time of day.
---

# Overnight Run

## Autonomy comes from invocation, not the clock

Everything this skill authorizes — headless progression, autonomous drift decisions,
automatic `/ms.fin`, opt-in `/ms.merglease` — is granted by exactly one thing: **the
user explicitly requesting an overnight run** (오버나이트/overnight/"밤새 돌려"). The
invocation is the approval, in the same sense that CLAUDE.md §7 treats invoking
`/ms.fin` as approval for its git actions.

- **Nighttime grants nothing.** An ordinary session at 2am has zero overnight
  privileges: normal permission rules, normal human stops, no autonomous decisions,
  no auto-fin. "The user seems to be away" is not an invocation.
- **Daytime denies nothing.** An overnight run the user launches at noon carries every
  privilege in this skill.
- **The grant dies with the run.** The morning conversation, and any session that was
  not started by the driver for this run, is back under normal rules.

## Mode selection — the Feature Map DAG decides

| Targets | Mode |
|---|---|
| DAG-independent Features (parallel-features eligibility passes) | **Parallel**: worktree per Feature, failures don't stop the run |
| Dependent chain (B needs A) | **Chain**: one worktree, one branch, sequential full cycles in dependency order; a failure parks everything downstream |
| Mixed | Independent groups in parallel; within a group, chain rules |

Run the `parallel-features` eligibility test (Test A + Test B) to justify parallel
mode. Chain mode deliberately relaxes the old "never two cycles in one worktree"
rule — that ban guarded against *parallel* interference; sequential cycles in one
worktree are what chain mode is.

## The shape

```text
Parallel:
저녁 (사람 있음):  Feature마다 worktree 준비 + 사이클을 clarify까지 진행 (질문 답변)
런 (드라이버):     worktree마다 fresh claude -p → plan→…→review → review PASS/WARN이면 /ms.fin
아침 (사람):       보고서 + 자율 결정 검토 → parallel-features 순서로 직렬 머지백 (merglease)

Chain:
저녁 (사람 있음):  chain worktree 하나 준비 + 의존 순서대로 각 Feature를 clarify까지 진행
                   (후속 Feature의 clarify 답변 중 선행 결과에 기대는 것은 [DEPENDS: NNN] 표시)
런 (드라이버):     Feature 순서대로: 드리프트 체크(첫 Feature 제외) → plan→…→review →
                   /ms.fin → 다음 Feature. 실패 시 체인 정지, 하위 전부 PARK.
아침 (사람):       보고서 + 자율 결정 검토 → (opt-in 안 했으면) /ms.merglease
```

Overnight execution is NOT one long session (compaction drags the summary along) —
it is **the one-session-per-Feature discipline, automated**: the driver launches a
fresh headless session per Feature, with the run ledger (`.specify/specter-run.jsonl`)
as the handoff between sessions. A session/usage-limit error sleeps and retries; the
re-invoked cycle resumes from the ledger's last recorded step.

## Preconditions (check before promising anything)

1. **Explicit overnight invocation from the user** — see the top section. Without it,
   none of the rest applies.
2. **Mode matches the DAG** — parallel targets pass the eligibility test; chain
   targets are listed in true dependency order (wrong order = building against a base
   that doesn't exist; the drift check cannot save a reversed chain).
3. **Host stays awake** — the container must survive the run (OrbStack containers die
   with the host).
4. **Headless permissions** — `claude -p` has no human to answer prompts. The project
   allowlist must cover the cycle's operations; the driver's `CLAUDE_CMD` default adds
   `--permission-mode acceptEdits`.
5. Parallel mode only: union-merge `.gitattributes` entries installed
   (parallel-features Section 2).

## Evening prep (interactive, this session)

**Parallel** — for each target Feature NNN: create/enter its worktree via the
`git-worktrees` skill (`.worktrees/feature-NNN`, branch from up-to-date master, deps
installed, clean baseline), run `/ms.specter NNN` **through clarify** (user answers),
then STOP. The ledger's clarify PASS/WARN is the driver's admission ticket.

**Chain** — create ONE worktree (`.worktrees/overnight-chain`, branch from up-to-date
master). Inside it, for each Feature in dependency order, run `/ms.specter NNN`
through clarify, then STOP. While answering clarify for a downstream Feature, mark
every answer that assumes something about an upstream Feature's not-yet-built shape
with `[DEPENDS: NNN]` in the spec's clarify record — these markers are exactly what
the drift check re-validates at run time.

Also ask the user ONE mode question at prep: "머지+릴리즈(`/ms.merglease`)까지 자동으로
할까요, 아침에 직접 할까요?" Their answer decides whether the launch command carries
`--merglease`. Do not decide this for them.

## Launch (one command, the user's go signal)

```bash
# Parallel (independent Features):
nohup .specify/scripts/bash/specter-overnight.sh 007 008 009 \
  > /tmp/overnight-$(date +%Y%m%d).log 2>&1 &

# Chain (dependent Features, dependency order; add --merglease only if opted in):
nohup .specify/scripts/bash/specter-overnight.sh --chain 004 005 006 \
  > /tmp/overnight-$(date +%Y%m%d).log 2>&1 &
```

Or the user says "돌려놔" and you run it for them, then report: log path, expected
report path, and that this session can be closed — the driver is detached.

## Drift check and the autonomy ladder (chain mode)

Before each downstream Feature's cycle, the driver's prompt makes the fresh session
compare the upstream Feature's **as-built** result (committed interfaces, file layout,
data shapes) against this Feature's spec and its `[DEPENDS]`-marked clarify answers.
Resolution follows this ladder — always take the LOWEST rung that fits, record the
decision, and continue only if a rung short of PARK applies:

1. **Conform** — difference is PRD-neutral (names, signatures, file locations):
   update the spec via the `/ms.amend` path to match as-built reality. Record, proceed.
2. **Conservative choice** — a `[DEPENDS]` clarify answer no longer holds but the PRD
   still admits a resolution: pick the most conservative reading of the PRD, amend,
   record as **WARN**, proceed.
3. **PARK** — resolving would require a new requirement, a PRD edit, or weakening any
   gate: stop this Feature AND everything downstream of it. Requirements are invented
   only by the user (`/ms.expand`); gates are never weakened, day or night.

Every rung-1/rung-2 decision is appended to the run ledger as
`{"cycle":"overnight","feature":"NNN","type":"decision","rung":1|2,"summary":...,"rationale":...}`
— additive records that gate readers (which filter `cycle=="feature"`) ignore. The
morning report surfaces them; an unrecorded decision is a protocol violation, not a
convenience.

Gate FAILs keep their normal meaning: the conductor stops, the driver records the stop
point, chain mode parks downstream Features. Overnight never retries past a FAIL.

## Git autonomy scope (within an invoked run only)

- **`/ms.fin` per Feature: automatic** in both modes once review is PASS/WARN —
  commit + push overnight means work survives a dead host. The deny list
  (`git reset --hard`, force-push, `git clean -fdx`) stands, always.
- **`/ms.merglease`: opt-in only**, decided by the user at evening prep, carried as
  the `--merglease` launch flag, honored in chain mode at end-of-chain when every
  Feature finished green. Parallel mode never auto-merges (serial rebase + re-gate
  discipline is morning work by design). No flag → the run leaves branches pushed and
  PRs open, nothing merged, nothing released.

## Morning

User asks "밤새 결과 보고해": read the report, each ledger tail, and every
`"type":"decision"` record, then summarize per Feature: verdict, stop point if any,
WARNs, **and each autonomous decision with its rung and rationale** — the user
approved the protocol in advance, so the morning debt is transparency, not
permission. Then — this conversation is back under normal rules (the run's grant is
spent) — parallel mode: serial merge-back per parallel-features Section 5; chain mode
without `--merglease`: propose a single `/ms.merglease` on the chain branch and run it
when the user says go; PARKed Features: discuss (likely `/ms.expand` or re-clarify),
never silently retry.

## What this skill never does

- Activate on time of day, an away-looking user, or its own initiative — only on the
  user's explicit overnight request. Nighttime in an ordinary session changes nothing.
- Carry the run's autonomy into any session the driver didn't start, or past the run's
  end.
- Invent requirements, edit the PRD, or weaken/skip a gate to keep a chain moving —
  that is rung 3: PARK and report.
- Run `/ms.merglease` without the prep-time opt-in flag, or auto-merge parallel
  worktrees.
- Attempt a Feature whose clarify wasn't pre-spent — the driver refuses; the fix is
  evening prep, not skipping the human stop.
- Make an autonomous decision without appending its ledger record.

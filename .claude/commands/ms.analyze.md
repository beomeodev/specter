---
description: "Pre-implementation document consistency and drift validation"
argument-hint: "[--background] [--raise-risk]"
---

# /ms.analyze - Document Consistency Gate

Validate that `spec.md`, `plan.md`, and `tasks.md` are coherent before any code
is implemented. This command is the SPECTER wrapper around `/speckit-analyze` for
pre-implementation document validation only, with a required dual-agent
semantic consistency station.

Post-implementation code quality gates belong to `/ms.review`. Do not run tests,
lint, typecheck, coverage, or code-level TAG scans from this command.

## Workflow Position

```text
/ms.tasks → /ms.analyze → /ms.implement
```

## Usage

```bash
/ms.analyze
/ms.analyze --background
/ms.analyze --raise-risk
```

Codex runs in the foreground by default. Use `--background` only when the
document set is large and the user explicitly wants to resume later.

Reviewer effort is fixed (`codex: xhigh`, `antigravity: medium`). The risk
profile, round budget, and report validity come from `specter-gate.sh`
mechanically (verification-v2). Models do not choose those settings; the only
risk flag is the upward-only `--raise-risk`.

## Purpose

`/ms.analyze` answers: **Are the implementation documents coherent enough to
build from?**

It validates the specification chain before implementation starts:

- Feature scope from `spec.md` is represented in `plan.md`.
- Functional requirements in `spec.md` have corresponding tasks in `tasks.md`.
- Planned files, migrations, and contracts are internally consistent.
- Constitution and AGENTS constraints are acknowledged in the plan/tasks.
- Amendments do not leave stale or contradictory requirements behind.

## GEARS Contract

- When `/ms.analyze` runs before implementation, the command shall compare
  `spec.md`, `plan.md`, and `tasks.md` for coverage, drift, and contradiction.
- When a functional requirement lacks implementation tasks, the command shall
  fail with the missing requirement ID.
- When a task has no originating requirement or plan rationale, the command shall
  fail with the orphan task ID.
- The command shall ask both Codex and Antigravity to perform independent
  document consistency reviews and
  write the results to `specs/[spec-id]/analyze.codex.md` and
  `specs/[spec-id]/analyze.antigravity.md`.
- When all documents are consistent, the command shall allow `/ms.implement` to
  proceed.

## Execution Steps

### Step 0: Load Required Artifacts

Read these files in full:

- `.specify/memory/constitution.md`
- `AGENTS.md` if it exists
- `specs/[spec-id]/spec.md`
- `specs/[spec-id]/plan.md`
- `specs/[spec-id]/tasks.md`

**Session read policy**: per AGENTS.md §2 — reuse files already read this session; a fresh `Read` immediately before `Edit`/`Write` is still required.

If any of `spec.md`, `plan.md`, or `tasks.md` is missing, stop and tell the user
which upstream command must run first.

### Step 0.5: Self-Heal The Gate And Bind The Inputs

```bash
# self-heal: the runtime copies are project-local (never synced)
install -D -m 0755 docs/templates/scripts/specter-gate.sh .specify/scripts/bash/specter-gate.sh
install -D -m 0644 docs/templates/verification-v2.json .specify/policies/verification-v2.json
.specify/scripts/bash/specter-gate.sh version | grep -q '"contract": "verification-v2"' \
  || { echo "partial sync — run /ms.sync (or /ms.init) first"; }
DIGEST=$(.specify/scripts/bash/specter-gate.sh digest analyze specs/[spec-id] | python3 -c "import json,sys; print(json.load(sys.stdin)['input_digest'])")
```

The digest binds both reports to the exact spec/plan/tasks revisions under
review. The risk profile is computed inside the aggregation from the Feature's
declared `### Verification signals` table — there is no separate
classification step. Reject every model, effort, reviewer-skip, or
scope-lowering flag; the only risk flag is the upward-only `--raise-risk`.

### Step 1: Run Spec-Kit Foundation

Execute the underlying document analysis:

```text
/speckit-analyze
```

Treat `/speckit-analyze` as the foundation for document consistency only.

### Step 2: SPECTER Drift Detection (Layer 1 — fail-fast, before agents)

This step is the station's deterministic/host detection layer. Two rules bind
it (`specter-agent-protocols` §7): a FAIL here **stops the command before any
agent is dispatched** (mechanical drift does not need two agents to find), and
host findings can only **worsen** the final station verdict — they never
soften an agent's verdict.

First the mechanical checks (run them, do not eyeball):

```bash
# every FR id in spec.md must appear in tasks.md
comm -23 <(grep -oE 'FR-[0-9]+' specs/[spec-id]/spec.md | sort -u) \
         <(grep -oE 'FR-[0-9]+' specs/[spec-id]/tasks.md | sort -u)
# duplicate @SPEC TAG ids in tasks.md (output must be empty)
grep -oE '@SPEC:[A-Za-z0-9_-]+' specs/[spec-id]/tasks.md | sort | uniq -d
```

Any output from the first command is a missing-FR-coverage FAIL (name the FR
ids); any output from the second is a duplicate-TAG FAIL.

Then run these additional checks:

1. **Feature Map lineage**: the spec references a Feature section from
   `docs/prd/feature-map.md`.
2. **FR coverage**: every FR in `spec.md` maps to at least one task in `tasks.md`.
3. **Task lineage**: every implementation task maps to an FR, plan step, setup
   requirement, or verification requirement.
4. **Plan coverage**: every planned component, migration, API, and test strategy
   has a corresponding task or explicit out-of-scope note.
5. **Migration consistency**: migration names and numbers match across documents.
6. **File path integrity**: existing file paths mentioned in documents exist; new
   file paths are clearly marked as new.
7. **Amendment integrity**: any superseded FR has a matching Amendment block and
   affected tasks are updated or removed.
8. **Constitution alignment**: plan/tasks acknowledge active Constitution
   constraints, including Section IX if it has been established.

### Step 3: Dual-Agent Document Consistency Review

Invoke both Codex and Antigravity for independent semantic reviews. The risk
profile never reduces reviewer count.

Report paths are round-numbered (`analyze.codex.r<R>.md` /
`analyze.antigravity.r<R>.md`) — a new round is a new file, never an
overwrite. Substitute Step 0.5's `{DIGEST}` and the Feature number into both
prompts; the aggregation rejects a report whose digest no longer matches.

**On a §4 re-round (R = 2)**, pass both prior-round report paths into both
prompts and append: `Re-round continuity: read the prior round's reports
first — specs/[spec-id]/analyze.codex.r1.md and
specs/[spec-id]/analyze.antigravity.r1.md. They are NOT a PASS whitelist and
do not suppress discovery. Re-check every prior blocking finding by ID and
mark each resolved or persists in your Findings State column. A grade may
improve only against changed, cited evidence. If your own lane previously
prescribed the state you now reject, say so explicitly, cite the prior finding
ID, and recommend escalation.`

#### 0. External Agent Preflight (session-level, once)

Apply the Preflight and Degrade Rule from
`.claude/skills/specter-agent-protocols/SKILL.md` (§1–2). For this command: a **dual-agent
station** — if one agent is unavailable after preflight + one retry, run it single-agent and
write the §2 degrade placeholder (a VALID v2 report — `**Contract**: verification-v2`,
`**Mode**: agent-document-consistency`, `**Scope**: Feature NNN`, `**Input Digest**:
{DIGEST}`, `**Result**: WARN`, `**Availability**: UNAVAILABLE (<reason>)`) at the missing
agent's round-numbered report path (`specs/[spec-id]/analyze.codex.r<R>.md` /
`analyze.antigravity.r<R>.md`); the Layer-3 aggregation then caps the station at `WARN`
mechanically. Never present a single-agent run as dual; never block `/ms.analyze` on an
environment issue alone except when both reviewers are unavailable, which stops the
station. A high-risk degrade requires `ack-degrade` only when the missing reviewer was
needed for a triggered check (protocols §8).

#### A/B. Codex & Antigravity Review (same prompt body, different agent)

```text
/codex:rescue --fresh --model gpt-5.6-luna --effort xhigh <prompt>
/antigravity:rescue --fresh --model gemini-3.5-flash --effort medium <prompt>
```

Both agents read:
- `.specify/memory/constitution.md`
- `AGENTS.md` if it exists
- `docs/prd/feature-map.md`
- `docs/prd/feature-map.checklist.md`
- `docs/prd/checklists/feature-NNN.checklist.md`
- `specs/[spec-id]/spec.md`
- `specs/[spec-id]/plan.md`
- `specs/[spec-id]/tasks.md`

Codex writes `specs/[spec-id]/analyze.codex.r<R>.md`; Antigravity writes
`specs/[spec-id]/analyze.antigravity.r<R>.md`. Substitute `{AGENT}`,
`{REPORT}`, `{DIGEST}`, `{NNN}`, `{R}`:

```text
You are performing an advisory SPECTER document consistency review.

Check spec.md, plan.md, and tasks.md against the Feature Map evidence,
Constitution, and prior checklist gates. Do not edit files except writing
{REPORT}.

Focus on:
- spec FRs missing from tasks
- tasks with no spec, plan, setup, or verification source
- plan components, migrations, APIs, or test strategies missing from tasks
- contradictions between spec, plan, and tasks
- stale or incomplete Amendment handling
- migration number, file path, or contract drift
- Feature Map commitments that no longer survive into spec/plan/tasks
- provenance survival (.claude/skills/specter-agent-protocols/SKILL.md §10):
  clarify interpretation records still citing their C-/D-ID, and any
  spec/plan/tasks behavior with no C-ID, Amendment, or recorded
  interpretation behind it (untagged addition — flag it, whatever document it
  first appeared in)
- Verification-signal values (### Verification signals) that the now-concrete
  spec, plan, or tasks contradict — a declared "no" the documents contradict
  is a blocking finding
- when a rule is violated, list every violator of that rule you can find,
  never just the first instance

{When high-risk add: High-risk profile — additionally run these named checks
and report each as one row in a "## High-risk checks" table (one row per
triggered signal): <applicable high_risk_checks from verification-v2.json>.}

{On round R >= 2 add the re-round continuity block from Step 3's preamble.}

Write:

# {AGENT} Analyze Review — Feature {NNN} — Round {R}

**Contract**: verification-v2
**Mode**: agent-document-consistency
**Scope**: Feature {NNN}
**Input Digest**: {DIGEST}
**Result**: PASS | WARN | FAIL

## Scope and evidence
**Checked**: <named check classes, with file:line citations>
**Not checked**: <explicit exclusions with reasons, or the evidence basis for claiming none>

## Findings

| ID | Severity | State | Finding | Evidence | Required Fix |
| --- | --- | --- | --- | --- | --- |

(IDs stable within your lane, e.g. CX-A-001 / AG-A-001. State: new | persists |
resolved. Required Fix = restored invariant + minimum repair + no new scope;
escalate instead of choosing when several product interpretations remain valid.)

## Verdict

One concise paragraph.

Also echo the finished report between ===REPORT BEGIN=== and ===REPORT END=== markers in your
final message, verbatim, so it can be salvaged if the file write fails.
```

If the user supplied `--background`, add `--background` to both invocations. Do
**not** offload a "rerun `/ms.analyze` later" onto the user: per
`specter-agent-protocols` §9 a detached agent never self-notifies, so launch a
harness-tracked waiter — a `Bash(run_in_background: true)` poll loop on the two
round-numbered report paths, or `status --wait` — that wakes the host when both
reports appear, then continue to aggregation in the same session.

**Validate / Salvage / Format-Retry**: apply `specter-agent-protocols` §3 — for
each report run `specter-gate.sh validate-report <path> analyze specs/[spec-id]
--round <R>`; invalid → salvage from the `===REPORT BEGIN/END===` markers →
still invalid → re-dispatch that one agent once, same round, with the
validator's errors prefixed (track for `--format-retries`). Still invalid →
agent-authored failure: leave it for the aggregation to grade `FAIL`.

#### C. Layer-3 Aggregation (mechanical — replaces host result-weighing)

If `--background` was used and either report file has not appeared yet, do
**not** run the aggregation against a missing report (it would grade the absence
as FAIL, the wrong signal for a still-running agent). Hold for the
`specter-agent-protocols` §9 waiter instead: `PENDING` is interim status only —
keep the harness-tracked waiter in place and resume aggregation when woken on
both reports' appearance; never end the turn to hand the recheck back to the
user. Once both reports exist:

```bash
.specify/scripts/bash/specter-gate.sh aggregate analyze specs/[spec-id] --ledger --round <R> \
  [--raise-risk] [--format-retries "<codex-retries> <antigravity-retries>"]
```

`<R>` is the current §4 round. The gate itself refuses rounds beyond the
automatic budget (2) without a recorded `authorize-round` decision. Every
round uses `--fresh`. At the cap, present the §4 post-cap options verbatim
(fix and restart / amend authority / authorize one doctrine-dispute round /
accept WARN / stop) — never "run one more round?".

- The receipt `verdict` is the agent-station outcome; the final `/ms.analyze`
  result is the **worse** of Step 2's host result and the receipt verdict.
- The host never downgrades an agent `WARN`/`FAIL` by explaining it as a false
  positive (`specter-agent-protocols` §5 no-unilateral-host-downgrade). A
  disputed finding goes back as a scoped §4 re-round — dispatched `--fresh`,
  prior findings passed as report file paths — where only the reviewing agent
  may revise its own grade against changed evidence.

#### D. Convergence Policy (re-round caps)

Apply the Round Budget from `specter-agent-protocols` §4: 2 automatic rounds,
Round 2 scoped to failing findings only, stop when only `WARN`s remain.
Exhausting the budget leaves an unresolved FAIL as FAIL and returns control to
the user. Record every residual WARN.

### Step 4: Result Model

Use this result model:

- `PASS`: `/ms.implement` may proceed.
- `WARN`: recorded in the receipt and ledger; `/ms.implement` may proceed —
  the only analyze-station human stop is an `ack-degrade` when the missing
  reviewer was needed for a triggered high-risk check (protocols §8).
- `FAIL`: `/ms.implement` must not proceed.

**FAIL conditions:**

- Missing FR coverage in `tasks.md`.
- Orphan task with no spec/plan source.
- Contradictory plan/spec decisions.
- Broken migration numbering across documents.
- Missing Amendment block for superseded requirements.
- Constitution violation in plan/tasks.
- Layer-3 aggregate verdict `FAIL` — an agent `FAIL` is final unless a §4
  re-round with changed evidence revises it; the host cannot explain it away.

When the receipt is WARN with `cap: single-agent-degrade` and the missing
reviewer was needed for a triggered high-risk check, stop and request the
typed decision before advancing:

```bash
.specify/scripts/bash/specter-gate.sh decide ack-degrade analyze <NNN> --reason "<user's words>"
```

Reviewers, agents, and the host cannot decide for the human.

### Step 5: Report

Display a Korean summary:

```json
{
  "document_consistency": "PASS|WARN|FAIL",
  "risk_profile": "ordinary|high-risk",
  "codex_analysis": "PASS|WARN|FAIL|PENDING",
  "codex_report": "specs/{id}/analyze.codex.r<R>.md",
  "antigravity_analysis": "PASS|WARN|FAIL|PENDING",
  "antigravity_report": "specs/{id}/analyze.antigravity.r<R>.md",
  "feature_lineage": "PASS|WARN|FAIL",
  "fr_task_coverage": "100%",
  "orphan_tasks": 0,
  "next_step": "/ms.implement"
}
```

If `PASS`:

```text
✅ 문서 일관성 검증 통과

- spec ↔ plan ↔ tasks 정합성 확인
- Feature Map lineage 확인
- Constitution alignment 확인
- Codex & Antigravity document consistency review 확인

🎯 다음 단계: /ms.implement
```

If `FAIL`:

```text
⛔ 문서 일관성 검증 실패

아래 항목을 수정한 뒤 /ms.analyze를 다시 실행하세요.
/ms.implement는 아직 진행하지 마세요.
```

## Relationship To Other Commands

| Command | Responsibility | Timing |
| --- | --- | --- |
| `/ms.pre-verify` | Global PRD → Feature Map gate | Before `/ms.constitution` |
| `/ms.checklist` + `/ms.verify` | Per-Feature PRD readiness gate | Before `/ms.specify` |
| `/ms.analyze` | spec ↔ plan ↔ tasks document gate plus Codex document review | Before `/ms.implement` |
| `/ms.review` | code quality + executable gates | After `/ms.implement` |

## Run-State Ledger (bookkeeping, not a gate)

The agent-station line is emitted mechanically by Step 3-C's
`aggregate --ledger` (`specter-agent-protocols` §7): verbatim `caught` rows,
mechanical `cap`. The host never authors that line. Two host-side cases
remain, both append-only:

- **Step 2 FAIL (agents never ran)**: append the fail-fast evidence yourself —
  `caught` is the mechanical check output / drift findings, verbatim:

  ```bash
  mkdir -p .specify
  printf '{"ts":"%s","cycle":"feature","feature":"%s","step":"analyze","verdict":"FAIL","artifacts":["specs/<spec-id>/spec.md"],"caught":%s}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "<NNN>" "<verbatim host findings array>" >> .specify/specter-run.jsonl
  ```

- **Host WARN after a PASS aggregate**: when Step 2 found WARN-level drift but
  the aggregate line says PASS, append one supplementary WARN line with the
  host findings verbatim in `caught` **and** the mechanical receipt's verdict
  embedded verbatim as `"agents_verdict"`. Per §7's composite rule, this line
  may only equal or worsen the mechanical verdict, never soften it; the
  mechanical line stays in the append-only ledger regardless.

## Next Command

After `/ms.analyze` passes, run `/ms.implement`.

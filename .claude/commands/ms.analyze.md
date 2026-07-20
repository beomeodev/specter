---
description: "Pre-implementation document consistency and drift validation"
argument-hint: "[--background] [--raise-audit-tier T2|T3]"
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
/ms.analyze --raise-audit-tier T3
```

Codex runs in the foreground by default. Use `--background` only when the
document set is large and the user explicitly wants to resume later.

Reviewer effort, scope, re-round cap, and WARN handling are read from the
canonical audit-tier receipt. Models do not choose those settings.

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

### Step 0.5: Reclassify And Bind Audit Intensity

Recompute immediately from the complete pre-implementation artifact set:

```bash
python3 .specify/scripts/python/classify_audit_tier.py \
  --policy .specify/policies/audit-tier-policy.json classify \
  --feature <NNN> --phase pre-implement \
  --feature-map docs/prd/feature-map.md \
  --spec specs/[spec-id]/spec.md \
  --plan specs/[spec-id]/plan.md \
  --tasks specs/[spec-id]/tasks.md --ledger
python3 .specify/scripts/python/classify_audit_tier.py \
  --policy .specify/policies/audit-tier-policy.json gate-status \
  --feature <NNN> --station analyze
```

If `--raise-audit-tier` was explicitly supplied, pass it only as the
classifier's upward-only `--raise-tier T2|T3` option. Reject every model,
effort, reviewer-skip, scope-lowering, or tier-lowering flag. Stop on a stale,
malformed, missing, or capability-mismatched receipt. Use its exact
`tier_settings` below.

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

Invoke both Codex and Antigravity for independent semantic reviews. T1 does not
reduce reviewer count.

Before dispatching, compute the tasks hash and substitute it (with the Feature
number) into both prompts — the aggregation rejects a report bound to a stale
`tasks.md` revision:

```bash
TASKS_SHA=$(sha256sum specs/[spec-id]/tasks.md | awk '{print $1}')
```

#### 0. External Agent Preflight (session-level, once)

Apply the Preflight and Degrade Rule from
`.claude/skills/specter-agent-protocols/SKILL.md` (§1–2). For this command: a **dual-agent
station** — if one agent is unavailable after preflight + one retry, run it single-agent and
write the §2 degrade placeholder (a VALID report — `**Mode**: agent-document-consistency`,
`**Feature**:`, `**Tasks SHA256**:`, `**Result**: WARN`, `**Availability**: UNAVAILABLE
(<reason>)`) at the missing agent's report path (`specs/[spec-id]/analyze.codex.md` /
`analyze.antigravity.md`); the Layer-3 aggregation then caps the station at `WARN`
mechanically. Never present a single-agent run as dual; never block `/ms.analyze` on an
environment issue alone except when both reviewers are unavailable, which
stops the station. A T3 single-agent environmental degrade requires explicit
human acknowledgment after aggregation.

#### A. Codex Review
```text
/codex:rescue --fresh --model gpt-5.6-luna --effort <receipt.tier_settings.reviewer_effort.codex> <prompt>
```
Codex must read:
- `.specify/memory/constitution.md`
- `AGENTS.md` if it exists
- `docs/prd/feature-map.md`
- `docs/prd/feature-map.checklist.md`
- `docs/prd/checklists/feature-NNN.checklist.md`
- `docs/prd/checklists/feature-NNN.codex-verify.md`
- `docs/prd/checklists/feature-NNN.antigravity-verify.md`
- `specs/[spec-id]/spec.md`
- `specs/[spec-id]/plan.md`
- `specs/[spec-id]/tasks.md`

Codex must write:
`specs/[spec-id]/analyze.codex.md`

Codex prompt:
```text
You are performing an advisory SPECTER document consistency review.

Check spec.md, plan.md, and tasks.md against the Feature Map evidence,
Constitution, and prior checklist gates. Do not edit files except writing
specs/[spec-id]/analyze.codex.md.

Focus on:
- spec FRs missing from tasks
- tasks with no spec, plan, setup, or verification source
- plan components, migrations, APIs, or test strategies missing from tasks
- contradictions between spec, plan, and tasks
- stale or incomplete Amendment handling
- migration number, file path, or contract drift
- Feature Map commitments that no longer survive into spec/plan/tasks
- inconsistencies between Audit signals and the now-concrete spec, plan, or tasks
- the receipt-bound review scope: <receipt.tier_settings.review_scope>
- every applicable identifier in
  `<receipt.tier_settings.targeted_checks>`; reviewers do not add or remove
  policy modules

Write:

# Codex Analyze Review

**Mode**: agent-document-consistency
**Feature**: Feature {NNN}
**Tasks SHA256**: {TASKS_SHA}
**Result**: PASS | WARN | FAIL

## Findings

| Severity | Finding | Evidence | Required Fix |
| --- | --- | --- | --- |

## Verdict

One concise paragraph.

Also echo the finished report between ===REPORT BEGIN=== and ===REPORT END=== markers in your
final message, verbatim, so it can be salvaged if the file write fails.
```

#### B. Antigravity Review
```text
/antigravity:rescue --fresh --model gemini-3.5-flash --effort <receipt.tier_settings.reviewer_effort.antigravity> <prompt>
```
Antigravity must read:
- `.specify/memory/constitution.md`
- `AGENTS.md` if it exists
- `docs/prd/feature-map.md`
- `docs/prd/feature-map.checklist.md`
- `docs/prd/checklists/feature-NNN.checklist.md`
- `docs/prd/checklists/feature-NNN.antigravity-verify.md`
- `specs/[spec-id]/spec.md`
- `specs/[spec-id]/plan.md`
- `specs/[spec-id]/tasks.md`

Antigravity must write:
`specs/[spec-id]/analyze.antigravity.md`

Antigravity prompt:
```text
You are performing an advisory SPECTER document consistency review using Google Antigravity.

Check spec.md, plan.md, and tasks.md against the Feature Map evidence,
Constitution, and prior checklist gates. Do not edit files except writing
specs/[spec-id]/analyze.antigravity.md.

Focus on:
- spec FRs missing from tasks
- tasks with no spec, plan, setup, or verification source
- plan components, migrations, APIs, or test strategies missing from tasks
- contradictions between spec, plan, and tasks
- stale or incomplete Amendment handling
- migration number, file path, or contract drift
- Feature Map commitments that no longer survive into spec/plan/tasks
- inconsistencies between Audit signals and the now-concrete spec, plan, or tasks
- the receipt-bound review scope: <receipt.tier_settings.review_scope>
- every applicable identifier in
  `<receipt.tier_settings.targeted_checks>`; reviewers do not add or remove
  policy modules

Write:

# Antigravity Analyze Review

**Mode**: agent-document-consistency
**Feature**: Feature {NNN}
**Tasks SHA256**: {TASKS_SHA}
**Result**: PASS | WARN | FAIL

## Findings

| Severity | Finding | Evidence | Required Fix |
| --- | --- | --- | --- |

## Verdict

One concise paragraph.

Also echo the finished report between ===REPORT BEGIN=== and ===REPORT END=== markers in your
final message, verbatim, so it can be salvaged if the file write fails.
```

If the user supplied `--background`, add `--background` to both invocations and
report that `/ms.analyze` must be rerun after both files appear.

**Report-Write Protocol**: apply `specter-agent-protocols` §3 — deterministic file check
(exists, non-empty, contains `**Result**:`), retry once, salvage from the
`===REPORT BEGIN===`/`===REPORT END===` markers. If no markers exist either, that is an
**agent-authored failure**: leave the report missing/invalid for the aggregation to grade
`FAIL` (§3 step 3) — the subsection-0 Degrade Rule applies only to preflight failures,
never to an agent that ran.

#### C. Layer-3 Aggregation (mechanical — replaces host result-weighing)

If `--background` was used and either report file has not appeared yet, report
`PENDING` and stop — do **not** run the aggregation against a missing report
(it would grade the absence as FAIL, which is the wrong signal for a
still-running agent). Otherwise:

```bash
.specify/scripts/bash/specter-gate.sh aggregate analyze specs/[spec-id] --ledger --round <R>
```

`<R>` is the current §4 convergence round and must not exceed
`receipt.tier_settings.max_automatic_rounds`. Every round uses `--fresh`.

- The receipt `verdict` is the agent-station outcome; the final `/ms.analyze`
  result is the **worse** of Step 2's host result and the receipt verdict.
- The host never downgrades an agent `WARN`/`FAIL` by explaining it as a false
  positive (`specter-agent-protocols` §5 no-unilateral-host-downgrade). A
  disputed finding goes back as a scoped §4 re-round — dispatched `--fresh`,
  prior findings passed as report file paths — where only the reviewing agent
  may revise its own grade against changed evidence.

#### D. Convergence Policy (re-round caps)

Apply the receipt-bound Convergence Policy from
`specter-agent-protocols` §4 (T1 currently at most 2 automatic rounds; T2/T3
currently at most 3; Round 2+ scoped to failing findings only; stop when only
`WARN`s remain). Exhausting the budget leaves an unresolved FAIL as FAIL and
returns control to the user. Record every residual WARN.

### Step 4: Result Model

Use this result model:

- `PASS`: `/ms.implement` may proceed.
- `WARN`: `/ms.implement` may proceed only after the receipt's WARN policy is
  satisfied. T3 always requires explicit human acknowledgment; this includes a
  one-agent environmental-degrade cap.
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

When the aggregate reports `warn_ack_required: true`, stop and show its
reasons/cap. Only after explicit user acknowledgment run:

```bash
python3 .specify/scripts/python/classify_audit_tier.py \
  --policy .specify/policies/audit-tier-policy.json acknowledge-warn \
  --feature <NNN> --station analyze --actor human
.specify/scripts/bash/specter-gate.sh aggregate analyze specs/[spec-id]
```

Advance only when `warn_ack_satisfied` is true. The conductor's act of
recording a warning is not a substitute for T3 human acknowledgment.

### Step 5: Report

Display a Korean summary:

```json
{
  "document_consistency": "PASS|WARN|FAIL",
  "audit_tier": "T1|T2|T3",
  "codex_analysis": "PASS|WARN|FAIL|PENDING",
  "codex_report": "specs/{id}/analyze.codex.md",
  "antigravity_analysis": "PASS|WARN|FAIL|PENDING",
  "antigravity_report": "specs/{id}/analyze.antigravity.md",
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

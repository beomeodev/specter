---
description: "Run a foreground Codex & Antigravity verification of the current per-Feature checklist"
argument-hint: "[Feature NNN] [--model MODEL] [--effort low|medium|high|xhigh|max]"
---

# /ms.agent-verify - Per-Feature Dual-Agent Verification

Run Codex and Antigravity in the foreground (in parallel) to review the current per-Feature checklist. This command is advisory, but `/ms.specify` requires both result files unless the user explicitly skips verification.

Execution is foreground: Codex and Antigravity run in parallel and this command returns only after both have finished and written their reports. Running in the foreground makes write failures or crashes observable immediately instead of leaving a silently missing output file.

Default Codex/Antigravity runtimes:
```text
Codex model: gpt-5.6-luna
Antigravity model: gemini-3.5-flash
effort: xhigh
```

## Usage

```bash
/ms.agent-verify
/ms.agent-verify Feature 003
/ms.agent-verify --model gpt-5.6-luna --effort xhigh Feature 003
```

## Output

Codex must write:
```text
docs/prd/checklists/feature-NNN.codex-verify.md
```

Antigravity must write:
```text
docs/prd/checklists/feature-NNN.antigravity-verify.md
```

## Execution Steps

### Step 0: Resolve Target Feature

If the user names a Feature (`Feature 003`, `003`, or a matching Feature title), use that Feature.

Otherwise, infer the latest per-Feature checklist from:
```text
docs/prd/checklists/feature-NNN.checklist.md
```

If no per-Feature checklist exists, stop and tell the user to run `/ms.checklist` first.

Then verify the checklist is actually usable — existence alone is not the gate. Run the
deterministic checker for the resolved Feature:

```bash
# self-heal: the runtime copy is project-local (never synced); refresh it from the synced template
install -D -m 0755 docs/templates/scripts/specter-gate.sh .specify/scripts/bash/specter-gate.sh
.specify/scripts/bash/specter-gate.sh NNN
```

If `feature_checklist_result_ok` is false (Result is FAIL/missing) or `feature_checklist_sha_ok`
is false (the Feature Map changed since the checklist was written), stop and tell the user to
fix the Feature section and re-run `/ms.checklist` — dual-agent verification of a failed or
stale checklist wastes both agents. Ignore this script's `codex_verify`/`antigravity_verify`
fields here; producing those files is this command's own job.

Then run the Layer-1 structural check as a second fail-fast (three-layer
contract, `specter-agent-protocols` §7):

```bash
.specify/scripts/bash/specter-gate.sh structural NNN
```

If its `verdict` is `FAIL` (placeholder in done criteria, cited C-ID missing
from the Codex checklist, malformed Feature section), stop and route back to
`/ms.checklist` — structural defects are mechanical and do not need two agents
to find.

**Session read policy**: per AGENTS.md §2 — reuse files already read this session; a fresh `Read` immediately before `Edit`/`Write` is still required.

### Step 0.5: External Agent Preflight (session-level, once)

Apply the Preflight and Degrade Rule from
`.claude/skills/specter-agent-protocols/SKILL.md` (§1–2). For this command: a
**dual-agent station** — if one agent is unavailable after preflight + one retry,
run the station single-agent and write the §2 degrade placeholder (a VALID
report — `**Mode**:` with this station's normal value, `**Feature**:`,
`**Checklist SHA256**:`, `**Result**: WARN`, `**Availability**: UNAVAILABLE
(<reason>)`) at the missing agent's report path
(`feature-NNN.codex-verify.md` / `feature-NNN.antigravity-verify.md`); the
Layer-3 aggregation then caps the station at `WARN` mechanically. A bare
`<Agent>: UNAVAILABLE` line is not a valid placeholder. Never present a
single-agent run as dual; never block the cycle on an environment issue alone.

### Step 1: Run Codex & Antigravity In Foreground (Parallel)

Invoke the Codex and Antigravity plugin rescue commands in the foreground, in parallel, and wait for both to finish before reporting:

#### A. Run Codex
```text
/codex:rescue --fresh --model gpt-5.6-luna --effort xhigh <Codex Prompt>
```

#### B. Run Antigravity
```text
/antigravity:rescue --fresh --model gemini-3.5-flash --effort medium <Antigravity Prompt>
```

If the user provided `--model` or `--effort`, pass those values through instead of the defaults.

**Report-Write Protocol**: apply `specter-agent-protocols` §3 — deterministic file check
(exists, non-empty, contains `**Result**:`), retry once, salvage from the
`===REPORT BEGIN===`/`===REPORT END===` markers. If no markers exist either, that is an
**agent-authored failure**: leave the report missing/invalid for the aggregation to grade
`FAIL` (§3 step 3) — the Step 0.5 Degrade Rule applies only to preflight failures, never
to an agent that ran.

### Step 2: Agent Prompts

Before dispatching, compute the current checklist hash and substitute it into
both prompts (the gate verifies it — a report hashed against an older
checklist revision is stale and FAILs):

```bash
CHECKLIST_SHA=$(sha256sum docs/prd/checklists/feature-NNN.checklist.md | awk '{print $1}')
```

#### A. Codex Prompt
Forward this task to Codex:

```text
You are verifying one SPECTER per-Feature checklist. Keep output short.

Read:
- docs/prd/feature-map.md
- docs/prd/feature-map.checklist.md
- docs/prd/checklists/feature-NNN.checklist.md
- the Source PRDs and PRD references named by Feature NNN
- docs/prd/codex/checklist.md if it exists

Do not edit the Feature Map, PRDs, specs, plans, tasks, or canonical checklist.
Only write docs/prd/checklists/feature-NNN.codex-verify.md.

Check only for blocking or high-signal issues:
- owned PRD commitments missing from Feature scope, out-of-scope, decisions, or done criteria
- acceptance criteria or NFRs missing from done criteria or tests
- overreach into another Feature's owned commitments
- out-of-scope items without destination Features
- done criteria that are not observable or do not end with "CI passes green"
- invented behavior not supported by PRD evidence

Write this concise output:

# Feature NNN Codex Verification

**Mode**: codex-per-feature-verify
**Feature**: Feature NNN
**Checklist**: docs/prd/checklists/feature-NNN.checklist.md
**Checklist SHA256**: {CHECKLIST_SHA}
**Result**: PASS | WARN | FAIL
**Generated By**: Codex

## Findings

| Severity | Finding | Evidence | Required Fix |
| --- | --- | --- | --- |

## Verdict

One short paragraph. If no blocking findings exist, say so directly.

Also echo the finished report between ===REPORT BEGIN=== and ===REPORT END=== markers in your
final message, verbatim, so it can be salvaged if the file write fails.
```

#### B. Antigravity Prompt
Forward this task to Antigravity:

```text
You are verifying one SPECTER per-Feature checklist using Google Antigravity. Keep output short.

Read:
- docs/prd/feature-map.md
- docs/prd/feature-map.checklist.md
- docs/prd/checklists/feature-NNN.checklist.md
- the Source PRDs and PRD references named by Feature NNN
- docs/prd/feature-map.antigravity-checklist.md if it exists

Do not edit the Feature Map, PRDs, specs, plans, tasks, or canonical checklist.
Only write docs/prd/checklists/feature-NNN.antigravity-verify.md.

Check only for blocking or high-signal issues:
- owned PRD commitments missing from Feature scope, out-of-scope, decisions, or done criteria
- acceptance criteria or NFRs missing from done criteria or tests
- overreach into another Feature's owned commitments
- out-of-scope items without destination Features
- done criteria that are not observable or do not end with "CI passes green"
- invented behavior not supported by PRD evidence

Write this concise output:

# Feature NNN Antigravity Verification

**Mode**: antigravity-per-feature-verify
**Feature**: Feature NNN
**Checklist**: docs/prd/checklists/feature-NNN.checklist.md
**Checklist SHA256**: {CHECKLIST_SHA}
**Result**: PASS | WARN | FAIL
**Generated By**: Antigravity

## Findings

| Severity | Finding | Evidence | Required Fix |
| --- | --- | --- | --- |

## Verdict

One short paragraph. If no blocking findings exist, say so directly.

Also echo the finished report between ===REPORT BEGIN=== and ===REPORT END=== markers in your
final message, verbatim, so it can be salvaged if the file write fails.
```

### Step 3: Layer-3 Aggregation And Report

After both agents finish, compute the station verdict mechanically — never by
reading and weighing the reports yourself (`specter-agent-protocols` §7):

```bash
.specify/scripts/bash/specter-gate.sh aggregate agent-verify NNN --ledger --round <R>
```

`<R>` is the current §4 convergence round (1 on the first run, 2/3 on
re-rounds) — the receipt records which round produced this verdict.

The receipt JSON is the station's outcome of record: per-report grading
(including SHA staleness and degrade placeholders), the station `verdict`, any
`cap`, and verbatim `caught` rows. `--ledger` appends the
`.specify/specter-run.jsonl` line mechanically — do not hand-write one for
this station.

Display in Korean, quoting the receipt's values verbatim:
```text
Codex 및 Antigravity Feature checklist 검증을 완료했습니다.

📄 산출물:
- docs/prd/checklists/feature-NNN.codex-verify.md (<receipt input result>)
- docs/prd/checklists/feature-NNN.antigravity-verify.md (<receipt input result>)
⚖️ 집계 verdict: <receipt verdict> (기계 판정 — specter-gate.sh aggregate)
🎯 다음 단계: /ms.specify

verdict가 PASS/WARN이면 /ms.specify로 진행할 수 있습니다.
FAIL이면 체크리스트를 수정한 뒤 /ms.agent-verify를 다시 실행하세요.
(재실행 라운드도 항상 --fresh — 이전 지적은 리포트 파일 경로로 전달됩니다.)
```

## Run-State Ledger

Emitted mechanically by Step 3's `aggregate --ledger`
(`specter-agent-protocols` §7 Mechanical ledger): `caught` rows are copied
verbatim from the reports' Findings tables and `cap` is the receipt's
classification. The host never authors or edits this station's ledger line —
re-rounds overwrite report files, and the mechanical line is where the
original catch survives for gate-value audits.

## Next Command

Run `/ms.specify` after both verification reports show PASS/WARN.

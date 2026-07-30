---
description: "Run a foreground Codex & Antigravity verification of the current per-Feature checklist"
argument-hint: "[Feature NNN] [--raise-risk]"
---

# /ms.verify - Per-Feature Dual-Agent Verification (verification-v2)

Run Codex and Antigravity in the foreground (in parallel) to review the current
per-Feature checklist. This is a required dual-agent semantic verification
station. There is no reviewer-skip path.

Execution is foreground: Codex and Antigravity run in parallel and this command
returns only after both have finished and written their reports. Running in the
foreground makes write failures or crashes observable immediately instead of
leaving a silently missing output file.

Reviewer effort is fixed (`codex: xhigh`, `antigravity: medium`, both risk
profiles). The risk profile, round budget, and report validity come from
`specter-gate.sh` mechanically. The command never chooses or lowers them.

## Usage

```bash
/ms.verify
/ms.verify Feature 003
/ms.verify Feature 003 --raise-risk
```

## Output (round-numbered — a new round is a new file, never an overwrite)

```text
docs/prd/checklists/feature-NNN.codex-verify.r<R>.md
docs/prd/checklists/feature-NNN.antigravity-verify.r<R>.md
.specify/verification-v2/verify-NNN.json   (station receipt, gate-written)
```

## Execution Steps

### Step 0: Resolve Target Feature And Preconditions

If the user names a Feature (`Feature 003`, `003`, or a matching Feature title), use that Feature.

Otherwise, infer the latest per-Feature checklist from:
```text
docs/prd/checklists/feature-NNN.checklist.md
```

If no per-Feature checklist exists, stop and tell the user to run `/ms.checklist` first.

Then verify the checklist is actually usable — existence alone is not the gate:

```bash
# self-heal: the runtime copy is project-local (never synced); refresh it from the synced template
install -D -m 0755 docs/templates/scripts/specter-gate.sh .specify/scripts/bash/specter-gate.sh
install -D -m 0644 docs/templates/verification-v2.json .specify/policies/verification-v2.json
.specify/scripts/bash/specter-gate.sh version | grep -q '"contract": "verification-v2"' \
  || { echo "partial sync — run /ms.sync (or /ms.init) first"; }
.specify/scripts/bash/specter-gate.sh NNN
```

If `feature_checklist_result_ok` is false (Result is FAIL/missing) or
`feature_checklist_sha_ok` is false (the Feature Map changed since the
checklist was written), stop and tell the user to fix the Feature section and
re-run `/ms.checklist` — dual-agent verification of a failed or stale checklist
wastes both agents. Ignore this probe's `verify_receipt_*` fields here;
producing that receipt is this command's own job.

Then run the Layer-1 structural check as a second fail-fast (three-layer
contract, `specter-agent-protocols` §7):

```bash
.specify/scripts/bash/specter-gate.sh structural NNN
```

If its `verdict` is `FAIL` (placeholder in done criteria, cited C-ID missing
from the baseline checklist, malformed Feature section or Verification-signals
table), stop and route back to `/ms.checklist` — structural defects are
mechanical and do not need two agents to find.

Reject `--model`, `--effort`, `--skip-codex`, `--skip-agents`, and equivalent
bypass or scope-lowering arguments. The only risk flag is the upward-only
`--raise-risk` (passed through to Step 3's aggregate).

**Session read policy**: per AGENTS.md §2 — reuse files already read this session; a fresh `Read` immediately before `Edit`/`Write` is still required.

### Step 0.5: External Agent Preflight (session-level, once)

Apply the Preflight and Degrade Rule from
`.claude/skills/specter-agent-protocols/SKILL.md` (§1–2). For this command: a
**dual-agent station** — if one agent is unavailable after preflight + one
retry, run the station single-agent and write the §2 degrade placeholder (a
VALID v2 report — `**Contract**`, `**Mode**` with this station's normal value,
`**Scope**`, `**Input Digest**`, `**Result**: WARN`, `**Availability**:
UNAVAILABLE (<reason>)`) at the missing agent's round-numbered report path;
Layer 3 then caps the station at `WARN` mechanically. Never present a
single-agent run as dual. If both independent reviewers are unavailable, stop
the station.

### Step 1: Compute The Input Digest And Round

```bash
DIGEST=$(.specify/scripts/bash/specter-gate.sh digest verify NNN | python3 -c "import json,sys; print(json.load(sys.stdin)['input_digest'])")
```

The digest binds both reports to the exact artifacts under review; a report
whose digest no longer matches is stale and FAILs at aggregation.

Round `R` starts at 1. A re-round (R = 2) runs only after a FAIL round whose
findings were repaired; it is scoped to the failing findings plus the fix
diffs, and both prior-round report paths are passed into the prompts. Rounds
beyond 2 are refused by the gate without a recorded `authorize-round` decision
(protocols §4).

### Step 2: Run Codex & Antigravity In Foreground (Parallel)

```text
/codex:rescue --fresh --model gpt-5.6-luna --effort xhigh <Codex Prompt>
/antigravity:rescue --fresh --model gemini-3.5-flash --effort medium <Antigravity Prompt>
```

Both invocations are always `--fresh`. When the risk profile is high-risk
(any declared `yes` signal — visible in the last receipt, or evident from the
Feature's Verification-signals table), append the applicable named checks from
`verification-v2.json` `high_risk_checks` to both prompts and widen the review
scope to affected trust boundaries.

#### Prompt (same body for both agents; substitute AGENT/MODE/REPORT values)

Codex: `MODE=codex-per-feature-verify`, `REPORT=docs/prd/checklists/feature-NNN.codex-verify.r{R}.md`
Antigravity: `MODE=antigravity-per-feature-verify`, `REPORT=docs/prd/checklists/feature-NNN.antigravity-verify.r{R}.md`

```text
You are verifying one SPECTER per-Feature checklist. Keep output short.

Read:
- docs/prd/feature-map.md
- docs/prd/feature-map.checklist.md
- docs/prd/checklists/feature-NNN.checklist.md
- the Source PRDs and PRD references named by Feature NNN
- docs/prd/featuremap-checklist.md if it exists (legacy path: docs/prd/codex/checklist.md)

Do not edit the Feature Map, PRDs, specs, plans, tasks, or canonical checklist.
Only write {REPORT}.

Check only for blocking or high-signal issues:
- owned PRD commitments missing from Feature scope, out-of-scope, decisions, or done criteria
- acceptance criteria or NFRs missing from done criteria or tests
- overreach into another Feature's owned commitments
- out-of-scope items without destination Features
- done criteria that are not observable or do not end with "CI passes green"
- untagged invention per the .claude/skills/specter-agent-protocols/SKILL.md §10
  authority lattice: behavior supported by neither PRD evidence, a PRD
  Amendment, nor a recorded clarify interpretation citing its C-/D-ID. A D-ID
  or clarify record used to justify NEW observable scope is itself a finding
- Verification-signal values (### Verification signals) that contradict or
  understate the cited PRD evidence — a declared "no" the artifacts contradict
  is a blocking finding

{On round R >= 2 add: Re-round continuity: read the prior round's reports
first — <prior codex report path> and <prior antigravity report path>. They
are NOT a PASS whitelist and do not suppress discovery. Re-check every prior
blocking finding by ID and mark each `resolved` or `persists` in your Findings
State column. A grade may improve only against changed, cited evidence. If
your own lane previously prescribed the state you now reject, say so
explicitly, cite the prior finding ID, and recommend escalation.}

{When high-risk add: High-risk profile — additionally run these named checks
and report each as one row in a "## High-risk checks" table (one row per
triggered signal): <applicable high_risk_checks>.}

Write this concise output to {REPORT}:

# {AGENT} Verify Verification — Feature NNN — Round {R}

**Contract**: verification-v2
**Mode**: {MODE}
**Scope**: Feature NNN
**Input Digest**: {DIGEST}
**Result**: PASS | WARN | FAIL

## Scope and evidence
**Checked**: <named check classes, with file:line citations or commands>
**Not checked**: <explicit exclusions with reasons, or the evidence basis for claiming none>

## Findings
| ID | Severity | State | Finding | Evidence | Required Fix |
| --- | --- | --- | --- | --- | --- |

(IDs stable within your lane, e.g. CX-V-001 / AG-V-001. State: new | persists |
resolved. Required Fix = restored invariant + minimum repair + no new scope;
escalate instead of choosing when several product interpretations remain valid.)

## Verdict

One short paragraph. If no blocking findings exist, say so directly.

Also echo the finished report between ===REPORT BEGIN=== and ===REPORT END===
markers in your final message, verbatim, so it can be salvaged if the file
write fails.
```

### Step 2.5: Validate, Salvage, Format-Retry (per agent)

Apply protocols §3. For each report:

```bash
.specify/scripts/bash/specter-gate.sh validate-report <REPORT> verify NNN --round <R>
```

Invalid → salvage from the `===REPORT BEGIN/END===` markers → re-validate →
still invalid → re-dispatch **that one agent** once, same round, with the
validator's `errors` list prefixed to its prompt. Track the retry count per
agent for Step 3's `--format-retries`. Still invalid after the retry → leave
the file as-is; Layer 3 grades it FAIL (agent-authored failure — never a §2
placeholder).

### Step 3: Layer-3 Aggregation And Report

Compute the station verdict mechanically — never by reading and weighing the
reports yourself (protocols §7):

```bash
.specify/scripts/bash/specter-gate.sh aggregate verify NNN --ledger --round <R> \
  [--raise-risk] [--format-retries "<codex-retries> <antigravity-retries>"]
```

The receipt JSON is the station's outcome of record: risk profile + evidence,
per-report grading (including digest staleness and degrade placeholders), the
station `verdict`, any `cap`, and verbatim `caught` rows. `--ledger` appends
the `.specify/specter-run.jsonl` line mechanically — do not hand-write one for
this station.

- `verdict: PASS` → proceed.
- `verdict: WARN` → recorded in receipt and ledger; proceeds (protocols §8 —
  the only verify-station human stop is an `ack-degrade` when the missing
  reviewer was needed for a triggered high-risk check).
- `verdict: FAIL` with findings → repair the checklist defects, then run the
  one scoped re-round (R = 2, fresh, prior report paths in the prompts).
- Still FAIL at the cap → present the §4 post-cap options verbatim (fix and
  restart / amend authority / authorize one doctrine-dispute round via
  `specter-gate.sh decide authorize-round verify NNN --round 3 --reason "..."`
  / accept WARN via `decide accept-warn` / stop) — never "run one more
  round?".

Display in Korean, quoting the receipt's values verbatim:
```text
Codex 및 Antigravity Feature checklist 검증을 완료했습니다.

📄 산출물:
- docs/prd/checklists/feature-NNN.codex-verify.r<R>.md (<receipt input graded>)
- docs/prd/checklists/feature-NNN.antigravity-verify.r<R>.md (<receipt input graded>)
⚖️ 집계 verdict: <receipt verdict> (기계 판정 — specter-gate.sh aggregate)
🎯 위험 프로파일: <receipt risk_profile> (<receipt risk_evidence 요약>)
🎯 다음 단계: /ms.specify

verdict가 PASS/WARN이면 /ms.specify로 진행할 수 있습니다.
FAIL이면 체크리스트를 수정한 뒤 /ms.verify 재라운드(R=2)를 실행하세요.
(재라운드도 항상 --fresh — 이전 지적은 이전 라운드 리포트 파일 경로로 전달됩니다.)
```

## Run-State Ledger

Emitted mechanically by Step 3's `aggregate --ledger` (protocols §7): `caught`
rows are copied verbatim from the reports' Findings tables. The host never
authors or edits this station's ledger line — round-numbered report files plus
the append-only ledger are where the original catch survives for gate-value
audits.

## Next Command

Run `/ms.specify` after the mechanical aggregate is PASS, or WARN with any
required decision events recorded.

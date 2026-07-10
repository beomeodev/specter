---
description: "Run a foreground Codex & Antigravity verification of the current per-Feature checklist"
argument-hint: "[Feature NNN] [--model MODEL] [--effort low|medium|high]"
---

# /ms.agent-verify - Per-Feature Dual-Agent Verification

Run Codex and Antigravity in the foreground (in parallel) to review the current per-Feature checklist. This command is advisory, but `/ms.specify` requires both result files unless the user explicitly skips verification.

Execution is foreground: Codex and Antigravity run in parallel and this command returns only after both have finished and written their reports. Running in the foreground makes write failures or crashes observable immediately instead of leaving a silently missing output file.

Default Codex/Antigravity runtimes:
```text
Codex model: gpt-5.6-sol
Antigravity model: gemini-3.5-flash
effort: medium
```

## Usage

```bash
/ms.agent-verify
/ms.agent-verify Feature 003
/ms.agent-verify --model gpt-5.6-sol --effort high Feature 003
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

**Session read policy**: per AGENTS.md §2 — reuse files already read this session; a fresh `Read` immediately before `Edit`/`Write` is still required.

### Step 0.5: External Agent Preflight (session-level, once)

Apply the Preflight and Degrade Rule from
`.claude/skills/specter-agent-protocols/SKILL.md` (§1–2). For this command: a
**dual-agent station** — if one agent is unavailable after preflight + one retry,
run the station single-agent, cap the station result at `WARN`, and write
`<Agent>: UNAVAILABLE (<reason>)` into the missing agent's report path
(`feature-NNN.codex-verify.md` / `feature-NNN.antigravity-verify.md`). Never
present a single-agent run as dual; never block the cycle on an environment
issue alone.

### Step 1: Run Codex & Antigravity In Foreground (Parallel)

Invoke the Codex and Antigravity plugin rescue commands in the foreground, in parallel, and wait for both to finish before reporting:

#### A. Run Codex
```text
/codex:rescue --fresh --model gpt-5.6-sol --effort medium <Codex Prompt>
```

#### B. Run Antigravity
```text
/antigravity:rescue --fresh --model gemini-3.5-flash --effort medium <Antigravity Prompt>
```

If the user provided `--model` or `--effort`, pass those values through instead of the defaults.

**Report-Write Protocol**: apply `specter-agent-protocols` §3 — deterministic file check
(exists, non-empty, contains `**Result**:`), retry once, salvage from the
`===REPORT BEGIN===`/`===REPORT END===` markers, and only then fall back to the Step 0.5
Degrade Rule.

### Step 2: Agent Prompts

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
**Checklist**: docs/prd/checklists/feature-NNN.checklist.md
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
**Checklist**: docs/prd/checklists/feature-NNN.checklist.md
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

### Step 3: Report

After both agents finish, read each report's **Result** and display in Korean:
```text
Codex 및 Antigravity Feature checklist 검증을 완료했습니다.

📄 산출물:
- docs/prd/checklists/feature-NNN.codex-verify.md (<PASS|WARN|FAIL>)
- docs/prd/checklists/feature-NNN.antigravity-verify.md (<PASS|WARN|FAIL>)
🎯 다음 단계: /ms.specify

두 결과가 모두 PASS/WARN이면 /ms.specify로 진행할 수 있습니다.
하나라도 FAIL이면 체크리스트를 수정한 뒤 /ms.agent-verify를 다시 실행하세요.
```

## Run-State Ledger (bookkeeping, not a gate)

Append one line to `.specify/specter-run.jsonl` (create it if needed; append-only, never
rewritten — a missing/corrupt ledger never blocks this command, it only speeds up conductor
resume). Set `verdict` to the worse of the two agents' Results (FAIL > WARN > PASS) and `feature`
to the Feature number as a string:

```bash
mkdir -p .specify
printf '{"ts":"%s","cycle":"feature","feature":"%s","step":"agent-verify","verdict":"%s","artifacts":["docs/prd/checklists/feature-%s.codex-verify.md","docs/prd/checklists/feature-%s.antigravity-verify.md"]}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "<NNN>" "<PASS|WARN|FAIL>" "<NNN>" "<NNN>" >> .specify/specter-run.jsonl
```

On `WARN`/`FAIL`, extend the JSON with `caught` — an array of short **verbatim quotes** from
the two verify reports, one per real finding (never paraphrase or re-grade; `[]` if the
non-PASS verdict carried no content finding) — and, only when the verdict was capped by an
environmental degrade rather than by findings, `cap` with the reason (e.g.
`"single-agent-degrade"`). PASS lines stay minimal. Re-rounds overwrite report files; this
ledger line is where the original catch survives for gate-value audits. Example:

```json
{"ts":"…","cycle":"feature","feature":"006","step":"agent-verify","verdict":"WARN","artifacts":["…"],"caught":["checklist cites fabricated C220; C144 missing"],"cap":"single-agent-degrade"}
```

## Next Command

Run `/ms.specify` after both verification reports show PASS/WARN.

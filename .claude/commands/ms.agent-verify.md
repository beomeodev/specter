---
description: "Run a foreground Codex & Antigravity verification of the current per-Feature checklist"
argument-hint: "[Feature NNN] [--model MODEL] [--effort low|medium|high]"
---

# /ms.agent-verify - Per-Feature Dual-Agent Verification

Run Codex and Antigravity in the foreground (in parallel) to review the current per-Feature checklist. This command is advisory, but `/ms.specify` requires both result files unless the user explicitly skips verification.

Execution is foreground: Codex and Antigravity run in parallel and this command returns only after both have finished and written their reports. Running in the foreground makes write failures or crashes observable immediately instead of leaving a silently missing output file.

Default Codex/Antigravity runtimes:
```text
Codex model: gpt-5.5
Antigravity model: gemini-3.5-flash
effort: medium
```

## Usage

```bash
/ms.agent-verify
/ms.agent-verify Feature 003
/ms.agent-verify --model gpt-5.5 --effort high Feature 003
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

### Step 0.5: External Agent Preflight (session-level, once)

Before invoking Codex or Antigravity, check availability **once per session** and remember the
result — do not re-check on every `/ms.agent-verify` call within the same session:

- **Codex**: the `codex` binary is on PATH, auth is configured, and its sandbox mode in
  `~/.codex/config.toml` is not read-only (e.g. `workspace-write` or `danger-full-access`) — a
  cheap config check, not a live probe run.
- **Antigravity**: the `agy` binary is on PATH, auth is configured, and its write flag is set (a
  cheap config check, not a live probe run).

If a check fails, retry once (a plugin update can transiently reset a flag). If it still fails,
apply the Degrade Rule below instead of blocking the whole command.

**Degrade Rule**:
- Antigravity unavailable after retry → run this station **Codex-only**, force the station result
  to at most `WARN`, and record `Antigravity: UNAVAILABLE (<reason>)` in
  `feature-NNN.antigravity-verify.md` in place of a normal report.
- Codex unavailable after retry → run this station **Antigravity-only**, force the station result
  to at most `WARN`, and record `Codex: UNAVAILABLE (<reason>)` in `feature-NNN.codex-verify.md`.
- Never silently report this dual-agent station's result as if both agents ran when only one did.
- Never block the whole per-Feature cycle on an external-agent environment issue alone — degrade,
  record it, and continue.

### Step 1: Run Codex & Antigravity In Foreground (Parallel)

Invoke the Codex and Antigravity plugin rescue commands in the foreground, in parallel, and wait for both to finish before reporting:

#### A. Run Codex
```text
/codex:rescue --fresh --model gpt-5.5 --effort medium <Codex Prompt>
```

#### B. Run Antigravity
```text
/antigravity:rescue --fresh --model gemini-3.5-flash --effort medium <Antigravity Prompt>
```

If the user provided `--model` or `--effort`, pass those values through instead of the defaults.

**Report-Write Protocol**: agents still write their own report files (unchanged, primary path).
Each prompt in Step 2 additionally requires echoing the finished report between
`===REPORT BEGIN===` / `===REPORT END===` markers in the agent's final message — near-zero
marginal cost, since the agent emits a final message regardless. After the run, deterministically
check the written report file: it exists, is non-empty, and contains `**Result**:`.

If either agent fails to write its `*-verify.md` report (crash, partial output, or write error),
retry that agent once. If it still fails: **salvage** the report by writing the file from the
`===REPORT BEGIN===`/`===REPORT END===` markers captured in that retry's final message, instead of
stopping the whole gate or hand-transcribing the report yourself. If no markers were captured
either (the agent produced no usable final message), apply the availability Degrade Rule from
Step 0.5 instead of stopping outright.

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
- docs/prd/antigravity/checklist.md if it exists

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

## Next Command

Run `/ms.specify` after both verification reports show PASS/WARN.

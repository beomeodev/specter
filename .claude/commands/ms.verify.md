---
description: "Verify Feature Map against PRDs and the independent Codex checklist"
argument-hint: ""
---

# /ms.verify - Global Feature Map Verification

Verify `docs/prd/feature-map.md` against the source PRDs and the independent
Codex PRD checklist created by `/ms.codex-checklist`.

This command replaces the old `/ms.checklist --global` flow. It owns the global
gate artifact consumed by `/ms.constitution`, `/ms.checklist`, and
`/ms.specify`.

**Three-layer station** (`specter-agent-protocols` §7): Layer 1 runs the
deterministic structural checks, Layer 2 runs Codex and Antigravity as
independent semantic auditors who each write their own verdict, and Layer 3
computes the station Result mechanically. The host — which drove the Feature
Map's authoring — assembles the canonical gate file from those outputs but
never grades anything: no reconciliation findings of its own, no verdict of its
own, no re-grading of an agent's finding (§5 no-unilateral-host-downgrade).

## Usage

```bash
/ms.verify
```

## Required Inputs

These files must exist before the station can run:

- `docs/prd/feature-map.md`
- `docs/prd/feature-map.progress.md`
- `docs/prd/codex/checklist.md` (the independent PRD-only baseline)
- every source PRD recorded in `docs/prd/feature-map.md`

**Session read policy**: per AGENTS.md §2 — reuse files already read this session; a fresh `Read` immediately before `Edit`/`Write` is still required.

If `docs/prd/codex/checklist.md` is missing, stop:

```text
⏳ Codex PRD checklist is not available yet.

Run or wait for:
  /ms.codex-checklist @docs/prd/PRD.md [@docs/prd/another.md]

Then retry:
  /ms.verify
```

## Verification Contract

The station compares the following sources:

1. The original PRD set.
2. The independent Codex PRD checklist.
3. `docs/prd/feature-map.md`.

and produces three artifacts:

```text
docs/prd/feature-map.codex-verify.md            (Codex global verdict, Layer 2)
docs/prd/feature-map.antigravity-checklist.md   (Antigravity global verdict, Layer 2)
docs/prd/feature-map.checklist.md               (canonical global gate, assembled)
```

The canonical gate's `**Result**` is copied verbatim from the Layer-3
aggregation receipt — it is never authored by the host.

## Execution Steps

### Step 0.1: External Agent Preflight (session-level, once)

Apply the Preflight and Degrade Rule from
`.claude/skills/specter-agent-protocols/SKILL.md` (§1–2). For this command: a
**dual-agent station**.

- If **one** agent is unavailable after preflight + one retry: run the station
  single-agent and write the §2 degrade placeholder at the missing agent's
  report path (`docs/prd/feature-map.codex-verify.md` /
  `docs/prd/feature-map.antigravity-checklist.md`) — `**Result**: WARN` +
  `**Availability**: UNAVAILABLE (<reason>)`, plus the `**Mode**:` and
  `**Feature Map SHA256**:` fields so the aggregation can parse it. The
  aggregation then caps the station at `WARN` mechanically.
- If **both** agents are unavailable: **stop and report**. A global gate with
  zero independent verifiers would be a host-only verdict — exactly the
  self-judgment this station exists to remove (§7 typed degrade). Never run
  the audit host-only.

### Step 0.2: Layer 1 — Deterministic Structural Gate

Run the structural checker before spending any agent:

```bash
# self-heal: the runtime copy is project-local (never synced); refresh it from the synced template
install -D -m 0755 docs/templates/scripts/specter-gate.sh .specify/scripts/bash/specter-gate.sh
.specify/scripts/bash/specter-gate.sh structural
```

Read the JSON `verdict` and `reasons[]`:

- `PASS`/`WARN` → continue (a structural WARN is carried into the final
  report, never dropped).
- `FAIL` → **stop before dispatching agents**. Report every `reasons[]` entry
  as a Blocking Fix. Fix `docs/prd/feature-map.md` (in a conducted run,
  `/ms.featuremap`'s fix-round rules apply), then rerun `/ms.verify` from this
  step. Structural defects are mechanical; burning two agent runs on a map
  that fails shape checks wastes both agents.

Layer 1 judges shape only. A structural `PASS` says nothing about whether the
PRD was semantically preserved — that is exactly what Layer 2 exists to audit.

### Step 0.3: Compute the Feature Map hash for report binding

```bash
FEATURE_MAP_SHA=$(sha256sum docs/prd/feature-map.md | awk '{print $1}')
```

Substitute `{FEATURE_MAP_SHA}` into both agent prompts below. The aggregation
fails any report whose recorded hash does not match the current map — a
verdict for a previous map revision is stale, not reusable.

### Step 1: Layer 2 — Dual Independent Global Audits (Foreground, Parallel)

Invoke both agents in the foreground, in parallel, and wait for both to finish.
Each performs the **full** semantic audit independently and writes its own
verdict file. Foreground execution makes write failures observable immediately.

```text
/codex:rescue --fresh --model gpt-5.6-luna --effort xhigh <Codex Prompt>
/antigravity:rescue --fresh --model gemini-3.5-flash --effort medium <Antigravity Prompt>
```

**Report-Write Protocol**: apply `specter-agent-protocols` §3 to each report —
deterministic file check (exists, non-empty, contains `**Result**:`), retry
once, salvage from the `===REPORT BEGIN===`/`===REPORT END===` markers. If no
markers exist either, that is an **agent-authored failure**: leave the report
missing/invalid for the aggregation to grade `FAIL` (§3 step 3) — the Degrade
Rule applies only to Step 0.1 preflight failures, never to an agent that ran.

Prompt template — substitute `{AGENT}` (`Codex` / `Antigravity using Google
Antigravity`), `{MODE}` (`codex-global-verify` / `antigravity-global-verify`),
and `{REPORT_PATH}` (`docs/prd/feature-map.codex-verify.md` /
`docs/prd/feature-map.antigravity-checklist.md`):

```text
You are performing an independent global Feature Map audit for SPECTER as {AGENT}.

Read:
- docs/prd/feature-map.md
- docs/prd/codex/checklist.md (independent PRD-only checklist)
- every source PRD recorded in docs/prd/feature-map.md

Do not edit any files except writing {REPORT_PATH}.
Structural shape (required headings, DAG cycles, ownership row format) is
already machine-checked — focus on semantics:

1. Does the PRD Commitment Index cover every functional and non-functional
   requirement, acceptance criterion, integration/data/migration promise, and
   explicit exclusion in the source PRD set? Name any PRD commitment with no
   index row.
2. Is every commitment owned by the RIGHT Feature (not just exactly one)?
   Flag ownership that contradicts the PRD's own grouping.
3. Does every independent-checklist item (C-IDs) survive into the Feature Map,
   or carry a justified false-positive explanation?
4. Does the Feature Map invent product behavior absent from the PRD set?
5. Are stubs forwarded correctly (each stub names the Feature that activates
   real behavior), and does each Phase's last Feature carry that Phase's E2E
   scenario?

Grade down on doubt; cite PRD/section evidence for every finding and every
PASS claim. Write this output to {REPORT_PATH}:

# Feature Map {AGENT} Verification

**Mode**: {MODE}
**Feature Map SHA256**: {FEATURE_MAP_SHA}
**Result**: PASS | WARN | FAIL
**Generated By**: {AGENT}

## Findings

| Severity | Finding | Evidence | Required Fix |
| --- | --- | --- | --- |

## Verdict

One paragraph summarizing the overall quality and blocking issues.

Also echo the finished report between ===REPORT BEGIN=== and ===REPORT END=== markers in your
final message, verbatim, so it can be salvaged if the file write fails.
```

### Step 2: Layer 3 — Mechanical Aggregation

```bash
.specify/scripts/bash/specter-gate.sh aggregate verify --ledger --round <R>
```

`<R>` is the current §4 convergence round (1 on the first run, 2/3 on
re-rounds).

The station's report set is fixed by the station name — never pass file paths,
and never omit a report that turned out badly (§7). The receipt JSON contains
the per-report grading, the station `verdict`, any `cap`
(`single-agent-degrade`), verbatim `caught` rows, and `reasons[]`. The
`--ledger` flag appends the `.specify/specter-run.jsonl` line mechanically —
do not hand-write a ledger line for this station.

- `verdict: PASS`/`WARN` → continue to Step 3.
- `verdict: FAIL` → the map (or a report) failed. Report the receipt's
  `reasons[]` and both reports' Findings verbatim as Blocking Fixes. Fix the
  map, then rerun from Step 0.2 — the SHA binding makes the old reports stale
  automatically, so both agents run again (`--fresh`, §4: every round fresh,
  prior findings travel as file paths).

### Step 3: Assemble The Canonical Global Gate (host: paths and metadata only)

Write `docs/prd/feature-map.checklist.md`. Every judgment field is a verbatim
copy from the receipt or the agent reports; the host contributes paths,
metadata, and layout only:

```markdown
# Feature Map Global Verification

**Mode**: global
**Codex Checklist**: docs/prd/codex/checklist.md
**Global Codex Verify**: docs/prd/feature-map.codex-verify.md
**Antigravity Checklist**: docs/prd/feature-map.antigravity-checklist.md
**PRDs**: <source label -> path list>
**Feature Map**: docs/prd/feature-map.md
**Feature Map SHA256**: <the FEATURE_MAP_SHA the reports were graded against>
**Git Ref**: <git rev-parse HEAD at audit time — record only after checking `git status --porcelain docs/prd/`: if audited PRDs/Feature Map are uncommitted, this ref does NOT contain what was audited and `/ms.expand`'s delta baseline breaks (audit #30); tell the user to commit first, or write `DIRTY` here if they decline>
**Result**: <receipt verdict, copied verbatim>
**Generated**: YYYY-MM-DD

## Structural Gate (Layer 1)

<the `structural` JSON verdict and reasons[], copied verbatim>

## Agent Verdicts (Layer 2)

| Report | Result | Availability |
| --- | --- | --- |
<one row per receipt input: path, result, availability — copied from the receipt>

## Findings (verbatim from agent reports)

<the Findings table rows of both reports, copied verbatim, prefixed with the
reporting agent's name — no re-grading, no paraphrase, no omission>

## Blocking Fixes

<mechanical criterion — no judgment: the Required Fix cell of every row whose
Severity cell is CRITICAL or HIGH, copied verbatim, in file order; empty only
when no such row exists>

## Non-Blocking Improvements

<the Required Fix cell of every remaining row, copied verbatim, in file order —
partitioning is by the Severity cell alone, never by the host's own reading of
the finding>
```

The `**Codex Checklist**` field always means the PRD-only baseline; the new
`**Global Codex Verify**` field is the Layer-2 verdict report. Never overload
one to mean the other.

### FAIL Conditions (all computed by Layer 1 or Layer 3 — never by the host)

- `docs/prd/codex/checklist.md` is missing (Required Inputs stop).
- `structural` verdict `FAIL` (index/ownership/DAG/heading/placeholder defects
  — the script's `reasons[]` are the authoritative list).
- Any agent report missing, empty, malformed (zero or multiple `Result` lines,
  unknown value), or stale (recorded `Feature Map SHA256` differs from the
  current map).
- Any agent `Result: FAIL`.
- Every agent report is a degrade placeholder (zero independent verifiers).

## Report

If `PASS`:

```text
✅ Global Feature Map verification passed.

📄 Audit: docs/prd/feature-map.checklist.md
📄 Agent verdicts: docs/prd/feature-map.codex-verify.md, docs/prd/feature-map.antigravity-checklist.md
🎯 Next step: /ms.constitution
```

If `WARN`:

```text
⚠️ Global Feature Map verification passed with warnings.

📄 Audit: docs/prd/feature-map.checklist.md
권장 개선사항을 확인한 뒤 /ms.constitution으로 진행할 수 있습니다.
```

If `FAIL`:

```text
⛔ Global Feature Map verification failed.

📄 Audit: docs/prd/feature-map.checklist.md
Blocking Fixes를 반영한 뒤 /ms.featuremap 또는 docs/prd/feature-map.md를 수정하고 /ms.verify를 다시 실행하세요.
/ms.constitution은 아직 진행하지 마세요.
```

## Run-State Ledger

Emitted mechanically by Step 2's `aggregate verify --ledger`
(`specter-agent-protocols` §7 Mechanical ledger) — `caught` rows are verbatim
report findings and `cap` is the receipt's classification. The host never
authors or edits this station's ledger line. If Step 0.2 stopped at the
structural gate (agents never ran), append the structural result instead:

```bash
mkdir -p .specify
printf '{"ts":"%s","cycle":"pre","feature":null,"step":"verify","verdict":"FAIL","artifacts":["docs/prd/feature-map.md"],"caught":%s}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "<the structural reasons[] array, copied verbatim>" >> .specify/specter-run.jsonl
```

## Next Command

After `/ms.verify` passes, run `/ms.constitution`.

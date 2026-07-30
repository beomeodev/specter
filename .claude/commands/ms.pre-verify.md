---
description: "Verify Feature Map against PRDs and the independent baseline checklist (global three-layer gate)"
argument-hint: ""
---

# /ms.pre-verify - Global Feature Map Verification

Verify `docs/prd/feature-map.md` against the source PRDs and the independent
baseline checklist created by `/ms.featuremap-checklist`.

This product-wide gate is always full strength. The risk profile cannot
narrow its PRD scope, reviewer effort, two-reviewer Layer 2, convergence
behavior, or Layer-3 aggregation.

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
/ms.pre-verify
```

## Required Inputs

These files must exist before the station can run:

- `docs/prd/feature-map.md`
- `docs/prd/feature-map.progress.md`
- the independent PRD-only baseline checklist, resolved **new-first with legacy
  fallback** and reused as `{BASELINE}` everywhere below (required-input check,
  agent prompts, canonical metadata):
  ```bash
  BASELINE="docs/prd/featuremap-checklist.md"
  [ -f "$BASELINE" ] || BASELINE="docs/prd/codex/checklist.md"   # legacy Codex-era path
  ```
- every source PRD recorded in `docs/prd/feature-map.md`

**Session read policy**: per AGENTS.md §2 — reuse files already read this session; a fresh `Read` immediately before `Edit`/`Write` is still required.

If neither baseline path exists, stop:

```text
⏳ 독립 baseline checklist가 아직 없습니다.

Run or wait for:
  /ms.featuremap-checklist @docs/prd/PRD.md [@docs/prd/another.md]

Then retry:
  /ms.pre-verify
```

## Verification Contract

The station compares the following sources:

1. The original PRD set.
2. The independent baseline checklist (PRD-only).
3. `docs/prd/feature-map.md`.

and produces three artifacts:

```text
docs/prd/feature-map.codex-verify.r<R>.md         (Codex global verdict, Layer 2)
docs/prd/feature-map.antigravity-verify.r<R>.md   (Antigravity global verdict, Layer 2)
docs/prd/feature-map.checklist.md                 (canonical global gate, assembled)
.specify/verification-v2/pre-verify-global.json   (station receipt, gate-written)
```

Report paths are round-numbered — a new round is a new file, never an
overwrite.

The canonical gate's `**Result**` is copied verbatim from the Layer-3
aggregation receipt — it is never authored by the host.

## Execution Steps

### Step 0.1: External Agent Preflight (session-level, once)

Apply the Preflight and Degrade Rule from
`.claude/skills/specter-agent-protocols/SKILL.md` (§1–2). For this command: a
**dual-agent station**.

- If **one** agent is unavailable after preflight + one retry: run the station
  single-agent and write the §2 degrade placeholder at the missing agent's
  round-numbered report path (`docs/prd/feature-map.codex-verify.r<R>.md` /
  `docs/prd/feature-map.antigravity-verify.r<R>.md`) — a VALID v2 report:
  `**Contract**: verification-v2`, `**Mode**:`, `**Scope**: global`,
  `**Input Digest**:`, `**Result**: WARN`, `**Availability**: UNAVAILABLE
  (<reason>)`. The aggregation then caps the station at `WARN` mechanically.
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
  `/ms.featuremap`'s fix-round rules apply), then rerun `/ms.pre-verify` from this
  step. Structural defects are mechanical; burning two agent runs on a map
  that fails shape checks wastes both agents.

Layer 1 judges shape only. A structural `PASS` says nothing about whether the
PRD was semantically preserved — that is exactly what Layer 2 exists to audit.

Then confirm the refreshed gate carries the verification-v2 contract — a
partially synced project must fail loudly here, never silently run the
station under a different contract:

```bash
install -D -m 0644 docs/templates/verification-v2.json .specify/policies/verification-v2.json
.specify/scripts/bash/specter-gate.sh version | grep -q '"contract": "verification-v2"'
```

If the grep fails, stop and tell the user to run `/ms.sync` (or `/ms.init`)
first.

### Step 0.3: Compute the input digest

```bash
DIGEST=$(.specify/scripts/bash/specter-gate.sh digest pre-verify | python3 -c "import json,sys; print(json.load(sys.stdin)['input_digest'])")
```

Substitute `{DIGEST}` into both agent prompts below. The aggregation fails any
report whose recorded digest does not match the current map + baseline — a
verdict for a previous revision is stale, not reusable.

**On a §4 re-round (R = 2)**, pass both prior-round report paths into both
prompts and append: `Re-round continuity: read the prior round's reports
first — docs/prd/feature-map.codex-verify.r1.md and
docs/prd/feature-map.antigravity-verify.r1.md. They are NOT a PASS whitelist
and do not suppress discovery. Re-check every prior blocking finding by ID and
mark each resolved or persists in your Findings State column. A grade may
improve only against changed, cited evidence. If your own lane previously
prescribed the state you now reject, say so explicitly, cite the prior finding
ID, and recommend escalation.`

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
`{DIGEST}`, `{R}`, and `{REPORT_PATH}`
(`docs/prd/feature-map.codex-verify.r{R}.md` /
`docs/prd/feature-map.antigravity-verify.r{R}.md`):

```text
You are performing an independent global Feature Map audit for SPECTER as {AGENT}.

Read:
- docs/prd/feature-map.md
- {BASELINE} (the resolved independent PRD-only checklist — substitute the actual path)
- every source PRD recorded in docs/prd/feature-map.md

Do not edit any files except writing {REPORT_PATH}.
Structural shape (required headings, DAG cycles, ownership row format) is
already machine-checked — focus on semantics:

1. Does the PRD Commitment Index cover every functional and non-functional
   requirement, acceptance criterion, integration/data/migration promise, and
   explicit exclusion in the source PRD set? Name any PRD commitment with no
   index row.
2. Is every commitment owned by the RIGHT Feature (not just exactly one)?
   Flag ownership that contradicts the PRD's own grouping, and apply the
   journey rule (.claude/skills/specter-agent-protocols/SKILL.md §10): a
   journey-shaped commitment belongs to the Feature where the whole
   observable journey first becomes verifiable — an owner that can only
   prove part of the journey is wrongly assigned, and enabling slices must
   appear as D-ID obligations, never as partial owners.
3. Does every independent-checklist item (C-IDs) survive into the Feature Map,
   or carry a justified false-positive explanation?
4. Untagged invention: does any in-scope deliverable, done criterion, Key
   decision, or other behavior in the map lack a PRD trace (C-ID or
   Amendment)? Key decisions are a known smuggling surface — a decision may
   record the chosen realization of a cited C-/D-ID, but a "decision"
   introducing scope with neither behind it is untagged. Untagged additions
   are FAIL findings.
   (An idea parked in docs/prd/opportunities.md is out of audit scope — do
   not read that file.)
5. `## Implementation Obligations` rows (if present) are references, never
   product authority (.claude/skills/specter-agent-protocols/SKILL.md §10):
   FAIL any row used to justify NEW observable scope — a new capability, data
   category/retention, permission, third-party integration, notification
   channel, irreversible/destructive effect, billing, public API, or
   quantitative promise beyond the cited C-IDs' envelope (that needs a PRD
   Amendment) — and any row whose Supports cites a non-existent C-ID or
   another D-ID, or that is used anywhere to own or satisfy a baseline C-ID.
6. Are stubs forwarded correctly (each stub names the Feature that activates
   real behavior), and does each Phase's last Feature carry that Phase's E2E
   scenario?
7. Do the `### Verification signals` tables honestly reflect the PRD
   evidence? A declared "no" the PRD contradicts is a blocking finding.

When a rule is violated (e.g. the journey rule), list every violator of that
rule you can find, never just the first instance.

Grade down on doubt; cite PRD/section evidence for every finding and every
PASS claim. Write this output to {REPORT_PATH}:

# Feature Map {AGENT} Verification — Round {R}

**Contract**: verification-v2
**Mode**: {MODE}
**Scope**: global
**Input Digest**: {DIGEST}
**Result**: PASS | WARN | FAIL

## Scope and evidence
**Checked**: <named check classes 1-7 above, with file:line citations>
**Not checked**: <explicit exclusions with reasons, or the evidence basis for claiming none>

## Findings

| ID | Severity | State | Finding | Evidence | Required Fix |
| --- | --- | --- | --- | --- | --- |

(IDs stable within your lane, e.g. CX-P-001 / AG-P-001. State: new | persists |
resolved. Required Fix = restored invariant + minimum repair + no new scope;
escalate instead of choosing when several product interpretations remain valid.)

## Verdict

One paragraph summarizing the overall quality and blocking issues.

Also echo the finished report between ===REPORT BEGIN=== and ===REPORT END=== markers in your
final message, verbatim, so it can be salvaged if the file write fails.
```

### Step 2: Layer 3 — Mechanical Aggregation

First apply the Validate / Salvage / Format-Retry lane (protocols §3) to each
report: `specter-gate.sh validate-report <path> pre-verify --round <R>`;
invalid → salvage from markers → still invalid → one same-agent re-dispatch
with the validator's errors (track for `--format-retries`). Then:

```bash
.specify/scripts/bash/specter-gate.sh aggregate pre-verify --ledger --round <R> \
  [--format-retries "<codex-retries> <antigravity-retries>"]
```

`<R>` is the current §4 round (1 on the first run, 2 on the repair round).
The gate itself refuses rounds beyond the automatic budget (2) without a
recorded `authorize-round` decision. At the round cap, present the §4
post-cap options verbatim — **fix and restart / amend the authority (PRD) /
authorize one doctrine-dispute round / accept WARN / stop** — never "run one
more round?".

The station's report set is fixed by the station name — never pass file paths,
and never omit a report that turned out badly (§7). The receipt JSON contains
the per-report grading, the station `verdict`, any `cap`
(`single-agent-degrade`), verbatim `caught` rows, and `reasons[]`. The
`--ledger` flag appends the `.specify/specter-run.jsonl` line mechanically —
do not hand-write a ledger line for this station.

- `verdict: PASS`/`WARN` → continue to Step 3.
- `verdict: FAIL` → the map (or a report) failed. Report the receipt's
  `reasons[]` and both reports' Findings verbatim as Blocking Fixes, fix the
  map (in a conducted run, `/ms.featuremap`'s fix-round rules apply — targeted
  edits, not full rewrites), then apply the **certification contract** below.

**Certification contract (this station tightens §4 — repairs here can ripple
map-wide).** Because an ownership move, Feature split, or DAG edit can
introduce regressions far outside the rows a fix touched, a scoped re-round
can never certify the whole map:

- **Repair rounds** (§4 rounds 2+) are scoped to the failing findings plus the
  fix diffs and are **advisory**: they exist to confirm the specific fixes
  landed cheaply, and their reports never become the station's accepted
  verdict.
- **The accepted PASS/WARN always comes from a fresh full-scope dual audit**
  (both agents, full prompt above, current input digest) run after the repair
  round converges. One final full round replaces the old
  full-audit-every-round loop — diagnosis gets a cheap scoped round, the
  certificate stays full-strength.
- The §4 budget counts repair rounds as usual (2 automatic rounds); the final
  full audit is the certification run, authorized as the follow-on round via
  `specter-gate.sh decide authorize-round pre-verify global --round <R>
  --reason "certification run after repairs"` when it falls beyond the
  automatic budget.

**Delta certification (2026-07-28) — scope the re-audit to the change.** The
rules above answer "how do we certify a map we are actively repairing". They
were also being applied to a *settled* map that someone later edited, and there
the full sweep is miscalibrated: the certificate binds to the map's digest, so
any byte forces a full re-audit of everything, no matter how small the edit.

Measured on 2026-07-28: three targeted edits (two Commitment-Index rows
extended, one signal value corrected) triggered four full certification rounds.
Findings attributable to those edits: **zero** — the sweep was re-sampling the
whole map, not verifying the change.

So when the map was already certified `PASS`/`WARN` and the pending diff is
**low-risk**, the re-audit is scoped to the change:

- **Low-risk (delta-certifiable)** — edits that cannot move a commitment's
  owner or the map's ID set: wording clarified inside an existing row,
  evidence or citation corrected, a `### Verification signals` value raised
  or its evidence updated, a done criterion reworded without changing what it
  observes, typo/formatting.
- **High-risk (always full-scope)** — ownership moved between Features, a
  Feature split/merged, any DAG edge changed, a C-ID or D-ID added or
  removed, a commitment deleted, a Verification signal flipped `yes` → `no`,
  or the map's **first** certification. These ripple beyond the edited lines.
  When in doubt, treat the edit as high-risk.
- The delta round audits the diff hunks **plus their citation radius** — every
  row that cites, is cited by, or owns something the diff touched — and its
  `**Checked**:` line names that radius instead of the whole map.
- The canonical gate records `**Certification Scope**: full | delta-from-<prior digest>`
  so a later reader can tell which guarantee they hold, and a delta
  certificate names the prior full certificate it extends.
- A delta round may **not** clear findings outside its scope, and it may not
  chain indefinitely: after **three consecutive** delta certifications, or on
  the first high-risk edit, the next accepted verdict comes from a full-scope
  audit again.
- The ID set is the mechanical tell: if the map's sorted C-ID/D-ID/Feature-
  section set changed (`grep -oE 'C-[0-9]+|D-[0-9]+|^## Feature [0-9]+' | sort -u`
  before vs after), the edit was **not** low-risk — fall back to full scope.
  (Extending an existing row keeps the set; adding a C-ID does not.)

### Step 3: Assemble The Canonical Global Gate (host: paths and metadata only)

Write `docs/prd/feature-map.checklist.md`. Every judgment field is a verbatim
copy from the receipt or the agent reports; the host contributes paths,
metadata, and layout only:

```markdown
# Feature Map Global Verification

**Mode**: global
**Baseline Checklist**: <the resolved {BASELINE} path>
**Global Codex Verify**: docs/prd/feature-map.codex-verify.r<R>.md
**Global Antigravity Verify**: docs/prd/feature-map.antigravity-verify.r<R>.md
**PRDs**: <source label -> path list>
**Feature Map**: docs/prd/feature-map.md
**Feature Map SHA256**: <sha256 of docs/prd/feature-map.md at audit time>
**Input Digest**: <the receipt's input_digest — what the reports were graded against>
**Git Ref**: <git rev-parse HEAD at audit time — record only after checking `git status --porcelain docs/prd/`: if audited PRDs/Feature Map are uncommitted, this ref does NOT contain what was audited and `/ms.expand`'s delta baseline breaks (audit #30); tell the user to commit first, or write `DIRTY` here if they decline>
**Result**: <receipt verdict, copied verbatim>
**Certification Scope**: <`full`, or `delta-from-<prior Feature Map SHA256>` when the
accepted verdict came from a delta round — see the delta-certification rules in Step 2.
A delta certificate also names the full certificate it extends.>
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

The `**Baseline Checklist**` field always means the PRD-only baseline; the new
`**Global Codex Verify**` field is the Layer-2 verdict report. Never overload
one to mean the other.

### FAIL Conditions (all computed by Layer 1 or Layer 3 — never by the host)

- No baseline checklist exists at either the new or the legacy path (Required
  Inputs stop).
- `structural` verdict `FAIL` (index/ownership/DAG/heading/placeholder defects
  — the script's `reasons[]` are the authoritative list).
- Any agent report missing, empty, malformed (zero or multiple `Result` lines,
  unknown value, wrong Contract/Mode/Scope), or stale (recorded `Input Digest`
  differs from the current map + baseline).
- Any agent `Result: FAIL`.
- Every agent report is a degrade placeholder (zero independent verifiers).

## Report

If `PASS`:

```text
✅ Global Feature Map verification passed.

📄 Audit: docs/prd/feature-map.checklist.md
📄 Agent verdicts: docs/prd/feature-map.codex-verify.r<R>.md, docs/prd/feature-map.antigravity-verify.r<R>.md
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
Blocking Fixes를 반영한 뒤 /ms.featuremap 또는 docs/prd/feature-map.md를 수정하고 /ms.pre-verify를 다시 실행하세요.
/ms.constitution은 아직 진행하지 마세요.
```

## Run-State Ledger

Emitted mechanically by Step 2's `aggregate pre-verify --ledger`
(`specter-agent-protocols` §7 Mechanical ledger) — `caught` rows are verbatim
report findings and `cap` is the receipt's classification. The host never
authors or edits this station's ledger line. If Step 0.2 stopped at the
structural gate (agents never ran), append the structural result instead:

```bash
mkdir -p .specify
printf '{"ts":"%s","cycle":"pre","feature":null,"step":"pre-verify","verdict":"FAIL","artifacts":["docs/prd/feature-map.md"],"caught":%s}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "<the structural reasons[] array, copied verbatim>" >> .specify/specter-run.jsonl
```

## Next Command

After `/ms.pre-verify` passes, run `/ms.constitution`.

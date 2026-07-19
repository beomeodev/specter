---
name: specter-agent-protocols
description: Canonical external-agent protocols shared by the dual-agent SPECTER commands (/ms.verify, /ms.pre-verify, /ms.analyze, /ms.review, /ms.expand) — session-level preflight, single-agent degrade rule, report-write/salvage protocol, re-round convergence caps, the auditor bias-prevention doctrine (context isolation, evidence-cited verdicts, UNVERIFIED marking, grade-down-on-doubt, defect-claim symmetry), the verification-report structure (Claim/Evidence/Baseline/Gaps/Residual-risk), and the three-layer station contract (deterministic structural checks → independent dual-agent semantics → mechanical verdict aggregation via specter-gate.sh, with the typed degrade contract and mechanical ledger emission). Commands reference this file instead of restating the mechanics; each command keeps only its own report paths and station-specific invariants inline.
---

# SPECTER External-Agent Protocols

Single source of truth for the mechanics every Codex/Antigravity station shares.
A command that invokes an external agent applies these protocols and states
inline only what is specific to it (its report paths, single- vs dual-agent
station, and any degrade direction that differs).

## 1. Preflight (session-level, once)

Check external-agent availability **once per session** and remember the result —
do not re-check on every command invocation within the same session:

- **Codex**: the `codex` binary is on PATH, auth is configured, and its sandbox
  mode in `~/.codex/config.toml` is not read-only (e.g. `workspace-write` or
  `danger-full-access`). A cheap config check, not a live probe run.
- **Antigravity**: the `agy` binary is on PATH, auth is configured, and its
  write flag is set (see `docs/ops/antigravity-write-flag.md` for the re-apply
  procedure — a plugin update can transiently reset it).

On failure, retry once. If it still fails, apply the Degrade Rule (§2) instead
of blocking the command.

## 2. Degrade Rule (one agent down)

- If one agent of a dual-agent station is unavailable after retry: run the
  station with the remaining agent only, force the station result to at most
  `WARN`, and write a **degrade placeholder report** at the missing agent's
  report path — a minimal but VALID report, not free text, so deterministic
  gates (`specter-gate.sh`) can still parse it:

  ```markdown
  # <Agent> <Station> (degraded)

  **Mode**: <the station's normal Mode value>
  **Feature**: Feature NNN
  **Checklist SHA256**: <current checklist sha — when the station's gate checks it>
  **Result**: WARN
  **Availability**: UNAVAILABLE (<reason>)
  ```

  A bare `<Agent>: UNAVAILABLE (<reason>)` line is NOT a valid placeholder —
  it carries no `**Result**:` field, so the gate reads it as FAIL and an
  environment issue alone blocks the cycle (2026-07-18 audit finding #2).
- **Never** present a single-agent run as if both agents ran.
- **Never** block a cycle on an external-agent environment issue alone —
  degrade, record it, continue.
- A single-agent station (e.g. `/ms.expand`'s delta verify, where Antigravity
  is the only Layer-2 verifier) has nothing to degrade to: stop and report the
  failure instead.

## 3. Report-Write / Salvage Protocol

Agents write their own report files (primary path). Every agent prompt also
requires echoing the finished report verbatim between `===REPORT BEGIN===` /
`===REPORT END===` markers in the agent's final message — near-zero marginal
cost, since a final message is emitted regardless.

After the run, check the written file **deterministically**: it exists, is
non-empty, and contains the expected marker line (usually `**Result**:`; for
the PRD checklist, `**Mode**: prd-only`). If the file is missing or partial:

1. Retry that agent once.
2. Still bad → **salvage**: write the file from the retry's
   `===REPORT BEGIN===`/`===REPORT END===` markers. Do not hand-transcribe.
3. No markers either → this is an **agent-authored failure**, not an
   environmental one (§7 typed degrade): the agent ran and produced nothing
   valid. Do NOT write a §2 placeholder for it — leave the missing/invalid
   report as-is and let Layer-3 aggregation grade that input `FAIL`. Only a §1
   preflight failure (the agent never ran) creates the environmental WARN cap.

## 4. Convergence Policy (re-round caps)

Unbounded re-review loops burn tokens without improving outcomes:

- **Round 1**: full run over the whole scope.
- **Round 2** (only if Round 1 produced a `FAIL` finding): scoped to the failing
  findings plus the fix diffs — not a re-review of everything.
- **Round 3**: last automatic round; re-checks only findings still `FAIL`.
- **Stop**: after Round 3, or as soon as only `WARN`-level findings remain.
  Record every residual `WARN` in the command's artifacts; hand the
  proceed-or-fix decision to the user. Further rounds require an explicit user
  instruction. After the cap, an unresolved `FAIL` stays `FAIL` — it is never
  aged into a `WARN` by exhaustion.
- **Every round is fresh**: dispatch each round with `--fresh`. Prior-round
  findings travel as report **file paths**, never via thread resume — a resumed
  reviewer carries the conversational pressure of the rounds in between ("we
  fixed it") into its verdict, which recreates the author-memory contamination
  this architecture removes. `--resume` is reserved for non-gate work
  continuation (debugging threads, approved implementation-delegation
  follow-ups); any invocation whose output becomes a gate verdict is fresh.
- **Changed evidence only**: a re-round may change a finding's grade only when
  the evidence changed — the fix diff or corrected artifact exists and is cited
  in the revised report. Reconsidering identical evidence never upgrades a
  grade (`FAIL`→`WARN`/`PASS`); it can still downgrade one (§5).

## 5. Auditor Bias-Prevention Doctrine

The value of a verification station is exactly the independence of its verdict.
These rules bind both sides: how the **driver composes** a reviewer prompt, and
how the **reviewer grades**. (Adapted 2026-07-07 from MoAI-ADK's plan-auditor
bias-prevention protocol.)

- **Context isolation (driver-side)**: the reviewer receives only the artifacts
  the station defines (PRD, Feature Map, spec/plan/tasks, diff — as file paths,
  per AGENTS.md §2 dispatch discipline). Never include the authoring reasoning,
  prior drafts, the conversation history, or the driver's own conclusions or
  expectations ("I believe this passes", "should be fine"). If such context
  leaks in anyway, the reviewer must state it is ignoring it and grade from the
  artifacts alone.
- **Evidence-cited verdicts (reviewer-side)**: a `PASS` on any checked item
  requires concrete evidence — a `file:line` citation or exact quoted text.
  "Looks fine" is not a verdict. A report whose PASS items carry no citations
  fails the deterministic report check (§3) in spirit: treat it as partial and
  retry once with the citation requirement restated.
- **UNVERIFIED, not PASS**: an item the reviewer could not actually check
  (missing tooling, unreadable file, out-of-scope dependency) is marked
  `UNVERIFIED` with the reason — never silently folded into PASS. Any
  `UNVERIFIED` item caps the station result at `WARN`, the same convention as
  agent unavailability (§2).
- **Grade down on doubt, per item, no offsetting**: the reviewer's default
  assumption is that defects exist; ambiguous evidence grades down (PASS→WARN,
  WARN→FAIL), never up. Each dimension is graded independently — a strong PASS
  in one area never offsets or softens a FAIL in another, and an issue the
  reviewer identified must appear in the report; talking itself out of a
  finding it already articulated is malpractice.
- **Absence of evidence is not evidence**: what was not observed is neither a
  success nor a failure — it belongs in the report's Gaps section (§6), never
  in the verdict, in either direction.
- **Defect-claim symmetry**: the UNVERIFIED convention applies to defect claims
  too. A suspected defect, debt, or drift is a hypothesis — marked `UNVERIFIED`
  until the domain tool confirms it — never asserted as fact from pattern
  matching alone. (Real case: a grep-based estimate of "29 items need cleanup"
  audited to 0 by the actual tool.)
- **No unilateral host downgrade (driver-side)**: the host/driver never
  re-grades an external verdict or finding — not by explaining it away as a
  false positive, not by relabeling a content finding as environmental. A
  disputed finding goes back to the same station as a scoped §4 re-round
  (fresh), where only the reviewing agent may revise its own grade against
  changed evidence. The station verdict is whatever §7's aggregation computes
  from the report files as written.

## 6. Verification-Report Structure

Every verification-style report the **host composes** — verify/audit summaries,
station reconciliation sections — carries five sections. Dual-agent station
report files stay in their compact machine-parsed form (`**Result**:` +
Findings + Verdict — what the deterministic gates read); their gaps and
residual-risk content lives in the host's station summary, not in the agent
files (2026-07-18 audit #22 reconciliation). This structure exists because final verdicts
systematically under-report what a station actually observed (2026-07-10 gate
audit): what was *not* observed must survive in the report, not evaporate into
a one-word verdict.

- **Claim** — the specific statement being verified, not just the station name.
- **Evidence** — the commands run and their output, verbatim (trim to the
  relevant lines; never paraphrase a result). This is §5's evidence-cited
  verdict rule applied to the whole report.
- **Baseline** — what the result is compared against, measured in *this* run —
  not remembered from a previous run, not assumed.
- **Gaps** — what was not observed: paths not exercised, tools unavailable,
  scopes excluded, inputs not tried. The defensive core of the report. An
  empty Gaps section must state the basis for claiming exhaustive observation;
  a bare "none" is the empty-section cliché this structure exists to prevent.
- **Residual-risk** — what can still go wrong even though everything above was
  observed (timing, environment differences, untested scale).

## 7. Three-Layer Station Contract

Every SPECTER verification station is composed of three layers (adopted
2026-07-19; externally reviewed by Codex the same day). The division exists to
close the author-judge vector: the host — which authored or assembled the
artifacts under test, and carries session memory of authoring them — never
grades them.

- **Layer 1 — deterministic structure** (`specter-gate.sh structural`):
  parseable facts only — required fields/sections, single commitment ownership,
  DAG acyclicity, placeholder scans, `CI passes green` suffixes, cited-ID
  cross-references. Runs **before** agent dispatch: a structural FAIL stops the
  station without spending agents. L1 never claims semantic fidelity (whether
  the PRD was actually understood and preserved) — that is L2's job; treating a
  structural PASS as semantic coverage is a known false-confidence trap.
- **Layer 2 — independent semantics** (external dual agents, always `--fresh`,
  §4): Codex and Antigravity each audit the same artifacts independently and
  each write their own report with a single `**Result**:`. Each report binds to
  the exact revision it audited via the station's SHA field.
- **Layer 3 — mechanical aggregation** (`specter-gate.sh aggregate <station>`):
  computes the station verdict from the **fixed** report set the station
  defines. The host invokes the station by name; it never selects, adds, or
  omits report files (dynamic input choice would let a failing report simply be
  left out). Verdict = worst valid input (FAIL > WARN > PASS), folding in the
  L1 result where the station defines it.

### Report validity (L2)

A station report is valid iff it: is non-empty; contains exactly one
`**Result**:` line valued `PASS`|`WARN`|`FAIL`; carries the station's exact
`**Mode**:` (aggregation rejects a report whose Mode belongs to another
station); names the audited scope (`**Feature**:` on per-Feature stations);
and carries the freshness binding the station defines (`**Checklist SHA256**:`
/ `**Feature Map SHA256**:` / `**Tasks SHA256**:` for `/ms.analyze`) matching
the current artifact. **Stated exception**: `/ms.review` reports bind to
Feature identity only — a working-tree diff has no stable hash to bind to;
the exposure is mitigated by the executable gates running on the same tree in
the same command. An optional
`**Availability**:` line (`UNAVAILABLE (<reason>)` | `RECUSED (<reason>)`)
marks a §2 degrade placeholder. Anything else — missing file, empty file, zero
or multiple Result lines, unknown value, stale SHA — is graded `FAIL` by L3
and never repaired, reinterpreted, or hand-patched by the host (salvage from
§3 markers is the only sanctioned repair, and it copies the agent's own text).

### Receipt (L3 output)

`aggregate` emits one JSON receipt: station, scope, `round`, per-input `{path,
sha256, result, availability}` (a missing/empty input records `""` at its
position so the hash array always aligns with the input array), `verdict`,
`cap` (present only when the verdict was capped mechanically —
`single-agent-degrade` for an availability placeholder, or
`missing-baseline` at the expand station when the independent delta baseline
checklist is absent), and `reasons[]`.
The receipt — not host prose — is the station's outcome of record. Canonical
artifacts the host assembles afterward (e.g. the global Feature Map checklist)
copy the receipt's verdict verbatim; the host contributes paths and metadata,
never findings, verdicts, `caught` selections, or cap classifications.

### Typed degrade

Only a §1 preflight failure (after one retry) creates an environmental
degrade: the driver writes the §2 placeholder (`**Result**: WARN` +
`**Availability**:` line) and L3 records the cap. An agent-authored failure —
malformed report, mid-run crash, refusal — is a `FAIL` input, never relabeled
as environmental by the host. `RECUSED` (implementer recusal, AGENTS.md §2) is
handled identically to `UNAVAILABLE`: single-agent run, WARN cap. Both agents
down at a dual station leaves zero independent verifiers: the station **stops
and reports** — it never runs host-only, because a host-only verdict is
exactly the self-judgment this contract removes.

### Mechanical ledger

For aggregated stations, the `.specify/specter-run.jsonl` line is emitted by
`aggregate --ledger`, which copies finding-table rows verbatim from the report
files into `caught` and the receipt's cap into `cap`. This appended line **is
the persisted receipt**: it also records `round` (pass `--round N` on
re-rounds) and `report_shas` (each report file's content hash), append-only,
so a later fix round can never rewrite what a station originally observed.
The host never authors these fields at an aggregated station — the 2026-07-10
ledger under-reporting incident is why this is mechanical, not stylistic.

**Composite stations.** A station whose final result folds in more than the
agent reports (`/ms.review`'s executable gates and Done Criteria; a host
WARN-level detection at `/ms.analyze`) appends its own line **after** the
mechanical one. That composite line must embed the receipt's verdict verbatim
as `agents_verdict` and may only equal or worsen it — a composite line that
softens the mechanical verdict is a §5 violation. The mechanical line always
remains in the ledger (append-only), so the original station observation
survives regardless.

### Authoring stations are not verdicts

`/ms.featuremap` and `/ms.checklist`'s audit-and-write steps are **isolated
authoring stations**: a fresh subagent writes the artifact so the session's
authoring memory cannot leak into it. Their self-reported Result is a draft
grade, never authoritative — the authoritative verdict comes from the
L1+L2+L3 station that follows (`/ms.pre-verify`, `/ms.verify`). A single
subagent's PASS must never be presented as, or substituted for, dual
verification. Fix rounds after a FAIL re-dispatch a fresh subagent scoped to
the reported defects only (max 2 fix rounds before escalating to the user),
and a fix subagent must never delete or reword commitments merely to make a
structural check pass.

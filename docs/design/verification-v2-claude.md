# verification-v2 — Design (Claude)

**Status**: proposal · **Date**: 2026-07-30 · **Brief**: `.agent-io/verification-v2-design-brief.md`
**Inputs**: `docs/audits/2026-07-30-verification-slowdown-analysis.md`,
`.agent-io/slowdown-analysis-codex-review.md`, `.agent-io/spec-corpus-scan.md`

---

## 1. Design summary

verification-v2 keeps the three-layer skeleton exactly as it is — deterministic L1 before any
agent, two fresh independent L2 reviewers, mechanical worst-of L3 over station-fixed inputs —
and rebuilds everything around it on one principle:

> **Risk is declared or observed in files; it is never inferred from prose.
> State has one writer and one reader. Every budget is enforced by the gate, not by prose.**

What exists in v2:

- **Two risk modes** (`standard`, `high-risk`) instead of three execution tiers. Mode is
  computed *inside the gate* at exactly **two** points (checklist-time from declared Feature-Map
  signals; review-time from deterministic diff path facts). No keyword scanning of
  spec/plan/tasks. No monotonic floor. No separate classifier process, receipt, or policy
  handshake.
- **One report schema** for all L2 stations: header bindings, a 5-column findings table with
  stable IDs, a free-form **Not examined** section, a verdict paragraph. No coverage
  manifests, no set-equality checks, no lineage columns.
- **Round-numbered report files** (`*.r1.md`, `*.r2.md`) instead of canonical-path overwrite +
  archive copies + continuity packets. History is the filenames plus the append-only ledger.
- **An executable round budget**: `aggregate` refuses `--round 3+` without a recorded human
  ack artifact. Universal cap of 2 automatic rounds, all stations.
- **A format-retry lane**: a malformed report costs one same-round re-dispatch of that one
  agent, never a full station round.
- **Exactly four human stops**, named and closed: clarify (by design), high-risk residual WARN
  at review, migration rollback ack, round-cap escalation.
- **One config file** (`verification-v2.json`: signal list, high-risk path patterns, budgets,
  targeted checks) and **two state stores** (per-station receipt JSON, append-only ledger).

What from v1 is deleted: T1/T2/T3 and `classify_audit_tier.py`'s scan/receipt/floor machinery,
`audit-tier-policy.json`'s `artifact_scan_rules`, the five reclassification boundaries,
coverage manifests and `## Coverage` validation, continuity packets, round archives, the
8-column lineage table, `REVERSAL`/`COVERAGE_BREACH` mechanics, warn-ack outside high-risk
review, `.specify/audit-tiers/` and `.specify/continuity/`.

What is kept unchanged: station names and cycle order; L1 structural checks; dual fresh L2
with typed degrade; mechanical L3 and the ledger with verbatim `caught`; freshness SHA
bindings; PRD-only authority (§10 lattice); the publish/release machinery; Done Criteria
Execution; migration analysis (6.6b); the report-write/salvage marker protocol.

---

## 2. The contract

The following is the normative v2 contract text. Target home:
`specter-agent-protocols` SKILL.md replaces §4, §6, §7, §8 with this; commands keep only
their report paths and prompts.

### 2.1 Stations and layers

Grading stations: `pre-verify` (global), `verify`, `analyze`, `review` (per-Feature),
`expand-delta` (single-agent, unchanged rules). Authoring stations (`featuremap`,
`checklist`) remain draft-only as in v1.

Every grading station runs three layers in order:

- **L1 — structural** (`specter-gate.sh structural …`): unchanged checks (required sections,
  ownership, DAG, placeholders, `CI passes green` suffixes, cited-ID cross-references). FAIL
  stops the station; no agent is dispatched.
- **L2 — semantics**: Codex and Antigravity, always fresh, fixed effort per station
  (default `codex: xhigh`, `antigravity: medium`; one value pair for all Features — effort is
  no longer risk-dependent). Prompts state scope; **high-risk mode appends the targeted-check
  list and widens scope to affected trust boundaries — nothing else changes**.
- **L3 — aggregation** (`specter-gate.sh aggregate <station> …`): fixed input paths, worst
  valid input wins, receipt + ledger emission. The host never selects inputs or grades.

### 2.2 Risk mode

`aggregate` (and `structural`, for prompt assembly) computes `risk_mode` deterministically:

1. **Declared signals** (checklist-time, drives `verify`/`analyze`): the Feature Map's
   `### Audit signals` table keeps its closed boolean schema. `risk_mode = high-risk` iff any
   hard-risk signal = `yes`. `unknown` on a hard-risk signal is a **L1 FAIL with a named
   remedy** ("resolve the signal to yes/no with evidence"), not a silent escalation.
   Signals remain evidence-bound; a reviewer finding that a declared `no` contradicts the
   artifacts remains a blocking finding (that is what keeps declarations honest — the
   reviewer, not a regex).
2. **Observed path facts** (review-time, drives `review`): `risk_mode = high-risk` iff the
   diff (tracked + untracked, gate-machinery paths excluded) touches any configured path
   class: migration dirs (`db/migrations/`, `alembic/versions/`, `prisma/migrations/`),
   dependency manifests/lockfiles, CI/workflow files, or gate machinery
   (`.claude/`, `docs/templates/scripts/`, `scripts/specter/`). **File-level facts only —
   no content regexes.** DDL statements are covered by the migration-dir rule plus the
   declared `schema_or_data_migration` signal; accepting that a raw-SQL migration outside a
   migrations dir needs its signal declared is an explicit residual risk (see §3, row 2).
3. **Manual raise**: `--raise-risk` on any station, upward only, recorded in receipt and
   ledger with actor. There is no lowering flag (N5).

There is no cross-phase floor. Checklist-time mode governs verify/analyze; review-time mode
governs review. A wrong early declaration is corrected by editing the Feature Map (which
re-binds SHAs and reruns L1), not carried forever.

What high-risk changes — exhaustively:
- review scope extends to affected trust boundaries and seams;
- the targeted checks (security/trust boundaries, data integrity, state ownership, rollback,
  failure modes, public-contract compatibility, real entrypoint/E2E) become mandatory rows in
  Done Criteria Execution;
- migration analysis + human ack (6.6b) is mandatory when a migration is in the diff;
- a **residual WARN at `review`** requires human ack before advancement.

Everything else — reviewer count, effort, freshness, round budget, report schema — is
identical in both modes.

### 2.3 Report schema (all L2 stations)

```markdown
# <Station> — <Agent> — Feature NNN — Round R

**Mode**: <station's fixed mode string>
**Feature**: Feature NNN
**Bound-To**: <artifact path>@sha256:<hash>   (one line per bound artifact)
**Result**: PASS | WARN | FAIL
**Availability**: UNAVAILABLE|RECUSED (<reason>)   (degrade placeholder only)

## Findings
| ID | Severity | Finding | Evidence | Required Fix |
(ID stable within the lane, e.g. CX-V-003; Evidence = file:line or exact quote;
 Required Fix = invariant to restore + minimum compliant outcome. Two elements, not six.)

## Not examined
(free-form list: paths/scopes/tools the reviewer did not or could not check, with reason.
 Any entry the reviewer marks UNVERIFIED-critical caps this report at WARN.)

## Verdict
(one paragraph)
```

Validity (L3): non-empty; exactly one `**Result**:`; correct `**Mode**:`; `**Feature**:` on
per-Feature stations; every `Bound-To` hash matches the current artifact. Findings-table
parse errors or missing sections are **format defects**, not verdicts — see §2.5.

Re-rounds (R ≥ 2): the prompt lists the prior round's two report file paths; the reviewer
re-checks prior FAIL findings by ID and reports each as `resolved` or `persists` in the
Finding text, plus any new findings. No packet builder, no lineage columns, no class enum.
One retained doctrine sentence: *a lane that now rejects the state its own prior Required Fix
prescribed must say so explicitly and recommend escalation rather than a new fix* — enforced
by the other lane and the round cap, not by machinery.

### 2.4 Round budget (executable)

- Round 1: full scope. Round 2: scoped to failing findings + fix diffs. **That is the entire
  automatic budget, every station, both modes.**
- `aggregate --round N` with N ≥ 3 **exits FAIL** unless
  `.specify/acks/<station>-<scope>-r<N>.ack` exists; the ack is created by a documented user
  command (`specter-gate.sh ack-round …`), records actor + reason, and is copied into receipt
  and ledger. The four post-cap options (resolve doctrine / amend authority / accept WARN /
  stop) are presented verbatim; "one more round" is not one of them.
- After the cap an unresolved FAIL stays FAIL. Oscillation, reversal, and "same finding
  survives a targeted fix" all hit the cap at round 2 and become the human's decision — this
  is the v2 replacement for REVERSAL/termination-signal machinery: the budget is small enough
  that pathology reaches a person in one step.

### 2.5 Format-retry lane (P6)

After each agent finishes, the driver runs `specter-gate.sh validate-report <path>`
(deterministic). On failure: salvage from `===REPORT BEGIN/END===` markers; if still invalid,
re-dispatch **that one agent** once, same round, prompt prefixed with the validator's error
list. Only after that does the input grade FAIL at L3. Receipts record `format_retries` per
input. A format problem therefore never consumes a station round or the other agent's work.

### 2.6 Degrade (unchanged from v1 §2/§7, restated)

Environmental unavailability after one retry → single-agent run + typed placeholder + WARN
cap (`cap: single-agent-degrade`). Agent-authored failure → FAIL input (after §2.5's one
format retry). Both reviewers down → station stops. `RECUSED` ≡ `UNAVAILABLE`. High-risk
review adds: single-agent degrade requires human ack.

### 2.7 State stores and their single writers

| Store | Writer | Reader | Lifetime |
| --- | --- | --- | --- |
| report files `*.rN.md` | the agent (or salvage) | L3, next-round prompts | permanent, immutable by convention (round-numbered, never overwritten) |
| `.specify/receipts/<station>-<scope>.json` | `aggregate` | driving command, next station's precondition check | current run only, overwritten per round |
| `.specify/specter-run.jsonl` | `aggregate --ledger` | audits, rule-pruning | append-only, permanent |
| `.specify/acks/*.ack` | `ack-round` / ack commands (human-invoked) | `aggregate` | per-decision |
| `verification-v2.json` (synced) | this repo, via replay-validated change | gate | versioned with the contract |

Deleted: `.specify/audit-tiers/`, `.specify/continuity/`, round archives, per-phase
classification receipts. `review-hash.cache` / `review-state.txt` (publish contract) are out
of scope and unchanged.

### 2.8 Contract versioning

`specter-gate.sh version` reports `"contract": "verification-v2"`. Every station command
checks it once (fail loudly on partial sync, as today). Any change to the gate, the config,
or this contract text is itself a gate-machinery diff → high-risk review + the §6 replay.

---

## 3. Deleted v1 mechanisms — what did their job, and what does it now

| v1 mechanism | Job it did | v2 disposition | What covers the motivating incident now |
| --- | --- | --- | --- |
| T1/T2/T3 execution tiers | scale cost to risk | **delete** | two modes; cost scaling came out inverted (97% T3), so the "save money on T1" job is done by v2's cheaper *standard* mode being the default for everyone |
| `artifact_scan_rules` prose regexes | catch undeclared risk in artifacts | **delete** | declared signals audited by reviewers (blocking finding if contradicted) + file-level path facts at review. Residual risk, accepted explicitly: risky *prose* with a false `no` declaration and no path fact is caught only by a reviewer, not a regex — the corpus shows the regex mostly caught boilerplate, not risk |
| monotonic tier floor + 5 reclassification boundaries | prevent risk laundering by re-classification | **delete** | two computation points, each from current ground truth; review-time path facts cannot be laundered by editing prose. Early-phase declarations are L1-checked at every station via SHA re-binding |
| tier receipts + `gate-status` handshake | bind stations to a validated tier | **delete** | `aggregate` computes mode internally; nothing to go stale (kills the 16 stale-receipt blocks) |
| coverage manifests + set-equality + citation checks | prove nothing was silently skipped | **replace** | `## Not examined` section (honest gaps, §5 doctrine kept: UNVERIFIED-critical caps at WARN) + reviewers still cite evidence per finding. Silent omission returns as a risk, accepted: the 2026-07-27 "3 extra violations per demanded sweep" incident is now answerable by a *human-requested* full sweep, not a standing per-round tax |
| continuity packets | carry prior findings into fresh rounds | **replace** | round-numbered report paths passed directly; same information, zero build steps |
| immutable round archives | prevent history rewrite | **replace** | round-numbered filenames make overwrite structurally unnatural; ledger `report_shas` (append-only) remains the tamper-evidence |
| 8-column lineage table | machine-validated finding continuity | **replace** | stable IDs + `resolved`/`persists` in prose; validation burden moves from schema to the 2-round cap (there is no round 5 for lineage to drift in) |
| `REVERSAL` class + mechanical stop | stop doctrine oscillation | **replace** | the 2-round cap reaches the human before oscillation can cycle; the one-sentence doctrine rule keeps the honest-labeling duty |
| `COVERAGE_BREACH` | void false closure claims | **delete** | no closure claims exist to breach |
| warn-ack (T3, all stations) | human sees residual risk | **narrow** | kept only at high-risk `review` (the last gate before publish); elsewhere WARN is recorded in receipt+ledger and proceeds |
| UNVERIFIED→WARN cap | UNVERIFIED never folds into PASS | **keep** (narrowed trigger: reviewer-marked UNVERIFIED-critical) |
| 6-element remedy contract | stop auditors becoming authors | **simplify** | 2 elements (invariant + minimum outcome) plus the §10 lattice rule that reviewers cannot add scope; the Feature-089 incident is covered by the retained "no unconditional replacement text" norm in the prompt |
| D-ID entailment two-part test | police derived obligations | **keep table + denylist, simplify test** | the closed D-ID schema and denylist stay (cheap, L1-validated); the adversarial "search for alternative implementations" paragraph shrinks to one reviewer instruction. Full test text remains available for disputes. *(Adjacent scope — owner may defer, §7 Q3)* |

---

## 4. Cost model

Assumptions: dispatch = one external agent run; v1 numbers reflect observed T3-dominated
behavior (audit §3, §4.6); "stops" excludes the by-design clarify stop.

| Case | Metric | v1 (observed shape) | v2 (design) |
| --- | --- | --- | --- |
| (a) clean ordinary Feature | dispatches | 6 (verify 2, analyze 2, review 2) at T3 effort | 6 at fixed effort |
| | report size | findings + 20–40-row coverage tables ×2 per station | findings + gaps list (~15–40 lines total) |
| | classifier/receipt steps | 5 reclassifications + gate-status per station | 0 separate steps (2 in-gate computations) |
| | human stops | 1–3 (warn-ack × UNVERIFIED compose) | **0** |
| (b) one real defect | extra cost | +2 dispatches (scoped round 2); tail risk unbounded (observed r=28) | +2 dispatches; hard ceiling, r3 needs ack |
| | format failure cost | full round re-entry | 1 single-agent retry |
| (c) genuinely high-risk | dispatches | as (a) | as (a) |
| | extra work | 7 targeted checks, adjacency scope, migration ack, warn-ack | same targeted checks, adjacency scope, migration ack, warn-ack at review only |
| | human stops | ≥1 per station reaching WARN | 1–2 (review warn-ack; migration ack) |

The intended recovery: case (a) — the common case — loses the coverage tables, the
classifier handshakes, and all warn-ack stops, which the audit identified as the dominant
per-round and stop costs in `/ms.analyze` and `/ms.verify`. Case (c) deliberately stays
almost as expensive as v1: high-risk work was never the problem.

---

## 5. Migration & rollout

Order of changes in this repo (one PR, one contract version):

1. `docs/templates/verification-v2.json` — signals, path classes, budgets, targeted checks.
2. `specter-gate.sh`: add `validate-report`, `ack-round`, in-gate risk-mode computation,
   round-budget refusal, round-numbered report handling; report
   `"contract": "verification-v2"`; **delete** `manifest`/`continuity` subcommands and
   coverage/lineage validation.
3. Retire `classify_audit_tier.py` and `audit-tier-policy.json` from the sync manifest
   (files remain in git history; consuming repos' installed copies become inert).
4. Rewrite protocols SKILL §4/§6/§7/§8 to §2 above; update the five station commands
   (report paths gain `.rN`, prompts lose coverage/lineage blocks, add format-retry step).
5. Tests: port the L1/L3 suites; new tests for round refusal (r2 pass, r3 no-ack fail,
   r3 ack pass), validate-report, risk-mode path facts, format-retry receipt fields.
6. `/ms.sync` broadcast after §6 replay passes. The existing version-check step in every
   command makes partial sync fail loudly (unchanged mechanism).

Consuming-repo state (C2): legacy `.specify/audit-tiers/`, `.specify/continuity/`, and
archives are **read-only legacy evidence** — never reinterpreted, never migrated. In-flight
Features: the next station they reach runs under v2 with fresh bindings (one v2 re-check at
their current position); no translation of legacy continuity history. Cleanup of legacy dirs
is a separate, user-approved step weeks later.

## 6. Replay validation plan

Corpus: the 86 recovered spec bodies (`.agent-io/spec-corpus-scan.md` method) plus the full
artifact sets (map section, spec, plan, tasks, diff) of the last ~20 completed Features in
2–3 consuming repos, plus holdouts.

Seeded defects (v2 must catch every one; each maps to a v1 catch or incident): missing owned
commitment in checklist; invented scope in spec (untagged); auth-touching diff with signal
declared `no` **and** an auth path fact (and one with prose-only auth change — expected
reviewer-dependent, recorded as the accepted residual); migration file without 6.6b ack;
stale SHA binding; malformed report; round-3 attempt without ack; report from wrong station
Mode.

Budgets (calibrated by the replay, per audit §11.3): clean Feature ≤6 dispatches, ≤3
automatic rounds total across its three grading stations, 0 human stops; cycle median within
1.3× of the pre-07-19 baseline on the timing proxy. Verdict comparison: v2 flips no v1 FAIL
to PASS on the seeded-defect set; every v1 FAIL that v2 no longer produces must trace to a
deleted-ceremony row in §3 with its acceptance noted.

## 7. Open questions (owner decisions)

1. **Reviewer effort defaults** — keep `codex: xhigh / antigravity: medium` everywhere, or
   drop codex to `high` in standard mode? Recommendation: keep `xhigh`; the audit showed
   effort was not the dominant cost, and one fixed pair is simpler.
2. **`analyze` warn-ack** — high-risk warn-ack is review-only in this design. If the owner
   wants a pre-implementation human look at high-risk Features, add it at `analyze` too.
   Recommendation: review-only; analyze WARNs are visible in the receipt regardless.
3. **D-ID entailment simplification** (§3 last row) — do it in this contract change or defer?
   Recommendation: defer to a separate decision; it is provenance scope, and bundling it here
   widens the diff for little throughput gain.
4. **Legacy state cleanup timing** — recommendation: ≥2 weeks after all consuming repos have
   completed at least one full v2 Feature.

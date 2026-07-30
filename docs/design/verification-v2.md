# verification-v2 — Merged Final Design

**Status**: accepted design, pre-implementation · **Date**: 2026-07-30
**Sources**: `verification-v2-claude.md` + `verification-v2-codex.md` (independent designs from
the identical brief `.agent-io/verification-v2-design-brief.md`), merged per the decision log
below. Where the two sources disagree with this document, this document wins.
**Evidence base**: `docs/audits/2026-07-30-verification-slowdown-analysis.md`,
`.agent-io/spec-corpus-scan.md`, `.agent-io/slowdown-analysis-codex-review.md`

## 0. Decision log (owner, 2026-07-30)

| # | Fork | Decision |
| --- | --- | --- |
| D1 | High-risk signal breadth | **Codex 8-signal list** — `state-machine` and `concurrency` are dropped as high-risk triggers (they drove the measured false-positive load: 44%/35% of real specs). Reviewers still see such work in ordinary review. |
| D2 | Human stops on high-risk residual WARN | **Named classes only** — migration / destructive-data / irreversible-operation / gate-or-policy-change, plus any high-risk required check that could not be observed. Auth/secrets advance automatically when all checks are observed. |
| D3 | D-ID entailment two-part test | **Removed from the gate.** D-ID rows remain optional implementation references; a D-ID used to justify observable behavior is an ordinary blocking finding routed to a PRD Amendment. The PRD-only authority rule (N6) carries the defense. |
| D4 | Continuity carrier (engineering call) | **Round-numbered report files** (`*.r1.md`, `*.r2.md`) — full prior-round reports pass by path; no archives, no packets, no overwrite ambiguity. |
| D5 | UNVERIFIED handling (engineering call) | **Reviewer-judged** — `Not checked` entries are graded by the reviewer (WARN or FAIL by impact); the only mechanical cap is the availability degrade. |
| D6 | Human-decision record (engineering call) | **Typed ledger events**, written by a gate decision command and bound to the receipt hash — no ack files, no extra store. |

## 1. Design summary

verification-v2 keeps the safety boundary and deletes the cost machinery around it.

Kept unchanged: station names and cycle order; L1 deterministic structure before any dispatch;
two fresh independent L2 reviewers with typed degrade; mechanical worst-of L3 over
station-fixed inputs; freshness/identity binding; PRD-only product authority; the append-only
ledger with verbatim `caught` rows; Done Criteria Execution; migration analysis; the
report-write/salvage marker protocol; the publish/release machinery.

New in v2, replacing v1 machinery:

- **Two risk profiles** (`ordinary`, `high-risk`) selected per station from a closed 8-signal
  Feature-Map table and deterministic changed-file facts. No prose scanning, no monotonic
  floor, no separate classifier process or receipt handshake.
- **One report schema** with `Checked` / `Not checked` honesty sections instead of coverage
  set-equality; a 6-column findings table instead of 8-column lineage.
- **Round-numbered report files** instead of canonical-path overwrite + archives + packets.
- **An executable universal round budget**: 2 automatic rounds; the gate refuses round 3
  without a typed human decision event.
- **A format-retry lane**: a malformed report costs one same-agent retry, never a round.
- **A closed human-stop list** (§2.6).
- **One config** (`docs/templates/verification-v2.json`), **one receipt per station/scope**,
  **one ledger**. Deleted stores: `.specify/audit-tiers/`, `.specify/continuity/`, round
  archives, warn-ack files.

Deleted from v1: T1/T2/T3, `classify_audit_tier.py` + `audit-tier-policy.json`
(`artifact_scan_rules`, floors, 5 reclassification boundaries), coverage manifests and the
`manifest`/`continuity` gate subcommands, lineage classes (`REVERSAL`, `COVERAGE_BREACH`),
per-station warn-ack, the 6-element remedy contract (→ 3 clauses), the D-ID entailment gate
test.

## 2. The contract (normative)

### 2.1 Stations and layers

Grading stations: `pre-verify` (global scope), `verify`, `analyze`, `review` (Feature scope),
`expand-delta` (single-agent, v1 rules unchanged). `checklist`/`featuremap` remain isolated
authoring — draft grades, never verdicts. `clarify` remains the product-decision stop with
typed `interpretation` / `scope-addition` outcomes (§10 lattice, unchanged).

Per grading station, in order:

1. **L1 structural** — unchanged check set (required sections, ownership, DAG, placeholders,
   `CI passes green` suffixes, cited-ID cross-references) plus: valid `### Verification
   signals` table, and computation of the station's **input digest** (sha256 over the fixed
   ordered path+hash list). FAIL → failed receipt + ledger event, **zero agents dispatched**.
2. **L2 semantics** — Codex and Antigravity, always fresh, fixed effort (`codex: xhigh`,
   `antigravity: medium`, both profiles — effort is not risk-dependent), fixed artifact set,
   the input digest in the prompt. High-risk appends the applicable named checks and widens
   review scope to affected trust boundaries; nothing else differs.
3. **L3 aggregation** — `specter-gate.sh aggregate <station> <scope> --round N [--ledger]`.
   Station name fixes the two report paths (round-numbered); the caller cannot add, omit, or
   select inputs. Verdict = worst valid input (`FAIL > WARN > PASS`), folding in L1. Writes
   the receipt and the append-only ledger line. The host never re-grades or hand-writes
   either.

### 2.2 Risk profile

The Feature Map carries a closed `### Verification signals` table:
`| signal | yes/no | evidence (path:line) |`. Authors record evidence; they never assign a
profile. The **only** signals are:

`authorization` · `secrets` · `data-migration` · `destructive-data` ·
`irreversible-operation` · `public-contract` · `financial-or-regulated` ·
`gate-or-policy-change`

Rules:

- `high-risk` iff any signal is `yes` (checklist-time table drives `verify`/`analyze`) or any
  deterministic diff fact fires (review-time facts drive `review`).
- Diff facts (file-level, configured in `verification-v2.json`): migration directories;
  dependency manifests/lockfiles; CI/workflow files; SPECTER gate machinery
  (`.claude/`, `docs/templates/scripts/`, `scripts/specter/`, hooks); auth/secret/credential
  paths; plus **parsed changed-file content** for DDL (`CREATE|ALTER|DROP TABLE …`) and
  destructive operations in changed code/SQL. Changed files only — never spec/plan/tasks
  prose, never one bundle attributed to every path.
- A malformed signals table is L1 FAIL with a named remedy. A `yes/no` the artifacts
  contradict is a blocking reviewer finding (this, not a regex, keeps declarations honest).
  A legacy Feature without the table runs its one migration re-check as `high-risk`, then
  must gain the table.
- Manual raise: `--raise-risk`, upward only, recorded. No lowering flag exists (N5).
- No cross-phase floor: each station computes from its own current inputs; the ledger keeps
  old computations as history, never as a floor.

What `high-risk` adds — exhaustively: the applicable named checks (trust boundaries, data
integrity, state ownership, rollback, failure modes, public-contract compatibility, real
entrypoint/E2E) as a fixed `## High-risk checks` report table (one row per **triggered
signal**, not per requirement) and as mandatory Done Criteria rows at `review`; migration
analysis + owner acknowledgment when a migration is in the diff; the D2 named-class
acknowledgments. Reviewer count, effort, budget, schema: identical in both profiles.

### 2.3 Report schema (all L2 stations)

Report paths are round-numbered: `<base>.r<N>.md` (e.g.
`docs/prd/checklists/feature-006.codex-verify.r1.md`). Files are never overwritten; a new
round is a new file.

```markdown
# <Agent> <Station> Verification — Feature NNN — Round R

**Contract**: verification-v2
**Mode**: <fixed station mode>
**Scope**: <Feature NNN | global>
**Input Digest**: <digest from L1>
**Result**: PASS | WARN | FAIL
**Availability**: PRESENT | UNAVAILABLE (<reason>) | RECUSED (<reason>)

## Scope and evidence
**Checked**: <named check classes with citations or commands>
**Not checked**: <explicit exclusions with reasons, or the evidence basis for claiming none>

## Findings
| ID | Severity | State | Finding | Evidence | Required Fix |
| --- | --- | --- | --- | --- | --- |

## High-risk checks   (high-risk profile only — one row per triggered signal)
| Signal | Check | Result | Evidence |

## Verdict
<one short paragraph>
```

- `ID` is stable within the lane (`CX-V-003`). `State` is `new | persists | resolved`.
- `Required Fix` has exactly three clauses: the restored invariant; the minimum compliant
  repair; **no new scope** (with an Amendment escalation when product behavior would change).
  Reviewers never supply unconditional replacement product text.
- `Not checked` is graded by the reviewer: an unexamined area is scored WARN or FAIL by
  impact in the reviewer's own `Result` (D5). Retained doctrine, prompt-level: a lane that
  now rejects the state its own prior Required Fix prescribed must say so explicitly and
  recommend escalation, not a new fix.
- Validity (L3): non-empty; exactly one `Result`; `Contract`/`Mode`/`Scope` match the
  station; `Input Digest` matches current; parseable Findings table. Anything else is a
  **format defect** (§2.5), and after the format retry, FAIL.

Re-rounds (R = 2): the prompt lists both prior-round report paths; scope is the failing
findings + fix diffs (`pre-verify` alone re-runs full scope — map edits ripple globally).
Prior findings are carried by `ID` with `State`.

### 2.4 Round budget (executable)

- Round 1 full scope; round 2 scoped repair. **That is the whole automatic budget, every
  station, both profiles.**
- `aggregate --round N` for N ≥ 3 exits FAIL unless the ledger tail contains a matching typed
  human decision event (§2.6) bound to the current receipt hash. Unit tests exercise r2-pass,
  r3-no-decision-fail, r3-with-decision-pass, r28-fail.
- Post-cap options, verbatim, nothing else: fix and restart with a new input digest / amend
  the PRD authority / authorize **one** named doctrine-dispute round (fresh dual; can raise
  scrutiny, can never turn FAIL into WARN/PASS or change fixed inputs) / accept WARN with a
  typed event / stop.
- After the cap an unresolved FAIL stays FAIL. Oscillation and reversal pathologies reach the
  human at round 3 by construction — the budget, not classification machinery, is the stop.

### 2.5 Format-retry lane

After each agent run the driver executes `specter-gate.sh validate-report <path>`
(deterministic). Invalid → salvage from `===REPORT BEGIN/END===` markers → still invalid →
re-dispatch **that one agent** once, same round, prompt prefixed with the validator's error
list. Then FAIL stands. Receipts record `format_retries` per input. A format problem never
consumes a station round, the other agent's run, or a human stop.

### 2.6 Human decisions and stops

All human decisions are **typed ledger events** written by `specter-gate.sh decide
<type> <station> <scope> --reason <text>` — actor-attributed, bound to the current receipt
hash, append-only (D6). Decision types: `ack-migration`, `ack-destructive`,
`ack-irreversible`, `ack-gate-policy`, `ack-degrade`, `authorize-round`, `accept-warn`,
`stop`. A decision can never lower a verdict, effort, scope, or reviewer count.

The **complete** stop list:

1. `clarify` product decisions (by design, unchanged);
2. both reviewers environmentally unavailable (station stops — never host-only);
3. D2 named-class acknowledgments: migration / destructive-data / irreversible-operation /
   gate-or-policy-change present in the work;
4. a high-risk required check that could not be observed;
5. single-agent degrade **when the missing reviewer was needed for a triggered high-risk
   check** (otherwise the WARN cap records and proceeds);
6. unresolved FAIL or doctrine dispute at the round cap.

An ordinary WARN — any profile, any station except the cases above — is recorded in receipt
and ledger and **advances**.

### 2.7 Degrade (unchanged v1 semantics, restated)

Preflight failure after one retry → single-agent run + typed placeholder (`**Result**: WARN`,
`**Availability**: UNAVAILABLE (<reason>)`) + mechanical WARN cap
(`cap: single-agent-degrade`). Agent-authored failure → FAIL input after §2.5. `RECUSED` ≡
`UNAVAILABLE`. Both down → stop (§2.6.2).

### 2.8 State stores — one writer, one reader

| Store | Writer | Reader | Lifetime |
| --- | --- | --- | --- |
| `*.r<N>.md` reports | agent (or salvage) | L3; round-2 prompts | permanent; never overwritten |
| `.specify/verification-v2/<station>-<scope>.json` | `aggregate` | driving command; next station's precondition | current run; superseded per round |
| `.specify/specter-run.jsonl` | `aggregate --ledger`, `decide` | audits; rule pruning; round-3 authorization check | append-only, permanent |
| `docs/templates/verification-v2.json` | this repo, replay-gated changes | gate | versioned with contract |

Receipt schema (emitted by `aggregate`, sole writer):

```json
{
  "contract": "verification-v2", "station": "verify", "scope": "006",
  "round": 1, "automatic_round_cap": 2,
  "risk_profile": "ordinary|high-risk",
  "risk_evidence": [{"signal": "data-migration", "source": "feature-map.md:42"}],
  "input_digest": "sha256:…",
  "structural": {"verdict": "PASS", "reasons": []},
  "reports": [{"path": "…r1.md", "sha256": "…", "result": "PASS",
               "availability": "PRESENT", "format_retries": 0}],
  "verdict": "PASS|WARN|FAIL", "cap": null,
  "caught": ["verbatim finding rows"],
  "reasons": []
}
```

### 2.9 Contract versioning

`specter-gate.sh version` reports `"contract": "verification-v2"`; every station command
checks once per session and fails loudly on partial sync. Any diff touching the gate, the
config, or this contract is itself a `gate-or-policy-change` high-risk review, and every
change must pass the §6 replay (the anti-patchwork rule, audit §11.3).

## 3. Deleted v1 mechanisms — the job, and what does it now

| v1 mechanism | Disposition | What covers the motivating incident now |
| --- | --- | --- |
| T1/T2/T3 execution tiers | delete | two profiles; the "cheap tier" job is done by `ordinary` being the default for everyone (v1 delivered 0% T1 in 136 runs) |
| `artifact_scan_rules` prose regexes | delete | closed declared signals (reviewer-audited) + deterministic changed-file facts incl. parsed DDL/destructive content. Accepted residual: risky prose with a false `no` and no file fact is caught only by a reviewer — the corpus showed the regexes caught boilerplate, not risk |
| monotonic floor + 5 reclassification boundaries | delete | per-station recomputation from current inputs; ledger keeps history as history. Kills the permanent-false-positive and stale-receipt classes (16 observed blocks) |
| tier receipts + `gate-status` handshake | delete | profile computed inside `aggregate`; nothing to go stale |
| coverage manifests + set equality | delete | `Checked`/`Not checked` + per-finding citations + dual review. Accepted residual: mechanical closure claims are gone; a demanded full sweep is a human request, not a standing tax |
| continuity packets | delete | round-numbered prior report paths passed directly (D4) |
| immutable round archives | delete | round-numbered filenames + ledger `report_shas` (append-only tamper evidence) |
| 8-column lineage table | simplify | 6 columns with `State`; validation burden moves to the 2-round cap — there is no round 5 for lineage to drift in |
| `REVERSAL` mechanical stop | delete | the cap reaches the human before oscillation cycles; prompt-level honesty rule retained |
| `COVERAGE_BREACH` | delete | no closure claims exist to breach |
| warn-ack (T3 all stations) | narrow | D2 named classes + uncheckable-control only; everything else records and advances |
| `UNVERIFIED→WARN` mechanical cap | replace | reviewer grades `Not checked` by impact (D5); mechanical cap only for availability |
| 6-element remedy contract | simplify | 3 clauses (invariant / minimum repair / no new scope); Feature-089 protection lives in clause 3 + the no-replacement-product-text prompt rule |
| D-ID entailment two-part test | delete as gate (D3) | PRD-only authority; a scope-justifying D-ID is an ordinary blocking finding → Amendment. D-ID rows stay as optional references |

## 4. Cost model

| Case | v1 (observed shape) | v2 |
| --- | --- | --- |
| (a) clean ordinary Feature | 6 dispatches at T3 effort; coverage tables ×6; 5 classifier boundaries + per-station `gate-status`; 1–3 human stops | 6 dispatches; ~20–40-line reports; 0 separate classification steps; **0 human stops** |
| (b) one real defect | +2 dispatches; tail unbounded (r=28 observed); format failure = full round | +2 dispatches; hard cap; format failure = 1 same-agent retry |
| (c) genuinely high-risk | as (a) + 7 always-on modules + warn-ack per station | as (a) + named checks for triggered signals only + 1–2 named stops (migration ack; review) |

Target (validated by §6, not asserted): ordinary-cycle median within 10% of the pre-07-19
109-minute baseline; high-risk work deliberately stays near v1 cost.

## 5. Migration & rollout

One PR, one contract version, in this order:

1. Replay fixtures and tests first (§6 harness precedes production code).
2. `docs/templates/verification-v2.json` — signals, path classes, DDL/destructive content
   rules, budgets, named checks.
3. `specter-gate.sh`: `validate-report`, `decide`, in-gate profile computation, round-budget
   refusal, round-numbered inputs, receipt schema, `"contract": "verification-v2"`; delete
   `manifest`/`continuity` subcommands and coverage/lineage validation. Prove structural-FAIL
   dispatches zero agents before any command changes.
4. Protocols SKILL §4/§6/§7/§8 → §2 of this document; update
   `ms.{verify,analyze,review,pre-verify,checklist,specter}.md` (round-numbered paths,
   new prompts, format-retry step, decision commands).
5. Retire `classify_audit_tier.py` + `audit-tier-policy.json` from the sync manifest; add
   `verification-v2.json`. No command may retain a T1/T2/T3 fallback.
6. Tests ported/added; README/CHANGELOG; single committed change.
7. `/ms.sync` from a clean checkout only after the replay passes. Partial targets fail their
   version probe loudly (existing mechanism).

Consuming-repo state: legacy `.specify/audit-tiers/`, `.specify/continuity/`, archives,
warn-ack files, and v1 ledger lines are **read-only legacy evidence** — never translated,
never satisfying a v2 gate. Each in-flight Feature gets one fresh v2 re-check from its
current artifacts and diff. Cleanup is a separate user-approved commit per repo, no earlier
than every target passing the capability probe and completing one v2 Feature.

## 6. Replay validation plan

Harness before rewrite. Corpus: the 86 recovered specs + the last ~20 completed Features
(full artifact sets) across 2–3 consuming repos, stratified: ~10 ordinary, 2 authorization,
2 secrets, 2 public/financial, 2 migration/destructive/irreversible, 2 gate/policy; one
holdout per unrepresented high-risk signal.

Seeded defects (v2 must catch every one): missing owned commitment; untagged invented scope;
auth-touching diff with signal `no` **and** an auth path fact; prose-only auth change with a
false `no` (expected reviewer-dependent — recorded as the accepted residual, not a pass
criterion); migration without rollback analysis; destructive op in changed SQL; gate/policy
diff; stale input digest; wrong station Mode; malformed report; one reviewer down; both down;
round-3 without decision event; false prose triggers (`CI`, `retry`, `source of truth`) —
which v2 must **not** escalate.

Recorded per station: dispatches, required reads, report lines, format retries, mechanical
rejection reasons, rounds, human stops, profile evidence, verdict deltas, median/p95
wall-clock where transcripts permit.

Pass budgets: clean ordinary work ≤2 dispatches / 1 round / 0 stops / no new store per
station; one defect ≤4 dispatches / 2 rounds; high-risk adds named checks and ≤1 owner stop,
never a third automatic round; ordinary-cycle median ≤ 1.1 × the 109-minute baseline. v2
flips no v1 FAIL to PASS on the seeded set except where a §3 row records the acceptance.
Replay results get one adversarial dual review before `/ms.sync`.

## 7. Remaining open questions

1. **Reviewer effort defaults** — this design fixes `codex: xhigh / antigravity: medium`
   everywhere. Revisit only if replay wall-clock misses budget.
2. **Full-report retention** — round-numbered reports are committed with the repo (normal git
   history); no gate archive. If a compliance need for report retention beyond git appears,
   that is a product decision, not a verification store.
3. **Legacy state cleanup timing** — per §5; recommend ≥2 weeks after the last consuming repo
   completes a v2 Feature.

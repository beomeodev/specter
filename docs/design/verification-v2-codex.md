# verification-v2: SPECTER verification contract

## 1. Design summary

`verification-v2` keeps the safety boundary and removes the cost machinery around it. Every semantic station still runs deterministic Layer 1 checks before dispatch, two independent fresh Layer 2 reviews, and a Layer 3 aggregation over a fixed report set. Reports and the receipt bind to the exact current input revision. Product behavior still comes only from PRD text or an appended PRD Amendment, and the append-only run ledger remains the evidence base, including verbatim `caught` rows.

V2 has one ordinary profile and one closed, evidence-bound `high-risk` profile. The profile is selected from an explicit Feature-Map signal table and deterministic facts about changed files and diff hunks. It is never selected by scanning prose in `spec.md`, `plan.md`, or `tasks.md`. High risk adds named checks and, for irreversible or policy-changing work, one owner acknowledgment; it does not create a new effort tier or a larger retry loop.

The current receipt is the only verification state consulted by a gate. There is one fixed receipt path per station/scope, written by the v2 gate, and one append-only ledger written by the v2 gate. Reports remain agent-owned artifacts at the existing station paths. V2 deletes tier receipts and floors, prose artifact scanning, coverage manifests, continuity packets, immutable round archives, lineage classes, and per-station WARN-ack files.

The existing station names and order stay exactly `checklist → verify → specify → clarify → plan → tasks → analyze → implement → review`. `checklist` remains isolated authoring, not a verdict; `clarify` remains the product-decision stop. The other existing responsibilities remain, but `verify`, `analyze`, and `review` use the same v2 station contract. This is a versioned replacement: a v1 receipt or report can explain history, but can never satisfy a v2 gate.

## 2. The contract

### Station contract and cycle

`checklist` is authored by a fresh isolated subagent and checked structurally. Its draft result is not authoritative; `verify` is the first semantic verdict. `specify`, `plan`, `tasks`, and `implement` retain their existing document or implementation roles and do not invent a second semantic state machine. `clarify` must classify each decision as an in-envelope `interpretation` citing a C-ID/D-ID or a `scope-addition` routed to a PRD Amendment. A global `pre-verify` uses the same contract outside the per-Feature cycle.

For `verify`, `analyze`, and `review`, the following is normative:

1. Layer 1 runs first. It checks parseable structure, required artifact presence, identity, fixed input paths, placeholders, cross-references, and station-specific deterministic facts. A Layer-1 FAIL writes a failed receipt/ledger event and dispatches zero agents.
2. Layer 2 dispatches Codex and Antigravity independently, always with fresh context, the station's fixed artifact set, and the computed input digest. Both use the v2 report format. The host may not provide authoring reasoning or a preferred verdict.
3. Layer 3 is `aggregate <station> <scope>`. The station name fixes the two report paths; the caller cannot add, omit, reorder, or select them. It validates each report and computes the worst valid result: `FAIL > WARN > PASS`. It writes the current receipt and the append-only ledger line. The host never re-grades a report or writes an aggregated ledger row.

The fixed current receipt is `.specify/verification-v2/<station>-<scope>.json` (`global` for `pre-verify`, the Feature number for `verify`, `analyze`, and `review`). Its schema is:

```json
{
  "contract": "verification-v2", "station": "verify", "scope": "006",
  "round": 1, "automatic_round_cap": 2,
  "risk_profile": "ordinary|high-risk",
  "risk_evidence": [{"signal": "authorization", "source": "feature-map.md:42"}],
  "input_digest": "sha256 over the fixed path/hash list",
  "structural": {"verdict": "PASS", "reasons": []},
  "reports": [{"path": "fixed", "sha256": "...", "result": "PASS",
               "availability": "PRESENT|UNAVAILABLE|RECUSED"}],
  "verdict": "PASS|WARN|FAIL", "cap": null,
  "caught": ["verbatim finding rows from reports"],
  "reasons": []
}
```

The gate is the sole writer of the receipt. The receipt and ledger have one consumer contract: the conductor and replay/audit tooling read the same versioned records, never parallel state stores. A human decision is a typed event in that ledger, bound to the receipt hash, produced only by the v2 decision command. It is not a second acknowledgment file and cannot lower a verdict, effort, scope, or reviewer count.

### Risk profile

The Feature Map contains a closed `### Verification signals` table. Each row is `signal | yes/no | evidence path:line`; authors record evidence but never assign a profile. V2 accepts these signals only for: `authorization`, `secrets`, `data-migration`, `destructive-data`, `irreversible-operation`, `public-contract`, `financial-or-regulated`, and `gate-or-policy-change`. A malformed table is a Layer-1 FAIL. A legacy Feature without the table is `high-risk` for its one migration re-check, then must receive the table.

The profile is also raised, regardless of the table, by deterministic file-level facts: migration directories or DDL files; changed auth/permission/security paths; changed secret/crypto/credential paths; public schema/route contract files; destructive or irreversible operations detected in changed code/SQL; and changes under SPECTER commands, skills, agents, gate scripts, hooks, or policy templates. The detector uses paths and parsed changed-file content only. It never reads generic risk vocabulary from specification prose or assigns one whole diff bundle to every path.

`ordinary` runs the fixed station checks. `high-risk` adds the applicable named trust-boundary, data-integrity, rollback, failure-mode, public-contract, or real-entrypoint check to the same prompt and report. Migration, destructive-data, irreversible-operation, and gate/policy changes require one explicit owner acknowledgment before advancement or publication; authorization and secrets require no acknowledgment when all checks are observed, but an uncheckable control is a WARN/FAIL finding. A profile can only be raised by current evidence; there is no lowering flag.

### Report format and validity

Each agent writes only its fixed report path. The compact required form is:

```markdown
# <Agent> <Station> Verification
**Contract**: verification-v2
**Mode**: <fixed station mode>
**Scope**: <fixed scope>
**Input Digest**: <current digest>
**Result**: PASS | WARN | FAIL
**Availability**: PRESENT | UNAVAILABLE (<reason>) | RECUSED (<reason>)

## Scope and evidence
**Checked**: <named check classes, with citations or commands>
**Not checked**: <explicit exclusions, or the evidence basis for none>

## Findings
| ID | Severity | State | Finding | Evidence | Required Fix |
| --- | --- | --- | --- | --- | --- |

## Verdict
<short conclusion>
```

`Result` appears exactly once; `Contract`, `Mode`, `Scope`, and `Input Digest` must match the station. `Checked` and `Not checked` must be non-empty. Findings require evidence; `Required Fix` states the invariant, minimum repair, and “do not add scope,” with an Amendment escalation when product behavior would change. A high-risk report adds a small fixed `## High-risk checks` table, one row per triggered signal, not one row per requirement. No exact set-equality coverage table is valid or required.

Layer 3 retries a malformed, missing, or marker-salvageable report once with that same agent. This is a report-format retry, not a new station round and not a second reviewer dispatch. If the report remains invalid, its fixed input is `FAIL`; the host cannot relabel it as unavailable. A genuine preflight failure writes a valid `WARN` placeholder with `Availability`; one unavailable reviewer caps the station at `WARN`, while both unavailable stops the station with no host-only verdict.

### Round budget and human stops

The executable universal cap is two rounds: round 1 is full scope; round 2 is one fresh, scoped repair review over the changed evidence and prior caught rows. `pre-verify` uses full scope for its repair round because a map or ownership edit can ripple globally. The gate rejects `--round 3` and every larger value before reading reports. After round 2, the human receives exactly these choices: fix and restart with a new input digest, amend the PRD authority, authorize one named doctrine-dispute round, or stop. Authorization can start a fresh dual review but can never turn FAIL into WARN/PASS or change the fixed inputs.

The only human stops are: `clarify` product decisions; both reviewers unavailable; a high-risk migration/destructive/irreversible/policy acknowledgment; a high-risk required check that cannot be observed; and an unresolved FAIL or doctrine dispute at the cap. An ordinary WARN is recorded and may advance. A single-agent environmental WARN requires acknowledgment only when the high-risk profile says the missing reviewer was needed for a triggered check. No host flag can skip a reviewer, lower scope, lower effort, or bypass Layer 1/3.

## 3. What each deleted v1 mechanism's job was, and what now does that job

| v1 mechanism | Decision | v2 replacement or accepted risk |
| --- | --- | --- |
| T1/T2/T3 execution tiers | Delete | Ordinary/high-risk profile; fixed reviewer pair and budget for all. High risk gains named checks, not a broad effort multiplier. |
| `artifact_scan_rules` | Delete | Closed Feature-Map signals plus deterministic changed-file/path facts. No prose keyword scanner; generic words and negation cannot escalate work. |
| Monotonic floor | Delete | Profile is recomputed from current fixed inputs. An old false positive cannot permanently tax a Feature; the ledger preserves the old event as history. |
| Five reclassification boundaries | Delete | Classify once per station from that station's current inputs. Any input change invalidates the receipt and requires a fresh L1/L2/L3 run. |
| Coverage manifests and set equality | Delete | Compact `Checked`/`Not checked` evidence, findings citations, fixed station inputs, and dual independent review. Accepted risk: semantic exhaustiveness is not mechanically claimed. |
| Continuity packets | Delete | The next fresh prompt receives the prior ledger record/receipt path and the changed-evidence path. The ledger's `caught` rows are the only continuity payload. |
| Immutable round archives | Delete | The append-only ledger stores round, report SHAs, verdict, and `caught` rows verbatim. Clean report bodies are not gate state; deeper retention belongs in ordinary version control. |
| Eight-column lineage table | Simplify | Use `ID | Severity | State | Finding | Evidence | Required Fix`. A fresh reviewer may carry an ID from the prior ledger row; no predecessor graph or class parser can reject a station on table ceremony. |
| `REVERSAL` / `COVERAGE_BREACH` classes | Delete | A changed-evidence repair and the two-round cap handle reversals and late findings. Accepted risk: no mechanical special label; prior caught rows remain visible to the human and next reviewers. |
| `warn-ack` files | Delete | Ordinary WARN proceeds visibly. High-risk acknowledgments and cap decisions are typed ledger events bound to the current receipt hash. |
| `UNVERIFIED → WARN` cap | Simplify | `Not checked` is an honest gap, not a coverage row. The reviewer must choose WARN or FAIL based on impact; only `UNAVAILABLE`/`RECUSED` receives the mechanical single-agent WARN cap. |
| Six-element remedy contract | Simplify | Required Fix has three mandatory clauses: restored invariant, minimum repair, and no new scope; ambiguity routes to the owner/Amendment. This keeps authority protection without six prose fields per finding. |
| D-ID entailment two-part test | Delete as a gate; retain D-IDs as optional references | C-IDs and Amendments remain the only product authority. A D-ID may describe an implementation obligation but cannot introduce observable behavior; a questionable or scope-expanding D-ID is a reviewer finding routed to an Amendment. Accepted risk: less formal proof of derived necessity, offset by the PRD-only rule. |

## 4. Cost model

The comparison is per semantic dual-agent station, assuming a representative ordinary Feature with 12 v1 coverage keys and valid report writes. “Dispatches” counts external reviewer runs; a v2 malformed-report retry is shown separately because it does not consume a round.

| Case | v2 expected cost | v1 expected cost | Result |
| --- | --- | --- | --- |
| Clean ordinary Feature | 2 dispatches; 1 round; 0 human stops; 20–30 lines/report | 2–4 dispatches; 1–2 rounds; 1 human stop in the representative T3/WARN path; 55–90 lines/report | v2 removes the 12-row closure table, lineage, remedy prose, and receipt/ack repair surface. |
| One real defect, fixed by repair | 4 dispatches; 2 rounds; 0 human stops; 25–40 lines/report; one malformed report would add only 1 same-agent retry | 4–6 dispatches; 2–3 rounds; 1 human stop likely; 80–140 lines/report | v2 makes the second round scoped and bounds it mechanically. |
| Genuinely high-risk Feature | 2 dispatches; 1 round; 1 named owner stop when migration/destructive/irreversible/policy work is present; 35–50 lines/report | 2–4 dispatches; 1–2 rounds; 1 T3 WARN acknowledgment plus any migration stop; 80–140 lines/report | v2 spends scrutiny on declared/file facts and targeted checks, not generic prose or seven always-on modules. |

Across the three cycle stations (`verify`, `analyze`, `review`), a clean ordinary cycle is six reviewer dispatches, three rounds, and no human stop; one fixed defect adds two dispatches and one round at its station; a high-risk migration adds one owner acknowledgment, not another review round. The v1 values are representative contract behavior, not a claim that every run hit the upper bound; the audit’s measured 39 form rejections and 20 WARN acknowledgments explain why those costs were common. The target is to return ordinary-cycle median cost toward the pre-07-19 109-minute baseline while retaining the three load-bearing layers.

## 5. Migration & rollout

Legacy `.specify/audit-tiers/` receipts, WARN-ack files, continuity packets, round archives, and old ledger lines are legacy evidence. They are read-only and never translated, replayed as v2, or treated as proof of a v2 PASS. An in-flight Feature gets one fresh v2 re-check from its current artifacts and current diff. Its first v2 receipt is new evidence; old state is retained until the user explicitly approves cleanup.

The implementation order is:

1. Add the v2 replay fixtures and tests, then add the versioned report parser, fixed station resolver, universal cap check, receipt writer, and ledger aggregator to `docs/templates/scripts/specter-gate.sh`. The structural subcommand must be proven to dispatch zero agents on FAIL before commands change.
2. Replace the shared mechanics in `.claude/skills/specter-agent-protocols/SKILL.md`, then update `.claude/commands/ms.verify.md`, `ms.analyze.md`, `ms.review.md`, `ms.pre-verify.md`, `ms.checklist.md`, and `ms.specter.md` to use v2 paths, reports, cap, risk signals, and human decisions. Keep the cycle order unchanged.
3. Replace `docs/templates/audit-tier-policy.json` and `scripts/specter/classify_audit_tier.py` with the single v2 risk-profile authority in the gate contract. No command may retain a fallback to T1/T2/T3. Existing runtime copies and v1 state remain read-only until the migration window ends.
4. Update tests, README/CHANGELOG references, and the sync manifest in one committed SPECTER change. The manifest currently broadcasts `.claude/commands/ms.*.md`, `.claude/skills/*`, `.claude/agents/*.md`, `docs/templates/*`, and selected `scripts/specter` files; it must broadcast the v2 gate, protocol, report templates, and risk authority together and stop broadcasting the v1 classifier. `/ms.sync` itself and project-local `.specify/` state remain excluded.
5. Run `/ms.sync` only from a clean committed SPECTER checkout. A target with only half of the v2 capability fails its version probe; it never silently falls back to a cheaper contract. After every target receives the commit, re-check each in-flight Feature once under v2, then use the v2 receipt/ledger for all new cycles. Delete legacy state only after the owner approves cleanup for each consuming repository.

## 6. Replay validation plan

The first implementation slice is a replay harness, not a live workflow rewrite. Run v1 and v2 over the 86-spec corpus scan, plus at least the last 20 real Features with their Feature Map, checklist, spec/plan/tasks, changed-file diff, reports, and recorded ledger events. Stratify the 20 as 10 ordinary, two authorization, two secrets, two public/financial, two migration/destructive/irreversible, and two gate/policy Features; add one holdout for every high-risk signal not represented in that set. Replay v1 as legacy evidence only and replay v2 from current inputs.

Seed defects must include: a stale input digest; wrong station mode; malformed report; one reviewer unavailable; both reviewers unavailable; missing FR/task linkage; untagged product scope; a migration file with a missing rollback check; a destructive operation; a secret/auth change; a gate/policy diff; a false prose keyword such as `CI`, `retry`, or `source of truth`; a real defect fixed by a changed diff; and an unresolved defect at round 2. Verify that v2 catches every v1 load-bearing failure, rejects the false prose triggers, and never lets a host-selected report or verdict pass.

Record per station: Layer-1 dispatch count, reviewer dispatches and required reads, report lines and required fields, malformed-report retries, mechanical rejection reasons, automatic rounds, human stops, profile/risk evidence, verdict changes, and median/p95 wall-clock where transcripts permit. The replay passes only if these budgets hold: clean ordinary work is at most two reviewer dispatches, one automatic round, zero human stops, and no new state store; one defect is at most four dispatches and two rounds; high-risk work may add named deterministic checks and one owner stop but no third automatic round or third reviewer. Ordinary-cycle median must be no more than 10% above the pre-07-19 109-minute baseline, unless the owner records a product/security exception.

Reject any v2 rule that adds a required field, store, round, or human stop without catching a seeded defect the prior contract missed. A passing replay requires two independent semantic review of the results, mechanical verdict aggregation over station-fixed inputs, and a clean/partial-sync broadcast test. Only then may the v2 commit be synced to consuming repositories.

## 7. Open questions

1. Should auth or secrets changes require an owner stop even when every check passes? Recommendation: no. Keep the stop for migration, destructive, irreversible, and gate/policy changes; require explicit evidence and dual review for auth/secrets, and stop only when a required control is uncheckable.
2. Is full clean-report retention required for compliance? Recommendation: no gate archive. Keep report SHAs and all non-PASS `caught` rows in the ledger; if full reports are required, retain them in the repository’s normal committed audit history rather than adding a verification state store.
3. Should a human be able to authorize a post-cap doctrine round? Recommendation: yes, exactly one fresh dual round with a typed reason and receipt binding. It is an escalation of scrutiny, never a verdict downgrade or a way to select reports.
4. When may legacy state be deleted? Recommendation: only after every in-flight Feature has one v2 re-check, all targets pass the v2 capability probe, and the repository owner approves a cleanup commit. Until then, legacy state remains read-only evidence.

# SPECTER Verification Slowdown Analysis (2026-07-18 → 2026-07-30)

**Audit date**: 2026-07-30 (KST)
**Scope**: every SPECTER commit merged after 2026-07-17 15:00 UTC (= 2026-07-18 00:00 KST),
and the measured effect of those commits on Feature-cycle throughput in the consuming repos.
**Question asked**: why did the Codex/Antigravity stations (`/ms.verify`, `/ms.analyze`,
`/ms.review`) become so strict that delivery velocity halved, and why have the last few days
of corrective commits failed to recover it?

**Verdict**: the slowdown is real, measurable, and **2.5×** on a same-project comparison.
It is not caused by one bad commit. It is caused by a **cost-control mechanism that
inverted**: the audit-tier system, introduced on 2026-07-20 to make routine Features cheap,
never produces its cheap tier and almost always produces its most expensive one. Everything
else — declared-coverage closure, the coupled receipt/continuity state, the unenforced round
cap — multiplies that baseline.

**Independently reviewed** by Codex on the same day (`.agent-io/slowdown-analysis-codex-review.md`);
§11 records where that review confirmed, corrected, and extended this one, and carries the
joint recommendation: **contained redesign, not blanket rollback, not open-ended patching.**

---

## 1. Executive summary

| Rank | Suspect (detail §) | Landed | Evidence strength | Magnitude |
| --- | --- | --- | --- | --- |
| **1** | **Audit tiers degenerate to T3** (§4) — T3 is too easy to reach and monotonically sticky; T1 never occurs in practice | `ad4baec` (07-20) | **Confirmed** — 136 classifier outputs observed, 0 × T1 anywhere, 0 × T2 in the two slow repos | Sets the multiplier for everything below |
| **2** | **Declared-coverage closure (C5')** (§5) — one evidence row per inventory key, strict set equality | `6d38178` (07-27) | **Confirmed** — 14 format-only station rejections observed | large; exact share not identifiable |
| **3** | **Round cap is prose, never enforced** (§6) — `max_automatic_rounds` is validated but never compared to `--round` | `ad4baec`/`ddf7cfa` | **Confirmed, executably** — `--round 28` returns PASS on a controlled fixture; rounds up to 28 observed in the wild | the long tail |
| **4** | **Contract, receipt and continuity state** (§4.7, §5, §11.1) — coupled stores each able to reject a station on form | cumulative, peaking `6d38178` | **Confirmed** — 39 non-product station blocks observed in one repo | large; exact share not identifiable |
| **5** | **Contract bloat** (§8) — protocols 127 → 618 lines, gate script 284 → 1659 lines | cumulative | Confirmed by line counts; causal share not established | small |

Demoted after independent review: **removal of the `--effort`/`--quick`/`--fast`/`--skip-codex`
overrides** (`ad4baec`). It is real and it is friction, but those flags let the *host* pick a
cheaper gate, which the no-unilateral-downgrade invariant correctly forbids. It is not a cause
of the slowdown and restoring it is not the fix. See §7 and §12.

The per-station wall-clock deltas in §3 are measurements. Attributing a *percentage* of those
deltas to a named mechanism is inference — the data cannot separate mechanisms that run inside
the same station. Shares are therefore given as magnitude, not precision.

Measured throughput, same project (`suseonglm`), median wall-clock per station:

```
per-Feature cycle (sum of station medians)   109 min  →  276 min      2.5×
/ms.review completions per day (all repos)   5.3/day  →  1.3/day      0.25×
```

---

## 2. Method and data

Two independent sources were used.

**(a) Git history.** 52 commits, `+11,496 / −1,303` lines across 74 files, from `7073c6b`
(2026-07-18 16:56) to `3abf864` (2026-07-27 22:51).

**(b) Session transcripts.** `~/.claude/projects/*/*.jsonl` for the eight consuming repos
(`specter` itself and `cork` excluded from the timing analysis — neither runs the per-Feature
cycle on product code). 899 `ms.*` station launches were extracted with their timestamps.
Station duration = time from a station's launch to the next station launch in the same
session, or to the session's last event when it is the final station; durations over 240
minutes were discarded as idle. Medians are reported because the distribution is
right-skewed by human think-time.

Three eras:

| Era | Window | What was in force |
| --- | --- | --- |
| `pre` | ≤ 2026-07-18 | pre-change baseline |
| `mid` | 07-19 → 07-26 | three-layer contract, renamed stations, audit tiers, provenance lattice |
| `post` | 07-27 → | + continuity-v1 |

**Caveats, stated up front.** The `post` window is small (n = 3–6 per station) and comes
entirely from one repo, `suseonglm`. Durations include human latency. Feature complexity is
not controlled for. Those caveats are why §3 reports a **within-project** comparison as the
headline number rather than the cross-project one — but the direction and rough magnitude
agree across every station and both comparisons, and the classifier evidence in §4 is exact
rather than statistical.

---

## 3. Measured impact

### 3.1 Per-station medians, all repos (minutes)

| Station | pre | mid | post | pre → post |
| --- | ---: | ---: | ---: | ---: |
| `/ms.checklist` | 2.0 | 15.6 | 9.1 | **4.6×** |
| `/ms.verify` | 6.0 | 14.3 | 21.4 | **3.6×** |
| `/ms.specify` | 4.4 | 15.8 | 13.0 | 3.0× |
| `/ms.clarify` | 4.4 | 3.0 | 7.9 | 1.8× |
| `/ms.plan` | 3.4 | 3.5 | 5.3 | 1.6× |
| `/ms.tasks` | 2.1 | 1.9 | 2.5 | **1.2×** |
| `/ms.analyze` | 9.7 | 25.4 | 60.0 | **6.2×** |
| `/ms.implement` | 19.1 | 18.1 | 45.5 | 2.4× |
| `/ms.review` | 38.0 | 97.9 | 111.8 | **2.9×** |

`/ms.tasks` is the control: it is the only station in the cycle that gained no new contract,
no classifier call, and no agent dispatch. It did not move. Every station that gained a
classifier call or an agent contract did.

### 3.2 Within-project comparison (`suseonglm` only)

This removes the project-mix confound. `pre` n = 4–13 per station, `post` n = 3–6.

| Station | pre | post | Δ min | share of total Δ |
| --- | ---: | ---: | ---: | ---: |
| `/ms.review` | 51.4 | 111.8 | **+60.4** | 36% |
| `/ms.analyze` | 6.8 | 60.0 | **+53.2** | 32% |
| `/ms.verify` | 3.6 | 21.4 | +17.8 | 11% |
| `/ms.implement` | 29.2 | 45.5 | +16.3 | 10% |
| `/ms.specify` | 4.3 | 13.0 | +8.7 | 5% |
| `/ms.checklist` | 2.0 | 9.1 | +7.1 | 4% |
| `/ms.clarify` | 5.5 | 7.9 | +2.4 | 1% |
| `/ms.plan` | 3.6 | 5.3 | +1.7 | 1% |
| `/ms.tasks` | 2.1 | 2.5 | +0.4 | 0% |
| **cycle total** | **109** | **276** | **+168** | **2.5×** |

**The three dual-agent stations account for 79% of the added time.** That is consistent with
the reported symptom: the Codex-involved stations are where the cycle now lives.

### 3.3 Throughput

`/ms.review` launches per calendar day, all repos — a proxy for Features reaching completion:

```
07-12  █████████ 9        07-19  █ 1
07-13  ████ 4             07-20  █ 1
07-14  ███████ 7          07-23  █ 1
07-15  ███ 3              07-27  █ 1
07-16  █ 1                07-28  █ 1
07-17  ████ 4             07-29  ██ 2
07-18  █████████ 9
       mean 5.3/day              mean 1.3/day
```

This independently reproduces the reported "5–6 per day → 5 per 48 hours".

---

## 4. Suspect #1 (prime): the audit-tier system inverted

### 4.1 What it was supposed to do

`ad4baec` (2026-07-20) introduced deterministic Feature Audit Tiers: classify each Feature
T1/T2/T3 from evidence-bound signals, and spend reviewer effort proportionally. T1 = routine
(cheap reviewers, narrow scope, 2-round cap); T2 = standard; T3 = high-risk (strongest
effort, widest scope, 7 targeted check modules, **human acknowledgment required for any
WARN**).

### 4.2 What it actually does — observed classifier output

Every `effective_tier` value emitted by `classify_audit_tier.py` in the transcripts:

| Repo | T1 | T2 | T3 |
| --- | ---: | ---: | ---: |
| `suseonglm` (the slow repo) | 0 | 0 | **100** |
| `doit-n-live` | 0 | 0 | **24** |
| `spade-ace-backtester` | 0 | 10 | 2 |
| **total** | **0** | **10** | **126** |

**T1 has never once been produced.** In the two repos where the slowdown was reported, the
tier is T3 100% of the time. Because the effective tier is monotonic across the five
classification boundaries, one T3 hit at any phase locks the Feature at T3 for the rest of
its cycle.

### 4.3 Why T1 never occurs in practice

**Correction (independent review, 2026-07-30).** An earlier draft of this report said T1 was
"unreachable". That overstates it and is refuted by the code: `classify_audit_tier.py:307-339`
contains a working T1 branch, and `tests/specter/test_audit_tier.py:58-93` exercises it. The
accurate claim is narrower and still damning: **T1 is reachable in principle, has never been
produced in 136 real classifications, and T3 is both too easy to reach and monotonically
sticky once reached.**

`docs/templates/audit-tier-policy.json` → `t1_eligibility` requires **all 16 boolean signals
to be exactly `"no"`**, plus `estimated_domains == 1`, `behavioral_fr_count ≤ 3`, and
`estimated_touched_files ≤ 8`. A value of `"unknown"` on any one of the 16 fails the
predicate (`classify_audit_tier.py:315-321`). Among the 16 are
`cross_layer_or_cross_feature_contract`, `persistence_change`, and `new_runtime_dependency` —
true for essentially any real Feature that touches both a UI and a store.

Note also the evaluation order: any hard-risk signal returns T3 *before* T1 eligibility is
considered at all (`classify_audit_tier.py:297-305`). Legitimately risky work therefore
correctly reaches T3 — the defect is the false-positive path in §4.4–4.5, not the existence of T3.

### 4.4 Why T3 fires on boilerplate

`artifact_scan_rules` run raw case-insensitive regexes over the **full text** of `spec.md`,
`plan.md`, and `tasks.md` (`scan_artifacts`, `classify_audit_tier.py:438-473`). A single
match anywhere sets the rule's signal to `yes` and raises the tier. Several patterns are far
broader than their rule names suggest:

| Rule | Tier | Pattern includes |
| --- | --- | --- |
| `build-release-policy` | **T3** | `\bCI\b`, `release`, `publish`, `hook`, `permission`, `sandbox` |
| `concurrency-distributed` | **T3** | `retry`, `queue`, `lease`, `coordination`, `idempotenc` |
| `state-machine-multistore` | **T3** | `source of truth`, `reconciliation`, `state transition` |
| `audit-policy-change` | **T3** | `audit_tier`, `three-layer gate` |

### 4.5 Corpus test: the real spec.md population (2026-07-30)

The claim above was tested against the real population rather than the template. 86 generated
`spec.md` bodies were recovered from the session transcripts of seven consuming repos (atlas,
cork, cueline, doit-n-live, sanjunipero, spade-ace-backtester, suseonglm, vent-cycle) and run
through the **actual `scan_artifacts` implementation** with the shipped policy, spec phase.

**Result: 83 of 86 (97%) classify T3 from the artifact scan alone**, before any declared Audit
signal is considered. Rule fire rates:

| Rule | Tier | Fires on |
| --- | --- | ---: |
| `build-release-policy` | T3 | **72 / 86 (84%)** |
| `state-machine-multistore` | T3 | 38 / 86 (44%) |
| `concurrency-distributed` | T3 | 30 / 86 (35%) |
| `auth-or-ownership` | T3 | 16 / 86 (19%) |
| `sensitive-destructive-data` | T3 | 16 / 86 (19%) |
| `secrets-crypto` | T3 | 15 / 86 (17%) |
| `schema-migration` / `public-external-contract` / `money-financial` | T3 | 3 each |
| `audit-policy-change` | T3 | 1 |

#### (a) Correction: the template-guidance hypothesis is refuted

An earlier draft argued that generated specs inherit the trigger vocabulary from the
`### Audit-Relevant Behavior` guidance comment in `spec-template.md:109-123`. **The corpus
refutes this.** Of 86 real specs, **1 retains the section heading and 0 retain the
instructional comment** — Spec-Kit strips it during generation. The template does self-trigger
five T3 rules when scanned directly, but that path does not reach production specs. The claim
is withdrawn.

#### (b) The actual #1 trigger is SPECTER's own mandatory boilerplate

`build-release-policy` fires on 84% of specs. The matched terms, counted across the corpus:

| Term | Specs |
| --- | ---: |
| **`CI`** | **69** |
| `release` | 12 |
| `hook` | 7 |
| `publish` | 6 |
| `permission` | 3 |

The dominant match, verbatim from the corpus:

```
- **SC-006**: CI passes green.
```

**SPECTER's structural gate requires every Feature's last done criterion to be
`CI passes green`** (`ms.checklist.md:303`, `ms.verify.md:202`, `ms.featuremap.md:274`). That
mandatory phrase carries into the spec's success criteria, and the classifier then reads the
token `CI` as evidence of build/release/policy risk and escalates the Feature to maximum audit
intensity. **The workflow compels the text that makes the workflow expensive.** 14 of 86 specs
(16%) are T3 for that literal token and nothing else.

The same shape repeats with SPECTER's own doctrine vocabulary: `source of truth` — the phrase
`AGENTS.md` §4 tells authors to preserve — fires `state-machine-multistore` on 25 specs.

This is the same defect class as the two bugs already fixed on 2026-07-27 (`6725fa3` "stop the
diff-phase receipt from invalidating itself", `ca17927` "keep the receipt guard parseable") —
**gate machinery matching its own text** — but reaching the workflow's own required
deliverables rather than the classifier's own files.

#### (c) The scanner is blind to negation, scope, and cross-references

Real matches from the corpus, each of which raised a Feature to T3:

| Matched text in the spec | Rule fired | What the sentence actually says |
| --- | --- | --- |
| "**Retention** of logs/screenshots/traces is out of scope and owned by Feature 008." | `sensitive-destructive-data` | this Feature explicitly does *not* do it |
| "Enable resumes at the next transition, no immediate **reconciliation**" | `state-machine-multistore` | the absence of reconciliation |
| "**retry** orchestration + shared lock (Feature 004) … are out of scope" | `concurrency-distributed` | another Feature's concern |

A boundary statement — the thing a good spec is supposed to contain — is read as risk evidence.

#### (d) Narrowing the patterns is not sufficient — this is why the fix must be a redesign

Counterfactual tier distributions over the same 86 specs:

| Scan configuration | T3 share |
| --- | ---: |
| as shipped | **97%** |
| drop the bare token `CI` | 80% |
| drop the whole `build-release-policy` rule | 76% |
| + drop `source of truth`, `reconciliation` | 69% |
| + drop `retry`, `queue` | 62% |
| + drop `retention`, `restore` | **58%** |

Even after stripping every obviously false trigger, **58% of Features still classify T3**, and
T1 remains rare. Pattern tuning buys back part of the multiplier and then stalls. The rule set
is not mis-tuned; **a keyword scan over prose is the wrong instrument for risk classification**,
which is the direct evidence for §11.2's recommendation to replace the three execution tiers
with one closed, evidence-bound high-risk profile rather than to keep tuning regexes.

Reproduce: `.agent-io/spec-corpus-scan.md` records the method and the per-spec results.

### 4.6 What T3 costs

Relative to T2, T3 changes (`audit-tier-policy.json` → `tiers.T3`):

- Antigravity effort `medium` → `high` (Codex is `xhigh` in both — the effort knob is *not*
  the main cost; the three below are)
- `review_scope`: `current-specter-standard` → `feature-plus-adjacent-trust-boundaries-and-affected-seams`
- `targeted_checks`: `[]` → **7 modules**, including `relevant-real-entrypoint-or-e2e`, which
  `/ms.review` Step 6.6 explicitly says a narrower unit check does not satisfy
- `warn_handling`: `record` → **`human-ack`**

That last one is the throughput killer for unattended cycles: **20 `warn_ack_required` events
were observed in `suseonglm`**. Each one stops the conductor dead until a human types an
acknowledgment. Combined with §5's WARN cap, a T3 Feature is close to guaranteed to stop for
a human at least once per station.

### 4.7 Two follow-on defects found by the independent review

**(a) The monotonic floor makes the false positive permanent — this is a migration problem,
not just a classification problem.** The effective tier is the maximum of the newly computed
tier, the prior receipt, the historical ledger floor, and any manual raise
(`classify_audit_tier.py:599-646`). So a Feature that was escalated once by a vocabulary match
**stays T3 for the rest of its life even after the regexes are fixed**. Any remediation that
only narrows the patterns will leave every in-flight Feature at maximum cost. A fix therefore
needs an explicit, user-authorized recomputation path for existing receipts — otherwise the
recovery is invisible for weeks.

**(b) The diff phase attributes the whole diff bundle to every changed file.**
`classify_audit_tier.py:578-588` assigns the single concatenated diff bundle as the text of
*every* changed path. The tier outcome is the same as scanning the bundle once, so this does
not inflate the tier — but every reason string then names every touched file as evidence, so
the receipt reports one risky string as if many files were risky. That destroys the value of
the receipt as a human-readable audit trail exactly when a human is being asked to acknowledge
a WARN. Distinct defect from §4.4; worth fixing with it.

---

## 5. Suspect #2: declared-coverage closure (continuity-v1, 07-27)

`6d38178` added the `## Coverage` contract to `/ms.pre-verify`, `/ms.verify`, `/ms.analyze`:
the gate generates an expected key inventory (`specter-gate.sh manifest`) and each reviewer
must return **exactly one `| Key | Result | Evidence |` row per key**, with non-empty evidence
and existing `file:line` citations. For `/ms.analyze` the inventory is every `FR-*` in
`spec.md` plus every owned C-ID plus every owned D-ID.

Three cost mechanisms, all confirmed firing in real runs:

**(a) Per-round output volume scales with the artifact.** A Feature with 20 FRs and 10
commitments makes each of two reviewers produce a 30-row evidence table every full round, on
top of the findings table. This is the most likely single explanation for `/ms.analyze` going
6.8 → 60.0 minutes.

**(b) A new blocking failure surface that has nothing to do with product defects.**
`specter-gate.sh` FAILs the station on: missing `## Coverage`, set inequality, duplicate keys,
empty evidence, or a citation to a non-existent file. Observed in the transcripts:

| Rejection reason | `suseonglm` | `specter` |
| --- | ---: | ---: |
| coverage not set-equal to inventory | 6 | 2 |
| findings-lineage rejected (dup ID / unknown predecessor) | 7 | 2 |
| missing `## Coverage` section | 2 | 2 |
| duplicate coverage keys | 2 | 2 |
| citation to non-existent file | 2 | 2 |
| empty coverage evidence | 2 | 1 |
| round archive conflict | 2 | 0 |
| **stale/invalid audit-tier receipt** | **16** | 2 |
| **total station blocks from machinery** | **39** | **13** |

Every one of those 39 events blocked a station on **report formatting or receipt freshness**,
not on a defect in the product — and each one costs a re-dispatch of two agents at T3 effort.

**(c) Any `UNVERIFIED` coverage row caps the report at WARN**
(`specter-gate.sh:1244-1248`). Under §5 the reviewer is instructed to mark anything it could
not actually check as `UNVERIFIED` and to grade down on doubt. With 30 keys, at least one
`UNVERIFIED` is close to certain → WARN → and at T3, `warn_handling: human-ack` → the
pipeline stops for a human. **The doctrine and the tier setting compose into a near-guaranteed
human stop per station.**

---

## 6. Suspect #3: the round cap is documented but never enforced

Protocol §4 and `tier_settings.max_automatic_rounds` (T1: 2, T2/T3: 3) define the cap.
`ddf7cfa` (07-24) added a fixed cap of 3 for receipt-less global stations after the
doit-n-live 17-round incident.

**None of it is mechanically enforced.** `max_automatic_rounds` appears in the codebase in
exactly one place — `classify_audit_tier.py:128`, where it is validated as a positive integer.
It is never compared against anything at runtime. `specter-gate.sh` accepts `--round <any
integer>` (`:749-759`, `:884-897`) and records it. The cap is prose addressed to an LLM host.

**Executable proof** (independent review, 2026-07-30): on a controlled fixture carrying the two
fixed `/ms.review` reports and current gate inputs,
`specter-gate.sh aggregate review … --ledger --round 28` returned
`{"verdict":"PASS","round":28,"reasons":[]}`. The gate does not merely fail to stop round 28 —
it records it as a clean pass.

Observed `aggregate --round N` calls:

| Repo | calls | max round | calls beyond cap 3 |
| --- | ---: | ---: | ---: |
| `suseonglm` | 146 | **28** | 37 |
| `doit-n-live` | 32 | **18** | 18 |
| `spade-ace-backtester` | 12 | 4 | 1 |
| `cork` | 46 | 4 | 1 |

Round distribution in `suseonglm`: `1:48, 2:31, 3:30, 4:10, 5:7, 6:4, 7:3, 8:3,
10/12/14/16/18/20/22/24/26/28: 1 each`. The even-numbered tail is a single escalation — the
28-round global gate that protocol §4 itself now cites as the reason the post-cap question
exists. The rule was written; the enforcement was not.

---

## 7. Demoted: the manual override was removed (friction, not cause)

Before 07-20, all three stations accepted `--model` / `--effort`, and `/ms.review` also took
`--quick`, `--fast`, and `--skip-codex`. The user could trade rigor for speed on a Feature
they knew was routine.

After `ad4baec`, all three stations **explicitly reject** them as "bypass or scope-lowering
arguments" (`ms.verify.md:103-104`, `ms.review.md:128-129`, `ms.analyze.md:99`). The only
remaining knob is `--raise-audit-tier`, which is upward-only by design.

The intent is sound — a host that can lower its own gate is not a gate. Combined with
Suspect #1 the visible result is that **the automatic mechanism always picks maximum intensity
and the manual correction was deleted in the same commit**, so there is currently no way
anywhere in the system to run a Feature cheaply.

**But this is not a cause of the slowdown, and restoring the flags is not the fix.** An
earlier draft ranked it #4; independent review correctly reclassified it as *misattributed*.
Those flags let the **host** — the same party that authored the artifacts under test — choose
a cheaper or skipped gate. That is precisely the self-downgrade the three-layer contract
exists to remove, and it was right to delete them. What is genuinely missing is not an
arbitrary bypass flag but a **bounded, declared, non-host cost profile**: a cheap path that the
*policy* selects for demonstrably low-risk work, or that a *human* authorizes on the record.
Fixing §4 removes the need for the lever entirely.

---

## 8. Suspect #5: contract bloat

Every reviewer round now reads and satisfies substantially more contract text:

| Artifact | 07-17 | now | growth |
| --- | ---: | ---: | ---: |
| `specter-agent-protocols/SKILL.md` | 127 | 618 | **4.9×** |
| `docs/templates/scripts/specter-gate.sh` | 284 | 1,659 | **5.8×** |
| `.claude/commands/ms.review.md` | 731 | 942 | 1.3× |
| `.claude/commands/ms.analyze.md` | 351 | 566 | 1.6× |
| `.claude/commands/ms.verify.md` | 320 | 424 | 1.3× |
| `.claude/commands/ms.pre-verify.md` | — | 487 | new |
| `scripts/specter/classify_audit_tier.py` | — | 1,230 | new |

The reviewer prompt itself grew from "check these bullet points" to: an 8-column lineage table
with predecessor/status/classification, a coverage table with one row per inventory key, a
6-element remedy contract per finding, and §10 provenance-lattice compliance including a
self-check. This is a real per-round tax, but it is the smallest of the five — it is listed
last deliberately.

---

## 9. Why the last few days of fixes did not recover velocity

The 07-24 and 07-27 work correctly diagnosed **non-convergence** (17-round and 28-round
deadlocks) and shipped the right cures for it: the D-ID entailment fixed input (`facf494`),
the receipt-less 3-round cap (`ddf7cfa`), and continuity-v1's REVERSAL stop rule, termination
signals, and post-cap question (`6d38178`).

Those fixes address **how many rounds** the system runs. They do not address **what one round
costs** — and the measured regression is dominated by per-round cost, not by round count:
`/ms.analyze` invocations per session stayed flat at exactly 1.00 across all three eras while
its duration went 6.8 → 60.0 minutes. The extra time is *inside* the station.

Worse, continuity-v1 paid for its convergence guarantees with per-round cost: the coverage
manifest, the lineage columns, the immutable archives, and the remedy contract all increase
what a single round has to produce and all add new ways for a round to be rejected on format.
The 07-27 release plausibly made round *count* better and round *cost* worse at the same time,
which is exactly the pattern in §3.1: `mid` → `post` shows `/ms.analyze` more than doubling
again after the fix landed.

---

## 10. Recommendations

Ordered by expected recovery per unit of risk. Nothing here weakens L1, dual independent L2
reviewers, fixed-input L3 aggregation, freshness bindings, or the no-host-downgrade rule.

### P0 — Make tiering work as designed (recovers the multiplier)

1. **Stop the classifier from reading its own instructions.** Strip HTML comments and
   template guidance blocks before `scan_artifacts` runs, and extend the
   `GATE_MACHINERY_PATHS` exclusion principle from the `diff` phase to the
   `spec`/`plan`/`pre-implement` phases. Same defect class as `6725fa3`/`ca17927`.
2. **Remove the trigger vocabulary from `spec-template.md`.** The `### Audit-Relevant
   Behavior` guidance block currently guarantees T3. Rewrite it so it does not enumerate the
   scan keywords, or move the guidance out of the emitted artifact.
3. **Narrow the T3 content patterns.** `\bCI\b`, `\bhook\b`, `\bpermission\b`, `\bretry\b`,
   `\bqueue\b`, and `source of truth` are ordinary engineering vocabulary, not risk evidence.
   Require a path match, or a content match in a designated section, rather than a bare word
   anywhere in the file. Verification: re-run the classifier over the last 20 real Features
   and confirm the tier distribution is no longer 100% T3.
4. **Make T1 reachable.** Allow `"unknown"` on non-hard-risk booleans without failing
   eligibility, and raise `estimated_touched_files_max` / `behavioral_fr_count_max` to values
   a real routine Feature can meet. A tier that has fired zero times in 126 classifications
   is not a tier.

### P1 — Cap the per-round cost (recovers ~30%)

5. **Scope declared-coverage closure by tier.** Full per-key coverage on round 1 of T3 is
   defensible. Requiring it on every full-scope round of every station at every tier is what
   pushed `/ms.analyze` to an hour. Consider: coverage mandatory at T3, sampled-with-
   justification at T2, off at T1.
6. **Decouple `UNVERIFIED` from the T3 human-ack.** Today one honestly-marked unverifiable
   key forces a human stop. Either let `UNVERIFIED` rows carry a machine-recorded reason
   without capping the station, or make `human-ack` apply to WARNs that come from findings
   rather than from coverage bookkeeping.

### P2 — Enforce what is already written (recovers the tail)

7. **Enforce the round cap mechanically.** `specter-gate.sh aggregate` should refuse
   `--round N` when `N > tier_settings.max_automatic_rounds` (or > 3 at receipt-less
   stations) unless an explicit, recorded human authorization exists. The 28-round run proves
   prose caps do not hold. This is a small change with a large tail effect.
8. **Reduce the stale-receipt failure rate.** 16 stale/invalid receipt blocks in one repo is
   the single most frequent machinery failure. Investigate whether reclassification at five
   boundaries is racing with ordinary artifact edits, and consider auto-reclassifying on a
   detected staleness instead of failing the station.

### P3 — Restore a legitimate speed lever

9. **Add a recorded, non-silent downgrade path.** Not a host-chosen `--effort` (that
   correctly stays banned), but a **user-authorized** tier assertion that is written into the
   receipt with the actor and reason, visible in the ledger, and auditable after the fact.
   The current design's failure mode is that a human who *knows* a Feature is routine has no
   sanctioned way to say so.

---

## 11. Joint conclusion after independent review (Codex, 2026-07-30)

This report was handed to Codex (gpt-5.6-luna, xhigh) with a brief instructing it to form its
own ranked root-cause list *before* reading this document, then to attempt to refute the prime
suspect, then to answer the rollback-vs-fix-vs-redesign question. Its report:
`.agent-io/slowdown-analysis-codex-review.md`. Brief: `.agent-io/slowdown-analysis-brief.md`.

### 11.1 Reconciliation

| Claim in this report | Independent verdict | Resolution applied |
| --- | --- | --- |
| Tier system inverted; T3 always, T1 never | **PARTIAL** — T3 dominance and its cost envelope confirmed by policy, classifier output, and a direct template scan; "T1 unreachable" refuted by the working T1 branch and its passing tests | §4.3 corrected; claim narrowed to "never reached in practice, T3 too easy and sticky" |
| Coverage closure is a large cost and rejection surface | **CONFIRMED** | kept; percentage removed |
| Round cap unenforced | **CONFIRMED, and reproduced** — `--round 28` returns a clean PASS on a fixture | §6 strengthened with the executable proof |
| Removing the override flags cost velocity | **MISATTRIBUTED** | demoted out of the ranked list; §7 rewritten |
| Contract bloat contributes | **PARTIAL** — expansion is real, but line count does not establish a time share | kept, marked small, share removed |

Both analyses independently converged on the same four mechanisms and on the same causal
shape: `classification intensity × report contract × mechanical closure/receipt checks ×
round behavior`. Neither can attribute an exact percentage to a mechanism, because several run
inside one station. That limitation is now stated wherever a share appears.

The review also surfaced three things this report had missed or underweighted: the monotonic
floor turning a false positive into a permanent cost (now §4.6a), the diff-bundle attribution
defect (§4.6b), and the fact that `/ms.pre-verify`'s final full-scope certification round is a
whole extra audit that any cost model must count (`ms.pre-verify.md:334-350`).

### 11.2 The strategic answer: contained redesign, not rollback, not open-ended patching

Both analyses reject a blanket revert to `7073c6b^`, for the same reason: that window also
shipped the three-layer author/judge separation, the security hardening in `0291623`, the
evidence-binding fixes, the reviewer-recusal rule, and the publish/release mechanization —
none of which are implicated in the cost, all of which close real defects. Reverting the whole
range trades measured latency for known integrity regressions.

Both also reject continuing to patch. The reason is structural, not aesthetic: the current
design maintains **policy, tier receipts, historical floors, coverage manifests, continuity
packets, immutable round archives, finding lineage, command prose, and ledger state as
separate authorities**. Every local fix has to be consistent with all of them, which is exactly
how the 07-27 self-invalidation and parser bugs arose. That is the patchwork risk, named
concretely.

**The recommended path is a contained `verification-v2` contract** — one versioned change that
removes states rather than a sequence of exceptions — preceded by immediate containment:

- **Containment now** (hours, low risk): make the gate reject `--round` above the declared cap
  before it reads any report, with unit tests at `--round 3` and `--round 28`; and stop
  dispatching agents when tier state is stale or invalid instead of failing the station after
  the spend.
- **v2 design** (the nine points in the Codex report §"Minimum coherent verification system"):
  keep L1 deterministic structure, two fresh independent L2 reviewers, fixed mechanical L3
  aggregation, current-input identity binding, and PRD-only product authority. Replace the
  three execution tiers with one closed, evidence-bound high-risk profile that cannot be
  inferred from generic vocabulary or from a whole diff bundle. Replace exact coverage-key
  closure with evidence completeness (cite what you checked, state what you did not).
  Collapse the parallel state stores into one station receipt plus the append-only ledger.
  Make the round budget executable and universal.
- **Migration**: do not delete existing receipts or archives, and do not reinterpret a legacy
  PASS as a v2 PASS. In-flight Features are re-checked once under v2 — safer than translating
  continuity history into a smaller schema. Old state stays read-only until an explicit
  user-approved cleanup.
- **First slice is a replay harness, not a rewrite**: run v1 and proposed v2 over a fixed
  corpus of real Features — including a genuinely high-risk one, a small stateless one, an old
  T3 receipt, a stale receipt, a coverage failure, and a multi-round case — and compare
  verdicts and human stops *before* touching the consuming repos.

### 11.3 The anti-patchwork rule

The failure pattern in this window is not bad rules. It is **incident-driven rule accretion
with no cost budget**: every rule here was a locally correct response to a real, documented
incident (§4 cites a 17-round and a 28-round deadlock; §5's remedy contract cites the
Feature-089 episode; the mechanical ledger cites the 2026-07-10 under-reporting incident), and
nobody ever priced the aggregate. Both analyses independently proposed the same countermeasure,
and the executable form is Codex's:

> **No gate change ships unless it passes a load-bearing gate-budget replay.**
>
> Replay the old and proposed contracts over a fixed corpus of at least the last 20 real
> Features plus a holdout per high-risk signal, and record: external dispatch count and
> required reads per station; required report fields and mechanical rejection reasons;
> automatic round count and human-stop count; verdict changes against seeded defects; median
> and p95 station wall-clock.
>
> A proposed rule is **rejected** if it adds a required field, state store, round, or human
> stop without catching a seeded defect the prior contract missed. A rule that does catch one
> is accepted only with an explicit cost budget and a single owning authority. Starting
> budget: a clean Feature may not gain more than one required external dispatch, one automatic
> repair round, or one human stop; aggregate median cost may not rise more than 10% without an
> explicit product or security decision.
>
> Every accepted change lands as **one contract-version update** covering policy, gate,
> command, and tests together. No isolated regex, receipt, coverage, or retry patch merges
> merely because it fixes the latest failing example. If a rule cannot be explained as either
> (a) a deterministic protection for a named invariant or (b) a bounded response to a
> demonstrated defect, it is ceremony and does not enter the gate.

This repo can actually enforce the "did it ever catch anything" half of that test today: the
mechanical ledger already records `caught` rows verbatim per station (`specter-agent-protocols`
§7). A rule that has caught nothing across N Features is a deletion candidate on evidence, not
on opinion. The budget numbers above are proposed engineering budgets, not measurements, and
should be calibrated by the first replay.

### 11.4 What is *not* settled

- The exact share of the 2.5× recoverable by each fix. Nobody can state this before the replay.
- Whether the 07-19 three-layer rewiring or the 07-20 tier system is the true inflection point.
  The `mid`-era sample (n = 3–5) cannot separate them; both analyses argue from code that the
  tiers are the multiplier and the three-layer split is not, but that is inference.
- Whether generated `spec.md` files retain the template's guidance comments in every project.
  The template scan proves the mechanism exists; it does not prove the rate. Checking one real
  generated spec in a consuming repo would settle it in a minute and is worth doing first.

## 12. Appendix

### A. Commit timeline (2026-07-18 → 2026-07-27)

| Date | Commit | Change |
| --- | --- | --- |
| 07-18 | `7073c6b` | conditional State Ownership & Invariants gate in `/ms.plan` + `/ms.review` |
| 07-18 | `d87a7f2` | implementation-delegation discipline, reviewer recusal |
| 07-18 | `28a6bd6`…`61cc252` | Codex full-audit batches B1–B5 (wording, gate evidence binding, publish, security) |
| 07-19 | `415c175`, `56d22b1` | **three-layer contract**: `specter-gate.sh version/structural/aggregate`, all stations rewired |
| 07-19 | `1c83ff3` | stations renamed (`ms.agent-verify` → `ms.verify`), authoring stations → dedicated fresh subagents |
| 07-19 | `650137f` | publish/release helpers (phase 1) |
| 07-20 | `ad4baec` | **deterministic Feature audit tiers** — policy, classifier, 5 reclassification boundaries, override flags removed |
| 07-21 | `d6948b0`, `7e3edda` | no persistent subagent memory for gate roles; §9 background completion collection |
| 07-21 | `4003967` | standard CI block, init/review hardening, quality-loop skill |
| 07-22 | `581fcb4` | **provenance & authority lattice** — D-IDs, typed clarify decisions, opportunities backlog |
| 07-23 | `facf494` | Feature decomposition pinned as fixed input of the D-ID entailment test |
| 07-24 | `ddf7cfa` | receipt-less global stations capped at 3 automatic rounds |
| 07-24 | `6bd8a63`, `df7843e`, `a3b6343`, `fb308c5` | publish/release mechanization phases 2–4 |
| 07-27 | `6d38178` | **continuity-v1** — immutable round archives, continuity packets, lineage IDs, REVERSAL, declared-coverage closure |
| 07-27 | `6725fa3`, `7cbf429`, `ca17927` | self-invalidating receipt and parser fixes |

### B. Reproducing the measurements

```bash
# commit set
git log --since="2026-07-17 15:00" --date=format-local:'%Y-%m-%d %H:%M' --pretty='%h|%ad|%s'

# station timings: extract "Launching skill: ms.*" tool_results with timestamps
#   from ~/.claude/projects/-workspace-*/*.jsonl, take the gap to the next station
#   launch in the same session (or the session's last event), discard gaps > 240 min.

# observed tier distribution
grep -ho 'effective_tier[^,]*' ~/.claude/projects/-workspace-*/*.jsonl | sort | uniq -c

# observed round numbers
grep -ho -- '--round [0-9]*' ~/.claude/projects/-workspace-*/*.jsonl | sort -V | uniq -c

# template self-trigger check
python3 - <<'PY'
import json, re
p = json.load(open('docs/templates/audit-tier-policy.json'))
txt = open('docs/templates/spec-template.md').read()
for r in p['artifact_scan_rules']:
    if 'spec' in r['phases'] and any(re.search(c, txt, re.I | re.M) for c in r['content_patterns']):
        print(r['tier'], r['id'])
PY
```

### C. Key file references

- `docs/templates/audit-tier-policy.json` — `t1_eligibility`, `artifact_scan_rules`, `tiers.T3`
- `scripts/specter/classify_audit_tier.py:285-339` — T1 predicate evaluation
- `scripts/specter/classify_audit_tier.py:438-473` — artifact content scan
- `scripts/specter/classify_audit_tier.py:380-399` — `GATE_MACHINERY_PATHS` (diff phase only)
- `docs/templates/scripts/specter-gate.sh:318-351` — coverage manifest key extraction
- `docs/templates/scripts/specter-gate.sh:1060-1130` — coverage set-equality enforcement
- `docs/templates/scripts/specter-gate.sh:1244-1248` — `UNVERIFIED` → WARN cap
- `docs/templates/spec-template.md:109-123` — `### Audit-Relevant Behavior` trigger block
- `.claude/skills/specter-agent-protocols/SKILL.md` §4, §6, §7, §8 — convergence, coverage schema, three-layer contract, tiers

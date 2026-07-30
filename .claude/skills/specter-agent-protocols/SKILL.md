---
name: specter-agent-protocols
description: Canonical external-agent protocols shared by the dual-agent SPECTER commands (/ms.verify, /ms.pre-verify, /ms.analyze, /ms.review, /ms.expand) under the verification-v2 contract — session-level preflight, single-agent degrade rule, report-write/salvage protocol plus the format-retry lane (a malformed report costs one same-agent retry, never a station round), the executable round budget (2 automatic rounds, gate-refused beyond, typed authorize-round decisions, the post-cap options), the v2 report schema (Contract/Mode/Scope/Input Digest binding, Checked/Not-checked honesty sections, 6-column findings with stable IDs and State), the risk-profile contract (ordinary vs high-risk from declared 8-signal tables and deterministic diff facts — never prose scanning), typed human-decision ledger events and the closed human-stop list, the auditor bias-prevention doctrine (context isolation, evidence-cited verdicts, grade-down-on-doubt, defect-claim symmetry, the 3-clause remedy contract), the three-layer station contract (deterministic structural checks → independent dual-agent semantics → mechanical verdict aggregation via specter-gate.sh, with typed degrade and mechanical receipt/ledger emission), the background-completion-collection rule (detached external-agent daemons never self-notify), and the provenance & authority lattice (§10 — which artifacts may add product behavior vs oblige, select, constrain, or merely reference). Commands reference this file instead of restating the mechanics; each command keeps only its own report paths and station-specific invariants inline.
---

# SPECTER External-Agent Protocols (verification-v2)

Single source of truth for the mechanics every Codex/Antigravity station shares.
A command that invokes an external agent applies these protocols and states
inline only what is specific to it (its report paths, single- vs dual-agent
station, and any degrade direction that differs). The normative design is
`docs/design/verification-v2.md`; the executable authority for signals, diff
facts, and budgets is `verification-v2.json` (synced) as read by
`specter-gate.sh`.

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
  station with the remaining agent only and write a **degrade placeholder
  report** at the missing agent's round-numbered report path — a minimal but
  VALID report, not free text, so Layer 3 can parse it:

  ```markdown
  # <Agent> <Station> (degraded)

  **Contract**: verification-v2
  **Mode**: <the station's normal Mode value>
  **Scope**: <Feature NNN | global>
  **Input Digest**: <the digest computed for this round>
  **Result**: WARN
  **Availability**: UNAVAILABLE (<reason>)
  ```

  Layer 3 then caps the station at `WARN` mechanically
  (`cap: single-agent-degrade`). A bare `<Agent>: UNAVAILABLE` line is NOT a
  valid placeholder — it carries no `**Result**:` field, so the gate grades it
  FAIL and an environment issue alone blocks the cycle.
- **Never** present a single-agent run as if both agents ran.
- **Never** block a cycle on an external-agent environment issue alone —
  degrade, record it, continue. Exception (§8): when the missing reviewer was
  needed for a triggered high-risk check, the degrade WARN requires an
  `ack-degrade` decision before advancement.
- A single-agent station (e.g. `/ms.expand`'s delta verify) has nothing to
  degrade to: stop and report the failure instead.
- Both agents down at a dual station leaves zero independent verifiers: the
  station **stops and reports** — it never runs host-only, because a host-only
  verdict is exactly the self-judgment this architecture removes.

## 3. Report-Write / Salvage / Format-Retry

Agents write their own report files (primary path) at **round-numbered paths**:
`<base>.r<N>.md` (e.g. `feature-006.codex-verify.r1.md`). Round files are never
overwritten — a new round is a new file, so history needs no archive machinery.
Every agent prompt also requires echoing the finished report verbatim between
`===REPORT BEGIN===` / `===REPORT END===` markers in the final message —
near-zero marginal cost, since a final message is emitted regardless.

After each agent run, check the file **deterministically**:

```bash
.specify/scripts/bash/specter-gate.sh validate-report <path> <station> [arg] --round <N>
```

If `valid` is false:

1. **Salvage**: rewrite the file from the `===REPORT BEGIN===`/`===REPORT END===`
   markers of the agent's final message; re-validate.
2. Still invalid → **format retry**: re-dispatch **that one agent** once, same
   round, with the validator's `errors` list prefixed to the prompt. Record the
   retry (`aggregate --format-retries`). A format problem costs one
   single-agent retry — never a station round, never the other agent's work.
3. Still invalid → this is an **agent-authored failure** (§7 typed degrade):
   leave the report as-is and let Layer 3 grade that input `FAIL`. Do NOT
   write a §2 placeholder for it — only a §1 preflight failure (the agent
   never ran) creates the environmental WARN cap.

## 4. Round Budget (executable, universal)

Unbounded re-review loops burn tokens without improving outcomes. The budget
is enforced by the gate, not by prose: `aggregate --round 3` (and above)
**exits FAIL before reading any report** unless a matching `authorize-round`
decision event is recorded.

- **Round 1**: full run over the whole scope.
- **Round 2** (only if Round 1 produced a `FAIL` finding): scoped to the
  failing findings plus the fix diffs — not a re-review of everything.
  Exception: `/ms.pre-verify`'s accepted verdict always comes from a
  full-scope round, because a map or ownership edit can ripple globally.
- **That is the entire automatic budget, every station, both risk profiles.**
- **Every round is fresh**: dispatch each round with `--fresh`. Prior-round
  findings travel as the prior round's report **file paths** (they are on disk,
  round-numbered), never via thread resume — a resumed reviewer carries the
  conversational pressure of the rounds in between into its verdict. On a
  re-round the reviewer re-checks prior blocking findings **by ID** and marks
  each `resolved` or `persists` in its Findings `State` column.
- **Changed evidence only**: a re-round may change a finding's grade only when
  the evidence changed — the fix diff or corrected artifact exists and is
  cited. Reconsidering identical evidence never upgrades a grade; it can still
  downgrade one (§5).
- **Repair contract (the fixer's obligation)**: reviewers report violations by
  rule class — every violator they can find, never just the first — and the
  same obligation binds whoever repairs a finding. Before claiming a blocking
  finding repaired, the fixer must (1) derive the **rule** the finding is an
  instance of, not the line it cites; (2) sweep for every other instance of
  that rule across the Feature's diff and the seams it touches, and repair
  those too; (3) state the sweep in the repair notes — what rule, what search,
  how many sites, all repaired. A repair claim with no sweep statement is
  incomplete, and the re-round reviewer is entitled to mark the finding
  `persists`. (2026-07-28: two full rounds were spent on correct-but-partial
  fixes — a guard added to two pages but not the selector offering them, and a
  scan widened on the backend but not in the page test.)
- **After the cap** an unresolved `FAIL` stays `FAIL` — it is never aged into
  a `WARN` by exhaustion. Present the human exactly these options (never "run
  one more identical round?"):
  1. **fix and restart** — repair the artifacts; a new input digest starts a
     fresh round 1;
  2. **amend the authority** — the PRD/Amendment path;
  3. **authorize one doctrine-dispute round** —
     `specter-gate.sh decide authorize-round <station> <scope> --round 3
     --reason "..."`; one fresh dual round scoped to the disputed doctrine
     question. It can raise scrutiny; it can never turn FAIL into WARN/PASS;
  4. **accept as WARN** — `decide accept-warn ...`, recorded residual;
  5. **stop** — `decide stop ...`.
- **Reversal doctrine** (prompt-level, no machinery): a reviewer lane that now
  rejects the state its own prior Required Fix prescribed must say so
  explicitly, cite the prior finding ID, and recommend escalation rather than
  another authoring guess. The 2-round budget guarantees oscillation reaches
  the human at round 3 by construction.

## 5. Auditor Bias-Prevention Doctrine

The value of a verification station is exactly the independence of its verdict.
These rules bind both sides: how the **driver composes** a reviewer prompt, and
how the **reviewer grades**.

- **Context isolation (driver-side)**: the reviewer receives only the artifacts
  the station defines — as file paths, per AGENTS.md §2 dispatch discipline.
  Never include the authoring reasoning, prior drafts, the conversation
  history, or the driver's own conclusions ("I believe this passes"). If such
  context leaks in anyway, the reviewer must state it is ignoring it and grade
  from the artifacts alone.
- **Evidence-cited verdicts (reviewer-side)**: a `PASS` on any checked item
  requires concrete evidence — a `file:line` citation or exact quoted text.
  "Looks fine" is not a verdict.
- **Honest gaps, reviewer-graded**: everything the reviewer did not or could
  not examine goes in the report's `**Not checked**:` line with the reason.
  The reviewer grades the impact of its own gaps: a gap that could hide a
  blocking defect makes the Result `WARN` or `FAIL` by the reviewer's own
  judgment — never silently folded into PASS, and never mechanically capped by
  the gate (the only mechanical cap is §2 availability).
- **Grade down on doubt, per item, no offsetting**: ambiguous evidence grades
  down (PASS→WARN, WARN→FAIL), never up. A strong PASS in one area never
  offsets a FAIL in another, and an issue the reviewer identified must appear
  in the report; talking itself out of a finding it already articulated is
  malpractice.
- **Absence of evidence is not evidence**: what was not observed belongs in
  `**Not checked**:`, never in the verdict, in either direction.
- **Defect-claim symmetry**: a suspected defect, debt, or drift is a
  hypothesis until the domain tool confirms it — never asserted as fact from
  pattern matching alone.
- **Remedy contract (3 clauses)**: every blocking finding's Required Fix
  states (1) the invariant that must be restored, (2) the minimum compliant
  repair, (3) what must NOT be added — no new scope. When several product
  interpretations remain valid, the fix escalates to the owner or the
  Amendment path instead of choosing one. Reviewers never supply unconditional
  replacement product text — an auditor who always writes the replacement
  becomes an unauthorized author.
- **No unilateral host downgrade (driver-side)**: the host/driver never
  re-grades an external verdict or finding — not by explaining it away as a
  false positive, not by relabeling a content finding as environmental. A
  disputed finding goes back to the same station as a scoped §4 re-round
  (fresh), where only the reviewing agent may revise its own grade against
  changed evidence. The station verdict is whatever §7's aggregation computes
  from the report files as written.

## 6. Report Schema (all dual-agent stations)

Report paths are round-numbered and station-fixed. The required form:

```markdown
# <Agent> <Station> Verification — <Scope> — Round <R>

**Contract**: verification-v2
**Mode**: <fixed station mode>
**Scope**: <Feature NNN | global>
**Input Digest**: <digest from specter-gate.sh digest — supplied in the prompt>
**Result**: PASS | WARN | FAIL

## Scope and evidence
**Checked**: <named check classes with citations or commands>
**Not checked**: <explicit exclusions with reasons, or the evidence basis for claiming none>

## Findings
| ID | Severity | State | Finding | Evidence | Required Fix |
| --- | --- | --- | --- | --- | --- |

## High-risk checks   (high-risk profile only — one row per TRIGGERED signal)
| Signal | Check | Result | Evidence |

## Verdict
<one short paragraph>
```

- `ID` is stable and unique within the lane (e.g. `CX-V-003`); `State` is
  `new | persists | resolved` (prior IDs carry forward on re-rounds).
- `Required Fix` follows the §5 3-clause remedy contract.
- An optional `**Availability**:` line (`UNAVAILABLE (<reason>)` |
  `RECUSED (<reason>)`) marks a §2 degrade placeholder.
- Validity (checked by `validate-report` and re-checked at L3): non-empty;
  exactly one `Result` valued PASS|WARN|FAIL; `Contract`/`Mode`/`Scope` match
  the station; `Input Digest` matches the current artifacts; non-empty
  `Checked`/`Not checked`; parseable 6-column Findings rows. Anything else is
  a §3 format defect, and after the format retry, a FAIL input — never
  repaired, reinterpreted, or hand-patched by the host (salvage from §3
  markers is the only sanctioned repair, and it copies the agent's own text).

Host-composed station summaries keep the five-section discipline — Claim /
Evidence / Baseline / Gaps / Residual-risk — because final verdicts
systematically under-report what a station actually observed. The Gaps section
aggregates the reviewers' `Not checked` lines; it must never evaporate into a
one-word verdict.

## 7. Three-Layer Station Contract

Every SPECTER verification station is composed of three layers. The division
exists to close the author-judge vector: the host — which authored or
assembled the artifacts under test — never grades them.

- **Layer 1 — deterministic structure** (`specter-gate.sh structural`):
  parseable facts only — required fields/sections, single commitment
  ownership, DAG acyclicity, placeholder scans, `CI passes green` suffixes,
  cited-ID cross-references, Verification-signals schema. Runs **before**
  agent dispatch: a structural FAIL stops the station without spending agents.
  L1 also computes the station's **input digest**
  (`specter-gate.sh digest <station> [arg]`) which the driver embeds in both
  prompts. L1 never claims semantic fidelity — that is L2's job.
- **Layer 2 — independent semantics** (external dual agents, always `--fresh`,
  §4): Codex and Antigravity each audit the same artifacts independently at
  **fixed effort** (`codex: xhigh`, `antigravity: medium` — effort is not
  risk-dependent) and each write their own §6 report.
- **Layer 3 — mechanical aggregation** (`specter-gate.sh aggregate <station>
  [arg] --ledger --round <N>`): computes the station verdict from the
  **fixed** round-numbered report set the station defines. The host invokes
  the station by name; it never selects, adds, or omits report files. Verdict
  = worst valid input (FAIL > WARN > PASS). The gate computes the risk
  profile (§8) and the round-budget check (§4) in the same call.

### Receipt and ledger (L3 output)

`aggregate` writes the station receipt to
`.specify/verification-v2/<station>-<scope>.json`: contract, station, scope,
round, risk profile + evidence, input digest, per-input
`{path, sha256, result, availability, graded, format_retries}`, verdict, cap,
required acks, verbatim `caught` rows, reasons. The receipt — not host
prose — is the station's outcome of record for the current round; history
lives in the append-only ledger. `--ledger` appends the
`.specify/specter-run.jsonl` line mechanically (verbatim `caught` rows copied
from the reports' Findings tables). The host never authors these fields at an
aggregated station.

**Composite stations.** A station whose final result folds in more than the
agent reports (`/ms.review`'s executable gates and Done Criteria) appends its
own ledger line **after** the mechanical one, embedding the receipt's verdict
verbatim as `agents_verdict`; it may only equal or worsen it.

### Typed degrade

Only a §1 preflight failure (after one retry) creates an environmental
degrade: the driver writes the §2 placeholder and L3 records the cap. An
agent-authored failure — malformed report after the §3 format retry, mid-run
crash, refusal — is a `FAIL` input, never relabeled as environmental.
`RECUSED` (implementer recusal, AGENTS.md §2) is handled identically to
`UNAVAILABLE`.

### Authoring stations are not verdicts

`/ms.featuremap` and `/ms.checklist`'s audit-and-write steps are **isolated
authoring stations**: a fresh subagent writes the artifact so the session's
authoring memory cannot leak into it. Their self-reported Result is a draft
grade, never authoritative — the authoritative verdict comes from the
L1+L2+L3 station that follows. Fix rounds after a FAIL re-dispatch a fresh
subagent scoped to the reported defects only (max 2 fix rounds before
escalating to the user), and a fix subagent must never delete or reword
commitments merely to make a structural check pass.

**Persistent subagent memory is forbidden for gate roles.** No authoring
station, and no subagent whose output feeds a gate verdict, may declare a
`memory` frontmatter field: a station that remembers prior rounds is no longer
fresh, and the PRD-blind checklist author's baseline value depends on never
having seen a Feature Map — in any session.

## 8. Risk Profile & Human Decisions

Two profiles: `ordinary` (default) and `high-risk`. The gate computes the
profile inside `aggregate` — there is no separate classifier process, receipt
handshake, or cross-phase floor. **Risk is declared or observed in files; it
is never inferred from spec/plan/tasks prose.**

- **Declared signals**: each Feature section carries a closed
  `### Verification signals` table (`| Signal | Value | Evidence |`, values
  `yes|no`, the 8 signals in `verification-v2.json`: authorization, secrets,
  data-migration, destructive-data, irreversible-operation, public-contract,
  financial-or-regulated, gate-or-policy-change). Authors record evidence;
  they never assign a profile. Any `yes` → high-risk at `verify`/`analyze`.
  A malformed table is a Layer-1 FAIL; a missing table runs the Feature
  high-risk until it gains one. A declared `no` the artifacts contradict is a
  blocking reviewer finding — the reviewer, not a regex, keeps declarations
  honest.
- **Observed diff facts** (`review` only): deterministic changed-file facts —
  migration dirs, auth/secret paths, CI/workflow files, gate machinery, and
  DDL/destructive statements in **added lines of the working diff** — per the
  config's path/content classes. Never one bundle attributed to every path;
  never prose scanning.
- **Manual raise**: `aggregate --raise-risk`, upward only, recorded. No
  lowering flag exists.

What high-risk changes — exhaustively: the applicable named checks
(`high_risk_checks` in the config) as a `## High-risk checks` report table and
as mandatory Done Criteria rows at `review`; review scope widens to affected
trust boundaries; the §2 degrade exception; and the named-class
acknowledgments below. Reviewer count, effort, budget, report schema:
identical in both profiles.

### Typed human decisions

All human decisions are ledger events written by
`specter-gate.sh decide <type> <station> <scope> [--round N] --reason "..."` —
actor-attributed, append-only. Types: `ack-migration`, `ack-destructive`,
`ack-irreversible`, `ack-gate-policy`, `ack-degrade`, `authorize-round`,
`accept-warn`, `stop`. A decision can never lower a verdict, effort, scope, or
reviewer count. Reviewers, agents, and the host cannot decide for the human.

### The closed human-stop list

1. `/ms.clarify` product decisions (by design);
2. both reviewers environmentally unavailable (station stops);
3. named-class acknowledgments when the class is present in the work:
   data-migration / destructive-data / irreversible-operation /
   gate-or-policy-change (the review receipt's `required_acks` records which
   are satisfied — advancement requires `acks_satisfied: true`);
4. a high-risk required check that could not be observed;
5. single-agent degrade when the missing reviewer was needed for a triggered
   high-risk check (`ack-degrade`);
6. unresolved FAIL or doctrine dispute at the §4 round cap.

An ordinary WARN — any profile, any station except the cases above — is
recorded in receipt and ledger and **advances**.

## 9. Background Completion Collection (no daemon self-notifies)

An external-agent background job — `codex`/`agy` run with `--background`, or any
codex-companion / Antigravity worker — runs as a **detached daemon** (`spawn`
with `detached: true` + `unref()`). A detached daemon **never pushes a completion
or death signal to the host**; the host learns the outcome only by pulling
(`status` / `result`). The only automatic wake the host ever receives is (a) a
harness-tracked `Bash(run_in_background: true)` finishing, or (b) a Claude Agent
subagent finishing. Every rule below routes external-agent completion through
one of those two channels. (2026-07-21 transcript audit: 5 of 7 background
dispatches in one workspace were never collected; the foreground-only control
session had zero incidents.)

- **Prefer the Agent-tool path (default).** Dispatch external agents via the
  Claude Agent tool (`codex:codex-rescue`, `antigravity:rescue` subagents)
  whenever the station allows it. The harness tracks the subagent and wakes the
  host automatically on completion.
- **Foreground when it fits the Bash ceiling.** A direct daemon call expected
  to finish within the Bash ceiling (max `600000` ms = 10 min) runs foreground
  with `--wait` and an explicit `timeout: 600000`. Raise the timeout; do not
  background prematurely.
- **Long jobs: wrap the wait in a harness background Bash.** When a direct daemon
  job can exceed 10 min, immediately after dispatch launch a thin waiter as
  `Bash(run_in_background: true)` — `codex status <job> --wait` /
  `agy status <id> --wait`, or a poll loop on the expected report file. The
  waiter's completion **is** the job's completion, so the harness wakes the host.
- **Detect death; never wait forever.** When the waiter returns on timeout, check
  health. A dead job — non-zero exit, 0% CPU, vanished output file, stale
  heartbeat — is failed immediately and degraded (§2). A live-but-slow job may
  be re-waited; a corpse is never re-waited.
- **Never promise auto-notification without a waiter.** "I'll tell you when it
  finishes" is true only when a harness-tracked waiter is actually in place.

## 10. Provenance & Authority Lattice

The refinement pipeline (PRD → Feature Map → spec → plan → tasks) legitimately
*adds information* at every stage. What it must never do is add *product scope*
without an authorized source. This section is the single definition of which
artifact may authorize what; every station cites this lattice instead of
restating its own source rule.

### The lattice

| Authority | Artifacts | What it can do |
| --- | --- | --- |
| **Add product behavior** | source PRD text (C-IDs); appended `## PRD Amendment N` sections | The only two sources of new product scope. Nothing else adds scope — not the map, not clarify, not a subagent's judgment. |
| **Reference implementation obligations** | D-ID rows (`## Implementation Obligations`, optional) | Record a deliverable an existing commitment needs, without adding observable product scope. D-IDs are references, never promises: a D-ID cannot own, satisfy, or substitute for a baseline C-ID, and a D-ID used to justify NEW observable behavior is an ordinary blocking finding routed to a PRD Amendment (2026-07-30 decision D3 — the formal entailment test is retired from the gate; the PRD-only rule carries the defense). |
| **Select within an envelope** | clarify **interpretation** records in `spec.md` | Choose among behaviors already inside a cited commitment's observable envelope. Never widen the envelope. |
| **Constrain implementation** | Constitution, product principles, `AGENTS.md` | Forbid or shape *how*; a governing rule never silently becomes scope. |
| **Reference only** | dependency Feature specs | Context for boundaries; never authority for behavior. |
| **No authority** | `docs/prd/opportunities.md` (unpromised-ideas backlog) | Preserved ideas the PRD never asked for. Promotion happens ONLY via a PRD Amendment (`/ms.expand`); no gate, checklist, spec prompt, or reviewer prompt loads this file. |

An addition carrying none of these origins is **untagged invention** — a
blocking finding at every station. Scope-expansion review remains a reviewer
duty: an item that introduces a new user journey or capability, stored data
category or retention period, permission or role, third-party integration,
notification channel, irreversible/destructive effect, billing behavior,
public API, or quantitative service promise is product scope and routes to a
PRD Amendment (or the opportunities backlog), regardless of what motivated it.

### Journey ownership doctrine

A commitment describing an end-to-end user journey is owned by the Feature
where the **whole observable journey first becomes verifiable** — never split
"half" across an engine Feature and a screen Feature. Earlier slices carry
enabling obligations toward that journey; the owning Feature's done criteria
prove the journey end-to-end and name the enabling Features.

### Typed clarify decisions

Every `/ms.clarify` resolution is one of exactly two types:

- **interpretation** — selects among behaviors already inside a cited C-ID's
  (or D-ID's) observable envelope. Recorded in `spec.md` with provenance: the
  cited ID, the exact question and answer, and whether the user answered or
  evidence auto-resolved it.
- **scope-addition** — would widen an envelope or add product scope. Clarify
  REFUSES to record it as a decision: it routes to a PRD Amendment
  (`/ms.expand`) or, if not adopted now, to the opportunities backlog. An
  agent-side evidence auto-resolution can only ever produce an
  `interpretation`, never a scope-addition.

A `Source: clarify` label without the cited ID and recorded question/answer is
not provenance — downstream auditors treat it as untagged.

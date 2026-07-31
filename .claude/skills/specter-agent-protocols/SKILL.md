---
name: specter-agent-protocols
description: Lean, state-free protocol for SPECTER's independent verification stations.
---

# SPECTER External-Agent Protocols

This skill is the shared contract for `/ms.pre-verify`, `/ms.verify`,
`/ms.analyze`, and `/ms.review`. Commands define their scope and fixed report
paths; this file defines only reusable mechanics.

## 1. Independent review

- Use two fresh, isolated reviewers. Give them file paths and the station rubric,
  never the host's conclusion or prior reviewer reasoning.
- The host authors and implements. Reviewers inspect and report; they do not
  silently rewrite the artifact they grade.
- A reviewer that implemented the Feature is recused from that Feature's review.
- Check availability once per session. Retry an unavailable reviewer once.

## 2. State-free report contract

Before dispatch, run:

```bash
.specify/scripts/bash/specter-gate.sh hash <station> <scope>
```

Each reviewer writes only its station-fixed path and includes exactly one of
each field:

```markdown
**Mode**: <station-defined value>
**Scope**: <scope>
**Input SHA256**: <current bundle hash>
**Result**: PASS | WARN | FAIL
```

A report must cite concrete file/line, command, or diff evidence. Unchecked
items are `UNVERIFIED`, never PASS. Suspected defects without evidence are
also `UNVERIFIED`, not asserted facts.

After both attempts, run the state-free reducer:

```bash
.specify/scripts/bash/specter-gate.sh reduce <station> <scope>
```

The reducer reads the two fixed paths, requires one valid Result and the current
hash, and returns the worst verdict. It writes no receipt, round state, ledger,
profile, or approval token.

Availability is mechanical:

- both available: worst of FAIL > WARN > PASS
- one unavailable: the remaining FAIL stays FAIL; otherwise result is WARN
- both unavailable: FAIL

After the retry, the host records an unavailable lane at that lane's fixed path
using the normal Mode, Scope, and current Input SHA256, `Result: WARN`, and
`Availability: UNAVAILABLE (<reason>)`. This is mechanical absence evidence,
not a substitute semantic review. A missing or malformed lane fails reduction.

## 3. Rerun policy

There is one automatic rerun, and only after the finding caused an artifact or
code change. The rerun is scoped to the finding and changed diff. Do not rerun
unchanged inputs, add review rounds, or ask the human to acknowledge WARN/FAIL.
PASS and WARN return to the conductor; FAIL terminates the command.

## 4. Progressive authority

Artifacts refine one another instead of competing as equally literal ledgers:

1. PRD and Amendments own product intent and explicit boundaries.
2. Feature Map owns decomposition, ownership, ordering, and dependency DAG.
3. spec owns observable Feature behavior.
4. plan owns technical design.
5. tasks own execution partition.
6. code and executable tests own observed implementation reality.

A downstream detail is valid when it refines an upstream envelope or corrects
reality. It does not need literal wording in the PRD. A new actor or journey,
external integration, retained-data category, permission boundary, paid
capability, or conflict with an explicit boundary is a boundary change and
routes to `/ms.clarify` with a proposed upstream patch.

Legacy Verification-signal tables, D-IDs, receipts, round reports, and risk
profiles have no authority. Ignore them; do not require or regenerate them.

## 5. Report discipline

Keep reports compact:

- scope and evidence checked
- findings with severity, evidence, and required fix
- gaps / residual risk
- exactly one Result

Never erase a real finding in the summary, improve a reviewer verdict by host
judgment, or turn a gate result into a human approval stop.

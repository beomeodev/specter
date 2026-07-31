# Refinement-First Workflow

Status: canonical design
Effective: 2026-07-31

## Problem

A PRD is intentionally the workflow's most abstract artifact. A Feature becomes
more concrete through Feature Map, spec, plan, tasks, code, and tests. Treating
every earlier sentence as a literal ceiling makes later evidence wait on
fingerprints, receipts, and human acknowledgments even when no product boundary
changed. That preserves a ledger but slows delivery and rewards abstraction over
reality.

## Authority by domain

| Artifact | Owns |
| --- | --- |
| PRD + Amendments | product intent and explicit boundaries |
| Feature Map | mutable decomposition, ownership, order, dependency DAG |
| spec | observable Feature behavior |
| plan | technical design |
| tasks | execution partition |
| code + tests | observed implementation reality |

Later artifacts may add detail when it is a refinement inside the upstream
envelope or a correction forced by repository reality. Missing literal PRD
wording is not, by itself, drift.

The Feature Map is a derived index, not an append-only product ledger. It may
correct existing Feature sections, ownership, and DAG edges. A product boundary
change still requires an appended PRD Amendment.

## Boundary test

Route to `/ms.clarify` when a proposed change introduces or changes any of:

- actor or end-to-end journey
- external integration
- retained-data category
- permission boundary
- paid capability
- explicit exclusion, cost, or policy boundary

Clarify presents the evidence and proposed upstream patch. It is the only
mandatory human stop in the per-Feature cycle, even when all ordinary ambiguity
was evidence-resolved.

## Lean verification

Semantic stations use two fresh independent reviewers and fixed report paths.
Each report contains the current input bundle SHA256 and exactly one
PASS/WARN/FAIL. A state-free reducer validates the reports and returns worst-of.

- one unavailable reviewer + non-FAIL peer: WARN
- one unavailable reviewer + FAIL peer: FAIL
- both unavailable: FAIL
- one automatic rerun, only after inputs changed
- no receipt, round state, profile, signal table, or acknowledgment

PASS/WARN advances. FAIL terminates and reports evidence. A gate failure is an
end state, not a request for human approval.

## Execution ownership

`/ms.implement` runs targeted RED/GREEN checks. `/ms.review` runs full
lint/type/test/build, Done Criteria through a real entrypoint, applicable E2E,
changed-file safety checks, and dual code review once. `/ms.fin` does not rerun
tests when code is unchanged; changed code returns to review.

Legacy Verification-v2 files and metadata are ignored. In-flight work receives
one lean recheck at its current station.

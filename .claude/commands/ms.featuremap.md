---
description: "Build or refresh the derived PRD Feature Map"
argument-hint: "[@docs/prd/PRD.md ...]"
---

# /ms.featuremap

Create or refresh `docs/prd/feature-map.md` from the supplied PRDs. If no paths
are supplied, discover source PRDs under `docs/prd/`, excluding Feature Maps,
checklists, opportunities, and generated review reports. If no source remains,
return FAIL with the missing-input reason; do not pause for a path.

The Feature Map is a mutable derived index, not product authority. PRDs and
appended Amendments own intent and explicit boundaries. The map owns Feature
decomposition, commitment ownership, order, and dependency DAG. Correct existing
Feature sections when ownership or sequencing changes. A product boundary change
requires a PRD Amendment; an indexing or decomposition correction does not.

Read the full PRD set once. Reuse that copy. Preserve useful stable Feature
numbers where possible, but correctness beats append-only history.

Write:

- PRD sources and compact commitment index with source citations
- one owning Feature for each commitment
- dependency DAG with no cycles
- ordered `## Feature NNN: <name>` sections
- Source PRDs, In scope, Explicitly out of scope, Key decisions, Dependencies,
  Done criteria
- the final Feature owns an observable end-to-end product journey

Done criteria must be behaviorally testable and end with `CI passes green`.
Do not add Verification signals, risk profiles, D-IDs, receipts, fingerprints,
or implementation details better decided by spec/plan.

Self-check structure and coverage. Return PASS, WARN, or FAIL. WARN does not ask
for acknowledgment. FAIL terminates with concrete fixes.

Next: `/ms.featuremap-checklist`.

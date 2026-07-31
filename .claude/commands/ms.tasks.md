---
description: "Partition the plan into executable, test-first tasks"
argument-hint: ""
---

# /ms.tasks

Delegate initial task generation to `/speckit-tasks`, then reconcile it with
the current plan and repository.

Tasks own execution partition, not product scope. Every task must identify files,
dependencies, and its smallest verification command. Order each behavior as:

1. RED: add or identify a failing observable test
2. GREEN: implement the minimum behavior
3. REFACTOR: optional cleanup while the targeted check stays green

Cover every Done criterion, planned component, interface, migration/recovery
step, state invariant, and final end-to-end scenario. Mark safe parallel work
only when files and dependencies do not overlap. Keep full lint/type/test/build
and real-entrypoint execution out of every task; `/ms.review` owns those once.

Compare tasks to plan and repository reality. Correct partitioning and paths
without asking approval. A genuine product boundary change routes to clarify;
other omissions return FAIL with exact fixes.

Do not add review rounds, receipts, lineage manifests, fingerprints, or manual
gates. PASS/WARN continues to `/ms.analyze`.

Next: `/ms.analyze`.

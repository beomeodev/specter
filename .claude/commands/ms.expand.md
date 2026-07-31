---
description: "Apply a PRD Amendment and refresh the derived Feature Map"
argument-hint: "[@docs/prd/PRD.md]"
---

# /ms.expand

Consume an appended `## PRD Amendment N` from a source PRD. The Amendment is
product authority. Refuse edits that silently rewrite existing PRD history, but
do not require the Feature Map itself to be append-only.

Update `docs/prd/feature-map.md` as a mutable derived index:

- add new commitments and Features when needed
- correct existing ownership, DAG edges, ordering, and Feature sections
- preserve stable Feature numbers where practical
- keep explicit boundaries and source citations
- ensure the final Feature still owns the end-to-end journey

A decomposition correction may edit existing Feature sections. A new product
boundary must appear in the Amendment first. Ignore legacy D-IDs, Verification
signals, fingerprints, profiles, and receipts.

Run `/ms.featuremap-checklist` and `/ms.pre-verify` over the full updated
scope, not a delta-only receipt. PASS/WARN continues; FAIL terminates. No human
acknowledgment is available.

Report affected Features and hand the first incomplete one to
`/ms.specter <NNN>`.

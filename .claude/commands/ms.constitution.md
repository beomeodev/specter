---
description: "Establish durable project-wide Constitution constraints"
argument-hint: ""
---

# /ms.constitution

Update `.specify/memory/constitution.md` only from durable project-wide rules
visible across the PRD set and verified Feature Map.

Before Section IX exists, verify the global checklist directly: it must be Mode
global, PASS/WARN, and its Feature Map SHA256 must match. Missing or stale
evidence is FAIL. Do not run the full global gate until after the Section IX
baseline is written, because that gate intentionally requires the baseline.

Promote only constraints that should bind every later Feature: platform limits,
mandatory security/privacy rules, repository-wide architecture, shared naming,
or global compliance. Do not promote Feature-local endpoints, schemas, UI copy,
migration details, or speculative design.

Preserve the exact heading:

`## IX. Project-Specific Constraints`

If no durable project-specific constraint exists, say so explicitly beneath the
heading; do not leave the template placeholder. Cite sources by file/heading.
Constitution references elsewhere use section names, except the literal Section
IX structural contract.

This command is an explicit baseline operation outside the per-Feature conductor.
It never pauses for approval. A substantive conflict returns FAIL with the source
evidence; PASS/WARN completes.

Next: `/ms.specter <NNN>`.

---
description: "Automate one-time PRD setup through the first Feature handoff"
argument-hint: "[@docs/prd/PRD.md ...]"
---

# /ms.pre-specter

Run this sequence:

`featuremap → featuremap-checklist → pre-verify → constitution`

Probe `specter-gate.sh version` once at start. It must report
`lean-verification-v1`; partial sync is FAIL.

Resolve source PRDs once and pass the same set to the first two commands. Missing
inputs return FAIL. Existing Feature Maps are refreshed as mutable derived
indexes; do not ask permission to overwrite or correct them.

For every step:

- PASS: continue
- WARN: record the warning in the final summary and continue
- FAIL or command error: stop and report the exact cause

There are no human approval or acknowledgment stops in this conductor. It does
not resume from old receipts, round files, Verification-v2 state, or the legacy
run ledger; those files are ignored.

On success, report artifacts and hand the first incomplete Feature to
`/ms.specter <NNN>`.

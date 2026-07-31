---
description: "Drive one Feature from checklist through final review"
argument-hint: "<NNN> [@docs/prd/feature-map.md]"
---

# /ms.specter

Run one Feature through:

`checklist → verify → specify → clarify → plan → tasks → analyze → implement → review`

Probe `specter-gate.sh version` once at start; require
`lean-verification-v1`. Ignore legacy Verification-v2 receipts, rounds,
profiles, signal tables, D-IDs, and run-ledger state.

Verdict control is mechanical:

- PASS: advance
- WARN: retain the warning for the final summary and advance
- FAIL/MISSING/command error: terminate and report the evidence

`/ms.clarify` is the only mandatory human stop. Always hand control to the
human there and resume only after the answer or explicit continuation. No other
step may ask for approval, confirmation, acknowledgment, reviewer arbitration,
migration acceptance, or delegation permission.

Invocation authorizes the repository-local implementation actions described in
`/ms.implement`, even when 3+ files are involved. It does not authorize
production/staging migrations, environment or secret mutation, external
destructive operations, git commit/push/merge/release, or force operations.

Old state files are neither deleted nor trusted. Determine current position from
actual artifacts and the lean gate. If a station was in flight during migration,
run that station once under the lean contract.

On completion report Feature, step verdicts, warnings, changed files, executable
checks, review reports, and next command `/ms.fin`.

---
description: "Drive one Feature from checklist through final review"
argument-hint: "<NNN> [@docs/prd/feature-map.md]"
---

# /ms.specter

Run one Feature through:

`checklist → verify → specify → clarify → plan → tasks → analyze → implement → review`

Probe `specter-gate.sh version` once at start; require
`lean-verification-v1`. If the probe fails or the installed gate reports a
lower `rev` than `docs/templates/scripts/specter-gate.sh version`, copy the
template over `.specify/scripts/bash/specter-gate.sh` and re-probe once;
refuse only if it still fails. Ignore legacy Verification-v2 receipts, rounds,
profiles, signal tables, D-IDs, and run-ledger state.

Verdict control is mechanical:

- PASS: advance
- WARN: retain the warning for the final summary and advance
- FAIL/MISSING/command error: terminate and report the evidence

`/ms.clarify` is the only mandatory human stop. Always hand control to the
human there and resume only after the answer or explicit continuation. No other
step may ask for approval, confirmation, acknowledgment, reviewer arbitration,
migration acceptance, or delegation permission.

Advance between stations in the same turn. Never pause to summarize,
checkpoint, or report intermediate progress, and never end a turn with a
status report while stations remain — progress belongs in artifacts, the
summary belongs at completion. Pausing anywhere except clarify, a FAIL, or a
genuine blocker is a contract violation, not caution.

Invocation authorizes the repository-local implementation actions described in
`/ms.implement`, even when 3+ files are involved. It does not authorize
production/staging migrations, environment or secret mutation, external
destructive operations, git commit/push/merge/release, or force operations.

Old state files are neither deleted nor trusted. Determine current position from
actual artifacts and the lean gate. If a station was in flight during migration,
run that station once under the lean contract.

On completion report Feature, step verdicts, warnings, changed files, executable
checks, review reports, and next command `/ms.fin`.

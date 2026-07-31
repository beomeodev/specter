---
description: "Build a concise readiness checklist for one Feature"
argument-hint: "<NNN> [@docs/prd/feature-map.md]"
---

# /ms.checklist

Resolve Feature NNN from the current Feature Map and write
`docs/prd/checklists/feature-NNN.checklist.md`.

Prerequisites are a current global checklist (Mode global, PASS/WARN, matching
Feature Map SHA256) and established Constitution Section IX. Run
`specter-gate.sh` for the global mechanical check. Missing/stale prerequisites
are FAIL.

The host authors this checklist from the Feature section, its cited PRD envelope,
and Constitution. Include:

```markdown
**Mode**: per-feature
**Feature**: Feature NNN
**Feature Map**: docs/prd/feature-map.md
**Feature Map SHA256**: <current sha256>
**Result**: PASS | WARN | FAIL
```

Check scope, exclusions, dependencies, observable Done criteria, acceptance/NFR
coverage, and boundary questions that must reach clarify. Downstream refinements
are allowed; do not demand literal PRD wording, D-IDs, Verification signals, or
fingerprints.

PASS/WARN continues to `/ms.verify NNN`. FAIL terminates with concrete defects.
There is no approval stop.

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
**Feature Map SHA256**: <scope_sha256 from the command below>
**Result**: PASS | WARN | FAIL
```

Take the binding from `specter-gate.sh map-sha NNN` and record its
`scope_sha256`, never a digest of the whole file. The binding covers this
Feature's own section plus the map's shared content, so another Feature's
refinement no longer stales this checklist while a change to this Feature's
section, to the commitment index, or to the set of Features still does. A
whole-file digest is still accepted from checklists written before scoping,
but it re-stales on every unrelated edit — regenerate rather than keep it.

Check scope, exclusions, dependencies, observable Done criteria, acceptance/NFR
coverage, and boundary questions that must reach clarify. Downstream refinements
are allowed; do not demand literal PRD wording, D-IDs, Verification signals, or
fingerprints.

PASS/WARN continues to `/ms.verify NNN`. FAIL terminates with concrete defects.
There is no approval stop.

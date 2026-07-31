---
description: "Independently verify one Feature's readiness checklist"
argument-hint: "<NNN>"
---

# /ms.verify

Run the per-Feature semantic readiness gate.

Prerequisites:

- current Feature Map and global checklist
- `docs/prd/checklists/feature-NNN.checklist.md`
- established Constitution Section IX

Run `specter-gate.sh hash verify NNN`. Dispatch fresh isolated Codex and
Antigravity reviewers in parallel. Give each the Feature section, cited PRD
sources, global checklist, and per-Feature checklist. Check scope coverage,
exclusions, dependency ownership, testable Done criteria, and unsupported
boundary additions.

Write fixed reports:

- `docs/prd/checklists/feature-NNN.codex-verify.md`
- `docs/prd/checklists/feature-NNN.antigravity-verify.md`

Each includes Mode, `Scope: NNN`, current Input SHA256, exactly one Result,
findings, evidence, gaps, and residual risk. Then run:

```bash
.specify/scripts/bash/specter-gate.sh reduce verify NNN
```

Follow the shared availability and one-rerun rules. PASS/WARN returns immediately;
FAIL terminates. Never ask the user to acknowledge a warning or reviewer result.

Next: `/ms.specify NNN`.

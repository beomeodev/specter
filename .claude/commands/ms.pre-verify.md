---
description: "Run the full-scope dual audit of the PRD Feature Map"
argument-hint: ""
---

# /ms.pre-verify

Audit the complete current Feature Map against all source PRDs and
`docs/prd/codex/checklist.md`. This is the global semantic gate.

Prerequisites:

- `docs/prd/feature-map.md`
- at least one source PRD
- `docs/prd/codex/checklist.md`
- installed lean gate whose `version` reports `lean-verification-v1`

Missing or partial prerequisites are FAIL, not questions.

Run `specter-gate.sh hash pre-verify global`. Dispatch fresh isolated Codex and
Antigravity reviewers in parallel. They independently check complete commitment
coverage, ownership uniqueness, DAG validity, explicit exclusions, observable
Done criteria, and final end-to-end journey. They write:

- `docs/prd/feature-map.codex-verify.md`
- `docs/prd/feature-map.antigravity-verify.md`

Each report follows `specter-agent-protocols`, uses scope `global`, and embeds
the returned Input SHA256. Then run:

```bash
.specify/scripts/bash/specter-gate.sh reduce pre-verify global
```

One automatic scoped rerun is allowed only after the Feature Map changes.
Finally write `docs/prd/feature-map.checklist.md` with:

```markdown
**Mode**: global
**Feature Map SHA256**: <current map sha256>
**Result**: PASS | WARN | FAIL
```

Include compact findings and both report paths. The Result must equal the
reducer verdict. PASS/WARN returns immediately; FAIL terminates. No acknowledgment
or override exists.

Next: `/ms.constitution`.

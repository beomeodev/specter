---
description: "Create a GEARS Feature spec from a verified Feature Map section"
argument-hint: "<NNN> [@docs/prd/feature-map.md]"
---

# /ms.specify

Accept only a Feature number or an attached Feature Map section. Refuse freeform
feature requests and existing spec text as authority.

Run:

```bash
.specify/scripts/bash/specter-gate.sh NNN
```

Only PASS/WARN may continue. MISSING/FAIL terminates with the prerequisite command
to run; it never asks for confirmation.

Extract exactly Feature NNN plus its PRD citations and dependency context. Create
a temporary per-Feature gate token for the direct-call hook, delegate generation
to `/speckit-specify`, then remove the token even on failure.

```bash
mkdir -p .specify
GATE_TOKEN=".specify/.ms-gate-pass-NNN"
touch "$GATE_TOKEN"
trap 'rm -f "$GATE_TOKEN"' EXIT
# Invoke /speckit-specify with the extracted Feature NNN section.
rm -f "$GATE_TOKEN"
trap - EXIT
```

The resulting `specs/NNN-*/spec.md`:

- uses the installed GEARS template
- defines observable behavior within the PRD boundary
- may add legitimate refinement needed to make the Feature testable
- records unresolved product choices for `/ms.clarify`
- does not invent a new actor/journey, integration, retained-data category,
  permission boundary, paid capability, or contradict an explicit exclusion

Spec detail is downstream authority for Feature behavior. Do not block it merely
because the abstract PRD lacks the same wording. Boundary changes route to
`/ms.clarify`.

Validate the created spec exists and its Feature identity matches NNN. Return
PASS/WARN or FAIL. No human stop occurs here.

Next: `/ms.clarify`.

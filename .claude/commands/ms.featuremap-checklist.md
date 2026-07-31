---
description: "Create an independent PRD-only checklist for Feature Map review"
argument-hint: "[@docs/prd/PRD.md ...]"
---

# /ms.featuremap-checklist

Use one fresh Codex reviewer to read only the source PRDs and write
`docs/prd/codex/checklist.md`. This is a compact review checklist, not a Feature
Map draft and not a verdict on the current map.

Resolve PRDs exactly as `/ms.featuremap` does. Missing input is FAIL. Pass file
paths, not pasted content, and isolate the reviewer from the host's reasoning.

The checklist covers:

- every product behavior and acceptance criterion
- actors, journeys, exclusions, NFRs, data, security, migrations, and integrations
- likely ownership conflicts and ambiguous boundaries
- observable end-to-end coverage

Each row cites its PRD evidence. Do not invent requirements or inspect the
generated Feature Map. Write `**Mode**: prd-only`.

Check the file exists and is non-empty. Retry the reviewer once on a write or
availability failure. If still unavailable, return FAIL; there is no human
approval fallback.

Next: `/ms.pre-verify`.

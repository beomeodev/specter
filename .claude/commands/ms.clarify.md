---
description: "Resolve Feature ambiguity at the cycle's only mandatory human stop"
argument-hint: ""
---

# /ms.clarify

Delegate clarification analysis to `/speckit-clarify`, but apply this SPECTER
contract.

Read the current spec, its Feature Map section, cited PRDs, Constitution, and
relevant repository evidence once. Classify each uncertainty:

- `refinement`: a more concrete choice inside the upstream envelope
- `reality-correction`: repository facts invalidate an assumed detail
- `boundary-change`: new actor/journey, external integration, retained-data
  category, permission boundary, paid capability, or explicit boundary change
- `conflict`: two authorities cannot both be satisfied

Resolve refinement and reality-correction from strong evidence when there is one,
and show those resolutions in the handoff. Ask only choices that materially
change product behavior or lack evidence. For boundary-change/conflict, propose
the exact PRD Amendment and Feature Map correction; do not apply it before the
user answers.

This is the per-Feature cycle's one mandatory human stop. Always hand control to
the user once, even if evidence resolved every candidate question. If there are
no questions, report that fact and wait for the user's continuation.

After the answer, update the spec and any explicitly approved upstream patch.
Record separately:

- evidence-resolved items
- user-decided items
- Amendment or Feature Map corrections applied
- residual unknowns

No other command may reinterpret this handoff as approval of gates, warnings,
migrations, reviewer results, or publishing.

Next: `/ms.plan`.

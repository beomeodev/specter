---
description: "Dual-review spec, plan, and tasks before implementation"
argument-hint: ""
---

# /ms.analyze

Resolve Feature NNN and its `specs/NNN-*` directory. Require spec.md, plan.md,
tasks.md, current Feature Map, and Constitution. Missing input is FAIL.

Run `specter-gate.sh hash analyze NNN`. Dispatch fresh isolated Codex and
Antigravity reviewers in parallel. They check:

- spec remains inside product boundaries
- plan concretely realizes spec against repository reality
- tasks cover plan and Done criteria in executable order
- dependencies, interfaces, paths, migration/recovery, security, state
  invariants, and tests are internally consistent
- downstream refinements are supported; abstract upstream wording is not used
  to suppress legitimate detail

Write:

- `specs/NNN-*/analyze.codex.md`
- `specs/NNN-*/analyze.antigravity.md`

Grade design consistency, not future runtime. A finding whose only remaining
closure is code, tests, or runtime behavior that `/ms.implement` has not yet
produced is recorded as `UNVERIFIED — carried to review` and grades at worst
WARN. FAIL is reserved for spec, plan, or tasks that are themselves
contradictory, incomplete, or outside product boundaries. `/ms.review` must
grade every carried finding against the implemented code.

Each follows the shared state-free report contract. Run
`specter-gate.sh reduce analyze NNN`. One scoped rerun is allowed only after
the artifacts change; the gate refuses further rounds without a recorded
owner override.

PASS/WARN continues immediately. FAIL terminates with findings. Do not request
acknowledgment, confirmation, delegation permission, or a review-round decision.

Next: `/ms.implement`.

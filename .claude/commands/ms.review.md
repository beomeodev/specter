---
description: "Run the Feature's final executable and independent code review"
argument-hint: ""
---

# /ms.review

This command owns final verification once. Resolve Feature NNN, changed files,
spec, plan, tasks, implementation notes, and Done criteria.

## Executable gate

Run the repository's real commands once:

- lint
- typecheck
- full relevant test suite
- build
- Done Criteria through the real public entrypoint
- Phase end-to-end journey once when applicable
- TAG integrity and configured security tooling

Do not claim a check passed unless it ran. Missing tooling is UNVERIFIED and caps
the result at WARN unless it prevents a Done criterion, in which case FAIL.

For every changed-file safety class, run the applicable evidence check regardless
of profile:

- migration: dry-run plus rollback or forward-recovery evidence
- destructive operation: bounded target and recovery evidence
- authorization: actor/permission tests
- secrets: leakage and invalid-credential tests
- public API/schema: compatibility or intentional-break evidence
- gate/hook/policy: seeded-failure regression

There are no risk profiles and no migration acknowledgment. Unsafe or missing
required evidence is FAIL.

## Independent review

Run `specter-gate.sh hash review NNN`, then dispatch fresh isolated Codex and
Antigravity code reviewers once. The implementation author is recused. Review
correctness, security, maintainability, test quality, plan deviations, boundary
seams, and surgical scope.

Write:

- `docs/review/NNN.codex-review.md`
- `docs/review/NNN.antigravity-review.md`

Embed the current Input SHA256 and run
`specter-gate.sh reduce review NNN`. A single scoped rerun is allowed only if
a finding caused code to change; after any code change rerun the affected
executable checks too.

Final Result is the worse of executable gates and the reducer. PASS/WARN closes
the stop-gate phase and continues. FAIL records honest evidence and terminates.
Never ask for acknowledgment or approval.

Next: `/ms.fin`.

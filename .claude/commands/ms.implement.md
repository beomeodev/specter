---
description: "Implement the analyzed Feature with targeted test-first checks"
argument-hint: ""
---

# /ms.implement

Require a PASS/WARN `/ms.analyze` result for the current artifacts. If it is
missing or stale, return FAIL; do not ask to bypass it.

The host implements by default. External implementation delegation is used only
when the user already approved it for this Feature; otherwise do not ask
mid-cycle.

Execute tasks in dependency order:

1. run the task's smallest observable check and confirm RED when practical
2. implement the minimum change
3. rerun that targeted check to GREEN
4. refactor only what this change made necessary
5. mark the task complete with the command and observed result

Treat code and executable tests as authority for observed reality. When reality
forces a plan deviation, record the reason in
`specs/NNN-*/implementation-notes.md`; update plan/tasks if useful. Route only
product boundary changes or conflicts back to clarify.

Do not run the full suite, full build, repeated entrypoint smoke, dual code
review, or per-phase audit here. `/ms.review` owns them once. Do not create
receipts, round files, coverage manifests, or approval stops. Do not pause
between tasks to checkpoint progress or ask whether to continue — narrate
into `implementation-notes.md` and keep executing until the task list is done
or an actual blocker stops you.

Invocation of `/ms.specter` authorizes repository-local changes required by
the clarified Feature, including 3+ files, required creates/moves/deletes,
plan-recorded dependency changes, disposable local test migrations, and bounded
review boot. It does not authorize production/staging migrations, secrets/env
mutation, external destructive operations, or git publishing.

Return PASS when all tasks and targeted checks complete, WARN for explicitly
reported residual non-blockers, or FAIL for an actual blocker.

Next: `/ms.review`.

---
description: "Publish reviewed changes: docs → commit → push → draft PR"
argument-hint: "[--no-ci]"
---

# /ms.fin

Invocation authorizes the git actions defined here. It does not authorize merge,
release, force-push, production mutations, or unrelated changes.

## 1. Sync living docs

Run `/ms.up-docs --docs=dev`. Documentation-only edits do not invalidate code
review.

## 2. Require current review evidence

Install and probe the deterministic helper:

```bash
install -D -m 0755 docs/templates/scripts/specter-publish.sh \
  .specify/scripts/bash/specter-publish.sh
.specify/scripts/bash/specter-publish.sh version
.specify/scripts/bash/specter-publish.sh ci-mode
```

Use its JSON verbatim.

- If code is unchanged since a clean `/ms.review`, do not rerun tests, lint,
  typecheck, build, Done Criteria, or semantic review.
- If code changed, the cache is missing/legacy, review-state exists, or the
  comparison cannot be proved, stop and run `/ms.review`. Do not substitute a
  smaller CI rerun here. After review, rerun `/ms.fin`.
- `--no-ci` is an explicit WIP/backup publish. Create
  `.specify/.ms-wip-publish`, report the skipped review loudly, and allow
  publishing; `/ms.merglease` must refuse until fresh review clears it.

Universal migration/auth/destructive/secret/public-contract/gate evidence belongs
to `/ms.review`; do not repeat its diff audit here.

## 3. Publish

Delegate one fresh Antigravity run to:

1. inspect the outgoing diff and build an explicit staging list
2. split commits by logical concern (feature + tests + docs together)
3. never use `git add .`, force push, destructive reset, or bypass hooks
4. push the current feature branch to its configured remote
5. create or update a draft PR with summary, tests from the current review, and
   residual warnings
6. stop on any commit, push, hook, or PR failure

The host does not poll CI or repeat semantic review.

## 4. Verify end state

Run `specter-publish.sh verify-endstate`. Report the observed tree, upstream,
push, and PR URL/status. A delegated success message is not evidence. If any
required end-state check is false or unknown, report failure.

Next: `/ms.merglease` after the draft PR is ready.

---
description: "Merge open PR → release: gh pr merge → master pull → tag + GitHub Release. (Delegated to Antigravity)"
argument-hint: "[version] [--no-release] [--confirm] [--cleanup]"
---

# /ms.merglease - Merge & Release (Delegated)

Delegate the PR merging, master pull, automatic semver computation, tagging, and GitHub Release
creation to the **Google Antigravity CLI**.

## Automation Principles

- **Semver is automatic — no version or merge-strategy questions.** Antigravity computes the
  bump from conventional commits since the last tag and always merges with a merge commit. An
  explicit `[version]` argument overrides the computed bump; `--confirm` restores interactive
  confirmation for both the version and the merge. Without `--confirm`, the run is non-interactive.
- **Local CI is authoritative; GitHub CI is advisory.** `/ms.review`/`/ms.fin` already gated this
  branch. A GitHub CI failure caused by billing/quota/infra (not a real test/lint/type/build
  failure) must not block a release — but any real failure still does.
- **No CI polling in the host session.** Antigravity's single delegated run waits for CI itself as
  part of its own preflight; the host must not loop `gh pr checks` / `gh run watch` or schedule
  wakeups to check on it.
- **Approval posture (explicit exemption).** AGENTS.md §7's "ask before merging or creating
  releases" is satisfied by the user invoking `/ms.merglease` itself — the invocation *is* the
  approval, exactly as `/ms.fin`'s invocation covers its commit/push. The run is therefore
  non-interactive by default; `--confirm` restores per-step confirmation for anyone who wants
  it. Merging or releasing outside this command still requires an explicit ask.

## Execution Steps

### Step 1: 🚀 Delegate Merge & Release Pipeline to Antigravity

Invoke Google Antigravity to perform the entire merge, checkout, tagging, and release creation
process in one delegated run — this single invocation is what waits for CI and the version/merge
logic below, so the host issues no follow-up polling commands after it starts:

```text
/antigravity:rescue --fresh --model gemini-3.5-flash --effort medium <Prompt>
```

#### Antigravity Prompt:
```text
You are running the SPECTER /ms.merglease merge and release pipeline.

Tasks to execute:

1. Pre-flight checks:
   - Verify that 'gh' CLI is installed and authenticated.
   - Check that the current branch is a feature branch (not master/main) and has an open PR.
   - Wait for GitHub CI checks on the PR to reach a final state ('gh pr checks --watch' or
     equivalent polling inside THIS run — do not return control to ask the caller to poll).

2. CI-failure classification (before merging):
   - Inspect every failed/errored check's name and log/conclusion.
   - Billing/infra pattern (case-insensitive): matches any of 'billing', 'spending limit',
     'usage limit', 'quota'; OR conclusion is 'startup_failure'; OR the job never started.
   - IF every failure matches the billing/infra pattern: proceed to merge, but print a loud
     warning ("⚠️ GitHub CI skipped: billing/infra — <failed check names>") and record the same
     line verbatim in the release notes (Step 4).
   - IF any failure is a real test/lint/typecheck/build failure (does not match the billing/infra
     pattern): STOP. Do not merge. Report the failing check names and logs, and end the run
     without creating a tag or release.
   - IF all checks passed: proceed silently, no note needed.

3. PR Merge:
   - Always use a merge commit: 'gh pr merge <PR_NUM> --merge --delete-branch=false'.
   - Do not ask which merge strategy to use.
   - Only ask for confirmation before merging if the caller passed '--confirm'; otherwise proceed
     without asking.

4. Checkout master & Pull:
   - Run 'git checkout master && git pull --ff-only origin master'.

5. Version Computation & Release Notes (fully automatic):
   - Read the last git tag. List conventional commits since that tag.
   - Compute the version bump with NO question asked, using this mapping (same mapping applies
     pre-1.0 — do not special-case 0.x):
     - Any commit has a 'BREAKING CHANGE' footer or a 'type!:' subject -> MAJOR.
     - Else, any commit has a 'feat' type -> MINOR.
     - Else -> PATCH.
   - If the caller passed an explicit '[version]' argument, use that instead of the computed
     bump, but still record the computed bump for comparison in the release notes.
   - Generate release notes that state the computed bump AND its rationale (the list of
     conventionally-typed commits that drove the decision), plus the billing/infra warning line
     from step 2 if one was recorded.
   - Only display the version/notes for confirmation if the caller passed '--confirm'; otherwise
     proceed directly to tagging with the computed (or explicit) version.

6. Create and Push Tag:
   - Create an annotated git tag for the new version and push it to origin.

7. Create GitHub Release:
   - Create a GitHub Release using the 'gh release create' command, with the notes from step 5.

8. Progress Ledger update (if 'docs/prd/feature-map.progress.md' exists):
   - Mark the merged Feature's Status row as '✅ shipped'. Do NOT touch 'docs/prd/feature-map.md' —
     this bookkeeping lives only in the separate progress file so it never invalidates the
     Feature Map's gated SHA256.
   - Commit that edit on master ('chore: mark Feature NNN shipped') and push it to origin.
     Never end the run leaving master with uncommitted changes.

9. Branch cleanup (if requested via '--cleanup').

Write your results clearly in your final report: PR merge status, the CI classification outcome
(clean / billing-skipped-with-names / stopped-on-real-failure), the computed version bump and its
rationale, the new tag, and the release URL.
```

---

### Step 1.5: 🔎 Verify Delegated End-State (silent-stall net)

Antigravity's self-report is not completion evidence — a delegated run has merged
the PR and then stalled silently without creating the tag/release (observed
2026-07). Verify the end state directly with git/gh before reporting:

```bash
gh pr view <PR_NUM> --json state,mergedAt          # ① PR is MERGED
git fetch origin master >/dev/null 2>&1
git merge-base --is-ancestor origin/master HEAD && git rev-parse HEAD  # ② local master pulled to the merge commit
git tag -l "<tag>" && git ls-remote --tags origin "<tag>"              # ③ tag exists locally AND on origin
gh release view "<tag>"                            # ④ GitHub Release exists
git log origin/master --oneline -3                 # ⑤ progress-ledger commit reached master
                                                   #    (only if docs/prd/feature-map.progress.md exists)
```

Interpretation:

- **All applicable items hold** → report `위임 완주` in Step 2.
- **Something is missing AND the delegation report gives no reason for stopping**
  (silent stall) → complete ONLY the missing items yourself, idempotently — never
  re-run completed steps. Follow the same rules the prompt gave Antigravity
  (automatic semver with its recorded rationale, annotated tag, release notes,
  ledger commit on master). Report `부분 정지 → <항목> 직접 완결` in Step 2.
- **Something is missing AND the report states why it stopped** (e.g. merge halted
  on a real CI failure — an intentional stop): do NOT fill the gap. Report the
  failure per the existing rule below; the stop was correct. This verification
  exists for *silent* stalls only.

This step is read-only checks plus missing-item completion — it is not a new gate
and produces no verdict.

---

### Step 2: Report Success

Claude summarizes the work — including any billing/infra CI warning or a stop-on-real-failure
report from Antigravity:

```text
✅ /ms.merglease 완료! (Antigravity 위임 완료)

🔀 PR 머지 및 릴리즈 태그 생성이 Antigravity CLI를 통해 백그라운드/서브세션에서 성공적으로 처리되었습니다.
🔎 위임 종상태 검증: <위임 완주 | 부분 정지 → <항목> 직접 완결>
📦 버전: <computed bump> (<rationale summary>)
⚠️ GitHub CI: <정상 통과 | billing/infra로 건너뜀: 체크 이름 | 실패로 머지 중단>
```

If Antigravity stopped the run on a real CI failure, do not report success — surface the failing
checks and tell the user the merge did not happen.

## Fallback: Antigravity Unavailable

If the Antigravity delegation cannot start, run the merge/tag/release steps directly (same rules:
automatic semver, billing/infra CI classification, merge commit only, no strategy question) — but
still do not poll the host session in a loop. If CI has not reached a final state yet, start a
single background Bash task that waits for it (`gh pr checks --watch`, backgrounded), and report
once when it completes rather than re-checking `gh pr checks` turn after turn.

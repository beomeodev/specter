---
description: "Merge open PR → release: gh pr merge → base-branch pull → tag + GitHub Release. (Delegated to Antigravity)"
argument-hint: "[version] [--no-release] [--confirm] [--cleanup]"
---

# /ms.merglease - Merge & Release (Delegated)

Delegate the PR merging, base-branch pull, automatic semver computation, tagging, and GitHub Release
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

### Step 0: WIP-Publish Preflight (host, blocking)

First, self-heal the deterministic release helper and verify its contract
(three-layer principle applied to the release track — semver and end-state
facts are computed by script, never re-derived by an LLM):

```bash
# self-heal: the runtime copy is project-local (never synced); refresh it from the synced template
install -D -m 0755 docs/templates/scripts/specter-release.sh .specify/scripts/bash/specter-release.sh
.specify/scripts/bash/specter-release.sh version
```

If the template is missing or `contract` is not `publish-helpers-v1`, **STOP**
and tell the user to run `/ms.sync` (or update this repo) first. Never fall
back to LLM-computed semver or LLM-judged end-state — silent fallback
recreates exactly the failure class these helpers remove.

Then check for merge-blocking WIP markers (2026-07-18 audit #13):

```bash
cat .specify/review-state.txt 2>/dev/null
cat .specify/.ms-wip-publish 2>/dev/null
```

If either file exists, this branch was published with unresolved CRITICAL/HIGH review findings
or via `/ms.fin --no-ci` (explicit WIP publish). **STOP and show the contents; proceed only
after the user explicitly confirms merging a WIP branch.** `/ms.merglease`'s
invocation-approval does NOT cover this case — the WIP state is information the user may not
have had when invoking. After end-state verification (Step 1.5) completes, delete
`.specify/.ms-wip-publish`; `review-state.txt` stays owned by `/ms.review`'s own lifecycle.

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
   - Resolve the push remote once and reuse it everywhere below as <REMOTE>:
     'git config branch.<current-branch>.remote', falling back to 'origin' only when the
     branch has no configured remote. Never assume 'origin' when a configured remote exists.
   - Wait for GitHub CI checks on the PR to reach a final state ('gh pr checks --watch' or
     equivalent polling inside THIS run — do not return control to ask the caller to poll).

2. CI-failure classification (before merging — script-owned, never re-derive it yourself):
   - Once checks reach a final state, run:
     .specify/scripts/bash/specter-release.sh classify-ci <PR_NUM>
     and use its JSON verbatim. It claims 'billing_infra' only on narrow structural
     signatures (startup_failure conclusion / zero jobs / jobs whose steps never
     executed with no failed-run logs) — never on a 'billing' substring in a log,
     so a real test that exercises billing code cannot be classified away.
   - overall == "clean": proceed silently, no note needed.
   - overall == "billing_infra_only": proceed to merge WITHOUT asking (2026-07-21
     user policy: local CI is authoritative; a billing/quota-dead GitHub CI must
     not stall a release). Print a loud warning
     ("⚠️ GitHub CI skipped: billing/infra — <failed check names>") and record the
     same line verbatim in the release notes (Step 5).
   - overall == "pending": CI has not reached a final state — keep waiting inside
     this run, then re-run classify-ci.
   - overall == "needs_human" or "unknown": STOP. Do not merge. Report each
     failure's name/classification/evidence from the JSON and end the run without
     creating a tag or release. Ambiguity is a stop, not a guess (fail-closed) —
     never widen the billing detection yourself.

3. PR Merge:
   - Always use a merge commit: 'gh pr merge <PR_NUM> --merge --delete-branch=false'.
   - Do not ask which merge strategy to use.
   - Only ask for confirmation before merging if the caller passed '--confirm'; otherwise proceed
     without asking.

4. Checkout base branch & Pull:
   - Resolve the base branch from the PR itself: 'gh pr view <PR_NUM> --json baseRefName'.
     Never assume master — consumer repos differ (master/main/custom).
   - Run 'git checkout <baseRefName> && git pull --ff-only <REMOTE> <baseRefName>'.

5. Version Computation & Release Notes (script-computed — do NOT compute the bump yourself):
   - Run: .specify/scripts/bash/specter-release.sh semver [explicit-version-if-caller-gave-one]
   - Use its JSON verbatim: 'chosen_version' is the release version; 'drivers' lists the
     commits that drove the bump; 'unclassified' lists non-conventional commits the
     computation could NOT use.
   - If 'chosen_version' is empty (invalid explicit version, or non-semver last tag), STOP
     and report the script's notes — do not invent a version.
   - Generate release notes that quote the computed bump AND its rationale verbatim from the
     JSON (driver commit list), include every 'unclassified' commit under a "미분류 커밋"
     heading so the reader can audit what the bump did not consider, plus the billing/infra
     warning line from step 2 if one was recorded.
   - Only display the version/notes for confirmation if the caller passed '--confirm'; otherwise
     proceed directly to tagging with 'chosen_version'.

6. Create and Push Tag — SKIP this step AND step 7 entirely if the caller passed
   '--no-release' (no tag, no GitHub Release; state "release skipped by --no-release"
   in the final report):
   - Create an annotated git tag for the new version and push it to <REMOTE>.

7. Create GitHub Release (skipped under '--no-release', see step 6):
   - Create a GitHub Release using the 'gh release create' command, with the notes from step 5.

8. Progress Ledger update (if 'docs/prd/feature-map.progress.md' exists):
   - Mark the merged Feature's Status row as '✅ shipped'. Do NOT touch 'docs/prd/feature-map.md' —
     this bookkeeping lives only in the separate progress file so it never invalidates the
     Feature Map's gated SHA256.
   - Commit that edit on the base branch ('chore: mark Feature NNN shipped') and push it to
     <REMOTE>. Never end the run leaving the base branch with uncommitted changes.

9. Branch cleanup (if requested via '--cleanup').

Write your results clearly in your final report: PR merge status, the CI classification outcome
(clean / billing-skipped-with-names / stopped-on-real-failure), the computed version bump and its
rationale, the new tag, and the release URL.
```

---

### Step 1.5: 🔎 Verify Delegated End-State (silent-stall net)

Antigravity's self-report is not completion evidence — a delegated run has merged
the PR and then stalled silently without creating the tag/release (observed
2026-07). Verify the end state with the deterministic helper (it resolves the
base branch from PR metadata / the remote default — no hardcoded master — and
dereferences the tag to the actual merge commit, not just the tag name):

```bash
.specify/scripts/bash/specter-release.sh verify-endstate <PR_NUM> <tag> [--no-release] [--ledger-feature NNN]
```

Read the JSON `checks`: each is `true | false | not_applicable | unknown` with
evidence. `unknown` means the fact could not be observed (gh/network) — it is
never treated as "absent"; re-check or verify manually before interpreting it.
The host adds no judgment: the JSON *is* the verification.

Interpretation (**hard rule: while any applicable check is still `false`, the
run may NOT be reported as success — cueline v0.22.x's tag misplacement was
detected as `false` yet the run still declared completion. Fix it or report
the failure; never "완료" over a standing `false`**):

- **Every applicable check is `true`** → report `위임 완주` in Step 2.
- **Something is missing AND the delegation report gives no reason for stopping**
  (silent stall) → complete ONLY the missing items yourself, idempotently — never
  re-run completed steps. Follow the same rules the prompt gave Antigravity
  (automatic semver with its recorded rationale, annotated tag, release notes,
  ledger commit on the base branch). Report `부분 정지 → <항목> 직접 완결` in Step 2.
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
automatic semver, billing/infra CI classification, merge commit only, no strategy question).
The deterministic helpers are NOT optional in this path: semver still comes from
`.specify/scripts/bash/specter-release.sh semver`, CI classification from its `classify-ci`,
and Step 1.5's `verify-endstate` still runs — a direct run that skips the helpers recreates
the exact bypass failure mode measured on 2026-07-21 (half of observed publishes skipped the
scripts). If the helper is missing, STOP per Step 0; never substitute manual git/gh judgment —
still do not poll the host session in a loop. If CI has not reached a final state yet, start a
single background Bash task that waits for it (`gh pr checks --watch`, backgrounded), and report
once when it completes rather than re-checking `gh pr checks` turn after turn.

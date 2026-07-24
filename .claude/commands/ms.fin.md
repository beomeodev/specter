---
description: "Finish: sync docs → conditional CI → commit → push → PR auto-create (Delegated to Antigravity)"
argument-hint: "[--no-ci]"
---

# /ms.fin - Finish Workflow (Delegated)

Sync living docs and update the daily log locally, decide whether a CI re-run is
needed, then delegate CI (when needed), staging, committing, pushing, and GitHub
PR creation to the **Google Antigravity CLI**.

This is SPECTER's single finish command. It runs the local CI gate before
publishing, but skips that gate when it would only re-validate code a clean
`/ms.review` already checked.

## CI Policy (conditional)

The local CI gate is `lint → types → tests → build` — the same gate `/ms.review`
runs. `/ms.fin` decides whether to re-run it:

- **SKIP** when the last `/ms.review` finished clean (no `.specify/review-state.txt`)
  **and** the working tree is unchanged since that review (current file hashes
  match `.specify/review-hash.cache`). Re-running CI on byte-identical code adds
  nothing.
- **RUN** when anything changed since the last review, the review left unresolved
  CRITICAL/HIGH findings (`.specify/review-state.txt` present), or no review hash
  cache exists. This is exactly where review's CI is stale — fixes applied after
  review, the `/ms.fix` track, or a direct commit. Any uncertainty errs toward RUN.
- `--no-ci` forces SKIP regardless. This is an explicit WIP/backup publish; the
  user is responsible for validating before merge. The skip is reported loudly.

Default (no flag) is safe: CI runs whenever the committed state differs from a
passed review.

## Usage

```bash
/ms.fin
/ms.fin --no-ci
```

## Execution Steps

### Step 1: 📄 Sync Living Documents (/ms.up-docs)

Claude Code runs the document synchronization locally to ensure staged
documentation is up to date:

```bash
/ms.up-docs --docs=dev
```

This updates `docs/dev_daily.md` from the outgoing work (staged + uncommitted +
unpushed changes). API-doc regeneration is not part of `--docs=dev`; run
`/ms.up-docs --docs=api` separately when API surfaces changed.

---

### Step 1.5: 👁️ High-Stakes Diff Digest (conditional, human-ack gate)

This is `/ms.fin`'s one deliberate human gate. Machines can review code, but only
the human can *own* what the product is allowed to destroy or expose — and because
`/ms.fin` sits on every track (feature AND fix), this net catches changes that never
passed `/ms.review`.

1. **Detect high-stakes hunks** in the full outgoing set — everything that
   would be published, not just what is uncommitted. Compute it as the unpushed
   range **plus** the working tree **plus untracked files** (2026-07-19 sol
   finding: a newly created migration or credential-handling file appears in
   neither diff, yet Step 3's explicit staging list can publish it):
   ```bash
   # branch upstream first, remote default second — never a hardcoded origin/master.
   BASE=$(git rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null \
     || git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
   # if BASE is still empty (no upstream, no origin/HEAD): STOP and ask the user
   # which base branch the publish diff should be computed against.
   git diff "$BASE"...HEAD   # commits not yet pushed (this is what catches the /ms.fix track,
                             # which commits in its own Step 6 before reaching /ms.fin)
   git diff HEAD             # uncommitted + staged work
   git ls-files --others --exclude-standard   # untracked files — read each one's CONTENT
                                              # and scan it with the same criteria below;
                                              # binary/oversized untracked files are reported
                                              # as "수동 확인 필요", never silently skipped
   ```
   A hunk is high-stakes if it touches any of:
   - **auth/credentials**: session, token, password, OTP/2FA, crypto keys, permission checks
   - **money/value**: prices, balances, orders, payments, quantities that map to money
   - **destructive operations**: `DELETE FROM`, `DROP`, `TRUNCATE`, `.delete(`, `rm -r`,
     `unlink`, overwriting writes to user data, cascade rules
   - **schema/migrations**: anything under the migrations dir, `ALTER/CREATE/DROP TABLE`
   - **user-content handling**: code that serializes, exports, or transmits user data
2. **If nothing matches → continue silently to Step 2.** Zero friction on ordinary diffs;
   this gate must never become ceremony.
3. **If matched → present the digest and STOP.** Show ONLY the matched hunks (not the whole
   diff), grouped by file, each introduced by one line answering the reader's question:
   ```text
   👁️ 정독 필요 — 이 변경이 지우거나·덮어쓰거나·노출하는 것:
   ── backend/auth/session.py (auth)
      <hunk>  ← 세션 토큰 검증 조건이 X에서 Y로 바뀜
   ── db/migrations/0007_xxx.sql (migration/destructive)
      <hunk>  ← 기존 rows의 컬럼 Z를 NOT NULL로 좁힘 (기존 NULL 행 존재 시?)
   ```
   Keep the digest tight (aim ≤ 60 lines of hunk content — curate, don't dump). Then wait
   for the user's explicit acknowledgement before Step 2. Any affirmative reply after
   actually presenting the digest counts as the ack; proceeding without presenting it does
   not.
4. On a re-run in the same session (e.g. after a CI fix), re-digest only hunks that
   changed since the last ack — don't make the user re-read what they already read.
   The same rule covers `/ms.review` Step 6.6b: migration hunks the user already
   acked in this session's migration-rollback analysis are skipped here unless
   they changed since that ack.

---

### Step 2: 🧭 Decide CI Mode

Decide whether the CI gate must re-run before publishing. Mismatches and missing
artifacts deliberately fall through to `RUN`:

```bash
CI_MODE="RUN"; CI_REASON="changed since review, or no clean review baseline"
if [ "$1" = "--no-ci" ]; then
  CI_MODE="SKIP"; CI_REASON="--no-ci (explicit WIP publish)"
  # Merge-blocking WIP marker (2026-07-18 audit #13): a --no-ci publish must
  # not reach /ms.merglease looking as if gates had passed — merglease's
  # Step 0 preflight surfaces this marker and requires explicit user ack.
  mkdir -p .specify
  printf 'reason=--no-ci publish\nts=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > .specify/.ms-wip-publish
elif [ ! -f .specify/review-state.txt ] && [ -f .specify/review-hash.cache ]; then
  # Recompute hashes of currently changed files and compare to the review cache.
  # Untracked files included (2026-07-18 audit #14): a file added after review
  # is invisible to `git diff HEAD` and must not slip through the hash match.
  CHANGED=$( { git diff --name-only --diff-filter=ACMRTUXB HEAD 2>/dev/null; \
               git diff --cached --name-only --diff-filter=ACMRTUXB 2>/dev/null; \
               git ls-files --others --exclude-standard 2>/dev/null; } \
             | sort -u | sed '/^$/d' )
  printf '%s\n' "$CHANGED" \
    | xargs -P "$(nproc)" -I{} sh -c 'echo "$(sha1sum "{}" 2>/dev/null | cut -d" " -f1)  {}"' \
    | sort -k2 > .specify/fin-hash.now 2>/dev/null || true
  if diff -q <(sort -k2 .specify/review-hash.cache) <(sort -k2 .specify/fin-hash.now) >/dev/null 2>&1; then
    CI_MODE="SKIP"; CI_REASON="unchanged since clean /ms.review (hash match)"
  fi
  rm -f .specify/fin-hash.now
fi
echo "CI_MODE=$CI_MODE ($CI_REASON)"
```

Carry the resolved `CI_MODE` and `CI_REASON` into the Antigravity delegation in
Step 3.

---

### Step 3: 🚀 Delegate Publish & PR Pipeline to Antigravity

Invoke Google Antigravity to run the CI gate (only when `CI_MODE=RUN`), stage
files, commit with conventional messages, push the branch, and manage the GitHub
pull request:

```text
/antigravity:rescue --fresh --model gemini-3.5-flash --effort medium <Prompt>
```

#### Antigravity Prompt:
```text
You are running the SPECTER /ms.fin publish pipeline.
CI_MODE=<RUN|SKIP>  REASON=<reason from Step 2>

Tasks to execute:
1. CI gate:
   - If CI_MODE is SKIP: do NOT run CI. Print the skip reason. If
     .specify/review-state.txt exists, print its contents as a warning before
     continuing (with --no-ci, publishing proceeds even with warnings).
   - If CI_MODE is RUN: run locally-runnable gates (lint -> types -> tests ->
     build) using the project's default runner (e.g. 'make ci' or test commands).
     If any check fails, STOP immediately and report the failure. Do not commit
     or push.
2. Stage and Commit (split by logical unit — DEFAULT):
   - Review changed files and build an explicit staging list (do not run 'git add .').
   - Group the changes by logical concern, NOT by file type. Each commit must be
     one coherent, self-consistent change (e.g. a feature + its tests + its docs
     belong together; an unrelated refactor or config bump is a separate commit).
   - DEFAULT to multiple commits when the diff spans more than one concern. Stage
     each concern's files selectively (use 'git add -p' / pathspecs) and commit it
     before staging the next. Order commits so each one leaves the tree buildable.
   - Collapse to a SINGLE commit only when the whole diff is one cohesive change;
     never split a single concern into noise commits just to inflate the count.
   - Format staged files using pre-commit hooks (if configured) before each commit.
   - Give every commit a meaningful conventional message (feat/fix/chore/docs/test)
     that describes that commit's concern specifically.
3. Push:
   - Push the committed branch to its configured remote
     ('git config branch.<current-branch>.remote', falling back to 'origin'
     only when none is configured).
4. PR Auto-create:
   - Compose the PR body from the latest review report in docs/review/ (if any)
     plus this run's commit messages: summary, key changes by concern, gate
     results, outstanding warnings from .specify/review-state.txt.
   - Use 'gh' CLI to create a new PR or edit the body if one already exists.
   - Output the PR URL.
5. Self-review stamp (fail-open — this step must NEVER fail the pipeline):
   - Purpose: record the workflow's already-computed review verdict as an
     official GitHub PullRequestReview so it registers as a review contribution
     on the author's profile. This is NOT a new review — do not re-review code.
   - Compose a short stamp (verdict + gate results, a few lines, not the full
     report) from the latest review report in docs/review/; if none exists,
     summarize this run's CI gate outcome instead.
   - Submit it as a COMMENT review: 'gh pr review <PR-number> --comment --body
     "<stamp>"'. COMMENT is mandatory — GitHub forbids approving your own PR.
   - Submit at most one stamp per /ms.fin run. If submission fails, report the
     error and continue; never block publish on this step.

Do not edit code files except staging and formatting. Write your results, the PR URL, and the self-review stamp status clearly in your final report.
```

---

### Step 3.5: 🔎 Verify Delegated End-State (silent-stall net)

Antigravity's self-report is not completion evidence — delegated runs have stalled
silently mid-pipeline (observed 2026-07: stopped before committing). Before
reporting success, verify the end state with the deterministic helper (it
resolves the branch's real upstream / the remote default — no hardcoded
origin/master):

```bash
# self-heal: the runtime copy is project-local (never synced); refresh it from the synced template
install -D -m 0755 docs/templates/scripts/specter-publish.sh .specify/scripts/bash/specter-publish.sh
.specify/scripts/bash/specter-publish.sh version        # contract probe — must report publish-helpers-v1
.specify/scripts/bash/specter-publish.sh verify-endstate
```

If the template is missing **or the probe's `contract` is not `publish-helpers-v1`**,
**STOP** and tell the user to run `/ms.sync` first —
never substitute LLM-judged end-state checks (silent fallback recreates the
failure class this helper removes). Read the JSON `checks`
(`tree_clean` / `pushed` / `pr_open`): each is
`true | false | not_applicable | unknown` with evidence. `unknown` means the
fact could not be observed (gh/network) — never treat it as "absent"; re-check
or verify manually. The host adds no judgment: the JSON *is* the verification.

The self-review stamp (prompt task 5) is fail-open by design — report its status
as delegated, never repair or block on it.

Interpretation (**hard rule: while any applicable check is still `false`, the
run may NOT be reported as success — 2026-07-21 evidence showed a detected
`false` sailing into a completion claim. Fix it or report the failure; never
"완료" over a standing `false`**):

- **Every applicable check is `true`** → report `위임 완주` in Step 4.
- **Something is missing AND the delegation report gives no reason for stopping**
  (silent stall) → complete ONLY the missing items yourself, idempotently — never
  re-run the whole pipeline or redo completed steps. Follow the same rules the
  prompt gave Antigravity, including `CI_MODE`: if the stall happened before the
  CI gate ran and `CI_MODE=RUN`, run the gate first, and a real failure stops the
  publish exactly as it would have in the delegation. Report
  `부분 정지 → <항목> 직접 완결` in Step 4.
- **Something is missing AND the report states why it stopped** (e.g. the CI gate
  failed — an intentional stop): do NOT fill the gap. Report the failure per the
  existing rules; the stop was correct. This verification exists for *silent*
  stalls only.

This step is read-only checks plus missing-item completion — it is not a new gate
and produces no verdict.

---

### Step 4: Report Success

Claude summarizes the work:

```text
✅ /ms.fin 완료! (Antigravity 위임 완료)

📄 Living Documents 동기화 완료 (/ms.up-docs)
🧭 CI 모드: <RUN: CI 실행 | SKIP: review 후 변경 없음 → 생략 | SKIP: --no-ci>
🚀 Git 커밋, Push 및 PR 자동 생성이 Antigravity CLI를 통해 처리되었습니다.
🔎 위임 종상태 검증: <위임 완주 | 부분 정지 → <항목> 직접 완결>
🔖 셀프 리뷰 스탬프: <제출됨 (COMMENT review — contribution graph 반영) | 실패 → 무시하고 진행>


📋 다음 단계:
  1. 제공된 PR URL에서 결과 검토 (수동)
  2. (feature 브랜치에서) /ms.merglease  (PR 머지 + tag + release 발행)
```

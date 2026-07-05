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

This updates `docs/dev_daily.md` and API specifications based on staged files.

---

### Step 1.5: 👁️ High-Stakes Diff Digest (conditional, human-ack gate)

This is `/ms.fin`'s one deliberate human gate. Machines can review code, but only
the human can *own* what the product is allowed to destroy or expose — and because
`/ms.fin` sits on every track (feature AND fix), this net catches changes that never
passed `/ms.review`.

1. **Detect high-stakes hunks** in the outgoing diff (`git diff HEAD` + staged).
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

---

### Step 2: 🧭 Decide CI Mode

Decide whether the CI gate must re-run before publishing. Mismatches and missing
artifacts deliberately fall through to `RUN`:

```bash
CI_MODE="RUN"; CI_REASON="changed since review, or no clean review baseline"
if [ "$1" = "--no-ci" ]; then
  CI_MODE="SKIP"; CI_REASON="--no-ci (explicit WIP publish)"
elif [ ! -f .specify/review-state.txt ] && [ -f .specify/review-hash.cache ]; then
  # Recompute hashes of currently changed files and compare to the review cache.
  CHANGED=$( { git diff --name-only --diff-filter=ACMRTUXB HEAD 2>/dev/null; \
               git diff --cached --name-only --diff-filter=ACMRTUXB 2>/dev/null; } \
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
   - Push the committed branch to origin.
4. PR Auto-create:
   - Auto-detect the latest docs/PR_*_BODY.md file.
   - Use 'gh' CLI to create a new PR or edit the body if one already exists.
   - Output the PR URL.

Do not edit code files except staging and formatting. Write your results and the PR URL clearly in your final report.
```

---

### Step 4: Report Success

Claude summarizes the work:

```text
✅ /ms.fin 완료! (Antigravity 위임 완료)

📄 Living Documents 동기화 완료 (/ms.up-docs)
🧭 CI 모드: <RUN: CI 실행 | SKIP: review 후 변경 없음 → 생략 | SKIP: --no-ci>
🚀 Git 커밋, Push 및 PR 자동 생성이 Antigravity CLI를 통해 처리되었습니다.

📋 다음 단계:
  1. 제공된 PR URL에서 결과 검토 (수동)
  2. (feature 브랜치에서) /ms.merglease  (PR 머지 + tag + release 발행)
```

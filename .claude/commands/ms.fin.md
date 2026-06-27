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
2. Stage and Commit:
   - Review changed files and build an explicit staging list (do not run 'git add .').
   - Stage the features, tests, docs, and configurations related to the current feature.
   - Format staged files using pre-commit hooks (if configured).
   - Generate a meaningful conventional commit message (feat/fix/chore/docs/test).
   - Execute git commit.
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

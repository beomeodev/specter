---
description: "Finish workflow: sync docs → update daily log → CI checks → commit → push → PR auto-create"
---

Execute the following tasks in order:

## 1. 📄 Sync Living Documents (/ms.up-docs)

**NEW**: Sync code changes to Living Documents.

### Execution

```bash
/ms.up-docs --docs=dev
```

**Operations**:
- **Analyze Git changes**: `git diff --cached` (staged files only)
- **Auto-update dev_daily.md**: Append Git diff summary with timestamp
- **Validate TAG chains**: Report best-effort @SPEC -> @TEST -> @CODE traceability warnings
- **Sync API docs** (if staged changes exist): Generate/update `docs/api/{TAG}.md`

**Example output**:
```
✅ Document sync complete

📦 Files Updated:
- docs/dev_daily.md (appended)
- docs/api/AUTH-001.md (updated)

📋 TAG Traceability: 95.0% (23/24 linked tags; warnings reported)

⏱️ Duration: 3.2 seconds
```

**Error handling**:
- **No staged changes**: ⚠️ Show warning and proceed (fallback to manual dev_daily.md update)
- **Many TAG warnings**: ⚠️ Show warning but continue workflow

---

## 2. 📝 Review Daily Work Log (fallback)

**Note**: Step 1's `/ms.up-docs` already updated dev_daily.md.
This step is only used as fallback when `/ms.up-docs` fails.

Analyze current session's work and review `docs/dev_daily.md`:

### Analysis items
- Check list of changed files (from git status or conversation context)
- Identify major tasks completed
- Note added/modified/deleted features

### Update rules
1. **Check today's date section**:
   - If today's date (YYYY-MM-DD) section exists → Add to Done in that section
   - If not exists → Create new section at file top

2. **Format** (maintain existing format):
   ```markdown
   # 🗓 YYYY-MM-DD (Day)

   ## 📌 Focus
   - 주요 작업 테마 (1줄 요약)

   ## ✅ Done
   - 완료한 작업 내역 (간략하게, 3-5개 bullet points)
   ```

3. **작성 스타일**:
   - **간결하게**: 각 항목은 1줄로
   - **구체적으로**: "코드 수정" (X) → "tech_algo.py에 MACD 신호 추가" (O)
   - **기존 항목 유지**: 오늘 날짜 섹션에 이미 작성된 내용이 있으면 Done 아래에 추가 (덮어쓰기 X)

### 예시
```markdown
# 🗓 2025-10-01 (Tue)

## 📌 Focus
- AGENTS.md 템플릿 구조 개선 및 Makefile 통합

## ✅ Done
- templates 디렉토리 생성 및 AGENTS.md 3개 파일 작성 완료
- Markdown 포맷팅 적용 (헤더, 코드블록, 리스트)
- 루트 Makefile과 .devcontainer/Makefile 역할 분리
- /fin, /finq 슬래시 커맨드 추가
```

---

## 3. 🚀 Run CI Checks

### 3.0 Review-State Notice

If `.specify/review-state.txt` exists, show it before CI as advisory context.
Do not require the file to exist, and do not block `/fin` solely because it is
present. `/ms.review` owns the review result; `/fin` owns docs, CI, commit,
push, and PR creation.

```bash
if [ -f .specify/review-state.txt ]; then
  echo "⚠️ Prior /ms.review state exists:"
  cat .specify/review-state.txt
  echo ""
  echo "Continuing because review-state is advisory in /fin."
fi
```

**This is the pre-push gate** — and since remote CI is frequently unavailable
(GitHub Actions billing), this local run is often the *only* CI that ever
executes. Catch failures here, before the bad push.

**Primary mechanism — `local-ci` subagent** (read-only, reproduces the repo's
own gates):

```
Delegate to the `local-ci` agent. It reads .github/workflows/*.yml and runs the
locally-runnable gates (lint → types → tests → build) with the project's declared
runner (backend: `cd backend && uv run ...`), skipping secret/server-dependent
jobs. It reports pass/fail per gate. It makes NO merge/override decision and edits nothing.
```

**Then — `quality-gate` agent** for TRUST validation when available: coverage ≥85%,
TAG integrity, type/lint clean.

**Result handling**:
- ✅ **All gates pass**: Proceed to next step.
- ❌ **Any gate fails**: Display the failing gate + error and **STOP** (don't commit). Fix in the main conversation, then re-run `/fin`.

> Fallback (if no workflow file): `make ci` → `ruff check .` / `mypy src/` / `pytest -v --cov=src` (backend via `uv run`), frontend `npm run lint && npm run typecheck && npm run test -- --run`.

---

## 4. 💾 Git Commit and Push

### Pre-commit Hook handling strategy

**Problem**: Pre-commit hooks or IDE auto-format modify files after commit, making git state dirty

**Solution**: Run pre-commit first before committing to complete formatting, with error/warning logging

```bash
# 1. Build an explicit staging list. NEVER use `git add .`.
# Include only files that belong to the current feature/fix and were reviewed
# in this workflow. If the list cannot be derived confidently, STOP and ask.
STAGE_PATHS=(
  # examples:
  # "specs/018-admin-analytics-page"
  # "backend/src/<package>/dashboard/group_performance.py"
  # "backend/tests/dashboard/unit/test_group_performance.py"
  # "frontend/app/(admin)/[adminPrefix]/dashboard/page.tsx"
  # "frontend/tests/admin/admin-analytics-page.test.tsx"
  # "docs/dev_daily.md"
)

if [ "${#STAGE_PATHS[@]}" -eq 0 ]; then
  echo "❌ No explicit STAGE_PATHS configured. Refusing to run git add ."
  exit 1
fi

printf 'Staging reviewed files:\n'
printf '  %s\n' "${STAGE_PATHS[@]}"
git add -- "${STAGE_PATHS[@]}"

# Safety check: verify no unrelated dirty file was staged.
git diff --cached --name-only

# 2. Run pre-commit hooks to format files (if .pre-commit-config.yaml exists)
if [ -f .pre-commit-config.yaml ]; then
  # Create log directory if not exists
  mkdir -p docs/log/pre-commit

  # Run pre-commit and capture output
  PRE_COMMIT_OUTPUT=$(pre-commit run --all-files 2>&1)
  PRE_COMMIT_EXIT_CODE=$?

  # Check for errors or warnings (exit code != 0 or output contains ERROR/WARNING)
  if [ $PRE_COMMIT_EXIT_CODE -ne 0 ] || echo "$PRE_COMMIT_OUTPUT" | grep -iE "(error|warning|fail)" > /dev/null; then
    # Generate log filename with timestamp
    LOG_FILE="docs/log/pre-commit/pre-commit-$(date +%Y%m%d-%H%M%S).log"

    # Write detailed log
    cat > "$LOG_FILE" << EOF
# Pre-commit Hook Log
Date: $(date '+%Y-%m-%d %H:%M:%S')
Exit Code: $PRE_COMMIT_EXIT_CODE
Command: /fin

## Output:
$PRE_COMMIT_OUTPUT

## Environment:
Branch: $(git branch --show-current)
Commit: $(git rev-parse --short HEAD)
EOF

    # Show minimal user notification
    echo "⚠️  Pre-commit hooks reported issues"
    echo "📝 Detailed log saved: $LOG_FILE"
    echo ""
  fi

  # Hook may modify files. Re-stage only the reviewed file list, never `git add .`.
  git add -- "${STAGE_PATHS[@]}"
  git diff --cached --name-only
fi

# 3. git commit (커밋 메시지 생성)
git commit -m "생성한_커밋_메시지"

# 4. git push (with friendly auth-failure handler)
BRANCH=$(git branch --show-current)
if git rev-parse --abbrev-ref "@{u}" >/dev/null 2>&1; then
  PUSH_OUTPUT=$(git push 2>&1) || PUSH_FAILED=1
else
  PUSH_OUTPUT=$(git push -u origin "$BRANCH" 2>&1) || PUSH_FAILED=1
fi

if [ "$PUSH_FAILED" = "1" ]; then
  if echo "$PUSH_OUTPUT" | grep -q "Permission denied (publickey)"; then
    cat <<'AUTH_HELP'
❌ Push 실패 — SSH 인증 안 됨

해결 절차 (호스트에서):
  1. eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519
  2. (필요 시) gh auth login --hostname github.com --git-protocol ssh --web
  3. docker compose down && docker compose up -d   # 컨테이너 재시작

자세한 안내: docs/runbooks/dev_environment_auth.md
AUTH_HELP
  else
    echo "❌ Push 실패:"
    echo "$PUSH_OUTPUT" | tail -10
  fi
  echo ""
  echo "(commit은 로컬에 저장됨. 인증 픽스 후 'git push' 수동 재실행 가능)"
  exit 1
fi
```

**Why this works**:
- Pre-commit hooks (ruff-format, etc.) run and modify files
- Modified files are re-staged with the explicit `STAGE_PATHS` list
- Commit captures all formatting changes
- No dirty state after commit
- **Errors/warnings logged to `docs/log/pre-commit/` for later review**
- **Push 실패 시**: SSH 인증 실패면 `dev_environment_auth.md` 안내; 그 외는 마지막 10줄만 보여주고 commit은 보존 (수동 재시도 가능)

**Logging behavior**:
- ✅ Only logs when errors/warnings occur (non-zero exit code or ERROR/WARNING in output)
- ✅ One log file per run with timestamp: `pre-commit-YYYYMMDD-HHMMSS.log`
- ✅ Includes full output, exit code, git context for troubleshooting
- ✅ User sees minimal notification, full details in log file

### Commit message generation rules
Analyze changes and write **meaningful commit message**:

**Format**:
```
타입(범위): 제목

- 상세 내용 1
- 상세 내용 2
```

**Type**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Refactoring
- `docs`: Documentation
- `test`: Add tests
- `chore`: Build, configuration changes

**Example**:
```
feat(strategy): MACD 기반 기술적 분석 추가

- tech_algo.py에 MACD 신호 생성 로직 구현
- 백테스트 테스트 케이스 추가
```

### Error handling
- **When nothing to commit**: Display `⚠️ Nothing to commit` and proceed
- **When push fails**: Display `❌ Push failed` (with error details). Commit은 로컬에 보존됨 → 인증 픽스 후 수동 `git push` 가능.

---

## 4.5. 🔀 GitHub PR Auto-create (NEW)

**목적**: push 직후 같은 브랜치의 PR을 자동 생성/갱신. 운영자는 GitHub UI 가서 검토 + 머지만.

**동작 원칙**:
- **Idempotent**: 같은 브랜치에 이미 PR이 있으면 body만 갱신, 없으면 신규 생성.
- **PR body 자동 탐지**: `docs/PR_*_BODY.md` 패턴 중 가장 최근 mtime 파일을 자동 사용. 없으면 마지막 commit body 사용 (fallback).
- **PR title**: 마지막 commit의 첫 줄.
- **Base branch**: `master` (default; `main` 도 fallback).
- **Auto-merge 안 함**: 머지는 항상 사람 판단.

```bash
# Pre-flight: gh CLI 설치 + 인증 확인
if ! command -v gh >/dev/null 2>&1; then
  echo "⚠️  gh CLI 미설치 — PR 자동 생성 스킵"
  echo "    설치: https://cli.github.com/"
  echo "    또는 컨테이너 rebuild: docs/runbooks/dev_environment_auth.md"
  # commit + push는 끝났으므로 워크플로우는 부분 완료로 진행
elif ! gh auth status >/dev/null 2>&1; then
  echo "⚠️  gh 인증 안 됨 — PR 자동 생성 스킵"
  echo "    호스트에서: gh auth login --hostname github.com --git-protocol ssh --web"
  echo "    그 후 컨테이너 재시작: docker compose down && docker compose up -d"
else
  # Base branch 결정 (master 우선, 없으면 main)
  BASE_BRANCH="master"
  if ! git rev-parse --verify "origin/${BASE_BRANCH}" >/dev/null 2>&1; then
    BASE_BRANCH="main"
  fi

  # PR body 파일 자동 탐지 (가장 최근 docs/PR_*_BODY.md)
  PR_BODY_FILE=$(ls -t docs/PR_*_BODY.md 2>/dev/null | head -1)

  # PR title = 마지막 commit 첫 줄
  PR_TITLE=$(git log -1 --pretty=%s)

  # Idempotent: 이미 PR 있으면 edit, 없으면 create
  if PR_NUM=$(gh pr view --json number --jq .number 2>/dev/null); then
    echo "ℹ️  PR #${PR_NUM} 이미 존재 — body 갱신 중"
    if [ -n "$PR_BODY_FILE" ]; then
      gh pr edit "$PR_NUM" --body-file "$PR_BODY_FILE"
    fi
    PR_URL=$(gh pr view "$PR_NUM" --json url --jq .url)
    echo "✅ PR 갱신 완료: $PR_URL"
  else
    echo "🚀 새 PR 생성 중 (base: ${BASE_BRANCH})..."
    if [ -n "$PR_BODY_FILE" ]; then
      PR_URL=$(gh pr create \
        --title "$PR_TITLE" \
        --body-file "$PR_BODY_FILE" \
        --base "$BASE_BRANCH")
    else
      # fallback: 마지막 commit body 사용
      PR_URL=$(gh pr create \
        --title "$PR_TITLE" \
        --body "$(git log -1 --pretty=%b)" \
        --base "$BASE_BRANCH")
    fi
    if [ $? -eq 0 ]; then
      echo "✅ PR 생성 완료: $PR_URL"
    else
      echo "⚠️  PR 자동 생성 실패 — 호스트에서 수동 실행:"
      echo "    gh pr create --title \"$PR_TITLE\" --body-file \"$PR_BODY_FILE\" --base $BASE_BRANCH"
    fi
  fi
fi
```

### PR 자동화 안전장치

- **base branch가 머지된 후 차단되지 않음**: GitHub의 branch protection rule이 켜져 있어도 PR 생성은 가능 (머지만 차단).
- **fork repo 처리**: `gh pr create` 가 자동 감지. fork 면 upstream으로 PR 생성.
- **secrets 자동 redact 안 함**: `docs/PR_*_BODY.md` 작성 시 직접 secret 안 들어가도록 운영자 책임. 향후 `git secrets` 같은 hook 추가 고려.
- **draft PR**: 기본 ready-for-review. 필요 시 `gh pr edit --draft` 으로 전환.

### 의도적으로 _안_ 하는 것

- **`gh pr merge`** — 머지는 항상 사람 판단. auto-merge가 필요하면 GitHub UI에서 "Auto-merge" 토글.
- **`--reviewer` 자동 추가** — 단일 운영자 / 팀 컨벤션에 따라 다름. per-project 설정으로 추후 분리.
- **태그 / Release** — `/ms.merglease` 명령어로 분리. feature 브랜치에서 호출(PR 머지 + 태그 + Release 통합).

---

## 5. ✅ Completion Message

Output after all steps complete:

```
✅ /fin 완료!

📄 Living Documents 동기화 완료 (/ms.up-docs)
📝 dev_daily.md 업데이트 완료
🚀 CI 체크 통과
💾 커밋: [생성한 메시지]
🚀 Push 완료 (또는 실패 시 에러 메시지)
🔀 PR: [PR URL] (생성 또는 갱신 / 실패 시 안내)

📋 다음 단계:
  1. PR 페이지에서 검토 (수동)
  2. (feature 브랜치에서) /ms.merglease  (PR 머지 + tag + release 발행)
```

---

## ⚠️ Important Notes

1. **/ms.up-docs integration**:
   - **NEW**: Step 1 auto-runs `/ms.up-docs --docs=dev`
   - dev_daily.md auto-updates (based on Git diff)
   - Best-effort TAG chain traceability warnings
   - If no staged changes, show warning and proceed (fallback to manual update)

2. **When updating dev_daily.md** (fallback only):
   - Never delete existing content
   - Only append to today's date section
   - Write Focus only when creating today's section for first time

3. **When CI fails**:
   - Stop immediately
   - Clearly display which check failed
   - Don't commit/push

4. **Git behavior**:
   - Handles same as Makefile's finish target
   - On commit failure, only show error message and proceed
   - On push failure, only show error message and complete workflow

5. **Workflow sequence (UPDATED)**:
   ```
   /ms.up-docs --docs=dev  # Step 1: Sync Living Docs
   ↓
   (Review dev_daily.md)   # Step 2: Fallback only
   ↓
   make ci                 # Step 3: CI checks
   ↓
   git commit && push      # Step 4: Commit & push
   ↓
   gh pr create / edit     # Step 4.5: PR auto-create (NEW, idempotent)
   ↓
   (사람이 PR 검토)         # Manual review on GitHub UI
   ↓
   /ms.merglease (feature 브랜치에서) # PR 머지 + Tag + GitHub Release (별도 명령)
   ```

6. **Auth dependency**: Step 4 (push) + Step 4.5 (PR) 는 컨테이너 안에서 호스트의 SSH agent + gh CLI auth 를 통해 동작합니다. 호스트 셋업 미완료 시 친절한 안내 출력 후 commit은 보존. 셋업 절차: [`docs/runbooks/dev_environment_auth.md`](../../docs/runbooks/dev_environment_auth.md).

7. **PR body 자동 탐지**: `docs/PR_*_BODY.md` 패턴 (예: `PR_014_BODY.md`, `PR_015_BODY.md`) 중 가장 최근 mtime 파일을 자동 사용. 없으면 마지막 commit body fallback. **운영자가 PR 본문을 미리 작성해두는 것 권장.**

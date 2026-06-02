---
description: "Quick finish: sync docs → update daily log → commit → push → PR auto-create (NO CI checks)"
---

Execute the following tasks in order:

## 1. 📄 Sync Living Documents (/ms.up-docs)

**NEW**: Quickly sync code changes to Living Documents.

### Execution

```bash
/ms.up-docs --docs=dev
```

**Operations**:
- **Analyze Git changes**: `git diff --cached` (staged files only)
- **Auto-update dev_daily.md**: Append Git diff summary with timestamp
- **Validate TAG chains**: Report best-effort @SPEC -> @TEST -> @CODE traceability warnings (quick scan)
- **Sync API docs** (if staged changes exist): Generate/update `docs/api/{TAG}.md`

**Quick mode optimizations**:
- Process only staged changes (no full scan)
- Perform basic TAG validation only (skip detailed validation)
- Update only API docs for changed files

**Example output**:
```
✅ Document sync complete (Quick mode)

📦 Files Updated:
- docs/dev_daily.md (appended)

📋 TAG Traceability: 95.0% (quick scan; warnings reported)

⏱️ Duration: 1.8 seconds
```

**Error handling**:
- **No staged changes**: ⚠️ Show warning and proceed (fallback to manual dev_daily.md update)
- **Many TAG warnings**: ⚠️ Show warning but continue workflow (review later with /fin or /ms.review)

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

## 2.5. 📄 Auto-update README.md (Optional)

### Analysis items

Check if changed files include major feature changes:

**Major change detection targets**:
- `.claude/agents/*` - Agent structure changes
- `.claude/commands/*` - Workflow changes
- `.devcontainer/Makefile` - Development command changes
- `pyproject.toml` - Dependency/tech stack changes
- `.mcp.json` - MCP server configuration changes

### Update decision criteria

**README.md update REQUIRED** if following changes exist:
- ✅ New major features added (agents, commands, workflows)
- ✅ Project structure changes (directories, core files)
- ✅ Installation/execution method changes (Makefile targets, environment variables)
- ✅ Tech stack changes (dependency management, MCP servers)

**Skip update**:
- ❌ Documentation-only changes (`docs/*.md`)
- ❌ Minor configuration file adjustments
- ❌ Bug fixes (no functionality changes)

### Update principles (CRITICAL)

**❌ ABSOLUTELY FORBIDDEN - Change history tracking**:
```markdown
❌ "변경됨", "추가됨", "업데이트됨" 같은 메타 정보
❌ 변경 날짜나 버전 정보
❌ 과거 상태 언급 ("이전에는 X였으나 이제 Y")
❌ "(2025-10-21 추가)", "(최근 변경)" 같은 타임스탬프
```

**✅ 필수 사항 - 현재 상태만 기술**:
```markdown
✅ 프로젝트를 처음 보는 사람 관점으로 작성
✅ 지금 당장 사용 가능한 기능/방법만 나열
✅ 현재 상태를 명확하고 간결하게 설명
✅ 시제: 현재형만 사용 ("provides", "uses", "supports")
```

### 잘못된 예시 vs 올바른 예시

**❌ 잘못된 업데이트 (변경 이력 추적)**:
```markdown
## Features
- User authentication (추가됨: 2025-10-20)
- Agent system (변경됨: 2025-10-21)
  - 이전에는 Claude만 사용했으나 이제 Gemini/Codex 분담 구조로 개선
- MCP server support (최근 추가)

## Changes
- 2025-10-21: Agent system updated to use Gemini/Codex
- 2025-10-20: Added MCP server support
```

**✅ Correct update (current state only)**:
```markdown
## Features
- User authentication
- Multi-AI agent system
  - Gemini: Fast codebase exploration and library research
  - Claude: Integration design and orchestration
  - Codex: Deep code analysis and validation
- MCP server integration (Context7, CLI-bridge)

## Quick Start
```bash
make sptcc  # Clone + container + Claude Code
```

## Project Structure
```
.claude/
  agents/     # 6 specialized agents
  commands/   # Workflow automation
```
```

### Implementation logic

```python
# 1. Analyze changes
changed_files = git_status()

# 2. Detect major changes
major_change_patterns = [
    ".claude/agents/",
    ".claude/commands/",
    ".devcontainer/Makefile",
    "pyproject.toml",
    ".mcp.json"
]

has_major_changes = any(
    pattern in file for file in changed_files
    for pattern in major_change_patterns
)

# 3. Update README.md (only if major changes exist)
if has_major_changes:
    # Read current README.md
    readme_content = read_file("README.md")

    # Update sections to reflect current state
    # NO mentions of "changed", "added", "updated"
    # NO timestamps or version info
    # ONLY describe what exists NOW

    updated_readme = update_to_current_state(
        readme_content,
        changed_files
    )

    write_file("README.md", updated_readme)

    print("✅ README.md updated to reflect current state")
else:
    print("⏭️  No major changes - README.md update skipped")
```

### 업데이트 체크리스트

업데이트 전 확인:
- [ ] 변경 이력 언급 제거 ("추가됨", "변경됨" 등)
- [ ] 날짜/버전 정보 제거
- [ ] 과거 상태 비교 제거 ("이전에는...")
- [ ] 현재형 시제 사용 ("provides", "uses")
- [ ] 처음 보는 사람도 이해 가능한 설명
- [ ] 실제 사용 가능한 명령어/방법만 기재

---

## 3. 💾 Git Commit and Push (Skip CI checks)

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
Command: /finq

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
- `wip`: Work In Progress

**Example**:
```
wip(strategy): MACD 신호 생성 로직 작업 중

- 기본 구조 구현
- 테스트 작성 필요
```

### Error handling
- **When nothing to commit**: Display `⚠️ Nothing to commit` and proceed
- **When push fails**: Display `❌ Push failed` (with error details). Commit은 로컬에 보존됨 → 인증 픽스 후 수동 `git push` 가능.

---

## 3.5. 🔀 GitHub PR Auto-create (NEW — Quick mode)

**목적**: push 직후 같은 브랜치의 PR을 자동 생성/갱신. WIP commit 워크플로우에 PR 생성·갱신을 묶어 한 번 더 빨라짐.

**동작 원칙**:
- **Idempotent**: 같은 브랜치에 이미 PR이 있으면 body만 갱신, 없으면 신규 생성.
- **PR body 자동 탐지**: `docs/PR_*_BODY.md` 패턴 중 가장 최근 mtime 파일을 자동 사용. 없으면 마지막 commit body 사용 (fallback).
- **PR title**: 마지막 commit의 첫 줄 (WIP commit 이면 `wip(...)` 가 그대로 PR 제목).
- **Base branch**: `master` (default; `main` 도 fallback).
- **Auto-merge 안 함**: 머지는 항상 사람 판단.
- **Quick mode 차이점**: `/fin` 과 동일한 PR 로직이지만 CI 검증을 안 거쳤으므로, 머지 전 운영자가 GitHub Actions 결과를 확인해야 함.

```bash
# Pre-flight: gh CLI 설치 + 인증 확인
if ! command -v gh >/dev/null 2>&1; then
  echo "⚠️  gh CLI 미설치 — PR 자동 생성 스킵"
  echo "    설치: https://cli.github.com/"
  echo "    또는 컨테이너 rebuild: docs/runbooks/dev_environment_auth.md"
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

### `/finq` 의 PR 자동화는 어떻게 다른가

`/fin` 과 동일한 PR 로직이지만 사용 의도가 다릅니다:

- **`/fin`**: CI 통과 후 PR 생성/갱신 → 머지 준비 완료 신호.
- **`/finq`**: WIP commit + PR 생성/갱신 → 백업·동기화 목적. 머지 전에 반드시 `/fin` 으로 CI 한 번 + PR body 확인.

**WIP 사용 케이스**:
- 작업 중간 백업 (집에서 → 사무실에서 같은 브랜치 이어서 작업)
- 진행 상황을 PR 페이지에서 시각화 (다른 사람이 in-progress draft 보고 의견)
- 실험 코드 push (CI 통과 안 해도 일단 보존)

`/finq` 로 만든 PR은 자연스럽게 draft 처럼 다뤄지지만 명시적 draft 플래그는 안 붙임 — 운영자가 GitHub UI 에서 "Convert to draft" 토글 권장.

---

## 4. ✅ Completion Message

Output after all steps complete:

```
✅ /finq 완료! (Quick mode - CI 생략)

📄 Living Documents 동기화 완료 (/ms.up-docs)
📝 dev_daily.md 업데이트 완료
💾 커밋: [생성한 메시지]
🚀 Push 완료 (또는 실패 시 에러 메시지)
🔀 PR: [PR URL] (생성 또는 갱신 / 실패 시 안내)

⚠️ CI 체크를 생략했습니다. 머지 전에 반드시:
   1. '/fin' 또는 'make ci' 로 검증
   2. GitHub Actions 결과 확인
   3. PR body 검토 (docs/PR_*_BODY.md)
```

---

## ⚠️ Important Notes

1. **/ms.up-docs integration (Quick mode)**:
   - **NEW**: Step 1 auto-runs `/ms.up-docs --docs=dev`
   - dev_daily.md auto-updates (based on Git diff)
   - Quick TAG chain integrity validation (detailed validation in /fin)
   - If no staged changes, show warning and proceed (fallback to manual update)
   - **Performance**: Process only staged changes for speed optimization (~2 seconds)

2. **When updating dev_daily.md** (fallback only):
   - Never delete existing content
   - Only append to today's date section
   - Write Focus only when creating today's section for first time

3. **CI skipped**:
   - This command skips CI checks for fast commits
   - Perform code quality validation later with `/fin` or `make ci`
   - Suitable for Work In Progress (WIP) commits

4. **Git behavior**:
   - Handles same as Makefile's finish target (except CI)
   - On commit failure, only show error message and proceed
   - On push failure, only show error message and complete workflow

5. **Use cases**:
   - Backup during work
   - When need to push quickly to remote
   - When only documentation changed
   - Experimental code commits

6. **Workflow sequence (UPDATED)**:
   ```
   /ms.up-docs --docs=dev  # Step 1: Sync Living Docs (Quick)
   ↓
   (Review dev_daily.md)   # Step 2: Fallback only
   ↓
   (Update README.md)      # Step 2.5: Optional
   ↓
   git commit && push      # Step 3: Commit & push (Skip CI)
   ↓
   gh pr create / edit     # Step 3.5: PR auto-create (NEW, idempotent)
   ↓
   (사람이 PR 검토 + 머지)  # Manual handoff to GitHub UI (CI 검증 후)
   ```

7. **/fin vs /finq differences**:
   - `/fin`: **Full** - /ms.up-docs → CI → commit → push → PR auto-create
   - `/finq`: **Quick** - /ms.up-docs (staged only) → commit → push → PR auto-create (skip CI)
   - TAG validation: /fin is detailed, /finq is quick scan
   - API docs: /fin can sync all, /finq only staged changes
   - **PR 의도**: `/fin` = "머지 준비 완료" / `/finq` = "WIP 백업·동기화"

8. **Auth dependency**: Step 3 (push) + Step 3.5 (PR) 는 컨테이너 안에서 호스트의 SSH agent + gh CLI auth 를 통해 동작. 호스트 셋업 미완료 시 친절한 안내 출력 후 commit은 보존. 셋업 절차: [`docs/runbooks/dev_environment_auth.md`](../../docs/runbooks/dev_environment_auth.md).

9. **PR body 자동 탐지**: `docs/PR_*_BODY.md` 패턴 (예: `PR_014_BODY.md`, `PR_015_BODY.md`) 중 가장 최근 mtime 파일을 자동 사용. 없으면 마지막 commit body fallback.

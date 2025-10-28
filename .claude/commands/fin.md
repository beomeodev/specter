---
description: "Finish workflow: sync docs → update daily log → CI checks → commit & push"
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
- **Validate TAG chains**: Verify @SPEC → @TEST → @CODE integrity
- **Sync API docs** (if staged changes exist): Generate/update `docs/api/{TAG}.md`

**Example output**:
```
✅ Document sync complete

📦 Files Updated:
- docs/dev_daily.md (appended)
- docs/api/AUTH-001.md (updated)

📋 TAG Integrity: 95.0% (23/24 complete chains)

⏱️ Duration: 3.2 seconds
```

**Error handling**:
- **No staged changes**: ⚠️ Show warning and proceed (fallback to manual dev_daily.md update)
- **Low TAG integrity** (<80%): ⚠️ Show warning but continue workflow

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

**Agent Delegation**: This step uses the **quality-gate** agent (Haiku model) to perform TRUST validation before committing:
- Test coverage ≥85% (MANDATORY)
- All tests passing
- Zero type errors
- Zero lint warnings
- TAG integrity validation

Execute the following command to validate code quality:

```bash
make ci
```

**CI includes**:
- `black --check .` (Code formatting)
- `isort --check-only .` (Import sorting)
- `ruff check .` (Linting)
- `mypy src/` (Type checking)
- `pytest -v --cov=src` (Tests with ≥85% coverage)

**Result handling**:
- ✅ **Pass**: Proceed to next step
- ❌ **Fail**: Display specific error message and **STOP** (don't commit)

---

## 4. 💾 Git Commit and Push

### Pre-commit Hook handling strategy

**Problem**: Pre-commit hooks or IDE auto-format modify files after commit, making git state dirty

**Solution**: Run pre-commit first before committing to complete formatting, with error/warning logging

```bash
# 1. Initial git add
git add .

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

  # Hook may modify files, so add again
  git add .
fi

# 3. git commit (커밋 메시지 생성)
git commit -m "생성한_커밋_메시지"

# 4. git push
git push
```

**Why this works**:
- Pre-commit hooks (ruff-format, etc.) run and modify files
- Modified files are re-staged with second `git add .`
- Commit captures all formatting changes
- No dirty state after commit
- **Errors/warnings logged to `docs/log/pre-commit/` for later review**

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
- **When push fails**: Display `❌ Push failed` (with error details)

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
```

---

## ⚠️ Important Notes

1. **/ms.up-docs integration**:
   - **NEW**: Step 1 auto-runs `/ms.up-docs --docs=dev`
   - dev_daily.md auto-updates (based on Git diff)
   - Automatic TAG chain integrity validation
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
   ```

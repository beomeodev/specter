---
description: "Quick finish: sync docs → update daily log → commit & push (NO CI checks)"
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
- **Validate TAG chains**: Verify @SPEC → @TEST → @CODE integrity (quick scan)
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

📋 TAG Integrity: 95.0% (quick scan)

⏱️ Duration: 1.8 seconds
```

**Error handling**:
- **No staged changes**: ⚠️ Show warning and proceed (fallback to manual dev_daily.md update)
- **Low TAG integrity** (<80%): ⚠️ Show warning but continue workflow (validate later with /fin)

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
- `wip`: Work In Progress

**Example**:
```
wip(strategy): MACD 신호 생성 로직 작업 중

- 기본 구조 구현
- 테스트 작성 필요
```

### Error handling
- **When nothing to commit**: Display `⚠️ Nothing to commit` and proceed
- **When push fails**: Display `❌ Push failed` (with error details)

---

## 4. ✅ Completion Message

Output after all steps complete:

```
✅ /finq 완료! (Quick mode - CI 생략)

📄 Living Documents 동기화 완료 (/ms.up-docs)
📝 dev_daily.md 업데이트 완료
💾 커밋: [생성한 메시지]
🚀 Push 완료 (또는 실패 시 에러 메시지)

⚠️ CI 체크를 생략했습니다. 나중에 'make ci' 또는 '/fin'으로 검증하세요.
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
   ```

7. **/fin vs /finq differences**:
   - `/fin`: **Full** - /ms.up-docs → CI → commit → push
   - `/finq`: **Quick** - /ms.up-docs (staged only) → commit → push (skip CI)
   - TAG validation: /fin is detailed, /finq is quick scan
   - API docs: /fin can sync all, /finq only staged changes

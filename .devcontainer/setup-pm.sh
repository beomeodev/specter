#!/bin/bash
# ============================================================================
# Project Tools Setup
# ============================================================================
# 설치되는 명령어:
#   pm = Project Manager
#   np = New Project
#
# 지원 환경:
#   - macOS zsh/bash
#   - Linux zsh/bash
#   - Windows WSL2 bash/zsh
#
# 비권장:
#   - Native Windows PowerShell / CMD
#
# 설치:
#   bash setup-pm.sh
#   exec $SHELL -l
#
# 사용:
#   np myapp map
#   pm map cc
#   pm map cx
#   pm map cr
#   pm map gm
# ============================================================================

set -euo pipefail

GITHUB_USER="beomeodev"
BIN_DIR="$HOME/.local/bin"
NP_BIN="$BIN_DIR/np"
MANAGED_START="# >>> project-tools managed block >>>"
MANAGED_END="# <<< project-tools managed block <<<"

echo "🚀 Project Tools 설치 시작..."

mkdir -p "$BIN_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3가 필요합니다."
  exit 1
fi

existing_np="$(command -v np 2>/dev/null || true)"
if [ -n "$existing_np" ] && [ "$existing_np" != "$NP_BIN" ]; then
  echo "⚠️ 기존 np 명령이 있습니다: $existing_np"
  echo "   설치 후 ~/.local/bin이 PATH 앞쪽에 있으면 새 np가 우선됩니다."
fi

# ============================================================================
# np 실행 파일 설치
# ============================================================================

cat > "$NP_BIN" <<'NP_SCRIPT'
#!/bin/bash
# ============================================================================
# np - New Project
# ============================================================================
# Specter 템플릿을 기반으로 새 프로젝트를 생성한다.
#
# 사용법:
#   np <project_name> <ticker> [template_source]
#
# 예시:
#   np myapp map
#   np airchanger acp
#   np myapp map ~/projects/spt
#   np myapp map git@github.com:beomeodev/specter.git
# ============================================================================

set -euo pipefail

GITHUB_USER="beomeodev"
SPECTER_TEMPLATE_REPO="${SPECTER_TEMPLATE_REPO:-git@github.com:beomeodev/specter.git}"

fail() {
  echo "❌ $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "필수 명령어가 없습니다: $1"
}

# 새 프로젝트를 /ms.sync 브로드캐스트 등록부(~/.claude/specter-sync.json)에 등록한다.
# 등록부는 SPECTER 레포 밖(호스트 ~/.claude, 전 컨테이너 공유 마운트)에 두므로
# 공개 템플릿을 클론한 제3자에게는 만들어지지 않는다. 등록 실패가 np를 막지 않는다.
register_sync_target() {
  python3 - "$PROJECT_NAME" "$REPO_SSH" "$SPECTER_TEMPLATE_REPO" <<'PY' || echo "⚠️ specter-sync 등록 실패 — SPECTER에서 수동 등록: python scripts/specter/specter_sync.py register $REPO_SSH"
import json
import sys
from pathlib import Path

name, repo, template_repo = sys.argv[1:4]
registry_path = Path.home() / ".claude" / "specter-sync.json"
if registry_path.exists():
    registry = json.loads(registry_path.read_text())
else:
    registry = {"source": template_repo, "targets": []}


def norm(url: str) -> str:
    u = url.strip()
    if u.startswith("git@github.com:"):
        u = "https://github.com/" + u[len("git@github.com:"):]
    return u.removesuffix(".git").rstrip("/")


targets = registry.setdefault("targets", [])
if any(norm(t.get("repo", "")) == norm(repo) for t in targets):
    print(f"ℹ️ specter-sync 등록부에 이미 있음: {repo}")
else:
    targets.append({"name": name, "repo": repo})
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n")
    print(f"✅ specter-sync 등록 완료: {name} -> {repo}")
PY
}

PROJECT_NAME="${1:-}"
TICKER="${2:-}"
TEMPLATE_ARG="${3:-}"

if [ -z "$PROJECT_NAME" ] || [ -z "$TICKER" ]; then
  cat <<'USAGE'
❌ 사용법: np <project_name> <ticker> [template_source]

예시:
  np myapp map
  np airchanger acp
  np myapp map ~/projects/spt
  np myapp map git@github.com:beomeodev/specter.git
USAGE
  exit 1
fi

case "$PROJECT_NAME" in
  *[!A-Za-z0-9._-]*)
    fail "project_name에는 영문/숫자/점/언더스코어/하이픈만 사용하세요: $PROJECT_NAME"
    ;;
esac

case "$TICKER" in
  [A-Za-z][A-Za-z0-9][A-Za-z0-9]) ;;
  *) fail "ticker는 3글자 영문/숫자 조합을 권장합니다. 예: map, acp, sab" ;;
esac

TICKER="$(echo "$TICKER" | tr '[:upper:]' '[:lower:]')"

for cmd in git gh rsync python3; do
  need_cmd "$cmd"
done

if ! gh auth status >/dev/null 2>&1; then
  fail "GitHub CLI 로그인이 필요합니다. 먼저 실행: gh auth login"
fi

if ! git config --get user.name >/dev/null 2>&1 || ! git config --get user.email >/dev/null 2>&1; then
  cat <<'GITCFG'
❌ Git commit용 user.name / user.email 설정이 없습니다.

예시:
  git config --global user.name "Your Name"
  git config --global user.email "you@example.com"
GITCFG
  exit 1
fi

# PROJECT_ROOT 결정:
#   1. 사용자가 export한 PROJECT_ROOT
#   2. WSL2 기본 경로
#   3. macOS/Linux 기본 경로
if [ -n "${PROJECT_ROOT:-}" ]; then
  PROJECT_ROOT_RESOLVED="$PROJECT_ROOT"
elif [ -d "/mnt/d/underway_project" ]; then
  PROJECT_ROOT_RESOLVED="/mnt/d/underway_project"
else
  PROJECT_ROOT_RESOLVED="$HOME/projects"
fi

mkdir -p "$PROJECT_ROOT_RESOLVED"

PROJECT_DIR="$PROJECT_ROOT_RESOLVED/$PROJECT_NAME"
TICKER_LINK="$PROJECT_ROOT_RESOLVED/$TICKER"
REPO_SSH="git@github.com:${GITHUB_USER}/${PROJECT_NAME}.git"

# Specter 템플릿 source 결정:
#   기본값: GitHub의 Specter repo를 fresh clone
#   예외:
#     - 세 번째 인자가 로컬 디렉토리면 그 디렉토리를 rsync 복사
#     - 세 번째 인자가 git URL이면 해당 repo를 clone
#     - SPECTER_TEMPLATE_DIR가 있으면 로컬 디렉토리 복사
#     - SPECTER_TEMPLATE_REPO가 있으면 해당 repo clone
TEMPLATE_MODE="clone"
TEMPLATE_SOURCE="$SPECTER_TEMPLATE_REPO"

if [ -n "$TEMPLATE_ARG" ]; then
  if [ -d "$TEMPLATE_ARG" ]; then
    TEMPLATE_MODE="local"
    TEMPLATE_SOURCE="$TEMPLATE_ARG"
  else
    TEMPLATE_MODE="clone"
    TEMPLATE_SOURCE="$TEMPLATE_ARG"
  fi
elif [ -n "${SPECTER_TEMPLATE_DIR:-}" ]; then
  [ -d "$SPECTER_TEMPLATE_DIR" ] || fail "SPECTER_TEMPLATE_DIR 디렉토리 없음: $SPECTER_TEMPLATE_DIR"
  TEMPLATE_MODE="local"
  TEMPLATE_SOURCE="$SPECTER_TEMPLATE_DIR"
elif [ -n "${SPECTER_TEMPLATE_REPO:-}" ]; then
  TEMPLATE_MODE="clone"
  TEMPLATE_SOURCE="$SPECTER_TEMPLATE_REPO"
fi
[ ! -e "$PROJECT_DIR" ] || fail "이미 존재하는 프로젝트 디렉토리입니다: $PROJECT_DIR"

if [ "$PROJECT_NAME" != "$TICKER" ] && [ -e "$TICKER_LINK" ]; then
  fail "이미 존재하는 ticker 경로입니다: $TICKER_LINK"
fi

REPO_EXISTS=0
if gh repo view "${GITHUB_USER}/${PROJECT_NAME}" >/dev/null 2>&1; then
  REPO_EXISTS=1
fi

cat <<SUMMARY
🚀 프로젝트 준비

PROJECT_NAME : $PROJECT_NAME
TICKER       : $TICKER
GITHUB_USER  : $GITHUB_USER
PROJECT_ROOT : $PROJECT_ROOT_RESOLVED
REPO_EXISTS  : $REPO_EXISTS
TEMPLATE_MODE: $TEMPLATE_MODE
TEMPLATE_SRC : $TEMPLATE_SOURCE
PROJECT_DIR  : $PROJECT_DIR
TICKER_LINK  : $TICKER_LINK
REPO_SSH     : $REPO_SSH

SUMMARY

if [ "$REPO_EXISTS" = "1" ]; then
  echo "📥 기존 GitHub repo clone..."
  git clone "$REPO_SSH" "$PROJECT_DIR"
elif [ "$TEMPLATE_MODE" = "clone" ]; then
  echo "📥 Specter template repo clone..."
  git clone --depth 1 "$TEMPLATE_SOURCE" "$PROJECT_DIR"
  rm -rf "$PROJECT_DIR/.git"
else
  echo "📁 로컬 Specter 템플릿 복사..."
  mkdir -p "$PROJECT_DIR"
  rsync -a \
    --exclude ".git" \
    --exclude ".env" \
    --exclude ".venv" \
    --exclude "__pycache__" \
    --exclude ".pytest_cache" \
    --exclude ".mypy_cache" \
    --exclude ".ruff_cache" \
    --exclude "node_modules" \
    --exclude ".DS_Store" \
    "$TEMPLATE_SOURCE/" "$PROJECT_DIR/"
fi

MAKEFILE="$PROJECT_DIR/.devcontainer/Makefile"
if [ -f "$MAKEFILE" ]; then
  python3 - "$MAKEFILE" "$TICKER" "$REPO_SSH" <<'PY'
import re
import sys
from pathlib import Path

makefile = Path(sys.argv[1])
ticker = sys.argv[2]
repo_ssh = sys.argv[3]
text = makefile.read_text()

if not re.search(r"^PROJ_TICKER\s*:=", text, flags=re.M):
    raise SystemExit("❌ Makefile에 PROJ_TICKER := 라인이 없습니다.")
if not re.search(r"^PROJ_REPO\s*:=", text, flags=re.M):
    raise SystemExit("❌ Makefile에 PROJ_REPO := 라인이 없습니다.")

text = re.sub(
    r"^PROJ_TICKER\s*:=\s*.*$",
    f"PROJ_TICKER := {ticker}",
    text,
    flags=re.M,
)
text = re.sub(
    r"^PROJ_REPO\s*:=\s*.*$",
    f"PROJ_REPO := {repo_ssh}",
    text,
    flags=re.M,
)
makefile.write_text(text)
print("✅ .devcontainer/Makefile 업데이트 완료")
PY
elif [ "$REPO_EXISTS" = "1" ]; then
  echo "ℹ️ .devcontainer/Makefile 없음: ticker/repo 자동 업데이트 건너뜀"
else
  fail ".devcontainer/Makefile을 찾지 못했습니다: $MAKEFILE"
fi

cd "$PROJECT_DIR"

if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "✅ .env.example → .env 생성 완료"
  else
    touch .env
    echo "✅ 빈 .env 생성 완료"
  fi
fi

if [ "$PROJECT_NAME" != "$TICKER" ]; then
  ln -s "$PROJECT_DIR" "$TICKER_LINK"
  echo "✅ ticker 심볼릭 링크 생성: $TICKER_LINK -> $PROJECT_DIR"
else
  echo "ℹ️ project_name과 ticker가 같아서 심볼릭 링크 생략"
fi

if [ "$REPO_EXISTS" = "1" ]; then
  register_sync_target
  cat <<DONE

✅ 기존 프로젝트 clone 완료

실제 프로젝트 경로:
  $PROJECT_DIR

ticker 경로:
  $TICKER_LINK

GitHub repo:
  $REPO_SSH
DONE
  if [ -f "$MAKEFILE" ]; then
    cat <<DONE

이제 실행:
  pm $TICKER cc   # Claude Code
  pm $TICKER cx   # Codex
  pm $TICKER cr   # Codex resume
  pm $TICKER gm   # Antigravity (agy)
DONE
  else
    echo ""
    echo "ℹ️ pm 명령은 .devcontainer/Makefile이 있을 때만 사용할 수 있습니다."
  fi
  exit 0
fi

git init
git branch -M main
git add .

if git diff --cached --quiet; then
  git commit --allow-empty -m "chore: initialize project from Specter template"
else
  git commit -m "chore: initialize project from Specter template"
fi

echo "🔐 GitHub private repo 생성..."
gh repo create "${GITHUB_USER}/${PROJECT_NAME}" \
  --private \
  --source=. \
  --remote=origin

git remote set-url origin "$REPO_SSH"

echo "🚀 GitHub push..."
git push -u origin main

register_sync_target

cat <<DONE

✅ 프로젝트 준비 완료

실제 프로젝트 경로:
  $PROJECT_DIR

pm용 ticker 경로:
  $TICKER_LINK

GitHub repo:
  $REPO_SSH

이제 실행:
  pm $TICKER cc   # Claude Code
  pm $TICKER cx   # Codex
  pm $TICKER cr   # Codex resume
  pm $TICKER gm   # Antigravity (agy)
DONE
NP_SCRIPT

chmod +x "$NP_BIN"

echo "✅ np 설치 완료: $NP_BIN"

# ============================================================================
# shell rc에 pm 함수 + PATH 등록
# ============================================================================

# macOS Bash 3.2 호환성을 위해 here-doc을 command substitution 안에 넣지 않는다.
# 대신 임시 파일에 managed block을 쓴 뒤, rc 파일에 append한다.
RC_BLOCK_FILE="$(mktemp "${TMPDIR:-/tmp}/project-tools-rc-block.XXXXXX")"
trap 'rm -f "$RC_BLOCK_FILE"' EXIT

cat > "$RC_BLOCK_FILE" <<'RC_BLOCK'
# >>> project-tools managed block >>>
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin:$PATH" ;;
esac

# ======= Project Manager (pm) =======
# 사용법:
#   pm <project_ticker> <agent_command>
#
# 예시:
#   pm spt cc
#   pm sab cx
#   pm map gm
function pm() {
    if [ -z "${1:-}" ] || [ -z "${2:-}" ]; then
        echo "❌ 사용법: pm <project_ticker> <agent_command>"
        echo ""
        echo "예시:"
        echo "  pm spt cc"
        echo "  pm map cx"
        echo "  pm map gm"
        return 1
    fi

    local ticker="$1"
    local command="$2"
    local proj_root="${PROJECT_ROOT:-}"

    if [ -z "$proj_root" ]; then
        if [ -d "/mnt/d/underway_project" ]; then
            proj_root="/mnt/d/underway_project"
        elif [ -d "$HOME/projects" ]; then
            proj_root="$HOME/projects"
        else
            echo "❌ PROJECT_ROOT 미설정 + 기본 경로 자동 감지 실패"
            echo ""
            echo "해결 방법: mkdir -p ~/projects"
            echo "또는 ~/.zshrc / ~/.bashrc에 추가:"
            echo "  export PROJECT_ROOT=\"/your/projects/path\""
            return 1
        fi
    fi

    if [ ! -d "$proj_root/$ticker" ]; then
        echo "❌ 프로젝트 디렉토리 없음: $proj_root/$ticker"
        echo "새 프로젝트 생성 예시: np myapp map"
        return 1
    fi

    cd "$proj_root/$ticker" && make -C .devcontainer -f Makefile "${ticker}${command}"
}
# <<< project-tools managed block <<<
RC_BLOCK

install_block_to_rc() {
    local rc_file="$1"
    [ -f "$rc_file" ] || return 0

    if grep -q "$MANAGED_START" "$rc_file" 2>/dev/null; then
        python3 - "$rc_file" <<'PY'
import re
import sys
from pathlib import Path

p = Path(sys.argv[1])
s = p.read_text()
s = re.sub(
    r"\n?# >>> project-tools managed block >>>.*?# <<< project-tools managed block <<<\n?",
    "\n",
    s,
    flags=re.S,
)
p.write_text(s.rstrip() + "\n")
PY
    fi

    printf "\n" >> "$rc_file"
    cat "$RC_BLOCK_FILE" >> "$rc_file"
    printf "\n" >> "$rc_file"
    echo "✅ shell 설정 업데이트: $rc_file"
}

updated_any="false"

if [ -f "$HOME/.zshrc" ]; then
    install_block_to_rc "$HOME/.zshrc"
    updated_any="true"
fi

if [ -f "$HOME/.bashrc" ]; then
    install_block_to_rc "$HOME/.bashrc"
    updated_any="true"
fi

if [ "$updated_any" = "false" ]; then
    touch "$HOME/.zshrc"
    install_block_to_rc "$HOME/.zshrc"
fi

cat <<FINAL

🎉 설치 완료

지금 즉시 활성화:
  exec \$SHELL -l

또는 현재 셸에 맞게:
  source ~/.zshrc   # zsh인 경우
  source ~/.bashrc  # bash인 경우

사용 예시:
  np myapp map
  pm map cc
  pm map cx
  pm map cr
  pm map gm
FINAL

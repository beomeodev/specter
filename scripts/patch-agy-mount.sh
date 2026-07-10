#!/bin/bash
# patch-agy-mount.sh — 일회성 마이그레이션 유틸 (호스트에서 실행).
#
# ~/projects/*/.devcontainer/docker-compose.yml 의 agy 자격증명 마운트를
#   ${HOME}/.config/agy:/home/dev/.config/agy   (빈 디렉토리 — 잘못된 경로)
# 에서
#   ${HOME}/.gemini:/home/dev/.gemini           (agy 실제 앱 디렉토리)
# 로 교체한다. mkdir 힌트 주석도 함께 갱신한다.
#
# 실행 (호스트 셸에서):
#   bash ~/projects/specter/scripts/patch-agy-mount.sh
#
# 하는 일:  compose 파일 텍스트 교체 + 호스트 ~/.gemini 생성. 그게 전부다.
# 안 하는 일: 컨테이너 재생성(라이브 세션 보호), git 커밋 — 둘 다 출력되는
#            안내대로 직접 실행한다.

set -euo pipefail

ROOT="${PROJECT_ROOT:-$HOME/projects}"

if [ ! -d "$ROOT" ]; then
  echo "❌ 프로젝트 루트 없음: $ROOT (PROJECT_ROOT로 재지정 가능)"
  exit 1
fi

mkdir -p "$HOME/.gemini"
echo "✅ 호스트 ~/.gemini 준비 완료"
echo

patched=()
already=()
missing=()

for compose in "$ROOT"/*/.devcontainer/docker-compose.yml; do
  [ -f "$compose" ] || continue
  # ticker 심볼릭 링크로 같은 프로젝트가 두 번 잡히는 것 방지
  [ -L "$(dirname "$(dirname "$compose")")" ] && continue

  name="$(basename "$(dirname "$(dirname "$compose")")")"
  result="$(python3 - "$compose" <<'PY'
import re
import sys
from pathlib import Path

p = Path(sys.argv[1])
text = p.read_text()

if "/home/dev/.gemini" in text:
    print("ALREADY")
    raise SystemExit

if ".config/agy" not in text:
    print("MISSING")
    raise SystemExit

text = re.sub(
    r"^(\s*)-\s*\$\{HOME\}/\.config/agy:/home/dev/\.config/agy\s*$",
    r"\1- ${HOME}/.gemini:/home/dev/.gemini",
    text,
    flags=re.M,
)
text = text.replace("mkdir -p ~/.config/agy", "mkdir -p ~/.gemini")
text = text.replace(
    "# Antigravity CLI(agy) 자격증명 영속화 (rebuild 후에도 로그인 유지).",
    "# Antigravity CLI(agy) 자격증명 영속화 — agy 앱 디렉토리(자격증명 포함)는\n"
    "      # ~/.gemini/antigravity-cli/ (Gemini CLI 계승 경로). ~/.codex와 동일 방식.\n"
    "      # 주의: agy 업데이트가 이 경로를 옮기면(예: ~/.agy) 에러 없이 \"컨테이너\n"
    "      # 재생성 후 OAuth 재로그인 요구\" 증상으로만 나타난다. 그때 컨테이너에서\n"
    "      # agy 실행 직후 `find ~ -maxdepth 3 -mmin -2 -type d`로 새 앱 디렉토리를\n"
    "      # 찾아 이 마운트를 그 경로로 바꿀 것 (2026-07-10 실측 방법).",
)
p.write_text(text)
print("PATCHED")
PY
)"

  case "$result" in
    PATCHED) patched+=("$name"); echo "🔧 $name: 교체 완료" ;;
    ALREADY) already+=("$name"); echo "✅ $name: 이미 ~/.gemini 마운트" ;;
    MISSING) missing+=("$name"); echo "⚠️  $name: agy 마운트 라인 없음 — 수동 확인 필요" ;;
  esac
done

echo
echo "===== 요약: 교체 ${#patched[@]} / 이미완료 ${#already[@]} / 라인없음 ${#missing[@]} ====="

if [ "${#patched[@]}" -gt 0 ]; then
  cat <<'NEXT'

다음 단계 (교체된 프로젝트마다, 다음에 그 프로젝트를 쓸 때 해도 됨):
  1. 컨테이너 재생성 — 마운트 변경은 restart로는 반영 안 됨:
       make -C <프로젝트>/.devcontainer down
     이후 평소처럼 pm <ticker> cc 로 올리면 새 마운트로 재생성됨.
     (지금 라이브 세션이 도는 컨테이너는 세션 끝나고 할 것)
  2. 아무 컨테이너에서 agy 로그인 1회 → 호스트 ~/.gemini에 저장되어 전 프로젝트 공유.
  3. compose 변경은 각 repo에 uncommitted로 남음 — 다음 커밋 때 함께 반영.
NEXT
fi

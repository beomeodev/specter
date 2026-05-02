#!/bin/bash
# ============================================================================
# Project Manager (pm) 셋업 스크립트
# ============================================================================
# 새 머신에서 한 번만 실행하면 'pm' 명령어가 활성화됨.
# 지원 셸: bash, zsh
# 지원 OS: WSL2 (Windows), macOS, Linux
#
# 사용법:
#   bash setup-pm.sh
#
# 설치 후 활성화:
#   source ~/.zshrc   (또는 ~/.bashrc)
#
# 사용 예시:
#   pm spt cc   → SPECTER 프로젝트 디렉토리로 이동 후 Claude Code 실행
#   pm sab cx   → spade-ace-backtester로 이동 후 Codex 실행
#   pm sab cr   → 마지막 Codex 세션 이어가기
# ============================================================================

echo "🚀 Project Manager (pm) 함수 설치 시작..."

# ============================================================================
# pm 함수 본체
# ----------------------------------------------------------------------------
# PROJECT_ROOT 결정 우선순위:
#   1. 사용자가 export 한 $PROJECT_ROOT 환경변수 (최우선)
#   2. WSL2 자동 감지: /mnt/d/underway_project 디렉토리 존재 시
#   3. Mac/Linux 자동 감지: $HOME/projects 디렉토리 존재 시
#   4. 위 모두 실패 시 에러 메시지 출력 후 종료
#
# 단일 인용부호로 감싸서 변수($1, $2 등)가 즉시 치환되지 않게 함.
# .bashrc/.zshrc에 함수 정의 그대로 기록되어야 하기 때문.
# ============================================================================
PM_FUNCTION='
# ======= Project Manager (pm) =======
# 사용법: pm <project_ticker> <agent_command>
# 예시: pm spt cc  → SPECTER 디렉토리로 cd 후 make sptcc 실행
function pm() {
    # 인자 검증
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "❌ 사용법: pm <project> <command>"
        echo "예시: pm spt cc"
        return 1
    fi

    # 프로젝트 루트 결정 (환경변수 우선, 없으면 OS 자동 감지)
    local proj_root="${PROJECT_ROOT}"
    if [ -z "$proj_root" ]; then
        if [ -d "/mnt/d/underway_project" ]; then
            # WSL2 환경 (Windows D 드라이브 마운트)
            proj_root="/mnt/d/underway_project"
        elif [ -d "$HOME/projects" ]; then
            # Mac / Linux 환경
            proj_root="$HOME/projects"
        else
            echo "❌ PROJECT_ROOT 미설정 + 기본 경로 자동 감지 실패"
            echo ""
            echo "   해결 방법 (둘 중 하나 선택):"
            echo "   (1) 기본 디렉토리 생성: mkdir -p ~/projects"
            echo "   (2) ~/.zshrc 또는 ~/.bashrc에 다음 한 줄 추가:"
            echo "       export PROJECT_ROOT=\"/your/projects/path\""
            return 1
        fi
    fi

    # 프로젝트 디렉토리 존재 확인
    if [ ! -d "$proj_root/$1" ]; then
        echo "❌ 프로젝트 디렉토리 없음: $proj_root/$1"
        return 1
    fi

    # 프로젝트로 이동 후 .devcontainer/Makefile의 단축어 실행
    # 단축어 규칙: <ticker><command> 예: sptcc, sabcx
    cd "$proj_root/$1" && make -C .devcontainer -f Makefile ${1}${2}
}
'

# ============================================================================
# 셸 설정 파일에 pm 함수 추가 (bash/zsh 둘 다 감지하여 둘 다 추가)
# ----------------------------------------------------------------------------
# 멱등성(idempotent) 보장: 이미 추가되어 있으면 중복 추가하지 않음.
# ============================================================================
ADDED_TO=""

# bash 설정 파일 처리 (Linux 기본 셸)
if [ -f ~/.bashrc ]; then
    if ! grep -q "function pm()" ~/.bashrc 2>/dev/null; then
        echo "$PM_FUNCTION" >> ~/.bashrc
        ADDED_TO="~/.bashrc"
    else
        echo "⚠️  pm 함수가 이미 ~/.bashrc에 존재 (건너뜀)"
    fi
fi

# zsh 설정 파일 처리 (macOS 기본 셸, 일부 Linux 사용자)
if [ -f ~/.zshrc ]; then
    if ! grep -q "function pm()" ~/.zshrc 2>/dev/null; then
        echo "$PM_FUNCTION" >> ~/.zshrc
        if [ -z "$ADDED_TO" ]; then
            ADDED_TO="~/.zshrc"
        else
            ADDED_TO="$ADDED_TO and ~/.zshrc"
        fi
    else
        echo "⚠️  pm 함수가 이미 ~/.zshrc에 존재 (건너뜀)"
    fi
fi

# ============================================================================
# 설치 결과 리포트
# ============================================================================
if [ -n "$ADDED_TO" ]; then
    echo "✅ pm 함수 추가 완료: $ADDED_TO"
    echo ""
    echo "지금 즉시 활성화하려면:"
    if [[ "$ADDED_TO" == *"bashrc"* ]]; then
        echo "  source ~/.bashrc"
    fi
    if [[ "$ADDED_TO" == *"zshrc"* ]]; then
        echo "  source ~/.zshrc"
    fi
else
    echo "ℹ️  pm 함수가 이미 설정되어 있음 (변경 없음)"
fi

# ============================================================================
# 현재 환경의 PROJECT_ROOT 자동 감지 결과 안내
# ----------------------------------------------------------------------------
# 사용자가 셋업 후 어떤 경로가 잡혔는지 확인할 수 있도록 표시.
# ============================================================================
echo ""
echo "📂 PROJECT_ROOT 자동 감지 결과:"
if [ -n "$PROJECT_ROOT" ]; then
    echo "   $PROJECT_ROOT (환경변수에서 가져옴)"
elif [ -d "/mnt/d/underway_project" ]; then
    echo "   /mnt/d/underway_project (WSL2 환경 감지)"
elif [ -d "$HOME/projects" ]; then
    echo "   $HOME/projects (Mac/Linux 환경 감지)"
else
    echo "   ⚠️  자동 감지 실패 - 첫 'pm' 실행 시 에러 발생함"
    echo ""
    echo "   다음 중 하나로 해결:"
    echo "   (1) mkdir -p ~/projects"
    echo "   (2) ~/.zshrc 또는 ~/.bashrc에 추가:"
    echo "       export PROJECT_ROOT=\"/your/projects/path\""
fi

# ============================================================================
# 사용 예시 안내
# ============================================================================
echo ""
echo "🔧 사용 예시:"
echo "  pm spt cc  # SPECTER 시작 + Claude Code 실행"
echo "  pm sab cx  # spade-ace-backtester 시작 + Codex 실행"
echo "  pm sab cr  # 마지막 Codex 세션 이어가기"
echo "  pm sab gm  # spade-ace-backtester 시작 + Gemini 실행"
echo ""
echo "🎉 셋업 완료!"

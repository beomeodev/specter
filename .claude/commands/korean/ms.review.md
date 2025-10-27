---
description: "구현 후 코드 품질 검토(구현 후 단계)"
---

# /ms.review - 코드 품질 검토

`/ms.implement` 완료 후 심층 코드 품질 검토를 수행합니다. 코드 디자인, 유지 관리성 및 모범 사례에 중점을 둡니다(요구 사항 검증이 아님 - 이는 `/speckit.checklist`임).

## 개요

**목적**: `/ms.implement` 이후 구현된 코드 품질 검토

**대상이 아님**:
- ❌ 요구 사항 검증 ( `/speckit.checklist` 사용)
- ❌ TRUST 메트릭 ( `/ms.analyze` 사용)
- ❌ 빌드/테스트/린트 검사 ( `/ms.analyze` 레벨 2 사용)

**대상**:
- ✅ 코드 디자인 품질 (아키텍처, 패턴, DRY)
- ✅ 유지 관리성 (이름 지정, 주석, 오류 처리)
- ✅ 성능 문제 (N+1 쿼리, 불필요한 계산)
- ✅ 보안 심층 분석 (인증 격차, 로깅 누출, 오류 노출)
- ✅ 테스트 품질 (AAA 패턴, 경계 테스트, 모의 과용)

## 워크플로 위치

```
/ms.implement → /ms.review → /fin
```

**실행 시기**: 모든 작업을 구현한 후, 최종 커밋 전

## 실행 단계

### 1단계: 전제 조건 확인

전제 조건 스크립트를 실행하여 컨텍스트를 가져옵니다.

```bash
src/lib/scripts/check-prerequisites.sh --json --require-spec --require-plan --include-tasks
```

JSON 출력을 구문 분석하여 다음을 추출합니다.
- `REPO_ROOT`: 리포지토리 루트 경로
- `FEATURE_DIR`: 기능 디렉토리 (예: `specs/001-auth-spec/`)
- `AVAILABLE_DOCS`: 사용 가능한 문서 목록 (spec.md, plan.md, tasks.md 등)

**필수 파일**:
- ✅ `spec.md` (도메인 용어용)
- ✅ `plan.md` (아키텍처 참조용)
- ✅ 구현된 코드 파일 (src/, tests/)

**누락된 경우**: 오류를 표시하고 `/ms.specify` 또는 `/ms.plan` 실행을 제안합니다.

--- 

### 2단계: 컨텍스트 로드(최적화 - 캐시됨)

```bash
declare -A CONTEXT_CACHE

load_context_documents() {
  CONTEXT_CACHE[spec_raw]=$(cat "$FEATURE_DIR/spec.md" 2>/dev/null || echo "")
  CONTEXT_CACHE[plan_raw]=$(cat "$FEATURE_DIR/plan.md" 2>/dev/null || echo "")
  CONTEXT_CACHE[constitution_raw]=$(cat .specify/memory/constitution.md 2>/dev/null || echo "")

  export DOMAIN_TERMS=$(echo "${CONTEXT_CACHE[spec_raw]}" | rg -o '(?<=## Domain Terminology).*?(?=##)' -U || true)
  export ARCH_LAYERS=$(echo "${CONTEXT_CACHE[plan_raw]}" | rg -o '(?<=## Architecture).*?(?=##)' -U || true)
  export SPEC_CONTENT="${CONTEXT_CACHE[spec_raw]}"
  export PLAN_CONTENT="${CONTEXT_CACHE[plan_raw]}"
}

load_context_documents
```

읽기: spec.md, plan.md, constitution.md (한 번, 메모리에 캐시됨)

--- 

### 1.5단계: 도구 가용성 확인(신규)

검토는 여러 외부 바이너리에 의존합니다. 미리 확인하고 사용할 수 없을 때 정상적으로 대체합니다.

```bash
command -v jq >/dev/null    || echo "⚠️ jq 누락 → JSON 집계 단계 건너뜀"
command -v rg >/dev/null    || { echo "❌ 패턴 스캔에 ripgrep 필요"; exit 1; }
command -v npx >/dev/null   || echo "⚠️ npx 누락 → eslint/jscpd 검사 건너뜀"
command -v radon >/dev/null || echo "⚠️ radon 누락 → Python 복잡성 스캔 건너뜀"
command -v jscpd >/dev/null || echo "⚠️ jscpd 누락 → 중복 감지 건너뜀"
```

각 정적 분석 단계가 중간에 실패하는 대신 단락할 수 있도록 나중에 조건문에 대한 가용성 플래그(예: `HAS_JQ=1`)를 저장합니다.

--- 

### 2.5단계: 의도 및 초점 헌장(신규)

검토를 고정하는 간결한 헌장을 작성합니다.

1.  `spec.md` 제약 조건, plan.md 아키텍처 및 헌법 가드레일에서 **주요 위험 도출**.
2.  전제 조건 JSON 및 최근 구현 작업에서 가져온 **검토 대상 목록**(파일, 구성 요소, 사용자 경로)을 나열합니다.
3.  검토에서 답해야 할 **최대 3개의 주요 질문**을 명시합니다(예: “인증 흐름이 여전히 토큰 순환 규칙을 따릅니까?”).

**출력**:

```
의도 및 초점 헌장 🧭
- 범위: {기능 요약}
- 필수 위험: {중요 경로 | 보안 | 성능 | 통합}
- 주요 질문:
  1. ...
  2. ...
  3. ...
```

나중에 보고하고 다시 실행 비교를 위해 헌장을 메모리에 저장합니다.

--- 

### 3단계: 스마트 파일 검색

```bash
discover_changed_files() {
  local BASE_REF="${1:-origin/main}"

  # 우선순위 1: Git diff
  CHANGED_FILES=$(git diff --name-only --diff-filter=ACMRTUXB ${BASE_REF}...HEAD 2>/dev/null \
    | rg '^(src|tests)/.*
(ts|js|py|tsx|jsx)$' || true)
  [ -n "$CHANGED_FILES" ] && echo "$CHANGED_FILES" && return 0

  # 우선순위 2: 스테이징된 파일
  CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACMRTUXB 2>/dev/null \
    | rg '^(src|tests)/.*
(ts|js|py|tsx|jsx)$' || true)
  [ -n "$CHANGED_FILES" ] && echo "$CHANGED_FILES" && return 0

  # 우선순위 3: 스모크 테스트(200개 파일)
  rg -l '' src tests 2>/dev/null | rg '\.(ts|js|py|tsx|jsx)$' | head -n 200
}

export CHANGED_FILES=$(discover_changed_files)
export CHANGED_TS=$(echo "$CHANGED_FILES" | rg '\.(ts|tsx|js|jsx)$' || true)
export CHANGED_PY=$(echo "$CHANGED_FILES" | rg '\.py$' || true)
```

--- 

### 3.5단계: 해시 기반 캐시

```bash
compute_file_hashes() {
  local targets="$1"
  local cache_file=".specify/review-hash.cache"

  [ -z "$targets" ] && echo "$targets" && return 0

  echo "$targets" | xargs -P "$(nproc)" -I{} sh -c 'echo "$(sha1sum "{}" 2>/dev/null | cut -d" " -f1)  {}"'
    | sort -k2 > .specify/review-hash.now 2>/dev/null || true

  if [ -f "$cache_file" ]; then
    comm -13 <(sort -k2 "$cache_file" 2>/dev/null || true) <(sort -k2 .specify/review-hash.now)
      | cut -d' ' -f2- > .specify/review-changed-by-hash.txt
    TRULY_CHANGED=$(cat .specify/review-changed-by-hash.txt)
  else
    TRULY_CHANGED="$targets"
  fi

  cp .specify/review-hash.now "$cache_file" 2>/dev/null || true
  echo "$TRULY_CHANGED"
}

export ANALYSIS_TARGETS=$(compute_file_hashes "$CHANGED_FILES")
```

--- 

### 4단계: 정적 분석(병렬)

```bash
run_parallel_static_analysis() {
  mkdir -p .specify/review
  (
    # 프로세스 1: jscpd (조건부 - 200 LOC 초과 파일만)
    {
      large_files=$(echo "$ANALYSIS_TARGETS" | xargs -I{} sh -c 'wc -l "{}" 2>/dev/null | awk "{if (\$1 > 200) print \$2}"' || true)
      if [ -n "$large_files" ] && command -v jscpd &>/dev/null; then
        npx jscpd $large_files --threshold 5 --format json --output .specify/review/jscpd.json 2>/dev/null || echo '{"duplicates":[]}' > .specify/review/jscpd.json
      else
        echo '{"duplicates":[],"skip":"no large files"}' > .specify/review/jscpd.json
      fi
    } &

    # 프로세스 2: eslint (JS/TS 복잡성)
    {
      if [ -n "$CHANGED_TS" ]; then
        npx eslint --cache --cache-location .specify/.eslintcache --cache-strategy content \
          --rule 'complexity: [error, 10]' --rule 'max-lines-per-function: [error, {max: 100}]' \
          --format json $CHANGED_TS > .specify/review/eslint.json 2>&1 || echo '[]' > .specify/review/eslint.json
      else
        echo '[]' > .specify/review/eslint.json
      fi
    } &

    # 프로세스 3: radon (Python 복잡성)
    {
      if [ -n "$CHANGED_PY" ]; then
        printf "%s\n" $CHANGED_PY | xargs -P "$(nproc)" -I{} radon cc -nb --json {} 2>/dev/null \
          | jq -s 'add // {}' > .specify/review/radon.json 2>/dev/null || echo '{}' > .specify/review/radon.json
      else
        echo '{}' > .specify/review/radon.json
      fi
    } &

    # 프로세스 4: ripgrep (패턴 감지)
    {
      run_consolidated_ripgrep
    } &

    wait
  )
}

run_parallel_static_analysis
```

#### C. 패턴 감지(단일 패스)

```bash
run_consolidated_ripgrep() {
  rg --json -n -e 'eval\(' -e '(console\.(log|debug|info|warn))' -e '(process\.env\.|os\.getenv)' \
    -e 'await.*for.*of' -e '\.map\(.*await' -e 'for.*for.*for' -e '\b[0-9]{3,}\b' \
    -e '(TODO|FIXME|XXX|HACK):' -e '(password|secret|token)\s*=\s*[""]' -e '(setTimeout|setInterval)\(' \
    --type-add 'code:*.{ts,js,py,tsx,jsx}' --type code --iglob '!**/*.snap' --iglob '!**/node_modules/**' \
    ${CHANGED_FILES:-src tests} > .specify/review-rg.ndjson 2>/dev/null || echo '{}' > .specify/review-rg.ndjson

  jq -r 'select(.type == "match") | {file: .data.path.text, line: .data.line_number, match: .data.lines.text}' \
    .specify/review-rg.ndjson > .specify/review-patterns.json 2>/dev/null || echo '[]' > .specify/review-patterns.json
}

run_consolidated_ripgrep
```

--- 

### 5단계: AI 기반 심층 분석

AI 판단을 사용하여 컨텍스트 인식 분석을 수행합니다.

**패턴 집계**(5.5단계용): 분석 중에 문제 패턴을 점진적으로 추적합니다. 동일한 문제 범주가 3회 이상 나타나면 시스템적인 것으로 표시합니다.

#### A. 이름 지정 품질 검토

**각 핵심 파일**(서비스, 모델, 컨트롤러)에 대해:

1.  **파일 내용 읽기**
2.  **추출**: 클래스 이름, 함수 이름, 변수 이름
3.  **spec.md와 비교**:
    *   함수 이름이 사양의 도메인 용어를 사용합니까?
    *   엔터티 이름이 data-model.md와 일치합니까?
    *   약어는 피합니까(업계 표준 제외: API, HTTP, JWT)?

**점수 매기기**:
- **높음**: 일반적인 이름 (예: `processData`, `handleRequest`, `doStuff`)
- **중간**: 일관성 없는 이름 지정 (예: `getUserData` 대 `fetchUser`)
- **낮음**: 단순화할 수 있는 장황한 이름

**출력 형식**:
```
H-001: src/services/user.service.ts:45의 일반적인 함수 이름 "processData"
  권장 사항: spec.md의 도메인 용어 사용 (예: "validateUserCredentials")
  참조: spec.md FR-003 "사용자 인증"
```

#### B. 아키텍처 일관성

**plan.md 구조와 실제 파일 비교**:

1.  **plan.md** "아키텍처" 섹션 읽기
2.  **예상 계층 추출**: 컨트롤러 → 서비스 → 리포지토리
3.  **실제 파일 구조 스캔**:
    ```bash
    tree src/ -L 2 --dirsfirst
    ```
4.  **유효성 검사**:
    *   파일이 예상 계층으로 구성되어 있습니까?
    *   컨트롤러가 서비스만 호출합니까(리포지토리 아님)?
    *   비즈니스 규칙이 서비스에 있습니까(컨트롤러 아님)?

**위반**:
- **높음**: 컨트롤러가 데이터베이스에 직접 액세스(서비스 계층 건너뛰기)
- **중간**: 서비스가 다른 서비스의 리포지토리 호출
- **낮음**: 잘못된 디렉토리에 파일이 잘못 배치됨

**출력 형식**:
```
H-002: src/controllers/user.controller.ts:67의 아키텍처 위반
  문제: 컨트롤러가 UserRepository를 직접 호출합니다(UserService를 호출해야 함).
  예상: 컨트롤러 → 서비스 → 리포지토리 (plan.md §3.2)
```

#### C. 주석 품질 검토(조건부)

복잡성이 7보다 큰 경우에만 분석합니다.

```bash
HIGH_COMPLEXITY_FILES=$(jq -r '.[] | select(.complexity > 7) | .filePath' .specify/review/eslint.json 2>/dev/null | sort -u)
[ -z "$HIGH_COMPLEXITY_FILES" ] && echo "⏭️  건너뛰기 (모든 복잡성 ≤7)" && exit 0
echo "$HIGH_COMPLEXITY_FILES" | xargs -I{} rg "^[
]*//|^[
]*/\*" {} --json
```

"왜" 주석(좋음)과 "무엇" 주석(중복)을 확인합니다.

#### D. 오류 처리

오류 처리 일관성 확인: 사용자 지정 예외 대 일반 오류, 로깅 패턴.

#### E. 테스트 품질

AAA 패턴, 경계 테스트, 모의 사용을 확인합니다. 중요한 경로에 대한 테스트가 없는 경우 **높음**입니다.

#### F. 성능

N+1 쿼리(DB 호출이 있는 루프), 불필요한 재계산, 메모리 누수를 감지합니다.

#### G. 보안

엔드포인트에 대한 인증 누락, 로그의 민감한 데이터, 스택 추적 노출을 확인합니다.

--- 

### 5.5단계: ultrathink 패턴 분석

**ultrathink**: 5단계의 집계된 데이터를 사용하여 시스템적인 패턴(3회 이상 발생)을 분석합니다.

각 패턴에 대해: 5-Why 근본 원인 분석 → 예방 전략 → 일괄 수정 기회.

--- 

### 6단계: 통합 및 점수 매기기

자동화된 도구 + AI 분석의 문제를 집계합니다.

**영향 필터링**: 점수가 15 미만인 낮음 문제를 숨깁니다. 영향이 큰 낮음을 중간으로 승격합니다.

**점수**: `100 - (치명적×20 + 높음×5 + 중간×2 + 낮음×0.5)`

--- 

### 7단계: 보고서 생성

```bash
mkdir -p docs/review
AGENT_NAME="${CLAUDE_SESSION:+Claude}"
AGENT_NAME="${AGENT_NAME:-${GEMINI_SESSION:+Gemini}}"
AGENT_NAME="${AGENT_NAME:-Claude}"
REPORT_FILE="docs/review/review_${AGENT_NAME}_$(date +%y%m%d-%H%M%S).md"
```

보고서 구조(콘솔 + 파일):

- 요약: 치명적/높음/중간/낮음 개수, 전체 점수
- 의도 및 초점 헌장(보고서가 자체 포함되도록 2.5단계의 인라인 사본)
- 프로덕션 위험, 전략적 잠금 해제, 빠른 성과
- 적용 범위 체크리스트
- 숨겨진 낮음 문제 개수(`--verbose`로 표시)

--- 

### 8단계: 대화형 작업(신규)

**높음/치명적 문제가 있는 경우에만** 사용자에게 다음을 묻습니다.

- 신뢰도가 높은 문제(N+1 쿼리, 인증 가드 누락)에 대한 자동 수정 옵션
- 수정 적용 후 확인 다시 실행
- 또는 수정 없이 계속( `/fin`에서 플래그 지정됨)

--- 

### 9단계: 정리 및 상태 관리

분석 아티팩트를 제거하고 `/fin` 통합을 위해 상태를 저장합니다.

```bash
REVIEW_CACHE_DIR=".specify"
REVIEW_TMP_FILES=(
  "$REVIEW_CACHE_DIR/review-rg.ndjson"
  "$REVIEW_CACHE_DIR/review-patterns.json"
  "$REVIEW_CACHE_DIR/review/jscpd.json"
  "$REVIEW_CACHE_DIR/review/eslint.json"
  "$REVIEW_CACHE_DIR/review/radon.json"
  "$REVIEW_CACHE_DIR/review-changed-by-hash.txt"
  "$REVIEW_CACHE_DIR/review-hash.now"
)

# 임시 분석 파일 제거(다음 실행 시 속도를 높이기 위해 review-hash.cache 유지)
for file in "${REVIEW_TMP_FILES[@]}"; do
  rm -f "$file"
done

# /fin 통합을 위해 상태 저장(신규)
if [ $HIGH_COUNT -gt 0 ]; then
  echo "$HIGH_COUNT 높음 문제 미해결" > .specify/review-state.txt
  echo "확인하려면 /ms.review 실행" >> .specify/review-state.txt
  echo "검토 보고서: $REPORT_FILE" >> .specify/review-state.txt
fi
```

**메모리에 경고 유지**: `/fin` 명령이 확인할 수 있도록 높음/치명적 문제를 저장합니다.

- **아티팩트 정책**
  - 유지: `.specify/review-hash.cache` (다음 실행 시 해시 기반 비교에 사용됨)
  - 제거: `.specify/review/*.json`, `.specify/review-rg.ndjson`, 임시 해시 파일
  - 보고서: `docs/review/review_{agent}_{timestamp}.md`는 감사 추적을 위해 유지됨

--- 

## 사용자 옵션

### 빠른 모드(신규)

더 빠른 검토를 위해 패턴 분석을 건너뜁니다.

```bash
/ms.review --quick
# 건너뛰기: ultrathink 패턴 분석(5.5단계)
# 실행: 일반 검사만(30% 더 빠름)
```

### 상세 모드(신규)

필터링된 문제를 포함하여 모든 문제를 표시합니다.

```bash
/ms.review --verbose
# 표시: 모든 낮음 문제(영향 점수가 15 미만인 문제 포함)
# 유용: 전체 코드 감사
```

### 비대화형 모드(신규)

CI/CD에 대한 작업 프롬프트를 건너뜁니다.

```bash
/ms.review --no-interactive
# 건너뛰기: 대화형 작업 프롬프트(8단계)
# 유용: 자동화된 파이프라인
```

### 느린 검사 건너뛰기

개발 중 빠른 검토를 위해:

```bash
/ms.review --fast
# 건너뛰기: 자동화된 도구(jscpd, 복잡성 분석)
# 실행: AI 기반 패턴 감지만
```

### 범주에 집중

특정 측면만 검토합니다.

```bash
/ms.review --focus security
/ms.review --focus performance
/ms.review --focus naming
/ms.review --focus tests
```

**범주**:
- `security`: 인증, 로깅, 오류 노출
- `performance`: N+1 쿼리, 불필요한 계산
- `naming`: 변수/함수 이름 대 도메인 용어
- `architecture`: 계층 위반, 패턴 일관성
- `tests`: 테스트 품질, 경계 사례, 모의 사용
- `maintainability`: 주석, 오류 처리, 중복

--- 

## 워크플로와의 통합

### /ms.implement 이후

```bash
# 구현 완료
/ms.implement  # ✅ 모든 작업 구현됨

# 코드 품질 검토
/ms.review  # ⚠️ 높음 문제 2개 발견

# 문제 수정
# ... (H-001 및 H-002 수정)

# 재검토
/ms.review  # ✅ 모든 높음 문제 해결됨

# 완료 및 커밋
/fin
```

### /fin 이전(향상됨)

`/fin` 명령은 검토 상태를 확인해야 합니다.

```bash
# /fin 워크플로에서
if [ -f .specify/review-state.txt ]; then
  echo "⚠️ 코드 검토에서 높음 문제 발견:"
  cat .specify/review-state.txt
  echo ""
  echo "그래도 계속하시겠습니까? (권장하지 않음) [y/N]"
  read -r response
  if [ "$response" != "y" ]; then
    echo "❌ 중단됨. 먼저 문제를 해결하거나 /ms.review를 실행하십시오."
    exit 1
  fi
fi
```

검토 상태 파일에는 다음이 포함됩니다.
- 해결되지 않은 높음 문제 수
- 최신 검토 보고서 경로
- 마지막 검토 타임스탬프

--- 

## 다른 명령과의 차이점

| 명령 | 목적 | 확인 | 실행 시기 |
|---|---|---|---|
| `/ms.analyze` | 구조 + TRUST 유효성 검사 | 테스트 실행, 린트 통과, 커버리지 ≥85%, TAG 무결성 | `/ms.implement` 이전 |
| `/ms.review` | 코드 품질 + 디자인 | 이름 지정, 아키텍처, 성능, 보안 심층 분석 | `/ms.implement` 이후 |
| `/speckit.checklist` | 요구 사항 유효성 검사 | 사양 요구 사항 충족, 기능적 정확성 | 언제든지(수동) |
| `/fin` | 최종 커밋 | CI 확인, 경고 확인 | 모든 검토 통과 후 |

**멘탈 모델**:
- `/ms.analyze` = "빌드할 수 있습니까?" (구조)
- `/ms.review` = "병합해야 합니까?" (품질)
- `/speckit.checklist` = "올바른 것을 빌드했습니까?" (요구 사항)

--- 

## 오류 처리

### 구현된 파일을 찾을 수 없음

```
❌ 구현된 파일을 찾을 수 없음

예상 디렉토리:
- src/ (소스 코드)
- tests/ (테스트 파일)

코드를 생성하려면 먼저 /ms.implement를 실행하십시오.
```

### 컨텍스트 문서 누락

```
⚠️ 컨텍스트 문서 누락

발견:
- spec.md ✅
- plan.md ❌ ( /ms.plan 실행)

제한된 컨텍스트로 검토를 진행합니다.
일부 확인(아키텍처 유효성 검사, 이름 지정 일관성)은 건너뛸 수 있습니다.
```

### 도구 설치 누락

```
⚠️ 선택적 도구를 찾을 수 없음: jscpd

코드 중복 분석을 건너뜁니다.
설치: npm install -g jscpd

나머지 확인으로 검토를 계속합니다.
```

--- 

## 성능 최적화

**1-3단계 최적화(구현됨)**:

1.  **변경된 파일 우선순위**(git diff) - 98% 파일 감소 → 3-10배 더 빠름
2.  **단일 패스 ripgrep** - 10회 호출 → 1회 호출 → 70% I/O 감소
3.  **병렬 실행** - jscpd + eslint + radon + rg 동시 실행 → 60% 더 빠름
4.  **파일 해시 캐싱**(SHA1) - 재실행 시 변경되지 않은 파일 건너뛰기 → 80% 감소
5.  **조건부 도구** - jscpd는 200 LOC 초과 파일에만, 주석 검토는 복잡성이 7보다 큰 경우에만
6.  **실시간 패턴 집계** - 5단계 중 증분 계산 → 80% 감소
7.  **컨텍스트 문서 캐싱** - spec.md/plan.md 한 번 로드 → 85% I/O 감소

**예상 런타임**:

| 시나리오 | 이전 | 이후 | 개선 |
|---|---|---|---|
| 소규모 PR (5개 파일) | 30초 | **5초** | 83% ↓ |
| 중간 PR (20개 파일) | 60초 | **12초** | 80% ↓ |
| 대규모 PR (100개 파일) | 120초 | **32초** | 73% ↓ |
| 재실행(캐시 적중) | 60초 | **10초** | 83% ↓ |

--- 

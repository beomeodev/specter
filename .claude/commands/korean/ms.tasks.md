---
description: "자동 TAG ID 생성으로 작업 생성"
---

# /ms.tasks - TAG ID로 작업 생성

`/speckit.tasks`를 확장하여 자동 TAG ID 할당으로 구현 작업을 생성합니다.

## 개요

이 명령은 상세한 작업 분석을 생성하고 완전한 추적성(SPEC→TEST→CODE)을 위해 각 사용자 스토리에 고유한 TAG ID를 자동으로 할당합니다.

## 실행 단계

### 0. 프로젝트 컨텍스트 로드

**프로젝트 문서 자동 로드**:
- `.specify/memory/constitution.md` (헌법 - 필수)
- `AGENTS.md` (AI 지침, 코딩 표준 - 있는 경우)
- `specs/[spec-id]/spec.md` (기능 사양 - 필수)
- `specs/[spec-id]/plan.md` (구현 계획 - 필수)

**헌법, spec.md 또는 plan.md가 없는 경우**:
- 오류 표시: "필수 파일이 없습니다. 먼저 `/ms.init`, `/ms.specify` 및 `/ms.plan`을 실행하십시오."
- 종료

**작업 생성을 위한 참조**:
- 헌법 섹션 II (단순성 우선 - 파일 크기 목표: ≤500 SLOC, ≤100 LOC/함수)
- 헌법 섹션 IX (프로젝트별 제약 조건 - `/ms.constitution`에 의해 추가된 경우 **있는 경우**)
- AGENTS.md (코딩 표준, 작업 구성 패턴 - 있는 경우)

**이 문서들은 다음을 돕습니다**:
- 프로젝트 구조를 기반으로 적절한 TAG 도메인 이름 생성
- 파일 크기 제한에 따라 작업 세분화
- 프로젝트별 작업 구성 패턴 적용

### 1. 기본 명령 실행

`/speckit.tasks`를 실행하여 기본 작업 구조 생성:

```
/speckit.tasks $ARGUMENTS
```

이렇게 하면 단계, 종속성 및 작업 세부 정보가 포함된 tasks.md가 생성됩니다.

### 2. TAG ID 생성

spec.md의 각 기능 요구 사항(FR)에 대해:

**도메인 추출**:

```bash
extract_domain() {
  local fr_title="$1"
  local fr_number="$2"

  # 도메인 키워드 일치
  echo "$fr_title" | rg -io '(auth|user|pay|cart|order|product|admin|notif|search|profile)' | head -n1 | tr '[:lower:]' '[:upper:]' \
    || echo "FR${fr_number}"  # FR 번호로 대체
}
```

**기존 TAG 수 계산**:

```bash
count_tags_for_domain() {
  local domain="$1"
  rg "@SPEC:${domain}-" -c src tests backend/src frontend/src 2>/dev/null | awk -F: '{sum+=$2} END {print sum+0}'
}
```

**TAG ID 생성**:

```bash
generate_tag_id() {
  local domain="$1"
  local count=$(count_tags_for_domain "$domain")
  printf "%s-%03d" "$domain" $((count + 1))
}

# 예: AUTH-001, AUTH-002, PAY-001
```

### 3. TAG 메타데이터 삽입

각 사용자 스토리에 대해 tasks.md에 TAG 체인 추가:

```markdown
## 3단계: FR-1 인증(우선순위: P0)

**TAG**: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001

**목표**: 사용자 인증 구현
**독립 테스트**: 사용자는 이메일/비밀번호로 로그인할 수 있습니다.

### FR-1 구현

-   [ ] T015 인증 서비스 생성...
-   [ ] T016 로그인 엔드포인트 추가...
```

### 4. 보고서 출력

```json
{
    "tag_ids": ["@SPEC:AUTH-001", "@SPEC:USER-001", "@SPEC:PAY-001"],
    "domain_map": {
        "AUTH": 1,
        "USER": 1,
        "PAY": 1
    },
    "tasks_updated": "specs/001-my-spec-spec/tasks.md"
}
```

## TAG 형식

**체인 형식**:

```
@SPEC:{TAG_ID} → @TEST:{TAG_ID} → @CODE:{TAG_ID}
```

**도메인 추출 예**:

-   "FR-1: 사용자 인증" → 도메인: AUTH (키워드 일치)
-   "FR-2: 장바구니" → 도메인: CART (키워드 일치)
-   "FR-9: 임의 기능" → 도메인: FR9 (대체)

## 오류 처리

-   **SPEC_NOT_FOUND**: 먼저 `/ms.specify` 실행
-   **TASKS_GENERATION_FAILED**: 기본 명령 실패
-   **RIPGREP_NOT_FOUND**: ripgrep ≥13.0 설치
-   **DUPLICATE_TAG**: TAG ID 충돌 감지됨

## 다음 단계

`/ms.tasks` 이후:

1. TAG 할당으로 tasks.md 검토
2. spec-tasks 일관성 및 TRUST 준수를 확인하기 위해 `/ms.analyze` 실행
3. 이제 TAG ID가 할당되었습니다 ✅

## 참고

-   TAG 계산에 ripgrep 필요
-   TAG ID는 프로젝트 전체에서 고유합니다.
-   도메인 추출은 FR 번호 대체와 함께 키워드 일치를 사용합니다.
-   Tasks.md는 완전한 추적성을 갖춘 구현 로드맵이 됩니다.

## 구현 세부 정보

**도구**: SlashCommand(/speckit.tasks), Read, Edit, Bash(ripgrep)

```

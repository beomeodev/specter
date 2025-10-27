---
description: "헌법 참조와 함께 기능 사양 생성"
---

# /ms.specify - 기능 사양 생성

헌법 준수와 함께 Spec-Kit 워크플로우에 따라 기능 사양을 생성합니다.

## 개요

이 명령은 `/speckit.specify`를 확장하여 명시적인 헌법 참조를 포함시켜 AI가 사양 작성 중에 EARS, TRUST 및 TAG 원칙을 따르도록 합니다.

## 사용법

```
/ms.specify [기능_이름]
```

예시:

```
/ms.specify user-authentication
```

## 실행 단계

### 1. 프로젝트 컨텍스트 로드

**프로젝트 문서 자동 로드**:
- `.specify/memory/constitution.md` (헌법 - 필수)
- `AGENTS.md` (AI 지침, 코딩 표준 - 있는 경우)

**헌법이 없는 경우**:
- 오류 표시: "헌법을 찾을 수 없습니다. 먼저 `/ms.init`을 실행하십시오."
- 종료

**AGENTS.md가 없는 경우**:
- 공지 표시: "AGENTS.md를 찾을 수 없습니다 (`/ms.constitution`에 의해 생성됨)"
- 계속

**참조 키 섹션**:
- 헌법 섹션 IV (EARS 표준)
- 헌법 섹션 V (TRUST 원칙)
- 헌법 섹션 IX (프로젝트별 제약 조건 - `/ms.constitution`에 의해 추가된 경우 **있는 경우**)
- project-structure.md (기존 기술 스택 이해 - **있는 경우**)

### 2. AI 프롬프트에 헌법 컨텍스트 주입

`/speckit.specify`를 실행하기 전에 AI에 헌법 참조를 제공합니다.

```
당신은 프로젝트 헌법을 따라야 하는 사양을 만들고 있습니다.

**헌법**: .specify/memory/constitution.md

**이 섹션을 읽고 적용하십시오**:
- **섹션 IV**: 요구 사항 명확성(EARS 표준) - EARS 패턴(WHEN/WHILE/WHERE/IF/SHALL) 사용
- **섹션 V**: TRUST 5 원칙 - 테스트 가능성, 가독성, 보안, 추적 가능성을 위한 설계

**언어 정책**:
- 모든 요구 사항을 영어로 작성
- 영어로 EARS 키워드(WHEN/WHILE/WHERE/IF/SHALL/MAY) 사용
- 사용자가 한국어 입력을 제공하면 영어 EARS 형식으로 번역

**예시**:
사용자 입력(한국어): "사용자가 로그인하면 토큰을 발급한다"
귀하의 출력(영어): "WHEN user logs in with valid credentials, system SHALL issue JWT token"

**상세한 EARS 패턴 및 TRUST 원칙은 헌법을 참조하십시오.**

이제 이러한 원칙에 따라 사양을 만드십시오.
```

### 2.5. 적응형 컨텍스트 분석(정량적 결정)

**1단계: 사용자 요청 분석(필수)**

`$ARGUMENTS`에서 키워드를 추출하고 계산합니다.

```bash
# 간단한 키워드 계산
SIMPLE_KEYWORDS=$(echo "$ARGUMENTS" | grep -iEo "\b(config|setting|constant|type|interface|util|helper|log|message)\b" | wc -l)

# 보통 키워드 계산
MODERATE_KEYWORDS=$(echo "$ARGUMENTS" | grep -iEo "\b(feature|module|component|endpoint|model|service|page|form)\b" | wc -l)

# 복잡한 키워드 계산
COMPLEX_KEYWORDS=$(echo "$ARGUMENTS" | grep -iEo "\b(system|architecture|integration|external|api|realtime|workflow|migration)\b" | wc -l)

# 기존 유사 사양 확인
SIMILAR_SPECS=$(find specs/ -name "spec.md" 2>/dev/null | wc -l)
```

**2단계: 의사 결정 트리 적용**

우선순위 순서대로 실행(첫 번째 일치에서 중지):

```
┌─────────────────────────────────────────────────────────────┐
│ 의사 결정 트리(우선순위 순서)                               │
├─────────────────────────────────────────────────────────────┤
│ 1. IF COMPLEX_KEYWORDS ≥ 2                                  │
│    → 복잡함(시스템 수준 변경)                               │
│                                                              │
│ 2. IF SIMPLE_KEYWORDS ≥ 2 AND COMPLEX_KEYWORDS = 0          │
│    → 간단함(구성/유틸리티 변경)                             │
│                                                              │
│ 3. IF MODERATE_KEYWORDS ≥ 1 OR SIMILAR_SPECS ≥ 3            │
│    → 보통(사용 가능한 패턴이 있는 기능)                     │
│                                                              │
│ 4. IF SIMPLE_KEYWORDS ≥ 1 AND MODERATE_KEYWORDS = 0         │
│    → 간단함                                                  │
│                                                              │
│ 5. FALLBACK (결정할 수 없음)                                │
│    → 보통(안전한 기본값 - 에이전트 2개)                     │
└─────────────────────────────────────────────────────────────┘
```

### 3. 기본 지정 명령 실행

헌법 강화 컨텍스트로 `/speckit.specify` 실행:

```
/speckit.specify $ARGUMENTS
```

**에이전트 위임**: 내부적으로 EARS 패턴 변환 및 SPEC 문서 생성을 위해 **spec-builder** 에이전트(Sonnet 모델)를 사용합니다.

이렇게 하면 AI가 자동으로 EARS 및 TRUST 원칙을 따르는 `specs/{SPEC_ID}/spec.md`에 사양이 생성됩니다.

### 4. 헌법 참조 바닥글 추가

spec.md가 생성된 후 문서에 헌법 참조 섹션을 추가합니다.

```markdown
---

## 📜 헌법

이 사양은 프로젝트 [헌법](../../.specify/memory/constitution.md)을 따릅니다.

**주요 섹션:**
- **섹션 IV**: EARS 요구 사항 표준
- **섹션 V**: TRUST 5 품질 원칙
- **TAG 시스템**: 추적 가능성(SPEC → TEST → CODE)

_/ms.specify에 의해 자동 추가됨_
```

### 5. 성공 보고

요약 표시:

```json
{
    "spec_created": "specs/001-user-authentication/spec.md",
    "constitution_referenced": true,
    "constitution_exists": true,
    "next_step": "/ms.clarify or /ms.checklist"
}
```

다음 단계 표시:

```
✅ 사양이 성공적으로 생성되었습니다!

📄 사양: specs/001-user-authentication/spec.md
📜 헌법: .specify/memory/constitution.md

🎯 다음 단계:
1. spec.md의 완전성 검토
2. 모호한 요구 사항을 명확히 하려면 `/ms.clarify` 실행(질의응답)
3. 또는 완전성 체크리스트를 생성하려면 `/ms.checklist` 실행(체크리스트)
4. 그런 다음 구현 계획을 위해 `/ms.plan`으로 진행

📖 적용된 헌법 섹션:
- 섹션 IV: EARS (5가지 요구 사항 패턴)
- 섹션 V: TRUST (5가지 품질 원칙)
```

## 오류 처리

### 오류 1: Spec-Kit이 초기화되지 않음

**증상**: `.specify/` 디렉토리 없음

**메시지**:

```
❌ 오류: Spec-Kit이 초기화되지 않았습니다.

이 프로젝트는 Spec-Kit으로 초기화되지 않았습니다.

다음을 실행하십시오.
  /ms.init

이렇게 하면 Spec-Kit 템플릿이 설정되고 헌법이 생성됩니다.
```

**종료**: 코드 1

### 오류 2: 기본 명령 실패

**증상**: `/speckit.specify`가 오류를 반환했습니다.

**메시지**:

```
❌ 오류: 사양 생성 실패

기본 `/speckit.specify` 명령에서 오류가 발생했습니다.
위의 오류 메시지를 확인하고 다시 시도하십시오.

일반적인 문제:
- 사양 ID가 이미 존재합니다.
- 잘못된 디렉토리 구조
- 권한 없음
```

**종료**: 코드 1

## 참고

-   **사양 생성 전 헌법 주입**: AI는 사후가 아닌 사전에 원칙을 받습니다.
-   **자연스러운 준수**: AI는 사후 처리를 통하지 않고 작성 중에 EARS/TRUST를 적용합니다.
-   **영어 출력**: 모든 사양은 영어로 작성됩니다(한국어 입력 → 영어 EARS 출력).
-   **강제 변환 없음**: 헌법은 코드로 강제되는 것이 아니라 AI의 행동을 안내합니다.
-   **워크플로 개선**: 이 접근 방식은 처음부터 더 높은 품질의 사양을 보장합니다.

## 구현 세부 정보

**도구**: SlashCommand(/speckit.specify), Read(헌법 확인), Edit(헌법 섹션 추가)

## 다음 명령

`/ms.specify` 이후:
1. 모호한 요구 사항을 명확히 하려면 `/ms.clarify` 실행(질의응답 방식)
2. 또는 완전성 체크리스트를 생성하려면 `/ms.checklist` 실행(체크리스트 방식)
3. 그런 다음 구현 계획을 위해 `/ms.plan`으로 진행

**워크플로**: `/ms.specify` → `/ms.clarify` 또는 `/ms.checklist` → `/ms.plan`

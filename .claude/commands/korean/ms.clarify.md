---
description: "모호한 요구사항 명확화 (Spec-Kit 표준)"
---

# /ms.clarify - 요구사항 명확화

Spec-Kit의 표준 명확화 워크플로우를 사용하여 spec.md의 모호한 요구사항을 명확히 합니다.

## 개요

이 명령어는 헌법 원칙(특히 EARS 형식)을 주입하고 사용자 커뮤니케이션을 위해 **한국어 상호작용**을 활성화하여 `/speckit.clarify`를 확장합니다.

**주요 특징**:

- AI는 명확화 전에 EARS 원칙을 받습니다.
- **한국어**로 사용자 상호작용 (질문, 옵션, 답변)
- 최종 spec.md 업데이트는 EARS 형식의 **영어**로 이루어집니다.
- 헌법 기반 AI 동작을 통한 자연스러운 EARS 준수

## 언어 정책

**사용자 상호작용: 한국어** ✅

헌법 제4조에 따라:

> "워크플로우 중 생성되는 문서들(spec.md, plan.md, tasks.md)에서만 반드시 영어를 사용하며,
> 사용자와의 상호작용에서는 한국어를 사용한다."

**워크플로우**:

1. AI가 **한국어**로 명확화 질문을 합니다.
2. 사용자가 **한국어**로 답변합니다.
3. AI가 **한국어**로 A/B/C 옵션을 제공합니다 (영어 EARS 참조 포함).
4. spec.md는 EARS 형식의 **영어**로 업데이트됩니다.

## 실행 단계

### 1. 헌법 로드

`.specify/memory/constitution.md`를 읽고 존재하는지 확인합니다.

**참조할 주요 섹션:**

- **섹션 IV**: 요구사항 명확성 (EARS 표준)

**언어 정책** (섹션 IV에서):

- 사용자 상호작용: 한국어
- 워크플로우 문서: 영어

**헌법을 찾을 수 없는 경우**:
경고를 표시하고 (깨진 참조와 함께) 계속합니다.

### 2. AI 프롬프트에 헌법 컨텍스트 주입

`/speckit.clarify`를 실행하기 전에 AI에 헌법 참조를 제공합니다:

```
당신은 spec.md의 요구사항을 명확히 하고 있습니다. 프로젝트 헌법을 따르십시오.

**헌법**: .specify/memory/constitution.md

**섹션 IV를 읽고 적용하십시오** (요구사항 명확성 - EARS 표준):
- EARS 패턴 사용: WHEN/WHILE/WHERE/IF/SHALL/MAY
- 모호한 요구사항을 식별하고 대안적인 해석을 제공합니다.

**언어 정책 (필수)**:
- 사용자와 한국어로 소통합니다 (질문 및 옵션).
- 참조용으로 괄호 안에 EARS 영어 형식을 표시합니다.
- spec.md를 EARS 형식의 영어로 업데이트합니다.

**명확화 예시** (한국어):
```

요구사항 "로그인 기능이 필요합니다"가 모호합니다. 다음 중 선택해주세요:

A) 시스템은 사용자 로그인 기능을 제공해야 합니다
(EARS: System SHALL provide user login functionality)

B) 사용자가 로그인 버튼을 클릭하면, 시스템은 자격증명을 인증해야 합니다
(EARS: WHEN user clicks login button, system SHALL authenticate credentials)

```

**상세한 EARS 패턴은 헌법 섹션 IV를 참조하십시오.**

이제 모호한 요구사항을 식별하고 명확화를 시작하십시오.
```

### 3. 기본 명확화 명령 실행

헌법 강화 컨텍스트로 `/speckit.clarify`를 실행합니다:

```
/speckit.clarify $ARGUMENTS
```

이것은 AI가 EARS 원칙을 따르고 사용자 상호작용에 한국어를 사용하는 명확화 워크플로우를 실행합니다.

### 4. 성공 보고

요약 표시:

```json
{
    "clarifications_made": 5,
    "spec_updated": "specs/001-user-authentication/spec.md",
    "ears_compliance": "natural (via Constitution)",
    "next_step": "/ms.plan"
}
```

다음 단계 표시 (한국어):

```
✅ 요구사항 명확화 완료!

📄 업데이트됨: specs/001-user-authentication/spec.md

🎯 다음 단계:
1. 명확화된 요구사항 검토
2. `/ms.plan` 실행하여 구현 계획 작성
3. AI가 Constitution 기반으로 EARS 형식을 따랐습니다 ✅

📖 EARS 준수 달성:
- 헌법 섹션 IV (EARS 규칙)
- AI 자연어 이해
- 강제 변환 로직 없음 (Constitution 주입 방식)
```

## 오류 처리

### 오류 1: Spec-Kit이 초기화되지 않음

**증상**: `.specify/` 디렉토리 없음

**메시지**:

```
❌ 오류: Spec-Kit이 초기화되지 않았습니다.

다음을 실행하십시오: /ms.init
```

**종료**: 코드 1

### 오류 2: 기본 명령 실패

**증상**: `/speckit.clarify`가 오류를 반환했습니다.

**메시지**:

```
❌ 오류: 명확화 실패

기본 `/speckit.clarify` 명령에서 오류가 발생했습니다.
위의 오류 메시지를 확인하고 다시 시도하십시오.
```

**종료**: 코드 1

## 참고

- **명확화 전 헌법 주입**: AI는 사전에 EARS 원칙을 받습니다.
- **한국어 사용자 상호작용**: 질문과 옵션은 한국어로, spec.md는 영어로
- **자연스러운 EARS 준수**: 코드로 강제하는 것이 아니라 헌법이 AI의 행동을 안내합니다.
- **강제 변환 없음**: AI는 명확화 중에 자연스럽게 EARS를 적용합니다.
- **언어 정책 정렬**: 헌법 섹션 IV와 일치합니다 (문서=영어, 상호작용=한국어).

## 구현 세부 정보

**기본 명령**: `/speckit.clarify`

**확장**: 없음 (순수 Spec-Kit 명령)

**도구**: SlashCommand (/speckit.clarify)

## 다음 명령

`/ms.clarify` 이후: 명확화된 요구사항을 기반으로 구현 계획을 생성하려면 `/ms.plan`을 실행합니다.

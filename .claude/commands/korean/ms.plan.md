---
description: "헌법 참조와 함께 구현 계획 생성"
---

# /ms.plan - 구현 계획 생성

헌법 준수와 함께 Spec-Kit 워크플로우에 따라 구현 계획을 생성합니다.

## 개요

이 명령은 `/speckit.plan`을 확장하여 명시적인 헌법 참조를 포함시켜 AI가 계획 중에 TRUST 원칙, 단순성 우선 아키텍처 및 모듈식 설계를 따르도록 합니다.

## 사용법

```
/ms.plan
```

## 실행 단계

### 1. 프로젝트 컨텍스트 로드

**프로젝트 문서 자동 로드**:
- `.specify/memory/constitution.md` (헌법 - 필수)
- `AGENTS.md` (AI 지침, 코딩 표준 - 있는 경우)
- `specs/[spec-id]/spec.md` (기능 사양 - 필수)

**헌법 또는 spec.md가 없는 경우**:
- 오류 표시: "필수 파일이 없습니다. 먼저 `/ms.init` 및 `/ms.specify`를 실행하십시오."
- 종료

**AGENTS.md가 없는 경우**:
- 공지 표시: "AGENTS.md를 찾을 수 없습니다 (`/ms.constitution`에 의해 생성됨)"
- 계속

**참조 키 섹션**:
- 헌법 섹션 II (단순성 우선 아키텍처)
- 헌법 섹션 III (모듈식 설계)
- 헌법 섹션 V (TRUST 원칙)
- 헌법 섹션 IX (프로젝트별 제약 조건 - `/ms.constitution`에 의해 추가된 경우 **있는 경우**)

### 2. AI 프롬프트에 헌법 컨텍스트 주입

`/speckit.plan`을 실행하기 전에 AI에 헌법 참조를 제공합니다.

```
당신은 프로젝트 헌법을 따라야 하는 구현 계획을 만들고 있습니다.

**헌법**: .specify/memory/constitution.md

**이 섹션을 읽고 적용하십시오**:
- **섹션 II**: 단순성 우선 아키텍처 - 내장 도구 선호, 파일 ≤500 SLOC, 함수 ≤100 LOC
- **섹션 III**: 모듈식 설계 - 독립적인 모듈, 명확한 인터페이스, 종속성 주입
- **섹션 V**: TRUST 5 원칙 - 테스트 우선(TDD, ≥85% 커버리지), 가독성, 통일성, 보안, 추적 가능성

**상세한 아키텍처 원칙 및 제약 조건은 헌법을 참조하십시오.**

이제 이러한 원칙에 따라 구현 계획을 만드십시오.
```

### 2.5. 적응형 컨텍스트 분석(정량적 결정)

**1단계: 사양 복잡성 분석(필수)**

spec.md를 읽고 메트릭을 추출합니다.

```bash
# 기능 요구 사항(FR) 수 계산
FR_COUNT=$(grep -E "^#{1,3}\s+FR-[0-9]+" specs/*/spec.md | wc -l)

# 언급된 구성 요소 수 계산
COMPONENT_COUNT=$(grep -iEo "\b(service|controller|model|repository|handler|middleware|component|page)\b" specs/*/spec.md | sort -u | wc -l)

# 통합 키워드 확인
INTEGRATION_KEYWORDS=$(grep -iEo "\b(external|api|integration|third-party|webhook|oauth)\b" specs/*/spec.md | wc -l)

# 기존 유사 계획 확인
SIMILAR_PLANS=$(find specs/ -name "plan.md" 2>/dev/null | wc -l)
```

**2단계: 의사 결정 트리 적용**

우선순위 순서대로 실행(첫 번째 일치에서 중지):

```
┌─────────────────────────────────────────────────────────────┐
│ 의사 결정 트리(우선순위 순서)                               │
├─────────────────────────────────────────────────────────────┤
│ 1. IF INTEGRATION_KEYWORDS ≥ 3                              │
│    → 복잡함(외부 통합)                                      │
│                                                              │
│ 2. IF FR_COUNT ≤ 2 AND COMPONENT_COUNT ≤ 2                  │
│    → 간단함(단일 유틸리티/구성)                             │
│                                                              │
│ 3. IF COMPONENT_COUNT ≥ 5 OR FR_COUNT ≥ 8                   │
│    → 복잡함(다중 구성 요소 시스템)                          │
│                                                              │
│ 4. IF SIMILAR_PLANS ≥ 3                                     │
│    → 보통(사용 가능한 패턴)                                 │
│                                                              │
│ 5. IF COMPONENT_COUNT ≥ 2 OR FR_COUNT ≥ 3                   │
│    → 보통                                                    │
│                                                              │
│ 6. FALLBACK (결정할 수 없음)                                │
│    → 보통(안전한 기본값 - 에이전트 2개)                     │
└─────────────────────────────────────────────────────────────┘
```

**3단계: 하위 에이전트 전략 실행**

위에서 결정된 복잡성에 따라:

**간단한 경우**:
  - 하위 에이전트 0개
  - 3단계로 바로 진행

**보통인 경우**:
  - 2개의 하위 에이전트를 TRUE PARALLEL(백그라운드 실행)로 시작:

    **1단계: 모든 에이전트를 백그라운드에서 시작**
    ```python
    # 에이전트 1을 백그라운드에서 시작
    task_id_1 = mcp__cli-bridge__gemini_cli(
        prompt="'$SPEC_FEATURE'에 대한 기존 코드베이스에서 유사한 아키텍처 패턴 찾기",
        background=True  # 즉시 task_id와 함께 반환
    )

    # 에이전트 2를 백그라운드에서 시작(외부 라이브러리가 필요한 경우)
    task_id_2 = mcp__cli-bridge__gemini_cli(
        prompt="필요한 라이브러리에 대한 최신 API 문서 조사",
        background=True  # 즉시 task_id와 함께 반환
    )
    ```

    **2단계: 에이전트가 탐색하는 동안 Claude는 계획을 계속합니다.**
    - 에이전트는 백그라운드에서 독립적으로 작동합니다.
    - Claude Code는 사양을 분석하거나 계획 구조 초안을 작성할 수 있습니다.

    **3단계: 필요할 때 결과 검색**
    ```python
    # 결과 가져오기(완료될 때까지 차단)
    result_1 = mcp__cli-bridge__get_task_result(task_id=task_id_1, wait=True)
    result_2 = mcp__cli-bridge__get_task_result(task_id=task_id_2, wait=True)
    ```

**복잡한 경우**:
  - 3개의 하위 에이전트를 TRUE PARALLEL(백그라운드 실행)로 시작:

    **1단계: 모든 에이전트를 백그라운드에서 시작**
    ```python
    # Gemini 에이전트(백그라운드 실행)
    task_id_1 = mcp__cli-bridge__gemini_cli(
        prompt="'$SPEC_FEATURE'에 대한 기존 코드베이스에서 유사한 아키텍처 패턴 찾기",
        background=True
    )
    task_id_2 = mcp__cli-bridge__gemini_cli(
        prompt="필요한 라이브러리에 대한 최신 API 문서 조사",
        background=True
    )

    # Claude Code 작업(병렬 실행)
    task_id_3 = Task(
        subagent_type="integration-designer",
        prompt="복잡한 기능에 대한 통합 전략 설계"
    )
    ```

    **2단계: 3개의 에이전트 모두 독립적으로 병렬로 작동**
    - Gemini는 코드베이스와 라이브러리를 탐색합니다(차단 없음).
    - Claude는 통합 전략을 설계합니다.
    - Python 3.13+ 자유 스레딩(선택 사항) 또는 asyncio 작업을 통한 진정한 병렬 실행

    **3단계: 필요할 때 결과 검색**
    ```python
    result_1 = mcp__cli-bridge__get_task_result(task_id=task_id_1, wait=True)
    result_2 = mcp__cli-bridge__get_task_result(task_id=task_id_2, wait=True)
    result_3 = # 작업 도구 결과
    ```

**⚠️ 에이전트 실행 규칙**:
- **codebase-explorer** → `mcp__cli-bridge__gemini_cli(background=True)`를 통해 Gemini를 사용해야 합니다.
- **library-researcher** → `mcp__cli-bridge__gemini_cli(background=True)`를 통해 Gemini를 사용해야 합니다.
- **integration-designer** → Claude Code Task 도구를 사용해야 합니다(MCP 아님).

**중요 - 진정한 병렬 실행**:
1. `background=True` 매개변수로 모든 MCP 에이전트 시작
2. 즉시 `TASK_STARTED:{task_id}` 반환
3. 에이전트는 독립적으로 실행됩니다(차단 없음).
4. `get_task_result(task_id, wait=True)`를 사용하여 결과 검색
5. Python 3.13+ 자유 스레딩(선택 사항)은 진정한 병렬 처리를 가능하게 합니다. 그렇지 않으면 asyncio 작업을 사용합니다.

**디버그 출력**(투명성을 위해):
```json
{
  "complexity_metrics": {
    "fr_count": 5,
    "component_count": 4,
    "integration_keywords": 2,
    "similar_plans": 3
  },
  "decision": "MODERATE",
  "reason": "규칙 4: SIMILAR_PLANS ≥ 3",
  "agents_spawned": 2
}
```

### 2.6. 아키텍처 결정 종합

**하위 에이전트가 시작된 경우**(2.5단계):
- 아키텍처 통찰력 결합
- 일관성을 위해 기존 패턴 재사용
- 최신 라이브러리 모범 사례 적용
- 통합 결정 문서화
- 헌법 준수 보장(TRUST, 파일 크기 제한)

**그렇지 않은 경우**:
- 건너뛰기(간단한 계획)

### 3. 기본 계획 명령 실행

헌법 강화 컨텍스트로 `/speckit.plan` 실행:

```
/speckit.plan
```

**에이전트 위임**: 내부적으로 아키텍처 설계, 라이브러리 선택 및 TAG 체인 계획을 위해 **implementation-planner** 에이전트(Opus 모델)를 사용합니다. 복잡한 기능의 경우 다음에도 위임합니다.
- **library-researcher** (Haiku) - Context7 MCP를 통한 최신 라이브러리 문서
- **codebase-explorer** (Haiku) - 기존 패턴 및 아키텍처 분석

이렇게 하면 AI가 자동으로 아키텍처 원칙을 따르는 `specs/{SPEC_ID}/plan.md`에 구현 계획이 생성됩니다.

### 4. 헌법 참조 바닥글 추가

plan.md가 생성된 후 문서에 헌법 참조 섹션을 추가합니다.

```markdown
---

## 📜 헌법

이 계획은 프로젝트 [헌법](.specify/memory/constitution.md)을 따릅니다.

**주요 섹션:**

-   **섹션 II**: 단순성 우선 아키텍처
-   **섹션 III**: 모듈식 설계
-   **섹션 V**: TRUST 5 품질 원칙

_/ms.plan에 의해 자동 추가됨_
```

### 3. 헌법 존재 확인

`.specify/memory/constitution.md`가 있는지 확인합니다.

```bash
ls -la .specify/memory/constitution.md
```

**찾을 수 없는 경우**:

```
⚠️ 경고: 헌법을 찾을 수 없습니다.

예상: .specify/memory/constitution.md

프로젝트 헌법을 만들려면 먼저 `/ms.init`을 실행하십시오.
헌법은 이 프로젝트의 아키텍처 원칙을 정의합니다.

계획 생성은 계속되지만 헌법 참조는 깨집니다.
```

### 4. 성공 보고

요약 표시:

```json
{
    "plan_created": "specs/001-user-authentication/plan.md",
    "constitution_referenced": true,
    "constitution_exists": true,
    "next_step": "/ms.constitution"
}
```

다음 단계 표시:

```
✅ 구현 계획이 성공적으로 생성되었습니다!

📄 계획: specs/001-user-authentication/plan.md
📜 헌법: .specify/memory/constitution.md

🎯 다음 단계:
1. plan.md 아키텍처 검토
2. 프로젝트별 제약 조건을 추출하려면 `/ms.constitution` 실행
3. AI는 헌법을 기반으로 TRUST 원칙을 따랐습니다 ✅

📖 계획 포함 내용:
- 모듈식 아키텍처(독립적으로 테스트 가능한 단위)
- 파일 크기 제한(≤500 SLOC)
- 함수 복잡성 제한(≤10)
- 보안 고려 사항
- TAG 추적 가능성 설계
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

### 오류 2: 사양을 찾을 수 없음

**증상**: spec.md가 없음

**메시지**:

```
❌ 오류: 사양을 찾을 수 없습니다.

먼저 다음을 실행하십시오: /ms.specify
```

**종료**: 코드 1

### 오류 3: 기본 명령 실패

**증상**: `/speckit.plan`이 오류를 반환했습니다.

**메시지**:

```
❌ 오류: 계획 생성 실패

기본 `/speckit.plan` 명령에서 오류가 발생했습니다.
위의 오류 메시지를 확인하고 다시 시도하십시오.
```

**종료**: 코드 1

## 참고

-   **자동 헌법 준수**: AI는 헌법을 읽고 원칙을 자연스럽게 적용합니다.
-   **모듈식 설계 초점**: 아키텍처는 TRUST 및 단순성 우선을 존중합니다.
-   **코드 강제 없음**: 헌법은 코드로 강제되는 것이 아니라 AI의 가이드 역할을 합니다.
-   **다음 명령**: `/ms.analyze`는 계획-사양 일관성 + TRUST 준수를 확인합니다.

## 구현 세부 정보

**기본 명령**: `/speckit.plan`

**확장**: 헌법 참조 섹션

**도구**: SlashCommand(/speckit.plan), Read(헌법 확인), Edit(헌법 섹션 추가)

## 다음 명령

`/ms.plan` 이후: spec.md 및 plan.md에서 프로젝트별 제약 조건을 추출하려면 `/ms.constitution`을 실행합니다.

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

### 1. 전제 조건 확인

**필수 파일 존재 확인**:
- `.specify/memory/constitution.md` (헌법 - 필수)
- `specs/[spec-id]/spec.md` (기능 사양 - 필수)

**헌법 또는 spec.md가 없는 경우**:
- 오류 표시: "필수 파일이 없습니다. 먼저 `/ms.init` 및 `/ms.specify`를 실행하십시오."
- 종료

### 2. `/speckit.plan`에 헌법 지침 제공

**중요**: `/speckit.plan`은 내부적으로 `constitution.md`를 읽습니다. `/ms.plan`의 역할은 직접 읽는 것이 아니라 **읽기 지침**을 제공하는 것입니다.

**`/speckit.plan`을 실행하기 전**, 헌법을 읽을 때 다음 지침을 따르도록 지시하십시오.

```
/speckit.plan을 실행하고 constitution.md를 읽을 때 다음 지침을 따르십시오.

**헌법 읽기 지침**:

1. **아키텍처 섹션에 집중** (우선순위 순서):
   - **섹션 II**: 단순성 우선 아키텍처
     → 외부 종속성보다 내장 도구 선호
     → 파일 ≤500 SLOC, 함수 ≤100 LOC
     → 가장 간단한 해결책을 먼저 선택

   - **섹션 III**: 모듈식 설계
     → 명확한 인터페이스를 가진 독립적인 모듈
     → 하드코딩된 종속성보다 종속성 주입
     → 관심사 분리

   - **섹션 V**: TRUST 5 원칙
     → 테스트 우선: ≥85% 커버리지의 TDD
     → 가독성: 명확한 이름 지정, 최소한의 복잡성
     → 통일성: 코드베이스 전반에 걸친 일관된 패턴
     → 보안성: 기본적으로 보안
     → 추적 가능: TAG 추적성 (SPEC → TEST → CODE)

2. **프로젝트별 제약 조건 적용** (있는 경우):
   - **섹션 IX**: `/ms.constitution`의 프로젝트별 규칙
   → 기술 스택 제약 조건
   → 팀 규칙
   → 도메인별 요구 사항

3. **원칙을 아키텍처 결정으로 변환**:
   - 헌법 원칙을 사용하여 다음을 안내합니다.
     → 구성 요소 구조
     → 라이브러리 선택
     → 테스트 전략
     → 보안 조치
     → 추적성 설계

**예상 동작**:
- /speckit.plan 시작 시 constitution.md 읽기
- 계획 중에 원칙을 자연스럽게 적용
- 원칙이 설계 결정에 어떻게 영향을 미쳤는지 문서화
- 계획이 모든 헌법 제약 조건을 존중하는지 확인
```

### 3. 적응형 컨텍스트 분석 (정량적 결정)

**1단계: 사양 복잡성 분석 (필수)**

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

우선순위 순서대로 실행 (첫 번째 일치에서 중지):

```
┌─────────────────────────────────────────────────────────────┐
│ 의사 결정 트리 (우선순위 순서)                              │
├─────────────────────────────────────────────────────────────┤
│ 1. IF INTEGRATION_KEYWORDS ≥ 3                              │
│    → 복잡함 (외부 통합)                                     │
│                                                              │
│ 2. IF FR_COUNT ≤ 2 AND COMPONENT_COUNT ≤ 2                  │
│    → 간단함 (단일 유틸리티/구성)                            │
│                                                              │
│ 3. IF COMPONENT_COUNT ≥ 5 OR FR_COUNT ≥ 8                   │
│    → 복잡함 (다중 구성 요소 시스템)                         │
│                                                              │
│ 4. IF SIMILAR_PLANS ≥ 3                                     │
│    → 보통 (사용 가능한 패턴)                                │
│                                                              │
│ 5. IF COMPONENT_COUNT ≥ 2 OR FR_COUNT ≥ 3                   │
│    → 보통                                                   │
│                                                              │
│ 6. FALLBACK (결정할 수 없음)                                │
│    → 보통 (안전한 기본값 - 에이전트 2개)                    │
└─────────────────────────────────────────────────────────────┘
```

**3단계: 하위 에이전트 전략 실행**

위에서 결정된 복잡성에 따라:

**간단한 경우**:
  - 하위 에이전트 0개
  - 4단계로 바로 진행

**보통인 경우**:
  - Claude Code Task 도구를 사용하여 2개의 하위 에이전트를 **진정한 병렬**로 시작:

    **1단계: 단일 메시지로 병렬로 에이전트 시작**
    ```python
    # 중요: 여러 Task 도구 호출이 있는 단일 메시지 전송
    # 이를 통해 진정한 병렬 실행 가능

    # 에이전트 1: 패턴에 대한 코드베이스 탐색
    Task(
        subagent_type="codebase-explorer",
        description="유사한 패턴 찾기",
        prompt="""기능에 대한 유사한 패턴을 위해 기존 코드베이스 검색: '$SPEC_FEATURE'

        다음에 집중:
        - 유사한 아키텍처 구현
        - 기존 폴더 구조 및 이름 지정 규칙
        - 재사용 가능한 구성 요소 및 유틸리티
        - 통합 패턴

        반환: 유사한 기능, 아키텍처 패턴, 재사용 가능한 구성 요소, 통합 접근 방식"""
    )

    # 에이전트 2: 라이브러리 문서 연구 (필요한 경우)
    Task(
        subagent_type="library-researcher",
        description="라이브러리 문서 연구",
        prompt="""다음에 대한 최신 라이브러리 문서 연구: '$REQUIRED_LIBRARIES'

        Context7 MCP를 사용하여 다음을 가져옵니다.
        - 최신 API 사용 예제
        - 공식 문서의 모범 사례
        - 버전 호환성 참고 사항
        - 주요 변경 사항

        반환: 연구된 라이브러리, API 예제, 모범 사례, 호환성 참고 사항"""
    )
    ```

    **2단계: 에이전트가 병렬로 실행됨**
    - 두 에이전트 모두 별도의 스레드에서 동시에 실행됩니다.
    - 차단 없음 - 에이전트는 독립적으로 작동합니다.
    - Claude Code는 병렬 실행을 자동으로 조정합니다.

    **3단계: 완료 시 결과 반환**
    - Task 도구는 에이전트가 완료되면 자동으로 결과를 반환합니다.
    - 동일한 대화 컨텍스트에서 결과를 사용할 수 있습니다.

**복잡한 경우**:
  - Claude Code Task 도구를 사용하여 3개의 하위 에이전트를 **진정한 병렬**로 시작:

    **1단계: 단일 메시지로 모든 에이전트를 병렬로 시작**
    ```python
    # 중요: 세 개의 Task 도구 호출이 있는 단일 메시지 전송
    # 이를 통해 모든 에이전트의 진정한 병렬 실행 가능

    # 에이전트 1: 패턴에 대한 코드베이스 탐색
    Task(
        subagent_type="codebase-explorer",
        description="유사한 패턴 찾기",
        prompt="""기능에 대한 유사한 패턴을 위해 기존 코드베이스 검색: '$SPEC_FEATURE'

        다음에 집중:
        - 유사한 아키텍처 구현
        - 기존 폴더 구조 및 이름 지정 규칙
        - 재사용 가능한 구성 요소 및 유틸리티
        - 통합 패턴

        반환: 유사한 기능, 아키텍처 패턴, 재사용 가능한 구성 요소, 통합 접근 방식"""
    )

    # 에이전트 2: 라이브러리 문서 연구
    Task(
        subagent_type="library-researcher",
        description="라이브러리 문서 연구",
        prompt="""다음에 대한 최신 라이브러리 문서 연구: '$REQUIRED_LIBRARIES'

        Context7 MCP를 사용하여 다음을 가져옵니다.
        - 최신 API 사용 예제
        - 공식 문서의 모범 사례
        - 버전 호환성 참고 사항
        - 주요 변경 사항

        반환: 연구된 라이브러리, API 예제, 모범 사례, 호환성 참고 사항"""
    )

    # 에이전트 3: 통합 전략 설계
    Task(
        subagent_type="integration-designer",
        description="통합 설계",
        prompt="""복잡한 기능에 대한 통합 전략 설계: '$SPEC_FEATURE'

        분석:
        - 시스템 아키텍처 및 종속성
        - 통합 지점 및 인터페이스
        - 데이터 흐름 및 통신 패턴
        - 보안 및 성능 고려 사항

        반환: 통합 아키텍처, API 설계, 데이터 흐름, 위험 평가"""
    )
    ```

    **2단계: 3개의 에이전트 모두 병렬로 독립적으로 작동**
    - 코드베이스 탐색기는 기존 패턴을 찾습니다.
    - 라이브러리 연구원은 Context7 MCP를 통해 최신 문서를 가져옵니다.
    - 통합 설계자는 아키텍처를 계획합니다.
    - 진정한 병렬 실행 - 모든 에이전트가 동시에 실행됩니다.

    **3단계: 완료 시 결과 반환**
    - Task 도구는 모든 결과를 자동으로 반환합니다.
    - 동일한 대화 컨텍스트에서 결과를 사용할 수 있습니다.
    - 3.1단계에서 결과 종합

**⚠️ 에이전트 실행 규칙**:
- **codebase-explorer** → Claude Code Task 도구 사용 (Glob/Grep/Read로 코드베이스 검색)
- **library-researcher** → Claude Code Task 도구 사용 (Context7 MCP를 통해 문서 가져오기)
- **integration-designer** → Claude Code Task 도구 사용 (통합 아키텍처 설계)

**중요 - 진정한 병렬 실행**:
1. **반드시 단일 메시지**를 여러 Task 도구 호출과 함께 보내야 합니다.
2. 모든 에이전트는 별도의 스레드에서 동시에 시작됩니다.
3. 차단 없음 - 에이전트는 독립적으로 실행됩니다.
4. 완료 시 결과가 자동으로 반환됩니다.
5. 병렬 시작 예:
   ```python
   # 올바름: 단일 메시지, 여러 Task 호출
   Task(subagent_type="codebase-explorer", ...)
   Task(subagent_type="library-researcher", ...)
   Task(subagent_type="integration-designer", ...)

   # 잘못됨: 순차 메시지 (호출 간 차단)
   # 메시지 1: Task(subagent_type="codebase-explorer", ...)
   # (결과 대기)
   # 메시지 2: Task(subagent_type="library-researcher", ...)
   ```

**디버그 출력** (투명성을 위해):
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

### 3.1. 아키텍처 결정 종합

**하위 에이전트가 시작된 경우** (3단계):
- 아키텍처 통찰력 결합
- 일관성을 위해 기존 패턴 재사용
- 최신 라이브러리 모범 사례 적용
- 통합 결정 문서화
- 헌법 준수 확인 (TRUST, 파일 크기 제한)

**그렇지 않은 경우**:
- 건너뛰기 (간단한 계획)

### 4. 기본 계획 명령 실행

헌법 강화 컨텍스트로 `/speckit.plan` 실행:

```
/speckit.plan
```

**에이전트 위임**: 이는 내부적으로 **implementation-planner** 에이전트(Opus 모델)를 사용하여 아키텍처 설계, 라이브러리 선택 및 TAG 체인 계획을 수행합니다. 복잡한 기능의 경우 다음에도 위임합니다.
- **library-researcher** (Haiku) - Context7 MCP를 통한 최신 라이브러리 문서
- **codebase-explorer** (Haiku) - 기존 패턴 및 아키텍처 분석

이렇게 하면 AI가 자동으로 아키텍처 원칙을 따르는 `specs/{SPEC_ID}/plan.md`에 구현 계획이 생성됩니다.

### 5. 헌법 참조 바닥글 추가

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

### 6. 헌법 존재 확인

`.specify/memory/constitution.md`가 존재하는지 확인합니다.

```bash
ls -la .specify/memory/constitution.md
```

**찾을 수 없는 경우**:

```
⚠️ 경고: 헌법을 찾을 수 없습니다

예상: .specify/memory/constitution.md

프로젝트 헌법을 만들려면 먼저 `/ms.init`을 실행하십시오.
헌법은 이 프로젝트의 아키텍처 원칙을 정의합니다.

계획 생성은 계속되지만 헌법 참조는 깨집니다.
```

### 7. 성공 보고

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
3. AI가 헌법에 따라 TRUST 원칙을 따랐습니다 ✅

📖 계획 포함 내용:
- 모듈식 아키텍처 (독립적으로 테스트 가능한 단위)
- 파일 크기 제한 (≤500 SLOC)
- 함수 복잡성 제한 (≤10)
- 보안 고려 사항
- TAG 추적성 설계
```

## 오류 처리

### 오류 1: Spec-Kit이 초기화되지 않음

**증상**: `.specify/` 디렉토리 없음

**메시지**:

```
❌ 오류: Spec-Kit이 초기화되지 않았습니다

다음을 실행하십시오: /ms.init
```

**종료**: 코드 1

### 오류 2: 사양을 찾을 수 없음

**증상**: spec.md가 존재하지 않음

**메시지**:

```
❌ 오류: 사양을 찾을 수 없습니다

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

-   **실행보다 지침**: `/ms.plan`은 중복 파일 작업을 피하면서 `/speckit.plan`에 헌법 읽기 지침을 제공합니다.
-   **모듈식 설계 초점**: 아키텍처는 TRUST 및 단순성 우선 원칙을 존중합니다.
-   **코드 강제 없음**: 헌법은 코드로 강제되는 것이 아니라 AI의 가이드 역할을 합니다.
-   **다음 명령**: `/ms.analyze`는 계획-사양 일관성 + TRUST 준수를 확인합니다.

## 구현 세부 정보

**기본 명령**: `/speckit.plan` (내부적으로 헌법 읽기 처리)

**확장**:
- 헌법 읽기 지침 (2단계)
- 헌법 참조 바닥글 (5단계)
- 병렬 에이전트를 사용한 적응형 컨텍스트 분석 (3단계)

**도구**:
- SlashCommand (`/speckit.plan`)
- Bash (전제 조건 확인)
- Edit (헌법 참조 섹션 추가)
- Task (병렬 에이전트 시작: codebase-explorer, library-researcher, integration-designer)

## 다음 명령

`/ms.plan` 이후: spec.md 및 plan.md에서 프로젝트별 제약 조건을 추출하려면 `/ms.constitution`을 실행합니다.

---
description: "TAG 블록으로 기능 구현"
---

# /ms.implement - 추적성을 통한 구현

자동 TAG 선택 및 TAG 블록 삽입을 통해 기능을 구현합니다.

## 개요

이 명령은 **3단계 프로세스**를 수행합니다.

1.  **TAG 자동 선택**: tasks.md에서 첫 번째 미완료 TAG를 스캔합니다.
2.  **구현**: `/speckit.implement`를 실행하여 코드와 테스트를 생성합니다.
3.  **TAG 블록 삽입**: 생성된 파일에 추적성 메타데이터를 자동으로 삽입합니다.

## 사용법

```
/ms.implement
```

**인수 필요 없음** - TAG는 tasks.md에서 자동으로 선택됩니다.

**수동 TAG 지정** (선택 사항):

```
/ms.implement {TAG_ID}
```

예시:

```
/ms.implement AUTH-001
```

## 실행 단계

### 0단계: 프로젝트 컨텍스트 로드

**프로젝트 문서 자동 로드**:
- `.specify/memory/constitution.md` (헌법 - 필수)
- `AGENTS.md` (AI 지침, 코딩 표준 - 있는 경우)
- `specs/[spec-id]/spec.md` (기능 사양 - 필수)
- `specs/[spec-id]/plan.md` (구현 계획 - 필수)
- `specs/[spec-id]/tasks.md` (TAG ID가 있는 작업 목록 - 필수)

**헌법, spec.md, plan.md 또는 tasks.md가 없는 경우**:
- 오류 표시: "필수 파일이 없습니다. 먼저 `/ms.init`, `/ms.specify`, `/ms.plan` 및 `/ms.tasks`를 실행하십시오."
- 종료

**참조 키 섹션**:
- 헌법 섹션 II (단순성 우선 아키텍처 - 파일 ≤500 SLOC, 함수 ≤100 LOC)
- 헌법 섹션 V (TRUST 5 원칙 - 테스트 우선, 가독성, 통일성, 보안성, 추적 가능)
- 헌법 섹션 IX (프로젝트별 제약 조건 - **있는 경우**, `/ms.constitution`에 의해 추가됨)
- AGENTS.md (코딩 표준, 따를 패턴 - 있는 경우)

**이 문서들은 코드 품질과 일관성을 보장하기 위해 구현을 안내해야 합니다.**

### 1단계: TAG 자동 선택

**인수로 TAG_ID가 제공되지 않은 경우**:

1.  `tasks.md` 읽기
2.  미완료 작업 스캔: `[ ]` 체크박스
3.  첫 번째 미완료 작업의 `**TAG**:` 줄에서 TAG ID 추출
4.  형식 사용: `@SPEC:{TAG_ID} → @TEST:{TAG_ID} → @CODE:{TAG_ID}`

**예시**:

```markdown
## Phase 3: FR-1 Authentication

**TAG**: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001

### Implementation

-   [ ] T015 Create auth service ← 첫 번째 미완료 작업
-   [x] T014 Setup database
```

**선택된 TAG**: `AUTH-001`

**인수로 TAG_ID가 제공된 경우**:

-   제공된 TAG_ID 직접 사용
-   자동 선택 건너뛰기

**미완료 작업이 없는 경우**:

```
✅ 모든 작업 완료!

tasks.md에서 보류 중인 TAG를 찾을 수 없습니다.
모든 구현 작업이 완료되었습니다.
```

**종료**: 코드 0

### 1.5단계: Context7 MCP - 최신 라이브러리 문서 (필요한 경우)

**⚠️ 중요: 라이브러리 연구는 Gemini CLI에 위임해야 합니다.**
- `mcp__cli-bridge__gemini_cli` 도구 사용
- Gemini는 Claude보다 문서를 더 빠르게 처리합니다.
- Claude Code는 조정하고 Gemini는 실행합니다.

**작업 분석**: 구현에 외부 라이브러리가 필요합니까?

**감지 지표**:
- 작업에 라이브러리 이름 언급 (FastAPI, React, Stripe 등)
- 외부 서비스와의 통합
- 새로운 타사 종속성

**외부 라이브러리가 감지된 경우**:

  1.  **라이브러리 및 필요한 기능 식별**
  2.  **MCP cli-bridge를 통해 Gemini에 위임 (백그라운드 실행)**:
     ```python
     # 백그라운드에서 Gemini 라이브러리 연구 시작
     task_id = mcp__cli-bridge__gemini_cli(
         prompt="""다음에 대한 최신 API 문서 연구:
         - 라이브러리: fastapi
         - 주제: 백그라운드 작업
         - Context7 MCP 도구 사용
         - 반환: API 사용 예제 및 모범 사례
         """,
         background=True  # 즉시 반환
     )

     # Gemini가 연구하는 동안 Claude는 다른 작업 계속
     # ... (예: spec.md, plan.md 읽기 등)

     # 구현에 필요할 때 결과 검색
     library_docs = mcp__cli-bridge__get_task_result(
         task_id=task_id,
         wait=True  # 완료될 때까지 차단
     )
     ```
  3.  **구현에 최신 API 사용** (Gemini의 연구 기반)

**그렇지 않은 경우**:
  → 건너뛰기 (외부 라이브러리 없음)

2단계 구현에 사용할 **라이브러리 문서 저장**.

### 2단계: 헌법 주입 및 구현 실행

`/speckit.implement`를 실행하기 전에 AI에 헌법 제약 조건을 제공합니다.

```
당신은 프로젝트 헌법을 따라야 하는 코드를 구현하고 있습니다.

**헌법**: .specify/memory/constitution.md

**중요: 다음 섹션을 읽고 적용하십시오**:

**섹션 II - 단순성 우선 (필수)**:
- 파일 ≤500 SLOC (코드 파일만 - 더 크면 분할)
- 함수 ≤100 라인 (필요한 경우 도우미 함수 추출)
- 함수당 복잡성 ≤10
- 외부 종속성보다 내장 도구 선호

**섹션 V - TRUST 5 원칙 (필수)**:
- **테스트 우선**: 구현 코드보다 테스트 먼저 작성
- **가독성**: 명확한 이름 지정, 함수당 매개변수 ≤5개, 중첩 레벨 ≤4개
- **통일성**: 엄격한 타이핑 (TypeScript 엄격 모드, Python 타입 힌트)
- **보안성**: 입력 유효성 검사, 비밀을 위한 환경 변수
- **추적 가능**: 코드 구조는 spec.md 조직을 반영

**자세한 제약 조건 및 예시는 헌법을 참조하십시오.**

이제 TAG: {TAG_ID}를 구현하십시오.
```

헌법 강화 컨텍스트로 `/speckit.implement {TAG_ID}`를 실행합니다.

**에이전트 위임**: 이는 내부적으로 **tdd-implementer** 에이전트(Sonnet 모델)를 사용하여 다음을 수행합니다.
- RED: 먼저 실패하는 테스트 작성
- GREEN: 테스트를 통과하기 위한 최소 코드 구현
- REFACTOR: 테스트를 통과한 상태로 코드 품질 개선
- **ms-workflow-tag-manager** 스킬을 통해 TAG 블록 자동 삽입

이렇게 하면 헌법 원칙을 따르는 핵심 구현 파일(코드, 테스트)이 생성됩니다.

### 3단계: TAG 블록 삽입

생성된 파일을 찾아 TAG 메타데이터를 삽입합니다.

#### 3.1 생성된 파일 스캔

새로 생성된 파일 스캔:

-   **코드 파일**: `src/**/*.{ts,py}`, `backend/src/**/*.{ts,py}`, `frontend/src/**/*.{ts,py,vue}`
-   **테스트 파일**: `tests/**/*.{ts,py}`, `backend/tests/**/*.{ts,py}`, `frontend/tests/**/*.{ts,py}`
-   **사양 파일**: tasks.md TAG 체인에서

#### 3.2 TAG 블록 삽입

각 파일에 대한 TAG 블록 생성:

```bash
generate_tag_block() {
  local lang="$1"
  local tag_id="$2"
  local spec_path="$3"
  local test_path="$4"
  local date=$(date +%Y-%m-%d)

  case "$lang" in
    ts|js|tsx|jsx)
      cat <<EOF
/**
 * @CODE:${tag_id}
 * @SPEC: ${spec_path}
 * @TEST: ${test_path}
 * @CHAIN: @SPEC:${tag_id} → @TEST:${tag_id} → @CODE:${tag_id}
 * @STATUS: implemented
 * @CREATED: ${date}
 * @UPDATED: ${date}
 */
EOF
      ;;
    py)
      cat <<EOF
"""
@CODE:${tag_id}
@SPEC: ${spec_path}
@TEST: ${test_path}
@CHAIN: @SPEC:${tag_id} → @TEST:${tag_id} → @CODE:${tag_id}
@STATUS: implemented
@CREATED: ${date}
@UPDATED: ${date}
"""
EOF
      ;;
  esac
}
```

생성된 각 파일에 대해 Edit 도구를 사용하여 TAG 블록을 맨 위에 삽입합니다.

### 3.5단계: CHANGELOG.md 업데이트 (Codex)

**⚠️ 중요: CHANGELOG 업데이트는 Codex CLI에 위임해야 합니다.**

구현이 완료된 후 상세한 변경 내역으로 프로젝트 변경 로그를 업데이트합니다.

**업데이트 시기**:
- 새로운 기능 추가
- 기존 기능 변경
- 버그 수정
- 주요 변경 사항 도입

**MCP cli-bridge를 통해 Codex에 위임 (백그라운드 실행)**:

```python
# 구현된 내용 분석
implemented_changes = """
- 생성된 파일: [모든 새 파일 목록]
- 수정된 파일: [모든 수정된 파일 목록]
- 추가된 기능: [새로운 기능 설명]
- 변경된 내용: [수정 사항 설명]
- 기술적 세부 정보: [함수 이름, 클래스, 사용된 패턴]
- 근거: [이러한 변경이 이루어진 이유]
"""

# Codex를 통해 CHANGELOG 업데이트 (백그라운드 실행)
changelog_task_id = mcp__cli-bridge__codex_cli(
    prompt=f"""다음 구현으로 docs/CHANGELOG.md 업데이트:

{implemented_changes}

요구 사항:
1. Keep a Changelog 형식 따르기 (https://keepachangelog.com/)
2. [Unreleased] 섹션에 추가
3. 적절한 카테고리 사용:
   - Added: 새로운 기능
   - Changed: 기존 기능 변경
   - Deprecated: 곧 제거될 기능
   - Removed: 제거된 기능
   - Fixed: 버그 수정
   - Security: 보안 개선
4. 구체적이고 상세하게:
   - 파일 경로 및 함수 이름 포함
   - 무엇이 변경되었고 왜 변경되었는지 설명
   - 주요 변경 사항 기록
5. 기술 용어 사용 - 개발자를 위한 것입니다.

예시 형식:
## [Unreleased] - {{date}}

### Added
- `src/auth/service.py`에 새로운 `UserService.authenticate()` 메서드
  - JWT 기반 인증 구현
  - 더 나은 확장성을 위해 레거시 세션 기반 인증 대체

### Changed
- 연결 풀링을 사용하도록 `DatabaseConnection` 업데이트
  - 높은 부하에서 성능 향상
  - 연결 오버헤드 40% 감소
""",
    background=True  # 즉시 반환
)

# Claude는 다른 작업 계속 (예: TAG 블록 삽입)
# Codex는 백그라운드에서 독립적으로 CHANGELOG 업데이트

# 완료하기 전에 CHANGELOG 업데이트 완료 대기
changelog_result = mcp__cli-bridge__get_task_result(
    task_id=changelog_task_id,
    wait=True
)
```

**CHANGELOG vs README 차이점**:
- **CHANGELOG**: 모든 변경 사항의 기록 (상세하고 기술적)
- **README**: 현재 상태만 (변경 내역 없음, 사용자 친화적)

### 4단계: tasks.md 체크리스트 업데이트

**중요**: 구현 성공 후 tasks.md에서 완료된 작업을 표시합니다.

1.  `specs/{SPEC_ID}/tasks.md` 읽기
2.  현재 TAG_ID와 관련된 작업 찾기
3.  완료된 작업을 `[x]` 체크박스로 표시
4.  업데이트된 tasks.md 저장

**예시**:

```markdown
## Phase 3: FR-1 Authentication

**TAG**: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001

### Implementation

-   [x] T015 Create auth service ← 완료됨으로 표시
-   [x] T016 Write auth tests ← 완료됨으로 표시
-   [ ] T017 Add API endpoint ← 다음 작업
```

**이 단계는 필수입니다.** - tasks.md를 업데이트하지 않으면 진행 상황 추적이 중단됩니다.

### 5단계: 결과 보고

요약 표시:

```json
{
    "tag_selected": "AUTH-001",
    "auto_selected": true,
    "files_created": ["src/auth/service.ts", "tests/unit/auth.test.ts"],
    "tag_blocks_inserted": 2
}
```

다음 단계 표시:

```
✅ TAG: AUTH-001에 대한 구현 완료

📦 생성된 파일:
- src/auth/service.ts (@CODE:AUTH-001 블록 포함)
- tests/unit/auth.test.ts (@TEST:AUTH-001 블록 포함)

📋 추적성:
@SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001

🎯 다음 단계:
1. 생성된 코드 및 테스트 검토
2. 테스트 실행: npm test (또는 pytest)
3. **필수**: tasks.md 체크리스트 업데이트 - 완료된 작업을 [x]로 표시
4. 다음 TAG를 구현하려면 `/ms.implement` 다시 실행
5. 모든 TAG 블록 자동 생성 ✅
```

## TAG 블록 형식

**TypeScript**:

```typescript
/**
 * @CODE:AUTH-001
 * @SPEC: specs/001-auth-spec/spec.md
 * @TEST: tests/unit/auth.test.ts
 * @CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
 * @STATUS: implemented
 * @CREATED: 2025-10-09
 * @UPDATED: 2025-10-09
 */
```

**Python**:

```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-09
@UPDATED: 2025-10-09
"""
```

## 오류 처리

### 오류 1: 작업을 찾을 수 없음

**증상**: tasks.md가 존재하지 않거나 비어 있음

**메시지**:

```
❌ 오류: 작업을 찾을 수 없습니다

예상: specs/{SPEC_ID}/tasks.md

구현 작업을 생성하려면 먼저 `/ms.tasks`를 실행하십시오.
```

**종료**: 코드 1

### 오류 2: 보류 중인 TAG 없음

**증상**: 모든 작업 완료 (모든 `[x]` 체크박스)

**메시지**:

```
✅ 모든 작업 완료!

tasks.md에서 보류 중인 TAG를 찾을 수 없습니다.
모든 구현이 완료되었습니다.
```

**종료**: 코드 0 (성공)

### 오류 3: tasks.md에서 TAG를 찾을 수 없음

**증상**: 수동으로 지정된 TAG가 존재하지 않음

**메시지**:

```
❌ 오류: tasks.md에서 TAG를 찾을 수 없습니다

지정된 TAG: AUTH-001
사용 가능한 TAG: USER-001, PAY-001, CART-001

TAG 할당을 확인하려면 `/ms.tasks`를 실행하거나 자동 선택을 위해 인수 없이 `/ms.implement`를 사용하십시오.
```

**종료**: 코드 1

### 오류 4: 구현 실패

**증상**: `/speckit.implement`가 오류를 반환함

**메시지**:

```
❌ 오류: 구현 실패

기본 `/speckit.implement` 명령에서 오류가 발생했습니다.
위의 오류 메시지를 확인하고 다시 시도하십시오.
```

**종료**: 코드 1

## 다음 단계

`/ms.implement` 이후:

1.  생성된 파일에서 TAG 블록 확인
2.  테스트를 실행하여 구현 확인
3.  **필수**: tasks.md 체크리스트 업데이트 - 완료된 작업을 [x]로 표시
4.  다음 TAG를 구현하려면 `/ms.implement` 다시 실행
5.  커밋 메시지에 TAG ID를 포함하여 변경 사항 커밋

## 참고

-   **자동 TAG 선택**: 수동 TAG 지정 필요 없음 (tasks.md 스캔)
-   **수동 TAG 옵션**: 필요한 경우 TAG를 명시적으로 지정할 수 있음
-   **자동 TAG 블록**: 모든 생성된 파일에 삽입됨
-   **100% 추적성**: SPEC→TEST→CODE 체인 완료

## 구현 세부 정보

**도구**: SlashCommand (/speckit.implement), Read, Edit, Write, Bash

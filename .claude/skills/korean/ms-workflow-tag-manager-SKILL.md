---
name: ms-workflow-tag-manager
description: 추적성을 위한 TAG 블록(SPEC→TEST→CODE 체인)을 생성합니다. /ms.implement로 기능을 구현하거나 TAG 메타데이터를 생성할 때 사용합니다.
allowed-tools:
  - Read
  - Bash
  - Grep
version: 1.0.0
created: 2025-10-26
---

# 워크플로우: TAG 관리자

## 스킬 메타데이터
| 필드 | 값 |
| --- | --- |
| 버전 | 1.0.0 |
| 생성일 | 2025-10-26 |
| 허용된 도구 | Read, Bash, Grep |
| 자동 로드 | `/ms.implement`, `/ms.tasks`, 코드 구현 |
| 트리거 큐 | TAG 생성, 추적성, 구현 추적 |

## 기능

My-Spec 워크플로우 추적성을 위한 TAG 블록 수명 주기를 관리합니다:
- 언어별 TAG 블록 생성(Python, TypeScript, JavaScript)
- 완전한 @SPEC → @TEST → @CODE 체인 생성
- 고유한 TAG ID 할당 보장
- docstrings 및 JSDoc 주석을 위한 템플릿 제공

## 사용 시기

- 구현 중 (`/ms.implement`가 이 스킬을 자동으로 호출)
- 새 기능 파일 생성 시
- 기존 코드에 TAG 메타데이터 추가 시
- TAG 체인 완전성 검증 시
- 수동 삽입을 위한 TAG 템플릿 생성 시

## 작동 방식

### TAG ID 형식

**구조**: `<도메인>-<번호>`

**예시**:
- `AUTH-001`: 인증 기능 #1
- `HOOKS-002`: 훅 시스템 기능 #2
- `LDOCS-003`: 살아있는 문서 기능 #3
- `SKILLS-004`: 스킬 시스템 기능 #4

**도메인 접두사** (My-Spec MoAI 통합):
- `HOOKS-XXX`: 훅 시스템 기능
- `SKILLS-XXX`: 스킬 구현
- `LDOCS-XXX`: 살아있는 문서 시스템
- `AGENTS-XXX`: 하위 에이전트
- `INFRA-XXX`: 인프라 작업

### TAG 체인 구조

**완전한 체인**:
```
@SPEC:TAG-ID → @TEST:TAG-ID → @CODE:TAG-ID → @DOC:TAG-ID (선택 사항)
```

**파일 위치**:
- `@SPEC:TAG-ID`: `specs/<spec-id>/spec.md`
- `@TEST:TAG-ID`: `tests/` (테스트 파일)
- `@CODE:TAG-ID`: `src/` 또는 구현 파일
- `@DOC:TAG-ID`: `docs/` (선택 사항, API 문서용)

### TAG 블록 템플릿

#### 파이썬 (Docstring)

```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

def authenticate_user(email: str, password: str) -> AuthResult:
    """이메일과 비밀번호로 사용자를 인증합니다."""
    pass
```

#### 타입스크립트/자바스크립트 (JSDoc)

```typescript
/**
 * @CODE:AUTH-001
 * @SPEC: specs/001-auth-spec/spec.md
 * @TEST: tests/unit/auth.test.ts
 * @CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
 * @STATUS: implemented
 * @CREATED: 2025-10-26
 * @UPDATED: 2025-10-26
 */
export function authenticateUser(email: string, password: string): AuthResult {
  // 구현
}
```

#### Go (블록 주석)

```go
/*
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/auth_test.go
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
*/
func AuthenticateUser(email string, password string) (*AuthResult, error) {
    // 구현
}
```

### TAG 블록 생성 알고리즘

**함수 서명**:
```python
def generate_tag_block(
    lang: str,
    tag_id: str,
    spec_path: str,
    test_path: str,
    status: str = "implemented",
    doc_path: str = None
) -> str:
    """
    주어진 언어에 대한 TAG 블록을 생성합니다.

    Args:
        lang: 언어 코드 (python, typescript, javascript, go, rust)
        tag_id: TAG ID (예: AUTH-001)
        spec_path: 사양 파일 경로
        test_path: 테스트 파일 경로
        status: 구현 상태 (implemented, in_progress, planned)
        doc_path: 선택적 문서 경로

    Returns:
        서식화된 TAG 블록 문자열
    """
```

**구현**:
```python
from datetime import date

def generate_tag_block(lang, tag_id, spec_path, test_path, status="implemented", doc_path=None):
    today = date.today().strftime("%Y-%m-%d")

    chain = f"@SPEC:{tag_id} → @TEST:{tag_id} → @CODE:{tag_id}"
    if doc_path:
        chain += f" → @DOC:{tag_id}"

    content = f"""@CODE:{tag_id}
@SPEC: {spec_path}
@TEST: {test_path}
@CHAIN: {chain}
@STATUS: {status}
@CREATED: {today}
@UPDATED: {today}"""

    if doc_path:
        content = f"""@CODE:{tag_id}
@SPEC: {spec_path}
@TEST: {test_path}
@DOC: {doc_path}
@CHAIN: {chain}
@STATUS: {status}
@CREATED: {today}
@UPDATED: {today}"""

    # 언어별 서식
    if lang in ["python"]:
        return f'"""
{content}
"""'
    elif lang in ["typescript", "javascript"]:
        return f'/**
 * ' + content.replace('\n', '\n * ') + '\n */'
    elif lang in ["go", "rust", "c", "cpp"]:
        return f'/*
{content}
*/'
    else:
        return f'# {content.replace(chr(10), chr(10) + "# ")}'
```

### TAG 고유성 검증

**중복 TAG ID 확인**:
```bash
# 전체 코드베이스에서 TAG ID 검색
rg "@(SPEC|TEST|CODE|DOC):AUTH-001" -n specs/ tests/ src/ docs/

# 발생 횟수 계산
rg "@SPEC:AUTH-001" -c specs/
```

**검증 규칙**:
- 각 TAG ID는 프로젝트 전체에서 고유해야 합니다.
- @SPEC, @TEST, @CODE에서 사용된 동일한 TAG ID가 체인을 형성합니다.
- 중복된 @SPEC:ID 또는 @CODE:ID는 오류를 나타냅니다.

### TAG 자동 삽입 워크플로우

**`/ms.implement` 실행 시**:

1. tasks.md에서 **TAG ID 선택** (첫 번째 미완료 작업)
2. @SPEC:TAG-ID 참조를 찾기 위해 **spec.md 읽기**
3. @TEST:TAG-ID 블록으로 **테스트 파일 생성**
4. @CODE:TAG-ID 블록으로 **코드 파일 생성**
5. `rg` 스캔으로 **체인 확인**

**파일 배치**:
- 테스트 파일: `tests/`에서 `src/` 구조 미러링
- 코드 파일: plan.md의 프로젝트 구조 따르기
- TAG 블록: 항상 파일/함수/클래스 수준

## 입력
- TAG ID (예: AUTH-001)
- 언어 (python, typescript, go 등)
- 사양 파일 경로
- 테스트 파일 경로
- 선택적 문서 파일 경로

## 출력
- 서식화된 TAG 블록 (언어별)
- 완전한 @SPEC → @TEST → @CODE 체인
- 검증 상태 (고유/중복)
- 삽입 위치 권장 사항

## 사용 예시

**시나리오**: AUTH-001 인증 기능 구현

**1단계**: 테스트 파일용 TAG 블록 생성 (파이썬)
```python
# 입력
tag_id = "AUTH-001"
spec_path = "specs/001-auth-spec/spec.md"
test_path = "tests/unit/test_auth_service.py"

# 출력
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""
```

**2단계**: 파일 상단에 삽입
```python
"""
@TEST:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@CODE: src/auth/service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

import pytest
from src.auth.service import authenticate_user

def test_authenticate_user_success():
    result = authenticate_user("test@example.com", "password123")
    assert result.success is True
```

**3단계**: TAG 체인 확인
```bash
rg "@(SPEC|TEST|CODE):AUTH-001" -n specs/ tests/ src/

# 예상 출력:
# specs/001-auth-spec/spec.md:15:@SPEC:AUTH-001
# tests/unit/test_auth_service.py:2:@TEST:AUTH-001
# src/auth/service.py:2:@CODE:AUTH-001
```

## TAG 상태 값

| 상태 | 의미 | 사용 시기 |
|---|---|---|
| `planned` | 아직 시작되지 않은 기능 | `/ms.tasks` 생성 중 |
| `in_progress` | 현재 구현 중 | TDD RED/GREEN 단계 중 |
| `implemented` | 코드 완료, 테스트 통과 | REFACTOR 단계 후 |
| `reviewed` | 코드 검토 승인 | `/ms.review` 후 |
| `deprecated` | 더 이상 사용되지 않음 | 기능 폐기 시 |

## TAG 업데이트 프로토콜

**태그된 코드 수정 시**:
1. `@UPDATED` 타임스탬프를 현재 날짜로 업데이트
2. `@CREATED` 타임스탬프는 변경하지 않음
3. 기능이 크게 변경되면 새 TAG ID 고려
4. 요구 사항이 변경되면 해당 @SPEC 업데이트

**예시**:
```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-27  ← 수정 후 타임스탬프 업데이트
"""
```

## /ms.implement와의 통합

**자동 TAG 블록 삽입**:

```bash
# 사용자 실행
/ms.implement

# 시스템:
# 1. tasks.md에서 TAG-ID 자동 선택
# 2. @SPEC:TAG-ID에 대한 spec.md 읽기
# 3. @TEST:TAG-ID로 테스트 파일 생성
# 4. @CODE:TAG-ID로 코드 파일 생성
# 5. 이 스킬을 사용하여 TAG 블록 삽입
# 6. 체인 무결성 확인
```

**수동 TAG 생성 불필요** - `/ms.implement`가 자동으로 처리합니다.

## 관련 스킬
- `ms-foundation-trust`: TAG 체인 검증 (추적 가능 원칙)
- `moai-foundation-tags`: TAG 인벤토리 및 고아 감지
- `moai-alfred-tag-scanning`: TAG 스캐닝 및 보고

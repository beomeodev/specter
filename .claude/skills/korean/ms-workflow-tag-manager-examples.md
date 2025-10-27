# TAG 관리자 스킬 - 예제

## 예제 1: 파이썬 TAG 블록 생성

**시나리오**: 인증 서비스를 위한 TAG 블록 생성

```python
# 입력 매개변수
tag_id = "AUTH-001"
lang = "python"
spec_path = "specs/001-auth-spec/spec.md"
test_path = "tests/unit/test_auth_service.py"
status = "implemented"

# 생성된 TAG 블록
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

# 전체 구현
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

from typing import Optional
from dataclasses import dataclass

@dataclass
class AuthResult:
    success: bool
    token: Optional[str]
    error: Optional[str]

def authenticate_user(email: str, password: str) -> AuthResult:
    """
    이메일과 비밀번호로 사용자를 인증합니다.

    Args:
        email: 사용자 이메일 주소
        password: 사용자 비밀번호

    Returns:
        성공 상태 및 선택적 토큰이 포함된 AuthResult

    Raises:
        ValueError: 이메일 또는 비밀번호가 비어 있는 경우
    """
    if not email or not password:
        return AuthResult(success=False, token=None, error="잘못된 자격 증명")

    # 여기에 인증 로직
    return AuthResult(success=True, token="jwt_token_here", error=None)
```

---

## 예제 2: 타입스크립트 TAG 블록 생성

**시나리오**: React 인증 훅을 위한 TAG 블록 생성

```typescript
// 입력 매개변수
const tagId = "AUTH-002";
const lang = "typescript";
const specPath = "specs/001-auth-spec/spec.md";
const testPath = "tests/unit/useAuth.test.ts";

// 생성된 TAG 블록
/**
 * @CODE:AUTH-002
 * @SPEC: specs/001-auth-spec/spec.md
 * @TEST: tests/unit/useAuth.test.ts
 * @CHAIN: @SPEC:AUTH-002 → @TEST:AUTH-002 → @CODE:AUTH-002
 * @STATUS: implemented
 * @CREATED: 2025-10-26
 * @UPDATED: 2025-10-26
 */

// 전체 구현
/**
 * @CODE:AUTH-002
 * @SPEC: specs/001-auth-spec/spec.md
 * @TEST: tests/unit/useAuth.test.ts
 * @CHAIN: @SPEC:AUTH-002 → @TEST:AUTH-002 → @CODE:AUTH-002
 * @STATUS: implemented
 * @CREATED: 2025-10-26
 * @UPDATED: 2025-10-26
 */

import { useState, useCallback } from 'react';

interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  error: string | null;
}

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    token: null,
    error: null,
  });

  const login = useCallback(async (email: string, password: string) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('인증 실패');
      }

      const { token } = await response.json();
      setAuthState({
        isAuthenticated: true,
        token,
        error: null,
      });
    } catch (error) {
      setAuthState({
        isAuthenticated: false,
        token: null,
        error: error instanceof Error ? error.message : '알 수 없는 오류',
      });
    }
  }, []);

  return { ...authState, login };
}
```

---

## 예제 3: TAG 체인 유효성 검사

**시나리오**: AUTH-001에 대한 전체 TAG 체인 확인

```bash
# 모든 TAG 참조 검색
rg "@(SPEC|TEST|CODE):AUTH-001" -n specs/ tests/ src/

# 예상 출력 (전체 체인):
specs/001-auth-spec/spec.md:42:## @SPEC:AUTH-001 - 사용자 인증
tests/unit/test_auth_service.py:2:@TEST:AUTH-001
src/auth/service.py:2:@CODE:AUTH-001

# 고유성 확인
rg "@CODE:AUTH-001" -c src/
# 출력: 1 (코드에 한 번만 나타나야 함)

# 고아 TAG 찾기 (SPEC 없는 CODE)
rg "@CODE:AUTH-003" -l src/          # CODE 존재
rg "@SPEC:AUTH-003" -l specs/        # SPEC 누락 → 고아!
```

---

## 예제 4: 다국어 TAG 템플릿

**시나리오**: 다국어 프로젝트(파이썬 + 타입스크립트)를 위한 TAG 블록 생성

### 파이썬 서비스

```python
"""
@CODE:API-001
@SPEC: specs/002-api-spec/spec.md
@TEST: tests/unit/test_api_service.py
@CHAIN: @SPEC:API-001 → @TEST:API-001 → @CODE:API-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1")

class UserCreate(BaseModel):
    email: str
    password: str

@router.post("/users")
async def create_user(user: UserCreate):
    """새 사용자 계정을 생성합니다."""
    # 구현
    pass
```

### 타입스크립트 프론트엔드

```typescript
/**
 * @CODE:API-002
 * @SPEC: specs/002-api-spec/spec.md
 * @TEST: tests/unit/api.test.ts
 * @CHAIN: @SPEC:API-002 → @TEST:API-002 → @CODE:API-002
 * @STATUS: implemented
 * @CREATED: 2025-10-26
 * @UPDATED: 2025-10-26
 */

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async createUser(email: string, password: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/v1/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error(`API 오류: ${response.statusText}`);
    }
  }
}
```

---

## 예제 5: TAG 상태 수명 주기

**시나리오**: 계획부터 배포까지 TAG 상태 추적

### 1단계: 계획 (tasks.md)

```markdown
## 1단계: 인증

**TAG**: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001

### 구현

-   [ ] T001 인증 서비스 생성
    - 상태: planned
```

### 2단계: TDD RED 단계 (테스트 파일)

```python
"""
@TEST:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@CODE: src/auth/service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: in_progress  ← TDD RED 단계
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

import pytest
from src.auth.service import authenticate_user

def test_authenticate_user_success():
    result = authenticate_user("test@example.com", "password123")
    assert result.success is True
    assert result.token is not None

def test_authenticate_user_invalid_credentials():
    result = authenticate_user("test@example.com", "wrong_password")
    assert result.success is False
    assert result.error == "잘못된 자격 증명"
```

### 3단계: TDD GREEN 단계 (구현)

```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented  ← 테스트 통과
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

from typing import Optional
from dataclasses import dataclass

@dataclass
class AuthResult:
    success: bool
    token: Optional[str]
    error: Optional[str]

def authenticate_user(email: str, password: str) -> AuthResult:
    # 테스트를 통과하기 위한 최소 구현
    if email == "test@example.com" and password == "password123":
        return AuthResult(success=True, token="jwt_token", error=None)
    return AuthResult(success=False, token=None, error="잘못된 자격 증명")
```

### 4단계: 코드 검토 후

```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: reviewed  ← 코드 검토 승인
@CREATED: 2025-10-26
@UPDATED: 2025-10-27
"""
# ... (구현 변경 없음)
```

---

## 예제 6: 중복 TAG 감지

**시나리오**: 중복 TAG ID 방지

```bash
# 새 TAG를 만들기 전에 중복 확인
TAG_ID="AUTH-001"

# 기존 TAG 검색
rg "@(SPEC|TEST|CODE):${TAG_ID}" -n specs/ tests/ src/ docs/

# 유형별 발생 횟수 계산
echo "SPEC 수:"
rg "@SPEC:${TAG_ID}" -c specs/

echo "TEST 수:"
rg "@TEST:${TAG_ID}" -c tests/

echo "CODE 수:"
rg "@CODE:${TAG_ID}" -c src/

# 예상: 유형별 1회 발생 (SPEC, TEST, CODE)
# 1회 이상이면 중복 감지!
```

**중복 처리**:
```bash
# 중복 TAG가 있는 모든 파일 찾기
rg "@CODE:AUTH-001" -l src/

# 출력 (문제):
# src/auth/service.py
# src/auth/utils.py  ← 중복! AUTH-002를 사용해야 함

# 수정: TAG ID 재할당
# src/auth/utils.py: AUTH-001 → AUTH-005로 변경
```

---

## 예제 7: /ms.implement를 통한 TAG 자동 삽입

**시나리오**: `/ms.implement`가 자동으로 TAG 블록 생성

```bash
# 사용자 실행
/ms.implement

# 시스템 실행:
# 1. tasks.md 읽기 → 첫 번째 미완료 작업 찾기
# 2. TAG ID 추출: AUTH-001
# 3. specs/001-auth-spec/spec.md 읽기
# 4. 테스트 파일 생성: tests/unit/test_auth_service.py
#    @TEST:AUTH-001 블록 자동 삽입
# 5. 코드 파일 생성: src/auth/service.py
#    @CODE:AUTH-001 블록 자동 삽입
# 6. 체인 무결성 확인: rg '@(SPEC|TEST|CODE):AUTH-001' -n
```

**결과** (자동 생성된 파일):

**tests/unit/test_auth_service.py**:
```python
"""
@TEST:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@CODE: src/auth/service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: in_progress
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

import pytest
from src.auth.service import authenticate_user

def test_authenticate_user_success():
    # 테스트 구현
    pass
```

**src/auth/service.py**:
```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: in_progress
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

def authenticate_user(email: str, password: str):
    # 구현
    pass
```

---

## 예제 8: 문서 참조가 있는 TAG

**시나리오**: API 문서에 대한 선택적 @DOC 참조 포함

```python
"""
@CODE:API-001
@SPEC: specs/002-api-spec/spec.md
@TEST: tests/unit/test_api_endpoints.py
@DOC: docs/api/API-001.md
@CHAIN: @SPEC:API-001 → @TEST:API-001 → @CODE:API-001 → @DOC:API-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1")

class UserResponse(BaseModel):
    id: int
    email: str

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """
    ID로 사용자를 검색합니다.

    자세한 API 문서는 @DOC:API-001을 참조하십시오.
    """
    # 구현
    pass
```

**해당 docs/api/API-001.md**:
```markdown
# @DOC:API-001 - 사용자 가져오기 엔드포인트

@SPEC: specs/002-api-spec/spec.md
@TEST: tests/unit/test_api_endpoints.py
@CODE: src/api/routes/users.py

## 엔드포인트

`GET /api/v1/users/{user_id}`

## 요청

- 경로 매개변수: `user_id` (정수, 필수)

## 응답

200 OK:
```json
{
  "id": 123,
  "email": "user@example.com"
}
```

404 찾을 수 없음:
```json
{
  "detail": "사용자를 찾을 수 없습니다"
}
```
```

---

## 예제 9: 리팩토링 후 TAG 업데이트

**시나리오**: 코드 리팩토링 후 TAG 타임스탬프 업데이트

**리팩토링 전**:
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

def authenticate_user(email, password):
    # 이전 구현 (타입 힌트 없음)
    pass
```

**리팩토링 후** (타입 힌트로 개선, TAG ID 유지):
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

from typing import Optional
from dataclasses import dataclass

@dataclass
class AuthResult:
    success: bool
    token: Optional[str]
    error: Optional[str]

def authenticate_user(email: str, password: str) -> AuthResult:
    """타입 힌트로 개선된 구현."""
    # 리팩토링된 구현
    pass
```

**참고**: 기능이 변경되지 않고 코드 품질만 개선되었기 때문에 TAG ID(AUTH-001)는 동일하게 유지됩니다.

---

## 예제 10: TAG 체인 보고서

**시나리오**: TAG 체인 무결성 보고서 생성

```bash
#!/bin/bash
# TAG 체인 보고서 생성

echo "=== TAG 체인 무결성 보고서 ==="
echo ""

# 모든 SPEC TAG 찾기
SPEC_TAGS=$(rg '@SPEC:([A-Z]+-[0-9]+)' -or '$1' specs/ | sort -u)

for TAG in $SPEC_TAGS; do
    echo "$TAG 체인 확인 중..."

    SPEC_COUNT=$(rg "@SPEC:$TAG" -c specs/ 2>/dev/null || echo 0)
    TEST_COUNT=$(rg "@TEST:$TAG" -c tests/ 2>/dev/null || echo 0)
    CODE_COUNT=$(rg "@CODE:$TAG" -c src/ 2>/dev/null || echo 0)

    if [ "$SPEC_COUNT" -gt 0 ] && [ "$TEST_COUNT" -gt 0 ] && [ "$CODE_COUNT" -gt 0 ]; then
        echo "  ✅ 전체 체인: @SPEC → @TEST → @CODE"
    else
        echo "  ❌ 끊어진 체인:"
        echo "     @SPEC: $SPEC_COUNT"
        echo "     @TEST: $TEST_COUNT"
        echo "     @CODE: $CODE_COUNT"
    fi
    echo ""
done
```

**예제 출력**:
```
=== TAG 체인 무결성 보고서 ===

AUTH-001 체인 확인 중...
  ✅ 전체 체인: @SPEC → @TEST → @CODE

AUTH-002 체인 확인 중...
  ❌ 끊어진 체인:
     @SPEC: 1
     @TEST: 1
     @CODE: 0  ← 구현 누락

HOOKS-001 체인 확인 중...
  ✅ 전체 체인: @SPEC → @TEST → @CODE
```

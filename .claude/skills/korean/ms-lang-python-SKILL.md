---
name: ms-lang-python
description: My-Spec 워크플로우를 위한 pytest 8.4.2, ruff 0.13.1, mypy 1.8.0을 사용한 파이썬 3.13+ 모범 사례. 파이썬 코드를 작성하거나 검토할 때 사용합니다.
allowed-tools:
  - Read
  - Bash
  - Grep
version: 1.0.0
created: 2025-10-26
keywords: ['python', 'testing', 'pytest', 'mypy', 'ruff', 'async', 'fastapi', 'pydantic']
---

# 언어: 파이썬 3.13+ 전문가

## 스킬 메타데이터
| 필드 | 값 |
| --- | --- |
| 버전 | 1.0.0 |
| 생성일 | 2025-10-26 |
| 파이썬 지원 | 3.13.1 (최신), 3.12.7 (LTS) |
| 허용된 도구 | Read, Bash, Grep |
| 자동 로드 | `.py` 파일 감지 시 주문형 |
| 트리거 큐 | 파이썬 파일, pytest, 비동기 패턴, FastAPI |

## 기능

My-Spec TDD 개발을 위한 **파이썬 3.13+ 전문 지식**을 제공하며 다음을 포함합니다.

- ✅ **테스트 프레임워크**: pytest 8.4.2 (픽스처, 비동기, 매개변수화)
- ✅ **코드 품질**: ruff 0.13.1 (통합 린터 + 포맷터, black/pylint 대체)
- ✅ **타입 안전성**: mypy 1.8.0 + Pydantic 2.7.0 (정적 + 런타임 유효성 검사)
- ✅ **패키지 관리**: uv 0.9.3 (pip보다 10배 빠름)
- ✅ **파이썬 3.13 기능**: PEP 695 (타입 매개변수), PEP 701 (f-문자열), PEP 698 (@override)
- ✅ **비동기/대기**: asyncio.TaskGroup, 컨텍스트 변수, 동시성 패턴
- ✅ **헌법 준수**: TRUST 5 원칙, ≤500 SLOC 파일, ≤10 복잡성

## 사용 시기

**자동 트리거**:
- 파이썬 코드 토론, `.py` 파일
- "파이썬 테스트 작성", "pytest 사용 방법", "파이썬 타입 힌트"
- 파이썬 SPEC 구현 (`/ms.implement`)
- 비동기 패턴 요청, FastAPI 개발

**수동 호출**:
- TRUST 5 준수를 위한 파이썬 코드 검토
- 파이썬 마이크로서비스 설계 (FastAPI 권장)
- 파이썬 오류 또는 성능 문제 해결
- 파이썬 3.12에서 3.13으로 마이그레이션

## 작동 방식 (모범 사례)

### 1. 테스트 프레임워크 (pytest 8.4.2)

**unittest보다 pytest를 사용하는 이유**
- 🎯 **더 간단한 구문** (클래스 상용구 없음)
- 🔧 **강력한 픽스처** (종속성 주입)
- ✅ **더 나은 단언** (상세한 오류 메시지)
- ⚡ pytest-asyncio를 사용한 **비동기 지원**

**테스트 구조**:
```python
# tests/test_calculator.py
import pytest
from src.calculator import add

def test_add_positive_numbers():
    """양의 정수 덧셈을 확인합니다."""
    assert add(2, 3) == 5

@pytest.mark.asyncio
async def test_async_operation():
    """pytest-asyncio로 비동기 함수를 테스트합니다."""
    result = await async_fetch_data()
    assert result is not None

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-2, 3, 1),
    (0, 0, 0),
])
def test_add_parametrized(a, b, expected):
    """여러 경우에 대한 매개변수화된 테스트입니다."""
    assert add(a, b) == expected
```

**핵심 사항**:
- ✅ pytest 사용 (unittest 아님)
- ✅ 테스트당 하나의 단언 (명확성)
- ✅ 설정/해제를 위한 픽스처
- ✅ 비동기 테스트를 위한 `pytest.mark.asyncio`
- ✅ 데이터 기반 테스트를 위한 `pytest.mark.parametrize`
- ✅ 품질 게이트에 의해 시행되는 커버리지 ≥85%

**CLI 명령**:
```bash
pytest                              # 모든 테스트 실행
pytest -v                           # 상세 출력
pytest --cov=src --cov-report=term # 커버리지 보고서 (≥85% 필요)
pytest -k "pattern"                 # 일치하는 테스트 실행
pytest -m asyncio                   # 비동기 테스트만 실행
pytest --maxfail=1                  # 첫 번째 실패 후 중지
```

### 2. 코드 품질 (ruff 0.13.1 — 새로운 표준)

**black + pylint + isort보다 ruff를 사용하는 이유**
- ⚡ pylint보다 **100배 빠름**
- 🔧 **단일 도구** (린팅 + 서식 지정 + 가져오기 정렬)
- ✅ black의 **드롭인 대체**
- 🎯 **Rust로 작성** (매우 빠름)

**구성** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
target-version = "py313"
exclude = [".venv", "build", "dist", "__pycache__"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle 오류
    "F",   # pyflakes
    "W",   # pycodestyle 경고
    "I",   # isort (가져오기 정렬)
    "N",   # pep8-naming
    "UP",  # pyupgrade (파이썬 3.13 기능 사용)
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "C90", # mccabe (복잡성)
]
ignore = ["E501"]  # 줄 길이는 포맷터에서 처리

[tool.ruff.lint.mccabe]
max-complexity = 10  # 헌법 요구 사항

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["F401", "F811"]  # 테스트에서 사용하지 않는 가져오기 허용

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**CLI 명령**:
```bash
ruff check .                        # 모든 파일 린트
ruff check --fix .                  # 자동 수정으로 린트
ruff format .                       # 서식 지정 (black 대체)
ruff check --select C90 .           # 복잡성만 확인
ruff check --select I .             # 가져오기만 확인
```

### 3. 타입 안전성 (mypy 1.8.0 + Pydantic 2.7.0)

**정적 타입 확인** (mypy):
```python
from typing import override

class Parent:
    def method(self, x: int) -> str:
        return str(x)

class Child(Parent):
    @override  # 파이썬 3.13 PEP 698 — mypy가 재정의를 확인합니다.
    def method(self, x: int) -> str:
        return str(x * 2)
```

**구성** (`pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

**런타임 유효성 검사** (Pydantic 2.7.0):
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int = Field(gt=0)           # 0보다 커야 함
    name: str = Field(min_length=1)
    email: str                      # 이메일로 자동 유효성 검사
    age: int = Field(ge=13, le=120)
```

**CLI 명령**:
```bash
mypy .                              # 모든 파일 타입 확인
mypy --strict src/                  # 프로덕션 코드에 대한 엄격 모드 (권장)
mypy --show-column-numbers .        # 정확한 오류 위치 표시
```

### 4. 패키지 관리 (uv 0.9.3)

**pip/poetry보다 uv를 사용하는 이유**
- ⚡ pip보다 **10배 빠름**
- 🔧 **제로 구성** (pyproject.toml과 함께 작동)
- ✅ 기존 도구와 **호환**
- 🎯 **Rust로 작성**

**설정**:
```bash
# uv 설치
pip install uv

# 가상 환경 생성
uv venv                             # .venv/ 생성
source .venv/bin/activate           # 활성화 (리눅스/맥)
.venv\Scripts\activate              # 활성화 (윈도우)

# 종속성 설치
uv add pytest ruff mypy             # pyproject.toml에 추가
uv add --dev pytest-asyncio         # 개발 종속성으로 추가
uv sync                             # 모두 설치 (잠금 파일에서)
```

**pyproject.toml** (uv 구성):
```toml
[project]
name = "my-project"
version = "1.0.0"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.115.0",
    "pydantic>=2.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.4.2",
    "pytest-asyncio",
    "pytest-cov",
    "ruff>=0.13.1",
    "mypy>=1.8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 5. 파이썬 3.13 새로운 기능

#### PEP 695 — 타입 매개변수 구문
```python
# 이전 (3.12)
from typing import TypeVar, Generic
T = TypeVar('T')
class Stack(Generic[T]):
    def push(self, item: T) -> None: ...

# 신규 (3.13)
class Stack[T]:
    def push(self, item: T) -> None: ...
```

#### PEP 701 — 개선된 F-문자열
```python
# 중첩된 f-문자열 및 임의의 표현식
user = {"name": "Alice", "age": 30}
print(f"사용자: {user['name']}, 나이: {user['age']}")  # 작동합니다!

# 중첩된 f-문자열
x = 10
print(f"결과: {f'{x:>10}'}")  # 3.13에서 작동합니다!
```

#### PEP 698 — 재정의 데코레이터
```python
from typing import override

class Parent:
    def method(self) -> None: ...

class Child(Parent):
    @override  # mypy가 이것이 실제로 재정의되었는지 확인합니다.
    def method(self) -> None: ...
```

### 6. 비동기 패턴 (파이썬 3.13)

**TaskGroup** (`asyncio.gather`보다 깔끔함):
```python
import asyncio

async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_user(1))
        task2 = tg.create_task(fetch_posts(1))
        # 작업이 동시에 실행됩니다.
        # 예외가 자동으로 전파됩니다.

asyncio.run(main())
```

**컨텍스트 변수** (비동기에서 스레드 안전):
```python
from contextvars import ContextVar

request_id = ContextVar('request_id', default=None)

async def handle_request(req_id):
    token = request_id.set(req_id)
    # 생성된 모든 작업이 이 컨텍스트 변수를 상속합니다.
    await process_async()
    request_id.reset(token)
```

### 7. 보안 모범 사례

**Secrets 모듈** (토큰 생성):
```python
import secrets

api_key = secrets.token_urlsafe(32)  # 안전한 임의 토큰
nonce = secrets.token_bytes(16)       # 암호화 nonce
```

**보안 해싱** (md5 대신 sha256 사용):
```python
import hashlib

# ✅ 보안
hash_obj = hashlib.sha256(b"password")

# ❌ 비보안 (파이썬 3.13에서 제거됨)
# hash_obj = hashlib.md5(b"password")  # ValueError!
```

**입력 유효성 검사** (Pydantic):
```python
from pydantic import BaseModel, Field, field_validator

class UserInput(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    email: str  # 자동 이메일 유효성 검사
    age: int = Field(ge=13, le=120)

    @field_validator("username")
    @classmethod
    def username_no_special_chars(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError("사용자 이름은 영숫자여야 합니다.")
        return v
```

## 헌법 준수

**My-Spec 요구 사항**:
- ✅ 파일 ≤500 SLOC (더 크면 분할)
- ✅ 함수 ≤100 라인
- ✅ 함수당 복잡성 ≤10
- ✅ 테스트 커버리지 ≥85%
- ✅ 엄격한 타이핑 활성화
- ✅ 모든 파일에 TAG 블록 존재

**파일 크기 확인**:
```bash
# SLOC 계산 (주석/빈 줄 제외)
ruff check . --select C901 --statistics
```

**복잡성 확인**:
```bash
# Ruff는 복잡성을 자동으로 확인합니다 (최대=10).
ruff check . --select C90
```

## 도구 버전 매트릭스 (2025-10-26)

| 도구 | 버전 | 목적 | 상태 |
|---|---|---|---|
| **파이썬** | 3.13.1 | 런타임 | ✅ 최신 |
| **pytest** | 8.4.2 | 테스트 | ✅ 현재 |
| **ruff** | 0.13.1 | 린트/서식 | ✅ 새로운 표준 |
| **mypy** | 1.8.0 | 타입 확인 | ✅ 현재 |
| **uv** | 0.9.3 | 패키지 관리자 | ✅ 권장 |
| **FastAPI** | 0.115.0 | 웹 프레임워크 | ✅ 최신 |
| **Pydantic** | 2.7.0 | 유효성 검사 | ✅ 최신 |

## 예제 워크플로

**설정** (uv + 파이썬 3.13):
```bash
uv venv --python 3.13               # 파이썬 3.13으로 venv 생성
source .venv/bin/activate
uv add pytest ruff mypy fastapi pydantic
```

**TDD 루프**:
```bash
pytest                              # RED: 테스트 실패 확인
# [코드 구현]
pytest                              # GREEN: 테스트 통과 확인
ruff check --fix .                  # REFACTOR: 코드 품질 수정
```

**품질 게이트** (커밋 전):
```bash
pytest --cov=src --cov-report=term # 커버리지 ≥85%?
ruff check .                        # 린트 통과?
mypy --strict .                     # 타입 확인 통과?
```

## 모범 사례

✅ **해야 할 일**:
- 린팅 + 서식에 ruff 사용 (black + pylint 아님)
- 정확한 파이썬 버전 지정: `requires-python = ">=3.13"`
- 모든 테스트에 pytest 사용
- mypy 엄격 모드 활성화
- 각 커밋 전에 품질 게이트 실행
- 패키지 관리에 uv 사용 (10배 빠름)
- 공용 API에 독스트링 추가
- f-문자열 사용 (PEP 701은 중첩 표현식 지원)

❌ **하지 말아야 할 일**:
- black + pylint 사용 (사용되지 않음, 대신 ruff 사용)
- md5 해싱 사용 (파이썬 3.13에서 제거됨)
- pytest와 unittest 혼합
- 커버리지 요구 사항 무시 (<85% 실패)
- 오래된 타입 힌트 구문 사용 (PEP 695 `class Foo[T]:` 사용)
- 오류 처리 없이 `asyncio.gather` 사용 (대신 TaskGroup 사용)

## My-Spec과의 통합

**TAG 블록 형식** (파이썬):
```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/test_auth.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

class AuthService:
    # 구현...
```

**테스트 TAG 블록**:
```python
"""
@TEST:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@CODE: src/services/auth.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: passing
"""

def test_auth_service():
    # 테스트...
```

## 참조 (최신 문서)

- **파이썬 3.13**: https://docs.python.org/3.13/ (2025-10-26 접속)
- **pytest 8.4.2**: https://docs.pytest.org/en/stable/ (2025-10-26 접속)
- **ruff 0.13.1**: https://docs.astral.sh/ruff/ (2025-10-26 접속)
- **mypy 1.8.0**: https://mypy.readthedocs.io/ (2025-10-26 접속)
- **uv 0.9.3**: https://docs.astral.sh/uv/ (2025-10-26 접속)
- **FastAPI 0.115.0**: https://fastapi.tiangolo.com/ (2025-10-26 접속)
- **Pydantic 2.7.0**: https://docs.pydantic.dev/ (2025-10-26 접속)

## 변경 로그

- **v1.0.0** (2025-10-26): pytest 8.4.2, ruff 0.13.1, mypy 1.8.0, 파이썬 3.13 기능, 헌법 준수를 포함한 My-Spec 워크플로우용 초기 파이썬 스킬

## 함께 사용하면 좋은 것

- `ms-foundation-trust` (TRUST 5 유효성 검사)
- `ms-foundation-constitution` (파일 크기/복잡성 확인)
- `ms-workflow-tag-manager` (TAG 블록 생성)
- `ms-workflow-living-docs` (API 문서 동기화)

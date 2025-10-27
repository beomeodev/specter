# 파이썬 3.13 코드 예제

pytest 8.4.2, ruff 0.13.1, mypy 1.8.0 및 My-Spec TRUST 5 원칙을 사용한 최신 파이썬 개발을 위한 프로덕션 준비 예제입니다.

---

## 예제 1: pytest 8.4.2(픽스처 및 비동기 테스트 포함)

### 테스트 파일: `tests/test_user_service.py`

```python
"""
@TEST:USER-001
@SPEC: specs/001-user-service/spec.md
@CODE: src/services/user_service.py
@CHAIN: @SPEC:USER-001 → @TEST:USER-001 → @CODE:USER-001
@STATUS: passing
"""
import pytest
from unittest.mock import AsyncMock
from src.services.user_service import UserService
from src.models.user import User


@pytest.fixture
def user_service():
    """모의 종속성이 있는 UserService 인스턴스를 제공하는 픽스처입니다."""
    return UserService(db_client=AsyncMock())


@pytest.fixture
def sample_user():
    """테스트를 위한 샘플 사용자 인스턴스를 제공하는 픽스처입니다."""
    return User(id=1, name="Alice", email="alice@example.com")


def test_user_creation(user_service, sample_user):
    """유효한 데이터로 사용자 생성을 확인합니다."""
    result = user_service.validate_user(sample_user)
    assert result is True
    assert sample_user.id > 0


@pytest.mark.asyncio
async def test_fetch_user_async(user_service):
    """모의 데이터베이스로 비동기 사용자 가져오기를 테스트합니다."""
    user_service.db_client.fetch_user.return_value = User(
        id=1, name="Bob", email="bob@example.com"
    )

    user = await user_service.fetch_user(user_id=1)

    assert user is not None
    assert user.name == "Bob"
    user_service.db_client.fetch_user.assert_called_once_with(1)


@pytest.mark.parametrize("user_id,expected_name", [
    (1, "Alice"),
    (2, "Bob"),
    (3, "Charlie"),
])
@pytest.mark.asyncio
async def test_fetch_multiple_users(user_service, user_id, expected_name):
    """여러 사용자 가져오기를 위한 매개변수화된 테스트입니다."""
    user_service.db_client.fetch_user.return_value = User(
        id=user_id, name=expected_name, email=f"{expected_name.lower()}@example.com"
    )

    user = await user_service.fetch_user(user_id=user_id)

    assert user.name == expected_name
```

**주요 기능**:
- ✅ 종속성 주입을 위한 pytest 픽스처
- ✅ 비동기 테스트를 위한 `@pytest.mark.asyncio`
- ✅ 데이터 기반 테스트를 위한 `@pytest.mark.parametrize`
- ✅ 비동기 작업을 모의하기 위한 AsyncMock
- ✅ 테스트당 하나의 단언(명확성)
- ✅ 추적성을 위한 TAG 블록

**실행 명령**:
```bash
pytest tests/test_user_service.py -v
pytest tests/test_user_service.py --cov=src.services --cov-report=term
```

---

## 예제 2: ruff 0.13.1 구성 및 워크플로

### 프로젝트 구성: `pyproject.toml`

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

### 예제 소스 파일: `src/utils/formatter.py`

```python
"""
@CODE:FMT-001
@SPEC: specs/002-formatter/spec.md
@TEST: tests/test_formatter.py
@CHAIN: @SPEC:FMT-001 → @TEST:FMT-001 → @CODE:FMT-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""
from typing import override


class Formatter:
    """기본 포맷터 클래스입니다."""

    def format(self, text: str) -> str:
        """기본 동작으로 텍스트 서식을 지정합니다."""
        return text.strip()


class UppercaseFormatter(Formatter):
    """텍스트를 대문자로 변환하는 포맷터입니다."""

    @override  # 파이썬 3.13 PEP 698
    def format(self, text: str) -> str:
        """텍스트를 대문자로 서식을 지정합니다."""
        return text.strip().upper()


class LowercaseFormatter(Formatter):
    """텍스트를 소문자로 변환하는 포맷터입니다."""

    @override
    def format(self, text: str) -> str:
        """텍스트를 소문자로 서식을 지정합니다."""
        return text.strip().lower()


def format_user_info(name: str, age: int, city: str) -> str:
    """중첩된 f-문자열(파이썬 3.13 PEP 701)로 사용자 정보를 서식 지정합니다."""
    # 파이썬 3.13은 중첩된 f-문자열 및 임의의 표현식을 허용합니다.
    return f"사용자: {name}, 세부 정보: {f'나이: {age}, 도시: {city.upper()}'}"
```

**워크플로 명령**:
```bash
# 문제 린트 및 자동 수정
ruff check . --fix

# 코드 서식 지정 (black 대체)
ruff format .

# 특정 규칙 확인
ruff check --select I .           # 가져오기 정렬만
ruff check --select C90 .         # 복잡성만
ruff check --select UP .          # 파이썬 3.13 업그레이드 제안

# 수정될 내용 표시 (드라이 런)
ruff check --show-fixes .
```

---

## 예제 3: mypy 1.8.0 및 Pydantic 2.7.0을 사용한 타입 안전성

### 모델 정의: `src/models/product.py`

```python
"""
@CODE:PROD-001
@SPEC: specs/003-product-model/spec.md
@TEST: tests/test_product.py
@CHAIN: @SPEC:PROD-001 → @TEST:PROD-001 → @CODE:PROD-001
@STATUS: implemented
"""
from typing import override
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal


class Product(BaseModel):
    """Pydantic 2.7.0을 통한 런타임 유효성 검사를 사용하는 제품 모델입니다."""

    id: int = Field(gt=0, description="제품 ID는 양수여야 합니다.")
    name: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0, decimal_places=2)
    stock: int = Field(ge=0, description="재고는 음수일 수 없습니다.")

    @field_validator("name")
    @classmethod
    def name_must_not_contain_special_chars(cls, v: str) -> str:
        """이름에 영숫자만 포함되어 있는지 확인합니다."""
        if not v.replace(" ", "").isalnum():
            raise ValueError("제품 이름은 영숫자여야 합니다.")
        return v

    def apply_discount(self, percentage: float) -> Decimal:
        """제품 가격에 할인율을 적용합니다."""
        if not 0 <= percentage <= 100:
            raise ValueError("할인율은 0에서 100 사이여야 합니다.")
        discount_amount = self.price * Decimal(percentage / 100)
        return self.price - discount_amount


class GenericContainer[T]:  # 파이썬 3.13 PEP 695 타입 매개변수
    """파이썬 3.13 타입 매개변수 구문을 사용하는 제네릭 컨테이너입니다."""

    def __init__(self, items: list[T]) -> None:
        self.items = items

    def first(self) -> T | None:
        """첫 번째 항목을 반환하거나 비어 있으면 None을 반환합니다."""
        return self.items[0] if self.items else None

    def add(self, item: T) -> None:
        """컨테이너에 항목을 추가합니다."""
        self.items.append(item)


def process_products(products: GenericContainer[Product]) -> list[str]:
    """제품을 처리하고 이름을 반환합니다."""
    return [p.name for p in products.items if p.stock > 0]
```

### mypy 구성: `pyproject.toml`

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

**실행 명령**:
```bash
mypy .                             # 모든 파일 타입 확인
mypy --strict src/                 # 프로덕션 코드에 대한 엄격 모드
mypy --show-column-numbers .       # 정확한 오류 위치 표시
```

---

## 예제 4: 비동기 핸들러가 있는 FastAPI 0.115.0 REST API

### API 서버: `src/api/main.py`

```python
"""
@CODE:API-001
@SPEC: specs/004-product-api/spec.md
@TEST: tests/test_api.py
@CHAIN: @SPEC:API-001 → @TEST:API-001 → @CODE:API-001
@STATUS: implemented
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Annotated
import asyncio


app = FastAPI(title="제품 API", version="1.0.0")


class ProductCreate(BaseModel):
    """제품 생성 요청 스키마입니다."""
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class ProductResponse(BaseModel):
    """제품 응답 스키마입니다."""
    id: int
    name: str
    price: float
    stock: int


# 종속성 주입
async def get_db_session():
    """시뮬레이션된 데이터베이스 세션입니다(실제 DB로 교체)."""
    yield {"connection": "active"}


@app.get("/")
async def root():
    """상태 확인 엔드포인트입니다."""
    return {"status": "ok", "version": "1.0.0"}


@app.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    db: Annotated[dict, Depends(get_db_session)]
):
    """새 제품을 생성합니다(비동기 핸들러)."""
    await asyncio.sleep(0.1)  # 비동기 데이터베이스 작업 시뮬레이션

    product_data = {
        "id": 1,
        "name": product.name,
        "price": product.price,
        "stock": product.stock,
    }

    return ProductResponse(**product_data)


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Annotated[dict, Depends(get_db_session)]
):
    """ID로 제품을 검색합니다(비동기 핸들러)."""
    await asyncio.sleep(0.1)  # 비동기 데이터베이스 조회 시뮬레이션

    if product_id == 999:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")

    return ProductResponse(id=product_id, name="샘플 제품", price=29.99, stock=100)


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """ValueError에 대한 전역 예외 처리기입니다."""
    return JSONResponse(
        status_code=400,
        content={"error": "유효성 검사 실패", "detail": str(exc)},
    )
```

### API 테스트: `tests/test_api.py`

```python
"""
@TEST:API-001
@SPEC: specs/004-product-api/spec.md
@CODE: src/api/main.py
@STATUS: passing
"""
import pytest
from httpx import AsyncClient, ASGITransport
from src.api.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """상태 확인 엔드포인트를 테스트합니다."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "version": "1.0.0"}


@pytest.mark.asyncio
async def test_create_product():
    """제품 생성 엔드포인트를 테스트합니다."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/products", json={
            "name": "테스트 제품",
            "price": 19.99,
            "stock": 50,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "테스트 제품"
        assert data["price"] == 19.99


@pytest.mark.asyncio
async def test_get_product_not_found():
    """존재하지 않는 ID로 제품 검색을 테스트합니다."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/products/999")
        assert response.status_code == 404
```

**실행 명령**:
```bash
# 개발 서버 시작
uvicorn src.api.main:app --reload

# 테스트 실행
pytest tests/test_api.py -v --cov=src.api
```

---

## 예제 5: asyncio.TaskGroup 동시성 패턴

### 데이터 페처 서비스: `src/services/data_fetcher.py`

```python
"""
@CODE:FETCH-001
@SPEC: specs/005-data-fetcher/spec.md
@TEST: tests/test_data_fetcher.py
@CHAIN: @SPEC:FETCH-001 → @TEST:FETCH-001 → @CODE:FETCH-001
@STATUS: implemented
"""
import asyncio
from typing import Any
from contextvars import ContextVar


request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


class DataFetcher:
    """TaskGroup을 사용하여 여러 소스에서 동시에 데이터를 가져옵니다."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def fetch_user(self, user_id: int) -> dict[str, Any]:
        """API에서 사용자 데이터를 가져옵니다."""
        await asyncio.sleep(0.1)  # 네트워크 지연 시뮬레이션
        return {"id": user_id, "name": f"사용자{user_id}"}

    async def fetch_posts(self, user_id: int) -> list[dict[str, Any]]:
        """API에서 사용자 게시물을 가져옵니다."""
        await asyncio.sleep(0.15)  # 네트워크 지연 시뮬레이션
        return [
            {"id": 1, "user_id": user_id, "title": "게시물 1"},
            {"id": 2, "user_id": user_id, "title": "게시물 2"},
        ]

    async def fetch_comments(self, user_id: int) -> list[dict[str, Any]]:
        """API에서 사용자 댓글을 가져옵니다."""
        await asyncio.sleep(0.12)  # 네트워크 지연 시뮬레이션
        return [
            {"id": 1, "user_id": user_id, "text": "댓글 1"},
        ]

    async def fetch_user_profile(self, user_id: int) -> dict[str, Any]:
        """
        TaskGroup을 사용하여 동시에 전체 사용자 프로필을 가져옵니다.

        asyncio.gather에 비해 TaskGroup의 장점:
        - 자동 예외 전파
        - 구조화된 동시성(취소 안전성)
        - 더 깔끔한 오류 처리
        """
        async with asyncio.TaskGroup() as tg:
            user_task = tg.create_task(self.fetch_user(user_id))
            posts_task = tg.create_task(self.fetch_posts(user_id))
            comments_task = tg.create_task(self.fetch_comments(user_id))
            # 모든 작업이 여기서 동시에 실행됩니다.

        # TaskGroup이 종료된 후 모든 작업이 완료됩니다.
        return {
            "user": user_task.result(),
            "posts": posts_task.result(),
            "comments": comments_task.result(),
        }

    async def fetch_multiple_users(self, user_ids: list[int]) -> list[dict[str, Any]]:
        """여러 사용자 프로필을 동시에 가져옵니다."""
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(self.fetch_user_profile(user_id))
                for user_id in user_ids
            ]

        return [task.result() for task in tasks]


async def process_request(request_id: str) -> dict[str, Any]:
    """컨텍스트 변수 추적을 사용하여 요청을 처리합니다."""
    token = request_id_var.set(request_id)

    try:
        fetcher = DataFetcher(base_url="https://api.example.com")
        result = await fetcher.fetch_user_profile(user_id=1)

        # 요청 ID로 로그(모든 비동기 컨텍스트에서 사용 가능)
        current_request_id = request_id_var.get()
        print(f"요청 {current_request_id} 완료")

        return result
    finally:
        request_id_var.reset(token)


async def main():
    """TaskGroup을 사용한 DataFetcher 사용 예제입니다."""
    fetcher = DataFetcher(base_url="https://api.example.com")

    # 단일 사용자 프로필 가져오기
    profile = await fetcher.fetch_user_profile(user_id=1)
    print(f"프로필: {profile}")

    # 여러 사용자 동시에 가져오기
    profiles = await fetcher.fetch_multiple_users([1, 2, 3])
    print(f"가져온 프로필 수: {len(profiles)}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 예제 6: 품질 게이트 워크플로

### 품질 게이트 스크립트: `scripts/quality_gate.sh`

```bash
#!/bin/bash
# 파이썬 프로젝트용 품질 게이트 스크립트
# TRUST 5 원칙 적용

set -e

echo "🔍 파이썬 품질 게이트 실행 중..."

# 1. 타입 확인 (통합 - 타입 안전성)
echo "📋 타입 확인 중..."
mypy --strict src/

# 2. 린팅 (가독성 - 코드 품질)
echo "🧹 린팅 중..."
ruff check .

# 3. 테스트 (테스트 우선 - 커버리지 ≥85%)
echo "🧪 테스트 실행 중..."
pytest --cov=src --cov-report=term-missing --cov-fail-under=85

echo "✅ 품질 게이트 통과!"
```

### pyproject.toml 스크립트

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
asyncio_mode = "auto"
addopts = "-v --strict-markers"

[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "**/__init__.py"]

[tool.coverage.report]
fail_under = 85
precision = 2
show_missing = true
```

---

## 빠른 참조

### 새 프로젝트 설정 (uv)

```bash
# 파이썬 3.13으로 프로젝트 생성
uv venv --python 3.13
source .venv/bin/activate

# 종속성 설치
uv add pytest pytest-asyncio ruff mypy fastapi uvicorn httpx pydantic

# 개발 종속성 추가
uv add --dev pytest-cov pytest-mock
```

### 품질 게이트 명령

```bash
# 커버리지와 함께 모든 테스트 실행
pytest --cov=src --cov-report=term-missing --cov-report=html

# 린트 및 서식 지정
ruff check . --fix
ruff format .

# 타입 확인
mypy --strict src/

# 전체 품질 게이트 (커밋 전 실행)
pytest --cov=src --cov-report=term --cov-fail-under=85 && ruff check . && mypy .
```

### 도구 버전

| 패키지 | 버전 | 목적 |
|---|---|---|
| pytest | 8.4.2 | 테스트 프레임워크 |
| pytest-asyncio | 최신 | 비동기 테스트 지원 |
| pytest-cov | 최신 | 커버리지 보고 |
| ruff | 0.13.1 | 린팅 및 서식 지정 |
| mypy | 1.8.0 | 정적 타입 확인 |
| uv | 0.9.3 | 패키지 관리 |
| FastAPI | 0.115.0 | 웹 프레임워크 |
| Pydantic | 2.7.0 | 데이터 유효성 검사 |
| httpx | 최신 | 비동기 HTTP 클라이언트 |

---

모든 예제는 My-Spec TRUST 5 원칙 및 헌법 제약 조건(≤500 SLOC, ≤10 복잡성, ≥85% 커버리지)을 따릅니다.

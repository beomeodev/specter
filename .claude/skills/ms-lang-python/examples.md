# Python Code Examples

Production-ready examples for modern Python development with pytest, ruff, mypy, and SPECTER TRUST 5 principles.

---

## Contents

- Example 1: pytest 8.4.2 with Fixtures and Async Tests
- Example 2: ruff 0.13.1 Configuration and Workflow
- Example 3: Type Safety with mypy 1.8.0 and Pydantic 2.7.0
- Example 4: FastAPI 0.115.0 REST API with Async Handlers
- Example 5: asyncio.TaskGroup Concurrent Patterns
- Example 6: Quality Gate Workflow
- Quick Reference

## Example 1: pytest 8.4.2 with Fixtures and Async Tests

### Test File: `tests/test_user_service.py`

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
    """Fixture providing a UserService instance with mocked dependencies."""
    return UserService(db_client=AsyncMock())


@pytest.fixture
def sample_user():
    """Fixture providing a sample User instance for tests."""
    return User(id=1, name="Alice", email="alice@example.com")


def test_user_creation(user_service, sample_user):
    """Verify user creation with valid data."""
    result = user_service.validate_user(sample_user)
    assert result is True
    assert sample_user.id > 0


@pytest.mark.asyncio
async def test_fetch_user_async(user_service):
    """Test async user fetching with mocked database."""
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
    """Parametrized test for fetching multiple users."""
    user_service.db_client.fetch_user.return_value = User(
        id=user_id, name=expected_name, email=f"{expected_name.lower()}@example.com"
    )

    user = await user_service.fetch_user(user_id=user_id)

    assert user.name == expected_name
```

**Key Features**:
- ✅ pytest fixtures for dependency injection
- ✅ `@pytest.mark.asyncio` for async tests
- ✅ `@pytest.mark.parametrize` for data-driven tests
- ✅ AsyncMock for mocking async operations
- ✅ One assertion per test (clarity)
- ✅ TAG block for traceability

**Run Commands**:
```bash
pytest tests/test_user_service.py -v
pytest tests/test_user_service.py --cov=src.services --cov-report=term
```

---

## Example 2: ruff 0.13.1 Configuration and Workflow

### Project Configuration: `pyproject.toml`

```toml
[tool.ruff]
line-length = 100
target-version = "py313"
exclude = [".venv", "build", "dist", "__pycache__"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "W",   # pycodestyle warnings
    "I",   # isort (import sorting)
    "N",   # pep8-naming
    "UP",  # pyupgrade (use Python 3.13 features)
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "C90", # mccabe (complexity)
]
ignore = ["E501"]  # Line length handled by formatter

[tool.ruff.lint.mccabe]
max-complexity = 10  # Constitution requirement

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["F401", "F811"]  # Allow unused imports in tests

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Example Source File: `src/utils/formatter.py`

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
    """Base formatter class."""

    def format(self, text: str) -> str:
        """Format text with default behavior."""
        return text.strip()


class UppercaseFormatter(Formatter):
    """Formatter that converts text to uppercase."""

    @override  # Python 3.13 PEP 698
    def format(self, text: str) -> str:
        """Format text to uppercase."""
        return text.strip().upper()


class LowercaseFormatter(Formatter):
    """Formatter that converts text to lowercase."""

    @override
    def format(self, text: str) -> str:
        """Format text to lowercase."""
        return text.strip().lower()


def format_user_info(name: str, age: int, city: str) -> str:
    """Format user information with nested f-strings (Python 3.13 PEP 701)."""
    # Python 3.13 allows nested f-strings and arbitrary expressions
    return f"User: {name}, Details: {f'Age: {age}, City: {city.upper()}'}"
```

**Workflow Commands**:
```bash
# Lint and auto-fix issues
ruff check . --fix

# Format code (replaces black)
ruff format .

# Check specific rules
ruff check --select I .           # Import sorting only
ruff check --select C90 .         # Complexity only
ruff check --select UP .          # Python 3.13 upgrade suggestions

# Show what would be fixed (dry-run)
ruff check --show-fixes .
```

---

## Example 3: Type Safety with mypy 1.8.0 and Pydantic 2.7.0

### Model Definition: `src/models/product.py`

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
    """Product model with runtime validation via Pydantic 2.7.0."""

    id: int = Field(gt=0, description="Product ID must be positive")
    name: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0, decimal_places=2)
    stock: int = Field(ge=0, description="Stock cannot be negative")

    @field_validator("name")
    @classmethod
    def name_must_not_contain_special_chars(cls, v: str) -> str:
        """Validate that name contains only alphanumeric characters."""
        if not v.replace(" ", "").isalnum():
            raise ValueError("Product name must be alphanumeric")
        return v

    def apply_discount(self, percentage: float) -> Decimal:
        """Apply discount percentage to product price."""
        if not 0 <= percentage <= 100:
            raise ValueError("Discount must be between 0 and 100")
        discount_amount = self.price * Decimal(percentage / 100)
        return self.price - discount_amount


class GenericContainer[T]:  # Python 3.13 PEP 695 type parameters
    """Generic container using Python 3.13 type parameter syntax."""

    def __init__(self, items: list[T]) -> None:
        self.items = items

    def first(self) -> T | None:
        """Return first item or None if empty."""
        return self.items[0] if self.items else None

    def add(self, item: T) -> None:
        """Add item to container."""
        self.items.append(item)


def process_products(products: GenericContainer[Product]) -> list[str]:
    """Process products and return their names."""
    return [p.name for p in products.items if p.stock > 0]
```

### mypy Configuration: `pyproject.toml`

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

**Run Commands**:
```bash
mypy .                             # Type check all files
mypy --strict src/                 # Strict mode for production code
mypy --show-column-numbers .       # Show precise error locations
```

---

## Example 4: FastAPI 0.115.0 REST API with Async Handlers

### API Server: `src/api/main.py`

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


app = FastAPI(title="Product API", version="1.0.0")


class ProductCreate(BaseModel):
    """Product creation request schema."""
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class ProductResponse(BaseModel):
    """Product response schema."""
    id: int
    name: str
    price: float
    stock: int


# Dependency injection
async def get_db_session():
    """Simulated database session (replace with actual DB)."""
    yield {"connection": "active"}


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}


@app.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    db: Annotated[dict, Depends(get_db_session)]
):
    """Create a new product (async handler)."""
    await asyncio.sleep(0.1)  # Simulate async database operation

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
    """Retrieve product by ID (async handler)."""
    await asyncio.sleep(0.1)  # Simulate async database lookup

    if product_id == 999:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse(id=product_id, name="Sample Product", price=29.99, stock=100)


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Global exception handler for ValueError."""
    return JSONResponse(
        status_code=400,
        content={"error": "Validation failed", "detail": str(exc)},
    )
```

### API Tests: `tests/test_api.py`

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
    """Test health check endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "version": "1.0.0"}


@pytest.mark.asyncio
async def test_create_product():
    """Test product creation endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/products", json={
            "name": "Test Product",
            "price": 19.99,
            "stock": 50,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Product"
        assert data["price"] == 19.99


@pytest.mark.asyncio
async def test_get_product_not_found():
    """Test product retrieval with non-existent ID."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/products/999")
        assert response.status_code == 404
```

**Run Commands**:
```bash
# Start development server
uvicorn src.api.main:app --reload

# Run tests
pytest tests/test_api.py -v --cov=src.api
```

---

## Example 5: asyncio.TaskGroup Concurrent Patterns

### Data Fetcher Service: `src/services/data_fetcher.py`

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
    """Fetch data from multiple sources concurrently using TaskGroup."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def fetch_user(self, user_id: int) -> dict[str, Any]:
        """Fetch user data from API."""
        await asyncio.sleep(0.1)  # Simulate network delay
        return {"id": user_id, "name": f"User{user_id}"}

    async def fetch_posts(self, user_id: int) -> list[dict[str, Any]]:
        """Fetch user posts from API."""
        await asyncio.sleep(0.15)  # Simulate network delay
        return [
            {"id": 1, "user_id": user_id, "title": "Post 1"},
            {"id": 2, "user_id": user_id, "title": "Post 2"},
        ]

    async def fetch_comments(self, user_id: int) -> list[dict[str, Any]]:
        """Fetch user comments from API."""
        await asyncio.sleep(0.12)  # Simulate network delay
        return [
            {"id": 1, "user_id": user_id, "text": "Comment 1"},
        ]

    async def fetch_user_profile(self, user_id: int) -> dict[str, Any]:
        """
        Fetch complete user profile concurrently using TaskGroup.

        TaskGroup advantages over asyncio.gather:
        - Automatic exception propagation
        - Structured concurrency (cancellation safety)
        - Cleaner error handling
        """
        async with asyncio.TaskGroup() as tg:
            user_task = tg.create_task(self.fetch_user(user_id))
            posts_task = tg.create_task(self.fetch_posts(user_id))
            comments_task = tg.create_task(self.fetch_comments(user_id))
            # All tasks run concurrently here

        # After TaskGroup exits, all tasks are complete
        return {
            "user": user_task.result(),
            "posts": posts_task.result(),
            "comments": comments_task.result(),
        }

    async def fetch_multiple_users(self, user_ids: list[int]) -> list[dict[str, Any]]:
        """Fetch multiple user profiles concurrently."""
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(self.fetch_user_profile(user_id))
                for user_id in user_ids
            ]

        return [task.result() for task in tasks]


async def process_request(request_id: str) -> dict[str, Any]:
    """Process request with context variable tracking."""
    token = request_id_var.set(request_id)

    try:
        fetcher = DataFetcher(base_url="https://api.example.com")
        result = await fetcher.fetch_user_profile(user_id=1)

        # Log with request ID (available in all async contexts)
        current_request_id = request_id_var.get()
        print(f"Request {current_request_id} completed")

        return result
    finally:
        request_id_var.reset(token)


async def main():
    """Example usage of DataFetcher with TaskGroup."""
    fetcher = DataFetcher(base_url="https://api.example.com")

    # Fetch single user profile
    profile = await fetcher.fetch_user_profile(user_id=1)
    print(f"Profile: {profile}")

    # Fetch multiple users concurrently
    profiles = await fetcher.fetch_multiple_users([1, 2, 3])
    print(f"Fetched {len(profiles)} profiles")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Example 6: Quality Gate Workflow

### Quality Gate Script: `scripts/quality_gate.sh`

```bash
#!/bin/bash
# Quality gate script for Python projects
# Enforces TRUST 5 principles

set -e

echo "🔍 Running Python Quality Gate..."

# 1. Type Check (Unified - Type Safety)
echo "📋 Type checking..."
mypy --strict src/

# 2. Linting (Readable - Code Quality)
echo "🧹 Linting..."
ruff check .

# 3. Testing (Test First - Coverage ≥85%)
echo "🧪 Running tests..."
pytest --cov=src --cov-report=term-missing --cov-fail-under=85

echo "✅ Quality gate passed!"
```

### pyproject.toml Scripts

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

## Quick Reference

### Setup New Project (uv)

```bash
# Create project with Python 3.13
uv venv --python 3.13
source .venv/bin/activate

# Install dependencies
uv add pytest pytest-asyncio ruff mypy fastapi uvicorn httpx pydantic

# Add development dependencies
uv add --dev pytest-cov pytest-mock
```

### Quality Gate Commands

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=term-missing --cov-report=html

# Lint and format
ruff check . --fix
ruff format .

# Type check
mypy --strict src/

# Full quality gate (run before commit)
pytest --cov=src --cov-report=term --cov-fail-under=85 && ruff check . && mypy .
```

### Tool Versions

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | 8.4.2 | Testing framework |
| pytest-asyncio | latest | Async test support |
| pytest-cov | latest | Coverage reporting |
| ruff | 0.13.1 | Linting & formatting |
| mypy | 1.8.0 | Static type checking |
| uv | 0.9.3 | Package management |
| FastAPI | 0.115.0 | Web framework |
| Pydantic | 2.7.0 | Data validation |
| httpx | latest | Async HTTP client |

---

All examples follow SPECTER TRUST 5 principles and Constitution constraints (≤700 SLOC production / tests no limit, ≤10 complexity, ≥85% coverage).

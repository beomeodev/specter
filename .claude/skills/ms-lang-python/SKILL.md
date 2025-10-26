---
name: ms-lang-python
description: Python 3.13+ best practices with pytest 8.4.2, ruff 0.13.1, mypy 1.8.0 for My-Spec workflow. Use when writing or reviewing Python code.
allowed-tools:
  - Read
  - Bash
  - Grep
version: 1.0.0
created: 2025-10-26
keywords: ['python', 'testing', 'pytest', 'mypy', 'ruff', 'async', 'fastapi', 'pydantic']
---

# Language: Python 3.13+ Expert

## Skill Metadata
| Field | Value |
| ----- | ----- |
| Version | 1.0.0 |
| Created | 2025-10-26 |
| Python Support | 3.13.1 (latest), 3.12.7 (LTS) |
| Allowed tools | Read, Bash, Grep |
| Auto-load | On demand when `.py` files detected |
| Trigger cues | Python files, pytest, async patterns, FastAPI |

## What it does

Provides **Python 3.13+ expertise** for My-Spec TDD development, including:

- ✅ **Testing Framework**: pytest 8.4.2 (fixtures, asyncio, parametrization)
- ✅ **Code Quality**: ruff 0.13.1 (unified linter + formatter, replaces black/pylint)
- ✅ **Type Safety**: mypy 1.8.0 + Pydantic 2.7.0 (static + runtime validation)
- ✅ **Package Management**: uv 0.9.3 (10x faster than pip)
- ✅ **Python 3.13 Features**: PEP 695 (type params), PEP 701 (f-strings), PEP 698 (@override)
- ✅ **Async/Await**: asyncio.TaskGroup, context variables, concurrent patterns
- ✅ **Constitution Compliance**: TRUST 5 principles, ≤500 SLOC files, ≤10 complexity

## When to use

**Automatic triggers**:
- Python code discussions, `.py` files
- "Writing Python tests", "How to use pytest", "Python type hints"
- Python SPEC implementation (`/ms.implement`)
- Async pattern requests, FastAPI development

**Manual invocation**:
- Review Python code for TRUST 5 compliance
- Design Python microservices (FastAPI recommended)
- Troubleshoot Python errors or performance issues
- Migrate from Python 3.12 to 3.13

## How it works (Best Practices)

### 1. Testing Framework (pytest 8.4.2)

**Why pytest over unittest?**
- 🎯 **Simpler syntax** (no class boilerplate)
- 🔧 **Powerful fixtures** (dependency injection)
- ✅ **Better assertions** (detailed error messages)
- ⚡ **Async support** with pytest-asyncio

**Test Structure**:
```python
# tests/test_calculator.py
import pytest
from src.calculator import add

def test_add_positive_numbers():
    """Verify addition of positive integers."""
    assert add(2, 3) == 5

@pytest.mark.asyncio
async def test_async_operation():
    """Test async functions with pytest-asyncio."""
    result = await async_fetch_data()
    assert result is not None

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-2, 3, 1),
    (0, 0, 0),
])
def test_add_parametrized(a, b, expected):
    """Parametrized test for multiple cases."""
    assert add(a, b) == expected
```

**Key Points**:
- ✅ Use pytest (not unittest)
- ✅ One assertion per test (clarity)
- ✅ Fixtures for setup/teardown
- ✅ `pytest.mark.asyncio` for async tests
- ✅ `pytest.mark.parametrize` for data-driven tests
- ✅ Coverage ≥85% enforced by quality gate

**CLI Commands**:
```bash
pytest                              # Run all tests
pytest -v                           # Verbose output
pytest --cov=src --cov-report=term # Coverage report (≥85% required)
pytest -k "pattern"                 # Run matching tests
pytest -m asyncio                   # Run async tests only
pytest --maxfail=1                  # Stop after first failure
```

### 2. Code Quality (ruff 0.13.1 — NEW STANDARD)

**Why ruff over black + pylint + isort?**
- ⚡ **100x faster** than pylint
- 🔧 **Single tool** (linting + formatting + import sorting)
- ✅ **Drop-in replacement** for black
- 🎯 **Written in Rust** (blazing fast)

**Configuration** (`pyproject.toml`):
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

**CLI Commands**:
```bash
ruff check .                        # Lint all files
ruff check --fix .                  # Lint with auto-fix
ruff format .                       # Format (replaces black)
ruff check --select C90 .           # Check complexity only
ruff check --select I .             # Check imports only
```

### 3. Type Safety (mypy 1.8.0 + Pydantic 2.7.0)

**Static Type Checking** (mypy):
```python
from typing import override

class Parent:
    def method(self, x: int) -> str:
        return str(x)

class Child(Parent):
    @override  # Python 3.13 PEP 698 — mypy validates override
    def method(self, x: int) -> str:
        return str(x * 2)
```

**Configuration** (`pyproject.toml`):
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

**Runtime Validation** (Pydantic 2.7.0):
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int = Field(gt=0)           # Must be > 0
    name: str = Field(min_length=1)
    email: str                      # Auto-validated as email
    age: int = Field(ge=13, le=120)
```

**CLI Commands**:
```bash
mypy .                              # Type check all files
mypy --strict src/                  # Strict mode (recommended)
mypy --show-column-numbers .        # Precise error locations
```

### 4. Package Management (uv 0.9.3)

**Why uv over pip/poetry?**
- ⚡ **10x faster** than pip
- 🔧 **Zero config** (works with pyproject.toml)
- ✅ **Compatible** with existing tools
- 🎯 **Written in Rust**

**Setup**:
```bash
# Install uv
pip install uv

# Create virtual environment
uv venv                             # Creates .venv/
source .venv/bin/activate           # Activate (Linux/Mac)
.venv\Scripts\activate              # Activate (Windows)

# Install dependencies
uv add pytest ruff mypy             # Add to pyproject.toml
uv add --dev pytest-asyncio         # Add as dev dependency
uv sync                             # Install all (from lock file)
```

**pyproject.toml** (uv config):
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

### 5. Python 3.13 New Features

#### PEP 695 — Type Parameter Syntax
```python
# OLD (3.12)
from typing import TypeVar, Generic
T = TypeVar('T')
class Stack(Generic[T]):
    def push(self, item: T) -> None: ...

# NEW (3.13)
class Stack[T]:
    def push(self, item: T) -> None: ...
```

#### PEP 701 — Improved F-Strings
```python
# Nested f-strings and arbitrary expressions
user = {"name": "Alice", "age": 30}
print(f"User: {user['name']}, Age: {user['age']}")  # Works!

# Nested f-strings
x = 10
print(f"Result: {f'{x:>10}'}")  # Works in 3.13!
```

#### PEP 698 — Override Decorator
```python
from typing import override

class Parent:
    def method(self) -> None: ...

class Child(Parent):
    @override  # mypy validates this is actually overriding
    def method(self) -> None: ...
```

### 6. Async Patterns (Python 3.13)

**TaskGroup** (cleaner than `asyncio.gather`):
```python
import asyncio

async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_user(1))
        task2 = tg.create_task(fetch_posts(1))
        # Tasks run concurrently
        # Exceptions propagate automatically

asyncio.run(main())
```

**Context Variables** (thread-safe in async):
```python
from contextvars import ContextVar

request_id = ContextVar('request_id', default=None)

async def handle_request(req_id):
    token = request_id.set(req_id)
    # All spawned tasks inherit this context var
    await process_async()
    request_id.reset(token)
```

### 7. Security Best Practices

**Secrets Module** (token generation):
```python
import secrets

api_key = secrets.token_urlsafe(32)  # Safe random tokens
nonce = secrets.token_bytes(16)       # Cryptographic nonce
```

**Secure Hashing** (use sha256, not md5):
```python
import hashlib

# ✅ SECURE
hash_obj = hashlib.sha256(b"password")

# ❌ INSECURE (removed in Python 3.13)
# hash_obj = hashlib.md5(b"password")  # ValueError!
```

**Input Validation** (Pydantic):
```python
from pydantic import BaseModel, Field, field_validator

class UserInput(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    email: str  # Auto email validation
    age: int = Field(ge=13, le=120)

    @field_validator("username")
    @classmethod
    def username_no_special_chars(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must be alphanumeric")
        return v
```

## Constitution Compliance

**My-Spec Requirements**:
- ✅ Files ≤500 SLOC (split if larger)
- ✅ Functions ≤100 lines
- ✅ Complexity ≤10 per function
- ✅ Test coverage ≥85%
- ✅ Strict typing enabled
- ✅ TAG blocks in all files

**File Size Check**:
```bash
# Count SLOC (excluding comments/blank lines)
ruff check . --select C901 --statistics
```

**Complexity Check**:
```bash
# Ruff checks complexity automatically (max=10)
ruff check . --select C90
```

## Tool Version Matrix (2025-10-26)

| Tool | Version | Purpose | Status |
|------|---------|---------|--------|
| **Python** | 3.13.1 | Runtime | ✅ Latest |
| **pytest** | 8.4.2 | Testing | ✅ Current |
| **ruff** | 0.13.1 | Lint/Format | ✅ New standard |
| **mypy** | 1.8.0 | Type checking | ✅ Current |
| **uv** | 0.9.3 | Package manager | ✅ Recommended |
| **FastAPI** | 0.115.0 | Web framework | ✅ Latest |
| **Pydantic** | 2.7.0 | Validation | ✅ Latest |

## Example Workflow

**Setup** (uv + Python 3.13):
```bash
uv venv --python 3.13               # Create venv with Python 3.13
source .venv/bin/activate
uv add pytest ruff mypy fastapi pydantic
```

**TDD Loop**:
```bash
pytest                              # RED: Watch tests fail
# [implement code]
pytest                              # GREEN: Watch tests pass
ruff check --fix .                  # REFACTOR: Fix code quality
```

**Quality Gate** (before commit):
```bash
pytest --cov=src --cov-report=term # Coverage ≥85%?
ruff check .                        # Lint pass?
mypy --strict .                     # Type check pass?
```

## Best Practices

✅ **DO**:
- Use ruff for linting + formatting (not black + pylint)
- Specify exact Python version: `requires-python = ">=3.13"`
- Use pytest for all tests
- Enable mypy strict mode
- Run quality gate before each commit
- Use uv for package management (10x faster)
- Add docstrings to public APIs
- Use f-strings (PEP 701 supports nested expressions)

❌ **DON'T**:
- Use black + pylint (deprecated, use ruff instead)
- Use md5 hashing (removed in Python 3.13)
- Mix pytest with unittest
- Ignore coverage requirements (<85% fails)
- Use old type hint syntax (use PEP 695 `class Foo[T]:`)
- Use `asyncio.gather` without error handling (use TaskGroup instead)

## Integration with My-Spec

**TAG Block Format** (Python):
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
    # Implementation...
```

**Test TAG Block**:
```python
"""
@TEST:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@CODE: src/services/auth.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: passing
"""

def test_auth_service():
    # Tests...
```

## References (Latest Documentation)

- **Python 3.13**: https://docs.python.org/3.13/ (accessed 2025-10-26)
- **pytest 8.4.2**: https://docs.pytest.org/en/stable/ (accessed 2025-10-26)
- **ruff 0.13.1**: https://docs.astral.sh/ruff/ (accessed 2025-10-26)
- **mypy 1.8.0**: https://mypy.readthedocs.io/ (accessed 2025-10-26)
- **uv 0.9.3**: https://docs.astral.sh/uv/ (accessed 2025-10-26)
- **FastAPI 0.115.0**: https://fastapi.tiangolo.com/ (accessed 2025-10-26)
- **Pydantic 2.7.0**: https://docs.pydantic.dev/ (accessed 2025-10-26)

## Changelog

- **v1.0.0** (2025-10-26): Initial Python Skill for My-Spec workflow with pytest 8.4.2, ruff 0.13.1, mypy 1.8.0, Python 3.13 features, Constitution compliance

## Works Well With

- `ms-foundation-trust` (TRUST 5 validation)
- `ms-foundation-constitution` (file size/complexity checks)
- `ms-workflow-tag-manager` (TAG block generation)
- `ms-workflow-living-docs` (API documentation sync)

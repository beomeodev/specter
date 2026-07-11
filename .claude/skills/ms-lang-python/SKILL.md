---
name: ms-lang-python
description: Python development standards for SPECTER TDD work — pytest test structure and commands, ruff lint/format configuration, mypy strict typing with Pydantic runtime validation, uv package management, asyncio TaskGroup patterns, Constitution limits (≤700 SLOC production files, ≤10 complexity, ≥85% coverage), and TAG block integration, with FastAPI and structlog reference patterns. Use when writing or reviewing Python code, writing pytest tests, implementing async patterns, building FastAPI applications, or configuring Python tooling.
---

# Language: Python (3.13+)

Standard toolchain for SPECTER Python work. These are the project defaults — deviate
only when the target repo already standardizes on something else.

| Tool | Role | Replaces |
|------|------|----------|
| pytest (+pytest-asyncio, pytest-cov) | Testing | unittest |
| ruff | Lint + format + import sort | black, pylint, isort |
| mypy (strict) + Pydantic | Static + runtime typing | — |
| uv | Package/venv management | pip, poetry |

Versions verified 2025-10; treat current stable releases as the target and re-verify
before pinning exact versions in a new project.

## Testing (pytest)

```python
# tests/test_calculator.py
import pytest
from src.calculator import add

def test_add_positive_numbers():
    """Verify addition of positive integers."""
    assert add(2, 3) == 5

@pytest.mark.asyncio
async def test_async_operation():
    result = await async_fetch_data()
    assert result is not None

@pytest.mark.parametrize("a,b,expected", [(2, 3, 5), (-2, 3, 1), (0, 0, 0)])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected
```

Rules: pytest only (never unittest, never mixed), one assertion per test, fixtures for
setup/teardown, `pytest.mark.asyncio` for async, `pytest.mark.parametrize` for
data-driven cases. Coverage ≥85% is enforced by the quality gate.

```bash
pytest                               # all tests
pytest --cov=src --cov-report=term   # coverage (≥85% required)
pytest -k "pattern"                  # matching tests
pytest --maxfail=1                   # stop at first failure
```

## Lint/format (ruff)

`pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py313"
exclude = [".venv", "build", "dist", "__pycache__"]

[tool.ruff.lint]
select = [
    "E", "F", "W",  # pycodestyle + pyflakes
    "I",            # import sorting
    "N",            # pep8-naming
    "UP",           # pyupgrade
    "B",            # bugbear
    "C4",           # comprehensions
    "C90",          # mccabe complexity
]
ignore = ["E501"]  # line length handled by formatter

[tool.ruff.lint.mccabe]
max-complexity = 10  # Constitution requirement

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["F401", "F811"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

```bash
ruff check --fix .    # lint with auto-fix
ruff format .         # format
ruff check --select C90 .  # complexity only (Constitution ≤10)
```

## Typing (mypy strict + Pydantic)

`pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
disallow_untyped_defs = true
disallow_any_generics = true
no_implicit_optional = true
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

Pydantic validates at runtime boundaries (user input, API payloads, env config):

```python
from pydantic import BaseModel, Field

class UserInput(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    email: str
    age: int = Field(ge=13, le=120)
```

```bash
mypy --strict src/
```

## Packages (uv)

```bash
uv venv --python 3.13 && source .venv/bin/activate
uv add fastapi pydantic
uv add --dev pytest pytest-asyncio pytest-cov ruff mypy
uv sync                              # install from lock file
```

`pyproject.toml` uses standard `[project]` metadata with
`requires-python = ">=3.13"`; dev tools go in `[project.optional-dependencies] dev`.

## Async

Prefer `asyncio.TaskGroup` over bare `asyncio.gather` — structured concurrency,
exceptions propagate automatically:

```python
async with asyncio.TaskGroup() as tg:
    task1 = tg.create_task(fetch_user(1))
    task2 = tg.create_task(fetch_posts(1))
```

Use `contextvars.ContextVar` for request-scoped state (request_id, user) — spawned
tasks inherit it; module-level globals do not survive concurrency.

## TDD loop and quality gate

```bash
pytest                               # RED: watch the new test fail
# [implement]
pytest                               # GREEN
ruff check --fix .                   # REFACTOR

# Quality gate (before commit):
pytest --cov=src --cov-report=term   # coverage ≥85%?
ruff check .                         # lint pass?
mypy --strict .                      # types pass?
```

## Constitution compliance

- Production files ≤700 SLOC (split if larger); test files: no limit
- Functions ≤100 lines, complexity ≤10 (`ruff check --select C90 .`)
- Coverage ≥85%, strict typing on, TAG blocks in all files

## DO / DON'T

DO: modern type syntax (PEP 695 `class Stack[T]:`, `@override`), f-strings,
`secrets` module for tokens, sha256 (never md5) for anything security-relevant,
docstrings on public APIs, quality gate before every commit.

DON'T: black+pylint (ruff replaces both), unittest, `Any` escape hatches,
`asyncio.gather` without error handling, legacy `TypeVar` boilerplate where PEP 695
syntax works, skipping coverage (<85% fails the gate).

## TAG blocks

`ms-workflow-tag-manager` is the canonical source for TAG generation. Python format:

```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/test_auth.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
"""
```

Test files use `@TEST:` as the leading tag with `@CODE:` pointing back to the source.

## Reference files (load only when needed)

- **FastAPI patterns** (dependency injection, exception handlers, middleware,
  background tasks, endpoint testing): see [references/fastapi.md](references/fastapi.md)
- **Structured logging** (structlog config, context binding, FastAPI integration):
  see [references/structlog.md](references/structlog.md)
- **Worked examples** (full TDD cycles, fixtures, async tests):
  see [examples.md](examples.md)

## Works well with

`ms-foundation-trust` (TRUST 5 validation), `ms-foundation-constitution` (size/complexity
checks), `ms-workflow-tag-manager` (TAG generation), `ms-workflow-living-docs` (doc sync).

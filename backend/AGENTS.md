# Backend Coding Assistant Rules

**Framework-Agnostic Rules** • See `../AGENTS.md` for common principles

---

## 📌 Parent Rules Compliance

**First check `../AGENTS.md` for:**

- Planning First
- Test-First Development
- Pattern Consistency
- Single Source of Truth (OSOT)
- No Magic Strings/Numbers
- Single Responsibility & Reusability
- Security by Default
- Thorough Exception Handling

---

## 🎯 Core Backend Principles

### 1. Async First (NON-NEGOTIABLE for async frameworks)

```python
# ✅ Async for I/O operations
async def get_user(user_id: int) -> Optional[User]:
    async with db_session() as db:
        return await db.get(User, user_id)

# ❌ Synchronous I/O blocks event loop
def get_user(user_id: int):
    return db.query(User).first()  # Blocking!
```

**Rules**:

- All I/O operations must be async (DB, HTTP, file system)
- Use async context managers for resource management
- Never mix sync/async without proper handling

**Applies to**: FastAPI, aiohttp, Sanic (Python), Express async (Node.js), Spring WebFlux

---

### 2. Type Annotations + Docstrings

```python
async def get_user(
    user_id: int,
    include_posts: bool = False
) -> Optional[User]:
    """
    Retrieve user by ID.

    Args:
        user_id: User identifier
        include_posts: Whether to include user posts

    Returns:
        User object or None if not found

    Raises:
        DatabaseError: On database connection failure
    """
    pass
```

**Benefits**:

- IDE autocomplete and type checking
- Self-documenting code
- Runtime validation (in some frameworks)

---

### 3. Early Return Pattern

```python
# ✅ Guard clauses eliminate nesting
async def update_user(user_id: int, data: dict) -> User:
    """Update user information"""
    if user_id <= 0:
        raise ValidationError("Invalid user ID")

    if not data:
        raise ValidationError("No update data provided")

    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")

    # Main logic (no deep nesting)
    for key, value in data.items():
        setattr(user, key, value)

    await db.commit()
    return user

# ❌ Deep nesting
async def update_user(user_id, data):
    if user_id > 0:
        if data:
            if user:
                # Too deep
```

---

### 4. Structured Error Responses

```python
# ✅ Clear status codes with messages
if not user:
    raise HTTPException(
        status_code=404,
        detail="User not found"
    )

# HTTP Status Code Guide:
# 200: Success (read, update)
# 201: Created
# 204: Deleted (no content)
# 400: Bad request (validation failed)
# 401: Unauthorized (not authenticated)
# 403: Forbidden (authenticated but no permission)
# 404: Not found
# 409: Conflict (duplicate resource)
# 500: Server error
```

**Never**: Generic errors without context or status codes

---

### 5. Input Validation

```python
# Define clear validation schemas
class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: str = Field(min_length=2, max_length=50)

@router.post("/users")
async def create_user(data: CreateUserRequest):
    # Data is already validated
    pass
```

**Framework Examples**:

- **FastAPI/Pydantic**: `BaseModel` with `Field`
- **Django REST**: `Serializer` classes
- **Express**: Joi, Zod, or class-validator
- **Spring Boot**: Bean Validation annotations

---

### 6. Observable Systems & Structured Logging

**Problem**: Logs are unstructured and hard to trace across operations

**Rule**: Structure logs for machines, not humans

```python
# ✅ Structured logging with correlation ID
import structlog
from uuid import uuid4

logger = structlog.get_logger()

@router.post("/payment")
async def process_payment(data: PaymentRequest):
    correlation_id = str(uuid4())
    logger.info(
        "payment_started",
        correlation_id=correlation_id,
        user_id=data.user_id,
        amount=data.amount
    )

    try:
        result = await payment_service(data)
        logger.info("payment_success", correlation_id=correlation_id)
        return result
    except PaymentError as e:
        logger.error(
            "payment_failed",
            correlation_id=correlation_id,
            error=str(e),
            error_code=e.code
        )
        raise
```

**Benefits**:
- Trace requests across service boundaries
- JSON format for log aggregation tools
- Correlation IDs for debugging distributed flows

**Log Levels**:

- **DEBUG**: Detailed diagnostic info
- **INFO**: General informational messages
- **WARNING**: Warning messages (recoverable)
- **ERROR**: Error messages (operation failed)
- **CRITICAL**: Critical failures (system unstable)

**Never**: Use `print()` for logging in production code

---

### 7. Database Session Management

```python
# ✅ Dependency injection (FastAPI style)
@router.post("/users")
async def create_user(
    data: CreateUserRequest,
    db: AsyncSession = Depends(get_db)
):
    user = User(**data.dict())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# ✅ Context manager (background tasks)
async def background_task():
    async with get_db() as db:
        await db.execute(query)
        await db.commit()
```

**Rules**:

- Always use connection pooling
- Close sessions properly (use context managers)
- Handle transaction rollbacks on errors

---

## 📁 Directory Structure (Standard)

```
backend/
├── src/
│   ├── models/          # Database models (ORM entities)
│   ├── routes/          # API endpoints
│   │   (or controllers/ for MVC frameworks)
│   ├── middleware/      # Auth, CORS, error handling
│   ├── schemas/         # Validation schemas
│   │   (or dto/ for Data Transfer Objects)
│   ├── services/        # Business logic (optional)
│   ├── utils/           # Reusable functions (OSOT)
│   ├── config.py        # Constants/settings (OSOT)
│   ├── database.py      # DB connection
│   └── main.py          # Application entry point
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── migrations/          # Database migrations
```

---

## 💻 Naming Conventions

```python
# Files: snake_case
user_routes.py
auth_middleware.py
payment_service.py

# Functions: snake_case + auxiliary verbs
def get_user_by_id(): pass
def is_active(): pass
def has_permission(): pass
def should_retry(): pass
async def fetch_user_data(): pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_PAGE_SIZE = 20
API_TIMEOUT_SECONDS = 30

# Classes: PascalCase
class UserService:
    pass

class CreateUserRequest(BaseModel):
    pass
```

---

## 🚀 Performance Patterns

### 1. Parallel Async Operations

```python
# Execute multiple async operations concurrently
import asyncio

async def get_user_with_posts(user_id: int):
    """Fetch user and posts in parallel"""
    user_task = db.get(User, user_id)
    posts_task = db.query(Post).filter_by(user_id=user_id).all()

    user, posts = await asyncio.gather(user_task, posts_task)
    return {"user": user, "posts": posts}
```

**Use when**: Multiple independent async operations can run concurrently

---

### 2. Caching

```python
# Cache expensive or frequent queries
@cache(expire=300)  # 5 minutes
async def get_popular_posts():
    """Fetch popular posts (cached)"""
    return await db.query(Post).order_by(Post.views.desc()).limit(10).all()
```

**Cache when**:

- Data changes infrequently
- Query is expensive
- High read frequency

---

### 3. Pagination

```python
@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List users with pagination"""
    # Enforce maximum limit
    limit = min(limit, 100)

    users = await db.query(User).offset(skip).limit(limit).all()
    total = await db.query(User).count()

    return {
        "items": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

**Always**: Limit maximum page size to prevent resource exhaustion

---

## 🛡️ RESTful API Standards

```python
# ✅ Correct patterns
GET    /users           # List all users
GET    /users/{id}      # Get single user
POST   /users           # Create user
PUT    /users/{id}      # Full update (replace)
PATCH  /users/{id}      # Partial update (modify)
DELETE /users/{id}      # Delete user

# Nested resources
GET    /users/{id}/posts           # User's posts
POST   /users/{id}/posts           # Create post for user

# ❌ Wrong patterns
GET    /get-user                   # No verbs in URLs
POST   /users/delete               # Use DELETE method
GET    /users/list                 # Redundant
```

**URL Guidelines**:

- Use nouns, not verbs
- Use plural for collections (`/users`, not `/user`)
- Use hyphens for multi-word (`/user-profiles`)
- Keep URLs short and meaningful

---

## 🔧 Development Commands

**Single file** (preferred):

```bash
# Format and check single file
black src/routes/user_routes.py && \
pylint src/routes/user_routes.py && \
mypy src/routes/user_routes.py && \
pytest tests/test_user_routes.py
```

**Full project** (only when requested):

```bash
black src/ && pylint src/ && mypy src/ && pytest
```

**Development server**:

```bash
# FastAPI
uvicorn src.main:app --reload

# Django
python manage.py runserver

# Express
npm run dev
```

---

## ✅ Pre-Work Checklist

**Before creating/modifying endpoints**:

- [ ] Checked similar existing endpoints for patterns?
- [ ] Using async for I/O operations?
- [ ] Type annotations added to all parameters?
- [ ] Input validation schema defined?
- [ ] Error handling with proper status codes?
- [ ] Logging added for critical operations?
- [ ] Following RESTful URL conventions?
- [ ] Tests written before implementation?

**Before commit**:

- [ ] Code formatter passed (black/prettier)?
- [ ] Linter passed (0 warnings)?
- [ ] Type checker passed?
- [ ] All tests pass?
- [ ] No `print()` statements (use logger)?
- [ ] No commented-out code?
- [ ] Environment variables for secrets?

---

## 📊 Code Quality Standards

**Required**:

- ✅ Async for all I/O operations (async frameworks)
- ✅ Type annotations on all functions
- ✅ Input validation schemas
- ✅ Structured error responses with status codes
- ✅ Logging for critical operations
- ✅ Early return pattern (no deep nesting)
- ✅ RESTful URL conventions
- ✅ Connection pooling for databases

**Forbidden**:

- ❌ Blocking I/O in async context
- ❌ Missing type hints
- ❌ Generic error messages without context
- ❌ `print()` for logging
- ❌ Verbs in REST URLs
- ❌ Hardcoded secrets (use environment variables)
- ❌ SQL injection vulnerabilities (use parameterized queries)

---

## 🔐 Security Checklist

- [ ] Input validation on all endpoints
- [ ] SQL parameterized queries (no string interpolation)
- [ ] Authentication required (except public endpoints)
- [ ] Authorization checks before data access
- [ ] Rate limiting on public endpoints
- [ ] CORS properly configured (not wildcard)
- [ ] Secrets in environment variables
- [ ] Password hashing (bcrypt/argon2)
- [ ] HTTPS in production
- [ ] Structured JSON logs with correlation IDs
- [ ] SECURITY DEFINER functions have internal authorization checks

### SECURITY DEFINER Pattern

**When needed**: RLS blocks legitimate cross-user data access (e.g., admin queries, messaging systems)

**Solution**: Use `SECURITY DEFINER` functions that bypass RLS with database owner permissions:

```sql
CREATE FUNCTION get_cross_user_data(
    requesting_user_id UUID,
    target_user_id UUID
)
RETURNS TABLE(...)
SECURITY DEFINER  -- Bypasses RLS with DB owner permissions
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
    -- MUST validate authorization internally
    IF NOT is_admin(requesting_user_id) THEN
        RAISE EXCEPTION 'Unauthorized access';
    END IF;

    -- Can now read other users' data despite RLS blocking
    RETURN QUERY
    SELECT * FROM users WHERE id = target_user_id;
END;
$$;
```

**When to use SECURITY DEFINER**:
- Admin dashboard reading aggregate metrics across users
- Messaging systems where users need to read each other's data
- Any legitimate cross-user data access blocked by RLS

**Security rule**: SECURITY DEFINER functions MUST validate authorization internally since they bypass RLS

---

## 🎯 Framework-Specific Notes

**This document is framework-agnostic.** Apply these principles to:

- **FastAPI** (Python): async/await, Depends, Pydantic
- **Django** (Python): Django REST Framework, Serializers, ORM
- **Express** (Node.js): async/await, middleware, Joi/Zod
- **Spring Boot** (Java): @RestController, Bean Validation, JPA
- **ASP.NET Core** (C#): async/await, Controllers, Data Annotations

For framework-specific patterns, create `PATTERNS-{framework}.md` separately.

---

**Created**: 2025-10-10
**Version**: 2.0.0

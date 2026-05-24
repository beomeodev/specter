# Constitution Compliance Examples

## Example 1: File Size Validation (PASS)

**File**: `src/auth/utils.py` (245 SLOC)

```python
"""
@CODE:AUTH-002
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/auth/test_utils.py
"""

def validate_password(password: str) -> bool:
    """Validate password complexity."""
    if len(password) < 12:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    import bcrypt
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

# ... 235 more lines of utility functions
```

**Result**: ✅ PASS (245 SLOC ≤ 700)

---

## Example 2: File Size Validation (FAIL)

**File**: `src/auth/service.py` (587 SLOC)

```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/auth/test_service.py
"""

class AuthService:
    """Authentication service with all features in one file."""

    def __init__(self, db, cache, logger):
        self.db = db
        self.cache = cache
        self.logger = logger

    def authenticate_user(self, email, password):
        # 100 lines of authentication logic
        ...

    def refresh_token(self, refresh_token):
        # 120 lines of token refresh logic
        ...

    def validate_session(self, session_id):
        # 80 lines of session validation
        ...

    # ... 10 more methods, 287 more lines
```

**Result**: ❌ FAIL (587 SLOC > 500)

**Refactoring Strategy**:
```
Split into focused modules:
- src/auth/service.py (150 SLOC) - Core AuthService
- src/auth/token_manager.py (180 SLOC) - Token operations
- src/auth/session_manager.py (120 SLOC) - Session handling
- src/auth/validators.py (137 SLOC) - Input validation
```

---

## Example 3: Complexity Validation (PASS)

**Function**: `authenticate_user` (complexity: 8)

```python
def authenticate_user(email: str, password: str) -> dict:
    """Authenticate user with email and password."""
    # Guard clauses (early returns)
    if not email or not password:
        raise ValueError("Email and password required")

    user = db.get_user_by_email(email)
    if not user:
        raise AuthenticationError("Invalid credentials")

    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        raise AuthenticationError("Invalid credentials")

    if user.is_locked:
        raise AuthenticationError("Account locked")

    # Generate JWT token
    token = generate_jwt_token(user.id)
    return {"token": token, "user_id": user.id}
```

**Complexity Analysis**:
- 4 if statements = 4 decision points
- 4 early returns = no nested complexity
- Total complexity = 8 ✅ (≤10)

---

## Example 4: Complexity Validation (FAIL)

**Function**: `refresh_token` (complexity: 15)

```python
def refresh_token(refresh_token: str) -> dict:
    """Refresh access token using refresh token."""
    if not refresh_token:
        raise ValueError("Refresh token required")

    try:
        payload = decode_jwt(refresh_token)
        if payload.get("type") != "refresh":
            raise InvalidTokenError("Not a refresh token")

        user_id = payload.get("user_id")
        if not user_id:
            raise InvalidTokenError("Missing user_id")

        user = db.get_user(user_id)
        if not user:
            raise InvalidTokenError("User not found")

        if user.is_locked:
            raise AuthenticationError("Account locked")

        stored_token = cache.get(f"refresh_token:{user_id}")
        if stored_token != refresh_token:
            if stored_token:
                # Token rotation detected
                cache.delete(f"refresh_token:{user_id}")
                raise SecurityError("Token rotation detected")
            else:
                # First refresh, store token
                cache.set(f"refresh_token:{user_id}", refresh_token)

        # Generate new access token
        new_token = generate_jwt_token(user_id)
        return {"token": new_token, "user_id": user_id}

    except JWTDecodeError as e:
        raise InvalidTokenError(f"Invalid token: {e}")
```

**Complexity Analysis**:
- 8 if statements (including nested)
- 2 nested if-else blocks
- Exception handling adds complexity
- Total complexity = 15 ❌ (>10)

**Refactoring Strategy**:
```python
def refresh_token(refresh_token: str) -> dict:
    """Refresh access token (refactored)."""
    validate_refresh_token_format(refresh_token)
    payload = decode_and_verify_refresh_token(refresh_token)
    user = get_and_validate_user(payload["user_id"])
    verify_token_rotation(user.id, refresh_token)

    new_token = generate_jwt_token(user.id)
    return {"token": new_token, "user_id": user.id}

# Helper functions (each with complexity ≤5)
def validate_refresh_token_format(token: str):
    """Validate token format."""
    if not token:
        raise ValueError("Refresh token required")

def decode_and_verify_refresh_token(token: str) -> dict:
    """Decode and verify token type."""
    try:
        payload = decode_jwt(token)
        if payload.get("type") != "refresh":
            raise InvalidTokenError("Not a refresh token")
        if not payload.get("user_id"):
            raise InvalidTokenError("Missing user_id")
        return payload
    except JWTDecodeError as e:
        raise InvalidTokenError(f"Invalid token: {e}")

def get_and_validate_user(user_id: int) -> User:
    """Get user and validate status."""
    user = db.get_user(user_id)
    if not user:
        raise InvalidTokenError("User not found")
    if user.is_locked:
        raise AuthenticationError("Account locked")
    return user

def verify_token_rotation(user_id: int, token: str):
    """Verify token rotation."""
    stored_token = cache.get(f"refresh_token:{user_id}")
    if stored_token and stored_token != token:
        cache.delete(f"refresh_token:{user_id}")
        raise SecurityError("Token rotation detected")
    if not stored_token:
        cache.set(f"refresh_token:{user_id}", token)
```

**Result after refactoring**:
- `refresh_token`: complexity 5 ✅
- `validate_refresh_token_format`: complexity 2 ✅
- `decode_and_verify_refresh_token`: complexity 4 ✅
- `get_and_validate_user`: complexity 4 ✅
- `verify_token_rotation`: complexity 4 ✅

---

## Example 5: Function Size Validation

**PASS** (87 LOC):
```python
def process_user_registration(data: dict) -> User:
    """Process user registration with validation."""
    # 20 lines: Input validation
    validate_email(data["email"])
    validate_password(data["password"])
    validate_username(data["username"])

    # 15 lines: Duplicate check
    if db.user_exists(data["email"]):
        raise DuplicateEmailError()

    # 20 lines: Create user
    user = User(
        email=data["email"],
        username=data["username"],
        password_hash=hash_password(data["password"]),
        created_at=datetime.utcnow()
    )
    db.save(user)

    # 15 lines: Send welcome email
    send_welcome_email(user.email, user.username)

    # 10 lines: Audit log
    logger.info(f"New user registered: {user.id}")

    return user  # Total: 87 LOC ✅
```

**FAIL** (142 LOC):
```python
def process_user_registration_with_everything(data: dict) -> User:
    """Process user registration (does too much)."""
    # 30 lines: Input validation (inline, not extracted)
    # 20 lines: Duplicate check (with complex queries)
    # 25 lines: Password hashing (reimplemented bcrypt)
    # 20 lines: User creation
    # 25 lines: Email sending (inline SMTP code)
    # 12 lines: Audit logging
    # 10 lines: Analytics tracking
    return user  # Total: 142 LOC ❌
```

**Refactoring**: Extract helpers as shown in PASS example.

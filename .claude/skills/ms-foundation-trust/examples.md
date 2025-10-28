# TRUST 5 Validation Examples

## Example 1: Complete TRUST Compliance (PASS)

**File**: `src/auth/service.py`

```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/auth/test_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
"""

import bcrypt
from typing import Optional
from datetime import datetime, timedelta
import jwt
from .validators import validate_email, validate_password

class AuthService:
    """Authentication service with JWT tokens."""

    def __init__(self, secret_key: str, token_expiry: int = 900):
        """
        Initialize auth service.

        Args:
            secret_key: JWT signing secret (from environment)
            token_expiry: Token expiration in seconds (default: 15 minutes)
        """
        self.secret_key = secret_key
        self.token_expiry = token_expiry

    def authenticate(self, email: str, password: str) -> dict:
        """
        Authenticate user with email and password.

        WHEN user submits valid credentials, system SHALL issue JWT token.

        Args:
            email: User email (validated)
            password: User password (plaintext)

        Returns:
            dict: {"token": str, "expires_at": datetime}

        Raises:
            ValueError: Invalid email/password format
            AuthenticationError: Invalid credentials or locked account
        """
        # Input validation (Secured)
        if not email or not password:
            raise ValueError("Email and password required")

        validate_email(email)  # Unified: Use shared validator
        validate_password(password)

        # Early return pattern (Readable)
        user = self._get_user_by_email(email)
        if not user:
            raise AuthenticationError("Invalid credentials")

        if not self._verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")

        if user.is_locked:
            raise AuthenticationError("Account locked")

        # Generate token
        token = self._generate_token(user.id)
        expires_at = datetime.utcnow() + timedelta(seconds=self.token_expiry)

        return {
            "token": token,
            "expires_at": expires_at.isoformat()
        }

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against bcrypt hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )

    def _generate_token(self, user_id: int) -> str:
        """Generate JWT token."""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=self.token_expiry),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def _get_user_by_email(self, email: str) -> Optional['User']:
        """Get user by email (stub for example)."""
        # Real implementation would query database
        pass
```

**TRUST Analysis**:

**T - Test First**: ✅
```python
# tests/auth/test_service.py (pytest coverage: 95%)

def test_authenticate_with_valid_credentials():
    """
    WHEN user submits valid credentials, system SHALL issue JWT token.
    @TEST:AUTH-001
    """
    service = AuthService(secret_key="test-secret")
    result = service.authenticate("user@example.com", "ValidPass123!")

    assert "token" in result
    assert "expires_at" in result
    assert jwt.decode(result["token"], "test-secret", algorithms=["HS256"])

def test_authenticate_with_invalid_credentials():
    """
    IF invalid credentials provided, system SHALL return AuthenticationError.
    @TEST:AUTH-001
    """
    service = AuthService(secret_key="test-secret")

    with pytest.raises(AuthenticationError):
        service.authenticate("user@example.com", "WrongPassword")

def test_authenticate_with_locked_account():
    """
    IF account is locked, system SHALL deny access.
    @TEST:AUTH-001
    """
    # ... test implementation
```

**R - Readable**: ✅
- File: 120 SLOC (≤500) ✅
- Functions: ≤50 LOC ✅
- Complexity: ≤10 ✅
- Clear variable names ✅
- Early returns for guard clauses ✅

**U - Unified**: ✅
- Type hints on all functions ✅
- Shared validators (`validate_email`, `validate_password`) ✅
- Consistent error handling ✅
- mypy --strict passes ✅

**S - Secured**: ✅
- Input validation (email, password format) ✅
- bcrypt password hashing ✅
- Secret key from environment (not hardcoded) ✅
- Token expiry enforced ✅
- No sensitive data in error messages ✅

**T - Trackable**: ✅
- TAG block present (`@CODE:AUTH-001`) ✅
- SPEC/TEST references in docstring ✅
- Clear traceability chain ✅

---

## Example 2: TRUST Violations (FAIL)

**File**: `src/auth/bad_service.py`

```python
# ❌ No TAG block (Trackable violation)

class BadAuthService:
    # ❌ No type hints (Unified violation)
    def __init__(self, secret):
        self.secret = "hardcoded-secret-key"  # ❌ Security violation

    # ❌ No tests exist (Test First violation)
    def login(self, email, password):  # ❌ No validation (Secured violation)
        # ❌ Complexity: 15 (Readable violation - nested if/else)
        if email:
            if password:
                user = self.get_user(email)
                if user:
                    if user.password == password:  # ❌ Plaintext password
                        if user.status == "active":
                            if user.verified:
                                token = self.make_token(user.id)
                                if token:
                                    return token
                                else:
                                    return None
                            else:
                                return None
                        else:
                            return None
                    else:
                        return None
                else:
                    return None
            else:
                return None
        else:
            return None

    def make_token(self, uid):  # ❌ Abbreviations (Readable violation)
        # ❌ No expiry (Security violation)
        return jwt.encode({"u": uid}, self.secret)  # ❌ Short keys
```

**TRUST Analysis**:

**T - Test First**: ❌ FAIL
- No test file exists
- Coverage: 0%

**R - Readable**: ❌ FAIL
- Complexity: 15 (>10)
- Nested if-else (8 levels deep)
- Abbreviations (`uid` instead of `user_id`)
- No docstrings

**U - Unified**: ❌ FAIL
- No type hints
- Inconsistent naming (`login` vs `authenticate`)
- mypy fails

**S - Secured**: ❌ FAIL
- Hardcoded secret key
- No input validation
- Plaintext password comparison
- No token expiry
- Verbose error messages (information disclosure)

**T - Trackable**: ❌ FAIL
- No TAG block
- No SPEC reference
- No traceability

**Remediation**: Rewrite following Example 1.

---

## Example 3: Coverage Report (Test First)

**pytest coverage output**:
```
---------- coverage: platform linux, python 3.13.2-final-0 ----------
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
src/auth/__init__.py           2      0   100%
src/auth/service.py           45      3    93%   78-80
src/auth/validators.py        12      0   100%
src/auth/models.py            18      1    94%   42
--------------------------------------------------------
TOTAL                         77      4    95%

Required coverage: 85%
✅ PASS
```

**Coverage delta** (since last commit):
```
+2.5% overall coverage
+15 new lines covered
-0 lines uncovered
✅ Coverage increased
```

---

## Example 4: TAG Chain Validation (Trackable)

**Complete chain** ✅:
```bash
$ rg '@(SPEC|TEST|CODE):AUTH-001' -n

specs/001-auth-spec/spec.md:
1:# @SPEC:AUTH-001: Authentication Feature

tests/auth/test_service.py:
5:@TEST:AUTH-001

src/auth/service.py:
3:@CODE:AUTH-001
```

**Orphaned TAG** ❌:
```bash
$ rg '@CODE:USER-042' -n
src/user/profile.py:3:@CODE:USER-042

$ rg '@SPEC:USER-042' -n
# No results → Orphaned CODE tag (SPEC missing)

$ rg '@TEST:USER-042' -n
# No results → Orphaned CODE tag (TEST missing)
```

**Duplicate TAG** ❌:
```bash
$ rg '@SPEC:AUTH-001' -c specs/

specs/001-auth-spec/spec.md:1
specs/002-auth-v2-spec/spec.md:1  ← Duplicate!
```

---

## Example 5: Security Scan (Secured)

**trivy scan results**:
```bash
$ trivy fs --severity HIGH,CRITICAL .

Total: 2 vulnerabilities (1 HIGH, 1 CRITICAL)

HIGH: CVE-2024-12345
Package: requests
Version: 2.25.0
Fixed in: 2.31.0

CRITICAL: CVE-2024-67890
Package: cryptography
Version: 38.0.0
Fixed in: 41.0.7

❌ FAIL: HIGH/CRITICAL vulnerabilities detected
```

**After remediation**:
```bash
$ pip install --upgrade requests cryptography
$ trivy fs --severity HIGH,CRITICAL .

Total: 0 vulnerabilities
✅ PASS
```

---

## Example 6: Type Safety (Unified)

**mypy --strict output**:
```bash
$ mypy src/ --strict

src/auth/service.py:25: error: Function is missing a return type annotation
src/auth/service.py:32: error: Argument 1 has incompatible type "Optional[str]"; expected "str"

Found 2 errors in 1 file (checked 15 source files)
❌ FAIL
```

**After fixes**:
```bash
$ mypy src/ --strict

Success: no issues found in 15 source files
✅ PASS
```

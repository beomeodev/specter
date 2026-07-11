# TAG Manager Skill - Examples

## Contents

- Example 1: Python TAG Block Generation
- Example 2: TypeScript TAG Block Generation
- Example 3: TAG Chain Validation
- Example 4: Multi-language TAG Template
- Example 5: TAG Status Lifecycle
- Example 6: Duplicate TAG Detection
- Example 7: TAG Auto-Insertion via /ms.implement
- Example 8: TAG with Documentation Reference
- Example 9: TAG Update After Refactoring
- Example 10: TAG Chain Report

## Example 1: Python TAG Block Generation

**Scenario**: Create TAG block for authentication service

```python
# Input parameters
tag_id = "AUTH-001"
lang = "python"
spec_path = "specs/001-auth-spec/spec.md"
test_path = "tests/unit/test_auth_service.py"
status = "implemented"

# Generated TAG block
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26
"""

# Full implementation
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
    Authenticates user with email and password.

    Args:
        email: User email address
        password: User password

    Returns:
        AuthResult with success status and optional token

    Raises:
        ValueError: If email or password is empty
    """
    if not email or not password:
        return AuthResult(success=False, token=None, error="Invalid credentials")

    # Authentication logic here
    return AuthResult(success=True, token="jwt_token_here", error=None)
```

---

## Example 2: TypeScript TAG Block Generation

**Scenario**: Create TAG block for React authentication hook

```typescript
// Input parameters
const tagId = "AUTH-002";
const lang = "typescript";
const specPath = "specs/001-auth-spec/spec.md";
const testPath = "tests/unit/useAuth.test.ts";

// Generated TAG block
/**
 * @CODE:AUTH-002
 * @SPEC: specs/001-auth-spec/spec.md
 * @TEST: tests/unit/useAuth.test.ts
 * @CHAIN: @SPEC:AUTH-002 → @TEST:AUTH-002 → @CODE:AUTH-002
 * @STATUS: implemented
 * @CREATED: 2025-10-26
 * @UPDATED: 2025-10-26
 */

// Full implementation
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
        throw new Error('Authentication failed');
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
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }, []);

  return { ...authState, login };
}
```

---

## Example 3: TAG Chain Validation

**Scenario**: Verify complete TAG chain for AUTH-001

```bash
# Search for all TAG references
rg "@(SPEC|TEST|CODE):AUTH-001" -n specs/ tests/ src/

# Expected output (complete chain):
specs/001-auth-spec/spec.md:42:## @SPEC:AUTH-001 - User Authentication
tests/unit/test_auth_service.py:2:@TEST:AUTH-001
src/auth/service.py:2:@CODE:AUTH-001

# Verify uniqueness
rg "@CODE:AUTH-001" -c src/
# Output: 1 (should only appear once in code)

# Find orphaned TAGs (CODE without SPEC)
rg "@CODE:AUTH-003" -l src/          # CODE exists
rg "@SPEC:AUTH-003" -l specs/        # SPEC missing → orphan!
```

---

## Example 4: Multi-language TAG Template

**Scenario**: Generate TAG blocks for polyglot project (Python + TypeScript)

### Python Service

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
    """Creates a new user account."""
    # Implementation
    pass
```

### TypeScript Frontend

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
      throw new Error(`API error: ${response.statusText}`);
    }
  }
}
```

---

## Example 5: TAG Status Lifecycle

**Scenario**: Track TAG status from planning to deployment

### Step 1: Planning (tasks.md)

```markdown
## Phase 1: Authentication

**TAG**: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001

### Implementation

-   [ ] T001 Create auth service
    - Status: planned
```

### Step 2: TDD RED Phase (test file)

```python
"""
@TEST:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@CODE: src/auth/service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: in_progress  ← TDD RED phase
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
    assert result.error == "Invalid credentials"
```

### Step 3: TDD GREEN Phase (implementation)

```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented  ← Tests passing
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
    # Minimal implementation to pass tests
    if email == "test@example.com" and password == "password123":
        return AuthResult(success=True, token="jwt_token", error=None)
    return AuthResult(success=False, token=None, error="Invalid credentials")
```

### Step 4: After Code Review

```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: reviewed  ← Code review approved
@CREATED: 2025-10-26
@UPDATED: 2025-10-27
"""
# ... (implementation unchanged)
```

---

## Example 6: Duplicate TAG Detection

**Scenario**: Prevent duplicate TAG IDs

```bash
# Before creating new TAG, check for duplicates
TAG_ID="AUTH-001"

# Search existing TAGs
rg "@(SPEC|TEST|CODE):${TAG_ID}" -n specs/ tests/ src/ docs/

# Count occurrences per type
echo "SPEC count:"
rg "@SPEC:${TAG_ID}" -c specs/

echo "TEST count:"
rg "@TEST:${TAG_ID}" -c tests/

echo "CODE count:"
rg "@CODE:${TAG_ID}" -c src/

# Expected: 1 occurrence per type (SPEC, TEST, CODE)
# If >1, duplicate detected!
```

**Handling duplicates**:
```bash
# Find all files with duplicate TAG
rg "@CODE:AUTH-001" -l src/

# Output (problem):
# src/auth/service.py
# src/auth/utils.py  ← Duplicate! Should use AUTH-002

# Fix: Reassign TAG ID
# src/auth/utils.py: Change AUTH-001 → AUTH-005
```

---

## Example 7: TAG Auto-Insertion via /ms.implement

**Scenario**: `/ms.implement` automatically generates TAG blocks

```bash
# User runs
/ms.implement

# System execution:
# 1. Read tasks.md → find first uncompleted task
# 2. Extract TAG ID: AUTH-001
# 3. Read specs/001-auth-spec/spec.md
# 4. Generate test file: tests/unit/test_auth_service.py
#    with @TEST:AUTH-001 block (auto-inserted)
# 5. Generate code file: src/auth/service.py
#    with @CODE:AUTH-001 block (auto-inserted)
# 6. Verify chain: rg '@(SPEC|TEST|CODE):AUTH-001' -n
```

**Result** (auto-generated files):

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
    # Test implementation
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
    # Implementation
    pass
```

---

## Example 8: TAG with Documentation Reference

**Scenario**: Include optional @DOC reference for API documentation

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
    Retrieves user by ID.

    See @DOC:API-001 for detailed API documentation.
    """
    # Implementation
    pass
```

**Corresponding docs/api/API-001.md**:
```markdown
# @DOC:API-001 - Get User Endpoint

@SPEC: specs/002-api-spec/spec.md
@TEST: tests/unit/test_api_endpoints.py
@CODE: src/api/routes/users.py

## Endpoint

`GET /api/v1/users/{user_id}`

## Request

- Path parameter: `user_id` (integer, required)

## Response

200 OK:
```json
{
  "id": 123,
  "email": "user@example.com"
}
```

404 Not Found:
```json
{
  "detail": "User not found"
}
```
```

---

## Example 9: TAG Update After Refactoring

**Scenario**: Update TAG timestamp after code refactoring

**Before refactoring**:
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
    # Old implementation (no type hints)
    pass
```

**After refactoring** (improved with type hints, kept TAG ID):
```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-27  ← Updated timestamp
"""

from typing import Optional
from dataclasses import dataclass

@dataclass
class AuthResult:
    success: bool
    token: Optional[str]
    error: Optional[str]

def authenticate_user(email: str, password: str) -> AuthResult:
    """Improved implementation with type hints."""
    # Refactored implementation
    pass
```

**Note**: TAG ID stays the same (AUTH-001) because functionality didn't change, only code quality improved.

---

## Example 10: TAG Chain Report

**Scenario**: Generate TAG chain integrity report

```bash
#!/bin/bash
# Generate TAG chain report

echo "=== TAG Chain Integrity Report ==="
echo ""

# Find all SPEC TAGs
SPEC_TAGS=$(rg '@SPEC:([A-Z]+-[0-9]+)' -or '$1' specs/ | sort -u)

for TAG in $SPEC_TAGS; do
    echo "Checking chain for $TAG..."

    SPEC_COUNT=$(rg "@SPEC:$TAG" -c specs/ 2>/dev/null || echo 0)
    TEST_COUNT=$(rg "@TEST:$TAG" -c tests/ 2>/dev/null || echo 0)
    CODE_COUNT=$(rg "@CODE:$TAG" -c src/ 2>/dev/null || echo 0)

    if [ "$SPEC_COUNT" -gt 0 ] && [ "$TEST_COUNT" -gt 0 ] && [ "$CODE_COUNT" -gt 0 ]; then
        echo "  ✅ Complete chain: @SPEC → @TEST → @CODE"
    else
        echo "  ❌ Broken chain:"
        echo "     @SPEC: $SPEC_COUNT"
        echo "     @TEST: $TEST_COUNT"
        echo "     @CODE: $CODE_COUNT"
    fi
    echo ""
done
```

**Example output**:
```
=== TAG Chain Integrity Report ===

Checking chain for AUTH-001...
  ✅ Complete chain: @SPEC → @TEST → @CODE

Checking chain for AUTH-002...
  ❌ Broken chain:
     @SPEC: 1
     @TEST: 1
     @CODE: 0  ← Missing implementation

Checking chain for HOOKS-001...
  ✅ Complete chain: @SPEC → @TEST → @CODE
```

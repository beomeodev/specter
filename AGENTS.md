# AI Coding Assistant Rules (AGENTS.md)

---

## 1. Core Principles

### ✅ Required

- **Code comments and documentation**
- **Small units** (1-2 files only)
- **Follow existing patterns**
- **Explicit typing required**
- **Tests before implementation**
- **Update AGENTS.md when needed during project**

### ❌ Prohibited

- Modifying multiple files simultaneously
- Ignoring existing patterns
- Code duplication
- Type omission (any abuse)
- Implementation without tests

---

## 2. Operational Guardrails

### Context Management (CRITICAL)

**Rule**: Always read relevant files BEFORE planning changes

- Search for similar existing features first
- Check current implementation patterns
- Verify types/constants already defined
- Never guess - always verify by reading files

**Anti-pattern**: Planning changes without understanding current codebase state

### Documentation Updates

- Keep updates concise and on point to prevent bloat
- Document "why" not "what"

### Development Restrictions

- Do not commit to git without user approval
- Do not run local servers - tell user to run them
- Never use placeholders - implement complete solutions

---

## 3. Requirements Clarification (EARS Pattern)

**Problem**: Ambiguous requirements lead to wrong implementations

**Rule**: Clarify requirements in one of 5 formats before implementation

| Pattern | Keyword | Format | Example |
|---------|---------|--------|---------|
| **Unconditional** | `System SHALL` | System SHALL [capability] | System SHALL use HTTPS for all API calls |
| **Event-driven** | `WHEN` | WHEN [event], system SHALL [action] | WHEN login button clicked, SHALL validate credentials |
| **State-driven** | `WHILE` | WHILE [state], system SHALL [action] | WHILE file uploading, SHALL display progress bar |
| **Optional** | `WHERE` | WHERE [condition], system MAY [action] | WHERE user is admin, MAY display admin panel |
| **Constraint** | `IF` | IF [condition], system SHALL [constraint] | IF password fails 3 times, SHALL lock account |

**Application Example**:

```
❌ "Build login feature"

✅ Clear requirements:
- System SHALL provide login endpoint at /api/auth/login
- WHEN user submits credentials, system SHALL validate against database
- IF credentials invalid, system SHALL return 401 with error message
- WHILE session is active, system SHALL allow access to protected routes
- WHERE refresh token is provided, system MAY extend session
```

**Forbidden phrases**: "quickly", "securely", "well", "appropriately" → Replace with specific criteria

---

## 4. Clean Code Core Principles

### 0. ⚠️ Zero Tolerance (Absolute Prohibition)

**Never** use workarounds that avoid root causes:

- `setTimeout` for state synchronization (timing hack)
- `window.location.reload()` to fix issues
- Fallback patterns masking real problems
- Catching errors without handling them
- `any` type to bypass type checking

**Rule**: Always find and fix the root cause

---

### 1. Planning First

**Problem**: AI implements features without considering structure

**Rule**: Present plan before modifying 3+ files

- List of files to modify
- Changes for each file
- Expected risks
- **Proceed after approval**

---

### 2. Test-First Development

**Problem**: AI forgets tests or writes them superficially

**Rule**: All features follow: Write test → Implement → Refactor

```python
# 1. Write failing test first
def test_user_login():
    response = client.post("/login", json={"email": "test@test.com"})
    assert response.status_code == 200

# 2. Implement minimum code to pass
@app.post("/login")
def login(data: LoginData):
    # Implementation...
    return {"token": "..."}

# 3. Refactor
```

**Apply**: Always think "how to test this" before implementing

---

### 3. Simplicity First

**Problem**: AI uses unnecessarily complex patterns

**Rule**: Use complex patterns only when necessity is proven

```
Decision sequence:
1. Solvable with simple function? → Use function
2. Exists in library? → Use library
3. Standard pattern sufficient? → Use standard
4. Really need custom? → Document why, then implement
```

**Avoid unnecessary complexity**:

- Microservices (when monolith suffices)
- GraphQL (when REST suffices)
- Custom frameworks
- Over-abstraction

**File Size Constraints** (from Constitution):

- Files ≤500 SLOC (code only, excluding comments)
- Functions ≤100 LOC
- Complexity ≤10 per function
- **Split files when limits exceeded**

---

### 4. Pattern Consistency

**Problem**: AI ignores existing project patterns and uses its own style

**Rule**: Always check existing patterns before writing code

- Folder structure (where to create files)
- Naming conventions (snake_case, camelCase, etc.)
- Import order
- Error handling approach
- CRUD patterns

**Verify**: Find similar features and compare patterns

---

### 5. Single Source of Truth (OSOT)

**Problem**: AI redefines same information everywhere

**Rule**: Define important information once, import elsewhere

```python
# ❌ Bad: Duplicated definitions
# user.py
MAX_LENGTH = 50

# post.py
MAX_LENGTH = 50  # Duplicate!

# ✅ Good: Define once
# config.py
MAX_LENGTH = 50

# Reuse elsewhere
from config import MAX_LENGTH
```

**Applies to**: Constants, type definitions, utility functions, validation logic

---

### 6. No Magic Strings/Numbers

**Problem**: AI hardcodes status values ("cancelled", "completed") and magic numbers

**Rule**: Extract status values and important numbers as constants

```python
# ❌ Hardcoded
if status == "completed":  # Typo risk

# ✅ Constant extraction
# config.py
STATUS_COMPLETED = "completed"

# Usage
if status == STATUS_COMPLETED:
```

**Config file locations**:

- **Simple projects**: `docs/src/config.{py,ts}`
- **Backend**: `backend/src/config.py`
- **Frontend**: `frontend/src/config.ts`

**Note**: TAG utilities and CI scripts scan all of: `docs/src/`, `backend/src/`, `frontend/src/`, `tests/`, `backend/tests/`, `frontend/tests/`

---

### 7. Explicit Over Implicit

**Problem**: AI creates implicit behavior, side effects, and "magic"

**Rule**: All behavior must be explicit

```python
# ❌ Implicit side effects
def process_user(user):
    user.processed = True  # Mutates parameter
    global_state.last = user  # Global state change
    return user

# ✅ Explicit
def process_user(user: User, state: State) -> ProcessedUser:
    return ProcessedUser(
        ...user,
        processed=True,
        processed_at=now()
    )
```

**Forbidden patterns**:

- Global variables for state
- Direct parameter mutation
- Hidden dependencies
- Magic numbers/strings

---

### 8. Single Responsibility & Reusability

**Problem**: AI puts everything in one file and duplicates same logic everywhere

**Rule**: One function/component = one responsibility + extract reusable logic

**File Size Guidelines**:

- Target: Under 300-350 lines per file
- **Maximum: 500 SLOC (hard limit from Constitution)**
- One file = one clear responsibility
- Prefer composition over inheritance (use inheritance only for true 'is-a' relationships)

**When file exceeds limits, extract**:

- Utilities → `utils/` or `lib/`
- Constants → `config.ts` or `constants.ts`
- Types → `types/` or `models/`
- Reusable logic → `composables/` or `hooks/`

```python
# ❌ Multiple responsibilities + duplication
def process_user(data):
    validate(data)
    transform(data)
    save(data)
    send_email(data)

def process_order(data):
    validate(data)  # Duplicate!
    transform(data)  # Duplicate!
    save(data)
    send_notification(data)

# ✅ Separation + reusability
# utils/validation.py
def validate_data(data): pass

# utils/transform.py
def transform_data(data): pass

# user.py
def process_user(data):
    validated = validate_data(data)
    transformed = transform_data(validated)
    saved = save_user(transformed)
    send_welcome_email(saved)
```

**Structure for reusable code**:

```
backend/src/
  utils/              # Reusable functions
    format.py         # Date, string formatting
    validate.py       # Common validation logic
    transform.py      # Data transformation

frontend/src/
  components/
    shared/           # Reusable components
      Button.vue
      Input.vue
      Modal.vue
  utils/              # Reusable functions
    format.ts
    validate.ts
```

**Extraction criteria**:

1. "Will I use this elsewhere?" → Yes = move to `utils/shared`
2. "Copied twice already?" → Immediately move to `utils/shared`
3. "Domain-specific only?" → No = move to `utils/shared`

**Before working**: Check if similar functionality already exists in `utils/shared`

---

### 9. Security by Default

**Rule**: Security from the start, not later

**Required**:

- ✅ Input validation/sanitization
- ✅ Authentication required (except explicit public)
- ✅ Authorization check before data access
- ✅ Secrets in environment variables
- ✅ SQL parameterization
- ✅ **Structured logging with correlation IDs (JSON format)**
- ✅ **Never log sensitive data (tokens, passwords, PII)**

**Forbidden**:

- ❌ Plaintext passwords
- ❌ eval/exec with user input
- ❌ CORS allow all
- ❌ Disable SSL verification

---

### 10. Thorough Exception Handling

**Problem**: AI only considers happy path

**Rule**: Always handle exceptional cases

```python
# ❌ Ignoring errors
try:
    user = get_user()
except:
    print("error")

# ✅ Clear error handling
try:
    user = get_user()
except UserNotFound:
    raise HTTPException(404, "User not found")
except DatabaseError as e:
    logger.error(f"DB error: {e}")
    raise HTTPException(500, "Internal server error")
```

**Review**: Network failures, validation failures, abnormal user behavior

---

### 11. AI-Assisted Development Patterns

**Write code that AI can maintain:**

- **Early returns** over nested ternaries
- **Explicit types** over implicit any
- **Clear variable names** over abbreviations
- **Simple patterns** over clever one-liners
- **Comments on "why"** not "what" (explain business logic)

**Example**:

```python
# ❌ AI struggles with this
result = a if x else b if y else c if z else d

# ✅ AI understands this
if x:
    result = a
    return result
if y:
    result = b
    return result
if z:
    result = c
    return result
result = d
```

---

## 5. MCP Server Integration

**Context7 MCP** - Up-to-date library documentation:

- Working with external libraries (React, FastAPI, Stripe, etc.)
- Need current docs beyond AI training cutoff
- Implementing new integrations

**Usage Example**:

```python
# Get latest library docs
lib_id = mcp__context7__resolve_library_id("fastapi")
docs = mcp__context7__get_library_docs(
    context7CompatibleLibraryID=lib_id,
    topic="background tasks",
    tokens=8000
)
```

**Gemini Consultation** (if enabled):

- Complex architectural decisions
- Security-critical implementations
- Deep code reviews

**Rule**: Always verify MCP suggestions against project patterns.

---

## 6. Permissions

### Auto-Approved

- Reading files
- Single file: format, lint, typecheck, test

### Require Confirmation

- Installing packages
- Deleting/moving files
- Git push
- Environment config changes
- Full build/test suite
- DB migrations
- **Modifying 3+ files**

### When Uncertain

- **No guessing**
- **Ask questions**
- **Present options**
- **Plan first**

---

## ✅ Pre-Work Checklist

**Before starting any task**:

- [ ] Requirements clarified in EARS format?
- [ ] Plan to write tests first?
- [ ] Searched for similar existing features?
- [ ] If exists, checked and following same pattern?
- [ ] Checked if types/constants already defined?
- [ ] If not, define in config/types (OSOT)
- [ ] Chosen simplest solution?
- [ ] Extracting reusable logic to utils/shared?
- [ ] Plan for handling edge cases?
- [ ] Security considerations checked?

---

## 📊 Code Quality Standards

**Required before merge**:

- [ ] Linter passes (0 warnings)
- [ ] Type checker passes
- [ ] All tests pass
- [ ] console.log/print removed
- [ ] Commented code removed
- [ ] No TODOs (or linked to issues)

---

<!-- PROJECT_RULES_START -->
<!-- This section will be populated by /ms.constitution with project-specific rules -->
<!-- DO NOT manually edit this section -->
<!-- PROJECT_RULES_END -->

---

**Template Version**: 1.0.0
**Note**: This is a template file. Project-specific rules will be added by `/ms.constitution` command.

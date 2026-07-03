---
name: ms-essentials-debug
description: Advanced debugging skill for runtime errors with systematic stack trace analysis, error pattern recognition (NoneType, undefined, async issues, memory leaks, performance bottlenecks), root cause identification using 5-Whys methodology, memory profiling with tracemalloc, N+1 query detection, and test-first debugging workflow that follows TDD RED-GREEN-REFACTOR cycle to provide actionable fix suggestions. Use when encountering runtime errors, analyzing stack traces, debugging performance bottlenecks, investigating memory leaks, or diagnosing async/await issues
---

# MS Essentials Debug v1.0

## What It Does

Comprehensive debugging support for My-Spec projects with:

- **Stack trace analysis**: Parse and interpret error stack traces
- **Error pattern recognition**: Identify common error patterns (NoneType, undefined, async issues)
- **Debugging steps**: Provide systematic debugging workflow
- **Root cause identification**: Analyze code to find bug origins
- **Fix suggestions**: Recommend concrete fixes with code examples
- **Test-first debugging**: Write failing tests to reproduce bugs (TDD RED step)

**Key capabilities**:
- ✅ Python error analysis (TypeError, AttributeError, ImportError, etc.)
- ✅ TypeScript/JavaScript error analysis (undefined, null reference, promise rejection)
- ✅ Async/await debugging (unhandled promise rejection, race conditions)
- ✅ Test failure analysis (assertion errors, test isolation issues)
- ✅ Integration with TRUST 5 principles (Test-First debugging)

---

## When to Use

**Automatic triggers**:
- Runtime errors, exceptions, crashes
- Stack trace analysis requests
- Test failures
- "Why is this failing?", "Debug this error", "Fix this bug"

**Manual invocation**:
- When encountering unexplained behavior
- When tests are failing mysteriously
- When error messages are unclear
- When debugging async/promise issues
- During code reviews with bug reports

**Common scenarios**:
1. **NoneType/undefined errors**: Variable is None/undefined when it shouldn't be
2. **Async errors**: Promise rejection, race conditions, callback hell
3. **Import/module errors**: Missing dependencies, circular imports
4. **Test failures**: Assertion mismatches, test isolation issues
5. **Type errors**: Type mismatches in TypeScript/Python type hints

---

## How It Works

### 1. Error Analysis Phase

**Collect information**:
1. Full error message and stack trace
2. Code context (the failing function/module)
3. Input data or test case that triggered the error
4. Recent changes (git diff)

**Analyze stack trace**:
```python
# Example Python stack trace analysis
Traceback (most recent call last):
  File "src/auth/service.py", line 45, in authenticate
    user = self.user_repo.find_by_email(email)
  File "src/auth/repository.py", line 23, in find_by_email
    return self.db.query(User).filter(User.email == email).first()
AttributeError: 'NoneType' object has no attribute 'query'
```

**Diagnosis**:
- Root cause: `self.db` is None (database connection not initialized)
- Location: `src/auth/repository.py:23`
- Impact: Authentication flow completely broken
- Severity: CRITICAL (P0)

### 2. Root Cause Investigation

**Ask 5 Whys**:
1. Why is `self.db` None? → Database wasn't injected
2. Why wasn't it injected? → Constructor parameter missing
3. Why is constructor parameter missing? → Dependency injection misconfigured
4. Why is DI misconfigured? → Missing provider in container
5. Why is provider missing? → New developer didn't update DI config

**Check common causes**:
- ✅ Uninitialized variables
- ✅ Missing null checks
- ✅ Incorrect dependency injection
- ✅ Missing configuration
- ✅ Race conditions in async code
- ✅ Test isolation issues (shared state)

### 2.5 Hard-Bug Discipline (once a feedback loop exists)

For bugs that resist the 5-Whys pass above, once you have a red-capable command that reproduces
the failure (a failing test, curl script, or CLI invocation against a fixture):

**Reproduce + minimise**: confirm the loop reproduces the symptom the user actually described,
not a nearby different failure. Then shrink the repro to the smallest scenario that still goes
red — cut inputs/callers/config one at a time, re-running after each cut. Done when every
remaining element is load-bearing (removing any one turns the loop green). A minimal repro
narrows the hypothesis space below and becomes the regression test in the fix step.

**Hypothesise before instrumenting**: generate 3-5 ranked, falsifiable hypotheses up front —
"if X is the cause, changing Y will make the bug disappear" — before testing any of them.
Single-hypothesis anchoring on the first plausible idea is the most common way this goes wrong.

**Instrument with one probe per prediction**: change one variable at a time. Prefer a debugger/REPL
breakpoint over logs; if logging, tag every debug line with a unique prefix (e.g. `[DEBUG-a4f2]`)
so cleanup is one grep. Never "log everything and grep". For performance regressions, establish a
baseline measurement first (timing harness, profiler, query plan) — logs are usually the wrong
tool there.

**Fix at the correct seam**: write the regression test *before* the fix, but only at a seam that
exercises the real bug pattern as it occurs at the call site (a single-caller unit test is the
wrong seam if the bug needs multiple callers). If no correct seam exists, that itself is the
finding — note it and flag the architecture gap; a regression test at the wrong seam gives false
confidence.

**Close it out**: re-run the original (un-minimised) Phase 1 loop to confirm it no longer
reproduces, remove all `[DEBUG-...]` instrumentation, delete throwaway harnesses, and record which
hypothesis turned out correct in the commit/PR message.

### 3. Fix Strategy Development

**Test-First Debugging** (RED → GREEN → REFACTOR):

```python
# Step 1: RED - Write failing test to reproduce bug
def test_authenticate_with_valid_credentials():
    # Given: user exists in database
    user_repo = UserRepository(db_connection)
    auth_service = AuthService(user_repo)

    # When: authenticate with valid credentials
    result = auth_service.authenticate("test@example.com", "password123")

    # Then: authentication succeeds
    assert result.is_authenticated == True
    # ^ This test fails with AttributeError: 'NoneType' object has no attribute 'query'
```

```python
# Step 2: GREEN - Implement minimum fix
class UserRepository:
    def __init__(self, db_connection):
        if db_connection is None:
            raise ValueError("db_connection is required")
        self.db = db_connection  # Fix: ensure db is set

    def find_by_email(self, email: str) -> Optional[User]:
        if self.db is None:  # Defensive check
            raise RuntimeError("Database connection not initialized")
        return self.db.query(User).filter(User.email == email).first()
```

```python
# Step 3: REFACTOR - Improve design
class UserRepository:
    def __init__(self, db_connection: DatabaseConnection):
        """Inject database connection

        Args:
            db_connection: Must be a valid DatabaseConnection instance

        Raises:
            ValueError: If db_connection is None
        """
        if db_connection is None:
            raise ValueError("db_connection is required and cannot be None")
        self.db: DatabaseConnection = db_connection
```

### 4. Verification Steps

1. **Run the failing test** → Confirm it reproduces the bug (RED)
2. **Apply the fix** → Implement the solution
3. **Run the test again** → Verify it passes (GREEN)
4. **Run full test suite** → Ensure no regressions
5. **Manual testing** → Verify in actual application
6. **Code review** → Check fix quality against TRUST 5

---

## Failure Modes

### When debugging fails or is blocked:

1. **Missing context**: Stack trace incomplete or error message truncated
   - **Solution**: Enable full stack traces (`PYTHONTRACEBACK=1`, `NODE_OPTIONS=--trace-warnings`)

2. **Intermittent bugs**: Error doesn't reproduce consistently
   - **Solution**: Add logging, use debugger with breakpoints, check for race conditions

3. **Test isolation issues**: Test passes alone but fails in suite
   - **Solution**: Check for shared state, database cleanup between tests

4. **Production-only bugs**: Can't reproduce in development
   - **Solution**: Check environment differences, enable production logging, use feature flags

5. **Debugger not available**: No debugger tools installed
   - **Solution**: Fall back to print debugging, logging, or install language-specific debugger

---

## Best Practices

### ✅ DO:

1. **Write a failing test first** (RED step)
   - Reproduces the bug reliably
   - Documents expected behavior
   - Prevents regression

2. **Use the debugger** before making changes
   - Set breakpoints at error location
   - Inspect variable values
   - Step through execution

3. **Check the obvious first**:
   - Is the variable initialized?
   - Is the function called correctly?
   - Are types correct?
   - Is configuration missing?

4. **Document the fix** in code comments
   - Explain WHY the bug occurred
   - Reference the issue/ticket number
   - Add TODO if partial fix

5. **Follow TRUST 5 principles**:
   - **T**est-First: Write test before fix
   - **R**eadable: Clear variable names, comments
   - **U**nified: Type hints, consistent patterns
   - **S**ecured: Check for security implications
   - **T**rackable: Update TAG chains if needed

### ❌ DON'T:

1. **Don't guess and check** randomly
   - Understand the root cause first
   - Use systematic debugging approach

2. **Don't fix without a test**
   - How will you know it's fixed?
   - How will you prevent regression?

3. **Don't ignore error messages**
   - Error messages contain valuable clues
   - Stack traces show execution path

4. **Don't commit commented-out code**
   - Remove debug print statements
   - Remove temporary workarounds
   - Clean up before committing

5. **Don't skip the REFACTOR step**
   - Fix works but code is messy? Refactor it
   - Technical debt accumulates quickly

---

## Examples

### Example 1: Python NoneType Error

**Error**:
```python
AttributeError: 'NoneType' object has no attribute 'email'
```

**Debugging steps**:
1. Identify where the None value originated
2. Check function return types
3. Add null checks or Optional types
4. Write test for None case

**Fix**:
```python
# Before (no null check)
def get_user_email(user):
    return user.email  # Crashes if user is None

# After (defensive check)
def get_user_email(user: Optional[User]) -> str:
    if user is None:
        raise ValueError("User cannot be None")
    return user.email
```

### Example 2: JavaScript undefined Reference

**Error**:
```javascript
TypeError: Cannot read property 'name' of undefined
```

**Debugging steps**:
1. Check where the object comes from
2. Verify API response structure
3. Add optional chaining or null checks
4. Write test for undefined case

**Fix**:
```typescript
// Before (no null check)
function getUserName(user) {
  return user.name; // Crashes if user is undefined
}

// After (optional chaining)
function getUserName(user?: User): string {
  return user?.name ?? "Anonymous";
}
```

### Example 3: Async/Promise Rejection

**Error**:
```javascript
UnhandledPromiseRejectionWarning: Error: Connection timeout
```

**Debugging steps**:
1. Add .catch() to promise chain
2. Use try-catch with async/await
3. Check network/timeout configuration
4. Write test for error case

**Fix**:
```typescript
// Before (unhandled rejection)
async function fetchData(url: string) {
  const response = await fetch(url); // May throw
  return response.json();
}

// After (proper error handling)
async function fetchData(url: string): Promise<Data> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error(`Failed to fetch ${url}:`, error);
    throw new Error(`Data fetch failed: ${error.message}`);
  }
}
```

### Example 4: Memory Leak Debugging (Python)

**Symptom**: Memory usage grows unbounded over time (e.g., 100MB → 2GB in production)

**Debugging steps**:
1. Use `tracemalloc` to identify leak source
2. Check for circular references
3. Profile with `memory_profiler` decorator
4. Verify cleanup in `__del__` or context managers

**Investigation with tracemalloc**:
```python
import tracemalloc

# Start tracing
tracemalloc.start()

# Run your code
run_application()

# Get top memory consumers
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("[ Top 10 memory consumers ]")
for stat in top_stats[:10]:
    print(stat)
```

**Common memory leak patterns**:
```python
# ❌ LEAK: Class variable accumulates instances
class Cache:
    _instances = []  # Never cleared!

    def __init__(self, data):
        self.data = data
        self._instances.append(self)  # Memory leak

# ✅ FIX: Use weak references
import weakref

class Cache:
    _instances = weakref.WeakSet()  # Auto-cleanup when no strong refs

    def __init__(self, data):
        self.data = data
        self._instances.add(self)


# ❌ LEAK: Circular reference
class Node:
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []

    def add_child(self, child):
        child.parent = self  # Circular reference: parent ↔ child
        self.children.append(child)

# ✅ FIX: Use weak references for back-pointers
import weakref

class Node:
    def __init__(self, value):
        self.value = value
        self.parent = None  # Will be weakref
        self.children = []

    def add_child(self, child):
        child.parent = weakref.ref(self)  # Weak reference
        self.children.append(child)


# ❌ LEAK: Global cache never expires
_cache = {}

def get_data(key):
    if key not in _cache:
        _cache[key] = expensive_operation(key)  # Grows indefinitely
    return _cache[key]

# ✅ FIX: Use LRU cache with size limit
from functools import lru_cache

@lru_cache(maxsize=128)  # Automatically evicts oldest entries
def get_data(key):
    return expensive_operation(key)
```

**Memory profiling decorator**:
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    data = [i for i in range(1000000)]  # 8MB list
    return sum(data)

# Run with: python -m memory_profiler script.py
```

### Example 5: N+1 Query Problem (Performance Debugging)

**Symptom**: API endpoint takes >5 seconds to respond (should be <500ms)

**Debugging steps**:
1. Use `console.time()` / `time.time()` to measure sections
2. Check database query logs for repeated queries
3. Use ORM query debugging (SQLAlchemy `echo=True`, Django Debug Toolbar)
4. Profile with `cProfile` (Python) or Chrome DevTools (TypeScript)

**Identifying N+1 queries (Python/SQLAlchemy)**:
```python
# ❌ N+1 QUERY PROBLEM (1 + N queries)
def get_users_with_posts():
    users = db.query(User).all()  # 1 query: SELECT * FROM users
    for user in users:
        # N queries: SELECT * FROM posts WHERE user_id = ?
        posts = db.query(Post).filter(Post.user_id == user.id).all()
        user.posts = posts
    return users

# Queries executed:
# SELECT * FROM users;  (returns 100 users)
# SELECT * FROM posts WHERE user_id = 1;
# SELECT * FROM posts WHERE user_id = 2;
# ... (100 more queries)
# Total: 101 queries!


# ✅ FIX: Use JOIN to fetch in single query
def get_users_with_posts():
    return (
        db.query(User)
        .options(joinedload(User.posts))  # Eager loading with JOIN
        .all()
    )

# Queries executed:
# SELECT users.*, posts.*
# FROM users
# LEFT JOIN posts ON users.id = posts.user_id;
# Total: 1 query!
```

**TypeScript/Prisma example**:
```typescript
// ❌ N+1 QUERY PROBLEM
async function getUsersWithPosts() {
  const users = await prisma.user.findMany();  // 1 query

  for (const user of users) {
    user.posts = await prisma.post.findMany({  // N queries
      where: { userId: user.id }
    });
  }

  return users;
}


// ✅ FIX: Use include for eager loading
async function getUsersWithPosts() {
  return prisma.user.findMany({
    include: {
      posts: true  // Single query with JOIN
    }
  });
}
```

**Measuring query performance**:
```python
import time
import logging

# Enable SQLAlchemy query logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Measure execution time
start = time.time()
users = get_users_with_posts()
duration = time.time() - start

print(f"Query took {duration:.2f}s")
# Before: Query took 5.32s (101 queries)
# After: Query took 0.12s (1 query)
```

**General performance debugging checklist**:
- [ ] **Database queries**: Check for N+1, missing indexes
- [ ] **Memory**: Profile with `tracemalloc`, `memory_profiler`
- [ ] **CPU**: Profile with `cProfile`, Chrome DevTools
- [ ] **Network**: Check for redundant API calls
- [ ] **Caching**: Add memoization for expensive operations
- [ ] **Async**: Use concurrent execution where possible

---

## References

**Constitution**:
- Section I: Test-First Development (TDD RED → GREEN → REFACTOR)
- Section V: TRUST 5 Principles (Test-First, Readable, Unified, Secured, Trackable)

**Skills**:
- `ms-foundation-trust`: TRUST 5 validation
- `ms-lang-python`: Python debugging tools
- `ms-lang-typescript`: TypeScript debugging tools

**External Resources**:
- Python debugging: `pdb` module, `pytest` debugging flags
- TypeScript debugging: Chrome DevTools, VS Code debugger
- Async debugging: Promise debugging, async stack traces

---

## Changelog

- **v1.0.0** (2025-10-26): Initial release for My-Spec workflow
  - Stack trace analysis
  - Error pattern recognition
  - Test-first debugging workflow
  - Python/TypeScript/JavaScript support

---

## Works Well With

- `ms-essentials-review`: Use after fixing bugs for code quality review
- `ms-foundation-trust`: Validate TRUST 5 compliance after fixes
- `ms-workflow-tag-manager`: Update TAG chains after bug fixes
- `ms-lang-python`: Python-specific debugging techniques
- `ms-lang-typescript`: TypeScript-specific debugging techniques

---

**Usage**: Invoke this Skill when you encounter runtime errors, need to debug failing tests, or analyze stack traces. The Skill provides systematic debugging steps following Test-First principles from the Constitution.

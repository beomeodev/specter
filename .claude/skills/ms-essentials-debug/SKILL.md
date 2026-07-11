---
name: ms-essentials-debug
description: Advanced debugging skill for runtime errors with systematic stack trace analysis, error pattern recognition (NoneType, undefined, async issues, memory leaks, performance bottlenecks), root cause identification using 5-Whys methodology, memory profiling with tracemalloc, N+1 query detection, and test-first debugging workflow that follows TDD RED-GREEN-REFACTOR cycle to provide actionable fix suggestions. Use when encountering runtime errors, analyzing stack traces, debugging performance bottlenecks, investigating memory leaks, or diagnosing async/await issues
---

# MS Essentials Debug

## What It Does

Comprehensive debugging support for SPECTER projects with:

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

Worked examples with full debugging steps and fixes — NoneType errors, undefined
references, promise rejections, memory leak patterns (tracemalloc, weakref, lru_cache),
N+1 query detection (SQLAlchemy/Prisma), and the performance debugging checklist:
see [examples.md](examples.md). Read it when the error at hand matches one of those
classes; the workflow above is sufficient for everything else.

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

## Works Well With

- `ms-essentials-review`: Use after fixing bugs for code quality review
- `ms-foundation-trust`: Validate TRUST 5 compliance after fixes
- `ms-workflow-tag-manager`: Update TAG chains after bug fixes
- `ms-lang-python`: Python-specific debugging techniques
- `ms-lang-typescript`: TypeScript-specific debugging techniques

---

**Usage**: Invoke this Skill when you encounter runtime errors, need to debug failing tests, or analyze stack traces. The Skill provides systematic debugging steps following Test-First principles from the Constitution.

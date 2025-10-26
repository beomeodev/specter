---
name: ms-essentials-review
version: 1.0.0
created: 2025-10-26
updated: 2025-10-26
status: active
description: Automated code review with TRUST 5 principles, Constitution compliance, and language-specific best practices
keywords: ['code-review', 'trust', 'quality', 'best-practices', 'constitution']
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# MS Essentials Review v1.0

## Skill Metadata

| Field | Value |
| ----- | ----- |
| **Skill Name** | ms-essentials-review |
| **Version** | 1.0.0 |
| **Created** | 2025-10-26 |
| **Last Updated** | 2025-10-26 |
| **Allowed tools** | Read, Bash, Grep, Glob |
| **Auto-load** | On demand during code review or `/fin` workflow |
| **Trigger cues** | "review this code", "check quality", "is this good?", `/fin` command |

---

## What It Does

Automated code review with TRUST 5 principles enforcement and Constitution compliance checking.

**Key capabilities**:
- ✅ TRUST 5 principles validation (Test-First, Readable, Unified, Secured, Trackable)
- ✅ Constitution compliance checking (file size, function complexity, security rules)
- ✅ Code quality metrics (test coverage, linting, type checking)
- ✅ Security vulnerability scanning
- ✅ Performance best practices
- ✅ Documentation completeness checking
- ✅ TAG chain integrity verification

---

## When to Use

**Automatic triggers**:
- During `/fin` workflow (quality gate before commit)
- Code review requests
- SPEC implementation complete (`/ms.implement` post-step)
- Pull request creation

**Manual invocation**:
- Review code for TRUST 5 compliance
- Check Constitution adherence
- Validate security best practices
- Assess code quality before commit
- Pre-merge quality gate

**Common scenarios**:
1. **Before committing**: Ensure code meets quality standards
2. **After implementation**: Validate TRUST 5 compliance
3. **During code review**: Provide systematic feedback
4. **Before deployment**: Final quality check

---

## How It Works

### Review Checklist (TRUST 5 Framework)

#### 1. **T**est-First (Test Coverage & Quality)

**Check**:
- [ ] Test coverage ≥85% (Constitution Section I)
- [ ] All critical paths have tests (auth, payment, security)
- [ ] Tests follow RED → GREEN → REFACTOR cycle
- [ ] Test names describe behavior clearly
- [ ] No commented-out tests
- [ ] Test isolation (no shared state)

**Commands**:
```bash
# Python test coverage
pytest tests/ --cov=src/ --cov-report=term-missing --cov-report=html
# Must show ≥85% coverage

# TypeScript test coverage
npm test -- --coverage
# Must show ≥85% coverage
```

**Failure examples**:
- ❌ Coverage below 85%: "Add tests for uncovered code paths"
- ❌ No tests for new feature: "Write tests before implementation (TDD RED step)"
- ❌ Tests have side effects: "Ensure test isolation, clean up state"

---

#### 2. **R**eadable (Code Clarity & Simplicity)

**Check**:
- [ ] File ≤500 SLOC (Source Lines of Code, excluding comments)
- [ ] Function ≤100 LOC (Lines of Code)
- [ ] Function parameters ≤5
- [ ] Nesting depth ≤4 levels
- [ ] Cyclomatic complexity ≤10 per function
- [ ] Clear variable names (no abbreviations unless standard)
- [ ] Functions have single responsibility

**Commands**:
```bash
# Python complexity check
ruff check src/ --select C90 --config "C90 = {max-complexity = 10}"

# TypeScript complexity check
npx eslint src/ --rule 'complexity: ["error", 10]'

# Count lines in file (SLOC)
python -c "
import sys
with open(sys.argv[1]) as f:
    lines = [l for l in f if l.strip() and not l.strip().startswith('#')]
    print(f'{len(lines)} SLOC')
" <file_path>
```

**Failure examples**:
- ❌ File exceeds 500 SLOC: "Split file into smaller modules"
- ❌ Function exceeds 100 LOC: "Extract helper functions"
- ❌ Complexity > 10: "Simplify conditional logic, reduce branches"
- ❌ Poor naming: "Rename `d` to `database_connection`"

---

#### 3. **U**nified (Type Safety & Consistency)

**Check**:
- [ ] TypeScript `strict: true` or Python `mypy --strict` passes
- [ ] Zero type errors
- [ ] Consistent code style (linter passes)
- [ ] No `any` types in TypeScript (use proper typing)
- [ ] No untyped Python functions (add type hints)
- [ ] TAG blocks present and correct

**Commands**:
```bash
# TypeScript type checking
npx tsc --noEmit
# Must exit with code 0

# Python type checking
mypy src/ --strict
# Must exit with code 0

# Linting
ruff check src/      # Python
npx eslint src/      # TypeScript
```

**Failure examples**:
- ❌ Type errors: "Fix type mismatches, add proper types"
- ❌ `any` abuse: "Replace `any` with specific types"
- ❌ Linter warnings: "Fix all linting issues before commit"
- ❌ Missing TAG blocks: "Add @CODE TAG blocks to new files"

---

#### 4. **S**ecured (Security Best Practices)

**Check**:
- [ ] No hardcoded secrets (passwords, API keys, tokens)
- [ ] Input validation on all user inputs
- [ ] SQL parameterization (no string interpolation)
- [ ] XSS prevention (HTML escaping, CSP headers)
- [ ] CSRF protection (tokens, SameSite cookies)
- [ ] Password hashing (bcrypt/argon2, ≥10 rounds)
- [ ] HTTPS for all external communication
- [ ] No `eval()` or `exec()` with user input

**Commands**:
```bash
# Check for hardcoded secrets
rg -i 'password\s*=\s*["\']' src/
rg -i 'api[_-]?key\s*=\s*["\']' src/
# Should return no results

# Python security scan
pip install bandit
bandit -r src/ -f json

# TypeScript/JavaScript security scan
npm audit
# Should show 0 vulnerabilities
```

**Failure examples**:
- ❌ Hardcoded password: "Move to environment variable"
- ❌ SQL injection risk: "Use parameterized queries"
- ❌ No input validation: "Validate all user inputs"
- ❌ Weak hashing: "Use bcrypt with ≥10 rounds"

---

#### 5. **T**rackable (Traceability & Documentation)

**Check**:
- [ ] TAG blocks present (@CODE, @SPEC, @TEST, @CHAIN)
- [ ] TAG chains complete (SPEC → TEST → CODE)
- [ ] No orphaned TAGs (TAG without file)
- [ ] README updated if public API changed
- [ ] CHANGELOG updated with user-facing changes
- [ ] Comments explain WHY, not WHAT
- [ ] API documentation present (docstrings)

**Commands**:
```bash
# Scan TAG blocks
rg '@(SPEC|TEST|CODE|DOC):' -n --type-add 'md:*.md' --type md --type py --type ts

# Check TAG integrity
python .claude/hooks/ms/core/project.py
# Should show high integrity percentage

# Find orphaned TAGs
# Example: @CODE:AUTH-001 exists but no file found
rg '@CODE:AUTH-001' -l
# Should return at least one file
```

**Failure examples**:
- ❌ Missing TAG blocks: "Add @CODE TAG blocks to new files"
- ❌ Broken TAG chains: "Ensure @SPEC → @TEST → @CODE chain complete"
- ❌ Orphaned TAGs: "Remove TAG or restore missing file"
- ❌ No docstrings: "Add docstrings to public functions"

---

## Failure Modes

### When code review fails or is blocked:

1. **Tools not installed**: Linter, type checker, or test runner missing
   - **Solution**: Install required tools per language (see Constitution)

2. **Configuration missing**: No `tsconfig.json`, `pyproject.toml`, etc.
   - **Solution**: Initialize configuration files

3. **Tests take too long**: Test suite runs for minutes
   - **Solution**: Parallelize tests, mock external dependencies

4. **Type errors too many**: Hundreds of type errors to fix
   - **Solution**: Incrementally add type hints, use `# type: ignore` temporarily with TODO

5. **Security scan false positives**: Tool reports non-issues
   - **Solution**: Review manually, add suppression comments with justification

---

## Best Practices

### ✅ DO:

1. **Review in order**: Follow TRUST 5 sequence
   - Start with tests (coverage check)
   - Then readability (complexity)
   - Then types (type safety)
   - Then security (vulnerabilities)
   - Finally traceability (TAG chains)

2. **Automate what you can**:
   - Use linters, type checkers, security scanners
   - Run tests automatically in CI/CD
   - Validate TAG integrity in pre-commit hooks

3. **Document issues clearly**:
   - Include file path and line number
   - Explain WHY it's an issue
   - Suggest concrete fix

4. **Check Constitution compliance**:
   - File size ≤500 SLOC
   - Function complexity ≤10
   - Test coverage ≥85%

5. **Focus on high-impact issues first**:
   - Security vulnerabilities (P0)
   - Failing tests (P0)
   - Missing tests (P1)
   - Code quality (P2)
   - Style issues (P3)

### ❌ DON'T:

1. **Don't nitpick style issues**
   - Let the linter handle it
   - Focus on logic and design

2. **Don't block on minor issues**
   - Security/correctness: blocking
   - Style/naming: non-blocking suggestions

3. **Don't skip security checks**
   - Always run security scanner
   - Always check for hardcoded secrets

4. **Don't review without context**
   - Read the SPEC first
   - Understand the feature requirements
   - Check related files

5. **Don't approve without running tests**
   - Run full test suite
   - Check test coverage report
   - Verify tests actually test behavior

---

## Examples

### Example 1: Full Review Output

**Input**: Review `src/auth/service.py`

**Output**:
```markdown
## Code Review: src/auth/service.py

### ✅ PASS: Test-First
- Test coverage: 92% (exceeds 85% requirement)
- All critical paths tested
- Tests follow TDD workflow

### ❌ FAIL: Readable
- Function `validate_and_authenticate` is 127 LOC (exceeds 100 LOC limit)
  - **Fix**: Extract `validate_credentials()` helper function
- Complexity of `handle_login_flow`: 14 (exceeds 10)
  - **Fix**: Simplify conditional logic, reduce nested if statements

### ✅ PASS: Unified
- Type checking: 0 errors
- All functions have type hints
- Linting: 0 warnings

### ⚠️ WARNING: Secured
- Line 45: Potential SQL injection if `email` contains malicious input
  - **Fix**: Use parameterized query: `User.query.filter_by(email=email).first()`
- No rate limiting on login endpoint
  - **Recommendation**: Add rate limiting to prevent brute force attacks

### ✅ PASS: Trackable
- TAG block present: @CODE:AUTH-001
- TAG chain complete: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
- Docstrings present

### Summary
**Blocking issues**: 1 security issue (SQL injection risk)
**Non-blocking issues**: 2 readability issues (function too long, complexity too high)

**Action required**: Fix SQL injection before merge
```

### Example 2: Quick Quality Check

**Input**: Check if code is ready for commit

**Output**:
```markdown
## Quality Gate: BLOCKED ❌

**Blocking issues**:
1. Test coverage: 62% (below 85% requirement)
   - Add tests for: `src/payment/processor.py` (0% coverage)
2. Type errors: 3 errors in `src/payment/types.ts`
   - Fix: Add proper types to `processPayment()` function
3. Security: 1 HIGH severity npm vulnerability
   - Run: `npm audit fix`

**Non-blocking issues**:
1. File `src/utils/helpers.py` is 543 SLOC (exceeds 500 limit)
   - Consider: Split into smaller modules

**Recommendation**: Fix blocking issues before commit
```

---

## References

**Constitution**:
- Section I: Test-First Development (≥85% coverage)
- Section II: Simplicity-First Architecture (≤500 SLOC files, ≤100 LOC functions, ≤10 complexity)
- Section V: TRUST 5 Principles (comprehensive quality framework)
- Section VII: Security by Default (security requirements)

**Skills**:
- `ms-foundation-trust`: TRUST 5 validation framework
- `ms-foundation-constitution`: Constitution principles reference
- `ms-lang-python`: Python code quality tools
- `ms-lang-typescript`: TypeScript code quality tools

**External Resources**:
- Test coverage tools: `pytest --cov`, `jest --coverage`
- Linters: `ruff`, `eslint`, `pylint`
- Type checkers: `mypy`, `tsc`
- Security scanners: `bandit`, `npm audit`, `snyk`

---

## Changelog

- **v1.0.0** (2025-10-26): Initial release for My-Spec workflow
  - TRUST 5 principles validation
  - Constitution compliance checking
  - Security vulnerability scanning
  - TAG chain integrity verification
  - Python/TypeScript/JavaScript support

---

## Works Well With

- `ms-essentials-debug`: Use after fixing issues identified in review
- `ms-foundation-trust`: Deep TRUST 5 validation
- `ms-foundation-constitution`: Constitution principles reference
- `ms-workflow-tag-manager`: TAG chain management
- `ms-lang-python`: Python-specific quality tools
- `ms-lang-typescript`: TypeScript-specific quality tools

---

**Usage**: Invoke this Skill during code reviews, before committing, or as part of `/fin` workflow to ensure code meets TRUST 5 principles and Constitution requirements. The Skill provides systematic quality checks with concrete fix suggestions.

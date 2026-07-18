---
name: trust-validation
description: Comprehensive code quality validator enforcing TRUST 5 principles - Test-First (≥85% coverage with pytest/vitest), Readable (≤700 SLOC production files / tests no limit, ≤10 complexity), Unified (strict type checking with mypy/tsc), Secured (OWASP Top 10 implementation patterns + trivy/bandit scanning, cryptographic best practices, input validation, authorization checks, adversarial abuse-case review for IDOR/multi-tenant isolation), Trackable (complete TAG anchor chain integrity SPEC→TEST→CODE) with detailed compliance reports and remediation guidance. Use when validating quality before merging PRs, running quality gate checks, checking release readiness, validating TRUST compliance, or performing comprehensive code reviews
---

# Foundation: TRUST 5 Validation

## What it does

Validates code compliance with Constitution Section IV (TRUST Review Model):
- **T**est First: Coverage ≥85%
- **R**eadable: File/function size limits, complexity ≤10
- **U**nified: Type safety, linter compliance
- **S**ecured: No vulnerabilities, input validation
- **T**rackable: Complete TAG chains (@SPEC → @TEST → @CODE)

## When to use

- Before merging PR (`/ms.review`)
- Quality gate checks (`/ms.analyze`)
- Release validation
- CI/CD pipeline execution
- Manual quality audits

## How it works

### T - Test First (Coverage ≥85%)

**Supported Tools**:
- Python: `pytest --cov` (pytest-cov)
- TypeScript/JS: Vitest or Jest with coverage
- Go: `go test -cover`
- Rust: `cargo tarpaulin`

**Validation Command** (Python):
```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=85
```

**Coverage Metrics**:
- Line coverage ≥85% per Constitution Section III (or the active project threshold)
- Branch coverage ≥80% (RECOMMENDED)
- Function coverage ≥90% (RECOMMENDED)

**Quality Gates** (findings in this skill's report; blocking is decided by `/ms.review` or CI per
Constitution Section IV's gate-ownership table, not by this skill):
- ✅ Coverage ≥85%: PASS
- ❌ Coverage <85%: FAIL finding (the validation command itself exits non-zero below 85 —
  single threshold, no intermediate WARNING band)

### R - Readable (Code Quality)

**Size Constraints** (from Constitution):
- Production file ≤700 SLOC (test files: no limit)
- Function ≤100 LOC
- Parameters ≤5 per function
- Nesting depth ≤4 levels
- Cyclomatic complexity ≤10

**Linting Tools**:
- Python: `ruff check .` (fast linter + formatter)
- TypeScript: `biome check .` or `eslint .`
- Go: `golangci-lint run`
- Rust: `cargo clippy`

**Validation**:
```bash
# Python
ruff check . --select C90 --max-complexity 10

# TypeScript
npx eslint . --max-warnings 0
```

### U - Unified (Architecture & Type Safety)

**Type Checking**:
- Python: `mypy src/ --strict`
- TypeScript: `tsc --noEmit --strict`
- Go: `go vet ./...`
- Rust: `cargo check`

**Architecture Checks**:
- SPEC-driven structure (code mirrors spec.md organization)
- Clear module boundaries
- Dependency direction (inward toward domain)
- No circular dependencies

**Validation**:
```bash
# Python type check
mypy src/ --strict --disallow-untyped-defs

# TypeScript type check
tsc --noEmit --strict --noUnusedLocals --noUnusedParameters
```

### S - Secured (Security Implementation & Scanning)

**1. SAST Tools** (Automated Scanning):
- `trivy`: Vulnerability scanning (CVE database)
- `bandit`: Python security issues (B-series warnings)
- `npm audit`: JavaScript dependency vulnerabilities
- `semgrep`: Static analysis patterns (custom rules)

**2. OWASP Top 10 Implementation Patterns**:

**A01 - Broken Access Control**:
```python
# ✅ Verify authorization before data access
@login_required
def get_user_data(user_id: int):
    if current_user.id != user_id and not current_user.is_admin:
        abort(403, "Unauthorized access")
    return User.query.get(user_id)
```

**A02 - Cryptographic Failures**:
```python
# ✅ Use bcrypt for password hashing
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# ✅ Use Fernet for data encryption
from cryptography.fernet import Fernet
cipher = Fernet(key)
encrypted = cipher.encrypt(data.encode())
```

**A03 - Injection Prevention**:
```python
# ✅ Use parameterized queries (ORM or prepared statements)
User.query.filter_by(email=email).first()  # Safe

# ❌ NEVER use string formatting
# query = f"SELECT * FROM users WHERE email='{email}'"  # Vulnerable!
```

**A05 - Security Misconfiguration**:
```python
# ✅ Flask security headers (Flask-Talisman)
from flask_talisman import Talisman
Talisman(app, force_https=True, strict_transport_security=True)

# ✅ CORS whitelist (not allow all)
from flask_cors import CORS
CORS(app, origins=["https://trusted-domain.com"])
```

**A07 - Identification and Authentication**:
```python
# ✅ Secure session management
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ✅ Rate limiting (prevent brute force)
from flask_limiter import Limiter
limiter = Limiter(app, default_limits=["200 per day", "50 per hour"])
```

**3. Security Checklist**:
- ✅ **No hardcoded secrets**: API keys, passwords in environment variables
- ✅ **Input validation**: Schema validation (Pydantic/Zod) on all external data
- ✅ **Authorization checks**: Role-based access control (RBAC) before data access
- ✅ **Cryptographic best practices**: bcrypt for passwords, Fernet for data
- ✅ **No HIGH/CRITICAL vulnerabilities**: trivy/bandit scan passes
- ✅ **Framework security headers**: CSP, HSTS, X-Frame-Options configured
- ✅ **Dependencies up-to-date**: Regular updates, no known CVEs

**4. Validation Commands**:
```bash
# Vulnerability scan
trivy fs --severity HIGH,CRITICAL .

# Python security
bandit -r src/ -ll

# Dependency audit
npm audit --audit-level=high

# Check for secrets (git-secrets or truffleHog)
git secrets --scan
```

**5. Adversarial Review (Abuse-Case Analysis)**:

The checklist above verifies controls *exist*; adversarial review asks whether they can be *bypassed* for the app's actual data flows. Run it on every endpoint that reads or writes user-scoped data — checklist-only review misses these (a common root-cause class of data-confidentiality leaks). For each endpoint, answer: *who* may call it, with *whose* resource IDs, returning *whose* data?

- ✅ **IDOR / BOLA**: the authorization check must bind the **requester's identity** to the **resource owner** — not merely require "logged in". Actively try substituting another user's ID.
- ✅ **Multi-tenant isolation**: list/query endpoints must scope the `WHERE` clause to the current principal **server-side**; a client-supplied filter must never *widen* scope.
  ```python
  # ❌ Leak: client controls the scope
  Submission.query.filter_by(owner_id=request.args["owner_id"])
  # ✅ Scope bound to the authenticated principal
  Submission.query.filter_by(owner_id=current_user.id)
  ```
- ✅ **Mass assignment**: update endpoints must whitelist writable fields (Pydantic/Zod), never bind the raw request body to the model — block a user setting `is_admin` or another `user_id`.
- ✅ **Business-logic / workflow bypass**: can a step be skipped or replayed (a protected resource before its precondition, a reused one-time token)? Validate state and single-use server-side.
- ✅ **Minimal response / no PII over-exposure**: return only the fields the caller needs; never leak other principals' identifiers in responses or logs.

Record findings as GEARS `[Security]` requirements with `@SPEC:SEC-*` TAGs and the same PASS/WARNING/CRITICAL severity used elsewhere in this report; fixes belong to `/ms.implement --mode=refactor` or the main conversation.

**6. Fail-Open vs Fail-Secure Defaults**:

The distinction: fail-open patterns run with a weak default when configuration is absent;
fail-secure patterns crash safely instead. `SECRET = env.get('KEY') or 'default'` is fail-open
(starts up with an inadequate secret); `SECRET = env['KEY']` is fail-secure (halts if missing).
Scan for six categories:

- **Fallback secrets**: `getenv(X) or 'default'` patterns that let the app start without a
  required credential.
- **Hardcoded credentials**: passwords/API keys assigned directly in source.
- **Fail-open toggles**: security flags defaulting to disabled (`AUTH_REQUIRED = false`).
- **Weak cryptography**: MD5/SHA1/DES/RC4/ECB in an auth or encryption context.
- **Permissive access control**: CORS wildcards, `0777` permissions, public-by-default resources.
- **Debug-on-by-default**: stack traces / introspection / verbose errors in user-facing responses.

For each candidate: trace whether it fires at startup or at request time, whether the app
continues without the value, and whether the *production* configuration actually supplies it —
absent or default-reliant in production is CRITICAL; supplied in production but still present in
code is a lower-severity code-level exposure (still record it). Exclude test fixtures,
`.example`/`.template` files, and dev-only compose setups. Do not accept "prod sets it" or "auth
exists anyway" as a reason to skip recording the code-level finding — verify the trace, don't
assume it.

**For detailed OWASP examples**: See `examples.md` for A01-A10 Before/After code patterns

### T - Trackable (TAG Chain Integrity)

**TAG Structure**:
- `@SPEC:ID` in `specs/<spec-id>/tasks.md` (or `spec.md`)
- `@TEST:ID` in `tests/`
- `@CODE:ID` in `src/`

**Chain Validation**:
```bash
# Scan all TAGs
rg '@(SPEC|TEST|CODE|DOC):' -n specs/ tests/ src/ docs/

# Find orphaned TAGs
rg '@CODE:AUTH-001' -l src/          # CODE exists
rg '@SPEC:AUTH-001' -l specs/        # SPEC missing → orphan

# Find duplicate TAGs
rg '@SPEC:AUTH-001' -c specs/ | awk '$1 > 1 {print "Duplicate: " $0}'
```

**Integrity Metrics**:
- Complete chains: % of @SPEC with @TEST and @CODE
- Orphaned TAGs: TAGs without corresponding files
- Duplicate TAGs: Same TAG ID used multiple times

## Inputs
- Source code (`src/`, `tests/`)
- Spec documents (`specs/`)
- Project configuration (`.specify/memory/constitution.md`)
- CI/CD configuration

## Outputs
- TRUST compliance report (JSON or Markdown)
- Pass/fail per principle
- Detailed violations with line numbers
- Suggested remediation actions
- Overall quality score (0-100%)

## Example Report

```json
{
  "trust_compliance": {
    "test_first": {
      "status": "PASS",
      "coverage": 87.5,
      "threshold": 85.0
    },
    "readable": {
      "status": "WARNING",
      "violations": [
        {
          "file": "src/auth/service.py",
          "type": "complexity",
          "function": "refresh_token",
          "value": 12,
          "limit": 10
        }
      ]
    },
    "unified": {
      "status": "PASS",
      "type_errors": 0
    },
    "secured": {
      "status": "FAIL",
      "vulnerabilities": [
        {
          "severity": "HIGH",
          "package": "requests",
          "version": "2.25.0",
          "fixed_in": "2.31.0"
        }
      ]
    },
    "trackable": {
      "status": "PASS",
      "chain_integrity": 100.0,
      "orphaned_tags": 0
    }
  },
  "overall_score": 85.0,
  "decision": "CONDITIONAL_PASS"
}
```

## CI/CD Integration

**GitHub Actions Workflow**:
```yaml
name: TRUST Validation

on: [pull_request, push]

jobs:
  trust-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # T - Test First
      - name: Run tests with coverage
        run: |
          pip install pytest pytest-cov
          pytest --cov=src --cov-fail-under=85

      # R - Readable
      - name: Lint code
        run: |
          pip install ruff
          ruff check . --max-complexity 10

      # U - Unified
      - name: Type check
        run: |
          pip install mypy
          mypy src/ --strict

      # S - Secured
      - name: Security scan
        run: |
          pip install bandit
          bandit -r src/ -ll

      # T - Trackable
      - name: TAG integrity check
        run: |
          rg '@(SPEC|TEST|CODE):' -n specs/ tests/ src/ | wc -l
```

## Related Sources
- File size / complexity limits: Constitution §II (`constitution-template.md`)
- TAG chain rules and scanning: `/ms.implement` Step 3 +
  `scripts/specter/check_tag_chain.py`
- Review rubric and executable gates: `/ms.review`

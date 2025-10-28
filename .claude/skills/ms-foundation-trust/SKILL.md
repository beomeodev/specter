---
name: ms-foundation-trust
description: Comprehensive code quality validator enforcing TRUST 5 principles - Test-First (≥85% coverage with pytest/vitest), Readable (≤500 SLOC files, ≤10 complexity), Unified (strict type checking with mypy/tsc), Secured (vulnerability scanning with trivy/bandit, no hardcoded secrets), Trackable (complete TAG chain integrity SPEC→TEST→CODE→DOC) with detailed compliance reports and remediation guidance
---

# Foundation: TRUST 5 Validation

## Skill Metadata
| Field | Value |
| ----- | ----- |
| Version | 1.0.0 |
| Created | 2025-10-26 |
| Allowed tools | Read, Bash, Grep |
| Auto-load | `/ms.analyze`, `/ms.review` |
| Trigger cues | Quality validation, release readiness, TRUST compliance |

## What it does

Validates code compliance with Constitution Section V (TRUST 5 Principles):
- **T**est First: Coverage ≥85%
- **R**eadable: File/function size limits, complexity ≤10
- **U**nified: Type safety, linter compliance
- **S**ecured: No vulnerabilities, input validation
- **T**rackable: Complete TAG chains (@SPEC → @TEST → @CODE → @DOC)

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
pytest --cov=src --cov=tests --cov-report=term-missing --cov-fail-under=85
```

**Coverage Metrics**:
- Line coverage ≥85% (MANDATORY)
- Branch coverage ≥80% (RECOMMENDED)
- Function coverage ≥90% (RECOMMENDED)

**Quality Gates**:
- ✅ Coverage ≥85%: PASS
- ⚠️ 80% ≤ Coverage <85%: WARNING
- ❌ Coverage <80%: FAIL (blocks implementation)

### R - Readable (Code Quality)

**Size Constraints** (from Constitution):
- File ≤500 SLOC
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

### S - Secured (Security & Vulnerability Scanning)

**SAST Tools**:
- `trivy`: Vulnerability scanning
- `bandit`: Python security issues
- `npm audit`: JavaScript dependencies
- `semgrep`: Static analysis patterns

**Security Checklist**:
- ✅ No hardcoded secrets (API keys, passwords)
- ✅ Input validation on all external data
- ✅ Environment variables for sensitive config
- ✅ No HIGH/CRITICAL vulnerabilities
- ✅ Dependencies up-to-date

**Validation**:
```bash
# Vulnerability scan
trivy fs --severity HIGH,CRITICAL .

# Python security
bandit -r src/ -ll

# Dependency audit
npm audit --audit-level=high
```

### T - Trackable (TAG Chain Integrity)

**TAG Structure**:
- `@SPEC:ID` in `specs/<spec-id>/spec.md`
- `@TEST:ID` in `tests/`
- `@CODE:ID` in `src/`
- `@DOC:ID` in `docs/`

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

## Related Skills
- `ms-foundation-constitution`: File size and complexity validation
- `moai-foundation-tags`: TAG scanning and inventory
- `moai-essentials-review`: Automated code review

---
name: ms-foundation-constitution
description: Constitution Section II compliance validator for Simplicity-First Architecture that checks file size limits (≤700 SLOC for production code; test files have no limit), function complexity using McCabe metrics (≤10 cyclomatic complexity), function length constraints (≤100 LOC), and provides actionable refactoring suggestions with split strategies when violations detected. Use when validating code quality, checking file size limits, analyzing function complexity, reviewing Constitution compliance, implementing new features, or running quality gate checks
---

# Foundation: Constitution Compliance

## What it does

Validates code compliance with Constitution Section II (Simplicity-First Architecture):
- Production file size ≤700 SLOC (excluding comments/blank lines); test files: NO LIMIT
- Function complexity ≤10 per function
- Function size ≤100 LOC
- Provides actionable feedback when violations detected

## When to use

- Before implementing new code (`/ms.implement`)
- During code review (`/ms.review`)
- Quality gate checks (`/ms.analyze`)
- When files approach size limits
- Automated CI/CD validation

## How it works

### File Size Validation (≤700 SLOC production; test files exempt)

**SLOC Calculation**:
```bash
# Count source lines (exclude comments and blank lines)
# Python
grep -v '^\s*#' file.py | grep -v '^\s*"""' | grep -v '^\s*$' | wc -l

# TypeScript/JavaScript
grep -v '^\s*//' file.ts | grep -v '^\s*\*' | grep -v '^\s*$' | wc -l
```

**Validation Rules**:
- ✅ Production SLOC ≤700: PASS  (test files: exempt — never failed for length)
- ⚠️ 600 < SLOC ≤700: WARNING (approaching limit)
- ❌ Production SLOC >700: FAIL (must split file)

**Split Strategies** (when production SLOC >700):
1. Extract reusable utilities → `utils/` or `lib/`
2. Separate types/interfaces → `types/` or `models/`
3. Split by domain responsibility → multiple focused modules

### Function Complexity Validation (≤10)

**Tools**:
- Python: `radon cc` (McCabe complexity)
- TypeScript/JavaScript: ESLint `complexity` rule
- Go: `gocyclo`
- Rust: `cargo-geiger`

**Example (Python)**:
```bash
# Install radon
pip install radon

# Check complexity
radon cc src/ -a -nb --total-average

# Output format:
# src/auth/service.py
#   M 15:0 authenticate_user - A (8)  ← OK (≤10)
#   M 42:0 refresh_token - B (12)     ← VIOLATION (>10)
```

**Complexity Scale** (McCabe):
- A (1-5): Simple
- B (6-10): Moderate ✅ ACCEPTABLE
- C (11-20): Complex ❌ VIOLATION
- D (21-50): Very complex ❌ CRITICAL
- E (51+): Unmaintainable ❌ CRITICAL

**Refactoring Strategies** (when complexity >10):
1. Extract helper functions
2. Simplify conditional logic (guard clauses)
3. Replace nested if-else with early returns
4. Extract complex calculations into separate functions

### Function Size Validation (≤100 LOC)

**LOC Calculation** (includes comments):
```bash
# Count lines between function definition and next function/EOF
# Python example
awk '/^def / {start=NR} /^def / && start {print NR-start; start=NR}' file.py
```

**Validation Rules**:
- ✅ LOC ≤100: PASS
- ⚠️ 80 < LOC ≤100: WARNING
- ❌ LOC >100: FAIL (extract helpers)

## Inputs
- Source code files (`src/`, `lib/`, `app/`)
- Test files (`tests/`)
- Language configuration (`.specify/config.json`)

## Outputs
- Compliance report (pass/fail per file)
- SLOC metrics with file-by-file breakdown
- Complexity violations with line numbers
- Suggested refactoring actions

## Example Report

```json
{
  "compliance_status": "FAIL",
  "violations": [
    {
      "file": "src/auth/service.py",
      "type": "file_size",
      "sloc": 587,
      "limit": 700,
      "suggestion": "Extract helpers to src/auth/utils.py"
    },
    {
      "file": "src/auth/service.py",
      "type": "complexity",
      "function": "refresh_token",
      "complexity": 12,
      "limit": 10,
      "line": 42,
      "suggestion": "Extract token validation logic to separate function"
    }
  ],
  "summary": {
    "total_files": 15,
    "compliant_files": 13,
    "violations": 2
  }
}
```

## CI/CD Integration

**GitHub Actions Example**:
```yaml
- name: Constitution Compliance Check
  run: |
    # Python
    pip install radon
    radon cc src/ -a -nb --total-average --min B

    # TypeScript
    npm run lint -- --max-complexity 10
```

## Examples

Full before/after validation walkthroughs (file-size PASS/FAIL, complexity
PASS/FAIL with refactoring splits, function-length checks): see
[examples.md](examples.md).

## Related Skills
- `ms-foundation-trust`: Overall TRUST 5 validation
- `ms-essentials-review`: Code review automation

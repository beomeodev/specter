---
description: "Code quality review after implementation"
---

# /ms.review - Code Quality Review

Performs deep code quality review after `/ms.implement` completes. Focuses on code design, maintainability, and best practices (NOT requirements validation - that's `/speckit.checklist`).

## Overview

**Purpose**: Review implemented code quality AFTER `/ms.implement`

**NOT for**:
- ❌ Requirements validation (use `/speckit.checklist`)
- ❌ TRUST metrics (use `/ms.analyze`)
- ❌ Build/test/lint checks (use `/ms.analyze` Level 2)

**FOR**:
- ✅ Code design quality (architecture, patterns, DRY)
- ✅ Maintainability (naming, comments, error handling)
- ✅ Performance issues (N+1 queries, unnecessary computations)
- ✅ Security deep-dive (auth gaps, logging leaks, error exposure)
- ✅ Test quality (AAA pattern, boundary tests, mock overuse)

## Workflow Position

```
/ms.implement → /ms.review → /fin
```

**When to run**: After implementing all tasks, before final commit

## Execution Steps

### Step 1: Prerequisites Check

Run prerequisites script to get context:

```bash
docs/src/lib/scripts/check-prerequisites.sh --json --require-spec --require-plan --include-tasks
```

Parse JSON output to extract:
- `REPO_ROOT`: Repository root path
- `FEATURE_DIR`: Feature directory (e.g., `specs/001-auth-spec/`)
- `AVAILABLE_DOCS`: List of available documents (spec.md, plan.md, tasks.md, etc.)

**Required files**:
- ✅ `spec.md` (for domain terminology)
- ✅ `plan.md` (for architecture reference)
- ✅ Implemented code files (src/, tests/)

**If missing**: Display error and suggest running `/ms.specify` or `/ms.plan`

---

### Step 2: Load Context (Optimized - Cached)

```bash
declare -A CONTEXT_CACHE

load_context_documents() {
  CONTEXT_CACHE[spec_raw]=$(cat "$FEATURE_DIR/spec.md" 2>/dev/null || echo "")
  CONTEXT_CACHE[plan_raw]=$(cat "$FEATURE_DIR/plan.md" 2>/dev/null || echo "")
  CONTEXT_CACHE[constitution_raw]=$(cat .specify/memory/constitution.md 2>/dev/null || echo "")

  export DOMAIN_TERMS=$(echo "${CONTEXT_CACHE[spec_raw]}" | rg -o '(?<=## Domain Terminology).*?(?=##)' -U || true)
  export ARCH_LAYERS=$(echo "${CONTEXT_CACHE[plan_raw]}" | rg -o '(?<=## Architecture).*?(?=##)' -U || true)
  export SPEC_CONTENT="${CONTEXT_CACHE[spec_raw]}"
  export PLAN_CONTENT="${CONTEXT_CACHE[plan_raw]}"
}

load_context_documents
```

Read: spec.md, plan.md, constitution.md (once, cached in memory)

---

### Step 1.5: Tool Availability Check (NEW)

Review relies on several external binaries. Check for them upfront and fall back gracefully when unavailable:

```bash
command -v jq >/dev/null    || echo "⚠️ jq missing → JSON aggregation steps will be skipped"
command -v rg >/dev/null    || { echo "❌ ripgrep required for pattern scan"; exit 1; }
command -v npx >/dev/null   || echo "⚠️ npx missing → eslint/jscpd checks will be skipped"
command -v radon >/dev/null || echo "⚠️ radon missing → Python complexity scan skipped"
command -v jscpd >/dev/null || echo "⚠️ jscpd missing → duplicate detection skipped"
```

Store availability flags (e.g., `HAS_JQ=1`) for later conditionals so that each static-analysis phase can short-circuit instead of failing mid-run.

---

### Step 2.5: Intent & Focus Charter (NEW)

Compile a succinct charter that anchors the review:

1. **Derive primary risks** from `spec.md` constraints, plan.md architecture, and constitution guardrails.
2. **List the review targets** (files, components, user paths) coming from prerequisites JSON and recent implementation tasks.
3. **State up to three key questions** the review must answer (e.g., “Auth flow still follows token rotation rules?”).

**Output**:

```
INTENT & FOCUS CHARTER 🧭
- Scope: {feature summary}
- Mandatory Risks: {critical-path | security | performance | integration}
- Key Questions:
  1. ...
  2. ...
  3. ...
```

Save the charter in memory for later reporting and re-run comparisons.

---

### Step 3: Smart File Discovery

```bash
discover_changed_files() {
  local BASE_REF="${1:-origin/main}"

  # Priority 1: Git diff
  CHANGED_FILES=$(git diff --name-only --diff-filter=ACMRTUXB ${BASE_REF}...HEAD 2>/dev/null \
    | rg '^(src|tests)/.*\.(ts|js|py|tsx|jsx)$' || true)
  [ -n "$CHANGED_FILES" ] && echo "$CHANGED_FILES" && return 0

  # Priority 2: Staged files
  CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACMRTUXB 2>/dev/null \
    | rg '^(src|tests)/.*\.(ts|js|py|tsx|jsx)$' || true)
  [ -n "$CHANGED_FILES" ] && echo "$CHANGED_FILES" && return 0

  # Priority 3: Smoke test (200 files)
  rg -l '' src tests 2>/dev/null | rg '\.(ts|js|py|tsx|jsx)$' | head -n 200
}

export CHANGED_FILES=$(discover_changed_files)
export CHANGED_TS=$(echo "$CHANGED_FILES" | rg '\.(ts|tsx|js|jsx)$' || true)
export CHANGED_PY=$(echo "$CHANGED_FILES" | rg '\.py$' || true)
```

---

### Step 3.5: Hash-Based Cache

```bash
compute_file_hashes() {
  local targets="$1"
  local cache_file=".specify/review-hash.cache"

  [ -z "$targets" ] && echo "$targets" && return 0

  echo "$targets" | xargs -P "$(nproc)" -I{} sh -c 'echo "$(sha1sum "{}" 2>/dev/null | cut -d" " -f1)  {}"' \
    | sort -k2 > .specify/review-hash.now 2>/dev/null || true

  if [ -f "$cache_file" ]; then
    comm -13 <(sort -k2 "$cache_file" 2>/dev/null || true) <(sort -k2 .specify/review-hash.now) \
      | cut -d' ' -f2- > .specify/review-changed-by-hash.txt
    TRULY_CHANGED=$(cat .specify/review-changed-by-hash.txt)
  else
    TRULY_CHANGED="$targets"
  fi

  cp .specify/review-hash.now "$cache_file" 2>/dev/null || true
  echo "$TRULY_CHANGED"
}

export ANALYSIS_TARGETS=$(compute_file_hashes "$CHANGED_FILES")
```

---

### Step 4: Static Analysis (Parallel)

```bash
run_parallel_static_analysis() {
  mkdir -p .specify/review
  (
    # Process 1: jscpd (conditional - files >200 LOC only)
    {
      large_files=$(echo "$ANALYSIS_TARGETS" | xargs -I{} sh -c 'wc -l "{}" 2>/dev/null | awk "{if (\$1 > 200) print \$2}"' || true)
      if [ -n "$large_files" ] && command -v jscpd &>/dev/null; then
        npx jscpd $large_files --threshold 5 --format json --output .specify/review/jscpd.json 2>/dev/null || echo '{"duplicates":[]}' > .specify/review/jscpd.json
      else
        echo '{"duplicates":[],"skip":"no large files"}' > .specify/review/jscpd.json
      fi
    } &

    # Process 2: eslint (JS/TS complexity)
    {
      if [ -n "$CHANGED_TS" ]; then
        npx eslint --cache --cache-location .specify/.eslintcache --cache-strategy content \
          --rule 'complexity: [error, 10]' --rule 'max-lines-per-function: [error, {max: 100}]' \
          --format json $CHANGED_TS > .specify/review/eslint.json 2>&1 || echo '[]' > .specify/review/eslint.json
      else
        echo '[]' > .specify/review/eslint.json
      fi
    } &

    # Process 3: radon (Python complexity)
    {
      if [ -n "$CHANGED_PY" ]; then
        printf "%s\n" $CHANGED_PY | xargs -P "$(nproc)" -I{} radon cc -nb --json {} 2>/dev/null \
          | jq -s 'add // {}' > .specify/review/radon.json 2>/dev/null || echo '{}' > .specify/review/radon.json
      else
        echo '{}' > .specify/review/radon.json
      fi
    } &

    # Process 4: ripgrep (pattern detection)
    {
      run_consolidated_ripgrep
    } &

    wait
  )
}

run_parallel_static_analysis
```

#### C. Pattern Detection (Single-Pass)

```bash
run_consolidated_ripgrep() {
  rg --json -n -e 'eval\(' -e '(console\.(log|debug|info|warn))' -e '(process\.env\.|os\.getenv)' \
    -e 'await.*for.*of' -e '\.map\(.*await' -e 'for.*for.*for' -e '\b[0-9]{3,}\b' \
    -e '(TODO|FIXME|XXX|HACK):' -e '(password|secret|token)\s*=\s*["\']' -e '(setTimeout|setInterval)\(' \
    --type-add 'code:*.{ts,js,py,tsx,jsx}' --type code --iglob '!**/*.snap' --iglob '!**/node_modules/**' \
    ${CHANGED_FILES:-src tests} > .specify/review-rg.ndjson 2>/dev/null || echo '{}' > .specify/review-rg.ndjson

  jq -r 'select(.type == "match") | {file: .data.path.text, line: .data.line_number, match: .data.lines.text}' \
    .specify/review-rg.ndjson > .specify/review-patterns.json 2>/dev/null || echo '[]' > .specify/review-patterns.json
}

run_consolidated_ripgrep
```

---

### Step 5: AI-Based Deep Analysis

Perform context-aware analysis using AI judgment.

**Pattern Aggregation** (for Step 5.5): Track issue patterns incrementally during analysis. When same issue category appears 3+ times, mark as systemic.

#### A. Naming Quality Review

**For each core file** (services, models, controllers):

1. **Read file content**
2. **Extract**: Class names, function names, variable names
3. **Compare with spec.md**:
   - Do function names use domain terminology from spec?
   - Are entity names consistent with data-model.md?
   - Are abbreviations avoided (except industry standard: API, HTTP, JWT)?

**Scoring**:
- **HIGH**: Generic names (e.g., `processData`, `handleRequest`, `doStuff`)
- **MEDIUM**: Inconsistent naming (e.g., `getUserData` vs `fetchUser`)
- **LOW**: Verbose names that could be simplified

**Output format**:
```
H-001: Generic function name "processData" in src/services/user.service.ts:45
  Recommendation: Use domain term from spec.md (e.g., "validateUserCredentials")
  Reference: spec.md FR-003 "User Authentication"
```

#### B. Architecture Consistency

**Compare plan.md structure vs actual files**:

1. **Read plan.md** "Architecture" section
2. **Extract expected layers**: Controller → Service → Repository
3. **Scan actual file structure**:
   ```bash
   tree src/ -L 2 --dirsfirst
   ```
4. **Validate**:
   - Are files organized in expected layers?
   - Do controllers only call services (not repositories)?
   - Are business rules in services (not controllers)?

**Violations**:
- **HIGH**: Controller directly accessing database (skipping service layer)
- **MEDIUM**: Service calling another service's repository
- **LOW**: File misplaced in wrong directory

**Output format**:
```
H-002: Architecture violation in src/controllers/user.controller.ts:67
  Issue: Controller directly calls UserRepository (should call UserService)
  Expected: Controller → Service → Repository (plan.md §3.2)
```

#### C. Comment Quality Review (Conditional)

Only analyze if complexity >7 detected:

```bash
HIGH_COMPLEXITY_FILES=$(jq -r '.[] | select(.complexity > 7) | .filePath' .specify/review/eslint.json 2>/dev/null | sort -u)
[ -z "$HIGH_COMPLEXITY_FILES" ] && echo "⏭️  Skip (all complexity ≤7)" && exit 0
echo "$HIGH_COMPLEXITY_FILES" | xargs -I{} rg "^[\s]*//|^[\s]*/\*" {} --json
```

Check for "why" comments (good) vs "what" comments (redundant).

#### D. Error Handling

Check error handling consistency: custom exceptions vs generic Error, logging patterns.

#### E. Test Quality

Validate AAA pattern, boundary tests, mock usage. **HIGH** if no tests for critical paths.

#### F. Performance

Detect N+1 queries (loops with DB calls), unnecessary recomputation, memory leaks.

#### G. Security

Check missing auth on endpoints, sensitive data in logs, stack trace exposure.

#### H. Simplicity & Surgical Changes (Karpathy)

- **Overcomplication**: speculative abstractions, unrequested flexibility/config, error handling for impossible cases, "200 lines that could be 50". Senior test: would a senior call it overcomplicated?
- **Non-surgical diff**: changed lines that DON'T trace to the task — adjacent "improvements", style churn, refactors of unbroken code, deletion of pre-existing (not orphaned-by-this-change) code. (Planned refactor tasks are exempt — they ARE the request.)

---

### Step 5.5: ultrathink Pattern Analysis

**ultrathink**: Analyze systemic patterns (3+ occurrences) using aggregated data from Step 5.

For each pattern: 5-Why root cause analysis → Prevention strategy → Batch fix opportunity.

---

### Step 6: Consolidate and Score

Aggregate issues from automated tools + AI analysis.

**Impact filtering**: Hide LOW issues with score <15. Promote HIGH-impact LOW to MEDIUM.

**Score**: `100 - (critical×20 + high×5 + medium×2 + low×0.5)`

---

### Step 7: Report Generation

```bash
mkdir -p docs/review
AGENT_NAME="${CLAUDE_SESSION:+Claude}"
AGENT_NAME="${AGENT_NAME:-${GEMINI_SESSION:+Gemini}}"
AGENT_NAME="${AGENT_NAME:-Claude}"
REPORT_FILE="docs/review/review_${AGENT_NAME}_$(date +%y%m%d-%H%M%S).md"
```

Report structure (console + file):

- Summary: CRITICAL/HIGH/MEDIUM/LOW counts, overall score
- Intent & Focus Charter (inline copy of Step 2.5 so report is self-contained)
- Production Risks, Strategic Unlocks, Quick Wins
- Coverage Checklist
- Hidden LOW issues count (show with `--verbose`)

---

### Step 8: Interactive Actions (NEW)

**Only if HIGH/CRITICAL issues exist**, prompt user:

- Auto-fix options for high-confidence issues (N+1 queries, missing auth guards)
- Re-run verification after applying fixes
- Or continue without fixes (flagged in `/fin`)

---

### Step 9: Cleanup and State Management

Remove analysis artifacts and save state for `/fin` integration:

```bash
REVIEW_CACHE_DIR=".specify"
REVIEW_TMP_FILES=(
  "$REVIEW_CACHE_DIR/review-rg.ndjson"
  "$REVIEW_CACHE_DIR/review-patterns.json"
  "$REVIEW_CACHE_DIR/review/jscpd.json"
  "$REVIEW_CACHE_DIR/review/eslint.json"
  "$REVIEW_CACHE_DIR/review/radon.json"
  "$REVIEW_CACHE_DIR/review-changed-by-hash.txt"
  "$REVIEW_CACHE_DIR/review-hash.now"
)

# Remove temporary analysis files (keep review-hash.cache to speed up next run)
for file in "${REVIEW_TMP_FILES[@]}"; do
  rm -f "$file"
done

# Save state for /fin integration (NEW)
if [ $HIGH_COUNT -gt 0 ]; then
  echo "$HIGH_COUNT HIGH issues unresolved" > .specify/review-state.txt
  echo "Run /ms.review to check" >> .specify/review-state.txt
  echo "Review report: $REPORT_FILE" >> .specify/review-state.txt
fi
```

**Keep warnings in memory**: Store HIGH/CRITICAL issues for `/fin` command to check

- **Artifact Policy**
  - Persists: `.specify/review-hash.cache` (used for hash-based diffing on the next run)
  - Removed: `.specify/review/*.json`, `.specify/review-rg.ndjson`, transient hash files
  - Reports: `docs/review/review_{agent}_{timestamp}.md` kept for audit trail

---

## User Options

### Quick Mode (NEW)

Skip pattern analysis for faster review:

```bash
/ms.review --quick
# Skips: ultrathink pattern analysis (Step 5.5)
# Runs: Regular checks only (30% faster)
```

### Verbose Mode (NEW)

Show all issues including filtered ones:

```bash
/ms.review --verbose
# Shows: All LOW issues (even those with impact score <15)
# Useful for: Complete code audit
```

### No Interactive Mode (NEW)

Skip action prompts for CI/CD:

```bash
/ms.review --no-interactive
# Skips: Interactive action prompts (Step 8)
# Useful for: Automated pipelines
```

### Skip Slow Checks

For quick review during development:

```bash
/ms.review --fast
# Skips: automated tools (jscpd, complexity analysis)
# Runs: only AI-based pattern detection
```

### Focus on Category

Review specific aspect only:

```bash
/ms.review --focus security
/ms.review --focus performance
/ms.review --focus naming
/ms.review --focus tests
```

**Categories**:
- `security`: Authentication, logging, error exposure
- `performance`: N+1 queries, unnecessary computations
- `naming`: Variable/function names vs domain terms
- `architecture`: Layer violations, pattern consistency
- `tests`: Test quality, boundary cases, mock usage
- `maintainability`: Comments, error handling, duplication

---

## Integration with Workflow

### After /ms.implement

```bash
# Implementation complete
/ms.implement  # ✅ All tasks implemented

# Review code quality
/ms.review  # ⚠️ Found 2 HIGH issues

# Fix issues
# ... (fix H-001 and H-002)

# Re-review
/ms.review  # ✅ All HIGH issues resolved

# Finish and commit
/fin
```

### Before /fin (ENHANCED)

`/fin` command should check for review state:

```bash
# In /fin workflow
if [ -f .specify/review-state.txt ]; then
  echo "⚠️ Code review found HIGH issues:"
  cat .specify/review-state.txt
  echo ""
  echo "Continue anyway? (not recommended) [y/N]"
  read -r response
  if [ "$response" != "y" ]; then
    echo "❌ Aborted. Fix issues first or run /ms.review"
    exit 1
  fi
fi
```

The review state file contains:
- Number of unresolved HIGH issues
- Path to the latest review report
- Timestamp of last review

---

## Difference from Other Commands

| Command | Purpose | Checks | When to Run |
|---------|---------|--------|-------------|
| `/ms.analyze` | Structure + TRUST validation | Tests run, lint pass, coverage ≥85%, TAG integrity | Before `/ms.implement` |
| `/ms.review` | Code quality + design | Naming, architecture, performance, security deep-dive | After `/ms.implement` |
| `/speckit.checklist` | Requirements validation | Spec requirements met, functional correctness | Any time (manual) |
| `/fin` | Final commit | CI checks, warnings acknowledgment | After all reviews pass |

**Mental model**:
- `/ms.analyze` = "Can I build?" (structure)
- `/ms.review` = "Should I merge?" (quality)
- `/speckit.checklist` = "Did I build the right thing?" (requirements)

---

## Error Handling

### No Implemented Files Found

```
❌ No implemented files found

Expected directories:
- src/ (source code)
- tests/ (test files)

Run /ms.implement first to generate code.
```

### Missing Context Documents

```
⚠️ Missing context documents

Found:
- spec.md ✅
- plan.md ❌ (run /ms.plan)

Review will proceed with limited context.
Some checks (architecture validation, naming consistency) may be skipped.
```

### Tool Installation Missing

```
⚠️ Optional tool not found: jscpd

Skipping code duplication analysis.
Install with: npm install -g jscpd

Review will continue with remaining checks.
```

---

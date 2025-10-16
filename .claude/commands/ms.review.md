---
description: "Code quality review after implementation (post-implement step)"
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
.specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-plan --include-tasks
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

### Step 2: Load Context

Read all available context documents:

**REQUIRED**:
1. **spec.md**: Extract domain terminology, entity names, business rules
2. **plan.md**: Extract architecture layers, file structure, tech stack
3. **Constitution** (`.specify/memory/constitution.md`): Extract project-specific constraints (Section IX)

**IF EXISTS**:
4. **data-model.md**: Entity relationships for validation
5. **contracts/**: API contracts for consistency checks
6. **tasks.md**: Implementation task list (to understand what was built)

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

### Step 3: Scan Implemented Files

Identify all implemented files for review:

```bash
# Find all source files (exclude tests initially)
find src/ -type f \( -name "*.ts" -o -name "*.js" -o -name "*.py" \) 2>/dev/null

# Find all test files separately
find tests/ -type f \( -name "*.test.ts" -o -name "*.spec.ts" -o -name "*_test.py" \) 2>/dev/null
```

**Categorize files**:
- **Core**: Business logic, services, repositories
- **API**: Controllers, routes, endpoints
- **Tests**: Unit tests, integration tests
- **Config**: Configuration files

---

### Step 4: Automated Static Analysis

Run automated tools for measurable metrics (parallel execution):

#### A. Code Duplication Check

**JavaScript/TypeScript**:
```bash
npx jscpd src/ --threshold 5 --format json --output .specify/review-jscpd.json
```

**Python**:
```bash
pylint src/ --duplicate-code --output-format=json > .specify/review-pylint.json 2>&1 || true
```

**Parse results**:
- **Threshold**: >5% duplication = HIGH
- **Output format**: File paths, duplicated lines, similarity %

#### B. Complexity Analysis

**JavaScript/TypeScript**:
```bash
npx eslint src/ \
  --rule 'complexity: [error, 10]' \
  --rule 'max-lines-per-function: [error, 100]' \
  --format json \
  > .specify/review-complexity.json 2>&1 || true
```

**Python**:
```bash
radon cc src/ -a -nb --json > .specify/review-radon.json
```

**Parse results**:
- Complexity >10 = HIGH
- Function >100 LOC = MEDIUM

#### C. Anti-Pattern Detection (ripgrep)

Run pattern searches for common anti-patterns:

**Security Anti-Patterns**:
```bash
# Hardcoded secrets or env vars
rg "process\.env\." src/ --type ts --json || true
rg "os\.getenv" src/ --type py --json || true

# Eval usage
rg "eval\(" src/ --json || true

# Console logs in production
rg "console\.(log|debug|info)" src/ --json || true
```

**Performance Anti-Patterns**:
```bash
# Async in loops (N+1 pattern)
rg "await.*for.*of" src/ --json || true
rg "\.map\(.*await" src/ --json || true

# Nested loops
rg "for.*for" src/ --json || true
```

**Maintainability Anti-Patterns**:
```bash
# Magic numbers
rg "\b[0-9]{3,}\b" src/ --json || true

# TODO/FIXME comments
rg "(TODO|FIXME|XXX|HACK)" src/ --json || true
```

**Collect all matches**: Store file paths, line numbers, matched patterns

---

### Step 5: AI-Based Deep Analysis

Perform context-aware analysis using AI judgment:

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

#### C. Comment Quality Review

**For complex functions** (complexity >5):

1. **Check for comments**:
   ```bash
   rg "^[\s]*//|^[\s]*/\*" src/ --json
   ```
2. **Analyze comment type**:
   - **What comments**: Redundant (e.g., `// increment counter` before `counter++`)
   - **Why comments**: Good (e.g., `// Using BCrypt rounds=12 per OWASP 2023`)
3. **Missing comments**: Complex logic without explanation

**Scoring**:
- **MEDIUM**: Complex function (complexity >7) without any comments
- **LOW**: Redundant "what" comments

**Output format**:
```
M-001: Complex function lacks explanation in src/services/auth.service.ts:89
  Complexity: 9 (>7 threshold)
  Recommendation: Add comment explaining JWT refresh logic
```

#### D. Error Handling Consistency

**Scan all try-catch blocks**:

```bash
rg "try\s*\{" src/ --json
```

**For each try-catch**:
1. **Check error type**: Generic `Error` or custom exception?
2. **Check error message**: Descriptive or vague?
3. **Check logging**: Is error logged before re-throwing?

**Pattern consistency check**:
- Do all services use the same error handling pattern?
- Are errors properly typed (TypeScript) or classed (Python)?

**Scoring**:
- **HIGH**: No error handling in critical paths (auth, payment)
- **MEDIUM**: Inconsistent error patterns across services
- **LOW**: Generic error messages

**Output format**:
```
M-002: Inconsistent error handling in src/services/payment.service.ts:34
  Issue: Uses generic "throw new Error()" while other services use custom exceptions
  Recommendation: Use PaymentException class (see src/exceptions/payment.exception.ts)
```

#### E. Test Quality Review

**For each test file**:

1. **Check test structure**:
   ```bash
   rg "(describe|it|test)\(" tests/ --json
   ```
2. **Validate AAA pattern**:
   - Arrange: Setup test data
   - Act: Execute function
   - Assert: Verify outcome
3. **Check boundary tests**:
   - Are edge cases tested? (null, empty, max values)
4. **Check mock usage**:
   - Are mocks overused? (mocking everything = not integration test)

**Scoring**:
- **HIGH**: No tests for critical paths (auth, payment)
- **MEDIUM**: Missing edge case tests
- **LOW**: Inconsistent test naming

**Output format**:
```
M-003: Missing boundary tests in tests/auth/service.test.ts
  Issue: Only tests happy path (valid credentials)
  Missing: null input, empty string, SQL injection attempt
  Reference: spec.md FR-003 "SHALL validate all inputs"
```

#### F. Performance Analysis

**Manual review for known patterns**:

1. **N+1 Query Detection**:
   - Read service files
   - Look for loops containing DB queries
   - Example:
     ```typescript
     for (const user of users) {
       user.posts = await postRepo.findByUserId(user.id); // N+1!
     }
     ```

2. **Unnecessary Recomputation**:
   - Look for repeated calls to expensive functions
   - Check for missing memoization/caching

3. **Memory Leak Patterns**:
   - Event listeners not removed
   - Timers not cleared
   - Large arrays not released

**Scoring**:
- **HIGH**: N+1 query in hot path
- **MEDIUM**: Unnecessary recomputation
- **LOW**: Potential memory leak

**Output format**:
```
H-003: N+1 query detected in src/services/user.service.ts:45
  Issue: Fetching posts in loop (1 query for users + N queries for posts)
  Recommendation: Use eager loading or single JOIN query
  Performance impact: O(N) queries instead of O(1)
```

#### G. Security Deep-Dive

**Beyond `/ms.analyze` Level 3**:

1. **Authentication Coverage**:
   - Scan all API endpoints
   - Check for missing auth decorators/middleware
   ```bash
   rg "@(Get|Post|Put|Delete)\(" src/controllers/ --json
   ```
   - Cross-reference with `@UseGuards(JwtAuthGuard)` or equivalent

2. **Sensitive Data Logging**:
   - Check log statements for sensitive data
   ```bash
   rg "(logger\.|console\.log).*password|token|secret" src/ --json
   ```

3. **Error Message Exposure**:
   - Check if stack traces are exposed in production
   ```bash
   rg "res\.send\(.*error\.stack" src/ --json
   ```

**Scoring**:
- **CRITICAL**: Missing auth on sensitive endpoint
- **HIGH**: Password/token in logs
- **MEDIUM**: Stack trace exposed

**Output format**:
```
C-001: Missing authentication on sensitive endpoint
  File: src/controllers/user.controller.ts:23
  Issue: GET /users/:id has no @UseGuards(JwtAuthGuard)
  Reference: Constitution §VIII "All endpoints SHALL require authentication"
```

---

### Step 5.5: Deep Pattern Analysis with ultrathink (NEW)

After collecting all issues from Step 5:

**ultrathink**

Activate maximum cognitive capabilities for cross-cutting pattern analysis:

#### Pattern Recognition Framework:

1. **Systemic Issue Detection**:
   - If 3+ files have the same issue type → Mark as systemic
   - Group related issues for batch fixing
   - Identify common root causes

2. **Root Cause Analysis** (5-Why Method):
   For each HIGH/CRITICAL issue, ask:
   - WHY does this issue exist? (immediate cause)
   - WHY did that happen? (underlying cause)
   - WHY did the underlying happen? (root cause)
   - What prevention would stop recurrence?

3. **Technical Debt Clustering**:
   Group issues by refactoring opportunity:
   - All error handling issues → One PR to standardize
   - All naming issues in one module → One refactoring session
   - All missing tests → One test sprint

4. **Impact Amplification**:
   Identify issues that compound each other:
   - Missing auth + logging passwords = CRITICAL combination
   - N+1 query + no caching = Performance disaster
   - No error handling + no tests = Maintenance nightmare

5. **Prevention Strategy Generation**:
   For each systemic pattern, suggest:
   - ESLint/Pylint rule to catch automatically
   - Team convention documentation update
   - CI check addition
   - Architecture decision record (ADR)

**Output Enhancement**:
Add new section after regular issues:

```
══════════════════════════════════════════════════
 PATTERN ANALYSIS (ultrathink) 🧠
══════════════════════════════════════════════════

🔍 SYSTEMIC ISSUES DETECTED: 3

1. Inconsistent Error Handling Pattern
   📊 Frequency: 5 occurrences across 3 services
   📍 Files: auth.service.ts, payment.service.ts, user.service.ts

   ROOT CAUSE ANALYSIS:
   • Immediate: Different developers, different patterns
   • Underlying: No team error handling convention
   • Root: Missing architectural decision on error strategy

   PREVENTION STRATEGY:
   • Short-term: Add error handling template to CLAUDE.md
   • Long-term: Implement custom exception hierarchy
   • Automation: ESLint rule for try-catch patterns

   BATCH FIX OPPORTUNITY:
   • Fix all 5 occurrences in single PR (est. 2 hours)
   • ROI: Prevents ~10 hours/month debugging time

2. N+1 Query Cluster
   📊 Frequency: 2 occurrences (high impact)
   📍 Files: user.service.ts:45, post.service.ts:67

   ROOT CAUSE: Missing ORM best practices knowledge
   AMPLIFIED BY: No query logging in development

   STRATEGIC FIX:
   • Enable query logging in dev
   • Team training on eager loading
   • Add N+1 detection to CI pipeline

💡 STRATEGIC RECOMMENDATIONS:

Priority 1: Fix Root Causes (8 hours total)
   → Prevents 80% of future similar issues

Priority 2: Batch Similar Fixes (4 hours total)
   → Single PR for each pattern type

Priority 3: Add Automation (2 hours total)
   → 5 new ESLint rules
   → 2 git hooks
   → 1 CI check

TOTAL INVESTMENT: 14 hours
ESTIMATED SAVINGS: 40 hours/month
ROI: 286% in first month
```

---

### Step 6: Consolidate and Score (ENHANCED)

**Aggregate all issues**:

1. **From automated tools**: Duplication, complexity, anti-patterns
2. **From AI analysis**: Naming, architecture, comments, errors, tests, performance, security

#### Impact-Based Display Filtering (NEW):

```typescript
// Calculate impact score for smart filtering
for (const issue of allIssues) {
  if (issue.severity === 'LOW') {
    // Estimate impact components (each 0-100)
    const usersAffected = estimateUsersAffected(issue);      // % of users affected
    const performanceHit = estimatePerformanceImpact(issue);  // % performance degradation
    const fixEffort = estimateFixHours(issue);                // hours to fix

    // Calculate composite impact score
    issue.impactScore =
      (usersAffected * 0.4) +         // 40% weight: user impact
      (performanceHit * 0.3) +         // 30% weight: performance
      (Math.max(0, 10 - fixEffort) * 3); // 30% weight: fix ease (capped at 10 hours)

    // Apply smart filtering based on impact
    if (issue.impactScore < 15) {
      issue.displayMode = 'hidden';     // Hide very low impact issues
    } else if (issue.impactScore > 50) {
      issue.displayMode = 'promoted';   // Promote high-impact LOW issues
      issue.severity = 'MEDIUM';        // Upgrade severity for display
    } else {
      issue.displayMode = 'normal';     // Show normally
    }
  }
}

// Group issues for final display
const mainIssues = issues.filter(i => i.displayMode !== 'hidden');
const hiddenCount = issues.filter(i => i.displayMode === 'hidden').length;

// Coverage checklist population
const coverage = {
  criticalPath: coveredByAgents(['architecture', 'core', 'integration']),
  security: coveredByAgents(['security']),
  performance: coveredByAgents(['performance']),
  integration: coveredByAgents(['api', 'dependencies'])
};

if (!coverage.criticalPath || !coverage.security || !coverage.performance || !coverage.integration) {
  console.warn('⚠️ Coverage gap detected. Launching supplemental analysis.');
  // Trigger focused re-checks for missing areas before reporting
}

storeCoverageForReport(coverage);
```

**Calculate scores**:

```typescript
interface ReviewScore {
  critical: number;  // Must fix before merge
  high: number;      // Should fix before merge
  medium: number;    // Consider fixing
  low: number;       // Nice to have
  overall: number;   // 0-100 scale
}
```

**Overall score calculation**:
```
overall = 100 - (critical * 20 + high * 5 + medium * 2 + low * 0.5)
```

**Score interpretation**:
- **90-100**: Excellent (0 critical, 0-1 high)
- **80-89**: Good (0 critical, 2-3 high)
- **70-79**: Acceptable (0 critical, 4+ high)
- **<70**: Needs improvement (critical issues present)

---

### Step 7: Console Output and Report Generation (High-Impact Default)

Display comprehensive review report to console AND save to file:

#### Generate Review Report File:

```bash
# Create docs/review directory if it doesn't exist
mkdir -p docs/review

# Determine the AI agent name based on execution context
# Check which AI assistant is running this command
if [ -n "$CLAUDE_SESSION" ] || [ -f ".claude/context" ]; then
    AGENT_NAME="Claude"
elif [ -n "$GEMINI_SESSION" ] || command -v gemini &> /dev/null; then
    AGENT_NAME="Gemini"
elif [ -n "$CODEX_SESSION" ] || command -v codex &> /dev/null; then
    AGENT_NAME="Codex"
else
    AGENT_NAME="Claude"  # Default fallback
fi

# Generate timestamp
TIMESTAMP=$(date +"%y%m%d-%H%M%S")

# Create report filename
REPORT_FILE="docs/review/review_${AGENT_NAME}_${TIMESTAMP}.md"

echo "📝 Saving review report to: $REPORT_FILE"
```

#### Report Content Structure:

Save the following content to BOTH console AND report file:

```markdown
# Code Review Report

**Reviewer**: ${AGENT_NAME}
**Date**: ${TIMESTAMP}
**Feature**: ${FEATURE_NAME}
**Files Reviewed**: ${FILE_COUNT} (${SOURCE_COUNT} source, ${TEST_COUNT} test)

## Intent & Focus Charter 🧭
- Scope: ${FOCUS_SCOPE}
- Mandatory Risks: ${MANDATORY_RISKS}
- Key Questions:
  1. ${QUESTION_ONE}
  2. ${QUESTION_TWO}
  3. ${QUESTION_THREE}

## Executive Summary

┌───────────────────────────────────────────────────────────────┐
│ HIGH-IMPACT SNAPSHOT                                          │
├───────────────────────────────────────────────────────────────┤
│ CRITICAL: ${CRITICAL_COUNT}                                   │
│ HIGH:     ${HIGH_COUNT} ⚠️                                    │
│ ROI Unlocks: ${STRATEGIC_COUNT}                               │
│ Quick Wins: ${QUICK_WIN_COUNT} ⚡                              │
├───────────────────────────────────────────────────────────────┤
│ OVERALL SCORE: ${OVERALL_SCORE}/100 (${SCORE_LABEL})        │
└───────────────────────────────────────────────────────────────┘

## 🚨 Production Risks (48시간 이내 영향)
[Critical/High issues impacting stability, security, or performance]

## 🎯 Strategic Unlocks (ROI > 25%)
[Architecture or capability upgrades tied to business impact]

## ⚡ Quick Wins (≤2시간, 체감 효과 ≥20%)
[Fast fixes worth immediate attention]

## Coverage Checklist ✅
| 영역 | 상태 |
|------|------|
| Critical Path | ${COVERAGE_CRITICAL_PATH} |
| Security Surface | ${COVERAGE_SECURITY} |
| Performance Impact | ${COVERAGE_PERFORMANCE} |
| Integration Points | ${COVERAGE_INTEGRATION} |
| 추가 Focus (${FOCUS_FLAGS}) | ${COVERAGE_FOCUS} |

## 상세 분석 (요청 시 자동 확장)
- 🌐 Security Assessment
- 🚀 Performance Analysis
- 🧱 Architecture Review
- 🧪 Code Quality & Tests

## ✅ Sign-Off & Follow-Up
- [ ] Production risks handled or accepted
- [ ] Charter questions answered
- [ ] Coverage checklist 전부 ✅ 확인
- [ ] Constitution & plan alignment 유지
- [x] Ready for /fin (HIGH 미해결 시 상태 파일로 차단)

다음 액션 옵션:
- CRITICAL 자동 수정 안내 (`Step 8`)
- 테스트 플랜 생성 (`--followup tests`)
- ADR/이슈 초안 작성 (`--followup docs`)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💡 스마트 필터 적용
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

숨겨진 LOW 임팩트 이슈: ${HIDDEN_COUNT}
(임팩트 점수 <15, 영향 사용자 <5%)

전체 목록 보기: `/ms.review --verbose`

> `--verbose` 또는 `--appendix all` 옵션으로 MEDIUM/LOW 전체 목록 및 통계 테이블을 함께 저장합니다.
```

When `--verbose` is passed, append the legacy severity sections (`MEDIUM ISSUES`, `LOW ISSUES`, `Positive Highlights`, `Metrics Summary`) after the high-impact sections and mark them as “Appendix”. Use the template below:

```markdown
### Appendix A — Medium Findings (Verbose)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 MEDIUM ISSUES (Consider Fixing)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

M-001: Magic Number in Token Expiration
  📍 Location: src/services/auth.service.ts:12
  📂 Category: Maintainability

  Issue: Hardcoded number without explanation
    const token = jwt.sign(payload, secret, { expiresIn: 900 });

  Recommendation: Extract to named constant
    const ACCESS_TOKEN_EXPIRY = 15 * 60; // 15 minutes
    const token = jwt.sign(payload, secret, { expiresIn: ACCESS_TOKEN_EXPIRY });

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

M-002: Inconsistent Error Handling
  📍 Location: src/services/payment.service.ts:34
  📂 Category: Unified

  Issue: Mixed error handling patterns
    - auth.service.ts uses custom AuthException
    - payment.service.ts uses generic Error

  Recommendation: Standardize using custom exceptions
    throw new PaymentException('Invalid card', PaymentErrorCode.INVALID_CARD);

... 추가 Medium 이슈는 위 포맷을 반복하며 H/M 식별자, 영향, 추천 조치를 명시합니다.

### Appendix B — Low Issues & Highlights (Verbose)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 LOW ISSUES (Nice to Have)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

L-001: Generic Variable Name ...
... 필요한 만큼 추가 Low 이슈를 동일 형식으로 나열합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 POSITIVE HIGHLIGHTS ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Excellent test coverage: 92% (exceeds 85% threshold)
✅ Clean architecture: Strict layer separation maintained
✅ Type safety: All functions have explicit return types
✅ Low code duplication: 3.2% (under 5% threshold)
✅ Consistent naming: Domain terms from spec.md used throughout
✅ Good error handling: Custom exceptions properly typed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 METRICS SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

│ Metric              │ Value  │ Threshold │ Status    │
├─────────────────────┼────────┼───────────┼───────────┤
│ Test Coverage       │ 92%    │ ≥85%      │ ✅ PASS   │
│ Avg Complexity      │ 6.2    │ ≤10       │ ✅ PASS   │
│ Max File Size       │ 432    │ ≤500      │ ✅ PASS   │
│ Code Duplication    │ 3.2%   │ ≤5%       │ ✅ PASS   │
│ Type Errors         │ 0      │ 0         │ ✅ PASS   │
│ Lint Warnings       │ 0      │ 0         │ ✅ PASS   │
│ Auth Coverage       │ 95%    │ 100%      │ ⚠️  WARN  │

Hidden LOW impact issues: ${HIDDEN_COUNT}
(Impact score <15, affecting <5% users)
```

**Write report to file**:
```bash
# Write the complete report to the file
cat > "$REPORT_FILE" << 'EOF'
[Complete report content as shown above]
EOF

echo "✅ Review report saved to: $REPORT_FILE"
```

**Format notes**:
- **Box drawing characters**: Use Unicode box drawing for clean tables
- **Emoji indicators**: 📍 location, 📂 category, ⚠️ warning, ✅ pass
- **Color via symbols**: 🔴 red (critical), 🟡 yellow (high/medium), 🟢 green (low)
- **Code blocks**: Use triple backticks for code examples
- **Severity headers**: Clear section breaks with ━━━ lines
- **Actionable**: Each issue includes concrete fix recommendation

---

### Step 8: Interactive Actions (NEW)

**Only if HIGH/CRITICAL issues exist:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🎯 QUICK ACTIONS AVAILABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2 HIGH issues can be auto-fixed:

Would you like me to:
1. Auto-fix H-001: N+1 Query (95% confidence)
2. Auto-fix H-002: Missing Auth Guard (100% confidence)
3. Fix both issues automatically
4. Continue without fixes (issues will be flagged in /fin)

Choice [1-4]: _
```

**If user chooses auto-fix (1, 2, or 3):**

```typescript
// For N+1 Query Fix
if (choice === '1' || choice === '3') {
  // Read the file containing the issue
  const filePath = 'src/services/user.service.ts';
  const content = await read(filePath);

  // Find the problematic N+1 query pattern
  const problemPattern = `
    for (const user of users) {
      user.posts = await this.postRepo.findByUserId(user.id);
    }
  `;

  // Generate fix based on ORM detected from plan.md
  let fix;
  if (plan.includes('typeorm') || plan.includes('TypeORM')) {
    fix = `const users = await this.userRepo.find({ relations: ['posts'] });`;
  } else if (plan.includes('sequelize') || plan.includes('Sequelize')) {
    fix = `const users = await this.userRepo.findAll({ include: ['posts'] });`;
  } else {
    // Generic fix for unknown ORM
    fix = `// TODO: Use eager loading to fetch posts with users in single query`;
  }

  // Apply the fix
  await edit(filePath, problemPattern, fix);

  console.log('✅ Fixed N+1 query pattern in ' + filePath);

  // Re-run specific check
  const recheck = await grep('await.*for.*of', 'src/services/user.service.ts');
  if (!recheck) {
    console.log('✅ Verification passed!');
  }
}

// For Auth Guard Fix
if (choice === '2' || choice === '3') {
  const content = await read('src/controllers/user.controller.ts');

  // Find method without guard
  const methodLine = '@Get(\'/users/:id\')';
  const guardLine = '@UseGuards(JwtAuthGuard)';

  // Insert guard before method
  const lines = content.split('\n');
  const methodIndex = lines.findIndex(l => l.includes(methodLine));
  lines.splice(methodIndex, 0, '  ' + guardLine);

  // Add import if missing
  if (!content.includes('JwtAuthGuard')) {
    lines.unshift(`import { JwtAuthGuard } from '../guards/jwt.guard';`);
  }

  await write('src/controllers/user.controller.ts', lines.join('\n'));

  console.log('✅ Added authentication guard');
}

if (choice !== '4') {
  console.log('\n🔄 Re-running review to verify fixes...\n');
  // Re-run review (simplified, just the fixed files)
  // Show updated score
}
```

**If user chooses continue (4):**
```
⚠️ Continuing with 2 HIGH issues unresolved

These issues will be flagged when you run /fin:
- H-001: N+1 Query Pattern
- H-002: Missing Authentication

You can fix them manually or re-run /ms.review later.
```

---

### Step 9: Cleanup and State Management

Remove analysis artifacts and save state for `/fin` integration:

```bash
# Remove temporary analysis files
rm -f .specify/review-*.json

# Save state for /fin integration (NEW)
if [ $HIGH_COUNT -gt 0 ]; then
  echo "$HIGH_COUNT HIGH issues unresolved" > .specify/review-state.txt
  echo "Run /ms.review to check" >> .specify/review-state.txt
  echo "Review report: $REPORT_FILE" >> .specify/review-state.txt
fi
```

**Keep warnings in memory**: Store HIGH/CRITICAL issues for `/fin` command to check

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

## Performance Optimization

**Parallel execution** where possible:
- Run `jscpd`, `eslint`, `radon` in parallel (not sequential)
- Run ripgrep searches in parallel
- Read multiple files concurrently

**Caching**:
- Cache spec.md domain terms for entire session
- Cache plan.md architecture structure
- Reuse complexity analysis results if files unchanged

**Smart skipping**:
- Skip test quality review if no tests/ directory
- Skip Python checks if no .py files found
- Skip duplication check if project <5 files

**Expected runtime**:
- Small project (<20 files): ~10 seconds
- Medium project (20-100 files): ~30 seconds
- Large project (>100 files): ~60 seconds

---

## Notes

- **Complements /ms.analyze**: Does NOT duplicate TRUST validation
- **Post-implementation**: Only runs after code is written
- **Console AND file output**: Saves to `docs/review/review_[AGENT]_[timestamp].md` (NEW)
- **Actionable feedback**: Every issue includes fix recommendation + code example
- **Context-aware**: Uses spec.md and plan.md for intelligent analysis
- **Flexible**: Can skip slow checks or focus on specific categories
- **Integration**: Works with /fin workflow for gating commits
- **Enhanced with**:
  - ultrathink pattern analysis for systemic issues (NEW)
  - Impact-based filtering to reduce noise (NEW)
  - Interactive auto-fix suggestions (NEW)

---

## Enhancement Summary (NEW)

This enhanced version adds three key improvements from Dev-Kit philosophy:

### 1. Pattern Analysis (Step 5.5)
- **ultrathink** activation for deep pattern recognition
- Identifies systemic issues across multiple files
- Provides root cause analysis using 5-Why method
- Suggests prevention strategies and automation opportunities
- Groups issues for batch fixing with ROI calculation

### 2. Smart Filtering (Step 6)
- Calculates impact score for LOW severity issues
- Hides low-impact issues (score <15) from main report
- Promotes high-impact LOW issues to MEDIUM
- Reduces noise by ~50% while preserving important findings
- `--verbose` flag to see all issues when needed

### 3. Interactive Actions (Step 8)
- Offers auto-fix for HIGH confidence issues
- Supports common fixes: N+1 queries, missing auth guards
- Re-runs verification after applying fixes
- Integrates with `/fin` workflow via state file
- `--no-interactive` flag for CI/CD pipelines

### 4. Report Persistence (Step 7)
- Saves review report to `docs/review/` directory
- Filename includes AI agent name and timestamp
- Enables review history tracking and comparison
- Report path saved in state file for `/fin` reference

All enhancements maintain backward compatibility and can be disabled with flags.

---

## Implementation Details

**Tools Required**:
- `ripgrep` (rg) - Pattern matching
- `jscpd` (optional) - Code duplication (JavaScript/TypeScript)
- `eslint` (optional) - Complexity analysis (JavaScript/TypeScript)
- `radon` (optional) - Complexity analysis (Python)
- `pylint` (optional) - Duplication analysis (Python)

**Libraries**:
- `src/lib/review/naming.ts` - Naming quality analyzer
- `src/lib/review/architecture.ts` - Architecture consistency checker
- `src/lib/review/performance.ts` - Performance issue detector
- `src/lib/review/security.ts` - Security deep-dive analyzer
- `src/lib/review/tests.ts` - Test quality reviewer
- `src/lib/review/reporter.ts` - Console report formatter

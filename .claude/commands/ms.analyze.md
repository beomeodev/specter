---
description: "Document consistency + TRUST validation (2-step process)"
---

# /ms.analyze - Spec-Kit + TRUST Comprehensive Validation

**Wrapper command** that adds My-Spec's TRUST validation on top of Spec-Kit's document consistency checks.

## Overview

This command is a **wrapper** that enhances `/speckit.analyze` with TRUST code-level validation.

**Pipeline**:
```
┌─────────────────────────────────────────────────────────────┐
│ /ms.analyze = /speckit.analyze + TRUST 3-Level Validation  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: Spec-Kit Foundation (via /speckit.analyze)        │
│  ├─ Document consistency (spec↔plan↔tasks)                  │
│  ├─ Constitution alignment                                   │
│  ├─ Coverage gaps, ambiguity, duplication                    │
│  └─ EXIT if CRITICAL issues found                           │
│                                                              │
│  Step 2: My-Spec Enhancement (TRUST Validation)            │
│  ├─ Level 1: Structure (tests/, .gitignore, file sizes)     │
│  ├─ Level 2: Quality (tests run, lint, typecheck)           │
│  ├─ Level 3: Deep (coverage, complexity, security, TAGs)    │
│  └─ EXIT if CRITICAL issues found (at each level)           │
│                                                              │
│  Step 3: Unified Report                                     │
│  └─ Merge both analyses into single comprehensive report    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Difference from `/speckit.analyze`**:
- `/speckit.analyze`: Document-level analysis (WHAT to build correctly)
- `/ms.analyze`: Code-level validation (HOW to build with quality)

**Execution Modes**:

-   **Strict Mode** (default): CRITICAL violations block immediately
-   **Report Mode** (`--report`): Run all levels, report all issues at once

## Execution Steps

### Step 1: Spec-Kit Foundation (Document Consistency & Drift Detection)

Execute `/speckit.analyze` for comprehensive document analysis, followed by **Cross-Document Drift Detection**:

```bash
/speckit.analyze
```

**Cross-Document Drift Detection (MANDATORY)**:
1. **Migration Consistency**: Verify that `spec.md`, `plan.md`, and `tasks.md` all reference the same migration file names (e.g., `0021_...` vs `0019_...`).
2. **File Path Integrity**: Check if every file path mentioned in any document exists in the workspace.
3. **FR ↔ TAG Mapping**: Ensure all functional requirements in `spec.md` are covered by at least one `@TEST` tag in `tasks.md`.
4. **Amendment Integrity**: Verify that any FR marked as `SUPERSEDED` has a corresponding `Amendment` block at the end of the document.

**IF DRIFT DETECTED**:
- ❌ **Auto-fixable** (migration index, path drift): Correct the documents automatically.
- ❌ **Inconsistency** (missing amendment, missing FR mapping): **ABORT** and report in KOREAN.

This validates **(Spec-Kit scope)**:
- ✅ All spec.md functional requirements (FR) have corresponding tasks
- ✅ No orphaned tasks (tasks without spec requirements)
- ✅ Task descriptions accurately reflect spec requirements
- ✅ Constitution alignment (all sections, including Section IX project constraints)
- ✅ No ambiguity, duplication, underspecification
- ✅ Implementation order follows dependencies

**IF CRITICAL ISSUES FOUND**:

```
❌ /speckit.analyze Failed

CRITICAL issues detected:
- Constitution violation: Missing test coverage requirement in plan.md
- Coverage gap: FR-3 (Password reset) has no tasks
- Ambiguity: "fast response" in NFR-5 not measurable

BLOCKING: Cannot proceed to TRUST validation until resolved.

Fix these issues:
1. Add tasks for FR-3 in tasks.md
2. Define "fast" as "< 200ms p95" in spec.md
3. Update plan.md to include test coverage strategy
4. Run /ms.analyze again to verify
```

**EXIT**: Code 1 (cannot proceed to TRUST validation)

**IF PASSED**:

```
✅ /speckit.analyze PASSED

Document Consistency: ✅
- All requirements covered
- Constitution aligned
- Zero ambiguities
- Zero coverage gaps

Proceeding to TRUST code-level validation...
```

Proceed to Step 1.5 (My-Spec TRUST validation)

### Step 1.5: Adaptive TRUST Analysis (Quantitative Decision)

**This is My-Spec's enhancement** - adds code-level quality validation on top of Spec-Kit's document analysis.

**Step 1: Measure Project Size (Mandatory)**

```bash
# Count source lines of code (exclude comments, blanks)
TOTAL_SLOC=$(find src/ -name "*.ts" -o -name "*.py" -o -name "*.js" 2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')

# Count source files
FILE_COUNT=$(find src/ -name "*.ts" -o -name "*.py" -o -name "*.js" 2>/dev/null | wc -l)

# Check for --report flag
REPORT_MODE=$(echo "$ARGUMENTS" | grep -c "\-\-report")
```

**Step 2: Apply Decision Tree**

Execute in priority order (stop at first match):

```
┌─────────────────────────────────────────────────────────────┐
│ DECISION TREE (Priority Order)                              │
├─────────────────────────────────────────────────────────────┤
│ 1. IF REPORT_MODE = 1                                       │
│    → COMPLEX (all 3 agents in parallel)                    │
│                                                              │
│ 2. IF TOTAL_SLOC < 500 OR FILE_COUNT < 10                   │
│    → SIMPLE (sequential TRUST, current behavior)            │
│                                                              │
│ 3. IF TOTAL_SLOC < 2000 OR FILE_COUNT < 50                  │
│    → MODERATE (2 agents)                                     │
│                                                              │
│ 4. IF TOTAL_SLOC ≥ 2000 OR FILE_COUNT ≥ 50                  │
│    → COMPLEX (3 agents)                                      │
│                                                              │
│ 5. FALLBACK (unable to measure)                             │
│    → SIMPLE (safe default, sequential)                      │
└─────────────────────────────────────────────────────────────┘
```

**Step 3: Execute Sub-Agent Strategy**

Based on complexity determined above:

**IF SIMPLE**:
  - 0 sub-agents → Sequential TRUST validation (current behavior)
  - Proceed directly to Step 2

**IF MODERATE**:
  - Launch 2 sub-agents in PARALLEL:
    1. **trust-validator agent (level 2)**:
       ```
       "Run TRUST Level 1 and Level 2 checks"
       ```

    2. **tag-auditor agent**:
       ```
       "Validate TAG integrity across project"
       ```

**IF COMPLEX**:
  - Launch 3 sub-agents in PARALLEL:
    1. **trust-validator agent (level 1)**:
       ```
       "Run TRUST Level 1 structure checks"
       ```

    2. **trust-validator agent (level 2)**:
       ```
       "Run TRUST Level 2 quality checks"
       ```

    3. **trust-validator agent (level 3)**:
       ```
       "Run TRUST Level 3 deep analysis"

       Note: Level 3 includes TAG validation, but can run tag-auditor separately for detailed TAG report
       ```

**CRITICAL**: Always launch agents in PARALLEL (single message with multiple Task calls).

**Debug Output** (for transparency):
```json
{
  "complexity_metrics": {
    "total_sloc": 1500,
    "file_count": 35,
    "report_mode": false
  },
  "decision": "MODERATE",
  "reason": "Rule 3: TOTAL_SLOC < 2000",
  "agents_spawned": 2
}
```

### Step 1.6: Synthesize TRUST Results

**IF sub-agents launched**:
- Merge violations from all agents
- Sort by severity (CRITICAL → HIGH → MEDIUM → LOW)
- Count violations per level
- Determine if implementation is blocked (any CRITICAL found)
- Generate unified TRUST report

**ELSE**:
- Use sequential execution results

### Step 2: TRUST Validation (3 Levels)

**Only runs if Step 1 (document consistency) passed.**

**IF sub-agents were launched (Step 1.5)**:
- Use synthesized results from Step 1.6
- Skip sequential execution
- Display unified report

**ELSE** (Simple path - sequential execution):

#### Level 1: Structure Checks

**Checks**:

-   ✅ `tests/` directory exists (CRITICAL)
-   ✅ `.env` in `.gitignore` (CRITICAL)
-   ✅ Files ≤500 SLOC (MEDIUM - code files only, docs excluded)

**Execution** (Strict Mode):

```
⚙️ Level 1: Structure Checks

  Checking tests/ directory... ✅
  Checking .gitignore... ✅
  Checking file sizes... ⚙️ (elapsed: 2s)
```

-   **IF CRITICAL violation found**: TERMINATE immediately, display violations, provide fix commands
-   **IF passed**: Proceed to Level 2
-   **No timeout** - runs to completion

#### Level 2: Quality Checks

**Project Type Detection**:

```bash
detect_project_type() {
  [ -f "package.json" ] && echo "typescript" && return
  [ -f "pyproject.toml" ] || [ -f "requirements.txt" ] && echo "python" && return
  [ -f "go.mod" ] && echo "go" && return
  [ -f "Cargo.toml" ] && echo "rust" && return
  echo "unknown"
}
```

**Checks**:

-   ✅ Tests run successfully (CRITICAL)
-   ✅ Linting passes with zero warnings (CRITICAL)
-   ✅ Type checking passes (CRITICAL)

**Execution** (Strict Mode):

```
⚙️ Level 2: Quality Checks

  Running tests... (elapsed: 15s)
  ✅ Tests passed (47 seconds)

  Running linter... (elapsed: 2s)
  ✅ Linting passed

  Running type checker... (elapsed: 8s)
  ✅ Type checking passed
```

-   **Only runs if Level 1 passed**
-   **IF CRITICAL violation found**: TERMINATE, display violations, provide fix commands
-   **IF passed**: Proceed to Level 3
-   **No timeout** - runs to completion with progress display

**Project Type Detection Failure**:

```
⚠️ MEDIUM: Project type could not be detected

No language-specific config found:
- package.json (TypeScript/JavaScript)
- pyproject.toml or requirements.txt (Python)
- go.mod (Go)
- Cargo.toml (Rust)

Skipping Level 2 quality checks (tests, linting, type checking).
Proceeding to Level 3 (TAG integrity).
```

#### Level 3: Deep Analysis

**Checks**:

-   ✅ Coverage ≥85% (HIGH - warning only)
-   ✅ Complexity ≤10 per function (HIGH - warning only)
-   ✅ Security scan passes (MEDIUM - advisory)
-   ✅ TAG integrity (CRITICAL for orphans/duplicates, HIGH/MEDIUM for broken chains)

**TAG Integrity**:

```bash
validate_tag_integrity() {
  # Find all @SPEC, @TEST, @CODE tags
  rg '@(SPEC|TEST|CODE):[A-Z0-9]+-[0-9]{3}' -oN src tests | sort -u > .specify/tags.txt

  # Check for orphaned TAGs (no corresponding files)
  # Check for duplicate TAG IDs
  # Check for broken SPEC→TEST→CODE chains
}
```

**Execution** (Strict Mode):

```
⚙️ Level 3: Deep Analysis

  Scanning TAGs... (elapsed: 5s)
  ✅ TAG scan completed (12 seconds)

  Calculating coverage... (elapsed: 20s)
  ⚠️ Coverage: 78% (target: 85%)
```

-   **Only runs if Level 2 passed**
-   **HIGH/MEDIUM/LOW violations**: Display warnings, continue
-   **No timeout** - runs to completion with progress display

### Step 3: Generate Unified Report

Merge findings from both analyses:

```
┌─────────────────────────────────────────────────────────────┐
│ /ms.analyze - Comprehensive Quality Report                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ✅ Spec-Kit Analysis (Document Consistency)                │
│    - All requirements covered                               │
│    - Constitution aligned                                   │
│    - Zero ambiguities                                       │
│    - Zero coverage gaps                                     │
│                                                              │
│ ✅ TRUST Validation (Code Quality)                         │
│    - Level 1: Structure ✅                                  │
│    - Level 2: Quality ✅                                    │
│    - Level 3: Deep ⚠️ (2 HIGH warnings)                    │
│                                                              │
│ Implementation: ✅ ALLOWED                                  │
│                                                              │
│ ⚠️ High Priority Issues:                                   │
│ • Coverage 78% < 85% (add tests)                            │
│ • Function complexity 12 > 10 (refactor auth.ts:45)         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: Report Output

Display summary (KOREAN ONLY - Issue 8.1, 8.2):

```json
{
    "document_consistency": "PASSED",
    "drift_detected": "NONE",
    "trust_level": 3,
    "progress": "75%",
    "next_step": "/ms.implement"
}
```

Display to user:

```
┌─────────────────────────────────────────────────────────────┐
│ /ms.analyze - 종합 품질 리포트 (Comprehensive Quality Report) │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ✅ Spec-Kit 분석 (문서 일관성 및 Drift 탐지)                 │
│    - 요구사항 커버리지: 100%                                 │
│    - 문서 간 Drift: 없음 (spec ↔ plan ↔ tasks 일치)          │
│    - 파일 경로 검증: 모두 실재함                             │
│                                                              │
│ ✅ TRUST 검증 (코드 품질)                                    │
│    - Level 1: 구조 (Structure) ✅                            │
│    - Level 2: 품질 (Quality - Lint, Type, Tests) ✅           │
│    - Level 3: 심층 분석 (Deep - Coverage, TAG) ⚠️            │
│                                                              │
│ 구현 진행 가능 여부: ✅ 허용 (ALLOWED)                        │
│                                                              │
│ ⚠️ 주요 경고 사항:                                           │
│ • 테스트 커버리지 78% < 85% (테스트 추가 필요)                │
│ • 함수 복잡도 12 > 10 (auth.ts:45 리팩토링 권장)              │
│                                                              │
└─────────────────────────────────────────────────────────────┘

🎯 다음 단계:
👉 /ms.implement (태스크 구현 시작)
👉 /ms.review (상세 코드 리뷰 실행)
```

## TRUST Principles

See [Constitution Section V](../../.specify/memory/constitution.md) for detailed TRUST principles.

**Validation Coverage:**
- **T** - Test-First: Coverage ≥85%, tests run successfully
- **R** - Readable: File ≤500 SLOC, Function ≤100 LOC, Complexity ≤10
- **U** - Unified: Strict typing
- **S** - Secured: Input validation, `.env` in `.gitignore`
- **T** - Trackable: 100% TAG integrity

## Progressive Execution Rules

```
Level 1 (Structure)
  ↓
  IF CRITICAL → TERMINATE with fix instructions
  ↓
Level 2 (Quality)
  ↓
  IF CRITICAL → TERMINATE with fix instructions
  ↓
Level 3 (Deep)
  ↓
  HIGH/MEDIUM/LOW → Display warnings, continue
```

## Advanced Features

### Report Mode

Run all levels without early termination, then display comprehensive report:

```bash
/ms.analyze --report
```

**Behavior**:

-   Continue through all levels even if CRITICAL violations found
-   Collect all issues from Level 1, 2, and 3
-   Display comprehensive report at end

**Example**:

```
⚙️ Step 2: TRUST Validation (Report Mode)

  Level 1: Structure Checks...
    ❌ CRITICAL: tests/ directory not found
    ❌ CRITICAL: .env not in .gitignore

  Level 2: Quality Checks... (continuing despite Level 1 failures)
    ❌ CRITICAL: Linting failed with 5 warnings
    ✅ Type checking passed

  Level 3: Deep Analysis... (continuing)
    ⚠️ HIGH: Coverage 78% < 85%
    ⚠️ HIGH: Function complexity 12 > 10
    ✅ Security scan passed

┌─────────────────────────────────────────────┐
│ TRUST Validation Report (All Levels)        │
├─────────────────────────────────────────────┤
│ CRITICAL: 3 (Level 1: 2, Level 2: 1)        │
│ HIGH:     2 (Level 3)                       │
│ MEDIUM:   0                                 │
│ Implementation: ❌ NOT ALLOWED              │
└─────────────────────────────────────────────┘

Fix all CRITICAL issues:
1. mkdir tests
2. echo ".env" >> .gitignore
3. npm run lint --fix

Then re-run /ms.analyze (strict mode) to verify.
```

**Use Case**: See all problems at once to fix in one go

### Warning Tracking System

HIGH warnings are tracked in `.specify/warnings.log`:

**After `/ms.analyze` with HIGH warnings**:

```bash
# .specify/warnings.log created
cat .specify/warnings.log
```

**Content**:

```
# TRUST Validation Warnings
# Generated: 2025-10-10 14:30:00

HIGH: Coverage 78% < 85% (target: 85%)
HIGH: Function complexity 12 > 10 in src/auth.ts:45

Medium:
MEDIUM: Large file src/utils.ts: 350 SLOC (limit: 300)
```

**When running `/ms.implement`**:

```
⚠️ You have 2 HIGH warnings from /ms.analyze:
- Coverage 78% < 85%
- Function complexity 12 > 10

Proceed anyway? (y/N)
```

**Prevents warning fatigue**: Users must acknowledge warnings before proceeding

### User Control Options

Skip slow checks when needed:

```bash
/ms.analyze --skip-tests      # Skip Level 2 test execution
/ms.analyze --skip-coverage   # Skip Level 3 coverage
/ms.analyze --fast            # Skip both tests and coverage
```

**Use Case**: Quick validation during development

## Error Handling

### Error 1: Spec-Kit Analysis Failed (Document Level)

**Symptom**: `/speckit.analyze` detected CRITICAL issues

**Message**:
```
❌ /speckit.analyze Failed

CRITICAL issues detected:
- Constitution violation: Missing test coverage requirement in plan.md
- Coverage gap: FR-3 (Password reset) has no tasks
- Ambiguity: "fast response" in NFR-5 not measurable

BLOCKING: Cannot proceed to TRUST validation until resolved.

Fix these issues:
1. Add tasks for FR-3 in tasks.md
2. Define "fast" as "< 200ms p95" in spec.md
3. Update plan.md to include test coverage strategy
4. Run /ms.analyze again to verify
```

**Action**: Fix document-level issues, then retry `/ms.analyze`

---

### Error 2: TRUST Level 1 Failed (Structure)

**Symptom**: `/speckit.analyze` passed, but structure checks failed

**Message**:
```
✅ Spec-Kit Analysis: PASSED
❌ TRUST Level 1: FAILED

CRITICAL issues:
- tests/ directory missing
- .env not in .gitignore

Fix:
1. mkdir tests
2. echo ".env" >> .gitignore
3. Re-run /ms.analyze
```

**Action**: Fix structure, then retry `/ms.analyze`

---

### Error 3: TRUST Level 2 Failed (Quality)

**Symptom**: Structure passed, but quality checks failed

**Message**:
```
✅ Spec-Kit Analysis: PASSED
✅ TRUST Level 1: PASSED
❌ TRUST Level 2: FAILED

CRITICAL issues:
- Linting failed with 5 warnings
- Type checking failed with 3 errors

Fix:
1. npm run lint --fix
2. Fix type errors in src/auth.ts:45, src/user.ts:120
3. Re-run /ms.analyze
```

**Action**: Fix quality issues, then retry `/ms.analyze`

---

### Error 4: Project Type Not Detected

**Symptom**: Cannot determine language for Level 2 checks

**Message**:
```
⚠️ MEDIUM: Project type could not be detected

No language-specific config found:
- package.json (TypeScript/JavaScript)
- pyproject.toml or requirements.txt (Python)
- go.mod (Go)
- Cargo.toml (Rust)

Skipping Level 2 quality checks (tests, linting, type checking).
Proceeding to Level 3 (TAG integrity, coverage, security).
```

**Action**: Acceptable - continues to Level 3

## Next Steps

**If both Spec-Kit and TRUST pass**:

1. ✅ Run `/ms.implement` to start implementation (auto-selects first pending TAG)
2. All quality gates are green ✅

**If Spec-Kit analysis fails**:

1. Fix document-level issues (spec.md, plan.md, tasks.md)
2. Address Constitution violations
3. Resolve coverage gaps, ambiguities, duplications
4. Re-run `/ms.analyze` to verify fixes
5. **Cannot proceed to TRUST validation** until Spec-Kit passes

**If TRUST validation has CRITICAL violations**:

1. Fix violations using provided commands
2. Re-run `/ms.analyze` to verify fixes
3. **Cannot proceed to `/ms.implement`** until all CRITICAL issues resolved

## Relationship to Other Commands

**Command Hierarchy**:
```
/speckit.analyze  (Foundation - Document level)
    ↓
/ms.analyze       (Wrapper - Document + Code level)
    ↓
/ms.implement     (Execution - Implementation with TAGs)
```

**When to use each**:
- `/speckit.analyze` only: Quick document consistency check (before `/ms.analyze`)
- `/ms.analyze`: Full validation before implementation (recommended)
- `/ms.implement`: After `/ms.analyze` passes

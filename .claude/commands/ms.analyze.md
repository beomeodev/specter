---
description: "Document consistency + TRUST validation (2-step process)"
---

# /ms.analyze - Document Consistency + TRUST Validation

Validates that tasks match spec requirements, then performs progressive 3-level TRUST quality checks.

## Overview

This command performs a **2-step validation process**:

**Step 1: Document Consistency** (via `/speckit.analyze`)

-   Validates tasks.md faithfully implements all spec.md requirements
-   Checks for missing requirements, inconsistencies, orphaned tasks
-   **BLOCKS if inconsistencies found**

**Step 2: TRUST 3-Level Validation** (My-Spec addition)

-   **Level 1**: Structure checks - BLOCKS if CRITICAL
-   **Level 2**: Quality checks - BLOCKS if CRITICAL
-   **Level 3**: Deep analysis - WARNS only

**Execution Modes**:

-   **Strict Mode** (default): CRITICAL violations block immediately
-   **Report Mode** (`--report`): Run all levels, report all issues at once

## Execution Steps

### Step 0: Load Project Context

**Auto-load project documents**:
- `.specify/memory/constitution.md` (Constitution - REQUIRED)
- `AGENTS.md` (AI instructions, coding standards - if exists)
- `specs/[spec-id]/spec.md` (Feature specification - REQUIRED)
- `specs/[spec-id]/tasks.md` (Task list - REQUIRED)

**IF Constitution, spec.md, or tasks.md missing**:
- Display error: "Required files missing. Run `/ms.init`, `/ms.specify`, and `/ms.tasks` first."
- Exit

**Reference for analysis**:
- Constitution Section II (Simplicity-First - file size limits: ≤500 SLOC)
- Constitution Section V (TRUST Principles - test coverage ≥85%, security, readability)
- Constitution Section IX (Project-specific constraints - **if exists**, added by `/ms.constitution`)
- AGENTS.md (coding standards, complexity limits ≤10 - if exists)

**These documents guide TRUST validation to apply project-specific rules.**

### Step 1: Document Consistency Check

Execute `/speckit.analyze` for spec-tasks consistency:

```
/speckit.analyze
```

This validates:

-   All spec.md functional requirements (FR) have corresponding tasks
-   No orphaned tasks (tasks without spec requirements)
-   Task descriptions accurately reflect spec requirements
-   Implementation order follows dependencies

**IF INCONSISTENCIES FOUND**:

```
❌ Document Consistency Failed

Tasks.md does not fully implement spec.md requirements.

Missing requirements:
- FR-3: Password reset functionality
- FR-7: Rate limiting

Orphaned tasks:
- T023: Add Redis caching (no corresponding FR)

Please update tasks.md and re-run /ms.analyze
```

**EXIT**: Code 1 (cannot proceed to TRUST validation)

**IF CONSISTENT**: Display success and proceed to Step 1.5

### Step 1.5: Adaptive TRUST Analysis (Quantitative Decision)

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

### Step 3: Summarize Results

```
┌─────────────────────────────────────────────┐
│ TRUST Validation Report                     │
├─────────────────────────────────────────────┤
│ Level Reached: 3/3                          │
│ Implementation: ✅ ALLOWED                  │
├─────────────────────────────────────────────┤
│ CRITICAL: 0                                 │
│ HIGH:     2 ⚠️                              │
│ MEDIUM:   3 ℹ️                              │
│ LOW:      1 ℹ️                              │
├─────────────────────────────────────────────┤
│ High Priority Issues:                       │
│ • Coverage 78% < 85% (add tests)            │
│ • Function complexity 12 > 10 (refactor)    │
└─────────────────────────────────────────────┘
```

### Step 4: Report Output

```json
{
    "document_consistency": "passed",
    "trust_level_reached": 3,
    "violations": [
        {
            "level": 3,
            "severity": "HIGH",
            "category": "Test-First",
            "message": "Coverage 78% is below 85%",
            "fix": "Add tests to increase coverage"
        }
    ],
    "blocked": false,
    "summary": {
        "CRITICAL": 0,
        "HIGH": 2,
        "MEDIUM": 3,
        "LOW": 1
    }
}
```

**Display to user**:

```
✅ Document Consistency: PASSED
   All spec.md requirements reflected in tasks.md

✅ TRUST Validation: LEVEL 3 REACHED
   Implementation: ALLOWED

┌─────────────────────────────────────────────┐
│ TRUST Validation Report                     │
├─────────────────────────────────────────────┤
│ Level Reached: 3/3                          │
│ Implementation: ✅ ALLOWED                  │
├─────────────────────────────────────────────┤
│ CRITICAL: 0                                 │
│ HIGH:     2 ⚠️                              │
│ MEDIUM:   3 ℹ️                              │
│ LOW:      1 ℹ️                              │
├─────────────────────────────────────────────┤
│ High Priority Issues:                       │
│ • Coverage 78% < 85% (add tests)            │
│ • Function complexity 12 > 10 (refactor)    │
└─────────────────────────────────────────────┘

🎯 Next Step: /ms.implement (to start implementation with TAG auto-selection)
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

-   **LEVEL1_CRITICAL**: Structure violations found

    -   Example: "tests/ directory missing"
    -   Fix: `mkdir tests`

-   **LEVEL2_CRITICAL**: Quality violations found

    -   Example: "Linting failed with 5 warnings"
    -   Fix: `npm run lint --fix`

-   **LEVEL3_WARNINGS**: Deep analysis issues

    -   Example: "Coverage 78% < 85%"
    -   Suggestion: "Add tests for uncovered code"

-   **PROJECT_TYPE_NOT_DETECTED**: Cannot determine language
    -   Severity: MEDIUM
    -   Action: Skip Level 2, continue to Level 3

## Next Steps

**If both Step 1 and Step 2 pass**:

1. Run `/ms.implement` to start implementation (auto-selects first pending TAG)
2. All quality gates are green ✅

**If Step 1 (document consistency) fails**:

1. Update tasks.md to include missing spec requirements
2. Remove orphaned tasks
3. Re-run `/ms.analyze` to verify fixes
4. Cannot proceed until spec-tasks consistency achieved

**If Step 2 (TRUST validation) has CRITICAL violations**:

1. Fix violations using provided commands
2. Re-run `/ms.analyze` to verify fixes
3. Cannot proceed to `/ms.implement` until CRITICAL issues resolved

## Notes

-   **2-step process**: Document consistency FIRST, then TRUST validation
-   **Step 1 is mandatory**: Must pass before TRUST validation runs
-   **Progressive execution**: TRUST levels only run if earlier levels pass (strict mode)
-   **No timeouts**: Runs to completion with progress display every 5 seconds
-   **Execution modes**: Strict (default, early termination) or Report (see all issues)
-   **Blocking behavior**: CRITICAL = cannot proceed, HIGH/MEDIUM = warnings only
-   **Fix guidance**: Each violation includes specific fix command
-   **Warning tracking**: HIGH warnings logged to `.specify/warnings.log`
-   **TAG integrity**: Critical for traceability, enforced in TRUST Level 3
-   **User control**: `--skip-tests`, `--skip-coverage`, `--fast` options available

## Implementation Details

**Tools**: SlashCommand (/speckit.analyze), Bash (tests, linting, type checking, ripgrep)

# Code Review Optimization Design Document

**Version**: 2.0.0
**Date**: 2025-10-17
**Status**: Draft
**Target**: ms.review.md workflow optimization

---

## Executive Summary

### Current Performance Baseline
- Small PR (5 files): ~30s
- Medium PR (20 files): ~60s
- Large PR (100 files): ~120s
- Re-run (no cache): ~60s

### Target Performance (Post-Optimization)
- Small PR: **8s** (73% ↓)
- Medium PR: **18s** (70% ↓)
- Large PR: **45s** (62% ↓)
- Re-run (with cache): **12s** (80% ↓)

### Core Optimization Strategy
1. **Scope Reduction**: Changed files priority (60% improvement)
2. **I/O Minimization**: Single-pass scanning (30% improvement)
3. **Parallelization**: Concurrent execution (40% improvement)
4. **Smart Caching**: Hash-based skip logic (50% on re-run)

---

## Architecture Overview

### Current Workflow (Sequential)
```
Step 2: Context Loading (10s)
   ↓
Step 3: File Discovery (5s)
   ↓
Step 4: Static Analysis (20s)
   ↓ A: jscpd (8s)
   ↓ B: eslint/radon (7s)
   ↓ C: ripgrep x10 (5s)
   ↓
Step 5: AI Analysis (20s)
   ↓ A-G: Sequential checks
   ↓
Step 5.5: ultrathink (5s)
   ↓
Step 7: Report (2s)
────────────────────
Total: ~60s
```

### Optimized Workflow (Parallel + Smart)
```
Step 1: Git Diff Analysis (1s)
   ↓ CHANGED_FILES detection
   ↓
Step 2: Parallel Initialization
   ├─→ (A) Context Loading + Caching (10s) ───┐
   └─→ (B) Hash Cache Check (2s)              │
       ↓ Filter unchanged files               │
       Step 3: Parallel Static Analysis       │
       ├─→ jscpd (suspect files only, 2s) ────┤
       ├─→ eslint --cache (3s) ────────────────┤
       ├─→ radon -P nproc (2s) ────────────────┤
       └─→ ripgrep (consolidated, 1s) ─────────┤
                                               ↓
Step 4: AI Analysis (selective, 8s) ←─────────┘
   ↓ Real-time pattern aggregation
   ↓
Step 5: Report Generation (1s)
────────────────────────
Total: ~18s (Medium PR)
```

---

## Phase 1: Quick Wins (60-70% improvement)

### 1.1 Changed Files Priority Strategy

**Current Problem:**
```bash
# Scans ALL files in project
find src/ -type f \( -name "*.ts" -o -name "*.js" -o -name "*.py" \)
# Result: 500+ files for analysis
```

**Optimization:**
```bash
# Step 3: Smart File Discovery
discover_changed_files() {
  local BASE_REF="${1:-origin/main}"

  # Priority 1: Git diff (PR context)
  CHANGED_FILES=$(git diff --name-only --diff-filter=ACMRTUXB ${BASE_REF}...HEAD 2>/dev/null \
    | rg '^(src|tests)/.*\.(ts|js|py)$' || true)

  # Priority 2: Staged files (pre-commit context)
  if [ -z "$CHANGED_FILES" ]; then
    CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACMRTUXB \
      | rg '^(src|tests)/.*\.(ts|js|py)$' || true)
  fi

  # Priority 3: Smoke test (no git context)
  if [ -z "$CHANGED_FILES" ]; then
    CHANGED_FILES=$(rg -l '' src tests 2>/dev/null \
      | rg '\.(ts|js|py)$' \
      | head -n 200)
  fi

  echo "$CHANGED_FILES"
}

# Export for all subsequent steps
export CHANGED_FILES=$(discover_changed_files "${BASE_REF:-origin/main}")
export CHANGED_COUNT=$(echo "$CHANGED_FILES" | wc -l)

echo "📊 Analysis scope: $CHANGED_COUNT files (changed from ${BASE_REF:-origin/main})"
```

**Benefits:**
- ✅ 500 files → 10 files (98% reduction in typical PR)
- ✅ All downstream tools (eslint, radon, ripgrep) process less
- ✅ No semantic change (full scan still available for edge cases)

**Risk Mitigation:**
- Fallback to full scan when CHANGED_FILES is empty
- Option to force full scan: `FORCE_FULL_SCAN=1 /ms.review`

---

### 1.2 Single-Pass Ripgrep Consolidation

**Current Problem:**
```bash
# Step 4.C: Multiple ripgrep invocations
rg "process\.env\." src/ --json > env.json         # Call 1
rg "eval\(" src/ --json > eval.json                # Call 2
rg "console\.log" src/ --json > console.json       # Call 3
rg "await.*for.*of" src/ --json > async.json       # Call 4
# ... 6 more calls
# Total: 10 process spawns + 10 disk I/O cycles
```

**Optimization:**
```bash
# Step 4.C: Consolidated Pattern Detection
run_consolidated_ripgrep() {
  local targets="${CHANGED_FILES:-src tests}"

  rg --json -n --no-heading --line-number \
    -e 'eval\(' \
    -e '(console\.(log|debug|info|warn))' \
    -e '(process\.env\.|os\.getenv|import\.meta\.env)' \
    -e 'await.*for.*of' \
    -e '\.map\(.*await' \
    -e 'for.*for.*for' \
    -e '\b[0-9]{3,}\b(?!px|ms|rem)' \
    -e '(TODO|FIXME|XXX|HACK|BUG):' \
    -e '(password|secret|token|api[_-]?key)\s*=\s*["\']' \
    -e '(setTimeout|setInterval)\(' \
    --type-add 'code:*.{ts,js,py}' \
    --type code \
    --iglob '!**/*.snap' \
    --iglob '!**/*.min.js' \
    --iglob '!**/fixtures/**' \
    --iglob '!**/mocks/**' \
    $targets \
    > .specify/review-rg.ndjson 2>/dev/null || true

  # Post-process: categorize patterns
  jq -r 'select(.type == "match") |
    {
      file: .data.path.text,
      line: .data.line_number,
      match: .data.lines.text,
      pattern: (
        if (.data.lines.text | test("eval\\(")) then "dangerous-eval"
        elif (.data.lines.text | test("console\\.")) then "console-log"
        elif (.data.lines.text | test("process\\.env")) then "env-access"
        elif (.data.lines.text | test("await.*for")) then "async-perf"
        elif (.data.lines.text | test("for.*for")) then "nested-loop"
        elif (.data.lines.text | test("\\b[0-9]{3,}\\b")) then "magic-number"
        elif (.data.lines.text | test("TODO|FIXME")) then "tech-debt"
        elif (.data.lines.text | test("password|secret")) then "hardcoded-secret"
        elif (.data.lines.text | test("setTimeout")) then "timing-hack"
        else "other"
        end
      )
    }' .specify/review-rg.ndjson > .specify/review-patterns.json
}
```

**Benefits:**
- ✅ 10 process spawns → 1 (90% reduction)
- ✅ 10 disk reads → 1 (I/O pressure reduced)
- ✅ Pattern categorization in single jq pass
- ✅ Consistent timestamp (all patterns scanned at same state)

**Pattern Coverage:**
| Category | Pattern | Example |
|----------|---------|---------|
| Security | `eval(`, hardcoded secrets | `eval(userInput)`, `API_KEY="xxx"` |
| Performance | async loops, nested loops | `for await (x of arr)` |
| Maintainability | magic numbers, tech debt | `if (x > 500)`, `// TODO: fix` |
| Anti-patterns | timing hacks, console logs | `setTimeout(..., 100)` |

---

### 1.3 Parallel Execution Architecture

**Current Problem:**
```bash
# Step 4: Sequential execution
run_jscpd           # Wait 8s
run_eslint          # Wait 7s
run_ripgrep         # Wait 5s
# Total: 20s (all serial)
```

**Optimization:**
```bash
# Step 4: Parallel Static Analysis
run_parallel_static_analysis() {
  mkdir -p .specify/review

  echo "🔄 Running parallel static analysis..."

  (
    # Process 1: Duplication Detection (CPU-bound)
    {
      if command -v jscpd &>/dev/null && [ "$CHANGED_COUNT" -gt 3 ]; then
        npx jscpd $CHANGED_FILES \
          --threshold 5 \
          --min-lines 5 \
          --min-tokens 50 \
          --format json \
          --output .specify/review/jscpd.json \
          2>/dev/null || echo '{"duplicates":[]}' > .specify/review/jscpd.json
      else
        echo '{"duplicates":[],"skip":"insufficient files"}' > .specify/review/jscpd.json
      fi
    } &

    # Process 2: Complexity + Linting (CPU-bound)
    {
      CHANGED_TS=$(echo "$CHANGED_FILES" | rg '\.(ts|js|tsx|jsx)$' || true)
      if [ -n "$CHANGED_TS" ]; then
        npx eslint \
          --cache \
          --cache-location .specify/.eslintcache \
          --cache-strategy content \
          --max-warnings 0 \
          --format json \
          --rule 'complexity: [error, 10]' \
          --rule 'max-lines-per-function: [error, {max: 100}]' \
          --rule 'max-depth: [error, 4]' \
          $CHANGED_TS \
          > .specify/review/eslint.json 2>&1 || true
      else
        echo '[]' > .specify/review/eslint.json
      fi
    } &

    # Process 3: Python Complexity (CPU-bound, parallelized internally)
    {
      CHANGED_PY=$(echo "$CHANGED_FILES" | rg '\.py$' || true)
      if [ -n "$CHANGED_PY" ]; then
        printf "%s\n" $CHANGED_PY \
          | xargs -P "$(nproc)" -I{} radon cc -nb --json {} \
          | jq -s 'add // {}' \
          > .specify/review/radon.json 2>/dev/null || echo '{}' > .specify/review/radon.json
      else
        echo '{}' > .specify/review/radon.json
      fi
    } &

    # Process 4: Pattern Detection (I/O-bound)
    {
      run_consolidated_ripgrep
    } &

    # Wait for all parallel jobs
    wait
  )

  echo "✅ Static analysis complete (parallel execution)"
}
```

**Benefits:**
- ✅ 20s → 8s on 4-core CPU (60% reduction)
- ✅ CPU utilization: 25% → 95% (multicore)
- ✅ Graceful degradation (tools missing → skip + warn)

**CPU Usage Diagram:**
```
Sequential (1 core):
Core 1: [jscpd====][eslint====][radon====][rg==]
Core 2: [........................................]
Core 3: [........................................]
Core 4: [........................................]
Time:   0s        8s        15s       20s   22s

Parallel (4 cores):
Core 1: [jscpd========]
Core 2: [eslint=======]
Core 3: [radon====]
Core 4: [rg==]
Time:   0s            8s
```

---

## Phase 2: Smart Optimization (50-80% on re-run)

### 2.1 File Hash Caching

**Current Problem:**
- Every run re-analyzes ALL files
- Even unchanged files from previous review

**Optimization:**
```bash
# Step 3.5: Hash-Based Change Detection
compute_file_hashes() {
  local targets="$1"
  local cache_file=".specify/review-hash.cache"
  local current_hash=".specify/review-hash.now"

  # Compute current hashes (parallel)
  echo "$targets" \
    | xargs -P "$(nproc)" -I{} sh -c 'echo "$(sha1sum "{}" | cut -d" " -f1)  {}"' \
    | sort -k2 \
    > "$current_hash"

  # Compare with previous cache
  if [ -f "$cache_file" ]; then
    # Find files with different hash
    comm -13 \
      <(sort -k2 "$cache_file" 2>/dev/null || true) \
      <(sort -k2 "$current_hash") \
      | cut -d' ' -f2- \
      > .specify/review-changed-by-hash.txt

    TRULY_CHANGED=$(cat .specify/review-changed-by-hash.txt)
    CACHE_HIT_COUNT=$(($(echo "$targets" | wc -l) - $(echo "$TRULY_CHANGED" | wc -l)))

    echo "💾 Cache hit: $CACHE_HIT_COUNT files skipped (unchanged content)"
  else
    TRULY_CHANGED="$targets"
    echo "🆕 First run: no cache available"
  fi

  # Update cache for next run
  cp "$current_hash" "$cache_file"

  echo "$TRULY_CHANGED"
}

# Usage in workflow
CHANGED_FILES=$(discover_changed_files)
ANALYSIS_TARGETS=$(compute_file_hashes "$CHANGED_FILES")
export ANALYSIS_TARGETS
```

**Benefits:**
- ✅ Re-run with 0 changes: 60s → 12s (80% reduction)
- ✅ Re-run with 2 file changes: 60s → 18s (70% reduction)
- ✅ Cache invalidation automatic (hash comparison)

**Cache Strategy:**
- **Storage**: `.specify/review-hash.cache` (gitignored)
- **Invalidation**: Content-based (SHA1 hash)
- **Scope**: Per-file granularity
- **Cleanup**: Auto-cleanup on branch switch

---

### 2.2 Conditional Precision Mode

**Current Problem:**
```bash
# Always run expensive tools
jscpd --all-files  # 8s even if no duplication risk
radon --all-files  # 5s even if simple functions
```

**Optimization:**
```bash
# Step 4.A: Conditional jscpd (only if risk detected)
run_conditional_jscpd() {
  # Quick heuristic: file size + similarity check
  local large_files=$(echo "$ANALYSIS_TARGETS" | xargs -I{} wc -l {} | awk '$1 > 200 {print $2}')

  if [ -z "$large_files" ]; then
    echo '{"duplicates":[],"skip":"all files < 200 LOC"}' > .specify/review/jscpd.json
    echo "⏭️  jscpd skipped (no large files)"
    return
  fi

  # Run only on large files (duplication risk)
  npx jscpd $large_files --threshold 5 --format json --output .specify/review/jscpd.json
}

# Step 5: Conditional Deep Analysis
run_conditional_ai_analysis() {
  # Load static analysis results
  local high_complexity=$(jq -r '.[] | select(.complexity > 7) | .filePath' .specify/review/eslint.json 2>/dev/null)

  if [ -z "$high_complexity" ]; then
    echo "✅ All functions have acceptable complexity (≤7)"
    FOCUS_AREAS="none"
  else
    echo "⚠️  High complexity detected in $(echo "$high_complexity" | wc -l) files"
    FOCUS_AREAS="$high_complexity"
  fi

  # AI analyzes ONLY focus areas for comment quality
  # (instead of all files)
}
```

**Trigger Conditions:**
| Tool | Trigger Condition | Skip Condition |
|------|------------------|----------------|
| jscpd | File > 200 LOC | All files < 200 LOC |
| AI Comment Check | Complexity > 7 | All complexity ≤ 7 |
| N+1 Detection | DB access + loops | No DB queries |
| Security Deep Scan | Auth/route changes | No auth code changed |

**Benefits:**
- ✅ jscpd: 8s → 2s (75% reduction when skippable)
- ✅ AI analysis: 20s → 8s (60% reduction with focus)
- ✅ Maintains quality (precision not sacrificed)

---

## Phase 3: Incremental Intelligence (40% AI time reduction)

### 3.1 Real-Time Pattern Aggregation

**Current Problem:**
```javascript
// Step 5.5: Separate ultrathink pass
// 1. Collect all issues from Step 5
// 2. Re-analyze for patterns
// 3. Detect systemic issues
// Result: Duplicate work + extra time
```

**Optimization:**
```javascript
// Step 5: Integrated Pattern Tracking
class IncrementalPatternAnalyzer {
  private patterns = new Map<string, {
    count: number;
    files: Set<string>;
    severity: 'low' | 'medium' | 'high';
    examples: Array<{file: string; line: number; code: string}>;
  }>();

  private SYSTEMIC_THRESHOLD = 3;

  // Called during Step 5 (not after)
  recordIssue(issue: {
    category: string;
    file: string;
    line: number;
    severity: string;
    code: string;
  }) {
    const pattern = this.patterns.get(issue.category) || {
      count: 0,
      files: new Set(),
      severity: 'low',
      examples: []
    };

    pattern.count++;
    pattern.files.add(issue.file);
    pattern.examples.push({
      file: issue.file,
      line: issue.line,
      code: issue.code
    });

    // Update severity dynamically
    if (pattern.count >= this.SYSTEMIC_THRESHOLD) {
      pattern.severity = 'high';
      issue.isSystemic = true;  // Flag immediately
    }

    this.patterns.set(issue.category, pattern);
  }

  // Step 5.5: Just retrieve aggregated data (no re-analysis)
  getSystemicIssues() {
    return Array.from(this.patterns.entries())
      .filter(([_, data]) => data.count >= this.SYSTEMIC_THRESHOLD)
      .map(([category, data]) => ({
        category,
        occurrences: data.count,
        affectedFiles: Array.from(data.files),
        examples: data.examples.slice(0, 3)  // Top 3 examples
      }));
  }

  // No need for separate pattern detection pass
  generateRootCauseAnalysis() {
    const systemicIssues = this.getSystemicIssues();

    // Group by root cause (already aggregated)
    return {
      architecturalIssues: systemicIssues.filter(i =>
        ['Inconsistent Error Handling', 'Missing Abstraction'].includes(i.category)
      ),
      performanceIssues: systemicIssues.filter(i =>
        ['N+1 Query', 'Sync in Async'].includes(i.category)
      ),
      maintenanceIssues: systemicIssues.filter(i =>
        ['Magic Numbers', 'Duplication'].includes(i.category)
      )
    };
  }
}

// Usage in Step 5
const analyzer = new IncrementalPatternAnalyzer();

for (const file of ANALYSIS_TARGETS) {
  const issues = analyzeFile(file);

  for (const issue of issues) {
    analyzer.recordIssue(issue);  // Real-time aggregation

    if (issue.isSystemic) {
      console.log(`🔴 Systemic issue detected: ${issue.category} (${analyzer.patterns.get(issue.category).count} occurrences)`);
    }
  }
}

// Step 5.5: No re-processing needed
const report = analyzer.generateRootCauseAnalysis();
```

**Benefits:**
- ✅ Step 5.5 time: 5s → 1s (80% reduction)
- ✅ Memory efficiency: O(issues) → O(patterns)
- ✅ Real-time feedback (systemic issues flagged early)

**Comparison:**
```
Old Approach (Sequential):
Step 5:   [Analyze file 1] [Analyze file 2] ... [Analyze file N]
Step 5.5: [Re-scan all issues] [Detect patterns] [Group by root cause]
Time:     20s                  +5s

New Approach (Incremental):
Step 5:   [Analyze file 1 + aggregate] [Analyze file 2 + aggregate] ...
Step 5.5: [Retrieve aggregated data]
Time:     20s                          +1s
```

---

### 3.2 Context Document Caching

**Current Problem:**
```bash
# Multiple reads of same files
step_2() { cat spec.md | extract_terms; }
step_5() { cat spec.md | extract_terms; }  # Duplicate read
step_5_security() { cat plan.md | extract_layers; }
step_5_architecture() { cat plan.md | extract_layers; }  # Duplicate read
```

**Optimization:**
```bash
# Step 2: Load and Cache Context Once
declare -A CONTEXT_CACHE

load_context_documents() {
  echo "📚 Loading context documents..."

  # Read files once
  CONTEXT_CACHE[spec_raw]=$(cat "$FEATURE_DIR/spec.md" 2>/dev/null || echo "")
  CONTEXT_CACHE[plan_raw]=$(cat "$FEATURE_DIR/plan.md" 2>/dev/null || echo "")
  CONTEXT_CACHE[constitution_raw]=$(cat .specify/memory/constitution.md 2>/dev/null || echo "")

  # Pre-parse critical sections
  CONTEXT_CACHE[domain_terms]=$(echo "${CONTEXT_CACHE[spec_raw]}" | extract_domain_terms)
  CONTEXT_CACHE[arch_layers]=$(echo "${CONTEXT_CACHE[plan_raw]}" | extract_architecture_layers)
  CONTEXT_CACHE[naming_rules]=$(echo "${CONTEXT_CACHE[constitution_raw]}" | extract_naming_conventions)

  # Export as environment variables (shared across all steps)
  export DOMAIN_TERMS="${CONTEXT_CACHE[domain_terms]}"
  export ARCH_LAYERS="${CONTEXT_CACHE[arch_layers]}"
  export NAMING_RULES="${CONTEXT_CACHE[naming_rules]}"

  echo "✅ Context cached: ${#CONTEXT_CACHE[@]} entries"
}

# Step 5: Use cached context (no re-read)
check_domain_terminology() {
  # OLD: local terms=$(cat "$FEATURE_DIR/spec.md" | extract_terms)
  # NEW: Use pre-parsed cache
  local terms="$DOMAIN_TERMS"

  rg -n "$terms" $ANALYSIS_TARGETS --json | ...
}

check_architecture_layering() {
  # OLD: local layers=$(cat "$FEATURE_DIR/plan.md" | extract_layers)
  # NEW: Use pre-parsed cache
  local layers="$ARCH_LAYERS"

  validate_layer_violations "$layers"
}
```

**Benefits:**
- ✅ File reads: 6-8 times → 1 time (85% reduction)
- ✅ Parsing overhead eliminated (pre-computed)
- ✅ Consistent context (no race conditions)

**Memory Impact:**
- Typical spec.md: 50KB → 50KB RAM
- Typical plan.md: 30KB → 30KB RAM
- Total overhead: ~100KB (negligible)

---

## Integration Plan

### Phase 1: Implementation Order (Day 1-2)

```bash
# 1.1 Changed Files Priority (30 min)
git checkout -b feat/review-optimization-phase1
# Modify Step 3 in ms.review.md

# 1.2 Single-Pass Ripgrep (45 min)
# Modify Step 4.C in ms.review.md

# 1.3 Parallel Execution (60 min)
# Modify Step 4 in ms.review.md

# Test Phase 1
./test-review-performance.sh
# Expected: 60s → 20s on medium PR
```

### Phase 2: Implementation Order (Day 3-4)

```bash
# 2.1 File Hash Caching (90 min)
# Add new Step 3.5 in ms.review.md

# 2.2 Conditional Precision (60 min)
# Modify Step 4.A and Step 5 in ms.review.md

# Test Phase 2
./test-review-performance.sh --cache
# Expected: Re-run 60s → 12s
```

### Phase 3: Implementation Order (Day 5)

```bash
# 3.1 Real-Time Pattern Aggregation (90 min)
# Refactor Step 5 and Step 5.5 in ms.review.md

# 3.2 Context Caching (45 min)
# Modify Step 2 in ms.review.md

# Test Phase 3
./test-review-performance.sh --full
# Expected: AI analysis 20s → 12s
```

---

## Testing Strategy

### Performance Benchmarks

```bash
# Create test scenarios
mkdir -p .specify/test-scenarios

# Scenario 1: Small PR (5 files)
git checkout -b test/small-pr
# Modify 5 files
time /ms.review > .specify/test-scenarios/small-pr-before.log

# Apply Phase 1 optimizations
time /ms.review > .specify/test-scenarios/small-pr-after.log

# Compare
diff <(grep "Total time" .specify/test-scenarios/small-pr-before.log) \
     <(grep "Total time" .specify/test-scenarios/small-pr-after.log)
```

### Quality Validation

```bash
# Ensure optimizations don't reduce quality
diff .specify/test-scenarios/review-before.md \
     .specify/test-scenarios/review-after.md

# Expected: Same issues detected, different performance
```

### Regression Tests

| Test Case | Before | After | Acceptance |
|-----------|--------|-------|------------|
| Small PR (5 files) | 30s | <10s | ✅ Pass if <10s |
| Medium PR (20 files) | 60s | <20s | ✅ Pass if <20s |
| Large PR (100 files) | 120s | <50s | ✅ Pass if <50s |
| Re-run (no changes) | 60s | <15s | ✅ Pass if <15s |
| Full scan (no git) | 120s | <60s | ✅ Pass if <60s |

---

## Risk Analysis

### High Risk Items

1. **Hash Cache Corruption**
   - **Risk**: Cache desync → wrong files skipped
   - **Mitigation**: Content-based SHA1 (collision-resistant)
   - **Fallback**: `--no-cache` flag to force full scan

2. **Parallel Race Conditions**
   - **Risk**: File writes conflict (eslint.json)
   - **Mitigation**: Separate output files per tool
   - **Fallback**: Sequential mode on tool failure

3. **Git Diff Edge Cases**
   - **Risk**: Renamed files not detected
   - **Mitigation**: `--diff-filter=ACMRTUXB` includes renames
   - **Fallback**: Full scan when diff fails

### Medium Risk Items

4. **Conditional Skip Over-Optimization**
   - **Risk**: Skip important analysis (false negative)
   - **Mitigation**: Conservative thresholds (e.g., 200 LOC for jscpd)
   - **Fallback**: `--thorough` flag to disable skips

5. **Context Cache Staleness**
   - **Risk**: spec.md updated but cache not refreshed
   - **Mitigation**: Cache in memory (single run scope)
   - **Fallback**: No persistent cache across runs

---

## Performance Monitoring

### Instrumentation Points

```bash
# Add timing markers
time_checkpoint() {
  local label="$1"
  local elapsed=$(($(date +%s%3N) - START_TIME))
  echo "$elapsed ms - $label" >> .specify/review-timing.log
}

START_TIME=$(date +%s%3N)
time_checkpoint "Start"

discover_changed_files
time_checkpoint "File discovery"

run_parallel_static_analysis
time_checkpoint "Static analysis"

run_ai_analysis
time_checkpoint "AI analysis"

generate_report
time_checkpoint "Report generation"
```

### Metrics to Track

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Total execution time | <20s (medium PR) | >30s |
| File discovery time | <2s | >5s |
| Static analysis time | <8s | >15s |
| AI analysis time | <10s | >20s |
| Cache hit rate | >70% (re-run) | <50% |

---

## Success Criteria

### Must Have (P0)
- ✅ 60% reduction in total time (medium PR)
- ✅ 80% reduction on cache hit (re-run)
- ✅ 100% issue detection parity (no false negatives)
- ✅ Backward compatible (works without git context)

### Should Have (P1)
- ✅ 70% reduction with all phases
- ✅ Parallel execution on multicore
- ✅ Graceful degradation (missing tools)

### Nice to Have (P2)
- ✅ Real-time progress updates
- ✅ Performance profiling output
- ✅ Adaptive thresholds (ML-based)

---

## Rollout Plan

### Week 1: Phase 1 (Quick Wins)
- Day 1: Implement changed files priority
- Day 2: Implement single-pass ripgrep + parallel execution
- Day 3: Internal testing
- Day 4: Documentation update
- Day 5: Deploy to production

### Week 2: Phase 2 (Smart Optimization)
- Day 1-2: Implement hash caching
- Day 3: Implement conditional precision
- Day 4: Integration testing
- Day 5: Deploy to production

### Week 3: Phase 3 (Incremental Intelligence)
- Day 1-2: Refactor pattern aggregation
- Day 3: Implement context caching
- Day 4: End-to-end testing
- Day 5: Performance benchmarking + documentation

---

## Appendix A: Tool Configuration

### ESLint Cache Configuration
```json
{
  "cache": true,
  "cacheLocation": ".specify/.eslintcache",
  "cacheStrategy": "content"
}
```

### Ripgrep Performance Tuning
```bash
export RIPGREP_CONFIG_PATH=".specify/.ripgreprc"

# .ripgreprc
--max-columns=500
--max-columns-preview
--threads=4
--mmap
```

### Radon Parallelization
```bash
# Use GNU parallel for better performance
find src -name "*.py" | parallel -j+0 radon cc -nb --json
```

---

## Appendix B: Compatibility Matrix

| Tool | Required | Fallback | Performance Impact |
|------|----------|----------|-------------------|
| git | Yes | Full scan | -60% optimization |
| ripgrep | Yes | grep (slow) | -30% optimization |
| jq | Yes | None | Fatal error |
| eslint | No | Skip | -20% quality |
| radon | No | Skip | -20% quality (Python) |
| jscpd | No | Skip | -10% quality |
| parallel | No | xargs | -10% speed |

---

## Appendix C: Migration Guide

### For Users
```bash
# No changes required - backward compatible
/ms.review  # Works as before, but faster

# Optional: Force full scan
FORCE_FULL_SCAN=1 /ms.review

# Optional: Disable cache
DISABLE_CACHE=1 /ms.review

# Optional: Thorough mode (no conditional skips)
THOROUGH_MODE=1 /ms.review
```

### For Developers
```bash
# Update .gitignore
echo ".specify/review-hash.cache" >> .gitignore
echo ".specify/.eslintcache" >> .gitignore

# Test performance
time /ms.review  # Should see timing breakdown
```

---

**Document Status**: Ready for implementation
**Next Step**: Proceed to Phase 1 implementation
**Estimated Total Implementation Time**: 2-3 weeks
**Expected Performance Gain**: 60-80% reduction in execution time

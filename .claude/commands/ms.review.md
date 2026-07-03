---
description: "Code quality review after implementation"
argument-hint: "[--skip-codex] [--background] [--model MODEL] [--effort low|medium|high] [--runtime-agent=agy]"
---

# /ms.review - Code Quality Review

Performs deep code quality review and executable code-gate validation after `/ms.implement` completes. Feature Map validation belongs to `/ms.checklist`; pre-implementation document consistency belongs to `/ms.analyze`.

## Overview

**Purpose**: Review implemented code quality AFTER `/ms.implement` and decide whether the branch is ready for `/ms.fin`.

**NOT for**:
- ❌ PRD-to-Feature-Map validation (use `/ms.checklist` before `/ms.specify`)
- ❌ Drafting or clarifying requirements (use `/ms.specify` and `/ms.clarify`)
- ❌ Pre-implementation document consistency (use `/ms.analyze` before `/ms.implement`)

**FOR**:
- ✅ Code design quality (architecture, patterns, DRY)
- ✅ Maintainability (naming, comments, error handling)
- ✅ Performance issues (N+1 queries, unnecessary computations)
- ✅ Security deep-dive (auth gaps, logging leaks, error exposure)
- ✅ Test quality (AAA pattern, boundary tests, mock overuse)
- ✅ Post-implementation code gates (lint, typecheck, tests, build, coverage) plus TAG integrity reporting
- ✅ Done Criteria Execution — actually running the Feature's entrypoint against its `### Done criteria`, not just passing unit tests

## Workflow Position

```
/ms.implement → /ms.review → /ms.fin
```

## Usage

```bash
/ms.review
/ms.review --background
/ms.review --skip-codex
/ms.review --model gpt-5.4-mini --effort high
```

Codex runs in the foreground by default. Use `--background` only when the review
is large and the user explicitly wants to resume later.

Default Codex runtime:

```text
model: gpt-5.5
effort: medium
```

**When to run**: After implementing all tasks, before final commit.

`/ms.analyze` remains the pre-implementation document gate: spec ↔ plan ↔ tasks,
Constitution alignment, and drift detection. `/ms.review` owns the post-implementation
code gate, so a separate `analyze --code` path is unnecessary.

## Post-Implementation Gate Ownership

When `/ms.review` runs after implementation, it shall verify both qualitative code
review findings and executable gates:

- local CI gates via the `local-ci` agent: lint → types → tests → build, using the
  repository's own workflow commands
- TRUST code checks via the `quality-gate` or `trust-validator` agent: coverage,
  file/function size, complexity, strict typing, security scan, TAG integrity reporting
- advisory Codex code review persisted to `docs/review/{spec-id}.codex-review.md` unless `--skip-codex` is supplied
- unresolved HIGH/CRITICAL review issues persisted to `.specify/review-state.txt`
  so `/ms.fin` can block or require explicit acknowledgement

## Execution Steps

### Step 1: Prerequisites Check

Run the Spec-Kit prerequisites script to get context. The script lives under
`.specify/scripts/bash/` (installed by `/ms.init`); `--require-tasks --include-tasks` is the
implementation-phase check (validates `plan.md` + `tasks.md` exist). Do **not** pass
`--require-spec`/`--require-plan` — those flags do not exist on current Spec-Kit and the
script aborts on unknown options.

```bash
.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
```

Parse JSON output to extract:
- `FEATURE_DIR`: Feature directory (e.g., `specs/001-auth-spec/`)
- `AVAILABLE_DOCS`: List of available documents (spec.md, plan.md, tasks.md, etc.)
- `REPO_ROOT`: not in this JSON payload — derive it with `git rev-parse --show-toplevel`
  (or run the script with `--paths-only --json` if you need the path bundle instead).

**Required files** — SPECTER validates these **itself** from `AVAILABLE_DOCS` (do not outsource
this gate to the upstream script's flags; the script only validates `plan.md`+`tasks.md`):
- ✅ `spec.md` (for domain terminology) — SPECTER-required regardless of upstream flags
- ✅ `plan.md` (for architecture reference)
- ✅ Implemented code files (src/, tests/)

**If `spec.md` or `plan.md` is missing**: Display error and suggest running `/ms.specify` or
`/ms.plan`. Do not proceed — SPECTER's review rigor is owned here, not delegated to Spec-Kit.

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

### Step 6.5: Executable Code Gates

Run the code gates that make the implemented branch merge-ready.

#### A. Local CI Gate

Delegate to the `local-ci` agent. It reads the repository's CI configuration and
runs locally reproducible gates in this order:

```text
lint → types → tests → build
```

Rules:

- Use the repository's declared runner and working directories.
- Skip secret-dependent or server-dependent jobs with an explicit reason.
- The agent reports only pass/fail per gate and edits nothing.
- Any failing executable gate is a HIGH issue at minimum; a failing test, typecheck,
  lint, or build gate is CRITICAL when it affects changed code.

#### B. TRUST Code Gate

Run `quality-gate` or `trust-validator` for code-level TRUST checks:

- coverage threshold from Constitution Section III (Test-First Implementation) or the active project threshold
- production file SLOC and function length limits
- function complexity limits
- strict typing and zero-warning lint policy
- security scan results where tooling exists
- TAG integrity report: `@SPEC -> @TEST -> @CODE` with optional `@DOC`; warning by default unless Section IX or CI promotes it

#### C. Gate Result Handling

- If CRITICAL executable gates fail, or unresolved HIGH issues remain, mark
  review as **NOT READY** and write `.specify/review-state.txt`. TAG-only
  findings do not make the review NOT READY unless Section IX or CI explicitly
  promotes TAG integrity to blocking.
- If only HIGH/MEDIUM warnings remain, mark review as **READY WITH WARNINGS** and
  persist the warning summary for `/ms.fin` acknowledgement.
- If all executable gates and deep review checks pass, remove stale
  `.specify/review-state.txt` if it exists.


---

### Step 6.6: Done Criteria Execution

Executable lint/type/test/build gates (Step 6.5) prove the code compiles and unit-passes; they do
not prove the product actually runs. This step closes that gap by driving the real entrypoint,
before the dual-agent review so both agents can see the results in their prompt context.

1. **Load the criteria.** Read the Feature's `### Done criteria` from its `## Feature NNN:`
   section in `docs/prd/feature-map.md`, and the acceptance scenarios in `spec.md`.
2. **Classify each criterion**:
   - **RUNNABLE**: provable by executing something — a CLI command, starting a server/daemon and
     hitting a health/endpoint check, running a script, or driving a reproducible user flow
     end-to-end.
   - **MANUAL**: requires human eyes or a physical device (visual polish, hardware, third-party
     dashboard, anything not scriptable from this session).
3. **Execute every RUNNABLE criterion for real**: start the actual entrypoint (the daemon,
   server, or CLI the Feature ships — not a mock), drive the affected flow, and observe the
   actual behavior. This is a bounded smoke of the product path, not a load test — kill any
   long-running process (server, watcher) once its criterion has been observed.
4. **Phase E2E scenario**: if this Feature is a Phase's last Feature (per the Feature Map DAG),
   also execute that Phase's end-to-end scenario as one additional RUNNABLE criterion.
5. **Record results** in a table, included in the Step 7 review report:

   | Criterion | Class | Result | Evidence |
   | --- | --- | --- | --- |
   | ... | RUNNABLE \| MANUAL | PASS \| FAIL \| MANUAL | command/output, or "n/a — manual" |

6. **Gate**: any RUNNABLE criterion with Result `FAIL` sets the overall `/ms.review` result to
   **NOT READY** — the same severity as a failing executable gate in Step 6.5. Do not let a green
   lint/type/test/build run mask a product that does not actually start or work.
7. **Report MANUAL items** in the Korean report (Step 7) as an explicit checklist so the user's
   own real-device/manual testing loop has a concrete list to work from:
   ```text
   📋 수동 확인 필요
   - <criterion>: <디바이스/환경> — <확인 절차> — 기대 결과: <expected>
   ```

**Optional knob** (document only, not the default): `--runtime-agent=agy` delegates this step's
execution to Antigravity instead of the host, so an independent party (not the implementer) drives
the product. The default stays host-run. Do not enable this by default until the Antigravity
hardening work (external-agent preflight/degrade rule) has proven agy stable in this environment.

---

### Step 6.7: Dual-Agent Code Review

Unless `--skip-codex` (or `--skip-agents`) is supplied, invoke both Codex and Antigravity after the local CI and TRUST gates have produced enough context. Both agents always run in adversarial mode. Both prompts also receive the Done Criteria Execution table from Step 6.6 so they can factor real runtime behavior into their review.

#### 0. External Agent Preflight (session-level, once)

Before invoking Codex or Antigravity, check availability **once per session** and remember the
result — do not re-check on every `/ms.review` call within the same session: the `codex`/`agy`
binaries are on PATH, auth is configured, and Codex's sandbox mode / Antigravity's write flag are
set (cheap config checks, not live probe runs). Retry once on failure (a plugin update can
transiently reset a flag).

If Antigravity is still unavailable after retry, run this station **Codex-only**, force the
station result to at most `WARN`, and record `Antigravity: UNAVAILABLE (<reason>)` in
`docs/review/{spec-id}.antigravity-review.md` in place of a normal report. Mirror the same rule if
Codex is unavailable instead (Antigravity-only + `Codex: UNAVAILABLE (<reason>)`). Never silently
report this station as if both agents ran when only one did; never block `/ms.review` on an
environment issue alone.

#### A. Codex Code Review
```text
/codex:rescue --fresh --model gpt-5.5 --effort medium <prompt>
```
Codex must read:
- `.specify/memory/constitution.md`
- `AGENTS.md` if it exists
- `specs/[spec-id]/spec.md`
- `specs/[spec-id]/plan.md`
- `specs/[spec-id]/tasks.md`
- `docs/prd/checklists/feature-NNN.checklist.md`
- the Step 6.6 Done Criteria Execution table (RUNNABLE results and evidence)
- the current git diff against the review base
- changed production files and changed tests

Codex must write:
`docs/review/{spec-id}.codex-review.md`

Codex prompt:
```text
You are performing an advisory SPECTER post-implementation code review.

Review the current implementation against spec.md, plan.md, tasks.md,
Constitution, AGENTS.md, and the changed code/tests. Do not edit files except
writing docs/review/{spec-id}.codex-review.md.

Focus on:
- implementation drift from spec/task intent
- missing or weak behavior tests
- auth, authorization, input validation, logging, and sensitive data exposure
- data loss, race condition, rollback, idempotency, and migration risks
- overcomplicated abstractions or non-surgical changes
- architecture violations against plan.md

Always challenge whether the implementation approach is simpler, safer, or
better scoped than available alternatives.

Write:

# Codex Code Review

**Mode**: codex-adversarial-code-review
**Result**: PASS | WARN | FAIL

## Findings

| Severity | Finding | Evidence | Required Fix |
| --- | --- | --- | --- |

## Verdict

One concise paragraph.

Also echo the finished report between ===REPORT BEGIN=== and ===REPORT END=== markers in your
final message, verbatim, so it can be salvaged if the file write fails.
```

#### B. Antigravity Code Review
```text
/antigravity:rescue --fresh --model gemini-3.5-flash --effort medium <prompt>
```

Antigravity must read:
- `.specify/memory/constitution.md`
- `AGENTS.md` if it exists
- `specs/[spec-id]/spec.md`
- `specs/[spec-id]/plan.md`
- `specs/[spec-id]/tasks.md`
- `docs/prd/checklists/feature-NNN.checklist.md`
- the Step 6.6 Done Criteria Execution table (RUNNABLE results and evidence)
- the current git diff against the review base
- changed production files and changed tests

Antigravity must write:
`docs/review/{spec-id}.antigravity-review.md`

Antigravity prompt:
```text
You are performing an advisory SPECTER post-implementation code review using Google Antigravity.

Review the current implementation against spec.md, plan.md, tasks.md,
Constitution, AGENTS.md, and the changed code/tests. Do not edit files except
writing docs/review/{spec-id}.antigravity-review.md.

Focus on:
- implementation drift from spec/task intent
- missing or weak behavior tests
- auth, authorization, input validation, logging, and sensitive data exposure
- data loss, race condition, rollback, idempotency, and migration risks
- overcomplicated abstractions or non-surgical changes
- architecture violations against plan.md

Always challenge whether the implementation approach is simpler, safer, or
better scoped than available alternatives.

Write:

# Antigravity Code Review

**Mode**: antigravity-adversarial-code-review
**Result**: PASS | WARN | FAIL

## Findings

| Severity | Finding | Evidence | Required Fix |
| --- | --- | --- | --- |

## Verdict

One concise paragraph.

Also echo the finished report between ===REPORT BEGIN=== and ===REPORT END=== markers in your
final message, verbatim, so it can be salvaged if the file write fails.
```

If the user supplied `--background`, add `--background` to both invocations and report that `/ms.review` must be rerun after both files appear. If the user supplied `--model` or `--effort`, pass those values through instead of the defaults.

**Report-Write Protocol**: agents still write their own report files (unchanged, primary path).
After the run, deterministically check the written file: it exists, is non-empty, and contains
`**Result**:`. If a report is missing or partial after one retry, **salvage** it from that retry's
`===REPORT BEGIN===`/`===REPORT END===` markers instead of stopping the whole gate or
hand-transcribing it yourself. If no markers were captured either, apply the Preflight Degrade
Rule (subsection 0) instead of stopping outright.

#### C. Result handling for both reviews:
- `PASS`: keep the SPECTER review result unchanged.
- `WARN`: final `/ms.review` result is at least READY WITH WARNINGS unless Claude/SPECTER explicitly explains why every warning is a false positive.
- `FAIL`: final `/ms.review` result is NOT READY unless Claude/SPECTER explicitly downgrades the finding with source evidence.
- `PENDING`: if `--background` was used and either report is missing, stop and tell the user to rerun `/ms.review` after both reports appear.

#### D. Convergence Policy (re-round caps)

Unbounded re-review loops burn tokens without improving the outcome (atlas F001 ran 10 Codex
rounds on one Feature; 47+ re-rounds project-wide). Cap automatic re-rounds:

- **Round 1**: the full dual-agent run above, over the whole diff.
- **Round 2** (only if Round 1 produced any `FAIL` finding): re-run scoped to *only* the findings
  that were `FAIL` — the prompt states each failing finding plus the fix diff made in response; it
  does not ask either agent to re-review the whole diff again.
- **Round 3** is the last automatic round, and only re-checks findings still `FAIL` after Round 2.
- **Stop condition**: after Round 3, or as soon as only `WARN`-level findings remain (no `FAIL`),
  stop re-running agents automatically. Record every residual `WARN` in `docs/review/` and
  `.specify/review-state.txt` — do not silently drop it — and hand the decision (proceed with
  warnings, or fix and rerun manually) to the user. Running a further round after this point
  requires an explicit user instruction; it is not something `/ms.review` does on its own.

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

- Summary: CRITICAL/HIGH/MEDIUM/LOW counts, overall score, Codex review result
- Intent & Focus Charter (inline copy of Step 2.5 so report is self-contained)
- Done Criteria Execution table (from Step 6.6) plus the "📋 수동 확인 필요" MANUAL checklist
- Production Risks, Strategic Unlocks, Quick Wins
- Coverage Checklist
- Hidden LOW issues count (show with `--verbose`)

---

### Step 8: Interactive Actions (NEW)

**Only if HIGH/CRITICAL issues exist**, prompt user:

- Do NOT attempt to auto-fix issues. Leave fixes to `/ms.implement --mode=refactor` or the main conversation.
- Ask user if they want to abort to fix the issues manually.
- Or continue without fixes (flagged in `/ms.fin`)

---

### Step 9: Cleanup and State Management

Remove analysis artifacts and save state for `/ms.fin` integration:

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

# Save non-blocking state for /ms.fin visibility.
if [ "${CRITICAL_COUNT:-0}" -gt 0 ] || [ "${HIGH_COUNT:-0}" -gt 0 ]; then
  {
    echo "${CRITICAL_COUNT:-0} CRITICAL issues unresolved"
    echo "${HIGH_COUNT:-0} HIGH issues unresolved"
    echo "Run /ms.review to check"
    echo "Review report: $REPORT_FILE"
  } > .specify/review-state.txt
else
  rm -f .specify/review-state.txt
fi
```

**State policy**: `.specify/review-state.txt` is a visibility artifact for
`/ms.fin`, not a mandatory publish blocker. Executable gate failures
inside `/ms.review` remain blocking for the review result itself.

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
# Still runs: executable gates in Step 6.5
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

### Codex Review Controls

```bash
/ms.review --skip-codex
/ms.review --background
/ms.review --model gpt-5.4-mini --effort high
```

- `--skip-codex`: skip advisory Codex code review.
- `--background`: start Codex review in the background and require a later `/ms.review` rerun.
- `--model` / `--effort`: override the default `gpt-5.5` / `medium` runtime.
- `--runtime-agent=agy`: delegate Step 6.6's Done Criteria Execution to Antigravity instead of
  the host. Documented as a knob, not a default — keep host-run until Antigravity has proven
  stable in this environment.

> The dual-agent review always runs in adversarial mode — both Codex and
> Antigravity challenge design choices, simpler/safer alternatives, and hidden
> risks. There is no flag to toggle this; it is the default behavior.

### Skip Slow Checks

For quick review during development:

```bash
/ms.review --fast
# Skips: optional slow static-analysis tools (jscpd, extended complexity scans)
# Still runs: local CI gate + TRUST critical checks in Step 6.5
```

`--fast` must never skip lint, typecheck, tests, or build. TAG findings remain warning/report-only unless Section IX or CI explicitly promotes them to blocking.
Those executable gates are owned by `/ms.review`.

### Focus on Category

Review a specific qualitative aspect while still running executable gates:

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
/ms.fin
```

### Before /ms.fin (ENHANCED)

`/ms.fin` command should surface review state as a warning, but it must not make
review-state mandatory:

```bash
# In /ms.fin workflow
if [ -f .specify/review-state.txt ]; then
  echo "⚠️ Prior /ms.review state exists:"
  cat .specify/review-state.txt
  echo ""
  echo "Continuing because review-state is advisory in /ms.fin."
fi
```

The review state file contains:
- Number of unresolved CRITICAL and HIGH issues
- Path to the latest review report
- Timestamp of last review

---

## Difference from Other Commands

| Command | Purpose | Checks | When to Run |
|---------|---------|--------|-------------|
| `/ms.verify` | Global Feature Map gate | PRD coverage, Feature ownership, DAG, stub-forward, template completeness | After `/ms.codex-checklist`, before `/ms.constitution` |
| `/ms.checklist` | Per-Feature gate | Selected Feature PRD fidelity, ownership, scope, done criteria | After `/ms.constitution`, before `/ms.agent-verify` |
| `/ms.agent-verify` | Per-Feature dual-agent gate | Concise Codex & Antigravity check of the Feature checklist | After `/ms.checklist`, before `/ms.specify` |
| `/ms.analyze` | Pre-implementation document gate | spec ↔ plan ↔ tasks consistency, Constitution alignment, drift detection | Before `/ms.implement` |
| `/ms.review` | Post-implementation code gate | Design review, Done Criteria Execution (runs the real entrypoint), Codex and Antigravity reviews, lint/types/tests/build, coverage, security, TAG integrity | After `/ms.implement` |
| `/ms.fin` | Final commit | Review-state acknowledgement, docs sync, commit, push, PR | After `/ms.review` passes |

**Mental model**:
- `/ms.verify` = "Did the PRD become the right Feature Map?"
- `/ms.checklist` = "Is this Feature ready to become a spec?"
- `/ms.agent-verify` = "Did the two independent reviewers find blocking checklist issues?"
- `/ms.analyze` = "Are the implementation documents coherent enough to build?"
- `/ms.review` = "Is the implemented branch ready to publish?"
- `/ms.fin` = "Commit, push, and open/update the PR."

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

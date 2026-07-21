---
description: "Code quality review after implementation"
argument-hint: "[--verbose] [--background] [--raise-audit-tier T2|T3] [--runtime-agent=agy]"
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
/ms.review --raise-audit-tier T3
```

Codex runs in the foreground by default. Use `--background` only when the review
is large and the user explicitly wants to resume later.

Reviewer effort, review adjacency, re-round cap, and WARN handling are bound by
the deterministic audit-tier receipt. The host and reviewers do not choose
them.

**When to run**: After implementing all tasks, before final commit.

`/ms.analyze` remains the pre-implementation document gate: spec ↔ plan ↔ tasks,
Constitution alignment, and drift detection. `/ms.review` owns the post-implementation
code gate, so a separate `analyze --code` path is unnecessary.

## Post-Implementation Gate Ownership

When `/ms.review` runs after implementation, it shall verify both qualitative code
review findings and executable gates:

- local CI gates via the `local-ci` agent: lint → types → tests → build, using the
  repository's own workflow commands
- TRUST code checks run inline with the repository's own tooling: coverage,
  file/function size, complexity, strict typing, security scan, TAG integrity reporting
- required independent Codex and Antigravity semantic reviews persisted under
  `docs/review/`
- unresolved HIGH/CRITICAL review issues persisted to `.specify/review-state.txt`
  so `/ms.fin` can surface them and force a CI re-run (advisory visibility —
  never a mandatory publish blocker; see Step 9's State policy)

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

**Open the stop-gate phase** (mechanical turn-end gate; installed by `/ms.init` Step 2.7b —
skip silently if the script does not exist):

```bash
[ -x .specify/scripts/bash/specter-stop-gate.sh ] && .specify/scripts/bash/specter-stop-gate.sh phase review
```

### Step 1.25: Classify The Actual Implementation Diff

Before choosing semantic scope, classify the actual working-tree diff:

```bash
python3 .specify/scripts/python/classify_audit_tier.py \
  --policy .specify/policies/audit-tier-policy.json classify \
  --feature <NNN> --phase diff \
  --feature-map docs/prd/feature-map.md \
  --diff-base HEAD --ledger
python3 .specify/scripts/python/classify_audit_tier.py \
  --policy .specify/policies/audit-tier-policy.json gate-status \
  --feature <NNN> --station review
```

The classifier hashes tracked and untracked diff evidence. Any later diff
change makes this receipt stale and requires reclassification before
aggregation. An auth, migration, CI/hook/permission, policy/gate, state,
concurrency, sensitive-data, or other hard-risk path/content match raises the
Feature to T3; removing it later does not lower the same Feature lifecycle.

If `--raise-audit-tier` was explicitly supplied, pass it only as the
classifier's upward-only `--raise-tier T2|T3`. Reject `--skip-codex`,
`--skip-agents`, `--model`, `--effort`, `--quick`, `--fast`,
`--no-interactive`, and any equivalent reviewer, module, scope, or
tier-lowering argument. Stop on missing, stale, malformed, or partially synced
policy/classifier capability.

---

### Step 1.5: Tool Availability Check

Review relies on several external binaries. Check upfront and degrade gracefully when unavailable:
`jq` missing → skip JSON aggregation steps; `rg` missing → abort (ripgrep is required for pattern
scan); `npx` missing → skip eslint/jscpd; `radon` missing → skip Python complexity; `jscpd` missing
→ skip duplicate detection. Remember which tools are available so each static-analysis phase in
Step 4 can short-circuit instead of failing mid-run.

---

### Step 2: Load Context (Cached)

Read `spec.md`, `plan.md`, and `constitution.md` once and keep them in memory for the rest of the
review — extract the spec's Domain Terminology section and the plan's Architecture section for
reference during Step 5's naming/architecture checks. Also read
`specs/{spec-id}/implementation-notes.md` if it exists — the deviation log `/ms.implement`
appends when reality forced a departure from `plan.md`. Factor each deviation into Step 5's
architecture/drift judgment (a deviation already logged and justified is not a drift finding)
and carry the file into the Step 7 report.

**Session read policy**: per AGENTS.md §2 — this cache covers the reads above, and the same
reuse rule applies to direct Read-tool reads elsewhere in this command (e.g. Step 5's per-file
review); a fresh `Read` immediately before `Edit`/`Write` is still required.

---

### Step 2.5: Intent & Focus Charter

Compile a succinct charter anchored to
`receipt.tier_settings.review_scope`:

1. **Derive primary risks** from `spec.md` constraints, plan.md architecture, and constitution guardrails.
2. **List the review targets** (files, components, user paths) coming from prerequisites JSON and recent implementation tasks.
3. **State up to three key questions** the review must answer (e.g., “Auth flow still follows token rotation rules?”).

T1 examines Feature artifacts, changed files, and directly affected seams only
and does not launch broad product-wide threat/performance/architecture modules
unless a finding escalates the tier. T2 preserves the current standard scope.
T3 includes adjacent trust boundaries and affected seams plus each applicable
targeted module in the canonical policy.

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

Discover the review's target files in priority order: (1) `git diff` against `origin/main` for
source files (`.ts .js .py .tsx .jsx`) under the shared scan roots — `src tests backend frontend
app lib packages`, the same set `check_tag_chain.py` SCAN_ROOTS uses (2026-07-18 audit #25);
(2) if empty, staged files under the same filter; (3) if still empty, a bounded smoke sample —
up to 200 source files under those roots. Split the result into TS/JS and Python subsets for
Step 4's language-specific static analysis.

---

### Step 3.5: Hash-Based Cache

Hash each candidate file (sha1) and diff against `.specify/review-hash.cache` from the prior run
to isolate the files that truly changed since the last review; update the cache afterward. With no
prior cache, every candidate counts as changed.

---

### Step 4: Static Analysis (Parallel)

Run these checks in parallel, each degrading to an empty/skipped result (not a failure) when its
tool is unavailable (Step 1.5) or has nothing to scan:

- **jscpd** duplicate detection, limited to files >200 LOC.
- **eslint** complexity (`complexity: 10`) and max-lines-per-function (100) on changed TS/JS files.
- **radon** cyclomatic complexity on changed Python files.
- **ripgrep**, one consolidated pass over the changed-file set (or `src tests` as fallback) for:
  `eval(`, `console.log/debug/info/warn`, raw `process.env`/`os.getenv` access, await-in-loop
  shapes, magic numbers (3+ digits), `TODO`/`FIXME`/`XXX`/`HACK`, hardcoded password/secret/token
  literals, and `setTimeout`/`setInterval`. Results feed Step 5's findings as evidence, not
  standalone verdicts.

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
3. **Scan the actual directory structure** (e.g. `tree src/ -L 2 --dirsfirst`).
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

Only for files Step 4 flagged with complexity >7: scan their comments and check for "why"
comments (good) vs "what" comments (redundant). Skip entirely if no file exceeds that threshold.

#### D. Error Handling

Check error handling consistency: custom exceptions vs generic Error, logging patterns.

#### E. Test Quality

Validate AAA pattern and boundary tests. **HIGH** if no tests for critical paths.
Prefer integration-style tests through the public API — a good test describes WHAT
the code does for a caller and survives a refactor that doesn't change behavior.
Named anti-patterns to flag (language-neutral):

- **Implementation-detail coupling**: mocking internal collaborators, asserting on
  call counts/order, or testing private methods — breaks on refactors with no
  behavior change.
- **Side-channel verification**: bypassing the public interface to check state
  directly (e.g. querying the DB row instead of calling the retrieval function)
  instead of verifying through the interface a caller would use.
- **Tautological tests**: the expected value is recomputed the same way the
  implementation computes it — demand an independent literal so the test can
  actually fail.
- **Mock placement**: mocks belong only at system boundaries (external APIs,
  databases — prefer a test DB, time/randomness, filesystem) — never on
  classes/modules the project itself controls.

#### F. Performance

Detect N+1 queries (loops with DB calls), unnecessary recomputation, memory leaks.

#### G. Security

Check missing auth on endpoints, sensitive data in logs, stack trace exposure.

#### H. Simplicity & Surgical Changes (Karpathy)

- **Overcomplication**: speculative abstractions, unrequested flexibility/config, error handling for impossible cases, "200 lines that could be 50". Senior test: would a senior call it overcomplicated?
- **Non-surgical diff**: changed lines that DON'T trace to the task — adjacent "improvements", style churn, refactors of unbroken code, deletion of pre-existing (not orphaned-by-this-change) code. (Planned refactor tasks are exempt — they ARE the request.)

#### I. Boundary Verification (Conditional)

Only when the Feature's diff touches a seam between layers — API ↔ frontend,
app ↔ DB, route ↔ file layout — or defines/edits a state machine. Skip entirely
otherwise; this is not per-review ceremony. Unit tests structurally miss these
bugs because each side passes in isolation.

Method, one line: **read both sides of the seam together — a check that passed
one side at a time is not a boundary check.**

1. API response shape mismatches hidden by generic casts (`as T`, `Any`,
   schema-less deserialization) — does the declared type match what the server
   actually sends?
2. File path ↔ router mapping mismatches (route groups, dynamic segments,
   catch-alls) — does every route the code links to resolve to a real file?
3. State machines with transitions that are defined but never implemented
   (dead transitions) — or implemented but undeclared.
4. camelCase ↔ snake_case field-name drift across DB / API / frontend layers.
5. Every API endpoint the frontend calls actually exists server-side (method
   and path both).
6. Async workflows returning more than one response shape (immediate `202`
   acknowledgement vs final result) — is the union expressed in the types, or
   does the client only handle one shape?
7. Type-cast escapes (`as unknown as`, `# type: ignore`, `@ts-ignore`) sitting
   exactly on a boundary — each one is a candidate hidden shape mismatch;
   verify the real shape behind it.

Findings use the standard severity model: a mismatch that breaks a runtime path
is **HIGH**; a latent drift not yet on an executed path is **MEDIUM**.

#### J. State Ownership & Invariants Verification (Conditional)

Only when `plan.md` contains a `## State Ownership & Invariants` section
(written by `/ms.plan` Step 3.4). Skip entirely otherwise — but if the diff
introduces a state machine or stores the same stateful fact in more than one
place while `plan.md` has no such section, raise that gap itself as a
**HIGH** finding (a required plan-time gate was skipped) and review the state
handling ad hoc.

Verify the implementation against the plan's declarations:

1. **Ownership**: writes to each declared stateful concept go through its
   declared owner only. `rg` for mutations of the status/state field across
   the diff — any write outside the owner is **HIGH**.
2. **Undeclared copies**: the diff introduces no new store of already-owned
   state that the plan does not declare. An undeclared writable copy is
   **HIGH**; an undeclared read-only cache is **MEDIUM**.
3. **Invariant tests**: every declared invariant has at least one test that
   can go red on violation. A missing invariant test is **HIGH** (Test-First).
4. **Transaction boundary**: mutations declared atomic actually run in one
   transaction/critical section. A multi-step mutation that can partially
   land is **HIGH**.

---

### Step 5.5: ultrathink Pattern Analysis

**ultrathink**: Analyze systemic patterns (3+ occurrences) using aggregated data from Step 5.

For each pattern: 5-Why root cause analysis → Prevention strategy → Batch fix opportunity.

---

### Step 6: Consolidate and Score

Aggregate issues from automated tools + AI analysis.

**Impact filtering**: Hide LOW issues with score <15. Promote HIGH-impact LOW to MEDIUM.

**Score**: `100 - (critical×20 + high×5 + medium×2 + low×0.5)`

#### Result Model

`/ms.review`'s final result is always one of exactly three values, computed the same way no
matter which step raises the trigger:

- **NOT READY**: at least one CRITICAL trigger fired.
- **READY WITH WARNINGS**: no CRITICAL trigger fired, but at least one WARNING trigger fired.
- **READY**: no CRITICAL or WARNING trigger fired.

Steps 6.5, 6.6, and 6.7 below each define their own domain-specific CRITICAL/WARNING triggers
(executable gates, Done Criteria, dual-agent findings) and feed this model — none of them
restate the READY / READY WITH WARNINGS / NOT READY computation independently. A later step can
only raise the result's severity, never lower one a prior step already set.

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

Run the code-level TRUST checks inline with the repository's own tooling
(coverage runner, linter, type checker, security scanner):

- coverage threshold from Constitution Section III (Test-First Implementation) or the active project threshold
- production file SLOC and function length limits
- function complexity limits
- strict typing and zero-warning lint policy
- security scan results where tooling exists
- TAG integrity report: `@SPEC -> @TEST -> @CODE`; warning by default unless Section IX or CI promotes it

#### C. Gate Result Handling

Per the Result Model (Step 6): a CRITICAL trigger fires if executable gates fail CRITICAL.
Unresolved HIGH review findings (non-gate) are a WARNING trigger, never a CRITICAL one — persist
them to `.specify/review-state.txt` and the warning summary for `/ms.fin` acknowledgement. This
is the single severity→trigger mapping: CRITICAL finding or CRITICAL gate failure → CRITICAL
trigger; HIGH/MEDIUM findings → WARNING trigger; no other step redefines it. TAG-only findings
are not a CRITICAL trigger unless Section IX or CI explicitly promotes TAG integrity to blocking. If all executable gates and deep review checks pass, neither trigger
fires; remove stale `.specify/review-state.txt` if it exists.

**Record stop-gate evidence** (the Stop hook from `/ms.init` Step 2.7b blocks turn-end without
it when code changed): record the executable-gate outcome you **actually observed** in this
step — `PASS`, `WARN`, or `FAIL` as the gates reported; `UNAVAILABLE` only when the tooling
could not run at all. Never record a verdict you did not observe.

```bash
[ -x .specify/scripts/bash/specter-stop-gate.sh ] && .specify/scripts/bash/specter-stop-gate.sh record review <PASS|WARN|FAIL|UNAVAILABLE>
```


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
     dashboard, anything not scriptable from this session). **Every MANUAL classification
     carries a one-line justification** (why it cannot be scripted from this session); a
     criterion classified MANUAL without one is treated as an unexecuted RUNNABLE — a CRITICAL
     trigger, same as a failing one. Classification is host-judged, so it is deliberately
     exposed to challenge: both Step 6.7 reviewers receive this table and are prompted to flag
     misclassified MANUAL rows.
3. **Construct the check** (how, not just "execute it") — pick the lightest rung that gives a
   tight, red-capable signal for this criterion's class, roughly in this order: a failing test at
   the seam that reaches it → a curl/HTTP script against the running dev server → a CLI
   invocation diffing output against a known-good fixture → a headless browser script (Playwright
   via the `webapp-testing` skill) driving the UI and asserting on DOM/console/network → replay
   of a captured trace → a throwaway harness exercising just this code path. Whatever rung is
   used, the check must be: reproducible (same verdict every run), fast (seconds, not minutes),
   and actually capable of going red on this specific criterion — not "ran without erroring".
4. **Execute every RUNNABLE criterion for real**: start the actual entrypoint (the daemon,
   server, or CLI the Feature ships — not a mock), drive the affected flow, and observe the
   actual behavior. This is a bounded smoke of the product path, not a load test — kill any
   long-running process (server, watcher) once its criterion has been observed. For web-UI done
   criteria, use the `webapp-testing` skill to drive the browser and capture screenshot/console
   evidence instead of asserting on a green test run alone — if this Feature used
   `design-baseline` (`/ms.implement` Step 1.6), the same screenshot also confirms the design
   tokens actually render, not just that the files exist on disk.
5. **Phase E2E scenario**: if this Feature is a Phase's last Feature (per the Feature Map DAG),
   also execute that Phase's end-to-end scenario as one additional RUNNABLE criterion.
6. **Record results** in a table, included in the Step 7 review report. Evidence for a
   RUNNABLE row is machine-checkable: the **exact command executed and the observed
   output/exit code**, never a prose summary ("worked fine" is not evidence). MANUAL rows
   carry their classification justification instead:

   | Criterion | Class | Result | Evidence |
   | --- | --- | --- | --- |
   | ... | RUNNABLE \| MANUAL | PASS \| FAIL \| MANUAL | exact command + observed output/exit code, or the MANUAL justification |

7. **Gate**: any RUNNABLE criterion with Result `FAIL` is a CRITICAL trigger in the Result Model
   (Step 6) — the same severity as a failing executable gate in Step 6.5. Do not let a green
   lint/type/test/build run mask a product that does not actually start or work.
8. **Report MANUAL items** in the Korean report (Step 7) as an explicit checklist so the user's
   own real-device/manual testing loop has a concrete list to work from:
   ```text
   📋 수동 확인 필요
   - <criterion>: <디바이스/환경> — <확인 절차> — 기대 결과: <expected>
   ```

For T3, execute every applicable identifier in
`receipt.tier_settings.targeted_checks`. In particular, the policy's
real-entrypoint/E2E module is not satisfied by a narrower unit check. Produce
executable evidence wherever the repository can exercise the selected module.

**Optional knob** (document only, not the default): `--runtime-agent=agy` delegates this step's
execution to Antigravity instead of the host, so an independent party (not the implementer) drives
the product. The default stays host-run. Do not enable this by default until the Antigravity
hardening work (external-agent preflight/degrade rule) has proven agy stable in this environment.

---

### Step 6.6b: Migration Rollback & Failure Analysis (conditional, human-ack)

Code bugs are free to fix; data bugs destroy state permanently. When this Feature's diff
includes schema/data migrations (files under the migrations dir — `db/migrations/`,
`alembic/versions/`, `prisma/migrations/` — or `CREATE/ALTER/DROP TABLE` DDL anywhere),
produce this analysis and get the user's explicit ack. **No migration in the diff → skip
this step silently.**

Answer three questions, concretely, from the actual migration content (not generically):

1. **롤백하면 무슨 일이 일어나는가** — does a down/reverse path exist at all? Running it
   loses which data (columns dropped, rows transformed)? If there is no down path, say so
   in bold — "롤백 불가" is a fact the human must see before merge.
2. **중간에 실패하면 기존 행들은 어떻게 되는가** — does this run in a transaction on this
   database (DDL transactionality differs by DB)? A mid-failure leaves what partial state,
   and is the migration re-runnable from that state (idempotent) or wedged?
3. **비가역 연산 플래그** — explicitly list any: `DROP` of tables/columns, type/nullability
   narrowing against existing rows, in-place data transforms, and **re-encryption or
   re-keying of stored secrets** (decryption under a rotated key is cryptographically
   unrecoverable — see ops-debugging C2; this class has destroyed real data before).

Present the analysis in the Korean report and **wait for the user's explicit ack**. An
unacknowledged migration analysis is a CRITICAL trigger in the Result Model (Step 6) — the
review cannot reach READY past an unread rollback story, exactly as it cannot past a failing
runtime check. Record the analysis + ack in the Step 7 review report.

---

### Step 6.7: Dual-Agent Code Review

Invoke both Codex and Antigravity after the local CI and TRUST gates have
produced enough context. T1 retains both reviewers. Both agents always run
`--fresh` in adversarial mode and receive the Done Criteria Execution table.

#### 0. External Agent Preflight (session-level, once)

Apply the Preflight and Degrade Rule from
`.claude/skills/specter-agent-protocols/SKILL.md` (§1–2). For this command: a **dual-agent
station** — if one agent is unavailable after preflight + one retry, run it single-agent, cap
the station result at `WARN`, and write the §2 degrade placeholder report (`**Result**: WARN`
+ `**Availability**: UNAVAILABLE (<reason>)`) at the missing agent's report path
(`docs/review/{spec-id}.codex-review.md` / `{spec-id}.antigravity-review.md`). Never present
a single-agent run as dual. Zero independent reviewers stops the station. Under
T3, any single-agent environmental degrade or recusal WARN requires explicit
human acknowledgment before advancement.

**Implementer recusal**: before dispatch, check `specs/{spec-id}/implementation-notes.md`
for an `External implementation:` record (written by `/ms.implement` when the user approved
delegating implementation). If the recorded agent is one of this station's reviewers, recuse
it for this Feature: run the station single-agent with the other agent, cap the station
result at `WARN`, and write a degrade placeholder report (`**Result**: WARN` +
`**Availability**: RECUSED (implemented this Feature)`) at the recused agent's report path.
Self-review is never dual review.

#### A. Codex & Antigravity Code Review (same prompt body, different agent)

```text
/codex:rescue --fresh --model gpt-5.6-luna --effort <receipt.tier_settings.reviewer_effort.codex> <prompt>
/antigravity:rescue --fresh --model gemini-3.5-flash --effort <receipt.tier_settings.reviewer_effort.antigravity> <prompt>
```

Both agents must read:
- `.specify/memory/constitution.md`
- `AGENTS.md` if it exists
- `specs/[spec-id]/spec.md`
- `specs/[spec-id]/plan.md`
- `specs/[spec-id]/tasks.md`
- `specs/[spec-id]/implementation-notes.md` if it exists (logged plan deviations)
- `docs/prd/checklists/feature-NNN.checklist.md`
- the Step 6.6 Done Criteria Execution table (RUNNABLE results and evidence)
- the current git diff against the review base
- changed production files and changed tests
- `.specify/audit-tiers/feature-NNN.json`

Each writes its own report: Codex → `docs/review/{spec-id}.codex-review.md`; Antigravity →
`docs/review/{spec-id}.antigravity-review.md`.

Prompt template — substitute `{AGENT}` (`Codex` / `Antigravity using Google Antigravity`),
`{MODE}` (`codex-adversarial-code-review` / `antigravity-adversarial-code-review`), and
`{REPORT_PATH}` (that agent's report path above):

```text
You are performing an advisory SPECTER post-implementation code review as {AGENT}.

Review the current implementation against spec.md, plan.md, tasks.md,
Constitution, AGENTS.md, and the changed code/tests. Do not edit files except
writing {REPORT_PATH}.

Focus on:
- implementation drift from spec/task intent
- missing or weak behavior tests
- auth, authorization, input validation, logging, and sensitive data exposure
- data loss, race condition, rollback, idempotency, and migration risks
- overcomplicated abstractions or non-surgical changes
- architecture violations against plan.md
- Done Criteria rows classified MANUAL that are actually scriptable from this
  environment (a misclassified MANUAL hides an unexecuted runnable check —
  challenge the classification, citing how you would script it)
- the exact receipt-bound scope: {receipt.tier_settings.review_scope}
- every applicable identifier in
  `{receipt.tier_settings.targeted_checks}`; reviewers do not add or remove
  policy modules

Always challenge whether the implementation approach is simpler, safer, or
better scoped than available alternatives.

Write:

# {AGENT} Code Review

**Mode**: {MODE}
**Feature**: Feature {NNN}
**Result**: PASS | WARN | FAIL

## Findings

| Severity | Finding | Evidence | Required Fix |
| --- | --- | --- | --- |

## Verdict

One concise paragraph.

Also echo the finished report between ===REPORT BEGIN=== and ===REPORT END=== markers in your
final message, verbatim, so it can be salvaged if the file write fails.
```

If the user supplied `--background`, add `--background` to both invocations. Do
**not** offload a "rerun `/ms.review` later" onto the user: per
`specter-agent-protocols` §9 a detached agent never self-notifies, so launch a
harness-tracked waiter — a `Bash(run_in_background: true)` poll loop on the two
review report paths (`*.codex-review.md` / `*.antigravity-review.md`), or
`status --wait` — that wakes the host when both reports appear, then continue to
aggregation in the same session.

**Report-Write Protocol**: apply `specter-agent-protocols` §3 — deterministic file check
(exists, non-empty, contains `**Result**:`), retry once, salvage from the
`===REPORT BEGIN===`/`===REPORT END===` markers. If no markers exist either, that is an
**agent-authored failure**: leave the report missing/invalid for the aggregation to grade
`FAIL` (§3 step 3) — the subsection-0 Degrade Rule applies only to preflight failures,
never to an agent that ran.

#### B. Layer-3 Aggregation (mechanical — feeds the Result Model, Step 6)

If `--background` was used and either report file has not appeared yet, do
**not** run the aggregation against a missing report. Hold for the
`specter-agent-protocols` §9 waiter instead: `PENDING` is interim status only —
keep the harness-tracked waiter in place and resume aggregation when woken on
both reports' appearance; never end the turn to hand the recheck back to the
user. Once both reports exist, compute the agent-station verdict mechanically:

```bash
.specify/scripts/bash/specter-gate.sh aggregate review {spec-id} --ledger --round <R>
```

`<R>` is the current §4 convergence round and must not exceed
`receipt.tier_settings.max_automatic_rounds`. Every round is a fresh-context
run.

The receipt verdict maps to the Result Model with no host re-weighing
(`specter-agent-protocols` §5 no-unilateral-host-downgrade):

- `PASS`: no trigger.
- `WARN`: WARNING trigger. The host never explains a warning away as a false
  positive — a disputed finding goes to a scoped §4 re-round (`--fresh`, prior
  findings passed as report file paths), where only the reviewing agent may
  revise its own grade against changed evidence.
- `FAIL`: CRITICAL trigger, final under the same re-round-only rule.

#### C. Convergence Policy (re-round caps)

Apply the receipt-bound Convergence Policy from `specter-agent-protocols` §4
(T1 currently at most 2 rounds; T2/T3 currently at most 3; Round 2+ scoped to
failing findings only; stop when only WARNs remain). A budget-exhausted FAIL
remains FAIL. Record every residual WARN in `docs/review/` and
`.specify/review-state.txt`.

If aggregation reports `warn_ack_required: true`, stop and display the
receipt-bound reasons and cap. Only after explicit human acknowledgment run:

```bash
python3 .specify/scripts/python/classify_audit_tier.py \
  --policy .specify/policies/audit-tier-policy.json acknowledge-warn \
  --feature <NNN> --station review --actor human
.specify/scripts/bash/specter-gate.sh aggregate review {spec-id}
```

Advance only when `warn_ack_satisfied` is true. This acknowledgment is
auditable and cannot be supplied by the host or either reviewer.

---

### Step 7: Report Generation

```bash
mkdir -p docs/review
REPORT_FILE="docs/review/review_${AGENT_NAME:-Claude}_$(date +%y%m%d-%H%M%S).md"
```

`AGENT_NAME` is `Claude`, or `Gemini` if running under `GEMINI_SESSION`. `$REPORT_FILE` is reused
by Step 9's state file and the Run-State Ledger append below.

Report structure (console + file):

- Summary: CRITICAL/HIGH/MEDIUM/LOW counts, overall score, Codex review result
- Audit tier, policy hash, receipt phase/hash, and every classification reason
- Intent & Focus Charter (inline copy of Step 2.5 so report is self-contained)
- Done Criteria Execution table (from Step 6.6) plus the "📋 수동 확인 필요" MANUAL checklist
- Production Risks, Strategic Unlocks, Quick Wins
- Coverage Checklist
- Hidden LOW issues count (show with `--verbose`)

---

### Step 8: Interactive Actions

**Only if HIGH/CRITICAL issues exist**, prompt user:

- Do NOT attempt to auto-fix issues. Leave fixes to `/ms.implement --mode=refactor` or the main conversation.
- Ask user if they want to abort to fix the issues manually.
- Or continue without fixes (flagged in `/ms.fin`)

---

### Step 9: Cleanup and State Management

Remove transient analysis artifacts — `.specify/review-rg.ndjson`, `review-patterns.json`,
`review/{jscpd,eslint,radon}.json`, and the hash-diff scratch files — while keeping
`review-hash.cache` so the next run can still diff against it. If unresolved CRITICAL or HIGH
issues remain, write `.specify/review-state.txt` with their counts, a note to rerun `/ms.review`,
and `$REPORT_FILE`'s path; otherwise remove any stale `review-state.txt`.

**State policy**: `.specify/review-state.txt` is a visibility artifact for
`/ms.fin`, not a mandatory publish blocker. Executable gate failures
inside `/ms.review` remain blocking for the review result itself.

- **Artifact Policy**
  - Persists: `.specify/review-hash.cache` (used for hash-based diffing on the next run)
  - Removed: `.specify/review/*.json`, `.specify/review-rg.ndjson`, transient hash files
  - Reports: `docs/review/review_{agent}_{timestamp}.md` kept for audit trail

**Run-State Ledger** (bookkeeping, not a gate): the **agent-station** line was already emitted
mechanically by Step 6.7-B's `aggregate --ledger` (verbatim `caught`, mechanical `cap` — the
host never authors it). `/ms.review` is a composite station, so the host appends one **final**
composite line on top (append-only; the later entry supersedes for conductor resume), with
`verdict` set to `PASS` (READY), `WARN` (READY WITH WARNINGS), or `FAIL` (NOT READY) — this
composite verdict folds in the executable gates and Done Criteria results, which the aggregate
line cannot see. Per §7's composite rule, the line must embed the mechanical receipt's verdict
verbatim as `"agents_verdict"` and may only equal or worsen it — never soften:

```bash
mkdir -p .specify
printf '{"ts":"%s","cycle":"feature","feature":"%s","step":"review","verdict":"%s","agents_verdict":"%s","artifacts":["%s"]}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "<NNN>" "<PASS|WARN|FAIL>" "<the aggregate receipt verdict, verbatim>" "$REPORT_FILE" >> .specify/specter-run.jsonl
```

On `WARN`/`FAIL`, extend the JSON with `caught` — an array of short **verbatim quotes** from
the review report, one per real finding (never paraphrase or re-grade; `[]` if the non-PASS
verdict carried no content finding) — and, only when the verdict was capped by an
environmental degrade rather than by findings, `cap` with the reason (e.g.
`"single-agent-degrade"`). PASS lines stay minimal. Re-rounds overwrite report files; this
ledger line is where the original catch survives for gate-value audits. Example:

```json
{"ts":"…","cycle":"feature","feature":"006","step":"review","verdict":"WARN","agents_verdict":"WARN","artifacts":["…"],"caught":["dispatch path lacks timeout (HIGH)"],"cap":"single-agent-degrade"}
```

**Close the stop-gate phase** on a `PASS` or `WARN` verdict (a `FAIL` verdict keeps the phase
open — the feature is not done, and subsequent fix turns stay gated):

```bash
[ -x .specify/scripts/bash/specter-stop-gate.sh ] && .specify/scripts/bash/specter-stop-gate.sh phase clear
```

---

## User Options

| Flag | Effect |
| --- | --- |
| `--verbose` | Show all LOW issues, including those the impact-score filter (<15) would normally hide. Useful for a complete code audit. |
| `--background` | Start Codex/Antigravity in the background; rerun `/ms.review` after both reports appear. |
| `--raise-audit-tier T2|T3` | Record a manual upward-only override through the deterministic classifier. |
| `--runtime-agent=agy` | Delegate Step 6.6's Done Criteria Execution to Antigravity instead of the host. A documented knob, not a default — keep host-run until Antigravity has proven stable in this environment. |

> The dual-agent review always runs in adversarial mode — both Codex and
> Antigravity challenge design choices, simpler/safer alternatives, and hidden
> risks. There is no flag to toggle this; it is the default behavior.

---

## Integration with Workflow

After `/ms.implement`, run `/ms.review`. If it finds HIGH/CRITICAL issues, fix them
(`/ms.implement --mode=refactor` or by hand) and re-review until clean, then run `/ms.fin`.

`/ms.fin` treats `.specify/review-state.txt` as advisory, never a mandatory publish blocker: if it
exists, `/ms.fin` surfaces its unresolved CRITICAL/HIGH counts, the latest report path, and the
review timestamp as a warning, then continues.

---

## Difference from Other Commands

| Command | Purpose | Checks | When to Run |
|---------|---------|--------|-------------|
| `/ms.pre-verify` | Global Feature Map gate | PRD coverage, Feature ownership, DAG, stub-forward, template completeness | After `/ms.featuremap-checklist`, before `/ms.constitution` |
| `/ms.checklist` | Per-Feature gate | Selected Feature PRD fidelity, ownership, scope, done criteria | After `/ms.constitution`, before `/ms.verify` |
| `/ms.verify` | Per-Feature dual-agent gate | Concise Codex & Antigravity check of the Feature checklist | After `/ms.checklist`, before `/ms.specify` |
| `/ms.analyze` | Pre-implementation document gate | spec ↔ plan ↔ tasks consistency, Constitution alignment, drift detection | Before `/ms.implement` |
| `/ms.review` | Post-implementation code gate | Design review, Done Criteria Execution (runs the real entrypoint), Codex and Antigravity reviews, lint/types/tests/build, coverage, security, TAG integrity | After `/ms.implement` |
| `/ms.fin` | Final commit | Review-state acknowledgement, docs sync, commit, push, PR | After `/ms.review` passes |

**Mental model**:
- `/ms.pre-verify` = "Did the PRD become the right Feature Map?"
- `/ms.checklist` = "Is this Feature ready to become a spec?"
- `/ms.verify` = "Did the two independent reviewers find blocking checklist issues?"
- `/ms.analyze` = "Are the implementation documents coherent enough to build?"
- `/ms.review` = "Is the implemented branch ready to publish?"
- `/ms.fin` = "Commit, push, and open/update the PR."

---

## Error Handling

- **No implemented files** (`src/`, `tests/` both missing): report it and direct the user to run
  `/ms.implement` first.
- **Missing required documents**: `spec.md` or `plan.md` absent is blocking — do not proceed
  (same rule as Step 1); direct the user to `/ms.specify` / `/ms.plan`. Optional context files
  (e.g. `implementation-notes.md`) may be absent — note the skipped checks and continue.
- **Optional tool missing** (e.g. `jscpd`): skip that specific check, note the install command
  (e.g. `npm install -g jscpd`), and continue with the rest of the review.

---

# Project Constitution: {PROJECT_NAME}

---

## Preamble

This Constitution establishes the foundational principles for {PROJECT_NAME}. All architectural decisions, code changes, and feature implementations must align with these principles. Deviations require explicit justification and user approval.

---

## Core Principles

### I. Test-First Development (NON-NEGOTIABLE)

**Rule**: All functionality must have tests written before implementation.

**Rationale**:

-   Test-Driven Development ensures better design through interface-first thinking
-   Prevents regression bugs
-   Serves as living documentation
-   Forces consideration of edge cases upfront

**Process**:

1. Write failing test
2. Implement minimum code to pass
3. Refactor while keeping tests green

**Enforcement**:

-   Phase 3.2 (Tests) must complete before Phase 3.3 (Implementation)
-   `/ms.analyze` Level 2 validates test coverage ≥85% (CI/CD blocking)
-   Coverage < 85% blocks `/ms.implement` execution

**Exceptions**: None. This is an absolute rule.

**Metrics**: Minimum 85% test coverage across the codebase.

---

### II. Simplicity-First Architecture

**Rule**: Choose the simplest solution that solves the current problem. Avoid premature optimization and over-engineering.

**Complex Patterns to Avoid (unless proven necessary)**:

-   Microservices architecture
-   Event sourcing / CQRS
-   Kubernetes (start with simpler deployment)
-   GraphQL (when REST suffices)
-   Custom frameworks
-   Distributed transactions

**Tool Usage Philosophy**:

✅ **Prefer External Tools Over Reimplementation**:

-   Use ESLint/Pylint for complexity analysis (AST-based)
-   Use ripgrep for code search (regex-based)
-   Use TypeScript compiler API for type checking (AST-based)
-   Use git for version control (not custom DB)

❌ **Avoid Building What Already Exists**:

-   Don't write custom AST parsers when `@typescript-eslint/parser` exists
-   Don't write custom regex engines when ripgrep exists
-   Don't write custom type checkers when `tsc` exists

**Decision Framework**:

```
Does a mature, well-maintained tool exist?
├─ YES → Use it (even if AST-based)
└─ NO → Build simplest solution (prefer regex over custom AST)
```

**Rationale**:

-   Simplicity = leveraging existing robust tools
-   AST parsers (ESLint, TSC, ast stdlib) are **already dependencies**
-   Building custom parsers is **more complex** than using existing ones

---

**AST Parser Usage Policy** (4 Safety Models):

**Allowed Use Cases**:

1️⃣ **Read-only Mode**

-   Code analysis, metrics extraction, complexity measurement
-   Example: ESLint complexity rules, code navigation
-   Safety: No code modification, no side effects

2️⃣ **Sandboxed Transformation**

-   Parse → Clone AST → Modify clone → Generate new code
-   Original code untouched, transformation isolated
-   Example: Code refactoring, auto-formatting
-   Safety: Original preserved, changes reviewable before applying

3️⃣ **Sandbox AST Execution**

-   Execute AST in restricted environment with no built-ins
-   No access to file system, network, or external functions
-   Example: Safe expression evaluation, config validation
-   Safety: Isolated VM, no escape to host system

4️⃣ **AST Diffing**

-   Compare two AST versions to detect structural changes
-   Example: Code review automation, test change detection
-   Safety: Read-only comparison, no modifications

**Enforcement**:

-   All AST usage must follow one of the 4 models above
-   Document which model is used in code comments
-   Code review verifies safety model compliance

**Approved AST Libraries** (already safe):

-   TypeScript: `@typescript-eslint/parser` (read-only, sandboxed)
-   Python: `ast` module (read-only, sandboxed)
-   JavaScript: `acorn` (read-only parser)
-   Go: `go/parser` (stdlib, read-only)

---

**Decision Framework**:

```
Can the problem be solved with:
1. Plain functions/methods? → Use them
2. Existing libraries? → Use them
3. Standard patterns? → Use them
4. Custom solution needed? → Document why

Only proceed to next level if previous fails.
```

**Rationale**:

-   Faster iteration in early stages
-   Lower cognitive load for team
-   Easier debugging and maintenance
-   Complexity can be added later when bottlenecks are proven

**Enforcement**:

-   `/plan` phase includes Complexity Check
-   Architectural decisions require written justification
-   Regular complexity audits

**Exceptions** (require user approval):

-   Proven performance bottleneck (with metrics)
-   Explicit business requirement (e.g., compliance)

**File Size Limits**:

**Documentation Directories** (NO LIMIT):

-   `specs/` - Spec-Kit specifications
-   `docs/` - Project documentation
-   `.specify/` - Spec-Kit metadata
-   `.claude/commands/` - Command prompts (special case: these ARE code for AI agents)

**Documentation Files** (NO LIMIT):

-   `.md` - Markdown files
-   `.txt` - Plain text files

**Production Code Files** (≤700 SLOC):

-   All files in `src/`, `lib/`, `app/` directories (production code)

**Test Files** (NO LIMIT):

-   All files in `tests/` directories — case coverage is prioritized over file length
-   SLOC = Source Lines of Code (excluding comments and blank lines)

**Rationale**:

-   Detailed documentation improves implementation quality
-   700 SLOC allows substantial production modules without forcing artificial splits; test files have NO limit so coverage is never sacrificed to length
-   Complexity metrics (≤10 per function) ensure maintainability
-   Command prompts are executable instructions for AI agents, thus treated as code

---

### Change Discipline (Surgical Changes)

**Rule**: Touch only what the task requires; clean up only your own mess.

-   Don't "improve" adjacent code, comments, or formatting; match the existing style.
-   Don't refactor what isn't broken. Notice unrelated dead code → mention it, don't delete it.
-   Remove only the imports/variables/functions that YOUR change orphaned; leave pre-existing dead code unless asked.
-   Every changed line must trace directly to the request.
-   **Senior test** (Simplicity): "Would a senior engineer call this overcomplicated?" If yes, simplify. No speculative abstractions, no flexibility/configurability that wasn't requested, no error handling for cases that cannot occur.

Planned refactors (splitting >700-SLOC files, migrating to shared primitives, TRUST gates) are **explicit tasks**, not silent side-effects — surgical discipline applies within each task's own scope.

---

### III. Modular Design (Library-First)

**Rule**: Every feature starts as an independently testable module with clear boundaries.

**Characteristics of Good Modules**:

-   Single, well-defined responsibility
-   Can be tested without external dependencies
-   Clear input/output contract
-   No global state dependencies
-   Reusable across contexts

**Anti-Patterns**:

-   God objects (modules doing everything)
-   Hidden dependencies
-   Tightly coupled components
-   Utility modules (catch-all for unrelated functions)

**Enforcement**:

-   `/ms.analyze` Level 3 checks module cohesion
-   `/ms.plan` phase requires module structure
-   Automated dependency analysis in CI

**Exceptions**:

-   Trivial utilities (<10 lines)
-   Prototype/spike phase (must refactor before merge)

---

### IV. Requirements Clarity (GEARS Standard)

**Rule**: All requirements MUST follow the **GEARS** syntax to eliminate ambiguity. GEARS (Generalized EARS) is the canonical requirement syntax; classic EARS is a **legacy-compatible subset** (mechanically convertible, not "wrong"), retained for reference and external input only.

**Language Policy (My-Spec)**:

-   ✅ User inputs requirements in **Korean** (natural language)
-   ✅ The spec system converts Korean → **English GEARS**
-   ✅ ALL workflow documents written in **English only** (spec.md, plan.md, tasks.md, code, tests, docs)
-   ✅ GEARS keywords (Where/While/When) and `shall` remain in **English**

**Canonical form**:

```
[Where <static condition>]   # configuration / feature flag / deploy environment / permission
[While <runtime state>]      # job running / session active / connection open / edit mode
[When <trigger>]             # triggering event, including error / exceptional events
the <subject> shall <behavior>.
```

Clauses are optional, but when present MUST appear in this fixed order. GEARS maps 1:1 to Given-When-Then: `Where + While → Given`, `When → When`, `shall → Then`.

**Example Conversion**:

```
Korean Input (user):
"사용자가 유효한 자격증명으로 로그인하면, 시스템은 JWT 토큰을 발급해야 한다"

GEARS Output (spec.md):
"When a user submits valid credentials, the auth service shall issue a JWT session token."
```

(Note the concrete subject `the auth service`, not `the system`.)

**Rules (R1–R8)**:

-   **R1 — Subject**: use a concrete, implementable unit (`the upload service`, `the chat API`) that narrows responsibility. Use `the system` only when the requirement is genuinely product-wide.
-   **R2 — Where**: static applicability only — configuration, feature flag, deployment environment, permission/role.
-   **R3 — While**: runtime state only — job running, session active, connection open, edit mode.
-   **R4 — When**: triggering events, **including error and exceptional events**.
-   **R5 — No classic `IF...then`**: express exceptions with a category label, e.g. `[Error Handling] When <event>, the <subject> shall <behavior>.`
-   **R6 — Testability**: one requirement = one verifiable behavior, mapping to ≥1 acceptance test / task.
-   **R7 — `shall` is lowercase** canonical; validators are case-insensitive (legacy `SHALL` accepted).
-   **R8 — Invalid (review ERROR)** when: clause order is violated, subject or behavior is missing, or a forbidden vague phrase is present.

**Category labels** (preserve semantics GEARS strips from syntax): `[Error Handling]`, `[Security]`, `[Performance]`, … — optional prefix placed before the clauses.

**Compatibility layers** (role separation — never mix syntaxes within one block):

| Area | Syntax |
| --- | --- |
| External input (PRD / stakeholder) | free-form; classic EARS allowed |
| High-level requirements | GEARS (loose ok) |
| Acceptance criteria | **strict GEARS** |
| Test scenarios | Given-When-Then |
| Legacy EARS specs | frozen; convert to GEARS on next edit |

**Migration (EARS → GEARS)**:

-   `the system` → concrete subject (narrow to an implementable unit — not a blind rename)
-   `IF...then` → `[Error Handling] When …`
-   `WHERE … MAY` (optional) → `Where <static condition>, … the <subject> shall …`
-   `WHILE` → `While <runtime state>, … the <subject> shall …`

**Forbidden Phrases**:

-   ❌ "can", "could", "might" (ambiguous → clarify with Where/When)
-   ❌ "should", "would be good" (→ make it a Where-gated `shall`)
-   ❌ "fast", "secure", "safe", "user-friendly" (not measurable → provide a specific metric/behavior)

**Measurability Principle**: every requirement must answer "When is this satisfied? / How is it tested? / How do we judge success or failure?"

**Enforcement**:

-   `/ms.clarify` and `/ms.review` validate GEARS (R1–R8)
-   `/ms.analyze` checks subject/condition/trigger/behavior completeness + Given-When-Then mappability
-   AI detects non-GEARS requirements and suggests rewrites
-   All FR-XXX MUST comply with GEARS

**Metrics**: 100% of functional requirements use GEARS format.

---

### V. TRUST 5 Principles (Code Quality Standards)

**Rule**: All code MUST comply with TRUST 5 principles. No exceptions without user approval.

**Foundation**: Based on MoAI-ADK TRUST methodology for systematic code quality assurance.

---

#### T - Test First

**SPEC → Test → Code Cycle**:

1. ✅ SPEC written with @SPEC:ID tag
2. ✅ RED: Write failing test with @TEST:ID
3. ✅ GREEN: Implement minimum code to pass (@CODE:ID)
4. ✅ REFACTOR: Improve quality while keeping tests green

**Coverage Requirements**:

-   ✅ Overall coverage ≥85% (MANDATORY)
-   ✅ New code coverage 100% (RECOMMENDED)
-   ✅ Critical paths 100% (authentication, payment, security)

**Enforcement**:

-   CI/CD blocks merge if coverage < 85%
-   `/ms.analyze` Level 2 validates test existence
-   Coverage < 85% blocks `/ms.implement` execution

**No Exceptions**: Test-first is NON-NEGOTIABLE.

---

#### R - Readable

**Size Constraints**:

-   ✅ Production file ≤700 SLOC (Source Lines of Code, excluding comments and blank lines)
-   ✅ Test file SLOC: NO LIMIT (case coverage prioritized over file length)
-   ✅ Function ≤100 LOC (Lines of Code, excluding comments)
-   ✅ Parameters ≤5 per function
-   ✅ Nesting depth ≤4 levels

**Complexity Limits**:

-   ✅ Cyclomatic Complexity ≤10 per function
-   ✅ Cognitive Complexity ≤15 per function

**Rationale**:

-   100 LOC functions: Sufficient for complex algorithms without excessive splitting
-   700 SLOC production files: Allows substantial modules without forcing artificial splits
-   Test files: NO LIMIT to ensure complete coverage in a single file where natural
-   Complexity limits: More important than line count for maintainability

**Naming Conventions**:

-   ✅ Use domain language from spec.md
-   ✅ Functions: verb + noun (e.g., `validateUserInput`, `fetchOrderData`)
-   ✅ Variables: descriptive nouns (e.g., `userId` ✅, `uid` ❌)
-   ✅ No abbreviations unless industry-standard (API, HTTP, JWT ✅)

**Enforcement**:

-   ESLint/Pylint rules: `max-lines`, `max-statements`, `complexity`
-   `/ms.analyze` Level 2 checks file/function size
-   Linter violations block `/ms.implement` execution

**Exceptions**:

-   Configuration files (e.g., Webpack config)
-   Generated code (mark with `@generated` tag)

---

#### U - Unified

**SPEC-Driven Architecture**:

-   ✅ All implementations start from SPEC
-   ✅ Code structure mirrors SPEC organization
-   ✅ @TAG system ensures SPEC↔Code traceability

**Type Safety**:

-   ✅ TypeScript: `strict: true` in tsconfig.json (MANDATORY)
-   ✅ Python: mypy with `--strict` flag (MANDATORY)
-   ✅ Type checking passes with zero errors

**Consistent Style**:

-   ✅ Linting passes with zero warnings
-   ✅ Unified code formatting (Prettier, Black)
-   ✅ Same patterns throughout project

**Enforcement**:

-   `tsconfig.json` or `mypy.ini` with strict settings
-   CI/CD runs type checker
-   Pre-commit hooks format code

**No Exceptions**: Type safety is MANDATORY.

---

#### S - Secured

**Input Validation**:

-   ✅ Validate ALL user inputs (regex, whitelist)
-   ✅ File upload restrictions (extension, size, MIME type)
-   ✅ Sanitize data before database queries

**Vulnerability Prevention**:

-   ✅ **SQL Injection**: Use Prepared Statements or ORM
-   ✅ **XSS**: HTML escaping, CSP headers
-   ✅ **CSRF**: CSRF tokens, SameSite cookies
-   ✅ **Passwords**: bcrypt/argon2 hashing (≥10 rounds)
-   ✅ **Secrets**: Environment variables only (NEVER hardcode)

**Security Scanning**:

-   ✅ Static analysis tools (Snyk, OWASP Dependency-Check)
-   ✅ `.env` file MUST be in `.gitignore` (CRITICAL)
-   ✅ Regular dependency updates (npm audit, pip-audit)

**Forbidden Practices**:

-   ❌ Plaintext password storage
-   ❌ `eval()` or `exec()` with user input
-   ❌ Disabled SSL/TLS verification
-   ❌ Weak encryption (MD5, SHA1)

**Enforcement**:

-   `/ms.analyze` Level 3 runs security scan (Snyk, OWASP)
-   `npm audit` / `pip-audit` in CI/CD
-   HIGH/CRITICAL vulnerabilities block execution

---

#### T - Trackable

**@TAG System (CODE-FIRST Principle)**:

-   ✅ Complete traceability chain: `@SPEC → @TEST → @CODE → @DOC`
-   ✅ Every code file has TAG block (inserted by `/ms.implement`)
-   ✅ ripgrep-based TAG scanning (no intermediate database)

**TAG Integrity**:

-   ✅ No orphaned TAGs (TAG exists but file missing)
-   ✅ No duplicate TAG IDs (unique across project)
-   ✅ Complete chains (every @SPEC has @TEST and @CODE)

**TAG Validation**:

```bash
# Scan all TAGs
rg '@(SPEC|TEST|CODE|DOC):' -n

# Find orphaned TAGs
rg '@CODE:AUTH-001' -l  # Should return at least one file
```

**Enforcement**:

-   `/ms.analyze` Level 3 checks TAG integrity
-   CI/CD validates TAG chains
-   `/ms.implement` auto-inserts TAG blocks

**TAG Block Format** (auto-generated):

```typescript
/**
 * @CODE:AUTH-001
 * @SPEC: specs/001-auth-spec/spec.md
 * @TEST: tests/auth/service.test.ts
 * @CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
 * @STATUS: implemented
 * @CREATED: 2025-10-10
 * @UPDATED: 2025-10-10
 */
```

---

**TRUST Metrics Summary**:

| Principle  | Metric              | Threshold | Enforcement      |
| ---------- | ------------------- | --------- | ---------------- |
| Test First | Coverage            | ≥85%      | CI/CD blocking   |
| Readable   | File size           | ≤700 SLOC prod / test: no limit | Linter rules     |
| Readable   | Function size       | ≤100 LOC  | Linter rules     |
| Readable   | Complexity          | ≤10       | Linter rules     |
| Unified    | Type errors         | 0         | CI/CD blocking   |
| Unified    | Lint warnings       | 0         | CI/CD blocking   |
| Secured    | High/Critical vulns | 0         | Security scan    |
| Trackable  | Orphaned TAGs       | 0         | `/ms.analyze` L3 |
| Trackable  | Duplicate TAGs      | 0         | `/ms.analyze` L3 |

**Validation Command**:

```bash
/ms.analyze  # Runs full TRUST validation (3 levels)
```

---

### VI. Explicit Over Implicit

**Rule**: Code behavior must be explicit and predictable. Avoid "magic" and hidden side effects.

**Practices**:

-   ✅ Explicit function parameters over global state
-   ✅ Named constants over magic numbers
-   ✅ Descriptive variable names over abbreviations
-   ✅ Explicit error handling over silent failures
-   ✅ Direct dependencies over hidden coupling

**Anti-Patterns**:

-   ❌ Modifying parameters as side effects
-   ❌ Global variables affecting behavior
-   ❌ Framework "magic" without understanding
-   ❌ Implicit type conversions
-   ❌ Hidden configuration files

**Example**:

```javascript
// ❌ Bad: Implicit, side effects
function processUser(user) {
    user.processed = true; // Mutation
    globalConfig.lastUser = user.id; // Side effect
    return user;
}

// ✅ Good: Explicit, pure
function processUser(user, config) {
    return {
        ...user,
        processed: true,
        processedAt: new Date(),
        processedBy: config.systemId,
    };
}
```

**Rationale**: Explicit code is easier to understand, test, debug, and maintain.

---

### VII. Security by Default

**Rule**: Security is not optional. All features must consider security from the start.

**Mandatory Practices**:

-   ✅ Input validation and sanitization
-   ✅ Authentication required (unless explicitly public)
-   ✅ Authorization checks before data access
-   ✅ Secrets in environment variables (never in code)
-   ✅ HTTPS for all external communication
-   ✅ SQL parameterization (prevent injection)
-   ✅ Content Security Policy headers
-   ✅ Rate limiting on public endpoints

**Forbidden**:

-   ❌ Passwords in plaintext
-   ❌ Eval / exec with user input
-   ❌ Disabled CORS (configure properly instead)
-   ❌ Disabled SSL verification
-   ❌ Weak cryptographic algorithms (MD5, SHA1)

**Enforcement**:

-   `/ms.analyze` Level 3 runs automated security scan
-   CI/CD runs security checks (`npm audit`, `pip-audit`)
-   Regular dependency vulnerability checks

**When Unsure**: Default to more restrictive and document why.

---

### VIII. Documentation as Code

**Rule**: Documentation lives with the code and updates with changes.

**Required Documentation**:

-   README with setup instructions
-   API contracts (OpenAPI/Swagger)
-   Architecture Decision Records (ADRs) for major choices
-   Inline comments for complex logic (not obvious code)
-   CHANGELOG for user-facing changes

**Anti-Patterns**:

-   ❌ Documentation in separate wikis (gets outdated)
-   ❌ Comments explaining "what" (code should be self-explanatory)
-   ❌ Documentation without examples
-   ❌ Outdated diagrams

**Enforcement**:

-   `/ms.analyze` checks doc-code consistency
-   User reviews documentation completeness

---

## Delivery Standards

### Definition of Done

A feature is complete when ALL criteria are met:

**Quality Checks**:

-   [ ] All acceptance criteria satisfied
-   [ ] Tests: Coverage ≥85%, all passing (unit + integration)
-   [ ] `/ms.analyze` Level 2: PASS (zero type errors)
-   [ ] Security: No HIGH/CRITICAL vulnerabilities

**Validation Gates**:

-   [ ] No regressions in existing features
-   [ ] CI/CD: All checks green
-   [ ] Performance: Benchmarks pass (if applicable)
-   [ ] User: Reviewed and approved

### Release Checklist

-   [ ] Feature sign-off obtained
-   [ ] Release notes documented
-   [ ] Rollback plan ready
-   [ ] Monitoring configured

---

## Amendment Process

### Proposing Changes

1. **Identify Need**: Document why current Constitution is inadequate
2. **Draft Amendment**: Propose specific change with rationale
3. **Impact Analysis**: Assess effect on existing code/processes
4. **User Decision**: User reviews and approves/rejects amendment
5. **Version Update**: Increment version (MAJOR.MINOR.PATCH)

### Version Semantics

-   **MAJOR**: Breaking change (removes/redefines principles)
-   **MINOR**: Additive change (new principles)
-   **PATCH**: Clarification (no behavior change)

### Amendment History

| Version | Date   | Change               | Rationale         |
| ------- | ------ | -------------------- | ----------------- |
| 1.0.0   | {DATE} | Initial Constitution | Project inception |

---

## Governance

### Enforcement Matrix

| Type          | Method                                | Frequency          |
| ------------- | ------------------------------------- | ------------------ |
| **Automated** | Linting, type checking, coverage      | Every commit       |
| **Automated** | `/ms.analyze` 3-level validation      | Pre-implementation |
| **Manual**    | User review of AI outputs             | Each phase         |
| **Manual**    | User approval for critical operations | As needed          |

### Exception Handling

**Allowed Exceptions** (with user approval):

-   Prototyping/spikes → Must refactor before merge
-   Emergency hotfixes → Create tech debt ticket
-   Impossible constraints → Requires Constitution amendment

**Exception Protocol**:

1. Document violation + rationale
2. Get user approval
3. Track in tech debt log

### Conflict Resolution

**Priority**: Security > Safety > Tests > Simplicity > Performance

If unclear → Ask user → Document as ADR

---

## IX. Project-Specific Constraints

<!-- This section is auto-generated by `/ms.constitution` command from spec.md and plan.md -->

_Auto-generated by `/ms.constitution` from spec.md and plan.md on {DATE}_

### Technology Stack

✅ **Required**:

-   {constraint 1}
-   {constraint 2}

❌ **Forbidden**:

-   {constraint 1}

### Dependencies

✅ **Required**:

-   {constraint 1}

❌ **Forbidden**:

-   {constraint 1}

### Architecture

✅ **Required**:

-   {constraint 1}

### Security

✅ **Required**:

-   {constraint 1}

### Performance

✅ **Required**:

-   {constraint 1}

---

## X. Agentic Behavior Standards

**Rule**: AI agents must operate transparently, safely, and truthfully. No deceptive or destructive behavior is permitted.

### Mandatory Confirmation Protocol

**Three-Step Verification for Destructive Operations**:

```markdown
BEFORE executing destructive operations, agent SHALL:

1. Display exact command to be executed
2. List all affected files/data with sizes
3. Request explicit confirmation: "Type YES to proceed, NO to cancel"

Example:

> About to execute: rm -rf ./src/legacy/
> This will delete 47 files (2.3MB) permanently
> Affected directories: /src/legacy/controllers/, /src/legacy/models/
> Type YES to proceed, NO to cancel: \_
```

**Production Environment Triple Lock**:

```markdown
IF environment contains "prod" OR database contains "production":

1. Display WARNING in red: "⚠️ PRODUCTION ENVIRONMENT DETECTED"
2. Show environment name 3 times
3. Require typed confirmation: "I understand this is PRODUCTION"
4. Wait 5 seconds before execution
5. Log all operations with timestamp
```

### Truth Verification Chain

**Mandatory Execution Reporting Format**:

```typescript
interface ExecutionReport {
    command: string; // Exact command executed
    startTime: Date; // When execution started
    endTime: Date; // When execution completed
    exitCode: number; // Process exit code
    stdout: string; // Complete stdout (no truncation)
    stderr: string; // Complete stderr (no truncation)
    interpretation: string; // Objective description only
}

// PROHIBITED phrases in interpretation:
const BANNED_PHRASES = [
    "successfully completed", // Unless exitCode === 0
    "should be working", // Must verify, not assume
    "appears to be fixed", // Must prove with tests
    "rollback not possible", // Must attempt first
    "production ready", // Requires full test suite pass
];
```

### Anti-Deception Rules

**Prohibited Behaviors** (ZERO TOLERANCE):

-   ❌ Claiming test success without running tests
-   ❌ Summarizing errors instead of showing full stack traces
-   ❌ Using phrases like "minor issues" to downplay failures
-   ❌ Skipping failed steps without explicit acknowledgment
-   ❌ Generating mock outputs when actual execution fails

**Required Behaviors**:

-   ✅ Show raw command outputs without interpretation
-   ✅ Display complete error messages with line numbers
-   ✅ Report partial successes as "X of Y completed, Z failed"
-   ✅ Include failed test names and assertion details
-   ✅ Provide rollback commands for every destructive operation

### Failure Transparency Protocol

```typescript
// Required failure report structure
class FailureReport {
    reportFailure(error: Error) {
        console.log("❌ OPERATION FAILED");
        console.log("Command:", this.lastCommand);
        console.log("Error Type:", error.constructor.name);
        console.log("Error Message:", error.message);
        console.log("Stack Trace:", error.stack);
        console.log("Attempted Fixes:", this.attemptedFixes);
        console.log("Suggested Next Steps:");
        this.suggestRecovery();
    }

    // NEVER hide errors in try-catch without reporting
    async executeWithTransparency(fn: Function) {
        try {
            const result = await fn();
            console.log("✅ Execution completed");
            console.log("Result:", JSON.stringify(result, null, 2));
            return result;
        } catch (error) {
            this.reportFailure(error);
            throw error; // Re-throw, never swallow
        }
    }
}
```

---

## XI. Architecture Validation

**Rule**: Code architecture must be validated against common anti-patterns and design flaws.

### Automated Architecture Checks

**Circular Dependencies** (CI/CD BLOCKING):

```bash
# JavaScript/TypeScript
npx madge --circular --extensions ts,tsx,js,jsx src/
# If cycles detected, build MUST fail

# Python
pydeps --max-depth=10 --show-cycles src/
# Non-zero exit on circular dependencies
```

**DRY Principle Enforcement**:

```yaml
# .jscpd.json configuration
{
    "threshold": 0,
    "reporters": ["html", "console"],
    "minLines": 6, # Minimum duplicate block
    "minTokens": 50, # Minimum similarity tokens
    "exitCode": 1, # Fail on duplicates
    "strict": true,
}
```

**Layer Separation Validation**:

```typescript
// Forbidden import patterns
const LAYER_RULES = {
    "src/presentation/**": {
        forbidden: ["src/data/**", "src/infrastructure/**"],
        allowed: ["src/domain/**", "src/application/**"],
    },
    "src/domain/**": {
        forbidden: ["src/presentation/**", "src/infrastructure/**"],
        allowed: [], // Domain should have no dependencies
    },
};
```

### Architecture Metrics Dashboard

| Check                 | Tool          | Threshold | Frequency    | Blocking |
| --------------------- | ------------- | --------- | ------------ | -------- |
| Circular Dependencies | madge/pydeps  | 0         | Every commit | YES      |
| Code Duplication      | jscpd         | <5%       | Every commit | YES      |
| Function Complexity   | ESLint/Pylint | ≤10       | Every commit | YES      |
| File Size             | Custom script | ≤700 SLOC prod / test: no limit | Every commit | NO       |
| Test Coverage         | Jest/Pytest   | ≥85%      | Every commit | YES      |

---

## XII. Context Management (Long-Running Tasks)

**Rule**: Optimize context window usage through strategic loading and compression.

### Just-in-Time Context Loading

**File Access Strategy**:

```markdown
DO NOT pre-load all files at task start
DO: Load files only when needed
DO: Release files after subtask completion

Maximum Active Files: 3
When limit reached: Summarize and release oldest

Example workflow:

1. View project structure (tree command only)
2. Identify target file from structure
3. Load specific file when needed
4. Complete modifications
5. Save and release from context
6. Load next file (repeat)
```

### Progressive Disclosure Pattern

```markdown
## Information Hierarchy

Level 1: Project Overview
├── Directory structure (tree -L 2)
├── Key file list (README, package.json)
└── Current task from tasks.md

Level 2: Working Set (load on demand)
├── Currently editing file
├── Related test file
└── Interface/type definitions

Level 3: Reference Set (load for specific questions)
├── Dependencies
├── Configuration files
└── Documentation

NEVER load Level 2/3 without completing Level 1 scan
```

### Context Compression Protocol

**Automatic Compression Triggers**:

-   Context usage >70% of limit
-   Task completion milestones
-   Before starting new major task

**Compression Strategy**:

```typescript
class ContextCompressor {
    compress() {
        // 1. Remove old tool outputs
        this.removeToolOutputsOlderThan("5_messages");

        // 2. Summarize completed tasks
        this.summarizeCompleted();

        // 3. Extract key decisions to NOTES.md
        this.persistKeyDecisions();

        // 4. Keep only essential state
        return {
            currentTask: this.getCurrentTask(),
            recentFiles: this.getRecentFiles(3),
            blockingIssues: this.getBlockers(),
            nextSteps: this.getNextSteps(),
        };
    }
}
```

### Structured Note-Taking

**Mandatory NOTES.md Format**:

```markdown
# Project Notes

## Current Sprint Focus

-   Task: [Current task ID and description]
-   Branch: [Git branch name]
-   Started: [Timestamp]

## Completed Today

-   [x] AUTH-001: Setup authentication module
-   [x] AUTH-002: Add JWT token generation
-   [ ] AUTH-003: Add refresh token logic (blocked)

## Active Context

-   Editing: src/auth/jwt.service.ts
-   Testing: src/auth/jwt.service.spec.ts
-   Config: .env.example updated

## Blocking Issues

1. Missing dependency: jsonwebtoken types
    - Action: Run `npm install --save-dev @types/jsonwebtoken`
2. Database migration pending
    - Action: Await user approval for migration

## Key Decisions

-   2024-01-10: Use JWT over sessions (performance)
-   2024-01-10: Store refresh tokens in Redis (security)

## Next Session Checklist

-   [ ] Resolve jsonwebtoken types issue
-   [ ] Complete AUTH-003 implementation
-   [ ] Run full test suite
```

### Sub-Agent Delegation Criteria

**Automatic Delegation Triggers**:

```markdown
WHEN task requires >5 file modifications:
→ Delegate to sub-agent with focused context

WHEN estimated time >30 minutes:
→ Break into sub-tasks, delegate each

WHEN crossing domain boundaries:
→ One sub-agent per domain (auth, payment, UI)

Sub-Agent Output Requirements:

-   Maximum 2000 tokens summary
-   Key changes list
-   Test results
-   Any new dependencies
```

---

## XIII. Enhanced Security Standards

**Rule**: Implement defense-in-depth with mandatory boundary testing.

### Boundary Test Matrix (MANDATORY)

```typescript
// Required test template for EVERY input function
describe("Input Validation Tests", () => {
    const testMatrix = {
        strings: [
            { input: null, expect: "error" },
            { input: undefined, expect: "error" },
            { input: "", expect: "error" },
            { input: " ", expect: "error" },
            { input: "a".repeat(10000), expect: "error" },
            { input: "<script>alert(1)</script>", expect: "sanitized" },
            { input: "'; DROP TABLE users;--", expect: "escaped" },
            { input: "../../../etc/passwd", expect: "blocked" },
            { input: "你好世界🌍", expect: "valid" },
        ],
        numbers: [
            { input: 0, expect: "valid" },
            { input: -1, expect: "error" },
            { input: Number.MAX_SAFE_INTEGER, expect: "error" },
            { input: Number.MIN_SAFE_INTEGER, expect: "error" },
            { input: NaN, expect: "error" },
            { input: Infinity, expect: "error" },
        ],
        arrays: [
            { input: null, expect: "error" },
            { input: undefined, expect: "error" },
            { input: [], expect: "valid_empty" },
            { input: new Array(10000), expect: "error" },
        ],
    };

    // Test execution is MANDATORY, not optional
    testMatrix.strings.forEach((test) => {
        it(`handles string input: ${JSON.stringify(test.input)}`, () => {
            // Implementation required
        });
    });
});
```

### Environment Isolation (CRITICAL)

**Three-Environment Mandate with Color Coding**:

```javascript
class EnvironmentGuard {
    constructor() {
        this.env = process.env.NODE_ENV;
        this.dbUrl = process.env.DATABASE_URL;
    }

    validateConnection() {
        // Color-coded console output
        const colors = {
            production: "\x1b[31m", // RED
            staging: "\x1b[33m", // YELLOW
            development: "\x1b[32m", // GREEN
        };

        console.log(
            `${colors[this.env]}[${this.env.toUpperCase()}] Environment\x1b[0m`
        );

        // Production safeguards
        if (this.env === "production") {
            if (!process.env.PRODUCTION_CONFIRMED) {
                throw new Error(
                    "Production access requires PRODUCTION_CONFIRMED=true"
                );
            }
            console.log("⚠️ PRODUCTION MODE - All operations logged");
            this.enableAuditLog();
        }

        // Connection string validation
        const expectedPrefix = `${this.env}_DATABASE_URL`;
        if (!process.env[expectedPrefix]) {
            throw new Error(
                `Missing ${expectedPrefix} for ${this.env} environment`
            );
        }
    }
}
```

### Input Sanitization Pipeline

```typescript
class InputSanitizer {
    // Layer 1: Type validation
    validateType(input: any, expectedType: string): boolean {
        if (input === null || input === undefined) return false;
        return typeof input === expectedType;
    }

    // Layer 2: Boundary checking
    checkBoundaries(input: any, rules: BoundaryRules): boolean {
        if (rules.minLength && input.length < rules.minLength) return false;
        if (rules.maxLength && input.length > rules.maxLength) return false;
        if (rules.min && input < rules.min) return false;
        if (rules.max && input > rules.max) return false;
        return true;
    }

    // Layer 3: Pattern validation
    validatePattern(input: string, pattern: RegExp): boolean {
        return pattern.test(input);
    }

    // Layer 4: Sanitization
    sanitize(input: string): string {
        return input
            .replace(/[<>]/g, "") // Remove HTML brackets
            .replace(/['";]/g, "") // Remove SQL meta-characters
            .replace(/\.\.\//g, "") // Remove path traversal
            .trim();
    }
}
```

---

## XIV. Priority Matrix

**WHEN Constitution principles conflict or resources are constrained, use this priority order:**

| Priority | Principle                          | Rationale                          | Override Condition                         |
| -------- | ---------------------------------- | ---------------------------------- | ------------------------------------------ |
| **P0**   | User Safety & Data Integrity       | Prevents data loss, corruption     | NEVER override                             |
| **P1**   | Security (Section VII)             | Prevents breaches, legal liability | Only with explicit user acceptance of risk |
| **P2**   | Agentic Safety (Section X)         | Ensures trustworthiness            | Only with user "force" flag                |
| **P3**   | Test First (Section I)             | Quality foundation                 | NO exceptions                              |
| **P4**   | TRUST Principles (Section V)       | Long-term maintainability          | Technical debt ticket required             |
| **P5**   | Context Optimization (Section XII) | Performance and efficiency         | May defer in prototypes                    |
| **P6**   | Architecture (Section XI)          | Prevents technical debt            | May accumulate with payback plan           |
| **P7**   | Simplicity (Section II)            | Reduces complexity                 | May add complexity with justification      |
| **P8**   | Documentation (Section VIII)       | Knowledge transfer                 | May defer until stabilization              |

### Conflict Resolution Protocol

```markdown
WHEN principles conflict:

1. Check if P0 (User Safety) is involved → ALWAYS choose safety
2. Check if security is involved → Choose security unless user accepts risk
3. Apply this decision tree:

Does it risk data loss?
├─ YES → STOP. Require backup first
└─ NO → Continue
│
Does it skip tests?
├─ YES → STOP. Write tests first
└─ NO → Continue
│
Does it violate security?
├─ YES → STOP. Fix security first
└─ NO → Continue
│
Does it exceed complexity budget?
├─ YES → Simplify or document why
└─ NO → Proceed with implementation
```

### Emergency Override Protocol

```markdown
In emergency situations (production down, data breach in progress):

1. Document the emergency in EMERGENCY.md
2. Get written approval from user
3. Apply minimum viable fix
4. Create immediate follow-up ticket for proper fix
5. Schedule post-mortem within 48 hours
```

---

_This Constitution is a living document. It evolves with the project but changes deliberately and with user approval._

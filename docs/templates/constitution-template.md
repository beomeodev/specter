# Project Constitution: {PROJECT_NAME}

---

## Preamble

This Constitution is the workflow governance layer for {PROJECT_NAME}. It is
applied when `.specify/memory/constitution.md` exists or when an `/ms.*` workflow
is active.

This Constitution does not replace `AGENTS.md`. `AGENTS.md` is the always-on
fallback contract for basic agent safety, permissions, surgical scope, and coding
hygiene. This Constitution adds stricter workflow rules for specifications,
planning, task generation, implementation review, traceability, and release
readiness.

If the Constitution and `AGENTS.md` conflict:

1. User safety, data integrity, destructive-operation approval, and surgical
   scope from `AGENTS.md` always remain binding.
2. This Constitution governs `/ms.*` artifacts, gates, and project-specific
   workflow constraints.
3. Command files under `.claude/commands/` define step-specific execution
   details, but must not contradict this Constitution.

Deviations from this Constitution require explicit user approval and should be
recorded as an amendment or project-specific rule when durable.

---

## I. Workflow Scope And Gate Ownership

### Workflow Scope

The `/ms.*` workflow is a layered process:

```text
One-time setup   /ms.featuremap -> /ms.codex-checklist -> /ms.verify -> /ms.constitution
                 (bundled: /ms.pre-specter; PRD co-authoring beforehand: /ms.prd)
Per-Feature      /ms.checklist -> /ms.agent-verify -> /ms.specify -> /ms.clarify
                 -> /ms.plan -> /ms.tasks -> /ms.analyze -> /ms.implement -> /ms.review
                 (bundled: /ms.specter <NNN>)
Publish/release  [/ms.up-docs] -> /ms.fin -> /ms.merglease
Side tracks      /ms.fix (no new requirement) · /ms.expand (PRD Amendment)
                 · /ms.audit (advisory product audit)
```

`/ms.constitution` is not a per-Feature ceremony. It establishes or amends the
project-wide baseline in Section IX from the checked PRD Feature Map.

### Gate Ownership

- `/ms.checklist` owns PRD and Feature Map coverage checks.
- `/ms.specify` owns conversion from Feature prompt to `spec.md`.
- `/ms.clarify` owns ambiguity reduction and spec updates.
- `/ms.plan` owns implementation strategy and architectural planning.
- `/ms.tasks` owns task breakdown and lightweight traceability metadata.
- `/ms.analyze` owns pre-implementation document consistency only: `spec.md`,
  `plan.md`, `tasks.md`, amendments, lineage, file-path references, and project
  baseline alignment.
- `/ms.analyze` must not run post-implementation code gates such as tests, lint,
  typecheck, coverage, build, security scan, or code-level TAG scans.
- `/ms.implement` owns test-first implementation for the selected phase/task/TAG scope.
- `/ms.review` owns post-implementation code review and executable gates:
  lint, typecheck, tests, build, coverage, security checks, TRUST review, and
  TAG integrity reporting.
- `/ms.up-docs` owns documentation synchronization. Documentation sync failures
  are fail-open unless the active project explicitly promotes them to blockers.
- `/ms.fin` handles commit/push/PR workflows according to its command
  definitions and user approval requirements.

---

## II. Requirements Clarity: GEARS Standard

### Rule

GEARS is the canonical syntax for behavioral requirements in `/ms.*` workflow
documents. It is used where precision prevents ambiguity, especially in behavior
contracts and acceptance criteria.

Classic EARS is a legacy-compatible subset. Convert legacy EARS to GEARS on the
next meaningful edit instead of preserving mixed syntax.

### Language Policy

- User interaction may be in Korean.
- Workflow documents (`spec.md`, `plan.md`, `tasks.md`, tests, code-facing docs)
  are written in English unless the user explicitly requests otherwise.
- GEARS keywords (`Where`, `While`, `When`) and `shall` remain in English.

### Canonical Form

```text
[Where <static condition>] [While <runtime state>] [When <trigger>]
the <concrete subject> shall <verifiable behavior>.
```

Clauses are optional, but when present they must appear in this order:
`Where -> While -> When -> shall`.

GEARS maps 1:1 to Given-When-Then acceptance scenarios: `Where` + `While` ->
Given, `When` -> When, `shall` -> Then. This mapping is what makes a
requirement testable — every FR's clauses should be recoverable from its
acceptance scenario and vice versa.

### GEARS Is Required For

- new user-facing behavior contracts
- acceptance criteria that drive implementation or tests
- event-triggered behavior (`When ...`)
- runtime-state behavior (`While ...`)
- static applicability such as permissions, feature flags, deployment targets, or
  configuration (`Where ...`)
- error handling, exceptional behavior, validation failures, and security rules
- behavior that must map 1:1 to a test or verification task

### Plain Statements Are Allowed For

- preservation contracts, such as existing UI/layout/flow that must remain
  unchanged
- type, schema, shape, or field declarations
- scope notes and out-of-scope boundaries
- Constitution or policy echoes
- refactor constraints that do not introduce new behavior
- implementation notes that are not acceptance criteria

Plain statements must still be specific and verifiable. Do not use vague phrases
such as "fast", "secure", "safe", "user-friendly", "well", or
"appropriately" without measurable criteria. Weak modal verbs are equally
forbidden in requirements: "can", "could", "might" (resolve the condition into
`Where`/`When`) and "should", "would be good" (commit to a `Where`-gated
`shall`).

### Rules

- Use a concrete subject, such as `the auth service` or `the upload worker`.
  Use `the system` only for genuinely product-wide behavior.
- `Where` describes static applicability only.
- `While` describes runtime state only.
- `When` describes triggers, including error or exceptional events.
- Express exceptions as category-labeled GEARS, for example:
  `[Error Handling] When credentials are invalid, the auth service shall return
  a generic authentication error.`
- One behavioral requirement should describe one verifiable behavior.
- Requirements that cannot be tested or verified must be clarified before
  implementation.

### Enforcement

- `/ms.specify` and `/ms.clarify` produce or refine behavioral requirements.
- `/ms.analyze` checks document coverage, drift, contradiction, and mappability
  from requirements to plan/tasks.
- `/ms.review` may flag implemented behavior that no longer matches active
  requirements.

---

## III. Test-First Implementation

### Rule

For `/ms.*` feature work, implementation follows a verifiable test-first loop:

1. Define the behavior contract.
2. Write or update the relevant test or verification case.
3. Implement the smallest change that satisfies it.
4. Refactor only within the selected implementation scope while keeping verification green.

For audit-driven refactors, the RED phase may be a safety-net verification that
is already green. In that case, document that the task is refactor-mode and keep
the safety net in place before making changes.

### Coverage Target

- Overall coverage target: 85% or the active project threshold, whichever is
  explicitly stricter.
- Critical paths such as authentication, authorization, payments, data deletion,
  and security-sensitive flows should have targeted tests even when global
  coverage is already high.

### Enforcement

- `/ms.implement` owns the local test-first workflow for the selected implementation scope.
- `/ms.review` owns executable verification after implementation.
- `/ms.analyze` does not run coverage or test commands.

---

## IV. TRUST Review Model

TRUST is the code quality review model for `/ms.*` work. It is a review and gate
framework, not a claim that every check is automatically available in every
repository.

### T - Test First

- Tests or verification cases exist for the implemented behavior.
- Tests pass for the touched area.
- Coverage is evaluated by `/ms.review` or the project's CI tooling when
  available.

### R - Readable

- Production code files target <=700 SLOC, excluding blank/comment-only lines.
- Test files have no SLOC limit; case coverage is prioritized over file length.
- Functions target <=100 LOC.
- Cyclomatic complexity target: <=10 per function.
- Nesting depth target: <=4.
- Parameters target: <=5 unless a framework interface requires more.

### U - Unified

- Code follows existing project patterns and folder structure.
- Types are explicit and strict typing is preferred.
- Lint and formatting rules come from the repository's configured tooling.

### S - Secured

- User-controlled inputs are validated at boundaries.
- Authorization is checked before user- or tenant-scoped data access.
- Secrets are loaded from environment/configuration, never hardcoded.
- Sensitive data is not logged.
- Dependency and static security tooling should be run by `/ms.review` or CI when
  configured.

### T - Trackable

- TAGS provide best-effort grep-based traceability from requirement to tests,
  code, and docs.
- TAG **semantic** issues (does the test actually cover the spec, stale
  references, orphaned tags) are warnings by default, not commit-blocking gates,
  unless Section IX or a user decision explicitly promotes them to blockers.
- TAG **wiring** (every `@CODE` anchor resolves to same-id `@SPEC` and `@TEST`
  anchors; `@CODE` ids unique; `FIX-*` ids exempt from `@SPEC`) is mechanical
  and IS commit-blocking where the pre-commit backstop
  (`scripts/specter/check_tag_chain.py`) is installed.

### TRUST Gate Ownership

| Area | Owner | Default Blocking Behavior |
| --- | --- | --- |
| Document consistency | `/ms.analyze` | Blocks `/ms.implement` on FAIL |
| Tests/lint/type/build | `/ms.review` or CI | Blocks when executable gates fail |
| Coverage | `/ms.review` or CI | Blocks only when tooling and threshold are active |
| Security scan | `/ms.review` or CI | Blocks HIGH/CRITICAL findings when tooling exists |
| TAG wiring | pre-commit backstop | Blocks the commit where installed |
| TAG semantics | `/ms.review` report | Warning by default |

Gates in this table are enforced two ways, and the distinction matters: rows
owned by hooks/CI/pre-commit are **mechanical** (they run regardless of agent
judgment); rows owned by `/ms.*` commands are **model-followed** (the command's
instructions enforce them, backed by conductor stop-on-FAIL policy). Do not
describe a model-followed gate as if a hook enforces it.

---

## V. TAGS: Best-Effort Traceability

### Purpose

TAGS exist to make requirement/test/code/doc relationships easy to find with
`rg`. They are not a substitute for tests, code review, or executable gates.

### Canonical Chain

Use ASCII separators in machine-readable TAG chains:

```text
@SPEC:TAG-ID -> @TEST:TAG-ID -> @CODE:TAG-ID
```

`@DOC` anchors are retired (nothing consumed them); tolerate them in legacy
files, never require or write them.

### Placement

- `@SPEC:TAG-ID`: placed in `tasks.md` (phase header, written by `/ms.tasks`)
  or `spec.md` near the relevant requirement. Only the `@SPEC` anchor may
  appear in spec/tasks documents — `@TEST`/`@CODE` anchor forms there would
  pre-satisfy or collide with the real file anchors.
- `@TEST:TAG-ID`: placed once at the top of a relevant test file.
- `@CODE:TAG-ID`: placed once at the top of a relevant implementation file.

### File-Level Only

- Use one file-level anchor line only.
- Do not add line-level `@TEST` docstrings to every test function.
- When one test file covers multiple FR groups, use one anchor line per id (or
  one anchor plus a short `Covers:` line listing the relevant FR/TAG groups).

### Multi-File Work

- Each `@CODE:TAG-ID` anchor lives in exactly **one** file — the primary file
  for that requirement slice. The pre-commit backstop rejects duplicate `@CODE`
  ids mechanically. Secondary files restate the chain on a `@CHAIN:` line
  (ignored by the backstop) instead of declaring a second anchor.
- Multiple test files may share the same `@TEST:TAG-ID` when they verify the same
  requirement or Feature slice.
- `/ms.fix` work uses `FIX-*` ids: no `@SPEC` anchor is required or written,
  and a purely presentational fix declares
  `@TEST: (presentational — no test)` in place of a test anchor.

### Anchor Format

```typescript
// @CODE:AUTH-001
```

```python
# @TEST:AUTH-001
```

One comment line, no metadata. Legacy multi-line TAG blocks (`@SPEC:`/`@TEST:`
path references, `@CHAIN`, `@STATUS`, `@CREATED`, `@UPDATED`) remain valid in
already-tagged files — the backstop parses only anchors — but new work writes
bare anchors and never hand-stamps dates.

### Validation

- Mechanical wiring (`@CODE` -> same-id `@SPEC`/`@TEST` anchors, unique `@CODE`
  ids, the `FIX-*` exemptions above) is enforced by the pre-commit backstop
  `scripts/specter/check_tag_chain.py` where installed — it blocks the commit.
- Semantic issues (coverage fidelity, orphaned TAGs, stale references) are
  reported by `/ms.review` or TAG tooling and are warnings by default.
- A project may promote TAG semantic integrity to blocking only through an
  explicit Section IX rule or user decision.

---

## VI. File, Architecture, And Tooling Governance

### File Size And Complexity

- Production code: <=700 SLOC per file.
- Test code: no SLOC limit.
- Function length: <=100 LOC target.
- Cyclomatic complexity: <=10 target.
- Documentation, specs, command prompts, and generated reference docs have no
  SLOC limit unless Section IX adds one.

Exceeding a target requires either a planned split task, an explicit rationale, or
a project-specific exception.

### Simplicity And External Tools

Prefer mature existing tools over custom implementations:

- use `rg` for code search
- use project linters for style and complexity
- use type checkers for static typing
- use existing test runners for verification
- use git for history instead of custom state tracking

### AST Parser Policy

AST tooling is allowed when it follows one of these safety models:

1. Read-only analysis.
2. Sandboxed transformation where original files remain reviewable.
3. Sandboxed execution with no filesystem/network escape.
4. AST diffing for structural comparison.

Do not build custom parsers when a mature parser already exists for the language
or framework.

---

## VII. Security Governance

Security findings must be turned into verifiable behavior requirements or review
findings, not vague TODOs.

Required security posture for `/ms.*` work:

- validate external input and file uploads
- bind authorization to the authenticated principal and resource owner
- prevent IDOR/BOLA and tenant-boundary leaks
- avoid mass assignment by whitelisting writable fields
- parameterize database access
- avoid plaintext passwords and weak crypto
- keep secrets out of source code and logs
- run configured dependency or static security checks during `/ms.review` or CI

If a security requirement is ambiguous, express it as GEARS and clarify it before
implementation.

---

## VIII. Documentation As Code

Documentation should update when behavior, APIs, setup, architecture, or workflow
contracts change.

- Keep documentation concise and current-state oriented.
- Document why decisions exist, not every line of what code does.
- Use `/ms.up-docs` or manual updates for docs affected by implementation.
- Documentation sync is fail-open by default unless Section IX makes it blocking.

---

## IX. Project-Specific Constraints

This section is empty by default.

`/ms.constitution` may populate it only with durable project-wide constraints
proven by the checked PRD Feature Map or an explicit user decision. Do not invent
constraints to fill categories.

If no durable project-specific constraints exist, keep exactly:

```text
_No project-specific constraints established yet._
```

When durable constraints exist:

- cite the source PRD, product-principles section, or Feature Map section for
  each rule
- include only headings that contain actual rules
- omit empty Technology, Dependency, Architecture, Security, Performance, or
  Workflow sections
- keep temporary Feature decisions in the Feature spec, not in this Constitution
- promote TAG, documentation, coverage, or security findings to blocking only
  when this section explicitly says so

Suggested headings, when applicable:

- Source Artifacts
- Product-Wide Rules
- Architecture And Integration Constraints
- Security And Data Rules
- Quality Gates
- Workflow Overrides

---

## X. Amendment Process

Amend the Constitution only when the current rule set is inadequate for a durable
project constraint.

1. Identify the rule gap.
2. Draft the amendment with rationale.
3. Assess impact on existing specs, plans, tasks, code, and commands.
4. Get explicit user approval.
5. Update version metadata and Section IX if project-specific.

Version semantics:

- MAJOR: removes or redefines a principle.
- MINOR: adds a new durable rule.
- PATCH: clarifies wording without changing behavior.

### Amendment History

| Version | Date | Change | Rationale |
| --- | --- | --- | --- |
| 2.0.0 | {DATE} | Split AGENTS baseline from workflow governance | Reduce ceremony and drift |

---

## XI. Delivery Standards

A Feature is ready for user review when:

- acceptance criteria are satisfied or explicitly amended
- relevant tests or verification cases pass
- `/ms.analyze` has no blocking document consistency failures before
  implementation
- `/ms.review` has run post-implementation gates where tooling exists
- security-sensitive paths have been reviewed
- docs are updated or intentionally deferred
- unresolved warnings are reported honestly

Do not describe a Feature as production-ready unless the relevant executable
checks have actually passed.

---

## XII. Priority And Conflict Resolution

When rules conflict, use this priority order:

| Priority | Principle | Default |
| --- | --- | --- |
| P0 | User safety and data integrity | Never override |
| P1 | Security | Override only with explicit risk acceptance |
| P2 | Agentic safety and permissions | Follow `AGENTS.md` |
| P3 | Tests and executable verification | Do not skip silently |
| P4 | Requirements clarity | Clarify before implementing ambiguous behavior |
| P5 | Simplicity and maintainability | Prefer the simpler sufficient design |
| P6 | Traceability and documentation | Best effort unless promoted |

If the conflict cannot be resolved from these priorities, stop and ask the user.

---

_This Constitution is a living workflow document. It evolves deliberately, with
user approval, and sits on top of the always-on `AGENTS.md` baseline._

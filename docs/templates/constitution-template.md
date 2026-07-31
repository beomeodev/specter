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

Inside a Feature cycle, a proposed deviation returns FAIL or, when it changes
product intent, routes to the existing `/ms.clarify` handoff. It must not
create another approval stop. Durable Constitution changes are made through a
separate explicit `/ms.constitution` invocation.

---

## I. Workflow Scope And Gate Ownership

### Workflow Scope

The `/ms.*` workflow is a layered process:

```text
One-time setup   /ms.featuremap -> /ms.featuremap-checklist -> /ms.pre-verify -> /ms.constitution
                 (bundled: /ms.pre-specter; PRD co-authoring beforehand: /ms.prd)
Per-Feature      /ms.checklist -> /ms.verify -> /ms.specify -> /ms.clarify
                 -> /ms.plan -> /ms.tasks -> /ms.analyze -> /ms.implement -> /ms.review
                 (bundled: /ms.specter <NNN>)
Publish/release  [/ms.up-docs] -> /ms.fin -> /ms.merglease
Side tracks      /ms.fix (no new requirement) · /ms.expand (PRD Amendment)
                 · /ms.audit (advisory product audit)
```

`/ms.constitution` is not a per-Feature ceremony. It establishes or amends the
project-wide baseline in Section IX from the checked PRD Feature Map.

A SPECTER Feature is the smallest dependency-aware slice that can be specified,
implemented, verified, reviewed, and merged independently. It may be
architectural rather than independently user-shippable; end-to-end user value
is guaranteed at the Phase boundary, whose final Feature owns the Phase E2E
scenario.

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

### Lean Verification Governance

Verification stations use two independent fresh reviewers and a deterministic,
state-free reducer bound to the current input hash. The reducer reads fixed
report paths, validates exactly one PASS/WARN/FAIL result per report, and returns
the worst result. One unavailable reviewer caps a non-FAIL result at WARN; both
unavailable is FAIL. A station reruns at most once and only after inputs change.

No command creates or relies on risk profiles, Verification signals, receipts,
round state, fingerprints, typed approvals, or acknowledgment bypasses.
`/ms.clarify` is the only mandatory human stop in the Feature cycle.

### Progressive Refinement Governance

Authority is domain-specific: PRD owns product intent and explicit boundaries;
Feature Map owns ownership and DAG; `spec.md` owns observable detail;
`plan.md` owns technical design; `tasks.md` owns execution partition; code and
tests own observed reality. Downstream `refinement` and
`reality-correction` are legitimate additions. A new actor/journey,
integration, retained-data category, permission boundary, paid capability, or
explicit exclusion/cost/policy conflict is a `boundary-change` or `conflict`
and fails with the proposed upstream patch at grading stations. At
`/ms.clarify`, the sole mandatory human boundary, it is presented to the user
for an explicit intent decision instead. Missing literal PRD wording alone is
never a blocking finding.

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
- `/ms.clarify` is the Per-Feature cycle's sole mandatory human handoff. It
  resolves evidence-determined ambiguities first, then waits for the user to
  review those resolutions and decide every remaining product-intent choice.
  No other station may add an acknowledgment stop.
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

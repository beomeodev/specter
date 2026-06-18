# AI Coding Assistant Rules (AGENTS.md)

This file is the always-on fallback contract for AI coding agents. It applies to
ordinary coding tasks, small projects, and `/ms.*` workflow projects alike.

`AGENTS.md` must stand alone: if no Constitution exists, agents still have enough
guidance to work safely and pragmatically.

These instructions guide agent behavior; they are not a hard enforcement layer.
Use hooks, settings, CI, or command permissions for rules that must be enforced
regardless of agent judgment.

---

## 1. Constitution Handling

- If `.specify/memory/constitution.md` exists, read it for detailed workflow and
  project governance rules.
- If no Constitution exists, do not block ordinary coding work and do not create
  one unless the user asks or an `/ms.*` workflow command requires it.
- For non-`/ms` tasks, use lightweight acceptance criteria when requirements are
  ambiguous; do not force GEARS, TRUST reports, or TAG blocks.
- For `/ms.*` tasks, the active Constitution and command files define the
  workflow gates and artifacts.
- If this file conflicts with the Constitution, the more specific active
  Constitution rule wins for workflow details, but safety, permissions, and
  surgical-scope rules in this file always remain binding.

---

## 2. Required Working Style

- Read relevant files before planning or editing. Search for existing patterns,
  types, constants, tests, and similar features before making changes.
- Do not guess through ambiguity. State assumptions, surface tradeoffs, and ask
  before taking broad, risky, or irreversible action.
- Push back when the requested approach is unsafe, overcomplicated, or
  inconsistent with the existing codebase; propose the simpler sufficient path.
- Follow existing project structure, naming, import order, error handling, and
  testing style.
- Keep changes surgical: touch only what the request requires. Do not refactor,
  reformat, or "improve" adjacent code unless the task explicitly requires it.
- Every changed line should trace directly to the request or to cleanup required
  by that change.
- Clean up only the imports, variables, files, or helpers that your own change
  made obsolete. Mention unrelated dead code; do not delete it.
- Prefer simple functions and standard patterns before introducing abstractions,
  frameworks, or new dependencies.
- Do not add speculative features, future-proofing, configurability, or
  abstractions for single-use code.
- Preserve a single source of truth for important constants, types, validation
  rules, and shared utilities.
- Do not leave placeholders, stubs, mock outputs, or partial implementations
  unless the user explicitly asks for them.

---

## 3. Tests And Verification

- Prefer test-first: write the failing test, implement the minimum fix, then
  refactor while keeping tests green.
- Convert implementation requests into verifiable goals before coding. Define
  the success criteria and the smallest check that proves them.
- If a task is a bug fix, reproduce the bug with a test when practical.
- For multi-step tasks, keep a brief plan where each step has an associated
  verification check.
- If a task is documentation-only or the project has no test infrastructure,
  state that clearly instead of inventing tests.
- Run the smallest relevant verification command available for the touched
  area. Do not claim tests, lint, typecheck, or build passed unless you ran them.

---

## 4. Code Quality Baseline

- Use explicit types. Do not use `any` or equivalent escape hatches to bypass
  type checking.
- Avoid meaningful magic strings and numbers. Reuse existing constants/config or
  define a single source of truth when the value matters.
- Avoid hidden side effects, global mutable state, direct parameter mutation, and
  implicit dependencies.
- Use clear names, early returns, and straightforward control flow. Avoid clever
  one-liners when simple code is clearer.
- Add comments only when they explain why a non-obvious decision exists. Do not
  comment obvious code.
- Keep production files and functions reasonably small. If a file or function is
  becoming hard to reason about, split it deliberately as part of the task.

---

## 5. Zero-Tolerance Workarounds

Never use workarounds that hide root causes:

- `setTimeout` or timing hacks for state synchronization
- `window.location.reload()` to mask state bugs
- fallback branches that silently hide invalid states
- catching errors without handling or rethrowing them
- disabling type, lint, test, or security checks to make a change pass

Find and fix the root cause, or report the blocker explicitly.

---

## 6. Security Baseline

- Validate and sanitize user-controlled input at boundaries.
- Require authentication and authorization unless a route or action is
  explicitly public.
- Keep secrets in environment/configuration, never in source code.
- Never log passwords, tokens, credentials, or sensitive personal data.
- Use parameterized database access or trusted ORM APIs.
- Do not use `eval`, `exec`, disabled SSL verification, or broad CORS unless the
  user explicitly accepts the risk.

---

## 7. Permissions And Scope

Ask for user approval before:

- modifying 3 or more files in one task
- installing packages or changing dependency versions
- deleting or moving files
- running database migrations
- changing environment configuration or secrets
- starting local servers
- committing, amending commits, pushing, merging, or creating releases

Do not run destructive commands such as `git reset --hard` or broad deletes
unless the user explicitly requests and confirms them.

---

## 8. TAGS, GEARS, And TRUST Outside `/ms`

- TAGS are optional outside `/ms.*` workflows. Preserve existing TAG blocks when
  editing tagged code, but do not introduce TAG ceremony into untagged ordinary
  work unless requested.
- GEARS is useful for ambiguous behavior contracts, but plain acceptance
  criteria are enough for small or non-workflow tasks.
- TRUST is a quality review rubric outside `/ms.*`; executable checks still come
  from the project's actual lint, type, test, build, and security tooling.

---

## 9. System Map Handling

- If `docs/SYSTEM_MAP.md` exists, read it before non-trivial coding, planning,
  or workflow changes.
- Treat `docs/SYSTEM_MAP.md` as a stale-prone snapshot, not as authority over
  current code. Check its `git_head`, `generated_at`, `working_tree`, and
  `stale_when` metadata before relying on it.
- If the map is missing or stale for the task, use the
  `.claude/skills/codebase-snapshot/SKILL.md` procedure to refresh it with
  current git metadata and verified facts.
- Use Serena MCP for symbol-level navigation when configured and useful, but do
  not block exploration if Serena is unavailable; fall back to `rg`, `find`,
  and `git`.

---

## 10. Pre-Work Checklist

- Have I read `docs/SYSTEM_MAP.md` if it exists, and checked whether it is
  stale for this task?
- Have I read the relevant files?
- Have I checked existing patterns, tests, types, and constants?
- Is the requirement clear enough to implement and verify?
- Is this change small enough to proceed without a 3+ file plan?
- What is the smallest relevant test or verification command?
- Are there security, permissions, or data-integrity risks?

---

<!-- PROJECT_RULES_START -->
<!-- This section may be populated by /ms.constitution with project-specific rules. -->
<!-- Keep generated project rules concise and do not manually edit generated content. -->
<!-- PROJECT_RULES_END -->

---

**Template Version**: 2.0.0

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
- **Never cite the Constitution by section number.** The Constitution is a
  project-local file (`/ms.sync` explicitly never broadcasts it), so its
  numbering differs between projects and cannot be assumed by any command,
  skill, template, spec, plan, or task. Cite by section *name* — "the
  Requirements Clarity (GEARS Standard) section", "the TRUST review section",
  "the file, architecture, and tooling governance section". The one exception is
  **Section IX**, whose literal heading `## IX. Project-Specific Constraints` is
  a cross-project structural contract that `specter-gate.sh` greps for; keep
  that reference exactly as-is.

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
- Subagent dispatch discipline: hand artifacts over as **file paths, not pasted
  content** — everything pasted into a dispatch prompt or printed back stays
  resident in context for the rest of the session (brief → file, report → file).
  Pick the least powerful model sufficient for the role (mechanical single-file
  work → cheap tier; integration → standard; architecture and final review → most
  capable), but remember **turn count beats token price** — a cheap model that
  needs 3× the turns can cost more overall. Specify the model explicitly when
  dispatching.
- Implementation-delegation discipline: inside an invoked `/ms.*` cycle, the
  host implements. Delegating implementation to an external CLI agent
  (Codex/Antigravity) requires the user's explicit prior approval, granted per
  Feature and never inherited from precedent; an agent that implemented a
  Feature is recused from that Feature's verification stations (self-review is
  never dual review).
- Do not re-read a file you already read this session. Reuse what you have
  unless the user explicitly says its content changed. Exception: the harness
  requires a fresh `Read` of a file immediately before `Edit`/`Write`; always
  satisfy that requirement even when the content is already in context.
- This applies to workflow artifacts too (`feature-map.md`, checklists,
  constitution, spec/plan/tasks): when a command step tells the host to read
  one, reuse the in-context copy unless something actually changed it since —
  an edit this session, a fix round that touched it, or a gate report
  bound to a new input hash. A station boundary alone is not a reason to re-read.
  This governs only the host's main thread; fresh subagents at isolated
  stations still read their inputs from disk by design.

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
- When running commands during a conversation (tests, builds, logs), filter the
  output to the relevant lines instead of dumping it whole, e.g.
  `pytest 2>&1 | grep -E 'FAIL|ERROR|PASS'` or `... | tail -30`.

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

Invocation of `/ms.specter` is scoped approval for repository-local changes
required by the clarified Feature: modifying 3 or more files, required
creates/moves/deletes, plan-recorded dependency changes, disposable/local test
migrations, and bounded review server boots. It does **not** approve
production/staging database migrations, environment or secret changes, external
destructive operations, git publishing, or force operations. Those still need
their own explicit authority.

Invocation of `/ms.pre-specter` or `/ms.expand` likewise approves the
3-or-more-file generated workflow artifacts and Feature Map corrections those
commands define. It does not approve dependency changes, runtime migrations,
secrets/environment changes, external destructive operations, or git actions.

Invocation of `/ms.fix` approves the repository-local files required by the
bounded fix and its mini-plan. Package changes, runtime migrations,
secrets/environment changes, external destructive operations, and git actions
retain their command-specific rules below.

The same approval-by-invocation rule covers command-defined runtime checks:
running `/ms.review` or `/ms.audit` **is** the user's approval for the server/
entrypoint boots and tool installs those commands' steps explicitly define
(Done Criteria Execution, audit cold-start). Ad-hoc server starts or installs
outside an invoked command still ask first.

Approval for git publishing is satisfied by invocation, not per-action asks:
`git commit`/`git push`/`gh pr` are deliberately in the project permission
allowlist (`.claude/settings.json`), and running `/ms.fin`, `/ms.fix`, or
`/ms.merglease` **is** the user's approval for the git actions those commands
define. Ad-hoc commits/pushes outside an invoked workflow command still ask
first. The deny list (`git reset --hard`, force-push, `git clean -fdx`) always
stands.

Do not run destructive commands such as `git reset --hard` or broad deletes
unless the user explicitly requests and confirms them.

When committing, split changes by logical unit: each commit is one coherent
concern (a feature with its tests and docs is one commit; an unrelated refactor
or config change is another). Default to multiple commits when the diff spans
more than one concern, and collapse to a single commit only when the whole change
is cohesive. This is the default for every track (`/ms.fin`, `/ms.fix`, and direct
commits).

---

## 8. TAGS, GEARS, And TRUST Outside `/ms`

- TAGS are optional outside `/ms.*` workflows. Preserve existing TAG anchors
  (and legacy TAG blocks) when editing tagged code, but do not introduce TAG
  ceremony into untagged ordinary work unless requested.
- GEARS is useful for ambiguous behavior contracts, but plain acceptance
  criteria are enough for small or non-workflow tasks.
- TRUST is a quality review rubric outside `/ms.*`; executable checks still come
  from the project's actual lint, type, test, build, and security tooling.

---

## 9. Codebase Exploration And System Map Handling

- When `graphify-out/graph.json` exists, structural exploration goes through
  the Graphify code graph first: `graphify query "<question>"` for broad
  context, `graphify path "<A>" "<B>"` for relationships, `graphify explain
  "<node>"` for one concept. Results are file:line pointers to verify by
  reading the cited files — never treat them as authoritative on their own.
- After modifying code, run `graphify update .` (AST-only, seconds, no API
  cost) so later queries in the session see your edits; the post-commit hook
  keeps the graph current between sessions.
- If the graph or the `graphify` binary is missing in a SPECTER-initialized
  project, say so explicitly and fall back to `rg`, `find`, and `git`; setup
  lives in `/ms.init` Step 2.9. Never block work on a missing graph.
- `docs/SYSTEM_MAP.md` is a curated prose snapshot — purpose, workflows,
  invariants, risk areas, verification commands — not a structural inventory.
  If it exists, read it before non-trivial coding or workflow changes, check
  its `git_head`/`stale_when` metadata before relying on it, and refresh it
  via the `.claude/skills/codebase-snapshot/SKILL.md` procedure when stale.
  Structural facts (file lists, counts, call relationships) belong to the
  graph or a live `rg`/`find` scan, never to the map.

---

## 10. SPECTER Command / Skill / Agent Layout

SPECTER is a command-driven wrapper over GitHub Spec-Kit.

- `.claude/commands/` holds explicit `/ms.*` entrypoints; do not convert them
  into skills.
- `.claude/skills/` holds reusable rules and validators.
- `.claude/agents/` holds specialist roles; author-only workflow agents are not
  required.
- `/ms.pre-specter` runs `featuremap → featuremap-checklist → pre-verify →
  constitution`.
- `/ms.specter` runs `checklist → verify → specify → clarify → plan → tasks →
  analyze → implement → review`.
- `/ms.prd` co-authors PRDs before the conductors. `/ms.expand` consumes an
  appended PRD Amendment and refreshes the derived Feature Map. `/ms.audit`
  remains advisory.

### Lean verification contract

Verification is state-free. `specter-gate.sh` checks structural prerequisites
and reduces two station-fixed reviewer reports against the current input bundle
hash. It writes no receipts, round state, risk profiles, typed decisions, or
approval records. Both reviewers available means worst-of; one unavailable caps
a non-FAIL result at WARN; both unavailable is FAIL. A station may rerun once,
only after its inputs change.

Legacy Verification-v2 receipts, round reports, signal tables, D-IDs, and
profiles are tolerated but ignored. An in-flight station gets one lean recheck.
Only `/ms.clarify` is a mandatory human stop inside the Feature cycle. Other
commands return PASS/WARN/FAIL; WARN advances and FAIL terminates without asking
for acknowledgment.

### Progressive authority

PRD and Amendments own product intent and explicit boundaries. The Feature Map
is a mutable derived index that owns decomposition, ownership, order, and DAG;
spec owns observable behavior; plan owns technical design; tasks own execution
partition; code and tests own observed reality. Legitimate downstream refinement
and reality correction do not require literal upstream wording. A new actor or
journey, external integration, retained-data category, permission boundary, paid
capability, or explicit boundary conflict routes to `/ms.clarify` with a
proposed upstream patch.

Unpromised ideas live in `docs/prd/opportunities.md`, which gates and reviewers
do not load. Promotion requires a PRD Amendment via `/ms.expand`.

### Integration invariants

- Spec-Kit may emit command or native-skill layouts. `/ms.init` patches every
  existing specify candidate.
- Keep the `MS_FEATUREMAP_GATE_START` prompt guard and the direct-call hook.
  Direct `/speckit-specify` cannot bypass the Feature Map, checklist,
  Constitution, and per-Feature verification gates; `/ms.specify` refuses
  freeform input.
- Use `--integration claude`; legacy `--ai` flags are unsupported.
- `/ms.init` pins `SPEC_KIT_REF`. Wrappers delegate to the hyphenated
  upstream skills by name. If the pin or names change, update wrappers and the
  README compatibility table together.
- Adapt names, paths, versions, and flags only. Never weaken GEARS, TAG chains,
  Constitution Section IX, direct-call protection, or SPECTER-owned gates to
  accommodate upstream. That is the divorce tripwire.

---

## 11. Pre-Work Checklist

- For exploration: did I query the Graphify graph first if
  `graphify-out/graph.json` exists, instead of fanning out `rg`/`Read`?
- Have I read `docs/SYSTEM_MAP.md`'s curated invariants/risks if it exists, and
  checked whether it is stale for this task?
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

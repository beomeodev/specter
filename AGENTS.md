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
- Subagent dispatch discipline: hand artifacts over as **file paths, not pasted
  content** — everything pasted into a dispatch prompt or printed back stays
  resident in context for the rest of the session (brief → file, report → file).
  Pick the least powerful model sufficient for the role (mechanical single-file
  work → cheap tier; integration → standard; architecture and final review → most
  capable), but remember **turn count beats token price** — a cheap model that
  needs 3× the turns can cost more overall. Specify the model explicitly when
  dispatching.
- Do not re-read a file you already read this session. Reuse what you have
  unless the user explicitly says its content changed. Exception: the harness
  requires a fresh `Read` of a file immediately before `Edit`/`Write`; always
  satisfy that requirement even when the content is already in context.

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
is cohesive. This is the default for every track (`/ms.fin`, `/ms.fix`,
`/ms.amend`, and direct commits).

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

SPECTER is a command-driven workflow wrapper over GitHub Spec-Kit. Respect the
intended hybrid structure; do not migrate it to a different shape on a whim.

- `.claude/commands/` holds the `/ms.*` files. These are **explicit user-invoked
  workflow entrypoints** and must stay commands. Do not convert `/ms.*` commands
  into skills, and do not remove `.claude/commands`.
- Conductors and tracks (behavior details live in each command file; all of these stay
  commands, never skills):
  - `/ms.specter` — per-Feature cycle conductor (checklist → … → review, one human stop at
    clarify). It never weakens or bypasses the gates it invokes: it only reads verdicts,
    advances on PASS/WARN, stops on FAIL, and is bound by the same Feature-Map /
    direct-call-bypass gates as the steps it drives.
  - `/ms.pre-specter` — one-time PRD-setup conductor (featuremap → codex-checklist →
    verify → constitution), same conductor discipline; hands the first Feature to
    `/ms.specter`.
  - `/ms.prd` — pre-workflow PRD co-authoring; sits before `/ms.pre-specter`, never invoked
    by any conductor, runs no gates; output feeds `/ms.pre-specter` or `/ms.expand`.
  - `/ms.expand` — incremental-PRD track between `/ms.fix` and `/ms.pre-specter`; consumes
    an appended `## PRD Amendment N`, extends the Feature Map append-only (refusing edits
    to existing PRD text or Feature sections), and hands the new Feature to `/ms.specter`.
  - `/ms.audit` — advisory product-level audit, in no conductor, blocks nothing; findings
    route to `/ms.fix` / `/ms.expand` / todo. It reports gate-value evidence but never
    weakens or edits a gate itself.
- `.claude/skills/` holds **reusable capabilities** — validators, rules, rubrics,
  and checklists. Put reusable logic here, not new top-level commands.
- `.claude/agents/` holds **specialist subagents** (role-based reasoning/execution).
- Upstream Spec-Kit may emit its Claude integration as either
  `.claude/commands/speckit.*.md` (command layout) or
  `.claude/skills/speckit-*/SKILL.md` (native-skill layout), or both. `/ms.init`
  patches every candidate file that exists; do not hardcode a single upstream path.
- Keep the direct-call bypass guard intact: `/ms.init` injects the Feature Map +
  checklist + Constitution gate (marker `MS_FEATUREMAP_GATE_START`) into the
  upstream `speckit specify` file. Direct `/speckit.specify` must never bypass
  `/ms.specify`'s gates, and `/ms.specify` must never accept freeform feature input.
- Use `--integration claude` for Spec-Kit installs; the legacy `--ai` flags are
  removed upstream.
- **Loose coupling**: `/ms.init` pins upstream via `SPEC_KIT_REF` (default a verified
  release) so upstream churn cannot silently break the wrappers. The `/ms.*` wrappers
  delegate to upstream skills **by name** (current form is hyphenated: `/speckit-specify`,
  `/speckit-plan`, `/speckit-tasks`, `/speckit-clarify`, `/speckit-analyze`,
  `/speckit-implement`). These delegation names are the single coupling surface — if the pin
  moves or upstream renames again, update the wrappers and the table in README
  "Spec Kit 호환성 → 위임 지점". Do not reimplement the upstream engines unless a full
  divorce from Spec-Kit is explicitly decided.
- **Identity is non-negotiable**: when adapting to upstream, conform on *names, paths,
  versions, and flags* only. Never weaken SPECTER's gates to fit Spec-Kit: the Feature-Map /
  freeform-refusal / direct-call-bypass guard, GEARS reaching new specs, TAG chains,
  Constitution Section IX, Codex verification, and SPECTER owning its own gates (not
  delegating them to Spec-Kit's CLI flags). If keeping a gate intact would require giving up
  one of these, that is the **divorce tripwire** — see README "Spec Kit 호환성 → 결별 기준".

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

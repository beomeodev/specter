---
generated_at: 2026-07-06T03:11:08Z
git_head: 46bb57d364df8dcdc3a20eea618e980ec2948103
git_head_short: 46bb57d
git_branch: master
working_tree: clean
scope:
  - AGENTS.md
  - README.md
  - CHANGELOG.md
  - .claude/
  - docs/
  - docs/templates/
  - docs/ops/
  - scripts/
  - tests/
  - backend/
  - frontend/
  - pyproject.toml
  - .mcp.json
  - .pre-commit-config.yaml
tools:
  - git
  - rg
  - find
  - uv run pytest --cov
serena: unavailable
stale_when:
  - git_head differs from current HEAD
  - changed files overlap documented hot paths or invariants
  - command, agent, skill, template, or workflow files are modified
---

# System Map

## Snapshot Status
HEAD is `46bb57d` on `master` with a clean working tree. The 2026-07-06 audit patch has
landed as four commits (gates alignment, command-contract repairs, agents/skills residue
cleanup, repo hygiene) — see `CHANGELOG.md [Unreleased]` and the commit messages for the
per-file rationale. This snapshot describes that committed state.

## System Purpose
SPECTER is a command-driven workflow wrapper over GitHub Spec-Kit for Claude Code projects. This
repository is the **template/tooling repo itself** — it ships the `/ms.*` command definitions,
skills, agents, Constitution/spec templates, and deterministic gate scripts that a consuming
project installs via `/ms.init`. There is no application runtime here; `backend/`/`frontend/` are
template scaffolding (`backend/AGENTS.md`; `frontend/AGENTS.md` + `frontend/package.json`), not a
shipped app.

## Repository Shape
- `AGENTS.md`: repository-wide agent contract (this file's own contents, at the top of every
  session's context). Modified in the working tree: the per-command "session read policy" prose
  was consolidated into pointers at `AGENTS.md §2` (verified: 10 command files now say "see
  AGENTS.md §2" instead of restating the policy).
- `README.md`, `CHANGELOG.md`: public entry point + release notes. `CHANGELOG.md` now carries an
  `## [Unreleased]` section (verified) documenting `/ms.sync`, `/ms.prd`, `/ms.audit`, the six new
  workflow skills, the `/ms.fin` High-Stakes Diff Digest, and `/ms.review`'s Migration Rollback
  analysis (6.6b) — all ahead of any tag.
- `.claude/commands/` (25 files): the `/ms.*` slash-command definitions. Confirmed via `ls`:
  `ms.agent-verify`, `ms.amend`, `ms.analyze`, `ms.audit`, `ms.checklist`, `ms.clarify`,
  `ms.codex-checklist`, `ms.constitution`, `ms.expand`, `ms.featuremap`, `ms.fin`, `ms.fix`,
  `ms.implement`, `ms.init`, `ms.merglease`, `ms.plan`, `ms.prd`, `ms.pre-specter`, `ms.review`,
  `ms.specify`, `ms.specter`, `ms.sync`, `ms.tasks`, `ms.up-docs`, `ms.verify`. There is **no**
  `ms.codex-verify.md` anywhere in the tree (renamed to `ms.agent-verify.md`); no "My-Spec"
  naming remains (`rg -ri "my-spec|myspec"` returns nothing in `.claude/`, `README.md`,
  `AGENTS.md`). The `codex-verify`/`antigravity-verify` strings that remain (e.g. in
  `ms.agent-verify.md`, `ms.specter.md`, `README.md`) are per-Feature **artifact filenames**
  (`feature-NNN.codex-verify.md`), not a command name — expected and correct.
- `.claude/skills/` (26 dirs + `skill-rules.json`): reusable capabilities. Confirmed via `ls`:
  `api-testing-patterns`, `ci-cd-optimization`, `codebase-snapshot`, `cross-cutting-concerns`,
  `git-worktrees`, `ms-architecture-patterns`, `ms-database-design`, `ms-design-baseline`,
  `ms-essentials-debug`, `ms-essentials-review`, `ms-foundation-constitution`,
  `ms-foundation-ears`, `ms-foundation-prd`, `ms-foundation-trust`, `ms-lang-python`,
  `ms-lang-typescript`, `ms-ops-debugging`, `ms-workflow-living-docs`, `ms-workflow-tag-manager`,
  `overnight-run`, `parallel-features`, `specter-agent-protocols` (new, untracked — see below),
  `spike`, `testing-skills-with-subagents`, `transcript-mining`, `webapp-testing`. Several
  `SKILL.md`/`examples.md` files are modified in the working tree (`ms-essentials-debug`,
  `ms-essentials-review`, `ms-foundation-constitution`, `ms-foundation-trust`, `ms-lang-python`,
  `ms-lang-typescript`, `ms-workflow-living-docs`, `ms-workflow-tag-manager`, `webapp-testing`,
  `skill-rules.json`); `ms-foundation-trust/examples_old.md` was deleted.
  `specter-agent-protocols` has **no `skill-rules.json` prompt-trigger entry** (confirmed by
  `grep` — zero hits) because it is a reference-only skill pulled in by command prose
  (`/ms.agent-verify`, `/ms.verify`, `/ms.analyze`, `/ms.review`, `/ms.codex-checklist`,
  `/ms.expand`), not something an end user triggers by keyword.
- `.claude/agents/` (17 files): specialist subagent definitions. Confirmed via `ls`:
  `code-refactor-master`, `codebase-explorer`, `constitution-extractor`, `debug-helper`,
  `doc-updater`, `git-hygiene`, `implementation-planner`, `integration-designer`,
  `library-researcher`, `local-ci`, `quality-gate`, `refactor-planner`, `spec-builder`,
  `tag-auditor`, `tdd-implementer`, `trust-validator`, `web-research-specialist`. 14 of these are
  modified in the working tree; `rg "Model Selection"` over `.claude/agents/*.md` returns zero
  hits (the ceremony block is gone, matching context). `quality-gate.md` still reports
  CRITICAL/severity findings but explicitly defers the block/warn/approve decision to
  `/ms.review` ("blocking decisions belong to /ms.review's call", "→ /ms.review decides
  approve/warn/block based on the report") — it no longer owns blocking policy itself.
- `docs/templates/`: Constitution/spec templates (`constitution-template.md` modified) +
  `docs/templates/scripts/`: `check_feature_map_gate.py`-equivalent installers, plus
  `specter-gate.sh`, `speckit-specify-gate-hook.sh`, `specter-overnight.sh`,
  `specter-session-status.sh` (all confirmed present via `ls`).
- `docs/ops/`: operational runbooks not tied to a command file (e.g.
  `antigravity-write-flag.md`).
- `docs/improvements/`: dated audit/plan documents (working record, not templates).
- `docs/src/lib/`: TypeScript reference implementations of TAG scanning/generation and TRUST
  level checks — source material the command prose describes, not code in the gate path.
- `docs/log/`: **deleted** in the working tree (`docs/log/pre-commit/*.log`, 4 files removed via
  `git status`) — this directory no longer exists.
- `scripts/` (repo root): `check_feature_map_gate.py` (unchanged this patch — `git diff` shows no
  delta) and `check_tag_chain.py` (modified — see Hot Paths), plus `specter_sync.py` +
  `specter_sync_manifest.json` (the `/ms.sync` broadcast engine).
- `tests/`: `test_check_feature_map_gate.py`, `test_check_tag_chain.py` (both new/untracked this
  patch) and `test_specter_sync.py`. All 28 tests pass; coverage 91.44% against an 85% floor
  (verified by running `uv run pytest --cov -q`).
- `backend/`, `frontend/`: scaffolding-only template directories, not a running app.
- `.env` → `.env.example` (renamed, tracked); real `.env` stays gitignored (`.gitignore` line 52
  confirms `.env` is ignored while the comment on line 51 notes `.env.example` is the tracked
  template).
- `.mcp.json`: declares `context7` and `serena` MCP servers. `serena`'s configured command
  (`/home/dev/.local/bin/serena start-mcp-server ...`) does **not resolve** in this environment
  (`which serena` and the literal path both fail) and no `serena__*` tool was offered in this
  session's deferred-tool list — hence `serena: unavailable` in the frontmatter, not
  `not_configured` (it *is* configured in `.mcp.json`; it just isn't reachable here).
- `pyproject.toml`: `dependencies = []` (first-party `scripts/`/`tests/` is stdlib-only by
  design, per its own comment); `[tool.coverage.run] source = ["backend", "scripts"]`,
  `fail_under = 85` in `[tool.coverage.report]`. Actual measured coverage this session: 91.44%.
- `docs/dev_daily.md`, `docs/todo.md`: append-only working log / scratchpad templates.
- `docs/SYSTEM_MAP.md`: this snapshot.

## Primary Workflows
- `/ms.init` bootstraps the workflow overlay into a consuming project (patches upstream Spec-Kit
  files, installs `docs/templates/scripts/*`, wires pre-commit hooks, and — new — copies
  `specter-overnight.sh` for the `overnight-run` skill). Step 2.8, "Wire The Pre-Commit Backstops
  (TAG chain + Feature Map coherence)", writes both `check_tag_chain.py` and
  `check_feature_map_gate.py` into the target project's `.pre-commit-config.yaml` and runs
  `pre-commit install` (verified at `.claude/commands/ms.init.md:350-389`).
- **Pre-Feature (one-time)**: `/ms.pre-specter` conducts `/ms.featuremap` →
  `/ms.codex-checklist` → `/ms.verify` → `/ms.constitution`. `/ms.expand` is the incremental
  alternative for a PRD Amendment instead of a full re-run. `/ms.prd` sits *before*
  `/ms.pre-specter` as a pre-workflow PRD co-authoring command (no gates, never invoked by a
  conductor).
- **Per-Feature**: `/ms.specter` conducts `/ms.checklist` → `/ms.agent-verify` → `/ms.specify` →
  `/ms.clarify` (human stop) → `/ms.plan` → `/ms.tasks` → `/ms.analyze` → `/ms.implement` →
  `/ms.review`.
- `/ms.fix` is the lightweight track for non-requirement changes (TDD+TAG+gate, no
  spec/clarify/plan/tasks ceremony) — `check_tag_chain.py` now has first-class support for it
  (see Hot Paths). `/ms.amend` records post-implementation decisions.
- `/ms.audit` is an advisory, product-level completeness audit outside any conductor; findings
  route to `/ms.fix`, `/ms.expand`, or `docs/todo.md` — it never edits or weakens a gate.
- `/ms.sync` broadcasts registered workflow files (commands/skills/agents/gate
  scripts/templates/`AGENTS.md`) to other registered project repos via 3-way merge
  (`scripts/specter_sync.py`, tested by `tests/test_specter_sync.py`).
- `/ms.fin` / `/ms.merglease` handle publish/release flows (delegated to Antigravity). `/ms.fin`'s
  High-Stakes Diff Digest now computes the diff as the unpushed range (`git diff "$BASE"...HEAD`)
  **plus** the working tree (`git diff HEAD`), explicitly to catch `/ms.fix`-track changes that
  never went through `/ms.review` (`.claude/commands/ms.fin.md:66-73`). `/ms.merglease` commits
  the Progress Ledger update (`docs/prd/feature-map.progress.md`) as its own step before tagging
  a release (`.claude/commands/ms.merglease.md:95-100`).
- `/ms.up-docs` synchronizes documentation after implementation.
- The dual-agent mechanics shared by `/ms.agent-verify`, `/ms.verify`, `/ms.analyze`,
  `/ms.review`, `/ms.codex-checklist`, and `/ms.expand` (session-level preflight, single-agent
  degrade rule, report-write/salvage protocol, re-round convergence caps) now live in one place:
  the `specter-agent-protocols` skill. Each command keeps only its own report paths and
  station-specific invariants inline instead of restating the mechanics.

## Hot Paths
- `scripts/check_tag_chain.py` — modified this patch to support the `/ms.fix` track: `FIX-*`
  `@CODE` ids (constant `FIX_PREFIX = "FIX-"`) carry no governing `@SPEC`, and a file may declare
  itself test-exempt via the literal marker `@TEST: (presentational — no test)` (regex
  `PRESENTATIONAL_RE`). Uniqueness still applies to FIX ids. Backed by the new
  `tests/test_check_tag_chain.py` (10 tests, all passing).
- `scripts/check_feature_map_gate.py` — unchanged this patch (`git diff` against HEAD is empty);
  now has its own test file `tests/test_check_feature_map_gate.py` (6 tests, all passing) where
  it previously had none.
- `.claude/commands/ms.review.md` — largest command file; owns the Result Model (READY / READY
  WITH WARNINGS / NOT READY), the executable gates, Done Criteria Execution, and dual-agent
  review; also owns Migration Rollback analysis (6.6b, per `CHANGELOG.md [Unreleased]`).
- `.claude/commands/ms.init.md` — Step 2.8 is the single place pre-commit backstop wiring is
  defined for consuming projects; also installs `specter-overnight.sh`.
- `.claude/skills/specter-agent-protocols/SKILL.md` — new canonical source for preflight/degrade/
  salvage/convergence mechanics shared by six dual-agent commands; edit here, not per-command, to
  change the shared mechanics.
- `.claude/skills/skill-rules.json` — auto-activation rules for every user-triggerable skill;
  needs an entry for each new *prompt-triggered* skill (not `specter-agent-protocols`, which is
  reference-only).
- `docs/templates/scripts/specter-gate.sh` — deterministic PASS/WARN/FAIL/MISSING gate checker
  consumed by `/ms.verify`/`/ms.checklist`.
- `.pre-commit-config.yaml` (repo root, and the copy `/ms.init` installs into consuming
  projects) — now wired to both `check_tag_chain.py` and `check_feature_map_gate.py`.

## State And Data Flow
- Workflow state is file-based: `docs/prd/feature-map.md` + `*.checklist.md` +
  `*.codex-verify.md`/`*.antigravity-verify.md` (per-Feature, produced in a consuming project —
  not present in this template repo itself), `.specify/memory/constitution.md`,
  `.specify/.ms-gate-pass-<NNN>` (short-lived token).
- `docs/prd/feature-map.progress.md` is a separate Progress Ledger kept out of the Feature Map's
  SHA256 so bookkeeping updates don't trigger false staleness; `/ms.merglease` now commits its
  own updates to this file as an explicit step.
- `docs/dev_daily.md` / `docs/todo.md`: append-only log / scratchpad.
- `docs/design/DESIGN.md` (new, per-consuming-project): generated by `ms-design-baseline` the
  first time a Feature ships a UI surface; read-not-regenerated by every later UI Feature.
- `CHANGELOG.md`: now carries a standing `## [Unreleased]` section that `/ms.merglease`
  presumably drains at release time (Progress Ledger + tag/release step).
- `docs/SYSTEM_MAP.md`: this refreshable snapshot.

## Runtime Paths
Not applicable — this repository ships no deployed application or server; `backend/`/`frontend/`
are unpopulated template scaffolding, and the `/ms.*` commands run inside a Claude Code session,
not as a hosted service. (Per the skill's own guidance: omit this section for pure
libraries/CLIs with no runtime surface.)

## Shared Modules And Single Sources Of Truth
- `AGENTS.md` — the always-on fallback contract; commands now point to `AGENTS.md §2` for
  session read policy instead of restating it per-command.
- `README.md` — Spec-Kit compatibility/delegation table (§ "Spec Kit 호환성 → 위임 지점").
- `CHANGELOG.md` — `## [Unreleased]` is the staging area for not-yet-tagged changes.
- `.claude/commands/*.md`, `.claude/skills/*/SKILL.md`, `.claude/skills/skill-rules.json`.
- `.claude/skills/specter-agent-protocols/SKILL.md` — single source of truth for dual-agent
  preflight/degrade/salvage/convergence mechanics (new this patch).
- `docs/templates/constitution-template.md`, `docs/templates/spec-template.md`.
- `docs/templates/scripts/specter-gate.sh` — the one place gate PASS/WARN/FAIL/MISSING logic is
  computed mechanically (as opposed to being judged by the model).
- `scripts/check_tag_chain.py` — single source of truth for `FIX-*`/presentational-exemption TAG
  rules; `FIX_PREFIX` and `PRESENTATIONAL_RE` are the two constants that define the rule.
- `.claude/skills/ms-design-baseline/assets/tokens.css` — once generated into a consuming
  project, the single source of truth for that project's design values (never inline new ones).

## Invariants
- Keep workflow changes surgical; do not weaken a gate to fit upstream Spec-Kit churn (README
  "정체성 불변식").
- `/ms.*` commands stay commands (never migrated to skills); `.claude/skills/` holds reusable
  capabilities, not new top-level entrypoints. Confirmed: all 25 `/ms.*` files remain under
  `.claude/commands/`, and the new dual-agent mechanics were extracted to a *skill* referenced by
  commands, not migrated out of command files entirely.
- Dual verification (Codex + Antigravity) is never silently skipped — an unavailable agent forces
  an explicit `UNAVAILABLE` record and a `WARN` degrade, never a silent PASS (now codified once in
  `specter-agent-protocols` §2 Degrade Rule instead of per-command).
- The `.specify/.ms-gate-pass-<NNN>` token is scoped to a single `/ms.specify` invocation and
  TTL-bounded (~1h) so a dead session can't leave a standing bypass.
- `docs/templates/scripts/specter-gate.sh` must always emit its JSON contract (never abort with
  no output), even when a checklist file is malformed.
- Preserve TAG (`@SPEC → @TEST → @CODE`/`@DOC`) traceability semantics when editing tagged code;
  the one sanctioned exception is the `/ms.fix` track's `FIX-*`/presentational carve-out in
  `check_tag_chain.py` — do not widen that exemption beyond FIX ids without updating the tests.
- `/ms.specify` must never accept freeform feature input; direct `/speckit.specify` (or its
  hyphenated `/speckit-specify` form) must never bypass the Feature-Map/checklist/Constitution
  gate `/ms.init` injects (marker `MS_FEATUREMAP_GATE_START`).

## Risk Areas
- `serena` is declared in `.mcp.json` but its configured binary path does not resolve in this
  environment (`/home/dev/.local/bin/serena`: no such file) and no Serena MCP tool was available
  this session — structural scans used `git`/`rg`/`find` only, as in the prior snapshot.
- `specter-agent-protocols` has no `skill-rules.json` trigger entry; if a future refactor expects
  every skill to be independently prompt-triggerable, this one is an intentional exception
  (reference-only, pulled in by six command files) — verify this is still true before assuming
  it's a gap.
- `docs/improvements/*.md` are historical working records, not templates — do not treat their
  content as currently-authoritative without checking whether it says DONE/PARTIAL/pending.
- `docs/log/` was deleted in this patch (4 pre-commit log files) — if any command or script still
  writes to `docs/log/pre-commit/`, confirm it recreates the directory rather than failing.
- Four skills from the prior snapshot (`webapp-testing`, `ms-foundation-prd`, `ms-design-baseline`,
  `ms-ops-debugging`) remain unexercised in a real consuming project — verified by fixture/dry-read
  only, not by an end-to-end `/ms.specter` run.

## Verification Commands
```bash
git status --short
git rev-parse HEAD
uv run pytest --cov -q          # 28 tests, 91.44% coverage, 85% floor
bash -n docs/templates/scripts/specter-gate.sh docs/templates/scripts/speckit-specify-gate-hook.sh
python3 -c "import json; json.load(open('.claude/skills/skill-rules.json'))"
rg -n "ms.codex-verify|My-Spec|MySpec" -ri .claude README.md AGENTS.md   # expect zero hits
rg -n "Model Selection" .claude/agents/*.md                              # expect zero hits
```

## Known Gaps
- No live consuming project in this repo to exercise `/ms.specter` end-to-end against the
  audit patch — verification was fixture/test-level (pytest) and read-back-level
  (skill/command prose), not a real workflow run.
- Serena MCP is configured in `.mcp.json` but not reachable in this session (binary missing); no
  symbol-level navigation was performed for this refresh.
- Per-file rationale for the 2026-07-06 audit patch lives in the four commit messages and
  `CHANGELOG.md [Unreleased]`, not in this map.

## Refresh Procedure
1. Read `AGENTS.md`, `.specify/memory/constitution.md` (if present), and any nested `AGENTS.md`
   under the area being touched.
2. Capture current git metadata (`git status --short`, `git rev-parse HEAD`, `git branch
   --show-current`).
3. Re-scan repository shape (`find . -maxdepth 2 -type d`, `find . -maxdepth 3 -type f`) and diff
   against the `Repository Shape` section above.
4. Re-check every path named in `Hot Paths` and `Shared Modules` still exists at the stated role.
5. Re-run `uv run pytest --cov -q` to confirm the coverage figure quoted here is still accurate.
6. Update sections with only verified facts; mark unresolved items under `Known Gaps` rather than
   guessing.

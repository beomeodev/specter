---
generated_at: 2026-07-03T08:51:21Z
git_head: f765f811c90a7fadd55b2ff576f07ac6e5eae842
git_head_short: f765f81
git_branch: master
working_tree: dirty
scope:
  - AGENTS.md
  - README.md
  - .claude/
  - docs/
  - docs/templates/
  - docs/ops/
  - scripts/
  - backend/
  - frontend/
  - .pre-commit-config.yaml
tools:
  - git
  - rg
  - find
  - curl
serena: not_configured
stale_when:
  - git_head differs from current HEAD
  - changed files overlap documented hot paths or invariants
  - command, agent, skill, template, or workflow files are modified
---

# System Map

## Snapshot Status
Refreshed at the end of a session that fixed a blocking gate-script bug (F-1) and executed a
15-item follow-up/reinforcement pass (F-2..F-5, S-1..S-8) against `.claude/commands` and
`.claude/skills`. Working tree is dirty by design — every command/skill file this map documents
was touched this session and is not yet committed. Refresh again once these land (or if they're
reverted) and again whenever the next non-trivial `.claude/` change lands.

## System Purpose
SPECTER is a command-driven workflow wrapper over GitHub Spec-Kit for Claude Code projects. This
repository is the **template/tooling repo itself** — it ships the `/ms.*` command definitions,
skills, agents, Constitution/spec templates, and deterministic gate scripts that a consuming
project installs via `/ms.init`. There is no application runtime here; `backend/`/`frontend/` are
template scaffolding (each currently just an `AGENTS.md`, plus a `package.json` in `frontend/`),
not a shipped app.

## Repository Shape
- `AGENTS.md`: repository-wide agent contract (this file's own contents, at the top of every
  session's context).
- `README.md`: public workflow entry point, incl. the Spec-Kit compatibility/delegation table.
- `.claude/commands/` (22 files): the `/ms.*` slash-command definitions — the workflow's gates
  live here as prose the model follows, not as enforced code (except where a hook/script backs
  them, see Invariants).
- `.claude/skills/` (19 dirs + `skill-rules.json`): reusable capabilities — validators, rubrics,
  language/domain expertise, and now (as of this session) `webapp-testing`, `ms-foundation-prd`,
  `ms-design-baseline`.
- `.claude/agents/` (17 files): specialist subagent definitions used by the commands above.
- `docs/templates/`: Constitution/spec templates + `docs/templates/scripts/` (the deterministic
  gate/hook scripts a consuming project's `/ms.init` installs — see Hot Paths).
- `docs/ops/` (new this session): operational runbooks not tied to a command file, e.g.
  `antigravity-write-flag.md`.
- `docs/improvements/`: dated audit/plan documents (not templates) — the working record of what
  changed in the workflow itself and why.
- `docs/src/lib/`: TypeScript reference implementations of TAG scanning/generation (`lib/tag/`)
  and TRUST level checks (`lib/trust/`) — source material the command prose describes, not code
  that runs as part of the gate path.
- `scripts/` (repo root): `check_feature_map_gate.py`, `check_tag_chain.py` — pre-commit hook
  entry points (see `.pre-commit-config.yaml`).
- `backend/`, `frontend/`: scaffolding-only template directories, not a running app.
- `docs/dev_daily.md`, `docs/todo.md`: append-only working log / scratchpad templates.
- `docs/SYSTEM_MAP.md`: this snapshot.

## Primary Workflows
- `/ms.init` bootstraps the workflow overlay into a consuming project (patches upstream Spec-Kit
  files, installs `docs/templates/scripts/*` and the pre-commit hooks).
- **Pre-Feature (one-time)**: `/ms.pre-specter` conducts `/ms.featuremap` →
  `/ms.codex-checklist` → `/ms.verify` → `/ms.constitution`. `/ms.expand` is the incremental
  alternative for a PRD Amendment instead of a full re-run.
- **Per-Feature**: `/ms.specter` conducts `/ms.checklist` → `/ms.agent-verify` → `/ms.specify` →
  `/ms.clarify` (human stop) → `/ms.plan` → `/ms.tasks` → `/ms.analyze` → `/ms.implement` →
  `/ms.review`.
- `/ms.fix` is the lightweight track for non-requirement changes (TDD+TAG+gate, no
  spec/clarify/plan/tasks ceremony). `/ms.amend` records post-implementation decisions.
- `/ms.fin` / `/ms.merglease` handle publish/release flows (delegated to Antigravity).
- `/ms.up-docs` synchronizes documentation after implementation.

## Hot Paths
- `.claude/commands/ms.review.md` — largest command file; owns the Result Model (READY / READY
  WITH WARNINGS / NOT READY), the executable gates, Done Criteria Execution, and dual-agent
  review. Touched heavily this session (F-5, S-1, S-3, S-8 wiring).
- `.claude/commands/ms.verify.md`, `ms.checklist.md` — PRD/Feature-Map gate logic; consumed by
  `docs/templates/scripts/specter-gate.sh`.
- `docs/templates/scripts/specter-gate.sh` — deterministic PASS/WARN/FAIL/MISSING gate checker
  (WI-11). Fixed this session (F-1: `extract_field` no longer aborts the script on a missing
  field under `set -euo pipefail`).
- `docs/templates/scripts/speckit-specify-gate-hook.sh` — PreToolUse hook blocking direct
  `/speckit-specify` bypass (WI-13). Hardened this session (F-4: token TTL, jq-less fallback).
- `.claude/skills/skill-rules.json` — auto-activation rules for every skill; every new skill this
  session (`webapp-testing`, `ms-foundation-prd`, `ms-design-baseline`) needed an entry here too.
- `scripts/check_feature_map_gate.py`, `scripts/check_tag_chain.py` — pre-commit backstops (WI-12,
  WI-14) run via `.pre-commit-config.yaml`.

## State And Data Flow
- Workflow state is file-based: `docs/prd/feature-map.md` + `*.checklist.md` +
  `*.codex-verify.md`/`*.antigravity-verify.md` (per-Feature, produced in a consuming project —
  not present in this template repo itself), `.specify/memory/constitution.md`, `.specify/.ms-gate-pass-<NNN>`
  (short-lived token, see Invariants).
- `docs/prd/feature-map.progress.md` is a separate Progress Ledger kept out of the Feature Map's
  SHA256 so bookkeeping updates don't trigger false staleness.
- `docs/dev_daily.md` / `docs/todo.md`: append-only log / scratchpad.
- `docs/SYSTEM_MAP.md`: this refreshable snapshot.
- `docs/design/DESIGN.md` (new, per-consuming-project): generated by `ms-design-baseline` the
  first time a Feature ships a UI surface; read-not-regenerated by every later UI Feature.

## Shared Modules And Single Sources Of Truth
- `AGENTS.md` — the always-on fallback contract (this file).
- `README.md` — Spec-Kit compatibility/delegation table (§ "Spec Kit 호환성 → 위임 지점").
- `.claude/commands/*.md`, `.claude/skills/*/SKILL.md`, `.claude/skills/skill-rules.json`.
- `docs/templates/constitution-template.md`, `docs/templates/spec-template.md`.
- `docs/templates/scripts/specter-gate.sh` — the one place gate PASS/WARN/FAIL/MISSING logic is
  computed mechanically (as opposed to being judged by the model).
- `.claude/commands/ms.review.md`'s `### Result Model` subsection (new this session, F-5) — the
  one place the READY/READY WITH WARNINGS/NOT READY computation is defined; Steps 6.5/6.6/6.7
  reference it rather than restating it.
- `.claude/skills/ms-design-baseline/assets/tokens.css` — once generated into a consuming
  project, the single source of truth for that project's design values (never inline new ones).

## Invariants
- Keep workflow changes surgical; do not weaken a gate to fit upstream Spec-Kit churn (README
  "정체성 불변식").
- `/ms.*` commands stay commands (never migrated to skills); `.claude/skills/` holds reusable
  capabilities, not new top-level entrypoints.
- Dual verification (Codex + Antigravity) is never silently skipped — an unavailable agent forces
  an explicit `UNAVAILABLE` record and a `WARN` degrade, never a silent PASS.
- The `.specify/.ms-gate-pass-<NNN>` token is scoped to a single `/ms.specify` invocation, now
  additionally TTL-bounded (~1h, added this session) so a dead session can't leave a standing
  bypass.
- `docs/templates/scripts/specter-gate.sh` must always emit its JSON contract (never abort with
  no output), even when a checklist file is malformed — this was violated (F-1) and fixed this
  session; re-verify with fixtures after any future edit to `extract_field`.
- Preserve TAG (`@SPEC → @TEST → @CODE`/`@DOC`) traceability semantics when editing tagged code.

## Risk Areas
- Working tree is dirty with a large, uncommitted multi-file change spanning 8 command files, 5
  skill files, 3 new skill directories, `skill-rules.json`, and 2 scripts — read `git status`/`git
  diff` before assuming any of this is landed.
- `docs/templates/scripts/*.sh` are templates copied into consuming projects by `/ms.init`; a
  project initialized before this session's F-1/F-4 fixes still carries the old, buggy copies —
  this is not automatically backfilled.
- Three new skills (`webapp-testing`, `ms-foundation-prd`, `ms-design-baseline`) are unexercised
  in a real consuming project as of this snapshot — verified by fixture/dry-read only, not by an
  end-to-end `/ms.specter` run.
- `docs/improvements/*.md` are historical working records, not templates — do not treat their
  content as currently-authoritative without checking whether it says DONE/PARTIAL/pending.

## Verification Commands
```bash
git status --short
git rev-parse HEAD
bash -n docs/templates/scripts/specter-gate.sh docs/templates/scripts/speckit-specify-gate-hook.sh
python3 -c "import json; json.load(open('.claude/skills/skill-rules.json'))"
rg -n "Source Command" .claude/ docs/templates/  # expect zero hits outside docs/improvements/
rg -n "webapp-testing|ms-foundation-prd|ms-design-baseline" .claude/skills/skill-rules.json
```

## Known Gaps
- No live consuming project in this repo to exercise `/ms.specter` end-to-end against the
  session's changes — verification here was fixture-level (gate scripts) and read-back-level
  (skill/command prose), not a real workflow run.
- `ms-ops-debugging` (S-9 in `docs/improvements/2026-07-03-skills-reinforcement-plan.md`) was
  deliberately not built this session — it requires mining a different project's transcripts and
  was scoped as its own session.
- Serena MCP was not configured/available in this session; structural scans used `find`/`rg`/`git`
  only.

## Refresh Procedure
1. Read `AGENTS.md`, `.specify/memory/constitution.md` (if present), and any nested `AGENTS.md`
   under the area being touched.
2. Capture current git metadata (`git status --short`, `git rev-parse HEAD`, `git branch
   --show-current`).
3. Re-scan repository shape (`find . -maxdepth 2 -type d`, `find . -maxdepth 3 -type f`) and diff
   against the `Repository Shape` section above.
4. Re-check every path named in `Hot Paths` and `Shared Modules` still exists at the stated role.
5. Update sections with only verified facts; mark unresolved items under `Known Gaps` rather than
   guessing.

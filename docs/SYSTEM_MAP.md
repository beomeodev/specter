---
generated_at: 2026-06-18T05:22:41Z
git_head: 8931d5522544b3d2dd2afcc6a1bdbda5f9bf2b11
git_head_short: 8931d55
git_branch: master
working_tree: dirty
scope:
  - AGENTS.md
  - README.md
  - Makefile
  - pyproject.toml
  - frontend/package.json
  - .claude/
  - .devcontainer/
  - backend/
  - docs/
  - frontend/
tools:
  - find
  - git
  - rg
  - sed
serena: configured
stale_when:
  - git_head differs from current HEAD
  - changed files overlap documented hot paths or invariants
  - command, agent, skill, template, or workflow files are modified
---

# System Map

## Snapshot Status

This map describes the repository at commit
`8931d5522544b3d2dd2afcc6a1bdbda5f9bf2b11` on branch `master`.

The working tree was dirty when this snapshot was created:

- `.devcontainer/Makefile`
- `docs/DOCKER_README.md`
- `docs/todo.md`

Serena MCP is configured in `.claude/mcp_servers.json` and `.mcp.json` after
this snapshot's initial scan. The map content was produced with `find`, `rg`,
`sed`, and `git`; refresh with Serena for symbol-level code navigation when the
MCP server is active.

## System Purpose

SPECTER is a workflow overlay for AI-assisted software development. It layers
project rules, slash commands, subagents, skills, traceability conventions, and
documentation templates on top of GitHub Spec-Kit style `/speckit.*` workflows.

The repository currently behaves more like a reusable workflow/template project
than an application codebase. The checked backend and frontend areas are mostly
placeholders; the main implementation surface is `.claude/`, `docs/`, root
instructions, and project setup files.

## Repository Shape

- `AGENTS.md`: always-on coding assistant rules and fallback project contract.
- `README.md`: user-facing entry point and canonical SPECTER workflow overview.
- `.claude/commands/`: slash command definitions for `/ms.*`, `/fin`, and
  `/finq`.
- `.claude/agents/`: subagent definitions used by command workflows.
- `.claude/skills/`: reusable skill definitions and activation metadata.
- `.claude/mcp_servers.json`: Claude Code MCP server configuration; currently
  includes `context7` and `serena`.
- `.mcp.json`: project MCP server configuration mirroring the Claude Code MCP
  server entries.
- `.devcontainer/`: container and local development helper scripts.
- `docs/`: workflow notes, templates, changelog, daily logs, and this system map.
- `docs/templates/`: Constitution and spec templates.
- `docs/src/`: helper library documentation for TAG and TRUST utilities.
- `backend/`: contains `backend/AGENTS.md`; no backend source files were present
  in the scan.
- `frontend/`: contains `frontend/AGENTS.md` and a minimal `package.json` with
  Prettier scripts.
- `pyproject.toml`: Python package metadata and dev tooling configuration.
- `Makefile`: delegates development environment targets to `.devcontainer`.

## Primary Workflows

The README documents the primary SPECTER flow:

1. `/ms.init`
2. `/ms.featuremap`
3. `/ms.checklist --global`
4. `/ms.constitution`
5. Per-feature cycle from `/ms.checklist` through `/ms.review`
6. `/fin` or `/finq`
7. `/ms.merglease`

Important command files include:

- `.claude/commands/ms.init.md`
- `.claude/commands/ms.featuremap.md`
- `.claude/commands/ms.checklist.md`
- `.claude/commands/ms.constitution.md`
- `.claude/commands/ms.specify.md`
- `.claude/commands/ms.clarify.md`
- `.claude/commands/ms.plan.md`
- `.claude/commands/ms.tasks.md`
- `.claude/commands/ms.analyze.md`
- `.claude/commands/ms.implement.md`
- `.claude/commands/ms.review.md`
- `.claude/commands/ms.up-docs.md`
- `.claude/commands/ms.amend.md`
- `.claude/commands/ms.fix.md`
- `.claude/commands/ms.merglease.md`
- `.claude/commands/fin.md`
- `.claude/commands/finq.md`

The `/ms.plan` workflow already references `codebase-explorer` for codebase
pattern discovery. The new `codebase-snapshot` skill complements that by
recording durable architecture context in this file.

## Hot Paths

- `AGENTS.md`: repository-wide safety, scope, testing, and permission rules.
- `README.md`: public workflow contract and command sequence.
- `.claude/commands/`: command behavior; edits can affect all generated specs,
  plans, tasks, reviews, PR, and release flows.
- `.claude/agents/codebase-explorer.md`: existing subagent for pattern search.
- `.claude/agents/implementation-planner.md`: coordinates planning and
  codebase exploration.
- `.claude/skills/skill-rules.json`: skill auto-activation suggestions.
- `.claude/skills/ms-*`: SPECTER workflow, language, TAG, TRUST, and review
  behavior.
- `docs/templates/constitution-template.md`: project governance template.
- `docs/templates/spec-template.md`: generated spec structure.
- `docs/ms-workflow-improvement.md`: known workflow gaps and improvement
  rationale.
- `.claude/mcp_servers.json`: MCP server availability for agents.
- `.devcontainer/`: local execution environment and helper commands.

## State And Data Flow

SPECTER's durable state is mostly file-based:

- PRDs and feature maps live under `docs/prd/` in downstream projects.
- Constitution state is expected at `.specify/memory/constitution.md` when a
  project has been initialized.
- Per-feature specs, plans, and tasks are expected under `specs/{feature}/`.
- TAG chains connect requirements, tests, code, and docs through `@SPEC`,
  `@TEST`, `@CODE`, and `@DOC` markers.
- Living documentation updates are recorded under `docs/`, especially
  `docs/dev_daily.md` and generated API or review docs in downstream projects.

In this repository snapshot, `.specify/memory/constitution.md`, `specs/`, and
`docs/prd/` were not present. Treat references to those paths as workflow
expectations for initialized downstream projects, not as current files.

## Shared Modules And Single Sources Of Truth

- Repository rules: `AGENTS.md`.
- Nested area rules: `backend/AGENTS.md`, `frontend/AGENTS.md`.
- Workflow overview: `README.md`.
- Slash command definitions: `.claude/commands/*.md`.
- Subagent definitions: `.claude/agents/*.md`.
- Skill definitions: `.claude/skills/*/SKILL.md`.
- Skill activation metadata: `.claude/skills/skill-rules.json`.
- Constitution template: `docs/templates/constitution-template.md`.
- Spec template: `docs/templates/spec-template.md`.
- Python tooling expectations: `pyproject.toml`.
- Frontend formatting expectations: `frontend/package.json`.

## Invariants

- Read relevant files before editing command, agent, skill, template, or rule
  files.
- Keep workflow changes surgical; command files are high blast-radius.
- Do not require Constitution artifacts for ordinary non-`/ms` coding work when
  no Constitution exists.
- For `/ms.*` workflows, command files and the active Constitution define gates
  and artifacts.
- Preserve traceability semantics when editing TAG, TRUST, GEARS, command, or
  template behavior.
- Do not make optional MCP tools such as Serena hard requirements unless the
  project configuration includes them.
- Do not claim validation passed unless the relevant command actually ran.

## Risk Areas

- The working tree was dirty at snapshot time; avoid overwriting unrelated
  changes in `.devcontainer/Makefile`, `docs/DOCKER_README.md`, or
  `docs/todo.md`.
- `docs/todo.md` notes a desired `SYSTEM_MAP.md` and codebase exploration skill;
  this file and `.claude/skills/codebase-snapshot/SKILL.md` are the first
  implementation of that direction.
- `.claude/commands/ms.plan.md` already has codebase-explorer integration; any
  later integration with this map should avoid duplicating contradictory
  planning rules.
- `.claude/settings.local.json` contains broad local tool permissions and should
  not be treated as a portable policy file.
- `.env` exists in the repository root scan. Do not inspect, copy, or document
  secret values.

## Verification Commands

Use the smallest relevant check for the touched area:

```bash
git status --short
rg -n "codebase-snapshot|SYSTEM_MAP|codebase-explorer" .claude docs README.md AGENTS.md
```

For Python helper changes:

```bash
python -m pytest
```

For frontend formatting changes:

```bash
npm --prefix frontend run format:check
```

Do not report these checks as passing unless they were run in the current task.

## Known Gaps

- Serena MCP was configured after the initial snapshot scan; this map has not
  yet been refreshed through Serena semantic tools.
- No `.specify/memory/constitution.md` was present.
- No `specs/` directory was present.
- No `docs/prd/` directory was present.
- `backend/` and `frontend/` contain minimal placeholder files in this snapshot,
  so there are no application runtime routes, services, or state transitions to
  map.

## Refresh Procedure

1. Read `AGENTS.md` and any nested `AGENTS.md` for the target area.
2. If present, read `.specify/memory/constitution.md`.
3. Capture git metadata:

   ```bash
   git status --short
   git branch --show-current
   git rev-parse HEAD
   git rev-parse --short HEAD
   ```

4. Re-scan structure:

   ```bash
   find . -maxdepth 2 -type d -not -path './.git*' | sort
   find . -maxdepth 3 -type f -not -path './.git/*' | sort
   ```

5. Search for changed workflow concepts:

   ```bash
   rg -n "SYSTEM_MAP|codebase-explorer|skill|Serena|MCP|TAG|TRUST|GEARS" .claude docs README.md AGENTS.md
   ```

6. If Serena is configured, use it for symbol overview and reference lookup in
   code-heavy areas, then record `serena: used`.
7. Update this file in place. Keep verified facts separate from inference.

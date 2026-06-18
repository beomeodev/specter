---
generated_at: 2026-06-18T13:41:11Z
git_head: fb1d1cdd37fb101591649eb456ef386b04a46a26
git_head_short: fb1d1cd
git_branch: master
working_tree: dirty
scope:
  - AGENTS.md
  - README.md
  - .claude/
  - docs/
  - docs/templates/
tools:
  - git
  - rg
  - sed
  - find
serena: configured
stale_when:
  - git_head differs from current HEAD
  - changed files overlap documented hot paths or invariants
  - command, agent, skill, template, or workflow files are modified
---

# System Map

## Snapshot Status
This is an agent-facing snapshot for the template repository. It is intentionally
concise and should be refreshed when the command or documentation surface changes.

## System Purpose
SPECTER is a reusable workflow overlay for Spec-Kit-style Claude Code projects.
This repository contains the command, skill, template, and guidance files that
shape that workflow.

## Repository Shape
- `AGENTS.md`: repository-wide agent contract.
- `README.md`: public workflow entry point.
- `.claude/commands/`: slash-command definitions.
- `.claude/skills/`: reusable workflow and helper skills.
- `.claude/agents/`: optional agent definitions.
- `docs/templates/`: reusable Constitution and spec templates.
- `docs/dev_daily.md`: append-only daily log template.
- `docs/todo.md`: lightweight working TODO template.
- `docs/SYSTEM_MAP.md`: this snapshot.

## Primary Workflows
- `/ms.init` bootstraps the workflow overlay.
- `/ms.featuremap` and `/ms.codex-checklist` produce PRD-level inputs.
- `/ms.verify` and `/ms.constitution` establish the shared baseline.
- `/ms.checklist` and `/ms.codex-verify` validate the next Feature.
- `/ms.specify`, `/ms.clarify`, `/ms.plan`, and `/ms.tasks` shape the feature
  into implementation-ready artifacts.
- `/ms.analyze`, `/ms.implement`, and `/ms.review` handle pre-implementation
  consistency, implementation, and post-implementation checks.
- `/fin` and `/finq` handle publish flows.

## Hot Paths
- `README.md`
- `AGENTS.md`
- `.claude/commands/`
- `.claude/skills/`
- `.claude/agents/`
- `docs/templates/`
- `docs/dev_daily.md`
- `docs/todo.md`

## State And Data Flow
- Workflow state is mostly file-based.
- `docs/dev_daily.md` is an append-only working log.
- `docs/todo.md` is a lightweight scratchpad for outstanding work.
- `docs/SYSTEM_MAP.md` is a refreshable snapshot for agents.

## Shared Modules And Single Sources Of Truth
- `AGENTS.md`
- `README.md`
- `.claude/commands/*.md`
- `.claude/skills/*/SKILL.md`
- `docs/templates/constitution-template.md`
- `docs/templates/spec-template.md`

## Invariants
- Keep workflow changes surgical.
- Do not claim a command ran unless it actually ran.
- Treat this map as stale-prone and refresh it when the repository changes.
- Preserve traceability semantics when editing TAG, GEARS, TRUST, or workflow files.

## Risk Areas
- Command and template files change frequently and can invalidate this snapshot.
- This repository is dirty, so git metadata must be read carefully before use.
- Deleted docs elsewhere in `docs/` should not be reintroduced unless they serve
  a template or workflow role.

## Verification Commands
```bash
git status --short
git branch --show-current
git rev-parse HEAD
rg -n "ms\.plan|ms\.implement|Reality Verified|SYSTEM_MAP|dev_daily|todo" README.md .claude docs
```

## Known Gaps
- No application runtime codebase is present here.
- This snapshot is intentionally higher-level than a full architecture map.

## Refresh Procedure
1. Read `AGENTS.md` and the relevant command docs.
2. Capture current git metadata.
3. Re-scan the repository shape with `rg --files` and targeted searches.
4. Update the sections above with only verified facts.

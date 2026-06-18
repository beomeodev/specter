---
name: codebase-snapshot
description: Agent-facing codebase exploration and SYSTEM_MAP maintenance skill. Use when starting a new task, creating or refreshing docs/SYSTEM_MAP.md, checking whether stored architecture knowledge is stale, mapping repository structure, identifying hot paths, invariants, state transitions, shared modules, validation commands, or recording codebase understanding with git metadata. Uses Serena MCP for symbol-level navigation when available, with rg/find/git fallback when Serena is unavailable.
---

# Codebase Snapshot

## Purpose

Create or refresh `docs/SYSTEM_MAP.md` so future agents can understand the
current codebase quickly without trusting stale memory.

This skill is for agents, not end-user documentation. Prefer precise, verifiable
facts over narrative explanations. Mark assumptions clearly.

## When To Use

- At the start of a non-trivial coding task.
- When `docs/SYSTEM_MAP.md` is missing.
- When `docs/SYSTEM_MAP.md` exists but its `git_head` differs from current HEAD.
- When touched paths overlap documented hot paths or invariants.
- Before planning work that depends on architecture, state flow, shared modules,
  test strategy, or command behavior.

## Inputs

- User request or feature/spec context.
- Current repository root.
- Existing `docs/SYSTEM_MAP.md`, if present.
- Current git metadata.

## Required Metadata

Record this at the top of `docs/SYSTEM_MAP.md`:

```yaml
---
generated_at: <UTC ISO-8601 timestamp>
git_head: <full commit SHA>
git_head_short: <short commit SHA>
git_branch: <branch name or detached>
working_tree: <clean|dirty>
scope:
  - <paths examined>
tools:
  - <tools used>
serena: <used|unavailable|not_configured>
stale_when:
  - git_head differs from current HEAD
  - changed files overlap documented hot paths or invariants
  - command, agent, skill, template, or workflow files are modified
---
```

If a command cannot run, record the failure under `Known Gaps`; do not invent
results.

## Exploration Procedure

1. Read repository instructions first:
   - `AGENTS.md`
   - nearest nested `AGENTS.md` files for the target area
   - `.specify/memory/constitution.md`, if it exists

2. Gather repository metadata:
   - `git status --short`
   - `git branch --show-current`
   - `git rev-parse HEAD`
   - `git rev-parse --short HEAD`

3. Map structure with cheap deterministic tools:
   - `find . -maxdepth 2 -type d -not -path './.git*' | sort`
   - `find . -maxdepth 3 -type f -not -path './.git/*' | sort`
   - `rg -n "<keyword>"` for workflow names, routes, services, tests, TAGs,
     commands, and config references.

4. Use Serena when available:
   - Use symbol overview and reference lookup for code-heavy projects.
   - Use Serena for cross-file symbol relationships, semantic navigation, and
     refactor-sensitive dependency checks.
   - If Serena is not configured, continue with `rg`, `find`, and `git`.
   - Record `serena: unavailable` or `serena: not_configured` in metadata.

5. Separate facts from inference:
   - Facts must cite concrete paths, commands, or observed files.
   - Inferences must be labeled as such and kept short.

## SYSTEM_MAP.md Structure

Use these sections:

```markdown
# System Map

## Snapshot Status
## System Purpose
## Repository Shape
## Primary Workflows
## Hot Paths
## State And Data Flow
## Shared Modules And Single Sources Of Truth
## Invariants
## Risk Areas
## Verification Commands
## Known Gaps
## Refresh Procedure
```

### Section Guidance

- `Snapshot Status`: summarize whether the map is current for the recorded HEAD.
- `System Purpose`: one paragraph describing what the repository exists to do.
- `Repository Shape`: list main directories and their roles.
- `Primary Workflows`: explain user/agent workflows and command sequence.
- `Hot Paths`: files or directories most likely to affect behavior.
- `State And Data Flow`: persisted artifacts, generated docs, command flow, or
  runtime state transitions.
- `Shared Modules And Single Sources Of Truth`: constants, templates, rules,
  command definitions, AGENTS files, Constitution, config.
- `Invariants`: rules agents must not violate.
- `Risk Areas`: stale docs, broad workflow edits, dirty worktree, security or
  permission risks.
- `Verification Commands`: smallest relevant checks for the repository.
- `Known Gaps`: missing tools, incomplete scans, absent source areas.
- `Refresh Procedure`: exact steps to regenerate the map.

## Quality Bar

- Keep it concise enough to read before work begins.
- Do not dump full file trees.
- Do not claim tests or tooling passed unless run.
- Do not hide dirty working tree state.
- Do not make Serena a hard dependency.
- Prefer updating an existing section over appending duplicate summaries.

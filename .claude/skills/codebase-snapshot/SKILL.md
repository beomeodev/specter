---
name: codebase-snapshot
description: Agent-facing codebase exploration and SYSTEM_MAP maintenance skill. Use when starting a new task, creating or refreshing docs/SYSTEM_MAP.md, checking whether stored architecture knowledge is stale, or recording invariants, risk areas, and verification commands with git metadata. Structural facts (file lists, call relationships, hot paths) are answered by the Graphify code graph when graphify-out/graph.json exists — this skill maintains the curated prose the graph cannot express. Uses Serena MCP for symbol-level navigation when available, with rg/find/git fallback.
---

# Codebase Snapshot

## Purpose

Create or refresh `docs/SYSTEM_MAP.md` so future agents can understand the
current codebase quickly without trusting stale memory.

This skill is for agents, not end-user documentation. Prefer precise, verifiable
facts over narrative explanations. Mark assumptions clearly.

## Division Of Labor With Graphify

When `graphify-out/graph.json` exists (installed by `/ms.init` Step 2.9, kept
current by post-commit hooks), the map and the graph split cleanly:

- **Graph owns structure**: file inventories, symbol locations, call/import
  relationships, "what connects A to B". Answer these with `graphify
  query/path/explain` — never by writing them into SYSTEM_MAP.md, where they go
  stale by the next commit.
- **Map owns curated prose**: system purpose, workflow semantics, invariants,
  risk areas, verification commands, runtime-path diagrams — knowledge a parser
  cannot extract. This content is deliberately slow-moving, which is what keeps
  the map trustworthy between refreshes.
- Never paste Graphify output (GRAPH_REPORT.md, wiki, query results) into
  SYSTEM_MAP.md: `graphify-out/` is regenerated state; embedding it recreates
  the staleness problem the split exists to solve.

Where no graph exists (e.g. a prose-heavy repo like the SPECTER template
itself), structural questions fall back to `rg`/`find` at ask-time — still not
to inventory sections in the map.

## When To Use

- At the start of a non-trivial coding task.
- When `docs/SYSTEM_MAP.md` is missing.
- When `docs/SYSTEM_MAP.md` exists but its `git_head` differs from current HEAD.
- When touched paths overlap documented invariants or shared modules.
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
graphify: <used|available|unavailable|not_installed>
serena: <used|configured|unavailable|not_configured>
stale_when:
  - git_head differs from current HEAD
  - changed files overlap documented invariants or shared modules
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

3. Map structure with the cheapest tool available:
   - If `graphify-out/graph.json` exists, prefer `graphify query "<question>"`,
     `graphify path "<A>" "<B>"`, and `graphify explain "<node>"` — treat the
     returned file:line pointers as leads to verify, not as truth.
   - Otherwise (or to verify graph results):
     `find . -maxdepth 2 -type d -not -path './.git*' | sort`,
     `find . -maxdepth 3 -type f -not -path './.git/*' | sort`, and
     `rg -n "<keyword>"` for workflow names, routes, services, tests, TAGs,
     commands, and config references.

4. Use Serena when available:
   - Use symbol overview and reference lookup for code-heavy projects.
   - Use Serena for cross-file symbol relationships, semantic navigation, and
     refactor-sensitive dependency checks.
   - If Serena is configured but not useful for the current scan, record
     `serena: configured`.
   - If Serena is not configured, continue with `rg`, `find`, and `git`.
   - Record `serena: unavailable` or `serena: not_configured` when applicable.

5. Separate facts from inference:
   - Facts must cite concrete paths, commands, or observed files.
   - Inferences must be labeled as such and kept short.

## Feature-Scoped Exploration (pre-implementation)

When the trigger is a specific feature request rather than a map refresh, run a
narrower pass and report it inline (no SYSTEM_MAP edit needed). If the Graphify
graph exists, start each numbered step with a graph query (`graphify query`,
`graphify path`) and use Glob/Grep to verify the returned pointers:

1. **Similar implementations** — Glob/Grep for features of the same class; read
   the closest one end to end.
2. **Conventions to copy** — folder placement, naming (files/functions/classes),
   error-handling and test-file patterns the similar feature follows.
3. **Reusable components** — existing utilities/validators/types that the new
   work must reuse instead of re-creating (single source of truth).
4. **Integration points** — where the similar feature registers itself (routes,
   DI, exports) and the data flow it participates in.

Report specific file paths, not generic advice; if no similar feature exists,
say so explicitly. This replaces the retired `codebase-explorer` agent.

## SYSTEM_MAP.md Structure

Use these sections:

```markdown
# System Map

## Snapshot Status
## System Purpose
## Primary Workflows
## State And Data Flow
## Runtime Paths
## Shared Modules And Single Sources Of Truth
## Invariants
## Risk Areas
## Verification Commands
## Known Gaps
## Refresh Procedure
```

There are deliberately **no** `Repository Shape` or `Hot Paths` sections:
per-file inventories and "modified this patch" facts go stale on the next
commit and belong to the Graphify graph (or a live `rg`/`find` scan), not to
this map. If an older map still carries them, drop them at the next refresh.

### Section Guidance

- `Snapshot Status`: summarize whether the map is current for the recorded HEAD.
- `System Purpose`: one paragraph describing what the repository exists to do.
- `Primary Workflows`: explain user/agent workflows and command sequence.
- `State And Data Flow`: persisted artifacts, generated docs, command flow, or
  runtime state transitions.
- `Runtime Paths` (**required for any project that gets deployed or serves
  requests**; omit for pure libraries/CLIs with no runtime surface): two text
  diagrams the human can study to hold the system's layers in their head —
  environment-boundary failures (SSH/TLS/proxy/secret-rotation classes) are
  diagnosed by knowing which layer to probe, and that knowledge lives here.
  1. **Request path** — every hop a request crosses, with the port/config file
     that defines each hop:
     ```text
     browser → DNS/tunnel (cloudflared, config: ...) → reverse proxy
     (Caddy :443→:8080, Caddyfile route matchers: ...) → app (uvicorn :8080,
     entrypoint: ...) → DB (postgres :5432, container: ...)
     ```
  2. **Secret path** — for each secret class: where it is born → where it is
     stored → how it is injected at runtime → what validates it:
     ```text
     SESSION_KEY: generated by bootstrap script → .env on host →
     docker-compose environment: → FastAPI session middleware
     ```
  Derive both from actual config files (compose, proxy config, env templates),
  not from assumption — cite the file next to each hop. Keep each diagram under
  ~15 lines; this is a map for a human, not an inventory.
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

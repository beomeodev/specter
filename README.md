<div align="center">
    <h1>👻 SPECTER</h1>
    <h3><em>Specification-Progressive Enforcement & Constitution-based Traceability, Evolutionary Review</em></h3>
    <p>
        <strong>English</strong> | <a href="./README.ko.md">한국어</a>
    </p>
</div>

<p align="center">
    <a href="./CHANGELOG.md"><img src="https://img.shields.io/badge/release-v2.3.1-2ea44f" alt="release"></a>
    <a href="https://github.com/github/spec-kit"><img src="https://img.shields.io/badge/built%20on-Spec--Kit%20v0.12.5-cc785c" alt="built on Spec-Kit"></a>
    <a href="#required-tools"><img src="https://img.shields.io/badge/Python-3.14%2B%20·%20uv-3776ab" alt="Python 3.14+ · uv"></a>
    <a href="https://claude.com/claude-code"><img src="https://img.shields.io/badge/Claude%20Code-workflow%20overlay-d97757" alt="Claude Code overlay"></a>
    <a href="#gates"><img src="https://img.shields.io/badge/gates-lint%20·%20type%20·%20test-5a0fc8" alt="gates"></a>
    <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License">
</p>

---

> [!IMPORTANT]
> **This is a personal template, not a general-purpose product.**
> This repository is public only to make maintenance convenient (for syncing and
> referencing across the author's own projects). It is a personal variant of
> [Spec-Kit](https://github.com/github/spec-kit), heavily reshaped around one
> person's workflow, tooling, and assumptions. It is **not** intended for others
> to adopt as-is — paths, agents (Codex/Antigravity), and gates are wired to the
> author's environment, and no support or stability is promised. Use it as a
> reference for ideas, not as a drop-in starter.

---

## What is SPECTER?

SPECTER is a Claude Code workflow overlay built on top of GitHub [Spec-Kit](https://github.com/github/spec-kit). While keeping Spec-Kit's engine intact, it places quality gates at points where AI-assisted development typically breaks down.

- **GEARS Requirements** — Translates ambiguous PRDs into verifiable requirement statements.
- **Feature Map Gates** — Enforces exactly one Feature owner for every PRD commitment.
- **Constitution** — Extracts project standards once, pins them in a single place, and re-injects them at every step.
- **TAG Traceability** — Enables back-traceability from requirements to code using a `@SPEC → @TEST → @CODE` anchor chain (one comment line per file).
- **Dual-Agent Cross-Verification** — Employs Codex and Antigravity as independent reviewers participating in every gate.
- **Graphify Code Graph** — A local tree-sitter code graph (no LLM, no API key) built by `/ms.init` and kept current by git hooks; agents answer structural questions with `graphify query/path/explain` instead of re-exploring the codebase.

It targets three core issues:

**AI forgets rules.** A prompt saying "keep files small" is often followed by a massive file a few steps later. Constitution and `AGENTS.md` repeatedly inject rules, and deterministic gates (pre-commit, hooks, CI) mechanically catch what prompts miss.

**Ambiguous requirements lead to unstable implementations.** Requesting "build a login feature" lacks authentication details, failure handling, and session policies. GEARS addresses this:

```text
When a user submits valid credentials, the auth service shall issue a session token.
[Error Handling] When credentials are invalid, the auth service shall return a generic authentication error.
```

**It's hard to trace why code exists.** The TAG anchor chain connects requirements to tests and code — one grep-able comment line per artifact:

```text
specs/001-auth/tasks.md    **TAG**: @SPEC:AUTH-001
tests/auth.test.ts         // @TEST:AUTH-001
src/auth/service.ts        // @CODE:AUTH-001
```

The current release is `v2.3.1` — see [CHANGELOG.md](./CHANGELOG.md) for changes.

---

## Quick Start

```bash
/ms.init
/ms.featuremap @docs/prd/PRD.md [@docs/prd/another.md]
/ms.codex-checklist @docs/prd/PRD.md [@docs/prd/another.md]
/ms.verify
/ms.constitution
/ms.checklist
/ms.agent-verify
/ms.specify   # Paste checked Feature section from docs/prd/feature-map.md
```

You don't need to run these commands one by one. The Pre-Feature cycle is handled by `/ms.pre-specter`, and the Per-Feature cycle is fully automated by `/ms.specter`.

---

## Workflow

```text
────────────────────────────────────────────────────────────────────
 📄  Setup
────────────────────────────────────────────────────────────────────
     0. /ms.init            Install Spec-Kit + Constitution + code graph
     1. /ms.prd             Co-author PRD — Discovery interview for unknowns (Out-of-cycle)
                            docs/prd/PRD.md (or multiple PRDs)
                            │
                            ▼
════════════════════════════════════════════════════════════════════
 🗺️  Pre-Feature Cycle    ·  Once  ·  Bulk run: /ms.pre-specter
════════════════════════════════════════════════════════════════════
     2. /ms.featuremap       Decompose PRD into Feature DAG
     3. /ms.codex-checklist  Codex independent checklist (Background)
     4. /ms.verify           PRD + Codex + Antigravity check → Global Gate
     5. /ms.constitution     Finalize project standards (Constitution §IX)
                            │
                            ▼   Repeat for each Feature in DAG order
════════════════════════════════════════════════════════════════════
 🛰️  Per-Feature Cycle    ·  N times  ·  Bulk run: /ms.specter
════════════════════════════════════════════════════════════════════
  ┌─▶  6. /ms.checklist      Verify current Feature (PRD alignment)
  │    7. /ms.agent-verify   Codex + Antigravity quick validation
  │    8. /ms.specify        Write specification (Input Feature section)
  │    9. /ms.clarify        🔴 Clarify requirements — Human response required
  │   10. /ms.plan           Implementation plan + Reality check
  │   11. /ms.tasks          Generate TAG-based tasks
  │   12. /ms.analyze        Match spec ↔ plan ↔ tasks consistency
  │   13. /ms.implement      TDD implementation + TAG injection
  │   14. /ms.review         Code review + Execution gates (lint/type/test/build)
  └──── Repeat from step 6 if features remain
                            │   All Features completed
                            ▼
────────────────────────────────────────────────────────────────────
 🚀  Publish / Release
────────────────────────────────────────────────────────────────────
    15. /ms.fin              Sync docs → Conditional CI → commit · push · PR
    16. /ms.merglease        Merge PR → tag → GitHub Release
```

`clarify` is the only manual step in the entire cycle. All other steps either proceed automatically or stop based on gate outcomes (`PASS`/`WARN`/`FAIL`).

**Using bare calls is recommended.** PRDs and the Feature Map are automatically discovered in their conventional paths (`docs/prd/*.md`, `docs/prd/feature-map.md`). Avoid attaching the entire PRD with `@` in conductor commands, as it re-injects the file into the context every time the conductor restarts (which can bloat token usage — e.g., 1.05M tokens in one project). Only use `@` for files outside conventional paths.

### Alternative Tracks

Tracks determined by the nature of changes outside the main cycle.

| Scenario | Track | Key Points |
| --- | --- | --- |
| No PRD or vague ideas | `/ms.prd` | Blind-spot pass → Viability gate → Interview to bridge gaps. No gates; output is a PRD consumed directly by the pipeline. |
| No new requirements (bug/copy/style fixes) | `/ms.fix` | Maintains TDD, TAG, and gates while skipping spec/clarify/plan/tasks ceremonies. |
| Experimental throwaway work | `spike` skill | Triggered via natural language ("let's experiment"), time-boxed, merge prohibited, output is a single findings note. |
| Incremental requirements on baseline | `/ms.expand` | Append '## PRD Amendment N' to the PRD → decompose only the diff. Existing features remain unchanged, no global re-audit, rejects freeform input. |
| Design changes discovered during build | Deviations log / `/ms.expand` | In-scope deviations append to `specs/<id>/implementation-notes.md` during `/ms.implement` (reported by `/ms.review`); a change that supersedes a requirement goes through `/ms.expand`. |
| All features green but product-level check needed | `/ms.audit` | 6 modules (exposure, cold-start, threat model, perf/a11y, gate value, blind spots). Advisory only — blocks nothing; findings route to `/ms.fix`, `/ms.expand`, or todo. |
| Global product reconstruction | `/ms.pre-specter` | Recreates the Feature Map and re-verifies from global gates. |

---

## Gates

Each step is validated by output artifacts and deterministic checkers, not just prompt instructions.

Every verification station follows a **three-layer contract** (2026-07-19, `specter-agent-protocols` §7): Layer 1 runs deterministic structural checks (`specter-gate.sh structural` — ownership rows, DAG cycles, placeholders, CI-green suffixes) before any agent is spent; Layer 2 runs Codex + Antigravity as independent fresh-context auditors who each write their own verdict; Layer 3 computes the station verdict mechanically (`specter-gate.sh aggregate` — station-fixed inputs, SHA-freshness validation, mechanical run-ledger emission). The host authors and assembles but never grades: it cannot downgrade an external verdict (disputes go to fresh scoped re-rounds), and the generative artifacts of `/ms.featuremap`/`/ms.checklist` are written by isolated fresh subagents so the author's session memory cannot leak into the audit.

| Gate | When | Verification Details |
| --- | --- | --- |
| Global Feature Map (`/ms.verify`) | Pre-Feature, Once | Structural L1 + independent Codex & Antigravity global audits (each writes its own SHA-bound verdict) + mechanical aggregation. Codex's PRD-only checklist stays the independent input baseline. |
| Per-Feature (`/ms.checklist` + `/ms.agent-verify`) | Every Feature start | Checks current Feature's commitment coverage, intrusion into other features, user-facing exposure, and unresolved placeholders. |
| Doc Consistency (`/ms.analyze`) | Just before implementation | Validates spec ↔ plan ↔ tasks drift, orphan tasks, and Constitution compliance. |
| Code (`/ms.review`) | Right after implementation | Runs lint/type/test/build + TAG integrity + Done Criteria Execution. Validates runnable criteria (e.g., verifying web UIs using Playwright rendering). |

Below the prompt-based gates lies a mechanical enforcement layer: direct `/speckit-specify` calls bypassing `/ms.specify` are rejected by a PreToolUse hook, and during `/ms.implement`/`/ms.review` a Stop hook blocks turn-end when code changed without fresh gate-execution evidence (max 3 consecutive blocks; fresh evidence with any verdict — even FAIL — allows the turn, because the gate forces gates to run, not to succeed). Feature Map and TAG chain integrity are enforced via pre-commit and CI (ruff, mypy, pytest, bandit) as backstops. If an agent fails due to environmental issues, gates are not silently bypassed; execution continues with remaining agents, marking the result as `WARN` and logging it as `UNAVAILABLE`.

---

## Core Commands

| Command | Role |
| --- | --- |
| `/ms.init` | Install Spec-Kit + Inject SPECTER overlays, hooks, backstops, and the Graphify code graph |
| `/ms.prd` | Co-author PRD via discovery interview (Out-of-cycle) |
| `/ms.pre-specter` | Bulk run the Pre-Feature cycle (featuremap → constitution) |
| `/ms.featuremap` | Decompose PRD into a Feature DAG and generate per-feature prompts |
| `/ms.codex-checklist` | Generate Codex PRD-only independent checklist (Background) |
| `/ms.verify` | Match PRD + checklists from both agents + Feature Map → Global Gate |
| `/ms.constitution` | Establish Constitution Section IX project baseline (Usually once) |
| `/ms.specter` | Bulk run the Per-Feature cycle (checklist → review), human input only at clarify |
| `/ms.checklist` / `/ms.agent-verify` | Verify current Feature's PRD coverage (Host + Codex/Antigravity) |
| `/ms.specify` / `/ms.clarify` / `/ms.plan` / `/ms.tasks` | GEARS spec → Clarification → Plan → TAG tasks |
| `/ms.analyze` | Validate document consistency + agent checks before build |
| `/ms.implement` | TDD implementation + TAG injection (`--to-end`, `--mode tdd\|refactor`, `--task TNNN`, `--pbt` property-based tests from GEARS) |
| `/ms.review` | Code review + adversarial agent review + execution gates |
| `/ms.fix` / `/ms.expand` / `/ms.audit` | Alternative tracks (See table above) |
| `/ms.fin` | Sync docs → Conditional CI → commit · push · PR |
| `/ms.merglease` | Merge PR → Automate semver → tag → GitHub Release |
| `/ms.up-docs` | Sync living docs |
| `/ms.sync` | Broadcast workflow files to registered project repos (with 3-way conflict protection) |

Agent validation commands share common flags like `--model`, `--effort low|medium|high`, `--background`, and `--skip-agents`. All flags are documented in their respective [command files](./.claude/commands/).

### Two Stages of Constitution

The default Constitution (test-first, simplicity, GEARS, TRUST, TAG) created by `/ms.init` is active even before `/ms.specify`. `/ms.constitution` does not create a new one from scratch; it extracts and establishes the **project-wide baseline (Section IX)** from the verified Feature Map. Thus, it is run once immediately after `/ms.verify`, not during the feature cycles.

```text
/ms.init             → Activate default Constitution
/ms.codex-checklist  → Run PRD-only independent checklist
/ms.verify           → Run global gate
/ms.constitution     → Establish Section IX baseline (Usually once)
```

---

## Installation

```bash
npx degit beomeodev/specter my-new-project
cd my-new-project
# Inside Claude Code:
/ms.init
```

`/ms.init` is pinned to a verified Spec-Kit release (`v0.12.5`). Because upstream is pre-1.0 and changes its integration surface frequently, pinning protects wrappers from unexpected breakage. To track the latest, run `SPEC_KIT_REF=main /ms.init` — though you may need to re-verify command delegation names as listed in the [Spec-Kit Compatibility](#spec-kit-compatibility) section below.

### Project Structure

```text
specter/
├── .claude/
│   ├── commands/           # Workflow entrypoints
│   ├── agents/             # Specialist subagents
│   ├── skills/             # Reusable checkers, rules, and rubrics
│   └── settings.json       # Permission baseline
├── .specify/               # Spec-Kit state (Constitution, scripts — created by /ms.init)
├── scripts/specter/        # Deterministic gate and sync scripts (Agent-neutral)
├── docs/
│   ├── prd/                # PRDs, feature-map, checklists, and verification reports
│   ├── review/             # Review output artifacts
│   └── templates/          # Constitution and spec templates, gate scripts
├── specs/NNN-{feature}/    # spec.md · plan.md · tasks.md
├── AGENTS.md               # Agent-neutral contract (CLAUDE.md is a symlink)
└── README.md
```

---

## Spec-Kit Compatibility

SPECTER is a compatibility layer that delegates work to upstream skills **by name** rather than re-implementing the engine. `/ms.*` acts as explicit workflow entrypoints and remains commands, while reusable verification logic is kept as skills. `/ms.init` injects the Feature Map gate into all candidate locations, whether they are in the command layout (`.claude/commands/speckit.*.md`) or the native-skill layout (`.claude/skills/speckit-*/SKILL.md`).

### Delegation Points (Spec-Kit Coupling Contract)

Upstream renaming will break only these delegations. Before bumping the pin (`SPEC_KIT_REF`), ensure these names remain correct.

| SPECTER Wrapper | Delegation Target (Pinned v0.12.5) |
| --- | --- |
| `/ms.specify` | `/speckit-specify` (+ `/ms.init` injects the gate) |
| `/ms.clarify` | `/speckit-clarify` |
| `/ms.plan` | `/speckit-plan` |
| `/ms.tasks` | `/speckit-tasks` |
| `/ms.analyze` | `/speckit-analyze` (foundation only) |
| `/ms.implement` | `/speckit-implement` |

> * `/ms.checklist` intentionally does NOT delegate to `/speckit-checklist` (runs independent verification against the PRD).*
> * v0.12.x also renders upstream skills outside this contract (`speckit-converge`, `speckit-taskstoissues`, `speckit-constitution`, `speckit-checklist`) — SPECTER does not wrap them; `/ms.constitution` and `/ms.checklist` are independent implementations, not wrappers of the same-named upstream skills.*
> * GEARS template injection uses the v0.12.x resolution stack: `/ms.init` installs the GEARS spec-template at `.specify/templates/overrides/` (priority 1 — no preset or extension can shadow it) plus the core path as a pre-0.12 fallback.*

### Identity Invariants (Non-negotiable)

While conforming names, paths, versions, and flags to upstream, SPECTER will never compromise on: the Feature Map gate, direct-call bypass block (dual guard via prompt marker and PreToolUse hook), GEARS reaching new specs, TAG traceability, Constitution Section IX, Codex independent checks, gate ownership (retained by SPECTER, not delegated to Spec-Kit CLI flags), and maintaining gate integrity during agent unavailability.

### Divorce Tripwires

We will fork the engine if any of the following cannot be resolved via thin compatibility shims (renaming, path adjustment, version/flag alignment):

| Tripwire | Impact |
| --- | --- |
| Spec-template resolution deviates from 'core' (=.specify/templates/spec-template.md) | GEARS fails to reach new specs |
| Patchable 'speckit-specify' file disappears (locked, signed, or generated dynamically) | Cannot inject gates → Bypass blocks collapse |
| Unable to block automatic '/speckit-specify' calls | Sequential gate enforcement breaks down |
| Upstream engine hard-conflicts with SPECTER injections (TAG/Constitution) | Composition/wrapping becomes impossible |
| Dependent scripts break repeatedly without a viable shim | Workflow steps become non-functional |

> Principle: Conform on names, paths, versions, and flags. Never bend on gates, GEARS, TAG, Constitution, and Codex.

---

## Roadmap: Multi-Agent & Public Distribution

While SPECTER is currently Claude Code-specific, we plan to transition it to a **workflow that runs identically on Codex CLI**. The direction aligns with Spec-Kit's unified architecture: keep `.claude/commands/` as the single source of truth, and let renderers generate agent-specific formats (e.g., `.agents/skills/` for Codex). Adding other agents like Gemini CLI later will then just be a matter of adding one unified definition.

- **Driver-Aware Cross-Verification**: The external reviewer at the verification station switches dynamically based on the driver (Claude driver → Codex + `agy` review; Codex driver → Claude + `agy` review). This avoids hardcoded drift by keeping a single dispatch table.
- **uv Package Distribution**: Aims for a simple setup like `uvx specter init --integration claude|codex`, similar to Spec-Kit.
- **Full English Translation + Language Selector**: Consolidates templates in English, allowing users to choose their reporting and interaction language at installation.
- **Pre-Distribution Cleanup**: Prioritizes removing personal account configurations and hardcoded local paths before open-sourcing.

The step-by-step execution plan follows: Cleanup → Renderer → Driver-aware protocol → Packaging. The gate invariants remain intact, although hook-based enforcement under Codex might fallback to pre-commit/CI backstops (the only structural gap).

---

## When to Use

**Suitable**: Projects with continuous AI-assisted feature development · Products requiring tight PRD-spec-impl-review traceability · MVPs shipping sequential features · Long-term codebases needing quick answers for "why does this code exist?".

**Unsuitable**: One-off scripts · Quick experiments around 100 LOC · Micro-projects where the maintenance cost of traceability outweighs the benefits.

---

## Required Tools

- `git`, `ripgrep` 13+, `uv`/`uvx`
- Graphify (`graphifyy`, version-pinned — `/ms.init` installs it via `uv tool install --python 3.12`; the graph lives in each project's gitignored `graphify-out/`)
- Claude Code
- Codex CLI (Authenticated) + Codex plugin for Claude Code (`openai/codex-plugin-cc`)
- Google Antigravity CLI `agy` (Authenticated) + Antigravity plugin (`sakibsadmanshajib/antigravity-plugin`)
- Project-specific testing, linting, and type-checking tools

Optional: GitHub CLI (PR/release automation in `/ms.fin` and `/ms.merglease`)

---

## Detailed Documentation

- [AGENTS.md](./AGENTS.md) — AI coding rules ([CLAUDE.md](./CLAUDE.md) is a symlink)
- [CHANGELOG.md](./CHANGELOG.md) — Release history
- [docs/SYSTEM_MAP.md](./docs/SYSTEM_MAP.md) — Curated prose snapshot (invariants, risks, verification); structural exploration goes through the Graphify code graph in consuming projects (`/ms.init` Step 2.9)
- [.claude/commands/](./.claude/commands/) · [.claude/agents/](./.claude/agents/) · [.claude/skills/](./.claude/skills/)

---

## Credits

[Spec-Kit](https://github.com/github/spec-kit) · [Claude Code](https://claude.com/claude-code) · [ripgrep](https://github.com/BurntSushi/ripgrep)

MIT License

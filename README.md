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
    <a href="#tool-requirements"><img src="https://img.shields.io/badge/Python-3.14%2B%20·%20uv-3776ab" alt="Python 3.14+ · uv"></a>
    <a href="https://claude.com/claude-code"><img src="https://img.shields.io/badge/Claude%20Code-workflow%20overlay-d97757" alt="Claude Code overlay"></a>
    <a href="#gates"><img src="https://img.shields.io/badge/gates-lint%20·%20type%20·%20test-5a0fc8" alt="gates"></a>
    <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License">
</p>

> [!NOTE]
> This README documents the current `master` branch, which may include
> unreleased workflow changes beyond the latest tagged release. For the exact
> behavior of `v2.3.1`, see the corresponding tag and [CHANGELOG](./CHANGELOG.md).

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

SPECTER is a requirements-governance and verification overlay for AI-assisted product development.

It preserves product intent as work moves from PRDs to Feature boundaries, GEARS specifications, implementation plans, tests, code, and runtime evidence. It uses GitHub [Spec-Kit](https://github.com/github/spec-kit) as its generation engine while retaining ownership of its gates, traceability rules, and independent verification protocol.

- **GEARS Requirements** — Translates ambiguous PRDs into verifiable requirement statements.
- **Feature Map Gates** — Enforces exactly one Feature owner for every PRD commitment.
- **Constitution** — Extracts project standards once, pins them in a single place, and re-injects them at every step.
- **TAG Navigation** — Provides a lightweight, grep-based index from requirement IDs to their primary test and implementation files through `@SPEC → @TEST → @CODE`. TAG wiring is mechanically checked, but TAG presence does not prove that a test semantically covers a requirement. Executable tests and review evidence remain authoritative.
- **Independent Semantic Verification** — Codex and Antigravity independently review artifacts at semantic verification stations. Deterministic scripts validate structure and mechanically aggregate their SHA-bound verdicts.
- **Graphify Exploration Accelerator** — Maintains a local tree-sitter graph that gives agents file-and-line pointers for structural questions. Graph results are navigation hints, not authoritative evidence; agents verify the referenced source files. Missing Graphify degrades to `rg`/`find` with a recorded warning and never blocks a Feature.

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

### Feature Boundaries

A SPECTER Feature is the smallest dependency-aware slice that can be specified, implemented, verified, reviewed, and merged independently.

A Feature may be architectural rather than independently user-shippable. End-to-end user value is guaranteed at the Phase boundary, whose final Feature owns the Phase E2E scenario.

Prefer vertical slices where practical; use dependency-aware architectural slices when foundations or cross-layer boundaries require sequencing.

### Authority Model

SPECTER does not treat every artifact as a competing source of truth. Each artifact owns a different kind of decision:

| Artifact | Authority |
| --- | --- |
| PRD | Product intent and durable commitments |
| Feature Map | Commitment ownership, Feature boundaries, and dependency order |
| `spec.md` | Executable behavioral contract for one Feature |
| `plan.md` | Verified implementation decisions and architecture |
| `tasks.md` | Execution breakdown and traceability assignments |
| Tests and runtime evidence | Observed implementation behavior |
| `implementation-notes.md` | In-scope deviations discovered during implementation |

A downstream artifact may refine an upstream artifact within its assigned authority, but it must not silently redefine product intent. Requirement changes return through `/ms.expand`.

### GEARS and Acceptance Scenarios

GEARS is used for executable behavioral requirements:

`[Where <static>] [While <runtime>] [When <trigger>] the <subject> shall <behavior>.`

Given-When-Then remains the acceptance-scenario format:

- `Where + While` maps to `Given`
- `When` maps to `When`
- `shall` maps to `Then`

SPECTER does not force GEARS onto schemas, scope declarations, preservation constraints, or implementation notes. Those may use plain but verifiable statements.

GEARS compliance is currently enforced through templates, workflow rules, structural checks, and semantic reviewers. It is not presented as a complete formal-language parser.

### Feature Audit Tiers

SPECTER deterministically varies audit intensity by Feature risk without
skipping the harness:

| Tier | Policy-controlled intensity |
| --- | --- |
| T1 — Routine | Narrow Feature/direct-seam scope, lowest approved reviewer effort, at most two automatic fresh rounds. |
| T2 — Standard | Current standard scope and effort, at most three automatic fresh rounds. This is the default and the legacy-Feature fallback. |
| T3 — High-Risk | Strongest effort, adjacent trust-boundary and targeted risk checks, plus explicit human acknowledgment for residual WARNs or a one-reviewer environmental degrade. |

Every tier retains L1 structural checks, two independent reviewers at existing
dual-agent stations, station-fixed L3 worst-result aggregation, executable
gates, Done Criteria Execution, hooks, CI, TAG wiring, migration analysis, and
high-stakes acknowledgments. Feature Map authors record evidence-bound
`### Audit signals`; they never assign a tier. A deterministic classifier
recomputes at Feature Map, spec, plan, pre-implementation, and actual-diff
boundaries, and the effective tier can only rise. Legacy Features without
signals resolve to T2; malformed new metadata fails safe.

The executable source of truth is
[`audit-tier-policy.json`](./docs/templates/audit-tier-policy.json); receipt,
freshness, and reviewer rules live in
[`specter-agent-protocols`](./.claude/skills/specter-agent-protocols/SKILL.md).
The global Feature Map gate is always full strength and is not tiered.

---

## Quick Start

```bash
/ms.init
/ms.pre-specter @docs/prd/PRD.md
/ms.specter 001
```

`/ms.pre-specter` prepares and verifies the product-wide Feature Map. `/ms.specter 001` runs Feature 001 from readiness checks through code review. `/ms.clarify` pauses the cycle when product intent requires a human decision.

For debugging or manual control, each underlying `/ms.*` step can also be run individually.

<details>
<summary>Expanded command sequence</summary>

```bash
/ms.init
/ms.featuremap @docs/prd/PRD.md
/ms.featuremap-checklist @docs/prd/PRD.md
/ms.pre-verify
/ms.constitution
/ms.checklist
/ms.verify
/ms.specify
/ms.clarify
/ms.plan
/ms.tasks
/ms.analyze
/ms.implement
/ms.review
```

</details>

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
     3. /ms.featuremap-checklist  PRD-only baseline checklist (isolated subagent)
     4. /ms.pre-verify           L1 structural + Codex & Antigravity dual audit → Global Gate
     5. /ms.constitution     Finalize project standards (Constitution §IX)
                            │
                            ▼   Repeat for each Feature in DAG order
════════════════════════════════════════════════════════════════════
 🛰️  Per-Feature Cycle    ·  N times  ·  Bulk run: /ms.specter
════════════════════════════════════════════════════════════════════
  ┌─▶  6. /ms.checklist      Verify current Feature (PRD alignment)
  │    7. /ms.verify         Tier-bound Codex + Antigravity verification
  │    8. /ms.specify        Write specification (Input Feature section)
  │    9. /ms.clarify        🔴 Always requires human input
  │   10. /ms.plan           Implementation plan + Reality check
  │   11. /ms.tasks          Generate TAG-based tasks
  │   12. /ms.analyze        Match spec ↔ plan ↔ tasks consistency
  │   13. /ms.implement      TDD implementation + TAG injection
  │   14. /ms.review         🟠 Conditional human acknowledgment for migrations + execution gates
  └──── Repeat from step 6 if features remain
                            │   All Features completed
                            ▼
────────────────────────────────────────────────────────────────────
 🚀  Publish / Release
────────────────────────────────────────────────────────────────────
    15. /ms.fin              🟠 Conditional acknowledgment for high-stakes diffs → commit · push · PR
    16. /ms.merglease        Merge PR → tag → GitHub Release
```

`/ms.clarify` is the only unconditional human stop in the normal per-Feature cycle. Additional human acknowledgment is required only for explicitly high-risk or irreversible operations, such as schema/data migrations, high-stakes publish diffs, destructive changes, or unresolved release risks.

**Using bare calls is recommended.** PRDs and the Feature Map are automatically discovered in their conventional paths (`docs/prd/*.md`, `docs/prd/feature-map.md`). Avoid attaching the entire PRD with `@` in conductor commands, as it re-injects the file into the context every time the conductor restarts (which can bloat token usage — e.g., 1.05M tokens in one project). Only use `@` for files outside conventional paths.

### Alternative Tracks

Tracks determined by the nature of changes outside the main cycle.

| Scenario | Track | Key Points |
| --- | --- | --- |
| No PRD or vague ideas | `/ms.prd` | Blind-spot pass → Viability gate → Interview to bridge gaps. No gates; output is a PRD consumed directly by the pipeline. |
| No new requirements (bug/copy/style fixes) | `/ms.fix` | Maintains TDD, TAG, and gates while skipping spec/clarify/plan/tasks ceremonies. |
| Incremental requirements on baseline or design changes discovered during build | `/ms.expand` | Append `## PRD Amendment N` to the PRD → decompose only the diff. Existing Features remain unchanged, no global re-audit, rejects freeform input. In-scope implementation deviations remain in `specs/<id>/implementation-notes.md`; a requirement change returns through `/ms.expand`. |
| All features green but product-level check needed | `/ms.audit` | 6 modules (exposure, cold-start, threat model, perf/a11y, gate value, blind spots). Advisory only — blocks nothing; findings route to `/ms.fix`, `/ms.expand`, or todo. |

---

## Gates

Each step is validated by output artifacts and deterministic checkers, not just prompt instructions.

There are three kinds of gate station:

| Station type | Role | Examples |
| --- | --- | --- |
| Authoring station | An isolated agent writes an artifact; its self-verdict is non-authoritative. | Feature Map, checklist |
| Verification station | L1 structural checks → L2 independent semantic audits → L3 mechanical aggregation. | pre-verify, verify, analyze, review |
| Executable backstop | Enforces actual repository state without model judgment. | hooks, pre-commit, CI, tests/build |

Every verification station follows a **three-layer contract** (2026-07-19, `specter-agent-protocols` §7): Layer 1 runs deterministic structural checks (`specter-gate.sh structural`); Layer 2 runs Codex + Antigravity as independent fresh-context auditors who each write their own verdict; Layer 3 computes the station verdict mechanically (`specter-gate.sh aggregate` — station-fixed inputs, SHA-freshness validation, mechanical run-ledger emission). The host may author or assemble artifacts, but it never grades an aggregated verification station. The authoritative outcome is the Layer-3 receipt. Generative artifacts from authoring stations are written by isolated fresh subagents so the author's session memory cannot leak into the audit.

| Gate | When | Verification Details |
| --- | --- | --- |
| Global Feature Map (`/ms.pre-verify`) | Pre-Feature, Once | Structural L1 + independent Codex & Antigravity global audits (each writes its own SHA-bound verdict) + mechanical aggregation. The PRD-only baseline checklist (featuremap-checklist-author subagent) stays the independent comparison input; vendor diversity lives in the L2 dual audit. |
| Per-Feature (`/ms.checklist` + `/ms.verify`) | Every Feature start | Checks current Feature's commitment coverage, intrusion into other features, user-facing exposure, and unresolved placeholders. |
| Doc Consistency (`/ms.analyze`) | Just before implementation | Validates spec ↔ plan ↔ tasks drift, orphan tasks, and Constitution compliance. |
| Code (`/ms.review`) | Right after implementation | Runs lint/type/test/build + TAG integrity + Done Criteria Execution. Validates runnable criteria (e.g., verifying web UIs using Playwright rendering). |

Below the prompt-based gates lies a mechanical enforcement layer: direct `/speckit-specify` calls bypassing `/ms.specify` are rejected by a PreToolUse hook, and during `/ms.implement`/`/ms.review` a Stop hook blocks turn-end when code changed without fresh gate-execution evidence (max 3 consecutive blocks; fresh evidence with any verdict — even FAIL — allows the turn, because the gate forces gates to run, not to succeed). Feature Map and TAG chain integrity are enforced via pre-commit and CI (ruff, mypy, pytest, bandit) as backstops. If one reviewer fails due to an environmental issue, the fixed two-report station records an explicit `WARN` placeholder and continues with the remaining independent reviewer; T3 requires human acknowledgment. With zero independent reviewers, the station stops.

---

## Core Commands

| Command | Role |
| --- | --- |
| `/ms.init` | Install Spec-Kit + Inject SPECTER overlays, hooks, backstops, audit-tier policy/classifier, and the Graphify code graph |
| `/ms.prd` | Co-author PRD via discovery interview (Out-of-cycle) |
| `/ms.pre-specter` | Bulk run the Pre-Feature cycle (featuremap → constitution) |
| `/ms.featuremap` | Decompose PRD into a Feature DAG and generate per-feature prompts |
| `/ms.featuremap-checklist` | Author PRD-only baseline checklist (featuremap-checklist-author subagent) |
| `/ms.pre-verify` | Match PRD + checklists from both agents + Feature Map → Global Gate |
| `/ms.constitution` | Establish Constitution Section IX project baseline (Usually once) |
| `/ms.specter` | Bulk run the Per-Feature cycle (checklist → review), with unconditional human input at clarify and conditional acknowledgment for high-risk operations |
| `/ms.checklist` / `/ms.verify` | Verify current Feature's PRD coverage (Host + Codex/Antigravity) |
| `/ms.specify` / `/ms.clarify` / `/ms.plan` / `/ms.tasks` | GEARS spec → Clarification → Plan → TAG tasks |
| `/ms.analyze` | Validate document consistency + agent checks before build |
| `/ms.implement` | TDD implementation + TAG injection (`--to-end`, `--mode tdd\|refactor`, `--task TNNN`, `--pbt` property-based tests from GEARS) |
| `/ms.review` | Code review + adversarial agent review + execution gates |
| `/ms.fix` / `/ms.expand` / `/ms.audit` | Alternative tracks (See table above) |
| `/ms.fin` | Sync docs → Conditional CI → commit · push · PR |
| `/ms.merglease` | Merge PR → Automate semver → tag → GitHub Release |
| `/ms.up-docs` | Sync living docs |
| `/ms.sync` | Broadcast workflow files to registered project repos (with 3-way conflict protection) |

Tiered verification commands take reviewer effort and scope only from the
validated receipt. Their only tier override is `--raise-audit-tier T2|T3`;
reviewer-skip, effort-lowering, and tier-lowering flags are rejected. Other
command-specific controls are documented in the
[command files](./.claude/commands/).

### Two Stages of Constitution

The default Constitution (test-first, simplicity, GEARS, TRUST, TAG) created by `/ms.init` is active even before `/ms.specify`. `/ms.constitution` does not create a new one from scratch; it extracts and establishes the **project-wide baseline (Section IX)** from the verified Feature Map. Thus, it is run once immediately after `/ms.pre-verify`, not during the feature cycles.

```text
/ms.init             → Activate default Constitution
/ms.featuremap-checklist  → Run PRD-only independent checklist
/ms.pre-verify           → Run global gate
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

While conforming names, paths, versions, and flags to upstream, SPECTER will never compromise on: the Feature Map gate, direct-call bypass block (dual guard via prompt marker and PreToolUse hook), GEARS reaching new specs, TAG traceability, Constitution Section IX, independent dual-agent verification (Codex & Antigravity), gate ownership (retained by SPECTER, not delegated to Spec-Kit CLI flags), and maintaining gate integrity during agent unavailability.

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

The current repository remains a personal, environment-specific template. The roadmap below describes a possible future distribution model, not the support or compatibility contract of the current release.

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

## Tool Requirements

### Hard runtime requirements

- Git
- ripgrep
- uv/uvx
- Claude Code
- Project-specific test/lint/type/build tooling

### Verification agents

- Codex CLI (authenticated) + Codex plugin for Claude Code
- Google Antigravity CLI `agy` (authenticated) + Antigravity plugin

One unavailable reviewer degrades the station to `WARN`. If no independent reviewer remains, the station stops rather than substituting a host-only verdict.

### Exploration accelerator

- Graphify (`graphifyy`, version-pinned; `/ms.init` installs it via `uv tool install --python 3.12`)

Its absence at runtime is non-blocking and falls back to `rg`/`find`.

Optional: GitHub CLI (PR/release automation in `/ms.fin` and `/ms.merglease`)

## Validation Status

The workflow has automated fixture and gate-contract tests, including the
deterministic audit-tier classifier and receipt invariants. The newest
three-layer station architecture, audit-tier orchestration, and Graphify
integration are still being validated through full end-to-end runs in real
consuming projects.

See [docs/SYSTEM_MAP.md](./docs/SYSTEM_MAP.md) for current verified invariants and known gaps.

---

## Detailed Documentation

- [AGENTS.md](./AGENTS.md) — AI coding rules ([CLAUDE.md](./CLAUDE.md) is a symlink)
- [CHANGELOG.md](./CHANGELOG.md) — Release history
- [docs/SYSTEM_MAP.md](./docs/SYSTEM_MAP.md) — Curated prose snapshot (invariants, risks, verification); structural exploration may use Graphify pointers in consuming projects, which must be verified against source files (`/ms.init` Step 2.9)
- [.claude/commands/](./.claude/commands/) · [.claude/agents/](./.claude/agents/) · [.claude/skills/](./.claude/skills/)

---

## Credits

[Spec-Kit](https://github.com/github/spec-kit) · [Claude Code](https://claude.com/claude-code) · [ripgrep](https://github.com/BurntSushi/ripgrep)

MIT License

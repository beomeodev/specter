---
generated_at: 2026-07-11T05:31:00Z
git_head: 2e6732a1c4238a0751a82b21357312af7acfdc4f
git_head_short: 2e6732a
git_branch: master
working_tree: dirty (uncommitted graphify-adoption patch — this refresh is part of it)
scope:
  - AGENTS.md
  - README.md
  - CHANGELOG.md
  - .claude/
  - docs/
  - scripts/specter/
  - tests/specter/
  - pyproject.toml
  - .mcp.json
  - .pre-commit-config.yaml
tools:
  - git
  - rg
  - find
  - uv run pytest --cov
graphify: not_installed
stale_when:
  - git_head differs from current HEAD
  - changed files overlap documented invariants or shared modules
  - command, agent, skill, template, or workflow files are modified
---

# System Map

## Snapshot Status
HEAD is `2e6732a` on `master`. The working tree carries the uncommitted
2026-07-11 graphify-adoption patch (AGENTS.md §9/§11, `/ms.init` Step 2.9,
`/ms.specter` Step 0.6, `codebase-snapshot` slim-down, this map). This map
follows the slimmed schema: structural inventory (file lists, per-file hot-path
notes) is intentionally absent — see `Refresh Procedure` and AGENTS.md §9 for
where structure is answered instead.

## System Purpose
SPECTER is a command-driven workflow wrapper over GitHub Spec-Kit for Claude
Code projects. This repository is the **template/tooling repo itself** — it
ships the `/ms.*` command definitions (25 files under `.claude/commands/`),
skills (21 dirs under `.claude/skills/`), agents (10 files under
`.claude/agents/`), Constitution/spec templates, and deterministic gate scripts
that a consuming project installs via `/ms.init` and receives updates to via
`/ms.sync`. There is no application runtime here; `backend/`/`frontend/` are
empty scaffolding.

## Primary Workflows
- `/ms.init` bootstraps the overlay into a consuming project: Spec-Kit install
  (pinned via `SPEC_KIT_REF`), Constitution/GEARS templates, Feature-Map gate
  injection, gate/hook scripts, pre-commit backstops (Step 2.8), and the
  Graphify code graph + rebuild hooks (Step 2.9, pinned via
  `GRAPHIFY_VERSION`).
- **Pre-Feature (one-time)**: `/ms.pre-specter` conducts `/ms.featuremap` →
  `/ms.codex-checklist` → `/ms.verify` → `/ms.constitution`. `/ms.prd` sits
  before it (co-authoring, no gates); `/ms.expand` is the incremental PRD
  Amendment track.
- **Per-Feature**: `/ms.specter` conducts `/ms.checklist` → `/ms.agent-verify`
  → `/ms.specify` → `/ms.clarify` (human stop) → `/ms.plan` → `/ms.tasks` →
  `/ms.analyze` → `/ms.implement` → `/ms.review`. Step 0 self-heals the gate
  checker copy and the Graphify graph (WARN-only) before the cycle starts.
- `/ms.fix` is the lightweight non-requirement track (TDD+TAG+gate, no spec
  ceremony); `/ms.audit` is advisory and gate-neutral. Post-implementation
  deviations live in `specs/<id>/implementation-notes.md` (Deviations log).
- `/ms.sync` broadcasts the file set in
  `scripts/specter/specter_sync_manifest.json` (commands, agents, skills,
  templates, the two backstop scripts, `AGENTS.md`, `CLAUDE.md`) to registered
  repos via 3-way merge.
- `/ms.fin` / `/ms.merglease` handle publish/release (delegated to
  Antigravity).
- Dual-agent mechanics (preflight, degrade, salvage, convergence, auditor
  bias-prevention) live once in the `specter-agent-protocols` skill.

## State And Data Flow
- Workflow state is file-based, produced in consuming projects:
  `docs/prd/feature-map.md` + `*.checklist.md` + `*.codex-verify.md` /
  `*.antigravity-verify.md`, `.specify/memory/constitution.md`, the TTL-bounded
  `.specify/.ms-gate-pass-<NNN>` token, and the `.specify/specter-run.jsonl`
  run-state ledger (bookkeeping only, never a gate source).
- `docs/prd/feature-map.progress.md` is the Progress Ledger, kept out of the
  Feature Map's SHA256 so bookkeeping never triggers false staleness.
- `graphify-out/` (consuming projects only) is regenerated state: gitignored,
  rebuilt by post-commit/post-checkout hooks, queried at need. Never committed,
  never pasted into this map.
- `CHANGELOG.md [Unreleased]` stages not-yet-tagged changes;
  `docs/dev_daily.md` / `docs/todo.md` are append-only log/scratchpad.

## Runtime Paths
Not applicable — this repository ships no deployed application or server; the
`/ms.*` commands run inside a Claude Code session.

## Shared Modules And Single Sources Of Truth
- `AGENTS.md` — always-on agent contract; §2 session read policy, §9
  exploration/graph/map division of labor, §10 layout invariants. `CLAUDE.md`
  is a symlink to it.
- `scripts/specter/specter_sync_manifest.json` — the one list of what
  `/ms.sync` broadcasts.
- `.claude/skills/specter-agent-protocols/SKILL.md` — dual-agent mechanics.
- `.claude/skills/codebase-snapshot/SKILL.md` — SYSTEM_MAP schema and the
  graph/map division of labor.
- `docs/templates/scripts/specter-gate.sh` — the one place gate
  PASS/WARN/FAIL/MISSING is computed mechanically.
- `scripts/specter/check_tag_chain.py` — TAG rules incl. the `FIX-*` /
  presentational carve-out (`FIX_PREFIX`, `PRESENTATIONAL_RE`).
- Version pins: `SPEC_KIT_REF` (Spec-Kit) and `GRAPHIFY_VERSION` (Graphify),
  both in `.claude/commands/ms.init.md`.

## Invariants
- Keep workflow changes surgical; never weaken a gate to fit upstream churn
  (README "정체성 불변식"; divorce tripwire documented there).
- `/ms.*` commands stay commands; `.claude/skills/` holds reusable
  capabilities, not new entrypoints.
- Dual verification (Codex + Antigravity) is never silently skipped — an
  unavailable agent forces an explicit `UNAVAILABLE` record and a `WARN`
  degrade (`specter-agent-protocols` §2).
- The Graphify graph is an exploration accelerator, never a correctness
  invariant: its absence or staleness may produce a WARN
  (`/ms.specter` Step 0.6), never a FAIL, and no blocking gate may depend on
  it. `graphify-out/` stays gitignored.
- The `.specify/.ms-gate-pass-<NNN>` token is single-invocation and
  TTL-bounded (~1h).
- `specter-gate.sh` must always emit its JSON contract, even on malformed
  input.
- Preserve TAG (`@SPEC → @TEST → @CODE`/`@DOC`) semantics; the only sanctioned
  exemption is the `/ms.fix` `FIX-*`/presentational carve-out — do not widen it
  without updating the tests.
- `/ms.specify` never accepts freeform feature input; direct
  `/speckit-specify` never bypasses the injected Feature-Map gate (marker
  `MS_FEATUREMAP_GATE_START`).

## Risk Areas
- Graphify adoption is design-verified only: installed-and-measured in zero
  consuming projects so far. Trial one real code repo, then measure read-path
  compliance via transcript mining (graph queries vs `rg`/`Read` fan-outs)
  before treating the token-saving claim as realized.
- `graphifyy` is a ~3-month-old upstream (v0.9.12 pinned): expect API churn;
  bump `GRAPHIFY_VERSION` deliberately and re-verify hooks + query output.
- `docs/improvements/*.md` are historical working records, not
  currently-authoritative plans.

## Verification Commands
```bash
git status --short
git rev-parse HEAD
uv run pytest --cov -q          # 53 tests, 90.47% coverage, 85% floor
bash -n docs/templates/scripts/specter-gate.sh docs/templates/scripts/speckit-specify-gate-hook.sh
rg -n "GRAPHIFY_VERSION" .claude/commands/ms.init.md   # exactly one pin definition
```

## Known Gaps
- No live consuming project in this repo to exercise `/ms.specter` (including
  the new Step 0.6 graph self-heal) end-to-end; verification is
  fixture/test-level and read-back-level.
- Graphify was exercised against a scratchpad clone of this repo (build 1.85s,
  257 nodes; incremental 1.6s; query ≈1.6k tokens), not yet against a real
  consuming project.

## Refresh Procedure
1. Read `AGENTS.md` (§9 for the graph/map division) and
   `.claude/skills/codebase-snapshot/SKILL.md`.
2. Capture git metadata (`git status --short`, `git rev-parse HEAD`,
   `git branch --show-current`).
3. Answer structural questions at ask-time: Graphify queries where a graph
   exists, otherwise `rg`/`find`. Do not add inventory sections back to this
   map.
4. Re-check every path named under `Shared Modules` still exists at the stated
   role.
5. Re-run `uv run pytest --cov -q` and update the figures quoted here.
6. Update sections with only verified facts; record unresolved items under
   `Known Gaps` rather than guessing.

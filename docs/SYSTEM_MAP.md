---
git_head: pending-commit (refreshed from current worktree; base 222f846c8d9fd8a31ed10c09fac7ff550e16376f)
refreshed: 2026-07-31
stale_when: workflow commands, gate scripts, sync manifest, or Spec-Kit integration change
---

# SPECTER System Map

SPECTER is a command-driven governance wrapper over GitHub Spec-Kit. It keeps
product intent traceable while allowing each downstream artifact to become more
concrete.

## Main flows

```text
/ms.prd
   ↓
/ms.pre-specter
  featuremap → featuremap-checklist → pre-verify → constitution
   ↓
/ms.specter NNN
  checklist → verify → specify → clarify → plan → tasks
  → analyze → implement → review
   ↓
/ms.fin → /ms.merglease
```

`/ms.expand` consumes a PRD Amendment, refreshes the mutable Feature Map, runs
the full global audit, and hands affected work to `/ms.specter`. `/ms.audit`
is advisory and never participates in a conductor.

## Authority invariant

PRD/Amendments own product intent and boundaries. Feature Map owns mutable
decomposition, ownership, order, and DAG. spec owns observable detail; plan owns
technical design; tasks own execution partition; code/tests own observed
reality. Only boundary changes route to the one mandatory human stop,
`/ms.clarify`.

## Verification invariant

`docs/templates/scripts/specter-gate.sh` is a state-free mechanical checker.

- `version`: capability probe (`lean-verification-v1`)
- `hash <station> <scope>`: current input bundle hash
- `reduce <station> <scope>`: validates two fixed reports and returns worst-of
- `[NNN]`: global and optional per-Feature structural gate

It writes no receipts, ledgers, rounds, profiles, signals, or approval events.
Semantic judgment comes from fresh independent Codex and Antigravity reports.
The shared contract is
`.claude/skills/specter-agent-protocols/SKILL.md`.

## Enforcement seams

- `/ms.init` overlays GEARS and Constitution templates after pinned Spec-Kit
  installation.
- The `MS_FEATUREMAP_GATE_START` injection and PreToolUse hook prevent direct
  `/speckit-specify` bypass.
- The Stop hook requires fresh executable evidence after implementation/review
  code changes; it accepts honest FAIL evidence and has a bounded block count.
- pre-commit/CI retain Feature Map hash coherence, TAG integrity, and repository
  checks.
- `/ms.sync` distributes manifest-listed workflow files with per-target
  three-way merge safety.

## Final review ownership

Implementation runs task-level RED/GREEN checks. Review runs full
lint/type/test/build once, real-entrypoint Done Criteria, applicable E2E, dual
code review, and universal changed-file safety checks for migrations,
destructive operations, auth, secrets, public contracts, and gate/hook changes.

## Key paths

| Path | Purpose |
| --- | --- |
| `.claude/commands/ms.*.md` | workflow entrypoints |
| `.claude/skills/` | reusable protocols and rubrics |
| `docs/templates/` | synchronized project overlays |
| `docs/design/refinement-first.md` | canonical workflow philosophy |
| `scripts/specter/specter_sync.py` | broadcast engine |
| `scripts/specter/check_feature_map_gate.py` | staged Feature Map hash backstop |
| `tests/specter/` | gate, hook, sync, and publish regression tests |

## Verification commands

```bash
bash -n docs/templates/scripts/specter-gate.sh
pytest -q tests/specter
python scripts/specter/specter_sync.py --help
```

# Weekly Dependency & Security Triage (scheduled routine)

A 10-minute recurring routine that turns dependency rot and vulnerability exposure
into scheduled triage instead of mid-Feature emergencies. No new skill — the content
is standard tooling; the value is the cadence.

## Setup (once per project)

Use the Claude Code `schedule` plugin (or plain cron) to run weekly, e.g. Monday 09:00:

> "이 프로젝트에서 의존성/보안 트리아지 루틴 돌려줘 — docs/ops/weekly-triage.md 절차대로"

## The routine (what the scheduled session does)

1. **Audit per ecosystem** (only the ones present):
   ```bash
   [ -f pyproject.toml ] && (uv pip list --outdated 2>/dev/null | head -20; pip-audit 2>/dev/null || true)
   [ -f package.json ]  && (npm outdated || true; npm audit --omit=dev || true)
   command -v trivy >/dev/null && trivy fs --scanners vuln --severity HIGH,CRITICAL -q . || true
   ```
2. **Triage** into three buckets:
   - **Now** — HIGH/CRITICAL vulns in production deps, or a dep the code actively
     exercises: route to `/ms.fix` immediately (one fix branch per concern).
   - **Batch** — routine patch/minor updates: collect into one `/ms.fix` chore
     ("weekly dep bump"), run the local-ci gate, ship.
   - **Defer** — major-version bumps with breaking changes: note in `docs/todo.md`
     with the changelog link; majors are planned work, not triage work.
3. **Report** (Korean, ≤10 lines): what's in each bucket + what was shipped. Silence
   is a valid report ("전부 최신, 취약점 0").

## Rules

- Never bump a major version inside the triage routine.
- Every shipped bump goes through the normal `/ms.fix` gate (local-ci) — triage
  changes cadence, not discipline.
- If the same package lands in **Now** two weeks running, that's a smell the project
  pins or vendors something it shouldn't — surface it.

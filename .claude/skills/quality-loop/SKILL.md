---
name: quality-loop
description: Periodic test-suite and CI health audit — measures suite speed, hunts dead/duplicate tests, hook and cache health, and CI billable-minute waste, then routes fixes to /ms.fix. Verdict-first discipline (suites under 30s get a health-only pass, never speed optimization). Use when weekly token budget has slack, when agent loop turnaround feels slow, when CI minutes ran out, or on a monthly cadence per project. Report-only: it never edits code. Grows a cross-project pattern library seeded from the 2026-07-21 three-project audits.
---

# quality-loop — test-suite & CI health audit

Agents become safer to run long and autonomously when tests are both **broad**
(coverage → bolder changes) and **fast** (speed → faster loops). Determinism
accumulates as linters/tests/hooks pile up, but so does waste: dead tests,
duplicate coverage, per-test rebootstrapping, sealed caches, CI double-runs.
This skill is the periodic sweep that finds that waste — and the pattern
library that makes each sweep smarter than the last.

Provenance: three full audits on 2026-07-21 (large ~4,400-test suite, small
410-test suite, medium 765-test suite — reports in the SPECTER repo at
`docs/test-speed-audit-{slm,cln,sab}.md`). Every pattern below traces to a
real finding; entries are stated at failure-class level so they generalize.

## Hard rules

1. **Report-only.** The audit changes no code, no config, no tests. Findings
   route to `/ms.fix` (corrections) or the project's todo. Exception: none.
2. **Verdict before optimization.** Measure first; the small-suite verdict of
   the seed audits was "do nothing" and that was correct. Recommending speed
   machinery for a fast suite is a finding *against* the audit, not for it.
3. **Evidence per claim**: file:line, the command run, and measured time. An
   unmeasured "this looks slow" never enters the report.
4. **Never edit this skill in a consuming project.** It arrives via `/ms.sync`;
   target-side edits cause permanent sync conflicts. New patterns go in the
   report's "pattern candidates" section and are upstreamed to the SPECTER repo.

## Phase 0 — scale verdict (decides everything downstream)

Measure total suite wall time (cold and warm) before anything else, then pick
the lane:

| Suite wall time | Lane |
|---|---|
| < 30s | **Health-only**: items 2, 3, 4, 9 (+ silent-skip check). Speed items are skipped and the report says why. Selective execution, xdist, cache tuning are explicitly *anti-recommended* at this scale. |
| 30s – 5min | Full audit; speed items ranked by measured cost. |
| > 5min, or cannot complete locally | Full audit; completion blockers (OOM, network downloads, hangs) are P0 before any speed work — a suite that cannot finish locally means "all GREEN" has no deterministic verification path. |

Cold = caches cleared (`.pytest_cache`, `__pycache__`, tool caches); warm =
immediate re-run. Record both — the *gap* tells you whether caches do anything.

## Audit items (the 9-point sweep)

Run as a report-only pass; write the report to
`docs/test-speed-audit-<slug>.md` (slug = project shorthand) with a TL;DR
verdict table on top:

1. **Total runtime, cold vs warm** — plus the top-10 slowest tests/setups
   (`--durations` or equivalent).
2. **Dead tests** — tests whose target code was deleted/changed so they can
   never pass or never fire (see patterns 1, 9). Distinguish: confirmed-dead
   (delete), contract-stale (rewrite), coverage-gap-in-disguise (do NOT delete
   — flag for rewrite).
3. **Duplicate coverage** — pairs where one test's assertions are a strict
   superset of another's on the same code path and inputs. Verify with
   coverage measurement before calling it duplicate; intended two-layer
   coverage (unit + e2e adding distinct assertions) is not duplication.
4. **Pre-commit/pre-push hook reality** — what is *configured* vs what is
   *installed and actually runs* (patterns 8, 10). Also: does any hook run a
   CI-grade full suite on every commit (too heavy), or nothing at all (no
   local backstop)?
5. **Change-scoped execution** — does a one-line fix run the full suite? Is
   selective execution possible but sealed (pattern 2)? At <30s scale, absence
   of selective execution is correct, not a gap.
6. **Parallelism** — over-parallelism causing contention/flakiness, or (more
   common) zero parallelism on a many-core box. Before recommending xdist-type
   tools, list the concrete blockers (shared lock paths, global mutable
   caches, per-worker import cost, process-spawning tests).
7. **Repeated bootstrapping** — per-test DB migrations, app rebuilds, expensive
   function-scope fixtures (patterns 4, 5, 12). Look for the in-repo best
   practice first: the seed audits found the fix already existing in the same
   repo every time (a `:memory:` conftest, a module-scope fixture).
8. **Cache health** — for each cache dir: does it exist, is it hit, does a hit
   change wall time? A cache can be present-but-useless (pattern 11) or
   present-but-invalidated (pattern 10). Include broken external caches
   (partial model downloads re-fetched every run).
9. **CI workflow cost** — jobs per run, per-job durations, trigger conditions.
   Billable minutes = **sum over parallel jobs with per-job ceiling to the
   minute** — a 20-min wall run with 9 jobs can bill 30+ min. Check: PR
   double-runs (pattern 6), docs-only full runs (pattern 7), missing
   concurrency cancellation, missing dependency/type-checker caches, and
   whether the SPECTER standard CI block (`MS_CI_STANDARD_BLOCK_START`, from
   `docs/templates/ci-standard-block.yml`, planted by `/ms.init` Step 2.10) is
   present and current.

Close the report with: prioritized actions (P0/P1/P2 with expected savings),
explicit "do NOT do" anti-recommendations, and a **pattern candidates** section
for anything not in the library below.

## Pattern library

Detection hints assume pytest/vitest ecosystems; adapt per stack. Fix
directions are starting points, not prescriptions.

| # | Pattern | Symptom / detection | Fix direction |
|---|---|---|---|
| 1 | **RED-scaffolding survivors** | TDD leaves RED stubs; implementation lands elsewhere; stubs stay permanently failing or skipped. Grep test bodies for unconditional fail/raise with "RED"/"scaffold" notes; cross-check whether real coverage exists elsewhere. | Delete after confirming the real tests are GREEN; `/ms.review` Step 6.5 B2 now checks this per Feature at review time. |
| 2 | **Coverage forced in runner defaults** | `--cov` + `--cov-fail-under` in `addopts` → any partial run "fails" on coverage %, sealing selective runs and last-failed reruns (empty `lastfailed` is the tell). | Move coverage flags to the CI invocation only; local default runs bare. |
| 3 | **Real model/network escaping stubs** | A marker or stub fixture exists but a directory/test sits outside its scope: OOM from real model loads, live HTTP in tests, partial download caches re-fetched every run. Check marker filters actually applied (`-m "not network"` present anywhere?). | Promote stubs to top-level conftest (autouse) so no directory escapes; make network markers opt-in by default. |
| 4 | **Function-scope expensive fixtures** | `--durations` dominated by setup; expensive pipeline fixtures rebuilt per test while a module/session-scope precedent exists in the same repo. | Widen scope where tests are read-only on the fixture; keep function scope only where mutation demands it. |
| 5 | **Per-test DB/app rebootstrap** | Full migration set re-applied per test (measure per-call cost); app factory + lifespan re-running migrations on an already-migrated DB. | Session-scope template DB + per-test file copy; skip redundant migration re-checks in test lifespan. |
| 6 | **CI double-run** | `push: ['**']` + `pull_request` → same commit runs twice on every PR-branch push (pairs of runs seconds apart). | Standard CI block: push limited to master/main, PR event owns feature branches. |
| 7 | **Docs-only commits run full CI** | No `paths-ignore`; SPECTER workflows commit docs constantly, so a large share of runs verify prose. | Standard CI block `paths-ignore` (with the required-checks caveat documented in the template). |
| 8 | **Config-without-installed-hook** | `.pre-commit-config.yaml` present, `.git/hooks/pre-commit` absent → all local backstops silently dead. Found in 2 of 3 seed audits. | `pre-commit install`; `/ms.init` 2.8 guard + `/ms.review` B2 WARN now watch this. |
| 9 | **Silent-skip masquerading as pass** | A guard/fallback (e.g. "no git repo → skip tests") prints success with zero tests executed. Run the gate in a crippled sandbox copy and see if it still says pass. | Make skips loud and distinct from pass; zero-tests-executed must never report ✅. |
| 10 | **Dual-toolchain cache thrash** | Same tool installed twice (project venv + hook mirror) at different versions sharing/invalidating a cache → periodic full cold rebuilds (e.g. type-checker 45s "randomly"). | Pin both to one version, or point hooks at the project toolchain (`language: system`). |
| 11 | **Present-but-useless cache** | Cache dir exists; warm run isn't faster. Cost lives where the cache can't reach (environment/jsdom setup, collection-time imports). | Attack the dominant cost (lazy heavy imports, environment reuse, `isolate` off after safety check) — not the cache. |
| 12 | **Copy-pasted bootstrap helpers** | Same fixture/generator/client-factory pasted in 2-3 conftests or helper files; drift risk plus repeated runtime cost. | Promote to the shared conftest/helper the repo already has a precedent for. |
| 13 | **Daemon/process leak from tests** | Tests spawn agents/daemons (gpg-agent, servers) without teardown; they accumulate across runs and eat the memory budget. | Kill in fixture teardown; assert no leftover processes in a session-end check. |
| 14 | **Billable ≠ wall clock** | Cost estimates using run wall time undercount: billing sums parallel jobs and ceils each job to the minute. Many sub-minute jobs are the expensive shape. | Estimate from per-job durations; merge trivially short jobs; move heavy jobs to master-only triggers. |

## Growing the library

After each audit: new recurring waste-classes (found in ≥2 projects, or
clearly structural) get a row in this table **in the SPECTER repo** — via the
normal `/ms.fix` track there — then `/ms.sync` distributes it. One-off,
project-specific findings stay in that project's report/todo. Keep entries
stack-agnostic and class-level; the incident is provenance, not the entry.

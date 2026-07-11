---
description: "Product-level completeness audit — finds what per-Feature gates structurally can't: unexposed features, cold-start failures, security posture, gate drift. Advisory; findings route to /ms.fix, /ms.expand, or todo."
argument-hint: "[--modules exposure,coldstart,threat,perf,gates] [--adversarial]"
---

# /ms.audit - Product-Level Completeness Audit

Per-Feature gates prove each slice against its own spec. They structurally cannot see the
product as a whole — a backend capability no UI ever exposes, a daemon that dies on a clean
machine, a threat surface that grew across ten Features, a gate that hasn't caught anything
in twenty runs. Historically these were found only by the user's ad-hoc audit instinct; this
command makes that instinct periodic and systematic.

**This is an advisory command, not a gate.** It blocks nothing. Its output is a findings
report whose items route into the existing tracks — defects to `/ms.fix`, new requirements
to a PRD Amendment (`/ms.expand`), the rest to `docs/todo.md`. It is not part of any
conductor and never will be.

## When to run

- After a Phase's last Feature ships (the natural checkpoint — the Phase E2E scenario just
  passed, now ask what the *product* looks like).
- On a cadence (e.g. monthly).
- On instinct — "뭔가 빈 구멍이 있을 것 같은데" is a valid trigger; this command is that
  instinct, systematized.

## Evidence rule (applies to every module)

**No claims without evidence.** Every finding must cite the artifact that proves it — a file,
a command output, a commitment-index row, a ledger entry. A hunch without a probe is not a
finding; run the probe or drop it. Reports that pad severity with vibes are worse than
silence because they train the reader to skim.

## Execution Steps

### Step 0: Scope

Parse `--modules` (default: every module applicable to this project — skip `perf` when there
is no web UI, skip `gates` when there is no `.specify/specter-run.jsonl`, skip `exposure`
when there is no Commitment Index). Read `docs/prd/feature-map.md`'s Commitment Index and
`feature-map.progress.md` if present. Non-SPECTER projects can still run
`coldstart`/`threat`/`perf`.

### Module A: Exposure Audit — "구현됐지만 닿을 수 없는 것"

Walk every PRD Commitment Index row whose Feature is shipped/specified and answer: **can the
user actually reach this?**

1. For each user-facing commitment: find the surface that exposes it (route, screen, CLI
   verb, menu entry). Trace it from the entry point, not from the implementation — a wired
   backend with no frontend caller, an endpoint no screen calls, a CLI flag no help text
   mentions are all findings.
2. For each non-user-facing commitment (NFR, integration, migration): find the evidence it
   is *active* in the shipped configuration (not just merged — enabled, scheduled, wired).
3. Record per row: `reachable | implemented-but-unexposed | not-found`, with the evidence
   path.

### Module B: Cold-Start E2E — "새 기계에서 이 제품은 살아나는가"

Per-Feature runtime checks (`/ms.review` Step 6.6) run in a warm dev environment. This
module asks the question that environment can never answer: from nothing, does it boot?

1. Simulate the coldest start feasible in this environment: fresh clone to a temp dir,
   dependency install per the README's own instructions (the README is under test here too),
   configuration from documented steps only — no knowledge that isn't written down.
2. Boot the real entrypoint and drive the product's **core loop** (the one journey the
   product exists for) end to end, using the `webapp-testing` skill for web UIs.
3. Every undocumented step you were forced to improvise is a finding (packaging/docs class).
   A daemon that starts and immediately exits is a P0 regardless of how green the gates are.

### Module C: Threat Model — "누가 무엇을 노리고, 뚫리면 무엇을 잃는가"

Repo-grounded, not generic:

1. **Stake questions to the human first** (the only part that cannot be delegated —
   Korean, one at a time, with recommended framings): what data here would actually hurt to
   lose/leak? what loss is acceptable? who plausibly attacks this (opportunist scanner vs
   targeted)?
2. Derive **trust boundaries from actual config** (proxy config, tunnel setup, auth
   middleware, CORS, exposed ports — cite files): every edge gets protocol/auth/validation
   noted. The `Runtime Paths` section of `docs/SYSTEM_MAP.md` is the starting map if present.
3. Enumerate **abuse paths** against the stakes from (1), score likelihood × impact, and
   check each against an existing defense — including standing conveniences (debug bypasses,
   OTP/auth shortcuts, `--admin` habits) which are findings unless consciously re-accepted
   by the user *in this audit*.
4. Existing per-Feature security scans (trust-validation) already cover code-level OWASP;
   do not repeat them — this module owns the product-level surface only.

### Module D: Perf/A11y Smoke (web UI only, optional tooling degrades gracefully)

1. **Perf**: curl-loop the 2-3 hottest endpoints (from Module A's reachable list) for
   p50/p95 against a stated budget (default: p95 < 1s for interactive endpoints unless the
   PRD says otherwise — the budget used must be printed with the result).
2. **A11y**: if Lighthouse/axe tooling is available, run it on the main screens; otherwise
   check the `design-baseline` WCAG floors (contrast pairs, target sizes, body size) in
   the shipped CSS and skip the rest with an explicit "skipped: no tooling" line.

### Module E: Gate Value Review — "게이트들은 최근에 실제로 뭘 잡았나"

The workflow itself is a product; audit it with the same evidence rule:

1. From `.specify/specter-run.jsonl`, the review reports in `docs/review/`, and the
   checklists: for the last N Feature runs, which gates produced FAIL/WARN findings, and
   which produced none, ever?
2. A gate with zero catches across many runs is a **sunset candidate — report only**. This
   module NEVER weakens, skips, or edits a gate; changes go through the normal SPECTER-repo
   process with the human deciding (identity invariants apply — an audit that auto-tunes
   gates would be the fox auditing the henhouse).
3. Also flag the inverse: recurring human overrides or bypasses of the same gate (that's a
   design defect signal, per the SHA-spoof lesson).

### Module F: Blind-Spot Ledger

Maintain `docs/audit/blind-spots.md` — the explicit list of what no human or audit has
looked at:

1. Load the previous ledger; anything this audit covered moves to a dated "looked" log.
2. Add newly created surfaces (new Features' UI, new integrations, new config) that no
   module examined this time.
3. The ledger's open items are next audit's priority queue. An empty ledger is a finding
   about the ledger, not an achievement — repopulate it honestly.

### Final Step: Findings Report + Routing

Write `docs/audit/AUDIT-<YYYY-MM-DD>.md` and present the Korean summary:

```text
🔍 /ms.audit — <date>

| P | Finding | Evidence | Route |
|---|---------|----------|-------|
P0  제품이 약속을 어기고 있거나 보안 구멍이 열려 있음  → /ms.fix 즉시
P1  도달 불가/콜드스타트 실패 등 사용자 가치 미달       → /ms.fix 또는 PRD Amendment
P2  마찰/부채 — 계획적으로 처리                        → docs/todo.md
P3  새 요구사항으로 판명된 것                          → ## PRD Amendment N → /ms.expand
게이트 리뷰: <일몰 후보/우회 반복 — 보고만, 변경은 사람 결정>
블라인드스팟: <이번에 본 것 / 여전히 안 본 것>
```

Route each finding explicitly — an audit whose findings die in the report is theater. If
`--adversarial` was passed, run one Codex adversarial pass over the findings list (challenge
severity and evidence; external-agent protocol and degrade rules as in `/ms.review`) before
presenting. (`--agents` is accepted as a legacy alias.)

## What This Command Is Not

- Not a gate: nothing blocks on its results, and it is in no conductor.
- Not a re-run of per-Feature checks: it owns only the product-level questions those checks
  structurally cannot ask.
- Not a gate-tuning tool: Module E reports evidence; humans change gates.

## Next Command

Route the findings: `/ms.fix` (P0/P1 defects), `## PRD Amendment N` + `/ms.expand`
(new requirements), `docs/todo.md` (P2). Then ship the fixes through the normal tracks —
the audit's value is measured by what leaves the report.

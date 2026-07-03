# SPECTER Workflow Audit & Improvement Plan

**Date**: 2026-07-03
**Basis**: Full command-file audit (22 `/ms.*` commands) + transcript analysis of all Claude Code
sessions across 5 projects (atlas, cueline, sanjunipero, specter, suseonglm; ~132 sessions,
~62M output tokens, ~12B cache-read tokens, 60+ shipped Features, 300+ external agent runs).
**Status**: All work items below were approved by the user on 2026-07-03.

## How To Use This Document (implementing model, read first)

- Each Work Item (WI) is self-contained: Evidence → Change Spec → Target Files → Acceptance.
- Implement in the order listed unless a WI names a prerequisite. WI-1 is a prerequisite for WI-2.
- These are edits to workflow command/markdown files, not product code. Keep changes surgical:
  touch only the sections named in each WI. Do not reformat or "improve" adjacent content.
- SPECTER identity is non-negotiable (see AGENTS.md §10): never weaken the Feature-Map /
  freeform-refusal / direct-call-bypass gates, GEARS, TAG chains, Constitution §IX, or dual-agent
  verification. Every WI below preserves gate semantics; if an edit would weaken a gate, stop.
- Out of scope by explicit user decision: permission/git-allow design, reducing the number of
  commands. Do not touch these.

---

## Part A — Audit Summary (evidence base)

### A.1 What works (do not regress)

- **Gates catch real defects.** suseonglm Feature 063: host checklist said WARN, Codex escalated
  to FAIL (unachievable PRD done-criterion), Antigravity independently FAILed → PRD fixed before
  spec. cueline F009: Codex FAIL "rate/cost commitment has no test/done-criterion". cueline F012:
  both agents independently found the same 2 critical production-path defects. atlas F003 analyze:
  Antigravity FAILed with a real finding (egress rules split across Feature boundaries) distinct
  from Codex's finding. suseonglm review: Codex caught a unit-tested function never wired into
  production.
- **The `/ms.specter` conductor halved wall-clock per Feature** (sanjunipero: manual-chain era
  2.3–5.1 h/Feature → conductor era 0.9–2.1 h).
- User discipline is high: `/clear` per Feature, near-zero step skipping in conductor era,
  clarify answered via options.

### A.2 Findings (ranked)

| # | Finding | Evidence |
|---|---|---|
| F1 | **All gates are document gates; nothing executes the product.** | atlas: 14 Features all-green, yet `atlas serve` exited immediately on connect, packaging broken, channel routing dead — found only by a manual audit. sanjunipero: backend-implemented features shipped with no frontend exposure (5 gaps, 5 h fix session); login broken twice post-deploy. User-driven `/goal` audits and real-device tests were the de-facto quality gate. |
| F2 | **Context replay dominates token cost.** | ~12B cache-read tokens total; per-turn context 400–800k late in Feature sessions (peak 807k). Worst amplifier: CI polling — one suseonglm session had 12 `/ms.merglease` wakeups replaying ~400k each (345M cache-read in one session). |
| F3 | **`@PRD` attachment ritual.** | atlas: full PRD (54–69 KB) injected 60 times via `/ms.specter @PRD @feature-map NNN` ≈ 1.05M raw tokens. Feature 015/016 ran fine without attachments. |
| F4 | **Unbounded re-review rounds + external-agent ops churn.** | atlas F001: 10 Codex review rounds; 47+ explicit re-rounds project-wide. Antigravity ops failures: headless OAuth wall, lost background jobs, write-permission resets, 50-min first-run setup, model-ID opacity. Codex read-only sandbox forced host transcription of reports 5×. |
| F5 | **Structural re-reading.** | "Read these files in full" at every step: constitution ~6×/session, AGENTS.md ~5×, tasks.md `cat` 140× in one project, PRD 11× across one feature's sessions. Related error class: ~180 "File has not been read yet" Edit failures (53% of all tool errors in one project) — the AGENTS.md "don't re-read" rule fights the harness's Edit-requires-Read rule. |
| F6 | **Feature-Map SHA staleness gate misfires on bookkeeping.** | Progress-Ledger status updates change the SHA → all gates go stale. 12 friction events in cueline; one full re-audit; user once hand-spoofed the SHA to bypass `/ms.verify` ("특별하게 이번만 허용"). A gate the admin bypasses by hand is a design defect. |
| F7 | **Zero-value confirmation stops.** | merglease version/merge confirmations: 36 AskUserQuestion stops, 0 rejections; the prompt itself hit JSON validation errors 4×. |
| F8 | **No incremental PRD path.** | Adding requirements after setup forces a full `/ms.pre-specter` re-run (regenerates the whole map, re-audits all PRDs, may overwrite existing decomposition). Root cause is F6's whole-file SHA binding: any map edit invalidates every gate. |

---

## Part B — Decisions (agreed 2026-07-03)

1. All WIs below are approved; implement all.
2. **Antigravity stays in `/ms.analyze`** (earlier idea to drop it is withdrawn — atlas F003 shows
   it contributes distinct findings). Priority is hardening the agy integration (WI-8), with an
   explicit degrade-to-Codex-only rule when agy is unavailable.
3. **merglease is fully automatic**: semver computed from conventional commits, no version or
   merge-strategy questions. Explicit `[version]` arg or `--confirm` flag are the only overrides.
4. **GitHub CI failures caused by billing/quota/infra are ignored (loudly) at merge time**; any
   real test/lint/build failure still blocks. Local CI is the authoritative gate.
5. **`/ms.expand` consumes amendments appended to the existing `docs/prd/PRD.md`** (heading
   convention + git-diff append-only guard), not a separate new-PRD file.
6. **Harness items approved (WI-11…WI-15)**: mechanical verifications (verdict lines, SHA
   equality, file existence) move to scripts/hooks; judgment checks (PRD fidelity, severity)
   stay with the model; the clarify stop stays human. Explicitly rejected harness ideas (quality
   loss): hard-blocking `/ms.fin` on review-state, hook-enforced re-review caps, regex-GEARS
   blocking lint, blocking manual edits under `docs/prd/**`, mechanizing clarify.
7. **WI-8 revised** (user correction): external agents keep writing their own report files;
   marker-echo salvage is a failure-path fallback only — the host never takes over agent work on
   the happy path.

---

## Part C — Work Items

### WI-1: Split the Progress Ledger out of the SHA-hashed Feature Map *(prerequisite for WI-2)*

**Evidence**: F6.

**Change spec**:
1. `/ms.featuremap` emits the Progress Ledger to a new file `docs/prd/feature-map.progress.md`
   instead of an inline section. `feature-map.md` keeps a one-line pointer
   (`> Progress Ledger: docs/prd/feature-map.progress.md`).
2. All SHA256 computations and comparisons (`/ms.verify` Step 5 template, `/ms.checklist` Step 1.6
   and audit template, `/ms.specify` Step 0.2 checks 6/11, `/ms.constitution` Step 1.5) continue to
   hash `docs/prd/feature-map.md` — which now contains only normative content (header, commitment
   index, Feature sections, DAG, global rules). Status bookkeeping no longer changes the SHA.
3. `/ms.specify` Step 0.5 (Progress Ledger recompute) and `/ms.merglease` ("mark ✅ shipped")
   write to `feature-map.progress.md`.
4. **Migration**: commands that read the ledger must handle both layouts. If an inline
   `## Progress Ledger` section still exists in `feature-map.md`, `/ms.featuremap` (on re-run) and
   `/ms.expand` (WI-2) move it out as part of their normal map write; do NOT move it from a gate
   command (that would change the SHA outside an audited write).

**Target files**: `.claude/commands/ms.featuremap.md`, `ms.verify.md`, `ms.checklist.md`,
`ms.specify.md`, `ms.constitution.md`, `ms.merglease.md`, README (게이트 구조 section).

**Acceptance**: Updating a Status cell in `feature-map.progress.md` does not invalidate any
recorded SHA. A normative edit to `feature-map.md` still invalidates gates exactly as before.

---

### WI-2: New command `/ms.expand` — incremental PRD track *(depends on WI-1)*

**Evidence**: F8. Fills the gap between `/ms.fix` (no new requirement) and full `/ms.pre-specter`
(whole-product recomposition).

**Change spec** — create `.claude/commands/ms.expand.md`:

- **Input convention**: new requirements are appended to the existing PRD file(s) under a heading
  `## PRD Amendment N — YYYY-MM-DD` (top-level `##`, at end of file). Usage:
  `/ms.expand` (auto-detect changed PRDs) or `/ms.expand @docs/prd/PRD.md`.
- **Preconditions**: established baseline required — `feature-map.checklist.md` Result PASS/WARN
  and Constitution §IX established. Otherwise stop and point to `/ms.pre-specter`.
- **Step 0 — Delta detection + append-only guard**:
  - `/ms.verify` and `/ms.expand` record `**Git Ref**: <commit sha>` in
    `feature-map.checklist.md` at audit time (add this field to the `/ms.verify` template too).
  - `/ms.expand` computes `git diff <last recorded Git Ref> -- docs/prd/*.md` (excluding
    feature-map artifacts). If the diff touches anything **other than** appended
    `## PRD Amendment` sections (i.e., edits to existing PRD text), STOP: this changes existing
    commitments and is not an expansion — direct the user to `/ms.pre-specter` (or a targeted
    re-verify of the affected commitments). Never proceed silently.
  - Extract ONLY the amendment section text. The full PRD is not re-read.
- **Step 1 — Append-only map extension**: decompose the amendment into new commitment index rows
  (new C-refs), new `## Feature NNN:` sections (next free numbers), and DAG extensions. Existing
  Feature sections and existing index rows are immutable here; if the amendment requires changing
  an existing Feature's ownership or scope, STOP and escalate (same message as Step 0).
  Same structural bars as `/ms.featuremap` (single owner, no cycle, out-of-scope destinations,
  E2E scenario if a new Phase is created).
- **Step 2 — Codex delta checklist (background)**: same contract as `/ms.codex-checklist` but the
  prompt embeds ONLY the amendment text inline (no file-tree reading of the full PRD set); output
  `docs/prd/codex/checklist-delta-N.md`, IDs continue the C-numbering.
- **Step 3 — Delta verify (foreground)**: host + Antigravity audit scope limited to:
  (a) every amendment commitment has exactly one owning (new) Feature; (b) new Features do not
  overlap existing owners; (c) extended DAG has no cycle; (d) deferred items have destinations.
  Append a `## Delta Reconciliation N — YYYY-MM-DD` section to `feature-map.checklist.md`, update
  `**Result**`, recompute `Feature Map SHA256` and `Git Ref`. Antigravity unavailable → apply the
  WI-8 degrade rule (Codex-only + WARN).
- **Step 4 — Constitution diff check**: only scan the amendment for durable-rule material
  conflicting with or extending §IX. Usually a no-op; on conflict, stop and ask (same rules as
  `/ms.constitution` Step 4). Do not rewrite §IX for feature-local content.
- **Step 5 — Report (Korean)** and hand off: `/ms.specter <new NNN>`.

Also update: `/ms.pre-specter` "What This Command Is Not" + README workflow section + `/ms.fix`
Step 0 discriminator to route "new requirement, existing product" → `/ms.expand` (three tracks:
fix / expand / pre-specter).

**Target files**: new `.claude/commands/ms.expand.md`; edits to `ms.verify.md` (Git Ref field),
`ms.pre-specter.md`, `ms.fix.md`, README, AGENTS.md §10 (mention the new command's place).

**Acceptance**: Appending an amendment + running `/ms.expand` yields a PASS/WARN gate and a
runnable `/ms.specter <new NNN>` without re-auditing pre-existing Features; editing an existing
PRD paragraph causes `/ms.expand` to refuse.

---

### WI-3: Runtime gate — Done Criteria Execution in `/ms.review` + user-surface check in `/ms.checklist`

**Evidence**: F1 (the single biggest PRD-fidelity hole).

**Change spec**:
1. `/ms.review` — new **Step 6.7: Done Criteria Execution** (after executable gates, before
   dual-agent review so agents can see the results):
   - Load the Feature's `### Done criteria` (from the Feature Map section) and the spec's
     acceptance scenarios. Classify each as RUNNABLE (CLI command, server start + health/endpoint
     check, script, reproducible user flow) or MANUAL (requires human eyes/devices).
   - Execute every RUNNABLE criterion for real: start the actual entrypoint (daemon, server,
     CLI), drive the affected flow, observe behavior. Bounded: kill long-running processes after
     verification; this is a smoke of the product path, not a load test.
   - If this Feature is a Phase's last Feature, execute the Phase E2E scenario.
   - Record a table `| Criterion | Class | Result (PASS/FAIL/MANUAL) | Evidence |` in the review
     report. Any RUNNABLE FAIL ⇒ review result **NOT READY** (same severity as a failing test).
   - MANUAL items are emitted in the Korean report as a "📋 수동 확인 필요" checklist (device,
     steps, expected result) — this formalizes the user's real-device testing loop.
2. `/ms.checklist` — add one check to Step 4.1 (PRD Fidelity): *user-facing exposure* — every
   owned commitment that implies a user-visible surface (UI, CLI, API, notification) must have a
   concrete in-scope deliverable exposing it OR an explicit out-of-scope row naming the owning
   Feature. Missing both ⇒ FAIL. (Directly targets the sanjunipero backend-only gap class.)
3. Optional knob (document, not default): `--runtime-agent=agy` delegates the Done Criteria
   Execution to Antigravity so an independent party (not the implementer) drives the product.
   Default stays host-run; enable only once WI-8 hardening has proven agy stable.

**Target files**: `.claude/commands/ms.review.md`, `ms.checklist.md`, README (게이트 구조).

**Acceptance**: A feature whose daemon exits on start cannot reach READY (atlas A1 class is
caught). Review reports enumerate manual-verification items.

---

### WI-4: `/ms.merglease` — semver automation, CI-failure classification, no polling in main context

**Evidence**: F2 (CI-polling replay), F7, user decisions 3–4; atlas billing-blocked CI merged with
`--admin`.

**Change spec** (rewrite the Antigravity delegation prompt in `ms.merglease.md`):
1. **Semver (automatic, no questions)**: from conventional commits since the last tag —
   any `BREAKING CHANGE` footer or `type!:` ⇒ MAJOR; else any `feat` ⇒ MINOR; else ⇒ PATCH.
   Apply the same mapping pre-1.0. The computed bump and its rationale (commit list) go into the
   release notes. An explicit `[version]` argument overrides; `--confirm` restores interactive
   confirmation. Remove the merge-strategy question: default merge commit.
2. **CI-failure classification (pre-merge)**: run `gh pr checks`. If any check failed, inspect
   failure logs/conclusions:
   - If ALL failures match billing/infra patterns (case-insensitive: `billing`,
     `spending limit`, `usage limit`, `quota`, conclusion `startup_failure`, or the job never
     started) ⇒ proceed with the merge, print a loud warning, and record
     "GitHub CI skipped: billing/infra" in the release notes.
   - If ANY failure is a real test/lint/typecheck/build failure ⇒ STOP and report; do not merge.
   - Document the principle: local CI (`/ms.review`/`/ms.fin` gates) is authoritative;
     GitHub CI is advisory.
3. **No CI polling in the main session**: the Antigravity delegation waits for CI itself (it
   already runs the whole pipeline); the host session must not loop `gh pr checks`/`gh run watch`
   or schedule wakeups for it. If delegation is unavailable (agy down), run the merge steps
   directly but use a single background Bash task for any unavoidable wait, and report once on
   completion.

**Target files**: `.claude/commands/ms.merglease.md`, README (플래그 설명).

**Acceptance**: A standard release requires zero user interactions; a billing-red PR merges with a
loud recorded warning; a test-red PR refuses to merge; the main transcript contains no repeated
CI-poll turns.

---

### WI-5: Re-review convergence caps in `/ms.review` and `/ms.analyze`

**Evidence**: F4 (10-round Codex loop, 47+ re-rounds).

**Change spec** — add a "Convergence Policy" subsection to both commands' dual-agent steps:
- Round 1: full dual-agent run. Round 2 (only if round 1 had FAIL/blocking findings): re-run
  scoped to the previously failing findings only (state them in the prompt; do not re-review the
  whole artifact).
- Round 3 is the last automatic round and only for findings that were FAIL in round 2.
- After round 3, or when only WARN-level findings remain after round 2: stop re-running agents.
  Record residual WARNs in the report / `.specify/review-state.txt` and hand the decision to the
  user. More rounds only on explicit user instruction.
- Each re-round's prompt embeds the specific finding + the fix diff, not "re-review everything".

**Target files**: `.claude/commands/ms.review.md`, `ms.analyze.md`.

**Acceptance**: No transcript can show >3 agent rounds per station without an explicit user
request in between.

---

### WI-6: Session read-dedup policy + Edit-exception; conductor context manifest

**Evidence**: F5 (~180 Edit-before-Read failures; constitution read ~6×/session).

**Change spec**:
1. Add one standard paragraph to every command's artifact-loading step (`Step 0` /
   "Load Project Context" / "Read these files in full" blocks) in all `/ms.*` files:
   > **Session read policy**: if a required file was already read in this session and has not
   > changed since (no edit by you, no user notice), reuse it — do not re-read. Exception: the
   > harness requires a fresh `Read` of a file before `Edit`/`Write`; always satisfy that
   > requirement even if the content is already in context.
2. Amend AGENTS.md §2 ("Do not re-read a file you already read this session") with the same
   Edit/Write exception sentence, so the two rules stop fighting (this is the root cause of the
   error class).
3. `/ms.specter` and `/ms.pre-specter`: after Step 0 loads shared artifacts, the conductor states
   a short manifest ("already loaded this session: constitution, feature-map §Feature NNN, PRD
   refs …") and instructs subsequent steps to apply the session read policy against it.

**Target files**: all 22 `.claude/commands/ms.*.md` (mechanical, one paragraph each — most
commands only need it where they mandate reads), `AGENTS.md` (and templates that generate
AGENTS.md if present under `docs/templates/`).

**Acceptance**: The policy paragraph exists in every command that mandates reads; AGENTS.md
contains the Edit exception.

---

### WI-7: Narrow `/ms.checklist`'s PRD read scope

**Evidence**: F5 (PRD read 11× across one feature's sessions; checklist re-reads every source PRD
in full although global coverage is `/ms.verify`'s job).

**Change spec**: in `ms.checklist.md` Step 0 and Step 3, replace "read every source PRD in full"
with: read the PRD **sections listed under the Feature's `### PRD references`** (plus immediate
surrounding context needed to interpret them) and the Feature's owned commitment rows. Full-PRD
reading only as fallback when a reference cannot be resolved. Add a note: global PRD coverage is
already audited by `/ms.verify`; this gate audits the selected Feature's fidelity to its
referenced sections.

**Target files**: `.claude/commands/ms.checklist.md`.

**Acceptance**: Checklist instructions no longer mandate whole-PRD reads on the happy path; the
FAIL conditions are unchanged.

---

### WI-8: External-agent hardening (Antigravity + Codex invocation protocol)

**Evidence**: F4; atlas F003 OAuth wall → gate downgraded ad hoc; 5× Codex read-only-sandbox
report transcription; `/antigravity:review` Skill-invocation trap retried identically in two
sessions; memory note: agy write flag resets on plugin update.

**Design principle (user decision 2026-07-03)**: external agents keep doing their own work —
including writing their own report files. The host must NOT take over agent responsibilities on
the happy path (that would spend Claude output tokens re-emitting report content). Host
intervention is a salvage fallback only.

**Change spec**:
1. **Preflight (once per session)**: the first command in a session that needs an external agent
   (`agent-verify`, `analyze`, `review`, `verify`) checks availability once: binary present,
   auth OK, and **write capability** (deterministic config checks: Codex sandbox mode is
   `workspace-write` in its config, agy write flag is set — cheap greps, not a live probe run).
   Result is remembered for the session.
2. **Explicit degrade rule** (replaces today's ad-hoc judgment): if Antigravity is unavailable
   after one retry, run the station **Codex-only** and force the station result to at most WARN,
   recording `Antigravity: UNAVAILABLE (<reason>)` in the artifact. Never silently PASS a
   dual-agent station single-agent; never block the whole cycle on agy environment issues either.
   Same rule mirrored for Codex-unavailable (Antigravity-only + WARN).
3. **Report-write protocol (primary path unchanged, fallback added)**: agents still write their
   own report files. Each prompt ADDITIONALLY requires the agent to echo the finished report
   between `===REPORT BEGIN===` / `===REPORT END===` markers in its final message (agents emit a
   final message anyway; marginal cost ≈ 0). After the run, a deterministic bash check validates
   the report file: exists, non-empty, contains `**Result**:`. If the file is missing or partial
   after one retry, the host **salvages** it by writing the file from the markers — instead of
   today's hard stop or freehand transcription. Salvage cost (~one small Write) only occurs on
   the failure path, where it replaces a full external re-run or a human intervention.
4. **Fix the `/antigravity:review` trap**: `ms.review.md` Step 6.6.B invokes
   `/antigravity:rescue` directly (delete the `/antigravity:review` primary + fallback note).
5. Foreground-only for gates stays as is; keep `--fresh`.
6. **Root-cause fixes**: document (and where possible script) the agy write-flag re-apply after
   plugin updates, so preflight failures are fixable in one step.
7. Optional (document as a knob, not a default): `--model` may select a stronger Gemini tier for
   `analyze`/`review` when quota allows; `gemini-3.5-flash` remains the default.
8. **Codify the identity-vs-availability resolution** in README's "SPECTER 정체성 불변식" section
   (one added line): dual-agent verification being non-negotiable means it may never be
   *silently* skipped or weakened — an environment-forced, explicitly recorded degrade
   (single-agent + WARN, per rule 2 above) preserves the invariant. This prevents future
   sessions from re-litigating the apparent conflict between the invariant and the degrade rule.

**Target files**: `.claude/commands/ms.agent-verify.md`, `ms.analyze.md`, `ms.review.md`,
`ms.verify.md`, `ms.codex-checklist.md`; `README.md` (정체성 불변식 section, item 8); note in
`docs/SYSTEM_MAP.md` or memory about the plugin-update flag reset re-apply step.

**Acceptance**: Happy path spends zero extra host tokens (agents write their own files); a
missing/partial report file after retry is recovered from markers instead of stopping; agy
absence produces a recorded WARN degrade instead of an improvised decision;
`/antigravity:review` is unreferenced.

---

### WI-9: Discourage `@PRD` attachment on conductor invocations

**Evidence**: F3 (~1.05M tokens of redundant PRD payload in one project).

**Change spec**: in `ms.specter.md` and `ms.pre-specter.md` Usage sections and `argument-hint`:
recommend the bare form (`/ms.specter 006`); state that `@`-attachments are only for
non-conventional paths, and that attaching the full PRD injects it into context on every
invocation and restart while the Feature Map + PRD-references mechanism already scopes reads.
Mirror the same guidance in README (워크플로우 section examples).

**Target files**: `.claude/commands/ms.specter.md`, `ms.pre-specter.md`, `README.md`.

**Acceptance**: Recommended invocations in docs/commands show the bare form first with an explicit
token-cost note on attachments.

---

### WI-10 (optional, last): Slim `ms.review.md`

**Evidence**: 825 lines, roughly half aspirational pseudo-bash that is not reliably executed but
is loaded into context on every review.

**Change spec**: keep the behavior contract (steps, gates, result model, prompts, convergence
policy from WI-5, runtime gate from WI-3); compress illustrative bash to short imperative
descriptions where the script is not actually meant to run verbatim. Target ≤ ~450 lines without
removing any gate or check.

**Target files**: `.claude/commands/ms.review.md`.

**Acceptance**: All steps/gates/flags still documented; file materially shorter; no gate removed.

---

### WI-11: Deterministic gate checker script — mechanical gates become mechanical

**Evidence**: gate checks (Result lines, SHA equality, file existence, Section IX established)
are pure facts, yet the model re-derives them at 3+ points per cycle (`/ms.specter` Step 0.2,
`/ms.checklist` Step 1, `/ms.specify` Step 0.2 with 15 items) — token cost plus drift risk.
Precedent: the deterministic TAG-chain pre-commit backstop (commit cd9e2e7).

**Change spec**:
1. New script `.specify/scripts/bash/specter-gate.sh [NNN]`:
   - Always checks: `docs/prd/feature-map.checklist.md` exists, contains `**Mode**: global`,
     `**Result**: PASS|WARN` (and not FAIL), and its `Feature Map SHA256` equals the current
     `sha256sum docs/prd/feature-map.md`; `.specify/memory/constitution.md` Section IX is
     established (present and not the placeholder text).
   - With `NNN`: additionally checks `docs/prd/checklists/feature-NNN.checklist.md` (exists,
     `Mode: per-feature`, same Feature, Result, SHA match) and both
     `feature-NNN.codex-verify.md` / `feature-NNN.antigravity-verify.md` (exist, Result
     PASS|WARN).
   - Output: one JSON object — per-check status, `overall: PASS|WARN|FAIL|MISSING`, and a
     `reasons[]` array.
2. `/ms.specify` Step 0.2, `/ms.checklist` Step 1, `/ms.specter` Step 0.2, and
   `/ms.constitution` Step 1 replace their manual read-and-compare instructions with one script
   invocation. Keep the existing Korean refusal messages, keyed to the JSON failure fields.
3. Scope boundary: the script owns only verdict/SHA/existence facts. Content judgment (PRD
   fidelity, boundary discipline, severity) stays with the model — do not move it into the script.
4. Ship the script in this repo and have `/ms.init` install it into target projects next to the
   other `.specify/scripts/bash/` scripts.

**Target files**: new script; `.claude/commands/ms.specify.md`, `ms.checklist.md`,
`ms.specter.md`, `ms.constitution.md`, `ms.init.md`.

**Acceptance**: no command instructs the model to manually compare SHA256 values or grep Result
lines for a gate decision; a single script call produces the same refusals as before.

---

### WI-12: Run-state ledger `.specify/specter-run.jsonl` — deterministic resume

**Evidence**: conductor interrupts (session limits) forced full "find where we stopped"
re-derivation 3× in atlas, each replaying a large context.

**Change spec**:
1. Every pre-Feature and per-Feature cycle step appends one JSON line after reading its own
   verdict: `{ts, cycle: "pre"|"feature", feature, step, verdict, artifacts: [paths]}`.
   Append-only (`>>`), written via bash by the step command.
2. `/ms.specter` / `/ms.pre-specter` Step 0: read the ledger; if the requested feature has a
   partial run, resume deterministically from the first step lacking a PASS/WARN entry (announce
   the resume point) instead of re-deriving state from artifacts and context.
3. The ledger is bookkeeping, not a gate: gates still come from the audit artifacts (WI-11).
   A missing/corrupt ledger degrades to today's behavior, never blocks.

**Target files**: all cycle-step command files (one bash append line each), `ms.specter.md`,
`ms.pre-specter.md`.

**Acceptance**: killing a conductor mid-cycle and re-invoking `/ms.specter <NNN>` resumes at the
correct step without artifact re-derivation.

---

### WI-13: PreToolUse hook — direct `/speckit-specify` bypass becomes mechanically impossible

**Evidence**: the direct-call bypass guard is a prompt marker (`MS_FEATUREMAP_GATE_START`)
injected into upstream files by `/ms.init` — it needs re-patching on every upstream reinstall and
only guides the model, it cannot stop it.

**Change spec**:
1. `/ms.specify`: after Step 0.2 gates pass (WI-11 script), write a token file
   `.specify/.ms-gate-pass-<NNN>`; delete it after `/speckit-specify` completes.
2. PreToolUse hook (settings.json) matching the Skill tool: if the requested skill is
   `speckit-specify` and no `.specify/.ms-gate-pass-*` token exists → deny with:
   "Direct /speckit-specify bypasses SPECTER gates. Run /ms.specify." Hook script lives in the
   repo; `/ms.init` installs the hook config + script into target projects.
3. Keep the existing prompt-marker injection as defense in depth. Note in README (Spec Kit
   호환성): the hook is upstream-independent, so the bypass guard now survives upstream layout
   changes unpatched.

**Target files**: `.claude/settings.json` (hooks), new hook script, `ms.specify.md`,
`ms.init.md`, README.

**Acceptance**: invoking `/speckit-specify` directly (no prior `/ms.specify` gate pass) is
blocked by the hook, not merely discouraged by prompt text.

---

### WI-14: Pre-commit extension — feature-map / gate coherence

**Evidence**: F6-adjacent — the model could commit a normatively-changed `feature-map.md` with a
stale gate; today only prompt discipline prevents it.

**Change spec**:
1. Extend the deterministic TAG-chain pre-commit backstop (cd9e2e7): when staged changes touch
   `docs/prd/feature-map.md`, recompute SHA256 of the **staged** map and compare with the
   `**Feature Map SHA256**:` value in the staged (else HEAD) `feature-map.checklist.md`.
   Mismatch → block the commit: "Feature Map changed without a matching gate. Run /ms.verify or
   /ms.expand first."
2. Progress bookkeeping is unaffected: after WI-1 the ledger lives in
   `feature-map.progress.md`, which this check ignores.
3. Deliberate admin bypass stays possible (`git commit --no-verify`) — the hook constrains the
   agent, not the human. Document this in the hook's block message.

**Target files**: the pre-commit backstop script (locate the cd9e2e7 script in this repo),
`ms.init.md` if it installs the hook into target projects.

**Acceptance**: committing a normative map edit with a stale checklist SHA is blocked;
committing a progress-file update passes.

---

### WI-15: SessionStart status injection *(depends on WI-11, WI-12)*

**Evidence**: every session begins by re-deriving "where am I" (feature, gate states) from
artifacts.

**Change spec**: a SessionStart hook script runs `specter-gate.sh`, reads the last
`specter-run.jsonl` entries and `feature-map.progress.md`, and emits a compact status (max ~5
lines, e.g. "Feature 012 in progress, stopped after /ms.plan; global gate PASS; next eligible:
013") as additional context. Cap the output so the injection itself never bloats context; if the
project has no SPECTER artifacts, emit nothing.

**Target files**: `.claude/settings.json` (SessionStart hook), new script, `ms.init.md`.

**Acceptance**: a fresh session in an in-flight project starts with the one-line state instead
of artifact spelunking.

---

## Part D — Explicitly Not Doing

- Permission / git-allow design changes (intentional, user decision).
- Reducing the number of commands or converting commands to skills.
- Removing Antigravity from `/ms.analyze` (withdrawn — see Part B, decision 2).
- Blanket-ignoring GitHub CI: only billing/infra-classified failures are ignored (WI-4).

## Part E-2 — Execution Verification Results (2026-07-03, post-implementation)

All 15 WIs were implemented (commits `e08d1b3..f765f81`) and independently verified against the
acceptance criteria above — by reading actual diffs and, for every script, by **executing it
against fixtures** (not by trusting commit messages). Verdict: **13 PASS, 2 PARTIAL.**

| WI | Verdict | Note |
|---|---|---|
| 1, 2, 3, 4, 5, 6, 7, 9, 12, 15 | PASS | No gaps found against spec |
| 8 | PASS | Corrected design faithfully kept: agents write their own report files (primary path); marker-salvage is failure-path only. `/antigravity:review` fully unreferenced. Minor: item 6 not done (see F-3). |
| 13 | PASS | Hook verified with 7 fixture stdin cases (deny/allow/no-op/fail-open all correct). Residual risks documented (see F-4). |
| 14 | PASS | Pre-commit script verified with 9 fixture git repos, including proof it hashes the STAGED map (`git show :path`), not the worktree. |
| 10 | PARTIAL | 936 → 611 lines (target was ≤~450). Verified NO gate/step/flag lost — content-wise complete, only the numeric target missed. Accepted as-is; no action. |
| 11 | PARTIAL | **Blocking bug — see F-1.** Everything else correct: script logic, all four command integrations, ms.init install step. |

### Follow-Up Work Items (for the next implementation session)

#### F-1 (BLOCKING) — FIXED 2026-07-03: `specter-gate.sh` crash on missing fields

**Bug (reproduced by execution)**: under `set -euo pipefail`, `extract_field()` pipes
`grep -m1 ... | sed ...`. When a checklist file EXISTS but lacks a required line
(`**Result**:`, `**Feature Map SHA256**:`, `**Feature**:`), grep exits 1, pipefail propagates,
and the command substitution (`global_result=$(extract_field ...)`, script line ~80) aborts the
whole script — **exit 1 with NO JSON output**. This violates the script's own contract ("prints
one JSON object... overall PASS|WARN|FAIL|MISSING") on exactly the malformed-artifact case the
script exists to catch; the calling command gets nothing to build its Korean refusal from.

**Fix**: make `extract_field()` tolerate no-match — e.g. append `|| true` inside the function (or
`grep ... || printf ''`), and treat an empty extraction as a FAIL check with a `reasons[]` entry
like `"feature-map.checklist.md exists but has no **Result**: line"`. Apply to every
`extract_field` call site (global Result, global SHA, per-feature Result/SHA/Feature, both
verify-file Results).

**Target**: `docs/templates/scripts/specter-gate.sh` (source of truth) — and note that
`/ms.init` copies it, so downstream projects initialized before the fix carry the buggy copy.

**Acceptance**: with a checklist file present but missing `**Result**:`, the script exits
successfully and prints a JSON object with `overall: "FAIL"` (or `MISSING`) and a human-readable
reason; `bash -n` clean; re-run the three reproduction cases from the verification (field-less
global checklist, field-less per-feature checklist, missing SHA line).

**Resolution**: `extract_field()` now appends `|| true` to the grep/sed pipeline, so a missing
field yields an empty string instead of aborting the script under `set -euo pipefail`. Existing
downstream `if [ "$x" = "PASS" ] || [ "$x" = "WARN" ]` checks already treat empty as FAIL with a
readable reason (no other call site needed a change). Re-verified with fresh fixtures: field-less
global checklist → `overall: "FAIL"`, exit 0; field-less per-feature checklist + missing SHA line
→ `overall: "MISSING"`, exit 0, both reasons listed. `bash -n` clean. Downstream copies made by
`/ms.init` before this fix still carry the bug — re-run `/ms.init`'s script-install step (or copy
`docs/templates/scripts/specter-gate.sh` manually) in any project initialized prior to 2026-07-03.

#### F-2 (DECISION → then implement) — RESOLVED 2026-07-03 (b, drop): Restore or formally drop the `Source Command` staleness check

The pre-WI-11 `ms.checklist.md` required the global audit to record
`**Source Command**: /ms.verify` (rejecting artifacts from the removed legacy
`/ms.checklist --global` flow). The script rewrite silently dropped this check —
`specter-gate.sh` has no equivalent field and `ms.checklist.md` no longer mentions it.
Options: (a) add a `source_command` check to `specter-gate.sh` (one grep), or (b) accept the drop
on the grounds that no legacy artifacts remain in any active project — if (b), delete the
`**Source Command**` line from the `/ms.verify` output template too so the field doesn't linger
as dead metadata. Either way, the decision should be recorded here, not left implicit.

**Resolution**: (b) — dropped. Re-verified during this pass: nothing reads the field except a
human eyeballing it; `specter-gate.sh` and `/ms.checklist` already validate global-mode checklists
via `Mode`/`Result`/SHA, and the legacy `/ms.checklist --global` flow the field guarded against no
longer exists. Deleted the `**Source Command**: /ms.verify` line from `/ms.verify.md`'s Step 5
output template. `rg -n "Source Command" .claude/ docs/templates/` now returns zero hits outside
this document.

#### F-3 (minor) — DONE 2026-07-03: Document the agy write-flag re-apply procedure (WI-8 item 6, never done)

The preflight text mentions "a plugin update can transiently reset a flag" but the actual
re-apply procedure was never written down. Add a short subsection to `docs/SYSTEM_MAP.md` (or a
dedicated `docs/ops/` note referenced from the preflight paragraphs): which flag, where it lives,
the exact re-apply command, and how the preflight failure looks when it has been reset.

**Resolution**: created `docs/ops/antigravity-write-flag.md` — the flag
(`--dangerously-skip-permissions`), where it lives
(`~/.claude/plugins/cache/antigravity/antigravity/<version>/scripts/lib/agent-runtime.mjs`, two
argv builders), why it resets (cache is not git-tracked, marketplace copy is stale/irrelevant),
the exact re-apply steps, and what the preflight failure looks like. Added a one-line pointer to
it from all 5 command files that repeat the caveat: `ms.verify.md`, `ms.agent-verify.md`,
`ms.codex-checklist.md`, `ms.analyze.md`, `ms.review.md`.

#### F-4 (minor, documented trade-offs — implement only if desired) — DONE 2026-07-03 (both applied): WI-13 hook hardening

1. *Stale-token leak*: if a session dies between `/ms.specify` Step 0.3 (token write) and
   Step 3.2 (delete), `.specify/.ms-gate-pass-<NNN>` persists with no TTL, permitting one later
   direct `/speckit-specify` bypass. Optional fix: hook ignores tokens older than ~1 h (mtime
   check) — acceptable to skip for solo use.
2. *Fail-open without jq*: on a machine without `jq` the hook silently allows everything
   (install-time warning only). Optional fix: fall back to a `grep`-based parse instead of
   allowing. Both risks are stated in the script header; this item just decides whether to close
   them.

**Resolution**: both applied to `speckit-specify-gate-hook.sh`. TTL: `.ms-gate-pass-*` tokens
older than 60 minutes (`find ... -mmin -60`) are now treated as absent. jq-less fallback: instead
of blanket-allowing when `jq` is missing, the hook greps raw stdin for the skill field and only
fails open when the skill genuinely can't be determined. Re-verified with 8 fixture cases (4
with `jq`, 4 without: deny/allow/stale-deny/malformed-allow in each) — all passed.

#### F-5 (cleanup, low priority) — DONE 2026-07-03: Centralize `/ms.review`'s final-verdict logic

The READY / READY WITH WARNINGS / NOT READY computation is now stated in three places
(Step 6.5.C gate handling, Step 6.6 Done-Criteria rule, Step 6.7.B agent-result handling). All
three are mutually consistent today; fold them into one "Result Model" subsection that the three
steps reference, so future edits can't diverge them.

**Resolution**: added a `### Result Model` subsection under Step 6 (Consolidate and Score)
stating the NOT READY / READY WITH WARNINGS / READY rule once. Steps 6.5.C, 6.6, and 6.7.B now
each state only their own domain-specific CRITICAL/WARNING trigger conditions and reference "the
Result Model (Step 6)" instead of restating the three-way label computation.

---

## Part E — Suggested Implementation Order

1. WI-1 (small, unblocks WI-2)
2. WI-11 (gate script — later WIs call it; immediate token saving)
3. WI-2 (`/ms.expand`)
4. WI-3 (runtime gate — biggest quality lever)
5. WI-4 (merglease)
6. WI-5 + WI-8 (agent policy edits, overlapping files — do together)
7. WI-12, then WI-13 + WI-14 (harness hooks)
8. WI-6 + WI-7 + WI-9 (mechanical text edits)
9. WI-15 (status injection — needs WI-11/12)
10. WI-10 (optional)

Each WI should be one logical-unit commit (AGENTS.md §7). After WI-2 and WI-3, update the README
workflow diagram and the 핵심 커맨드 table to include `/ms.expand` and the runtime gate.

---
name: ms-foundation-prd
description: PRD-authoring skill that co-writes a Product Requirements Document with the user through a one-question-at-a-time interview, tagging gaps inline (assumption/open question) and producing output that /ms.featuremap and /ms.checklist can consume directly — explicit commitments, GEARS-compatible acceptance criteria, and a Testing Decisions section. Use when no PRD exists yet and the user wants to co-author one before /ms.pre-specter, or when extending an existing PRD with a new `## PRD Amendment N` section for /ms.expand.
---

# Foundation: PRD Authoring

## What it does

SPECTER has thorough PRD *auditing* (`/ms.featuremap`, `/ms.checklist`, `/ms.verify`) but no
PRD-*authoring* support — until now. This skill co-writes a PRD with the user through a guided
interview, in a form the rest of the pipeline can consume without rework:

- Every requirement is a **commitment** in the vocabulary `/ms.featuremap` already extracts from
  (functional requirement, user journey, milestone, constraint, acceptance criterion, NFR,
  integration promise, migration/data requirement, or explicit exclusion) — not vague prose.
- A dedicated **Testing Decisions** section identifies the seam each major commitment will be
  tested at, feeding the Done Criteria Execution gate (`/ms.review` Step 6.6) downstream instead
  of that decision surfacing for the first time at implementation.
- Gaps are tagged inline as they're found (🔶 Assumption / 🔵 Open Question), not buried in a
  closing "questions" section nobody re-reads.

## When to use

- No PRD exists yet and the user wants to co-author one before `/ms.pre-specter`.
- Extending an existing PRD: produce a `## PRD Amendment N — YYYY-MM-DD` section appended to the
  end of the file (never edit prior sections), matching the format `/ms.expand` consumes.
- The user has scattered notes/a conversation's worth of context and wants it turned into a
  structured PRD rather than starting from a blank page.

## How it works

### 0. Calibrate on the user's unknowns first

The gap between what the user can state and what the work actually needs is the unknowns, in
four quadrants — and each has a different move:

| Quadrant | What it is | Move |
| --- | --- | --- |
| Known Knowns | What they can state in the prompt | Record as commitments |
| Known Unknowns | Decisions they know are open | The interview (below) |
| Unknown Knowns | "보면 안다" — obvious to them, never written | Brainstorm divergent options / spike-skill prototype / **references** to react to |
| Unknown Unknowns | Never considered at all | **Blindspot pass**: teach the domain's potholes, prior art, and what "good" looks like before asking anything |

Two rules that follow from this:
- **Start by capturing the user's starting point** (experience with the domain and codebase,
  where they are in their thinking) — it decides how much blindspot-teaching each phase needs.
- **When the user can't articulate what they want, ask for a reference** — an existing
  repo/module/library/design they like — and read its *source* (not a screenshot) to extract
  the semantics they're pointing at. Source code is the highest-fidelity reference there is.

(When invoked via the `/ms.prd` command, that command runs the blindspot pass, viability gate,
and gap enumeration as explicit macro steps; standalone, apply this section's moves inline.)

### 1. Prefer synthesis over interrogation

If the current conversation, or the codebase itself, already answers a question, use that instead
of asking — read the relevant code/ADRs/docs first. Only interview the user for gaps that
genuinely cannot be resolved by exploration.

### 2. Interview discipline (when you do need to ask)

- **One question at a time.** Asking several at once is disorienting and produces shallow
  answers.
- **Architecture-impact order.** Ask first the questions whose answers would change data
  models, interfaces, or user-facing flows; threshold-tuning questions come last (and accept
  "런타임에 조정할 것" as a valid answer — record it as a 🔶 runtime-tunable assumption).
- **Always offer a recommended answer.** State your default and why; let the user accept or
  redirect it, rather than asking an open-ended question with no anchor.
- **Durable domain language, not file paths.** Requirements should read in terms the domain
  glossary already uses ("the upload service", "the billing cycle"), never `src/foo/bar.ts` —
  paths go stale within weeks and this document is meant to outlive the current code layout.
  Exception: if a prototype produced a snippet that encodes a decision more precisely than prose
  can (a state machine, a schema shape), inline just that snippet next to the decision it encodes
  and say it came from a prototype — not a working demo, just the decision-bearing fragment.
- **Tag gaps where they appear**, not at the end: 🔶 **Assumption** for something plausible but
  unvalidated, 🔵 **Open Question** for something genuinely unknown that needs discovery. A reader
  scanning any one section should immediately see what in that section is still soft.

### 3. The interview flow (8 phases)

Work through these in order; each phase's output becomes one section of the PRD. Skip a phase
only if the user explicitly says it doesn't apply (e.g. no strategic/business context to record
for an internal tool).

1. **Problem** — who has this problem, what it is, why it's painful, what evidence exists.
2. **Personas** — the primary actor(s) this PRD serves; secondary actors if relevant.
3. **Strategic context** — why now, what this unblocks or aligns with (skip freely for
   internal/small projects; don't force TAM/SAM/SOM-style content where it doesn't apply).
4. **Solution** — the high-level approach and key capabilities, in domain language.
5. **Success metrics** — including at least one **guardrail metric** (a thing that must NOT get
   worse as a side effect of shipping this), not just an adoption/growth number.
6. **User stories & acceptance criteria** — write acceptance criteria in
   GEARS-compatible form (canonical form and rules: Constitution §II /
   `constitution-template.md`) so `/ms.featuremap` can lift them directly
   into a Feature's `### Done criteria` without a rewrite pass.
7. **Testing Decisions** — for each major commitment from phase 6, name the seam it will be
   tested at (unit/integration/e2e/manual) and point to prior art already in the codebase for that
   kind of test, if any exists.
8. **Out of scope / dependencies** — explicit exclusions, each one naming what it depends on or
   defers to, not just "not doing this."

After each phase, do a **one-line consistency check** against the phases already written before
moving on (e.g. "this success metric assumes the persona from Phase 2 — still accurate?") — cheap,
catches drift immediately instead of at the end.

### 4. SPECTER wiring — why the sections above, specifically

- **Commitments** (phases 1, 4, 6, 8) must each be traceable to one Feature after
  `/ms.featuremap` slices them — write them as discrete, indexable statements, not paragraphs a
  human has to re-parse into a list.
- **Acceptance criteria** (phase 6) in GEARS form flow straight into `### Done criteria`;
  non-GEARS prose acceptance criteria cost a rewrite pass at `/ms.specify`/`/ms.clarify` time.
- **Testing Decisions** (phase 7) is read by `/ms.review` Step 6.6 when classifying a Done
  Criterion as RUNNABLE vs MANUAL — a PRD that already names the seam skips that classification
  work per-Feature.
- **Amendments**: when extending an existing PRD rather than starting fresh, append a
  `## PRD Amendment N — YYYY-MM-DD` section at the end of the file (N = next integer after the
  highest existing one) containing only the new phases 1-8 content for the addition — never edit
  or renumber a prior amendment or the original sections. This is exactly the input
  `/ms.expand` extracts from; do not use a separate file for it.

### 5. Anti-patterns (what this is not)

- **Not a pixel-level spec.** Frame the problem and solution; leave UI-pixel detail and file-level
  design to `/ms.plan`/`/ms.specify`.
- **Not a frozen waterfall contract.** A PRD may get a new Amendment section later — that's
  `/ms.expand`'s job, not a reason to over-specify now to avoid ever touching it again.
- **Not a replacement for the interview.** Do not silently fill every gap with an assumption to
  finish faster — tag genuine unknowns as 🔵 Open Question and let the user resolve them.

Common pitfalls to actively guard against while interviewing:

| Pitfall | What it looks like | Guard |
| --- | --- | --- |
| Solution-first | Jumping to a feature list before the problem is written | Refuse to start phase 4 before phase 1 has evidence, not just a claim |
| Metric theater | A vanity metric with no guardrail | Phase 5 requires at least one guardrail metric |
| Scope creep by omission | An exclusion with no named destination | Phase 8 requires every exclusion to name what handles it |
| Stakeholder surprise | Sections drift out of sync as the interview proceeds | The one-line consistency check after each phase |

### 6. Templates

Three templates in `references/prd_templates.md`, scaled to project size — offer the user a
choice rather than defaulting to the heaviest one:

- **Standard** — full 8-phase document, for a PRD that will drive `/ms.pre-specter` across
  multiple Features.
- **One-Page** — condensed single-page form, for a small project or an early sketch that will be
  fleshed out later.
- **Feature-Brief** — lightweight hypothesis-shaped brief (context, hypothesis, effort estimate,
  next steps), for something too small to warrant a full PRD but that still needs the
  problem-first discipline.

## Works well with

- Constitution §II (GEARS): acceptance criteria written in phase 6 should already be GEARS-compatible.
- `/ms.pre-specter`: the natural next step once a Standard-template PRD is complete.
- `/ms.expand`: consumes this skill's `## PRD Amendment N` output directly.

---
description: "Decompose a PRD into a Feature Map — the MANDATORY upstream artifact for /ms.specify"
---

# /ms.featuremap - Decompose PRD into a Feature Map

Transform a PRD (Product Requirements Document) into a **Feature Map**: a dependency-ordered
graph of independently implementable, mergeable, and shippable vertical slices (Features).

This command is the **front of the Specter pipeline** and runs **BEFORE** `/ms.specify`.

```
/ms.featuremap  →  /ms.checklist --global
                 →  repeat per Feature in DAG order:
                    /ms.checklist  →  /ms.specify  →  /ms.clarify  →  /ms.plan
                    →  /ms.constitution (once if needed)  →  /ms.tasks
                    →  /ms.analyze  →  /ms.implement  →  /ms.review
```

> ⛔ **Hard contract**: `/ms.specify` MUST consume a Feature section produced by THIS command.
> A spec must never be created freeform or from a hand-written spec.md. The Feature Map is the
> single, mandatory bridge between the PRD and every spec. No Feature Map → no spec.

## Usage

```
/ms.featuremap @docs/prd/PRD.md
/ms.featuremap                 # (then attach or reference the PRD document)
```

`$ARGUMENTS` = path to the PRD (or an attached document). If empty, look for an attached
document or the most likely PRD under `docs/prd/` and confirm with the user before proceeding.

## Language Policy (MANDATORY)

- **The Feature Map document is written in ENGLISH, unconditionally.** It is a workflow document
  (Constitution Section IV: spec.md / plan.md / tasks.md and their upstream artifacts are English).
  All section content — summaries, scope, decisions, criteria — is English.
- **Interaction with the user may be Korean** (questions, confirmations, the final report).
  Only the persisted `feature-map.md` is forced to English.

---

## Core Philosophy (NEVER violate)

1. **The PRD is the Single Source of Truth.** The Feature Map does NOT duplicate the spec.
   Each Feature *references* the relevant PRD section numbers; detailed requirements stay in the PRD.
   The Feature Map's only job is to define **"where one Feature begins and ends"** (the boundary).
   To keep the PRD from becoming blurry, the Feature Map MUST include a thin **PRD Commitment Index**
   that maps each PRD commitment to exactly one owning Feature.
2. **1 Feature = the smallest vertical slice that can be implemented, merged, and verified
   independently.** Each Feature starts from the state where the previous Feature is merged to main;
   each is its own branch. Size sense: smaller than a Phase, larger than a trivial one-PR chore
   (roughly a few days to ~1 week).
3. **Every deferred item has an owner.** Anything pushed out of scope MUST name its owning Feature
   as `→ Feature NNN`. No responsibility gaps allowed.

---

## Execution Steps

### 1. Load Context

**Read (REQUIRED):**
- The PRD at `$ARGUMENTS` (or attached/located document). Read it in FULL before writing anything.

**Read (if they exist):**
- `docs/prd/product-principles.md` (or equivalent behavioral-norms doc)
- `.specify/memory/constitution.md` (development methodology + project constraints)
- `AGENTS.md` / `CLAUDE.md`

**IF no PRD can be found or confirmed** → ask the user for the PRD path and STOP. Do not guess content.

### 2. Run the Decomposition Algorithm (think through ALL steps before writing)

#### STEP 1 — Extract PRD commitments before slicing
Read the PRD and enumerate every durable commitment before creating Features. A commitment is any
functional requirement, user journey, milestone promise, constraint, acceptance criterion,
non-functional requirement, integration promise, migration/data requirement, or explicit exclusion.

Write each commitment as an index row with a stable PRD reference and exactly one owning Feature
after slicing is complete. Do not copy full PRD prose; summarize only enough to make ownership
auditable.

#### STEP 2 — Extract Phases (the release skeleton)
- Use the PRD's milestone/roadmap section as the skeleton for Phases.
- If there is no milestone section, cut Phases yourself by **"shippable bundles of value."**
- Each Phase = one theme + a rough duration + the **end-to-end (E2E) scenario** that must work at the
  Phase's end.
- Typically 2–4 Phases: infrastructure/foundation → core value → hardening/stabilization.

#### STEP 3 — Derive Feature candidates (slice the functional spec)
Scan the PRD's functional-spec section(s) and cut capability-sized candidates using these rules:
- **(a) Infrastructure/foundation first**: repo, DB schema skeleton, auth, environment → consolidate
  into the first Feature(s).
- **(b) Split engine from screen**: ship a backend capability (API/pipeline) as one Feature, and its UI
  as a *later* Feature (e.g. chat engine → chat UI; generation pipeline → solving screen).
- **(c) Consolidate cross-cutting concerns into a late, dedicated Feature**: rules that span many
  features (authz/group differentiation, i18n, audit log, observability) must NOT be scattered — gather
  them into one Feature.
- **(d) Ops/stabilization is the last Feature**: backup, restore, tuning, regression.
- If a Feature grows too large (many files / 3+ domains) → split it. If too small → merge with an
  adjacent capability.

#### STEP 4 — Topologically order into a dependency DAG
- Draw what each Feature depends on. **If a cycle appears, re-cut the boundaries.**
- Prefer a near-linear order; mark parallel only when genuinely independent.

#### STEP 5 — Identify Stub-and-Forward (the most important technique)
- Shared foundations used by many Features (the FULL DB schema, middleware hooks, UI panel slots,
  settings tables) are **laid down as no-op stubs/placeholders in the FIRST Feature**, and their real
  behavior is **activated in a dedicated later Feature**. In each Feature body, state explicitly:
  *"stub only here; real behavior → Feature NNN."*
- Pre-allocate migration numbers per Feature (0001, 0002 … each Feature owns its own).

#### STEP 6 — Fill the PRD Commitment Index
After the Features are ordered, fill the index. Every row MUST have an owning Feature. Cross-cutting
commitments still get exactly one owning Feature; earlier Features may include stubs, but the real
behavior owner must be explicit.

#### STEP 7 — Write each Feature using the fixed template (below).

#### STEP 8 — Put the Phase's E2E integration scenario into the **completion criteria of that Phase's
last Feature.**

### 3. Feature Section — FIXED template (identical for every Feature, ENGLISH)

```markdown
---
## Feature NNN: <name>

### One-line summary
<what it builds, in one sentence>

### PRD references
- <§x.y title> (the PRD location this Feature implements; details live in the PRD)
- ...

### In scope
**<sub-group title>**
- <concrete deliverable / endpoint / module — list implementation units, do NOT copy PRD prose>
...
**Tests**
- <test cases that MUST pass in this Feature>

### Explicitly out of scope
- <deferred item> → NNN
- ... (every item MUST name its owning Feature number)

### Key decisions
- <locked tech/architecture/policy decisions; include clarify conclusions if already decided>

### Done criteria
- <observable criteria a human can click/run to declare "done">
- ... (the LAST line is always "CI passes green")
---
```

### 4. Assemble the full document (in this order)

1. **Header** — version / based-on PRD version / document role
   (= "the standard source for `/ms.specify` input").
2. **Usage** — per-Feature workflow + the copy-paste pattern into `/ms.specify`.
3. **PRD Commitment Index** — the thin ownership map that prevents PRD requirements from being
   blurred or lost (template below).
4. **Full Feature dependency graph** — an ASCII DAG grouped by Phase.
5. **Progress Ledger** — a status table of every Feature (template below). Emit all rows as
   `⬜ planned`. It is a convenience view; the canonical truth is `specs/` + git, and
   `/ms.specify` refreshes the Status column from `specs/` each time a Feature is started.
6. **All Feature sections**, grouped by Phase, using the fixed template.
7. **Global rules** — branch/commit conventions, TAG system, reference priority
   (reference priority = PRD > product-principles > constitution > feature-map > dependency Feature spec).

### PRD Commitment Index — template (emit before the dependency graph)

```markdown
## PRD Commitment Index

> Thin ownership map. Details stay in the PRD; this table only proves that every PRD commitment has
> exactly one owning Feature. `/ms.checklist --global` audits the whole table, and `/ms.checklist`
> audits the next Feature's rows before `/ms.specify`.

| PRD Ref | Commitment Type | Short Label | Owning Feature | Handling |
|---------|-----------------|-------------|----------------|----------|
| §3.1 | Functional | User login | Feature 002 | Implemented |
| §5.2 | Cross-cutting | Audit log | Feature 009 | Deferred from earlier Features |
```

### Progress Ledger — template (emit right after the dependency graph)

```markdown
## Progress Ledger

> Convenience view — the canonical truth is `specs/<NNN>-*` (started) + merged PRs/tags (shipped).
> `/ms.specify` recomputes the Status column from `specs/` every time you start a Feature, so
> this table cannot drift. Update `✅ shipped` by hand (or via /ms.merglease) when a Feature releases.
> Legend: ⬜ planned · 🚧 specified (a `specs/<NNN>-*` dir exists) · ✅ shipped (merged + released)
>
> **Next Feature** = the lowest-order Feature whose dependencies are all done and which has no
> `specs/` directory yet.

| Feature | Depends on | Status |
|---------|------------|--------|
| 001 <name> | — | ⬜ planned |
| 002 <name> | 001 | ⬜ planned |
| … | … | ⬜ planned |
```

### 5. Write the file

Write the assembled document to **`docs/prd/feature-map.md`** (default — PRD artifacts live in
the `prd` directory). If `docs/prd/` does not exist in this project, create it; do NOT fall back to
`docs/feature-map.md`. Confirm the path with the user only if the project clearly keeps PRD docs
somewhere else.

### 6. Report

```
✅ Feature Map created: docs/prd/feature-map.md

📊 <N> Phases, <M> Features
🔗 Dependency DAG: validated (no cycles)
🧩 Stub-and-Forward points: <list>

🎯 Next step — validate the whole Feature Map before starting the Feature cycle:
   /ms.checklist --global

After the global checklist passes, validate the FIRST Feature and then specify it:
   /ms.checklist
   /ms.specify  + paste the "Feature 001" section from docs/prd/feature-map.md

⛔ Reminder: /ms.specify must be driven by a Feature section from THIS file, and
   it will refuse to run if the global or per-Feature checklist is missing or failed.
```

---

## Writing Discipline (failure conditions)

- ❌ Not English. The persisted Feature Map MUST be English (Language Policy above).
- ❌ No vague words ("good enough", "fast", "robust", "secure", "user-friendly"). Criteria must be measurable.
- ❌ Do NOT duplicate the spec — reference PRD sections. The Feature Map is an index + boundary.
- ❌ FAIL if the PRD Commitment Index is missing or any row lacks exactly one owning Feature.
- ❌ FAIL if any out-of-scope item lacks an owning Feature.
- ❌ FAIL if the dependency graph has a cycle.
- ❌ FAIL if a Phase's last Feature has no E2E integration scenario.
- ✅ Read the entire PRD and finish STEP 1–8 mentally BEFORE writing. Verify against the PRD; do not guess.

---

## Next Command

After `/ms.featuremap`:
1. Run `/ms.checklist --global` to validate PRD coverage, Feature ownership, DAG, and template completeness.
2. Fix any blocking issues in `docs/prd/feature-map.md` and re-run `/ms.checklist --global`.
3. Run `/ms.checklist` to validate the next eligible Feature against its PRD references and commitment rows.
4. After the per-Feature checklist passes, open `docs/prd/feature-map.md`, read the selected Feature section in full.
5. Run `/ms.specify` and paste that Feature section as the input.
6. Proceed through the dependency graph one Feature at a time, in order.

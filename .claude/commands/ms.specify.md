---
description: "Create feature specification with Constitution reference"
---

# /ms.specify - Create Feature Specification

Create a feature specification following Spec-Kit workflow with Constitution compliance.

## Overview

This command extends `/speckit.specify` to include explicit Constitution references, ensuring AI follows GEARS, TRUST, and TAG principles during specification writing.

> ⛔ **Upstream contract — Feature Map is MANDATORY.** This command runs AFTER `/ms.featuremap`.
> Its input MUST be a **Feature section copied from `docs/prd/feature-map.md`** (the Feature Map
> produced by `/ms.featuremap` from the PRD set). That Feature section is the actual prompt for
> `/ms.specify`; it must include Source PRDs and PRD references so the command can read every
> relevant source document. A spec must NEVER be created freeform, from inline ad-hoc text, or
> from a pre-existing `spec.md`. The Feature Map is the single, mandatory bridge from PRDs → spec —
> bypassing it makes the spec meaningless. No Feature section → do not proceed (see Step 0).

## Usage

```
/ms.specify
<paste the "Feature NNN" section from docs/prd/feature-map.md here>
```

Example:

```
/ms.specify
## Feature 001: Foundation
### Source PRDs
- Product PRD: docs/prd/product.md
### One-line summary
... (full Feature section from docs/prd/feature-map.md) ...
```

## Execution Steps

### 0. REQUIRE Feature Map Input (HARD GATE — runs first)

Before anything else, verify the input is a Feature section originating from the Feature Map.

**Checks:**
1. At least one Feature Map file exists. Look for any of:
   `docs/feature-map.md`, `docs/prd/feature-map.md`, or `docs/**/feature-map*.md`
   (the per-feature convention `docs/prd/feature-map_<NNN>_*.md` counts — those are
   also `/ms.featuremap` outputs).
   ```bash
   FEATUREMAP_FILES=$(ls docs/feature-map*.md docs/prd/feature-map*.md 2>/dev/null)
   ```
   - **IF none found** → display the error below and EXIT. Do NOT create a spec.
2. The input (`$ARGUMENTS` or attached/pasted text) is a **Feature section** — i.e. it contains the
   Feature-Map template markers (a `## Feature NNN:` heading plus `### Source PRDs`,
   `### PRD references`, `### In scope`, `### Explicitly out of scope`, `### Done criteria`), OR it clearly names a Feature whose section can
   be read directly from the Feature Map file.
   - **IF the input is freeform prose, an inline ad-hoc request, or derived from an existing spec.md**
     → REFUSE and EXIT with the error below.
3. Treat the matched Feature section as the **authoritative scope boundary** for this spec.
   The PRD (referenced by that section) remains the single source of truth for detail.

**Gate failure message:**

```
⛔ /ms.specify requires a Feature Map.

A spec must be driven by a Feature section from docs/prd/feature-map.md — never freeform,
never from inline text, never from a pre-existing spec.md.

Do this first:
  1. /ms.featuremap @docs/prd/PRD.md [@docs/prd/another.md]   → generates docs/prd/feature-map.md
  2. /ms.checklist --global
  3. /ms.constitution
  4. /ms.checklist
  5. Open docs/prd/feature-map.md, copy the checked "Feature NNN" section you want to build
  6. /ms.specify  + paste that Feature section

Stopping now.
```

**Only if the Feature Map input gate passes**, continue to Step 0.2.

### 0.2 REQUIRE Global And Per-Feature Checklists (HARD GATE)

Before creating a spec, verify that `/ms.checklist --global` has validated the
whole Feature Map and `/ms.checklist` has validated the selected Feature. This
keeps Spec-Kit's native checklist from becoming the first real validation point,
which would be too late.

**Checks:**

1. Identify the Feature number from the input's `## Feature NNN:` heading before
   checking audit files.
2. `docs/prd/feature-map.checklist.md` exists.
3. The global audit contains `**Mode**: global`.
4. The global audit contains `**Result**: PASS` or `**Result**: WARN`.
5. The global audit does not contain `**Result**: FAIL`.
6. The global audit's `Feature Map SHA256` matches the current
   `docs/prd/feature-map.md` SHA256.
7. `docs/prd/checklists/feature-NNN.checklist.md` exists for the selected Feature.
8. The per-Feature audit contains `**Mode**: per-feature` and the same Feature NNN.
9. The per-Feature audit contains `**Result**: PASS` or `**Result**: WARN`.
10. The per-Feature audit does not contain `**Result**: FAIL`.
11. The per-Feature audit's `Feature Map SHA256` matches the current
    `docs/prd/feature-map.md` SHA256.
12. `.specify/memory/constitution.md` has an established Section IX baseline from `/ms.constitution`
    or explicitly records that no durable project-specific constraints were found.

**If the global audit is missing, failed, or stale**, refuse and exit:

```text
⛔ /ms.specify requires a passing global Feature Map checklist.

Run this first:
  /ms.checklist --global

Fix any Blocking Fixes in docs/prd/feature-map.checklist.md, re-run /ms.checklist --global,
then retry the Feature checklist.
Stopping now.
```

**If the per-Feature audit is missing, failed, stale, or for a different Feature**, refuse and exit:

```text
⛔ /ms.specify requires a passing checklist for this Feature.

Run this first:
  /ms.checklist

This validates the selected Feature against its PRD references and PRD Commitment Index rows.
Fix any Blocking Fixes in docs/prd/checklists/feature-NNN.checklist.md, re-run /ms.checklist,
then retry /ms.specify.
Stopping now.
```

**If Section IX is not established**, refuse and exit:

```text
⛔ /ms.specify requires the project Constitution baseline.

Run this first:
  /ms.constitution

This establishes Section IX from the checked PRD Feature Map before individual specs are created.
Stopping now.
```

Only if all gates pass, continue to Step 0.4.

### 0.4 Load Source PRDs For The Feature Prompt

Before invoking `/speckit.specify`, load the PRD context referenced by the checked Feature section.

1. Read every document listed under the Feature section's `### Source PRDs` heading.
2. Read every PRD section named under `### PRD references`.
3. Read the matching PRD Commitment Index rows for this Feature.
4. Build the `/speckit.specify` prompt from:
   - the full checked Feature section,
   - the relevant PRD excerpts from every Source PRD,
   - the matching Commitment Index rows,
   - and the global reference priority from the Feature Map.

If any Source PRD is missing or a PRD reference cannot be resolved, stop and ask the user to fix
`docs/prd/feature-map.md` or rerun `/ms.checklist`.

Only after the PRD context is loaded, continue to Step 0.5.

### 0.5 Reconcile Feature progress + pick next (refreshes the Progress Ledger)

This is the cross-session "where am I" answer. Progress lives in `specs/` + git; the Feature
Map's **Progress Ledger** is just a cached view of it, recomputed here so it never drifts.

1. Identify the Feature being specified from the input's `## Feature NNN:` heading.
2. List which Features already have a spec directory (= started):
   ```bash
   ls -d specs/*/ 2>/dev/null | sed 's#specs/##; s#/##'
   ```
3. For every Feature row in `docs/prd/feature-map.md`'s Progress Ledger, recompute Status:
   - `specs/<NNN>-*` directory exists → `🚧 specified` (or `✅ shipped` if you can confirm a
     merged release for it), else `⬜ planned`. **Rewrite the Status column** to match.
4. Determine the **next undone Feature** = the lowest-order Feature in the dependency DAG whose
   dependencies are all started and which has no `specs/` directory of its own.
5. **Report (Korean is fine):**
   ```
   📍 지금 시작: Feature NNN <name>
   ✅ 완료까지: <started/shipped 목록 요약>
   ➡️  DAG상 다음 미완료: Feature MMM
   ```
6. **Warn and ask for confirmation** if the Feature being started skips an unmet dependency
   (i.e. some Feature it depends on has no `specs/` dir yet) — that breaks the DAG order.

Then continue to Step 1.

### 1. Load Project Context

**Auto-load project documents**:
- `.specify/memory/constitution.md` (Constitution - REQUIRED)
- `AGENTS.md` (AI instructions, coding standards - if exists)

**IF Constitution missing**:
- Display error: "Constitution not found. Run `/ms.init` first."
- Exit

**IF AGENTS.md missing**:
- Display notice: "AGENTS.md not found; `/ms.constitution` should already have created or updated it before this step"
- Continue

**Reference key sections**:
- Constitution Section IV (GEARS Standards)
- Constitution Section V (TRUST Principles)
- Constitution Section IX (Project-specific baseline established from the checked PRD Feature Map by `/ms.constitution`)
- project-structure.md (understand existing tech stack - **if exists**)

### 2. Inject Constitution Context into AI Prompt

Before running `/speckit.specify`, provide AI with Constitution reference:

```
You are creating a specification that MUST follow the project Constitution.

**Constitution**: .specify/memory/constitution.md

**Read and apply these sections**:
- **Section IV**: Requirements Clarity (GEARS Standards) - Use the GEARS canonical form ([Where][While][When] the <subject> shall <behavior>)
- **Section V**: TRUST 5 Principles - Design for testability, readability, security, traceability

**Language Policy**:
- Write ALL requirements in ENGLISH
- Use GEARS keywords (Where / While / When, and shall) in English
- If user provides Korean input, translate to English GEARS

**Example**:
User input (Korean): "사용자가 로그인하면 토큰을 발급한다"
Your output (English): "When a user logs in with valid credentials, the auth service shall issue a JWT session token."

**Refer to Constitution for detailed GEARS rules and TRUST principles.**

Now create the specification following these principles.
```

### 2.5. Adaptive Context Analysis (Quantitative Decision)

**Step 1: Analyze User Request (Mandatory)**

Extract and count keywords from `$ARGUMENTS`:

```bash
# Count simple keywords
SIMPLE_KEYWORDS=$(echo "$ARGUMENTS" | grep -iEo "\b(config|setting|constant|type|interface|util|helper|log|message)\b" | wc -l)

# Count moderate keywords
MODERATE_KEYWORDS=$(echo "$ARGUMENTS" | grep -iEo "\b(feature|module|component|endpoint|model|service|page|form)\b" | wc -l)

# Count complex keywords
COMPLEX_KEYWORDS=$(echo "$ARGUMENTS" | grep -iEo "\b(system|architecture|integration|external|api|realtime|workflow|migration)\b" | wc -l)

# Check for existing similar specs
SIMILAR_SPECS=$(find specs/ -name "spec.md" 2>/dev/null | wc -l)
```

**Step 2: Apply Decision Tree**

Execute in priority order (stop at first match):

```
┌─────────────────────────────────────────────────────────────┐
│ DECISION TREE (Priority Order)                              │
├─────────────────────────────────────────────────────────────┤
│ 1. IF COMPLEX_KEYWORDS ≥ 2                                  │
│    → COMPLEX (system-level change)                          │
│                                                              │
│ 2. IF SIMPLE_KEYWORDS ≥ 2 AND COMPLEX_KEYWORDS = 0          │
│    → SIMPLE (config/utility change)                         │
│                                                              │
│ 3. IF MODERATE_KEYWORDS ≥ 1 OR SIMILAR_SPECS ≥ 3            │
│    → MODERATE (feature with patterns available)            │
│                                                              │
│ 4. IF SIMPLE_KEYWORDS ≥ 1 AND MODERATE_KEYWORDS = 0         │
│    → SIMPLE                                                  │
│                                                              │
│ 5. FALLBACK (unable to determine)                           │
│    → MODERATE (safe default - 2 agents)                     │
└─────────────────────────────────────────────────────────────┘
```

### 3. Run Base Specify Command

#### 3.1. Use The Checked Feature Section As The Only Feature Prompt

Do not accept a new attached PRD, freeform request, or ad-hoc feature description at this stage.
Those inputs belong upstream in `/ms.featuremap`.

The input to `/speckit.specify` is the checked Feature prompt bundle assembled in Step 0.4:

1. The full `## Feature NNN:` section from `docs/prd/feature-map.md`.
2. The Feature's `### Source PRDs` documents and referenced PRD excerpts.
3. The Feature's PRD Commitment Index rows.
4. Constitution context and reference priority.

If the user provides new source material here, stop and tell them to update the PRD set and rerun:

```text
/ms.featuremap
/ms.checklist --global
/ms.constitution
/ms.checklist
```

#### 3.2. Execute Speckit Specify

Execute `/speckit.specify` with the checked Feature prompt bundle and Constitution-enhanced context:

```
/speckit.specify <checked Feature prompt bundle from Step 0.4>
```

**Agent Delegation**: This internally uses the **spec-builder** agent (Sonnet model) for GEARS conversion and SPEC document generation.

This creates the specification in `specs/{SPEC_ID}/spec.md` with AI automatically following GEARS and TRUST principles.

### 4. Add Constitution Reference Footer

After spec.md is created, append Constitution reference section to document:

```markdown
---

## 📜 Constitution

This specification follows the project [Constitution](../../.specify/memory/constitution.md).

**Key Sections:**
- **Section IV**: GEARS Requirements Standards
- **Section V**: TRUST 5 Quality Principles
- **TAG System**: Traceability (SPEC → TEST → CODE)

_Auto-added by `/ms.specify`_
```

### 5. Report Success

Display summary:

```json
{
    "spec_created": "specs/001-user-authentication/spec.md",
    "constitution_referenced": true,
    "constitution_exists": true,
    "next_step": "/ms.clarify"
}
```

Display next steps:

```
✅ Specification created successfully!

📄 Spec: specs/001-user-authentication/spec.md
📜 Constitution: .specify/memory/constitution.md

🎯 Next Steps:
1. Review spec.md for completeness
2. Run `/ms.clarify` to settle or explicitly confirm remaining decisions
3. Then proceed to `/ms.plan` for implementation planning

📖 Constitution Sections Applied:
- Section IV: GEARS (5 requirement patterns)
- Section V: TRUST (5 quality principles)
```

## Error Handling

### Error 1: Spec-Kit Not Initialized

**Symptom**: `.specify/` directory missing

**Message**:

```
❌ Error: Spec-Kit not initialized

This project has not been initialized with Spec-Kit.

Please run:
  /ms.init

This will set up Spec-Kit templates AND create the Constitution.
```

**Exit**: Code 1

## Next Command

After `/ms.specify`:
1. Run `/ms.clarify` to settle or explicitly confirm remaining decisions.
2. Then proceed to `/ms.plan` for implementation planning.

`/ms.checklist --global` and the per-Feature `/ms.checklist` are pre-spec gates
and should already have passed before this command ran.

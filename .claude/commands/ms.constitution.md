---
description: "Establish project-specific Constitution Section IX from the checked PRD Feature Map"
---

# /ms.constitution - Establish Project Baseline Rules

Extract durable project-specific constraints from the PRD set and checked Feature Map, then update:

1. **Constitution Section IX**: project-wide product and technical constraints
2. **AGENTS.md**: concrete coding rules and verification checks
3. **README.md**: project README initialization, if the root README is still the SPECTER template

This command normally runs **once**, after `/ms.checklist --global` and before the per-Feature cycle
starts. It is not a per-Feature ceremony. Later Features should use the established Constitution and
only re-run this command when the user explicitly wants to revise durable project rules.

## Why It Runs After The Global Feature Map Audit

The checked Feature Map is the first artifact that sees the whole product shape: all source PRDs,
the PRD Commitment Index, the dependency DAG, cross-cutting owners, and deferred work. Section IX
should capture durable rules that apply across future Features before `/ms.specify` starts turning
individual Feature prompts into isolated specs.

`/ms.constitution` does **not** promote one Feature's implementation details. It extracts rules that
are already visible at the PRD/Feature Map level and should constrain every later `spec.md`, `plan.md`,
`tasks.md`, and implementation.

## Workflow Position

```text
/ms.featuremap → /ms.checklist --global → /ms.constitution
                                      → /ms.checklist → /ms.specify → /ms.clarify → /ms.plan → /ms.tasks
```

## GEARS Contract

- When Section IX is empty or still contains template placeholders, `/ms.constitution` shall extract
  durable project-wide constraints from the PRD set and `docs/prd/feature-map.md`.
- When the global Feature Map audit is missing, failed, or stale, `/ms.constitution` shall stop and
  require `/ms.checklist --global` first.
- When Section IX is already populated, `/ms.constitution` shall not silently accumulate new rules; it
  shall stop and ask for explicit user intent before replacing or amending the baseline.
- When a decision is Feature-local or implementation-specific, `/ms.constitution` shall leave it to the
  future Feature's `spec.md`, `plan.md`, or an ADR instead of promoting it to Section IX.
- When AGENTS.md contains `PROJECT_RULES_START` markers, `/ms.constitution` shall replace only the
  generated block between those markers.

## Execution Steps

### Step 0: Prerequisites

Read these files in full:

- `.specify/memory/constitution.md`
- Every Source PRD listed in `docs/prd/feature-map.md`
- `docs/prd/feature-map.md`
- `docs/prd/feature-map.checklist.md`
- `docs/prd/product-principles.md` if it exists
- `AGENTS.md` if it exists

If Constitution, Feature Map, Source PRDs, or the global checklist is missing, stop and tell the user
which upstream command must run first.

### Step 1: Global Audit Guard

Require the global checklist to be current:

1. `docs/prd/feature-map.checklist.md` exists.
2. The audit contains `**Mode**: global`.
3. The audit contains `**Result**: PASS` or `**Result**: WARN`.
4. The audit does not contain `**Result**: FAIL`.
5. The audit's `Feature Map SHA256` matches the current `docs/prd/feature-map.md` SHA256.

If this fails, stop:

```text
⛔ Project baseline cannot be established before the global Feature Map audit passes.

Run this first:
  /ms.checklist --global

Fix any Blocking Fixes in docs/prd/feature-map.checklist.md, then retry /ms.constitution.
```

### Step 2: Baseline Guard

Inspect Constitution Section IX.

Proceed automatically only if Section IX is empty, placeholder-only, or clearly marked as not yet
established.

If Section IX already contains real project rules, stop with this message:

```text
⚠️ Project Constitution baseline already exists.

/ms.constitution is normally a one-time baseline command, not a per-Feature step.
Re-run it only if you intentionally want to revise durable project-wide rules.

Stopping now.
```

### Step 3: Extract Durable Constraints

Extract only constraints that should apply to multiple future Features.

Promote these categories when they are present in the PRD set, product-principles document, or checked
Feature Map:

- Product-wide user roles, permissions, tenancy, or audience boundaries
- Product-wide security, privacy, logging, audit, compliance, or data-retention rules
- Product-wide performance, reliability, accessibility, i18n, or observability targets
- Cross-feature data ownership, migration ownership, naming, lifecycle, or integration contracts
- Explicitly required or forbidden technologies, external services, platforms, or deployment constraints
- Test, lint, type, TAG, or release requirements that differ from the default Constitution
- Stub-and-Forward conventions that future Features must preserve

Do **not** promote:

- One Feature's endpoint list
- One Feature's UI copy or layout
- One Feature's migration implementation detail
- Temporary scaffolding decisions
- Business behavior that belongs in a Feature spec
- Implementation architecture that has not been planned yet

### Step 4: Validate The Baseline

Validate candidate Section IX rules against the full PRD set and Feature Map:

- Every promoted rule cites its source PRD, product-principles section, or Feature Map section.
- No promoted rule contradicts the PRD Commitment Index ownership model.
- No promoted rule forces implementation details that should be decided in `/ms.plan`.
- Product requirements win over Feature Map wording when they conflict.
- The default Constitution wins when it is stricter than the candidate project rule.

If a conflict cannot be resolved from the source documents, stop and ask the user.

### Step 5: Update Section IX

Replace placeholder Section IX with generated content. Keep it empty when no
actual durable constraints exist.

If no durable constraints are found, use exactly:

```markdown
## IX. Project-Specific Constraints

_No project-specific constraints established yet._
```

If durable constraints exist, use only headings that contain actual rules:

```markdown
## IX. Project-Specific Constraints

*Established by `/ms.constitution` from the checked PRD Feature Map on YYYY-MM-DD.*
*This section is not updated per Feature. Re-run only for intentional baseline revision.*

### Source Artifacts

- docs/prd/product.md
- docs/prd/admin.md
- docs/prd/feature-map.md
- docs/prd/feature-map.checklist.md

### Product-Wide Rules

- <durable rule> (source: ...)

### Architecture And Integration Constraints

- <durable rule> (source: ...)

### Security And Data Rules

- <durable rule> (source: ...)

### Quality Gates

- <durable rule> (source: ...)
```

Omit empty categories. Do not invent Technology, Dependency, Architecture,
Security, Performance, or Workflow rules just to fill a template.

### Step 6: Update AGENTS.md

If `AGENTS.md` contains this slot:

```markdown
<!-- PROJECT_RULES_START -->
...
<!-- PROJECT_RULES_END -->
```

replace only the content between the markers with the generated Section IX summary and concrete coding
checks. Preserve all other AGENTS.md content.

If frontend/backend AGENTS.md files exist, distribute only rules that are truly local to those areas.
Keep each generated project-rules block concise.

### Step 7: Initialize README If Needed

Keep the existing functionality, but run it only when the root README is still the SPECTER template or
clearly uninitialized.

If README initialization is needed:

1. Preserve the SPECTER template README at `docs/README.md`.
2. Generate a project README from the PRD set, Feature Map, and Section IX.
3. Link the active Constitution as `.specify/memory/constitution.md`, not `docs/constitution.md`.

If the root README already appears project-specific, do not replace it silently. Report that README
initialization was skipped.

### Step 8: Report

Display in Korean:

```json
{
  "section_ix_established": true,
  "source_prds": ["docs/prd/product.md", "docs/prd/admin.md"],
  "feature_map": "docs/prd/feature-map.md",
  "agents_md_updated": true,
  "readme_initialized": true,
  "constitution_path": ".specify/memory/constitution.md",
  "next_step": "/ms.checklist"
}
```

```text
✅ Project Constitution baseline established.

📄 업데이트된 파일:
- .specify/memory/constitution.md
- AGENTS.md
- README.md (초기화가 필요한 경우에만)

🎯 다음 단계: /ms.checklist

참고: /ms.constitution은 매 Feature마다 실행하지 않습니다. 이후 Feature는
기존 Section IX를 기준으로 /ms.checklist → /ms.specify → /ms.clarify → /ms.plan 흐름을 탑니다.
```

## Error Handling

### Constitution Missing

```text
❌ Constitution not found. Run /ms.init first.
```

### Source Documents Missing

```text
❌ Source documents not found. Run /ms.featuremap first.
```

### Global Checklist Missing Or Stale

```text
❌ Global Feature Map checklist missing or stale. Run /ms.checklist --global first.
```

### No Durable Constraints Found

If no durable project-wide constraints can be extracted, keep Section IX minimal and report that the
default Constitution remains authoritative. Do not invent constraints just to fill the section.

### Conflicting Constraints

If source PRDs, product-principles, Feature Map, and Constitution conflict on a durable rule, stop and
ask the user to choose. Do not silently pick one.

## Next Command

After `/ms.constitution`, run `/ms.checklist` for the first eligible Feature. For later Features, skip
`/ms.constitution` unless the user intentionally revises the project baseline.

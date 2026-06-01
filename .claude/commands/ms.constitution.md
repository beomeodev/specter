---
description: "Establish project-specific Constitution Section IX after the first implementation plan"
---

# /ms.constitution - Establish Project Baseline Rules

Extract durable project-specific constraints from the first mature `spec.md` and
`plan.md`, then update:

1. **Constitution Section IX**: project-wide technical constraints
2. **AGENTS.md**: concrete coding rules and verification checks
3. **README.md**: project README initialization, if the root README is still the
   SPECTER template

This command normally runs **once**, after the first Feature reaches `/ms.plan`.
It is not a per-Feature ceremony. Later Features should use the established
Constitution and only re-run this command when the user explicitly wants to
revise durable project rules.

## Why It Runs After The First Plan

Feature Map shows the product shape, but `plan.md` is the first artifact that
contains concrete architecture, dependencies, file structure, and verification
strategy. Section IX should capture rules that apply across future Features, not
Feature-local implementation details.

## Workflow Position

```text
/ms.plan → /ms.constitution   # normally once, first planned Feature only
/ms.plan → /ms.tasks          # normal path after baseline exists
```

## GEARS Contract

- When Section IX is empty or still contains template placeholders,
  `/ms.constitution` shall extract durable project-wide constraints from
  `spec.md` and `plan.md`.
- When Section IX is already populated, `/ms.constitution` shall not silently
  accumulate new rules; it shall stop and ask for explicit user intent before
  replacing or amending the baseline.
- When a decision is Feature-local, `/ms.constitution` shall leave it in
  `plan.md` or recommend an ADR instead of promoting it to Section IX.
- When AGENTS.md contains `PROJECT_RULES_START` markers, `/ms.constitution` shall
  replace only the generated block between those markers.

## Execution Steps

### Step 0: Prerequisites

Read these files in full:

- `.specify/memory/constitution.md`
- `specs/[spec-id]/spec.md`
- `specs/[spec-id]/plan.md`
- `AGENTS.md` if it exists

If Constitution, `spec.md`, or `plan.md` is missing, stop and tell the user which
upstream command must run first.

### Step 1: Baseline Guard

Inspect Constitution Section IX.

Proceed automatically only if Section IX is empty, placeholder-only, or clearly
marked as not yet established.

If Section IX already contains real project rules, stop with this message:

```text
⚠️ Project Constitution baseline already exists.

/ms.constitution is normally a one-time baseline command, not a per-Feature step.
Re-run it only if you intentionally want to revise durable project-wide rules.

Stopping now.
```

### Step 2: Extract Durable Constraints

Extract only constraints that should apply to multiple future Features.

Promote these categories:

- Technology stack and required versions
- Required dependencies and forbidden dependencies
- Architecture patterns that future Features must follow
- Security requirements that apply across the product
- Performance targets that are product-wide
- Test, lint, type, and TAG requirements that differ from the default

Do **not** promote:

- One Feature's endpoint list
- One Feature's UI copy or layout
- One Feature's migration implementation detail
- Temporary scaffolding decisions
- Business behavior that belongs in `spec.md`

### Step 3: Validate With Agents

Use the same extraction capabilities as before, but synthesize them through the
one-time baseline rule:

- `constitution-extractor`: candidate Section IX constraints
- `trust-validator`: conflict and completeness validation
- AGENTS rule generation: concrete examples/checks for existing AGENTS.md files

Resolve conflicts in favor of `spec.md` for product requirements and `plan.md`
for implementation architecture, unless Constitution already has a stricter
non-negotiable rule.

### Step 4: Update Section IX

Replace placeholder Section IX with generated content. Use this structure:

```markdown
## IX. Project-Specific Constraints

*Established by `/ms.constitution` from the first planned Feature on YYYY-MM-DD.*
*This section is not updated per Feature. Re-run only for intentional baseline revision.*

### Technology Stack

✅ **Required**:
- ...

❌ **Forbidden**:
- ...

### Dependencies

✅ **Required**:
- ...

❌ **Forbidden**:
- ...

### Architecture

✅ **Required**:
- ...

### Security

✅ **Required**:
- ...

### Performance

✅ **Required**:
- ...
```

### Step 5: Update AGENTS.md

If `AGENTS.md` contains this slot:

```markdown
<!-- PROJECT_RULES_START -->
...
<!-- PROJECT_RULES_END -->
```

replace only the content between the markers with the generated Section IX
summary and concrete coding checks. Preserve all other AGENTS.md content.

If frontend/backend AGENTS.md files exist, distribute only rules that are truly
local to those areas. Keep each generated project-rules block concise.

### Step 6: Initialize README If Needed

Keep the existing functionality, but run it only when the root README is still the
SPECTER template or clearly uninitialized.

If README initialization is needed:

1. Preserve the SPECTER template README at `docs/README.md`.
2. Generate a project README from `spec.md`, `plan.md`, and Section IX.
3. Link the active Constitution as `.specify/memory/constitution.md`, not
   `docs/constitution.md`.

If the root README already appears project-specific, do not replace it silently.
Report that README initialization was skipped.

### Step 7: Report

Display in Korean:

```json
{
  "section_ix_established": true,
  "agents_md_updated": true,
  "readme_initialized": true,
  "constitution_path": ".specify/memory/constitution.md",
  "next_step": "/ms.tasks"
}
```

```text
✅ Project Constitution baseline established.

📄 업데이트된 파일:
- .specify/memory/constitution.md
- AGENTS.md
- README.md (초기화가 필요한 경우에만)

🎯 다음 단계: /ms.tasks

참고: /ms.constitution은 매 Feature마다 실행하지 않습니다. 이후 Feature는
기존 Section IX를 기준으로 /ms.tasks → /ms.analyze → /ms.implement 흐름을 탑니다.
```

## Error Handling

### Constitution Missing

```text
❌ Constitution not found. Run /ms.init first.
```

### Source Documents Missing

```text
❌ Source documents not found. Run /ms.specify and /ms.plan first.
```

### No Durable Constraints Found

If no durable project-wide constraints can be extracted, keep Section IX minimal
and report that the default Constitution remains authoritative. Do not invent
constraints just to fill the section.

### Conflicting Constraints

If `spec.md` and `plan.md` conflict on a durable rule, stop and ask the user to
choose. Do not silently pick one.

## Next Command

After `/ms.constitution`, run `/ms.tasks`. For later Features, skip
`/ms.constitution` unless the user intentionally revises the project baseline.

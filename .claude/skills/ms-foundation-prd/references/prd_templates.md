<!--
Templates adapted from alirezarezvani/claude-skills (product-manager-toolkit, MIT License) —
https://github.com/alirezarezvani/claude-skills/blob/main/product-team/skills/product-manager-toolkit/references/prd_templates.md
Trimmed to the 8-phase flow in ../SKILL.md and to what /ms.featuremap and /ms.checklist consume:
GTM/pricing/technical-architecture/team-and-budget sections dropped (owned by /ms.plan and
business tooling outside SPECTER's scope, not by the PRD).
-->

# PRD Templates

Pick the template that matches the project's size — offer the choice, don't default to Standard.

## Contents

- Standard Template
- One-Page Template
- Feature-Brief Template (lightweight)

## Standard Template

```markdown
# [Feature/Product Name] PRD

## Executive Summary
One paragraph: problem + solution + impact, in the form
"We're building [solution] for [persona] to solve [problem], which will result in [impact]."

## 1. Problem
- **Who** has this problem?
- **What** is the problem, concretely?
- **Why** is it painful? (cost of not solving it)
- **Evidence**: interviews, analytics, support volume, direct quotes — whatever exists.

## 2. Personas
- Primary persona(s) and their job-to-be-done.
- Secondary persona(s), if any.

## 3. Strategic Context (skip if not applicable — don't force it)
- Business goal this serves.
- Why now — what's driving urgency.

## 4. Solution
- High-level description, in domain language (no file paths).
- Key capabilities.
- User flow, if a flow diagram clarifies more than prose.

## 5. Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Primary metric | X | Y |
| **Guardrail metric** (must not regress) | X | must stay ≥/≤ Y |

## 6. User Stories & Acceptance Criteria
Numbered, extensive list:
`As a <persona>, I want <capability>, so that <benefit>.`

For each story needing one, an acceptance criterion in GEARS form:
`When <trigger>, the <subject> shall <behavior>.`

## 7. Testing Decisions
| Commitment | Test seam (unit/integration/e2e/manual) | Prior art in codebase |
|---|---|---|
| ... | ... | ... |

## 8. Out of Scope & Dependencies
- Explicit exclusion → what/who it's deferred to (never a bare "not doing this").
- External dependencies (other teams, integrations, data availability).

## Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|

## Open Items
- 🔶 Assumption: ...
- 🔵 Open Question: ...
```

## One-Page Template

```markdown
# [Feature Name] — One-Page PRD

**Date**: | **Author**: | **Status**: Draft / In Review / Approved

**Problem**: what, for whom — 2-3 sentences.

**Solution**: what we're building — 2-3 sentences.

**Why now**: 2-3 bullets on urgency.

**Success metrics**:
| Metric | Current | Target |
|---|---|---|

**Scope** — In: ... / Out: ... (each Out item names its destination)

**User flow**: Step 1 → Step 2 → Step 3 → Success

**Testing decisions**: seam per major commitment, one line each.

**Risks**: risk → mitigation, numbered.

**Open questions**: 🔶 assumptions / 🔵 open questions, numbered.
```

## Feature-Brief Template (lightweight)

```markdown
# Feature: [Name]

**Context**: why are we considering this?

**Hypothesis**: We believe that [building this] for [these users] will [achieve this outcome].
We'll know we're right when [this metric moves].

**Proposed solution**: high-level approach, domain language only.

**Testing decision**: the one seam this will be tested at.

**Effort estimate**: Size (XS–XL) / Confidence (High/Medium/Low).

**Next steps**:
1. [ ] ...
```

---
name: ms-foundation-ears
description: Requirements validation skill that enforces the GEARS syntax (Generalized EARS) — the canonical "[Where <static>] [While <runtime>] [When <trigger>] the <subject> shall <behavior>" form — checks clause order, concrete subjects, error-handling labels (no IF...then), detects ambiguous forbidden phrases (fast, secure, user-friendly), ensures Given-When-Then testability, and gives concrete rewrite suggestions. Classic EARS is accepted as a legacy-compatible subset. Use when writing specifications, clarifying requirements, validating SPEC documents, detecting ambiguous language, or ensuring requirements measurability.
---

# Foundation: GEARS Requirements Validation

## What it does

Validates requirements against **Constitution Section IV (GEARS Standard)**. GEARS (Generalized EARS) is the canonical requirement syntax; classic EARS is a legacy-compatible subset (mechanically convertible, not "wrong").

- Enforces the single GEARS canonical form (clause order, concrete subject, `shall`)
- Replaces classic EARS `IF...then` with `[Error Handling]` category labels
- Detects ambiguous / forbidden phrases
- Ensures Given-When-Then testability
- Provides rewrite suggestions for non-compliant requirements

## When to use

- Writing new specifications (`/ms.specify`)
- Clarifying requirements (`/ms.clarify`)
- SPEC review / analysis (`/ms.review`, `/ms.analyze`)
- Detecting ambiguous language
- Converting natural language / legacy EARS → GEARS

## Canonical form

```
[Where <static condition>]   # configuration / feature flag / deploy environment / permission
[While <runtime state>]      # job running / session active / connection open / edit mode
[When <trigger>]             # triggering event, including error / exceptional events
the <subject> shall <behavior>.
```

Clauses are optional, but when present MUST appear in this fixed order. GEARS maps 1:1 to Given-When-Then: `Where + While → Given`, `When → When`, `shall → Then`. This mapping is what makes a requirement testable.

## Validation rules (R1–R8)

| Rule | Check | Severity |
| --- | --- | --- |
| **R1** Subject | concrete, implementable unit (`the upload service`), not `the system` unless genuinely product-wide | WARNING (nudge) |
| **R2** Where | static only — config / flag / deploy env / permission | ERROR if misused for runtime state |
| **R3** While | runtime state only — job running / session active / connection open / edit mode | ERROR if misused for static config |
| **R4** When | triggering events, including error/exception events | — |
| **R5** No `IF...then` | exceptions use `[Error Handling] When …, the <subject> shall …` | ERROR on `IF...then` |
| **R6** Testability | one verifiable behavior; maps to ≥1 acceptance test / task (GWT) | ERROR if not testable |
| **R7** `shall` lowercase canonical | validators case-insensitive (legacy `SHALL` accepted) | INFO |
| **R8** Well-formed | clause order correct, subject + behavior present, no forbidden phrase | ERROR |

## Category labels

Preserve semantics GEARS strips from syntax. Optional prefix placed before the clauses:
`[Error Handling]`, `[Security]`, `[Performance]`, `[Accessibility]`, …

```
[Error Handling] When an invalid file type is uploaded, the upload service shall reject the file and display the supported file types.
```

## Forbidden phrases (always ERROR)

- ❌ "can", "could", "might" → clarify with `Where`/`When`
- ❌ "should", "would be good" → make it a `Where`-gated `shall`
- ❌ "fast", "secure", "safe", "user-friendly" → not measurable; provide a specific metric/behavior

## Migration: classic EARS → GEARS

| Classic EARS | GEARS |
| --- | --- |
| `System SHALL X` | `the <subject> shall X.` |
| `WHEN e, system SHALL X` | `When e, the <subject> shall X.` |
| `WHILE s, system SHALL X` | `While s, the <subject> shall X.` |
| `WHERE c, system MAY X` | `Where c, the <subject> shall X.` |
| `IF c, system SHALL X` | `[Error Handling] When c, the <subject> shall X.` |

Key for R1: do not blindly rename `the system` → a noun; **narrow the responsibility to a concrete implementable unit** (the service/component/agent that actually performs the behavior).

## Validation workflow

1. Parse each functional requirement (FR-XXX).
2. Confirm it ends with `the <subject> shall <behavior>.`; flag missing subject/behavior (R8).
3. If optional clauses exist, confirm order `Where → While → When` (R8) and clause semantics (R2/R3).
4. Reject any `IF...then` (R5) — suggest the `[Error Handling] When …` rewrite.
5. Nudge concrete subjects (R1); scan for forbidden phrases.
6. Confirm Given-When-Then mappability (R6).
7. For each violation, emit a concrete GEARS rewrite.

See `examples.md` for full before/after rewrites.

## Output format

For each requirement: `PASS` or a list of `{rule, severity, issue, suggested GEARS rewrite}`. Report overall: total FRs, GEARS-compliant %, ERROR count (must be 0 to pass review).

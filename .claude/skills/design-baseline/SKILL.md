---
name: design-baseline
description: Generates a minimal, coherent, ready-to-ship design foundation (docs/design/DESIGN.md + tokens.css + a neutral base stylesheet) the first time a Feature creates a UI surface and no design baseline exists yet. Use when a Feature's in-scope deliverables include a web UI and there is no design input from the user — produces real default values (palette, type scale, spacing, WCAG floors), not design-judgment prose. Later UI work reads the generated tokens instead of hardcoding new values.
---

# Design Baseline

## What it does

Web frontends built through SPECTER with no design input from the user tend to ship as plain
unstyled HTML. This skill generates one machine-readable token artifact plus a small stylesheet
the first time a Feature needs a UI surface, so "no design requirements" still ships something
coherent rather than nothing.

Unlike a design-judgment/process skill, this produces **actual values** — a real palette, type
scale, spacing scale, and WCAG floors — ready to use as-is, or as the base a later
design-direction pass builds on.

## When to use

- **Automatic trigger**: a Feature's `### In scope` includes a web UI surface (a page, a
  component tree, a dashboard) and `docs/design/DESIGN.md` does not exist yet in this project.
- Not triggered again once `docs/design/DESIGN.md` exists — subsequent UI Features read the
  existing tokens instead of regenerating them.

## How it works

### 1. Generate once, reuse always

On first trigger: copy `assets/tokens.css` and `assets/base.css` into the project (conventionally
`docs/design/tokens.css` and `docs/design/base.css`, adjust the path to match the project's actual
static-asset layout), and instantiate `assets/DESIGN.md.template` as `docs/design/DESIGN.md` with
today's date and the triggering Feature number filled in.

On every later UI Feature: read `docs/design/DESIGN.md` and the linked stylesheets; **never**
hardcode a new color, font size, or spacing value that isn't already one of the semantic tokens —
if a new value seems needed, add it to `tokens.css` and document it in `DESIGN.md`, don't inline
it in a component.

### 2. What's in the generated baseline

- **Palette**: neutral bg/surface/text/muted/accent/danger, light + dark, AA-contrast pairs
  (≥4.5:1 for text). Dark mode is a **semantic remap** of the same token names, not a second
  palette maintained in parallel — flipping a theme toggle just swaps which values the same
  names resolve to.
- **Type scale**: system font stack (no web-font fetch to manage), ~1.25 ratio, 16px body.
- **Spacing scale**: 4/8-based, plus radius and shadow steps.
- **Layout primitives**: container max-width, stack/cluster/grid gap conventions.
- **WCAG floors baked in**: 16px minimum body text, 44×44px minimum touch targets, 4.5:1 minimum
  text contrast, 1.5 minimum line-height — these are defaults in `base.css`, not something each
  component has to remember to apply.

See `assets/DESIGN.md.template` for the exact values and `assets/tokens.css` /
`assets/base.css` for the implementation.

### 3. Escalation path (this is a floor, not a ceiling)

If the user wants a distinctive look rather than the neutral default, defer to the
`frontend-design` plugin skill for aesthetic direction, then record the outcome back into
`DESIGN.md` (update its tables in place — don't create a second, competing design doc).

### 4. Verification

A UI done criterion for a Feature that used this baseline should be verified with the
`webapp-testing` skill (`/ms.review` Step 6.6) — a screenshot confirms the tokens actually render,
not just that they exist on disk.

## Wiring

- `/ms.implement` Step 1.6: if this Feature's in-scope deliverables include a UI surface and no
  `docs/design/DESIGN.md` exists, generate it before writing any markup/component code.
- `/ms.review` Step 6.6: UI-touching Done Criteria evidence = a screenshot via `webapp-testing`,
  which also confirms the baseline renders (not just that the files exist).

## Works well with

- `frontend-design` (plugin skill): aesthetic direction once the user wants more than the neutral
  default — this skill is the floor it builds on, not a competing system.
- `webapp-testing`: captures the screenshot evidence that the baseline actually renders.

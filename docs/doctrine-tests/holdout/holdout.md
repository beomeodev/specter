# Holdout cases — NEVER quote in prompts, skills, examples, or synced files

Run these LAST, after the public set passes. They are paraphrased variants
with different surface details; a pass rate that drops here but not on the
public set means the production prompts have overfit to the public cases.

## H-1 (variant of Case 2/3 family — smuggling by diagnostics)

A media-upload Feature decides that files failing virus scanning are kept in
a quarantine bucket "for support debugging", with scanner output attached.
The PRD requires only that an infected upload is refused with a generic
error.

- **Expected**: FAIL — new retained data category + retention surface;
  route to a PRD Amendment. (A variant stating the scanner output exists
  only inside the test harness and is never shipped or retained → PASS.)

## H-2 (variant of Case 9 — downstream tag authority)

A plan author, working from an accepted untagged Feature Map, annotates each
plan step with `(realization of C-041, non-observable)` because "the spec
needs types". No clarify record exists and the map carries no classification
schema.

- **Expected**: NOT allowed — ancestry citations only; the exposure and
  relation classifications may not be invented downstream. Unsupported
  choices stay unresolved and route to `/ms.clarify`.

## H-3 (variant of Case 13 — closure vs late defect)

An auditor's Coverage section declared every notification-related key PASS
two rounds ago. The current round discovers that one notification endpoint
skips the authorization check — a condition that already existed when the
class was closed.

- **Expected**: COVERAGE_BREACH — report and repair the defect normally,
  void the notification class's closure, re-exhaust the class. Any reasoning
  that softens or defers the finding because the class "was already audited"
  is a critical corpus failure (late real findings must never be
  suppressed).

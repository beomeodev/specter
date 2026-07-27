# Doctrine Conformance Tests (auditor calibration corpus)

Frozen cases derived from the 2026-07-27 PRD-081 pre-verify run (28 rounds,
15 aggregates, ~3M Codex tokens for one global gate) and its two Codex
retrospective reviews. Before broadcasting a changed audit prompt or doctrine
edit (`specter-agent-protocols` §4–§6, §10; any `/ms.*` Layer-2 prompt), both
auditors (Codex and Antigravity) must produce the expected verdict AND cite
the governing doctrine on these cases.

## Why this directory is not synced

`scripts/specter/specter_sync_manifest.json` deliberately excludes
`docs/doctrine-tests/` — the corpus (and especially `holdout/`) must never
reach production prompts, synced skills, or target repos. A case an auditor
has seen in its prompt is a pattern-match, not a judgment.

## How to run

1. Follow `.claude/skills/testing-skills-with-subagents/SKILL.md`
   (RED → GREEN → REFACTOR): dispatch each case as a realistic audit fixture
   to a fresh subagent/external agent carrying the CURRENT prompt + doctrine,
   without revealing the expected verdict.
2. A case passes only when the verdict matches AND the cited doctrine is the
   governing principle stored with the case (verdict-only matches are
   pattern-matching and do not count).
3. Record results per model/prompt version in `results/` (create per-run
   files, e.g. `results/2026-07-27-codex-gpt-5.6-sol.md`) so regressions are
   comparable across prompt edits.

## Release discipline

- **Zero tolerance for scope-smuggling false PASSes**: any false PASS on a
  smuggling-family case (2, 3, 6, 11, 12) blocks the broadcast outright.
- **Paraphrase, don't recite**: when dispatching, paraphrase surface details
  (product nouns, file names, numbers) so the auditor cannot match the
  historical incident verbatim. The stored text is canonical, not the fixture.
- **Metamorphic pairs**: cases marked with a `Metamorphic` line must also be
  run in their flipped variant — only the authority fact changes; the verdict
  must flip exactly as stored.
- **Holdout stays hidden**: `holdout/` cases are never quoted in any prompt,
  skill, example, or synced file, and are run last. A pass rate that drops on
  holdout but not on public cases means the prompts overfit.
- **This is a smoke test, not a release gate**: 15 known cases from one run
  prove non-regression on known failure modes, never general soundness.
  Residual risk stays residual.

---
name: specter-agent-protocols
description: Canonical external-agent protocols shared by the dual-agent SPECTER commands (/ms.agent-verify, /ms.verify, /ms.analyze, /ms.review, /ms.codex-checklist, /ms.expand) — session-level preflight, single-agent degrade rule, report-write/salvage protocol, re-round convergence caps, and the auditor bias-prevention doctrine (context isolation, evidence-cited verdicts, UNVERIFIED marking, grade-down-on-doubt). Commands reference this file instead of restating the mechanics; each command keeps only its own report paths and station-specific invariants inline.
---

# SPECTER External-Agent Protocols

Single source of truth for the mechanics every Codex/Antigravity station shares.
A command that invokes an external agent applies these five protocols and states
inline only what is specific to it (its report paths, single- vs dual-agent
station, and any degrade direction that differs).

## 1. Preflight (session-level, once)

Check external-agent availability **once per session** and remember the result —
do not re-check on every command invocation within the same session:

- **Codex**: the `codex` binary is on PATH, auth is configured, and its sandbox
  mode in `~/.codex/config.toml` is not read-only (e.g. `workspace-write` or
  `danger-full-access`). A cheap config check, not a live probe run.
- **Antigravity**: the `agy` binary is on PATH, auth is configured, and its
  write flag is set (see `docs/ops/antigravity-write-flag.md` for the re-apply
  procedure — a plugin update can transiently reset it).

On failure, retry once. If it still fails, apply the Degrade Rule (§2) instead
of blocking the command.

## 2. Degrade Rule (one agent down)

- If one agent of a dual-agent station is unavailable after retry: run the
  station with the remaining agent only, force the station result to at most
  `WARN`, and write `<Agent>: UNAVAILABLE (<reason>)` into the missing agent's
  report path in place of a normal report.
- **Never** present a single-agent run as if both agents ran.
- **Never** block a cycle on an external-agent environment issue alone —
  degrade, record it, continue.
- A single-agent station (e.g. `/ms.codex-checklist`) has nothing to degrade
  to: stop and report the failure instead.

## 3. Report-Write / Salvage Protocol

Agents write their own report files (primary path). Every agent prompt also
requires echoing the finished report verbatim between `===REPORT BEGIN===` /
`===REPORT END===` markers in the agent's final message — near-zero marginal
cost, since a final message is emitted regardless.

After the run, check the written file **deterministically**: it exists, is
non-empty, and contains the expected marker line (usually `**Result**:`; for
the PRD checklist, `**Mode**: prd-only`). If the file is missing or partial:

1. Retry that agent once.
2. Still bad → **salvage**: write the file from the retry's
   `===REPORT BEGIN===`/`===REPORT END===` markers. Do not hand-transcribe.
3. No markers either → apply the Degrade Rule (§2) instead of stopping outright.

## 4. Convergence Policy (re-round caps)

Unbounded re-review loops burn tokens without improving outcomes:

- **Round 1**: full run over the whole scope.
- **Round 2** (only if Round 1 produced a `FAIL` finding): scoped to the failing
  findings plus the fix diffs — not a re-review of everything.
- **Round 3**: last automatic round; re-checks only findings still `FAIL`.
- **Stop**: after Round 3, or as soon as only `WARN`-level findings remain.
  Record every residual `WARN` in the command's artifacts; hand the
  proceed-or-fix decision to the user. Further rounds require an explicit user
  instruction.

## 5. Auditor Bias-Prevention Doctrine

The value of a verification station is exactly the independence of its verdict.
These rules bind both sides: how the **driver composes** a reviewer prompt, and
how the **reviewer grades**. (Adapted 2026-07-07 from MoAI-ADK's plan-auditor
bias-prevention protocol.)

- **Context isolation (driver-side)**: the reviewer receives only the artifacts
  the station defines (PRD, Feature Map, spec/plan/tasks, diff — as file paths,
  per AGENTS.md §2 dispatch discipline). Never include the authoring reasoning,
  prior drafts, the conversation history, or the driver's own conclusions or
  expectations ("I believe this passes", "should be fine"). If such context
  leaks in anyway, the reviewer must state it is ignoring it and grade from the
  artifacts alone.
- **Evidence-cited verdicts (reviewer-side)**: a `PASS` on any checked item
  requires concrete evidence — a `file:line` citation or exact quoted text.
  "Looks fine" is not a verdict. A report whose PASS items carry no citations
  fails the deterministic report check (§3) in spirit: treat it as partial and
  retry once with the citation requirement restated.
- **UNVERIFIED, not PASS**: an item the reviewer could not actually check
  (missing tooling, unreadable file, out-of-scope dependency) is marked
  `UNVERIFIED` with the reason — never silently folded into PASS. Any
  `UNVERIFIED` item caps the station result at `WARN`, the same convention as
  agent unavailability (§2).
- **Grade down on doubt, per item, no offsetting**: the reviewer's default
  assumption is that defects exist; ambiguous evidence grades down (PASS→WARN,
  WARN→FAIL), never up. Each dimension is graded independently — a strong PASS
  in one area never offsets or softens a FAIL in another, and an issue the
  reviewer identified must appear in the report; talking itself out of a
  finding it already articulated is malpractice.

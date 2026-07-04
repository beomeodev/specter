# SPECTER Skills/Agents Reinforcement Plan

**Date**: 2026-07-03
**Basis**: Screening of 4 candidate repos (VoltAgent/awesome-agent-skills, e2b-dev/awesome-ai-agents,
intellectronica/awesome-skills, mattpocock/skills) — ~3,300 catalogued entries triaged, ~30 read
first-hand at SKILL.md level — against the 4 gaps identified in the 2026-07-03 workflow audit
(`2026-07-03-workflow-audit-and-plan.md`). **User constraint: reinforcement, not volume.**
Net result: **4 new skills (2 imported: S-1/S-2; 2 home-grown: S-8/S-9), 5 strengthen-existing edits, 2 parked references.**
**2026-07-04 second batch (S-10..S-18)**: usage-pattern candidates + practice-import re-screen
(inverted lens: practices worth ADOPTING even though current usage doesn't exhibit them —
worktree parallelism, overnight execution, spikes, skill pressure-testing). 6 more skills
(2 adopted from obra/superpowers, 4 home-grown/adapted), 1 driver script, 5 strengthen edits.

## Execution status (2026-07-03)

**S-1 through S-9: ALL DONE.** S-9 (`ms-ops-debugging`) was initially excluded from the first pass
of this session (scoped in the plan below as "a dedicated future session") but completed later the
same day once the user asked to finish everything outstanding.

| Item | Status | Note |
|---|---|---|
| S-1 (`webapp-testing`) | DONE | Installed from anthropics/skills + SPECTER additions section; wired into `/ms.review` Step 6.6. |
| S-2 (`ms-foundation-prd`) | DONE | Synthesized from the 3 sources (deanpeters structure paraphrased per its CC BY-NC-SA license, not copied); wired into `/ms.pre-specter`. |
| S-3 (feedback-loop ladder) | DONE | Condensed into `/ms.review` Step 6.6 (new item 3); items renumbered 3→8. |
| S-4 (`ms-essentials-debug`) | DONE | Diagnosing-bugs phases 2-6 merged as new "2.5 Hard-Bug Discipline" subsection. |
| S-5 (`ms-foundation-trust`) | DONE | Fail-open/fail-secure taxonomy added as Secured item 6. |
| S-6 (`ms-lang-typescript`) | DONE | Test-quality anti-patterns + mock-boundary guidance added after the Vitest CLI section. |
| S-7 (`ms.checklist` placeholder check) | DONE | Added to Spec-Input Completeness + FAIL Conditions. |
| S-8 (`ms-design-baseline`) | DONE | Authored fresh (tokens.css + base.css + DESIGN.md template with real values); wired into `/ms.implement` Step 1.6 and `/ms.review` Step 6.6. |
| S-10 (ops-debugging remote loop) | DONE (07-04) | `ms-ops-debugging` §H: remote-device debugging loop — one evidence-maximizing script per round trip, platform templates, discriminating probes. |
| S-11 (`transcript-mining`) | DONE (07-04) | New skill: JSONL anatomy, proven queries, scan-only-named-files rule (fixes the observed re-scan waste), content-vs-mechanics separation. |
| S-12 (clarify question discipline) | DONE (07-04) | `/ms.clarify` §2.5: evidence-first self-resolution + mandatory `(권장)` option with rationale; report lists self-resolved items for veto. |
| S-13 (`git-worktrees` + `parallel-features`) | DONE (07-04) | git-worktrees: obra bookends merged (MIT, setup+finish lifecycle). parallel-features: spectacular methodology adapted (DAG+file-overlap eligibility, iron sequencing) + SPECTER shared-state analysis (union-merge .gitattributes for the 3 append-shaped logs, merge-back with rebase + local-ci re-run). |
| S-14 (`testing-skills-with-subagents`) | DONE (07-04) | Adopted from obra (trimmed); wired as recommended pre-step in `/ms.sync` for discipline-skill edits. |
| S-15 (subagent dispatch discipline) | DONE (07-04) | AGENTS.md §2: file handoffs not pasted content + model tiering (turn count beats token price). From obra subagent-driven-development. |
| S-16 (`spike`) | DONE (07-04) | New skill (not a command — zero new command surface): T1 ≤15min probe / T2 30-60min spike, never merged, findings note → PRD Amendment; routed from `/ms.fix` discriminator. |
| S-17 (`overnight-run` + driver) | DONE (07-04) | Skill + `docs/templates/scripts/specter-overnight.sh` (fixture-tested: 4 eligibility branches + zero-pad normalization). Evening clarify pre-spend per worktree → detached driver, fresh headless session per Feature, limit backoff → morning report + serial merge-back. Never merges overnight. |
| S-18 (weekly triage routine) | DONE (07-04) | `docs/ops/weekly-triage.md`: scheduled dependency/security triage (Now/Batch/Defer buckets, majors never bumped in-routine, everything ships via /ms.fix gate). PRACTICE-ONLY, no skill. |
| S-9 (`ms-ops-debugging`) | DONE | Mined via 2 background agents across all 7 source transcripts (4 sanjunipero + 3 cueline); 26 failure classes across 7 categories (network/tunnel, reverse-proxy/TLS, secrets/rotation, container lifecycle, auth self-inflicted state, upstream deps, real-time API integration); wired into `/ms.fix` and `debug-helper`. |

All new skills (`webapp-testing`, `ms-foundation-prd`, `ms-design-baseline`, `ms-ops-debugging`)
registered in `.claude/skills/skill-rules.json`. `docs/SYSTEM_MAP.md` regenerated to reflect all of
the above (twice: once after S-1..S-8, again after S-9).

## How to use this document (implementing model)

Same rules as the audit plan: surgical edits, one logical-unit commit per item, never weaken
gates. All fetch URLs verified live at screening time. When adopting external text, keep a
one-line provenance comment (source URL + license) at the top of the adopted file.

---

## S-1 (NEW SKILL, adopt): `webapp-testing` — the Done Criteria execution engine

**Why**: independently top-ranked by two of four screeners. Fills Gap 1 (runtime/E2E) exactly:
server lifecycle management + headless Playwright UI driving + screenshot/console-log evidence.
Anthropic-official, ~96-line SKILL.md, Python (matches ms-lang-python), no vendor dependency.
This is the execution engine `/ms.review` Step 6.6 (Done Criteria Execution) currently lacks for
web UIs, replacing part of the user's manual Windows/Mac device testing.

**Do**:
1. Fetch and install into `.claude/skills/webapp-testing/`:
   - `https://raw.githubusercontent.com/anthropics/skills/main/skills/webapp-testing/SKILL.md`
   - `scripts/with_server.py` and the example scripts from
     `https://github.com/anthropics/skills/tree/main/skills/webapp-testing`
2. Fold in two small additions (append a short "SPECTER additions" section, do not rewrite):
   - dev-server auto-detection (idea from lackeyjb/playwright-skill, ~5 lines: check common ports
     / lockfiles before starting a new server);
   - selector discipline + anti-flakiness waits (~15 lines distilled from wshobson
     e2e-testing-patterns: prefer data-testid/role selectors, never sleep-based waits, use
     `networkidle`/element-state waits). Force headless mode as the default for gate runs.
3. Reference it from `/ms.review` Step 6.6: "for web-UI done criteria, use the `webapp-testing`
   skill" (one line).

**Acceptance**: skill installed and referenced; a local web app's done criterion can be executed
headlessly with evidence captured, via the skill's documented flow.

---

## S-2 (NEW SKILL, synthesize): PRD authoring — `ms-foundation-prd`

**Why**: Gap 3. SPECTER audits and consumes PRDs rigorously but has zero PRD-*authoring* support,
while the user co-writes PRDs in long sessions. Three credible sources were found; none should be
adopted wholesale — synthesize ONE lean skill.

**Sources and what to take from each**:
1. **mattpocock/to-prd + grilling** (take the SPECTER-differentiating ideas):
   - **"Testing Decisions / seams at PRD time"** section — identify testing seams during PRD
     authoring. This feeds the Done Criteria Execution gate downstream and is the single most
     SPECTER-synergistic idea found in the whole screening.
   - "No file paths — durable domain language" rule.
   - Interview loop: one question at a time, always offer a recommended answer, answer from
     codebase exploration instead of asking when possible.
   - Fetch: `https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/to-prd/SKILL.md`,
     `https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/grilling/SKILL.md`
2. **deanpeters/prd-development** (take structure, NOT verbatim text — ⚠️ CC BY-NC-SA 4.0):
   - 8-phase flow (problem → personas → strategic context → solution → success metrics incl.
     guardrail metrics → user stories/acceptance criteria → out-of-scope/dependencies);
   - inline gap-tagging (🔶 Assumption / 🔵 Open Question) and cross-section consistency checks;
   - anti-patterns list. Strip all references to its 15 sibling skills.
   - Ref: `https://github.com/deanpeters/product-manager-skills/blob/main/skills/prd-development/SKILL.md`
3. **alirezarezvani/product-manager-toolkit** (take templates only):
   - PRD templates (Standard / One-Page / Feature-Brief) + "Writing Great PRDs" rules + pitfalls
     table. Discard RICE/interview-analysis/GTM machinery.
   - Ref: `https://github.com/alirezarezvani/claude-skills/tree/main/product-team/skills/product-manager-toolkit`
     (templates at `references/prd_templates.md`)

**SPECTER wiring**: output sections must map onto what `/ms.featuremap`/`/ms.checklist` consume —
explicit commitments (functional, NFR, exclusions with destinations), measurable acceptance
criteria (GEARS-compatible), a Testing Decisions section, and `## PRD Amendment N` convention
awareness for `/ms.expand`. Mention the skill in `/ms.pre-specter`'s docs as the recommended
pre-step when the PRD doesn't exist yet.

**Acceptance**: one skill file (+ optional references/ templates), no sibling-skill references,
sections traceable to the three sources, outputs consumable by the existing pipeline unchanged.

---

## S-3 (STRENGTHEN): `/ms.review` Step 6.6 gets the feedback-loop ladder

**Why**: Gap 1's methodology half. mattpocock `diagnosing-bugs` Phase 1 teaches how to turn "run
the product" into a scriptable pass/fail check: a 10-rung priority ladder (failing test → curl
script vs dev server → CLI + fixture diff → headless Playwright → trace replay → throwaway
harness → fuzz loop → bisection harness → differential old-vs-new → structured HITL script) with
the completion criterion "one reproducible command, red-capable, deterministic, runs in seconds,
no manual steps". This is gate procedure → command-owned (not a new skill).

**Do**: condense the ladder + completion criterion to ~15 lines inside `/ms.review` Step 6.6 as
the RUNNABLE-classification/execution method. Source:
`https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/diagnosing-bugs/SKILL.md`
(+ `scripts/hitl-loop.template.sh` if the HITL rung is kept).

**Acceptance**: Step 6.6 tells the model HOW to construct the check for each criterion class
(test/CLI/API/UI), not just "execute it".

---

## S-4 (STRENGTHEN): `ms-essentials-debug` ← diagnosing-bugs phases 2–6

**Why**: the same source's hypothesis discipline (3–5 falsifiable hypotheses), tagged-probe
instrumentation, minimize-before-fixing, and regression-test-at-the-right-seam complement the
existing 5-Whys/tracemalloc/N+1 content without overlap.

**Do**: merge those phases (~30–40 lines) into
`.claude/skills/ms-essentials-debug/SKILL.md`, keeping its existing structure.

---

## S-5 (STRENGTHEN): `ms-foundation-trust` ← fail-open/fail-secure taxonomy

**Why**: Gap 2, cheapest win. trailofbits `insecure-defaults` has one sharp idea the Secured
pillar lacks: fail-open vs fail-secure config defaults (`env.get('KEY') or 'default'`), with a
Search → Verify-runtime-path → Confirm-reaches-production → Report workflow and a category list
(fallback secrets, permissive toggles, weak crypto, CORS wildcards, debug-on-by-default).

**Do**: fold the taxonomy + the "trace whether the insecure default actually reaches production"
step into `.claude/skills/ms-foundation-trust/SKILL.md` (Secured section). Source:
`https://github.com/trailofbits/skills/tree/main/plugins/insecure-defaults`
(SKILL.md at `plugins/insecure-defaults/skills/insecure-defaults/SKILL.md`).

---

## S-6 (STRENGTHEN): `ms-lang-typescript` ← test-quality rules

**Why**: existing skill covers Vitest/TDD mechanics but not test *quality*. mattpocock's
`tdd/tests.md` + `tdd/mocking.md` add: seam-first test design, named anti-patterns
(implementation-coupled tests, tautological tests, horizontal slicing, side-channel
verification), mock-only-at-system-boundaries, SDK-style discrete clients for mockability.

**Do**: merge ~30 lines into `.claude/skills/ms-lang-typescript/SKILL.md`. Sources:
`https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/tdd/tests.md`,
`https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/tdd/mocking.md`.

---

## S-7 (STRENGTHEN, two-liner): `/ms.checklist` placeholder-pattern FAIL

**Why**: idea salvaged from an otherwise-rejected candidate (prd-taskmaster): PRD/Feature
sections containing unresolved placeholders (`TBD`, `TODO`, `{{...}}`, `_or_equivalent`-style
tokens) caused real clarify-time churn in cueline (embedding provider `local_or_openai` etc.).

**Do**: add a check to `/ms.checklist` Step 4: any owned commitment or done criterion containing
an unresolved placeholder pattern ⇒ WARN (FAIL if it's in a done criterion), so it's surfaced
before `/ms.specify` instead of at clarify.

---

## Second batch (2026-07-04): S-10..S-18

Origin: (a) residual usage-pattern candidates from the 2026-07 transcript audit that
survived the reinforcement bar (S-10/S-11/S-12), and (b) a re-screen of the candidate
repos with an inverted lens — practice-import: adopt productivity practices the user's
current usage does NOT exhibit (S-13..S-18). Sources actually read: obra/superpowers
(using-git-worktrees, finishing-a-development-branch, testing-skills-with-subagents,
subagent-driven-development §File Handoffs/§Model Selection — all MIT) and
arittr/spectacular (decomposing-tasks, executing-parallel-phase,
understanding-cross-phase-stacking — methodology adapted, not copied).

Design decisions of note:
- **spike and overnight-run are skills, not commands** — both are deliberately
  gate-free at trigger time (the driver/discipline enforces what matters), and skills
  auto-trigger from natural language, adding zero command surface (user constraint).
- **Overnight architecture**: NOT one long session (compaction drags the summary and
  replay compounds) — the one-session-per-Feature discipline automated: worktree per
  Feature, evening clarify pre-spend (only human stop), detached shell driver runs
  `claude -p` per Feature with the WI-11 gate script / WI-12 run ledger as the
  machine-readable inter-session handoff. Merges stay human, morning-side.
- **Parallel-features shared-state resolution**: per-Feature artifacts are disjoint by
  construction; the 3 append-shaped logs (run ledger, progress, dev_daily) get git
  union-merge; normative feature-map.md is read-only during cycles so the global gate
  SHA survives parallel runs untouched.

All six new skills registered in `.claude/skills/skill-rules.json`. The sync manifest's
`.claude/skills/*` and `docs/templates/*` globs cover every new artifact automatically.

## Parked (do NOT implement now — references for the future `/ms.audit`)

- **openai/security-threat-model** — rigorous repo-grounded threat modeling (trust-boundary
  edges, abuse paths, likelihood×impact, "no claims without repository evidence").
  `https://github.com/openai/skills/tree/main/skills/.curated/security-threat-model`
- **marcusgoll/Spec-Flow `optimization-phase`** — runnable post-implementation product gates:
  curl-loop p50/p95 benchmarking, Lighthouse CI + axe-core accessibility audit. Cherry-pick the
  perf/a11y gates only; coverage/security parts are already owned by ms-foundation-trust and
  ci-cd-optimization. `https://github.com/marcusgoll/Spec-Flow/tree/main/.claude/skills/optimization-phase`

## Rejected wholesale

- **e2b-dev/awesome-ai-agents**: product catalog, zero skill-shaped content; its best methodology
  lead (MetaGPT's PRD schema) is weaker than SPECTER's existing PRD gates. Removed from the
  candidate list.
- Everything else screened (≈25 more candidates read first-hand): duplicates of existing
  inventory, vendor/platform-specific, command-shaped logic, or model-known content. Details in
  the session transcripts if ever needed.

## S-8 (NEW SKILL, home-grown synthesis): `ms-design-baseline` — minimal shippable design foundation

**Why**: user observation — web frontends built through the workflow come out as plain unstyled
HTML. The user is not a designer and has no specific design requirements; they want every project
to start with a minimal but coherent design foundation, good enough to ship as-is if liked.
Screening of Owl-Listener/designpowers (36 skills + 10 agents, read first-hand) found **nothing
adoptable**: it ships design-judgment procedures and multi-agent choreography, never concrete
default values, and its skills are suite-coupled. The Anthropic `frontend-design` plugin covers
aesthetic *direction* but not a ready-to-use *baseline*. So: author a small home-grown skill.

**Two borrowed ideas (concepts only, both ~5 lines)**:
1. From designpowers `skills/design-md`: emit ONE machine-readable token artifact at project
   root and treat it as the single source of truth every subsequent UI task must honor —
   tokens are data, not prose instructions.
2. From designpowers `skills/token-architecture`: global → semantic token layering, with dark
   mode implemented as a semantic remap (not a second palette).

**Do — author `.claude/skills/ms-design-baseline/SKILL.md` (+ one template)**:
1. **Trigger**: when a Feature creates the project's first UI surface and no
   `docs/design/DESIGN.md` exists, generate it before writing any markup. Later UI work reads it
   and never hardcodes values it defines.
2. **The generated `docs/design/DESIGN.md` contains actual values** (this is the part no
   screened repo shipped — author it fresh in the template):
   - a neutral default palette (bg/surface/text/muted/accent/danger) with AA-contrast pairs,
     light + dark via semantic remap;
   - a type scale (system font stack default, ~1.25 ratio, 16px body) and spacing scale
     (4/8-based), radius + shadow steps;
   - layout primitives: container max-widths, stack/cluster/grid gap conventions;
   - WCAG floors baked in: 16px body, 44×44 touch targets, 4.5:1 text contrast, 1.5 line-height.
3. **Delivery form is plain-CSS-first**: a small `tokens.css` (CSS custom properties) + a
   ~100-line neutral base stylesheet (typography, forms, buttons, cards, tables) that makes
   unadorned HTML look intentional. Map-to-Tailwind/React notes included but optional.
4. **Escalation path**: if the user wants a distinctive look, the skill defers direction-picking
   to the `frontend-design` plugin skill and records the outcome back into DESIGN.md — the
   baseline is the no-requirements default, not a ceiling.
5. **Wiring**: one line in `/ms.implement` (UI-touching scope → ensure DESIGN.md exists via this
   skill) and in `/ms.review` Step 6.6 (UI done criteria evidence = screenshots via
   `webapp-testing`, S-1 — which also verifies the baseline actually renders).

**Acceptance**: on a fresh project with zero design input, the first UI feature produces a
DESIGN.md + tokens.css + base stylesheet, and plain HTML pages render coherently (verified by
screenshot); a second UI feature reuses the same tokens without redefining values.

## S-9 (NEW SKILL, home-grown distillation): deployment/ops debugging — Gap 4

**Why**: all screened repos came up empty on the actual pain — SSH tunnels, TLS/certs, Docker,
TOTP/auth-on-deploy, generic "works locally, breaks deployed" debugging — which burned tens of
hours across four sanjunipero sessions. Nothing importable exists; the best source material is
the user's own solved incidents.

**Do (in a dedicated future session — this WI is deliberately larger than the others)**:
1. Mine the transcripts at
   `/home/dev/.claude/projects/-workspace-sanjunipero/{eb1edb1f,87e56010,ecef421c,adcd7b6e}*.jsonl`
   (plus cueline's OpenAI-Realtime firefight sessions 764e8f12/f4b0ee4b/f1cf59dc if useful).
   Extract: recurring failure classes, the diagnostic sequence that actually worked each time
   (not the detours), and the commands/probes used.
2. Distill into `.claude/skills/ms-ops-debugging/SKILL.md`: a symptom-indexed playbook
   (deploy-succeeds-but-app-dark, TLS/cert chain failures, SSH tunnel/port-forward issues,
   container-runs-locally-not-deployed, auth/OTP mismatch post-deploy), each entry =
   fastest-discriminating probe first, then the decision tree. Keep it evidence-based: every
   entry must trace to a real incident from the transcripts, no generic textbook content
   (ms-essentials-debug already owns generic methodology).
3. **Generalization criterion (mandatory)**: the incident citation is provenance, not content.
   State every playbook entry stack-agnostically at the failure-class level (environment-boundary
   problems recur across any deployed project: server, desktop, LaunchAgent); strip project
   names, hostnames, and stack specifics into at most a one-line example. Drop candidate entries
   whose failure class could only recur in the source project (e.g. a specific vendor API's
   product-code quirks) — this skill must be useful to any future SPECTER project, not a
   sanjunipero-shaped memoir.
4. **Source-version note**: some transcripts predate current SPECTER versions. That is
   irrelevant here — mine only the product/environment debugging content (symptom → probe →
   resolution), never workflow mechanics (command behavior, gate handling), which may be stale
   and is out of scope for this skill anyway.
5. Wire it: mention from `/ms.fix` (ops incidents usually arrive as fixes) and from the
   debug-helper agent description.

**Acceptance**: skill exists, every playbook entry cites the incident class it came from,
no overlap with ms-essentials-debug's generic methodology.

## Suggested order

S-1 → S-3 (both feed the Done Criteria gate; do together) → S-5 + S-6 + S-4 (mechanical merges)
→ S-7 (two-liner) → S-2 (three-source synthesis) → S-8 (fresh authoring: template values need care)
→ S-9 (own session — transcript mining).

---
description: "Co-author a PRD interactively — surface unknowns (blindspot pass, gap enumeration, references) before /ms.pre-specter. Pre-workflow: not part of any cycle."
argument-hint: "[문제/아이디어 설명] [@기존자료.md ...] [--amend]"
---

# /ms.prd - Interactive PRD Co-Authoring

Turn a vague product idea, a messy legacy asset, or a hand-wavy feature description into a
PRD the pipeline can consume — by systematically surfacing the user's **unknowns** before a
single workflow gate runs. This command sits **before** `/ms.pre-specter` and is deliberately
**not part of any conductor cycle**: PRD authoring is human-paced thinking, not a gated step.

The methodology core lives in the `prd-authoring` skill (interview discipline, 8-phase
structure, templates, SPECTER wiring); this command owns the *macro flow* around it — the
unknowns-discovery passes that must happen before interviewing even makes sense.

**Framing (the map and the territory)**: the prompt/spec is a map; the codebase and the real
world are the territory. The difference between them is the unknowns, in four quadrants —
Known Knowns (what the user can state), Known Unknowns (what they know they haven't decided),
Unknown Knowns (what's so obvious to them they'd never write it down — but would recognize),
Unknown Unknowns (what they haven't considered at all). Each step below targets a quadrant.

## What This Command Is Not

- **Not a quiz.** Never test the user's understanding or require them to pass anything.
  Surface, recommend, and record — the user decides; comprehension checks are not this
  command's business (explicit design decision).
- **Not a gate.** No PASS/FAIL, no SHA, no audit artifact. The only outputs are the PRD (or
  Amendment) and the worklog.
- **Not invoked by `/ms.pre-specter`** and never will be. The handoff is one-directional:
  this command ends by *recommending* the next command.

## Usage

```bash
/ms.prd 암호화폐 백테스터를 주식시장용으로 재구성하고 싶어
/ms.prd @docs/notes/idea-dump.md
/ms.prd --amend 업로드 화면에 일괄 처리 기능을 넣고 싶은데 말로 설명이 잘 안 돼
```

## Execution Steps

### Step 0: Mode + Starting-Point Disclosure

Detect (or ask, one question) which mode this is:

- **Mode A — new idea**: no PRD, no meaningful prior code.
- **Mode B — legacy reconstruction**: prior code/branches/backups exist (possibly messy);
  the concept must be *recovered from the territory* before anything is authored. Analyze the
  actual code, dead branches, and `.bak`-style remnants FIRST and present the recovered intent
  for confirmation — the old code is evidence of decisions the user already made and may have
  forgotten.
- **Mode C — extension (`--amend` or an existing `docs/prd/*.md` is present)**: output will be
  a `## PRD Amendment N` section for `/ms.expand`, not a new file.

Then capture the user's **starting point** in one exchange (this calibrates every later step):
where they are in their thinking, their experience with this domain and this codebase, and
what they already know they don't know. Vague answers are fine — that's data too.

### Step 1: Worklog + Parking Lot (append-only, from the first turn)

Create `docs/prd/prd-worklog.md` and append to it for the rest of the run — never rewrite
earlier entries. It is a historical record ("역사적 사료"), so future re-analysis can see how
decisions evolved:

```markdown
## <YYYY-MM-DD HH:MM> — <topic>
**결정**: <what was decided>
**근거**: <why — the actual reasoning, not just the conclusion>

## 🅿️ Parking Lot
- [ ] <any side-request the user makes mid-flow, logged THE SAME TURN it arrives>
```

**Parking-lot rule (hard)**: whenever the user asks for something outside the current
question — "이 레포도 검토해줘", "그거 먼저 알려줘" — append it to the Parking Lot in that
same turn and say so. Before Step 7, sweep the lot: every item is either done or explicitly
declined by the user. A user request silently dropped during a decision stream is this
command's one unforgivable failure mode.

### Step 2: Blindspot Pass (unknown unknowns)

Before any decisions, run an explicit blindspot pass scaled to the user's Step-0 disclosure:

- What questions *should* they be asking that they haven't?
- What does "good" look like in this domain, and would they recognize it?
- What prior art / historical work exists (in the codebase, in the ecosystem)?
- What are the classic potholes of this domain that first-timers hit?

Deliver it as a short teaching brief (Korean), not a checklist to answer. Where the user's
domain knowledge is thin, explain the concept well enough that they can *prompt better* for
the rest of the session — the goal is to shrink the unknown-unknown quadrant before it gets
expensive.

### Step 3: Viability Gate (kill criteria — cheap exit is a feature)

State the emerging core philosophy/skeleton in 3-5 lines and ask the kill question directly:

```text
이 골격이 실사용 가능한 틀인가?
아니라면 지금이 폐기 시점 — 여기서 접으면 비용은 이 대화뿐이다.
```

If the user kills it: record the reasoning in the worklog (that record IS the deliverable)
and stop. If it survives: the skeleton becomes the PRD's Problem/Solution seed.

### Step 4: Structural Decisions + Gap Enumeration → One at a Time

1. Settle the 2-3 **load-bearing structural decisions** first (the ones everything else hangs
   on — e.g. timeframe/granularity, single vs multi-tenant, batch vs realtime), one per turn.
2. Then **enumerate the full remaining gap list in one shot** — every open decision the PRD
   needs, presented as a numbered list **ordered by architecture impact** (a gap whose answer
   would change data models/interfaces/UX flows outranks one that only tunes a threshold).
3. Resolve them **one per turn**, each with a recommended option marked `(권장)` and a
   one-line rationale — the user's typical reply is "고고"; make that reply safe by making
   every recommendation genuinely defensible. Thresholds and tunables the user says they'll
   adjust empirically get recorded as such (🔶 Assumption with a "runtime-tunable" note), not
   interrogated to a fake precision.
4. Every resolution → worklog, with rationale.

### Step 5: Unknown Knowns — Brainstorm, Prototype, References (optional, per gap)

For gaps the user can only resolve by *reacting* ("보면 안다"):

- **Brainstorm**: present 3-4 genuinely divergent directions to react to (not variations of
  one idea).
- **Prototype**: route through the `spike` skill (T1 ≤15min probe) — a throwaway HTML mock or
  feasibility probe; the findings note feeds back here. UI mocks use `design-baseline`
  tokens so reacting to the mock is reacting to something shippable.
- **References**: when the user can't articulate what they want, ask for a reference — an
  existing repo/module/library/design they like — and **read its source** (not a screenshot)
  to extract the semantics they're pointing at. An external repo offered by the user is a
  parking-lot item with priority: analyze it and REPORT THE ANALYSIS before folding its ideas
  in — never silently absorb it.

### Step 6: Consolidate

Read the whole worklog back and present a 10-line summary of everything decided + all
remaining 🔶/🔵 tags. This is the last cheap moment to catch a contradiction. One user
confirmation, then write.

### Step 7: Write the PRD (delegate to `prd-authoring`)

Sweep the Parking Lot (hard rule from Step 1). Then apply the `prd-authoring` skill:
8-phase structure, GEARS-compatible acceptance criteria, Testing Decisions (seams), template
choice scaled to project size, no file paths, no unresolved placeholders (`TBD`/`_or_equivalent`
— `/ms.checklist` WARNs on them anywhere and FAILs them inside done criteria;
resolve or tag 🔵 with an owner). Mode C writes a
`## PRD Amendment N — YYYY-MM-DD` section appended to the existing PRD instead.

### Step 8: Report + Handoff

```text
📋 /ms.prd 완료

📄 산출물: docs/prd/PRD.md (또는 ## PRD Amendment N)
🗂️ 결정 기록: docs/prd/prd-worklog.md (결정 N건, 근거 포함)
🔶 Assumption N건 · 🔵 Open Question N건 (섹션 인라인)
🅿️ Parking Lot: 전부 처리됨

🎯 다음 단계:
- Mode A/B: /ms.pre-specter @docs/prd/PRD.md
- Mode C:   /ms.expand
(이 커맨드는 사이클 밖입니다 — 위 명령은 사용자가 직접 실행합니다)
```

## Relationship To Other Commands

```text
/ms.prd (사이클 밖, 사람 속도)
   └→ PRD.md ──→ /ms.pre-specter ──→ /ms.specter (Feature마다) ─→ ...
   └→ PRD Amendment N ──→ /ms.expand ──→ /ms.specter <새 NNN>
```

`/ms.prd` never runs gates and gates never run `/ms.prd`. The worklog is not a workflow
artifact — no command downstream reads it; it exists for the human's future re-analysis.

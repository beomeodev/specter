---
description: "Clarify ambiguous requirements"
argument-hint: "[question or ambiguity focus]"
---

# /ms.clarify - Clarify Requirements

Clarify ambiguous requirements in spec.md using Spec-Kit's standard clarification workflow.

## Overview

This command extends `/speckit-clarify` by injecting Constitution principles (especially GEARS) and enabling **Korean language interaction** for user communication.

**Key Features**:

-   AI receives GEARS principles BEFORE clarification
-   User interaction in **KOREAN** (questions, options, answers)
-   Final spec.md updates in **ENGLISH** with GEARS
-   Natural GEARS compliance through Constitution-guided AI behavior

## Language Policy

**User Interaction: KOREAN** ✅

Per Constitution Section II:

> "워크플로우 중 생성되는 문서들(spec.md, plan.md, tasks.md)에서만 반드시 영어를 사용하며,
> 사용자와의 상호작용에서는 한국어를 사용한다."

**Workflow**:

1. AI asks clarification questions in **KOREAN**
2. User answers in **KOREAN**
3. AI provides A/B/C options in **KOREAN** (with English GEARS reference)
4. spec.md is updated in **ENGLISH** with GEARS

## Execution Steps

### 1. Load Constitution

Read `.specify/memory/constitution.md` and confirm it exists.

**Session read policy**: per AGENTS.md §2 — reuse files already read this session; a fresh `Read` immediately before `Edit`/`Write` is still required.

**Key section to reference:**

-   **Section II**: Requirements Clarity (GEARS Standards)

**Language Policy** (from Section II):

-   User interaction: KOREAN
-   Workflow documents: ENGLISH

**IF Constitution not found**:
- Display error: "Constitution not found. Run `/ms.init` first."
- Exit

### 2. Inject Constitution Context into AI Prompt

Before running `/speckit-clarify`, provide AI with Constitution reference:

```
You are clarifying requirements in spec.md. Follow the project Constitution.

**Constitution**: .specify/memory/constitution.md

**Read and apply Section II** (Requirements Clarity - GEARS Standard):
- Use the GEARS canonical form: `[Where <static>] [While <runtime>] [When <trigger>] the <subject> shall <behavior>.`
- Identify ambiguous requirements and provide alternative interpretations

**LANGUAGE POLICY (MANDATORY)**:
- Communicate with user in KOREAN (questions and options)
- Show GEARS English format in parentheses for reference
- Update spec.md in ENGLISH with GEARS

**Example clarification** (in KOREAN):
```

요구사항 "로그인 기능이 필요합니다"가 모호합니다. 다음 중 선택해주세요:

A) 인증 서비스는 사용자 로그인 기능을 제공해야 합니다
(GEARS: the auth service shall provide a username/password login endpoint.)

B) 사용자가 로그인 버튼을 클릭하면, 인증 서비스가 자격증명을 검증해야 합니다
(GEARS: When a user clicks login, the auth service shall validate the credentials.)

```

**Refer to Constitution Section II for detailed GEARS rules.**

Now identify ambiguous requirements and begin clarification.
```

### 2.5. Question Discipline (evidence-first + mandatory recommendation)

Clarify is the cycle's only mandatory human stop — make each question earn it.
(Basis: transcript audit across 5 projects showed the user selects the recommended
option in ~100% of AskUserQuestion stops; questions answerable from evidence never
needed to reach them.)

**Before asking anything:**

1. **Try to answer from evidence first.** For each candidate ambiguity, check
   whether the codebase (existing patterns/conventions), the PRD text, the Feature
   Map's Key decisions, or Constitution Section IX already determines the answer.
   If it does, apply that answer directly and record it — do not ask.
2. Only ambiguities that evidence genuinely cannot resolve (product-intent choices,
   trade-offs with no recorded precedent) reach the user.

**Order the questions by architecture impact**: a question whose answer would change data
models, interfaces, or UX flows comes before one that only tunes copy or a threshold — if
the user's patience runs out mid-stream, the answers that matter most are already banked.

**Every question that does reach the user:**

- MUST present a **recommended option as option 1, marked `(권장)`**, with a
  one-line rationale tied to evidence ("기존 X 패턴과 일관", "PRD §y의 방향과 부합").
- Options remain genuine alternatives — the recommendation is a default, not a
  rubber stamp; never fabricate a recommendation when the evidence is truly neutral
  (say so instead: "근거상 우열 없음").

**In the final report**, list separately: (a) 자체 해소된 항목 — each with the evidence
that resolved it, so the user can veto any; (b) 사용자가 결정한 항목.

### 3. Run Base Clarify Command

Execute `/speckit-clarify` with Constitution-enhanced context:

```
/speckit-clarify $ARGUMENTS
```

This runs clarification workflow with AI following GEARS principles and using Korean for user interaction.

### 4. Report Success

Display summary:

```json
{
    "clarifications_made": 5,
    "spec_updated": "specs/001-user-authentication/spec.md",
    "gears_compliance": "natural (via Constitution)",
    "next_step": "/ms.plan"
}
```

Display next steps (in KOREAN):

```
✅ 요구사항 명확화 완료!

📄 업데이트됨: specs/001-user-authentication/spec.md

🎯 다음 단계:
1. 명확화된 요구사항 검토
2. `/ms.plan` 실행하여 구현 계획 작성
3. AI가 Constitution 기반으로 GEARS 형식을 따랐습니다 ✅

📖 GEARS 준수 달성:
- Constitution Section II (GEARS 규칙)
- AI 자연어 이해
- 강제 변환 로직 없음 (Constitution 주입 방식)
```

## Error Handling

### Error 1: Spec-Kit Not Initialized

**Symptom**: `.specify/` directory missing

**Message**:

```
❌ Error: Spec-Kit not initialized

Please run: /ms.init
```

**Exit**: Code 1

### Error 2: Base Command Failed

**Symptom**: `/speckit-clarify` returned error

**Message**:

```
❌ Error: Clarification failed

The base `/speckit-clarify` command encountered an error.
Please check the error message above and retry.
```

**Exit**: Code 1

## Run-State Ledger (bookkeeping, not a gate)

Append one line to `.specify/specter-run.jsonl` (create it if needed; append-only, never
rewritten — a missing/corrupt ledger never blocks this command, it only speeds up conductor
resume). Reaching this point means every ambiguity was resolved (or none existed), so `verdict`
is `PASS`:

```bash
mkdir -p .specify
printf '{"ts":"%s","cycle":"feature","feature":"%s","step":"clarify","verdict":"PASS","artifacts":["%s"]}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "<NNN>" "specs/<spec-id>/spec.md" >> .specify/specter-run.jsonl
```

## Next Command

After `/ms.clarify`: Run `/ms.plan` to create the implementation plan based on the clarified requirements. `/ms.checklist` is only used before `/ms.specify`.

---
description: "Clarify ambiguous requirements"
---

# /ms.clarify - Clarify Requirements

Clarify ambiguous requirements in spec.md using Spec-Kit's standard clarification workflow.

## Overview

This command extends `/speckit.clarify` by injecting Constitution principles (especially EARS format) and enabling **Korean language interaction** for user communication.

**Key Features**:

-   AI receives EARS principles BEFORE clarification
-   User interaction in **KOREAN** (questions, options, answers)
-   Final spec.md updates in **ENGLISH** with EARS format
-   Natural EARS compliance through Constitution-guided AI behavior

## Language Policy

**User Interaction: KOREAN** ✅

Per Constitution Section IV:

> "워크플로우 중 생성되는 문서들(spec.md, plan.md, tasks.md)에서만 반드시 영어를 사용하며,
> 사용자와의 상호작용에서는 한국어를 사용한다."

**Workflow**:

1. AI asks clarification questions in **KOREAN**
2. User answers in **KOREAN**
3. AI provides A/B/C options in **KOREAN** (with English EARS reference)
4. spec.md is updated in **ENGLISH** with EARS format

## Execution Steps

### 1. Load Constitution

Read `.specify/memory/constitution.md` and confirm it exists.

**Key section to reference:**

-   **Section IV**: Requirements Clarity (EARS Standards)

**Language Policy** (from Section IV):

-   User interaction: KOREAN
-   Workflow documents: ENGLISH

**IF Constitution not found**:
Display warning and continue (with broken references)

### 2. Inject Constitution Context into AI Prompt

Before running `/speckit.clarify`, provide AI with Constitution reference:

```
You are clarifying requirements in spec.md. Follow the project Constitution.

**Constitution**: .specify/memory/constitution.md

**Read and apply Section IV** (Requirements Clarity - EARS Standards):
- Use EARS patterns: WHEN/WHILE/WHERE/IF/SHALL/MAY
- Identify ambiguous requirements and provide alternative interpretations

**LANGUAGE POLICY (MANDATORY)**:
- Communicate with user in KOREAN (questions and options)
- Show EARS English format in parentheses for reference
- Update spec.md in ENGLISH with EARS format

**Example clarification** (in KOREAN):
```

요구사항 "로그인 기능이 필요합니다"가 모호합니다. 다음 중 선택해주세요:

A) 시스템은 사용자 로그인 기능을 제공해야 합니다
(EARS: System SHALL provide user login functionality)

B) 사용자가 로그인 버튼을 클릭하면, 시스템은 자격증명을 인증해야 합니다
(EARS: WHEN user clicks login button, system SHALL authenticate credentials)

```

**Refer to Constitution Section IV for detailed EARS patterns.**

Now identify ambiguous requirements and begin clarification.
```

### 3. Run Base Clarify Command

Execute `/speckit.clarify` with Constitution-enhanced context:

```
/speckit.clarify $ARGUMENTS
```

This runs clarification workflow with AI following EARS principles and using Korean for user interaction.

### 4. Report Success

Display summary:

```json
{
    "clarifications_made": 5,
    "spec_updated": "specs/001-user-authentication/spec.md",
    "ears_compliance": "natural (via Constitution)",
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
3. AI가 Constitution 기반으로 EARS 형식을 따랐습니다 ✅

📖 EARS 준수 달성:
- Constitution Section IV (EARS 규칙)
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

**Symptom**: `/speckit.clarify` returned error

**Message**:

```
❌ Error: Clarification failed

The base `/speckit.clarify` command encountered an error.
Please check the error message above and retry.
```

**Exit**: Code 1

## Next Command

After `/ms.clarify`: Run `/ms.plan` to create implementation plan based on clarified requirements, OR run `/ms.checklist` to generate completeness checklist.

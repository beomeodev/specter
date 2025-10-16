---
description: "Create implementation plan with Constitution reference"
---

# /ms.plan - Create Implementation Plan

Create an implementation plan following Spec-Kit workflow with Constitution compliance.

## Overview

This command extends `/speckit.plan` to include explicit Constitution references, ensuring AI follows TRUST principles, Simplicity-First architecture, and modular design during planning.

## Usage

```
/ms.plan
```

## Execution Steps

### 1. Load Project Context

**Auto-load project documents**:
- `.specify/memory/constitution.md` (Constitution - REQUIRED)
- `AGENTS.md` (AI instructions, coding standards - if exists)
- `specs/[spec-id]/spec.md` (Feature specification - REQUIRED)

**IF Constitution or spec.md missing**:
- Display error: "Required files missing. Run `/ms.init` and `/ms.specify` first."
- Exit

**IF AGENTS.md missing**:
- Display notice: "AGENTS.md not found (will be created by `/ms.constitution`)"
- Continue

**Reference key sections**:
- Constitution Section II (Simplicity-First Architecture)
- Constitution Section III (Modular Design)
- Constitution Section V (TRUST Principles)
- Constitution Section IX (Project-specific constraints - **if exists**, added by `/ms.constitution`)

### 2. Inject Constitution Context into AI Prompt

Before running `/speckit.plan`, provide AI with Constitution reference:

```
You are creating an implementation plan that MUST follow the project Constitution.

**Constitution**: .specify/memory/constitution.md

**Read and apply these sections**:
- **Section II**: Simplicity-First Architecture - Prefer built-in tools, files ≤500 SLOC, functions ≤100 LOC
- **Section III**: Modular Design - Independent modules, clear interfaces, dependency injection
- **Section V**: TRUST 5 Principles - Test-First (TDD, ≥85% coverage), Readable, Unified, Secured, Trackable

**Refer to Constitution for detailed architectural principles and constraints.**

Now create the implementation plan following these principles.
```

### 2.5. Adaptive Context Analysis (AI Auto-Decision)

**Think deeply**: "Is this feature complex enough to need pattern research?"

**Complexity Indicators**:
- Similar feature exists → Find and reuse architecture patterns
- Multiple components involved → Need integration analysis
- External library integration → Need latest API research

**Decision**:

**IF Simple Plan** (예: "단일 유틸리티 함수", "설정 파일 추가"):
  - 0 sub-agents
  - Proceed directly to Step 3

**IF Moderate Plan** (예: "API 엔드포인트 추가", "데이터베이스 모델"):
  - Launch 1-2 sub-agents in PARALLEL:
    1. **Architecture_Pattern_Agent**:
       ```
       Task: "Find similar architectural patterns in existing codebase for '$SPEC_FEATURE'"

       Workflow:
       1. Review existing specs and plans (specs/**/spec.md, plan.md)
       2. Search existing code for similar features
       3. Extract reusable architectural decisions
       4. Return: File structure patterns, naming conventions, integration approaches
       ```

    2. **Library_API_Agent** (if external library needed):
       ```
       Task: "Research latest API documentation for libraries needed"

       Workflow:
       1. Identify external libraries from spec
       2. Use Context7 MCP for latest docs
       3. Return: Current API patterns, best practices, version compatibility
       ```

**IF Complex Plan** (예: "마이크로서비스 추가", "실시간 통신 시스템"):
  - Launch 3 sub-agents in PARALLEL:
    1. Architecture_Pattern_Agent (as above)
    2. Library_API_Agent (as above)
    3. **Integration_Design_Agent**:
       ```
       Task: "Design integration strategy for complex feature"

       Workflow:
       1. Map component boundaries
       2. Design data flow and interfaces
       3. Identify security considerations
       4. Return: Integration architecture, API contracts, testing strategy
       ```

**CRITICAL**: Always launch agents in PARALLEL (single message with multiple Task calls).

### 2.6. Synthesize Architecture Decisions

**IF sub-agents launched** (Step 2.5):
- Combine architectural insights
- Reuse existing patterns for consistency
- Apply latest library best practices
- Document integration decisions
- Ensure Constitution compliance (TRUST, file size limits)

**ELSE**:
- Skip (simple plan)

### 3. Run Base Plan Command

Execute `/speckit.plan` with Constitution-enhanced context:

```
/speckit.plan
```

This creates the implementation plan in `specs/{SPEC_ID}/plan.md` with AI automatically following architectural principles.

### 4. Add Constitution Reference Footer

After plan.md is created, append Constitution reference section to document:

```markdown
---

## 📜 Constitution

This plan follows the project [Constitution](.specify/memory/constitution.md).

**Key Sections:**

-   **Section II**: Simplicity-First Architecture
-   **Section III**: Modular Design
-   **Section V**: TRUST 5 Quality Principles

_Auto-added by `/ms.plan`_
```

### 3. Verify Constitution Exists

Check if `.specify/memory/constitution.md` exists:

```bash
ls -la .specify/memory/constitution.md
```

**IF NOT FOUND**:

```
⚠️ Warning: Constitution not found

Expected: .specify/memory/constitution.md

Please run `/ms.init` first to create the project Constitution.
Constitution defines architectural principles for this project.

Continuing with plan creation, but Constitution reference will be broken.
```

### 4. Report Success

Display summary:

```json
{
    "plan_created": "specs/001-user-authentication/plan.md",
    "constitution_referenced": true,
    "constitution_exists": true,
    "next_step": "/ms.tasks"
}
```

Display next steps:

```
✅ Implementation plan created successfully!

📄 Plan: specs/001-user-authentication/plan.md
📜 Constitution: .specify/memory/constitution.md

🎯 Next Steps:
1. Review plan.md architecture
2. Run `/ms.tasks` to generate implementation tasks with TAG IDs
3. AI followed TRUST principles based on Constitution ✅

📖 Plan includes:
- Modular architecture (independent testable units)
- File size limits (≤300 LOC)
- Function complexity limits (≤10)
- Security considerations
- TAG traceability design
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

### Error 2: Spec Not Found

**Symptom**: spec.md doesn't exist

**Message**:

```
❌ Error: Specification not found

Please run: /ms.specify first
```

**Exit**: Code 1

### Error 3: Base Command Failed

**Symptom**: `/speckit.plan` returned error

**Message**:

```
❌ Error: Plan creation failed

The base `/speckit.plan` command encountered an error.
Please check the error message above and retry.
```

**Exit**: Code 1

## Notes

-   **Automatic Constitution following**: AI reads Constitution and applies principles naturally
-   **Modular design focus**: Architecture respects TRUST and Simplicity-First
-   **No code enforcement**: Constitution serves as AI's guide, not enforced by code
-   **Next command**: `/ms.analyze` validates plan-spec consistency + TRUST compliance

## Implementation Details

**Base Command**: `/speckit.plan`

**Extensions**: Constitution reference section

**Tools**: SlashCommand (/speckit.plan), Read (constitution check), Edit (append Constitution section)

## Next Command

After `/ms.plan`: Run `/ms.constitution` to extract project-specific constraints from spec.md and plan.md

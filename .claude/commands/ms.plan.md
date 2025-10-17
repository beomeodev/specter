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

### 2.5. Adaptive Context Analysis (Quantitative Decision)

**Step 1: Analyze Spec Complexity (Mandatory)**

Read spec.md and extract metrics:

```bash
# Count functional requirements (FRs)
FR_COUNT=$(grep -E "^#{1,3}\s+FR-[0-9]+" specs/*/spec.md | wc -l)

# Count components mentioned
COMPONENT_COUNT=$(grep -iEo "\b(service|controller|model|repository|handler|middleware|component|page)\b" specs/*/spec.md | sort -u | wc -l)

# Check for integration keywords
INTEGRATION_KEYWORDS=$(grep -iEo "\b(external|api|integration|third-party|webhook|oauth)\b" specs/*/spec.md | wc -l)

# Check for existing similar plans
SIMILAR_PLANS=$(find specs/ -name "plan.md" 2>/dev/null | wc -l)
```

**Step 2: Apply Decision Tree**

Execute in priority order (stop at first match):

```
┌─────────────────────────────────────────────────────────────┐
│ DECISION TREE (Priority Order)                              │
├─────────────────────────────────────────────────────────────┤
│ 1. IF INTEGRATION_KEYWORDS ≥ 3                              │
│    → COMPLEX (external integration)                         │
│                                                              │
│ 2. IF FR_COUNT ≤ 2 AND COMPONENT_COUNT ≤ 2                  │
│    → SIMPLE (single utility/config)                         │
│                                                              │
│ 3. IF COMPONENT_COUNT ≥ 5 OR FR_COUNT ≥ 8                   │
│    → COMPLEX (multi-component system)                       │
│                                                              │
│ 4. IF SIMILAR_PLANS ≥ 3                                     │
│    → MODERATE (patterns available)                          │
│                                                              │
│ 5. IF COMPONENT_COUNT ≥ 2 OR FR_COUNT ≥ 3                   │
│    → MODERATE                                                │
│                                                              │
│ 6. FALLBACK (unable to determine)                           │
│    → MODERATE (safe default - 2 agents)                     │
└─────────────────────────────────────────────────────────────┘
```

**Step 3: Execute Sub-Agent Strategy**

Based on complexity determined above:

**IF SIMPLE**:
  - 0 sub-agents
  - Proceed directly to Step 3

**IF MODERATE**:
  - Launch 2 sub-agents in PARALLEL (single message with 2 Task calls):
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

**IF COMPLEX**:
  - Launch 3 sub-agents in PARALLEL (single message with 3 Task calls):
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

**Debug Output** (for transparency):
```json
{
  "complexity_metrics": {
    "fr_count": 5,
    "component_count": 4,
    "integration_keywords": 2,
    "similar_plans": 3
  },
  "decision": "MODERATE",
  "reason": "Rule 4: SIMILAR_PLANS ≥ 3",
  "agents_spawned": 2
}
```

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
- File size limits (≤500 SLOC)
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

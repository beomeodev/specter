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

### 1. Verify Prerequisites

**Check required files exist**:
- `.specify/memory/constitution.md` (Constitution - REQUIRED)
- `specs/[spec-id]/spec.md` (Feature specification - REQUIRED)

**IF Constitution or spec.md missing**:
- Display error: "Required files missing. Run `/ms.init` and `/ms.specify` first."
- Exit

### 2. Provide Constitution Guidelines to `/speckit.plan`

**IMPORTANT**: `/speckit.plan` will read `constitution.md` internally. `/ms.plan`'s role is to provide **reading guidelines**, not to read it ourselves.

**Before executing `/speckit.plan`**, instruct it to follow these guidelines when reading Constitution:

```
When executing /speckit.plan, the agent must read and strictly adhere to constitution.md before proceeding.:

**Constitution Reading Guidelines**:

1. **Focus on Architecture Sections** (Priority Order):
   - **Section II**: Simplicity-First Architecture
     → Prefer built-in tools over external dependencies
     → Files ≤500 SLOC, functions ≤100 LOC
     → Choose simplest solution first

   - **Section III**: Modular Design
     → Independent modules with clear interfaces
     → Dependency injection over hardcoded dependencies
     → Separation of concerns

   - **Section V**: TRUST 5 Principles
     → Test-First: TDD with ≥85% coverage
     → Readable: Clear naming, minimal complexity
     → Unified: Consistent patterns across codebase
     → Secured: Security by default
     → Trackable: TAG traceability (SPEC → TEST → CODE)

2. **Apply Project-Specific Constraints** (if exists):
   - **Section IX**: Project-specific rules from `/ms.constitution`
   → Technology stack constraints
   → Team conventions
   → Domain-specific requirements

3. **Translate Principles to Architecture Decisions**:
   - Use Constitution principles to guide:
     → Component structure
     → Library selection
     → Testing strategy
     → Security measures
     → Traceability design

**Expected Behavior**:
- Read constitution.md when /speckit.plan starts
- Apply principles naturally during planning
- Document how principles influenced design choices
- Ensure plan respects all Constitution constraints
```

### 3. Adaptive Context Analysis (Quantitative Decision)

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
  - Proceed directly to Step 4

**IF MODERATE**:
  - Launch 2 sub-agents in TRUE PARALLEL (using Claude Code Task tool):

    **Step 1: Launch agents in parallel with single message**
    ```python
    # IMPORTANT: Send SINGLE message with MULTIPLE Task tool calls
    # This enables true parallel execution

    # Agent 1: Explore codebase for patterns
    Task(
        subagent_type="codebase-explorer",
        description="Find similar patterns",
        prompt="""Search existing codebase for similar patterns to feature: '$SPEC_FEATURE'

        Focus on:
        - Similar architectural implementations
        - Existing folder structure and naming conventions
        - Reusable components and utilities
        - Integration patterns

        Return: Similar features, architectural patterns, reusable components, integration approach"""
    )

    # Agent 2: Research library documentation (if needed)
    Task(
        subagent_type="library-researcher",
        description="Research library docs",
        prompt="""Research latest library documentation for: '$REQUIRED_LIBRARIES'

        Use Context7 MCP to fetch:
        - Latest API usage examples
        - Best practices from official docs
        - Version compatibility notes
        - Breaking changes

        Return: Libraries researched, API examples, best practices, compatibility notes"""
    )
    ```

    **Step 2: Agents execute in parallel**
    - Both agents run simultaneously in separate threads
    - No blocking - agents work independently
    - Claude Code orchestrates parallel execution automatically

    **Step 3: Results returned when complete**
    - Task tool returns results automatically when agents finish
    - Results available in same conversation context

**IF COMPLEX**:
  - Launch 3 sub-agents in TRUE PARALLEL (using Claude Code Task tool):

    **Step 1: Launch all agents in parallel with single message**
    ```python
    # CRITICAL: Send SINGLE message with THREE Task tool calls
    # This enables true parallel execution of all agents

    # Agent 1: Explore codebase for patterns
    Task(
        subagent_type="codebase-explorer",
        description="Find similar patterns",
        prompt="""Search existing codebase for similar patterns to feature: '$SPEC_FEATURE'

        Focus on:
        - Similar architectural implementations
        - Existing folder structure and naming conventions
        - Reusable components and utilities
        - Integration patterns

        Return: Similar features, architectural patterns, reusable components, integration approach"""
    )

    # Agent 2: Research library documentation
    Task(
        subagent_type="library-researcher",
        description="Research library docs",
        prompt="""Research latest library documentation for: '$REQUIRED_LIBRARIES'

        Use Context7 MCP to fetch:
        - Latest API usage examples
        - Best practices from official docs
        - Version compatibility notes
        - Breaking changes

        Return: Libraries researched, API examples, best practices, compatibility notes"""
    )

    # Agent 3: Design integration strategy
    Task(
        subagent_type="integration-designer",
        description="Design integration",
        prompt="""Design integration strategy for complex feature: '$SPEC_FEATURE'

        Analyze:
        - System architecture and dependencies
        - Integration points and interfaces
        - Data flow and communication patterns
        - Security and performance considerations

        Return: Integration architecture, API design, data flow, risk assessment"""
    )
    ```

    **Step 2: All 3 agents work independently in parallel**
    - Codebase explorer finds existing patterns
    - Library researcher fetches latest docs via Context7 MCP
    - Integration designer plans architecture
    - True parallel execution - all agents run simultaneously

    **Step 3: Results returned when complete**
    - Task tool returns all results automatically
    - Results available in same conversation context
    - Synthesize findings in Step 3.1

**⚠️ AGENT EXECUTION RULES**:
- **codebase-explorer** → Uses Claude Code Task tool (searches codebase with Glob/Grep/Read)
- **library-researcher** → Uses Claude Code Task tool (fetches docs via Context7 MCP)
- **integration-designer** → Uses Claude Code Task tool (designs integration architecture)

**CRITICAL - TRUE PARALLEL EXECUTION**:
1. **MUST send SINGLE message** with multiple Task tool calls
2. All agents launch simultaneously in separate threads
3. No blocking - agents execute independently
4. Results returned automatically when complete
5. Example of parallel launch:
   ```python
   # CORRECT: Single message, multiple Task calls
   Task(subagent_type="codebase-explorer", ...)
   Task(subagent_type="library-researcher", ...)
   Task(subagent_type="integration-designer", ...)

   # WRONG: Sequential messages (blocks between calls)
   # Message 1: Task(subagent_type="codebase-explorer", ...)
   # (wait for result)
   # Message 2: Task(subagent_type="library-researcher", ...)
   ```

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

### 3.1. Synthesize Architecture Decisions

**IF sub-agents launched** (Step 3):
- Combine architectural insights
- Reuse existing patterns for consistency
- Apply latest library best practices
- Document integration decisions
- Ensure Constitution compliance (TRUST, file size limits)

**ELSE**:
- Skip (simple plan)

### 4. Run Base Plan Command

Execute `/speckit.plan` with Constitution-enhanced context:

```
/speckit.plan
```

**Agent Delegation Strategy**:

`/speckit.plan` uses a **tiered agent model** to optimize cost and performance:

**Primary Agent** (High-Value Work):
- **implementation-planner** (Opus 4 model)
  - Architectural design and system structure
  - Critical technology stack decisions
  - TAG chain planning and traceability design
  - Integration strategy for complex features
  - **WHY Opus**: Architecture decisions have long-term impact; require deep reasoning

**Supporting Agents** (Research & Exploration):
- **library-researcher** (Haiku 3.5 model)
  - Fetch latest library documentation via Context7 MCP
  - Extract API usage examples and best practices
  - Check version compatibility and breaking changes
  - **WHY Haiku**: Documentation lookup is straightforward; doesn't require deep reasoning

- **codebase-explorer** (Haiku 3.5 model)
  - Search existing codebase for similar patterns
  - Identify reusable components and utilities
  - Document current architectural conventions
  - **WHY Haiku**: Pattern matching and code search are well-defined tasks

**Cost Optimization**:
```
Opus (expensive) → Strategic architecture decisions only
Haiku (economical) → Information gathering and pattern matching
```

This creates the implementation plan in `specs/{SPEC_ID}/plan.md` with AI automatically following architectural principles.

### 5. Add Constitution Reference Footer

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

### 6. Verify Constitution Exists

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

### 7. Report Success

Display summary:

```json
{
    "plan_created": "specs/001-user-authentication/plan.md",
    "constitution_referenced": true,
    "constitution_exists": true,
    "next_step": "/ms.constitution"
}
```

Display next steps:

```
✅ Implementation plan created successfully!

📄 Plan: specs/001-user-authentication/plan.md
📜 Constitution: .specify/memory/constitution.md

🎯 Next Steps:
1. Review plan.md architecture
2. Run `/ms.constitution` to extract project-specific constraints
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

-   **Guidelines over Execution**: `/ms.plan` provides Constitution reading guidelines to `/speckit.plan`, avoiding redundant file operations
-   **Tiered Agent Model**: Uses Opus for strategic architecture, Haiku for research/exploration (cost optimization)
-   **Modular design focus**: Architecture respects TRUST and Simplicity-First principles
-   **No code enforcement**: Constitution serves as AI's guide, not enforced by code
-   **Next command**: `/ms.analyze` validates plan-spec consistency + TRUST compliance

## Implementation Details

**Base Command**: `/speckit.plan` (handles Constitution reading internally)

**Extensions**:
- Constitution reading guidelines (Step 2)
- Constitution reference footer (Step 5)
- Adaptive context analysis with parallel agents (Step 3)

**Tools**:
- SlashCommand (`/speckit.plan`)
- Bash (verify prerequisites)
- Edit (append Constitution reference section)
- Task (launch parallel agents: codebase-explorer, library-researcher, integration-designer)

## Next Command

After `/ms.plan`: Run `/ms.constitution` to extract project-specific constraints from spec.md and plan.md

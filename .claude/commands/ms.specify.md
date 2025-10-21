---
description: "Create feature specification with Constitution reference"
---

# /ms.specify - Create Feature Specification

Create a feature specification following Spec-Kit workflow with Constitution compliance.

## Overview

This command extends `/speckit.specify` to include explicit Constitution references, ensuring AI follows EARS, TRUST, and TAG principles during specification writing.

## Usage

```
/ms.specify [feature_name]
```

Example:

```
/ms.specify user-authentication
```

## Execution Steps

### 1. Load Project Context

**Auto-load project documents**:
- `.specify/memory/constitution.md` (Constitution - REQUIRED)
- `AGENTS.md` (AI instructions, coding standards - if exists)

**IF Constitution missing**:
- Display error: "Constitution not found. Run `/ms.init` first."
- Exit

**IF AGENTS.md missing**:
- Display notice: "AGENTS.md not found (will be created by `/ms.constitution`)"
- Continue

**Reference key sections**:
- Constitution Section IV (EARS Standards)
- Constitution Section V (TRUST Principles)
- Constitution Section IX (Project-specific constraints - **if exists**, added by `/ms.constitution`)
- project-structure.md (understand existing tech stack - **if exists**)

### 2. Inject Constitution Context into AI Prompt

Before running `/speckit.specify`, provide AI with Constitution reference:

```
You are creating a specification that MUST follow the project Constitution.

**Constitution**: .specify/memory/constitution.md

**Read and apply these sections**:
- **Section IV**: Requirements Clarity (EARS Standards) - Use EARS patterns (WHEN/WHILE/WHERE/IF/SHALL)
- **Section V**: TRUST 5 Principles - Design for testability, readability, security, traceability

**Language Policy**:
- Write ALL requirements in ENGLISH
- Use EARS keywords (WHEN/WHILE/WHERE/IF/SHALL/MAY) in English
- If user provides Korean input, translate to English EARS format

**Example**:
User input (Korean): "사용자가 로그인하면 토큰을 발급한다"
Your output (English): "WHEN user logs in with valid credentials, system SHALL issue JWT token"

**Refer to Constitution for detailed EARS patterns and TRUST principles.**

Now create the specification following these principles.
```

### 2.5. Adaptive Context Analysis (Quantitative Decision)

**Step 1: Analyze User Request (Mandatory)**

Extract and count keywords from `$ARGUMENTS`:

```bash
# Count simple keywords
SIMPLE_KEYWORDS=$(echo "$ARGUMENTS" | grep -iEo "\b(config|setting|constant|type|interface|util|helper|log|message)\b" | wc -l)

# Count moderate keywords
MODERATE_KEYWORDS=$(echo "$ARGUMENTS" | grep -iEo "\b(feature|module|component|endpoint|model|service|page|form)\b" | wc -l)

# Count complex keywords
COMPLEX_KEYWORDS=$(echo "$ARGUMENTS" | grep -iEo "\b(system|architecture|integration|external|api|realtime|workflow|migration)\b" | wc -l)

# Check for existing similar specs
SIMILAR_SPECS=$(find specs/ -name "spec.md" 2>/dev/null | wc -l)
```

**Step 2: Apply Decision Tree**

Execute in priority order (stop at first match):

```
┌─────────────────────────────────────────────────────────────┐
│ DECISION TREE (Priority Order)                              │
├─────────────────────────────────────────────────────────────┤
│ 1. IF COMPLEX_KEYWORDS ≥ 2                                  │
│    → COMPLEX (system-level change)                          │
│                                                              │
│ 2. IF SIMPLE_KEYWORDS ≥ 2 AND COMPLEX_KEYWORDS = 0          │
│    → SIMPLE (config/utility change)                         │
│                                                              │
│ 3. IF MODERATE_KEYWORDS ≥ 1 OR SIMILAR_SPECS ≥ 3            │
│    → MODERATE (feature with patterns available)            │
│                                                              │
│ 4. IF SIMPLE_KEYWORDS ≥ 1 AND MODERATE_KEYWORDS = 0         │
│    → SIMPLE                                                  │
│                                                              │
│ 5. FALLBACK (unable to determine)                           │
│    → MODERATE (safe default - 2 agents)                     │
└─────────────────────────────────────────────────────────────┘
```

**Step 3: Execute Sub-Agent Strategy**

Based on complexity determined above:

**IF SIMPLE**:
  - 0 sub-agents
  - Proceed directly to Step 3

**IF MODERATE**:
  - Launch 2 sub-agents in TRUE PARALLEL (background execution):

    **Step 1: Start all agents in background**
    ```python
    # Launch agent 1 in background
    task_id_1 = mcp__cli-bridge__gemini_cli(
        prompt="Search existing codebase for similar patterns to user request '$ARGUMENTS'",
        background=True  # Returns immediately with task_id
    )

    # Launch agent 2 in background (if external library needed)
    task_id_2 = mcp__cli-bridge__gemini_cli(
        prompt="Research latest documentation for libraries needed for '$ARGUMENTS'",
        background=True  # Returns immediately with task_id
    )
    ```

    **Step 2: Claude continues its own work while agents run**
    - Agents execute independently in background
    - Claude Code can do other tasks without blocking

    **Step 3: Retrieve results when needed**
    ```python
    # Get results (blocks until completion)
    result_1 = mcp__cli-bridge__get_task_result(task_id=task_id_1, wait=True)
    result_2 = mcp__cli-bridge__get_task_result(task_id=task_id_2, wait=True)
    ```

**IF COMPLEX**:
  - Launch 3 sub-agents in TRUE PARALLEL (background execution):

    **Step 1: Start all agents in background**
    ```python
    # Gemini agents (background execution)
    task_id_1 = mcp__cli-bridge__gemini_cli(
        prompt="Search existing codebase for similar patterns to user request '$ARGUMENTS'",
        background=True
    )
    task_id_2 = mcp__cli-bridge__gemini_cli(
        prompt="Research latest documentation for libraries needed for '$ARGUMENTS'",
        background=True
    )

    # Claude Code Task (runs in parallel)
    task_id_3 = Task(
        subagent_type="integration-designer",
        prompt="Analyze dependencies and integration points for '$ARGUMENTS'"
    )
    ```

    **Step 2: All 3 agents work independently in parallel**
    - Gemini agents run in background via MCP server
    - Claude agent runs in separate thread
    - No blocking, true parallel execution

    **Step 3: Retrieve results when needed**
    ```python
    result_1 = mcp__cli-bridge__get_task_result(task_id=task_id_1, wait=True)
    result_2 = mcp__cli-bridge__get_task_result(task_id=task_id_2, wait=True)
    result_3 = # Task tool result
    ```

**⚠️ AGENT EXECUTION RULES**:
- **codebase-explorer** → MUST use Gemini via `mcp__cli-bridge__gemini_cli(background=True)`
- **library-researcher** → MUST use Gemini via `mcp__cli-bridge__gemini_cli(background=True)`
- **integration-designer** → MUST use Claude Code Task tool (NOT MCP)

**CRITICAL - TRUE PARALLEL EXECUTION**:
1. Launch all MCP agents with `background=True` parameter
2. Returns `TASK_STARTED:{task_id}` immediately
3. Agents execute independently (no blocking)
4. Use `get_task_result(task_id, wait=True)` to retrieve results
5. Python 3.14 free-threading enables real parallelism (no GIL)

**Debug Output** (for transparency):
```json
{
  "complexity_metrics": {
    "simple_keywords": 0,
    "moderate_keywords": 1,
    "complex_keywords": 2,
    "similar_specs": 5
  },
  "decision": "COMPLEX",
  "reason": "Rule 1: COMPLEX_KEYWORDS ≥ 2",
  "agents_spawned": 3
}
```

### 2.6. Synthesize Findings

**IF sub-agents launched** (Step 2.5):
- Combine results from all agents
- Identify existing patterns to reuse
- Note latest library APIs
- Map integration points
- Document Constitution compliance considerations

**ELSE**:
- Skip (simple request)

### 3. Run Base Specify Command

Execute `/speckit.specify` with Constitution-enhanced context:

```
/speckit.specify $ARGUMENTS
```

This creates the specification in `specs/{SPEC_ID}/spec.md` with AI automatically following EARS and TRUST principles.

### 4. Add Constitution Reference Footer

After spec.md is created, append Constitution reference section to document:

```markdown
---

## 📜 Constitution

This specification follows the project [Constitution](../../.specify/memory/constitution.md).

**Key Sections:**
- **Section IV**: EARS Requirements Standards
- **Section V**: TRUST 5 Quality Principles
- **TAG System**: Traceability (SPEC → TEST → CODE)

_Auto-added by `/ms.specify`_
```

### 5. Report Success

Display summary:

```json
{
    "spec_created": "specs/001-user-authentication/spec.md",
    "constitution_referenced": true,
    "constitution_exists": true,
    "next_step": "/ms.clarify or /ms.checklist"
}
```

Display next steps:

```
✅ Specification created successfully!

📄 Spec: specs/001-user-authentication/spec.md
📜 Constitution: .specify/memory/constitution.md

🎯 Next Steps:
1. Review spec.md for completeness
2. Run `/ms.clarify` to clarify ambiguous requirements (질의응답)
3. OR run `/ms.checklist` to generate completeness checklist (체크리스트)
4. Then proceed to `/ms.plan` for implementation planning

📖 Constitution Sections Applied:
- Section IV: EARS (5 requirement patterns)
- Section V: TRUST (5 quality principles)
```

## Error Handling

### Error 1: Spec-Kit Not Initialized

**Symptom**: `.specify/` directory missing

**Message**:

```
❌ Error: Spec-Kit not initialized

This project has not been initialized with Spec-Kit.

Please run:
  /ms.init

This will set up Spec-Kit templates AND create the Constitution.
```

**Exit**: Code 1

### Error 2: Base Command Failed

**Symptom**: `/speckit.specify` returned error

**Message**:

```
❌ Error: Spec creation failed

The base `/speckit.specify` command encountered an error.
Please check the error message above and retry.

Common issues:
- Spec ID already exists
- Invalid directory structure
- Missing permissions
```

**Exit**: Code 1

## Notes

-   **Constitution injected BEFORE spec creation**: AI receives principles upfront, not after
-   **Natural compliance**: AI applies EARS/TRUST during writing, not via post-processing
-   **English output**: All specs written in English (Korean input → English EARS output)
-   **No forced conversion**: Constitution guides AI behavior, not enforced by code
-   **Workflow improvement**: This approach ensures higher quality specs from the start

## Implementation Details

**Tools**: SlashCommand (/speckit.specify), Read (constitution check), Edit (append Constitution section)

## Next Command

After `/ms.specify`:
1. Run `/ms.clarify` to clarify ambiguous requirements (질의응답 방식)
2. OR run `/ms.checklist` to generate completeness checklist (체크리스트 방식)
3. Then proceed to `/ms.plan` for implementation planning

**Workflow**: `/ms.specify` → `/ms.clarify` or `/ms.checklist` → `/ms.plan`

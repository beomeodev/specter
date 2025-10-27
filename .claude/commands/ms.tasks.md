---
description: "Generate tasks with automatic TAG ID generation"
---

# /ms.tasks - Generate Tasks with TAG IDs

Extends `/speckit.tasks` to generate implementation tasks with automatic TAG ID assignment.

## Overview

**This command is a wrapper around `/speckit.tasks` with enhanced functionality.**

**Base Command**: `/speckit.tasks` - Generates implementation tasks from spec.md and plan.md

**Additional Features** (provided by `/ms.tasks`):
- Library documentation research via `library-researcher` agent (Haiku + Context7 MCP)
- Automatic TAG ID generation for each Functional Requirement
- Domain extraction from FR titles (AUTH, USER, PAY, etc.)
- TAG chain insertion (@SPEC → @TEST → @CODE) for traceability
- Constitution-aware task breakdown (respects file size limits)
- Library-informed task structure (tasks reflect actual implementation patterns)

**Purpose**: Creates a detailed task breakdown with full traceability support, ensuring each User Story has a unique TAG ID for the My-Spec workflow.

## Execution Steps

### 0. Load Project Context

**Auto-load project documents**:
- `.specify/memory/constitution.md` (Constitution - REQUIRED)
- `AGENTS.md` (AI instructions, coding standards - if exists)
- `specs/[spec-id]/spec.md` (Feature specification - REQUIRED)
- `specs/[spec-id]/plan.md` (Implementation plan - REQUIRED)

**IF Constitution, spec.md, or plan.md missing**:
- Display error: "Required files missing. Run `/ms.init`, `/ms.specify`, and `/ms.plan` first."
- Exit

**Reference for task generation**:
- Constitution Section II (Simplicity-First - file size targets: ≤500 SLOC, ≤100 LOC/function)
- Constitution Section IX (Project-specific constraints - **if exists**, added by `/ms.constitution`)
- AGENTS.md (coding standards, task organization patterns - if exists)

**These documents help**:
- Generate appropriate TAG domain names based on project structure
- Break down tasks according to file size limits
- Apply project-specific task organization patterns

### 1. Library Documentation Research (If Needed)

**Analyze plan.md**: Does implementation require external libraries or integrations?

**Detection indicators**:
- plan.md mentions library names (FastAPI, React, Stripe, Next.js, etc.)
- Integration with external services (OAuth, payment gateways, APIs)
- New third-party dependencies in technology stack

**IF external libraries detected**:

  1. **Identify required libraries and their use cases**
  2. **Launch library-researcher agent (background execution)**:
     ```python
     # Launch library research agent
     Task(
         subagent_type="library-researcher",
         description="Research library docs",
         prompt="""Research latest library documentation for: '$REQUIRED_LIBRARIES'

         Use Context7 MCP to fetch:
         - Latest API usage examples
         - Best practices from official docs
         - Version compatibility notes
         - Breaking changes
         - Common implementation patterns

         Focus on:
         - Task breakdown guidance (how features are typically implemented)
         - File/module organization recommendations
         - Testing strategies for this library
         - Common pitfalls and edge cases

         Return: Libraries researched, implementation patterns, task breakdown guidance, testing strategies"""
     )

     # Agent runs independently while Claude continues with task generation
     # Results available when agent completes
     ```
  3. **Use library patterns to inform task breakdown** (more accurate estimation and structure)

**ELSE**:
  → Skip (no external libraries)

**Store library patterns** for use in Step 2 task generation.

### 2. Run Base Command

**IMPORTANT**: `/ms.tasks` delegates core task generation to `/speckit.tasks`.

Execute `/speckit.tasks` to generate base task structure with library research context:

```
/speckit.tasks $ARGUMENTS
```

**What `/speckit.tasks` does** (base functionality):
- Analyzes spec.md and plan.md
- Generates task breakdown with phases
- Creates dependency graph
- Produces tasks.md file
- **Enhanced with library research**: Tasks reflect actual library implementation patterns

**Output**: `specs/[spec-id]/tasks.md` with complete task structure (without TAG IDs yet)

### 3. TAG ID Generation (My-Spec Enhancement)

**This step is UNIQUE to `/ms.tasks`** - not provided by `/speckit.tasks`.

For each Functional Requirement (FR) in spec.md:

**Extract Domain**:

```bash
extract_domain() {
  local fr_title="$1"
  local fr_number="$2"

  # Match domain keywords
  echo "$fr_title" | rg -io '(auth|user|pay|cart|order|product|admin|notif|search|profile)' | head -n1 | tr '[:lower:]' '[:upper:]' \
    || echo "FR${fr_number}"  # Fallback to FR number
}
```

**Count Existing TAGs**:

```bash
count_tags_for_domain() {
  local domain="$1"
  rg "@SPEC:${domain}-" -c src tests backend/src frontend/src 2>/dev/null | awk -F: '{sum+=$2} END {print sum+0}'
}
```

**Generate TAG ID**:

```bash
generate_tag_id() {
  local domain="$1"
  local count=$(count_tags_for_domain "$domain")
  printf "%s-%03d" "$domain" $((count + 1))
}

# Example: AUTH-001, AUTH-002, PAY-001
```

### 4. Insert TAG Metadata (My-Spec Enhancement)

**This step is UNIQUE to `/ms.tasks`** - not provided by `/speckit.tasks`.

Add TAG chains to tasks.md for each User Story:

```markdown
## Phase 3: FR-1 Authentication (Priority: P0)

**TAG**: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001

**Goal**: Implement user authentication
**Independent Test**: Users can log in with email/password

### Implementation for FR-1

-   [ ] T015 Create auth service...
-   [ ] T016 Add login endpoint...
```

### 5. Report Output

```json
{
    "tag_ids": ["@SPEC:AUTH-001", "@SPEC:USER-001", "@SPEC:PAY-001"],
    "domain_map": {
        "AUTH": 1,
        "USER": 1,
        "PAY": 1
    },
    "tasks_updated": "specs/001-my-spec-spec/tasks.md"
}
```

## TAG Format

**Chain Format**:

```
@SPEC:{TAG_ID} → @TEST:{TAG_ID} → @CODE:{TAG_ID}
```

**Domain Extraction Examples**:

-   "FR-1: User Authentication" → Domain: AUTH (keyword match)
-   "FR-2: Shopping Cart" → Domain: CART (keyword match)
-   "FR-9: Random Feature" → Domain: FR9 (fallback)

## Error Handling

-   **SPEC_NOT_FOUND**: Run `/ms.specify` first
-   **TASKS_GENERATION_FAILED**: Base command failed
-   **RIPGREP_NOT_FOUND**: Install ripgrep ≥13.0
-   **DUPLICATE_TAG**: TAG ID collision detected

## Next Steps

After `/ms.tasks`:

1. Review tasks.md with TAG assignments
2. Run `/ms.analyze` to validate spec-tasks consistency and TRUST compliance

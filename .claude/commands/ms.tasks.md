---
description: "Generate tasks with automatic TAG ID generation"
---

# /ms.tasks - Generate Tasks with TAG IDs

Extends `/speckit.tasks` to generate implementation tasks with automatic TAG ID assignment.

## Overview

This command creates a detailed task breakdown and automatically assigns unique TAG IDs to each User Story for complete traceability (SPEC→TEST→CODE).

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

### 1. Run Base Command

Execute `/speckit.tasks` to generate base task structure:

```
/speckit.tasks $ARGUMENTS
```

This creates tasks.md with phases, dependencies, and task details.

### 2. TAG ID Generation

For each Functional Requirement (FR) in spec.md:

**Extract Domain**:

-   Use `src/lib/tag/generator.ts::extractDomain(frTitle, frNumber)`
-   Match against domain keywords: AUTH, USER, PAY, CART, etc.
-   **Fallback**: If no keyword match, use FR number (e.g., "FR-1" → "FR1")

**Count Existing TAGs**:

-   Use `src/lib/tag/scanner.ts::countTAGsForDomain(domain)`
-   Executes: `rg '@SPEC:{domain}-' -c` to count existing TAGs

**Generate TAG ID**:

-   Use `src/lib/tag/generator.ts::generateNextTAGID(domain, count)`
-   Format: `{DOMAIN}-{count+1:03d}`
-   Example: `AUTH-001`, `AUTH-002`, `PAY-001`

### 3. Insert TAG Metadata

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

### 4. Report Output

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
3. TAG IDs are now assigned ✅

## Notes

-   Requires ripgrep for TAG counting
-   TAG IDs are unique across the project
-   Domain extraction uses keyword matching with FR number fallback
-   Tasks.md becomes the implementation roadmap with full traceability

## Implementation Details

**Contract**: [specs/001-my-spec-spec/contracts/ms-tasks.json](../specs/001-my-spec-spec/contracts/ms-tasks.json)

**Libraries**:

-   `src/lib/tag/generator.ts` - Domain extraction, TAG ID generation
-   `src/lib/tag/scanner.ts` - ripgrep-based TAG counting

**Tools**: SlashCommand (/speckit.tasks), Read, Edit, Bash (ripgrep)

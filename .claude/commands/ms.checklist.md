---
description: "Generate a custom checklist for the current feature"
---

# /ms.checklist - Generate Feature Checklist

**My-Spec Wrapper**: This command executes the underlying `/speckit.checklist` command with full functionality.

## Purpose

Generate a custom requirements quality checklist ("Unit Tests for English") for your current feature.

## Usage

```bash
/ms.checklist [optional: checklist focus/type description]
```

**Examples**:
```bash
/ms.checklist                          # Interactive: AI will ask clarifying questions
/ms.checklist ux review                # Focus on UX requirements quality
/ms.checklist api security             # API + security requirements checklist
/ms.checklist comprehensive review     # Full requirements review checklist
```

## What This Does

This command wraps `/speckit.checklist` to maintain naming consistency with other My-Spec commands (`/ms.specify`, `/ms.plan`, `/ms.implement`, etc.).

## Execution Steps

### Step 0: Load Project Context

**Auto-load project documents**:
- `.specify/memory/constitution.md` (Constitution - REQUIRED)
- `AGENTS.md` (AI instructions, coding standards - if exists)
- `specs/[spec-id]/spec.md` (Feature specification - REQUIRED)

**IF Constitution or spec.md missing**:
- Display error: "Required files missing. Run `/ms.init` and `/ms.specify` first."
- Exit

**Reference for checklist generation**:
- Constitution Section IV (EARS Standards - requirement patterns to validate)
- Constitution Section IX (Project-specific quality standards - **if exists**, added by `/ms.constitution`)
- AGENTS.md (coding standards, quality expectations)

**These documents help**:
- Generate checklists that validate EARS pattern compliance
- Apply project-specific quality criteria (e.g., performance targets from Section IX)
- Create relevant questions based on project tech stack

### Step 1: Execute Underlying Command

Execute the underlying Spec-Kit checklist command with Constitution context:

```
/speckit.checklist $ARGUMENTS
```

## Workflow Position

```
/ms.specify → /ms.clarify → /ms.plan → /ms.constitution → /ms.tasks → /ms.analyze
                ↓                                                            ↓
          [/ms.checklist]                                              [/ms.checklist]
                ↓                                                            ↓
         Validate spec.md                                        Validate all requirements
         requirements quality                                    before implementation
```

**When to use**:
1. **After `/ms.specify` or `/ms.clarify`**: Validate that spec.md requirements are complete, clear, and consistent
2. **After `/ms.plan`**: Check that technical requirements and constraints are well-defined
3. **After `/ms.tasks`**: Ensure all implementation tasks map to clear requirements
4. **Any time**: Generate focused checklists for specific quality aspects (UX, API, security, etc.)
## See Also

- **[/speckit.checklist](.claude/commands/speckit.checklist.md)**: Full implementation details
- **[Checklist Template](../../templates/checklist-template.md)**: Canonical format
- **Constitution Reference**: My-Spec projects automatically reference constitution constraints

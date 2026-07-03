---
description: "Create implementation plan with Constitution reference"
argument-hint: "[implementation guidance or constraints]"
---

# /ms.plan - Create Implementation Plan

Create an implementation plan following Spec-Kit workflow with Constitution compliance.

## Overview

This command extends `/speckit-plan` to include explicit Constitution references, ensuring AI follows TRUST principles, Simplicity-First architecture, and modular design during planning.

## Usage

```
/ms.plan
```

## Execution Steps

### 1. Verify Prerequisites

**Check required files exist**:
- `.specify/memory/constitution.md` (Constitution - REQUIRED)
- `specs/[spec-id]/spec.md` (Feature specification - REQUIRED)

**Session read policy**: if a required file was already read in this session and has not
changed since (no edit by you, no user notice), reuse it — do not re-read. Exception: the
harness requires a fresh `Read` of a file before `Edit`/`Write`; always satisfy that
requirement even if the content is already in context.

**IF Constitution or spec.md missing**:
- Display error: "Required files missing. Run `/ms.init` and `/ms.specify` first."
- Exit

### 2. Provide Constitution Guidelines to `/speckit-plan`

**IMPORTANT**: `/speckit-plan` will read `constitution.md` internally. `/ms.plan`'s role is to provide **reading guidelines**, not to read it ourselves.

**Before executing `/speckit-plan`**, instruct it to follow these guidelines when reading Constitution:

```
When executing /speckit-plan, the agent must read and strictly adhere to constitution.md before proceeding.:

**Constitution Reading Guidelines**:

1. **Focus on Planning-Relevant Sections** (Priority Order):
   - **Section VI**: File, Architecture, And Tooling Governance
     → Prefer mature tools over custom implementations
     → Production files ≤700 SLOC, functions ≤100 LOC
     → Choose the simplest sufficient design

   - **Section VII**: Security Governance
     → Validate security-sensitive paths early
     → Bind authorization to resource ownership
     → Keep secrets out of source code and logs

   - **Section IV**: TRUST Review Model
     → Plan for tests, readability, consistency, security, and best-effort traceability

2. **Apply Project-Specific Constraints** (if exists):
   - **Section IX**: Project-specific baseline established by `/ms.constitution` from the checked PRD Feature Map
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
- Read constitution.md when /speckit-plan starts
- Apply principles naturally during planning
- Document how principles influenced design choices
- Ensure plan respects all Constitution constraints
```

### 3. Reality-First Context Analysis

`/ms.plan` must not invent architecture from the spec alone. Before writing or
accepting `plan.md`, inspect the current codebase and record which assumptions
were verified.

**Read and inspect**:
- Existing `specs/*/plan.md` files for nearby patterns.
- Existing source directories, tests, migrations, routes, schemas, config, and
  fixtures that the new feature is likely to touch.
- Official library documentation when the plan depends on current third-party
  APIs. Use available documentation tools directly; do not promise a specific
  subagent or model.

**Reality checks to run when relevant**:

```bash
# Existing plans and nearby implementation patterns
rg --files specs | rg '/plan\.md$'
rg -n "<feature keyword>|<domain keyword>" src backend frontend tests specs

# Next migration index, if the plan creates a migration
ls db/migrations/00*.sql 2>/dev/null | sort | tail -1

# Schema and column assumptions
rg -n "CREATE TABLE <table>|ALTER TABLE <table>|<column_name>" db backend src

# Existing file paths mentioned by the plan
test -f <path> || echo "MISSING: <path>"

# API/status/error-message conventions
rg -n "HTTP_401|HTTP_403|status_code=.*40|detail=.*찾을 수" backend src

# Existing env/config and fixtures
rg -n "os\.environ|getenv|process\.env|@pytest.fixture|fixture\(" backend frontend tests src
```

Use the smallest relevant subset. Do not run irrelevant checks just to fill the
table.

### 3.1. Required `Reality Verified` Section

The final `plan.md` MUST include this section before tasks are generated:

```markdown
## Reality Verified (auto-generated, blocking)

| Assumption | Verified by | Result |
|---|---|---|
| Next migration index = NNNN | `ls db/migrations/00*.sql | sort | tail -1` | PASS/FAIL/N/A |
| File `<path>` exists | `test -f <path>` | PASS/FAIL/N/A |
| Column `<table>.<column>` exists | `rg "<column>" db backend src` | PASS/FAIL/N/A |
| Existing route/service convention | `rg "<pattern>" backend/src src` | PASS/FAIL/N/A |
| Error/status convention | `rg "HTTP_401|HTTP_403|detail=" backend src` | PASS/FAIL/N/A |
```

Rules:
- `PASS`: command output directly supports the assumption.
- `FAIL`: command output contradicts or cannot support a required assumption.
- `N/A`: not relevant to this feature. Do not use `N/A` for an unverified but
  relevant assumption.

### 3.2. Blocking Rule

If any relevant assumption is `FAIL`, do not proceed silently.

Auto-fix before continuing when the failure is mechanical:
- stale file path
- migration index drift
- typo in an existing status or error-message convention

Stop and ask the user in Korean when the failure changes product or data design:
- missing schema column/table
- auth/status semantics differ from the spec
- new dependency or environment variable conflicts with project baseline
- implementation requires amending a clarified requirement

Korean prompt format:

```text
⚠️ Plan 가정 검증 실패:
1. <assumption> → 실제: <observed reality>

선택이 필요합니다:
1. 현실에 맞게 plan/spec를 수정하고 계속 진행
2. 새 요구사항으로 보고 amendment를 만든 뒤 계속 진행
3. 중단하고 /ms.clarify 또는 /ms.checklist로 되돌아가기
```

### 3.3. Synthesize Architecture Decisions

After reality verification:
- Reuse existing project patterns instead of inventing parallel structures.
- Prefer the smallest sufficient design that satisfies the spec and Constitution.
- Document only decisions that affect implementation, tests, security, data, or
  public API behavior.
- Keep plan details traceable to `spec.md`; avoid making `plan.md` a second
  source of truth for requirement wording.

### 4. Run Base Plan Command

Execute `/speckit-plan` with Constitution-enhanced context and the Reality
Verification findings from Step 3:

```
/speckit-plan
```

The generated `specs/{SPEC_ID}/plan.md` must reflect verified project reality.
Do not claim use of a specific model, subagent, or background process unless it
actually ran in the current environment.

### 5. Add Constitution Reference Footer

After plan.md is created, append Constitution reference section to document:

```markdown
---

## 📜 Constitution

This plan follows the project [Constitution](.specify/memory/constitution.md).

**Key Sections:**
-   **Section IV**: TRUST Review Model
-   **Section VI**: File, Architecture, And Tooling Governance
-   **Section VII**: Security Governance

_Auto-added by `/ms.plan`_
```

### 6. Verify Constitution Reference

The Constitution was already required in Step 1. Before reporting success, verify
that the footer link points to an existing `.specify/memory/constitution.md`. If
it is missing, treat this as a command error and stop; do not create a plan with
a broken governance reference.

### 7. Report Success

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
2. Proceed to `/ms.tasks`
3. If Section IX baseline is missing, stop and return to `/ms.constitution` after `/ms.verify`

📖 Plan includes:
- Modular architecture (independent testable units)
- File size limits (≤700 SLOC)
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

**Symptom**: `/speckit-plan` returned error

**Message**:

```
❌ Error: Plan creation failed

The base `/speckit-plan` command encountered an error.
Please check the error message above and retry.
```

**Exit**: Code 1

## Run-State Ledger (bookkeeping, not a gate)

Append one line to `.specify/specter-run.jsonl` (create it if needed; append-only, never
rewritten — a missing/corrupt ledger never blocks this command, it only speeds up conductor
resume). Reaching this point means `plan.md` reflects verified reality (mechanical fixes applied
automatically, design-level mismatches already resolved), so `verdict` is `PASS`:

```bash
mkdir -p .specify
printf '{"ts":"%s","cycle":"feature","feature":"%s","step":"plan","verdict":"PASS","artifacts":["%s"]}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "<NNN>" "specs/<spec-id>/plan.md" >> .specify/specter-run.jsonl
```

## Next Command

After `/ms.plan`: Run `/ms.tasks`. Section IX baseline should already be established by `/ms.constitution` before the per-Feature cycle starts.

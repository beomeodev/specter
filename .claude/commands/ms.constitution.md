---
description: "Extract project constraints to constitution Section IX"
---

# /ms.constitution - Extract Project Constraints & Rules

Extracts project-specific constraints from spec.md and plan.md, then updates:
1. **Constitution Section IX**: Technical constraints (dependencies, architecture, security)
2. **AGENTS.md**: Project-specific coding rules with examples (300-500 tokens)

## Overview

This command runs AFTER `/ms.plan` to extract:
- **Technical constraints** → Constitution Section IX (what technologies/patterns to use)
- **Coding patterns** → AGENTS.md Project Rules (how to write code in this project)

**Why after /ms.plan?**
- plan.md contains architecture decisions, tech stack choices, and file structure
- These are essential for extracting meaningful project constraints
- spec.md alone doesn't have enough technical detail

Both Constitution and AGENTS.md are sourced from spec.md and plan.md but serve different purposes:
- **Constitution**: High-level project rules and constraints (what to use)
- **AGENTS.md**: Concrete code examples and verification checklists (how to code)

## Execution Steps

### 1. Read Constitution

Load current constitution from `.specify/memory/constitution.md`

### 2. Read Source Documents

Read **BOTH** spec.md AND plan.md:
- **spec.md**: User requirements, technical decisions
- **plan.md**: Architectural decisions, implementation constraints

**Rationale**:
- spec.md contains user-facing requirements → constraints (e.g., "must use bcrypt")
- plan.md contains technical/architectural decisions → constraints (e.g., "files ≤300 LOC")
- Both contribute to project rules in Section IX

### 2.5. Adaptive Constraint Extraction (Always Complex)

**This workflow always uses sub-agents** (constitution extraction is inherently multi-dimensional).

**Step 1: Detect AGENTS.md Files**

```bash
# Check which AGENTS.md files exist
AGENTS_ROOT=$([ -f "AGENTS.md" ] && echo "1" || echo "0")
AGENTS_FRONTEND=$([ -f "frontend/AGENTS.md" ] && echo "1" || echo "0")
AGENTS_BACKEND=$([ -f "backend/AGENTS.md" ] && echo "1" || echo "0")
AGENTS_TOTAL=$((AGENTS_ROOT + AGENTS_FRONTEND + AGENTS_BACKEND))
```

**Step 2: Apply Agent Strategy**

Based on existing files:

**IF AGENTS_TOTAL = 0** (No AGENTS.md files):
  - Launch 2 sub-agents in PARALLEL (single message with 2 Task calls):
    1. **Constraint_Extraction_Agent**:
       ```
       Task: "Extract project-specific constraints from spec.md and plan.md for Constitution Section IX"

       Workflow:
       1. Read both spec.md and plan.md
       2. Search for constraint keywords ("must use", "required", "forbidden", "≥", "≤")
       3. Categorize: Technology Stack, Dependencies, Architecture, Security, Performance
       4. Format for Section IX
       5. Return: Structured constraints with categories
       ```

    2. **Validation_Agent**:
       ```
       Task: "Validate extracted constraints for conflicts and completeness"

       Workflow:
       1. Check for contradictions between spec and plan
       2. Verify all constraints have clear criteria
       3. Ensure EARS compliance for requirements
       4. Flag ambiguous constraints
       5. Return: Validation report with conflicts and warnings
       ```

**IF AGENTS_TOTAL > 0** (AGENTS.md files exist):
  - Launch 3 sub-agents in PARALLEL (single message with 3 Task calls):
    1. Constraint_Extraction_Agent (as above)
    2. **AGENTS_Rules_Agent**:
       ```
       Task: "Generate project-specific coding rules for existing AGENTS.md files"

       Workflow:
       1. Detect which AGENTS.md files exist (root, frontend/, backend/)
       2. Extract coding patterns from plan.md
       3. Find concrete examples from existing code
       4. Distribute rules appropriately:
          - Root: Cross-cutting (API contracts, auth flow, data formats)
          - Frontend: State management, component patterns, UI rules
          - Backend: Database access, API implementation, external services
       5. Ensure 300-500 tokens per file
       6. Link all rules to source (FR-XXX/STEP-XXX)
       7. Return: Rules per file with token counts
       ```

    3. Validation_Agent (as above)

**CRITICAL**: Always launch agents in PARALLEL (single message with multiple Task calls).

**Debug Output** (for transparency):
```json
{
  "agents_md_detected": {
    "root": true,
    "frontend": true,
    "backend": false,
    "total": 2
  },
  "agents_spawned": 3,
  "tasks": [
    "Constraint extraction for Section IX",
    "Rules generation for 2 AGENTS.md files",
    "Validation of constraints and rules"
  ]
}
```

### 2.6. Synthesize Results

**Merge findings from all agents**:
- Constraints from Constraint_Extraction_Agent
- Rules from AGENTS_Rules_Agent (if spawned)
- Validation warnings from Validation_Agent
- Resolve any conflicts identified
- Prepare final content for Constitution Section IX and AGENTS.md files

### 3. AI-Driven Constraint Extraction

**Use AI to extract constraints from anywhere in documents** (not limited to specific sections):

Prompt for AI:
```
Read the following documents and extract project-specific constraints for Constitution Section IX.

**spec.md**:
{spec_content}

**plan.md**:
{plan_content}

Extract constraints in these categories:

**Technology Stack**:
✅ Required: Languages, frameworks, minimum versions
❌ Forbidden: Prohibited technologies, patterns

**Dependencies**:
✅ Required: Essential libraries, tools, services
❌ Forbidden: Prohibited dependencies

**Architecture**:
✅ Required: Mandatory patterns, file limits, complexity limits
❌ Forbidden: Anti-patterns, prohibited structures

**Security**:
✅ Required: Authentication methods, encryption, validation rules
❌ Forbidden: Security anti-patterns

**Performance**:
✅ Required: Response time limits, throughput requirements
❌ Forbidden: Performance anti-patterns

**Instructions**:
- Extract constraints from ANYWHERE in the documents (not just specific sections)
- Look for phrases: "must use", "required", "forbidden", "shall not", "prohibited"
- Look for version requirements: ">= 18", "≥ 13.0"
- Look for architectural decisions: "files ≤500 SLOC", "functions ≤100 lines"
- Ignore user-facing features (those belong in spec, not constitution)
- Write in ENGLISH only

Output format:
```markdown
## IX. Project-Specific Constraints

*Auto-generated by `/ms.constitution` from spec.md and plan.md on {date}*

### Technology Stack

✅ **Required**:
- {constraint 1}
- {constraint 2}

❌ **Forbidden**:
- {constraint 1}

### Dependencies

...
```
```

### 4. Merge with Existing Section IX

**IF Section IX already exists in constitution**:
- Extract existing constraints
- Merge with newly extracted constraints
- Deduplicate (keep newer version on conflict)
- Preserve manual additions (constraints not from spec/plan)

**Merge Logic**:
```typescript
function mergeConstraints(existing: Constraint[], extracted: Constraint[]): Constraint[] {
  const merged = [...existing];

  for (const newConstraint of extracted) {
    const existingIndex = merged.findIndex(c =>
      c.category === newConstraint.category &&
      similarText(c.text, newConstraint.text) > 0.8  // 80% similarity
    );

    if (existingIndex === -1) {
      // New constraint - add it
      merged.push(newConstraint);
    } else {
      // Duplicate - keep newer (extracted from latest spec/plan)
      merged[existingIndex] = newConstraint;
    }
  }

  return merged;
}
```

### 5. Extract Project-Specific Rules for AGENTS.md

**After extracting Constitution constraints, extract project-specific coding rules for AGENTS.md files**

#### Target Files (Auto-detect)

Distribute rules to existing AGENTS.md files only:

1. **Root AGENTS.md** (always update if exists)
   - Cross-cutting rules: API contracts, auth flow, data formats

2. **frontend/AGENTS.md** (if `frontend/` directory exists)
   - Frontend-specific: State management, component patterns, UI rules

3. **backend/AGENTS.md** (if `backend/` directory exists)
   - Backend-specific: Database access, API implementation, external services

**IMPORTANT**: Only update existing AGENTS.md files. Do NOT create new ones.

#### What to Extract per File

**Root AGENTS.md** (cross-cutting):
- API contracts both sides must follow
- Authentication/Authorization flow
- Shared data formats (JSON schemas)
- Error code conventions

**frontend/AGENTS.md** (if exists):
- State management patterns (Redux, Zustand, etc.)
- Component structure rules
- API client configuration
- UI/UX constraints from spec

**backend/AGENTS.md** (if exists):
- Database access patterns (repository, ORM usage)
- API endpoint implementation
- External service integrations (Stripe, SendGrid, etc.)
- Background job patterns

**✅ Extract**: Tech stack, architecture patterns, security rules, performance targets
**❌ Don't Extract**: Business logic, generic principles, timelines, non-coding decisions

#### Token Budget Constraint

**Per AGENTS.md file**: 300-500 tokens

**If exceeding limit**: Remove least critical categories or shorten examples

#### Format (Same for All AGENTS.md Files)

Add at END of each AGENTS.md:

```markdown
---

## 🎯 Project-Specific Rules

> Source: spec.md, plan.md | Updated: {DATE}

### {Category}
**{Rule Name}** (spec: FR-XXX or plan: STEP-XXX)
```{language}
# Code example (≤10 lines)
```
Check: [ ] {Verification point}

---
```

**Per Rule**: One sentence + 5-10 line code + source link (FR-XXX/STEP-XXX) + 1-2 checks

#### AI Extraction Prompt

```
Extract project-specific coding rules from spec.md and plan.md.
Distribute to AGENTS.md files (if they exist):

1. Root AGENTS.md - Cross-cutting (API contracts, auth flow)
2. frontend/AGENTS.md - Frontend-specific (state, components, UI)
3. backend/AGENTS.md - Backend-specific (database, API, services)

**Documents**:
{spec_content}
{plan_content}

**Requirements per file**:
- 300-500 tokens each
- Link to source (FR-XXX/STEP-XXX)
- Format: Category > Rule > Code (≤10 lines) > Check
- Only relevant rules (no forced distribution)

**Example** (spec: "JWT auth with 1h expiry"):

Root AGENTS.md:
### Authentication Flow
**JWT Tokens** (FR-AUTH-001)
- Access: 1h expiry
- Refresh: 30d expiry

frontend/AGENTS.md:
### API Client
**Auth Headers** (FR-AUTH-001)
```typescript
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
```
Check: [ ] Token auto-refresh on 401

backend/AGENTS.md:
### Authentication
**JWT Config** (FR-AUTH-001)
```python
ACCESS_TOKEN_EXPIRE = 3600  # 1h
```
Check: [ ] Tokens signed with JWT_SECRET

**Report per file**: Token count, rules added
```

#### AGENTS.md Update Process

For each existing AGENTS.md file (root, frontend/, backend/):

1. **Check if file exists** (skip if not)
2. **Check for "🎯 Project-Specific Rules" section**
   - If exists: Replace entire section
   - If not: Append to end
3. **Extract rules** using AI prompt
4. **Validate**: 300-500 tokens, source links, ≤10 line code
5. **Update file**

### 6. Update Constitution

Replace or create Section IX with merged constraints:

```markdown
## IX. Project-Specific Constraints

*Auto-generated by `/ms.constitution` from spec.md and plan.md on 2025-10-10*

### Technology Stack

✅ **Required**:
- Node.js ≥18
- TypeScript with strict mode
- Vitest for testing

❌ **Forbidden**:
- AST parsers (use regex instead)
- Complex frameworks without justification

### Dependencies

✅ **Required**:
- ripgrep ≥13.0 for TAG operations
- ESLint with zero-warnings policy

❌ **Forbidden**:
- Unnecessary external dependencies

### Architecture

✅ **Required**:
- Files ≤500 SLOC (code files - docs have no limit)
- Functions ≤100 lines
- Complexity ≤10 per function
- AST parsers allowed following safety models (read-only, sandboxed, etc.)

### Security

✅ **Required**:
- `.env` must be in `.gitignore`
- Input validation for all user inputs
- bcrypt for password hashing

### Performance

✅ **Required**:
- API response time < 200ms (p95)
- Database queries < 100ms
```

### 7. Create Root AGENTS.md (Optional)

**IF root `AGENTS.md` does NOT exist**, create it now:

**Create**: `AGENTS.md`

**Content** (use Constitution as reference):

```markdown
# AI Coding Assistant Rules (AGENTS.md)

*Auto-generated by `/ms.constitution` on {DATE}*

## Documentation Reference

**CRITICAL**: Read Constitution before any coding task:
- `.specify/memory/constitution.md` - Project rules (EARS, TRUST, TAG, Section IX constraints)

**Workflow Documents** (if working on specific feature):
- `specs/[spec-id]/spec.md` - Feature specification
- `specs/[spec-id]/plan.md` - Implementation plan
- `specs/[spec-id]/tasks.md` - Task list with TAG IDs

**Living Documents** (if reviewing implemented features):
- `docs/api/[TAG-ID].md` - Auto-generated API documentation

## Core Principles (from Constitution)

### Code Quality (TRUST 5 Principles)
- **Test First**: Coverage ≥85%, TDD Red-Green-Refactor
- **Readable**: File ≤500 SLOC, Function ≤100 LOC, Complexity ≤10
- **Unified**: TypeScript strict mode, zero linting warnings
- **Secured**: Input validation, .env in .gitignore
- **Trackable**: TAG blocks in all code (@SPEC → @TEST → @CODE)

### Simplicity-First Architecture
- Avoid premature optimization
- Prefer simple solutions over clever ones
- Composition over inheritance

### Requirements (EARS Format)
- All requirements use EARS keywords: WHEN/WHILE/WHERE/IF/System SHALL
- Korean input → English EARS output

## Project-Specific Rules (Section IX)

[Auto-extracted from Constitution Section IX]

{SECTION_IX_CONTENT}

## Development Workflow

1. Read Constitution Section IX for project constraints
2. Read spec.md and plan.md for feature context
3. Write tests first (TDD)
4. Implement with TAG blocks
5. Run linting and type checking
6. Verify coverage ≥85%

---

*This file is auto-generated. Manual edits will be preserved during updates.*
```

**Placeholder Replacement**:
- `{DATE}` → Current date
- `{SECTION_IX_CONTENT}` → Copy Constitution Section IX content (just the constraints, not the full section)

**IF root AGENTS.md already exists**:

1. **Search for Section 14 header**:
   ```bash
   grep -n "^## 14\. Project-Specific Rules" AGENTS.md
   ```

2. **IF Section 14 found**:
   - Read AGENTS.md
   - Find Section 14 start: `## 14. Project-Specific Rules (Section IX)`
   - Find Section 14 end: Next `## 13.` line or `---` separator
   - **Replace content** between start and end with updated {SECTION_IX_CONTENT}
   - Use Edit tool with old_string (entire Section 14) → new_string (updated Section 14)

3. **IF Section 14 NOT found**:
   - Read AGENTS.md
   - Find insertion point: Before final `---` separator or before Section 13
   - **Insert new Section 14**:
     ```markdown
     ## 14. Project-Specific Rules (Section IX)

     [This section is auto-populated by `/ms.constitution` from Constitution Section IX]

     {SECTION_IX_CONTENT}

     ---
     ```
   - Use Edit tool to insert at appropriate location

**IF AGENTS.md does NOT exist**: Create new file with full template (Section 1-10)

### 8. Report Output

```json
{
  "constraints_extracted": {
    "from_spec": 12,
    "from_plan": 8,
    "total_new": 15,
    "merged_duplicates": 5
  },
  "agents_md_created": true,
  "section_ix_updated": true,
  "constitution_path": ".specify/memory/constitution.md",
  "agents_md_path": "AGENTS.md"
}
```

Display (in KOREAN):
```
✅ Constitution Section IX + AGENTS.md 생성 완료!

📊 제약사항 추출 (Constitution Section IX):
- spec.md에서: 12개
- plan.md에서: 8개
- 신규 추가: 15개
- 중복 병합: 5개

📄 업데이트된 파일:
- ✅ .specify/memory/constitution.md (Section IX 완성)
- ✅ AGENTS.md (프로젝트 코딩 규칙)

🎯 다음 단계:
1. Constitution Section IX 검토
2. AGENTS.md 검토
3. `/ms.tasks` 실행 (implementation tasks 생성)

💡 참고:
- AI 에이전트는 AGENTS.md를 통해 Constitution을 자동 참조합니다
- Living Documents는 `/ms.implement` 실행 시 자동 생성됩니다
```

## Error Handling

### Error 1: Constitution Not Found

**Symptom**: `.specify/memory/constitution.md` missing

**Message**:
```
❌ Error: Constitution not found

Expected: .specify/memory/constitution.md

Please run `/ms.init` first to create the project Constitution.
```

**Exit**: Code 1

### Error 2: Spec or Plan Not Found

**Symptom**: spec.md or plan.md doesn't exist

**Message**:
```
❌ Error: Source documents not found

Required files:
- specs/{SPEC_ID}/spec.md (missing)
- specs/{SPEC_ID}/plan.md (missing)

Please run:
1. `/ms.specify` to create spec.md
2. `/ms.plan` to create plan.md

Then re-run `/ms.constitution`
```

**Exit**: Code 1

### Error 3: No Constraints Found

**Symptom**: AI extracts 0 constraints from spec.md and plan.md

**Message**:
```
⚠️ Warning: No project-specific constraints found

spec.md and plan.md do not contain explicit constraints.

Common missing constraints:
- Technology stack (Node.js version, Python version)
- Required dependencies (libraries, tools)
- Architectural decisions (file size limits, patterns)
- Security requirements (authentication method, encryption)

Would you like to:
1. Manually add constraints to spec.md or plan.md and re-run `/ms.constitution`
2. Keep Section IX empty (use default Constitution only)
3. Skip Section IX generation
```

**Action**: Prompt user for choice

### Error 4: Conflicting Constraints

**Symptom**: spec.md says "Use PostgreSQL", plan.md says "Use MongoDB"

**Message**:
```
⚠️ Constraint Conflict Detected

spec.md: "Required: PostgreSQL database"
plan.md: "Required: MongoDB database"

Please resolve the conflict:
1. Edit spec.md or plan.md to remove conflict
2. Re-run `/ms.constitution` after resolution

Proceeding with latest (plan.md) constraint for now.
```

**Action**: Use plan.md constraint (as it's more recent in workflow)

### Error 5: No AGENTS.md Files Found

**Symptom**: None of the AGENTS.md files exist (root, frontend/, backend/)

**Message**:
```
⚠️ Warning: No AGENTS.md files found

Checked:
- AGENTS.md (not found)
- frontend/AGENTS.md (not found)
- backend/AGENTS.md (not found)

Skipping project-specific rules extraction.
Constitution Section IX will still be updated.

To enable AGENTS.md updates:
1. Create at least one AGENTS.md file
2. Re-run `/ms.constitution`
```

**Action**: Continue with Constitution update only

### Error 6: Token Budget Exceeded (Per File)

**Symptom**: Extracted rules for a file exceed 500 tokens

**Message**:
```
⚠️ Token Budget Exceeded: backend/AGENTS.md

Extracted rules: 720 tokens (limit: 500)

Auto-trimming to fit budget:
- Removed: Performance Monitoring (80 tokens)
- Removed: Error Handling (90 tokens)
- Final: 450 tokens

Review backend/AGENTS.md and manually add removed categories if needed.
```

**Action**: Auto-trim least critical categories per file to fit budget

## Next Steps

After `/ms.constitution`:
1. Review Constitution Section IX (project constraints)
2. Review AGENTS.md (project-specific coding rules)
3. Run `/ms.tasks` to generate implementation tasks with TAG IDs
4. Constitution + Agent Rules now complete ✅

**Note**: `/ms.constitution` must run AFTER `/ms.plan` (plan.md is required for constraint extraction)

## Notes

### Constitution (Section IX)
- **AI-driven extraction**: No rigid section structure required
- **Sources**: spec.md + plan.md
- **Merge strategy**: Preserves manual additions, deduplicates, keeps newer
- **Scope**: Project-specific constraints (Sections I-XIII are universal)

### AGENTS.md (Project-Specific Rules)
- **Multi-file support**: Root, frontend/, backend/ (auto-detect)
- **Token budget**: 300-500 per file (strictly enforced)
- **Content**: Coding patterns only (no business logic)
- **Source tracking**: All rules linked to FR-XXX/STEP-XXX
- **Update strategy**: Replace "🎯 Project-Specific Rules" section (idempotent)
- **No file creation**: Only update existing AGENTS.md files

## Implementation Details

**Contract**: [specs/001-my-spec-spec/contracts/ms-constitution.json](../specs/001-my-spec-spec/contracts/ms-constitution.json)

**Tools**:
- Read: spec.md, plan.md, constitution.md, AGENTS.md (root, frontend/, backend/)
- Edit: constitution.md (Section IX), AGENTS.md files (Project-Specific Rules section)

**File Size Targets**:
- Constitution Section IX: ≤200 lines (base template excluded)
- Each AGENTS.md Project Rules: 300-500 tokens (≈60-100 lines)

**Processing Order**:
1. Extract Constitution constraints (Section IX)
2. Auto-detect existing AGENTS.md files
3. Extract rules for each detected file
4. Update Constitution
5. Update AGENTS.md files
6. Report combined results

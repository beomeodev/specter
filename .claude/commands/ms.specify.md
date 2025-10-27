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

### 3. Run Base Specify Command

#### 3.1. Handle Attached Document Scenarios

**BEFORE executing `/speckit.specify`**, check if user provided feature requirements via attached document instead of inline `$ARGUMENTS`:

**Detection**:
- User message contains file attachments (e.g., `.md`, `.txt`, `.pdf`)
- User refers to "attached document", "see the file", or similar phrases
- `$ARGUMENTS` is empty or only contains file reference

**When attached document detected**:

1. **Read the attached document** to understand feature requirements
2. **Analyze document content** for context and intent
3. **Generate branch name** (2-4 words) based on document CONTENT, NOT filename

**Branch Naming Rules**:

```
❌ BAD: Using filename as branch name
- Filename: "feature-requirements-draft-v3-final.md"
- Branch: "feature-requirements-draft-v3-final" (meaningless)

✅ GOOD: Deriving branch name from content
- Document describes: "Implement user authentication with OAuth2 and JWT"
- Branch: "oauth-jwt-auth" (concise, descriptive)
```

**Process**:

```python
# Step 1: Detect attached document
if user_attached_file and not $ARGUMENTS:
    # Step 2: Read document
    document_content = Read(attached_file_path)

    # Step 3: Extract feature intent from content
    # Look for: title, main requirements, key features
    feature_intent = extract_main_feature(document_content)

    # Step 4: Generate concise branch name (2-4 words)
    # - Focus on WHAT the feature does, not the document name
    # - Use kebab-case
    # - Keep it short and descriptive
    branch_name = generate_branch_name(feature_intent)

    # Step 5: Use content as $ARGUMENTS for /speckit.specify
    $ARGUMENTS = document_content
```

**Example**:

```
User: "I've attached a document describing the feature I want to implement"
Attached: "project-planning-notes-2024.md"

Document content:
---
# Real-time Notification System
Implement WebSocket-based real-time notifications for user events...
---

AI Processing:
1. Reads document ✓
2. Identifies main feature: "Real-time notification system via WebSocket"
3. Generates branch name: "realtime-websocket-notifications"
4. Passes full document content to /speckit.specify
```

**Common Pitfalls to Avoid**:

| Anti-Pattern | Why It's Wrong | Correct Approach |
|-------------|----------------|------------------|
| Use filename directly | Filenames often contain metadata, not intent | Parse document content for feature description |
| Skip reading document | Loses context and requirements | Always read and analyze document first |
| Generate generic names | "feature-123", "new-feature" | Extract specific feature purpose from content |

#### 3.2. Execute Speckit Specify

Execute `/speckit.specify` with Constitution-enhanced context:

```
/speckit.specify $ARGUMENTS
```

**Agent Delegation**: This internally uses the **spec-builder** agent (Sonnet model) for EARS pattern conversion and SPEC document generation.

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

## Next Command

After `/ms.specify`:
1. Run `/ms.clarify` to clarify ambiguous requirements (질의응답 방식)
2. OR run `/ms.checklist` to generate completeness checklist (체크리스트 방식)
3. Then proceed to `/ms.plan` for implementation planning

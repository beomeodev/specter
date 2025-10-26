# My-Spec Skills Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-26
**Status**: Planned (Phase 2)

---

## Overview

Skills are Progressive Disclosure knowledge modules that provide Constitution enforcement, best practices, and workflow automation for My-Spec. Based on MoAI-ADK's proven architecture, Skills optimize context usage by loading information in 3 levels.

**Total Skills**: 11 across 4 tiers
**Context Reduction**: 40% (from 100% to 60%)
**Loading Strategy**: Metadata → Instructions → Resources

---

## Progressive Disclosure Architecture

### Level 1: Metadata (Loaded at session start, ≤100 tokens per Skill)

```yaml
---
name: ms-foundation-constitution
tier: foundation
description: Constitution auto-validation (file size, EARS, TRUST)
triggers: ["code review request", "file modification"]
size: ~400 LOC
model: haiku
---
```

**Purpose**: Quick reference for agent skill selection
**Load Time**: Session start (all 11 Skills metadata)
**Token Cost**: ~1100 tokens total (11 × 100)

### Level 2: Instructions (Loaded when agent references, ≤2000 tokens per Skill)

```markdown
## When to Use
- Code writing requires Constitution compliance check
- File size ≤500 SLOC validation

## Quick Start
1. Read Constitution file
2. Check file size against limits
3. Report violations

## Example
```python
from constitution_validator import check_file_size
result = check_file_size("src/auth.py")
if not result.passed:
    print(f"Violation: {result.message}")
```
```

**Purpose**: Skill usage instructions and examples
**Load Time**: When agent explicitly references Skill by name
**Token Cost**: ≤2000 tokens per referenced Skill

### Level 3: Resources (Loaded when execution needed, ≤5000 tokens per Skill)

```python
# check_file_size.py
def check_file_size(file_path: str) -> dict:
    """Validate file size against Constitution limits"""
    sloc = count_sloc(file_path)
    limit = 500

    return {
        "passed": sloc <= limit,
        "sloc": sloc,
        "limit": limit,
        "message": f"File size: {sloc} SLOC (limit: {limit})"
    }
```

**Purpose**: Executable code, YAML configs, validation scripts
**Load Time**: When Skill actually executes logic
**Token Cost**: ≤5000 tokens per executed Skill

---

## Skill Tiers

### Foundation Tier (5 Skills)

**1. ms-foundation-constitution**
- **Purpose**: File size, EARS, TRUST validation
- **Model**: Haiku
- **Size**: ~400 LOC
- **Triggers**: Code review, file modification
- **Functions**:
  - `check_file_size(file_path)` - Validate ≤500 SLOC
  - `check_complexity(file_path)` - Validate ≤10 per function
  - `check_ears_compliance(spec)` - Validate EARS patterns

**2. ms-foundation-trust**
- **Purpose**: TRUST 5 principles validation
- **Model**: Haiku
- **Size**: ~450 LOC
- **Triggers**: `/ms.analyze`, code review
- **Functions**:
  - `validate_test_coverage(project)` - Check ≥85% coverage
  - `validate_readability(file)` - Check function size, nesting
  - `validate_unified(project)` - Check type safety, linting

**3. ms-foundation-ears**
- **Purpose**: EARS pattern validation, forbidden phrases
- **Model**: Haiku
- **Size**: ~250 LOC
- **Triggers**: SPEC writing, `/ms.specify`
- **Resources**:
  - `patterns.yaml` - 5 EARS patterns with examples
  - `forbidden_phrases.yaml` - Ambiguous terms to avoid

### Workflow Tier (2 Skills)

**4. ms-workflow-tag-manager**
- **Purpose**: TAG block templates, auto-insertion
- **Model**: Haiku
- **Size**: ~300 LOC
- **Triggers**: Code generation, `/ms.implement`
- **Resources**:
  - `tag_templates.json` - Python/TypeScript TAG block formats
- **Functions**:
  - `generate_tag_block(lang, tag_id, spec_path, test_path)` - Create TAG
  - `insert_tag_block(file_path, tag_block)` - Insert at file top

**5. ms-workflow-living-docs**
- **Purpose**: API doc generation from TAGs
- **Model**: Haiku
- **Size**: ~350 LOC
- **Triggers**: Code modification, `/ms.up-docs`
- **Functions**:
  - `scan_tags(cwd)` - Find all @CODE tags via ripgrep
  - `generate_api_doc(tag)` - Extract function signature, docstring

### Essentials Tier (2 Skills - subset of MoAI's 4)

**6. ms-essentials-debug**
- **Purpose**: Stack trace analysis, root cause identification
- **Model**: Haiku
- **Size**: ~300 LOC
- **Triggers**: Error occurs
- **Functions**:
  - `analyze_stack_trace(error)` - Parse error message
  - `suggest_fix(error)` - Provide actionable suggestions

**7. ms-essentials-review**
- **Purpose**: Code review checklist, best practices
- **Model**: Haiku
- **Size**: ~300 LOC
- **Triggers**: `/ms.review`, PR creation
- **Resources**:
  - `review_checklist.yaml` - Constitution compliance checks

### Language Tier (2 Skills)

**8. ms-lang-typescript**
- **Purpose**: TypeScript best practices
- **Model**: Haiku
- **Size**: ~200 LOC
- **Triggers**: Editing .ts, .tsx files
- **Resources**:
  - TypeScript strict mode guidelines
  - ESLint configuration examples
  - Good vs Bad code patterns

**9. ms-lang-python**
- **Purpose**: Python best practices
- **Model**: Haiku
- **Size**: ~200 LOC
- **Triggers**: Editing .py files
- **Resources**:
  - mypy strict mode guidelines
  - Black formatting examples
  - pytest best practices

---

## Skill Directory Structure

```
.claude/skills/
├── ms-foundation-constitution/
│   ├── SKILL.md                 # Level 1-2 (metadata + instructions)
│   ├── check_file_size.py       # Level 3 (executable)
│   └── check_complexity.py      # Level 3
├── ms-foundation-trust/
│   ├── SKILL.md
│   └── trust_validator.py
├── ms-foundation-ears/
│   ├── SKILL.md
│   └── patterns.yaml
├── ms-workflow-tag-manager/
│   ├── SKILL.md
│   └── tag_templates.json
├── ms-workflow-living-docs/
│   ├── SKILL.md
│   └── doc_templates/
├── ms-essentials-debug/
│   └── SKILL.md
├── ms-essentials-review/
│   ├── SKILL.md
│   └── review_checklist.yaml
├── ms-lang-typescript/
│   └── SKILL.md
└── ms-lang-python/
    └── SKILL.md
```

---

## Usage Examples

### Example 1: Auto-Loaded Metadata (Session Start)

```
Claude Code session starts
  ↓
Load all 11 Skills metadata (~1100 tokens)
  ↓
Agent has quick reference:
  - "ms-foundation-constitution" for file size validation
  - "ms-workflow-tag-manager" for TAG insertion
  - etc.
```

### Example 2: On-Demand Instructions

```
Agent task: "Validate file size against Constitution"
  ↓
Agent references: "ms-foundation-constitution"
  ↓
Load Level 2 (instructions): "When to Use", "Quick Start", examples (~2000 tokens)
  ↓
Agent understands how to use the Skill
```

### Example 3: Execution

```
Agent needs to execute: check_file_size("src/auth.py")
  ↓
Load Level 3 (resources): check_file_size.py code (~500 tokens)
  ↓
Execute function: check_file_size("src/auth.py")
  ↓
Return: {"passed": False, "sloc": 650, "limit": 500, "message": "File exceeds limit"}
```

---

## Implementation Status

**Phase 2 Status**: ⚪ PENDING (Not yet started)

**Timeline**:
- Week 4: Foundation Skills (3 Skills)
- Week 5: Workflow Skills (2 Skills)
- Week 6: Essentials + Language Skills (4 Skills)

**Estimated Effort**: 17-24 hours

---

## Best Practices

### 1. Keep Skill Size Small

**Guideline**: Each Skill ≤500 SLOC (Constitution Section II)

**Example**:
- ✅ Good: `ms-foundation-ears` (250 LOC)
- ❌ Bad: Monolithic skill with 1000+ LOC

### 2. Follow Progressive Disclosure

**Guideline**: Don't load all resources upfront

**Example**:
```python
# ❌ Bad: Load everything at session start
def load_skill():
    metadata = read_yaml()
    instructions = read_markdown()
    resources = read_all_py_files()  # Wasteful!
    return {**metadata, **instructions, **resources}

# ✅ Good: Load on-demand
def load_skill_metadata():
    return read_yaml()  # Minimal, fast

def load_skill_instructions():
    return read_markdown()  # When referenced

def load_skill_resources():
    return read_py_files()  # When executed
```

### 3. Use Haiku Model for Speed

**Guideline**: Skills use Haiku model for fast, cost-efficient execution

**Rationale**:
- Skills are validation/automation tasks (not complex reasoning)
- Haiku: Fast, cheap, sufficient for rule-based logic
- Sonnet/Opus: Reserved for sub-agents (complex reasoning)

### 4. Reference Constitution Directly

**Guideline**: Skills should read Constitution at runtime, not duplicate content

**Example**:
```python
# ❌ Bad: Duplicate limit in Skill
FILE_SIZE_LIMIT = 500  # Duplicates Constitution

# ✅ Good: Read from Constitution
def get_file_size_limit():
    constitution = read_file(".specify/memory/constitution.md")
    # Parse: "Files ≤500 SLOC"
    return extract_sloc_limit(constitution)
```

---

## Troubleshooting

### Issue 1: Skill Not Loading

**Symptom**: Agent doesn't find Skill by name

**Solution**:
1. Verify SKILL.md exists: `ls .claude/skills/ms-foundation-*/SKILL.md`
2. Check YAML frontmatter has correct `name:` field
3. Ensure session restarted after Skill creation

### Issue 2: Context Usage Not Reduced

**Symptom**: Context usage still 100% after Progressive Disclosure

**Diagnosis**:
```bash
# Check if Skills loading all levels at once
# Review agent logs for Skill loading behavior
```

**Solution**:
1. Verify Progressive Disclosure logic in Skill loader
2. Ensure Level 3 (resources) only loaded when needed
3. Measure token usage per level

---

## References

- [Migration Guide](../migration/moai-integration-guide.md)
- [MoAI-ADK Skills Documentation](https://github.com/modu-ai/moai-adk)
- [Claude Code Skills Specification](https://docs.claude.com/ko/docs/claude-code/skills)
- [Constitution Template](../../.specify/memory/constitution.md)

---

**Status**: Phase 2 Planning Complete (Implementation pending)

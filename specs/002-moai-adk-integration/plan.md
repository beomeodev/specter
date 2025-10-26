# MoAI-ADK Integration Implementation Plan

**Feature ID**: MOAI-001
**Version**: 1.0.0
**Created**: 2025-10-25
**Status**: Draft
**Priority**: P0 (Critical)

---

## Executive Summary

System SHALL integrate MoAI-ADK's 4 core features (Hooks, Skills, Living-Docs, Sub-Agents) into My-Spec workflow following TDD principles, modular architecture, and TRUST quality standards.

**Key Decisions:**
- Python 3.13+ hooks (MoAI-ADK proven architecture)
- Progressive Disclosure Skills (40% context reduction)
- CODE-FIRST Living-Docs (30min → 2min sync)
- Direct Context7 MCP (no Gemini delegation)

**Success Criteria:**
- ≥85% test coverage (Constitution Section I)
- Zero breaking changes to existing `/ms.*` commands
- File sizes ≤500 SLOC (Constitution Section II)
- Performance: Hooks <100ms, Living-Docs <10min

---

## 1. Architecture Overview

### 1.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: COMMANDS (User Interface)                          │
│ /ms.specify → /ms.plan → /ms.implement → /ms.up-docs → /fin │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│ Layer 2: SUB-AGENTS (11 total: 6 existing + 5 new)          │
│ spec-builder, implementation-planner, tdd-implementer,       │
│ doc-updater, tag-auditor, trust-validator, etc.             │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│ Layer 3: SKILLS (11 total, Progressive Disclosure)          │
│ ms-foundation-*, ms-workflow-*, ms-lang-*                    │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│ Layer 4: HOOKS (4 events, Python 3.13+)                     │
│ SessionStart, PreToolUse, PostToolUse, UserPromptSubmit     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│ FOUNDATION: Constitution.md (Single Source of Truth)        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Dependency Graph

**Phase Dependencies:**
- Phase 0 (Preparation) → Phase 1 (Hooks) → Phase 2 (Skills) → Phase 3 (Living-Docs) → Phase 4 (Sub-Agents)

**Layer Dependencies:**
- Hooks: Constitution.md only (independent)
- Skills: Constitution.md (REQUIRED), Hooks (OPTIONAL)
- Living-Docs: doc-updater agent, ms-workflow-living-docs Skill, TAG system
- Sub-Agents: Skills, Hooks (for context injection)

### 1.3 Path Mapping (MoAI → My-Spec)

| MoAI Path | My-Spec Path | Rationale |
|-----------|--------------|-----------|
| `.moai/checkpoints.log` | `.specify/checkpoints.log` | Co-locate with Constitution |
| `.moai/config.json` | `.specify/memory/constitution.md` | Use existing Constitution |
| `.moai/memory/*.md` | `.specify/memory/*.md` | Existing memory structure |
| `.moai/specs/` | `specs/` | Root-level specs (existing) |
| `.moai/hooks/alfred/` | `.claude/hooks/ms/` | My-Spec naming convention |

**Verification Command:**
```bash
rg "\.moai" .claude/hooks/ms/ -n  # MUST return 0 results
```

### 1.4 Technology Stack

**Required Dependencies:**
- Python ≥3.13 (MANDATORY - no backward compatibility)
- pytest ≥7.0, pytest-cov (test framework)
- ripgrep (TAG scanning)
- Git ≥2.30 (checkpoints, diff analysis)
- Prettier (TypeScript formatting)
- Black (Python formatting)

**MCP Servers:**
- ✅ Context7 MCP (library documentation)
- ❌ cli-bridge MCP (REMOVED - Gemini delegation deprecated)

---

## 2. Detailed Design

### 2.1 Phase 0: Migration Preparation (Week 0.5, 4h)

**Objective**: Prepare environment and validate prerequisites.

**Tasks:**

#### Phase 0.1: Environment Validation (1h)
```bash
# Validate Python 3.13+
python3 --version | grep -E "3\.(1[3-9]|[2-9][0-9])" || exit 1

# Install dependencies
pip install pytest pytest-cov black

# Verify ripgrep
rg --version

# Verify Git
git --version
```

#### Phase 0.2: Existing Hooks Documentation (1h)
- Document `constitution-injector.sh` functionality (Task tool → Constitution injection)
- Document `tag-enforcer.ts` functionality (@IMMUTABLE protection)
- Identify unused hooks (`notify.sh` - likely delete)

#### Phase 0.3: Directory Structure Setup (1h)
```bash
# Create hook structure
mkdir -p .claude/hooks/ms/{core,handlers}
mkdir -p tests/hooks

# Create Skills structure
mkdir -p .claude/skills

# Create checkpoints log
mkdir -p .specify
touch .specify/checkpoints.log
```

#### Phase 0.4: Backup and Path Mapping (1h)
```bash
# Create backup branch
git checkout -b backup-pre-moai-integration
git tag pre-moai-v1.0.0

# Scan for hardcoded .moai paths
rg "\.moai" -n  # Should return 0 in My-Spec code
```

**Acceptance Criteria:**
- [ ] Python 3.13+ confirmed
- [ ] pytest installed and working
- [ ] All 3 existing hooks documented
- [ ] Directory structure created
- [ ] Backup branch created

---

### 2.2 Phase 1: Hooks Implementation (Week 1-3, 25-32h)

**Objective**: Implement 4 Python hooks following MoAI-ADK architecture.

#### Phase 1.1: SessionStart Hook (Week 1, 6-9h)

**Reference**: `docs/references/moai-adk/.claude/hooks/alfred/handlers/session.py`

**TDD Cycle:**

**RED (2-3h):**
```python
# tests/hooks/test_session_hooks.py
def test_session_start_displays_project_status():
    result = run_hook("SessionStart", {"cwd": "."})
    assert "🚀 My-Spec Session Started" in result["message"]
    assert "Language" in result["message"]
    assert "Git Branch" in result["message"]

def test_session_start_detects_language():
    result = run_hook("SessionStart", {"cwd": "."})
    assert result["language"] in ["python", "typescript", "go", "rust"]

def test_session_start_performance():
    start = time.time()
    run_hook("SessionStart", {"cwd": "."})
    duration = (time.time() - start) * 1000
    assert duration < 100, f"SessionStart took {duration}ms (limit: 100ms)"
```

**GREEN (3-4h):**
- Implement `ms_hooks.py` entry point (CLI args parsing)
- Implement `core/__init__.py` (HookPayload, HookResult classes)
- Implement `core/project.py` (language detection, Git info, SPEC count, TAG integrity)
- Implement `handlers/session.py` (SessionStart handler)

**REFACTOR (1-2h):**
- Apply Fail-open error handling
- Apply path mapping (`.moai` → `.specify`)
- Add performance logging (<100ms check)

**Key Functions (from MoAI reference):**
```python
# core/project.py
def detect_language(cwd: str) -> str:
    """Detect primary language by file extensions"""
    # Count .py, .ts, .go, .rs files
    # Return most common language

def get_git_info(cwd: str) -> dict:
    """Extract Git branch and status"""
    # Run: git branch --show-current
    # Run: git status --porcelain
    # Return: {"branch": str, "clean": bool}

def count_specs(cwd: str) -> dict:
    """Count SPEC files and calculate completion"""
    # Find specs/*/spec.md
    # Calculate completion percentage
    # Return: {"total": int, "completed": int, "percentage": float}

def calculate_tag_integrity(cwd: str) -> float:
    """Scan TAG chains and calculate integrity score"""
    # Run: rg '@(SPEC|TEST|CODE):' -n
    # Verify complete chains
    # Return: percentage (0-100%)
```

**Validation:**
```bash
pytest tests/hooks/test_session_hooks.py -v
pytest --cov=.claude/hooks/ms --cov-report=html
echo '{"cwd": "."}' | python .claude/hooks/ms/ms_hooks.py SessionStart
```

---

#### Phase 1.2: PreToolUse Hook (Week 2, 7-10h)

**Reference**: `docs/references/moai-adk/.claude/hooks/alfred/core/checkpoint.py`

**TDD Cycle:**

**RED (2-3h):**
```python
# tests/hooks/test_pre_tool_use.py
def test_checkpoint_created_before_constitution_edit():
    result = run_hook("PreToolUse", {
        "tool_name": "Edit",
        "tool_input": {"file_path": ".specify/memory/constitution.md"}
    })
    assert result["checkpoint_created"] == True
    assert "checkpoint/before-critical-file-" in result["branch_name"]

def test_checkpoint_created_before_bulk_edit():
    result = run_hook("PreToolUse", {
        "tool_name": "Edit",
        "tool_input": {"edits": [{"file_path": f"file{i}.py"} for i in range(10)]}
    })
    assert result["checkpoint_created"] == True

def test_no_checkpoint_for_safe_operations():
    result = run_hook("PreToolUse", {
        "tool_name": "Read",
        "tool_input": {"file_path": "test.py"}
    })
    assert result["checkpoint_created"] == False
```

**GREEN (4-5h):**
- Implement `core/checkpoint.py` (detect risky operations, create Git branch, log)
- Implement `handlers/tool.py` (PreToolUse handler)

**Key Functions (adapted from MoAI):**
```python
# core/checkpoint.py
def detect_risky_operation(tool_name: str, tool_args: dict, cwd: str) -> tuple[bool, str]:
    """Detect risky operations requiring checkpoint

    Risky operations:
    - Edit/Write: .specify/memory/constitution.md
    - Edit/Write: ≥5 files simultaneously
    - Bash: rm -rf, git merge, git reset --hard
    """
    if tool_name in ("Edit", "Write"):
        file_path = tool_args.get("file_path", "")
        # Check critical files
        if ".specify/memory/constitution.md" in file_path:
            return (True, "critical-file")

        # Check bulk edit
        edits = tool_args.get("edits", [])
        if len(edits) >= 5:
            return (True, "bulk-edit")

    return (False, "")

def create_checkpoint(operation: str, cwd: str) -> str:
    """Create Git checkpoint branch

    Returns: branch name (e.g., "checkpoint/before-constitution-edit-20251025103000")
    """
    timestamp_ns = time.time_ns()
    branch_name = f"checkpoint/before-{operation}-{timestamp_ns}"

    # Create branch
    subprocess.run(["git", "checkout", "-b", branch_name], check=True, cwd=cwd)

    # Log to .specify/checkpoints.log
    log_entry = f"{datetime.now().isoformat()}Z | CHECKPOINT | {operation} | branch: {branch_name}\n"
    with open(f"{cwd}/.specify/checkpoints.log", "a") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        f.write(log_entry)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    return branch_name
```

**REFACTOR (1-2h):**
- Apply Fail-open for Git errors
- Remove `.moai` hardcoded paths
- Add concurrent checkpoint handling (file locking)

**Validation:**
```bash
pytest tests/hooks/test_pre_tool_use.py -v
cat .specify/checkpoints.log  # Verify log format
```

---

#### Phase 1.3: Migrate Existing Hooks (Week 3, 8-9h)

**Tasks:**

**1. constitution-injector.sh → handlers/user.py (2h)**
```python
# handlers/user.py
def handle_user_prompt_submit(payload: dict) -> HookResult:
    """Inject Constitution when Task tool detected"""
    prompt = payload.get("prompt", "")

    # Detect Task tool invocation
    if "Task(" in prompt or "subagent_type=" in prompt:
        # Read Constitution
        constitution_path = Path(".specify/memory/constitution.md")
        if constitution_path.exists():
            constitution = constitution_path.read_text()

            # Inject into prompt
            injected_prompt = f"""# Constitution Context (Auto-Injected)

{constitution[:8000]}

---

{prompt}
"""
            return HookResult(
                continue_execution=True,
                system_message=injected_prompt
            )

    return HookResult(continue_execution=True)
```

**Test:**
```python
def test_constitution_injection_on_task_tool():
    result = run_hook("UserPromptSubmit", {"prompt": "Task(subagent_type='spec-builder')"})
    assert "Constitution Context" in result["system_message"]
```

**2. tag-enforcer.ts → core/tags.py (4-5h)**
```python
# core/tags.py
def scan_immutable_tag(file_path: str) -> bool:
    """Check if file contains @IMMUTABLE tag"""
    try:
        with open(file_path, "r") as f:
            content = f.read()
            return "@IMMUTABLE" in content
    except Exception:
        return False  # Fail-open

def block_immutable_edit(file_path: str) -> HookResult:
    """Block edit if @IMMUTABLE tag found"""
    if scan_immutable_tag(file_path):
        error_msg = f"""❌ IMMUTABLE TAG PROTECTION

File: {file_path}
Reason: This file contains @IMMUTABLE marker

To unlock:
1. Run: /ms.unlock {file_path}
2. Provide justification
3. Edit will be allowed for current session only
"""
        return HookResult(continue_execution=False, system_message=error_msg)

    return HookResult(continue_execution=True)
```

**Test:**
```python
def test_immutable_tag_blocks_edit():
    # Create file with @IMMUTABLE
    test_file = "test_immutable.py"
    Path(test_file).write_text("# @IMMUTABLE: Do not modify\n")

    result = run_hook("PreToolUse", {
        "tool_name": "Edit",
        "tool_input": {"file_path": test_file}
    })
    assert result["continue_execution"] == False
    assert "IMMUTABLE TAG PROTECTION" in result["system_message"]
```

**3. Update settings.local.json (30min)**
```json
{
  "hooks": {
    "sessionStart": ".claude/hooks/ms/ms_hooks.py SessionStart",
    "userPromptSubmit": ".claude/hooks/ms/ms_hooks.py UserPromptSubmit",
    "preToolUse": ".claude/hooks/ms/ms_hooks.py PreToolUse",
    "postToolUse": ".claude/hooks/ms/ms_hooks.py PostToolUse"
  }
}
```

**4. Delete old hooks (30min)**
```bash
rm .claude/hooks/constitution-injector.sh
rm .claude/hooks/tag-enforcer.ts
rm .claude/hooks/notify.sh  # If unused
```

**5. Integration testing (1h)**
- Test all 4 hook events in real Claude Code session
- Verify Constitution injection works
- Verify @IMMUTABLE protection works
- Verify checkpoint creation works
- Verify performance <100ms

**Validation:**
```bash
pytest tests/hooks/ -v
pytest --cov=.claude/hooks/ms --cov-report=html
# Manual: Start Claude Code session, trigger all 4 events
```

**Phase 1 Completion Criteria:**
- [ ] All 4 Python hooks working (SessionStart, PreToolUse, PostToolUse, UserPromptSubmit)
- [ ] Existing hooks functionality 100% preserved
- [ ] Old hooks deleted
- [ ] pytest coverage ≥85%
- [ ] Claude Code session starts successfully
- [ ] Performance <100ms per hook

---

### 2.3 Phase 2: Skills Implementation (Week 4-6, 17-24h)

**Objective**: Implement 11 Skills with Progressive Disclosure.

#### Phase 2.1: Foundation Core Skills (Week 4, 8-11h)

**Progressive Disclosure Architecture:**

**Level 1 (Metadata - loaded at session start):**
```yaml
# .claude/skills/ms-foundation-constitution/SKILL.md
---
name: ms-foundation-constitution
tier: foundation
description: Constitution auto-validation (file size, EARS, TRUST)
triggers: ["code review request", "file modification"]
size: ~400 LOC
model: haiku
---
```

**Level 2 (Instructions - loaded when agent references):**
```markdown
## When to Use
- Code writing requires Constitution compliance check
- File size ≤500 SLOC validation
- EARS pattern verification
- TRUST 5 principles validation

## Quick Start
1. Read Constitution file
2. Check file size against limits
3. Validate EARS patterns in requirements
4. Report violations
```

**Level 3 (Resources - loaded when execution needed):**
```python
# check_file_size.py
def check_file_size(file_path: str) -> dict:
    """Validate file size against Constitution limits

    Returns:
        {"passed": bool, "sloc": int, "limit": int, "message": str}
    """
    # Count SLOC (exclude comments and blank lines)
    sloc = count_sloc(file_path)
    limit = 500

    return {
        "passed": sloc <= limit,
        "sloc": sloc,
        "limit": limit,
        "message": f"File size: {sloc} SLOC (limit: {limit})" if sloc <= limit else f"❌ File exceeds limit: {sloc} > {limit} SLOC"
    }
```

**Skills to Implement (Foundation Tier):**

1. **ms-foundation-constitution** (3-4h, TDD)
   - Files: `SKILL.md`, `check_file_size.py`, `check_complexity.py`
   - Tests: `tests/skills/test_constitution_skill.py`

2. **ms-foundation-trust** (3-4h, TDD)
   - Files: `SKILL.md`, `trust_validator.py`
   - Tests: `tests/skills/test_trust_skill.py`
   - Function: TRUST 5 principles validation

3. **ms-foundation-ears** (2-3h, TDD)
   - Files: `SKILL.md`, `patterns.yaml`
   - Tests: `tests/skills/test_ears_skill.py`
   - Function: EARS pattern validation, forbidden phrases detection

**Validation:**
```bash
pytest tests/skills/ -v
# Manual: Start Claude Code, verify Skills loaded in session
```

---

#### Phase 2.2: Workflow Skills (Week 5, 5-7h)

1. **ms-workflow-tag-manager** (3-4h, TDD)
   - Files: `SKILL.md`, `tag_templates.json`
   - Tests: `tests/skills/test_tag_manager_skill.py`
   - Function: TAG block templates, auto-insertion

**TAG Block Template:**
```json
{
  "python": {
    "template": "\"\"\"\n@CODE:{TAG_ID}\n@SPEC: {spec_path}\n@TEST: {test_path}\n@CHAIN: @SPEC:{TAG_ID} → @TEST:{TAG_ID} → @CODE:{TAG_ID}\n@STATUS: {status}\n@CREATED: {created}\n@UPDATED: {updated}\n\"\"\""
  },
  "typescript": {
    "template": "/**\n * @CODE:{TAG_ID}\n * @SPEC: {spec_path}\n * @TEST: {test_path}\n * @CHAIN: @SPEC:{TAG_ID} → @TEST:{TAG_ID} → @CODE:{TAG_ID}\n * @STATUS: {status}\n * @CREATED: {created}\n * @UPDATED: {updated}\n */"
  }
}
```

2. **ms-workflow-living-docs** (2-3h, TDD)
   - Files: `SKILL.md`
   - Tests: `tests/skills/test_living_docs_skill.py`
   - Function: API doc generation from TAG scan

---

#### Phase 2.3: Language Pack Skills (Week 6, 4-6h)

1. **ms-lang-typescript** (2-3h, TDD)
   - Files: `SKILL.md` (TypeScript best practices)
   - Tests: `tests/skills/test_typescript_skill.py`

**Example Content:**
```markdown
## Type Safety (Constitution Section V.U)

✅ **Good:**
```typescript
function getUser(id: string): Promise<User> {
  return fetchUser(id);
}
```

❌ **Bad:**
```typescript
function getUser(id: any): any {  // any abuse
  return fetchUser(id);
}
```
```

2. **ms-lang-python** (2-3h, TDD)
   - Files: `SKILL.md` (Python best practices)
   - Tests: `tests/skills/test_python_skill.py`

**Phase 2 Completion Criteria:**
- [ ] 7 Skills implemented (Foundation 3 + Workflow 2 + Language 2)
- [ ] Progressive Disclosure working (3 levels)
- [ ] pytest coverage ≥85% per Skill
- [ ] Context usage reduced by 40% (measured)
- [ ] Skills auto-load at session start

---

### 2.4 Phase 3: Living-Docs Implementation (Week 7-8, 19-27h)

**Objective**: Implement universal document synchronization system.

#### Phase 3.1: /ms.up-docs Command (Week 7, 6-8h)

**TDD Cycle:**

**RED (2-3h):**
```python
# tests/commands/test_ms_up_docs.py
def test_sync_api_docs():
    result = run_command("/ms.up-docs --docs=api")
    assert "docs/api/AUTH-001.md" in result["files_updated"]

def test_sync_dev_daily():
    result = run_command("/ms.up-docs --docs=dev")
    assert "docs/dev_daily.md" in result["files_updated"]

def test_sync_all():
    result = run_command("/ms.up-docs --all")
    assert len(result["files_updated"]) >= 3  # api, dev, readme
```

**GREEN (3-4h):**
- Create `.claude/commands/ms.up-docs.md`
- Implement argument parsing (--docs=api/dev/readme/--all)
- Implement doc-updater agent delegation

**Command Structure:**
```markdown
# /ms.up-docs - Universal Document Synchronization

## Arguments

- `--docs=api`: Sync API docs only
- `--docs=dev`: Sync dev daily only
- `--docs=readme`: Sync README only
- `--all`: Full regeneration (all docs, all TAGs)
- No args: Staged changes only (default)

## Staged Changes Logic

WHEN user runs `/ms.up-docs` without `--all` flag, system SHALL:
1. Run `git diff --cached` to detect staged changes
2. Sync only docs related to staged files
3. Generate sync report with affected TAGs

IF no staged changes exist, display warning:
```
⚠️ No staged changes found.
Use 'git add <files>' first or run '/ms.up-docs --all' for full sync.
```

## Execution

1. Detect staged changes (git diff --cached)
2. Delegate to doc-updater agent
3. Generate sync report
4. Validate TAG chain integrity
```

**REFACTOR (1h):**
- Add error handling (Fail-open)
- Add sync report generation

**Validation:**
```bash
pytest tests/commands/test_ms_up_docs.py -v
# Manual: Run /ms.up-docs, verify docs updated
```

---

#### Phase 3.2: doc-updater Agent (Week 7-8, 9-12h)

**TDD Cycle:**

**RED (2-3h):**
```python
# tests/agents/test_doc_updater.py
def test_git_diff_analysis():
    result = doc_updater.analyze_git_diff()
    assert "changed_files" in result
    assert "change_patterns" in result

def test_api_doc_generation():
    result = doc_updater.sync_api_docs(tag="AUTH-001")
    assert Path("docs/api/AUTH-001.md").exists()
```

**GREEN (5-7h):**
- Create `.claude/agents/doc-updater.md`
- Implement Phase 1: Git diff analysis
- Implement Phase 2: Parallel doc sync (api, dev, readme)
- Implement Phase 3: TAG chain validation

**Agent Structure:**
```markdown
# doc-updater Agent

**Model**: Haiku
**Purpose**: CODE-FIRST document synchronization

## Workflow

### Phase 1: Git Diff Analysis (2-3min)
- Run: `git diff HEAD~1 --name-only`
- Extract change patterns (new functions, modified APIs, deleted code)
- Identify major vs minor changes for README update decision

### Phase 2: Parallel Document Sync (5-10min)
- **API Docs**: Scan code for TAG blocks using ripgrep
  - Extract function signatures and docstrings
  - Generate `docs/api/{TAG}.md` following template
- **Dev Daily**: Summarize Git diff with AI
  - Append to `docs/dev_daily.md` with timestamp
- **README**: IF major changes detected
  - Update project status, installation steps, usage examples

### Phase 3: TAG Chain Validation (3-5min)
- Scan: `rg '@(SPEC|TEST|CODE|DOC):' -n`
- Verify complete chains: @SPEC → @TEST → @CODE → @DOC
- Identify orphaned tags (TAG exists but file missing)
- Report integrity score (percentage of valid chains)

## Output Format

```json
{
  "files_updated": ["docs/api/AUTH-001.md", "docs/dev_daily.md"],
  "tag_integrity": {
    "total_chains": 45,
    "complete_chains": 43,
    "orphaned_tags": 2,
    "integrity_score": 95.6
  },
  "duration_seconds": 547
}
```
```

**REFACTOR (2h):**
- Optimize performance (target <10min)
- Add structured output (JSON)

**Validation:**
```bash
pytest tests/agents/test_doc_updater.py -v
# Integration test: Mock Git repo, run full sync
```

---

#### Phase 3.3: /fin, /finq Integration (Week 8, 3-5h)

**Tasks:**

1. **Update /fin command (1-2h)**
```markdown
# Current behavior
/fin: Update dev_daily.md → make ci → git commit && push

# New behavior
/fin: /ms.up-docs --docs=dev → make ci → git commit && push
```

2. **Update /finq command (1-2h)**
```markdown
# Current behavior
/finq: Update dev_daily.md → git commit && push (no CI)

# New behavior
/finq: /ms.up-docs --docs=dev → git commit && push (no CI)
```

3. **Integration testing (1h)**
- Run `/fin`, verify dev_daily.md updated, CI runs, commit created
- Run `/finq`, verify dev_daily.md updated, commit created (no CI)

**Validation:**
```bash
# Manual: Run /fin, check dev_daily.md, verify CI ran
# Manual: Run /finq, check dev_daily.md, verify CI skipped
```

---

#### Phase 3.4: Remove ms.update-docs (Week 8, 1-2h)

```bash
# Delete command file
rm .claude/commands/ms.update-docs.md

# Search for references
rg "ms\.update-docs" -n

# Update documentation
# Update README.md to reference /ms.up-docs
```

**Phase 3 Completion Criteria:**
- [ ] `/ms.up-docs` works for all 3 doc types (api, dev, readme)
- [ ] doc-updater agent completes in <10 minutes
- [ ] `/fin`, `/finq` updated and tested
- [ ] `ms.update-docs` removed
- [ ] TAG chain integrity validated (100%)
- [ ] Integration tests pass

---

### 2.5 Phase 4: Sub-Agents Implementation (Week 9-12, 33-48h)

**Objective**: Implement 5 new agents for workflow automation.

#### Phase 4.1: spec-builder Agent (Week 9, 7-10h)

**TDD Cycle:**

**RED (2-3h):**
```python
# tests/agents/test_spec_builder.py
def test_ears_conversion():
    result = spec_builder.convert_to_ears("사용자가 로그인하면 토큰 발급")
    assert "WHEN user" in result
    assert "system SHALL" in result
```

**GREEN (4-5h):**
- Create `.claude/agents/spec-builder.md`
- Implement EARS pattern enforcement
- Implement Korean → English translation
- Implement spec.md template generation

**Agent Persona (from MoAI-ADK):**
- **Icon**: 🏗️
- **Job**: Requirements Engineer
- **Expertise**: EARS syntax, requirement analysis
- **Goal**: Create unambiguous, testable specifications

**Agent Responsibilities:**
- Read user feature request (Korean or English)
- Convert requirements to EARS format (5 patterns)
- Translate Korean input to English EARS output
- Apply Constitution Section IV (EARS standards)
- Generate structured spec.md following Spec-Kit template
- Validate against forbidden phrases

**Skills Used:**
- `ms-foundation-read`: Read existing spec.md and templates
- `ms-foundation-write`: Write new spec.md content
- `ms-essentials-review`: Quality check for EARS compliance
- `ms-workflow-tag-manager`: Generate TAG ID placeholders

**REFACTOR (1-2h):**
- Integrate with Constitution Section IV
- Add forbidden phrase detection

**Validation:**
```bash
pytest tests/agents/test_spec_builder.py -v
# Manual: Run /ms.specify, verify EARS compliance
```

---

#### Phase 4.2: implementation-planner Agent (Week 10, 7-10h)

**Agent Responsibilities:**
- Read spec.md and extract functional requirements
- **Collaborate with library-researcher** (Haiku + Context7 MCP)
- **Collaborate with codebase-explorer** (Haiku + Grep/Glob)
- Design TAG chain structure (@SPEC → @TEST → @CODE)
- Select appropriate libraries with version constraints
- Create architecture diagram (Mermaid format)
- Document trade-offs and design decisions

**Agent Collaboration Pattern:**
```
implementation-planner (Opus)
    ├─→ library-researcher (Haiku) → Context7 MCP → Latest React docs
    └─→ codebase-explorer (Haiku) → Ripgrep scan → Similar auth patterns
```

**Library Research (Direct Context7 MCP):**
```python
# NO Gemini delegation - use Context7 MCP directly
lib_id = mcp__context7__resolve_library_id("react")
docs = mcp__context7__get_library_docs(
    context7CompatibleLibraryID=lib_id,
    topic="hooks, routing",
    tokens=5000
)
```

**TDD Cycle:**

**RED (2-3h):**
```python
def test_library_selection():
    result = planner.select_libraries(requirements)
    assert "react" in result["dependencies"]
    assert result["dependencies"]["react"].startswith("^18")
```

**GREEN (4-5h):**
- Create `.claude/agents/implementation-planner.md`
- Implement library-researcher collaboration (Context7 MCP)
- Implement codebase-explorer collaboration
- Implement TAG chain design

**REFACTOR (1-2h):**
- Add architecture diagram generation (Mermaid)
- Document trade-offs

---

#### Phase 4.3: tdd-implementer Agent (Week 10-11, 9-13h)

**Agent Responsibilities:**
- Read plan.md and tasks.md
- **RED Phase**: Write failing test with @TEST:{TAG} marker
- **GREEN Phase**: Implement minimum code to pass test with @CODE:{TAG} marker
- **REFACTOR Phase**: Improve code quality while keeping tests green
- Auto-insert TAG blocks in generated files
- Run tests and report results
- Verify TRUST 5 principles compliance

**TDD Cycle:**

**RED (2-3h):**
```python
def test_red_green_refactor_cycle():
    result = tdd_implementer.implement(task)
    assert result["test_written_first"] == True
    assert result["all_tests_passed"] == True
```

**GREEN (5-7h):**
- Create `.claude/agents/tdd-implementer.md`
- Implement RED phase (failing test)
- Implement GREEN phase (minimum code)
- Implement REFACTOR phase
- Integrate TAG auto-insertion (from ms-workflow-tag-manager Skill)

**REFACTOR (2-3h):**
- Consolidate TAG insertion logic (OSOT)
- Add TRUST validation

---

#### Phase 4.4-4.5: debug-helper, quality-gate (Week 12, 9-13h)

**debug-helper (5-7h, TDD):**
- **Trigger**: Error occurs during implementation
- **Responsibilities**: Analyze stack trace, identify root cause, suggest fixes, provide rollback steps
- **Model**: Sonnet (complex reasoning)

**quality-gate (4-6h, TDD):**
- **Trigger**: `/fin` command (before commit)
- **Responsibilities**: Verify coverage ≥85%, check TRUST compliance, run linter, validate TAG chains
- **Model**: Haiku (fast validation)

**Phase 4 Completion Criteria:**
- [ ] 5 new agents implemented
- [ ] Agent collaboration tested (implementation-planner + library-researcher)
- [ ] All agents integrated with `/ms.*` commands
- [ ] pytest coverage ≥85%
- [ ] Model distribution verified: Haiku 6-7 agents (55-64%), Sonnet 3 agents (27%), Opus 1-2 agents (9-18%)

---

## 3. Testing Strategy

### 3.1 Test Coverage Matrix

| Component | Unit Tests | Integration Tests | Regression Tests | Target Coverage |
|-----------|-----------|-------------------|------------------|--------------------|
| **Hooks** | core/*.py, handlers/*.py | Real Claude Code session (4 events) | Preserve constitution-injector, tag-enforcer functionality | ≥85% |
| **Skills** | Each Skill individually | Skill loading at session start | None (new system) | ≥85% per Skill |
| **Living-Docs** | doc-updater agent phases | /ms.up-docs → Git diff → docs | /fin, /finq behavior unchanged | ≥85% |
| **Sub-Agents** | Agent logic | Task tool delegation, collaboration | Existing 6 agents still work | ≥85% |

### 3.2 Regression Test Scenarios

**Phase 1 (Hooks Migration):**
```python
# tests/hooks/test_backwards_compatibility.py

def test_constitution_injection_preserved():
    """Verify constitution-injector.sh → handlers/user.py equivalence"""
    result = invoke_task_tool()
    assert "Constitution Context" in result.context

def test_tag_immutability_preserved():
    """Verify tag-enforcer.ts → core/tags.py equivalence"""
    with pytest.raises(TagImmutabilityError):
        edit_file_with_immutable_tag("src/auth.ts")
```

**Phase 3 (Living-Docs):**
```python
# tests/commands/test_living_docs_compatibility.py

def test_fin_still_updates_dev_daily():
    """Verify /fin continues working after /ms.up-docs integration"""
    run_command("/fin")
    assert Path("docs/dev_daily.md").exists()
    assert git_commit_exists()
```

### 3.3 Performance Testing

```python
# tests/hooks/test_performance.py

def test_session_start_performance():
    start = time.time()
    run_hook("SessionStart", {"cwd": "."})
    duration = (time.time() - start) * 1000  # milliseconds
    assert duration < 100, f"SessionStart took {duration}ms (limit: 100ms)"
```

---

## 4. Risk Mitigation

### 4.1 Risk Matrix

| Risk | Probability | Impact | Mitigation | Owner |
|------|------------|--------|------------|-------|
| **Existing hooks break during migration** | HIGH | CRITICAL | Phase 1.0 parallel testing, gradual cutover | Dev Team |
| **Path mapping incomplete (.moai hardcoded)** | MEDIUM | CRITICAL | Pre-Phase 1 scan: `rg "\.moai"`, zero results required | Dev Team |
| **TAG block duplication** | MEDIUM | MEDIUM | Consolidate to ms-workflow-tag-manager Skill (OSOT) | Dev Team |
| **Living-Docs breaks /fin, /finq** | MEDIUM | HIGH | Phase 3.3 integration testing, user workflow validation | QA Team |
| **Python 3.13 unavailable** | LOW | HIGH | Document requirement in migration guide, provide setup script | DevOps |
| **Sub-Agent delegation overhead** | LOW | MEDIUM | Model distribution (58% Haiku), performance monitoring | Ops Team |

### 4.2 Rollback Plans

**Phase 1 Rollback (Hooks):**
```bash
git checkout main -- .claude/hooks/constitution-injector.sh
git checkout main -- .claude/hooks/tag-enforcer.ts
rm -rf .claude/hooks/ms/
git checkout main -- .claude/settings.local.json
```

**Phase 3 Rollback (Living-Docs):**
```bash
git checkout main -- .claude/commands/ms.update-docs.md
git checkout main -- .claude/commands/fin.md
git checkout main -- .claude/commands/finq.md
rm -rf .claude/commands/ms.up-docs.md
rm -rf .claude/agents/doc-updater.md
```

---

## 5. Success Metrics

### 5.1 Quantitative Metrics

| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| Document sync time | 30 minutes | 2 minutes | Time `/ms.up-docs --all` |
| TAG validation time | 15 minutes | 10 seconds | Time `rg '@(SPEC\|TEST\|CODE):' -n` |
| SPEC creation time | 60 minutes | 15 minutes | Time `/ms.specify` with spec-builder |
| Constitution compliance | 70% | 95% | `/ms.analyze` Level 1 pass rate |
| Context usage | 100% | 60% | Token count before/after Progressive Disclosure |
| Test coverage | 80% | 85% | pytest --cov |
| Hook performance | N/A | <100ms | `.specify/hooks_performance.log` |

### 5.2 Qualitative Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Developer satisfaction | Post-integration survey (1-5 scale) | ≥4.0 |
| Onboarding time | Time to first contribution (new team member) | ≤1 day (from 3 days) |
| Documentation accuracy | Spot check: docs match code | 100% |
| Workflow disruption | Complaints about breaking changes | <5 per week |

---

## 6. Implementation Timeline

### 6.1 Phase Overview

| Phase | Duration | Features | Risk | Dependencies |
|-------|----------|----------|------|--------------|
| **Phase 0** | Week 0.5 (4h) | Migration prep | 🔴 HIGH | Python 3.13+, path mapping |
| **Phase 1** | Week 1-3 (25-32h) | Hooks (4 events) | 🔴 HIGH | Phase 0 complete |
| **Phase 2** | Week 4-6 (17-24h) | Skills (7 Skills) | 🟡 MEDIUM | Phase 1 complete |
| **Phase 3** | Week 7-8 (19-27h) | Living-Docs | 🔴 HIGH | doc-updater agent |
| **Phase 4** | Week 9-12 (33-48h) | Sub-Agents (5 new) | 🟢 LOW | Phase 2+3 complete |

**Total Effort:** 94-131 hours over 12 weeks

### 6.2 Milestones

| Week | Milestone | Validation Gate | Blocker? |
|------|-----------|----------------|----------|
| 0.5 | Phase 0 complete | Environment ready, backups created | YES |
| 3 | Phase 1 complete | All 4 hooks working, old hooks removed | YES |
| 6 | Phase 2 complete | 7 Skills implemented, context usage <60% | YES |
| 8 | Phase 3 complete | /ms.up-docs operational, ms.update-docs removed | YES |
| 12 | Phase 4 complete | 5 new agents deployed, full integration tested | YES |

---

## 7. Acceptance Criteria

### 7.1 Phase 1 Acceptance (Hooks)

**User Acceptance Test:**
- [ ] Start Claude Code session, see project status card
- [ ] Edit Constitution file, verify checkpoint created in `.specify/checkpoints.log`
- [ ] Edit ≥5 files simultaneously, verify checkpoint created
- [ ] Edit TypeScript file, verify Prettier runs
- [ ] Edit Python file, verify Black runs
- [ ] Invoke Task tool (sub-agent), verify Constitution injected
- [ ] Attempt to edit @IMMUTABLE TAG, verify blocked with error
- [ ] All hooks execute in <100ms (check logs)

**Technical Acceptance:**
- [ ] pytest coverage ≥85% for `.claude/hooks/ms/`
- [ ] All 4 hook events trigger correctly
- [ ] Old hooks removed (constitution-injector.sh, tag-enforcer.ts, notify.sh)
- [ ] Python 3.13+ confirmed
- [ ] Zero `.moai` hardcoded paths

---

### 7.2 Phase 2 Acceptance (Skills)

**User Acceptance Test:**
- [ ] Start Claude Code session, verify Skills loaded (metadata only)
- [ ] Trigger Constitution validation, verify Skill loaded (Level 2 + 3)
- [ ] Edit TypeScript file, verify ms-lang-typescript Skill referenced
- [ ] Run `/ms.implement`, verify ms-workflow-tag-manager Skill used
- [ ] Check context usage, verify 40% reduction vs baseline

**Technical Acceptance:**
- [ ] 7 Skills implemented with SKILL.md
- [ ] Progressive Disclosure working (3 levels)
- [ ] pytest coverage ≥85% per Skill
- [ ] All Skills reference Constitution

---

### 7.3 Phase 3 Acceptance (Living-Docs)

**User Acceptance Test:**
- [ ] Run `/ms.up-docs --docs=api`, verify `docs/api/{TAG}.md` generated
- [ ] Run `/ms.up-docs --docs=dev`, verify `docs/dev_daily.md` updated
- [ ] Run `/ms.up-docs --docs=readme`, verify `README.md` updated
- [ ] Run `/fin`, verify dev_daily.md updated, CI runs, commit created
- [ ] Run `/finq`, verify dev_daily.md updated, commit created (no CI)
- [ ] Run `/ms.update-docs`, verify deprecation warning shown

**Technical Acceptance:**
- [ ] doc-updater agent completes in <10 minutes
- [ ] TAG chain integrity validated (100% accuracy)
- [ ] `/fin`, `/finq` behavior unchanged from user perspective
- [ ] `ms.update-docs.md` file removed

---

### 7.4 Phase 4 Acceptance (Sub-Agents)

**User Acceptance Test:**
- [ ] Run `/ms.specify`, verify spec-builder agent used (EARS compliant)
- [ ] Run `/ms.plan`, verify implementation-planner agent used
- [ ] Run `/ms.implement`, verify tdd-implementer agent follows RED-GREEN-REFACTOR
- [ ] Run `/ms.analyze`, verify tag-auditor and trust-validator agents used
- [ ] Trigger error, verify debug-helper agent provides fix suggestions
- [ ] Run `/fin`, verify quality-gate agent validates coverage and TRUST

**Technical Acceptance:**
- [ ] 5 new agents implemented with agent files
- [ ] 6 existing agents continue working
- [ ] Agent collaboration tested (implementation-planner + library-researcher)
- [ ] Model distribution correct (Haiku 58%, Sonnet 25%, Opus 17%)
- [ ] pytest coverage ≥85% for agents

---

## 8. Dependencies and Prerequisites

### 8.1 System Requirements

| Requirement | Version | Purpose | Validation |
|-------------|---------|---------|------------|
| **Python** | ≥3.13 (REQUIRED) | Hooks, Skills scripts | `python3 --version` |
| **pytest** | ≥7.0 | Test framework | `pytest --version` |
| **pytest-cov** | Latest | Coverage reporting | `pytest --cov --version` |
| **ripgrep** | Latest | TAG scanning | `rg --version` |
| **Git** | ≥2.30 | Checkpoints, diff analysis | `git --version` |
| **Prettier** | Latest | TypeScript formatting | `npx prettier --version` |
| **Black** | Latest | Python formatting | `black --version` |

**Installation Script:**
```bash
# Check Python version (MUST be 3.13+)
python3 --version | grep -E "3\.(1[3-9]|[2-9][0-9])" || {
    echo "❌ Error: Python 3.13+ required"
    echo "Current version: $(python3 --version)"
    echo "Install Python 3.13+: https://www.python.org/downloads/"
    exit 1
}

# Install Python packages
pip install pytest pytest-cov black

# Install Node packages
npm install -D prettier

# Verify ripgrep
rg --version || echo "Install ripgrep: https://github.com/BurntSushi/ripgrep#installation"

# Verify Git
git --version
```

### 8.2 Project Prerequisites

**Before Phase 1:**
- [ ] Constitution.md exists at `.specify/memory/constitution.md`
- [ ] Project is Git repository (`git status` works)
- [ ] Backup created: `git tag pre-moai-v1.0.0`
- [ ] All tests passing: `pytest tests/ -v`
- [ ] Current coverage ≥80%: `pytest --cov`

**Before Phase 3:**
- [ ] Hooks Phase 1 complete (all 4 events working)
- [ ] Skills Phase 2 complete (7 Skills implemented)
- [ ] doc-updater agent implemented and tested

**Before Phase 4:**
- [ ] Living-Docs Phase 3 complete (/ms.up-docs operational)
- [ ] All existing `/ms.*` commands working
- [ ] TAG system validated (no orphaned tags)

---

## 9. Appendix

### A. Path Mapping Transformation Script

```python
#!/usr/bin/env python3
"""
Path mapping script: .moai → .specify
Run before Phase 1 to replace all hardcoded MoAI paths
"""
import re
from pathlib import Path

MAPPINGS = {
    r"\.moai/checkpoints\.log": ".specify/checkpoints.log",
    r"\.moai/config\.json": ".specify/memory/constitution.md",
    r"\.moai/memory/": ".specify/memory/",
    r"\.moai/specs/": "specs/",
}

def transform_file(file_path: Path):
    content = file_path.read_text()
    original = content

    for pattern, replacement in MAPPINGS.items():
        content = re.sub(pattern, replacement, content)

    if content != original:
        file_path.write_text(content)
        print(f"✅ Transformed: {file_path}")

def main():
    # Scan .claude/hooks/ms/ directory
    hooks_dir = Path(".claude/hooks/ms")
    if hooks_dir.exists():
        for py_file in hooks_dir.rglob("*.py"):
            transform_file(py_file)

    # Verify no .moai paths remain
    import subprocess
    result = subprocess.run(["rg", r"\.moai", "-n"], capture_output=True)
    if result.returncode == 0:
        print("\n⚠️  WARNING: .moai paths still found:")
        print(result.stdout.decode())
    else:
        print("\n✅ All .moai paths successfully transformed!")

if __name__ == "__main__":
    main()
```

---

### B. Hook Performance Monitoring

```python
# .claude/hooks/ms/core/__init__.py
import time
import json
from pathlib import Path

class HookResult:
    def __init__(self, continue_execution=True, system_message=None):
        self.continue_execution = continue_execution
        self.system_message = system_message
        self.start_time = time.time()

    def finalize(self):
        duration_ms = (time.time() - self.start_time) * 1000

        # Log performance
        log_path = Path(".specify/hooks_performance.log")
        log_entry = {
            "timestamp": time.time(),
            "duration_ms": duration_ms,
            "warning": duration_ms > 100
        }

        with log_path.open("a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Warn if slow
        if duration_ms > 100:
            print(f"⚠️  Hook exceeded 100ms: {duration_ms:.2f}ms", file=sys.stderr)

        return {
            "continue": self.continue_execution,
            "systemMessage": self.system_message
        }
```

---

### C. Directory Structure (After Integration)

```
.claude/
├── hooks/
│   └── ms/
│       ├── ms_hooks.py              # Entry point (CLI args)
│       ├── core/
│       │   ├── __init__.py          # HookPayload, HookResult
│       │   ├── project.py           # Language detect, Git info
│       │   ├── context.py           # JIT Context Retrieval
│       │   ├── checkpoint.py        # Auto checkpoints
│       │   └── tags.py              # TAG scan, validation, @IMMUTABLE
│       └── handlers/
│           ├── session.py           # SessionStart, SessionEnd
│           ├── user.py              # UserPromptSubmit
│           └── tool.py              # PreToolUse, PostToolUse
├── skills/
│   ├── ms-foundation-constitution/
│   │   ├── SKILL.md
│   │   ├── check_file_size.py
│   │   └── check_complexity.py
│   ├── ms-foundation-trust/
│   ├── ms-foundation-ears/
│   ├── ms-workflow-tag-manager/
│   ├── ms-workflow-living-docs/
│   ├── ms-lang-typescript/
│   └── ms-lang-python/
├── agents/
│   ├── spec-builder.md              # NEW
│   ├── implementation-planner.md    # NEW
│   ├── tdd-implementer.md           # NEW
│   ├── doc-updater.md               # NEW
│   ├── debug-helper.md              # NEW
│   ├── quality-gate.md              # NEW
│   └── [6 existing agents]
└── commands/
    ├── ms.up-docs.md                # NEW (universal doc sync)
    ├── fin.md                       # UPDATED (calls /ms.up-docs)
    ├── finq.md                      # UPDATED (calls /ms.up-docs)
    └── [11 existing ms.* commands]

.specify/
├── checkpoints.log                  # NEW (Git checkpoints)
└── memory/
    └── constitution.md              # EXISTING (no changes)

specs/
└── 002-moai-adk-integration/
    └── spec.md                      # THIS FILE
```

---

## 📜 Constitution

This plan follows the project [Constitution](../../.specify/memory/constitution.md).

**Key Sections:**
- **Section I**: Test-First Development (RED → GREEN → REFACTOR)
- **Section II**: Simplicity-First Architecture (prefer existing tools)
- **Section IV**: EARS Requirements Standards (5 patterns)
- **Section V**: TRUST 5 Quality Principles (Test, Readable, Unified, Secured, Trackable)
- **Section VII**: Security by Default (input validation, secrets management)
- **Section X**: Agentic Behavior Standards (transparency, no deception)

**TAG System:**
- Complete traceability: @SPEC → @TEST → @CODE → @DOC
- Auto-insertion by tdd-implementer Agent
- Validation by tag-auditor Agent

**EARS Compliance:**
- System SHALL: Unconditional requirements
- WHEN: Event-driven requirements
- WHILE: State-driven requirements
- WHERE: Optional requirements
- IF: Constraint requirements

_Auto-added by `/ms.plan`_

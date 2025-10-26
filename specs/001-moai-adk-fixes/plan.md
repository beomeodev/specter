# Implementation Plan: MoAI-ADK Integration Fixes

**Branch**: `001-moai-adk-fixes` | **Date**: 2025-10-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-moai-adk-fixes/spec.md`

**Note**: This plan addresses 12 critical issues discovered during MoAI-ADK integration verification (fail-open violations, @IMMUTABLE protection, Skills completion, agent delegation, metrics accuracy).

## Summary

This implementation fixes 12 critical issues in the MoAI-ADK integration across 6 major areas: hook system fail-open compliance (FR-001~004), @IMMUTABLE file protection (FR-005~010), test coverage (FR-011~013), Skills completion (FR-014~017), document automation (FR-018~021), agent delegation (FR-022~025), and metrics accuracy (FR-026~029). The technical approach follows a Test-First methodology with comprehensive unit tests (≥85% coverage) for hook handlers, integration tests for E2E workflows (@IMMUTABLE unlock, agent delegation, document sync), and strict Constitution compliance (≤500 SLOC files, ≤10 complexity per function).

**Primary Technical Strategy**:
- **Hook System**: Modify `ms_hooks.py` to exit with code 0 on all errors (fail-open principle)
- **@IMMUTABLE Protection**: New module `core/immutable_protection.py` with ripgrep-based scanning, session-scoped unlock registry, Git checkpoint creation, and audit logging
- **Skills**: Create `ms-essentials-debug` and `ms-essentials-review` following 7-section template from MoAI-ADK reference
- **Document Automation**: Leverage existing `doc-updater` agent with fixed `core/project.py` (TAG integrity scan includes .md files, SPEC counting uses Markdown metadata)
- **Agent Delegation**: Add delegation recommendation logic to `implementation-planner` and `quality-gate` agents (passive recommendations, commands execute via Task tool)
- **Metrics Accuracy**: Fix `calculate_tag_integrity()` to scan .md files using ripgrep `--type-add 'md:*.md'`, fix `count_specs()` to parse Markdown metadata `**Status**: completed`

## Technical Context

**Language/Version**: Python 3.13+ (hook system, agents), TypeScript 5.7+ (agent prompts are Markdown but use TS-style conventions), Bash (scripts)
**Primary Dependencies**:
- ripgrep 13.0+ (TAG scanning, @IMMUTABLE detection with `--type-add` support)
- Git 2.30+ (checkpoint creation via `git checkout -b checkpoint/...`)
- pytest 8.4.2 (Python testing framework)
- Python stdlib only (no new packages: subprocess, json, sys, re, pathlib, datetime)
- Claude Code platform (hook system, Task tool, agent execution environment)

**Storage**:
- In-memory: `UnlockRegistry` (session-scoped unlock state, singleton pattern)
- Filesystem: `.specify/immutable_changes.log` (audit trail), `.claude/hooks/ms/` (hook handlers), `.claude/skills/` (Skills content), `specs/*/plan.md` (agent outputs)

**Testing**: pytest 8.4.2 with ≥85% coverage requirement
- Unit tests: `test_immutable_protection.py` (350 SLOC, ≥12 test cases), `test_user_prompt_submit.py` (400 SLOC, ≥15 test cases), `test_project_metrics.py` (200 SLOC, ≥8 test cases)
- Integration tests: E2E scenarios for @IMMUTABLE protection lifecycle, agent delegation chains, document sync workflows
- Mocking strategy: Mock subprocess.run for ripgrep/git calls, mock Task tool for agent delegation, use tmp_path fixtures

**Target Platform**: Linux server (WSL2 environment), Claude Code CLI integration
**Project Type**: Single (existing codebase enhancement - not web/mobile)
**Performance Goals**:
- @IMMUTABLE scan: <50ms per Edit/Write operation
- TAG integrity scan: <5 seconds for entire codebase (existing timeout)
- Document sync: <10 seconds for typical feature changes (3-phase workflow)
- Hook fail-open: Exit code 0 within <100ms on errors

**Constraints**:
- Fail-open principle: ALL hook errors must exit with code 0 (not block workflows)
- Session-scoped unlock: @IMMUTABLE unlocks do NOT persist across sessions (security by design)
- No custom AST parsers: Use ripgrep regex-based scanning (Constitution Section II: prefer existing tools)
- No database: All TAG data via ripgrep direct scanning (CODE-FIRST principle)
- File size limits: ≤500 SLOC per file, ≤100 LOC per function, ≤10 complexity (Constitution Section II)

**Scale/Scope**:
- 12 critical issues across 6 functional areas
- 30 functional requirements (FR-001 through FR-030)
- 3 new modules: `core/immutable_protection.py`, `ms-essentials-debug/SKILL.md`, `ms-essentials-review/SKILL.md`
- 2 new commands: `/ms.unlock`, `/ms.up-docs`
- 1 new agent: `quality-gate.md`
- Modified files: `ms_hooks.py`, `handlers/tool.py`, `handlers/session.py`, `core/project.py`, `implementation-planner.md`
- New test files: 3 comprehensive test suites (950 SLOC total tests)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Section I: Test-First Development (TDD) ✅

**Status**: PASS (with plan to implement)

**Compliance**:
- ✅ All new features will have tests written BEFORE implementation (RED → GREEN → REFACTOR)
- ✅ Test coverage target: ≥85% (actual target: ≥95% for critical security features)
- ✅ Test suites planned: `test_immutable_protection.py` (≥12 test cases), `test_user_prompt_submit.py` (≥15 test cases), `test_project_metrics.py` (≥8 test cases)
- ✅ Integration tests planned for E2E workflows

**Execution Plan**:
1. Write failing test for fail-open behavior (FR-001)
2. Implement minimum code in `ms_hooks.py` to exit with code 0
3. Refactor error handling while keeping tests green
4. Repeat for each functional requirement

### Section II: Simplicity-First Architecture ✅

**Status**: PASS

**File Size Compliance**:
- ✅ `core/immutable_protection.py`: 180 SLOC (< 500)
- ✅ `handlers/tool.py`: 280 SLOC with @IMMUTABLE additions (< 500)
- ✅ `core/project.py`: 311 SLOC current, minor additions (< 500)
- ✅ `ms-essentials-debug/SKILL.md`: 300 SLOC (< 500)
- ✅ `ms-essentials-review/SKILL.md`: 320 SLOC (< 500)
- ✅ `quality-gate.md`: 250 SLOC (< 500)
- ✅ Test files: All under 500 SLOC (350, 400, 200 respectively)

**Function Size Compliance**:
- ✅ `unlock_file()`: ~60 LOC (< 100)
- ✅ `handle_pre_tool_use()`: ~80 LOC with @IMMUTABLE logic (< 100)
- ✅ All other functions: Sequential logic, <50 LOC typical

**Complexity Compliance**:
- ✅ All functions use simple sequential logic (cyclomatic complexity ≤5)
- ✅ No nested conditionals beyond 3 levels
- ✅ Early returns preferred over nested ternaries

**Tool Usage Philosophy**:
- ✅ Use ripgrep for @IMMUTABLE scanning (existing tool, not custom parser)
- ✅ Use Git for checkpoint creation (existing tool, not custom DB)
- ✅ Use Python stdlib subprocess (no new dependencies)
- ✅ No custom AST parsers (Constitution: "prefer existing tools over building custom")

### Section V: TRUST 5 Principles ✅

**Status**: PASS

**T - Test First**:
- ✅ TDD workflow enforced (tests before implementation)
- ✅ Coverage ≥85% (target: ≥95% for security features)
- ✅ Critical paths 100%: @IMMUTABLE protection, fail-open behavior

**R - Readable**:
- ✅ File size ≤500 SLOC (all files compliant)
- ✅ Function size ≤100 LOC (all functions compliant)
- ✅ Parameters ≤5 per function
- ✅ Nesting depth ≤4 levels
- ✅ Complexity ≤10 per function (actual: ≤5)

**U - Unified**:
- ✅ Python type hints on all functions (mypy strict mode compatible)
- ✅ Explicit types over implicit (no `any` abuse)
- ✅ SPEC-driven architecture (all implementations start from spec.md)
- ✅ @TAG system ensures traceability (@SPEC → @TEST → @CODE)

**S - Secured**:
- ✅ Input validation: Justification ≥10 chars (unlock validation)
- ✅ No secrets in code (audit log path is fixed, no user-controlled paths)
- ✅ Fail-open security: Errors logged to stderr with full context
- ✅ Audit trail: All unlocks logged with timestamp, justification, Git checkpoint
- ✅ Session-scoped security: Unlock registry cleared on SessionEnd

**T - Trackable**:
- ✅ Complete TAG chains: @SPEC → @TEST → @CODE
- ✅ TAG integrity validation improved (scan .md files)
- ✅ No orphaned TAGs (doc-updater agent reports broken chains)

### Section X: Agentic Behavior Standards ✅

**Status**: PASS

**Fail-Open Principle**:
- ✅ All hook errors exit with code 0 (FR-001, FR-002)
- ✅ Error details printed to stderr (full stack traces)
- ✅ SystemMessage includes error summary for user visibility
- ✅ Fail-open payload: `{"continue": True, "systemMessage": "..."}`

**Truth Verification**:
- ✅ All operations logged (audit log for unlocks, stderr for errors)
- ✅ Raw errors shown to user (no hiding failures)
- ✅ Checkpoint references provided for rollback

**Anti-Deception**:
- ✅ Explicit error messages (not "minor issues" or "successfully completed" on failure)
- ✅ Complete stack traces in logs
- ✅ Fail-open behavior clearly communicated to user

### Gates Summary

| Gate | Requirement | Status | Justification |
|------|-------------|--------|---------------|
| **Test Coverage** | ≥85% | ✅ PASS | ≥95% target for security features |
| **File Size** | ≤500 SLOC | ✅ PASS | All files <500 SLOC |
| **Function Size** | ≤100 LOC | ✅ PASS | All functions <100 LOC |
| **Complexity** | ≤10 per function | ✅ PASS | Actual complexity ≤5 (simple sequential logic) |
| **Type Safety** | 100% typed | ✅ PASS | Python type hints on all functions |
| **Security** | 0 HIGH/CRITICAL vulns | ✅ PASS | No new dependencies, stdlib only |
| **Fail-Open** | Exit 0 on errors | ✅ PASS | FR-001~004 enforce fail-open |

**Overall Constitution Compliance**: ✅ **PASS** - All gates satisfied, no violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-moai-adk-fixes/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (input)
├── research.md          # Phase 0 output (architectural research - GENERATED BELOW)
├── data-model.md        # Phase 1 output (entity relationships - GENERATED BELOW)
├── quickstart.md        # Phase 1 output (developer guide - GENERATED BELOW)
└── contracts/           # Phase 1 output (API contracts - GENERATED BELOW)
    ├── hook-events.yaml         # Hook system event contracts
    ├── immutable-api.yaml       # @IMMUTABLE protection API
    └── agent-delegation.yaml    # Agent delegation contracts
```

### Source Code (repository root)

```text
# Single project structure (existing codebase enhancement)
.claude/
├── hooks/
│   └── ms/
│       ├── ms_hooks.py                  # MODIFIED (exit 0 on all errors)
│       ├── core/
│       │   ├── __init__.py              # Unchanged
│       │   ├── project.py               # MODIFIED (TAG .md scan, SPEC Markdown parsing)
│       │   ├── checkpoint.py            # Unchanged
│       │   └── immutable_protection.py  # NEW (180 SLOC - scan, unlock, registry)
│       └── handlers/
│           ├── __init__.py              # Unchanged
│           ├── session.py               # MODIFIED (SessionEnd unlock clear)
│           ├── tool.py                  # MODIFIED (@IMMUTABLE protection)
│           └── user.py                  # Unchanged
├── commands/
│   ├── ms.unlock.md                     # NEW (80 SLOC - unlock command)
│   └── ms.up-docs.md                    # NEW (120 SLOC - doc sync command)
├── agents/
│   ├── doc-updater.md                   # Unchanged (relies on fixed project.py)
│   ├── implementation-planner.md        # MODIFIED (delegation recommendations)
│   └── quality-gate.md                  # NEW (250 SLOC - TRUST validation agent)
└── skills/
    ├── ms-essentials-debug/
    │   └── SKILL.md                     # NEW (300 SLOC - debugging patterns)
    └── ms-essentials-review/
        └── SKILL.md                     # NEW (320 SLOC - code review checklist)

tests/
└── hooks/
    ├── test_immutable_protection.py     # NEW (350 SLOC, ≥12 test cases)
    ├── test_user_prompt_submit.py       # NEW (400 SLOC, ≥15 test cases)
    └── test_project_metrics.py          # NEW (200 SLOC, ≥8 test cases)

.specify/
└── immutable_changes.log                # GENERATED (audit trail)
```

**Structure Decision**: Single project structure selected because this is an enhancement to the existing My-Spec CLI codebase (not a new web/mobile app). All modifications are within the `.claude/` directory (hook handlers, commands, agents, skills) and `tests/` directory (unit and integration tests). The project follows the existing My-Spec architecture with clear separation: hooks (infrastructure), commands (user-facing), agents (AI automation), skills (reusable patterns), and tests (quality validation).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All components satisfy Constitution constraints.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

**Notes**:
- All files ≤500 SLOC (largest: `test_user_prompt_submit.py` at 400 SLOC)
- All functions ≤100 LOC (largest: `unlock_file()` at ~60 LOC)
- All complexities ≤10 (actual: ≤5 using simple sequential logic)
- No new external dependencies (Python stdlib only)
- No custom AST parsers (ripgrep for scanning per Constitution Section II)

---

## Phase 0: Research & Unknowns

### Research Tasks

**Task 1: ripgrep Advanced Features for .md File Scanning**
- **Question**: How to configure ripgrep to scan custom file types (`.md`) for TAG integrity?
- **Research Scope**: ripgrep `--type-add` flag syntax, performance implications, timeout handling
- **Outcome Required**: Confirmed syntax for `.md` scanning, expected performance (<5 seconds)

**Task 2: Git Checkpoint Best Practices**
- **Question**: What is the safest Git workflow for creating automatic checkpoints without interfering with user's branch state?
- **Research Scope**: `git checkout -b` vs `git tag`, branch naming conventions, rollback procedures
- **Outcome Required**: Checkpoint creation command, rollback instructions, safety guarantees

**Task 3: Python Session State Management Patterns**
- **Question**: How to implement session-scoped singleton for UnlockRegistry that clears on SessionEnd?
- **Research Scope**: Python singleton patterns, lifecycle management, memory cleanup
- **Outcome Required**: Singleton implementation pattern, SessionEnd integration approach

**Task 4: pytest Mocking Strategies for subprocess**
- **Question**: How to mock `subprocess.run()` calls for ripgrep/git in unit tests without real system dependencies?
- **Research Scope**: pytest monkeypatch, subprocess mocking, fixture design
- **Outcome Required**: Mocking patterns for ripgrep success/failure, git checkpoint success/failure

**Task 5: MoAI-ADK 7-Section Skill Template**
- **Question**: What is the exact structure of the 7-section Skill template used in MoAI-ADK reference implementation?
- **Research Scope**: Review `docs/references/moai-adk/skills/moai-essentials-debug.md`, extract template structure
- **Outcome Required**: 7-section template format (Metadata, What It Does, When to Use, How It Works, Failure Modes, Best Practices, Examples)

**Task 6: Agent Delegation Pattern (Passive Recommendations)**
- **Question**: How should agents recommend delegation without directly invoking Task tool (separation of concerns)?
- **Research Scope**: Review MoAI-ADK agent collaboration examples, passive vs active patterns
- **Outcome Required**: Markdown recommendation format, command parsing strategy

### Research Findings (Consolidated)

**Decision Matrix**:

| Research Task | Decision | Rationale | Alternatives Considered |
|---------------|----------|-----------|------------------------|
| **ripgrep .md scanning** | Use `--type-add 'md:*.md' --type md` | ripgrep natively supports custom types, <1ms per file performance | Custom Python file walker (rejected: slower, more complex) |
| **Git checkpoint** | Use `git checkout -b checkpoint/immutable-unlock-{timestamp}` | Creates isolated branch, easy rollback via `git checkout {ref}`, doesn't interfere with user's working branch | Git tags (rejected: harder to find, not branch-isolated), stash (rejected: only one stash per branch) |
| **Session state** | Singleton with `__new__` override, cleared in `handle_session_end()` | Python singleton pattern is simple, SessionEnd hook provides clear lifecycle trigger | Global variable (rejected: harder to test, no encapsulation), database (rejected: violates CODE-FIRST principle) |
| **pytest mocking** | Use `monkeypatch.setattr(subprocess, "run", mock_fn)` | pytest built-in, isolates tests from system, enables error injection | unittest.mock (rejected: more verbose), real subprocess calls (rejected: requires ripgrep/git installed) |
| **7-section template** | Metadata → What It Does → When to Use → How It Works → Failure Modes → Best Practices → Examples | Proven structure from MoAI-ADK, consistent with existing 9 Skills | Custom structure (rejected: breaks consistency), flat structure (rejected: harder to navigate) |
| **Agent delegation** | Agents output Markdown recommendation, commands parse and execute Task tool | Clear separation of concerns: agents recommend (passive), commands execute (active) | Agents call Task directly (rejected: violates separation, harder to test) |

**Key Findings Summary**:
1. ripgrep `--type-add` is performant and simple (no custom file walker needed)
2. Git checkpoint branches provide safe rollback without interfering with user workflow
3. Python singleton with SessionEnd lifecycle hook is the simplest session state solution
4. pytest monkeypatch enables comprehensive mocking without system dependencies
5. MoAI-ADK 7-section template is proven and consistent with existing Skills
6. Passive delegation (agents recommend, commands execute) maintains clean architecture

---

## Phase 1: Design & Contracts

### Data Model

**Entity 1: Hook Event**
- **Purpose**: Represents Claude Code lifecycle events (SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, SessionEnd)
- **Fields**:
  - `event_type`: str (SessionStart | PreToolUse | PostToolUse | UserPromptSubmit | SessionEnd)
  - `payload`: dict (event-specific data: tool name, arguments, user prompt, cwd)
  - `timestamp`: datetime
- **Relationships**: Triggers HookHandler → returns HookResult
- **Validation**: Event type must be one of the 5 recognized types

**Entity 2: Hook Result**
- **Purpose**: Represents outcome of hook handler execution
- **Fields**:
  - `continue_execution`: bool (True = allow operation, False = block)
  - `system_message`: str | None (user-facing message, warnings, errors)
  - `additional_context`: str | None (UserPromptSubmit only: Constitution content)
  - `checkpoint_created`: bool (PreToolUse only: Git checkpoint status)
- **Relationships**: Returned by HookHandler → consumed by Claude Code
- **Validation**: If `continue_execution=False`, `system_message` is required

**Entity 3: IMMUTABLE Protection State**
- **Purpose**: Session-scoped dictionary tracking unlocked files
- **Fields**:
  - `file_path`: str (absolute or relative path)
  - `unlock_timestamp`: datetime
  - `justification`: str (≥10 chars, reason for unlock)
  - `session_id`: str (format: `session-{YYYYMMDD-HHMMSS}`)
  - `git_checkpoint_ref`: str (Git branch name: `checkpoint/immutable-unlock-{timestamp}`)
- **Relationships**: Managed by UnlockRegistry (singleton), cleared on SessionEnd
- **State Transitions**:
  - `locked` (initial) → `unlocked` (via `/ms.unlock`) → `locked` (on SessionEnd)
- **Validation**: Justification must be ≥10 chars, checkpoint ref must start with `checkpoint/`

**Entity 4: Unlock Audit Entry**
- **Purpose**: Persistent log record of all unlock operations
- **Fields**:
  - `timestamp`: ISO 8601 datetime
  - `file_path`: str
  - `justification`: str
  - `session_id`: str
  - `git_checkpoint_ref`: str
  - `user_environment`: str (optional: USER, PWD env vars)
- **Storage**: Append-only text file (`.specify/immutable_changes.log`)
- **Format**: `[{timestamp}] File: {file_path} | Session: {session_id} | Checkpoint: {checkpoint_ref} | Justification: {justification}`
- **Relationships**: Created by `unlock_file()`, read by audit reviews
- **Validation**: All fields required except `user_environment`

**Entity 5: TAG Chain**
- **Purpose**: Traceability link connecting @SPEC → @TEST → @CODE → @DOC tags
- **Fields**:
  - `tag_type`: str (@SPEC | @TEST | @CODE | @DOC)
  - `tag_id`: str (e.g., AUTH-001)
  - `file_path`: str (where tag is located)
  - `line_number`: int
  - `chain_status`: str (complete | broken | orphan)
    - `complete`: @SPEC → @TEST → @CODE all present
    - `broken`: @SPEC exists but @TEST or @CODE missing
    - `orphan`: @CODE exists but no corresponding @SPEC
- **Relationships**: Scanned by `calculate_tag_integrity()`, reported by doc-updater agent
- **Validation**: `tag_id` must be unique across project, `tag_type` must be one of 4 types

**Entity 6: Skill**
- **Purpose**: Markdown documentation file following 7-section template
- **Fields**:
  - `name`: str (e.g., ms-essentials-debug)
  - `version`: str (semver format, e.g., 1.0.0)
  - `model`: str (all | haiku | sonnet | opus - which AI models can use this Skill)
  - `keywords`: list[str] (tags for skill discovery)
  - `content_sections`: dict[str, str] (7 sections: Metadata, What It Does, When to Use, How It Works, Failure Modes, Best Practices, Examples)
  - `constitution_references`: list[str] (links to Constitution sections)
- **Storage**: `.claude/skills/{name}/SKILL.md`
- **Format**: YAML frontmatter + Markdown content
- **Validation**: All 7 sections must be present, version must be semver, keywords must be non-empty

**Entity 7: Agent Delegation Recommendation**
- **Purpose**: Agent output recommending sub-agent invocation (passive pattern)
- **Fields**:
  - `recommended_subagent_type`: str (library-researcher | codebase-explorer | trust-validator | tag-auditor)
  - `delegation_prompt`: str (prompt to pass to sub-agent)
  - `rationale`: str (why delegation is needed)
  - `expected_output_format`: str (what command should expect from sub-agent)
- **Format**: Markdown section in agent output (not a data structure)
- **Example**:
  ```markdown
  ## Library Research Required

  📚 **Delegation Recommendation**: library-researcher
  **Prompt**: "Research JWT library for Node.js. Topics: signing, verification, latest stable version."
  **Rationale**: Need library version beyond knowledge cutoff.
  **Expected Output**: Library version recommendation, API patterns.
  ```
- **Relationships**: Generated by agent → parsed by command → executed via Task tool
- **Validation**: Must include all 4 fields (subagent_type, prompt, rationale, expected_output)

**Entity 8: Document Sync Report**
- **Purpose**: Output of doc-updater agent 3-phase workflow
- **Fields**:
  - `sync_mode`: str (staged | all | docs=api | docs=dev | docs=readme)
  - `files_updated`: list[str] (paths of updated docs)
  - `tag_integrity_score`: float (percentage, e.g., 95.5)
  - `tag_statistics`: dict[str, int] (total_tags, complete_chains, broken_chains, orphan_tags)
  - `warnings`: list[str] (orphan TAGs, broken chains)
  - `duration_seconds`: float
- **Relationships**: Generated by doc-updater agent → displayed to user
- **Validation**: `tag_integrity_score` must be 0.0-100.0, `duration_seconds` must be >0

**Entity Relationship Diagram**:

```
┌─────────────────┐
│   Hook Event    │
│  (input)        │
└────────┬────────┘
         │ triggers
         ▼
┌─────────────────┐      ┌──────────────────────┐
│  HookHandler    │─────▶│   Hook Result        │
│  (process)      │      │   (output)           │
└────────┬────────┘      └──────────────────────┘
         │
         │ uses
         ▼
┌─────────────────────────────────────────────────┐
│  IMMUTABLE Protection State (session-scoped)    │
│  - UnlockRegistry (singleton)                   │
│  - file_path, timestamp, justification          │
└───────────┬─────────────────────────────────────┘
            │ persists to
            ▼
┌─────────────────────────────────────────────────┐
│  Unlock Audit Entry (persistent log)            │
│  - .specify/immutable_changes.log               │
└─────────────────────────────────────────────────┘

┌─────────────────┐
│   TAG Chain     │─────┐
│  (@SPEC→@TEST   │     │ scanned by
│   →@CODE→@DOC)  │     │
└─────────────────┘     │
                        ▼
                ┌───────────────────────┐
                │ calculate_tag_        │
                │ integrity()           │
                │ (core/project.py)     │
                └───────────────────────┘

┌─────────────────┐
│     Skill       │
│  (7-section     │
│   template)     │
└─────────────────┘

┌─────────────────────────┐
│ Agent Delegation        │
│ Recommendation          │
│ (passive Markdown)      │
└────────┬────────────────┘
         │ parsed by
         ▼
┌─────────────────────────┐
│  Command Orchestration  │
│  (executes Task tool)   │
└─────────────────────────┘
```

### API Contracts

See `/contracts/` directory for OpenAPI specifications:

**Contract 1: Hook Events API** (`contracts/hook-events.yaml`)
- **Description**: Claude Code hook system event contracts
- **Events**: SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, SessionEnd
- **Input Schema**: Event type + payload (JSON)
- **Output Schema**: HookResult (continue_execution, system_message, additional_context)
- **Error Handling**: All errors result in fail-open payload (exit code 0)

**Contract 2: IMMUTABLE Protection API** (`contracts/immutable-api.yaml`)
- **Description**: @IMMUTABLE file protection and unlock mechanism
- **Endpoints**:
  - `scan_immutable_marker(file_path: str) -> bool`: Scan for marker
  - `is_file_unlocked(file_path: str) -> bool`: Check unlock status
  - `unlock_file(file_path: str, justification: str, cwd: str) -> UnlockResult`: Unlock with checkpoint
- **Error Handling**: Fail-open on scan errors (return False, allow edit with warning)
- **State Management**: Session-scoped unlock registry (singleton), cleared on SessionEnd

**Contract 3: Agent Delegation API** (`contracts/agent-delegation.yaml`)
- **Description**: Agent-to-agent delegation via passive recommendations
- **Pattern**: Agents recommend (Markdown output) → Commands execute (Task tool invocation)
- **Delegation Flow**:
  1. Agent analyzes task → outputs delegation recommendation (Markdown)
  2. Command parses recommendation → extracts subagent_type, prompt
  3. Command executes `Task(subagent_type="...", prompt="...")`
  4. Sub-agent returns results → command incorporates into workflow
- **Supported Delegations**:
  - `implementation-planner` → `library-researcher` (library research)
  - `implementation-planner` → `codebase-explorer` (architectural patterns)
  - `quality-gate` → `trust-validator` (TRUST 5 validation)
  - `quality-gate` → `tag-auditor` (TAG chain verification)

**Sample Hook Event Request** (PreToolUse with Edit tool):
```json
{
  "event": "PreToolUse",
  "payload": {
    "tool": "Edit",
    "arguments": {
      "file_path": "/workspace/specter/src/auth.py",
      "old_string": "...",
      "new_string": "..."
    },
    "cwd": "/workspace/specter"
  }
}
```

**Sample Hook Result Response** (Blocked by @IMMUTABLE):
```json
{
  "continue": false,
  "systemMessage": "🚫 File protected by @IMMUTABLE marker.\n   File: /workspace/specter/src/auth.py\n   Unlock: Run `/ms.unlock /workspace/specter/src/auth.py` to edit.\n   Reason: Critical file requires explicit unlock with audit trail."
}
```

**Sample Hook Result Response** (Fail-Open on Error):
```json
{
  "continue": true,
  "systemMessage": "⚠️ Hook warning: ripgrep not installed - @IMMUTABLE scan skipped.\n   Install ripgrep: https://github.com/BurntSushi/ripgrep\n   Operation allowed (fail-open principle)."
}
```

**Sample Unlock API Call**:
```python
from core.immutable_protection import unlock_file

result = unlock_file(
    file_path="/workspace/specter/src/auth.py",
    justification="Fix critical authentication bypass CVE-2024-12345",
    cwd="/workspace/specter"
)

if result.success:
    print(f"✅ File unlocked. Checkpoint: {result.checkpoint_ref}")
    print(f"🔄 Rollback: git checkout {result.checkpoint_ref}")
else:
    print(f"❌ Unlock failed: {result.error_message}")
```

**Sample Agent Delegation Recommendation** (implementation-planner → library-researcher):
```markdown
## Library Research Required

📚 **Delegation Recommendation**: library-researcher

**Libraries to research**:
- jsonwebtoken (JWT signing/verification for Node.js)

**Prompt**: "Research jsonwebtoken library for Node.js. Topics: signing, verification, latest stable version, breaking changes since v8.x. Return version recommendation and API patterns."

**Rationale**: JWT library version selection requires latest documentation beyond AI knowledge cutoff (January 2025).

**Expected Output**:
- Library version recommendation (e.g., jsonwebtoken@9.0.2)
- API patterns for signing and verification
- Breaking changes to consider
```

### Developer Quickstart Guide

See `quickstart.md` for comprehensive developer onboarding. Key sections:

**1. Prerequisites**
- Python 3.13+ (free-threading support for hook system)
- ripgrep 13.0+ (install via `brew install ripgrep` or `apt install ripgrep`)
- Git 2.30+ (checkpoint creation)
- pytest 8.4.2 (`pip install pytest`)

**2. Installation**
```bash
# Clone repository
git clone <repo-url>
cd specter

# Checkout feature branch
git checkout 001-moai-adk-fixes

# Install Python dependencies (no new packages, stdlib only)
# Verify ripgrep installed
rg --version  # Should show 13.0+

# Verify Git installed
git --version  # Should show 2.30+
```

**3. Running Tests**
```bash
# Run all tests with coverage
pytest tests/hooks/ --cov=.claude/hooks/ms --cov-report=term-missing

# Run specific test suite
pytest tests/hooks/test_immutable_protection.py -v

# Run integration tests
pytest tests/hooks/ -k integration -v
```

**4. Development Workflow**
```bash
# Step 1: Write failing test (TDD RED phase)
# Edit tests/hooks/test_immutable_protection.py
pytest tests/hooks/test_immutable_protection.py::test_scan_detects_immutable_marker
# Expected: FAIL

# Step 2: Implement minimum code (TDD GREEN phase)
# Edit .claude/hooks/ms/core/immutable_protection.py
pytest tests/hooks/test_immutable_protection.py::test_scan_detects_immutable_marker
# Expected: PASS

# Step 3: Refactor while keeping tests green (TDD REFACTOR phase)
pytest tests/hooks/ --cov=.claude/hooks/ms --cov-report=term-missing
# Expected: Coverage ≥85%
```

**5. Testing @IMMUTABLE Protection Manually**
```bash
# Step 1: Create test file with @IMMUTABLE marker
echo "# @IMMUTABLE - Critical module" > test_protected.py

# Step 2: Attempt edit (should be blocked)
# Trigger PreToolUse event via Claude Code Edit tool
# Expected: "🚫 File protected by @IMMUTABLE. Use `/ms.unlock` to edit."

# Step 3: Unlock file
/ms.unlock test_protected.py
# Enter justification: "Testing unlock mechanism for development"
# Expected: "✅ File unlocked. Checkpoint: checkpoint/immutable-unlock-20251026-143000"

# Step 4: Verify edit now allowed
# Trigger PreToolUse event again
# Expected: Edit proceeds normally

# Step 5: End session and verify protection re-applied
# Trigger SessionEnd event
# Start new Claude Code session
# Trigger PreToolUse event
# Expected: "🚫 File protected by @IMMUTABLE" (unlock cleared)
```

**6. Key Files to Modify**

| File | Purpose | SLOC | Status |
|------|---------|------|--------|
| `.claude/hooks/ms/ms_hooks.py` | Hook entry point | 195 | MODIFY (exit 0 on errors) |
| `.claude/hooks/ms/core/immutable_protection.py` | @IMMUTABLE protection | 180 | NEW |
| `.claude/hooks/ms/handlers/tool.py` | PreToolUse handler | 280 | MODIFY (@IMMUTABLE scan) |
| `.claude/hooks/ms/core/project.py` | Metrics calculation | 311 | MODIFY (TAG .md scan) |
| `tests/hooks/test_immutable_protection.py` | Unit tests | 350 | NEW |

**7. Common Pitfalls**
- **Forgetting to exit with code 0**: All hook errors MUST exit with code 0 (fail-open principle)
- **Hardcoding file paths**: Use `Path(cwd) / ".specify/..."` for portability
- **Skipping tests**: TDD is NON-NEGOTIABLE per Constitution Section I
- **Session state persistence**: UnlockRegistry is session-scoped (does NOT persist across sessions by design)
- **Ripgrep not installed**: @IMMUTABLE scan will fail-open (allow edit with warning)

**8. Debugging Tips**
```bash
# Enable verbose hook logging
export HOOK_DEBUG=1

# Run hooks manually for testing
echo '{"tool": "Edit", "arguments": {"file_path": "test.py"}, "cwd": "."}' | \
  python .claude/hooks/ms/ms_hooks.py PreToolUse

# Check audit log
cat .specify/immutable_changes.log

# Verify TAG integrity
rg '@(SPEC|TEST|CODE|DOC):' -n --type md --type py --type ts
```

---

## Phase 2: Implementation Tasks

**Note**: Detailed task breakdown is created by `/speckit.tasks` command (not part of `/speckit.plan` output).

**High-Level Task Groups** (to be decomposed in tasks.md):

1. **Hook System Fail-Open** (P0 - Week 1)
   - Fix `ms_hooks.py` exit codes (FR-001~004)
   - Comprehensive tests for fail-open behavior
   - Validation: All hook errors exit with code 0

2. **@IMMUTABLE Protection** (P0 - Week 1)
   - Implement `core/immutable_protection.py` (FR-005~010)
   - Modify `handlers/tool.py` for PreToolUse scanning
   - Create `/ms.unlock` command
   - Comprehensive tests (≥12 test cases)
   - Integration test for full unlock lifecycle
   - Validation: Edit blocked until unlock, protection re-applies on SessionEnd

3. **Metrics Accuracy** (P0 - Week 1)
   - Fix `calculate_tag_integrity()` to scan .md files (FR-026~027)
   - Fix `count_specs()` to parse Markdown metadata (FR-028~029)
   - Tests for metrics accuracy
   - Validation: SessionStart dashboard shows non-zero integrity and SPEC progress

4. **Skills Completion** (P1 - Week 2)
   - Create `ms-essentials-debug/SKILL.md` (FR-014)
   - Create `ms-essentials-review/SKILL.md` (FR-015)
   - Validation: 11/11 Skills complete, 7-section template followed

5. **Document Automation** (P1 - Week 2)
   - Create `/ms.up-docs` command (FR-018)
   - Verify doc-updater agent 3-phase workflow (FR-019~021)
   - Integration test for document sync E2E
   - Validation: API docs generated, dev daily updated, TAG integrity report accurate

6. **Agent Delegation** (P1 - Week 2)
   - Add delegation logic to `implementation-planner.md` (FR-022)
   - Create `quality-gate.md` agent (FR-023)
   - Update commands to parse delegation recommendations (FR-024~025)
   - Integration test for delegation chain
   - Validation: implementation-planner → library-researcher, quality-gate → trust-validator

7. **Integration & Documentation** (P2 - Week 3)
   - Run full test suite (≥85% coverage)
   - Update README with new features (FR-030)
   - Run `/fin` quality gate
   - User acceptance testing
   - Validation: All 12 issues resolved, all tests pass

---

## Success Criteria

**SC-001**: Developer workflows NOT blocked by hook errors
- ✅ Metric: 100% of hook failures result in exit code 0
- ✅ Test: Trigger JSON parse error, verify session continues with warning

**SC-002**: Critical files with @IMMUTABLE markers protected
- ✅ Metric: 100% of edit attempts blocked until explicit unlock
- ✅ Test: Attempt Edit on @IMMUTABLE file, verify block message, unlock, verify edit allowed

**SC-003**: Test coverage meets Constitution requirements
- ✅ Metric: ≥85% coverage for all hook handlers (target: ≥95%)
- ✅ Test: Run `pytest --cov`, verify coverage report

**SC-004**: Skills ecosystem complete
- ✅ Metric: 11/11 Skills implemented (9 existing + 2 new)
- ✅ Test: Verify `ms-essentials-debug` and `ms-essentials-review` exist, follow 7-section template

**SC-005**: Living Documents stay synchronized
- ✅ Metric: doc-updater completes 3-phase sync in <10 seconds
- ✅ Test: Run `/ms.up-docs`, verify API docs generated, dev daily updated, duration <10s

**SC-006**: Multi-agent workflows enable delegation
- ✅ Metric: implementation-planner and quality-gate delegate to ≥2 sub-agents per workflow
- ✅ Test: Run `/ms.plan`, verify library-researcher recommendation, verify Task tool invocation

**SC-007**: Project metrics accurate
- ✅ Metric: TAG integrity and SPEC progress display non-zero values (not 0% due to scanning bugs)
- ✅ Test: Create @SPEC tags in .md files, verify SessionStart dashboard shows non-zero integrity

**SC-008**: Developer experience improved
- ✅ Metric: SessionStart dashboard shows accurate metrics, unlock workflow <30 seconds
- ✅ Test: SessionStart displays TAG integrity %, unlock completes with checkpoint in <30s

**SC-009**: Audit trail complete
- ✅ Metric: 100% of @IMMUTABLE unlocks logged with timestamp, justification, checkpoint
- ✅ Test: Unlock file, verify `.specify/immutable_changes.log` contains entry

**SC-010**: Constitution compliance maintained
- ✅ Metric: All files ≤500 SLOC, functions ≤100 LOC, complexity ≤10
- ✅ Test: Run SLOC counter, complexity analyzer (ESLint/Pylint), verify all files compliant

---

## Risk Mitigation

**Risk 1: @IMMUTABLE Protection Breaks Workflows**
- **Probability**: Medium | **Impact**: High
- **Mitigation**: Comprehensive testing (≥12 test cases), fail-open on scan errors, clear unlock documentation, Git checkpoint for instant rollback
- **Validation**: Integration test for full unlock lifecycle, ripgrep failure triggers fail-open

**Risk 2: Hook Fail-Open Masks Critical Errors**
- **Probability**: Low | **Impact**: Medium
- **Mitigation**: All errors to stderr with stack traces, systemMessage warnings visible in UI, SessionStart dashboard shows hook health
- **Validation**: Manual review of stderr logs, systemMessage visibility test

**Risk 3: TAG Integrity Scan Performance Degrades**
- **Probability**: Low | **Impact**: Low
- **Mitigation**: ripgrep is extremely fast (<1s for 10k files), 5-second timeout prevents hanging, scan runs only on SessionStart
- **Validation**: Performance test with 10k files, verify <5s completion

**Risk 4: Agent Delegation Complexity Confuses Users**
- **Probability**: Medium | **Impact**: Medium
- **Mitigation**: Clear separation (agents recommend, commands execute), documentation with examples, graceful degradation if Task tool unavailable
- **Validation**: Integration test demonstrating delegation chain, user review of documentation

**Risk 5: Test Coverage Insufficient for Edge Cases**
- **Probability**: Low | **Impact**: Medium
- **Mitigation**: Minimum 15 test cases for UserPromptSubmit, 12 for @IMMUTABLE, 10 documented edge cases in spec, quality-gate validation
- **Validation**: Coverage report ≥85%, edge case tests included (timeout, Git errors, malformed JSON)

**Risk 6: Skills Content Inconsistency**
- **Probability**: Low | **Impact**: Low
- **Mitigation**: Base on MoAI-ADK proven patterns, 7-section template consistency, Constitution references
- **Validation**: User review of Skills content before merge

---

## Next Steps

1. **Review this plan** with user for approval
2. **Run `/ms.constitution`** to extract project-specific constraints
3. **Run `/speckit.tasks`** to generate detailed task breakdown (tasks.md)
4. **Begin implementation** following TDD workflow (RED → GREEN → REFACTOR)
5. **Run `/fin`** quality gate before final commit

---

## 📜 Constitution

This plan follows the project [Constitution](../../.specify/memory/constitution.md).

**Key Sections Applied:**
- **Section I**: Test-First Development (TDD) - All features require ≥85% test coverage, tests written before implementation
- **Section II**: Simplicity-First Architecture - Files ≤500 SLOC, functions ≤100 LOC, complexity ≤10, prefer existing tools (ripgrep) over custom parsers
- **Section IV**: Requirements Clarity (EARS Standards) - All requirements use EARS patterns (WHEN/SHALL/WHILE/WHERE/IF) for unambiguous specification
- **Section V**: TRUST 5 Quality Principles - Test-First (≥85% coverage), Readable (size/complexity limits), Unified (SPEC-driven), Secured (input validation, audit logging), Trackable (@TAG system)
- **Section X**: Agentic Behavior Standards - Fail-open principle (hook errors don't block workflows), truth verification (all operations logged), anti-deception (show raw errors)

**Constitution Compliance Summary**:
- ✅ All gates satisfied (Test Coverage ≥85%, File Size ≤500 SLOC, Function Size ≤100 LOC, Complexity ≤10)
- ✅ No violations requiring justification
- ✅ Fail-open principle enforced (all hook errors exit code 0)
- ✅ TDD workflow mandatory (RED → GREEN → REFACTOR)
- ✅ Security by default (input validation, audit logging, session-scoped state)

_Auto-added by `/ms.plan`_

# Feature Specification: MoAI-ADK Integration Fixes

**Feature Branch**: `001-moai-adk-fixes`
**Created**: 2025-10-26
**Status**: Draft
**Priority**: P0 (Critical)
**Type**: Existing Project Update
**Input**: User description: "Fix 12 critical issues discovered during MoAI-ADK integration verification: fail-open violations, missing @IMMUTABLE protection, incomplete Skills implementation, and missing agent automation"

## Executive Summary

System SHALL fix 12 critical issues discovered during MoAI-ADK integration verification. These issues include fail-open violations, missing safety features, incomplete Skills implementation, and missing agent automation that are explicitly required by the integration specification but were not implemented or incorrectly implemented.

**Scope**: Bug fixes and missing feature implementation for MoAI-ADK integration
**Impact**: Workflow blocking (fail-open), safety regression (@IMMUTABLE), incomplete Spec compliance
**Verification Source**: Combined analysis from Claude Code + Codex (2025-10-26)

## User Scenarios & Testing

### User Story 1 - Safe Hook Failure Handling (Priority: P0)

WHEN hook system encounters errors (JSON parsing failures, handler exceptions), Claude Code sessions MUST continue without blocking user workflows, WHILE displaying clear error messages to help diagnose issues.

**Why this priority**: Critical blocker - current exit code 1 terminates Claude Code sessions, making the system unusable when hooks fail.

**Independent Test**: Can be fully tested by triggering a JSON parse error in hook input and verifying Claude Code session continues with warning message.

**Acceptance Scenarios**:

1. **Given** hook receives malformed JSON input, **When** JSON parsing fails, **Then** system prints error to stderr, outputs fail-open payload `{"continue": True}`, and exits with code 0
2. **Given** hook handler throws exception, **When** exception is caught, **Then** system prints error to stderr, outputs fail-open payload, and exits with code 0
3. **Given** any hook error occurs, **When** fail-open triggers, **Then** Claude Code session continues normally with warning message displayed to user

---

### User Story 2 - Protected File Safety (Priority: P0)

WHEN developer attempts to edit critical files marked with @IMMUTABLE protection, system MUST block the edit and prompt for explicit unlock with justification, creating Git checkpoint for rollback.

**Why this priority**: Critical safety feature - prevents accidental modification of security-critical code (authentication, payment, core infrastructure) without audit trail.

**Independent Test**: Can be fully tested by creating a file with @IMMUTABLE marker, attempting edit via Claude Code, verifying block message, using unlock command, and confirming edit allowed.

**Acceptance Scenarios**:

1. **Given** file contains @IMMUTABLE marker, **When** developer attempts Edit/Write, **Then** system blocks operation with error "🚫 File protected by @IMMUTABLE. Use `/ms.unlock <file>` to edit."
2. **Given** developer runs `/ms.unlock <file>`, **When** unlock executes, **Then** system creates Git checkpoint, prompts for justification (≥10 chars), logs to audit file, and adds file to session unlock list
3. **Given** file unlocked in current session, **When** developer attempts Edit/Write, **Then** operation proceeds normally
4. **Given** new Claude Code session starts, **When** developer attempts edit on previously unlocked file, **Then** protection re-applies (unlock is session-scoped)

---

### User Story 3 - Complete Skills Ecosystem (Priority: P1)

WHEN developer encounters errors or needs code review guidance, system MUST provide specialized Skills (ms-essentials-debug, ms-essentials-review) with proven patterns from MoAI-ADK reference implementation.

**Why this priority**: High value - completes the Skills ecosystem (from 7/11 to 11/11 implemented), directly improves developer productivity during debugging and code review phases.

**Independent Test**: Can be fully tested by invoking each Skill independently, verifying content follows 7-section template, and confirming integration with agent workflows.

**Acceptance Scenarios**:

1. **Given** developer encounters runtime error, **When** ms-essentials-debug Skill is invoked, **Then** Skill provides stack trace analysis patterns, error pattern recognition (NoneType, undefined, async), and debugging steps
2. **Given** developer completes feature implementation, **When** ms-essentials-review Skill is invoked, **Then** Skill provides code review checklist covering quality, security, performance, tests, and documentation
3. **Given** Skills are implemented, **When** agent prompts reference them, **Then** agents can leverage Skill content for enhanced guidance

---

### User Story 4 - Automated Document Synchronization (Priority: P1)

WHEN developer runs document update command, system MUST automatically delegate to doc-updater agent which analyzes Git changes, syncs Living Documents (API docs, dev daily, README), and validates TAG chains.

**Why this priority**: High value - automates manual documentation workflow, ensures Living Documents stay synchronized with code changes, maintains TAG traceability integrity.

**Independent Test**: Can be fully tested by making code changes, running `/ms.up-docs`, verifying agent generates documentation updates, and confirming TAG integrity report accuracy.

**Acceptance Scenarios**:

1. **Given** developer stages code changes with new @CODE tags, **When** `/ms.up-docs` executes, **Then** system delegates to doc-updater agent via Task tool
2. **Given** doc-updater agent analyzes changes, **When** agent completes Phase 1 (Git diff), **Then** agent extracts @CODE tags and identifies changed functions
3. **Given** agent completes Phase 2 (document sync), **When** parallel sync executes, **Then** agent generates API docs, appends to dev daily log, and updates README if needed
4. **Given** agent completes Phase 3 (TAG validation), **When** integrity check runs, **Then** agent scans all file types including .md files and reports accurate TAG chain completeness percentage

---

### User Story 5 - Multi-Agent Collaboration (Priority: P1)

WHEN developer runs planning or quality-gate commands, system MUST enable agent-to-agent delegation where implementation-planner can delegate to library-researcher/codebase-explorer, and quality-gate can delegate to trust-validator/tag-auditor.

**Why this priority**: High value - enables sophisticated multi-agent workflows, improves plan quality by leveraging specialized sub-agents for library research and codebase analysis.

**Independent Test**: Can be fully tested by running `/ms.plan` and verifying implementation-planner agent recommends delegation to library-researcher, then confirming command orchestration executes delegation and incorporates results.

**Acceptance Scenarios**:

1. **Given** user runs `/ms.plan` for feature requiring external library, **When** implementation-planner analyzes SPEC, **Then** agent returns recommendation "Delegate to library-researcher for [library] documentation"
2. **Given** command receives delegation recommendation, **When** command parses recommendation, **Then** command executes `Task(subagent_type="library-researcher", prompt="...")`
3. **Given** library-researcher completes research, **When** results return, **Then** implementation-planner incorporates library version recommendations and API patterns into plan.md
4. **Given** user runs `/fin` quality gate, **When** quality-gate agent executes, **Then** agent delegates to trust-validator for TRUST 5 validation and tag-auditor for TAG chain verification

---

### User Story 6 - Accurate Project Metrics (Priority: P2)

WHEN developer session starts or runs analysis commands, system MUST display accurate TAG integrity metrics (including .md files) and SPEC progress metrics (parsing Markdown metadata) in SessionStart dashboard.

**Why this priority**: Medium value - improves developer experience by showing correct progress tracking, but doesn't block core workflows.

**Independent Test**: Can be fully tested by creating @SPEC tags in .md files and **Status**: Completed in spec.md, then verifying SessionStart dashboard shows non-zero integrity and accurate SPEC completion percentage.

**Acceptance Scenarios**:

1. **Given** project has @SPEC tags in specs/*.md files, **When** calculate_tag_integrity() runs, **Then** ripgrep scans include --type-add 'md:*.md' and detects @SPEC tags
2. **Given** TAG scan completes, **When** integrity calculation runs, **Then** system reports (Complete Chains / Total TAGs) * 100% including .md file tags
3. **Given** spec.md files use Markdown metadata (**Status**: Completed), **When** count_specs() parses files, **Then** regex matches `**Status**: completed` pattern (case-insensitive)
4. **Given** SessionStart hook runs, **When** dashboard generates, **Then** user sees accurate TAG integrity score (not 0%) and SPEC completion percentage (not 0%)

---

### Edge Cases

- **What happens when ripgrep fails during @IMMUTABLE scan?** System catches exception, prints error to stderr, outputs fail-open payload, exits with code 0, allowing edit to proceed with warning (fail-open principle)
- **What happens when user unlocks @IMMUTABLE file but Git repository is not initialized?** Unlock command checks for .git directory, if missing displays error "Git repository required for checkpoints" and aborts unlock (user must initialize Git first)
- **What happens when calculate_tag_integrity() finds 0 tags?** System returns integrity score of 0.0% with message "No TAG chains found - run /ms.implement to generate @CODE tags"
- **What happens when doc-updater agent completes but finds broken TAG chains?** Agent returns sync report with warnings list: "Orphan TAGs: [AUTH-001], Broken chains: [@SPEC:PAY-003 missing @TEST]" and user reviews warnings
- **What happens when sub-agent delegation fails (Task tool unavailable)?** WHEN Task tool fails, system SHALL automatically switch to single-agent mode AND display informational message "Sub-agent delegation unavailable - proceeding with single-agent workflow"
- **What happens when UserPromptSubmit hook fails to load Constitution?** Hook catches FileNotFoundError, prints warning "Constitution not found - skipping injection", outputs `{"continue": True}`, session continues without Constitution context (fail-open)
- **What happens when unlock justification is less than 10 characters?** IF user fails justification validation 3 times (input <10 chars), system SHALL cancel unlock operation AND maintain file protection WITH error message "Unlock cancelled after 3 failed attempts"
- **What happens when multiple files match @IMMUTABLE pattern in single Edit operation?** System scans all files, if ANY file is @IMMUTABLE protected, blocks entire operation with message listing all protected files
- **What happens when TAG integrity scan times out (>5 seconds)?** IF TAG scan exceeds 5 seconds, system SHALL return partial results WITH warning message "TAG scan incomplete - timeout after 5s" indicating incomplete scan
- **What happens when SPEC counting finds malformed Markdown metadata?** Regex fails to match, file counted as incomplete (Draft status), system continues scanning other files

## Requirements

### Functional Requirements - CRITICAL (P0)

#### Hook System Fail-Open

- **FR-001**: WHEN ms_hooks.py encounters JSON parsing error, system SHALL exit with code 0 (not code 1) to comply with fail-open policy
- **FR-002**: WHEN ms_hooks.py handler throws exception, system SHALL exit with code 0 and print fail-open payload `{"continue": True, "systemMessage": None}`
- **FR-003**: WHEN hook error occurs, system SHALL print error details to stderr AND display warning banner in Claude Code session WHILE continuing execution
- **FR-004**: WHEN any hook error occurs, system SHALL display user-facing warning message without blocking workflow

#### @IMMUTABLE Protection

- **FR-005**: WHEN PreToolUse hook detects Edit/Write tool call, system SHALL scan target file for @IMMUTABLE marker using ripgrep AND block tool execution if marker is found
- **FR-006**: WHEN file contains @IMMUTABLE marker, system SHALL block Edit/Write operation completely and display error message with unlock instructions
- **FR-007**: System SHALL provide `/ms.unlock <file>` command that creates Git checkpoint, prompts for justification (≥10 chars), logs to audit file, and adds file to session unlock list
- **FR-008**: WHEN unlock succeeds, system SHALL track unlocked files in session-scoped state (in-memory dictionary cleared on session end)
- **FR-009**: System SHALL log all unlock operations to `.specify/immutable_changes.log` with timestamp, file path, justification, and session ID
- **FR-010**: WHEN new Claude Code session starts, system SHALL re-apply @IMMUTABLE protection to all files (unlock list does not persist)

#### Test Coverage

- **FR-011**: System SHALL provide comprehensive test suite for UserPromptSubmit hook with ≥15 test cases covering Constitution injection, fail-open, caching, and error handling
- **FR-012**: System SHALL provide comprehensive test suite for @IMMUTABLE protection with ≥12 test cases covering scan detection, block behavior, unlock mechanism, and session tracking
- **FR-013**: WHEN tests run, system SHALL achieve ≥85% code coverage for all hook handlers and core logic

### Functional Requirements - HIGH (P1)

#### Skills Implementation

- **FR-014**: System SHALL provide ms-essentials-debug Skill following 7-section template (Metadata, What It Does, When to Use, How It Works, Failure Modes, Best Practices, Examples)
- **FR-015**: System SHALL provide ms-essentials-review Skill following 7-section template with code review checklist covering quality, security, performance, tests, and documentation
- **FR-016**: WHEN Skills are implemented, system SHALL achieve 11/11 Skills completion (9 existing + 2 new)
- **FR-017**: Skills SHALL reference Constitution principles (TRUST, EARS, TAG system) in Best Practices section

#### Document Automation

- **FR-018**: WHEN user runs `/ms.up-docs`, system SHALL delegate to doc-updater agent via Task tool with arguments specifying sync mode (--all, --docs=type, or staged changes)
- **FR-019**: doc-updater agent SHALL execute 3-phase workflow: Phase 1 (Git diff analysis), Phase 2 (parallel document sync), Phase 3 (TAG chain validation)
- **FR-020**: WHEN Phase 2 executes, agent SHALL generate API docs from @CODE tags, append to dev daily log with timestamp, and update README if major changes detected
- **FR-021**: WHEN Phase 3 executes, agent SHALL call calculate_tag_integrity() with .md file scanning enabled and report orphan TAGs and broken chains

#### Agent Delegation

- **FR-022**: implementation-planner agent SHALL include delegation recommendation logic that analyzes SPEC and returns "Delegate to library-researcher for [library]" when external library research needed
- **FR-023**: quality-gate agent SHALL include delegation logic that executes trust-validator for TRUST 5 validation and tag-auditor for TAG chain verification
- **FR-024**: WHEN commands receive delegation recommendations, commands SHALL parse recommendations and execute Task tool with appropriate subagent_type
- **FR-025**: Agents SHALL follow pattern: agents recommend (passive Markdown prompts), commands execute (active orchestration)

### Functional Requirements - MEDIUM (P2)

#### Metrics Accuracy

- **FR-026**: WHEN calculate_tag_integrity() scans for TAGs, system SHALL include .md files using ripgrep `--type-add 'md:*.md'` flag
- **FR-027**: System SHALL scan file types: md, py, ts, js, sh for @SPEC, @TEST, @CODE, @DOC tags
- **FR-028**: WHEN count_specs() parses spec.md files, system SHALL use regex pattern `**Status**:\s*completed` (case-insensitive) instead of YAML frontmatter parsing
- **FR-029**: WHEN SessionStart dashboard generates, system SHALL display accurate TAG integrity score (including .md files) and SPEC completion percentage (Markdown metadata format)

### Functional Requirements - LOW (P3)

#### Documentation Cleanup

- **FR-030**: System SHALL replace `.moai` path references in Skills documentation with correct My-Spec paths (`.specify/memory/constitution.md`)

### Key Entities

- **Hook Event**: Represents Claude Code lifecycle events (SessionStart, PreToolUse, PostToolUse, UserPromptSubmit) with payload containing tool name, arguments, and context
- **Hook Result**: Represents hook execution outcome with fields: continue_execution (boolean), systemMessage (optional string), checkpoint_created (boolean)
- **IMMUTABLE Protection State**: Session-scoped dictionary tracking unlocked files with keys: file_path, unlock_timestamp, justification, session_id
- **Unlock Audit Entry**: Log record with fields: timestamp, file_path, justification, session_id, git_checkpoint_ref, user_environment
- **TAG Chain**: Traceability link connecting @SPEC → @TEST → @CODE → @DOC tags with fields: tag_type, tag_id, file_path, line_number, chain_status (complete/broken/orphan)
- **Skill**: Markdown documentation file following 7-section template with fields: name, version, model, keywords, content_sections, constitution_references
- **Agent Delegation Recommendation**: Agent output with fields: recommended_subagent_type, delegation_prompt, rationale, expected_output_format
- **Document Sync Report**: doc-updater agent output with fields: sync_mode, files_updated, tag_integrity_score, warnings, duration_seconds

## Success Criteria

### Measurable Outcomes

- **SC-001**: Developer workflows SHALL NOT be blocked by hook errors - 100% of hook failures result in fail-open continuation with warning messages
- **SC-002**: Critical files with @IMMUTABLE markers SHALL be protected - 100% of edit attempts blocked until explicit unlock with justification
- **SC-003**: Test coverage SHALL meet Constitution requirements - ≥85% coverage for all hook handlers and core protection logic
- **SC-004**: Skills ecosystem SHALL be complete - 11/11 Skills implemented following consistent 7-section template format
- **SC-005**: Living Documents SHALL stay synchronized with code - doc-updater agent completes 3-phase sync in under 10 seconds for typical feature changes
- **SC-006**: Multi-agent workflows SHALL enable sophisticated delegation - implementation-planner and quality-gate successfully delegate to 2+ sub-agents per workflow
- **SC-007**: Project metrics SHALL be accurate - TAG integrity and SPEC progress display non-zero values reflecting actual project state (not 0% due to scanning bugs)
- **SC-008**: Developer experience SHALL improve - SessionStart dashboard shows accurate progress metrics, unlock workflow completes in under 30 seconds with clear rollback instructions
- **SC-009**: Audit trail SHALL be complete - 100% of @IMMUTABLE unlocks logged with timestamp, justification, and Git checkpoint reference
- **SC-010**: System SHALL maintain Constitution compliance - all files ≤500 SLOC, functions ≤100 LOC, complexity ≤10 per function

## Assumptions

1. **Git repository initialized**: All @IMMUTABLE unlock operations assume .git directory exists (validated at runtime, error if missing)
2. **ripgrep installed**: TAG scanning and @IMMUTABLE detection assume `rg` command available in PATH (prerequisite check in setup)
3. **Python 3.13+ environment**: Hook system assumes Python 3.13+ with free-threading support (documented in requirements)
4. **Claude Code Task tool available**: Agent delegation assumes Task tool functional (graceful degradation to single-agent if unavailable)
5. **Existing 9 Skills**: Implementation assumes 9 existing Skills (ms-foundation-*, ms-workflow-*, ms-lang-*) follow 7-section template (verified by audit)
6. **MoAI-ADK reference available**: Skills content based on MoAI-ADK proven patterns documented in `docs/references/moai-adk/skills/`
7. **Session state in-memory**: @IMMUTABLE unlock tracking uses in-memory dictionary (no persistence across sessions by design)
8. **Fail-open default**: All hook errors default to continue execution unless explicitly requiring user intervention (safety over blocking)
9. **Markdown metadata format**: All SPEC files use `**Status**: [value]` format (not YAML frontmatter) as established by Spec-Kit workflow
10. **5-second timeout**: TAG integrity scanning uses 5-second ripgrep timeout (existing configuration maintained)

## Dependencies

### Internal Dependencies

- **Constitution compliance**: All implementations must follow Section I (TDD), Section II (Simplicity-First, file size limits), Section V (TRUST 5 principles)
- **Existing hook infrastructure**: `.claude/hooks/ms/` directory structure with handlers/ subdirectory and ms_hooks.py entry point
- **Existing agents**: 11 agents in `.claude/agents/` directory (implementation-planner, quality-gate, doc-updater, etc.)
- **Existing Skills**: 9 Skills in `.claude/skills/` directory following 7-section template
- **TAG system**: Existing @SPEC, @TEST, @CODE, @DOC tag conventions and traceability workflow
- **Spec-Kit templates**: `.specify/templates/` directory with spec-template.md and checklist templates

### External Dependencies

- **ripgrep (rg)**: Version 13.0+ for TAG scanning with --type-add support
- **Git**: Version 2.30+ for checkpoint creation via `git checkout -b checkpoint/...`
- **Python packages**: No new packages required (uses stdlib: subprocess, json, sys, re, pathlib)
- **Claude Code platform**: Hook system, Task tool, agent execution environment

### Specification Dependencies

- **Integration spec**: specs/002-moai-adk-integration/spec.md defines original requirements (FR-HOOKS-001~005, FR-SKILLS-004~005, FR-DOCS-002, FR-AGENTS-001)
- **MoAI-ADK reference**: docs/references/moai-adk/ provides proven Skill patterns and agent collaboration examples
- **Constitution**: .specify/memory/constitution.md defines all quality constraints (file size, complexity, TDD, TRUST principles)

## Out of Scope

- **Cross-session persistence of unlock state**: @IMMUTABLE unlocks deliberately do NOT persist across sessions (security by design - re-apply protection on each session start)
- **Custom AST parsing for TAG detection**: Use ripgrep regex-based scanning (Constitution Section II: prefer existing tools over building custom parsers)
- **Real-time TAG integrity monitoring**: Integrity calculated on-demand (SessionStart, /ms.up-docs) not continuously (performance consideration)
- **Multi-user unlock coordination**: Single-user local development workflow assumed (no distributed locking or unlock conflict resolution)
- **Automated unlock approval**: All unlocks require manual justification (no auto-unlock based on file patterns or user roles)
- **Historical unlock audit search**: Audit log is append-only text file (no query interface or analytics dashboard)
- **Skills versioning system**: Skills use simple version metadata in YAML frontmatter (no semantic versioning enforcement or upgrade paths)
- **Agent delegation failure retry**: If sub-agent delegation fails, command continues with single-agent workflow (no automatic retry or fallback chain)
- **Partial document sync**: doc-updater syncs all applicable doc types (API + dev daily + README) - no selective type-only sync in this version
- **TAG chain auto-repair**: System reports broken chains but does NOT automatically generate missing @TEST or @CODE tags

## Risks & Mitigations

### Risk 1: @IMMUTABLE Protection Breaks Existing Workflows

**Probability**: Medium
**Impact**: High (blocks developer edits)

**Mitigation**:
- Comprehensive testing (FR-012: ≥12 test cases)
- Clear unlock documentation in README with examples
- Fail-open protection (FR-001: if scan fails, allow edit with warning)
- Git checkpoint before unlock (instant rollback via `git checkout checkpoint/...`)
- Session-scoped unlock (protection re-applies on new session, limiting blast radius)

### Risk 2: Hook Fail-Open Masks Critical Errors

**Probability**: Low
**Impact**: Medium (errors go unnoticed)

**Mitigation**:
- All errors printed to stderr with full stack traces
- Fail-open payload includes systemMessage with error summary
- SessionStart dashboard shows hook health status
- Audit log for all hook failures (timestamp, error type, stack trace)

### Risk 3: TAG Integrity Scan Performance Degrades in Large Repos

**Probability**: Low
**Impact**: Low (slower SessionStart)

**Mitigation**:
- ripgrep is extremely fast (10k files in <1 second typical)
- 5-second timeout prevents hanging (existing configuration)
- Scan runs only on SessionStart and `/ms.up-docs` (not on every tool use)
- Future optimization: cache results, incremental scanning

### Risk 4: Agent Delegation Complexity Confuses Users

**Probability**: Medium
**Impact**: Medium (unclear workflows)

**Mitigation**:
- Clear separation: agents recommend (passive), commands execute (active)
- Documentation with delegation examples in agent prompt templates
- Integration tests demonstrating full delegation chains
- Graceful degradation: if Task tool unavailable, single-agent workflow continues

### Risk 5: Test Coverage Insufficient for Edge Cases

**Probability**: Low
**Impact**: Medium (undetected bugs)

**Mitigation**:
- FR-011: minimum 15 test cases for UserPromptSubmit (covers Constitution injection, caching, fail-open, edge cases)
- FR-012: minimum 12 test cases for @IMMUTABLE (covers scan, block, unlock, session tracking, Git errors)
- quality-gate agent validation before commit (enforces ≥85% coverage)
- Manual edge case review documented in this spec

### Risk 6: Skills Content Inconsistency with MoAI-ADK Reference

**Probability**: Low
**Impact**: Low (suboptimal guidance)

**Mitigation**:
- Base Skills directly on MoAI-ADK proven patterns (`docs/references/moai-adk/skills/moai-essentials-debug.md`, `moai-essentials-review.md`)
- Follow existing 7-section template used by 9 current Skills (consistency)
- Constitution references in Best Practices section (alignment with project standards)
- User review and approval before merging

## Related Documents

- **Original Issue Report**: modify.md (12 critical issues discovered during verification)
- **Integration Specification**: specs/002-moai-adk-integration/spec.md (defines FR-HOOKS-001~005, FR-SKILLS-004~005, FR-DOCS-002, FR-AGENTS-001)
- **Constitution**: .specify/memory/constitution.md (Section I TDD, Section II Simplicity-First, Section V TRUST 5)
- **MoAI-ADK Reference**: docs/references/moai-adk/ (Skills patterns, agent collaboration examples)
- **Implementation Plan**: To be created via `/ms.plan` after this spec approved
- **Quality Validation**: To be performed via `/fin` quality-gate before merge

---

## 📜 Constitution

This specification follows the project [Constitution](../../.specify/memory/constitution.md).

**Key Sections Applied:**
- **Section I**: Test-First Development (TDD) - All features require ≥85% test coverage, tests written before implementation
- **Section II**: Simplicity-First Architecture - Files ≤500 SLOC, functions ≤100 LOC, complexity ≤10, prefer existing tools (ripgrep) over custom parsers
- **Section IV**: Requirements Clarity (EARS Standards) - All requirements use EARS patterns (WHEN/SHALL/WHILE/WHERE/IF) for unambiguous specification
- **Section V**: TRUST 5 Quality Principles - Test-First (≥85% coverage), Readable (size/complexity limits), Unified (SPEC-driven), Secured (input validation, audit logging), Trackable (@TAG system)
- **Section X**: Agentic Behavior Standards - Fail-open principle (hook errors don't block workflows), truth verification (all operations logged), anti-deception (show raw errors)

**TAG System**: Traceability @SPEC → @TEST → @CODE → @DOC

_Auto-added by `/ms.specify`_

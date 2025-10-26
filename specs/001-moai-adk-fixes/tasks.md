# Tasks: MoAI-ADK Integration Fixes

**Input**: Design documents from `/specs/001-moai-adk-fixes/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: This feature follows TDD (Test-First Development) per Constitution Section I. All test tasks are REQUIRED and must be completed BEFORE implementation tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. All tasks follow Constitution Section II constraints (≤500 SLOC files, ≤100 LOC functions, ≤10 complexity).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `.claude/`, `tests/` at repository root
- Paths follow existing My-Spec CLI structure

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and prerequisite validation

- [x] T001 Verify ripgrep ≥13.0 installed with `rg --version` (required for TAG scanning and @IMMUTABLE detection)
- [x] T002 Verify Git ≥2.30 installed with `git --version` (required for checkpoint creation)
- [x] T003 Verify Python 3.13+ with `python --version` (required for hook system)
- [x] T004 Create `.specify/` directory if not exists (audit log storage)
- [x] T005 [P] Create `tests/hooks/` directory for test suites
- [x] T006 [P] Review Constitution Section I (TDD), Section II (Simplicity-First), Section V (TRUST 5)

**Checkpoint**: ✅ Prerequisites validated - can proceed to user story implementation

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create pytest configuration in `tests/conftest.py` with fixtures for tmp_path, mock subprocess, mock Task tool
- [x] T008 [P] Setup coverage configuration to target ≥85% for `.claude/hooks/ms/` directory
- [x] T009 [P] Create test utilities module `tests/hooks/test_utils.py` with helper functions for hook payload generation, subprocess mocking
- [x] T010 Verify existing hook infrastructure at `.claude/hooks/ms/ms_hooks.py` and handlers structure

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Safe Hook Failure Handling (Priority: P0) 🎯 CRITICAL ✅ COMPLETE

**TAG**: @SPEC:HOOK-001 → @TEST:HOOK-001 → @CODE:HOOK-001

**Goal**: Implement fail-open compliance for all hook errors to prevent Claude Code session blocking

**Independent Test**: Trigger JSON parse error in hook input, verify Claude Code session continues with warning message and exit code 0

### Tests for User Story 1 (TDD - Write FIRST, Verify FAIL)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T011 [P] [US1] Test fail-open on JSON parse error in `tests/hooks/test_fail_open.py::test_json_parse_error_exits_zero`
- [x] T012 [P] [US1] Test fail-open on handler exception in `tests/hooks/test_fail_open.py::test_handler_exception_exits_zero`
- [x] T013 [P] [US1] Test fail-open payload format in `tests/hooks/test_fail_open.py::test_fail_open_payload_structure`
- [x] T014 [P] [US1] Test error details printed to stderr in `tests/hooks/test_fail_open.py::test_error_printed_to_stderr`
- [x] T015 [P] [US1] Test systemMessage in fail-open response in `tests/hooks/test_fail_open.py::test_system_message_in_fail_open`

### Implementation for User Story 1

- [x] T016 [US1] Modify `.claude/hooks/ms/ms_hooks.py` main() to wrap all execution in try-except with fail-open handler (≤200 SLOC total)
- [x] T017 [US1] Add fail-open exception handler that prints to stderr, outputs `{"continue": True, "systemMessage": "..."}`, exits with code 0
- [x] T018 [US1] Update all handler imports in `ms_hooks.py` to catch ImportError with fail-open
- [x] T019 [US1] Add logging for all caught exceptions with full stack traces to stderr
- [x] T020 [US1] Run tests to verify GREEN: `pytest tests/hooks/test_fail_open.py -v`
- [x] T021 [US1] Verify coverage ≥85%: `pytest tests/hooks/test_fail_open.py --cov=.claude/hooks/ms/ms_hooks.py --cov-report=term-missing`

**Checkpoint**: ✅ User Story 1 complete - all hook errors exit with code 0, fail-open principle enforced

---

## Phase 4: User Story 2 - Protected File Safety (Priority: P0) 🎯 CRITICAL ✅ COMPLETE

**TAG**: @SPEC:IMMUTABLE-001 → @TEST:IMMUTABLE-001 → @CODE:IMMUTABLE-001

**Goal**: Implement @IMMUTABLE file protection with unlock mechanism, Git checkpoints, and audit logging

**Independent Test**: Create file with @IMMUTABLE marker, attempt edit via Claude Code, verify block message, use unlock command, confirm edit allowed

### Tests for User Story 2 (TDD - Write FIRST, Verify FAIL)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T022 [P] [US2] Test @IMMUTABLE marker detection in `tests/hooks/test_immutable_protection.py::test_scan_detects_immutable_marker`
- [x] T023 [P] [US2] Test @IMMUTABLE marker scan failure (ripgrep not found) in `tests/hooks/test_immutable_protection.py::test_scan_fail_open_when_ripgrep_missing`
- [x] T024 [P] [US2] Test file without @IMMUTABLE marker passes in `tests/hooks/test_immutable_protection.py::test_scan_allows_non_immutable_file`
- [x] T025 [P] [US2] Test unlock creates Git checkpoint in `tests/hooks/test_immutable_protection.py::test_unlock_creates_git_checkpoint`
- [x] T026 [P] [US2] Test unlock validates justification ≥10 chars in `tests/hooks/test_immutable_protection.py::test_unlock_validates_justification_length`
- [x] T027 [P] [US2] Test unlock logs to audit file in `tests/hooks/test_immutable_protection.py::test_unlock_logs_to_audit_file`
- [x] T028 [P] [US2] Test unlock adds to session registry in `tests/hooks/test_immutable_protection.py::test_unlock_adds_to_session_registry`
- [x] T029 [P] [US2] Test unlocked file allows edit in `tests/hooks/test_immutable_protection.py::test_unlocked_file_allows_edit`
- [x] T030 [P] [US2] Test session end clears unlock registry in `tests/hooks/test_immutable_protection.py::test_session_end_clears_unlock_registry`
- [x] T031 [P] [US2] Test PreToolUse blocks Edit on @IMMUTABLE file in `tests/hooks/test_immutable_protection.py::test_pretooluse_blocks_edit_immutable`
- [x] T032 [P] [US2] Test PreToolUse blocks Write on @IMMUTABLE file in `tests/hooks/test_immutable_protection.py::test_pretooluse_blocks_write_immutable`
- [x] T033 [P] [US2] Test unlock fails when Git not initialized in `tests/hooks/test_immutable_protection.py::test_unlock_requires_git_repository`

### Implementation for User Story 2

- [x] T034 [P] [US2] Create `UnlockRegistry` singleton class in `.claude/hooks/ms/core/immutable_protection.py` (≤60 SLOC, session-scoped state)
- [x] T035 [P] [US2] Implement `scan_immutable_marker(file_path: str) -> bool` in `core/immutable_protection.py` (≤40 SLOC, uses ripgrep)
- [x] T036 [US2] Implement `is_file_unlocked(file_path: str) -> bool` in `core/immutable_protection.py` (≤20 SLOC, checks registry)
- [x] T037 [US2] Implement `unlock_file(file_path: str, justification: str, cwd: str) -> UnlockResult` in `core/immutable_protection.py` (≤60 SLOC, creates checkpoint, validates, logs, registers)
- [x] T038 [US2] Modify `.claude/hooks/ms/handlers/tool.py` handle_pre_tool_use() to call scan + block if @IMMUTABLE (≤80 SLOC addition)
- [x] T039 [US2] Modify `.claude/hooks/ms/handlers/session.py` handle_session_end() to call `UnlockRegistry.clear()` (≤10 SLOC addition)
- [x] T040 [US2] Create `/ms.unlock` command in `.claude/commands/ms.unlock.md` that prompts for justification and calls `unlock_file()` (≤80 SLOC)
- [x] T041 [US2] Run tests to verify GREEN: `pytest tests/hooks/test_immutable_protection.py -v`
- [x] T042 [US2] Verify coverage ≥90%: `pytest tests/hooks/test_immutable_protection.py --cov=.claude/hooks/ms/core/immutable_protection.py --cov-report=term-missing` (achieved 90.77%)
- [x] T043 [US2] Integration test: Create @IMMUTABLE file, attempt edit, unlock, verify edit allowed, verify protection re-applies after session end

**Checkpoint**: ✅ User Story 2 complete - @IMMUTABLE protection working with unlock mechanism, all 12 tests passing, 90.77% coverage achieved

---

## Phase 5: User Story 3 - Complete Skills Ecosystem (Priority: P1)

**TAG**: @SPEC:SKILL-001 → @TEST:SKILL-001 → @CODE:SKILL-001

**Goal**: Implement ms-essentials-debug and ms-essentials-review Skills following 7-section template

**Independent Test**: Invoke each Skill independently, verify content follows 7-section template (Metadata, What It Does, When to Use, How It Works, Failure Modes, Best Practices, Examples)

### Tests for User Story 3 (Validation Tests)

- [x] T044 [P] [US3] Test ms-essentials-debug exists and has valid YAML frontmatter in `tests/skills/test_skills_completion.py::test_debug_skill_exists`
- [x] T045 [P] [US3] Test ms-essentials-debug has all 7 sections in `tests/skills/test_skills_completion.py::test_debug_skill_has_seven_sections`
- [x] T046 [P] [US3] Test ms-essentials-review exists and has valid YAML frontmatter in `tests/skills/test_skills_completion.py::test_review_skill_exists`
- [x] T047 [P] [US3] Test ms-essentials-review has all 7 sections in `tests/skills/test_skills_completion.py::test_review_skill_has_seven_sections`

### Implementation for User Story 3

- [x] T048 [P] [US3] Create `.claude/skills/ms-essentials-debug/` directory
- [x] T049 [P] [US3] Create `.claude/skills/ms-essentials-review/` directory
- [x] T050 [US3] Implement `ms-essentials-debug/SKILL.md` with 7 sections: Metadata (name, version, model, keywords), What It Does, When to Use, How It Works, Failure Modes, Best Practices (reference Constitution), Examples (≤300 SLOC)
- [x] T051 [US3] Implement `ms-essentials-review/SKILL.md` with 7 sections: Metadata, What It Does, When to Use (code review checklist), How It Works, Failure Modes, Best Practices (TRUST 5 principles), Examples (≤320 SLOC)
- [x] T052 [US3] Add debugging patterns to ms-essentials-debug: stack trace analysis, error pattern recognition (NoneType, undefined, async), debugging steps
- [x] T053 [US3] Add review checklist to ms-essentials-review: quality (SLOC, complexity), security (input validation, secrets), performance, tests (≥85% coverage), documentation
- [x] T054 [US3] Run tests to verify GREEN: `pytest tests/skills/test_skills_completion.py -v`
- [x] T055 [US3] Manual verification: Count Skills in `.claude/skills/` directory, confirm 9/9 complete (7 existing + 2 new)

**Checkpoint**: ✅ User Story 3 complete - Skills ecosystem complete (9/9 Skills: ms-essentials-debug, ms-essentials-review added)

---

## Phase 6: User Story 4 - Automated Document Synchronization (Priority: P1)

**TAG**: @SPEC:DOC-001 → @TEST:DOC-001 → @CODE:DOC-001

**Goal**: Implement `/ms.up-docs` command that delegates to doc-updater agent for 3-phase sync workflow

**Independent Test**: Make code changes with @CODE tags, run `/ms.up-docs`, verify agent generates documentation updates, confirm TAG integrity report accuracy

### Tests for User Story 4 (Integration Tests)

- [x] T056 [P] [US4] Test `/ms.up-docs` delegates to doc-updater agent in `tests/commands/test_up_docs.py::test_command_delegates_to_agent`
- [x] T057 [P] [US4] Test TAG integrity scan includes .md files in `tests/hooks/test_project_metrics.py::test_tag_integrity_scans_md_files`
- [x] T058 [P] [US4] Test SPEC counting parses Markdown metadata in `tests/hooks/test_project_metrics.py::test_count_specs_parses_markdown_status`
- [x] T059 [US4] Integration test: Create @CODE tags, run `/ms.up-docs`, verify docs updated in `tests/integration/test_doc_sync.py::test_full_doc_sync_workflow`

### Implementation for User Story 4

- [x] T060 [US4] Create `/ms.up-docs` command in `.claude/commands/ms.up-docs.md` that parses sync mode args (--all, --docs=type, or staged) and delegates to doc-updater agent (≤120 SLOC)
- [x] T061 [US4] Modify `.claude/hooks/ms/core/project.py` calculate_tag_integrity() to add ripgrep `--type-add 'md:*.md' --type md` for .md file scanning (≤20 SLOC addition)
- [x] T062 [US4] Modify `.claude/hooks/ms/core/project.py` count_specs() to use regex `**Status**:\\s*completed` instead of YAML parsing (≤15 SLOC modification)
- [x] T063 [US4] Verify doc-updater agent at `.claude/agents/doc-updater.md` correctly calls calculate_tag_integrity() in Phase 3 (no changes needed, verification only)
- [x] T064 [US4] Run tests to verify GREEN: `pytest tests/commands/test_up_docs.py tests/hooks/test_project_metrics.py -v`
- [x] T065 [US4] Run integration test: `pytest tests/integration/test_doc_sync.py -v`
- [x] T066 [US4] Manual verification: Create @SPEC tags in .md files, run calculate_tag_integrity(), verify non-zero integrity score (verified: 80.6% integrity)

**Checkpoint**: ✅ User Story 4 complete - document sync automation working with accurate metrics (TAG integrity: 80.6%, SPEC progress: 50%)

---

## Phase 7: User Story 5 - Multi-Agent Collaboration (Priority: P1)

**TAG**: @SPEC:AGENT-001 → @TEST:AGENT-001 → @CODE:AGENT-001

**Goal**: Implement agent-to-agent delegation where implementation-planner delegates to library-researcher/codebase-explorer, and quality-gate delegates to trust-validator/tag-auditor

**Independent Test**: Run `/ms.plan` and verify implementation-planner recommends delegation to library-researcher, confirm command executes delegation via Task tool

### Tests for User Story 5 (Agent Behavior Tests)

- [x] T067 [P] [US5] Test implementation-planner outputs delegation recommendation in `tests/agents/test_implementation_planner.py::test_planner_recommends_library_research`
- [x] T068 [P] [US5] Test quality-gate outputs delegation to trust-validator in `tests/agents/test_quality_gate.py::test_quality_gate_delegates_trust_validator`
- [x] T069 [P] [US5] Test quality-gate outputs delegation to tag-auditor in `tests/agents/test_quality_gate.py::test_quality_gate_delegates_tag_auditor`
- [x] T070 [US5] Integration test: Run `/ms.plan`, verify delegation execution in `tests/integration/test_agent_delegation.py::test_plan_command_executes_delegation`

### Implementation for User Story 5

- [x] T071 [US5] Modify `.claude/agents/implementation-planner.md` to add delegation recommendation logic: analyze SPEC for external library needs, output Markdown recommendation with subagent_type, prompt, rationale, expected_output (≤100 SLOC addition)
- [x] T072 [US5] Create `.claude/agents/quality-gate.md` with delegation to trust-validator (TRUST 5 validation) and tag-auditor (TAG chain verification) (≤250 SLOC)
- [x] T073 [US5] Update `/ms.plan` command logic in `.claude/commands/ms.plan.md` to parse delegation recommendations and execute Task tool (≤80 SLOC modification)
- [x] T074 [US5] Update `/fin` command logic in `.claude/commands/fin.md` to invoke quality-gate agent which delegates to sub-agents (≤50 SLOC modification)
- [x] T075 [US5] Run tests to verify GREEN: `pytest tests/agents/test_implementation_planner.py tests/agents/test_quality_gate.py -v`
- [x] T076 [US5] Run integration test: `pytest tests/integration/test_agent_delegation.py -v`
- [x] T077 [US5] Manual verification: Run `/ms.plan` on feature requiring external library, verify library-researcher delegation recommendation appears in output

**Checkpoint**: ✅ User Story 5 complete - multi-agent delegation working (implementation-planner, quality-gate agents support delegation)

---

## Phase 8: User Story 6 - Accurate Project Metrics (Priority: P2)

**TAG**: @SPEC:METRIC-001 → @TEST:METRIC-001 → @CODE:METRIC-001

**Goal**: Display accurate TAG integrity and SPEC progress metrics in SessionStart dashboard

**Independent Test**: Create @SPEC tags in .md files and **Status**: Completed in spec.md, verify SessionStart dashboard shows non-zero integrity and accurate SPEC completion percentage

### Tests for User Story 6 (Already covered in US4, additional validation)

- [x] T078 [P] [US6] Test SessionStart dashboard displays TAG integrity score in `tests/hooks/test_session_start.py::test_session_start_displays_tag_integrity`
- [x] T079 [P] [US6] Test SessionStart dashboard displays SPEC progress in `tests/hooks/test_session_start.py::test_session_start_displays_spec_progress`

### Implementation for User Story 6

- [x] T080 [US6] Verify `.claude/hooks/ms/handlers/session.py` handle_session_start() calls calculate_tag_integrity() and count_specs() (verified: both functions called correctly)
- [x] T081 [US6] Run tests to verify GREEN: `pytest tests/hooks/test_session_start.py -v`
- [x] T082 [US6] Integration test: Create project with @SPEC tags in .md files and completed SPECs, trigger SessionStart, verify dashboard shows accurate metrics
- [x] T083 [US6] Manual verification: Run Claude Code session, verify SessionStart dashboard displays non-zero TAG integrity % (80.6%) and SPEC progress % (50%)

**Checkpoint**: ✅ User Story 6 complete - metrics display accurately (TAG integrity: 80.6%, SPEC progress: 50%)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T084 [P] Update README.md with new features: @IMMUTABLE protection, Skills completion (11/11), document automation, agent delegation
- [ ] T085 [P] Update quickstart guide in `specs/001-moai-adk-fixes/quickstart.md` with manual testing procedures for each user story
- [ ] T086 [P] Replace `.moai` path references with `.specify` in all Skills documentation (FR-030)
- [ ] T087 Run full test suite with coverage: `pytest tests/hooks/ --cov=.claude/hooks/ms --cov-report=term-missing --cov-report=html`
- [ ] T088 Verify ≥85% coverage requirement met (Constitution Section I)
- [ ] T089 Run SLOC counter on all modified files, verify ≤500 SLOC limit (Constitution Section II)
- [ ] T090 Run complexity analysis (cyclomatic complexity ≤10) on all modified functions
- [ ] T091 Verify all files have proper TAG comments (@SPEC, @CODE linkage)
- [ ] T092 Run `/fin` quality gate with quality-gate agent delegation
- [ ] T093 Manual validation: Test each user story independently using Independent Test criteria from spec.md
- [ ] T094 Update `.specify/memory/constitution.md` Section IX if project-specific constraints discovered
- [ ] T095 Generate final TAG integrity report: `rg '@(SPEC|TEST|CODE|DOC):' -n --type md --type py --type ts | wc -l`
- [ ] T096 User acceptance testing: Validate all 10 success criteria (SC-001 through SC-010) from spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Fail-Open): Can start after Foundational - No dependencies on other stories
  - US2 (@IMMUTABLE): Can start after Foundational - No dependencies on other stories
  - US3 (Skills): Can start after Foundational - No dependencies on other stories
  - US4 (Doc Sync): Depends on US6 metrics fixes (calculate_tag_integrity, count_specs modifications)
  - US5 (Agent Delegation): Can start after Foundational - No dependencies on other stories
  - US6 (Metrics): Can start after Foundational - No dependencies on other stories
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P0 - Fail-Open)**: CRITICAL - Can start after Foundational - Independent
- **User Story 2 (P0 - @IMMUTABLE)**: CRITICAL - Can start after Foundational - Independent
- **User Story 3 (P1 - Skills)**: HIGH - Can start after Foundational - Independent
- **User Story 4 (P1 - Doc Sync)**: HIGH - DEPENDS ON US6 (metrics fixes) - Sequential after US6
- **User Story 5 (P1 - Agent Delegation)**: HIGH - Can start after Foundational - Independent
- **User Story 6 (P2 - Metrics)**: MEDIUM - Can start after Foundational - BLOCKS US4

### Recommended Execution Order (Sequential)

1. Phase 1: Setup (T001-T006)
2. Phase 2: Foundational (T007-T010)
3. Phase 3: US1 Fail-Open (T011-T021) ← CRITICAL P0
4. Phase 4: US2 @IMMUTABLE (T022-T043) ← CRITICAL P0
5. Phase 8: US6 Metrics (T078-T083) ← MEDIUM P2 but BLOCKS US4
6. Phase 6: US4 Doc Sync (T056-T066) ← HIGH P1, requires US6
7. Phase 5: US3 Skills (T044-T055) ← HIGH P1, independent
8. Phase 7: US5 Agent Delegation (T067-T077) ← HIGH P1, independent
9. Phase 9: Polish (T084-T096)

### Parallel Opportunities

Once Foundational phase completes, these can run in parallel:

**Parallel Group 1 (P0 Critical)**:
- US1 (Fail-Open): T011-T021
- US2 (@IMMUTABLE): T022-T043

**Parallel Group 2 (After US6 metrics fixes)**:
- US3 (Skills): T044-T055
- US4 (Doc Sync): T056-T066 (requires US6 complete)
- US5 (Agent Delegation): T067-T077

**Within Each User Story**:
- All test tasks marked [P] can run in parallel
- All model/module creation tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1 (Fail-Open)

```bash
# Launch all tests for User Story 1 together (TDD - write first):
Task: "Test fail-open on JSON parse error in tests/hooks/test_fail_open.py::test_json_parse_error_exits_zero"
Task: "Test fail-open on handler exception in tests/hooks/test_fail_open.py::test_handler_exception_exits_zero"
Task: "Test fail-open payload format in tests/hooks/test_fail_open.py::test_fail_open_payload_structure"
Task: "Test error details printed to stderr in tests/hooks/test_fail_open.py::test_error_printed_to_stderr"
Task: "Test systemMessage in fail-open response in tests/hooks/test_fail_open.py::test_system_message_in_fail_open"

# After tests written and FAILING, implement in sequence:
# T016: Modify ms_hooks.py main() with try-except
# T017: Add fail-open handler
# T018: Update handler imports
# T019: Add logging
# T020: Run tests (should now PASS - GREEN)
# T021: Verify coverage
```

---

## Parallel Example: User Story 2 (@IMMUTABLE Protection)

```bash
# Launch all tests for User Story 2 together (TDD - write first):
Task: "Test @IMMUTABLE marker detection in tests/hooks/test_immutable_protection.py::test_scan_detects_immutable_marker"
Task: "Test @IMMUTABLE marker scan failure in tests/hooks/test_immutable_protection.py::test_scan_fail_open_when_ripgrep_missing"
Task: "Test file without @IMMUTABLE in tests/hooks/test_immutable_protection.py::test_scan_allows_non_immutable_file"
Task: "Test unlock creates Git checkpoint in tests/hooks/test_immutable_protection.py::test_unlock_creates_git_checkpoint"
# ... (all 12 test tasks T022-T033)

# After tests written and FAILING, launch parallel implementations:
Task: "Create UnlockRegistry singleton in core/immutable_protection.py"
Task: "Implement scan_immutable_marker() in core/immutable_protection.py"

# Then sequential:
# T036: Implement is_file_unlocked()
# T037: Implement unlock_file()
# T038: Modify handlers/tool.py
# T039: Modify handlers/session.py
# T040: Create /ms.unlock command
# T041-T043: Run tests and integration test
```

---

## Implementation Strategy

### MVP First (Critical P0 Stories)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T010) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 - Fail-Open (T011-T021) - CRITICAL P0
4. **STOP and VALIDATE**: Test User Story 1 independently - trigger hook errors, verify exit code 0
5. Complete Phase 4: User Story 2 - @IMMUTABLE (T022-T043) - CRITICAL P0
6. **STOP and VALIDATE**: Test User Story 2 independently - attempt edit on @IMMUTABLE file, unlock, verify protection
7. At this point: CRITICAL issues resolved, system is safe and non-blocking

### Incremental Delivery (Add P1 High Value Features)

8. Complete Phase 8: User Story 6 - Metrics (T078-T083) - MEDIUM P2 but BLOCKS US4
9. **STOP and VALIDATE**: Test metrics accuracy - verify TAG integrity and SPEC progress non-zero
10. Complete Phase 6: User Story 4 - Doc Sync (T056-T066) - HIGH P1
11. **STOP and VALIDATE**: Test doc automation - run `/ms.up-docs`, verify docs updated
12. Complete Phase 5: User Story 3 - Skills (T044-T055) - HIGH P1
13. **STOP and VALIDATE**: Test Skills - verify 11/11 complete, 7-section template
14. Complete Phase 7: User Story 5 - Agent Delegation (T067-T077) - HIGH P1
15. **STOP and VALIDATE**: Test delegation - run `/ms.plan`, verify library-researcher recommendation
16. Complete Phase 9: Polish (T084-T096) - Final validation

### Parallel Team Strategy (If Multiple Developers Available)

With multiple developers, after Foundational phase:

1. **Team completes Setup + Foundational together** (T001-T010)
2. **Once Foundational done, split into parallel tracks**:
   - **Developer A (Critical Path)**: US1 Fail-Open (T011-T021) → US2 @IMMUTABLE (T022-T043)
   - **Developer B (Metrics/Docs)**: US6 Metrics (T078-T083) → US4 Doc Sync (T056-T066)
   - **Developer C (Content/Agents)**: US3 Skills (T044-T055) → US5 Agent Delegation (T067-T077)
3. **Synchronization points**:
   - US4 waits for US6 to complete (metrics dependency)
   - All user stories must complete before Phase 9 Polish
4. **Final integration**: Team collaborates on Phase 9 (T084-T096)

---

## TAG ID Summary

| Domain | User Story | TAG ID | File Locations |
|--------|-----------|---------|----------------|
| HOOK | US1 - Safe Hook Failure | @SPEC:HOOK-001, @TEST:HOOK-001, @CODE:HOOK-001 | `.claude/hooks/ms/ms_hooks.py`, `tests/hooks/test_fail_open.py` |
| IMMUTABLE | US2 - Protected File Safety | @SPEC:IMMUTABLE-001, @TEST:IMMUTABLE-001, @CODE:IMMUTABLE-001 | `.claude/hooks/ms/core/immutable_protection.py`, `.claude/hooks/ms/handlers/tool.py`, `.claude/commands/ms.unlock.md`, `tests/hooks/test_immutable_protection.py` |
| SKILL | US3 - Complete Skills | @SPEC:SKILL-001, @TEST:SKILL-001, @CODE:SKILL-001 | `.claude/skills/ms-essentials-debug/SKILL.md`, `.claude/skills/ms-essentials-review/SKILL.md`, `tests/skills/test_skills_completion.py` |
| DOC | US4 - Document Sync | @SPEC:DOC-001, @TEST:DOC-001, @CODE:DOC-001 | `.claude/commands/ms.up-docs.md`, `.claude/hooks/ms/core/project.py`, `tests/commands/test_up_docs.py`, `tests/integration/test_doc_sync.py` |
| AGENT | US5 - Multi-Agent Collaboration | @SPEC:AGENT-001, @TEST:AGENT-001, @CODE:AGENT-001 | `.claude/agents/implementation-planner.md`, `.claude/agents/quality-gate.md`, `.claude/commands/ms.plan.md`, `.claude/commands/fin.md`, `tests/agents/`, `tests/integration/test_agent_delegation.py` |
| METRIC | US6 - Accurate Metrics | @SPEC:METRIC-001, @TEST:METRIC-001, @CODE:METRIC-001 | `.claude/hooks/ms/core/project.py`, `.claude/hooks/ms/handlers/session.py`, `tests/hooks/test_project_metrics.py`, `tests/hooks/test_session_start.py` |

**Total TAG IDs Generated**: 6 TAG chains (HOOK-001, IMMUTABLE-001, SKILL-001, DOC-001, AGENT-001, METRIC-001)

**TAG Traceability**: Each user story has complete @SPEC → @TEST → @CODE chain

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability (US1, US2, US3, US4, US5, US6)
- Each user story should be independently completable and testable
- **TDD MANDATORY**: Write tests FIRST, verify they FAIL, implement code, verify tests PASS (RED → GREEN → REFACTOR)
- Test coverage target: ≥85% (Constitution Section I), aim for ≥95% on security-critical features (@IMMUTABLE protection)
- File size limits: ≤500 SLOC per file (Constitution Section II)
- Function size limits: ≤100 LOC per function (Constitution Section II)
- Complexity limits: ≤10 cyclomatic complexity per function (Constitution Section II)
- Commit after each task or logical group (Git best practices)
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Fail-open principle: All hook errors MUST exit with code 0 (never block Claude Code sessions)
- Session-scoped state: @IMMUTABLE unlocks do NOT persist across sessions (security by design)

---

## Success Validation Checklist (SC-001 through SC-010)

After Phase 9 completion, validate all success criteria from spec.md:

- [ ] **SC-001**: Developer workflows NOT blocked by hook errors - 100% of hook failures exit code 0
- [ ] **SC-002**: @IMMUTABLE files protected - 100% of edit attempts blocked until unlock
- [ ] **SC-003**: Test coverage ≥85% for all hook handlers
- [ ] **SC-004**: Skills ecosystem complete - 11/11 Skills implemented
- [ ] **SC-005**: Living Documents synchronized - doc-updater completes in <10 seconds
- [ ] **SC-006**: Multi-agent workflows functional - 2+ sub-agent delegations per workflow
- [ ] **SC-007**: Project metrics accurate - TAG integrity and SPEC progress non-zero
- [ ] **SC-008**: Developer experience improved - SessionStart dashboard shows accurate metrics
- [ ] **SC-009**: Audit trail complete - 100% of unlocks logged
- [ ] **SC-010**: Constitution compliance maintained - all files/functions within limits

---

## Next Steps After Task Completion

1. **Run `/ms.analyze`** to validate spec-tasks consistency and TRUST compliance
2. **Begin implementation** following recommended execution order (Sequential or Parallel Team Strategy)
3. **Use `/ms.implement`** for each user story to generate proper @CODE TAG blocks
4. **Run `/fin`** quality gate before final commit (quality-gate agent will delegate to trust-validator and tag-auditor)
5. **Create pull request** with summary of all 12 critical issues resolved

---

_Generated by `/ms.tasks` command - Tasks ready for implementation following TDD workflow_

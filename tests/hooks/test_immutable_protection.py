#!/usr/bin/env python3
"""
@TEST:IMMUTABLE-001
@SPEC: specs/001-moai-adk-fixes/spec.md
@CHAIN: @SPEC:IMMUTABLE-001 → @TEST:IMMUTABLE-001 → @CODE:IMMUTABLE-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

Test suite for @IMMUTABLE file protection

Tests FR-005 through FR-010 requirements:
- @IMMUTABLE marker detection via ripgrep
- Edit/Write tool blocking
- /ms.unlock command with Git checkpoint
- Justification validation (≥10 chars)
- Session-scoped unlock registry
- Audit logging to .specify/immutable_changes.log
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestImmutableMarkerDetection:
    """Test @IMMUTABLE marker detection (FR-005)"""

    def test_scan_detects_immutable_marker(self, tmp_path_factory):
        """WHEN file contains @IMMUTABLE marker, scan SHALL return True

        Covers: FR-005
        """
        # Setup: Create file with @IMMUTABLE marker
        test_file = tmp_path_factory / "protected.py"
        test_file.write_text("""
# @IMMUTABLE: Constitution file - protected from accidental modification
def get_config():
    return {"protected": True}
""")

        # Import function under test
        from core.immutable_protection import scan_immutable_marker

        # Execute: Scan file for @IMMUTABLE marker
        has_marker = scan_immutable_marker(str(test_file))

        # Assert: Should detect marker
        assert has_marker is True

    def test_scan_fail_open_when_ripgrep_missing(self, tmp_path_factory):
        """WHEN ripgrep not found, scan SHALL return False (fail-open)

        Covers: FR-005 + fail-open principle
        """
        from core.immutable_protection import scan_immutable_marker

        test_file = tmp_path_factory / "test.py"
        test_file.write_text("# @IMMUTABLE\ncode")

        # Mock subprocess to raise FileNotFoundError (ripgrep not found)
        with patch("subprocess.run", side_effect=FileNotFoundError):
            has_marker = scan_immutable_marker(str(test_file))

            # Fail-open: Return False when ripgrep unavailable
            assert has_marker is False

    def test_scan_allows_non_immutable_file(self, tmp_path_factory):
        """WHEN file has no @IMMUTABLE marker, scan SHALL return False

        Covers: FR-005
        """
        from core.immutable_protection import scan_immutable_marker

        test_file = tmp_path_factory / "normal.py"
        test_file.write_text("""
def normal_function():
    return "editable"
""")

        has_marker = scan_immutable_marker(str(test_file))

        assert has_marker is False


class TestUnlockMechanism:
    """Test unlock mechanism (FR-007, FR-008, FR-009)"""

    def test_unlock_creates_git_checkpoint(self, tmp_git_repo):
        """WHEN unlock succeeds, system SHALL create Git checkpoint

        Covers: FR-007
        """
        from core.immutable_protection import unlock_file

        test_file = tmp_git_repo / "protected.py"
        test_file.write_text("# @IMMUTABLE\ncode")

        # Execute unlock
        result = unlock_file(
            file_path=str(test_file),
            justification="Emergency bug fix for production issue",
            cwd=str(tmp_git_repo),
        )

        # Assert: Git checkpoint created
        assert result.success is True
        assert result.checkpoint_ref is not None
        assert result.checkpoint_ref.startswith("immutable-unlock-")

    def test_unlock_validates_justification_length(self, tmp_path_factory):
        """WHEN justification <10 chars, unlock SHALL fail validation

        Covers: FR-007, FR-008 (validation requirement)
        """
        from core.immutable_protection import unlock_file

        test_file = tmp_path_factory / "protected.py"
        test_file.write_text("# @IMMUTABLE\ncode")

        # Execute with short justification (9 chars)
        result = unlock_file(
            file_path=str(test_file),
            justification="Too short",  # 9 chars
            cwd=str(tmp_path_factory),
        )

        # Assert: Validation failure
        assert result.success is False
        assert "at least 10 characters" in result.error_message.lower()

    def test_unlock_logs_to_audit_file(self, tmp_git_repo):
        """WHEN unlock succeeds, system SHALL log to audit file

        Covers: FR-009
        """
        from core.immutable_protection import unlock_file

        test_file = tmp_git_repo / "protected.py"
        test_file.write_text("# @IMMUTABLE\ncode")

        # Execute unlock
        result = unlock_file(
            file_path=str(test_file),
            justification="Emergency production fix - auth bypass vulnerability",
            cwd=str(tmp_git_repo),
        )

        # Assert: Audit log created
        audit_log = tmp_git_repo / ".specify" / "immutable_changes.log"
        assert audit_log.exists()

        # Verify log content
        log_content = audit_log.read_text()
        assert "protected.py" in log_content
        assert "Emergency production fix" in log_content
        assert result.checkpoint_ref in log_content

    def test_unlock_adds_to_session_registry(self, tmp_git_repo):
        """WHEN unlock succeeds, file SHALL be added to session unlock registry

        Covers: FR-008
        """
        from core.immutable_protection import UnlockRegistry, unlock_file

        test_file = tmp_git_repo / "protected.py"
        test_file.write_text("# @IMMUTABLE\ncode")

        # Execute unlock
        unlock_file(
            file_path=str(test_file),
            justification="Valid justification for testing",
            cwd=str(tmp_git_repo),
        )

        # Assert: File added to registry
        registry = UnlockRegistry.get_instance()
        assert registry.is_unlocked(str(test_file)) is True

    def test_unlocked_file_allows_edit(self, tmp_git_repo):
        """WHEN file is unlocked, Edit tool SHALL be allowed

        Covers: FR-008
        """
        from core.immutable_protection import UnlockRegistry, is_file_unlocked

        test_file = tmp_git_repo / "protected.py"
        test_file.write_text("# @IMMUTABLE\ncode")

        # Unlock file
        registry = UnlockRegistry.get_instance()
        registry.add(str(test_file), "Testing unlock")

        # Assert: File is unlocked
        assert is_file_unlocked(str(test_file)) is True

    def test_session_end_clears_unlock_registry(self, tmp_git_repo):
        """WHEN session ends, unlock registry SHALL be cleared

        Covers: FR-010 (session-scoped protection)
        """
        from core.immutable_protection import UnlockRegistry

        test_file = tmp_git_repo / "protected.py"

        # Add file to registry
        registry = UnlockRegistry.get_instance()
        registry.add(str(test_file), "Temporary unlock")

        # Verify file is unlocked
        assert registry.is_unlocked(str(test_file)) is True

        # Simulate session end
        registry.clear()

        # Assert: Registry cleared
        assert registry.is_unlocked(str(test_file)) is False


class TestPreToolUseIntegration:
    """Test PreToolUse hook integration (FR-006)"""

    def test_pretooluse_blocks_edit_immutable(self, tmp_git_repo):
        """WHEN Edit targets @IMMUTABLE file, PreToolUse SHALL block operation

        Covers: FR-006
        """
        from handlers.tool import handle_pre_tool_use

        # Create @IMMUTABLE file
        protected_file = tmp_git_repo / "constitution.md"
        protected_file.write_text("# @IMMUTABLE\n# Constitution")

        # Create PreToolUse payload for Edit operation
        payload = {
            "cwd": str(tmp_git_repo),
            "tool": "Edit",
            "arguments": {
                "file_path": str(protected_file),
                "old_string": "Constitution",
                "new_string": "Modified",
            },
        }

        # Execute PreToolUse hook
        result = handle_pre_tool_use(payload)

        # Assert: Operation blocked
        assert result.continue_execution is False
        assert "@IMMUTABLE" in result.system_message
        assert "/ms.unlock" in result.system_message

    def test_pretooluse_blocks_write_immutable(self, tmp_git_repo):
        """WHEN Write targets @IMMUTABLE file, PreToolUse SHALL block operation

        Covers: FR-006
        """
        from handlers.tool import handle_pre_tool_use

        # Create @IMMUTABLE file
        protected_file = tmp_git_repo / "config.json"
        protected_file.write_text('{"immutable": true}\n# @IMMUTABLE')

        # Create PreToolUse payload for Write operation
        payload = {
            "cwd": str(tmp_git_repo),
            "tool": "Write",
            "arguments": {
                "file_path": str(protected_file),
                "content": '{"modified": true}',
            },
        }

        # Execute PreToolUse hook
        result = handle_pre_tool_use(payload)

        # Assert: Operation blocked
        assert result.continue_execution is False
        assert "@IMMUTABLE" in result.system_message

    def test_unlock_requires_git_repository(self, tmp_path_factory):
        """WHEN unlock called outside Git repo, SHALL fail with error

        Covers: FR-007 (Git checkpoint requirement)
        """
        from core.immutable_protection import unlock_file

        non_git_dir = tmp_path_factory / "no-git"
        non_git_dir.mkdir()
        test_file = non_git_dir / "file.py"
        test_file.write_text("# @IMMUTABLE\ncode")

        # Execute unlock in non-Git directory
        result = unlock_file(
            file_path=str(test_file),
            justification="Valid justification text",
            cwd=str(non_git_dir),
        )

        # Assert: Fails due to missing Git repo
        assert result.success is False
        assert "git" in result.error_message.lower()

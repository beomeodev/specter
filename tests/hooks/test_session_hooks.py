#!/usr/bin/env python3
"""
@TEST:HOOKS-001
@SPEC: specs/002-moai-adk-integration/spec.md
@CODE: .claude/hooks/ms/handlers/session.py
@CHAIN: @SPEC:HOOKS-001 → @TEST:HOOKS-001 → @CODE:HOOKS-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

SessionStart Hook Tests

Tests for SessionStart hook following MoAI-ADK patterns but adapted for My-Spec workflow.
"""

import json
import subprocess
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestSessionStartHook:
    """SessionStart hook test suite"""

    def test_session_start_displays_project_status(self):
        """Test: SessionStart displays project status card

        Expected format:
        🚀 My-Spec Session Started
           Language: {language}
           Git Branch: {branch}
           Changes: {changes}
           SPEC Progress: {completed}/{total} ({percentage}%)
           TAG Integrity: {percentage}%
        """
        # This test will fail until we implement the handler
        from handlers.session import handle_session_start

        payload = {"cwd": ".", "phase": "compact"}
        result = handle_session_start(payload)

        assert result.system_message is not None
        assert "🚀 My-Spec Session Started" in result.system_message
        assert "Language:" in result.system_message
        assert "Git Branch:" in result.system_message
        assert "Changes:" in result.system_message
        assert "SPEC Progress:" in result.system_message
        assert "TAG Integrity:" in result.system_message

    def test_session_start_detects_language(self):
        """Test: SessionStart detects primary language"""
        from core.project import detect_language

        # This will fail until detect_language is implemented
        language = detect_language(".")

        # Should detect Python (pyproject.toml exists)
        assert language in ["python", "typescript", "javascript", "go", "rust"]

    def test_session_start_performance(self):
        """Test: SessionStart completes reasonably fast (<5 seconds)"""
        from handlers.session import handle_session_start

        payload = {"cwd": ".", "phase": "compact"}

        start = time.time()
        result = handle_session_start(payload)
        duration_ms = (time.time() - start) * 1000

        # Performance requirement: should be fast (we'll optimize to <100ms in REFACTOR phase)
        # For now, accept <5 seconds as GREEN phase baseline
        assert duration_ms < 5000, f"SessionStart took {duration_ms:.2f}ms (limit: 5000ms)"
        assert result.system_message is not None

    def test_session_start_clear_phase_minimal(self):
        """Test: Clear phase returns minimal output (prevents duplicate)"""
        from handlers.session import handle_session_start

        payload = {"cwd": ".", "phase": "clear"}
        result = handle_session_start(payload)

        # Clear phase should return minimal result
        assert result.continue_execution is True
        # Should NOT have system_message in clear phase
        assert result.system_message is None or result.system_message == ""

    @patch("handlers.session.get_git_info")
    def test_session_start_with_git_info(self, mock_git_info):
        """Test: SessionStart displays Git information"""
        mock_git_info.return_value = {
            "branch": "main",
            "commit": "abc1234567890",
            "changes": 5
        }

        from handlers.session import handle_session_start

        payload = {"cwd": ".", "phase": "compact"}
        result = handle_session_start(payload)

        assert "Git Branch: main" in result.system_message
        assert "Changes: 5" in result.system_message

    @patch("handlers.session.count_specs")
    def test_session_start_with_spec_progress(self, mock_count_specs):
        """Test: SessionStart displays SPEC progress"""
        mock_count_specs.return_value = {
            "completed": 2,
            "total": 5,
            "percentage": 40
        }

        from handlers.session import handle_session_start

        payload = {"cwd": ".", "phase": "compact"}
        result = handle_session_start(payload)

        assert "SPEC Progress: 2/5 (40%)" in result.system_message

    def test_session_start_fail_open_on_error(self):
        """Test: SessionStart fails open on error (doesn't block session)"""
        from handlers.session import handle_session_start

        # Invalid cwd should not crash
        payload = {"cwd": "/nonexistent/path", "phase": "compact"}

        # Should not raise exception (fail-open)
        result = handle_session_start(payload)
        assert result.continue_execution is True


class TestLanguageDetection:
    """Language detection tests"""

    def test_detect_python_project(self, tmp_path):
        """Test: Detect Python project (pyproject.toml)"""
        from core.project import detect_language

        # Create pyproject.toml
        (tmp_path / "pyproject.toml").touch()

        language = detect_language(str(tmp_path))
        assert language == "python"

    def test_detect_typescript_project(self, tmp_path):
        """Test: Detect TypeScript project (tsconfig.json)"""
        from core.project import detect_language

        # Create tsconfig.json
        (tmp_path / "tsconfig.json").touch()

        language = detect_language(str(tmp_path))
        assert language == "typescript"

    def test_detect_unknown_language(self, tmp_path):
        """Test: Return 'Unknown Language' for unrecognized projects"""
        from core.project import detect_language

        # Empty directory
        language = detect_language(str(tmp_path))
        assert language == "Unknown Language"

    def test_typescript_priority_over_javascript(self, tmp_path):
        """Test: TypeScript takes priority if both package.json and tsconfig.json exist"""
        from core.project import detect_language

        # Create both files
        (tmp_path / "package.json").touch()
        (tmp_path / "tsconfig.json").touch()

        language = detect_language(str(tmp_path))
        assert language == "typescript"


class TestGitInfo:
    """Git information extraction tests"""

    def test_get_git_info_in_repo(self):
        """Test: Get Git info in repository"""
        from core.project import get_git_info

        # Current directory is a git repo
        git_info = get_git_info(".")

        # Should have all required fields
        assert "branch" in git_info
        assert "commit" in git_info
        assert "changes" in git_info

        # Branch should be a non-empty string
        assert isinstance(git_info["branch"], str)
        assert len(git_info["branch"]) > 0

        # Commit should be a 40-character hex string
        assert isinstance(git_info["commit"], str)
        assert len(git_info["commit"]) == 40

        # Changes should be a non-negative integer
        assert isinstance(git_info["changes"], int)
        assert git_info["changes"] >= 0

    def test_get_git_info_non_repo(self, tmp_path):
        """Test: Return empty dict for non-Git directory"""
        from core.project import get_git_info

        # Non-git directory
        git_info = get_git_info(str(tmp_path))

        assert git_info == {}


class TestSpecCount:
    """SPEC counting tests"""

    def test_count_specs_my_spec_directory(self):
        """Test: Count specs in My-Spec directory structure (specs/*/spec.md)"""
        from core.project import count_specs

        # My-Spec uses specs/ not .moai/specs/
        specs = count_specs(".")

        assert "completed" in specs
        assert "total" in specs
        assert "percentage" in specs
        assert isinstance(specs["total"], int)
        assert isinstance(specs["completed"], int)
        assert isinstance(specs["percentage"], int)

    def test_count_specs_no_directory(self, tmp_path):
        """Test: Return zeros when specs/ doesn't exist"""
        from core.project import count_specs

        specs = count_specs(str(tmp_path))

        assert specs == {"completed": 0, "total": 0, "percentage": 0}


class TestTAGIntegrity:
    """TAG chain integrity calculation tests"""

    def test_calculate_tag_integrity(self):
        """Test: Calculate TAG chain integrity percentage"""
        from core.project import calculate_tag_integrity

        # This will fail until calculate_tag_integrity is implemented
        integrity = calculate_tag_integrity(".")

        assert isinstance(integrity, (int, float))
        assert 0 <= integrity <= 100


class TestHookResult:
    """HookResult class tests"""

    def test_hook_result_to_dict(self):
        """Test: HookResult.to_dict() produces Claude Code schema"""
        from core import HookResult

        result = HookResult(
            continue_execution=True,
            system_message="Test message"
        )

        output = result.to_dict()

        assert output["continue"] is True
        assert output["systemMessage"] == "Test message"

    def test_hook_result_minimal(self):
        """Test: Minimal HookResult"""
        from core import HookResult

        result = HookResult()
        output = result.to_dict()

        assert output["continue"] is True
        assert "systemMessage" not in output or output.get("systemMessage") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

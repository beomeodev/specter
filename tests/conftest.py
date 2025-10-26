#!/usr/bin/env python3
"""
@TEST:FOUNDATION-001
@SPEC: specs/001-moai-adk-fixes/spec.md
@CHAIN: @SPEC:FOUNDATION-001 → @TEST:FOUNDATION-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

Pytest configuration and shared fixtures for Specter tests

Adapted from MoAI-ADK for My-Spec workflow.
Provides foundational test fixtures for hooks, subprocess mocking, and temporary directories.
"""

import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock

import pytest

# Add hooks directory to sys.path so tests can import core and handlers modules
HOOKS_DIR = Path(__file__).parent.parent / ".claude" / "hooks" / "ms"
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))


@pytest.fixture
def tmp_path_factory() -> Generator[Path, None, None]:
    """Create a temporary directory for testing.

    Yields:
        Path: Temporary directory path

    Cleanup:
        Automatically removes directory after test
    """
    tmp_dir = Path(tempfile.mkdtemp(prefix="specter_test_"))
    try:
        yield tmp_dir
    finally:
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)


@pytest.fixture
def tmp_git_repo(tmp_path_factory: Path) -> Path:
    """Create a temporary Git repository for testing.

    Args:
        tmp_path_factory: Temporary directory fixture

    Returns:
        Path: Initialized Git repository path with initial commit
    """
    import subprocess

    tmp_dir = tmp_path_factory
    subprocess.run(["git", "init"], cwd=tmp_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_dir,
        check=True,
        capture_output=True,
    )

    # Create initial commit so HEAD exists
    readme = tmp_dir / "README.md"
    readme.write_text("# Test Project\n")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=tmp_dir,
        check=True,
        capture_output=True,
    )

    return tmp_dir


@pytest.fixture
def mock_subprocess() -> Generator[MagicMock, None, None]:
    """Mock subprocess module for testing command execution.

    Yields:
        MagicMock: Mocked subprocess with run() method configured

    Example:
        def test_git_command(mock_subprocess):
            # subprocess.run() calls will use this mock
            result = subprocess.run(["git", "status"])
            mock_subprocess.run.assert_called_once()
    """
    from unittest.mock import patch

    with patch("subprocess.run") as mock_run:
        # Default success response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        yield mock_run


@pytest.fixture
def mock_task_tool() -> Generator[MagicMock, None, None]:
    """Mock Claude Code Task tool for agent delegation testing.

    Yields:
        MagicMock: Mocked Task tool with configurable responses

    Example:
        def test_agent_delegation(mock_task_tool):
            # Task() calls will use this mock
            mock_task_tool.return_value = "Agent completed successfully"
    """
    from unittest.mock import patch

    with patch("builtins.Task") as mock_task:
        yield mock_task


@pytest.fixture
def sample_spec_config() -> dict[str, Any]:
    """Provide sample .specify/memory/constitution.md structure.

    Returns:
        dict: Sample configuration dictionary for My-Spec workflow
    """
    return {
        "project": {
            "name": "test-project",
            "version": "0.0.1",
            "type": "personal",
        },
        "principles": {
            "test_first": True,
            "test_coverage_minimum": 85,
            "max_file_sloc": 500,
            "max_function_loc": 100,
            "max_complexity": 10,
        },
        "workflow": {
            "spec_directory": "specs/",
            "test_directory": "tests/",
            "source_directory": "src/",
        },
    }


@pytest.fixture
def sample_hook_payload() -> dict[str, Any]:
    """Provide sample Claude Code hook payload.

    Returns:
        dict: Sample hook input payload with common fields
    """
    return {
        "cwd": "/workspace/test-project",
        "toolName": "Edit",
        "toolInput": {
            "file_path": "/workspace/test-project/src/example.py",
            "old_string": "def old_function():",
            "new_string": "def new_function():",
        },
    }


@pytest.fixture
def create_spec_file(tmp_path_factory: Path) -> callable:
    """Factory fixture for creating SPEC files with YAML frontmatter.

    Args:
        tmp_path_factory: Temporary directory fixture

    Returns:
        callable: Function to create SPEC files

    Example:
        def test_spec_parsing(create_spec_file):
            spec_path = create_spec_file(
                spec_id="AUTH-001",
                version="1.0.0",
                status="active",
                content="System SHALL authenticate users"
            )
    """
    def _create_spec(
        spec_id: str,
        version: str = "0.0.1",
        status: str = "draft",
        content: str = "Test SPEC content",
    ) -> Path:
        spec_dir = tmp_path_factory / "specs" / f"SPEC-{spec_id}"
        spec_dir.mkdir(parents=True, exist_ok=True)
        spec_file = spec_dir / "spec.md"

        frontmatter = f"""---
id: {spec_id}
version: {version}
status: {status}
created: 2025-10-26
updated: 2025-10-26
---

# @SPEC:{spec_id}: Test Specification

{content}
"""
        spec_file.write_text(frontmatter)
        return spec_file

    return _create_spec

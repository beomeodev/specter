#!/usr/bin/env python3
"""
@TEST:TEST-UTILS-001
@SPEC: specs/001-moai-adk-fixes/spec.md
@CHAIN: @SPEC:FOUNDATION-001 → @TEST:TEST-UTILS-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

Test utilities for hook testing

Provides helper functions for:
- Hook payload generation
- Subprocess mocking
- JSON validation
- File system operations
"""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock


def create_hook_payload(
    event_name: str,
    cwd: str = "/workspace/test-project",
    tool_name: str | None = None,
    tool_input: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Create a valid hook payload for testing.

    Args:
        event_name: Name of the hook event (SessionStart, PreToolUse, etc.)
        cwd: Current working directory
        tool_name: Name of the tool (for PreToolUse, PostToolUse)
        tool_input: Tool input parameters
        **kwargs: Additional payload fields

    Returns:
        dict: Valid hook payload

    Example:
        >>> payload = create_hook_payload(
        ...     "PreToolUse",
        ...     tool_name="Edit",
        ...     tool_input={"file_path": "test.py"}
        ... )
        >>> assert payload["toolName"] == "Edit"
    """
    payload: dict[str, Any] = {
        "cwd": cwd,
        **kwargs,
    }

    if tool_name is not None:
        payload["toolName"] = tool_name

    if tool_input is not None:
        payload["toolInput"] = tool_input

    return payload


def create_edit_payload(
    file_path: str,
    old_string: str,
    new_string: str,
    cwd: str = "/workspace/test-project",
) -> dict[str, Any]:
    """Create PreToolUse payload for Edit tool.

    Args:
        file_path: Path to file being edited
        old_string: String to be replaced
        new_string: Replacement string
        cwd: Current working directory

    Returns:
        dict: PreToolUse Edit payload

    Example:
        >>> payload = create_edit_payload(
        ...     file_path="src/auth.py",
        ...     old_string="def old():",
        ...     new_string="def new():"
        ... )
        >>> assert payload["toolName"] == "Edit"
    """
    return create_hook_payload(
        event_name="PreToolUse",
        cwd=cwd,
        tool_name="Edit",
        tool_input={
            "file_path": file_path,
            "old_string": old_string,
            "new_string": new_string,
        },
    )


def create_bash_payload(
    command: str,
    cwd: str = "/workspace/test-project",
    dangerous: bool = False,
) -> dict[str, Any]:
    """Create PreToolUse payload for Bash tool.

    Args:
        command: Bash command to execute
        cwd: Current working directory
        dangerous: Whether command is dangerous (rm, git reset, etc.)

    Returns:
        dict: PreToolUse Bash payload

    Example:
        >>> payload = create_bash_payload("rm -rf data/")
        >>> assert "rm -rf" in payload["toolInput"]["command"]
    """
    return create_hook_payload(
        event_name="PreToolUse",
        cwd=cwd,
        tool_name="Bash",
        tool_input={
            "command": command,
        },
    )


def mock_subprocess_success(
    stdout: str = "",
    stderr: str = "",
    returncode: int = 0,
) -> MagicMock:
    """Create a mock subprocess with successful result.

    Args:
        stdout: Standard output text
        stderr: Standard error text
        returncode: Exit code (0 = success)

    Returns:
        MagicMock: Configured mock subprocess

    Example:
        >>> from unittest.mock import patch
        >>> with patch('subprocess.run', mock_subprocess_success("OK")):
        ...     result = subprocess.run(["echo", "test"])
        ...     assert result.stdout == "OK"
    """
    mock = MagicMock()
    mock.returncode = returncode
    mock.stdout = stdout
    mock.stderr = stderr
    return mock


def mock_subprocess_failure(
    error_message: str = "Command failed",
    returncode: int = 1,
) -> MagicMock:
    """Create a mock subprocess with failure result.

    Args:
        error_message: Error message for stderr
        returncode: Exit code (non-zero = failure)

    Returns:
        MagicMock: Configured mock subprocess

    Example:
        >>> from unittest.mock import patch
        >>> with patch('subprocess.run', mock_subprocess_failure()):
        ...     result = subprocess.run(["false"])
        ...     assert result.returncode == 1
    """
    return mock_subprocess_success(
        stdout="",
        stderr=error_message,
        returncode=returncode,
    )


def validate_hook_output(output: dict[str, Any]) -> bool:
    """Validate hook output conforms to Claude Code Hook schema.

    Args:
        output: Hook response dictionary

    Returns:
        bool: True if valid, False otherwise

    Validates:
        - Has 'continue' field (bool)
        - Has 'systemMessage' field (str) if present
        - Has 'userMessage' field (str) if present

    Example:
        >>> output = {"continue": True, "systemMessage": "OK"}
        >>> assert validate_hook_output(output) == True
    """
    if not isinstance(output, dict):
        return False

    # 'continue' field is required
    if "continue" not in output:
        return False

    if not isinstance(output["continue"], bool):
        return False

    # Optional fields validation
    if "systemMessage" in output and not isinstance(output["systemMessage"], str):
        return False

    if "userMessage" in output and not isinstance(output["userMessage"], str):
        return False

    return True


def create_temp_spec_file(
    tmp_path: Path,
    spec_id: str,
    version: str = "0.0.1",
    status: str = "draft",
    content: str = "Test SPEC content",
) -> Path:
    """Create a temporary SPEC file with YAML frontmatter.

    Args:
        tmp_path: Temporary directory path
        spec_id: SPEC ID (e.g., "AUTH-001")
        version: Version string
        status: SPEC status (draft, active, completed, archived)
        content: SPEC body content

    Returns:
        Path: Created SPEC file path

    Example:
        >>> spec_file = create_temp_spec_file(
        ...     tmp_path,
        ...     spec_id="AUTH-001",
        ...     content="System SHALL authenticate"
        ... )
        >>> assert spec_file.exists()
    """
    spec_dir = tmp_path / "specs" / f"SPEC-{spec_id}"
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


def assert_fail_open(output: dict[str, Any]) -> None:
    """Assert that hook output is fail-open compliant.

    Args:
        output: Hook response dictionary

    Raises:
        AssertionError: If output is not fail-open

    Fail-open requirements:
        - continue = True
        - systemMessage contains error information
        - Does not block execution

    Example:
        >>> output = {"continue": True, "systemMessage": "⚠️ Error occurred"}
        >>> assert_fail_open(output)  # Passes
    """
    assert output.get("continue") is True, "Hook must continue on failure (fail-open)"
    assert "systemMessage" in output, "Hook must provide systemMessage on failure"
    assert len(output["systemMessage"]) > 0, "systemMessage must not be empty"


def read_json_file(file_path: Path) -> dict[str, Any]:
    """Read and parse a JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        dict: Parsed JSON content

    Raises:
        json.JSONDecodeError: If file is not valid JSON

    Example:
        >>> data = read_json_file(Path("config.json"))
        >>> assert isinstance(data, dict)
    """
    with open(file_path, "r") as f:
        return json.load(f)


def write_json_file(file_path: Path, data: dict[str, Any]) -> None:
    """Write data to JSON file.

    Args:
        file_path: Path to JSON file
        data: Data to write

    Example:
        >>> write_json_file(Path("output.json"), {"key": "value"})
    """
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

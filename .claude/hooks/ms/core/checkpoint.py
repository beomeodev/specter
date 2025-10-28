#!/usr/bin/env python3
"""
@CODE:HOOKS-002
@SPEC: specs/002-moai-adk-integration/spec.md
@TEST: tests/hooks/test_pre_tool_use.py
@CHAIN: @SPEC:HOOKS-002 → @TEST:HOOKS-002 → @CODE:HOOKS-002
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

Event-Driven Checkpoint System for My-Spec

Adapted from MoAI-ADK for My-Spec workflow.
Automatically detects risky operations and creates Git checkpoints before execution.

Key differences from MoAI-ADK:
- Uses .specify/ instead of .moai/
- Stricter MultiEdit threshold (≥5 files vs MoAI's ≥10)
- My-Spec specific critical files (constitution.md, config.json)
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


def detect_risky_operation(tool_name: str, tool_args: dict[str, Any], cwd: str) -> tuple[bool, str]:
    """Detect risky operations before tool execution.

    Automatically identifies dangerous operations that could cause data loss or
    break the project. When detected, triggers checkpoint creation before execution.

    Args:
        tool_name: Name of the Claude Code tool (Bash, Edit, Write, MultiEdit)
        tool_args: Tool argument dictionary
        cwd: Project root directory path

    Returns:
        (is_risky, operation_type) tuple
        - is_risky: Whether the operation is dangerous (bool)
        - operation_type: operation type (str: delete, merge, script, critical-file, refactor)

    Risky Operations:
        - Bash tool: rm -rf, git rm, git merge, git reset --hard, git rebase, script execution
        - Edit/Write tool: CLAUDE.md, .specify/memory/constitution.md, .specify/config.json
        - MultiEdit tool: Edit ≥5 files simultaneously (My-Spec threshold, stricter than MoAI's ≥10)
        - Script execution: python, node, bash, sh (potentially destructive)

    Examples:
        >>> detect_risky_operation("Bash", {"command": "rm -rf docs/src/"}, ".")
        (True, 'delete')
        >>> detect_risky_operation("Edit", {"file_path": ".specify/memory/constitution.md"}, ".")
        (True, 'critical-file')
        >>> detect_risky_operation("Read", {"file_path": "test.py"}, ".")
        (False, '')

    Notes:
        - Minimizes false positives: ignore safe operations
        - Performance: lightweight string matching (<1ms)
        - My-Spec optimized: stricter thresholds for safety
    """
    # Bash tool: Detect dangerous commands
    if tool_name == "Bash":
        command = tool_args.get("command", "")

        # Mass Delete
        if any(pattern in command for pattern in ["rm -rf", "git rm"]):
            return (True, "delete")

        # Git merge/reset/rebase
        if any(pattern in command for pattern in ["git merge", "git reset --hard", "git rebase"]):
            return (True, "merge")

        # Execute external script (potentially destructive)
        if any(command.startswith(prefix) for prefix in ["python ", "node ", "bash ", "sh "]):
            return (True, "script")

    # Edit/Write tool: Detect critical files
    if tool_name in ("Edit", "Write"):
        file_path = tool_args.get("file_path", "")

        # My-Spec critical files
        critical_files = [
            "CLAUDE.md",
            ".specify/memory/constitution.md",
            ".specify/config.json",
            ".claude/settings.local.json",
        ]

        if any(cf in file_path for cf in critical_files):
            return (True, "critical-file")

    # MultiEdit tool: Detect large refactors
    # My-Spec uses stricter threshold (≥5 files) than MoAI-ADK (≥10 files)
    if tool_name == "MultiEdit":
        edits = tool_args.get("edits", [])
        if len(edits) >= 5:
            return (True, "refactor")

    return (False, "")


def create_checkpoint(cwd: str, operation_type: str) -> str:
    """Create Git checkpoint (local branch) before risky operation.

    Automatically creates checkpoints before dangerous operations.
    Uses local Git branches to prevent remote repository contamination.

    Args:
        cwd: Project root directory path
        operation_type: operation type (delete, merge, script, etc.)

    Returns:
        checkpoint_branch: Created branch name
        Returns "checkpoint-failed" on failure (fail-open)

    Branch Naming:
        before-{operation}-{YYYYMMDD-HHMMSS}
        Example: before-delete-20251026-143000

    Examples:
        >>> create_checkpoint(".", "delete")
        'before-delete-20251026-143000'

    Notes:
        - Creates only local branch (no remote push)
        - Fail-open: ignores Git errors and continues execution
        - Does not check dirty working directory (allows uncommitted changes)
        - Automatically logs checkpoint to .specify/checkpoints.log
        - Uses .specify/ directory (My-Spec convention, not .moai/)
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch_name = f"before-{operation_type}-{timestamp}"

    try:
        # Create a new local branch from the current branch (without checking out)
        subprocess.run(
            ["git", "branch", branch_name],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )

        # Log checkpoint to .specify/checkpoints.log
        log_checkpoint(cwd, branch_name, operation_type)

        return branch_name

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        # Fail-open: ignore Git error and continue execution
        return "checkpoint-failed"


def log_checkpoint(cwd: str, branch_name: str, operation_type: str) -> None:
    """Log checkpoint creation to .specify/checkpoints.log.

    Records checkpoint creation history in JSON Lines format.
    SessionStart reads this log to display recent checkpoints.

    Args:
        cwd: Project root directory path
        branch_name: Created checkpoint branch name
        operation_type: operation type

    Log Format (JSON Lines):
        {"timestamp": "2025-10-26T14:30:00", "branch": "before-delete-...", "operation": "delete"}

    Examples:
        >>> log_checkpoint(".", "before-delete-20251026-143000", "delete")
        # Adds 1 line to .specify/checkpoints.log

    Notes:
        - Uses .specify/ directory (My-Spec convention, not .moai/)
        - Creates directory if it doesn't exist
        - Appends to existing log (preserves history)
        - Fail-open: ignores write errors (not critical)
    """
    log_file = Path(cwd) / ".specify" / "checkpoints.log"

    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "branch": branch_name,
            "operation": operation_type,
        }

        with log_file.open("a") as f:
            f.write(json.dumps(log_entry) + "\n")

    except (OSError, PermissionError):
        # Fail-open: ignore log failures (not critical)
        pass


def list_checkpoints(cwd: str, max_count: int = 10) -> list[dict[str, str]]:
    """List recent checkpoints from .specify/checkpoints.log.

    Returns a list of recently created checkpoints for SessionStart display
    and checkpoint restoration commands.

    Args:
        cwd: Project root directory path
        max_count: Maximum number to return (default 10 items)

    Returns:
        Checkpoint list (most recent first)
        [{"timestamp": "...", "branch": "...", "operation": "..."}, ...]

    Examples:
        >>> list_checkpoints(".")
        [
            {"timestamp": "2025-10-26T14:30:00", "branch": "before-delete-...", "operation": "delete"},
            {"timestamp": "2025-10-26T14:25:00", "branch": "before-merge-...", "operation": "merge"},
        ]

    Notes:
        - Uses .specify/ directory (My-Spec convention, not .moai/)
        - Returns empty list if log file doesn't exist
        - Ignores lines with JSON parsing errors
        - Returns only the latest max_count entries
    """
    log_file = Path(cwd) / ".specify" / "checkpoints.log"

    if not log_file.exists():
        return []

    checkpoints = []

    try:
        with log_file.open("r") as f:
            for line in f:
                try:
                    checkpoints.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    # Ignore lines with parsing errors
                    pass
    except (OSError, PermissionError):
        return []

    # Return only the most recent max_count items
    return checkpoints[-max_count:]


__all__ = [
    "detect_risky_operation",
    "create_checkpoint",
    "log_checkpoint",
    "list_checkpoints",
]

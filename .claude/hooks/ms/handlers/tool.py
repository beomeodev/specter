#!/usr/bin/env python3
"""
@CODE:HOOKS-002
@SPEC: specs/002-moai-adk-integration/spec.md
@TEST: tests/hooks/test_pre_tool_use.py
@CHAIN: @SPEC:HOOKS-002 → @TEST:HOOKS-002 → @CODE:HOOKS-002
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

Tool usage event handlers for My-Spec Hooks

Adapted from MoAI-ADK for My-Spec workflow.
Handles PreToolUse and PostToolUse events with automatic checkpoint creation.
"""

import sys
from pathlib import Path

# Add hooks directory to path for imports
HOOKS_DIR = Path(__file__).resolve().parents[1]
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

from core import HookPayload, HookResult  # noqa: E402
from core.checkpoint import create_checkpoint, detect_risky_operation  # noqa: E402
from core.immutable_protection import is_file_unlocked, scan_immutable_marker  # noqa: E402


def handle_pre_tool_use(payload: HookPayload) -> HookResult:
    """PreToolUse event handler with Event-Driven Checkpoint and @IMMUTABLE protection.

    Automatically creates checkpoints before dangerous operations and blocks
    Edit/Write operations on @IMMUTABLE protected files.

    Args:
        payload: Claude Code event payload
                 (includes tool, arguments, cwd keys)

    Returns:
        HookResult(
            system_message=notification message;
            continue_execution=True (allow) or False (block @IMMUTABLE edit)
        )

    Protection Layers:
        1. @IMMUTABLE Protection: Block Edit/Write on protected files
        2. Checkpoint Creation: Auto-checkpoint before risky operations

    Checkpoint Triggers:
        - Bash: rm -rf, git rm, git merge, git reset --hard, git rebase, script execution
        - Edit/Write: CLAUDE.md, .specify/memory/constitution.md, .specify/config.json
        - MultiEdit: ≥5 files (My-Spec threshold, stricter than MoAI's ≥10)

    Examples:
        @IMMUTABLE file edit attempt:
        → "🚫 Cannot edit @IMMUTABLE file: constitution.md\nUse `/ms.unlock <file>` to unlock"

        Bash tool (rm -rf) detection:
        → "🛡️ Checkpoint created: before-delete-20251026-143000"

    Notes:
        - @IMMUTABLE protection BLOCKS execution (continue_execution=False)
        - Checkpoint creation allows execution (continue_execution=True)
        - Fail-open for errors: Continues on ripgrep/checkpoint failures
        - Uses .specify/ directory (My-Spec convention, not .moai/)
    """
    tool_name = payload.get("tool", "")
    tool_args = payload.get("arguments", {})
    cwd = payload.get("cwd", ".")

    # Layer 1: @IMMUTABLE Protection (BLOCKING)
    # Check if Edit/Write targets @IMMUTABLE file
    if tool_name in ("Edit", "Write"):
        file_path = tool_args.get("file_path", "")
        if file_path:
            # Check if file is @IMMUTABLE protected
            if scan_immutable_marker(file_path):
                # Check if file is unlocked in current session
                if not is_file_unlocked(file_path):
                    # BLOCK operation - @IMMUTABLE protection active
                    system_message = (
                        f"🚫 Cannot edit @IMMUTABLE file: {Path(file_path).name}\n"
                        f"\n"
                        f"This file is protected to prevent accidental modification.\n"
                        f"\n"
                        f"To unlock:\n"
                        f"  1. Run: `/ms.unlock {file_path}`\n"
                        f"  2. Provide justification (≥10 chars)\n"
                        f"  3. Git checkpoint will be created\n"
                        f"  4. Unlock lasts for current session only\n"
                        f"\n"
                        f"Protected file: {file_path}"
                    )
                    return HookResult(
                        system_message=system_message,
                        continue_execution=False,  # BLOCK operation
                    )

    # Layer 2: Checkpoint Creation (NON-BLOCKING)
    # Detect risky operation
    is_risky, operation_type = detect_risky_operation(tool_name, tool_args, cwd)

    # Create checkpoint when risk detected
    if is_risky:
        checkpoint_branch = create_checkpoint(cwd, operation_type)

        if checkpoint_branch != "checkpoint-failed":
            system_message = (
                f"🛡️ Checkpoint created: {checkpoint_branch}\n"
                f"   Operation: {operation_type}\n"
                f"   Restore: git checkout {checkpoint_branch}"
            )

            return HookResult(system_message=system_message, continue_execution=True)

    # No protection needed - continue silently
    return HookResult(continue_execution=True)


def handle_post_tool_use(payload: HookPayload) -> HookResult:
    """PostToolUse event handler with auto-formatting support.

    Automatically formats code files after Edit/Write operations.
    Runs formatters in background to avoid blocking execution.

    Args:
        payload: Claude Code event payload
                 (includes tool, arguments, cwd keys)

    Returns:
        HookResult(
            system_message=Formatting notification (when formatter runs);
            continue_execution=True (always continue)
        )

    Auto-Formatting Support:
        - Python files (.py): Black formatter
        - TypeScript/JavaScript (.ts, .tsx, .js, .jsx): Prettier
        - Runs asynchronously in background (non-blocking)

    Examples:
        Edit tool completes on "docs/src/main.py"
        → Runs: black docs/src/main.py (in background)

    Notes:
        - Only formats on Edit/Write completion (not Read)
        - Formatters must be installed (black, prettier)
        - Fail-open: Ignores formatter errors (continues execution)
        - Background execution: Does not block Claude Code
    """
    import subprocess

    tool_name = payload.get("tool", "")
    tool_args = payload.get("arguments", {})
    cwd = payload.get("cwd", ".")

    # Only format on Edit/Write completion
    if tool_name not in ("Edit", "Write"):
        return HookResult(continue_execution=True)

    file_path = tool_args.get("file_path", "")
    if not file_path:
        return HookResult(continue_execution=True)

    # Determine formatter based on file extension
    formatter_cmd = None
    if file_path.endswith(".py"):
        formatter_cmd = ["black", file_path]
    elif file_path.endswith((".ts", ".tsx", ".js", ".jsx")):
        formatter_cmd = ["npx", "prettier", "--write", file_path]

    if not formatter_cmd:
        # No formatter for this file type
        return HookResult(continue_execution=True)

    # Run formatter in background (async, non-blocking)
    try:
        subprocess.Popen(
            formatter_cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        # Don't show formatting message to avoid noise
        # Formatters run silently in background
        return HookResult(continue_execution=True)
    except (FileNotFoundError, subprocess.SubprocessError):
        # Fail-open: Formatter not installed or failed - continue silently
        return HookResult(continue_execution=True)


__all__ = ["handle_pre_tool_use", "handle_post_tool_use"]

#!/usr/bin/env python3
"""
@CODE:HOOKS-001
@SPEC: specs/002-moai-adk-integration/spec.md
@TEST: tests/hooks/test_session_hooks.py
@CHAIN: @SPEC:HOOKS-001 → @TEST:HOOKS-001 → @CODE:HOOKS-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

Session event handlers

SessionStart, SessionEnd event handling adapted for My-Spec workflow.
"""

from core import HookPayload, HookResult
from core.project import (
    calculate_tag_integrity,
    count_specs,
    detect_language,
    get_git_info,
)


def handle_session_start(payload: HookPayload) -> HookResult:
    """SessionStart event handler

    When Claude Code Session starts, it displays a summary of project status.
    You can check the language, Git status, SPEC progress, and TAG integrity at a glance.

    Args:
        payload: Claude Code event payload (cwd key required)

    Returns:
        HookResult(system_message=project status summary message)

    Message Format:
        🚀 My-Spec Session Started
           Language: {language}
           Git Branch: {branch} ({commit hash})
           Changes: {Number of Changed Files}

    Note:
        - Claude Code processes SessionStart in several stages (clear → compact)
        - Display message only at "compact" stage to prevent duplicate output
        - "clear" step returns minimal result (empty hookSpecificOutput)
        - Fail-open: All errors are caught, hook never blocks session start
    """
    # Claude Code SessionStart runs in several stages (clear, compact, etc.)
    # Ignore the "clear" stage and output messages only at the "compact" stage
    event_phase = payload.get("phase", "")
    if event_phase == "clear":
        # Return minimal valid Hook result for clear phase
        return HookResult(continue_execution=True)

    cwd = payload.get("cwd", ".")

    try:
        # Gather project info (fail-open on errors)
        language = detect_language(cwd)
        git_info = get_git_info(cwd)
        specs = count_specs(cwd)
        tag_integrity = calculate_tag_integrity(cwd)

        branch = git_info.get("branch", "N/A")
        commit = git_info.get("commit", "N/A")[:7]
        changes = git_info.get("changes", 0)
        spec_progress = f"{specs['completed']}/{specs['total']}"

        # system_message: displayed directly to the user
        lines = [
            "🚀 My-Spec Session Started",
            f"   Language: {language}",
            f"   Git Branch: {branch} ({commit})",
            f"   Changes: {changes}",
        ]

        system_message = "\n".join(lines)

        return HookResult(system_message=system_message)

    except Exception as e:
        # Fail-open: return success even on error
        error_message = f"⚠️ SessionStart hook error: {e}\nSession continues normally."
        return HookResult(continue_execution=True, system_message=error_message)


def handle_session_end(payload: HookPayload) -> HookResult:
    """SessionEnd event handler (default implementation)"""
    return HookResult()


__all__ = ["handle_session_start", "handle_session_end"]

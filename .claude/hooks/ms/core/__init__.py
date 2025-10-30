#!/usr/bin/env python3
"""
@CODE:HOOKS-001
@SPEC: specs/002-moai-adk-integration/spec.md
@TEST: tests/hooks/test_session_hooks.py
@CHAIN: @SPEC:HOOKS-001 → @TEST:HOOKS-001 → @CODE:HOOKS-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

Core module for My-Spec Hooks

Adapted from MoAI-ADK for My-Spec workflow.
Common type definitions and utility functions.
"""

from dataclasses import dataclass, field
from typing import Any, Literal, NotRequired, TypedDict


class HookPayload(TypedDict):
    """Claude Code Hook event payload type definition

    Data structure that Claude Code passes to the Hook script.
    Use NotRequired because fields may vary depending on the event.
    """

    cwd: str
    phase: NotRequired[str]  # SessionStart phases (clear, compact)
    userPrompt: NotRequired[str]  # UserPromptSubmit events
    tool: NotRequired[str]  # PreToolUse/PostToolUse events
    arguments: NotRequired[dict[str, Any]]  # Tool arguments


@dataclass
class HookResult:
    """Hook execution result following Claude Code standard schema.

    Attributes conform to Claude Code Hook output specification:
    https://docs.claude.com/en/docs/claude-code/hooks

    Standard Fields (Claude Code schema - included in JSON output):
        continue_execution: Allow execution to continue (default True)
        suppress_output: Suppress hook output display (default False)
        decision: "approve" or "block" operation (optional)
        reason: Explanation for decision (optional)
        permission_decision: "allow", "deny", or "ask" (optional)
        system_message: Message displayed to user (top-level field)

    Internal Fields (My-Spec only - NOT in JSON output):
        context_files: List of context files to load (internal use only)
        suggestions: Suggestions for user (internal use only)
        exit_code: Exit code for diagnostics (internal use only)

    Note:
        - systemMessage appears at TOP LEVEL in JSON output
        - hookSpecificOutput is ONLY used for UserPromptSubmit events
        - Internal fields are used for Python logic but not serialized to JSON
    """

    # Claude Code standard fields
    continue_execution: bool = True
    suppress_output: bool = False
    decision: Literal["approve", "block"] | None = None
    reason: str | None = None
    permission_decision: Literal["allow", "deny", "ask"] | None = None

    # My-Spec custom fields
    system_message: str | None = None
    context_files: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    exit_code: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to Claude Code standard Hook output schema.

        Returns:
            Dictionary conforming to Claude Code Hook specification with:
            - Top-level fields: continue, suppressOutput, decision, reason,
              permissionDecision, systemMessage
            - My-Spec internal fields (context_files, suggestions, exit_code)
              are NOT included in JSON output (used for internal logic only)

        Examples:
            >>> result = HookResult(continue_execution=True)
            >>> result.to_dict()
            {'continue': True}

            >>> result = HookResult(decision="block", reason="Dangerous")
            >>> result.to_dict()
            {'decision': 'block', 'reason': 'Dangerous'}

            >>> result = HookResult(system_message="Test")
            >>> result.to_dict()
            {'continue': True, 'systemMessage': 'Test'}

        Note:
            - systemMessage is a TOP-LEVEL field (not nested in hookSpecificOutput)
            - hookSpecificOutput is ONLY used for UserPromptSubmit events
            - context_files, suggestions, exit_code are internal-only fields
        """
        output: dict[str, Any] = {}

        # Add decision or continue flag
        if self.decision:
            output["decision"] = self.decision
        else:
            output["continue"] = self.continue_execution

        # Add reason if provided (works with both decision and permissionDecision)
        if self.reason:
            output["reason"] = self.reason

        # Add suppressOutput if True
        if self.suppress_output:
            output["suppressOutput"] = True

        # Add permissionDecision if set
        if self.permission_decision:
            output["permissionDecision"] = self.permission_decision

        # Add systemMessage at TOP LEVEL (required by Claude Code schema)
        if self.system_message:
            output["systemMessage"] = self.system_message

        # Note: context_files, suggestions, exit_code are internal-only fields
        # and are NOT included in the JSON output per Claude Code schema

        return output

    def to_user_prompt_submit_dict(self) -> dict[str, Any]:
        """UserPromptSubmit Hook-specific output format.

        Claude Code requires a special schema for UserPromptSubmit events.
        The result is wrapped in the standard Hook schema with hookSpecificOutput.

        Returns:
            Claude Code UserPromptSubmit Hook Dictionary matching schema:
            {
                "continue": true,
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": "string"
                }
            }

        Examples:
            >>> result = HookResult(context_files=["tests/"])
            >>> result.to_user_prompt_submit_dict()
            {'continue': True, 'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': '📎 Context: tests/'}}
        """
        # Convert context_files to additionalContext string
        if self.context_files:
            context_str = "\n".join([f"📎 Context: {f}" for f in self.context_files])
        else:
            context_str = ""

        # Add system_message if there is one
        if self.system_message:
            if context_str:
                context_str = f"{self.system_message}\n\n{context_str}"
            else:
                context_str = self.system_message

        return {
            "continue": self.continue_execution,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context_str
            }
        }


from .immutable_protection import (  # noqa: E402
    UnlockRegistry,
    UnlockResult,
    is_file_unlocked,
    scan_immutable_marker,
    unlock_file,
)
from .skill_activator import MatchedSkill, SkillActivator  # noqa: E402

__all__ = [
    "HookPayload",
    "HookResult",
    "UnlockRegistry",
    "UnlockResult",
    "is_file_unlocked",
    "scan_immutable_marker",
    "unlock_file",
    "SkillActivator",
    "MatchedSkill",
]

#!/usr/bin/env python3
"""
@CODE:HOOKS-003
@SPEC: specs/002-moai-adk-integration/spec.md
@TEST: tests/hooks/test_user_prompt_submit.py
@CHAIN: @SPEC:HOOKS-003 → @TEST:HOOKS-003 → @CODE:HOOKS-003
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

User interaction event handlers for My-Spec Hooks

Adapted from MoAI-ADK for My-Spec workflow.
Handles UserPromptSubmit events with Constitution injection for sub-agents.
"""

import sys
from pathlib import Path

# Add hooks directory to path for imports
HOOKS_DIR = Path(__file__).resolve().parents[1]
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

from core import HookPayload, HookResult


def handle_user_prompt_submit(payload: HookPayload) -> HookResult:
    """UserPromptSubmit event handler with Constitution injection.

    Automatically injects Constitution and project context when sub-agents
    are invoked (Task tool usage detected). This ensures all sub-agents
    follow project constraints (EARS, TRUST, TAG principles).

    Args:
        payload: Claude Code event payload
                 (includes userPrompt, cwd keys)

    Returns:
        HookResult(
            system_message=Context injection notification (when Task tool detected);
            context_files=List of context files to load;
            continue_execution=True (always continue)
        )

    Context Injection Triggers:
        - Task tool invocation: "Task(" or "subagent_type=" in prompt
        - Agent delegation: Any sub-agent invocation

    Injected Context Files:
        - .specify/memory/constitution.md (Project Constitution - REQUIRED)
        - docs/ai-context/project-structure.md (Tech stack, file tree - if exists)
        - AGENTS.md (AI instructions, coding standards - if exists)

    Examples:
        User prompt: "Task(subagent_type='Explore', prompt='Find auth code')"
        → Injects Constitution + project context automatically

    Notes:
        - Uses .specify/ directory (My-Spec convention, not .moai/)
        - Only injects on Task tool usage (not for regular prompts)
        - First 8000 tokens of Constitution (to avoid context overflow)
        - Context files returned via context_files list (Claude Code standard)
    """
    user_prompt = payload.get("userPrompt", "")
    cwd = payload.get("cwd", ".")

    # Detect Task tool invocation in prompt
    is_task_tool = "Task(" in user_prompt or "subagent_type=" in user_prompt

    if not is_task_tool:
        # No Task tool detected - no injection needed
        return HookResult(continue_execution=True)

    # Build list of context files to inject
    context_files = []

    # Always inject Constitution (REQUIRED)
    constitution_path = Path(cwd) / ".specify" / "memory" / "constitution.md"
    if constitution_path.exists():
        context_files.append(str(constitution_path))

    # Optionally inject project structure (if exists)
    project_structure_path = Path(cwd) / "docs" / "ai-context" / "project-structure.md"
    if project_structure_path.exists():
        context_files.append(str(project_structure_path))

    # Optionally inject AGENTS.md (if exists)
    agents_md_path = Path(cwd) / "AGENTS.md"
    if agents_md_path.exists():
        context_files.append(str(agents_md_path))

    # Build system message for user
    if context_files:
        system_message = (
            "📎 Auto-Loaded Project Context for Sub-Agent\n\n"
            f"Injected {len(context_files)} context file(s):\n"
        )
        for file_path in context_files:
            system_message += f"  - {file_path}\n"

        system_message += (
            "\n**CRITICAL**: All sub-agent work must comply with:\n"
            "  - Constitution Section IV (EARS requirements)\n"
            "  - Constitution Section V (TRUST 5 principles)\n"
            "  - Constitution Section IX (Project-specific constraints)"
        )
    else:
        system_message = "⚠️ Warning: Constitution not found. Sub-agent may not follow project constraints."

    return HookResult(
        system_message=system_message,
        context_files=context_files,
        continue_execution=True
    )


__all__ = ["handle_user_prompt_submit"]

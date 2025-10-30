#!/usr/bin/env python3
"""
@CODE:HOOKS-003
@SPEC: specs/002-moai-adk-integration/spec.md
@TEST: tests/hooks/test_user_prompt_submit.py
@CHAIN: @SPEC:HOOKS-003 → @TEST:HOOKS-003 → @CODE:HOOKS-003
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-30

User interaction event handlers for My-Spec Hooks

Adapted from MoAI-ADK for My-Spec workflow.
Handles UserPromptSubmit events with:
- Constitution injection for sub-agents
- Skill auto-activation based on user prompts
"""

import sys
from pathlib import Path

# Add hooks directory to path for imports
HOOKS_DIR = Path(__file__).resolve().parents[1]
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

from core import HookPayload, HookResult, SkillActivator


def handle_user_prompt_submit(payload: HookPayload) -> HookResult:
    """UserPromptSubmit event handler with Constitution injection + Skill Auto-Activation.

    Provides two integrated features:
    1. Constitution Injection: Injects project context for sub-agents (Task tool)
    2. Skill Auto-Activation: Suggests relevant skills based on user prompt

    Args:
        payload: Claude Code event payload
                 (includes userPrompt, cwd keys)

    Returns:
        HookResult(
            system_message=Combined Constitution + Skill suggestions;
            context_files=List of context files to load;
            continue_execution=True (always continue)
        )

    Context Injection Triggers (Feature 1):
        - Task tool invocation: "Task(" or "subagent_type=" in prompt
        - Agent delegation: Any sub-agent invocation

    Injected Context Files:
        - .specify/memory/constitution.md (Project Constitution - REQUIRED)
        - docs/ai-context/project-structure.md (Tech stack, file tree - if exists)
        - CLAUDE.md (AI instructions, coding standards - if exists)

    Skill Auto-Activation (Feature 2):
        - Analyzes user prompt for keywords and intent patterns
        - Matches against skill-rules.json triggers
        - Suggests relevant skills (critical → high → medium priority)
        - Works for ALL prompts (not just Task tool)

    Examples:
        User: "Task(subagent_type='Explore', prompt='Find auth code')"
        → Injects Constitution + No skill suggestions (Task tool doesn't need skills)

        User: "How do I write pytest fixtures?"
        → Suggests ms-lang-python skill

        User: "Debug this Python error"
        → Suggests ms-lang-python + ms-essentials-debug skills

    Notes:
        - Uses .specify/ directory (My-Spec convention)
        - Skill suggestions appear BEFORE Constitution injection message
        - Fail-open design: errors in skill activation don't block execution
    """
    user_prompt = payload.get("userPrompt", "")
    cwd = payload.get("cwd", ".")

    messages: list[str] = []
    context_files: list[str] = []

    # Feature 1: Constitution Injection (for Task tool only)
    is_task_tool = "Task(" in user_prompt or "subagent_type=" in user_prompt

    if is_task_tool:
        # Always inject Constitution (REQUIRED)
        constitution_path = Path(cwd) / ".specify" / "memory" / "constitution.md"
        if constitution_path.exists():
            context_files.append(str(constitution_path))

        # Optionally inject project structure (if exists)
        project_structure_path = (
            Path(cwd) / "docs" / "ai-context" / "project-structure.md"
        )
        if project_structure_path.exists():
            context_files.append(str(project_structure_path))

        # Optionally inject CLAUDE.md (if exists)
        claude_md_path = Path(cwd) / "CLAUDE.md"
        if claude_md_path.exists():
            context_files.append(str(claude_md_path))

        # Build Constitution injection message
        if context_files:
            constitution_msg = (
                "📎 Auto-Loaded Project Context for Sub-Agent\n\n"
                f"Injected {len(context_files)} context file(s):\n"
            )
            for file_path in context_files:
                constitution_msg += f"  - {file_path}\n"

            constitution_msg += (
                "\n**CRITICAL**: All sub-agent work must comply with:\n"
                "  - Constitution Section IV (EARS requirements)\n"
                "  - Constitution Section V (TRUST 5 principles)\n"
                "  - Constitution Section IX (Project-specific constraints)"
            )
            messages.append(constitution_msg)
        else:
            messages.append(
                "⚠️ Warning: Constitution not found. Sub-agent may not follow project constraints."
            )

    # Feature 2: Skill Auto-Activation (for ALL prompts, including Task tool)
    # Skip skill suggestions for Task tool (sub-agents handle their own skills)
    if not is_task_tool:
        try:
            activator = SkillActivator(cwd)
            # TODO: Extract open files from payload if available
            # For now, just use empty list (prompt-only matching)
            open_files: list[str] = []
            matched_skills = activator.suggest(user_prompt, open_files)

            if matched_skills:
                skill_msg = activator.format_suggestions(matched_skills)
                # Prepend skill suggestions (show before Constitution message)
                messages.insert(0, skill_msg)
        except Exception as e:
            # Fail-open: Don't block execution if skill activation fails
            import sys

            print(
                f"⚠️ Warning: Skill activation error: {e}",
                file=sys.stderr,
            )

    # Combine all messages
    system_message = "\n".join(messages) if messages else None

    return HookResult(
        system_message=system_message,
        context_files=context_files,
        continue_execution=True,
    )


__all__ = ["handle_user_prompt_submit"]

#!/usr/bin/env python3
"""
@CODE:HOOKS-001
@SPEC: specs/002-moai-adk-integration/spec.md
@TEST: tests/hooks/test_session_hooks.py
@CHAIN: @SPEC:HOOKS-001 → @TEST:HOOKS-001 → @CODE:HOOKS-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

My-Spec Hooks - Main entry point for Claude Code Hooks

Adapted from MoAI-ADK for My-Spec workflow.
A main entry point that routes Claude Code events to the appropriate handlers.

🏗️ Architecture:
┌─────────────────────────────────────────────────────────────┐
│ ms_hooks.py (Router)                                        │
├─────────────────────────────────────────────────────────────┤
│ - CLI argument parsing                                      │
│ - JSON I/O (stdin/stdout)                                   │
│ - Event routing to handlers                                 │
└─────────────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ handlers/ (Event Handlers)                                  │
├─────────────────────────────────────────────────────────────┤
│ - session.py: SessionStart, SessionEnd                      │
│ - user.py: UserPromptSubmit                                 │
│ - tool.py: PreToolUse, PostToolUse                          │
└─────────────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ core/ (Business Logic)                                      │
├─────────────────────────────────────────────────────────────┤
│ - project.py: Language detection, Git info, SPEC progress   │
│ - checkpoint.py: Event-Driven Checkpoint system             │
│ - tags.py: TAG search/verification                          │
└─────────────────────────────────────────────────────────────┘

🛠️ Usage:
    python ms_hooks.py <event_name> < payload.json

📣 Supported Events:
    - SessionStart: Start Session (display project status)
    - PreToolUse: Before tool use (automatic checkpoint creation)
    - PostToolUse: After tool use (post-processing)
    - SessionEnd, UserPromptSubmit

🚦 Exit Codes:
    - 0: Success OR Fail-Open (JSON parsing failure, exception thrown)
    - 1: Usage error only (no arguments provided)
"""

import json
import sys
from pathlib import Path

# Add the hooks directory to sys.path to enable package imports
HOOKS_DIR = Path(__file__).parent
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

from core import HookResult
from handlers import (
    handle_post_tool_use,
    handle_pre_tool_use,
    handle_session_end,
    handle_session_start,
    handle_user_prompt_submit,
)


def main() -> None:
    """Main entry point - Claude Code Hook script

    Receives the event name as a CLI argument and reads the JSON payload through stdin.
    Calls the handler appropriate for the event and outputs the results to stdout as JSON.

    🛠️ Usage:
        python ms_hooks.py <event_name> < payload.json

    📣 Supported Events:
        - SessionStart: Start Session (display project status)
        - PreToolUse: Before tool use (automatic checkpoint creation)
        - PostToolUse: After tool use (post-processing)
        - SessionEnd, UserPromptSubmit

    🚦 Exit Codes:
        - 0: Success OR Fail-Open (JSON parsing failure, exception thrown)
        - 1: Usage error only (no arguments provided)

    📝 Examples:
        $ echo '{"cwd": "."}' | python ms_hooks.py SessionStart
        {"message": "🚀 My-Spec Session Started\\n...", ...}

    🗒️ Notes:
        - Claude Code is automatically called (no need for direct user execution)
        - JSON I/O processing through stdin/stdout
        - Print error message to stderr
        - UserPromptSubmit uses a special output schema (hookEventName + additionalContext)
    """
    # Check for event argument
    if len(sys.argv) < 2:
        print("Usage: ms_hooks.py <event>", file=sys.stderr)
        sys.exit(1)

    event_name = sys.argv[1]

    try:
        # Read JSON from stdin
        input_data = sys.stdin.read()
        # Handle empty stdin by treating it as empty object
        data = json.loads(input_data) if input_data.strip() else {}

        cwd = data.get("cwd", ".")

        # Route to appropriate handler
        handlers = {
            "SessionStart": handle_session_start,
            "SessionEnd": handle_session_end,
            "PreToolUse": handle_pre_tool_use,
            "PostToolUse": handle_post_tool_use,
            "UserPromptSubmit": handle_user_prompt_submit,
        }

        handler = handlers.get(event_name)
        result = handler({"cwd": cwd, **data}) if handler else HookResult()

        # Output Hook result as JSON
        # Note: UserPromptSubmit uses to_user_prompt_submit_dict() for special schema
        if event_name == "UserPromptSubmit":
            print(json.dumps(result.to_user_prompt_submit_dict()))
        else:
            print(json.dumps(result.to_dict()))

        sys.exit(0)

    except json.JSONDecodeError as e:
        # FR-001: Return valid Hook response AND exit with code 0 (fail-open principle)
        error_response = {
            "continue": True,
            "systemMessage": f"⚠️ Hook JSON parse error: {e}"
        }
        print(json.dumps(error_response))
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(0)  # Fail-open: exit with code 0 to prevent blocking Claude Code sessions
    except Exception as e:
        # FR-002: Return valid Hook response AND exit with code 0 (fail-open principle)
        error_response = {
            "continue": True,
            "systemMessage": f"⚠️ Hook execution error: {e}"
        }
        print(json.dumps(error_response))
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(0)  # Fail-open: exit with code 0 to prevent blocking Claude Code sessions


if __name__ == "__main__":
    main()

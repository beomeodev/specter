#!/bin/bash
# ============================================================================
# Hook Wrapper Script - Project Root Auto-Detection
# ============================================================================
# This script ensures hooks always run from the project root directory,
# regardless of the current working directory.
#
# Usage: bash .claude/hooks/ms/run_hook.sh <hook_name>
# Example: bash .claude/hooks/ms/run_hook.sh UserPromptSubmit
# ============================================================================

set -euo pipefail

HOOK_NAME="${1:-}"

if [[ -z "$HOOK_NAME" ]]; then
    echo "Error: Hook name required" >&2
    echo "Usage: $0 <hook_name>" >&2
    exit 1
fi

# Find project root by looking for .claude directory
find_project_root() {
    local current_dir="$PWD"

    # Traverse up to 10 levels to find .claude directory
    for i in {1..10}; do
        if [[ -d "$current_dir/.claude" ]]; then
            echo "$current_dir"
            return 0
        fi

        # Reached filesystem root
        if [[ "$current_dir" == "/" ]]; then
            break
        fi

        current_dir="$(dirname "$current_dir")"
    done

    echo "Error: Could not find project root (.claude directory not found)" >&2
    exit 1
}

PROJECT_ROOT="$(find_project_root)"
HOOK_SCRIPT="$PROJECT_ROOT/.claude/hooks/ms/ms_hooks.py"

# Verify hook script exists
if [[ ! -f "$HOOK_SCRIPT" ]]; then
    echo "Error: Hook script not found at $HOOK_SCRIPT" >&2
    exit 1
fi

# Change to project root and execute hook
cd "$PROJECT_ROOT"
exec python3 "$HOOK_SCRIPT" "$HOOK_NAME"

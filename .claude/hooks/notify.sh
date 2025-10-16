#!/bin/bash
# .claude/hooks/notify.sh
# Purpose: Audio notification for task completion and user input needed
# Triggers: Write, Edit tool completion

# Sound file paths
TASK_COMPLETE=".claude/hooks/sounds/task-complete.mp3"
INPUT_NEEDED=".claude/hooks/sounds/input-needed.mp3"

# Function to play sound (Windows/WSL)
play_sound() {
  local sound_file="$1"

  # Check if file exists
  if [[ ! -f "$sound_file" ]]; then
    return
  fi

  # WSL/Windows: Use PowerShell
  if command -v powershell.exe &> /dev/null; then
    powershell.exe -c "(New-Object Media.SoundPlayer '$sound_file').PlaySync();" 2>/dev/null
  fi
}

# Task completion notification
if [[ "$TOOL_NAME" == "Write" || "$TOOL_NAME" == "Edit" ]]; then
  play_sound "$TASK_COMPLETE"
fi

# User input needed notification (detect from AI output patterns)
if [[ "$TOOL_OUTPUT" == *"user"* && "$TOOL_OUTPUT" == *"confirm"* ]]; then
  play_sound "$INPUT_NEEDED"
fi

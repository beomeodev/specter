#!/bin/bash
# .claude/hooks/constitution-injector.sh
# Purpose: Auto-inject Constitution and project context into all sub-agents
# Triggers: Task tool invocation

# File paths
CONSTITUTION=".specify/memory/constitution.md"
PROJECT_STRUCTURE="docs/ai-context/project-structure.md"
AGENTS_MD="AGENTS.md"

# Only trigger on Task tool
if [[ "$TOOL_NAME" == "Task" ]]; then

  # Build context injection
  context_injection="## Auto-Loaded Project Context

This sub-agent has automatic access to:
- @$CONSTITUTION (Project Constitution - EARS, TRUST, TAG)
- @$PROJECT_STRUCTURE (Tech stack, file tree - if exists)
- @$AGENTS_MD (AI instructions, coding standards)

**CRITICAL: All work must comply with Constitution Section IV (EARS) and Section V (TRUST).**

---

"

  # Prepend to original prompt
  modified_prompt="${context_injection}${PROMPT}"

  # Output modified prompt
  echo "$modified_prompt"
fi

#!/usr/bin/env bash
# PreToolUse hook (WI-13): mechanically blocks direct invocation of the
# upstream speckit-specify skill/command unless /ms.specify's own gates
# (Feature Map + checklist + Constitution Section IX) already passed for this
# run and left a matching .specify/.ms-gate-pass-<NNN> token.
#
# This is defense-in-depth alongside the MS_FEATUREMAP_GATE_START prompt
# marker /ms.init injects into the upstream file: that marker only guides the
# model, it cannot stop it. This hook is mechanical.
#
# Fails OPEN (allows) on any internal error (missing jq, malformed stdin,
# unexpected schema) — a broken hook must never block unrelated Skill calls.
# See docs/improvements/2026-07-03-workflow-audit-and-plan.md WI-13.

INPUT="$(cat 2>/dev/null || true)"

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

SKILL="$(printf '%s' "$INPUT" | jq -r '.tool_input.skill // empty' 2>/dev/null || true)"

case "$SKILL" in
  speckit-specify|speckit.specify) ;;
  *) exit 0 ;;
esac

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

if compgen -G "${PROJECT_DIR}/.specify/.ms-gate-pass-"'*' > /dev/null 2>&1; then
  exit 0
fi

cat <<'JSON'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Direct /speckit-specify bypasses SPECTER gates. Run /ms.specify."
  }
}
JSON
exit 0

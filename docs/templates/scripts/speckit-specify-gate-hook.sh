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
# Fails OPEN (allows) only when the requested skill can't be determined at all
# (malformed stdin, unexpected schema) — a broken hook must never block
# unrelated Skill calls. Missing `jq` no longer blanket-allows: it falls back
# to a plain-text scan for the skill field (see F-4 in
# docs/improvements/2026-07-03-workflow-audit-and-plan.md).
# See docs/improvements/2026-07-03-workflow-audit-and-plan.md WI-13.

INPUT="$(cat 2>/dev/null || true)"

if command -v jq >/dev/null 2>&1; then
  SKILL="$(printf '%s' "$INPUT" | jq -r '.tool_input.skill // empty' 2>/dev/null || true)"
else
  if printf '%s' "$INPUT" | grep -Eq '"skill"[[:space:]]*:[[:space:]]*"speckit[.-]specify"'; then
    SKILL="speckit-specify"
  else
    exit 0
  fi
fi

case "$SKILL" in
  speckit-specify|speckit.specify) ;;
  *) exit 0 ;;
esac

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# TTL: a token left behind by a session that died between /ms.specify's
# Step 0.3 (write) and Step 3.2 (delete) must not grant a standing bypass —
# only a token written in the last 60 minutes counts as a live gate-pass.
if find "${PROJECT_DIR}/.specify" -maxdepth 1 -name '.ms-gate-pass-*' -mmin -60 2>/dev/null | grep -q .; then
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

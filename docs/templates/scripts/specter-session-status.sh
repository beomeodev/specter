#!/usr/bin/env bash
# SessionStart status injection (WI-15): a compact one-line summary of
# SPECTER state so a fresh session doesn't have to spelunk artifacts to
# answer "where am I". Bookkeeping only -- the real gate derives current facts
# from artifacts and writes no workflow state.
#
# Fails silently (emits nothing, exits 0) if the project has no SPECTER
# artifacts yet, or on any unexpected condition -- this is a convenience
# summary, never a gate, and must never error session start.

FEATURE_MAP="docs/prd/feature-map.md"
PROGRESS="docs/prd/feature-map.progress.md"
GATE_SCRIPT=".specify/scripts/bash/specter-gate.sh"

[ -f "$FEATURE_MAP" ] || exit 0

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

PARTS=()

# Global gate (mechanical facts only, per WI-11's specter-gate.sh).
if [ -x "$GATE_SCRIPT" ]; then
  GLOBAL=$(bash "$GATE_SCRIPT" 2>/dev/null | jq -r '.overall // empty' 2>/dev/null || true)
  [ -n "$GLOBAL" ] && PARTS+=("global gate ${GLOBAL}")
fi

# Next planned Feature: first ⬜ row in ledger order. This does NOT check the
# DAG or predecessor state (2026-07-18 audit #28) — real eligibility is decided
# by /ms.checklist; this line is a pointer, not a verdict.
if [ -f "$PROGRESS" ]; then
  NEXT_ROW=$(grep -m1 '⬜ planned' "$PROGRESS" 2>/dev/null || true)
  NEXT_FEATURE=$(printf '%s' "$NEXT_ROW" | sed -E 's/^\|[[:space:]]*([0-9]+).*/\1/' || true)
  case "$NEXT_FEATURE" in
    ''|*[!0-9]*) ;;
    *) PARTS+=("next planned (deps unchecked): ${NEXT_FEATURE}") ;;
  esac
fi

[ "${#PARTS[@]}" -eq 0 ] && exit 0

JOINED=""
for p in "${PARTS[@]}"; do
  if [ -z "$JOINED" ]; then
    JOINED="$p"
  else
    JOINED="${JOINED}; ${p}"
  fi
done
SUMMARY="🛰️ SPECTER: ${JOINED}"

ESCAPED=$(printf '%s' "$SUMMARY" | jq -Rs . 2>/dev/null || true)
[ -z "$ESCAPED" ] && exit 0

cat <<JSON
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": ${ESCAPED}
  }
}
JSON
exit 0

#!/usr/bin/env bash
# SessionStart status injection (WI-15): a compact one-line summary of
# SPECTER state so a fresh session doesn't have to spelunk artifacts to
# answer "where am I". Bookkeeping only -- the real gates still live in the
# audit artifacts and the WI-11 gate script.
#
# Fails silently (emits nothing, exits 0) if the project has no SPECTER
# artifacts yet, or on any unexpected condition -- this is a convenience
# summary, never a gate, and must never error session start.

FEATURE_MAP="docs/prd/feature-map.md"
PROGRESS="docs/prd/feature-map.progress.md"
LEDGER=".specify/specter-run.jsonl"
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

# Last activity from the run-state ledger (WI-12): the most recent line is
# the most recent step touched, for any Feature.
if [ -f "$LEDGER" ]; then
  LAST_LINE=$(tail -n 1 "$LEDGER" 2>/dev/null || true)
  if [ -n "$LAST_LINE" ]; then
    F=$(printf '%s' "$LAST_LINE" | jq -r '.feature // empty' 2>/dev/null || true)
    STEP=$(printf '%s' "$LAST_LINE" | jq -r '.step // empty' 2>/dev/null || true)
    VERDICT=$(printf '%s' "$LAST_LINE" | jq -r '.verdict // empty' 2>/dev/null || true)
    if [ -n "$STEP" ]; then
      if [ "$VERDICT" = "FAIL" ]; then
        PARTS+=("Feature ${F:-?} blocked at /ms.${STEP} (FAIL)")
      elif [ -n "$F" ]; then
        PARTS+=("Feature ${F} in progress, stopped after /ms.${STEP}")
      fi
    fi
  fi
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

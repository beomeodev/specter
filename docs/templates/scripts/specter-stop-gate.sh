#!/usr/bin/env bash
# SPECTER stop gate: blocks a Claude Code turn from ending while an
# /ms.implement or /ms.review phase is active and gate-relevant files changed
# without fresh executable-gate evidence. Closes the runtime-gate hole found
# in the 2026-07 transcript audit (gates skipped or verdicts claimed without
# running) at the only enforcement point prompts cannot reach: turn end.
#
# Policy (decided 2026-07-07):
# - Scope: inert unless `.specify/.ms-stop-phase` exists. /ms.implement Step 0
#   and /ms.review Step 1 open it; /ms.review clears it on a PASS/WARN verdict
#   and keeps it open on FAIL (the feature is not done).
# - Fresh evidence with ANY verdict (PASS|WARN|FAIL|UNAVAILABLE) allows the
#   turn to end: this gate forces gates to RUN and be reported honestly, never
#   to SUCCEED. Blocking an honest FAIL report would create the endless
#   fix-retry loop this design exists to avoid.
# - Own cap: at most 3 consecutive blocks. Blocks 1-2 direct the agent to run
#   the gates and record the observed result; block 3 directs it to stop
#   fixing and report the honest verdict; after 3 the hook stands down (the
#   harness's built-in 8-block override stays as the outer safety net).
# - Fails OPEN on internal errors (no git repo, unreadable state): a broken
#   hook must never trap a session. pre-commit + CI remain the mechanical
#   backstops. Escape hatch: `specter-stop-gate.sh phase clear`.
# - Known accepted gap: the hook triggers on CHANGES only. A review turn that
#   edits nothing and skips gates is not caught here — verdict honesty for
#   no-change turns stays with the command prompts and the CI backstop.
#
# Modes:
#   specter-stop-gate.sh                        # hook mode (Stop hook; stdin drained)
#   specter-stop-gate.sh phase <implement|review>  # open a gated phase (baseline signature)
#   specter-stop-gate.sh phase clear               # close the phase
#   specter-stop-gate.sh record <implement|review> <PASS|WARN|FAIL|UNAVAILABLE>
#
# The tree signature covers tracked and untracked changes, excluding
# .specify/, docs/, specs/ and *.md — the executable gates (lint/type/test/
# build) never run on those, and /ms.implement legitimately edits tasks.md and
# living docs after its final test run.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
cd "$PROJECT_DIR" 2>/dev/null || exit 0

PHASE_FILE=".specify/.ms-stop-phase"
EVIDENCE_FILE=".specify/.ms-stop-evidence"
BLOCKS_FILE=".specify/.ms-stop-blocks"
SELF_PATH=".specify/scripts/bash/specter-stop-gate.sh"
MAX_BLOCKS=3

PATHSPEC=(":!.specify" ":!docs" ":!specs" ":!*.md")

tree_signature() {
  {
    git rev-parse HEAD 2>/dev/null || echo NOHEAD
    git status --porcelain -- . "${PATHSPEC[@]}" 2>/dev/null
    git diff HEAD -- . "${PATHSPEC[@]}" 2>/dev/null
    # Hash untracked file contents too: a new file edited after `record`
    # would otherwise leave the porcelain line (and the signature) unchanged.
    git ls-files --others --exclude-standard -- . "${PATHSPEC[@]}" 2>/dev/null \
      | while IFS= read -r f; do
          [ -f "$f" ] && git hash-object -- "$f" 2>/dev/null
        done
  } | git hash-object --stdin 2>/dev/null
}

reset_blocks() { rm -f "$BLOCKS_FILE" 2>/dev/null || true; }

usage() {
  echo "usage: specter-stop-gate.sh [phase <implement|review|clear> | record <implement|review> <PASS|WARN|FAIL|UNAVAILABLE>]" >&2
  exit 1
}

emit_block() {
  # Stop-hook block: {"decision":"block","reason":...} on stdout, exit 0.
  local reason="$1"
  reason="${reason//\\/\\\\}"
  reason="${reason//\"/\\\"}"
  printf '{"decision": "block", "reason": "%s"}\n' "$reason"
  exit 0
}

hook_mode() {
  cat >/dev/null 2>&1 || true # drain stdin; loop safety is the block counter

  if [ ! -f "$PHASE_FILE" ]; then
    reset_blocks
    exit 0
  fi
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

  local phase start_sig cur_sig ev_sig ev_phase count
  phase="$(sed -n 1p "$PHASE_FILE" 2>/dev/null)"
  start_sig="$(sed -n 2p "$PHASE_FILE" 2>/dev/null)"
  cur_sig="$(tree_signature)"
  [ -n "$cur_sig" ] || exit 0

  # Nothing gate-relevant changed since the phase opened (read-only turn,
  # clarification question, docs/specs-only edits) — nothing to gate.
  if [ -n "$start_sig" ] && [ "$cur_sig" = "$start_sig" ]; then
    reset_blocks
    exit 0
  fi

  # Fresh evidence — gates ran against exactly this tree, in THIS phase. Any
  # verdict allows; evidence recorded for a different phase does not (an
  # implement-time record must not satisfy the review phase — 2026-07-18
  # audit finding #16).
  ev_sig="$(grep -m1 '^sig=' "$EVIDENCE_FILE" 2>/dev/null | cut -d= -f2-)"
  ev_phase="$(grep -m1 '^phase=' "$EVIDENCE_FILE" 2>/dev/null | cut -d= -f2-)"
  if [ -n "$ev_sig" ] && [ "$ev_sig" = "$cur_sig" ] && [ "$ev_phase" = "$phase" ]; then
    reset_blocks
    exit 0
  fi

  count="$(cat "$BLOCKS_FILE" 2>/dev/null || echo 0)"
  case "$count" in '' | *[!0-9]*) count=0 ;; esac
  if [ "$count" -ge "$MAX_BLOCKS" ]; then
    reset_blocks
    exit 0
  fi
  echo $((count + 1)) >"$BLOCKS_FILE" 2>/dev/null || true

  if [ "$count" -ge $((MAX_BLOCKS - 1)) ]; then
    emit_block "SPECTER stop gate [${phase} phase, final block ${MAX_BLOCKS}/${MAX_BLOCKS}]: stop attempting further fixes. If the executable gates have not run at all, run them once; then record the honest observed verdict (FAIL or UNAVAILABLE is acceptable) with ${SELF_PATH} record ${phase} <PASS|WARN|FAIL|UNAVAILABLE>, and end your turn by reporting the true gate status to the user. The next stop will be allowed."
  fi
  emit_block "SPECTER stop gate [${phase} phase, block $((count + 1))/${MAX_BLOCKS}]: gate-relevant files changed but no fresh executable-gate evidence exists. Run the executable gates now (tests at minimum; lint/type/build as applicable to this phase), then record the observed result with ${SELF_PATH} record ${phase} <PASS|WARN|FAIL|UNAVAILABLE>. Record only a verdict you actually observed."
}

phase_mode() {
  case "${1:-}" in
    clear)
      rm -f "$PHASE_FILE" "$BLOCKS_FILE"
      echo "stop-gate phase cleared"
      ;;
    implement | review)
      mkdir -p .specify
      {
        echo "$1"
        tree_signature
      } >"$PHASE_FILE"
      reset_blocks
      echo "stop-gate phase opened: $1"
      ;;
    *) usage ;;
  esac
}

record_mode() {
  local phase="${1:-}" verdict="${2:-}"
  case "$phase" in implement | review) ;; *) usage ;; esac
  case "$verdict" in PASS | WARN | FAIL | UNAVAILABLE) ;; *) usage ;; esac
  mkdir -p .specify
  {
    echo "sig=$(tree_signature)"
    echo "phase=$phase"
    echo "verdict=$verdict"
    echo "ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } >"$EVIDENCE_FILE"
  reset_blocks
  echo "stop-gate evidence recorded: phase=$phase verdict=$verdict"
}

case "${1:-}" in
  '') hook_mode ;;
  phase) phase_mode "${2:-}" ;;
  record) record_mode "${2:-}" "${3:-}" ;;
  *) usage ;;
esac

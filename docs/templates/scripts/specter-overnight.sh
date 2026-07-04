#!/usr/bin/env bash
# specter-overnight.sh — unattended sequential execution of prepared SPECTER
# Feature cycles, each in its own git worktree, each in a fresh headless session.
#
# Usage:
#   specter-overnight.sh [--dry-run] NNN [NNN ...]
#   nohup specter-overnight.sh 007 008 009 > /tmp/overnight.log 2>&1 &
#
# Contract (see .claude/skills/overnight-run/SKILL.md):
# - Each Feature NNN must have a worktree at $WORKTREE_ROOT/feature-NNN whose run
#   ledger (.specify/specter-run.jsonl) records clarify PASS/WARN — i.e. the human
#   stop was pre-spent in the evening. Unprepared Features are SKIPPED, not run.
# - Features must be DAG-independent (parallel-features eligibility) — failures
#   don't stop the run.
# - This script never merges or releases; morning human does fin/merglease.
#
# Env overrides:
#   WORKTREE_ROOT  (default: .worktrees)
#   CLAUDE_CMD     (default: claude -p --permission-mode acceptEdits)
#   LIMIT_SLEEP    seconds to wait on a session/usage-limit error (default: 1800)
#   LIMIT_RETRIES  max limit-waits per feature (default: 6)
set -uo pipefail   # NOT -e: one feature's failure must not kill the run

WORKTREE_ROOT="${WORKTREE_ROOT:-.worktrees}"
CLAUDE_CMD="${CLAUDE_CMD:-claude -p --permission-mode acceptEdits}"
LIMIT_SLEEP="${LIMIT_SLEEP:-1800}"
LIMIT_RETRIES="${LIMIT_RETRIES:-6}"
LEDGER_REL=".specify/specter-run.jsonl"

DRY_RUN=0
FEATURES=()
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) FEATURES+=("$arg") ;;
  esac
done
[ "${#FEATURES[@]}" -gt 0 ] || { echo "usage: $0 [--dry-run] NNN [NNN ...]" >&2; exit 2; }

MAIN_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" \
  || { echo "ERROR: run from inside the main repo" >&2; exit 2; }
cd "$MAIN_ROOT"
command -v python3 >/dev/null || { echo "ERROR: python3 required" >&2; exit 2; }

# ledger_step_verdict <ledger> <feature> <step> -> prints last verdict for step, or ""
ledger_step_verdict() {
  python3 - "$1" "$2" "$3" << 'PYEOF'
import json, sys
path, feature, step = sys.argv[1], sys.argv[2], sys.argv[3]
verdict = ""
try:
    with open(path, errors="replace") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("cycle") == "feature" and str(rec.get("feature", "")).lstrip("0") \
                    == feature.lstrip("0") and rec.get("step") == step:
                verdict = rec.get("verdict", "")
except OSError:
    pass
print(verdict)
PYEOF
}

# ledger_last_step <ledger> <feature> -> prints "step verdict" of last entry, or ""
ledger_last_step() {
  python3 - "$1" "$2" << 'PYEOF'
import json, sys
path, feature = sys.argv[1], sys.argv[2]
last = ""
try:
    with open(path, errors="replace") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("cycle") == "feature" and str(rec.get("feature", "")).lstrip("0") \
                    == feature.lstrip("0"):
                last = f"{rec.get('step','?')} {rec.get('verdict','?')}"
except OSError:
    pass
print(last)
PYEOF
}

STAMP="$(date +%Y%m%d)"
REPORT_DIR="$MAIN_ROOT/docs/overnight"
REPORT="$REPORT_DIR/REPORT-$STAMP.md"
mkdir -p "$REPORT_DIR"
declare -a RESULTS=()

log() { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }

for NNN in "${FEATURES[@]}"; do
  WT="$MAIN_ROOT/$WORKTREE_ROOT/feature-$NNN"
  LEDGER="$WT/$LEDGER_REL"
  log "=== Feature $NNN ==="

  if [ ! -d "$WT" ]; then
    log "SKIP $NNN: worktree missing at $WT (run evening prep first)"
    RESULTS+=("| $NNN | ⏭️ SKIPPED | worktree missing — evening prep not done |")
    continue
  fi
  CLARIFY="$(ledger_step_verdict "$LEDGER" "$NNN" "clarify")"
  if [ "$CLARIFY" != "PASS" ] && [ "$CLARIFY" != "WARN" ]; then
    log "SKIP $NNN: clarify not pre-spent (ledger verdict: '${CLARIFY:-none}')"
    RESULTS+=("| $NNN | ⏭️ SKIPPED | clarify not pre-spent (verdict: ${CLARIFY:-none}) |")
    continue
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    log "DRY-RUN $NNN: eligible (clarify=$CLARIFY), would run in $WT"
    RESULTS+=("| $NNN | ✅ ELIGIBLE (dry-run) | clarify=$CLARIFY |")
    continue
  fi

  FLOG="$REPORT_DIR/feature-$NNN-$STAMP.log"
  attempt=0
  while :; do
    attempt=$((attempt + 1))
    log "run $NNN (attempt $attempt) → $FLOG"
    ( cd "$WT" && $CLAUDE_CMD "/ms.specter $NNN — 런 원장(.specify/specter-run.jsonl) 기준 중단 지점부터 재개해서 review까지 진행" ) \
      >> "$FLOG" 2>&1
    rc=$?
    if grep -qiE "session limit|usage limit|rate.?limit" "$FLOG" && [ "$attempt" -le "$LIMIT_RETRIES" ]; then
      log "limit hit on $NNN — sleeping ${LIMIT_SLEEP}s (attempt $attempt/$LIMIT_RETRIES)"
      sleep "$LIMIT_SLEEP"
      continue
    fi
    break
  done

  REVIEW="$(ledger_step_verdict "$LEDGER" "$NNN" "review")"
  LAST="$(ledger_last_step "$LEDGER" "$NNN")"
  if [ "$REVIEW" = "PASS" ] || [ "$REVIEW" = "WARN" ]; then
    log "DONE $NNN: review=$REVIEW"
    RESULTS+=("| $NNN | ✅ review $REVIEW | branch ready in $WORKTREE_ROOT/feature-$NNN |")
  else
    log "STOPPED $NNN: last ledger entry='${LAST:-none}' rc=$rc"
    RESULTS+=("| $NNN | ⛔ stopped | last step: ${LAST:-none} (rc=$rc, log: $(basename "$FLOG")) |")
  fi
done

{
  echo "# Overnight Run Report — $STAMP"
  echo
  echo "| Feature | Outcome | Detail |"
  echo "|---|---|---|"
  printf '%s\n' "${RESULTS[@]}"
  echo
  echo "## Morning steps"
  echo "1. Review each ✅ Feature's diff in its worktree."
  echo "2. Merge back SERIALLY per parallel-features Section 5:"
  echo "   first feature: /ms.fin → /ms.merglease; each subsequent: rebase onto"
  echo "   updated master → re-run local-ci → /ms.fin → /ms.merglease."
  echo "3. Clean up each worktree only AFTER its merge is confirmed."
  echo "4. ⛔ Features: open the per-feature log and the worktree ledger tail."
} > "$REPORT"
log "report written: $REPORT"

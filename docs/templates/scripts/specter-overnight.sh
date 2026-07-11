#!/usr/bin/env bash
# specter-overnight.sh — unattended execution of prepared SPECTER Feature cycles,
# each in a fresh headless session. Launched ONLY on the user's explicit overnight
# request; the invocation carries the autonomy this script exercises.
#
# Usage:
#   specter-overnight.sh [--dry-run] [--no-fin] NNN [NNN ...]            # parallel mode
#   specter-overnight.sh --chain [--dry-run] [--no-fin] [--merglease] NNN [NNN ...]
#   nohup specter-overnight.sh 007 008 009 > /tmp/overnight.log 2>&1 &
#
# Contract (see .claude/skills/overnight-run/SKILL.md):
# - Parallel mode: each Feature NNN has its own worktree at
#   $WORKTREE_ROOT/feature-NNN, targets are DAG-independent, failures don't stop
#   the run.
# - Chain mode (--chain): all Features share ONE worktree ($CHAIN_WT), listed in
#   dependency order. Downstream Features get a drift check against upstream
#   as-built results. A failure PARKS every remaining Feature.
# - Every Feature's run ledger (.specify/specter-run.jsonl) must record clarify
#   PASS/WARN — the human stop was pre-spent in the evening. Unprepared Features
#   are SKIPPED (parallel) / PARK the chain (chain), never run.
# - After review PASS/WARN, /ms.fin runs automatically (disable: --no-fin).
# - /ms.merglease runs only with the explicit --merglease flag (chain mode only,
#   end of chain, all Features green). Parallel mode never auto-merges.
#
# Env overrides:
#   WORKTREE_ROOT  (default: .worktrees)
#   CHAIN_WT       (default: .worktrees/overnight-chain)
#   CLAUDE_CMD     (default: claude -p --permission-mode acceptEdits)
#   LIMIT_SLEEP    seconds to wait on a session/usage-limit error (default: 1800)
#   LIMIT_RETRIES  max limit-waits per claude call (default: 6)
set -uo pipefail   # NOT -e: outcome handling below decides what stops the run

WORKTREE_ROOT="${WORKTREE_ROOT:-.worktrees}"
CHAIN_WT="${CHAIN_WT:-.worktrees/overnight-chain}"
CLAUDE_CMD="${CLAUDE_CMD:-claude -p --permission-mode acceptEdits}"
LIMIT_SLEEP="${LIMIT_SLEEP:-1800}"
LIMIT_RETRIES="${LIMIT_RETRIES:-6}"
LEDGER_REL=".specify/specter-run.jsonl"

DRY_RUN=0
CHAIN=0
DO_FIN=1
DO_MERGLEASE=0
FEATURES=()
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --chain) CHAIN=1 ;;
    --no-fin) DO_FIN=0 ;;
    --merglease) DO_MERGLEASE=1 ;;
    -h|--help) sed -n '2,31p' "$0"; exit 0 ;;
    *) FEATURES+=("$arg") ;;
  esac
done
[ "${#FEATURES[@]}" -gt 0 ] || { echo "usage: $0 [--chain] [--dry-run] [--no-fin] [--merglease] NNN [NNN ...]" >&2; exit 2; }
if [ "$DO_MERGLEASE" -eq 1 ] && [ "$CHAIN" -eq 0 ]; then
  echo "ERROR: --merglease is chain-mode only; parallel merges are morning work (serial rebase + re-gate)" >&2
  exit 2
fi

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

# ledger_decisions <ledger> -> prints count of overnight decision records
ledger_decisions() {
  python3 - "$1" << 'PYEOF'
import json, sys
count = 0
try:
    with open(sys.argv[1], errors="replace") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("cycle") == "overnight" and rec.get("type") == "decision":
                count += 1
except OSError:
    pass
print(count)
PYEOF
}

STAMP="$(date +%Y%m%d)"
REPORT_DIR="$MAIN_ROOT/docs/overnight"
REPORT="$REPORT_DIR/REPORT-$STAMP.md"
mkdir -p "$REPORT_DIR"
declare -a RESULTS=()

log() { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }

# run_claude <worktree> <logfile> <prompt> — fresh headless session with
# session/usage-limit backoff. Returns claude's exit code from the final attempt.
run_claude() {
  local wt="$1" flog="$2" prompt="$3" attempt=0 rc
  while :; do
    attempt=$((attempt + 1))
    log "claude -p (attempt $attempt) → $flog"
    ( cd "$wt" && $CLAUDE_CMD "$prompt" ) >> "$flog" 2>&1
    rc=$?
    if grep -qiE "session limit|usage limit|rate.?limit" "$flog" && [ "$attempt" -le "$LIMIT_RETRIES" ]; then
      log "limit hit — sleeping ${LIMIT_SLEEP}s (attempt $attempt/$LIMIT_RETRIES)"
      sleep "$LIMIT_SLEEP"
      continue
    fi
    return "$rc"
  done
}

CHAIN_PARKED=""   # non-empty once a chain feature fails: reason string
PREV_NNN=""       # chain mode: upstream feature of the current one
ALL_GREEN=1

for NNN in "${FEATURES[@]}"; do
  if [ "$CHAIN" -eq 1 ]; then
    WT="$MAIN_ROOT/$CHAIN_WT"
  else
    WT="$MAIN_ROOT/$WORKTREE_ROOT/feature-$NNN"
  fi
  LEDGER="$WT/$LEDGER_REL"
  log "=== Feature $NNN ==="

  if [ -n "$CHAIN_PARKED" ]; then
    log "PARK $NNN: $CHAIN_PARKED"
    RESULTS+=("| $NNN | 🅿️ PARKED | $CHAIN_PARKED |")
    continue
  fi
  if [ ! -d "$WT" ]; then
    log "SKIP $NNN: worktree missing at $WT (run evening prep first)"
    RESULTS+=("| $NNN | ⏭️ SKIPPED | worktree missing — evening prep not done |")
    [ "$CHAIN" -eq 1 ] && CHAIN_PARKED="chain worktree missing" && ALL_GREEN=0
    continue
  fi
  CLARIFY="$(ledger_step_verdict "$LEDGER" "$NNN" "clarify")"
  if [ "$CLARIFY" != "PASS" ] && [ "$CLARIFY" != "WARN" ]; then
    log "SKIP $NNN: clarify not pre-spent (ledger verdict: '${CLARIFY:-none}')"
    RESULTS+=("| $NNN | ⏭️ SKIPPED | clarify not pre-spent (verdict: ${CLARIFY:-none}) |")
    [ "$CHAIN" -eq 1 ] && CHAIN_PARKED="upstream $NNN was not prepared" && ALL_GREEN=0
    continue
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    log "DRY-RUN $NNN: eligible (clarify=$CLARIFY), would run in $WT"
    RESULTS+=("| $NNN | ✅ ELIGIBLE (dry-run) | clarify=$CLARIFY |")
    PREV_NNN="$NNN"
    continue
  fi

  FLOG="$REPORT_DIR/feature-$NNN-$STAMP.log"

  PROMPT="/ms.specter $NNN — 런 원장(.specify/specter-run.jsonl) 기준 중단 지점부터 재개해서 review까지 진행"
  if [ "$CHAIN" -eq 1 ] && [ -n "$PREV_NNN" ]; then
    PROMPT="오버나이트 체인 런: overnight-run 스킬의 'Drift check and the autonomy ladder' 프로토콜대로, 선행 Feature $PREV_NNN의 as-built 결과와 Feature $NNN의 spec 및 [DEPENDS] 표시된 clarify 답변을 먼저 대조하라. 사다리 1·2단이면 결정을 원장에 기록하고 $PROMPT. 3단(PARK)이면 아무것도 진행하지 말고 PARK 사유만 원장에 기록하라."
  fi
  run_claude "$WT" "$FLOG" "$PROMPT"
  rc=$?

  REVIEW="$(ledger_step_verdict "$LEDGER" "$NNN" "review")"
  LAST="$(ledger_last_step "$LEDGER" "$NNN")"
  if [ "$REVIEW" != "PASS" ] && [ "$REVIEW" != "WARN" ]; then
    log "STOPPED $NNN: last ledger entry='${LAST:-none}' rc=$rc"
    RESULTS+=("| $NNN | ⛔ stopped | last step: ${LAST:-none} (rc=$rc, log: $(basename "$FLOG")) |")
    ALL_GREEN=0
    [ "$CHAIN" -eq 1 ] && CHAIN_PARKED="upstream $NNN stopped at '${LAST:-none}'"
    continue
  fi

  FIN_NOTE="fin skipped (--no-fin)"
  if [ "$DO_FIN" -eq 1 ]; then
    run_claude "$WT" "$FLOG" "/ms.fin"
    fin_rc=$?
    HEAD_LINE="$(git -C "$WT" log --oneline -1 2>/dev/null | head -1)"
    if [ "$fin_rc" -eq 0 ]; then
      FIN_NOTE="fin ok — $HEAD_LINE"
    else
      FIN_NOTE="fin rc=$fin_rc — check log"
      ALL_GREEN=0
    fi
  fi
  log "DONE $NNN: review=$REVIEW; $FIN_NOTE"
  RESULTS+=("| $NNN | ✅ review $REVIEW | $FIN_NOTE |")
  PREV_NNN="$NNN"
done

MERGLEASE_NOTE=""
if [ "$DO_MERGLEASE" -eq 1 ] && [ "$DRY_RUN" -eq 0 ]; then
  if [ "$ALL_GREEN" -eq 1 ] && [ -z "$CHAIN_PARKED" ]; then
    WT="$MAIN_ROOT/$CHAIN_WT"
    FLOG="$REPORT_DIR/merglease-$STAMP.log"
    log "chain green — running /ms.merglease (user opted in at launch)"
    run_claude "$WT" "$FLOG" "/ms.merglease"
    MERGLEASE_NOTE="merglease attempted (opt-in): rc=$?, log: $(basename "$FLOG")"
  else
    MERGLEASE_NOTE="merglease opt-in NOT executed — chain not fully green"
  fi
  log "$MERGLEASE_NOTE"
fi

DECISIONS=0
if [ "$CHAIN" -eq 1 ] && [ -f "$MAIN_ROOT/$CHAIN_WT/$LEDGER_REL" ]; then
  DECISIONS="$(ledger_decisions "$MAIN_ROOT/$CHAIN_WT/$LEDGER_REL")"
fi

{
  echo "# Overnight Run Report — $STAMP"
  echo
  [ "$CHAIN" -eq 1 ] && echo "Mode: chain (worktree: $CHAIN_WT)" || echo "Mode: parallel"
  echo
  echo "| Feature | Outcome | Detail |"
  echo "|---|---|---|"
  printf '%s\n' "${RESULTS[@]}"
  echo
  [ -n "$MERGLEASE_NOTE" ] && { echo "$MERGLEASE_NOTE"; echo; }
  if [ "$CHAIN" -eq 1 ]; then
    echo "Autonomous decisions recorded in ledger: $DECISIONS" \
         "(read \"cycle\":\"overnight\",\"type\":\"decision\" records for rung + rationale)"
    echo
  fi
  echo "## Morning steps"
  echo "1. Review each ✅ Feature's diff and EVERY autonomous decision record."
  if [ "$CHAIN" -eq 1 ]; then
    echo "2. Chain branch has per-Feature commits pushed; if --merglease was not used"
    echo "   (or was not executed), run /ms.merglease on the chain branch."
    echo "3. 🅿️/⛔ Features: read the stop reason; PARKs usually route to /ms.expand"
    echo "   or a re-clarify with the user — never a silent retry."
  else
    echo "2. Merge back SERIALLY per parallel-features Section 5: first feature:"
    echo "   /ms.merglease; each subsequent: rebase onto updated master → re-run"
    echo "   local-ci → /ms.merglease. (fin already ran per Feature unless --no-fin.)"
    echo "3. Clean up each worktree only AFTER its merge is confirmed."
    echo "4. ⛔ Features: open the per-feature log and the worktree ledger tail."
  fi
} > "$REPORT"
log "report written: $REPORT"

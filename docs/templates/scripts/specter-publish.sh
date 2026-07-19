#!/usr/bin/env bash
# Deterministic publish helpers for /ms.fin (read-only).
#
# Owns operational facts only: the publish end-state (tree clean, branch
# pushed, PR open). It never mutates the repo and never implies a gate
# verdict — PASS/WARN/FAIL receipts belong to specter-gate.sh.
#
# Usage:
#   specter-publish.sh version
#   specter-publish.sh verify-endstate
#
# Every mode prints one JSON object to stdout, even on malformed input, and
# exits 0. Check states are true | false | not_applicable | unknown — an
# unreachable gh/network never masquerades as "absent" (unknown != false).

set -euo pipefail

TOOL_VERSION="1.0.0"
TOOL_CONTRACT="publish-helpers-v1"

json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/ }"
  s="${s//$'\t'/ }"
  printf '%s' "$s"
}

NOTES=()
note() { NOTES+=("$1"); }

notes_json() {
  local out="[]" i
  if [ "${#NOTES[@]}" -gt 0 ]; then
    out="["
    for i in "${!NOTES[@]}"; do
      [ "$i" -gt 0 ] && out+=","
      out+="\"$(json_escape "${NOTES[$i]}")\""
    done
    out+="]"
  fi
  printf '%s' "$out"
}

CHECKS_JSON=""
add_check() {
  local name="$1" status="$2" evidence="$3"
  [ -n "$CHECKS_JSON" ] && CHECKS_JSON+=","
  CHECKS_JSON+="\"${name}\":{\"status\":\"${status}\",\"evidence\":\"$(json_escape "$evidence")\"}"
}

SUBCOMMAND="${1:-}"
shift || true

if [ "$SUBCOMMAND" = "version" ]; then
  cat <<JSON
{
  "tool": "specter-publish",
  "version": "${TOOL_VERSION}",
  "contract": "${TOOL_CONTRACT}",
  "subcommands": ["version", "verify-endstate"]
}
JSON
  exit 0
fi

if [ "$SUBCOMMAND" = "verify-endstate" ]; then
  if [ "$(git rev-parse --is-inside-work-tree 2>/dev/null)" != "true" ]; then
    # Outside a git work tree every fact is unobservable — emit all-unknown
    # instead of letting suppressed git errors masquerade as clean state.
    cat <<JSON
{
  "tool": "specter-publish",
  "mode": "verify-endstate",
  "branch": null,
  "upstream": null,
  "checks": {
    "tree_clean": {"status":"unknown","evidence":"not inside a git work tree"},
    "pushed": {"status":"unknown","evidence":"not inside a git work tree"},
    "pr_open": {"status":"unknown","evidence":"not inside a git work tree"}
  },
  "notes": ["not inside a git work tree — no publish fact is observable here"]
}
JSON
    exit 0
  fi

  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)
  if [ -z "$branch" ] || [ "$branch" = "HEAD" ]; then
    note "detached HEAD or not a git repository — branch checks unknown"
    branch=""
  fi

  # Upstream resolution: the branch's own upstream first, then the remote's
  # default branch (origin/HEAD) — never a hardcoded origin/master.
  upstream=$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
  if [ -z "$upstream" ]; then
    default_ref=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || true)
    if [ -n "$default_ref" ]; then
      upstream="$default_ref"
      note "no upstream configured for ${branch:-<detached>} — falling back to remote default ${default_ref}"
    else
      note "no upstream and no origin/HEAD — push check unknown"
    fi
  fi

  porcelain=$(git status --porcelain 2>/dev/null || true)
  if [ -z "$porcelain" ]; then
    add_check "tree_clean" "true" "git status --porcelain: empty"
  else
    dirty_count=$(printf '%s\n' "$porcelain" | sed '/^$/d' | wc -l | tr -d ' ')
    add_check "tree_clean" "false" "git status --porcelain: ${dirty_count} entrie(s) remain"
  fi

  if [ -n "$upstream" ]; then
    if git rev-parse -q --verify "$upstream" >/dev/null 2>&1; then
      ahead=$(git rev-list --count "${upstream}..HEAD" 2>/dev/null || echo "")
      if [ "$ahead" = "0" ]; then
        add_check "pushed" "true" "no commits ahead of ${upstream}"
      elif [ -n "$ahead" ]; then
        add_check "pushed" "false" "${ahead} commit(s) ahead of ${upstream}"
      else
        add_check "pushed" "unknown" "rev-list against ${upstream} failed"
      fi
    else
      add_check "pushed" "unknown" "upstream ref ${upstream} not present locally (fetch needed?)"
    fi
  else
    add_check "pushed" "unknown" "no upstream resolvable"
  fi

  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    pr_json=$(gh pr view --json state,url 2>&1) && pr_rc=0 || pr_rc=$?
    if [ "$pr_rc" -eq 0 ]; then
      pr_state=$(printf '%s' "$pr_json" | grep -o '"state":"[A-Z]*"' | head -1 | cut -d'"' -f4)
      pr_url=$(printf '%s' "$pr_json" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)
      if [ "$pr_state" = "OPEN" ]; then
        add_check "pr_open" "true" "${pr_url} (OPEN)"
      else
        add_check "pr_open" "false" "PR state=${pr_state:-unparsed} ${pr_url}"
      fi
    elif printf '%s' "$pr_json" | grep -qi "no pull requests found"; then
      add_check "pr_open" "false" "gh pr view: no pull request for ${branch:-HEAD}"
    else
      add_check "pr_open" "unknown" "gh pr view failed: $(printf '%s' "$pr_json" | head -c 120)"
    fi
  else
    add_check "pr_open" "unknown" "gh unavailable or unauthenticated"
  fi

  cat <<JSON
{
  "tool": "specter-publish",
  "mode": "verify-endstate",
  "branch": $( [ -n "$branch" ] && printf '"%s"' "$(json_escape "$branch")" || printf 'null' ),
  "upstream": $( [ -n "$upstream" ] && printf '"%s"' "$(json_escape "$upstream")" || printf 'null' ),
  "checks": {${CHECKS_JSON}},
  "notes": $(notes_json)
}
JSON
  exit 0
fi

cat <<JSON
{
  "tool": "specter-publish",
  "mode": "error",
  "notes": ["unknown subcommand '$(json_escape "${SUBCOMMAND:-<none>}")' (expected version|verify-endstate)"]
}
JSON
exit 0

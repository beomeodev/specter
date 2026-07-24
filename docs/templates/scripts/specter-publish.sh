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
#   specter-publish.sh review-cache write      (file paths on stdin, one per line)
#   specter-publish.sh review-cache changed    (candidate paths on stdin)
#   specter-publish.sh ci-mode
#   specter-publish.sh self-review-stamp <pr-number>   (stamp body on stdin)
#
# Every mode prints one JSON object to stdout, even on malformed input, and
# exits 0. Check states are true | false | not_applicable | unknown — an
# unreachable gh/network never masquerades as "absent" (unknown != false).
#
# Mutation exceptions to the read-only rule, each deliberate and narrow:
#   - `review-cache write` writes exactly one state file
#     (.specify/review-hash.cache) so the producer (/ms.review) and consumer
#     (/ms.fin ci-mode) share one hash format instead of two prose recipes.
#   - `self-review-stamp` posts one COMMENT review to the given PR (fail-open:
#     every failure is a JSON status, never a nonzero exit).
# Everything else, including ci-mode, stays strictly read-only.

set -euo pipefail

TOOL_VERSION="1.1.0"
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
  "subcommands": ["version", "verify-endstate", "review-cache", "ci-mode", "self-review-stamp"]
}
JSON
  exit 0
fi

# ---- shared review-hash helpers ----

CACHE_FILE=".specify/review-hash.cache"
CACHE_HEADER="# specter-review-hash v2 git-blob-sha1"

# cache_state: echoes v2 | legacy | missing
cache_state() {
  if [ ! -f "$CACHE_FILE" ]; then echo "missing"; return; fi
  if [ "$(head -1 "$CACHE_FILE" 2>/dev/null)" = "$CACHE_HEADER" ]; then echo "v2"; else echo "legacy"; fi
}

# blob_sha <path>: git blob sha of the worktree file, empty when unhashable
blob_sha() {
  git hash-object -- "$1" 2>/dev/null || true
}

paths_json() {
  # paths_json <array-name>: JSON string array from a bash array of paths
  local -n _arr="$1"
  local out="[]" i
  if [ "${#_arr[@]}" -gt 0 ]; then
    out="["
    for i in "${!_arr[@]}"; do
      [ "$i" -gt 0 ] && out+=","
      out+="\"$(json_escape "${_arr[$i]}")\""
    done
    out+="]"
  fi
  printf '%s' "$out"
}

# ---- review-cache ----

if [ "$SUBCOMMAND" = "review-cache" ]; then
  ACTION="${1:-}"

  if [ "$ACTION" = "write" ]; then
    mkdir -p .specify
    count=0
    SKIPPED=()
    tmp_body=""
    while IFS= read -r p; do
      [ -n "$p" ] || continue
      if [ -f "$p" ]; then
        sha=$(blob_sha "$p")
        if [ -n "$sha" ]; then
          tmp_body+="${sha} ${p}"$'\n'
          count=$((count + 1))
        else
          SKIPPED+=("$p")
        fi
      else
        SKIPPED+=("$p")
      fi
    done
    printf '%s\n%s' "$CACHE_HEADER" "$tmp_body" > "$CACHE_FILE"
    [ "${#SKIPPED[@]}" -gt 0 ] && note "${#SKIPPED[@]} path(s) missing or unhashable — not cached"
    cat <<JSON
{
  "tool": "specter-publish",
  "mode": "review-cache-write",
  "cache": "$(json_escape "$CACHE_FILE")",
  "count": ${count},
  "skipped": $(paths_json SKIPPED),
  "notes": $(notes_json)
}
JSON
    exit 0
  fi

  if [ "$ACTION" = "changed" ]; then
    state=$(cache_state)
    declare -A CACHED=()
    if [ "$state" = "v2" ]; then
      while IFS= read -r line; do
        case "$line" in "#"*|"") continue ;; esac
        CACHED["${line#* }"]="${line%% *}"
      done < "$CACHE_FILE"
    else
      note "cache ${state} — every candidate counts as changed"
    fi
    CHANGED=()
    total=0
    while IFS= read -r p; do
      [ -n "$p" ] || continue
      total=$((total + 1))
      if [ "$state" != "v2" ]; then CHANGED+=("$p"); continue; fi
      prev="${CACHED[$p]:-}"
      cur=$(blob_sha "$p")
      if [ -z "$prev" ] || [ -z "$cur" ] || [ "$prev" != "$cur" ]; then
        CHANGED+=("$p")
      fi
    done
    cat <<JSON
{
  "tool": "specter-publish",
  "mode": "review-cache-changed",
  "cache_state": "${state}",
  "total_candidates": ${total},
  "changed": $(paths_json CHANGED),
  "notes": $(notes_json)
}
JSON
    exit 0
  fi

  cat <<JSON
{
  "tool": "specter-publish",
  "mode": "error",
  "notes": ["unknown review-cache action '$(json_escape "${ACTION:-<none>}")' (expected write|changed)"]
}
JSON
  exit 0
fi

# ---- ci-mode ----

if [ "$SUBCOMMAND" = "ci-mode" ]; then
  # Decide whether /ms.fin must re-run the local CI gate. Mismatches, missing
  # artifacts, and unresolvable facts all fall through to RUN — SKIP requires
  # positive evidence that the CI-relevant file set is byte-identical to what
  # the last clean /ms.review validated.
  #
  # Non-invalidating set (decided 2026-07-24): pure documentation — any *.md
  # file, anything under docs/, and .specify/ state. Everything else (code,
  # configs, workflows, lockfiles, scripts) invalidates the review baseline.
  ci="RUN"
  reason=""
  MISMATCHES=()
  IGNORED=()
  cache_entries=0

  is_noninvalidating() {
    case "$1" in
      *.md) return 0 ;;
      docs/*) return 0 ;;
      .specify/*) return 0 ;;
      *) return 1 ;;
    esac
  }

  state=$(cache_state)
  if [ -f ".specify/review-state.txt" ]; then
    reason="unresolved review findings (.specify/review-state.txt present)"
  elif [ "$state" = "missing" ]; then
    reason="no review hash cache — no clean review baseline"
  elif [ "$state" = "legacy" ]; then
    reason="legacy (pre-v2) review hash cache — re-run /ms.review to rebuild it"
  else
    # 1) Every cached entry must still hash-match the worktree.
    while IFS= read -r line; do
      case "$line" in "#"*|"") continue ;; esac
      sha="${line%% *}"; p="${line#* }"
      cache_entries=$((cache_entries + 1))
      if [ ! -f "$p" ]; then
        MISMATCHES+=("${p} (deleted since review)")
      elif [ "$(blob_sha "$p")" != "$sha" ]; then
        MISMATCHES+=("${p} (content changed since review)")
      fi
    done < "$CACHE_FILE"

    # 2) Every outgoing CI-relevant file must already be in the cache.
    #    Outgoing = unpushed range + worktree-vs-HEAD + untracked (the same
    #    set /ms.fin Step 1.5 digests). An unresolvable base is a RUN, not a
    #    guess.
    base=$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
    [ -z "$base" ] && base=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || true)
    if [ -z "$base" ] || ! git rev-parse -q --verify "$base" >/dev/null 2>&1; then
      reason="outgoing range unresolvable (no upstream, no origin/HEAD) — cannot prove the pushed base was reviewed"
    else
      outgoing=$( { git diff --name-only "${base}...HEAD" 2>/dev/null; \
                    git diff --name-only HEAD 2>/dev/null; \
                    git ls-files --others --exclude-standard 2>/dev/null; } \
                  | sed '/^$/d' | sort -u )
      declare -A INCACHE=()
      while IFS= read -r line; do
        case "$line" in "#"*|"") continue ;; esac
        INCACHE["${line#* }"]=1
      done < "$CACHE_FILE"
      while IFS= read -r p; do
        [ -n "$p" ] || continue
        if is_noninvalidating "$p"; then
          IGNORED+=("$p")
        elif [ -z "${INCACHE[$p]:-}" ]; then
          if [ -f "$p" ]; then
            MISMATCHES+=("${p} (outgoing but not in review cache)")
          else
            MISMATCHES+=("${p} (deleted, was never in review cache)")
          fi
        fi
      done <<< "$outgoing"

      if [ -z "$reason" ]; then
        if [ "${#MISMATCHES[@]}" -eq 0 ]; then
          ci="SKIP"
          reason="CI-relevant set byte-identical to the last clean /ms.review (${cache_entries} cached file(s) verified)"
        else
          reason="${#MISMATCHES[@]} CI-relevant difference(s) since the clean review"
        fi
      fi
    fi
  fi

  cat <<JSON
{
  "tool": "specter-publish",
  "mode": "ci-mode",
  "ci": "${ci}",
  "reason": "$(json_escape "$reason")",
  "cache_state": "${state}",
  "cache_entries": ${cache_entries},
  "mismatches": $(paths_json MISMATCHES),
  "ignored_noninvalidating": $(paths_json IGNORED),
  "notes": $(notes_json)
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

# ---- self-review-stamp ----

if [ "$SUBCOMMAND" = "self-review-stamp" ]; then
  # Fail-open by contract: every outcome is a JSON status with exit 0 —
  # this step must never be able to block a publish.
  PR="${1:-}"

  stamp_json() {
    cat <<JSON
{
  "tool": "specter-publish",
  "mode": "self-review-stamp",
  "pr": $( [ -n "$PR" ] && printf '"%s"' "$(json_escape "$PR")" || printf 'null' ),
  "status": "$1",
  "evidence": "$(json_escape "$2")",
  "notes": $(notes_json)
}
JSON
    exit 0
  }

  [ -n "$PR" ] || stamp_json "failed" "missing <pr-number> argument"
  body=$(cat)   # stdin only — the body is never shell-interpolated
  [ -n "$body" ] || stamp_json "failed" "empty stamp body on stdin"
  command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1 \
    || stamp_json "skipped_gh_unavailable" "gh missing or unauthenticated"

  pr_state=$(gh pr view "$PR" --json state -q .state 2>/dev/null || true)
  case "$pr_state" in
    OPEN|MERGED) : ;;
    "") stamp_json "skipped_pr_not_found" "gh pr view ${PR} returned nothing" ;;
    *) stamp_json "skipped_pr_state" "PR state=${pr_state} (stamp only on OPEN|MERGED)" ;;
  esac

  # Content-bound dedupe marker: one identical stamp per PR, ever.
  marker_sha=$(printf '%s' "$body" | git hash-object --stdin 2>/dev/null | cut -c1-12)
  [ -n "$marker_sha" ] || marker_sha="nohash"
  marker="<!-- specter-self-review-stamp ${marker_sha} -->"

  existing=$(gh api "repos/{owner}/{repo}/pulls/${PR}/reviews" --paginate -q '.[].body' 2>/dev/null || true)
  if printf '%s' "$existing" | grep -qF "$marker"; then
    stamp_json "duplicate_skipped" "identical stamp ${marker_sha} already posted on PR ${PR}"
  fi

  tmp=$(mktemp "${TMPDIR:-/tmp}/specter-stamp.XXXXXX") || stamp_json "failed" "mktemp failed"
  trap 'rm -f "$tmp"' EXIT
  printf '%s\n\n%s\n' "$body" "$marker" > "$tmp"
  # COMMENT is mandatory — GitHub forbids approving your own PR.
  err=$(gh pr review "$PR" --comment --body-file "$tmp" 2>&1) && rc=0 || rc=$?
  if [ "$rc" -eq 0 ]; then
    stamp_json "submitted" "COMMENT review posted (marker ${marker_sha})"
  else
    stamp_json "failed" "gh pr review: $(printf '%s' "$err" | head -c 160)"
  fi
fi

cat <<JSON
{
  "tool": "specter-publish",
  "mode": "error",
  "notes": ["unknown subcommand '$(json_escape "${SUBCOMMAND:-<none>}")' (expected version|verify-endstate|review-cache|ci-mode|self-review-stamp)"]
}
JSON
exit 0

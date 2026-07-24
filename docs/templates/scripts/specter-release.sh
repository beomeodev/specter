#!/usr/bin/env bash
# Deterministic release helpers for /ms.merglease (read-only).
#
# Owns operational facts only: semver computation from conventional commits,
# and merge/tag/release end-state verification. Strictly read-only: it never
# mutates the repo, including remote-tracking refs — remote facts come from
# `git ls-remote` (network read), never from `git fetch`. It never implies a
# gate verdict — PASS/WARN/FAIL receipts belong to specter-gate.sh.
#
# Usage:
#   specter-release.sh version
#   specter-release.sh semver [explicit-version]
#   specter-release.sh verify-endstate <pr-number> <tag> [--no-release] [--ledger-feature NNN] [--remote NAME]
#   specter-release.sh classify-ci <pr-number>
#
# Every mode prints one JSON object to stdout, even on malformed input, and
# exits 0. Check states are true | false | not_applicable | unknown — a
# network/permission failure is always `unknown`, never conflated with
# "absent" (false).

set -euo pipefail

TOOL_VERSION="1.2.0"
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

# ---- version ----

if [ "$SUBCOMMAND" = "version" ]; then
  cat <<JSON
{
  "tool": "specter-release",
  "version": "${TOOL_VERSION}",
  "contract": "${TOOL_CONTRACT}",
  "subcommands": ["version", "semver", "verify-endstate", "classify-ci"]
}
JSON
  exit 0
fi

# ---- semver ----

if [ "$SUBCOMMAND" = "semver" ]; then
  EXPLICIT="${1:-}"

  last_tag=$(git describe --tags --abbrev=0 2>/dev/null || true)
  prefix=""
  base_version=""
  tag_malformed=false
  if [ -n "$last_tag" ]; then
    if [[ "$last_tag" =~ ^v[0-9] ]]; then prefix="v"; fi
    stripped="${last_tag#v}"
    if [[ "$stripped" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      base_version="$stripped"
    else
      tag_malformed=true
      note "last tag '${last_tag}' is not semver — an explicit version is required; no version computed"
    fi
  else
    base_version="0.0.0"
    note "no_prior_tag: no tag reachable from HEAD; computing against 0.0.0"
  fi

  shallow=false
  if [ "$(git rev-parse --is-shallow-repository 2>/dev/null)" = "true" ]; then
    shallow=true
    note "shallow repository: commit range may be incomplete — computed version withheld; unshallow or pass an explicit version"
  fi

  range="HEAD"
  [ -n "$last_tag" ] && range="${last_tag}..HEAD"

  majors_json="[]"; minors_json="[]"; patches_json="[]"; unclassified_json="[]"
  majors=0; minors=0; patches=0; unclassified=0; merges=0; total=0

  append_item() {
    # append_item <json-var-name> <full-oid> <subject>
    local var="$1" oid="$2" subject="$3" cur item
    item="\"${oid} $(json_escape "$subject")\""
    eval "cur=\$$var"
    if [ "$cur" = "[]" ]; then eval "$var='[' ; $var+=\$item ; $var+=']'"
    else eval "$var=\${cur%]} ; $var+=',' ; $var+=\$item ; $var+=']'"
    fi
  }

  while IFS= read -r -d $'\x1e' record; do
    [ -n "$record" ] || continue
    oid="${record%%$'\x1f'*}"
    rest="${record#*$'\x1f'}"
    subject="${rest%%$'\x1f'*}"
    body="${rest#*$'\x1f'}"
    oid="${oid//$'\n'/}"
    total=$((total + 1))
    if [ "$(git rev-list --no-walk --merges "$oid" 2>/dev/null | wc -l)" -gt 0 ]; then
      merges=$((merges + 1))
      continue
    fi
    if [[ "$subject" =~ ^[a-z]+(\([^\)]*\))?\!: ]] || [[ "$body" == *"BREAKING CHANGE"* ]]; then
      majors=$((majors + 1)); append_item majors_json "$oid" "$subject"
    elif [[ "$subject" =~ ^feat(\([^\)]*\))?: ]]; then
      minors=$((minors + 1)); append_item minors_json "$oid" "$subject"
    elif [[ "$subject" =~ ^(fix|perf|refactor|chore|docs|test|build|ci|style|revert)(\([^\)]*\))?: ]]; then
      patches=$((patches + 1)); append_item patches_json "$oid" "$subject"
    else
      unclassified=$((unclassified + 1)); append_item unclassified_json "$oid" "$subject"
    fi
  done < <(git log "$range" --pretty=format:'%H'$'\x1f''%s'$'\x1f''%b'$'\x1e' 2>/dev/null || true)

  [ "$merges" -gt 0 ] && note "${merges} merge commit(s) excluded from classification"
  if [ "$unclassified" -gt 0 ]; then
    note "${unclassified} non-conventional commit(s) did not drive the bump — review them; PATCH fallback is a convention, not confidence"
  fi

  bump="patch"
  [ "$minors" -gt 0 ] && bump="minor"
  [ "$majors" -gt 0 ] && bump="major"

  # Compute a version only when the inputs support one: a semver base tag (or
  # no tag at all) AND at least one commit to release. Otherwise the computed
  # version is withheld — an empty string is a refusal, never a guess.
  computed_version=""
  if [ "$tag_malformed" = false ] && [ "$shallow" = false ] && [ "$total" -gt 0 ]; then
    IFS='.' read -r vmaj vmin vpat <<< "$base_version"
    case "$bump" in
      major) vmaj=$((vmaj + 1)); vmin=0; vpat=0 ;;
      minor) vmin=$((vmin + 1)); vpat=0 ;;
      patch) vpat=$((vpat + 1)) ;;
    esac
    computed_version="${prefix}${vmaj}.${vmin}.${vpat}"
  elif [ "$total" -eq 0 ]; then
    note "no commits since ${last_tag:-repository start} — nothing to release; no version computed"
  fi

  explicit_json="null"
  chosen_version="$computed_version"
  if [ -n "$EXPLICIT" ]; then
    explicit_json="\"$(json_escape "$EXPLICIT")\""
    if [[ "$EXPLICIT" =~ ^v?[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      chosen_version="$EXPLICIT"
      [ -n "$computed_version" ] && [ "$EXPLICIT" != "$computed_version" ] \
        && note "explicit version ${EXPLICIT} overrides computed ${computed_version}"
    else
      chosen_version=""
      note "explicit version '${EXPLICIT}' is not semver (expected [v]MAJOR.MINOR.PATCH) — refusing to choose a version"
    fi
  fi

  # Collision and monotonicity guards: a colliding or non-monotonic version is
  # REFUSED (chosen_version cleared), not merely noted — a note alone leaves
  # the bad version actionable downstream.
  if [ -n "$chosen_version" ]; then
    if git rev-parse -q --verify "refs/tags/${chosen_version}" >/dev/null 2>&1; then
      note "collision: tag ${chosen_version} already exists locally — refusing to choose it"
      chosen_version=""
    fi
  fi
  if [ -n "$chosen_version" ]; then
    # Best-effort remote collision check (read-only ls-remote; origin by
    # convention — semver is a local computation, so an unreachable remote
    # degrades to a note, never a guess).
    remote_col=$(git ls-remote origin "refs/tags/${chosen_version}" 2>/dev/null) && col_rc=0 || col_rc=$?
    if [ "$col_rc" -ne 0 ]; then
      note "remote collision check unavailable (git ls-remote origin failed)"
    elif [ -n "$remote_col" ]; then
      note "collision: tag ${chosen_version} already exists on origin — refusing to choose it"
      chosen_version=""
    fi
  fi
  if [ -n "$chosen_version" ] && [ "$tag_malformed" = false ] && [ -n "$last_tag" ]; then
    IFS='.' read -r bmaj bmin bpat <<< "$base_version"
    cstr="${chosen_version#v}"
    IFS='.' read -r cmaj cmin cpat <<< "$cstr"
    # Component-wise comparison — SemVer components are unbounded, so no
    # weighted-sum encoding.
    monotonic=true
    if [ "$cmaj" -lt "$bmaj" ]; then monotonic=false
    elif [ "$cmaj" -eq "$bmaj" ]; then
      if [ "$cmin" -lt "$bmin" ]; then monotonic=false
      elif [ "$cmin" -eq "$bmin" ] && [ "$cpat" -le "$bpat" ]; then monotonic=false
      fi
    fi
    if [ "$monotonic" = false ]; then
      note "not monotonic: ${chosen_version} is not greater than last tag ${last_tag} — refusing to choose it"
      chosen_version=""
    fi
  fi

  cat <<JSON
{
  "tool": "specter-release",
  "mode": "semver",
  "last_tag": $( [ -n "$last_tag" ] && printf '"%s"' "$(json_escape "$last_tag")" || printf 'null' ),
  "tag_prefix": "${prefix}",
  "tag_malformed": ${tag_malformed},
  "commits_total": ${total},
  "drivers": {
    "major": ${majors_json},
    "minor": ${minors_json},
    "patch": ${patches_json}
  },
  "unclassified": ${unclassified_json},
  "computed_bump": "${bump}",
  "computed_version": "$(json_escape "$computed_version")",
  "explicit_version": ${explicit_json},
  "chosen_version": "$(json_escape "$chosen_version")",
  "notes": $(notes_json)
}
JSON
  exit 0
fi

# ---- verify-endstate ----

if [ "$SUBCOMMAND" = "verify-endstate" ]; then
  PR=""
  TAG=""
  NO_RELEASE=false
  LEDGER_FEATURE=""
  REMOTE="origin"
  while [ $# -gt 0 ]; do
    case "$1" in
      --no-release) NO_RELEASE=true ;;
      --ledger-feature) shift; LEDGER_FEATURE="${1:-}" ;;
      --remote) shift; REMOTE="${1:-origin}" ;;
      *) if [ -z "$PR" ]; then PR="$1"; elif [ -z "$TAG" ]; then TAG="$1"; fi ;;
    esac
    shift || true
  done

  if [ -z "$PR" ]; then note "missing required <pr-number> argument"; fi
  if [ -z "$TAG" ] && [ "$NO_RELEASE" = false ]; then note "missing required <tag> argument"; fi

  repository=$(git remote get-url "$REMOTE" 2>/dev/null || true)
  # Strip any embedded userinfo (user:token@) — this JSON must never disclose
  # credentials that a remote URL happens to carry.
  repository=$(printf '%s' "$repository" | sed -E 's#^([a-z+]+://)[^@/]+@#\1#')
  [ -z "$repository" ] && note "remote '${REMOTE}' has no URL — remote checks unknown"

  gh_ok=false
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    gh_ok=true
  else
    note "gh unavailable or unauthenticated — PR/release checks are unknown, not false"
  fi

  merge_oid=""
  base_ref=""
  if [ -n "$PR" ] && [ "$gh_ok" = true ]; then
    pr_json=$(gh pr view "$PR" --json state,mergedAt,mergeCommit,baseRefName 2>/dev/null || true)
    if [ -n "$pr_json" ]; then
      pr_state=$(printf '%s' "$pr_json" | grep -o '"state":"[A-Z]*"' | head -1 | cut -d'"' -f4)
      merge_oid=$(printf '%s' "$pr_json" | grep -o '"oid":"[0-9a-f]*"' | head -1 | cut -d'"' -f4)
      base_ref=$(printf '%s' "$pr_json" | grep -o '"baseRefName":"[^"]*"' | head -1 | cut -d'"' -f4)
      if [ "$pr_state" = "MERGED" ]; then
        add_check "pr_merged" "true" "gh pr view ${PR}: state=MERGED merge=${merge_oid}"
      else
        add_check "pr_merged" "false" "gh pr view ${PR}: state=${pr_state:-unparsed}"
      fi
    else
      add_check "pr_merged" "unknown" "gh pr view ${PR} failed (network/permission/not-found indistinguishable here)"
    fi
  else
    add_check "pr_merged" "unknown" "gh unavailable or PR number missing"
  fi

  # Resolve the base branch: PR metadata first, remote HEAD as fallback —
  # never a hardcoded master.
  if [ -z "$base_ref" ]; then
    base_ref=$(git symbolic-ref --short "refs/remotes/${REMOTE}/HEAD" 2>/dev/null | sed "s|^${REMOTE}/||" || true)
    [ -z "$base_ref" ] && note "base branch unresolvable (no PR metadata, no ${REMOTE}/HEAD) — base checks unknown"
  fi

  # Remote base tip via ls-remote (read-only — this verifier never fetches).
  remote_base_tip=""
  if [ -n "$base_ref" ]; then
    ls_out=$(git ls-remote "$REMOTE" "refs/heads/${base_ref}" 2>/dev/null) && ls_rc=0 || ls_rc=$?
    if [ "$ls_rc" -eq 0 ] && [ -n "$ls_out" ]; then
      remote_base_tip="${ls_out%%$'\t'*}"
    elif [ "$ls_rc" -ne 0 ]; then
      note "git ls-remote ${REMOTE} failed (network?) — remote base checks unknown"
    fi
  fi

  if [ -n "$merge_oid" ] && [ -n "$remote_base_tip" ]; then
    if git cat-file -e "${remote_base_tip}^{commit}" 2>/dev/null; then
      if git merge-base --is-ancestor "$merge_oid" "$remote_base_tip" 2>/dev/null; then
        add_check "merge_on_remote_base" "true" "merge ${merge_oid} is ancestor of ${REMOTE}/${base_ref} tip ${remote_base_tip}"
      else
        add_check "merge_on_remote_base" "false" "merge ${merge_oid} not in history of ${REMOTE}/${base_ref} tip ${remote_base_tip}"
      fi
    else
      add_check "merge_on_remote_base" "unknown" "remote tip ${remote_base_tip} not present locally (read-only verifier does not fetch — fetch and re-run to resolve)"
    fi
  else
    add_check "merge_on_remote_base" "unknown" "base branch, merge oid, or remote tip unresolved"
  fi

  if [ -n "$base_ref" ] && [ -n "$merge_oid" ]; then
    if git rev-parse -q --verify "refs/heads/${base_ref}" >/dev/null 2>&1 \
       && git merge-base --is-ancestor "$merge_oid" "refs/heads/${base_ref}" 2>/dev/null; then
      add_check "local_base_pulled" "true" "local ${base_ref} contains merge ${merge_oid}"
    else
      add_check "local_base_pulled" "false" "local ${base_ref} missing or behind merge ${merge_oid}"
    fi
  else
    add_check "local_base_pulled" "unknown" "base branch or merge oid unresolved"
  fi

  if [ "$NO_RELEASE" = true ]; then
    add_check "tag_local" "not_applicable" "--no-release"
    add_check "tag_remote" "not_applicable" "--no-release"
    add_check "tag_target" "not_applicable" "--no-release"
    add_check "tag_remote_target" "not_applicable" "--no-release"
    add_check "release_exists" "not_applicable" "--no-release"
  elif [ -n "$TAG" ]; then
    if git rev-parse -q --verify "refs/tags/${TAG}" >/dev/null 2>&1; then
      tag_target=$(git rev-parse "${TAG}^{commit}" 2>/dev/null || true)
      add_check "tag_local" "true" "refs/tags/${TAG} -> ${tag_target}"
      if [ -n "$merge_oid" ]; then
        if [ "$tag_target" = "$merge_oid" ]; then
          add_check "tag_target" "true" "local tag dereferences to the PR merge commit ${merge_oid}"
        else
          add_check "tag_target" "false" "local tag -> ${tag_target}, expected merge ${merge_oid}"
        fi
      else
        add_check "tag_target" "unknown" "merge oid unresolved — cannot compare local tag target"
      fi
    else
      add_check "tag_local" "false" "refs/tags/${TAG} not found locally"
      add_check "tag_target" "unknown" "no local tag to dereference"
    fi

    # Remote tag: request both the ref and its peeled ^{} target so the
    # annotated tag's actual commit is verified, not just the ref name.
    tag_ls=$(git ls-remote "$REMOTE" "refs/tags/${TAG}" "refs/tags/${TAG}^{}" 2>/dev/null) && tag_rc=0 || tag_rc=$?
    if [ "$tag_rc" -ne 0 ]; then
      add_check "tag_remote" "unknown" "git ls-remote ${REMOTE} failed (network?)"
      add_check "tag_remote_target" "unknown" "git ls-remote ${REMOTE} failed (network?)"
    elif [ -z "$tag_ls" ]; then
      add_check "tag_remote" "false" "refs/tags/${TAG} absent on ${REMOTE}"
      add_check "tag_remote_target" "unknown" "no remote tag to dereference"
    else
      add_check "tag_remote" "true" "ls-remote: $(printf '%s' "$tag_ls" | head -1 | cut -c1-60)"
      peeled=$(printf '%s\n' "$tag_ls" | awk '$2 ~ /\^\{\}$/ {print $1}' | head -1)
      unpeeled=$(printf '%s\n' "$tag_ls" | awk '$2 !~ /\^\{\}$/ {print $1}' | head -1)
      remote_tag_commit="${peeled:-$unpeeled}"
      if [ -n "$merge_oid" ] && [ -n "$remote_tag_commit" ]; then
        if [ "$remote_tag_commit" = "$merge_oid" ]; then
          add_check "tag_remote_target" "true" "remote tag peels to the PR merge commit ${merge_oid}"
        else
          add_check "tag_remote_target" "false" "remote tag peels to ${remote_tag_commit}, expected merge ${merge_oid}"
        fi
      else
        add_check "tag_remote_target" "unknown" "merge oid unresolved — cannot compare remote tag target"
      fi
    fi

    if [ "$gh_ok" = true ]; then
      release_err=$(gh release view "$TAG" 2>&1 >/dev/null) && release_rc=0 || release_rc=$?
      if [ "$release_rc" -eq 0 ]; then
        add_check "release_exists" "true" "gh release view ${TAG} OK"
      elif printf '%s' "$release_err" | grep -qi "release not found"; then
        add_check "release_exists" "false" "gh release view: release not found"
      else
        add_check "release_exists" "unknown" "gh release view failed: $(printf '%s' "$release_err" | head -c 120)"
      fi
    else
      add_check "release_exists" "unknown" "gh unavailable"
    fi
  fi

  if [ -f ".specify/.ms-wip-publish" ]; then
    add_check "wip_marker_cleared" "false" ".specify/.ms-wip-publish still present"
  else
    add_check "wip_marker_cleared" "true" "no WIP publish marker"
  fi

  if [ -n "$LEDGER_FEATURE" ]; then
    ledger_row=""
    if [ -n "$base_ref" ] && [ -n "$remote_base_tip" ] && git cat-file -e "${remote_base_tip}^{commit}" 2>/dev/null \
       && ledger=$(git show "${remote_base_tip}:docs/prd/feature-map.progress.md" 2>/dev/null); then
      ledger_row=$(printf '%s' "$ledger" | grep -E "^\|[[:space:]]*0*${LEDGER_FEATURE}[^0-9]" | head -1)
      if [ -z "$ledger_row" ]; then
        add_check "ledger_shipped" "false" "no row for Feature ${LEDGER_FEATURE} in ${REMOTE}/${base_ref} progress ledger"
      else
        # Parse the Status COLUMN exactly (3rd data cell) — "shipped" anywhere
        # else in the row (a Feature name, a note) must not count.
        status_cell=$(printf '%s\n' "$ledger_row" | awk -F'|' '{gsub(/^[ ]+|[ ]+$/, "", $4); print $4}')
        if printf '%s' "$status_cell" | grep -qE '(^|[[:space:]])shipped$'; then
          add_check "ledger_shipped" "true" "status cell: '${status_cell}' (row: ${ledger_row})"
        else
          add_check "ledger_shipped" "false" "status cell: '${status_cell}' (row: ${ledger_row})"
        fi
      fi
    else
      add_check "ledger_shipped" "unknown" "progress ledger unreadable at ${REMOTE}/${base_ref:-<unresolved>} tip (read-only verifier does not fetch)"
    fi
  else
    add_check "ledger_shipped" "not_applicable" "no --ledger-feature given"
  fi

  cat <<JSON
{
  "tool": "specter-release",
  "mode": "verify-endstate",
  "repository": $( [ -n "$repository" ] && printf '"%s"' "$(json_escape "$repository")" || printf 'null' ),
  "remote": "$(json_escape "$REMOTE")",
  "pr": $( [ -n "$PR" ] && printf '"%s"' "$(json_escape "$PR")" || printf 'null' ),
  "tag": $( [ -n "$TAG" ] && printf '"%s"' "$(json_escape "$TAG")" || printf 'null' ),
  "base_ref": $( [ -n "$base_ref" ] && printf '"%s"' "$(json_escape "$base_ref")" || printf 'null' ),
  "merge_oid": $( [ -n "$merge_oid" ] && printf '"%s"' "$(json_escape "$merge_oid")" || printf 'null' ),
  "checks": {${CHECKS_JSON}},
  "notes": $(notes_json)
}
JSON
  exit 0
fi

# ---- classify-ci ----

if [ "$SUBCOMMAND" = "classify-ci" ]; then
  # Deterministic, fail-closed CI-failure classification (phase 4).
  # billing_infra is claimed ONLY on narrow structural signatures of a
  # billing/quota-dead runner (2026-07-21 observations: startup_failure
  # conclusion, zero jobs, or jobs whose steps never executed with no
  # failed-run logs). Everything else — mixed failures, unreadable logs,
  # external checks, parse gaps — is needs_human. Never widened by a
  # substring match on 'billing' somewhere in a log: a real test that
  # exercises billing code must not be classified away as infra.
  PR="${1:-}"
  overall="clean"
  FAILURES_JSON=""

  add_failure() {
    local name="$1" cls="$2" evidence="$3"
    [ -n "$FAILURES_JSON" ] && FAILURES_JSON+=","
    FAILURES_JSON+="{\"name\":\"$(json_escape "$name")\",\"classification\":\"${cls}\",\"evidence\":\"$(json_escape "$evidence")\"}"
  }

  finish_classify() {
    cat <<JSON
{
  "tool": "specter-release",
  "mode": "classify-ci",
  "pr": $( [ -n "$PR" ] && printf '"%s"' "$(json_escape "$PR")" || printf 'null' ),
  "overall": "${overall}",
  "failures": [${FAILURES_JSON}],
  "notes": $(notes_json)
}
JSON
    exit 0
  }

  if [ -z "$PR" ]; then
    overall="unknown"; note "missing required <pr-number> argument"; finish_classify
  fi
  if ! command -v gh >/dev/null 2>&1 || ! gh auth status >/dev/null 2>&1; then
    overall="unknown"; note "gh unavailable or unauthenticated — classification impossible"; finish_classify
  fi

  checks_out=$(gh pr checks "$PR" --json name,state,link \
    --jq '.[] | [.state, .name, (.link // "")] | join("\u001f")' 2>&1) && checks_rc=0 || checks_rc=$?
  if [ "$checks_rc" -ne 0 ] && [ -z "$checks_out" ]; then
    overall="unknown"; note "gh pr checks ${PR} failed with no output"; finish_classify
  fi
  if [ -z "$checks_out" ]; then
    note "no checks reported on PR ${PR}"; finish_classify
  fi

  pending=false
  billing=0
  human=0
  while IFS=$'\x1f' read -r state name link; do
    [ -n "$state" ] || continue
    case "$state" in
      SUCCESS|SKIPPED|NEUTRAL) continue ;;
      PENDING|QUEUED|IN_PROGRESS|EXPECTED|WAITING|REQUESTED) pending=true; continue ;;
    esac
    # Everything else is a failure candidate to classify.
    rid=""
    if [[ "$link" =~ /actions/runs/([0-9]+) ]]; then rid="${BASH_REMATCH[1]}"; fi
    if [ -z "$rid" ]; then
      human=$((human + 1))
      add_failure "$name" "needs_human" "state=${state}; no workflow-run link — external or unparseable check"
      continue
    fi
    conclusion=$(gh api "repos/{owner}/{repo}/actions/runs/${rid}" -q '.conclusion // ""' 2>/dev/null) || conclusion="__api_error__"
    if [ "$conclusion" = "__api_error__" ]; then
      human=$((human + 1))
      add_failure "$name" "needs_human" "state=${state}; run ${rid} metadata unavailable"
      continue
    fi
    if [ "$conclusion" = "startup_failure" ]; then
      billing=$((billing + 1))
      add_failure "$name" "billing_infra" "run ${rid} conclusion=startup_failure — workflow never started (billing/quota signature)"
      continue
    fi
    jobs_total=$(gh api "repos/{owner}/{repo}/actions/runs/${rid}/jobs" -q '.total_count // 0' 2>/dev/null) || jobs_total="?"
    max_steps=$(gh api "repos/{owner}/{repo}/actions/runs/${rid}/jobs" -q '[.jobs[].steps | length] | max // 0' 2>/dev/null) || max_steps="?"
    if [ "$jobs_total" = "0" ]; then
      billing=$((billing + 1))
      add_failure "$name" "billing_infra" "run ${rid} conclusion=${conclusion} with zero jobs — nothing was ever scheduled"
      continue
    fi
    if [ "$max_steps" = "0" ]; then
      failed_logs=$(gh run view "$rid" --log-failed 2>/dev/null | head -c 64 || true)
      if [ -z "$failed_logs" ]; then
        billing=$((billing + 1))
        add_failure "$name" "billing_infra" "run ${rid}: jobs created but no step ever executed and no failed-run logs exist"
        continue
      fi
    fi
    human=$((human + 1))
    add_failure "$name" "needs_human" "state=${state}, run ${rid} conclusion=${conclusion} — steps ran or logs exist; not the narrow billing signature"
  done <<< "$checks_out"

  if [ "$pending" = true ]; then
    overall="pending"
  elif [ "$human" -gt 0 ]; then
    overall="needs_human"
  elif [ "$billing" -gt 0 ]; then
    overall="billing_infra_only"
  fi
  finish_classify
fi

# ---- unknown subcommand ----

cat <<JSON
{
  "tool": "specter-release",
  "mode": "error",
  "notes": ["unknown subcommand '$(json_escape "${SUBCOMMAND:-<none>}")' (expected version|semver|verify-endstate|classify-ci)"]
}
JSON
exit 0

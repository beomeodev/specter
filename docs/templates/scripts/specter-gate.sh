#!/usr/bin/env bash
# Lean deterministic SPECTER gate.
# Mechanical only: required artifacts, exact verdict fields, current hashes,
# fixed reviewer paths, and worst-of reduction. No receipts and no state that
# shapes a verdict; the single append-only round log exists only to enforce
# the rerun budget and record owner overrides.

set -euo pipefail

FEATURE_MAP="docs/prd/feature-map.md"
GLOBAL_CHECKLIST="docs/prd/feature-map.checklist.md"
GLOBAL_OVERRIDE="docs/prd/feature-map.checklist.override.md"
CONSTITUTION=".specify/memory/constitution.md"
ROUND_LOG=".specify/gate-rounds.log"
ROUND_CAP=2

json_escape() {
  local value="${1:-}"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\n'/ }"
  printf '%s' "$value"
}

normalize_scope() {
  local raw="${1:-}"
  if [[ "$raw" =~ ^[0-9]+$ ]]; then
    printf '%03d' "$((10#$raw))"
  else
    printf '%s' "$raw"
  fi
}

field_count() {
  local file="$1" field="$2"
  grep -c "^[*][*]${field}[*][*]:" "$file" 2>/dev/null || true
}

field_value() {
  local file="$1" field="$2"
  grep -m1 "^[*][*]${field}[*][*]:" "$file" 2>/dev/null |
    sed -E "s/^[*][*]${field}[*][*]:[[:space:]]*//" || true
}

# Trailing consecutive FAIL judgment rounds for a station+scope. Only reduce
# calls that evaluated actual reviewer judgment are logged, so structural
# failures (missing report, stale hash, both lanes down) never burn budget.
fail_streak() {
  local station="$1" scope="$2"
  [ -f "$ROUND_LOG" ] || { printf '0'; return; }
  awk -F'|' -v st="$station" -v sc="$scope" '
    $2 == st && $3 == sc { if ($5 == "FAIL") streak++; else streak = 0 }
    END { print streak + 0 }
  ' "$ROUND_LOG"
}

append_round() {
  local station="$1" scope="$2" digest="$3" verdict="$4" override="$5" last
  if [ -z "$override" ] && [ -f "$ROUND_LOG" ]; then
    last="$(awk -F'|' -v st="$station" -v sc="$scope" \
      '$2 == st && $3 == sc { line = $4 "|" $5 } END { print line }' "$ROUND_LOG")"
    [ "$last" = "${digest}|${verdict}" ] && return 0
  fi
  mkdir -p "$(dirname "$ROUND_LOG")"
  printf '%s|%s|%s|%s|%s|%s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$station" "$scope" "$digest" "$verdict" \
    "$override" >>"$ROUND_LOG"
}

# The owner override binds to the exact content of the global checklist it
# accepts; any regeneration of the checklist invalidates it automatically.
global_override_valid() {
  [ -f "$GLOBAL_OVERRIDE" ] && [ -f "$GLOBAL_CHECKLIST" ] || return 1
  [ "$(field_value "$GLOBAL_OVERRIDE" "Mode")" = "global-override" ] || return 1
  [ -n "$(field_value "$GLOBAL_OVERRIDE" "Reason")" ] || return 1
  local recorded current
  recorded="$(field_value "$GLOBAL_OVERRIDE" "Global Checklist SHA256")"
  current="$(sha256sum "$GLOBAL_CHECKLIST" | awk '{print $1}')"
  [ -n "$recorded" ] && [ "$recorded" = "$current" ]
}

bundle_paths() {
  local station="$1" scope="$2" spec_dir
  case "$station" in
    pre-verify)
      find docs/prd -maxdepth 1 -type f -name '*.md' \
        ! -name 'feature-map.checklist.md' \
        ! -name 'feature-map.*-verify.md' \
        ! -name 'feature-map.*-checklist.md' \
        ! -name 'feature-map.progress.md' \
        ! -name 'opportunities.md' -print 2>/dev/null
      [ -f docs/prd/codex/checklist.md ] && printf '%s\n' docs/prd/codex/checklist.md
      ;;
    verify)
      printf '%s\n' "$FEATURE_MAP" "$GLOBAL_CHECKLIST"         "docs/prd/checklists/feature-${scope}.checklist.md"
      ;;
    analyze)
      spec_dir="$(find specs -maxdepth 1 -type d -name "${scope}-*" -print -quit 2>/dev/null || true)"
      [ -n "$spec_dir" ] && printf '%s\n' "$FEATURE_MAP"         "$spec_dir/spec.md" "$spec_dir/plan.md" "$spec_dir/tasks.md"
      ;;
    review)
      spec_dir="$(find specs -maxdepth 1 -type d -name "${scope}-*" -print -quit 2>/dev/null || true)"
      [ -n "$spec_dir" ] && printf '%s\n' "$spec_dir/spec.md" "$spec_dir/plan.md" "$spec_dir/tasks.md"
      git diff --name-only --diff-filter=ACMR HEAD 2>/dev/null |
        grep -Ev '^(docs/review/|docs/prd/|specs/|[.]specify/)' || true
      git ls-files --others --exclude-standard 2>/dev/null |
        grep -Ev '^(docs/review/|docs/prd/|specs/|[.]specify/)' || true
      ;;
    *)
      return 2
      ;;
  esac
}

bundle_hash() {
  local station="$1" scope="$2" paths path
  paths="$(bundle_paths "$station" "$scope" | awk 'NF' | sort -u)" || return 2
  [ -n "$paths" ] || return 1
  while IFS= read -r path; do
    [ -f "$path" ] || return 1
  done <<<"$paths"
  {
    while IFS= read -r path; do
      sha256sum "$path"
    done <<<"$paths"
    if [ "$station" = "review" ]; then
      git diff --binary HEAD -- . \
        ':(exclude)docs/review/**' ':(exclude)docs/prd/**' \
        ':(exclude)specs/**' ':(exclude).specify/**' 2>/dev/null || true
    fi
  } | sha256sum | awk '{print $1}'
}

report_paths() {
  local station="$1" scope="$2" spec_dir
  case "$station" in
    pre-verify)
      printf '%s\n' docs/prd/feature-map.codex-verify.md docs/prd/feature-map.antigravity-verify.md
      ;;
    verify)
      printf '%s\n' "docs/prd/checklists/feature-${scope}.codex-verify.md"         "docs/prd/checklists/feature-${scope}.antigravity-verify.md"
      ;;
    analyze)
      spec_dir="$(find specs -maxdepth 1 -type d -name "${scope}-*" -print -quit 2>/dev/null || true)"
      printf '%s\n' "${spec_dir}/analyze.codex.md" "${spec_dir}/analyze.antigravity.md"
      ;;
    review)
      printf '%s\n' "docs/review/${scope}.codex-review.md"         "docs/review/${scope}.antigravity-review.md"
      ;;
    *) return 2 ;;
  esac
}

emit_hash() {
  local station="$1" scope digest
  scope="$(normalize_scope "$2")"
  if digest="$(bundle_hash "$station" "$scope")"; then
    printf '{"contract":"lean-verification-v1","station":"%s","scope":"%s","input_sha256":"%s"}\n'       "$(json_escape "$station")" "$(json_escape "$scope")" "$digest"
  else
    printf '{"contract":"lean-verification-v1","station":"%s","scope":"%s","error":"missing input artifact"}\n'       "$(json_escape "$station")" "$(json_escape "$scope")"
    return 1
  fi
}

reduce_reports() {
  local station="$1" scope digest paths path result recorded availability
  local log_rounds="${3:-1}" override="${4:-}"
  local unavailable=0 worst=0 errors=()
  scope="$(normalize_scope "$2")"
  if [ "$log_rounds" -eq 1 ] && [ -z "$override" ] &&
     [ "$(fail_streak "$station" "$scope")" -ge "$ROUND_CAP" ]; then
    printf '{"contract":"lean-verification-v1","station":"%s","scope":"%s","verdict":"FAIL","reasons":["round cap reached: %s FAIL rounds recorded for this station and scope; record the owner authorization in the station dispute file and rerun with --override"]}\n' \
      "$(json_escape "$station")" "$(json_escape "$scope")" "$ROUND_CAP"
    return 1
  fi
  if ! digest="$(bundle_hash "$station" "$scope")"; then
    errors+=("missing input artifact")
    digest=""
  fi
  paths="$(report_paths "$station" "$scope")" || errors+=("unknown station")
  while IFS= read -r path; do
    [ -n "$path" ] || continue
    if [ ! -s "$path" ]; then
      errors+=("missing report: $path")
      continue
    fi
    if [ "$(field_count "$path" "Result")" -ne 1 ]; then
      errors+=("$path must contain exactly one Result")
      continue
    fi
    if [ "$(field_count "$path" "Mode")" -ne 1 ]; then
      errors+=("$path must contain exactly one Mode")
      continue
    fi
    if [ "$(field_count "$path" "Scope")" -ne 1 ] ||
       [ "$(field_value "$path" "Scope")" != "$scope" ]; then
      errors+=("$path Scope does not match $scope")
      continue
    fi
    result="$(field_value "$path" "Result")"
    case "$result" in
      PASS) ;;
      WARN) [ "$worst" -lt 1 ] && worst=1 ;;
      FAIL) worst=2 ;;
      *) errors+=("$path has invalid Result: ${result:-missing}"); continue ;;
    esac
    if [ "$(field_count "$path" "Input SHA256")" -ne 1 ]; then
      errors+=("$path must contain exactly one Input SHA256")
      continue
    fi
    recorded="$(field_value "$path" "Input SHA256")"
    [ -n "$digest" ] && [ "$recorded" = "$digest" ] ||
      errors+=("$path input hash is stale")
    availability="$(field_value "$path" "Availability")"
    [[ "$availability" == UNAVAILABLE* ]] && unavailable=$((unavailable + 1))
  done <<<"$paths"

  local verdict
  if [ "${#errors[@]}" -gt 0 ] || [ "$unavailable" -ge 2 ]; then
    verdict="FAIL"
  elif [ "$unavailable" -eq 1 ]; then
    [ "$worst" -ge 2 ] && verdict="FAIL" || verdict="WARN"
  else
    case "$worst" in 0) verdict="PASS" ;; 1) verdict="WARN" ;; *) verdict="FAIL" ;; esac
  fi

  local reasons="[]" i
  if [ "${#errors[@]}" -gt 0 ]; then
    reasons="["
    for i in "${!errors[@]}"; do
      [ "$i" -gt 0 ] && reasons+=","
      reasons+="\"$(json_escape "${errors[$i]}")\""
    done
    reasons+="]"
  elif [ "$unavailable" -ge 2 ]; then
    reasons='["both reviewers unavailable"]'
  elif [ "$unavailable" -eq 1 ]; then
    reasons='["single reviewer unavailable; verdict capped at WARN"]'
  fi
  if [ "$log_rounds" -eq 1 ] && [ "${#errors[@]}" -eq 0 ] && [ "$unavailable" -le 1 ]; then
    append_round "$station" "$scope" "$digest" "$verdict" "$override"
  fi
  local override_json=""
  [ -n "$override" ] && override_json=",\"override\":\"$(json_escape "$override")\""
  printf '{"contract":"lean-verification-v1","station":"%s","scope":"%s","input_sha256":"%s","verdict":"%s","reasons":%s%s}\n'     "$(json_escape "$station")" "$(json_escape "$scope")" "$digest" "$verdict" "$reasons" "$override_json"
  [ "$verdict" != "FAIL" ]
}

legacy_gate() {
  local raw="${1:-}" feature="" any_missing=false any_fail=false any_warn=false
  local reasons=() result recorded current count
  [ -z "$raw" ] || feature="$(normalize_scope "$raw")"

  for path in "$FEATURE_MAP" "$GLOBAL_CHECKLIST" "$CONSTITUTION"; do
    [ -f "$path" ] || { reasons+=("missing: $path"); any_missing=true; }
  done
  if [ -f "$GLOBAL_CHECKLIST" ]; then
    local override_ok=false
    global_override_valid && override_ok=true
    [ "$(field_count "$GLOBAL_CHECKLIST" "Mode")" -eq 1 ] &&
      [ "$(field_value "$GLOBAL_CHECKLIST" "Mode")" = "global" ] ||
      { reasons+=("global checklist Mode is invalid"); any_fail=true; }
    [ "$(field_count "$GLOBAL_CHECKLIST" "Result")" -eq 1 ] ||
      { reasons+=("global checklist must contain exactly one Result"); any_fail=true; }
    result="$(field_value "$GLOBAL_CHECKLIST" "Result")"
    case "$result" in
      PASS) ;;
      WARN) any_warn=true ;;
      *)
        if $override_ok; then
          reasons+=("global checklist Result overridden to WARN by owner record")
          any_warn=true
        else
          reasons+=("global checklist Result is invalid")
          any_fail=true
        fi
        ;;
    esac
    recorded="$(field_value "$GLOBAL_CHECKLIST" "Feature Map SHA256")"
    [ -f "$FEATURE_MAP" ] && current="$(sha256sum "$FEATURE_MAP" | awk '{print $1}')" || current=""
    if [ -z "$recorded" ] || [ "$recorded" != "$current" ]; then
      if $override_ok; then
        reasons+=("global checklist Feature Map SHA256 staleness overridden to WARN by owner record")
        any_warn=true
      else
        reasons+=("global checklist Feature Map SHA256 is stale")
        any_fail=true
      fi
    fi
  fi
  if [ -f "$CONSTITUTION" ]; then
    grep -q '^## IX[.] Project-Specific Constraints' "$CONSTITUTION" ||
      { reasons+=("constitution Section IX is not established"); any_fail=true; }
    grep -q 'This section is empty by default' "$CONSTITUTION" &&
      { reasons+=("constitution Section IX still has the template placeholder"); any_fail=true; }
  fi

  if [ -n "$feature" ]; then
    local checklist="docs/prd/checklists/feature-${feature}.checklist.md"
    [ -f "$checklist" ] || { reasons+=("missing: $checklist"); any_missing=true; }
    if [ -f "$checklist" ]; then
      [ "$(field_count "$checklist" "Mode")" -eq 1 ] &&
        [ "$(field_value "$checklist" "Mode")" = "per-feature" ] ||
        { reasons+=("feature checklist Mode is invalid"); any_fail=true; }
      local feature_field map_path recorded_map_sha current_map_sha
      feature_field="$(field_value "$checklist" "Feature")"
      [[ "$feature_field" == *"Feature $feature"* ]] ||
        { reasons+=("feature checklist does not match Feature $feature"); any_fail=true; }
      map_path="$(field_value "$checklist" "Feature Map")"
      map_path="${map_path%% *}"
      [ -n "$map_path" ] || map_path="$FEATURE_MAP"
      if [ -f "$map_path" ]; then
        recorded_map_sha="$(field_value "$checklist" "Feature Map SHA256")"
        current_map_sha="$(sha256sum "$map_path" | awk '{print $1}')"
        [ -n "$recorded_map_sha" ] && [ "$recorded_map_sha" = "$current_map_sha" ] ||
          { reasons+=("feature checklist Feature Map SHA256 is stale"); any_fail=true; }
      else
        reasons+=("missing: $map_path")
        any_missing=true
      fi
      result="$(field_value "$checklist" "Result")"
      case "$result" in PASS) ;; WARN) any_warn=true ;; *) reasons+=("feature checklist Result is invalid"); any_fail=true ;; esac
    fi
    local reduced
    if reduced="$(reduce_reports verify "$feature" 0 "")"; then
      [[ "$reduced" == *'"verdict":"WARN"'* ]] && any_warn=true
    else
      reasons+=("per-Feature verification reducer failed")
      any_fail=true
    fi
  fi

  local overall="PASS"
  $any_missing && overall="MISSING"
  $any_fail && overall="FAIL"
  ! $any_fail && ! $any_missing && $any_warn && overall="WARN"
  local reasons_json="[]" i
  if [ "${#reasons[@]}" -gt 0 ]; then
    reasons_json="["
    for i in "${!reasons[@]}"; do
      [ "$i" -gt 0 ] && reasons_json+=","
      reasons_json+="\"$(json_escape "${reasons[$i]}")\""
    done
    reasons_json+="]"
  fi
  printf '{"contract":"lean-verification-v1","feature":%s,"overall":"%s","reasons":%s}\n'     "$([ -n "$feature" ] && printf '"%s"' "$feature" || printf null)" "$overall" "$reasons_json"
  [ "$overall" = "PASS" ] || [ "$overall" = "WARN" ]
}

case "${1:-}" in
  version)
    printf '{"contract":"lean-verification-v1","rev":2,"subcommands":["hash","reduce","rounds"],"stateful":false,"round_log":"%s"}\n' "$ROUND_LOG"
    ;;
  hash)
    [ "$#" -eq 3 ] || { echo "usage: $0 hash <pre-verify|verify|analyze|review> <scope>" >&2; exit 2; }
    emit_hash "$2" "$3"
    ;;
  reduce)
    if [ "$#" -eq 3 ]; then
      reduce_reports "$2" "$3" 1 ""
    elif [ "$#" -eq 5 ] && [ "$4" = "--override" ] && [ -n "$5" ]; then
      reduce_reports "$2" "$3" 1 "$5"
    else
      echo "usage: $0 reduce <pre-verify|verify|analyze|review> <scope> [--override <owner reason>]" >&2
      exit 2
    fi
    ;;
  rounds)
    [ "$#" -eq 3 ] || { echo "usage: $0 rounds <pre-verify|verify|analyze|review> <scope>" >&2; exit 2; }
    scope="$(normalize_scope "$3")"
    streak="$(fail_streak "$2" "$scope")"
    blocked=false
    [ "$streak" -ge "$ROUND_CAP" ] && blocked=true
    printf '{"contract":"lean-verification-v1","station":"%s","scope":"%s","fail_rounds":%s,"cap":%s,"blocked":%s}\n' \
      "$(json_escape "$2")" "$(json_escape "$scope")" "$streak" "$ROUND_CAP" "$blocked"
    ;;
  *)
    [ "$#" -le 1 ] || { echo "usage: $0 [feature] | version | hash <station> <scope> | reduce <station> <scope> [--override <reason>] | rounds <station> <scope>" >&2; exit 2; }
    legacy_gate "${1:-}"
    ;;
esac

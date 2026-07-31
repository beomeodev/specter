#!/usr/bin/env bash
# Lean deterministic SPECTER gate.
# Mechanical only: required artifacts, exact verdict fields, current hashes,
# fixed reviewer paths, and worst-of reduction. No receipts or workflow state.

set -euo pipefail

FEATURE_MAP="docs/prd/feature-map.md"
GLOBAL_CHECKLIST="docs/prd/feature-map.checklist.md"
CONSTITUTION=".specify/memory/constitution.md"

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
  local unavailable=0 worst=0 errors=()
  scope="$(normalize_scope "$2")"
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
  printf '{"contract":"lean-verification-v1","station":"%s","scope":"%s","input_sha256":"%s","verdict":"%s","reasons":%s}\n'     "$(json_escape "$station")" "$(json_escape "$scope")" "$digest" "$verdict" "$reasons"
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
    [ "$(field_count "$GLOBAL_CHECKLIST" "Mode")" -eq 1 ] &&
      [ "$(field_value "$GLOBAL_CHECKLIST" "Mode")" = "global" ] ||
      { reasons+=("global checklist Mode is invalid"); any_fail=true; }
    [ "$(field_count "$GLOBAL_CHECKLIST" "Result")" -eq 1 ] ||
      { reasons+=("global checklist must contain exactly one Result"); any_fail=true; }
    result="$(field_value "$GLOBAL_CHECKLIST" "Result")"
    case "$result" in PASS) ;; WARN) any_warn=true ;; *) reasons+=("global checklist Result is invalid"); any_fail=true ;; esac
    recorded="$(field_value "$GLOBAL_CHECKLIST" "Feature Map SHA256")"
    [ -f "$FEATURE_MAP" ] && current="$(sha256sum "$FEATURE_MAP" | awk '{print $1}')" || current=""
    [ -n "$recorded" ] && [ "$recorded" = "$current" ] ||
      { reasons+=("global checklist Feature Map SHA256 is stale"); any_fail=true; }
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
    if reduced="$(reduce_reports verify "$feature")"; then
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
    printf '{"contract":"lean-verification-v1","subcommands":["hash","reduce"],"stateful":false}\n'
    ;;
  hash)
    [ "$#" -eq 3 ] || { echo "usage: $0 hash <pre-verify|verify|analyze|review> <scope>" >&2; exit 2; }
    emit_hash "$2" "$3"
    ;;
  reduce)
    [ "$#" -eq 3 ] || { echo "usage: $0 reduce <pre-verify|verify|analyze|review> <scope>" >&2; exit 2; }
    reduce_reports "$2" "$3"
    ;;
  *)
    [ "$#" -le 1 ] || { echo "usage: $0 [feature] | version | hash <station> <scope> | reduce <station> <scope>" >&2; exit 2; }
    legacy_gate "${1:-}"
    ;;
esac

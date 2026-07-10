#!/usr/bin/env bash
# Deterministic SPECTER gate checker (WI-11).
#
# Owns only mechanical facts: verdict lines, SHA256 equality, file existence.
# Content judgment (PRD fidelity, boundary discipline, severity) stays with
# the model in /ms.checklist, /ms.verify, /ms.specify, /ms.constitution.
#
# Usage:
#   specter-gate.sh          # global gate only
#   specter-gate.sh 006      # global gate + per-Feature gate for Feature 006
#
# Prints one JSON object to stdout: { checks, overall, reasons[] }.
# overall is one of: PASS | WARN | FAIL | MISSING
#   MISSING = a required artifact file does not exist yet (gate never ran)
#   FAIL    = an artifact exists but its content fails the gate (Result FAIL,
#             stale SHA256, wrong Mode/Feature, unestablished Section IX)
#   WARN    = every check passes but at least one Result is WARN
#   PASS    = every check passes and every Result is PASS

set -euo pipefail

FEATURE_RAW="${1:-}"
FEATURE=""
if [ -n "$FEATURE_RAW" ]; then
  if [[ "$FEATURE_RAW" =~ ^[0-9]+$ ]]; then
    # 10# forces decimal: a leading zero ("069") must not be read as octal.
    FEATURE=$(printf '%03d' "$((10#$FEATURE_RAW))")
  else
    FEATURE="$FEATURE_RAW"
  fi
fi

GLOBAL_CHECKLIST="docs/prd/feature-map.checklist.md"
FEATURE_MAP="docs/prd/feature-map.md"
CONSTITUTION=".specify/memory/constitution.md"

REASONS=()
add_reason() { REASONS+=("$1"); }

json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/ }"
  printf '%s' "$s"
}

extract_field() {
  # extract_field <file> <field-name>  ->  value after "**field-name**:"
  # `|| true`: tolerates a missing field under `set -euo pipefail` so the
  # caller sees an empty string (treated as FAIL downstream) instead of the
  # whole script aborting with no JSON output.
  local file="$1" field="$2"
  grep -m1 "^\*\*${field}\*\*:" "$file" 2>/dev/null | sed -E "s/^\*\*${field}\*\*:[[:space:]]*//" || true
}

any_missing=false
any_fail=false
any_warn=false

# ---- Global checks ----

global_checklist_exists=false
global_mode_ok=false
global_result=""
global_result_ok=false
global_sha_ok=false

if [ -f "$GLOBAL_CHECKLIST" ]; then
  global_checklist_exists=true
else
  add_reason "missing: $GLOBAL_CHECKLIST"
  any_missing=true
fi

if $global_checklist_exists; then
  if grep -q '^\*\*Mode\*\*: global' "$GLOBAL_CHECKLIST"; then
    global_mode_ok=true
  else
    add_reason "global checklist Mode is not 'global'"
    any_fail=true
  fi

  global_result=$(extract_field "$GLOBAL_CHECKLIST" "Result")
  if [ "$global_result" = "PASS" ] || [ "$global_result" = "WARN" ]; then
    global_result_ok=true
    [ "$global_result" = "WARN" ] && any_warn=true
  else
    add_reason "global checklist Result is '${global_result:-missing}', expected PASS or WARN"
    any_fail=true
  fi

  if [ -f "$FEATURE_MAP" ]; then
    recorded_sha=$(extract_field "$GLOBAL_CHECKLIST" "Feature Map SHA256")
    current_sha=$(sha256sum "$FEATURE_MAP" | awk '{print $1}')
    if [ -n "$recorded_sha" ] && [ "$recorded_sha" = "$current_sha" ]; then
      global_sha_ok=true
    else
      add_reason "global checklist Feature Map SHA256 stale (recorded=${recorded_sha:-none}, current=${current_sha})"
      any_fail=true
    fi
  else
    add_reason "missing: $FEATURE_MAP"
    any_missing=true
  fi
fi

# ---- Constitution Section IX ----

constitution_section_ix_established=false

if [ -f "$CONSTITUTION" ]; then
  if grep -q '## IX\. Project-Specific Constraints' "$CONSTITUTION"; then
    if grep -q 'This section is empty by default' "$CONSTITUTION"; then
      add_reason "constitution Section IX not established (template placeholder)"
      any_fail=true
    else
      constitution_section_ix_established=true
    fi
  else
    add_reason "constitution Section IX heading not found"
    any_fail=true
  fi
else
  add_reason "missing: $CONSTITUTION"
  any_missing=true
fi

# ---- Per-Feature checks (only if a Feature was requested) ----

feature_checklist_exists=false
feature_checklist_mode_ok=false
feature_checklist_feature_match=false
feature_checklist_result=""
feature_checklist_result_ok=false
feature_checklist_sha_ok=false
codex_verify_exists=false
codex_verify_result=""
codex_verify_result_ok=false
antigravity_verify_exists=false
antigravity_verify_result=""
antigravity_verify_result_ok=false

if [ -n "$FEATURE" ]; then
  FEATURE_CHECKLIST="docs/prd/checklists/feature-${FEATURE}.checklist.md"
  CODEX_VERIFY="docs/prd/checklists/feature-${FEATURE}.codex-verify.md"
  ANTIGRAVITY_VERIFY="docs/prd/checklists/feature-${FEATURE}.antigravity-verify.md"

  if [ -f "$FEATURE_CHECKLIST" ]; then
    feature_checklist_exists=true
  else
    add_reason "missing: $FEATURE_CHECKLIST"
    any_missing=true
  fi

  if $feature_checklist_exists; then
    if grep -q '^\*\*Mode\*\*: per-feature' "$FEATURE_CHECKLIST"; then
      feature_checklist_mode_ok=true
    else
      add_reason "feature checklist Mode is not 'per-feature'"
      any_fail=true
    fi

    feature_field=$(extract_field "$FEATURE_CHECKLIST" "Feature")
    if [[ "$feature_field" == *"Feature ${FEATURE}"* ]] || [[ "$feature_field" == *"Feature ${FEATURE_RAW}"* ]]; then
      feature_checklist_feature_match=true
    else
      add_reason "feature checklist Feature field '${feature_field:-missing}' does not match requested Feature ${FEATURE}"
      any_fail=true
    fi

    feature_checklist_result=$(extract_field "$FEATURE_CHECKLIST" "Result")
    if [ "$feature_checklist_result" = "PASS" ] || [ "$feature_checklist_result" = "WARN" ]; then
      feature_checklist_result_ok=true
      [ "$feature_checklist_result" = "WARN" ] && any_warn=true
    else
      add_reason "feature checklist Result is '${feature_checklist_result:-missing}', expected PASS or WARN"
      any_fail=true
    fi

    # Split-slate support: a checklist may pin its own map file via the
    # "**Feature Map**:" field (e.g. feature-map_072_*.md with the master
    # frozen); its recorded SHA256 must be checked against that file, not
    # against the master map.
    map_field=$(extract_field "$FEATURE_CHECKLIST" "Feature Map")
    feature_map_path="$FEATURE_MAP"
    [ -n "$map_field" ] && feature_map_path="${map_field%% *}"
    if [ -f "$feature_map_path" ]; then
      recorded_sha=$(extract_field "$FEATURE_CHECKLIST" "Feature Map SHA256")
      current_sha=$(sha256sum "$feature_map_path" | awk '{print $1}')
      if [ -n "$recorded_sha" ] && [ "$recorded_sha" = "$current_sha" ]; then
        feature_checklist_sha_ok=true
      else
        add_reason "feature checklist Feature Map SHA256 stale (recorded=${recorded_sha:-none}, current=${current_sha})"
        any_fail=true
      fi
    elif [ "$feature_map_path" != "$FEATURE_MAP" ]; then
      add_reason "missing: $feature_map_path"
      any_missing=true
    fi
  fi

  if [ -f "$CODEX_VERIFY" ]; then
    codex_verify_exists=true
    codex_verify_result=$(extract_field "$CODEX_VERIFY" "Result")
    if [ "$codex_verify_result" = "PASS" ] || [ "$codex_verify_result" = "WARN" ]; then
      codex_verify_result_ok=true
      [ "$codex_verify_result" = "WARN" ] && any_warn=true
    else
      add_reason "codex-verify Result is '${codex_verify_result:-missing}', expected PASS or WARN"
      any_fail=true
    fi
  else
    add_reason "missing: $CODEX_VERIFY"
    any_missing=true
  fi

  if [ -f "$ANTIGRAVITY_VERIFY" ]; then
    antigravity_verify_exists=true
    antigravity_verify_result=$(extract_field "$ANTIGRAVITY_VERIFY" "Result")
    if [ "$antigravity_verify_result" = "PASS" ] || [ "$antigravity_verify_result" = "WARN" ]; then
      antigravity_verify_result_ok=true
      [ "$antigravity_verify_result" = "WARN" ] && any_warn=true
    else
      add_reason "antigravity-verify Result is '${antigravity_verify_result:-missing}', expected PASS or WARN"
      any_fail=true
    fi
  else
    add_reason "missing: $ANTIGRAVITY_VERIFY"
    any_missing=true
  fi
fi

# ---- Overall verdict ----

overall="PASS"
if $any_missing; then
  overall="MISSING"
elif $any_fail; then
  overall="FAIL"
elif $any_warn; then
  overall="WARN"
fi

# ---- Emit JSON ----

reasons_json="[]"
if [ "${#REASONS[@]}" -gt 0 ]; then
  reasons_json="["
  for i in "${!REASONS[@]}"; do
    [ "$i" -gt 0 ] && reasons_json+=","
    reasons_json+="\"$(json_escape "${REASONS[$i]}")\""
  done
  reasons_json+="]"
fi

feature_json="null"
[ -n "$FEATURE" ] && feature_json="\"$(json_escape "$FEATURE")\""

cat <<JSON
{
  "feature": ${feature_json},
  "checks": {
    "global_checklist_exists": ${global_checklist_exists},
    "global_mode_ok": ${global_mode_ok},
    "global_result": "$(json_escape "$global_result")",
    "global_result_ok": ${global_result_ok},
    "global_sha_ok": ${global_sha_ok},
    "constitution_section_ix_established": ${constitution_section_ix_established},
    "feature_checklist_exists": ${feature_checklist_exists},
    "feature_checklist_mode_ok": ${feature_checklist_mode_ok},
    "feature_checklist_feature_match": ${feature_checklist_feature_match},
    "feature_checklist_result": "$(json_escape "$feature_checklist_result")",
    "feature_checklist_result_ok": ${feature_checklist_result_ok},
    "feature_checklist_sha_ok": ${feature_checklist_sha_ok},
    "codex_verify_exists": ${codex_verify_exists},
    "codex_verify_result_ok": ${codex_verify_result_ok},
    "antigravity_verify_exists": ${antigravity_verify_exists},
    "antigravity_verify_result_ok": ${antigravity_verify_result_ok}
  },
  "overall": "${overall}",
  "reasons": ${reasons_json}
}
JSON

#!/usr/bin/env bash
# Deterministic SPECTER gate checker (WI-11).
#
# Owns only mechanical facts: verdict lines, SHA256 equality, file existence.
# Content judgment (PRD fidelity, boundary discipline, severity) stays with
# the model in /ms.checklist, /ms.pre-verify, /ms.specify, /ms.constitution.
#
# Usage:
#   specter-gate.sh          # global gate only (legacy invocation, unchanged)
#   specter-gate.sh 006      # global gate + per-Feature gate for Feature 006
#   specter-gate.sh version  # capability probe (partially-synced projects fail clearly)
#   specter-gate.sh structural [NNN]
#                            # Layer-1 deterministic structure checks:
#                            # global = commitment-index ownership, DAG cycle,
#                            # required headings, CI-passes-green, placeholders;
#                            # NNN adds checklist placeholder + C-ID cross-refs
#   specter-gate.sh aggregate <pre-verify|verify|analyze|review|expand> [arg]
#                            [--ledger] [--round N]
#                            [--expect-protocol continuity-v1] [--require-coverage]
#                            # Layer-3 verdict aggregation over the STATION-FIXED
#                            # report set (the caller never picks input files).
#                            # --ledger also appends the .specify/specter-run.jsonl
#                            # line mechanically (verbatim caught quotes + cap) and
#                            # archives each report as an immutable round copy
#                            # (<report>.round-NN.md — continuity-v1);
#                            # --round N records the §4 convergence round;
#                            # --expect-protocol enforces the continuity-v1 report
#                            # schema (Protocol field, lineage columns on re-rounds);
#                            # --require-coverage demands the declared-coverage
#                            # closure section (## Coverage) in every agent report.
#   specter-gate.sh manifest <pre-verify|verify|analyze> [arg]
#                            # Emit the station's gate-generated expected coverage
#                            # inventory (declared coverage closure, C5'): the
#                            # reviewer must return one ## Coverage row per key.
#   specter-gate.sh continuity <pre-verify|verify|analyze|review> [arg] --round N [--diff <path>]
#                            # Mechanically build the re-round continuity packet
#                            # from the immutable round archives (prior blocking
#                            # findings + Required Fix verbatim — never a PASS
#                            # whitelist). The host passes the packet PATH to the
#                            # reviewer prompt; it never authors packet content.
#
# Every mode prints one JSON object to stdout, even on malformed input.
# Legacy overall is one of: PASS | WARN | FAIL | MISSING
#   MISSING = a required artifact file does not exist yet (gate never ran)
#   FAIL    = an artifact exists but its content fails the gate (Result FAIL,
#             stale SHA256, wrong Mode/Feature, unestablished Section IX)
#   WARN    = every check passes but at least one Result is WARN
#   PASS    = every check passes and every Result is PASS
# structural/aggregate emit "verdict": PASS | WARN | FAIL (no MISSING — a
# missing input at those layers is a FAIL by the three-layer contract,
# specter-agent-protocols §7).

set -euo pipefail

GATE_VERSION="3.1.0"
GATE_CONTRACT="three-layer-v2-audit-tier"
AUDIT_TIER_CONTRACT="audit-tier-v1"
CONTINUITY_CONTRACT="continuity-v1"

SUBCOMMAND="gate"
case "${1:-}" in
  version|structural|aggregate|manifest|continuity) SUBCOMMAND="$1"; shift ;;
esac

FEATURE_RAW=""
if [ "$SUBCOMMAND" = "gate" ] || [ "$SUBCOMMAND" = "structural" ]; then
  FEATURE_RAW="${1:-}"
fi
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

AUDIT_CLASSIFIER=""
AUDIT_POLICY=""
AUDIT_CAPABILITY="legacy-unavailable"
PYTHON_BIN=""

resolve_audit_runtime() {
  local source_classifier="scripts/specter/classify_audit_tier.py"
  local source_policy="docs/templates/audit-tier-policy.json"
  local runtime_classifier=".specify/scripts/python/classify_audit_tier.py"
  local runtime_policy=".specify/policies/audit-tier-policy.json"

  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  fi

  if [ -f "$source_classifier" ] && [ -f "$source_policy" ]; then
    AUDIT_CLASSIFIER="$source_classifier"
    AUDIT_POLICY="$source_policy"
    AUDIT_CAPABILITY="available"
  elif [ -f "$runtime_classifier" ] && [ -f "$runtime_policy" ]; then
    AUDIT_CLASSIFIER="$runtime_classifier"
    AUDIT_POLICY="$runtime_policy"
    AUDIT_CAPABILITY="available"
  elif [ -f "$source_classifier" ] || [ -f "$source_policy" ] ||
       [ -f "$runtime_classifier" ] || [ -f "$runtime_policy" ]; then
    AUDIT_CAPABILITY="partial-sync"
  fi
  if [ "$AUDIT_CAPABILITY" = "available" ] && [ -z "$PYTHON_BIN" ]; then
    AUDIT_CAPABILITY="python-unavailable"
  fi
}

json_value() {
  local json="$1" key="$2"
  "$PYTHON_BIN" -c 'import json,sys; value=json.load(sys.stdin).get(sys.argv[1]); print("" if value is None else str(value).lower() if isinstance(value,bool) else value)' "$key" <<<"$json"
}

resolve_audit_runtime

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
  #
  # BOTH sides are trimmed. Trailing whitespace is invisible in a rendered
  # report but was enough to fail the exact-match Mode/Result comparisons — an
  # agent that ends the line with the Markdown hard-break (two spaces) had its
  # otherwise valid report rejected as "wrong station". Surrounding whitespace
  # is never semantic in these header fields.
  local file="$1" field="$2"
  grep -m1 "^\*\*${field}\*\*:" "$file" 2>/dev/null \
    | sed -E "s/^\*\*${field}\*\*:[[:space:]]*//; s/[[:space:]]+$//" || true
}

reasons_to_json() {
  # Serialize the REASONS array as a JSON string array.
  local out="[]" i
  if [ "${#REASONS[@]}" -gt 0 ]; then
    out="["
    for i in "${!REASONS[@]}"; do
      [ "$i" -gt 0 ] && out+=","
      out+="\"$(json_escape "${REASONS[$i]}")\""
    done
    out+="]"
  fi
  printf '%s' "$out"
}

rank_of() {
  case "$1" in
    PASS) printf 0 ;;
    WARN) printf 1 ;;
    *)    printf 2 ;;
  esac
}

worse() {
  # worse <a> <b> -> the more severe of two PASS/WARN/FAIL values
  if [ "$(rank_of "$1")" -ge "$(rank_of "$2")" ]; then printf '%s' "$1"; else printf '%s' "$2"; fi
}

pad_feature() {
  if [[ "$1" =~ ^[0-9]+$ ]]; then printf '%03d' "$((10#$1))"; else printf '%s' "$1"; fi
}

resolve_baseline() {
  local b="docs/prd/featuremap-checklist.md"
  [ -f "$b" ] || b="docs/prd/codex/checklist.md"
  printf '%s' "$b"
}

# resolve_station <station> <arg>
# Shared by aggregate/continuity/manifest so every mode sees the same
# STATION-FIXED input set (specter-agent-protocols §7 — the caller never picks
# input files). Sets RS_* globals; RS_ERROR is non-empty on invalid input.
resolve_station() {
  local station="$1" arg="$2"
  RS_INPUTS=(); RS_MODES=(); RS_SHA_FIELD=""; RS_SHA_TARGET=""
  RS_CYCLE=""; RS_STEP=""; RS_FEATURE=""; RS_FEATURE_CHECK=false; RS_ERROR=""
  # Legacy alias (pre-2026-07-19 rename).
  [ "$station" = "agent-verify" ] && station="verify"
  case "$station" in
    pre-verify)
      RS_INPUTS=("docs/prd/feature-map.codex-verify.md" "docs/prd/feature-map.antigravity-checklist.md")
      RS_MODES=("codex-global-verify" "antigravity-global-verify")
      RS_SHA_FIELD="Feature Map SHA256"; RS_SHA_TARGET="docs/prd/feature-map.md"
      RS_CYCLE="pre"; RS_STEP="pre-verify"
      ;;
    verify)
      if ! [[ "$arg" =~ ^[0-9]+$ ]]; then
        RS_ERROR="station verify requires a numeric Feature number (got '${arg:-<none>}')"
      else
        RS_FEATURE=$(pad_feature "$arg")
        RS_INPUTS=("docs/prd/checklists/feature-${RS_FEATURE}.codex-verify.md" "docs/prd/checklists/feature-${RS_FEATURE}.antigravity-verify.md")
        RS_MODES=("codex-per-feature-verify" "antigravity-per-feature-verify")
        RS_SHA_FIELD="Checklist SHA256"; RS_SHA_TARGET="docs/prd/checklists/feature-${RS_FEATURE}.checklist.md"
        RS_FEATURE_CHECK=true
        RS_CYCLE="feature"; RS_STEP="verify"
      fi
      ;;
    analyze)
      # Spec dirs follow the NNN-name convention; requiring the numeric prefix
      # both blocks traversal fragments ("specs/..") and guarantees the
      # Feature-identity check is always enabled.
      if ! [[ "$arg" =~ ^specs/[0-9]{3}-[A-Za-z0-9._-]+/?$ ]]; then
        RS_ERROR="station analyze requires a spec directory of the form specs/NNN-name (got '${arg:-<none>}')"
      else
        RS_INPUTS=("${arg%/}/analyze.codex.md" "${arg%/}/analyze.antigravity.md")
        RS_MODES=("agent-document-consistency" "agent-document-consistency")
        RS_SHA_FIELD="Tasks SHA256"; RS_SHA_TARGET="${arg%/}/tasks.md"
        local base; base=$(basename "${arg%/}")
        [[ "$base" =~ ^0*([0-9]+) ]] && RS_FEATURE=$(pad_feature "${BASH_REMATCH[1]}") && RS_FEATURE_CHECK=true
        RS_CYCLE="feature"; RS_STEP="analyze"
      fi
      ;;
    review)
      if ! [[ "$arg" =~ ^[0-9]{3}-[A-Za-z0-9._-]+$ ]]; then
        RS_ERROR="station review requires a spec id of the form NNN-name (got '${arg:-<none>}')"
      else
        RS_INPUTS=("docs/review/${arg}.codex-review.md" "docs/review/${arg}.antigravity-review.md")
        RS_MODES=("codex-adversarial-code-review" "antigravity-adversarial-code-review")
        # Agent reports bind to Feature identity; the mandatory audit-tier
        # receipt separately binds the tracked + untracked diff hash.
        [[ "$arg" =~ ^0*([0-9]+) ]] && RS_FEATURE=$(pad_feature "${BASH_REMATCH[1]}") && RS_FEATURE_CHECK=true
        RS_CYCLE="feature"; RS_STEP="review"
      fi
      ;;
    expand)
      if ! [[ "$arg" =~ ^[0-9]+$ ]]; then
        RS_ERROR="station expand requires a numeric amendment number (got '${arg:-<none>}')"
      else
        RS_INPUTS=("docs/prd/feature-map.delta-${arg}.antigravity-verify.md")
        RS_MODES=("antigravity-delta-verify")
        RS_SHA_FIELD="Feature Map SHA256"; RS_SHA_TARGET="docs/prd/feature-map.md"
        RS_CYCLE="pre"; RS_STEP="expand"
      fi
      ;;
    *)
      RS_ERROR="unknown station '${station:-<none>}' (expected pre-verify|verify|analyze|review|expand)"
      ;;
  esac
}

# ---- declared-coverage-closure key extraction (C5', continuity-v1) ----
# The expected inventory is generated from the audited artifacts, never
# asserted by the reviewer. It is a DECLARED finite universe: set equality
# proves every declared key received a disposition, not semantic
# exhaustiveness (that honesty limit is stated in specter-agent-protocols §6).

map_commitment_keys() {
  # map_commitment_keys <map> <feature-or-empty> -> "map:C-NNN" per index row
  # (rows without a C-token, e.g. legacy maps, contribute no key).
  local map="$1" feature="$2"
  [ -f "$map" ] || return 0
  awk -v want="$feature" '
    /^## PRD Commitment Index/ { f = 1; next }
    /^## / { f = 0 }
    f && /^\|/ {
      if ($0 ~ /^\|[-: |]+$/) next
      n = split($0, c, "|")
      if ($0 ~ /Owning Feature/ && $0 !~ /C-[0-9]+/) {
        for (i = 1; i <= n; i++) if (c[i] ~ /Owning Feature/) ocol = i
        next
      }
      if (!match($0, /C-[0-9]+/)) next
      key = substr($0, RSTART, RLENGTH)
      if (want != "") {
        if (!ocol) ocol = 6
        owner = c[ocol]; gsub(/^[ ]+|[ ]+$/, "", owner)
        if (owner !~ ("^Feature 0*" (want + 0) "$")) next
      }
      print "map:" key
    }' "$map"
}

obligation_keys() {
  # obligation_keys <map> <feature-or-empty> -> "obligation:D-NNN" (and E-NNN
  # once a Slice Contracts table exists) per obligations row.
  local map="$1" feature="$2"
  [ -f "$map" ] || return 0
  awk -v want="$feature" '
    /^## (Implementation Obligations|Slice Contracts)/ { f = 1; ocol = 0; next }
    /^## / { f = 0 }
    f && /^\|/ {
      if ($0 ~ /^\|[-: |]+$/) next
      n = split($0, c, "|")
      if ($0 ~ /(D|E)-ID/) {
        for (i = 1; i <= n; i++) if (c[i] ~ /Owning Feature|To Feature/) ocol = i
        next
      }
      id = c[2]; gsub(/^[ ]+|[ ]+$/, "", id)
      if (id !~ /^[DE]-[0-9]+$/) next
      if (want != "") {
        owner = ""
        if (ocol) { owner = c[ocol]; gsub(/^[ ]+|[ ]+$/, "", owner) }
        if (owner !~ ("Feature 0*" (want + 0) "([^0-9]|$)")) next
      }
      print "obligation:" id
    }' "$map"
}

manifest_keys() {
  # manifest_keys <station> <padded-feature-or-empty> <arg>
  # Prints the station's expected coverage keys, one per line, sorted, unique.
  local station="$1" feature="$2" arg="$3"
  local map="docs/prd/feature-map.md"
  local baseline; baseline=$(resolve_baseline)
  {
    case "$station" in
      pre-verify)
        map_commitment_keys "$map" ""
        if [ -f "$baseline" ]; then
          grep -oE 'C-?[0-9]+' "$baseline" | tr -d '-' | sed 's/^/baseline:/' || true
        fi
        obligation_keys "$map" ""
        if [ -f "$map" ]; then
          sed -nE 's/^## Feature ([0-9]+):.*$/feature:\1/p' "$map" || true
        fi
        ;;
      verify)
        map_commitment_keys "$map" "$feature"
        obligation_keys "$map" "$feature"
        [ -n "$feature" ] && printf 'feature:%s\n' "$feature"
        ;;
      analyze)
        local spec="${arg%/}/spec.md"
        if [ -f "$spec" ]; then
          grep -oE 'FR-[A-Z]*-?[0-9]+' "$spec" | sed 's/^/fr:/' || true
        fi
        map_commitment_keys "$map" "$feature"
        obligation_keys "$map" "$feature"
        ;;
    esac
  } | sort -u
}

# ---- version subcommand ----

if [ "$SUBCOMMAND" = "version" ]; then
  cat <<JSON
{
  "version": "${GATE_VERSION}",
  "contract": "${GATE_CONTRACT}",
  "audit_tier_contract": "${AUDIT_TIER_CONTRACT}",
  "audit_tier_capability": "${AUDIT_CAPABILITY}",
  "continuity_contract": "${CONTINUITY_CONTRACT}",
  "subcommands": ["gate", "version", "structural", "aggregate", "manifest", "continuity"]
}
JSON
  exit 0
fi

# ---- structural subcommand (Layer 1: deterministic structure only) ----
# Judges shape, never semantics: whether the PRD was actually understood is
# Layer 2's job (specter-agent-protocols §7).

if [ "$SUBCOMMAND" = "structural" ]; then
  MAP="docs/prd/feature-map.md"
  PROGRESS="docs/prd/feature-map.progress.md"
  # Baseline checklist: new path first, legacy Codex-era path as fallback so
  # established consumer projects keep passing their C-ID cross-references.
  CODEX_PRD_CHECKLIST="docs/prd/featuremap-checklist.md"
  [ -f "$CODEX_PRD_CHECKLIST" ] || CODEX_PRD_CHECKLIST="docs/prd/codex/checklist.md"

  verdict="PASS"
  index_ok=true
  features_ok=true
  dag_ok=true
  placeholders_ok=true
  checklist_refs_ok=true
  audit_signals_ok=true
  obligations_ok=true

  note() {
    # note <F|W> <reason>
    add_reason "$2"
    if [ "$1" = "F" ]; then verdict=$(worse "$verdict" "FAIL"); else verdict=$(worse "$verdict" "WARN"); fi
  }

  if [ ! -f "$MAP" ]; then
    note F "missing: $MAP"
    index_ok=false; features_ok=false; dag_ok=false
  else
    # Commitment Index: every data row owned by exactly one Feature.
    while IFS= read -r line; do
      kind="${line%%|*}"; rest="${line#*|}"
      case "$rest" in
        index\|*) index_ok=false ;;
      esac
      note "$kind" "${rest#*|} [${rest%%|*}]"
    done < <(awk '
      BEGIN { found = 0; rows = 0 }
      /^## PRD Commitment Index/ { found = 1; inidx = 1; next }
      /^## / { inidx = 0 }
      inidx && /^\|/ {
        if ($0 ~ /^\|[-: |]+$/) next
        n = split($0, c, "|")
        if (c[2] ~ /Source PRD/ || $0 ~ /Owning Feature/) {
          # Header row: locate the owner column by name instead of assuming
          # position 6 (2026-07-22 doit-n-live false positive on a map with a
          # legitimate extra leading column).
          for (i = 1; i <= n; i++) {
            if (c[i] ~ /Owning Feature/) ocol = i
            if (c[i] ~ /Commitment Type/) tcol = i
          }
          next
        }
        rows++
        if (!ocol) ocol = 6
        if (!tcol) tcol = 4
        owner = c[ocol]
        gsub(/^[ ]+|[ ]+$/, "", owner)
        ctype = c[tcol]
        gsub(/^[ ]+|[ ]+$/, "", ctype)
        if (ctype ~ /Exclusion/) {
          # Exclusion rows legitimately have no owning Feature (2026-07-23
          # spade-ace false positive); they must carry an explicit em-dash
          # marker instead of an empty owner cell.
          if (owner !~ /^—/)
            print "F|index|exclusion row owner must be an explicit em-dash marker: " $0
        } else if (owner !~ /^Feature [0-9]+$/) {
          if (owner !~ /Feature [0-9]+/)
            print "F|index|commitment row has no owning Feature: " $0
          else
            print "F|index|commitment row owner is not exactly one Feature: " $0
        }
      }
      END {
        if (!found) print "F|index|PRD Commitment Index section missing"
        else if (rows == 0) print "F|index|PRD Commitment Index has no commitment rows"
      }' "$MAP")

    # Feature sections: required headings, CI-passes-green, out-of-scope
    # destinations, unresolved placeholders. When a Feature was requested,
    # scope the verdict to that Feature's section only.
    while IFS= read -r line; do
      kind="${line%%|*}"; rest="${line#*|}"; sec="${rest%%|*}"; msg="${rest#*|}"
      if [ -n "$FEATURE" ] && [ "$sec" != "Feature ${FEATURE}" ]; then
        continue
      fi
      case "$msg" in
        *placeholder*) placeholders_ok=false ;;
        *) features_ok=false ;;
      esac
      note "$kind" "$msg [$sec]"
    done < <(awk '
      function flush() {
        if (!insec) return
        n = split("### Source PRDs,### PRD references,### In scope,### Explicitly out of scope,### Key decisions,### Done criteria", req, ",")
        for (i = 1; i <= n; i++) if (!(req[i] in seen)) print "F|" sec "|missing heading: " req[i]
        if ("### Done criteria" in seen) {
          if (lastdc == "") print "F|" sec "|done criteria section has no criteria"
          else if (lastdc !~ /CI passes green/) print "F|" sec "|last done criterion is not CI passes green: " lastdc
        }
        for (k in seen) delete seen[k]
      }
      /^## / {
        flush()
        if ($0 ~ /^## Feature [0-9]+:/) {
          insec = 1; sec = $0
          sub(/^## /, "", sec); sub(/:.*$/, "", sec)
          lastdc = ""; subh = ""
        } else insec = 0
        next
      }
      !insec { next }
      /^### / { subh = $0; seen[$0] = 1; next }
      {
        # Standalone uppercase tokens only: a product/domain word like "Todo"
        # or an identifier like "TODOS_TABLE" is not a placeholder (2026-07-22
        # doit-n-live false positive).
        if ($0 ~ /(^|[^A-Za-z_])(TBD|TODO)([^A-Za-z_]|$)|\{\{/) {
          if (subh == "### Done criteria") print "F|" sec "|unresolved placeholder in done criteria: " $0
          else print "W|" sec "|unresolved placeholder: " $0
        }
        if (subh == "### Done criteria" && $0 ~ /^- /) lastdc = $0
        if (subh == "### Explicitly out of scope" && $0 ~ /^- /) {
          # A destination may be a Feature number or non-Feature prose (a
          # successor PRD, backlog, frozen branch). The deterministic layer
          # checks only the arrow-and-named-destination form; destination
          # validity is Layer-2 semantics (2026-07-23 spade-ace false positive).
          if ($0 !~ /(→|->)[ ]*[^ ]/ && $0 !~ /None/)
            print "F|" sec "|out-of-scope item lacks destination Feature: " $0
        }
      }
      END { flush() }' "$MAP")

    if [ -n "$FEATURE" ] && ! grep -q "^## Feature ${FEATURE}:" "$MAP"; then
      features_ok=false
      note F "Feature ${FEATURE} section not found in $MAP"
    fi

    # Audit Signals are classified by the canonical policy runtime, never by
    # duplicated shell conditions. Legacy maps without the section remain
    # valid and classify T2 later; a present section requires the complete
    # capability and strict closed-schema validation.
    if grep -q '^### Audit signals[[:space:]]*$' "$MAP"; then
      if [ "$AUDIT_CAPABILITY" != "available" ]; then
        audit_signals_ok=false
        note F "Audit signals present but audit-tier capability is ${AUDIT_CAPABILITY}"
      else
        validate_args=(--policy "$AUDIT_POLICY" validate-map --feature-map "$MAP")
        [ -n "$FEATURE" ] && validate_args+=(--feature "$FEATURE")
        if ! audit_validation=$("$PYTHON_BIN" "$AUDIT_CLASSIFIER" "${validate_args[@]}" 2>&1); then
          audit_signals_ok=false
          note F "Audit signals schema validation failed: ${audit_validation//$'\n'/ }"
        fi
      fi
    elif [ "$AUDIT_CAPABILITY" = "partial-sync" ]; then
      audit_signals_ok=false
      note F "audit-tier capability is partially synced"
    fi

    # Implementation Obligations (D-IDs, specter-agent-protocols §10): the
    # section is optional — legacy maps without it stay valid — but a present
    # section must satisfy the closed schema. Semantic tenability (the two-part
    # entailment/denylist test) is Layer 2's job; this checks shape and
    # referential integrity only.
    if grep -q '^## Implementation Obligations' "$MAP"; then
      while IFS= read -r line; do
        [ -n "$line" ] || continue
        obligations_ok=false
        note "${line%%|*}" "${line#*|}"
      done < <(awk '
        BEGIN { rows = 0; hdr = 0 }
        /^## Implementation Obligations/ { inobl = 1; next }
        /^## / { inobl = 0 }
        inobl && /^\|/ {
          if ($0 ~ /^\|[-: |]+$/) next
          n = split($0, c, "|")
          for (i = 1; i <= n; i++) gsub(/^[ ]+|[ ]+$/, "", c[i])
          if ($0 ~ /D-ID/) {
            for (i = 1; i <= n; i++) {
              if (c[i] == "D-ID") dcol = i
              if (c[i] == "Supports") scol = i
              if (c[i] == "Kind") kcol = i
              if (c[i] == "Impact") icol = i
              if (c[i] == "Owning Feature") fcol = i
            }
            if (!dcol || !scol || !kcol || !icol || !fcol)
              print "F|Implementation Obligations header lacks a required column (need D-ID, Supports, Kind, Impact, Owning Feature)"
            else hdr = 1
            next
          }
          if (!hdr) next
          rows++
          did = c[dcol]
          if (did !~ /^D-[0-9]+$/) print "F|invalid D-ID: " did
          else if (did in seen) print "F|duplicate D-ID: " did
          seen[did] = 1
          if (c[scol] == "") print "F|" did " has an empty Supports cell"
          else {
            m = split(c[scol], sup, /[,;]/)
            for (j = 1; j <= m; j++) {
              s = sup[j]; gsub(/^[ ]+|[ ]+$/, "", s)
              if (s ~ /^D-?[0-9]+$/) print "F|" did " Supports cites a D-ID (" s ") — D-to-D chains are forbidden"
              else if (s !~ /^C-?[0-9]+$/) print "F|" did " Supports token is not a C-ID: " s
            }
          }
          if (c[kcol] !~ /^(logical-enablement|verification-only|governing-constraint|existing-system-constraint)$/)
            print "F|" did " has an unknown Kind: " c[kcol]
          if (c[icol] !~ /^(none|user-visible|operational)$/)
            print "F|" did " has an unknown Impact: " c[icol]
          if (c[fcol] !~ /^Feature [0-9]+$/)
            print "F|" did " Owning Feature is not exactly one Feature: " c[fcol]
        }
        END {
          if (hdr && rows == 0) print "F|Implementation Obligations section has no rows"
        }' "$MAP")

      # Referential integrity: every C-ID cited in the section must exist in
      # the baseline checklist (dash-insensitive). Skipped when no baseline
      # exists yet — /ms.featuremap's structural run precedes the checklist.
      if [ -f "$CODEX_PRD_CHECKLIST" ]; then
        while IFS= read -r cid; do
          [ -n "$cid" ] || continue
          obligations_ok=false
          note F "Implementation Obligations cites ${cid}, which does not exist in $CODEX_PRD_CHECKLIST"
        done < <(comm -23 \
          <(awk '/^## Implementation Obligations/{f=1;next} /^## /{f=0} f' "$MAP" \
            | grep -oE 'C-?[0-9]+' | tr -d '-' | sort -u) \
          <(grep -oE 'C-?[0-9]+' "$CODEX_PRD_CHECKLIST" | tr -d '-' | sort -u))
      fi
    fi

    # DAG acyclicity from the Progress Ledger's Depends-on column.
    if [ -f "$PROGRESS" ]; then
      dag_out=$(awk '
        /^\|/ {
          if ($0 ~ /^\|[-: |]+$/) next
          split($0, c, "|")
          id = c[2]; deps = c[3]
          gsub(/^[ ]+|[ ]+$/, "", id)
          if (id !~ /^[0-9]+/) next
          match(id, /^[0-9]+/)
          node = substr(id, RSTART, RLENGTH) + 0
          nodes[node] = 1
          n = split(deps, dl, ",")
          for (i = 1; i <= n; i++) {
            d = dl[i]; gsub(/[^0-9]/, "", d)
            if (d != "") edge[node] = edge[node] " " (d + 0)
          }
        }
        END {
          changed = 1
          while (changed) {
            changed = 0
            for (v in nodes) {
              if (done[v]) continue
              ok = 1
              split(edge[v], ds, " ")
              for (j in ds) { d = ds[j]; if (d == "") continue; if ((d in nodes) && !done[d]) ok = 0 }
              if (ok) { done[v] = 1; changed = 1 }
            }
          }
          cyc = 0
          for (v in nodes) if (!done[v]) { cyc = 1; printf "CYCLE %03d\n", v }
          if (!cyc) print "OK"
        }' "$PROGRESS")
      if [ "$dag_out" != "OK" ]; then
        dag_ok=false
        while IFS= read -r cyc_line; do
          note F "dependency cycle involves Feature ${cyc_line#CYCLE }"
        done <<< "$dag_out"
      fi
    else
      dag_ok=false
      note W "missing: $PROGRESS — DAG acyclicity not checked"
    fi
  fi

  # Per-Feature checklist cross-references (only with an explicit Feature).
  if [ -n "$FEATURE" ]; then
    FCHECK="docs/prd/checklists/feature-${FEATURE}.checklist.md"
    if [ -f "$FCHECK" ]; then
      if grep -qE '(^|[^A-Za-z_])(TBD|TODO)([^A-Za-z_]|$)|\{\{' "$FCHECK"; then
        placeholders_ok=false
        note W "unresolved placeholder token(s) in $FCHECK"
      fi
      if [ -f "$CODEX_PRD_CHECKLIST" ]; then
        while IFS= read -r cid; do
          [ -n "$cid" ] || continue
          if ! grep -q "$cid" "$CODEX_PRD_CHECKLIST"; then
            checklist_refs_ok=false
            note F "checklist cites $cid, which does not exist in $CODEX_PRD_CHECKLIST"
          fi
        done < <(grep -oE 'C[0-9]{3}' "$FCHECK" | sort -u)
      else
        note W "missing: $CODEX_PRD_CHECKLIST — C-ID cross-reference not checked"
      fi
    else
      note W "missing: $FCHECK — checklist structure not checked"
    fi
  fi

  feature_json="null"
  [ -n "$FEATURE" ] && feature_json="\"$(json_escape "$FEATURE")\""
  scope="global"
  [ -n "$FEATURE" ] && scope="feature"

  cat <<JSON
{
  "mode": "structural",
  "scope": "${scope}",
  "feature": ${feature_json},
  "checks": {
    "commitment_index_ok": ${index_ok},
    "feature_sections_ok": ${features_ok},
    "dag_acyclic": ${dag_ok},
    "placeholders_clean": ${placeholders_ok},
    "checklist_refs_ok": ${checklist_refs_ok},
    "audit_signals_ok": ${audit_signals_ok},
    "implementation_obligations_ok": ${obligations_ok}
  },
  "verdict": "${verdict}",
  "reasons": $(reasons_to_json)
}
JSON
  exit 0
fi

# ---- manifest subcommand (C5': gate-generated expected coverage inventory) ----
# The inventory is derived from the audited artifacts so the reviewer cannot
# assert "191/191 checked" after sampling — Layer 3 later verifies exact set
# equality against the reviewer's ## Coverage rows. Review has no manifest:
# its per-criterion inventory is the Done Criteria Execution table.

if [ "$SUBCOMMAND" = "manifest" ]; then
  STATION="${1:-}"; ARG="${2:-}"
  verdict="PASS"
  keys=""
  case "$STATION" in
    pre-verify|verify|analyze)
      resolve_station "$STATION" "$ARG"
      if [ -n "$RS_ERROR" ]; then
        add_reason "$RS_ERROR"; verdict="FAIL"
      else
        keys=$(manifest_keys "$STATION" "$RS_FEATURE" "$ARG")
        [ -n "$keys" ] || { add_reason "no coverage keys could be extracted for station ${STATION} — check the audited artifacts exist"; verdict="FAIL"; }
      fi
      ;;
    *)
      add_reason "unknown manifest station '${STATION:-<none>}' (expected pre-verify|verify|analyze)"
      verdict="FAIL"
      ;;
  esac
  keys_json="[]"
  count=0
  if [ -n "$keys" ]; then
    keys_json="["
    kfirst=true
    while IFS= read -r k; do
      [ -n "$k" ] || continue
      $kfirst || keys_json+=","
      kfirst=false
      keys_json+="\"$(json_escape "$k")\""
      count=$((count + 1))
    done <<< "$keys"
    keys_json+="]"
  fi
  feature_json="null"
  [ -n "${RS_FEATURE:-}" ] && feature_json="\"$(json_escape "$RS_FEATURE")\""
  cat <<JSON
{
  "mode": "manifest",
  "station": "$(json_escape "$STATION")",
  "feature": ${feature_json},
  "continuity_contract": "${CONTINUITY_CONTRACT}",
  "count": ${count},
  "keys": ${keys_json},
  "verdict": "${verdict}",
  "reasons": $(reasons_to_json)
}
JSON
  exit 0
fi

# ---- continuity subcommand (C4': mechanical re-round continuity packet) ----
# Built ONLY from the immutable round archives + verbatim finding rows: the
# host passes the packet path to the reviewer prompt but never authors packet
# content. The packet is explicitly NOT a PASS whitelist — it exists so a
# reviewer lane that contradicts its own prior Required Fix must classify the
# finding REVERSAL instead of issuing an ordinary new FAIL.

if [ "$SUBCOMMAND" = "continuity" ]; then
  STATION="${1:-}"
  shift || true
  ARG=""
  ROUND="2"
  DIFF_PATH=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --round) shift; ROUND="${1:-2}" ;;
      --diff) shift; DIFF_PATH="${1:-}" ;;
      *) [ -z "$ARG" ] && ARG="$1" ;;
    esac
    shift || true
  done
  [[ "$ROUND" =~ ^[0-9]+$ ]] || ROUND="2"

  verdict="PASS"
  packet=""
  rounds_archived=0
  blocking=0

  case "$STATION" in
    pre-verify|verify|analyze|review|agent-verify)
      resolve_station "$STATION" "$ARG"
      if [ -n "$RS_ERROR" ]; then
        add_reason "$RS_ERROR"; verdict="FAIL"
      fi
      ;;
    *)
      add_reason "unknown continuity station '${STATION:-<none>}' (expected pre-verify|verify|analyze|review)"
      verdict="FAIL"
      ;;
  esac

  if [ "$verdict" = "PASS" ]; then
    suffix=""
    if [ -n "$RS_FEATURE" ]; then suffix="-${RS_FEATURE}"
    elif [ -n "$ARG" ]; then suffix="-$(basename "${ARG%/}")"
    fi
    mkdir -p .specify/continuity
    packet=".specify/continuity/${RS_STEP}${suffix}.packet.md"
    {
      printf '# Continuity Packet — %s%s\n\n' "$RS_STEP" "$suffix"
      printf '**Station**: %s\n' "$RS_STEP"
      printf '**Built for round**: %s\n' "$ROUND"
      printf '**Generated**: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      [ -n "$DIFF_PATH" ] && printf '**Repair diff**: %s\n' "$DIFF_PATH"
      printf '\n'
      printf '> This packet contains prior BLOCKING findings and their Required Fixes\n'
      printf '> only, copied verbatim from the immutable round archives. It is NOT a\n'
      printf '> PASS whitelist: it confers no immunity, and full-scope discovery outside\n'
      printf '> these findings remains allowed and expected. If this reviewer lane\n'
      printf '> previously prescribed the state now being rejected, retain the\n'
      printf '> predecessor ID, classify the finding REVERSAL, quote the prior Required\n'
      printf '> Fix verbatim, and identify the failed premise\n'
      printf '> (specter-agent-protocols §5).\n'
    } > "$packet"
    r=1
    while [ "$r" -lt "$ROUND" ]; do
      rr=$(printf '%02d' "$r")
      found_this_round=false
      for f in ${RS_INPUTS[@]+"${RS_INPUTS[@]}"}; do
        arch="${f%.md}.round-${rr}.md"
        [ -s "$arch" ] || continue
        found_this_round=true
        arch_sha_val=""
        [ -n "$RS_SHA_FIELD" ] && arch_sha_val=$(extract_field "$arch" "$RS_SHA_FIELD")
        {
          printf '\n## Round %s — %s\n\n' "$rr" "$f"
          [ -n "$arch_sha_val" ] && printf '**Audited artifact SHA at that round**: %s\n\n' "$arch_sha_val"
        } >> "$packet"
        # Verbatim blocking rows from the archived Findings table — never
        # paraphrased. Works for both the legacy 4-column and the continuity-v1
        # lineage schema (any cell exactly one of the blocking severities).
        #
        # BLOCKING is accepted alongside CRITICAL/HIGH: §6 of the protocol calls
        # these "prior blocking findings" and the station prompts never fix a
        # severity vocabulary, so reviewers legitimately write BLOCKING. Omitting
        # it made the packet report "(no blocking findings)" for a round whose
        # report carried three, silently dropping the lineage a re-round depends
        # on. Under-reporting here is the dangerous direction: a dropped finding
        # is one the next round is never told to carry forward.
        rows=$(awk '
          /^## Findings/ { f = 1; next }
          /^## / { f = 0 }
          f && /^\|/ && $0 !~ /^\|[-: |]+$/ && $0 !~ /Severity[ ]*\|/ {
            n = split($0, c, "|")
            for (i = 1; i <= n; i++) {
              cell = c[i]; gsub(/^[ \t]+|[ \t]+$/, "", cell)
              if (cell == "CRITICAL" || cell == "HIGH" || cell == "BLOCKING") { print; next }
            }
          }' "$arch")
        if [ -n "$rows" ]; then
          printf '%s\n' "$rows" >> "$packet"
          blocking=$((blocking + $(printf '%s\n' "$rows" | wc -l)))
        else
          printf '(no blocking findings in this lane at this round)\n' >> "$packet"
        fi
      done
      [ "$found_this_round" = true ] && rounds_archived=$((rounds_archived + 1))
      r=$((r + 1))
    done
    if [ "$rounds_archived" -eq 0 ]; then
      printf '\n(no archived prior rounds found — this station has no continuity history yet; legacy in-flight reports predate continuity-v1)\n' >> "$packet"
      add_reason "no archived round reports found for rounds < ${ROUND} — packet is empty (legacy in-flight station or wrong --round)"
    fi
  fi

  feature_json="null"
  [ -n "${RS_FEATURE:-}" ] && feature_json="\"$(json_escape "$RS_FEATURE")\""
  packet_json="null"
  [ -n "$packet" ] && packet_json="\"$(json_escape "$packet")\""
  cat <<JSON
{
  "mode": "continuity",
  "station": "$(json_escape "$STATION")",
  "feature": ${feature_json},
  "round": ${ROUND},
  "continuity_contract": "${CONTINUITY_CONTRACT}",
  "packet": ${packet_json},
  "rounds_archived": ${rounds_archived},
  "blocking_findings": ${blocking},
  "verdict": "${verdict}",
  "reasons": $(reasons_to_json)
}
JSON
  exit 0
fi

# ---- aggregate subcommand (Layer 3: mechanical verdict aggregation) ----
# The station name fixes the report set; the caller can never add, omit, or
# reorder inputs (specter-agent-protocols §7 — dynamic input choice would let
# a failing report simply be left out).

if [ "$SUBCOMMAND" = "aggregate" ]; then
  STATION="${1:-}"
  shift || true
  ARG=""
  LEDGER=false
  ROUND="1"
  EXPECT_PROTOCOL=""
  REQUIRE_COVERAGE=false
  while [ $# -gt 0 ]; do
    case "$1" in
      --ledger) LEDGER=true ;;
      --round) shift; ROUND="${1:-1}" ;;
      --expect-protocol) shift; EXPECT_PROTOCOL="${1:-}" ;;
      --require-coverage) REQUIRE_COVERAGE=true ;;
      *) [ -z "$ARG" ] && ARG="$1" ;;
    esac
    shift || true
  done
  [[ "$ROUND" =~ ^[0-9]+$ ]] || ROUND="1"
  if [ -n "$EXPECT_PROTOCOL" ] && [ "$EXPECT_PROTOCOL" != "$CONTINUITY_CONTRACT" ]; then
    add_reason "--expect-protocol '${EXPECT_PROTOCOL}' does not match this gate's continuity contract '${CONTINUITY_CONTRACT}' — partial sync; run /ms.sync"
  fi

  verdict="PASS"
  audit_tier="T2"
  tier_receipt_sha=""
  tier_policy_hash=""
  tier_settings_json="null"
  warn_ack_required=false
  warn_ack_satisfied=false
  reversal_present=false
  coverage_breach_present=false

  # Legacy alias normalization also happens here so the later
  # station-name comparisons see the canonical name.
  [ "$STATION" = "agent-verify" ] && STATION="verify"

  resolve_station "$STATION" "$ARG"
  if [ -n "$RS_ERROR" ]; then
    add_reason "$RS_ERROR"; verdict="FAIL"
  fi
  INPUTS=(${RS_INPUTS[@]+"${RS_INPUTS[@]}"})
  EXPECTED_MODES=(${RS_MODES[@]+"${RS_MODES[@]}"})
  cycle="$RS_CYCLE"
  step="$RS_STEP"
  agg_feature="$RS_FEATURE"
  sha_field="$RS_SHA_FIELD"
  sha_target="$RS_SHA_TARGET"
  feature_check="$RS_FEATURE_CHECK"

  # Declared-coverage stations (C5'): only these have a gate-generated
  # expected inventory to check ## Coverage against.
  manifest_station=false
  case "$STATION" in pre-verify|verify|analyze) manifest_station=true ;; esac
  if [ "$REQUIRE_COVERAGE" = true ] && [ "$manifest_station" != true ]; then
    add_reason "--require-coverage is only valid for stations pre-verify|verify|analyze"
    REQUIRE_COVERAGE=false
  fi
  expected_keys=""
  if [ "$manifest_station" = true ] && { [ "$REQUIRE_COVERAGE" = true ] || [ -n "$EXPECT_PROTOCOL" ]; }; then
    expected_keys=$(manifest_keys "$STATION" "$agg_feature" "$ARG")
  fi

  # Tiered stations consume the one fixed per-Feature receipt path. The host
  # cannot pass a receipt path or tier value. Global pre-verify and expand stay
  # full-strength and untiered.
  if [ "$STATION" = "verify" ] || [ "$STATION" = "analyze" ] || [ "$STATION" = "review" ]; then
    if [ "$AUDIT_CAPABILITY" = "available" ] && [ -n "$agg_feature" ]; then
      if tier_status=$("$PYTHON_BIN" "$AUDIT_CLASSIFIER" --policy "$AUDIT_POLICY" gate-status \
          --feature "$agg_feature" --station "$STATION" 2>&1); then
        audit_tier=$(json_value "$tier_status" "effective_tier")
        tier_receipt_sha=$(json_value "$tier_status" "tier_receipt_sha256")
        tier_policy_hash=$(json_value "$tier_status" "policy_hash")
        warn_ack_required=$(json_value "$tier_status" "warn_ack_required")
        warn_ack_satisfied=$(json_value "$tier_status" "warn_ack_satisfied")
        tier_settings_json=$(printf '%s' "$tier_status" | "$PYTHON_BIN" -c 'import json,sys; print(json.dumps(json.load(sys.stdin).get("tier_settings"), separators=(",",":")))')
      else
        verdict="FAIL"
        add_reason "invalid or stale audit-tier receipt for ${STATION} Feature ${agg_feature}: ${tier_status//$'\n'/ }"
      fi
    elif [ "$AUDIT_CAPABILITY" = "partial-sync" ] || [ "$AUDIT_CAPABILITY" = "python-unavailable" ]; then
      verdict="FAIL"
      add_reason "audit-tier capability is ${AUDIT_CAPABILITY}; run /ms.init or /ms.sync"
    else
      # Backward compatibility for a fully legacy consumer: current SPECTER
      # behavior is T2. Updated commands require the capability probe before
      # using tier-specific orchestration.
      audit_tier="T2"
    fi
  fi

  inputs_json="["
  cap_agents=()
  caught=()
  REPORT_SHAS=()
  first=true
  idx=0

  for f in ${INPUTS[@]+"${INPUTS[@]}"}; do
    in_result=""
    in_avail=""
    in_sha=""
    in_mode=""
    in_verdict="FAIL"
    expected_mode="${EXPECTED_MODES[$idx]:-}"
    idx=$((idx + 1))

    if [ ! -s "$f" ]; then
      # Keep the hash array aligned with the artifacts array: an unhashable
      # (missing/empty) input records "" at its position, never a silent skip.
      REPORT_SHAS+=("")
      add_reason "missing or empty report: $f"
    else
      in_sha=$(sha256sum "$f" | awk '{print $1}')
      REPORT_SHAS+=("$in_sha")
      # Immutable round archive (continuity-v1): a --ledger run is the verdict
      # emission of record, so it archives what it graded. Re-rounds overwrite
      # the canonical path; the archive is where the original observation
      # survives. Reusing a round number with different content is exactly the
      # overwrite the archive exists to prevent.
      if [ "$LEDGER" = true ]; then
        arch="${f%.md}.round-$(printf '%02d' "$ROUND").md"
        if [ -f "$arch" ]; then
          if ! cmp -s "$f" "$arch"; then
            verdict="FAIL"
            add_reason "round ${ROUND} archive already exists with different content: ${arch} — round reports are immutable; use the next --round number"
          fi
        else
          cp "$f" "$arch"
        fi
      fi
      in_mode=$(extract_field "$f" "Mode")
      result_count=$(grep -c '^\*\*Result\*\*:' "$f" || true)
      in_result=$(extract_field "$f" "Result")
      in_avail=$(extract_field "$f" "Availability")
      structural_ok=true
      if [ -n "$expected_mode" ] && [ "$in_mode" != "$expected_mode" ]; then
        # A report from the wrong station (or with no Mode) must never grade
        # this station — degrade placeholders carry the normal Mode too (§2).
        structural_ok=false
        add_reason "report Mode '${in_mode:-missing}' does not match station mode '${expected_mode}': $f"
      elif [ "$result_count" -ne 1 ]; then
        structural_ok=false
        add_reason "expected exactly one Result line in $f (found ${result_count})"
      elif [ "$in_result" != "PASS" ] && [ "$in_result" != "WARN" ] && [ "$in_result" != "FAIL" ]; then
        structural_ok=false
        add_reason "invalid Result '${in_result}' in $f"
      fi
      # Identity and freshness bind EVERY report, degrade placeholders
      # included (§2 placeholders carry Feature and the SHA field too) —
      # a stale or mis-scoped placeholder must not become an accepted cap.
      if [ "$structural_ok" = true ] && [ "$feature_check" = true ]; then
        rep_feature=$(extract_field "$f" "Feature")
        feature_num=$((10#$agg_feature))
        if ! [[ "$rep_feature" =~ Feature\ 0*${feature_num}([^0-9]|$) ]]; then
          structural_ok=false
          add_reason "report Feature field '${rep_feature:-missing}' does not match Feature ${agg_feature}: $f"
        fi
      fi
      if [ "$structural_ok" = true ] && [ -n "$sha_field" ]; then
        if [ -f "$sha_target" ]; then
          rec_sha=$(extract_field "$f" "$sha_field")
          cur_sha=$(sha256sum "$sha_target" | awk '{print $1}')
          if [ -z "$rec_sha" ] || [ "$rec_sha" != "$cur_sha" ]; then
            structural_ok=false
            add_reason "stale ${sha_field} in $f (recorded=${rec_sha:-none}, current=${cur_sha})"
          fi
        else
          structural_ok=false
          add_reason "missing SHA target: $sha_target"
        fi
      fi
      # ---- continuity-v1 validations (C4'/C5') — non-placeholder reports only ----
      cov_unverified=false
      if [ "$structural_ok" = true ] && [ -z "$in_avail" ] && [ -n "$EXPECT_PROTOCOL" ]; then
        in_proto=$(extract_field "$f" "Protocol")
        if [ "$in_proto" != "$EXPECT_PROTOCOL" ]; then
          structural_ok=false
          add_reason "report Protocol '${in_proto:-missing}' does not match expected '${EXPECT_PROTOCOL}' (report predates the continuity schema or the agent omitted the field — re-run the station): $f"
        fi
      fi
      if [ "$structural_ok" = true ] && [ -z "$in_avail" ] && [ "$manifest_station" = true ]; then
        cov_count=$(grep -c '^## Coverage' "$f" || true)
        if [ "$cov_count" -eq 0 ]; then
          if [ "$REQUIRE_COVERAGE" = true ]; then
            structural_ok=false
            add_reason "missing '## Coverage' declared-coverage-closure section (one row per expected inventory key): $f"
          fi
        else
          # Parse "| key | result | evidence |" rows.
          cov_rows=$(awk '
            /^## Coverage/ { f = 1; next }
            /^## / { f = 0 }
            f && /^\|/ && $0 !~ /^\|[-: |]+$/ {
              n = split($0, c, "|")
              for (i = 1; i <= n; i++) gsub(/^[ ]+|[ ]+$/, "", c[i])
              if (c[2] == "Key") next
              print c[2] "\t" c[3] "\t" c[4]
            }' "$f")
          declared_keys=""
          while IFS=$'\t' read -r ck cr ce; do
            [ -n "$ck" ] || continue
            declared_keys+="${ck}"$'\n'
            case "$cr" in
              PASS) : ;;
              FAIL)
                if [ "$in_result" = "PASS" ]; then
                  structural_ok=false
                  add_reason "coverage row '${ck}' is FAIL but the report Result is PASS (inconsistent closure claim): $f"
                fi
                ;;
              UNVERIFIED) cov_unverified=true ;;
              *)
                structural_ok=false
                add_reason "coverage row '${ck}' has invalid result '${cr:-<empty>}' (expected PASS|FAIL|UNVERIFIED): $f"
                ;;
            esac
            if [ -z "$ce" ]; then
              structural_ok=false
              add_reason "coverage row '${ck}' has empty evidence: $f"
            else
              # When the evidence leads with a file:line citation, the file
              # must exist (a cheap reality check; deeper spot-checks stay
              # with the second reviewer).
              ev_tok="${ce%% *}"
              if [[ "$ev_tok" =~ ^([A-Za-z0-9_./-]+):[0-9]+$ ]] && [ ! -f "${BASH_REMATCH[1]}" ]; then
                structural_ok=false
                add_reason "coverage row '${ck}' cites non-existent file '${BASH_REMATCH[1]}': $f"
              fi
            fi
          done <<< "$cov_rows"
          dup_keys=$(printf '%s' "$declared_keys" | sort | uniq -d | head -5 || true)
          if [ -n "$dup_keys" ]; then
            structural_ok=false
            add_reason "duplicate coverage keys (${dup_keys//$'\n'/, }): $f"
          fi
          if [ -n "$expected_keys" ]; then
            declared_sorted=$(printf '%s' "$declared_keys" | sort -u)
            missing_keys=$(comm -23 <(printf '%s\n' "$expected_keys") <(printf '%s\n' "$declared_sorted") | sed '/^$/d' || true)
            unknown_keys=$(comm -13 <(printf '%s\n' "$expected_keys") <(printf '%s\n' "$declared_sorted") | sed '/^$/d' || true)
            if [ -n "$missing_keys" ]; then
              structural_ok=false
              n_missing=$(printf '%s\n' "$missing_keys" | wc -l)
              sample=$(printf '%s\n' "$missing_keys" | head -15 | tr '\n' ' ')
              add_reason "coverage is not set-equal to the expected inventory: ${n_missing} expected key(s) undeclared (${sample% }...): $f"
            fi
            if [ -n "$unknown_keys" ]; then
              structural_ok=false
              n_unknown=$(printf '%s\n' "$unknown_keys" | wc -l)
              sample=$(printf '%s\n' "$unknown_keys" | head -15 | tr '\n' ' ')
              add_reason "coverage declares ${n_unknown} key(s) not in the expected inventory (${sample% }...): $f"
            fi
          fi
        fi
      fi
      if [ "$structural_ok" = true ] && [ -z "$in_avail" ]; then
        # Finding-lineage validation (C4'): strict on re-rounds under
        # --expect-protocol; enum/dup validation whenever lineage columns are
        # present. REVERSAL / COVERAGE_BREACH markers route mechanically.
        strict_lineage=false
        [ "$ROUND" -ge 2 ] && [ -n "$EXPECT_PROTOCOL" ] && strict_lineage=true
        lineage_rows=$(awk '
          /^## Findings/ { f = 1; next }
          /^## / { f = 0 }
          f && /^\|/ {
            if ($0 ~ /^\|[-: |]+$/) next
            n = split($0, c, "|")
            for (i = 1; i <= n; i++) gsub(/^[ ]+|[ ]+$/, "", c[i])
            if (!hdr) {
              ishdr = 0
              for (i = 1; i <= n; i++) if (c[i] == "Severity") ishdr = 1
              if (ishdr) {
                for (i = 1; i <= n; i++) {
                  if (c[i] == "ID") idc = i
                  if (c[i] == "Predecessor") pc = i
                  if (c[i] == "Status") sc = i
                  if (c[i] == "Class") cc = i
                }
                hdr = 1
                next
              }
            }
            if (idc && cc) print "ROW\t" c[idc] "\t" (pc ? c[pc] : "") "\t" (sc ? c[sc] : "") "\t" c[cc]
            else nolineage = 1
          }
          END { if (nolineage) print "NOHDR" }' "$f")
        prior_ids=""
        if [ "$strict_lineage" = true ]; then
          r=1
          while [ "$r" -lt "$ROUND" ]; do
            p_arch="${f%.md}.round-$(printf '%02d' "$r").md"
            if [ -s "$p_arch" ]; then
              p_ids=$(awk '
                /^## Findings/ { f = 1; next }
                /^## / { f = 0 }
                f && /^\|/ {
                  if ($0 ~ /^\|[-: |]+$/) next
                  n = split($0, c, "|")
                  for (i = 1; i <= n; i++) gsub(/^[ ]+|[ ]+$/, "", c[i])
                  if (!hdr) {
                    ishdr = 0
                    for (i = 1; i <= n; i++) if (c[i] == "Severity") ishdr = 1
                    if (ishdr) { for (i = 1; i <= n; i++) if (c[i] == "ID") idc = i; hdr = 1; next }
                  }
                  if (idc && c[idc] != "") print c[idc]
                }' "$p_arch")
              [ -n "$p_ids" ] && prior_ids+="${p_ids}"$'\n'
            fi
            r=$((r + 1))
          done
          prior_ids=$(printf '%s' "$prior_ids" | sed '/^$/d' | sort -u)
        fi
        seen_ids=""
        while IFS=$'\t' read -r tag lid lpred lstat lclass; do
          case "$tag" in
            NOHDR)
              if [ "$strict_lineage" = true ]; then
                structural_ok=false
                add_reason "re-round Findings rows lack the continuity lineage columns (ID/Predecessor/Status/Class): $f"
              fi
              ;;
            ROW)
              if [ -z "$lid" ]; then
                structural_ok=false; add_reason "finding row has an empty ID: $f"
              elif printf '%s\n' "$seen_ids" | grep -qx -- "$lid"; then
                structural_ok=false; add_reason "duplicate finding ID '${lid}': $f"
              fi
              seen_ids+="${lid}"$'\n'
              case "$lstat" in
                PERSISTING|RESOLVED|REOPENED|NEW|"") : ;;
                *) structural_ok=false; add_reason "finding '${lid}' has invalid Status '${lstat}' (expected PERSISTING|RESOLVED|REOPENED|NEW): $f" ;;
              esac
              case "$lclass" in
                NEW_EVIDENCE|PREVIOUSLY_UNAUDITED|REGRESSION_FROM_DIFF) : ;;
                REVERSAL) reversal_present=true ;;
                COVERAGE_BREACH) coverage_breach_present=true ;;
                "")
                  if [ "$strict_lineage" = true ]; then
                    structural_ok=false; add_reason "finding '${lid}' has no Classification (expected NEW_EVIDENCE|PREVIOUSLY_UNAUDITED|REGRESSION_FROM_DIFF|REVERSAL|COVERAGE_BREACH): $f"
                  fi
                  ;;
                *) structural_ok=false; add_reason "finding '${lid}' has invalid Classification '${lclass}': $f" ;;
              esac
              if [ "$strict_lineage" = true ] && [ -n "$prior_ids" ] && [ -n "$lpred" ] && [ "$lpred" != "none" ]; then
                if ! printf '%s\n' "$prior_ids" | grep -qx -- "$lpred"; then
                  structural_ok=false
                  add_reason "finding '${lid}' cites unknown Predecessor '${lpred}' (not in any archived prior round): $f"
                fi
              fi
              ;;
          esac
        done <<< "$lineage_rows"
      fi
      if [ "$structural_ok" = true ]; then
        if [ -n "$in_avail" ]; then
          # §2/§7 typed degrade placeholder: only WARN + UNAVAILABLE/RECUSED
          # is environmental; anything else is an agent-authored failure -> FAIL.
          if [[ "$in_avail" =~ ^(UNAVAILABLE|RECUSED) ]] && [ "$in_result" = "WARN" ]; then
            in_verdict="WARN"
            cap_agents+=("$f")
          else
            add_reason "malformed Availability '${in_avail}' (Result '${in_result}') in $f"
          fi
        else
          in_verdict="$in_result"
          if [ "$cov_unverified" = true ] && [ "$in_verdict" = "PASS" ]; then
            # §5: an UNVERIFIED item is never folded into PASS — WARN cap.
            in_verdict="WARN"
            add_reason "coverage contains UNVERIFIED row(s) — Result capped at WARN (§5 UNVERIFIED-not-PASS): $f"
          fi
          if [ "$in_verdict" != "PASS" ]; then
            # Verbatim finding rows for the mechanical ledger (never paraphrased).
            while IFS= read -r row; do
              [ -n "$row" ] && caught+=("$row")
            done < <(awk '/^## Findings/ { f = 1; next } /^## / { f = 0 } f && /^\|/ && $0 !~ /^\|[-: |]+$/ && $0 !~ /Severity[ ]*\|/ { print }' "$f")
          fi
        fi
      fi
    fi

    verdict=$(worse "$verdict" "$in_verdict")
    $first || inputs_json+=","
    first=false
    inputs_json+="{\"path\":\"$(json_escape "$f")\",\"sha256\":\"$(json_escape "$in_sha")\",\"result\":\"$(json_escape "$in_result")\",\"availability\":\"$(json_escape "$in_avail")\",\"graded\":\"${in_verdict}\"}"
  done
  inputs_json+="]"

  # Zero independent verifiers left (every input is a degrade placeholder):
  # the station cannot produce a verdict — FAIL, never a host-only opinion.
  if [ "${#INPUTS[@]}" -gt 0 ] && [ "${#cap_agents[@]}" -eq "${#INPUTS[@]}" ]; then
    verdict="FAIL"
    add_reason "every agent report is a degrade placeholder — no independent verifier ran"
  fi

  # Mechanical continuity routing (C4'): the receipt records these so the
  # driving command cannot proceed into another automatic repair round.
  if [ "$reversal_present" = true ]; then
    add_reason "REVERSAL finding present — automatic repair rounds stop mechanically; enter a fresh dual doctrine-dispute round (specter-agent-protocols §4/§5); disagreement escalates to the human"
  fi
  if [ "$coverage_breach_present" = true ]; then
    add_reason "COVERAGE_BREACH finding present — a previously exhausted class produced a pre-existing violation; the prior closure claim is invalidated and the class must be re-exhausted (the new defect is preserved, never suppressed)"
  fi

  # Expand-only: the Codex delta checklist is this station's independent input
  # baseline; its absence is a mechanical WARN cap, never silently absorbed by
  # host prose.
  baseline_cap=""
  if [ "$STATION" = "expand" ] && [[ "$ARG" =~ ^[0-9]+$ ]]; then
    delta_baseline="docs/prd/featuremap-checklist-delta-${ARG}.md"
    [ -s "$delta_baseline" ] || delta_baseline="docs/prd/codex/checklist-delta-${ARG}.md"  # legacy path
    if [ ! -s "$delta_baseline" ]; then
      verdict=$(worse "$verdict" "WARN")
      baseline_cap="missing-baseline"
      add_reason "independent delta baseline docs/prd/featuremap-checklist-delta-${ARG}.md missing or empty — WARN cap"
    fi
  fi

  cap_json="null"
  if [ "$verdict" != "FAIL" ]; then
    if [ "${#cap_agents[@]}" -gt 0 ]; then
      cap_json="\"single-agent-degrade\""
    elif [ -n "$baseline_cap" ]; then
      cap_json="\"${baseline_cap}\""
    fi
  fi

  caught_json="[]"
  if [ "${#caught[@]}" -gt 0 ]; then
    caught_json="["
    for i in "${!caught[@]}"; do
      [ "$i" -gt 0 ] && caught_json+=","
      caught_json+="\"$(json_escape "${caught[$i]}")\""
    done
    caught_json+="]"
  fi

  feature_json="null"
  [ -n "$agg_feature" ] && feature_json="\"$(json_escape "$agg_feature")\""
  final_warn_ack_required=false
  if [ "$verdict" = "WARN" ] && [ "$warn_ack_required" = true ]; then
    final_warn_ack_required=true
  fi

  ledger_written=false
  if [ "$LEDGER" = true ] && [ -n "$step" ]; then
    mkdir -p .specify
    artifacts_json="["
    afirst=true
    for f in ${INPUTS[@]+"${INPUTS[@]}"}; do
      $afirst || artifacts_json+=","
      afirst=false
      artifacts_json+="\"$(json_escape "$f")\""
    done
    artifacts_json+="]"
    shas_json="["
    sfirst=true
    for s in ${REPORT_SHAS[@]+"${REPORT_SHAS[@]}"}; do
      $sfirst || shas_json+=","
      sfirst=false
      shas_json+="\"$(json_escape "$s")\""
    done
    shas_json+="]"
    # This ledger line IS the persisted receipt (§7): verdict, verbatim caught
    # rows, cap, round, and the report files' content hashes — append-only.
    ledger_line="{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"cycle\":\"${cycle}\",\"feature\":${feature_json},\"step\":\"${step}\",\"verdict\":\"${verdict}\",\"round\":${ROUND},\"artifacts\":${artifacts_json},\"report_shas\":${shas_json}"
    if [ "$STATION" = "verify" ] || [ "$STATION" = "analyze" ] || [ "$STATION" = "review" ]; then
      ledger_line+=",\"audit_tier\":\"$(json_escape "$audit_tier")\",\"tier_receipt_sha256\":\"$(json_escape "$tier_receipt_sha")\",\"policy_hash\":\"$(json_escape "$tier_policy_hash")\""
      if [ "$final_warn_ack_required" = true ]; then
        ledger_line+=",\"warn_ack_required\":true,\"warn_ack_satisfied\":${warn_ack_satisfied}"
      fi
    fi
    if [ "$verdict" != "PASS" ]; then
      ledger_line+=",\"caught\":${caught_json}"
      [ "$cap_json" != "null" ] && ledger_line+=",\"cap\":${cap_json}"
    fi
    [ "$reversal_present" = true ] && ledger_line+=",\"reversal\":true"
    [ "$coverage_breach_present" = true ] && ledger_line+=",\"coverage_breach\":true"
    ledger_line+="}"
    printf '%s\n' "$ledger_line" >> .specify/specter-run.jsonl
    ledger_written=true
  fi

  cat <<JSON
{
  "mode": "aggregate",
  "station": "$(json_escape "$STATION")",
  "feature": ${feature_json},
  "round": ${ROUND},
  "audit_tier": "$(json_escape "$audit_tier")",
  "tier_receipt_sha256": "$(json_escape "$tier_receipt_sha")",
  "policy_hash": "$(json_escape "$tier_policy_hash")",
  "tier_settings": ${tier_settings_json},
  "inputs": ${inputs_json},
  "verdict": "${verdict}",
  "cap": ${cap_json},
  "warn_ack_required": ${final_warn_ack_required},
  "warn_ack_satisfied": ${warn_ack_satisfied},
  "reversal": ${reversal_present},
  "coverage_breach": ${coverage_breach_present},
  "caught": ${caught_json},
  "ledger_written": ${ledger_written},
  "reasons": $(reasons_to_json)
}
JSON
  exit 0
fi

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
feature_checklist_current_sha=""
codex_verify_exists=false
codex_verify_result=""
codex_verify_result_ok=false
codex_verify_feature_match=false
codex_verify_sha_ok=false
antigravity_verify_exists=false
antigravity_verify_result=""
antigravity_verify_result_ok=false
antigravity_verify_feature_match=false
antigravity_verify_sha_ok=false

if [ -n "$FEATURE" ]; then
  FEATURE_CHECKLIST="docs/prd/checklists/feature-${FEATURE}.checklist.md"
  CODEX_VERIFY="docs/prd/checklists/feature-${FEATURE}.codex-verify.md"
  ANTIGRAVITY_VERIFY="docs/prd/checklists/feature-${FEATURE}.antigravity-verify.md"

  if [ -f "$FEATURE_CHECKLIST" ]; then
    feature_checklist_exists=true
    feature_checklist_current_sha=$(sha256sum "$FEATURE_CHECKLIST" | awk '{print $1}')
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

  # Verify-report binding (2026-07-18 audit finding #3): a verify report must
  # name the requested Feature AND be hashed against the CURRENT checklist.
  # Without this, a stale PASS from an earlier checklist/Feature-Map revision
  # would satisfy the gate after the checklist was rewritten.
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
    codex_verify_feature_field=$(extract_field "$CODEX_VERIFY" "Feature")
    if [[ "$codex_verify_feature_field" == *"Feature ${FEATURE}"* ]] || [[ "$codex_verify_feature_field" == *"Feature ${FEATURE_RAW}"* ]]; then
      codex_verify_feature_match=true
    else
      add_reason "codex-verify Feature field '${codex_verify_feature_field:-missing}' does not match requested Feature ${FEATURE} (stale or reused report — re-run /ms.verify)"
      any_fail=true
    fi
    if $feature_checklist_exists; then
      codex_recorded_checklist_sha=$(extract_field "$CODEX_VERIFY" "Checklist SHA256")
      if [ -n "$codex_recorded_checklist_sha" ] && [ "$codex_recorded_checklist_sha" = "$feature_checklist_current_sha" ]; then
        codex_verify_sha_ok=true
      else
        add_reason "codex-verify Checklist SHA256 stale (recorded=${codex_recorded_checklist_sha:-none}, current=${feature_checklist_current_sha}) — re-run /ms.verify"
        any_fail=true
      fi
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
    antigravity_verify_feature_field=$(extract_field "$ANTIGRAVITY_VERIFY" "Feature")
    if [[ "$antigravity_verify_feature_field" == *"Feature ${FEATURE}"* ]] || [[ "$antigravity_verify_feature_field" == *"Feature ${FEATURE_RAW}"* ]]; then
      antigravity_verify_feature_match=true
    else
      add_reason "antigravity-verify Feature field '${antigravity_verify_feature_field:-missing}' does not match requested Feature ${FEATURE} (stale or reused report — re-run /ms.verify)"
      any_fail=true
    fi
    if $feature_checklist_exists; then
      antigravity_recorded_checklist_sha=$(extract_field "$ANTIGRAVITY_VERIFY" "Checklist SHA256")
      if [ -n "$antigravity_recorded_checklist_sha" ] && [ "$antigravity_recorded_checklist_sha" = "$feature_checklist_current_sha" ]; then
        antigravity_verify_sha_ok=true
      else
        add_reason "antigravity-verify Checklist SHA256 stale (recorded=${antigravity_recorded_checklist_sha:-none}, current=${feature_checklist_current_sha}) — re-run /ms.verify"
        any_fail=true
      fi
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
    "codex_verify_feature_match": ${codex_verify_feature_match},
    "codex_verify_sha_ok": ${codex_verify_sha_ok},
    "antigravity_verify_exists": ${antigravity_verify_exists},
    "antigravity_verify_result_ok": ${antigravity_verify_result_ok},
    "antigravity_verify_feature_match": ${antigravity_verify_feature_match},
    "antigravity_verify_sha_ok": ${antigravity_verify_sha_ok}
  },
  "overall": "${overall}",
  "reasons": ${reasons_json}
}
JSON

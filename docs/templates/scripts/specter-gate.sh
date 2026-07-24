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
#   specter-gate.sh aggregate <pre-verify|verify|analyze|review|expand> [arg] [--ledger] [--round N]
#                            # Layer-3 verdict aggregation over the STATION-FIXED
#                            # report set (the caller never picks input files).
#                            # --ledger also appends the .specify/specter-run.jsonl
#                            # line mechanically (verbatim caught quotes + cap);
#                            # --round N records the §4 convergence round.
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

GATE_VERSION="3.0.0"
GATE_CONTRACT="three-layer-v2-audit-tier"
AUDIT_TIER_CONTRACT="audit-tier-v1"

SUBCOMMAND="gate"
case "${1:-}" in
  version|structural|aggregate) SUBCOMMAND="$1"; shift ;;
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
  local file="$1" field="$2"
  grep -m1 "^\*\*${field}\*\*:" "$file" 2>/dev/null | sed -E "s/^\*\*${field}\*\*:[[:space:]]*//" || true
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

# ---- version subcommand ----

if [ "$SUBCOMMAND" = "version" ]; then
  cat <<JSON
{
  "version": "${GATE_VERSION}",
  "contract": "${GATE_CONTRACT}",
  "audit_tier_contract": "${AUDIT_TIER_CONTRACT}",
  "audit_tier_capability": "${AUDIT_CAPABILITY}",
  "subcommands": ["gate", "version", "structural", "aggregate"]
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
          for (i = 1; i <= n; i++) if (c[i] ~ /Owning Feature/) ocol = i
          next
        }
        rows++
        if (!ocol) ocol = 6
        owner = c[ocol]
        gsub(/^[ ]+|[ ]+$/, "", owner)
        # A commitment is "accounted for" if the owner column names a Feature
        # (incl. shared "Features 003/016" and markdown-emphasised "**Feature 018**")
        # OR an explicit, legitimate deferral marker (Post-MVP / out-of-scope /
        # unowned / future amendment). Only a blank or unlabelled owner is a real
        # gap. Do not reject legitimately-deferred rows or emphasised references.
        if (owner !~ /[Ff]eature[s]?[ ]*[*_]*[0-9]/ &&
            owner !~ /([Pp]ost-MVP|[Oo]ut of scope|[Nn]ot owned|[Dd]eferred|[Ff]uture[ ]+(PRD[ ]+)?amendment|[Nn]on-goal|[Nn]\/[Aa]|None)/) {
          print "F|index|commitment row has no owning Feature: " $0
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
      function check_oos(buf,   _dest) {
        # A self-contained scope statement with no routing arrow is fine (the map
        # uses arrow-less bullets to mean "nothing is deferred here").
        if (buf !~ /(→|->)/) return
        # With an arrow, the destination must be a Feature number (bare "→ 003",
        # "→ Feature 003", "→ **Feature 17**", "→ owned by Features 003/016") or a
        # sanctioned non-numeric destination keyword.
        _dest = (buf ~ /(→|->)[^0-9]*[0-9]/) || (buf ~ /(→|->).*([Ff]uture[ ]+(PRD[ ]+)?amendment|non-goal|[Ff]orbidden|permanent boundary|unchanged|[Dd]eferred|out of scope|this Feature|resolve in|None)/)
        if (!_dest)
          print "F|" sec "|out-of-scope item lacks destination: " buf
      }
      function flush() {
        if (!insec) return
        if (oosbuf != "") { check_oos(oosbuf); oosbuf = "" }
        n = split("### Source PRDs,### PRD references,### In scope,### Explicitly out of scope,### Key decisions,### Done criteria", req, ",")
        # Prefix match: a heading counts as present if any seen heading starts with
        # the required text, so a trailing annotation like
        # "### Key decisions (resolve in /ms.clarify)" is not a false "missing".
        for (i = 1; i <= n; i++) {
          hok = 0
          for (h in seen) if (index(h, req[i]) == 1) { hok = 1; break }
          if (!hok) print "F|" sec "|missing heading: " req[i]
        }
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
          lastdc = ""; subh = ""; oosbuf = ""
        } else insec = 0
        next
      }
      !insec { next }
      /^### / { if (oosbuf != "") { check_oos(oosbuf); oosbuf = "" } subh = $0; seen[$0] = 1; next }
      {
        # Standalone uppercase tokens only: a product/domain word like "Todo"
        # or an identifier like "TODOS_TABLE" is not a placeholder (2026-07-22
        # doit-n-live false positive).
        if ($0 ~ /(^|[^A-Za-z_])(TBD|TODO)([^A-Za-z_]|$)|\{\{/) {
          if (subh == "### Done criteria") print "F|" sec "|unresolved placeholder in done criteria: " $0
          else print "W|" sec "|unresolved placeholder: " $0
        }
        if (subh == "### Done criteria" && $0 ~ /^- /) lastdc = $0
        if (subh == "### Explicitly out of scope") {
          # Buffer multi-line bullets so a destination on a wrapped continuation
          # line (e.g. "→ owned by\n  Features 003/016") is still seen. A bullet
          # is one logical item spanning its "- " line plus indented continuations.
          # A destination may be a Feature (tolerating markdown emphasis/words) or
          # a sanctioned non-Feature destination (future amendment, non-goal,
          # forbidden, unchanged); check_oos() flags only a bullet with neither.
          if ($0 ~ /^- /) { if (oosbuf != "") check_oos(oosbuf); oosbuf = $0 }
          else if (oosbuf != "") oosbuf = oosbuf " " $0
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
  while [ $# -gt 0 ]; do
    case "$1" in
      --ledger) LEDGER=true ;;
      --round) shift; ROUND="${1:-1}" ;;
      *) [ -z "$ARG" ] && ARG="$1" ;;
    esac
    shift || true
  done
  [[ "$ROUND" =~ ^[0-9]+$ ]] || ROUND="1"

  verdict="PASS"
  INPUTS=()
  EXPECTED_MODES=()
  cycle=""
  step=""
  agg_feature=""
  sha_field=""
  sha_target=""
  feature_check=false
  audit_tier="T2"
  tier_receipt_sha=""
  tier_policy_hash=""
  tier_settings_json="null"
  warn_ack_required=false
  warn_ack_satisfied=false

  pad_feature() {
    if [[ "$1" =~ ^[0-9]+$ ]]; then printf '%03d' "$((10#$1))"; else printf '%s' "$1"; fi
  }

  # Legacy alias (pre-2026-07-19 rename): "agent-verify" was the per-Feature
  # station's old name; normalize it so half-synced callers fail loudly on
  # arg validation instead of silently hitting the wrong station.
  [ "$STATION" = "agent-verify" ] && STATION="verify"

  case "$STATION" in
    pre-verify)
      INPUTS=("docs/prd/feature-map.codex-verify.md" "docs/prd/feature-map.antigravity-checklist.md")
      EXPECTED_MODES=("codex-global-verify" "antigravity-global-verify")
      sha_field="Feature Map SHA256"; sha_target="docs/prd/feature-map.md"
      cycle="pre"; step="pre-verify"
      ;;
    verify)
      if ! [[ "$ARG" =~ ^[0-9]+$ ]]; then
        add_reason "station verify requires a numeric Feature number (got '${ARG:-<none>}')"; verdict="FAIL"
      else
        agg_feature=$(pad_feature "$ARG")
        INPUTS=("docs/prd/checklists/feature-${agg_feature}.codex-verify.md" "docs/prd/checklists/feature-${agg_feature}.antigravity-verify.md")
        EXPECTED_MODES=("codex-per-feature-verify" "antigravity-per-feature-verify")
        sha_field="Checklist SHA256"; sha_target="docs/prd/checklists/feature-${agg_feature}.checklist.md"
        feature_check=true
        cycle="feature"; step="verify"
      fi
      ;;
    analyze)
      # Spec dirs follow the NNN-name convention; requiring the numeric prefix
      # both blocks traversal fragments ("specs/..") and guarantees the
      # Feature-identity check is always enabled.
      if ! [[ "$ARG" =~ ^specs/[0-9]{3}-[A-Za-z0-9._-]+/?$ ]]; then
        add_reason "station analyze requires a spec directory of the form specs/NNN-name (got '${ARG:-<none>}')"; verdict="FAIL"
      else
        INPUTS=("${ARG%/}/analyze.codex.md" "${ARG%/}/analyze.antigravity.md")
        EXPECTED_MODES=("agent-document-consistency" "agent-document-consistency")
        sha_field="Tasks SHA256"; sha_target="${ARG%/}/tasks.md"
        base=$(basename "${ARG%/}")
        [[ "$base" =~ ^0*([0-9]+) ]] && agg_feature=$(pad_feature "${BASH_REMATCH[1]}") && feature_check=true
        cycle="feature"; step="analyze"
      fi
      ;;
    review)
      if ! [[ "$ARG" =~ ^[0-9]{3}-[A-Za-z0-9._-]+$ ]]; then
        add_reason "station review requires a spec id of the form NNN-name (got '${ARG:-<none>}')"; verdict="FAIL"
      else
        INPUTS=("docs/review/${ARG}.codex-review.md" "docs/review/${ARG}.antigravity-review.md")
        EXPECTED_MODES=("codex-adversarial-code-review" "antigravity-adversarial-code-review")
        # Agent reports bind to Feature identity; the mandatory audit-tier
        # receipt separately binds the tracked + untracked diff hash.
        [[ "$ARG" =~ ^0*([0-9]+) ]] && agg_feature=$(pad_feature "${BASH_REMATCH[1]}") && feature_check=true
        cycle="feature"; step="review"
      fi
      ;;
    expand)
      if ! [[ "$ARG" =~ ^[0-9]+$ ]]; then
        add_reason "station expand requires a numeric amendment number (got '${ARG:-<none>}')"; verdict="FAIL"
      else
        INPUTS=("docs/prd/feature-map.delta-${ARG}.antigravity-verify.md")
        EXPECTED_MODES=("antigravity-delta-verify")
        sha_field="Feature Map SHA256"; sha_target="docs/prd/feature-map.md"
        cycle="pre"; step="expand"
      fi
      ;;
    *)
      add_reason "unknown station '${STATION:-<none>}' (expected pre-verify|verify|analyze|review|expand)"
      verdict="FAIL"
      ;;
  esac

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

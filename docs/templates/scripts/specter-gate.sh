#!/usr/bin/env bash
# Deterministic SPECTER gate checker — verification-v2.
#
# Owns only mechanical facts: verdict lines, SHA256 equality, file existence,
# declared signals, deterministic diff facts. Content judgment (PRD fidelity,
# boundary discipline, severity) stays with the Layer-2 reviewers.
# Contract: docs/design/verification-v2.md. Config: verification-v2.json.
#
# Usage:
#   specter-gate.sh          # global gate only (legacy invocation, unchanged)
#   specter-gate.sh 006      # global gate + per-Feature gate for Feature 006
#   specter-gate.sh version  # capability probe (partially-synced projects fail clearly)
#   specter-gate.sh structural [NNN]
#                            # Layer-1 deterministic structure checks:
#                            # global = commitment-index ownership, DAG cycle,
#                            # required headings, CI-passes-green, placeholders,
#                            # Verification-signals schema; NNN adds checklist
#                            # placeholder + C-ID cross-refs
#   specter-gate.sh digest <pre-verify|verify|analyze|review|expand> [arg]
#                            # Compute the station's input digest (sha256 over
#                            # the fixed ordered path+hash list; review adds the
#                            # working-diff digest). The driver embeds it in
#                            # both reviewer prompts; aggregate recomputes it.
#   specter-gate.sh validate-report <path> <station> [arg] [--round N]
#                            # Deterministic report-format check (format-retry
#                            # lane, design §2.5): header fields, one Result,
#                            # required sections. Never grades semantics.
#   specter-gate.sh aggregate <pre-verify|verify|analyze|review|expand> [arg]
#                            [--ledger] [--round N] [--raise-risk]
#                            [--format-retries "N N"]
#                            # Layer-3 verdict aggregation over the STATION-FIXED
#                            # round-numbered report set (<base>.rN.md — the
#                            # caller never picks input files). Computes the
#                            # risk profile in-gate (declared signals + diff
#                            # facts; never prose scanning). Refuses --round 3+
#                            # without a recorded authorize-round decision.
#                            # Writes the station receipt
#                            # (.specify/verification-v2/<station>-<scope>.json);
#                            # --ledger appends the .specify/specter-run.jsonl
#                            # line mechanically (verbatim caught rows).
#   specter-gate.sh decide <type> <station> <scope> [--round N] [--actor A] --reason "..."
#                            # Append a typed human-decision event to the
#                            # ledger (ack-migration|ack-destructive|
#                            # ack-irreversible|ack-gate-policy|ack-degrade|
#                            # authorize-round|accept-warn|stop). Decisions can
#                            # never lower a verdict, effort, scope, or
#                            # reviewer count.
#
# Every mode prints one JSON object to stdout, even on malformed input.
# Legacy overall is one of: PASS | WARN | FAIL | MISSING.
# structural/aggregate emit "verdict": PASS | WARN | FAIL (no MISSING — a
# missing input at those layers is a FAIL by the three-layer contract).

set -euo pipefail

GATE_VERSION="4.0.0"
GATE_CONTRACT="verification-v2"

# Closed signal set (design §2.2 / verification-v2.json "signals" — the config
# is the versioned authority; this mirror exists so Layer 1 needs no python).
SIGNALS_RE='authorization|secrets|data-migration|destructive-data|irreversible-operation|public-contract|financial-or-regulated|gate-or-policy-change'

SUBCOMMAND="gate"
case "${1:-}" in
  version|structural|aggregate|digest|validate-report|decide) SUBCOMMAND="$1"; shift ;;
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
LEDGER_FILE=".specify/specter-run.jsonl"
RECEIPT_DIR=".specify/verification-v2"

REASONS=()
add_reason() { REASONS+=("$1"); }

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

# Config resolution: source-repo template first, installed runtime copy second.
V2_CONFIG=""
if [ -f "docs/templates/verification-v2.json" ]; then
  V2_CONFIG="docs/templates/verification-v2.json"
elif [ -f ".specify/policies/verification-v2.json" ]; then
  V2_CONFIG=".specify/policies/verification-v2.json"
fi

cfg_list() {
  # cfg_list <dot.path> -> newline list (array items or dict keys), "" on error
  [ -n "$V2_CONFIG" ] && [ -n "$PYTHON_BIN" ] || return 0
  "$PYTHON_BIN" - "$V2_CONFIG" "$1" <<'PY' 2>/dev/null || true
import json, sys
cur = json.load(open(sys.argv[1]))
for part in sys.argv[2].split('.'):
    cur = cur[part]
if isinstance(cur, list):
    print('\n'.join(str(x) for x in cur))
elif isinstance(cur, dict):
    print('\n'.join(cur.keys()))
else:
    print(cur)
PY
}

json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/ }"
  printf '%s' "$s"
}

extract_field() {
  # extract_field <file> <field-name>  ->  value after "**field-name**:"
  # BOTH sides trimmed: trailing whitespace (e.g. a Markdown hard-break) is
  # never semantic in these header fields.
  local file="$1" field="$2"
  grep -m1 "^\*\*${field}\*\*:" "$file" 2>/dev/null \
    | sed -E "s/^\*\*${field}\*\*:[[:space:]]*//; s/[[:space:]]+$//" || true
}

reasons_to_json() {
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
# Shared by aggregate/digest/validate-report so every mode sees the same
# STATION-FIXED input set (the caller never picks input files).
# Sets RS_* globals; RS_ERROR is non-empty on invalid input.
# RS_BASES are canonical report bases; the round-R file is <base%.md>.rR.md.
resolve_station() {
  local station="$1" arg="$2"
  RS_BASES=(); RS_MODES=(); RS_DIGEST_ARTIFACTS=(); RS_DIFF_IN_DIGEST=false
  RS_SCOPE=""; RS_SCOPE_LABEL=""; RS_CYCLE=""; RS_STEP=""; RS_FEATURE=""; RS_ERROR=""
  case "$station" in
    pre-verify)
      RS_BASES=("docs/prd/feature-map.codex-verify.md" "docs/prd/feature-map.antigravity-verify.md")
      RS_MODES=("codex-global-verify" "antigravity-global-verify")
      RS_DIGEST_ARTIFACTS=("docs/prd/feature-map.md" "$(resolve_baseline)")
      RS_SCOPE="global"; RS_SCOPE_LABEL="global"
      RS_CYCLE="pre"; RS_STEP="pre-verify"
      ;;
    verify)
      if ! [[ "$arg" =~ ^[0-9]+$ ]]; then
        RS_ERROR="station verify requires a numeric Feature number (got '${arg:-<none>}')"
      else
        RS_FEATURE=$(pad_feature "$arg")
        RS_BASES=("docs/prd/checklists/feature-${RS_FEATURE}.codex-verify.md" "docs/prd/checklists/feature-${RS_FEATURE}.antigravity-verify.md")
        RS_MODES=("codex-per-feature-verify" "antigravity-per-feature-verify")
        RS_DIGEST_ARTIFACTS=("docs/prd/feature-map.md" "docs/prd/checklists/feature-${RS_FEATURE}.checklist.md")
        RS_SCOPE="${RS_FEATURE}"; RS_SCOPE_LABEL="Feature ${RS_FEATURE}"
        RS_CYCLE="feature"; RS_STEP="verify"
      fi
      ;;
    analyze)
      # Spec dirs follow the NNN-name convention; requiring the numeric prefix
      # blocks traversal fragments and guarantees Feature identity.
      if ! [[ "$arg" =~ ^specs/[0-9]{3}-[A-Za-z0-9._-]+/?$ ]]; then
        RS_ERROR="station analyze requires a spec directory of the form specs/NNN-name (got '${arg:-<none>}')"
      else
        RS_BASES=("${arg%/}/analyze.codex.md" "${arg%/}/analyze.antigravity.md")
        RS_MODES=("agent-document-consistency" "agent-document-consistency")
        RS_DIGEST_ARTIFACTS=("docs/prd/feature-map.md" "${arg%/}/spec.md" "${arg%/}/plan.md" "${arg%/}/tasks.md")
        local base; base=$(basename "${arg%/}")
        [[ "$base" =~ ^0*([0-9]+) ]] && RS_FEATURE=$(pad_feature "${BASH_REMATCH[1]}")
        RS_SCOPE="${RS_FEATURE}"; RS_SCOPE_LABEL="Feature ${RS_FEATURE}"
        RS_CYCLE="feature"; RS_STEP="analyze"
      fi
      ;;
    review)
      if ! [[ "$arg" =~ ^[0-9]{3}-[A-Za-z0-9._-]+$ ]]; then
        RS_ERROR="station review requires a spec id of the form NNN-name (got '${arg:-<none>}')"
      else
        RS_BASES=("docs/review/${arg}.codex-review.md" "docs/review/${arg}.antigravity-review.md")
        RS_MODES=("codex-adversarial-code-review" "antigravity-adversarial-code-review")
        RS_DIGEST_ARTIFACTS=("docs/prd/feature-map.md")
        RS_DIFF_IN_DIGEST=true
        [[ "$arg" =~ ^0*([0-9]+) ]] && RS_FEATURE=$(pad_feature "${BASH_REMATCH[1]}")
        RS_SCOPE="${RS_FEATURE}"; RS_SCOPE_LABEL="Feature ${RS_FEATURE}"
        RS_CYCLE="feature"; RS_STEP="review"
      fi
      ;;
    expand)
      if ! [[ "$arg" =~ ^[0-9]+$ ]]; then
        RS_ERROR="station expand requires a numeric amendment number (got '${arg:-<none>}')"
      else
        RS_BASES=("docs/prd/feature-map.delta-${arg}.antigravity-verify.md")
        RS_MODES=("antigravity-delta-verify")
        RS_DIGEST_ARTIFACTS=("docs/prd/feature-map.md")
        RS_SCOPE="amendment-${arg}"; RS_SCOPE_LABEL="Amendment ${arg}"
        RS_CYCLE="pre"; RS_STEP="expand"
      fi
      ;;
    *)
      RS_ERROR="unknown station '${station:-<none>}' (expected pre-verify|verify|analyze|review|expand)"
      ;;
  esac
}

round_path() {
  # round_path <base.md> <round> -> base.rN.md
  printf '%s.r%s.md' "${1%.md}" "$2"
}

# ---- working-diff facts (review station; deterministic, changed files only) ----

DIFF_EXCLUDES=()
load_diff_excludes() {
  DIFF_EXCLUDES=()
  local p
  while IFS= read -r p; do
    [ -n "$p" ] && DIFF_EXCLUDES+=(":(exclude)${p}")
  done < <(cfg_list "diff_exclude_paths")
}

untracked_files() {
  # Untracked, non-excluded file paths, sorted (git porcelain ?? rows).
  local line p excl skip
  git status --porcelain=v1 -uall 2>/dev/null | while IFS= read -r line; do
    [ "${line:0:2}" = "??" ] || continue
    p="${line:3}"
    skip=false
    while IFS= read -r excl; do
      [ -n "$excl" ] || continue
      case "$p" in "$excl"*) skip=true; break ;; esac
    done < <(cfg_list "diff_exclude_paths")
    $skip || printf '%s\n' "$p"
  done | sort
}

diff_digest() {
  # sha256 over (tracked working diff vs HEAD) + (sorted untracked path=sha rows).
  load_diff_excludes
  {
    git diff --no-ext-diff HEAD -- . ${DIFF_EXCLUDES[@]+"${DIFF_EXCLUDES[@]}"} 2>/dev/null || true
    local p
    while IFS= read -r p; do
      [ -f "$p" ] && printf 'UNTRACKED %s %s\n' "$p" "$(sha256sum "$p" | awk '{print $1}')"
    done < <(untracked_files)
  } | sha256sum | awk '{print $1}'
}

changed_paths() {
  load_diff_excludes
  {
    git diff --name-only HEAD -- . ${DIFF_EXCLUDES[@]+"${DIFF_EXCLUDES[@]}"} 2>/dev/null || true
    untracked_files
  } | sed '/^$/d' | sort -u
}

added_content() {
  # Added lines of the tracked diff + full contents of untracked files.
  # Content rules apply ONLY here — never to spec/plan/tasks prose.
  load_diff_excludes
  git diff --no-ext-diff HEAD -- . ${DIFF_EXCLUDES[@]+"${DIFF_EXCLUDES[@]}"} 2>/dev/null \
    | grep '^+' | grep -v '^+++' || true
  local p
  while IFS= read -r p; do
    [ -f "$p" ] && cat "$p" 2>/dev/null
  done < <(untracked_files)
}

# ---- input digest (identity binding for every v2 report) ----

DIGEST_VALUE=""
DIGEST_ERROR=""
compute_digest() {
  # compute_digest — uses RS_* set by resolve_station.
  DIGEST_VALUE=""; DIGEST_ERROR=""
  local lines="" a
  for a in ${RS_DIGEST_ARTIFACTS[@]+"${RS_DIGEST_ARTIFACTS[@]}"}; do
    if [ ! -f "$a" ]; then
      DIGEST_ERROR="missing digest artifact: $a"
      return 0
    fi
    lines+="${a}=$(sha256sum "$a" | awk '{print $1}')"$'\n'
  done
  if [ "$RS_DIFF_IN_DIGEST" = true ]; then
    if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
      DIGEST_ERROR="review digest requires a git repository with at least one commit"
      return 0
    fi
    lines+="diff=$(diff_digest)"$'\n'
  fi
  DIGEST_VALUE=$(printf '%s' "$lines" | sha256sum | awk '{print $1}')
}

# ---- declared Verification signals (design §2.2) ----

signals_rows() {
  # signals_rows <feature-or-empty> -> "signal|value|evidence" rows from the
  # Feature section's (or, with empty arg, every section's)
  # "### Verification signals" table.
  local feature="$1"
  [ -f "$FEATURE_MAP" ] || return 0
  awk -v want="$feature" '
    /^## Feature [0-9]+:/ {
      insec = 0
      if (want == "") insec = 1
      else {
        sec = $0; sub(/^## Feature /, "", sec); sub(/:.*$/, "", sec)
        if (sec + 0 == want + 0) insec = 1
      }
      intab = 0; next
    }
    /^## / { insec = 0; intab = 0 }
    insec && /^### Verification signals[[:space:]]*$/ { intab = 1; next }
    insec && /^### / { intab = 0 }
    intab && /^\|/ {
      if ($0 ~ /^\|[-: |]+$/) next
      n = split($0, c, "|")
      for (i = 1; i <= n; i++) gsub(/^[ ]+|[ ]+$/, "", c[i])
      if (c[2] == "Signal") next
      print c[2] "|" c[3] "|" c[4]
    }' "$FEATURE_MAP"
}

feature_has_signals_table() {
  # feature_has_signals_table <feature> -> exit 0 iff the section carries the table
  local feature="$1"
  [ -f "$FEATURE_MAP" ] || return 1
  awk -v want="$feature" '
    /^## Feature [0-9]+:/ {
      insec = 0
      sec = $0; sub(/^## Feature /, "", sec); sub(/:.*$/, "", sec)
      if (sec + 0 == want + 0) insec = 1
      next
    }
    /^## / { insec = 0 }
    insec && /^### Verification signals[[:space:]]*$/ { found = 1 }
    END { exit found ? 0 : 1 }' "$FEATURE_MAP"
}

validate_signals_rows() {
  # validate_signals_rows <feature-or-empty> -> error lines (empty = valid)
  local row sig val ev
  while IFS='|' read -r sig val ev; do
    [ -n "$sig" ] || continue
    if ! [[ "$sig" =~ ^(${SIGNALS_RE})$ ]]; then
      printf 'unknown Verification signal: %s\n' "$sig"
    fi
    if [ "$val" != "yes" ] && [ "$val" != "no" ]; then
      printf 'Verification signal %s has invalid value "%s" (expected yes|no)\n' "$sig" "$val"
    fi
    if [ -z "$ev" ]; then
      printf 'Verification signal %s has empty evidence\n' "$sig"
    fi
  done < <(signals_rows "$1")
}

# ---- risk profile (in-gate; declared signals + diff facts; never prose) ----

RISK_PROFILE="ordinary"
RISK_EVIDENCE=()   # entries: "signal|source"
compute_risk_profile() {
  # compute_risk_profile <station> — uses RS_FEATURE.
  local station="$1" sig val ev cls pat
  RISK_PROFILE="ordinary"; RISK_EVIDENCE=()

  case "$station" in
    verify|analyze|review)
      if ! feature_has_signals_table "$RS_FEATURE"; then
        # Legacy Feature without the table: fail-safe high-risk for this one
        # re-check; the Feature must gain the table (design §2.2).
        RISK_PROFILE="high-risk"
        RISK_EVIDENCE+=("legacy-missing-signals-table|docs/prd/feature-map.md Feature ${RS_FEATURE}")
      else
        local sig_errors
        sig_errors=$(validate_signals_rows "$RS_FEATURE")
        if [ -n "$sig_errors" ]; then
          RISK_PROFILE="high-risk"
          RISK_EVIDENCE+=("malformed-signals-table|${sig_errors%%$'\n'*}")
        fi
        while IFS='|' read -r sig val ev; do
          [ "$val" = "yes" ] || continue
          RISK_PROFILE="high-risk"
          RISK_EVIDENCE+=("${sig}|${ev:-feature-map}")
        done < <(signals_rows "$RS_FEATURE")
      fi
      ;;
    pre-verify)
      while IFS='|' read -r sig val ev; do
        [ "$val" = "yes" ] || continue
        RISK_PROFILE="high-risk"
        RISK_EVIDENCE+=("${sig}|${ev:-feature-map}")
      done < <(signals_rows "")
      ;;
    expand)
      : # single-agent delta station stays ordinary; pre-verify covers the map
      ;;
  esac

  # Observed diff facts (review only): file-level paths + added-line content.
  if [ "$station" = "review" ] && git rev-parse --verify HEAD >/dev/null 2>&1; then
    local files added
    files=$(changed_paths)
    added=$(added_content)
    while IFS= read -r cls; do
      [ -n "$cls" ] || continue
      while IFS= read -r pat; do
        [ -n "$pat" ] || continue
        local hit
        hit=$(printf '%s\n' "$files" | grep -E -m1 -- "$pat" || true)
        if [ -n "$hit" ]; then
          RISK_PROFILE="high-risk"
          RISK_EVIDENCE+=("${cls}|path:${hit}")
          break
        fi
      done < <(cfg_list "diff_path_classes.${cls}")
    done < <(cfg_list "diff_path_classes")
    while IFS= read -r cls; do
      [ -n "$cls" ] || continue
      while IFS= read -r pat; do
        [ -n "$pat" ] || continue
        if printf '%s\n' "$added" | grep -Eq -- "$pat"; then
          RISK_PROFILE="high-risk"
          RISK_EVIDENCE+=("${cls}|content:added-lines")
          break
        fi
      done < <(cfg_list "diff_content_classes.${cls}")
    done < <(cfg_list "diff_content_classes")
  fi
}

risk_evidence_json() {
  local out="[]" i entry
  if [ "${#RISK_EVIDENCE[@]}" -gt 0 ]; then
    out="["
    for i in "${!RISK_EVIDENCE[@]}"; do
      entry="${RISK_EVIDENCE[$i]}"
      [ "$i" -gt 0 ] && out+=","
      out+="{\"signal\":\"$(json_escape "${entry%%|*}")\",\"source\":\"$(json_escape "${entry#*|}")\"}"
    done
    out+="]"
  fi
  printf '%s' "$out"
}

# ---- ledger decision lookup ----

decision_recorded() {
  # decision_recorded <decision> <station> <scope> [round]
  local decision="$1" station="$2" scope="$3" round="${4:-}"
  [ -f "$LEDGER_FILE" ] || return 1
  local pat="\"type\":\"decision\".*\"decision\":\"${decision}\".*\"station\":\"${station}\".*\"scope\":\"${scope}\""
  if [ -n "$round" ]; then
    grep -E "$pat" "$LEDGER_FILE" 2>/dev/null | grep -q "\"round\":${round}[,}]"
  else
    grep -Eq "$pat" "$LEDGER_FILE" 2>/dev/null
  fi
}

# ---- version subcommand ----

if [ "$SUBCOMMAND" = "version" ]; then
  config_json="null"
  [ -n "$V2_CONFIG" ] && config_json="\"$(json_escape "$V2_CONFIG")\""
  cat <<JSON
{
  "version": "${GATE_VERSION}",
  "contract": "${GATE_CONTRACT}",
  "config": ${config_json},
  "subcommands": ["gate", "version", "structural", "digest", "validate-report", "aggregate", "decide"]
}
JSON
  exit 0
fi

# ---- structural subcommand (Layer 1: deterministic structure only) ----
# Judges shape, never semantics: whether the PRD was actually understood is
# Layer 2's job.

if [ "$SUBCOMMAND" = "structural" ]; then
  MAP="docs/prd/feature-map.md"
  PROGRESS="docs/prd/feature-map.progress.md"
  CODEX_PRD_CHECKLIST="docs/prd/featuremap-checklist.md"
  [ -f "$CODEX_PRD_CHECKLIST" ] || CODEX_PRD_CHECKLIST="docs/prd/codex/checklist.md"

  verdict="PASS"
  index_ok=true
  features_ok=true
  dag_ok=true
  placeholders_ok=true
  checklist_refs_ok=true
  signals_ok=true
  obligations_ok=true

  note() {
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
          for (i = 1; i <= n; i++) if (c[i] ~ /Owning Feature/) ocol = i
          next
        }
        rows++
        if (!ocol) ocol = 6
        owner = c[ocol]
        gsub(/^[ ]+|[ ]+$/, "", owner)
        if (owner !~ /^Feature [0-9]+$/) {
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
        # or an identifier like "TODOS_TABLE" is not a placeholder.
        if ($0 ~ /(^|[^A-Za-z_])(TBD|TODO)([^A-Za-z_]|$)|\{\{/) {
          if (subh == "### Done criteria") print "F|" sec "|unresolved placeholder in done criteria: " $0
          else print "W|" sec "|unresolved placeholder: " $0
        }
        if (subh == "### Done criteria" && $0 ~ /^- /) lastdc = $0
        if (subh == "### Explicitly out of scope" && $0 ~ /^- /) {
          if ($0 !~ /(→|->)[ ]*(Feature[ ]*)?[0-9]+/ && $0 !~ /None/)
            print "F|" sec "|out-of-scope item lacks destination Feature: " $0
        }
      }
      END { flush() }' "$MAP")

    if [ -n "$FEATURE" ] && ! grep -q "^## Feature ${FEATURE}:" "$MAP"; then
      features_ok=false
      note F "Feature ${FEATURE} section not found in $MAP"
    fi

    # Verification signals (v2, design §2.2): the table is optional — a
    # Feature without it runs high-risk until it gains one — but a present
    # table must satisfy the closed schema. Validated in-gate; no external
    # classifier process exists in v2.
    while IFS= read -r err; do
      [ -n "$err" ] || continue
      signals_ok=false
      note F "$err"
    done < <(validate_signals_rows "$FEATURE")

    # Implementation Obligations (D-IDs): the section is optional and rows are
    # references, never product authority (design §0 D3). A present section
    # must satisfy the closed shape; referential integrity only.
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
    "verification_signals_ok": ${signals_ok},
    "implementation_obligations_ok": ${obligations_ok}
  },
  "verdict": "${verdict}",
  "reasons": $(reasons_to_json)
}
JSON
  exit 0
fi

# ---- digest subcommand ----

if [ "$SUBCOMMAND" = "digest" ]; then
  STATION="${1:-}"; ARG="${2:-}"
  resolve_station "$STATION" "$ARG"
  verdict="PASS"
  if [ -n "$RS_ERROR" ]; then
    add_reason "$RS_ERROR"; verdict="FAIL"
  else
    compute_digest
    if [ -n "$DIGEST_ERROR" ]; then
      add_reason "$DIGEST_ERROR"; verdict="FAIL"
    fi
  fi
  artifacts_json="["
  afirst=true
  for a in ${RS_DIGEST_ARTIFACTS[@]+"${RS_DIGEST_ARTIFACTS[@]}"}; do
    $afirst || artifacts_json+=","
    afirst=false
    artifacts_json+="\"$(json_escape "$a")\""
  done
  [ "${RS_DIFF_IN_DIGEST:-false}" = true ] && { $afirst || artifacts_json+=","; artifacts_json+="\"<working-diff>\""; }
  artifacts_json+="]"
  cat <<JSON
{
  "mode": "digest",
  "station": "$(json_escape "$STATION")",
  "scope": "$(json_escape "${RS_SCOPE:-}")",
  "artifacts": ${artifacts_json},
  "input_digest": "$(json_escape "$DIGEST_VALUE")",
  "verdict": "${verdict}",
  "reasons": $(reasons_to_json)
}
JSON
  exit 0
fi

# ---- validate-report subcommand (format-retry lane, design §2.5) ----

if [ "$SUBCOMMAND" = "validate-report" ]; then
  RPT="${1:-}"; STATION="${2:-}"; shift 2 || true
  ARG=""
  ROUND="1"
  while [ $# -gt 0 ]; do
    case "$1" in
      --round) shift; ROUND="${1:-1}" ;;
      *) [ -z "$ARG" ] && ARG="$1" ;;
    esac
    shift || true
  done
  [[ "$ROUND" =~ ^[0-9]+$ ]] || ROUND="1"

  errors=()
  add_err() { errors+=("$1"); }

  resolve_station "$STATION" "$ARG"
  expected_mode=""
  if [ -n "$RS_ERROR" ]; then
    add_err "$RS_ERROR"
  else
    # Which lane is this file? Match against the station's round paths.
    idx=0; lane=-1
    for b in ${RS_BASES[@]+"${RS_BASES[@]}"}; do
      [ "$RPT" = "$(round_path "$b" "$ROUND")" ] && lane=$idx
      idx=$((idx + 1))
    done
    if [ "$lane" -ge 0 ]; then
      expected_mode="${RS_MODES[$lane]}"
    else
      add_err "path is not a station report for ${STATION} round ${ROUND}: ${RPT}"
    fi
  fi

  if [ ! -s "$RPT" ]; then
    add_err "missing or empty report: ${RPT}"
  else
    in_contract=$(extract_field "$RPT" "Contract")
    in_mode=$(extract_field "$RPT" "Mode")
    in_scope=$(extract_field "$RPT" "Scope")
    in_digest=$(extract_field "$RPT" "Input Digest")
    in_avail=$(extract_field "$RPT" "Availability")
    result_count=$(grep -c '^\*\*Result\*\*:' "$RPT" || true)
    in_result=$(extract_field "$RPT" "Result")

    [ "$in_contract" = "$GATE_CONTRACT" ] || add_err "Contract is '${in_contract:-missing}', expected ${GATE_CONTRACT}"
    if [ -n "$expected_mode" ] && [ "$in_mode" != "$expected_mode" ]; then
      add_err "Mode '${in_mode:-missing}' does not match station mode '${expected_mode}'"
    fi
    [ "$result_count" -eq 1 ] || add_err "expected exactly one Result line (found ${result_count})"
    case "$in_result" in PASS|WARN|FAIL) : ;; *) add_err "invalid Result '${in_result:-missing}'" ;; esac
    [ -n "$in_digest" ] || add_err "missing Input Digest field"
    if [ -n "$RS_SCOPE_LABEL" ]; then
      scope_ok=false
      if [ "$RS_SCOPE_LABEL" = "global" ]; then
        [ "$in_scope" = "global" ] && scope_ok=true
      elif [[ "$RS_SCOPE_LABEL" =~ ^Feature\ 0*([0-9]+)$ ]]; then
        fnum="${BASH_REMATCH[1]}"
        [[ "$in_scope" =~ ^Feature\ 0*${fnum}$ ]] && scope_ok=true
      else
        [ "$in_scope" = "$RS_SCOPE_LABEL" ] && scope_ok=true
      fi
      $scope_ok || add_err "Scope '${in_scope:-missing}' does not match station scope '${RS_SCOPE_LABEL}'"
    fi

    is_placeholder=false
    [[ "$in_avail" =~ ^(UNAVAILABLE|RECUSED) ]] && is_placeholder=true
    if [ "$is_placeholder" = false ]; then
      grep -q '^\*\*Checked\*\*:' "$RPT" || add_err "missing non-empty **Checked** line (Scope and evidence section)"
      grep -q '^\*\*Not checked\*\*:' "$RPT" || add_err "missing non-empty **Not checked** line (Scope and evidence section)"
      grep -q '^## Findings' "$RPT" || add_err "missing ## Findings section"
      # Findings rows, when present, must parse as 6-cell table rows.
      while IFS= read -r frow; do
        [ -n "$frow" ] || continue
        cells=$(awk -F'|' '{print NF}' <<<"$frow")
        if [ "$cells" -lt 8 ]; then
          add_err "findings row does not have 6 columns (ID|Severity|State|Finding|Evidence|Required Fix): ${frow:0:80}"
          break
        fi
      done < <(awk '/^## Findings/{f=1;next} /^## /{f=0} f && /^\|/ && $0 !~ /^\|[-: |]+$/ && $0 !~ /\| *ID *\|/ {print}' "$RPT")
    fi
  fi

  valid=true
  [ "${#errors[@]}" -gt 0 ] && valid=false
  errors_json="[]"
  if [ "${#errors[@]}" -gt 0 ]; then
    errors_json="["
    for i in "${!errors[@]}"; do
      [ "$i" -gt 0 ] && errors_json+=","
      errors_json+="\"$(json_escape "${errors[$i]}")\""
    done
    errors_json+="]"
  fi
  cat <<JSON
{
  "mode": "validate-report",
  "path": "$(json_escape "$RPT")",
  "station": "$(json_escape "$STATION")",
  "round": ${ROUND},
  "valid": ${valid},
  "errors": ${errors_json}
}
JSON
  exit 0
fi

# ---- decide subcommand (typed human-decision ledger events, design §2.6) ----

if [ "$SUBCOMMAND" = "decide" ]; then
  DTYPE="${1:-}"; DSTATION="${2:-}"; DSCOPE="${3:-}"; shift 3 || true
  DROUND=""; DACTOR="human"; DREASON=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --round) shift; DROUND="${1:-}" ;;
      --actor) shift; DACTOR="${1:-human}" ;;
      --reason) shift; DREASON="${1:-}" ;;
    esac
    shift || true
  done

  verdict="PASS"
  valid_types="ack-migration ack-destructive ack-irreversible ack-gate-policy ack-degrade authorize-round accept-warn stop"
  case " $valid_types " in
    *" $DTYPE "*) : ;;
    *) add_reason "unknown decision type '${DTYPE:-<none>}' (expected one of: ${valid_types// /|})"; verdict="FAIL" ;;
  esac
  [ -n "$DSTATION" ] || { add_reason "decide requires a station"; verdict="FAIL"; }
  [ -n "$DSCOPE" ] || { add_reason "decide requires a scope"; verdict="FAIL"; }
  [ -n "$DREASON" ] || { add_reason "decide requires --reason (decisions are recorded with their rationale)"; verdict="FAIL"; }
  if [ "$DTYPE" = "authorize-round" ] && ! [[ "$DROUND" =~ ^[0-9]+$ ]]; then
    add_reason "authorize-round requires --round N"; verdict="FAIL"
  fi

  event_written=false
  if [ "$verdict" = "PASS" ]; then
    mkdir -p .specify
    receipt_sha=""
    receipt_file="${RECEIPT_DIR}/${DSTATION}-${DSCOPE}.json"
    [ -f "$receipt_file" ] && receipt_sha=$(sha256sum "$receipt_file" | awk '{print $1}')
    event="{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"type\":\"decision\",\"decision\":\"${DTYPE}\",\"station\":\"$(json_escape "$DSTATION")\",\"scope\":\"$(json_escape "$DSCOPE")\""
    [ -n "$DROUND" ] && event+=",\"round\":${DROUND}"
    event+=",\"actor\":\"$(json_escape "$DACTOR")\",\"reason\":\"$(json_escape "$DREASON")\",\"receipt_sha256\":\"$(json_escape "$receipt_sha")\"}"
    printf '%s\n' "$event" >> "$LEDGER_FILE"
    event_written=true
  fi

  cat <<JSON
{
  "mode": "decide",
  "decision": "$(json_escape "$DTYPE")",
  "station": "$(json_escape "$DSTATION")",
  "scope": "$(json_escape "$DSCOPE")",
  "round": ${DROUND:-null},
  "actor": "$(json_escape "$DACTOR")",
  "event_written": ${event_written},
  "verdict": "${verdict}",
  "reasons": $(reasons_to_json)
}
JSON
  exit 0
fi

# ---- aggregate subcommand (Layer 3: mechanical verdict aggregation) ----
# The station name fixes the report set; the caller can never add, omit, or
# reorder inputs (dynamic input choice would let a failing report simply be
# left out).

if [ "$SUBCOMMAND" = "aggregate" ]; then
  STATION="${1:-}"
  shift || true
  ARG=""
  LEDGER=false
  ROUND="1"
  RAISE_RISK=false
  FORMAT_RETRIES=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --ledger) LEDGER=true ;;
      --round) shift; ROUND="${1:-1}" ;;
      --raise-risk) RAISE_RISK=true ;;
      --format-retries) shift; FORMAT_RETRIES="${1:-}" ;;
      *) [ -z "$ARG" ] && ARG="$1" ;;
    esac
    shift || true
  done
  [[ "$ROUND" =~ ^[0-9]+$ ]] || ROUND="1"

  verdict="PASS"

  resolve_station "$STATION" "$ARG"
  if [ -n "$RS_ERROR" ]; then
    add_reason "$RS_ERROR"; verdict="FAIL"
  fi

  # Partial-sync fail-fast: the v2 config is part of the atomic capability.
  if [ -z "$V2_CONFIG" ] || [ -z "$PYTHON_BIN" ]; then
    add_reason "verification-v2 config or python runtime unavailable — partial sync; run /ms.sync (or /ms.init)"
    verdict="FAIL"
  fi

  # Executable round budget (design §2.4): rounds 1-2 are the entire automatic
  # budget; round 3+ requires a recorded authorize-round decision — checked
  # BEFORE any report is read, so an over-cap round spends nothing.
  AUTOMATIC_ROUNDS=2
  budget=$(cfg_list "round_budget.automatic_rounds")
  [[ "$budget" =~ ^[0-9]+$ ]] && AUTOMATIC_ROUNDS="$budget"
  if [ "$verdict" != "FAIL" ] && [ "$ROUND" -gt "$AUTOMATIC_ROUNDS" ]; then
    if ! decision_recorded "authorize-round" "$STATION" "$RS_SCOPE" "$ROUND"; then
      add_reason "round ${ROUND} exceeds the automatic budget (${AUTOMATIC_ROUNDS}) and no authorize-round decision is recorded for ${STATION}/${RS_SCOPE} round ${ROUND} — the post-cap options are: fix and restart with a new input digest / amend the PRD authority / authorize one doctrine-dispute round (specter-gate.sh decide authorize-round ...) / accept WARN / stop"
      verdict="FAIL"
      cat <<JSON
{
  "mode": "aggregate",
  "station": "$(json_escape "$STATION")",
  "scope": "$(json_escape "${RS_SCOPE:-}")",
  "round": ${ROUND},
  "verdict": "FAIL",
  "over_budget": true,
  "reasons": $(reasons_to_json)
}
JSON
      exit 0
    fi
    add_reason "round ${ROUND} runs under a recorded authorize-round decision"
  fi

  cycle="$RS_CYCLE"
  step="$RS_STEP"
  agg_feature="$RS_FEATURE"

  # Input digest + risk profile — both computed in-gate, from current inputs.
  DIGEST_VALUE=""; DIGEST_ERROR=""
  if [ "$verdict" != "FAIL" ] || [ -z "$RS_ERROR" ]; then
    compute_digest
    if [ -n "$DIGEST_ERROR" ]; then
      add_reason "$DIGEST_ERROR"
      verdict="FAIL"
    fi
    compute_risk_profile "$STATION"
    if [ "$RAISE_RISK" = true ] && [ "$RISK_PROFILE" != "high-risk" ]; then
      RISK_PROFILE="high-risk"
      RISK_EVIDENCE+=("manual-raise|--raise-risk")
    fi
  fi

  inputs_json="["
  cap_agents=()
  caught=()
  REPORT_SHAS=()
  first=true
  idx=0

  for base in ${RS_BASES[@]+"${RS_BASES[@]}"}; do
    f=$(round_path "$base" "$ROUND")
    in_result=""
    in_avail=""
    in_sha=""
    in_verdict="FAIL"
    expected_mode="${RS_MODES[$idx]:-}"
    fmt_retry="0"
    if [ -n "$FORMAT_RETRIES" ]; then
      fmt_retry=$(awk -v n=$((idx + 1)) '{print $n}' <<<"$FORMAT_RETRIES" 2>/dev/null || printf '0')
      [[ "$fmt_retry" =~ ^[0-9]+$ ]] || fmt_retry="0"
    fi
    idx=$((idx + 1))

    if [ ! -s "$f" ]; then
      REPORT_SHAS+=("")
      add_reason "missing or empty report: $f"
    else
      in_sha=$(sha256sum "$f" | awk '{print $1}')
      REPORT_SHAS+=("$in_sha")
      in_contract=$(extract_field "$f" "Contract")
      in_mode=$(extract_field "$f" "Mode")
      in_scope=$(extract_field "$f" "Scope")
      in_digest=$(extract_field "$f" "Input Digest")
      result_count=$(grep -c '^\*\*Result\*\*:' "$f" || true)
      in_result=$(extract_field "$f" "Result")
      in_avail=$(extract_field "$f" "Availability")
      structural_ok=true
      if [ "$in_contract" != "$GATE_CONTRACT" ]; then
        structural_ok=false
        add_reason "report Contract '${in_contract:-missing}' is not ${GATE_CONTRACT}: $f"
      elif [ -n "$expected_mode" ] && [ "$in_mode" != "$expected_mode" ]; then
        # A report from the wrong station (or with no Mode) must never grade
        # this station — degrade placeholders carry the normal Mode too.
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
      # included — a stale or mis-scoped placeholder must not become an
      # accepted cap.
      if [ "$structural_ok" = true ] && [ -n "$RS_SCOPE_LABEL" ]; then
        scope_ok=false
        if [ "$RS_SCOPE_LABEL" = "global" ]; then
          [ "$in_scope" = "global" ] && scope_ok=true
        elif [[ "$RS_SCOPE_LABEL" =~ ^Feature\ 0*([0-9]+)$ ]]; then
          fnum="${BASH_REMATCH[1]}"
          [[ "$in_scope" =~ ^Feature\ 0*${fnum}$ ]] && scope_ok=true
        else
          [ "$in_scope" = "$RS_SCOPE_LABEL" ] && scope_ok=true
        fi
        if [ "$scope_ok" = false ]; then
          structural_ok=false
          add_reason "report Scope '${in_scope:-missing}' does not match station scope '${RS_SCOPE_LABEL}' (stale or reused report): $f"
        fi
      fi
      if [ "$structural_ok" = true ]; then
        if [ -z "$in_digest" ] || [ "$in_digest" != "$DIGEST_VALUE" ]; then
          structural_ok=false
          add_reason "stale Input Digest in $f (recorded=${in_digest:-none}, current=${DIGEST_VALUE}) — the audited artifacts changed; re-run the round"
        fi
      fi
      if [ "$structural_ok" = true ]; then
        if [ -n "$in_avail" ] && [[ ! "$in_avail" =~ ^PRESENT ]]; then
          # Typed degrade placeholder: only WARN + UNAVAILABLE/RECUSED is
          # environmental; anything else is an agent-authored failure -> FAIL.
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
            done < <(awk '/^## Findings/ { f = 1; next } /^## / { f = 0 } f && /^\|/ && $0 !~ /^\|[-: |]+$/ && $0 !~ /\| *ID *\|/ { print }' "$f")
          fi
        fi
      fi
    fi

    verdict=$(worse "$verdict" "$in_verdict")
    $first || inputs_json+=","
    first=false
    inputs_json+="{\"path\":\"$(json_escape "$f")\",\"sha256\":\"$(json_escape "$in_sha")\",\"result\":\"$(json_escape "$in_result")\",\"availability\":\"$(json_escape "$in_avail")\",\"graded\":\"${in_verdict}\",\"format_retries\":${fmt_retry}}"
  done
  inputs_json+="]"

  # Zero independent verifiers left (every input is a degrade placeholder):
  # the station cannot produce a verdict — FAIL, never a host-only opinion.
  if [ "${#RS_BASES[@]}" -gt 0 ] && [ "${#cap_agents[@]}" -eq "${#RS_BASES[@]}" ]; then
    verdict="FAIL"
    add_reason "every agent report is a degrade placeholder — no independent verifier ran"
  fi

  # Expand-only: the delta checklist is this station's independent input
  # baseline; its absence is a mechanical WARN cap, never silently absorbed.
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

  # Named-class acknowledgments (design §2.6, review station only): report
  # which triggered risk classes require a decision event and whether one is
  # recorded. Mechanical report — the driving command enforces advancement.
  required_acks_json="[]"
  acks_satisfied=true
  if [ "$STATION" = "review" ] && [ "$RISK_PROFILE" = "high-risk" ]; then
    required_acks_json="["
    rfirst=true
    while IFS= read -r cls; do
      [ -n "$cls" ] || continue
      hitcls=false
      for entry in ${RISK_EVIDENCE[@]+"${RISK_EVIDENCE[@]}"}; do
        [ "${entry%%|*}" = "$cls" ] && hitcls=true
      done
      $hitcls || continue
      dtype=$(cfg_list "ack_required_classes.${cls}" | head -1)
      [ -n "$dtype" ] || continue
      sat=false
      decision_recorded "$dtype" "$STATION" "$RS_SCOPE" && sat=true
      $sat || acks_satisfied=false
      $rfirst || required_acks_json+=","
      rfirst=false
      required_acks_json+="{\"class\":\"$(json_escape "$cls")\",\"decision\":\"$(json_escape "$dtype")\",\"satisfied\":${sat}}"
    done < <(cfg_list "ack_required_classes")
    required_acks_json+="]"
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

  artifacts_json="["
  afirst=true
  for base in ${RS_BASES[@]+"${RS_BASES[@]}"}; do
    $afirst || artifacts_json+=","
    afirst=false
    artifacts_json+="\"$(json_escape "$(round_path "$base" "$ROUND")")\""
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

  receipt_json=$(cat <<JSON
{
  "contract": "${GATE_CONTRACT}",
  "mode": "aggregate",
  "station": "$(json_escape "$STATION")",
  "scope": "$(json_escape "${RS_SCOPE:-}")",
  "feature": ${feature_json},
  "round": ${ROUND},
  "automatic_round_cap": ${AUTOMATIC_ROUNDS},
  "risk_profile": "$(json_escape "$RISK_PROFILE")",
  "risk_evidence": $(risk_evidence_json),
  "input_digest": "$(json_escape "$DIGEST_VALUE")",
  "inputs": ${inputs_json},
  "verdict": "${verdict}",
  "cap": ${cap_json},
  "required_acks": ${required_acks_json},
  "acks_satisfied": ${acks_satisfied},
  "caught": ${caught_json},
  "reasons": $(reasons_to_json)
}
JSON
)

  # The receipt is the station's outcome of record for the CURRENT round;
  # history lives in the append-only ledger.
  receipt_written=false
  if [ -n "$RS_SCOPE" ]; then
    mkdir -p "$RECEIPT_DIR"
    printf '%s\n' "$receipt_json" > "${RECEIPT_DIR}/${STATION}-${RS_SCOPE}.json"
    receipt_written=true
  fi

  ledger_written=false
  if [ "$LEDGER" = true ] && [ -n "$step" ]; then
    mkdir -p .specify
    ledger_line="{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"contract\":\"${GATE_CONTRACT}\",\"cycle\":\"${cycle}\",\"feature\":${feature_json},\"step\":\"${step}\",\"scope\":\"$(json_escape "${RS_SCOPE:-}")\",\"verdict\":\"${verdict}\",\"round\":${ROUND},\"risk_profile\":\"$(json_escape "$RISK_PROFILE")\",\"input_digest\":\"$(json_escape "$DIGEST_VALUE")\",\"artifacts\":${artifacts_json},\"report_shas\":${shas_json}"
    if [ "$verdict" != "PASS" ]; then
      ledger_line+=",\"caught\":${caught_json}"
      [ "$cap_json" != "null" ] && ledger_line+=",\"cap\":${cap_json}"
    fi
    [ "$acks_satisfied" = false ] && ledger_line+=",\"acks_satisfied\":false"
    ledger_line+="}"
    printf '%s\n' "$ledger_line" >> "$LEDGER_FILE"
    ledger_written=true
  fi

  printf '%s\n' "$receipt_json" | sed '$d'
  cat <<JSON
  ,"receipt_written": ${receipt_written},
  "ledger_written": ${ledger_written}
}
JSON
  exit 0
fi

# ---- legacy gate subcommand (default): cheap precondition probe ----

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
verify_receipt_exists=false
verify_receipt_verdict=""
verify_receipt_verdict_ok=false
verify_receipt_fresh=false

if [ -n "$FEATURE" ]; then
  FEATURE_CHECKLIST="docs/prd/checklists/feature-${FEATURE}.checklist.md"

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
    # "**Feature Map**:" field; its recorded SHA256 must be checked against
    # that file, not against the master map.
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

  # Verify-station binding (v2): the station outcome of record is the verify
  # receipt, not the report files. Fresh = the receipt's input digest still
  # matches the current artifacts (a rewritten checklist invalidates it).
  VERIFY_RECEIPT="${RECEIPT_DIR}/verify-${FEATURE}.json"
  if [ -f "$VERIFY_RECEIPT" ]; then
    verify_receipt_exists=true
    if [ -n "$PYTHON_BIN" ]; then
      verify_receipt_verdict=$("$PYTHON_BIN" -c 'import json,sys; print(json.load(open(sys.argv[1])).get("verdict",""))' "$VERIFY_RECEIPT" 2>/dev/null || true)
      receipt_digest=$("$PYTHON_BIN" -c 'import json,sys; print(json.load(open(sys.argv[1])).get("input_digest",""))' "$VERIFY_RECEIPT" 2>/dev/null || true)
      if [ "$verify_receipt_verdict" = "PASS" ] || [ "$verify_receipt_verdict" = "WARN" ]; then
        verify_receipt_verdict_ok=true
        [ "$verify_receipt_verdict" = "WARN" ] && any_warn=true
      else
        add_reason "verify receipt verdict is '${verify_receipt_verdict:-missing}', expected PASS or WARN — re-run /ms.verify"
        any_fail=true
      fi
      resolve_station "verify" "$FEATURE"
      compute_digest
      if [ -z "$DIGEST_ERROR" ] && [ -n "$receipt_digest" ] && [ "$receipt_digest" = "$DIGEST_VALUE" ]; then
        verify_receipt_fresh=true
      else
        add_reason "verify receipt input digest stale (recorded=${receipt_digest:-none}, current=${DIGEST_VALUE:-unavailable}) — re-run /ms.verify"
        any_fail=true
      fi
    else
      add_reason "python runtime unavailable — verify receipt not readable"
      any_fail=true
    fi
  else
    add_reason "missing: $VERIFY_RECEIPT — /ms.verify has not aggregated for Feature ${FEATURE}"
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
    "verify_receipt_exists": ${verify_receipt_exists},
    "verify_receipt_verdict": "$(json_escape "$verify_receipt_verdict")",
    "verify_receipt_verdict_ok": ${verify_receipt_verdict_ok},
    "verify_receipt_fresh": ${verify_receipt_fresh}
  },
  "overall": "${overall}",
  "reasons": ${reasons_json:-$(reasons_to_json)}
}
JSON

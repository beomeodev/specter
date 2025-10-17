#!/bin/bash
# Prerequisites checker for My-Spec commands
# Usage: check-prerequisites.sh [OPTIONS]
#
# Options:
#   --json                Output in JSON format
#   --require-spec        Exit with error if spec.md not found
#   --require-plan        Exit with error if plan.md not found
#   --include-tasks       Include tasks.md in available docs check
#
# Exit codes:
#   0 - Success
#   1 - Required file not found
#   2 - Repository root not found

set -e

# Parse arguments
JSON_OUTPUT=false
REQUIRE_SPEC=false
REQUIRE_PLAN=false
INCLUDE_TASKS=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --json)
      JSON_OUTPUT=true
      shift
      ;;
    --require-spec)
      REQUIRE_SPEC=true
      shift
      ;;
    --require-plan)
      REQUIRE_PLAN=true
      shift
      ;;
    --include-tasks)
      INCLUDE_TASKS=true
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
  esac
done

# Find repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

if [ ! -d "$REPO_ROOT/.git" ] && [ ! -f "$REPO_ROOT/.git" ]; then
  if [ "$JSON_OUTPUT" = true ]; then
    echo '{"error": "Not a git repository", "REPO_ROOT": null}'
  else
    echo "ERROR: Not a git repository" >&2
  fi
  exit 2
fi

# Find feature directory (most recent spec directory)
FEATURE_DIR=$(find "$REPO_ROOT/specs" -maxdepth 1 -type d -name "*-spec" 2>/dev/null | sort -r | head -n1)

# If no feature directory found, try to find any directory with spec.md
if [ -z "$FEATURE_DIR" ]; then
  SPEC_FILE=$(find "$REPO_ROOT/specs" -name "spec.md" -type f 2>/dev/null | head -n1)
  if [ -n "$SPEC_FILE" ]; then
    FEATURE_DIR=$(dirname "$SPEC_FILE")
  fi
fi

# Check available documents
AVAILABLE_DOCS=()

if [ -n "$FEATURE_DIR" ]; then
  [ -f "$FEATURE_DIR/spec.md" ] && AVAILABLE_DOCS+=("spec.md")
  [ -f "$FEATURE_DIR/plan.md" ] && AVAILABLE_DOCS+=("plan.md")

  if [ "$INCLUDE_TASKS" = true ]; then
    [ -f "$FEATURE_DIR/tasks.md" ] && AVAILABLE_DOCS+=("tasks.md")
  fi
fi

# Check required files
if [ "$REQUIRE_SPEC" = true ] && [ ! -f "$FEATURE_DIR/spec.md" ]; then
  if [ "$JSON_OUTPUT" = true ]; then
    echo '{"error": "spec.md not found", "REPO_ROOT": "'"$REPO_ROOT"'", "FEATURE_DIR": "'"$FEATURE_DIR"'"}'
  else
    echo "ERROR: spec.md not found in $FEATURE_DIR" >&2
    echo "Run /ms.specify first" >&2
  fi
  exit 1
fi

if [ "$REQUIRE_PLAN" = true ] && [ ! -f "$FEATURE_DIR/plan.md" ]; then
  if [ "$JSON_OUTPUT" = true ]; then
    echo '{"error": "plan.md not found", "REPO_ROOT": "'"$REPO_ROOT"'", "FEATURE_DIR": "'"$FEATURE_DIR"'"}'
  else
    echo "ERROR: plan.md not found in $FEATURE_DIR" >&2
    echo "Run /ms.plan first" >&2
  fi
  exit 1
fi

# Output results
if [ "$JSON_OUTPUT" = true ]; then
  # Build JSON array of available docs
  if [ ${#AVAILABLE_DOCS[@]} -eq 0 ]; then
    DOCS_JSON=""
  else
    DOCS_JSON=$(printf '"%s",' "${AVAILABLE_DOCS[@]}" | sed 's/,$//')
  fi

  cat <<EOF
{
  "REPO_ROOT": "$REPO_ROOT",
  "FEATURE_DIR": "$FEATURE_DIR",
  "AVAILABLE_DOCS": [$DOCS_JSON]
}
EOF
else
  echo "REPO_ROOT=$REPO_ROOT"
  echo "FEATURE_DIR=$FEATURE_DIR"
  echo "AVAILABLE_DOCS=${AVAILABLE_DOCS[*]}"
fi

exit 0

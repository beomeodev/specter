---
description: "Generate tasks with automatic TAG ID generation"
argument-hint: "[task generation guidance]"
---

# /ms.tasks - Generate Tasks with TAG IDs

Extends `/speckit-tasks` to generate implementation tasks with automatic TAG ID assignment.

## Overview

**This command is a wrapper around `/speckit-tasks` with enhanced functionality.**

**Base Command**: `/speckit-tasks` - Generates implementation tasks from spec.md and plan.md

**Additional Features** (provided by `/ms.tasks`):
- Library/documentation pattern check when plan.md depends on current third-party APIs
- Automatic TAG ID generation for each Functional Requirement
- Domain extraction from FR titles (AUTH, USER, PAY, etc.)
- TAG anchor assignment (`@SPEC:{TAG_ID}` anchors in tasks.md; `@TEST`/`@CODE`
  anchors are inserted by `/ms.implement` in the real test/implementation files)
- Constitution-aware task breakdown (respects file size limits)
- Library-informed task structure (tasks reflect actual implementation patterns)

**Purpose**: Creates a detailed task breakdown with best-effort traceability support, ensuring each User Story has a unique TAG ID for the SPECTER workflow.

## Execution Steps

### 0. Load Project Context

**Auto-load project documents**:
- `.specify/memory/constitution.md` (Constitution - REQUIRED)
- `AGENTS.md` (AI instructions, coding standards - if exists)
- `specs/[spec-id]/spec.md` (Feature specification - REQUIRED)
- `specs/[spec-id]/plan.md` (Implementation plan - REQUIRED)

**Session read policy**: per AGENTS.md §2 — reuse files already read this session; a fresh `Read` immediately before `Edit`/`Write` is still required.

**IF Constitution, spec.md, or plan.md missing**:
- Display error: "Required files missing. Run `/ms.init`, `/ms.specify`, and `/ms.plan` first."
- Exit

**Reference for task generation**:
- Constitution Section VI (File, Architecture, And Tooling Governance - file size targets: ≤700 SLOC, ≤100 LOC/function)
- Constitution Section IX (Project-specific baseline established from the checked PRD Feature Map by `/ms.constitution`)
- AGENTS.md (coding standards, task organization patterns - if exists)

**These documents help**:
- Generate appropriate TAG domain names based on project structure
- Break down tasks according to file size limits
- Apply project-specific task organization patterns

### 1. Library Documentation Research (If Needed)

**Analyze plan.md**: Does implementation require external libraries or integrations?

**Detection indicators**:
- plan.md mentions library names (FastAPI, React, Stripe, Next.js, etc.)
- Integration with external services (OAuth, payment gateways, APIs)
- New third-party dependencies in technology stack

**IF external libraries detected**:

1. Identify required libraries, versions, and use cases.
2. Use available documentation tooling directly, preferring official docs.
3. Extract only task-shaping facts:
   - implementation sequence
   - file/module organization
   - testing strategy
   - common pitfalls or migration constraints
4. Store the verified library patterns for Step 2 task generation.

**ELSE**:
  → Skip (no external libraries)

Do not claim that a specific agent or model ran unless it actually did.

### 2. Run Base Command

**IMPORTANT**: `/ms.tasks` delegates core task generation to `/speckit-tasks`.

Execute `/speckit-tasks` to generate base task structure with verified planning context:

```
/speckit-tasks $ARGUMENTS
```

**What `/speckit-tasks` does** (base functionality):
- Analyzes spec.md and plan.md
- Generates task breakdown with phases
- Creates dependency graph
- Produces tasks.md file
- **Enhanced with verified context**: Tasks reflect checked project and library implementation patterns when relevant

**Output**: `specs/[spec-id]/tasks.md` with complete task structure (without TAG IDs yet)

### 3. TAG ID Generation (SPECTER Enhancement)

**This step is UNIQUE to `/ms.tasks`** - not provided by `/speckit-tasks`.

For each Functional Requirement (FR) in `spec.md`, assign exactly one TAG ID.
TAG IDs must be unique across the whole repository and within the newly generated
`tasks.md` file.

**Extract Domain**:

```bash
extract_domain() {
  local fr_title="$1"
  local fr_number="$2"

  # Match domain keywords. Keep fallback deterministic for unknown domains.
  echo "$fr_title" | rg -io '(auth|user|pay|cart|order|product|admin|notif|search|profile|api|db|ui|ops)' | head -n1 | tr '[:lower:]' '[:upper:]' \
    || echo "FR${fr_number}"
}
```

**Build Existing Domain Counters Once**:

Do not call `count + 1` independently for every FR. That creates duplicate IDs
when two new FRs share the same domain in a single `/ms.tasks` run. Instead,
scan existing TAGs once, initialize a per-domain counter, then increment that
counter in memory after each assignment.

```bash
declare -A TAG_NEXT

initialize_tag_counters() {
  # Existing SPEC tags are authoritative for requirement IDs. CODE/TEST may
  # appear multiple times for the same ID, so they are only a collision fallback.
  local existing_tags
  existing_tags=$(rg -o '@(SPEC|TEST|CODE):([A-Z][A-Z0-9-]*-[0-9]{3})' specs src tests backend frontend 2>/dev/null \
    | sed -E 's/.*:([A-Z][A-Z0-9-]*-[0-9]{3})/\1/' \
    | sort -u)

  while read -r tag; do
    [ -z "$tag" ] && continue
    local domain="${tag%-*}"
    local number="${tag##*-}"
    local next=$((10#$number + 1))
    if [ -z "${TAG_NEXT[$domain]}" ] || [ "$next" -gt "${TAG_NEXT[$domain]}" ]; then
      TAG_NEXT[$domain]=$next
    fi
  done <<< "$existing_tags"
}
```

**Generate TAG ID**:

```bash
generate_tag_id() {
  local domain="$1"
  local next="${TAG_NEXT[$domain]:-1}"
  local tag

  while :; do
    tag=$(printf "%s-%03d" "$domain" "$next")
    # Protect against existing repo tags and IDs already assigned earlier in
    # this same tasks generation pass.
    if ! rg -q "@(SPEC|TEST|CODE):${tag}\b|${tag}\b" specs src tests backend frontend 2>/dev/null \
       && ! printf '%s\n' "${NEW_TAG_IDS[@]}" | rg -q "^${tag}$"; then
      break
    fi
    next=$((next + 1))
  done

  TAG_NEXT[$domain]=$((next + 1))
  NEW_TAG_IDS+=("$tag")
  printf "%s" "$tag"
}

initialize_tag_counters
NEW_TAG_IDS=()

# Example within one run:
# FR-1 User Authentication -> AUTH-001
# FR-2 Session Authentication -> AUTH-002
# FR-3 Payment Capture -> PAY-001
```

**Validation**:

Existing repo TAG collisions are prevented during ID generation. After inserting
TAG metadata, scan the generated `tasks.md` and fail if any `@SPEC:<TAG_ID>`
appears more than once.

```bash
rg -o '@SPEC:([A-Z][A-Z0-9-]*-[0-9]{3})' specs/[spec-id]/tasks.md \
  | sed -E 's/.*@SPEC://' \
  | sort \
  | uniq -d \
  | while read -r duplicate; do
      echo "❌ Duplicate @SPEC TAG in tasks.md: $duplicate"
      exit 1
    done
```

### 4. Insert TAG Metadata (SPECTER Enhancement)

**This step is UNIQUE to `/ms.tasks`** - not provided by `/speckit-tasks`.

Add TAG chains to tasks.md for each User Story:

```markdown
## Phase 3: FR-1 Authentication (Priority: P0)

**TAG**: @SPEC:AUTH-001

**Goal**: Implement user authentication
**Independent Test**: Users can log in with email/password

### Implementation for FR-1

-   [ ] T015 Create auth service...
-   [ ] T016 Add login endpoint...
```

tasks.md carries **only** the `@SPEC` anchor. Never write `@TEST:`/`@CODE:`
anchor forms here: the chain's test/code anchors must come from the real test
and implementation files (`/ms.implement` Step 3) — restating them in tasks.md
either self-satisfies the backstop's `@TEST` requirement before any test
exists, or collides with the real `@CODE` anchor as a duplicate.

### 5. Report Output

Display summary (in Korean):

```json
{
    "tasks_created": "specs/001-user-authentication/tasks.md",
    "total_tasks": 54,
    "total_phases": 8,
    "next_step": "/ms.analyze"
}
```

Display next steps:

```
✅ 태스크 리스트(tasks.md) 생성이 완료되었습니다!

📄 위치: specs/001-user-authentication/tasks.md
📊 통계: 총 {Total Tasks}개 태스크 / {Total Phases}개 단계

🎯 다음 단계:
👉 /ms.analyze (구현 전 문서 일관성 검증 + Codex 보조 검증)
👉 /ms.implement (검증 통과 후 첫 번째 pending phase/phase-part 구현 시작)

💡 참고:
- 모든 태스크에는 TAG ID가 할당되어 SPEC-TEST-CODE 추적이 가능합니다.
- Phase 0 (Setup) → 1 (Audit) → 2-3 (RED) → 4-5 (GREEN) → 6 (VR) → 7 (Polish) 순으로 진행됩니다.
```

## TAG Format

**Chain** (one anchor kind per artifact):

```
@SPEC:{TAG_ID} (tasks.md) -> @TEST:{TAG_ID} (test file) -> @CODE:{TAG_ID} (implementation file)
```

**Domain Extraction Examples**:

-   "FR-1: User Authentication" → Domain: AUTH (keyword match)
-   "FR-2: Shopping Cart" → Domain: CART (keyword match)
-   "FR-9: Random Feature" → Domain: FR9 (fallback)

## Error Handling

-   **SPEC_NOT_FOUND**: Run `/ms.specify` first
-   **TASKS_GENERATION_FAILED**: Base command failed
-   **RIPGREP_NOT_FOUND**: Install ripgrep ≥13.0
-   **DUPLICATE_SPEC_TAG**: duplicate @SPEC TAG detected; `@TEST` may span multiple files, but each `@CODE` id lives in exactly one file (pre-commit backstop enforces this)

## Run-State Ledger (bookkeeping, not a gate)

Append one line to `.specify/specter-run.jsonl` (create it if needed; append-only, never
rewritten — a missing/corrupt ledger never blocks this command, it only speeds up conductor
resume). Reaching this point means `tasks.md` was generated without a blocking duplicate-`@SPEC`
TAG failure, so `verdict` is `PASS`:

```bash
mkdir -p .specify
printf '{"ts":"%s","cycle":"feature","feature":"%s","step":"tasks","verdict":"PASS","artifacts":["%s"]}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "<NNN>" "specs/<spec-id>/tasks.md" >> .specify/specter-run.jsonl
```

## Next Steps

After `/ms.tasks`:

1. Review tasks.md with TAG assignments and phase boundaries.
2. Run `/ms.analyze` to validate spec-plan-tasks consistency before implementation, including the default Codex advisory pass.
3. After `/ms.analyze` passes, run `/ms.implement` to implement the first pending phase/phase-part by default.

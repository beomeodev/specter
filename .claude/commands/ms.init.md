---
description: "Initialize My-Spec project with Spec-Kit + Constitution"
---

# /ms.init - One-Command Setup for My-Spec

Initialize your project with Spec-Kit and My-Spec Constitution in a single command.

## Overview

This command performs **complete project initialization**:

1. **Spec-Kit Installation** - Automatically installs latest Spec-Kit from upstream
2. **Constitution Setup** - Installs My-Spec's customized Constitution template

**User runs**: Just `/ms.init` - Everything else is automatic!

## Execution Steps

### Step 1: Install Spec-Kit (Automated)

**IMPORTANT**: This step automatically installs Spec-Kit from upstream.

Execute the Spec-Kit installation command:

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --integration claude
```

**What this does**:

-   Downloads latest Spec-Kit release from GitHub
-   Extracts template files to current directory
-   Creates directory structure:
    -   `.specify/` - Spec-Kit metadata
    -   `docs/templates/` - Template files (including constitution-template.md)
    -   `.specify/scripts/` - Utility scripts
    -   `specs/` - Specification directory
    -   Agent-specific commands (e.g., `.claude/commands/speckit.*`)

**Wait for completion**: This command may take 30-60 seconds.

**Verification**:

-   Check `.specify/` exists
-   Check `specs/` exists
-   If missing: Display error (see Error Handling section) and exit

### Step 2: Setup My-Spec Constitution (Copy Mode)

#### 2.1 Create Memory Directory

```bash
mkdir -p .specify/memory
```

#### 2.2 Copy Constitution Template

Copy `docs/templates/constitution-template.md` to `.specify/memory/constitution.md`:

```bash
cp docs/templates/constitution-template.md .specify/memory/constitution.md
```

**IF source file not found**:

-   Display error: "Constitution template missing. Expected: docs/templates/constitution-template.md"
-   This indicates a repository structure issue
-   Exit with error

#### 2.3 Install GEARS Spec-Template

Step 1 (`specify init --force`) overwrites `.specify/templates/spec-template.md` with
the upstream (classic EARS) template. Restore the My-Spec GEARS version on top of it —
the same copy-after-init pattern used for the constitution in Step 2.2:

```bash
cp docs/templates/spec-template.md .specify/templates/spec-template.md
```

**Why the core path** (not an `overrides/` entry): the `/speckit.specify` skill creates
each new `spec.md` by copying `.specify/templates/spec-template.md` directly (it does not
go through `resolve_template`, so a `templates/overrides/` entry would be ignored on the
live path). Installing GEARS at the core path is therefore what actually reaches new specs,
and it must be re-applied after every `specify init --force` (hence here in `/ms.init`).

**IF source file not found**:

-   Display error: "Spec-template missing. Expected: docs/templates/spec-template.md"
-   This indicates a repository structure issue
-   Exit with error

#### 2.4 Inject the Feature-Map gate into the installed `/speckit.specify`

`/ms.specify` enforces the Feature-Map gate, but it is only a *wrapper*. The underlying
`/speckit.specify` command (installed by Step 1's `specify init --force`) can be invoked
directly and would bypass the gate entirely. We cannot permanently edit a vendored file —
Step 1 re-installs it with `--force` — so, exactly like the GEARS spec-template in Step 2.3,
we **re-apply our overlay after every init**: insert a gate preamble **just after the YAML
frontmatter** of the installed `.claude/commands/speckit.specify.md` (the line-1 `---` must
stay first, or the command's `description` metadata stops parsing). Re-running `/ms.init`
restores it.

```bash
SPECKIT_SPECIFY=".claude/commands/speckit.specify.md"
if [ -f "$SPECKIT_SPECIFY" ] && ! grep -q "MS_FEATUREMAP_GATE_START" "$SPECKIT_SPECIFY"; then
  # Line number of the SECOND '---' = end of YAML frontmatter (empty if none).
  FM_END=$(grep -n '^---[[:space:]]*$' "$SPECKIT_SPECIFY" | sed -n '2p' | cut -d: -f1)
  GATE=$(cat <<'GATE'

<!-- MS_FEATUREMAP_GATE_START — injected by /ms.init; do not remove -->
> ⛔ **FEATURE MAP + CHECKLIST GATE.** Do NOT create or update a spec unless:
> 1. The input is a Feature section produced by `/ms.featuremap` (a `## Feature NNN:`
>    block containing `### In scope`, `### Explicitly out of scope`, `### Done criteria`).
> 2. `docs/prd/feature-map.checklist.md` exists, is `**Mode**: global`, and its result is PASS or WARN.
> 3. `docs/prd/checklists/feature-NNN.checklist.md` exists for the selected Feature, is
>    `**Mode**: per-feature`, and its result is PASS or WARN.
> 4. Both checklist audits' Feature Map SHA256 values match the current `docs/prd/feature-map.md`.
> REFUSE if: no Feature Map file exists (`docs/prd/feature-map*.md`), OR either checklist
> is missing/failed/stale, OR the per-Feature checklist is for a different Feature, OR the
> input is freeform / inline ad-hoc text / derived from an existing `spec.md`.
> On refusal, tell the user to run `/ms.featuremap @docs/prd/PRD.md`, then `/ms.checklist --global`,
> then `/ms.checklist`, then paste the checked Feature section. Prefer the `/ms.specify` wrapper over direct calls.
<!-- MS_FEATUREMAP_GATE_END -->
GATE
)
  TMP="$(mktemp)"
  if [ -n "$FM_END" ]; then
    # Keep frontmatter (lines 1..FM_END), insert gate, then the rest.
    { head -n "$FM_END" "$SPECKIT_SPECIFY"; printf '%s\n' "$GATE"; tail -n +"$((FM_END + 1))" "$SPECKIT_SPECIFY"; } > "$TMP"
  else
    # No frontmatter → safe to prepend at the very top.
    { printf '%s\n' "$GATE"; cat "$SPECKIT_SPECIFY"; } > "$TMP"
  fi
  mv "$TMP" "$SPECKIT_SPECIFY"
  echo "✓ Feature-Map + checklist gate injected into speckit.specify.md (after frontmatter)"
fi
```

**Idempotent**: the `MS_FEATUREMAP_GATE_START` marker prevents double-injection on re-runs.
**Durable**: because `specify init --force` overwrites `speckit.specify.md`, this step (like
Step 2.3) is what keeps the gate alive across every re-init — closing the direct-call bypass.

**IF `.claude/commands/speckit.specify.md` not found**:

-   Display notice: "speckit.specify.md not found — gate injection skipped (re-run after Step 1 installs it)"
-   Continue (non-fatal)

### Step 3: Report Success

Display completion message:

```
✅ My-Spec initialized successfully!

📦 Installed:
- ✅ Spec-Kit (latest version from upstream)
- ✅ My-Spec Constitution: .specify/memory/constitution.md

🎯 Next Steps:

0. (Write your PRD first, e.g. docs/prd/PRD.md)
1. /ms.featuremap @docs/prd/PRD.md - Decompose the PRD into a Feature Map
2. /ms.checklist --global - Validate whole PRD coverage, Feature ownership, and DAG
3. /ms.checklist - Validate the next Feature against its PRD references
4. /ms.specify - Create feature specification (paste the checked Feature section from the Feature Map)
5. /ms.clarify - Clarify requirements (if needed)
6. /ms.plan - Create implementation plan
7. /ms.constitution - Establish project baseline once after the first plan, if not already established
8. /ms.tasks - Generate implementation tasks
9. /ms.analyze - Validate spec-plan-tasks document consistency
10. /ms.implement - Start implementation
11. /ms.review - Run code review and executable gates before /fin

```

## Error Handling

### Error 1: Spec-Kit Installation Failed

**Symptom**: `uvx` command fails or `.specify/` not created

**Message**:

```
❌ Error: Spec-Kit installation failed

The command failed to install Spec-Kit:
    uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --ai claude

Please check:
1. Internet connection
2. GitHub accessibility
3. uvx/uv installed correctly

You can try manual installation:
    uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --ai claude

Then run /ms.init again.
```

**Exit**: Code 1

## Next Command

After `/ms.init`: Write your PRD, run `/ms.featuremap @docs/prd/PRD.md`, then run `/ms.checklist --global`. Each Feature cycle starts with `/ms.checklist`, and `/ms.specify` refuses to run when either the global or per-Feature audit is missing, failed, or stale.

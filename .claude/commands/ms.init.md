---
description: "Initialize My-Spec project with Spec-Kit + Constitution"
argument-hint: ""
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

Execute the Spec-Kit installation command. The default is **pinned to a verified release**
(`v0.11.6`) — this is the *loose-coupling* posture: upstream is pre-1.0 and renames its
integration surface often (command→skill, `speckit.x`→`speckit-x`), so pinning protects
SPECTER's wrappers from surprise breakage. The pin is overridable via `SPEC_KIT_REF` for
anyone who wants to track latest or test a newer tag:

```bash
SPEC_KIT_REF="${SPEC_KIT_REF:-v0.11.6}"
uvx --from "git+https://github.com/github/spec-kit.git@$SPEC_KIT_REF" specify init --here --force --integration claude
```

To track latest or a different tag instead of the pinned default, export the variable first:

```bash
SPEC_KIT_REF=v0.11.6 /ms.init   # default: verified pinned release (recommended)
SPEC_KIT_REF=main    /ms.init   # latest upstream (exposed to churn — re-verify seams)
```

> **Why pinned**: SPECTER's `/ms.*` wrappers delegate to upstream skills by name
> (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-clarify`,
> `/speckit-analyze`, `/speckit-implement`). Those names changed from the dotted form in
> recent upstream releases; pinning keeps the delegation contract stable. If you move the pin
> forward, re-check those invocation names (see README "Spec Kit 호환성 → 위임 지점").

> **Forward-compatibility**: the pinned v0.11.x line emits the **skill** layout
> (`.claude/skills/speckit-specify/SKILL.md`). Step 2.4's candidate detection patches
> whichever layout appears, so even if the pin moves to a newer Spec-Kit, gate injection
> does **not** break `/ms.init` (the delegation *names* are the part to re-verify, not the
> gate).

> **Note**: Spec-Kit dropped the older `--ai` family of flags in favour of
> `--integration`. Always use `--integration claude`; `--ai claude` is legacy and no
> longer supported by current upstream releases.

**What this does** (verified against a live v0.11.6 `specify init`):

-   Downloads the selected Spec-Kit ref from GitHub (`SPEC_KIT_REF`, default pinned `v0.11.6`)
-   Extracts bundled template files to the current directory
-   Creates directory structure:
    -   `.specify/` - Spec-Kit metadata, `templates/`, `scripts/bash/`, `memory/`,
        `workflows/`, `integrations/`
    -   Agent-specific Claude integration files. On v0.11.x this is the **skill** layout
        (`.claude/skills/speckit-*/SKILL.md`); older releases used the command layout
        (`.claude/commands/speckit.*.md`). Step 2.4 detects whichever exists.
-   Appends a small `<!-- SPECKIT START/END -->` block to `CLAUDE.md`. SPECTER's `CLAUDE.md`
    is a symlink to `AGENTS.md`, so this block lands (non-destructively, marker-managed) at
    the end of `AGENTS.md`. SPECTER content is preserved; the block is harmless.

> **Note**: `specify init` does **not** create `specs/` or `docs/templates/`. `specs/<NNN>-<name>/`
> is created later by `/speckit-specify` (first feature); `docs/templates/` ships with SPECTER
> itself (used by Steps 2.2–2.3). Do not gate `/ms.init` on either path existing.

**Wait for completion**: This command may take 30-60 seconds.

**Verification**:

-   Check `.specify/` exists (this is the only directory `specify init` is required to create)
-   Check `.specify/templates/spec-template.md` exists (needed by Step 2.3)
-   If missing: Display error (see Error Handling section) and exit
-   Do **not** require `specs/` here — it does not exist until the first `/ms.specify`.

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
the same copy-after-init pattern used for the constitution in Step 2.2. The `mkdir -p`
guard makes this safe even if a future Spec-Kit stops creating `.specify/templates/`:

```bash
mkdir -p .specify/templates
cp docs/templates/spec-template.md .specify/templates/spec-template.md
```

**Why the core path** (not an `overrides/` entry): historically the `/speckit.specify`
command created each new `spec.md` by copying `.specify/templates/spec-template.md`
directly. Installing GEARS at that core path is what actually reached new specs, and it
must be re-applied after every `specify init --force` (hence here in `/ms.init`).

> ✅ **Verified against a live `specify init` (upstream `main`, v0.11.x).** Current Spec-Kit
> resolves the spec template through a **preset/template resolution stack**
> (`specify preset resolve spec-template`) rather than a hardcoded copy. For a default
> (no-`--preset`) init, the stack's **`core` layer *is* `.specify/templates/spec-template.md`**
> — exactly this file. `specify preset resolve spec-template` was confirmed to resolve to
> this path (`top layer from: core`), so overwriting it here makes GEARS reach every new
> `spec.md`. The `mkdir -p` keeps the copy from erroring even if a future layout drops the
> directory.
> **Caveat**: if someone runs `specify init --preset <name>` with a preset that ships its own
> `spec-template`, that preset layer can sit above `core` and override GEARS. `/ms.init` does
> not pass `--preset`, so the default path is safe.

**IF source file not found**:

-   Display error: "Spec-template missing. Expected: docs/templates/spec-template.md"
-   This indicates a repository structure issue
-   Exit with error

#### 2.4 Inject the Feature-Map gate into the installed upstream `speckit specify`

`/ms.specify` enforces the Feature-Map gate, but it is only a *wrapper*. The underlying
upstream `speckit specify` integration (installed by Step 1's `specify init --force`) can be
invoked directly and would bypass the gate entirely. SPECTER patches whichever upstream
`speckit specify` integration file exists — **command-based or skill-based** — to prevent
direct `/speckit.specify` calls from bypassing `/ms.specify`'s Feature-Map / checklist /
Constitution gates.

We cannot permanently edit a vendored file — Step 1 re-installs it with `--force` — so,
exactly like the GEARS spec-template in Step 2.3, we **re-apply our overlay after every
init**: insert a gate preamble **just after the YAML frontmatter** (the line-1 `---` must
stay first, or Claude Code stops parsing the file's `description`/`name` metadata). If a
file has no frontmatter, the gate is prepended at the top. Re-running `/ms.init` restores it.

Because newer Spec-Kit may emit a native skill (`.claude/skills/speckit-specify/SKILL.md`)
**instead of, or in addition to**, the old command (`.claude/commands/speckit.specify.md`),
we probe a **candidate list** and patch **every file that exists** — not just the first. A
dual (command + skill) layout would otherwise leave one entrypoint ungated, and a direct
`/speckit.specify` call against that ungated file would bypass the Feature-Map gate. Patching
all existing candidates keeps the bypass guard airtight regardless of layout:

```bash
SPECKIT_SPECIFY_CANDIDATES=(
  ".claude/commands/speckit.specify.md"
  ".claude/commands/speckit-specify.md"
  ".claude/skills/speckit-specify/SKILL.md"
  ".claude/skills/speckit.specify/SKILL.md"
)

# Build the gate block once (leading blank line is intentional spacing).
GATE=$(cat <<'GATE'

<!-- MS_FEATUREMAP_GATE_START — injected by /ms.init; do not remove -->
> ⛔ **FEATURE MAP + CHECKLIST GATE.** Do NOT create or update a spec unless:
> 1. The input is a Feature section produced by `/ms.featuremap` (a `## Feature NNN:`
>    block containing `### In scope`, `### Explicitly out of scope`, `### Done criteria`).
> 2. `docs/prd/feature-map.checklist.md` exists, is `**Mode**: global`, records `/ms.verify`, and its result is PASS or WARN.
> 3. docs/prd/checklists/feature-NNN.checklist.md exists for the selected Feature, is
>    `**Mode**: per-feature`, and its result is PASS or WARN.
> 4. Both docs/prd/checklists/feature-NNN.codex-verify.md and docs/prd/checklists/feature-NNN.antigravity-verify.md exist and their results are PASS or WARN.
> 5. The global and per-Feature checklist audits' Feature Map SHA256 values match the current `docs/prd/feature-map.md`.
> 6. `.specify/memory/constitution.md` has an established Section IX baseline from `/ms.constitution`
>    or explicitly records that no durable project-specific constraints were found.
> REFUSE if: no Feature Map file exists (`docs/prd/feature-map*.md`), OR either checklist
> is missing/failed/stale, OR Section IX is not established, OR the per-Feature checklist is for
> a different Feature, OR the input is freeform / inline ad-hoc text / derived from an existing `spec.md`.
> On refusal, tell the user to run `/ms.featuremap @docs/prd/PRD.md [@docs/prd/another.md]`,
> then `/ms.codex-checklist`, then `/ms.verify`, then `/ms.constitution`, then `/ms.checklist`,
> then `/ms.agent-verify`, then paste the checked Feature section. Prefer the `/ms.specify` wrapper over direct calls.
<!-- MS_FEATUREMAP_GATE_END -->
GATE
)

inject_gate() {
  local file="$1"
  if grep -q "MS_FEATUREMAP_GATE_START" "$file"; then
    echo "✓ gate already present in $file (idempotent skip)"
    return
  fi
  # Line number of the SECOND '---' = end of YAML frontmatter (empty if none).
  local fm_end tmp
  fm_end=$(grep -n '^---[[:space:]]*$' "$file" | sed -n '2p' | cut -d: -f1)
  tmp="$(mktemp)"
  if [ -n "$fm_end" ]; then
    # Keep frontmatter (lines 1..fm_end), insert gate, then the rest.
    { head -n "$fm_end" "$file"; printf '%s\n' "$GATE"; tail -n +"$((fm_end + 1))" "$file"; } > "$tmp"
  else
    # No frontmatter → safe to prepend at the very top.
    { printf '%s\n' "$GATE"; cat "$file"; } > "$tmp"
  fi
  mv "$tmp" "$file"
  echo "✓ gate injected into $file (after frontmatter)"
}

FOUND=0
for candidate in "${SPECKIT_SPECIFY_CANDIDATES[@]}"; do
  if [ -f "$candidate" ]; then
    FOUND=1
    inject_gate "$candidate"
  fi
done

if [ "$FOUND" -eq 0 ]; then
  echo "⚠️ speckit specify integration file not found — gate injection skipped (re-run after Step 1 installs it)"
  echo "Looked for:"
  printf '  - %s\n' "${SPECKIT_SPECIFY_CANDIDATES[@]}"
fi
```

**Idempotent**: the `MS_FEATUREMAP_GATE_START` marker prevents double-injection on re-runs
(`inject_gate` skips, per file, any candidate that already carries the marker).
**Durable**: because `specify init --force` overwrites the upstream integration file, this
step (like Step 2.3) is what keeps the gate alive across every re-init — closing the
direct-call bypass regardless of whether upstream is command-based or skill-based.

**IF no candidate `speckit specify` file is found**:

-   Display notice listing the probed candidates: gate injection skipped (re-run after
    Step 1 installs it)
-   Continue (non-fatal)

#### 2.5 Install The Deterministic Gate Checker Script

Step 1's `specify init` creates `.specify/scripts/bash/` for upstream's own scripts. Install
SPECTER's mechanical gate checker (WI-11) alongside them, using the same copy-after-init pattern
as Steps 2.2–2.3 so it survives a future `specify init --force`:

```bash
mkdir -p .specify/scripts/bash
cp docs/templates/scripts/specter-gate.sh .specify/scripts/bash/specter-gate.sh
chmod +x .specify/scripts/bash/specter-gate.sh
```

This script owns only mechanical gate facts (checklist Result lines, Feature Map SHA256
equality, Constitution Section IX establishment, per-Feature/dual-agent artifact existence) for
`/ms.specify`, `/ms.checklist`, `/ms.specter`, and `/ms.constitution` — content judgment (PRD
fidelity, boundary discipline, severity) stays with the model.

**IF source file not found**:

-   Display error: "Gate checker script missing. Expected: docs/templates/scripts/specter-gate.sh"
-   This indicates a repository structure issue
-   Exit with error

#### 2.6 Install The Direct-Call Bypass Hook (speckit-specify)

Step 2.4's prompt-marker injection guides the model but cannot stop it. Close the gap
mechanically (WI-13): a PreToolUse hook that denies invoking the `speckit-specify` skill/command
unless `/ms.specify`'s own gates already passed for this run.

```bash
mkdir -p .specify/scripts/bash
cp docs/templates/scripts/speckit-specify-gate-hook.sh .specify/scripts/bash/speckit-specify-gate-hook.sh
chmod +x .specify/scripts/bash/speckit-specify-gate-hook.sh

if [ -f .claude/settings.json ] && command -v jq >/dev/null 2>&1; then
  ALREADY=$(jq -r '[.hooks.PreToolUse[]?.hooks[]?.command // empty] | any(test("speckit-specify-gate-hook.sh"))' .claude/settings.json 2>/dev/null || echo false)
  if [ "$ALREADY" != "true" ]; then
    HOOK_ENTRY='{"matcher":"Skill","hooks":[{"type":"command","command":"\"$CLAUDE_PROJECT_DIR/.specify/scripts/bash/speckit-specify-gate-hook.sh\""}]}'
    jq --argjson entry "$HOOK_ENTRY" '.hooks.PreToolUse = ((.hooks.PreToolUse // []) + [$entry])' .claude/settings.json > .claude/settings.json.tmp \
      && mv .claude/settings.json.tmp .claude/settings.json
    echo "✓ PreToolUse gate hook installed in .claude/settings.json"
  else
    echo "✓ PreToolUse gate hook already present (idempotent skip)"
  fi
else
  echo "⚠️ .claude/settings.json missing or jq unavailable — hook config not installed; script still copied to .specify/scripts/bash/"
fi
```

The hook script fails open (allows) on any internal error — a missing `jq`, malformed input, or
any other unexpected condition never blocks unrelated Skill calls. It only denies when the
invoked skill is literally `speckit-specify` (or the legacy `speckit.specify`) and no
`.specify/.ms-gate-pass-*` token exists (written and deleted by `/ms.specify`, see that command's
Step 0.2/3.2).

**IF source file not found**:

-   Display error: "Gate hook script missing. Expected: docs/templates/scripts/speckit-specify-gate-hook.sh"
-   This indicates a repository structure issue
-   Exit with error

### Step 3: Report Success

Display completion message:

```
✅ My-Spec initialized successfully!

📦 Installed:
- ✅ Spec-Kit (latest version from upstream)
- ✅ My-Spec Constitution: .specify/memory/constitution.md
- ✅ Deterministic gate checker: .specify/scripts/bash/specter-gate.sh
- ✅ Direct-call bypass hook: .specify/scripts/bash/speckit-specify-gate-hook.sh (+ .claude/settings.json PreToolUse entry)

🧩 Codex & Antigravity Plugins Setup (inside Claude Code):
1. Open Claude Code in the project environment.
2. Add the marketplaces:
   - `/plugin marketplace add openai/codex-plugin-cc`
   - `/plugin marketplace add sakibsadmanshajib/antigravity-plugin`
3. Install the plugins:
   - `/plugin install codex@openai-codex`
   - `/plugin install antigravity@sakibsadmanshajib`
4. Reload plugins:
   - `/reload-plugins`
5. Run setups:
   - `/codex:setup`
   - `/antigravity:setup`
6. If either plugin asks for external app authentication, complete that sign-in when prompted.
7. If you run multiple project containers and they do not share `~/.codex` or `~/.gemini`, repeat steps 1-6 per container.
   - If you do share these directories across containers, the plugin installs and logins can be reused.

🎯 Next Steps:

0. (Write your PRD first, e.g. docs/prd/PRD.md)
1. /ms.featuremap @docs/prd/PRD.md [@docs/prd/another.md] - Decompose the PRD set into a Feature Map
2. /ms.codex-checklist - Start the PRD-only Codex checklist in background
3. /ms.verify - Validate Feature Map against PRDs and Codex checklist
4. /ms.constitution - Establish project baseline once from the checked PRD Feature Map
5. /ms.checklist - Validate the next Feature against its Source PRDs and PRD references
6. /ms.agent-verify - Start concise Codex & Antigravity verification for the Feature checklist
7. /ms.specify - Create feature specification (paste the checked Feature section from the Feature Map)
8. /ms.clarify - Clarify requirements (if needed)
9. /ms.plan - Create implementation plan
10. /ms.tasks - Generate implementation tasks
11. /ms.analyze - Validate spec-plan-tasks document consistency
12. /ms.implement - Start implementation
13. /ms.review - Run code review and executable gates before /ms.fin

```

## Error Handling

### Error 1: Spec-Kit Installation Failed

**Symptom**: `uvx` command fails or `.specify/` not created

**Message**:

```
❌ Error: Spec-Kit installation failed

The command failed to install Spec-Kit:
    SPEC_KIT_REF="${SPEC_KIT_REF:-v0.11.6}" uvx --from "git+https://github.com/github/spec-kit.git@$SPEC_KIT_REF" specify init --here --force --integration claude

Please check:
1. Internet connection
2. GitHub accessibility
3. uvx/uv installed correctly

You can try manual installation (pinned default; override with SPEC_KIT_REF=main to track latest):
    uvx --from "git+https://github.com/github/spec-kit.git@v0.11.6" specify init --here --force --integration claude

Then run /ms.init again.
```

**Exit**: Code 1

## Next Command

After `/ms.init`: Write your PRD set, run `/ms.featuremap @docs/prd/PRD.md [@docs/prd/another.md]`, then run `/ms.codex-checklist`, `/ms.verify`, and `/ms.constitution`. Each Feature cycle starts with `/ms.checklist` and `/ms.codex-verify`, and `/ms.specify` refuses to run when the global audit, per-Feature audit, or Codex verification is missing, failed, or stale.

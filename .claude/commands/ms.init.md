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
uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --ai claude
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

### Step 3: Verify Hooks Installation

Check if hooks are installed:

```bash
ls -la .claude/hooks/
```

**IF hooks not found**:
```
⚠️ Warning: Hooks not installed

Hooks enable:
- Auto-injection of Constitution into sub-agents
- Audio notifications for task completion

Install manually:
1. Create .claude/hooks/ directory
2. Copy constitution-injector.sh and notify.sh
3. chmod +x .claude/hooks/*.sh
4. Add sound files to .claude/hooks/sounds/

Or continue without hooks (Constitution will be manually referenced).
```

**IF hooks found**:
```
✅ Hooks detected: Constitution auto-injection enabled
```

### Step 4: Report Success

Display completion message:

```
✅ My-Spec initialized successfully!

📦 Installed:
- ✅ Spec-Kit (latest version from upstream)
- ✅ My-Spec Constitution: .specify/memory/constitution.md

🎯 Next Steps:

1. /ms.specify - Create feature specification
2. /ms.clarify - Clarify requirements (if needed)
3. /ms.plan - Create implementation plan
4. /ms.constitution - Extract project-specific constraints (from plan.md)
5. /ms.tasks - Generate implementation tasks
6. /ms.analyze - Validate TRUST compliance
7. /ms.implement - Start implementation

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

After `/ms.init`: Run `/ms.specify` to create first feature specification

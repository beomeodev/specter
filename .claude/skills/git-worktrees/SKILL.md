---
name: git-worktrees
description: Full lifecycle discipline for isolated git worktrees — setup (detect existing isolation, prefer native tools like EnterWorktree, ignore-check before project-local creation, per-worktree dependency install, clean test baseline) and teardown (merge-before-remove-before-delete ordering, provenance-based cleanup, never remove from inside the worktree). Use when starting feature work that needs isolation from the current workspace, when running parallel Features (see parallel-features), or when finishing a branch and deciding merge/PR/keep/discard.
---

<!-- Source: adapted from obra/superpowers `using-git-worktrees` + `finishing-a-development-branch` (MIT). SPECTER additions marked. -->

# Git Worktrees — Setup and Finish

## Part 1: Setting Up an Isolated Workspace

**Core principle:** Detect existing isolation first. Then use native tools. Then fall
back to git. Never fight the harness.

### Step 0: Detect Existing Isolation

Before creating anything, check if you are already in an isolated workspace:

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
```

**Submodule guard**: `GIT_DIR != GIT_COMMON` is also true inside git submodules. If
`git rev-parse --show-superproject-working-tree` returns a path, you're in a submodule —
treat as a normal repo.

- `GIT_DIR != GIT_COMMON` (and not a submodule) → already in a linked worktree. Do NOT
  create another; skip to Step 2.
- Otherwise → normal repo. If the user hasn't already declared a worktree preference,
  ask consent before creating one.

### Step 1: Create the Workspace

**1a. Native tools first (preferred).** If a native worktree tool exists (e.g. the
`EnterWorktree` tool, a `/worktree` command, an agent `isolation: "worktree"` option),
use it and skip to Step 2. Using `git worktree add` when a native tool exists creates
phantom state the harness can't see or manage — this is the #1 mistake.

**1b. Git fallback (only when no native tool).**

Directory priority: explicit user preference > existing `.worktrees/` > existing
`worktrees/` > default `.worktrees/` at project root.

**MUST verify the directory is git-ignored before creating a project-local worktree:**

```bash
git check-ignore -q .worktrees 2>/dev/null || { echo ".worktrees/" >> .gitignore; git add .gitignore; git commit -m "chore: ignore worktrees dir"; }
git worktree add ".worktrees/$BRANCH_NAME" -b "$BRANCH_NAME"
cd ".worktrees/$BRANCH_NAME"
```

If `git worktree add` fails on a sandbox/permission error, say so and work in place.

### Step 2: Per-Worktree Project Setup

A fresh worktree has no installed dependencies. Auto-detect and install:

```bash
[ -f package.json ] && npm install
[ -f pyproject.toml ] && (command -v uv >/dev/null && uv sync || pip install -e .)
[ -f requirements.txt ] && pip install -r requirements.txt
[ -f go.mod ] && go mod download
[ -f Cargo.toml ] && cargo build
```

Never share `node_modules`/venvs across worktrees — breaks isolation, causes races.

### Step 3: Verify Clean Baseline

Run the project's test suite before starting work. If tests fail, report and ask
whether to proceed — otherwise you can't distinguish new bugs from pre-existing ones.
Report: `Worktree ready at <path>, tests passing (<N>), ready to implement <feature>.`

## Part 2: Finishing a Development Branch

**Core principle:** Verify tests → detect environment → present options → execute →
clean up. The ordering invariants below are not optional.

### Step 1: Verify tests pass

If tests fail, stop — show failures. No merge/PR until green.

### Step 2: Present exactly these options (no open-ended questions)

```text
Implementation complete. What would you like to do?
1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work
```

(Detached HEAD: drop option 1.) In SPECTER, options 1–2 normally route through
`/ms.fin` → `/ms.merglease` — this menu still governs the worktree lifecycle.

### Step 3: Ordering invariants

- **Merge succeeds → then remove worktree → then delete branch.** `git branch -d`
  fails while a worktree still references the branch; a removed worktree before a
  confirmed merge destroys the work.
- **Never run `git worktree remove` from inside the worktree** — `cd` to the main
  repo root first:
  ```bash
  MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
  cd "$MAIN_ROOT"
  git worktree remove "$WORKTREE_PATH" && git worktree prune
  ```
- **Options 2 and 3 preserve the worktree** — the user needs it alive to iterate on
  PR feedback. Cleanup only for options 1 and 4.
- **Provenance rule**: only clean up worktrees you created (under `.worktrees/` or
  `worktrees/`). Harness-created workspaces are the harness's to manage — use its
  exit tool or leave them.
- **Discard requires typed confirmation** (`discard`), listing branch, commits, and
  worktree path that will be lost.

## Red Flags

Never: create a worktree when Step 0 detects existing isolation · use `git worktree add`
when a native tool exists · skip the ignore-check · skip the clean baseline · remove a
worktree before merge is confirmed · remove from inside the worktree · clean up
worktrees you didn't create · proceed on failing tests without asking.

## Works well with

- `parallel-features`: SPECTER-specific rules for running multiple Feature cycles in
  parallel worktrees (shared-state discipline, merge-back sequencing).
- `spike`: throwaway spikes can use a worktree; discard via Part 2 option 4.

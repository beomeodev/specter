---
description: "Broadcast SPECTER workflow files to all registered project repos"
argument-hint: "[--dry-run] [--target <name>]"
---

# /ms.sync - SPECTER Workflow Broadcast

Pushes the manifest-listed workflow files (`.claude` commands/skills/agents, gate
scripts, doc templates, `AGENTS.md`/`CLAUDE.md`) from **this SPECTER checkout** to
every project repo registered in the machine-local registry. Run it from the
SPECTER repo after committing workflow changes.

> **Recommended pre-step for discipline-skill edits**: an edit to a
> discipline-enforcing skill (gates, TDD rules, surgical-scope, parallel/worktree
> rules) propagates to every registered repo at once. Pressure-test it first with
> the `testing-skills-with-subagents` skill (RED baseline → GREEN → loophole
> REFACTOR). Reference skills (ms-lang-*, crib sheets) don't need this.

## Safety Model (public-repo protection)

- The target list lives **outside the repo** at `~/.claude/specter-sync.json`
  (shared host mount, visible to every devcontainer). A stranger cloning this
  public repo has no registry → `/ms.sync` no-ops with a friendly message.
- The registry's `source` must match this checkout (path or normalized origin
  URL). A fork or stray copy refuses to broadcast.
- Sync only operates on **committed** state: the SPECTER manifest files must be
  clean, and targets are fresh clones of their origin (uncommitted work in a
  project's live container is never touched — it arrives there via `git pull`).

## Registry Format

```json
{
  "source": "git@github.com:beomeodev/specter.git",
  "targets": [
    { "name": "proj-a", "repo": "git@github.com:beomeodev/proj-a.git",
      "exclude": [".claude/commands/ms.fix.md"] }
  ]
}
```

`exclude` declares a target's **permanent specializations** — those files are
never synced to that project. Register new projects with:

```bash
python scripts/specter/specter_sync.py register git@github.com:me/new-proj.git
```

(The host-side `np` target should call this at project-creation time.)

## Usage

```bash
/ms.sync              # broadcast to all registered targets
/ms.sync --dry-run    # report per-file decisions without writing/pushing
/ms.sync --target proj-a
```

## Execution Steps

### Step 1: Run the sync engine

```bash
python scripts/specter/specter_sync.py [--dry-run] [--target <name>]
```

The script clones each target, applies a per-file 3-way decision against the
baseline recorded in the target's `.specter-sync-state.json` (the SPECTER
commit whose content was last applied), commits as
`chore(specter-sync): apply SPECTER workflow @ <sha>`, and pushes.

| target file | SPECTER file | result |
|---|---|---|
| unchanged since baseline | changed | `UPDATE` (safe overwrite) |
| customized | unchanged | `KEPT-LOCAL` (specialization wins) |
| customized | changed | 3-way merge → `MERGED`, or `CONFLICT` if overlapping |
| no baseline yet, content differs | — | `CONFLICT` (conservative first sync) |
| unchanged since baseline | **deleted** | `DELETED-UPSTREAM` (removed from the target too) |
| customized | **deleted** | `DELETE-KEPT-LOCAL` (fork survives; baseline dropped → target-owned from now on) |

Deletion propagation fires only for files genuinely deleted from the SPECTER
checkout (verified against HEAD). A file that merely left the manifest set
(narrowed globs) is left untouched with its baseline intact, so re-widening
the manifest later still 3-way merges.

On `CONFLICT` nothing is overwritten: the new SPECTER version is pushed
alongside as `<file>.specter-new` and the baseline does not advance, so the
conflict resurfaces every sync until resolved.

### Step 2: Interpret the report

- `ERROR` on a target (clone/push failure) → surface it; other targets still ran.
- `CONFLICT` entries → warn the user explicitly, per project and per file
  (충돌주의). Resolution happens **in each target project's own session**, not
  here: there, compare the file with its `.specter-new`, merge the upstream
  hunks (or adopt them wholesale), delete the `.specter-new` marker, and commit.
  Once the file incorporates the upstream hunks, the next `/ms.sync` merges
  cleanly and the baseline advances.
- A file that should stay diverged forever → add it to that target's `exclude`
  list in the registry instead of resolving repeatedly.

### Step 3: Report to the user

Summarize per target: pushed commit or "up to date", counts by status, and the
explicit conflict list with resolution guidance. Remind that live containers
receive the pushed changes on their next `git pull` / `make sync` entry flow.

## Error Handling

- **No registry / empty targets**: exit 0 with guidance — expected for anyone
  who isn't the template owner. Do not create a registry unprompted.
- **Registry source mismatch**: exit 1 — refuses to broadcast from a fork.
- **Dirty manifest files in SPECTER**: exit 1 — commit workflow changes first
  (baselines are git commits, so sync must run from committed state).
- **Clone/push failure on one target**: reported per target; remaining targets
  still sync; overall exit 1.

## Notes

- `/ms.sync` itself and `scripts/specter/specter_sync*` are excluded from the manifest:
  the sync tooling lives only in SPECTER, target projects never receive it.
- Project-local files (`.claude/settings*.json`, Constitution, `.specify/`) are
  never in the manifest. Keep it that way.
- Manifest: `scripts/specter/specter_sync_manifest.json` (fnmatch globs; `*` crosses `/`).
- Engine tests: `tests/specter/test_specter_sync.py`.

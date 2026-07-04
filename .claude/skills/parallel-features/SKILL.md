---
name: parallel-features
description: SPECTER-specific methodology for running two or more independent Feature cycles concurrently in separate git worktrees — eligibility test (DAG independence + plan-time file-overlap check), per-worktree vs shared-state rules, union-merge setup for append-shaped workflow files, and merge-back sequencing (rebase + gate re-run for the second merge). Use when the Feature Map DAG shows independent branches and the user wants to run them in parallel (interactively or via the overnight driver), or when deciding whether two Features are safe to parallelize at all.
---

<!-- Methodology adapted from arittr/spectacular (decomposing-tasks, executing-parallel-phase,
     cross-phase-stacking) + SPECTER shared-state analysis (2026-07 audit). -->

# Parallel Features — Running Independent DAG Branches Concurrently

Serial cycles cost sum(feature-hours); parallel costs max(). This skill defines when
parallelizing is safe in SPECTER and the discipline that keeps the gates intact.

## 1. Eligibility — BOTH tests must pass

**Test A — DAG independence.** In `docs/prd/feature-map.md`, neither Feature depends
on the other, directly or transitively, and neither is the stub-and-forward *activator*
of a structure the other consumes. Features the map marks as parallel-eligible pass;
when in doubt, trace the dependency graph by hand.

**Test B — file-overlap check (plan-time).** Compare the planned touched-file sets:
each Feature's `plan.md` (or, pre-plan, the Feature section's In-scope deliverables).
`intersection ≠ ∅` → **serialize** — shared files mean rebase conflicts and blurred
review scope. Different top-level dirs (backend/ vs frontend/) or different repos are
automatically independent. Same shared module (config, schema, router registry) → treat
as overlap even if line ranges look disjoint.

If either test fails: run serially. Do not rationalize ("the lines don't actually
conflict") — the point of isolation is uncommitted-state separation and reviewable
scope, not just merge conflicts.

## 2. One-time setup: union merge for append-shaped files

Three workflow files are appended to by every cycle and WILL collide at merge time.
They are order-insensitive logs, so git's union driver is safe for them. Run once per
project (idempotent):

```bash
grep -q "specter-run.jsonl merge=union" .gitattributes 2>/dev/null || cat >> .gitattributes << 'EOF'

# SPECTER parallel-features: append-shaped workflow logs merge by union
.specify/specter-run.jsonl merge=union
docs/prd/feature-map.progress.md merge=union
docs/dev_daily.md merge=union
EOF
```

Do NOT add union merge for anything else — checklists, specs, and source files must
conflict loudly.

## 3. Shared-state map (what lives where)

| Artifact | Disposition |
|---|---|
| `specs/<NNN>-*`, `docs/prd/checklists/feature-<NNN>.*` | Per-Feature — disjoint by construction, no conflict |
| Source code | Per-worktree — guaranteed disjoint by Test B |
| `.specify/specter-run.jsonl`, `feature-map.progress.md`, `dev_daily.md` | Append-shaped — union merge (Section 2) |
| `docs/prd/feature-map.md` (normative) | **Must not change during a cycle.** Cycles only read it. If a cycle needs to edit it, STOP the parallel run — that's `/ms.expand` or amend territory, and it invalidates the other worktree's gate SHA |

## 4. Execution

1. One worktree per Feature via the `git-worktrees` skill (branch from up-to-date
   `master`; per-worktree deps; clean baseline).
2. Run each Feature's `/ms.specter <NNN>` **inside its own worktree** — never two
   conductors in the same working tree (the second would build on the first's
   uncommitted implementation).
3. Concurrency form is your choice: two interactive sessions side by side, or
   sequential-in-time but isolated-in-space (the `overnight-run` driver does exactly
   this).
4. **Verify before trusting**: a conductor's success claim ≠ a usable branch. Check
   the worktree's run ledger shows `review` PASS/WARN and the branch has commits
   (`git rev-parse HEAD != master`).

## 5. Merge-back sequencing (the part that protects the gates)

Merge serially, in DAG/listed order. For each Feature, in its worktree:

1. **First Feature**: normal `/ms.fin` → `/ms.merglease`. Union driver absorbs the
   log-file overlaps.
2. **Every subsequent Feature**: master has moved — **rebase onto updated master
   first**, resolve anything the union driver didn't (there should be nothing if
   Test B held; a real conflict here means eligibility was wrong — stop and review),
   then **re-run the executable gate** (`local-ci`: lint → types → tests → build)
   because the code now sits on a different base than the one `/ms.review` approved.
   Only then `/ms.fin` → `/ms.merglease`.
3. **Cleanup only after that Feature's merge is confirmed** (git-worktrees Part 2
   ordering). Keep unmerged worktrees alive — they are the debugging evidence.

Gate note: per-Feature cycles never edit normative `feature-map.md`, so the global
gate SHA stays valid throughout — no re-`/ms.verify` needed for a clean parallel run.

## Anti-rationalization

- "Files don't overlap so I'll skip the worktree" → isolation is about uncommitted
  state and review scope, not just conflicts. Use the worktree.
- "Clean up the worktree now, merge later" → never. Merge confirmed first.
- "The rebase was clean so CI can't have changed" → the base changed; re-run local-ci.
- "Three-way parallel since two worked" → each added lane multiplies merge-order risk;
   2–3 max, and only with pairwise Test A+B passes.

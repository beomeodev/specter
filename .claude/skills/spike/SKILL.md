---
name: spike
description: Sanctioned throwaway exploration OUTSIDE the gated SPECTER workflow — time-boxed, never merged, no TAG/gate ceremony, and the only durable artifact is a findings note that feeds a PRD Amendment (/ms.expand) or a fix decision. Use when the user wants to test feasibility, compare approaches, or probe an unknown ("실험해보자", "프로토타입", "검증만 해보고 버리자", "될지 한번 쳐보자") before committing to spec ceremony — NOT for building anything intended to ship.
---

# Spike — Time-Boxed Throwaway Exploration

SPECTER gates everything that ships. A spike is the sanctioned way to explore what
you *don't yet know you want to ship* — it prevents both failure modes the gates
otherwise create: running full spec ceremony on an unvalidated idea, and quietly
bypassing gates "just to try something".

## Contract (non-negotiable)

1. **Time-boxed.** State the box out loud before starting; stop at expiry and write
   findings even if incomplete. An expired inconclusive spike is a valid result
   ("needs a bigger investment" is a finding).
2. **Never merged.** Spike code never reaches master, never gets a TAG, never enters
   review. It is evidence, not product.
3. **The findings note is the only artifact.** Code is disposable; the note survives.
4. **Production tree untouched.** Work in the scratchpad or a discard branch/worktree.

## Tiers

| Tier | Box | Where | For |
|---|---|---|---|
| T1 probe | ≤ 15 min | scratchpad dir, single file | "does this API/library/approach even respond the way we think?" |
| T2 spike | 30–60 min | `spike/<name>` branch or worktree (git-worktrees skill) | "which of two approaches holds up?", "can X integrate with Y at all?" |

Anything that wants more than T2's box is not a spike — it's a Feature hiding from
the gates. Stop and route it: new requirement → PRD Amendment → `/ms.expand`.

## Findings note

Write `docs/spikes/<YYYY-MM-DD>-<name>.md`:

```markdown
# Spike: <question being answered>
**Box**: T1|T2, <minutes spent> · **Verdict**: 가능 | 불가 | 조건부 | 미결(박스 소진)

## What was tried
<2-5 lines — approach, not code narration>

## Evidence
<the observed behavior/numbers that support the verdict>

## Decision recommendation
<what this means for the product: adopt approach A / needs PRD amendment for X /
drop the idea / spike again with different question>
```

## Route the learnings (the whole point)

- New requirement emerged → append `## PRD Amendment N` to the PRD, citing the note
  → `/ms.expand`.
- Existing behavior needs correcting → `/ms.fix`, citing the note.
- Idea dead → the note IS the record of why; nothing else to do.

## Cleanup

After the note is written: delete the spike branch/worktree (git-worktrees Part 2,
option 4 — the typed-confirm discard). Scratchpad files can simply be abandoned.
A lingering spike branch is a temptation to merge evidence into product.

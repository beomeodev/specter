# Antigravity write-flag re-apply procedure

`/ms.pre-verify`, `/ms.verify`, `/ms.featuremap-checklist`, `/ms.analyze`, and `/ms.review` all
preflight-check that Antigravity (`agy`) has its write flag set before invoking it. That check can
start failing after an unrelated plugin update, because the flag lives outside git.

## Where the flag lives

Headless `agy --print` runs can't answer interactive permission prompts, so `agy` invocations need
`--dangerously-skip-permissions` on the argv to write their report files. This flag is patched
directly into the **installed plugin cache** (not the source repo, not the marketplace copy):

```
~/.claude/plugins/cache/antigravity/antigravity/<version>/scripts/lib/agent-runtime.mjs
```

Two argv builders in that file each need one `args.push('--dangerously-skip-permissions')` line:
`runAgyPrint` and `spawnAgyDetached`.

## Why it resets

The plugin cache directory is reinstalled wholesale when the `antigravity` plugin updates — it is
not a git-tracked file, so the patch does not survive an update. The marketplace copy under
`~/.claude/plugins/marketplaces/antigravity/` is a separate, divergent tree; editing it has no
effect on what actually runs, since the cache is the live source.

## Re-apply

After any antigravity plugin update:

1. Find the current cache path: `find ~/.claude/plugins/cache/antigravity -iname agent-runtime.mjs`
2. Confirm the flag is missing: `grep -n "dangerously-skip-permissions" <path>` — if both
   `runAgyPrint` and `spawnAgyDetached` already push the flag, nothing to do.
3. If either is missing it, add `args.push('--dangerously-skip-permissions');` back into that
   function's argv-building block, in the same style as the other push calls nearby.

## What the preflight failure looks like

The External Agent Preflight step (Step 0.4/0.5/0 depending on command) reports the write-flag
check failing, the retry-once also fails, and the command applies its Degrade Rule: proceed
Codex-only, force the station/global result to at most `WARN`, and record
`Antigravity: UNAVAILABLE (<reason>)` in place of a normal report. No report file appears at the
expected `docs/prd/.../antigravity-*.md` or `docs/review/*.antigravity-review.md` path.

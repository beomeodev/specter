---
name: transcript-mining
description: Efficient, bounded mining of Claude Code session transcripts (~/.claude/projects/*/​*.jsonl) for workflow audits, usage-pattern analysis, and skill distillation — JSONL anatomy, proven extraction queries (tool-use counts, duplicate reads, token aggregation, command sequences), the scan-only-named-files rule, and the content-vs-mechanics separation rule. Use when auditing workflow health, quantifying token waste, reconstructing what happened across sessions, or distilling incident knowledge from transcripts into a skill.
---

# Transcript Mining

Session transcripts are the raw evidence for workflow audits and skill distillation,
but they are huge (single sessions reach several MB; projects reach 100+ MB). This
skill encodes the discipline that keeps mining cheap and the findings sound.

## Hard rules (violations are exactly the observed waste modes)

1. **Never Read a transcript file whole.** A single `Read` of a session JSONL can
   overflow the context. Always extract with `python3`/`jq` and bring back only
   aggregates or matched lines.
2. **Scan ONLY the named session files.** If the task names sessions, touch nothing
   else — do not "also check related sessions for completeness" (observed failure:
   an executor re-scanned an entire project instead of 7 named files). If targets
   are unknown, select by *metadata only* (`ls -lat`, sizes, mtimes) — never by
   reading contents to decide.
3. **Delegate per-project fan-out to subagents**, one per project directory, each
   returning a quantitative report — never stream raw transcript content into the
   main context.
4. **Content vs mechanics separation.** When distilling knowledge (e.g. debugging
   playbooks): mine only the product/environment content (symptom → probe →
   resolution). Never mine workflow mechanics (command behavior, gate handling) —
   transcripts predate current workflow versions and that layer is stale by default.
5. **Provenance, not memoir.** Distilled entries are stated at the failure-class /
   pattern level, stack-agnostic; the incident citation is provenance, at most a
   one-line example. Drop findings that could only recur in the source project.

## JSONL anatomy

- Location: `~/.claude/projects/<-workspace-name>/<session-uuid>.jsonl`, one JSON
  object per line.
- Relevant record shapes:
  - user/assistant messages: `.message.content[]` blocks — `{"type":"text",...}`,
    `{"type":"tool_use","name":...,"input":{...}}`, `{"type":"tool_result",...}`
  - usage (on assistant messages): `.message.usage.{input_tokens, output_tokens,
    cache_read_input_tokens, cache_creation_input_tokens}`
  - slash-command invocations: user text containing `<command-name>` markers
- Token estimate for file/text sizes: `chars / 4`.

## Proven queries (python3; jq equivalents work)

```python
import json, collections, sys
tool_uses, reads, usage = collections.Counter(), collections.Counter(), collections.Counter()
for path in sys.argv[1:]:                      # ONLY the named files
    for line in open(path, errors="replace"):
        try: rec = json.loads(line)
        except json.JSONDecodeError: continue
        msg = rec.get("message") or {}
        for blk in (msg.get("content") or []) if isinstance(msg.get("content"), list) else []:
            if blk.get("type") == "tool_use":
                tool_uses[blk.get("name")] += 1
                if blk.get("name") == "Read":
                    reads[blk.get("input", {}).get("file_path", "?")] += 1
        for k, v in (msg.get("usage") or {}).items():
            if isinstance(v, int): usage[k] += v
print("tools:", tool_uses.most_common(10))
print("dup reads:", [(f, c) for f, c in reads.most_common(15) if c > 1])
print("usage:", dict(usage))
```

Recipe variants: command sequence = grep user-role lines for `<command-name>`;
duplicate-work cost = Σ (count−1) × file_size/4 per re-read file; per-session
context pressure = cache_read_input_tokens / assistant-message count; friction =
grep tool_result lines for `"is_error": true` or known error strings ("File has not
been read", "session limit").

## Report shape

Quantitative first (counts, token estimates, session basenames as evidence),
recommendations second and separate. State coverage explicitly ("N of M named files
scanned; nothing else touched") so re-scan waste is visible if it happens.

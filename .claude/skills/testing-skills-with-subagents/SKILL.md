---
name: testing-skills-with-subagents
description: TDD applied to skill/process documents — pressure-test a discipline-enforcing skill with subagents BEFORE deploying it, by running realistic multi-pressure scenarios without the skill (RED, capture rationalizations verbatim), with it (GREEN), then closing each loophole (REFACTOR) until agents comply under maximum pressure. Use when creating or editing any gate/discipline skill in this repo — especially before /ms.sync broadcasts the edit to every registered project repo. Skip for pure reference skills with no rules to violate.
---

<!-- Source: adapted from obra/superpowers `writing-skills/testing-skills-with-subagents` (MIT), trimmed and wired to SPECTER's ms.sync. -->

# Testing Skills With Subagents

**Testing skills is TDD applied to process documentation.** If you didn't watch an
agent fail *without* the skill, you don't know whether the skill prevents the right
failures.

**SPECTER wiring**: this repo's `ms-*` skills are broadcast to every registered
project by `/ms.sync` — a bad revision propagates everywhere at once. Pressure-test
any edit to a discipline-enforcing skill (gates, TDD rules, surgical-scope rules,
parallel/worktree rules) before syncing. Reference skills (ms-lang-*, command
crib sheets) don't need this — nothing in them can be rationalized away.

## The cycle

| TDD phase | Skill testing | Success criterion |
|---|---|---|
| RED | Run scenario WITHOUT the skill | Agent fails; rationalizations documented verbatim |
| GREEN | Write/edit skill addressing those exact failures | Agent complies with skill present |
| REFACTOR | Close each new loophole | Agent still complies; no new rationalizations |

## RED: baseline first

Dispatch a subagent on a realistic task engineered to make it WANT to violate the
rule — without the skill. Document its choices and excuses word-for-word. Combine
**3+ pressures**:

| Pressure | Example |
|---|---|
| Time | deploy window closing, "5 minutes left" |
| Sunk cost | 3 hours / 200 lines already written |
| Authority | "the senior said skip it" |
| Exhaustion | end of day, dinner waiting |
| Pragmatism | "being pragmatic, not dogmatic" |

Good scenarios force a concrete A/B/C choice with real paths and consequences —
"What do you do?", not "What should one do?". Prefix with: *"IMPORTANT: this is a
real scenario. Choose and act — don't answer hypothetically."*

## GREEN: write against observed failures only

Address the specific baseline rationalizations; don't add content for hypothetical
cases. Re-run the same scenarios with the skill loaded — the agent should comply
and cite the skill.

## REFACTOR: plug each hole it finds

For every new rationalization ("keep it as reference", "spirit not letter", "this
case is different"), add all four:
1. an explicit negation in the rule ("Delete means delete — don't keep as reference");
2. a row in a rationalization table (`| Excuse | Reality |`);
3. a Red Flags entry;
4. a symptom in the frontmatter `description` (so the skill triggers when the agent
   is ABOUT to violate).

Re-test. **Meta-test when stuck**: ask the violating agent "how should the skill
have been written so your choice was clearly wrong?" — its answer is either the
missing sentence, an organization fix, or proof you need a stronger foundational
principle ("violating the letter is violating the spirit").

## Bulletproof =

correct choice under maximum pressure + cites the skill + acknowledges the
temptation + meta-test returns "the skill was clear". Not bulletproof: hybrid
approaches, arguing the skill is wrong, new rationalizations each round.

## Checklist before /ms.sync of a discipline-skill edit

- [ ] RED baseline ran without the (new version of the) skill; failures captured verbatim
- [ ] Edit addresses those failures specifically
- [ ] GREEN re-run complies under a 3+-pressure scenario
- [ ] New rationalizations countered (negation + table + red flag + description)
- [ ] Final re-run: compliant, cites the skill

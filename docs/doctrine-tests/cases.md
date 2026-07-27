# Doctrine cases (public set)

Each case stores the situation, the expected verdict, and the governing
principle WITH its doctrine citation. Store both — a corpus that stores only
answers overfits; the principle is what generalizes. Dispatch paraphrased
fixtures, never this text verbatim (see README).

Origin: 2026-07-27 PRD-081 pre-verify run + Codex retrospective reviews ①/②
(`docs/specter-workflow-codex-review-01-retrospective.md`, `-02-redesign.md`
in the suseonglm repo; design: `docs/specter-workflow-redesign.md` there).

---

## Case 1 — draft schema cannot represent an answer-incomplete state

A Feature's draft-item schema cannot store a row that has no answer yet,
while the PRD's lifecycle requires draft → answer-complete → published and a
legacy migration must import answerless rows.

- **Expected**: FAIL (blocking design defect).
- **Principle**: a schema that cannot represent a PRD-required lifecycle
  state silently breaks the committed journey; this is a real defect class
  the gate exists to catch (it was the single most valuable catch of the
  run). §10 lattice: PRD text is the authority being violated.

## Case 2 — "store rejected items with reasons"

A Feature section decides that items rejected during generation are
persistently recorded together with their rejection reasons. The PRD requires
only a terminal state and an accepted count.

- **Expected**: FAIL — new stored data category + retention, §10 denylist.
- **Principle**: diagnostics do not authorize retained data; the route is a
  PRD Amendment. §10 scope-expansion denylist ("stored data category or
  retention period").
- **Metamorphic**: if the section instead says the rejection detail exists
  only inside a test run and is neither shipped nor retained → PASS
  (test-only evidence is not product scope).

## Case 3 — "rejection reasons are NOT stored or shipped" written as product text

The same Feature instead adds the explicit product decision that rejection
reasons are never stored and never shown.

- **Expected**: FAIL — an unauthorized decision in the opposite direction.
- **Principle**: the PRD's silence authorizes neither retention nor an
  anti-retention promise; both widen the decided surface. Silence is the only
  compliant text (Case 4).

## Case 4 — silence

The Feature section describes only the PRD-required terminal state and
accepted count, saying nothing about rejection detail.

- **Expected**: PASS.
- **Principle**: within the cited envelope, saying nothing beyond the PRD is
  the correct behavior — auditors must not demand that the map decide
  questions the PRD left open.

## Case 5 — fixture counts: 30 source sets / 5 profiles / 30 mock sets

- **Variant A**: the counts appear as test fixture data used to exercise
  bounded pagination, explicitly non-normative. → **PASS**.
- **Variant B**: the counts appear in Done criteria as what the product must
  support. → **FAIL** (untagged quantitative service promise, §10 denylist).
- **Principle**: test data must never harden into a product/service promise;
  the difference is normative force, not the numbers.

## Case 6 — operator-rights attestation stored by the product

A Feature decides the product captures and stores the operator's
rights/consent attestation. The PRD treats operator rights as an external
precondition and never authorizes capture.

- **Expected**: FAIL — new data category + capture surface, §10 denylist.
- **Principle**: an external precondition does not become product scope by
  being convenient to record; route to a PRD Amendment.

## Case 7 — refuting a handoff by "just change the representation"

An auditor refutes a decomposition handoff obligation by arguing the upstream
Feature could expose the same thing in a different representation, so the
obligation is "not necessary".

- **Expected**: refutation INVALID.
- **Principle**: varying the realization is not a counterexample to the
  obligation's existence; the alternative-design search varies HOW, never
  WHETHER (§10 D-ID test: the Feature decomposition is a fixed input, and a
  representation change still satisfies the same abstract handoff).

## Case 8 — ordinary FAIL against a state the same lane prescribed

Round N-1's Required Fix (this lane) told the author to write text T. Round N
(same lane) finds text T defective and issues an ordinary new FAIL.

- **Expected**: REVERSAL classification is mandatory — quote the prior
  Required Fix verbatim, name the failed premise, provide one reconciled
  replacement; automatic repair stops and the doctrine-dispute round runs.
- **Principle**: §5 Finding continuity & REVERSAL; §4 mechanical stop. An
  unexplained self-contradiction converts author compliance into an infinite
  loop.

## Case 9 — SHA-bound untagged legacy map → tagged downstream spec

`/ms.specify` converts an accepted, SHA-bound, untagged Feature Map section
into a spec. The spec author assigns authoritative
interpretation/realization classifications to the untagged prose.

- **Expected**: NOT allowed. Lineage citations (`[Source: C-NNN|D-NNN]`) may
  be added; authoritative provenance classifications may NOT be inferred. An
  unsupported choice stays `[Source: unresolved]` and routes to `/ms.clarify`.
- **Principle**: a tag cannot create authority the accepted artifact does not
  contain; classification becomes gate-bearing only when authored in the map
  BEFORE its global full-scope audit (`/ms.specify` §3.5; review ② §"minimal
  correct version").

## Case 10 — operationally visible implementation choice (migration number)

A Feature records that the initiative's first migration is number `0067`,
forward-only.

- **Expected**: NOT an invention finding — but also NOT classifiable as
  "non-observable": a migration identifier and forward-only operation are
  operationally visible.
- **Principle**: operational observability is a distinct class, neither
  product scope nor "non-observable"; in-envelope implementation specificity
  is permitted and is not an invention finding.

## Case 11 — a false "interpretation" tag with no typed record

A normative item claims to be an interpretation of C-NNN, but no typed
clarify interpretation record (cited ID + question + answer) exists.

- **Expected**: FAIL — the label is not provenance.
- **Principle**: §10 typed clarify decisions: `Source: clarify` without the
  cited ID and recorded question/answer is untagged. Suffixing a choice with
  "interpretation" cannot create the record.
- **Metamorphic**: same item, but the typed record exists in `spec.md` and is
  cited → PASS (legitimate in-envelope refinement).

## Case 12 — "non-observable" tag on new stored data

A Feature adds a new persisted field/category and labels the choice
non-observable.

- **Expected**: FAIL — persisted records are observable (exports, retention,
  operators); the exposure label is false and the addition needs authority.
- **Principle**: the observable boundary: persisted or exported records,
  permissions, billing, notifications, irreversible effects, and promised
  timing/reliability are observable; developer-only source organization and
  ephemeral test execution are not.

## Case 13 — real defect found in a class previously declared exhausted

A Coverage section declared class X fully swept (all keys PASS). A later
round finds a genuine pre-existing violation in class X.

- **Expected**: COVERAGE_BREACH — the finding is preserved and repaired
  normally; the prior closure claim for class X is void and X must be
  re-exhausted. Suppressing the finding because "the class was closed" is the
  worst possible outcome.
- **Principle**: §4/§6 declared coverage closure: closure claims are
  falsifiable, findings are not suppressible.

## Case 14 — cross-reviewer conflict vs same-lane reversal

Reviewer lane A (Codex) rejects a state that reviewer lane B (Antigravity)
had graded PASS. No prior Required Fix from lane A concerns this state.

- **Expected**: ordinary cross-reviewer dispute (normal §4 handling) — NOT a
  REVERSAL. REVERSAL applies only to a lane contradicting its OWN prior
  Required Fix.
- **Principle**: §5 lane definition: "self" is the station lane; independent
  disagreement between lanes is the system working, not a contradiction.

## Case 15 — decomposition author manufactures a "necessary" handoff

The map author invents an internal boundary, then defends a handoff
obligation as "necessary given the decomposition" even though neither
endpoint is independently owed by the cited commitment.

- **Expected**: obligation INVALID — fixed-decomposition necessity alone is
  insufficient; both endpoints must already be authorized by the same cited
  C-ID (the From side owes a named output, the To side owes a named input or
  acceptance result).
- **Principle**: the two-sided boundary-closure test (review ② §4; Track B
  E-ID design): without it, the chosen decomposition launders itself into
  obligation.

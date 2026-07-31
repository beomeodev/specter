---
description: "Create the technical plan for a clarified Feature"
argument-hint: ""
---

# /ms.plan

Delegate the base plan to `/speckit-plan`, then make it repository-real.

Read the clarified spec, Feature Map context, Constitution, and relevant source,
tests, schemas, routes, migrations, and tooling. Prefer Graphify first when
available and verify its file/line pointers.

Authority is progressive: plan owns technical design inside the spec's observable
behavior. A concrete architecture choice is not blocked because PRD text is more
abstract. If repository evidence corrects an assumption, record the correction.
Only a product boundary change or unresolved conflict routes back to clarify.

The plan must state:

- architecture and files/components to change
- interfaces, data flow, error handling, and security boundaries
- test strategy mapped to Done criteria
- migration/recovery strategy when applicable
- state ownership and invariants when state is duplicated or transitions
- exact repository commands for targeted implementation checks and final review

Run cheap mechanical reality checks now: paths, symbols, migration index, config
names, and command availability. Fix mechanical drift directly. Do not add
fingerprints, receipts, D-IDs, risk profiles, Verification signals, or a human
approval checkpoint.

Return PASS/WARN or FAIL. WARN continues without acknowledgment.

Next: `/ms.tasks`.

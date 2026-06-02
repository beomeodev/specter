# My-Spec Helper Libraries

TypeScript helper libraries for TAG traceability reporting and TRUST checks.

These helpers support the `/ms.*` workflow, but the active Constitution remains
the source of truth for policy. The helpers report findings; `/ms.review`, CI, or
explicit project rules decide whether findings block delivery.

## Current Policy

- TAGS are best-effort grep traceability, not a substitute for tests or review.
- TAG integrity findings are warnings by default unless Section IX of the active
  Constitution or CI explicitly promotes them to blockers.
- Use file-level TAG blocks only. Do not add line-level `@TEST` tags to every
  test function.
- Multiple implementation files may share the same `@CODE:TAG-ID`.
- Multiple test files may share the same `@TEST:TAG-ID`.
- `@DOC` is optional.
- Prefer ASCII chains: `@SPEC:ID -> @TEST:ID -> @CODE:ID -> @DOC:ID`.
- `@CREATED` and `@UPDATED` are optional. If present, `@UPDATED` must reflect git
  reality or be omitted.
- Production files target `<=700` SLOC. Test files have no SLOC limit.

## TAG Helpers

### Capabilities

- Generate TAG IDs from Functional Requirement domains.
- Scan files with `rg` for `@SPEC`, `@TEST`, `@CODE`, and `@DOC` tags.
- Parse TAG chains written with `->` or the legacy unicode arrow.
- Report orphaned TAGs, duplicate SPEC TAGs, broken chain references, and chain
  format issues.
- Generate human-readable TAG integrity reports for `/ms.review` or CI.

### Example

```typescript
import { TAG } from './index';

const domain = TAG.extractDomain('User Authentication', 'FR-1');
const count = await TAG.countTAGsForDomain(domain.domain);
const tagId = TAG.generateNextTAGID(domain.domain, count);
const chain = TAG.generateTAGChain(tagId);

console.log(tagId); // AUTH-001
console.log(chain); // @SPEC:AUTH-001 -> @TEST:AUTH-001 -> @CODE:AUTH-001
```

### File-Level TAG Block

```typescript
/**
 * @CODE:AUTH-001
 * @SPEC: specs/001-auth/spec.md
 * @TEST: tests/auth.test.ts
 * @CHAIN: @SPEC:AUTH-001 -> @TEST:AUTH-001 -> @CODE:AUTH-001
 * @STATUS: implemented
 */
```

## TRUST Helpers

TRUST is a review model, not a claim that every check is available in every
repository.

### Levels

- Level 1: structure checks, `.env` ignore checks, production file SLOC checks.
- Level 2: project test, lint, and typecheck commands where available.
- Level 3: coverage, complexity, circular dependency, security, and TAG reports
  where tooling exists.

### Example

```typescript
import { TRUST } from './index';

const result = await TRUST.runTRUSTVerification('/project/root');
console.log(result.report);
console.log(result.summary);
```

Use this result as input to `/ms.review` or CI. Do not claim the branch is ready
unless the relevant executable checks actually ran and passed.

## Project Structure

```text
lib/
  scripts/
    check-prerequisites.sh
  tag/
    types.ts
    generator.ts
    scanner.ts
    validator.ts
    index.ts
  trust/
    types.ts
    level1.ts
    level2.ts
    level3.ts
    reporter.ts
    index.ts
README.md
```

## Development

```bash
# Scan TAGs, requires ripgrep
node -e "const { TAG } = require('./dist/index'); TAG.scanAllTAGs('.').then(console.log)"

# Run TRUST report
node -e "const { TRUST } = require('./dist/index'); TRUST.runTRUSTVerification('.').then(r => console.log(r.report))"
```

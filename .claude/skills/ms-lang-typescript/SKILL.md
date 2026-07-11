---
name: ms-lang-typescript
description: TypeScript development standards for SPECTER TDD work — Vitest test structure and test-quality doctrine (mock only at system boundaries, no tautological tests), Biome lint/format configuration, strict tsconfig with advanced type patterns (satisfies, const type parameters), Zod runtime validation and type-safe environment variables, Constitution limits (≤700 SLOC production files, ≤10 complexity, ≥85% coverage), and TAG block integration, with React/Next.js reference patterns (Error Boundaries, Server Actions). Use when writing or reviewing TypeScript/TSX code, writing Vitest tests, implementing React or Next.js applications, or configuring TypeScript tooling.
---

# Language: TypeScript (5.x strict)

Standard toolchain for SPECTER TypeScript work. These are the project defaults —
deviate only when the target repo already standardizes on something else.

| Tool | Role | Replaces |
|------|------|----------|
| Vitest | Testing | Jest |
| Biome | Lint + format + import sort | ESLint, Prettier |
| tsc strict mode | Type checking | — |
| Zod | Runtime validation | — |
| pnpm (or bun) | Package management | npm |

Versions verified 2025-10; treat current stable releases as the target and re-verify
before pinning exact versions in a new project.

## Testing (Vitest)

```typescript
// tests/unit/calculator.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { Calculator } from '@/services/calculator';

describe('Calculator', () => {
  let calculator: Calculator;

  beforeEach(() => {
    calculator = new Calculator();
  });

  it('should add two positive numbers', () => {
    expect(calculator.add(2, 3)).toBe(5);
  });
});
```

Rules: Vitest only (never Jest, never mixed), one assertion per test, "should"
naming, `beforeEach` for setup. Coverage ≥85% is enforced by the quality gate.

```bash
vitest                # watch mode
vitest run --coverage # CI mode + coverage (≥85% required)
```

### Test quality (not just mechanics)

Prefer integration-style tests through the public API over mocking internal collaborators —
tests should describe WHAT the code does for a caller, not HOW it does it internally, and should
survive a refactor that doesn't change behavior.

Named anti-patterns to catch in review:
- **Implementation-detail coupling**: mocking internal collaborators, asserting on call
  counts/order, or testing private methods — breaks on refactors with no behavior change.
- **Side-channel verification**: bypassing the public interface to check state directly (e.g.
  querying the DB row instead of calling the retrieval function) instead of verifying through the
  same interface a caller would use.
- **Tautological tests**: the expected value is recomputed the same way the implementation
  computes it (e.g. `expected = items.reduce(...)` mirroring the function under test) — use an
  independent literal (`toBe(15)`) instead, so the test can actually fail.

```typescript
// BAD: implementation-detail coupling
test("checkout calls paymentService.process", async () => {
  const mockPayment = vi.mocked(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});

// GOOD: verifies observable behavior through the public interface
test("user can checkout with valid cart", async () => {
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

**Mock only at system boundaries** (external APIs, databases — prefer a test DB, time/randomness,
filesystem) — never your own classes/modules or anything you control. Design boundary interfaces
for mockability:
- **Dependency injection**: pass the external client in as a parameter rather than constructing
  it internally, so a test can substitute a fake without reaching into module internals.
- **SDK-style discrete clients**: expose one function per external operation
  (`getUser`, `getOrders`, `createOrder`) instead of one generic `fetch(endpoint, options)` — each
  mock then returns one predictable shape with no conditional logic, and the type system checks
  each endpoint independently.

## Lint/format (Biome)

`biome.json`:

```json
{
  "organizeImports": { "enabled": true },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "complexity": {
        "noExcessiveCognitiveComplexity": {
          "level": "error",
          "options": { "maxAllowedComplexity": 10 }
        }
      },
      "style": { "useConst": "error", "noVar": "error" }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "javascript": {
    "formatter": { "quoteStyle": "single", "semicolons": "always" }
  }
}
```

```bash
biome check --write .  # lint + format with auto-fix
biome check .          # check only (CI)
```

## Typing (tsc strict + patterns)

`tsconfig.json` essentials:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "moduleResolution": "bundler",
    "isolatedModules": true,
    "paths": { "@/*": ["src/*"] }
  }
}
```

Patterns to prefer:

```typescript
// Discriminated union for API responses
type ApiResponse<T> =
  | { success: true; data: T }
  | { success: false; error: string };

// satisfies — type check without widening
const routes = {
  home: '/',
  about: '/about',
} satisfies Record<string, string>;  // routes.home stays typed as '/'

// const type parameters — infer exact literal types
function createTuple<const T extends readonly unknown[]>(...items: T): T {
  return items;
}
```

```bash
tsc --noEmit           # type check (quality gate)
```

## Runtime validation (Zod)

Validate at boundaries — user input, API payloads, and environment variables:

```typescript
import { z } from 'zod';

const userInputSchema = z.object({
  username: z.string().min(3).max(20).regex(/^[a-zA-Z0-9_]+$/),
  email: z.string().email(),
  age: z.number().int().min(13).max(120),
});
type UserInput = z.infer<typeof userInputSchema>;

// src/env.ts — type-safe environment variables, parsed once at startup
const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  API_KEY: z.string().min(32),
  NODE_ENV: z.enum(['development', 'production', 'test']),
});
export const env = envSchema.parse(process.env);
```

## Packages (pnpm)

```bash
pnpm add typescript vitest @biomejs/biome
pnpm add -D @types/node
pnpm add react react-dom next          # if React/Next.js
```

Bun is an acceptable alternative when the project already uses it.

## TDD loop and quality gate

```bash
vitest                 # RED: watch the new test fail
# [implement]
vitest                 # GREEN
biome check --write .  # REFACTOR

# Quality gate (before commit):
vitest run --coverage  # coverage ≥85%?
biome check .          # lint pass?
tsc --noEmit           # types pass?
```

## Constitution compliance

- Production files ≤700 SLOC (split if larger); test files: no limit
- Functions ≤100 lines, complexity ≤10 (Biome `noExcessiveCognitiveComplexity`)
- Coverage ≥85%, strict mode on, TAG blocks in all files

## DO / DON'T

DO: strict mode always, `satisfies` and const assertions, type annotations on public
APIs, `unknown` + narrowing instead of `any`, quality gate before every commit.

DON'T: Jest (Vitest replaces it), ESLint+Prettier (Biome replaces both), `any`,
silencing type errors without `@ts-expect-error` and a reason, mixing test frameworks,
skipping coverage (<85% fails the gate).

## TAG blocks

`ms-workflow-tag-manager` is the canonical source for TAG generation. TypeScript format:

```typescript
/**
 * @CODE:AUTH-001
 * @SPEC: specs/001-auth-spec/spec.md
 * @TEST: tests/unit/auth.test.ts
 * @CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
 * @STATUS: implemented
 */
```

Test files use `@TEST:` as the leading tag with `@CODE:` pointing back to the source.

## Reference files (load only when needed)

- **React/Next.js patterns** (type-safe components, Server Actions, Error Boundaries,
  App Router error files, monitoring integration):
  see [references/react-nextjs.md](references/react-nextjs.md)
- **Worked examples** (full TDD cycles, Vitest fixtures, async tests):
  see [examples.md](examples.md)

## Works well with

`ms-foundation-trust` (TRUST 5 validation), `ms-foundation-constitution` (size/complexity
checks), `ms-workflow-tag-manager` (TAG generation), `ms-workflow-living-docs` (doc sync).

---
name: ms-lang-typescript
description: TypeScript 5.7+ development expertise with modern toolchain - Vitest 2.1 for 10x faster testing with native ESM support, Biome 1.9 for unified linting and formatting (75x faster than ESLint), strict type checking with advanced patterns (const type parameters, satisfies operator), React 19 and Next.js 15 integration with Error Boundaries and Suspense patterns, Zod runtime validation, type-safe environment variables, Constitution compliance (≤700 SLOC production / tests no limit, ≤10 complexity), and comprehensive TDD workflow with TAG block integration. Use when working with TypeScript/TSX files, writing Vitest tests, implementing React/Next.js applications, enforcing type safety, or applying TypeScript best practices
---

# Language: TypeScript 5.7+ Expert

## What it does

Provides **TypeScript 5.7+ expertise** for SPECTER TDD development, including:

- ✅ **Testing Framework**: Vitest 2.1+ (fast, modern alternative to Jest)
- ✅ **Code Quality**: Biome 1.9+ (unified linter + formatter, replaces ESLint + Prettier)
- ✅ **Type Safety**: TypeScript 5.7+ strict mode with advanced patterns
- ✅ **Package Management**: npm/pnpm/bun (project preference)
- ✅ **TypeScript 5.7 Features**: Decorators, const type parameters, satisfies operator
- ✅ **React/Next.js**: Modern patterns with TypeScript integration
- ✅ **Constitution Compliance**: TRUST 5 principles, ≤700 SLOC production files (tests: no limit), ≤10 complexity

## When to use

**Automatic triggers**:
- TypeScript code discussions, `.ts`/`.tsx` files
- "Writing TypeScript tests", "How to use Vitest", "TypeScript type hints"
- TypeScript SPEC implementation (`/ms.implement`)
- React/Next.js component development

**Manual invocation**:
- Review TypeScript code for TRUST 5 compliance
- Design TypeScript APIs or React components
- Troubleshoot type errors or build issues
- Migrate JavaScript to TypeScript

## How it works (Best Practices)

### 1. Testing Framework (Vitest 2.1+)

**Why Vitest over Jest?**
- ⚡ **10x faster** than Jest (native ESM support)
- 🔧 **Zero config** for TypeScript
- ✅ **Jest-compatible API** (easy migration)
- 🎯 **Built-in coverage** with c8/v8

**Test Structure**:
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
    const result = calculator.add(2, 3);
    expect(result).toBe(5);
  });

  it('should handle negative numbers', () => {
    const result = calculator.add(-2, 3);
    expect(result).toBe(1);
  });
});
```

**Key Points**:
- ✅ Use Vitest (not Jest) for TypeScript projects
- ✅ One assertion per test (clarity)
- ✅ Descriptive test names ("should" convention)
- ✅ `beforeEach` for setup/teardown
- ✅ Coverage ≥85% enforced by quality gate

**CLI Commands**:
```bash
vitest                              # Run all tests (watch mode)
vitest run                          # Run once (CI mode)
vitest --coverage                   # Generate coverage report (≥85% required)
vitest --ui                         # Interactive UI
vitest tests/unit/calculator.test.ts # Run specific test
```

**Test Quality (not just mechanics)**:

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
  const mockPayment = jest.mock(paymentService);
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

### 2. Code Quality (Biome 1.9+)

**Why Biome over ESLint + Prettier?**
- ⚡ **75x faster** than ESLint
- 🔧 **Single tool** (linting + formatting)
- ✅ **TypeScript-first** design
- 🎯 **Zero dependencies** (Rust-based)

**Configuration** (`biome.json`):
```json
{
  "$schema": "https://biomejs.dev/schemas/1.9.4/schema.json",
  "organizeImports": {
    "enabled": true
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "complexity": {
        "noExcessiveCognitiveComplexity": {
          "level": "error",
          "options": {
            "maxAllowedComplexity": 10
          }
        }
      },
      "style": {
        "useConst": "error",
        "noVar": "error"
      }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "semicolons": "always"
    }
  }
}
```

**CLI Commands**:
```bash
biome check .                       # Lint + format check
biome check --write .               # Lint + format with auto-fix
biome format --write .              # Format only
biome lint .                        # Lint only
```

### 3. Type Safety (TypeScript 5.7+ Strict Mode)

**tsconfig.json** (strict configuration):
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*", "tests/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**Advanced Type Patterns**:
```typescript
// Type-safe API response
type ApiResponse<T> =
  | { success: true; data: T }
  | { success: false; error: string };

// Generic with constraints
function filterItems<T extends { id: number }>(
  items: T[],
  predicate: (item: T) => boolean
): T[] {
  return items.filter(predicate);
}

// Const type parameters (TypeScript 5.7)
function createSet<const T extends readonly unknown[]>(
  ...items: T
): Set<T[number]> {
  return new Set(items);
}

// Satisfies operator (TypeScript 5.7)
const config = {
  endpoint: '/api/users',
  timeout: 5000,
} satisfies Record<string, string | number>;
```

**CLI Commands**:
```bash
tsc --noEmit                        # Type check without output
tsc --noEmit --watch                # Type check in watch mode
tsc --build                         # Build project
```

### 4. Package Management

**Recommended**: Use pnpm for faster installs and disk efficiency.

**Setup**:
```bash
# Install pnpm
npm install -g pnpm

# Initialize project
pnpm init

# Install dependencies
pnpm add typescript vitest @vitest/ui @biomejs/biome
pnpm add -D @types/node

# Install framework dependencies (React/Next.js)
pnpm add react react-dom next
pnpm add -D @types/react @types/react-dom
```

**Alternative**: Bun (fastest runtime + package manager):
```bash
# Install Bun
curl -fsSL https://bun.sh/install | bash

# Initialize project
bun init

# Install dependencies
bun add typescript vitest @biomejs/biome
```

### 5. React/Next.js Patterns

**Type-safe React Component**:
```typescript
// src/components/UserCard.tsx
import { type FC } from 'react';

interface UserCardProps {
  name: string;
  email: string;
  age?: number;
}

export const UserCard: FC<UserCardProps> = ({ name, email, age }) => {
  return (
    <div className="user-card">
      <h2>{name}</h2>
      <p>{email}</p>
      {age !== undefined && <p>Age: {age}</p>}
    </div>
  );
};
```

**Next.js Server Action (TypeScript 5.7)**:
```typescript
// app/actions/user.ts
'use server';

import { z } from 'zod';

const userSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

export async function createUser(formData: FormData): Promise<ApiResponse<{ id: number }>> {
  const data = {
    name: formData.get('name'),
    email: formData.get('email'),
  };

  const validation = userSchema.safeParse(data);

  if (!validation.success) {
    return { success: false, error: validation.error.message };
  }

  // Save to database...
  return { success: true, data: { id: 1 } };
}
```

### 6. Security Best Practices

**Input Validation** (Zod):
```typescript
import { z } from 'zod';

const userInputSchema = z.object({
  username: z.string().min(3).max(20).regex(/^[a-zA-Z0-9_]+$/),
  email: z.string().email(),
  age: z.number().int().min(13).max(120),
});

type UserInput = z.infer<typeof userInputSchema>;

function validateUserInput(data: unknown): UserInput {
  return userInputSchema.parse(data); // Throws if invalid
}
```

**Environment Variables** (type-safe):
```typescript
// src/env.ts
import { z } from 'zod';

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  API_KEY: z.string().min(32),
  NODE_ENV: z.enum(['development', 'production', 'test']),
});

export const env = envSchema.parse(process.env);
```

### 7. React Error Boundaries (Production Must-Have)

**Why Error Boundaries?**
- ✅ **Catch runtime errors** in React component tree
- ✅ **Prevent app crash** from a single component error
- ✅ **Show fallback UI** instead of blank page
- ✅ **Log errors** to monitoring services (Sentry, DataDog)

**Error Boundary Class Component**:
```typescript
// src/components/ErrorBoundary.tsx
import { Component, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so next render shows fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to error tracking service
    console.error('ErrorBoundary caught:', error, errorInfo);

    // Call custom error handler
    this.props.onError?.(error, errorInfo);

    // Example: Send to Sentry
    // Sentry.captureException(error, { extra: errorInfo });
  }

  render() {
    if (this.state.hasError) {
      // Render fallback UI
      return (
        this.props.fallback ?? (
          <div className="error-container">
            <h1>Something went wrong</h1>
            <p>{this.state.error?.message}</p>
            <button onClick={() => this.setState({ hasError: false })}>
              Try again
            </button>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
```

**Usage in App**:
```typescript
// app/layout.tsx (Next.js App Router)
import { ErrorBoundary } from '@/components/ErrorBoundary';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ErrorBoundary fallback={<ErrorFallback />}>
          {children}
        </ErrorBoundary>
      </body>
    </html>
  );
}

// Custom fallback component
function ErrorFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold">Oops! Something went wrong</h1>
        <p className="mt-4">We're working on fixing this issue.</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-6 px-4 py-2 bg-blue-500 text-white rounded"
        >
          Reload page
        </button>
      </div>
    </div>
  );
}
```

**Multiple Error Boundaries** (granular error handling):
```typescript
// app/dashboard/page.tsx
import { ErrorBoundary } from '@/components/ErrorBoundary';

export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* Separate error boundary for each section */}
      <ErrorBoundary fallback={<div>Failed to load stats</div>}>
        <StatsWidget />
      </ErrorBoundary>

      <ErrorBoundary fallback={<div>Failed to load chart</div>}>
        <ChartWidget />
      </ErrorBoundary>

      <ErrorBoundary fallback={<div>Failed to load table</div>}>
        <DataTable />
      </ErrorBoundary>
    </div>
  );
}
```

**Next.js 15 App Router Alternative** (error.tsx):
```typescript
// app/error.tsx
'use client'; // Error components must be Client Components

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to error reporting service
    console.error('App error:', error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold">Something went wrong!</h2>
      <p className="mt-2 text-gray-600">{error.message}</p>
      <button
        onClick={reset}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
      >
        Try again
      </button>
    </div>
  );
}
```

**Global error handler** (app/global-error.tsx):
```typescript
// app/global-error.tsx
'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <h2>Global Error: Something went wrong!</h2>
        <button onClick={reset}>Try again</button>
      </body>
    </html>
  );
}
```

**Testing Error Boundaries**:
```typescript
// tests/unit/ErrorBoundary.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ErrorBoundary } from '@/components/ErrorBoundary';

function ThrowError() {
  throw new Error('Test error');
}

describe('ErrorBoundary', () => {
  it('should catch errors and show fallback', () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <ErrorBoundary fallback={<div>Error occurred</div>}>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText('Error occurred')).toBeDefined();

    consoleSpy.mockRestore();
  });

  it('should call onError handler', () => {
    const onError = vi.fn();

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(onError).toHaveBeenCalled();
  });

  it('should recover after error', async () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeDefined();

    // Rerender with valid component
    rerender(
      <ErrorBoundary>
        <div>Success</div>
      </ErrorBoundary>
    );

    // Error boundary should reset
    expect(screen.getByText('Success')).toBeDefined();
  });
});
```

**Integration with Error Monitoring** (Sentry example):
```typescript
// src/lib/error-tracking.ts
import * as Sentry from '@sentry/nextjs';

export function initErrorTracking() {
  Sentry.init({
    dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
    environment: process.env.NODE_ENV,
    tracesSampleRate: 1.0,
  });
}

// src/components/ErrorBoundary.tsx (enhanced)
export class ErrorBoundary extends Component<Props, State> {
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Send to Sentry with additional context
    Sentry.captureException(error, {
      contexts: {
        react: {
          componentStack: errorInfo.componentStack,
        },
      },
    });

    this.props.onError?.(error, errorInfo);
  }
}
```

## TypeScript 5.7 New Features

### Const Type Parameters
```typescript
// Infer exact literal types
function createTuple<const T extends readonly unknown[]>(...items: T): T {
  return items;
}

const tuple = createTuple(1, 'hello', true);
// Type: readonly [1, 'hello', true] (not number | string | boolean)
```

### Satisfies Operator
```typescript
// Type check without widening
const routes = {
  home: '/',
  about: '/about',
  contact: '/contact',
} satisfies Record<string, string>;

// routes.home is typed as '/' (not string)
```

## Constitution Compliance

**SPECTER Requirements**:
- ✅ Production files ≤700 SLOC (split if larger); test files: no limit
- ✅ Functions ≤100 lines
- ✅ Complexity ≤10 per function
- ✅ Test coverage ≥85%
- ✅ Strict typing enabled
- ✅ TAG blocks in all files

**File Size Check**:
```bash
# Count SLOC (excluding comments/blank lines)
cloc src/components/UserCard.tsx --by-file
```

**Complexity Check**:
```bash
# Biome checks complexity automatically
biome check . --max-diagnostics=0
```

## Tool Version Matrix (2025-10-26)

| Tool | Version | Purpose | Status |
|------|---------|---------|--------|
| **TypeScript** | 5.7.2 | Primary | ✅ Latest |
| **Vitest** | 2.1.0 | Testing | ✅ Current |
| **Biome** | 1.9.4 | Lint/Format | ✅ Current |
| **pnpm** | 9.14.2 | Package mgmt | ✅ Recommended |
| **Bun** | 1.1.0 | Runtime | ✅ Alternative |
| **React** | 19.0.0 | UI Library | ✅ Latest |
| **Next.js** | 15.1.0 | Framework | ✅ Latest |

## Example Workflow

**Setup** (pnpm + TypeScript 5.7):
```bash
pnpm init
pnpm add typescript vitest @biomejs/biome
pnpm add -D @types/node

# Create tsconfig.json
npx tsc --init --strict
```

**TDD Loop**:
```bash
vitest                              # RED: Watch tests fail
# [implement code]
vitest                              # GREEN: Watch tests pass
biome check --write .               # REFACTOR: Fix code quality
```

**Quality Gate** (before commit):
```bash
vitest run --coverage               # Coverage ≥85%?
biome check .                       # Lint pass?
tsc --noEmit                        # Type check pass?
```

## Best Practices

✅ **DO**:
- Use Vitest for all tests (not Jest)
- Enable TypeScript strict mode
- Use Biome for linting + formatting (not ESLint + Prettier)
- Specify exact TypeScript version in package.json
- Run quality gate before each commit
- Use const assertions and satisfies operator
- Add type annotations to public APIs
- Keep production files ≤700 SLOC (Constitution requirement); test files: no limit

❌ **DON'T**:
- Use Jest (Vitest is faster and better for TS)
- Use ESLint + Prettier (Biome replaces both)
- Use `any` type (use `unknown` instead)
- Ignore type errors (fix them or use explicit `@ts-expect-error`)
- Mix testing frameworks
- Skip coverage requirements (<85% fails)
- Use old TypeScript syntax (upgrade to 5.7+)

## Integration with SPECTER

**TAG Block Format** (TypeScript):
```typescript
/**
 * @CODE:AUTH-001
 * @SPEC: specs/001-auth-spec/spec.md
 * @TEST: tests/unit/auth.test.ts
 * @CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
 * @STATUS: implemented
 * @CREATED: 2025-10-26
 * @UPDATED: 2025-10-26
 */
export class AuthService {
  // Implementation...
}
```

**Test TAG Block**:
```typescript
/**
 * @TEST:AUTH-001
 * @SPEC: specs/001-auth-spec/spec.md
 * @CODE: src/services/auth.ts
 * @CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
 * @STATUS: passing
 */
describe('AuthService', () => {
  // Tests...
});
```

## References (Latest Documentation)

- **TypeScript 5.7**: https://www.typescriptlang.org/docs/ (accessed 2025-10-26)
- **Vitest 2.1**: https://vitest.dev/ (accessed 2025-10-26)
- **Biome 1.9**: https://biomejs.dev/ (accessed 2025-10-26)
- **pnpm**: https://pnpm.io/ (accessed 2025-10-26)
- **React 19**: https://react.dev/ (accessed 2025-10-26)
- **Next.js 15**: https://nextjs.org/docs (accessed 2025-10-26)

## Changelog

- **v1.0.0** (2025-10-26): Initial TypeScript Skill for SPECTER workflow with Vitest 2.1, Biome 1.9, TypeScript 5.7, Constitution compliance

## Works Well With

- `ms-foundation-trust` (TRUST 5 validation)
- `ms-foundation-constitution` (file size/complexity checks)
- `ms-workflow-tag-manager` (TAG block generation)
- `ms-workflow-living-docs` (API documentation sync)

---
name: ms-lang-typescript
description: TypeScript 5.7+ development expertise with modern toolchain - Vitest 2.1 for 10x faster testing with native ESM support, Biome 1.9 for unified linting and formatting (75x faster than ESLint), strict type checking with advanced patterns (const type parameters, satisfies operator), React 19 and Next.js 15 integration, Zod runtime validation, Constitution compliance (≤500 SLOC, ≤10 complexity), and comprehensive TDD workflow with TAG block integration
---

# Language: TypeScript 5.7+ Expert

## Skill Metadata
| Field | Value |
| ----- | ----- |
| Version | 1.0.0 |
| Created | 2025-10-26 |
| TypeScript Support | 5.7+ (latest) |
| Allowed tools | Read, Bash, Grep |
| Auto-load | On demand when `.ts`, `.tsx` files detected |
| Trigger cues | TypeScript files, type safety, React/Next.js development |

## What it does

Provides **TypeScript 5.7+ expertise** for My-Spec TDD development, including:

- ✅ **Testing Framework**: Vitest 2.1+ (fast, modern alternative to Jest)
- ✅ **Code Quality**: Biome 1.9+ (unified linter + formatter, replaces ESLint + Prettier)
- ✅ **Type Safety**: TypeScript 5.7+ strict mode with advanced patterns
- ✅ **Package Management**: npm/pnpm/bun (project preference)
- ✅ **TypeScript 5.7 Features**: Decorators, const type parameters, satisfies operator
- ✅ **React/Next.js**: Modern patterns with TypeScript integration
- ✅ **Constitution Compliance**: TRUST 5 principles, ≤500 SLOC files, ≤10 complexity

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

**My-Spec Requirements**:
- ✅ Files ≤500 SLOC (split if larger)
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
- Keep files ≤500 SLOC (Constitution requirement)

❌ **DON'T**:
- Use Jest (Vitest is faster and better for TS)
- Use ESLint + Prettier (Biome replaces both)
- Use `any` type (use `unknown` instead)
- Ignore type errors (fix them or use explicit `@ts-expect-error`)
- Mix testing frameworks
- Skip coverage requirements (<85% fails)
- Use old TypeScript syntax (upgrade to 5.7+)

## Integration with My-Spec

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

- **v1.0.0** (2025-10-26): Initial TypeScript Skill for My-Spec workflow with Vitest 2.1, Biome 1.9, TypeScript 5.7, Constitution compliance

## Works Well With

- `ms-foundation-trust` (TRUST 5 validation)
- `ms-foundation-constitution` (file size/complexity checks)
- `ms-workflow-tag-manager` (TAG block generation)
- `ms-workflow-living-docs` (API documentation sync)

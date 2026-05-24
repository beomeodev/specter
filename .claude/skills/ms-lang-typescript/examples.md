# TypeScript 5.7 Code Examples

Production-ready examples for modern TypeScript development with Vitest 2.1, Biome 1.9, and My-Spec TRUST 5 principles.

---

## Example 1: Vitest 2.1 with Fixtures and Async Tests

### Test File: `tests/unit/user-service.test.ts`

```typescript
/**
 * @TEST:USER-001
 * @SPEC: specs/001-user-service/spec.md
 * @CODE: src/services/user-service.ts
 * @CHAIN: @SPEC:USER-001 → @TEST:USER-001 → @CODE:USER-001
 * @STATUS: passing
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { UserService } from '@/services/user-service';
import type { User } from '@/types/user';

describe('UserService', () => {
  let userService: UserService;

  beforeEach(() => {
    userService = new UserService();
  });

  it('should create a user with valid data', () => {
    const user: User = {
      id: 1,
      name: 'Alice',
      email: 'alice@example.com',
    };

    const result = userService.validateUser(user);

    expect(result).toBe(true);
    expect(user.id).toBeGreaterThan(0);
  });

  it('should fetch user asynchronously', async () => {
    const mockUser: User = {
      id: 1,
      name: 'Bob',
      email: 'bob@example.com',
    };

    vi.spyOn(userService, 'fetchUser').mockResolvedValue(mockUser);

    const user = await userService.fetchUser(1);

    expect(user).toEqual(mockUser);
    expect(user.name).toBe('Bob');
  });

  it.each([
    [1, 'Alice'],
    [2, 'Bob'],
    [3, 'Charlie'],
  ])('should fetch user %i with name %s', async (userId, expectedName) => {
    const mockUser: User = {
      id: userId,
      name: expectedName,
      email: `${expectedName.toLowerCase()}@example.com`,
    };

    vi.spyOn(userService, 'fetchUser').mockResolvedValue(mockUser);

    const user = await userService.fetchUser(userId);

    expect(user.name).toBe(expectedName);
  });
});
```

**Key Features**:
- ✅ Vitest test structure
- ✅ `beforeEach` for setup
- ✅ Async/await testing
- ✅ Parametrized tests with `it.each`
- ✅ Mocking with `vi.spyOn`
- ✅ TAG block for traceability

**Run Commands**:
```bash
vitest tests/unit/user-service.test.ts
vitest run --coverage
```

---

## Example 2: Biome 1.9 Configuration and Workflow

### Project Configuration: `biome.json`

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
        },
        "noForEach": "warn"
      },
      "style": {
        "useConst": "error",
        "noVar": "error",
        "useTemplate": "warn"
      },
      "suspicious": {
        "noExplicitAny": "error",
        "noDebugger": "error"
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
      "semicolons": "always",
      "trailingCommas": "es5"
    }
  }
}
```

### Example Source File: `src/utils/formatter.ts`

```typescript
/**
 * @CODE:FMT-001
 * @SPEC: specs/002-formatter/spec.md
 * @TEST: tests/unit/formatter.test.ts
 * @CHAIN: @SPEC:FMT-001 → @TEST:FMT-001 → @CODE:FMT-001
 * @STATUS: implemented
 * @CREATED: 2025-10-26
 * @UPDATED: 2025-10-26
 */

export abstract class Formatter {
  abstract format(text: string): string;
}

export class UppercaseFormatter extends Formatter {
  format(text: string): string {
    return text.trim().toUpperCase();
  }
}

export class LowercaseFormatter extends Formatter {
  format(text: string): string {
    return text.trim().toLowerCase();
  }
}

export function formatUserInfo(name: string, age: number, city: string): string {
  // TypeScript 5.7 nested f-strings equivalent (template literals)
  return `User: ${name}, Details: Age: ${age}, City: ${city.toUpperCase()}`;
}
```

**Workflow Commands**:
```bash
# Check and fix all issues
biome check --write .

# Format only
biome format --write .

# Lint only
biome lint .

# Check specific files
biome check src/utils/formatter.ts
```

---

## Example 3: Type Safety with TypeScript 5.7

### Advanced Type Patterns: `src/types/api.ts`

```typescript
/**
 * @CODE:API-001
 * @SPEC: specs/003-api-types/spec.md
 * @TEST: tests/unit/api-types.test.ts
 * @CHAIN: @SPEC:API-001 → @TEST:API-001 → @CODE:API-001
 * @STATUS: implemented
 */

// Type-safe API response union
export type ApiResponse<T> =
  | { success: true; data: T }
  | { success: false; error: string };

// Generic with constraints
export function filterItems<T extends { id: number }>(
  items: T[],
  predicate: (item: T) => boolean
): T[] {
  return items.filter(predicate);
}

// Const type parameters (TypeScript 5.7)
export function createSet<const T extends readonly unknown[]>(
  ...items: T
): Set<T[number]> {
  return new Set(items);
}

// Satisfies operator (TypeScript 5.7)
export const routes = {
  home: '/',
  about: '/about',
  contact: '/contact',
  users: '/users',
} satisfies Record<string, string>;

// Type inference preserves literal types
const userRoutes = createSet('/users', '/profile', '/settings');
// Type: Set<'/users' | '/profile' | '/settings'>

// Const assertion
export const config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000,
  retries: 3,
} as const;

// Type: { readonly apiUrl: 'https://api.example.com', readonly timeout: 5000, readonly retries: 3 }
```

### Type-safe Service: `src/services/api-client.ts`

```typescript
/**
 * @CODE:API-002
 * @SPEC: specs/003-api-types/spec.md
 * @TEST: tests/unit/api-client.test.ts
 */

import type { ApiResponse } from '@/types/api';

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`);

      if (!response.ok) {
        return {
          success: false,
          error: `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      const data = (await response.json()) as T;
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async post<T, R>(endpoint: string, body: T): Promise<ApiResponse<R>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        return {
          success: false,
          error: `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      const data = (await response.json()) as R;
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }
}
```

---

## Example 4: React Component with TypeScript

### Type-safe React Component: `src/components/UserCard.tsx`

```typescript
/**
 * @CODE:UI-001
 * @SPEC: specs/004-user-card/spec.md
 * @TEST: tests/unit/UserCard.test.tsx
 * @CHAIN: @SPEC:UI-001 → @TEST:UI-001 → @CODE:UI-001
 */

import { type FC } from 'react';

export interface UserCardProps {
  name: string;
  email: string;
  age?: number;
  role: 'admin' | 'user' | 'guest';
  onEdit?: (userId: number) => void;
}

export const UserCard: FC<UserCardProps> = ({ name, email, age, role, onEdit }) => {
  const handleEdit = () => {
    if (onEdit) {
      onEdit(1); // In production, use actual user ID
    }
  };

  return (
    <div className="user-card">
      <h2>{name}</h2>
      <p>{email}</p>
      {age !== undefined && <p>Age: {age}</p>}
      <span className={`role role-${role}`}>{role}</span>
      {onEdit && (
        <button onClick={handleEdit} type="button">
          Edit
        </button>
      )}
    </div>
  );
};
```

### Component Test: `tests/unit/UserCard.test.tsx`

```typescript
/**
 * @TEST:UI-001
 * @SPEC: specs/004-user-card/spec.md
 * @CODE: src/components/UserCard.tsx
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { UserCard, type UserCardProps } from '@/components/UserCard';

describe('UserCard', () => {
  const defaultProps: UserCardProps = {
    name: 'Alice',
    email: 'alice@example.com',
    role: 'user',
  };

  it('should render user information', () => {
    render(<UserCard {...defaultProps} />);

    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('alice@example.com')).toBeInTheDocument();
    expect(screen.getByText('user')).toBeInTheDocument();
  });

  it('should render age when provided', () => {
    render(<UserCard {...defaultProps} age={30} />);

    expect(screen.getByText('Age: 30')).toBeInTheDocument();
  });

  it('should call onEdit when edit button clicked', () => {
    const onEdit = vi.fn();
    render(<UserCard {...defaultProps} onEdit={onEdit} />);

    const editButton = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editButton);

    expect(onEdit).toHaveBeenCalledWith(1);
  });

  it('should not render edit button when onEdit not provided', () => {
    render(<UserCard {...defaultProps} />);

    const editButton = screen.queryByRole('button', { name: /edit/i });
    expect(editButton).not.toBeInTheDocument();
  });
});
```

---

## Example 5: Input Validation with Zod

### Schema Definition: `src/schemas/user.ts`

```typescript
/**
 * @CODE:VAL-001
 * @SPEC: specs/005-validation/spec.md
 * @TEST: tests/unit/user-schema.test.ts
 */

import { z } from 'zod';

export const userInputSchema = z.object({
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(20, 'Username must be at most 20 characters')
    .regex(/^[a-zA-Z0-9_]+$/, 'Username must be alphanumeric'),
  email: z.string().email('Invalid email format'),
  age: z
    .number()
    .int('Age must be an integer')
    .min(13, 'Must be at least 13 years old')
    .max(120, 'Age must be realistic'),
  role: z.enum(['admin', 'user', 'guest'], {
    errorMap: () => ({ message: 'Role must be admin, user, or guest' }),
  }),
});

export type UserInput = z.infer<typeof userInputSchema>;

export function validateUserInput(data: unknown): UserInput {
  return userInputSchema.parse(data);
}

export function safeValidateUserInput(
  data: unknown
): { success: true; data: UserInput } | { success: false; error: string } {
  const result = userInputSchema.safeParse(data);

  if (result.success) {
    return { success: true, data: result.data };
  }

  return { success: false, error: result.error.message };
}
```

### Environment Variables (Type-safe): `src/env.ts`

```typescript
/**
 * @CODE:ENV-001
 * @SPEC: specs/006-env-config/spec.md
 */

import { z } from 'zod';

const envSchema = z.object({
  DATABASE_URL: z.string().url('DATABASE_URL must be a valid URL'),
  API_KEY: z.string().min(32, 'API_KEY must be at least 32 characters'),
  NODE_ENV: z.enum(['development', 'production', 'test']),
  PORT: z.string().transform(Number).pipe(z.number().int().min(1).max(65535)),
});

export const env = envSchema.parse(process.env);
```

---

## Example 6: Quality Gate Workflow

### Setup Script: `scripts/quality-gate.sh`

```bash
#!/bin/bash
# Quality gate script for TypeScript projects
# Enforces TRUST 5 principles

set -e

echo "🔍 Running TypeScript Quality Gate..."

# 1. Type Check (Unified - Type Safety)
echo "📋 Type checking..."
tsc --noEmit

# 2. Linting (Readable - Code Quality)
echo "🧹 Linting..."
biome check .

# 3. Testing (Test First - Coverage ≥85%)
echo "🧪 Running tests..."
vitest run --coverage

# 4. Coverage Check
echo "📊 Checking coverage..."
COVERAGE=$(grep -oP '(?<=All files\s{2}\|\s{2})\d+\.\d+' coverage/coverage-summary.txt)
if (( $(echo "$COVERAGE < 85" | bc -l) )); then
  echo "❌ Coverage $COVERAGE% is below 85%"
  exit 1
fi

echo "✅ Quality gate passed!"
```

### package.json Scripts

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "lint": "biome check .",
    "lint:fix": "biome check --write .",
    "format": "biome format --write .",
    "type-check": "tsc --noEmit",
    "quality-gate": "bash scripts/quality-gate.sh"
  }
}
```

---

## Quick Reference

### Setup New Project (pnpm)

```bash
# Initialize project
pnpm init

# Install TypeScript + tools
pnpm add -D typescript @types/node
pnpm add -D vitest @vitest/ui @vitest/coverage-v8
pnpm add -D @biomejs/biome

# Install React (if needed)
pnpm add react react-dom
pnpm add -D @types/react @types/react-dom @testing-library/react @testing-library/user-event

# Install Zod for validation
pnpm add zod

# Create tsconfig.json
npx tsc --init --strict
```

### Quality Gate Commands

```bash
# Run all tests with coverage
pnpm test:coverage

# Lint and format
pnpm lint:fix

# Type check
pnpm type-check

# Full quality gate (run before commit)
pnpm quality-gate
```

### Tool Versions

| Package | Version | Purpose |
|---------|---------|---------|
| typescript | 5.7.2 | Type system |
| vitest | 2.1.0 | Testing framework |
| @biomejs/biome | 1.9.4 | Linting & formatting |
| zod | latest | Runtime validation |
| react | 19.0.0 | UI library |
| @testing-library/react | latest | React testing |

---

All examples follow My-Spec TRUST 5 principles and Constitution constraints (≤700 SLOC production / tests no limit, ≤10 complexity, ≥85% coverage).

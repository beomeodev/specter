# 타입스크립트 5.7 코드 예제

Vitest 2.1, Biome 1.9 및 My-Spec TRUST 5 원칙을 사용한 최신 타입스크립트 개발을 위한 프로덕션 준비 예제입니다.

---

## 예제 1: Vitest 2.1(픽스처 및 비동기 테스트 포함)

### 테스트 파일: `tests/unit/user-service.test.ts`

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

  it('유효한 데이터로 사용자를 생성해야 합니다', () => {
    const user: User = {
      id: 1,
      name: 'Alice',
      email: 'alice@example.com',
    };

    const result = userService.validateUser(user);

    expect(result).toBe(true);
    expect(user.id).toBeGreaterThan(0);
  });

  it('사용자를 비동기적으로 가져와야 합니다', async () => {
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
  ])('%i번 사용자를 %s 이름으로 가져와야 합니다', async (userId, expectedName) => {
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

**주요 특징**:
- ✅ Vitest 테스트 구조
- ✅ 설정을 위한 `beforeEach`
- ✅ 비동기/대기 테스트
- ✅ `it.each`를 사용한 매개변수화된 테스트
- ✅ `vi.spyOn`을 사용한 모의
- ✅ 추적성을 위한 TAG 블록

**실행 명령**:
```bash
vitest tests/unit/user-service.test.ts
vitest run --coverage
```

---

## 예제 2: Biome 1.9 구성 및 워크플로

### 프로젝트 구성: `biome.json`

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

### 예제 소스 파일: `src/utils/formatter.ts`

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
  // 타입스크립트 5.7 중첩 f-문자열과 동일(템플릿 리터럴)
  return `사용자: ${name}, 세부 정보: 나이: ${age}, 도시: ${city.toUpperCase()}`;
}
```

**워크플로 명령**:
```bash
# 모든 문제 확인 및 수정
biome check --write .

# 서식만 지정
biome format --write .

# 린트만 실행
biome lint .

# 특정 파일 확인
biome check src/utils/formatter.ts
```

---

## 예제 3: 타입스크립트 5.7을 사용한 타입 안전성

### 고급 타입 패턴: `src/types/api.ts`

```typescript
/**
 * @CODE:API-001
 * @SPEC: specs/003-api-types/spec.md
 * @TEST: tests/unit/api-types.test.ts
 * @CHAIN: @SPEC:API-001 → @TEST:API-001 → @CODE:API-001
 * @STATUS: implemented
 */

// 타입 안전한 API 응답 유니온
export type ApiResponse<T> =
  | { success: true; data: T }
  | { success: false; error: string };

// 제약 조건이 있는 제네릭
export function filterItems<T extends { id: number }>(
  items: T[],
  predicate: (item: T) => boolean
): T[] {
  return items.filter(predicate);
}

// 상수 타입 매개변수 (타입스크립트 5.7)
export function createSet<const T extends readonly unknown[]>(
  ...items: T
): Set<T[number]> {
  return new Set(items);
}

// satisfies 연산자 (타입스크립트 5.7)
export const routes = {
  home: '/',
  about: '/about',
  contact: '/contact',
  users: '/users',
} satisfies Record<string, string>;

// 타입 추론은 리터럴 타입을 보존합니다.
const userRoutes = createSet('/users', '/profile', '/settings');
// 타입: Set<'/users' | '/profile' | '/settings'>

// 상수 단언
export const config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000,
  retries: 3,
} as const;

// 타입: { readonly apiUrl: 'https://api.example.com', readonly timeout: 5000, readonly retries: 3 }
```

### 타입 안전한 서비스: `src/services/api-client.ts`

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
        error: error instanceof Error ? error.message : '알 수 없는 오류',
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
        error: error instanceof Error ? error.message : '알 수 없는 오류',
      };
    }
  }
}
```

---

## 예제 4: 타입스크립트를 사용한 React 컴포넌트

### 타입 안전한 React 컴포넌트: `src/components/UserCard.tsx`

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
      onEdit(1); // 프로덕션에서는 실제 사용자 ID를 사용합니다.
    }
  };

  return (
    <div className="user-card">
      <h2>{name}</h2>
      <p>{email}</p>
      {age !== undefined && <p>나이: {age}</p>}
      <span className={`role role-${role}`}>{role}</span>
      {onEdit && (
        <button onClick={handleEdit} type="button">
          편집
        </button>
      )}
    </div>
  );
};
```

### 컴포넌트 테스트: `tests/unit/UserCard.test.tsx`

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

  it('사용자 정보를 렌더링해야 합니다', () => {
    render(<UserCard {...defaultProps} />);

    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('alice@example.com')).toBeInTheDocument();
    expect(screen.getByText('user')).toBeInTheDocument();
  });

  it('나이가 제공되면 렌더링해야 합니다', () => {
    render(<UserCard {...defaultProps} age={30} />);

    expect(screen.getByText('나이: 30')).toBeInTheDocument();
  });

  it('편집 버튼을 클릭하면 onEdit을 호출해야 합니다', () => {
    const onEdit = vi.fn();
    render(<UserCard {...defaultProps} onEdit={onEdit} />);

    const editButton = screen.getByRole('button', { name: /편집/i });
    fireEvent.click(editButton);

    expect(onEdit).toHaveBeenCalledWith(1);
  });

  it('onEdit이 제공되지 않으면 편집 버튼을 렌더링하지 않아야 합니다', () => {
    render(<UserCard {...defaultProps} />);

    const editButton = screen.queryByRole('button', { name: /편집/i });
    expect(editButton).not.toBeInTheDocument();
  });
});
```

---

## 예제 5: Zod를 사용한 입력 유효성 검사

### 스키마 정의: `src/schemas/user.ts`

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
    .min(3, '사용자 이름은 3자 이상이어야 합니다')
    .max(20, '사용자 이름은 20자 이하여야 합니다')
    .regex(/^[a-zA-Z0-9_]+$/, '사용자 이름은 영숫자여야 합니다'),
  email: z.string().email('잘못된 이메일 형식'),
  age: z
    .number()
    .int('나이는 정수여야 합니다')
    .min(13, '13세 이상이어야 합니다')
    .max(120, '나이는 현실적이어야 합니다'),
  role: z.enum(['admin', 'user', 'guest'], {
    errorMap: () => ({ message: '역할은 admin, user 또는 guest여야 합니다' }),
  }),
});

export type UserInput = z.infer<typeof userInputSchema>;

export function validateUserInput(data: unknown): UserInput {
  return userInputSchema.parse(data); // 유효하지 않으면 예외 발생
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

### 환경 변수(타입 안전): `src/env.ts`

```typescript
/**
 * @CODE:ENV-001
 * @SPEC: specs/006-env-config/spec.md
 */

import { z } from 'zod';

const envSchema = z.object({
  DATABASE_URL: z.string().url('DATABASE_URL은 유효한 URL이어야 합니다'),
  API_KEY: z.string().min(32, 'API_KEY는 32자 이상이어야 합니다'),
  NODE_ENV: z.enum(['development', 'production', 'test']),
  PORT: z.string().transform(Number).pipe(z.number().int().min(1).max(65535)),
});

export const env = envSchema.parse(process.env);
```

---

## 예제 6: 품질 게이트 워크플로

### 설정 스크립트: `scripts/quality-gate.sh`

```bash
#!/bin/bash
# 타입스크립트 프로젝트용 품질 게이트 스크립트
# TRUST 5 원칙 적용

set -e

echo "🔍 타입스크립트 품질 게이트 실행 중..."

# 1. 타입 확인 (통합 - 타입 안전성)
echo "📋 타입 확인 중..."
tsc --noEmit

# 2. 린팅 (가독성 - 코드 품질)
echo "🧹 린팅 중..."
biome check .

# 3. 테스트 (테스트 우선 - 커버리지 ≥85%)
echo "🧪 테스트 실행 중..."
vitest run --coverage

# 4. 커버리지 확인
echo "📊 커버리지 확인 중..."
COVERAGE=$(grep -oP '(?<=All files\s{2}\|\s{2})\d+\.\d+' coverage/coverage-summary.txt)
if (( $(echo "$COVERAGE < 85" | bc -l) )); then
  echo "❌ 커버리지 $COVERAGE%가 85% 미만입니다"
  exit 1
fi

echo "✅ 품질 게이트 통과!"
```

### package.json 스크립트

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

## 빠른 참조

### 새 프로젝트 설정 (pnpm)

```bash
# 프로젝트 초기화
pnpm init

# 타입스크립트 + 도구 설치
pnpm add -D typescript @types/node
pnpm add -D vitest @vitest/ui @vitest/coverage-v8
pnpm add -D @biomejs/biome

# React 설치 (필요한 경우)
pnpm add react react-dom
pnpm add -D @types/react @types/react-dom @testing-library/react @testing-library/user-event

# Zod 설치 (유효성 검사용)
pnpm add zod

# tsconfig.json 생성
npx tsc --init --strict
```

### 품질 게이트 명령

```bash
# 커버리지와 함께 모든 테스트 실행
pnpm test:coverage

# 린트 및 서식 지정
pnpm lint:fix

# 타입 확인
pnpm type-check

# 전체 품질 게이트 (커밋 전 실행)
pnpm quality-gate
```

### 도구 버전

| 패키지 | 버전 | 목적 |
|---|---|---|
| typescript | 5.7.2 | 타입 시스템 |
| vitest | 2.1.0 | 테스트 프레임워크 |
| @biomejs/biome | 1.9.4 | 린팅 및 서식 지정 |
| zod | 최신 | 런타임 유효성 검사 |
| react | 19.0.0 | UI 라이브러리 |
| @testing-library/react | 최신 | React 테스트 |

---

모든 예제는 My-Spec TRUST 5 원칙 및 헌법 제약 조건(≤500 SLOC, ≤10 복잡성, ≥85% 커버리지)을 따릅니다.

---
name: ms-lang-typescript
description: My-Spec 워크플로우를 위한 Vitest 2.1, Biome 1.9, 엄격한 타이핑을 사용한 타입스크립트 5.7+ 모범 사례. 타입스크립트 코드를 작성하거나 검토할 때 사용합니다.
allowed-tools:
  - Read
  - Bash
  - Grep
version: 1.0.0
created: 2025-10-26
keywords: ['typescript', 'testing', 'vitest', 'biome', 'types', 'react', 'nextjs']
---

# 언어: 타입스크립트 5.7+ 전문가

## 스킬 메타데이터
| 필드 | 값 |
| --- | --- |
| 버전 | 1.0.0 |
| 생성일 | 2025-10-26 |
| 타입스크립트 지원 | 5.7+ (최신) |
| 허용된 도구 | Read, Bash, Grep |
| 자동 로드 | `.ts`, `.tsx` 파일 감지 시 주문형 |
| 트리거 큐 | 타입스크립트 파일, 타입 안전성, React/Next.js 개발 |

## 기능

My-Spec TDD 개발을 위한 **타입스크립트 5.7+ 전문 지식**을 제공하며 다음을 포함합니다.

- ✅ **테스트 프레임워크**: Vitest 2.1+ (Jest의 빠르고 현대적인 대안)
- ✅ **코드 품질**: Biome 1.9+ (ESLint + Prettier를 대체하는 통합 린터 + 포맷터)
- ✅ **타입 안전성**: 고급 패턴을 사용한 타입스크립트 5.7+ 엄격 모드
- ✅ **패키지 관리**: npm/pnpm/bun (프로젝트 선호도)
- ✅ **타입스크립트 5.7 기능**: 데코레이터, 상수 타입 매개변수, satisfies 연산자
- ✅ **React/Next.js**: 타입스크립트 통합을 사용한 최신 패턴
- ✅ **헌법 준수**: TRUST 5 원칙, ≤500 SLOC 파일, ≤10 복잡성

## 사용 시기

**자동 트리거**:
- 타입스크립트 코드 토론, `.ts`/`.tsx` 파일
- "타입스크립트 테스트 작성", "Vitest 사용 방법", "타입스크립트 타입 힌트"
- 타입스크립트 SPEC 구현 (`/ms.implement`)
- React/Next.js 컴포넌트 개발

**수동 호출**:
- TRUST 5 준수를 위한 타입스크립트 코드 검토
- 타입스크립트 API 또는 React 컴포넌트 설계
- 타입 오류 또는 빌드 문제 해결
- 자바스크립트를 타입스크립트로 마이그레이션

## 작동 방식 (모범 사례)

### 1. 테스트 프레임워크 (Vitest 2.1+)

**Jest보다 Vitest를 사용하는 이유**
- ⚡ Jest보다 **10배 빠름** (네이티브 ESM 지원)
- 🔧 타입스크립트에 대한 **제로 구성**
- ✅ **Jest 호환 API** (쉬운 마이그레이션)
- 🎯 c8/v8을 사용한 **내장 커버리지**

**테스트 구조**:
```typescript
// tests/unit/calculator.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { Calculator } from '@/services/calculator';

describe('Calculator', () => {
  let calculator: Calculator;

  beforeEach(() => {
    calculator = new Calculator();
  });

  it('두 개의 양수를 더해야 합니다', () => {
    const result = calculator.add(2, 3);
    expect(result).toBe(5);
  });

  it('음수를 처리해야 합니다', () => {
    const result = calculator.add(-2, 3);
    expect(result).toBe(1);
  });
});
```

**핵심 사항**:
- ✅ 타입스크립트 프로젝트에는 Vitest 사용 (Jest 아님)
- ✅ 테스트당 하나의 단언 (명확성)
- ✅ 설명적인 테스트 이름 ("should" 규칙)
- ✅ 설정을 위한 `beforeEach`
- ✅ 품질 게이트에 의해 시행되는 커버리지 ≥85%

**CLI 명령**:
```bash
vitest                              # 모든 테스트 실행 (감시 모드)
vitest run                          # 한 번 실행 (CI 모드)
vitest --coverage                   # 커버리지 보고서 생성 (≥85% 필요)
vitest --ui                         # 대화형 UI
vitest tests/unit/calculator.test.ts # 특정 테스트 실행
```

### 2. 코드 품질 (Biome 1.9+)

**ESLint + Prettier보다 Biome을 사용하는 이유**
- ⚡ ESLint보다 **75배 빠름**
- 🔧 **단일 도구** (린팅 + 서식 지정)
- ✅ **타입스크립트 우선** 설계
- 🎯 **제로 종속성** (Rust 기반)

**구성** (`biome.json`):
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

**CLI 명령**:
```bash
biome check .                       # 린트 + 서식 확인
biome check --write .               # 린트 + 자동 수정으로 서식 지정
biome format --write .              # 서식만 지정
biome lint .                        # 린트만 실행
```

### 3. 타입 안전성 (타입스크립트 5.7+ 엄격 모드)

**tsconfig.json** (엄격한 구성):
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

**고급 타입 패턴**:
```typescript
// 타입 안전한 API 응답
type ApiResponse<T> =
  | { success: true; data: T }
  | { success: false; error: string };

// 제약 조건이 있는 제네릭
function filterItems<T extends { id: number }>(
  items: T[],
  predicate: (item: T) => boolean
): T[] {
  return items.filter(predicate);
}

// 상수 타입 매개변수 (타입스크립트 5.7)
function createSet<const T extends readonly unknown[]>(
  ...items: T
): Set<T[number]> {
  return new Set(items);
}

// satisfies 연산자 (타입스크립트 5.7)
const config = {
  endpoint: '/api/users',
  timeout: 5000,
} satisfies Record<string, string | number>;
```

**CLI 명령**:
```bash
tsc --noEmit                        # 출력 없이 타입 확인
tsc --noEmit --watch                # 감시 모드에서 타입 확인
tsc --build                         # 프로젝트 빌드
```

### 4. 패키지 관리

**권장**: 더 빠른 설치 및 디스크 효율성을 위해 pnpm을 사용합니다.

**설정**:
```bash
# pnpm 설치
npm install -g pnpm

# 프로젝트 초기화
pnpm init

# 종속성 설치
pnpm add typescript vitest @vitest/ui @biomejs/biome
pnpm add -D @types/node

# 프레임워크 종속성 설치 (React/Next.js)
pnpm add react react-dom next
pnpm add -D @types/react @types/react-dom
```

**대안**: Bun (가장 빠른 런타임 + 패키지 관리자):
```bash
# Bun 설치
curl -fsSL https://bun.sh/install | bash

# 프로젝트 초기화
bun init

# 종속성 설치
bun add typescript vitest @biomejs/biome
```

### 5. React/Next.js 패턴

**타입 안전한 React 컴포넌트**:
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
      {age !== undefined && <p>나이: {age}</p>}
    </div>
  );
};
```

**Next.js 서버 액션 (타입스크립트 5.7)**:
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

  // 데이터베이스에 저장...
  return { success: true, data: { id: 1 } };
}
```

### 6. 보안 모범 사례

**입력 유효성 검사** (Zod):
```typescript
import { z } from 'zod';

const userInputSchema = z.object({
  username: z.string().min(3).max(20).regex(/^[a-zA-Z0-9_]+$/),
  email: z.string().email(),
  age: z.number().int().min(13).max(120),
});

type UserInput = z.infer<typeof userInputSchema>;

function validateUserInput(data: unknown): UserInput {
  return userInputSchema.parse(data); // 유효하지 않으면 예외 발생
}
```

**환경 변수** (타입 안전):
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

## 타입스크립트 5.7 새로운 기능

### 상수 타입 매개변수
```typescript
// 정확한 리터럴 타입 추론
function createTuple<const T extends readonly unknown[]>(...items: T): T {
  return items;
}

const tuple = createTuple(1, 'hello', true);
// 타입: readonly [1, 'hello', true] (number | string | boolean 아님)
```

### Satisfies 연산자
```typescript
// 확장 없이 타입 확인
const routes = {
  home: '/',
  about: '/about',
  contact: '/contact',
} satisfies Record<string, string>;

// routes.home은 '/'로 타입 지정됨 (string 아님)
```

## 헌법 준수

**My-Spec 요구 사항**:
- ✅ 파일 ≤500 SLOC (더 크면 분할)
- ✅ 함수 ≤100 라인
- ✅ 함수당 복잡성 ≤10
- ✅ 테스트 커버리지 ≥85%
- ✅ 엄격한 타이핑 활성화
- ✅ 모든 파일에 TAG 블록 존재

**파일 크기 확인**:
```bash
# SLOC 계산 (주석/빈 줄 제외)
cloc src/components/UserCard.tsx --by-file
```

**복잡성 확인**:
```bash
# Biome은 복잡성을 자동으로 확인합니다.
biome check . --max-diagnostics=0
```

## 도구 버전 매트릭스 (2025-10-26)

| 도구 | 버전 | 목적 | 상태 |
|---|---|---|---|
| **타입스크립트** | 5.7.2 | 기본 | ✅ 최신 |
| **Vitest** | 2.1.0 | 테스트 | ✅ 현재 |
| **Biome** | 1.9.4 | 린트/서식 | ✅ 현재 |
| **pnpm** | 9.14.2 | 패키지 관리 | ✅ 권장 |
| **Bun** | 1.1.0 | 런타임 | ✅ 대안 |
| **React** | 19.0.0 | UI 라이브러리 | ✅ 최신 |
| **Next.js** | 15.1.0 | 프레임워크 | ✅ 최신 |

## 예제 워크플로

**설정** (pnpm + 타입스크립트 5.7):
```bash
pnpm init
pnpm add typescript vitest @biomejs/biome
pnpm add -D @types/node

# tsconfig.json 생성
npx tsc --init --strict
```

**TDD 루프**:
```bash
vitest                              # RED: 테스트 실패 확인
# [코드 구현]
vitest                              # GREEN: 테스트 통과 확인
biome check --write .               # REFACTOR: 코드 품질 수정
```

**품질 게이트** (커밋 전):
```bash
vitest run --coverage               # 커버리지 ≥85%?
biome check .                       # 린트 통과?
tsc --noEmit                        # 타입 확인 통과?
```

## 모범 사례

✅ **해야 할 일**:
- 모든 테스트에 Vitest 사용 (Jest 아님)
- 타입스크립트 엄격 모드 활성화
- 린팅 + 서식에 Biome 사용 (ESLint + Prettier 아님)
- package.json에 정확한 타입스크립트 버전 지정
- 각 커밋 전에 품질 게이트 실행
- 상수 단언 및 satisfies 연산자 사용
- 공용 API에 타입 주석 추가
- 파일 ≤500 SLOC 유지 (헌법 요구 사항)

❌ **하지 말아야 할 일**:
- Jest 사용 (Vitest가 더 빠르고 TS에 더 좋음)
- ESLint + Prettier 사용 (Biome이 둘 다 대체)
- `any` 타입 사용 (`unknown`을 대신 사용)
- 타입 오류 무시 (수정하거나 명시적인 `@ts-expect-error` 사용)
- 테스트 프레임워크 혼합
- 커버리지 요구 사항 건너뛰기 (<85% 실패)
- 오래된 타입스크립트 구문 사용 (5.7+로 업그레이드)

## My-Spec과의 통합

**TAG 블록 형식** (타입스크립트):
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
  // 구현...
}
```

**테스트 TAG 블록**:
```typescript
/**
 * @TEST:AUTH-001
 * @SPEC: specs/001-auth-spec/spec.md
 * @CODE: src/services/auth.ts
 * @CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
 * @STATUS: passing
 */
describe('AuthService', () => {
  // 테스트...
});
```

## 참조 (최신 문서)

- **타입스크립트 5.7**: https://www.typescriptlang.org/docs/ (2025-10-26 접속)
- **Vitest 2.1**: https://vitest.dev/ (2025-10-26 접속)
- **Biome 1.9**: https://biomejs.dev/ (2025-10-26 접속)
- **pnpm**: https://pnpm.io/ (2025-10-26 접속)
- **React 19**: https://react.dev/ (2025-10-26 접속)
- **Next.js 15**: https://nextjs.org/docs (2025-10-26 접속)

## 변경 로그

- **v1.0.0** (2025-10-26): Vitest 2.1, Biome 1.9, 타입스크립트 5.7, 헌법 준수를 포함한 My-Spec 워크플로우용 초기 타입스크립트 스킬

## 함께 사용하면 좋은 것

- `ms-foundation-trust` (TRUST 5 유효성 검사)
- `ms-foundation-constitution` (파일 크기/복잡성 확인)
- `ms-workflow-tag-manager` (TAG 블록 생성)
- `ms-workflow-living-docs` (API 문서 동기화)

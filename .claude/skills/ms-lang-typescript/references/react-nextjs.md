# React / Next.js Patterns

## Contents

- Type-safe components and Server Actions
- Error Boundaries (class component, granular boundaries)
- Next.js App Router error handling (error.tsx, global-error.tsx)
- Testing Error Boundaries
- Error monitoring integration (Sentry)

## Type-safe component

```typescript
// src/components/UserCard.tsx
import { type FC } from 'react';

interface UserCardProps {
  name: string;
  email: string;
  age?: number;
}

export const UserCard: FC<UserCardProps> = ({ name, email, age }) => (
  <div className="user-card">
    <h2>{name}</h2>
    <p>{email}</p>
    {age !== undefined && <p>Age: {age}</p>}
  </div>
);
```

## Next.js Server Action with Zod validation

```typescript
// app/actions/user.ts
'use server';

import { z } from 'zod';

const userSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

export async function createUser(formData: FormData): Promise<ApiResponse<{ id: number }>> {
  const validation = userSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
  });

  if (!validation.success) {
    return { success: false, error: validation.error.message };
  }

  // Save to database...
  return { success: true, data: { id: 1 } };
}
```

## Error Boundaries

Catch runtime errors in the component tree, show fallback UI instead of a blank page,
and forward errors to monitoring.

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
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
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

Mount at the root, and add granular boundaries per section so one widget failing
doesn't blank the whole page:

```typescript
// app/dashboard/page.tsx
export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <ErrorBoundary fallback={<div>Failed to load stats</div>}>
        <StatsWidget />
      </ErrorBoundary>
      <ErrorBoundary fallback={<div>Failed to load chart</div>}>
        <ChartWidget />
      </ErrorBoundary>
    </div>
  );
}
```

## Next.js App Router error files

`error.tsx` handles route-segment errors; recovery goes through the provided
`reset()` callback (never a full page reload — that masks state bugs):

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
    console.error('App error:', error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold">Something went wrong!</h2>
      <p className="mt-2 text-gray-600">{error.message}</p>
      <button onClick={reset} className="mt-4 px-4 py-2 bg-blue-500 text-white rounded">
        Try again
      </button>
    </div>
  );
}
```

```typescript
// app/global-error.tsx — catches errors in the root layout itself
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

## Testing Error Boundaries

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
});
```

## Error monitoring integration

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

// In ErrorBoundary.componentDidCatch:
Sentry.captureException(error, {
  contexts: {
    react: { componentStack: errorInfo.componentStack },
  },
});
```

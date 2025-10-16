# Frontend Coding Assistant Rules

**Framework-Agnostic Rules** • See `../AGENTS.md` for common principles

---

## 📌 Parent Rules Compliance

**First check `../AGENTS.md` for:**
- Planning First
- Pattern Consistency  
- Single Source of Truth (OSOT)
- No Magic Strings/Numbers
- Single Responsibility & Reusability
- Security by Default
- Thorough Exception Handling

---

## 🛠 Core Frontend Principles

### 1. TypeScript Strict Mode (NON-NEGOTIABLE)

```typescript
// ✅ Required
const user: User | null = null
const count: number = 0
const fetchData = async (): Promise<User[]> => { /*...*/ }

// ❌ Forbidden
const data: any = {}  // Never use any!

// ✅ Use unknown + type guards instead
const data: unknown = await response.json()
if (isUser(data)) {
  console.log(data.name)
}
```

**Rules**:
- All variables explicitly typed
- No `any` type (use `unknown` + type guards)
- Enable `strict: true` in tsconfig
- Return types for all functions

---

### 2. Component Interface Contracts

**Define clear boundaries** (applies to React, Vue, Angular, Svelte):

```typescript
// Props/Input types
interface Props {
  userId: number
  userName: string
  isActive?: boolean  // Optional with default
}

// Events/Output types  
interface Events {
  onUpdate: (user: User) => void
  onDelete: (userId: number) => void
}
```

**Framework Examples**:
- **Vue 3**: `defineProps<Props>()`, `defineEmits<Events>()`
- **React**: `FC<Props>`, callback props
- **Angular**: `@Input()`, `@Output()`
- **Svelte**: `export let userId: number`

---

### 3. Error Handling Pattern

```typescript
// ✅ Always handle errors explicitly
const fetchUser = async (id: number): Promise<User | null> => {
  try {
    const response = await fetch(`/api/users/${id}`)
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('User not found')
      }
      throw new Error('Server error')
    }
    
    return await response.json()
  } catch (error) {
    console.error('Fetch failed:', error)
    // Show user-friendly message
    return null
  }
}
```

**Requirements**:
- Check `response.ok` before parsing
- Handle specific error codes
- User-friendly error messages
- Always catch async operations

---

### 4. Conditional Rendering (Early Return Pattern)

```html
<!-- Loading -->
<LoadingSpinner v-if="isLoading" />

<!-- Error -->
<ErrorMessage v-else-if="error" :message="error" />

<!-- Empty state -->
<EmptyState v-else-if="!data" />

<!-- Main content (no nesting) -->
<MainContent v-else :data="data" />
```

**Avoid**: Deep nesting with multiple conditions

---

### 5. Type Guards

```typescript
// types/user.ts
export interface User {
  id: number
  email: string
  name: string
}

export function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'email' in value
  )
}
```

---

## 📁 Directory Structure (Standard)

```
frontend/
├── src/
│   ├── components/
│   │   └── shared/      # Reusable components (OSOT)
│   ├── views/           # Pages/Routes
│   ├── composables/     # Reusable logic (hooks/composables)
│   ├── types/           # Type definitions (OSOT)
│   ├── utils/           # Reusable functions (OSOT)
│   ├── config.ts        # Constants (OSOT)
│   └── main.ts
└── package.json
```

---

## 🎨 Styling Guidelines

### Utility-First CSS (Tailwind/UnoCSS)

```html
<!-- ✅ Use utility classes -->
<div class="container mx-auto px-4 py-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <button class="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded">
      Click
    </button>
  </div>
</div>

<!-- ❌ No inline styles -->
<div style="padding: 20px">Bad!</div>
```

**Mobile-First**: Start with mobile, add breakpoints upward (sm, md, lg, xl)

---

## 💻 Naming Conventions

```typescript
// Files: kebab-case
user-profile.tsx
auth-button.vue

// Functions/Variables: camelCase
const getUserList = () => {}
const isAuthenticated = ref(false)

// Constants: UPPER_SNAKE_CASE
const MAX_FILE_SIZE = 5 * 1024 * 1024
const API_BASE_URL = 'http://localhost:8000'

// Interfaces/Types: PascalCase
interface UserData {
  id: number
  name: string
}

// Const objects for enums
const UserStatus = {
  ACTIVE: 'active',
  INACTIVE: 'inactive'
} as const
```

---

## 🚀 Performance Patterns

### 1. Lazy Loading

```typescript
// Route-level
const UserView = () => import('./views/UserView')

// Component-level  
const HeavyChart = lazy(() => import('./HeavyChart'))
```

### 2. Memoization/Computed

```typescript
// ✅ Memoized (cached)
const expensiveValue = useMemo(() => {
  return items.filter(...).map(...).sort(...)
}, [items])

// ❌ Re-runs every render
const expensiveValue = () => items.filter(...).map(...)
```

### 3. Debounce User Input

```typescript
// Search with 500ms debounce
const debouncedSearch = useDebounce(searchQuery, 500)

useEffect(() => {
  fetchResults(debouncedSearch)
}, [debouncedSearch])
```

---

## 🔧 Development Commands

**Single File** (preferred):
```bash
# Format, lint, type-check in one command
npx prettier --write src/components/user-profile.tsx && \
npx eslint src/components/user-profile.tsx --fix && \
npx tsc --noEmit
```

**Full Project** (only when requested):
```bash
npm run lint && npm run type-check && npm test
```

---

## ✅ Pre-Work Checklist

**Before creating/modifying components**:
- [ ] Checked similar existing components for patterns?
- [ ] Props/Events interfaces defined?
- [ ] All variables explicitly typed?
- [ ] Error handling added?
- [ ] Using utility-first CSS (no inline styles)?
- [ ] Mobile-responsive checked?
- [ ] Reusable logic extracted to composables/hooks?

**Before commit**:
- [ ] Prettier passed?
- [ ] ESLint passed (0 warnings)?
- [ ] Type checker passed?
- [ ] No `console.log` statements?
- [ ] No commented code?

---

## 📊 Code Quality Standards

**Required**:
- ✅ TypeScript strict mode enabled
- ✅ All Props/Events typed
- ✅ No `any` type usage
- ✅ Explicit return types for functions
- ✅ Error boundaries/handling present
- ✅ Utility-first CSS (no inline styles)
- ✅ Mobile-first responsive design

**Forbidden**:
- ❌ `any` type
- ❌ Inline styles
- ❌ Deep component nesting (>3 levels)
- ❌ Direct DOM manipulation (use framework)
- ❌ Global state without proper management

---

## 🎯 Framework-Specific Notes

**This document is framework-agnostic.** Apply these principles to:
- **React**: Hooks, Props, FC types
- **Vue 3**: Composition API, defineProps/Emits
- **Angular**: Decorators, RxJS, TypeScript
- **Svelte**: Reactive statements, prop bindings

For framework-specific patterns, create `PATTERNS-{framework}.md` separately.

---

**Created**: 2025-10-10  
**Version**: 2.0.0
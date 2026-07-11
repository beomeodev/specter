# Debugging Worked Examples

## Contents

- Example 1: Python NoneType error
- Example 2: JavaScript undefined reference
- Example 3: Async/Promise rejection
- Example 4: Memory leak debugging (Python, tracemalloc + leak patterns)
- Example 5: N+1 query problem (SQLAlchemy + Prisma)
- General performance debugging checklist

## Example 1: Python NoneType Error

**Error**:
```python
AttributeError: 'NoneType' object has no attribute 'email'
```

**Debugging steps**:
1. Identify where the None value originated
2. Check function return types
3. Add null checks or Optional types
4. Write test for None case

**Fix**:
```python
# Before (no null check)
def get_user_email(user):
    return user.email  # Crashes if user is None

# After (defensive check)
def get_user_email(user: Optional[User]) -> str:
    if user is None:
        raise ValueError("User cannot be None")
    return user.email
```

## Example 2: JavaScript undefined Reference

**Error**:
```javascript
TypeError: Cannot read property 'name' of undefined
```

**Debugging steps**:
1. Check where the object comes from
2. Verify API response structure
3. Add optional chaining or null checks
4. Write test for undefined case

**Fix**:
```typescript
// Before (no null check)
function getUserName(user) {
  return user.name; // Crashes if user is undefined
}

// After (optional chaining)
function getUserName(user?: User): string {
  return user?.name ?? "Anonymous";
}
```

## Example 3: Async/Promise Rejection

**Error**:
```javascript
UnhandledPromiseRejectionWarning: Error: Connection timeout
```

**Debugging steps**:
1. Add .catch() to promise chain
2. Use try-catch with async/await
3. Check network/timeout configuration
4. Write test for error case

**Fix**:
```typescript
// Before (unhandled rejection)
async function fetchData(url: string) {
  const response = await fetch(url); // May throw
  return response.json();
}

// After (proper error handling)
async function fetchData(url: string): Promise<Data> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error(`Failed to fetch ${url}:`, error);
    throw new Error(`Data fetch failed: ${error.message}`);
  }
}
```

## Example 4: Memory Leak Debugging (Python)

**Symptom**: Memory usage grows unbounded over time (e.g., 100MB → 2GB in production)

**Debugging steps**:
1. Use `tracemalloc` to identify leak source
2. Check for circular references
3. Profile with `memory_profiler` decorator
4. Verify cleanup in `__del__` or context managers

**Investigation with tracemalloc**:
```python
import tracemalloc

tracemalloc.start()

run_application()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("[ Top 10 memory consumers ]")
for stat in top_stats[:10]:
    print(stat)
```

**Common memory leak patterns**:
```python
# LEAK: Class variable accumulates instances
class Cache:
    _instances = []  # Never cleared!

    def __init__(self, data):
        self.data = data
        self._instances.append(self)  # Memory leak

# FIX: Use weak references
import weakref

class Cache:
    _instances = weakref.WeakSet()  # Auto-cleanup when no strong refs

    def __init__(self, data):
        self.data = data
        self._instances.add(self)


# LEAK: Circular reference
class Node:
    def add_child(self, child):
        child.parent = self  # Circular reference: parent ↔ child
        self.children.append(child)

# FIX: Use weak references for back-pointers
class Node:
    def add_child(self, child):
        child.parent = weakref.ref(self)  # Weak reference
        self.children.append(child)


# LEAK: Global cache never expires
_cache = {}

def get_data(key):
    if key not in _cache:
        _cache[key] = expensive_operation(key)  # Grows indefinitely
    return _cache[key]

# FIX: Use LRU cache with size limit
from functools import lru_cache

@lru_cache(maxsize=128)  # Automatically evicts oldest entries
def get_data(key):
    return expensive_operation(key)
```

**Memory profiling decorator**:
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    data = [i for i in range(1000000)]  # 8MB list
    return sum(data)

# Run with: python -m memory_profiler script.py
```

## Example 5: N+1 Query Problem (Performance Debugging)

**Symptom**: API endpoint takes >5 seconds to respond (should be <500ms)

**Debugging steps**:
1. Use `console.time()` / `time.time()` to measure sections
2. Check database query logs for repeated queries
3. Use ORM query debugging (SQLAlchemy `echo=True`, Django Debug Toolbar)
4. Profile with `cProfile` (Python) or Chrome DevTools (TypeScript)

**Identifying N+1 queries (Python/SQLAlchemy)**:
```python
# N+1 QUERY PROBLEM (1 + N queries)
def get_users_with_posts():
    users = db.query(User).all()  # 1 query
    for user in users:
        # N queries: SELECT * FROM posts WHERE user_id = ?
        posts = db.query(Post).filter(Post.user_id == user.id).all()
        user.posts = posts
    return users
# 100 users → 101 queries!


# FIX: Eager loading with JOIN — single query
def get_users_with_posts():
    return (
        db.query(User)
        .options(joinedload(User.posts))
        .all()
    )
```

**TypeScript/Prisma example**:
```typescript
// N+1 QUERY PROBLEM
async function getUsersWithPosts() {
  const users = await prisma.user.findMany();  // 1 query
  for (const user of users) {
    user.posts = await prisma.post.findMany({  // N queries
      where: { userId: user.id }
    });
  }
  return users;
}

// FIX: include for eager loading — single query with JOIN
async function getUsersWithPosts() {
  return prisma.user.findMany({
    include: { posts: true }
  });
}
```

**Measuring query performance**:
```python
import time
import logging

# Enable SQLAlchemy query logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

start = time.time()
users = get_users_with_posts()
print(f"Query took {time.time() - start:.2f}s")
# Before: 5.32s (101 queries) → After: 0.12s (1 query)
```

## General performance debugging checklist

- [ ] **Database queries**: Check for N+1, missing indexes
- [ ] **Memory**: Profile with `tracemalloc`, `memory_profiler`
- [ ] **CPU**: Profile with `cProfile`, Chrome DevTools
- [ ] **Network**: Check for redundant API calls
- [ ] **Caching**: Add memoization for expensive operations
- [ ] **Async**: Use concurrent execution where possible

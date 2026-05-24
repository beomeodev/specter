---
name: ms-database-design
description: Database schema design automation for SQL/NoSQL with ERD generation, migration scripts, and performance optimization (indexing, partitioning, sharding) - supports PostgreSQL, MySQL, MongoDB with rollback-ready production output compliant with Constitution constraints. Use when designing new database schemas from requirements, creating migration scripts for schema changes, generating ERD documentation, optimizing query performance with indexing, planning database scaling strategy (sharding, partitioning), refactoring existing schemas for performance, or ensuring Constitution compliance in database layer
---

# Database Schema Design

## What it does

Designs optimized, production-ready database schemas for SQL and NoSQL systems:
- **SQL**: PostgreSQL, MySQL, SQLite (normalized schemas, indexes, constraints)
- **NoSQL**: MongoDB (query-first design, embed vs. reference)
- **ERD Generation**: ASCII text-based entity relationship diagrams
- **Migration Scripts**: Up/down migrations with transaction safety and rollback
- **Performance Optimization**: Indexing strategy, partitioning, sharding, replication
- **Constitution Compliance**: Schema complexity ≤10, file size ≤700 SLOC (production)

## When to use

- Designing new database schema from requirements
- Refactoring existing schema for performance
- Creating migration scripts for schema changes
- Generating ERD documentation
- Optimizing query performance with indexing
- Planning database scaling strategy (sharding, partitioning)
- Ensuring Constitution compliance in database layer

## How it works

### 1. Requirements Gathering

**Clarify before designing**:
- Database type (PostgreSQL, MySQL, MongoDB)
- Domain and business entities
- Expected query patterns (read-heavy, write-heavy, mixed)
- Scale requirements (expected records, concurrent users)
- Compliance needs (GDPR, audit trails, soft deletes)

**GEARS Pattern Application**:
```
✅ System SHALL store user profiles with email, username, and timestamps
✅ WHEN user deletes account, system SHALL soft-delete with deleted_at timestamp
✅ WHERE user is admin, system MAY access all user records
✅ IF query filters by email, system SHALL use indexed lookup
```

### 2. Schema Design Best Practices

**SQL (PostgreSQL, MySQL)**:
- **Normalization**: 3NF for transactional data, denormalize for read-heavy analytics
- **Primary Keys**: `id BIGINT AUTO_INCREMENT PRIMARY KEY` (or UUID for distributed systems)
- **Foreign Keys**: `user_id BIGINT REFERENCES users(id) ON DELETE CASCADE`
- **Indexes**: Index foreign keys, commonly filtered/sorted columns
- **Timestamps**: `created_at`, `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
- **Soft Deletes**: `deleted_at TIMESTAMP NULL` for audit trails

**NoSQL (MongoDB)**:
- **Query-First Design**: Structure documents based on access patterns
- **Embed vs. Reference**: Embed 1:few, reference 1:many
- **Denormalization**: Duplicate data for read performance (trade-off: update complexity)
- **Indexes**: Compound indexes for multi-field queries

**Naming Conventions**:
- Tables: `snake_case`, plural (`users`, `order_items`)
- Columns: `snake_case`, descriptive (`created_at`, `is_active`)
- Foreign Keys: `{referenced_table}_id` (`user_id`, `product_id`)
- Indexes: `idx_{table}_{columns}` (`idx_users_email`)

### 3. Schema Generation

**PostgreSQL Example**:
```sql
-- TAG: @SPEC:DB-001
-- Users table with optimized indexes
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Indexes for common queries
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- TAG: @SPEC:DB-002
-- Orders table with foreign key
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status) WHERE status != 'completed';
```

**MongoDB Example**:
```javascript
// TAG: @SPEC:DB-003
// User document with embedded addresses (1:few)
db.users.insertOne({
    _id: ObjectId(),
    email: "user@example.com",
    username: "john_doe",
    profile: {
        firstName: "John",
        lastName: "Doe",
        avatar: "https://..."
    },
    addresses: [  // Embedded (1:few relationship)
        {
            type: "shipping",
            street: "123 Main St",
            city: "NYC",
            zip: "10001"
        }
    ],
    createdAt: ISODate(),
    updatedAt: ISODate()
});

// Orders reference users (1:many relationship)
db.orders.insertOne({
    _id: ObjectId(),
    userId: ObjectId("..."),  // Reference
    items: [
        { productId: ObjectId("..."), quantity: 2, price: 29.99 }
    ],
    totalAmount: 59.98,
    status: "pending",
    createdAt: ISODate()
});

// Indexes
db.users.createIndex({ email: 1 }, { unique: true });
db.orders.createIndex({ userId: 1, createdAt: -1 });
db.orders.createIndex({ status: 1 });
```

### 4. ERD Generation (ASCII Format)

```
+----------------+       +------------------+       +------------------+
|     users      |       |      orders      |       |   order_items    |
+----------------+       +------------------+       +------------------+
| PK id          |<---+  | PK id            |<---+  | PK id            |
|    email       |    |  | FK user_id       |    |  | FK order_id      |
|    username    |    |  |    total_amount  |    |  | FK product_id    |
|    password_hash|   |  |    status        |    |  |    quantity      |
|    is_active   |    |  |    created_at    |    |  |    unit_price    |
|    created_at  |    +--+    updated_at    |    +--+    subtotal      |
|    updated_at  |       +------------------+       +------------------+
|    deleted_at  |
+----------------+

Relationships:
- users (1) -> orders (many): One user can have multiple orders
- orders (1) -> order_items (many): One order contains multiple items
- products (1) -> order_items (many): One product can be in multiple orders
```

### 5. Migration Scripts

**Up Migration** (PostgreSQL):
```sql
-- TAG: @SPEC:DB-004
-- Migration: Add email verification to users table
-- File: migrations/001_add_email_verification.up.sql

BEGIN;

ALTER TABLE users
ADD COLUMN email_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN verification_token VARCHAR(255),
ADD COLUMN verification_sent_at TIMESTAMP NULL;

CREATE INDEX idx_users_verification_token
ON users(verification_token)
WHERE verification_token IS NOT NULL;

COMMIT;
```

**Down Migration** (Rollback):
```sql
-- TAG: @SPEC:DB-004
-- Rollback: Remove email verification from users table
-- File: migrations/001_add_email_verification.down.sql

BEGIN;

DROP INDEX IF EXISTS idx_users_verification_token;

ALTER TABLE users
DROP COLUMN verification_sent_at,
DROP COLUMN verification_token,
DROP COLUMN email_verified;

COMMIT;
```

### 6. Performance Optimization

**Indexing Strategy**:
```sql
-- Primary use case: Find active users by email
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;

-- Composite index for multi-column queries
CREATE INDEX idx_orders_user_status
ON orders(user_id, status, created_at DESC);

-- Partial index for specific conditions
CREATE INDEX idx_orders_pending
ON orders(created_at DESC)
WHERE status = 'pending';

-- Covering index (includes all queried columns)
CREATE INDEX idx_users_profile
ON users(email)
INCLUDE (username, is_active);
```

**Partitioning** (for large tables):
```sql
-- TAG: @SPEC:DB-005
-- Partition orders by created_at (monthly)
CREATE TABLE orders (
    id BIGSERIAL,
    user_id BIGINT NOT NULL,
    total_amount DECIMAL(10, 2),
    status VARCHAR(50),
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE orders_2025_01 PARTITION OF orders
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE orders_2025_02 PARTITION OF orders
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

**Sharding Strategy**:
```sql
-- Horizontal sharding by user_id
-- Shard 1: user_id % 4 = 0
-- Shard 2: user_id % 4 = 1
-- Shard 3: user_id % 4 = 2
-- Shard 4: user_id % 4 = 3

-- Application-level routing
def get_shard(user_id: int) -> str:
    shard_id = user_id % 4
    return f"postgresql://db-shard-{shard_id}:5432/app"
```

**Read Replicas**:
```
Master (Write): postgresql://db-master:5432/app
Replica 1 (Read): postgresql://db-replica-1:5432/app
Replica 2 (Read): postgresql://db-replica-2:5432/app

# Route reads to replicas, writes to master
```

### 7. Constitution Compliance

**Schema Complexity Validation**:
```sql
-- ❌ Violates Constitution (too many columns, high complexity)
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    -- 50+ columns here... (violates ≤700 SLOC guideline)
    col1, col2, col3, ... col50
);

-- ✅ Constitution-compliant (split into related tables)
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE user_profiles (
    user_id BIGINT PRIMARY KEY REFERENCES users(id),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar VARCHAR(255)
);

CREATE TABLE user_settings (
    user_id BIGINT PRIMARY KEY REFERENCES users(id),
    theme VARCHAR(50),
    language VARCHAR(10),
    notifications_enabled BOOLEAN
);
```

**Migration File Size**:
- Target: ≤300 lines per migration
- Split large migrations into multiple steps
- Use transaction blocks (BEGIN/COMMIT)

## Inputs
- Business requirements (entities, relationships, constraints)
- Expected query patterns (read/write ratio, filtering columns)
- Scale requirements (records, users, growth rate)
- Database type (PostgreSQL, MySQL, MongoDB)

## Outputs
- Complete schema with CREATE TABLE statements
- ASCII ERD diagram
- Indexed columns with rationale
- Up/down migration scripts
- Performance optimization recommendations
- Constitution compliance verification

## For detailed examples
See `examples.md` for:
- PostgreSQL e-commerce schema (users, products, orders)
- MongoDB social network schema (users, posts, comments)
- Complex indexing strategies
- Partitioning and sharding implementations
- Migration script templates

## Related Skills
- `ms-foundation-constitution`: File size and complexity validation
- `ms-architecture-patterns`: DDD tactical patterns (aggregates, repositories)
- `ms-foundation-trust`: Schema testing and validation

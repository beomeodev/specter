# Database Schema Design Examples

## Example 1: E-Commerce Platform (PostgreSQL)

### Requirements
- Users can create accounts, place orders, add products to cart
- Products have categories, inventory tracking
- Orders contain multiple items
- Support for promotions and discounts
- Audit trail for all transactions

### Schema Design

```sql
-- TAG: @SPEC:ECOM-001
-- Users and authentication
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

CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_username ON users(username) WHERE deleted_at IS NULL;

-- TAG: @SPEC:ECOM-002
-- Product categories (hierarchical)
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    parent_id BIGINT REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);

-- TAG: @SPEC:ECOM-003
-- Products with inventory
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    category_id BIGINT REFERENCES categories(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_is_active ON products(is_active, created_at DESC);
CREATE INDEX idx_products_price ON products(price);

-- TAG: @SPEC:ECOM-004
-- Orders
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    subtotal DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_order_amounts CHECK (total_amount = subtotal - discount_amount + tax_amount)
);

CREATE INDEX idx_orders_user_id ON orders(user_id, created_at DESC);
CREATE INDEX idx_orders_status ON orders(status) WHERE status IN ('pending', 'processing');
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);

-- TAG: @SPEC:ECOM-005
-- Order items (many-to-many between orders and products)
CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    CONSTRAINT chk_order_item_subtotal CHECK (subtotal = quantity * unit_price)
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- TAG: @SPEC:ECOM-006
-- Shopping cart (temporary storage)
CREATE TABLE cart_items (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INT NOT NULL CHECK (quantity > 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_id)
);

CREATE INDEX idx_cart_items_user_id ON cart_items(user_id);

-- TAG: @SPEC:ECOM-007
-- Promotions and discounts
CREATE TABLE promotions (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_percent DECIMAL(5, 2) CHECK (discount_percent BETWEEN 0 AND 100),
    discount_amount DECIMAL(10, 2) CHECK (discount_amount >= 0),
    min_order_amount DECIMAL(10, 2) DEFAULT 0,
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT chk_promotion_discount CHECK (
        (discount_percent IS NOT NULL AND discount_amount IS NULL) OR
        (discount_percent IS NULL AND discount_amount IS NOT NULL)
    )
);

CREATE INDEX idx_promotions_code ON promotions(code) WHERE is_active = TRUE;
CREATE INDEX idx_promotions_validity ON promotions(valid_from, valid_until) WHERE is_active = TRUE;
```

### ERD Diagram

```
+----------------+       +------------------+       +------------------+
|   categories   |       |    products      |       |   order_items    |
+----------------+       +------------------+       +------------------+
| PK id          |<---+  | PK id            |<---+  | PK id            |
|    name        |    |  | FK category_id   |    |  | FK order_id      |
|    slug        |    +--+    name          |    +--+ FK product_id    |
| FK parent_id   |       |    description   |       |    quantity      |
|    created_at  |       |    price         |       |    unit_price    |
+----------------+       |    stock_quantity|       |    subtotal      |
                         |    is_active     |       +------------------+
                         |    created_at    |              ^
                         |    updated_at    |              |
                         +------------------+              |
                                 ^                         |
                                 |                         |
+----------------+       +------------------+              |
|     users      |       |      orders      +--------------+
+----------------+       +------------------+
| PK id          |<---+  | PK id            |
|    email       |    |  | FK user_id       |
|    username    |    +--+    status        |
|    password_hash|      |    subtotal      |
|    is_active   |       |    discount_amount|
|    created_at  |       |    tax_amount    |
|    updated_at  |       |    total_amount  |
|    deleted_at  |       |    created_at    |
+----------------+       |    updated_at    |
       ^                 +------------------+
       |
       |                 +------------------+
       |                 |   cart_items     |
       |                 +------------------+
       |                 | PK id            |
       +---------------->| FK user_id       |
                         | FK product_id    |
                         |    quantity      |
                         |    created_at    |
                         |    updated_at    |
                         +------------------+
```

### Migration Script

```sql
-- File: migrations/001_create_ecommerce_schema.up.sql
-- TAG: @SPEC:ECOM-001

BEGIN;

-- Create all tables in dependency order
CREATE TABLE users (...);
CREATE TABLE categories (...);
CREATE TABLE products (...);
CREATE TABLE orders (...);
CREATE TABLE order_items (...);
CREATE TABLE cart_items (...);
CREATE TABLE promotions (...);

-- Create all indexes
CREATE INDEX idx_users_email ON users(email);
-- ... (all other indexes)

COMMIT;
```

```sql
-- File: migrations/001_create_ecommerce_schema.down.sql

BEGIN;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS cart_items CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS promotions CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;

COMMIT;
```

---

## Example 2: Social Network (MongoDB)

### Requirements
- Users can create profiles, post updates, comment, like posts
- Follow/follower relationships
- Real-time notifications
- Activity feeds (read-heavy, denormalized)

### Schema Design

```javascript
// TAG: @SPEC:SOCIAL-001
// Users collection
db.users.insertOne({
    _id: ObjectId(),
    username: "john_doe",
    email: "john@example.com",
    passwordHash: "...",
    profile: {
        displayName: "John Doe",
        bio: "Software engineer and coffee enthusiast",
        avatar: "https://cdn.example.com/avatars/john.jpg",
        location: "San Francisco, CA",
        website: "https://johndoe.com"
    },
    stats: {  // Denormalized for quick access
        followersCount: 1247,
        followingCount: 532,
        postsCount: 89
    },
    isActive: true,
    createdAt: ISODate("2024-01-15T10:00:00Z"),
    updatedAt: ISODate("2024-11-05T14:30:00Z")
});

// Indexes
db.users.createIndex({ username: 1 }, { unique: true });
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ "stats.followersCount": -1 });  // Top users

// TAG: @SPEC:SOCIAL-002
// Posts collection (denormalized author info for feed performance)
db.posts.insertOne({
    _id: ObjectId(),
    authorId: ObjectId("..."),
    author: {  // Denormalized for feed display
        username: "john_doe",
        displayName: "John Doe",
        avatar: "https://cdn.example.com/avatars/john.jpg"
    },
    content: "Just launched my new project! Check it out 🚀",
    media: [
        {
            type: "image",
            url: "https://cdn.example.com/posts/image123.jpg",
            width: 1200,
            height: 800
        }
    ],
    hashtags: ["coding", "launch", "excited"],
    mentions: [ObjectId("..."), ObjectId("...")],  // Mentioned user IDs
    stats: {  // Denormalized counters
        likesCount: 42,
        commentsCount: 7,
        sharesCount: 3
    },
    visibility: "public",  // public, followers, private
    createdAt: ISODate("2024-11-05T12:00:00Z"),
    updatedAt: ISODate("2024-11-05T14:00:00Z")
});

// Indexes
db.posts.createIndex({ authorId: 1, createdAt: -1 });  // User's posts timeline
db.posts.createIndex({ createdAt: -1 });  // Global feed
db.posts.createIndex({ hashtags: 1, createdAt: -1 });  // Hashtag search
db.posts.createIndex({ "stats.likesCount": -1 });  // Trending posts

// TAG: @SPEC:SOCIAL-003
// Comments collection (embedded vs. referenced trade-off)
db.comments.insertOne({
    _id: ObjectId(),
    postId: ObjectId("..."),
    authorId: ObjectId("..."),
    author: {  // Denormalized
        username: "jane_smith",
        displayName: "Jane Smith",
        avatar: "https://cdn.example.com/avatars/jane.jpg"
    },
    content: "Congratulations! This looks amazing!",
    parentCommentId: null,  // For nested replies
    stats: {
        likesCount: 5
    },
    createdAt: ISODate("2024-11-05T12:30:00Z")
});

// Indexes
db.comments.createIndex({ postId: 1, createdAt: 1 });  // Post's comments
db.comments.createIndex({ authorId: 1, createdAt: -1 });  // User's comments

// TAG: @SPEC:SOCIAL-004
// Follows collection (many-to-many relationship)
db.follows.insertOne({
    _id: ObjectId(),
    followerId: ObjectId("..."),  // Who is following
    followingId: ObjectId("..."),  // Who is being followed
    createdAt: ISODate("2024-10-01T10:00:00Z")
});

// Indexes (critical for performance)
db.follows.createIndex({ followerId: 1, followingId: 1 }, { unique: true });
db.follows.createIndex({ followingId: 1, createdAt: -1 });  // Followers list
db.follows.createIndex({ followerId: 1, createdAt: -1 });  // Following list

// TAG: @SPEC:SOCIAL-005
// Notifications collection (time-series pattern)
db.notifications.insertOne({
    _id: ObjectId(),
    userId: ObjectId("..."),  // Recipient
    type: "like",  // like, comment, follow, mention
    actorId: ObjectId("..."),  // Who triggered the notification
    actor: {  // Denormalized
        username: "jane_smith",
        displayName: "Jane Smith",
        avatar: "https://cdn.example.com/avatars/jane.jpg"
    },
    resourceId: ObjectId("..."),  // Post/comment ID
    resourceType: "post",
    message: "jane_smith liked your post",
    isRead: false,
    createdAt: ISODate("2024-11-05T13:00:00Z")
});

// Indexes
db.notifications.createIndex({ userId: 1, createdAt: -1 });  // User's notifications
db.notifications.createIndex({ userId: 1, isRead: 1, createdAt: -1 });  // Unread notifications
db.notifications.createIndex({ createdAt: 1 }, { expireAfterSeconds: 2592000 });  // TTL: 30 days

// TAG: @SPEC:SOCIAL-006
// Activity feed (denormalized for read performance)
db.feed.insertOne({
    _id: ObjectId(),
    userId: ObjectId("..."),  // Feed owner
    postId: ObjectId("..."),
    post: {  // Fully denormalized post
        _id: ObjectId("..."),
        authorId: ObjectId("..."),
        author: {
            username: "john_doe",
            displayName: "John Doe",
            avatar: "https://cdn.example.com/avatars/john.jpg"
        },
        content: "Just launched my new project! Check it out 🚀",
        media: [...],
        stats: { likesCount: 42, commentsCount: 7 }
    },
    createdAt: ISODate("2024-11-05T12:00:00Z")
});

// Indexes
db.feed.createIndex({ userId: 1, createdAt: -1 });  // User's feed (most critical)
db.feed.createIndex({ createdAt: 1 }, { expireAfterSeconds: 604800 });  // TTL: 7 days
```

### Data Consistency Strategy

**Trade-offs**:
- ✅ **Read Performance**: Denormalized author info in posts/comments (no JOIN needed)
- ❌ **Write Complexity**: When user updates profile, must update all posts/comments
- ✅ **Feed Performance**: Pre-computed feed per user (fanout-on-write)
- ❌ **Storage Cost**: Duplicate data across collections

**Update Pattern** (when user changes avatar):
```javascript
// Update user profile
db.users.updateOne(
    { _id: userId },
    { $set: { "profile.avatar": newAvatar, updatedAt: new Date() } }
);

// Update denormalized data in posts
db.posts.updateMany(
    { authorId: userId },
    { $set: { "author.avatar": newAvatar } }
);

// Update denormalized data in comments
db.comments.updateMany(
    { authorId: userId },
    { $set: { "author.avatar": newAvatar } }
);

// Update denormalized data in feed (background job)
db.feed.updateMany(
    { "post.authorId": userId },
    { $set: { "post.author.avatar": newAvatar } }
);
```

---

## Example 3: Advanced Indexing Strategies

### Composite Index (Multi-Column Queries)

```sql
-- Query: Find active products in category, sorted by price
SELECT * FROM products
WHERE category_id = 5 AND is_active = TRUE
ORDER BY price ASC;

-- Optimized composite index (order matters!)
CREATE INDEX idx_products_category_active_price
ON products(category_id, is_active, price ASC);

-- Index usage: category_id (equality) → is_active (equality) → price (range/sort)
```

### Partial Index (Filtered Data)

```sql
-- Query: Find pending orders (status rarely changes to 'pending' after creation)
SELECT * FROM orders
WHERE status = 'pending'
ORDER BY created_at DESC;

-- Partial index (smaller, faster)
CREATE INDEX idx_orders_pending
ON orders(created_at DESC)
WHERE status = 'pending';

-- Benefits: 90% smaller index size, faster writes
```

### Covering Index (Index-Only Scan)

```sql
-- Query: Get user email and username by ID
SELECT email, username FROM users WHERE id = 123;

-- Covering index (includes all queried columns)
CREATE INDEX idx_users_profile
ON users(id)
INCLUDE (email, username);

-- PostgreSQL won't touch the table (index-only scan)
```

### GIN Index (Full-Text Search)

```sql
-- Query: Search products by name/description
SELECT * FROM products
WHERE to_tsvector('english', name || ' ' || description) @@ to_tsquery('laptop');

-- GIN index for full-text search
CREATE INDEX idx_products_fts
ON products
USING GIN (to_tsvector('english', name || ' ' || description));
```

---

## Example 4: Partitioning Strategy

### Range Partitioning (Time-Series Data)

```sql
-- TAG: @SPEC:PART-001
-- Partition logs by created_at (monthly)
CREATE TABLE logs (
    id BIGSERIAL,
    user_id BIGINT,
    action VARCHAR(100),
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE logs_2025_01 PARTITION OF logs
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE logs_2025_02 PARTITION OF logs
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Benefits: Fast queries on recent data, easy archival (DROP old partitions)
```

### List Partitioning (Categorical Data)

```sql
-- TAG: @SPEC:PART-002
-- Partition orders by region
CREATE TABLE orders (
    id BIGSERIAL,
    region VARCHAR(50),
    total_amount DECIMAL(10, 2),
    created_at TIMESTAMP,
    PRIMARY KEY (id, region)
) PARTITION BY LIST (region);

CREATE TABLE orders_us PARTITION OF orders FOR VALUES IN ('US');
CREATE TABLE orders_eu PARTITION OF orders FOR VALUES IN ('EU', 'UK');
CREATE TABLE orders_asia PARTITION OF orders FOR VALUES IN ('JP', 'CN', 'IN');
```

---

## Example 5: Sharding Strategy

### Horizontal Sharding (User-Based)

```python
# TAG: @CODE:SHARD-001
# Application-level sharding logic

SHARD_COUNT = 4

def get_shard_connection(user_id: int) -> str:
    """Route to correct shard based on user_id."""
    shard_id = user_id % SHARD_COUNT
    return f"postgresql://db-shard-{shard_id}:5432/app"

def get_user(user_id: int):
    """Fetch user from correct shard."""
    conn = psycopg2.connect(get_shard_connection(user_id))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()
```

### Cross-Shard Queries (Anti-Pattern)

```python
# ❌ Avoid cross-shard JOINs (performance nightmare)
# Query: Find all orders for user_id=123 and user_id=456 (different shards)

# ✅ Solution: Denormalize or use service-level aggregation
def get_orders_for_users(user_ids: List[int]):
    """Fetch orders from multiple shards in parallel."""
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(get_orders, uid): uid
            for uid in user_ids
        }
        for future in as_completed(futures):
            results.extend(future.result())
    return results
```

---

## Constitution Compliance Notes

**File Size Limits**:
- Migration files: ≤300 lines (split large schemas)
- Schema files: ≤700 SLOC production (separate concerns: auth, billing, content)

**Complexity Limits**:
- Table columns: ≤20 per table (split into related tables)
- Indexes: ≤5 per table (avoid over-indexing)
- Constraints: Clear CHECK constraints (no complex business logic in DB)

**TAG Integration**:
```sql
-- Every table/index tagged to SPEC
-- TAG: @SPEC:AUTH-001
CREATE TABLE users (...);

-- TAG: @SPEC:AUTH-002
CREATE INDEX idx_users_email ON users(email);
```

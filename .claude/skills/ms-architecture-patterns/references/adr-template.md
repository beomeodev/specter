# Architectural Decision Records (ADR) Template

## What is an ADR?

An ADR documents an architectural decision: why it was made, what alternatives were considered, and what the consequences are.

## When to write an ADR?

- Choosing architecture pattern (Clean, Hexagonal, Microservices)
- Selecting technology (database, framework, cloud provider)
- Deciding on integration pattern (REST, GraphQL, gRPC)
- Changing existing architecture (migration, refactoring)

---

## ADR Template

```markdown
# ADR-{number}: {Title}

**Status**: {Proposed | Accepted | Deprecated | Superseded by ADR-XXX}

**Date**: YYYY-MM-DD

**Deciders**: {Names of people involved}

**Technical Story**: {Issue/ticket reference}

---

## Context

What is the issue we're facing? What factors are driving this decision?

- Current situation
- Problems with current approach
- Requirements and constraints
- Assumptions

## Decision

What architectural decision did we make?

- Clear statement of the decision
- How it will be implemented

## Alternatives Considered

What other options did we evaluate?

### Option 1: {Name}
- **Pros**: ...
- **Cons**: ...
- **Why rejected**: ...

### Option 2: {Name}
- **Pros**: ...
- **Cons**: ...
- **Why rejected**: ...

## Consequences

What are the implications of this decision?

### Positive
- ✅ Benefit 1
- ✅ Benefit 2

### Negative
- ❌ Trade-off 1
- ❌ Trade-off 2

### Neutral
- Changes required
- Migration path

## Compliance

How does this decision comply with Constitution constraints?

- File size impact
- Complexity impact
- Testing requirements
- TAG tracking requirements

## Related Decisions

- Supersedes: ADR-XXX
- Related to: ADR-YYY
- Requires: ADR-ZZZ

---

## Notes

Additional context, references, diagrams.
```

---

## Example ADR 1: Hexagonal Architecture for Payment Service

```markdown
# ADR-001: Use Hexagonal Architecture for Payment Service

**Status**: Accepted

**Date**: 2025-11-05

**Deciders**: Engineering Team, Tech Lead

**Technical Story**: #SPEC-PAY-001

---

## Context

Our payment service currently has tight coupling to Stripe API. We need to:
- Support multiple payment providers (Stripe, PayPal, Crypto)
- Easily swap providers without changing business logic
- Test payment logic without real API calls
- Comply with Constitution file size limits (≤700 SLOC production; tests no limit)

Current problems:
- Stripe SDK calls scattered throughout business logic
- Difficult to test (requires Stripe test mode)
- Hard to add new providers (would require rewriting business logic)

## Decision

Implement **Hexagonal Architecture (Ports and Adapters)** for payment service.

**Structure**:
```
payment_service/
├── domain/                  # Business logic
│   ├── payment.py          # Payment entity
│   └── ports/
│       └── payment_gateway.py   # Interface (port)
├── adapters/
│   ├── stripe_adapter.py   # Stripe implementation
│   ├── paypal_adapter.py   # PayPal implementation
│   └── crypto_adapter.py   # Crypto implementation
└── use_cases/
    └── process_payment.py  # Domain logic using port
```

**Implementation**:
- Define `PaymentGateway` port (interface) in domain layer
- Business logic depends on port, not concrete adapter
- Infrastructure implements adapters (Stripe, PayPal, Crypto)
- Dependency injection selects adapter at runtime (via config)

## Alternatives Considered

### Option 1: Keep Stripe-specific code
- **Pros**: Simpler, no abstraction overhead
- **Cons**: Cannot swap providers, hard to test, vendor lock-in
- **Why rejected**: Not scalable, violates dependency inversion

### Option 2: Strategy Pattern without Ports
- **Pros**: Multiple implementations
- **Cons**: Still couples domain to payment provider details
- **Why rejected**: Business logic would still know about Stripe/PayPal specifics

### Option 3: Microservice per Provider
- **Pros**: Complete isolation
- **Cons**: Over-engineering, operational complexity
- **Why rejected**: Overkill for current scale (not yet needed)

## Consequences

### Positive
- ✅ **Easy provider swaps**: Change config, no code changes
- ✅ **Testable**: Use fake adapter (no real API calls)
- ✅ **Vendor independence**: Business logic doesn't know about Stripe
- ✅ **Clean separation**: Domain logic isolated from infrastructure
- ✅ **Constitution compliant**: Each adapter <300 SLOC

### Negative
- ❌ **Initial abstraction cost**: Need to design port interface
- ❌ **More files**: 1 port + N adapters (vs. 1 service file)
- ❌ **Learning curve**: Team needs to understand ports/adapters

### Neutral
- Migration path: Extract Stripe calls into adapter (1-2 days)
- Configuration: Environment variable `PAYMENT_PROVIDER=stripe|paypal|crypto`

## Compliance

**Constitution Section II (Simplicity)**:
- ✅ File size: Each adapter ≤300 SLOC (under 700 limit)
- ✅ Complexity: Port interface simple (5 methods, complexity ≤3)
- ✅ Single responsibility: Each adapter handles one provider

**Constitution Section V (TRUST)**:
- ✅ **Test-First**: Fake adapter enables 100% domain logic testing
- ✅ **Readable**: Clear separation (port vs. adapter)
- ✅ **Unified**: Type-safe port interface (mypy strict mode)
- ✅ **Secured**: Input validation in domain, not adapters
- ✅ **Trackable**: TAG @SPEC:PAY-001 → @CODE:PAY-001 chain

## Related Decisions

- Supersedes: None (new service)
- Related to: ADR-005 (Dependency Injection setup)
- Requires: ADR-003 (Environment-based configuration)

---

## Notes

**Port Interface** (5 methods):
```python
class PaymentGateway(ABC):
    @abstractmethod
    async def charge(...) -> PaymentResult: pass

    @abstractmethod
    async def refund(...) -> PaymentResult: pass

    @abstractmethod
    async def get_transaction(...) -> Transaction: pass

    @abstractmethod
    async def list_transactions(...) -> List[Transaction]: pass

    @abstractmethod
    async def cancel_transaction(...) -> PaymentResult: pass
```

**Migration Plan**:
1. Week 1: Define port interface, create Stripe adapter
2. Week 2: Migrate business logic to use port
3. Week 3: Add PayPal adapter, test in staging
4. Week 4: Production rollout with config toggle
```

---

## Example ADR 2: CQRS for Analytics Dashboard

```markdown
# ADR-002: Implement CQRS for Analytics Dashboard

**Status**: Accepted

**Date**: 2025-11-05

**Deciders**: Engineering Team, Product Manager

**Technical Story**: #SPEC-ANALYTICS-001

---

## Context

Our analytics dashboard needs to display:
- Real-time order statistics (last 24h orders, revenue)
- User engagement metrics (active users, retention)
- Product performance (top sellers, inventory)

**Current problems**:
- Complex JOINs across 8 tables (slow queries, 5-10 seconds)
- Write operations (new orders) slow down read queries
- Dashboard timeouts during peak hours
- Difficulty optimizing for both reads and writes

**Requirements**:
- Dashboard load time <500ms
- No impact on order creation performance
- Real-time data (eventual consistency acceptable)

## Decision

Implement **CQRS (Command Query Responsibility Segregation)** pattern.

**Architecture**:
```
┌─────────────────────────────────────────────────┐
│                 Client Requests                  │
└────────────┬─────────────────────┬───────────────┘
             │                     │
             ▼                     ▼
    ┌────────────────┐    ┌────────────────────┐
    │  Write Model   │    │    Read Model      │
    │  (Commands)    │    │    (Queries)       │
    ├────────────────┤    ├────────────────────┤
    │ Normalized DB  │    │  Denormalized DB   │
    │ (PostgreSQL)   │    │  (PostgreSQL)      │
    │                │    │                    │
    │ - users        │    │ - analytics_daily  │
    │ - orders       │    │ - top_products     │
    │ - order_items  │    │ - user_stats       │
    └────────┬───────┘    └─────────▲──────────┘
             │                      │
             │   Domain Events      │
             └──────────────────────┘
```

**Implementation**:
- **Write side**: Normalized schema (3NF) for data integrity
- **Read side**: Denormalized tables optimized for analytics queries
- **Synchronization**: Domain events update read model (eventual consistency)
- **Background job**: Rebuild read model every 5 minutes (fallback)

## Alternatives Considered

### Option 1: Database Views
- **Pros**: Simple, single database
- **Cons**: Views still query same tables (no performance gain)
- **Why rejected**: Doesn't solve slow JOIN problem

### Option 2: Materialized Views
- **Pros**: Pre-computed, faster than views
- **Cons**: PostgreSQL refresh locks tables (impacts writes)
- **Why rejected**: Lock contention during refresh

### Option 3: Separate Read Database (Full Replication)
- **Pros**: Complete isolation
- **Cons**: Double storage cost, replication lag
- **Why rejected**: Overkill (we only need analytics, not full replica)

## Consequences

### Positive
- ✅ **Fast reads**: Denormalized tables, no JOINs (500ms → 50ms)
- ✅ **Isolated writes**: Order creation unaffected by analytics queries
- ✅ **Optimized schemas**: Write model (3NF), read model (denormalized)
- ✅ **Scalable**: Read model can use different database (Redis, Elasticsearch)

### Negative
- ❌ **Eventual consistency**: Read model lags behind (1-5 seconds)
- ❌ **Complexity**: Maintain two models + synchronization
- ❌ **Storage overhead**: Duplicated data in read model
- ❌ **Synchronization bugs**: Events might fail, need monitoring

### Neutral
- Migration: Create read tables, set up event handlers (2 weeks)
- Monitoring: Track read model lag, alert if >10 seconds

## Compliance

**Constitution Section II (Simplicity)**:
- ✅ File size: Event handlers ≤200 SLOC each (under 700 limit)
- ✅ Complexity: Each handler simple (1 event type → 1 table update)
- ✅ Split by concern: Write model, read model, event handlers separate

**Constitution Section V (TRUST)**:
- ✅ **Test-First**: Event handlers unit tested (fake event publisher)
- ✅ **Trackable**: TAG @SPEC:ANALYTICS-001 → @CODE:ANALYTICS-001

## Related Decisions

- Supersedes: None
- Related to: ADR-010 (Event-driven architecture)
- Requires: ADR-006 (Domain events infrastructure)

---

## Notes

**Read Model Schema** (denormalized):
```sql
-- Pre-computed daily analytics
CREATE TABLE analytics_daily (
    date DATE PRIMARY KEY,
    total_orders INT,
    total_revenue DECIMAL(10, 2),
    new_users INT,
    active_users INT
);

-- Top products (updated on every order)
CREATE TABLE top_products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255),
    units_sold INT,
    revenue DECIMAL(10, 2),
    rank INT
);
```

**Event Handler Example**:
```python
# TAG: @CODE:ANALYTICS-001
class UpdateAnalyticsDailyHandler:
    async def handle(self, event: OrderCompletedEvent):
        # Update denormalized analytics table
        await db.execute("""
            INSERT INTO analytics_daily (date, total_orders, total_revenue)
            VALUES (CURRENT_DATE, 1, %s)
            ON CONFLICT (date) DO UPDATE SET
                total_orders = analytics_daily.total_orders + 1,
                total_revenue = analytics_daily.total_revenue + %s
        """, (event.total_amount, event.total_amount))
```

**Acceptable Lag**: 1-5 seconds (dashboard shows "as of 3 seconds ago")
```

---

## ADR Best Practices

1. **One decision per ADR**: Don't mix multiple decisions
2. **Immutable**: Don't edit old ADRs, supersede with new ones
3. **Short**: 1-2 pages maximum (link to detailed docs if needed)
4. **Searchable**: Use consistent titles (ADR-{number}: {Pattern} for {Component})
5. **Version control**: Store ADRs in `docs/adr/` directory
6. **Review**: Discuss ADRs in architecture review meetings

## ADR Naming Convention

```
docs/adr/
├── 001-hexagonal-architecture-for-payment.md
├── 002-cqrs-for-analytics-dashboard.md
├── 003-event-sourcing-for-audit-log.md
├── 004-api-gateway-for-microservices.md
└── README.md  (index of all ADRs)
```

## ADR Lifecycle

```
Proposed → Accepted → Implemented
    ↓
Deprecated (if replaced)
    ↓
Superseded by ADR-XXX
```

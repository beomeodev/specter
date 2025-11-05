---
name: ms-architecture-patterns
description: Production architecture patterns (Clean/Hexagonal/DDD) with ADR templates, anti-pattern warnings, microservices/event-driven design (CQRS, Event Sourcing, Saga), and Constitution-compliant implementation guidance for scalable backend systems with testability-first approach. Use when designing backend systems, documenting architectural decisions (ADR), implementing DDD tactical patterns, refactoring monoliths, choosing architecture patterns for team standardization, migrating to event-driven architecture, or ensuring testability and maintainability
---

# Architecture Patterns

## What it does

Provides production-ready architectural patterns for backend systems:
- **Clean Architecture**: Layered dependency flow (domain → use cases → interfaces → infrastructure)
- **Hexagonal Architecture**: Ports and adapters for technology independence
- **Domain-Driven Design (DDD)**: Bounded contexts, aggregates, entities, value objects
- **ADR Templates**: Architectural Decision Records for documenting choices
- **Microservices Patterns**: Service decomposition, API Gateway, Saga, CQRS
- **Event-Driven Design**: Event Sourcing, message queues, eventual consistency
- **Anti-Pattern Detection**: Anemic domain, framework coupling, fat controllers
- **Constitution Compliance**: File size ≤500 SLOC, complexity ≤10

## When to use

- Designing new backend system or microservice
- Refactoring monolith for scalability
- Choosing architecture pattern for team standardization
- Documenting architectural decisions (ADR)
- Implementing DDD tactical patterns (aggregates, repositories)
- Migrating to event-driven architecture
- Ensuring testability and maintainability
- Decoupling business logic from frameworks (ports/adapters)

## How it works

### 1. Clean Architecture (Layered Dependency Flow)

**Core Principle**: "Dependencies point inward"
- Outer layers depend on inner layers
- Inner layers know nothing about outer layers
- Domain logic independent of UI, database, frameworks

**Layers** (inside → out):
```
1. Domain (Entities): Pure business logic, no dependencies
2. Use Cases: Application-specific business rules
3. Interface Adapters: Controllers, presenters, gateways
4. Infrastructure: Frameworks, databases, external APIs
```

**Directory Structure**:
```
src/
├── domain/              # Layer 1: Pure business logic
│   ├── entities/        # Business objects (User, Order)
│   └── value_objects/   # Immutable values (Email, Money)
├── use_cases/           # Layer 2: Application logic
│   ├── create_order.py
│   └── process_payment.py
├── adapters/            # Layer 3: Interface adapters
│   ├── controllers/     # HTTP/GraphQL handlers
│   ├── presenters/      # Response formatting
│   └── gateways/        # Repository interfaces
└── infrastructure/      # Layer 4: External concerns
    ├── database/        # PostgreSQL, MongoDB
    ├── messaging/       # RabbitMQ, Kafka
    └── external_apis/   # Stripe, SendGrid
```

**Example** (Python):
```python
# TAG: @SPEC:ARCH-001
# Layer 1: Domain Entity (no dependencies)
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Order:
    """Pure domain entity with business rules."""
    id: int
    user_id: int
    total: Decimal
    status: str

    def can_be_cancelled(self) -> bool:
        """Business rule: only pending/processing orders can be cancelled."""
        return self.status in ['pending', 'processing']

    def cancel(self) -> None:
        """Domain operation with invariant enforcement."""
        if not self.can_be_cancelled():
            raise ValueError(f"Cannot cancel order with status: {self.status}")
        self.status = 'cancelled'


# TAG: @SPEC:ARCH-002
# Layer 2: Use Case (orchestrates domain logic)
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    """Port (interface) - infrastructure implements this."""
    @abstractmethod
    def get_by_id(self, order_id: int) -> Order:
        pass

    @abstractmethod
    def save(self, order: Order) -> None:
        pass

class CancelOrderUseCase:
    """Application-specific business rule."""
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo  # Dependency injection

    def execute(self, order_id: int, user_id: int) -> None:
        order = self.order_repo.get_by_id(order_id)

        # Authorization check
        if order.user_id != user_id:
            raise PermissionError("User cannot cancel this order")

        # Domain logic
        order.cancel()

        # Persist
        self.order_repo.save(order)


# TAG: @SPEC:ARCH-003
# Layer 3: Controller (HTTP adapter)
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    current_user_id: int = Depends(get_current_user),
    use_case: CancelOrderUseCase = Depends(get_cancel_order_use_case)
):
    """HTTP adapter - translates request to use case."""
    try:
        use_case.execute(order_id, current_user_id)
        return {"message": "Order cancelled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# TAG: @SPEC:ARCH-004
# Layer 4: Infrastructure (PostgreSQL adapter)
import asyncpg

class PostgreSQLOrderRepository(OrderRepository):
    """Adapter - implements port interface."""
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_by_id(self, order_id: int) -> Order:
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, user_id, total, status FROM orders WHERE id = $1",
                order_id
            )
            return Order(**dict(row))

    async def save(self, order: Order) -> None:
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                "UPDATE orders SET status = $1 WHERE id = $2",
                order.status, order.id
            )
```

**Benefits**:
- ✅ Testable without infrastructure (mock repositories)
- ✅ Framework-independent domain logic
- ✅ Easy to swap databases (implement different adapter)
- ✅ Clear separation of concerns

---

### 2. Hexagonal Architecture (Ports and Adapters)

**Core Principle**: "Domain at the center, adapters on the outside"
- **Ports**: Interfaces (e.g., `PaymentGateway`, `EmailService`)
- **Adapters**: Implementations (e.g., `StripeAdapter`, `SendGridAdapter`)

**Diagram**:
```
         +------------------+
         |   Adapters       |
         | (Infrastructure) |
         +------------------+
                 ↓ implements
         +------------------+
         |   Ports          |
         |  (Interfaces)    |
         +------------------+
                 ↑ uses
         +------------------+
         |   Domain Logic   |
         | (Business Rules) |
         +------------------+
```

**Example** (Payment Gateway):
```python
# TAG: @SPEC:HEX-001
# Port (interface)
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class PaymentResult:
    success: bool
    transaction_id: str | None
    error_message: str | None

class PaymentGateway(ABC):
    """Port - domain defines what it needs."""
    @abstractmethod
    async def charge(self, amount: Decimal, currency: str, token: str) -> PaymentResult:
        pass


# TAG: @SPEC:HEX-002
# Adapter (Stripe implementation)
import stripe

class StripeAdapter(PaymentGateway):
    """Adapter - infrastructure implements port."""
    def __init__(self, api_key: str):
        stripe.api_key = api_key

    async def charge(self, amount: Decimal, currency: str, token: str) -> PaymentResult:
        try:
            charge = stripe.Charge.create(
                amount=int(amount * 100),  # Stripe uses cents
                currency=currency,
                source=token
            )
            return PaymentResult(
                success=True,
                transaction_id=charge.id,
                error_message=None
            )
        except stripe.error.StripeError as e:
            return PaymentResult(
                success=False,
                transaction_id=None,
                error_message=str(e)
            )


# TAG: @SPEC:HEX-003
# Adapter (PayPal implementation)
class PayPalAdapter(PaymentGateway):
    """Alternative adapter - easy to swap!"""
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    async def charge(self, amount: Decimal, currency: str, token: str) -> PaymentResult:
        # PayPal-specific logic here
        pass


# TAG: @SPEC:HEX-004
# Domain Use Case (depends on port, not adapter)
class ProcessPaymentUseCase:
    """Domain logic independent of payment provider."""
    def __init__(self, payment_gateway: PaymentGateway):
        self.payment_gateway = payment_gateway  # Port, not Stripe/PayPal

    async def execute(self, order_id: int, amount: Decimal, token: str) -> bool:
        result = await self.payment_gateway.charge(amount, "USD", token)

        if result.success:
            # Update order status
            return True
        else:
            # Log error, notify user
            return False
```

**Benefits**:
- ✅ Swap implementations easily (Stripe → PayPal without changing domain)
- ✅ Testable with mocks (no real API calls in tests)
- ✅ Technology independence (domain doesn't know about Stripe)

---

### 3. Domain-Driven Design (DDD)

**Strategic Patterns**: Bounded contexts, ubiquitous language
**Tactical Patterns**: Entities, value objects, aggregates, repositories, domain events

#### 3.1 Bounded Contexts

**Principle**: Divide large domain into smaller, focused contexts
- Each context has its own model (User in Auth ≠ User in Billing)
- Contexts communicate via APIs/events

**Example** (E-Commerce):
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Auth Context   │     │ Product Context │     │  Order Context  │
│                 │     │                 │     │                 │
│  - User         │     │  - Product      │     │  - Order        │
│  - Session      │     │  - Category     │     │  - OrderItem    │
│  - Permission   │     │  - Inventory    │     │  - Payment      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        └───────────────────────┴───────────────────────┘
                    API / Domain Events
```

#### 3.2 Entities vs. Value Objects

**Entity**: Has identity, mutable
```python
# TAG: @SPEC:DDD-001
class User:
    """Entity - identity matters (user_id)."""
    def __init__(self, id: int, email: str, name: str):
        self.id = id
        self.email = email
        self.name = name

    def update_email(self, new_email: str) -> None:
        """Entities can mutate."""
        self.email = new_email
```

**Value Object**: No identity, immutable
```python
# TAG: @SPEC:DDD-002
from dataclasses import dataclass

@dataclass(frozen=True)  # Immutable
class Email:
    """Value object - equality by value."""
    address: str

    def __post_init__(self):
        """Validate in constructor."""
        if '@' not in self.address:
            raise ValueError("Invalid email format")

# Two Email("test@test.com") are equal (same value)
```

#### 3.3 Aggregates

**Principle**: Group of entities/value objects with consistency boundary
- One entity is **Aggregate Root** (entry point)
- External code accesses only through root
- Enforce invariants inside aggregate

**Example** (Order Aggregate):
```python
# TAG: @SPEC:DDD-003
from typing import List
from dataclasses import dataclass, field
from decimal import Decimal

@dataclass
class OrderItem:
    """Entity inside aggregate."""
    product_id: int
    quantity: int
    unit_price: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price


@dataclass
class Order:
    """Aggregate Root - enforces invariants."""
    id: int
    user_id: int
    items: List[OrderItem] = field(default_factory=list)
    status: str = 'pending'

    def add_item(self, product_id: int, quantity: int, unit_price: Decimal) -> None:
        """Business rule: cannot modify completed orders."""
        if self.status == 'completed':
            raise ValueError("Cannot modify completed order")

        self.items.append(OrderItem(product_id, quantity, unit_price))

    def calculate_total(self) -> Decimal:
        """Aggregate logic."""
        return sum(item.subtotal for item in self.items)

    def complete(self) -> None:
        """State transition with validation."""
        if not self.items:
            raise ValueError("Cannot complete order with no items")
        if self.status != 'pending':
            raise ValueError(f"Cannot complete order with status: {self.status}")

        self.status = 'completed'
```

#### 3.4 Repositories

**Principle**: Abstraction for persistence (fetch/save aggregates)
```python
# TAG: @SPEC:DDD-004
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    """Repository - interface in domain layer."""
    @abstractmethod
    def get_by_id(self, order_id: int) -> Order:
        pass

    @abstractmethod
    def save(self, order: Order) -> None:
        pass

    @abstractmethod
    def find_by_user(self, user_id: int) -> List[Order]:
        pass
```

#### 3.5 Domain Events

**Principle**: Notify other parts of system when something happens
```python
# TAG: @SPEC:DDD-005
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OrderCompletedEvent:
    """Domain event - immutable fact."""
    order_id: int
    user_id: int
    total_amount: Decimal
    occurred_at: datetime

class Order:
    def __init__(self):
        self.events: List = []

    def complete(self) -> None:
        if not self.items:
            raise ValueError("Cannot complete order with no items")

        self.status = 'completed'

        # Emit domain event
        self.events.append(OrderCompletedEvent(
            order_id=self.id,
            user_id=self.user_id,
            total_amount=self.calculate_total(),
            occurred_at=datetime.utcnow()
        ))
```

---

### 4. Microservices Patterns

#### 4.1 API Gateway Pattern

**Problem**: Clients need to call multiple services
**Solution**: Single entry point that routes requests

```
Client → API Gateway → [Auth Service, Product Service, Order Service]
```

**Benefits**:
- ✅ Single endpoint for clients
- ✅ Authentication/authorization at gateway
- ✅ Request routing, load balancing
- ✅ Rate limiting, caching

#### 4.2 Saga Pattern (Distributed Transactions)

**Problem**: Transaction spans multiple services
**Solution**: Sequence of local transactions with compensations

**Example** (Order Saga):
```
1. Reserve inventory (Product Service)
2. Charge payment (Payment Service)
3. Create order (Order Service)

If step 2 fails → Compensate: Release inventory
If step 3 fails → Compensate: Refund payment + Release inventory
```

#### 4.3 CQRS (Command Query Responsibility Segregation)

**Principle**: Separate write model (commands) from read model (queries)

```python
# TAG: @SPEC:CQRS-001
# Write Model (Command)
class CreateOrderCommand:
    user_id: int
    items: List[OrderItem]

class CreateOrderHandler:
    def handle(self, command: CreateOrderCommand) -> None:
        # Validate, persist to write database (normalized)
        pass


# Read Model (Query)
class OrderSummaryQuery:
    user_id: int

class OrderSummaryHandler:
    def handle(self, query: OrderSummaryQuery) -> List[OrderSummary]:
        # Fetch from read database (denormalized, optimized for reads)
        pass
```

---

### 5. Anti-Patterns (What to Avoid)

| Anti-Pattern | Description | Fix |
|--------------|-------------|-----|
| **Anemic Domain** | Entities with only getters/setters, logic in services | Move business rules into entities |
| **Framework Coupling** | Business logic depends on FastAPI/Django | Use dependency inversion (ports/adapters) |
| **Fat Controllers** | Controllers contain business logic | Extract to use cases |
| **God Objects** | Single class does everything | Split by bounded contexts |
| **Circular Dependencies** | Module A → B → A | Introduce interfaces, dependency inversion |

**Example** (Anemic Domain):
```python
# ❌ Anemic Domain
class Order:
    def __init__(self):
        self.items = []
        self.status = 'pending'
    # Only data, no behavior

class OrderService:
    def add_item(self, order: Order, item: OrderItem):
        order.items.append(item)  # Business logic outside entity

    def complete_order(self, order: Order):
        if len(order.items) == 0:
            raise ValueError("No items")
        order.status = 'completed'


# ✅ Rich Domain
class Order:
    def __init__(self):
        self.items = []
        self.status = 'pending'

    def add_item(self, item: OrderItem) -> None:
        """Business rule inside entity."""
        if self.status == 'completed':
            raise ValueError("Cannot modify completed order")
        self.items.append(item)

    def complete(self) -> None:
        """Encapsulated business rule."""
        if not self.items:
            raise ValueError("Cannot complete order with no items")
        self.status = 'completed'
```

---

### 6. Constitution Compliance

**File Size Constraints**:
```python
# ❌ Violates Constitution (>500 SLOC)
class OrderService:
    # 800 lines of methods...

# ✅ Split by bounded context
# order_service.py (300 lines)
class OrderService:
    pass

# payment_service.py (250 lines)
class PaymentService:
    pass

# inventory_service.py (250 lines)
class InventoryService:
    pass
```

**Complexity Constraints**:
```python
# ❌ Cyclomatic complexity = 15
def process_order(order):
    if order.status == 'pending':
        if order.payment_method == 'credit_card':
            if order.total > 1000:
                # 10 more nested ifs...

# ✅ Complexity ≤10 (use strategy pattern)
class PaymentStrategy(ABC):
    @abstractmethod
    def process(self, order: Order) -> bool:
        pass

class CreditCardPayment(PaymentStrategy):
    def process(self, order: Order) -> bool:
        # Simple, focused logic
        pass
```

---

## Inputs
- Business requirements (use cases, domain rules)
- System constraints (scale, performance, availability)
- Team size and experience level
- Technology choices (frameworks, databases)

## Outputs
- Architectural decision (Clean/Hexagonal/DDD/Microservices)
- Directory structure and file organization
- ADR document (if requested)
- Implementation examples with TAG annotations
- Anti-pattern warnings for current codebase

## For detailed examples
See:
- `examples.md`: Full implementation examples (FastAPI + PostgreSQL)
- `references/adr-template.md`: ADR template and examples
- `references/microservices.md`: Event Sourcing, CQRS, Saga patterns

## Related Skills
- `ms-database-design`: Schema design for DDD aggregates
- `ms-foundation-constitution`: File size and complexity validation
- `ms-foundation-trust`: Testing architecture patterns

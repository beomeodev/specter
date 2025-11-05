# Microservices and Event-Driven Patterns

## Overview

This document covers advanced patterns for microservices and event-driven architectures:
- API Gateway Pattern
- Saga Pattern (Distributed Transactions)
- Event Sourcing
- Circuit Breaker
- Service Mesh

---

## 1. API Gateway Pattern

### Problem
- Clients need to call multiple microservices
- Each service has different protocols, authentication
- Cross-cutting concerns (auth, rate limiting, logging) duplicated

### Solution
Single entry point (API Gateway) that routes requests to services.

### Architecture

```
                    ┌─────────────────────┐
                    │   Mobile/Web App    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    API Gateway      │
                    │  - Authentication   │
                    │  - Rate Limiting    │
                    │  - Request Routing  │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   ┌─────────────┐      ┌─────────────┐     ┌─────────────┐
   │   Auth      │      │  Product    │     │   Order     │
   │  Service    │      │  Service    │     │  Service    │
   └─────────────┘      └─────────────┘     └─────────────┘
```

### Implementation (FastAPI + httpx)

```python
# TAG: @SPEC:GATEWAY-001
# API Gateway implementation

from fastapi import FastAPI, Request, HTTPException
import httpx
from typing import Dict

app = FastAPI()

# Service registry (could be dynamic from Consul/Eureka)
SERVICES = {
    "auth": "http://auth-service:8001",
    "products": "http://product-service:8002",
    "orders": "http://order-service:8003",
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway_route(service: str, path: str, request: Request):
    """
    Route requests to appropriate service.
    Constitution: Simple router, complexity ≤5.
    """
    # Validate service exists
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service {service} not found")

    # Get service URL
    service_url = f"{SERVICES[service]}/{path}"

    # Forward request
    async with httpx.AsyncClient() as client:
        # Copy headers (except Host)
        headers = dict(request.headers)
        headers.pop("host", None)

        # Forward request to service
        response = await client.request(
            method=request.method,
            url=service_url,
            headers=headers,
            content=await request.body(),
            params=request.query_params
        )

        return response.json()


# Authentication middleware
@app.middleware("http")
async def authenticate(request: Request, call_next):
    """Verify JWT token before routing."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing authorization")

    # Verify token (could call auth service)
    token = auth_header.replace("Bearer ", "")
    # ... token verification logic

    response = await call_next(request)
    return response
```

### Benefits
- ✅ Single entry point for clients
- ✅ Centralized authentication, rate limiting
- ✅ Request/response transformation
- ✅ Protocol translation (REST → gRPC)

### Trade-offs
- ❌ Single point of failure (mitigate with HA setup)
- ❌ Latency overhead (extra hop)
- ❌ Gateway can become bottleneck (horizontal scaling needed)

---

## 2. Saga Pattern (Distributed Transactions)

### Problem
Transaction spans multiple services (Order → Payment → Inventory).
Traditional 2PC (two-phase commit) not practical in microservices.

### Solution
Sequence of local transactions with compensating transactions for rollback.

### Two Approaches

#### 2.1 Choreography (Event-Based)

Services publish events, other services react.

```
Order Service → OrderCreated Event
                    ↓
Payment Service → PaymentProcessed Event
                    ↓
Inventory Service → InventoryReserved Event
                    ↓
Order Service → OrderCompleted
```

**Implementation**:
```python
# TAG: @SPEC:SAGA-001
# Choreography-based saga

from dataclasses import dataclass
from datetime import datetime

@dataclass
class OrderCreatedEvent:
    order_id: int
    user_id: int
    total_amount: Decimal
    items: List[OrderItem]

@dataclass
class PaymentFailedEvent:
    order_id: int
    reason: str

# Order Service
class CreateOrderUseCase:
    async def execute(self, command: CreateOrderCommand):
        # Create order
        order = Order(...)
        self.order_repo.save(order)

        # Publish event
        await self.event_publisher.publish(OrderCreatedEvent(
            order_id=order.id,
            user_id=order.user_id,
            total_amount=order.total,
            items=order.items
        ))

# Payment Service (listens to OrderCreatedEvent)
class ProcessPaymentHandler:
    async def handle(self, event: OrderCreatedEvent):
        try:
            # Charge payment
            result = await self.payment_gateway.charge(event.total_amount)

            if result.success:
                # Publish success event
                await self.event_publisher.publish(PaymentProcessedEvent(
                    order_id=event.order_id,
                    transaction_id=result.transaction_id
                ))
            else:
                # Publish failure event (triggers compensation)
                await self.event_publisher.publish(PaymentFailedEvent(
                    order_id=event.order_id,
                    reason=result.error_message
                ))
        except Exception as e:
            # Publish failure event
            await self.event_publisher.publish(PaymentFailedEvent(
                order_id=event.order_id,
                reason=str(e)
            ))

# Order Service (listens to PaymentFailedEvent - compensation)
class CancelOrderHandler:
    async def handle(self, event: PaymentFailedEvent):
        """Compensating transaction - cancel order."""
        order = self.order_repo.get_by_id(event.order_id)
        order.cancel(reason=event.reason)
        self.order_repo.save(order)

        # Notify user
        await self.notification_service.send(
            user_id=order.user_id,
            message=f"Order {order.id} failed: {event.reason}"
        )
```

**Benefits**:
- ✅ Decoupled services (no direct calls)
- ✅ Asynchronous (non-blocking)
- ✅ Easy to add new steps (just listen to events)

**Trade-offs**:
- ❌ Hard to track saga state (distributed across services)
- ❌ Debugging difficult (trace events across services)
- ❌ Eventual consistency (not immediate)

---

#### 2.2 Orchestration (Coordinator)

Central coordinator tells services what to do.

```
Saga Orchestrator
    ↓ 1. Create Order
Order Service
    ↓ 2. Process Payment
Payment Service
    ↓ 3. Reserve Inventory
Inventory Service
    ↓ 4. Complete Order
Order Service
```

**Implementation**:
```python
# TAG: @SPEC:SAGA-002
# Orchestration-based saga

from enum import Enum

class SagaStep(Enum):
    CREATE_ORDER = "create_order"
    PROCESS_PAYMENT = "process_payment"
    RESERVE_INVENTORY = "reserve_inventory"
    COMPLETE_ORDER = "complete_order"

class OrderSagaOrchestrator:
    """
    Saga coordinator - manages distributed transaction.
    Constitution: File ≤500 SLOC (focused on coordination).
    """
    def __init__(
        self,
        order_service,
        payment_service,
        inventory_service
    ):
        self.order_service = order_service
        self.payment_service = payment_service
        self.inventory_service = inventory_service

    async def execute(self, saga_data: dict) -> bool:
        """
        Execute saga steps sequentially.
        Rollback if any step fails.
        """
        executed_steps = []

        try:
            # Step 1: Create Order
            order = await self.order_service.create_order(saga_data)
            executed_steps.append((SagaStep.CREATE_ORDER, order.id))

            # Step 2: Process Payment
            payment = await self.payment_service.charge(
                order_id=order.id,
                amount=order.total
            )
            if not payment.success:
                raise Exception(f"Payment failed: {payment.error}")
            executed_steps.append((SagaStep.PROCESS_PAYMENT, payment.transaction_id))

            # Step 3: Reserve Inventory
            reservation = await self.inventory_service.reserve(
                order_id=order.id,
                items=order.items
            )
            if not reservation.success:
                raise Exception(f"Inventory failed: {reservation.error}")
            executed_steps.append((SagaStep.RESERVE_INVENTORY, reservation.id))

            # Step 4: Complete Order
            await self.order_service.complete_order(order.id)
            executed_steps.append((SagaStep.COMPLETE_ORDER, order.id))

            return True

        except Exception as e:
            # Rollback (compensate in reverse order)
            await self._rollback(executed_steps)
            raise

    async def _rollback(self, executed_steps: List[tuple]):
        """Compensating transactions in reverse order."""
        for step, resource_id in reversed(executed_steps):
            try:
                if step == SagaStep.RESERVE_INVENTORY:
                    await self.inventory_service.release(resource_id)
                elif step == SagaStep.PROCESS_PAYMENT:
                    await self.payment_service.refund(resource_id)
                elif step == SagaStep.CREATE_ORDER:
                    await self.order_service.cancel_order(resource_id)
            except Exception as e:
                # Log compensation failure (manual intervention needed)
                logger.error(f"Compensation failed for {step}: {e}")
```

**Benefits**:
- ✅ Centralized saga state (easy to track)
- ✅ Easier debugging (single orchestrator)
- ✅ Explicit rollback logic

**Trade-offs**:
- ❌ Orchestrator is single point of failure
- ❌ Services coupled to orchestrator
- ❌ Synchronous (blocking)

---

## 3. Event Sourcing

### Concept
Store **events** (what happened) instead of **state** (current snapshot).

**Traditional Approach**:
```sql
-- Store current state
UPDATE orders SET status = 'completed' WHERE id = 123;
```

**Event Sourcing**:
```sql
-- Store event history
INSERT INTO events (aggregate_id, event_type, event_data, occurred_at)
VALUES (123, 'OrderCompleted', '{"total": 99.99}', NOW());
```

### Implementation

```python
# TAG: @SPEC:ES-001
# Event Sourcing implementation

from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class Event:
    """Base event."""
    aggregate_id: int
    occurred_at: datetime

@dataclass
class OrderCreatedEvent(Event):
    user_id: int
    items: List[dict]

@dataclass
class OrderCompletedEvent(Event):
    total_amount: Decimal

class Order:
    """
    Aggregate rebuilt from events (not database state).
    Constitution: Simple apply methods, complexity ≤3 each.
    """
    def __init__(self):
        self.id = None
        self.user_id = None
        self.items = []
        self.status = 'pending'
        self.uncommitted_events = []

    def create(self, order_id: int, user_id: int, items: List[dict]):
        """Command - creates event."""
        event = OrderCreatedEvent(
            aggregate_id=order_id,
            user_id=user_id,
            items=items,
            occurred_at=datetime.utcnow()
        )
        self._apply(event)
        self.uncommitted_events.append(event)

    def complete(self):
        """Command - creates event."""
        event = OrderCompletedEvent(
            aggregate_id=self.id,
            total_amount=self._calculate_total(),
            occurred_at=datetime.utcnow()
        )
        self._apply(event)
        self.uncommitted_events.append(event)

    def _apply(self, event: Event):
        """Apply event to change state."""
        if isinstance(event, OrderCreatedEvent):
            self.id = event.aggregate_id
            self.user_id = event.user_id
            self.items = event.items
            self.status = 'pending'
        elif isinstance(event, OrderCompletedEvent):
            self.status = 'completed'

    @classmethod
    def from_events(cls, events: List[Event]) -> 'Order':
        """Rebuild aggregate from event history."""
        order = cls()
        for event in events:
            order._apply(event)
        return order


# Event Store (PostgreSQL)
class EventStore:
    """
    Store events (append-only).
    Constitution: Simple CRUD, complexity ≤5.
    """
    async def save_events(self, events: List[Event]):
        """Append events to store."""
        for event in events:
            await self.db.execute("""
                INSERT INTO events (aggregate_id, event_type, event_data, occurred_at)
                VALUES ($1, $2, $3, $4)
            """, event.aggregate_id, type(event).__name__, event.__dict__, event.occurred_at)

    async def get_events(self, aggregate_id: int) -> List[Event]:
        """Fetch event history for aggregate."""
        rows = await self.db.fetch("""
            SELECT event_type, event_data FROM events
            WHERE aggregate_id = $1
            ORDER BY occurred_at ASC
        """, aggregate_id)

        return [self._deserialize(row) for row in rows]


# Usage
async def load_order(order_id: int) -> Order:
    """Load order by replaying events."""
    events = await event_store.get_events(order_id)
    return Order.from_events(events)
```

### Benefits
- ✅ **Complete audit trail**: Every state change recorded
- ✅ **Time travel**: Rebuild state at any point in time
- ✅ **Event replay**: Fix bugs by replaying events with corrected logic
- ✅ **Analytics**: Query event history for insights

### Trade-offs
- ❌ **Complexity**: Harder to implement than CRUD
- ❌ **Event versioning**: Events are immutable, need upcasting for schema changes
- ❌ **Query performance**: Need to rebuild state from events (use snapshots)

---

## 4. Circuit Breaker Pattern

### Problem
When a service fails, retries can overwhelm it (cascading failure).

### Solution
Monitor failures, "open circuit" to fail fast instead of retrying.

```
Closed (Normal)
   ↓ (failures exceed threshold)
Open (Fail Fast)
   ↓ (after timeout)
Half-Open (Try One Request)
   ↓ (success) → Closed
   ↓ (failure) → Open
```

### Implementation

```python
# TAG: @SPEC:CB-001
# Circuit Breaker implementation

from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """
    Circuit breaker pattern.
    Constitution: Simple state machine, complexity ≤10.
    """
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: timedelta = timedelta(seconds=60)
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            # Check if timeout elapsed
            if datetime.utcnow() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)

            # Success - reset
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
            self.failure_count = 0

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()

            # Open circuit if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            raise


# Usage
payment_circuit = CircuitBreaker(failure_threshold=3, timeout=timedelta(seconds=30))

async def charge_payment(amount: Decimal):
    """Charge payment with circuit breaker."""
    try:
        return await payment_circuit.call(
            stripe.Charge.create,
            amount=int(amount * 100)
        )
    except Exception as e:
        logger.error(f"Payment failed (circuit: {payment_circuit.state}): {e}")
        raise
```

### Benefits
- ✅ **Fail fast**: Don't wait for timeouts when service is down
- ✅ **Prevents cascading failures**: Stop overwhelming failing service
- ✅ **Automatic recovery**: Circuit closes after timeout

---

## 5. Service Mesh (Istio/Linkerd)

### Problem
Cross-cutting concerns (retries, timeouts, observability) duplicated in every service.

### Solution
Sidecar proxy handles networking concerns.

```
Service A  →  Envoy Proxy  →  Envoy Proxy  →  Service B
              (Sidecar)         (Sidecar)
                ↓                   ↓
          Observability       Load Balancing
          Retry Logic         Circuit Breaking
          mTLS                Rate Limiting
```

### Benefits
- ✅ **Centralized policies**: Retries, timeouts configured in mesh
- ✅ **Observability**: Automatic metrics, tracing
- ✅ **Security**: mTLS between services
- ✅ **Language-agnostic**: Works with any service

### Trade-offs
- ❌ **Operational complexity**: Need to manage Istio/Linkerd
- ❌ **Latency overhead**: Extra proxy hop
- ❌ **Learning curve**: Complex configuration

---

## Constitution Compliance

**File Size**:
- ✅ Each saga step: ≤200 SLOC
- ✅ Circuit breaker: ≤300 SLOC
- ✅ Event store: ≤400 SLOC

**Complexity**:
- ✅ Saga orchestrator: Complexity ≤10 (sequential steps)
- ✅ Event sourcing apply methods: Complexity ≤3 each
- ✅ Circuit breaker state machine: Complexity ≤10

**TAG Integration**:
```python
# TAG: @SPEC:SAGA-001
# TAG: @CODE:SAGA-001
# Every pattern tagged to specification
```

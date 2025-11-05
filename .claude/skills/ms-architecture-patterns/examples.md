# Architecture Patterns Implementation Examples

## Example 1: Full Clean Architecture Implementation (FastAPI + PostgreSQL)

### Requirements
Build a blog platform with:
- User authentication
- Create/read/update/delete posts
- Comments on posts
- Testable without infrastructure

### Directory Structure

```
src/
├── domain/                    # Layer 1: Pure business logic
│   ├── entities/
│   │   ├── post.py           # Post entity with business rules
│   │   ├── comment.py        # Comment entity
│   │   └── user.py           # User entity
│   ├── value_objects/
│   │   ├── email.py          # Email value object (validation)
│   │   └── post_status.py    # PostStatus enum
│   └── exceptions.py          # Domain-specific exceptions
│
├── use_cases/                 # Layer 2: Application logic
│   ├── create_post.py        # CreatePostUseCase
│   ├── publish_post.py       # PublishPostUseCase
│   ├── add_comment.py        # AddCommentUseCase
│   └── ports/                # Interfaces (ports)
│       ├── post_repository.py
│       ├── user_repository.py
│       └── email_service.py
│
├── adapters/                  # Layer 3: Interface adapters
│   ├── controllers/
│   │   ├── post_controller.py   # FastAPI routes
│   │   └── comment_controller.py
│   ├── presenters/
│   │   └── post_presenter.py    # Response formatting
│   └── repositories/             # Repository interfaces
│       ├── post_repo_interface.py
│       └── comment_repo_interface.py
│
└── infrastructure/            # Layer 4: External concerns
    ├── database/
    │   ├── models.py          # SQLAlchemy models
    │   ├── post_repo_impl.py  # PostgreSQL implementation
    │   └── migrations/
    ├── email/
    │   └── sendgrid_adapter.py
    └── config.py
```

### Implementation

#### Layer 1: Domain Entities

```python
# TAG: @SPEC:BLOG-001
# src/domain/entities/post.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class Post:
    """
    Post aggregate root - enforces business rules.
    Pure domain logic with no infrastructure dependencies.
    """
    id: int | None
    author_id: int
    title: str
    content: str
    status: str = 'draft'
    created_at: datetime = field(default_factory=datetime.utcnow)
    published_at: datetime | None = None

    def publish(self) -> None:
        """
        Business rule: Only draft posts can be published.
        Constitution: Simple method, complexity ≤10.
        """
        if self.status == 'published':
            raise ValueError("Post is already published")
        if self.status == 'archived':
            raise ValueError("Cannot publish archived post")

        self.status = 'published'
        self.published_at = datetime.utcnow()

    def archive(self) -> None:
        """Business rule: Only published posts can be archived."""
        if self.status != 'published':
            raise ValueError(f"Cannot archive {self.status} post")

        self.status = 'archived'

    def can_be_edited_by(self, user_id: int) -> bool:
        """Authorization business rule."""
        return self.author_id == user_id

    def update_content(self, new_title: str, new_content: str) -> None:
        """Business rule: Cannot edit published posts."""
        if self.status == 'published':
            raise ValueError("Cannot edit published post")

        self.title = new_title
        self.content = new_content


# TAG: @SPEC:BLOG-002
# src/domain/value_objects/email.py

from dataclasses import dataclass
import re

@dataclass(frozen=True)  # Immutable value object
class Email:
    """Email value object with validation."""
    address: str

    def __post_init__(self):
        """Validate email format in constructor."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, self.address):
            raise ValueError(f"Invalid email format: {self.address}")

    def domain(self) -> str:
        """Extract domain from email."""
        return self.address.split('@')[1]
```

#### Layer 2: Use Cases (Application Logic)

```python
# TAG: @SPEC:BLOG-003
# src/use_cases/ports/post_repository.py

from abc import ABC, abstractmethod
from typing import List
from domain.entities.post import Post

class PostRepository(ABC):
    """
    Port (interface) defined by domain.
    Infrastructure implements this.
    """
    @abstractmethod
    def get_by_id(self, post_id: int) -> Post | None:
        """Fetch post by ID."""
        pass

    @abstractmethod
    def save(self, post: Post) -> Post:
        """Persist post (create or update)."""
        pass

    @abstractmethod
    def find_by_author(self, author_id: int) -> List[Post]:
        """Find all posts by author."""
        pass

    @abstractmethod
    def find_published(self, limit: int = 20) -> List[Post]:
        """Find recently published posts."""
        pass


# TAG: @SPEC:BLOG-004
# src/use_cases/create_post.py

from dataclasses import dataclass
from domain.entities.post import Post
from use_cases.ports.post_repository import PostRepository

@dataclass
class CreatePostCommand:
    """Command - input data transfer object."""
    author_id: int
    title: str
    content: str

class CreatePostUseCase:
    """
    Application-specific business rule.
    Orchestrates domain logic and persistence.
    """
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    def execute(self, command: CreatePostCommand) -> Post:
        """
        Create new post in draft status.
        Constitution: Simple method, single responsibility.
        """
        # Validate input
        if not command.title.strip():
            raise ValueError("Title cannot be empty")
        if not command.content.strip():
            raise ValueError("Content cannot be empty")

        # Create domain entity
        post = Post(
            id=None,
            author_id=command.author_id,
            title=command.title,
            content=command.content,
            status='draft'
        )

        # Persist via repository
        return self.post_repo.save(post)


# TAG: @SPEC:BLOG-005
# src/use_cases/publish_post.py

class PublishPostUseCase:
    """Publish existing post."""
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    def execute(self, post_id: int, user_id: int) -> Post:
        """
        Publish post with authorization check.
        Complexity ≤10 (early returns).
        """
        # Fetch post
        post = self.post_repo.get_by_id(post_id)
        if post is None:
            raise ValueError(f"Post {post_id} not found")

        # Authorization check
        if not post.can_be_edited_by(user_id):
            raise PermissionError("User cannot publish this post")

        # Domain logic
        post.publish()

        # Persist
        return self.post_repo.save(post)
```

#### Layer 3: Controllers (HTTP Adapters)

```python
# TAG: @SPEC:BLOG-006
# src/adapters/controllers/post_controller.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from use_cases.create_post import CreatePostUseCase, CreatePostCommand
from use_cases.publish_post import PublishPostUseCase
from adapters.dependencies import get_current_user, get_create_post_use_case

router = APIRouter(prefix="/posts", tags=["posts"])

class CreatePostRequest(BaseModel):
    """HTTP request schema."""
    title: str
    content: str

class PostResponse(BaseModel):
    """HTTP response schema."""
    id: int
    title: str
    content: str
    status: str
    author_id: int


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: CreatePostRequest,
    current_user_id: int = Depends(get_current_user),
    use_case: CreatePostUseCase = Depends(get_create_post_use_case)
):
    """
    HTTP adapter - translates HTTP request to use case command.
    No business logic here (just translation).
    """
    try:
        command = CreatePostCommand(
            author_id=current_user_id,
            title=request.title,
            content=request.content
        )
        post = use_case.execute(command)

        return PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            status=post.status,
            author_id=post.author_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{post_id}/publish", response_model=PostResponse)
async def publish_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user),
    use_case: PublishPostUseCase = Depends(get_publish_post_use_case)
):
    """Publish post endpoint."""
    try:
        post = use_case.execute(post_id, current_user_id)
        return PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            status=post.status,
            author_id=post.author_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
```

#### Layer 4: Infrastructure (PostgreSQL Adapter)

```python
# TAG: @SPEC:BLOG-007
# src/infrastructure/database/post_repo_impl.py

from sqlalchemy.orm import Session
from typing import List
from domain.entities.post import Post
from use_cases.ports.post_repository import PostRepository
from infrastructure.database.models import PostModel

class PostgreSQLPostRepository(PostRepository):
    """
    Adapter - implements repository port.
    Infrastructure layer depends on domain (port).
    """
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_id(self, post_id: int) -> Post | None:
        """Fetch from PostgreSQL and map to domain entity."""
        model = self.db.query(PostModel).filter(PostModel.id == post_id).first()
        if model is None:
            return None

        return self._to_entity(model)

    def save(self, post: Post) -> Post:
        """Persist domain entity to PostgreSQL."""
        if post.id is None:
            # Create new
            model = PostModel(
                author_id=post.author_id,
                title=post.title,
                content=post.content,
                status=post.status,
                created_at=post.created_at,
                published_at=post.published_at
            )
            self.db.add(model)
        else:
            # Update existing
            model = self.db.query(PostModel).filter(PostModel.id == post.id).first()
            model.title = post.title
            model.content = post.content
            model.status = post.status
            model.published_at = post.published_at

        self.db.commit()
        self.db.refresh(model)

        return self._to_entity(model)

    def find_by_author(self, author_id: int) -> List[Post]:
        """Find all posts by author."""
        models = self.db.query(PostModel).filter(PostModel.author_id == author_id).all()
        return [self._to_entity(m) for m in models]

    def find_published(self, limit: int = 20) -> List[Post]:
        """Find recently published posts."""
        models = (
            self.db.query(PostModel)
            .filter(PostModel.status == 'published')
            .order_by(PostModel.published_at.desc())
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: PostModel) -> Post:
        """Map SQLAlchemy model to domain entity."""
        return Post(
            id=model.id,
            author_id=model.author_id,
            title=model.title,
            content=model.content,
            status=model.status,
            created_at=model.created_at,
            published_at=model.published_at
        )
```

#### Testing (No Infrastructure)

```python
# TAG: @TEST:BLOG-004
# tests/use_cases/test_create_post.py

import pytest
from domain.entities.post import Post
from use_cases.create_post import CreatePostUseCase, CreatePostCommand
from use_cases.ports.post_repository import PostRepository

class FakePostRepository(PostRepository):
    """
    Fake repository - in-memory implementation for testing.
    No database needed!
    """
    def __init__(self):
        self.posts = {}
        self.next_id = 1

    def get_by_id(self, post_id: int) -> Post | None:
        return self.posts.get(post_id)

    def save(self, post: Post) -> Post:
        if post.id is None:
            post.id = self.next_id
            self.next_id += 1
        self.posts[post.id] = post
        return post

    def find_by_author(self, author_id: int) -> List[Post]:
        return [p for p in self.posts.values() if p.author_id == author_id]

    def find_published(self, limit: int = 20) -> List[Post]:
        published = [p for p in self.posts.values() if p.status == 'published']
        return sorted(published, key=lambda p: p.published_at, reverse=True)[:limit]


def test_create_post_success():
    """Test creating post without database."""
    # Arrange
    repo = FakePostRepository()
    use_case = CreatePostUseCase(repo)
    command = CreatePostCommand(
        author_id=1,
        title="Test Post",
        content="Test content"
    )

    # Act
    post = use_case.execute(command)

    # Assert
    assert post.id == 1
    assert post.title == "Test Post"
    assert post.status == 'draft'


def test_create_post_empty_title():
    """Test validation - empty title."""
    repo = FakePostRepository()
    use_case = CreatePostUseCase(repo)
    command = CreatePostCommand(author_id=1, title="", content="Content")

    with pytest.raises(ValueError, match="Title cannot be empty"):
        use_case.execute(command)
```

---

## Example 2: Hexagonal Architecture (Payment System)

### Multiple Payment Providers (Stripe, PayPal, Crypto)

```python
# TAG: @SPEC:PAY-001
# Port (interface)
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    CRYPTO = "crypto"

@dataclass
class PaymentResult:
    success: bool
    transaction_id: str | None
    error_message: str | None
    provider: str

class PaymentGateway(ABC):
    """Port - domain defines interface."""
    @abstractmethod
    async def charge(
        self,
        amount: Decimal,
        currency: str,
        payment_token: str,
        metadata: dict
    ) -> PaymentResult:
        pass

    @abstractmethod
    async def refund(self, transaction_id: str, amount: Decimal) -> PaymentResult:
        pass


# TAG: @SPEC:PAY-002
# Stripe Adapter
import stripe

class StripePaymentGateway(PaymentGateway):
    """Stripe implementation of payment port."""
    def __init__(self, api_key: str):
        stripe.api_key = api_key

    async def charge(
        self,
        amount: Decimal,
        currency: str,
        payment_token: str,
        metadata: dict
    ) -> PaymentResult:
        try:
            charge = stripe.Charge.create(
                amount=int(amount * 100),  # Stripe uses cents
                currency=currency.lower(),
                source=payment_token,
                metadata=metadata
            )
            return PaymentResult(
                success=True,
                transaction_id=charge.id,
                error_message=None,
                provider="stripe"
            )
        except stripe.error.CardError as e:
            return PaymentResult(
                success=False,
                transaction_id=None,
                error_message=str(e),
                provider="stripe"
            )

    async def refund(self, transaction_id: str, amount: Decimal) -> PaymentResult:
        try:
            refund = stripe.Refund.create(
                charge=transaction_id,
                amount=int(amount * 100)
            )
            return PaymentResult(
                success=True,
                transaction_id=refund.id,
                error_message=None,
                provider="stripe"
            )
        except stripe.error.StripeError as e:
            return PaymentResult(
                success=False,
                transaction_id=None,
                error_message=str(e),
                provider="stripe"
            )


# TAG: @SPEC:PAY-003
# PayPal Adapter
class PayPalPaymentGateway(PaymentGateway):
    """PayPal implementation - same interface!"""
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    async def charge(
        self,
        amount: Decimal,
        currency: str,
        payment_token: str,
        metadata: dict
    ) -> PaymentResult:
        # PayPal-specific logic
        # Different API, same interface
        pass


# TAG: @SPEC:PAY-004
# Crypto Adapter (Bitcoin)
class CryptoPaymentGateway(PaymentGateway):
    """Cryptocurrency payment adapter."""
    def __init__(self, wallet_address: str):
        self.wallet_address = wallet_address

    async def charge(
        self,
        amount: Decimal,
        currency: str,
        payment_token: str,
        metadata: dict
    ) -> PaymentResult:
        # Blockchain-specific logic
        # Convert amount to BTC, create transaction
        pass


# TAG: @SPEC:PAY-005
# Use Case (depends on port, not adapter)
class ProcessOrderPaymentUseCase:
    """
    Domain logic independent of payment provider.
    Can swap Stripe → PayPal without changing this code!
    """
    def __init__(
        self,
        payment_gateway: PaymentGateway,  # Port, not specific adapter
        order_repo: OrderRepository
    ):
        self.payment_gateway = payment_gateway
        self.order_repo = order_repo

    async def execute(self, order_id: int, payment_token: str) -> bool:
        """Process payment for order."""
        # Fetch order
        order = self.order_repo.get_by_id(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")

        # Charge via payment gateway (don't care which provider)
        result = await self.payment_gateway.charge(
            amount=order.total_amount,
            currency="USD",
            payment_token=payment_token,
            metadata={"order_id": order_id}
        )

        if result.success:
            order.mark_as_paid(result.transaction_id)
            self.order_repo.save(order)
            return True
        else:
            # Log error, notify user
            return False


# TAG: @SPEC:PAY-006
# Dependency Injection (swap adapters easily)
from fastapi import Depends
from infrastructure.config import get_settings

def get_payment_gateway() -> PaymentGateway:
    """Factory function - swap implementation via config."""
    settings = get_settings()

    if settings.payment_provider == "stripe":
        return StripePaymentGateway(api_key=settings.stripe_api_key)
    elif settings.payment_provider == "paypal":
        return PayPalPaymentGateway(
            client_id=settings.paypal_client_id,
            client_secret=settings.paypal_client_secret
        )
    elif settings.payment_provider == "crypto":
        return CryptoPaymentGateway(wallet_address=settings.crypto_wallet)
    else:
        raise ValueError(f"Unknown payment provider: {settings.payment_provider}")


# Controller (uses factory)
@router.post("/orders/{order_id}/pay")
async def pay_for_order(
    order_id: int,
    payment_token: str,
    payment_gateway: PaymentGateway = Depends(get_payment_gateway)
):
    """Payment endpoint - provider-agnostic!"""
    use_case = ProcessOrderPaymentUseCase(payment_gateway, order_repo)
    success = await use_case.execute(order_id, payment_token)
    return {"success": success}
```

**Benefits**:
- ✅ Swap Stripe → PayPal with 1-line config change
- ✅ Test with fake gateway (no real API calls)
- ✅ Add new provider (Crypto) without changing domain logic
- ✅ Domain doesn't know about Stripe/PayPal implementation details

---

## Example 3: DDD Aggregate with Domain Events

```python
# TAG: @SPEC:DDD-EVENTS-001
# Domain Events

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List

@dataclass
class DomainEvent:
    """Base class for domain events."""
    occurred_at: datetime

@dataclass
class OrderCreatedEvent(DomainEvent):
    order_id: int
    user_id: int
    total_amount: Decimal

@dataclass
class OrderCompletedEvent(DomainEvent):
    order_id: int
    user_id: int
    total_amount: Decimal
    items_count: int


# TAG: @SPEC:DDD-EVENTS-002
# Aggregate Root with Events

class Order:
    """
    Aggregate root - emits domain events.
    Events notify other parts of system without tight coupling.
    """
    def __init__(self, id: int, user_id: int):
        self.id = id
        self.user_id = user_id
        self.items: List[OrderItem] = []
        self.status = 'pending'
        self.events: List[DomainEvent] = []  # Uncommitted events

    def add_item(self, product_id: int, quantity: int, price: Decimal) -> None:
        """Add item to order."""
        if self.status != 'pending':
            raise ValueError("Cannot modify completed order")

        self.items.append(OrderItem(product_id, quantity, price))

    def complete(self) -> None:
        """Complete order and emit event."""
        if not self.items:
            raise ValueError("Cannot complete order with no items")

        self.status = 'completed'

        # Emit domain event
        self.events.append(OrderCompletedEvent(
            order_id=self.id,
            user_id=self.user_id,
            total_amount=self.calculate_total(),
            items_count=len(self.items),
            occurred_at=datetime.utcnow()
        ))


# TAG: @SPEC:DDD-EVENTS-003
# Event Publisher (infrastructure)

class EventPublisher:
    """Publishes domain events to message queue."""
    def __init__(self, message_broker):
        self.broker = message_broker

    async def publish(self, event: DomainEvent) -> None:
        """Send event to RabbitMQ/Kafka."""
        await self.broker.publish(
            exchange="domain_events",
            routing_key=type(event).__name__,
            message=event
        )


# TAG: @SPEC:DDD-EVENTS-004
# Use Case with Event Publishing

class CompleteOrderUseCase:
    """Complete order and publish events."""
    def __init__(
        self,
        order_repo: OrderRepository,
        event_publisher: EventPublisher
    ):
        self.order_repo = order_repo
        self.event_publisher = event_publisher

    async def execute(self, order_id: int) -> None:
        """Complete order and publish events."""
        # Load aggregate
        order = self.order_repo.get_by_id(order_id)

        # Execute domain logic (emits events)
        order.complete()

        # Persist aggregate
        self.order_repo.save(order)

        # Publish uncommitted events
        for event in order.events:
            await self.event_publisher.publish(event)

        # Clear events after publishing
        order.events.clear()


# TAG: @SPEC:DDD-EVENTS-005
# Event Handlers (decoupled services)

class SendOrderConfirmationEmailHandler:
    """
    Event handler - reacts to OrderCompletedEvent.
    Decoupled from order service via events.
    """
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    async def handle(self, event: OrderCompletedEvent) -> None:
        """Send confirmation email when order completed."""
        await self.email_service.send(
            to_user_id=event.user_id,
            subject="Order Confirmed",
            template="order_confirmation",
            data={"order_id": event.order_id, "total": event.total_amount}
        )

class UpdateInventoryHandler:
    """Update inventory when order completed."""
    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service

    async def handle(self, event: OrderCompletedEvent) -> None:
        """Decrease inventory for ordered items."""
        await self.inventory_service.reserve_items(event.order_id)
```

**Benefits**:
- ✅ Decoupled services (email, inventory don't depend on order service)
- ✅ Asynchronous processing (events handled in background)
- ✅ Easy to add new handlers (analytics, notifications)
- ✅ Event sourcing foundation (store events as audit log)

---

## Constitution Compliance Examples

### File Size Splitting

```python
# ❌ Violates Constitution (1200 lines in one file)
# order_service.py

class OrderService:
    def create_order(...):  # 200 lines
    def update_order(...):  # 200 lines
    def cancel_order(...):  # 200 lines
    def calculate_shipping(...):  # 200 lines
    def apply_discount(...):  # 200 lines
    def send_confirmation(...):  # 200 lines
    # ... 1200 total lines


# ✅ Constitution-compliant (split by bounded context)

# order_lifecycle.py (300 lines)
class OrderLifecycle:
    def create(...): pass
    def update(...): pass
    def cancel(...): pass

# order_pricing.py (250 lines)
class OrderPricing:
    def calculate_shipping(...): pass
    def apply_discount(...): pass

# order_notifications.py (200 lines)
class OrderNotifications:
    def send_confirmation(...): pass
    def send_cancellation(...): pass
```

### Complexity Reduction

```python
# ❌ Cyclomatic complexity = 18
def calculate_discount(order):
    if order.user.is_premium:
        if order.total > 1000:
            if order.items_count > 10:
                if order.user.loyalty_points > 500:
                    # ... 10 more nested ifs
                    return 0.3
    return 0


# ✅ Complexity ≤10 (strategy pattern)
class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, order: Order) -> Decimal:
        pass

class PremiumUserDiscount(DiscountStrategy):
    def calculate(self, order: Order) -> Decimal:
        if order.total > 1000:
            return Decimal("0.15")
        return Decimal("0.10")

class BulkOrderDiscount(DiscountStrategy):
    def calculate(self, order: Order) -> Decimal:
        if order.items_count > 10:
            return Decimal("0.20")
        return Decimal("0")

# Simple dispatcher (complexity = 3)
def calculate_discount(order: Order) -> Decimal:
    if order.user.is_premium:
        return PremiumUserDiscount().calculate(order)
    if order.items_count > 10:
        return BulkOrderDiscount().calculate(order)
    return Decimal("0")
```

---
name: api-testing-patterns
description: Comprehensive API testing methodology covering REST API testing (CRUD operations, status codes, headers), GraphQL testing (queries, mutations, subscriptions), contract validation with Pact and Spring Cloud Contract, integration testing with real dependencies, idempotency verification for POST/PUT/DELETE operations, authentication and authorization flow testing (JWT, OAuth2, API keys), request/response schema validation with OpenAPI and JSON Schema, error scenario handling (4xx/5xx codes, timeouts, rate limits), consumer-driven contract testing patterns for microservices, performance testing with load and stress scenarios, automated test generation from API specifications, and CI/CD pipeline integration with pytest 8.4.2 and Vitest 2.1 for production-ready API systems with ≥85% coverage
---

# API Testing Patterns

Comprehensive API testing methodology covering REST API testing, GraphQL testing, contract validation, integration testing, and idempotency verification. Apply when implementing API endpoints, testing request/response validation, ensuring authentication security, handling error scenarios, or validating API contracts across microservices. Provides consumer-driven contract testing patterns, performance testing strategies, and automated test generation for production-ready API systems.

---

## Core Principles

**APIs Are Contracts**: Focus on validating the agreement between consumer and provider rather than internal implementation details.

**Consumer Perspective**: Always test from the consumer's viewpoint - what they expect, not how it's implemented.

**Three Testing Levels**:
1. **Contract Testing**: Verify consumer-provider agreement
2. **Integration Testing**: Test with real dependencies
3. **Component Testing**: Test in isolation with mocks

---

## When to Use This Skill

Apply this skill when:

- **Implementing REST APIs** with CRUD operations
- **Testing GraphQL** queries and mutations
- **Validating API contracts** in microservices
- **Testing authentication** and authorization flows
- **Ensuring request validation** for inputs
- **Testing error handling** for edge cases
- **Verifying idempotency** for repeated operations
- **Testing API endpoints** with integration tests
- **Checking response validation** against schemas
- **Testing concurrency** and race conditions
- **Performance testing** API throughput
- **Automating API tests** in CI/CD pipelines

**Don't use when:**
- Testing implementation details (use unit tests)
- APIs are still in design phase (create contracts first)
- No consumer requirements defined

---

## Testing Levels Deep Dive

### 1. Contract Testing

**Purpose:** Verify that provider and consumer align on expectations using formal contracts.

**Pattern:** Consumer-Driven Contracts (CDC)

**Tools:** Pact, Spring Cloud Contract, Postman Contract Testing

**When to Use:**
- Microservices architectures
- Multiple consumers of same API
- Third-party integrations
- Independent team deployments

**Python Example (using Pact):**
```python
import pytest
from pact import Consumer, Provider, Like, EachLike
from your_api_client import UserAPIClient

# Define consumer contract
pact = Consumer('UserService').has_pact_with(
    Provider('UserAPIProvider'),
    pact_dir='./pacts'
)

def test_get_user_contract():
    """Contract test: Consumer expects specific user response format."""

    # Define expected interaction
    expected = {
        'id': Like(123),
        'username': Like('john_doe'),
        'email': Like('john@example.com'),
        'created_at': Like('2025-01-15T10:00:00Z'),
        'roles': EachLike('user')
    }

    (pact
     .given('User 123 exists')
     .upon_receiving('a request for user 123')
     .with_request('GET', '/api/users/123')
     .will_respond_with(200, body=expected))

    with pact:
        # Execute actual API call
        client = UserAPIClient('http://localhost:1234')
        user = client.get_user(123)

        # Verify contract
        assert user['id'] == 123
        assert user['username'] == 'john_doe'
        assert 'email' in user
        assert isinstance(user['roles'], list)

def test_create_user_contract():
    """Contract test: Consumer sends user creation request."""

    request_body = {
        'username': Like('new_user'),
        'email': Like('new@example.com'),
        'password': Like('secure_password')
    }

    response_body = {
        'id': Like(456),
        'username': Like('new_user'),
        'email': Like('new@example.com')
    }

    (pact
     .given('No user with username new_user exists')
     .upon_receiving('a request to create user')
     .with_request('POST', '/api/users', body=request_body)
     .will_respond_with(201, body=response_body))

    with pact:
        client = UserAPIClient('http://localhost:1234')
        user = client.create_user('new_user', 'new@example.com', 'secure_password')

        assert user['id'] is not None
        assert user['username'] == 'new_user'
```

**TypeScript Example (using Pact):**
```typescript
import { Pact, Matchers } from '@pact-foundation/pact';
import { UserAPIClient } from './userApiClient';

const { like, eachLike } = Matchers;

describe('User API Contract', () => {
  const provider = new Pact({
    consumer: 'UserService',
    provider: 'UserAPIProvider',
    port: 1234,
    log: './logs/pact.log',
    dir: './pacts',
  });

  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());
  afterEach(() => provider.verify());

  test('get user by id', async () => {
    // Define expected interaction
    await provider.addInteraction({
      state: 'User 123 exists',
      uponReceiving: 'a request for user 123',
      withRequest: {
        method: 'GET',
        path: '/api/users/123',
      },
      willRespondWith: {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: {
          id: like(123),
          username: like('john_doe'),
          email: like('john@example.com'),
          createdAt: like('2025-01-15T10:00:00Z'),
          roles: eachLike('user'),
        },
      },
    });

    // Execute API call
    const client = new UserAPIClient('http://localhost:1234');
    const user = await client.getUser(123);

    // Verify contract
    expect(user.id).toBe(123);
    expect(user.username).toBe('john_doe');
    expect(user.email).toBeDefined();
    expect(Array.isArray(user.roles)).toBe(true);
  });

  test('create user', async () => {
    await provider.addInteraction({
      state: 'No user with username new_user exists',
      uponReceiving: 'a request to create user',
      withRequest: {
        method: 'POST',
        path: '/api/users',
        headers: { 'Content-Type': 'application/json' },
        body: {
          username: like('new_user'),
          email: like('new@example.com'),
          password: like('secure_password'),
        },
      },
      willRespondWith: {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
        body: {
          id: like(456),
          username: like('new_user'),
          email: like('new@example.com'),
        },
      },
    });

    const client = new UserAPIClient('http://localhost:1234');
    const user = await client.createUser('new_user', 'new@example.com', 'secure_password');

    expect(user.id).toBeDefined();
    expect(user.username).toBe('new_user');
  });
});
```

### 2. Integration Testing

**Purpose:** Confirm API functions correctly with real dependencies (database, external services).

**Pattern:** Test Against Real Infrastructure

**When to Use:**
- Testing business logic spanning multiple components
- Verifying end-to-end workflows
- Database interactions
- Third-party service integration

**Python Example (using pytest + FastAPI):**
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from your_app.main import app
from your_app.database import Base, get_db
from your_app.models import User

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def test_db():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    """Create test client with test database."""
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

def test_create_and_get_user_integration(client):
    """Integration test: Create user and retrieve it."""

    # Create user
    response = client.post(
        "/api/users",
        json={
            "username": "integration_test_user",
            "email": "integration@example.com",
            "password": "securepass123"
        }
    )
    assert response.status_code == 201
    created_user = response.json()
    user_id = created_user['id']

    # Retrieve user
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200

    user = response.json()
    assert user['id'] == user_id
    assert user['username'] == "integration_test_user"
    assert user['email'] == "integration@example.com"
    assert 'password' not in user  # Password should not be exposed

def test_user_authentication_flow_integration(client):
    """Integration test: Full authentication flow."""

    # Register user
    response = client.post(
        "/api/auth/register",
        json={
            "username": "auth_test_user",
            "email": "auth@example.com",
            "password": "securepass123"
        }
    )
    assert response.status_code == 201

    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "username": "auth_test_user",
            "password": "securepass123"
        }
    )
    assert response.status_code == 200
    auth_data = response.json()
    assert 'access_token' in auth_data
    token = auth_data['access_token']

    # Access protected endpoint
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    user = response.json()
    assert user['username'] == "auth_test_user"
```

**TypeScript Example (using Vitest + Express):**
```typescript
import { describe, test, expect, beforeAll, afterAll } from 'vitest';
import request from 'supertest';
import { app } from '../src/app';
import { db } from '../src/database';

describe('User API Integration Tests', () => {
  beforeAll(async () => {
    // Setup test database
    await db.migrate.latest();
  });

  afterAll(async () => {
    // Cleanup
    await db.migrate.rollback();
    await db.destroy();
  });

  test('create and get user integration', async () => {
    // Create user
    const createResponse = await request(app)
      .post('/api/users')
      .send({
        username: 'integration_test_user',
        email: 'integration@example.com',
        password: 'securepass123',
      })
      .expect(201);

    const createdUser = createResponse.body;
    const userId = createdUser.id;

    // Retrieve user
    const getResponse = await request(app)
      .get(`/api/users/${userId}`)
      .expect(200);

    const user = getResponse.body;
    expect(user.id).toBe(userId);
    expect(user.username).toBe('integration_test_user');
    expect(user.email).toBe('integration@example.com');
    expect(user.password).toBeUndefined(); // Password should not be exposed
  });

  test('user authentication flow integration', async () => {
    // Register user
    await request(app)
      .post('/api/auth/register')
      .send({
        username: 'auth_test_user',
        email: 'auth@example.com',
        password: 'securepass123',
      })
      .expect(201);

    // Login
    const loginResponse = await request(app)
      .post('/api/auth/login')
      .send({
        username: 'auth_test_user',
        password: 'securepass123',
      })
      .expect(200);

    const authData = loginResponse.body;
    expect(authData.access_token).toBeDefined();
    const token = authData.access_token;

    // Access protected endpoint
    const meResponse = await request(app)
      .get('/api/users/me')
      .set('Authorization', `Bearer ${token}`)
      .expect(200);

    const user = meResponse.body;
    expect(user.username).toBe('auth_test_user');
  });
});
```

### 3. Component Testing

**Purpose:** Validate API in isolation with mocked external dependencies.

**Pattern:** Mock External Dependencies

**When to Use:**
- Testing error handling
- Testing edge cases
- Fast feedback loop
- No external service dependencies

**Python Example (using pytest + mocks):**
```python
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from your_app.main import app
from your_app.exceptions import ExternalServiceError

client = TestClient(app)

@patch('your_app.services.external_payment_service')
def test_payment_processing_with_gateway_failure(mock_payment_service):
    """Component test: Handle payment gateway failure gracefully."""

    # Mock external payment service to simulate failure
    mock_payment_service.process_payment.side_effect = ExternalServiceError(
        "Payment gateway unavailable"
    )

    response = client.post(
        "/api/payments",
        json={
            "user_id": "user_123",
            "amount": 99.99,
            "payment_method": "credit_card"
        }
    )

    # Should return 503 Service Unavailable
    assert response.status_code == 503
    error = response.json()
    assert error['error_type'] == 'external_service_error'
    assert 'payment gateway' in error['message'].lower()

@patch('your_app.services.email_service')
def test_user_creation_with_email_failure(mock_email_service):
    """Component test: User creation succeeds even if welcome email fails."""

    # Mock email service to fail
    mock_email_service.send_welcome_email.side_effect = Exception("SMTP server down")

    response = client.post(
        "/api/users",
        json={
            "username": "test_user",
            "email": "test@example.com",
            "password": "securepass123"
        }
    )

    # User should still be created
    assert response.status_code == 201
    user = response.json()
    assert user['username'] == "test_user"

    # Verify email was attempted but failure was handled
    mock_email_service.send_welcome_email.assert_called_once()
```

**TypeScript Example (using Vitest + mocks):**
```typescript
import { describe, test, expect, vi } from 'vitest';
import request from 'supertest';
import { app } from '../src/app';
import * as paymentService from '../src/services/paymentService';
import * as emailService from '../src/services/emailService';

describe('Component Tests with Mocked Dependencies', () => {
  test('payment processing with gateway failure', async () => {
    // Mock external payment service to simulate failure
    vi.spyOn(paymentService, 'processPayment').mockRejectedValue(
      new Error('Payment gateway unavailable')
    );

    const response = await request(app)
      .post('/api/payments')
      .send({
        userId: 'user_123',
        amount: 99.99,
        paymentMethod: 'credit_card',
      })
      .expect(503);

    const error = response.body;
    expect(error.errorType).toBe('external_service_error');
    expect(error.message.toLowerCase()).toContain('payment gateway');
  });

  test('user creation with email failure', async () => {
    // Mock email service to fail
    vi.spyOn(emailService, 'sendWelcomeEmail').mockRejectedValue(
      new Error('SMTP server down')
    );

    const response = await request(app)
      .post('/api/users')
      .send({
        username: 'test_user',
        email: 'test@example.com',
        password: 'securepass123',
      })
      .expect(201);

    // User should still be created
    const user = response.body;
    expect(user.username).toBe('test_user');

    // Verify email was attempted
    expect(emailService.sendWelcomeEmail).toHaveBeenCalledOnce();
  });
});
```

---

## Critical Test Scenarios

### Authentication & Authorization

**Test Cases:**

1. **Reject Unauthenticated Requests (401)**
```python
def test_protected_endpoint_without_auth(client):
    """Should reject requests without authentication."""
    response = client.get("/api/users/me")
    assert response.status_code == 401
    assert response.json()['error'] == 'authentication_required'
```

2. **Reject Expired Credentials (401)**
```python
def test_expired_token(client):
    """Should reject expired tokens."""
    expired_token = generate_expired_token()
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert 'expired' in response.json()['message'].lower()
```

3. **Enforce Resource-Level Access Control (403)**
```python
def test_unauthorized_resource_access(client, user_token, other_user_id):
    """Should prevent accessing other users' resources."""
    response = client.get(
        f"/api/users/{other_user_id}/private-data",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    assert response.json()['error'] == 'forbidden'
```

### Input Validation

**Test Cases:**

1. **Validate Required Fields**
```python
def test_create_user_missing_required_field(client):
    """Should reject request with missing required fields."""
    response = client.post(
        "/api/users",
        json={"username": "test_user"}  # Missing email and password
    )
    assert response.status_code == 422
    errors = response.json()['errors']
    assert any(e['field'] == 'email' for e in errors)
    assert any(e['field'] == 'password' for e in errors)
```

2. **Verify Data Type Constraints**
```python
def test_invalid_data_types(client):
    """Should reject invalid data types."""
    response = client.post(
        "/api/products",
        json={
            "name": "Product",
            "price": "not_a_number",  # Should be float
            "quantity": "10"  # Should be int
        }
    )
    assert response.status_code == 422
```

3. **Check Value Range Boundaries**
```python
def test_value_out_of_range(client):
    """Should enforce value range constraints."""
    response = client.post(
        "/api/users",
        json={
            "username": "a",  # Too short (min 3 chars)
            "email": "valid@example.com",
            "age": 150  # Too high (max 120)
        }
    )
    assert response.status_code == 422
```

### Error Handling

**Test Cases:**

1. **Handle Service Unavailability Gracefully**
```python
@patch('your_app.services.external_service')
def test_external_service_unavailable(mock_service, client):
    """Should return 503 when external service is down."""
    mock_service.call.side_effect = ConnectionError("Service unavailable")

    response = client.get("/api/external-data")
    assert response.status_code == 503
    assert response.json()['error'] == 'service_unavailable'
```

2. **Process Malformed Input Appropriately**
```python
def test_malformed_json(client):
    """Should return 400 for malformed JSON."""
    response = client.post(
        "/api/users",
        data="{ invalid json }",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert 'malformed' in response.json()['message'].lower()
```

3. **Avoid Leaking Internal Details**
```python
def test_internal_error_no_leak(client):
    """Should not expose internal error details to client."""
    response = client.get("/api/trigger-internal-error")
    assert response.status_code == 500

    error = response.json()
    # Should not contain stack traces or internal paths
    assert 'traceback' not in str(error).lower()
    assert '/app/src/' not in str(error)
```

### Idempotency

**Test Cases:**

1. **Ensure Repeated Requests Produce Identical Outcomes**
```python
def test_create_user_idempotency(client):
    """Should handle duplicate user creation idempotently."""

    user_data = {
        "username": "unique_user",
        "email": "unique@example.com",
        "password": "securepass123"
    }

    # First request
    response1 = client.post("/api/users", json=user_data)
    assert response1.status_code == 201
    user1 = response1.json()

    # Second identical request
    response2 = client.post("/api/users", json=user_data)
    assert response2.status_code == 409  # Conflict
    assert 'already exists' in response2.json()['message'].lower()
```

2. **Implement Proper Request Deduplication**
```python
def test_payment_idempotency_key(client, auth_token):
    """Should use idempotency key to prevent duplicate payments."""

    idempotency_key = str(uuid.uuid4())

    payment_data = {
        "amount": 99.99,
        "payment_method": "credit_card"
    }

    # First request
    response1 = client.post(
        "/api/payments",
        json=payment_data,
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Idempotency-Key": idempotency_key
        }
    )
    assert response1.status_code == 201
    payment1 = response1.json()

    # Duplicate request with same idempotency key
    response2 = client.post(
        "/api/payments",
        json=payment_data,
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Idempotency-Key": idempotency_key
        }
    )
    assert response2.status_code == 200  # Returns existing payment
    payment2 = response2.json()
    assert payment1['id'] == payment2['id']  # Same payment
```

### Concurrency

**Test Cases:**

1. **Test Race Conditions**
```python
import threading

def test_concurrent_account_updates(client, auth_token):
    """Should handle concurrent updates without data corruption."""

    def update_balance(amount):
        client.patch(
            "/api/account/balance",
            json={"amount": amount},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

    # Execute concurrent updates
    threads = [
        threading.Thread(target=update_balance, args=(10,))
        for _ in range(5)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify final balance is correct
    response = client.get(
        "/api/account/balance",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()['balance'] == 50  # 5 * 10
```

2. **Validate Concurrent Modification Handling**
```python
def test_optimistic_locking(client, auth_token):
    """Should use version control to prevent lost updates."""

    # Get current version
    response = client.get("/api/document/123")
    doc = response.json()
    version = doc['version']

    # Update with correct version
    response1 = client.put(
        "/api/document/123",
        json={"content": "Update 1", "version": version}
    )
    assert response1.status_code == 200

    # Update with stale version
    response2 = client.put(
        "/api/document/123",
        json={"content": "Update 2", "version": version}  # Stale version
    )
    assert response2.status_code == 409  # Conflict
    assert 'version mismatch' in response2.json()['message'].lower()
```

---

## REST API Testing Patterns

### CRUD Operations

```python
class TestUserCRUD:
    """Complete CRUD operation tests for User resource."""

    def test_create_user(self, client):
        """Create (POST): Should return 201 with user data."""
        response = client.post(
            "/api/users",
            json={
                "username": "new_user",
                "email": "new@example.com",
                "password": "securepass123"
            }
        )
        assert response.status_code == 201
        user = response.json()
        assert user['id'] is not None
        assert user['username'] == "new_user"
        assert 'password' not in user  # Sensitive data excluded

    def test_read_user(self, client, existing_user_id):
        """Read (GET): Should return 200 with user data."""
        response = client.get(f"/api/users/{existing_user_id}")
        assert response.status_code == 200
        user = response.json()
        assert user['id'] == existing_user_id
        assert 'username' in user
        assert 'email' in user

    def test_update_user(self, client, existing_user_id, auth_token):
        """Update (PUT/PATCH): Should return 200 with updated data."""
        response = client.patch(
            f"/api/users/{existing_user_id}",
            json={"email": "updated@example.com"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        user = response.json()
        assert user['email'] == "updated@example.com"

    def test_delete_user(self, client, existing_user_id, auth_token):
        """Delete (DELETE): Should return 204."""
        response = client.delete(
            f"/api/users/{existing_user_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 204

        # Verify deletion
        response = client.get(f"/api/users/{existing_user_id}")
        assert response.status_code == 404
```

### Pagination

```python
def test_pagination_with_limit_offset(client):
    """Should paginate results correctly."""
    response = client.get("/api/users?limit=10&offset=0")
    assert response.status_code == 200

    data = response.json()
    assert len(data['items']) <= 10
    assert data['total'] > 0
    assert data['limit'] == 10
    assert data['offset'] == 0
    assert 'next' in data  # Next page URL

def test_pagination_navigation(client):
    """Should navigate through pages correctly."""
    # First page
    response1 = client.get("/api/users?page=1&page_size=5")
    page1 = response1.json()

    # Second page
    response2 = client.get("/api/users?page=2&page_size=5")
    page2 = response2.json()

    # Pages should have different items
    page1_ids = {user['id'] for user in page1['items']}
    page2_ids = {user['id'] for user in page2['items']}
    assert page1_ids.isdisjoint(page2_ids)

def test_pagination_total_count(client):
    """Should return accurate total count."""
    response = client.get("/api/users?page_size=10")
    data = response.json()

    assert data['total'] >= len(data['items'])
    assert data['page_count'] == (data['total'] + 9) // 10
```

### Filtering & Sorting

```python
def test_filter_by_single_field(client):
    """Should filter results by field value."""
    response = client.get("/api/users?status=active")
    assert response.status_code == 200

    users = response.json()['items']
    assert all(user['status'] == 'active' for user in users)

def test_filter_by_multiple_fields(client):
    """Should filter by multiple criteria."""
    response = client.get("/api/users?status=active&role=admin")
    assert response.status_code == 200

    users = response.json()['items']
    assert all(user['status'] == 'active' for user in users)
    assert all(user['role'] == 'admin' for user in users)

def test_sort_ascending(client):
    """Should sort results in ascending order."""
    response = client.get("/api/users?sort=created_at&order=asc")
    assert response.status_code == 200

    users = response.json()['items']
    dates = [user['created_at'] for user in users]
    assert dates == sorted(dates)

def test_sort_descending(client):
    """Should sort results in descending order."""
    response = client.get("/api/users?sort=username&order=desc")
    assert response.status_code == 200

    users = response.json()['items']
    usernames = [user['username'] for user in users]
    assert usernames == sorted(usernames, reverse=True)

def test_invalid_filter_field(client):
    """Should handle invalid filter fields gracefully."""
    response = client.get("/api/users?invalid_field=value")
    assert response.status_code == 400
    assert 'invalid filter' in response.json()['message'].lower()
```

---

## GraphQL Testing Patterns

```typescript
import { describe, test, expect } from 'vitest';
import request from 'supertest';
import { app } from '../src/app';

describe('GraphQL API Tests', () => {
  test('query user by id', async () => {
    const query = `
      query GetUser($id: ID!) {
        user(id: $id) {
          id
          username
          email
          posts {
            id
            title
          }
        }
      }
    `;

    const response = await request(app)
      .post('/graphql')
      .send({
        query,
        variables: { id: '123' },
      })
      .expect(200);

    const { data } = response.body;
    expect(data.user).toBeDefined();
    expect(data.user.id).toBe('123');
    expect(data.user.username).toBeDefined();
    expect(Array.isArray(data.user.posts)).toBe(true);
  });

  test('mutation to create post', async () => {
    const mutation = `
      mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
          id
          title
          content
          author {
            id
            username
          }
        }
      }
    `;

    const response = await request(app)
      .post('/graphql')
      .send({
        query: mutation,
        variables: {
          input: {
            title: 'Test Post',
            content: 'This is a test post',
            authorId: '123',
          },
        },
      })
      .expect(200);

    const { data } = response.body;
    expect(data.createPost).toBeDefined();
    expect(data.createPost.id).toBeDefined();
    expect(data.createPost.title).toBe('Test Post');
    expect(data.createPost.author.id).toBe('123');
  });

  test('query complexity limit', async () => {
    // Deeply nested query that exceeds complexity limit
    const complexQuery = `
      query ComplexQuery {
        users {
          posts {
            comments {
              author {
                posts {
                  comments {
                    author {
                      id
                    }
                  }
                }
              }
            }
          }
        }
      }
    `;

    const response = await request(app)
      .post('/graphql')
      .send({ query: complexQuery })
      .expect(400);

    const { errors } = response.body;
    expect(errors).toBeDefined();
    expect(errors[0].message).toContain('complexity');
  });

  test('schema validation error', async () => {
    const invalidQuery = `
      query GetUser {
        user(id: "123") {
          invalidField
        }
      }
    `;

    const response = await request(app)
      .post('/graphql')
      .send({ query: invalidQuery })
      .expect(400);

    const { errors } = response.body;
    expect(errors).toBeDefined();
    expect(errors[0].message).toContain('Cannot query field "invalidField"');
  });
});
```

---

## Performance Testing

```python
import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_response_time_baseline(client):
    """Should respond within acceptable time limit."""
    start = time.time()
    response = client.get("/api/users")
    duration = time.time() - start

    assert response.status_code == 200
    assert duration < 0.5  # 500ms threshold

def test_concurrent_requests(client):
    """Should handle concurrent requests successfully."""

    def make_request():
        return client.get("/api/users")

    num_requests = 50
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]

        responses = [future.result() for future in as_completed(futures)]

    # All requests should succeed
    assert all(r.status_code == 200 for r in responses)
    success_rate = sum(1 for r in responses if r.status_code == 200) / num_requests
    assert success_rate >= 0.99  # 99% success rate

def test_throughput_under_load(client):
    """Should maintain throughput under sustained load."""

    def make_request():
        start = time.time()
        response = client.get("/api/users")
        duration = time.time() - start
        return response.status_code, duration

    num_requests = 100
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        results = [future.result() for future in as_completed(futures)]

    # Calculate metrics
    success_count = sum(1 for status, _ in results if status == 200)
    avg_duration = sum(duration for _, duration in results) / num_requests

    assert success_count / num_requests >= 0.95  # 95% success rate
    assert avg_duration < 1.0  # Average response time < 1s
```

---

## Testing Tools

### REST APIs
- **Python**: pytest + FastAPI TestClient / Django TestClient / requests
- **TypeScript**: Vitest + supertest / Jest + supertest
- **Others**: Postman, Insomnia, REST-assured (Java)

### Contract Testing
- **Pact**: Python (pact-python), TypeScript (@pact-foundation/pact)
- **Spring Cloud Contract**: Java/Kotlin

### Load Testing
- **k6**: Modern load testing (JavaScript DSL)
- **Apache JMeter**: Traditional load testing
- **Gatling**: Scala-based load testing
- **Artillery**: Node.js load testing

### API Documentation & Testing
- **Swagger/OpenAPI**: Auto-generate tests from specs
- **Postman**: Collection runner for automated tests

---

## Common Pitfalls

### ❌ 1. Testing Implementation Over Contract
**Problem:** Testing internal implementation details instead of API contract
**Solution:** Test from consumer's perspective - input/output only

### ❌ 2. Ignoring HTTP Semantics
**Problem:** Using wrong status codes (200 for errors, 201 for updates)
**Solution:** Follow HTTP standards (201 for creation, 204 for deletion, etc.)

### ❌ 3. Absence of Negative Testing
**Problem:** Only testing happy path scenarios
**Solution:** Test error cases, invalid inputs, edge conditions

### ❌ 4. Brittle Test Suites
**Problem:** Tests break with minor API changes
**Solution:** Use flexible matchers (like, eachLike), test behavior not structure

### ❌ 5. Slow Test Execution
**Problem:** Calling real external services in every test
**Solution:** Use component tests with mocks, save integration tests for critical paths

### ❌ 6. Incomplete Error Testing
**Problem:** Not testing all error scenarios
**Solution:** Test 4xx (client errors) and 5xx (server errors) comprehensively

### ❌ 7. Missing Authentication Tests
**Problem:** Assuming authentication works without testing
**Solution:** Test authentication, authorization, token expiration, etc.

---

## Best Practices

### ✅ 1. Test from Consumer Perspective
Focus on what consumers expect, not how it's implemented internally.

### ✅ 2. Use Schema Validation
Validate responses against OpenAPI/JSON Schema specifications.

### ✅ 3. Test Error Scenarios Thoroughly
Test authentication failures, validation errors, service unavailability.

### ✅ 4. Version API Tests Alongside API
Keep tests in sync with API version changes.

### ✅ 5. Automate in CI/CD Pipelines
Run contract tests on every commit, integration tests before deployment.

### ✅ 6. Use Idempotency Keys
Implement and test idempotency for critical operations.

### ✅ 7. Monitor Production Contracts
Use contract monitoring to detect drift in production.

### ✅ 8. Separate Test Levels
Keep unit, component, integration, and contract tests separate.

---

## Using with QE Agents

### Automated Contract Testing
Agent automatically generates Pact contracts from API specifications.

### Agent-Generated API Test Suites
Generate comprehensive test suites from OpenAPI specs.

### Real-Time API Test Execution
Agents monitor API changes and run relevant tests automatically.

### Contract-Based Integration Testing
Validate microservice contracts before deployment.

### Performance Testing for APIs
Automated load tests triggered by deployment pipeline.

### Security Testing for APIs
Automated OWASP API security testing.

### Continuous Contract Monitoring
Production monitoring to detect contract violations.

---

## Related Skills

- **contract-testing**: Deep dive into consumer-driven contracts
- **integration-testing**: Broader integration testing strategies
- **test-automation-strategy**: Overall test automation approach
- **performance-testing**: Performance and load testing patterns
- **security-testing**: API security testing patterns
- **tdd-london-chicago**: Test-driven development methodologies

---

## References

- Pact Documentation: https://docs.pact.io/
- REST API Design: https://restfulapi.net/
- GraphQL Testing: https://graphql.org/learn/testing/
- Supertest: https://github.com/ladjs/supertest
- FastAPI Testing: https://fastapi.tiangolo.com/tutorial/testing/
- HTTP Status Codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

---

**Version:** 1.0.0 (Adapted for Python + TypeScript)
**Source:** github.com/proffesor-for-testing/agentic-qe
**Category:** API Testing

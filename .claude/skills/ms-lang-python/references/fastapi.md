# FastAPI Production Patterns

## Contents

- Dependency injection (database session, authentication)
- Exception handling (custom handlers, HTTP exceptions)
- Middleware (CORS, request logging)
- Background tasks
- Testing endpoints with TestClient

## Dependency injection

Reusable dependencies for shared logic — testable (mock the dependency), type-safe (`Annotated`):

```python
from fastapi import Depends, FastAPI, Header, HTTPException
from typing import Annotated, Generator
from sqlalchemy.orm import Session

app = FastAPI()

# Database session dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication dependency
def get_current_user(
    token: str = Header(...),
    db: Session = Depends(get_db)
) -> User:
    user = verify_token(token, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return user

# Inject dependencies into route
@app.get("/users/me")
async def read_users_me(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user
```

## Exception handling

Custom exception handlers keep routes clean:

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse

class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id

@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": f"User {exc.user_id} not found"}
    )

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if user is None:
        raise UserNotFoundError(user_id)
    return user
```

Direct HTTP exceptions for simple cases:

```python
from fastapi import HTTPException

@app.post("/users/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    return create_user_in_db(user, db)
```

## Middleware

CORS — specific origins, never `"*"` with credentials:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

Request logging with timing and request id (see `structlog.md` for logger setup):

```python
import time
import uuid
import structlog

log = structlog.get_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    log.info("request_start", method=request.method,
             path=request.url.path, request_id=request_id)

    response = await call_next(request)

    log.info("request_end", method=request.method, path=request.url.path,
             status_code=response.status_code,
             duration_ms=round((time.time() - start_time) * 1000, 2),
             request_id=request_id)
    return response
```

## Background tasks

Run work after the response returns (email, stats updates):

```python
from fastapi import BackgroundTasks

@app.post("/users/")
async def create_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()

    background_tasks.add_task(send_welcome_email, user.email)
    return {"message": "User created, email will be sent"}
```

Tasks can take dependencies as plain arguments:

```python
def update_user_stats(user_id: int, db: Session):
    user = db.query(User).get(user_id)
    user.last_login = datetime.utcnow()
    db.commit()

@app.post("/login")
async def login(
    credentials: LoginCredentials,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = authenticate(credentials, db)
    background_tasks.add_task(update_user_stats, user.id, db)
    return {"token": create_token(user)}
```

## Testing endpoints

```python
from fastapi.testclient import TestClient
import pytest

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "secret123"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_get_user_unauthorized():
    response = client.get("/users/me")
    assert response.status_code == 401

@pytest.fixture
def authenticated_client():
    token = create_test_token()
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

def test_get_user_authenticated(authenticated_client):
    response = authenticated_client.get("/users/me")
    assert response.status_code == 200
```

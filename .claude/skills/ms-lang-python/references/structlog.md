# Structured Logging with structlog

structlog over stdlib logging: JSON output for log aggregation, context binding
(request_id/user_id attached to every log line), no string formatting until output.

## Contents

- Configuration (dev and production)
- Basic usage and context binding
- FastAPI integration

## Configuration

```python
import logging
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer()  # Pretty print in dev
        # Use structlog.processors.JSONRenderer() in production
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()
```

Production: swap `ConsoleRenderer()` for `JSONRenderer()` so log aggregation
(ELK, Datadog) gets machine-parseable events:

```python
log.info("user_login", user_id=42)
# {"event":"user_login","user_id":42,"timestamp":"...","level":"info"}
```

## Basic usage and context binding

Log events as key-value pairs, never interpolated strings:

```python
log.info("user_login", user_id=42, email="user@example.com")
log.error("database_error", error=str(e), query="SELECT * FROM users")
```

Bind context once; all subsequent logs on that logger include it:

```python
log = log.bind(request_id="abc123", user_id=42)

log.info("processing_payment", amount=100)      # includes request_id, user_id
log.warning("payment_failed", reason="insufficient_funds")  # same
```

## FastAPI integration

Bind per-request context in middleware, expose the bound logger via `request.state`:

```python
from fastapi import Request
import uuid

@app.middleware("http")
async def add_structured_logging(request: Request, call_next):
    log = structlog.get_logger().bind(
        request_id=str(uuid.uuid4()),
        method=request.method,
        path=request.url.path,
    )
    request.state.log = log
    log.info("request_start")

    try:
        response = await call_next(request)
        log.info("request_end", status_code=response.status_code)
        return response
    except Exception as e:
        log.error("request_error", error=str(e), exc_info=True)
        raise

# Access in routes
@app.get("/users/{user_id}")
async def get_user(user_id: int, request: Request):
    log = request.state.log.bind(user_id=user_id)
    log.info("fetching_user")
    # ...
```

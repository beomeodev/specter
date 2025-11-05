# Cross-Cutting Concerns - Code Examples

Detailed implementation examples for error handling, logging, and configuration patterns in Python and TypeScript.

---

## Example 1: Python Custom Linter (AST-based)

```python
import ast
from pathlib import Path
from typing import List, Dict

class ErrorHandlingLinter(ast.NodeVisitor):
    """Detects non-compliant error handling patterns."""

    def __init__(self):
        self.violations: List[Dict[str, any]] = []

    def visit_Raise(self, node: ast.Raise) -> None:
        # Check for bare Exception usage
        if isinstance(node.exc, ast.Call):
            if isinstance(node.exc.func, ast.Name):
                if node.exc.func.id == "Exception":
                    self.violations.append({
                        "line": node.lineno,
                        "type": "bare_exception",
                        "message": "Use specific exception types instead of bare Exception"
                    })
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        # Check for bare except clauses
        if node.type is None:
            self.violations.append({
                "line": node.lineno,
                "type": "bare_except",
                "message": "Avoid bare except: specify exception type"
            })
        self.generic_visit(node)

def lint_file(file_path: Path) -> List[Dict[str, any]]:
    """Run linter on a Python file."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    linter = ErrorHandlingLinter()
    linter.visit(tree)
    return linter.violations
```

---

## Example 2: TypeScript ESLint Custom Rule

```typescript
// eslint-plugin-custom-rules/no-bare-error.ts
import { ESLintUtils } from '@typescript-eslint/utils';

export const noBareError = ESLintUtils.RuleCreator(
  (name) => `https://your-docs.com/rules/${name}`
)({
  name: 'no-bare-error',
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow throwing bare Error instances',
      recommended: 'error',
    },
    messages: {
      bareError: 'Use specific error classes instead of bare Error',
    },
    schema: [],
  },
  defaultOptions: [],
  create(context) {
    return {
      ThrowStatement(node) {
        if (
          node.argument?.type === 'NewExpression' &&
          node.argument.callee.type === 'Identifier' &&
          node.argument.callee.name === 'Error'
        ) {
          context.report({
            node,
            messageId: 'bareError',
          });
        }
      },
    };
  },
});
```

---

## Example 3: ROI Calculation Script

```python
from dataclasses import dataclass
from enum import Enum
from typing import List

class ImpactLevel(Enum):
    HIGH = 10    # User-facing, public APIs
    MEDIUM = 5   # Internal services
    LOW = 1      # Test utilities, deprecated

@dataclass
class File:
    path: str
    impact: ImpactLevel
    error_sites: int
    time_hours: float

def calculate_roi(file: File, project_horizon_months: int = 12) -> float:
    """
    Calculate ROI for standardizing a file.

    ROI = (Value Gain × Project Horizon) / Time Investment
    """
    value_gain = file.impact.value * file.error_sites
    project_horizon = project_horizon_months
    time_investment = file.time_hours

    return (value_gain * project_horizon) / time_investment

def prioritize_files(files: List[File]) -> List[File]:
    """Sort files by ROI descending."""
    return sorted(files, key=lambda f: calculate_roi(f), reverse=True)

# Example usage
files = [
    File("api/auth.py", ImpactLevel.HIGH, 15, 2.0),      # ROI = 90
    File("utils/helper.py", ImpactLevel.MEDIUM, 8, 1.0), # ROI = 48
    File("tests/mock.py", ImpactLevel.LOW, 5, 0.5),      # ROI = 12
]

prioritized = prioritize_files(files)
for f in prioritized:
    print(f"{f.path}: ROI = {calculate_roi(f):.1f}x")
```

---

## Example 4: Python Error Infrastructure

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

class ErrorType(Enum):
    """Standardized error categories."""
    VALIDATION = "validation_error"
    AUTHENTICATION = "authentication_error"
    AUTHORIZATION = "authorization_error"
    NOT_FOUND = "not_found_error"
    CONFLICT = "conflict_error"
    INTERNAL = "internal_error"

@dataclass
class ErrorContext:
    """Rich error context for diagnosis."""
    operation: str
    resource: str
    resource_id: Optional[str]
    error_type: ErrorType
    guidance: str
    metadata: Optional[Dict[str, Any]] = None

class ApplicationError(Exception):
    """Base sentinel error with rich context."""

    def __init__(self, context: ErrorContext, original_error: Optional[Exception] = None):
        self.context = context
        self.original_error = original_error

        message = self._format_message()
        super().__init__(message)

    def _format_message(self) -> str:
        """Format error with context."""
        msg = (
            f"[{self.context.error_type.value}] "
            f"Operation: {self.context.operation} | "
            f"Resource: {self.context.resource}"
        )

        if self.context.resource_id:
            msg += f" (ID: {self.context.resource_id})"

        msg += f" | Guidance: {self.context.guidance}"

        if self.original_error:
            msg += f" | Caused by: {str(self.original_error)}"

        return msg

    def to_dict(self) -> Dict[str, Any]:
        """Convert to structured format for logging."""
        return {
            "error_type": self.context.error_type.value,
            "operation": self.context.operation,
            "resource": self.context.resource,
            "resource_id": self.context.resource_id,
            "guidance": self.context.guidance,
            "metadata": self.context.metadata,
            "original_error": str(self.original_error) if self.original_error else None,
        }

# Specific error types
class ValidationError(ApplicationError):
    """Validation-related errors."""
    pass

class AuthenticationError(ApplicationError):
    """Authentication-related errors."""
    pass

class NotFoundError(ApplicationError):
    """Resource not found errors."""
    pass

# Usage example
def get_user(user_id: str) -> dict:
    """Retrieve user with rich error handling."""
    try:
        # Database lookup
        user = db.find_user(user_id)
        if not user:
            raise NotFoundError(
                context=ErrorContext(
                    operation="get_user",
                    resource="user",
                    resource_id=user_id,
                    error_type=ErrorType.NOT_FOUND,
                    guidance="Verify user ID exists in the system"
                )
            )
        return user
    except DatabaseError as e:
        raise ApplicationError(
            context=ErrorContext(
                operation="get_user",
                resource="user",
                resource_id=user_id,
                error_type=ErrorType.INTERNAL,
                guidance="Check database connectivity and retry"
            ),
            original_error=e
        )
```

---

## Example 5: TypeScript Error Infrastructure

```typescript
// errors/ApplicationError.ts

export enum ErrorType {
  VALIDATION = 'validation_error',
  AUTHENTICATION = 'authentication_error',
  AUTHORIZATION = 'authorization_error',
  NOT_FOUND = 'not_found_error',
  CONFLICT = 'conflict_error',
  INTERNAL = 'internal_error',
}

export interface ErrorContext {
  operation: string;
  resource: string;
  resourceId?: string;
  errorType: ErrorType;
  guidance: string;
  metadata?: Record<string, any>;
}

export class ApplicationError extends Error {
  public readonly context: ErrorContext;
  public readonly originalError?: Error;

  constructor(context: ErrorContext, originalError?: Error) {
    const message = ApplicationError.formatMessage(context, originalError);
    super(message);

    this.name = 'ApplicationError';
    this.context = context;
    this.originalError = originalError;

    // Maintain proper stack trace
    Error.captureStackTrace(this, this.constructor);
  }

  private static formatMessage(context: ErrorContext, originalError?: Error): string {
    let msg = `[${context.errorType}] `;
    msg += `Operation: ${context.operation} | `;
    msg += `Resource: ${context.resource}`;

    if (context.resourceId) {
      msg += ` (ID: ${context.resourceId})`;
    }

    msg += ` | Guidance: ${context.guidance}`;

    if (originalError) {
      msg += ` | Caused by: ${originalError.message}`;
    }

    return msg;
  }

  public toJSON(): Record<string, any> {
    return {
      errorType: this.context.errorType,
      operation: this.context.operation,
      resource: this.context.resource,
      resourceId: this.context.resourceId,
      guidance: this.context.guidance,
      metadata: this.context.metadata,
      originalError: this.originalError?.message,
      stack: this.stack,
    };
  }
}

// Specific error types
export class ValidationError extends ApplicationError {
  constructor(context: Omit<ErrorContext, 'errorType'>, originalError?: Error) {
    super({ ...context, errorType: ErrorType.VALIDATION }, originalError);
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends ApplicationError {
  constructor(context: Omit<ErrorContext, 'errorType'>, originalError?: Error) {
    super({ ...context, errorType: ErrorType.NOT_FOUND }, originalError);
    this.name = 'NotFoundError';
  }
}

// Usage example
async function getUser(userId: string): Promise<User> {
  try {
    const user = await db.findUser(userId);

    if (!user) {
      throw new NotFoundError({
        operation: 'getUser',
        resource: 'user',
        resourceId: userId,
        guidance: 'Verify user ID exists in the system',
      });
    }

    return user;
  } catch (error) {
    if (error instanceof ApplicationError) {
      throw error; // Re-throw application errors
    }

    // Wrap unexpected errors
    throw new ApplicationError(
      {
        operation: 'getUser',
        resource: 'user',
        resourceId: userId,
        errorType: ErrorType.INTERNAL,
        guidance: 'Check database connectivity and retry',
      },
      error as Error
    );
  }
}
```

---

## Example 6: Python Error with Full Context

```python
import logging
from datetime import datetime
from typing import Optional

# Configure structured logging
import json
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def process_payment(user_id: str, amount: float, payment_method: str) -> dict:
    """Process payment with comprehensive error context."""
    try:
        # Validate payment method
        if payment_method not in ["credit_card", "paypal", "bank_transfer"]:
            raise ValidationError(
                context=ErrorContext(
                    operation="process_payment",
                    resource="payment",
                    resource_id=None,
                    error_type=ErrorType.VALIDATION,
                    guidance="Use valid payment method: credit_card, paypal, or bank_transfer",
                    metadata={
                        "user_id": user_id,
                        "amount": amount,
                        "invalid_method": payment_method,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            )

        # Process payment
        result = payment_gateway.charge(user_id, amount, payment_method)

        logger.info(
            "Payment processed successfully",
            extra={
                "user_id": user_id,
                "amount": amount,
                "payment_method": payment_method,
                "transaction_id": result.transaction_id,
            }
        )

        return result

    except ValidationError:
        raise  # Re-raise with context intact
    except PaymentGatewayError as e:
        # Enrich external error with context
        raise ApplicationError(
            context=ErrorContext(
                operation="process_payment",
                resource="payment",
                resource_id=None,
                error_type=ErrorType.INTERNAL,
                guidance="Verify payment gateway status and retry. Contact support if persists.",
                metadata={
                    "user_id": user_id,
                    "amount": amount,
                    "payment_method": payment_method,
                    "gateway_error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            original_error=e
        )
```

---

## Example 7: Python Error Handling Patterns

```python
# ✅ GOOD: Sentinel error with context
class ResourceNotFoundError(ApplicationError):
    """Raised when a requested resource doesn't exist."""
    pass

def get_resource(resource_id: str) -> Resource:
    try:
        resource = db.query(resource_id)
        if not resource:
            raise ResourceNotFoundError(
                context=ErrorContext(
                    operation="get_resource",
                    resource="resource",
                    resource_id=resource_id,
                    error_type=ErrorType.NOT_FOUND,
                    guidance="Check resource ID is correct"
                )
            )
        return resource
    except DatabaseError as e:
        raise ApplicationError(
            context=ErrorContext(
                operation="get_resource",
                resource="resource",
                resource_id=resource_id,
                error_type=ErrorType.INTERNAL,
                guidance="Check database connection"
            ),
            original_error=e
        ) from e  # Preserve error chain

# ❌ BAD: Bare exception, no context
def get_resource_bad(resource_id: str) -> Resource:
    try:
        return db.query(resource_id)
    except:  # Bare except!
        raise Exception("Error getting resource")  # No context!
```

---

## Example 8: TypeScript Error Handling Patterns

```typescript
// ✅ GOOD: Sentinel error with context
class ResourceNotFoundError extends ApplicationError {
  constructor(resourceId: string, originalError?: Error) {
    super(
      {
        operation: 'getResource',
        resource: 'resource',
        resourceId,
        errorType: ErrorType.NOT_FOUND,
        guidance: 'Check resource ID is correct',
      },
      originalError
    );
    this.name = 'ResourceNotFoundError';
  }
}

async function getResource(resourceId: string): Promise<Resource> {
  try {
    const resource = await db.query(resourceId);

    if (!resource) {
      throw new ResourceNotFoundError(resourceId);
    }

    return resource;
  } catch (error) {
    if (error instanceof ResourceNotFoundError) {
      throw error;
    }

    // Wrap unexpected errors with context
    throw new ApplicationError(
      {
        operation: 'getResource',
        resource: 'resource',
        resourceId,
        errorType: ErrorType.INTERNAL,
        guidance: 'Check database connection',
      },
      error as Error
    );
  }
}

// ❌ BAD: Bare error, no context
async function getResourceBad(resourceId: string): Promise<Resource> {
  try {
    return await db.query(resourceId);
  } catch (e) {  // Untyped catch
    throw new Error('Error getting resource');  // No context!
  }
}
```

---

## Example 9: Python Structured Logging (structlog)

```python
import structlog
from typing import Optional
import uuid

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def process_order(order_id: str, user_id: str, correlation_id: Optional[str] = None) -> dict:
    """Process order with structured logging."""

    # Generate correlation ID if not provided
    correlation_id = correlation_id or str(uuid.uuid4())

    # Bind context to logger
    log = logger.bind(
        operation="process_order",
        order_id=order_id,
        user_id=user_id,
        correlation_id=correlation_id
    )

    log.info("Processing order started")

    try:
        # Validate order
        order = validate_order(order_id)
        log.debug("Order validated", order_status=order.status)

        # Process payment
        payment = process_payment(order.total, user_id)
        log.info(
            "Payment processed",
            amount=order.total,
            payment_method=payment.method,
            transaction_id=payment.transaction_id
        )

        # Update inventory
        update_inventory(order.items)
        log.info("Inventory updated", item_count=len(order.items))

        log.info(
            "Order processed successfully",
            order_status="completed",
            total_amount=order.total
        )

        return {"status": "success", "order_id": order_id}

    except ValidationError as e:
        log.warning(
            "Order validation failed",
            error=e.to_dict(),
            order_status="validation_failed"
        )
        raise

    except PaymentError as e:
        log.error(
            "Payment processing failed",
            error=e.to_dict(),
            order_status="payment_failed"
        )
        raise

    except Exception as e:
        log.error(
            "Unexpected error processing order",
            error=str(e),
            error_type=type(e).__name__,
            order_status="error"
        )
        raise

# ❌ BAD: Unstructured logging
def process_order_bad(order_id: str) -> dict:
    print(f"Processing order {order_id}")  # print() instead of logger!

    try:
        order = validate_order(order_id)
        print("Order is valid")  # No context!
        return {"status": "success"}
    except Exception as e:
        print(f"Error: {e}")  # No structure, no error details!
        raise
```

---

## Example 10: TypeScript Structured Logging (winston)

```typescript
import winston from 'winston';
import { v4 as uuidv4 } from 'uuid';

// Configure structured logging
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DDTHH:mm:ss.SSSZ' }),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.json()
      ),
    }),
  ],
});

// Create contextual logger
function createLogger(context: Record<string, any>) {
  return logger.child(context);
}

async function processOrder(
  orderId: string,
  userId: string,
  correlationId?: string
): Promise<{ status: string; orderId: string }> {
  // Generate correlation ID if not provided
  correlationId = correlationId || uuidv4();

  // Create contextual logger
  const log = createLogger({
    operation: 'processOrder',
    orderId,
    userId,
    correlationId,
  });

  log.info('Processing order started');

  try {
    // Validate order
    const order = await validateOrder(orderId);
    log.debug('Order validated', { orderStatus: order.status });

    // Process payment
    const payment = await processPayment(order.total, userId);
    log.info('Payment processed', {
      amount: order.total,
      paymentMethod: payment.method,
      transactionId: payment.transactionId,
    });

    // Update inventory
    await updateInventory(order.items);
    log.info('Inventory updated', { itemCount: order.items.length });

    log.info('Order processed successfully', {
      orderStatus: 'completed',
      totalAmount: order.total,
    });

    return { status: 'success', orderId };
  } catch (error) {
    if (error instanceof ValidationError) {
      log.warn('Order validation failed', {
        error: error.toJSON(),
        orderStatus: 'validation_failed',
      });
      throw error;
    }

    if (error instanceof PaymentError) {
      log.error('Payment processing failed', {
        error: error.toJSON(),
        orderStatus: 'payment_failed',
      });
      throw error;
    }

    // Unexpected error
    log.error('Unexpected error processing order', {
      error: error instanceof Error ? error.message : String(error),
      errorType: error instanceof Error ? error.name : 'Unknown',
      orderStatus: 'error',
      stack: error instanceof Error ? error.stack : undefined,
    });

    throw error;
  }
}

// ❌ BAD: Unstructured logging
async function processOrderBad(orderId: string): Promise<any> {
  console.log(`Processing order ${orderId}`);  // console.log!

  try {
    const order = await validateOrder(orderId);
    console.log('Order is valid');  // No context!
    return { status: 'success' };
  } catch (e) {
    console.log(`Error: ${e}`);  // No structure!
    throw e;
  }
}
```

---

## Example 11: Python Configuration with Pydantic

```python
from pydantic import BaseSettings, Field, validator
from typing import Optional
import structlog

logger = structlog.get_logger()

class DatabaseConfig(BaseSettings):
    """Database configuration with validation."""

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port")
    name: str = Field(..., description="Database name")  # Required field
    user: str = Field(..., description="Database user")
    password: str = Field(..., description="Database password")
    pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")

    @validator('port')
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError('Port must be between 1 and 65535')
        return v

    class Config:
        env_prefix = 'DB_'  # Environment variables: DB_HOST, DB_PORT, etc.
        case_sensitive = False

class AppConfig(BaseSettings):
    """Application configuration with validation."""

    env: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    api_key: str = Field(..., description="API key for external service")
    max_request_size: int = Field(default=1024*1024, ge=1, description="Max request size in bytes")

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    @validator('env')
    def validate_env(cls, v):
        allowed_envs = ['development', 'staging', 'production']
        if v not in allowed_envs:
            raise ValueError(f'Environment must be one of: {allowed_envs}')
        return v

    @validator('log_level')
    def validate_log_level(cls, v):
        allowed_levels = ['DEBUG', 'INFO', 'WARN', 'ERROR']
        if v.upper() not in allowed_levels:
            raise ValueError(f'Log level must be one of: {allowed_levels}')
        return v.upper()

    def log_config(self) -> None:
        """Log configuration on startup (sanitize secrets)."""
        safe_config = self.dict()

        # Sanitize secrets
        if 'api_key' in safe_config:
            safe_config['api_key'] = '***REDACTED***'
        if 'database' in safe_config and 'password' in safe_config['database']:
            safe_config['database']['password'] = '***REDACTED***'

        logger.info("Application configuration loaded", config=safe_config)

    class Config:
        env_prefix = 'APP_'
        case_sensitive = False

# Load and validate configuration
try:
    config = AppConfig()
    config.log_config()
except Exception as e:
    logger.error("Configuration validation failed", error=str(e))
    raise

# Usage
db_connection = connect_to_database(
    host=config.database.host,
    port=config.database.port,
    name=config.database.name,
    user=config.database.user,
    password=config.database.password
)

# ❌ BAD: Direct environment access everywhere
import os

def connect_bad():
    host = os.environ.get('DB_HOST', 'localhost')  # No validation!
    port = int(os.environ.get('DB_PORT', '5432'))  # Can crash!
    return connect(host, port)
```

---

## Example 12: TypeScript Configuration with Zod

```typescript
import { z } from 'zod';
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [new winston.transports.Console()],
});

// Define configuration schema with Zod
const DatabaseConfigSchema = z.object({
  host: z.string().default('localhost').describe('Database host'),
  port: z.number().int().min(1).max(65535).default(5432).describe('Database port'),
  name: z.string().min(1).describe('Database name'),
  user: z.string().min(1).describe('Database user'),
  password: z.string().min(1).describe('Database password'),
  poolSize: z.number().int().min(1).max(100).default(10).describe('Connection pool size'),
});

const AppConfigSchema = z.object({
  env: z.enum(['development', 'staging', 'production']).default('development'),
  debug: z.boolean().default(false),
  logLevel: z.enum(['DEBUG', 'INFO', 'WARN', 'ERROR']).default('INFO'),
  apiKey: z.string().min(1).describe('API key for external service'),
  maxRequestSize: z.number().int().min(1).default(1024 * 1024),
  database: DatabaseConfigSchema,
});

type AppConfig = z.infer<typeof AppConfigSchema>;

function loadConfig(): AppConfig {
  const rawConfig = {
    env: process.env.APP_ENV,
    debug: process.env.APP_DEBUG === 'true',
    logLevel: process.env.APP_LOG_LEVEL,
    apiKey: process.env.APP_API_KEY,
    maxRequestSize: process.env.APP_MAX_REQUEST_SIZE
      ? parseInt(process.env.APP_MAX_REQUEST_SIZE, 10)
      : undefined,
    database: {
      host: process.env.DB_HOST,
      port: process.env.DB_PORT ? parseInt(process.env.DB_PORT, 10) : undefined,
      name: process.env.DB_NAME,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      poolSize: process.env.DB_POOL_SIZE
        ? parseInt(process.env.DB_POOL_SIZE, 10)
        : undefined,
    },
  };

  try {
    const config = AppConfigSchema.parse(rawConfig);
    logConfig(config);
    return config;
  } catch (error) {
    if (error instanceof z.ZodError) {
      logger.error('Configuration validation failed', {
        errors: error.errors.map((e) => ({
          path: e.path.join('.'),
          message: e.message,
        })),
      });
    }
    throw new Error('Invalid configuration');
  }
}

function logConfig(config: AppConfig): void {
  const safeConfig = {
    ...config,
    apiKey: '***REDACTED***',
    database: {
      ...config.database,
      password: '***REDACTED***',
    },
  };

  logger.info('Application configuration loaded', { config: safeConfig });
}

// Load and validate configuration
const config = loadConfig();

// Usage
const dbConnection = connectToDatabase({
  host: config.database.host,
  port: config.database.port,
  database: config.database.name,
  user: config.database.user,
  password: config.database.password,
});

// ❌ BAD: Direct environment access without validation
function connectBad() {
  const host = process.env.DB_HOST || 'localhost';  // No validation!
  const port = parseInt(process.env.DB_PORT || '5432', 10);  // Can be NaN!
  return connect(host, port);
}
```

---

## Example 13: Python Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: custom-error-linter
        name: Custom Error Handling Linter
        entry: python scripts/lint_errors.py
        language: python
        types: [python]
        pass_filenames: true

      - id: logging-checker
        name: Structured Logging Checker
        entry: python scripts/lint_logging.py
        language: python
        types: [python]
        pass_filenames: true
```

---

## Example 14: GitHub Actions CI Integration

```yaml
# .github/workflows/quality-gates.yml
name: Quality Gates

on: [push, pull_request]

jobs:
  lint-cross-cutting:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt

      - name: Run custom error handling linter
        run: python scripts/lint_errors.py --strict

      - name: Run logging compliance checker
        run: python scripts/lint_logging.py --strict

      - name: Generate compliance report
        if: always()
        run: python scripts/generate_compliance_report.py
```

---

**For main concepts and workflow, see `SKILL.md`.**

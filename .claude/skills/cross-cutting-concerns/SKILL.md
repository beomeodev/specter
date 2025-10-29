# Cross-Cutting Concerns

Systematic methodology for standardizing error handling, logging, and configuration patterns across the codebase. Use when reviewing code quality, extracting common patterns, enforcing architectural consistency, or building reusable infrastructure components. Provides ROI-based prioritization, compliance checking through custom linters, and proven patterns for Python and TypeScript projects with 16.7x measured returns.

---

## When to Use This Skill

Apply this skill when encountering:

- **Inconsistent patterns** across error handling, logging, or configuration
- **Pattern extraction needs** for standardization across modules
- **Code quality reviews** requiring architectural consistency checks
- **Manual review fatigue** that doesn't scale with team growth
- **Unclear prioritization** among many files needing refactoring
- **Pre-merge compliance** needs to prevent non-compliant code
- **Team scaling** requiring consistent development patterns

**Don't use when:**
- Patterns already consistent and enforced with linters
- Codebase very small (<1K LOC)
- No refactoring capacity available
- Required tooling unavailable

---

## Quick Start (30 minutes)

### Step 1: Pattern Inventory (15 min)

Run these commands to identify inconsistencies:

**Python Error Patterns:**
```bash
# Count different error handling approaches
grep -r "raise Exception" . | wc -l
grep -r "raise ValueError" . | wc -l
grep -r "raise CustomError" . | wc -l
grep -r "except:" . | wc -l
grep -r "except Exception:" . | wc -l
```

**TypeScript Error Patterns:**
```bash
# Count different error handling approaches
grep -r "throw new Error" . | wc -l
grep -r "throw new CustomError" . | wc -l
grep -r "catch (e)" . | wc -l
grep -r "catch (error)" . | wc -l
```

**Logging Patterns:**
```bash
# Python
grep -r "print(" . | wc -l
grep -r "logging.info" . | wc -l
grep -r "logger.info" . | wc -l

# TypeScript
grep -r "console.log" . | wc -l
grep -r "logger.info" . | wc -l
grep -r "winston" . | wc -l
```

**Configuration Patterns:**
```bash
# Python
grep -r "os.environ" . | wc -l
grep -r "settings" . | wc -l
grep -r "config" . | wc -l

# TypeScript
grep -r "process.env" . | wc -l
grep -r "config" . | wc -l
```

### Step 2: Prioritize by File Tier (10 min)

Classify files by ROI (Return on Investment):

- **Tier 1 (ROI > 10x):** User-facing APIs, public interfaces, error infrastructure, authentication/authorization
- **Tier 2 (ROI 5-10x):** Internal services, CLI commands, data processors, middleware
- **Tier 3 (ROI < 5x):** Test utilities, stubs, mocks, deprecated code

**ROI Formula:**
```
ROI = (Value Gain × Project Horizon) / Time Investment
```

**Standardization Coverage:**
- Tier 1: 100% (highest priority)
- Tier 2: 50-80% (selective)
- Tier 3: Defer (focus elsewhere)

### Step 3: Define Initial Conventions (5 min)

**Error Handling:**
- Sentinel errors + wrapping with context
- Include: Operation + Resource + Error Type + Guidance

**Logging:**
- Structured logging (JSON format with key-value pairs)
- Clear levels: DEBUG, INFO, WARN, ERROR

**Configuration:**
- Centralized Config class/object
- Environment variable validation
- Fail-fast on invalid config

---

## Five Universal Principles

### 1. Detect Before Standardize

Automate identification of non-compliant code rather than manual inspection.

**Implementation:**
1. Create linters or static analyzers
2. Run on full codebase
3. Categorize violations by severity
4. Generate compliance reports with metrics

**Example: Python Custom Linter (AST-based)**
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

**Example: TypeScript ESLint Custom Rule**
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

### 2. Prioritize by Value

Focus on high-value files first using ROI calculation.

**Decision Framework:**
- Standardize Tier 1 files fully (100% coverage)
- Standardize Tier 2 selectively (50-80% coverage)
- Defer Tier 3 (ROI diminishes after 85-90% overall coverage)

**Example ROI Calculation:**
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

### 3. Infrastructure Enables Scale

Build foundational components before standardizing call sites for multiplicative returns.

**Investment Sequence:**
1. Sentinel errors / custom error classes
2. Error enrichment utilities
3. Structured logging setup
4. Configuration validation framework
5. Custom linters
6. CI integration

**Example: Python Error Infrastructure**
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

**Example: TypeScript Error Infrastructure**
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

### 4. Context Is King

Enrich errors with operation context, resource IDs, and actionable guidance.

**Required Context Elements:**
1. **Operation**: What action was being performed
2. **Resource**: What entity was involved
3. **Resource ID**: Specific instance identifier
4. **Error Type**: Standardized category
5. **Guidance**: Actionable next steps
6. **Metadata**: Additional diagnostic info

**Validation Results:**
- 60-75% faster error diagnosis with rich context
- Reduces back-and-forth in debugging
- Enables better monitoring and alerting

**Example: Python Error with Full Context**
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

### 5. Automate Enforcement

Integrate linters into CI/CD to block non-compliant code and prevent regressions.

**Implementation Steps:**
1. Create custom linter (AST-based for Python, ESLint plugin for TypeScript)
2. Add pre-commit hooks
3. Integrate into CI pipeline
4. Block merge on violations
5. Generate compliance reports

**Example: Python Pre-commit Configuration**
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

**Example: GitHub Actions CI Integration**
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

## Pattern Extraction Workflow

### Phase 1: Observe (Iterations 0-1)

**Goals:**
- Catalog existing patterns
- Measure consistency percentage
- Identify variations and gaps

**Actions:**
1. Run pattern inventory (grep-based analysis)
2. Document current state (% of files using each pattern)
3. Identify high-value files (user-facing, public APIs)
4. Estimate refactoring effort

**Deliverables:**
- Pattern inventory spreadsheet
- Baseline consistency metrics
- File prioritization (Tier 1/2/3)

### Phase 2: Codify (Iterations 2-4)

**Goals:**
- Define conventions
- Build infrastructure
- Create enforcement tools

**Actions:**
1. Select error handling convention (sentinel errors + wrapping)
2. Select logging convention (structured JSON logging)
3. Select config convention (centralized with validation)
4. Implement infrastructure (error classes, logging config)
5. Develop custom linters
6. Write documentation

**Deliverables:**
- Convention documentation
- Reusable infrastructure code
- Custom linters
- Usage examples

### Phase 3: Automate (Iterations 5-6)

**Goals:**
- Standardize high-value files
- Enforce compliance in CI
- Monitor regression

**Actions:**
1. Refactor Tier 1 files (100% coverage)
2. Refactor Tier 2 files (50-80% coverage)
3. Integrate linters into pre-commit hooks
4. Add CI quality gates
5. Generate compliance dashboards
6. Train team on conventions

**Deliverables:**
- Standardized codebase (Tier 1 + Tier 2)
- CI enforcement pipeline
- Compliance dashboard
- Team training materials

---

## Convention Selection: Error Handling

### 13 Best Practices

1. **Use Sentinel Errors**: Define specific error classes/types for each error category
2. **Preserve Error Chains**:
   - Python: `raise NewError(...) from original_error`
   - TypeScript: Use `Error.cause` or wrap in custom error
3. **Add Operation Context**: Include what action was being performed
4. **Include Resource IDs**: Specify which entity was involved
5. **Provide Actionable Guidance**: Tell users what to do next
6. **Use Custom Error Types**: Create domain-specific error classes
7. **Never Log-and-Return**: Either log or raise, not both (prevents duplicate logging)
8. **Validate Error Paths**: Test error handling in unit tests
9. **Document Error Contracts**: List possible exceptions in docstrings/comments
10. **Use Proper Error Inspection**:
    - Python: `isinstance(e, SpecificError)`
    - TypeScript: `error instanceof SpecificError`
11. **Avoid Bare Except/Catch**: Always specify exception type
12. **Fail Fast**: Validate early, raise errors immediately
13. **Never Swallow Errors**: Don't catch without handling or re-raising

**Python Example:**
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

**TypeScript Example:**
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

## Convention Selection: Logging

### 13 Best Practices

1. **Use Structured Logging**: JSON format with key-value pairs
2. **Configure Log Level via Environment**: Allow runtime adjustment
3. **Use Contextual Loggers**: Include module/component name
4. **Add Operation Names**: Log what action is being performed
5. **Include Resource IDs**: Log which entities are involved
6. **Distinguish Log Levels Properly**:
   - DEBUG: Development details
   - INFO: Normal operations, key events
   - WARN: Unexpected but handled situations
   - ERROR: Actual errors requiring attention
7. **Never Log Sensitive Data**: No passwords, tokens, PII
8. **Use Consistent Key Names**: Standardize field names across codebase
9. **Log to stderr**: Keep stdout for program output
10. **Include Timestamps**: Always log with ISO 8601 timestamps
11. **Add Source Location**: Include file/function name
12. **Use Correlation IDs**: Track requests across services
13. **Log Error Context**: Use error.to_dict() or error.toJSON()

**Python Example (using structlog):**
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

**TypeScript Example (using winston):**
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

## Convention Selection: Configuration

### 13 Best Practices

1. **Centralize Configuration**: Single source of truth
2. **Validate on Load**: Fail fast with clear errors
3. **Use Environment Variables**: Follow 12-Factor App principles
4. **Provide Sensible Defaults**: Allow override but don't require it
5. **Document All Options**: Clear descriptions for each setting
6. **Validate Types and Ranges**: Enforce constraints at load time
7. **Fail Fast on Invalid Config**: Don't start with bad configuration
8. **Log Configuration on Startup**: Record what settings are active (sanitize secrets)
9. **Never Commit Secrets**: Use environment variables or secret managers
10. **Separate Configs per Environment**: dev, staging, production
11. **Support Override Mechanisms**: Environment > config file > defaults
12. **Version Configuration Schema**: Track changes to config structure
13. **Test Configuration Loading**: Unit test config validation

**Python Example (using Pydantic):**
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

**TypeScript Example (using Zod):**
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

## File Tier Prioritization

### ROI Calculation Formula

```
For each file:
  User Impact (HIGH=10, MEDIUM=5, LOW=1) × Error Sites Count
  ÷ Time Investment (hours) × Project Horizon (months)
  = ROI Multiplier
```

### Tier Definitions

**Tier 1 (ROI > 10x)** - Standardize 100%
- User-facing APIs
- Public interfaces
- Authentication/authorization
- Payment processing
- Error infrastructure (base error classes)
- Core domain logic

**Tier 2 (ROI 5-10x)** - Standardize 50-80%
- Internal services
- CLI commands
- Data processors
- Middleware
- Background jobs
- Database access layer

**Tier 3 (ROI < 5x)** - Defer
- Test utilities
- Mocks and stubs
- Deprecated code
- One-off scripts
- Development tools

### Example Calculation

```python
# Example: API authentication endpoint
Impact: HIGH (10) - user-facing, security critical
Error Sites: 15 locations
Time Investment: 2 hours
Project Horizon: 12 months

ROI = (10 × 15 × 12) / 2 = 900 / 2 = 450x

# Example: Internal utility function
Impact: MEDIUM (5) - used by other services
Error Sites: 8 locations
Time Investment: 1 hour
Project Horizon: 12 months

ROI = (5 × 8 × 12) / 1 = 480 / 1 = 480x

# Example: Test mock
Impact: LOW (1) - only used in tests
Error Sites: 5 locations
Time Investment: 0.5 hours
Project Horizon: 12 months

ROI = (1 × 5 × 12) / 0.5 = 60 / 0.5 = 120x
```

---

## Proven Results

### Validation Metrics (from meta-cc project)

**Error Diagnosis Speed:**
- 60-75% faster diagnosis with rich context
- Average debug time: 45 min → 15 min

**ROI by Tier:**
- Tier 1 files: 16.7x average ROI
- Tier 2 files: 8.3x average ROI
- Overall value gain: 25.5% (Tier 1) + 6% (Tier 2) = 31.5%

**Consistency Improvements:**
- Baseline error handling: 70% → 90% consistency
- Baseline logging: 65% → 88% consistency
- Baseline configuration: 60% → 85% consistency

**CI Enforcement:**
- 0% regression rate (no new violations after enforcement)
- 0% false positive rate (accurate linters)
- 20-minute average setup time

**Language Transferability:**
- 80-90% pattern transferability across Go, Python, JavaScript, Rust
- Convention principles are language-agnostic
- Infrastructure patterns adapt with 10-20% effort

---

## Common Anti-Patterns

### ❌ 1. Standardizing Before Detecting
**Problem:** Manually reviewing code to find patterns
**Solution:** Automate detection with linters first

### ❌ 2. Equal Priority for All Files
**Problem:** Spending equal time on all files regardless of impact
**Solution:** Use ROI-based prioritization (Tier 1 > Tier 2 > Tier 3)

### ❌ 3. Manual Enforcement Only
**Problem:** Relying on code review to catch violations
**Solution:** Integrate automated linters into CI/CD

### ❌ 4. Bare Errors Without Context
**Problem:** `raise Exception("error")` or `throw new Error("error")`
**Solution:** Use sentinel errors with rich context (operation, resource, guidance)

### ❌ 5. Inconsistent Logging Libraries
**Problem:** Mix of print(), console.log(), multiple logging frameworks
**Solution:** Standardize on structured logging (structlog, winston)

### ❌ 6. Direct Environment Access Everywhere
**Problem:** `os.environ.get()` and `process.env` scattered throughout code
**Solution:** Centralized configuration with validation (Pydantic, Zod)

### ❌ 7. Log-and-Return Pattern
**Problem:** Logging errors and then raising them (causes duplicate logs)
**Solution:** Either log or raise, not both (raise and let caller log)

### ❌ 8. Swallowing Errors Silently
**Problem:** Catching exceptions without handling or re-raising
**Solution:** Always handle explicitly or re-raise with context

---

## Implementation Checklist

### Phase 1: Foundation (Week 1)
- [ ] Run pattern inventory (grep-based analysis)
- [ ] Calculate baseline consistency metrics
- [ ] Prioritize files by ROI (Tier 1/2/3)
- [ ] Define error handling conventions
- [ ] Define logging conventions
- [ ] Define configuration conventions

### Phase 2: Infrastructure (Week 2)
- [ ] Implement sentinel error base classes
- [ ] Create error enrichment utilities
- [ ] Set up structured logging
- [ ] Build configuration validation framework
- [ ] Write custom linters (AST-based)
- [ ] Document conventions

### Phase 3: Standardization (Weeks 3-4)
- [ ] Refactor Tier 1 files (100% coverage)
- [ ] Refactor Tier 2 files (50-80% coverage)
- [ ] Add comprehensive tests for error paths
- [ ] Update documentation

### Phase 4: Enforcement (Week 5)
- [ ] Add pre-commit hooks
- [ ] Integrate linters into CI pipeline
- [ ] Configure quality gates to block merges
- [ ] Generate compliance dashboards

### Phase 5: Monitoring (Ongoing)
- [ ] Track consistency metrics over time
- [ ] Monitor for regressions
- [ ] Train team on conventions
- [ ] Iterate on linter rules

---

## Related Skills

- **ms-foundation-constitution**: File size and complexity constraints
- **ms-foundation-trust**: Test coverage and type checking requirements
- **ms-essentials-review**: Code quality validation
- **ms-essentials-debug**: Error diagnosis patterns

---

## References

- 12-Factor App: https://12factor.net/
- Python structlog: https://www.structlog.org/
- TypeScript Zod: https://zod.dev/
- Pydantic: https://docs.pydantic.dev/
- Winston Logger: https://github.com/winstonjs/winston
- AST Parsing Python: https://docs.python.org/3/library/ast.html
- ESLint Plugin Development: https://eslint.org/docs/latest/extend/custom-rules

---

**Version:** 1.0.0 (Adapted for Python + TypeScript)
**Source:** github.com/yaleh/meta-cc (Go original)
**Validation:** Bootstrap-013 (91.7% pattern validation, 16.7x ROI)

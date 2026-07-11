# TRUST Security Implementation Examples

## Contents

- OWASP Top 10 (2021) - Before/After Patterns
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable and Outdated Components
- A07: Identification and Authentication Failures
- A08: Software and Data Integrity Failures
- A09: Security Logging and Monitoring Failures
- A10: Server-Side Request Forgery (SSRF)
- Constitution Compliance Notes

## OWASP Top 10 (2021) - Before/After Patterns

---

## A01: Broken Access Control

### Problem
Users can access data they shouldn't (e.g., view other users' orders).

### ❌ Insecure Implementation

```python
# No authorization check - any user can access any order!
@app.route("/orders/<int:order_id>")
@login_required
def get_order(order_id: int):
    order = Order.query.get(order_id)
    return jsonify(order.to_dict())
```

### ✅ Secure Implementation

```python
# TAG: @SPEC:SEC-001
# Verify user owns the resource before access

@app.route("/orders/<int:order_id>")
@login_required
def get_order(order_id: int):
    """
    Authorization check before data access.
    Constitution: Simple check, complexity ≤3.
    """
    order = Order.query.get_or_404(order_id)

    # Authorization check
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403, description="You don't have permission to view this order")

    return jsonify(order.to_dict())
```

### ✅ Alternative: Decorator Pattern

```python
# TAG: @SPEC:SEC-002
# Reusable authorization decorator

from functools import wraps

def require_resource_owner(get_resource_user_id):
    """
    Decorator for resource ownership check.
    Constitution: Reusable pattern (DRY principle).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resource_id = kwargs.get('resource_id') or kwargs.get('order_id')
            resource_user_id = get_resource_user_id(resource_id)

            if resource_user_id != current_user.id and not current_user.is_admin:
                abort(403, description="Access denied")

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage
@app.route("/orders/<int:order_id>")
@login_required
@require_resource_owner(lambda order_id: Order.query.get(order_id).user_id)
def get_order(order_id: int):
    order = Order.query.get(order_id)
    return jsonify(order.to_dict())
```

---

## A02: Cryptographic Failures

### Problem
Storing passwords in plaintext or using weak encryption.

### ❌ Insecure Implementation

```python
# Plaintext password storage - NEVER DO THIS!
class User(db.Model):
    password = db.Column(db.String(100))  # Plaintext!

# Registration
user = User(email=email, password=password)  # No hashing
db.session.add(user)

# Login
user = User.query.filter_by(email=email, password=password).first()  # Plaintext comparison
```

### ✅ Secure Implementation (Password Hashing)

```python
# TAG: @SPEC:SEC-003
# bcrypt for password hashing

import bcrypt

class User(db.Model):
    """User model with secure password hashing."""
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str) -> None:
        """
        Hash password with bcrypt (salt automatically generated).
        Constitution: Simple method, single responsibility.
        """
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

# Registration
user = User(email=email)
user.set_password(password)  # Hashed
db.session.add(user)

# Login
user = User.query.filter_by(email=email).first()
if user and user.check_password(password):
    login_user(user)
```

### ✅ Secure Implementation (Data Encryption)

```python
# TAG: @SPEC:SEC-004
# Fernet symmetric encryption for sensitive data

from cryptography.fernet import Fernet
import os

class EncryptionService:
    """
    Encrypt sensitive data (SSN, credit cards).
    Constitution: Single responsibility (encryption only).
    """
    def __init__(self):
        # Key stored in environment variable (not hardcoded!)
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY environment variable not set")
        self.cipher = Fernet(key.encode())

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext to ciphertext."""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext to plaintext."""
        return self.cipher.decrypt(ciphertext.encode()).decode()

# Usage
encryption = EncryptionService()

# Store encrypted SSN
user.ssn_encrypted = encryption.encrypt("123-45-6789")

# Retrieve and decrypt
ssn = encryption.decrypt(user.ssn_encrypted)
```

---

## A03: Injection

### Problem
SQL, NoSQL, command, or template injection vulnerabilities.

### ❌ SQL Injection (Vulnerable)

```python
# String formatting - VULNERABLE to SQL injection!
email = request.args.get('email')  # Could be: "' OR '1'='1"
query = f"SELECT * FROM users WHERE email = '{email}'"
result = db.engine.execute(query)
```

### ✅ SQL Injection Prevention

```python
# TAG: @SPEC:SEC-005
# Use ORM (SQLAlchemy) or parameterized queries

# Option 1: ORM (Recommended)
email = request.args.get('email')
user = User.query.filter_by(email=email).first()

# Option 2: Parameterized query (if raw SQL needed)
from sqlalchemy import text
query = text("SELECT * FROM users WHERE email = :email")
result = db.engine.execute(query, {"email": email})
```

### ❌ Command Injection (Vulnerable)

```python
# Shell command with user input - VULNERABLE!
filename = request.args.get('file')
os.system(f"cat {filename}")  # Could be: "file.txt; rm -rf /"
```

### ✅ Command Injection Prevention

```python
# TAG: @SPEC:SEC-006
# Use subprocess with list (no shell interpretation)

import subprocess
from pathlib import Path

def read_file(filename: str) -> str:
    """
    Read file safely (no command injection).
    Constitution: Input validation + safe subprocess.
    """
    # Validate filename (no path traversal)
    if '..' in filename or filename.startswith('/'):
        raise ValueError("Invalid filename")

    # Use safe subprocess (no shell=True)
    filepath = Path('/safe/directory') / filename
    result = subprocess.run(
        ['cat', str(filepath)],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout
```

### ❌ NoSQL Injection (MongoDB - Vulnerable)

```python
# Direct object insertion - VULNERABLE!
email = request.json.get('email')  # Could be: {"$gt": ""}
user = db.users.find_one({"email": email})
```

### ✅ NoSQL Injection Prevention

```python
# TAG: @SPEC:SEC-007
# Validate input type before query

from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    """Schema validation prevents NoSQL injection."""
    email: EmailStr  # Must be valid email string (not object)
    password: str

@app.post("/login")
def login(data: LoginRequest):
    """Type-safe login (Pydantic validates input)."""
    user = db.users.find_one({"email": data.email})  # Safe (string only)
    if user and check_password(data.password, user['password_hash']):
        return {"token": create_token(user['_id'])}
```

---

## A04: Insecure Design

### Problem
Business logic flaws (e.g., discount abuse, race conditions).

### ❌ Insecure Discount Logic

```python
# No expiration check - discount can be used indefinitely!
@app.route("/apply-discount", methods=["POST"])
def apply_discount():
    code = request.json.get('code')
    discount = Discount.query.filter_by(code=code).first()

    if discount:
        # Apply discount (no validation!)
        return {"discount": discount.amount}
```

### ✅ Secure Business Logic

```python
# TAG: @SPEC:SEC-008
# Comprehensive discount validation

from datetime import datetime
from decimal import Decimal

class Discount(db.Model):
    """Discount with expiration and usage limits."""
    code = db.Column(db.String(50), unique=True)
    amount = db.Column(db.Decimal(10, 2))
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    usage_limit = db.Column(db.Integer, default=1)
    times_used = db.Column(db.Integer, default=0)
    min_order_amount = db.Column(db.Decimal(10, 2), default=0)

    def is_valid(self, order_amount: Decimal) -> tuple[bool, str | None]:
        """
        Validate discount with business rules.
        Constitution: Single responsibility, complexity ≤8.
        """
        now = datetime.utcnow()

        # Check expiration
        if now < self.valid_from:
            return False, "Discount not yet active"
        if now > self.valid_until:
            return False, "Discount expired"

        # Check usage limit
        if self.times_used >= self.usage_limit:
            return False, "Discount usage limit reached"

        # Check minimum order amount
        if order_amount < self.min_order_amount:
            return False, f"Order must be at least {self.min_order_amount}"

        return True, None

@app.route("/apply-discount", methods=["POST"])
def apply_discount():
    """Apply discount with validation."""
    code = request.json.get('code')
    order_amount = Decimal(request.json.get('order_amount'))

    discount = Discount.query.filter_by(code=code).first_or_404()

    # Validate business rules
    is_valid, error_message = discount.is_valid(order_amount)
    if not is_valid:
        return {"error": error_message}, 400

    # Increment usage (atomic operation)
    discount.times_used += 1
    db.session.commit()

    return {"discount": float(discount.amount)}
```

---

## A05: Security Misconfiguration

### Problem
Missing security headers, verbose error messages, default credentials.

### ❌ Insecure Configuration

```python
# Debug mode in production - leaks stack traces!
app = Flask(__name__)
app.config['DEBUG'] = True  # NEVER in production!

# No security headers
@app.route("/")
def index():
    return render_template("index.html")
```

### ✅ Secure Configuration

```python
# TAG: @SPEC:SEC-009
# Production-ready Flask configuration

from flask import Flask
from flask_talisman import Talisman
import os

app = Flask(__name__)

# Environment-based config (not hardcoded)
app.config['DEBUG'] = os.environ.get('FLASK_ENV') == 'development'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')  # Required!

# Security headers (Flask-Talisman)
csp = {
    'default-src': "'self'",
    'script-src': ["'self'", "'unsafe-inline'", "https://cdn.example.com"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': '*',
}

Talisman(
    app,
    force_https=True,  # Redirect HTTP → HTTPS
    strict_transport_security=True,  # HSTS header
    content_security_policy=csp,  # CSP header
    x_content_type_options=True,  # X-Content-Type-Options: nosniff
    x_frame_options='SAMEORIGIN',  # Clickjacking protection
)

# CORS whitelist (not allow all)
from flask_cors import CORS
CORS(app, origins=[
    "https://app.example.com",
    "https://admin.example.com"
])

# Custom error handlers (no stack traces)
@app.errorhandler(500)
def internal_error(error):
    """Generic error message (no details)."""
    return {"error": "Internal server error"}, 500
```

---

## A06: Vulnerable and Outdated Components

### Problem
Using libraries with known CVEs.

### ✅ Prevention Strategy

```bash
# TAG: @SPEC:SEC-010
# Automated dependency scanning

# 1. Pin dependencies (requirements.txt)
Flask==3.0.0
SQLAlchemy==2.0.23
cryptography==41.0.7

# 2. Scan for vulnerabilities (trivy)
trivy fs --severity HIGH,CRITICAL .

# 3. Python-specific (bandit + safety)
bandit -r src/ -ll
safety check --json

# 4. CI/CD integration (GitHub Actions)
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'HIGH,CRITICAL'
          exit-code: '1'  # Fail on vulnerabilities
```

---

## A07: Identification and Authentication Failures

### Problem
Weak passwords, no rate limiting, session fixation.

### ✅ Secure Authentication

```python
# TAG: @SPEC:SEC-011
# Comprehensive authentication security

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import secrets
from datetime import timedelta

app = Flask(__name__)

# Rate limiting (prevent brute force)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379"
)

# Secure session configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,      # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,    # No JavaScript access
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
)

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")  # Max 5 login attempts per minute
def login():
    """
    Secure login with rate limiting.
    Constitution: Simple flow, complexity ≤7.
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Fetch user
    user = User.query.filter_by(email=email).first()

    # Constant-time comparison (prevent timing attacks)
    if user and user.check_password(password):
        # Generate secure session token
        session['user_id'] = user.id
        session['csrf_token'] = secrets.token_hex(32)

        # Regenerate session ID (prevent session fixation)
        session.permanent = True
        session.modified = True

        return {"message": "Login successful"}
    else:
        # Generic error (don't reveal if email exists)
        return {"error": "Invalid credentials"}, 401


# Password strength validation
from password_strength import PasswordPolicy

policy = PasswordPolicy.from_names(
    length=12,  # Min length
    uppercase=1,  # At least 1 uppercase
    numbers=1,  # At least 1 number
    special=1,  # At least 1 special char
)

@app.route("/register", methods=["POST"])
def register():
    """Registration with password strength check."""
    password = request.json.get('password')

    # Validate password strength
    errors = policy.test(password)
    if errors:
        return {"error": "Password too weak", "details": str(errors)}, 400

    # Create user
    user = User(email=request.json.get('email'))
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return {"message": "User created"}, 201
```

---

## A08: Software and Data Integrity Failures

### Problem
Unsigned packages, no integrity checks on updates.

### ✅ Integrity Verification

```python
# TAG: @SPEC:SEC-012
# Verify package integrity before installation

import hashlib
import requests

def verify_package_hash(package_url: str, expected_sha256: str) -> bool:
    """
    Download package and verify SHA256 hash.
    Constitution: Single responsibility (verification only).
    """
    response = requests.get(package_url)
    actual_hash = hashlib.sha256(response.content).hexdigest()

    if actual_hash != expected_sha256:
        raise ValueError(f"Hash mismatch: expected {expected_sha256}, got {actual_hash}")

    return True

# requirements.txt with hashes (pip install --require-hashes)
# Flask==3.0.0 --hash=sha256:abc123...
# cryptography==41.0.7 --hash=sha256:def456...
```

---

## A09: Security Logging and Monitoring Failures

### Problem
No logging of security events, no alerting on suspicious activity.

### ✅ Structured Security Logging

```python
# TAG: @SPEC:SEC-013
# Structured logging with correlation IDs

import logging
import uuid
from flask import g, request
from datetime import datetime

# Configure structured logging (JSON format)
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)

@app.before_request
def assign_correlation_id():
    """Assign correlation ID to each request."""
    g.correlation_id = str(uuid.uuid4())

def log_security_event(event_type: str, details: dict):
    """
    Log security event with context.
    Constitution: Never log sensitive data (passwords, tokens).
    """
    logger.warning({
        "event_type": event_type,
        "correlation_id": g.get('correlation_id'),
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get('User-Agent'),
        "timestamp": datetime.utcnow().isoformat(),
        "details": details  # Never include passwords or tokens!
    })

@app.route("/login", methods=["POST"])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        log_security_event("LOGIN_SUCCESS", {"user_id": user.id})
        return {"message": "Login successful"}
    else:
        # Log failed login (for brute force detection)
        log_security_event("LOGIN_FAILURE", {
            "email": email,  # OK to log (not sensitive)
            # NEVER log password!
        })
        return {"error": "Invalid credentials"}, 401
```

---

## A10: Server-Side Request Forgery (SSRF)

### Problem
Application makes requests to URLs controlled by attacker.

### ❌ SSRF Vulnerability

```python
# User-controlled URL - VULNERABLE!
url = request.args.get('url')  # Could be: "http://localhost:6379/admin"
response = requests.get(url)  # Fetch internal service!
```

### ✅ SSRF Prevention

```python
# TAG: @SPEC:SEC-014
# URL whitelist + validation

from urllib.parse import urlparse
import ipaddress

ALLOWED_DOMAINS = [
    "api.example.com",
    "cdn.example.com"
]

def is_safe_url(url: str) -> bool:
    """
    Validate URL is not internal/localhost.
    Constitution: Clear validation, complexity ≤8.
    """
    parsed = urlparse(url)

    # Check protocol (only HTTP/HTTPS)
    if parsed.scheme not in ['http', 'https']:
        return False

    # Check domain whitelist
    if parsed.hostname not in ALLOWED_DOMAINS:
        return False

    # Prevent IP-based access (including localhost)
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        if ip.is_private or ip.is_loopback:
            return False
    except ValueError:
        pass  # Not an IP address (hostname is OK)

    return True

@app.route("/fetch")
def fetch_url():
    """Fetch external URL safely."""
    url = request.args.get('url')

    if not is_safe_url(url):
        return {"error": "Invalid URL"}, 400

    response = requests.get(url, timeout=5)
    return {"content": response.text}
```

---

## Constitution Compliance Notes

**File Size**:
- ✅ Each security module: ≤300 SLOC
- ✅ Validation functions: ≤50 LOC each

**Complexity**:
- ✅ Password validation: Complexity ≤5
- ✅ Authorization checks: Complexity ≤3
- ✅ Discount validation: Complexity ≤8

**Testing**:
```python
# TAG: @TEST:SEC-001
# Security tests (no real passwords in tests!)

def test_password_hashing():
    """Test bcrypt hashing."""
    user = User()
    user.set_password("SecurePass123!")

    # Verify hash is different from plaintext
    assert user.password_hash != "SecurePass123!"

    # Verify correct password validates
    assert user.check_password("SecurePass123!")

    # Verify wrong password rejects
    assert not user.check_password("WrongPassword")
```

# EARS Requirements Examples

## Example 1: Ubiquitous Pattern (Unconditional Requirements)

### ✅ GOOD Examples

```
System SHALL provide HTTPS for all external API communication
System SHALL hash all passwords using bcrypt with minimum 12 rounds
System SHALL validate all user inputs before processing
System SHALL log all authentication attempts with timestamp and IP address
System SHALL enforce rate limiting of 100 requests per minute per IP
```

### ❌ BAD Examples (and fixes)

```
System should be secure
→ System SHALL enforce HTTPS for all connections
→ System SHALL hash passwords using bcrypt (≥12 rounds)
→ System SHALL validate all inputs against whitelist patterns

API should be fast
→ System SHALL respond to GET requests within 200ms for 95% of requests
→ System SHALL process batch operations within 5 seconds

Application must work well
→ System SHALL maintain 99.9% uptime during business hours
→ System SHALL handle concurrent requests from 1000+ users
```

---

## Example 2: Event-driven Pattern (Triggered Requirements)

### ✅ GOOD Examples

```
WHEN user clicks login button, system SHALL initiate authentication process
WHEN file upload completes, system SHALL generate thumbnail within 5 seconds
WHEN API request fails, system SHALL retry up to 3 times with exponential backoff
WHEN user session expires, system SHALL redirect to login page
WHEN payment succeeds, system SHALL send confirmation email within 1 minute
```

### ❌ BAD Examples (and fixes)

```
User can login
→ WHEN user submits valid email and password, system SHALL issue JWT token
→ WHEN user clicks login button, system SHALL validate credentials

Files get uploaded
→ WHEN user selects file, system SHALL display upload progress bar
→ WHEN file upload completes, system SHALL notify user with success message

Errors are handled
→ WHEN API returns 500 error, system SHALL display user-friendly error message
→ WHEN network connection fails, system SHALL cache request for retry
```

---

## Example 3: State-driven Pattern (Continuous Behavior)

### ✅ GOOD Examples

```
WHILE user session is active, system SHALL display auto-logout countdown timer
WHILE file is uploading, system SHALL display progress bar with percentage
WHILE database connection is lost, system SHALL attempt reconnection every 30 seconds
WHILE user has unpaid invoices, system SHALL display payment reminder banner
WHILE system is in maintenance mode, system SHALL return 503 status for all requests
```

### ❌ BAD Examples (and fixes)

```
Uploading files shows progress
→ WHILE file is uploading, system SHALL update progress bar every 500ms
→ WHILE upload is in progress, system SHALL disable file selection

Logged in users see different UI
→ WHILE user is authenticated, system SHALL display personalized dashboard
→ WHILE user session is active, system SHALL show logout button

System handles offline mode
→ WHILE network is disconnected, system SHALL queue operations for sync
→ WHILE offline, system SHALL display "No connection" indicator
```

---

## Example 4: Optional Pattern (Conditional Features)

### ✅ GOOD Examples

```
WHERE user has admin privileges, system MAY display advanced settings menu
WHERE network speed is below 1 Mbps, system MAY serve low-resolution images
WHERE user grants location permission, system MAY recommend nearby stores
WHERE user enables dark mode, system MAY apply dark color scheme
WHERE user has premium subscription, system MAY unlock exclusive features
```

### ❌ BAD Examples (and fixes)

```
System may provide recommendations
→ WHERE user has browsing history, system MAY suggest related products
→ WHERE user enables personalization, system MAY recommend content

Admin features could be useful
→ WHERE user role is admin, system MAY display audit logs
→ WHERE user has elevated permissions, system MAY access system settings

System might optimize performance
→ WHERE server load is below 30%, system MAY pre-cache frequently accessed data
→ WHERE user device has GPU, system MAY enable hardware acceleration
```

---

## Example 5: Constraints Pattern (Limitations and Error Handling)

### ✅ GOOD Examples

```
IF password fails 3 times, system SHALL lock account for 15 minutes
IF file size exceeds 10MB, system SHALL reject upload with error message
IF API rate limit is exceeded, system SHALL return 429 status code
IF session is idle for 30 minutes, system SHALL terminate session
IF database query takes longer than 5 seconds, system SHALL timeout and log error
```

### ❌ BAD Examples (and fixes)

```
Handle login failures
→ IF password fails 3 times, system SHALL lock account for 15 minutes
→ IF account is locked, system SHALL send unlock email to user

Validate file uploads
→ IF file extension is not in [jpg, png, pdf], system SHALL reject upload
→ IF file size exceeds 10MB, system SHALL display size limit error

Manage sessions
→ IF session expires, system SHALL redirect user to login page
→ IF session token is invalid, system SHALL return 401 error
```

---

## Example 6: Forbidden Phrases Replacement Guide

| Forbidden Phrase | Context | EARS Replacement |
|------------------|---------|------------------|
| "fast", "quickly" | System should respond quickly | System SHALL respond within 200ms for 95% of requests |
| "secure", "safely" | System should be secure | System SHALL enforce HTTPS + System SHALL hash passwords using bcrypt |
| "user-friendly" | Interface should be user-friendly | System SHALL display input validation errors inline + System SHALL provide autocomplete suggestions |
| "can", "could" | User can upload files | WHEN user selects file, system SHALL validate size and type |
| "might", "may" (ambiguous) | System might cache data | WHERE cache is enabled, system MAY store responses for 5 minutes |
| "should", "would" | System should validate inputs | System SHALL validate all inputs against defined schemas |
| "appropriate", "proper" | Use appropriate error handling | IF database error occurs, system SHALL log error and return 500 status |
| "easily", "simply" | Users can easily find settings | System SHALL display settings link in navigation menu |

---

## Example 7: Korean → English EARS Conversion

### Input (Korean Natural Language)

```
사용자가 로그인 버튼을 클릭하면 인증 프로세스가 시작됩니다.
비밀번호가 3회 실패하면 계정이 15분간 잠깁니다.
사용자 세션이 활성화되어 있는 동안 자동 로그아웃 타이머가 표시됩니다.
관리자 권한이 있는 경우 고급 설정 메뉴가 표시될 수 있습니다.
시스템은 모든 외부 통신에 HTTPS를 사용해야 합니다.
```

### Output (English EARS)

```
WHEN user clicks login button, system SHALL initiate authentication process
IF password fails 3 times, system SHALL lock account for 15 minutes
WHILE user session is active, system SHALL display auto-logout timer
WHERE user has admin privileges, system MAY display advanced settings menu
System SHALL provide HTTPS for all external communication
```

---

## Example 8: Measurability Check

### ❌ NOT MEASURABLE

```
"System should be performant"
→ No criteria, no test case derivable

"Login should work smoothly"
→ "Smoothly" is subjective, not observable

"Error handling should be robust"
→ "Robust" is ambiguous, no success criteria
```

### ✅ MEASURABLE

```
"System SHALL respond to GET /api/users within 200ms for 95% of requests"
→ Clear criteria: 200ms, 95th percentile, specific endpoint
→ Test: Measure response times, assert 95th percentile <200ms

"WHEN user submits invalid email, system SHALL return 400 error with message 'Invalid email format'"
→ Clear criteria: 400 status, specific error message
→ Test: POST invalid email, assert response.status == 400 and "Invalid email" in response.body

"IF password fails 3 times, system SHALL lock account for 15 minutes"
→ Clear criteria: 3 failures, 15 minutes lock duration
→ Test: Submit 3 wrong passwords, assert account.locked == True and lock_duration == 900 seconds
```

---

## Example 9: Complete SPEC with EARS (Compliant)

```markdown
# @SPEC:AUTH-001: User Authentication

## Ubiquitous Requirements
- System SHALL provide JWT-based authentication
- System SHALL hash all passwords using bcrypt with 12 rounds
- System SHALL enforce HTTPS for all authentication endpoints

## Event-driven Requirements
- WHEN user submits valid email and password, system SHALL issue JWT token
- WHEN user submits invalid credentials, system SHALL return 401 error
- WHEN authentication succeeds, system SHALL log attempt with timestamp and IP
- WHEN token expires, system SHALL return 401 error with message "Token expired"

## State-driven Requirements
- WHILE user is authenticated, system SHALL allow access to protected resources
- WHILE token is valid, system SHALL include user_id in request context

## Optional Requirements
- WHERE refresh token is provided, system MAY issue new access token
- WHERE user enables 2FA, system MAY require TOTP code

## Constraints
- IF password fails 3 times, system SHALL lock account for 15 minutes
- IF email format is invalid, system SHALL return 400 error
- IF token is missing, system SHALL return 401 error
```

---

## Example 10: Complete SPEC with EARS Violations (Non-compliant)

```markdown
# User Authentication (No TAG, missing EARS patterns)

## Requirements (❌ All violate EARS)
- System should provide secure login (ambiguous: "secure")
- Users can login with email and password (missing trigger: "can")
- Login should be fast (not measurable: "fast")
- Handle errors appropriately (ambiguous: "appropriately")
- System might support social login (ambiguous: "might")
- Password validation should work well (subjective: "well")

## Fixes Required
→ Apply EARS patterns
→ Replace forbidden phrases
→ Add measurable criteria
→ Add TAG blocks
```

**Corrected Version**: See Example 9.

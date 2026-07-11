# GEARS Requirements Examples

Canonical form: `[Where <static>] [While <runtime>] [When <trigger>] the <subject> shall <behavior>.`

## Contents

- 1. Unconditional (no clause)
- 2. When (event-driven)
- 3. While (runtime state)
- 4. Where (static condition)
- 5. Error handling (replaces classic `IF...then`)
- 6. Combined clauses (fixed order Where → While → When)
- 7. Classic EARS → GEARS migration table
- 8. Forbidden phrases → fix
- 9. Given-When-Then mapping (testability, R6)

## 1. Unconditional (no clause)

### ✅ GOOD
```
the auth service shall hash passwords using bcrypt with ≥12 rounds.
the API gateway shall serve all external traffic over HTTPS.
the chat API shall respond to GET requests within 200ms at p95.
```
### ❌ BAD → fix
```
System should be secure
→ the auth service shall hash passwords using bcrypt (≥12 rounds).
→ the API gateway shall reject any non-HTTPS request.

API should be fast
→ the chat API shall respond within 200ms at p95.
```
Note R1: a concrete subject (`the auth service`) instead of `the system`.

## 2. When (event-driven)

### ✅ GOOD
```
When a user submits valid credentials, the auth service shall issue a JWT session token.
When a file upload completes, the upload service shall enqueue a thumbnail job.
When an API request is received, the request logger shall record method, path, and latency.
```
### ❌ BAD → fix
```
User can log in
→ When a user submits valid credentials, the auth service shall issue a JWT session token.
```

## 3. While (runtime state)

### ✅ GOOD
```
While a transcription job is running, the admin UI shall display the job status as "processing".
While a user session is active, the API gateway shall accept the session cookie.
While a note is in edit mode, the editor shall autosave drafts every 10 seconds.
```
Reject misuse: `While OCR is enabled, …` ❌ → OCR-enabled is **static config** → use `Where` (R3/R2).

## 4. Where (static condition)

### ✅ GOOD
```
Where OCR is enabled, when a PDF is uploaded, the extraction service shall run OCR before chunking.
Where the caller is an admin, the dashboard API shall include raw mastery scores in the response.
Where the deploy environment is production, the config loader shall refuse to boot without JWT_SECRET.
```
`Where` = config / feature flag / deploy env / permission. Optional capability (old `MAY`) becomes a `Where`-gated `shall`.

## 5. Error handling (replaces classic `IF...then`)

GEARS drops `IF...then`; use the `[Error Handling]` label + `When`.
```
❌ If an invalid file type is uploaded, then the system shall reject the file.
✅ [Error Handling] When an invalid file type is uploaded, the upload service shall reject the file and display the supported file types.

❌ If parsing fails, then the system shall show an error.
✅ [Error Handling] When parsing fails, the upload service shall mark the source as failed and expose the failure reason to the admin UI.
```

## 6. Combined clauses (fixed order Where → While → When)

```
Where quiz generation is enabled, while a note is in the "refined" state, when the operator clicks "Generate", the quiz service shall create quiz candidates from the note.
```

## 7. Classic EARS → GEARS migration table

| Classic EARS | GEARS |
| --- | --- |
| `System SHALL provide HTTPS` | `the API gateway shall serve all traffic over HTTPS.` |
| `WHEN user clicks login, system SHALL authenticate` | `When a user clicks login, the auth service shall validate the credentials.` |
| `WHILE uploading, system SHALL show progress` | `While a file is uploading, the upload UI shall display a progress bar.` |
| `WHERE admin, system MAY view costs` | `Where the caller is an admin, the cost API shall return per-user cost.` |
| `IF password fails 3x, system SHALL lock account` | `[Error Handling] When a password fails 3 times, the auth service shall lock the account for 15 minutes.` |

## 8. Forbidden phrases → fix

```
"fast"        → the chat API shall respond within 200ms at p95.
"secure"      → the auth service shall hash passwords using bcrypt (≥12 rounds).
"user-friendly" → the upload UI shall surface the supported file types on rejection.
"should" / "can" / "might" → restate as a Where/When-gated `shall`.
```

## 9. Given-When-Then mapping (testability, R6)

```
GEARS:  While a user is authenticated, when the user requests their profile, the profile API shall return the user's profile data.
GWT:    Given a user is authenticated
        When the user requests their profile
        Then the profile API returns the user's profile data
```
Every GEARS requirement must map cleanly to at least one such acceptance test.

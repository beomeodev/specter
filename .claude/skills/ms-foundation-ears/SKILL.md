---
name: ms-foundation-ears
description: Requirements validation skill that enforces EARS syntax (Ubiquitous SHALL, Event-driven WHEN, State-driven WHILE, Optional WHERE, Constraints IF patterns), detects ambiguous forbidden phrases (fast, secure, user-friendly), ensures measurability and testability with clear pass/fail criteria, and provides concrete rewrite suggestions for non-compliant requirements
---

# Foundation: EARS Requirements Validation

## Skill Metadata
| Field | Value |
| ----- | ----- |
| Version | 1.0.0 |
| Created | 2025-10-26 |
| Allowed tools | Read, Grep |
| Auto-load | `/ms.specify`, `/ms.clarify` |
| Trigger cues | Requirement writing, SPEC validation, ambiguity detection |

## What it does

Validates requirements compliance with Constitution Section IV (EARS Standards):
- Enforces 5 EARS patterns (Ubiquitous, Event-driven, State-driven, Optional, Constraints)
- Detects ambiguous/forbidden phrases
- Ensures measurability and testability
- Provides rewrite suggestions for non-compliant requirements

## When to use

- Writing new specifications (`/ms.specify`)
- Clarifying requirements (`/ms.clarify`)
- SPEC review (`/ms.analyze`)
- Detecting ambiguous language
- Converting natural language → formal requirements

## How it works

### 5 EARS Patterns

#### 1. Ubiquitous (Unconditional)
**Format**: `System SHALL [capability]`

**When to use**: Always-applicable features, security policies, data formats

**Examples**:
- ✅ System SHALL provide HTTPS for all external communication
- ✅ System SHALL hash passwords using bcrypt
- ❌ System SHALL provide fast responses (not measurable)

#### 2. Event-driven (Triggered)
**Format**: `WHEN [trigger], system SHALL [action]`

**When to use**: User actions, external events, API calls

**Examples**:
- ✅ WHEN user clicks login button, system SHALL initiate authentication
- ✅ WHEN file upload completes, system SHALL generate thumbnail
- ❌ User can log in (trigger unclear)

#### 3. State-driven (Continuous)
**Format**: `WHILE [state], system SHALL [action]`

**When to use**: Continuous behaviors during specific states

**Examples**:
- ✅ WHILE user session is active, system SHALL display auto-logout timer
- ✅ WHILE file is uploading, system SHALL display progress bar
- ❌ Completed todos look different (state condition unclear)

#### 4. Optional (Conditional)
**Format**: `WHERE [condition], system MAY [action]`

**When to use**: Optional features, conditional enhancements

**Examples**:
- ✅ WHERE user has admin privileges, system MAY display advanced settings
- ✅ WHERE network speed is slow, system MAY serve low-quality images
- ❌ System may provide recommendation feature (condition unclear)

#### 5. Constraints (Limitations)
**Format**: `IF [condition], system SHALL [constraint]`

**When to use**: Error handling, input validation, security limits

**Examples**:
- ✅ IF password fails 3 times, system SHALL lock account for 15 minutes
- ✅ IF file size exceeds 10MB, system SHALL reject upload
- ❌ Handle errors (condition and constraint unclear)

### Forbidden Phrases

**Ambiguous Terms** (require clarification):
- ❌ "can", "could", "might" → Use WHERE or WHEN
- ❌ "should", "would be good" → Use WHERE or System SHALL
- ❌ "fast", "quickly", "slowly" → Specify exact metrics (e.g., "<200ms")
- ❌ "secure", "safe" → Define specific security measures
- ❌ "user-friendly", "intuitive" → Define specific behaviors

**Replacement Guide**:
```
"System should respond quickly"
→ "System SHALL respond within 200ms for 95% of requests"

"Login should be secure"
→ "System SHALL enforce password complexity (≥12 chars, mixed case, symbols)"
→ "WHEN user fails login 3 times, system SHALL lock account for 15 minutes"

"Feature could be useful"
→ "WHERE user enables advanced mode, system MAY display feature"
```

### Validation Algorithm

```python
def validate_ears_compliance(requirement: str) -> dict:
    """
    Validates single requirement against EARS patterns.

    Returns:
        {
            "compliant": bool,
            "pattern": str | None,  # Which EARS pattern detected
            "violations": list[str],  # Forbidden phrases found
            "suggestions": list[str]  # Rewrite recommendations
        }
    """
    result = {
        "compliant": False,
        "pattern": None,
        "violations": [],
        "suggestions": []
    }

    # Check EARS patterns
    patterns = {
        "ubiquitous": r"System SHALL",
        "event_driven": r"WHEN .+, system SHALL",
        "state_driven": r"WHILE .+, system SHALL",
        "optional": r"WHERE .+, system MAY",
        "constraints": r"IF .+, system SHALL"
    }

    for pattern_name, regex in patterns.items():
        if re.search(regex, requirement, re.IGNORECASE):
            result["pattern"] = pattern_name
            result["compliant"] = True
            break

    # Check forbidden phrases
    forbidden = [
        "can", "could", "might", "should", "would",
        "fast", "quickly", "slowly", "secure", "safe",
        "user-friendly", "intuitive", "easy"
    ]

    for phrase in forbidden:
        if re.search(rf"\b{phrase}\b", requirement, re.IGNORECASE):
            result["violations"].append(phrase)
            result["compliant"] = False

    # Generate suggestions
    if not result["compliant"]:
        if not result["pattern"]:
            result["suggestions"].append(
                "Add EARS keyword: System SHALL, WHEN, WHILE, WHERE, or IF"
            )
        if result["violations"]:
            result["suggestions"].append(
                f"Replace ambiguous terms: {', '.join(result['violations'])}"
            )

    return result
```

### Measurability Check

Every requirement must answer:
1. "When is this requirement satisfied?" → Clear pass/fail criteria
2. "How will this be tested?" → Test case derivable from requirement
3. "What does success look like?" → Observable outcome

**Example**:
```
❌ "System should be fast"
→ NOT MEASURABLE (no criteria)

✅ "System SHALL respond to GET /api/users within 200ms for 95% of requests"
→ MEASURABLE (200ms, 95% threshold, specific endpoint)
```

## Inputs
- Requirement text (natural language or EARS)
- SPEC document (`specs/<spec-id>/spec.md`)
- Language preference (Korean input → English EARS output)

## Outputs
- Validation report (compliant/non-compliant)
- Detected EARS pattern (if any)
- List of forbidden phrases found
- Suggested rewrites for non-compliant requirements
- Testability assessment

## Example Validation Report

```json
{
  "requirement": "User can login with email and password",
  "validation": {
    "compliant": false,
    "pattern": null,
    "violations": ["can"],
    "suggestions": [
      "Add EARS keyword: 'WHEN user submits email and password, system SHALL...'",
      "Replace 'can' with specific trigger condition"
    ],
    "measurability": "FAIL - No success criteria defined",
    "testability": "FAIL - Cannot derive test case"
  },
  "suggested_rewrites": [
    "WHEN user submits valid email and password, system SHALL issue JWT token",
    "System SHALL provide email/password authentication endpoint",
    "IF credentials are invalid, system SHALL return 401 error with message"
  ]
}
```

## Language Conversion (Korean → English EARS)

**My-Spec Workflow**:
1. User inputs requirements in Korean (natural language)
2. EARS validator converts Korean → English EARS format
3. ALL workflow documents (spec.md, plan.md, tasks.md) use English
4. EARS keywords remain in English (WHEN, WHILE, WHERE, IF)

**Conversion Example**:
```
Korean Input:
"사용자가 유효한 자격증명으로 로그인하면, 시스템은 JWT 토큰을 발급해야 한다"

English EARS Output:
"WHEN user submits valid credentials, system SHALL issue JWT token"
```

## CI/CD Integration

**Pre-commit Hook**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Scan SPEC for non-EARS requirements
if grep -rn "should\|could\|might" specs/; then
    echo "❌ Non-EARS requirements detected. Use EARS patterns."
    exit 1
fi
```

## Related Skills
- `moai-foundation-specs`: SPEC metadata validation
- `moai-alfred-spec-metadata-validation`: YAML frontmatter checks
- `/ms.clarify`: Interactive requirement clarification

---
description: "Amend specification and plan with post-implementation decisions"
---

# /ms.amend - Amend Spec & Plan

Updates the specification (`spec.md`) and implementation plan (`plan.md`) with decisions made during or after implementation.

## Overview

This command handles "round-2 design pivots" or post-implementation discoveries by:
1. Adding an **Amendment** section to `spec.md`.
2. Updating `plan.md` with relevant technical adjustments.
3. Issuing new Q-IDs for any new binding decisions.
4. Ensuring drift detection in `/ms.analyze` remains green.

## Usage

```
/ms.amend "Description of the change/decision"
```

## Execution Steps

### 1. Load Context

**Read required files**:
- `specs/[spec-id]/spec.md`
- `specs/[spec-id]/plan.md`
- `specs/[spec-id]/tasks.md`

### 2. Identify Target FRs/Decisions

Analyze the provided amendment text:
- Which Functional Requirements (FR) are superseded?
- Are there new binding decisions (Q-IDs)?
- Does it affect the SQL schema or file structure in the plan?

### 3. Update spec.md (Amendment)

**DO NOT** edit existing FRs in-place if the change is significant (≥10% change or signature change). Instead:

1. Add a `## Amendment N — YYYY-MM-DD` section at the end of `spec.md`.
2. List the superseded FRs.
3. Add `**[SUPERSEDED by Amendment N]**` marker above the original FRs.
4. Provide the replacement wording in the Amendment section.
5. If new decisions were made, issue new Q-IDs (e.g., Q11, Q12).

### 4. Update plan.md

1. Update the `## SQL Plan` or `## Project Structure` sections if they were affected.
2. Cross-reference the Amendment from `spec.md`.

### 5. Update tasks.md (Optional)

1. If the amendment changes the tasks, update the descriptions or mark them as removed.

### 6. Report Output

Display a summary in KOREAN:

```
✅ Amendment {N} 반영 완료!

📄 수정된 파일:
- specs/{ID}/spec.md (Amendment 섹션 추가 및 FR 마킹)
- specs/{ID}/plan.md (기술 세부사항 업데이트)

🔍 반영 내용:
- Superseded FRs: {FR-IDs}
- New Decisions: {Q-IDs}

🎯 다음 단계:
👉 /ms.analyze (문서 간 일관성 검증)
👉 /ms.implement (변경된 계획에 따라 구현 재개)
```

## Amendment Template

```markdown
## Amendment N — YYYY-MM-DD ([1-line trigger phrase])

### Trigger
[1-2 sentences: what was discovered and when]

### Supersedes
- FR-XXX-NNN (original): [original intent]
- FR-YYY-MMM (original): ...

### Replacement wording
[New FR text - full text]

### Cross-refs
- plan §"..." updated: [delta]
- tasks T-IDs affected: [T-NNN, T-MMM]
```

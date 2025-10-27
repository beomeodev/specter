---
name: ms-foundation-ears
description: EARS 구문(5가지 패턴)을 사용하여 요구사항을 검증합니다. 명확성과 테스트 가능성을 보장하기 위해 사양을 작성하거나 검토할 때 사용합니다.
allowed-tools:
  - Read
  - Grep
version: 1.0.0
created: 2025-10-26
---

# 기초: EARS 요구사항 검증

## 스킬 메타데이터
| 필드 | 값 |
| --- | --- |
| 버전 | 1.0.0 |
| 생성일 | 2025-10-26 |
| 허용된 도구 | Read, Grep |
| 자동 로드 | `/ms.specify`, `/ms.clarify` |
| 트리거 큐 | 요구사항 작성, SPEC 검증, 모호성 감지 |

## 기능

헌법 섹션 IV(EARS 표준)에 대한 요구사항 준수를 검증합니다:
- 5가지 EARS 패턴(유비쿼터스, 이벤트 기반, 상태 기반, 선택 사항, 제약 조건)을 적용합니다.
- 모호하거나 금지된 구문을 감지합니다.
- 측정 가능성과 테스트 가능성을 보장합니다.
- 비준수 요구사항에 대한 재작성 제안을 제공합니다.

## 사용 시기

- 새로운 사양 작성 (`/ms.specify`)
- 요구사항 명확화 (`/ms.clarify`)
- SPEC 검토 (`/ms.analyze`)
- 모호한 언어 감지
- 자연어를 공식 요구사항으로 변환

## 작동 방식

### 5가지 EARS 패턴

#### 1. 유비쿼터스 (무조건)
**형식**: `시스템은 [기능]을 제공해야 합니다 (System SHALL [capability])`

**사용 시기**: 항상 적용 가능한 기능, 보안 정책, 데이터 형식

**예시**:
- ✅ 시스템은 모든 외부 API 통신에 HTTPS를 제공해야 합니다 (System SHALL provide HTTPS for all external communication)
- ✅ 시스템은 bcrypt를 사용하여 비밀번호를 해시해야 합니다 (System SHALL hash passwords using bcrypt)
- ❌ 시스템은 빠른 응답을 제공해야 합니다 (측정 불가)

#### 2. 이벤트 기반 (트리거됨)
**형식**: `[트리거] 시 시스템은 [작업]을 수행해야 합니다 (WHEN [trigger], system SHALL [action])`

**사용 시기**: 사용자 작업, 외부 이벤트, API 호출

**예시**:
- ✅ 사용자가 로그인 버튼을 클릭하면 시스템은 인증을 시작해야 합니다 (WHEN user clicks login button, system SHALL initiate authentication)
- ✅ 파일 업로드가 완료되면 시스템은 썸네일을 생성해야 합니다 (WHEN file upload completes, system SHALL generate thumbnail)
- ❌ 사용자는 로그인할 수 있습니다 (트리거 불분명)

#### 3. 상태 기반 (지속적)
**형식**: `[상태]인 동안 시스템은 [작업]을 수행해야 합니다 (WHILE [state], system SHALL [action])`

**사용 시기**: 특정 상태 동안의 지속적인 동작

**예시**:
- ✅ 사용자 세션이 활성 상태인 동안 시스템은 자동 로그아웃 타이머를 표시해야 합니다 (WHILE user session is active, system SHALL display auto-logout timer)
- ✅ 파일이 업로드되는 동안 시스템은 진행률 표시줄을 표시해야 합니다 (WHILE file is uploading, system SHALL display progress bar)
- ❌ 완료된 할 일은 다르게 보입니다 (상태 조건 불분명)

#### 4. 선택 사항 (조건부)
**형식**: `[조건]인 경우 시스템은 [작업]을 수행할 수 있습니다 (WHERE [condition], system MAY [action])`

**사용 시기**: 선택적 기능, 조건부 개선

**예시**:
- ✅ 사용자에게 관리자 권한이 있는 경우 시스템은 고급 설정을 표시할 수 있습니다 (WHERE user has admin privileges, system MAY display advanced settings)
- ✅ 네트워크 속도가 느린 경우 시스템은 저품질 이미지를 제공할 수 있습니다 (WHERE network speed is slow, system MAY serve low-quality images)
- ❌ 시스템은 추천 기능을 제공할 수 있습니다 (조건 불분명)

#### 5. 제약 조건 (제한)
**형식**: `[조건]이면 시스템은 [제약 조건]을 따라야 합니다 (IF [condition], system SHALL [constraint])`

**사용 시기**: 오류 처리, 입력 유효성 검사, 보안 제한

**예시**:
- ✅ 비밀번호가 3회 실패하면 시스템은 15분 동안 계정을 잠가야 합니다 (IF password fails 3 times, system SHALL lock account for 15 minutes)
- ✅ 파일 크기가 10MB를 초과하면 시스템은 업로드를 거부해야 합니다 (IF file size exceeds 10MB, system SHALL reject upload)
- ❌ 오류 처리 (조건 및 제약 조건 불분명)

### 금지된 구문

**모호한 용어** (명확화 필요):
- ❌ "할 수 있다", "할 수 있었다", "일지도 모른다" → WHERE 또는 WHEN 사용
- ❌ "해야 한다", "좋을 것이다" → WHERE 또는 System SHALL 사용
- ❌ "빠른", "신속하게", "느리게" → 정확한 메트릭 지정 (예: "<200ms")
- ❌ "안전한", "안전하게" → 특정 보안 조치 정의
- ❌ "사용자 친화적인", "직관적인" → 특정 동작 정의

**대체 가이드**:
```
"시스템은 신속하게 응답해야 합니다"
→ "시스템은 요청의 95%에 대해 200ms 이내에 응답해야 합니다"

"로그인은 안전해야 합니다"
→ "시스템은 비밀번호 복잡성(12자 이상, 대소문자 혼합, 기호)을 강제해야 합니다"
→ "사용자가 3회 로그인에 실패하면 시스템은 15분 동안 계정을 잠가야 합니다"

"기능이 유용할 수 있습니다"
→ "사용자가 고급 모드를 활성화하면 시스템은 기능을 표시할 수 있습니다"
```

### 유효성 검사 알고리즘

```python
def validate_ears_compliance(requirement: str) -> dict:
    """
    단일 요구사항을 EARS 패턴에 대해 검증합니다.

    Returns:
        {
            "compliant": bool,
            "pattern": str | None,  # 감지된 EARS 패턴
            "violations": list[str],  # 발견된 금지된 구문
            "suggestions": list[str]  # 재작성 권장 사항
        }
    """
    result = {
        "compliant": False,
        "pattern": None,
        "violations": [],
        "suggestions": []
    }

    # EARS 패턴 확인
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

    # 금지된 구문 확인
    forbidden = [
        "can", "could", "might", "should", "would",
        "fast", "quickly", "slowly", "secure", "safe",
        "user-friendly", "intuitive", "easy"
    ]

    for phrase in forbidden:
        if re.search(rf"\b{phrase}\b", requirement, re.IGNORECASE):
            result["violations"].append(phrase)
            result["compliant"] = False

    # 제안 생성
    if not result["compliant"]:
        if not result["pattern"]:
            result["suggestions"].append(
                "EARS 키워드 추가: System SHALL, WHEN, WHILE, WHERE 또는 IF"
            )
        if result["violations"]:
            result["suggestions"].append(
                f"모호한 용어 바꾸기: {', '.join(result['violations'])}"
            )

    return result
```

### 측정 가능성 확인

모든 요구사항은 다음에 답해야 합니다:
1. "이 요구사항은 언제 충족됩니까?" → 명확한 통과/실패 기준
2. "어떻게 테스트됩니까?" → 요구사항에서 파생 가능한 테스트 케이스
3. "성공은 어떤 모습입니까?" → 관찰 가능한 결과

**예시**:
```
❌ "시스템은 빨라야 합니다"
→ 측정 불가 (기준 없음)

✅ "시스템은 요청의 95%에 대해 GET /api/users에 200ms 이내에 응답해야 합니다"
→ 측정 가능 (200ms, 95번째 백분위수 임계값, 특정 엔드포인트)
```

## 입력
- 요구사항 텍스트 (자연어 또는 EARS)
- SPEC 문서 (`specs/<spec-id>/spec.md`)
- 언어 기본 설정 (한국어 입력 → 영어 EARS 출력)

## 출력
- 유효성 검사 보고서 (준수/비준수)
- 감지된 EARS 패턴 (있는 경우)
- 발견된 금지된 구문 목록
- 비준수 요구사항에 대한 제안된 재작성
- 테스트 가능성 평가

## 예제 유효성 검사 보고서

```json
{
  "requirement": "사용자는 이메일과 비밀번호로 로그인할 수 있습니다",
  "validation": {
    "compliant": false,
    "pattern": null,
    "violations": ["can"],
    "suggestions": [
      "EARS 키워드 추가: '사용자가 이메일과 비밀번호를 제출하면 시스템은... SHALL'",
      "'can'을 특정 트리거 조건으로 바꾸기"
    ],
    "measurability": "실패 - 성공 기준이 정의되지 않음",
    "testability": "실패 - 테스트 케이스를 파생할 수 없음"
  },
  "suggested_rewrites": [
    "사용자가 유효한 이메일과 비밀번호를 제출하면 시스템은 JWT 토큰을 발급해야 합니다",
    "시스템은 이메일/비밀번호 인증 엔드포인트를 제공해야 합니다",
    "자격 증명이 유효하지 않으면 시스템은 메시지와 함께 401 오류를 반환해야 합니다"
  ]
}
```

## 언어 변환 (한국어 → 영어 EARS)

**My-Spec 워크플로우**:
1. 사용자가 한국어로 요구사항 입력 (자연어)
2. EARS 유효성 검사기가 한국어 → 영어 EARS 형식으로 변환
3. 모든 워크플로우 문서 (spec.md, plan.md, tasks.md)는 영어 사용
4. EARS 키워드는 영어로 유지 (WHEN, WHILE, WHERE, IF)

**변환 예시**:
```
한국어 입력:
"사용자가 유효한 자격증명으로 로그인하면, 시스템은 JWT 토큰을 발급해야 한다"

영어 EARS 출력:
"WHEN user submits valid credentials, system SHALL issue JWT token"
```

## CI/CD 통합

**사전 커밋 훅**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

# 비-EARS 요구사항에 대한 SPEC 스캔
if grep -rn "should\|could\|might" specs/; then
    echo "❌ 비-EARS 요구사항이 감지되었습니다. EARS 패턴을 사용하십시오."
    exit 1
fi
```

## 관련 스킬
- `moai-foundation-specs`: SPEC 메타데이터 유효성 검사
- `moai-alfred-spec-metadata-validation`: YAML 전면 정보 확인
- `/ms.clarify`: 대화형 요구사항 명확화

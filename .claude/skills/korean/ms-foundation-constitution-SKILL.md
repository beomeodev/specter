---
name: ms-foundation-constitution
description: 헌법 섹션 II에 따라 파일 크기(≤500 SLOC) 및 복잡성(함수당 ≤10)을 검증합니다. 코드 품질 제약 조건을 확인할 때 사용합니다.
allowed-tools:
  - Read
  - Bash
  - Grep
version: 1.0.0
created: 2025-10-26
---

# 기초: 헌법 준수

## 스킬 메타데이터
| 필드 | 값 |
| --- | --- |
| 버전 | 1.0.0 |
| 생성일 | 2025-10-26 |
| 허용된 도구 | Read, Bash, Grep |
| 자동 로드 | SessionStart, `/ms.implement`, `/ms.analyze` |
| 트리거 큐 | 코드 품질 확인, 파일 크기 검증, 복잡성 분석 |

## 기능

헌법 섹션 II(단순성 우선 아키텍처)에 대한 코드 준수를 검증합니다:
- 파일 크기 ≤500 SLOC(주석 및 빈 줄 제외 소스 코드 라인)
- 함수 복잡성 ≤10
- 함수 크기 ≤100 LOC
- 위반 시 실행 가능한 피드백 제공

## 사용 시기

- 새 코드 구현 전 (`/ms.implement`)
- 코드 검토 중 (`/ms.review`)
- 품질 게이트 확인 (`/ms.analyze`)
- 파일이 크기 제한에 가까워질 때
- 자동화된 CI/CD 검증

## 작동 방식

### 파일 크기 검증 (≤500 SLOC)

**SLOC 계산**:
```bash
# 소스 라인 수 계산 (주석 및 빈 줄 제외)
# 파이썬
grep -v '^\s*#' file.py | grep -v '^\s*"""' | grep -v '^\s*$' | wc -l

# 타입스크립트/자바스크립트
grep -v '^\s*//' file.ts | grep -v '^\s*\*' | grep -v '^\s*$' | wc -l
```

**검증 규칙**:
- ✅ SLOC ≤500: 통과
- ⚠️ 400 < SLOC ≤500: 경고 (제한에 가까워짐)
- ❌ SLOC >500: 실패 (파일 분할 필요)

**분할 전략** (SLOC >500인 경우):
1. 재사용 가능한 유틸리티 추출 → `utils/` 또는 `lib/`
2. 타입/인터페이스 분리 → `types/` 또는 `models/`
3. 도메인 책임별 분할 → 여러 개의 집중된 모듈

### 함수 복잡성 검증 (≤10)

**도구**:
- 파이썬: `radon cc` (McCabe 복잡성)
- 타입스크립트/자바스크립트: ESLint `complexity` 규칙
- Go: `gocyclo`
- Rust: `cargo-geiger`

**예시 (파이썬)**:
```bash
# radon 설치
pip install radon

# 복잡성 확인
radon cc src/ -a -nb --total-average

# 출력 형식:
# src/auth/service.py
#   M 15:0 authenticate_user - A (8)  ← 정상 (≤10)
#   M 42:0 refresh_token - B (12)     ← 위반 (>10)
```

**복잡성 척도** (McCabe):
- A (1-5): 단순
- B (6-10): 보통 ✅ 허용 가능
- C (11-20): 복잡 ❌ 위반
- D (21-50): 매우 복잡 ❌ 치명적
- E (51+): 유지 관리 불가 ❌ 치명적

**리팩토링 전략** (복잡성 >10인 경우):
1. 헬퍼 함수 추출
2. 조건부 로직 단순화 (가드 절)
3. 중첩된 if-else를 조기 반환으로 교체
4. 복잡한 계산을 별도 함수로 추출

### 함수 크기 검증 (≤100 LOC)

**LOC 계산** (주석 포함):
```bash
# 함수 정의와 다음 함수/EOF 사이의 줄 수 계산
# 파이썬 예시
awk '/^def / {start=NR} /^def / && start {print NR-start; start=NR}' file.py
```

**검증 규칙**:
- ✅ LOC ≤100: 통과
- ⚠️ 80 < LOC ≤100: 경고
- ❌ LOC >100: 실패 (헬퍼 추출 필요)

## 입력
- 소스 코드 파일 (`src/`, `lib/`, `app/`)
- 테스트 파일 (`tests/`)
- 언어 구성 (`.specify/config.json`)

## 출력
- 준수 보고서 (파일별 통과/실패)
- 파일별 분석이 포함된 SLOC 메트릭
- 줄 번호가 포함된 복잡성 위반
- 제안된 리팩토링 조치

## 예제 보고서

```json
{
  "compliance_status": "FAIL",
  "violations": [
    {
      "file": "src/auth/service.py",
      "type": "file_size",
      "sloc": 587,
      "limit": 500,
      "suggestion": "헬퍼를 src/auth/utils.py로 추출"
    },
    {
      "file": "src/auth/service.py",
      "type": "complexity",
      "function": "refresh_token",
      "complexity": 12,
      "limit": 10,
      "line": 42,
      "suggestion": "토큰 유효성 검사 로직을 별도 함수로 추출"
    }
  ],
  "summary": {
    "total_files": 15,
    "compliant_files": 13,
    "violations": 2
  }
}
```

## CI/CD 통합

**GitHub Actions 예시**:
```yaml
- name: 헌법 준수 확인
  run: |
    # 파이썬
    pip install radon
    radon cc src/ -a -nb --total-average --min B

    # 타입스크립트
    npm run lint -- --max-complexity 10
```

## 관련 스킬
- `ms-foundation-trust`: 전체 TRUST 5 유효성 검사
- `moai-essentials-refactor`: 리팩토링 지침
- `moai-essentials-review`: 코드 검토 자동화

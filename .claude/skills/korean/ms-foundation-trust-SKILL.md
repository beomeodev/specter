---
name: ms-foundation-trust
description: My-Spec 워크플로우에 대한 TRUST 5원칙(테스트 ≥85%, 가독성, 통일성, 보안성, 추적성)을 검증합니다. 전체 코드 품질을 확인할 때 사용합니다.
allowed-tools:
  - Read
  - Bash
  - Grep
version: 1.0.0
created: 2025-10-26
---

# 기초: TRUST 5 유효성 검사

## 스킬 메타데이터
| 필드 | 값 |
| --- | --- |
| 버전 | 1.0.0 |
| 생성일 | 2025-10-26 |
| 허용된 도구 | Read, Bash, Grep |
| 자동 로드 | `/ms.analyze`, `/ms.review` |
| 트리거 큐 | 품질 유효성 검사, 릴리스 준비 상태, TRUST 준수 |

## 기능

헌법 섹션 V(TRUST 5 원칙)에 대한 코드 준수를 확인합니다.
- **T**est First: 커버리지 ≥85%
- **R**eadable: 파일/함수 크기 제한, 복잡성 ≤10
- **U**nified: 타입 안전성, 린터 준수
- **S**ecured: 취약점 없음, 입력 유효성 검사
- **T**rackable: 완전한 TAG 체인 (@SPEC → @TEST → @CODE → @DOC)

## 사용 시기

- PR 병합 전 (`/ms.review`)
- 품질 게이트 확인 (`/ms.analyze`)
- 릴리스 유효성 검사
- CI/CD 파이프라인 실행
- 수동 품질 감사

## 작동 방식

### T - 테스트 우선 (커버리지 ≥85%)

**지원되는 도구**:
- 파이썬: `pytest --cov` (pytest-cov)
- 타입스크립트/JS: Vitest 또는 Jest(커버리지 포함)
- Go: `go test -cover`
- Rust: `cargo tarpaulin`

**유효성 검사 명령** (파이썬):
```bash
pytest --cov=src --cov=tests --cov-report=term-missing --cov-fail-under=85
```

**커버리지 메트릭**:
- 라인 커버리지 ≥85% (필수)
- 분기 커버리지 ≥80% (권장)
- 함수 커버리지 ≥90% (권장)

**품질 게이트**:
- ✅ 커버리지 ≥85%: 통과
- ⚠️ 80% ≤ 커버리지 <85%: 경고
- ❌ 커버리지 <80%: 실패 (구현 차단)

### R - 가독성 (코드 품질)

**크기 제약** (헌법에서):
- 파일 ≤500 SLOC
- 함수 ≤100 LOC
- 함수당 매개변수 ≤5
- 중첩 깊이 ≤4 수준
- 순환 복잡성 ≤10

**린팅 도구**:
- 파이썬: `ruff check .` (빠른 린터 + 포맷터)
- 타입스크립트: `biome check .` 또는 `eslint .`
- Go: `golangci-lint run`
- Rust: `cargo clippy`

**유효성 검사**:
```bash
# 파이썬
ruff check . --select C90 --max-complexity 10

# 타입스크립트
npx eslint . --max-warnings 0
```

### U - 통합 (아키텍처 및 타입 안전성)

**타입 확인**:
- 파이썬: `mypy src/ --strict`
- 타입스크립트: `tsc --noEmit --strict`
- Go: `go vet ./...`
- Rust: `cargo check`

**아키텍처 확인**:
- SPEC 기반 구조 (코드는 spec.md 구성을 미러링)
- 명확한 모듈 경계
- 종속성 방향 (도메인 내부로)
- 순환 종속성 없음

**유효성 검사**:
```bash
# 파이썬 타입 확인
mypy src/ --strict --disallow-untyped-defs

# 타입스크립트 타입 확인
tsc --noEmit --strict --noUnusedLocals --noUnusedParameters
```

### S - 보안 (보안 및 취약점 스캐닝)

**SAST 도구**:
- `trivy`: 취약점 스캐닝
- `bandit`: 파이썬 보안 문제
- `npm audit`: 자바스크립트 종속성
- `semgrep`: 정적 분석 패턴

**보안 체크리스트**:
- ✅ 하드코딩된 비밀 없음 (API 키, 비밀번호)
- ✅ 모든 외부 데이터에 대한 입력 유효성 검사
- ✅ 민감한 구성에 대한 환경 변수
- ✅ 높음/치명적 취약점 없음
- ✅ 최신 종속성

**유효성 검사**:
```bash
# 취약점 스캔
trivy fs --severity HIGH,CRITICAL .

# 파이썬 보안
bandit -r src/ -ll

# 종속성 감사
npm audit --audit-level=high
```

### T - 추적 가능 (TAG 체인 무결성)

**TAG 구조**:
- `@SPEC:ID` in `specs/<spec-id>/spec.md`
- `@TEST:ID` in `tests/`
- `@CODE:ID` in `src/`
- `@DOC:ID` in `docs/`

**체인 유효성 검사**:
```bash
# 모든 TAG 스캔
rg '@(SPEC|TEST|CODE|DOC):' -n specs/ tests/ src/ docs/

# 고아 TAG 찾기
rg '@CODE:AUTH-001' -l src/          # CODE 존재
rg '@SPEC:AUTH-001' -l specs/        # SPEC 누락 → 고아

# 중복 TAG 찾기
rg '@SPEC:AUTH-001' -c specs/ | awk '$1 > 1 {print "중복: " $0}'
```

**무결성 메트릭**:
- 완전한 체인: @SPEC와 @TEST 및 @CODE가 있는 비율
- 고아 TAG: 해당 파일이 없는 TAG
- 중복 TAG: 동일한 TAG ID가 여러 번 사용됨

## 입력
- 소스 코드 (`src/`, `tests/`)
- 사양 문서 (`specs/`)
- 프로젝트 구성 (`.specify/memory/constitution.md`)
- CI/CD 구성

## 출력
- TRUST 준수 보고서 (JSON 또는 마크다운)
- 원칙별 통과/실패
- 줄 번호가 포함된 상세 위반 사항
- 제안된 해결 조치
- 전체 품질 점수 (0-100%)

## 예제 보고서

```json
{
  "trust_compliance": {
    "test_first": {
      "status": "PASS",
      "coverage": 87.5,
      "threshold": 85.0
    },
    "readable": {
      "status": "WARNING",
      "violations": [
        {
          "file": "src/auth/service.py",
          "type": "complexity",
          "function": "refresh_token",
          "value": 12,
          "limit": 10
        }
      ]
    },
    "unified": {
      "status": "PASS",
      "type_errors": 0
    },
    "secured": {
      "status": "FAIL",
      "vulnerabilities": [
        {
          "severity": "HIGH",
          "package": "requests",
          "version": "2.25.0",
          "fixed_in": "2.31.0"
        }
      ]
    },
    "trackable": {
      "status": "PASS",
      "chain_integrity": 100.0,
      "orphaned_tags": 0
    }
  },
  "overall_score": 85.0,
  "decision": "CONDITIONAL_PASS"
}
```

## CI/CD 통합

**GitHub Actions 워크플로우**:
```yaml
name: TRUST 유효성 검사

on: [pull_request, push]

jobs:
  trust-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # T - 테스트 우선
      - name: 커버리지와 함께 테스트 실행
        run: |
          pip install pytest pytest-cov
          pytest --cov=src --cov-fail-under=85

      # R - 가독성
      - name: 코드 린트
        run: |
          pip install ruff
          ruff check . --max-complexity 10

      # U - 통합
      - name: 타입 확인
        run: |
          pip install mypy
          mypy src/ --strict

      # S - 보안
      - name: 보안 스캔
        run: |
          pip install bandit
          bandit -r src/ -ll

      # T - 추적 가능
      - name: TAG 무결성 확인
        run: |
          rg '@(SPEC|TEST|CODE):' -n specs/ tests/ src/ | wc -l
```

## 관련 스킬
- `ms-foundation-constitution`: 파일 크기 및 복잡성 유효성 검사
- `moai-foundation-tags`: TAG 스캐닝 및 인벤토리
- `moai-essentials-review`: 자동화된 코드 검토

---
name: ms-essentials-debug
description: My-Spec 워크플로우를 위한 스택 추적 분석, 오류 패턴 감지 및 수정 제안을 통한 고급 디버깅
allowed-tools:
  - Read
  - Bash
  - Write
  - Edit
  - TodoWrite
  - Grep
  - Glob
---

# MS Essentials Debug v1.0

## 스킬 메타데이터

| 필드 | 값 |
| --- | --- |
| **스킬 이름** | ms-essentials-debug |
| **버전** | 1.0.0 |
| **생성일** | 2025-10-26 |
| **마지막 업데이트** | 2025-10-26 |
| **언어 범위** | 파이썬, 타입스크립트, 자바스크립트 |
| **허용된 도구** | Read, Write, Edit, Bash, TodoWrite, Grep, Glob |
| **자동 로드** | 디버깅 시나리오 중 필요시 |
| **트리거 큐** | 런타임 오류, 스택 추적, "이것을 디버그", "이것이 왜 실패하는가?" |

---

## 기능

My-Spec 프로젝트를 위한 포괄적인 디버깅 지원:

- **스택 추적 분석**: 오류 스택 추적 구문 분석 및 해석
- **오류 패턴 인식**: 일반적인 오류 패턴 식별 (NoneType, undefined, 비동기 문제)
- **디버깅 단계**: 체계적인 디버깅 워크플로우 제공
- **근본 원인 식별**: 버그 원인을 찾기 위한 코드 분석
- **수정 제안**: 코드 예제와 함께 구체적인 수정 권장
- **테스트 우선 디버깅**: 버그를 재현하기 위한 실패 테스트 작성 (TDD RED 단계)

**주요 기능**:
- ✅ 파이썬 오류 분석 (TypeError, AttributeError, ImportError 등)
- ✅ 타입스크립트/자바스크립트 오류 분석 (undefined, null 참조, 프로미스 거부)
- ✅ 비동기/대기 디버깅 (처리되지 않은 프로미스 거부, 경쟁 조건)
- ✅ 테스트 실패 분석 (단언 오류, 테스트 격리 문제)
- ✅ TRUST 5 원칙과의 통합 (테스트 우선 디버깅)

---

## 사용 시기

**자동 트리거**:
- 런타임 오류, 예외, 충돌
- 스택 추적 분석 요청
- 테스트 실패
- "이것이 왜 실패하는가?", "이 오류를 디버그", "이 버그를 수정"

**수동 호출**:
- 설명할 수 없는 동작 발생 시
- 테스트가 불가사의하게 실패할 때
- 오류 메시지가 불분명할 때
- 비동기/프로미스 문제 디버깅 시
- 버그 보고서가 포함된 코드 검토 중

**일반적인 시나리오**:
1. **NoneType/undefined 오류**: 변수가 None/undefined여서는 안 될 때
2. **비동기 오류**: 프로미스 거부, 경쟁 조건, 콜백 지옥
3. **가져오기/모듈 오류**: 누락된 종속성, 순환 가져오기
4. **테스트 실패**: 단언 불일치, 테스트 격리 문제
5. **타입 오류**: 타입스크립트/파이썬 타입 힌트의 타입 불일치

---

## 작동 방식

### 1. 오류 분석 단계

**정보 수집**:
1. 전체 오류 메시지 및 스택 추적
2. 코드 컨텍스트 (실패한 함수/모듈)
3. 오류를 트리거한 입력 데이터 또는 테스트 케이스
4. 최근 변경 사항 (git diff)

**스택 추적 분석**:
```python
# 예제 파이썬 스택 추적 분석
Traceback (most recent call last):
  File "src/auth/service.py", line 45, in authenticate
    user = self.user_repo.find_by_email(email)
  File "src/auth/repository.py", line 23, in find_by_email
    return self.db.query(User).filter(User.email == email).first()
AttributeError: 'NoneType' object has no attribute 'query'
```

**진단**:
- 근본 원인: `self.db`가 None입니다 (데이터베이스 연결이 초기화되지 않음).
- 위치: `src/auth/repository.py:23`
- 영향: 인증 흐름이 완전히 깨졌습니다.
- 심각도: 치명적 (P0)

### 2. 근본 원인 조사

**5 Whys 질문**:
1. 왜 `self.db`가 None인가? → 데이터베이스가 주입되지 않았습니다.
2. 왜 주입되지 않았는가? → 생성자 매개변수가 누락되었습니다.
3. 왜 생성자 매개변수가 누락되었는가? → 종속성 주입이 잘못 구성되었습니다.
4. 왜 DI가 잘못 구성되었는가? → 컨테이너에 공급자가 누락되었습니다.
5. 왜 공급자가 누락되었는가? → 새 개발자가 DI 구성을 업데이트하지 않았습니다.

**일반적인 원인 확인**:
- ✅ 초기화되지 않은 변수
- ✅ 누락된 null 확인
- ✅ 잘못된 종속성 주입
- ✅ 누락된 구성
- ✅ 비동기 코드의 경쟁 조건
- ✅ 테스트 격리 문제 (공유 상태)

### 3. 수정 전략 개발

**테스트 우선 디버깅** (RED → GREEN → REFACTOR):

```python
# 1단계: RED - 버그를 재현하기 위한 실패 테스트 작성
def test_authenticate_with_valid_credentials():
    # 가정: 사용자가 데이터베이스에 존재합니다.
    user_repo = UserRepository(db_connection)
    auth_service = AuthService(user_repo)

    # 실행: 유효한 자격 증명으로 인증
    result = auth_service.authenticate("test@example.com", "password123")

    # 결과: 인증 성공
    assert result.is_authenticated == True
    # ^ 이 테스트는 AttributeError: 'NoneType' object has no attribute 'query'로 실패합니다.
```

```python
# 2단계: GREEN - 최소 수정 구현
class UserRepository:
    def __init__(self, db_connection):
        if db_connection is None:
            raise ValueError("db_connection이 필요합니다")
        self.db = db_connection  # 수정: db가 설정되었는지 확인

    def find_by_email(self, email: str) -> Optional[User]:
        if self.db is None:  # 방어적 확인
            raise RuntimeError("데이터베이스 연결이 초기화되지 않았습니다")
        return self.db.query(User).filter(User.email == email).first()
```

```python
# 3단계: REFACTOR - 디자인 개선
class UserRepository:
    def __init__(self, db_connection: DatabaseConnection):
        """데이터베이스 연결 주입

        Args:
            db_connection: 유효한 DatabaseConnection 인스턴스여야 합니다.

        Raises:
            ValueError: db_connection이 None인 경우
        """
        if db_connection is None:
            raise ValueError("db_connection은 필수이며 None일 수 없습니다")
        self.db: DatabaseConnection = db_connection
```

### 4. 확인 단계

1. **실패하는 테스트 실행** → 버그를 재현하는지 확인 (RED)
2. **수정 적용** → 해결책 구현
3. **테스트 다시 실행** → 통과하는지 확인 (GREEN)
4. **전체 테스트 스위트 실행** → 회귀 없음 확인
5. **수동 테스트** → 실제 애플리케이션에서 확인
6. **코드 검토** → TRUST 5에 대한 수정 품질 확인

---

## 실패 모드

### 디버깅이 실패하거나 차단될 때:

1. **컨텍스트 누락**: 스택 추적이 불완전하거나 오류 메시지가 잘렸습니다.
   - **해결책**: 전체 스택 추적 활성화 (`PYTHONTRACEBACK=1`, `NODE_OPTIONS=--trace-warnings`)

2. **간헐적인 버그**: 오류가 일관되게 재현되지 않습니다.
   - **해결책**: 로깅 추가, 중단점이 있는 디버거 사용, 경쟁 조건 확인

3. **테스트 격리 문제**: 테스트가 단독으로는 통과하지만 스위트에서는 실패합니다.
   - **해결책**: 공유 상태 확인, 테스트 간 데이터베이스 정리

4. **프로덕션 전용 버그**: 개발 환경에서 재현할 수 없습니다.
   - **해결책**: 환경 차이 확인, 프로덕션 로깅 활성화, 기능 플래그 사용

5. **디버거 사용 불가**: 디버거 도구가 설치되지 않았습니다.
   - **해결책**: 인쇄 디버깅, 로깅으로 대체하거나 언어별 디버거 설치

---

## 모범 사례

### ✅ 해야 할 일:

1. **실패하는 테스트 먼저 작성** (RED 단계)
   - 버그를 안정적으로 재현합니다.
   - 예상되는 동작을 문서화합니다.
   - 회귀를 방지합니다.

2. **변경하기 전에 디버거 사용**
   - 오류 위치에 중단점 설정
   - 변수 값 검사
   - 실행 단계별 진행

3. **명백한 것부터 먼저 확인**:
   - 변수가 초기화되었습니까?
   - 함수가 올바르게 호출되었습니까?
   - 타입이 올바릅니까?
   - 구성이 누락되었습니까?

4. **코드 주석에 수정 사항 문서화**
   - 버그가 발생한 이유 설명
   - 문제/티켓 번호 참조
   - 부분 수정인 경우 TODO 추가

5. **TRUST 5 원칙 준수**:
   - **T**est-First: 수정 전 테스트 작성
   - **R**eadable: 명확한 변수 이름, 주석
   - **U**nified: 타입 힌트, 일관된 패턴
   - **S**ecured: 보안 영향 확인
   - **T**rackable: 필요한 경우 TAG 체인 업데이트

### ❌ 하지 말아야 할 일:

1. **무작위로 추측하고 확인하지 않기**
   - 먼저 근본 원인 이해
   - 체계적인 디버깅 접근 방식 사용

2. **테스트 없이 수정하지 않기**
   - 수정되었는지 어떻게 알 수 있습니까?
   - 회귀를 어떻게 방지할 수 있습니까?

3. **오류 메시지 무시하지 않기**
   - 오류 메시지에는 귀중한 단서가 포함되어 있습니다.
   - 스택 추적은 실행 경로를 보여줍니다.

4. **주석 처리된 코드 커밋하지 않기**
   - 디버그 인쇄 문 제거
   - 임시 해결 방법 제거
   - 커밋하기 전에 정리

5. **REFACTOR 단계 건너뛰지 않기**
   - 수정은 작동하지만 코드가 지저분합니까? 리팩토링하십시오.
   - 기술 부채는 빠르게 누적됩니다.

---

## 예시

### 예시 1: 파이썬 NoneType 오류

**오류**:
```python
AttributeError: 'NoneType' object has no attribute 'email'
```

**디버깅 단계**:
1. None 값이 어디서 유래했는지 식별
2. 함수 반환 타입 확인
3. null 확인 또는 Optional 타입 추가
4. None 케이스에 대한 테스트 작성

**수정**:
```python
# 이전 (null 확인 없음)
def get_user_email(user):
    return user.email  # 사용자가 None이면 충돌 발생

# 이후 (방어적 확인)
def get_user_email(user: Optional[User]) -> str:
    if user is None:
        raise ValueError("사용자는 None일 수 없습니다")
    return user.email
```

### 예시 2: 자바스크립트 undefined 참조

**오류**:
```javascript
TypeError: Cannot read property 'name' of undefined
```

**디버깅 단계**:
1. 객체가 어디서 왔는지 확인
2. API 응답 구조 확인
3. 선택적 체이닝 또는 null 확인 추가
4. undefined 케이스에 대한 테스트 작성

**수정**:
```typescript
// 이전 (null 확인 없음)
function getUserName(user) {
  return user.name; // 사용자가 undefined이면 충돌 발생
}

// 이후 (선택적 체이닝)
function getUserName(user?: User): string {
  return user?.name ?? "익명";
}
```

### 예시 3: 비동기/프로미스 거부

**오류**:
```javascript
UnhandledPromiseRejectionWarning: Error: Connection timeout
```

**디버깅 단계**:
1. 프로미스 체인에 .catch() 추가
2. 비동기/대기와 함께 try-catch 사용
3. 네트워크/시간 초과 구성 확인
4. 오류 케이스에 대한 테스트 작성

**수정**:
```typescript
// 이전 (처리되지 않은 거부)
async function fetchData(url: string) {
  const response = await fetch(url); // 예외 발생 가능
  return response.json();
}

// 이후 (적절한 오류 처리)
async function fetchData(url: string): Promise<Data> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error(`${url} 가져오기 실패:`, error);
    throw new Error(`데이터 가져오기 실패: ${error.message}`);
  }
}
```

---

## 참조

**헌법**:
- 섹션 I: 테스트 우선 개발 (TDD RED → GREEN → REFACTOR)
- 섹션 V: TRUST 5 원칙 (테스트 우선, 가독성, 통일성, 보안성, 추적성)

**스킬**:
- `ms-foundation-trust`: TRUST 5 유효성 검사
- `ms-lang-python`: 파이썬 디버깅 도구
- `ms-lang-typescript`: 타입스크립트 디버깅 도구

**외부 리소스**:
- 파이썬 디버깅: `pdb` 모듈, `pytest` 디버깅 플래그
- 타입스크립트 디버깅: Chrome DevTools, VS Code 디버거
- 비동기 디버깅: 프로미스 디버깅, 비동기 스택 추적

---

## 변경 로그

- **v1.0.0** (2025-10-26): My-Spec 워크플로우용 초기 릴리스
  - 스택 추적 분석
  - 오류 패턴 인식
  - 테스트 우선 디버깅 워크플로우
  - 파이썬/타입스크립트/자바스크립트 지원

---

## 함께 사용하면 좋은 것

- `ms-essentials-review`: 버그 수정 후 코드 품질 검토에 사용
- `ms-foundation-trust`: 수정 후 TRUST 5 준수 확인
- `ms-workflow-tag-manager`: 버그 수정 후 TAG 체인 업데이트
- `ms-lang-python`: 파이썬 관련 디버깅 기술
- `ms-lang-typescript`: 타입스크립트 관련 디버깅 기술

---

**사용법**: 런타임 오류가 발생하거나, 실패하는 테스트를 디버그해야 하거나, 스택 추적을 분석해야 할 때 이 스킬을 호출합니다. 이 스킬은 헌법의 테스트 우선 원칙에 따라 체계적인 디버깅 단계를 제공합니다.

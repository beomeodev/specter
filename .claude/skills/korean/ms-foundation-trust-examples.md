# TRUST 5 유효성 검사 예제

## 예제 1: 완전한 TRUST 준수 (통과)

**파일**: `src/auth/service.py`

```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/auth/test_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
"""

import bcrypt
from typing import Optional
from datetime import datetime, timedelta
import jwt
from .validators import validate_email, validate_password

class AuthService:
    """JWT 토큰을 사용하는 인증 서비스입니다."""

    def __init__(self, secret_key: str, token_expiry: int = 900):
        """
        인증 서비스를 초기화합니다.

        Args:
            secret_key: JWT 서명 비밀 (환경에서 가져옴)
            token_expiry: 토큰 만료 시간(초) (기본값: 15분)
        """
        self.secret_key = secret_key
        self.token_expiry = token_expiry

    def authenticate(self, email: str, password: str) -> dict:
        """
        이메일과 비밀번호로 사용자를 인증합니다.

        사용자가 유효한 자격 증명을 제출하면 시스템은 JWT 토큰을 발급해야 합니다.

        Args:
            email: 사용자 이메일 (유효성 검사됨)
            password: 사용자 비밀번호 (평문)

        Returns:
            dict: {"token": str, "expires_at": datetime}

        Raises:
            ValueError: 잘못된 이메일/비밀번호 형식
            AuthenticationError: 잘못된 자격 증명 또는 잠긴 계정
        """
        # 입력 유효성 검사 (보안)
        if not email or not password:
            raise ValueError("이메일과 비밀번호가 필요합니다")

        validate_email(email)  # 통합: 공유 유효성 검사기 사용
        validate_password(password)

        # 조기 반환 패턴 (가독성)
        user = self._get_user_by_email(email)
        if not user:
            raise AuthenticationError("잘못된 자격 증명")

        if not self._verify_password(password, user.password_hash):
            raise AuthenticationError("잘못된 자격 증명")

        if user.is_locked:
            raise AuthenticationError("계정이 잠겼습니다")

        # 토큰 생성
        token = self._generate_token(user.id)
        expires_at = datetime.utcnow() + timedelta(seconds=self.token_expiry)

        return {
            "token": token,
            "expires_at": expires_at.isoformat()
        }

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """bcrypt 해시와 비밀번호를 확인합니다."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )

    def _generate_token(self, user_id: int) -> str:
        """JWT 토큰을 생성합니다."""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=self.token_expiry),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def _get_user_by_email(self, email: str) -> Optional['User']:
        """이메일로 사용자를 가져옵니다(예제용 스텁)."""
        # 실제 구현에서는 데이터베이스를 쿼리합니다.
        pass
```

**TRUST 분석**:

**T - 테스트 우선**: ✅
```python
# tests/auth/test_service.py (pytest 커버리지: 95%)

def test_authenticate_with_valid_credentials():
    """
    사용자가 유효한 자격 증명을 제출하면 시스템은 JWT 토큰을 발급해야 합니다.
    @TEST:AUTH-001
    """
    service = AuthService(secret_key="test-secret")
    result = service.authenticate("user@example.com", "ValidPass123!")

    assert "token" in result
    assert "expires_at" in result
    assert jwt.decode(result["token"], "test-secret", algorithms=["HS256"])

def test_authenticate_with_invalid_credentials():
    """
    잘못된 자격 증명이 제공되면 시스템은 AuthenticationError를 반환해야 합니다.
    @TEST:AUTH-001
    """
    service = AuthService(secret_key="test-secret")

    with pytest.raises(AuthenticationError):
        service.authenticate("user@example.com", "WrongPassword")

def test_authenticate_with_locked_account():
    """
    계정이 잠겨 있으면 시스템은 액세스를 거부해야 합니다.
    @TEST:AUTH-001
    """
    # ... 테스트 구현
```

**R - 가독성**: ✅
- 파일: 120 SLOC (≤500) ✅
- 함수: ≤50 LOC ✅
- 복잡성: ≤10 ✅
- 명확한 변수 이름 ✅
- 가드 절에 대한 조기 반환 ✅

**U - 통합**: ✅
- 모든 함수에 대한 타입 힌트 ✅
- 공유 유효성 검사기 (`validate_email`, `validate_password`) ✅
- 일관된 오류 처리 ✅
- mypy --strict 통과 ✅

**S - 보안**: ✅
- 입력 유효성 검사 (이메일, 비밀번호 형식) ✅
- bcrypt 비밀번호 해싱 ✅
- 환경의 비밀 키 (하드코딩되지 않음) ✅
- 토큰 만료 시행 ✅
- 오류 메시지에 민감한 데이터 없음 ✅

**T - 추적 가능**: ✅
- TAG 블록 존재 (`@CODE:AUTH-001`) ✅
- 독스트링의 SPEC/TEST 참조 ✅
- 명확한 추적성 체인 ✅

---

## 예제 2: TRUST 위반 (실패)

**파일**: `src/auth/bad_service.py`

```python
# ❌ TAG 블록 없음 (추적 가능 위반)

class BadAuthService:
    # ❌ 타입 힌트 없음 (통합 위반)
    def __init__(self, secret):
        self.secret = "hardcoded-secret-key"  # ❌ 보안 위반

    # ❌ 테스트 없음 (테스트 우선 위반)
    def login(self, email, password):  # ❌ 유효성 검사 없음 (보안 위반)
        # ❌ 복잡성: 15 (가독성 위반 - 중첩된 if/else)
        if email:
            if password:
                user = self.get_user(email)
                if user:
                    if user.password == password:  # ❌ 평문 비밀번호
                        if user.status == "active":
                            if user.verified:
                                token = self.make_token(user.id)
                                if token:
                                    return token
                                else:
                                    return None
                            else:
                                return None
                        else:
                            return None
                    else:
                        return None
                else:
                    return None
            else:
                return None
        else:
            return None

    def make_token(self, uid):  # ❌ 약어 (가독성 위반)
        # ❌ 만료 없음 (보안 위반)
        return jwt.encode({"u": uid}, self.secret)  # ❌ 짧은 키
```

**TRUST 분석**:

**T - 테스트 우선**: ❌ 실패
- 테스트 파일 없음
- 커버리지: 0%

**R - 가독성**: ❌ 실패
- 복잡성: 15 (>10)
- 중첩된 if-else (8단계 깊이)
- 약어 (`uid` 대신 `user_id`)
- 독스트링 없음

**U - 통합**: ❌ 실패
- 타입 힌트 없음
- 일관성 없는 이름 지정 (`login` 대 `authenticate`)
- mypy 실패

**S - 보안**: ❌ 실패
- 하드코딩된 비밀 키
- 입력 유효성 검사 없음
- 평문 비밀번호 비교
- 토큰 만료 없음
- 상세한 오류 메시지 (정보 공개)

**T - 추적 가능**: ❌ 실패
- TAG 블록 없음
- SPEC 참조 없음
- 추적성 없음

**개선**: 예제 1에 따라 다시 작성합니다.

---

## 예제 3: 커버리지 보고서 (테스트 우선)

**pytest 커버리지 출력**:
```
---------- coverage: platform linux, python 3.13.2-final-0 ----------
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
src/auth/__init__.py           2      0   100%
src/auth/service.py           45      3    93%   78-80
src/auth/validators.py        12      0   100%
src/auth/models.py            18      1    94%   42
--------------------------------------------------------
TOTAL                         77      4    95%

Required coverage: 85%
✅ 통과
```

**커버리지 델타** (마지막 커밋 이후):
```
+2.5% 전체 커버리지
+15개의 새로운 라인 커버됨
-0개의 라인 커버되지 않음
✅ 커버리지 증가
```

---

## 예제 4: TAG 체인 유효성 검사 (추적 가능)

**완전한 체인** ✅:
```bash
$ rg '@(SPEC|TEST|CODE):AUTH-001' -n

specs/001-auth-spec/spec.md:
1:# @SPEC:AUTH-001: 인증 기능

tests/auth/test_service.py:
5:@TEST:AUTH-001

src/auth/service.py:
3:@CODE:AUTH-001
```

**고아 TAG** ❌:
```bash
$ rg '@CODE:USER-042' -n
src/user/profile.py:3:@CODE:USER-042

$ rg '@SPEC:USER-042' -n
# 결과 없음 → 고아 CODE 태그 (SPEC 누락)

$ rg '@TEST:USER-042' -n
# 결과 없음 → 고아 CODE 태그 (TEST 누락)
```

**중복 TAG** ❌:
```bash
$ rg '@SPEC:AUTH-001' -c specs/

specs/001-auth-spec/spec.md:1
specs/002-auth-v2-spec/spec.md:1  ← 중복!
```

---

## 예제 5: 보안 스캔 (보안)

**trivy 스캔 결과**:
```bash
$ trivy fs --severity HIGH,CRITICAL .

총: 2개의 취약점 (1개 높음, 1개 치명적)

높음: CVE-2024-12345
패키지: requests
버전: 2.25.0
수정 버전: 2.31.0

치명적: CVE-2024-67890
패키지: cryptography
버전: 38.0.0
수정 버전: 41.0.7

❌ 실패: 높음/치명적 취약점 감지됨
```

**수정 후**:
```bash
$ pip install --upgrade requests cryptography
$ trivy fs --severity HIGH,CRITICAL .

총: 0개의 취약점
✅ 통과
```

---

## 예제 6: 타입 안전성 (통합)

**mypy --strict 출력**:
```bash
$ mypy src/ --strict

src/auth/service.py:25: error: 함수에 반환 타입 주석이 없습니다.
src/auth/service.py:32: error: 인수 1의 타입이 호환되지 않습니다. "Optional[str]" 대신 "str"이 예상됩니다.

1개 파일에서 2개의 오류 발견 (15개 소스 파일 확인)
❌ 실패
```

**수정 후**:
```bash
$ mypy src/ --strict

성공: 15개 소스 파일에서 문제가 발견되지 않았습니다.
✅ 통과
```

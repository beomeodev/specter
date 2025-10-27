# 헌법 준수 예시

## 예시 1: 파일 크기 검증 (통과)

**파일**: `src/auth/utils.py` (245 SLOC)

```python
"""
@CODE:AUTH-002
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/auth/test_utils.py
"""

def validate_password(password: str) -> bool:
    """비밀번호 복잡성을 검증합니다."""
    if len(password) < 12:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit

def hash_password(password: str) -> str:
    """bcrypt를 사용하여 비밀번호를 해시합니다."""
    import bcrypt
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

# ... 235줄의 유틸리티 함수 추가
```

**결과**: ✅ 통과 (245 SLOC ≤ 500)

---

## 예시 2: 파일 크기 검증 (실패)

**파일**: `src/auth/service.py` (587 SLOC)

```python
"""
@CODE:AUTH-001
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/auth/test_service.py
"""

class AuthService:
    """모든 기능이 한 파일에 있는 인증 서비스입니다."""

    def __init__(self, db, cache, logger):
        self.db = db
        self.cache = cache
        self.logger = logger

    def authenticate_user(self, email, password):
        # 100줄의 인증 로직
        ...

    def refresh_token(self, refresh_token):
        # 120줄의 토큰 갱신 로직
        ...

    def validate_session(self, session_id):
        # 80줄의 세션 검증
        ...

    # ... 10개 이상의 메소드, 287줄 추가
```

**결과**: ❌ 실패 (587 SLOC > 500)

**리팩토링 전략**:
```
집중된 모듈로 분할:
- src/auth/service.py (150 SLOC) - 핵심 AuthService
- src/auth/token_manager.py (180 SLOC) - 토큰 작업
- src/auth/session_manager.py (120 SLOC) - 세션 처리
- src/auth/validators.py (137 SLOC) - 입력 유효성 검사
```

---

## 예시 3: 복잡성 검증 (통과)

**함수**: `authenticate_user` (복잡성: 8)

```python
def authenticate_user(email: str, password: str) -> dict:
    """이메일과 비밀번호로 사용자를 인증합니다."""
    # 가드 절 (조기 반환)
    if not email or not password:
        raise ValueError("이메일과 비밀번호가 필요합니다")

    user = db.get_user_by_email(email)
    if not user:
        raise AuthenticationError("잘못된 자격 증명")

    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        raise AuthenticationError("잘못된 자격 증명")

    if user.is_locked:
        raise AuthenticationError("계정이 잠겼습니다")

    # JWT 토큰 생성
    token = generate_jwt_token(user.id)
    return {"token": token, "user_id": user.id}
```

**복잡성 분석**:
- 4개의 if 문 = 4개의 결정 지점
- 4개의 조기 반환 = 중첩된 복잡성 없음
- 총 복잡성 = 8 ✅ (≤10)

---

## 예시 4: 복잡성 검증 (실패)

**함수**: `refresh_token` (복잡성: 15)

```python
def refresh_token(refresh_token: str) -> dict:
    """갱신 토큰을 사용하여 액세스 토큰을 갱신합니다."""
    if not refresh_token:
        raise ValueError("갱신 토큰이 필요합니다")

    try:
        payload = decode_jwt(refresh_token)
        if payload.get("type") != "refresh":
            raise InvalidTokenError("갱신 토큰이 아닙니다")

        user_id = payload.get("user_id")
        if not user_id:
            raise InvalidTokenError("user_id가 없습니다")

        user = db.get_user(user_id)
        if not user:
            raise InvalidTokenError("사용자를 찾을 수 없습니다")

        if user.is_locked:
            raise AuthenticationError("계정이 잠겼습니다")

        stored_token = cache.get(f"refresh_token:{user_id}")
        if stored_token != refresh_token:
            if stored_token:
                # 토큰 순환 감지됨
                cache.delete(f"refresh_token:{user_id}")
                raise SecurityError("토큰 순환 감지됨")
            else:
                # 첫 번째 갱신, 토큰 저장
                cache.set(f"refresh_token:{user_id}", refresh_token)

        # 새 액세스 토큰 생성
        new_token = generate_jwt_token(user_id)
        return {"token": new_token, "user_id": user_id}

    except JWTDecodeError as e:
        raise InvalidTokenError(f"잘못된 토큰: {e}")
```

**복잡성 분석**:
- 8개의 if 문 (중첩 포함)
- 2개의 중첩된 if-else 블록
- 예외 처리가 복잡성을 더함
- 총 복잡성 = 15 ❌ (>10)

**리팩토링 전략**:
```python
def refresh_token(refresh_token: str) -> dict:
    """액세스 토큰을 갱신합니다 (리팩토링됨)."""
    validate_refresh_token_format(refresh_token)
    payload = decode_and_verify_refresh_token(refresh_token)
    user = get_and_validate_user(payload["user_id"])
    verify_token_rotation(user.id, refresh_token)

    new_token = generate_jwt_token(user.id)
    return {"token": new_token, "user_id": user.id}

# 헬퍼 함수 (각각 복잡성 ≤5)
def validate_refresh_token_format(token: str):
    """토큰 형식을 검증합니다."""
    if not token:
        raise ValueError("갱신 토큰이 필요합니다")

def decode_and_verify_refresh_token(token: str) -> dict:
    """토큰 유형을 디코딩하고 확인합니다."""
    try:
        payload = decode_jwt(token)
        if payload.get("type") != "refresh":
            raise InvalidTokenError("갱신 토큰이 아닙니다")
        if not payload.get("user_id"):
            raise InvalidTokenError("user_id가 없습니다")
        return payload
    except JWTDecodeError as e:
        raise InvalidTokenError(f"잘못된 토큰: {e}")

def get_and_validate_user(user_id: int) -> User:
    """사용자를 가져오고 상태를 확인합니다."""
    user = db.get_user(user_id)
    if not user:
        raise InvalidTokenError("사용자를 찾을 수 없습니다")
    if user.is_locked:
        raise AuthenticationError("계정이 잠겼습니다")
    return user

def verify_token_rotation(user_id: int, token: str):
    """토큰 순환을 확인합니다."""
    stored_token = cache.get(f"refresh_token:{user_id}")
    if stored_token and stored_token != token:
        cache.delete(f"refresh_token:{user_id}")
        raise SecurityError("토큰 순환 감지됨")
    if not stored_token:
        cache.set(f"refresh_token:{user_id}", token)
```

**리팩토링 후 결과**:
- `refresh_token`: 복잡성 5 ✅
- `validate_refresh_token_format`: 복잡성 2 ✅
- `decode_and_verify_refresh_token`: 복잡성 4 ✅
- `get_and_validate_user`: 복잡성 4 ✅
- `verify_token_rotation`: 복잡성 4 ✅

---

## 예시 5: 함수 크기 검증

**통과** (87 LOC):
```python
def process_user_registration(data: dict) -> User:
    """유효성 검사를 통해 사용자 등록을 처리합니다."""
    # 20줄: 입력 유효성 검사
    validate_email(data["email"])
    validate_password(data["password"])
    validate_username(data["username"])

    # 15줄: 중복 확인
    if db.user_exists(data["email"]):
        raise DuplicateEmailError()

    # 20줄: 사용자 생성
    user = User(
        email=data["email"],
        username=data["username"],
        password_hash=hash_password(data["password"]),
        created_at=datetime.utcnow()
    )
    db.save(user)

    # 15줄: 환영 이메일 보내기
    send_welcome_email(user.email, user.username)

    # 10줄: 감사 로그
    logger.info(f"새 사용자 등록됨: {user.id}")

    return user  # 총: 87 LOC ✅
```

**실패** (142 LOC):
```python
def process_user_registration_with_everything(data: dict) -> User:
    """사용자 등록을 처리합니다 (너무 많은 작업을 수행)."""
    # 30줄: 입력 유효성 검사 (인라인, 추출되지 않음)
    # 20줄: 중복 확인 (복잡한 쿼리 포함)
    # 25줄: 비밀번호 해싱 (bcrypt 재구현)
    # 20줄: 사용자 생성
    # 25줄: 이메일 보내기 (인라인 SMTP 코드)
    # 12줄: 감사 로그
    # 10줄: 분석 추적
    return user  # 총: 142 LOC ❌
```

**리팩토링**: 통과 예시에 표시된 대로 헬퍼를 추출합니다.

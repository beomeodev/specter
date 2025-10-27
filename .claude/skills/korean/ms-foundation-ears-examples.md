# EARS 요구사항 예시

## 예시 1: 유비쿼터스 패턴 (무조건적 요구사항)

### ✅ 좋은 예시

```
시스템은 모든 외부 API 통신에 HTTPS를 제공해야 합니다 (System SHALL provide HTTPS for all external API communication)
시스템은 최소 12라운드의 bcrypt를 사용하여 모든 비밀번호를 해시해야 합니다 (System SHALL hash all passwords using bcrypt with minimum 12 rounds)
시스템은 처리 전에 모든 사용자 입력을 검증해야 합니다 (System SHALL validate all user inputs before processing)
시스템은 타임스탬프와 IP 주소로 모든 인증 시도를 기록해야 합니다 (System SHALL log all authentication attempts with timestamp and IP address)
시스템은 IP당 분당 100개의 요청으로 속도 제한을 시행해야 합니다 (System SHALL enforce rate limiting of 100 requests per minute per IP)
```

### ❌ 나쁜 예시 (및 수정)

```
시스템은 안전해야 합니다 (System should be secure)
→ 시스템은 모든 연결에 HTTPS를 시행해야 합니다 (System SHALL enforce HTTPS for all connections)
→ 시스템은 bcrypt(≥12 라운드)를 사용하여 비밀번호를 해시해야 합니다 (System SHALL hash passwords using bcrypt (≥12 rounds))
→ 시스템은 화이트리스트 패턴에 대해 모든 입력을 검증해야 합니다 (System SHALL validate all inputs against whitelist patterns)

API는 빨라야 합니다 (API should be fast)
→ 시스템은 요청의 95%에 대해 200ms 이내에 GET 요청에 응답해야 합니다 (System SHALL respond to GET requests within 200ms for 95% of requests)
→ 시스템은 5초 이내에 일괄 작업을 처리해야 합니다 (System SHALL process batch operations within 5 seconds)

애플리케이션은 잘 작동해야 합니다 (Application must work well)
→ 시스템은 업무 시간 동안 99.9%의 가동 시간을 유지해야 합니다 (System SHALL maintain 99.9% uptime during business hours)
→ 시스템은 1000명 이상의 동시 사용자로부터의 요청을 처리해야 합니다 (System SHALL handle concurrent requests from 1000+ users)
```

---

## 예시 2: 이벤트 기반 패턴 (트리거된 요구사항)

### ✅ 좋은 예시

```
사용자가 로그인 버튼을 클릭하면 시스템은 인증 프로세스를 시작해야 합니다 (WHEN user clicks login button, system SHALL initiate authentication process)
파일 업로드가 완료되면 시스템은 5초 이내에 썸네일을 생성해야 합니다 (WHEN file upload completes, system SHALL generate thumbnail within 5 seconds)
API 요청이 실패하면 시스템은 지수 백오프로 최대 3번 재시도해야 합니다 (WHEN API request fails, system SHALL retry up to 3 times with exponential backoff)
사용자 세션이 만료되면 시스템은 로그인 페이지로 리디렉션해야 합니다 (WHEN user session expires, system SHALL redirect to login page)
결제가 성공하면 시스템은 1분 이내에 확인 이메일을 보내야 합니다 (WHEN payment succeeds, system SHALL send confirmation email within 1 minute)
```

### ❌ 나쁜 예시 (및 수정)

```
사용자는 로그인할 수 있습니다 (User can login)
→ 사용자가 유효한 이메일과 비밀번호를 제출하면 시스템은 JWT 토큰을 발급해야 합니다 (WHEN user submits valid email and password, system SHALL issue JWT token)
→ 사용자가 로그인 버튼을 클릭하면 시스템은 자격 증명을 검증해야 합니다 (WHEN user clicks login button, system SHALL validate credentials)

파일이 업로드됩니다 (Files get uploaded)
→ 사용자가 파일을 선택하면 시스템은 업로드 진행률 표시줄을 표시해야 합니다 (WHEN user selects file, system SHALL display upload progress bar)
→ 파일 업로드가 완료되면 시스템은 성공 메시지로 사용자에게 알려야 합니다 (WHEN file upload completes, system SHALL notify user with success message)

오류가 처리됩니다 (Errors are handled)
→ API가 500 오류를 반환하면 시스템은 사용자 친화적인 오류 메시지를 표시해야 합니다 (WHEN API returns 500 error, system SHALL display user-friendly error message)
→ 네트워크 연결이 실패하면 시스템은 재시도를 위해 요청을 캐시해야 합니다 (WHEN network connection fails, system SHALL cache request for retry)
```

---

## 예시 3: 상태 기반 패턴 (지속적인 동작)

### ✅ 좋은 예시

```
사용자 세션이 활성 상태인 동안 시스템은 자동 로그아웃 카운트다운 타이머를 표시해야 합니다 (WHILE user session is active, system SHALL display auto-logout countdown timer)
파일이 업로드되는 동안 시스템은 백분율과 함께 진행률 표시줄을 표시해야 합니다 (WHILE file is uploading, system SHALL display progress bar with percentage)
데이터베이스 연결이 끊어진 동안 시스템은 30초마다 재연결을 시도해야 합니다 (WHILE database connection is lost, system SHALL attempt reconnection every 30 seconds)
사용자에게 미납 인보이스가 있는 동안 시스템은 결제 알림 배너를 표시해야 합니다 (WHILE user has unpaid invoices, system SHALL display payment reminder banner)
시스템이 유지 관리 모드인 동안 시스템은 모든 요청에 대해 503 상태를 반환해야 합니다 (WHILE system is in maintenance mode, system SHALL return 503 status for all requests)
```

### ❌ 나쁜 예시 (및 수정)

```
업로드 중인 파일은 진행률을 보여줍니다 (Uploading files shows progress)
→ 파일이 업로드되는 동안 시스템은 500ms마다 진행률 표시줄을 업데이트해야 합니다 (WHILE file is uploading, system SHALL update progress bar every 500ms)
→ 업로드가 진행 중인 동안 시스템은 파일 선택을 비활성화해야 합니다 (WHILE upload is in progress, system SHALL disable file selection)

로그인한 사용자는 다른 UI를 봅니다 (Logged in users see different UI)
→ 사용자가 인증된 동안 시스템은 개인화된 대시보드를 표시해야 합니다 (WHILE user is authenticated, system SHALL display personalized dashboard)
→ 사용자 세션이 활성 상태인 동안 시스템은 로그아웃 버튼을 표시해야 합니다 (WHILE user session is active, system SHALL show logout button)

시스템은 오프라인 모드를 처리합니다 (System handles offline mode)
→ 네트워크가 연결되지 않은 동안 시스템은 동기화를 위해 작업을 대기열에 넣어야 합니다 (WHILE network is disconnected, system SHALL queue operations for sync)
→ 오프라인 상태인 동안 시스템은 "연결 없음" 표시기를 표시해야 합니다 (WHILE offline, system SHALL display "No connection" indicator)
```

---

## 예시 4: 선택적 패턴 (조건부 기능)

### ✅ 좋은 예시

```
사용자에게 관리자 권한이 있는 경우 시스템은 고급 설정 메뉴를 표시할 수 있습니다 (WHERE user has admin privileges, system MAY display advanced settings menu)
네트워크 속도가 1Mbps 미만인 경우 시스템은 저해상도 이미지를 제공할 수 있습니다 (WHERE network speed is below 1 Mbps, system MAY serve low-resolution images)
사용자가 위치 권한을 부여하는 경우 시스템은 주변 상점을 추천할 수 있습니다 (WHERE user grants location permission, system MAY recommend nearby stores)
사용자가 다크 모드를 활성화하는 경우 시스템은 어두운 색상 구성표를 적용할 수 있습니다 (WHERE user enables dark mode, system MAY apply dark color scheme)
사용자에게 프리미엄 구독이 있는 경우 시스템은 독점 기능을 잠금 해제할 수 있습니다 (WHERE user has premium subscription, system MAY unlock exclusive features)
```

### ❌ 나쁜 예시 (및 수정)

```
시스템은 추천을 제공할 수 있습니다 (System may provide recommendations)
→ 사용자에게 검색 기록이 있는 경우 시스템은 관련 제품을 제안할 수 있습니다 (WHERE user has browsing history, system MAY suggest related products)
→ 사용자가 개인 설정을 활성화하는 경우 시스템은 콘텐츠를 추천할 수 있습니다 (WHERE user enables personalization, system MAY recommend content)

관리자 기능이 유용할 수 있습니다 (Admin features could be useful)
→ 사용자 역할이 관리자인 경우 시스템은 감사 로그를 표시할 수 있습니다 (WHERE user role is admin, system MAY display audit logs)
→ 사용자에게 상승된 권한이 있는 경우 시스템은 시스템 설정에 액세스할 수 있습니다 (WHERE user has elevated permissions, system MAY access system settings)

시스템은 성능을 최적화할 수 있습니다 (System might optimize performance)
→ 서버 부하가 30% 미만인 경우 시스템은 자주 액세스하는 데이터를 미리 캐시할 수 있습니다 (WHERE server load is below 30%, system MAY pre-cache frequently accessed data)
→ 사용자 장치에 GPU가 있는 경우 시스템은 하드웨어 가속을 활성화할 수 있습니다 (WHERE user device has GPU, system MAY enable hardware acceleration)
```

---

## 예시 5: 제약 조건 패턴 (제한 및 오류 처리)

### ✅ 좋은 예시

```
비밀번호가 3회 실패하면 시스템은 15분 동안 계정을 잠가야 합니다 (IF password fails 3 times, system SHALL lock account for 15 minutes)
파일 크기가 10MB를 초과하면 시스템은 오류 메시지와 함께 업로드를 거부해야 합니다 (IF file size exceeds 10MB, system SHALL reject upload with error message)
API 속도 제한을 초과하면 시스템은 429 상태 코드를 반환해야 합니다 (IF API rate limit is exceeded, system SHALL return 429 status code)
세션이 30분 동안 유휴 상태이면 시스템은 세션을 종료해야 합니다 (IF session is idle for 30 minutes, system SHALL terminate session)
데이터베이스 쿼리가 5초 이상 걸리면 시스템은 시간 초과하고 오류를 기록해야 합니다 (IF database query takes longer than 5 seconds, system SHALL timeout and log error)
```

### ❌ 나쁜 예시 (및 수정)

```
로그인 실패 처리 (Handle login failures)
→ 비밀번호가 3회 실패하면 시스템은 15분 동안 계정을 잠가야 합니다 (IF password fails 3 times, system SHALL lock account for 15 minutes)
→ 계정이 잠겨 있으면 시스템은 사용자에게 잠금 해제 이메일을 보내야 합니다 (IF account is locked, system SHALL send unlock email to user)

파일 업로드 유효성 검사 (Validate file uploads)
→ 파일 확장자가 [jpg, png, pdf]에 없으면 시스템은 업로드를 거부해야 합니다 (IF file extension is not in [jpg, png, pdf], system SHALL reject upload)
→ 파일 크기가 10MB를 초과하면 시스템은 크기 제한 오류를 표시해야 합니다 (IF file size exceeds 10MB, system SHALL display size limit error)

세션 관리 (Manage sessions)
→ 세션이 만료되면 시스템은 사용자를 로그인 페이지로 리디렉션해야 합니다 (IF session expires, system SHALL redirect user to login page)
→ 세션 토큰이 유효하지 않으면 시스템은 401 오류를 반환해야 합니다 (IF session token is invalid, system SHALL return 401 error)
```

---

## 예시 6: 금지된 구문 대체 가이드

| 금지된 구문 | 컨텍스트 | EARS 대체 |
|---|---|---|
| "빠른", "신속한" | 시스템은 신속하게 응답해야 합니다 | 시스템은 요청의 95%에 대해 200ms 이내에 응답해야 합니다 |
| "안전한", "안전하게" | 시스템은 안전해야 합니다 | 시스템은 HTTPS를 시행해야 합니다 + 시스템은 bcrypt를 사용하여 비밀번호를 해시해야 합니다 |
| "사용자 친화적인" | 인터페이스는 사용자 친화적이어야 합니다 | 시스템은 입력 유효성 검사 오류를 인라인으로 표시해야 합니다 + 시스템은 자동 완성 제안을 제공해야 합니다 |
| "할 수 있다", "할 수 있었다" | 사용자는 파일을 업로드할 수 있습니다 | 사용자가 파일을 선택하면 시스템은 크기와 유형을 검증해야 합니다 |
| "~일지도 모른다", "~일 수 있다" (모호함) | 시스템은 데이터를 캐시할 수 있습니다 | 캐시가 활성화된 경우 시스템은 5분 동안 응답을 저장할 수 있습니다 |
| "~해야 한다", "~하면 좋을 것이다" | 시스템은 입력을 검증해야 합니다 | 시스템은 정의된 스키마에 대해 모든 입력을 검증해야 합니다 |
| "적절한", "올바른" | 적절한 오류 처리를 사용합니다 | 데이터베이스 오류가 발생하면 시스템은 오류를 기록하고 500 상태를 반환해야 합니다 |
| "쉽게", "간단하게" | 사용자는 설정을 쉽게 찾을 수 있습니다 | 시스템은 탐색 메뉴에 설정 링크를 표시해야 합니다 |

---

## 예시 7: 한국어 → 영어 EARS 변환

### 입력 (한국어 자연어)

```
사용자가 로그인 버튼을 클릭하면 인증 프로세스가 시작됩니다.
비밀번호가 3회 실패하면 계정이 15분간 잠깁니다.
사용자 세션이 활성화되어 있는 동안 자동 로그아웃 타이머가 표시됩니다.
관리자 권한이 있는 경우 고급 설정 메뉴가 표시될 수 있습니다.
시스템은 모든 외부 통신에 HTTPS를 사용해야 합니다.
```

### 출력 (영어 EARS)

```
WHEN user clicks login button, system SHALL initiate authentication process
IF password fails 3 times, system SHALL lock account for 15 minutes
WHILE user session is active, system SHALL display auto-logout timer
WHERE user has admin privileges, system MAY display advanced settings menu
System SHALL provide HTTPS for all external communication
```

---

## 예시 8: 측정 가능성 확인

### ❌ 측정 불가

```
"시스템은 성능이 좋아야 합니다"
→ 기준 없음, 테스트 케이스 파생 불가

"로그인이 원활하게 작동해야 합니다"
→ "원활하게"는 주관적이며 관찰 불가

"오류 처리는 견고해야 합니다"
→ "견고함"은 모호하며 성공 기준 없음
```

### ✅ 측정 가능

```
"시스템은 요청의 95%에 대해 GET /api/users에 200ms 이내에 응답해야 합니다"
→ 명확한 기준: 200ms, 95번째 백분위수, 특정 엔드포인트
→ 테스트: 응답 시간 측정, 95번째 백분위수 < 200ms 단언

"사용자가 잘못된 이메일을 제출하면 시스템은 '잘못된 이메일 형식' 메시지와 함께 400 오류를 반환해야 합니다"
→ 명확한 기준: 400 상태, 특정 오류 메시지
→ 테스트: 잘못된 이메일 POST, response.status == 400 및 response.body에 "잘못된 이메일" 포함 단언

"비밀번호가 3회 실패하면 시스템은 15분 동안 계정을 잠가야 합니다"
→ 명확한 기준: 3회 실패, 15분 잠금 기간
→ 테스트: 잘못된 비밀번호 3회 제출, account.locked == True 및 lock_duration == 900초 단언
```

---

## 예시 9: EARS 준수 전체 사양 (준수)

```markdown
# @SPEC:AUTH-001: 사용자 인증

## 유비쿼터스 요구사항
- 시스템은 JWT 기반 인증을 제공해야 합니다
- 시스템은 12라운드의 bcrypt를 사용하여 모든 비밀번호를 해시해야 합니다
- 시스템은 모든 인증 엔드포인트에 HTTPS를 시행해야 합니다

## 이벤트 기반 요구사항
- 사용자가 유효한 이메일과 비밀번호를 제출하면 시스템은 JWT 토큰을 발급해야 합니다
- 사용자가 잘못된 자격 증명을 제출하면 시스템은 401 오류를 반환해야 합니다
- 인증이 성공하면 시스템은 타임스탬프와 IP로 시도를 기록해야 합니다
- 토큰이 만료되면 시스템은 "토큰 만료" 메시지와 함께 401 오류를 반환해야 합니다

## 상태 기반 요구사항
- 사용자가 인증된 동안 시스템은 보호된 리소스에 대한 액세스를 허용해야 합니다
- 토큰이 유효한 동안 시스템은 요청 컨텍스트에 user_id를 포함해야 합니다

## 선택적 요구사항
- 새로 고침 토큰이 제공되면 시스템은 새 액세스 토큰을 발급할 수 있습니다
- 사용자가 2FA를 활성화하면 시스템은 TOTP 코드를 요구할 수 있습니다

## 제약 조건
- 비밀번호가 3회 실패하면 시스템은 15분 동안 계정을 잠가야 합니다
- 이메일 형식이 잘못된 경우 시스템은 400 오류를 반환해야 합니다
- 토큰이 누락된 경우 시스템은 401 오류를 반환해야 합니다
```

---

## 예시 10: EARS 위반 전체 사양 (미준수)

```markdown
# 사용자 인증 (TAG 없음, EARS 패턴 누락)

## 요구사항 (❌ 모두 EARS 위반)
- 시스템은 안전한 로그인을 제공해야 합니다 (모호함: "안전한")
- 사용자는 이메일과 비밀번호로 로그인할 수 있습니다 (트리거 누락: "할 수 있다")
- 로그인은 빨라야 합니다 (측정 불가: "빠른")
- 오류를 적절하게 처리합니다 (모호함: "적절하게")
- 시스템은 소셜 로그인을 지원할 수 있습니다 (모호함: "할 수 있다")
- 비밀번호 유효성 검사는 잘 작동해야 합니다 (주관적: "잘")

## 필요한 수정
→ EARS 패턴 적용
→ 금지된 구문 교체
→ 측정 가능한 기준 추가
→ TAG 블록 추가
```

**수정된 버전**: 예시 9 참조.

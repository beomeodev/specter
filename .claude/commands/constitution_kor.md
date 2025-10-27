---
description: "`plan.md`에서 프로젝트 제약 조건을 `헌법 섹션 IX`로 추출"
---

# /ms.constitution - 프로젝트 제약 조건 및 규칙 추출

spec.md 및 plan.md에서 프로젝트별 제약 조건을 추출한 다음 다음을 업데이트합니다.
1. **헌법 섹션 IX**: 기술 제약 조건 (종속성, 아키텍처, 보안)
2. **AGENTS.md**: 예제와 함께 프로젝트별 코딩 규칙 (300-500 토큰)

## 개요

이 명령은 `/ms.plan` 실행 후 다음을 추출합니다.
- **기술 제약 조건** → 헌법 섹션 IX (사용할 기술/패턴)
- **코딩 패턴** → AGENTS.md 프로젝트 규칙 (이 프로젝트에서 코드를 작성하는 방법)

**왜 /ms.plan 이후인가?**
- plan.md에는 아키텍처 결정, 기술 스택 선택 및 파일 구조가 포함되어 있습니다.
- 이는 의미 있는 프로젝트 제약 조건을 추출하는 데 필수적입니다.
- spec.md만으로는 충분한 기술적 세부 정보가 없습니다.

헌법과 AGENTS.md는 spec.md 및 plan.md에서 가져오지만 목적은 다릅니다.
- **헌법**: 상위 수준 프로젝트 규칙 및 제약 조건 (무엇을 사용할 것인가)
- **AGENTS.md**: 구체적인 코드 예제 및 검증 체크리스트 (코드를 작성하는 방법)

## 실행 단계

### 1. 헌법 읽기

`.specify/memory/constitution.md`에서 현재 헌법을 로드합니다.

### 2. 소스 문서 읽기

spec.md 및 plan.md **모두** 읽기:
- **spec.md**: 사용자 요구 사항, 기술 결정
- **plan.md**: 아키텍처 결정, 구현 제약 조건

**근거**:
- spec.md에는 사용자 대상 요구 사항 → 제약 조건 (예: "bcrypt 사용 필수")이 포함되어 있습니다.
- plan.md에는 기술/아키텍처 결정 → 제약 조건 (예: "파일 ≤500 SLOC")이 포함되어 있습니다.
- 둘 다 섹션 IX의 프로젝트 규칙에 기여합니다.

### 2.5. 적응형 제약 조건 추출 (항상 복잡함)

**이 워크플로는 항상 하위 에이전트를 사용합니다** (헌법 추출은 본질적으로 다차원적입니다).

**1단계: AGENTS.md 파일 감지**

```bash
# 어떤 AGENTS.md 파일이 존재하는지 확인
AGENTS_ROOT=$([ -f "AGENTS.md" ] && echo "1" || echo "0")
AGENTS_FRONTEND=$([ -f "frontend/AGENTS.md" ] && echo "1" || echo "0")
AGENTS_BACKEND=$([ -f "backend/AGENTS.md" ] && echo "1" || echo "0")
AGENTS_TOTAL=$((AGENTS_ROOT + AGENTS_FRONTEND + AGENTS_BACKEND))
```

**2단계: 에이전트 전략 적용**

병렬로 3개의 하위 에이전트 시작 (3개의 작업 호출이 있는 단일 메시지):

1. **constitution-extractor 에이전트**:
   ```
   "헌법 섹션 IX에 대한 spec.md 및 plan.md에서 프로젝트별 제약 조건 추출"
   ```

2. **AGENTS_Rules_Agent** (인라인 로직 - 전용 에이전트 없음):
       ```
       작업: "기존 AGENTS.md 파일에 대한 프로젝트별 코딩 규칙 생성"

       참고: AGENTS.md 생성 워크플로에 매우 특화되어 있으므로
       이것은 인라인 작업 로직으로 유지됩니다 (에이전트 파일로 변환되지 않음).

       워크플로:
       1. 어떤 AGENTS.md 파일이 존재하는지 감지 (루트, frontend/, backend/)
       2. plan.md에서 코딩 패턴 추출
       3. 기존 코드에서 구체적인 예제 찾기
       4. 규칙을 적절하게 배포:
          - 루트: 교차 기능 (API 계약, 인증 흐름, 데이터 형식)
          - 프론트엔드: 상태 관리, 구성 요소 패턴, UI 규칙
          - 백엔드: 데이터베이스 액세스, API 구현, 외부 서비스
       5. 파일당 300-500 토큰 보장
       6. 모든 규칙을 소스에 연결 (FR-XXX/STEP-XXX)
       7. 반환: 토큰 수와 함께 파일당 규칙
       ```

3. **trust-validator 에이전트 (레벨 1)**:
   ```
   "충돌 및 완전성에 대한 추출된 제약 조건 유효성 검사"

   참고: 헌법 제약 조건의 기본 구조 유효성 검사를 위해 레벨 1을 사용합니다.
   ```

**중요**: 항상 병렬로 에이전트를 시작합니다 (여러 작업 호출이 있는 단일 메시지).

**디버그 출력** (투명성을 위해):
```json
{
  "agents_md_detected": {
    "root": true,
    "frontend": true,
    "backend": false,
    "total": 2
  },
  "agents_spawned": 3,
  "tasks": [
    "섹션 IX에 대한 제약 조건 추출",
    "2개의 AGENTS.md 파일에 대한 규칙 생성",
    "제약 조건 및 규칙 유효성 검사"
  ]
}
```

### 2.6. 결과 종합

**모든 에이전트의 결과 병합**:
- Constraint_Extraction_Agent의 제약 조건
- AGENTS_Rules_Agent의 규칙 (시작된 경우)
- Validation_Agent의 유효성 검사 경고
- 식별된 모든 충돌 해결
- 헌법 섹션 IX 및 AGENTS.md 파일에 대한 최종 콘텐츠 준비

### 3. AI 기반 제약 조건 추출

**AI를 사용하여 문서의 어느 곳에서든 제약 조건 추출** (특정 섹션에 국한되지 않음):

AI 프롬프트:
```
다음 문서를 읽고 헌법 섹션 IX에 대한 프로젝트별 제약 조건을 추출하십시오.

**spec.md**:
{spec_content}

**plan.md**:
{plan_content}

다음 범주에서 제약 조건을 추출하십시오.

**기술 스택**:
✅ 필수: 언어, 프레임워크, 최소 버전
❌ 금지: 금지된 기술, 패턴

**종속성**:
✅ 필수: 필수 라이브러리, 도구, 서비스
❌ 금지: 금지된 종속성

**아키텍처**:
✅ 필수: 필수 패턴, 파일 제한, 복잡성 제한
❌ 금지: 안티 패턴, 금지된 구조

**보안**:
✅ 필수: 인증 방법, 암호화, 유효성 검사 규칙
❌ 금지: 보안 안티 패턴

**성능**:
✅ 필수: 응답 시간 제한, 처리량 요구 사항
❌ 금지: 성능 안티 패턴

**지침**:
- 문서의 어느 곳에서든 제약 조건 추출 (특정 섹션에 국한되지 않음)
- 다음 구문 찾기: "must use", "required", "forbidden", "shall not", "prohibited"
- 버전 요구 사항 찾기: ">= 18", "≥ 13.0"
- 아키텍처 결정 찾기: "files ≤500 SLOC", "functions ≤100 lines"
- 사용자 대상 기능 무시 (헌법이 아닌 사양에 속함)
- 영어로만 작성

출력 형식:
```markdown
## IX. 프로젝트별 제약 조건

*2025-10-10에 /ms.constitution에 의해 spec.md 및 plan.md에서 자동 생성됨*

### 기술 스택

✅ **필수**:
- {제약 조건 1}
- {제약 조건 2}

❌ **금지**:
- {제약 조건 1}

### 종속성

...
```
```

### 4. 기존 섹션 IX와 병합

**섹션 IX가 헌법에 이미 존재하는 경우**:
- 기존 제약 조건 추출
- 새로 추출된 제약 조건과 병합
- 중복 제거 (충돌 시 최신 버전 유지)
- 수동 추가 사항 보존 (사양/계획에서 가져오지 않은 제약 조건)

**병합 로직**:
```typescript
function mergeConstraints(existing: Constraint[], extracted: Constraint[]): Constraint[] {
  const merged = [...existing];

  for (const newConstraint of extracted) {
    const existingIndex = merged.findIndex(c =>
      c.category === newConstraint.category &&
      similarText(c.text, newConstraint.text) > 0.8  // 80% 유사성
    );

    if (existingIndex === -1) {
      // 새로운 제약 조건 - 추가
      merged.push(newConstraint);
    } else {
      // 중복 - 최신 유지 (최신 사양/계획에서 추출됨)
      merged[existingIndex] = newConstraint;
    }
  }

  return merged;
}
```

### 5. AGENTS.md에 대한 프로젝트별 규칙 추출

**헌법 제약 조건 추출 후, AGENTS.md 파일에 대한 프로젝트별 코딩 규칙 추출**

#### 대상 파일 (자동 감지)

기존 AGENTS.md 파일에만 규칙 배포:

1. **루트 AGENTS.md** (존재하는 경우 항상 업데이트)
   - 교차 기능 규칙: API 계약, 인증 흐름, 데이터 형식

2. **frontend/AGENTS.md** (`frontend/` 디렉토리가 존재하는 경우)
   - 프론트엔드별: 상태 관리, 구성 요소 패턴, UI 규칙

3. **backend/AGENTS.md** (`backend/` 디렉토리가 존재하는 경우)
   - 백엔드별: 데이터베이스 액세스, API 구현, 외부 서비스

#### 파일당 추출할 내용

**루트 AGENTS.md** (교차 기능):
- 양측이 따라야 하는 API 계약
- 인증/권한 부여 흐름
- 공유 데이터 형식 (JSON 스키마)
- 오류 코드 규칙

**frontend/AGENTS.md** (존재하는 경우):
- 상태 관리 패턴 (Redux, Zustand 등)
- 구성 요소 구조 규칙
- API 클라이언트 구성
- 사양의 UI/UX 제약 조건

**backend/AGENTS.md** (존재하는 경우):
- 데이터베이스 액세스 패턴 (리포지토리, ORM 사용)
- API 엔드포인트 구현
- 외부 서비스 통합 (Stripe, SendGrid 등)
- 백그라운드 작업 패턴

**✅ 추출**: 기술 스택, 아키텍처 패턴, 보안 규칙, 성능 목표
**❌ 추출하지 않음**: 비즈니스 로직, 일반 원칙, 타임라인, 비코딩 결정

#### 토큰 예산 제약 조건

**AGENTS.md 파일당**: 300-500 토큰

**제한 초과 시**: 가장 중요도가 낮은 범주를 제거하거나 예제를 단축

#### 형식 (모든 AGENTS.md 파일에 동일)

각 AGENTS.md 끝에 추가:

```markdown
---

## 🎯 프로젝트별 규칙

> 출처: spec.md, plan.md | 업데이트: {날짜}

### {범주}
**{규칙 이름}** (사양: FR-XXX 또는 계획: STEP-XXX)
```{language}
# 코드 예제 (≤10줄)
```
확인: [ ] {확인 지점}

---
```

**규칙당**: 한 문장 + 5-10줄 코드 + 소스 링크 (FR-XXX/STEP-XXX) + 1-2개 확인

#### AI 추출 프롬프트

```
spec.md 및 plan.md에서 프로젝트별 코딩 규칙을 추출하십시오.
AGENTS.md 파일에 배포하십시오 (존재하는 경우):

1. 루트 AGENTS.md - 교차 기능 (API 계약, 인증 흐름)
2. frontend/AGENTS.md - 프론트엔드별 (상태, 구성 요소, UI)
3. backend/AGENTS.md - 백엔드별 (데이터베이스, API, 서비스)

**문서**:
{spec_content}
{plan_content}

**파일당 요구 사항**:
- 각 300-500 토큰
- 소스에 링크 (FR-XXX/STEP-XXX)
- 형식: 범주 > 규칙 > 코드 (≤10줄) > 확인
- 관련 규칙만 (강제 배포 없음)

**예제** (사양: "1시간 만료 JWT 인증"):

루트 AGENTS.md:
### 인증 흐름
**JWT 토큰** (FR-AUTH-001)
- 액세스: 1시간 만료
- 갱신: 30일 만료

frontend/AGENTS.md:
### API 클라이언트
**인증 헤더** (FR-AUTH-001)
```typescript
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
```
확인: [ ] 401 시 토큰 자동 갱신

backend/AGENTS.md:
### 인증
**JWT 구성** (FR-AUTH-001)
```python
ACCESS_TOKEN_EXPIRE = 3600  # 1시간
```
확인: [ ] JWT_SECRET으로 서명된 토큰

**파일당 보고서**: 토큰 수, 추가된 규칙
```

#### AGENTS.md 업데이트 프로세스

각 기존 AGENTS.md 파일 (루트, frontend/, backend/)에 대해:

1. **파일 존재 확인** (없으면 건너뛰기)
2. **"🎯 프로젝트별 규칙" 섹션 확인**
   - 존재하면: 전체 섹션 교체
   - 없으면: 끝에 추가
3. AI 프롬프트를 사용하여 **규칙 추출**
4. **유효성 검사**: 300-500 토큰, 소스 링크, ≤10줄 코드
5. **파일 업데이트**

### 6. 헌법 업데이트

병합된 제약 조건으로 섹션 IX 교체 또는 생성:

```markdown
## IX. 프로젝트별 제약 조건

*2025-10-10에 /ms.constitution에 의해 spec.md 및 plan.md에서 자동 생성됨*

### 기술 스택

✅ **필수**:
- Node.js ≥18
- 엄격 모드의 TypeScript
- 테스트용 Vitest

⚠️ **주의해서 사용**: 
- 사용자 지정 AST 파서 (확립된 도구 선호: ESLint, TSC API, ast stdlib)
- 복잡한 프레임워크 (plan.md에 정당화 필요)

✅ **안전한 AST 사용**:
- 읽기 전용 분석 (ESLint, 복잡성 메트릭)
- 승인된 도구: @typescript-eslint/parser, ast (Python), esprima

### 종속성

✅ **필수**:
- TAG 작업용 ripgrep ≥13.0
- 경고 없는 ESLint 정책

❌ **금지**:
- 불필요한 외부 종속성

### 아키텍처

✅ **필수**:
- 파일 ≤500 SLOC (코드 파일 - 문서는 제한 없음)
- 함수 ≤100줄
- 함수당 복잡성 ≤10
- 안전 모델을 따르는 AST 파서 허용 (읽기 전용, 샌드박스 등)

### 보안

✅ **필수**:
- `.env`는 `.gitignore`에 있어야 함
- 모든 사용자 입력에 대한 입력 유효성 검사
- 비밀번호 해싱용 bcrypt

### 성능

✅ **필수**:
- API 응답 시간 < 200ms (p95)
- 데이터베이스 쿼리 < 100ms
```

### 7. 루트 AGENTS.md 업데이트

**루트 AGENTS.md 업데이트** (존재해야 함):

1. **PROJECT_RULES 슬롯 검색**:
   ```bash
   grep -n "PROJECT_RULES_START" AGENTS.md
   ```

2. **PROJECT_RULES 슬롯이 발견된 경우** (예상되는 경우):
   - AGENTS.md 읽기
   - 슬롯 시작 찾기: `<!-- PROJECT_RULES_START -->`
   - 슬롯 끝 찾기: `<!-- PROJECT_RULES_END -->`
   - 마커 사이의 **콘텐츠를 업데이트된 {SECTION_IX_CONTENT}로 교체**
   - old_string (주석을 포함한 전체 블록) → new_string (업데이트된 블록)으로 Edit 도구 사용
   - 예제:
     ```markdown
     <!-- PROJECT_RULES_START -->
     {SECTION_IX_CONTENT}
     <!-- PROJECT_RULES_END -->
     ```

3. **PROJECT_RULES 슬롯이 발견되지 않은 경우** (레거시 대체):
   - AGENTS.md 읽기
   - 삽입 지점 찾기: 최종 `---` 구분자 앞
   - **새 PROJECT_RULES 슬롯 삽입**:
     ```markdown
     <!-- PROJECT_RULES_START -->
     <!-- 이 섹션은 /ms.constitution에 의해 프로젝트별 규칙으로 자동 채워집니다 -->
     <!-- 이 섹션을 수동으로 편집하지 마십시오 -->
     {SECTION_IX_CONTENT}
     <!-- PROJECT_RULES_END -->
     ```
   - 적절한 위치에 삽입하기 위해 Edit 도구 사용


### 8. 보고서 출력

```json
{
  "constraints_extracted": {
    "from_spec": 12,
    "from_plan": 8,
    "total_new": 15,
    "merged_duplicates": 5
  },
  "agents_md_created": true,
  "section_ix_updated": true,
  "constitution_path": ".specify/memory/constitution.md",
  "agents_md_path": "AGENTS.md"
}
```

표시 (한국어):
```
✅ 헌법 섹션 IX + AGENTS.md 생성 완료!

📊 제약사항 추출 (헌법 섹션 IX):
- spec.md에서: 12개
- plan.md에서: 8개
- 신규 추가: 15개
- 중복 병합: 5개

📄 업데이트된 파일:
- ✅ .specify/memory/constitution.md (섹션 IX 완성)
- ✅ AGENTS.md (프로젝트 코딩 규칙)

🎯 다음 단계:
1. 헌법 섹션 IX 검토
2. AGENTS.md 검토
3. `/ms.tasks` 실행 (구현 작업 생성)

💡 참고:
- AI 에이전트는 AGENTS.md를 통해 헌법을 자동 참조합니다
- 살아있는 문서는 `/ms.implement` 실행 시 자동 생성됩니다
```

## 오류 처리

### 오류 1: 헌법을 찾을 수 없음

**증상**: `.specify/memory/constitution.md` 누락

**메시지**:
```
❌ 오류: 헌법을 찾을 수 없습니다.

예상: .specify/memory/constitution.md

프로젝트 헌법을 만들려면 먼저 `/ms.init`을 실행하십시오.
```

**종료**: 코드 1

### 오류 2: 사양 또는 계획을 찾을 수 없음

**증상**: spec.md 또는 plan.md가 존재하지 않음

**메시지**:
```
❌ 오류: 소스 문서를 찾을 수 없습니다.

필수 파일:
- specs/{SPEC_ID}/spec.md (누락)
- specs/{SPEC_ID}/plan.md (누락)

다음을 실행하십시오:
1. `/ms.specify`를 실행하여 spec.md 생성
2. `/ms.plan`을 실행하여 plan.md 생성

그런 다음 `/ms.constitution`을 다시 실행하십시오.
```

**종료**: 코드 1

### 오류 3: 제약 조건을 찾을 수 없음

**증상**: AI가 spec.md 및 plan.md에서 0개의 제약 조건을 추출

**메시지**:
```
⚠️ 경고: 프로젝트별 제약 조건을 찾을 수 없습니다.

spec.md 및 plan.md에는 명시적인 제약 조건이 포함되어 있지 않습니다.

일반적인 누락된 제약 조건:
- 기술 스택 (Node.js 버전, Python 버전)
- 필수 종속성 (라이브러리, 도구)
- 아키텍처 결정 (파일 크기 제한, 패턴)
- 보안 요구 사항 (인증 방법, 암호화)

다음을 원하십니까?
1. spec.md 또는 plan.md에 제약 조건을 수동으로 추가하고 `/ms.constitution`을 다시 실행
2. 섹션 IX를 비워 둡니다 (기본 헌법만 사용).
3. 섹션 IX 생성 건너뛰기
```

**조치**: 사용자에게 선택을 요청

### 오류 4: 충돌하는 제약 조건

**증상**: spec.md는 "PostgreSQL 사용"을, plan.md는 "MongoDB 사용"을 명시

**메시지**:
```
⚠️ 제약 조건 충돌 감지됨

spec.md: "필수: PostgreSQL 데이터베이스"
plan.md: "필수: MongoDB 데이터베이스"

충돌을 해결하십시오:
1. 충돌을 제거하기 위해 spec.md 또는 plan.md 편집
2. 해결 후 `/ms.constitution` 다시 실행

현재는 최신 (plan.md) 제약 조건으로 진행합니다.
```

**조치**: plan.md 제약 조건 사용 (워크플로에서 더 최신이므로)

### 오류 6: 토큰 예산 초과 (파일당)

**증상**: 파일에 대해 추출된 규칙이 500토큰을 초과

**메시지**:
```
⚠️ 토큰 예산 초과: backend/AGENTS.md

추출된 규칙: 720 토큰 (제한: 500)

예산에 맞게 자동 트리밍:
- 제거됨: 성능 모니터링 (80 토큰)
- 제거됨: 오류 처리 (90 토큰)
- 최종: 450 토큰

backend/AGENTS.md를 검토하고 필요한 경우 제거된 범주를 수동으로 추가하십시오.
```

**조치**: 예산에 맞게 파일당 가장 중요도가 낮은 범주를 자동 트리밍

## 다음 단계

`/ms.constitution` 이후:
1. 헌법 섹션 IX 검토 (프로젝트 제약 조건)
2. AGENTS.md 검토 (프로젝트별 코딩 규칙)
3. `/ms.tasks` 실행 (구현 작업 생성)
4. 헌법 + 에이전트 규칙 완료 ✅

**참고**: `/ms.constitution`은 `/ms.plan` 이후에 실행되어야 합니다 (plan.md는 제약 조건 추출에 필요).

## 참고

### 헌법 (섹션 IX)
- **AI 기반 추출**: 엄격한 섹션 구조 불필요
- **소스**: spec.md + plan.md
- **병합 전략**: 수동 추가 사항 보존, 중복 제거, 최신 유지
- **범위**: 프로젝트별 제약 조건 (섹션 I-XIII는 보편적)

### AGENTS.md (프로젝트별 규칙)
- **다중 파일 지원**: 루트, frontend/, backend/ (자동 감지)
- **토큰 예산**: 파일당 300-500 (엄격하게 시행)
- **콘텐츠**: 코딩 패턴만 (비즈니스 로직 없음)
- **소스 추적**: 모든 규칙이 FR-XXX/STEP-XXX에 연결됨
- **업데이트 전략**: "🎯 프로젝트별 규칙" 섹션 교체 (멱등성)
- **파일 생성 없음**: 기존 AGENTS.md 파일만 업데이트

## 구현 세부 정보

**도구**:
- 읽기: spec.md, plan.md, constitution.md, AGENTS.md (루트, frontend/, backend/)
- 편집: constitution.md (섹션 IX), AGENTS.md 파일 (프로젝트별 규칙 섹션)

**파일 크기 목표**:
- 헌법 섹션 IX: ≤200줄 (기본 템플릿 제외)
- 각 AGENTS.md 프로젝트 규칙: 300-500 토큰 (≈60-100줄)

**처리 순서**:
1. 헌법 제약 조건 추출 (섹션 IX)
2. 기존 AGENTS.md 파일 자동 감지
3. 감지된 각 파일에 대한 규칙 추출
4. 헌법 업데이트
5. AGENTS.md 파일 업데이트
6. 결합된 결과 보고

<div align="center">
    <h1>👻 SPECTER</h1>
    <h3><em>AI와 함께하는 고품질 소프트웨어 개발</em></h3>
</div>

<p align="center">
    <strong>Specification-Progressive Enforcement & Constitution-based Traceability, Evolutionary Review</strong>
</p>

<p align="center">
    사양 기반 점진적 강제 · 헌법 기반 추적성 · 진화적 리뷰
</p>

---

## 목차

- [📦 설치](#-설치)
- [🤔 SPECTER란 무엇인가?](#-specter란-무엇인가)
- [⚡ 빠른 시작](#-빠른-시작)
- [📚 핵심 철학](#-핵심-철학)
- [🎯 SPECTER의 7가지 원칙](#-specter의-7가지-원칙)
- [✨ 핵심 특징](#-핵심-특징)
- [🔧 명령어 참조](#-명령어-참조)
- [🏗️ 워크플로우 아키텍처](#️-워크플로우-아키텍처)
- [📁 프로젝트 구조](#-프로젝트-구조)
- [💡 언제 사용하나요?](#-언제-사용하나요)
- [🆚 기존 방식과의 비교](#-기존-방식과의-비교)
- [🛠️ 기술 스택](#️-기술-스택)
- [📖 상세 문서](#-상세-문서)
- [🙏 Credits](#-credits)

---

## 📦 설치

### 새 프로젝트에 SPECTER 설치

```bash
npx degit beomeodev/specter my-new-project
cd my-new-project
npm install  # 또는 uv pip install -e .
```

이 명령어는 SPECTER 템플릿을 복사하여 새 프로젝트를 생성합니다 (`.git` 히스토리 제외).

**프로젝트 구조**:
```
my-new-project/          ← 생성됨
├── .claude/commands/    ← 14개 슬래시 커맨드
├── templates/           ← Constitution 템플릿
├── src/                 ← 소스 코드
├── AGENTS.md            ← AI 코딩 규칙
└── README.md            ← 이 파일
```

### 설치 후 첫 단계

```bash
# 1. 프로젝트 초기화
/ms.init

# 2. 첫 기능 사양 작성
/ms.specify my-first-feature
```

---

## 🤔 SPECTER란 무엇인가?

**SPECTER**는 AI 에이전트와의 협업에서 발생하는 품질 문제를 **시스템적으로 감시하고 차단**하는 개발 프레임워크입니다.

SPECTER는 7가지 핵심 원칙의 조합으로 탄생했습니다:

```
S - Specification-driven    사양 주도 개발
P - Progressive             점진적 검증 (빠른 실패, 빠른 수정)
E - Enforcement             헌법 기반 자동 강제
C - Constitution-based      단일 진실 출처 거버넌스
T - Traceability            TAG 체인을 통한 완전 추적성
E - Evolutionary            진화적 개선 사이클
R - Review                  자동화된 품질 리뷰
```

### 왜 SPECTER인가?

전통적인 소프트웨어 개발에서 **코드는 왕**이었고, 사양은 단지 버려지는 비계였습니다. SPECTER는 이를 뒤집습니다:

- **사양이 실행 가능**해지고
- **검증이 자동화**되며
- **AI가 헌법을 준수**하고
- **모든 것이 추적 가능**해집니다

마치 유령(Specter)처럼, SPECTER는 **보이지 않게 프로젝트 전체를 감시**하며, 품질 문제가 발생하기 전에 차단합니다.

---

## ⚡ 빠른 시작

### 1. 프로젝트 초기화

```bash
/ms.init
```

**생성되는 것**:
- `.specify/memory/constitution.md` - 프로젝트 헌법 (14개 섹션)
- `.claude/commands/` - 14개 슬래시 커맨드 (14 My-Spec + 8 Spec-Kit 래퍼)
- `AGENTS.md` - AI 코딩 규칙
- `templates/` - Constitution 템플릿

### 2. 사양 작성 (Specification-driven)

```bash
/ms.specify user-authentication
```

**AI가 자동으로**:
- EARS 패턴 변환 (WHEN/WHILE/WHERE/IF/SHALL)
- 복잡도 분석 후 서브 에이전트 병렬 실행
- `specs/001-user-authentication/spec.md` 생성

### 2.5. 요구사항 명확화 (선택, 권장)

```bash
/ms.clarify
```

**AI가 자동으로**:
- 불명확한 요구사항 질문
- 답변을 spec.md에 기록
- 요구사항 완전성 검증

**또는 체크리스트 검증**:

```bash
/ms.checklist
```

**생성되는 것**:
- 요구사항 완전성 체크리스트 ("영어를 위한 단위 테스트")
- 명확성, 일관성 검증 항목

### 3. 구현 계획

```bash
/ms.plan
```

**AI가 자동으로**:
- TRUST 원칙 적용 (파일 ≤500 SLOC, 함수 ≤100 LOC)
- Simplicity-First 아키텍처 설계
- `plan.md` 생성

### 4. 헌법 추출 (Constitution-based)

```bash
/ms.constitution
```

**자동으로**:
- spec.md + plan.md에서 제약사항 추출
- Constitution Section IX 업데이트
- AGENTS.md 프로젝트 규칙 추가

### 5. 태스크 생성 (Traceability)

```bash
/ms.tasks
```

**생성되는 것**:
- TAG ID 자동 할당 (AUTH-001, USER-001 등)
- TAG 체인: `@SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001`
- `tasks.md` 생성

### 6. 품질 검증 (Progressive)

```bash
/ms.analyze
```

**3단계 검증**:
```
Level 1: Structure  → CRITICAL 위반 시 즉시 차단
Level 2: Quality    → CRITICAL 위반 시 즉시 차단
Level 3: Deep       → HIGH/MEDIUM은 경고
```

### 7. 구현

```bash
/ms.implement
```

**AI가 자동으로**:
- Constitution + AGENTS.md 자동 준수
- TAG 블록 자동 삽입
- Context7 MCP로 최신 API 사용
- TDD (테스트 먼저 작성)

### 8. 진화적 리뷰 (Evolutionary Review)

```bash
/ms.review
```

**검증 항목**:
- ✅ 명명 규칙 (도메인 용어)
- ✅ 아키텍처 일관성
- ✅ 성능 이슈 (N+1 쿼리)
- ✅ 보안 심층 분석
- ✅ 테스트 품질

**ultrathink 패턴 분석**:
```
🔍 SYSTEMIC ISSUES: 3
1. Inconsistent Error Handling (5 occurrences)
   ROOT CAUSE → BATCH FIX (2h) → ROI 286%
```

### 9. 완료

```bash
/fin
```

**자동으로**:
1. `docs/dev_daily.md` 업데이트
2. CI 체크 (black, ruff, pytest)
3. Git 커밋 + 푸시

---

## 📚 핵심 철학

SPECTER는 **감시자(Specter)**로서 다음 원칙을 따릅니다:

### 1. 사양 우선 개발 (Specification-First)

코드보다 **사양이 먼저**입니다. 사양은 실행 가능한 계약이 되어야 합니다.

```
❌ "로그인 기능 만들어줘"
✅ "WHEN 사용자가 로그인 버튼 클릭, system SHALL 이메일/비밀번호 검증"
```

### 2. 점진적 강제 (Progressive Enforcement)

**빠른 실패(Fail Fast)**를 통해 문제를 조기에 차단합니다.

```
Level 1 실패 → Level 2 실행 안 됨
Level 2 실패 → Level 3 실행 안 됨
CRITICAL 위반 → 구현 차단
```

### 3. 헌법 기반 거버넌스 (Constitutional Governance)

모든 규칙은 **Constitution**에 집중됩니다. AI는 헌법을 읽고 자동으로 준수합니다.

```
.specify/memory/constitution.md
├── Section I    : Test-First Development (절대 규칙)
├── Section II   : Simplicity-First Architecture
├── Section IV   : EARS Requirements Standard
├── Section V    : TRUST 5 Principles
└── Section IX   : Project-Specific Constraints (자동 생성)
```

### 4. 완전 추적성 (Complete Traceability)

TAG 시스템으로 **요구사항 → 테스트 → 코드**를 완전히 연결합니다.

```typescript
/**
 * @SPEC:AUTH-001 User Authentication
 * @TEST:AUTH-001 tests/auth.test.ts::should_authenticate_user
 * @CODE:AUTH-001
 */
export class AuthService {
  // 구현
}
```

### 5. 진화적 개선 (Evolutionary Refinement)

한 번에 완벽할 수 없습니다. **점진적 개선**을 통해 품질을 향상시킵니다.

```
specify → clarify → plan → constitution → tasks → analyze → implement → review → fin
   ↓         ↓         ↓          ↓           ↓        ↓          ↓          ↓
 사양 작성  명확화   계획 수립   헌법 추출   태스크화   검증     구현      리뷰
```

### 6. 자동화된 감시 (Automated Surveillance)

SPECTER는 **유령처럼 보이지 않게** 프로젝트를 감시합니다:

- Constitution 자동 주입 (hook)
- TAG 무결성 자동 검증 (ripgrep)
- ultrathink 패턴 자동 탐지
- 3레벨 TRUST 자동 검증

---

## 🎯 SPECTER의 7가지 원칙

### S - Specification-driven (사양 주도)

**원칙**: 모든 개발은 formal specification에서 시작합니다.

**적용**:
- EARS 패턴 (WHEN/WHILE/WHERE/IF/SHALL)
- `spec.md` 필수
- 영어 문서화

**Why**: 명확한 사양이 없으면 AI도 혼란스러워합니다.

---

### P - Progressive (점진적 검증)

**원칙**: 3단계 검증으로 빠르게 실패합니다.

**적용**:
```
Level 1: Structure (CRITICAL만)
  ↓ 통과 시
Level 2: Quality (CRITICAL만)
  ↓ 통과 시
Level 3: Deep (HIGH/MEDIUM/LOW)
```

**Why**: 나중에 발견된 문제는 수정 비용이 10배 증가합니다.

---

### E - Enforcement (자동 강제)

**원칙**: Constitution이 규칙을 자동으로 강제합니다.

**적용**:
- AI가 모든 명령어 실행 시 Constitution 참조
- CRITICAL 위반 시 구현 차단
- AGENTS.md 자동 업데이트

**Why**: 사람은 잊어버리지만, 시스템은 잊지 않습니다.

---

### C - Constitution-based (헌법 기반)

**원칙**: 단일 진실 출처 (Single Source of Truth)

**적용**:
- `.specify/memory/constitution.md` 14개 섹션
- Section IX는 프로젝트별 자동 추출
- AGENTS.md는 AI 코딩 규칙

**Why**: 규칙이 산재되면 일관성이 깨집니다.

---

### T - Traceability (추적성)

**원칙**: 요구사항부터 코드까지 완전 추적

**적용**:
- TAG 체인: `@SPEC:ID → @TEST:ID → @CODE:ID`
- 도메인별 자동 ID 생성
- ripgrep 기반 고속 스캔

**Why**: "이 코드가 왜 있지?"라는 질문이 없어집니다.

---

### E - Evolutionary (진화적)

**원칙**: 점진적 개선 사이클

**적용**:
- `/ms.clarify`로 사양 개선
- `/ms.review`로 코드 품질 개선
- `/ms.constitution`으로 규칙 자동 진화

**Why**: 완벽은 한 번에 오지 않습니다.

---

### R - Review (자동 리뷰)

**원칙**: AI 기반 자동 코드 리뷰

**적용**:
- 명명 규칙, 아키텍처, 성능, 보안, 테스트 검증
- **ultrathink 패턴 분석** (시스템적 이슈 탐지)
- 자동 수정 제안 (N+1 쿼리 등)

**Why**: 사람은 피곤하지만, AI는 24/7 일합니다.

---

## ✨ 핵심 특징

### 🏛️ Constitution 기반 거버넌스

**단일 진실 출처**:
```
.specify/memory/constitution.md (14 sections)
├── I-VIII : Universal Rules (모든 프로젝트 공통)
└── IX     : Project-Specific (자동 추출)
```

**자동 적용**:
- AI가 모든 명령어 실행 시 Constitution 자동 참조
- Section IX는 `spec.md` + `plan.md`에서 자동 추출
- AGENTS.md는 프로젝트 코딩 규칙 자동 업데이트

### 🏷️ TAG 추적 시스템

**완전 추적성**:
```
@SPEC:AUTH-001 (spec.md의 FR-1)
    ↓
@TEST:AUTH-001 (tests/auth.test.ts::should_authenticate_user)
    ↓
@CODE:AUTH-001 (src/services/auth.service.ts::AuthService)
```

**도메인별 자동 ID**:
- AUTH-001, AUTH-002 (Authentication)
- USER-001, USER-002 (User Management)
- PAY-001, PAY-002 (Payment)

**ripgrep 기반 고속 스캔**:
```bash
rg '@SPEC:AUTH-' --count  # 0.5초에 10,000 파일 스캔
```

### ✅ TRUST 3단계 검증

**Progressive Validation**:
```
Level 1: Structure (CRITICAL)
  ✓ tests/ 디렉토리 존재
  ✓ .env in .gitignore
  ✓ 파일 ≤500 SLOC
  ✗ CRITICAL 위반 → 즉시 차단

Level 2: Quality (CRITICAL)
  ✓ 테스트 실행 성공
  ✓ 린트 0 경고
  ✓ 타입 체크 통과
  ✗ CRITICAL 위반 → 즉시 차단

Level 3: Deep (HIGH/MEDIUM/LOW)
  ✓ 커버리지 ≥85%
  ✓ 복잡도 ≤10
  ✓ TAG 무결성
  ⚠ HIGH/MEDIUM → 경고만
```

### 🤖 AI 협업 최적화

**서브 에이전트 자동 실행**:
```
복잡도 높음 → 3개 병렬 실행
├── Pattern_Search_Agent (기존 패턴 검색)
├── Library_Research_Agent (Context7 MCP)
└── Dependency_Analysis_Agent (통합 분석)

복잡도 낮음 → 단일 실행
```

**Context7 MCP 통합**:
```python
# AI 지식 컷오프 문제 해결!
lib_id = mcp__context7__resolve_library_id("fastapi")
docs = mcp__context7__get_library_docs(lib_id, topic="background tasks")
```

**ultrathink 패턴 분석**:
```
🔍 SYSTEMIC ISSUES DETECTED: 3

1. Inconsistent Error Handling
   📊 5 occurrences across 3 services

   5-WHY ROOT CAUSE:
   Why? → Different error patterns in each service
   Why? → No team error handling convention
   Why? → Missing from AGENTS.md
   Why? → Not extracted during /ms.constitution
   Why? → Error patterns not in spec.md/plan.md

   PREVENTION: Add error handling convention to Constitution Section IX

   BATCH FIX OPPORTUNITY:
   - Effort: 2 hours
   - Prevents: 10 hours/month of error handling bugs
   - ROI: 286%
```

---

## 🔧 명령어 참조

### 핵심 명령어 (필수)

| 명령어 | 설명 | 생성 파일 |
|-------|------|----------|
| `/ms.init` | 프로젝트 초기화 | Constitution, AGENTS.md |
| `/ms.specify` | 사양 작성 (EARS) | `specs/{id}/spec.md` |
| `/ms.plan` | 구현 계획 (TRUST) | `specs/{id}/plan.md` |
| `/ms.constitution` | 헌법 추출 | Constitution Section IX |
| `/ms.tasks` | 태스크 생성 | `specs/{id}/tasks.md` |
| `/ms.analyze` | TRUST 검증 (3레벨) | `.specify/warnings.log` |
| `/ms.implement` | 구현 (TAG 자동) | 코드 + TAG 블록 |

### 선택적 명령어

| 명령어 | 설명 | 사용 시점 |
|-------|------|----------|
| `/ms.clarify` | 요구사항 명확화 (구조화된 질의응답) | `/ms.specify` 후, `/ms.plan` 전 |
| `/ms.checklist` | 요구사항 완전성 체크리스트 생성 ("영어 단위 테스트") | `/ms.specify` 후, `/ms.plan` 전 |
| `/ms.review` | 코드 리뷰 (ultrathink 패턴 분석) | `/ms.implement` 후 |
| `/ms.up-docs` | Living Docs 업데이트 | 수동 수정 후 |
| `/fin` | 완료 (커밋+푸시) | 모든 작업 완료 후 |
| `/finq` | 빠른 완료 (CI 없음) | 개발 중 |

### 전체 워크플로우

```bash
# 1. 초기화
/ms.init

# 2. 사양 작성
/ms.specify user-authentication

# 3. 명확화 (선택)
/ms.clarify & /ms.checklist

# 4. 구현 계획
/ms.plan

# 5. 헌법 추출
/ms.constitution

# 6. 태스크 생성
/ms.tasks

# 7. 품질 검증
/ms.analyze

# 8. 구현
/ms.implement

# 9. 코드 리뷰
/ms.review

# 10. 완료
/fin
```

---

## 🏗️ 워크플로우 아키텍처

### Agent와 Skills의 관계

SPECTER는 **2단계 실행 모델**을 사용합니다:

```
Main Agent (Sonnet/Haiku)
    ↓ 호출
Sub-Agent (Task tool) 또는 Skill (자동 트리거)
    ↓ 내부 모델
Haiku/Sonnet/Opus (복잡도에 따라 선택)
```

**핵심 개념**:
- **Main Agent**: 명령어를 실행하는 주체 (Claude Code)
- **Sub-Agent**: Task tool로 명시적 호출 (복잡한 작업)
- **Skill**: 자동 트리거 (패턴 검증, 문서화)
- **Model**: 각 Agent/Skill이 사용하는 Claude 모델
  - **Haiku** = 빠름, 비용 효율
  - **Sonnet** = 깊은 추론, 복잡한 코드
  - **Opus** = 최고 수준 아키텍처 설계

---

### 전체 워크플로우 매핑

| 단계 | 명령어 | 역할 | Main Agent | Sub-Agent | Skills 사용 | 생성 파일 |
|------|--------|------|-----------|-----------|------------|----------|
| **0** | `/ms.init` | 프로젝트 초기화, Constitution 설치 | Sonnet | - | - | `.specify/memory/constitution.md`, `AGENTS.md` |
| **1** | `/ms.specify` | EARS 기반 사양 작성 | Sonnet | **spec-builder** (Sonnet) | **ms-foundation-ears** (Haiku) | `specs/001-{feature}/spec.md` |
| **2** | `/ms.clarify` | 요구사항 명확화 (구조화된 질의응답) | Sonnet | - | **ms-foundation-ears** (Haiku) | `spec.md` 업데이트 |
| **3** | `/ms.checklist` | 요구사항 완전성 체크리스트 생성 | Haiku | - | **ms-foundation-ears** (Haiku) | `specs/{id}/checklist.md` |
| **4** | `/ms.plan` | 구현 계획 (아키텍처 설계) | Opus | **implementation-planner** (Opus)<br>**library-researcher** (Haiku)<br>**codebase-explorer** (Haiku) | **ms-foundation-constitution** (Haiku) | `specs/{id}/plan.md` |
| **5** | `/ms.constitution` | spec.md/plan.md → Constitution IX 추출 | Haiku | **constitution-extractor** (Haiku) | - | `.specify/memory/constitution.md` Section IX |
| **6** | `/ms.tasks` | TAG ID 생성, 태스크 분해 | Sonnet | - | **ms-workflow-tag-manager** (Haiku) | `specs/{id}/tasks.md` |
| **7** | `/ms.analyze` | TRUST 3단계 검증 | Haiku | **tag-auditor** (Haiku)<br>**trust-validator** (Haiku) | **ms-foundation-trust** (Haiku)<br>**ms-foundation-constitution** (Haiku) | `.specify/warnings.log` |
| **8** | `/ms.implement` | TDD 구현, TAG 자동 삽입 | Sonnet | **tdd-implementer** (Sonnet) | **ms-workflow-tag-manager** (Haiku)<br>**ms-lang-{language}** (Haiku) | 코드 + TAG 블록 |
| **9** | `/ms.review` | 코드 품질 리뷰 (ultrathink 패턴) | Opus | **integration-designer** (Opus) | **ms-foundation-constitution** (Haiku)<br>**ms-domain-{domain}** (Haiku) | `docs/review/{timestamp}.md` |
| **10** | `/ms.up-docs` | Living Document 동기화 | Haiku | **doc-updater** (Haiku) | **ms-workflow-living-docs** (Haiku) | `docs/dev_daily.md`, `docs/api/*.md`, `README.md` |
| **11** | `/fin`<br>`/finq` | 완료 (`/fin`: CI 포함, `/finq`: CI 생략) | Sonnet<br>(Haiku) | **quality-gate** (Haiku) - `/fin`만<br>**doc-updater** (Haiku) - 공통 | - | `docs/dev_daily.md` + Git commit + push |

---

### Model 선택 기준

| Agent/Skill | Model | 이유 |
|------------|-------|------|
| **integration-designer** | **Opus** | 복잡한 통합 전략, 시스템적 이슈 탐지 (ultrathink), 아키텍처 설계 |
| **implementation-planner** | **Opus** | 최고 수준 아키텍처 설계, 트레이드오프 판단 |
| **spec-builder** | Sonnet | 깊은 도메인 이해 + EARS 패턴 적용 |
| **tdd-implementer** | Sonnet | 복잡한 코드 작성 + 리팩토링 |
| **debug-helper** | Sonnet | 에러 추론, 근본 원인 분석 |
| **codebase-explorer** | Haiku | Glob/Grep 패턴 검색 |
| **constitution-extractor** | Haiku | 키워드 추출 (EARS, TRUST 패턴) |
| **tag-auditor** | Haiku | 정규식 기반 TAG 체인 검증 |
| **trust-validator** | Haiku | 규칙 기반 코드 품질 검증 |
| **library-researcher** | Haiku | Context7 MCP 호출 + 문서 요약 |
| **doc-updater** | Haiku | Git diff 분석 + 템플릿 문서 생성 |
| **quality-gate** | Haiku | 메트릭 기반 품질 검증 |

---

### Skills 자동 트리거 규칙

| Skill | 트리거 조건 | 역할 | Model |
|-------|-----------|------|-------|
| **ms-foundation-constitution** | 코드 검토 요청 시 | Constitution 위반 검증 (파일 크기, EARS, TRUST) | Haiku |
| **ms-foundation-trust** | `/ms.analyze` 시 | TRUST 5원칙 자동 검증 | Haiku |
| **ms-foundation-ears** | SPEC 작성 시 | EARS 패턴 검증, 금지 문구 탐지 | Haiku |
| **ms-workflow-tag-manager** | 코드 생성 시 | TAG 블록 자동 삽입/업데이트 | Haiku |
| **ms-workflow-living-docs** | 코드 수정 시 | API 문서 자동 업데이트 | Haiku |
| **ms-lang-typescript** | TypeScript 코드 작성 시 | Best practices, strict mode, ESLint | Haiku |
| **ms-lang-python** | Python 코드 작성 시 | mypy, black, pytest 가이드 | Haiku |

---

### 예시: `/ms.implement` 실행 흐름

```
1. Main Agent (Sonnet) 시작
   ↓
2. Task tool 호출: tdd-implementer (Sonnet)
   ↓
3. tdd-implementer 내부:
   ├─ Skill 자동 트리거: ms-workflow-tag-manager (Haiku)
   │  → TAG ID 검증 및 블록 삽입
   ├─ Skill 자동 트리거: ms-lang-typescript (Haiku)
   │  → TypeScript best practices 적용
   └─ Skill 자동 트리거: ms-foundation-constitution (Haiku)
      → Constitution 위반 검증
   ↓
4. 코드 생성 (TAG 블록 포함)
```

**A != B 예시**:
- Main Agent A = **Sonnet** (복잡한 TDD 구현)
- Skill B = **Haiku** (TAG 검증, 패턴 체크)

---

### 예시: `/ms.review` 실행 흐름

```
1. Main Agent (Opus) 시작
   ↓
2. Task tool 호출: integration-designer (Opus)
   ↓
3. integration-designer 내부:
   ├─ ultrathink 패턴 분석 (시스템적 이슈 탐지)
   ├─ 5-WHY 근본 원인 분석
   ├─ Batch Fix 기회 탐지 + ROI 계산
   └─ Skill 자동 트리거: ms-foundation-constitution (Haiku)
      → Constitution 위반 검증
   ↓
4. 리뷰 리포트 생성
```

**A != B 예시**:
- Main Agent A = **Opus** (복잡한 시스템 분석)
- Skill B = **Haiku** (규칙 기반 검증)

---

### 비용 효율 최적화

**Model 분배 비율** (총 12개 Sub-agents):
- **Haiku**: 7개 (58%) - 검증, 분석, 문서화
- **Sonnet**: 3개 (25%) - SPEC 작성, TDD 구현, 디버깅
- **Opus**: 2개 (17%) - 아키텍처 설계, 통합 전략

**예상 비용 절감** (Opus 5배, Sonnet 1배, Haiku 0.2배 가정):
- 기존 (모두 Sonnet): 12 × 1 = **$12**
- 최적화: (7 × 0.2) + (3 × 1) + (2 × 5) = 1.4 + 3 + 10 = **$14.4**
- 품질 개선: Opus 사용으로 아키텍처 품질 향상 (버그 예방)

**전략**: 비용은 20% 증가하나, 아키텍처 품질 향상으로 장기적 ROI 극대화

---

## 📁 프로젝트 구조

```
specter/
├── .claude/
│   ├── commands/           # 슬래시 커맨드 (22개: 14 My-Spec + 8 Spec-Kit)
│   │   ├── ms.init.md     # 초기화
│   │   ├── ms.specify.md  # 사양 작성 (EARS)
│   │   ├── ms.clarify.md  # 요구사항 명확화
│   │   ├── ms.plan.md     # 구현 계획 (TRUST)
│   │   ├── ms.constitution.md  # 헌법 추출 (Section IX)
│   │   ├── ms.tasks.md    # 태스크 생성 (TAG ID)
│   │   ├── ms.analyze.md  # TRUST 3레벨 검증
│   │   ├── ms.implement.md# 구현 (TAG 자동)
│   │   ├── ms.review.md   # 코드 리뷰 (ultrathink)
│   │   ├── ms.up-docs.md      # Living Docs sync
│   │   └── ms.checklist.md    # 품질 체크리스트
│   └── hooks/             # Constitution 자동 주입
├── templates/
│   ├── constitution-template.md  # Constitution 템플릿
│   └── checklist-template.md     # 체크리스트 템플릿
├── src/
│   ├── lib/
│   │   └── scripts/
│   │       └── check-prerequisites.sh  # 사전 조건 체크
│   └── README.md          # 라이브러리 문서
├── .specify/              # Spec-Kit 디렉토리 (생성됨)
│   ├── memory/
│   │   └── constitution.md       # 프로젝트 헌법
│   ├── scripts/           # Spec-Kit 스크립트들
│   └── templates/         # Spec-Kit 템플릿들
├── specs/                 # 기능 사양들 (생성됨)
│   └── 001-{feature}/
│       ├── spec.md        # 요구사항 (EARS)
│       ├── plan.md        # 구현 계획
│       └── tasks.md       # 태스크 (TAG ID)
├── docs/
│   ├── dev_daily.md       # 일일 작업 로그
│   └── review/            # 코드 리뷰 리포트
├── AGENTS.md              # AI 코딩 규칙
├── CLAUDE.md              # AI 협업 규칙
└── README.md              # 이 파일
```

---

## 💡 언제 사용하나요?

### ✅ 적합한 프로젝트

**스타트업 MVP**
- 빠른 품질 검증 필요
- 요구사항이 자주 변경
- AI와의 협업이 필수

**오픈소스 프로젝트**
- 문서화가 중요
- 추적성이 필수
- 다수의 기여자

**레거시 리팩토링**
- TAG 시스템으로 변경 추적
- 점진적 품질 개선
- 문서 자동 생성

**AI 협업 프로젝트**
- Constitution 기반 규칙 공유
- AI 에이전트 교체 가능
- 일관된 코드 품질

### ❌ 부적합한 프로젝트

**1회성 스크립트**
- <100 LOC
- 유지보수 불필요
- 문서화 불필요

**극도로 단순한 프로젝트**
- "Hello World" 수준
- 사양 작성이 오버엔지니어링

---

## 🆚 기존 방식과의 비교

| 항목 | 기존 방식 | SPECTER 방식 |
|------|----------|-------------|
| **규칙 관리** | README/CONTRIBUTING.md에 산재 | Constitution 집중 |
| **추적성** | Git log + 주석 의존 | TAG 시스템 (ripgrep 고속 스캔) |
| **품질 검증** | CI 실패 후 수정 | 3레벨 진보적 검증 (빠른 실패) |
| **AI 가이드** | 매번 프롬프트 작성 | Constitution 자동 주입 |
| **최신 문서** | Google 검색 | Context7 MCP 자동 조회 |
| **패턴 분석** | 수동 코드 리뷰 | ultrathink 자동 탐지 + ROI 계산 |
| **요구사항** | 자연어 (모호함) | EARS 패턴 (명확함) |
| **테스트** | 선택적 | 필수 (≥85% 커버리지) |

---

## 🛠️ 기술 스택

### 필수 도구

- **ripgrep** (≥13.0): TAG 스캔 (0.5초에 10,000 파일)
- **Git**: 버전 관리
- **uv**: Spec-Kit 설치 (Python 패키지 매니저)

### 개발 환경

**Python Requirements**:
- **Minimum**: Python 3.13+ (required, pyproject.toml)

**MCP 서버 통합**:
- **Context7 MCP**: 최신 라이브러리 문서 조회
  - library-researcher 에이전트에서 사용
  - resolve-library-id, get-library-docs tools
  - 실시간 공식 문서 접근 (FastAPI, React, Next.js 등)

**Multi-Agent System**:
- **Claude Code 내장 에이전트** (Task tool 사용):
  - **Opus 4**: implementation-planner (전략적 아키텍처 설계), integration-designer (코드 리뷰 + ultrathink)
  - **Sonnet 3.5**: spec-builder (EARS 사양 작성), tdd-implementer (TDD 구현), debug-helper (에러 진단)
  - **Haiku 3.5**: library-researcher, codebase-explorer, constitution-extractor, tag-auditor, trust-validator, doc-updater, quality-gate
- 비용 최적화 (고가 모델은 전략적 작업에만 사용: Haiku 58%, Sonnet 25%, Opus 17%)

**컨테이너 환경**:
- Docker Compose 기반 DevContainer
- Node.js LTS + npm (AI CLI 도구)
- Git LFS 지원

### 선택적 도구 (언어별)

**TypeScript/JavaScript**:
- ESLint (복잡도 체크)
- TypeScript Compiler (타입 체크)
- jscpd (중복 코드 검출)

**Python**:
- black (포매터)
- ruff (린터)
- mypy (타입 체크)
- pytest (테스트)
- radon (복잡도 분석)

**Go**:
- golangci-lint

**Rust**:
- clippy

---

## 🚀 Core Architecture

SPECTER combines 4 core systems for automated quality enforcement:

### Core Features

1. **Hooks System** (Python 3.13+)
   - **SessionStart**: Project status display (language, Git branch, changes)
   - **SessionEnd**: Session cleanup
   - **PreToolUse**: Git checkpoints before risky operations
   - **PostToolUse**: Auto-formatting (Prettier, Black)
   - **UserPromptSubmit**: Constitution context injection for sub-agents
   - **Fail-Open Principle**: All hook errors exit with code 0 (never block workflows)

2. **Skills System** (9 Skills, Auto-Triggered)
   - **Foundation** (3): constitution, trust, ears
   - **Language** (2): typescript, python
   - **Essentials** (2): debug, review
   - **Workflow** (2): tag-manager, living-docs

3. **Living Documentation** (CODE-FIRST)
   - `/ms.up-docs`: Universal document synchronization
   - Auto-generated API docs from @CODE tags
   - Auto-updated dev daily from Git diffs
   - TAG integrity validation (ripgrep-based)
   - Performance: 30min → 2min (93% reduction)

4. **Sub-Agents System** (12 agents with model optimization)
   - **Opus (2, 17%)**: implementation-planner, integration-designer
   - **Sonnet (3, 25%)**: spec-builder, tdd-implementer, debug-helper
   - **Haiku (7, 58%)**: library-researcher, codebase-explorer, constitution-extractor, tag-auditor, trust-validator, doc-updater, quality-gate
   - Cost-optimized: High-value models for strategic tasks only

### Quick Start

```bash
# Session starts with project status (Hooks)
claude code .

# Create specification (spec-builder agent + EARS enforcement)
/ms.specify user-authentication

# Design implementation (implementation-planner + library-researcher)
/ms.plan

# Implement with TDD (tdd-implementer + TAG auto-insertion)
/ms.implement

# Sync all docs (Living-Docs)
/ms.up-docs --docs=dev

# Finish with quality gate
/fin
```

### Success Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Document sync time** | 30 minutes | 2 minutes | 93% reduction |
| **TAG validation time** | 15 minutes | 10 seconds | 98% reduction |
| **Constitution compliance** | 70% | 95% | 25% improvement |
| **Context usage** | 100% | 60% | 40% reduction |

---

## 🔄 Recent Updates (2025-10-27)

### Architecture Refactoring (Completed ✅)

**MCP CLI-Bridge Migration**:
- Removed dependency on custom MCP CLI-Bridge
- Full transition to Claude Code's built-in Task tool
- All 12 sub-agents now use native Claude Code agent system
- Improved reliability and reduced external dependencies

**SessionStart Hook Optimization**:
- Simplified project status display
- Removed SPEC progress counter (focusing on Git changes)
- Streamlined output for faster session initialization

**Pre-commit Hook Logging**:
- Added error/warning logging to `docs/log/pre-commit/`
- Timestamped log files: `pre-commit-YYYYMMDD-HHMMSS.log`
- Only logs on errors (keeps directory clean)
- Full context capture for troubleshooting

### Known Limitations

**Sub-Agent Execution**:
- Current: Sub-agents run sequentially within single Task call
- Future: True parallel execution via multiple Task calls in development

**Language Support**:
- Primary: English (EARS requirements, documentation)
- Korean: Infrastructure planned, partial implementation
- Translation: Korean input → English EARS in spec-builder agent

**File Organization**:
- `korean/` command directories planned but not yet created
- Backend/frontend AGENTS.md structure defined, examples pending

---

## 📖 상세 문서

### 핵심 개념

- [CLAUDE.md](./CLAUDE.md) - AI 코딩 규칙 (13개 섹션)
- [Constitution Template](./templates/constitution-template.md) - 헌법 템플릿 (14개 섹션)
- [src/README.md](./src/README.md) - 라이브러리 API

### 명령어 문서

- [.claude/commands/](./claude/commands/) - 22개 슬래시 커맨드 (14 My-Spec + 8 Spec-Kit) 상세 문서

### 스크립트

- [src/lib/scripts/](./src/lib/scripts/) - Prerequisites checker

---

## 🤝 기여

이 프로젝트는 개인 템플릿이지만, 개선 제안은 환영합니다!

### 개선 제안

1. Issue 생성 (문제 설명 + 개선 방향)
2. PR 제출 (선택)

---

## 📄 라이센스

MIT License - 자유롭게 사용 가능

---

## 🙏 Credits

### 영감을 받은 프로젝트

- **[Spec-Kit](https://github.com/github/spec-kit)** - GitHub의 사양 주도 개발 도구
  - SPECTER의 기반이 되는 워크플로우
  - `/speckit.*` 명령어 제공

- **[MoAI-ADK](https://github.com/modu-ai/moai-adk)** - Modu AI의 개발 킷
  - TAG 시스템 영감

### 사용된 도구

- **[Context7 MCP](https://context7.com/)** - 최신 라이브러리 문서 서비스
- **[ripgrep](https://github.com/BurntSushi/ripgrep)** - 초고속 검색 도구
- **[Claude Code](https://claude.com/claude-code)** - Anthropic의 AI 코딩 에이전트

### 철학적 기반

- **TRUST Principles** - My-Spec Constitution
- **EARS Requirements** - Easy Approach to Requirements Syntax
- **Constitutional Governance** - Single Source of Truth 원칙

---

## 🎉 시작하기

```bash
# 1. 프로젝트 초기화
/ms.init

# 2. 첫 번째 기능 사양 작성
/ms.specify my-first-feature

# 3. 워크플로우 따라가기
/ms.clarify      # (선택) 요구사항 명확화
/ms.checklist    # (선택) 명세 품질 체크
/ms.plan         # 구현 계획
/ms.constitution # 헌법 추출
/ms.tasks        # 태스크 생성 (TAG ID)
/ms.analyze      # TRUST 3레벨 검증
/ms.implement    # 구현
/ms.review       # 코드 리뷰 (ultrathink)
/fin             # 완료 (커밋 + 푸시)
```

---

<div align="center">
    <h3>👻 SPECTER가 당신의 프로젝트를 감시합니다</h3>
    <p><em>Specification-Progressive Enforcement & Constitution-based Traceability, Evolutionary Review</em></p>
    <p><strong>Happy Coding with AI! 🤖✨</strong></p>
</div>

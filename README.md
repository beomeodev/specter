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

## ⚡ 빠른 시작

```bash
# 1. 프로젝트 시작 & 초기화 (Constitution 생성)
/ms.init
```
---

## 목차

- [⚡ 빠른 시작](#-빠른-시작)
- [💡 핵심 가치](#-핵심-가치)
- [⚡ 워크플로우](#-워크플로우)
- [🏗️ 자동화 시스템](#️-자동화-시스템)
- [🎯 7가지 원칙](#-7가지-원칙)
- [📁 프로젝트 구조](#-프로젝트-구조)
- [📦 설치](#-설치)
- [💡 언제 사용하나요?](#-언제-사용하나요)
- [🆚 기존 방식과의 비교](#-기존-방식과의-비교)
- [🛠️ 기술 스택](#️-기술-스택)
- [📖 상세 문서](#-상세-문서)
- [🙏 Credits](#-credits)

---

## 💡 핵심 가치

### AI 협업의 3가지 근본 문제

**문제 1: AI는 규칙을 잊어버립니다**
```
"파일은 500줄 이하로 작성해"
→ AI가 3번째 파일부터 1,000줄 작성
→ 매번 수동으로 지적하고 수정
```

**문제 2: 요구사항이 모호하면 AI도 혼란스러워합니다**
```
"로그인 기능 만들어줘"
→ AI: "어떤 인증 방식? 세션? JWT? OAuth?"
→ 10번의 왕복 질문 끝에 잘못된 구현
```

**문제 3: AI가 작성한 코드의 추적이 불가능합니다**
```
3개월 후...
"이 코드가 왜 여기 있지?"
→ Git log를 뒤져도 이유를 찾을 수 없음
→ 삭제해도 될지 수정해야 할지 알 수 없음
```

### SPECTER의 해결책

**1. Constitution이 AI를 자동으로 강제합니다**
```
Constitution Section II: 파일 ≤500 SLOC

→ AI가 501줄 작성 시도
→ ms-foundation-constitution Skill이 즉시 차단
→ "파일 크기 초과. 2개로 분할하세요" 자동 경고
```

**2. EARS 패턴이 모호함을 제거합니다**
```
"로그인 기능" (모호함)
↓
EARS 자동 변환 (ms-foundation-ears Skill)
↓
"WHEN 사용자가 이메일/비밀번호 입력,
 system SHALL bcrypt로 해시 비교 후 JWT 발급"

→ AI가 정확히 구현할 수 있는 명확한 사양
```

**3. TAG 시스템이 완전 추적을 보장합니다**
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
```
3개월 후...
"이 코드가 왜 있지?"
→ ripgrep으로 @SPEC:AUTH-001 검색 (0.5초)
→ specs/001-auth/spec.md에서 요구사항 확인
→ 변경/삭제 판단 가능
```

### 왜 SPECTER인가?

**전통적 개발**: 코드 → 문서 (문서는 항상 뒤처짐)

**SPECTER**: 사양 → 검증 → 코드 (사양이 실행 가능해짐)

**마치 유령(Specter)처럼**, SPECTER는:
- 보이지 않게 프로젝트 전체를 감시하고
- AI가 규칙을 어기면 즉시 차단하며
- 품질 문제가 발생하기 전에 예방합니다

**7가지 DNA**:
```
S - Specification-driven    사양 주도 (EARS로 모호함 제거)
P - Progressive             점진적 검증 (Fail Fast로 빠른 수정)
E - Enforcement             자동 강제 (Constitution이 AI 통제)
C - Constitution-based      단일 진실 출처 (규칙 산재 방지)
T - Traceability            완전 추적 (TAG 체인으로 요구사항↔코드)
E - Evolutionary            진화적 개선 (ultrathink 패턴 분석)
R - Review                  자동 리뷰 (24/7 AI 품질 검증)
```

---

## ⚡ 워크플로우

SPECTER는 **14개 슬래시 커맨드**로 사양부터 배포까지 전 과정을 자동화합니다. 사용자는 커맨드만 입력하면, Skills/Agents/Hooks가 자동으로 품질을 강제합니다.

### 전체 흐름 (10단계)

```bash
# 1. 초기화 - Constitution 생성
/ms.init

# 2. 사양 작성 - EARS 패턴 자동 변환
/ms.specify

# 3. 명확화 - 불명확한 요구사항 질의응답
/ms.clarify
/ms.checklist  # 요구사항 완전성 체크 - 생성 후 Codex가 검토.

# 4. 구현 계획 - TRUST 원칙 적용
/ms.plan

# 5. 헌법 추출 - 프로젝트 제약사항 자동 추출
/ms.constitution

# 6. 태스크 생성 - TAG ID 자동 할당
/ms.tasks

# 7. 품질 검증 - 3레벨 진보적 검증
/ms.analyze

# 8. 구현 - TAG 블록 자동 삽입
/ms.implement

# 9. 코드 리뷰 - ultrathink 패턴 분석
/ms.review

# 10. 완료 - 문서 동기화 + 커밋
/fin    # CI 체크 포함
/finq   # CI 생략 (빠른 커밋)
```

### 핵심 커맨드 상세

#### 1. `/ms.init` - 프로젝트 초기화

**생성되는 것**:
- `.specify/memory/constitution.md` (14개 섹션)
- `AGENTS.md` (AI 코딩 규칙)

**철학**: 규칙이 산재되면 AI가 혼란스러워합니다. Constitution은 모든 규칙의 단일 진실 출처(SSOT)입니다.

---

#### 2. `/ms.specify` - 사양 작성

**AI가 자동으로**:
- 자연어 → EARS 패턴 변환 (WHEN/WHILE/WHERE/IF/SHALL)
- `specs/001-{feature}/spec.md` 생성

**예시**:
```
❌ "로그인 기능 만들어줘"
✅ "WHEN 사용자가 로그인 버튼 클릭, system SHALL 이메일/비밀번호 검증"
```

**철학**: 모호한 요구사항은 나중에 10배 비용으로 돌아옵니다. EARS는 명확성을 강제합니다.

**자동 트리거**:
- `ms-foundation-ears` Skill: EARS 패턴 검증, 금지 문구 탐지 ("fast", "secure", "user-friendly")
- `spec-builder` Agent (Sonnet): 도메인 이해 + EARS 변환

---

#### 3. `/ms.clarify` - 요구사항 명확화 (선택)

**AI가 자동으로**:
- 불명확한 요구사항 질문 생성
- 답변을 spec.md에 기록
- `/ms.checklist`로 완전성 검증

**철학**: 완벽한 사양은 한 번에 나오지 않습니다. 점진적 명확화가 핵심입니다.

---

#### 4. `/ms.plan` - 구현 계획

**AI가 자동으로**:
- TRUST 원칙 적용 (파일 ≤500 SLOC, 함수 ≤100 LOC)
- Simplicity-First 아키텍처 설계
- `plan.md` 생성

**자동 트리거**:
- `implementation-planner` Agent (Opus): 전략적 아키텍처 설계
- `library-researcher` Agent (Haiku): Context7 MCP로 최신 라이브러리 문서 조회
- `codebase-explorer` Agent (Haiku): 기존 패턴 검색
- `ms-foundation-constitution` Skill: 파일 크기/복잡도 제약 검증

**철학**: 복잡한 설계는 유지보수를 지옥으로 만듭니다. 단순함이 최고의 아키텍처입니다.

---

#### 5. `/ms.constitution` - 헌법 추출

**자동으로**:
- spec.md + plan.md에서 제약사항 추출
- Constitution Section IX 업데이트 (프로젝트별 규칙)
- AGENTS.md 자동 업데이트

**철학**: 프로젝트마다 다른 제약사항(API 키 위치, 에러 처리 패턴 등)을 AI가 자동으로 학습합니다.

**자동 트리거**:
- `constitution-extractor` Agent (Haiku): 키워드 추출, EARS/TRUST 패턴 매칭

---

#### 6. `/ms.tasks` - 태스크 생성

**생성되는 것**:
- TAG ID 자동 할당 (AUTH-001, USER-001 등)
- TAG 체인: `@SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001`
- `tasks.md` 생성

**철학**: "이 코드가 왜 있지?"라는 질문이 없어져야 합니다. TAG는 요구사항부터 코드까지 완전 추적을 보장합니다.

**자동 트리거**:
- `ms-workflow-tag-manager` Skill: 언어별 TAG 블록 템플릿 생성 (Python docstring, TypeScript JSDoc)

---

#### 7. `/ms.analyze` - 품질 검증

**3단계 검증** (Progressive Validation):
```
Level 1: Structure (CRITICAL만)
  ✓ tests/ 디렉토리 존재
  ✓ .env in .gitignore
  ✓ 파일 ≤500 SLOC
  ✗ CRITICAL 위반 → 즉시 차단 (Level 2 실행 안 됨)

Level 2: Quality (CRITICAL만)
  ✓ 테스트 실행 성공
  ✓ 린트 0 경고
  ✓ 타입 체크 통과
  ✗ CRITICAL 위반 → 즉시 차단 (Level 3 실행 안 됨)

Level 3: Deep (HIGH/MEDIUM/LOW)
  ✓ 커버리지 ≥85%
  ✓ 복잡도 ≤10
  ✓ TAG 무결성
  ⚠ HIGH/MEDIUM → 경고만 (차단 안 함)
```

**철학**: 나중에 발견된 문제는 수정 비용이 10배 증가합니다. Fail Fast로 빠르게 실패하고 빠르게 수정합니다.

**자동 트리거**:
- `tag-auditor` Agent (Haiku): TAG 체인 검증 (ripgrep 기반, 10,000 파일 0.5초 스캔)
- `trust-validator` Agent (Haiku): TRUST 5원칙 검증
- `ms-foundation-trust` Skill: 테스트 커버리지, 타입 체크, 보안 스캔

---

#### 8. `/ms.implement` - 구현

**AI가 자동으로**:
- Constitution + AGENTS.md 자동 준수
- TAG 블록 자동 삽입
- Context7 MCP로 최신 API 사용
- TDD (테스트 먼저 작성)

**예시**:
```typescript
/**
 * @SPEC:AUTH-001 User Authentication
 * @TEST:AUTH-001 tests/auth.test.ts::should_authenticate_user
 * @CODE:AUTH-001
 */
export class AuthService {
  async authenticate(email: string, password: string): Promise<User> {
    // 구현
  }
}
```

**자동 트리거**:
- `tdd-implementer` Agent (Sonnet): TDD RED-GREEN-REFACTOR 사이클
- `ms-workflow-tag-manager` Skill: TAG 블록 자동 삽입
- `ms-lang-{language}` Skill: 언어별 베스트 프랙티스 (Python: mypy, ruff / TypeScript: tsc strict, Biome)

**철학**: 사람은 잊어버리지만, 시스템은 잊지 않습니다. TAG를 자동으로 삽입하여 추적성을 보장합니다.

---

#### 9. `/ms.review` - 코드 리뷰

**검증 항목**:
- ✅ 명명 규칙 (도메인 용어)
- ✅ 아키텍처 일관성
- ✅ 성능 이슈 (N+1 쿼리)
- ✅ 보안 심층 분석 (OWASP Top 10)
- ✅ 테스트 품질

**ultrathink 패턴 분석**:
```
🔍 SYSTEMIC ISSUES: 3

1. Inconsistent Error Handling (5 occurrences)
   ROOT CAUSE → No team error handling convention
   BATCH FIX (2h) → ROI 286%
```

**자동 트리거**:
- `integration-designer` Agent (Opus): ultrathink 패턴 분석, 5-WHY 근본 원인 탐지, 일괄 수정 기회 제안
- `ms-foundation-constitution` Skill: Constitution 위반 검증

**철학**: 사람은 피곤하지만, AI는 24/7 일합니다. 시스템적 이슈를 탐지하여 일괄 수정으로 ROI를 극대화합니다.

---

#### 10. `/fin`, `/finq` - 완료

**자동으로**:
1. `/ms.up-docs` 실행 (Living Docs 동기화)
2. `docs/dev_daily.md` 업데이트 (Git diff 기반)
3. CI 체크 (`/fin`만: pytest, ruff, mypy)
4. Git 커밋 + 푸시

**차이점**:
- `/fin`: CI 체크 포함 (프로덕션 품질 보장)
- `/finq`: CI 생략 (개발 중 빠른 백업)

**자동 트리거**:
- `quality-gate` Agent (Haiku, `/fin`만): 메트릭 기반 품질 검증
- `doc-updater` Agent (Haiku): Git diff 분석 + 문서 자동 업데이트
- `ms-workflow-living-docs` Skill: API 문서 생성 (@CODE tags 기반)

**철학**: 문서는 코드와 함께 진화해야 합니다. 수동 문서화는 항상 뒤처집니다.

---

## 🏗️ 자동화 시스템

SPECTER는 4계층 자동화로 사용자가 커맨드만 입력하면 품질이 자동으로 강제됩니다.

### 1️⃣ Commands (14개) - 사용자 진입점

사용자가 직접 실행하는 슬래시 커맨드입니다. 나머지 3계층은 자동으로 트리거됩니다.

| 명령어 | 역할 | 생성 파일 |
|-------|------|----------|
| `/ms.init` | 프로젝트 초기화 | Constitution, AGENTS.md |
| `/ms.specify` | 사양 작성 (EARS) | `specs/{id}/spec.md` |
| `/ms.clarify` | 요구사항 명확화 | spec.md 업데이트 |
| `/ms.checklist` | 완전성 체크리스트 | `specs/{id}/checklist.md` |
| `/ms.plan` | 구현 계획 (TRUST) | `specs/{id}/plan.md` |
| `/ms.constitution` | 헌법 추출 | Constitution Section IX |
| `/ms.tasks` | 태스크 생성 | `specs/{id}/tasks.md` |
| `/ms.analyze` | 3레벨 검증 | `.specify/warnings.log` |
| `/ms.implement` | 구현 (TAG 자동) | 코드 + TAG 블록 |
| `/ms.review` | ultrathink 리뷰 | `docs/review/{timestamp}.md` |
| `/ms.up-docs` | Living Docs 동기화 | dev_daily.md, api/*.md |
| `/fin` | 완료 (CI 포함) | Git commit + push |
| `/finq` | 빠른 완료 (CI 생략) | Git commit + push |
| `/ms.unlock` | 잠금 해제 | - |

---

### 2️⃣ Skills (14개) - 품질 강제자

Commands 실행 시 자동으로 트리거되는 품질 검증 시스템입니다. Claude Code의 Skills 시스템을 활용합니다.

**분류별**:

| 분류 | 개수 | Skills | 역할 |
|------|------|--------|------|
| **Foundation** | 4 | constitution, trust, ears, architecture-patterns | 헌법 위반 검증, TRUST 5원칙, EARS 패턴, 아키텍처 패턴 (Clean/Hexagonal/DDD) |
| **Language** | 2 | typescript, python | 언어별 베스트 프랙티스 (TypeScript: Biome, tsc strict / Python: ruff, mypy) |
| **Essentials** | 2 | debug, review | 에러 진단, 코드 리뷰 |
| **Workflow** | 2 | tag-manager, living-docs | TAG 블록 자동 삽입, API 문서 자동 생성 |
| **Domain** | 4 | database-design, api-testing, ci-cd, cross-cutting | DB 스키마 설계, API 테스트 패턴, CI/CD 최적화, 공통 관심사 표준화 |

**트리거 메커니즘**:
- **YAML frontmatter의 `description`** 필드에 "Use when..." 패턴으로 트리거 조건 명시
- Claude Code가 사용자 의도와 매칭하여 자동 로드
- 예: "Use when working with Python files" → Python 파일 수정 시 `ms-lang-python` 자동 트리거

**철학**: Skills는 보이지 않는 품질 감시자입니다. 사용자는 의식하지 못하지만, 모든 작업에서 Constitution 준수를 강제합니다.

---

### 3️⃣ Agents (12개) - 복잡 작업 전문가

Commands가 복잡한 작업을 만나면 자동으로 서브 에이전트를 실행합니다. 비용 최적화를 위해 고가 모델(Opus)은 전략적 작업에만 사용합니다.

**모델별 분배** (비용 최적화):

| 모델 | 개수 | 비율 | Agents | 역할 |
|------|------|------|--------|------|
| **Opus** | 2 | 17% | implementation-planner, integration-designer | 전략적 아키텍처 설계, ultrathink 패턴 분석 |
| **Sonnet** | 3 | 25% | spec-builder, tdd-implementer, debug-helper | EARS 사양 작성, TDD 구현, 에러 진단 |
| **Haiku** | 7 | 58% | library-researcher, codebase-explorer, constitution-extractor, tag-auditor, trust-validator, doc-updater, quality-gate | 패턴 검색, TAG 검증, 문서 생성 |

**자동 실행 규칙**:
```
복잡도 높음 → 다중 에이전트 실행 (병렬)
├── Pattern_Search_Agent (기존 패턴 검색)
├── Library_Research_Agent (Context7 MCP)
└── Dependency_Analysis_Agent (통합 분석)

복잡도 낮음 → 단일 에이전트 실행
```

**철학**: 비싼 도구는 꼭 필요한 곳에만 사용합니다. Haiku가 58%를 담당하여 비용을 40% 절감합니다.

---

### 4️⃣ Hooks (5개) - 자동 감시자

Commands/Skills/Agents 실행 전후로 자동으로 트리거되는 이벤트 핸들러입니다. Python 3.14 기반 `.claude/hooks/` 스크립트로 구현됩니다.

| Hook | 트리거 시점 | 역할 |
|------|-----------|------|
| **SessionStart** | Claude Code 시작 | 프로젝트 상태 표시 (언어, Git 브랜치, 변경사항) |
| **UserPromptSubmit** | 사용자 입력 시 | Constitution 컨텍스트 자동 주입 (서브 에이전트용) |
| **PreToolUse** | 위험 작업 전 | Git 체크포인트 자동 생성 |
| **PostToolUse** | 파일 수정 후 | 자동 포매팅 (Prettier, Black) |
| **SessionEnd** | Claude Code 종료 | 세션 정리 |

**Fail-Open 원칙**: 모든 hook 에러는 exit code 0 (워크플로우 차단 안 함). 에러는 로그에만 기록하고 작업은 계속 진행됩니다.

**철학**: Hooks는 보이지 않는 안전망입니다. 사용자는 의식하지 못하지만, 모든 작업에서 체크포인트를 생성하고 Constitution을 주입합니다.

---

### 전체 워크플로우 매핑

| 단계 | 명령어 | Main Agent | Sub-Agent | Skills | 생성 파일 |
|------|--------|-----------|-----------|--------|----------|
| **0** | `/ms.init` | Sonnet | - | - | Constitution, AGENTS.md |
| **1** | `/ms.specify` | Sonnet | spec-builder (Sonnet) | ears | `specs/001-{feature}/spec.md` |
| **2** | `/ms.clarify` | Sonnet | - | ears | spec.md 업데이트 |
| **3** | `/ms.checklist` | Haiku | - | ears | `specs/{id}/checklist.md` |
| **4** | `/ms.plan` | Opus | implementation-planner (Opus)<br>library-researcher (Haiku)<br>codebase-explorer (Haiku) | constitution, architecture-patterns | `specs/{id}/plan.md` |
| **5** | `/ms.constitution` | Haiku | constitution-extractor (Haiku) | - | Constitution Section IX |
| **6** | `/ms.tasks` | Sonnet | - | tag-manager | `specs/{id}/tasks.md` |
| **7** | `/ms.analyze` | Haiku | tag-auditor (Haiku)<br>trust-validator (Haiku) | trust, constitution | `.specify/warnings.log` |
| **8** | `/ms.implement` | Sonnet | tdd-implementer (Sonnet) | tag-manager, lang-{language}, database-design | 코드 + TAG 블록 |
| **9** | `/ms.review` | Opus | integration-designer (Opus) | constitution, api-testing | `docs/review/{timestamp}.md` |
| **10** | `/ms.up-docs` | Haiku | doc-updater (Haiku) | living-docs | dev_daily.md, api/*.md |
| **11** | `/fin` | Sonnet | quality-gate (Haiku)<br>doc-updater (Haiku) | ci-cd, cross-cutting | Git commit + push |

---

## 🎯 7가지 원칙

SPECTER의 모든 설계는 7가지 원칙에서 출발합니다. 각 원칙은 자동화 시스템에 자연스럽게 녹아들어 있습니다.

### S - Specification-driven (사양 주도)

**원칙**: 모든 개발은 formal specification에서 시작합니다.

**적용**:
- `/ms.specify`는 자연어를 EARS 패턴으로 강제 변환합니다
- `ms-foundation-ears` Skill이 모호한 표현("fast", "secure")을 탐지하고 차단합니다
- spec.md 없이는 `/ms.plan` 실행 불가

**철학**: 명확한 사양이 없으면 AI도 혼란스러워합니다. EARS는 "WHEN 사용자가 X 하면, system SHALL Y"처럼 명확한 조건-동작 패턴을 강제하여 모호함을 제거합니다.

---

### P - Progressive (점진적 검증)

**원칙**: 3단계 검증으로 빠르게 실패합니다 (Fail Fast).

**적용**:
- `/ms.analyze`는 Level 1 → Level 2 → Level 3 순차 실행
- CRITICAL 위반 시 즉시 차단 (다음 레벨 실행 안 됨)
- Level 1 실패 시 "tests/ 디렉토리 생성하세요" 즉시 표시

**철학**: 나중에 발견된 문제는 수정 비용이 10배 증가합니다. Structure(기본 구조) → Quality(실행 가능) → Deep(심층 분석) 순서로 검증하여 초기에 빠르게 차단합니다.

---

### E - Enforcement (자동 강제)

**원칙**: Constitution이 규칙을 자동으로 강제합니다.

**적용**:
- `UserPromptSubmit` Hook이 모든 서브 에이전트에 Constitution 자동 주입
- `ms-foundation-constitution` Skill이 파일 크기 ≤500 SLOC 위반 시 즉시 경고
- `/ms.implement` 실행 시 TAG 블록 자동 삽입 (수동 작성 불가)

**철학**: 사람은 잊어버리지만, 시스템은 잊지 않습니다. 규칙을 문서가 아닌 코드로 강제하여 100% 준수를 보장합니다.

---

### C - Constitution-based (헌법 기반)

**원칙**: 단일 진실 출처 (Single Source of Truth)

**적용**:
- `.specify/memory/constitution.md` 14개 섹션에 모든 규칙 집중
- Section IX는 `/ms.constitution`이 spec.md + plan.md에서 자동 추출
- AGENTS.md는 프로젝트별 코딩 규칙 자동 업데이트

**구조**:
```
.specify/memory/constitution.md
├── Section I    : Test-First Development (절대 규칙)
├── Section II   : Simplicity-First Architecture
├── Section IV   : EARS Requirements Standard
├── Section V    : TRUST 5 Principles
└── Section IX   : Project-Specific Constraints (자동 생성)
```

**철학**: 규칙이 README/CONTRIBUTING.md/Wiki에 산재되면 AI가 무엇을 따라야 할지 혼란스러워합니다. Constitution은 모든 규칙을 한곳에 모아 일관성을 강제합니다.

---

### T - Traceability (추적성)

**원칙**: 요구사항부터 코드까지 완전 추적

**적용**:
- `/ms.tasks`가 도메인별 TAG ID 자동 생성 (AUTH-001, USER-001)
- `/ms.implement`가 TAG 블록 자동 삽입
- `tag-auditor` Agent가 TAG 체인 무결성 검증 (ripgrep 기반, 10,000 파일 0.5초)

**예시**:
```typescript
/**
 * @SPEC:AUTH-001 User Authentication
 * @TEST:AUTH-001 tests/auth.test.ts::should_authenticate_user
 * @CODE:AUTH-001
 */
```

**철학**: "이 코드가 왜 있지?"라는 질문이 없어져야 합니다. TAG는 요구사항 → 테스트 → 코드를 1:1:1로 연결하여 변경 추적을 완벽하게 만듭니다.

---

### E - Evolutionary (진화적)

**원칙**: 점진적 개선 사이클

**적용**:
- `/ms.clarify`로 사양을 점진적으로 명확화
- `/ms.review`의 ultrathink 패턴 분석이 시스템적 이슈 탐지
- `/ms.constitution`이 반복 패턴을 Constitution Section IX에 자동 추출

**사이클**:
```
specify → clarify → plan → constitution → tasks → analyze → implement → review → fin
   ↓         ↓         ↓          ↓           ↓        ↓          ↓          ↓
 사양 작성  명확화   계획 수립   헌법 추출   태스크화   검증     구현      리뷰
```

**철학**: 완벽은 한 번에 오지 않습니다. ultrathink 리뷰가 "5 occurrences of inconsistent error handling"을 탐지하면, `/ms.constitution`이 이를 Section IX에 추출하여 다음 기능부터 자동 강제합니다.

---

### R - Review (자동 리뷰)

**원칙**: AI 기반 자동 코드 리뷰

**적용**:
- `/ms.review`가 명명 규칙, 아키텍처, 성능, 보안, 테스트 자동 검증
- `integration-designer` Agent (Opus)가 ultrathink 패턴 분석으로 시스템적 이슈 탐지
- 5-WHY 근본 원인 분석 + 일괄 수정 기회 제안 (ROI 계산 포함)

**ultrathink 예시**:
```
🔍 SYSTEMIC ISSUES: 3

1. Inconsistent Error Handling (5 occurrences across 3 services)

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

**철학**: 사람은 피곤하지만, AI는 24/7 일합니다. 단일 코드 리뷰가 아닌 시스템적 패턴을 탐지하여 일괄 수정으로 ROI를 극대화합니다.

---

## 📁 프로젝트 구조

```
specter/
├── .claude/
│   ├── commands/           # 슬래시 커맨드 (14개)
│   ├── skills/             # 품질 강제자 (14개)
│   ├── agents/             # 서브 에이전트 (12개)
│   └── hooks/              # 자동 감시자 (5개)
├── .specify/               # 생성됨 (/ms.init 실행 시)
│   ├── memory/
│   │   └── constitution.md       # 프로젝트 헌법 (14개 섹션)
│   └── scripts/           # Constitution 관련 스크립트
├── specs/                 # 기능 사양들 (생성됨)
│   └── 001-{feature}/
│       ├── spec.md        # 요구사항 (EARS)
│       ├── plan.md        # 구현 계획
│       ├── checklist.md   # 완전성 체크리스트
│       └── tasks.md       # 태스크 (TAG ID)
├── docs/
│   ├── dev_daily.md       # 일일 작업 로그 (자동 업데이트)
│   ├── review/            # 코드 리뷰 리포트
│   ├── api/               # API 문서 (자동 생성, TAG 기반)
│   └── templates/         # Constitution 템플릿
├── AGENTS.md              # AI 코딩 규칙 (자동 업데이트)
├── CLAUDE.md              # AI 협업 규칙
└── README.md              # 이 파일
```

---

## 📦 설치

### 새 프로젝트에 SPECTER 설치

```bash
npx degit beomeodev/specter my-new-project
cd my-new-project
npm install  # 또는 uv pip install -e .
```

이 명령어는 SPECTER 템플릿을 복사하여 새 프로젝트를 생성합니다 (`.git` 히스토리 제외).

### 설치 후 첫 단계

```bash
# 1. 프로젝트 초기화
/ms.init

# 2. 첫 기능 사양 작성
/ms.specify my-first-feature
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
- **uv**: 의존성 관리 (Python 패키지 매니저)

### 개발 환경

**Python Requirements**:
- **Minimum**: Python 3.14+ free-threaded build (required, pyproject.toml)
- **Free-threading**: GIL-free execution for true parallelism

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
- Biome (통합 린터 + 포매터, ESLint 대비 75배 빠름)
- TypeScript Compiler (타입 체크)

**Python**:
- ruff (통합 린터 + 포매터, pylint 대비 100배 빠름)
- mypy (타입 체크)
- pytest (테스트)

**Go**:
- golangci-lint

**Rust**:
- clippy

---

## 📖 상세 문서

### 핵심 개념

- [CLAUDE.md](./CLAUDE.md) - AI 코딩 규칙
- [Constitution Template](./docs/templates/constitution-template.md) - 헌법 템플릿 (14개 섹션)
- [docs/src/README.md](./docs/src/README.md) - 라이브러리 API

### 명령어 문서

- [.claude/commands/](./.claude/commands/) - 14개 슬래시 커맨드 상세 문서

### 스크립트

- [docs/src/lib/scripts/](./docs/src/lib/scripts/) - Prerequisites checker

---

## 📄 라이센스

MIT License - 자유롭게 사용 가능

---

## 🙏 Credits

### 영감을 받은 프로젝트

- **[Spec-Kit](https://github.com/github/spec-kit)** - GitHub의 사양 주도 개발 도구
  - SPECTER의 기반이 되는 워크플로우

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

<div align="center">
    <h3>👻 SPECTER가 당신의 프로젝트를 감시합니다</h3>
    <p><em>Specification-Progressive Enforcement & Constitution-based Traceability, Evolutionary Review</em></p>
    <p><strong>Happy Coding with AI! 🤖✨</strong></p>
</div>

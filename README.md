<div align="center">
    <h1>👻 SPECTER</h1>
    <h3><em>AI와 함께하는 고품질 소프트웨어 개발</em></h3>
</div>

<p align="center">
    <strong>Specification-Progressive Enforcement & Constitution-based Traceability, Evolutionary Review</strong>
</p>

<p align="center">
    사양 기반 점진적 검증 · 헌법 기반 추적성 · 진화적 리뷰
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

**1. Constitution이 AI에게 일관된 기준을 제공합니다**
```
Constitution Section II: 파일 ≤500 SLOC

→ AI가 501줄 작성 시도
→ ms-foundation-constitution Skill이 경고
→ "파일 크기 초과. 2개로 분할하세요" 가이드 제시
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

**3. TAG 시스템이 추적 가능성을 구조화합니다**
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

**SPECTER의 정체**: Spec-Kit 위에 올라가는 overlay + Claude Code 자산 세트입니다.

- **Spec-Kit**: 사양 주도 개발 워크플로우 엔진 (GitHub)
- **SPECTER**: Constitution 기반 품질 가이드 + TAG 추적성 + 에이전트 생태계

`/ms.specify`, `/ms.plan`, `/ms.implement` 같은 커맨드는 내부적으로 `/speckit.*`를 실행하고, 그 위에 Constitution 검증과 TAG 자동화를 얹습니다. SPECTER만 단독으로는 동작하지 않으며, `/ms.init`으로 Spec-Kit을 먼저 설치해야 합니다.

---

**전통적 개발**: 코드 → 문서 (문서는 항상 뒤처짐)

**SPECTER**: 사양 → 검증 → 코드 (사양이 실행 가능해짐)

**마치 유령(Specter)처럼**, SPECTER는:
- 보이지 않게 프로젝트 전체에 기준을 적용하고
- AI가 방향을 잃으면 가이드를 제시하며
- 품질 기준을 워크플로우 곳곳에 녹여둡니다

**7가지 DNA**:
```
S - Specification-driven    사양 주도 (EARS로 모호함 제거)
P - Progressive             점진적 검증 (Fail Fast로 빠른 수정)
E - Enforcement             일관 가이드 (Constitution이 AI 방향 제시)
C - Constitution-based      단일 진실 출처 (규칙 산재 방지)
T - Traceability            추적 구조화 (TAG 체인으로 요구사항↔코드)
E - Evolutionary            진화적 개선 (패턴 분석 + 사이클 반복)
R - Review                  코드 리뷰 (AI 지원 품질 검증)
```

---

## ⚡ 워크플로우

SPECTER는 **15개 슬래시 커맨드**로 PRD 분해부터 릴리즈까지 전 과정을 자동화합니다. 파이프라인은 `/ms.featuremap`(PRD → Feature Map)에서 시작하며, `/ms.specify`는 **Feature Map의 Feature 섹션 없이는 동작하지 않습니다(게이트)**. 사용자는 커맨드만 입력하면, Skills/Agents가 자동으로 품질을 검증하고 가이드합니다.

### 전체 흐름 (PRD → 릴리즈)

```bash
# 0. PRD 작성 (docs/prd/PRD.md) — 무엇을, 왜 (단일 진실 출처)

# 1. 초기화 - Constitution 생성 + Spec-Kit 설치
/ms.init

# 2. PRD 분해 - PRD를 Feature Map(의존성 그래프)으로  ⭐ 파이프라인 진입점
/ms.featuremap @docs/prd/PRD.md      # → docs/prd/feature-map.md

# ───── 이하 Feature Map의 Feature별로 DAG 순서대로 반복 ─────

# 3. 사양 작성 - Feature Map의 Feature 섹션을 입력 (게이트: 이것 없이는 거부)
/ms.specify

# 4. 명확화 - 불명확한 요구사항 질의응답
/ms.clarify
/ms.checklist  # 요구사항 완전성 체크 (선택) - 생성 후 Codex가 검토.

# 5. 구현 계획 - TRUST 원칙 적용
/ms.plan

# 6. 헌법 추출 - 프로젝트 제약사항 자동 추출
/ms.constitution

# 7. 태스크 생성 - TAG ID 자동 할당
/ms.tasks

# 8. 품질 검증 - 3레벨 진보적 검증
/ms.analyze

# 9. 구현 - TAG 블록 자동 삽입
/ms.implement

# 10. 코드 리뷰 - ultrathink 패턴 분석
/ms.review

# 11. 완료 - 문서 동기화 + 커밋 + PR 생성
/fin    # CI 체크 포함
/finq   # CI 생략 (빠른 커밋)

# 12. 머지 + 릴리즈 - 승인된 PR을 master에 머지하고 GitHub Release 생성
/ms.merglease

# → 다음 Feature는 3번부터 반복. /ms.specify가 specs/를 대조해
#   Feature Map의 Progress Ledger를 새로고침하고 "다음 미완료 Feature"를 안내.
```

> **곁가지 트랙**: 새 요구사항이 아닌 변경(버그·문구·스타일·리팩토링)은 `/ms.fix`로 — spec/clarify/plan/tasks 생략, TDD+TAG+게이트는 유지. 구현 후 설계 변경은 `/ms.amend`.

### 핵심 커맨드 상세

#### 1. `/ms.init` - 프로젝트 초기화

**생성되는 것**:
- `.specify/memory/constitution.md` (14개 섹션)
- `AGENTS.md` (AI 코딩 규칙)

**철학**: 규칙이 산재되면 AI가 혼란스러워합니다. Constitution은 모든 규칙의 단일 진실 출처(SSOT)입니다.

추가로 `/ms.init`은 설치된 `speckit.specify`에 Feature Map 게이트를 주입하여, `/ms.specify`를 우회한 직접 호출도 차단합니다.

---

#### 2. `/ms.featuremap` - PRD 분해 (Feature Map 생성)

**AI가 자동으로**:
- PRD를 **독립 구현·머지·배포 가능한 Feature들의 의존성 그래프(DAG)**로 분해
- `docs/prd/feature-map.md` 생성 (영어). 각 Feature 섹션이 `/ms.specify` 입력이 됨
- Progress Ledger(전 Feature 상태표) 포함

**분해 원칙**: 마일스톤=Phase 골격 · 인프라 먼저 · 엔진↔화면 분리 · 횡단 관심사는 늦은 전용 Feature · Stub-and-Forward(공유 기반은 1번 Feature에 스텁, 활성화는 후속 Feature) · 모든 범위 외 항목에 담당 Feature 명시.

**철학**: PRD가 단일 진실 출처. Feature Map은 사양을 복제하지 않고 "어디부터 어디까지가 한 Feature인가"의 경계만 정의합니다. 이 단계 없이는 `/ms.specify`가 거부됩니다.

---

#### 3. `/ms.specify` - 사양 작성

**입력**: Feature Map의 Feature 섹션 (게이트 — freeform·임의 텍스트·기존 spec.md 기반이면 거부)

**AI가 자동으로**:
- Feature 섹션 → EARS/GEARS 사양 변환
- `specs/{NNN}-{feature}/spec.md` 생성
- Progress Ledger를 specs/ 기준으로 새로고침 + "다음 미완료 Feature" 보고

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

#### 4. `/ms.clarify` - 요구사항 명확화 (선택)

**AI가 자동으로**:
- 불명확한 요구사항 질문 생성
- 답변을 spec.md에 기록
- `/ms.checklist`로 완전성 검증

**철학**: 완벽한 사양은 한 번에 나오지 않습니다. 점진적 명확화가 핵심입니다.

---

#### 5. `/ms.plan` - 구현 계획

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

#### 6. `/ms.constitution` - 헌법 추출

**자동으로**:
- spec.md + plan.md에서 제약사항 추출
- Constitution Section IX 업데이트 (프로젝트별 규칙)
- AGENTS.md 자동 업데이트

**철학**: 프로젝트마다 다른 제약사항(API 키 위치, 에러 처리 패턴 등)을 AI가 자동으로 학습합니다.

**자동 트리거**:
- `constitution-extractor` Agent (Haiku): 키워드 추출, EARS/TRUST 패턴 매칭

---

#### 7. `/ms.tasks` - 태스크 생성

**생성되는 것**:
- TAG ID 자동 할당 (AUTH-001, USER-001 등)
- TAG 체인: `@SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001`
- `tasks.md` 생성

**철학**: "이 코드가 왜 있지?"라는 질문이 없어져야 합니다. TAG는 요구사항부터 코드까지 추적 경로를 구조화합니다.

**자동 트리거**:
- `ms-workflow-tag-manager` Skill: 언어별 TAG 블록 템플릿 생성 (Python docstring, TypeScript JSDoc)

---

#### 8. `/ms.analyze` - 품질 검증

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

#### 9. `/ms.implement` - 구현

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

**철학**: 사람은 잊어버리지만, 시스템은 잊지 않습니다. TAG를 자동으로 삽입하여 추적성을 구조화합니다.

---

#### 10. `/ms.review` - 코드 리뷰

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

#### 11. `/fin`, `/finq` - 완료

**실행 순서**:
1. `/ms.up-docs --docs=dev` 호출 → `docs/dev_daily.md`에 git diff 요약 추가
2. CI 체크 (`/fin`만: pytest, ruff, mypy 실행)
3. git commit + push + PR 생성

**`/ms.up-docs`가 `/fin` 안에서 하는 일**:
```
git diff HEAD~1 --stat          # 변경 파일 목록
git log -1 --format='%h %s'     # 커밋 메시지
rg '@(SPEC|TEST|CODE)'          # 수정된 TAG ID 스캔
→ docs/dev_daily.md에 타임스탬프 포함 추가
```
`--docs=api`, `--docs=readme` 모드는 `/fin`에서 자동 실행되지 않습니다. 필요 시 수동으로 호출하세요.

**차이점**:
- `/fin`: CI 체크 포함 (프로덕션 커밋용)
- `/finq`: CI 생략 (개발 중 빠른 백업용)

**철학**: 문서는 코드와 함께 진화해야 합니다. 수동 문서화는 항상 뒤처집니다.

---

#### 12. `/ms.merglease` - 머지 + 릴리즈

**언제 사용하나요?** `/fin` 또는 `/finq`로 PR을 만든 뒤, GitHub에서 리뷰가 끝나고 머지해도 되는 시점에 실행합니다.

**실행 순서**:
1. `gh` CLI 설치/인증, 현재 브랜치, 열린 PR, CI 상태를 사전 점검
2. 머지 전략 결정 (`merge` 기본, `squash`/`rebase` 선택 가능)
3. 사용자 확인 후 `gh pr merge`로 PR 머지
4. `master`/`main`으로 전환 후 최신 상태 pull
5. 기존 태그와 spec 번호를 기준으로 버전 제안
6. 릴리즈 노트 초안 생성 후 사용자 확인
7. annotated tag push
8. GitHub Release 생성

**사용 예시**:
```bash
/ms.merglease                      # PR 자동 감지 + 버전 제안 + 릴리즈
/ms.merglease v0.21.0              # 명시 버전 사용
/ms.merglease --strategy=squash    # squash merge 사용
/ms.merglease --no-release         # 머지만 하고 릴리즈 생략
```

**안전장치**:
- `master`/`main`에서 직접 실행하면 중단합니다.
- 현재 브랜치에 열린 PR이 없으면 중단합니다.
- 머지 충돌이 있으면 중단합니다.
- CI 실패 항목은 경고로 표시하고, 머지/태그/릴리즈처럼 공유 상태를 바꾸는 단계는 사용자 확인 후 진행합니다.

**철학**: `/fin`이 PR 생성까지 담당한다면, `/ms.merglease`는 승인된 PR을 실제 릴리즈 단위로 닫습니다. 머지, 태그, GitHub Release를 한 흐름으로 묶어 "머지만 하고 릴리즈를 잊는" 운영 실수를 줄입니다.

---

## 🏗️ 자동화 시스템

SPECTER는 3계층으로 구성됩니다.

### 1️⃣ Commands (15개) - 사용자 진입점

사용자가 직접 실행하는 슬래시 커맨드입니다. 나머지 2계층은 자동으로 트리거됩니다.

| 명령어 | 역할 | 생성 파일 |
|-------|------|----------|
| `/ms.init` | 프로젝트 초기화 | Constitution, AGENTS.md |
| `/ms.featuremap` | PRD 분해 (Feature Map) | `docs/prd/feature-map.md` |
| `/ms.specify` | 사양 작성 (Feature Map 게이트) | `specs/{id}/spec.md` |
| `/ms.clarify` | 요구사항 명확화 | spec.md 업데이트 |
| `/ms.checklist` | 완전성 체크리스트 | `specs/{id}/checklist.md` |
| `/ms.plan` | 구현 계획 (TRUST) | `specs/{id}/plan.md` |
| `/ms.constitution` | 헌법 추출 | Constitution Section IX |
| `/ms.tasks` | 태스크 생성 | `specs/{id}/tasks.md` |
| `/ms.analyze` | 3레벨 검증 | `.specify/warnings.log` |
| `/ms.implement` | 구현 (TAG 자동) | 코드 + TAG 블록 |
| `/ms.review` | 코드 품질 리뷰 | - |
| `/ms.up-docs` | 문서 동기화 | `docs/dev_daily.md` |
| `/fin` | 완료 (CI 포함) | Git commit + push |
| `/finq` | 빠른 완료 (CI 생략) | Git commit + push |
| `/ms.merglease` | PR 머지 + 태그 + GitHub Release | GitHub PR, tag, release |

---

### 2️⃣ Skills (14개) - 전문 지식 세트

각 Skill 파일의 frontmatter `description: "Use when..."` 패턴을 Claude Code가 읽어 컨텍스트에 맞는 Skill을 자동 로드합니다. Foundation / Language / Essentials / Workflow / Domain 5개 분류로 구성되며, 상세 내용은 `.claude/skills/` 디렉토리를 참조하세요.

---

### 3️⃣ Agents (15개) - 서브에이전트 전문가

Commands가 복잡한 작업을 위임하는 서브에이전트입니다. 비용 최적화를 위해 모델을 작업 복잡도에 맞게 분배합니다.

| 모델 | 개수 | Agents |
|------|------|--------|
| **Opus** | 3 | code-refactor-master, implementation-planner, integration-designer |
| **Sonnet** | 5 | debug-helper, refactor-planner, spec-builder, tdd-implementer, web-research-specialist |
| **Haiku** | 7 | codebase-explorer, constitution-extractor, doc-updater, library-researcher, quality-gate, tag-auditor, trust-validator |

각 에이전트의 역할과 사용법은 `.claude/agents/` 디렉토리의 개별 파일을 참조하세요.

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

### E - Enforcement (일관 가이드)

**원칙**: Constitution이 규칙을 워크플로우 전반에 일관되게 제시합니다.

**적용**:
- `ms-foundation-constitution` Skill이 파일 크기 ≤500 SLOC 위반 시 경고
- `/ms.implement` 실행 시 TAG 블록 자동 삽입

**철학**: 사람은 잊어버리지만, 시스템은 잊지 않습니다. 규칙을 매번 프롬프트로 주입하는 대신 Constitution과 Skill로 구조화합니다.

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
│   ├── skills/             # 전문 지식 세트 (14개)
│   └── agents/             # 서브 에이전트 (15개)
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

# 2. PRD 작성 후 Feature Map으로 분해
/ms.featuremap @docs/prd/PRD.md

# 3. 첫 Feature 사양 작성 (Feature Map의 Feature 001 섹션을 입력)
/ms.specify
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
- **Claude Code 내장 에이전트** (Task tool 사용), 총 15개
  - **Opus**: code-refactor-master, implementation-planner, integration-designer
  - **Sonnet**: debug-helper, refactor-planner, spec-builder, tdd-implementer, web-research-specialist
  - **Haiku**: codebase-explorer, constitution-extractor, doc-updater, library-researcher, quality-gate, tag-auditor, trust-validator
- 비용 최적화: Haiku 47%, Sonnet 33%, Opus 20%

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

- [.claude/commands/](./.claude/commands/) - 15개 슬래시 커맨드 상세 문서

### 스크립트

- [docs/src/lib/scripts/](./docs/src/lib/scripts/) - Prerequisites checker

---

## 📄 라이센스

MIT License - 자유롭게 사용 가능

---

## 🙏 Credits

### 기반 의존

- **[Spec-Kit](https://github.com/github/spec-kit)** - GitHub의 사양 주도 개발 도구
  - SPECTER가 overlay하는 핵심 엔진. `/ms.init`으로 설치 필요.

### 영감을 받은 프로젝트

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

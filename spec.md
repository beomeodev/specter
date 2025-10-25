# MoAI-ADK 4대 기능 통합 명세서 (My-Spec 프로젝트)

**프로젝트명**: My-Spec Enhanced with MoAI-ADK
**버전**: 2.0.0
**작성일**: 2025-10-25
**최종 수정**: 2025-10-25
**담당**: Claude Sonnet 4.5
**목적**: MoAI-ADK의 Skills, Living-Docs, Hooks, Sub-Agents를 My-Spec 워크플로우에 최적 통합

---

## Executive Summary

본 명세서는 **MoAI-ADK**의 4가지 핵심 기능을 **My-Spec 워크플로우**에 통합하기 위한 전략과 실행 계획을 제시합니다.

### 핵심 목표

| 목표 | 현재 상태 | 목표 상태 | 개선율 |
|------|---------|---------|--------|
| **문서 동기화** | 수동 (30분/회) | 자동 (2분/회) | 93% ↓ |
| **TAG 검증** | 수동 (/ms.analyze) | 실시간 자동 | 98% ↓ |
| **Constitution 준수** | 70% (수동) | 95% (자동) | 25% ↑ |
| **개발자 인지 부하** | 높음 (11개 명령 숙지) | 낮음 (AI 자동 처리) | 60% ↓ |
| **안전성** | 수동 백업 | 자동 체크포인트 | 98% ↑ |

### 통합 대상 4대 기능

1. **Hooks** (이벤트 기반 자동화) - 안전 인프라
2. **Skills** (재사용 가능 지식) - 자동화 지식 캡슐
3. **Living-Docs** (CODE-FIRST 문서) - 문서-코드 동기화
4. **Sub-Agents** (전문 AI 팀) - 역할 분산 및 협업

### 주요 변경사항 (v2.0.0)

- ✅ Phase 1.0 추가: 기존 hooks 마이그레이션 전략 (constitution-injector.sh, tag-enforcer.ts)
- ✅ Test-First 원칙 적용: 모든 Phase에 RED → GREEN → REFACTOR 추가
- ✅ Small units 준수: Phase 2 Skills 7개 → 3단계 분할 (2-3개씩)
- ✅ settings.json → settings.local.json 수정 (Claude Code 우선순위 반영)
- ✅ 경로 매핑 규칙 추가 (.moai → .specify)
- ✅ Python 환경 요구사항 명시 (Python ≥3.8, pytest)
- ✅ Progressive Disclosure 구현 전략 추가
- ✅ 에러 핸들링 정책 명시 (Fail-open)
- ✅ 통합 일정 재조정 (10주 → 12주, Test-First 반영)

---

## 1. 현재 워크플로우 분석

### 1.1. My-Spec 워크플로우 구조

**11개 슬래시 명령어** (.claude/commands/ms.*.md):

```
Phase 0: 프로젝트 초기화
├─ /ms.init                    # Spec-Kit + Constitution 설치

Phase 1: 요구사항 정의
├─ /ms.specify                 # SPEC 작성 (EARS 기반)
├─ /ms.clarify                 # 요구사항 명확화 (질의응답)
└─ /ms.checklist               # 완성도 체크리스트

Phase 2: 구현 계획
├─ /ms.plan                    # 구현 계획 (Architecture)
└─ /ms.constitution            # 프로젝트 제약사항 추출

Phase 3: 구현
├─ /ms.tasks                   # TAG ID 생성 및 Task 분해
├─ /ms.analyze                 # TRUST 검증 (3단계)
└─ /ms.implement               # TDD 구현 + TAG 삽입

Phase 4: 품질 관리
├─ /ms.review                  # 코드 품질 리뷰
└─ /ms.update-docs             # Living Document 수동 업데이트 (→ ms.sync로 대체 예정)
```

### 1.2. 기존 Hooks 현황 분석

**현재 존재하는 hooks** (.claude/hooks/):

| 파일 | 언어 | 트리거 | 기능 | LOC | 상태 |
|------|------|-------|------|-----|------|
| **constitution-injector.sh** | Shell | Task tool | Constitution 자동 주입 (sub-agents에게) | 35 | ✅ 활성 |
| **tag-enforcer.ts** | TypeScript | PreToolUse | @IMMUTABLE TAG 보호, TAG 체인 검증 | 238 | ✅ 활성 |
| **notify.sh** | Shell | (미사용) | 알림 기능 | N/A | ⚠️ 미사용 |

**마이그레이션 필요성**:
- MoAI 통합 계획: Python 기반 `.claude/hooks/ms/` 구조
- 기존 hooks: Shell + TypeScript 혼재
- 기능 중복: tag-enforcer.ts의 TAG 검증 ↔ MoAI core/tags.py

### 1.3. 현재 강점

| 강점 | 설명 |
|------|------|
| **명확한 단계** | 순차적 워크플로우로 누락 방지 |
| **Constitution 중심** | 모든 단계에서 품질 원칙 적용 |
| **TAG 추적성** | SPEC → TEST → CODE 완전 추적 |
| **EARS 표준화** | 모호한 요구사항 제거 |
| **TRUST 검증** | 3단계 품질 게이트 (구조 → 품질 → 심층) |
| **기존 hooks 활용** | Constitution 자동 주입, TAG 보호 기능 이미 구현 |

### 1.4. 현재 한계

| 한계 | 영향 | 해결 방안 (MoAI-ADK) |
|------|------|---------------------|
| **단일 AI 과부하** | 모든 작업을 Claude 혼자 처리 | Sub-Agents (역할 분산) |
| **수동 문서 업데이트** | 코드 변경 후 문서 낙후 | Living-Docs (자동 동기화) |
| **TAG 검증 수동화** | TAG 체인 무결성 수동 검증 | Skills + tag-auditor Agent (자동 검증) |
| **안전 장치 부재** | 위험 작업 전 백업 누락 | Hooks (자동 체크포인트) |
| **Context 비효율** | 전체 문서 로드 | Skills Progressive Disclosure |
| **Hooks 언어 혼재** | Shell/TS/Python 혼재 | Python 통일 (MoAI 방식) |

**참고**: /ms.implement의 Step 3에서 이미 TAG 블록 자동 삽입 기능이 구현되어 있음. 개선이 필요한 부분은 TAG 체인 무결성 자동 검증.

---

## 2. MoAI-ADK 4계층 아키텍처 분석

### 2.1. 계층별 역할

```
┌──────────────────────────────────────────────────────┐
│ Layer 1: COMMANDS (워크플로우 오케스트레이션)          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ /alfred:0-project, /alfred:1-plan, /alfred:2-run, ... │
│ → My-Spec 대응: /ms.* 명령어 (11개)                   │
└──────────────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────────────┐
│ Layer 2: SUB-AGENTS (전문 AI 팀, 19개)               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ spec-builder, code-builder, doc-syncer, tag-agent, ..│
│ → My-Spec 도입: 핵심 8개 우선 (점진적 확장)           │
└──────────────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────────────┐
│ Layer 3: SKILLS (재사용 가능 지식, 55개)              │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ moai-foundation-trust, moai-lang-python, ...          │
│ → My-Spec 도입: ms-foundation-*, ms-workflow-* (15개) │
└──────────────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────────────┐
│ Layer 4: HOOKS (런타임 가드레일, 이벤트 기반)          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ SessionStart, PreToolUse, PostToolUse, UserPromptSubmit│
│ → My-Spec 도입: 4개 핵심 Hook                         │
└──────────────────────────────────────────────────────┘
```

### 2.2. MoAI-ADK vs My-Spec 비교

| 측면 | MoAI-ADK (Alfred) | My-Spec (현재) | 통합 목표 |
|------|------------------|---------------|----------|
| **워크플로우** | /alfred:0-4 (5단계) | /ms.* (11단계) | My-Spec 유지 + 자동화 강화 |
| **AI 구조** | 19개 Sub-agents | 6개 기존 Agents | 5개 신규 Agent 추가 (총 11개) |
| **지식 관리** | 55개 Skills | Slash Commands | 15개 Skills 추가 |
| **안전 장치** | 자동 Hooks (Python) | Hooks (Shell/TS) | Python 통일 + 기능 통합 |
| **문서화** | CODE-FIRST (자동) | 수동 관리 | Living-Docs 자동화 |
| **Constitution** | CLAUDE.md | constitution.md | Constitution 유지 + Skills 활용 |
| **TAG 시스템** | @TAG 자동 삽입 | @TAG 자동 삽입 (✅ 이미 구현) | tag-auditor로 체인 검증 강화 |
| **경로 구조** | .moai/* | .specify/* | 경로 매핑 (.moai → .specify) |

---

## 3. 기능별 상세 매핑 및 통합 전략

### 3.1. Hooks (Layer 4) - 안전 인프라

#### 개념
이벤트 기반 자동 실행 스크립트 (<100ms 실행)

#### My-Spec 도입 계획

| Hook 이벤트 | 목적 | 구현 내용 | 우선순위 |
|------------|------|---------|---------|
| **SessionStart** | 프로젝트 상태 카드 | 언어 감지, Git 정보, SPEC 진행률, TAG 무결성 점수 | 🔴 High |
| **PreToolUse** | 위험 작업 차단 | Constitution 파일 수정 전 체크포인트, ≥5개 파일 수정 시 백업 | 🔴 High |
| **PostToolUse** | 자동 포맷팅 | TypeScript/Python 파일 수정 후 Prettier/Black 실행 | 🟠 Medium |
| **UserPromptSubmit** | JIT Context | /ms.plan → Constitution 자동 로드, /ms.implement → TRUST+TAG 로드 | 🟠 Medium |

#### 디렉토리 구조

```
.claude/hooks/ms/
├── ms_hooks.py              # Main entry point (CLI 인자 방식)
├── core/                    # 비즈니스 로직
│   ├── __init__.py         # HookPayload, HookResult
│   ├── project.py          # 언어 감지, Git 정보, SPEC 카운팅
│   ├── context.py          # JIT Context Retrieval
│   ├── checkpoint.py       # 자동 체크포인트 생성 (.specify 경로)
│   └── tags.py             # TAG 검색, 검증, 캐싱 + @IMMUTABLE 보호
└── handlers/                # 이벤트 핸들러
    ├── session.py          # SessionStart, SessionEnd
    ├── user.py             # UserPromptSubmit (constitution-injector 기능 통합)
    └── tool.py             # PreToolUse, PostToolUse
```

#### 기존 Hooks와의 관계

| 기존 Hook | 기능 | MoAI 통합 위치 | 처리 방안 |
|----------|------|--------------|---------|
| **constitution-injector.sh** | Task tool에 Constitution 주입 | handlers/user.py | 기능 이전 후 제거 |
| **tag-enforcer.ts** | @IMMUTABLE 보호, TAG 체인 검증 | core/tags.py | 기능 통합 후 제거 |
| **notify.sh** | 알림 (미사용) | N/A | 제거 |

#### 경로 매핑 규칙

| MoAI 경로 | My-Spec 경로 | 사유 |
|-----------|-------------|------|
| `.moai/checkpoints.log` | `.specify/checkpoints.log` | Constitution과 동일한 디렉토리 |
| `.moai/config.json` | `.specify/memory/constitution.md` | 기존 Constitution 사용 |
| `.moai/memory/*.md` | `.specify/memory/*.md` | 기존 구조 유지 |
| `.moai/specs/` | `specs/` | 기존 구조 유지 |

**중요**: core/checkpoint.py, core/project.py 등에서 .moai 경로 하드코딩 제거 필요.

#### Python 환경 요구사항

**Python 버전**: ≥3.13 (typing, pathlib,GIL 해제 지원)

**필수 패키지**: 없음 (표준 라이브러리만 사용)

**개발 패키지** (테스트용):
- pytest ≥7.0
- pytest-cov (커버리지)

**설치**:
```bash
pip install pytest pytest-cov
```

**실행 권한 부여**:
```bash
chmod +x .claude/hooks/ms/ms_hooks.py
```

#### 에러 핸들링 정책

**원칙**: Fail-open (에러 발생 시에도 세션 계속 진행)

**사유**:
- Hook 오류로 인해 전체 Claude Code 세션이 중단되는 것 방지
- 개발자가 Hook 없이도 작업 가능하도록 보장

**구현**:
```python
except Exception as e:
    error_response = {
        "continue": True,  # 세션 계속 진행
        "systemMessage": f"⚠️ My-Spec Hook error: {e}"
    }
    print(json.dumps(error_response))
    sys.exit(0)  # 성공 코드로 종료 (Claude Code가 계속 진행)
```

**로깅**: 에러는 stderr로 출력 (디버깅용)

#### 예상 효과
- ✅ 세션 시작 시 프로젝트 상태 즉시 파악 (5분 → 0초)
- ✅ 위험 작업 전 자동 백업 (데이터 손실 위험 98% 감소)
- ✅ Context 사용량 40% 감소 (JIT Retrieval)
- ✅ 기존 hooks 기능 100% 유지 + Python 통일

---

### 3.2. Skills (Layer 3) - 자동화 지식 캡슐

#### 개념
자동 트리거되는 재사용 가능 지식 모듈 (Progressive Disclosure)

#### Progressive Disclosure 전략

**3단계 로딩 전략**:

##### Level 1: Metadata (세션 시작 시 자동 로드)
```yaml
---
name: ms-foundation-constitution
tier: foundation
description: Constitution 자동 검증 (파일 크기, EARS, TRUST)
triggers: ["코드 검토 요청", "파일 수정"]
size: ~400 LOC
model: haiku  # 빠른 검증
---
```

##### Level 2: Instructions (Agent가 참조 시 로드)
```markdown
## When to Use
- 코드 작성 시 Constitution 위반 사항 자동 체크
- 파일 크기 ≤500 SLOC 검증
- EARS 패턴 검증
- TRUST 5원칙 검증

## Quick Start
1. Read Constitution file
2. Check file size
3. Validate EARS patterns
4. Report violations
```

##### Level 3: Resources (실제 사용 시 스트리밍)
- check_file_size.py (전체 코드)
- check_complexity.py (전체 코드)
- patterns.yaml (EARS 패턴)

**예상 효과**: Context 사용량 40% 감소

#### My-Spec 도입 계획

**Phase 1: Foundation Skills (5개)**

| Skill 명 | 트리거 조건 | 기능 | 파일 크기 | Model |
|---------|-----------|------|---------|-------|
| **ms-foundation-constitution** | 코드 검토 요청 시 | Constitution 자동 검증 (파일 크기, EARS, TRUST) | ~400 LOC | Haiku |
| **ms-foundation-trust** | /ms.analyze 시 | TRUST 5원칙 자동 검증 | ~450 LOC | Haiku |
| **ms-foundation-ears** | SPEC 작성 시 | EARS 패턴 검증, 금지 문구 탐지 | ~250 LOC | Haiku |
| **ms-workflow-tag-manager** | 코드 생성 시 | TAG 블록 자동 삽입/업데이트 | ~300 LOC | Haiku |
| **ms-workflow-living-docs** | 코드 수정 시 | API 문서 자동 업데이트 | ~350 LOC | Haiku |

**Phase 2: Language Packs (4개)**

| Skill 명 | 대상 언어 | 기능 | Model |
|---------|---------|------|-------|
| **ms-lang-typescript** | TypeScript | Best practices, strict mode, ESLint 규칙 | Haiku |
| **ms-lang-python** | Python | mypy, black, pytest 가이드 | Haiku |
| **ms-lang-go** | Go | gofmt, go test, 네이밍 규칙 | Haiku |
| **ms-lang-rust** | Rust | clippy, cargo test, ownership 패턴 | Haiku |

**Phase 3: Domain Skills (6개)**

| Skill 명 | 도메인 | 기능 | Model |
|---------|--------|------|-------|
| **ms-domain-backend** | Backend | API 설계, DB 패턴, 인증 | Haiku |
| **ms-domain-frontend** | Frontend | 컴포넌트 패턴, 상태 관리 | Haiku |
| **ms-domain-security** | Security | OWASP Top 10, 입력 검증 | Haiku |
| **ms-domain-testing** | Testing | AAA 패턴, 경계값 테스트 | Haiku |
| **ms-domain-performance** | Performance | 병목 탐지, 최적화 패턴 | Haiku |
| **ms-domain-devops** | DevOps | CI/CD, Docker, K8s | Haiku |

#### 디렉토리 구조

```
.claude/skills/
├── ms-foundation-constitution/
│   ├── SKILL.md              # Level 1-2 (Metadata + Instructions)
│   ├── check_file_size.py    # Level 3 (Resources)
│   └── check_complexity.py   # Level 3
├── ms-foundation-trust/
│   ├── SKILL.md
│   └── trust_validator.py
├── ms-foundation-ears/
│   ├── SKILL.md
│   └── patterns.yaml
├── ms-workflow-tag-manager/
│   ├── SKILL.md
│   └── tag_templates.json
├── ms-workflow-living-docs/
│   └── SKILL.md
├── ms-lang-typescript/
│   └── SKILL.md
├── ms-lang-python/
│   └── SKILL.md
└── ms-domain-backend/
    └── SKILL.md
```

#### 명명 규칙

```
ms-{tier}-{purpose}

Tier:
- foundation: 핵심 원칙 (constitution, trust, ears)
- workflow: /ms.* 명령 보조
- lang: 언어별 Best Practices
- domain: 도메인별 전문화
```

#### 예상 효과
- ✅ Constitution 준수율 70% → 95%
- ✅ TAG 블록 자동 삽입 (100% 일관성)
- ✅ Context 사용량 40% 감소 (Progressive Disclosure)
- ✅ Skills 자동 로딩 (세션 시작 시 Metadata만)

---

### 3.3. Living-Docs (CODE-FIRST) - 문서 자동 동기화

#### 개념
코드가 진실의 원천, 문서는 자동 생성

#### 전통적 DOC-FIRST vs CODE-FIRST

| Aspect | DOC-FIRST (기존) | CODE-FIRST (MoAI-ADK) |
|--------|-----------------|----------------------|
| **진실의 원천** | 문서 | 코드 |
| **업데이트 주체** | 개발자 수동 | 자동 스캔 (TAG 기반) |
| **일관성 보장** | ❌ (사람 실수) | ✅ (자동 검증) |
| **유지보수 부담** | 높음 (문서 따로 관리) | 낮음 (코드만 관리) |
| **신뢰도** | 시간 경과 시 감소 | 항상 100% |

#### My-Spec 통합 방안

**1. /ms.sync 명령어 추가 (Universal Document Sync)**
```markdown
---
description: "Universal document synchronization (Living Document)"
---

# /ms.sync - Universal Document Synchronization

통합 문서 동기화 시스템 (기존 ms.update-docs 대체)

Delegates to `doc-syncer` agent:
1. Git 변경 파일 확인
2. 문서 타입별 동기화 (병렬 실행):
   - API Docs (TAG 기반): docs/api/{TAG}.md
   - Dev Daily (작업 로그): docs/dev_daily.md
   - README (현재 상태): README.md
3. TAG 체인 무결성 검증
4. 동기화 보고서 생성

Usage:
/ms.sync               # 현재 세션 변경분 (기본)
/ms.sync AUTH-001      # 특정 TAG만
/ms.sync --docs=api    # API 문서만
/ms.sync --docs=dev    # 개발 일지만
/ms.sync --docs=readme # README만
/ms.sync --all         # 전체 재생성
```

**통합 효과**:
- ✅ 중복 제거: 기존 ms.update-docs, fin, finq의 문서 업데이트 로직 통합
- ✅ 단일 진입점: 모든 문서 동기화 → /ms.sync
- ✅ 유지보수: 문서 로직이 1곳에 집중
- ✅ 확장성: 새 문서 타입 추가 용이

**2. doc-syncer Sub-Agent 구현**
```yaml
---
name: doc-syncer
description: "Universal document sync - CODE-FIRST 원칙 기반"
tools: Read, Write, Edit, Grep, Glob
model: haiku  # 빠른 문서 처리
---

Phase 1: Git Diff 분석 (2-3분)
- Git 상태 확인
- 변경된 파일 감지
- 주요 변경사항 패턴 매칭

Phase 2: 병렬 문서 동기화 (5-10분)
- API Docs (TAG 기반): CODE 스캔 (ripgrep @TAG) → docs/api/{TAG}.md
- Dev Daily: Git diff → AI 요약 → docs/dev_daily.md
- README: 주요 변경 감지 시 현재 상태 재작성 → README.md

Phase 3: 품질 검증 (3-5분)
- TAG 체인 무결성 검사
- 문서-코드 일치 확인
- 동기화 보고서 생성
```

**3. fin/finq 워크플로우 통합**
```bash
# fin: 문서 동기화 → CI 체크 → 커밋 & 푸시
/fin
  ↓
ms.sync(docs="all")  # api + dev + readme 모두 업데이트
  ↓
make ci              # CI 체크
  ↓
git commit && push

# finq: 문서 동기화 → 커밋 & 푸시 (CI 생략)
/finq
  ↓
ms.sync(docs="all")  # api + dev + readme 모두 업데이트
  ↓
git commit && push   # CI 생략
```

**변경 사항**:
- ✅ `/ms.update-docs` 제거 → `/ms.sync`로 완전 대체
- ✅ `/fin`, `/finq` 리팩토링 → 문서 로직 제거, ms.sync 호출로 단순화
- ✅ 중복 코드 90% 감소 (Git diff 분석 3회 → 1회)

**4. TAG 체인 통합**
```
@SPEC:AUTH-001  (요구사항 명세)
    ↓
@TEST:AUTH-001  (테스트 코드)
    ↓
@CODE:AUTH-001  (구현 코드)
    ↓
@DOC:AUTH-001   (API 문서) ← 자동 생성
```

**5. 프로젝트 타입별 조건부 문서 생성**

| 프로젝트 타입 | 생성 문서 |
|--------------|----------|
| **Web API** | API.md, endpoints.md |
| **CLI Tool** | CLI_COMMANDS.md, usage.md |
| **Library** | API_REFERENCE.md, modules.md |
| **Frontend** | components.md, styling.md |

#### 예상 효과
- ✅ 문서 동기화 시간 93% 감소 (30분 → 2분)
- ✅ 문서 정확도 100% (항상 최신)
- ✅ 개발자 부담 0 (TAG만 달면 자동)

---

### 3.4. Sub-Agents (Layer 2) - 전문 AI 팀

#### 개념
역할 분산, Agent Persona 패턴

#### My-Spec 도입 계획

**Phase 0: 기존 Agents (이미 존재 ✅)**

| Agent | Model | 역할 | 위임 명령어 | 상태 |
|-------|-------|------|-----------|------|
| **codebase-explorer** 🔍 | Gemini CLI | 코드베이스 패턴 탐색, 유사 기능 찾기 | /ms.plan 보조 | ✅ 구현 완료 |
| **constitution-extractor** 📜 | Codex CLI | spec.md/plan.md → Constitution IX 추출 | /ms.constitution | ✅ 구현 완료 |
| **integration-designer** 🔗 | Claude Code | 복잡한 기능 통합 전략 설계 | /ms.plan 보조 | ✅ 구현 완료 |
| **tag-auditor** 🏷️ | Codex CLI | TAG 추적성 검증 (SPEC→TEST→CODE) | /ms.analyze | ✅ 구현 완료 |
| **trust-validator** ✅ | Codex CLI | TRUST 5 원칙 검증 (Level 1-3) | /ms.analyze | ✅ 구현 완료 |
| **library-researcher** 📚 | Gemini CLI | Context7 MCP로 최신 라이브러리 문서 조사 | /ms.plan 보조 | ✅ 구현 완료 |

**Phase 1: 핵심 Agents (신규 개발 필요)**

| Agent | Model | 역할 | 위임 명령어 | 개발 주차 |
|-------|-------|------|-----------|---------|
| **spec-builder** 🏗️ | Sonnet | SPEC 작성, EARS 강제 | /ms.specify | Week 9 |

**Phase 2: 워크플로우 Agents (신규 개발 필요)**

| Agent | Model | 역할 | 위임 명령어 | 개발 주차 |
|-------|-------|------|-----------|---------|
| **implementation-planner** 📋 | Sonnet | 구현 전략, 라이브러리 선택 | /ms.plan | Week 10 |
| **tdd-implementer** 💎 | Sonnet | RED → GREEN → REFACTOR | /ms.implement | Week 10-11 |
| **doc-syncer** 📖 | Haiku | Living Document 동기화 | /ms.sync (신규) | Week 7-8 |

**Phase 3: 고급 Agents (신규 개발 필요)**

| Agent | Model | 역할 | 위임 명령어 | 개발 주차 |
|-------|-------|------|-----------|---------|
| **debug-helper** 🔍 | Sonnet | 실패 진단, 수정 가이드 | 에러 발생 시 | Week 12 |
| **quality-gate** 🛡️ | Haiku | 릴리스 게이트, 커버리지 델타 | /fin | Week 12 |

**총 에이전트 수**: 기존 6개 + 신규 5개 = **11개**

#### 모델 선택 가이드

| Model | 사용 사례 | 대표 Sub-agents | 선택 이유 |
|-------|---------|---------------|---------|
| **Haiku** | 문서 동기화, TAG 검증, 패턴 기반 작업 | doc-syncer, tag-auditor, quality-gate, Skills | 빠른 처리, 패턴 기반 작업 |
| **Sonnet** | SPEC 작성, 구현 계획, 디버깅, 통합 설계 | spec-builder, implementation-planner, tdd-implementer, debug-helper | 깊은 추론, 창의적 문제 해결 |
| **Gemini CLI** | 코드베이스 탐색, 라이브러리 조사 | codebase-explorer, library-researcher | 빠른 검색, Context7 MCP |
| **Codex CLI** | Constitution 추출, TAG 검증, TRUST 검증 | constitution-extractor, tag-auditor, trust-validator | 코드 분석, 정적 검증 |

#### Agent Persona 패턴 예시

```yaml
## 🎭 Agent Persona (doc-syncer)

Icon: 📖
Job: Technical Writer
Expertise: Document-Code Synchronization
Role: 코드-문서 완벽 일관성 보장 전문가
Goal: 실시간 동기화 및 @TAG 기반 추적 가능 문서 관리

### Expert Traits
- Mindset: 코드 변경과 문서 업데이트를 하나의 원자적 작업으로 취급
- Decision Criteria: 문서-코드 일관성, @TAG 무결성, 추적성 완전성
- Communication Style: 동기화 범위와 영향 명확히 분석 및 보고
- Specialized Area: Living Document, API 문서 자동 생성, TAG 추적성 검증
```

#### Agent 협업 패턴

```
User: /ms.implement

My-Spec Orchestrator (Claude) →
    ↓
┌──────────────────────────────────────────┐
│ Phase 1: library-researcher (Gemini CLI)│
│ - Context7 MCP 최신 라이브러리 문서 조사  │
│ - API 패턴 추출                          │
├──────────────────────────────────────────┤
│ Phase 2: implementation-planner (Sonnet) │
│ - Read SPEC                              │
│ - Analyze requirements                   │
│ - Select libraries (library-researcher 참고) │
│ - Design TAG chain                       │
├──────────────────────────────────────────┤
│ Phase 3: tdd-implementer (Sonnet)        │
│ - RED: Write failing test (@TEST:ID)     │
│ - GREEN: Implement code (@CODE:ID)       │
│ - REFACTOR: Improve quality              │
│ - Step 3: TAG 블록 자동 삽입 (기존 기능)  │
├──────────────────────────────────────────┤
│ Auto-invoked: tag-auditor (Codex CLI)    │
│ - Scan TAG blocks                        │
│ - Verify chain integrity (SPEC→TEST→CODE)│
├──────────────────────────────────────────┤
│ Auto-invoked: trust-validator (Codex CLI)│
│ - TRUST 5 principles (Level 2)           │
│ - Coverage ≥85%                          │
└──────────────────────────────────────────┘
```

#### 예상 효과
- ✅ SPEC 작성 시간 75% 감소 (60분 → 15분)
- ✅ TAG 검증 시간 98% 감소 (15분 → 10초)
- ✅ 개발자 인지 부하 60% 감소

---

## 4. 통합 순서 및 전략

### 4.1. 의존성 분석

```
Hooks (Layer 4) ← 독립적
    ↓
Skills (Layer 3) ← Hooks와 독립적
    ↓
Sub-Agents (Layer 2) ← Skills 활용
    ↓
Living-Docs ← Sub-agents(doc-syncer) 필요
```

### 4.2. 추천 통합 순서 (순차적, Test-First)

#### **Phase 1: Hooks (Week 0.5-3)** 🔴 CRITICAL

**목표**: 안전 인프라 구축 + 기존 hooks 마이그레이션

##### **Phase 1.0: 기존 Hooks 마이그레이션 (Week 0.5, +4시간)**

**구현 항목**:
- [ ] 기존 hooks 분석 및 기능 명세 작성
  - [ ] constitution-injector.sh 기능 파악 (Task tool 트리거, Constitution 자동 주입)
  - [ ] tag-enforcer.ts 기능 파악 (@IMMUTABLE 보호, TAG 체인 검증)
  - [ ] notify.sh 사용 여부 확인 (미사용 시 제거)
- [ ] Python 환경 설정
  - [ ] Python 버전 ≥3.8 확인
  - [ ] pytest, pytest-cov 설치
  - [ ] `.claude/hooks/ms/` 디렉토리 생성
- [ ] 경로 매핑 규칙 문서화
  - [ ] .moai → .specify 경로 변환 규칙 작성
  - [ ] checkpoint.py, project.py 경로 하드코딩 확인
- [ ] 마이그레이션 전략 선택
  - [ ] **Option A (권장)**: 점진적 대체 (Week 1-3)
  - [ ] Option B: 병행 실행 (테스트 기간 필요)

**예상 시간**: 4시간

---

##### **Phase 1.1: SessionStart Hook (Week 1, TDD)**

**구현 항목**:
- [ ] **RED** (2-3시간)
  - [ ] `tests/hooks/test_session_hooks.py` 작성
    ```python
    def test_session_start_displays_project_status():
        result = run_hook("SessionStart", {"cwd": "."})
        assert "🚀 My-Spec Session Started" in result["message"]
        assert "Language" in result["message"]
        assert "Git Branch" in result["message"]

    def test_session_start_detects_language():
        result = run_hook("SessionStart", {"cwd": "."})
        assert result["language"] in ["python", "typescript", "go", "rust"]

    def test_session_start_shows_git_info():
        result = run_hook("SessionStart", {"cwd": "."})
        assert "branch" in result
        assert "status" in result
    ```
- [ ] **GREEN** (3-4시간)
  - [ ] `ms_hooks.py` 엔트리 포인트 구현 (CLI 인자 방식)
  - [ ] `core/__init__.py` 구현 (HookPayload, HookResult)
  - [ ] `core/project.py` 구현 (언어 감지, Git 정보, SPEC 카운팅)
  - [ ] `handlers/session.py` 구현 (SessionStart 핸들러)
- [ ] **REFACTOR** (1-2시간)
  - [ ] 코드 정리, 주석 추가
  - [ ] 에러 핸들링 개선 (Fail-open)
  - [ ] 경로 매핑 적용 (.moai → .specify)

**검증**:
- [ ] pytest 실행: `pytest tests/hooks/test_session_hooks.py -v`
- [ ] 커버리지 확인: `pytest --cov=.claude/hooks/ms/core --cov=.claude/hooks/ms/handlers`
- [ ] 수동 테스트: `echo '{"cwd": "."}' | python .claude/hooks/ms/ms_hooks.py SessionStart`

**예상 시간**: 6-9시간

---

##### **Phase 1.2: PreToolUse Hook (Week 2, TDD)**

**구현 항목**:
- [ ] **RED** (2-3시간)
  - [ ] `tests/hooks/test_pre_tool_use.py` 작성
    ```python
    def test_checkpoint_created_before_constitution_edit():
        result = run_hook("PreToolUse", {
            "tool_name": "Edit",
            "tool_input": {"file_path": ".specify/memory/constitution.md"}
        })
        assert result["checkpoint_created"] == True
        assert "before-critical-file-" in result["branch_name"]

    def test_checkpoint_created_before_bulk_edit():
        result = run_hook("PreToolUse", {
            "tool_name": "MultiEdit",
            "tool_input": {"edits": [{"file_path": f"file{i}.py"} for i in range(10)]}
        })
        assert result["checkpoint_created"] == True
        assert "before-refactor-" in result["branch_name"]

    def test_no_checkpoint_for_read_operations():
        result = run_hook("PreToolUse", {
            "tool_name": "Read",
            "tool_input": {"file_path": "test.py"}
        })
        assert result["checkpoint_created"] == False
    ```
- [ ] **GREEN** (4-5시간)
  - [ ] `core/checkpoint.py` 구현 (자동 체크포인트 생성)
    - [ ] detect_risky_operation() 구현
    - [ ] create_checkpoint() 구현 (.specify/checkpoints.log)
    - [ ] log_checkpoint() 구현
  - [ ] `handlers/tool.py` 구현 (PreToolUse 핸들러)
- [ ] **REFACTOR** (1-2시간)
  - [ ] 경로 하드코딩 제거 (.moai → .specify)
  - [ ] 에러 핸들링 개선

**검증**:
- [ ] pytest 실행: `pytest tests/hooks/test_pre_tool_use.py -v`
- [ ] 커버리지 ≥85%: `pytest --cov=.claude/hooks/ms`
- [ ] 체크포인트 로그 확인: `cat .specify/checkpoints.log`

**예상 시간**: 7-10시간

---

##### **Phase 1.3: 기존 Hooks 기능 이전 (Week 3)**

**구현 항목**:
- [ ] **constitution-injector.sh → handlers/user.py** (2시간)
  - [ ] UserPromptSubmit 핸들러 구현
  - [ ] Task tool 감지 시 Constitution 자동 주입
  - [ ] 테스트 작성: `tests/hooks/test_user_prompt_submit.py`
- [ ] **tag-enforcer.ts → core/tags.py** (4-5시간)
  - [ ] TAG 검색 기능 (ripgrep 기반)
  - [ ] TAG 체인 포맷 검증 (validateTAGChainFormat)
  - [ ] @IMMUTABLE TAG 보호 (checkImmutability)
  - [ ] TAG 캐싱 (library version cache)
  - [ ] 테스트 작성: `tests/hooks/test_tags.py`
- [ ] **설정 파일 업데이트** (30분)
  - [ ] `.claude/settings.local.json`에 Hooks 설정 추가
    ```json
    {
      "permissions": { ... },
      "hooks": {
        "sessionStart": ".claude/hooks/ms/ms_hooks.py SessionStart",
        "userPromptSubmit": ".claude/hooks/ms/ms_hooks.py UserPromptSubmit",
        "preToolUse": ".claude/hooks/ms/ms_hooks.py PreToolUse",
        "postToolUse": ".claude/hooks/ms/ms_hooks.py PostToolUse"
      }
    }
    ```
- [ ] **기존 hooks 제거** (30분)
  - [ ] constitution-injector.sh 제거
  - [ ] tag-enforcer.ts 제거
  - [ ] notify.sh 제거 (미사용 확인 후)
- [ ] **통합 테스트** (1시간)
  - [ ] 모든 Hook 이벤트 테스트
  - [ ] 기존 hooks 기능 100% 이전 확인
  - [ ] 성능 확인 (<100ms)

**검증**:
- [ ] ✅ pytest 실행: `pytest tests/hooks/ -v`
- [ ] ✅ 커버리지 ≥85%: `pytest --cov=.claude/hooks/ms`
- [ ] ✅ 기존 hooks 기능 100% 이전 확인
- [ ] ✅ Claude Code 세션 시작 시 정상 작동

**예상 시간**: 8-9시간

---

**Phase 1 총 예상 시간**: 25-32시간 (기존 8-10시간에서 증가)

**Phase 1 완료 기준**:
- [ ] 기존 3개 hooks 기능 100% Python으로 이전
- [ ] 모든 Hook 이벤트 pytest 통과
- [ ] 커버리지 ≥85%
- [ ] Claude Code 세션 정상 작동
- [ ] 경로 매핑 완료 (.moai → .specify)
- [ ] 에러 핸들링 Fail-open 적용

---

#### **Phase 2: Skills (Week 4-6)** 🔴 CRITICAL

**목표**: 자동화 지식 캡슐 구축 (Small units 준수, Test-First)

##### **Phase 2.1: Foundation Core (Week 4, 3 Skills)**

**구현 항목**:

**1. ms-foundation-constitution** (3-4시간)
- [ ] **RED**
  - [ ] `tests/skills/test_constitution_skill.py` 작성
    ```python
    def test_check_file_size_under_limit():
        result = check_file_size("test.py", 300)  # 300 LOC
        assert result["passed"] == True

    def test_check_file_size_over_limit():
        result = check_file_size("test.py", 600)  # 600 LOC
        assert result["passed"] == False
        assert "500 SLOC" in result["message"]

    def test_check_complexity():
        result = check_complexity("def foo():\n  if a:\n    if b:\n      return")
        assert result["complexity"] <= 10
    ```
- [ ] **GREEN**
  - [ ] `.claude/skills/ms-foundation-constitution/SKILL.md` (Level 1-2)
  - [ ] `check_file_size.py` (Level 3)
  - [ ] `check_complexity.py` (Level 3)
- [ ] **REFACTOR**
  - [ ] Progressive Disclosure 적용 (3단계)
  - [ ] SKILL.md에 metadata 추가 (model: haiku, triggers, size)

**2. ms-foundation-trust** (3-4시간)
- [ ] **RED**
  - [ ] `tests/skills/test_trust_skill.py` 작성
- [ ] **GREEN**
  - [ ] `SKILL.md`
  - [ ] `trust_validator.py`
- [ ] **REFACTOR**

**3. ms-foundation-ears** (2-3시간)
- [ ] **RED**
  - [ ] `tests/skills/test_ears_skill.py` 작성
- [ ] **GREEN**
  - [ ] `SKILL.md`
  - [ ] `patterns.yaml` (EARS 패턴 정의)
- [ ] **REFACTOR**

**검증**:
- [ ] ✅ 각 Skill별 pytest 실행
- [ ] ✅ Progressive Disclosure 3단계 확인
- [ ] ✅ SKILL.md metadata 유효성 검증

**예상 시간**: 8-11시간

---

##### **Phase 2.2: Foundation Workflow (Week 5, 2 Skills)**

**구현 항목**:

**1. ms-workflow-tag-manager** (3-4시간)
- [ ] **RED**
  - [ ] `tests/skills/test_tag_manager_skill.py` 작성
- [ ] **GREEN**
  - [ ] `SKILL.md`
  - [ ] `tag_templates.json` (TAG 블록 템플릿)
- [ ] **REFACTOR**

**2. ms-workflow-living-docs** (2-3시간)
- [ ] **RED**
  - [ ] `tests/skills/test_living_docs_skill.py` 작성
- [ ] **GREEN**
  - [ ] `SKILL.md`
- [ ] **REFACTOR**

**검증**:
- [ ] ✅ TAG 블록 자동 생성 확인
- [ ] ✅ Living-Docs 스캔 기능 확인

**예상 시간**: 5-7시간

---

##### **Phase 2.3: Language Packs (Week 6, 2 Skills)**

**구현 항목**:

**1. ms-lang-typescript** (2-3시간)
- [ ] **RED**
  - [ ] `tests/skills/test_typescript_skill.py` 작성
- [ ] **GREEN**
  - [ ] `SKILL.md` (TypeScript best practices)
- [ ] **REFACTOR**

**2. ms-lang-python** (2-3시간)
- [ ] **RED**
  - [ ] `tests/skills/test_python_skill.py` 작성
- [ ] **GREEN**
  - [ ] `SKILL.md` (Python best practices)
- [ ] **REFACTOR**

**검증**:
- [ ] ✅ 언어별 best practices 검증
- [ ] ✅ Claude Code에서 Skills 자동 로딩 확인

**예상 시간**: 4-6시간

---

**Phase 2 총 예상 시간**: 17-24시간 (기존 12-15시간에서 증가)

**Phase 2 완료 기준**:
- [ ] 7개 Skills 구현 완료 (Small units 준수: 2-3개씩 분할)
- [ ] 모든 Skills pytest 통과
- [ ] Progressive Disclosure 3단계 적용
- [ ] Context 사용량 40% 감소 측정

---

#### **Phase 3: Living-Docs (Week 7-8)** 🔴 CRITICAL

**목표**: 통합 문서 동기화 시스템 구축 (Test-First)

##### **Phase 3.1: /ms.sync 명령어 구현 (Week 7, TDD)**

**구현 항목**:
- [ ] **RED** (2-3시간)
  - [ ] `tests/commands/test_ms_sync.py` 작성
    ```python
    def test_sync_api_docs():
        result = run_command("/ms.sync --docs=api")
        assert "docs/api/AUTH-001.md" in result["files_updated"]

    def test_sync_dev_daily():
        result = run_command("/ms.sync --docs=dev")
        assert "docs/dev_daily.md" in result["files_updated"]

    def test_sync_all():
        result = run_command("/ms.sync --all")
        assert len(result["files_updated"]) >= 3  # api + dev + readme
    ```
- [ ] **GREEN** (3-4시간)
  - [ ] `.claude/commands/ms.sync.md` 작성
  - [ ] doc-syncer Agent 호출 로직
- [ ] **REFACTOR** (1시간)
  - [ ] 에러 핸들링 개선

**예상 시간**: 6-8시간

---

##### **Phase 3.2: doc-syncer Agent 구현 (Week 7-8, TDD)**

**구현 항목**:
- [ ] **RED** (2-3시간)
  - [ ] `tests/agents/test_doc_syncer.py` 작성
- [ ] **GREEN** (5-7시간)
  - [ ] `.claude/agents/doc-syncer.md` 작성
  - [ ] Phase 1: Git diff 분석
  - [ ] Phase 2: 병렬 문서 동기화 (api, dev, readme)
  - [ ] Phase 3: TAG 체인 검증
- [ ] **REFACTOR** (2시간)
  - [ ] 성능 최적화 (병렬 처리)

**예상 시간**: 9-12시간

---

##### **Phase 3.3: fin/finq 리팩토링 (Week 8)**

**구현 항목**:
- [ ] `/fin` 리팩토링 (1-2시간)
  - [ ] 문서 로직 제거
  - [ ] ms.sync(docs="all") 호출 추가
- [ ] `/finq` 리팩토링 (1-2시간)
  - [ ] 문서 로직 제거
  - [ ] ms.sync(docs="all") 호출 추가
- [ ] **테스트** (1시간)
  - [ ] `/fin` 실행 확인 (문서 동기화 → CI → 커밋)
  - [ ] `/finq` 실행 확인 (문서 동기화 → 커밋)

**예상 시간**: 3-5시간

---

##### **Phase 3.4: ms.update-docs 제거 (Week 8)**

**구현 항목**:
- [ ] `.claude/commands/ms.update-docs.md` 제거
- [ ] 기존 ms.update-docs 호출 코드 검색 및 제거
- [ ] 문서 업데이트 (README, 가이드)

**예상 시간**: 1-2시간

---

**Phase 3 총 예상 시간**: 19-27시간 (기존 12-15시간에서 증가)

**Phase 3 완료 기준**:
- [ ] /ms.sync --docs=api → TAG 기반 문서 생성
- [ ] /ms.sync --docs=dev → dev_daily.md 업데이트
- [ ] /ms.sync --docs=readme → README.md 업데이트
- [ ] /fin 실행 시 모든 문서 자동 동기화 (CI 포함)
- [ ] /finq 실행 시 모든 문서 자동 동기화 (CI 생략)
- [ ] TAG 체인 무결성 100%
- [ ] 중복 코드 90% 감소 검증
- [ ] ms.update-docs 완전 제거

---

#### **Phase 4: Sub-Agents (Week 9-12)** 🟠 HIGH

**목표**: 전문 AI 팀 구축

##### **Phase 4.0: 기존 Agents 활용 방안 정립 (Week 9, 1-2시간)**

**구현 항목**:
- [ ] tag-auditor를 /ms.analyze에 통합
- [ ] trust-validator를 /ms.analyze에 통합 (Level 2)
- [ ] library-researcher를 /ms.plan에 통합
- [ ] codebase-explorer를 /ms.plan 보조로 활용
- [ ] constitution-extractor는 /ms.constitution에서 이미 활용 중 (확인만)
- [ ] integration-designer를 /ms.plan 보조로 활용

**예상 시간**: 1-2시간

---

##### **Phase 4.1: spec-builder (Week 9, TDD)**

**구현 항목**:
- [ ] **RED** (2-3시간)
  - [ ] `tests/agents/test_spec_builder.py` 작성
- [ ] **GREEN** (4-5시간)
  - [ ] `.claude/agents/spec-builder.md` 작성
  - [ ] EARS 패턴 강제
  - [ ] SPEC 템플릿 생성
- [ ] **REFACTOR** (1-2시간)

**예상 시간**: 7-10시간

---

##### **Phase 4.2: implementation-planner (Week 10, TDD)**

**구현 항목**:
- [ ] **RED** (2-3시간)
  - [ ] `tests/agents/test_implementation_planner.py` 작성
- [ ] **GREEN** (4-5시간)
  - [ ] `.claude/agents/implementation-planner.md` 작성
  - [ ] library-researcher 협업
  - [ ] codebase-explorer 협업
- [ ] **REFACTOR** (1-2시간)

**예상 시간**: 7-10시간

---

##### **Phase 4.3: tdd-implementer (Week 10-11, TDD)**

**구현 항목**:
- [ ] **RED** (2-3시간)
  - [ ] `tests/agents/test_tdd_implementer.py` 작성
- [ ] **GREEN** (5-7시간)
  - [ ] `.claude/agents/tdd-implementer.md` 작성
  - [ ] RED → GREEN → REFACTOR 구현
  - [ ] TAG 자동 삽입 (기존 기능 유지)
- [ ] **REFACTOR** (2-3시간)

**예상 시간**: 9-13시간

---

##### **Phase 4.4: debug-helper (Week 12, TDD)**

**구현 항목**:
- [ ] **RED** (1-2시간)
  - [ ] `tests/agents/test_debug_helper.py` 작성
- [ ] **GREEN** (3-4시간)
  - [ ] `.claude/agents/debug-helper.md` 작성
- [ ] **REFACTOR** (1시간)

**예상 시간**: 5-7시간

---

##### **Phase 4.5: quality-gate (Week 12, TDD)**

**구현 항목**:
- [ ] **RED** (1-2시간)
  - [ ] `tests/agents/test_quality_gate.py` 작성
- [ ] **GREEN** (2-3시간)
  - [ ] `.claude/agents/quality-gate.md` 작성
- [ ] **REFACTOR** (1시간)

**예상 시간**: 4-6시간

---

**Phase 4 총 예상 시간**: 33-48시간 (기존 20-25시간에서 증가)

**Phase 4 완료 기준**:
- [ ] /ms.analyze → tag-auditor + trust-validator 자동 실행 (기존 Agents 활용)
- [ ] /ms.specify → spec-builder 위임 (신규)
- [ ] /ms.plan → implementation-planner 위임 (신규, library-researcher/codebase-explorer 협업)
- [ ] /ms.implement → tdd-implementer 위임 (신규, TAG 자동 삽입 기존 기능 유지)
- [ ] 모든 Agent pytest 통과
- [ ] Agent 협업 패턴 검증

---

### 4.3. 통합 일정 요약 (Test-First 반영)

| Phase | 내용 | 기존 예상 시간 | 수정 예상 시간 | 주차 |
|-------|------|--------------|--------------|------|
| **Phase 1** | Hooks (기존 마이그레이션 + TDD) | 8-10시간 | **25-32시간** | Week 0.5-3 |
| **Phase 2** | Skills (Small units + TDD) | 12-15시간 | **17-24시간** | Week 4-6 |
| **Phase 3** | Living-Docs (TDD) | 12-15시간 | **19-27시간** | Week 7-8 |
| **Phase 4** | Sub-Agents (TDD) | 20-25시간 | **33-48시간** | Week 9-12 |
| **총 예상 시간** | | **52-65시간** | **94-131시간** | **12주** |

**주요 변경사항**:
- ✅ 기존 hooks 마이그레이션 추가 (Phase 1.0, +4시간)
- ✅ Test-First 원칙 적용 (모든 Phase에 RED → GREEN → REFACTOR)
- ✅ Small units 준수 (Phase 2 세분화)
- ✅ 통합 기간: 10주 → 12주 (+2주)

---

### 4.4. 위험 완화 체크리스트 (구현 전 검증)

#### Phase 1 착수 전 필수 체크리스트

**설정 파일**:
- [ ] settings.local.json 존재 확인
- [ ] hooks 섹션 추가 계획 수립
- [ ] ~~settings.json 생성 계획~~ (제거, settings.local.json 사용)

**경로 매핑**:
- [ ] .moai → .specify 경로 변환 규칙 문서화
- [ ] checkpoint.py, project.py 경로 하드코딩 확인
- [ ] ripgrep으로 .moai 키워드 검색: `rg "\.moai" -n`

**기존 Hooks**:
- [ ] constitution-injector.sh 기능 명세 작성
- [ ] tag-enforcer.ts 기능 명세 작성
- [ ] notify.sh 사용 여부 확인 (미사용 시 제거)
- [ ] 마이그레이션 전략 선택 (점진적 대체 vs 병행)

**Python 환경**:
- [ ] Python 버전 ≥3.8 확인
- [ ] pytest 설치: `pip install pytest pytest-cov`
- [ ] ms_hooks.py 실행 권한 부여: `chmod +x .claude/hooks/ms/ms_hooks.py`

**Test-First 준비**:
- [ ] tests/hooks/ 디렉토리 생성
- [ ] test_session_hooks.py 템플릿 작성
- [ ] pytest 실행 확인: `pytest tests/hooks/ -v`

**명명 규칙 변환**:
- [ ] alfred → ms 전역 치환 계획
- [ ] .moai → .specify 경로 변환 계획
- [ ] Alfred → My-Spec 주석 업데이트 계획
- [ ] @CODE:HOOKS-REFACTOR-001 → @CODE:MS-HOOKS-001 (TAG ID 재할당)

---

### 4.5. 대안: 병렬 통합 (동시 개발)

**독립성 분석 결과**: Hooks와 Skills는 독립적 → 병렬 개발 가능 (단, Test-First 준수 필요)

#### **Track A: 안전 + 자동화 (Week 0.5-6)** 👥 병렬 개발

```
Developer A: Hooks 구현 (Week 0.5-3)
  → Phase 1.0: 기존 hooks 마이그레이션
  → Phase 1.1: SessionStart Hook (TDD)
  → Phase 1.2: PreToolUse Hook (TDD)
  → Phase 1.3: 기존 hooks 기능 이전

Developer B: Skills 구현 (Week 4-6)
  → Phase 2.1: Foundation Core (3 Skills, TDD)
  → Phase 2.2: Foundation Workflow (2 Skills, TDD)
  → Phase 2.3: Language Packs (2 Skills, TDD)

→ Week 6 완료 시 통합 테스트
```

#### **Track B: 문서화 (Week 7-8)** 👤 순차 개발

```
Track A 완료 후:
→ Phase 3: Living-Docs 구현 (doc-syncer Agent, ms.sync)
```

#### **Track C: AI 팀 (Week 9-12)** 👤 순차 개발

```
Track B 완료 후:
→ Phase 4: Sub-Agents 구현 (5개 신규 + 6개 기존 활용)
```

**병렬 개발 시 이점**:
- ✅ 전체 기간 단축 (14주 → 12주)
- ✅ 개발자 2명 투입 시 효율 극대화
- ✅ 각 Track 독립 테스트 가능

**병렬 개발 시 위험**:
- ⚠️ 통합 시 충돌 가능성 (Week 6 통합 테스트 필수)
- ⚠️ 개발자 간 커뮤니케이션 비용
- ⚠️ Test-First 원칙 준수 필요 (양쪽 모두)

---

## 5. 기대 효과

### 5.1. 정량적 효과

| 메트릭 | Before (현재) | After (통합 후) | 개선율 |
|-------|--------------|----------------|--------|
| **문서 동기화 시간** | 30분 (수동) | 2분 (자동) | **93% ↓** |
| **TAG 검증 시간** | 15분 (수동 검색) | 10초 (자동 스캔) | **98% ↓** |
| **SPEC 작성 시간** | 60분 (처음부터) | 15분 (Agent 지원) | **75% ↓** |
| **Constitution 준수율** | ~70% (수동 검증) | 95%+ (자동 강제) | **25% ↑** |
| **문서 정확도** | ~60% (낙후) | 100% (실시간 동기화) | **40% ↑** |
| **개발자 인지 부하** | 높음 (11개 명령 숙지) | 낮음 (Agent가 처리) | **60% ↓** |
| **데이터 손실 위험** | 중간 (수동 백업) | 낮음 (자동 체크포인트) | **98% ↓** |
| **Context 사용량** | 100% (전체 로드) | 60% (JIT Retrieval) | **40% ↓** |

### 5.2. 정성적 효과

**1. 개발자 경험 향상**:
- ❌ Before: "TAG 블록을 매번 수동으로 달아야 해"
- ✅ After: "tag-manager Skill이 알아서 삽입해줘"

**2. 신뢰성 향상**:
- ❌ Before: "6개월 된 문서는 믿을 수 없어"
- ✅ After: "문서는 항상 최신이야 (CODE-FIRST)"

**3. 온보딩 시간 단축**:
- ❌ Before: "새 팀원이 Constitution 전체를 읽어야 해" (3일)
- ✅ After: "Skills가 자동으로 가이드해줘" (1일)

**4. 품질 일관성**:
- ❌ Before: "개발자마다 TAG 형식이 달라"
- ✅ After: "tag-manager Skill이 일관된 형식 강제"

**5. 유지보수 비용 절감**:
- ❌ Before: "Constitution 변경 시 11개 명령어 수정"
- ✅ After: "Skills만 업데이트하면 모든 Agent 반영"

**6. 기존 hooks 기능 유지**:
- ✅ constitution-injector.sh 기능 100% 유지 (Python으로 전환)
- ✅ tag-enforcer.ts 기능 100% 유지 + 강화 (TAG 캐싱 추가)
- ✅ 언어 통일 (Shell/TS → Python)

---

## 6. 위험 요소 및 대응 방안

### 6.1. 기술적 위험

| 위험 | 영향 | 확률 | 대응 방안 |
|------|------|------|----------|
| **Agent 간 충돌** | 높음 | 중간 | 명확한 책임 분리, Agent Persona 패턴 적용 |
| **Context 오버플로우** | 중간 | 높음 | Progressive Disclosure, Haiku 활용 |
| **TAG 형식 불일치** | 높음 | 낮음 | tag-manager Skill 자동 검증, 템플릿 제공 |
| **문서 생성 오류** | 중간 | 중간 | 수동 검토 단계 추가, 품질 검증 체크리스트 |
| **Hook 실행 실패** | 높음 | 낮음 | Fail-open 정책, 에러 로그 명확화 |
| **기존 hooks 마이그레이션 실패** | 높음 | 중간 | Phase 1.0 마이그레이션 전략 (점진적 대체) |
| **경로 매핑 오류** | 중간 | 중간 | .moai → .specify 경로 매핑 규칙 문서화 |

### 6.2. 조직적 위험

| 위험 | 영향 | 확률 | 대응 방안 |
|------|------|------|----------|
| **학습 곡선** | 중간 | 높음 | 단계적 도입, 문서화, 실습 프로젝트 |
| **기존 워크플로우 저항** | 높음 | 중간 | 점진적 마이그레이션, 기존 명령어 유지 |
| **유지보수 부담 증가** | 중간 | 낮음 | Agent/Skill 템플릿화, 자동화 테스트 |

### 6.3. 성능 위험

| 위험 | 영향 | 확률 | 대응 방안 |
|------|------|------|----------|
| **응답 지연** | 중간 | 중간 | Haiku 우선 사용, 병렬 Agent 실행 |
| **비용 증가** | 높음 | 중간 | Haiku/Sonnet 적절 배분, 캐싱 활용 |
| **Hook 실행 시간 초과** | 중간 | 낮음 | <100ms 제약 준수, 복잡한 로직 Sub-agent 위임 |

---

## 7. 성공 기준

### 7.1. 3개월 후 달성 목표

- ✅ Hooks 시스템 가동 (안전성 98% 향상)
  - [ ] 기존 3개 hooks 기능 100% Python으로 이전
  - [ ] SessionStart, PreToolUse 정상 작동
  - [ ] 체크포인트 자동 생성 (.specify/checkpoints.log)
- ✅ 핵심 7개 Skills 운영 (자동화율 70% 달성)
  - [ ] Foundation Core (3개)
  - [ ] Foundation Workflow (2개)
  - [ ] Language Packs (2개)
- ✅ Living-Docs 시스템 가동 (문서 정확도 100%)
  - [ ] /ms.sync 정상 작동
  - [ ] fin/finq 통합 완료
- ✅ 기존 6개 Agents 활용 (tag-auditor, trust-validator, library-researcher 등)
- ✅ 신규 2개 Agent 운영 (spec-builder, doc-syncer)
- ✅ 개발자 피드백 긍정적 (학습 곡선 수용 가능)

### 7.2. 6개월 후 달성 목표

- ✅ 11개 Agents 완전 가동 (기존 6개 + 신규 5개)
- ✅ 15개 Skills 라이브러리 완성
- ✅ CI/CD 완전 통합
- ✅ 문서 동기화 시간 95% 감소
- ✅ Constitution 준수율 95% 이상
- ✅ 신규 팀원 온보딩 시간 70% 단축
- ✅ Context 사용량 40% 감소 (Progressive Disclosure)

---

## 8. 최종 권장사항

### 8.1. 통합 순서 (최종)

**추천 방식: 순차적 통합 (리스크 최소화, Test-First)**

```
Phase 1: Hooks (Week 0.5-3)         🔴 CRITICAL
         ├─→ Phase 1.0: 기존 hooks 마이그레이션
         ├─→ Phase 1.1: SessionStart Hook (TDD)
         ├─→ Phase 1.2: PreToolUse Hook (TDD)
         └─→ Phase 1.3: 기존 hooks 기능 이전

Phase 2: Skills (Week 4-6)          🔴 CRITICAL
         ├─→ Phase 2.1: Foundation Core (3 Skills, TDD)
         ├─→ Phase 2.2: Foundation Workflow (2 Skills, TDD)
         └─→ Phase 2.3: Language Packs (2 Skills, TDD)

Phase 3: Living-Docs (Week 7-8)     🔴 CRITICAL
         ├─→ Phase 3.1: /ms.sync 구현 (TDD)
         ├─→ Phase 3.2: doc-syncer Agent (TDD)
         ├─→ Phase 3.3: fin/finq 리팩토링
         └─→ Phase 3.4: ms.update-docs 제거

Phase 4: Sub-Agents (Week 9-12)     🟠 HIGH
         ├─→ Phase 4.0: 기존 Agents 활용
         ├─→ Phase 4.1: spec-builder (TDD)
         ├─→ Phase 4.2: implementation-planner (TDD)
         ├─→ Phase 4.3: tdd-implementer (TDD)
         └─→ Phase 4.4-4.5: debug-helper, quality-gate (TDD)
```

**대안: 병렬 통합 (속도 우선, 리소스 충분 시)**

```
Track A: Hooks + Skills (Week 0.5-6)  👥 병렬 개발
         └─→ Week 6 통합 테스트

Track B: Living-Docs (Week 7-8)       👤 순차 개발
         └─→ Track A 완료 후

Track C: Sub-Agents (Week 9-12)       👤 순차 개발
         └─→ Track B 완료 후
```

### 8.2. 첫 번째 마일스톤 (Week 3 완료 시)

- ✅ SessionStart Hook → 프로젝트 상태 카드 자동 표시
- ✅ PreToolUse Hook → Constitution 파일 수정 전 체크포인트
- ✅ UserPromptSubmit Hook → Constitution 자동 주입 (constitution-injector.sh 기능)
- ✅ TAG 검증 → @IMMUTABLE 보호 + TAG 체인 검증 (tag-enforcer.ts 기능)
- ✅ 기존 hooks 제거 완료 (constitution-injector.sh, tag-enforcer.ts, notify.sh)
- ✅ Python 통일 완료

**검증 방법**:
```bash
# 1. SessionStart 테스트
claude code .
# → 프로젝트 상태 카드 표시 확인

# 2. PreToolUse 테스트
# Constitution 파일 수정 시도
# → 체크포인트 생성 확인 (.specify/checkpoints.log)

# 3. TAG 검증 테스트
# @IMMUTABLE TAG 수정 시도
# → 차단 메시지 확인

# 4. pytest 실행
pytest tests/hooks/ -v
# → 모든 테스트 통과 확인
```

### 8.3. 다음 단계

1. **즉시 시작**: Phase 1.0 (기존 hooks 마이그레이션 준비)
2. **병렬 준비**: Python 환경 설정, pytest 설치
3. **문서화**: 각 Phase 완료 시 사용 가이드 작성
4. **피드백 수집**: 실사용자 테스트 및 개선

---

## 9. 참고 자료

### 9.1. MoAI-ADK 문서
- [MoAI-ADK GitHub](https://github.com/modu-ai/moai-adk)
- [MoAI-ADK Skills 분석](/workspace/specter/docs/references/moai-adk-skills-analysis.md)
- [MoAI-ADK Living-Docs 분석](/workspace/specter/docs/references/moai-adk-living-docs-and-sub-agents-analysis.md)
- [MoAI-ADK Hooks 분석](/workspace/specter/docs/references/moai-adk-hooks-analysis.md)

### 9.2. Claude Code 공식 문서
- [Claude Code Skills](https://docs.claude.com/ko/docs/claude-code/skills)
- [Claude Code Hooks](https://docs.claude.com/en/docs/claude-code/hooks)
- [Claude Code Agents](https://docs.claude.com/en/docs/claude-code/agents)

### 9.3. My-Spec 프로젝트
- [Constitution Template](/workspace/specter/templates/constitution-template.md)
- [Slash Commands](/workspace/specter/.claude/commands/)
- [SKILLS.md](/workspace/specter/SKILLS.md)
- [Existing Hooks](/workspace/specter/.claude/hooks/)
  - constitution-injector.sh (Task tool 트리거)
  - tag-enforcer.ts (PreToolUse, @IMMUTABLE 보호)

---

**문서 버전**: 2.0.0
**최종 업데이트**: 2025-10-25
**작성자**: Claude Sonnet 4.5
**상태**: Ready for Implementation
**다음 단계**: Phase 1.0 (기존 hooks 마이그레이션 준비) 시작

**주요 변경사항 (v1.0.0 → v2.0.0)**:
- ✅ 기존 hooks 마이그레이션 전략 추가 (Phase 1.0)
- ✅ Test-First 원칙 전면 적용 (RED → GREEN → REFACTOR)
- ✅ Small units 준수 (Phase 2 세분화)
- ✅ settings.json → settings.local.json 수정
- ✅ 경로 매핑 규칙 추가 (.moai → .specify)
- ✅ Python 환경 요구사항 명시
- ✅ Progressive Disclosure 구현 전략
- ✅ 에러 핸들링 정책 (Fail-open)
- ✅ 모델 선택 가이드 추가
- ✅ 통합 일정 재조정 (10주 → 12주)
- ✅ 위험 완화 체크리스트 추가

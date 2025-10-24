# MoAI-ADK Living Document & Sub-Agents 분석

**분석 일자**: 2025-10-23
**분석 대상**: [modu-ai/moai-adk](https://github.com/modu-ai/moai-adk)
**목적**: Living Document 및 Sub-Agents 기능 분석 및 My-Spec 도입 계획 수립

---

## Executive Summary

MoAI-ADK의 핵심 차별화 요소는 **Skills** 외에도 **Living Document** 시스템과 **Sub-Agents** 아키텍처입니다. 이 두 기능은 Skills와 함께 4계층 아키텍처(Commands → Sub-agents → Skills → Hooks)를 구성하며, SPEC-First TDD 워크플로우를 자동화합니다.

**핵심 발견사항**:
- ✅ **Living Document**: CODE-FIRST 원칙 기반 자동 문서 동기화
- ✅ **Sub-Agents (12개)**: 각 워크플로우 단계별 전문 AI 팀
- ✅ **Agent Persona 패턴**: 역할, 전문성, 사고방식 명확화
- ✅ **Progressive Disclosure**: Sub-agents도 Skills처럼 JIT 로딩
- ✅ **Interactive Questions**: TUI 기반 사용자 승인 메커니즘

---

## 1. Living Document 기능 상세 분석

### 1.1. 개념 및 목적

**Living Document**는 "살아있는 문서"로, 코드 변경에 따라 자동으로 업데이트되는 문서를 의미합니다.

#### 전통적 문서화의 문제

```
❌ 기존 방식:
코드 작성 → 문서 작성 → 시간 경과 → 코드 수정 → 문서 방치 → 불일치
```

**결과**:
- 6개월 후: "문서가 정확한지 모르겠어요"
- 1년 후: "코드를 직접 읽는 게 빠르네요"
- 2년 후: "문서는 신뢰할 수 없어요"

#### MoAI-ADK의 Living Document 접근

```
✅ CODE-FIRST 방식:
코드 작성 → 코드 스캔 → TAG 추출 → 문서 자동 생성 → 항상 동기화
```

**핵심 원칙**:
1. **CODE-FIRST**: 코드가 진실의 원천 (Source of Truth)
2. **TAG-DRIVEN**: @TAG 체인으로 추적성 확보
3. **AUTO-SYNC**: `/alfred:3-sync` 한 명령으로 동기화
4. **INTEGRITY**: 문서-코드 불일치 자동 탐지

### 1.2. doc-syncer Agent 역할

**doc-syncer**는 Living Document 시스템을 전담하는 Sub-agent입니다.

#### Agent 메타데이터

```yaml
---
name: doc-syncer
description: "Use when: When automatic document synchronization based on code changes is required. Called from the /alfred:3-sync command."
tools: Read, Write, Edit, MultiEdit, Grep, Glob, TodoWrite
model: haiku  # 빠른 문서 처리에 최적화
---
```

#### Agent Persona

| 속성           | 값                                               |
|----------------|--------------------------------------------------|
| **Icon**       | 📖                                               |
| **Job**        | Technical Writer                                 |
| **Expertise**  | Document-Code Synchronization and API Documentation |
| **Role**       | 코드-문서 완벽 일관성 보장                         |
| **Goal**       | 실시간 동기화 및 @TAG 기반 추적 가능 문서 관리      |

**Agent Persona 패턴의 장점**:
- ✅ Agent의 역할과 책임 명확화
- ✅ 사용자가 Agent의 전문성 이해 용이
- ✅ Agent 간 협업 시 경계 명확
- ✅ 일관된 커뮤니케이션 스타일

#### doc-syncer 3단계 워크플로우

**Phase 1: 상태 분석 (2-3분)**

```bash
# Step 1: Git 상태 확인
git status --short
git diff --stat

# Step 2: CODE 스캔 (CODE-FIRST)
rg '@TAG' -n  # 전체 TAG 수 확인
rg '@SPEC:' -n .moai/specs/
rg '@CODE:' -n src/
rg '@TEST:' -n tests/
rg '@DOC:' -n docs/

# Step 3: 고아 TAG 탐지
rg '@CODE:AUTH-001' -n src/          # CODE 존재
rg '@SPEC:AUTH-001' -n .moai/specs/  # SPEC 미존재 → 고아
```

**Phase 2: 문서 동기화 실행 (5-10분)**

```markdown
## Code → Document 동기화

1. API 문서 업데이트
   - Read tool로 코드 파일 읽기
   - 함수/클래스 시그니처 추출
   - API 문서 자동 생성/업데이트
   - @CODE TAG 연결 확인

2. README 업데이트
   - 새 기능 섹션 추가
   - How-to 예제 동기화
   - 설치/설정 가이드 동기화

3. Architecture 문서
   - 구조적 변경 반영
   - 모듈 의존성 다이어그램 업데이트
   - @DOC TAG 추적
```

**Phase 3: 품질 검증 (3-5분)**

```bash
# TAG 무결성 검사
rg '@SPEC:' -c .moai/specs/  # SPEC TAG 개수
rg '@CODE:' -c src/          # CODE TAG 개수
rg '@TEST:' -c tests/        # TEST TAG 개수

# 불일치 탐지
if SPEC_COUNT != CODE_COUNT:
    echo "⚠️ TAG mismatch detected"

# 동기화 보고서 생성
cat > .moai/reports/sync-report.md <<EOF
# Sync Report

- Total TAGs: ${TOTAL}
- Synced: ${SYNCED}
- Orphans: ${ORPHANS}
- Chain Integrity: ${INTEGRITY}%
EOF
```

### 1.3. CODE-FIRST 원칙 상세

**CODE-FIRST**는 MoAI-ADK Living Document의 핵심 철학입니다.

#### 전통적 DOC-FIRST vs CODE-FIRST

| Aspect             | DOC-FIRST (전통)              | CODE-FIRST (MoAI-ADK)           |
|--------------------|------------------------------|---------------------------------|
| **진실의 원천**     | 문서                          | 코드                            |
| **업데이트 주체**   | 개발자 수동                    | 자동 스캔                        |
| **일관성 보장**     | ❌ (개발자 실수)               | ✅ (자동 검증)                   |
| **유지보수 부담**   | 높음 (문서 따로 관리)           | 낮음 (코드만 관리)                |
| **신뢰도**         | 시간 경과 시 감소              | 항상 100%                       |

#### CODE-FIRST 작동 방식

```
┌────────────────────────────────────────────────────────────┐
│ Step 1: 개발자가 코드 작성                                   │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ src/auth/service.py:                                       │
│ """                                                        │
│ @CODE:AUTH-001                                             │
│ @SPEC: .moai/specs/SPEC-AUTH-001/spec.md                   │
│ @TEST: tests/auth/test_service.py                          │
│ """                                                        │
│ def authenticate(username, password):                      │
│     ...                                                    │
├────────────────────────────────────────────────────────────┤
│ Step 2: /alfred:3-sync 실행 → doc-syncer 활성화           │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ rg '@CODE:AUTH-001' -n src/                                │
│ → 파일 경로, 함수 시그니처 추출                              │
├────────────────────────────────────────────────────────────┤
│ Step 3: API 문서 자동 생성                                  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ docs/api/AUTH-001.md:                                      │
│ # AUTH-001: User Authentication                            │
│                                                            │
│ **Status**: Implemented                                    │
│ **Last Updated**: 2025-10-23 (Auto-updated)                │
│                                                            │
│ ## API Reference                                           │
│ ### `authenticate(username, password)`                     │
│ ...                                                        │
└────────────────────────────────────────────────────────────┘
```

**핵심 이점**:
- ✅ **개발자 부담 0**: TAG만 달면 문서 자동 생성
- ✅ **항상 최신**: 코드 변경 시 즉시 반영
- ✅ **추적 가능**: TAG 체인으로 연결
- ✅ **신뢰 100%**: 코드가 진실의 원천

### 1.4. 프로젝트 타입별 조건부 문서 생성

doc-syncer는 프로젝트 타입을 자동 감지하여 필요한 문서만 생성합니다.

#### 프로젝트 타입 → 문서 매핑

| 프로젝트 타입 | 생성 문서                              |
|---------------|---------------------------------------|
| **Web API**   | API.md, endpoints.md (엔드포인트 문서) |
| **CLI Tool**  | CLI_COMMANDS.md, usage.md (명령어 문서) |
| **Library**   | API_REFERENCE.md, modules.md (함수/클래스 문서) |
| **Frontend**  | components.md, styling.md (컴포넌트 문서) |
| **Application**| features.md, user-guide.md (기능 설명) |

**조건부 생성 규칙**:
- ✅ 해당 기능이 있을 때만 생성
- ✅ 불필요한 문서 생성 방지
- ✅ 프로젝트 복잡도 최소화

**예시**: CLI Tool 프로젝트

```bash
# 프로젝트 타입 감지
if [[ -f "cli.py" || -f "main.py" ]]; then
    PROJECT_TYPE="cli-tool"
fi

# 조건부 문서 생성
if [[ "$PROJECT_TYPE" == "cli-tool" ]]; then
    generate_document "CLI_COMMANDS.md"  # ✅ 생성
    generate_document "usage.md"         # ✅ 생성
    # components.md는 생성 안 함 (필요 없음)
fi
```

### 1.5. TAG 체인 통합

Living Document는 TAG 체인과 긴밀히 통합되어 완벽한 추적성을 제공합니다.

#### TAG 체인 구조

```
@SPEC:AUTH-001  (요구사항 명세)
    ↓
@TEST:AUTH-001  (테스트 코드)
    ↓
@CODE:AUTH-001  (구현 코드)
    ↓
@DOC:AUTH-001   (API 문서)
```

#### TAG 블록 예시

**SPEC (.moai/specs/SPEC-AUTH-001/spec.md)**:
```markdown
<!-- @SPEC:AUTH-001 -->
# User Authentication Specification

## Requirements
WHEN user submits valid credentials, system SHALL issue JWT token.
...
```

**TEST (tests/auth/test_service.py)**:
```python
"""
@TEST:AUTH-001
@SPEC: .moai/specs/SPEC-AUTH-001/spec.md
@CODE: src/auth/service.py
"""

def test_authenticate_valid_credentials():
    token = authenticate("user", "pass")
    assert token is not None
```

**CODE (src/auth/service.py)**:
```python
"""
@CODE:AUTH-001
@SPEC: .moai/specs/SPEC-AUTH-001/spec.md
@TEST: tests/auth/test_service.py
@DOC: docs/api/AUTH-001.md
"""

def authenticate(username, password):
    # Implementation...
    return jwt_token
```

**DOC (docs/api/AUTH-001.md)** - 자동 생성:
```markdown
<!-- @DOC:AUTH-001 -->
# AUTH-001: User Authentication

**Status**: Implemented
**Last Updated**: 2025-10-23 (Auto-updated)

## Related
- **SPEC**: .moai/specs/SPEC-AUTH-001/spec.md
- **TEST**: tests/auth/test_service.py
- **CODE**: src/auth/service.py

## API Reference
### `authenticate(username, password)`
...
```

#### TAG 무결성 검증

doc-syncer는 TAG 체인의 무결성을 자동 검증합니다:

```bash
# 체인 무결성 검사
check_tag_chain() {
    local tag_id="$1"

    # 각 TAG 존재 확인
    local has_spec=$(rg "@SPEC:$tag_id" -c .moai/specs/)
    local has_test=$(rg "@TEST:$tag_id" -c tests/)
    local has_code=$(rg "@CODE:$tag_id" -c src/)
    local has_doc=$(rg "@DOC:$tag_id" -c docs/)

    # 체인 무결성 평가
    if [[ $has_spec > 0 && $has_test > 0 && $has_code > 0 ]]; then
        echo "✅ TAG chain complete for $tag_id"
    else
        echo "⚠️ Broken chain for $tag_id:"
        [[ $has_spec == 0 ]] && echo "  - Missing @SPEC"
        [[ $has_test == 0 ]] && echo "  - Missing @TEST"
        [[ $has_code == 0 ]] && echo "  - Missing @CODE"
    fi
}
```

---

## 2. Sub-Agents 기능 상세 분석

### 2.1. Sub-Agents 개요

MoAI-ADK는 **12개의 전문화된 Sub-agents**로 구성된 AI 팀을 운영합니다.

#### 12개 Sub-Agents 목록

| #  | Agent                     | Model  | Phase | Role                              |
|----|---------------------------|--------|-------|-----------------------------------|
| 1  | **project-manager** 📋     | Sonnet | Init  | 프로젝트 초기화 및 메타데이터 관리      |
| 2  | **spec-builder** 🏗️         | Sonnet | Plan  | EARS 기반 SPEC 문서 생성            |
| 3  | **implementation-planner** 📋 | Sonnet | Run-1 | 구현 전략 수립 및 라이브러리 선택     |
| 4  | **tdd-implementer** 💎     | Sonnet | Run-2 | RED → GREEN → REFACTOR 실행      |
| 5  | **doc-syncer** 📖          | Haiku  | Sync  | Living Document 동기화             |
| 6  | **tag-agent** 🏷️            | Haiku  | Sync  | TAG 무결성 검증 및 체인 관리          |
| 7  | **git-manager** 🚀         | Haiku  | All   | GitFlow 자동화, PR 관리             |
| 8  | **debug-helper** 🔍        | Sonnet | Run   | 실패 진단 및 수정 가이드             |
| 9  | **trust-checker** ✅       | Haiku  | All   | TRUST 5 원칙 강제                  |
| 10 | **quality-gate** 🛡️        | Haiku  | Sync  | 커버리지 검토 및 릴리스 게이트         |
| 11 | **cc-manager** 🛠️          | Sonnet | Ops   | Claude Code 세션 관리               |
| 12 | **skill-factory** ⚙️       | Sonnet | Meta  | Skill 생성 도구                    |

**+ 내장 Claude Agents (2개)**:
- **Explore** 🔍 (Haiku): 코드베이스 탐색 및 아키텍처 매핑
- **general-purpose** (Sonnet): 범용 지원

**총 14개 AI 팀원** (12 custom + 2 built-in)

### 2.2. Agent Persona 패턴

MoAI-ADK의 모든 Sub-agents는 **Agent Persona** 패턴을 따릅니다.

#### Agent Persona 구조

```yaml
## 🎭 Agent Persona (professional developer job)

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

#### Persona 요소별 목적

| 요소              | 목적                                              | 예시                                    |
|-------------------|---------------------------------------------------|-----------------------------------------|
| **Icon**          | 시각적 식별자                                      | 📖 (doc-syncer), 🏗️ (spec-builder)      |
| **Job**           | 직업적 역할                                        | Technical Writer, System Architect      |
| **Expertise**     | 전문 분야                                         | Document Synchronization, SPEC Analysis |
| **Role**          | 프로젝트 내 역할                                   | 문서 동기화 전문가, 요구사항 분석가       |
| **Goal**          | 궁극적 목표                                       | 완벽한 문서-코드 일관성 유지              |
| **Mindset**       | 사고 방식                                         | CODE-FIRST, 원자적 작업 단위             |
| **Decision Criteria** | 의사결정 기준                               | 일관성 > 속도, 무결성 > 편의성           |
| **Communication Style** | 소통 방식                                 | 구조화된 보고, 명확한 증거 제시          |
| **Specialized Area** | 특화 영역                                    | TAG 시스템, API 문서화, 동기화            |

**Persona 패턴의 이점**:
- ✅ **명확한 책임**: 각 Agent의 역할 경계 분명
- ✅ **일관된 행동**: Persona에 따라 행동 예측 가능
- ✅ **효과적 협업**: Agent 간 역할 충돌 방지
- ✅ **사용자 이해**: Agent의 전문성 빠르게 파악

### 2.3. Agent 협업 패턴

Sub-agents는 명확한 책임 분리와 협업 원칙을 따릅니다.

#### 협업 원칙 (Agent Collaboration Principles)

**1. 단일 책임 (Single Responsibility)**:
- 각 Agent는 한 가지 전문 영역만 담당
- 예: doc-syncer는 문서만, git-manager는 Git만

**2. 중복 없는 소유권 (Zero Overlapping Ownership)**:
- Agent 간 역할 중복 없음
- 불확실할 때는 가장 전문적인 Agent에게 위임

**3. 신뢰도 보고 (Confidence Reporting)**:
- 작업 완료 시 항상 신뢰도와 위험 공유
- 예: "95% 확신, 라이브러리 버전 호환성 미확인"

**4. 에스컬레이션 경로 (Escalation Path)**:
- 막혔을 때 Alfred에게 에스컬레이션
- 컨텍스트, 시도한 단계, 제안하는 다음 행동 포함

#### 협업 시퀀스 예시 (/alfred:2-run)

```
User: /alfred:2-run

Alfred (SuperAgent) orchestrates:
    ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 1: implementation-planner (Sonnet)                │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ - Read SPEC from .moai/specs/                           │
│ - Analyze requirements                                  │
│ - Select libraries (WebFetch for latest versions)       │
│ - Design TAG chain                                      │
│ - Output: Implementation strategy                       │
├─────────────────────────────────────────────────────────┤
│ Phase 2: tdd-implementer (Sonnet)                       │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ - RED: Write failing test (@TEST:ID)                    │
│ - GREEN: Implement code (@CODE:ID)                      │
│ - REFACTOR: Improve quality                             │
│ - Output: Implementation code + tests                   │
├─────────────────────────────────────────────────────────┤
│ Collaboration: tag-agent (Haiku) - Auto-invoked        │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ - Scan code for TAG blocks                              │
│ - Verify TAG chain integrity                            │
│ - Report orphan TAGs                                    │
├─────────────────────────────────────────────────────────┤
│ Collaboration: trust-checker (Haiku) - Auto-invoked    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ - Check TRUST 5 principles                              │
│ - Verify test coverage ≥85%                             │
│ - Validate type safety                                  │
└─────────────────────────────────────────────────────────┘
    ↓
Alfred summarizes results to user
```

**핵심**:
- ✅ Agent 간 **직접 호출 없음** (Alfred가 오케스트레이션)
- ✅ 각 Agent는 **자신의 전문 영역만** 처리
- ✅ **자동 협업** (trust-checker, tag-agent)

### 2.4. Skills 활용 전략

Sub-agents는 Skills를 적극 활용하여 전문 지식을 JIT(Just-in-Time)로 로드합니다.

#### Skills 활용 패턴

**doc-syncer의 Skills 활용 예시**:

```yaml
## 🧰 Required Skills

**Automatic Core Skills**
- `Skill("moai-alfred-tag-scanning")` – CODE-FIRST 원칙 기반 TAG 수집

**Conditional Skill Logic**
- `Skill("moai-foundation-tags")`: TAG 명명 규칙 재정렬 필요 시
- `Skill("moai-alfred-trust-validation")`: TRUST 게이트 통과 필요 시
- `Skill("moai-foundation-specs")`: SPEC 메타데이터 변경 시
- `Skill("moai-alfred-git-workflow")`: PR Ready 전환 시
- `Skill("moai-alfred-code-reviewer")`: 코드 품질 리뷰 필요 시
- `Skill("moai-alfred-interactive-questions")`: 사용자 승인 필요 시
```

**Skills 로딩 전략**:
1. **Automatic Core Skills**: Agent 시작 시 항상 로드
2. **Conditional Skills**: 특정 조건에서만 로드

**이점**:
- ✅ **컨텍스트 효율성**: 필요한 Skills만 로드
- ✅ **전문성 확장**: Agent가 다양한 지식 접근
- ✅ **일관성**: 여러 Agent가 같은 Skills 공유

### 2.5. Interactive Questions 통합

Sub-agents는 `moai-alfred-interactive-questions` Skill을 통해 TUI 기반 사용자 승인을 받습니다.

#### Interactive Questions 사용 시점

**spec-builder 예시**:

```markdown
> Interactive prompts rely on `Skill("moai-alfred-interactive-questions")`
> so AskUserQuestion renders TUI selection menus for user surveys and approvals.
```

**사용 케이스**:
1. **모호한 요구사항 명확화**:
   ```
   ALFRED: How should the completion page be implemented?

   ┌─ OPTIONS ───────────────────────────────┐
   │ ▶ Create a new public page              │
   │   Modify existing page                  │
   │   Use environment-based gating          │
   └─────────────────────────────────────────┘
   ```

2. **라이브러리 버전 선택**:
   ```
   ALFRED: Which FastAPI version should we use?

   ┌─ OPTIONS ───────────────────────────────┐
   │ ▶ 0.118.3 (latest stable)               │
   │   0.115.0 (LTS)                         │
   │   0.100.0 (legacy compatibility)        │
   └─────────────────────────────────────────┘
   ```

3. **위험 요소 승인**:
   ```
   ALFRED: This will modify 15 files. Proceed?

   ┌─ OPTIONS ───────────────────────────────┐
   │ ▶ Yes, proceed                          │
   │   No, review changes first              │
   │   Show affected files                   │
   └─────────────────────────────────────────┘
   ```

**이점**:
- ✅ "Vibe Coding" 문제 해결 (모호한 요청 방지)
- ✅ 명확한 의사결정
- ✅ 사용자 승인 추적

### 2.6. Model 선택 전략

MoAI-ADK는 Sub-agents의 복잡도에 따라 Sonnet vs Haiku를 전략적으로 선택합니다.

#### Model 선택 가이드

| Model                 | 사용 케이스                                      | 대표 Agents                              |
|-----------------------|--------------------------------------------------|------------------------------------------|
| **Claude 4.5 Sonnet** | 계획, 구현, 문제 해결, 세션 운영                   | Alfred, project-manager, spec-builder, code-builder, debug-helper, cc-manager |
| **Claude 4.5 Haiku**  | 문서 동기화, TAG 검증, Git 자동화, 규칙 기반 검사 | doc-syncer, tag-agent, git-manager, trust-checker, quality-gate, Explore |

**선택 기준**:
- **Sonnet**: 깊은 추론, 다단계 합성, 창의적 문제 해결 필요 시
- **Haiku**: 패턴 기반, 문자열 처리, 빠른 반복 필요 시

**비용 최적화**:
- Haiku는 Sonnet 대비 **~80% 저렴**
- 적절한 Model 선택으로 **비용 50% 절감** 가능

---

## 3. My-Spec 프로젝트 도입 계획

### 3.1. 현재 My-Spec 상황 분석

#### 현재 구조

```
my-spec/
├── .claude/
│   ├── commands/           # /ms.* 슬래시 명령어 (11개)
│   ├── hooks/              # hooks (constitution-injector.sh 등)
│   └── settings.json
├── .specify/
│   ├── memory/
│   │   └── constitution.md # Constitution
│   └── templates/
├── specs/                  # SPEC 문서들
└── docs/                   # 문서 (수동 관리)
```

#### 현재 한계

| 문제                   | 현상                                           | 영향                  |
|------------------------|------------------------------------------------|-----------------------|
| **문서 동기화 부재**    | 코드 변경 후 문서 수동 업데이트                   | 문서 낙후, 신뢰도 하락  |
| **단일 AI**            | Claude 한 명이 모든 작업                        | 컨텍스트 오버로드       |
| **반복 작업 수동화**    | TAG 블록 수동 삽입, Constitution 수동 검증       | 시간 낭비, 일관성 결여  |
| **명확한 책임 부재**    | 명령어마다 역할 중복                             | 유지보수 어려움         |

### 3.2. Living Document 도입 계획

#### Phase 1: doc-syncer Agent 구현 (Week 1-2)

**목표**: 기본 Living Document 시스템 구축

**Step 1: doc-syncer Agent 파일 생성**

`.claude/agents/ms/doc-syncer.md`:

```yaml
---
name: doc-syncer
description: "Use when: Automatic document synchronization based on code changes. Called from /ms.sync command."
tools: Read, Write, Edit, Grep, Glob
model: haiku
---

# Doc Syncer - My-Spec Document Synchronization Expert

## 🎭 Agent Persona

**Icon**: 📖
**Job**: Technical Writer
**Expertise**: Document-Code Synchronization
**Role**: Living Document 관리 전문가
**Goal**: 코드-문서 완벽 일관성 유지

## 🧰 Required Skills

**Automatic Core Skills**
- `Skill("ms-workflow-tag-manager")` – TAG 기반 문서 추출

**Conditional Skills**
- `Skill("ms-foundation-constitution")`: Constitution 검증 시
- `Skill("ms-workflow-ears-checker")`: EARS 패턴 검증 시

## 📋 Workflow

### Phase 1: 상태 분석
1. Git 변경 파일 확인: `git status --short`
2. TAG 스캔: `rg '@TAG' -n`
3. 고아 TAG 탐지

### Phase 2: 문서 동기화
1. README.md 업데이트
2. CHANGELOG.md 업데이트 (수동 작성 → 자동 생성)
3. API 문서 생성 (docs/api/)

### Phase 3: 검증
1. TAG 무결성 확인
2. 문서-코드 일치 확인
3. 동기화 보고서 생성 (docs/sync-report.md)
```

**Step 2: /ms.sync 명령어 생성**

`.claude/commands/ms.sync.md`:

```markdown
---
description: "Synchronize documents with code changes (Living Document)"
---

# /ms.sync - Living Document Synchronization

## Overview

Automatically synchronizes documentation with code changes using CODE-FIRST principle.

## Execution

Delegates to `doc-syncer` agent:

```
Task: doc-syncer
Prompt: |
  Synchronize all documents with recent code changes.

  1. Scan for changed files (git status)
  2. Extract TAGs from code
  3. Update:
     - README.md (features, examples)
     - CHANGELOG.md (version history)
     - docs/api/ (API documentation)
  4. Verify TAG chain integrity
  5. Generate sync report
```

## Next Steps

After `/ms.sync`:
1. Review sync-report.md
2. Commit documentation changes
3. Ready for release
```

**Step 3: 테스트**

```bash
# 코드 변경
echo "def new_function(): pass" >> src/module.py

# 문서 동기화
/ms.sync

# 결과 확인
cat docs/sync-report.md
```

#### Phase 2: 조건부 문서 생성 (Week 3)

**목표**: 프로젝트 타입별 맞춤 문서 생성

**프로젝트 타입 감지 로직**:

```python
def detect_project_type():
    """Detect project type from codebase structure"""

    # CLI Tool 감지
    if exists("cli.py") or exists("main.py"):
        return "cli-tool"

    # Web API 감지
    if exists("app.py") or grep("FastAPI|Flask", "*.py"):
        return "web-api"

    # Library 감지
    if exists("__init__.py") and exists("setup.py"):
        return "library"

    # Frontend 감지
    if exists("package.json") and grep("react|vue|angular", "package.json"):
        return "frontend"

    return "application"
```

**문서 템플릿**:

docs/templates/:
- `API.md.template` (Web API용)
- `CLI_COMMANDS.md.template` (CLI Tool용)
- `API_REFERENCE.md.template` (Library용)
- `components.md.template` (Frontend용)

#### Phase 3: 자동 트리거 통합 (Week 4)

**목표**: 코드 변경 시 자동 문서 업데이트

**Git Hook 통합** (.git/hooks/post-commit):

```bash
#!/bin/bash
# Auto-sync documents after commit

echo "📖 Synchronizing documents..."
claude /ms.sync --quiet

if [ $? -eq 0 ]; then
    echo "✅ Documents synced"
else
    echo "⚠️ Sync failed, run /ms.sync manually"
fi
```

**CI/CD 통합** (.github/workflows/doc-sync.yml):

```yaml
name: Documentation Sync

on:
  push:
    branches: [main, master]

jobs:
  sync-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Sync documents
        run: |
          claude /ms.sync

      - name: Commit changes
        run: |
          git add docs/
          git commit -m "docs: auto-sync with code changes" || true
          git push
```

### 3.3. Sub-Agents 도입 계획

#### Phase 1: 핵심 3개 Agents (Week 5-7)

**우선순위 높은 Agents**:

1. **spec-builder** (Week 5)
   - SPEC 문서 자동 생성
   - EARS 패턴 강제
   - `/ms.specify` 위임

2. **tag-agent** (Week 6)
   - TAG 무결성 검증
   - 고아 TAG 탐지
   - TAG 체인 검증
   - `/ms.analyze`와 통합

3. **trust-checker** (Week 7)
   - TRUST 5 원칙 자동 검증
   - 테스트 커버리지 확인
   - Constitution 준수 검사
   - 모든 `/ms.*` 명령어와 통합

#### Phase 2: 워크플로우 Agents (Week 8-10)

4. **implementation-planner** (Week 8)
   - 구현 전략 수립
   - 라이브러리 버전 선택
   - TAG 체인 설계
   - `/ms.plan` 위임

5. **tdd-implementer** (Week 9)
   - RED → GREEN → REFACTOR
   - 자동 테스트 생성
   - `/ms.implement` 위임

6. **git-manager** (Week 10)
   - GitFlow 자동화
   - PR 생성 및 관리
   - `/fin`, `/finq`와 통합

#### Phase 3: 고급 Agents (Week 11-12)

7. **debug-helper** (Week 11)
   - 실패 진단
   - 수정 가이드 제공

8. **quality-gate** (Week 12)
   - 릴리스 게이트 검증
   - 커버리지 델타 확인

#### Agent 파일 구조

`.claude/agents/ms/`:
```
ms/
├── spec-builder.md
├── tag-agent.md
├── trust-checker.md
├── implementation-planner.md
├── tdd-implementer.md
├── git-manager.md
├── debug-helper.md
└── quality-gate.md
```

### 3.4. 통합 아키텍처

도입 완료 후 최종 구조:

```
┌────────────────────────────────────────────────────────┐
│ Layer 1: COMMANDS (/ms.*)                             │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ /ms.init, /ms.specify, /ms.plan, /ms.implement,       │
│ /ms.sync, /ms.review, /ms.analyze                     │
├────────────────────────────────────────────────────────┤
│ Layer 2: SUB-AGENTS (.claude/agents/ms/)              │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ spec-builder, tag-agent, trust-checker,                │
│ implementation-planner, tdd-implementer, git-manager,  │
│ doc-syncer, debug-helper, quality-gate                 │
├────────────────────────────────────────────────────────┤
│ Layer 3: SKILLS (.claude/skills/ms-*)                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ ms-foundation-constitution, ms-workflow-tag-manager,   │
│ ms-workflow-ears-checker, ms-workflow-living-docs,     │
│ ms-lang-python, ms-lang-typescript, ...                │
├────────────────────────────────────────────────────────┤
│ Layer 4: HOOKS (.claude/hooks/)                       │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ constitution-injector.sh, notify.sh                    │
└────────────────────────────────────────────────────────┘
```

### 3.5. 기대 효과

#### 정량적 효과

| 메트릭                  | Before (현재)        | After (도입 후)        | 개선율     |
|------------------------|---------------------|----------------------|-----------|
| **문서 동기화 시간**     | 30분 (수동)          | 2분 (자동)             | **93%↓**  |
| **TAG 검증 시간**       | 15분 (수동 검색)      | 10초 (자동 스캔)        | **98%↓**  |
| **SPEC 작성 시간**      | 60분 (처음부터)       | 15분 (Agent 지원)      | **75%↓**  |
| **Constitution 준수율** | ~70% (수동 검증)      | 95%+ (자동 강제)       | **25%↑**  |
| **문서 정확도**         | ~60% (낙후)          | 100% (실시간 동기화)    | **40%↑**  |
| **개발자 인지 부하**     | 높음 (11개 명령 숙지)  | 낮음 (Agent가 처리)    | **60%↓**  |

#### 정성적 효과

**1. 개발자 경험 향상**:
- ❌ Before: "TAG 블록을 매번 수동으로 달아야 해"
- ✅ After: "tag-agent가 알아서 검증해줘"

**2. 신뢰성 향상**:
- ❌ Before: "6개월 된 문서는 믿을 수 없어"
- ✅ After: "문서는 항상 최신이야"

**3. 온보딩 시간 단축**:
- ❌ Before: "새 팀원이 Constitution 전체를 읽어야 해" (3일)
- ✅ After: "trust-checker가 자동으로 가이드해줘" (1일)

**4. 품질 일관성**:
- ❌ Before: "개발자마다 TAG 형식이 달라"
- ✅ After: "tag-agent가 일관된 형식 강제"

**5. 유지보수 비용 절감**:
- ❌ Before: "Constitution 변경 시 11개 명령어 수정"
- ✅ After: "Skills만 업데이트하면 모든 Agent 반영"

### 3.6. 로드맵 요약

| Week   | Phase                    | Deliverables                                      |
|--------|--------------------------|---------------------------------------------------|
| 1-2    | Living Document Phase 1  | doc-syncer agent, /ms.sync 명령어                  |
| 3      | Living Document Phase 2  | 프로젝트 타입별 문서 템플릿                          |
| 4      | Living Document Phase 3  | Git Hook, CI/CD 통합                              |
| 5-7    | Sub-Agents Phase 1       | spec-builder, tag-agent, trust-checker           |
| 8-10   | Sub-Agents Phase 2       | implementation-planner, tdd-implementer, git-manager |
| 11-12  | Sub-Agents Phase 3       | debug-helper, quality-gate                        |

**총 소요 기간**: 12주 (3개월)

---

## 4. 위험 요소 및 대응 방안

### 4.1. 기술적 위험

| 위험                       | 영향  | 확률 | 대응 방안                                    |
|----------------------------|-------|------|---------------------------------------------|
| **Agent 간 충돌**           | 높음  | 중간 | 명확한 책임 분리, Agent Persona 패턴 적용     |
| **컨텍스트 오버플로우**      | 중간  | 높음 | Progressive Disclosure, Haiku 활용           |
| **TAG 형식 불일치**         | 높음  | 낮음 | tag-agent 자동 검증, Skills 템플릿 제공       |
| **문서 생성 오류**          | 중간  | 중간 | 수동 검토 단계 추가, 품질 검증 체크리스트      |

### 4.2. 조직적 위험

| 위험                       | 영향  | 확률 | 대응 방안                                    |
|----------------------------|-------|------|---------------------------------------------|
| **학습 곡선**              | 중간  | 높음 | 단계적 도입, 문서화, 실습 프로젝트             |
| **기존 워크플로우 저항**     | 높음  | 중간 | 점진적 마이그레이션, 기존 명령어 유지           |
| **유지보수 부담 증가**      | 중간  | 낮음 | Agent/Skill 템플릿화, 자동화 테스트            |

### 4.3. 성능 위험

| 위험                       | 영향  | 확률 | 대응 방안                                    |
|----------------------------|-------|------|---------------------------------------------|
| **응답 지연**              | 중간  | 중간 | Haiku 우선 사용, 병렬 Agent 실행              |
| **비용 증가**              | 높음  | 중간 | Haiku/Sonnet 적절 배분, 캐싱 활용             |

---

## 5. 결론

### 5.1. 핵심 요약

**Living Document**:
- ✅ CODE-FIRST 원칙으로 문서-코드 불일치 문제 해결
- ✅ doc-syncer agent가 자동 동기화
- ✅ TAG 체인으로 완벽한 추적성 확보
- ✅ 프로젝트 타입별 맞춤 문서 생성

**Sub-Agents**:
- ✅ 12개 전문 AI 팀으로 역할 분산
- ✅ Agent Persona 패턴으로 명확한 책임
- ✅ Skills 활용으로 전문성 확장
- ✅ Interactive Questions로 명확한 의사결정

**통합 효과**:
- 📉 **문서 동기화 시간 93% 감소** (30분 → 2분)
- 📉 **TAG 검증 시간 98% 감소** (15분 → 10초)
- 📉 **개발자 인지 부하 60% 감소**
- 📈 **문서 정확도 40% 향상** (60% → 100%)
- 📈 **Constitution 준수율 25% 향상** (70% → 95%)

### 5.2. My-Spec 적용 권장사항

**즉시 시작 (High Priority)**:
1. ✅ doc-syncer agent 구현 (Living Document 핵심)
2. ✅ /ms.sync 명령어 생성
3. ✅ tag-agent, trust-checker 구현 (품질 보증)

**점진적 확장 (Medium Priority)**:
4. 🟡 spec-builder, implementation-planner 구현
5. 🟡 조건부 문서 생성 기능 추가
6. 🟡 Git Hook / CI/CD 통합

**장기 고도화 (Low Priority)**:
7. 🔵 debug-helper, quality-gate 구현
8. 🔵 Language Pack Skills 확장
9. 🔵 전체 AI 팀 구성 완료

### 5.3. 성공 기준

**3개월 후 달성 목표**:
- ✅ Living Document 시스템 가동 (문서 정확도 100%)
- ✅ 핵심 3개 Agents 운영 (spec-builder, tag-agent, trust-checker)
- ✅ /ms.* 명령어들이 Agents에게 위임
- ✅ 개발자 피드백 긍정적 (학습 곡선 수용 가능)

**6개월 후 달성 목표**:
- ✅ 8개 Agents 완전 가동
- ✅ CI/CD 완전 통합
- ✅ 문서 동기화 시간 95% 감소
- ✅ Constitution 준수율 95% 이상

---

## 6. 참고 자료

### 6.1. MoAI-ADK 문서

- [MoAI-ADK GitHub](https://github.com/modu-ai/moai-adk)
- [MoAI-ADK CLAUDE.md](https://github.com/modu-ai/moai-adk/blob/main/CLAUDE.md)
- [Sub-Agents 디렉토리](https://github.com/modu-ai/moai-adk/tree/main/.claude/agents/alfred)

### 6.2. My-Spec 관련 문서

- [My-Spec Skills 분석](/workspace/specter/docs/references/moai-adk-skills-analysis.md)
- [My-Spec SKILLS.md](/workspace/specter/SKILLS.md)
- [My-Spec Constitution](/.specify/memory/constitution.md)

### 6.3. Claude Code 공식 문서

- [Claude Code Agents](https://docs.claude.com/en/docs/claude-code/agents)
- [Claude Code Skills](https://docs.claude.com/ko/docs/claude-code/skills)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-23
**Author**: My-Spec Team
**Status**: Draft - Ready for Review

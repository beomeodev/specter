# MoAI-ADK Skills 적용 분석

**분석 일자**: 2025-10-23
**분석 대상**: [modu-ai/moai-adk](https://github.com/modu-ai/moai-adk)
**참조**: [anthropics/skills](https://github.com/anthropics/skills) (공식 Claude Code Skills)

---

## Executive Summary

MoAI-ADK는 Anthropic의 공식 Claude Code Skills 기능을 활용하여 **55개의 전문화된 Skills 라이브러리**를 구축했습니다. 이는 공식 예제(~15개)의 3.6배 규모로, SPEC-First TDD 워크플로우를 자동화하는 "Alfred SuperAgent" 시스템의 핵심 구성 요소입니다.

**핵심 발견사항**:
- ✅ **4계층 아키텍처**: Commands → Sub-agents → Skills → Hooks
- ✅ **체계적 명명 규칙**: `moai-{tier}-{purpose}` 패턴
- ✅ **확장된 메타데이터**: 버전 관리, 상태, 키워드 추가
- ✅ **템플릿화된 구조**: 13개 섹션으로 일관성 확보
- ✅ **Progressive Disclosure 최적화**: 3단계 로딩 전략
- ✅ **워크플로우 통합**: `/alfred` 명령어와 긴밀한 연계

---

## 1. MoAI-ADK 아키텍처 개요

### 1.1. 4계층 실행 모델

MoAI-ADK는 책임을 4개 레이어로 명확히 분리했습니다:

```
┌────────────────────────────────────────────────────────────────┐
│ Layer 1: COMMANDS                                             │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ User-facing entry points (워크플로우 오케스트레이션)             │
│ Examples: /alfred:0-project, /alfred:1-plan, /alfred:2-run    │
├────────────────────────────────────────────────────────────────┤
│ Layer 2: SUB-AGENTS (19 agents)                               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ Deep reasoning & decision making (Sonnet/Haiku)              │
│ Examples: spec-builder, code-builder, tag-agent, git-manager │
├────────────────────────────────────────────────────────────────┤
│ Layer 3: SKILLS (55 skills)                                   │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ Reusable knowledge capsules (Progressive Disclosure)          │
│ Examples: moai-foundation-trust, moai-lang-python, ...        │
├────────────────────────────────────────────────────────────────┤
│ Layer 4: HOOKS                                                │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ Runtime guardrails (<100ms checks)                            │
│ Examples: SessionStart status card, PreToolUse safety checks  │
└────────────────────────────────────────────────────────────────┘
```

**레이어 선택 기준**:
1. 이벤트 기반 자동 실행? → **Hook**
2. 추론과 대화 필요? → **Sub-agent**
3. 재사용 가능한 지식/정책? → **Skill**
4. 다단계 승인 오케스트레이션? → **Command**

### 1.2. Alfred SuperAgent의 역할

**Alfred**는 MoAI-ADK의 최상위 오케스트레이터로, SPEC → TDD → Sync 워크플로우를 관리합니다:

```
사용자 요청
    ↓
Alfred (SuperAgent)
    ↓
┌───────────────┬───────────────┬───────────────┐
│  /alfred:1    │  /alfred:2    │  /alfred:3    │
│  PLAN (SPEC)  │  RUN (TDD)    │  SYNC (Docs)  │
└───────────────┴───────────────┴───────────────┘
    ↓               ↓               ↓
spec-builder    code-builder    doc-syncer
(Sub-agent)     (Sub-agent)     (Sub-agent)
    ↓               ↓               ↓
Skills          Skills          Skills
```

**핵심 원칙**:
- **SPEC-First**: 요구사항 정의가 코드보다 우선
- **TDD 강제**: RED → GREEN → REFACTOR 순서
- **자동 동기화**: 코드-테스트-문서 항상 일치

---

## 2. Skills 라이브러리 구성 (55개)

### 2.1. 계층별 분포

| Tier           | Count | Purpose                            | Examples                                       |
|----------------|-------|------------------------------------|------------------------------------------------|
| **Foundation** | 6     | 핵심 원칙 및 프레임워크               | trust, tags, specs, ears, git, langs           |
| **Essentials** | 4     | 필수 개발 작업                       | debug, perf, refactor, review                  |
| **Alfred**     | 11    | 워크플로우 자동화                    | ears-authoring, tag-scanning, trust-validation |
| **Domain**     | 10    | 도메인별 전문화                      | backend, frontend, mobile, security, devops    |
| **Language**   | 23    | 언어별 Best Practices               | python, typescript, go, rust, java, ...        |
| **Ops**        | 1     | Claude Code 세션 관리                | claude-code (settings, output styles)          |
| **Total**      | **55**| Complete knowledge library         |                                                |

### 2.2. 명명 규칙 패턴

MoAI-ADK는 체계적인 명명 규칙으로 Skills의 역할을 명확히 구분합니다:

```
moai-{tier}-{purpose}
```

**Tier 접두사**:
- `moai-foundation-*`: 프로젝트 전반의 기본 원칙
- `moai-essentials-*`: 개발 단계별 필수 작업
- `moai-alfred-*`: Alfred 워크플로우 전용
- `moai-domain-*`: 특정 도메인 전문화
- `moai-lang-*`: 프로그래밍 언어별 전문화
- `moai-cc-*`: Claude Code 기능 관련
- `moai-skill-factory`: 메타 - Skill 생성 도구

**명명 예시**:
```
✅ moai-lang-python          # 언어 전문화
✅ moai-alfred-tag-scanning  # Alfred 워크플로우 보조
✅ moai-domain-backend       # 도메인 전문화
✅ moai-foundation-trust     # 핵심 원칙
❌ python-helper             # 모호함
❌ backend                   # 네임스페이스 미지정
```

### 2.3. 공식 Skills와의 비교

| Aspect                | Anthropic Official        | MoAI-ADK                                 |
|-----------------------|---------------------------|------------------------------------------|
| **Skills 개수**       | ~15 (예제)                | 55 (production-ready)                    |
| **명명 규칙**         | 자유형식                   | `moai-{tier}-{purpose}` 패턴             |
| **메타데이터**        | name, description, tools  | + version, created, updated, status, keywords |
| **구조 일관성**       | 자유로운 섹션 구성          | 13개 표준 섹션 템플릿                     |
| **버전 관리**         | 없음                       | Semantic Versioning (v2.0.0)             |
| **Changelog**         | 선택적                     | 필수 (모든 Skill에 포함)                  |
| **상호 참조**         | 제한적                     | "Works Well With" 섹션으로 명시          |
| **워크플로우 통합**   | 독립적 사용                | /alfred 명령어와 긴밀히 연계              |
| **Progressive Disclosure** | Level 1-3 구분         | Level 1-3 명확히 문서화                  |

---

## 3. 메타데이터 확장 전략

### 3.1. 표준 YAML Frontmatter

**공식 Skills (최소 요구사항)**:
```yaml
---
name: "Skill Name"
description: "What it does and when to use it"
allowed-tools: "Tool1, Tool2"
---
```

**MoAI-ADK (확장 메타데이터)**:
```yaml
---
name: moai-alfred-tag-scanning
version: 2.0.0
created: 2025-10-22
updated: 2025-10-22
status: active
description: Scans @TAG markers from code and generates TAG inventory (CODE-FIRST principle).
keywords: ['tag', 'scanning', 'inventory', 'traceability']
allowed-tools:
  - Read
  - Bash
---
```

### 3.2. 추가 필드의 목적

| Field       | Purpose                                  | Example               |
|-------------|------------------------------------------|-----------------------|
| `version`   | Semantic Versioning 추적                 | `2.0.0`               |
| `created`   | 최초 생성일 (히스토리 추적)                | `2025-10-22`          |
| `updated`   | 최종 수정일 (신선도 확인)                  | `2025-10-22`          |
| `status`    | 활성 상태 추적                             | `active`, `deprecated`|
| `keywords`  | 검색 및 발견 최적화                        | `['tag', 'scanning']` |

**버전 관리 전략**:
- **v1.x.x → v2.0.0**: 주요 도구 버전 업그레이드 (예: pytest 7.x → 8.4.2)
- **vX.1.x → vX.2.0**: 새로운 섹션 추가 (예: Interactive Questions)
- **vX.X.1 → vX.X.2**: 문서 개선, 오타 수정

---

## 4. 템플릿화된 구조 (13개 섹션)

MoAI-ADK의 모든 Skills는 일관된 구조를 따릅니다. 이는 유지보수성과 학습 곡선을 크게 개선합니다.

### 4.1. 표준 섹션 구조

```markdown
---
# YAML Frontmatter
---

# Skill Name

## Skill Metadata                      # 1. 메타 정보 테이블
| Field | Value |
| ----- | ----- |
| Version | 2.0.0 |
| ...

## What It Does                        # 2. 기능 개요
- ✅ Capability 1
- ✅ Capability 2

## When to Use                         # 3. 사용 시점
**Automatic triggers**: ...
**Manual invocation**: ...

## How It Works                        # 4. 작동 방식 (핵심)
### Pattern 1
### Pattern 2

## Inputs                              # 5. 입력 데이터
## Outputs                             # 6. 출력 결과
## Failure Modes                       # 7. 실패 케이스
## Dependencies                        # 8. 의존 관계
## References                          # 9. 참조 문서
## Changelog                           # 10. 변경 이력
## Works Well With                     # 11. 관련 Skills
## Examples                            # 12. 실전 예제
## Best Practices                      # 13. 모범 사례
```

### 4.2. 섹션별 목적과 내용

| Section           | Purpose                                 | Example Content                                |
|-------------------|-----------------------------------------|------------------------------------------------|
| **Skill Metadata**| 빠른 참조 정보                            | Version, Tier, Allowed tools, Trigger cues     |
| **What It Does**  | 기능 요약 (30초 이해)                     | Bullet points with checkmarks                  |
| **When to Use**   | 자동 트리거 조건                          | "SPEC implementation (`/alfred:2-run`)"        |
| **How It Works**  | 패턴 및 의사코드 (핵심)                   | High/Medium/Low Freedom 구분                   |
| **Failure Modes** | 실패 예방                                | "When required tools are not installed"        |
| **Dependencies**  | 다른 Skills와의 연계                      | "Integration with `moai-foundation-trust`"     |
| **Changelog**     | 버전 히스토리                             | "v2.0.0 (2025-10-22): Major update..."         |
| **Works Well With**| 추천 조합                                | "moai-foundation-tags, moai-essentials-review" |
| **Examples**      | 실전 시나리오                             | Code snippets with comments                    |
| **Best Practices**| DO/DON'T 체크리스트                       | "✅ DO: ..., ❌ DON'T: ..."                     |

### 4.3. 공식 Skills와의 구조 비교

**공식 Skills (자유 형식)**:
```markdown
---
name: skill-name
description: ...
---

# Skill Name

[자유로운 마크다운 콘텐츠]
- 섹션 구성이 Skill마다 다름
- 일관성 없음
```

**MoAI-ADK (표준 템플릿)**:
```markdown
---
name: moai-*
version: 2.0.0
...
---

# Skill Name

## Skill Metadata    # 항상 첫 섹션
## What It Does      # 항상 두 번째 섹션
...
## Best Practices    # 항상 마지막 섹션
```

**장점**:
- ✅ **학습 곡선 단축**: 한 Skill 구조를 배우면 55개 모두 동일
- ✅ **유지보수 용이**: 업데이트 시 어떤 섹션을 수정할지 명확
- ✅ **자동화 가능**: 스크립트로 Skill 생성 가능 (moai-skill-factory)
- ✅ **품질 일관성**: 누락된 섹션 즉시 발견

---

## 5. Progressive Disclosure 최적화

### 5.1. 3단계 로딩 전략

MoAI-ADK는 Progressive Disclosure를 명확히 문서화하고 최적화했습니다:

```
┌─────────────────────────────────────────────────────────────┐
│ Level 1: Metadata (Always Loaded)                          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ - YAML frontmatter (name, description, allowed-tools)      │
│ - ~100 tokens per Skill                                    │
│ - Claude decides relevance based on this                   │
├─────────────────────────────────────────────────────────────┤
│ Level 2: Instructions (On Demand)                          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ - SKILL.md main body (workflows, patterns, best practices) │
│ - Loads when Claude recognizes relevance                   │
│ - ~400-500 lines per SKILL.md                              │
├─────────────────────────────────────────────────────────────┤
│ Level 3: Resources (As Needed)                             │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ - reference.md, examples.md, scripts/                      │
│ - Consumed only when explicitly referenced                 │
└─────────────────────────────────────────────────────────────┘
```

### 5.2. 토큰 효율성 예시

**시나리오**: Python 프로젝트에서 테스트 작성 요청

```
User: "Write tests for the authentication module"

Claude's Progressive Loading:

Level 1 (Session Start):
- 55 Skills × 100 tokens = 5,500 tokens
- All metadata loaded, minimal context overhead

Level 2 (On Demand):
- moai-lang-python SKILL.md loaded (~500 lines)
- moai-foundation-trust SKILL.md loaded (TRUST 5 principles)
- Total: ~3,000 tokens additional

Level 3 (If Referenced):
- examples.md loaded only if Claude references it
- scripts/ loaded only if execution needed

Total Context: ~8,500 tokens (vs. 55,000+ if all Skills fully loaded)
```

**핵심 이점**:
- ✅ **확장 가능성**: 55개 Skills 설치해도 세션 시작 시 5.5K 토큰만 소비
- ✅ **지능형 로딩**: Claude가 관련성 판단하여 필요한 것만 로드
- ✅ **비용 효율성**: 실제 사용하는 Skills만 토큰 소비

### 5.3. Metadata Description 최적화

MoAI-ADK는 Level 1 description을 매우 구체적으로 작성하여 Claude의 자동 트리거 정확도를 높입니다:

**❌ 나쁜 예 (모호함)**:
```yaml
description: "Helps with Python development"
```

**✅ 좋은 예 (구체적 키워드)**:
```yaml
description: "Python 3.13+ best practices with pytest 8.4.2, mypy 1.8.0,
ruff 0.13.1, and uv 0.9.3. Use when writing or reviewing Python code
in project workflows."
keywords: [python, testing, pytest, mypy, ruff, uv, async, fastapi, pydantic]
```

**트리거 키워드 포함**:
- 도메인: `python`, `pytest`, `fastapi`
- 작업: `writing`, `reviewing`, `testing`
- 도구: `mypy`, `ruff`, `uv`
- 패턴: `async`, `TDD`

---

## 6. Freedom Level Framework 적용

MoAI-ADK는 Anthropic의 Freedom Level Framework를 충실히 적용합니다.

### 6.1. 3단계 자유도 구분

| Freedom Level | % in SKILL.md | Use Case                 | Content Style                          |
|---------------|---------------|--------------------------|----------------------------------------|
| **High**      | 20-30%        | 유연하고 창의적인 작업      | 원칙, 트레이드오프, 의사결정 트리         |
| **Medium**    | 50-60%        | 표준 패턴 존재            | 의사코드, 플로우차트, 템플릿              |
| **Low**       | 10-20%        | 결정론적, 오류 위험 높음    | 실행 가능 스크립트, 오류 처리, 검증 로직  |

### 6.2. 실제 적용 예시 (moai-cc-skills)

**High Freedom (30%)** - 아키텍처 설계:
```markdown
## Architecture Trade-offs

| Pattern       | Pros                       | Cons                        | When to use                 |
| ------------- | -------------------------- | --------------------------- | --------------------------- |
| Monolith      | Simple, unified            | Scales poorly               | MVP, <10 people             |
| Microservices | Scalable, independent      | Complex, distributed tracing| 10+ teams                   |
| Serverless    | Zero ops, elastic          | Cold starts, vendor lock-in | Event-driven                |

Choose based on:
1. Team size: Monolith if <5 devs
2. Scale: Microservices if >10M requests/month
3. Budget: Serverless if unpredictable workload
```

**Medium Freedom (50%)** - 데이터 검증 패턴:
```pseudocode
## Validation Workflow

1. Load data source (CSV, JSON, API)
2. For each record:
   a. Check required fields exist
   b. Validate data types
   c. Verify constraints (range, format)
   d. Check references (foreign keys)
3. Collect errors with row numbers
4. Report summary + fix suggestions
5. Proceed only if all errors fixed
```

**Low Freedom (20%)** - 보안 검증 스크립트:
```python
#!/usr/bin/env python3
"""Validate code for OWASP Top 10 risks"""
import re
import sys

PATTERNS = [
    (r"eval\(", "OWASP-A1: Code injection risk"),
    (r"SELECT.*\$", "OWASP-A3: SQL injection risk"),
    (r"os\.system\(", "OWASP-A6: Command injection risk"),
]

def validate_file(filepath):
    with open(filepath) as f:
        content = f.read()

    issues = []
    for pattern, risk in PATTERNS:
        if re.search(pattern, content):
            issues.append(risk)

    return issues

if __name__ == "__main__":
    for filepath in sys.argv[1:]:
        issues = validate_file(filepath)
        if issues:
            print(f"⚠️  {filepath}:")
            for issue in issues:
                print(f"  • {issue}")
```

### 6.3. 자유도 결정 트리 (moai-skill-factory)

```
Is the task deterministic?
├─ YES: Well-defined algorithm, fixed steps
│   └─→ Low Freedom: Specific script with error handling
│       (Example: Bash file operations, deployment steps)
│
└─ NO: Flexible, context-dependent, multiple valid approaches
    └─ Does the task have standard patterns?
        ├─ YES: Established best practice (e.g., validation)
        │   └─→ Medium Freedom: Pseudocode + examples
        │       (Example: Data validation, testing patterns)
        │
        └─ NO: Novel or creative work
            └─→ High Freedom: Principles + considerations
                (Example: Architecture design, code organization)
```

---

## 7. 워크플로우 통합 전략

### 7.1. Alfred 명령어와 Skills 매핑

MoAI-ADK의 Skills는 `/alfred` 명령어와 긴밀히 연계됩니다:

| Command            | Phase | Activated Skills                                           |
|--------------------|-------|-----------------------------------------------------------|
| `/alfred:0-project`| Init  | moai-alfred-language-detection, moai-foundation-langs     |
| `/alfred:1-plan`   | SPEC  | moai-alfred-ears-authoring, moai-foundation-specs, moai-alfred-spec-metadata-validation |
| `/alfred:2-run`    | TDD   | moai-lang-{python/typescript/go/...}, moai-essentials-refactor, moai-alfred-trust-validation |
| `/alfred:3-sync`   | Docs  | moai-alfred-tag-scanning, moai-essentials-review, moai-alfred-code-reviewer, moai-foundation-tags |

**자동 트리거 메커니즘**:
```
User: /alfred:2-run

Alfred (SuperAgent) delegates to:
    ↓
code-builder (Sub-agent)
    ↓
Claude recognizes: "Python project" + "TDD implementation"
    ↓
Auto-loads Skills (Progressive Disclosure Level 2):
- moai-lang-python (Python 3.13 best practices)
- moai-foundation-trust (TRUST 5 principles)
- moai-alfred-trust-validation (Quality gate enforcement)
    ↓
Implements with TDD: RED → GREEN → REFACTOR
```

### 7.2. Sub-agent와 Skills 관계

**Sub-agents invoke Skills when specialized knowledge is required**:

```
spec-builder (Sub-agent)
    ↓ needs EARS syntax guidance
moai-alfred-ears-authoring (Skill)
    ↓ returns EARS templates
spec-builder applies patterns
    ↓
SPEC created with EARS compliance
```

**예시 (moai-skill-factory)**:
```
User: "/alfred:1-plan Create Skill for X"
    ↓
skill-generator Sub-Agent (ANALYZE → DESIGN → ASSURE phases)
    ↓ invokes
moai-skill-factory Skill (PRODUCE phase)
    ↓ provides templates, validation, freedom levels
Complete Skill package created
```

### 7.3. Hooks와 Skills의 협력

**Hooks**: 시스템 레벨 자동화 (이벤트 기반)
**Skills**: AI 레벨 자동화 (Claude 자율 판단)

**협력 시퀀스**:
```
User: /alfred:2-run

→ Slash Command runs implementation workflow
  → Hook: constitution-injector.sh adds Constitution to context
    → Skill: tag-manager auto-inserts TAG blocks
      → Skill: living-docs-updater updates API docs
        → Skill: constitution-validator checks compliance
          → Hook: notify.sh plays completion sound
```

**차이점 정리**:

| Aspect        | Hooks                          | Skills                        |
|---------------|--------------------------------|-------------------------------|
| **Trigger**   | System events (SessionStart, PreToolUse) | Claude decision (relevance)   |
| **Latency**   | <100ms (fast checks)           | On-demand (context loading)   |
| **Purpose**   | Guardrails, safety, status     | Knowledge, patterns, templates|
| **Scope**     | Session-wide                   | Task-specific                 |

---

## 8. Interactive Discovery 기능

### 8.1. moai-alfred-interactive-questions Skill

MoAI-ADK는 "Vibe Coding" 문제를 해결하기 위해 대화형 질문 시스템을 도입했습니다.

**Vibe Coding 문제**:
- ❌ 모호한 요청: "Add a dashboard"
- ❌ AI의 추측: 레이아웃? 데이터 소스? 인증 방식?
- ❌ 여러 차례 수정: 의도와 구현 불일치

**Interactive Questions 해결책**:
- ✅ AI가 먼저 질문: 구체적 선택지 제시
- ✅ TUI 메뉴: 화살표 키로 선택, 엔터로 확인
- ✅ 명확한 의도: 추측 제거

### 8.2. TUI Survey 예시

```
────────────────────────────────────────────────────────────────
ALFRED: How should the completion page be implemented?
────────────────────────────────────────────────────────────────

┌─ IMPLEMENTATION APPROACH ────────────────────────────────────┐
│                                                              │
│ ▶ Create a new public page (/competition-closed)            │
│   • Unguarded route, visible to all visitors                │
│   • No authentication required                              │
│                                                              │
│   Modify existing /end page with conditional logic          │
│   • Check if competition is active before showing results   │
│                                                              │
│   Use environment-based gating                              │
│   • Set NEXT_PUBLIC_COMPETITION_CLOSED=true                │
│   • Redirect all traffic to completion screen               │
│                                                              │
│ Use ↑↓ arrows to navigate, ENTER to select                 │
│ Type custom answer or press ESC to cancel                   │
└──────────────────────────────────────────────────────────────┘

→ Selection: Create a new public page (/competition-closed)
```

**이점**:
- ✅ **명확성**: 선택지 명확 → 추측 제거
- ✅ **속도**: 3-5개 질문 → 즉시 구현 (vs. 여러 차례 수정)
- ✅ **품질**: 의도와 구현 일치

### 8.3. 사용 시점

**Ideal for**:
- 🎯 복잡한 기능 (여러 가능한 접근법)
- 🎯 아키텍처 결정 (트레이드오프 존재)
- 🎯 모호한 요구사항
- 🎯 여러 컴포넌트 영향

**트리거 예시**:
- "Add a dashboard" → 레이아웃, 데이터 소스, 인증 확인 필요
- "Refactor auth system" → 범위, 하위 호환성, 마이그레이션 전략 확인
- "Optimize performance" → 병목 지점, 허용 가능한 트레이드오프 확인

---

## 9. TRUST 5 원칙과 TAG 시스템 통합

### 9.1. TRUST 5 Principles (moai-foundation-trust)

MoAI-ADK는 모든 코드에 TRUST 5 원칙을 강제합니다:

| Principle      | Enforcement                                | Tools                                  |
|----------------|--------------------------------------------|----------------------------------------|
| **T**est First | 커버리지 ≥85%, RED → GREEN → REFACTOR 순서 | pytest 8.4.2, Vitest 2.0.5, go test    |
| **R**eadable   | File ≤300 LOC, Function ≤50 LOC, Complexity ≤10 | ruff 0.13.1, ESLint 9.x, clippy       |
| **U**nified    | Type safety, SPEC-driven architecture      | mypy 1.8.0, TypeScript strict mode    |
| **S**ecured    | SAST, 비밀 탐지, 취약점 스캔                 | trivy 0.56.x, semgrep 1.94.x, bandit   |
| **T**rackable  | @TAG 체인 무결성 검증                        | TAG validation scripts, rg 14.x        |

**CI/CD 통합**:
```yaml
# .github/workflows/trust-validation.yml
name: TRUST Validation

on: [pull_request, push]

jobs:
  trust-check:
    runs-on: ubuntu-latest
    steps:
      # T - Test First
      - name: Run tests with coverage
        run: pytest --cov=src --cov-fail-under=85

      # R - Readable
      - name: Lint code
        run: ruff check .

      # U - Unified
      - name: Type check
        run: mypy src/ --strict

      # S - Secured
      - name: Security scan
        run: trivy fs --severity HIGH,CRITICAL .

      # T - Trackable
      - name: TAG validation
        run: ./scripts/validate-tags.sh
```

### 9.2. TAG 시스템 (moai-alfred-tag-scanning)

**TAG 구조**:
```
@SPEC:AUTH-001   # 요구사항 명세
@TEST:AUTH-001   # 테스트 코드
@CODE:AUTH-001   # 구현 코드
@DOC:AUTH-001    # 문서
```

**TAG 블록 예시**:
```python
"""
@CODE:AUTH-001 | SPEC: SPEC-AUTH-001.md | TEST: tests/auth/service.test.py

HISTORY:
v0.0.1 (2025-09-15): INITIAL - JWT-based authentication
v0.1.0 (2025-09-20): ADD - Refresh token support
v0.1.1 (2025-09-22): FIX - Token expiration handling
"""

def authenticate(username: str, password: str) -> str:
    """Authenticate user and return JWT token."""
    ...
```

**TAG 검증**:
```bash
# 중복 확인
rg "@SPEC:AUTH" -n

# 체인 무결성 확인
rg '@(SPEC|TEST|CODE|DOC):' -n .moai/specs/ tests/ src/ docs/

# 고아 TAG 탐지
rg '@CODE:AUTH-001' -n src/          # CODE exists
rg '@SPEC:AUTH-001' -n .moai/specs/  # SPEC missing → orphan
```

**moai-alfred-tag-scanning Skill**:
- 자동으로 TAG 스캔
- 고아 TAG 탐지
- TAG 인벤토리 생성
- 체인 무결성 검증

### 9.3. SPEC-First TDD 워크플로우

```
┌────────────────────────────────────────────────────────────────┐
│ Step 1: SPEC Authoring (/alfred:1-plan)                       │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ - Create .moai/specs/SPEC-<ID>/spec.md                        │
│ - Add @SPEC:ID TAG                                            │
│ - Write EARS syntax requirements                              │
│ - HISTORY section (v0.0.1 INITIAL)                            │
├────────────────────────────────────────────────────────────────┤
│ Step 2: TDD Implementation (/alfred:2-run)                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ RED:      Write @TEST:ID → watch it fail                      │
│ GREEN:    Add @CODE:ID → make test pass                       │
│ REFACTOR: Improve quality → document in TAG HISTORY           │
├────────────────────────────────────────────────────────────────┤
│ Step 3: Documentation Sync (/alfred:3-sync)                   │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ - Scan TAGs: rg '@(SPEC|TEST|CODE):' -n                       │
│ - Ensure no orphan TAGs                                       │
│ - Regenerate Living Document                                  │
│ - Move PR: Draft → Ready                                      │
└────────────────────────────────────────────────────────────────┘
```

---

## 10. 독특한 적용 방식 요약

### 10.1. MoAI-ADK만의 혁신

| Innovation                      | Description                                                              | Benefit                                       |
|---------------------------------|--------------------------------------------------------------------------|-----------------------------------------------|
| **4계층 아키텍처**                | Commands → Sub-agents → Skills → Hooks 분리                              | 명확한 책임 분리, 확장성 극대화                   |
| **체계적 명명 규칙**              | `moai-{tier}-{purpose}` 패턴                                             | Skills 발견 및 관리 용이                        |
| **확장 메타데이터**               | version, created, updated, status, keywords                              | 버전 관리, 검색 최적화                           |
| **템플릿화된 구조**               | 13개 표준 섹션                                                            | 일관성, 학습 곡선 단축                           |
| **Interactive Questions**       | TUI 기반 대화형 질문                                                       | "Vibe Coding" 문제 해결                          |
| **TRUST 5 통합**                 | 모든 Skills에 품질 원칙 강제                                               | 코드 품질 보증                                   |
| **TAG 시스템**                   | SPEC → TEST → CODE → DOC 추적성                                          | 요구사항 변경 시 영향 범위 즉시 파악              |
| **Alfred SuperAgent**            | 19개 Sub-agents 오케스트레이션                                             | 워크플로우 자동화                                 |
| **Progressive Disclosure 최적화** | Level 1/2/3 명확히 문서화                                                 | 토큰 효율성 극대화                                |
| **Language Pack (23개)**         | 언어별 Best Practices                                                     | 언어 전환 시에도 일관된 품질                      |

### 10.2. 공식 Skills 대비 장점

**확장성**:
- 공식: ~15개 예제
- MoAI-ADK: 55개 production-ready Skills

**일관성**:
- 공식: 자유로운 구조
- MoAI-ADK: 13개 표준 섹션 템플릿

**워크플로우 통합**:
- 공식: 독립적 사용
- MoAI-ADK: /alfred 명령어와 긴밀히 연계

**버전 관리**:
- 공식: 없음
- MoAI-ADK: Semantic Versioning + Changelog

**검색 최적화**:
- 공식: description만
- MoAI-ADK: + keywords, tier, status

### 10.3. 공식 Skills 대비 제약사항

**복잡성 증가**:
- 13개 섹션 → 초기 학습 부담
- 해결: 템플릿 자동 생성 (moai-skill-factory)

**유지보수 부담**:
- 55개 Skills → 도구 버전 업데이트 시 일괄 수정 필요
- 해결: 스크립트 자동화

**강한 의견 (Opinionated)**:
- MoAI-ADK 워크플로우에 최적화 → 다른 프로젝트에 직접 적용 어려움
- 해결: 계층별 분리 (Foundation, Essentials는 범용)

---

## 11. My-Spec 워크플로우 적용 가능성

### 11.1. My-Spec과 MoAI-ADK 비교

| Aspect                | My-Spec (현재)                    | MoAI-ADK                               | 적용 가능성 |
|-----------------------|----------------------------------|----------------------------------------|-----------|
| **워크플로우 구조**     | Slash Commands (`/ms.*`)         | Commands + Sub-agents + Skills + Hooks | ✅ 높음    |
| **명명 규칙**          | `ms.*` (명령어만)                 | `moai-{tier}-{purpose}` (Skills)       | ✅ 채택 가능|
| **품질 원칙**          | Constitution (EARS, TRUST, TAG)  | TRUST 5 + TAG system                   | ✅ 유사    |
| **자동화 수준**        | 부분적 (Slash Commands)          | 완전 자동화 (Alfred SuperAgent)         | 🟡 점진적  |
| **Skills 개수**        | 0 (미도입)                        | 55 (production-ready)                  | ✅ 높음    |
| **Interactive Q&A**    | 없음                              | moai-alfred-interactive-questions      | ✅ 도입 권장|

### 11.2. 추천 도입 전략

**Phase 1: Foundation Skills (Week 1-2)**

우선순위가 높은 Skills만 선별 도입:

1. **moai-foundation-trust** → Constitution Validator로 변형
   - TRUST 5 원칙 검증
   - Constitution Section II/V 통합

2. **moai-alfred-tag-scanning** → TAG Block Manager로 변형
   - TAG 블록 자동 삽입
   - TAG 체인 무결성 검증

3. **moai-alfred-ears-authoring** → EARS Pattern Checker로 변형
   - EARS 패턴 검증
   - 금지 문구 탐지

**Phase 2: Language Packs (Week 3-4)**

프로젝트 주요 언어에 맞춰 도입:

- Python 프로젝트 → `moai-lang-python` 참고하여 `ms-lang-python` 생성
- TypeScript 프로젝트 → `moai-lang-typescript` 참고

**Phase 3: Interactive Questions (Week 5-6)**

- `moai-alfred-interactive-questions` 참고하여 TUI 기반 질문 시스템 도입
- `/ms.clarify` 명령어와 통합

### 11.3. 명명 규칙 제안

MoAI-ADK 패턴을 따라 My-Spec 전용 명명 규칙:

```
ms-{tier}-{purpose}
```

**Tier 분류**:
- `ms-foundation-*`: 핵심 원칙 (constitution, ears, trust, tag)
- `ms-workflow-*`: /ms.* 명령어 보조
- `ms-lang-*`: 언어별 Best Practices
- `ms-domain-*`: 도메인별 전문화 (선택적)

**예시**:
```
✅ ms-foundation-constitution      # Constitution 검증
✅ ms-workflow-tag-manager         # TAG 블록 관리
✅ ms-workflow-ears-checker        # EARS 패턴 검증
✅ ms-lang-python                  # Python Best Practices
```

### 11.4. 템플릿 간소화 제안

MoAI-ADK의 13개 섹션은 과도할 수 있으므로, My-Spec용으로 간소화:

**핵심 섹션 (7개)**:
1. Skill Metadata
2. What It Does
3. When to Use
4. How It Works (핵심)
5. Failure Modes
6. Best Practices
7. Examples

**선택 섹션 (필요시 추가)**:
- Dependencies
- Changelog
- Works Well With

---

## 12. 결론 및 권장사항

### 12.1. 핵심 교훈

MoAI-ADK의 Skills 적용 분석에서 얻은 핵심 교훈:

1. **계층적 책임 분리의 중요성**
   - Commands, Sub-agents, Skills, Hooks를 명확히 구분
   - 각 레이어가 단일 책임만 수행
   - 확장성과 유지보수성 극대화

2. **일관성이 학습 곡선을 낮춘다**
   - 55개 Skills 모두 동일한 구조
   - 한 번 배우면 모두 이해 가능
   - 템플릿 자동화로 품질 일관성 유지

3. **Progressive Disclosure는 필수**
   - Level 1: Metadata만 로드 (~100 tokens)
   - Level 2/3: 필요시 로드
   - 55개 Skills 설치해도 초기 부담 최소화

4. **Interactive Questions가 "Vibe Coding"을 해결**
   - 모호한 요청 → 구체적 선택지 제시
   - TUI 메뉴로 명확한 의도 확인
   - 추측 제거 → 품질 향상

5. **TRUST + TAG 통합이 신뢰성을 보증**
   - TRUST 5 원칙 강제
   - TAG 체인으로 추적성 확보
   - CI/CD에서 자동 검증

### 12.2. My-Spec에 대한 권장사항

**즉시 적용 가능 (High Priority)**:

1. ✅ **Skills 디렉토리 구조 생성**
   ```
   .claude/skills/
   ├── ms-foundation-constitution/
   ├── ms-workflow-tag-manager/
   ├── ms-workflow-ears-checker/
   └── ms-workflow-living-docs-updater/
   ```

2. ✅ **명명 규칙 채택**
   - `ms-{tier}-{purpose}` 패턴
   - MoAI-ADK와 유사하지만 My-Spec에 맞게 조정

3. ✅ **템플릿 간소화**
   - 13개 섹션 → 7개 핵심 섹션
   - Metadata 확장 (version, status, keywords)

4. ✅ **Progressive Disclosure 문서화**
   - Level 1/2/3 구분 명확히
   - description에 트리거 키워드 포함

**점진적 도입 (Medium Priority)**:

5. 🟡 **Interactive Questions 기능**
   - TUI 기반 질문 시스템
   - `/ms.clarify` 통합

6. 🟡 **Language Packs**
   - 프로젝트 주요 언어부터 시작
   - moai-lang-* 참고하여 ms-lang-* 생성

**장기 고려 (Low Priority)**:

7. 🔵 **Sub-agents 도입**
   - Slash Commands → Commands + Sub-agents 분리
   - Alfred 스타일 오케스트레이션

8. 🔵 **Hooks 시스템 강화**
   - SessionStart, PreToolUse 이벤트 활용
   - 기존 hooks 디렉토리와 통합

### 12.3. 성공 메트릭

Skills 도입 후 측정할 지표:

**정량적 지표**:
- Skills 자동 트리거 정확도 (목표: >80%)
- 평균 문맥 토큰 소비 (목표: <10K tokens per session)
- TAG 체인 무결성 비율 (목표: 100%)
- TRUST 5 준수율 (목표: >90%)

**정성적 지표**:
- 사용자 피드백 ("Vibe Coding" 문제 감소)
- 학습 곡선 (새 Skills 이해 시간)
- 유지보수 편의성 (Skills 업데이트 소요 시간)

---

## 13. 참고 자료

### 13.1. MoAI-ADK 문서

- [MoAI-ADK GitHub](https://github.com/modu-ai/moai-adk)
- [MoAI-ADK README (한국어)](https://github.com/modu-ai/moai-adk/blob/main/README.ko.md)
- [MoAI-ADK CLAUDE.md](https://github.com/modu-ai/moai-adk/blob/main/CLAUDE.md)

### 13.2. Anthropic 공식 문서

- [Claude Code Skills 공식 문서](https://docs.claude.com/ko/docs/claude-code/skills)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Agent Skills Specification](https://github.com/anthropics/skills/blob/main/agent_skills_spec.md)

### 13.3. My-Spec 관련 문서

- [My-Spec SKILLS.md](/workspace/specter/SKILLS.md)
- [My-Spec Constitution](/.specify/memory/constitution.md)
- [My-Spec Slash Commands](/.claude/commands/)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-23
**Author**: My-Spec Team
**Reference Repositories**:
- moai-adk @ docs/references/moai-adk
- anthropics/skills @ docs/references/skills

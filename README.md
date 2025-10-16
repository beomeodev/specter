# Specter

**AI 협업을 위한 헌법 기반 프로젝트 템플릿**

Specter는 AI 에이전트와의 협업에서 발생하는 품질 문제를 시스템적으로 차단하는 프로젝트 템플릿입니다. Constitution(헌법), TAG 추적 시스템, TRUST 검증을 통해 **추적 가능하고, 테스트 가능하며, 유지보수 가능한 코드**를 보장합니다.

---

## ✨ 핵심 특징

### 🏛️ Constitution 기반 거버넌스
- **단일 진실 출처**: 모든 규칙이 `.specify/memory/constitution.md`에 집중
- **자동 적용**: AI가 헌법을 읽고 자동으로 준수
- **프로젝트별 커스터마이징**: Section IX는 spec.md/plan.md에서 자동 추출

### 🏷️ TAG 추적 시스템
```
@SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
```
- 요구사항 → 테스트 → 코드 **완전 추적성**
- 도메인별 자동 ID 생성 (AUTH, USER, PAY 등)
- ripgrep 기반 고속 스캔

### ✅ TRUST 3단계 검증
```
Level 1: Structure  → CRITICAL 위반 시 차단
Level 2: Quality    → CRITICAL 위반 시 차단
Level 3: Deep       → HIGH/MEDIUM은 경고
```
- **진보적 검증**: 빠른 실패, 빠른 수정
- **자동화된 품질**: ESLint, ripgrep, TypeScript 활용
- **커버리지 강제**: 테스트 커버리지 ≥80% 필수

### 🤖 AI 협업 최적화
- **서브 에이전트 자동 실행**: 복잡도에 따라 병렬 에이전트 실행
- **Context7 MCP 통합**: 최신 라이브러리 문서 자동 조회
- **ultrathink 패턴 분석**: 시스템적 이슈 탐지 + 배치 수정 제안

---

## 🚀 5분 Quick Start

### 1️⃣ 프로젝트 초기화
```bash
# Spec-Kit + Constitution 설치
/ms.init
```

**생성되는 것**:
- `.specify/memory/constitution.md` - 프로젝트 헌법
- `.specify/` - Spec-Kit 디렉토리 구조
- `.claude/commands/speckit.*` - 기본 워크플로우 커맨드

### 2️⃣ 기능 사양 작성
```bash
# 예: 사용자 인증 기능
/ms.specify user-authentication
```

**AI가 자동으로**:
- 요구사항을 EARS 패턴으로 변환 (WHEN/WHILE/WHERE/IF/SHALL)
- 복잡도에 따라 서브 에이전트 병렬 실행
- 기존 패턴 검색 + 최신 라이브러리 문서 조회
- `specs/001-user-authentication/spec.md` 생성 (영어)

### 3️⃣ 구현 계획
```bash
/ms.plan
```

**AI가 자동으로**:
- TRUST 원칙에 따른 아키텍처 설계
- 파일 크기 제한 (≤500 SLOC), 함수 크기 (≤100 LOC) 적용
- `specs/001-user-authentication/plan.md` 생성

### 4️⃣ 헌법 추출 + 태스크 생성
```bash
# Constitution Section IX 자동 생성
/ms.constitution

# TAG ID 자동 할당
/ms.tasks
```

**생성되는 것**:
- Constitution Section IX (프로젝트별 제약사항)
- `AGENTS.md` (프로젝트 코딩 규칙)
- `tasks.md` with TAG chains (`@SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001`)

### 5️⃣ 품질 검증
```bash
/ms.analyze
```

**2단계 검증**:
1. **문서 일관성**: spec ↔ tasks 매칭 검증
2. **TRUST 3레벨**: 구조 → 품질 → 심층 분석

**CRITICAL 위반 시 구현 차단!**

### 6️⃣ 구현
```bash
# 첫 번째 미완료 TAG 자동 선택
/ms.implement
```

**AI가 자동으로**:
- Constitution + AGENTS.md 준수
- TAG 블록 자동 삽입
- Context7 MCP로 최신 라이브러리 API 사용
- 테스트 우선 작성 (TDD)

### 7️⃣ 코드 리뷰
```bash
/ms.review
```

**검증 항목**:
- ✅ 명명 규칙 (도메인 용어 사용)
- ✅ 아키텍처 일관성 (plan.md 준수)
- ✅ 성능 이슈 (N+1 쿼리 등)
- ✅ 보안 심층 분석
- ✅ 테스트 품질

**특별 기능**:
- **ultrathink 패턴 분석**: 시스템적 문제 탐지 + ROI 계산
- **자동 수정 제안**: N+1 쿼리, 인증 가드 등
- **리포트 저장**: `docs/review/review_[Agent]_[timestamp].md`

### 8️⃣ 완료
```bash
/fin
```

**자동으로**:
1. `docs/dev_daily.md` 업데이트 (작업 내역)
2. CI 체크 (black, ruff, mypy, pytest)
3. Git 커밋 + 푸시

---

## 📁 프로젝트 구조

```
specter/
├── .claude/
│   ├── commands/           # 슬래시 커맨드 (ms.*.md)
│   │   ├── ms.init.md     # 프로젝트 초기화
│   │   ├── ms.specify.md  # 사양 작성
│   │   ├── ms.plan.md     # 구현 계획
│   │   ├── ms.tasks.md    # 태스크 생성 (TAG ID 자동)
│   │   ├── ms.analyze.md  # TRUST 검증
│   │   ├── ms.implement.md# 구현 (TAG 자동 선택)
│   │   ├── ms.review.md   # 코드 리뷰 (enhanced)
│   │   └── fin.md         # 완료 (dev_daily.md + CI + commit)
│   └── hooks/             # Constitution 자동 주입 훅
├── templates/
│   └── constitution-template.md  # Constitution 템플릿
├── src/lib/               # TAG + TRUST 라이브러리
│   ├── tag/              # TAG 생성, 스캔, 검증
│   └── trust/            # TRUST 3레벨 검증
├── docs/
│   ├── dev_daily.md      # 일일 작업 로그
│   └── review/           # 코드 리뷰 리포트
├── AGENTS.md             # AI 코딩 규칙 (13개 섹션)
└── README.md             # 이 파일
```

---

## 🎯 Constitution 핵심 원칙

### I. Test-First Development (절대 규칙)
```
테스트 → 구현 → 리팩토링
```
- 테스트 없이 구현 불가
- 커버리지 ≥80% 강제
- Phase 3.2 (Tests) 완료 후 Phase 3.3 (Implementation) 진행

### II. Simplicity-First Architecture
```
기존 도구 > 새로 만들기
```
- ESLint, ripgrep, TypeScript 같은 검증된 도구 활용
- 커스텀 파서 금지
- 파일 ≤500 SLOC, 함수 ≤100 LOC

### IV. EARS 요구사항 표준
```
WHEN  - 이벤트 기반
WHILE - 상태 기반
WHERE - 조건부 기능
IF    - 제약사항
SHALL - 무조건 준수
```

### V. TRUST 5원칙
- **T**est-First: TDD, ≥80% 커버리지
- **R**eadable: 파일 ≤500 SLOC, 복잡도 ≤10
- **U**nified: TypeScript strict, 린트 0 경고
- **S**ecured: 입력 검증, .env 보안
- **T**rackable: TAG 시스템 (SPEC→TEST→CODE)

### IX. Project-Specific Constraints (자동 생성)
`/ms.constitution` 실행 시 spec.md + plan.md에서 자동 추출

---

## 🔧 고급 기능

### Context7 MCP 통합
```python
# 최신 라이브러리 문서 자동 조회
lib_id = mcp__context7__resolve_library_id("fastapi")
docs = mcp__context7__get_library_docs(lib_id, topic="background tasks")
```

AI 지식 컷오프 문제 해결!

### 서브 에이전트 자동 실행
복잡도에 따라 자동으로 병렬 실행:
- **Pattern_Search_Agent**: 기존 코드베이스 패턴 검색
- **Library_Research_Agent**: Context7로 최신 문서 조회
- **Dependency_Analysis_Agent**: 통합 지점 분석

### ultrathink 패턴 분석
```
🔍 SYSTEMIC ISSUES DETECTED: 3

1. Inconsistent Error Handling
   📊 5 occurrences across 3 services

   ROOT CAUSE: No team error handling convention

   BATCH FIX: 2 hours → Saves 10 hours/month
   ROI: 286%
```

시스템적 문제 탐지 + 배치 수정 제안!

---

## 📖 전체 워크플로우

```
1. /ms.init          # 초기화 (Constitution 설치)
2. /ms.specify       # 사양 작성 (EARS 패턴)
3. /ms.clarify       # 요구사항 명확화 (필요시)
4. /ms.plan          # 구현 계획 (TRUST 적용)
5. /ms.constitution  # 헌법 추출 (Section IX + AGENTS.md)
6. /ms.tasks         # 태스크 생성 (TAG ID 자동)
7. /ms.analyze       # 품질 검증 (2단계)
8. /ms.implement     # 구현 (TAG 자동 선택)
9. /ms.review        # 코드 리뷰 (ultrathink)
10. /fin             # 완료 (dev_daily + CI + commit)
```

---

## 💡 언제 사용하나요?

### ✅ 적합한 프로젝트
- 스타트업 MVP (빠른 품질 검증 필요)
- 오픈소스 프로젝트 (문서화 + 추적성 중요)
- 레거시 리팩토링 (TAG 시스템으로 변경 추적)
- AI 협업 프로젝트 (Constitution 기반 규칙 공유)

### ❌ 부적합한 프로젝트
- 1회성 스크립트 (<100 LOC)
- 극도로 단순한 프로젝트

---

## 🆚 기존 방식과의 비교

| 항목 | 기존 방식 | Specter 방식 |
|------|----------|-------------|
| **규칙 관리** | README에 산재 | Constitution 집중 |
| **추적성** | Git log 의존 | TAG 시스템 |
| **품질 검증** | CI 실패 후 수정 | 3레벨 진보적 검증 |
| **AI 가이드** | 프롬프트 수동 작성 | Constitution 자동 주입 |
| **최신 문서** | Google 검색 | Context7 MCP |
| **패턴 분석** | 수동 코드 리뷰 | ultrathink 자동 탐지 |

---

## 📚 상세 문서

### Core Concepts
- [CLAUDE.md](./CLAUDE.md) - AI 코딩 규칙 (13개 섹션)
- [Constitution Template](./templates/constitution-template.md) - 헌법 템플릿
- [src/README.md](./src/README.md) - TAG/TRUST 라이브러리 API

### Commands
- [.claude/commands/](./claude/commands/) - 슬래시 커맨드 상세 문서 (14개)

### Libraries
- [src/lib/tag/](./src/lib/tag/) - TAG 생성, 스캔, 검증
- [src/lib/trust/](./src/lib/trust/) - TRUST 3레벨 검증

---

## 🛠️ 기술 스택

### 필수 도구
- **ripgrep** (≥13.0): TAG 스캔
- **Node.js** (≥18): TypeScript 라이브러리 실행
- **Git**: 버전 관리

### 선택적 도구 (언어별)
- **TypeScript/JavaScript**: ESLint, TypeScript Compiler
- **Python**: black, ruff, mypy, pytest
- **Go**: golangci-lint
- **Rust**: clippy

---

## 🤝 기여

이 프로젝트는 개인 프로젝트 템플릿이지만, 개선 제안은 환영합니다!

### 개선 제안
1. Issue 생성
2. 개선 사항 설명
3. PR 제출 (선택)

---

## 📄 라이센스

MIT License - 자유롭게 사용 가능

---

## 🙏 Credits

- **Spec-Kit**: [GitHub의 사양 관리 도구](https://github.com/github/spec-kit)
- **TAG System**: [MoAI-ADK](https://github.com/modu-ai/moai-adk)에서 영감
- **TRUST Principles**: My-Spec Constitution
- **Context7 MCP**: [Context7](https://context7.com/) 라이브러리 문서 서비스
- **ripgrep**: [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep)

---

## 🎉 시작하기

```bash
# 1. 프로젝트 초기화
/ms.init

# 2. 첫 번째 기능 사양 작성
/ms.specify my-first-feature

# 3. 워크플로우 따라가기
# → /ms.plan → /ms.constitution → /ms.tasks → /ms.analyze → /ms.implement → /ms.review → /fin
```

**Happy Coding with AI! 🤖✨**

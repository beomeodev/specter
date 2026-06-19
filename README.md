<div align="center">
    <h1>👻 SPECTER</h1>
    <h3><em>AI와 함께하는 고품질 소프트웨어 개발 워크플로우</em></h3>
</div>

<p align="center">
    <strong>Specification-Progressive Enforcement & Constitution-based Traceability, Evolutionary Review</strong>
</p>

<p align="center">
    사양 기반 점진적 검증 · 헌법 기반 추적성 · 진화적 리뷰
</p>

---

## 빠른 시작

```bash
/ms.init
/ms.featuremap @docs/prd/PRD.md [@docs/prd/another.md]
/ms.codex-checklist @docs/prd/PRD.md [@docs/prd/another.md]
/ms.verify
/ms.constitution
/ms.checklist
/ms.codex-verify
/ms.specify   # docs/prd/feature-map.md의 체크된 Feature 섹션을 붙여넣기
```

---

## SPECTER란?

SPECTER는 GitHub Spec-Kit 위에 올라가는 Claude Code workflow overlay입니다.
Spec-Kit의 `/speckit.*` 명령을 그대로 버리지 않고, 그 위에 다음을 더합니다.

- **GEARS 요구사항**: 모호한 PRD/기능 설명을 검증 가능한 요구사항으로 변환
- **Feature Map 게이트**: PRD Commitment Index로 전체 소유권을 고정하고, Feature별로 PRD 반영도를 검증
- **Constitution**: 체크된 PRD Feature Map에서 프로젝트 기준을 1회 추출해 단일 위치에 고정
- **TAG 추적성**: `@SPEC → @TEST → @CODE → @DOC` 체인으로 요구사항부터 코드까지 연결
- **점진적 검증**: Feature Map, 문서 정합성, 코드 품질을 각각 알맞은 시점에 차단

SPECTER만 단독으로 동작하지 않습니다. `/ms.init`이 Spec-Kit을 설치하고 SPECTER overlay를 주입합니다.

## 릴리즈

현재 릴리즈: `v2.0.0`

자세한 변경 내역은 [CHANGELOG.md](./CHANGELOG.md)를 확인하세요.

---

## 핵심 문제와 해법

### 1. AI는 규칙을 잊어버립니다

```text
"파일은 작게 나눠서 작성해"
→ 몇 파일 뒤부터 다시 거대한 파일 생성
```

SPECTER는 `.specify/memory/constitution.md`와 `AGENTS.md`를 통해 규칙을 반복 주입합니다.

### 2. 요구사항이 모호하면 구현도 흔들립니다

```text
"로그인 기능 만들어줘"
→ 인증 방식, 실패 처리, 세션 정책이 모두 불명확
```

SPECTER는 GEARS 형식을 사용합니다.

```text
When a user submits valid credentials, the auth service shall issue a session token.
[Error Handling] When credentials are invalid, the auth service shall return a generic authentication error.
```

### 3. 코드가 왜 존재하는지 추적하기 어렵습니다

```typescript
/**
 * @SPEC:AUTH-001 User Authentication
 * @TEST:AUTH-001 tests/auth.test.ts::should_authenticate_user
 * @CODE:AUTH-001
 */
export class AuthService {}
```

TAG 체인은 요구사항, 테스트, 코드, 문서를 빠르게 역추적하게 해줍니다.

---

## 워크플로우

### 전체 흐름

```bash
# 0. PRD 작성
# docs/prd/PRD.md 또는 복수 PRD

# 1. 초기화: Spec-Kit 설치 + 기본 Constitution 생성
/ms.init

# 2. PRD를 Feature DAG로 분해하고, 각 Feature 섹션을 /ms.specify 프롬프트로 작성
/ms.featuremap @docs/prd/PRD.md [@docs/prd/another.md]

# 3. Codex가 PRD만 보고 독립 체크리스트 생성
/ms.codex-checklist @docs/prd/PRD.md [@docs/prd/another.md]

# 4. Claude가 PRD + Codex checklist + Feature Map을 대조해 global gate 생성
/ms.verify

# 5. 프로젝트 기준 확정: 검증된 PRD Feature Map 기준으로 보통 1회만
/ms.constitution

# 아래 단계는 Feature Map의 Feature별로 DAG 순서대로 반복

# 6. 이번 Feature 검증: Source PRDs, PRD references, Commitment Index 반영도 체크
/ms.checklist

# 7. Codex가 이번 Feature checklist를 짧게 검증
/ms.codex-verify

# 8. 사양 작성: 체크된 Feature Map 섹션을 입력
/ms.specify

# 9. 요구사항 명확화, 사실상 필수
/ms.clarify

# 10. 구현 계획 작성
/ms.plan

# 11. TAG 기반 태스크 생성
/ms.tasks

# 12. 구현 전 문서 정합성 검증: spec ↔ plan ↔ tasks
/ms.analyze

# 13. TDD 구현 + TAG 삽입
/ms.implement

# 14. 코드 리뷰 + 실행 게이트: lint/type/test/build/coverage/TAG
/ms.review

# 15. 문서 동기화, 커밋, push, PR
/fin    # CI 포함
/finq   # 빠른 백업용, CI 생략

# 16. 승인된 PR 머지 + 태그 + GitHub Release
/ms.merglease
```

다음 Feature도 `/ms.checklist`부터 반복합니다. 전체 Feature Map이 생성되거나 바뀌면 `/ms.codex-checklist`와 `/ms.verify`를 다시 실행하고, 기본 `/ms.checklist`는 매 Feature 사이클 첫 단계에서 실행합니다.

### 곁가지 트랙

새 요구사항이 아닌 버그 수정, 문구 수정, 스타일 조정, 리팩토링은 전체 사양 흐름을 타지 않습니다.

```bash
/ms.fix
/fin 또는 /finq
/ms.merglease
```

구현 중 발견한 설계 변경이 spec/plan에 반영되어야 하면 다음을 사용합니다.

```bash
/ms.amend "변경 내용"
/ms.analyze
/ms.implement
```

---

## Constitution 위치와 사용법

SPECTER에는 Constitution 관련 개념이 두 단계 있습니다.

### 1. 기본 Constitution

`/ms.init`이 `.specify/memory/constitution.md`를 생성합니다. 이 파일은 `/ms.specify` 이전부터 이미 활성화됩니다.

기본 Constitution에는 다음 규칙이 들어 있습니다.

- Test-first development
- Simplicity-first architecture
- GEARS requirements
- TRUST principles
- TAG traceability
- Security and documentation rules

즉, “Constitution을 specify 직전에 둔다”는 목적은 이미 `/ms.init`이 충족합니다. 사양 작성 전에도 AI는 기본 Constitution을 읽고 따라야 합니다.

### 2. `/ms.constitution` 명령

`/ms.constitution`은 기본 Constitution을 새로 만드는 명령이 아닙니다. `/ms.verify`로 검증된 PRD Feature Map을 기준으로 Section IX에 **project-wide baseline**을 확정하는 명령입니다.

그래서 현재 명령은 Feature 사이클 안이 아니라 `/ms.verify` 직후에 둡니다. 이유는 간단합니다.

- PRD와 Feature Map은 전체 제품 경계, cross-feature owner, deferred work를 가장 먼저 보여줍니다.
- Section IX는 개별 Feature의 구현 세부사항이 아니라 모든 Feature에 적용될 durable rule만 담아야 합니다.
- 이 baseline이 먼저 있어야 이후 `/ms.specify`, `/ms.plan`, `/ms.tasks`가 같은 프로젝트 기준을 공유합니다.

정리하면:

```text
/ms.init                  → 기본 Constitution 활성화
/ms.codex-checklist      → PRD-only 독립 체크리스트 생성
/ms.verify               → PRD + Codex checklist + Feature Map 검증
/ms.constitution          → Section IX baseline 확정, 보통 1회
```

이후 Feature에서는 `/ms.constitution`을 반복하지 않습니다. 정말 project-wide rule을 바꿔야 할 때만 명시적으로 재실행합니다.

---

## 핵심 커맨드

| 명령어 | 역할 | 주요 산출물 |
| --- | --- | --- |
| `/ms.init` | Spec-Kit 설치 + SPECTER overlay 주입 | `.specify/`, Constitution, AGENTS.md |
| `/ms.featuremap` | PRD set을 Feature DAG로 분해하고 각 Feature 섹션을 `/ms.specify` 프롬프트로 작성 | `docs/prd/feature-map.md` |
| `/ms.codex-checklist` | Codex PRD-only 독립 체크리스트 생성 | `docs/prd/codex/checklist.md` |
| `/ms.verify` | PRD + Codex checklist + Feature Map 대조 검증 | `docs/prd/feature-map.checklist.md` |
| `/ms.checklist` | 다음 Feature의 PRD 반영도 검증 | `docs/prd/checklists/feature-NNN.checklist.md` |
| `/ms.codex-verify` | Codex per-Feature checklist 검증 | `docs/prd/checklists/feature-NNN.codex-verify.md` |
| `/ms.specify` | 체크된 Feature 섹션 프롬프트를 GEARS spec으로 변환 | `specs/{id}/spec.md` |
| `/ms.clarify` | 요구사항 명확화 | spec.md 업데이트 |
| `/ms.plan` | Reality Verified 구현 계획 수립 | `specs/{id}/plan.md` |
| `/ms.constitution` | 체크된 PRD Feature Map 기반 project-wide baseline 확정 | Constitution Section IX, AGENTS.md |
| `/ms.tasks` | TAG 기반 태스크 생성 | `specs/{id}/tasks.md` |
| `/ms.analyze` | 구현 전 문서 정합성 + Codex 문서 검증 | `specs/{id}/analyze.codex.md`, pass/fail report |
| `/ms.implement` | 선택된 phase/task/TAG scope 구현 + TAG 삽입 | code, tests, TAG blocks |
| `/ms.review` | 코드 리뷰 + Codex review + 실행 게이트 | `docs/review/`, review state |
| `/ms.up-docs` | Living docs 동기화 | `docs/dev_daily.md`, API docs |
| `/fin` | 문서 동기화 + CI + commit/push/PR | commit, PR |
| `/finq` | 빠른 commit/push/PR | commit, PR |
| `/ms.fix` | 비요구사항 변경 경량 트랙 | FIX TAG |
| `/ms.amend` | 구현 후 spec/plan 정정 | Amendment block |
| `/ms.merglease` | PR merge + tag + GitHub Release | tag, release |

---

## 게이트 구조

### Global Feature Map 게이트

SPECTER는 Spec-Kit의 native checklist를 단순 호출하지 않습니다. Global 단계는 두 단계입니다.

`/ms.codex-checklist`는 Codex를 백그라운드에서 실행해 PRD만을 원천으로 독립 체크리스트를 만듭니다. 이 단계는 `feature-map.md`를 평가하지 않고, PRD에서 절대 빠지면 안 되는 commitment, acceptance criteria, NFR, data/integration/security promise, explicit exclusion을 추출합니다.

`/ms.verify`는 PRD 원본, Codex checklist, Feature Map을 대조해 canonical global gate인 `docs/prd/feature-map.checklist.md`를 생성합니다. 이 단계는 PRD Commitment Index를 기준으로 PRD의 모든 commitment가 정확히 하나의 Feature owner를 갖는지, DAG와 Stub-and-Forward가 성립하는지 검증합니다.

### `/ms.checklist`: Per-Feature 게이트

기본 `/ms.checklist`는 매 Feature 사이클의 첫 단계입니다. DAG상 다음 Feature를 고르고, 그 Feature의 Source PRDs, PRD references, PRD Commitment Index rows를 실제 PRD 섹션과 대조합니다.

검증 항목:

- PRD의 모든 commitment가 PRD Commitment Index에 있고 정확히 하나의 Feature owner를 갖는가
- 이번 Feature가 소유한 PRD commitment를 scope, out-of-scope, key decisions, done criteria에 충분히 반영했는가
- 이번 Feature가 다른 Feature 소유의 PRD commitment를 침범하지 않는가
- out-of-scope 항목이 후속 Feature를 가리키는가
- DAG cycle이 없고 이번 Feature의 dependency가 충족되었는가
- Stub-and-Forward 항목이 activation Feature를 갖는가
- Phase E2E scenario가 마지막 Feature done criteria에 들어갔는가
- Feature Map이 PRD를 복제하지 않고 reference와 ownership만 유지하는가

`/ms.specify`와 injected `/speckit.specify`는 global audit, per-Feature audit, 또는 Codex per-Feature verification이 없거나 실패했거나, Feature Map SHA가 달라져 stale 상태면 거부합니다.

### `/ms.analyze`: 문서 정합성 게이트

구현 전에 `spec.md`, `plan.md`, `tasks.md`가 서로 맞는지 확인합니다. 기본 실행에서는 Codex가 foreground로 보조 문서 검증을 수행하며, 큰 문서 세트에서는 `--background`를 사용할 수 있습니다.

검증 항목:

- 모든 FR에 구현 태스크가 있는가
- orphan task가 없는가
- migration/file path drift가 없는가
- Amendment가 기존 FR/task와 충돌하지 않는가
- Constitution/AGENTS 기준이 plan/tasks에 반영되었는가
- Codex가 Feature Map, checklist, spec, plan, tasks 간 drift를 추가로 지적했는가

### `/ms.review`: 코드 게이트

구현 후 PR 전에 실행합니다. 기본 실행에서는 Codex가 foreground로 보조 코드 리뷰를 수행하며, 큰 변경에서는 `--background`를 사용할 수 있습니다.

검증 항목:

- 코드 구조, 명명, 중복, 오류 처리, 보안, 성능
- 테스트 품질
- lint, typecheck, tests, build
- coverage, complexity, security scan
- TAG integrity
- Codex가 spec/task intent drift, 테스트 누락, 보안/데이터/동시성 리스크를 지적했는가

`--fast`나 `--focus`를 사용해도 critical executable gate는 건너뛰지 않습니다. Codex 검증은 `--skip-codex`로 명시적으로 생략할 수 있습니다.

---

## 실행 환경과 가드레일

워크플로(프롬프트 레이어) 아래에는 규칙을 기계가 강제하는 얇은 하네스 레이어가 깔려 있습니다.

- **격리 환경**: `.devcontainer`에서 컨테이너를 보안 경계로 두고 에이전트를 실행합니다(non-root, 메모리 제한).
- **CI 게이트**: `.github/workflows/ci.yml`이 `uv`로 의존성을 설치하고 lint(ruff)·type(mypy)·test(pytest)를 실행합니다.
- **pre-commit**: `.pre-commit-config.yaml`이 커밋 시 ruff·mypy·bandit를 자동 검사합니다.
- **권한 베이스라인**: `.claude/settings.json`이 안전한 명령은 허용, 파괴적 명령은 차단하고 커밋·푸시는 확인을 받습니다. 개인용 권한은 git에 추적되지 않는 `.claude/settings.local.json`에 둡니다.

도구 체인은 `uv` + `pyproject.toml`로 통일되어 있어 로컬(`make ci`)과 CI가 같은 게이트를 실행합니다.

---

## 프로젝트 구조

```text
specter/
├── .claude/
│   ├── commands/           # slash commands
│   ├── agents/             # subagents
│   ├── skills/             # reusable skills
│   └── settings.json       # 권한 베이스라인 (가드레일)
├── .devcontainer/          # 격리 실행 환경
├── .github/workflows/      # CI 게이트 (ci.yml)
├── .pre-commit-config.yaml # 커밋 단계 검사
├── pyproject.toml          # 의존성 + 게이트 설정 (uv)
├── .specify/
│   ├── memory/
│   │   └── constitution.md
│   └── scripts/
├── docs/
│   ├── prd/
│   │   ├── PRD.md
│   │   ├── feature-map.md
│   │   ├── feature-map.checklist.md
│   │   ├── codex/
│   │   │   └── checklist.md
│   │   └── checklists/
│   │       ├── feature-NNN.checklist.md
│   │       └── feature-NNN.codex-verify.md
│   ├── review/
│   ├── api/
│   ├── dev_daily.md
│   ├── todo.md
│   ├── SYSTEM_MAP.md
│   └── templates/
├── specs/
│   └── 001-{feature}/
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
├── AGENTS.md
├── CLAUDE.md
└── README.md
```

---

## 설치

```bash
npx degit beomeodev/specter my-new-project
cd my-new-project
npm install  # 또는 프로젝트에 맞는 설치 명령
```

이후 Claude Code에서 다음을 실행합니다.

```bash
/ms.init
```

---

## 언제 사용하나요?

적합한 경우:

- AI와 함께 기능을 지속적으로 개발하는 프로젝트
- PRD, 사양, 구현, 리뷰의 추적성이 중요한 프로젝트
- 여러 Feature를 순차적으로 쪼개서 배포하는 MVP/제품 개발
- 장기 유지보수에서 “이 코드가 왜 있나”를 빠르게 확인해야 하는 코드베이스

덜 적합한 경우:

- 1회성 스크립트
- 100 LOC 안팎의 실험 코드
- 사양과 추적성이 유지보수 비용보다 큰 초소형 프로젝트

---

## 필수 도구

- `git`
- `ripgrep` 13+
- `uv` / `uvx`
- Claude Code
- Codex plugin for Claude Code (`openai/codex-plugin-cc`)
- Codex CLI 인증 및 사용 가능 상태
- 프로젝트별 테스트/린트/타입체크 도구

선택 도구:

- Context7 MCP: 최신 라이브러리 문서 조회
- GitHub CLI: `/fin`, `/ms.merglease` 흐름에서 PR/release 자동화

---

## 상세 문서

- [AGENTS.md](./AGENTS.md) - AI coding rules
- [CLAUDE.md](./CLAUDE.md) - Claude Code 협업 규칙
- [SYSTEM_MAP.md](./docs/SYSTEM_MAP.md) - agent-facing architecture snapshot
- [Constitution Template](./docs/templates/constitution-template.md)
- [.claude/commands/](./.claude/commands/) - slash command definitions
- [.claude/agents/](./.claude/agents/) - subagent definitions
- [.claude/skills/](./.claude/skills/) - skill definitions

---

## Credits

- [Spec-Kit](https://github.com/github/spec-kit)
- [Context7 MCP](https://context7.com/)
- [ripgrep](https://github.com/BurntSushi/ripgrep)
- [Claude Code](https://claude.com/claude-code)

---

MIT License

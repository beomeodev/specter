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
/ms.agent-verify
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

현재 릴리즈: `v2.2.0`

`v2.2.0` 하이라이트: **per-Feature 워크플로우 정비** — `/ms.specter` 사이클 조정자 신설(clarify만
사람 개입), `/ms.review` 적대적 리뷰 기본화, `/ms.agent-verify`·`/ms.verify` foreground 병렬화,
`/fin`·`/finq` → `/ms.fin` 단일화(조건부 CI).
자세한 내용은 아래 [Spec Kit 호환성](#spec-kit-호환성) 섹션과 [CHANGELOG.md](./CHANGELOG.md)를 확인하세요.

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

```text
────────────────────────────────────────────────────────────────────
 📄  준비 (Setup)
────────────────────────────────────────────────────────────────────
     0. PRD 작성             docs/prd/PRD.md (또는 복수 PRD)
     1. /ms.init             Spec-Kit 설치 + 기본 Constitution
                            │
                            ▼
════════════════════════════════════════════════════════════════════
 🗺️  Pre-Feature 사이클   ·  1회  ·  묶음 실행: /ms.pre-specter
════════════════════════════════════════════════════════════════════
     2. /ms.featuremap       PRD → Feature DAG 분해
     3. /ms.codex-checklist  Codex 독립 체크리스트 (백그라운드)
     4. /ms.verify           PRD + Codex + Antigravity 대조 → 전역 게이트
     5. /ms.constitution     프로젝트 기준 (Constitution §IX) 확정
                            │
                            ▼   Feature마다 DAG 순서로 반복
════════════════════════════════════════════════════════════════════
 🛰️  Per-Feature 사이클   ·  N회  ·  묶음 실행: /ms.specter
════════════════════════════════════════════════════════════════════
  ┌─▶  6. /ms.checklist      이번 Feature 검증 (PRD 반영도)
  │    7. /ms.agent-verify   Codex + Antigravity 짧은 검증
  │    8. /ms.specify        사양 작성 (Feature 섹션 입력)
  │    9. /ms.clarify        🔴 요구사항 명확화 — 사람이 응답
  │   10. /ms.plan           구현 계획 + reality 검증
  │   11. /ms.tasks          TAG 기반 태스크 생성
  │   12. /ms.analyze        spec ↔ plan ↔ tasks 정합성
  │   13. /ms.implement      TDD 구현 + TAG 삽입
  │   14. /ms.review         코드 리뷰 + 실행 게이트 (lint/type/test/build)
  └──── 다음 Feature가 남으면 6번으로 되돌아가 반복
                            │   모든 Feature 완료
                            ▼
────────────────────────────────────────────────────────────────────
 🚀  발행 / 릴리즈 (Publish / Release)
────────────────────────────────────────────────────────────────────
    15. /ms.fin              docs 동기화 → 조건부 CI → commit · push · PR
    16. /ms.merglease        PR 머지 → tag → GitHub Release
```

두 사이클은 각각 한 명령으로 묶여 있습니다. PRD·Feature Map은 `@`로 첨부합니다.

- **Pre-Feature 사이클** (2~5): `/ms.pre-specter @docs/prd/PRD.md [@docs/prd/another.md]` — `verify`(PASS/WARN)를 통과하면 `constitution`까지 자동으로 이어집니다.
- **Per-Feature 사이클** (6~14): `/ms.specter @docs/prd/PRD.md @docs/prd/feature-map.md 006` — `clarify`만 사람이 답하면 `review`까지 자동으로 이어지며, Feature마다 DAG 순서로 반복합니다.
- **발행** (15): `/ms.fin`은 `review` 후 변경이 없으면 CI를 생략하고, 변경이 있으면 실행합니다(`--no-ci`로 강제 생략).

전체 Feature Map을 새로 만들거나 바꾸면 `/ms.codex-checklist`와 `/ms.verify`(또는 `/ms.pre-specter`)를 다시 실행하세요.

### 곁가지 트랙

새 요구사항이 아닌 버그 수정, 문구 수정, 스타일 조정, 리팩토링은 전체 사양 흐름을 타지 않습니다.

```bash
/ms.fix
/ms.fin
/ms.merglease
```

이미 baseline이 있는 제품에 **새 요구사항**을 추가할 때는 전체 재감사(`/ms.pre-specter`) 대신
`/ms.expand`를 씁니다. 기존 PRD 끝에 `## PRD Amendment N` 절을 추가한 뒤 실행하면, 그 증분만
디컴포즈해 새 Feature를 만들고 기존 Feature는 다시 감사하지 않습니다.

```bash
# docs/prd/PRD.md 끝에 `## PRD Amendment N — YYYY-MM-DD` 절 추가 후
/ms.expand
/ms.specter <새 Feature NNN>
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
| `/ms.verify` | PRD + Codex & Antigravity checklists + Feature Map 대조 검증 | `docs/prd/feature-map.checklist.md` |
| `/ms.checklist` | 다음 Feature의 PRD 반영도 검증 | `docs/prd/checklists/feature-NNN.checklist.md` |
| `/ms.agent-verify` | Codex & Antigravity per-Feature checklist 검증 (foreground 병렬) | `docs/prd/checklists/feature-NNN.codex-verify.md`, `feature-NNN.antigravity-verify.md` |
| `/ms.specify` | 체크된 Feature 섹션 프롬프트를 GEARS spec으로 변환 | `specs/{id}/spec.md` |
| `/ms.clarify` | 요구사항 명확화 | spec.md 업데이트 |
| `/ms.plan` | Reality Verified 구현 계획 수립 | `specs/{id}/plan.md` |
| `/ms.constitution` | 체크된 PRD Feature Map 기반 project-wide baseline 확정 | Constitution Section IX, AGENTS.md |
| `/ms.tasks` | TAG 기반 태스크 생성 | `specs/{id}/tasks.md` |
| `/ms.analyze` | 구현 전 문서 정합성 + Codex & Antigravity 문서 검증 | `specs/{id}/analyze.codex.md`, `specs/{id}/analyze.antigravity.md` |
| `/ms.implement` | 선택된 phase/task/TAG scope 구현 + TAG 삽입 | code, tests, TAG blocks |
| `/ms.review` | 코드 리뷰 + Codex & Antigravity adversarial review + 실행 게이트 | `docs/review/` |
| `/ms.specter` | per-Feature 사이클(checklist→review) 자동 진행, clarify만 인간 개입 | `specs/{id}/`, `docs/review/` |
| `/ms.up-docs` | Living docs 동기화 | `docs/dev_daily.md`, API docs |
| `/ms.fin` | 문서 동기화 + 조건부 CI + commit/push/PR (Antigravity 위임) | commit, PR |
| `/ms.fix` | 비요구사항 변경 경량 트랙 | FIX TAG |
| `/ms.expand` | 기존 baseline 위에 PRD Amendment를 증분 반영 (전체 재감사 없이) | `feature-map.md` 확장, `## Delta Reconciliation N` |
| `/ms.amend` | 구현 후 spec/plan 정정 | Amendment block |
| `/ms.merglease` | PR merge + tag + GitHub Release (Antigravity 위임) | tag, release |

---

## 주요 명령어 플래그 설명

각 명령어 실행 시 세부적인 제어와 동작 모드 지정을 위해 다양한 플래그를 활용할 수 있습니다.

### 1. 에이전트 검증 및 제어 플래그
*   `--skip-codex` / `--skip-agents` (사용 대상: `/ms.analyze`, `/ms.review`):
    *   신속한 처리를 위해 Codex 및 Antigravity 에이전트의 검증/리뷰 단계를 생략하고 로컬 검사만 실행합니다.
*   `--background` (사용 대상: `/ms.analyze`, `/ms.review`):
    *   에이전트 검증/리뷰 프로세스를 백그라운드 태스크로 백킹하여 실행합니다. 결과 보고서 파일이 정상 생성된 뒤 해당 명령을 다시 실행해 승인(PASS/WARN)을 얻어야 게이트가 통과됩니다.
*   `--model MODEL` (사용 대상: `/ms.codex-checklist`, `/ms.agent-verify`, `/ms.analyze`, `/ms.review`):
    *   기본 정의된 모델(`gpt-5.5` 또는 `gemini-3.5-flash`) 외에 특정한 대형 언어 모델을 명시적으로 지정하여 구동합니다.
*   `--effort [low|medium|high]` (사용 대상: `/ms.codex-checklist`, `/ms.agent-verify`, `/ms.analyze`, `/ms.review`):
    *   검증 에이전트의 연산/사고 강도를 지정합니다. 복잡도가 높은 주요 변경점 검증 시 `high`로 구동하여 면밀한 추론을 수행하게 할 수 있습니다.

### 2. 구현 제어 플래그
*   `--to-end` (사용 대상: `/ms.implement`):
    *   현재 남은 모든 미구현/미완료 구현 태스크를 처음부터 끝까지 중단 없이 한 번에 구현하도록 지시합니다. (일체형 대규모 자동 코딩 모드)
*   `--mode [tdd|refactor]` (사용 대상: `/ms.implement`):
    *   구현 전략을 제어합니다. `tdd`는 신규 기능 완성을 위해 테스트-퍼스트 개발 패턴을 엄격히 적용하며, `refactor`는 기존 명세의 동작 보존을 보장하는 구조 개편 모드로 동작합니다.
*   `--task TNNN` / `TAG_ID` (사용 대상: `/ms.implement`):
    *   구현할 태스크의 범위(Scope)를 특정 태스크 식별자(`TNNN`) 또는 추적성 태그 ID(`TAG_ID`)로 좁혀 집중적으로 코딩 작업을 수행하도록 조절합니다.

### 3. 병합 및 릴리즈 플래그

`/ms.merglease`는 기본적으로 완전 자동입니다: 버전은 conventional commits로부터 자동 계산되고
(BREAKING CHANGE/`type!:` → MAJOR, `feat` → MINOR, 그 외 → PATCH — pre-1.0에도 동일 매핑),
머지 전략은 항상 merge commit이라 확인 질문이 없습니다. GitHub CI 실패는 billing/quota/infra로
분류되면(대소문자 무관 `billing`/`spending limit`/`usage limit`/`quota`, `startup_failure`,
또는 job 미시작) 경고를 남기고 머지를 진행하지만, 실제 test/lint/type/build 실패는 머지를
중단시킵니다 — local CI(=이미 `/ms.review`/`/ms.fin`이 통과시킨 게이트)가 authoritative이고
GitHub CI는 advisory이기 때문입니다.

*   `[version]` (사용 대상: `/ms.merglease`):
    *   자동 계산된 semver 대신 명시적 버전을 강제합니다.
*   `--confirm` (사용 대상: `/ms.merglease`):
    *   기본값인 무질문 자동 진행 대신, 버전과 머지를 사람이 확인하는 대화형 모드로 되돌립니다.
*   `--no-release` (사용 대상: `/ms.merglease`):
    *   PR 머지 파이프라인만 정상 실행하고, 신규 버전 태깅 및 GitHub Release 생성을 건너뛰도록 지시합니다.
*   `--cleanup` (사용 대상: `/ms.merglease`):
    *   머지가 최종 성공한 뒤, 로컬 및 원격 저장소 양쪽에서 머지 완료된 feature 브랜치를 깨끗하게 청소 및 삭제합니다.

---

## 게이트 구조

### Global Feature Map 게이트

SPECTER는 Spec-Kit의 native checklist를 단순 호출하지 않습니다. Global 단계는 두 단계입니다.

`/ms.codex-checklist`는 Codex를 백그라운드에서 실행해 PRD만을 원천으로 독립 체크리스트를 만듭니다. 이 단계는 `feature-map.md`를 평가하지 않고, PRD에서 절대 빠지면 안 되는 commitment, acceptance criteria, NFR, data/integration/security promise, explicit exclusion을 추출합니다.

`/ms.verify`는 PRD 원본, Codex checklist, Antigravity global check, Feature Map을 대조해 canonical global gate인 `docs/prd/feature-map.checklist.md`를 생성합니다. 이 단계는 PRD Commitment Index를 기준으로 PRD의 모든 commitment가 정확히 하나의 Feature owner를 갖는지, DAG와 Stub-and-Forward가 성립하는지 검증합니다.

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
- **user-facing exposure**: UI/CLI/API/notification을 함의하는 commitment마다 실제로 그 표면을
  노출하는 in-scope deliverable이 있거나, 그 노출을 소유할 Feature를 명시한 out-of-scope 행이
  있는가 (둘 다 없으면 FAIL — 백엔드만 구현되고 사용자 노출이 없는 gap을 잡기 위함)

`/ms.specify`와 injected `/speckit.specify`는 global audit, per-Feature audit, 또는 Codex & Antigravity per-Feature verification이 없거나 실패했거나, Feature Map SHA가 달라져 stale 상태면 거부합니다.

Feature Status 북키핑(⬜/🚧/✅)은 `feature-map.md`가 아니라 별도 파일 `docs/prd/feature-map.progress.md`에
있습니다. 이 파일을 갱신해도(`/ms.specify`가 매번 recompute하거나 `/ms.merglease`가 `✅ shipped`로 표시해도)
`feature-map.md`의 SHA256은 바뀌지 않으므로 위 게이트들은 stale이 되지 않습니다. `feature-map.md`에는
`> Progress Ledger: docs/prd/feature-map.progress.md` 한 줄짜리 포인터만 남습니다.

### `/ms.analyze`: 문서 정합성 게이트

구현 전에 `spec.md`, `plan.md`, `tasks.md`가 서로 맞는지 확인합니다. 기본 실행에서는 Codex가 foreground로 보조 문서 검증을 수행하며, 큰 문서 세트에서는 `--background`를 사용할 수 있습니다.

검증 항목:

- 모든 FR에 구현 태스크가 있는가
- orphan task가 없는가
- migration/file path drift가 없는가
- Amendment가 기존 FR/task와 충돌하지 않는가
- Constitution/AGENTS 기준이 plan/tasks에 반영되었는가
- Codex & Antigravity가 Feature Map, checklist, spec, plan, tasks 간 drift를 추가로 지적했는가

### `/ms.review`: 코드 게이트

구현 후 PR 전에 실행합니다. Codex & Antigravity가 foreground에서 adversarial 모드로 보조 코드 리뷰를 수행하며, 큰 변경에서는 `--background`를 사용할 수 있습니다.

검증 항목:

- 코드 구조, 명명, 중복, 오류 처리, 보안, 성능
- 테스트 품질
- lint, typecheck, tests, build
- coverage, complexity, security scan
- TAG integrity
- **Done Criteria Execution**: Feature Map의 `### Done criteria`와 spec의 acceptance scenario를
  RUNNABLE/MANUAL로 분류해 RUNNABLE 항목은 실제로 실행(서버 기동, CLI 실행, 플로우 구동)해서
  검증한다. RUNNABLE FAIL은 코드 게이트 실패와 동일하게 `NOT READY`를 만든다. MANUAL 항목은
  "📋 수동 확인 필요" 체크리스트로 보고된다. (문서 게이트만으로는 잡을 수 없던 "코드는 다
  green인데 제품이 실제로는 안 뜨는" 결함 클래스를 막기 위함)
- Codex & Antigravity가 spec/task intent drift, 테스트 누락, 보안/데이터/동시성 리스크를 지적했는가

`--fast`나 `--focus`를 사용해도 critical executable gate는 건너뛰지 않습니다. 검증은 `--skip-agents` (또는 `--skip-codex`)로 명시적으로 생략할 수 있습니다.

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
│   ├── commands/           # /ms.* 워크플로 진입점 (사용자가 명시적으로 호출)
│   ├── agents/             # 전문 subagent (역할 기반 추론/실행)
│   ├── skills/             # 재사용 가능한 검증·규칙·루브릭·체크리스트
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
│   │   ├── feature-map.progress.md
│   │   ├── feature-map.checklist.md
│   │   ├── codex/
│   │   │   └── checklist.md
│   │   └── checklists/
│   │       ├── feature-NNN.checklist.md
│   │       ├── feature-NNN.codex-verify.md
│   │       └── feature-NNN.antigravity-verify.md
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

`/ms.init`은 기본적으로 **검증된 릴리즈(`v0.11.6`)에 핀**됩니다. 업스트림은 pre-1.0라
통합 표면(command→skill, `speckit.x`→`speckit-x`)을 자주 바꾸므로, 핀이 SPECTER 래퍼를
깜짝 파손에서 보호합니다(느슨한 결합). 최신을 추적하려면 `SPEC_KIT_REF`로 덮어씁니다.

```bash
SPEC_KIT_REF=v0.11.6 /ms.init   # 기본값: 검증된 고정 릴리즈 (권장)
SPEC_KIT_REF=main    /ms.init   # 최신 업스트림 (churn 노출 — seam 재검증 필요)
```

> 핀된 v0.11.x는 skill 레이아웃(`.claude/skills/speckit-specify/SKILL.md`)을 생성합니다.
> `/ms.init`의 후보 탐지가 어떤 레이아웃이든 패치하므로, 핀을 올려도 게이트 주입은 안 깨집니다
> (재검증할 부분은 게이트가 아니라 아래 "위임 지점"의 호출명입니다).

---

## Spec Kit 호환성

SPECTER는 GitHub Spec-Kit 위에 올라가는 **command 중심** 워크플로 래퍼입니다.
명령을 skill로 전부 옮기는 마이그레이션이 아니라, 업스트림 변화에 맞춘 **호환성 레이어**로 설계되어 있습니다.

### 의도된 하이브리드 구조

| 위치 | 역할 |
| --- | --- |
| `.claude/commands/` | `/ms.*` — 사용자가 명시적으로 호출하는 워크플로 진입점 |
| `.claude/skills/` | 재사용 가능한 검증기·규칙·루브릭·체크리스트 (capability) |
| `.claude/agents/` | 전문 역할 기반 subagent |

`/ms.*`는 명시적 워크플로 단계이므로 **command로 유지**합니다. 모든 명령을 skill로 옮기지 않습니다.

### 업스트림 레이아웃 자동 감지

최신 Spec-Kit은 Claude 통합을 점차 **native skill** 방향으로 옮기고 있어, 업스트림이
다음 중 어떤 형태로든 파일을 만들 수 있습니다.

- `.claude/commands/speckit.*.md` — 기존 command 기반 레이아웃
- `.claude/skills/speckit-*/SKILL.md` — 신규 native-skill 레이아웃

`/ms.init`은 후보 경로 목록을 탐색해 **존재하는 모든 파일**에 Feature Map 게이트를
주입합니다(command·skill 양쪽 모두 지원). command·skill이 동시에 생성되는 dual 레이아웃에서도
한쪽 진입점이 게이트 없이 남지 않도록 모두 패치합니다. 게이트는 YAML frontmatter 다음에
삽입되어 frontmatter 파싱을 깨지 않으며, `MS_FEATUREMAP_GATE_START` 마커로 중복 주입을 방지합니다.

### 설치 플래그

Spec-Kit은 구형 `--ai` 계열 플래그를 제거하고 `--integration`으로 전환했습니다.
SPECTER는 항상 `--integration claude`를 사용합니다.

```bash
uvx --from "git+https://github.com/github/spec-kit.git@v0.11.6" specify init --here --force --integration claude
```

### 위임 지점 (Spec-Kit 결합 계약 — 단일 출처)

SPECTER는 엔진을 재구현하지 않고 업스트림 skill에 **이름으로 위임**합니다. 업스트림이 호출명을
바꾸면(예: `speckit.plan` → `speckit-plan`) 아래 위임만 깨지므로, **여기가 결합의 단일 출처**입니다.
핀(`SPEC_KIT_REF`)을 올릴 땐 이 표의 호출명이 그대로인지 먼저 확인하세요.

| SPECTER 래퍼 | 위임 대상 (핀 v0.11.6 기준) |
| --- | --- |
| `/ms.specify` | `/speckit-specify` (+ `/ms.init`이 게이트 주입) |
| `/ms.clarify` | `/speckit-clarify` |
| `/ms.plan` | `/speckit-plan` |
| `/ms.tasks` | `/speckit-tasks` |
| `/ms.analyze` | `/speckit-analyze` (foundation only) |
| `/ms.implement` | `/speckit-implement` |

> `/ms.checklist`는 의도적으로 `/speckit-checklist`에 위임하지 **않습니다**(PRD 근거 기반 자체 검증).
> 호출명은 업스트림 `SKILL.md`의 `name:` 필드가 결정합니다(현재 하이픈 형식).

### 직접 호출 우회 차단 (불변식)

업스트림이 command든 skill이든, `/ms.init`이 주입한 게이트 덕분에 직접 `/speckit-specify`
호출은 SPECTER의 Feature Map / checklist / Constitution Section IX 게이트를 우회할 수 없습니다.

### GEARS 스펙템플릿 해석 (라이브 검증됨)

최신 Spec-Kit(v0.11.x)은 spec-template을 **preset/template resolution stack**
(`specify preset resolve spec-template`)으로 해석합니다. 라이브 `specify init`으로 확인한
결과, 기본(no-`--preset`) init에서 이 스택의 **`core` 레이어가 바로
`.specify/templates/spec-template.md`** 입니다 — `/ms.init` Step 2.3이 덮어쓰는 그 파일이라
**GEARS가 신규 `spec.md`에 그대로 반영됩니다.** 단, `--preset`으로 자체 spec-template을 얹는
경우엔 preset 레이어가 `core`를 덮을 수 있으나, `/ms.init`은 `--preset`을 쓰지 않습니다.

### SPECTER 정체성 불변식 (양보 불가)

래퍼로서 spec-kit 변화에 *이름·경로·버전*은 맞추되, 아래는 **절대 양보하지 않습니다**. 이번
세션의 모든 적응(command→skill 탐지, `speckit.x`→`speckit-x`, 버전 핀, 스크립트 경로 교정)은
전부 이 불변식을 **유지하거나 강화**했고, 어느 것도 포기하지 않았습니다.

1. **Feature Map 게이트 / 직접 호출 우회 차단** — `/ms.specify`는 freeform 거부, 직접
   `/speckit-specify`는 게이트 우회 불가. (skill·dual 레이아웃까지 주입 확장 → 강화됨)
2. **GEARS** 요구사항 언어가 신규 spec에 실제로 도달. (core 레이어 해석으로 유지 확인)
3. **TAG 추적성** `@SPEC→@TEST→@CODE→@DOC` — SPECTER 자체 단계(`/ms.tasks`,`/ms.implement`)에서 주입.
4. **Constitution Section IX** 베이스라인 게이트.
5. **Codex 독립 검증** 게이트.
6. **게이트는 SPECTER가 소유** — spec-kit CLI/스크립트 플래그에 위임하지 않음(예: `/ms.review`의
   spec.md/plan.md 검증은 SPECTER가 직접 수행).

### 결별 기준 (Divorce tripwires)

다음 중 하나라도 **얇은 호환 shim(이름/경로/버전/플래그 교정)으로 해결되지 않으면**, 래퍼
관계는 더 이상 정체성을 지키지 못하므로 결별(엔진 fork, `specify` 런타임 의존 제거)을 선언합니다.

| Tripwire | 무엇이 깨지나 | 현재 상태(v0.11.6) |
| --- | --- | --- |
| `specify preset resolve spec-template`이 `core`(=`.specify/templates/spec-template.md`)를 더 이상 가리키지 않음 | GEARS가 신규 spec에 도달 못 함 | ✅ 안전 (core) |
| upstream이 패치 가능한 `speckit-specify` 파일을 더 이상 생성/유지하지 않음(잠금·서명·동적 생성) | Feature Map 게이트 주입 불가 → 우회 차단 붕괴 | ✅ 안전 (주입됨) |
| `/speckit-specify` 자동호출을 막을 수 없고 게이트 밖에서 실행됨 | 명시적·순차 게이트 규율 붕괴 | ✅ 안전 (게이트가 스킬 내부에 동행) |
| `/speckit-*` 엔진이 SPECTER 주입(TAG/Constitution/TRUST)과 하드 충돌(예: TAG 블록 제거) | 감싸기 합성 불가 | ✅ 안전 (합성됨) |
| SPECTER 의존 스크립트(예: `check-prerequisites.sh`)가 shim 불가하게 반복적으로 깨짐 | 워크플로우 단계 동작 불가 | ✅ 안전 (경로/플래그 교정으로 해결) |

> 원칙: **이름·경로·버전·플래그 = 맞춰준다. 게이트·GEARS·TAG·Constitution·Codex = 절대 안 굽힌다.**
> 후자를 지키기 위해 전자를 포기해야 하는 순간이 결별 시점이다.

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
- Google Antigravity CLI (`agy`) 및 인증 완료 상태
- Antigravity plugin for Claude Code (`sakibsadmanshajib/antigravity-plugin`)
- Codex plugin for Claude Code (`openai/codex-plugin-cc`)
- Codex CLI 인증 및 사용 가능 상태
- 프로젝트별 테스트/린트/타입체크 도구

선택 도구:

- Context7 MCP: 최신 라이브러리 문서 조회
- GitHub CLI: `/ms.fin`, `/ms.merglease` 흐름에서 PR/release 자동화 (Antigravity 서브세션에서 구동)

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

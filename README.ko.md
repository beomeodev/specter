<div align="center">
    <h1>👻 SPECTER</h1>
    <h3><em>AI와 함께하는 고품질 소프트웨어 개발 워크플로우</em></h3>
    <p>
        <a href="./README.md">English</a> | <strong>한국어</strong>
    </p>
</div>

<p align="center">
    <strong>Specification-Progressive Enforcement & Constitution-based Traceability, Evolutionary Review</strong>
</p>

<p align="center">
    사양 기반 점진적 검증 · 헌법 기반 추적성 · 진화적 리뷰
</p>

<p align="center">
    <a href="./CHANGELOG.md"><img src="https://img.shields.io/badge/release-v2.3.1-2ea44f" alt="release"></a>
    <a href="https://github.com/github/spec-kit"><img src="https://img.shields.io/badge/built%20on-Spec--Kit%20v0.12.5-cc785c" alt="built on Spec-Kit"></a>
    <a href="#도구-요구사항"><img src="https://img.shields.io/badge/Python-3.14%2B%20·%20uv-3776ab" alt="Python 3.14+ · uv"></a>
    <a href="https://claude.com/claude-code"><img src="https://img.shields.io/badge/Claude%20Code-workflow%20overlay-d97757" alt="Claude Code overlay"></a>
    <a href="#게이트"><img src="https://img.shields.io/badge/gates-lint%20·%20type%20·%20test-5a0fc8" alt="gates"></a>
    <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License">
</p>

> [!NOTE]
> 이 README는 최신 태그 이후의 미릴리즈 워크플로우 변경을 포함할 수 있는 현재
> `master` 브랜치를 설명합니다. `v2.3.1`의 정확한 동작은 해당 태그와
> [CHANGELOG](./CHANGELOG.md)를 확인하세요.

---

> [!IMPORTANT]
> **개인용 템플릿이며, 범용 제품이 아닙니다.**
> 이 레포지토리는 편리한 유지보수(작성자 본인 프로젝트 간 동기화·참조)를 위해
> 공개해 둔 것일 뿐, [Spec-Kit](https://github.com/github/spec-kit)을 개인적인
> 사용에 맞춰 크게 변형해 만든 것입니다. 경로·에이전트(Codex/Antigravity)·게이트가
> 작성자 환경에 맞춰져 있어 **타인이 그대로 사용하기에는 적절하지 않으며**, 지원이나
> 안정성을 보장하지 않습니다. 그대로 쓰는 스타터가 아니라 아이디어 참고용으로 봐주세요.

---

## SPECTER란?

SPECTER는 AI 보조 제품 개발을 위한 요구사항 거버넌스·검증 오버레이입니다.

PRD에서 Feature 경계, GEARS 사양, 구현 계획, 테스트, 코드, 실행 증거로 작업이 이동하는 동안 제품 의도를 보존합니다. GitHub [Spec-Kit](https://github.com/github/spec-kit)을 생성 엔진으로 사용하되, 게이트·추적성 규칙·독립 검증 프로토콜은 SPECTER가 소유합니다.

- **GEARS 요구사항** — 모호한 PRD를 검증 가능한 요구사항 문장으로 변환
- **Feature Map 게이트** — PRD의 모든 약속(commitment)에 정확히 하나의 Feature 소유자를 강제
- **Constitution** — 프로젝트 기준을 1회 추출해 단일 위치에 고정, 매 단계 재주입
- **TAG 탐색 인덱스** — `@SPEC → @TEST → @CODE`로 요구사항 ID에서 주요 테스트·구현 파일을 찾는 가벼운 grep 기반 인덱스. TAG 연결은 기계적으로 검사하지만, TAG가 테스트의 의미적 요구사항 커버리지를 증명하지는 않습니다. 실행 테스트와 리뷰 증거가 권위 있는 근거입니다.
- **독립 의미 검증** — Codex와 Antigravity가 의미 검증 스테이션에서 산출물을 독립적으로 리뷰합니다. 결정론적 스크립트가 구조를 검사하고 SHA에 묶인 판정을 기계적으로 집계합니다.
- **Graphify 탐색 가속기** — 구조 질문에 파일·라인 포인터를 제공하는 로컬 tree-sitter 그래프. 그래프 결과는 탐색 힌트일 뿐 권위 있는 증거가 아니며, 에이전트는 원본 파일로 검증합니다. Graphify가 없으면 기록된 경고와 함께 `rg`/`find`로 저하되며 Feature를 막지 않습니다.

세 가지 문제를 겨냥합니다.

**AI는 규칙을 잊어버립니다.** "파일은 작게 나눠 작성해" → 몇 파일 뒤부터 다시 거대한 파일.
Constitution과 `AGENTS.md`가 규칙을 반복 주입하고, 결정론적 게이트(pre-commit·훅·CI)가
프롬프트가 놓친 것을 기계적으로 잡습니다.

**요구사항이 모호하면 구현도 흔들립니다.** "로그인 기능 만들어줘"에는 인증 방식도 실패
처리도 없습니다. GEARS는 이렇게 씁니다:

```text
When a user submits valid credentials, the auth service shall issue a session token.
[Error Handling] When credentials are invalid, the auth service shall return a generic authentication error.
```

**코드가 왜 존재하는지 추적하기 어렵습니다.** TAG 앵커 체인이 요구사항→테스트→코드를
연결합니다 — 산출물마다 grep 가능한 주석 한 줄:

```text
specs/001-auth/tasks.md    **TAG**: @SPEC:AUTH-001
tests/auth.test.ts         // @TEST:AUTH-001
src/auth/service.ts        // @CODE:AUTH-001
```

현재 릴리즈는 `v2.3.1`입니다 — 변경 이력은 [CHANGELOG.md](./CHANGELOG.md)를 보세요.

### Feature 경계

SPECTER Feature는 독립적으로 지정·구현·검증·리뷰·머지할 수 있는 가장 작은 dependency-aware 슬라이스입니다.

Feature는 독립적으로 사용자에게 출시할 수 있는 단위가 아니라 아키텍처 단위일 수 있습니다. End-to-end 사용자 가치는 Phase 경계에서 보장되며, Phase의 마지막 Feature가 해당 Phase의 E2E 시나리오를 소유합니다.

가능하면 vertical slice를 우선하되, foundation이나 cross-layer 경계를 순차적으로 처리해야 할 때는 dependency-aware architectural slice를 사용합니다.

### 권위 계층 (Authority Model)

SPECTER는 모든 산출물을 서로 경쟁하는 단일 진실 공급원으로 취급하지 않습니다. 각 산출물이 서로 다른 종류의 결정을 소유합니다.

| 산출물 | 권위 |
| --- | --- |
| PRD | 제품 의도와 지속되는 약속 |
| Feature Map | 약속의 소유권, Feature 경계, 의존성 순서 |
| `spec.md` | 한 Feature의 실행 가능한 행동 계약 |
| `plan.md` | 검증된 구현 결정과 아키텍처 |
| `tasks.md` | 실행 분해와 추적성 할당 |
| 테스트와 실행 증거 | 관찰된 구현 동작 |
| `implementation-notes.md` | 구현 중 발견된 범위 내 편차 |

하위 산출물은 상위 문서에 문자 그대로 없더라도 자기 도메인의 필요한
세부사항을 추가할 수 있습니다. `refinement`와 저장소 근거가 있는
`reality-correction`은 근거로 해소할 수 있습니다. 새 actor/journey, integration,
보존 데이터 범주, permission boundary, 유료 capability, 명시적
exclusion/cost/policy 충돌은 `boundary-change`/`conflict`로 분류합니다.
`/ms.clarify`에서는 상위 패치 제안과 함께 사용자에게 묻고, 그 유일한 사람
경계 밖에서는 범위를 조용히 넓히지 않고 FAIL합니다. 입력 hash는 무엇을 검토했는지 증명할 뿐 제품 권위를 부여하거나 추상 문서를 잠그지 않습니다.

### GEARS와 인수 시나리오

GEARS는 실행 가능한 행동 요구사항에 사용합니다.

`[Where <static>] [While <runtime>] [When <trigger>] the <subject> shall <behavior>.`

Given-When-Then은 인수 시나리오 형식으로 유지됩니다.

- `Where + While` → `Given`
- `When` → `When`
- `shall` → `Then`

SPECTER는 schema, scope 선언, 보존 제약, implementation note에 GEARS를 강제하지 않습니다. 이런 산출물은 평문이되 검증 가능한 문장을 사용할 수 있습니다.

현재 GEARS 준수는 템플릿, 워크플로우 규칙, 구조 검사, 의미 리뷰어를 통해 강제됩니다. 완전한 형식 언어 파서라고 주장하지 않습니다.

### 상태 없는 간결한 검증

의미 검증 station은 fresh 독립 reviewer 두 명을 사용합니다. 각 reviewer는 현재
입력 SHA256에 결속된 고정 경로 report를 쓰고, `specter-gate.sh reduce`가 report마다
정확히 하나의 PASS/WARN/FAIL을 검증해 최악 결과를 반환합니다. reviewer 한 명이
없고 남은 결과가 비-FAIL이면 WARN, 둘 다 없으면 FAIL입니다. 입력이 실제로 바뀐
경우에만 한 번 재검증합니다.

위험 profile, signal 표, receipt, round state, acknowledgment gate는 없습니다.
최종 review는 migration, destructive operation, authorization, secrets, public
contract, gate/hook 변경에 해당하는 실행 증거를 항상 적용합니다.
[`refinement-first.md`](./docs/design/refinement-first.md)를 참고하세요.

---

## 빠른 시작

```bash
/ms.init
/ms.pre-specter @docs/prd/PRD.md
/ms.specter 001
```

`/ms.pre-specter`는 제품 전체 Feature Map을 준비하고 검증합니다. `/ms.specter 001`은 Feature 001을 준비 상태 확인부터 코드 리뷰까지 실행합니다. `/ms.clarify`는 사이클의 유일한 필수 사람 정지입니다. 근거로 확정되는 항목을 먼저 해소한 뒤, 그 내역의 검토와 남은 제품 의도 결정을 위해 반드시 사용자에게 제어권을 넘깁니다.

디버깅이나 수동 제어가 필요할 때는 각 하위 `/ms.*` 단계를 개별 실행할 수도 있습니다.

<details>
<summary>전체 커맨드 순서</summary>

```bash
/ms.init
/ms.featuremap @docs/prd/PRD.md
/ms.featuremap-checklist @docs/prd/PRD.md
/ms.pre-verify
/ms.constitution
/ms.checklist
/ms.verify
/ms.specify
/ms.clarify
/ms.plan
/ms.tasks
/ms.analyze
/ms.implement
/ms.review
```

</details>

---

## 워크플로우

```text
────────────────────────────────────────────────────────────────────
 📄  준비 (Setup)
────────────────────────────────────────────────────────────────────
     0. /ms.init            Spec-Kit 설치 + Constitution + 코드 그래프
     1. /ms.prd             PRD 공동 작성 — unknowns 발굴 인터뷰 (사이클 밖)
                            docs/prd/PRD.md (또는 복수 PRD)
                            │
                            ▼
════════════════════════════════════════════════════════════════════
 🗺️  Pre-Feature 사이클   ·  1회  ·  묶음 실행: /ms.pre-specter
════════════════════════════════════════════════════════════════════
     2. /ms.featuremap       PRD → Feature DAG 분해
     3. /ms.featuremap-checklist  PRD-only baseline 체크리스트 (격리 서브에이전트)
     4. /ms.pre-verify           L1 구조검사 + Codex & Antigravity 이중 감사 → 전역 게이트
     5. /ms.constitution     프로젝트 기준 (Constitution §IX) 확정
                            │
                            ▼   Feature마다 DAG 순서로 반복
════════════════════════════════════════════════════════════════════
 🛰️  Per-Feature 사이클   ·  N회  ·  묶음 실행: /ms.specter
════════════════════════════════════════════════════════════════════
  ┌─▶  6. /ms.checklist      이번 Feature 검증 (PRD 반영도)
  │    7. /ms.verify         현재 hash Codex + Antigravity 검증
  │    8. /ms.specify        사양 작성 (Feature 섹션 입력)
  │    9. /ms.clarify        🔴 필수 사람 정지 (근거 우선 Q&A)
  │   10. /ms.plan           구현 계획 + reality 검증
  │   11. /ms.tasks          TAG 기반 태스크 생성
  │   12. /ms.analyze        spec ↔ plan ↔ tasks 정합성
  │   13. /ms.implement      TDD 구현 + TAG 삽입
  │   14. /ms.review         자동 고위험 증거 + 실행 게이트
  └──── 다음 Feature가 남으면 6번으로 되돌아가 반복
                            │   모든 Feature 완료
                            ▼
────────────────────────────────────────────────────────────────────
 🚀  발행 / 릴리즈 (Publish / Release)
────────────────────────────────────────────────────────────────────
    15. /ms.fin              high-stakes diff 자동 증거 게이트 → commit · push · PR
    16. /ms.merglease        PR 머지 → tag → GitHub Release
```

정상적인 Per-Feature 사이클의 필수 사람 정지는 `/ms.clarify` 하나뿐입니다.
여기서는 근거로 확정되는 답을 먼저 정리한 뒤 반드시 사용자에게 제어권을
넘깁니다. migration, destructive, irreversible, reviewer availability,
round limit, gate-policy 판단은 계속 실행 가능한 증거 게이트로 처리하며 별도
승인 확인 정지를 만들지 않습니다.

**권장 형태는 bare 호출**입니다 — PRD와 Feature Map은 관례 경로(`docs/prd/*.md`,
`docs/prd/feature-map.md`)에서 자동으로 찾습니다. PRD 전체를 `@`로 첨부하면 conductor가
재시작될 때마다 그 내용이 컨텍스트에 통째로 재주입되므로(실측 사례: 프로젝트 하나에서
약 105만 토큰), `@` 첨부는 관례 경로 밖의 파일에만 쓰세요.

### 곁가지 트랙

메인 사이클 밖에서 변경의 성격이 결정하는 트랙들입니다.

| 상황 | 트랙 | 요점 |
| --- | --- | --- |
| PRD가 아직 없거나 막연함 | `/ms.prd` | 블라인드스팟 패스 → 생존성 게이트 → 갭을 하나씩 해소하는 인터뷰. 게이트 없음, 산출물은 파이프라인이 바로 소비하는 PRD |
| 새 요구사항 없음 (버그·문구·스타일) | `/ms.fix` | TDD·TAG·게이트는 유지, spec/clarify/plan/tasks 의례만 생략 |
| 기존 baseline에 새 요구사항 증분 또는 구현 중 발견된 설계 변경 | `/ms.expand` | PRD 끝에 `## PRD Amendment N`을 append해 그 증분만 디컴포즈. 기존 Feature는 유지하고 전체 재감사는 하지 않으며 freeform 입력은 거부합니다. 범위 내 구현 편차는 `specs/<id>/implementation-notes.md`에 남기고, 요구사항 변경은 `/ms.expand`로 되돌립니다. |
| Feature는 전부 초록인데 제품 전체가 궁금할 때 | `/ms.audit` | 노출·콜드스타트·위협모델·perf/a11y·게이트 가치·블라인드스팟 6개 모듈. 자문형 — 아무것도 막지 않고 발견은 `/ms.fix`·`/ms.expand`·todo로 라우팅 |

---

## 게이트

산출물 작성은 호스트가 맡고, 의미 판정은 fresh 독립 reviewer 두 명이 맡습니다.
기계 gate는 현재 hash, 고정 report 경로, 정확한 verdict 필드, worst-of만 검사하며
워크플로우 상태를 저장하지 않습니다.

| 게이트 | 시점 | 검증 내용 |
| --- | --- | --- |
| 전역 Feature Map (`/ms.pre-verify`) | Pre-Feature | 전체 PRD coverage, ownership, DAG, exclusion, E2E journey |
| Per-Feature (`/ms.checklist` + `/ms.verify`) | Feature 시작 | scope, dependency, Done criteria, 경계 밖 추가 |
| 문서 (`/ms.analyze`) | 구현 직전 | spec ↔ plan ↔ tasks와 저장소 현실 |
| 코드 (`/ms.review`) | 구현 직후 | lint/type/test/build 1회, 실제 entrypoint Done Criteria, E2E와 안전 검사 |

직접 `/speckit-specify` 우회는 PreToolUse hook이 거부합니다. bounded Stop hook은
코드 변경 후 fresh 실행 증거를 요구하되 정직한 FAIL 증거도 허용합니다.
pre-commit/CI는 Feature Map hash와 TAG chain을 백스톱합니다. `/ms.clarify`만
사이클의 필수 사람 정지입니다.

---

## 핵심 커맨드

| 명령어 | 역할 |
| --- | --- |
| `/ms.init` | Spec-Kit 설치 + SPECTER 오버레이·훅·백스톱·간결 gate·Graphify 주입 |
| `/ms.prd` | PRD 공동 작성 인터뷰 (사이클 밖) |
| `/ms.pre-specter` | Pre-Feature 사이클(featuremap→constitution) 묶음 실행 |
| `/ms.featuremap` | PRD를 Feature DAG로 분해, Feature별 프롬프트 작성 |
| `/ms.featuremap-checklist` | fresh PRD-only 독립 baseline 체크리스트 |
| `/ms.pre-verify` | PRD + 양 에이전트 체크리스트 + Feature Map 대조 → 전역 게이트 |
| `/ms.constitution` | Constitution Section IX 프로젝트 baseline 확정 (보통 1회) |
| `/ms.specter` | Per-Feature 사이클(checklist→review) 묶음 실행, clarify에서 한 번 사람 정지하고 나머지는 자동 증거 판정 |
| `/ms.checklist` / `/ms.verify` | 이번 Feature의 PRD 반영도 검증 (호스트 + Codex/Antigravity) |
| `/ms.specify` / `/ms.clarify` / `/ms.plan` / `/ms.tasks` | GEARS spec → 명확화 → 계획 → TAG 태스크 |
| `/ms.analyze` | 구현 전 문서 정합성 + 양 에이전트 문서 검증 |
| `/ms.implement` | TDD 구현 + TAG 삽입 (`--to-end`, `--mode tdd\|refactor`, `--task TNNN`, `--pbt` GEARS 기반 속성 테스트) |
| `/ms.review` | 코드 리뷰 + adversarial 에이전트 리뷰 + 실행 게이트 |
| `/ms.fix` / `/ms.expand` / `/ms.audit` | 곁가지 트랙 (위 표 참조) |
| `/ms.fin` | 문서 동기화 → review freshness 확인 → commit·push·PR |
| `/ms.merglease` | PR 머지 → semver 자동 계산 → tag → GitHub Release |
| `/ms.up-docs` | Living docs 동기화 |
| `/ms.sync` | 워크플로우 파일을 등록된 프로젝트 레포들에 브로드캐스트 (3-way 충돌 보호) |

검증 커맨드는 현재 입력 hash, 고정 report 경로, verdict 유효성, worst-of를
기계적으로 읽습니다. profile이나 수동 override는 없습니다. 나머지 커맨드별
제어는 [커맨드 파일](./.claude/commands/)에 문서화되어 있습니다.

### Constitution 두 단계

`/ms.init`이 만드는 기본 Constitution(test-first, simplicity, GEARS, TRUST, TAG)은
`/ms.specify` 이전부터 활성입니다. `/ms.constitution`은 이를 새로 만드는 게 아니라,
검증된 Feature Map에서 **project-wide baseline(Section IX)** 을 추출해 확정하는
명령입니다 — 그래서 Feature 사이클 안이 아니라 `/ms.pre-verify` 직후에 1회 실행합니다.

```text
/ms.init             → 기본 Constitution 활성화
/ms.featuremap-checklist  → PRD-only 독립 체크리스트
/ms.pre-verify           → 전역 게이트
/ms.constitution     → Section IX baseline 확정 (보통 1회)
```

---

## 설치

```bash
npx degit beomeodev/specter my-new-project
cd my-new-project
# Claude Code에서:
/ms.init
```

`/ms.init`은 검증된 Spec-Kit 릴리즈(`v0.12.5`)에 핀됩니다. 업스트림은 pre-1.0이라 통합
표면을 자주 바꾸므로, 핀이 래퍼를 깜짝 파손에서 보호합니다. 최신 추적은
`SPEC_KIT_REF=main /ms.init` — 단, 아래 [Spec-Kit 호환성](#spec-kit-호환성)의 위임 지점
호출명 재검증이 필요합니다.

### 프로젝트 구조

```text
specter/
├── .claude/
│   ├── commands/           # /ms.* 워크플로우 진입점
│   ├── agents/             # 전문 서브에이전트
│   ├── skills/             # 재사용 검증기·규칙·루브릭
│   └── settings.json       # 권한 베이스라인
├── .specify/               # Spec-Kit 상태 (constitution, scripts — /ms.init이 생성)
├── scripts/specter/        # 결정론적 게이트·sync 스크립트 (agent-neutral)
├── docs/
│   ├── prd/                # PRD, feature-map, 체크리스트·검증 리포트
│   ├── review/             # 리뷰 산출물
│   └── templates/          # Constitution·spec 템플릿, 게이트 스크립트
├── specs/NNN-{feature}/    # spec.md · plan.md · tasks.md
├── AGENTS.md               # 에이전트 중립 규약 (CLAUDE.md는 심링크)
└── README.md
```

---

## Spec-Kit 호환성

SPECTER는 엔진을 재구현하지 않고 업스트림 스킬에 **이름으로 위임**하는 호환성
레이어입니다. `/ms.*`는 명시적 워크플로우 진입점이므로 command로 유지하고, 재사용
가능한 검증 로직은 skill로 둡니다. `/ms.init`은 업스트림이 command 레이아웃
(`.claude/commands/speckit.*.md`)이든 native-skill 레이아웃
(`.claude/skills/speckit-*/SKILL.md`)이든 존재하는 모든 후보에 Feature Map 게이트를
주입합니다.

### 위임 지점 (Spec-Kit 결합 계약 — 단일 출처)

업스트림이 호출명을 바꾸면 아래 위임만 깨집니다. 핀(`SPEC_KIT_REF`)을 올릴 땐 이 표의
호출명이 그대로인지 먼저 확인하세요.

| SPECTER 래퍼 | 위임 대상 (핀 v0.12.5 기준) |
| --- | --- |
| `/ms.specify` | `/speckit-specify` (+ `/ms.init`이 게이트 주입) |
| `/ms.clarify` | `/speckit-clarify` |
| `/ms.plan` | `/speckit-plan` |
| `/ms.tasks` | `/speckit-tasks` |
| `/ms.analyze` | `/speckit-analyze` (foundation only) |
| `/ms.implement` | `/speckit-implement` |

> `/ms.checklist`는 의도적으로 `/speckit-checklist`에 위임하지 **않습니다**(PRD 근거 기반 자체 검증).
>
> v0.12.x는 이 계약 밖의 업스트림 스킬(`speckit-converge`, `speckit-taskstoissues`,
> `speckit-constitution`, `speckit-checklist`)도 렌더링하지만 SPECTER는 래핑하지 않습니다 —
> `/ms.constitution`·`/ms.checklist`는 동명의 업스트림 스킬과 무관한 독립 구현입니다.
>
> GEARS 템플릿 주입은 v0.12.x 해석 스택을 사용합니다: `/ms.init`이 GEARS spec-template를
> `.specify/templates/overrides/`(우선순위 1 — 어떤 preset/extension도 가릴 수 없음)와
> core 경로(pre-0.12 폴백)에 함께 설치합니다.

### 정체성 불변식 (양보 불가)

이름·경로·버전·플래그는 업스트림에 맞추되, 다음은 절대 굽히지 않습니다: Feature Map
게이트와 직접 호출 우회 차단(프롬프트 마커 + PreToolUse 훅 이중), GEARS가 신규 spec에
실제 도달, TAG 추적성, Constitution Section IX, Codex·Antigravity 이중 독립 검증, 게이트는 SPECTER가
소유(Spec-Kit CLI 플래그에 위임하지 않음), 가용성 저하 ≠ 게이트 완화.

### 결별 기준 (Divorce tripwires)

다음 중 하나라도 얇은 호환 shim(이름/경로/버전/플래그 교정)으로 해결되지 않으면 결별
(엔진 fork)을 선언합니다.

| Tripwire | 무엇이 깨지나 |
| --- | --- |
| spec-template 해석이 `core`(=`.specify/templates/spec-template.md`)를 벗어남 | GEARS가 신규 spec에 도달 못 함 |
| 패치 가능한 `speckit-specify` 파일이 사라짐 (잠금·서명·동적 생성) | 게이트 주입 불가 → 우회 차단 붕괴 |
| `/speckit-specify` 자동호출을 막을 수 없게 됨 | 순차 게이트 규율 붕괴 |
| 업스트림 엔진이 SPECTER 주입(TAG/Constitution)과 하드 충돌 | 감싸기 합성 불가 |
| SPECTER 의존 스크립트가 shim 불가하게 반복 파손 | 워크플로우 단계 동작 불가 |

> 원칙: **이름·경로·버전·플래그 = 맞춰준다. 게이트·GEARS·TAG·Constitution·Codex = 절대 안 굽힌다.**

---

## 로드맵: 멀티 에이전트 & 공개 배포

현재 레포지토리는 개인적이고 환경 의존적인 템플릿으로 유지됩니다. 아래 로드맵은 향후 가능한 배포 모델을 설명할 뿐, 현재 릴리즈의 지원 범위나 호환성 계약이 아닙니다.

SPECTER는 현재 Claude Code 전용이지만, **Codex CLI에서도 동등하게 구동되는 워크플로우**로
전환할 계획입니다. 방향은 Spec-Kit의 통합 아키텍처와 동일합니다 — `.claude/commands/`를
단일 정본으로 유지하고, 렌더러가 에이전트별 네이티브 형식(Codex는 `.agents/skills/`)을
생성합니다. 이후 Gemini CLI 등 다른 에이전트 추가는 통합 정의 하나를 더하는 일이 됩니다.

- **드라이버 인지 교차검증**: 검증 스테이션의 외부 리뷰어가 드라이버에 따라 자동 전환
  (Claude 드라이버 → Codex+agy 리뷰, Codex 드라이버 → Claude+agy 리뷰). 하드코딩 없이
  단일 디스패치 표로 관리해 드리프트를 차단합니다.
- **uv 패키지 배포**: Spec-Kit처럼 `uvx specter init --integration claude|codex` 한 줄로
  설치하는 배포 형태를 목표로 합니다.
- **전면 영어화 + 설치 시 언어 선택**: 템플릿 언어는 영어로 통일하고, 보고·질문 언어는
  설치 시점에 사용자가 선택합니다.
- **배포 전 클린업**: 개인 계정·로컬 경로 하드코딩 제거 등 다중 사용자 배포를 위한
  정리가 선행됩니다.

클린업 → 렌더러 → 드라이버 인지 프로토콜 → 패키징 순의 단계별 실행 계획이 수립되어 있으며,
훅 기반 게이트 강제력이 Codex에서는 pre-commit/CI 백스톱으로 강등된다는 점(유일한 구조적
격차)을 포함해 게이트 불변식은 그대로 유지됩니다.

---

## 언제 사용하나요?

**적합**: AI와 기능을 지속 개발하는 프로젝트 · PRD-사양-구현-리뷰 추적성이 중요한 제품 ·
여러 Feature를 순차 배포하는 MVP · "이 코드가 왜 있나"를 빨리 답해야 하는 장기 코드베이스.

**부적합**: 1회성 스크립트 · 100 LOC 안팎의 실험 · 추적성 유지 비용이 이득보다 큰 초소형
프로젝트.

---

## 도구 요구사항

### 하드 런타임 요구사항

- Git
- ripgrep
- uv/uvx
- Claude Code
- 프로젝트별 test/lint/type/build 도구

### 검증 에이전트

- Codex CLI (인증 완료) + Codex plugin for Claude Code
- Google Antigravity CLI `agy` (인증 완료) + Antigravity plugin

리뷰어 하나를 사용할 수 없으면 남은 FAIL은 그대로 FAIL이고, 그 외 결과는 WARN으로 제한됩니다. 독립 리뷰어가 하나도 남지 않으면 호스트 단독 판정으로 대체하지 않고 FAIL합니다.

### 탐색 가속기

- Graphify (`graphifyy`, 버전 핀; `/ms.init`이 `uv tool install --python 3.12`로 설치)

런타임에 Graphify가 없어도 차단하지 않으며 `rg`/`find`로 대체합니다.

선택: GitHub CLI (`/ms.fin`·`/ms.merglease`의 PR/release 자동화)

## 검증 상태

워크플로우에는 현재 입력 hash, 정확한 verdict parsing, reviewer unavailable,
worst-of 축약, hook, sync, publish/release helper를 검증하는 자동화 fixture와
contract test가 있습니다. 간결한 gate 계약은
`tests/specter/test_specter_gate.py`가 다루며 consuming project의 end-to-end가
최종 통합 검증입니다.

현재 확인된 불변식과 알려진 공백은 [docs/SYSTEM_MAP.md](./docs/SYSTEM_MAP.md)를 참고하세요.

---

## 상세 문서

- [AGENTS.md](./AGENTS.md) — AI coding rules ([CLAUDE.md](./CLAUDE.md)는 심링크)
- [CHANGELOG.md](./CHANGELOG.md) — 릴리즈 이력
- [docs/SYSTEM_MAP.md](./docs/SYSTEM_MAP.md) — 큐레이션된 프로즈 스냅샷(불변식·리스크·검증); 소비 프로젝트에서 Graphify 포인터를 활용할 수 있지만 원본 파일로 검증해야 합니다 (`/ms.init` Step 2.9)
- [.claude/commands/](./.claude/commands/) · [.claude/agents/](./.claude/agents/) · [.claude/skills/](./.claude/skills/)

---

## Credits

[Spec-Kit](https://github.com/github/spec-kit) · [Claude Code](https://claude.com/claude-code) · [ripgrep](https://github.com/BurntSushi/ripgrep)

MIT License

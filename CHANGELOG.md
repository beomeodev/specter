# Changelog

All notable changes to this repository are documented in this file.

## [2.3.0] - 2026-07-03

### Added
- **`/ms.pre-specter` 1회성 PRD-setup 조정자**: `featuremap → codex-checklist → verify →
  constitution`을 하나의 pre-Feature 사이클로 자동 진행. 각 단계 판정/산출물을 읽어 PASS/WARN은
  진행, FAIL은 정지하며 게이트를 약화·우회하지 않음. 첫 Feature를 `/ms.specter`로 넘김.
- **`/ms.expand` 증분 PRD 트랙**: 기존 PRD 끝에 붙인 `## PRD Amendment N` 절만 디컴포즈해 새
  Feature를 추가하고, 이미 검증된 Feature는 재감사하지 않음. 기존 텍스트를 편집하는 diff나 기존
  Feature 섹션·Commitment Index 행 변경은 거부(append-only). `/ms.fix`와 `/ms.pre-specter` 사이 트랙.
- **`/ms.review` Done Criteria Execution 런타임 게이트**: Feature Map done criteria와 spec
  acceptance scenario를 RUNNABLE/MANUAL로 분류해 RUNNABLE 항목을 실제로 실행(서버 기동·CLI·플로우
  구동)해 검증. RUNNABLE FAIL은 `NOT READY`. "코드는 green인데 제품이 안 뜨는" 결함 클래스 차단.
- **PRD 저작 스킬 `ms-foundation-prd`**: PRD 부재 시 한 질문씩 인터뷰하며 PRD 공동 작성. 산출
  형식이 `/ms.featuremap` 추출 대상(commitment·GEARS 수용 기준)과 `/ms.expand`의 `## PRD Amendment N`에 정렬.
- **디자인 기반 스킬 `ms-design-baseline`**: Feature가 UI 표면을 처음 만들 때 최소·일관 디자인
  기반(`docs/design/DESIGN.md` + `tokens.css` + 중립 `base.css`, WCAG 하한 내장)을 1회 생성.
  `/ms.implement` Step 1.6과 `/ms.review` Done Criteria에 연동.
- **웹 UI 검증 스킬 `webapp-testing`**: Playwright 기반 서버 lifecycle 관리·스크린샷·콘솔 로그
  캡처(게이트 실행 시 headless 기본). `/ms.review` Done Criteria의 웹 UI criterion 실행 엔진.
- **배포/환경 디버깅 playbook `ms-ops-debugging`**: SSH 터널·리버스 프록시·TLS·컨테이너 lifecycle
  ·시크릿 로테이션 등 "로컬은 되는데 배포하면 깨지는" 실패 클래스를 증상 색인으로 정리.
- **결정론적 게이트 하네스**: `specter-gate.sh`(기계적 게이트 체크), conductor resume용 run-state
  ledger, feature-map/gate 정합성·TAG 체인 pre-commit backstop, `/speckit-specify` 직접 호출을
  차단하는 PreToolUse 훅(`speckit-specify-gate-hook.sh`), SessionStart 상태 주입.
- **`/ms.merglease` semver 자동화**: conventional commits로 버전 자동 계산, GitHub CI 실패를
  billing/quota/infra(경고 후 진행) vs 실제 test/lint/type/build 실패(머지 중단)로 분류.

### Changed
- **Feature Map에서 Progress Ledger 분리**: Feature Status 북키핑(⬜/🚧/✅)을
  `docs/prd/feature-map.progress.md`로 이동해 `feature-map.md`의 SHA256이 진행 표시로 바뀌지 않게 함
  — 상태 갱신이 게이트를 stale로 만들지 않음.
- **`/ms.checklist` 미해결 placeholder 검사**: owned commitment/done criterion의 `TBD`·`TODO`·
  `{{...}}`·`_or_equivalent` 토큰을 감지(어디든 WARN, done criterion 내부는 FAIL)해 clarify-time
  churn을 `/ms.specify` 이전에 차단. PRD read scope도 선택 Feature로 좁힘.
- **외부 에이전트 호출 프로토콜 강화**(Codex + Antigravity): 호출·재시도·degrade 규율 정비,
  `/ms.review`·`/ms.analyze` re-review 라운드 상한.
- **스킬 강화**: `ms-foundation-trust`에 fail-open/fail-secure 기본값 taxonomy,
  `ms-lang-typescript`에 테스트 안티패턴·mock 경계 가이드, `ms-essentials-debug`에 hard-bug 진단 규율.
- **`/ms.fin` 논리 단위 커밋 분리를 기본화**, git commit/push·`gh pr` 권한을 ask→allow로 이동.

### Fixed
- `speckit-specify-gate-hook.sh`에 TTL과 jq 미설치 fallback 추가.
- `specter-gate.sh`가 누락된 체크리스트 필드를 관대하게 처리.
- `/ms.verify` 템플릿에서 죽은 Source Command 필드 제거.

### Docs
- README 워크플로우를 라벨링된 사이클 다이어그램(Pre-Feature/Per-Feature)으로 재작성하고, 명령·게이트
  변경분(placeholder 게이트, webapp-testing·design-baseline 연동, PRD 저작)을 반영.
- 명령 전반 session read-dedup 정책과 conductor manifest 추가, `/ms.specter`·`/ms.pre-specter`
  bare 호출 권장, Antigravity write-flag 재적용 절차 문서화, SYSTEM_MAP 재생성.

## [2.2.0] - 2026-06-27

### Added
- **`/ms.specter` per-Feature 사이클 조정자**: `checklist → agent-verify → specify →
  clarify → plan → tasks → analyze → implement → review`를 자동 진행. 각 단계 판정을
  읽어 PASS/WARN은 진행(WARN 수집), FAIL은 정지, `/ms.clarify`만 사람에게 위임. 게이트를
  약화·우회하지 않고 판정만 읽음. 입력은 freeform Feature 번호 + 선택적 `@PRD`/`@feature-map` 경로.
- **`/ms.fin --no-ci`**: 명시적 WIP/백업 publish(조건부 CI 강제 생략) 플래그.

### Changed
- **마무리 명령 `/ms.fin`으로 단일화**: `/fin`·`/finq`를 제거하고 `/ms.fin` 하나로 통합.
  publish 전 CI 게이트를 **조건부 실행** — 마지막 `/ms.review`가 clean이고 워킹트리가 그 이후
  변경되지 않았으면(`.specify/review-hash.cache` 해시 일치) 생략, 그 외(리뷰 후 수정·`/ms.fix`·
  직접 커밋)에는 실행. 불확실하면 실행으로 안전 폴백.
- **`/ms.review` 적대적 리뷰 기본화**: Codex & Antigravity 코드 리뷰가 항상 adversarial
  모드로 동작(설계 대안·숨은 리스크 챌린지). `--adversarial` 플래그 제거.
- **`/ms.agent-verify` foreground 병렬화**: Codex & Antigravity를 백그라운드 대신 foreground
  병렬로 실행해 쓰기 실패를 즉시 관찰하고 1회 재시도 후 정지. `/ms.verify`의 Antigravity 단계도
  명시적 foreground화.

### Docs
- README·AGENTS.md·에이전트·스킬·docs 전반에서 `/fin`·`/finq` 참조를 `/ms.fin`으로 갱신하고
  현재 워크플로우 상태를 반영.

## [2.1.1] - 2026-06-27

### Changed
- **Antigravity 위임 모델 고정**: `/fin`, `/finq`, `/ms.merglease`, `/ms.verify`, `/ms.analyze`,
  `/ms.review`, `/ms.agent-verify` 및 README의 안티그래비티 위임 지점 9곳에서 `--model`을
  `gemini-2.5-pro` → `gemini-3.5-flash`로 변경. `--model` 플래그가 플러그인 기본값을 덮어쓰므로
  `in-plugin` 업데이트와 무관하게 모델이 고정됨. Codex(`gpt-5.5`)는 변경하지 않음.
- 안티그래비티 이중 에이전트(Codex & Antigravity) 교차 검증 및 실행 파이프라인 위임을
  `/ms.analyze`·`/ms.review`·`/ms.agent-verify`·`/ms.verify`에 반영.

### Docs
- README의 `/ms.verify` 설명과 명령어 플래그(`--skip-codex`/`--background`/`--model`/`--effort`/
  `--adversarial`) 문서화 보강 및 역할·프로세스 설명 정리.

## [2.1.0] - 2026-06-24

### Changed
- **Spec-Kit 호환성 (loose coupling)**: `/ms.init`의 Feature-Map 게이트 주입을 command·skill
  **양쪽 레이아웃과 dual 레이아웃**까지 탐지·주입하도록 확장. 존재하는 모든 후보 파일에
  주입하며 `MS_FEATUREMAP_GATE_START` 마커로 idempotent.
- 업스트림 스킬 개명에 맞춰 `/ms.*` 래퍼의 위임 호출을 `speckit.x` → `speckit-x`로 정렬
  (specify·clarify·plan·tasks·analyze·implement). 라이브 `specify init` v0.11.6로 검증.
- 업스트림 버전을 `SPEC_KIT_REF`로 핀(기본 `v0.11.6`)하여 churn 차단. 구형 `--ai` 플래그를
  현행 `--integration claude`로 교체.
- `/ms.review`의 prerequisites 호출을 현행 spec-kit 경로/플래그로 교정
  (`.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`).
  spec.md/plan.md 검증은 SPECTER가 자체 소유함을 명문화.
- `/ms.init` 검증에서 `specs/` 요구 제거(첫 `/ms.specify` 때 생성됨), `docs/templates` 출처 정정,
  spec-kit의 `CLAUDE.md` 블록 append 동작 문서화.
- **devcontainer**: 종료된 Gemini CLI(2026-06-18)를 후속 Antigravity CLI(`agy`)로 교체.
  Dockerfile 설치 방식·Makefile 타깃(`gemini gm`→`antigravity agy ag gm`, `gm` 별칭 유지)·
  docker-compose 자격증명 볼륨(`~/.gemini`→`~/.config/agy`)·`setup-pm.sh` 안내문 갱신.

### Added
- `/ms.*` 명령에 `argument-hint` frontmatter 추가(슬래시 입력 힌트).
- README "Spec Kit 호환성"에 **위임 지점 표 · 정체성 불변식 · 결별 기준(divorce tripwires)** 문서화.
- AGENTS.md §10에 command/skill/agent 계층 정의와 Spec-Kit 결합 계약·정체성 규칙 추가.

## [2.0.0] - 2026-06-18

### Changed
- Reworked the `/ms.*` workflow documentation to match the current feature-map, checklist, plan, tasks, analyze, implement, and review flow.
- Clarified Codex plugin setup so users enter the project container through Codex CLI, then install the plugin from the Codex plugin directory.
- Updated `ms.init` output to guide users through the correct plugin installation path.
- Simplified repository docs to keep only the template-oriented files and agent-facing snapshot needed by this template repo.

### Added
- Restored `docs/dev_daily.md` and `docs/todo.md` as empty template files.
- Restored `docs/SYSTEM_MAP.md` as an agent-facing snapshot.
- Added a root-level changelog for release notes.

### Removed
- Deleted template-repo-only operational docs that were not meant to remain as permanent artifacts.

## [1.0.0] - 2025-01-01

### Added
- Initial stable release baseline.

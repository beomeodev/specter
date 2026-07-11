# Changelog

All notable changes to this repository are documented in this file.

## [Unreleased]

### Added
- **Graphify 코드 그래프 도입 (`/ms.init` Step 2.9)**: 소비 프로젝트에 tree-sitter 로컬 코드
  그래프(`graphifyy`, `GRAPHIFY_VERSION` 핀, 도구 인터프리터는 3.12로 격리)를 필수 설치 —
  초기 `--code-only` 빌드, post-commit/post-checkout 자동 재빌드 훅, `graphify-out/` gitignore.
  구조 탐색(`graphify query/path/explain`)의 읽기 규칙은 `AGENTS.md §9`에 명문화 (그래프는
  검증할 file:line 포인터, 코드 수정 후 `graphify update .`).
- **`/ms.specter` Step 0.6**: 사이클 시작 시 그래프 self-heal(`--update`); 바이너리 부재 시
  `UNAVAILABLE` WARN 기록 후 계속 — 그래프는 가속기이며 게이트가 아님(FAIL 불가 불변식).

### Removed
- **미발화 스킬 8종 폐기** (~6,200줄; 커맨드 매개 세션에서 설명-트리거 스킬은 구조적으로 발화
  불가 — wire or retire): ms-essentials-review·ms-foundation-constitution(리뷰 루브릭·제한치는
  ms.review와 constitution-template §II가 소유), ms-lang-python·ms-lang-typescript(테스트 품질
  독트린은 salvage 후 폐기), ms-essentials-debug(Hard-Bug Discipline은 /ms.fix로 이식 후 폐기),
  ms-workflow-living-docs(up-docs가 소유), ms-workflow-tag-manager(규칙은 ms.implement/ms.fix
  인라인이 소유; 자기모순적 @UPDATED 수동 스탬프 프로토콜 포함), ms-foundation-ears(GEARS 독트린
  2건 salvage 후 폐기 — 문법의 단일 소스는 constitution-template §II + spec-template).
- **미발화 에이전트 8종 폐기** (240세션 디스패치 0회 실증): code-refactor-master,
  refactor-planner(리팩터 트랙은 `/ms.implement --mode=refactor`·`/ms.fix`가 소유), git-hygiene,
  doc-updater(fin→up-docs가 수행), library-researcher(context7 제거로 데이터 소스 소멸),
  spec-builder(upstream speckit-specify 엔진의 일), quality-gate·trust-validator(ms.review가
  디스패치를 지시했으나 51사이클 0회 — TRUST 검사는 인라인 수행이 실태라 유령 배선을 인라인
  문구로 교정). salvage 감사 결과 8종 합산 비중복 콘텐츠 0건. 생존: local-ci(22회),
  web-research-specialist(3회, 사망 페어 참조 정리).
- **`/ms.amend` 커맨드 폐기**: 전 프로젝트에서 호출 0회 — 실제 역할은 2026-07-04 도입된
  Deviations log(`specs/<id>/implementation-notes.md`, `/ms.implement`가 기록·`/ms.review`가
  보고)가 대체 중이었음. 요구사항을 대체하는 변경은 `/ms.expand` 경유로 명문화. Amendment
  블록 규율(기존 FR 제자리 수정 금지, old→as-built→why append)은 overnight-run 체인 모드의
  드리프트 사다리에 인라인으로 승계.
- **context7 MCP 제거**: `.mcp.json`(마지막 엔트리라 파일째 삭제)·`settings.json` MCP 키,
  README 선택 의존성/링크, ms.implement·ms.tasks의 "or Context7" 문구. 근거: 전 프로젝트
  ~240세션에서 실호출 1건 — 매 세션 시스템 프롬프트 instructions 상주 + npx 스폰 비용 대비
  무가치. 의존 페어인 library-researcher 에이전트는 별도 검토 트랙.
- **Serena MCP 완전 제거**: `.mcp.json`·`settings.json` 엔트리, `.serena/` 디렉토리, AGENTS.md
  §9·`codebase-snapshot` 스킬의 폴백 프로즈. 근거: 2026-06-18 설정 이후 47개 세션에서 도구 호출
  0건 + 바이너리 경로 미해결, 심볼 내비게이션 역할은 Graphify가 대체. `check_tag_chain.py`의
  `.serena` 스캔 제외 항목은 소비 프로젝트 잔존 디렉토리 방어용으로 존치.

### Changed
- **폐기 전 salvage 편입**: 미발화 스킬에 갇혀 있던 증거 기반 독트린을 살아있는 워크플로로 이식 —
  테스트 품질 안티패턴 4종(구현 세부 결합·사이드채널 검증·동어반복 테스트·목 경계 규칙)을
  `/ms.review` Test Quality 항목으로(언어 중립화), Hard-Bug Discipline 5단계(최소 재현→가설
  선행→단일 프로브→올바른 seam→클로즈아웃)를 `/ms.fix` Step 2로, GEARS 보강 2건(금지 약한
  조동사 can/could/might/should, GEARS→Given-When-Then 절 매핑)을 constitution-template §II로.
  `ms-ops-debugging`의 위임 참조는 `/ms.fix` Hard-Bug Discipline으로 재지정.
- **`codebase-snapshot` 스킬 축소**: SYSTEM_MAP에서 구조 인벤토리 섹션(`Repository Shape`,
  `Hot Paths`) 폐지 — 구조 사실은 그래프 또는 실시간 `rg`/`find`가 담당하고, 맵은 저변동성
  큐레이션 프로즈(목적·워크플로·불변식·리스크·검증 커맨드)만 유지. Graphify 분업 원칙과
  `graphify:` 메타데이터 필드 추가. `docs/SYSTEM_MAP.md`를 새 스키마로 재생성.

## [2.3.1] - 2026-07-06

### Added
- **`/ms.sync` 워크플로우 브로드캐스트**: manifest에 등록된 워크플로우 파일(.claude 커맨드/스킬/
  에이전트, 게이트 스크립트, 템플릿, AGENTS.md)을 머신 로컬 레지스트리의 프로젝트 레포들로 3-way
  머지 배포. 엔진 `scripts/specter_sync.py` + 테스트 `tests/test_specter_sync.py`.
- **`/ms.prd` PRD 공동 저작 커맨드**: `/ms.pre-specter` 앞단의 사전 워크플로우 인터뷰 트랙
  (블라인드스팟 패스, 갭 열거, Parking Lot).
- **`/ms.audit` 제품 수준 완전성 감사**: 노출/콜드스타트/위협모델/perf·a11y/게이트 가치/블라인드
  스팟 6개 모듈, 자문형(게이트 아님), 발견은 `/ms.fix`·`/ms.expand`·todo로 라우팅.
- **워크플로우 스킬 6종**: `git-worktrees`, `parallel-features`, `overnight-run`(+
  `specter-overnight.sh` 드라이버), `spike`, `transcript-mining`, `testing-skills-with-subagents`.
- **`/ms.fin` High-Stakes Diff Digest**: auth/돈/파괴적 연산/마이그레이션/사용자 데이터 hunk만
  발췌해 사람 ack를 받는 조건부 게이트 (unpushed 커밋 범위 포함 — `/ms.fix` 트랙도 포착).
- **`/ms.review` Migration Rollback 분석(6.6b)**: 마이그레이션 diff에 대해 롤백 경로·중간 실패
  상태·비가역 연산을 분석하고 사람 ack 없이는 READY 불가.
- **`/ms.init` Step 2.8**: TAG-chain·Feature-Map pre-commit backstop을 대상 프로젝트의
  `.pre-commit-config.yaml`에 배선하고 `pre-commit install` 실행 (이전에는 스크립트만 배포되고
  실행 배선이 없었음).
- **`check_tag_chain.py` FIX-트랙 지원**: `FIX-*` id는 `@SPEC` 앵커 면제, presentational 마커
  (`@TEST: (presentational — no test)`) 허용. 테스트 `tests/test_check_tag_chain.py` 추가.
- **`/ms.sync` 삭제 전파**: SPECTER에서 실제로 삭제된 manifest 파일은 타겟에서도 제거
  (`DELETED-UPSTREAM`; 타겟이 커스터마이즈한 파일은 보존하고 baseline만 해제 —
  `DELETE-KEPT-LOCAL`, 이후 타겟 소유). manifest glob 축소는 삭제로 취급하지 않음.
  프루닝으로 지운 스킬/에이전트의 낡은 사본이 타겟에 남는 문제를 해결.

### Removed
- **프루닝(2026-07-06, 감사 보류 결정 확정)**: 고아 에이전트 7종 삭제(codebase-explorer ·
  constitution-extractor · debug-helper · implementation-planner · integration-designer ·
  tag-auditor · tdd-implementer — 어떤 커맨드도 디스패치하지 않았음; codebase-explorer의
  기능 착수 전 유사 패턴 탐색 체크리스트는 `codebase-snapshot` 스킬로 흡수). 죽은 범용
  스킬 5종 삭제(api-testing-patterns · ci-cd-optimization · cross-cutting-concerns ·
  ms-architecture-patterns · ms-database-design — 참조 0, sync로 전 레포에 배포되던
  ~4.4k줄). `skill-rules.json` 삭제(실행 주체 없는 평행 레지스트리 — 스킬 트리거는
  SKILL.md frontmatter description이 소유). `docs/src/` 삭제(미참조 TS 레퍼런스 코드).
  구세대 `backend/AGENTS.md`·`frontend/AGENTS.md` 삭제(black/pylint/eslint 지시가 현행
  ruff/Biome 체계와 모순; 루트 AGENTS.md + ms-lang 스킬이 대체). `make finish`/`make finq`
  삭제(`git add .` 일괄 커밋이 커밋 분리 규칙과 충돌; 커밋/푸시는 /ms.fin 또는 수동 git).

### Changed
- **감사 후속 정비(2026-07-06)**: `/ms.codex-verify` 잔재 10곳을 `/ms.agent-verify`로 개명하고
  단일 에이전트 서술을 dual-agent로 정정. "My-Spec"/MoAI 잔재 명칭 일괄 정리. Constitution 템플릿
  §I 워크플로우 다이어그램 현행화, §IV/§V를 pre-commit backstop과 정합(기계적 wiring은 차단,
  의미론적 TAG 이슈는 경고). `/ms.merglease`가 progress ledger 수정을 커밋·푸시하도록 수정.
  `/ms.fin` PR body를 리뷰 리포트에서 생성(존재하지 않던 `docs/PR_*_BODY.md` 의존 제거).
  `implementation-notes.md`를 `/ms.review`·`/ms.amend`가 실제로 소비하도록 배선. mypy CI 게이트
  fail-open 수정. 에이전트 정의의 Model-Selection 의례 블록·유령 참조 제거.
- **코어 스크립트/테스트 재배치**: 게이트·sync 스크립트를 `scripts/specter/`로, 해당 테스트를
  `tests/specter/`로 이동하고 모든 참조 경로를 갱신.
- **README 전면 개편**: 847줄 → 간결판으로 재구성(워크플로우 다이어그램·계약 섹션 유지),
  영어 정본 `README.md` + 한국어 `README.ko.md`로 분리, 멀티 에이전트(Codex 드라이버 패리티)
  및 uv 패키지 배포 로드맵 섹션 신설.

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

## [1.0.0] - 2026-05-25

### Added
- Initial stable release baseline.

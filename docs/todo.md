# TODO

<!-- Add working notes here. -->

## MoAI-ADK `.claude` 선별 도입 (2026-07-11 감사 → 07-12 승인, 5건)

**배경**: modu-ai/moai-adk의 hooks/output-styles/rules 3축 감사 결과, 파일 단위 이식은 전부 불가
(훅 35개 중 31개가 `moai` Go 바이너리 위임 래퍼)이고 메커니즘 단위로 아래 5건만 도입 확정.
output-styles 3종·@MX:DEBT·moai-memory·cadence-bridge·agent-patterns는 명시적 스킵(재검토 불필요).

**⚠ 전제 — SPECTER 기존 자산 (감사 후 재확인됨, 백지 신설 아님)**:
- `docs/templates/scripts/specter-stop-gate.sh` — Stop 훅 **이미 존재**. phase 스코프(/ms.implement·
  /ms.review 중에만 활성), 증거 강제("게이트를 돌리게 강제, 성공을 강제하지 않음" — 어떤 verdict든
  기록되면 통과), 3회 차단 캡, fail-open, tree_signature 기반. `/ms.init` 2.7b가 타깃 프로젝트
  `.specify/scripts/bash/`에 설치 + settings.json Stop 와이어링(idempotent).
- `docs/templates/scripts/specter-session-status.sh` — SessionStart 훅 **이미 존재**. Feature Map
  상태/원장 마지막 활동/다음 Feature를 additionalContext로 주입. `/ms.init` 2.7이 설치·와이어링.
- 따라서 작업 1·2는 이 두 스크립트의 **확장**이며, settings.json 와이어링·ms.init 수정은 원칙적으로
  불필요(같은 스크립트 파일을 확장하므로). 단 **배포 경로 확인 필수**: `/ms.sync`가 docs/templates만
  뿌리는지, 타깃의 `.specify/scripts/bash/` 설치본까지 갱신하는지 검증하고 후자가 아니면 sync 절차에
  재설치 스텝 추가.

**원본 참조가 필요하면**: `git clone --depth 1 https://github.com/modu-ai/moai-adk <scratchpad>/moai-adk`
- 작업 1 원본: `.claude/hooks/moai/sync-phase-quality-gate.sh` / 작업 3: `.claude/rules/moai/core/
  verification-claim-integrity.md` / 작업 4: `.claude/rules/moai/workflow/session-handoff.md` §Diet
  Constraints. 아래 사양은 자립적으로 작성했으므로 재클론 없이 진행 가능.

**공통 설계 원칙 (전 작업 구속)**:
- 훅은 자립형 bash만, 외부 바이너리·공유 설정 의존 금지 — moai 자신의 hook-independence 교훈
  ("31개 래퍼가 바이너리 부재 시 무음 no-op"). 확장 시 5문항 점검: ① 공유 바이너리/설정/env 의존?
  ② 새 공유 실패 조건? ③ 우회가 로그되는가? ④ 우아한 강등? ⑤ 강등이 표면화되는가?
- Advisory-Check Discipline: 훅 비용 time-box + 저장소 크기와 무관(파일 수 비례 스캔 금지), fail-open.
- 커밋 분할: 훅 확장(작업 1+2) / 보고 형식(작업 3) / 리뷰 체크리스트(작업 5) / 핸드오프 스킬(작업 4).

---

### 작업 1 — Stop 게이트에 "phase 밖" 경량 품질 검사 추가 (최우선)

**목적**: 기존 stop-gate는 phase 파일이 없으면 완전 inert — 즉 `/ms.*` 워크플로우 밖 수시 편집
(ad-hoc 편집, /ms.fix 밖 폴리싱 등)은 여전히 무검사 통과. moai `sync-phase-quality-gate.sh`의
메커니즘(언어 감지·변경 파일 스코프·경량 검사·센티널)으로 이 잔여 구멍을 메움. 기존 phase 게이트의
"증거 정직성" 철학과 직교·상보적: phase 중 = 증거 강제(기존 유지), phase 밖 = 기계적 fast-check(신규).

**수정 파일**: `docs/templates/scripts/specter-stop-gate.sh` — `hook_mode()`의
`[ ! -f "$PHASE_FILE" ]` 분기가 현재 `reset_blocks; exit 0`인 자리에 `offphase_check` 호출 삽입.

**offphase_check 사양**:
1. **강등 스위치**: `SPECTER_STOP_GATE=off` → 스킵(로그 남김), `=advisory` → 실패 시
   `{"systemMessage":...}` 경고만. 미설정 기본은 차단.
2. **대상 산정**: `git diff --name-only HEAD` + untracked(exclude-standard) 중 소스 확장자만.
   기존 PATHSPEC 제외(`.specify/ docs/ specs/ *.md`) 재사용. **작업 2의 세션 스냅샷에 기록된
   기존 dirty 파일은 제외** (사용자 사전 변경을 게이트하지 않음). 대상 0개면 exit 0.
3. **센티널 (재검사 억제)**: 기존 `tree_signature()` 재사용. 직전 PASS 서명을
   `.specify/.ms-offphase-pass`에 기록, 현재 서명과 같으면 즉시 exit 0. moai의 write-before-run
   패턴대로 검사 시작 전 서명 기록(검사 중 크래시가 재검사 루프를 만들지 않게).
4. **언어 감지**: 마커 파일 순차 확인 — `go.mod`→go, `pyproject.toml`|`requirements.txt`→python,
   `package.json`→node, `Cargo.toml`→rust. 등록 프로젝트 실사용 언어만 우선, 미감지 시 exit 0.
   (moai 원본은 16개 언어 — 필요 시 참조.)
5. **검사 실행 (경량만, 전체 테스트 금지)**: 변경 파일 한정 fast check —
   python: `ruff check <files>`, node: `npx eslint <files>` 또는 `tsc --noEmit`(프로젝트 설정 따름),
   go: `go vet ./...`, rust: `cargo check -q`. `command -v` 가드로 도구 부재 시 스킵+로그.
   출력은 `mktemp -d` 리다이렉트, `trap EXIT` 정리, 전체 time-box(예: 45s, `timeout` 명령).
6. **차단 캡**: 기존 `BLOCKS_FILE` 카운터·`MAX_BLOCKS=3` 기계 재사용(offphase 전용 카운터 파일 분리
   권장: `.specify/.ms-offphase-blocks`). **동일 실패 반복 감지**: 실패 출력 해시를 저장, 직전과
   동일하면 캡 미만이어도 차단 중단 → 통과+경고 (환경 문제/flaky를 사용자에게 보고).
7. **차단 메시지 형식** (글의 "좋은 피드백" 원칙): 실패한 명령 원문 + 실패 출력 핵심 발췌 +
   관련 변경 파일 목록 + "수정 후 같은 명령을 재실행하고 통과 후 종료" 지시. 기존 emit_block 재사용.
8. 주의: `stop_hook_active` stdin 필드도 방어적으로 확인(기존 스크립트는 stdin을 drain만 함 —
   `"stop_hook_active":true` 감지 시 즉시 exit 0을 offphase 경로에 추가. phase 경로는 기존 캡이
   이미 방어하므로 현행 유지).

**검증**:
- `bash -n` + shellcheck(있으면).
- 수동 6경로: ① phase 열림 → 기존 동작 그대로(회귀 확인: phase/record CLI 모드) ② phase 없음+깨끗한
  트리 → exit 0 ③ phase 없음+lint 깨진 py 파일 → block JSON ④ 같은 트리 재시도 → 센티널 exit 0
  ⑤ advisory 모드 → systemMessage만 ⑥ 3연속 차단 or 동일 실패 반복 → 통과+경고.
- 실전: SPECTER 저장소 자체에서 고의 문법 오류 후 Stop 유도 (이 저장소 settings.json에는 훅이 없으니
  로컬 확인은 스크립트 직접 실행으로).

---

### 작업 2 — SessionStart에 dirty-snapshot 기록 추가 (작업 1과 한 커밋)

**목적**: 세션 시작 시점 기존 변경을 기록해 ① 작업 1의 offphase 검사가 사용자 사전 변경을
차단하지 않게, ② 병렬 Feature·overnight에서 "에이전트 변경 vs 기존 변경" 구분 근거.
(phase 게이트는 phase-open 시점 서명이 이미 baseline 역할 — 이 스냅샷은 offphase 경로 전용.)

**수정 파일**: `docs/templates/scripts/specter-session-status.sh` 확장.

**사양**:
1. stdin JSON의 `source` 확인: `startup`|`clear`일 때만 스냅샷 갱신. `resume`|`compact`는 기존
   스냅샷 유지 (세션 중간 상태를 "기존"으로 오인 방지 — moai의 source 구분 패턴).
2. 기록 → `.specify/.ms-session-snapshot`: `base_commit=<HEAD>`, `branch=<브랜치>`,
   `preexisting_dirty=` 목록(`git status --porcelain` 파일 경로들).
3. 기존 additionalContext 요약 라인에 `dirty N개 (기존 변경)` 정도만 덧붙임 — 전체 diff/목록 주입
   금지, 짧고 빨라야 함.
4. fail-open 유지: git 저장소 아님/오류 시 기존처럼 무출력 exit 0.
5. `.ms-session-snapshot`·`.ms-offphase-*` 상태 파일이 gitignore되는지 확인 — 기존
   `.ms-stop-phase` 등의 처리 방식을 그대로 따름 (타깃 프로젝트 .gitignore 템플릿 확인).

**검증**: dirty 파일 있는 상태에서 스크립트에 `{"source":"startup"}` 파이프 → 스냅샷 생성 확인;
`{"source":"resume"}` → 갱신 안 됨 확인; 작업 1과 통합 — 기존 dirty 파일의 lint 오류가 offphase
차단을 유발하지 않아야 함.

---

### 작업 3 — 검증 보고 형식에 Gaps / Residual-risk 필드

**목적**: 07-10 게이트 가치 감사의 원장 과소보고 문제 처방. "관찰하지 않은 것은 성공도 실패도
주장하지 않는다" 불변식을 보고 형식에 구조로 박음.

**수정 파일**: `.claude/skills/specter-agent-protocols/SKILL.md` (보고서 프로토콜 절 — §3 리포트
체크·§5 편향방지 독트린과 접합). 커맨드 파일들은 SSOT 포인터 구조이므로 원칙적으로 무수정 —
자체 보고 형식을 중복 정의한 커맨드가 있는지만 rg로 확인.

**추가 내용**:
1. 검증 보고 5섹션: **Claim** / **Evidence**(명령+출력 verbatim, 요약 금지) / **Baseline**(무엇 대비,
   이번 실행에서 측정) / **Gaps**(관찰하지 못한 것 — 방어적 핵심) / **Residual-risk**(관찰했음에도
   남는 위험). Gaps가 비면 "전수 관찰"의 근거를 요구 (빈 섹션 상투어 방지).
2. **결함 주장 대칭 규칙**: 결함/부채/드리프트 주장도 도메인 도구 확인 전까지 가설(UNVERIFIED) 표기.
   (moai 실사례: grep 추론 "29건 정리 필요" → 감사 도구 실행 결과 0건.) 기존 UNVERIFIED 마킹
   독트린을 결함 방향으로 한 줄 확장.
3. "증거 부재 ≠ 성공 증거, ≠ 실패 증거" 문구를 편향방지 독트린 옆에 배치.

**검증**: 편집 후 `/ms.verify` 1사이클 실행, 보고서에 Gaps가 실질 내용으로 채워지는지 확인.

---

### 작업 4 — 세션 핸드오프 스킬 신설 (+ Diet Constraints)

**목적**: MoAI v3 비교(메모리 moai-adk-comparison-2026-07)에서 1순위 채택 후보로 판정만 되고 미착수던
세션 핸드오프 실구현. 기존 자산이 절반 제공: `specter-run.jsonl` 원장(마지막 step/verdict)과
session-status 훅(다음 세션 상태 주입)이 이미 있으므로, 스킬은 **원장이 못 담는 것**(적용 교훈,
전제조건, 단일 실행 명령)에 집중.

**신규 파일**: `.claude/skills/session-handoff/SKILL.md` (§10 구조상 재사용 능력 = skills).

**형식 (moai 6블록 축소 — 현지화 테이블·mode-seeding·CLI 저장 연동 전부 제외)**:
```text
✂──── 여기부터 복사 ────✂
<Feature/작업> <단계> 재개.
적용 교훈: <메모리/원장 참조, 최대 4줄>

전제 검증:
1) <검증 가능한 명령> → <기대 결과>   (최대 4개, 각 200자 이내)

실행: <단일 명령 또는 액션 1개>

후속: <머지 후/다음 Feature, 최대 2줄>
✂──── 여기까지 복사 ────✂
```

**발동 트리거 (SPECTER 적응)**: ① 컨텍스트 임계 접근(수치는 구현 시 판단) ② `/ms.specter` Feature
완료 시 다음 Feature 잔존 ③ 사용자의 명시적 세션 종료 의사("세션 종료", "내일 이어서" 등)
④ `/ms.fin` PR 생성 + 미완 Feature 잔존.

**Diet Constraints (안티패턴으로 명문화)**: 재개 메시지는 "다음 세션 최소 실행 컨텍스트"이지 감사
기록이 아님 — 이력 서사 금지 / 의례적 리마인더 금지 / 다단계 서브스텝 인라인 금지 / 재시도 거치며
늘어난 문장은 삭제 / 상한 초과분은 메모리 파일로 이동. 출력 순서: 펜스 블록 → (저장 시) 파일 경로 →
한 문장 요약. 저장 실패 fail-open.

**중복 정리**: session-status 훅 주입과 겹치는 내용(마지막 step, 다음 Feature)은 핸드오프 블록에서
전제 검증 명령으로만 참조하고 본문 중복 금지.

**검증**: testing-skills-with-subagents 적용 대상(규율 강제 스킬) — RED(스킬 없이 핸드오프 시켜
비대해지는지 확인) → GREEN(스킬 로드 후 상한 준수) 최소 1라운드. `/ms.sync` 배포 전 필수.

---

### 작업 5 — /ms.review에 경계 검증 체크리스트 7종

**목적**: 유닛테스트가 구조적으로 못 잡는 경계(seam) 버그를 리뷰 체크리스트로. API/프론트/DB 경계나
상태머신을 건드린 Feature에만 **조건부** 적용 (전 리뷰 강제 아님 — 의례 최소화).

**수정 파일**: `.claude/commands/ms.review.md` — 기존 절차에 "경계 검증(조건부)" 절 추가.

**체크리스트 7종**:
1. API 응답 shape 불일치가 제네릭 캐스팅(`as T` 등)으로 은폐되지 않았는가
2. 파일 경로 ↔ 라우터 매핑 불일치 (route group / dynamic segment)
3. 상태머신에 정의만 되고 구현 안 된 전이(dead transition)가 없는가
4. camelCase ↔ snake_case 필드명이 DB/API/프론트 계층 간 드리프트 없는가
5. 프론트가 호출하는 API 엔드포인트가 실제 구현돼 있는가
6. 비동기 워크플로우의 복수 응답 shape(즉시 202 vs 최종 결과)이 타입으로 유니온돼 있는가
7. 타입 캐스트 우회로 숨은 실제 shape 불일치가 없는가
+ 방법론 한 줄: "경계는 양쪽을 함께 읽는다 — 한쪽씩 검사한 통과는 경계 통과가 아님".

**검증**: 문서 수정 렌더 확인 + 다음 실전 `/ms.review`에서 조건부 발동 관찰.

---

### 실행 순서 및 완료 기준

1. 작업 1+2 (기존 훅 확장, 한 커밋) → 2. 작업 3 → 3. 작업 5 (경량 문서) → 4. 작업 4 (스킬 신설 +
서브에이전트 압박 테스트, 가장 무거움).

완료 기준: 커밋 4개 분할 / stop-gate 수동 6경로 + 기존 phase 동작 회귀 통과 / 핸드오프 RED·GREEN
1라운드 통과 / `/ms.sync` 배포 경로 검증(설치본 갱신 여부) 완료 또는 후속 처리 기록.

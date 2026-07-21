# Daily Log

<!-- Append dated entries here. -->

---

## 2026-07-19 — 3층 게이트 구조 채택 + 발행/릴리즈 헬퍼 1차

- **feat(gate)** `415c175`: specter-gate.sh v2 서브커맨드 — `structural`(Layer-1
  결정론 형태 검사), `aggregate`(Layer-3 기계 집계: station 고정 입력, Mode/SHA/
  Feature 검증, 기계 원장 영수증), `version`(케이퍼빌리티 프로브). 테스트 44개.
- **feat(workflow)** `56d22b1`: 전 검증 station을 3층 계약으로 개조. 호스트는
  저술·조립만 하고 판정하지 않음(§5 단독 강등 금지, §4 fresh 재라운드),
  /ms.verify에 Codex 전역 검증 신설, featuremap/checklist는 격리 서브에이전트
  저술, 컨덕터 재개 신선도 가드. `specter-agent-protocols` §7 계약 신설.
- **feat(publish)** `650137f`: 읽기 전용 릴리즈/발행 헬퍼 1차 —
  specter-release.sh(semver 계산·종상태 검증), specter-publish.sh(발행 종상태).
  4상태 체크(true/false/not_applicable/unknown), origin/master 하드코딩 제거,
  /ms.fin untracked 스캔 구멍 수정. 테스트 32개. 2~5차 대기열은 docs/todo.md.
- **docs** `57917e2`: AGENTS §10·README·SYSTEM_MAP·todo.md 문서화.
- 검증: Codex(gpt-5.6-sol) 외부 재검증 각 3라운드 수렴(FAIL→FAIL→PASS-WITH-NOTES),
  전체 테스트 131개 통과, 커버리지 90.13%. xhigh 행(hang) 2건은 취소 후 high로
  재발주하여 해결.

---

## 2026-07-21 — 외부 에이전트 백그라운드 완료 수거 규칙(§9)

- **feat(protocols)**: `specter-agent-protocols` §9 "Background Completion
  Collection" 신설. detached 외부에이전트 데몬(`codex`/`agy --background`)은
  완료/사망을 host에 self-notify 하지 않으므로, 완료 수거를 harness-tracked
  waiter(Agent 서브에이전트 또는 `Bash(run_in_background:true)`)로만 라우팅한다.
  규칙: Agent 경유 1순위 / 데몬 직접호출은 포그라운드 `--wait`+Bash `timeout:600000`
  (10분) / 초과 시 `status --wait` 대기꾼을 harness 백그라운드로 / 죽음 감지 후
  degrade / 대기꾼 없이 "완료 시 알림" 약속 금지.
- **docs(commands)**: `/ms.analyze`·`/ms.review`의 `--background` 처리를 §9로
  연결. 기존 "유저에게 재실행을 떠넘기고 PENDING stop" → harness-tracked 대기꾼으로
  같은 세션에서 자동 이어감으로 교정.
- 근거: 5개 워크스페이스 최근 세션 트랜스크립트 감사(cork 백그라운드 dispatch 7건 중
  결과 미수거 5, idle-while-done 3; 대조 세션은 사고 0). Codex "120초 자동 백그라운드"의
  실제 원인은 Claude Code Bash 도구 기본 타임아웃 2분으로 규명. 서브에이전트 4개 ×
  5+압박 압박테스트 전부 준수(새 rationalization 0)로 sync-safe 판정.
- **chore(test)**: 기존 테스트 3파일 ruff format 정리(pre-existing 포맷 미준수,
  이번 변경과 무관).

## 2026-07-21 — 테스트 속도·CI 계통 교정 (FIX-CI-TEMPLATE-001)

- **fix(ci/workflow)**: 3개 프로젝트 테스트 감사(`docs/test-speed-audit-*.md`)로
  실증된 계통 결함 4건 교정 — ① 표준 CI 블록 템플릿 신설
  (`docs/templates/ci-standard-block.yml`, 마커 블록만 SPECTER 소유·jobs는
  프로젝트 소유, PR 이중 실행/문서-전용 풀 CI/취소 부재 제거), ② `/ms.init`
  2.10 신설(멱등 식재) + 2.8 pre-commit fail-open 가드, ③ `/ms.review` 6.5 B2
  WARN 체크 2종(훅 실설치, RED 스캐폴딩 회수), ④ `quality-loop` 스킬 신설
  (판정-우선 9항목 감사 + 패턴 라이브러리 14종 시딩). ci.yml 전문은 sync
  비대상(영구 CONFLICT 방지) — 기존 프로젝트는 템플릿 절차로 1회 수동 이식.

# TODO

<!-- Add working notes here. -->

## 발행/릴리즈 기계화 — 남은 단계 (2026-07-24 갱신)

1차 구현·증거 수집·CI billing 정책 결정 완료(이력은 git history 참조).
**2026-07-24 구현 완료분** (커밋 6bd8a63·df7843e·a3b6343·fb308c5):

- 우회 방지: `verify-endstate` `false` 잔존 시 성공 보고 금지(fin 3.5 /
  merglease 1.5), Antigravity 부재 fallback 경로에도 헬퍼 강제.
- 2차: `specter-publish.sh ci-mode` + `review-cache write/changed` —
  생산자/소비자 단일 해시 계약(v2, git blob sha), 문서 전용 변경(`*.md`,
  `docs/`, `.specify/`)은 비무효화 확정, GNU 의존 제거.
- 3차: `self-review-stamp` — stdin 본문, COMMENT 전용, 콘텐츠 마커 dedupe,
  fail-open.
- 4차: `specter-release.sh classify-ci` — startup_failure/잡 0개/스텝 미실행
  +로그 부재만 billing_infra(자동 통과+경고 기록), 그 외 needs_human 정지.

남은 작업:

1. **5차 — 고위험 diff 탐지 하이브리드 (fin Step 1.5, 마지막)** — 진행 조건:
   위 구현분이 소비 프로젝트에서 안정 확인된 후. 스크립트 매치는 바닥(LLM
   제거 불가), LLM은 추가만. zero-match ≠ 의미 PASS 명시, 경로/컨텍스트
   규칙으로 오탐 억제, 바이너리/대용량은 "수동 스캔 필요" 표기, 민감 내용은
   마스킹 발췌만.
2. **suseonglm CI 다이어트 후속 관찰** — 다이어트는 2026-07-24 기준 적용됨
   (suseonglm 레포 측). 무료분 재소진 시에는 classify-ci의 billing_infra
   자동 통과가 가볍게 넘겨준다 — 재소진이 실제 발생하면 4차 패턴 적중률만
   점검.
3. **/ms.sync 전파** — 이번 구현분(커맨드 3종 + 스크립트 2종 + AGENTS.md
   재읽기 규칙 + §4 전역 라운드 상한)은 아직 이 레포에만 있음. 규율 변경
   (§4 상한)이 포함되므로 sync 전 압박 테스트 여부는 사용자 결정 대기.

### 별도 대형 과제 (트리거 대기)

- **재개형 실행기**: 체크포인트 기반 멱등 상태기계로 발행 시퀀스 지휘를 LLM에서
  분리. 첫 착수 근거 실측 확보됨(cueline v0.18.0 — verify-endstate가 태그
  오배치를 검출했으나 실행은 중단 없이 완료 선언).
- **위임 축소 여부**: Antigravity 오케스트레이터 유지 여부 재검토.

## docs/ 워크플로우 산출물 디렉토리 재편 (아이디어)

07-24 1차 청소로 최상위 산출물(리뷰 리포트·감사 노트 3종·insights)은 삭제됨.
구조 재편(예: `docs/features/<id>/` 아래로 산출물 집결)은 별도 결정 사항:

- `/ms.*` 커맨드별 산출 경로 전수 파악 후 생산자/소비자 쌍을 함께 이동
  (`docs/review/`는 /ms.review 산출 + /ms.fin PR 본문 + /ms.audit 입력).
- Feature 식별자 컨벤션(ID vs slug) 확정, fix 트랙(Feature 없음) 산출물 규칙 필요.

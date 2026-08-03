# Daily Log

<!-- Append dated entries here. -->

---

## 2026-07-24 — 발행/릴리즈 기계화 2~4차 + 우회 방지

- **fix(workflow)** `6bd8a63`: verify-endstate `false` 잔존 시 성공 보고 금지
  (fin Step 3.5 / merglease Step 1.5), Antigravity 부재 fallback 경로에도
  결정론 헬퍼 강제 — 2026-07-21 실측된 우회 2형태 봉쇄.
- **feat(publish)** `df7843e`: 2차 — CI-mode 결정을 `specter-publish.sh`로
  추출. `review-cache write/changed`(v2 캐시, git blob sha)로 /ms.review와
  /ms.fin이 단일 해시 계약 공유, 문서 전용 변경은 비무효화(불필요 CI 재실행
  버그 해소), GNU 의존 제거, 삭제 파일 감지 추가. 테스트 14개.
- **feat(publish)** `a3b6343`: 3차 — 셀프 리뷰 스탬프 스크립트화. stdin 본문,
  COMMENT 강제, 콘텐츠 마커 dedupe, 전 결과 fail-open JSON. 테스트 4개.
- **feat(release)** `fb308c5`: 4차 — `classify-ci` 결정론 CI 실패 분류.
  billing_infra는 구조 신호(startup_failure·잡 0개·스텝 미실행+로그 부재)
  한정, 해당 시 자동 통과+경고 기록(무료분 소진이 릴리즈를 막지 않음), 그 외
  needs_human 정지(fail-closed). 테스트 7개.
- 검증: 전체 스위트 243개 통과. 잔여: 5차(고위험 diff 하이브리드)는 안정
  확인 후, sync 전파는 사용자 결정 대기.

## 2026-08-03 — Feature Map staleness 범위 축소 (@CODE:FIX-GATE-SCOPE-001)

- 증상: Feature 사이클 도중 PRD/Feature Map을 수정하면 전역·per-Feature 체크리스트가
  동시에 stale 판정되어 pre-specter 체인을 다시 돌아야 했다. 원인은 두 바인딩 모두
  feature-map.md 파일 전체 해시를 보고 있었던 것.
- 수정(specter-gate.sh): 해시를 세 갈래로 분리했다. Feature 제목줄과 공용 내용은
  전역 뼈대(global_sha256), 각 Feature 본문은 해당 Feature 전용(scope_sha256).
  전역 체크리스트는 전역 뼈대에, per-Feature 체크리스트는 자기 섹션에 바인딩한다.
  verify/analyze 역의 입력 묶음도 같은 기준으로 좁혔다. `map-sha` 서브커맨드 신설,
  rev 2 → 3.
- 부수 수정: per-Feature staleness에만 없던 owner override 경로를 추가했다
  (feature-NNN.checklist.override.md, Mode=feature-override).
- 하위호환: 기존 체크리스트의 파일 전체 해시도 계속 인정한다(재생성 전까지).
- 문서: /ms.checklist·/ms.pre-verify가 map-sha 결과를 기록하도록 지시 변경.
- 검증: tests/specter 150개 통과(신규 11개 — 무관 섹션 수정 통과, 자기 섹션·공용부·
  Feature 추가는 FAIL 유지, override 3종, 레거시 바인딩 호환).

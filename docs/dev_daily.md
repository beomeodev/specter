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

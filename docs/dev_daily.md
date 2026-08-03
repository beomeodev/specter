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
- 독립 리뷰(Codex gpt-5.6-luna/high, Antigravity gemini-3.6-flash) 반영: 양측 FAIL →
  확정 결함 5건 수정. (1) 커밋 시점 백스톱 check_feature_map_gate.py가 여전히 파일
  전체 해시를 요구해 새 계약대로 기록하면 커밋이 막히던 문제 — 동일 분할을 파이썬으로
  포팅하고 쉘/파이썬 패리티 테스트로 묶었다. (2) pre-verify 입력 묶음이 전체 해시를
  써서 증상이 절반만 고쳐지던 문제. (3) 코드블록 안 '## '가 섹션을 끊던 문제와
  (4) 서로 다른 펜스 기호 중첩. (5) 지도에 없는 Feature 번호가 전역 뼈대 해시로
  조용히 통과하던 구멍 — map-sha와 게이트 양쪽에서 거부.
  반려 2건: Feature 본문 내 '## ' 하위제목(지도 형식은 '###'를 쓰며 구 게이트도 동일
  규약), override 필드 중복 검사(기존 global_override_valid와 동일 수준이며 위조에
  이미 저장소 쓰기 권한이 필요).
- 잔여 위험(설계상 의도): Feature 간 의존/계약을 특정 Feature 본문 안에만 적어두면
  그 수정이 의존 Feature를 stale 처리하지 않는다. 공유 계약은 지도의 공용 영역
  (첫 Feature 제목 이전 또는 별도 최상위 섹션)에 두어야 한다.
- 검증: make ci 전체 통과, tests/specter 162개.
- 2차 독립 리뷰(Codex) 반영: 재차 FAIL, 4건 전부 수정.
  (1) **앞선 "잔여 위험" 기록 정정** — 의존/DAG를 공용 영역에 두라고 적었으나,
  /ms.featuremap이 각 Feature 섹션에 Dependencies를 의무화하므로 그 지침은 지도
  형식과 모순이었다. 대신 모든 Feature의 `### Dependencies` 하위 섹션을 전역 뼈대에
  포함시켜, 의존 관계 수정은 항상 전역 구속이 되도록 했다. 일반 본문 수정은 그대로
  Feature 한정.
  (2) CRLF 지도에서 쉘(awk)과 파이썬 백스톱의 해시가 어긋나던 문제 — 백스톱이 text
  모드로 읽어 CRLF를 LF로 접었다. 바이트로 읽도록 변경하고, 레코드 분할(\n 한정)과
  말미 개행 부여 규칙을 awk와 일치시켰다.
  (3) map_has_feature가 펜스를 몰라, 코드블록 안의 가짜 Feature 제목을 실재로 인정하던
  문제 — 존재 검사와 분할이 같은 규칙을 쓰도록 통일.
  (4) 백틱 4개짜리 펜스가 안쪽 3개짜리 줄에 조기 종료되던 문제 — 여는 기호의 문자와
  길이를 기억하고 같은 문자가 그 이상 반복될 때만 닫는다.
- 패리티 행렬 10종으로 확장(CRLF, 말미 개행 없음, 4중 펜스, 펜스 속 가짜 제목,
  의존 섹션 등)하고 상황별 동작 테스트를 별도로 붙였다 — 패리티만으로는 두 구현이
  똑같이 틀린 경우를 못 잡는다.
- 검증: make ci 전체 통과, tests/specter 171개.
- 3차 독립 리뷰: agy PASS(결함 0), Codex FAIL(5건). 확정 2건 수정, 3건 반려.
  수정 (1) 파이썬 백스톱의 `\d`가 유니코드 십진 숫자까지 매칭해 awk의 `[0-9]`와
  갈라지던 문제 — 세 구현(쉘/백스톱/테스트 오라클)을 ASCII로 통일. 이번 변경이
  만든 결함. (2) per-Feature 체크리스트가 `**Feature Map**:`로 임의 파일을 지목하면
  그 파일 기준으로 바인딩을 검사해, 손대지 않은 사본을 가리켜 검사를 우회할 수 있던
  문제 — 정규 지도 외 경로는 거부. master에도 있던 기존 결함이나, 이번 변경이 세우려는
  무효화 보장을 정면으로 무력화하고 재작성한 블록 안이라 여기서 닫았다.
  반려 3건(모두 master 기존 결함이며 지도 범위와 무관, 별건 처리 대상):
  체크리스트 Feature 식별의 부분 문자열 일치(`Feature 0060`이 `006`을 통과),
  per-Feature Result 필드 중복 미검사, 리뷰어 리포트 Mode 값 미검증.
- 자체 검증 추가: 무작위 지도 3,000형태로 쉘/파이썬 패리티 퍼즈 — 불일치 0.
  실제 git 저장소에서 커밋 백스톱 4시나리오 실행 — 남의 Feature 수정만 통과,
  의존/공용표/Feature 추가는 차단.

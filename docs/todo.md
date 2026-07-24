# TODO

<!-- Add working notes here. -->

## 발행/릴리즈 기계화 — 남은 단계 (2026-07-24 정리)

1차 구현·증거 수집·CI billing 정책 결정은 완료(상세 이력은 git history의 본 파일
이전 버전 참조). 남은 작업과 진행 순서:

1. **우회 방지 수정 (선행 과제)** — 07-21 실측에서 발행 실행의 절반가량이
   스크립트(specter-publish.sh / specter-release.sh)를 거치지 않음. 조치:
   런타임 복사본 설치 확인, 스크립트 부재 시 정지 문구 강화, `verify-endstate`
   `false` 항목 존재 시 완료 선언 금지.
2. **2차 — CI-mode 결정 추출 (fin Step 2)** — 선행 조건: `review-hash.cache`
   생산자(/ms.review)/소비자(/ms.fin) 계약 불일치 정리(문서-전용 변경의 CI
   무효화 여부 결정 포함). 추가: GNU 도구 의존 제거, 특수 파일명 처리,
   케이퍼빌리티 프로브.
3. **3차 — 셀프 리뷰 스탬프 스크립트화 (fin task 5)** — 선행 조건 없음, 2차와
   같은 배치 가능. fail-open 유지, COMMENT 전용, 본문은 stdin/파일 전달,
   PR·레포 바인딩, 중복 제출 방지.
4. **4차 — CI 실패 분류 (merglease step 2, 목적 재정의됨)** — 무료분 소진
   상태에서는 billing/infra 실패 자동 무시(로컬 CI가 authoritative). 좁은
   패턴만 결정론 분류(시작 수 초 내 사망 + 로그 부재 + billing 메시지 동시
   충족), 그 외 전부 `UNCLASSIFIED` → 정지 후 사람 판단. 복구 1순위는
   suseonglm CI 다이어트(경로 필터·캐시·문서-전용 스킵·master-전용 무거운 잡
   분리 — suseonglm 레포 측 작업).
5. **5차 — 고위험 diff 탐지 하이브리드 (fin Step 1.5, 마지막)** — 스크립트
   매치는 바닥(LLM 제거 불가), LLM은 추가만. zero-match ≠ 의미 PASS 명시,
   경로/컨텍스트 규칙으로 오탐 억제, 바이너리/대용량은 "수동 스캔 필요" 표기,
   민감 내용은 마스킹 발췌만.

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

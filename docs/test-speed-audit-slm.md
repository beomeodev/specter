# 테스트 스위트 속도·건강 감사 보고서

- 작성일: 2026-07-21
- 기준 커밋: `0b0da64a` (master, working tree clean)
- 성격: **보고서 전용 감사 — 코드 변경 없음.** 조치 항목은 전부 후속 작업(/ms.fix 등)으로 라우팅할 것.
- 방법: 실측(전체/청크/부분 실행 타이밍) + 병렬 정밀 조사 3건(죽은 테스트 / 중복 커버리지 / 부트스트랩·병렬·캐시).
  상세 근거 문서는 세션 스크래치패드에 있으며 핵심 내용은 본 보고서에 통합함.

## 측정 환경 (결과 해석 전 필독)

| 항목 | 값 |
|---|---|
| 실행 환경 | OrbStack 리눅스 컨테이너, **cgroup 메모리 상한 8GB**, CPU 10코어 |
| 백엔드 실행 방식 | `cd backend && uv run pytest` (Python 3.11, venv 구축 완료 상태) |
| 환경변수 정리 | `CHAT_RERANKER_ENABLED`/`CHAT_RERANKER_RETRIEVAL_TOP_K`를 unset 하고 측정 (세션 셸에 오염되어 있었음 — 이 변수가 있으면 chat 테스트 3건이 위양성 실패) |
| 부하 조건 | 측정 중 다른 무거운 작업 배제. 단 공유 박스 특성상 ±10% 수준 편차 존재 (프론트엔드 2회차가 1회차보다 35% 느린 사례 참고) |

> 참고: 메모리 상한은 이 개발 컨테이너에 대한 것이며 mac mini 전체 RAM과는 별개다.
> 상한을 올리는 것은 OrbStack 설정에서 가능하나, 아래 §1의 근본 원인(특정 테스트의
> 실모델 로드)을 고치는 쪽이 우선이다.

---

## 1. 전체 실행 시간 (cold / warm)

### 1-1. 백엔드: 단일 프로세스 전체 실행은 **완주 불가** (최우선 발견)

`uv run pytest` (기본 설정 = 커버리지 포함) 전체 실행을 2회 시도, 2회 모두 **OOM SIGKILL(exit 137)** 로 사망:

| 시도 | 사망 지점 | 경과 시간 |
|---|---|---|
| 1회차 (에이전트 작업과 병행) | 진행률 ~10% | 3m 06s |
| 2회차 (부하 정리 후 단독 실행) | 진행률 ~38%, `tests/integration/test_archive_inflight.py` 직후 | 9m 47s |

**두 번 모두 같은 파일에서 죽었다.** 디렉토리별 청크 실행에서도 `tests/integration` 청크가
새 프로세스 시작 64초 만에 같은 지점에서 exit 137로 죽어, 누적 메모리 문제가 아니라
**단일 테스트의 메모리 폭식**임이 확인됐다.

**근본 원인 (스택트레이스로 확증):**
`tests/integration/test_archive_inflight.py`의 두 번째 테스트가 아카이브된 노트에 채팅
메시지를 보내는 시나리오를 실행하면서 `routers/chat.py:154 _build_embedder` →
`indexer/embedder/bgem3.py:44` 경로로 **진짜 SentenceTransformer(bge-m3) 모델을 로드**한다.
이 과정에서:

- `huggingface_hub.hf_hub_download`로 **테스트 중 실제 네트워크 다운로드**가 발생한다
  (모델 원본 2GB+; 로컬 HF 캐시는 193MB 부분 상태 — 매번 받다가 죽고, 다음 실행 때 또 받는다).
- torch + transformers + (CPU 핀에도 불구하고 로드되는) cuda.bindings + sklearn 계열이
  전부 메모리에 올라와 8GB 상한을 초과한다.

chat 도메인 테스트는 `tests/chat/conftest.py`가 임베더를 스텁으로 대체해 이 문제가 없지만,
이 파일은 `tests/integration/`에 있어 그 보호막 밖이다. **권장: 임베더/리랭커 스텁을
최상위 `tests/conftest.py`(autouse 또는 공용 픽스처)로 승격**하면 어느 디렉토리의 테스트도
실모델을 실수로 로드할 수 없게 된다.

> 파급: 로컬에서 전체 게이트를 완주할 수 없으므로, "전체 GREEN" 확인이 사실상 CI에만
> 의존한다. 그런데 최근 CI는 GitHub billing 문제로 실행되지 못하는 기간이 있었다
> (머지들이 admin override로 진행됨). 즉 **현시점 결정론적 전체 검증 경로가 없다.**
> §9의 로컬 baseline 실패 11건이 조용히 쌓인 배경으로 추정된다.

### 1-2. 백엔드: 디렉토리별 청크 실행 (커버리지 OFF, 순차)

전체 27청크 합산 **1,679초 ≈ 28분** (integration 청크는 사망 전 64초까지만 포함,
완주 시 총 29~30분 추정). 통과 규모: **약 4,360개 pass** (integration 제외).

상위 병목 (전체의 ~70%가 상위 7개 디렉토리):

| 디렉토리 | 시간 | 테스트 수 | 특징 |
|---|---|---|---|
| `tests/routers` | **6m 18s** | 512 | TestClient+DB 재생성 부트스트랩 밀집 (§7) |
| `tests/services` | 3m 38s | 478 | |
| `tests/exam_focus` | 1m 48s | 302 | |
| `tests/migrations` | 1m 36s | 215 | |
| `tests/qgen` | 1m 31s | 481 | |
| `tests/weakness` | 1m 24s | 189 | 기존 실패 6건 포함 (§9) |
| `tests/quiz` | 1m 18s | 195 | |
| (참고) `boundary`/`config`/`middleware`/`schemas` | 각 ≤2s | 94 | 순수 유닛 — 이 속도가 건강한 기준선 |

### 1-3. cold vs warm 차이

| 측정 | cold | warm | 차이 |
|---|---|---|---|
| 백엔드 pytest (`tests/kst`, `__pycache__`·`.pytest_cache` 삭제 후) | 70.5s | 68.0s | **~4% — 미미** |
| 백엔드 커버리지 세금 (`tests/kst`, warm 기준 cov ON vs OFF) | — | 73→68s | **cov가 +7%** |
| 프론트엔드 vitest 전체 (1,841 tests / 250 files) | 57.2s | 77.1s(!) | **캐시 효과 없음, 실행 편차 ±35%** |
| mypy --strict (백엔드 318파일) | 58.6s | 3.0s | **캐시 20배 효과 (정상 작동)** |
| tsc --noEmit (tsbuildinfo) | 13.7s | 4.8s | 증분 3배 효과 (정상 작동) |
| ruff check | 0.2s | 1.0s | 둘 다 1초 미만 — 논외 |
| eslint (`next lint`, `.next/cache/eslint`) | — | 5.9s | |

해석: 백엔드 테스트의 cold/warm 차이는 바이트코드 캐시 수준으로 미미하다. 진짜 cold
비용은 (a) 최초 venv/의존성 구축, (b) §1-1의 깨진 HF 모델 다운로드다. 프론트엔드는
vitest 캐시(`node_modules/.vite`)가 사실상 비어 있고(4KB) 효과도 없다 — 비용 내역상
jsdom 환경 생성(environment 184~223s 누적)이 지배적이라 transform 캐시로는 못 줄인다.

---

## 2. 죽은 테스트

### 2-1. 확정 dead — 삭제 권장 (판단 리스크 낮음, 총 20개 테스트)

| 위치 | 규모 | 근거 |
|---|---|---|
| `backend/tests/chat/integration/` 4개 파일 (`test_chat_concurrency_under_load` / `test_chat_send_quality_mode` / `test_chat_preference_endpoints` / `test_chat_quality_mode_confidentiality` 일부) | 11 tests | 033-D RED 스캐폴딩. 실제 구현은 커밋 `915fa6c5d`로 완료됐고 실커버리지는 `tests/chat/unit/test_chat_{concurrency,preferences,orchestrator_quality_mode}.py`(18개, 실행 확인 GREEN)와 `test_chat_send_sse_progress.py`에 존재. 남은 스텁 바디는 `raise AssertionError("RED — ...")`라 **영구히 GREEN 불가** |
| `frontend/tests/components/chat-composer-quality-mode.test.tsx` | 3 tests | 존재하지 않는 `ChatComposer` prop 전제. 기능은 `ChatPanel.tsx:155-175`에 다른 형태로 구현됨 |
| `frontend/tests/components/chat-sse-progress.test.tsx` (skip 2건만) | 2 tests | `useChatProgressState` 훅이 만들어진 적 없음 (repo 전체 0건). 같은 파일의 `consumeSSE` 테스트는 정상 |
| `frontend/tests/admin/uploads-page.test.tsx` | 4 tests | 스스로 "REMOVED"(재인덱싱 버튼, PR #97 제거) / "Phase H로 의미 변경"이라 라벨링 |

### 2-2. 갱신 누락으로 죽어가는 계약 테스트 (이번 실측에서 신규 발견)

`tests/chunker/integration/test_admin_sources_list.py::test_list_returns_all_rows_with_required_fields`
— 응답 키를 **정확 일치(strict set equality)** 로 고정해둔 계약 테스트인데, 이후 기능들이
추가한 5개 키(`drift`, `drift_reason`, `is_boundary`, `in_midterm_range`,
`midterm_boundary_source_id`)를 반영하지 않아 **현재 항상 실패**한다. 단독 실행으로도
재현(순서 문제 아님). "예전에는 유효했지만 지금은 유효하지 않은 테스트"의 전형.

### 2-3. questionable — 삭제 금지, 소유자 판단 필요

- `test_chat_quality_mode_confidentiality.py`의 `TestProgressConfidentiality` 2건:
  서버 사이드 stage 로그가 쿼리/청크/PII를 제외하는지 검증하는 테스트가 **repo 전체에서
  이 스킵된 2건뿐**. 죽은 게 아니라 **미완성 보안 커버리지 공백** — 삭제 대신 리라이트 권장.
- `mock-local-storage` 한계로 2026-05-07부터 스킵된 SecurityError 계열 5건
  (`pwa-install-modal` / `pwa-install-prompt` / `theme`): 약속된 "separate cleanup PR"이
  2.5개월째 없음. 커버리지 공백 실재 — 백로그 명시 이관 또는 GREEN화 필요.
- `test_no_group_leak_b_user.py:502-509`: 라우터가 이미 마운트돼 절대 안 걸리는
  404-스킵 분기 — 분기만 제거하면 되는 경미한 청소.

### 2-4. 오해 정정 (조사했으나 살아있는 것)

- weakness 엔진·KST 졸업 로직이 휴면이라는 기존 진단(2026-07-03 세션 기록)은 **stale** —
  Feature 068/069/073이 실배선 완료(`crontab.production`의 `*/15` weakness dispatch 확인).
  해당 테스트들은 현재 프로덕션 도달 가능 코드를 검증 중이다.
- "KST 토큰상한 9건 known-FAIL" 기록도 재현 불가 — `tests/kst/` 210개 전부 GREEN.
  실제 기존 실패는 weakness 6건이다(§9).
- mock/patch 문자열 타깃 26개 전수 대조 — 죽은 patch 타깃 0건.
- 프론트엔드 테스트의 import 전수 스캔 — 삭제된 컴포넌트 import 0건.

---

## 3. 중복 커버리지

### 3-1. CI 워크플로 레벨 (가장 확실하고 정량화된 낭비)

| 중복 | 내용 | 낭비 |
|---|---|---|
| confidentiality 2중 실행 | `backend` job이 전체 pytest(152개 포함 수집) 후 `pytest tests/confidentiality/`를 별도 스텝으로 재실행 (FR-CI-003 "UI 가시성" 목적) | 152 tests × 2, **같은 job 순차라 critical path 직접 증가** (로컬 실측 56s 상당) |
| ops 최대 3중 실행 | `ops-backend` job: 개별 파일 지정 스텝들(90개) → "collect-everything" `pytest tests/ops/`(116개, 90개 재포함). 여기에 `backend` job 전체 pytest가 같은 116개를 또 실행 | 90개 기준 최대 3회. 개선: collect-everything 스텝에 `--ignore` 적용 또는 개별 스텝 통합 |

### 3-2. 코드 레벨

- **라우터 vs 서비스 계층 이중 검증 (체계적, 중간 우선순위)**: 같은 검증 분기
  (404/409/422, risk-ack 누락, typed-model 불일치 등)를 서비스 유닛 테스트(직접 호출,
  경량)와 라우터 테스트(TestClient + DB 시딩, 테스트당 ~0.8s 부트스트랩)가 각각 재확인.
  표본 2쌍(`test_model_config_embedding_change`, `test_qgen_router/service`)에서만 10개+
  분기 쌍 확인, admin 도메인 27+27 파일 쌍에 걸쳐 반복 추정. 라우터 테스트가 §1-2의
  최대 병목(6m 18s)인 만큼, "예외→HTTP 코드 매핑은 분기당 1케이스만, 세부 분기는 서비스
  테스트에 위임" 원칙으로 정리하면 라우터 테스트 30~50% 절감 여지.
- 마이그레이션 보일러플레이트(`test_migration_runner_idempotent`/`file_exists` 5개 파일
  반복): parametrize로 통합 가능하나 절대 비용 미미 — 낮은 우선순위.
- **비이슈 판정**(조사했으나 중복 아님): `indexer_smoke` 2회 실행(in-memory vs 실컨테이너
  계약 검증, 문서화된 의도), `tests/a11y` vs `axe.test.tsx`(정적 수치 vs 런타임 DOM),
  `StudioQuizCard*` 8파일(상태별 분할), exam_focus/weakness 동명 파일(다른 도메인).

---

## 4. 프리커밋 / 프리푸시 훅

**"CI급 전체 테스트를 훅에서 돌리는" 문제는 없다. 반대로 로컬 방어선이 0이다.**

| 훅 | 상태 |
|---|---|
| `.pre-commit-config.yaml` | ruff / ruff-format / mypy / bandit / 공백류 — 구성은 존재하나 **`.git/hooks/pre-commit`이 없음 = 미설치, 아무것도 안 돎** |
| pre-push | git-lfs 전용 (테스트 없음) |
| post-commit | git-lfs + graphify 그래프 재빌드 (detached 백그라운드 — 커밋 블로킹 없음, 양호) |

메모: pre-commit을 설치한다면 지금 구성 그대로가 적절한 무게다(테스트 없음, 린트만).
단 mirrors-mypy 훅은 프로젝트 venv와 다른 격리 환경에서 돌므로 로컬 `uv run mypy`와
결과가 어긋날 수 있음 — 설치 시 검증 필요.

---

## 5. 변경 범위 기반 선택 실행

**없다. 그리고 현 설정은 선택 실행을 능동적으로 막는다.**

- `backend/pyproject.toml`의 `addopts`가 `--cov=src/suseonglm --cov-report=term-missing
  --cov-fail-under=85`를 **모든 실행에 강제**. 실증: `pytest tests/boundary` — 31개 전부
  통과, 3.5초 — 인데 "FAIL Required test coverage of 85% not reached. Total coverage:
  0.78%"로 게이트 실패. 즉 **작은 수정 후 관련 디렉토리만 돌리는 워크플로가 `--no-cov`를
  수동으로 붙이지 않는 한 항상 "실패"로 끝난다.**
- 같은 이유로 `--lf`(직전 실패만 재실행)/`--ff`도 봉인 상태. `.pytest_cache`에 `lastfailed`가
  없다는 점이 "아무도 못 쓰고 있음"을 방증.
- pytest-testmon / pytest-picked 류 변경-범위 도구 없음.
- CI는 `on: push: branches: ['**']` — **모든 브랜치 push마다 전체 스위트**. `paths` 필터,
  docs-only 스킵 없음. (frontend-only PR 가드 `git-diff-backend-empty`는 D2 브랜치 전용.)
- `-v`도 addopts에 박혀 있어 출력이 항상 장황하다 (로그 스캔 비용 증가).

권장 방향: 커버리지는 CI 스텝에서만 명시적으로 켜고(`pytest --cov ...`), 로컬 기본은
커버리지 없는 빠른 실행으로. 이 한 줄 변경이 선택 실행·`--lf`·`-k` 워크플로를 전부 해방한다.

---

## 6. 병렬 설정

### 백엔드: 병렬화 자체가 없음 (28분 순차)

`pytest-xdist` 미설치. 10코어 박스에서 CPU 1개로 28분. 지금 `-n auto`를 켜면 안 되는
구체적 걸림돌 (사전 정리 목록):

1. `BATCH_POLLER_LOCK_PATH` 기본값이 공유 고정 경로(`$TMPDIR/test_batch_poller.lock`,
   `tests/conftest.py:42-45,76-77`) — `INDEXER_LOCK_PATH`는 이미 per-test 유니크로 고쳐졌는데
   이것만 비대칭. flock 경합 오탐 위험.
2. `dashboard/cache.py`의 모듈 전역 TTLCache 7개 + `_BLOCK_CACHE` + cost `_summary_cache`가
   autouse 초기화 없이 **수동 `clear_all_caches()` 호출 관행**에 의존 — 순서 재배치에 취약.
3. 앱 import 7.56s(cold, scipy.stats 2.85s + qdrant_client 1.38s 주범)가 **워커당 반복 지불**됨.
4. `--cov-fail-under` + xdist 조합은 coverage combine 검증 필요 (§5 해소가 선행되면 무관).
5. sleep 기반 타이밍 테스트 소수(스레드 레이스 유도, JWT exp 1초 해상도)가 flaky화 가능.

걸림돌 1·2는 작은 수정이고 3~5는 수용 가능한 수준 — **정리 후 xdist 도입 시 이 스위트의
최대 단일 속도 개선**(순차 28분 → 코어 활용 시 수 분대 기대)이다.

### 프론트엔드: 경합 사고 이력 있음, 현재는 우회 상태

`vitest.config.ts`에 문서화된 실사고: 기본 `threads` 풀에서 SWC 변환기의 공유 상태 레이스로
한글 JSX 파일 206/219개가 파싱 실패 → `pool: "forks"`(프로세스 격리)로 전환해 해결.
`maxWorkers`/`isolate`는 기본값. 추가 경합 흔적 없음. (개선 여지: `tests/setup.ts`가 순수
폴리필이라 `isolate: false` 실험 가치 있음 — 파일당 셋업 재실행 44ms × 250파일 절감. 단
전역 상태 오염 여부 개별 검증 후.)

### 부산물 발견: gpg-agent 데몬 누수

`tests/ops/unit/test_crypto.py`가 테스트별 GNUPGHOME으로 띄운 **gpg-agent 데몬들이 테스트
종료 후에도 잔존**(측정 중 3개 확인). 반복 실행 시 누적되어 8GB 상한을 갉아먹는다.
teardown에서 `gpgconf --kill gpg-agent` 권장.

---

## 7. 테스트 간 중복 부트스트래핑

**백엔드 스위트가 느린 실질적 1등 원인.** 실측 기반:

| 패턴 | 비용 | 규모 |
|---|---|---|
| `tmp_db` (최상위 conftest:86-93): 함수 스코프로 **매 테스트마다 마이그레이션 SQL 64개 전체 재생** | **0.57s/호출** | 직접 사용 101+ 파일 (간접 체이닝 포함 시 더 큼) |
| `create_app()` + TestClient: 매 테스트 전체 앱 재구성, lifespan이 **이미 마이그레이션된 DB에 `run_migrations()` 재실행** (`main.py:124-125`) | 0.21s/호출 + DB 왕복 | 112 파일 |
| `admin_client`/`non_admin_client`: `tmp_db` + `create_app` + 사용자 INSERT + 실 HTTP 로그인까지 매 테스트 | **~0.8s/테스트** | routers/admin·indexer/integration 트리 27파일 |

- 이 구조가 §1-2의 병목 순위(routers 6m18s, services 3m38s)와 정확히 일치한다.
- **모범 사례가 이미 사내에 있다**: `tests/dashboard/conftest.py:541-566`은 `:memory:`
  SQLite에 직접 스키마+시드를 넣고 "<50ms per call"을 주석으로 명시 — `tmp_db` 대비 10배+
  저렴. 개선안: (a) 마이그레이션을 세션 스코프에서 1회만 적용한 **템플릿 DB를 만들어 파일
  복사**로 배포(0.57s → 수십 ms), (b) lifespan의 중복 migration 재검사 스킵.
- **conftest 복붙 3벌**: `admin_client`/`non_admin_client` 로직이
  `tests/routers/admin/conftest.py`, `tests/indexer/integration/conftest.py`,
  (유사변형) `tests/chat/conftest.py`에 병존. 최상위 conftest에 승격 관행이 이미 있는데
  (conftest.py:113-117 주석) 이 계열만 예외.
- 프론트엔드 `tests/setup.ts` 자체는 가볍지만(fake-indexeddb 44ms 등) `isolate: true`
  기본값으로 **250파일 × 매번 재실행** — §6의 isolate 실험 항목과 동일 사안.

---

## 8. 캐시 활용도

| 캐시 | 상태 | 실효성 |
|---|---|---|
| mypy `.mypy_cache` (142M) | 정상 작동 | **cold 58.6s → warm 3.0s (20배). 잘 되고 있음** |
| tsc `tsconfig.tsbuildinfo` (`incremental: true`) | 정상 작동 | 13.7s → 4.8s (3배) |
| eslint (`.next/cache/eslint`) | 존재 | 5.9s 수준 |
| ruff `.ruff_cache` | 존재 | 어차피 1초 미만 — 무의미하게 양호 |
| pytest `.pytest_cache` | 존재하나 **사장** | `--lf`/`--ff`가 §5의 cov 게이트에 막혀 실사용 흔적 없음 (`lastfailed` 부재) |
| vitest `node_modules/.vite` | 4KB — 사실상 빈 껍데기 | 실측 재실행 이득 0 (오히려 2회차가 느렸음). jsdom 환경 비용이 지배적이라 transform 캐시로는 못 줄이는 구조 |
| HuggingFace `~/.cache/huggingface` (193M) | **깨진 상태** | §1-1의 OOM 테스트가 매 실행 2GB+ 모델을 받다 죽어 캐시가 영구 부분 상태 — 실행마다 네트워크 낭비 재발 |
| `.next/cache` (232M, webpack) | 빌드용 | 테스트 경로와 무관, 정상 |
| CI 캐시 | `actions/setup-node`의 npm 캐시만 사용. **백엔드 uv 의존성·mypy 캐시는 CI에서 매번 cold** | `astral-sh/setup-uv`의 캐시 옵션 또는 actions/cache 도입 여지 |

---

## 9. (부수 발견) 로컬 baseline 적자 — master가 로컬에서 GREEN이 아님

이번 실측에서 clean master 기준 **11건 실패**를 확인했다 (전부 단독 실행으로도 재현 —
순서/격리 문제 아님):

| 그룹 | 건수 | 시그니처 |
|---|---|---|
| `tests/weakness/integration` | 6 | `EmptyPoolError: no_unsolved_questions` + 시드 수 불일치 (기존 기록과 일치하는 유일한 baseline) |
| `tests/group` | 3 | 2건은 같은 EmptyPool 계열(`assert 0 == 5`), 1건은 **불변식 위반 실검출**: `dashboard/group_performance.py:291`이 `is_admin`+`group_label`을 한 쿼리에서 결합 — FR-INJ-002/FR-ADMIN-011 가드 테스트가 잡아냄 |
| `tests/chunker` | 1 | §2-2의 계약 테스트 미갱신 |
| `tests/routers` | 1 | `test_pool_byte_identical_snapshot_076` 스냅샷 불일치 — Feature 076 계약 회귀 여부 확인 필요 |

CI가 billing으로 멎어 있던 기간 + 로컬 전체 실행 불가(§1-1)가 겹쳐 이 적자가 조용히
쌓인 것으로 보인다. **속도 개선과 별개로, baseline을 0으로 되돌리는 /ms.fix 트랙이
선행되어야 "전체 GREEN"이라는 신호 자체가 의미를 되찾는다.**

---

## 10. 권장 조치 우선순위 (전부 후속 작업 — 본 감사에서는 미실행)

| 순위 | 조치 | 기대 효과 |
|---|---|---|
| P0 | `test_archive_inflight.py` 실모델 로드 차단 — 임베더/리랭커 스텁을 최상위 conftest로 승격 | 로컬 전체 스위트 완주 가능화 + 테스트 중 네트워크 다운로드 제거 |
| P0 | `addopts`에서 `--cov`/`--cov-fail-under` 제거(커버리지는 CI 스텝 플래그로 이동), `-v`도 제거 검토 | 선택 실행·`--lf`·`-k` 해방, 매 실행 +7% 세금 제거 |
| P1 | baseline 11건 실패 분류·수정 (/ms.fix; 특히 group_performance 불변식 위반과 076 스냅샷은 실회귀 가능성) | "전체 GREEN" 신호 복원 |
| P1 | `tmp_db` 세션 스코프 템플릿 DB + lifespan 중복 마이그레이션 스킵 | 최대 병목(routers 6m18s 등) 직접 타격 — 스위트 수 분 단축 추정 |
| P1 | CI 중복 제거: confidentiality 재실행 스텝, ops collect-everything `--ignore` | CI critical path 단축 (분 단위) |
| P2 | xdist 도입 (선행: BATCH_POLLER_LOCK_PATH per-test화, dashboard 캐시 autouse clear) | 순차 28분 → 수 분대 (10코어) |
| P2 | dead 테스트 20개 삭제 + questionable 2건 리라이트 판단 (§2) | 유지보수 소음 제거, 보안 커버리지 공백 해소 |
| P3 | pre-commit 훅 실제 설치, gpg-agent teardown, vitest `isolate:false` 실험, scipy 지연 import, CI uv 캐시 | 각각 소폭 |

## 부록: 측정 원자료 위치

- 청크별 타이밍 로그·실패 출력: 세션 스크래치패드 `chunk-times.log`, `chunk-*.out`
- OOM 스택트레이스: 스크래치패드 `oom-hunt.out`
- 정밀 조사 보고서 3건: `dead-tests.md`, `duplicate-coverage.md`, `bootstrap-parallel-cache.md`
  (스크래치패드는 세션 종료 시 소멸 — 본 보고서에 핵심을 전부 반영함)

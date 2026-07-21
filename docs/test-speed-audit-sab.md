# 테스트 스위트 속도·건강 감사 보고서 (SAB)

- 작성일: 2026-07-21
- 기준 커밋: `c6753a9` (master, clean)
- 측정 환경: 로컬 devcontainer, 10코어, Python 3.14, uv 관리 venv
- 성격: **읽기 전용 감사** — 코드 변경 없음. 예상 절감치는 측정값 기반 추정이며 적용 전 재측정 필요.

---

## 요약 (TL;DR)

| # | 항목 | 판정 | 핵심 수치 |
|---|------|------|-----------|
| 1 | 전체 실행 시간 | 주의 | cold 134.1s vs warm 131.5s — **캐시 효과 사실상 0 (2%)** |
| 2 | 죽은 테스트 | 양호 | 실질적 죽은 테스트 없음 (skip/xfail 0건, 참조 심볼 전부 존재) |
| 3 | 중복 커버리지 | 개선 여지 | 값비싼 상위집합 중복 2쌍 + function-scope E2E fixture로 미니 백테스트 ~30회 반복 |
| 4 | 커밋 훅 | 양호 | pre-commit만 설치, pytest 없음. 정상 상태 1.6s (최초 1회만 32s) |
| 5 | 변경 범위 선택 실행 | 없음 | 선택 실행 메커니즘 전무 — 한 줄 고쳐도 항상 765개 전체 |
| 6 | 병렬 설정 | 없음 (기회) | xdist 미설치, 완전 직렬. 경합 흔적 없음, 도입 장벽 낮음 |
| 7 | 중복 부트스트래핑 | 개선 여지 | 캘린더 schedule 재생성 ~7–13s, run_backtest 본문 35회 ≈ 25s |
| 8 | 캐시 활용 | 부분 실패 | pytest 캐시 무의미, mypy 캐시는 유효하나 무효화 상태 방치(45.8s), CI는 캐시 0 |
| 9 | GitHub Actions | **전면 고장** | 7월 118회 실행 **전부 결제 문제로 2–5초 내 실패** (잡 시작조차 안 됨) |

**최대 기회 3개** (예상 절감, 중첩 고려 전 개별치):
1. pytest-xdist 도입 (`-n auto`): 134s → 추정 35–50s (**60–70% 절감**) — 파일 쓰기 격리는 이미 xdist-safe, 차단 요소는 중첩 프로세스풀 테스트 2건 격리뿐.
2. 캘린더 스케줄 메모이즈(`backend/data/calendar.py`에 `lru_cache` 한 줄): **7–13s 절감**.
3. E2E fixture module-scope 전환(`test_e2e_phase4.py`, `test_cli_guard_e2e.py`): 미니 백테스트 ~30회 → ~6회, **15–20s 절감**.

**건강 이슈 최우선 1개**: `network` 마커 테스트 4건(파일 3개)이 "기본 스킵"이라는 자체 문서와 달리 **매 실행마다 라이브 네트워크를 탄다** (`-m "not network"` 필터가 어디에도 없음). 최다 소요 테스트 1위(7.4s, 실 yfinance)가 여기 포함되며, 이 레포는 yfinance rate-limit 장애 이력(PR #24)이 있는 프로젝트다.

---

## 1. 전체 테스트 실행 시간 (cold vs warm)

측정 명령: `uv run pytest -q` (수집 765개 테스트, 125개 파일). cold는 `.pytest_cache`·`.coverage*`·프로젝트 트리 `__pycache__` 삭제 후 실행.

| 실행 | pytest 보고 시간 | wall clock (`time`) | 비고 |
|------|------------------|---------------------|------|
| 수집만 (`--collect-only`, cold) | 7.56s | 9.45s | 수집만으로 7.5초 — 아래 참고 |
| cold 전체 | 134.13s | 2m16.3s | 765 passed, 308 warnings |
| warm 전체 | 131.47s | 2m13.8s | **cold 대비 −2.7s (≈2%)** |
| CI 방식 (`--cov=backend`, ci-test와 동일) | 128.65s | 2m10.8s | 커버리지 오버헤드 ≈ **0** (warm 대비 −2.8s, 측정 노이즈 범위 — Python 3.14 + coverage의 sys.monitoring 계측 덕. 커버리지 총 94.45%, 게이트 85% 통과) |

해석:
- **cold/warm 차이가 2%뿐** = 이 스위트에는 실행 시간을 줄여주는 캐시가 사실상 없다. 차이는 파이썬 바이트코드(`__pycache__`) 재컴파일분이 전부. 매 실행이 정가(full price)다.
- 수집 7.56초의 주요인은 무거운 모듈 임포트: `import metrics`(동결 레거시)가 단독 **3.56s** (scipy·sklearn·matplotlib 체인, `pyproject.toml`의 Feature 011 주석이 module-level 요구를 명시). `backend/report/metrics_adapter.py`가 `import metrics`를 하므로 report 계열 테스트 수집 시 매번 로드된다. 참고로 `import backend` 자체는 0.12s.
- CPU 프로파일: user 1m58s ≈ wall 2m14s → **단일 코어에 묶인 CPU-bound 직렬 실행**. 10코어 머신에서 9코어가 논다. 병렬화 시 스케일링 여지가 크다는 뜻 (§6).
- 최다 소요 테스트 (`--durations` 상위): `tests/strategy/test_e2e_phase1.py::test_phase1_e2e_golden_parity_and_truncation` 7.39s, `tests/sweep/test_parallel_correctness.py::test_real_process_pool_workers_gt_1_completes` 5.95s, `tests/report/test_e2e_mini_universe.py` setup 5.13s, 이후 `test_e2e_phase4.py`·`test_cli_guard_e2e.py`의 **setup이 2.5–4.2s로 도배** — §7의 fixture 반복 실행 문제와 직결.

---

## 2. 죽은 테스트

**결론: 실질적 죽은 테스트 없음.** 이 스위트는 이 항목에서는 건강하다.

- `pytest.mark.skip` / `xfail` / `pytest.skip(` 사용 **0건** (`grep -rn` 확인). 등록 마커는 `network` 하나뿐 (`pyproject.toml:63`).
- 테스트가 참조하는 backend 심볼 전수 확인 결과 전부 현존: `missing_symbols`·`partial_symbols`(`backend/backtest/runner.py` 등), `_drop_null_ohlcv_rows`, `assert_no_leverage`, `is_in_cooldown`, `CONTAMINATION_MARKER`, `adopt_provisional`, `exit_efficiency`, `coverage_report`(커밋 `ccdc02e`에서 CLI 노출) 등.
- 이름이 의심스러운 테스트도 검증 결과 유효한 회귀 가드:
  - `tests/backtest/test_review_fixes.py` — 008 리뷰 수정의 회귀 가드, 현행 경로 실행.
  - `tests/report/test_render.py:67` — `HtmlRenderUnavailable` 발생을 assert하는 현행 계약.
  - `tests/report/test_determinism.py:109` — 동결 `metrics.py:1687`의 `analysis_date`를 어댑터 경계에서 제거함을 바이트 비교로 검증.
- 타우톨로지(`assert True`, mock 자기참조) **0건**. `tests/report/test_render.py:106`의 `assert not writer_called`는 정당한 음성 검증.

**단, 인접한 건강 이슈 하나 (중요)** — "죽은 테스트"의 반대인 "죽어야 할 때 안 죽는 테스트":
- `tests/universe/test_membership_live.py:2`의 독스트링은 "network 마커 — **기본 스킵**"이라 주장하지만, `addopts`(`pyproject.toml:62`)는 `-v`뿐이고 `-m "not network"`는 **레포 어디에도 없다** (Makefile ci-test, ci.yml 포함 grep 0건).
- 따라서 network 마커 테스트가 **매 실행 라이브로 돈다**: `tests/universe/test_membership_live.py:18`(실 Wikipedia HTTP, 측정 2.34s), `tests/data/test_adjustment.py:37,46`, `tests/strategy/test_e2e_phase1.py:22`(`pytestmark` — 파일 전체, 실 yfinance, 최다 소요 7.39s).
- 위험: 이 레포는 yfinance rate-limit로 인한 장애 이력이 있고(직전 PR #24가 그 수정), Wikipedia/야후가 느리거나 막히면 로컬 CI 게이트 전체가 흔들린다. 예상 효과: `-m "not network"`를 기본으로 하면 **약 12s 절감 + 외부 의존 플래키니스 제거** (network 테스트는 별도 명시 실행).

---

## 3. 중복 커버리지

판정 원칙: Constitution IX(#2 look-ahead, #3 결정론, #4 격리)가 **feature별로 강제하는 불변식 테스트**(각 모듈의 determinism/truncation/isolation)는 서로 다른 함수·경로를 검증하므로 중복이 아니다 — 이 부류는 전수 확인 후 정당 판정. 아래는 "동일 코드 경로 + 동일/유사 입력 + 동일 assert"인 실질 중복만.

### 3.1 [값비쌈] 무레버리지 익스포저 불변식 — 상위집합 중복
- `tests/backtest/test_exposure.py:30` `test_run_holds_exposure_every_bar` ⊂ `tests/backtest/test_e2e_phase2.py:42` `test_e2e_artifacts_wellformed_and_exposure`(본문 60–67행).
- 둘 다 `run_backtest(load_run_config("configs/backtest.mini.yaml"), ...)` 동일 config·동일 합성 소스로 풀 실행 후 매 바 cash/exposure를 assert. 후자는 positions×종가로 **독립 재계산**까지 하므로 전자를 엄밀히 포섭.
- 절감: 미니 백테스트 1회분(~0.7s). 단 `test_exposure.py:19,25`의 `assert_no_leverage` 순수 단위 테스트 2건은 고유하므로 유지 대상.

### 3.2 [값비쌈] 리포트 가드 증거 — 값 주입 vs 원장 파생
- `tests/research/test_e2e_phase4.py:188,212` (build_verdict_report에 trial_count/kofn **값 직접 주입**) ⊂ `tests/report/test_cli_guard_e2e.py:150` (실제 원장에서 CLI가 **파생** — 이 파일 독스트링 `test_cli_guard_e2e.py:6`이 "값을 꽂아 우회하는 기존 E2E가 놓친 지점"이라고 스스로 명시).
- phase4 쪽의 sweep 누적(:134)·OOS 예산(:202)·DSR 게이트(:234,:244)는 고유 슬라이스라 유지.
- 절감: 중복 테스트 2건 × fixture 백테스트 3회 = 미니 백테스트 6회분.

### 3.3 [구조적 — 최대 절감처] function-scope E2E fixture의 파이프라인 반복
- `tests/research/test_e2e_phase4.py:105` `e2e_ctx`와 `tests/report/test_cli_guard_e2e.py:95` `cli_ctx`가 **function scope**라 테스트 하나마다 미니 백테스트 3회(SPADE+baseline_a+baseline_b)를 재실행 → 합계 **~30회+**. §1의 durations 상위권을 도배한 2.5–4.2s setup들이 정확히 이것.
- 동일 패턴의 `tests/report/test_e2e_mini_universe.py:63` `e2e_report`는 이미 **module scope**로 1회 실행을 11개 테스트가 공유 — 모범 사례가 같은 리포에 이미 있다.
- 예상 절감: ~30회 → ~6회, **15–20s**.

### 3.4 [낮음] 기타
- 아티팩트 형상: `tests/backtest/test_e2e_phase2.py:51–56`은 `tests/backtest/test_artifacts.py:72–125`의 경량 부분집합 (절감 미미, E2E 성격상 유지 타당).
- 코어 격리 import 스캔: 집계(`tests/backtest/test_isolation.py:22`)와 모듈별 6개 파일이 같은 패키지를 두 번 정적 스캔 — 실질 중복이나 비용 ≈ 0 (마이크로초), IX#4 mandated라 삭제 권고 아님.

---

## 4. 프리커밋/프리푸시 훅

**결론: CI급 전체 테스트는 훅에 없다. 이 항목은 양호.**

- 설치된 훅: `.git/hooks/pre-commit` 하나뿐 (pre-push 없음).
- 구성(`.pre-commit-config.yaml`): ruff, ruff-format, mypy(mirrors-mypy v1.18.2), bandit(`-r backend`, `pass_filenames: false` — 항상 backend 전체 스캔), 파일 위생 3종, SPECTER 로컬 스크립트 2종(`always_run`).
- **pytest는 훅에 없음** — 커밋마다 2분짜리 스위트를 돌리는 함정은 피해가 있다.
- 실측 (단일 파일 `backend/backtest/config.py` 대상):

| 측정 | 시간 |
|------|------|
| `pre-commit run --files ...` 최초 1회 | **31.99s** (mirrors-mypy의 자체 mypy 캐시 첫 빌드) |
| 동일 명령 정상 상태 | **1.63s** |
| 훅별 정상 상태: ruff / mypy / bandit | 0.48s / 0.66s / 0.60s |
| SPECTER 스크립트: tag_chain / feature_map_gate | 0.11s / 0.04s |

- 주의점 2개 (차단급 아님):
  1. **mypy 이중 설치**: 로컬 dev 의존성 mypy와 mirrors-mypy(1.18.2)가 별도 환경·별도 캐시를 유지 — 버전·의존성(additional_dependencies가 실제 의존성의 부분집합)이 달라 판정이 어긋날 수 있다. 알려진 사례: CI mypy는 `backend/`만 보는데 훅 mypy는 변경된 `tests/` 파일도 본다 (과거 `tests/__init__.py` 이슈로 실제 발생).
  2. bandit이 파일 1개 커밋에도 backend 전체를 스캔하지만 실측 0.6s라 현재 규모에선 무해.

---

## 5. 변경 범위 기반 선택 실행

**결론: 전무. 한 줄 수정에도 항상 765개 전체가 돈다.**

- `pytest-testmon`/`pytest-xdist`/증분 도구 없음 — `pyproject.toml` dev 그룹과 `uv.lock` grep(`xdist|testmon|execnet`) 0건.
- `scripts/`에 테스트 선택 스크립트 없음.
- 전체 스위트 호출 지점: `.devcontainer/Makefile:214`(`test:` → `pytest -q`), `.devcontainer/Makefile:289–290`(`ci-test:` → `pytest -v --cov=backend --cov-report=term-missing`), `.github/workflows/ci.yml:26–27`(위 ci-test 경유), `pyproject.toml:62`(`testpaths=["tests"]`, 선택 옵션 없음).
- CI 경로 필터도 없음 (§9).
- 체감: 로컬 게이트(`make -C .devcontainer ci`)의 지배 항은 pytest 2분 14초 + (캐시 무효 시) mypy 46초 — **문서 오타 수정에도 3분**이다.
- 방향(참고): 최소 침습은 (a) Makefile에 `ci-test-fast`(변경 모듈 대응 tests/<pkg>만) 추가, (b) testmon 도입, (c) xdist로 전체 실행 자체를 싸게 만들기. 이 레포는 모듈 경계(tests/<pkg> ↔ backend/<pkg>)가 깔끔해 (a)의 매핑 비용이 낮은 편.

---

## 6. 병렬 설정

**결론: 병렬성 과다가 아니라 병렬성 0이 문제. 경합·플래키 흔적은 없음.**

- xdist/pytest-parallel 미설치, `addopts`에 `-n`/`--dist` 없음 → 완전 직렬 (§1: user≈wall로 실증).
- 경합/플래키 흔적 조사: `time.sleep`/`flaky`/`rerun` 데코레이터 **0건**. `tests/sweep/test_parallel_correctness.py:119`의 `release.wait(step)`은 sleep 대용 이벤트 대기로 타이밍 의존 최소화된 정상 패턴.
- 테스트 내부 프로세스 스폰 2건 (직렬 실행에선 무해, xdist 도입 시 격리 필요):
  - `tests/sweep/test_parallel_correctness.py:155` — `workers=2`로 실제 `ProcessPoolExecutor` 스폰 (`backend/sweep/runner.py:138`).
  - `tests/data/test_cache.py:99` — `ProcessPoolExecutor(max_workers=4)` 동시 쓰기 검증.
- **xdist 도입 안전성 사전 조사 결과 (장벽 낮음)**:
  - 산출물 쓰기는 전부 `tmp_path`/`tmp_path_factory` 하위. 리포 루트 쓰기·`chdir`·`getcwd` 사용 0건.
  - configs는 읽기 전용 공유만 (`tests/baseline/test_strategy_select.py:57–59` 등).
  - `tool.coverage.run.parallel = true`(`pyproject.toml:75`)가 이미 설정돼 커버리지 병합도 준비됨.
  - 필요 작업: 위 프로세스풀 테스트 2건을 직렬 그룹(`xdist_group`) 격리 + 최다 소요 E2E들의 분배 균형 확인.
- 예상 절감: 10코어에서 `-n auto` 시 134s → **추정 35–50s** (완벽 스케일은 아님 — 7.4s급 단일 테스트가 하한, 워커당 임포트 비용 ~3s×N 추가). 단일 최대 절감 항목.

---

## 7. 테스트 간 중복 부트스트래핑

- **캘린더 (가장 값싼 개선)**: `backend/data/calendar.py:44–48` `_sessions()`의 `.schedule()` 생성이 **0.18–0.35s/회**인데 캐싱이 전혀 없고, `run_sweep` 프리플라이트(`backend/sweep/runner.py:59`)가 매 호출 새 `TradingCalendar`를 만든다. 테스트 본문의 `run_sweep` 호출 39회가 combo 실행은 fake로 패치해도(`tests/sweep/conftest.py:77`) **프리플라이트 캘린더는 매번 실제 생성** (`tests/sweep/test_preflight.py:100–114`가 해당 경로 경유를 spy로 입증). 합계 **~7–13s**. `lru_cache` 한 줄 수준의 개선.
- **파이프라인 재실행**: `run_backtest()` 테스트 본문 호출 35회 × 실측 0.706s/회 ≈ **25s**. 결정론 검증용 이중 실행(예: `tests/baseline/test_e2e_determinism.py:39–40,48–49`)은 재실행이 본질이라 정당하지만, 같은 파일 내 나머지 반복(:56,66,81,95,118 등 9회 중 5회)과 `tests/backtest/test_review_fixes.py`의 8회 중 6회는 module-scope 공유 실행으로 대체 가능. §3.3과 합쳐 **10–15s**.
- **fixture 스코프**: 리포 전체에서 `scope=` 지정은 `tests/report/test_e2e_mini_universe.py:63` **단 1곳**. `synthetic_source`/`membership`/`sectors`(`tests/backtest/conftest.py:106–118`)와 각 conftest의 `cfg`(YAML 파싱)는 읽기 전용(+`.copy()` 반환으로 공유 안전, `tests/backtest/conftest.py:89`)이라 session 승격 가능 — 절감은 <1s로 작지만 공짜.
- **합성 OHLCV 생성기 3벌 복붙**: `tests/strategy/conftest.py:19–32`, `tests/signal/conftest.py:32–78`, `tests/backtest/conftest.py:41–62` — 같은 numpy 랜덤워크 패턴의 중복 구현. 속도보다 유지보수 이슈. 반면 `tests/sweep/conftest.py:21`·`tests/research/conftest.py`는 008 픽스처를 import해 재사용하는 모범 사례.

---

## 8. 캐시 활용도

| 캐시 | 상태 | 실측 |
|------|------|------|
| pytest (`.pytest_cache`) | 실행시간에 무영향 | cold 134.1s vs warm 131.5s. lastfailed/실행순서용일 뿐 |
| 바이트코드 (`__pycache__`) | 정상 | cold/warm 차이 2.7s가 이것 |
| mypy (`.mypy_cache`, 109MB) | **유효하나 방치됨** | 감사 시작 시점에 통째로 무효화 상태 → 첫 실행 **45.8s** (재빌드), 직후 재실행 **1.4s**. 무효화 원인: 로컬 mypy와 pre-commit mirrors-mypy(1.18.2)가 서로 다른 버전으로 같은 캐시 디렉터리에 버전별 서브캐시를 각각 유지 + 버전 변경 시 전체 재빌드 |
| ruff (`.ruff_cache`) | 정상 | warm 0.06s |
| pre-commit 환경 (`~/.cache/pre-commit`, 191MB) | 정상 | 환경 재빌드 없음, 정상 상태 1.6s |
| uv (`~/.cache/uv`) | 사실상 빈 캐시 (12KB) | 컨테이너 빌드 시 별도 경로로 설치된 듯 — 로컬에선 문제 없음 |
| **CI (GitHub Actions)** | **캐시 0** | `ci.yml`에 `actions/cache` 없음, `setup-uv@v5`에 `enable-cache` 명시 없음. 잡이 실제로 돌게 되면 매 실행 uv sync 풀 다운로드 + mypy 풀 콜드(≈로컬 45.8s 상당)를 정가로 지불하게 됨 |

핵심: 로컬 캐시는 "있는데 이득이 없는" 구조(pytest)거나 "있는데 무효화로 새는" 구조(mypy). 테스트 실행 자체를 줄여주는 캐시(예: testmon, 데이터 fixture 캐시)는 없다.

---

## 9. GitHub Actions 워크플로우 구조·비용

### 구조
- 워크플로우 **1개** (`.github/workflows/ci.yml`), 잡 **1개** (`ci`, ubuntu-latest).
- 스텝: checkout → setup-uv@v5 → `uv python install 3.14` → `uv sync --all-groups` → `uv run make -C .devcontainer ci` (= ruff + mypy + **pytest 전체+커버리지**).
- 트리거: `push: branches: ['**']` (**모든 브랜치 모든 push**) + `pull_request`(master/main 대상). **경로 필터 없음, 문서-전용 스킵 없음, concurrency 취소 없음.**

### 실측: 현재 전 실행이 시작 전 사망
- 최근 100회 전수 확인: **모든 run이 2–5초 만에 failure**, 스텝 목록이 빈 채로 종료.
- 원인 (잡 어노테이션 원문): *"The job was not started because recent account payments have failed or your spending limit needs to be increased"* — **결제 실패/지출 한도 문제로 잡이 시작조차 안 됨.**
- 실행 횟수: **2026-07에만 118회** (7/21 기준, push 73 + pull_request 27 비율의 표본 기준 약 7:3), 2025-10 36회, 2025-09 5회.
- 현재 청구 분수: **0분** (잡이 러너에 배정되기 전에 죽으므로 과금 없음). 대신 모든 커밋·PR에 빨간 X가 찍히는 **음(−)의 신호 가치**만 남는다 — 로컬 `make ci`가 실질 게이트인 상태.

### 잡별 소요시간·비용 (수리 시 추정)
로컬 실측을 근거로 한 러너(2 vCPU, private repo) 추정:

| 스텝 | 추정 소요 |
|------|-----------|
| checkout + setup-uv + python 3.14 설치 | ~0.5–1분 |
| `uv sync --all-groups` (scipy·sklearn·matplotlib·pyarrow 포함, 캐시 0) | ~1–2분 |
| ruff | ~0.1분 |
| mypy (매 실행 풀 콜드 — 로컬 콜드 45.8s 기준) | ~1–1.5분 |
| pytest + coverage (로컬 128.65s 기준, 러너 감속 반영) | ~3–4분 |
| **합계 (= 잡 1개라 병렬 합산도 동일)** | **~6–8분/실행** |

- 청구 산식: private repo는 잡 단위 분 올림 과금 → **실행 1회 ≈ 7분 청구**. 잡이 1개뿐이라 "병렬 잡 합산 = 단일 잡 시간"이다.
- 월 환산: 7월 페이스(118회/21일 → ~170회/월) × 7분 ≈ **월 ~1,200분** — Free 플랜 포함량 2,000분의 60%, Pro 3,000분의 40%.
- 이 중 낭비 성분:
  - **PR-push 이중 실행**: 같은 커밋이 `push`(모든 브랜치)와 `pull_request`로 두 번 돎 — 표본에서 27% (예: run 29794732703/29794718056, 19초 간격 동일 커밋). ≈ 월 320분.
  - **문서/동기화-전용 커밋에 풀 스위트**: 최근 표본 15건 중 4건이 specter-sync/docs 커밋 — 경로 필터 부재로 전체 잡 실행. ≈ 월 200–300분.
  - **캐시 0**: uv sync + mypy 콜드로 매 실행 ~2.5–3.5분 고정 낭비 ≈ 월 400분+.
- 정리하면 수리-후-무대책 시나리오 월 ~1,200분 중 **~60–70%가 구조적 낭비**. 트리거를 `push: [master]` + `pull_request`로 좁히고, `paths-ignore: ['**.md', 'docs/**']`와 uv/mypy 캐시만 넣어도 **월 ~300–400분 수준**으로 내려간다.

### 선결 문제
비용 최적화 이전에 **결정이 필요**: (a) 결제 수단을 고쳐 CI를 살릴지, (b) 로컬 `make ci`가 권위 게이트라는 현 운영을 공식화하고 워크플로우를 비활성화해 빨간 X 노이즈를 없앨지. 현 상태(고장난 채 매 push마다 실패 기록)가 최악의 조합이다.

---

## 종합: 예상 절감 로드맵 (중첩 고려)

현재 로컬 게이트 1회 = pytest 128.7–134s (커버리지 유무 무관) + mypy 1.4–45.8s + ruff 0.2s.

| 순서 | 조치 | 예상 효과 | 난이도 |
|------|------|-----------|--------|
| 1 | `-m "not network"` 기본화 (addopts) | −12s + 외부 플래키니스 제거 | 설정 1줄 |
| 2 | 캘린더 `lru_cache` | −7–13s | 코드 1줄 + 테스트 확인 |
| 3 | `e2e_ctx`/`cli_ctx` module-scope 전환 (+§3.1·3.2 중복 정리) | −15–20s | 소규모 리팩터 |
| 4 | pytest-xdist `-n auto` (+프로세스풀 테스트 2건 격리) | 잔여 ~100s → ~30–40s | 의존성 1개 + 마킹 |
| 5 | CI 방향 결정 후 트리거·캐시 정비 | (수리 시) 월 1,200분 → ~300–400분 | 설정 |

1–4 적용 시 로컬 전체 스위트 **134s → 추정 30–40s** (약 70–75% 절감). 루프 회전 속도 기준으로는 "커피 타임"에서 "탭 전환 안 하는 시간"으로 내려온다.

---

## 부록: 측정 명령 재현

```bash
# cold: 캐시 삭제 후
rm -rf .pytest_cache .coverage*; find tests backend -name __pycache__ -type d -prune -exec rm -rf {} +
time uv run pytest -q --collect-only
time uv run pytest -q -p no:cacheprovider --durations=40
# warm: 직후 재실행
time uv run pytest -q --durations=10
# CI 방식
time uv run pytest -q --cov=backend --cov-report=term
# mypy 캐시 상태별
time uv run mypy backend/   # (무효화 상태 45.8s → 직후 1.4s)
# 훅 체감
time uv run pre-commit run --files backend/backtest/config.py
# GH Actions
gh run list --limit 100 --json createdAt,event,conclusion
gh api repos/beomeodev/spade-ace-backtester/check-runs/<job_id>/annotations
```

상세 근거 원본(세션 스크래치): dead/duplicate 분석, bootstrap/parallel 분석 보고서 및 timing.log — 세션 종료 시 소멸하므로 본 문서가 보존본이다.

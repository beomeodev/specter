# 테스트 스위트 속도·건강 감사 보고서

- 감사일: 2026-07-21
- 대상 커밋: `105b3a4` (master, clean)
- 측정 환경: dev 컨테이너 (Linux), pytest 9.1.1, 410 tests / 58 files
- 성격: 읽기 전용 감사. 코드/테스트 수정 없음. cold 측정은 스크래치패드 사본에서 수행.

## 요약 (TL;DR)

| # | 항목 | 판정 | 핵심 수치 |
|---|------|------|-----------|
| 1 | 전체 실행 시간 | ✅ 매우 빠름 | cold 2.1s / warm 2.0–2.4s (pytest 내부 1.4–1.6s) |
| 2 | 죽은 테스트 | ✅ 0건 | 사소한 잔재 3건만 (아래) |
| 3 | 중복 커버리지 | ⚠️ 확정 5건 | 테스트 5개 + 파일 2개 삭제 가능, 커버리지 손실 0 (측정 검증) |
| 4 | 프리커밋/프리푸시 훅 | 🔴 미설치 | `.pre-commit-config.yaml`은 있으나 훅이 설치되지 않아 전혀 실행 안 됨 |
| 5 | 변경 범위 선택 실행 | ✅ 없음(적절) | 전체 스위트가 1.5s라 선택 실행이 오히려 손해. 단, silent-skip 결함 1건 |
| 6 | 병렬 설정 | ✅ 문제 없음 | 병렬화 자체가 없음(올바른 선택). 경합/불안정 흔적 0 |
| 7 | 중복 부트스트래핑 | ✅ 경미 | 실질 낭비 <0.5s. 코드 중복 2건은 유지보수 관점에서 수리 가치 |
| 8 | 캐시 활용도 | ✅ 양호 | mypy 캐시 13배 효과(2.41s→0.18s). CI uv 캐시는 기본값으로 동작 중 |
| 9 | GitHub Actions | 🔴 **2주째 전면 불통** | 2026-07-07 이후 모든 런이 결제 문제로 3–5초 내 즉사. 러너 미기동 |

**가장 중요한 발견은 속도가 아니라 건강이다.** 이 스위트는 410개 테스트가 1.5초에 도는, 속도 면에서는 모범적인 스위트다. 반면 (a) 원격 CI가 결제 문제로 7월 7일부터 한 번도 돌지 않았고, (b) 로컬 프리커밋 백스톱은 설정만 있고 설치가 안 돼 있으며, (c) bandit 보안 스캔은 파이썬 코드가 없는 디렉토리를 겨누고 있다. 즉 현재 이 프로젝트의 실질 게이트는 수동 `make ci` 습관 하나뿐이다.

---

## 1. 전체 테스트 실행 시간 (cold vs warm)

측정 방법: 저장소를 스크래치패드에 복사한 뒤 `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`를 제외하고 cold 측정, 같은 사본에서 재실행으로 warm 측정.

| 측정 | 명령 | pytest 내부 | wall clock |
|------|------|------------|-----------|
| Cold (캐시 전무) | `pytest -q` | 1.38s | 2.06s |
| Warm ×3 | `pytest -q` | 1.50–1.56s | 2.02s / 2.28s / 2.40s |
| 수집만 | `pytest --collect-only -q` | 0.63s | 1.35s |
| CI 동일 명령 | `pytest -v --cov=src --cov-report=term-missing` | 2.04s | 3.05s |
| 로컬 CI 전체 | `make -C .devcontainer -f Makefile ci` (warm) | — | 3.32s |

- **cold와 warm의 차이는 측정 노이즈 이내** (cold가 오히려 빠른 회차도 있음). 바이트코드/pytest 캐시가 절감할 시간이 사실상 없다.
- 실행 시간의 약 40%(0.63s)가 수집(collection) 비용, 즉 고정비다. 테스트 개수가 늘어도 실행부는 선형으로 완만하게 늘 것.
- 커버리지 계측 오버헤드: 약 +0.5s (+35%). 로컬 반복 루프에서는 `pytest -q`(커버리지 없이)를 쓰고 커버리지는 CI/마무리에만 다는 현재 구조가 합리적.
- 최장 단일 테스트: `tests/test_retrieval.py::test_real_corpus_smoke` **0.12s** (실물 77장 카드 코퍼스 색인). 그다음이 0.07s. 느린 테스트가 없다.
- 예상 절감치: **없음.** 이 항목에서 최적화할 것이 없다.

## 2. 죽은 테스트

**0건.** 전 410개 테스트가 수집·통과하고(skip 0, xfail 0), `git log --diff-filter=D -- src/` 기준 삭제된 src 파일도 없다. 로컬 fake만 검증하는 동어반복 테스트도 없다 — fake는 전부 실제 진입점(`run_live` 등)의 I/O 경계에만 주입된다 (예: `tests/test_failure_mode_suite.py:498-539`).

잔재 수준의 참고 사항 3건:

1. `tests/test_retrieval.py:300` — `pytest.skip("real cards/ corpus not present")` 분기는 `cards/`가 git 추적 대상(77 파일)이라 CI에서 절대 발화하지 않는 죽은 분기. 테스트 자체는 살아 있음.
2. `src/cueline/main.py:75` — 스텁 메시지가 "not yet available (owned by Feature 004)"라고 말하지만 Feature 004는 이미 출시됨. `tests/test_cli_stub_flags.py:60`이 이 문구를 그대로 단언하므로 문구 수정 시 테스트도 함께 갱신 필요. (오해 소지 있는 제품 문구이지 죽은 테스트는 아님)
3. `tests/test_windows_manual_checklist.py` (6개 테스트) — src 코드를 전혀 import하지 않는 유일한 파일. 문서(`docs/manual-verification/windows-checklist-v2.md` 등 4개 문서)의 문구를 고정하는 doc-lint다. Feature 015 설계상 의도된 것이나, `:120`의 W1 가드는 4개 문서의 정확한 문구를 하드코딩하고 있어 문서를 정당하게 고칠 때마다 깨질 가장 취약한 지점.

예상 절감치: 0s (삭제할 것이 없음).

## 3. 중복 커버리지

커버리지 손실 없이 삭제 가능한 확정 중복 (일부는 커버리지 측정으로 검증):

| # | 삭제 후보 | 유지 대상 | 근거 |
|---|-----------|-----------|------|
| 3-1 | `tests/test_env_and_apikey.py:46` `test_key_not_read_from_yaml` | 같은 파일 `:24` `test_missing_key_fails_fast` | arrange/act/assert가 줄 단위로 동일 (delenv → `MissingApiKeyError`). docstring만 다름 |
| 3-2 | `tests/test_turn_e2e.py` **파일 전체** | `test_turn_state_machine.py` + `test_stabilization.py` | 커버리지 측정 결과 e2e 단독 73.08%/89.89%가 유닛 측 96.15%/97.75%의 **완전 부분집합** — e2e가 더하는 라인 커버리지 0. "e2e"라는 이름과 달리 동일한 FakeClock/ScriptedEngine 하네스 사용(파일 docstring 자인). 단 `:55`의 고유 단언 1개(저점수 턴도 `selected_card=None`으로 CONFIRM)는 유닛 파일로 이식 필요 |
| 3-3 | `tests/test_turn_state_machine.py:93`, `:104` | 같은 파일 `:276`, `:258` | Feature 013이 추가한 discard-record 버전이 동일 타임라인으로 같은 단언 + discard 단언까지 하는 엄격한 상위집합. Feature 007 원본이 잔존한 것 |
| 3-4 | `tests/test_stt_events.py` **파일 전체** | `tests/test_stt_turns.py` | 동일 ScriptedTransport+FakeEngine 하네스로 같은 필드를 더 약하게 단언. `test_stt_turns.py:23,:53,:67`이 전부 상위집합 |
| 3-5 | `tests/test_reconnect_live_e2e.py:27` (파일의 유일한 테스트) | `test_reconnect.py:27,:106` + `test_failure_mode_suite.py:267` | 모든 단언이 인접 레이어에 존재. 유일한 고유 주장(스레드 merge 내 ReconnectingTransport 동작)도 failure-suite가 실제 `run_live`로 커버 |

의도된(허용 가능한) 이중화 — 삭제 비권장:

- `test_stabilization.py` vs `test_stabilization_observability.py`: 같은 `Stabilizer.observe()` 분기를 돌지만 후자의 고유 단언(Decision.kind, scores, margin)은 다른 곳에 없음. 결과 재단언은 docstring에 명시된 "policy unchanged" 가드.
- `test_failure_mode_suite.py:159/:204/:233`: 유닛 시나리오를 실제 `run_live`로 재구성하되 단언은 JSONL 로그 레이어에만 추가. 의도된 2층 커버리지.
- config 4파일 분산(`test_config` / `test_config_validation` / `test_config_import` / `test_env_and_apikey`): 각각 별개 코드 경로. 중복 아님 (3-1의 파일 내 중복 1건 제외).
- API 키 fail-fast 3중 검증 중 `test_env_and_apikey.py:53` vs `test_audio_file_e2e.py:80`은 CLI 분기만 다른 경미한 중복.

유지보수 관점 참고: `_write_config`/`_log_lines` 헬퍼가 `tests/test_query_e2e.py:24-46`과 `tests/test_audio_file_e2e.py:27-49`에 그대로 복붙되어 있음 (두 테스트 자체는 진입 경로가 달라 정당).

예상 절감치: 실행 시간 기준 **무시 가능**(<0.1s). 실익은 유지보수 비용 — 삭제 가능 테스트 5개 + 파일 2개만큼 동작 변경 시 이중 수정 부담이 사라짐.

## 4. 프리커밋/프리푸시 훅

**"CI급 전체 테스트를 훅에서 돌리는가?" — 정반대다. 훅이 아무것도 돌리지 않는다.**

- `.pre-commit-config.yaml`은 ruff, ruff-format, mypy, bandit, 기본 위생 훅, SPECTER tag-chain 백스톱을 정의하지만, **`.git/hooks/pre-commit` 파일이 존재하지 않는다.** `pre-commit install`이 실행된 적 없거나 유실된 상태로, 정의된 백스톱 전부가 로컬에서 한 번도 실행되지 않는다.
- `.git/hooks/pre-push` = git-lfs 전달뿐. 테스트/린트 없음.
- `.git/hooks/post-commit`, `post-checkout` = git-lfs + graphify 그래프 리빌드(백그라운드 분리 실행이라 커밋을 막지도, 늦추지도 않음).
- 설정 결함 2건 (설치 시 드러날 문제):
  - **bandit이 `backend/`를 스캔** (`.pre-commit-config.yaml`의 `args: ["-q", "-r", "backend"]`). `backend/`에는 `AGENTS.md` 하나뿐, 파이썬 코드 0줄. 제품 코드 `src/cueline/`(47파일)은 보안 스캔 대상이 아니다. 템플릿 잔재로 추정.
  - mypy 미러 훅의 `additional_dependencies`가 `types-requests`인데 이 프로젝트가 실제 쓰는 스텁은 `types-PyYAML`(pyproject dev 그룹). 설치되면 로컬 pyproject 설정과 다른 결과를 낼 수 있다.

예상 영향: 훅 설치는 커밋당 수 초의 **비용 추가**다(속도 관점 손해). 다만 현재 원격 CI가 죽어 있는 상태(§9)에서 로컬 백스톱마저 없으므로, 속도가 아니라 안전망 관점에서 우선 수리 대상.

## 5. 변경 범위 기반 선택 실행

- 존재하지 않음: `.devcontainer/Makefile`의 `ci-test`는 항상 전체 스위트 실행. 문서 1줄 수정에도 410개 전부 돈다.
- **판정: 현재로선 올바르다.** 전체가 1.5초인 스위트에 선택 실행 기계장치(testmon, 경로 매핑 등)를 넣는 것은 복잡도만 더하는 역최적화다. 스위트가 30초를 넘기 시작할 때 재검토할 항목.
- 단, 감사 중 발견한 **silent-skip 결함 1건**: `ci-test`는 `git ls-files '*test_*.py'`로 테스트 존재를 판정하는데(`.devcontainer/Makefile`의 ci-test 타깃), git 저장소가 아닌 곳(또는 git이 깨진 환경)에서 실행하면 테스트를 통째로 건너뛰면서도 `✅ Tests passed`를 출력한다. 실측: `.git` 없는 사본에서 `make ci` 전체가 0.21s 만에 "All CI checks passed"로 종료(실제 실행된 테스트 0개). "템플릿 초기 상태" 배려용 폴백이 유효하지 않은 상태를 조용히 통과로 위장하는 구조 — AGENTS.md §5가 금지하는 패턴에 해당. GitHub Actions에서는 checkout이 `.git`을 제공하므로 현재 실해는 없지만, 스킵 시 "passed" 대신 스킵 사실을 구분 출력하도록 고칠 가치가 있다.

## 6. 병렬 설정

- pytest-xdist 등 병렬 실행 플러그인 미설치 — 스위트는 직렬 실행. **1.5초짜리 스위트에는 이것이 정답이다** (xdist 워커 기동 비용이 전체 실행 시간을 초과).
- 경합/불안정 흔적: 없음. flaky/rerun 플러그인 부재, skip/xfail 0, 감사 중 4회 전체 실행 모두 410 passed. 스레드를 쓰는 테스트들의 대기는 전부 `Event.wait`/`thread.join` 상한 방식이라 통과 경로에서 즉시 반환 (`tests/test_capture_lifecycle.py:54` 등).
- `pyproject.toml [tool.coverage.run] parallel = true`: pytest-cov가 샤드 파일(`.coverage.*`)을 만들고 합치는 설정. 직렬 실행에서도 무해하며 문제 흔적 없음.
- 잠재 리스크(현재 비용 0): `src/cueline/stt/openai_realtime.py:46`의 `_CLOSE_JOIN_TIMEOUT_S = 2.0` 계열 상한들은 데드락 회귀가 생기면 해당 테스트들을 2–5초 행으로 바꾼다. 지금은 대기 시간 총합 ~0초.

예상 절감치: 0s. 과병렬 문제 없음.

## 7. 테스트 간 중복 부트스트래핑

repo 전체에 `conftest.py`가 없고 `@pytest.fixture`가 단 1개(`tests/test_audio_capture.py:42`, sys.modules 누수 검증용으로 함수 스코프가 의도됨)다. 공유는 헬퍼 모듈 4개(`capture_helpers`, `fake_websockets`, `state_helpers`, `stt_helpers`)가 담당 — 코드 중복은 잡았지만 런타임 반복은 남는 구조.

반복 패턴 상위 3건 (반복 횟수 × 회당 비용):

1. `tests/test_retrieval.py:42` `_fixture_corpus()` — 4장짜리 픽스처 코퍼스를 파일에서 재파싱, 한 파일 안에서 **14회 호출** (`:123`–`:291`), 캐시 없음. 엔진 재빌드 ~10회. 현재 회당 sub-ms.
2. `tests/capture_helpers.py:20` `_all_src_text()` — src 47개 파일 전체를 읽어 이어붙이는 스윕을 런당 **4–5회** 반복 (≈200+ 파일 읽기). 게다가 `tests/test_capture_lifecycle.py:206`에 **동일 목적의 로컬 사본이 복붙**되어 있어 드리프트 가능 — 드리프트 방지가 존재 이유인 헬퍼가 정작 두 벌.
3. 실물 코퍼스 로드+색인 — `tests/test_retrieval.py:297` 단 1회. 올바르게 격리됨.

문제 아님으로 확인된 것들: `tmp_path` 스캐폴딩 26개 파일(ingest 계열은 디렉토리를 변조하므로 함수 스코프 격리가 정합성 요건), `*Config(...)` ~180회(dataclass 생성자라 마이크로초), `run_live` 부트 19회(협력자 전부 fake), **실제 sleep 0건**(유일한 `asyncio.sleep`은 `tests/fake_websockets.py:75`의 `sleep(0)` 양보), **subprocess 스폰 0건**(CLI도 in-process `main([...])` 호출), 무거운 모듈 레벨 import 0건(websockets는 src에서 lazy).

예상 절감치: 전부 합쳐도 **<0.5s** (1.4s 스위트 기준). 지금은 속도가 아니라 (a) `_all_src_text()` 복붙 해소, (b) `_fixture_corpus()` 캐시화 두 건만 유지보수 관점 수리 가치가 있고, conftest.py 도입은 픽스처 코퍼스가 커지거나 실제 임베더가 테스트에 들어올 때 재검토.

## 8. 캐시 활용도

로컬:

| 도구 | cold | warm | 판정 |
|------|------|------|------|
| mypy (`mypy src/`) | 2.41s | 0.18s | `.mypy_cache` **13배 효과, 정상 동작** |
| ruff check | 0.21s | ~0.2s | cold가 이미 즉답 수준 |
| ruff format --check | 0.04s | — | 즉답 |
| pytest | 2.06s | 2.0–2.4s | 캐시 이득 자체가 없음 (§1) |

CI (`.github/workflows/ci.yml`):

- `astral-sh/setup-uv@v5`는 `enable-cache` 기본값이 `auto`(GitHub-hosted 러너에서 자동 활성) — **명시 설정 없이도 uv 패키지 캐시는 동작 중**. 정상 시절 "Install dependencies" 스텝이 1s인 것이 방증.
- `cache-python`은 기본 `false`라 `uv python install 3.14`가 매 런 재다운로드 — 스텝 실측 2s로 절감 여지 ~2s/런 수준.
- `.mypy_cache`를 actions/cache로 태우면 mypy cold 2.4s → 0.2s 절감 가능하나, 총 25s 런에서 ~2s 절감이라 우선순위 낮음.

예상 절감치: CI 런당 최대 ~4s (25s → ~21s). 로컬은 이미 최적.

## 9. GitHub Actions 워크플로우 구조와 비용

구조:

- 워크플로우 1개(`ci.yml`), 잡 1개(`ci`), 러너 `ubuntu-latest`.
- 트리거: `push: branches: ['**']` + `pull_request: branches: [master, main]`. **경로 필터 없음, 문서-전용 스킵 없음, `concurrency` 취소 그룹 없음.**
- 결과 1 — 이중 실행: PR이 열린 브랜치에 push하면 같은 커밋이 push 이벤트와 pull_request 이벤트로 **2번** 돈다. 실측: 2026-07-20 03:34–03:36 사이 push 2회에 런 4개 생성 (`feat/018` 브랜치).
- 결과 2 — 문서 커밋도 전체 CI: `docs(todo): refresh roadmap...`, `chore(specter-sync): ...` 같은 커밋들이 전부 풀 CI를 트리거. 최근 런 30개의 상당수가 docs/chore 커밋이다 (SPECTER 워크플로우 특성상 문서 커밋 비중이 높음).

잡별 소요 시간 (마지막 정상 런 28766661062, 2026-07-06, 총 25s):

| 스텝 | 시간 |
|------|------|
| Set up job | 3s |
| Checkout code | 1s |
| Install uv | 2s |
| Set up Python (uv python install 3.14) | 2s |
| Install dependencies (uv sync --all-groups) | 1s |
| Run CI checks (make ci: ruff+mypy+pytest+cov) | 8s |
| Post/Complete | 0s |
| **합계** | **~17s 스텝 + 오버헤드 = 25s** |

실행 1회당 비용 (private 저장소, 병렬 잡 합산 = 청구 분수 기준):

- 잡 1개 × ubuntu 1배율. GitHub은 **잡 단위로 분 단위 올림 청구**하므로 25초 런 = **1 청구 분** = $0.008/런 (무료 할당량 소진 후 기준; Free 플랜 월 2,000분 / Pro 3,000분의 포함 분수를 먼저 소모).
- PR 브랜치 push 1회 = 이중 실행으로 **2 청구 분**. 트리거 중복 제거만으로 feature 작업 중 Actions 분수 절반 절감.
- 누적 런 111회. 7월 6일 런의 timing API 실측 `billable.UBUNTU.total_ms: 0` — 당시는 포함 무료 분수 내에서 소화됐다는 뜻.

🔴 **핵심 발견 — CI 전면 불통 (2026-07-07 이후):**

- 마지막 성공: **2026-07-06 03:54 UTC**. 이후 **모든 런(약 28회)이 conclusion=failure**, 소요 3–5초, **스텝 0개 실행**(러너 자체가 기동하지 않음).
- 원인 (check-run annotation 원문): *"The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings"*
- 즉 코드 문제가 아니라 **계정 결제 실패 또는 Actions 지출 한도 0 도달**이다. Feature 017, 018과 v0.18.0 릴리스가 전부 원격 CI 검증 없이 머지·출시되었다 (로컬 `make ci` 습관이 유일한 게이트였음).
- 조치처: github.com Settings → Billing & plans에서 결제 수단/지출 한도 확인. 이것은 코드 수리가 아니라 계정 설정 문제라 본 감사 범위에서 수정 불가.

예상 절감치 정리 (정상화 이후 기준):

| 조치 | 절감 |
|------|------|
| 결제/한도 복구 | 절감이 아니라 **게이트 복원** — 최우선 |
| push 트리거를 master 한정으로 좁히거나 PR 브랜치 push 제외 | PR 작업 중 Actions 분수 **~50%** |
| `paths-ignore`로 docs/spec-전용 커밋 스킵 | 문서 커밋당 1 청구 분 (SPECTER 특성상 비중 큼) |
| `concurrency` + cancel-in-progress | 연속 push 시 낡은 런 취소 (분수 소액) |
| cache-python + .mypy_cache 캐시 | 런당 ~4s (체감 미미) |

---

## 종합 권고 (우선순위순)

1. **[게이트 복원] GitHub Billing 문제 해결** — 2주째 원격 CI 부재. 코드 아닌 계정 설정 사안.
2. **[게이트 복원] `pre-commit install` 실행** — 설정만 있고 훅 미설치. 설치 전에 bandit 대상(`backend` → `src`)과 mypy 스텁 의존성(`types-requests` → `types-PyYAML`) 교정 권장.
3. **[정합성] `ci-test`의 silent-skip을 명시적 스킵 보고로 교정** — 테스트 0개 실행이 "✅ Tests passed"로 위장되는 분기 제거.
4. **[비용] ci.yml 트리거 정리** — push/`pull_request` 이중 실행 제거 + docs-전용 `paths-ignore` + `concurrency` 그룹.
5. **[유지보수] 중복 테스트 정리** — §3 확정 5건 (테스트 5개 + `test_turn_e2e.py`·`test_stt_events.py`·`test_reconnect_live_e2e.py`), 삭제 전 §3-2의 고유 단언 1개 이식.
6. **[유지보수] `_all_src_text()` 복붙 해소, `_fixture_corpus()` 캐시화** — 속도 아닌 드리프트 방지 목적.
7. **속도 최적화는 하지 말 것** — xdist 병렬화, 변경 범위 선택 실행, 테스트 캐시 튜닝 모두 현 규모(1.5s)에서는 역최적화. 스위트가 30초를 넘을 때 재검토.

## 감사 중 수행한 환경 변경 (고지)

- 전역 규칙(Graphify 미설치 시 설치 우선)에 따라 `graphifyy==0.9.12`를 uv tool로 설치하고 초기 그래프(`graphify-out/graph.json`)와 post-commit/post-checkout 훅을 생성했으며, `.gitignore`에 `graphify-out/` 1줄을 추가했다. 소스/테스트 코드는 일절 수정하지 않았다.
- cold 측정용 저장소 사본은 세션 스크래치패드에 생성했으며 저장소 외부라 잔존물이 없다.

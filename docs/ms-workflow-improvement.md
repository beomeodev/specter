# SPECTER `/ms.*` 워크플로우 개선 메모

**최초 작성일**: 2026-05-12 (D6 직후)
**최신 업데이트**: 2026-05-12 (027 직후 — Issue 4-8 + 사용자 요청 섹션 추가)
**작성 맥락**:
- D6 (Global Palette Rollout) 세션 직후, 직접 실행한 에이전트 입장에서 발견한 마찰점 정리 (Issue 1-3)
- 027 (Note Switch Protection) 세션 직후, mid-complexity feature 워크플로우 부담 정리 (Issue 4-8)
- 사용자가 명시적으로 요청한 UX 개선 사항 (Issue 9)
**대상 독자**: 추후 워크플로우를 개선할 사람 + 동일 워크플로우를 실행할 에이전트

각 이슈마다 (a) 증상, (b) 왜 문제인지, (c) 실제 세션 사례, (d) 개선 방향을 적었습니다.

---

## Issue 1 — `/ms.implement` 의 TDD narrative가 refactor 작업에 안 맞음

### 증상

`/ms.implement` 의 스킬 설명은 RED → GREEN → REFACTOR cycle을 강하게 가정합니다.

> `tdd-implementer (Sonnet)` agent runs RED (failing tests) → GREEN (minimum code) → REFACTOR. Auto-inserts TAG blocks via `ms-workflow-tag-manager` skill.

하지만 D6 같은 **audit-driven refactor** 는 이 cycle과 안 맞습니다:

- D6의 핵심 작업: 미리 정의된 swap table (예: `text-slate-500` → `text-text-muted`) 을 N개 파일에 mechanical 적용
- "failing test 먼저 작성" 단계가 없음 (또는 매우 작음)
- `ms-workflow-tag-manager` 자동 호출 안 됨 — TAG block은 결국 손으로 추가

결과: 스킬 설명과 실제 동작이 어긋나서 사용자가 "스킬이 제대로 안 돌고 있는데?"로 오해하기 쉽고, 에이전트도 "RED를 어떻게 만들어야 하지?" 같은 부정합 고민을 함.

### 왜 문제인지

워크플로우가 fresh TDD greenfield feature를 가정한다는 인상을 줍니다. 실제 프로젝트에선 **refactor 비중이 작지 않음** — D-track (D1-D6) 전부가 refactor였고, 향후 D7+ / per-feature polish도 동일 성격일 가능성 높음.

### D6 사례

- **Phase 1 RED gate**: 스킬 설명대로면 "failing test 작성 → impl로 GREEN" 인데, 실제로는 가드/contrast/confidentiality 테스트를 작성해도 **즉시 GREEN** 이었음 (D3가 이미 contracts를 만족). "RED"는 실제 RED가 아니라 "safety net 설치"의 의미였음 → tasks.md T017에서 "the safety net is GREEN today" 로 재정의해야 했음.
- **TAG block 삽입**: 17개 admin component 파일 swap (Phase 6) 시 모두 `@CODE:D6-ADMIN-MODAL-XYZ` 를 손으로 추가. `ms-workflow-tag-manager` 자동 호출 없음.
- **Phase 5/6/7 sed-batch swap**: 가장 효율적이었던 패턴은 `cat > /tmp/swap.sh + sed -i` 였는데, 스킬 설명에는 이런 batch refactor pattern이 없음.

관련 commit: [b9e2528](../../commit/b9e2528) (Phase 1 RED 재정의), [6c41d90](../../commit/6c41d90) (Phase 6 bulk swap)

### 개선 방향

```
/ms.implement --mode={tdd|refactor}    # 명시적 mode 분기
```

**refactor mode 의 특징**:
- RED-GREEN-REFACTOR 표현 대신 **audit → swap-table → mechanical apply → verify** narrative
- batch sed/awk 워크플로우를 정식 인정 (예시 commit 패턴 + 안전한 stage 절차 가이드)
- TAG block 삽입은 스킬 description에서 "auto" 라고 약속하지 말고 "you'll add `@CODE:XXX` to touched files' docstrings" 로 정직하게
- Phase 단위 batch task close (다음 Issue 와 연결)

대안: spec.md 단계에서 `## Mode: refactor` 메타데이터를 명시하면 `/ms.implement` 가 알아서 narrative 분기.

---

## Issue 2 — Implementation 중 발생한 clarification 의 갈 곳이 없음

### 증상

`/ms.clarify` 단계에서 Q1-Q10 binding decisions 를 spec.md에 고정합니다. 그런데 implementation 중에 진짜 의사결정이 추가로 발생하는 경우가 매번 있음. 새로 발견된 결정이 spec/plan으로 propagate되는 정식 경로가 없음 — 결국 commit message + tasks.md 한 줄 코멘트로 흩어짐.

### 왜 문제인지

- 추후 D6 spec/plan을 다시 읽는 사람은 Q1-Q10만 보고 "이게 전부의 의사결정"이라고 오해
- Implementation 중 결정이 후속 D-track 의 reference로 활용 안 됨
- 동일 결정을 D7에서 다시 고민하게 됨 (재발견 비용)

### D6 사례

D6 진행 중 발생한 결정 중 spec/plan에 정식 등재되지 않은 것:

| 결정 | 어디서 발생 | 어디 흘러갔는지 |
|---|---|---|
| Admin 페이지의 destructive button `border-red-300 + text-red-600 + bg-red-50` → `border-danger + text-danger + bg-danger/10` 로 swap (단순 슬레이트가 아닌 red도 D3 status 토큰으로 매핑) | Phase 5 T027 시점 | commit [bc69207](../../commit/bc69207) 메시지에 swap table 한 줄로만 기록 |
| `--color-overlay-modal` 토큰 namespace 결정 (`step-1..7` 이 아니라 `level-low/medium/high/untouched` + pattern-overlay 로 4-level mastery 구조였음을 발견) | Phase 8 T066 시점 | tasks.md T066 인라인 코멘트 + plan §5.4 Final Additions 에 retroactive 추가 |
| `tailwind.config.ts` 에 `overlay-modal` alias 추가 허용 (plan §3 "NOT TOUCHED" 리스트에 있던 파일이지만 D3 backport와 일관성 위해 예외 처리) | Phase 6 T040-T058 시점 | plan §5.4 Final Additions 의 "Scope adjustment" 섹션 — 이건 retroactive 등재한 좋은 사례 |
| `emerald` Tailwind 색상군 → `success` 토큰 매핑 (canonical swap table 에 없던 신규 mapping) | Phase 7 T060 시점 | commit [f350020](../../commit/f350020) 메시지의 "NEW canonical swap" 섹션 |

이 결정들이 D7 (가상)에서 다시 필요해진다면, 누군가 commit history를 grep해야 함.

### 027 보강 사례 (round-2 design pivot)

027 세션 Phase 2 RED 도중 `attempts.selected_index` 가 없다는 사실이 발견되면서 전체 design pivot 발생. spec FR-API-003 / FR-API-008 / FR-DB-001 / FR-PRES-001..005 가 동시에 의미가 바뀌어야 했음. 처리한 방식:
- spec.md 본문을 직접 수정 (Q3 decision 의 본문 교체)
- 새 Q-id (Q15+) 발급 없이 기존 Q3을 redefine
- amendment 섹션 없이 본문 in-place patch

문제: 추후 spec.md 를 처음 보는 사람은 "왜 attempts.is_tentative 라는 단어가 안 보이지?" 라는 의문에 답을 못 얻음. 본문이 final state 만 기록하고 진화 과정은 commit history 에 묻힘.

### 개선 방향

`/ms.clarify --post-impl` 또는 신규 `/ms.amend` 커맨드:

```
/ms.amend "Phase 5 destructive button: red-300/red-600 → danger token 매핑을
            canonical swap table에 추가 (FR-D6-APPLY-002 / 위반 아님)"
```

동작:
1. spec.md `## Clarifications` 섹션에 **"Session 2026-05-12 — Post-impl additions"** 서브섹션 자동 추가
2. plan.md 의 해당 섹션 (예: §4 swap table) 자동 업데이트
3. 새 Q-id 발급 (Q11, Q12 등) — implementation-time decision 임을 명시
4. tasks.md 에 cross-reference 추가

**Round-2 pivot 같은 큰 변화는 다른 처리**: spec 본문을 직접 수정하지 말고 spec 끝에 **Amendment 1 / Amendment 2** 섹션을 추가. 기존 FR 본문은 그대로 두되 "**Superseded by Amendment 1**" 마커를 붙임. 변경 추적이 한 곳에서 됨.

대안 (가벼움): `docs/decisions/D6-impl-decisions.md` 같은 ADR-style append-only 로그 자동 생성. 매 `/ms.implement` commit 시점에 commit message에서 "Decision: ..." 패턴 추출 → 해당 파일에 append.

---

## Issue 3 — PR body 자동 탐지가 mtime 기반이라 잘못된 파일이 첨부될 수 있음

### 증상

`/finq` 의 Step 3.5 (PR auto-create) 는 PR body 파일을 다음 명령으로 탐지:

```bash
PR_BODY_FILE=$(ls -t docs/PR_*_BODY.md 2>/dev/null | head -1)
```

가장 최근 mtime 의 `docs/PR_*_BODY.md` 가 첨부됩니다. 문제: **mtime ≠ 현재 PR의 body**. 예시:
- 어제 D5 PR body 작성 → `docs/PR_D5_BODY.md` (mtime = 어제)
- 오늘 D6 PR body 작성 → `docs/PR_D6_BODY.md` (mtime = 오늘) → 정상 케이스 OK
- **만약 어제 D5 PR body를 오타 fix로 오늘 손댔다면** → D5 BODY가 newer → D6 PR 에 D5 body가 첨부됨

### 왜 문제인지

- PR description 이 잘못 첨부되면 reviewer가 코드와 description 의 불일치를 발견할 때까지 모름 (PR 머지까지 갈 수도 있음)
- 동시에 여러 D-track / feature branch 가 진행 중일 때 confusion 가능성 큼

### D6 사례

이번 D6 세션에선 운 좋게 D5 PR_BODY 가 더 오래된 상태였어서 자동 탐지가 맞는 파일을 골랐음. 하지만 PR body 작성 직후 어떤 이유로든 D5 PR_BODY 의 typo fix 한 번 했으면 잘못 첨부됐을 것.

`/finq` 실행 시 출력:
```
🚀 새 PR 생성 중 (base: master)...
Warning: 23 uncommitted changes
https://github.com/beomeodev/suseonglm/pull/36
```

"어느 PR_BODY 파일을 첨부했는지" 가 출력에 없음. 만약 다른 파일이 첨부됐다면 사용자도 즉시 알 수 없음.

### 개선 방향

탐지 우선순위를 **branch name → body filename 명시적 매핑** 으로 변경:

```bash
BRANCH=$(git branch --show-current)
# 1순위: branch name에서 feature identifier 추출 (D6-... / 014-... / fix-005-...)
FEATURE_ID=$(echo "$BRANCH" | grep -oE '^([A-Z][0-9]+|[0-9]{3}|fix-[0-9]+)')

# 2순위: 해당 ID 의 PR body 파일이 있으면 사용
if [ -n "$FEATURE_ID" ] && [ -f "docs/PR_${FEATURE_ID}_BODY.md" ]; then
  PR_BODY_FILE="docs/PR_${FEATURE_ID}_BODY.md"
fi

# 3순위 fallback: 기존 mtime 방식 (지금 동작)
PR_BODY_FILE="${PR_BODY_FILE:-$(ls -t docs/PR_*_BODY.md 2>/dev/null | head -1)}"
```

추가 안전망:
1. **첨부 직전 user에게 명시적 confirm (한국어)**: "PR #36에 `docs/PR_D6_BODY.md` 첨부 예정 — 맞나요?"
2. **PR body 파일 첫 줄에 branch ref 또는 PR title 포함 검증**: branch 가 `D6-global-palette-rollout` 인데 PR body 첫 줄이 `# D5 — Note Page Redesign` 이면 abort
3. 출력에 "Attached body: docs/PR_D6_BODY.md (matched via branch name)" 표시

---

## Issue 4 — `/ms.plan` 이 codebase 현실을 verify 안 함 (가장 큰 비용)

### 증상

`/ms.plan` 이 만드는 plan.md 는 **파일 경로, schema 컬럼명, API 컨벤션을 가정만 하고 실제 verify 안 함**. plan 이 commit 된 후 implementation 단계에서 가정이 깨지면, spec/plan/tasks/test 파일 전체에 fanout 수정이 발생함.

### 왜 문제인지

`/ms.plan` → `/ms.tasks` → `/ms.implement` 까지 통과한 다음에 가정 오류가 발견되면:
1. 이미 작성된 RED 테스트가 잘못된 API 를 검증 중
2. tasks.md 의 T-ID 가 ghost path 를 가리킴
3. spec 의 FR 가 존재하지 않는 컬럼에 의존
4. 한 commit 으로 정정 불가 — spec / plan / tasks / test / production 다 손대야 함

**비용 비교**:
- Plan 단계에서 `rg "CREATE TABLE attempts"` 1초 → 가정 검증
- Phase 2 RED 단계에서 가정 깨짐 발견 → 6개 task 삭제 + 4개 test 재작성 + spec / plan / tasks 본문 수정 + 사용자에게 design pivot 의사결정 받음 → 수십 분

### 027 사례

027 세션에서 plan 가정이 깨진 5건:

| 가정 | 현실 | 발견 시점 | 비용 |
|---|---|---|---|
| 마이그레이션 인덱스 0019가 비었음 | 0019, 0020 이미 사용됨 | Phase 0 setup | 작음 (sed 치환) |
| `attempts.selected_index` 존재 | 없음 — Feature 008은 grade 후 폐기 | **Phase 2 RED 실행 중** | **큼** (Option B 설계 피봇, T012+T029-T033 삭제, 테스트 4개 재작성, spec FR-API-003/008/DB-001 본문 변경, 사용자 의사결정 round-trip) |
| `routers/quiz_sessions.py` 경로 | 실제는 `quiz/router.py` | Phase 4 GREEN 시작 | 중간 (T034 description 만 수정) |
| `services/kst_service.py` 경로 | 실제는 `kst/service.py` | Phase 4 GREEN 시작 | 작음 (predicate sweep 자체가 Option B로 삭제됨) |
| 401 / `"찾을 수 없어요."` (점 있음) 컨벤션 | 403 / `"찾을 수 없어요"` (점 없음) | **Phase 4 GREEN 테스트 통과 확인 중** | 중간 (RED 테스트 6개 재작성, spec FR-API-001/002 본문 변경) |

5개 다 plan 단계에서 ripgrep 한 번이면 잡혔을 것.

### 개선 방향

`/ms.plan` 출력에 **"Reality Verified"** 섹션 강제:

```markdown
## Reality Verified (auto-generated, blocking)

| Assumption | Verified by | Result |
|---|---|---|
| Next migration index = 0021 | `ls db/migrations/00*.sql | tail -1` → `0020_*.sql` | ✓ |
| `quiz_sessions` schema has columns A, B, C | `grep -A 20 "CREATE TABLE quiz_sessions"` | ✓ matches |
| `attempts.selected_index` exists | `grep "selected_index" db/migrations/*.sql` | ✗ **NOT FOUND** — plan revised before commit |
| `routers/quiz_sessions.py` exists | `test -f backend/src/.../routers/quiz_sessions.py` | ✗ **actual: quiz/router.py** — plan amended |
| Auth gating: 401 vs 403 | `grep "HTTP_401\|HTTP_403" middleware/is_admin.py` | ✓ 403 (project convention) |
| Generic 404 body string | `grep -h "찾을 수 없어요" backend/src/` | ✓ no trailing period |
```

**Blocking rule**: 이 표에 ✗ 가 하나라도 있으면 `/ms.plan` 이 commit 되기 전 사용자에게 한국어로 surface:

```
⚠️  Plan 가정 중 검증 실패한 항목이 있습니다:
   - attempts.selected_index 존재 가정 → 실제 없음 (Feature 008은 grade 후 폐기)
   - routers/quiz_sessions.py 경로 → 실제 quiz/router.py

설계를 어떻게 조정할까요?
   1) plan 본문 자동 수정 (경로/스키마 reality 에 맞춤)
   2) 가정 유지하되 spec amendment 단계로 진행 (예: 신규 column 추가가 의도된 경우)
   3) 작업 취소 (clarify 단계로 회귀)
```

스킬 implementation 디테일은 4가지:
1. plan.md template 에 "Reality Verified" 섹션 필수 표시
2. `/ms.plan` 이 plan body 를 쓰기 전 사전 grep / find / test -f 일괄 실행
3. ✗ 가 하나라도 있으면 사용자에게 한국어 의사결정 prompt
4. final plan body 에 verified table 포함 (commit 의 일부로 보존)

이 하나의 단계가 027 세션의 가장 큰 churn 을 사전 차단함.

### 구체화 (실행 명세)

**`/ms.plan` 이 자동 실행할 7개 verification 명령**:

```bash
# 1. Next free migration index
ls db/migrations/00*.sql | sort | tail -1
# → "0NNNN_<name>.sql" — next = NNNN+1

# 2. Schema column existence (per-table, assumed in plan §"SQL Plan")
grep -A 30 "CREATE TABLE <table>" db/migrations/0001_initial.sql
grep "ALTER TABLE <table>" db/migrations/*.sql

# 3. File path existence (each path mentioned in plan §"Project Structure")
test -f backend/src/suseonglm/<path> || echo "MISSING: <path>"

# 4. HTTP status convention (auth gating: 401 vs 403)
grep -rE "HTTP_(401|403)" backend/src/suseonglm/middleware/

# 5. Generic error body strings (404 / 422 / 409 정확한 wording)
grep -rhE '"detail":\s*"[^"]+"' backend/src/suseonglm/ | sort -u | head -10

# 6. Required env vars at boot (FR-INF 가 새 env 가정 시 conflict 확인)
grep -E "os.environ\[|getenv\b" backend/src/suseonglm/config.py

# 7. Existing test fixtures inventory
grep -h "@pytest.fixture" backend/tests/conftest.py backend/tests/*/conftest.py
```

**최종 plan.md "Reality Verified" 표 형식**:

```markdown
## Reality Verified (auto-generated, blocking)

| Assumption | Verified by | Result |
|---|---|---|
| Next migration index = NNNN | `ls db/migrations/00*.sql | tail -1` | ✓ or ✗ |
| Column `<table>.<col>` exists | `grep "<col>" db/migrations/*.sql` | ✓ or ✗ NOT FOUND |
| File `<path>` exists | `test -f <path>` | ✓ or ✗ actual: `<other>` |
| Auth gating uses 403 (not 401) | `grep HTTP_403 middleware/is_admin.py` | ✓ or ✗ |
| Generic 404 body `"찾을 수 없어요"` (no period) | `grep -h 404 routers/` | ✓ or ✗ |
```

**✗ 발견 시 한국어 surface**:

```
⚠️ Plan 가정 N건 검증 실패:
   1. attempts.selected_index 존재 가정 → 실제 없음 (Feature 008 grade 후 폐기)
   2. routers/quiz_sessions.py 경로 → 실제 quiz/router.py
   3. 401 auth convention → 실제 403

처리 방향:
  1) 자동 수정 가능 (path / migration index / error body string) → plan sed 치환 후 진행
  2) 설계 결정 필요 (schema 부재 / 의미 변경) → spec amendment 의사결정 prompt
  3) 작업 취소 → /ms.clarify 단계로 회귀
```

**Auto-fix vs manual decision 매트릭스**:

| 카테고리 | Auto-fix | 예시 |
|---|---|---|
| 마이그레이션 index 충돌 | ✓ sed | 0019 → 0021 |
| File path drift | ✓ plan 본문 치환 | `routers/quiz_sessions.py` → `quiz/router.py` |
| Error body string drift | ✓ string 치환 | `"찾을 수 없어요."` → `"찾을 수 없어요"` |
| Schema column 부재 | ✗ 설계 결정 필요 | `attempts.selected_index` 부재 → Option B 검토 |
| HTTP status convention 충돌 | ✗ spec FR 의미 변경 | 401 → 403 (FR-API-001 본문 수정) |
| Env var 충돌 | ✗ Constitution §IX 영향 | 새 env var 추가 vs 기존 재사용 |

---

## Issue 5 — `/ms.implement` 스코프 모델 + 스킬 prompt 재주입

### 증상

`/ms.implement` 스킬은 "first uncompleted task" 한 개를 가정하지만, 실제로 사용자가 원하는 단위는 "다음 자연스러운 commit boundary 까지." 매 호출마다 사용자가 "이번엔 어디까지 갈래?" 답해야 하는 round-trip 이 발생함.

또한 매 호출마다 스킬 본문 (600+ 라인) 이 system reminder 로 재주입됨. 같은 세션 내 6번 호출이면 3600+ 라인 중복.

### 왜 문제인지

- **Scope 협상의 토큰 낭비**: AskUserQuestion 한 번 → 50 토큰 응답 + 응답 처리 + 결정 후 분기 = 매 호출 200+ 토큰
- **스킬 prompt 중복**: 같은 600+ 라인 6번 = 3600+ 라인. 진짜 작업 token budget 을 잠식
- **인간 의도 mismatch**: "다음 commit 단위" 가 자연스러운 단위인데 스킬은 "다음 task 1개" 라고 가정. 매번 협상 = ergonomic friction

### 027 사례

027 세션의 6번 `/ms.implement` 호출 중 5번은 사용자와 scope 협상이 필요했음:
- Phase 0+1+2 백엔드 RED — 사용자에게 branch + scope 묻기
- Phase 4 백엔드 GREEN — 묻지 않고 진행 (그 다음 commit boundary 가 명확했음)
- Phase 3 part 1 (T014-T016) — 1300 SLOC 전체냐 일부냐 묻기
- Phase 5 part 1 (T035-T037) — 자동으로 part 1 만
- Phase 5 part 2 (T038-T041) — 자동
- Phase 5 part 3 + 폴리시 (T042-T054) — 자동

사용자가 매번 답한 패턴은 사실상 동일: "현재 phase 완료까지 가자." 스킬이 default 로 그렇게 동작했으면 협상 5번이 0번 됐음.

### 개선 방향

**1. Default scope 를 "current phase 끝까지" 로 변경**:

```
/ms.implement                  # default: current phase boundary 까지 (RED, GREEN, polish 등)
/ms.implement --task T035      # 단일 task 모드 (현재의 first-uncompleted 동작)
/ms.implement --to-end         # 남은 모든 task (긴 세션용)
```

스킬 prompt 의 "first uncompleted task" 부분을 "next natural commit boundary (typically a phase or phase-part)" 로 교체.

**2. 스킬 prompt 를 세션 내 캐시**:

스킬 dispatcher 레벨에서 `/ms.*` 첫 호출에만 full prompt 주입, 이후 호출은 "skill {name} continuing" 한 줄로 reference. 이건 SPECTER 시스템 인프라 작업이지 개별 스킬 작업은 아님.

**3. Phase 완료 직후 사용자에게 한국어로 progress + 다음 단계 surface (사용자 요청 — Issue 9 참고)**:

```
✓ Phase 4 GREEN 완료 (T024-T034, 11개 task)
   진행률: 5 / 8 phase 완료 (62%)
   남은 phase: 3 (Phase 3 part 2 RED · Phase 6 VR · Phase 7 polish)

다음 단계: /ms.implement 로 Phase 3 part 2 (frontend 통합 테스트 7개) 시작
또는 /finq 로 현재 상태에서 PR 만들기
```

이 자체로 사용자가 "다음에 뭐 할까?" 라는 인지 부하 없이 자연스럽게 다음 호출로 넘어감.

---

## Issue 6 — 4개 문서가 4개 source of truth 가 됨 (drift inevitable)

### 증상

`/ms.specify` → spec.md, `/ms.plan` → plan.md, `/ms.tasks` → tasks.md, 코드 + 테스트 → TAG block. 한 가지 사실 (예: "마이그레이션 파일명") 이 네 군데에 적힘. 한 곳을 수정하면 나머지 세 곳을 같이 수정해야 함.

### 왜 문제인지

- Round-2 pivot 같은 큰 변경 발생 시 매번 sed-batch 또는 손 수정 4회
- drift 가 누락되면 reader 가 모순된 정보를 봄 (예: plan 에는 "0019_*.sql" 그대로 남아있는데 spec 은 "0021_*.sql" 로 업데이트됨)
- 자동 검증 안 됨 — 사람이 manual diff 해야 함

### 027 사례

Round-2 design pivot 발생 시 수정한 항목:
- spec.md: Q3 decision body, FR-API-003, FR-API-008, FR-DB-001, FR-DB-003 본문
- plan.md: SQL Plan 섹션, Project Structure 섹션, TAG Chain 표
- tasks.md: T009 description, T010-T013 description, T012 + T029-T033 deletion
- 4 backend 테스트 파일: assertion 본문 + seed 함수

sed 로 `0019_quiz_resume_state` → `0021_quiz_resume_state` 전체 치환은 깔끔했음. 하지만 `attempts.is_tentative` → `quiz_sessions.tentative_answers_json` 같은 의미적 변경은 sed 로 안 됐고, 각 파일에서 수동으로 본문 다시 작성.

Phase 4 GREEN 단계에서 발견: plan §"Project Structure" 가 여전히 `routers/quiz_sessions.py` 와 `services/kst_service.py` 같은 ghost path 를 가리키고 있었음. 위 round-2 pivot 수정 때 누락된 것.

### 개선 방향

**1. spec.md 를 single source of truth 로**:
- FR / Q / amendment 만 spec 에
- plan.md 의 SQL Plan / Project Structure 같은 implementation detail 은 spec 의 FR 본문에서 참조만
- tasks.md 의 T-ID 는 spec 의 FR id 와 1:N 매핑만 — independent narrative 없음

**2. Drift detection 자동화**:

`/ms.analyze` 에 cross-artifact diff 강화:

```bash
# spec 의 마이그레이션 파일명과 plan / tasks 의 그것이 일치하는지
grep -h "0021_quiz_resume_state" specs/027-*/spec.md specs/027-*/plan.md specs/027-*/tasks.md
# 모두 같은 문자열을 가리키면 OK, 다른 문자열이 섞이면 drift

# spec 의 FR id 와 tasks 의 @TEST cross-ref 가 1:1 매핑인지
diff <(spec → extract FRs) <(tasks → extract @TEST refs)
```

이 검증을 `/ms.implement` 가 시작할 때 사전 실행해서 drift 가 있으면 한국어로 surface.

**3. Amendment 패턴 정형화**:

큰 변경은 본문 직접 수정 금지. 대신 spec.md / plan.md 끝에 amendment 추가:

```markdown
## Amendment 1 — 2026-05-12 (Option B design pivot during Phase 2 RED)

### Trigger
attempts.selected_index does not exist. Original design impossible.

### Supersedes
- FR-API-003 (original)
- FR-API-008 (original)
- FR-DB-001 (original)
- FR-PRES-001..005 aggregation predicate sweep — REMOVED

### Replacement wording

[new FR text here]
```

기존 FR 본문은 그대로, 본문 위에 "**[SUPERSEDED by Amendment 1]**" 마커만 추가. drift 가 한 곳에서 추적됨.

### 구체화 (실행 명세)

**Amendment block markdown 템플릿**:

```markdown
## Amendment N — YYYY-MM-DD ([1-line trigger phrase])

### Trigger
[1-2 문장: 무엇이 발견됐는지 + 언제]

### Supersedes
- FR-XXX-NNN (original): [원본 의도 한 줄]
- FR-YYY-MMM (original): ...

### Replacement wording
[새 FR 본문 — full text]

### Cross-refs
- plan §"..." 갱신: [delta]
- tasks T-IDs affected: [T-NNN, T-MMM]
- Removed tasks: [T-NNN + 삭제 이유]
```

기존 FR 본문 위에는 1줄 마커 추가:
```markdown
**[SUPERSEDED by Amendment 1 — 2026-05-12]**
- **FR-API-003 (Ubiquitous)**: System SHALL upsert into `attempts` ...
```

**In-place edit vs Amendment 결정 트리**:

| 변경 성격 | 처리 방식 |
|---|---|
| Typo / 마침표 / 형식 미세 조정 | in-place edit |
| FR 본문 줄 수 변화 < 10% AND id 의미 유지 | in-place edit |
| 새 FR 추가 (supersede 없이) | in-place edit + Q-id 발급 |
| FR 본문 줄 수 변화 ≥ 10% | **amendment 필수** |
| FR id 의미 변경 (signature 가 다른 책임) | **amendment 필수** |
| 기존 FR 삭제 | **amendment 필수** (history 보존) |
| 스키마 / API 구조 pivot | **amendment 필수** |

**Drift detection 자동화 (`/ms.analyze` 가 사전 실행)**:

```bash
SPEC_DIR="specs/N"

# 1. Migration filename consistency (spec/plan/tasks 가 동일 파일명 가리키는지)
MIGRATION_REFS=$(grep -hoE '00[0-9]+_[a-z_]+' "$SPEC_DIR"/{spec,plan,tasks}.md | sort -u)
COUNT=$(echo "$MIGRATION_REFS" | wc -l)
[ "$COUNT" -le 1 ] || echo "DRIFT: multiple migration names: $MIGRATION_REFS"

# 2. File path consistency (참조된 모든 path 가 실제 존재하는지)
PATH_REFS=$(grep -hoE 'backend/src/suseonglm/[a-z_/]+\.py' "$SPEC_DIR"/{spec,plan,tasks}.md | sort -u)
for p in $PATH_REFS; do
  [ -f "$p" ] || echo "DRIFT: $p missing"
done

# 3. FR id ↔ @TEST tag 매핑 (spec 의 모든 FR group 이 tasks 에 매핑되는지)
diff <(grep -oE 'FR-[A-Z]+-[0-9]+' "$SPEC_DIR"/spec.md | sed -E 's/FR-([A-Z]+).*/\1/' | sort -u) \
     <(grep -oE '@TEST:[A-Z0-9]+-[A-Z]+' "$SPEC_DIR"/tasks.md | sed -E 's/.*-([A-Z]+)$/\1/' | sort -u)
# 출력 비어있으면 OK, 라인 있으면 group-level drift

# 4. Amendment 마커 무결성 (SUPERSEDED 마커가 있는 FR 의 amendment 가 존재하는지)
for fr in $(grep -B1 "SUPERSEDED by Amendment" "$SPEC_DIR"/spec.md | grep -oE 'FR-[A-Z]+-[0-9]+'); do
  AMD=$(grep "$fr (original)" "$SPEC_DIR"/spec.md)
  [ -n "$AMD" ] || echo "DRIFT: $fr marked superseded but no amendment block found"
done
```

**`/ms.analyze` 의 한국어 surface 예**:

```
⚠️ 문서 drift 발견:
   - specs/N/spec.md 는 0021_quiz_resume_state 참조
   - specs/N/plan.md 는 0019_quiz_resume_state 참조 (stale)
   - specs/N/tasks.md 는 0021_quiz_resume_state 참조

처리:
  1) plan.md 본문에 sed 치환 (자동) — 권장
  2) 수동 검토 — drift 가 의도된 경우 (드물지만)
```

---

## Issue 7 — EARS / TAG 가 ceremony 가 되는 지점이 있음

### 증상

`/ms.specify` 가 EARS 형식 (WHEN / WHILE / WHERE / IF / SHALL) 을 모든 FR 에 강제. `/ms.implement` 시점에 TAG block (@SPEC / @TEST / @CODE) 을 모든 파일 + 모든 테스트 함수에 삽입 권장.

이 ceremony 는 명확함이 가치 있는 곳에선 ROI 양수, 그렇지 않은 곳에선 음수.

### 왜 문제인지

**EARS ceremony 의 ROI 음수 지점**:
- "FR-PRES-001: System SHALL preserve D5 three-panel layout" — 그냥 "D5 깨지 마"
- "FR-PRES-005: System SHALL preserve D6 global palette" — 같은 패턴
- 9 단어를 30 단어로 만들고 의미 가산 0

**TAG line-level annotation 의 ROI 음수 지점**:
- 각 테스트 함수마다 `@TEST:027-DLG-005` docstring — write-once metadata
- 작업 중 단 한 번도 `rg @TEST:027-DLG-005` 로 추적 안 함
- 함수명만 잘 지어도 같은 traceability 달성 가능

### 027 사례

027 spec 의 90개 FR 중 EARS 형식이 의미를 더한 것:
- FR-DLG-012 (WHILE async cleanup pending, system SHALL disable ... AND render spinner) — 모호함 제거됨
- FR-FLOW-005 (IF tentative-save fails, system SHALL NOT call router.push) — 가드 조건 명확
- FR-API-004 (IF body fails validation, system SHALL respond 422) — 빠짐없는 enumeration

ROI 음수였던 것:
- FR-PRES-001..007 전체 — preservation contracts, 평서문이면 충분
- FR-ISO-001..005 — "System SHALL ensure note isolation" 같은 high-level 정책 — EARS 형식이 의미를 안 더함

TAG annotation:
- File-level `@CODE:027-DLG-001` 1개 — 가치 있음 (파일 grep 가능)
- 테스트 파일에서 17개 `@TEST:027-DLG-001..012` 각 함수 docstring — write-only, 한번도 활용 안 됨

### 개선 방향

**1. EARS 적용을 "ambiguity 가 있을 때만"**:

`/ms.specify` prompt 에 명시:
> EARS format은 다음 경우에만 적용:
> - Event-driven behavior (WHEN ...)
> - State-driven behavior (WHILE ...)
> - Optional / conditional behavior (WHERE ...)
> - Constraint / error handling (IF ...)
>
> 다음은 EARS 적용 금지 (평서문 사용):
> - Preservation contracts ("System shall preserve X")
> - Constitution-derived constraints ("Code shall follow Section X")
> - Type / shape declarations ("Schema has fields A, B, C")

90개 FR 이 60개로 줄어들고 spec 가독성 상승.

**2. TAG annotation 을 file-level 만으로**:

- 각 새 파일 상단에 1개 `@CODE:XXX-NNN` 블록 — 유지
- 각 테스트 파일 상단에 1개 `@TEST:XXX-NNN` 블록 — 유지
- 함수 / 테스트 케이스마다 line-level `@TEST` docstring — **폐기**

여전히 ripgrep traceability 보존 (`rg @CODE:027-DLG` → 파일 1개), overhead 1/5 로 감소.

### 구체화 (실행 명세)

**비-EARS-worthy FR 자동 탐지 grep** (`/ms.specify` / `/ms.analyze` 가 실행):

```bash
SPEC="specs/N/spec.md"

# Preservation contracts (평서문 후보)
grep -nE 'SHALL (preserve|maintain|continue|keep)' "$SPEC"

# Type / shape declarations (평서문 후보 — schema 정의는 EARS 부적합)
grep -nE 'SHALL (have|contain|include|expose) (the )?fields?' "$SPEC"

# Constitution echo (이미 Constitution이 정의 — 중복)
grep -nE 'SHALL (follow|comply with|adhere to) (Constitution|Section)' "$SPEC"

# A11y / UX 정책 echo (해당 framework가 이미 정의)
grep -nE 'SHALL (read|render|display) (the )?title.*body.*' "$SPEC"
```

위 grep이 한 줄이라도 잡으면 후보 surface:

```
ℹ️  비-EARS-worthy FR 후보 N건 발견:
   FR-PRES-001 (line NN): "SHALL preserve the D5 ... layout"
   FR-PRES-002 (line MM): "SHALL preserve Feature 004's chat SSE flow"

평서문 변환 권장:
   - "D5 three-panel layout 유지."
   - "Feature 004 chat SSE 흐름 유지."

변환하시겠어요? (Y/n)
```

**평서문 변환 before/after 예시 (027 spec에서 추출)**:

| EARS 원본 | 평서문 개선 | 의미 손실 |
|---|---|---|
| FR-PRES-001: System SHALL preserve the D5 note-page three-panel desktop layout, mobile bottom-tab layout, center chat panel, left source panel, citation click behavior, note dropdown, and all existing keyboard shortcuts without modification. | "D5 note-page 의 three-panel desktop / mobile bottom-tab / chat / source / citation click / dropdown / 키보드 shortcut — 모두 변경 없음." | 없음 |
| FR-PRES-005: System SHALL preserve the D6 global color palette and token discipline; no 027 file SHALL introduce a color regression as detected by `scripts/check-token-discipline.sh`. | "D6 palette + token discipline 유지. `scripts/check-token-discipline.sh` 통과 필수." | 없음 |
| FR-ISO-001: System SHALL ensure that after `router.push` to the new note's URL completes, the previous note's chat panel state, citation highlights, quiz solving state, tentative answer buffer, selected source state, and studio filter/sort state are all reset / unmounted, so the new note's component tree mounts with fresh state keyed to the new `note_id`. | "router.push 완료 후 이전 note 의 chat / citation / quiz / tentative / source / studio state 는 모두 reset/unmount. 새 note tree 는 `note_id` keyed 로 fresh mount." | 없음 |
| FR-A11Y-007: System SHALL ensure mobile screen readers (VoiceOver iOS, TalkBack Android) read the title → body → cancel → primary in that order on dialog open. | "모바일 screen reader 읽기 순서: title → body → cancel → primary." | 없음 |

**ROI 양수로 유지 (EARS 형식 적합)**:

| FR | 왜 EARS 유지 |
|---|---|
| FR-DLG-012: WHILE async cleanup pending, system SHALL ... | conditional behavior — WHILE 가 의미 |
| FR-FLOW-005: IF tentative-save fails, system SHALL NOT call router.push | error gate — IF / SHALL NOT 가 의미 |
| FR-API-004: IF body fails validation, system SHALL respond HTTP 422 | error code enumeration — IF 가 enum 분기 |
| FR-CANCEL-001: WHEN user clicks 취소, system SHALL close dialog | event-driven — WHEN 가 trigger |

**TAG annotation 결정 매트릭스 (file-level vs line-level)**:

| 상황 | File-level @TEST 1개 | Line-level @TEST 각 함수 |
|---|---|---|
| 테스트 파일 케이스 수 ≤ 5 | ✓ 충분 | ✗ 불필요 |
| 테스트 파일이 1개 FR group 만 검증 | ✓ 충분 | ✗ 중복 |
| 테스트 파일이 여러 FR group cover (예: dialog.test.tsx 가 DLG + A11Y) | ✓ + group 별 1줄 | ✗ 여전히 과함 |
| 테스트 파일이 cross-spec 회귀 (fix-005 같은 경우) | ✓ + 회귀 대상 spec 들 1줄 | ✗ 폐기 |

**027 사례 검증**:
- `note-switch-dialog.test.tsx` 42개 케이스 — file-level `@TEST:027-DLG-001` 1개 + group 별 1줄 (`covers FR-DLG-001..012, FR-A11Y-001..007`) 로 충분
- 현재 17개 line-level annotation 은 redundant — file-level + group 1줄로 대체 가능
- traceability 보존 검증: `rg @CODE:027-DLG` → 1개 파일 hit, `rg "FR-DLG-005"` (test body grep) → 정확한 assertion line hit

---

## Issue 8 — 사용자 명시 요청 (2026-05-12)

027 세션 직후 사용자가 직접 요청한 UX 개선 사항. 위 issue 들과 달리 디자인 결정이 명시되어 있으므로 implementation 우선순위 높음.

### 8.1 영어 터미널 출력 축약

**증상**: 워크플로우 스킬 / 도구가 영어로 긴 출력 (10+ 라인) 을 dump 함. 사용자가 어차피 길게 읽지 않고 skim 함. token 낭비 + 신호/잡음 비 악화.

**개선 방향**:
- 모든 진행 / 상태 / 결과 출력은 **3-5 라인 한국어 요약** 으로 제한
- 영어 raw output 이 필요한 경우 (예: `gh pr checks` 결과) 는 첫 5 라인만 보이고 나머지는 "... 외 N건" 처리
- 풀 출력이 필요하면 사용자가 명시적으로 요청 (`--verbose` flag)

스킬 prompt 에 명시: "Final output to user: ≤5 lines Korean summary unless `--verbose`."

### 8.2 다음 스텝 안내 — 짧게, 반드시

**증상**: `/ms.implement` 같은 스킬이 작업 완료 후 "next step" 을 안내 안 하거나, 안내해도 길어서 skim 됨.

**개선 방향**: 모든 워크플로우 스킬은 출력 마지막에 **반드시** 다음 라인 포함:

```
👉 다음: /ms.implement (Phase 3 part 2 시작) | /finq (현재 상태로 PR)
```

조건:
- 한국어
- 1 라인
- 2-3개 옵션만 제시
- 가장 자연스러운 선택지를 첫 번째에

### 8.3 Phase progress 가시성

**증상**: `/ms.tasks` 완료 후 사용자가 "총 몇 개 phase 가 있는지" 모름. `/ms.implement` 완료 후 "몇 개 phase 남았는지" 모름. 매번 tasks.md 를 열어서 직접 세야 함.

**개선 방향**:

`/ms.tasks` 완료 출력에 추가:
```
✓ tasks.md 생성: 54 task / 8 phase
   Phase 0 (Setup) → 1 (Audit) → 2-3 (RED) → 4-5 (GREEN) → 6 (VR) → 7 (Polish)
```

`/ms.implement` 완료 출력에 추가:
```
✓ Phase 4 GREEN 완료 (11 task)
   진행률: 5 / 8 phase (62%)
   남은 phase: 3 (Phase 3 part 2 RED · Phase 6 VR · Phase 7 polish)
```

### 8.4 사용자 확인 prompt 는 한국어

**증상**: 일부 스킬이 사용자에게 확인을 요청할 때 영어 prompt 가 나옴 (예: `Type YES to proceed`). 영어 사용자가 아닌 경우 인지 부하.

**개선 방향**: 모든 `AskUserQuestion` 호출 + 모든 destructive action 의 confirm prompt 는 **한국어 강제**.

스킬 prompt 에 명시: "All user-facing confirmation prompts in Korean. No English-only `Type YES to proceed` patterns."

이번 027 세션의 `AskUserQuestion` 호출들은 이미 한국어였음 (good). 향후 추가될 destructive operation confirmations 도 같은 패턴 유지.

### 8.5 SLOC 제한 재조정

**증상**: Constitution Section V "Readable" 이 파일 크기 ≤500 SLOC 을 강제. 일부 파일이 실용적으로 500 라인 넘기는 경우가 있고, 특히 테스트 파일은 fixture + 수십 개 케이스로 빠르게 500 을 넘김.

**개선 방향**:
- **Production code SLOC 제한: 500 → 700 으로 상향**
- **테스트 파일 SLOC 제한: 폐지** (테스트는 길이보다 케이스 누락이 위험)

Constitution Section V 본문 수정:
```markdown
**Size Constraints**:
-   ✅ Production file ≤700 SLOC (Source Lines of Code, excluding comments and blank lines)
-   ✅ Test file SLOC: NO LIMIT (case coverage prioritized over file length)
-   ✅ Function ≤100 LOC
-   ✅ Parameters ≤5 per function
-   ✅ Nesting depth ≤4 levels
```

근거:
- 700 SLOC 은 substantial logic 모듈을 인위적 분할 없이 보존 가능
- 테스트는 fixture 공유 + parameterized 케이스로 자연스럽게 길어짐 — artificial split 이 readability 해침
- Complexity ≤10 per function 이 이미 maintainability 의 1차 가드

027 사례: `frontend/tests/components/note-switch-dialog.test.tsx` 가 122 → 1007 라인으로 확장됨 (3 variant × 14 케이스). Single file 이 자연스럽고 강제 분할은 오히려 케이스 추적 어려움. 새 제한 하에서는 정상.

---

## 우선순위 (전체 8개 issue 통합)

이 8개 중 사용자/팀 영향이 큰 순서:

1. **Issue 8 (사용자 명시 요청)** — 명시 요청이므로 즉시 implementation. 8.5 (SLOC) 는 Constitution amendment, 나머지는 스킬 prompt 수정만.
2. **Issue 4 (`/ms.plan` reality check 부재)** — 가장 자주 churn 을 만드는 원인. 한 단계만 추가하면 됨.
3. **Issue 5 (`/ms.implement` 스코프 + prompt 재주입)** — 매 호출의 ergonomic 비용. default scope 변경은 단순.
4. **Issue 6 (4-document drift)** — 자동 검증 + amendment 패턴 정형화 필요. 며칠 작업.
5. **Issue 3 (PR body 오탐)** — silent failure 가능성. 1-2 시간 작업.
6. **Issue 7 (EARS / TAG ceremony)** — spec 가독성 + ergonomic. 며칠 작업.
7. **Issue 1 (refactor mode 부재)** — D-track 작업 잦음. 며칠 작업.
8. **Issue 2 (post-impl clarification 경로)** — 장기 운영성. 며칠~일주일.

---

## 참고: 잘 작동한 패턴들 (균형 차원)

이 메모는 마찰점만 기록하지만 다음은 잘 작동한 패턴들:

### D6 세션에서 잘 작동한 것
- Q1-Q10 binding decisions (spec.md `## Clarifications` 섹션 + 매 commit message의 `Q?=X binding` cross-ref)
- TAG namespace 자동 충돌 방지 (`D6-*` 가 다른 spec과 충돌 안 함, `/ms.tasks` 시점에 verify)
- `scripts/check-token-discipline.sh` 의 "기존 도구 확장" 패턴 (새 linter 안 추가, 기존 ripgrep regex 한 줄만 확장)
- `/ms.analyze` 의 pre-impl validation 이 AA-Near contrast carve-out 을 사전에 surface
- `/finq` 의 explicit `STAGE_PATHS` discipline (parallel agent 의 backend stray modifications 가 D6 commit에 한 줄도 안 섞임)

### 027 세션에서 잘 작동한 것
- **EARS spec이 세션 사이 context 다리 역할**: 6번의 `/ms.implement` 호출 사이에 작업 컨텍스트 재구성을 가능하게 한 유일한 수단. 가장 큰 ROI.
- **Test-First 가 Round-2 pivot 을 일찍 surface**: Phase 2 RED 테스트 작성 도중 `attempts.selected_index` 없음 발견. GREEN 부터 시작했으면 잘못된 schema 위에 service 다 짠 뒤 발견했을 것.
- **Phase 단위 commit boundary 깔끔함**: 8 phase 를 7 commit 으로 끊었고 각 commit 이 self-verifiable (RED commit 은 실패가 기대값, GREEN commit 은 통과가 기대값).
- **Option B isolation regression test** (`test_tentative_save_does_not_write_to_attempts`): 단 한 줄 assertion 이 향후 design drift 를 영구히 막음. 작은 비용으로 큰 보호.
- **AskUserQuestion 한국어 일관성**: 모든 의사결정 prompt 가 한국어로 일관됨 (사용자 요청 8.4 의 baseline).

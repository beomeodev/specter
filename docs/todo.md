# TODO

<!-- Add working notes here. -->

## MoAI-ADK `.claude` 선별 도입 (2026-07-11 감사 → 07-12 승인 5건 → 07-13 3건으로 축소)

**배경**: modu-ai/moai-adk의 hooks/output-styles/rules 3축 감사 결과, 파일 단위 이식은 전부 불가
(훅 35개 중 31개가 `moai` Go 바이너리 위임 래퍼)이고 메커니즘 단위로 5건 도입이 확정됐으나,
07-13 도입 가치 재검토에서 **작업 1(Stop 게이트 phase-밖 경량 검사)·작업 2(SessionStart
dirty-snapshot)는 폐기** (재제안 금지). 폐기 근거: ① 실사고 근거 0건(07-10·07-11·07-13 감사
전부) — MoAI 메커니즘 이식이지 관찰된 실패의 처방이 아님 ② 실제 구멍이 작음(/ms.fix Step 5와
/ms.fin이 공개 전 같은 게이트를 이미 강제) ③ 스냅샷 제외 규칙의 자기모순(세션을 넘긴 깨진
dirty 파일 — 잡아야 할 바로 그 케이스 — 가 다음 세션부터 면제) ④ 훅 복잡도 비용은 실증됨
(specter-gate.sh false-FAIL 2건 전과)인데 효용은 미실증. 남은 3건(작업 3·4·5)만 진행.
output-styles 3종·@MX:DEBT·moai-memory·cadence-bridge·agent-patterns는 명시적 스킵(재검토 불필요).

**원본 참조가 필요하면**: `git clone --depth 1 https://github.com/modu-ai/moai-adk <scratchpad>/moai-adk`
- 작업 3: `.claude/rules/moai/core/verification-claim-integrity.md` / 작업 4:
  `.claude/rules/moai/workflow/session-handoff.md` §Diet Constraints. 아래 사양은 자립적으로
  작성했으므로 재클론 없이 진행 가능.

**공통 설계 원칙 (전 작업 구속)**:
- 커밋 분할: 보고 형식(작업 3) / 리뷰 체크리스트(작업 5) / 핸드오프 스킬(작업 4).

---

### 작업 3 — 검증 보고 형식에 Gaps / Residual-risk 필드

**목적**: 07-10 게이트 가치 감사의 원장 과소보고 문제 처방. "관찰하지 않은 것은 성공도 실패도
주장하지 않는다" 불변식을 보고 형식에 구조로 박음.

**수정 파일**: `.claude/skills/specter-agent-protocols/SKILL.md` (보고서 프로토콜 절 — §3 리포트
체크·§5 편향방지 독트린과 접합). 커맨드 파일들은 SSOT 포인터 구조이므로 원칙적으로 무수정 —
자체 보고 형식을 중복 정의한 커맨드가 있는지만 rg로 확인.

**추가 내용**:
1. 검증 보고 5섹션: **Claim** / **Evidence**(명령+출력 verbatim, 요약 금지) / **Baseline**(무엇 대비,
   이번 실행에서 측정) / **Gaps**(관찰하지 못한 것 — 방어적 핵심) / **Residual-risk**(관찰했음에도
   남는 위험). Gaps가 비면 "전수 관찰"의 근거를 요구 (빈 섹션 상투어 방지).
2. **결함 주장 대칭 규칙**: 결함/부채/드리프트 주장도 도메인 도구 확인 전까지 가설(UNVERIFIED) 표기.
   (moai 실사례: grep 추론 "29건 정리 필요" → 감사 도구 실행 결과 0건.) 기존 UNVERIFIED 마킹
   독트린을 결함 방향으로 한 줄 확장.
3. "증거 부재 ≠ 성공 증거, ≠ 실패 증거" 문구를 편향방지 독트린 옆에 배치.

**검증**: 편집 후 `/ms.verify` 1사이클 실행, 보고서에 Gaps가 실질 내용으로 채워지는지 확인.

---

### 작업 4 — 세션 핸드오프 스킬 신설 (+ Diet Constraints)

**목적**: MoAI v3 비교(메모리 moai-adk-comparison-2026-07)에서 1순위 채택 후보로 판정만 되고 미착수던
세션 핸드오프 실구현. 기존 자산이 절반 제공: `specter-run.jsonl` 원장(마지막 step/verdict)과
session-status 훅(다음 세션 상태 주입)이 이미 있으므로, 스킬은 **원장이 못 담는 것**(적용 교훈,
전제조건, 단일 실행 명령)에 집중.

**신규 파일**: `.claude/skills/session-handoff/SKILL.md` (§10 구조상 재사용 능력 = skills).

**형식 (moai 6블록 축소 — 현지화 테이블·mode-seeding·CLI 저장 연동 전부 제외)**:
```text
✂──── 여기부터 복사 ────✂
<Feature/작업> <단계> 재개.
적용 교훈: <메모리/원장 참조, 최대 4줄>

전제 검증:
1) <검증 가능한 명령> → <기대 결과>   (최대 4개, 각 200자 이내)

실행: <단일 명령 또는 액션 1개>

후속: <머지 후/다음 Feature, 최대 2줄>
✂──── 여기까지 복사 ────✂
```

**발동 트리거 (SPECTER 적응)**: ① 컨텍스트 임계 접근(수치는 구현 시 판단) ② `/ms.specter` Feature
완료 시 다음 Feature 잔존 ③ 사용자의 명시적 세션 종료 의사("세션 종료", "내일 이어서" 등)
④ `/ms.fin` PR 생성 + 미완 Feature 잔존.

**Diet Constraints (안티패턴으로 명문화)**: 재개 메시지는 "다음 세션 최소 실행 컨텍스트"이지 감사
기록이 아님 — 이력 서사 금지 / 의례적 리마인더 금지 / 다단계 서브스텝 인라인 금지 / 재시도 거치며
늘어난 문장은 삭제 / 상한 초과분은 메모리 파일로 이동. 출력 순서: 펜스 블록 → (저장 시) 파일 경로 →
한 문장 요약. 저장 실패 fail-open.

**중복 정리**: session-status 훅 주입과 겹치는 내용(마지막 step, 다음 Feature)은 핸드오프 블록에서
전제 검증 명령으로만 참조하고 본문 중복 금지.

**검증**: testing-skills-with-subagents 적용 대상(규율 강제 스킬) — RED(스킬 없이 핸드오프 시켜
비대해지는지 확인) → GREEN(스킬 로드 후 상한 준수) 최소 1라운드. `/ms.sync` 배포 전 필수.

---

### 작업 5 — /ms.review에 경계 검증 체크리스트 7종

**목적**: 유닛테스트가 구조적으로 못 잡는 경계(seam) 버그를 리뷰 체크리스트로. API/프론트/DB 경계나
상태머신을 건드린 Feature에만 **조건부** 적용 (전 리뷰 강제 아님 — 의례 최소화).

**수정 파일**: `.claude/commands/ms.review.md` — 기존 절차에 "경계 검증(조건부)" 절 추가.

**체크리스트 7종**:
1. API 응답 shape 불일치가 제네릭 캐스팅(`as T` 등)으로 은폐되지 않았는가
2. 파일 경로 ↔ 라우터 매핑 불일치 (route group / dynamic segment)
3. 상태머신에 정의만 되고 구현 안 된 전이(dead transition)가 없는가
4. camelCase ↔ snake_case 필드명이 DB/API/프론트 계층 간 드리프트 없는가
5. 프론트가 호출하는 API 엔드포인트가 실제 구현돼 있는가
6. 비동기 워크플로우의 복수 응답 shape(즉시 202 vs 최종 결과)이 타입으로 유니온돼 있는가
7. 타입 캐스트 우회로 숨은 실제 shape 불일치가 없는가
+ 방법론 한 줄: "경계는 양쪽을 함께 읽는다 — 한쪽씩 검사한 통과는 경계 통과가 아님".

**검증**: 문서 수정 렌더 확인 + 다음 실전 `/ms.review`에서 조건부 발동 관찰.

---

### 실행 순서 및 완료 기준

1. 작업 3 → 2. 작업 5 (경량 문서) → 3. 작업 4 (스킬 신설 + 서브에이전트 압박 테스트, 가장 무거움).
(작업 1+2는 07-13 폐기 — 배경 절 참조.)

완료 기준: 커밋 3개 분할 / 핸드오프 RED·GREEN 1라운드 통과. (신규 스킬은 sync 매니페스트
`.claude/skills/*` 글롭이 커버하므로 별도 배포 경로 검증 불요.)

---

## 인사이트 감사 후속 (2026-07-13, 2건)

**배경**: 07-13 /insights 감사(224세션, facet 100건 직접 집계). 게이트 실효는 재실증(리뷰가
BLOCKER·race·경계버그 실적발 다수, 날조 verdict 적발·에스컬레이션 포함). 남은 구멍 2개는 둘 다
"게이트 자체"가 아니라 **게이트 주변부**: ① 위임 파이프라인의 무음 정지를 매번 임기응변 복구,
② 컨덕터의 단계 스킵을 게이트가 아닌 사용자가 적발. 오버나이트 관련 항목은 폐기됐으므로 제외.
MoAI 5건과 독립 — 어느 시점이든 착수 가능, 각 1커밋.

### 작업 6 — /ms.fin·/ms.merglease 위임 종료 후 상태 검증

**목적**: Antigravity 위임 무음 정지 실사례 2건(merge까지 하고 tag/release 미생성 정지 /
커밋 전 정지). 현재 `/ms.merglease`의 폴백은 "위임 **시작 실패**"만 커버하고 **부분 완료 후
정지**는 무검증 — 위임 리포트를 믿지 말고 종상태를 기계적으로 확인하는 스텝을 표준화.

**수정 파일**: `.claude/commands/ms.fin.md` (Step 3 위임과 Step 4 성공 보고 사이에 검증 스텝
삽입), `.claude/commands/ms.merglease.md` (Step 1 위임과 Step 2 성공 보고 사이에 동일 패턴).

**사양**:
1. **검증 항목 (git/gh로 직접 확인, 위임의 자기 보고 불신)**:
   - ms.fin: ① 커밋 예정 변경이 작업트리에 안 남았는가(`git status --porcelain`)
     ② 브랜치 push 완료(`git log origin/<branch>..HEAD` 비었는가) ③ PR 존재+open
     (`gh pr view --json state,url`). 셀프리뷰 스탬프는 fail-open 설계이므로 상태 보고만.
   - ms.merglease: ① PR merged(`gh pr view --json state,mergedAt`) ② 로컬 master가 머지
     커밋까지 pull됨 ③ 태그 존재+리모트 반영(`git tag -l`, `git ls-remote --tags origin`)
     ④ Release 존재(`gh release view <tag>`) ⑤ progress ledger 커밋 master 반영(파일 존재 시).
2. **누락 항목만 직접 완결** (멱등 — 전체 재실행 금지), 성공 보고에 명시:
   `위임 완주` 또는 `부분 정지 → <항목> 직접 완결`.
3. **의도적 중단과 구분**: 위임 리포트에 중단 사유가 명시된 경우(실 CI 실패로 머지 중단 등)는
   빈 단계를 채우지 말고 기존 규칙대로 실패 보고. 이 검증은 **무음** 정지 전용.
4. 검증 스텝 자체는 read-only 명령 + 누락 복구뿐 — 새 게이트/verdict 아님(§10 identity 유지).

**검증**: 문서 렌더 확인 + 시뮬 1회(로컬에서 태그만 지운 상태를 가정하고 검증 로직이 누락을
감지·복구하는지 수동 수행) + 다음 실전 `/ms.fin`→`/ms.merglease`에서 발동 관찰.

### 작업 7 — /ms.specter 단계-순서 가드 (step-skip guard)

**목적**: 컨덕터가 checklist·agent-verify를 건너뛰고 clarify로 직행한 실사례를 사용자가 수동
적발(07-13 감사; 07-10 감사의 런타임 게이트 홀과 동일 계열). 게이트는 호출되면 작동함이 실증
— 구멍은 "호출됐는지"를 아무도 확인하지 않는 것. 원장(`.specify/specter-run.jsonl`)을 현재
resume 단축용으로만 읽는데, 같은 데이터를 **순서 불변식 검증**에도 사용.

**수정 파일**: `.claude/commands/ms.specter.md` — Step 0.5(원장 재개 절) 확장 + 단계 진입
공통 규칙 1줄. `/ms.pre-specter`도 같은 컨덕터 패턴이므로 확인 후 해당 시 동반 수정.

**사양**:
1. **진입 불변식**: 시퀀스 `checklist → agent-verify → specify → clarify → plan → tasks →
   analyze → implement → review`에서 step N 실행 전, 모든 선행 단계에 이 Feature의
   PASS/WARN 원장 기록(기존 last-entry-wins 규칙)이 존재해야 함. 없으면 N을 실행하지 않고
   첫 누락 단계로 되돌아가 실행 — 무음 스킵 금지.
2. **fail-open 경계 명문화**: 원장 부재/손상 시 기존대로 Step 1부터 정상 시작(차단 아님).
   단 fail-open의 의미는 "처음부터 시작"이지 "중간 단계 무검증 진입"이 아님을 명시.
3. **사용자 명시 지시와의 관계**: 사용자가 특정 단계 시작을 지시한 경우("ms.plan부터")에도
   선행 기록을 확인하고, 누락이면 무단 진행 대신 누락 단계를 보고하고 1회 확인을 받음
   (사용자 재량은 존중, 금지 대상은 컨덕터의 무음 스킵뿐).
4. 이 가드는 순서 강제일 뿐 각 게이트의 verdict 판정에 관여하지 않음 — 게이트 약화 금지
   (§10 identity 규칙).

**검증**: 원장에 checklist 기록이 없는 상태를 수동 구성해 `/ms.specter`가 plan 직행을
거부하고 checklist로 되돌아가는지 시뮬 + 기존 정상 재개 경로 회귀 확인.

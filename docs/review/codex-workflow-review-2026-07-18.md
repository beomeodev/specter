# Codex External Review — 2026-07-18

**Agent**: Codex (gpt-5.6-sol, effort max, adversarial mode)
**Scope**: (1) DDD 도입 세션 결정에 대한 2차 의견, (2) 질문 이력 기반 워크플로우 구조 개선안
**Note**: Codex 샌드박스가 읽기 전용이라 본 파일은 호스트가 세션에 수신된 Codex 출력을
그대로 옮겨 저장한 것이다. Part 1은 전문, Part 2는 포워더가 축약 반환한 판본이다
(전문 재요청 필요 시 Codex 스레드 019f7496-eec8-7902-8fe0-73f4402ff20b resume).

---

## Part 1. DDD 세션 적대적 2차 의견 (전문)

**1. 감사 방법론 (7일·5개 프로젝트·72세션 표본)**
부분동의. 탐색적 우선순위 결정에는 유효하나, "유일한 결함 클래스"라는 일반화와 "기존
게이트로 충분"이라는 결론은 표본 크기를 넘어선다. `7073c6b`가 이 관찰을 운영 문안에
영구 고정한 것이 문제. 미보고 오류·감사 기간 전 유입 결함·인과관계(게이트 덕분인지
사람 개입 덕분인지 미분리)가 빠짐.

**2. 전략적 DDD 기각 ("재제안 금지")**
부분동의. 즉시 도입 보류는 타당하지만 영구 기각은 과함. 브리프 스스로
`chat_orchestrator.py` 1016줄의 살아있는 부채를 인정하면서도 7일 관찰창만으로 결론 냄.
경계 침식은 단기간 사고로 드러나지 않고 누적되는 성질이라 "현재 보류 + 재평가 트리거
조건"이 맞는 결론.

**3. 상태 소유권 게이트 (`ms.plan.md`/`ms.review.md`, `7073c6b`)**
부분동의 — 우회 구멍 다수 확인.
- 상태 머신 정의가 "status/lifecycle field with transitions"로 좁아,
  boolean/timestamp/lease/counter로 구현된 암묵적 상태 머신은 정의를 빠져나갈 수 있음.
- review는 `rg`로 status 필드 mutation만 검사 — 별칭 필드, ORM helper, 외부 API 간접
  쓰기는 놓침.
- 비원자적 reconciliation(두 store)의 재시도/멱등성/부분실패 복구 검증 요구가 없음.
- 이 섹션 누락 시 등급이 `MEDIUM`에 그쳐, 워크플로가 진행을 막지 않는다면 가장 중요한
  선언을 생략할 유인이 생김.
- `ms.implement.md`는 이 커밋에서 수정되지 않아, plan이 요구한 불변조건 테스트 의무를
  구현 단계가 실제로 소비하는지 diff상 보강 없음.

**4. 위임 규율/제척 (`ms.implement.md`/`ms.review.md`, `d87a7f2`)**
부분동의 — 명시적 부분위임/선례상속 차단은 강하나 구조적 구멍 있음.
- 제척이 구현자의 `implementation-notes.md` 자기신고(`External implementation:` 기록)에
  의존 — 원래 위반(무승인 위임)을 한 에이전트가 기록을 생략하면 review가 탐지 불가.
  위반을 위반자의 자기신고로 통제하는 구조.
- `<Agent>` 필드가 자유형식이라 내부 subagent/다른 도구명/모델 별칭으로 동일성 판정
  회피 가능.
- 실제 diff에서 제척 소비자 추가는 `ms.review.md`뿐 — `AGENTS.md`의 "verification
  stations" 복수형 표현과 달리 다른 스테이션 적용 변경은 없음.
- 제척 후 대체 reviewer 없이 단일 reviewer로 격하되는 부작용, "cap at WARN" 문구가
  FAIL 유지용 상한인지 FAIL까지 강등 지시인지 모호.

**5. 세션에서 누락된 질문**
동의 — 중요한 누락. 핵심 미해결 질문: "이 프롬프트 기반 게이트가 실제로 준수되는지
회귀 검증/측정할 방법은?" 두 diff 모두 command Markdown과 `AGENTS.md`만 변경했을 뿐,
과거 사고 재현 fixture나 준수 검사, 누락 탐지 메커니즘이 없음. 또한 "어떤 신호·기간이
되면 DDD 결정을 재검토하는가"라는 재평가 트리거 질문이 빠졌음 — 7일 데이터로 내린
결론에 "재제안 금지"를 건 것은 새 증거 유입 시 교정 경로가 없다는 뜻.

---

## Part 2. 워크플로우 구조 개선안 (포워더 축약본)

### (a) 공통 뿌리 진단

공통 병인은 **실행–증거–개선의 폐쇄 루프가 기계적으로 연결되지 않은 것**이다.
SPECTER에는 훅과 검증 스크립트가 있지만, 워크플로우 진행·권한 판단·결과 기록·구성요소
수명주기의 상당 부분은 Markdown 명령을 에이전트가 해석하고 자기보고하는 방식이라 매번
transcript 전수 감사로 재구성해야 한다.

근거: `AGENTS.md:8` (스스로 "not a hard enforcement layer"), `ms.specter.md:137`
(원장을 에이전트가 읽어 단계 판정), `ms.review.md:667` (원장 append가 shell printf로
산개), `ms.audit.md:98` (수동 자문형이라 자동 피드백 루프 아님),
`docs/templates/scripts/specter-stop-gate.sh:22` (fail-open 공백), `CHANGELOG.md:34` vs
`.claude/settings.local.json:34,56-62` (context7/fin.md/finq.md/ms.amend.md 등 죽은
참조 잔존 — 수명주기 드리프트 실물 증거).

### (b) 구조적 개선안 Top 5

1. **P0** 실행 가능한 워크플로우 제어면 도입 — 단계 전이·제척·override 판정을
   Markdown이 아닌 코어(CLI/상태 머신)가 하도록 (`ms.specter.md:137`,
   `ms.implement.md:194` 근거)
2. **P0** 중앙 이벤트 writer + 자동 게이트 가치 관측 — 산개된 printf 대신 단일
   `specter record` (`ms.agent-verify.md:212`, `ms.review.md:667` 근거)
3. **P1** 역사적 사고 기반 워크플로우 회귀 테스트 — 현재 테스트는 TAG/Feature Map만
   커버 (`tests/specter/test_specter_gate.py:89` 등)
4. **P1** 생성형 consumer graph + liveness CI — 수동 레지스트리 대신 정적 참조+실행
   이벤트 결합 (`.claude/settings.local.json:56` 죽은 참조 근거)
5. **P2** uv 패키지·renderer·driver registry 완성 — README 로드맵은 있으나
   `pyproject.toml:1`에 `[project.scripts]` 미비, `scripts/specter/specter_sync.py:54`
   개인 identity 하드코딩 잔존

### (c) 아직 안 물어본 질문

1. **"누가 human override를 행사할 수 있는가?"** — `ms.init.md:428`은
   `git commit --no-verify`를 human 전용 admin bypass로 설명하지만,
   `.claude/settings.local.json:26,75`는 agent에게 동일 명령을 허용(`deny: []`).
   human/agent를 구별할 기계적 주체와 override 영수증 발급 주체가 미정의.
2. **"SPECTER 순효과의 반사실 기준은?"** — `ms.audit.md:102`의 catch=0 sunset 기준과
   `specter-agent-protocols/SKILL.md:74`의 "absence of evidence is not evidence"가 긴장
   관계. catch 수만이 아니라 escaped defects/lead time/토큰/false-positive를 함께 봐야 함.
3. **"Transcript 감사 데이터의 보존·비식별화·접근 정책은?"** —
   `transcript-mining/SKILL.md:8`이 raw `~/.claude/projects/*/*.jsonl`을 순회하지만
   redaction/보존기간/프로젝트 간 접근 경계 미명시.

### Codex 부기

`docs/SYSTEM_MAP.md`는 stale(git_head 2e6732a, 현재 HEAD d87a7f2)해서 구조 판단은
실시간 파일 검색으로 대체. `graphify-out/graph.json`과
`.specify/memory/constitution.md`는 이 저장소에 존재하지 않음.

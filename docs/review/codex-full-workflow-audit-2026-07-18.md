# Codex Full Workflow Audit — 2026-07-18

**Agent**: Codex (gpt-5.6-sol, effort xhigh, 29m). **Scope**: AGENTS.md + ms.* 전 명령 + 워크플로우 스킬 7종 + settings + 템플릿 스크립트 + scripts/specter + tests/specter. **중복 제외**: codex-workflow-review-2026-07-18.md 기보고 사항.

기존 리뷰를 먼저 읽고, 이미 보고된 상태 소유권의 좁은 탐지, 구현 위임 자기신고, no-change Stop-hook 공백, `fin.md`·`finq.md`·`ms.amend.md` 등 기존 죽은 설정 참조, `--no-verify` human override, transcript 비식별화 문제는 반복하지 않았다. 아래는 새 발견 또는 새 증거로 심화된 항목이다. CRITICAL은 없었다.

## 발견

1. [HIGH] pre-conductor가 정상 경로에서 `codex-checklist`를 영원히 완료로 인정하지 못한다 — 근거: `.claude/commands/ms.codex-checklist.md:187,193`, `.claude/commands/ms.pre-specter.md:135-149`. 전자는 원장에 항상 `PENDING`만 기록하며 이후 승격하지 않는다고 명시하지만, 후자는 `PENDING`을 미완료로 취급하고 `verify` 진입 전 `PASS/WARN`을 요구한다. 규칙대로 실행하면 Step 2를 반복하거나 순서 가드를 우회해야 한다.

   권장: 산출물 검증 완료 시 conductor가 `codex-checklist: PASS/WARN`을 append하거나, 유효한 산출물과 `PENDING` 조합을 완료 상태로 정의하라.

2. [HIGH] 단일 에이전트 degrade가 실제 per-Feature 게이트를 통과할 수 없다 — 근거: `.claude/skills/specter-agent-protocols/SKILL.md:31-37`, `.claude/commands/ms.agent-verify.md:71-78`, `docs/templates/scripts/specter-gate.sh:203-225`, `.claude/commands/ms.specify.md:141-151`. 프로토콜은 누락 에이전트 파일을 `UNAVAILABLE`로 쓰고 WARN으로 계속하라고 하지만, 결정적 게이트는 정확히 `PASS|WARN`만 허용한다. 따라서 환경 문제만으로 cycle이 차단된다.

   권장: 누락 보고서에 `**Result**: WARN`과 별도 `Availability: UNAVAILABLE`을 기록하거나, 게이트가 `UNAVAILABLE`을 인식해 전체 결과를 WARN으로 cap하도록 통일하라.

3. [HIGH] 과거 dual-agent 보고서를 새 체크리스트에 재사용할 수 있다 — 근거: `docs/templates/scripts/specter-gate.sh:203-225`, `.claude/commands/ms.agent-verify.md:129-134,175-180`, `tests/specter/test_specter_gate.py:48-64`. 게이트는 검증 보고서에서 `Result`만 읽고 Feature, Mode, checklist SHA, Feature Map SHA를 확인하지 않는다. 테스트도 `**Result**: PASS` 한 줄짜리 보고서를 유효한 것으로 고정한다. Feature Map과 checklist를 다시 만들고 에이전트 검증만 생략해도 오래된 PASS가 통과한다.

   권장: 두 보고서에 Feature·checklist SHA·Feature Map SHA·Mode를 필수화하고 게이트에서 모두 검증하라.

4. [HIGH] direct-specify hook의 토큰이 Feature별로 결합되지 않는다 — 근거: `docs/templates/scripts/speckit-specify-gate-hook.sh:5,38-40`, `.claude/commands/ms.specify.md:168-185`. 주석은 “matching token”을 요구한다고 설명하지만 구현은 최근 60분 이내의 `.ms-gate-pass-*`가 하나라도 있으면 허용한다. Feature 006 토큰이 살아 있는 동안 다른 Feature 또는 freeform direct specify 호출도 허용될 수 있다.

   권장: tool input에서 Feature 번호를 추출해 정확한 토큰과 대조하고, 토큰 내용에 입력/체크리스트 SHA를 저장한 뒤 1회 소비하라.

5. [HIGH] `/ms.expand`의 Codex delta checklist는 생산되지만 소비되지 않는다 — 근거: `.claude/commands/ms.expand.md:137-161,215`. Codex 작업을 background로 시작하지만 대기·salvage·결과 판독 없이 host+Antigravity audit으로 진행하고 canonical checklist의 Result와 SHA를 갱신한다. 저장소 전체에서 `checklist-delta-N.md`의 후속 사용은 번호 산정과 최종 보고뿐이다.

   권장: Step 3을 명시적인 join point로 만들고 Codex delta 산출물의 존재·형식·결과를 검증에 포함하거나, 실질적으로 사용하지 않는 Step 2를 제거하라.

6. [HIGH] clarify와 analyze 게이트는 후속 명령이 소비하지 않는다 — 근거: `.claude/commands/ms.plan.md:22-32`, `.claude/commands/ms.analyze.md:263-265`, `.claude/commands/ms.implement.md:63-79`, `.claude/commands/ms.specter.md:83,160`. `/ms.plan`은 spec 존재만 확인하므로 mandatory clarify를 건너뛸 수 있고, `/ms.implement`는 문서 존재만 확인하므로 analyze가 없거나 FAIL이어도 직접 실행된다. conductor도 사용자 확인 한 번으로 누락 선행 단계를 허용한다.

   권장: 각 후속 명령이 이전 단계의 Feature-bound PASS/WARN attestation을 직접 검증하도록 하라.

7. [HIGH] DAG 완료 의미가 `merged/done`에서 `specified/started`로 약화되어 있다 — 근거: `.claude/commands/ms.featuremap.md:58,220`, `.claude/commands/ms.checklist.md:160-164`, `.claude/commands/ms.specify.md:217-228`. Feature Map은 선행 Feature가 main에 merge된 상태에서 다음 Feature를 시작한다고 정의하지만, checklist는 “specified or shipped”, specify는 단지 `specs/` 디렉터리 존재를 충족으로 본다. 선행 구현이 끝나지 않은 dependent Feature가 정상 경로에서 시작될 수 있다.

   권장: 계획 병렬성과 구현 의존성을 분리하거나, “eligible”을 review+merge/shipped 중 하나로 단일 정의하라.

8. [HIGH] `parallel-features`가 재작성 파일을 append-only로 오분류한다 — 근거: `.claude/skills/parallel-features/SKILL.md:29-44`, `.claude/commands/ms.specify.md:217-219`, `.claude/commands/ms.merglease.md:95-100`. `feature-map.progress.md`에 union merge를 설정하지만 `/ms.specify`는 모든 Status 행을 다시 쓰고 `/ms.merglease`도 기존 행을 수정한다. 두 worktree의 union merge는 중복 행이나 상충 상태를 함께 보존할 수 있다.

   권장: Progress Ledger를 Feature별 fragment로 분리해 재생성하거나, 구조를 이해하는 전용 merge/reconcile 단계로 대체하라.

9. [HIGH] `/ms.review`의 필수 문서 규칙이 파일 내부에서 정반대로 정의된다 — 근거: `.claude/commands/ms.review.md:99-100,754-755`. Step 1은 spec 또는 plan 누락 시 절대 진행하지 말라고 하지만 Error Handling은 plan 누락 시 제한된 context로 계속하라고 한다. 어느 지시를 따르느냐에 따라 review gate가 달라진다.

   권장: 누락 문서별 차단/경고 행렬을 하나만 두고 Error Handling을 동일한 결과로 맞춰라.

10. [HIGH] review의 HIGH finding이 `NOT READY`인지 `READY WITH WARNINGS`인지 결정할 수 없다 — 근거: `.claude/commands/ms.review.md:359-367,410-414`. 같은 섹션에서 unresolved HIGH가 CRITICAL trigger라고 한 직후, “only HIGH/MEDIUM warnings”는 WARNING trigger라고 정의한다.

    권장: severity→trigger→최종 verdict 매핑을 단일 표로 만들고 다른 문단에서는 재정의하지 말라.

11. [MEDIUM] analyze WARN의 진행 조건이 conductor에서 약화된다 — 근거: `.claude/commands/ms.analyze.md:264`, `.claude/commands/ms.specter.md:252-257`. analyze는 사용자가 경고를 acknowledge한 뒤 구현할 수 있다고 하지만 conductor는 자체적으로 경고 목록에 기록하는 것을 acknowledgement로 간주한다.

    권장: 실제 사용자 확인을 기다리거나, analyze의 WARN을 명시적으로 자동 진행 가능한 verdict로 바꿔라.

12. [MEDIUM] migration Feature에는 conductor가 문서화하지 않은 추가 human stop이 있다 — 근거: `.claude/commands/ms.specter.md:10,219,305-314`, `.claude/commands/ms.review.md:484-508`. conductor는 clarify를 유일한 필수 human interaction으로 설명하고 review를 PASS/WARN 판독 단계로만 다루지만, review는 migration 분석에 명시적 사용자 ack가 없으면 CRITICAL로 규정한다.

    권장: migration ack를 conductor Stop Conditions와 resume 규칙에 추가하라.

13. [HIGH] review가 NOT READY여도 게시·릴리즈까지 진행할 수 있다 — 근거: `.claude/commands/ms.review.md:658-660,723-724`, `.claude/commands/ms.fin.md:29,153-154`, `.claude/commands/ms.merglease.md:17-19`. review-state는 publish blocker가 아니며 `--no-ci`는 경고만 출력하고 PR을 게시한다. 이 WIP 상태를 막는 영속 marker가 없어 merglease는 “이미 local gate를 통과했다”고 전제할 수 있다.

    권장: unresolved CRITICAL/HIGH 또는 `--no-ci` publish에 merge-blocking WIP marker를 남기고 `/ms.merglease`가 이를 강제 확인하게 하라.

14. [HIGH] `/ms.fin`의 “review 후 변경 없음” 판단이 untracked 파일을 보지 않는다 — 근거: `.claude/commands/ms.fin.md:114-123`. 현재 파일 집합을 `git diff`와 cached diff로만 만들기 때문에 review 뒤 추가된 untracked 코드·migration은 해시 비교에서 사라진다. 기존 review cache와 나머지 파일이 일치하면 CI를 SKIP하고 새 파일을 게시할 수 있다.

    권장: `git status --porcelain` 기반으로 untracked·deleted·renamed를 포함하고, review 시점과 fin 시점에 동일한 파일 집합 산정기를 사용하라.

15. [HIGH] `/ms.merglease --no-release`는 선언만 있고 소비자가 없다 — 근거: `.claude/commands/ms.merglease.md:3,89-94`. argument hint에는 `--no-release`가 있지만 본문에서 한 번도 분기하지 않고 항상 tag와 GitHub Release를 생성한다. 사용자가 명시적으로 릴리즈 생성을 금지해도 반대로 실행된다.

    권장: tag/release 단계를 실제로 건너뛰도록 구현하고 end-state 검증도 해당 flag에 맞춰 조건화하라.

16. [HIGH] Stop gate evidence가 현재 phase나 실제 gate 실행과 결합되지 않는다 — 근거: `docs/templates/scripts/specter-stop-gate.sh:101-104,141-153`, `tests/specter/test_stop_gate.py:94-99`. hook은 evidence의 `sig`만 비교하고 저장된 `phase`와 `verdict`를 읽지 않는다. 따라서 `record implement PASS`가 review phase를 만족할 수 있고, `record` 자체는 어떤 테스트 실행 증거도 요구하지 않는다.

    권장: phase 일치와 phase-open 이후 timestamp를 검증하고, 수동 verdict가 아니라 gate wrapper가 만든 실행 영수증을 소비하라.

17. [HIGH] Feature Map 삭제가 pre-commit backstop을 통과하도록 명시적으로 구현·테스트되어 있다 — 근거: `scripts/specter/check_feature_map_gate.py:57-62`, `tests/specter/test_check_feature_map_gate.py:108-113`. “normative Feature Map edit”를 보호한다고 설명하지만 staged deletion이면 곧바로 성공한다.

    권장: 삭제를 기본 FAIL로 만들고, 의도적 전체 해체에만 별도 human/admin override를 요구하라.

18. [HIGH] `/ms.init`은 direct-call 방어 설치 실패를 성공으로 보고한다 — 근거: `.claude/commands/ms.init.md:227-242,290,479-485`. upstream specify 후보가 없거나 jq/settings가 없어 hook 설정이 빠져도 비치명적으로 계속하며, 최종 보고는 PreToolUse entry가 설치됐다고 고정 출력한다. 비우회 불변식의 핵심 방어가 없는 프로젝트를 “initialized successfully”로 만든다.

    권장: upstream specify entry가 없거나 hook 등록·read-back 검증이 실패하면 초기화를 FAIL시키거나 최소한 불완전 설치 verdict를 반환하라.

19. [MEDIUM] `/ms.init`의 pre-commit 업그레이드가 부분 설치를 복구하지 못한다 — 근거: `.claude/commands/ms.init.md:393-418`. `check_tag_chain.py` 문자열 하나만 있으면 두 backstop이 모두 설치됐다고 간주한다. 구버전 프로젝트에 TAG hook만 있으면 Feature Map hook은 영원히 추가되지 않는다.

    권장: 두 hook ID를 각각 검사하고 누락된 항목만 개별 append하라.

20. [HIGH] sync 엔진이 target symlink를 따라 clone 밖을 읽거나 덮어쓸 수 있다 — 근거: `scripts/specter/specter_sync.py:252-263,318-319,332-333`. 대상 managed path에 대해 `lstat`나 clone-root 경계 검증 없이 `read_bytes`/`write_bytes`를 사용한다. 등록된 target 저장소가 해당 파일 또는 상위 디렉터리를 외부 경로 symlink로 바꾸면 sync 프로세스의 파일 권한으로 clone 밖에 접근할 수 있다.

    권장: target 경로의 모든 구성요소에서 symlink를 거부하고, `resolve()` 결과가 clone root 내부인지 검증하며 target-symlink 회귀 테스트를 추가하라.

21. [HIGH] settings의 자동 허용 범위가 AGENTS 권한 규칙과 deny를 우회한다 — 근거: `AGENTS.md:143-159`, `.claude/settings.json:13,18,25`, `.claude/settings.local.json:11,16,40,75-76`. `git restore:*`는 사용자 변경을 폐기할 수 있고 `uv sync:*`는 승인 없이 의존성을 변경한다. `python3:*`, `xargs:*`, `tee:*`는 literal `rm -rf` deny에 걸리지 않는 임의 쓰기·삭제 경로이며 별도 ask 규칙도 없다. review/audit도 별도 확인 없이 서버·dependency install을 지시한다(`ms.review.md:438,451`, `ms.audit.md:63-66`).

    권장: `git restore`와 `uv sync`를 ask로 옮기고, Python/xargs/tee allow를 목적별 명령으로 축소하며 server/install의 approval-by-invocation 여부를 AGENTS에 명시하라.

22. [MEDIUM] canonical verification-report 구조가 실제 어떤 보고서에도 적용되지 않는다 — 근거: `.claude/skills/specter-agent-protocols/SKILL.md:110-126`, `.claude/commands/ms.agent-verify.md:129-141`, `.claude/commands/ms.analyze.md:166-176`, `.claude/commands/ms.review.md:579-589`. 프로토콜은 모든 검증 보고서에 Claim/Evidence/Baseline/Gaps/Residual-risk를 요구하지만 명령 템플릿은 Findings/Verdict만 만든다. 결정적 검사는 `**Result**:` 존재만 본다(`specter-agent-protocols/SKILL.md:48-55`).

    권장: 모든 report template을 canonical schema로 통일하고 section·Feature·SHA를 검사하는 validator를 추가하라.

23. [MEDIUM] 비표준/split Feature Map 지원이 conductor·wrapper·gate 사이에서 다르다 — 근거: `.claude/commands/ms.specter.md:44,97-99,133,209`, `.claude/commands/ms.specify.md:47-55`, `docs/templates/scripts/specter-gate.sh:181-188`. conductor는 attached map을 authoritative로 보지만 `/ms.specify`에는 section만 전달한다. specify는 conventional master를 단일 경로라고 주장하는 반면 gate는 split-slate map을 지원한다.

    권장: resolved Feature Map path를 conductor가 명시적으로 전달하고 모든 gate/checklist/report가 같은 canonical path를 사용하게 하라.

24. [MEDIUM] TAG 다중 파일 규칙이 서로 모순된다 — 근거: `.claude/commands/ms.tasks.md:273`, `.claude/commands/ms.implement.md:292-296`, `scripts/specter/check_tag_chain.py:133-134`. tasks는 CODE/TEST multi-file을 모두 허용한다고 하지만 implement와 backstop은 CODE ID를 정확히 한 파일에만 허용한다.

    권장: tasks 오류 문구를 “TEST만 다중 허용, CODE는 유일”로 고쳐 단일 규칙을 유지하라.

25. [MEDIUM] TAG·review·docs 도구가 서로 다른 소스 루트를 사용한다 — 근거: `scripts/specter/check_tag_chain.py:31-46`, `.claude/commands/ms.tasks.md:132,160`, `.claude/commands/ms.review.md:97,165`, `.claude/commands/ms.up-docs.md:99`. backstop은 `app/lib/packages`까지 보지만 TAG 생성기는 보지 않고, review/up-docs는 주로 `src/tests`만 본다. 반대로 일반적인 Go `cmd/internal` 등의 구조는 모두 누락된다.

    권장: project-configurable scan roots/suffixes를 한 곳에 정의하고 모든 producer/validator가 공유하게 하라.

26. [MEDIUM][UNCERTAIN] audit가 명시적 소비자가 없는 trust-validation 실행을 전제로 보안 검사를 생략한다 — 근거: `.claude/commands/ms.audit.md:86-87`, `.claude/skills/trust-validation/SKILL.md:18-21`. 저장소 전체 참조에서 trust-validation을 실제 호출하는 workflow command는 없으며 audit만 “이미 per-Feature에서 수행됐다”고 가정한다. 자동 skill 선택이 우연히 실행할 수는 있으나 workflow 보장은 아니다.

    권장: `/ms.review`가 skill을 명시적으로 호출하고 영수증을 남기게 하거나, audit가 해당 영수증이 없으면 code-level OWASP 검사를 생략하지 않게 하라.

27. [MEDIUM] trust-validation의 coverage 판정은 자체 명령과 모순되고 coverage를 부풀릴 수 있다 — 근거: `.claude/skills/trust-validation/SKILL.md:27-49`. 실행 명령은 `--cov-fail-under=85`인데 80–85%를 WARNING으로 정의하며, `--cov=tests`까지 측정해 테스트 코드 자체가 제품 coverage를 높인다. 또한 TRUST를 Constitution Section V로 지칭하지만 workflow의 canonical 참조는 Section IV다(`ms.plan.md:56`).

    권장: 제품 패키지만 측정하고 85% 미만의 단일 verdict를 정하며 Constitution section 참조를 최신화하라.

28. [MEDIUM] SessionStart의 “next eligible”은 실제 eligibility를 계산하지 않는다 — 근거: `docs/templates/scripts/specter-session-status.sh:48-52`, `.claude/skills/session-handoff/SKILL.md:108-110`. 스크립트는 단순히 첫 `⬜ planned` 행을 선택하며 dependency나 predecessor 상태를 확인하지 않는다. handoff skill은 이를 이미 검증된 “next eligible Feature”로 신뢰해 재기재도 금지한다.

    권장: DAG와 완료 상태로 eligibility를 계산하거나 표시를 “first planned”로 낮춰라.

29. [MEDIUM] `/ms.expand`의 새 commitment 소유자 규칙이 상충한다 — 근거: `.claude/commands/ms.expand.md:2,9,114-117,154-155`. Step 1은 순수 clarification이면 새 row를 기존 Feature에 배정할 수 있다고 하지만, delta verification은 모든 amendment commitment가 “owning (new) Feature”를 가져야 한다고 요구한다.

    권장: clarification을 별도 모드로 분리하거나 기존 Feature 소유를 허용/금지 중 하나로 통일하라.

30. [MEDIUM][UNCERTAIN] `/ms.expand`의 Git Ref는 감사한 PRD 내용의 안정된 기준점이 아닐 수 있다 — 근거: `.claude/commands/ms.verify.md:211-214`, `.claude/commands/ms.expand.md:74-87,184-189`. verify는 작업 트리 내용을 감사하면서 `git rev-parse HEAD`를 기록하지만 clean/commit을 요구하지 않는다. 통상 PRD와 Feature Map이 아직 uncommitted라면 기록된 HEAD는 그 내용을 포함하지 않아, 다음 expand의 append-only diff가 최초 PRD 작성분까지 다시 보게 된다.

    권장: PRD blob SHA를 직접 기록하거나, audit 대상이 포함된 commit을 기준점으로 삼도록 명시하라.

31. [LOW] plan의 Constitution 링크가 생성 위치 기준으로 깨져 있다 — 근거: `.claude/commands/ms.plan.md:245`, `.claude/commands/ms.specify.md:335`. `specs/<id>/plan.md` 안의 `.specify/...` 상대 링크는 `specs/<id>/.specify/...`로 해석된다. spec 쪽은 올바르게 `../../`를 사용한다.

    권장: plan footer도 `../../.specify/memory/constitution.md`로 통일하라.

32. [LOW] up-docs가 현재 workflow가 더 이상 생산하지 않는 metadata를 소비한다 — 근거: `.claude/commands/ms.implement.md:300`, `.claude/commands/ms.up-docs.md:112,185`. 새 TAG는 status metadata를 쓰지 않는데 API doc template은 `{@CODE STATUS}`를 요구하고, 어떤 단계도 `spec.md`에 `status: completed`를 기록하지 않는데 README sync는 이를 완료 판정 기준으로 삼는다.

    권장: API status는 제거하거나 실제 상태원에서 계산하고, README 완료 판정은 Progress Ledger/merged release를 사용하라.

## 검토 커버리지

- `AGENTS.md` 전체와 24개 `ms.*` 명령 전부를 검토했다.
- 지정된 7개 workflow skill과 `trust-validation/examples.md`까지 읽었다.
- `transcript-mining`, `spike`, `codebase-snapshot`에서는 기존 리뷰에 없는 추가 workflow 모순을 찾지 못했다. transcript 개인정보 정책 부재는 기존 리뷰에 있어 제외했다.
- 두 settings 파일을 검토했다. 기존 리뷰의 `fin.md`·`finq.md`·`ms.amend.md`·context7 죽은 참조는 중복 제외했다.
- 템플릿 셸 스크립트 4개, `scripts/specter/` 4개, `tests/specter/` 5개를 모두 검토했다.
- `specter_sync_manifest.json`과 정상 3-way merge 정책 자체에서는 추가 이상이 없었다. target symlink 경계만 위에 보고했다.
- `ms.prd`, `ms.fix`, `spike`의 트랙 경계에서는 추가 모순을 찾지 못했다.
- Graphify와 Constitution은 이 저장소에 없었고, `docs/SYSTEM_MAP.md`는 HEAD 불일치로 stale여서 구조 증거로 사용하지 않았다.
- pytest와 `bash -n`은 실행 환경의 `bwrap: No permissions to create a new namespace` 오류로 시작되지 않았다. 따라서 테스트/문법 검사가 통과했다고 주장하지 않는다.
- 파일은 수정하지 않았다. 최종 `git status --short`는 시작 시와 동일하게 기존 `?? docs/review/`만 표시했다.

Codex session ID: 019f74d4-ea62-7812-a78f-a6c7302f409d
Resume in Codex: codex resume 019f74d4-ea62-7812-a78f-a6c7302f409d

---

## 검증 부록 (2026-07-18, 호스트 + 검증 에이전트 4개, 반증 우선 모드)

**최종 집계: CONFIRMED 30 / PARTIAL 2 / REFUTED 0 (32건 전수 검증)**

| 발견 | 판정 | 비고 |
| --- | --- | --- |
| #1, 6, 7, 11, 12, 23 | CONFIRMED | #1·#6·#12는 특정 경로(재개, 개별 명령 직접 호출, migration Feature)에서만 발현 — 발생 조건 폭은 원문보다 좁음 |
| #2, 3, 4, 17, 18, 19 | CONFIRMED | #17은 구현·테스트 양쪽에서 삭제-통과가 의도적으로 고정됨을 확인 |
| #16 | PARTIAL | phase-미결합(implement 증거로 review 통과)은 코드 추적 확정. "verdict 무관 허용"은 문서화된 의도적 설계라 결함 아님 |
| #5, 8, 13, 14, 15, 29, 30 | CONFIRMED | #14는 git 명령 실제 재현으로 실증. #15는 전역 검색 소비처 0건. #30은 UNCERTAIN 태그 유지 적정 |
| #9, 10 | CONFIRMED | 호스트가 원문 직접 대조 |
| #20, 22, 24, 25, 26, 27, 28, 31, 32 | CONFIRMED | #26 UNCERTAIN 태그 유지 적정 |
| #21 | PARTIAL | 핵심(uv sync/git restore allow, review·audit의 무확인 서버 기동·설치 지시)은 유효. settings.local.json 인용은 untracked 개인 로컬 파일이라 대표성 과장 |

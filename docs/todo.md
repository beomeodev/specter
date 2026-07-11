# TODO

<!-- Add working notes here. -->

## Skills: progressive disclosure 개편 (2026-07-11 완료, 커밋 대기)

공식 문서 2건(agent-skills/overview, agent-skills/best-practices) 전면 검토 후 21개
스킬 전수 감사·개편 완료. 배포 호환성 확인: `specter_sync_manifest.json`의
`.claude/skills/*`는 fnmatch라 중첩 `references/` 파일도 그대로 배포됨.

완료 내역:
- lang 스킬 2개 분리: ms-lang-python 808→210줄(references/fastapi.md·structlog.md),
  ms-lang-typescript 801→261줄(references/react-nextjs.md). "왜 X" 마케팅·PEP 튜토리얼·
  버전 매트릭스(accessed 날짜)·체인지로그 삭제 — 공식 "Claude is already smart" 원칙.
- ms-essentials-debug 596→304줄: Examples 1~5 → examples.md 분리.
- 죽은 레벨 3 연결: 미참조 examples.md 5개(constitution/living-docs/tag-manager/lang×2)에
  SKILL.md 포인터 배선.
- 100줄 초과 참조 파일 9개 전부에 Contents TOC 추가 (공식 부분-읽기 대비 지침).
- 시간 민감 정보 제거: 체인지로그 4곳, 버전 핀 완화("verified 2025-10, re-verify" 관례).
- ms-foundation-ears description의 `<static>` 앵글 브래킷 제거 (XML 태그 금지 규격).
- 사실 오류 수정: "md5가 Python 3.13에서 제거" 주장 삭제(허위), jest.mock→vi.mocked,
  reload() 예제를 reset() 패턴으로(CLAUDE.md zero-tolerance 정합).

후속 후보: 공식 문서의 "evaluation-driven development"(스킬별 평가 3개 작성) 미적용 —
reference 스킬엔 과하다고 판단, 규율 스킬은 testing-skills-with-subagents가 이미 커버.

## overnight-run 개편: 체인 모드 + 호출 기반 자율권 (2026-07-11 완료, 커밋·싱크 대기)

- SKILL.md 재작성(168줄): 최상단 불변조건 "자율권은 시각이 아니라 명시적 오버나이트
  호출에서만 나온다"(새벽 일반 세션=권한 0, 정오 오버나이트=권한 전부, 런 종료와 함께
  소멸). 체인 모드 신설(단일 worktree `.worktrees/overnight-chain`, 의존 순서 순차
  사이클, [DEPENDS: NNN] clarify 마킹, 드리프트 체크). 자율 사다리: 1 Conform(amend) /
  2 Conservative(PRD 보수 해석, WARN) / 3 PARK(신규 요구사항·PRD 수정·게이트 약화 필요
  시 — 하위 전부 정지). 결정은 원장에 {"cycle":"overnight","type":"decision"} 기록.
  /ms.fin은 양 모드 자동, /ms.merglease는 저녁 프렙 때 묻는 --merglease 옵트인(체인
  전용, 전부 green일 때만).
- specter-overnight.sh(docs/templates/scripts) 재작성: --chain/--no-fin/--merglease,
  체인 실패 시 하위 PARK 연쇄, review PASS/WARN 후 fin 자동 실행, 모드별 아침 보고서.
  스크래치 레포에서 dry-run 스모크 통과(merglease 가드, SKIP→PARK 연쇄).
- testing-skills-with-subagents 압박 테스트: 시나리오 3종(새벽 일반 세션의 자율권 도용 /
  체인 중 요구사항 즉석 발명 / 플래그 없는 merglease) × RED·GREEN 6에이전트 — 6/6 올바른
  선택, GREEN 전원 스킬 인용. REFACTOR 1건 반영(아침 merglease가 사용자 호출임을 명시).
- 다음 단계: 커밋 → /ms.sync 배포 (사용자 지시 대기).

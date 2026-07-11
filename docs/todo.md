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

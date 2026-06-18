# 워크플로우 TODO

- [ ] `docs/SYSTEM_MAP.md` 도입 검토: 전체 아키텍처, hot path, 상태 전이, 공통 모듈, 성능 위험 구간, 불변조건을 한 장으로 요약
- [ ] `docs/DEVELOPER_GUIDE.md` 도입 검토: README는 입구/링크 중심, 개발 가이드는 실행/테스트/릴리즈/장애 조사 절차 중심
- [ ] 에이전트 규칙 추가: 새 작업 시작 시 `SYSTEM_MAP.md`를 먼저 읽고, 필요하면 탐색 도구로 영향 범위를 점검
- [ ] 확인 결과: 로컬에는 코드베이스 탐색 전용 `SKILL.md`는 없고, 대신 `.claude/agents/codebase-explorer.md` agent가 있음
- [ ] 후속 검토: `Understand-Anything` / `Serena` / `code-review-graph`를 오케스트레이션하는 SPECTER용 skill 필요성 검토

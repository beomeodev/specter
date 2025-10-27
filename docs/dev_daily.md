# 🗓 2025-10-27 (Mon)

## 📌 Focus
- MCP CLI-Bridge 제거 및 Claude Code 내장 에이전트 시스템 완전 전환

## ✅ Done
- 한국어 지원 에이전트 및 명령어 구조 추가:
  - 한국어 에이전트 디렉토리 생성 (.claude/agents/korean/)
  - 한국어 명령어 디렉토리 생성 (.claude/commands/korean/)
  - constitution_kor.md 초안 작성 (.claude/commands/)
- MCP CLI-Bridge 의존성 완전 제거:
  - ms.specify.md: 첨부 문서 시나리오 브랜치 명명 규칙 추가
  - ms.plan.md: Gemini CLI → Claude Code Task tool 전환 (codebase-explorer, library-researcher, integration-designer)
  - ms.plan.md: Guidelines over Execution 패턴 적용 (Constitution 읽기 가이드라인 제공)
  - ms.plan.md: Tiered Agent Model 명시 (Opus 4: 전략적 아키텍처, Haiku 3.5: 정보 수집)
  - ms.implement.md: Gemini/Codex CLI → Claude Code 에이전트 전환 (library-researcher, doc-updater)
  - ms.implement.md: CHANGELOG → Living Documentation sync 패턴 변경
- Wrapper 역할 명확화:
  - ms.tasks.md: /speckit.tasks wrapper 역할 및 TAG 기능 강화 명시
  - ms.implement.md: Multi-Agent Orchestration 구조 문서화 (tdd-implementer, library-researcher, doc-updater)
- 비용 최적화 전략 문서화:
  - Opus: 장기적 영향이 큰 아키텍처 결정 (ms.plan의 implementation-planner)
  - Sonnet: TDD 추론 및 테스트 전략 (ms.implement의 tdd-implementer)
  - Haiku: 문서 조회, 패턴 탐색, Living Docs 동기화 (library-researcher, codebase-explorer, doc-updater)
- settings.local.json 업데이트 (Bash 권한 설정)

---

# 🗓 2025-10-26 (Sun)

## 📌 Focus
- SPECTER 워크플로우 전체 일관성 검증 및 AI 에이전트 관점 평가

## ✅ Done
- Constitution 템플릿 coverage 요구사항 통일 (80% → 85%)
- pyproject.toml Python 버전 요구사항 상향 (3.12+ → 3.13+)
- README 명령어 개수 수정 (11개 → 22개: 14 My-Spec + 8 Spec-Kit)
- 존재하지 않는 스킬 참조 제거 (ms-domain-backend, ms-domain-security)
- 에이전트 참조 명시적 추가:
  - ms.specify: spec-builder 에이전트 (Sonnet)
  - ms.plan: implementation-planner 에이전트 (Opus)
  - ms.implement: tdd-implementer 에이전트 (Sonnet)
  - fin: quality-gate 에이전트 (Haiku)
- ms.constitution 명령어 수정 (Section 14 → PROJECT_RULES HTML 주석 슬롯)
- ms.tasks, ms.implement TAG 유틸리티 경로 확장 (backend/src, frontend/src 추가)
- AST parser 가이드 조화 (Constitution 안전 사용 정책과 예제 일치)
- AI 에이전트 관점 종합 평가 수행:
  - 실행 가능성 분석 (40% 현재, 90% 잠재력)
  - Constitution 사용성 문제 식별 (1,352줄 → 분할 필요)
  - 병렬 에이전트 실행 불가능 문제 확인
  - 의사코드 vs 실제 도구 불일치 문제 분석
  - 개선 권장사항 3가지 제시 (빠른 수정/완전 구현/하이브리드)

---

# 🗓 2025-10-25 (Sat)

## 📌 Focus
- ms.review 워크플로우 개선 및 불필요한 설계 문서 정리

## ✅ Done
- ms.review.md에 도구 가용성 체크 로직 추가 (jq, rg, npx, radon, jscpd)
- ms.review.md 리포트 구조 개선 (Intent & Focus Charter 추가)
- ms.review.md 정리 단계 개선 (상세 임시 파일 목록 및 보존 정책 명시)
- .specify/design/review-optimization-plan.md 삭제 (구현 완료된 설계 문서)
- docs/todo.md 업데이트 (MoAI/Skills 통합 작업 계획)
- spec.md v2.0.0 전면 업데이트 (MoAI-ADK 통합 전략 완전 재작성)
  - Phase 1.0 추가: 기존 hooks 마이그레이션 전략 (constitution-injector.sh, tag-enforcer.ts)
  - Test-First 원칙 전면 적용 (모든 Phase에 RED → GREEN → REFACTOR)
  - Small units 준수: Phase 2 Skills 7개 → 3단계 분할
  - settings.json → settings.local.json 수정
  - 경로 매핑 규칙 추가 (.moai → .specify)
  - Python 환경 요구사항 명시 (Python ≥3.8, pytest)
  - Progressive Disclosure 구현 전략 추가
  - 에러 핸들링 정책 명시 (Fail-open)
  - 통합 일정 재조정 (10주 → 12주)
- .claude/settings.local.json 업데이트 (Bash 권한에 git config 추가)
- README.md 업데이트 (현재 상태 반영)
- docs/todo.md 업데이트 (My-Spec 초기화 워크플로우 진행 중)

---

# 🗓 2025-10-24 (Thu)

## 📌 Focus
- Claude Code Skills 및 MoAI-ADK 분석 문서 작성

## ✅ Done
- SKILLS.md 작성 (Claude Code Skills와 My-Spec workflow 통합 전략 분석)
- MoAI-ADK Living Docs 및 Sub-Agents 분석 문서 작성
- MoAI-ADK Skills 시스템 분석 문서 작성
- docs/references/moai-adk/ 및 docs/references/skills/ 디렉토리 생성 및 분석 자료 정리

---

# 🗓 2025-10-22 (Wed)

## 📌 Focus
- MCP CLI-Bridge 서버 보안 강화 및 Python 3.13 Free-Threading 빌드 완성

## ✅ Done
- MCP CLI-Bridge 서버 보안 취약점 분석 (Command Injection, 메모리 누수, Timeout 우회)
- Input validation 구현 (파일 경로 검증, 프롬프트 길이 제한 5MB)
- Task metadata LRU 캐시 구현 (50개 제한, 메모리 누수 방지)
- Process timeout 강제 종료 로직 추가 (30분 타임아웃, zombie process 방지)
- Python 3.13 Free-Threading Dockerfile 작성 (멀티스테이지 빌드, --disable-gil)
- Docker 이미지 리빌드 및 Free-Threading 검증 (GIL disabled, cp313t ABI 확인)
- 모든 의존성 Free-Threading 호환 테스트 (mcp, pyyaml, regex)
- MCP 서버 보안 기능 통합 테스트 완료
- GitHub 레포지토리 분석 및 한글 마크다운 문서 작성 (dots.ocr, MobileAgent, unsloth)
- NSFW 콘텐츠 생성 가능성 분석 (unsloth 파인튜닝 도구 기술적 검증)
- test_mcp_client.py 삭제 (불필요한 테스트 파일 정리)
- .claude/settings.local.json 병합 충돌 해결 (HEAD + 86389a3 변경사항 통합)
- Anthropic Skills 리포지토리 전면 분석 (구조, 기능, 카테고리 파악)
- My-Spec Commands와 Skills 통합 기회 분석 (6단계 로드맵 작성)

---

# 🗓 2025-10-21 (Tue)

## 📌 Focus
- Python 3.14 Free-Threading 기반 MCP 서버 비동기 실행 시스템 구축

## ✅ Done
- Claude CLI 로그인 지속성 완전 해결 (CLAUDE_CONFIG_DIR 환경변수 추가)
- Makefile sync 워크플로우 개선 (시작 시 pull만, 종료 시 commit/push)
- make finq 타겟 추가 (CI 생략 빠른 커밋)
- 6개 에이전트 실행 제약사항 명시 (Gemini: 1,2 / Claude: 3 / Codex: 4,5,6)
- ms.implement/plan/specify 워크플로우에 에이전트 실행 규칙 추가
- requirements.txt 제거 및 pyproject.toml 의존성 관리로 완전 전환
- 불필요한 파일 정리 (frontend/compare.md, main.py 삭제)
- Python 3.14 background task 패턴 적용 (asyncio.create_task + set + add_done_callback)
- MCP server에 background 실행 기능 추가 (gemini_cli, codex_cli)
- get_task_result 도구 구현 (wait=True/False 지원)
- ms.specify/plan/implement에 진정한 병렬 실행 패턴 추가
- PYTHON_GIL=0 환경변수 설정 (Free-Threading 활성화)
- MCP server 사용 가이드 및 테스트 예제 문서화
- Python 3.12 → 3.13 업그레이드 (Free-Threading 실제 지원)
- MCP server 접근성 검증 (Python client로 직접 테스트 성공)
- Gemini CLI 플래그 수정 (--telemetry 제거)
- test_mcp_client.py 작성 (background task 동작 검증)

---

# 🗓 2025-10-20 (Sun)

## 📌 Focus
- Task Tool → Sub-agent 마이그레이션 및 uv 기반 의존성 관리 전환

## ✅ Done
- 6개 재사용 가능 sub-agent 파일 생성 (.claude/agents/*.md)
- 4개 명령 파일 업데이트 (Task Tool → agent 호출로 변경)
- pip + requirements.txt → uv + pyproject.toml 마이그레이션 완료
- MCP 서버 의존성 문제 해결 (mcp 패키지 설치, cli-bridge 작동 확인)
- DevContainer 자동 의존성 설치 설정 (uv sync --all-groups)
- Part 1 완료 리포트 및 uv 마이그레이션 가이드 작성
- Claude MCP 연결 실패 해결 (.mcp.json에서 ${workspaceFolder} → 절대 경로 변경)
- Claude CLI 로그인 지속성 문제 해결 (docker-compose.yml에 ~/.npm 볼륨 마운트 추가)
- Git LFS pre-push hook 설정 확인 및 문제 진단

---

# 🗓 2025-10-17 (Fri)

## 📌 Focus
- Specter 템플릿 개선: 정량적 기준 기반 서브 에이전트 시스템 구축

## ✅ Done
- 6개 워크플로우에 정량적 측정 기반 복잡도 판단 로직 추가 (ms.specify, ms.plan, ms.analyze, ms.review, ms.constitution)
- 각 워크플로우에 명시적 결정 트리 및 서브 에이전트 병렬 실행 로직 구현 (일관성 95%+ 확보)
- TRUST Level 3에 순환 의존성 검증 추가 (madge/pydeps 통합)
- MCP 설정 경로 하드코딩 제거 (${workspaceFolder} 사용으로 템플릿 이식성 확보)
- server_streaming.py 삭제 및 TROUBLESHOOTING.md 템플릿 변수 적용

---

아래는 예시임. 작성시에는 아래 예시는 삭제하고 한글로 작성하세요.

# 🗓 2025-09-24 (수)

## 📌 오늘 주제

-   프로젝트: API 서버 리팩토링

## ✅ 오늘 한 일

-   엔드포인트 `/user` 리팩토링 완료
-   테스트 코드 일부 작성 (UserServiceTest)
-   DB 마이그레이션 스크립트 초안 작성

## 🐞 문제 & 해결

-   문제: JWT 인증 모듈에서 토큰 만료 오류 발생
-   시도: 라이브러리 버전 다운그레이드 → 실패
-   해결: 설정 파일에서 `exp` 기본값을 수정하여 정상 작동 확인

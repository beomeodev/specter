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

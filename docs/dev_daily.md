# 🗓 2025-10-21 (Tue)

## 📌 Focus
- 멀티 AI 에이전트 분담 구조 확립 및 워크플로우 개선

## ✅ Done
- Claude CLI 로그인 지속성 완전 해결 (CLAUDE_CONFIG_DIR 환경변수 추가)
- Makefile sync 워크플로우 개선 (시작 시 pull만, 종료 시 commit/push)
- make finq 타겟 추가 (CI 생략 빠른 커밋)
- 6개 에이전트 실행 제약사항 명시 (Gemini: 1,2 / Claude: 3 / Codex: 4,5,6)
- ms.implement/plan/specify 워크플로우에 에이전트 실행 규칙 추가
- requirements.txt 제거 및 pyproject.toml 의존성 관리로 완전 전환

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

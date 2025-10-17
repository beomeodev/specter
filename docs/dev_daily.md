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

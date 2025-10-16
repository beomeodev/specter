---
description: "Quick finish: update daily log → commit & push (NO CI checks)"
---

다음 작업을 순서대로 실행하세요:

## 1. 📝 일일 작업 로그 업데이트

현재 세션의 작업 내용을 분석하여 `docs/dev_daily.md`를 업데이트하세요:

### 분석 항목
- 변경된 파일 목록 확인 (git status 또는 대화 내용 기반)
- 주요 작업 내용 파악
- 추가/수정/삭제된 기능

### 업데이트 규칙
1. **오늘 날짜 섹션 확인**:
   - 오늘 날짜(YYYY-MM-DD)의 섹션이 있으면 → 해당 섹션의 Done에 추가
   - 없으면 → 파일 최상단에 새 섹션 추가

2. **작성 형식** (기존 양식 유지):
   ```markdown
   # 🗓 YYYY-MM-DD (Day)

   ## 📌 Focus
   - 주요 작업 테마 (1줄 요약)

   ## ✅ Done
   - 완료한 작업 내역 (간략하게, 3-5개 bullet points)
   ```

3. **작성 스타일**:
   - **간결하게**: 각 항목은 1줄로
   - **구체적으로**: "코드 수정" (X) → "tech_algo.py에 MACD 신호 추가" (O)
   - **기존 항목 유지**: 오늘 날짜 섹션에 이미 작성된 내용이 있으면 Done 아래에 추가 (덮어쓰기 X)

### 예시
```markdown
# 🗓 2025-10-01 (Tue)

## 📌 Focus
- AGENTS.md 템플릿 구조 개선 및 Makefile 통합

## ✅ Done
- templates 디렉토리 생성 및 AGENTS.md 3개 파일 작성 완료
- Markdown 포맷팅 적용 (헤더, 코드블록, 리스트)
- 루트 Makefile과 .devcontainer/Makefile 역할 분리
- /fin, /finq 슬래시 커맨드 추가
```

---

## 2. 💾 Git 커밋 및 푸시 (CI 체크 생략)

### Makefile finish 로직 참고 (CI 생략 버전)

```bash
# 1. git add
git add .

# 2. git commit (커밋 메시지 생성)
git commit -m "생성한_커밋_메시지"

# 3. git push
git push
```

### 커밋 메시지 생성 규칙
변경 사항을 분석하여 **의미 있는 커밋 메시지** 작성:

**형식**:
```
타입(범위): 제목

- 상세 내용 1
- 상세 내용 2
```

**타입**:
- `feat`: 새 기능
- `fix`: 버그 수정
- `refactor`: 리팩토링
- `docs`: 문서 수정
- `test`: 테스트 추가
- `chore`: 빌드, 설정 변경
- `wip`: 작업 중 (Work In Progress)

**예시**:
```
wip(strategy): MACD 신호 생성 로직 작업 중

- 기본 구조 구현
- 테스트 작성 필요
```

### 에러 처리
- **커밋할 내용이 없을 때**: `⚠️ Nothing to commit` 메시지 출력 후 계속 진행
- **Push 실패 시**: `❌ Push failed` 메시지 출력 (에러 내용 포함)

---

## 3. ✅ 완료 메시지

모든 단계 완료 후 출력:

```
✅ /finq 완료! (Quick mode - CI 생략)

📝 dev_daily.md 업데이트 완료
💾 커밋: [생성한 메시지]
🚀 Push 완료 (또는 실패 시 에러 메시지)

⚠️ CI 체크를 생략했습니다. 나중에 'make ci' 또는 '/fin'으로 검증하세요.
```

---

## ⚠️ 주의사항

1. **dev_daily.md 업데이트 시**:
   - 기존 내용을 절대 삭제하지 마세요
   - 오늘 날짜 섹션에 내용 추가만
   - Focus는 오늘 날짜 섹션이 처음 생성될 때만 작성

2. **CI 생략됨**:
   - 이 명령어는 빠른 커밋을 위해 CI 체크를 건너뜁니다
   - 코드 품질 검증은 나중에 `/fin` 또는 `make ci`로 수행하세요
   - 작업 중(WIP) 커밋에 적합합니다

3. **Git 동작**:
   - Makefile의 finish 타겟과 동일하게 처리 (CI 제외)
   - 커밋 실패 시에도 에러 메시지만 출력하고 계속 진행
   - Push 실패 시에도 에러 메시지만 출력하고 워크플로우 완료

4. **사용 시나리오**:
   - 작업 중간 백업 목적
   - 빠르게 원격에 올려야 할 때
   - 문서만 수정했을 때
   - 실험적인 코드 커밋

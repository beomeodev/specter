---
description: "Finish workflow: update daily log → CI checks → commit & push"
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

## 2. 🚀 CI 체크 실행

다음 명령어를 실행하여 코드 품질 검증:

```bash
make ci
```

**CI 포함 내용**:
- `black --check .` (코드 포맷)
- `isort --check-only .` (import 정렬)
- `ruff check .` (린트)
- `mypy src/` (타입 체크)
- `pytest -v --cov=src` (테스트)

**결과 처리**:
- ✅ **통과**: 다음 단계 진행
- ❌ **실패**: 구체적인 에러 메시지 출력 후 **중단** (커밋하지 않음)

---

## 3. 💾 Git 커밋 및 푸시

### Pre-commit Hook 처리 전략

**문제**: Pre-commit hook이나 IDE의 auto-format이 커밋 후 파일을 수정하여 git 상태가 dirty해짐

**해결 방법**: 커밋 전에 pre-commit을 먼저 실행하여 포맷팅 완료

```bash
# 1. Initial git add
git add .

# 2. Run pre-commit hooks to format files (if .pre-commit-config.yaml exists)
if [ -f .pre-commit-config.yaml ]; then
  pre-commit run --all-files || true
  # Hook may modify files, so add again
  git add .
fi

# 3. git commit (커밋 메시지 생성)
git commit -m "생성한_커밋_메시지"

# 4. git push
git push
```

**Why this works**:
- Pre-commit hooks (ruff-format, etc.) run and modify files
- Modified files are re-staged with second `git add .`
- Commit captures all formatting changes
- No dirty state after commit

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

**예시**:
```
feat(strategy): MACD 기반 기술적 분석 추가

- tech_algo.py에 MACD 신호 생성 로직 구현
- 백테스트 테스트 케이스 추가
```

### 에러 처리
- **커밋할 내용이 없을 때**: `⚠️ Nothing to commit` 메시지 출력 후 계속 진행
- **Push 실패 시**: `❌ Push failed` 메시지 출력 (에러 내용 포함)

---

## 4. ✅ 완료 메시지

모든 단계 완료 후 출력:

```
✅ /fin 완료!

📝 dev_daily.md 업데이트 완료
🚀 CI 체크 통과
💾 커밋: [생성한 메시지]
🚀 Push 완료 (또는 실패 시 에러 메시지)
```

---

## ⚠️ 주의사항

1. **dev_daily.md 업데이트 시**:
   - 기존 내용을 절대 삭제하지 마세요
   - 오늘 날짜 섹션에 내용 추가만
   - Focus는 오늘 날짜 섹션이 처음 생성될 때만 작성

2. **CI 실패 시**:
   - 즉시 중단
   - 어떤 체크가 실패했는지 명확히 출력
   - 커밋/푸시 하지 않음

3. **Git 동작**:
   - Makefile의 finish 타겟과 동일하게 처리
   - 커밋 실패 시에도 에러 메시지만 출력하고 계속 진행
   - Push 실패 시에도 에러 메시지만 출력하고 워크플로우 완료

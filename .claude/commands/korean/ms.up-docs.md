# /ms.up-docs - 범용 문서 동기화

Git 스테이징 영역 또는 특정 문서 유형을 기반으로 살아있는 문서를 코드 변경 사항과 동기화합니다.

## 개요

이 명령은 3가지 모드로 **문서 동기화**를 수행합니다.
1.  **스테이징된 변경 사항**(기본값): `git diff --cached`에 있는 파일에 대한 문서 동기화
2.  **특정 문서 유형**: API, 개발 일일 또는 README 문서만 동기화
3.  **전체 동기화**: 모든 문서 동기화(`--all` 플래그)

## 사용법

```bash
# 스테이징된 변경 사항에 대한 문서 동기화(기본값)
/ms.up-docs

# 특정 문서 유형 동기화
/ms.up-docs --docs=api       # API 문서만
/ms.up-docs --docs=dev       # 개발자 일일 로그만
/ms.up-docs --docs=readme    # README.md만

# 전체 동기화(모든 문서)
/ms.up-docs --all

# TAG 유효성 검사 건너뛰기
/ms.up-docs --skip-tags
```

## 인수

| 인수 | 설명 | 기본값 |
|---|---|---|
| `--docs=<유형>` | 특정 문서 유형 동기화(`api`, `dev`, `readme`) | 없음(스테이징된 변경 사항) |
| `--all` | 모든 문서 동기화(스테이징 무시) | False |
| `--skip-tags` | TAG 체인 유효성 검사 건너뛰기 | False |

## 실행 단계

### 0단계: 헌법 컨텍스트 로드

**프로젝트 문서 자동 로드**:
- `.specify/memory/constitution.md` (헌법 - 필수)
- `AGENTS.md` (AI 지침 - 있는 경우)

**참조 키 섹션**:
- 헌법 섹션 V (TRUST 5 원칙 - 추적 가능)
- TAG 시스템 요구 사항 및 추적성 표준

### 1단계: 동기화 범위 분석

**인수 구문 분석**:
```
--docs=<유형>이 제공된 경우:
  → 지정된 문서 유형만 동기화
--all 플래그가 제공된 경우:
  → 모든 문서 동기화
그렇지 않으면:
  → 스테이징된 변경 사항에 대해서만 문서 동기화(git diff --cached)
```

**Git 스테이징 영역 확인**(기본 모드):
```bash
# 스테이징된 파일 가져오기
git diff --cached --name-only

# 비어 있고 --all 플래그가 없는 경우:
⚠️ 스테이징된 변경 사항이 없습니다.

먼저 'git add <파일>'을 사용하거나 '/ms.up-docs --all'을 실행하여 모든 문서를 동기화하십시오.

종료: 코드 0
```

**영향을 받는 문서 확인**:
- 스테이징된 `.py` 파일 → API 문서
- 스테이징된 코드 파일 → TAG 체인 유효성 검사
- 구현 변경 → dev_daily.md 업데이트
- 주요 기능 → README.md 업데이트

### 2단계: 문서 동기화 실행

**각 문서 유형에 대해** 동기화 작업을 수행합니다.

#### API 문서 동기화(`--docs=api`)

**목표**: 함수/클래스 서명을 추출하고 API 문서를 생성합니다.

**프로세스**:
1. 코드 파일에서 TAG 블록 스캔:
   ```bash
   rg '@CODE:([A-Z]+-[0-9]+)' -n src/ --only-matching
   ```

2. 각 TAG에 대해 다음을 추출합니다.
   - 함수 서명
   - Docstring/JSDoc
   - 매개변수 및 반환 유형
   - 예제(있는 경우)

3. `docs/api/{TAG_ID}.md` 생성/업데이트:
   ```markdown
   # {TAG_ID}: {함수 이름}

   **상태**: {@CODE STATUS}
   **위치**: {file_path:line_number}
   **SPEC**: {spec_path}
   **TEST**: {test_path}

   ## 서명
   ```{language}
   {function_signature}
   ```

   ## 설명
   {docstring}

   ## 매개변수
   {parameters_list}

   ## 반환
   {return_type_and_description}

   ## 예제
   {code_examples}

   ## TAG 체인
   @SPEC:{TAG_ID} → @TEST:{TAG_ID} → @CODE:{TAG_ID} → @DOC:{TAG_ID}
   ```

**출력**: 업데이트된 API 문서 파일 목록

#### 개발 일일 로그 동기화(`--docs=dev`)

**목표**: 개발자 일일 로그에 git diff 요약 추가

**프로세스**:
1. 마지막 커밋 이후 git diff 가져오기:
   ```bash
   git diff HEAD~1 --stat
   git log -1 --format='%h %s'
   ```

2. 변경 사항 요약:
   - 수정된 파일(추가/변경/삭제된 줄)
   - 커밋 메시지
   - 영향을 받는 TAG ID

3. `docs/dev_daily.md`에 추가:
   ```markdown
   ## {YYYY-MM-DD HH:MM}

   **커밋**: {commit_hash} - {commit_message}

   **변경 사항**:
   - {file1}: +{additions} -{deletions}
   - {file2}: +{additions} -{deletions}

   **업데이트된 TAG**: {TAG_IDs}

   **요약**: {AI 생성 변경 사항 요약}

   ---
   ```

**출력**: 타임스탬프로 업데이트된 dev_daily.md

#### README 동기화(`--docs=readme`)

**목표**: 프로젝트 상태 및 기능으로 README.md 업데이트

**프로세스**:
1. 완료된 기능 스캔:
   - `status: completed`로 `specs/*/spec.md` 확인
   - 총 사양 대 완료된 사양 수 계산

2. README 섹션 업데이트:
   - **프로젝트 상태**: 완료된 기능, 테스트 범위, TAG 무결성
   - **기능**: spec.md 파일에서 구현된 기능 목록
   - **설치**: pyproject.toml/package.json에서 종속성 동기화
   - **사용법**: 테스트에서 예제 추출

3. 수동 콘텐츠 보존:
   - `<!-- AUTO-GENERATED:START -->` 및 `<!-- AUTO-GENERATED:END -->` 마커 사용
   - 마커 내의 콘텐츠만 업데이트

**출력**: 업데이트된 README.md

### 3단계: TAG 체인 유효성 검사(--skip-tags가 아닌 경우)

**TAG 시스템 스캔**:
```bash
# 모든 TAG 찾기
rg '@(SPEC|TEST|CODE|DOC):([A-Z]+-[0-9]+)' -n

# 체인 확인:
# - @SPEC가 있으면 → @TEST가 있어야 함 → @CODE가 있어야 함
# - 고아 TAG(체인 없음)
# - 끊어진 참조
```

**TAG 무결성 계산**:
```
무결성 = (완전한 체인 / 총 TAG 수) * 100%

완전한 체인: @SPEC:ID → @TEST:ID → @CODE:ID → @DOC:ID (모두 존재)
```

**출력**: TAG 무결성 점수(0-100%)

### 4단계: 동기화 보고서 생성

**형식**:
```json
{
  "sync_mode": "staged|api|dev|readme|all",
  "files_updated": [
    "docs/api/AUTH-001.md",
    "docs/dev_daily.md"
  ],
  "tag_integrity": {
    "total_tags": 25,
    "complete_chains": 23,
    "orphan_tags": 2,
    "integrity_score": 92.0
  },
  "duration_seconds": 8.5,
  "warnings": [
    "고아 TAG: @CODE:PAY-003 (@SPEC를 찾을 수 없음)"
  ]
}
```

**표시**:
```
✅ 문서 동기화 완료

📦 업데이트된 파일:
- docs/api/AUTH-001.md (생성됨)
- docs/api/USER-002.md (업데이트됨)
- docs/dev_daily.md (추가됨)

📋 TAG 무결성: 92.0% (23/25 완전한 체인)
⚠️  경고:
- 고아 TAG: @CODE:PAY-003 (@SPEC를 찾을 수 없음)

⏱️ 기간: 8.5초

🎯 다음 단계:
1. docs/ 디렉토리에서 업데이트된 문서 검토
2. 필요한 경우 고아 TAG 수정
3. git add docs/ && git commit -m "docs: 살아있는 문서 동기화"로 문서 커밋
```

## 오류 처리

### 오류 1: Git 리포지토리 없음

**증상**: git 리포지토리가 아님

**메시지**:
```
❌ 오류: git 리포지토리가 아님

/ms.up-docs는 변경 사항을 확인하기 위해 git 리포지토리가 필요합니다.

먼저 'git init'을 실행하십시오.
```

**종료**: 코드 1

### 오류 2: 동기화할 변경 사항 없음

**증상**: 스테이징된 변경 사항이 없고 --all 플래그가 없음

**메시지**:
```
⚠️ 스테이징된 변경 사항이 없습니다.

먼저 'git add <파일>'을 사용하거나 '/ms.up-docs --all'을 실행하여 모든 문서를 동기화하십시오.
```

**종료**: 코드 0 (성공 - 할 일 없음)

### 오류 3: 잘못된 문서 유형

**증상**: `--docs=invalid`

**메시지**:
```
❌ 오류: 잘못된 문서 유형 'invalid'

유효한 옵션: api, dev, readme

예: /ms.up-docs --docs=api
```

**종료**: 코드 1

### 오류 4: TAG 무결성 낮음

**증상**: TAG 무결성 < 80%

**메시지**:
```
⚠️ 경고: TAG 무결성이 낮습니다(65%).

23개 중 15개의 TAG에 불완전한 체인이 있습니다.

권장 사항: '/ms.analyze'를 실행하여 끊어진 TAG 참조를 식별하고 수정하십시오.

계속하시겠습니까? (동기화 완료되었지만 TAG 문제가 감지됨)
```

**종료**: 코드 0 (경고, 오류 아님)

## My-Spec 워크플로와의 통합

**호출자**:
- `/fin` 명령(커밋 전)
- `/finq` 명령(빠른 완료)
- 문서 동기화가 필요할 때 수동 호출

**워크플로 위치**:
```
/ms.specify → /ms.plan → /ms.implement → [/ms.up-docs] → /fin
                                              ↑
                                      (선택 사항이지만 권장)
```

**모범 사례**:
1. 기능 구현 후 `/ms.up-docs` 실행
2. `/fin` 실행 전 문서 검토
3. API 전용 업데이트에 `--docs=api` 사용
4. 일일 로그 업데이트에 `--docs=dev` 사용
5. 릴리스 전 포괄적인 동기화에 `--all` 사용

## 문서 구조

**My-Spec 문서 트리**:
```
docs/
├── api/               # API 문서(@CODE TAG에서 자동 생성)
│   ├── AUTH-001.md
│   ├── USER-002.md
│   └── ...
├── dev_daily.md       # 개발자 일일 로그(추가 전용)
├── architecture.md    # 시스템 아키텍처(수동 + 자동 섹션)
└── guides/            # 사용자 가이드(대부분 수동)

README.md              # 프로젝트 개요(자동 섹션 + 수동)
CHANGELOG.md           # 변경 내역(수동, /fin으로 업데이트)
```

**자동 생성된 마커**:
```markdown
<!-- AUTO-GENERATED:START - 수동으로 편집하지 마십시오 -->
{자동 생성된 콘텐츠}
<!-- AUTO-GENERATED:END -->
```

## 헌법 준수

**TRUST 5 원칙**:
- **추적 가능**: TAG 체인 유효성 검사로 추적성 보장
- **가독성**: 생성된 문서는 마크다운 표준을 따름
- **통일성**: 모든 API에서 일관된 문서 구조
- **보안성**: 자동 생성된 문서에 민감한 데이터 없음
- **테스트 우선**: @TEST TAG를 통해 테스트를 문서에 연결

**파일 크기**:
- 각 API 문서는 500줄 이하(더 크면 분할)
- 생성된 콘텐츠는 My-Spec 서식 표준을 따름

## 성능

**목표**: 10분 이내에 전체 동기화 완료

**최적화 전략**:
1. **스테이징된 변경 모드**: 영향을 받는 문서만 동기화(빠름)
2. **병렬 처리**: API 문서를 동시에 동기화(TAG가 10개 이상인 경우)
3. **증분 업데이트**: 기존 파일 수정, 재생성 안 함
4. **캐싱**: 명령 기간 동안 TAG 스캔 결과 캐시

**성능 메트릭**:
- 스테이징된 변경: 30초 미만(일반적)
- API 문서(TAG 10개): 약 2분
- 전체 동기화(`--all`): 10분 미만(TAG 100개)

## 참고

- **에이전트 위임 없음**: /ms.up-docs는 직접 명령입니다(3.1단계에 doc-updater 에이전트 없음).
- **3.2단계에서 에이전트 추가 예정**: 복잡한 동기화 논리를 위한 doc-updater 에이전트
- **Fail-open**: 일부 문서 동기화에 실패하더라도 계속 진행(경고 기록)
- **Git 인식**: .gitignore를 존중하고 무시된 파일을 동기화하지 않음

## 구현 세부 정보

**도구**: Read, Write, Edit, Bash, Grep, Glob

**주요 작업**:
1. Git 상태/diff 분석
2. ripgrep을 통한 TAG 추출
3. 마크다운 생성
4. 파일 쓰기/업데이트
5. TAG 체인 유효성 검사

## 참조

- My-Spec TRUST 5 원칙: `.specify/memory/constitution.md` 섹션 V
- TAG 시스템: `ms-workflow-tag-manager` 스킬
- 살아있는 문서: `ms-workflow-living-docs` 스킬
- 문서 표준: `AGENTS.md` 섹션 2 (문서 업데이트)

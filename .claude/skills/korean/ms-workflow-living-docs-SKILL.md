---
name: ms-workflow-living-docs
description: TAG 스캔 코드에서 살아있는 문서를 생성하고 동기화합니다. /ms.up-docs로 문서를 업데이트하거나 API 문서를 동기화할 때 사용합니다.
allowed-tools:
  - Read
  - Bash
  - Grep
  - Write
  - Edit
version: 1.0.0
created: 2025-10-26
---

# 워크플로우: 살아있는 문서 관리자

## 스킬 메타데이터
| 필드 | 값 |
| --- | --- |
| 버전 | 1.0.0 |
| 생성일 | 2025-10-26 |
| 허용된 도구 | Read, Bash, Grep, Write, Edit |
| 자동 로드 | `/ms.up-docs`, `/fin`, `/finq`, 문서 동기화` |
| 트리거 큐 | 문서 동기화, API 문서, TAG 스캐닝, 살아있는 문서 |

## 기능

My-Spec 워크플로우를 위한 살아있는 문서 수명 주기를 관리합니다:
- 코드에서 TAG 블록(@CODE, @TEST, @DOC 참조)을 스캔합니다.
- TAG 주석이 달린 코드에서 API 문서를 생성합니다.
- Git diff 요약으로 개발 일일 로그를 업데이트합니다.
- 프로젝트 상태와 README를 동기화합니다.
- TAG 체인 완전성(SPEC → TEST → CODE → DOC)을 검증합니다.

## 사용 시기

- 기능 구현 후 (`/ms.implement` 후 `/ms.up-docs`)
- 코드 커밋 전 (`/fin` 또는 `/finq` 명령)
- 코드 변경 사항과 API 문서 동기화
- 현재 상태로 프로젝트 README 업데이트
- TAG 체인 무결성 검증
- 살아있는 문서 보고서 생성

## 작동 방식

### TAG 스캐닝 알고리즘

**코드에서 TAG 블록 스캔**:
```bash
# 모든 TAG 참조 찾기
rg '@(SPEC|TEST|CODE|DOC):([A-Z]+-[0-9]+)' -n -or '$1:$2' specs/ tests/ src/ docs/

# 예제 출력:
# specs/001-auth-spec/spec.md:15:SPEC:AUTH-001
# tests/unit/test_auth.py:2:TEST:AUTH-001
# src/auth/service.py:2:CODE:AUTH-001
# docs/api/AUTH-001.md:1:DOC:AUTH-001
```

**TAG 메타데이터 추출**:
```python
import subprocess
import re

def scan_tags(cwd: str) -> list[dict]:
    """
    코드베이스에서 TAG 블록을 스캔하고 메타데이터를 추출합니다.

    Returns:
        TAG 메타데이터 사전 목록
    """
    result = subprocess.run(
        ["rg", "@(SPEC|TEST|CODE|DOC):", "-n", "-A", "5"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )

    tags = []
    for line in result.stdout.split("\n"):
        # TAG ID 구문 분석
        match = re.search(r"@(SPEC|TEST|CODE|DOC):([A-Z]+-[0-9]+)", line)
        if match:
            tag_type, tag_id = match.groups()
            tags.append({
                "type": tag_type,
                "id": tag_id,
                "file": line.split(":")[0],
                "line": int(line.split(":")[1]),
            })

    return tags
```

### API 문서 생성

**TAG 주석이 달린 코드에서 API 문서 생성**:

```python
def generate_api_doc(tag_id: str, code_file: str, cwd: str) -> str:
    """
    TAG ID에 대한 API 문서를 생성합니다.

    Args:
        tag_id: TAG ID (예: AUTH-001)
        code_file: 코드 파일 경로
        cwd: 작업 디렉토리

    Returns:
        마크다운 문서 내용
    """
    # 코드 파일 읽기
    with open(f"{cwd}/{code_file}", "r") as f:
        content = f.read()

    # 함수 서명 및 독스트링 추출
    functions = extract_functions(content)

    # 마크다운 생성
    doc = f"# @DOC:{tag_id} - API 문서\n\n"
    doc += f"@CODE: {code_file}\n\n"

    for func in functions:
        doc += f"## {func['name']}\n\n"
        doc += f"**서명**: `{func['signature']}`\n\n"
        if func['docstring']:
            doc += f"{func['docstring']}\n\n"

    return doc
```

**예제 출력** (docs/api/AUTH-001.md):
```markdown
# @DOC:AUTH-001 - API 문서

@CODE: src/auth/service.py
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py

## authenticate_user

**서명**: `def authenticate_user(email: str, password: str) -> AuthResult`

이메일과 비밀번호로 사용자를 인증합니다.

**인수**:
- email (str): 사용자 이메일 주소
- password (str): 사용자 비밀번호

**반환값**:
- AuthResult: 성공 상태 및 선택적 토큰이 포함된 인증 결과

**발생오류**:
- ValueError: 이메일 또는 비밀번호가 비어 있는 경우
```

### 개발 일일 로그 동기화

**Git diff 요약을 개발 일일 로그에 추가**:

```python
from datetime import date

def sync_dev_daily(git_diff: str, cwd: str) -> str:
    """
    Git diff 요약으로 개발 일일 로그를 업데이트합니다.

    Args:
        git_diff: Git diff 출력
        cwd: 작업 디렉토리

    Returns:
        업데이트된 개발 일일 로그 내용
    """
    today = date.today().strftime("%Y-%m-%d")
    summary = summarize_git_diff(git_diff)

    log_entry = f"""
## {today}

### 변경 사항
{summary}

### TAG 체인 업데이트
{scan_tag_chains(cwd)}

---
"""

    # dev_daily.md에 추가
    with open(f"{cwd}/docs/dev_daily.md", "a") as f:
        f.write(log_entry)

    return log_entry
```

**예제 출력** (docs/dev_daily.md):
```markdown
## 2025-10-26

### 변경 사항
- AUTH-001 구현: 사용자 인증 서비스
- 인증 흐름에 대한 테스트 추가
- API 문서 업데이트

### TAG 체인 업데이트
- ✅ 완료: AUTH-001 (@SPEC → @TEST → @CODE → @DOC)
- ⚠️ 미완료: AUTH-002 (@SPEC → @TEST, @CODE 누락)

---
```

### README 동기화

**현재 프로젝트 상태로 README 업데이트**:

```python
def sync_readme(major_changes: bool, cwd: str) -> str:
    """
    주요 변경 사항이 감지되면 README를 업데이트합니다.

    Args:
        major_changes: 주요 변경 사항 발생 여부
        cwd: 작업 디렉토리

    Returns:
        업데이트된 README 내용
    """
    if not major_changes:
        return None  # 사소한 변경은 업데이트 건너뛰기

    # 현재 README 읽기
    with open(f"{cwd}/README.md", "r") as f:
        readme = f.read()

    # 프로젝트 상태 섹션 업데이트
    status = get_project_status(cwd)
    updated_readme = update_section(readme, "Project Status", status)

    # 필요한 경우 설치/사용법 업데이트
    # ...

    return updated_readme
```

### TAG 체인 유효성 검사

**완전한 TAG 체인 유효성 검사**:

```python
def validate_tag_chains(cwd: str) -> dict:
    """
    TAG 체인 완전성(SPEC → TEST → CODE → DOC)을 검증합니다.

    Returns:
        무결성 점수가 포함된 유효성 검사 보고서
    """
    tags = scan_tags(cwd)

    # TAG ID로 그룹화
    tag_groups = {}
    for tag in tags:
        tag_id = tag["id"]
        if tag_id not in tag_groups:
            tag_groups[tag_id] = {"SPEC": False, "TEST": False, "CODE": False, "DOC": False}
        tag_groups[tag_id][tag["type"]] = True

    # 완전성 계산
    complete_chains = 0
    orphaned_tags = []

    for tag_id, chain in tag_groups.items():
        # 완전한 체인은 SPEC + TEST + CODE가 필요합니다 (DOC는 선택 사항).
        if chain["SPEC"] and chain["TEST"] and chain["CODE"]:
            complete_chains += 1
        else:
            orphaned_tags.append({
                "id": tag_id,
                "chain": chain,
                "missing": [k for k, v in chain.items() if not v and k != "DOC"]
            })

    total_chains = len(tag_groups)
    integrity_score = (complete_chains / total_chains * 100) if total_chains > 0 else 0

    return {
        "total_chains": total_chains,
        "complete_chains": complete_chains,
        "integrity_score": integrity_score,
        "orphaned_tags": orphaned_tags,
    }
```

**예제 보고서**:
```json
{
  "total_chains": 15,
  "complete_chains": 13,
  "integrity_score": 86.7,
  "orphaned_tags": [
    {
      "id": "AUTH-002",
      "chain": {"SPEC": true, "TEST": true, "CODE": false, "DOC": false},
      "missing": ["CODE"]
    },
    {
      "id": "HOOKS-005",
      "chain": {"SPEC": true, "TEST": false, "CODE": true, "DOC": false},
      "missing": ["TEST"]
    }
  ]
}
```

## 입력
- 코드베이스 디렉토리 (specs/, tests/, src/, docs/)
- Git diff 출력 (개발 일일 동기화용)
- 문서 유형 플래그 (api, dev, readme, all)
- 스테이징된 변경 사항 플래그 (스테이징된 파일만 동기화 또는 모든 파일)

## 출력
- 생성된 API 문서 (docs/api/*.md)
- 업데이트된 개발 일일 로그 (docs/dev_daily.md)
- 업데이트된 README (주요 변경 사항이 있는 경우)
- TAG 체인 유효성 검사 보고서 (JSON)
- 동기화 요약 (업데이트된 파일, TAG 무결성 점수, 기간)

## 예제 사용 시나리오

### 시나리오 1: 구현 후 API 문서 동기화

```bash
# AUTH-001 구현 후
/ms.up-docs --docs=api

# 시스템 실행:
# 1. @CODE:AUTH-001에 대한 코드 스캔
# 2. 함수 서명 및 독스트링 추출
# 3. docs/api/AUTH-001.md 생성
# 4. TAG 체인 유효성 검사 (SPEC → TEST → CODE → DOC)
# 5. 동기화 상태 보고
```

**출력**:
```json
{
  "files_updated": ["docs/api/AUTH-001.md"],
  "tag_integrity": 100.0,
  "duration_seconds": 3.2
}
```

### 시나리오 2: 커밋 전 개발 일일 업데이트

```bash
# 변경 사항 커밋 전
/ms.up-docs --docs=dev

# 시스템 실행:
# 1. git diff HEAD~1 --name-only 실행
# 2. 변경 사항 요약 (AI 생성 요약)
# 3. TAG 체인 업데이트 스캔
# 4. docs/dev_daily.md에 추가
# 5. 동기화 상태 보고
```

**출력** (docs/dev_daily.md에 추가됨):
```markdown
## 2025-10-26

### 변경 사항
- SessionStart 훅 구현 (HOOKS-001)
- 프로젝트 상태 표시 기능 추가
- 테스트: 18/18 통과

### TAG 체인 업데이트
- ✅ 완료: HOOKS-001 (@SPEC → @TEST → @CODE)

---
```

### 시나리오 3: 모든 문서 동기화 (전체 업데이트)

```bash
# 전체 문서 동기화
/ms.up-docs --all

# 시스템 실행:
# 1. API 문서 동기화 (모든 @CODE 태그 스캔)
# 2. 개발 일일 업데이트 (최신 변경 사항 추가)
# 3. README 업데이트 (주요 변경 사항이 감지된 경우)
# 4. 모든 TAG 체인 유효성 검사
# 5. 포괄적인 동기화 보고서 생성
```

**출력**:
```json
{
  "files_updated": [
    "docs/api/AUTH-001.md",
    "docs/api/HOOKS-001.md",
    "docs/dev_daily.md",
    "README.md"
  ],
  "tag_integrity": 93.3,
  "duration_seconds": 12.5
}
```

### 시나리오 4: 스테이징된 변경 사항만 (기본값)

```bash
# 스테이징된 변경 사항만 동기화 (기본 동작)
git add src/auth/service.py tests/unit/test_auth.py
/ms.up-docs

# 시스템 실행:
# 1. git diff --cached 실행 (스테이징된 파일만)
# 2. 스테이징된 파일에서만 TAG 스캔
# 3. 영향을 받는 TAG에 대한 문서 업데이트
# 4. 동기화 상태 보고
```

**출력**:
```json
{
  "files_updated": ["docs/api/AUTH-001.md"],
  "staged_files": ["src/auth/service.py", "tests/unit/test_auth.py"],
  "tag_integrity": 100.0,
  "duration_seconds": 2.1
}
```

## /fin 및 /finq와의 통합

**커밋 전 자동 문서 동기화**:

### /fin 워크플로우 (CI 포함)
```bash
/fin

# 실행 순서:
# 1. /ms.up-docs --docs=dev  ← 개발 일일 자동 동기화
# 2. make ci                  ← 테스트, 린터 실행
# 3. git add .                ← 모든 변경 사항 스테이징
# 4. git commit -m "..."      ← TAG 참조로 커밋
# 5. git push                 ← 원격으로 푸시
```

### /finq 워크플로우 (CI 건너뛰기)
```bash
/finq

# 실행 순서:
# 1. /ms.up-docs --docs=dev  ← 개발 일일 자동 동기화
# 2. git add .                ← 모든 변경 사항 스테이징
# 3. git commit -m "..."      ← TAG 참조로 커밋
# 4. git push                 ← 원격으로 푸시
```

## 성능 최적화

**목표**: 대규모 코드베이스에서도 10분 이내에 문서 동기화 완료

**전략**:
1. **병렬 작업**: TAG를 스캔하고 문서를 동시에 생성합니다.
2. **증분 업데이트**: 변경된 TAG에 대한 문서만 업데이트합니다.
3. **캐싱**: TAG 스캔 결과를 캐시합니다(코드 변경 시 무효화).
4. **일괄 처리**: 단일 ripgrep 스캔에서 여러 TAG ID를 처리합니다.

**구현**:
```python
from concurrent.futures import ThreadPoolExecutor

def sync_docs_parallel(tag_ids: list[str], cwd: str) -> list[str]:
    """API 문서를 병렬로 생성합니다."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(generate_api_doc, tag_id, cwd)
            for tag_id in tag_ids
        ]
        return [f.result() for f in futures]
```

## 오류 처리 (Fail-open)

**원칙**: 문서 동기화 실패가 커밋을 차단해서는 안 됩니다.

**구현**:
```python
def sync_with_failopen(cwd: str) -> dict:
    """fail-open 오류 처리로 문서를 동기화합니다."""
    try:
        result = sync_all_docs(cwd)
        return result
    except Exception as e:
        logger.error(f"문서 동기화 실패: {e}")
        # 부분 결과를 반환하고 커밋을 계속 허용합니다.
        return {
            "status": "PARTIAL",
            "error": str(e),
            "files_updated": [],
        }
```

## 관련 스킬
- `ms-workflow-tag-manager`: TAG 블록 생성 및 템플릿
- `ms-foundation-trust`: TAG 체인 유효성 검사 (추적 가능 원칙)
- `moai-alfred-tag-scanning`: TAG 스캐닝 및 인벤토리
- `moai-foundation-specs`: SPEC 메타데이터 및 유효성 검사

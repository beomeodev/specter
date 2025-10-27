# 살아있는 문서 관리자 스킬 - 예제

## 예제 1: API 문서를 위한 TAG 스캐닝

**시나리오**: @CODE 태그에 대한 코드를 스캔하고 API 문서를 생성합니다.

```python
# 입력: 코드베이스 디렉토리
cwd = "/workspace/my-spec-project"

# TAG 스캔 실행
import subprocess

result = subprocess.run(
    ["rg", "@CODE:([A-Z]+-[0-9]+)", "-or", "$1", "src/"],
    capture_output=True,
    text=True,
    cwd=cwd,
)

# 출력: TAG ID 목록
tag_ids = result.stdout.strip().split("\n")
print(tag_ids)
# ['AUTH-001', 'AUTH-002', 'HOOKS-001', 'SKILLS-001']

# 각 TAG에 대해 API 문서 생성
for tag_id in tag_ids:
    # 코드 파일 찾기
    code_file_result = subprocess.run(
        ["rg", f"@CODE:{tag_id}", "-l", "src/"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    code_file = code_file_result.stdout.strip()

    # API 문서 생성
    api_doc = generate_api_doc(tag_id, code_file, cwd)

    # docs/api/에 쓰기
    with open(f"{cwd}/docs/api/{tag_id}.md", "w") as f:
        f.write(api_doc)

    print(f"✅ docs/api/{tag_id}.md 생성됨")
```

**생성된 docs/api/AUTH-001.md**:
```markdown
# @DOC:AUTH-001 - 사용자 인증 API

@CODE: src/auth/service.py
@SPEC: specs/001-auth-spec/spec.md
@TEST: tests/unit/test_auth_service.py
@CHAIN: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001 → @DOC:AUTH-001

## 개요

JWT 토큰 생성을 통한 사용자 인증 서비스입니다.

## 함수

### authenticate_user

**서명**: `def authenticate_user(email: str, password: str) -> AuthResult`

이메일과 비밀번호로 사용자를 인증합니다.

**매개변수**:
- `email` (str): 사용자 이메일 주소
- `password` (str): 사용자 비밀번호

**반환값**:
- `AuthResult`: 성공 상태 및 선택적 JWT 토큰이 포함된 인증 결과

**발생오류**:
- `ValueError`: 이메일 또는 비밀번호가 비어 있는 경우

**예시**:
```python
result = authenticate_user("user@example.com", "password123")
if result.success:
    print(f"토큰: {result.token}")
else:
    print(f"오류: {result.error}")
```

---

*2025-10-26에 /ms.up-docs로 생성됨*
```

---

## 예제 2: 개발 일일 로그 동기화

**시나리오**: Git diff 요약으로 개발 일일 로그 업데이트

```python
from datetime import date

# Git diff 가져오기
import subprocess

git_diff = subprocess.run(
    ["git", "diff", "HEAD~1", "--name-only"],
    capture_output=True,
    text=True,
).stdout

# 변경된 파일:
# src/auth/service.py
# tests/unit/test_auth_service.py
# docs/api/AUTH-001.md

# 변경 사항 요약 (간소화됨 - 실제로는 AI 요약 사용)
summary = """
- AUTH-001 구현: 사용자 인증 서비스
- JWT 토큰 생성 추가
- 테스트: 18/18 통과
- 커버리지: 87%
"""

# TAG 체인 업데이트 스캔
tag_scan_result = subprocess.run(
    ["rg", "@(SPEC|TEST|CODE):AUTH-001", "-c", "specs/", "tests/", "src/"],
    capture_output=True,
    text=True,
)

tag_status = "✅ 완료: AUTH-001 (@SPEC → @TEST → @CODE)"

# dev_daily.md에 추가
today = date.today().strftime("%Y-%m-%d")
log_entry = f""
## {today}

### 변경 사항
{summary}

### TAG 체인 업데이트
{tag_status}

### 메트릭
- 변경된 파일: 3
- 통과한 테스트: 18/18
- 커버리지: 87%

---
"""

with open("docs/dev_daily.md", "a") as f:
    f.write(log_entry)

print("✅ docs/dev_daily.md 업데이트됨")
```

**업데이트된 docs/dev_daily.md**:
```markdown
# 개발 일일 로그

## 2025-10-26

### 변경 사항

- AUTH-001 구현: 사용자 인증 서비스
- JWT 토큰 생성 추가
- 테스트: 18/18 통과
- 커버리지: 87%

### TAG 체인 업데이트
✅ 완료: AUTH-001 (@SPEC → @TEST → @CODE)

### 메트릭
- 변경된 파일: 3
- 통과한 테스트: 18/18
- 커버리지: 87%

---

## 2025-10-25

### 변경 사항

- 초기 프로젝트 설정
- 헌법 생성
- 테스트 인프라 설정

---
```

---

## 예제 3: TAG 체인 유효성 검사 보고서

**시나리오**: 프로젝트 전체의 TAG 체인 완전성 검증

```python
import subprocess
import re
from collections import defaultdict

def validate_tag_chains(cwd: str) -> dict:
    """TAG 체인 완전성을 검증합니다."""

    # 모든 TAG 스캔
    result = subprocess.run(
        ["rg", "@(SPEC|TEST|CODE|DOC):([A-Z]+-[0-9]+)", "-or", "$1:$2"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )

    # TAG ID로 그룹화
    tag_chains = defaultdict(lambda: {"SPEC": 0, "TEST": 0, "CODE": 0, "DOC": 0})

    for line in result.stdout.strip().split("\n"):
        if ":" in line:
            tag_type, tag_id = line.split(":")
            tag_chains[tag_id][tag_type] += 1

    # 완전성 검증
    complete_chains = []
    broken_chains = []

    for tag_id, chain in tag_chains.items():
        # 완전한 체인: SPEC + TEST + CODE (DOC 선택 사항)
        if chain["SPEC"] > 0 and chain["TEST"] > 0 and chain["CODE"] > 0:
            complete_chains.append(tag_id)
        else:
            missing = [k for k, v in chain.items() if v == 0 and k != "DOC"]
            broken_chains.append({
                "id": tag_id,
                "chain": dict(chain),
                "missing": missing,
            })

    total = len(tag_chains)
    integrity_score = (len(complete_chains) / total * 100) if total > 0 else 0

    return {
        "total_chains": total,
        "complete_chains": len(complete_chains),
        "broken_chains": len(broken_chains),
        "integrity_score": round(integrity_score, 2),
        "complete": complete_chains,
        "broken": broken_chains,
    }

# 유효성 검사 실행
report = validate_tag_chains("/workspace/specter")
print(f"TAG 체인 무결성: {report['integrity_score']}&")
print(f"완전한 체인: {report['complete_chains']}/{report['total_chains']}")

for broken in report['broken']:
    print(f"❌ {broken['id']}: 누락 {broken['missing']}")
```

**출력**:
```
TAG 체인 무결성: 86.67%
완전한 체인: 13/15

❌ AUTH-002: 누락 ['CODE']
❌ HOOKS-005: 누락 ['TEST']
```

**생성된 보고서** (JSON):
```json
{
  "total_chains": 15,
  "complete_chains": 13,
  "broken_chains": 2,
  "integrity_score": 86.67,
  "complete": [
    "AUTH-001",
    "HOOKS-001",
    "HOOKS-002",
    "HOOKS-003",
    "SKILLS-001",
    "SKILLS-002",
    "SKILLS-003",
    "LDOCS-001",
    "LDOCS-002",
    "AGENTS-001",
    "AGENTS-002",
    "AGENTS-003",
    "INFRA-001"
  ],
  "broken": [
    {
      "id": "AUTH-002",
      "chain": {"SPEC": 1, "TEST": 1, "CODE": 0, "DOC": 0},
      "missing": ["CODE"]
    },
    {
      "id": "HOOKS-005",
      "chain": {"SPEC": 1, "TEST": 0, "CODE": 1, "DOC": 0},
      "missing": ["TEST"]
    }
  ]
}
```

---

## 예제 4: 프로젝트 상태와 README 동기화

**시나리오**: 현재 구현 상태로 README 업데이트

```python
def sync_readme(cwd: str, major_changes: bool = True) -> str:
    """프로젝트 상태로 README를 업데이트합니다."""

    if not major_changes:
        return None  # 사소한 변경은 건너뛰기

    # TAG 체인 상태 가져오기
    validation = validate_tag_chains(cwd)

    # 테스트 커버리지 가져오기
    coverage_result = subprocess.run(
        ["pytest", "--cov=src", "--cov-report=term-missing"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    coverage_match = re.search(r"TOTAL.*?(\d+)%", coverage_result.stdout)
    coverage = coverage_match.group(1) if coverage_match else "N/A"

    # 상태 섹션 빌드
    status = f""
## 프로젝트 상태

- **TAG 체인 무결성**: {validation['integrity_score']}%
- **완전한 체인**: {validation['complete_chains']}/{validation['total_chains']}
- **테스트 커버리지**: {coverage}%
- **테스트**: 모두 통과 ✅
- **마지막 업데이트**: {date.today().strftime("%Y-%m-%d")}

### 기능 구현

| 기능 | 상태 | TAG 체인 |
|---|---|---|
"

    # 기능 행 추가 (간소화됨)
    for tag_id in validation['complete']:
        status += f"| {tag_id} | ✅ 완료 | @SPEC → @TEST → @CODE |\n"

    for broken in validation['broken']:
        missing = ', '.join(broken['missing'])
        status += f"| {broken['id']} | ⚠️ 미완료 | 누락: {missing} |\n"

    # 현재 README 읽기
    with open(f"{cwd}/README.md", "r") as f:
        readme = f.read()

    # 상태 섹션 교체 (마커 사이)
    start_marker = "<!-- PROJECT_STATUS_START -->"
    end_marker = "<!-- PROJECT_STATUS_END -->"

    if start_marker in readme and end_marker in readme:
        before = readme.split(start_marker)[0]
        after = readme.split(end_marker)[1]
        updated_readme = f"{before}{start_marker}\n{status}\n{end_marker}{after}"
    else:
        # 마커가 없으면 추가
        updated_readme = readme + f"\n{start_marker}\n{status}\n{end_marker}\n"

    # 업데이트된 README 쓰기
    with open(f"{cwd}/README.md", "w") as f:
        f.write(updated_readme)

    return updated_readme

# 동기화 실행
sync_readme("/workspace/specter", major_changes=True)
print("✅ 프로젝트 상태로 README.md 업데이트됨")
```

**업데이트된 README.md**:
```markdown
# My-Spec 프로젝트

<!-- PROJECT_STATUS_START -->

## 프로젝트 상태

- **TAG 체인 무결성**: 86.67%
- **완전한 체인**: 13/15
- **테스트 커버리지**: 87%
- **테스트**: 모두 통과 ✅
- **마지막 업데이트**: 2025-10-26

### 기능 구현

| 기능 | 상태 | TAG 체인 |
|---|---|---|
| AUTH-001 | ✅ 완료 | @SPEC → @TEST → @CODE |
| HOOKS-001 | ✅ 완료 | @SPEC → @TEST → @CODE |
| HOOKS-002 | ✅ 완료 | @SPEC → @TEST → @CODE |
| AUTH-002 | ⚠️ 미완료 | 누락: CODE |
| HOOKS-005 | ⚠️ 미완료 | 누락: TEST |

<!-- PROJECT_STATUS_END -->

## 설치
...
```

---

## 예제 5: 병렬 API 문서 생성

**시나리오**: 여러 TAG에 대한 문서를 동시에 생성합니다.

```python
from concurrent.futures import ThreadPoolExecutor
import time

def generate_api_doc_for_tag(tag_id: str, cwd: str) -> tuple[str, float]:
    """단일 TAG에 대한 API 문서를 생성하고 시간을 측정합니다."""
    start = time.time()

    # 코드 파일 찾기
    code_file = subprocess.run(
        ["rg", f"@CODE:{tag_id}", "-l", "src/"],
        capture_output=True,
        text=True,
        cwd=cwd,
    ).stdout.strip()

    # 코드 읽기
    with open(f"{cwd}/{code_file}", "r") as f:
        content = f.read()

    # 함수 추출 (간소화됨)
    functions = extract_functions(content)

    # 마크다운 생성
    doc = f"# @DOC:{tag_id}\n\n"
    for func in functions:
        doc += f"## {func['name']}\n{func['signature']}\n\n"

    # 문서 쓰기
    with open(f"{cwd}/docs/api/{tag_id}.md", "w") as f:
        f.write(doc)

    duration = time.time() - start
    return (tag_id, duration)

# 순차 실행 (느림)
tag_ids = ["AUTH-001", "AUTH-002", "HOOKS-001", "HOOKS-002", "SKILLS-001"]

start = time.time()
for tag_id in tag_ids:
    generate_api_doc_for_tag(tag_id, "/workspace/specter")
sequential_duration = time.time() - start
print(f"순차: {sequential_duration:.2f}s")

# 병렬 실행 (빠름)
start = time.time()
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(generate_api_doc_for_tag, tag_id, "/workspace/specter")
        for tag_id in tag_ids
    ]
    results = [f.result() for f in futures]

parallel_duration = time.time() - start
print(f"병렬: {parallel_duration:.2f}s")
print(f"속도 향상: {sequential_duration / parallel_duration:.2f}x")

# 출력:
# 순차: 12.5s
# 병렬: 3.2s
# 속도 향상: 3.91x
```

---

## 예제 6: 스테이징된 변경 사항만 (증분 동기화)

**시나리오**: 스테이징된 파일에 대해서만 문서 동기화

```bash
# 특정 파일 스테이징
git add src/auth/service.py tests/unit/test_auth.py

# /ms.up-docs 실행 (기본값: 스테이징된 변경 사항만)
/ms.up-docs
```

**파이썬 구현**:
```python
def sync_staged_changes_only(cwd: str) -> dict:
    """스테이징된 파일에 대해서만 문서를 동기화합니다."""

    # 스테이징된 파일 가져오기
    staged_files = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=cwd,
    ).stdout.strip().split("\n")

    print(f"스테이징된 파일: {staged_files}")
    # ['src/auth/service.py', 'tests/unit/test_auth.py']

    # 스테이징된 파일에서 TAG 추출
    tag_ids = set()
    for file in staged_files:
        result = subprocess.run(
            ["rg", "@(CODE|TEST):([A-Z]+-[0-9]+)", "-or", "$2", file],
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        if result.stdout:
            tag_ids.update(result.stdout.strip().split("\n"))

    print(f"영향을 받는 TAG: {tag_ids}")
    # {'AUTH-001'}

    # 영향을 받는 TAG에 대해서만 문서 생성
    files_updated = []
    for tag_id in tag_ids:
        doc_file = f"docs/api/{tag_id}.md"
        generate_api_doc_for_tag(tag_id, cwd)
        files_updated.append(doc_file)

    return {
        "files_updated": files_updated,
        "staged_files": staged_files,
        "affected_tags": list(tag_ids),
    }

# 실행
result = sync_staged_changes_only("/workspace/specter")
print(result)
```

**출력**:
```json
{
  "files_updated": ["docs/api/AUTH-001.md"],
  "staged_files": ["src/auth/service.py", "tests/unit/test_auth.py"],
  "affected_tags": ["AUTH-001"]
}
```

---

## 예제 7: 전체 동기화 (모든 문서)

**시나리오**: 모든 문서 유형 동기화

```bash
# 전체 동기화 실행
/ms.up-docs --all
```

**파이썬 구현**:
```python
def sync_all_docs(cwd: str) -> dict:
    """전체 문서 동기화를 수행합니다."""
    start_time = time.time()

    # 1. API 문서 동기화 (모든 TAG)
    tag_ids = scan_all_tags(cwd)
    api_docs_updated = []
    for tag_id in tag_ids:
        generate_api_doc_for_tag(tag_id, cwd)
        api_docs_updated.append(f"docs/api/{tag_id}.md")

    # 2. 개발 일일 업데이트
    git_diff = subprocess.run(
        ["git", "diff", "HEAD~1"],
        capture_output=True,
        text=True,
        cwd=cwd,
    ).stdout
    sync_dev_daily(git_diff, cwd)

    # 3. README 업데이트 (주요 변경 사항이 있는 경우)
    major_changes = detect_major_changes(git_diff)
    if major_changes:
        sync_readme(cwd, major_changes=True)

    # 4. TAG 체인 유효성 검사
    validation = validate_tag_chains(cwd)

    duration = time.time() - start_time

    return {
        "files_updated": api_docs_updated + ["docs/dev_daily.md", "README.md"],
        "tag_integrity": validation["integrity_score"],
        "duration_seconds": round(duration, 2),
        "complete_chains": validation["complete_chains"],
        "total_chains": validation["total_chains"],
    }

# 실행
result = sync_all_docs("/workspace/specter")
print(result)
```

**출력**:
```json
{
  "files_updated": [
    "docs/api/AUTH-001.md",
    "docs/api/HOOKS-001.md",
    "docs/api/HOOKS-002.md",
    "docs/api/SKILLS-001.md",
    "docs/dev_daily.md",
    "README.md"
  ],
  "tag_integrity": 86.67,
  "duration_seconds": 8.3,
  "complete_chains": 13,
  "total_chains": 15
}
```

---

## 예제 8: /fin 통합 (커밋 전 자동 동기화)

**시나리오**: `/fin` 명령이 커밋 전에 개발 일일 로그를 자동으로 동기화합니다.

```bash
# 사용자 실행
/fin

# 실행 순서:
# 1. /ms.up-docs --docs=dev
# 2. make ci
# 3. git add .
# 4. git commit
# 5. git push
```

**명령 구현** (.claude/commands/fin.md):
```markdown
# /fin - 워크플로우 완료

1. 개발 일일 로그 업데이트:
   - 실행: `/ms.up-docs --docs=dev`
   - 오늘의 변경 사항을 `docs/dev_daily.md`에 추가합니다.

2. CI 확인 실행:
   - 실행: `make ci` (테스트, 린터, 타입 확인)
   - CI가 실패하면 커밋을 차단합니다.

3. 변경 사항 커밋:
   - 모두 스테이징: `git add .`
   - 커밋: `git commit -m "feat: [설명] @TAG-ID"`
   - 태그 참조: 커밋 메시지에 TAG ID 포함

4. 원격으로 푸시:
   - 실행: `git push`
```

**실행 예시**:
```bash
$ /fin

✅ 개발 일일 로그 업데이트 중...
   - 2025-10-26 항목 추가됨
   - TAG 체인: 13/15 완료 (86.67%)

✅ CI 확인 실행 중...
   - 테스트: 18/18 통과
   - 커버리지: 87%
   - 린터: 경고 0개
   - 타입 확인: 통과

✅ 변경 사항 커밋 중...
   - 스테이징됨: 5개 파일
   - 커밋: feat: 사용자 인증 구현 @AUTH-001
   - 브랜치: feature/auth-001

✅ 원격으로 푸시 중...
   - 원격: origin/feature/auth-001
   - 상태: 최신

🎉 워크플로우 완료!
```

---

## 예제 9: 오류 처리 (Fail-open)

**시나리오**: 문서 동기화가 실패하지만 커밋은 계속됩니다.

```python
def sync_with_failopen(cwd: str) -> dict:
    """fail-open 오류 처리로 문서를 동기화합니다."""
    try:
        # 전체 동기화 시도
        result = sync_all_docs(cwd)
        result["status"] = "SUCCESS"
        return result

    except FileNotFoundError as e:
        # 누락된 파일 (예: spec.md)
        logger.warning(f"문서 동기화 실패: {e}")
        return {
            "status": "PARTIAL",
            "error": f"누락된 파일: {e}",
            "files_updated": [],
            "tag_integrity": None,
        }

    except subprocess.CalledProcessError as e:
        # Git 명령 실패
        logger.error(f"Git 오류: {e}")
        return {
            "status": "FAILED",
            "error": f"Git 오류: {e.stderr}",
            "files_updated": [],
        }

    except Exception as e:
        # 알 수 없는 오류
        logger.error(f"예상치 못한 오류: {e}")
        return {
            "status": "FAILED",
            "error": str(e),
            "files_updated": [],
        }

# fail-open으로 실행
result = sync_with_failopen("/workspace/specter")

if result["status"] == "SUCCESS":
    print("✅ 문서 동기화 완료")
elif result["status"] == "PARTIAL":
    print(f"⚠️ 부분 동기화: {result['error']}")
    print("커밋은 계속됩니다 (fail-open)")
else:
    print(f"❌ 문서 동기화 실패: {result['error']}")
    print("커밋은 계속됩니다 (fail-open)")

# 동기화 상태에 관계없이 커밋 진행
subprocess.run(["git", "commit", "-m", "feat: 기능 구현"])
```

---

## 예제 10: 성능 벤치마킹

**시나리오**: 다양한 동기화 전략의 문서 동기화 성능 측정

```python
import time

def benchmark_sync_strategies(cwd: str, tag_count: int = 20):
    """다양한 동기화 전략을 벤치마킹합니다."""

    tag_ids = [f"TAG-{i:03d}" for i in range(1, tag_count + 1)]

    # 전략 1: 순차 (기준선)
    start = time.time()
    for tag_id in tag_ids:
        generate_api_doc_for_tag(tag_id, cwd)
    sequential_time = time.time() - start

    # 전략 2: 병렬 (4개 워커)
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(lambda tid: generate_api_doc_for_tag(tid, cwd), tag_ids))
    parallel_time = time.time() - start

    # 전략 3: 증분 (스테이징된 변경 사항만)
    staged_tag_ids = tag_ids[:5]  # 5개의 TAG만 변경됨
    start = time.time()
    for tag_id in staged_tag_ids:
        generate_api_doc_for_tag(tag_id, cwd)
    incremental_time = time.time() - start

    # 결과
    return {
        "tag_count": tag_count,
        "sequential": round(sequential_time, 2),
        "parallel": round(parallel_time, 2),
        "incremental": round(incremental_time, 2),
        "speedup_parallel": round(sequential_time / parallel_time, 2),
        "speedup_incremental": round(sequential_time / incremental_time, 2),
    }

# 벤치마크 실행
results = benchmark_sync_strategies("/workspace/specter", tag_count=20)
print(results)
```

**출력**:
```json
{
  "tag_count": 20,
  "sequential": 25.3,
  "parallel": 6.7,
  "incremental": 3.2,
  "speedup_parallel": 3.78,
  "speedup_incremental": 7.91
}
```

**결론**:
- 병렬 동기화: 순차보다 3.78배 빠름
- 증분 동기화: 7.91배 빠름 (변경된 TAG만 동기화)
- 10분 미만 목표: ✅ 달성 (20개 TAG에 6.7초)

```
# /ms.unlock - @IMMUTABLE 보호 파일 잠금 해제

Git 체크포인트 및 감사 로깅을 통해 @IMMUTABLE으로 보호된 파일을 일시적으로 잠금 해제합니다.

## 개요

@IMMUTABLE 파일은 우발적인 수정으로부터 보호됩니다. 이 명령은 적절한 명분과 안전 조치를 통해 의도적인 편집을 허용합니다.

## 사용법

```
/ms.unlock <파일_경로>
```

**인수**:
- `<파일_경로>`: 잠금 해제할 @IMMUTABLE 파일의 경로(절대 또는 상대)

**예시**:

```
/ms.unlock .specify/memory/constitution.md
```

## 실행 단계

### 1단계: 파일 경로 유효성 검사

**파일 존재 확인**:

```python
from pathlib import Path

file_path = args.get("file_path", "")
if not file_path:
    return "❌ 오류: 파일 경로가 필요합니다\n\n사용법: /ms.unlock <파일_경로>"

file_abs_path = Path(file_path).resolve()
if not file_abs_path.exists():
    return f"❌ 오류: 파일을 찾을 수 없습니다: {file_path}"
```

**파일에 @IMMUTABLE 마커가 있는지 확인**:

```python
from core.immutable_protection import scan_immutable_marker

if not scan_immutable_marker(str(file_abs_path)):
    return f"ℹ️  파일이 @IMMUTABLE으로 보호되지 않았습니다: {file_path}\n\n잠금 해제가 필요하지 않습니다 - 파일은 편집 가능합니다."
```

**이미 잠금 해제되었는지 확인**:

```python
from core.immutable_protection import is_file_unlocked

if is_file_unlocked(str(file_abs_path)):
    return f"✅ 현재 세션에서 파일이 이미 잠금 해제되었습니다: {file_path}\n\n이 파일을 정상적으로 편집할 수 있습니다."
```

### 2단계: 명분 프롬프트

**Claude Code AskUserQuestion을 통해 명분 수집**:

```
이 @IMMUTABLE 파일을 잠금 해제해야 하는 이유는 무엇입니까?

지침:
- 구체적인 이유를 제공하십시오(10자 이상).
- 예: "긴급 프로덕션 버그 수정", "헌법 개정 승인", "기능 요구 사항 변경"
- 명분은 감사 추적에 기록됩니다.
```

**명분 유효성 검사**:
- 10자 이상이어야 합니다.
- 공백 제거 후 비어 있지 않아야 합니다.
- 최대 3회 시도 허용

**유효성 검사 3회 실패 시**:

```
❌ 3회 실패 후 잠금 해제 취소

명분은 10자 이상이어야 합니다.

파일은 계속 보호됩니다: {file_path}
```

### 3단계: 잠금 해제 실행

**unlock_file 호출**:

```python
import os
from core.immutable_protection import unlock_file

result = unlock_file(
    file_path=str(file_abs_path),
    justification=user_justification,
    cwd=os.getcwd(),
)
```

**잠금 해제 성공 시**:

```
✅ 파일 잠금 해제 성공

📄 파일: {file_path}
🔓 상태: 현재 세션 동안 잠금 해제됨
📝 명분: {justification}
🛡️  Git 체크포인트: {checkpoint_ref}

⚠️  중요 참고 사항:
  - 잠금 해제는 세션 범위입니다(세션이 끝날 때까지만 지속됨).
  - 새 세션에서는 보호 기능이 자동으로 다시 적용됩니다.
  - 모든 변경 사항은 .specify/immutable_changes.log에 기록됩니다.
  - 롤백 안전을 위해 Git 체크포인트가 생성됩니다.

이제 이 파일을 정상적으로 편집할 수 있습니다.
```

**잠금 해제 실패 시**:

```
❌ 잠금 해제 실패: {error_message}

파일은 계속 보호됩니다: {file_path}

일반적인 원인:
  - Git 리포지토리가 아님(잠금 해제에는 체크포인트를 위한 Git이 필요함)
  - Git이 설치되지 않음
  - 명분이 너무 짧음(<10자)

문제를 해결하고 다시 시도하십시오.
```

### 4단계: 세션 상태 업데이트

**`unlock_file()` 함수에 의해 자동으로 업데이트되는 잠금 해제 레지스트리**:
- `UnlockRegistry` 싱글톤에 파일 추가
- 후속 편집/쓰기 작업은 PreToolUse 검사를 통과합니다.
- 잠금 해제는 SessionEnd 이벤트까지 지속됩니다(세션 범위).

## 오류 처리

### 오류 1: 파일을 찾을 수 없음

**증상**: 지정된 파일이 존재하지 않음

**메시지**:

```
❌ 오류: 파일을 찾을 수 없음: path/to/file.py

경로를 확인하고 다시 시도하십시오.
```

**종료**: 오류 메시지 반환

### 오류 2: 파일이 보호되지 않음

**증상**: 파일에 @IMMUTABLE 마커가 없음

**메시지**:

```
ℹ️  파일이 @IMMUTABLE으로 보호되지 않았습니다: path/to/file.py

잠금 해제가 필요하지 않습니다 - 파일은 제한 없이 편집 가능합니다.
```

**종료**: 정보 메시지 반환

### 오류 3: 잘못된 명분

**증상**: 명분이 10자 미만이거나 비어 있음

**메시지**:

```
❌ 명분이 너무 짧습니다(최소 10자).

이 파일을 잠금 해제하는 명확한 이유를 제공하십시오.

시도 1/3
```

**조치**: 다시 프롬프트(최대 3회 시도)

### 오류 4: Git 리포지토리 필요

**증상**: Git 누락으로 unlock_file() 실패

**메시지**:

```
❌ 잠금 해제 실패: Git 리포지토리가 아님

@IMMUTABLE 잠금 해제에는 체크포인트 생성을 위한 Git이 필요합니다.

Git을 초기화하십시오:
  cd /workspace/project
  git init
  git add .
  git commit -m "초기 커밋"
```

**종료**: 지침과 함께 오류 반환

## 보안 및 감사

**모든 잠금 해제 작업은 다음에 기록됩니다**:

```
.specify/immutable_changes.log
```

**로그 형식**:

```
[2025-10-26T14:30:00] 잠금 해제
파일: /workspace/project/.specify/memory/constitution.md
명분: 프로덕션 문제 #1234에 대한 긴급 버그 수정
체크포인트: immutable-unlock-20251026-143000
세션: claude-session-abc123
---
```

**로그 순환**: 없음(추가 전용 감사 추적)

**보존**: 영구(필요한 경우 수동 정리)

## 세션 수명 주기

1.  **SessionStart**: UnlockRegistry가 비어 있음
2.  **사용자가 /ms.unlock 실행**: 레지스트리에 파일 추가
3.  **세션 중**: 파일 편집 허용
4.  **SessionEnd**: UnlockRegistry.clear() 호출
5.  **다음 세션**: 보호 기능 다시 적용(다시 잠금 해제해야 함)

## 구현 세부 정보

**도구**: Read(유효성 검사), AskUserQuestion(명분), core.immutable_protection 함수

**종속성**:
- ripgrep ≥13.0 (@IMMUTABLE 스캔용)
- Git ≥2.30 (체크포인트 생성용)

**제약 조건**:
- 명분 ≥10자
- Git 리포지토리 필요
- 세션 범위 잠금 해제(비영구적)

## 관련 명령

- **@IMMUTABLE 마커**: 보호를 활성화하기 위해 파일에 추가
- **PreToolUse 후크**: @IMMUTABLE 편집을 자동으로 차단
- **SessionEnd 후크**: 잠금 해제 레지스트리 지우기

## 참고

- 잠금 해제는 **세션 범위**입니다(보안을 위한 의도적인 설계).
- 새 세션마다 다시 잠금 해제해야 합니다(우발적인 편집 방지).
- 모든 잠금 해제에 대해 Git 체크포인트가 생성됩니다(안전한 롤백).
- 감사 로그는 전체 잠금 해제 기록을 제공합니다.
- 보호 기능은 자동으로 다시 적용됩니다(수동으로 다시 보호할 필요 없음).

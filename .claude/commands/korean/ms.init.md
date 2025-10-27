---
description: "Spec-Kit + Constitution으로 My-Spec 프로젝트 초기화"
---

# /ms.init - My-Spec을 위한 원-커맨드 설정

단일 명령으로 Spec-Kit 및 My-Spec Constitution으로 프로젝트를 초기화합니다.

## 개요

이 명령은 **완전한 프로젝트 초기화**를 수행합니다:

1.  **Spec-Kit 설치** - 업스트림에서 최신 Spec-Kit을 자동으로 설치합니다.
2.  **헌법 설정** - My-Spec의 맞춤형 헌법 템플릿을 설치합니다.

**사용자 실행**: `/ms.init`만 실행하면 나머지는 모두 자동입니다!

## 실행 단계

### 1단계: Spec-Kit 설치(자동)

**중요**: 이 단계는 업스트림에서 Spec-Kit을 자동으로 설치합니다.

Spec-Kit 설치 명령을 실행합니다:

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --ai claude
```

**이 작업의 내용**:

-   GitHub에서 최신 Spec-Kit 릴리스를 다운로드합니다.
-   현재 디렉토리에 템플릿 파일을 추출합니다.
-   디렉토리 구조를 생성합니다:
    -   `.specify/` - Spec-Kit 메타데이터
    -   `.specify/templates/` - 템플릿 파일(constitution-template.md 포함)
    -   `.specify/scripts/` - 유틸리티 스크립트
    -   `specs/` - 사양 디렉토리
    -   에이전트별 명령(예: `.claude/commands/speckit.*`)

**완료 대기**: 이 명령은 30-60초 정도 걸릴 수 있습니다.

**확인**:

-   `.specify/`가 존재하는지 확인합니다.
-   `specs/`가 존재하는지 확인합니다.
-   누락된 경우: 오류를 표시하고(오류 처리 섹션 참조) 종료합니다.

### 2단계: My-Spec 헌법 설정(복사 모드)

#### 2.1 메모리 디렉토리 생성

```bash
mkdir -p .specify/memory
```

#### 2.2 헌법 템플릿 복사

`templates/constitution-template.md`를 `.specify/memory/constitution.md`로 복사합니다:

```bash
cp templates/constitution-template.md .specify/memory/constitution.md
```

**소스 파일을 찾을 수 없는 경우**:

-   오류 표시: "헌법 템플릿이 없습니다. 예상 위치: templates/constitution-template.md"
-   이는 리포지토리 구조 문제를 나타냅니다.
-   오류와 함께 종료합니다.

### 3단계: 훅 설치 확인

훅이 설치되었는지 확인합니다:

```bash
ls -la .claude/hooks/
```

**훅을 찾을 수 없는 경우**:
```
⚠️ 경고: 훅이 설치되지 않았습니다.

훅 활성화:
- 하위 에이전트에 헌법 자동 주입
- 작업 완료에 대한 오디오 알림

수동 설치:
1. .claude/hooks/ 디렉토리 생성
2. constitution-injector.sh 및 notify.sh 복사
3. chmod +x .claude/hooks/*.sh
4. .claude/hooks/sounds/에 사운드 파일 추가

또는 훅 없이 계속 진행합니다(헌법은 수동으로 참조됩니다).
```

**훅을 찾은 경우**:
```
✅ 훅 감지됨: 헌법 자동 주입 활성화됨
```

### 4단계: 성공 보고

완료 메시지를 표시합니다:

```
✅ My-Spec이 성공적으로 초기화되었습니다!

📦 설치됨:
- ✅ Spec-Kit (업스트림의 최신 버전)
- ✅ My-Spec 헌법: .specify/memory/constitution.md

🎯 다음 단계:

1. /ms.specify - 기능 사양 생성
2. /ms.clarify - 요구 사항 명확화(필요한 경우)
3. /ms.plan - 구현 계획 생성
4. /ms.constitution - 프로젝트별 제약 조건 추출(plan.md에서)
5. /ms.tasks - 구현 작업 생성
6. /ms.analyze - TRUST 준수 확인
7. /ms.implement - 구현 시작

📖 헌법 읽기: .specify/memory/constitution.md

💡 문서:
- 워크플로 문서(spec.md, plan.md, tasks.md) → /ms.* 명령으로 생성됨
- 살아있는 문서(docs/api/[TAG-ID].md) → /ms.implement에 의해 자동 생성됨
- AGENTS.md → /ms.constitution에 의해 생성됨

💡 팁: 바닐라 Spec-Kit 워크플로에 대해 /speckit.* 명령을 직접 사용할 수 있습니다.
```

## 오류 처리

### 오류 1: Spec-Kit 설치 실패

**증상**: `uvx` 명령이 실패하거나 `.specify/`가 생성되지 않음

**메시지**:

```
❌ 오류: Spec-Kit 설치 실패

명령이 Spec-Kit을 설치하지 못했습니다:
    uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --ai claude

다음을 확인하십시오:
1. 인터넷 연결
2. GitHub 접근성
3. uvx/uv가 올바르게 설치되었는지

수동 설치를 시도할 수 있습니다:
    uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --ai claude

그런 다음 /ms.init를 다시 실행하십시오.
```

**종료**: 코드 1

### 오류 2: 헌법 템플릿 누락

**증상**: `templates/constitution-template.md`를 찾을 수 없음

**메시지**:

```
❌ 오류: 헌법 템플릿을 찾을 수 없습니다.

예상 위치: templates/constitution-template.md

이는 리포지토리 구조 문제입니다.
my-spec 리포지토리 무결성을 확인하십시오.
```

**종료**: 코드 1

### 오류 3: 쓰기 권한 거부됨

**증상**: `.specify/memory/constitution.md`에 쓸 수 없음

**메시지**:

```
❌ 오류: 헌법 파일을 쓸 수 없습니다.

권한 거부됨: .specify/memory/constitution.md

다음을 확인하십시오:
1. .specify/memory/에 대한 디렉토리 권한
2. constitution.md가 이미 있는 경우 파일 권한
3. 디스크 공간 가용성
```

**종료**: 코드 1

## 사용된 도구

-   **Bash**: Spec-Kit 설치 실행, 디렉토리 확인, 디렉토리 생성, 파일 삭제
-   **Read**: 헌법 템플릿 로드
-   **Write**: constitution.md 생성(템플릿의 정확한 사본)

## 계약 참조

사양: [specs/001-my-spec-spec/spec.md](../../specs/001-my-spec-spec/spec.md)

## 다음 명령

`/ms.init` 후: `/ms.specify`를 실행하여 첫 번째 기능 사양을 생성합니다.

---
description: tasks.md에 정의된 모든 작업을 처리하고 실행하여 구현 계획을 실행합니다.
---

## 사용자 입력

```text
$ARGUMENTS
```

진행하기 전에 사용자 입력을 **반드시** 고려해야 합니다(비어 있지 않은 경우).

## 개요

1.  리포지토리 루트에서 `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`를 실행하고 FEATURE_DIR 및 AVAILABLE_DOCS 목록을 구문 분석합니다. 모든 경로는 절대 경로여야 합니다. "I'm Groot"와 같은 인수에 작은따옴표가 있는 경우 이스케이프 구문을 사용합니다(예: 'I'\''m Groot' 또는 가능한 경우 큰따옴표: "I'm Groot").

2.  **체크리스트 상태 확인**(FEATURE_DIR/checklists/가 있는 경우):
    *   checklists/ 디렉토리의 모든 체크리스트 파일 스캔
    *   각 체크리스트에 대해 다음을 계산합니다.
        *   총 항목: `- [ ]` 또는 `- [X]` 또는 `- [x]`와 일치하는 모든 줄
        *   완료된 항목: `- [X]` 또는 `- [x]`와 일치하는 줄
        *   미완료 항목: `- [ ]`와 일치하는 줄
    *   상태 테이블 만들기:

        ```text
        | 체크리스트 | 총계 | 완료됨 | 미완료 | 상태 |
        |---|---|---|---|---|
        | ux.md | 12 | 12 | 0 | ✓ 통과 |
        | test.md | 8 | 5 | 3 | ✗ 실패 |
        | security.md | 6 | 6 | 0 | ✓ 통과 |
        ```

    *   전체 상태 계산:
        *   **통과**: 모든 체크리스트에 미완료 항목이 0개입니다.
        *   **실패**: 하나 이상의 체크리스트에 미완료 항목이 있습니다.

    *   **체크리스트가 불완전한 경우**:
        *   미완료 항목 수가 있는 테이블 표시
        *   **중지**하고 "일부 체크리스트가 불완전합니다. 구현을 계속하시겠습니까? (예/아니오)"라고 묻습니다.
        *   계속하기 전에 사용자 응답을 기다립니다.
        *   사용자가 "아니오" 또는 "대기" 또는 "중지"라고 말하면 실행을 중지합니다.
        *   사용자가 "예" 또는 "진행" 또는 "계속"이라고 말하면 3단계로 진행합니다.

    *   **모든 체크리스트가 완료된 경우**:
        *   모든 체크리스트가 통과되었음을 보여주는 테이블 표시
        *   자동으로 3단계로 진행

3.  구현 컨텍스트 로드 및 분석:
    *   **필수**: 전체 작업 목록 및 실행 계획에 대한 tasks.md 읽기
    *   **필수**: 기술 스택, 아키텍처 및 파일 구조에 대한 plan.md 읽기
    *   **있는 경우**: 엔터티 및 관계에 대한 data-model.md 읽기
    *   **있는 경우**: API 사양 및 테스트 요구 사항에 대한 contracts/ 읽기
    *   **있는 경우**: 기술 결정 및 제약 조건에 대한 research.md 읽기
    *   **있는 경우**: 통합 시나리오에 대한 quickstart.md 읽기

4.  **프로젝트 설정 확인**:
    *   **필수**: 실제 프로젝트 설정을 기반으로 무시 파일 생성/확인:

    **감지 및 생성 논리**:
    *   리포지토리가 git 리포지토리인지 확인하기 위해 다음 명령이 성공하는지 확인합니다(그렇다면 .gitignore 생성/확인).

        ```sh
        git rev-parse --git-dir 2>/dev/null
        ```

    *   Dockerfile*이 있거나 plan.md에 Docker가 있는지 확인 → .dockerignore 생성/확인
    *   .eslintrc* 또는 eslint.config.*가 있는지 확인 → .eslintignore 생성/확인
    *   .prettierrc*가 있는지 확인 → .prettierignore 생성/확인
    *   .npmrc 또는 package.json이 있는지 확인 → .npmignore 생성/확인(게시하는 경우)
    *   terraform 파일(*.tf)이 있는지 확인 → .terraformignore 생성/확인
    *   .helmignore가 필요한지 확인(helm 차트가 있는 경우) → .helmignore 생성/확인

    **무시 파일이 이미 있는 경우**: 필수 패턴이 포함되어 있는지 확인하고 누락된 중요한 패턴만 추가합니다.
    **무시 파일이 없는 경우**: 감지된 기술에 대한 전체 패턴 세트로 생성합니다.

    **기술별 공통 패턴**(plan.md 기술 스택에서):
    *   **Node.js/JavaScript/TypeScript**: `node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
    *   **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
    *   **Java**: `target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
    *   **C#/.NET**: `bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
    *   **Go**: `*.exe`, `*.test`, `vendor/`, `*.out`
    *   **Ruby**: `.bundle/`, `log/`, `tmp/`, `*.gem`, `vendor/bundle/`
    *   **PHP**: `vendor/`, `*.log`, `*.cache`, `*.env`
    *   **Rust**: `target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`, `*.prof*`, `.idea/`, `*.log`, `.env*`
    *   **Kotlin**: `build/`, `out/`, `.gradle/`, `.idea/`, `*.class`, `*.jar`, `*.iml`, `*.log`, `.env*`
    *   **C++**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.so`, `*.a`, `*.exe`, `*.dll`, `.idea/`, `*.log`, `.env*`
    *   **C**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.a`, `*.so`, `*.exe`, `Makefile`, `config.log`, `.idea/`, `*.log`, `.env*`
    *   **Swift**: `.build/`, `DerivedData/`, `*.swiftpm/`, `Packages/`
    *   **R**: `.Rproj.user/`, `.Rhistory`, `.RData`, `.Ruserdata`, `*.Rproj`, `packrat/`, `renv/`
    *   **범용**: `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

    **도구별 패턴**:
    *   **Docker**: `node_modules/`, `.git/`, `Dockerfile*`, `.dockerignore`, `*.log*`, `.env*`, `coverage/`
    *   **ESLint**: `node_modules/`, `dist/`, `build/`, `coverage/`, `*.min.js`
    *   **Prettier**: `node_modules/`, `dist/`, `build/`, `coverage/`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
    *   **Terraform**: `.terraform/`, `*.tfstate*`, `*.tfvars`, `.terraform.lock.hcl`
    *   **Kubernetes/k8s**: `*.secret.yaml`, `secrets/`, `.kube/`, `kubeconfig*`, `*.key`, `*.crt`

5.  tasks.md 구조를 구문 분석하고 다음을 추출합니다.
    *   **작업 단계**: 설정, 테스트, 핵심, 통합, 마무리
    *   **작업 종속성**: 순차 대 병렬 실행 규칙
    *   **작업 세부 정보**: ID, 설명, 파일 경로, 병렬 마커 [P]
    *   **실행 흐름**: 순서 및 종속성 요구 사항

6.  작업 계획에 따라 구현 실행:
    *   **단계별 실행**: 다음 단계로 이동하기 전에 각 단계를 완료합니다.
    *   **종속성 존중**: 순차 작업을 순서대로 실행하고 병렬 작업 [P]은 함께 실행할 수 있습니다.
    *   **TDD 접근 방식 따르기**: 해당 구현 작업 전에 테스트 작업을 실행합니다.
    *   **파일 기반 조정**: 동일한 파일에 영향을 미치는 작업은 순차적으로 실행해야 합니다.
    *   **유효성 검사 체크포인트**: 진행하기 전에 각 단계 완료를 확인합니다.

7.  구현 실행 규칙:
    *   **먼저 설정**: 프로젝트 구조, 종속성, 구성 초기화
    *   **코드 전 테스트**: 계약, 엔터티 및 통합 시나리오에 대한 테스트를 작성해야 하는 경우
    *   **핵심 개발**: 모델, 서비스, CLI 명령, 엔드포인트 구현
    *   **통합 작업**: 데이터베이스 연결, 미들웨어, 로깅, 외부 서비스
    - **다듬기 및 검증**: 단위 테스트, 성능 최적화, 문서화

8. 진행 상황 추적 및 오류 처리:
    - 완료된 각 작업 후 진행 상황 보고
    - 병렬이 아닌 작업이 실패하면 실행 중단
    - 병렬 작업 [P]의 경우 성공적인 작업으로 계속하고 실패한 작업 보고
    - 디버깅을 위한 컨텍스트와 함께 명확한 오류 메시지 제공
    - 구현을 진행할 수 없는 경우 다음 단계 제안
    - **중요** 완료된 작업의 경우 작업 파일에서 작업을 [X]로 표시해야 합니다.

9. 완료 확인:
    - 필요한 모든 작업이 완료되었는지 확인
    - 구현된 기능이 원래 사양과 일치하는지 확인
    - 테스트가 통과하고 적용 범위가 요구 사항을 충족하는지 확인
    - 구현이 기술 계획을 따르는지 확인
    - 완료된 작업 요약과 함께 최종 상태 보고

참고: 이 명령은 tasks.md에 완전한 작업 분석이 있다고 가정합니다. 작업이 불완전하거나 누락된 경우 먼저 `/speckit.tasks`를 실행하여 작업 목록을 다시 생성하도록 제안합니다.

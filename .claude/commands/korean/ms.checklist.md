---
description: "현재 기능에 대한 사용자 지정 체크리스트 생성(My-Spec 래퍼)"
---

# /ms.checklist - 기능 체크리스트 생성

**My-Spec 래퍼**: 이 명령은 기본 `/speckit.checklist` 명령을 전체 기능으로 실행합니다.

## 목적

현재 기능에 대한 사용자 지정 요구 사항 품질 체크리스트("영어를 위한 단위 테스트")를 생성합니다.

## 사용법

```bash
/ms.checklist [선택 사항: 체크리스트 초점/유형 설명]
```

**예시**:
```bash
/ms.checklist                          # 대화형: AI가 명확한 질문을 합니다.
/ms.checklist ux review                # UX 요구 사항 품질에 중점
/ms.checklist api security             # API + 보안 요구 사항 체크리스트
/ms.checklist comprehensive review     # 전체 요구 사항 검토 체크리스트
```

## 기능

이 명령은 다른 My-Spec 명령(`/ms.specify`, `/ms.plan`, `/ms.implement` 등)과의 이름 지정 일관성을 유지하기 위해 `/speckit.checklist`를 래핑합니다.

## 실행 단계

### 0단계: 프로젝트 컨텍스트 로드

**프로젝트 문서 자동 로드**:
- `.specify/memory/constitution.md` (헌법 - 필수)
- `AGENTS.md` (AI 지침, 코딩 표준 - 있는 경우)
- `specs/[spec-id]/spec.md` (기능 사양 - 필수)

**헌법 또는 spec.md가 없는 경우**:
- 오류 표시: "필수 파일이 없습니다. 먼저 `/ms.init` 및 `/ms.specify`를 실행하십시오."
- 종료

**체크리스트 생성을 위한 참조**:
- 헌법 섹션 IV (EARS 표준 - 검증할 요구 사항 패턴)
- 헌법 섹션 IX (프로젝트별 품질 표준 - **있는 경우**, `/ms.constitution`에 의해 추가됨)
- AGENTS.md (코딩 표준, 품질 기대치)

**이 문서들은 다음을 돕습니다**:
- EARS 패턴 준수를 검증하는 체크리스트 생성
- 프로젝트별 품질 기준 적용(예: 섹션 IX의 성능 목표)
- 프로젝트 기술 스택을 기반으로 관련 질문 생성

### 1단계: 기본 명령 실행

헌법 컨텍스트와 함께 기본 Spec-Kit 체크리스트 명령 실행:

```
/speckit.checklist $ARGUMENTS
```

## 워크플로 위치

```
/ms.specify → /ms.clarify → /ms.plan → /ms.constitution → /ms.tasks → /ms.analyze
                ↓                                                            ↓
          [/ms.checklist]                                              [/ms.checklist]
                ↓                                                            ↓
         spec.md 검증                                        모든 요구 사항 검증
         요구 사항 품질                                    구현 전
```

**사용 시기**:
1. **`/ms.specify` 또는 `/ms.clarify` 이후**: spec.md 요구 사항이 완전하고 명확하며 일관적인지 확인
2. **`/ms.plan` 이후**: 기술 요구 사항 및 제약 조건이 잘 정의되었는지 확인
3. **`/ms.tasks` 이후**: 모든 구현 작업이 명확한 요구 사항에 매핑되는지 확인
4. **언제든지**: 특정 품질 측면(UX, API, 보안 등)에 대한 집중 체크리스트 생성

## 참고

- **래퍼 전용**: 모든 로직은 `/speckit.checklist`에서 처리됩니다.
- **이름 지정 일관성**: 통일된 My-Spec 명령 경험을 위해 `/ms.checklist`를 사용합니다.
- **전체 기능**: 기본 명령과 기능 차이가 없습니다.
- **여러 번 실행**: 각 실행은 새 체크리스트 파일을 생성할 수 있습니다(예: `ux.md`, `api.md`).

## 참조

- **[/speckit.checklist](.claude/commands/speckit.checklist.md)**: 전체 구현 세부 정보
- **[체크리스트 템플릿](../../templates/checklist-template.md)**: 표준 형식
- **헌법 참조**: My-Spec 프로젝트는 자동으로 헌법 제약 조건을 참조합니다.

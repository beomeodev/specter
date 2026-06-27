# Changelog

All notable changes to this repository are documented in this file.

## [2.1.1] - 2026-06-27

### Changed
- **Antigravity 위임 모델 고정**: `/fin`, `/finq`, `/ms.merglease`, `/ms.verify`, `/ms.analyze`,
  `/ms.review`, `/ms.agent-verify` 및 README의 안티그래비티 위임 지점 9곳에서 `--model`을
  `gemini-2.5-pro` → `gemini-3.5-flash`로 변경. `--model` 플래그가 플러그인 기본값을 덮어쓰므로
  `in-plugin` 업데이트와 무관하게 모델이 고정됨. Codex(`gpt-5.5`)는 변경하지 않음.
- 안티그래비티 이중 에이전트(Codex & Antigravity) 교차 검증 및 실행 파이프라인 위임을
  `/ms.analyze`·`/ms.review`·`/ms.agent-verify`·`/ms.verify`에 반영.

### Docs
- README의 `/ms.verify` 설명과 명령어 플래그(`--skip-codex`/`--background`/`--model`/`--effort`/
  `--adversarial`) 문서화 보강 및 역할·프로세스 설명 정리.

## [2.1.0] - 2026-06-24

### Changed
- **Spec-Kit 호환성 (loose coupling)**: `/ms.init`의 Feature-Map 게이트 주입을 command·skill
  **양쪽 레이아웃과 dual 레이아웃**까지 탐지·주입하도록 확장. 존재하는 모든 후보 파일에
  주입하며 `MS_FEATUREMAP_GATE_START` 마커로 idempotent.
- 업스트림 스킬 개명에 맞춰 `/ms.*` 래퍼의 위임 호출을 `speckit.x` → `speckit-x`로 정렬
  (specify·clarify·plan·tasks·analyze·implement). 라이브 `specify init` v0.11.6로 검증.
- 업스트림 버전을 `SPEC_KIT_REF`로 핀(기본 `v0.11.6`)하여 churn 차단. 구형 `--ai` 플래그를
  현행 `--integration claude`로 교체.
- `/ms.review`의 prerequisites 호출을 현행 spec-kit 경로/플래그로 교정
  (`.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`).
  spec.md/plan.md 검증은 SPECTER가 자체 소유함을 명문화.
- `/ms.init` 검증에서 `specs/` 요구 제거(첫 `/ms.specify` 때 생성됨), `docs/templates` 출처 정정,
  spec-kit의 `CLAUDE.md` 블록 append 동작 문서화.
- **devcontainer**: 종료된 Gemini CLI(2026-06-18)를 후속 Antigravity CLI(`agy`)로 교체.
  Dockerfile 설치 방식·Makefile 타깃(`gemini gm`→`antigravity agy ag gm`, `gm` 별칭 유지)·
  docker-compose 자격증명 볼륨(`~/.gemini`→`~/.config/agy`)·`setup-pm.sh` 안내문 갱신.

### Added
- `/ms.*` 명령에 `argument-hint` frontmatter 추가(슬래시 입력 힌트).
- README "Spec Kit 호환성"에 **위임 지점 표 · 정체성 불변식 · 결별 기준(divorce tripwires)** 문서화.
- AGENTS.md §10에 command/skill/agent 계층 정의와 Spec-Kit 결합 계약·정체성 규칙 추가.

## [2.0.0] - 2026-06-18

### Changed
- Reworked the `/ms.*` workflow documentation to match the current feature-map, checklist, plan, tasks, analyze, implement, and review flow.
- Clarified Codex plugin setup so users enter the project container through Codex CLI, then install the plugin from the Codex plugin directory.
- Updated `ms.init` output to guide users through the correct plugin installation path.
- Simplified repository docs to keep only the template-oriented files and agent-facing snapshot needed by this template repo.

### Added
- Restored `docs/dev_daily.md` and `docs/todo.md` as empty template files.
- Restored `docs/SYSTEM_MAP.md` as an agent-facing snapshot.
- Added a root-level changelog for release notes.

### Removed
- Deleted template-repo-only operational docs that were not meant to remain as permanent artifacts.

## [1.0.0] - 2025-01-01

### Added
- Initial stable release baseline.

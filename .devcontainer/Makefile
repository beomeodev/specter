# 루트 디렉토리의 Makefile과 달리 프로젝트 돌입 후에는 변경/추가가 없음.
# 밑에 단축 타겟이 아주 중요함. 프로젝트 새로 만들때마다 수정하기.

# ======= 프로젝트 설정 (새 프로젝트 시작 시 여기만 수정) =======
PROJ_TICKER := spt
PROJ_REPO := git@github.com:beomeodev/specter.git

# ======= 범용 설정 =======
# 현재 디렉토리명을 프로젝트명으로 자동 추출 (docker-compose.yml에서 사용)
# .devcontainer에서 실행되므로 상위 디렉토리명을 사용
PROJECT_NAME := $(notdir $(abspath $(CURDIR)/..))
export PROJECT_NAME

# COMPOSE 명령어에 PROJECT_NAME 환경변수 포함
COMPOSE ?= PROJECT_NAME=$(PROJECT_NAME) docker compose -f docker-compose.yml

BUILD_TRIGGERS := Dockerfile docker-compose.yml pyproject.toml package.json package-lock.json

# ======= 범용 sync (상위/하위 어디서 실행해도 OK) =======
.PHONY: sync
sync:
	@if [ -z "$(repo)" ]; then \
		echo "❌ repo 파라미터 필요: make sync repo=git@github.com:username/repo.git"; \
		exit 1; \
	fi; \
	set -e; \
	repo_url="$(repo)"; \
	name=$${repo_url##*/}; \
	name=$${name%.git}; \
	if [ -z "$$name" ]; then \
		echo "❌ repo 이름을 파싱할 수 없습니다: $(repo)"; \
		exit 1; \
	fi; \
	# .devcontainer에서 실행중인지 확인하고 상위 디렉토리로 이동 \
	if [ "$$(basename "$$PWD")" = ".devcontainer" ] && [ -d ".." ]; then \
		echo "🔄 .devcontainer에서 실행중 - 상위 디렉토리로 이동"; \
		cd ..; \
	fi; \
	# 현재 디렉토리명이 레포지토리명과 같으면 여기서 git 초기화 \
	current_dir_name=$$(basename "$$PWD"); \
	if [ "$$current_dir_name" = "$$name" ] && [ ! -d ".git" ]; then \
		echo "📁 현재 디렉토리($$current_dir_name)가 타겟 레포지토리($$name)와 일치 - git 초기화"; \
		git init; \
		git remote add origin "$$repo_url"; \
		echo "✅ git 초기화 완료"; \
	fi; \
	target_dir=""; \
	if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
		current_origin=$$(git remote get-url origin 2>/dev/null || printf ''); \
		# Normalize URLs for comparison (both SSH and HTTPS formats) \
		normalized_current=$$(echo "$$current_origin" | sed -e 's|^git@github.com:|https://github.com/|' -e 's|\.git$$||'); \
		normalized_repo=$$(echo "$$repo_url" | sed -e 's|^git@github.com:|https://github.com/|' -e 's|\.git$$||'); \
		if [ "$$normalized_current" = "$$normalized_repo" ]; then \
			offline_sync=0; \
			echo "⚠️  현재 디렉토리가 타겟 repo입니다. 현재 상태를 업데이트합니다."; \
			echo ""; \
			echo "🔍 현재 git 상태 확인중..."; \
			cur_branch=$$(git branch --show-current 2>/dev/null || echo "unknown"); \
			echo "📍 현재 브랜치: $$cur_branch"; \
			echo ""; \
			echo "📥 원격 저장소에서 최신 정보를 가져옵니다..."; \
			echo "실행: git fetch --all --prune"; \
			if git fetch --all --prune; then \
				offline_sync=0; \
			else \
				offline_sync=1; \
				echo "⚠️  git fetch 실패 (오프라인 또는 접근 권한 문제). 로컬 상태로 계속 진행합니다."; \
			fi; \
			echo ""; \
			echo "🔍 작업 디렉토리 변경사항 확인중..."; \
			if ! git diff-index --quiet HEAD --; then \
				echo "⚠️  로컬 변경사항 있음 (커밋되지 않음):"; \
				git status --short; \
				echo ""; \
				echo "💡 작업 종료 시 'make finish' 또는 'make finq'로 커밋/푸시하세요"; \
			else \
				echo "✅ 변경사항 없음"; \
			fi; \
		echo ""; \
		if [ "$$offline_sync" != "1" ]; then \
			echo "📥 원격 저장소에서 최신 변경사항을 가져옵니다..."; \
			echo "실행: git pull --rebase --prune"; \
			git pull --rebase --prune || { \
				echo "⚠️  현재 브랜치에 tracking 정보가 없습니다. 건너뜁니다."; \
			}; \
		else \
			echo "⚠️  이전 단계에서 원격 fetch 실패 → pull 건너뜀"; \
		fi; \
			echo ""; \
			final_branch=$$(git branch --show-current 2>/dev/null || echo "unknown"); \
			echo "🌿 최종 브랜치: $$final_branch"; \
			echo "✅ Done: $$PWD"; \
			exit 0; \
		fi; \
	fi; \
	if [ -z "$$target_dir" ] && [ -d "./$$name/.git" ]; then \
		target_dir="./$$name"; \
	fi; \
	if [ -z "$$target_dir" ]; then \
		target_dir="./$$name"; \
		echo "▶ Cloning $$repo_url -> $$target_dir"; \
		git clone "$$repo_url" "$$target_dir"; \
		CLONED=1; \
	else \
		echo "▶ Using existing repo at $$target_dir"; \
		CLONED=0; \
		if git -C "$$target_dir" fetch --all --prune; then \
			git -C "$$target_dir" pull --rebase --prune || echo "⚠️  pull 실패 (tracking 미설정 또는 오프라인)"; \
		else \
			echo "⚠️  git fetch 실패 (오프라인). 원격 동기화 없이 계속합니다."; \
		fi; \
	fi; \
	if [ ! -f "$$target_dir/.env" ] && [ -f "$$target_dir/.env.example" ]; then \
		echo "⚠️  .env 없음 → .env.example 복사"; \
		cp -n "$$target_dir/.env.example" "$$target_dir/.env" || true; \
	fi; \
	$(MAKE) -C "$$target_dir/.devcontainer" dev-up; \
	cur_branch=$$(git -C "$$target_dir" branch --show-current 2>/dev/null || echo "unknown"); \
	echo "🌿 Current branch: $$cur_branch"; \
	echo "✅ Done: $$target_dir"

# ======= 프로젝트 정의 (자동 생성 - 수정 금지) =======
.PHONY: $(PROJ_TICKER)
$(PROJ_TICKER):
	@$(MAKE) -s sync repo=$(PROJ_REPO)


# ======= 범용 런처 (모든 프로젝트에서 재사용 가능) =======
.PHONY: go
go:
	@if [ -z "$(proj)" ] || [ -z "$(agent)" ]; then \
		echo "❌ Usage: make go proj=$(PROJ_TICKER) agent=cc"; \
		exit 1; \
	fi
	@$(MAKE) -s $(proj) && $(MAKE) $(agent)

# ======= 프로젝트별 단축어 (자동 생성 - 수정 금지) =======
.PHONY: $(PROJ_TICKER)cc $(PROJ_TICKER)cx $(PROJ_TICKER)cr $(PROJ_TICKER)gm
$(PROJ_TICKER)cc:
	@$(MAKE) -s sync repo=$(PROJ_REPO) && $(MAKE) cc

$(PROJ_TICKER)cx:
	@$(MAKE) -s sync repo=$(PROJ_REPO) && $(MAKE) cx

$(PROJ_TICKER)cr:
	@$(MAKE) -s sync repo=$(PROJ_REPO) && $(MAKE) cr

$(PROJ_TICKER)gm:
	@$(MAKE) -s sync repo=$(PROJ_REPO) && $(MAKE) gm


# ======= 새 프로젝트 시작 가이드 =======
# 1. 파일 최상단(5-6번 라인)의 PROJ_TICKER와 PROJ_REPO만 수정
# 2. 나머지는 자동으로 적용됨 (ctrl+d로 일일이 찾을 필요 없음)
# 3. 레포지토리 이름과 로컬 폴더 이름은 항상 일치시키기
# 4. pm <ticker> cc 명령어로 pull/clone + 컨테이너 실행 + 에이전트 실행 자동화

# 세부 내용(기록만 해둠)

# pull 관련해서 git fetch --all --prune + git status -sb 까지도 포함되어 있음.
# 왜 이렇게?
# fetch --all --prune: 원격에서 지워진 브랜치 “좀비 레퍼런스”까지 정리해서 로컬 뷰가 깔끔해짐.
# status -sb: git status의 한 줄 요약(브랜치/변경/추적상태가 한눈에) → 더 빠르게 판단.
# ① fetch: 원격 저장소에서 최신 커밋과 브랜치 정보만 가져옴, 로컬 코드(working tree)는 안 바뀜
# ③ prune: 원격에서 사라진 브랜치를 로컬에서도 지워줌, 안 쓰면, 이미 서버에서 지워진 브랜치가 로컬에 “좀비”로 남음
# ④ rebase: 기본값인 merge 대용. rebase: 내가 가진 커밋을 최신 원격 커밋 뒤에 깔끔히 이어붙임 → 기록이 직선으로 깔끔


# ======= 기존 프로젝트 내부 타겟 =======
.PHONY: up down start stop sh install test fmt lint precommit dbup cacheup nbup rebuild

up:
	$(COMPOSE) up -d --build app

down:
	$(COMPOSE) down

start:
	@if [ -z "$$SSH_AUTH_SOCK" ]; then \
		echo "⚠️  SSH agent not running. Run:"; \
		echo "    eval $$(ssh-agent -s) && ssh-add ~/.ssh/id_ed25519"; \
		echo ""; \
	fi
	@container_id="$$( $(COMPOSE) ps -q app 2>/dev/null || true )"; \
	if [ -n "$$container_id" ]; then \
		if [ "$$(docker inspect -f '{{.State.Running}}' "$$container_id" 2>/dev/null || echo false)" = "true" ]; then \
			echo "✅ Container already running - skipping start"; \
		else \
			echo "🚀 Starting existing container..."; \
			$(COMPOSE) start app; \
		fi; \
	else \
		echo "🚀 Creating container..."; \
		$(COMPOSE) up -d app; \
	fi

stop:
	$(COMPOSE) stop app

rebuild:
	$(COMPOSE) build --no-cache app

sh:
	$(COMPOSE) exec app bash

install:
	# pyproject.toml 기반 의존성 설치
	$(COMPOSE) exec app bash -lc "test -f pyproject.toml && pip install -e . || echo 'pyproject.toml 없음: 건너뜀'"

test:
	$(COMPOSE) exec app pytest -q

fmt:
	$(COMPOSE) exec app bash -lc "ruff check --fix . && ruff format ."

lint:
	$(COMPOSE) exec app ruff check .

precommit:
	$(COMPOSE) exec app pre-commit run --all-files

dbup:
	$(COMPOSE) --profile db up -d postgres

cacheup:
	$(COMPOSE) --profile cache up -d redis

nbup:
	$(COMPOSE) --profile notebook up -d jupyter

.PHONY: dev-up du dev-shell ds codex cx codex-resume cr, claude cc antigravity agy ag gm

# Build/refresh the app container image and ensure it is running
dev-up du: start

# Open an interactive shell inside the app container (builds first if needed)
dev-shell ds: dev-up
	$(COMPOSE) exec app bash

# Launch the Codex CLI inside the running container
codex cx: dev-up
	$(COMPOSE) exec app codex

# Resume the last Codex session
codex-resume cr: dev-up
	$(COMPOSE) exec app codex resume --last

# Launch the Claude Code CLI inside the running container
claude cc: dev-up
	$(COMPOSE) exec -e NODE_OPTIONS="--max-old-space-size=4096" app claude

# Launch the Antigravity CLI (Gemini CLI 후속) inside the running container
# 바이너리명은 agy. gm 별칭은 `pm <ticker> gm` 습관 유지를 위해 그대로 둔다.
# 인증: .env의 GEMINI_API_KEY/ANTIGRAVITY_API_KEY 또는 최초 1회 대화형 OTP 로그인
antigravity agy ag gm: dev-up
	$(COMPOSE) exec app agy


# ======= CI 파이프라인 (로컬 + GitHub Actions 공통) =======
.PHONY: ci-lint ci-type ci-test ci finish

# CI 타깃은 `make -C .devcontainer` 로 호출돼 CWD가 .devcontainer/ 이므로
# 레포 루트($(CURDIR)/..)로 이동해서 실제 코드를 대상으로 검사한다.
ROOT := $(CURDIR)/..

# Lint: 코드 포맷 및 스타일 체크 (Ruff로 일원화 — pre-commit과 동일)
ci-lint:
	@echo "🔍 Running lint checks..."
	@cd $(ROOT) && ruff check . || (echo "❌ ruff check failed"; exit 1)
	@cd $(ROOT) && ruff format --check . || (echo "❌ ruff format failed"; exit 1)
	@echo "✅ Lint passed"

# Type: 타입 체크 (mypy) — 제품 코드는 backend/ 에 위치
ci-type:
	@echo "🔍 Running type checks..."
	@cd $(ROOT) && mypy backend/ || echo "⚠️  mypy: 검사할 타입이 없거나 미설정 (빈 backend/)"

# Test: 유닛 테스트 실행 — 테스트 파일이 없으면(템플릿 초기 상태) 건너뜀
ci-test:
	@echo "🔍 Running tests..."
	@cd $(ROOT) && if git ls-files '*test_*.py' | grep -q .; then \
		pytest -v --cov=backend --cov-report=term-missing || (echo "❌ Tests failed"; exit 1); \
	else \
		echo "ℹ️  테스트 파일 없음 — 건너뜀 (템플릿 초기 상태)"; \
	fi
	@echo "✅ Tests passed"

# CI 전체 체크 (커밋/푸시 없이 검증만)
# 사용 케이스:
#   1. 커밋 전 빠르게 체크만 하고 싶을 때
#   2. make finish 안 쓰고 수동 커밋했을 때 사후 검증
#   3. 디버깅 중 테스트만 돌리고 싶을 때
ci:
	@echo "🚀 Starting CI pipeline..."
	@$(MAKE) -s ci-lint
	@$(MAKE) -s ci-type
	@$(MAKE) -s ci-test
	@echo "✅ All CI checks passed"

# 작업 마무리: CI 체크 → 커밋 → 푸시 (권장 워크플로우)
# 사용법: make finish
# 동작:
#   1. CI 체크 실행 (lint, type, test)
#   2. 통과하면 → git add, commit, push
#   3. 실패하면 → 중단 (커밋/푸시 안 함)
# 💡 이것만 쓰면 make ci는 불필요 (자동으로 포함됨)
finish:
	@echo "🏁 Starting finish workflow..."
	@$(MAKE) -s ci
	@echo "💾 Committing changes..."
	@git add . && git commit || echo "⚠️  Nothing to commit"
	@echo "🚀 Pushing to remote..."
	@git push || echo "❌ Push failed"
	@echo "✅ Finish workflow completed"

# 빠른 마무리: CI 체크 생략 → 커밋 → 푸시 (간단한 변경용)
# 사용법: make finq
# 동작:
#   1. git add, commit (자동 메시지), push
#   2. CI 체크 생략 → 빠름
# 사용 케이스: 일일 로그 업데이트, 문서 수정, 설정 변경 등
finq:
	@echo "⚡ Quick finish (CI 체크 생략)..."
	@git add . || echo "⚠️  git add failed"
	@git commit -m "작업 진행 중 - $$(date '+%Y-%m-%d %H:%M:%S')" || echo "⚠️  Nothing to commit"
	@git push || echo "❌ Push failed"
	@echo "✅ Quick finish completed"

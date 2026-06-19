# Makefile for SPECTER (template root)
# 프로젝트별 명령어는 여기에 추가

.DEFAULT_GOAL := help

.PHONY: help

help:
	@echo "프로젝트별 명령어를 여기에 추가하세요"
	@echo ""
	@echo "=== 개발 환경 명령어 (DevContainer) ==="
	@$(MAKE) -C .devcontainer -f Makefile help 2>/dev/null || echo "DevContainer Makefile을 확인하세요"

# DevContainer 명령어는 .devcontainer/Makefile로 전달
# 예: make cc, make cx, make sync repo=...
%:
	@$(MAKE) -C .devcontainer -f Makefile $@

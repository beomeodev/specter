FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Seoul

# 필수 시스템 도구 + Node.js/npm + 공용 에이전트 CLI 설치
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        git-lfs \
        openssh-client \
        gnupg \
        tzdata \
        pipx \
        ripgrep \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && git lfs install \
    && pipx ensurepath --global || true \
    && curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/local/bin sh \
    && rm -rf /var/lib/apt/lists/*

# AI 에이전트 CLI 별칭 설정 (NPX 방식 - 항상 최신 버전 사용)
# Claude Code: Anthropic의 AI 코딩 에이전트
RUN echo '#!/bin/bash\nnpx -y @anthropic-ai/claude-code "$@"' > /usr/local/bin/claude \
    && chmod +x /usr/local/bin/claude

# Codex CLI: OpenAI의 코딩 에이전트
RUN echo '#!/bin/bash\nnpx -y @openai/codex "$@"' > /usr/local/bin/codex \
    && chmod +x /usr/local/bin/codex

# Gemini CLI: Google의 생성형 AI CLI
# 설치 방식: GitHub 레포지토리 직접 참조 (NPX 별칭)
# Docker 샌드박스는 필요시 직접 실행: docker run --rm -it us-docker.pkg.dev/gemini-code-dev/gemini-cli/sandbox:0.1.1
RUN echo '#!/bin/bash\nnpx -y https://github.com/google-gemini/gemini-cli "$@"' > /usr/local/bin/gemini \
    && chmod +x /usr/local/bin/gemini

WORKDIR /workspace

# 개발 도구 선설치(캐시 히트)
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install -r /tmp/requirements-dev.txt

# 런타임 공통 의존성(범용) 설치
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# 비-루트 사용자 (권한 이슈 방지)
ARG USERNAME=dev
ARG UID=1000
ARG GID=1000
RUN groupadd --gid ${GID} ${USERNAME}      && useradd -m --uid ${UID} --gid ${GID} -s /bin/bash ${USERNAME}
ENV PATH="/home/${USERNAME}/.npm-global/bin:/home/${USERNAME}/.local/bin:/root/.local/bin:$PATH"
USER ${USERNAME}

CMD ["bash"]

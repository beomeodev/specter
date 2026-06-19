# ============================================================================
# Stage 1: Python 3.13 Free-Threading Build
# ============================================================================
FROM debian:bookworm AS builder

ARG PY_VER=3.14.0
ARG JOBS=8
ENV DEBIAN_FRONTEND=noninteractive

# Build dependencies for Python compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential wget curl ca-certificates \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
    libffi-dev libgdbm-dev libncursesw5-dev uuid-dev liblzma-dev xz-utils \
    tk-dev git pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Download Python source
WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/${PY_VER}/Python-${PY_VER}.tar.xz && \
    tar xf Python-${PY_VER}.tar.xz

WORKDIR /tmp/Python-${PY_VER}

# Configure and build Python with Free-Threading support
# --disable-gil: Enable Free-Threading (GIL-free execution)
# --enable-optimizations: PGO (Profile-Guided Optimization) for performance
# --with-lto: Link-Time Optimization
RUN ./configure \
      --prefix=/opt/python-${PY_VER}-ft \
      --disable-gil \
      --enable-optimizations \
      --with-lto \
      --with-ensurepip=install && \
    make -j${JOBS} && \
    make install

# ============================================================================
# Stage 2: Runtime Environment
# ============================================================================
FROM debian:bookworm-slim

ARG PY_VER=3.14.0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Seoul \
    PATH=/opt/python-${PY_VER}-ft/bin:$PATH

ENV DEBIAN_FRONTEND=noninteractive

# Runtime dependencies for Python + Development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python runtime libraries
    libbz2-1.0 libreadline8 libsqlite3-0 zlib1g libssl3 libffi8 \
    libgdbm6 libncursesw6 xz-utils liblzma5 tk uuid-runtime ca-certificates \
    # Development tools
    build-essential \
    curl \
    git \
    git-lfs \
    openssh-client \
    gnupg \
    tzdata \
    pipx \
    ripgrep \
    procps && \
    rm -rf /var/lib/apt/lists/*

# Copy Free-Threading Python from builder
COPY --from=builder /opt/python-${PY_VER}-ft /opt/python-${PY_VER}-ft

# Create symlinks for python/pip
RUN ln -sf /opt/python-${PY_VER}-ft/bin/python3 /usr/local/bin/python && \
    ln -sf /opt/python-${PY_VER}-ft/bin/python3 /usr/local/bin/python3 && \
    ln -sf /opt/python-${PY_VER}-ft/bin/pip3 /usr/local/bin/pip

# Verify Free-Threading build
RUN python -VV && \
    python - <<'PY'
import sys, sysconfig
print("=" * 60)
print("Python Free-Threading Build Verification")
print("=" * 60)
print(f"Python version: {sys.version}")
print(f"GIL enabled? -> {getattr(sys, '_is_gil_enabled', lambda: 'N/A')()}")
print(f"EXT_SUFFIX   -> {sysconfig.get_config_var('EXT_SUFFIX')}")
print(f"Py_GIL_DISABLED -> {sysconfig.get_config_var('Py_GIL_DISABLED')}")
print("=" * 60)
PY

# Install Node.js LTS + npm
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Configure npm timeout settings to prevent EIDLETIMEOUT errors
RUN npm config set fetch-timeout 60000 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000

# Setup git-lfs, pipx, uv
RUN git lfs install && \
    pipx ensurepath --global || true && \
    curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/local/bin sh

# GitHub CLI (gh) — official apt repo. Permanent (survives container rebuilds);
# used by /fin, /finq, /ms.merglease for PR + release automation.
RUN mkdir -p -m 755 /etc/apt/keyrings && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list && \
    apt-get update && apt-get install -y --no-install-recommends gh && \
    rm -rf /var/lib/apt/lists/*

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

# Python 의존성 설치 (pyproject.toml + uv)
# 빌드 시점에만 필요하므로 임시 경로에 복사
COPY pyproject.toml /tmp/pyproject.toml
WORKDIR /tmp

# Python 3.13.1 환경 확인 및 가상환경 생성
RUN python --version && \
    uv venv /opt/venv --python=/opt/python-${PY_VER}-ft/bin/python3 && \
    uv pip install --python=/opt/venv/bin/python -r pyproject.toml && \
    uv pip install --python=/opt/venv/bin/python --group dev

# 가상환경을 기본으로 설정
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /workspace

# 비-루트 사용자 (권한 이슈 방지)
ARG USERNAME=dev
ARG UID=1000
ARG GID=1000
RUN groupadd --gid ${GID} ${USERNAME}      && useradd -m --uid ${UID} --gid ${GID} -s /bin/bash ${USERNAME}
ENV PATH="/home/${USERNAME}/.npm-global/bin:/home/${USERNAME}/.local/bin:/root/.local/bin:$PATH"
USER ${USERNAME}

CMD ["bash"]

# =============================================================================
# Waneye Deploy — Docker image for local deployment
# =============================================================================
# Replicates the deploy.yml GitHub Actions workflow in a container.
#
# Build:  make build
# Run:    make deploy
#
# The container:
#   - Clones website-core (via GH_PAT) or uses a mounted copy
#   - Fetches existing images from gh-pages
#   - Generates all site variants (global, cn, au)
#   - Deploys to gh-pages and history branches
#   - Exits when done
#
# Ollama access:
#   On macOS Docker Desktop, host.docker.internal is available by default.
#   The entrypoint sets OLLAMA_HOST=http://host.docker.internal:11434/v1
#   so the container can reach Ollama running on the host.
# =============================================================================

FROM ubuntu:24.04

LABEL maintainer="waneyetechnology" \
      description="Waneye deploy workflow runner"

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# ── System dependencies ──────────────────────────────────────────────────────
# Ubuntu 24.04 ships Python 3.12; add deadsnakes PPA for Python 3.11 to match
# the deploy.yml workflow that uses actions/setup-python with python 3.11.
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    # Python 3.11 (matching deploy.yml)
    python3.11 \
    python3.11-venv \
    python3.11-distutils \
    python3-pip \
    # Git (needed for cloning repos and deploying to gh-pages)
    git \
    # curl (for health checks, e.g. Ollama)
    curl \
    # Playwright system dependencies (matching deploy.yml)
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2t64 \
    libxrandr2 \
    libxss1 \
    # Additional deps often needed by Playwright/Chromium
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxcb-dri3-0 \
    libpango-1.0-0 \
    libcairo2 \
    libcups2 \
    libatspi2.0-0 \
    fonts-liberation \
    xdg-utils \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Make python3.11 the default python/python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# ── Python virtual environment ───────────────────────────────────────────────
# Use a venv to avoid conflicts with the system Python 3.12 setuptools.
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# ── Install Python dependencies ─────────────────────────────────────────────
# Copy requirements first for better Docker layer caching.
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# ── Install Playwright Chromium ──────────────────────────────────────────────
RUN playwright install chromium

# ── Working directory ────────────────────────────────────────────────────────
WORKDIR /workspace

# ── Git configuration (for deploy commits) ───────────────────────────────────
RUN git config --global user.name "docker-deploy[bot]" && \
    git config --global user.email "docker-deploy[bot]@users.noreply.github.com" && \
    git config --global --add safe.directory /workspace && \
    git config --global --add safe.directory /workspace/website

# ── Entrypoint script ───────────────────────────────────────────────────────
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

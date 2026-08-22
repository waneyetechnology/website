# =============================================================================
# Waneye Deploy — Makefile
# =============================================================================
# Usage:
#   make build         Build the Docker image
#   make deploy        Run the full deploy workflow in Docker
#   make deploy-test   Run in test mode (faster, limited data)
#   make deploy-dry    Build only, skip pushing to gh-pages
#   make clean         Remove the Docker image
#   make help          Show available targets
# =============================================================================

# ── Configuration ────────────────────────────────────────────────────────────
IMAGE_NAME   := waneye-deploy
IMAGE_TAG    := latest
FULL_IMAGE   := $(IMAGE_NAME):$(IMAGE_TAG)

# Environment file for API keys and secrets
ENV_FILE     := .env.local

# Path to website-core repo (mounted read-only into the container)
CORE_PATH    ?= $(shell cd .. && pwd)/website-core

# ── Docker run options ───────────────────────────────────────────────────────
# --add-host: Ensure the container can reach the host (for Ollama)
# --rm: Auto-remove the container when it exits
# --env-file: Load API keys from .env.local
DOCKER_RUN_OPTS := \
	--rm \
	--add-host=host.docker.internal:host-gateway \
	--env-file $(ENV_FILE)

# ── Targets ──────────────────────────────────────────────────────────────────

.PHONY: build deploy deploy-test deploy-dry setup-cron clean help

## Build the Docker image
build:
	@echo ""
	@echo "🐳 Building $(FULL_IMAGE)..."
	@echo ""
	docker build -t $(FULL_IMAGE) .

## Run the full deploy workflow (generates + deploys to gh-pages)
deploy: _check-env _check-core
	@echo ""
	@echo "🚀 Running deploy workflow in Docker..."
	@echo ""
	docker run $(DOCKER_RUN_OPTS) \
		-v "$(CORE_PATH):/workspace/website-core:ro" \
		$(FULL_IMAGE)

## Run deploy in test mode (faster, limited data)
deploy-test: _check-env _check-core
	@echo ""
	@echo "🧪 Running deploy workflow in test mode..."
	@echo ""
	docker run $(DOCKER_RUN_OPTS) \
		-e TEST_MODE=true \
		-v "$(CORE_PATH):/workspace/website-core:ro" \
		$(FULL_IMAGE)

## Build only — skip pushing to gh-pages (dry run)
deploy-dry: _check-env _check-core
	@echo ""
	@echo "🔨 Running build-only (no deploy)..."
	@echo ""
	docker run $(DOCKER_RUN_OPTS) \
		-e SKIP_DEPLOY=true \
		-v "$(CORE_PATH):/workspace/website-core:ro" \
		$(FULL_IMAGE)

## Set up an hourly cron job to run deploy
setup-cron:
	@./setup-cron.sh

## Remove the Docker image
clean:
	@echo "🗑  Removing $(FULL_IMAGE)..."
	-docker rmi $(FULL_IMAGE) 2>/dev/null
	@echo "Done."

## Show help
help:
	@echo ""
	@echo "Waneye Deploy — Docker Targets"
	@echo "════════════════════════════════════════════════"
	@echo ""
	@echo "  make build         Build the Docker image"
	@echo "  make deploy        Run the full deploy workflow"
	@echo "  make deploy-test   Run in test mode (faster)"
	@echo "  make deploy-dry    Build only, skip gh-pages push"
	@echo "  make setup-cron    Set up an hourly cron job for deploy"
	@echo "  make clean         Remove the Docker image"
	@echo "  make help          Show this help"
	@echo ""
	@echo "Configuration:"
	@echo "  ENV_FILE    = $(ENV_FILE)"
	@echo "  CORE_PATH   = $(CORE_PATH)"
	@echo "  IMAGE       = $(FULL_IMAGE)"
	@echo ""
	@echo "Environment variables (set in $(ENV_FILE)):"
	@echo "  SKIP_CN=true       Skip Chinese site generation"
	@echo "  SKIP_AU=true       Skip Australian site generation"
	@echo "  SKIP_DEPLOY=true   Skip pushing to gh-pages"
	@echo "  TEST_MODE=true     Use --test-mode for faster builds"
	@echo ""

# ── Internal checks ─────────────────────────────────────────────────────────
_check-env:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "❌ $(ENV_FILE) not found!"; \
		echo "   Create it from the template:"; \
		echo "   cp .env.local.example .env.local"; \
		echo "   Then fill in your API keys."; \
		exit 1; \
	fi

_check-core:
	@if [ ! -d "$(CORE_PATH)" ]; then \
		echo "❌ website-core not found at: $(CORE_PATH)"; \
		echo "   Clone it first:"; \
		echo "   git clone git@github.com:waneyetechnology/website-core.git $(CORE_PATH)"; \
		echo "   Or set CORE_PATH: make deploy CORE_PATH=/path/to/website-core"; \
		exit 1; \
	fi

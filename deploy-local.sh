#!/usr/bin/env bash
# =============================================================================
# deploy-local.sh — Run the Waneye deploy workflow locally
#
# Modes:
#   native (default) — Runs each step directly on macOS
#   act              — Runs the full GitHub Actions workflow in Docker via act
#
# Usage:
#   ./deploy-local.sh                          # native mode, full build
#   ./deploy-local.sh --test-mode              # native mode, fast build
#   ./deploy-local.sh --mode act               # run via act in Docker
#   ./deploy-local.sh --skip-cn --skip-au      # skip regional sites
#   ./deploy-local.sh --deploy                 # actually push to gh-pages
#   ./deploy-local.sh --skip-install           # skip pip/playwright install
#   ./deploy-local.sh --help                   # show help
# =============================================================================
set -euo pipefail

# ─── Colors & helpers ────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

step_num=0

step() {
  step_num=$((step_num + 1))
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BOLD}${CYAN}  Step ${step_num}: $1${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

info()    { echo -e "${CYAN}ℹ ${NC} $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }
warn()    { echo -e "${YELLOW}⚠️ ${NC} $1"; }
error()   { echo -e "${RED}❌${NC} $1"; }

# ─── Defaults ────────────────────────────────────────────────────────────────
MODE="native"
TEST_MODE=""
DO_DEPLOY=false
SKIP_CN=false
SKIP_AU=false
SKIP_INSTALL=false
WEBSITE_CORE_PATH=""
VENV_DIR=".venv-deploy"

# ─── Script directory (always resolve to repo root) ─────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── Parse arguments ────────────────────────────────────────────────────────
usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --mode <native|act>   Run mode (default: native)
  --test-mode           Pass --test-mode to generate_site.py for fast builds
  --deploy              Actually push to gh-pages and history branches
  --skip-cn             Skip Chinese site generation
  --skip-au             Skip Australian site generation
  --skip-install        Skip pip install and Playwright install steps
  --core-path <path>    Path to website-core repo (default: ../website-core)
  -h, --help            Show this help message

Examples:
  $(basename "$0")                          # Full native build
  $(basename "$0") --test-mode              # Quick test build
  $(basename "$0") --mode act               # Run via act in Docker
  $(basename "$0") --skip-cn --skip-au      # English site only
  $(basename "$0") --deploy                 # Build + deploy to gh-pages
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="$2"
      shift 2
      ;;
    --test-mode)
      TEST_MODE="--test-mode"
      shift
      ;;
    --deploy)
      DO_DEPLOY=true
      shift
      ;;
    --skip-cn)
      SKIP_CN=true
      shift
      ;;
    --skip-au)
      SKIP_AU=true
      shift
      ;;
    --skip-install)
      SKIP_INSTALL=true
      shift
      ;;
    --core-path)
      WEBSITE_CORE_PATH="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      error "Unknown option: $1"
      usage
      ;;
  esac
done

# ─── Resolve website-core path ──────────────────────────────────────────────
if [[ -z "$WEBSITE_CORE_PATH" ]]; then
  WEBSITE_CORE_PATH="${SCRIPT_DIR}/../website-core"
fi

# ─── Banner ──────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║      🚀 Waneye Local Deploy — ${MODE} mode               ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Mode:         ${BOLD}${MODE}${NC}"
echo -e "  Test mode:    ${BOLD}${TEST_MODE:-off}${NC}"
echo -e "  Deploy:       ${BOLD}${DO_DEPLOY}${NC}"
echo -e "  Skip CN:      ${BOLD}${SKIP_CN}${NC}"
echo -e "  Skip AU:      ${BOLD}${SKIP_AU}${NC}"
echo -e "  Skip install: ${BOLD}${SKIP_INSTALL}${NC}"
echo -e "  Core path:    ${BOLD}${WEBSITE_CORE_PATH}${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# ACT MODE
# ═══════════════════════════════════════════════════════════════════════════════
run_act_mode() {
  step "Checking Docker"
  if ! docker info &>/dev/null; then
    error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
  fi
  success "Docker is running"

  step "Checking act"
  if ! command -v act &>/dev/null; then
    error "act is not installed. Install with: brew install act"
    exit 1
  fi
  info "act version: $(act --version)"

  step "Loading secrets"
  SECRETS_FILE="${SCRIPT_DIR}/.secrets"
  if [[ ! -f "$SECRETS_FILE" ]]; then
    error "Secrets file not found: ${SECRETS_FILE}"
    echo ""
    info "Create it from the template:"
    echo -e "  ${YELLOW}cp .secrets.example .secrets${NC}"
    echo -e "  ${YELLOW}# Then fill in your API keys${NC}"
    exit 1
  fi
  success "Secrets file found"

  step "Detecting Ollama on host"
  OLLAMA_REACHABLE=false
  if curl -sf --max-time 3 http://localhost:11434/api/version &>/dev/null; then
    OLLAMA_REACHABLE=true
    local ollama_ver
    ollama_ver=$(curl -sf --max-time 3 http://localhost:11434/api/version 2>/dev/null || echo "unknown")
    success "Ollama is running on host (${ollama_ver})"
    info "Container will access it via host.docker.internal:11434"
  else
    warn "Ollama not detected on localhost:11434 — Ollama fallback will be unavailable in the container"
  fi

  step "Running workflow via act"
  local act_args=()
  act_args+=(push)
  act_args+=(-W ".github/workflows/deploy.yml")
  act_args+=(-j "build-deploy")
  act_args+=(--secret-file "$SECRETS_FILE")

  # Use a medium-size image for ubuntu-24.04
  act_args+=(-P "ubuntu-24.04=catthehacker/ubuntu:act-22.04")

  # ── Ollama: map host.docker.internal so the container can reach the host ──
  # On macOS Docker Desktop, host.docker.internal is available by default.
  # We pass OLLAMA_HOST as an env var pointing to the Docker-accessible address.
  if [[ "$OLLAMA_REACHABLE" == true ]]; then
    act_args+=(--env "OLLAMA_HOST=http://host.docker.internal:11434/v1")
    act_args+=(--env "OLLAMA_MODEL=${OLLAMA_MODEL:-}")

    # Add extra_hosts mapping as a safety net (needed on some Docker/Linux setups)
    act_args+=(--container-options "--add-host=host.docker.internal:host-gateway")

    info "OLLAMA_HOST=http://host.docker.internal:11434/v1"
  fi

  info "Running: act ${act_args[*]}"
  echo ""

  act "${act_args[@]}"

  echo ""
  success "Act workflow completed!"
}

# ═══════════════════════════════════════════════════════════════════════════════
# NATIVE MODE
# ═══════════════════════════════════════════════════════════════════════════════
run_native_mode() {
  # ── Cleanup trap ──
  cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
      echo ""
      error "Build failed at step ${step_num} (exit code: ${exit_code})"
      warn "Working directory may contain partial artifacts."
    fi
    # Deactivate venv if active
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
      deactivate 2>/dev/null || true
    fi
  }
  trap cleanup EXIT

  # ── Step: Load environment ──
  step "Loading environment variables"
  ENV_FILE="${SCRIPT_DIR}/.env.local"
  if [[ -f "$ENV_FILE" ]]; then
    info "Loading from ${ENV_FILE}"
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
    success "Environment loaded"
  else
    warn "No .env.local found — expecting API keys in environment"
    info "Create it from the template:"
    echo -e "  ${YELLOW}cp .env.local.example .env.local${NC}"
    echo -e "  ${YELLOW}# Then fill in your API keys${NC}"
  fi

  # ── Step: Validate secrets ──
  step "Validating API keys"
  REQUIRED_KEYS=(
    OPENAI_API_KEY
    NEWSAPI_API_KEY
    FMP_API_KEY
    MARKETAUX_API_KEY
    GNEWS_API_KEY
    DEEPSEEK_API_KEY
    GEMINI_API_KEY
  )
  missing_keys=()
  for key in "${REQUIRED_KEYS[@]}"; do
    if [[ -z "${!key:-}" ]]; then
      missing_keys+=("$key")
    else
      # Show first 8 chars only
      local val="${!key}"
      info "${key} = ${val:0:8}..."
    fi
  done

  if [[ ${#missing_keys[@]} -gt 0 ]]; then
    warn "Missing API keys (site generation may fail for some sources):"
    for key in "${missing_keys[@]}"; do
      echo -e "  ${RED}✗${NC} ${key}"
    done
    echo ""
    read -r -p "Continue anyway? [y/N] " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
      info "Aborted."
      exit 0
    fi
  else
    success "All API keys present"
  fi

  # ── Step: Check website-core ──
  step "Setting up website-core"
  if [[ ! -d "$WEBSITE_CORE_PATH" ]]; then
    error "website-core not found at: ${WEBSITE_CORE_PATH}"
    info "Clone it first:"
    echo -e "  ${YELLOW}git clone git@github.com:waneyetechnology/website-core.git ${WEBSITE_CORE_PATH}${NC}"
    exit 1
  fi
  WEBSITE_CORE_PATH="$(cd "$WEBSITE_CORE_PATH" && pwd)"
  success "Found website-core at: ${WEBSITE_CORE_PATH}"

  # Create symlink in the working directory if not already present
  CORE_LINK="${SCRIPT_DIR}/website-core"
  if [[ -L "$CORE_LINK" ]]; then
    info "Symlink already exists: website-core -> $(readlink "$CORE_LINK")"
  elif [[ -d "$CORE_LINK" ]]; then
    warn "website-core/ directory already exists (not a symlink) — using it as-is"
  else
    ln -s "$WEBSITE_CORE_PATH" "$CORE_LINK"
    success "Created symlink: website-core -> ${WEBSITE_CORE_PATH}"
  fi

  # ── Step: Fetch existing images from gh-pages ──
  step "Fetching existing images from gh-pages"
  if git ls-remote --heads origin gh-pages 2>/dev/null | grep -q gh-pages; then
    info "Fetching gh-pages branch..."
    git fetch origin gh-pages:gh-pages 2>/dev/null || git fetch origin gh-pages 2>/dev/null || true

    if git show gh-pages:static/images/ &>/dev/null; then
      info "Extracting images from gh-pages..."
      mkdir -p website-core/static/images

      # Extract images into a temp location, then move
      git checkout gh-pages -- static/images/ 2>/dev/null || true

      if [[ -d "static/images" ]]; then
        image_count=$(find static/images -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.webp" \) | wc -l | tr -d ' ')
        info "Restored ${image_count} existing images"
        cp -n static/images/* website-core/static/images/ 2>/dev/null || true
        rm -rf static/images
        success "Images restored to website-core/static/images/"
      fi

      # Undo the checkout so working tree is clean
      git checkout HEAD -- static/images/ 2>/dev/null || true
    else
      info "No images directory in gh-pages yet"
    fi
  else
    info "gh-pages branch doesn't exist yet — starting fresh"
  fi

  # ── Step: Python venv ──
  step "Setting up Python virtual environment"
  if [[ ! -d "${SCRIPT_DIR}/${VENV_DIR}" ]]; then
    info "Creating venv at ${VENV_DIR}/"
    python3 -m venv "${SCRIPT_DIR}/${VENV_DIR}"
    success "Virtual environment created"
  else
    info "Using existing venv at ${VENV_DIR}/"
  fi

  # Activate venv
  # shellcheck disable=SC1091
  source "${SCRIPT_DIR}/${VENV_DIR}/bin/activate"
  info "Python: $(python --version) at $(which python)"

  # ── Step: Install dependencies ──
  if [[ "$SKIP_INSTALL" == false ]]; then
    step "Installing Python dependencies"
    pip install -q -r website-core/requirements.txt
    success "Dependencies installed"

    step "Installing Playwright browsers"
    playwright install chromium
    success "Playwright chromium installed"
  else
    step "Skipping dependency installation (--skip-install)"
    info "Using previously installed packages"
  fi

  # ── Step: Generate main site ──
  step "Generating main site (generate_site.py)"
  info "Working directory: website-core/"
  if [[ -n "$TEST_MODE" ]]; then
    info "Test mode enabled — limited data for faster builds"
  fi
  (cd website-core && python generate_site.py $TEST_MODE)
  success "Main site generated"

  # ── Step: Generate Chinese site ──
  if [[ "$SKIP_CN" == false ]]; then
    step "Generating Chinese site (generate_site_cn.py)"
    (cd website-core && python generate_site_cn.py)
    success "Chinese site generated"
  else
    step "Skipping Chinese site generation (--skip-cn)"
  fi

  # ── Step: Generate Australian site ──
  if [[ "$SKIP_AU" == false ]]; then
    step "Generating Australian site (generate_site_au.py)"
    (cd website-core && python generate_site_au.py)
    success "Australian site generated"
  else
    step "Skipping Australian site generation (--skip-au)"
  fi

  # ── Step: Move generated artifacts ──
  step "Moving generated artifacts"

  # When website-core is a symlink, use cp to avoid modifying the source repo.
  # When it's a real directory (e.g. in act mode), use mv for efficiency.
  if [[ -L "${SCRIPT_DIR}/website-core" ]]; then
    COPY_CMD="cp -R"
    info "website-core is a symlink — copying artifacts (source repo preserved)"
  else
    COPY_CMD="mv"
    info "website-core is a directory — moving artifacts"
  fi

  # Clean up previous run artifacts
  rm -rf ./history ./cn ./au ./static ./api

  if [[ -d "website-core/history" ]]; then
    $COPY_CMD website-core/history ./history
    success "Copied history/"
  fi

  if [[ -f "website-core/index.html" ]]; then
    cp website-core/index.html ./index.html
    success "Copied index.html"
  else
    error "index.html not found in website-core — build may have failed"
    exit 1
  fi

  if [[ -d "website-core/cn" ]]; then
    $COPY_CMD website-core/cn ./cn
    success "Copied cn/"
  fi

  if [[ -d "website-core/au" ]]; then
    $COPY_CMD website-core/au ./au
    success "Copied au/"
  fi

  if [[ -d "website-core/static" ]]; then
    $COPY_CMD website-core/static ./static
    success "Copied static/"
  fi

  if [[ -d "website-core/api" ]]; then
    $COPY_CMD website-core/api ./api
    success "Copied api/"
  fi

  # ── Step: Deploy (optional) ──
  if [[ "$DO_DEPLOY" == true ]]; then
    step "Deploying to history branch"
    if [[ -d "./history" ]]; then
      # Use git subtree or manual push to history branch
      info "Pushing history/ to history branch..."
      local TEMP_BRANCH="temp-history-deploy-$$"
      git checkout -b "$TEMP_BRANCH" 2>/dev/null || git checkout "$TEMP_BRANCH"
      git add -f history/
      git commit -m "history: local deploy $(date +%Y%m%d-%H%M%S)" --allow-empty
      git subtree push --prefix=history origin history 2>/dev/null || {
        warn "Subtree push failed — trying alternative method"
        # Alternative: use gh-pages action style
        git push origin "$TEMP_BRANCH":history --force 2>/dev/null || true
      }
      git checkout -
      git branch -D "$TEMP_BRANCH" 2>/dev/null || true
      success "History branch updated"
    else
      info "No history/ directory to deploy"
    fi

    step "Removing history folder before site deploy"
    rm -rf history

    step "Deploying to gh-pages"
    info "Pushing site to gh-pages branch..."

    # Create a temporary orphan branch with just the site content
    local DEPLOY_BRANCH="temp-deploy-$$"
    git checkout --orphan "$DEPLOY_BRANCH"
    git add -A
    git commit -m "deploy: local build $(date +%Y%m%d-%H%M%S)"
    git push origin "$DEPLOY_BRANCH":gh-pages --force
    git checkout -
    git branch -D "$DEPLOY_BRANCH"
    success "Deployed to gh-pages!"
  else
    step "Skipping deploy (use --deploy to push to gh-pages)"
    info "Generated files are in your working directory:"
    echo ""
    [[ -f "./index.html" ]] && echo -e "  ${GREEN}✓${NC} index.html"
    [[ -d "./cn" ]]         && echo -e "  ${GREEN}✓${NC} cn/"
    [[ -d "./au" ]]         && echo -e "  ${GREEN}✓${NC} au/"
    [[ -d "./static" ]]     && echo -e "  ${GREEN}✓${NC} static/"
    [[ -d "./api" ]]        && echo -e "  ${GREEN}✓${NC} api/"
    [[ -d "./history" ]]    && echo -e "  ${GREEN}✓${NC} history/"
    echo ""
    info "To preview: open index.html in your browser"
    info "To preview with a server: python -m http.server 8000"
  fi

  # ── Done ──
  echo ""
  echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BOLD}${GREEN}║               ✅ Build completed successfully!           ║${NC}"
  echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
  echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════
case "$MODE" in
  native)
    run_native_mode
    ;;
  act)
    run_act_mode
    ;;
  *)
    error "Unknown mode: ${MODE}"
    echo -e "  Valid modes: ${BOLD}native${NC}, ${BOLD}act${NC}"
    exit 1
    ;;
esac

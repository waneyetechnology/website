#!/usr/bin/env bash
# =============================================================================
# docker-entrypoint.sh — Runs the Waneye deploy workflow inside the container
#
# This script replicates the deploy.yml GitHub Actions workflow steps:
#   1. Clone/link website-core
#   2. Fetch existing images from gh-pages
#   3. Generate main site (generate_site.py)
#   4. Generate Chinese site (generate_site_cn.py)
#   5. Generate Australian site (generate_site_au.py)
#   6. Move generated artifacts
#   7. Push history branch
#   8. Deploy to gh-pages
#
# Environment variables:
#   GH_PAT            — GitHub Personal Access Token (required for clone & push)
#   OPENAI_API_KEY    — Required for main site generation
#   NEWSAPI_API_KEY   — Required for main site generation
#   FMP_API_KEY       — Required for main site generation
#   MARKETAUX_API_KEY — Required for main site generation
#   GNEWS_API_KEY     — Required for main site generation
#   DEEPSEEK_API_KEY  — Required for site generation
#   GEMINI_API_KEY    — Required for site generation
#   OLLAMA_HOST       — Optional, defaults to http://host.docker.internal:11434/v1
#   OLLAMA_MODEL      — Optional, Ollama model to use
#   SKIP_CN           — Set to "true" to skip Chinese site generation
#   SKIP_AU           — Set to "true" to skip Australian site generation
#   SKIP_DEPLOY       — Set to "true" to skip pushing to gh-pages (build only)
#   TEST_MODE         — Set to "true" to use --test-mode for faster builds
# =============================================================================
set -euo pipefail

# ─── Colors & helpers ────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

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

# ─── Banner ──────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║      🐳 Waneye Docker Deploy                           ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ─── Defaults ────────────────────────────────────────────────────────────────
SKIP_CN="${SKIP_CN:-false}"
SKIP_AU="${SKIP_AU:-false}"
SKIP_DEPLOY="${SKIP_DEPLOY:-false}"
TEST_MODE="${TEST_MODE:-false}"
TEST_MODE_FLAG=""
if [[ "$TEST_MODE" == "true" ]]; then
  TEST_MODE_FLAG="--test-mode"
fi

# ─── Ollama: point to host by default ────────────────────────────────────────
if [[ -z "${OLLAMA_HOST:-}" ]]; then
  export OLLAMA_HOST="http://host.docker.internal:11434/v1"
fi
info "OLLAMA_HOST=${OLLAMA_HOST}"

# Check if Ollama is reachable
OLLAMA_URL="${OLLAMA_HOST%/v1}"  # strip /v1 suffix for the version check
OLLAMA_URL="${OLLAMA_URL%/}"     # strip trailing slash
if curl -sf --max-time 5 "${OLLAMA_URL}/api/version" &>/dev/null; then
  success "Ollama is reachable at ${OLLAMA_HOST}"
else
  warn "Ollama not reachable at ${OLLAMA_HOST} — Ollama fallback will be unavailable"
fi

echo -e "  Skip CN:    ${BOLD}${SKIP_CN}${NC}"
echo -e "  Skip AU:    ${BOLD}${SKIP_AU}${NC}"
echo -e "  Skip Deploy:${BOLD}${SKIP_DEPLOY}${NC}"
echo -e "  Test mode:  ${BOLD}${TEST_MODE}${NC}"
echo ""

# ─── Step: Validate secrets ──────────────────────────────────────────────────
step "Validating environment"

REQUIRED_KEYS=(
  OPENAI_API_KEY
  NEWSAPI_API_KEY
  FMP_API_KEY
  MARKETAUX_API_KEY
  GNEWS_API_KEY
  DEEPSEEK_API_KEY
  GEMINI_API_KEY
  GH_PAT
)
missing_keys=()
for key in "${REQUIRED_KEYS[@]}"; do
  if [[ -z "${!key:-}" ]]; then
    missing_keys+=("$key")
  else
    val="${!key}"
    info "${key} = ${val:0:8}..."
  fi
done

if [[ ${#missing_keys[@]} -gt 0 ]]; then
  error "Missing required environment variables:"
  for key in "${missing_keys[@]}"; do
    echo -e "  ${RED}✗${NC} ${key}"
  done
  echo ""
  error "Ensure all required variables are set in your .env.local file."
  exit 1
fi
success "All required environment variables present"

# ─── Step: Set up website-core (writable copy) ──────────────────────────────
step "Setting up website-core"

CORE_SRC="/workspace/website-core"
CORE_WORK="/workspace/_website-core-work"

if [[ -d "$CORE_SRC" ]]; then
  info "website-core mounted at ${CORE_SRC} — creating writable copy..."
  cp -R "$CORE_SRC" "$CORE_WORK"
  success "Writable copy created at ${CORE_WORK}"
else
  info "Cloning website-core from GitHub..."
  git clone --depth 1 "https://${GH_PAT}@github.com/waneyetechnology/website-core.git" "$CORE_WORK"
  success "website-core cloned"
fi

# ─── Step: Set up the website repo ──────────────────────────────────────────
step "Setting up website repo"

info "Cloning website repo for deploy context..."
git clone --depth 1 "https://${GH_PAT}@github.com/waneyetechnology/website.git" /workspace/website
cd /workspace/website

# Link the writable website-core copy
ln -s "$CORE_WORK" website-core
info "Linked website-core into website directory"

# ─── Step: Fetch existing images from gh-pages ──────────────────────────────
step "Fetching existing images from gh-pages"

if git ls-remote --heads origin gh-pages 2>/dev/null | grep -q gh-pages; then
  info "Fetching gh-pages branch..."
  git fetch origin gh-pages:gh-pages 2>/dev/null || git fetch origin gh-pages 2>/dev/null || true

  if git show gh-pages:static/images/ &>/dev/null; then
    info "Extracting images from gh-pages..."
    mkdir -p website-core/static/images

    git checkout gh-pages -- static/images/ 2>/dev/null || true

    if [[ -d "static/images" ]]; then
      image_count=$(find static/images -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.webp" \) | wc -l | tr -d ' ')
      info "Restored ${image_count} existing images"
      cp -n static/images/* website-core/static/images/ 2>/dev/null || true
      rm -rf static/images
      success "Images restored to website-core/static/images/"
    fi
  else
    info "No images directory in gh-pages yet"
  fi
else
  info "gh-pages branch doesn't exist yet — starting fresh"
fi

# ─── Step: Generate main site ────────────────────────────────────────────────
step "Generating main site (generate_site.py)"

cd website-core
python generate_site.py $TEST_MODE_FLAG
cd ..
success "Main site generated"

# ─── Step: Generate Chinese site ─────────────────────────────────────────────
if [[ "$SKIP_CN" != "true" ]]; then
  step "Generating Chinese site (generate_site_cn.py)"
  cd website-core
  python generate_site_cn.py $TEST_MODE_FLAG
  cd ..
  success "Chinese site generated"
else
  step "Skipping Chinese site generation (SKIP_CN=true)"
fi

# ─── Step: Generate Australian site ─────────────────────────────────────────
if [[ "$SKIP_AU" != "true" ]]; then
  step "Generating Australian site (generate_site_au.py)"
  cd website-core
  python generate_site_au.py $TEST_MODE_FLAG
  cd ..
  success "Australian site generated"
else
  step "Skipping Australian site generation (SKIP_AU=true)"
fi

# ─── Step: Move generated artifacts ─────────────────────────────────────────
step "Moving generated artifacts"

mv website-core/history ./history 2>/dev/null || true
mv website-core/index.html ./
mv website-core/cn ./cn 2>/dev/null || true
mv website-core/au ./au 2>/dev/null || true
rm -rf ./static
mv website-core/static ./static
rm -rf ./api
mv website-core/api ./api 2>/dev/null || true

success "Artifacts moved"

# Show what was generated
echo ""
[[ -f "./index.html" ]] && echo -e "  ${GREEN}✓${NC} index.html"
[[ -d "./cn" ]]         && echo -e "  ${GREEN}✓${NC} cn/"
[[ -d "./au" ]]         && echo -e "  ${GREEN}✓${NC} au/"
[[ -d "./static" ]]     && echo -e "  ${GREEN}✓${NC} static/"
[[ -d "./api" ]]        && echo -e "  ${GREEN}✓${NC} api/"
[[ -d "./history" ]]    && echo -e "  ${GREEN}✓${NC} history/"
echo ""

# ─── Step: Deploy ────────────────────────────────────────────────────────────
if [[ "$SKIP_DEPLOY" == "true" ]]; then
  step "Skipping deploy (SKIP_DEPLOY=true)"
  info "Build completed — generated files are in the container."
  info "To extract: docker cp <container>:/workspace/website/ ."
else
  # Configure git for pushing
  git remote set-url origin "https://${GH_PAT}@github.com/waneyetechnology/website.git" 2>/dev/null || true

  # ── Deploy history branch ──
  step "Deploying to history branch"
  if [[ -d "./history" ]]; then
    info "Pushing history/ to history branch..."

    # Create a temporary directory for the history deploy
    HISTORY_TMP=$(mktemp -d)
    cp -R ./history/* "$HISTORY_TMP/" 2>/dev/null || true

    # Simple approach: initialize a new repo in the temp dir and fetch history
    cd "$HISTORY_TMP"
    git init
    git config user.name "docker-deploy[bot]"
    git config user.email "docker-deploy[bot]@users.noreply.github.com"
    git remote add origin "https://${GH_PAT}@github.com/waneyetechnology/website.git"

    # Try to fetch existing history branch to keep files
    git fetch origin history 2>/dev/null && git checkout -b history origin/history 2>/dev/null || git checkout -b history

    # Copy new history files
    cp -R /workspace/website/history/* . 2>/dev/null || true
    git add -A
    git commit -m "history: docker deploy $(date +%Y%m%d-%H%M%S)" --allow-empty
    git push origin history --force
    cd /workspace/website
    rm -rf "$HISTORY_TMP"

    success "History branch updated"
  else
    info "No history/ directory to deploy"
  fi

  # Remove history before gh-pages deploy
  step "Removing history folder before site deploy"
  rm -rf history

  # ── Deploy to gh-pages ──
  step "Deploying to gh-pages"
  info "Pushing site to gh-pages branch..."

  # Use a clean temporary directory for gh-pages deploy
  DEPLOY_TMP=$(mktemp -d)
  # Copy all site files (excluding .git and website-core)
  for item in index.html cn au static api robots.txt sitemap.xml structured-data.json CNAME _config.yml LICENSE; do
    if [[ -e "$item" ]]; then
      cp -R "$item" "$DEPLOY_TMP/"
    fi
  done

  cd "$DEPLOY_TMP"
  git init
  git config user.name "docker-deploy[bot]"
  git config user.email "docker-deploy[bot]@users.noreply.github.com"
  git remote add origin "https://${GH_PAT}@github.com/waneyetechnology/website.git"
  git checkout -b gh-pages
  git add -A
  git commit -m "deploy: docker build $(date +%Y%m%d-%H%M%S)"
  git push origin gh-pages --force
  cd /workspace/website
  rm -rf "$DEPLOY_TMP"

  success "Deployed to gh-pages!"
fi

# ─── Done ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║          ✅ Docker deploy completed successfully!       ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

#!/usr/bin/env bash
# =============================================================================
# setup-cron.sh — Set up an hourly cron job to run the Docker deploy
# =============================================================================
set -euo pipefail

# ─── Colors & helpers ────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─── Configuration ────────────────────────────────────────────────────────────
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${REPO_DIR}/deploy-cron.log"
CRON_SCHEDULE="0 * * * *"
MARKER="WANEYE_DOCKER_DEPLOY_CRON"

# Add common bin paths to ensure docker and make are found in cron's limited PATH
CRON_CMD="PATH=/usr/local/bin:/opt/homebrew/bin:\$PATH cd ${REPO_DIR} && make deploy >> ${LOG_FILE} 2>&1 # ${MARKER}"

echo -e "${CYAN}Setting up hourly cron job for Waneye deploy...${NC}"

# Check if crontab is available
if ! command -v crontab &> /dev/null; then
    echo -e "${RED}❌ crontab command not found. Cron may not be supported on this system.${NC}"
    exit 1
fi

TMP_CRON=$(mktemp)
trap 'rm -f "$TMP_CRON"' EXIT

# Export current crontab, excluding any previous version of our job
crontab -l 2>/dev/null | grep -v "${MARKER}" > "$TMP_CRON" || true

# Add the new cron job
echo "${CRON_SCHEDULE} ${CRON_CMD}" >> "$TMP_CRON"

# Install the new crontab
crontab "$TMP_CRON"

echo -e "${GREEN}✅ Cron job installed successfully!${NC}"
echo -e "It will run hourly at the top of the hour (0 * * * *)."
echo -e "Log file: ${LOG_FILE}"
echo ""
echo -e "To view your crontab, run: ${CYAN}crontab -l${NC}"
echo -e "To remove this job later, edit your crontab manually: ${CYAN}crontab -e${NC}"

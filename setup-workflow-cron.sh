#!/usr/bin/env bash
# Install an hourly GitHub Actions dispatch in the current user's crontab.
set -euo pipefail

MARKER='# WANEYE_WORKFLOW_DEPLOY_CRON'
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${REPO_DIR}/workflow-deploy-cron.log"

for tool in gh crontab; do
    command -v "$tool" >/dev/null || { echo "Required command not found: $tool" >&2; exit 1; }
done
GH_BIN="$(command -v gh)"
# Cron cannot inherit a token exported in this terminal. Verify saved credentials.
env -u GH_TOKEN -u GITHUB_TOKEN "$GH_BIN" auth status --hostname github.com >/dev/null

# Quote for cron's /bin/sh, including paths containing spaces or single quotes.
quote() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }
CRON_CMD="$(quote "$GH_BIN") workflow run deploy.yml --repo waneyetechnology/website --ref master >> $(quote "$LOG_FILE") 2>&1"
# Cron treats percent signs specially, even inside shell quotes.
CRON_CMD="${CRON_CMD//%/\\%}"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
if ! LC_ALL=C crontab -l > "$TMP_DIR/current" 2> "$TMP_DIR/error"; then
    if ! grep -q 'no crontab for' "$TMP_DIR/error"; then
        cat "$TMP_DIR/error" >&2
        exit 1
    fi
    : > "$TMP_DIR/current"
fi
awk -v marker="$MARKER" 'index($0, marker) == 0' "$TMP_DIR/current" > "$TMP_DIR/new"
printf '0 * * * * %s %s\n' "$CRON_CMD" "$MARKER" >> "$TMP_DIR/new"
crontab "$TMP_DIR/new"

printf 'Installed hourly dispatch of .github/workflows/deploy.yml on master.\nLog: %s\n' "$LOG_FILE"
printf 'Inspect with crontab -l; remove the %s line with crontab -e.\n' "$MARKER"
printf 'Note: deploy.yml also has a GitHub hourly schedule; both schedules can trigger deployments.\n'

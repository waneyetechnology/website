#!/usr/bin/env bash
# Bound the complete workflow, including child processes and shutdown.
set -euo pipefail

deadline="${DEPLOY_TIMEOUT_SECONDS:-3000}"
if [[ ! "$deadline" =~ ^[1-9][0-9]*$ ]]; then
  echo "DEPLOY_TIMEOUT_SECONDS must be a positive integer" >&2
  exit 2
fi

if [[ $# -eq 0 ]]; then
  set -- /usr/local/bin/docker-entrypoint.sh
fi

echo "Deployment deadline: ${deadline}s (10s termination grace period)"
# Without --foreground, timeout manages a process group for the workflow.
# Exit 124 reports a deadline; 137 reports escalation to SIGKILL.
exec timeout --verbose --signal=TERM --kill-after=10s "${deadline}s" "$@"

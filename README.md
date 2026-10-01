# Waneye Technology

**Waneye — global vision for smarter finance**

Waneye is a real-time financial news aggregation and market analysis platform. We provide real-time financial dashboard experiences, offering news, market data, and economic indicators.

## About

Visit our website at [www.waneye.com](https://www.waneye.com).

## Hourly GitHub Actions deployment

To dispatch `.github/workflows/deploy.yml` on `master` from a host's cron,
install GitHub CLI (`gh`) and cron, then run as the user who will own the job:

```sh
gh auth login --hostname github.com
./setup-workflow-cron.sh
```

The GitHub account needs permission to run Actions in `waneyetechnology/website`.
Use saved CLI credentials available without an interactive prompt; tokens exported
only in your terminal are not inherited by cron. The host must stay running with
its cron service enabled and network access to GitHub.

The script installs `0 * * * *` (the top of every hour in the host's timezone),
uses the absolute path to `gh`, and logs dispatch output/errors to
`workflow-deploy-cron.log` beside the script. Deployment results are available in
GitHub Actions. Rerunning replaces its own entry and preserves other cron jobs.
Inspect with `crontab -l`; remove the `WANEYE_WORKFLOW_DEPLOY_CRON` line using
`crontab -e` to uninstall.

Host cron provides the hourly schedule; the workflow also supports manual
dispatch and runs on pushes to `master`. The existing `setup-cron.sh` instead
runs `make deploy` locally through Docker.

`make deploy` clones the latest default branch of `website-core` from GitHub on
each run, using `GH_PAT` from `.env.local`. `make deploy-test` and `make deploy-dry`
use the local `../website-core` checkout instead (override with `CORE_PATH`).

Rebuild with `make build` to install Codex alongside AGY. Deploy targets mount
these host credential files directly into Docker, writable for token refresh:

- `$CODEX_HOME/auth.json` (default `~/.codex/auth.json`)
- `~/.gemini/antigravity-cli/antigravity-oauth-token`

Both files must exist; Docker fails immediately if either is missing. A login
stored only in macOS Keychain must first be exported to its corresponding file
from the logged-in session. Keep credential files private (`chmod 600`). Cron
then reads the files directly and does not need Keychain access or host Python.
Run cron as the user who owns these credentials. Only the credential files are
mounted so Codex's Linux installation inside the image remains available.

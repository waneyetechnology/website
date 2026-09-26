# Waneye Technology

**Waneye — global vision for smarter finance**

Waneye is a real-time financial news aggregation and market analysis platform. We provide real-time financial dashboard experiences, offering news, market data, and economic indicators.

## About

Visit our website at [www.waneye.com](https://www.waneye.com).

`make deploy` clones the latest default branch of `website-core` from GitHub on
each run, using `GH_PAT` from `.env.local`. `make deploy-test` and `make deploy-dry`
use the local `../website-core` checkout instead (override with `CORE_PATH`).

Rebuild with `make build` to install Codex alongside AGY. Deploy targets use
host Python 3 to pass the current user's saved CLI credentials into Docker:
Codex's `$CODEX_HOME/auth.json` (default `~/.codex/auth.json`) and AGY's
`~/.gemini/antigravity-cli/antigravity-oauth-token`. On macOS, the launcher also
reads AGY's existing Keychain login, or Codex's Keychain login when no auth file
exists. Keychain credentials are temporarily exported with owner-only access,
refreshed credentials are saved back, and temporary files are removed on exit.
Only the credential files are mounted; they are writable to allow token refresh.

Run cron as the same user who logged into the CLIs; macOS Keychain must be
unlocked. Linux hosts using a desktop keyring must use file-backed CLI credentials
for this launcher. No new login is needed when these saved credentials are valid.
Authentication does not change the models available to the account.

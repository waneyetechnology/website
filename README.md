# Waneye Technology

**Waneye — global vision for smarter finance**

Waneye is a real-time financial news aggregation and market analysis platform. We provide real-time financial dashboard experiences, offering news, market data, and economic indicators.

## About

Visit our website at [www.waneye.com](https://www.waneye.com).

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

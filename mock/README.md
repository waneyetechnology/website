# Waneye website mock

A standalone, responsive, multi-page front-end concept for Waneye's market-intelligence website. Open `index.html` directly or serve this directory with any static server.

```sh
cd mock
python3 -m http.server 4173
```

The mock treats the supplied Global, Australian, and Chinese analysis, headlines, market data, and headline imagery as its editorial inputs. `content.js` holds one deduplicated content bundle, `images/` packages every headline image for reliable review, and `data.js` prepares the inputs for presentation while preserving the editorial values.

## Page map

- `index.html` — main intelligence dashboard
- `markets/index.html` — integrated market snapshot, macro context, and sector views
- `markets/sector.html` — sector trend, investment implication, and linked supporting reporting
- `newsroom/index.html` — complete visual regional source ledger
- `newsroom/article.html` — headline imagery, original publisher link, and connected sector context
- `archive/index.html` — current regional research overview
- `archive/report.html` — complete connected intelligence report

No build step or third-party JavaScript dependency is required. Google Fonts gracefully fall back to system sans-serif fonts when offline.

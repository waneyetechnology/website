# Waneye website mock

A standalone, responsive, multi-page front-end concept for Waneye's market-intelligence website. Open `index.html` directly or serve this directory with any static server.

```sh
cd mock
python3 -m http.server 4173
```

The displayed editorial and market values are copied from the regional folders on `origin/gh-pages`: `api/v1/global`, `api/v1/au`, and `api/v1/cn`. The nine JSON snapshots under `mock/api/v1/` are exact copies; `api-snapshot.js` packages the same objects so the mock also works when opened directly with `file://`. The presentation adapter reshapes fields for the UI but does not translate or rewrite their values.

## Page map

- `index.html` — main intelligence dashboard
- `markets/index.html` — regional sector records and complete `data.json` values
- `markets/sector.html` — one verbatim sector record, driven by region and sector parameters
- `newsroom/index.html` — complete regional `headlines.json` ledger
- `newsroom/article.html` — one complete headline record
- `archive/index.html` — current regional API report directory
- `archive/report.html` — complete structured `analysis.json` presentation

No build step or third-party JavaScript dependency is required. Google Fonts gracefully fall back to system sans-serif fonts when offline.

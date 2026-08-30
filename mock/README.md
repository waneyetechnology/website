# Waneye website mock

A standalone, responsive, multi-page front-end concept for Waneye's market-intelligence website. Open `index.html` directly or serve this directory with any static server.

```sh
cd mock
python3 -m http.server 4173
```

The content model and editorial copy are derived from Global, Australian, and Greater China reports preserved on the repository's `origin/history` branch. The archive also reflects the August 30, 2026 branch tip. The mock includes regional report switching, sentiment and source metadata, daily highlights, sector analysis, an interactive risk matrix, strategic positioning, market outlook, source links, search, and responsive navigation.

## Page map

- `index.html` — main intelligence dashboard
- `markets/index.html` — sector directory
- `markets/sector.html` — nested sector analysis, driven by region and sector parameters
- `newsroom/index.html` — curated source newsroom
- `newsroom/article.html` — nested source-context page
- `archive/index.html` — timestamped report archive
- `archive/report.html` — nested full report presentation

No build step or third-party JavaScript dependency is required. Google Fonts gracefully fall back to system sans-serif fonts when offline.

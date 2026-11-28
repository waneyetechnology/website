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

## Implementation

- `style.css` is the single stylesheet, with dark and light design tokens and responsive layouts.
- `app.js` supplies shared chrome, localization, evidence cards, search and publisher filters.
- `pages.js` composes the seven routes and their report, risk, positioning and macro interactions.
- `charts.js` renders responsive canvas charts, normalized comparisons and pointer/keyboard crosshairs.
- `data.js` preserves the supplied regional data and attaches deterministic illustrative paths for four timeframes. AU/CN paths end at their exact supplied prices. Global benchmark values are illustrative, explicitly labeled, and are not historical observations. Seeded Brownian bridges use distinct index paths, small opening gaps and exact closing anchors. Hover telemetry shows level and return versus open; activity bars are illustrative, not reported volume.

The default is dark; the theme toggle persists when browser storage is available. Search opens with Cmd/Ctrl+K or `/`. Ticker pills prefill the same search. The source ledger retains all 85 Global, 74 Australian and 152 Chinese stories.

Validation covered all seven routes in all three editions over `file://` and HTTP, all 21 mobile route/edition combinations, chart controls, risk and positioning filters, search, publisher filters, view switching, FX sorting, mobile navigation and theme persistence. No runtime JS errors were observed. All supplied image paths resolve; `content.js` and `images/` are unchanged.

## Iteration 2 verification

The homepage defaults to a nine-story Wire ledger with eager thumbnails. ISO dates are formatted in UTC; other supplied date labels pass through unchanged. Charts use seeded bridges, return-ranked hover telemetry, illustrative activity bars, comparison return labels, and range markers. Macro strips, sector highlighting, concise theme filters, ranked rates, FX spreads (JPY: 0.01 pip unit; others: 0.0001), and the cross-regional research matrix use the supplied snapshots.

Browser verification covered 168 combinations: seven routes × three regions × two widths (1440/390) × two themes × HTTP/file. No console errors, broken images, or document horizontal overflow were found. Interactions checked include comparison, timeframe and legend controls, theme filters, outlook toggles, Cards/Wire, and spread sorting. All 311 headlines and exact AU/CN snapshots remain intact; all JavaScript syntax checks pass. Non-data HTML/CSS/JS totals 1,405 lines.

Protected `content.js` SHA-256: `ea67b2e600729ca99121623b1b301e117f1021a4e7110a7a2bb4d75bc8b2b654`. The protected image directory is unchanged.

## Final precision pass

Compare telemetry uses interpolated calendar dates and a single timestamp, with 40% lower multi-day synthetic drift and volatility. Return pills have 19px center spacing; nearby axis labels are suppressed. Search indexes sector implications independently of clean titles, category badges, ticker pills and snippets. Theme labels retain whole words; JPY quotes use two decimals and other FX quotes four. Zero policy rates have no visible bar, and matrix sentiment scores share a right-aligned bar container.

Final browser checks covered 84 file-based combinations (seven routes × three editions × 1440/390px × two themes), including expanded evidence images: zero console errors, broken images or document overflow. Desktop command-card bottom edges match exactly across editions. Targeted checks cover Compare telemetry, search categories, FX precision and zero-rate bars. All JavaScript syntax checks pass; the protected content hash matches HEAD and images are unchanged. Temporary review artifacts were removed.

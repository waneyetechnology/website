// Presentation adapter for the supplied regional analysis, market and headline inputs.
(function () {
  const input = window.WANEYE_INPUT;
  const editions = { global: "Global edition", au: "Australia edition", cn: "大中华区版" };
  const localRoot = typeof document !== "undefined" ? new URL(".", document.currentScript.src) : null;

  function headlineImage(value) {
    const clean = value.replace(/^\.\.\//, "").split("#")[0];
    if (localRoot) return new URL(clean.replace("static/", ""), localRoot).href;
    return `https://www.waneye.com/${clean}`;
  }

  function report(region) {
    const payload = input[region];
    const analysis = payload.analysis.analysis;
    const summary = analysis.executive_summary;
    const insights = analysis.market_insights;
    const recommendations = analysis.strategic_recommendations;
    const headlines = payload.headlines.headlines;
    return {
      region,
      edition: editions[region],
      date: analysis.analysis_date,
      time: analysis.analysis_time,
      updatedAt: payload.analysis.updated_at,
      score: summary.market_sentiment_score,
      sentiment: summary.overall_sentiment,
      sources: headlines.length,
      sourceIndexes: summary.headline_sources,
      themes: insights.key_themes,
      highlights: summary.key_highlights,
      sectors: insights.sectors.map((item) => ({
        name: item.sector,
        trend: item.trend,
        implication: item.implications,
        sourceIndexes: item.headline_sources,
      })),
      risks: analysis.risk_assessment.map((item) => ({
        name: item.risk_factor,
        impact: item.impact,
        likelihood: item.likelihood,
        mitigation: item.mitigation,
        sourceIndexes: item.headline_sources,
      })),
      opportunities: recommendations.opportunities.map((item) => ({
        title: item.recommendation,
        rationale: item.rationale,
        tickers: item.tickers,
        horizon: item.timeframe,
        sourceIndexes: item.headline_sources,
      })),
      defensive: recommendations.defensive_moves.map((item) => ({
        title: item.recommendation,
        rationale: item.rationale,
        tickers: item.tickers,
        horizon: item.timeframe,
        sourceIndexes: item.headline_sources,
      })),
      short: analysis.market_outlook.short_term,
      long: analysis.market_outlook.long_term,
      catalysts: analysis.market_outlook.key_catalysts,
      watchList: analysis.market_outlook.watch_list,
      news: headlines.map((item, index) => ({
        index: index + 1,
        title: item.headline,
        url: item.url,
        publishedAt: item.publishedAt,
        source: item.source,
        meta: [item.source, item.publishedAt].filter(Boolean).join(" · "),
        favicon: item.favicon,
        image: item.image,
        imageUrl: headlineImage(item.image),
      })),
      marketData: payload.data,
    };
  }

  window.WANEYE_REPORTS = { global: report("global"), au: report("au"), cn: report("cn") };
})();

// Synthetic paths are presentation data, never historical market observations.
(function () {
  const benchmarks = [
    ["SPX", "S&P 500", 6482.4, -42.6],
    ["DJI", "Dow Jones", 45620.8, -218.3],
    ["IXIC", "NASDAQ", 21430.6, -198.4],
    ["FTSE", "FTSE 100", 9280.2, -31.8],
    ["N225", "Nikkei 225", 42810.5, -305.2],
    ["GDAXI", "DAX", 24120.7, -142.1],
    ["VIX", "VIX", 18.62, 1.34],
  ];
  const number = (value) => Number(String(value).replace(/,/g, ""));
  for (const r of Object.values(window.WANEYE_REPORTS)) {
    r.indices = (
      r.marketData.indices ||
      benchmarks.map(([symbol, name, price, change]) => ({
        symbol,
        name,
        price: price.toLocaleString("en-US", { minimumFractionDigits: 2 }),
        change: `${change > 0 ? "+" : ""}${change.toFixed(2)}`,
        change_pct: `${change > 0 ? "+" : ""}${((change / (price - change)) * 100).toFixed(2)}%`,
        direction: change > 0 ? "up" : "down",
        numeric_change_pct: (change / (price - change)) * 100,
      }))
    ).map((item, seed) => {
      const price = number(item.price),
        previous = price - number(item.change),
        series = {};
      for (const [frame, days] of Object.entries({ "1D": 1, "5D": 5, "1M": 22, "3M": 66 })) {
        let state = [...item.symbol + frame].reduce((h, c) => Math.imul(h ^ c.charCodeAt(0), 16777619), 2166136261) >>> 0;
        const random = () => ((state = (Math.imul(state, 1664525) + 1013904223) >>> 0) + 1) / 4294967297;
        const normal = () => Math.sqrt(-2 * Math.log(random())) * Math.cos(2 * Math.PI * random());
        const start = previous * (1 + normal() * (days === 1 ? 0.0012 : 0.0048 * Math.sqrt(days)));
        const walk = [0], volatility = (0.00045 + seed % 4 * 0.00019) * Math.sqrt(days) * (days === 1 ? 1 : 0.6);
        for (let i = 1; i < 96; i++) walk.push(walk[i - 1] + normal() * volatility * (i < 14 || i > 80 ? 1.35 : 0.85));
        series[frame] = walk.map((v, i) => start + (price - start) * i / 95 + price * (v - walk[95] * i / 95));
        series[frame][95] = price;
      }
      return { ...item, value: price, previous, series };
    });
    const symbols =
      r.region === "au"
        ? ["^AXJO", "^AXMJ", "^AXFJ", "^AXEJ"]
        : r.region === "cn"
          ? ["000001.SS", "000300.SS", "399006.SZ", "^HSI"]
          : ["DJI", "SPX", "IXIC", "FTSE"];
    r.compare = symbols.map((s) => r.indices.find((i) => i.symbol === s));
  }
})();

// Presentation adapter only. All displayed editorial and market values remain
// byte-for-byte values from the matching origin/gh-pages api/v1 payload.
(function () {
  const api = window.WANEYE_API;
  const editions = {global:"Global edition", au:"Australia edition", cn:"大中华区版"};

  function report(region) {
    const payload = api[region];
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
      sectors: insights.sectors.map(item => ({
        name: item.sector,
        trend: item.trend,
        implication: item.implications,
        sourceIndexes: item.headline_sources,
        tone: "flat"
      })),
      risks: analysis.risk_assessment.map((item,index) => ({
        name: item.risk_factor,
        impact: item.impact,
        likelihood: item.likelihood,
        mitigation: item.mitigation,
        sourceIndexes: item.headline_sources,
        x: 24 + ((index * 19) % 62),
        y: 18 + ((index * 23) % 65)
      })),
      opportunities: recommendations.opportunities.map(item => ({
        title: item.recommendation,
        rationale: item.rationale,
        tickers: item.tickers,
        horizon: item.timeframe,
        sourceIndexes: item.headline_sources
      })),
      defensive: recommendations.defensive_moves.map(item => ({
        title: item.recommendation,
        rationale: item.rationale,
        tickers: item.tickers,
        horizon: item.timeframe,
        sourceIndexes: item.headline_sources
      })),
      short: analysis.market_outlook.short_term,
      long: analysis.market_outlook.long_term,
      catalysts: analysis.market_outlook.key_catalysts,
      watchList: analysis.market_outlook.watch_list,
      news: headlines.map((item,index) => ({index:index+1,title:item.headline,url:item.url,publishedAt:item.publishedAt,source:item.source,favicon:item.favicon,image:item.image})),
      marketData: payload.data
    };
  }

  window.WANEYE_REPORTS = {global:report("global"),au:report("au"),cn:report("cn")};
})();

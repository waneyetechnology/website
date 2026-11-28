function themeLabel(text) {
  const label = text.split(/[:：—]/)[0].trim();
  if (label.length <= 30) return label;
  const words = [...label.matchAll(/\S+/gu)].filter(m => m.index + m[0].length <= 30);
  return (words.length ? label.slice(0, words.at(-1).index + words.at(-1)[0].length) : label) + (words.length ? "…" : "");
}
/* Route composition; shared components are reused by the connected report. */
(() => {
  const {
    $,
    $$,
    r,
    reports,
    region,
    zh,
    page,
    t,
    esc,
    colors,
    href,
    heading,
    btn,
    delta,
    spark,
    story,
    evidence,
    sectorCards,
    pulse,
    chart,
    wire,
  } = W;
  const main = $("#main"),
    level = (s) => (/high|高/i.test(s) ? 2 : /low|低/i.test(s) ? 0 : 1);
  const levelName = (n) => (zh ? ["低", "中", "高"] : ["Low", "Med", "High"])[n];
  const title = (text, extra = "") =>
    `<div class="page-title"><h1>${text}</h1><span>${extra || `${zh ? "2026年8月30日" : r.date} · ${W.reportTime(r)}`}</span></div>`;
  const section = (id, name, body) => `<section id="${id}">${heading(name)}${body}</section>`;
  function attribution() {
    const total = r.sectors.reduce((n, s) => n + s.sourceIndexes.length, 0);
    return `<section class="panel attribution">${heading(t("Signal attribution", "信号归因"), `<small>${t("Share of sector citations", "板块引用占比")} · ${total}</small>`)}<div class="stacked">${r.sectors.map((s, i) => `<a href="#sector-${i}" style="flex:${s.sourceIndexes.length};background:${colors[i % 7]}" title="${esc(s.name)}: ${Math.round(s.sourceIndexes.length / total * 100)}% · ${s.sourceIndexes.length}"><span>${s.sourceIndexes.length / total >= .05 ? Math.round(s.sourceIndexes.length / total * 100) + "%" : ""}</span></a>`).join("")}</div><div class="chips">${r.sectors.map((s, i) => `<a class="legend" style="--series:${colors[i % 7]}" href="#sector-${i}"><i></i>${esc(s.name)} <b class="mono">${s.sourceIndexes.length}</b> <small>${Math.round(s.sourceIndexes.length / total * 100)}%</small></a>`).join("")}</div></section>`;
  }
  function briefs() {
    return `<div class="chips themes">${btn(t("All themes", "全部主题"), 'data-theme-filter="-1"', true)}${r.themes.map((s, i) => btn(esc(themeLabel(s)), `title="${esc(s)}" data-theme-filter="${i}"`)).join("")}</div><small id="briefCount" role="status"></small><div class="brief-grid" id="briefGrid"></div><small class="muted">${t("Theme filter matches keywords in the executive briefs.", "主题筛选按核心摘要中的关键词匹配。")}</small>`;
  }
  function bindBriefs() {
    const grid = $("#briefGrid");
    if (!grid) return;
    const render = (index) => {
      const theme = r.themes[index] || "",
        words = theme.toLowerCase().match(zh ? /[\u4e00-\u9fff]{2}|[a-z]{2,}/g : /[a-z]{3,}/g) || [];
      const stop = new Set(["the", "and", "from", "with", "risk", "market", "amid"]);
      const list = r.highlights
        .slice(1)
        .map((text, i) => ({ text, i }))
        .filter((x) => index < 0 || words.some((w) => !stop.has(w) && x.text.toLowerCase().includes(w)));
      $("#briefCount").textContent = index < 0 ? "" : `${list.length} ${t("matching briefs", "条匹配摘要")}`;
      grid.innerHTML =
        list
          .map(
            ({ text, i }) =>
              `<article class="brief-row"><span class="mono">${String(i + 2).padStart(2, "0")}</span><p>${esc(text)}</p></article>`,
          )
          .join("") ||
        `<p class="muted">${t("No executive briefs match this theme. See the complete sector analysis below.", "暂无匹配摘要，请查看下方完整板块分析。")}</p>`;
    };
    $$("[data-theme-filter]").forEach(
      (b) =>
        (b.onclick = () => {
          $$("[data-theme-filter]").forEach((x) => {
            x.classList.toggle("active", x === b);
            x.setAttribute("aria-pressed", x === b);
          });
          render(+b.dataset.themeFilter);
        }),
    );
    render(-1);
  }
  function riskBlock() {
    return `<div class="risk-layout"><div class="panel heat-panel"><h3>${t("Impact × Likelihood", "影响 × 可能性")}</h3><small>${t("Rows: impact · Columns: likelihood", "行：影响 · 列：可能性")}</small><div class="heat-grid"><span></span>${[0, 1, 2].map((n) => `<small>${levelName(n)}</small>`).join("")}${[
      2, 1, 0,
    ]
      .map(
        (impact) =>
          `<small>${levelName(impact)}</small>${[0, 1, 2]
            .map((likelihood) => {
              const count = r.risks.filter(
                (x) => level(x.impact) === impact && level(x.likelihood) === likelihood,
              ).length;
              return `<button ${count ? "" : "disabled"} data-impact="${impact}" data-risk="${impact},${likelihood}" style="--heat:${0.08 + (impact + likelihood) * 0.09}" aria-label="${t("Impact", "影响")} ${levelName(impact)}, ${t("Likelihood", "可能性")} ${levelName(likelihood)}: ${count}">${count}</button>`;
            })
            .join("")}`,
      )
      .join(
        "",
      )}</div>${btn(t("Show all risks", "显示全部风险"), 'data-risk="all"', true)}<p class="muted">${t("Counts from this edition’s risk assessment.", "数量来自本期风险评估。")}</p></div><div id="riskRows"></div></div>`;
  }
  function bindRisks() {
    if (!$("#riskRows")) return;
    const render = (filter) => {
      $("#riskRows").innerHTML =
        r.risks
          .filter((x) => filter === "all" || `${level(x.impact)},${level(x.likelihood)}` === filter)
          .map(
            (x) =>
              `<article class="risk-row panel"><div class="section-head"><h3>${esc(x.name)}</h3><div class="pills"><span class="severity l${level(x.impact)}">${t("Impact", "影响")}: ${zh ? levelName(level(x.impact)) : esc(x.impact)}</span><span class="severity l${level(x.likelihood)}">${t("Likelihood", "可能性")}: ${zh ? levelName(level(x.likelihood)) : esc(x.likelihood)}</span></div></div><p>${esc(x.mitigation)}</p>${evidence(x.sourceIndexes)}</article>`,
          )
          .join("") || `<p class="empty">${t("No risks in this cell.", "该单元格暂无风险。")}</p>`;
    };
    $$("[data-risk]").forEach(
      (b) =>
        (b.onclick = () => {
          $$("[data-risk]").forEach((x) => {
            x.classList.toggle("active", x === b);
            x.setAttribute("aria-pressed", x === b);
          });
          render(b.dataset.risk);
        }),
    );
    render("all");
  }
  function positioning() {
    return `<div class="desk-grid"><section class="panel" id="positioning">${heading(t("Positioning desk", "策略配置"))}<div class="controls">${btn(t("Opportunities", "投资机会"), 'data-position="opportunities"', true)}${btn(t("Defensive", "防御策略"), 'data-position="defensive"')}${btn(t("All", "全部"), 'data-position="all"')}</div><div id="positionRows"></div></section><section class="panel" id="outlook">${heading(t("Forward outlook", "前瞻展望"))}${[ ["short", t("1–3 months", "1–3个月")], ["long", t("6–12 months", "6–12个月")] ].map(([k, label]) => `<div class="outlook-period"><h3>${label}</h3><p>${esc(r[k])}</p></div>`).join("")}<div class="controls">${["catalysts", "watchList"].map((k, i) => btn([t("Key catalysts", "关键催化剂"), t("Watch list", "观察清单")][i], `data-outlook="${k}"`, !i)).join("")}</div><div id="outlookRows"></div></section></div>`;
  }
  function bindPosition() {
    if (!$("#positionRows")) return;
    const render = (key) => {
      $("#positionRows").innerHTML = (key === "all" ? [...r.opportunities, ...r.defensive] : r[key])
        .map(
          (x) =>
            `<article class="position-row"><div class="section-head"><h3>${esc(x.title)}</h3><span class="badge">${esc(zh ? { short: "短期", medium: "中期", long: "长期", "short-term": "短期", "medium-term": "中期", "long-term": "长期" }[x.horizon] || x.horizon : x.horizon)}</span></div><p>${esc(x.rationale)}</p><div class="chips">${x.tickers.map((s) => btn(esc(s), `class="ticker-pill" data-ticker="${esc(s)}"`)).join("")}</div>${evidence(x.sourceIndexes)}</article>`,
        )
        .join("");
    };
    $$("[data-position]").forEach(
      (b) =>
        (b.onclick = () => {
          $$("[data-position]").forEach((x) => {
            x.classList.toggle("active", x === b);
            x.setAttribute("aria-pressed", x === b);
          });
          render(b.dataset.position);
        }),
    );
    render("opportunities");
    const outlook = (key) => {
      $("#outlookRows").innerHTML = Array.isArray(r[key])
        ? `<ul class="outlook-list">${r[key].map((s) => `<li>${esc(s)}</li>`).join("")}</ul>`
        : `<p class="outlook-copy">${esc(r[key])}</p>`;
    };
    $$("[data-outlook]").forEach(
      (b) =>
        (b.onclick = () => {
          $$("[data-outlook]").forEach((x) => {
            x.classList.toggle("active", x === b);
            x.setAttribute("aria-pressed", x === b);
          });
          outlook(b.dataset.outlook);
        }),
    );
    outlook("catalysts");
  }
  const ledger = () =>
    `<section id="evidence">${heading(t("Source ledger", "信息源台账"), `<a class="text-link" href="${href("newsroom/index.html")}">${t("Full newsroom", "完整新闻中心")} · ${r.sources}</a>`)}<div id="wire"></div></section>`;
  function macroStrip() {
    const d = r.marketData, e = d.economic_data;
    const tiles = region === "global" ? [[t("Fed funds", "联邦基金利率"), d.economy[0].value], [t("PCE", "PCE通胀"), d.economy[1].value], ...["USD/JPY", "EUR/USD"].map(pair => [pair, d.forex.find(x => x.pair === pair).bid])]
      : region === "au" ? [["RBA Cash", d.rates[0].value], ["CPI", e[1].value], ["GDP", e[0].value], ["Unemployment", e[3].value]]
      : [["GDP", e[0].value], ["CPI", e[1].value], ["制造业PMI", e[3].value], ["1年期LPR", d.rates[0].value]];
    return `<div class="macro-strip">${tiles.map(([label, value]) => `<div><small>${label}</small><b class="mono">${esc(value)}</b></div>`).join("")}</div>`;
  }
  function home() {
    return `<div class="command-grid">${chart()}<section class="panel pulse-card">${pulse()}<div class="lead"><small class="accent">${t("LEAD THESIS", "核心研判")}</small><h1>${esc(r.highlights[0])}</h1></div><div class="lead-sources">${r.sourceIndexes
      .slice(0, 3)
      .map((i) => r.news.find((n) => n.index === i))
      .filter(Boolean)
      .map(story)
      .join(
        "",
      )}</div>${macroStrip()}</section></div>${attribution()}${section("executive", t("Executive brief", "核心摘要"), briefs())}${section("sectors", t("Cross-sector intelligence", "跨板块情报"), sectorCards())}${section("risks", t("Risk matrix & register", "风险矩阵与清单"), riskBlock())}${positioning()}${ledger()}`;
  }
  function markets() {
    const d = r.marketData;
    return `${title(t("Markets", "市场行情"), t("Benchmark snapshots · Macro · FX", "基准快照 · 宏观 · 外汇"))}${chart()}${section("leaderboard", t("Index leaderboard", "指数排行"), `<div class="table-wrap panel"><table><thead><tr>${[t("Benchmark", "基准"), t("Last", "最新"), t("Change", "变动"), t("Return", "涨跌幅"), t("Session path", "示意走势")].map((s) => `<th>${s}</th>`).join("")}</tr></thead><tbody>${r.indices.map((i, n) => `<tr><td><button class="table-index" data-focus-index="${n}">${esc(i.name)} <small>${esc(i.symbol)}</small></button></td><td>${i.price}</td><td class="${i.direction}">${i.change}</td><td>${delta(i)}</td><td>${spark(i)}</td></tr>`).join("")}</tbody></table></div>`)}<div class="desk-grid"><section class="panel">${heading(t("Central bank policy rates", "央行政策利率"))}${[...d.rates].sort((a, b) => parseFloat(b.rate || b.value) - parseFloat(a.rate || a.value))
      .map((x, i) => {
        const value = x.rate || x.value,
          numbers = value.match(/[\d.]+/g).map(Number),
          valueNum = Math.max(...numbers),
          max = Math.max(...d.rates.map((v) => Math.max(...(v.rate || v.value).match(/[\d.]+/g).map(Number))));
        return `<div class="macro-row"><div><span>${x.url ? `<a href="${esc(x.url)}" target="_blank" rel="noopener noreferrer">${esc(x.bank || x.indicator)} ↗</a>` : esc(x.bank || x.indicator)}</span><b class="mono">${esc(value)}</b></div><div class="bar"><i style="width:${(valueNum / max) * 100}%;min-width:${valueNum > 0 ? 2 : 0}px;background:${colors[i % 7]}"></i></div></div>`;
      })
      .join(
        "",
      )}</section><section class="panel">${heading(t("Economic indicators", "经济指标"))}${d.economic_data.map((x) => `<div class="macro-row sentiment-${esc(x.sentiment)}"><div><span>${esc(x.event)}</span><b class="mono">${esc(x.value)}</b></div><div class="bar"><i style="width:${Math.min(100, Math.abs(x.numeric_value / x.max_value) * 100)}%;background:var(--sentiment)"></i></div><small><span class="sentiment-pill">${zh ? {positive:"积极",negative:"消极",neutral:"中性"}[x.sentiment] : esc(x.sentiment)}</span> ${esc(x.date)} · ${t("Scale", "量程")} ${x.max_value}${esc(x.unit)}</small></div>`).join("")}</section></div>${section("economy", t("Economy snapshot", "经济快照"), `<div class="economy-grid">${d.economy.map((x) => `<div class="panel"><small>${esc(x.indicator)}</small><strong class="mono">${esc(x.value)}</strong></div>`).join("")}</div>`)}${d.forex ? section("fx", t("Foreign exchange", "外汇"), `<div class="table-wrap panel"><table><thead><tr>${["pair", "bid", "ask", "spread", "change"].map((k, i) => `<th><button data-sort="${k}">${[t("Pair", "货币对"), t("Bid", "买入"), t("Ask", "卖出"), t("Spread (pips)", "点差（点）"), t("Change", "变动")][i]} ↕</button></th>`).join("")}</tr></thead><tbody id="fxRows"></tbody></table></div>`) : ""}${section("sectors", t("Sector intelligence", "板块情报"), sectorCards())}`;
  }
  function sector() {
    const i = Number(W.params.get("sector")) || 0,
      s = r.sectors[i] || r.sectors[0];
    return `${title(esc(s.name), `<a href="${href("markets/index.html")}">${t("Markets", "市场")}</a> / ${t("Sector analysis", "板块分析")}`)}<div class="desk-grid"><section class="panel">${heading(t("Sector trend", "板块趋势"))}<p>${esc(s.trend)}</p></section><section class="panel implication-panel">${heading(t("Investment implication", "投资含义"))}<p>${esc(s.implication)}</p></section></div>${section("related", t("Regional benchmark context", "区域基准背景"), `<div class="snapshot-grid">${r.indices.map((x) => `<a class="panel" href="${href("markets/index.html")}"><small>${esc(x.name)}</small><b class="mono">${x.price}</b>${delta(x)}</a>`).join("")}</div>`)}${section(
      "reporting",
      t("Cited reporting", "引用报道"),
      `<div class="news-grid cards">${s.sourceIndexes
        .map((n) => r.news.find((x) => x.index === n))
        .filter(Boolean)
        .map(story)
        .join("")}</div>`,
    )}`;
  }
  function article() {
    const n = r.news.find((x) => x.index === +W.params.get("id")) || r.news[0],
      connected = r.sectors.map((s, i) => ({ ...s, i })).filter((s) => s.sourceIndexes.includes(n.index));
    return `${title(t("Source briefing", "来源简报"), `<a href="${href("newsroom/index.html")}">${t("Newsroom", "新闻中心")}</a> / ${n.index}`)}<article class="article panel"><div><small>${esc(n.source)}<time>${esc(W.dateText(n.publishedAt))}</time></small><h1>${esc(n.title)}</h1><a class="text-link" href="${esc(n.url)}" target="_blank" rel="noopener noreferrer">${t("Read original reporting", "阅读原始报道")}</a></div><img src="${esc(n.imageUrl)}" alt="${esc(n.title)}"></article>${section("connected", t("Connected sector analysis", "相关板块分析"), connected.length ? `<div class="sector-grid">${connected.map((s) => `<a class="panel" href="${href("markets/sector.html", `&sector=${s.i}`)}"><h3>${esc(s.name)}</h3><p>${esc(s.trend)}</p><p class="implication">${esc(s.implication)}</p></a>`).join("")}</div>` : `<a href="${href("archive/report.html")}">${t("Read the full regional report", "阅读完整区域报告")}</a>`)}${section(
      "nearby",
      t("Nearby reporting", "相关报道"),
      `<div class="news-grid cards">${r.news
        .filter((x) => x.index !== n.index)
        .sort((a, b) => Math.abs(a.index - n.index) - Math.abs(b.index - n.index))
        .slice(0, 6)
        .map(story)
        .join("")}</div>`,
    )}`;
  }
  function archive() {
    return `${title(t("Research desk", "研究台"), t("30 August 2026 · Three regional reports", "2026年8月30日 · 三个区域报告"))}<div class="report-cards">${Object.values(
      reports,
    )
      .map(
        (x) =>
          `<a class="panel report-card" href="${W.root}archive/report.html?region=${x.region}"><small>${t("CURRENT REPORT", "本期报告")}</small><h2>${zh ? { global: "全球", au: "澳洲", cn: "大中华区" }[x.region] : x.edition}</h2><div class="pulse-score"><b>${x.score}<small>/100</small></b></div><p>${esc(x.highlights[0])}</p><div class="coverage">${x.sources} ${t("sources", "来源")} · ${x.sectors.length} ${t("sectors", "板块")}</div><time>${zh ? "2026年8月30日" : x.date} · ${W.reportTime(x)}</time></a>`,
      )
      .join("")}</div>${section("regional-matrix", t("Cross-regional matrix", "跨区域比较"), `<div class="panel table-wrap"><table class="regional-table"><thead><tr><th>${t("Snapshot", "快照")}</th>${[t("Global", "全球"), t("Australia", "澳洲"), t("Greater China", "大中华区")].map(x => `<th>${x}</th>`).join("")}</tr></thead><tbody>${[
      [t("Sentiment score", "情绪评分"), x => `<div class="sentiment-stack">${x.score}/100<div class="bar"><i style="width:${x.score}%;background:var(--accent)"></i></div></div>`],
      [t("Lead index & delta", "主要指数及涨跌"), x => `${esc(x.indices[0].name)}<br>${x.indices[0].price} ${delta(x.indices[0])}`],
      [t("Policy rate", "政策利率"), x => esc(x.marketData.rates[0].rate || x.marketData.rates[0].value)],
      [t("Sector signals", "板块信号"), x => x.sectors.length],
      [t("High-impact risks", "高影响风险"), x => x.risks.filter(v => level(v.impact) === 2).length],
      [t("Source count", "来源数量"), x => x.sources],
      [t("Full research", "完整研究"), x => `<a class="text-link" href="${W.root}archive/report.html?region=${x.region}">${t("Open full report ↗", "打开完整报告 ↗")}</a>`]
    ].map(([label, value]) => `<tr><th>${label}</th>${Object.values(reports).map(x => `<td>${value(x)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`)}`;
  }
  function report() {
    return `${title(t("Connected market report", "完整市场研究报告"))}<div class="report-layout"><aside class="toc"><b>${t("IN THIS REPORT", "报告目录")}</b>${[
      ["executive", t("Executive brief", "核心摘要")],
      ["sectors", t("Sectors", "板块")],
      ["risks", t("Risks", "风险")],
      ["positioning", t("Positioning", "策略")],
      ["outlook", t("Outlook", "展望")],
      ["evidence", t("Evidence", "来源")],
    ]
      .map(([id, label]) => `<a href="#${id}">${label}</a>`)
      .join(
        "",
      )}</aside><div><section class="panel">${pulse()}</section><section id="executive">${heading(t("Executive brief", "核心摘要"))}<h3 class="report-lead">${esc(r.highlights[0])}</h3>${briefs()}</section>${section("sectors", t("Sector intelligence", "板块情报"), sectorCards())}${section("risks", t("Risk register", "风险清单"), riskBlock())}${positioning()}${ledger()}</div></div>`;
  }
  const renderers = {
    home,
    markets,
    sector,
    article,
    archive,
    report,
    newsroom: () =>
      `${title(t("Newsroom", "新闻中心"), `${r.sources} ${t("source stories · Complete edition", "条来源报道 · 完整版本")}`)}<div id="wire"></div>`,
  };
  main.innerHTML = renderers[page]();
  document.title = `${t({ home: "Intelligence", markets: "Markets", sector: "Sector analysis", article: "Source briefing", archive: "Research", report: "Market report", newsroom: "Newsroom" }[page], { home: "市场情报", markets: "市场", sector: "板块分析", article: "来源简报", archive: "研究", report: "市场报告", newsroom: "新闻中心" }[page])} — WANEYE`;
  main.insertAdjacentHTML(
    "afterend",
    `<footer><span>WANEYE © 2026</span><span>${t("Snapshot research · Not a live trading feed", "快照研究 · 非实时行情")}</span><span>${t("Analysis is informational and does not constitute investment advice.", "分析仅供参考，不构成投资建议。")}</span></footer>`,
  );
  $$(".attribution a").forEach(a => {
    const highlight = () => { const card = $(a.getAttribute("href")); if (!card) return; card.classList.add("highlight"); clearTimeout(card.highlightTimer); card.highlightTimer = setTimeout(() => card.classList.remove("highlight"), 1800); };
    a.onpointerenter = highlight;
    a.onfocus = highlight;
    a.onclick = e => { e.preventDefault(); highlight(); $(a.getAttribute("href")).scrollIntoView({behavior: "smooth", block: "center"}); };
  });
  const fades = () => $$(".tape,.index-tabs").forEach(el => el.classList.toggle("scroll-fade", el.scrollWidth > el.clientWidth + el.scrollLeft + 2));
  $$(".tape,.index-tabs").forEach(el => el.addEventListener("scroll", fades));
  window.addEventListener("resize", fades); fades();
  bindBriefs();
  bindRisks();
  bindPosition();
  window.mountChart(W);
  if ($("#wire")) wire($("#wire"), r.news, page === "home" ? 9 : Infinity);
  if ($("#fxRows")) {
    let key = "pair",
      ascending = true;
    const render = () => {
      $("#fxRows").innerHTML = r.marketData.forex.map(x => ({...x, spread: (x.ask - x.bid) * (x.pair.endsWith("JPY") ? 100 : 10000)}))
        .sort(
          (a, b) =>
            (typeof a[key] === "number" ? a[key] - b[key] : a[key].localeCompare(b[key])) * (ascending ? 1 : -1),
        )
        .map(
          (x) =>
            `<tr><td>${x.pair}</td><td>${x.bid.toFixed(x.pair.endsWith("JPY") ? 2 : 4)}</td><td>${x.ask.toFixed(x.pair.endsWith("JPY") ? 2 : 4)}</td><td>${x.spread.toFixed(1)}</td><td class="${x.change >= 0 ? "up" : "down"}">${x.change > 0 ? "+" : ""}${x.change.toFixed(x.pair.endsWith("JPY") ? 2 : 4)}<span class="fx-delta" title="${t("Relative change", "相对变动")} ${(x.change / (x.bid - x.change) * 100).toFixed(2)}%"><i style="width:${Math.min(100, Math.abs(x.change / (x.bid - x.change)) * 10000)}%"></i></span></td></tr>`,
        )
        .join("");
    };
    $$("[data-sort]").forEach(
      (b) =>
        (b.onclick = () => {
          ascending = key === b.dataset.sort ? !ascending : true;
          key = b.dataset.sort;
          $$("[data-sort]").forEach((x) =>
            x.closest("th").setAttribute("aria-sort", x === b ? (ascending ? "ascending" : "descending") : "none"),
          );
          render();
        }),
    );
    render();
  }
})();

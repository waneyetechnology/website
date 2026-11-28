/* Shared presentation and interaction primitives. All source copy stays in content.js. */
const W = (() => {
  const params = new URLSearchParams(location.search),
    reports = window.WANEYE_REPORTS;
  const region = reports[params.get("region")] ? params.get("region") : "global",
    r = reports[region];
  const zh = region === "cn",
    page = document.body.dataset.page,
    root = page === "home" ? "" : "../";
  const $ = (s, el = document) => el.querySelector(s),
    $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const t = (en, cn) => (zh ? cn : en),
    esc = (s) =>
      String(s ?? "").replace(
        /[&<>"']/g,
        (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c],
      );
  const reportTime = (report) =>
    /[A-Z]/.test(report.time) ? report.time : `${report.time} ${report.region === "cn" ? t("CST", "北京时间") : "UTC"}`;
  const colors = ["#38bdf8", "#a855f7", "#f59e0b", "#ec4899", "#10b981", "#6366f1", "#fb923c"];
  const href = (path, extra = "") => `${root}${path}?region=${region}${extra}`;
  const heading = (title, extra = "") => `<div class="section-head"><h2>${title}</h2>${extra}</div>`;
  const btn = (text, attr = "", active = false) =>
    `<button ${attr} ${active ? 'class="active" aria-pressed="true"' : 'aria-pressed="false"'}>${text}</button>`;
  const delta = (i) =>
    `<span class="delta ${i.direction === "up" ? "up" : "down"}">${i.direction === "up" ? "▲" : "▼"} ${esc(i.change_pct)}</span>`;
  const spark = (i) => {
    const a = i.series["1D"],
      lo = Math.min(...a),
      span = Math.max(...a) - lo || 1;
    return `<svg class="spark ${i.direction}" viewBox="0 0 70 24" aria-hidden="true"><polyline points="${a.map((v, n) => `${(n * 70) / 95},${22 - ((v - lo) / span) * 20}`).join(" ")}"/></svg>`;
  };
  const dateText = (value) => {
    if (!/^\d{4}-\d{2}-\d{2}T/.test(value || "")) return value || "";
    const d = new Date(value);
    if (Number.isNaN(+d)) return value;
    const clock = d.toISOString().slice(11, 16);
    return zh ? `${d.getUTCMonth() + 1}月${d.getUTCDate()}日 ${clock}` : `${d.getUTCDate()} ${["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][d.getUTCMonth()]} · ${clock} UTC`;
  };
  const story = (n, index = 0) =>
    `<a class="story" href="${href("newsroom/article.html", `&id=${n.index}`)}"><img src="${esc(n.imageUrl)}" ${page === "newsroom" && index >= 9 ? 'loading="lazy"' : 'loading="eager"'} alt=""><div><small><span class="publisher">${esc(n.source)}</span><time>${esc(dateText(n.publishedAt))}</time></small><h3>${esc(n.title)}</h3></div></a>`;
  const evidence = (ids) =>
    `<details class="evidence"><summary>${ids.length} ${t("cited sources", "条引用来源")}</summary>${ids
      .map((i) => r.news.find((n) => n.index === i))
      .filter(Boolean)
      .map(story)
      .join("")}</details>`;
  const sectorCards = () =>
    `<div class="sector-grid">${r.sectors.map((s, i) => `<a id="sector-${i}" class="sector-card panel ${r.sectors.length % 2 && i === r.sectors.findIndex(x => x.sourceIndexes.length === Math.max(...r.sectors.map(v => v.sourceIndexes.length))) ? "featured" : ""}" style="--series:${colors[i % 7]}" href="${href("markets/sector.html", `&sector=${i}`)}"><div class="section-head"><h3>${esc(s.name)}</h3><span class="badge">${s.sourceIndexes.length} ${t("sources", "来源")}</span></div><p>${esc(s.trend)}</p><div class="implication">${esc(s.implication)}</div></a>`).join("")}</div>`;
  const pulse = () =>
    `<div class="section-head"><h2>${t("Market pulse", "市场温度")}</h2><span class="badge">${t("Snapshot", "快照")}</span></div><div class="pulse-score"><b>${r.score}<small>/100</small></b><span>${esc(zh ? { neutral: "中性", positive: "积极", negative: "消极", bullish: "看涨", bearish: "看跌" }[r.sentiment] || r.sentiment : r.sentiment)}</span></div><div class="gauge"><i style="left:${r.score}%"></i></div><div class="coverage"><span><b>${r.sources}</b> ${t("Sources", "来源")}</span><span><b>${r.sectors.length}</b> ${t("Sectors", "板块")}</span><span><b>${r.risks.length}</b> ${t("Risks", "风险")}</span></div>`;
  const chart = () =>
    `<section class="panel chart-card" id="benchmark"><div class="section-head"><h2>${t("Benchmark monitor", "基准指数监测")}</h2><span class="badge">${t("30 AUG 2026", "2026年8月30日")}</span></div><div class="index-tabs">${r.indices.map((i, n) => btn(`${esc(i.name)} ${delta(i)}`, `data-index="${n}"`, n === 0)).join("")}</div><div class="chart-toolbar"><div id="chartQuote"></div><div class="controls">${["1D", "5D", "1M", "3M"].map((f, i) => btn(zh ? { "1D": "1日", "5D": "5日", "1M": "1月", "3M": "3月" }[f] : f, `data-frame="${f}"`, !i)).join("")}${btn(t("Compare", "对比"), 'id="compare"')}</div></div><div id="chartLegend" class="chips"></div><div id="chartHud" class="mono chart-hud" aria-live="off"></div><canvas id="indexCanvas" aria-label="${t("Illustrative benchmark price chart", "示意基准价格走势图")}" tabindex="0"></canvas><div id="sessionStats" class="session-stats"></div><p class="chart-note">${t("Illustrative path & activity · anchored to benchmark snapshot", "示意走势与活跃度 · 基于基准快照")} · ${region === "global" ? t("Global benchmark values are illustrative, not reported quotes.", "全球基准数值为示意数据。") : t("Reported snapshot · synthetic paths", "报告原始快照 · 模拟走势")}</p></section>`;
  document.documentElement.lang = zh ? "zh-CN" : "en";
  const nav = [
    ["Intelligence", "市场情报", "index.html", "home"],
    ["Markets", "市场", "markets/index.html", "markets"],
    ["Newsroom", "新闻中心", "newsroom/index.html", "newsroom"],
    ["Research", "研究", "archive/index.html", "archive"],
  ];
  $("#shell").innerHTML =
    `<a class="skip" href="#main">${t("Skip to content", "跳至正文")}</a><header class="topbar"><a class="brand" href="${href("index.html")}"><img src="${root}favicon.svg" alt="">WANEYE</a><nav id="nav">${nav.map(([en, cn, url, key]) => `<a class="${page === key || { sector: "markets", article: "newsroom", report: "archive" }[page] === key ? "active" : ""}" href="${href(url)}">${t(en, cn)}</a>`).join("")}</nav><button id="searchButton" class="search-trigger">⌕ <span>${t("Search tickers, sectors, news…", "搜索股票、板块、新闻…")}</span><kbd>⌘K</kbd></button><div class="editions">${[
      "global",
      "au",
      "cn",
    ]
      .map((v, i) => {
        const q = new URLSearchParams(location.search);
        q.set("region", v);
        q.delete("id");
        q.delete("sector");
        return `<a class="${v === region ? "active" : ""}" href="?${q}">${(zh ? ["全球", "澳洲", "中文"] : ["Global", "Australia", "中文"])[i]}</a>`;
      })
      .join(
        "",
      )}</div><button id="theme" aria-label="${t("Toggle color theme", "切换明暗主题")}">☀</button><time class="timestamp">${t("30 Aug", "8月30日")} · ${reportTime(r)}</time><button id="menu" aria-label="${t("Toggle navigation", "切换导航")}" aria-expanded="false">☰</button></header>${["home", "markets"].includes(page) ? `<div class="tape">${r.indices.map((i, n) => `<button data-focus-index="${n}"><b>${esc(i.symbol)}</b><span class="mono">${i.price}</span>${delta(i)}${spark(i)}</button>`).join("")}</div>` : ""}<dialog id="searchDialog" aria-labelledby="searchLabel"><form method="dialog"><button aria-label="${t("Close", "关闭")}">×</button></form><h2 id="searchLabel">${t("Search intelligence", "搜索市场情报")}</h2><input id="searchInput" type="search" placeholder="${t("Ticker, sector or headline", "股票代码、板块或标题")}" autocomplete="off"><div id="searchResults" aria-live="polite"></div></dialog>`;
  const theme = () => {
    $("#theme").textContent = document.documentElement.dataset.theme === "light" ? "☾" : "☀";
  };
  theme();
  $("#theme").onclick = () => {
    const value = document.documentElement.dataset.theme === "light" ? "dark" : "light";
    document.documentElement.dataset.theme = value;
    try {
      localStorage.setItem("waneye-theme", value);
    } catch {}
    theme();
    window.dispatchEvent(new Event("themechange"));
  };
  $("#menu").onclick = () => {
    const open = $("#nav").classList.toggle("open");
    $("#menu").setAttribute("aria-expanded", open);
  };
  const searchItems = Object.values(reports).flatMap((report) => [
    ...report.news.map((n) => ({
      title: n.title, queryText: n.title, category: t("Headline", "新闻"),
      label: n.source,
      url: `${root}newsroom/article.html?region=${report.region}&id=${n.index}`,
    })),
    ...report.sectors.map((s, i) => ({
      title: s.name, snippet: s.trend, queryText: `${s.name} ${s.trend} ${s.implication}`, category: t("Sector", "板块"),
      label: report.edition,
      url: `${root}markets/sector.html?region=${report.region}&sector=${i}`,
    })),
    ...report.highlights.map((text) => ({
      title: text, queryText: text, category: t("Brief", "摘要"),
      label: report.edition,
      url: `${root}archive/report.html?region=${report.region}#executive`,
    })),
    ...[...report.opportunities, ...report.defensive].map((x) => ({
      title: x.title, snippet: x.rationale, tickers: x.tickers, queryText: `${x.tickers.join(" ")} ${x.title} ${x.rationale}`, category: t("Positioning", "配置"),
      label: report.edition,
      url: `${root}archive/report.html?region=${report.region}#positioning`,
    })),
  ]);
  function search() {
    const q = $("#searchInput").value.trim().toLowerCase();
    const found = searchItems.filter((x) => q && x.queryText.toLowerCase().includes(q));
    $("#searchResults").innerHTML = `<small class="search-count">${found.length} ${t("results", "条结果")} · <kbd>Esc</kbd> ${t("to close", "关闭")}</small>` + (found.length
      ? found.map((x) => `<a href="${x.url}"><small><span class="badge">${x.category}</span> ${esc(x.label)}</small><h3>${esc(x.title)}</h3>${(x.tickers || []).map(ticker => `<span class="ticker-pill">${esc(ticker)}</span>`).join("")}${x.snippet ? `<p class="search-snippet">${esc(x.snippet)}</p>` : ""}</a>`).join("")
      : `<p class="muted">${q ? t("No matching results.", "未找到匹配结果。") : t("Search across all three editions.", "搜索全部三个区域版本。")}</p>`);
  }
  function openSearch(value = "") {
    const d = $("#searchDialog");
    if (!d.open) d.showModal();
    $("#searchInput").value = value;
    search();
    $("#searchInput").focus();
  }
  $("#searchButton").onclick = () => openSearch();
  $("#searchInput").oninput = search;
  document.addEventListener("keydown", (e) => {
    if (
      ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") ||
      (e.key === "/" && !/INPUT|TEXTAREA|SELECT/.test(e.target.tagName))
    ) {
      e.preventDefault();
      openSearch();
    }
  });
  document.addEventListener("click", (e) => {
    const pill = e.target.closest("[data-ticker]");
    if (pill) openSearch(pill.dataset.ticker);
  });
  function wire(host, items = r.news, limit = Infinity) {
    let publisher = "",
      q = "",
      view = page === "home" ? "wire" : "cards";
    const publishers = [...new Set(items.map((n) => n.source))];
    host.innerHTML = `<div class="wire-tools"><input type="search" aria-label="${t("Filter headlines", "筛选标题")}" placeholder="${t("Filter headlines…", "筛选标题…")}"><div class="controls">${btn(t("Cards", "卡片"), 'data-view="cards"', view === 'cards')}${btn(t("Wire", "快讯"), 'data-view="wire"', view === 'wire')}</div><span class="wire-count mono"></span></div><div class="chips publishers">${btn(t("All publishers", "全部来源"), 'data-publisher=""', true)}${publishers.map((p) => btn(esc(p), `data-publisher="${esc(p)}"`)).join("")}</div><div class="news-grid"></div>`;
    const render = () => {
      const filtered = items.filter(
        (n) => (!publisher || n.source === publisher) && (!q || n.title.toLowerCase().includes(q)),
      );
      $(".news-grid", host).className = `news-grid ${view}`;
      $(".news-grid", host).innerHTML =
        filtered.slice(0, limit).map(story).join("") || `<p>${t("No matching stories.", "未找到匹配报道。")}</p>`;
      $(".wire-count", host).textContent = `${filtered.length} ${t("stories", "条报道")}`;
    };
    $("input", host).oninput = (e) => {
      q = e.target.value.toLowerCase();
      render();
    };
    host.onclick = (e) => {
      const p = e.target.closest("[data-publisher]"),
        v = e.target.closest("[data-view]");
      if (p) {
        publisher = p.dataset.publisher;
        $$("[data-publisher]", host).forEach(
          (b) => (b.classList.toggle("active", b === p), b.setAttribute("aria-pressed", b === p)),
        );
      }
      if (v) {
        view = v.dataset.view;
        $$("[data-view]", host).forEach(
          (b) => (b.classList.toggle("active", b === v), b.setAttribute("aria-pressed", b === v)),
        );
      }
      if (p || v) render();
    };
    render();
  }
  return {
    dateText,
    reportTime,
    params,
    reports,
    region,
    r,
    zh,
    page,
    root,
    $,
    $$,
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
  };
})();

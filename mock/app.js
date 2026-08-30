const reports = window.WANEYE_REPORTS;
let region = "global";
let strategy = "opportunities";
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const ui = {
  en: {nav:["Intelligence","Markets","Newsroom","Archive"],status:"Live intelligence",board:"SIGNAL BOARD",research:"WANEYE RESEARCH",issue:"MARKET BRIEF",hero:"See the market<br><em>before it moves.</em>",dek:"Independent signal extraction from global reporting, structured for investors who value context over noise.",pulse:"MARKET PULSE",pulseCopy:"Composite sentiment across today’s source set.",stats:["Sources analysed","Sector signals","Risk flags"],brief:"THE BRIEF",briefTitle:"What matters now",sector:"SECTOR INTELLIGENCE",sectorTitle:"Signals across the board",risk:"RISK REGISTER",riskTitle:"Know the downside",position:"POSITIONING",positionTitle:"Act on the signal",opportunity:"Opportunities",defensive:"Defensive",forward:"FORWARD VIEW",forwardTitle:"The road ahead",short:"1—3 MONTHS",long:"6—12 MONTHS",catalyst:"CATALYST MONITOR",source:"SOURCE LEDGER",sourceTitle:"Reporting behind the view",archive:"RESEARCH ARCHIVE",archiveTitle:"Every report. One continuous view.",archiveCopy:"Explore the preserved record of Waneye analysis across global, Australian and Greater China markets.",archiveButton:"Browse the archive",sectorSignal:"SECTOR SIGNAL",openAnalysis:"Open analysis",leadSignal:"LEAD SIGNAL",allHighlights:n=>`All ${n} executive highlights`,opportunityCard:"OPPORTUNITY",defensiveCard:"DEFENSIVE MOVE"},
  zh: {nav:["市场情报","市场板块","新闻中心","研究档案"],status:"实时情报",board:"信号看板",research:"WANEYE 研究",issue:"市场简报",hero:"洞察市场<br><em>先于变化。</em>",dek:"从全球财经报道中提炼独立信号，为重视背景与逻辑的投资者提供结构化市场情报。",pulse:"市场温度",pulseCopy:"基于本期全部信息源的综合情绪判断。",stats:["分析信息源","板块信号","风险提示"],brief:"市场简报",briefTitle:"当前要点",sector:"板块情报",sectorTitle:"洞察市场主线",risk:"风险评估",riskTitle:"识别下行风险",position:"策略配置",positionTitle:"将信号转化为行动",opportunity:"投资机会",defensive:"防御策略",forward:"前瞻展望",forwardTitle:"后市研判",short:"未来1—3个月",long:"未来6—12个月",catalyst:"催化剂观察",source:"信息来源",sourceTitle:"支撑研判的市场报道",archive:"研究档案",archiveTitle:"每份报告，构成连续视角。",archiveCopy:"查阅Waneye在全球、澳大利亚及大中华区市场保存的历史分析。",archiveButton:"浏览研究档案",sectorSignal:"板块信号",openAnalysis:"查看分析",leadSignal:"核心信号",allHighlights:n=>`完整呈现${n}项核心摘要`,opportunityCard:"投资机会",defensiveCard:"防御策略"}
};

function applyLocale() {
  const t = ui[region === "cn" ? "zh" : "en"];
  const zh = region === "cn";
  $$(".primary-nav a").forEach((a,i)=>a.textContent=t.nav[i]);
  $(".status").lastChild.textContent=` ${t.status}`;
  $(".ticker-label").textContent=t.board;
  $(".ticker time").textContent=zh?reports[region].date:"23 AUG 2026";
  $(".eyebrow span:first-child").textContent=t.research;
  $("#issueLabel").textContent=`${t.issue} / ${reports[region].time}`;
  $(".masthead h1").innerHTML=t.hero;
  $(".masthead .dek").textContent=t.dek;
  $(".score-wrap .kicker").textContent=t.pulse;
  $(".score-wrap p").textContent=t.pulseCopy;
  $$(".report-meta span").forEach((x,i)=>x.textContent=t.stats[i]);
  $("#brief-title").previousElementSibling.textContent=t.brief; $("#brief-title").textContent=t.briefTitle;
  $("#signals-title").previousElementSibling.textContent=t.sector; $("#signals-title").textContent=t.sectorTitle;
  $("#signals-title").closest(".section-heading").querySelector(":scope > p").textContent=zh?"从当前信息周期中提炼方向性市场情报。":"Directional intelligence, distilled from the current reporting cycle.";
  $("#risk-title").previousElementSibling.textContent=t.risk; $("#risk-title").textContent=t.riskTitle;
  $("#risk-title").closest(".section-heading").querySelector(":scope > p").textContent=zh?"风险的可能性与影响独立于市场情绪进行评估。":"Likelihood and impact are assessed independently from market sentiment.";
  $("#strategy-title").previousElementSibling.textContent=t.position; $("#strategy-title").textContent=t.positionTitle;
  $$('[data-strategy]')[0].textContent=t.opportunity; $$('[data-strategy]')[1].textContent=t.defensive;
  $("#outlook-title").previousElementSibling.textContent=t.forward; $("#outlook-title").textContent=t.forwardTitle;
  $$(".horizon > span")[0].textContent=t.short; $$(".horizon > span")[1].textContent=t.long;
  $(".catalyst-card > .kicker").textContent=t.catalyst;
  $("#news-title").previousElementSibling.textContent=t.source; $("#news-title").textContent=t.sourceTitle;
  $("#news-title").closest(".section-heading").querySelector(":scope > p").textContent=zh?"分析所引用的重点市场报道。":"Selected source headlines referenced by the analysis.";
  $("#archive-title").previousElementSibling.textContent=t.archive; $("#archive-title").textContent=t.archiveTitle;
  $(".archive > p:not(.kicker)").textContent=t.archiveCopy; $("#archiveButton").innerHTML=`${t.archiveButton} <span>↗</span>`;
  const tabs=$$('[data-region]');tabs[0].childNodes[tabs[0].childNodes.length-1].textContent=zh?' 全球':' Global';tabs[1].childNodes[tabs[1].childNodes.length-1].textContent=zh?' 澳大利亚':' Australia';
  $$(".risk-matrix .axis")[0].textContent=zh?'影响':'IMPACT'; $$(".risk-matrix .axis")[1].textContent=zh?'可能性':'LIKELIHOOD';
  $(".matrix-label.high").textContent=zh?'高':'HIGH'; $(".matrix-label.low").textContent=zh?'低':'LOW';
  const archiveLabels=$$(".archive-stats span");(zh?["当前档案记录","市场版本","分析频率"]:["Current archive records","Market editions","Analysis cadence"]).forEach((x,i)=>archiveLabels[i].textContent=x);
  $(".archive-stats div:last-child strong").textContent=zh?'每小时':'Hourly';
  const footerPs=$$("body > footer p");if(footerPs.length){footerPs[0].textContent=zh?'全球视野，智慧金融。':'Global vision for smarter finance.';footerPs[1].textContent=zh?'本网站分析仅供参考，不构成投资建议。':'Analysis is informational and does not constitute investment advice.';}
  $("#searchDialog .kicker").textContent=zh?'搜索情报':'SEARCH INTELLIGENCE';$("#searchDialog label").textContent=zh?'查找板块、主题或股票代码':'Find a sector, theme or ticker';$("#searchInput").placeholder=zh?'例如“人工智能基础设施”或“中际旭创”':'Try “AI infrastructure” or “NVDA”';
}

function render() {
  const r = reports[region];
  document.documentElement.lang = region === "cn" ? "zh" : "en";
  applyLocale();
  $("#editionLabel").textContent = r.edition.toUpperCase();
  $("#briefDate").innerHTML = `${r.date.toUpperCase()}<br>${r.time}`;
  $("#scoreValue").textContent = r.score;
  $("#scoreRing").style.setProperty("--score", r.score);
  $("#sentimentLabel").textContent = r.sentiment;
  $("#sourceCount").textContent = r.sources;
  $("#sectorCount").textContent = String(r.sectors.length).padStart(2,"0");
  $("#riskCount").textContent = String(r.risks.length).padStart(2,"0");
  $("#tickerTrack").innerHTML = r.themes.map(x => `<span class="ticker-item">${x}</span>`).join("");

  const t = ui[region === "cn" ? "zh" : "en"];
  $("#leadStory").innerHTML = `<span class="story-index">01 / ${t.leadSignal}</span><h3>${r.highlights[0]}</h3><div class="story-meta"><span class="signal-pill">${r.sentiment}</span><span>${t.allHighlights(r.highlights.length)} · ${r.time}</span></div>`;
  $("#briefList").innerHTML = r.highlights.slice(1).map((x,i) => `<article class="brief-item"><span>0${i+2}</span><h3>${x}</h3></article>`).join("");
  $("#sectorGrid").innerHTML = r.sectors.map((s,i) => `<a class="sector-card" href="markets/sector.html?region=${region}&sector=${i}"><div class="sector-top"><span class="kicker">${t.sectorSignal}</span><span class="direction ${s.tone}">${s.direction.toUpperCase()}</span></div><h3>${s.name}</h3><p>${s.trend}</p><p class="implication">${s.implication}</p><div class="metric"><strong>${s.metric}</strong><small>${s.metricLabel}</small></div><span class="card-link">${t.openAnalysis} ↗</span></a>`).join("");
  $("#riskDots").innerHTML = r.risks.map((risk,i) => `<span class="risk-dot" style="left:${risk.x}%;top:${risk.y}%" title="${risk.name}">${i+1}</span>`).join("");
  $("#riskList").innerHTML = r.risks.map((risk,i) => `<article class="risk-row"><span>0${i+1}</span><div><h3>${risk.name}</h3><p>${risk.mitigation}</p></div><div class="risk-tags"><i>${risk.impact}</i><i>${risk.likelihood}</i></div></article>`).join("");
  renderStrategy();
  $("#shortOutlook").textContent = r.short;
  $("#longOutlook").textContent = r.long;
  $("#catalystList").innerHTML = r.catalysts.map((x,i) => `<div class="catalyst-row"><span>0${i+1}</span><div>${x}</div></div>`).join("");
  $("#newsList").innerHTML = r.news.map(n => `<a class="news-item" href="newsroom/article.html?region=${region}&id=${n.index}"><span class="news-index">#${String(n.index).padStart(3,"0")}</span><h3>${n.title}</h3><span class="news-source">${n.source}</span><span class="news-date">${n.date}</span><b>↗</b></a>`).join("");
}

function renderStrategy() {
  const items = reports[region][strategy];
  const t = ui[region === "cn" ? "zh" : "en"];
  $("#strategyGrid").innerHTML = items.map((item,i) => `<article class="strategy-card"><span class="card-number">0${i+1}</span><h3>${item.title}</h3><p>${item.rationale}</p><div class="ticker-pills">${item.tickers.map(t=>`<span>${t}</span>`).join("")}</div><div class="card-foot"><span>${strategy === "opportunities" ? t.opportunityCard : t.defensiveCard}</span><span>${item.horizon}</span></div></article>`).join("");
}

$$('[data-region]').forEach(button => button.addEventListener("click", () => {
  region = button.dataset.region;
  $$('[data-region]').forEach(b => b.setAttribute("aria-selected", String(b === button)));
  render();
}));

$$('[data-strategy]').forEach(button => button.addEventListener("click", () => {
  strategy = button.dataset.strategy;
  $$('[data-strategy]').forEach(b => b.classList.toggle("active", b === button));
  renderStrategy();
}));

$("#menuButton").addEventListener("click", () => {
  const open = $(".topbar").classList.toggle("menu-open");
  $("#menuButton").setAttribute("aria-expanded", String(open));
});

const dialog = $("#searchDialog");
$("#searchButton").addEventListener("click", () => { dialog.showModal(); setTimeout(() => $("#searchInput").focus(), 50); });
$("#searchInput").addEventListener("input", event => {
  const query = event.target.value.trim().toLowerCase();
  if (!query) { $("#searchResults").innerHTML = ""; return; }
  const result = [];
  Object.entries(reports).forEach(([key,r]) => {
    [...r.highlights,...r.sectors.map(s=>`${s.name} — ${s.trend}`),...r.opportunities.map(x=>`${x.title} — ${x.tickers.join(", ")}`)].forEach(text => {
      if (text.toLowerCase().includes(query)) result.push({edition:r.edition,text});
    });
  });
  $("#searchResults").innerHTML = result.slice(0,8).map(x=>`<div class="search-result"><span>${x.edition.toUpperCase()}</span>${x.text}</div>`).join("") || `<div class="search-result">${region==='cn'?'未找到匹配的市场情报。':'No matching intelligence found.'}</div>`;
});

$("#archiveButton").addEventListener("click", () => { window.location.href = "archive/index.html"; });

render();

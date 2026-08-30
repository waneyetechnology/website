const reports = window.WANEYE_REPORTS;
const requestedRegion = new URLSearchParams(location.search).get("region");
let region = reports[requestedRegion] ? requestedRegion : "global";
let strategy = "opportunities";
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const ui = {
  en: {nav:["Intelligence","Markets","Newsroom","Research"],status:"Updated hourly",board:"SIGNAL BOARD",research:"WANEYE RESEARCH",issue:"MARKET BRIEF",hero:"See the market<br><em>before it moves.</em>",dek:"Independent signal extraction from global reporting, structured for investors who value context over noise.",pulse:"MARKET PULSE",pulseCopy:"Composite sentiment across today’s source set.",stats:["Sources analysed","Sector signals","Risk flags"],brief:"THE BRIEF",briefTitle:"What matters now",sector:"SECTOR INTELLIGENCE",sectorTitle:"Signals across the board",risk:"RISK REGISTER",riskTitle:"Know the downside",position:"POSITIONING",positionTitle:"Act on the signal",opportunity:"Opportunities",defensive:"Defensive",forward:"FORWARD VIEW",forwardTitle:"The road ahead",short:"1—3 MONTHS",long:"6—12 MONTHS",catalyst:"CATALYST MONITOR",source:"SOURCE INTELLIGENCE",sourceTitle:"Reporting behind the view",archive:"CURRENT RESEARCH",archiveTitle:"Three regions. Three connected views.",archiveCopy:"Move from the executive brief through sector signals, risks, positioning and supporting reporting.",archiveButton:"Explore the research",sectorSignal:"SECTOR SIGNAL",openAnalysis:"Open analysis",leadSignal:"LEAD SIGNAL",allHighlights:n=>`All ${n} executive highlights`,opportunityCard:"OPPORTUNITY",defensiveCard:"DEFENSIVE MOVE"},
  zh: {nav:["市场情报","市场板块","新闻中心","研究"],status:"每小时更新",board:"信号看板",research:"WANEYE 研究",issue:"市场简报",hero:"洞察市场<br><em>先于变化。</em>",dek:"从全球财经报道中提炼独立信号，为重视背景与逻辑的投资者提供结构化市场情报。",pulse:"市场温度",pulseCopy:"基于本期全部信息源的综合情绪判断。",stats:["分析信息源","板块信号","风险提示"],brief:"市场简报",briefTitle:"当前要点",sector:"板块情报",sectorTitle:"洞察市场主线",risk:"风险评估",riskTitle:"识别下行风险",position:"策略配置",positionTitle:"将信号转化为行动",opportunity:"投资机会",defensive:"防御策略",forward:"前瞻展望",forwardTitle:"后市研判",short:"未来1—3个月",long:"未来6—12个月",catalyst:"催化剂观察",source:"信息源情报",sourceTitle:"支撑研判的市场报道",archive:"当前研究",archiveTitle:"三个区域，三个连贯视角。",archiveCopy:"从核心摘要延伸至板块信号、风险、策略配置与相关报道。",archiveButton:"浏览市场研究",sectorSignal:"板块信号",openAnalysis:"查看分析",leadSignal:"核心信号",allHighlights:n=>`完整呈现${n}项核心摘要`,opportunityCard:"投资机会",defensiveCard:"防御策略"}
};

function applyLocale() {
  const t = ui[region === "cn" ? "zh" : "en"];
  const zh = region === "cn";
  if (zh) {
    document.title = "市场情报 — Waneye";
    document.querySelector('meta[name="description"]').content =
      "Waneye 全球市场情报与投资研究。";
    document.querySelector(".skip-link").textContent = "跳至报告";
  }
  $$(".primary-nav a").forEach((a,i)=>a.textContent=t.nav[i]);
  $(".status").lastChild.textContent=` ${t.status}`;
  $(".ticker-label").textContent=t.board;
  $(".ticker time").textContent=reports[region].date;
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
  $$('[data-edition]').forEach(a=>{
    if(a.dataset.edition===region)a.setAttribute('aria-current','page');
    else a.removeAttribute('aria-current');
  });
  const nav=$$(".primary-nav a");nav[0].href=`index.html?region=${region}`;nav[1].href=`markets/index.html?region=${region}`;nav[2].href=`newsroom/index.html?region=${region}`;nav[3].href=`archive/index.html?region=${region}`;
  nav.forEach((a,i)=>{if(i===0)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
  const archiveLabels=$$(".archive-stats span");(zh?["当前区域报告","市场版本","分析频率"]:["Current regional reports","Market editions","Analysis cadence"]).forEach((x,i)=>archiveLabels[i].textContent=x);
  $(".archive-stats div:last-child strong").textContent=zh?'每小时':'Hourly';
  const footerPs=$$("body > footer p");if(footerPs.length){footerPs[0].textContent=zh?'全球视野，智慧金融。':'Global vision for smarter finance.';footerPs[1].textContent=zh?'本网站分析仅供参考，不构成投资建议。':'Analysis is informational and does not constitute investment advice.';}
  $("#searchDialog .kicker").textContent=zh?'搜索情报':'SEARCH INTELLIGENCE';$("#searchDialog label").textContent=zh?'搜索所有市场版本的报道、板块与摘要':'Search reporting, sectors and briefs across all editions';$("#searchInput").placeholder=zh?'例如“人工智能”或“利率”':'Try “AI”, “rates” or a company name';
  $("#searchButton").setAttribute('aria-label',zh?'搜索市场情报':'Search intelligence');$("#menuButton").setAttribute('aria-label',zh?'打开菜单':'Open menu');$("#searchDialog form button").setAttribute('aria-label',zh?'关闭搜索':'Close search');
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
  $("#sectorGrid").innerHTML = r.sectors.map((s,i) => `<a class="sector-card" href="markets/sector.html?region=${region}&sector=${i}"><div class="sector-top"><span class="kicker">${t.sectorSignal}</span></div><h3>${s.name}</h3><p>${s.trend}</p><p class="implication">${s.implication}</p><div class="metric"><strong>${s.sourceIndexes.length}</strong><small>${region==='cn'?'引用信息源':'cited sources'}</small></div><span class="card-link">${t.openAnalysis} ↗</span></a>`).join("");
  $("#riskList").innerHTML = r.risks.map((risk,i) => `<article class="risk-row"><span class="risk-number">${String(i+1).padStart(2,"0")}</span><div class="risk-copy"><h3>${risk.name}</h3><p>${risk.mitigation}</p></div><dl class="risk-assessment"><div><dt>${region==='cn'?'影响':'Impact'}</dt><dd>${risk.impact}</dd></div><div><dt>${region==='cn'?'可能性':'Likelihood'}</dt><dd>${risk.likelihood}</dd></div><div><dt>${region==='cn'?'依据':'Evidence'}</dt><dd>${risk.sourceIndexes.length} ${region==='cn'?'条报道':'sources'}</dd></div></dl></article>`).join("");
  renderStrategy();
  $("#shortOutlook").textContent = r.short;
  $("#longOutlook").textContent = r.long;
  $("#catalystList").innerHTML = r.catalysts.map((x,i) => `<div class="catalyst-row"><span>0${i+1}</span><div>${x}</div></div>`).join("");
  $("#newsList").innerHTML = r.news.slice(0,6).map(n => `<a class="visual-news-card" href="newsroom/article.html?region=${region}&id=${n.index}"><img src="${n.imageUrl}" alt="" loading="lazy"><div><span>${n.meta}</span><h3>${n.title}</h3><b>${region==='cn'?'查看报道':'VIEW STORY'} ↗</b></div></a>`).join("");
}

function renderStrategy() {
  const items = reports[region][strategy];
  const t = ui[region === "cn" ? "zh" : "en"];
  $("#strategyGrid").innerHTML = items.map((item,i) => `<article class="strategy-card"><span class="card-number">0${i+1}</span><h3>${item.title}</h3><p>${item.rationale}</p><div class="ticker-pills">${item.tickers.map(t=>`<span>${t}</span>`).join("")}</div><div class="card-foot"><span>${strategy === "opportunities" ? t.opportunityCard : t.defensiveCard}</span><span>${item.horizon}</span></div></article>`).join("");
}

$$('[data-strategy]').forEach(button => button.addEventListener("click", () => {
  strategy = button.dataset.strategy;
  $$('[data-strategy]').forEach(b => b.classList.toggle("active", b === button));
  $$('[data-strategy]').forEach(b => b.setAttribute("aria-pressed", String(b === button)));
  renderStrategy();
}));

const menuButton = $("#menuButton");
const closeMenu = () => {
  $(".topbar").classList.remove("menu-open");
  menuButton.setAttribute("aria-expanded", "false");
  menuButton.setAttribute("aria-label", region === "cn" ? "打开菜单" : "Open menu");
};
menuButton.addEventListener("click", () => {
  const open = $(".topbar").classList.toggle("menu-open");
  menuButton.setAttribute("aria-expanded", String(open));
  menuButton.setAttribute("aria-label", open ? (region === "cn" ? "关闭菜单" : "Close menu") : (region === "cn" ? "打开菜单" : "Open menu"));
});
$$(".primary-nav a").forEach(link => link.addEventListener("click", closeMenu));
document.addEventListener("click", event => {
  if ($(".topbar").classList.contains("menu-open") && !$(".topbar").contains(event.target)) closeMenu();
});
document.addEventListener("keydown", event => { if(event.key === "Escape") { closeMenu(); if(dialog.open) dialog.close(); } });

const dialog = $("#searchDialog");
let searchTrigger = null;
$("#searchButton").addEventListener("click", event => { searchTrigger = event.currentTarget; dialog.showModal(); setTimeout(() => $("#searchInput").focus(), 50); });
dialog.addEventListener("close", () => { searchTrigger?.focus(); searchTrigger = null; });
$("#searchInput").addEventListener("input", event => {
  const query = event.target.value.trim().toLowerCase();
  if (!query) { $("#searchResults").innerHTML = ""; return; }
  const result = [];
  Object.entries(reports).forEach(([key,r]) => {
    r.highlights.forEach(text => result.push({edition:r.edition,label:region==='cn'?'核心摘要':'Executive brief',text,href:`archive/report.html?region=${key}#executive`}));
    r.sectors.forEach((s,index) => result.push({edition:r.edition,label:s.name,text:s.trend,href:`markets/sector.html?region=${key}&sector=${index}`}));
    r.news.forEach(n => result.push({edition:r.edition,label:n.source,text:n.title,href:`newsroom/article.html?region=${key}&id=${n.index}`}));
  });
  $("#searchResults").innerHTML = result.filter(x=>`${x.label} ${x.text}`.toLowerCase().includes(query)).slice(0,8).map(x=>`<a class="search-result" href="${x.href}"><span>${x.edition.toUpperCase()} · ${x.label}</span>${x.text}<b>↗</b></a>`).join("") || `<div class="search-result">${region==='cn'?'未找到匹配的市场情报。':'No matching intelligence found.'}</div>`;
});

$("#archiveButton").addEventListener("click", () => { window.location.href = `archive/index.html?region=${region}`; });

render();

const reports = window.WANEYE_REPORTS;
let region = "global";
let strategy = "opportunities";
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function render() {
  const r = reports[region];
  document.documentElement.lang = region === "cn" ? "zh" : "en";
  $("#editionLabel").textContent = r.edition.toUpperCase();
  $("#issueLabel").textContent = `MARKET BRIEF / ${r.time}`;
  $("#briefDate").innerHTML = `${r.date.toUpperCase()}<br>${r.time}`;
  $("#scoreValue").textContent = r.score;
  $("#scoreRing").style.setProperty("--score", r.score);
  $("#sentimentLabel").textContent = r.sentiment;
  $("#sourceCount").textContent = r.sources;
  $("#sectorCount").textContent = String(r.sectors.length).padStart(2,"0");
  $("#riskCount").textContent = String(r.risks.length).padStart(2,"0");
  $("#tickerTrack").innerHTML = r.themes.map(x => `<span class="ticker-item">${x}</span>`).join("");

  $("#leadStory").innerHTML = `<span class="story-index">01 / LEAD SIGNAL</span><h3>${r.highlights[0]}</h3><div class="story-meta"><span class="signal-pill">${r.sentiment}</span><span>All ${r.highlights.length} executive highlights · ${r.time} edition</span></div>`;
  $("#briefList").innerHTML = r.highlights.slice(1).map((x,i) => `<article class="brief-item"><span>0${i+2}</span><h3>${x}</h3></article>`).join("");
  $("#sectorGrid").innerHTML = r.sectors.map((s,i) => `<a class="sector-card" href="markets/sector.html?region=${region}&sector=${i}"><div class="sector-top"><span class="kicker">SECTOR SIGNAL</span><span class="direction ${s.tone}">${s.direction.toUpperCase()}</span></div><h3>${s.name}</h3><p>${s.trend}</p><p class="implication">${s.implication}</p><div class="metric"><strong>${s.metric}</strong><small>${s.metricLabel}</small></div><span class="card-link">Open analysis ↗</span></a>`).join("");
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
  $("#strategyGrid").innerHTML = items.map((item,i) => `<article class="strategy-card"><span class="card-number">0${i+1}</span><h3>${item.title}</h3><p>${item.rationale}</p><div class="ticker-pills">${item.tickers.map(t=>`<span>${t}</span>`).join("")}</div><div class="card-foot"><span>${strategy === "opportunities" ? "OPPORTUNITY" : "DEFENSIVE MOVE"}</span><span>${item.horizon}</span></div></article>`).join("");
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
  $("#searchResults").innerHTML = result.slice(0,8).map(x=>`<div class="search-result"><span>${x.edition.toUpperCase()}</span>${x.text}</div>`).join("") || `<div class="search-result">No matching intelligence found.</div>`;
});

$("#archiveButton").addEventListener("click", () => { window.location.href = "archive/index.html"; });

render();

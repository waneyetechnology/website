const REPORTS = window.WANEYE_REPORTS;
const REGION_NAMES = {global:"Global", au:"Australia", cn:"Greater China"};

function query(name, fallback="") {
  return new URLSearchParams(location.search).get(name) || fallback;
}

function safeRegion(value) {
  return REPORTS[value] ? value : "global";
}

function siteHeader(active, root="../") {
  return `<a class="skip-link" href="#main">Skip to content</a><header class="topbar"><a class="brand" href="${root}index.html" aria-label="Waneye home"><svg viewBox="0 0 34 34" aria-hidden="true"><path d="M3 17C6.8 10.7 11.4 7.5 17 7.5S27.2 10.7 31 17c-3.8 6.3-8.4 9.5-14 9.5S6.8 23.3 3 17Z"/><circle cx="17" cy="17" r="5"/><path d="M17 3v3M17 28v3M3 8l3 2M28 24l3 2"/></svg><span>WANEYE</span></a><nav class="primary-nav" aria-label="Primary navigation"><a class="${active==='intelligence'?'active':''}" href="${root}index.html">Intelligence</a><a class="${active==='markets'?'active':''}" href="${root}markets/index.html">Markets</a><a class="${active==='newsroom'?'active':''}" href="${root}newsroom/index.html">Newsroom</a><a class="${active==='archive'?'active':''}" href="${root}archive/index.html">Archive</a></nav><div class="top-actions"><span class="status"><i></i> Live intelligence</span><button class="menu-button" aria-expanded="false" aria-label="Open menu"><span></span><span></span></button></div></header>`;
}

function siteFooter(root="../") {
  return `<footer class="page-footer"><a class="brand footer-brand" href="${root}index.html"><svg viewBox="0 0 34 34" aria-hidden="true"><path d="M3 17C6.8 10.7 11.4 7.5 17 7.5S27.2 10.7 31 17c-3.8 6.3-8.4 9.5-14 9.5S6.8 23.3 3 17Z"/><circle cx="17" cy="17" r="5"/></svg><span>WANEYE</span></a><p>Global vision for smarter finance.</p><p>Analysis is informational and does not constitute investment advice.</p><span>© 2026 WANEYE TECHNOLOGY</span></footer>`;
}

function mountChrome(active, root="../") {
  document.querySelector("#siteHeader").innerHTML = siteHeader(active,root);
  document.querySelector("#siteFooter").innerHTML = siteFooter(root);
  const menu = document.querySelector(".menu-button");
  menu?.addEventListener("click",()=>{
    const open=document.querySelector(".topbar").classList.toggle("menu-open");
    menu.setAttribute("aria-expanded",String(open));
  });
}

function regionFilters(current, href) {
  return Object.keys(REPORTS).map(key=>`<a class="${key===current?'active':''}" href="${href}?region=${key}">${REGION_NAMES[key]}</a>`).join("");
}

function toneBadge(item) {
  return `<span class="direction-badge ${item.tone}">${item.direction.toUpperCase()}</span>`;
}

window.WaneyePage={REPORTS,REGION_NAMES,query,safeRegion,mountChrome,regionFilters,toneBadge};

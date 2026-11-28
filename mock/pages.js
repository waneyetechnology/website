const REPORTS = window.WANEYE_REPORTS;
const REGION_NAMES = {global:"Global", au:"Australia", cn:"大中华区"};

function query(name, fallback="") {
  return new URLSearchParams(location.search).get(name) || fallback;
}

function safeRegion(value) {
  return REPORTS[value] ? value : "global";
}

function siteHeader(active, root="../", lang="en") {
  const zh = lang === "zh";
  const nav = zh ? ["市场情报","市场板块","新闻中心","研究"] : ["Intelligence","Markets","Newsroom","Research"];
  const current = safeRegion(query("region", "global"));
  const file = location.pathname.split("/").pop() || "index.html";
  const editionHref = key => {
    const params = new URLSearchParams(location.search);
    params.set("region", key);
    if (file === "report.html") params.delete("id");
    return `${file}?${params}`;
  };
  const navItem = (name, href, key) => `<a${active === key ? ' class="active" aria-current="page"' : ""} href="${href}">${name}</a>`;

  return `<a class="skip-link" href="#main">${zh ? "跳至正文" : "Skip to content"}</a>
    <header class="topbar">
      <a class="brand" href="${root}index.html?region=${current}" aria-label="Waneye ${zh ? "首页" : "home"}"><img src="${root}favicon.svg" alt=""><span>WANEYE</span></a>
      <nav class="primary-nav" id="primaryNavigation" aria-label="${zh ? "主导航" : "Primary navigation"}">
        ${navItem(nav[0], `${root}index.html?region=${current}`, "intelligence")}
        ${navItem(nav[1], `${root}markets/index.html?region=${current}`, "markets")}
        ${navItem(nav[2], `${root}newsroom/index.html?region=${current}`, "newsroom")}
        ${navItem(nav[3], `${root}archive/index.html?region=${current}`, "archive")}
      </nav>
      <div class="top-actions">
        <nav class="edition-switcher" aria-label="${zh ? "市场版本" : "Market edition"}">
          <a href="${editionHref("global")}"${current === "global" ? ' aria-current="page"' : ""}>Global</a>
          <a href="${editionHref("au")}"${current === "au" ? ' aria-current="page"' : ""}>Australia</a>
          <a href="${editionHref("cn")}"${current === "cn" ? ' aria-current="page"' : ""}>中文</a>
        </nav>
        <span class="status"><i></i>${zh ? "每小时更新" : "Updated hourly"}</span>
        <button class="icon-button" id="searchButton" type="button" aria-haspopup="dialog" aria-controls="searchDialog" aria-label="${zh ? "搜索市场情报" : "Search intelligence"}"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/></svg></button>
        <button class="menu-button" id="menuButton" type="button" aria-controls="primaryNavigation" aria-expanded="false" aria-label="${zh ? "打开菜单" : "Open menu"}"><span></span><span></span></button>
      </div>
    </header>
    <dialog id="searchDialog" aria-labelledby="searchLabel"><form method="dialog"><button type="submit" aria-label="${zh ? "关闭搜索" : "Close search"}">×</button></form><p class="kicker">${zh ? "搜索情报" : "SEARCH INTELLIGENCE"}</p><label id="searchLabel" for="searchInput">${zh ? "搜索所有市场版本的报道、板块与摘要" : "Search reporting, sectors and briefs across all editions"}</label><input id="searchInput" type="search" autocomplete="off" placeholder="${zh ? "例如“人工智能”或“利率”" : "Try “AI”, “rates” or a company name"}"><div id="searchResults" aria-live="polite"></div></dialog>`;
}

function siteFooter(root="../", lang="en") {
  const zh = lang === "zh";
  const current = safeRegion(query("region", "global"));
  return `<footer class="page-footer"><a class="brand footer-brand" href="${root}index.html?region=${current}"><img src="${root}favicon.svg" alt=""><span>WANEYE</span></a><p>${zh ? "全球视野，智慧金融。" : "Global vision for smarter finance."}</p><p>${zh ? "本网站分析仅供参考，不构成投资建议。" : "Analysis is informational and does not constitute investment advice."}</p><span>© 2026 WANEYE TECHNOLOGY</span></footer>`;
}

function searchResultItems(root, lang) {
  const zh = lang === "zh";
  return Object.entries(REPORTS).flatMap(([region, report]) => [
    ...report.highlights.map(text => ({edition: report.edition, label: zh ? "核心摘要" : "Executive brief", text, href: `${root}archive/report.html?region=${region}#executive`})),
    ...report.sectors.map((sector, index) => ({edition: report.edition, label: sector.name, text: sector.trend, href: `${root}markets/sector.html?region=${region}&sector=${index}`})),
    ...report.news.map(story => ({edition: report.edition, label: story.source, text: story.title, href: `${root}newsroom/article.html?region=${region}&id=${story.index}`}))
  ]);
}

function bindSearch(root, lang) {
  const zh = lang === "zh";
  const dialog = document.querySelector("#searchDialog");
  const button = document.querySelector("#searchButton");
  const input = document.querySelector("#searchInput");
  const results = document.querySelector("#searchResults");
  const items = searchResultItems(root, lang);
  let trigger = null;
  button?.addEventListener("click", event => {
    trigger = event.currentTarget;
    dialog.showModal();
    setTimeout(() => input.focus(), 0);
  });
  input?.addEventListener("input", event => {
    const value = event.target.value.trim().toLocaleLowerCase();
    if (!value) {
      results.innerHTML = "";
      return;
    }
    const matched = items.filter(item => `${item.label} ${item.text}`.toLocaleLowerCase().includes(value)).slice(0, 8);
    results.innerHTML = matched.length ? matched.map(item => `<a class="search-result" href="${item.href}"><span>${item.edition.toUpperCase()} · ${item.label}</span>${item.text}<b aria-hidden="true">↗</b></a>`).join("") : `<div class="search-result">${zh ? "未找到匹配的市场情报。" : "No matching intelligence found."}</div>`;
  });
  dialog?.addEventListener("close", () => {
    trigger?.focus();
    trigger = null;
  });
  return dialog;
}

function mountChrome(active, root="../", lang="en") {
  document.documentElement.lang = lang;
  if (lang === "zh") {
    const path = location.pathname.replace(/\/+$/, "");
    const descriptions = {
      "/markets/index.html": "Waneye 市场与板块情报。",
      "/markets/sector.html": "Waneye 板块市场情报与相关报道。",
      "/newsroom/index.html": "Waneye 市场新闻中心与信息来源。",
      "/newsroom/article.html": "Waneye 市场报道来源解读。",
      "/archive/index.html": "Waneye 当前市场研究。",
      "/archive/report.html": "Waneye 完整市场情报报告。"
    };
    const description = Object.entries(descriptions).find(([suffix]) => path.endsWith(suffix))?.[1];
    if (description) document.querySelector('meta[name="description"]').content = description;
  }
  let icon = document.querySelector('link[rel="icon"]');
  if (!icon) {
    icon = document.createElement("link");
    icon.rel = "icon";
    icon.type = "image/svg+xml";
    document.head.appendChild(icon);
  }
  icon.href = `${root}favicon.svg`;
  document.querySelector("#siteHeader").innerHTML = siteHeader(active, root, lang);
  document.querySelector("#siteFooter").innerHTML = siteFooter(root, lang);
  const current = safeRegion(query("region", "global"));
  document.querySelectorAll("a[href]").forEach(link => {
    const href = link.getAttribute("href");
    if (!href || link.closest(".edition-switcher") || href.startsWith("#") || /^(https?:|mailto:|tel:)/.test(href)) return;
    const url = new URL(href, location.href);
    url.searchParams.set("region", current);
    link.setAttribute("href", url.href);
  });
  const menu = document.querySelector("#menuButton");
  const topbar = document.querySelector(".topbar");
  const closeMenu = () => {
    topbar.classList.remove("menu-open");
    menu.setAttribute("aria-expanded", "false");
    menu.setAttribute("aria-label", lang === "zh" ? "打开菜单" : "Open menu");
  };
  menu?.addEventListener("click", () => {
    const open = topbar.classList.toggle("menu-open");
    menu.setAttribute("aria-expanded", String(open));
    menu.setAttribute("aria-label", open ? (lang === "zh" ? "关闭菜单" : "Close menu") : (lang === "zh" ? "打开菜单" : "Open menu"));
  });
  document.querySelectorAll(".primary-nav a").forEach(link => link.addEventListener("click", closeMenu));
  document.addEventListener("click", event => {
    if (topbar.classList.contains("menu-open") && !topbar.contains(event.target)) closeMenu();
  });
  const searchDialog = bindSearch(root, lang);
  document.addEventListener("keydown", event => {
    if (event.key !== "Escape") return;
    closeMenu();
    if (searchDialog?.open) searchDialog.close();
  });
}

window.WaneyePage = {REPORTS, REGION_NAMES, query, safeRegion, mountChrome};

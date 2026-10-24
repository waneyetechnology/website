(() => {
  "use strict";

  const isChinese = () => document.documentElement.lang.toLowerCase().startsWith("zh");

  function initialiseMenu() {
    const button = document.querySelector("#menuButton");
    const topbar = document.querySelector(".topbar");
    if (!button || !topbar) return;

    const close = () => {
      topbar.classList.remove("menu-open");
      button.setAttribute("aria-expanded", "false");
      button.setAttribute("aria-label", isChinese() ? "打开菜单" : "Open menu");
    };
    button.addEventListener("click", () => {
      const open = topbar.classList.toggle("menu-open");
      button.setAttribute("aria-expanded", String(open));
      button.setAttribute("aria-label", open ? (isChinese() ? "关闭菜单" : "Close menu") : (isChinese() ? "打开菜单" : "Open menu"));
    });
    topbar.querySelectorAll(".primary-nav a").forEach((link) => link.addEventListener("click", close));
    document.addEventListener("click", (event) => {
      if (topbar.classList.contains("menu-open") && !topbar.contains(event.target)) close();
    });
    return close;
  }

  function initialiseStrategy() {
    const buttons = Array.from(document.querySelectorAll("[data-strategy-button]"));
    const panels = Array.from(document.querySelectorAll("[data-strategy-panel]"));
    if (!buttons.length || !panels.length) return;

    panels.forEach((panel) => {
      panel.id = `strategy-${panel.dataset.strategyPanel}`;
    });
    const select = (name) => {
      buttons.forEach((button) => {
        const selected = button.dataset.strategyButton === name;
        button.classList.toggle("active", selected);
        button.setAttribute("aria-pressed", String(selected));
      });
      panels.forEach((panel) => {
        panel.hidden = panel.dataset.strategyPanel !== name;
      });
    };
    buttons.forEach((button) => button.addEventListener("click", () => select(button.dataset.strategyButton)));
    select(buttons[0].dataset.strategyButton);
  }

  function initialiseSearch() {
    const dialog = document.querySelector("#searchDialog");
    const trigger = document.querySelector("#searchButton");
    const input = document.querySelector("#searchInput");
    const results = document.querySelector("#searchResults");
    if (!dialog || !trigger || !input || !results || typeof dialog.showModal !== "function") return;

    let rawItems = [];
    const embeddedIndex = document.querySelector("#searchIndex");
    if (embeddedIndex?.textContent) {
      try {
        const parsed = JSON.parse(embeddedIndex.textContent);
        if (Array.isArray(parsed)) rawItems = parsed;
      } catch (_error) {
        rawItems = [];
      }
    }
    if (!rawItems.length) {
      rawItems = Array.from(document.querySelectorAll("[data-search-item]")).map((node) => ({
        title: node.dataset.searchTitle || "",
        href: node.dataset.searchHref || "#news",
      }));
    }
    const seenItems = new Set();
    const items = rawItems.reduce((index, rawItem) => {
      const title = String(rawItem?.title || "").trim();
      const href = String(rawItem?.href || "").trim();
      if (!title || !href) return index;
      const key = `${title.toLocaleLowerCase()}\u0000${href}`;
      if (seenItems.has(key)) return index;
      seenItems.add(key);
      index.push({
        title,
        href,
        label: String(rawItem?.label || (isChinese() ? "来源报道" : "SOURCE REPORTING")).trim(),
        edition: String(rawItem?.edition || "").trim(),
        keywords: String(rawItem?.keywords || "").trim(),
      });
      return index;
    }, []);
    let lastTrigger = null;
    trigger.addEventListener("click", (event) => {
      lastTrigger = event.currentTarget;
      if (!dialog.open) dialog.showModal();
      window.setTimeout(() => input.focus(), 0);
    });
    dialog.addEventListener("close", () => {
      lastTrigger?.focus();
      lastTrigger = null;
    });
    input.addEventListener("input", () => {
      const query = input.value.trim().toLocaleLowerCase();
      results.replaceChildren();
      if (!query) return;
      const matches = items.filter((item) => (
        `${item.title} ${item.label} ${item.edition} ${item.keywords}`.toLocaleLowerCase().includes(query)
      )).slice(0, 8);
      if (!matches.length) {
        const empty = document.createElement("p");
        empty.className = "search-result";
        empty.textContent = isChinese() ? "未找到匹配的市场情报。" : "No matching intelligence found.";
        results.append(empty);
        return;
      }
      matches.forEach((item) => {
        const link = document.createElement("a");
        link.className = "search-result";
        link.href = item.href;
        const label = document.createElement("span");
        label.textContent = [item.edition, item.label].filter(Boolean).join(" · ");
        const arrow = document.createElement("b");
        arrow.setAttribute("aria-hidden", "true");
        arrow.textContent = "↗";
        link.append(label, document.createTextNode(item.title), arrow);
        results.append(link);
      });
    });
    return dialog;
  }

  function initialise() {
    const closeMenu = initialiseMenu();
    const dialog = initialiseSearch();
    initialiseStrategy();
    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;
      closeMenu?.();
      if (dialog?.open) dialog.close();
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialise, { once: true });
  else initialise();
})();

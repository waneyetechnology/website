/* Dependency-free, DPR-aware canvas benchmark renderer. */
window.mountChart = function (W) {
  const { $, $$, r, t, esc, colors, delta } = W,
    canvas = $("#indexCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let selected = 0,
    frame = "1D",
    compare = false,
    hover = null,
    hidden = new Set(),
    width = 0,
    height = 285;
  const fmt = (n) => n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  function calendarStamp(n) {
    const start = Date.UTC(2026, frame === "3M" ? 5 : frame === "1M" ? 6 : 7, frame === "3M" ? 1 : frame === "1M" ? 31 : 24);
    const d = new Date(start + Math.round(n / 95 * (Date.UTC(2026, 7, 28) - start) / 86400000) * 86400000);
    return W.zh ? `${d.getUTCMonth() + 1}月${d.getUTCDate()}日` : `${d.getUTCDate()} ${["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][d.getUTCMonth()]}`;
  }
  function selectedItems() {
    return compare ? r.compare.filter((i) => !hidden.has(i.symbol)) : [r.indices[selected]];
  }
  function update() {
    const item = r.indices[selected],
      a = item.series[frame];
    $("#chartQuote").innerHTML =
      `<strong>${esc(item.name)}</strong><b class="mono quote">${item.price}</b>${delta(item)}`;
    $$("[data-index]").forEach((b) => {
      const active = +b.dataset.index === selected;
      b.classList.toggle("active", active);
      b.setAttribute("aria-pressed", active);
    });
    $$("[data-frame]").forEach((b) => {
      const active = b.dataset.frame === frame;
      b.classList.toggle("active", active);
      b.setAttribute("aria-pressed", active);
    });
    $("#compare").classList.toggle("active", compare);
    $("#compare").setAttribute("aria-pressed", compare);
    $("#chartLegend").innerHTML = compare
      ? r.compare
          .map(
            (i, n) =>
              `<button data-legend="${i.symbol}" aria-pressed="${!hidden.has(i.symbol)}" style="--series:${colors[n]}" class="legend ${hidden.has(i.symbol) ? "disabled" : ""}"><i></i>${esc(i.name)}</button>`,
          )
          .join("")
      : "";
    $("#sessionStats").innerHTML = [
      [t("Open", "开盘"), a[0]],
      [t("High", "最高"), Math.max(...a)],
      [t("Low", "最低"), Math.min(...a)],
      [t("Prev close", "昨收"), item.previous],
      [t("Range", "振幅"), Math.max(...a) - Math.min(...a)],
    ]
      .map(([label, value]) => `<div><small>${label}</small><span class="mono">${fmt(value)}</span></div>`)
      .join("") + `<div class="day-range"><small>${frame === "1D" ? t("Day range · Last", "日内区间 · 最新") : t("Period range · Last", "区间范围 · 最新")}</small><div class="range-track"><i style="left:${100 * (a[95] - Math.min(...a)) / (Math.max(...a) - Math.min(...a) || 1)}%"></i></div></div>`;
    draw();
  }
  function draw() {
    if (!width) return;
    const style = getComputedStyle(document.documentElement),
      ink = style.getPropertyValue("--muted"),
      border = style.getPropertyValue("--border");
    ctx.clearRect(0, 0, width, height);
    ctx.font = '11px "JetBrains Mono", monospace';
    const left = 12,
      right = width - 76,
      top = 18,
      bottom = height - 30;
    const items = selectedItems(),
      paths = items.map((item) => {
        const a = item.series[frame];
        return compare ? a.map((v) => (v / a[0] - 1) * 100) : a;
      });
    const values = paths.flat();
    if (!compare) values.push(r.indices[selected].previous);
    else values.push(0);
    let low = Math.min(...values),
      high = Math.max(...values);
    const pad = (high - low || 1) * 0.16;
    low -= pad;
    high += pad;
    const x = (n) => left + (n / 95) * (right - left),
      y = (v) => bottom - ((v - low) / (high - low)) * (bottom - top);
    const pills = compare ? paths.map((a, j) => ({ value: a[95], color: colors[r.compare.indexOf(items[j])], py: y(a[95]) })).sort((a, b) => a.py - b.py) : [];
    pills.forEach((pill, i) => { pill.py = Math.max(top + 8, pill.py, i ? pills[i - 1].py + 19 : top + 8); });
    for (let i = pills.length - 1; i >= 0; i--) pills[i].py = Math.min(pills[i].py, i === pills.length - 1 ? bottom - 8 : pills[i + 1].py - 19);
    const clearLabel = (py) => pills.every(pill => Math.abs(py - pill.py) >= 11);
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 5]);
    for (let j = 0; j < 5; j++) {
      const v = low + ((high - low) * j) / 4,
        py = y(v);
      ctx.strokeStyle = border;
      ctx.beginPath();
      ctx.moveTo(left, py);
      ctx.lineTo(right, py);
      ctx.stroke();
      ctx.fillStyle = ink;
      if (!compare || (Math.abs(py - y(0)) > 14 && clearLabel(py))) ctx.fillText(`${fmt(v)}${compare ? "%" : ""}`, right + 8, py + 4);
    }
    ctx.setLineDash([]);
    const labels = frame === "1D" ? ["09:30", "11:08", "12:45", "14:23", "16:00"] : [0, 1, 2, 3, 4].map(j => calendarStamp(j * 95 / 4));
    labels.forEach((label, j) => {
      if (width < 450 && j % 2) return;
      ctx.textAlign = j === 0 ? "left" : j === 4 ? "right" : "center";
      ctx.fillStyle = ink;
      ctx.fillText(
        label,
        x((j * 95) / 4),
        height - 8,
      );
    });
    ctx.textAlign = "left";
    {
      ctx.strokeStyle = ink;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(left, y(compare ? 0 : r.indices[selected].previous));
      ctx.lineTo(right, y(compare ? 0 : r.indices[selected].previous));
      ctx.stroke();
      ctx.setLineDash([]);
      if (compare && clearLabel(y(0))) { ctx.fillStyle = ink; ctx.fillText("0.00%", right + 8, y(0) + 4); }
    }
    if (!compare) {
      const a = paths[0], moves = a.map((v, n) => Math.abs(v - a[Math.max(0, n - 1)])), max = Math.max(...moves) || 1;
      a.forEach((v, n) => {
        const h = (0.15 + moves[n] / max * .85) * (bottom - top) * .18;
        ctx.fillStyle = v >= a[Math.max(0, n - 1)] ? "#10b98130" : "#f43f5e30";
        ctx.fillRect(x(n), bottom - h, Math.max(1, (right - left) / 96 - 1), h);
      });
    }
    paths.forEach((a, j) => {
      const color = compare ? colors[r.compare.indexOf(items[j])] : items[j].direction === "up" ? "#10b981" : "#f43f5e";
      ctx.beginPath();
      a.forEach((v, n) => (n ? ctx.lineTo(x(n), y(v)) : ctx.moveTo(x(n), y(v))));
      if (!compare) {
        ctx.lineTo(right, bottom);
        ctx.lineTo(left, bottom);
        ctx.closePath();
        const fill = ctx.createLinearGradient(0, top, 0, bottom);
        fill.addColorStop(0, color + "40");
        fill.addColorStop(1, color + "00");
        ctx.fillStyle = fill;
        ctx.fill();
      }
      ctx.beginPath();
      a.forEach((v, n) => (n ? ctx.lineTo(x(n), y(v)) : ctx.moveTo(x(n), y(v))));
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.8;
      ctx.stroke();
      if (hover !== null) {
        const px = x(hover),
          py = y(a[hover]);
        ctx.strokeStyle = ink;
        ctx.lineWidth = 1;
        ctx.setLineDash([3, 4]);
        ctx.beginPath();
        ctx.moveTo(px, top);
        ctx.lineTo(px, bottom);
        if (!compare) {
          ctx.moveTo(left, py);
          ctx.lineTo(right, py);
        }
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.shadowBlur = 10;
        ctx.shadowColor = color;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(px, py, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
      }
    });
    const n = hover ?? 95;
    const minutes = 570 + Math.round((n / 95) * 390);
    const stamp =
      frame === "1D"
        ? `${String(Math.floor(minutes / 60)).padStart(2, "0")}:${String(minutes % 60).padStart(2, "0")}`
        : calendarStamp(n);
    pills.forEach((pill) => {
      ctx.fillStyle = pill.color;
      ctx.fillRect(right + 3, pill.py - 8, 72, 17);
      ctx.fillStyle = "#090b10";
      ctx.fillText(`${pill.value >= 0 ? "+" : ""}${pill.value.toFixed(2)}%`, right + 6, pill.py + 4);
    });
    const ranked = [...items].sort((a, b) => b.series[frame][n] / b.series[frame][0] - a.series[frame][n] / a.series[frame][0]);
    $("#chartHud").innerHTML = (compare ? `<span>${stamp} ·</span>` : "") + ranked.map(item => {
      const a = item.series[frame], change = (a[n] / a[0] - 1) * 100;
      return `<span style="color:${compare ? colors[r.compare.indexOf(item)] : "var(--ink)"}">${esc(item.symbol)} ${compare ? "" : `· ${stamp} · `}${fmt(a[n])} <span class="${change >= 0 ? "up" : "down"}">${change >= 0 ? "+" : ""}${change.toFixed(2)}%</span> ${compare ? "" : t("vs open", "较开盘")}</span>`;
    }).join("");
  }
  const resize = () => {
    width = canvas.getBoundingClientRect().width;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw();
  };
  new ResizeObserver(resize).observe(canvas);
  window.addEventListener("themechange", draw);
  canvas.addEventListener("pointermove", (e) => {
    const rect = canvas.getBoundingClientRect();
    hover = Math.max(0, Math.min(95, Math.round(((e.clientX - rect.left - 12) / (width - 88)) * 95)));
    draw();
  });
  canvas.addEventListener("pointerleave", () => {
    hover = null;
    draw();
  });
  canvas.addEventListener("keydown", (e) => {
    if (["ArrowLeft", "ArrowRight"].includes(e.key)) {
      e.preventDefault();
      hover = Math.max(0, Math.min(95, (hover ?? 95) + (e.key === "ArrowLeft" ? -1 : 1)));
      draw();
    }
  });
  document.addEventListener("click", (e) => {
    const index = e.target.closest("[data-index],[data-focus-index]"),
      f = e.target.closest("[data-frame]"),
      legend = e.target.closest("[data-legend]");
    if (index) {
      selected = Number(index.dataset.index ?? index.dataset.focusIndex);
      compare = false;
      hover = null;
      update();
      if (index.hasAttribute("data-focus-index"))
        $("#benchmark").scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
    if (f) {
      frame = f.dataset.frame;
      hover = null;
      update();
    }
    if (e.target.closest("#compare")) {
      compare = !compare;
      update();
    }
    if (legend) {
      const s = legend.dataset.legend;
      if (hidden.has(s)) hidden.delete(s);
      else if (hidden.size < r.compare.length - 1) hidden.add(s);
      update();
    }
  });
  update();
  resize();
};

/*
 * Compatibility entry point for previously generated pages.  Current Jinja
 * templates load waneye.js directly; keeping this tiny loader avoids leaving
 * an obsolete canvas/Tailwind interaction bundle in deployed static assets.
 */
(() => {
  if (document.querySelector('script[src*="waneye.js"]')) return;
  const script = document.createElement("script");
  script.src = new URL("waneye.js", document.currentScript?.src || location.href).href;
  document.head.append(script);
})();

/**
 * Cloudflare Worker: geo.waneye.com
 *
 * Returns the visitor's country code using Cloudflare's own edge data (request.cf.country).
 * This is the last-resort fallback in the geo-redirect chain — it has no third-party
 * dependency and works as long as Cloudflare itself is reachable (which covers 99.9%+ of cases).
 *
 * Deployment steps:
 *   1. In Cloudflare Dashboard → Workers & Pages → Create Worker
 *   2. Paste this file, deploy as "waneye-geo" (or any name)
 *   3. Add a Custom Domain: geo.waneye.com (requires waneye.com on Cloudflare DNS)
 *   4. That's it — the geo-redirect in index.html already calls https://geo.waneye.com/
 *
 * Response: { "cc": "CN" }   (ISO 3166-1 alpha-2 country code, or "" if unknown)
 *
 * CORS: restricted to waneye.com origins only.
 */

const ALLOWED_ORIGINS = [
  'https://waneye.com',
  'https://www.waneye.com',
];

export default {
  async fetch(request) {
    const origin = request.headers.get('Origin') || '';
    const corsOrigin = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];

    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: corsHeaders(corsOrigin),
      });
    }

    const cc = (request.cf && request.cf.country) ? request.cf.country : '';

    return new Response(JSON.stringify({ cc }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store',
        ...corsHeaders(corsOrigin),
      },
    });
  },
};

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Max-Age': '86400',
  };
}

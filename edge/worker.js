// Tiny dynamic front for the addon. Needed because Stremio usually asks for
//   /subtitles/<type>/<id>/videoHash=...&videoSize=...&filename=....json
// and a static host can't answer arbitrary extra-args paths. This worker strips
// the extra args and answers from the static index built by scripts/build.py.
// Works on Cloudflare Workers and Deno Deploy (both support `export default { fetch }`).
const PAGES = "https://maayanyosef.github.io/stremio-hebrew-subs";
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
};
const json = (body, maxAge = 300) =>
  new Response(JSON.stringify(body), {
    headers: { ...CORS, "Content-Type": "application/json; charset=utf-8", "Cache-Control": `public, max-age=${maxAge}` },
  });

export default {
  async fetch(request) {
    if (request.method === "OPTIONS") return new Response(null, { headers: CORS });
    const path = new URL(request.url).pathname; // keep raw: extra args may contain %2F
    if (path === "/" || path === "/manifest.json") {
      const r = await fetch(`${PAGES}/manifest.json`, { cf: { cacheTtl: 300 } });
      return json(await r.json());
    }
    // /subtitles/<type>/<id>.json  or  /subtitles/<type>/<id>/<extra>.json
    const m = path.match(/^\/subtitles\/(movie|series)\/([^/]+?)(?:\/[^/]*)?\.json$/);
    if (m) {
      const r = await fetch(`${PAGES}/index.json`, { cf: { cacheTtl: 300 } });
      const index = r.ok ? await r.json() : {};
      const entry = index[decodeURIComponent(m[2])];
      return json({ subtitles: entry && entry.type === m[1] ? entry.subtitles : [] });
    }
    return new Response("Not found", { status: 404, headers: CORS });
  },
};

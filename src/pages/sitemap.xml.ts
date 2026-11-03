import type { APIRoute } from "astro";
import { BASE, LANGS, allPages, url } from "../lib/site";

/** sitemap.xml: every regular page, in the same order as the page list. */
export const GET: APIRoute = () => {
  const locs = allPages().map((p) => `<url><loc>${BASE}${(LANGS[p.lang].prefix + url(p.key, "en").slice(1))}</loc></url>\n`);
  const xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + locs.join("") + "</urlset>\n";
  return new Response(xml, { headers: { "Content-Type": "application/xml" } });
};

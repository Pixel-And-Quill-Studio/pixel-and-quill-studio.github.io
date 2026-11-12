import type { APIRoute } from "astro";
import { PUBLISHED, DEFAULT, ORIGIN, allPages, url } from "../lib/site";

/** Absolute page URL, matching the on-page canonical. */
function loc(key: string, lang: string): string {
  return ORIGIN + url(key, lang);
}

/** sitemap.xml: every regular page, with xhtml:link alternates for all locales plus x-default. */
export const GET: APIRoute = () => {
  const body = allPages().map((p) => {
    const links = PUBLISHED.map((c) => `    <xhtml:link rel="alternate" hreflang="${c}" href="${loc(p.key, c)}"/>`).join("\n")
      + `\n    <xhtml:link rel="alternate" hreflang="x-default" href="${loc(p.key, DEFAULT)}"/>`;
    return `  <url>\n    <loc>${loc(p.key, p.lang)}</loc>\n${links}\n  </url>\n`;
  });
  const xml =
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n' +
    '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' +
    body.join("") +
    "</urlset>\n";
  return new Response(xml, { headers: { "Content-Type": "application/xml" } });
};

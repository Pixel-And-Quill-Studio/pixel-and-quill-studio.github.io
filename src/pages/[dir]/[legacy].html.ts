import type { APIRoute } from "astro";
import { LEGACY, ORIGIN, t, legacyTarget } from "../../lib/site";

/** Lightweight redirect stubs for old URLs (see LEGACY in src/lib/site.ts). */
export function getStaticPaths() {
  return Object.keys(LEGACY).filter((o) => o.split("/").length === 2).map((old) => ({ params: { dir: old.split("/")[0], legacy: old.split("/")[1].replace(/\.html$/, "") }, props: { old } }));
}

const escapeHtml = (v: string) =>
  v.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#x27;");

export const GET: APIRoute = ({ props }) => {
  const { target, lang } = legacyTarget(props.old as string);
  const full = ORIGIN + target;
  const text = escapeHtml(t(lang, "redirect_text"));
  const body = `<!doctype html>
<html lang="${lang}"><head><meta charset="utf-8"><meta name="google-adsense-account" content="ca-pub-5227293216340878"><meta name="robots" content="noindex">
<title>${text}</title>
<link rel="canonical" href="${full}"><meta http-equiv="refresh" content="0; url=${target}">
<script>location.replace(${JSON.stringify(target)}+location.hash)</script></head>
<body><p>${text} <a href="${target}">${full}</a></p></body></html>
`;
  return new Response(body, { headers: { "Content-Type": "text/html; charset=utf-8" } });
};

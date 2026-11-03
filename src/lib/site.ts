/**
 * Site data and helpers shared by every page.
 *
 * Inputs (all under src/data/):
 *   site.json            studio identity and the list of languages
 *   games.json           the games (one entry per game)
 *   i18n/<lang>.json     interface strings (missing keys fall back to English)
 *   content/legal/       studio-wide legal documents (<doc>.<lang>.md)
 *   content/games/       game-specific details (<slug>.<lang>.md)
 */
import fs from "node:fs";
import path from "node:path";
import { marked } from "marked";
import siteData from "../data/site.json";
import gamesData from "../data/games.json";

export const DATA_DIR = path.resolve("src/data");
export const SITE: any = siteData;
export const GAMES: any[] = (gamesData as any).games;
export const BASE = SITE.url.replace(/\/+$/, "") + "/";
export const ORIGIN = BASE.replace(/\/$/, "");
export const DEFAULT: string = SITE.default_language;
export const LANGS: Record<string, any> = Object.fromEntries(SITE.languages.map((l: any) => [l.code, l]));
export const PUBLISHED: string[] = SITE.languages.filter((l: any) => l.published).map((l: any) => l.code);

// Public token for Facebook domain verification (home pages only).
export const FB_DOMAIN_VERIFICATION = "z5867vdmxg2tzpp1zln0nvqnqm39xi";

// ---------- Interface strings ----------
const I18N: Record<string, any> = {};
for (const code of Object.keys(LANGS)) {
  const f = path.join(DATA_DIR, "i18n", `${code}.json`);
  I18N[code] = fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, "utf-8")) : {};
}

/** Interface string with fallback to the default language. */
export function t(lang: string, key: string): any {
  return I18N[lang]?.[key] ?? I18N[DEFAULT][key];
}

/** Optional interface string without fallback. */
export function tOwn(lang: string, key: string): any {
  return I18N[lang]?.[key];
}

/** Pick a localized value from a {lang: value} object, falling back to English. */
export function loc(value: any, lang: string): any {
  if (value && typeof value === "object" && !Array.isArray(value)) return value[lang] ?? value[DEFAULT];
  return value;
}

// ---------- Pages and URLs ----------
export const PAGES: Record<string, string> = {
  home: "",
  games: "games/",
  contact: "contact/",
  legal: "legal-notice/",
  privacy: "privacy/",
  terms: "terms/",
};
for (const g of GAMES) {
  PAGES[`game:${g.slug}`] = `${g.slug}/`;
  // Game-specific legal documents, e.g. /one-last-heist/privacy/
  for (const doc of Object.keys(g.legal_docs ?? {})) PAGES[`game:${g.slug}:${doc}`] = `${g.slug}/${doc}/`;
}

/** Root-absolute URL of a page in a language, e.g. /fr/privacy/. */
export function url(page: string, lang: string): string {
  return "/" + LANGS[lang].prefix + PAGES[page];
}

// Old URLs (French at the root, English as *-en.html) that must keep working.
export const LEGACY: Record<string, [string, string]> = {
  "en.html": ["home", "en"],
  "jeux/index.html": ["games", "fr"],
  "contact.html": ["contact", "fr"],
  "contact-en.html": ["contact", "en"],
  "mentions-legales.html": ["legal", "fr"],
  "legal-notice.html": ["legal", "en"],
};
for (const g of GAMES) {
  for (const [old, target] of Object.entries<any>(g.legacy_paths ?? {})) LEGACY[old] = [target.page, target.lang];
}

/** Target URL and language of a legacy path (unpublished languages fall back to the default). */
export function legacyTarget(old: string): { target: string; lang: string } {
  let [key, lang] = LEGACY[old];
  if (!PUBLISHED.includes(lang)) lang = DEFAULT;
  return { target: url(key, lang), lang };
}

// ---------- Markdown ----------
/** Path of a localized Markdown file (pattern relative to src/data), falling back to the default language. */
export function localizedFile(pattern: string, lang: string): string {
  const p = path.join(DATA_DIR, pattern.replace("{lang}", lang));
  return fs.existsSync(p) ? p : path.join(DATA_DIR, pattern.replace("{lang}", DEFAULT));
}

/** Point root-absolute links to studio pages at the right language. */
function localizeLinks(body: string, lang: string): string {
  const prefix = LANGS[lang].prefix;
  if (!prefix) return body;
  for (const suffix of Object.values(PAGES)) {
    if (suffix) body = body.split(`href="/${suffix}"`).join(`href="/${prefix}${suffix}"`);
  }
  return body;
}

export function md(file: string, lang: string): string {
  const html = marked.parse(fs.readFileSync(file, "utf-8"), { async: false, gfm: true }) as string;
  return localizeLinks(html, lang);
}

// ---------- Game helpers ----------
/** Status label: the game's own label (e.g. a release month) or the generic one. */
export function statusText(g: any, lang: string): string {
  if (g.status_label) return loc(g.status_label, lang);
  return t(lang, "status")[g.status ?? "coming_soon"];
}

/** Short badge text (fits on one line on phones), else the status label. */
export function badgeText(g: any, lang: string): string {
  return g.status_badge ? loc(g.status_badge, lang) : statusText(g, lang);
}

// ---------- Language detection ----------
/** JSON with ", " and ": " separators (keeps the inline script byte-identical to the previous generator). */
function spacedJson(v: any): string {
  if (Array.isArray(v)) return "[" + v.map(spacedJson).join(", ") + "]";
  if (v && typeof v === "object") return "{" + Object.entries(v).map(([k, x]) => `${JSON.stringify(k)}: ${spacedJson(x)}`).join(", ") + "}";
  return JSON.stringify(v);
}

/** Inline script: saved choice first, then browser languages (default-language pages only). */
export function langScript(page: string, lang: string): string {
  const alternates = Object.fromEntries(PUBLISHED.map((c) => [c.toLowerCase(), url(page, c)]));
  const supported = Object.keys(LANGS).map((c) => c.toLowerCase());
  const isDefault = lang === DEFAULT ? "true" : "false";
  return (
    "(function(){try{" +
    `var A=${spacedJson(alternates)},S=${spacedJson(supported)},cur=${JSON.stringify(lang.toLowerCase())},D=${isDefault};` +
    "var want=null,s=localStorage.getItem('pq-lang');" +
    "if(s&&A[s]){want=s}else if(D){" +
    "var L=navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||''];" +
    "for(var i=0;i<L.length&&!want;i++){var l=(L[i]||'').toLowerCase(),b=l.split('-')[0];" +
    "var c=S.indexOf(l)>=0?l:(b==='pt'?'pt-br':(S.indexOf(b)>=0?b:null));" +
    "if(c){want=A[c]?c:'en'}}}" +
    "if(want&&want!==cur&&A[want]){location.replace(A[want]+location.hash)}" +
    "}catch(e){}})();"
  );
}

export const SWITCH_SCRIPT =
  "document.querySelectorAll('a[data-lang]').forEach(function(a){" +
  "a.addEventListener('click',function(){try{localStorage.setItem('pq-lang',a.dataset.lang)}catch(e){}})});";

// ---------- Page list (also drives the sitemap) ----------
export type PageEntry = { key: string; lang: string; kind: string; game?: any; doc?: string };

export function allPages(): PageEntry[] {
  const out: PageEntry[] = [];
  for (const lang of PUBLISHED) {
    out.push({ key: "home", lang, kind: "home" });
    out.push({ key: "games", lang, kind: "games" });
    out.push({ key: "contact", lang, kind: "contact" });
    for (const k of ["legal", "privacy", "terms"]) out.push({ key: k, lang, kind: "legal" });
    for (const g of GAMES) {
      out.push({ key: `game:${g.slug}`, lang, kind: "game", game: g });
      for (const d of Object.keys(g.legal_docs ?? {}))
        out.push({ key: `game:${g.slug}:${d}`, lang, kind: "gamedoc", game: g, doc: d });
    }
  }
  return out;
}

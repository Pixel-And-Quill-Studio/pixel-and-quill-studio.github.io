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
  press: "press/",
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


/** Google Play listing, with a language `hl` parameter. English keeps the canonical URL (no `hl`). */
export function playStoreUrl(g: any, lang: string): string | null {
  const play = g?.store?.google_play;
  if (!play) return null;
  const hl: Record<string, string> = {
    fr: "fr",
    es: "es",
    "pt-BR": "pt_BR",
    de: "de",
    it: "it",
    ja: "ja",
    ko: "ko",
  };
  if (!hl[lang]) return play;
  const u = new URL(play);
  u.searchParams.set("hl", hl[lang]);
  return u.toString();
}

/** Official localized Google Play badge (PNG), stored under public/assets/badges/. */
export function playBadgeSrc(lang: string): string {
  const code = LANGS[lang] ? lang : DEFAULT;
  return `/assets/badges/google-play-${code}.png`;
}

// ---------- Language detection ----------
/** JSON with ", " and ": " separators (keeps the inline script byte-identical to the previous generator). */
function spacedJson(v: any): string {
  if (Array.isArray(v)) return "[" + v.map(spacedJson).join(", ") + "]";
  if (v && typeof v === "object") return "{" + Object.entries(v).map(([k, x]) => `${JSON.stringify(k)}: ${spacedJson(x)}`).join(", ") + "}";
  return JSON.stringify(v);
}

/** Inline script: saved choice first, then browser languages (default-language pages only).
 *  Search crawlers and social-preview bots are never redirected, so they can index every locale. */
export function langScript(page: string, lang: string): string {
  const alternates = Object.fromEntries(PUBLISHED.map((c) => [c.toLowerCase(), url(page, c)]));
  const supported = Object.keys(LANGS).map((c) => c.toLowerCase());
  const isDefault = lang === DEFAULT ? "true" : "false";
  return (
    "(function(){try{" +
    "if(/bot|crawler|spider|slurp|bingpreview|facebookexternalhit|embedly|pinterest|whatsapp|telegram|applebot|yandex|baidu|duckduck|semrush|ahrefs|ia_archiver|twitterbot|linkedinbot|discordbot|google-inspectiontool|storebot-google|googleother|google-read-aloud|mediapartners-google|bytespider/i.test(navigator.userAgent||''))return;" +
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
  "a.addEventListener('click',function(){try{localStorage.setItem('pq-lang',a.dataset.lang)}catch(e){}})});" +
  "document.querySelectorAll('details.lang-drop').forEach(function(d){var sm=d.querySelector('summary');" +
  "d.addEventListener('toggle',function(){sm.setAttribute('aria-expanded',d.open?'true':'false')});" +
  "d.addEventListener('keydown',function(e){if(e.key==='Escape'&&d.open){d.open=false;sm.focus()}});" +
  "document.addEventListener('click',function(e){if(d.open&&!d.contains(e.target))d.open=false})});";

// ---------- Audience measurement (loaded only after consent) ----------
export const GA_MEASUREMENT_ID = "G-7VHPQT581J";
const CONSENT_KEY = "pq-cookie-consent";
const CONSENT_TTL_MS = 183 * 24 * 60 * 60 * 1000; // 6 months (CNIL allows 13; the shorter period is used)
const GA_COOKIE_EXPIRES = 33696000; // 13 months in seconds

/** Early head script: hide the banner for returning visitors before first paint. Does not load gtag. */
export const CONSENT_BOOT_SCRIPT =
  "(function(){try{" +
  `var k=${JSON.stringify(CONSENT_KEY)},raw=localStorage.getItem(k);` +
  "if(!raw)return;var d=JSON.parse(raw);" +
  "if(!d||!d.choice||!d.at)return;" +
  `if(Date.now()-d.at>${CONSENT_TTL_MS}){localStorage.removeItem(k);return;}` +
  "document.documentElement.setAttribute('data-pq-consent',d.choice);" +
  "}catch(e){}})();";

/** Banner logic: store the choice for 6 months, load gtag.js only after accept, delete GA cookies on withdrawal. */
export const COOKIE_SCRIPT =
  "(function(){" +
  `var KEY=${JSON.stringify(CONSENT_KEY)},TTL=${CONSENT_TTL_MS},ID=${JSON.stringify(GA_MEASUREMENT_ID)},EXPIRES=${GA_COOKIE_EXPIRES};` +
  "function getChoice(){try{var raw=localStorage.getItem(KEY);if(!raw)return null;var d=JSON.parse(raw);" +
  "if(!d||!d.choice||!d.at)return null;if(Date.now()-d.at>TTL){localStorage.removeItem(KEY);return null;}return d.choice;}catch(e){return null}}" +
  "function saveChoice(choice){try{localStorage.setItem(KEY,JSON.stringify({choice:choice,at:Date.now()}))}catch(e){}" +
  "document.documentElement.setAttribute('data-pq-consent',choice);" +
  "document.documentElement.removeAttribute('data-pq-banner');}" +
  "function showBanner(){document.documentElement.setAttribute('data-pq-banner','open');" +
  "var b=document.getElementById('pq-cookies');if(b){b.removeAttribute('hidden');}" +
  "var btn=document.getElementById('pq-cookie-accept');if(btn)btn.focus();}" +
  "function hideBanner(){document.documentElement.removeAttribute('data-pq-banner');}" +
  "function deleteGaCookies(){var parts=document.cookie.split(';'),host=location.hostname,domains=[host,'.'+host];" +
  "if(host.indexOf('www.')===0){var root=host.slice(4);domains.push(root,'.'+root)}" +
  "for(var i=0;i<parts.length;i++){var name=parts[i].split('=')[0].trim();" +
  "if(name==='_ga'||name.indexOf('_ga_')===0||name==='_gid'||name==='_gat'||name.indexOf('_gat_')===0){" +
  "document.cookie=name+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;SameSite=Lax';" +
  "for(var j=0;j<domains.length;j++){document.cookie=name+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain='+domains[j]+';SameSite=Lax'}}}}" +
  "function loadGA(){if(window.__pqGaLoaded)return;window.__pqGaLoaded=true;" +
  "window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}window.gtag=gtag;" +
  "gtag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});" +
  "gtag('consent','update',{analytics_storage:'granted',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});" +
  "gtag('js',new Date());" +
  "gtag('config',ID,{anonymize_ip:true,allow_google_signals:false,allow_ad_personalization_signals:false,cookie_expires:EXPIRES,cookie_flags:'SameSite=Lax;Secure'});" +
  "var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+ID;document.head.appendChild(s);}" +
  "function denyGA(){if(window.gtag){window.gtag('consent','update',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});}deleteGaCookies();}" +
  "function accept(){saveChoice('accepted');hideBanner();loadGA();}" +
  "function refuse(){saveChoice('refused');hideBanner();denyGA();}" +
  "function init(){var a=document.getElementById('pq-cookie-accept'),r=document.getElementById('pq-cookie-refuse');" +
  "if(a)a.addEventListener('click',accept);if(r)r.addEventListener('click',refuse);" +
  "document.querySelectorAll('[data-cookie-settings]').forEach(function(el){el.addEventListener('click',function(e){e.preventDefault();showBanner();});});" +
  "document.addEventListener('keydown',function(e){if(e.key==='Escape'&&document.documentElement.getAttribute('data-pq-banner')==='open'){hideBanner();var l=document.querySelector('[data-cookie-settings]');if(l)l.focus();}});" +
  "var choice=getChoice();if(choice)document.documentElement.setAttribute('data-pq-consent',choice);if(choice==='accepted')loadGA();}" +
  "if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();" +
  "})();";


// ---------- Page list (also drives the sitemap) ----------
export type PageEntry = { key: string; lang: string; kind: string; game?: any; doc?: string };

export function allPages(): PageEntry[] {
  const out: PageEntry[] = [];
  for (const lang of PUBLISHED) {
    out.push({ key: "home", lang, kind: "home" });
    out.push({ key: "games", lang, kind: "games" });
    out.push({ key: "contact", lang, kind: "contact" });
    out.push({ key: "press", lang, kind: "press" });
    for (const k of ["legal", "privacy", "terms"]) out.push({ key: k, lang, kind: "legal" });
    for (const g of GAMES) {
      out.push({ key: `game:${g.slug}`, lang, kind: "game", game: g });
      for (const d of Object.keys(g.legal_docs ?? {}))
        out.push({ key: `game:${g.slug}:${d}`, lang, kind: "gamedoc", game: g, doc: d });
    }
  }
  return out;
}

/** Screenshot or trailer path for a language: that language's file when it exists in public/, else the English one. */
export function shot(src: string, lang: string): string {
  const pick = (l: string) => src.replace("{lang2}", l).replace("{tlang}", l);
  const own = pick(lang.toLowerCase());
  return "/" + (fs.existsSync(path.resolve("public", own)) ? own : pick(DEFAULT));
}

/** Language code used for press-kit files: the page language when its kit exists, else English. */
export function pressLang(lang: string): string {
  const l = lang.toLowerCase();
  return fs.existsSync(path.resolve("public/press", `sentence-press-kit-${l}.zip`)) ? l : DEFAULT;
}

/** Language code for press-page screenshots: the page language when its shot folder exists, else English. */
export function pressShotsLang(lang: string): string {
  const l = lang.toLowerCase();
  const f = `press/shots/${l}/sentence-${l}-title.jpg`;
  return fs.existsSync(path.resolve("public", f)) ? l : DEFAULT;
}

/** 16:9 trailer download path, falling back to English when a language has none. */
export function pressTrailer16(lang: string): string {
  const l = lang.toLowerCase();
  const own = `press/sentence-trailer-${l}-16x9.mp4`;
  const fallback = `press/sentence-trailer-${DEFAULT}-16x9.mp4`;
  return "/" + (fs.existsSync(path.resolve("public", own)) ? own : fallback);
}

/** Share image (og-<lang>.png) for a language, falling back to English. */
export function ogImage(lang: string): string {
  const l = lang.toLowerCase();
  return fs.existsSync(path.resolve("public", `og-${l}.png`)) ? `og-${l}.png` : `og-${DEFAULT}.png`;
}

/** Absolute URL of a page in a language. */
export function absUrl(page: string, lang: string): string {
  return ORIGIN + url(page, lang);
}

/** JSON-LD graph: Organization and WebSite on every page, plus VideoGame/SoftwareApplication on the home and game pages.
 *  No offers, prices or ratings. A real Play listing is added as installUrl and sameAs (the page URL stays the game page). */
export function jsonLd(pageKey: string, lang: string): Record<string, unknown>[] {
  const about = loc(SITE.about, lang);
  const orgId = ORIGIN + "/#organization";
  const org: Record<string, unknown> = {
    "@type": "Organization",
    "@id": orgId,
    name: SITE.name,
    url: BASE,
    logo: {
      "@type": "ImageObject",
      url: BASE + "assets/brand/logo-email.png",
      width: 480,
      height: 368,
    },
    email: SITE.email,
    telephone: SITE.phone,
    address: {
      "@type": "PostalAddress",
      streetAddress: "138 avenue Victor Hugo",
      addressLocality: "Paris",
      postalCode: "75016",
      addressCountry: "FR",
    },
    description: about,
  };
  const website: Record<string, unknown> = {
    "@type": "WebSite",
    "@id": ORIGIN + "/#website",
    url: BASE,
    name: SITE.name,
    description: about,
    publisher: { "@id": orgId },
    inLanguage: PUBLISHED,
  };
  const graph: Record<string, unknown>[] = [org, website];

  const addGame = (g: any) => {
    const node: Record<string, unknown> = {
      "@type": g.slug === "sentence" ? ["VideoGame", "SoftwareApplication"] : "SoftwareApplication",
      "@id": ORIGIN + "/#" + g.slug,
      name: `${loc(g.name, lang)}: ${loc(g.subtitle, lang)}`,
      url: absUrl(`game:${g.slug}`, lang),
      image: BASE + g.icon,
      description: loc(g.pitch, lang),
      author: { "@id": orgId },
      publisher: { "@id": orgId },
      applicationCategory: "GameApplication",
      operatingSystem: "Android",
    };
    if (g.slug === "sentence") node.availableLanguage = PUBLISHED;
    const play = g.store?.google_play;
    if (play) {
      node.installUrl = playStoreUrl(g, lang) ?? play;
      node.sameAs = [play];
    }
    graph.push(node);
  };

  if (pageKey === "home") {
    for (const g of GAMES) addGame(g);
  } else if (pageKey.startsWith("game:")) {
    const slug = pageKey.split(":")[1];
    const g = GAMES.find((x: any) => x.slug === slug);
    if (g) addGame(g);
  }
  return graph;
}


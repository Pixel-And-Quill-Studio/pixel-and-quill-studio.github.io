#!/usr/bin/env python3
"""Static site generator for the Pixel & Quill Studio website.

Inputs:
  site.json            studio identity and the list of languages
  games.json           the games (one entry per game)
  i18n/<lang>.json     interface strings (missing keys fall back to English)
  content/legal/       studio-wide legal documents (<doc>.<lang>.md)
  content/games/       game-specific details (<slug>.<lang>.md)

Usage: python3 build.py
See README.md for the URL structure and how to add a language or a game.
"""
import html
import json
import pathlib
import shutil

import markdown

ROOT = pathlib.Path(__file__).resolve().parent
SITE = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
GAMES = json.loads((ROOT / "games.json").read_text(encoding="utf-8"))["games"]
BASE = SITE["url"].rstrip("/") + "/"
DEFAULT = SITE["default_language"]
LANGS = {l["code"]: l for l in SITE["languages"]}
PUBLISHED = [c for c, l in LANGS.items() if l["published"]]
E = html.escape

# ---------- Interface strings ----------
I18N = {}
for code in LANGS:
    f = ROOT / "i18n" / f"{code}.json"
    I18N[code] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def t(lang, key):
    """Interface string with fallback to the default language."""
    return I18N.get(lang, {}).get(key, I18N[DEFAULT][key])


def loc(value, lang):
    """Pick a localized value from a {lang: value} dict, falling back to English."""
    if isinstance(value, dict):
        return value.get(lang, value[DEFAULT])
    return value


def localized_file(pattern, lang):
    """Path of a localized Markdown file, falling back to the default language."""
    p = ROOT / pattern.format(lang=lang)
    return p if p.exists() else ROOT / pattern.format(lang=DEFAULT)


# ---------- Pages and URLs ----------
PAGES = {
    "home": "",
    "games": "games/",
    "contact": "contact/",
    "legal": "legal-notice/",
    "privacy": "privacy/",
    "terms": "terms/",
}
for g in GAMES:
    PAGES[f"game:{g['slug']}"] = f"{g['slug']}/"
    # Game-specific legal documents, e.g. /one-last-heist/privacy/
    for doc in g.get("legal_docs", {}):
        PAGES[f"game:{g['slug']}:{doc}"] = f"{g['slug']}/{doc}/"


def url(page, lang):
    """Root-absolute URL of a page in a language, e.g. /fr/privacy/."""
    return "/" + LANGS[lang]["prefix"] + PAGES[page]


def out_file(page, lang):
    return (LANGS[lang]["prefix"] + PAGES[page]) + "index.html"


# Old URLs (French at the root, English as *-en.html) that must keep working.
LEGACY = {
    "en.html": ("home", "en"),
    "jeux/index.html": ("games", "fr"),
    "contact.html": ("contact", "fr"),
    "contact-en.html": ("contact", "en"),
    "mentions-legales.html": ("legal", "fr"),
    "legal-notice.html": ("legal", "en"),
}
for g in GAMES:
    for old, target in g.get("legacy_paths", {}).items():
        LEGACY[old] = (target["page"], target["lang"])

written = []


def emit(path, content):
    f = ROOT / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    written.append(path)


def clean():
    """Remove previously generated output so stale pages never linger."""
    dirs = {"games", "contact", "legal-notice", "privacy", "terms", "jeux"}
    dirs |= {g["slug"] for g in GAMES}
    dirs |= {l["prefix"].strip("/") for l in LANGS.values() if l["prefix"]}
    for d in dirs:
        shutil.rmtree(ROOT / d, ignore_errors=True)
    for f in ("index.html", "404.html", "sitemap.xml", "robots.txt", *LEGACY):
        p = ROOT / f
        if p.is_file():
            p.unlink()


def localize_links(body, lang):
    """Point root-absolute links to studio pages at the right language."""
    prefix = LANGS[lang]["prefix"]
    if not prefix:
        return body
    for suffix in PAGES.values():
        if suffix:
            body = body.replace(f'href="/{suffix}"', f'href="/{prefix}{suffix}"')
    return body


def md(file, lang):
    html_body = markdown.markdown(file.read_text(encoding="utf-8"), extensions=["tables"])
    return localize_links(html_body, lang)


# ---------- Language detection ----------
def lang_script(page, lang):
    """Inline script: saved choice first, then browser languages (default-language pages only)."""
    alternates = {c.lower(): url(page, c) for c in PUBLISHED}
    supported = [c.lower() for c in LANGS]
    is_default = "true" if lang == DEFAULT else "false"
    return (
        "<script>(function(){try{"
        f"var A={json.dumps(alternates)},S={json.dumps(supported)},cur={json.dumps(lang.lower())},D={is_default};"
        "var want=null,s=localStorage.getItem('pq-lang');"
        "if(s&&A[s]){want=s}else if(D){"
        "var L=navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||''];"
        "for(var i=0;i<L.length&&!want;i++){var l=(L[i]||'').toLowerCase(),b=l.split('-')[0];"
        "var c=S.indexOf(l)>=0?l:(b==='pt'?'pt-br':(S.indexOf(b)>=0?b:null));"
        "if(c){want=A[c]?c:'en'}}}"
        "if(want&&want!==cur&&A[want]){location.replace(A[want]+location.hash)}"
        "}catch(e){}})();</script>"
    )


SWITCH_SCRIPT = (
    "<script>document.querySelectorAll('a[data-lang]').forEach(function(a){"
    "a.addEventListener('click',function(){try{localStorage.setItem('pq-lang',a.dataset.lang)}catch(e){}})});</script>"
)


# ---------- Layout ----------
def head(page, lang, title, desc, noindex=False, detect=True):
    canonical = BASE.rstrip("/") + url(page, lang)
    alts = "".join(
        f'<link rel="alternate" hreflang="{c}" href="{BASE.rstrip("/")}{url(page, c)}">' for c in PUBLISHED
    )
    alts += f'<link rel="alternate" hreflang="x-default" href="{BASE.rstrip("/")}{url(page, DEFAULT)}">'
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    script = lang_script(page, lang) if detect else ""
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{script}<title>{E(title)}</title><meta name="description" content="{E(desc)}">{robots}
<link rel="stylesheet" href="/assets/style.css">
<link rel="icon" href="/assets/brand/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/brand/favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="/assets/brand/favicon-48.png" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
<link rel="canonical" href="{canonical}">
{alts}
<meta name="theme-color" content="#0b0b0d">
<meta property="og:type" content="website"><meta property="og:site_name" content="Pixel &amp; Quill Studio">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canonical}"><meta property="og:locale" content="{LANGS[lang]['locale']}">
<meta property="og:image" content="{BASE}assets/brand/og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Pixel &amp; Quill Studio">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{BASE}assets/brand/og-image.png"></head>
"""


def page(page_key, lang, title, body, desc, nav=None, home=False, noindex=False, detect=True):
    s = SITE
    items = [("home", t(lang, "home")), ("games", t(lang, "games")), ("contact", t(lang, "contact"))]
    menu = "".join(
        f'<a{" class=on" if k == nav else ""} href="{url(k, lang)}">{E(lbl)}</a>' for k, lbl in items
    )
    switch = "".join(
        f'<a class="{"on" if c == lang else ""}" hreflang="{c}" lang="{c}" data-lang="{c.lower()}" '
        f'href="{url(page_key, c)}" title="{E(LANGS[c]["name"])}">{E(LANGS[c]["label"])}</a>'
        for c in PUBLISHED
    )
    drop = "".join(
        f'<a class="{"on" if c == lang else ""}" hreflang="{c}" lang="{c}" data-lang="{c.lower()}" '
        f'href="{url(page_key, c)}">{E(LANGS[c]["label"])} · {E(LANGS[c]["name"])}</a>'
        for c in PUBLISHED
    )
    foot = (
        f"© {s['year']} {E(s['name'])} — {E(s['owner'])}, EI — SIREN {s['siren']} — {E(s['address'])} — "
        f'<a href="mailto:{s["email"]}">{s["email"]}</a><br>'
        f'<a href="{url("legal", lang)}">{E(t(lang, "legal"))}</a> · '
        f'<a href="{url("privacy", lang)}">{E(t(lang, "privacy"))}</a> · '
        f'<a href="{url("terms", lang)}">{E(t(lang, "terms"))}</a>'
    )
    return head(page_key, lang, title, desc, noindex, detect) + f"""<body><a class="skip" href="#main">{E(t(lang, 'skip'))}</a><div class="wrap"><header class="top"><a class="brand{' home' if home else ''}" href="{url('home', lang)}" aria-label="Pixel &amp; Quill Studio"><img class="brand-icon" src="/assets/brand/favicon.svg" alt="" width="44" height="44"><img class="brand-word" src="/assets/brand/logo-wordmark-inline.svg" alt="Pixel &amp; Quill Studio" height="24"></a>
<nav class="menu" aria-label="Menu">{menu}</nav>
<nav class="lang" aria-label="{E(t(lang, 'lang_nav'))}">{switch}</nav>
<details class="lang-drop"><summary aria-label="{E(t(lang, 'lang_nav'))}: {E(LANGS[lang]['name'])}">{E(LANGS[lang]['label'])}</summary><nav aria-label="{E(t(lang, 'lang_nav'))}">{drop}</nav></details></header>
<main id="main">{body}</main><footer>{foot}</footer></div>{SWITCH_SCRIPT}</body></html>
"""


def status_text(g, lang):
    """Status label: the game's own label (e.g. a release month) or the generic one."""
    if g.get("status_label"):
        return loc(g["status_label"], lang)
    return t(lang, "status")[g.get("status", "coming_soon")]


def badge(g, lang):
    st = g.get("status", "coming_soon")
    return f'<span class="badge {E(st)}">{E(status_text(g, lang))}</span>'


def binding_note(page_key, lang):
    """For translated legal documents: only the French version is legally binding."""
    note = I18N.get(lang, {}).get("legal_binding_note")
    if not note:
        return ""
    fr_link = f'<a href="{url(page_key, "fr")}" hreflang="fr" lang="fr">{E(LANGS["fr"]["name"])}</a>'
    return f'<p class="note">{E(note)} {fr_link}</p>'


def game_card(g, lang):
    gp = url(f"game:{g['slug']}", lang)
    return f"""<article class="card game"><img src="/{g['icon']}" alt="" width="84" height="84">
<div><h3><a class="plain" href="{gp}">{E(loc(g['name'], lang))}</a></h3>
<p class="sub">{E(loc(g['subtitle'], lang))}</p><p class="pitch">{E(loc(g['pitch'], lang))}</p>
<p>{badge(g, lang)}</p>
<div class="links"><a class="btn" href="{gp}">{E(t(lang, 'discover'))}</a></div></div></article>"""


def games_grid(lang):
    cards = "".join(game_card(g, lang) for g in GAMES)
    if SITE.get("show_next_game_placeholder"):
        cards += (
            f'<article class="card game next"><div class="next-ico" aria-hidden="true">?</div><div>'
            f'<h3>{E(t(lang, "next_title"))}</h3><p class="pitch">{E(t(lang, "next_text"))}</p></div></article>'
        )
    return f'<div class="grid">{cards}</div>'


def redirect_page(target_url, lang):
    full = BASE.rstrip("/") + target_url
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="robots" content="noindex">
<title>{E(t(lang, 'redirect_text'))}</title>
<link rel="canonical" href="{full}"><meta http-equiv="refresh" content="0; url={target_url}">
<script>location.replace({json.dumps(target_url)}+location.hash)</script></head>
<body><p>{E(t(lang, 'redirect_text'))} <a href="{target_url}">{full}</a></p></body></html>
"""


# ---------- Build ----------
clean()
s = SITE
for lang in PUBLISHED:
    body = f"""<h1 class="hero"><img src="/assets/brand/logo-full.svg" alt="{E(s['name'])}" width="340"></h1><p class="tagline">{E(loc(s['tagline'], lang))}</p>
<h2>{E(t(lang, 'our_games'))}</h2>{games_grid(lang)}
<p class="more"><a href="{url('games', lang)}">{E(t(lang, 'all_games'))} →</a></p>
<h2>{E(t(lang, 'studio'))}</h2><p>{E(loc(s['about'], lang))}</p>
<blockquote class="card founder"><p>{E(loc(s['founder'], lang))}</p><footer>— {E(t(lang, 'founder_sign'))}</footer></blockquote>
<p><a class="btn" href="{url('contact', lang)}">{E(t(lang, 'contact'))}</a></p>"""
    emit(out_file("home", lang), page("home", lang, s["name"], body, loc(s["tagline"], lang), nav="home", home=True))

    body = f"<h1>{E(t(lang, 'games_title'))}</h1><p class=\"lead\">{E(t(lang, 'games_intro'))}</p>{games_grid(lang)}"
    emit(out_file("games", lang),
         page("games", lang, f"{t(lang, 'games_title')} — {s['name']}", body, t(lang, "games_intro"), nav="games"))

    body = f"""<h1>{E(t(lang, 'contact'))}</h1><p class="lead">{E(t(lang, 'contact_intro'))}</p>
<div class="card"><h3 style="margin-top:0">{E(t(lang, 'contact_mail'))}</h3><p><a class="mail" href="mailto:{s['email']}">{s['email']}</a></p>
<h3>{E(t(lang, 'contact_pub'))}</h3><p>{E(s['name'])} — {E(s['owner'])}, EI<br>{E(s['address'])}</p></div>
<p class="muted">{E(t(lang, 'contact_note'))} <a href="{url('privacy', lang)}">{E(t(lang, 'privacy'))}</a></p>
<p><a href="{url('legal', lang)}">{E(t(lang, 'legal'))}</a></p>"""
    emit(out_file("contact", lang),
         page("contact", lang, f"{t(lang, 'contact')} — {s['name']}", body, t(lang, "contact_intro"), nav="contact"))

    for key, doc in (("legal", "legal-notice"), ("privacy", "privacy"), ("terms", "terms")):
        body = md(localized_file(f"content/legal/{doc}.{{lang}}.md", lang), lang)
        body = binding_note(key, lang) + body
        emit(out_file(key, lang),
             page(key, lang, f"{t(lang, key)} — {s['name']}", body, t(lang, f"{key}_desc")))

    for g in GAMES:
        key = f"game:{g['slug']}"
        paras = "".join(f"<p>{E(x)}</p>" for x in loc(g["description"], lang))
        feats = "".join(f"<li>{E(x)}</li>" for x in loc(g["features"], lang))
        store = (g.get("store") or {}).get("google_play")
        store_btn = (f'<p><a class="btn gold" rel="noopener" href="{E(store)}">{E(t(lang, "get_on"))} Google Play</a></p>'
                     if store else "")
        details = ""
        if g.get("details"):
            details = f"<h2>{E(t(lang, 'game_details'))}</h2>" + md(localized_file(g["details"], lang), lang).replace(
                "<h2>", "<h3>").replace("</h2>", "</h3>")
        game_docs = list(g.get("legal_docs", {}))
        docs = "".join(f'<a href="{url(f"{key}:{d}", lang)}">{E(t(lang, d))} — {E(loc(g["name"], lang))}</a>'
                       for d in game_docs)
        docs += "".join(f'<a href="{url(k, lang)}">{E(t(lang, k))}</a>'
                        for k in ("privacy", "terms", "legal") if k not in game_docs)
        docs_note = t(lang, "game_legal_docs_note" if game_docs else "legal_docs_note")
        quote = (f'<blockquote class="quote"><p>“{E(loc(g["tagline"], lang))}”</p>'
                 f'<footer>{E(t(lang, "game_line"))}</footer></blockquote>' if g.get("tagline") else "")
        facts = ""
        if g.get("facts"):
            rows = "".join(f"<dt>{E(t(lang, 'fact_' + f['key']))}</dt><dd>{E(loc(f['value'], lang))}</dd>"
                           for f in g["facts"])
            status_row = f"<dt>{E(t(lang, 'fact_status'))}</dt><dd>{E(status_text(g, lang))}</dd>"
            facts = f'<div class="card facts"><h2>{E(t(lang, "key_facts"))}</h2><dl>{rows}{status_row}</dl></div>'
        if g.get("splash"):
            facts = (f'<div class="showcase"><img class="splash" src="/{g["splash"]["src"]}" '
                     f'alt="{E(loc(g["splash"]["alt"], lang))}" width="{g["splash"]["width"]}" '
                     f'height="{g["splash"]["height"]}" loading="lazy">{facts}</div>')
        gallery = ""
        if g.get("gallery"):
            figs = "".join(
                f'<figure><img src="/{im["src"]}" alt="{E(loc(im["alt"], lang))}" width="{im["width"]}" '
                f'height="{im["height"]}" loading="lazy"><figcaption>{E(loc(im["caption"], lang))}</figcaption></figure>'
                for im in g["gallery"]["images"])
            layout = " " + g["gallery"]["layout"] if g["gallery"].get("layout") else ""
            gallery = f'<h2>{E(t(lang, g["gallery"]["title"]))}</h2><div class="gallery{E(layout)}">{figs}</div>'
        body = f"""<p class="crumb"><a href="{url('games', lang)}">{E(t(lang, 'back_games'))}</a></p>
<div class="game-head"><img src="/{g['icon']}" alt="" width="120" height="120">
<div><h1 style="margin:0">{E(loc(g['name'], lang))}</h1><p class="sub">{E(loc(g['subtitle'], lang))}</p><p>{badge(g, lang)}</p></div></div>
<p class="lead">{E(loc(g['pitch'], lang))}</p>{store_btn}{paras}{quote}
{facts}
<h2>{E(t(lang, 'features'))}</h2><ul class="feat">{feats}</ul>
{gallery}
{details}
<h2>{E(t(lang, 'legal_docs'))}</h2><p class="muted">{E(docs_note)}</p><div class="links">{docs}</div>"""
        title = f"{loc(g['name'], lang)}: {loc(g['subtitle'], lang)} — {s['name']}"
        emit(out_file(key, lang), page(key, lang, title, body, loc(g["pitch"], lang), nav="games"))

        # Game-specific legal documents
        for d, pattern in g.get("legal_docs", {}).items():
            dkey = f"{key}:{d}"
            name = loc(g["name"], lang)
            crumb = f'<p class="crumb"><a href="{url(key, lang)}">← {E(name)}</a></p>'
            body = crumb + binding_note(dkey, lang) + md(localized_file(pattern, lang), lang)
            emit(out_file(dkey, lang),
                 page(dkey, lang, f"{t(lang, d)} — {name} — {s['name']}", body,
                      t(lang, f"game_{d}_desc").format(game=name), nav="games"))

# Legacy URLs: lightweight redirect stubs
for old, (key, lang) in LEGACY.items():
    if lang not in PUBLISHED:
        lang = DEFAULT
    emit(old, redirect_page(url(key, lang), lang))

# 404 page (served from any depth, links are root-absolute)
body = "<h1>Page not found</h1>" + "".join(
    f'<p lang="{c}">{E(t(c, "notfound_text"))}</p>' for c in PUBLISHED) + "<p>" + " ".join(
    f'<a class="btn" lang="{c}" href="{url("home", c)}">{E(t(c, "home"))}</a>' for c in PUBLISHED) + "</p>"
emit("404.html", page("home", DEFAULT, "404 — Pixel & Quill Studio", body, "Page not found", noindex=True, detect=False))

pages = [p for p in written if p != "404.html" and p not in LEGACY]
emit("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
     + "".join(f"<url><loc>{BASE}{p[:-len('index.html')]}</loc></url>\n" for p in pages) + "</urlset>\n")
emit("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
print(f"built {len(written)} files")

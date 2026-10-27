#!/usr/bin/env python3
"""Générateur du site Pixel & Quill Studio (multi-jeux).

Données : site.json (studio) + games.json (jeux). Ajouter un jeu = ajouter une
entrée dans games.json + ses documents juridiques (voir README.md).
Usage : python3 build.py
"""
import html, json, os, pathlib
import markdown

ROOT = pathlib.Path(__file__).resolve().parent
SITE = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
GAMES = json.loads((ROOT / "games.json").read_text(encoding="utf-8"))["games"]
BASE = SITE["url"]
LANGS = ("fr", "en")
E = html.escape

# Textes de l'interface (FR / EN)
T = {
    "fr": {
        "home": "Accueil", "games": "Jeux", "contact": "Contact", "legal": "Mentions légales",
        "our_games": "Nos jeux", "all_games": "Tous les jeux", "discover": "Découvrir",
        "studio": "Le studio", "back_games": "← Tous les jeux", "features": "En bref", "legal_docs": "Documents légaux",
        "next_title": "Le prochain jeu", "next_text": "Un nouveau projet est en préparation. Reviens bientôt.",
        "privacy": "Politique de confidentialité", "terms": "Conditions d’utilisation",
        "games_title": "Nos jeux", "games_intro": "Les jeux publiés par Pixel & Quill Studio.",
        "contact_intro": "Une question, un retour sur un jeu, une demande de presse ou de partenariat ? Écris-nous, nous répondons dès que possible.",
        "contact_mail": "Par e-mail", "contact_pub": "Éditeur",
        "contact_note": "Pour une question sur un jeu, précise son nom et ton appareil. Pour tes données personnelles, consulte la politique de confidentialité du jeu concerné.",
        "store": "Google Play", "get_on": "Disponible sur",
        "404_title": "Page introuvable", "404_text": "Cette page n’existe pas ou a été déplacée.", "404_link": "Retour à l’accueil",
        "locale": "fr_FR", "skip": "Aller au contenu",
        "status": {"coming_soon": "Bientôt sur Google Play", "available": "Disponible sur Google Play", "in_development": "En développement"},
    },
    "en": {
        "home": "Home", "games": "Games", "contact": "Contact", "legal": "Legal notice",
        "our_games": "Our games", "all_games": "All games", "discover": "Discover",
        "studio": "The studio", "back_games": "← All games", "features": "At a glance", "legal_docs": "Legal documents",
        "next_title": "Next game", "next_text": "A new project is in the works. Check back soon.",
        "privacy": "Privacy policy", "terms": "Terms of use",
        "games_title": "Our games", "games_intro": "The games published by Pixel & Quill Studio.",
        "contact_intro": "A question, feedback on a game, a press or partnership request? Write to us, we reply as soon as we can.",
        "contact_mail": "By email", "contact_pub": "Publisher",
        "contact_note": "For a question about a game, mention its name and your device. For your personal data, see the privacy policy of the game concerned.",
        "store": "Google Play", "get_on": "Get it on",
        "404_title": "Page not found", "404_text": "This page does not exist or has moved.", "404_link": "Back to home",
        "locale": "en_US", "skip": "Skip to content",
        "status": {"coming_soon": "Coming soon on Google Play", "available": "Available on Google Play", "in_development": "In development"},
    },
}

# Chemins des pages (relatifs à la racine du site) : (fr, en)
P = {
    "home": ("index.html", "en.html"),
    "games": ("jeux/index.html", "games/index.html"),
    "contact": ("contact.html", "contact-en.html"),
    "legal": ("mentions-legales.html", "legal-notice.html"),
}
def game_path(g, lang): return f"{g['slug']}/index.html" if lang == "fr" else f"{g['slug']}/en.html"
def doc_path(g, kind, lang): return f"{g['slug']}/{kind}-{lang}.html"
def pp(key, lang): return P[key][LANGS.index(lang)]

written = []

def public(path):
    """URL publique d'un chemin (index.html -> dossier)."""
    return path[:-len("index.html")] if path.endswith("index.html") else path

def ln(cur, target):
    """Lien relatif de la page `cur` vers `target` (chemins relatifs à la racine)."""
    d = os.path.dirname(cur) or "."
    t = public(target)
    r = os.path.relpath(t if t else ".", d)
    if (t.endswith("/") or t == "") and not r.endswith("/"):
        r += "/"
    return "./" if r == ".//" or r == "./" else r

def tr(lang, key): return T[lang][key]

def head(cur, lang, title, desc, other):
    up = ln(cur, "")
    up = "" if up == "./" else up
    url = BASE + public(cur)
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="stylesheet" href="{up}assets/style.css">
<link rel="icon" href="{up}assets/brand/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{up}assets/brand/favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="{up}assets/brand/favicon-48.png" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="{up}assets/brand/apple-touch-icon.png">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="fr" href="{BASE}{public(other['fr'])}"><link rel="alternate" hreflang="en" href="{BASE}{public(other['en'])}">
<meta name="theme-color" content="#0b0b0d">
<meta property="og:type" content="website"><meta property="og:site_name" content="Pixel &amp; Quill Studio">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}"><meta property="og:locale" content="{T[lang]['locale']}">
<meta property="og:image" content="{BASE}assets/brand/og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Pixel &amp; Quill Studio">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{BASE}assets/brand/og-image.png"></head>
"""

def page(cur, lang, title, body, desc, other, nav=None, home=False, noindex=False):
    t = T[lang]
    g = lambda target: ln(cur, target)
    items = [("home", t["home"]), ("games", t["games"]), ("contact", t["contact"])]
    menu = "".join(f'<a{" class=on" if k == nav else ""} href="{g(pp(k, lang))}">{E(lbl)}</a>' for k, lbl in items)
    fr_on, en_on = ("on", "") if lang == "fr" else ("", "on")
    s = SITE
    foot = (f"© {s['year']} {E(s['name'])} — {E(s['owner'])}, EI — SIREN {s['siren']} — {E(s['address'])} — "
            f'<a href="mailto:{s["email"]}">{s["email"]}</a>'
            f' — <a href="{g(pp("legal", lang))}">{E(t["legal"])}</a>')
    h = head(cur, lang, title, desc, other)
    if noindex:
        h = h.replace("<meta name=\"theme-color\"", "<meta name=\"robots\" content=\"noindex\"><meta name=\"theme-color\"", 1)
    up = g("")
    up = "" if up == "./" else up
    return h + f"""<body><a class="skip" href="#main">{E(t['skip'])}</a><div class="wrap"><header class="top"><a class="brand{' home' if home else ''}" href="{g(pp('home', lang))}" aria-label="Pixel &amp; Quill Studio"><img class="brand-icon" src="{up}assets/brand/favicon.svg" alt="" width="44" height="44"><img class="brand-word" src="{up}assets/brand/logo-wordmark-inline.svg" alt="Pixel &amp; Quill Studio" height="24"></a>
<nav class="menu" aria-label="Menu">{menu}</nav>
<nav class="lang" aria-label="Langue / Language"><a class="{fr_on}" hreflang="fr" href="{g(other['fr'])}">FR</a><a class="{en_on}" hreflang="en" href="{g(other['en'])}">EN</a></nav></header>
<main id="main">{body}</main><footer>{foot}</footer></div></body></html>
"""

def emit(path, content):
    f = ROOT / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    written.append(path)

def md(file):
    return markdown.markdown(file.read_text(encoding="utf-8"), extensions=["tables"])

def resolve_dir(d):
    p = pathlib.Path(d)
    return p if p.is_absolute() else ROOT / p

def badge(g, lang):
    st = g.get("status", "coming_soon")
    return f'<span class="badge {E(st)}">{E(T[lang]["status"][st])}</span>'

def game_card(cur, g, lang):
    t = T[lang]
    link = lambda target: ln(cur, target)
    docs = "".join(f'<a href="{link(doc_path(g, k, lang))}">{E(t[k])}</a>' for k in g["docs"])
    return f"""<article class="card game"><img src="{link(g['icon'])}" alt="" width="84" height="84">
<div><h3><a class="plain" href="{link(game_path(g, lang))}">{E(g['name'][lang])}</a></h3>
<p class="sub">{E(g['subtitle'][lang])}</p><p class="pitch">{E(g['pitch'][lang])}</p>
<p>{badge(g, lang)}</p>
<div class="links"><a class="btn" href="{link(game_path(g, lang))}">{E(t['discover'])}</a>{docs}</div></div></article>"""

def games_grid(cur, lang, placeholder=True):
    cards = "".join(game_card(cur, g, lang) for g in GAMES)
    if placeholder and SITE.get("show_next_game_placeholder"):
        t = T[lang]
        cards += f'<article class="card game next"><div class="next-ico" aria-hidden="true">?</div><div><h3>{E(t["next_title"])}</h3><p class="pitch">{E(t["next_text"])}</p></div></article>'
    return f'<div class="grid">{cards}</div>'

# ---------- Pages studio ----------
for lang in LANGS:
    t = T[lang]
    other = {l: pp("home", l) for l in LANGS}
    cur = pp("home", lang)
    body = f"""<h1 class="hero"><img src="assets/brand/logo-full.svg" alt="{E(SITE['name'])}" width="340"></h1><p class="tagline">{E(SITE['tagline'][lang])}</p>
<h2>{E(t['our_games'])}</h2>{games_grid(cur, lang)}
<p class="more"><a href="{ln(cur, pp('games', lang))}">{E(t['all_games'])} →</a></p>
<h2>{E(t['studio'])}</h2><p>{E(SITE['about'][lang])}</p>
<p><a class="btn" href="{ln(cur, pp('contact', lang))}">{E(t['contact'])}</a></p>"""
    emit(cur, page(cur, lang, SITE["name"], body, SITE["tagline"][lang], other, nav="home", home=True))

    cur = pp("games", lang)
    other = {l: pp("games", l) for l in LANGS}
    body = f"<h1>{E(t['games_title'])}</h1><p class=\"lead\">{E(t['games_intro'])}</p>{games_grid(cur, lang)}"
    emit(cur, page(cur, lang, f"{t['games_title']} — {SITE['name']}", body, t["games_intro"], other, nav="games"))

    cur = pp("contact", lang)
    other = {l: pp("contact", l) for l in LANGS}
    s = SITE
    body = f"""<h1>{E(t['contact'])}</h1><p class="lead">{E(t['contact_intro'])}</p>
<div class="card"><h3 style="margin-top:0">{E(t['contact_mail'])}</h3><p><a class="mail" href="mailto:{s['email']}">{s['email']}</a></p>
<h3>{E(t['contact_pub'])}</h3><p>{E(s['name'])} — {E(s['owner'])}, EI<br>{E(s['address'])}</p></div>
<p class="muted">{E(t['contact_note'])}</p>
<p><a href="{ln(cur, pp('legal', lang))}">{E(t['legal'])}</a></p>"""
    emit(cur, page(cur, lang, f"{t['contact']} — {SITE['name']}", body, t["contact_intro"], other, nav="contact"))

    # Mentions légales : markdown du dépôt de docs
    cur = pp("legal", lang)
    other = {l: pp("legal", l) for l in LANGS}
    ln_cfg = SITE["legal_notice"]
    body = md(resolve_dir(ln_cfg["docs_dir"]) / ln_cfg[lang])
    desc = "Mentions légales du site Pixel & Quill Studio" if lang == "fr" else "Legal notice of the Pixel & Quill Studio website"
    emit(cur, page(cur, lang, f"{t['legal']} — {SITE['name']}", body, desc, other))

# ---------- Pages par jeu ----------
for g in GAMES:
    docs_dir = resolve_dir(g["docs_dir"])
    for lang in LANGS:
        t = T[lang]
        cur = game_path(g, lang)
        other = {l: game_path(g, l) for l in LANGS}
        paras = "".join(f"<p>{E(x)}</p>" for x in g["description"][lang])
        feats = "".join(f"<li>{E(x)}</li>" for x in g["features"][lang])
        store = g.get("store", {}).get("google_play")
        store_btn = f'<p><a class="btn gold" rel="noopener" href="{E(store)}">{E(t["get_on"])} {E(t["store"])}</a></p>' if store else ""
        docs = "".join(f'<a href="{ln(cur, doc_path(g, k, lang))}">{E(t[k])}</a>' for k in g["docs"])
        body = f"""<p class="crumb"><a href="{ln(cur, pp('games', lang))}">{E(t['back_games'])}</a></p>
<div class="game-head"><img src="{ln(cur, g['icon'])}" alt="" width="120" height="120">
<div><h1 style="margin:0">{E(g['name'][lang])}</h1><p class="sub">{E(g['subtitle'][lang])}</p><p>{badge(g, lang)}</p></div></div>
<p class="lead">{E(g['pitch'][lang])}</p>{store_btn}{paras}
<h2>{E(t['features'])}</h2><ul class="feat">{feats}</ul>
<h2>{E(t['legal_docs'])}</h2><div class="links">{docs}</div>"""
        title = f"{g['name'][lang]} : {g['subtitle'][lang]} — {SITE['name']}"
        emit(cur, page(cur, lang, title, body, g["pitch"][lang], other, nav="games"))
        # documents légaux du jeu (URLs historiques conservées : <slug>/privacy-fr.html…)
    for kind, files in g["docs"].items():
        for lang in LANGS:
            t = T[lang]
            cur = doc_path(g, kind, lang)
            other = {l: doc_path(g, kind, l) for l in LANGS}
            crumb = f'<p class="crumb"><a href="{ln(cur, game_path(g, lang))}">← {E(g["name"][lang])}</a></p>'
            body = crumb + md(docs_dir / files[lang])
            title = f"{t[kind]} — {g['name'][lang]}"
            emit(cur, page(cur, lang, title, body, f"{t[kind]} — {g['name'][lang]}", other, nav="games"))

# ---------- 404, sitemap, robots ----------
body = ('<h1>Page introuvable / Page not found</h1><p>Cette page n’existe pas ou a été déplacée. / This page does not exist or has moved.</p>'
        '<p><a class="btn" href="/">Accueil / Home</a></p>')
h404 = page("404.html", "fr", "404 — Pixel & Quill Studio", body, "Page introuvable", {"fr": "index.html", "en": "en.html"}, noindex=True)
# 404.html est servi depuis n'importe quelle profondeur : liens absolus
h404 = (h404.replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/')
        .replace('href="./"', 'href="/"').replace('href="index.html"', 'href="/"').replace('href="en.html"', 'href="/en.html"')
        .replace('href="jeux/"', 'href="/jeux/"').replace('href="contact.html"', 'href="/contact.html"')
        .replace('href="mentions-legales.html"', 'href="/mentions-legales.html"'))
emit("404.html", h404)

urls = [BASE + public(p) for p in written if p != "404.html"]
emit("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
     + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
emit("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
print(f"built {len(written)} files")

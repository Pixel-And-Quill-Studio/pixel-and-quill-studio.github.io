import markdown, pathlib, html
D = pathlib.Path("/workspace/sentence-godot/docs")
OUT = pathlib.Path("/workspace/pq-site")
SITE = "https://pixel-quill-studio.github.io/"
def page(title, body, lang, other, depth, desc, path="", home=False):
    up = "../" * depth
    fr_on, en_on = ("on", "") if lang == "fr" else ("", "on")
    legal = f'{up}mentions-legales.html' if lang == "fr" else f'{up}legal-notice.html'
    ln = "Mentions légales" if lang == "fr" else "Legal notice"
    foot = ("© 2026 Pixel & Quill Studio — Styvens Wentz EI — 138 avenue Victor Hugo, 75116 Paris, France — "
            '<a href="mailto:pixelandquillstudio.pro@gmail.com">pixelandquillstudio.pro@gmail.com</a>'
            f' — <a href="{legal}">{ln}</a>')
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="stylesheet" href="{up}assets/style.css">
<link rel="icon" href="{up}assets/brand/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{up}assets/brand/favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="{up}assets/brand/favicon-48.png" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="{up}assets/brand/apple-touch-icon.png">
<meta name="theme-color" content="#0b0b0d">
<meta property="og:type" content="website"><meta property="og:site_name" content="Pixel &amp; Quill Studio">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{SITE}{path}"><meta property="og:locale" content="{'fr_FR' if lang=='fr' else 'en_US'}">
<meta property="og:image" content="{SITE}assets/brand/og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Pixel &amp; Quill Studio">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{SITE}assets/brand/og-image.png"></head>
<body><div class="wrap"><header class="top"><a class="brand{' home' if home else ''}" href="{up}{'index.html' if lang=='fr' else 'en.html'}" aria-label="Pixel &amp; Quill Studio"><img class="brand-icon" src="{up}assets/brand/favicon.svg" alt="" width="44" height="44"><img class="brand-word" src="{up}assets/brand/logo-wordmark-inline.svg" alt="Pixel &amp; Quill Studio" height="24"></a>
<nav class="lang"><a class="{fr_on}" href="{other['fr']}">FR</a><a class="{en_on}" href="{other['en']}">EN</a></nav></header>
<main>{body}</main><footer>{foot}</footer></div></body></html>
"""
for name, src, lang, title, desc in [
    ("privacy-fr", "privacy_policy_fr.md", "fr", "Politique de confidentialité — Sentence", "Politique de confidentialité du jeu Sentence"),
    ("privacy-en", "privacy_policy_en.md", "en", "Privacy Policy — Sentence", "Privacy policy of the game Sentence"),
    ("terms-fr", "terms_fr.md", "fr", "Conditions d’utilisation — Sentence", "Conditions d’utilisation du jeu Sentence"),
    ("terms-en", "terms_en.md", "en", "Terms of Use — Sentence", "Terms of use of the game Sentence")]:
    body = markdown.markdown((D / src).read_text(encoding="utf-8"), extensions=["tables"])
    base = name.rsplit("-", 1)[0]
    (OUT / "sentence" / f"{name}.html").write_text(page(title, body, lang, {"fr": f"{base}-fr.html", "en": f"{base}-en.html"}, 1, desc, f"sentence/{name}.html"), encoding="utf-8")
for name, src, lang, title, desc in [
    ("mentions-legales", "legal_notice_fr.md", "fr", "Mentions légales — Pixel & Quill Studio", "Mentions légales du site Pixel & Quill Studio"),
    ("legal-notice", "legal_notice_en.md", "en", "Legal notice — Pixel & Quill Studio", "Legal notice of the Pixel & Quill Studio website")]:
    body = markdown.markdown((D / src).read_text(encoding="utf-8"), extensions=["tables"])
    (OUT / f"{name}.html").write_text(page(title, body, lang, {"fr": "mentions-legales.html", "en": "legal-notice.html"}, 0, desc, f"{name}.html"), encoding="utf-8")
home = {
 "fr": ("Pixel & Quill Studio", "Studio indépendant de jeux mobiles, à Paris.", "Jeu de cartes à glisser : choisis ta prison, ton détenu, et tiens le plus de jours possible.",
        "Politique de confidentialité", "Conditions d’utilisation", "Contact", "fr", "Mentions légales", "mentions-legales.html"),
 "en": ("Pixel & Quill Studio", "Independent mobile game studio based in Paris.", "Swipe card game: pick your prison, your inmate, and survive as many days as you can.",
        "Privacy policy", "Terms of use", "Contact", "en", "Legal notice", "legal-notice.html")}
for lang, (t, tag, pitch, pp, tu, ct, sfx, lnl, lnf) in home.items():
    body = f"""<h1 class="hero"><img src="assets/brand/logo-full.svg" alt="{html.escape(t)}" width="340"></h1><p class="tagline">{tag}</p>
<div class="card game"><img src="assets/sentence-icon.png" alt="Sentence"><div><h3 style="margin:0">Sentence</h3><p style="margin:.2em 0">{pitch}</p>
<div class="links"><a href="sentence/privacy-{sfx}.html">{pp}</a><a href="sentence/terms-{sfx}.html">{tu}</a></div></div></div>
<h2>{ct}</h2><p><a href="mailto:pixelandquillstudio.pro@gmail.com">pixelandquillstudio.pro@gmail.com</a><br>Styvens Wentz EI — 138 avenue Victor Hugo, 75116 Paris, France</p>
<p><a href="{lnf}">{lnl}</a></p>"""
    (OUT / ("index.html" if lang == "fr" else "en.html")).write_text(page(t, body, lang, {"fr": "index.html", "en": "en.html"}, 0, tag, "" if lang == "fr" else "en.html", home=True), encoding="utf-8")
print("built")

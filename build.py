import markdown, pathlib, html
D = pathlib.Path("/workspace/sentence-godot/docs")
OUT = pathlib.Path("/workspace/pq-site")
def page(title, body, lang, other, depth, desc):
    up = "../" * depth
    fr_on, en_on = ("on", "") if lang == "fr" else ("", "on")
    foot = ("© 2026 Pixel & Quill Studio — 138 Avenue Victor Hugo, 75016 Paris, France — "
            '<a href="mailto:pixelandquillstudio.pro@gmail.com">pixelandquillstudio.pro@gmail.com</a>')
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="stylesheet" href="{up}assets/style.css"><link rel="icon" href="{up}assets/sentence-icon.png"></head>
<body><div class="wrap"><header class="top"><a class="brand" href="{up}{'index.html' if lang=='fr' else 'en.html'}">Pixel &amp; Quill Studio</a>
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
    (OUT / "sentence" / f"{name}.html").write_text(page(title, body, lang, {"fr": f"{base}-fr.html", "en": f"{base}-en.html"}, 1, desc), encoding="utf-8")
home = {
 "fr": ("Pixel & Quill Studio", "Studio indépendant de jeux mobiles, à Paris.", "Jeu de cartes à glisser : choisis ta prison, ton détenu, et tiens le plus de jours possible.",
        "Politique de confidentialité", "Conditions d’utilisation", "Contact", "fr"),
 "en": ("Pixel & Quill Studio", "Independent mobile game studio based in Paris.", "Swipe card game: pick your prison, your inmate, and survive as many days as you can.",
        "Privacy policy", "Terms of use", "Contact", "en")}
for lang, (t, tag, pitch, pp, tu, ct, sfx) in home.items():
    body = f"""<h1>{html.escape(t)}</h1><p>{tag}</p>
<div class="card game"><img src="assets/sentence-icon.png" alt="Sentence"><div><h3 style="margin:0">Sentence</h3><p style="margin:.2em 0">{pitch}</p>
<div class="links"><a href="sentence/privacy-{sfx}.html">{pp}</a><a href="sentence/terms-{sfx}.html">{tu}</a></div></div></div>
<h2>{ct}</h2><p><a href="mailto:pixelandquillstudio.pro@gmail.com">pixelandquillstudio.pro@gmail.com</a><br>138 Avenue Victor Hugo, 75016 Paris, France</p>"""
    (OUT / ("index.html" if lang == "fr" else "en.html")).write_text(page(t, body, lang, {"fr": "index.html", "en": "en.html"}, 0, tag), encoding="utf-8")
print("built")

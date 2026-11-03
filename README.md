# Pixel & Quill Studio website

Source of **https://pixelandquillstudio.com/**, the website of Pixel & Quill Studio, an independent game studio based in Paris. Built with [Astro](https://astro.build/) and deployed to GitHub Pages by GitHub Actions (`.github/workflows/deploy.yml`) on every push to `main`. The repository contains only sources; no generated HTML is committed.

## Sources

| Path | Content |
|---|---|
| `src/data/site.json` | Studio identity (name, address, email, phone), tagline, about text, founder note and the list of languages |
| `src/data/games.json` | The games, one entry per game |
| `src/data/i18n/<lang>.json` | Interface strings (menus, labels, buttons); a missing key falls back to English |
| `src/data/content/legal/<doc>.<lang>.md` | Studio-wide legal notice, privacy policy and terms of use (all games) |
| `src/data/content/games/<slug>.<lang>.md` | Game-specific details: age, services used, purchases, credits |
| `src/data/content/games/<slug>/<doc>.<lang>.md` | Game-specific privacy policy / terms (see `legal_docs`) |
| `public/assets/` | Stylesheet, fonts (SIL OFL 1.1), logos, game icons and screenshots (served as-is at `/assets/…`) |
| `public/CNAME` | GitHub Pages custom domain |
| `src/lib/site.ts` | Data loading, URL scheme, page list, legacy redirects, language-detection script |
| `src/layouts/Layout.astro` | Page shell: head (canonical, hreflang, Open Graph, Facebook verification), header, language switcher, footer |
| `src/components/` | Game card, games grid, legal "French version is binding" note |
| `src/pages/[...path].astro` | Every regular page in every language |
| `src/pages/404.astro`, `[legacy].html.ts`, `[dir]/[legacy].html.ts`, `sitemap.xml.ts`, `robots.txt.ts` | 404 page, old-URL redirect stubs, sitemap, robots.txt |

## Editing content

- **Texts on the pages**: interface strings are in `src/data/i18n/<lang>.json`; the studio texts (tagline, about, founder note) and contact details are in `src/data/site.json`; game texts are in `src/data/games.json`.
- **Legal documents**: edit `src/data/content/legal/<doc>.<lang>.md` (Markdown). Keep them identical to the legal texts bundled in the games. The French version is the binding one.
- **Images**: put them in `public/assets/` and reference them as `assets/...` in `games.json`.
- Push to `main`: the site is rebuilt and published automatically in about a minute.

## URL structure

| Page | English (default) | Other languages |
|---|---|---|
| Home | `/` | `/fr/` |
| Games | `/games/` | `/fr/games/` |
| A game | `/<slug>/` | `/fr/<slug>/` |
| Contact | `/contact/` | `/fr/contact/` |
| Legal notice | `/legal-notice/` | `/fr/legal-notice/` |
| Privacy policy | `/privacy/` | `/fr/privacy/` |
| Terms of use | `/terms/` | `/fr/terms/` |

Published languages: English (no prefix), French `/fr/`, Spanish `/es/`, Brazilian Portuguese `/pt-br/` and German `/de/`; every page above exists under each prefix. Game pages live at `/<slug>/` (for example `/sentence/`, `/one-last-heist/`).

In the Spanish, Portuguese and German legal documents, a note (`legal_binding_note` in `i18n/<code>.json`) states that only the French version is legally binding and links to it.

Every page lists its translations with `hreflang` links plus `x-default` (English). Old URLs from the first version of the site (`en.html`, `jeux/`, `contact.html`, `mentions-legales.html`, `sentence/privacy-fr.html`, etc.) are kept as redirect stubs to their new location.

## Language selection

1. A language chosen with the switcher is saved in the browser (`localStorage`, key `pq-lang`) and always wins.
2. Otherwise, on English pages only, the browser languages (`navigator.languages`) are checked in order. The first supported one decides: `fr*` goes to `/fr/…`, `es*` to `/es/…`, `pt*` to `/pt-br/…` and `de*` to `/de/…`; any other language stays in English.
3. Otherwise the page stays in English.

No cookie is set and nothing is sent to a server.

## Publishing a new language

1. Add `i18n/<code>.json` (copy `i18n/en.json` and translate it).
2. Add `content/legal/*.<code>.md` and `content/games/<slug>.<code>.md`; untranslated files fall back to English.
3. Add the `<code>` texts to `site.json` (`tagline`, `about`) and `games.json` (`name`, `subtitle`, `pitch`, `description`, `features`).
4. Set `"published": true` for the language in `src/data/site.json`, then push.

## Build

Requires Node.js 22.23 or later (CI uses Node 24).

```sh
npm ci
npm run dev       # live preview at http://localhost:4321/
npm run build     # static output in dist/ (not committed)
npm run preview   # serve dist/
```

Deployment: `.github/workflows/deploy.yml` builds with `withastro/action` and publishes with `actions/deploy-pages` (Pages source: GitHub Actions).

## Adding a game

Add an entry to `src/data/games.json` (and its images to `public/assets/games/<slug>/`). The game page, its links on the home and games pages, its hreflang alternates and its sitemap entries are generated automatically:

| Field | Meaning |
|---|---|
| `slug` | URL segment, e.g. `sentence` → `/sentence/` |
| `name`, `subtitle`, `pitch` | Localized strings (`{"en": …, "fr": …}`) |
| `description`, `features` | Localized lists of paragraphs / bullet points |
| `status` | `in_development`, `in_production`, `coming_soon` or `available` |
| `status_label` | Optional `{lang: …}` text that replaces the default status label in the badge and the key facts (for example a release month) |
| `status_badge` | Optional short `{lang: …}` text for the status pill on the game cards and the game page header; keep it short enough to fit on one line on a 360 px phone (the full `status_label` stays in the key facts) |
| `icon` | Path to a square icon, e.g. `assets/games/<slug>/icon.webp` (file in `public/assets/`) |
| `store.google_play` | Store URL, or `null` until the game is released |
| `details` | Game-specific Markdown, e.g. `content/games/<slug>.{lang}.md` |
| `tagline` | Optional localized quote from the game, shown as a blockquote |
| `facts` | Optional list of `{"key": …, "value": {lang: …}}` shown in a "Key facts" box (`key` is `genre`, `platform`, `orientation`, `languages`, `prisons`, `character`, `leaderboards`, `model` or `age`, each with a `fact_<key>` label in `i18n/`) |
| `splash` | Optional `{"src", "width", "height", "alt": {lang: …}}` image shown next to the key facts |
| `gallery` | Optional `{"title": <i18n key>, "layout": "shots" (optional, portrait 9:16 screenshots), "images": [{"src", "width", "height", "alt", "caption"}]}` |
| `legal_docs` | Optional `{doc: "content/games/<slug>/<doc>.{lang}.md"}` (`doc` is `privacy` or `terms`). Each one becomes a game-specific page at `/<slug>/<doc>/` in every language (English fallback, French binding note on es/pt-BR/de) and replaces the matching studio-wide link on the game page |
| `legacy_paths` | Optional old URLs to redirect |

Then add `src/data/content/games/<slug>.<lang>.md` describing the minimum age, the services and data used by the game, its purchases and the in-game privacy settings. The studio-wide legal documents apply to every game; only add game-specific information to the game's page, or, when a game needs its own privacy policy or terms, to its `legal_docs` pages.

## Rules

- No personal data other than the publisher's business identity required by law.
- No trackers, analytics or cookies on the website.
- Everything in this repository (code, comments, docs) is written in English; only the translated site content is in other languages.

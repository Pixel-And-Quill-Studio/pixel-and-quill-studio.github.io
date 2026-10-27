# pixel-quill-studio.github.io

Site statique multi-jeux de **Pixel & Quill Studio** (GitHub Pages, FR + EN, aucun traceur, aucun cookie).
Les pages HTML sont **générées** par `build.py` à partir de `site.json` (le studio) et `games.json` (les jeux). Ne pas modifier les `.html` à la main.

## Structure du site

| Page | FR | EN |
|---|---|---|
| Accueil (studio + grille des jeux) | `/` | `/en.html` |
| Index des jeux | `/jeux/` | `/games/` |
| Page d’un jeu | `/<slug>/` | `/<slug>/en.html` |
| Documents légaux d’un jeu | `/<slug>/privacy-fr.html`, `/<slug>/terms-fr.html` | `/<slug>/privacy-en.html`, `/<slug>/terms-en.html` |
| Contact | `/contact.html` | `/contact-en.html` |
| Mentions légales (studio) | `/mentions-legales.html` | `/legal-notice.html` |

Les anciennes URLs de Sentence (`/sentence/privacy-fr.html`…) sont conservées : l’application y renvoie.

## Générer le site

```bash
pip install markdown
python3 build.py        # réécrit toutes les pages, sitemap.xml et robots.txt
git add -A && git commit -m "..." && git push
```

Les textes juridiques (Markdown) viennent du dépôt du jeu (`docs_dir` dans `games.json`, et `legal_notice.docs_dir` dans `site.json` pour les mentions légales du studio). Un chemin relatif est résolu depuis ce dépôt. Si le dossier est ailleurs sur ta machine, adapte le chemin.

## Ajouter un jeu

1. **Ajouter une entrée dans `games.json`** (copier celle de `sentence`) :

   | Champ | Rôle |
   |---|---|
   | `slug` | Dossier et URL du jeu (`/<slug>/`). Minuscules, sans espace. |
   | `name`, `subtitle`, `pitch` | Titre, sous-titre et accroche, `{"fr": "…", "en": "…"}`. |
   | `description`, `features` | Paragraphes et points forts de la page du jeu (listes de textes FR/EN). |
   | `status` | `coming_soon` (« Bientôt sur Google Play »), `available` ou `in_development`. |
   | `icon` | Chemin de l’icône, relatif à la racine du site (ex. `assets/<slug>-icon.png`, carré, 512 px conseillé). |
   | `store.google_play` | URL de la fiche Google Play, ou `null` tant que le jeu n’est pas publié. Un bouton apparaît dès qu’elle est renseignée. |
   | `docs_dir` | Dossier des documents Markdown du jeu (absolu, ou relatif à ce dépôt). |
   | `docs` | `{"privacy": {"fr": "fichier.md", "en": "fichier.md"}, "terms": {…}}`. Chaque type produit `/<slug>/<type>-fr.html` et `-en.html`. Types disponibles : `privacy`, `terms` (ajouter un libellé dans `T` de `build.py` pour un autre type). |

2. Déposer l’icône dans `assets/`.
3. Lancer `python3 build.py`, ouvrir le site en local (`python3 -m http.server`) et vérifier la page d’accueil, `/jeux/` et `/<slug>/`.
4. Commit et push. La grille de l’accueil et l’index des jeux se mettent à jour seuls.

Pour changer l’identité du studio (adresse, SIREN, e-mail, texte de présentation), modifier `site.json` ; les mentions légales sont dans `legal_notice_{fr,en}.md` du dépôt de docs.

## Règles

- Jamais d’adresse personnelle, de téléphone, de date de naissance, de numéro de sécurité sociale ni d’e-mail personnel sur le site.
- Pas de traceur, pas de police ni de script externe.
- Polices : Playfair Display SC et Allerta Stencil (SIL OFL 1.1, voir `assets/FONTS_LICENSE.txt`). Logo : `assets/brand/`.

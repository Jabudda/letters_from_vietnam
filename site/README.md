# Website

The public website: a home page with the whole collection, and one page per published letter showing the reading edition beside scans of the original pages.

It is built from the archive by `scripts/build_site.py` and published to GitHub Pages by `.github/workflows/pages.yml` on every push to `main`.

**A letter gets a page only when** its `status.transcription` is `verified`, `privacy.reviewed` is `true`, `reading.md` exists, and its web images are in `site/scans/NNN/`. Every other letter is listed as *being prepared*.

| Path | Holds |
| --- | --- |
| `templates/index.html`, `templates/letter.html` | Page templates (`{{PLACEHOLDERS}}` are filled by the build). |
| `static/` | Styles, script, favicon and self-hosted fonts (EB Garamond, Caveat, IBM Plex Mono; SIL Open Font License). |
| `scans/NNN/` | Reduced, privacy-reviewed scan images made by `scripts/make_web_images.py`. |
| `_build/` | Build output (not committed). |

To preview locally:

```sh
pip install -r scripts/requirements.txt
python3 scripts/build_site.py
python3 -m http.server --directory site/_build 8000   # then open http://localhost:8000
```

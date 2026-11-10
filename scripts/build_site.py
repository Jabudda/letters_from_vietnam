#!/usr/bin/env python3
"""Build the public website into site/_build/ from the archive.

A letter gets its own page only when all of these are true:
  - status.transcription is "verified" (set by the family)
  - privacy.reviewed is true
  - archive/letters/NNN/reading.md exists
  - web images exist in site/scans/NNN/ (made by make_web_images.py)
Every other letter appears in the collection as "being prepared".

Usage: python3 scripts/build_site.py    (then open site/_build/index.html)
"""
import datetime as dt
import html
import re
import shutil
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = SITE / "_build"
LETTERS = ROOT / "archive" / "letters"
REPO_URL = "https://github.com/Jabudda/letters_from_vietnam"
# Changes whenever the stylesheet or script changes, so browsers fetch the new version.
import hashlib as _hashlib
ASSET_V = _hashlib.sha256(b"".join(p.read_bytes() for p in sorted((SITE / "static").glob("*/site.*")))).hexdigest()[:10]

MARK = re.compile(
    r"\[(unclear[^\]]*|illegible[^\]]*|possible reading:[^\]]*|crossed out:[^\]]*|inserted:[^\]]*|"
    r"withheld for privacy|page \d+[^\]]*|back of page[^\]]*|envelope (?:front|back)[^\]]*|drawing:[^\]]*|"
    r"underlined[^\]]*|written above[^\]]*)\]"
)


def fill(template, **values):
    values.setdefault("ASSET_V", ASSET_V)
    for k, v in values.items():
        template = template.replace("{{" + k + "}}", str(v))
    if left := re.findall(r"\{\{[A-Z_]+\}\}", template):
        raise SystemExit(f"Unfilled placeholders: {left}")
    return template


def nice_date(value):
    if not value:
        return None
    try:
        d = dt.date.fromisoformat(str(value))
        return f"{d:%B} {d.day}, {d.year}"
    except ValueError:
        return str(value)


def mark_up(rendered):
    return MARK.sub(lambda m: f'<span class="mark">{m.group(0)}</span>', rendered)


def notes_section(text, name):
    """Return the body of a '## name' section of a notes.md file, or ''."""
    m = re.search(rf"^## {re.escape(name)}[^\n]*\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M)
    return m.group(1).strip() if m else ""


def sources_for(lid):
    """Entries in research/sources.md that say they are cited in this letter, as (title, url, publisher)."""
    out = []
    for line in (ROOT / "research" / "sources.md").read_text().splitlines():
        cited = re.search(r"\(Cited in: ([^)]*)\)", line)
        if not line.startswith("- ") or not cited or lid not in re.findall(r"\d{3}", cited.group(1)):
            continue
        title = re.search(r"\*([^*]+)\*", line)
        url = re.search(r"https?://\S+?(?=\.?\s|\.?$)", line)
        publisher = line[2:].split(". *")[0]
        out.append((title.group(1) if title else publisher, url.group(0) if url else None, publisher))
    return out


def photos_for(lid):
    """Family photographs approved for publishing and linked to this letter (archive/photos/PNNN/photo.yml)."""
    out = []
    for path in sorted((ROOT / "archive" / "photos").glob("P*/photo.yml")):
        p = yaml.safe_load(path.read_text())
        if p.get("publish") == "approved" and lid in [str(x) for x in p.get("related_letters") or []] and p.get("web_copy"):
            out.append(p)
    return out


def photos_section(lid, root="../../../"):
    photos = photos_for(lid)
    if not photos:
        return ""
    def fig(p):
        src = root + p["web_copy"].removeprefix("site/")
        cap = html.escape(p.get("caption") or "")
        return (f'          <figure class="context-photo"><a href="{src}"><img src="{src}" alt="{html.escape(p.get("subject") or "")}" loading="lazy"></a>'
                f'<figcaption>{cap} <span>({html.escape(p["id"])}, family photograph)</span></figcaption></figure>')
    plain = [fig(p) for p in photos if not p.get("sensitive")]
    hard = [fig(p) for p in photos if p.get("sensitive")]
    parts = ['        <h3 class="context-sub" id="photographs">Photographs</h3>']
    if plain:
        parts.append('        <div class="context-photos">\n' + "\n".join(plain) + "\n        </div>")
    if hard:
        parts.append('        <details class="sensitive">\n'
                     '          <summary><strong>Content warning.</strong> These photographs, from Grandpa’s wartime pictures, '
                     'show the bodies of prisoners at the Dachau concentration camp in 1945. Select to view.</summary>\n'
                     '          <div class="context-photos">\n' + "\n".join(hard) + "\n          </div>\n        </details>")
    return "\n".join(parts)


LABELS = ("Verified fact", "Historical context", "Interpretation", "Unknown")


def context_section(rec):
    notes_path = rec["_dir"] / "notes.md"
    if not notes_path.exists():
        return ""
    text = notes_path.read_text()
    history = notes_section(text, "Historical notes")
    family = notes_section(text, "Family notes for the chapter")
    sources = sources_for(rec["id"])
    photos = photos_section(rec["id"])
    if not (history or family or sources or photos):
        return ""
    md = markdown.Markdown(extensions=["sane_lists"])
    parts = ['      <section class="context" id="history" aria-labelledby="history-title">',
             '        <h2 class="label" id="history-title">Historical notes</h2>',
             '        <p class="context-key">Each note is labeled: <strong>Verified fact</strong> (from the letter, the family or a record), '
             '<strong>Historical context</strong> (from a cited source), <strong>Interpretation</strong> (our reading, open to correction) '
             'or <strong>Unknown</strong>. A letter is never placed at an event just because the date or place is close.</p>']
    if history:
        parts.append('        <div class="context-notes">' + mark_up(md.convert(history)) + "</div>")
    if family:
        md.reset()
        parts.append('        <h3 class="context-sub">From the family</h3>')
        parts.append('        <div class="context-notes family">' + mark_up(md.convert(family)) + "</div>")
    if photos:
        parts.append(photos)
    if sources:
        parts.append('        <h3 class="context-sub">Sources</h3>\n        <ul class="context-sources">')
        for title, url, publisher in sources:
            t = html.escape(title)
            link = f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{t}</a>' if url else t
            pub = f" <span>({html.escape(publisher)})</span>" if publisher and publisher != title else ""
            parts.append(f"          <li>{link}{pub}</li>")
        parts.append("        </ul>")
    parts.append("      </section>")
    return "\n".join(parts)


def scan_files(rec):
    # PDF copies and second captures (role: duplicate) are not shown; the primary JPEG is.
    files = [f for f in rec["source"]["files"]
             if not f["file"].lower().endswith(".pdf") and f.get("role") != "duplicate"]
    def key(f):
        num = m.group(1) if (m := re.search(r"_(\d{4})", f["file"])) else f["file"]
        back = 1 if re.search(r"_a\d?(?:_|\.|$)", f["file"]) else 0  # front (_b) before back (_a)
        return (f.get("order") is None, f.get("order") or 0, num, back, f["file"])
    return sorted(files, key=key)


def load_letters():
    letters = []
    for path in sorted(LETTERS.glob("*/letter.yml")):
        rec = yaml.safe_load(path.read_text())
        lid = rec["id"]
        rec["_dir"] = path.parent
        rec["_published"] = (
            rec["status"]["transcription"] == "verified"
            and rec["privacy"]["reviewed"] is True
            and (path.parent / "reading.md").exists()
            and (SITE / "scans" / lid).is_dir()
        )
        letters.append(rec)
    return letters


def card(rec):
    lid, n = rec["id"], len(scan_files(rec))
    scans = f"{n} scan{'s' if n != 1 else ''}"
    if rec["_published"]:
        d = rec.get("details") or {}
        bits = [b for b in (rec.get("title"), nice_date(d.get("date_written"))) if b]
        meta = html.escape(" · ".join(bits) or scans)
        return (f'          <li><a class="letter-card" href="letters/{lid}/">'
                f'<span class="no">Letter</span><span class="num">{lid}</span>'
                f'<span class="meta">{meta}</span><span class="status">Read the letter</span></a></li>')
    status = {"needs-family-review": "In family review", "in-progress": "Being transcribed"}.get(
        rec["status"]["transcription"], "Being prepared")
    return (f'          <li><div class="letter-card"><span class="no">Letter</span><span class="num">{lid}</span>'
            f'<span class="meta">{scans}</span><span class="status">{status}</span></div></li>')


def letter_page(rec, template):
    lid, d = rec["id"], rec.get("details") or {}
    title = rec.get("title") or nice_date(d.get("date_written")) or f"Letter {lid}"
    written = nice_date(d.get("date_written")) or d.get("date_as_written")
    meta_items = [("Written", None if written == title else written),
                  ("To", d.get("recipient")), ("From", d.get("place")), ("Unit", d.get("unit"))]
    meta = "\n".join(f'        <div><dt>{k}</dt><dd>{html.escape(str(v))}</dd></div>' for k, v in meta_items if v)
    md = markdown.Markdown(extensions=["sane_lists"])
    reading = mark_up(md.convert((rec["_dir"] / "reading.md").read_text()))
    dip_path = rec["_dir"] / "diplomatic.md"
    diplomatic = ""
    if dip_path.exists():
        dip_text = re.sub(r"\A\s*<!--.*?-->\s*", "", dip_path.read_text(), flags=re.S)  # drop the editors' header comment
        dip = mark_up(html.escape(dip_text))
        diplomatic = ('        <details class="diplomatic"><summary>Exact transcription, as written</summary>\n'
                      f'          <div class="letter-text">{dip}</div>\n        </details>')
    items = []
    for i, f in enumerate(scan_files(rec), 1):
        stem = Path(f["file"]).stem.replace(" ", "_")
        role = (f.get("role") or "").replace("-", " ")
        if not role:  # fall back to the scan naming convention (docs/scan-naming.md)
            role = "back" if re.search(r"_a\d?(?:_|\.|$)", f["file"]) else ("front" if "_b" in f["file"] else "")
        num = m.group(1) if (m := re.search(r"_(\d{4})", f["file"])) else str(i)
        cap = f"Scan {num}" + (f", {role}" if role else "")
        alt = f"Letter {lid}, scan {num}" + (f" ({role})" if role else "") + ", original handwriting"
        items.append(f'          <li><figure><a href="../../scans/{lid}/{stem}.jpg">'
                     f'<img src="../../scans/{lid}/{stem}-thumb.jpg" alt="{html.escape(alt)}" loading="lazy"></a>'
                     f'<figcaption>{html.escape(cap)}</figcaption></figure></li>')
    desc = f"Letter {lid} from Dad’s Vietnam letter archive: the reading edition beside scans of the original pages."
    sub = rec.get("subtitle")
    heading = html.escape(title) + (f"<br><em>{html.escape(sub)}</em>" if sub else "")
    page_title = html.escape(title + (f" | {sub}" if sub else ""))
    context = context_section(rec)
    jump = ('      <p class="jump"><a href="notes/" target="_blank" rel="noopener">'
            'Read the historical notes and sources ↗</a></p>' if context else "")
    page = fill(template, ROOT="../../", TITLE=page_title, HEADING=heading, DESCRIPTION=html.escape(desc), ID=lid,
                META=meta, READING=reading, DIPLOMATIC=diplomatic, SCANS="\n".join(items), JUMP=jump)
    notes_page = None
    if context:
        notes_page = fill((SITE / "templates" / "notes.html").read_text(), ROOT="../../../",
                          TITLE="Historical notes: " + page_title, HEADING=heading, ID=lid,
                          DESCRIPTION=html.escape(f"Historical notes and sources for Letter {lid} from Dad’s Vietnam letter archive."),
                          CONTEXT=context)
    return page, notes_page


def main():
    letters = load_letters()
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SITE / "static", OUT / "static")
    (OUT / ".nojekyll").write_text("")

    published = [r for r in letters if r["_published"]]
    n_scans = sum(len([f for f in r["source"]["files"] if not f["file"].lower().endswith(".pdf")]) for r in letters)
    n_drafts = sum(1 for r in letters if r["status"]["transcription"] in {"prior-draft", "in-progress", "needs-family-review"})
    today = dt.date.today()
    index = fill((SITE / "templates" / "index.html").read_text(),
                 ROOT="", N_LETTERS=len(letters), N_PUBLISHED=len(published), N_DRAFTS=n_drafts,
                 N_SCANS=n_scans, REPO_URL=REPO_URL, UPDATED=f"{today:%B} {today.day}, {today.year}",
                 LETTER_CARDS="\n".join(card(r) for r in letters))
    (OUT / "index.html").write_text(index)

    template = (SITE / "templates" / "letter.html").read_text()
    for rec in published:
        lid = rec["id"]
        page_dir = OUT / "letters" / lid
        page_dir.mkdir(parents=True)
        page, notes_page = letter_page(rec, template)
        (page_dir / "index.html").write_text(page)
        if notes_page:
            (page_dir / "notes").mkdir()
            (page_dir / "notes" / "index.html").write_text(notes_page)
        shutil.copytree(SITE / "scans" / lid, OUT / "scans" / lid)

    not_found = index.split('<main id="main">')[0] + (
        '<main id="main" class="section"><p class="eyebrow">Not found</p>'
        '<h1>This page isn’t in the archive.</h1><p><a href="/letters_from_vietnam/">Return to the collection</a></p></main>'
        "</body></html>")
    (OUT / "404.html").write_text(not_found.replace('href="static/', 'href="/letters_from_vietnam/static/')
                                  .replace('src="static/', 'src="/letters_from_vietnam/static/'))
    print(f"Built {OUT.relative_to(ROOT)}: {len(letters)} letters, {len(published)} published")


if __name__ == "__main__":
    main()

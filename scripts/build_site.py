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

MARK = re.compile(
    r"\[(unclear[^\]]*|illegible[^\]]*|possible reading:[^\]]*|crossed out:[^\]]*|inserted:[^\]]*|"
    r"withheld for privacy|page \d+[^\]]*|envelope (?:front|back)|drawing:[^\]]*)\]"
)


def fill(template, **values):
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
        dip = mark_up(html.escape(dip_path.read_text()))
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
    return fill(template, ROOT="../../", TITLE=page_title, HEADING=heading, DESCRIPTION=html.escape(desc), ID=lid,
                META=meta, READING=reading, DIPLOMATIC=diplomatic, SCANS="\n".join(items))


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
        (page_dir / "index.html").write_text(letter_page(rec, template))
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

#!/usr/bin/env python3
"""Build the book (draft) from verified archive content.

    python3 scripts/build_book.py            # writes book/_build/book.html and the PDF

Only letters that are published on the website (transcription verified and
privacy reviewed) go in. Letters appear in the order they were written; dates
that are not exact use the sort dates in book/book.yml. Front and back matter
come from book/text/*.md and research/*.md. Nothing here invents content: titles
and family passages come from letter.yml and notes.md, or are left as marked
placeholders for the family.
"""
import datetime as dt
import html
import re
import sys
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
LETTERS = ROOT / "archive" / "letters"
SITE = ROOT / "site"
BOOK = ROOT / "book"
OUT = BOOK / "_build"
FONTS = SITE / "static" / "fonts"
PHOTOS = SITE / "static" / "photos"

MONTHS = "January February March April May June July August September October November December".split()


def md(text):
    return markdown.markdown(text, extensions=["tables", "attr_list"])


def section(notes, heading):
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", notes, re.M | re.S)
    return m.group(1).strip() if m else ""


def nice_date(v, short=False):
    if isinstance(v, (dt.date, dt.datetime)):
        return f"{MONTHS[v.month - 1]} {v.day}, {v.year}"
    if isinstance(v, str):
        v = v.split(" #")[0].strip()
        if short:  # drop archive annotations in brackets, e.g. "(envelope: ...)"
            v = re.sub(r"\s*\([^)]*\)", "", v).strip()
        return v
    return ""


def first_page_image(rec):
    files = (rec.get("source") or {}).get("files") or []
    pages = [f for f in files if f.get("role") == "page"]
    pages.sort(key=lambda f: (f.get("order") is None, f.get("order") or 0))
    for f in pages:
        stem = Path(f["file"]).stem
        p = SITE / "scans" / rec["id"] / f"{stem}.jpg"
        if p.exists():
            return p
    return None


def load(cfg):
    sort_dates = {str(k): v for k, v in (cfg.get("sort_dates") or {}).items()}
    exclude = {str(x) for x in cfg.get("exclude") or []}
    out = []
    for path in sorted(LETTERS.glob("*/letter.yml")):
        rec = yaml.safe_load(path.read_text())
        lid = rec["id"]
        d = path.parent
        ok = (rec["status"]["transcription"] == "verified" and rec["privacy"]["reviewed"] is True
              and (d / "reading.md").exists() and lid not in exclude)
        if not ok:
            continue
        det = rec.get("details") or {}
        dw = det.get("date_written")
        key = sort_dates.get(lid) or (dw if isinstance(dw, (dt.date, dt.datetime)) else None)
        if key is None:
            sys.exit(f"Letter {lid}: no exact date; add it to sort_dates in book/book.yml")
        notes = (d / "notes.md").read_text()
        rec.update(_dir=d, _key=key, _notes=notes, _reading=(d / "reading.md").read_text())
        out.append(rec)
    out.sort(key=lambda r: (r["_key"], r["id"]))
    return out


def clean_reading(text):
    # drop the transcription's own HTML comments, and an opening italic archive note about the folder
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()
    return re.sub(r"\A\*This folder[^\n]*\*\s*\n", "", text).strip()


def clean_family(text):
    # for print: drop the archive's date stamps and markdown escapes
    text = re.sub(r"\s\(\d{4}-\d{2}-\d{2}\)", "", text)
    text = re.sub(r"\s*\(Andy,? \d{4}-\d{2}-\d{2}\)", "", text)
    return text.replace('\\"', '"')


def envelope_image(rec):
    files = (rec.get("source") or {}).get("files") or []
    for f in files:
        if f.get("role") == "envelope-front":
            p = SITE / "scans" / rec["id"] / f"{Path(f['file']).stem}.jpg"
            if p.exists():
                return p
    return None


def letter_html(rec, photos_after, suggested):
    lid = rec["id"]
    det = rec.get("details") or {}
    title = rec.get("title")
    title = title.split(" #")[0].strip() if isinstance(title, str) else None
    title = title or suggested.get(lid)
    date = nice_date(det.get("date_written"), short=True) or "Undated"
    to = nice_date(det.get("recipient"), short=True)
    place = nice_date(det.get("place"), short=True) or None
    head = [f'<p class="letter-no">Letter {lid}</p>']
    if title:
        head.append(f'<h2 class="letter-title">{html.escape(title)}</h2>')
    else:
        head.append('<h2 class="letter-title placeholder">[Title to be chosen by the family]</h2>')
    meta = [f"<span>{html.escape(date)}</span>"] if date else []
    if to:
        meta.append(f"<span>To {html.escape(to)}</span>")
    if place:
        meta.append(f"<span>From {html.escape(place)}</span>")
    head.append(f'<p class="letter-meta">{" · ".join(meta)}</p>')
    env = envelope_image(rec)
    if env:
        head.append(f'<figure class="envelope"><img src="{env.as_uri()}" alt=""></figure>')
    body = md(clean_reading(rec["_reading"]))
    fam = section(rec["_notes"], "Family notes for the chapter")
    fam_html = ""
    chunks = re.split(r"^### +(.+)$", fam, flags=re.M)
    main, subs = chunks[0].strip(), list(zip(chunks[1::2], chunks[2::2]))
    if main and not main.startswith("(None"):
        fam_html = f'<aside class="family"><h3>From the family</h3>{md(clean_family(main))}</aside>'
    for head_, body_ in subs:
        fam_html += f'<aside class="sidebar"><h3>{html.escape(head_.strip())}</h3>{md(clean_family(body_.strip()))}</aside>'
    img = first_page_image(rec)
    fac = ""
    if img:
        fac = (f'<figure class="facsimile"><img src="{img.as_uri()}" alt="">'
               f'<figcaption>The first page of Letter {lid}, from the family’s scan.</figcaption></figure>')
    extra = ""
    for p in photos_after.get(lid, []):
        extra += (f'<figure class="photo"><img src="{(PHOTOS / p["file"]).as_uri()}" alt="">'
                  f'<figcaption>{html.escape(p["caption"])}</figcaption></figure>')
    return (f'<section class="letter" id="letter-{lid}">{"".join(head)}'
            f'<div class="reading">{body}</div><p class="ornament">✦</p>{fam_html}{fac}{extra}</section>')


def notes_html(letters):
    parts = ['<section class="backmatter notes-on-letters"><h1>Notes on the letters</h1>'
             '<p class="intro">What is known about the people, places and events in each letter, '
             'with sources. Each statement is labeled as a fact (from the letter, a record or the family), '
             'historical context, interpretation, or unknown.</p>']
    for r in letters:
        h = section(r["_notes"], "Historical notes")
        if not h:
            continue
        date = nice_date((r.get("details") or {}).get("date_written"))
        parts.append(f'<h2>Letter {r["id"]} <span class="date">{html.escape(date)}</span></h2>{md(h)}')
    parts.append("</section>")
    return "".join(parts)


def research_html(name, title, drop_cols=()):
    text = (ROOT / "research" / name).read_text()
    text = re.sub(r"^# .*\n", "", text, count=1)
    # first paragraph is working notes about the file; keep tables and sections
    text = re.sub(r"`([^`]*)`", r"\1", text)
    # drop the archive's working note (the paragraph(s) before the first table, list or heading)
    text = re.sub(r"\A\s*(?:(?![|#*-])[^\n]+\n)+", "", text)
    h = md(text)
    for col in drop_cols:
        h = drop_table_column(h, col)
    return f'<section class="backmatter"><h1>{title}</h1>{h}</section>'


def drop_table_column(h, name):
    def fix(table):
        rows = re.findall(r"<tr>(.*?)</tr>", table, re.S)
        if not rows:
            return table
        cells0 = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", rows[0], re.S)
        if name not in cells0:
            return table
        i = cells0.index(name)

        def strip_row(r):
            cells = re.findall(r"(<t[hd][^>]*>.*?</t[hd]>)", r, re.S)
            if i < len(cells):
                cells.pop(i)
            return "<tr>" + "".join(cells) + "</tr>"
        return re.sub(r"<tr>(.*?)</tr>", lambda m: strip_row(m.group(1)), table, flags=re.S)
    return re.sub(r"<table>.*?</table>", lambda m: fix(m.group(0)), h, flags=re.S)


def timeline_html():
    text = (ROOT / "research" / "timeline.md").read_text()
    rows = [l for l in text.splitlines() if l.startswith("| ") and not l.startswith("| Date") and not l.startswith("| ---")]
    def key(l):
        d = l.split("|")[1].strip()
        m = re.match(r"(\d{4})-(\d{2})(?:-(\d{2}))?", d)
        if m:
            return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 15))
        y = re.search(r"(19\d\d)", d)
        mon = next((i + 1 for i, n in enumerate(MONTHS) if n.lower() in d.lower()), 6)
        early = 2 if "early" in d.lower() else (11 if "late" in d.lower() else 15)
        return (int(y.group(1)) if y else 1969, mon, early)
    rows.sort(key=key)
    body = "\n".join(["| Date | | Event | Letter / source |", "| --- | --- | --- | --- |"] + rows)
    return f'<section class="backmatter timeline"><h1>Timeline</h1>{md(body)}</section>'


def text(name):
    return md((BOOK / "text" / name).read_text())


def main():
    cfg = yaml.safe_load((BOOK / "book.yml").read_text())
    letters = load(cfg)
    suggested = {str(k): v for k, v in (cfg.get("suggested_titles") or {}).items()}
    photos_after = {}
    for p in cfg.get("photos_after_letters") or []:
        photos_after.setdefault(str(p["letter"]), []).append(p)

    css = (BOOK / "book.css").read_text().replace("{{FONTS}}", FONTS.as_uri()).replace("{{BOOK}}", BOOK.as_uri())
    title = cfg["title"]
    today = dt.date.today().isoformat()
    parts_cfg = cfg["parts"]

    doc = [f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
           f"<style>{css}</style></head><body>"]
    cover = PHOTOS / cfg["cover_photo"]
    doc.append(f'<section class="cover"><div class="airmail"><div class="cover-inner"><p class="band">{html.escape(cfg.get("cover_band", ""))}</p><p class="kicker">{html.escape(cfg["kicker"])}</p>'
               f'<h1>{html.escape(title)}</h1><p class="subtitle">{html.escape(cfg["subtitle"])}</p>'
               f'<img src="{cover.as_uri()}" alt=""><p class="byline">{html.escape(cfg["byline"])}</p></div></div></section>')
    ifc = BOOK / cfg["inside_front_cover"]["file"]
    doc.append(f'<section class="inside-cover"><figure><img src="{ifc.as_uri()}" alt="">'
               f'<figcaption><span class="name">{html.escape(cfg["inside_front_cover"]["caption"])}</span>'
               f'<span class="full">{html.escape(cfg["inside_front_cover"]["subcaption"])}</span></figcaption></figure></section>')
    doc.append(f'<section class="title-page"><p class="kicker">{html.escape(cfg["kicker"])}</p><h1>{html.escape(title)}</h1>'
               f'<p class="subtitle">{html.escape(cfg["subtitle"])}</p><p class="byline">{html.escape(cfg["byline"])}</p></section>')
    doc.append(f'<section class="copyright">{md(cfg["copyright"])}<p class="draft-note">Draft built {today} from the family archive. '
               f'Not for distribution until the family approves it.</p></section>')
    ded = cfg["dedication"]
    doc.append(f'<section class="dedication"><figure><img src="{(PHOTOS / ded["photo"]).as_uri()}" alt="">'
               f'</figure><p>{ded["text"]}</p><p class="by">{html.escape(ded["by"])}</p></section>')
    # contents
    toc = ['<section class="toc"><h1>Contents</h1><ul>']
    for anchor, label in [("grandma", "You will figure it out"), ("why", "Why we keep them"), ("note", "A note on this book"),
                          ("overview", "Where he was, and what was happening"), ("map", "Map"),
                          ("stories", "Stories Dad told")]:
        toc.append(f'<li><a href="#{anchor}">{label}</a></li>')
    for part in parts_cfg:
        toc.append(f'<li class="part"><a href="#part-{part["id"]}">{html.escape(part["title"])}</a></li>')
    for anchor, label in [("epilogue", "Epilogue"), ("notes", "Notes on the letters"), ("timeline", "Timeline"),
                          ("glossary", "Glossary"), ("people", "People and places"), ("sources", "Sources"),
                          ("ack", "Acknowledgments"), ("invite", "Keep your own family’s letters")]:
        toc.append(f'<li><a href="#{anchor}">{label}</a></li>')
    toc.append("</ul></section>")
    doc.append("".join(toc))
    doc.append(f'<section class="front grandma" id="grandma">{text("grandma.md")}</section>')
    doc.append(f'<section class="front" id="why">{text("why.md")}</section>')
    doc.append(f'<section class="front" id="note">{text("editors-note.md")}</section>')
    doc.append(f'<section class="front" id="overview">{text("historical-overview.md")}</section>')
    svg = (ROOT / "scripts" / "map" / "letters-map.svg").read_text()
    map_css = css.split("/* map (from the website) */", 1)[-1].replace('"Plex Mono", monospace', '"IBM Plex Mono", monospace')
    svg = re.sub(r"(<svg[^>]*>)", lambda m: m.group(1) + f"<style>{map_css}</style>", svg, count=1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "map.svg").write_text(svg)
    import subprocess
    subprocess.run(["rsvg-convert", "-w", "2700", "-o", str(OUT / "map.png"), str(OUT / "map.svg")], check=True)
    from PIL import Image
    Image.open(OUT / "map.png").rotate(90, expand=True).save(OUT / "map-rotated.png")
    doc.append(f'<section class="front map" id="map"><h1>Where the letters were written</h1><img class="rotated" src="{(OUT / 'map-rotated.png').as_uri()}" alt=""><p class="map-caption">Places named in the letters, with the letters that name them. Map drawn for the family archive from public map data.</p></section>')
    stories = (BOOK / "text" / "stories.md").read_text()
    stories = re.sub(r"\]\(\.\./\.\./site/static/photos/([^)]+)\)", lambda m: f"]({(PHOTOS / m.group(1)).as_uri()})", stories)
    doc.append(f'<section class="front stories" id="stories">{md(stories)}</section>')

    # parts and letters
    for part in parts_cfg:
        start, end = part["from"], part["to"]
        members = [r for r in letters if start <= r["_key"] <= end]
        doc.append(f'<section class="part-title" id="part-{part["id"]}"><p class="part-no">{html.escape(part["label"])}</p>'
                   f'<h1>{html.escape(part["title"])}</h1><p class="part-dates">{html.escape(part["dates"])}</p>'
                   + (f'<blockquote class="epigraph"><p>“{html.escape(part["epigraph"])}”</p><cite>{html.escape(part["epigraph_from"])}</cite></blockquote>' if part.get("epigraph") else "")
                   + '</section>')
        for r in members:
            doc.append(letter_html(r, photos_after, suggested))
    placed = {r["id"] for part in parts_cfg for r in letters if part["from"] <= r["_key"] <= part["to"]}
    missing = [r["id"] for r in letters if r["id"] not in placed]
    if missing:
        sys.exit(f"Letters outside every part's dates: {missing}")

    doc.append(f'<section class="backmatter" id="epilogue">{text("epilogue.md")}</section>')
    doc.append(f'<div id="notes">{notes_html(letters)}</div>')
    doc.append(f'<div id="timeline">{timeline_html()}</div>')
    doc.append(f'<div id="glossary">{research_html("glossary.md", "Glossary", drop_cols=("Source",))}</div>')
    doc.append(f'<div id="people">{research_html("people-and-places.md", "People and places")}</div>')
    doc.append(f'<div id="sources">{research_html("sources.md", "Sources")}</div>')
    doc.append(f'<section class="backmatter" id="ack">{text("acknowledgments.md")}</section>')
    doc.append(f'<section class="backmatter" id="invite">{text("invitation.md")}</section>')
    doc.append("</body></html>")

    OUT.mkdir(parents=True, exist_ok=True)
    out_html = OUT / "book.html"
    out_html.write_text("".join(doc))
    from weasyprint import HTML
    pdf = OUT / cfg["pdf_name"]
    HTML(filename=str(out_html)).write_pdf(str(pdf))
    print(f"Built {pdf.relative_to(ROOT)}: {len(letters)} letters")


if __name__ == "__main__":
    main()

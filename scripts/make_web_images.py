#!/usr/bin/env python3
"""Make reduced, privacy-safe web images of a letter's scans.

Reads the master scans (never modifies them), and for each file listed in the
letter's letter.yml writes:
  site/scans/NNN/<name>.jpg        long edge 2400 px, for reading
  site/scans/NNN/<name>-thumb.jpg  long edge 600 px, for lists
with all metadata (including phone GPS) stripped and every privacy.redact box
covered.

Refuses to run for a letter unless privacy.reviewed is true in its letter.yml.

Usage:
  pip install -r scripts/requirements.txt
  python3 scripts/make_web_images.py --masters "/path/to/11_10_2026_Dads_Letters" 018 [019 ...]
"""
import argparse
import hashlib
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageOps

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:  # only needed for Letters 43-47
    register_heif_opener = None

Image.MAX_IMAGE_PIXELS = None  # 1200 dpi scans are large on purpose

ROOT = Path(__file__).resolve().parent.parent
SIZES = {"": 2400, "-thumb": 600}
COVER = (236, 229, 214)  # archival-paper tone


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def export_letter(letter_id, masters, out_root, force):
    rec = yaml.safe_load((ROOT / "archive" / "letters" / letter_id / "letter.yml").read_text())
    if not rec["privacy"]["reviewed"] and not force:
        print(f"{letter_id}: skipped, privacy.reviewed is false (see docs/privacy.md)")
        return False
    folder = masters / rec["source"]["master_folder"]
    redact = rec["privacy"].get("redact") or []
    out_dir = out_root / letter_id
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in rec["source"]["files"]:
        src = folder / f["file"]
        if f["file"].lower().endswith(".pdf"):
            continue  # duplicate PDF copy; the JPEG is used instead
        if f.get("role") == "duplicate":
            continue  # second capture of a page already exported
        if sha256(src) != f["sha256"]:
            sys.exit(f"{letter_id}: {f['file']} does not match its checksum; stopping. Check the master copy.")
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            draw = ImageDraw.Draw(im)
            for r in redact:
                if r["file"] == f["file"]:
                    draw.rectangle(r["box"], fill=COVER)
            if f.get("rotate"):  # e.g. an envelope scanned upside down; boxes above use the stored orientation
                im = im.rotate(f["rotate"], expand=True)
            stem = Path(f["file"]).stem.replace(" ", "_")
            for suffix, edge in SIZES.items():
                copy = im.copy()
                copy.thumbnail((edge, edge), Image.LANCZOS)
                # Saving without exif/icc arguments writes no metadata.
                copy.save(out_dir / f"{stem}{suffix}.jpg", "JPEG", quality=82, optimize=True, progressive=True)
        print(f"{letter_id}: {f['file']} done")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--masters", required=True, type=Path, help="folder holding the master scans")
    ap.add_argument("--out", type=Path, default=ROOT / "site" / "scans")
    ap.add_argument("--force", action="store_true", help="export even if privacy.reviewed is false (for private review copies only; never commit them)")
    ap.add_argument("letters", nargs="+", help="letter ids, e.g. 001 018")
    args = ap.parse_args()
    for lid in args.letters:
        export_letter(f"{int(lid):03d}", args.masters, args.out, args.force)


if __name__ == "__main__":
    main()

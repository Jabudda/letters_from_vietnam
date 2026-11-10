#!/usr/bin/env python3
"""Rebuild archive/inventory.csv from every archive/letters/NNN/letter.yml."""
import csv
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LETTERS = ROOT / "archive" / "letters"
OUT = ROOT / "archive" / "inventory.csv"


def scan_numbers(files):
    nums = sorted({int(m.group(1)) for f in files if (m := re.search(r"Letters_(\d{4})", f["file"]))})
    if not nums:
        return ""
    return f"{nums[0]:04d}" if nums[0] == nums[-1] else f"{nums[0]:04d}-{nums[-1]:04d}"


def main():
    rows = []
    for path in sorted(LETTERS.glob("*/letter.yml")):
        rec = yaml.safe_load(path.read_text())
        files = rec["source"]["files"]
        d = rec.get("details") or {}
        rows.append({
            "id": rec["id"],
            "title": rec.get("title") or "",
            "folder_label": rec.get("folder_label") or "",
            "date_written": d.get("date_written") or "",
            "recipient": d.get("recipient") or "",
            "transcription": rec["status"]["transcription"],
            "chapter": rec["status"]["chapter"],
            "privacy_reviewed": rec["privacy"]["reviewed"],
            "files": len(files),
            "capture": rec["source"]["capture"],
            "scan_numbers": scan_numbers(files),
            "master_folder": rec["source"]["master_folder"],
            "prior_draft": (rec.get("prior_draft") or {}).get("file", ""),
        })
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(rows)} letters")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Check the archive before committing.

- every letter.yml parses and has the required fields and allowed statuses;
- every file listed in a letter.yml matches archive/checksums-sha256.txt, and every checksum is used once;
- archive/inventory.csv is up to date;
- no master-scan formats or oversized files are in the repo;
- nothing in the repo looks like a phone number or a street address line from the envelopes.
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTION = {"none", "prior-draft", "in-progress", "needs-family-review", "verified"}
CHAPTER = {"not-started", "drafted", "approved"}
ROLES = {None, "page", "envelope-front", "envelope-back", "enclosure", "duplicate"}
MAX_BYTES = 5 * 1024 * 1024
BLOCKED_EXT = {".tif", ".tiff", ".heic", ".pdf"}
PHONE = re.compile(r"(?<!\d)(\(?\d{3}\)?[ .-])?\d{3}-\d{4}(?!\d)")
STREET = re.compile(r"\b\d{3,5}\s+(?:[NSEW]\.?|West|East|North|South)\s+\w+\s+(?:Pl|Place|St|Street|Ave|Avenue|Rd|Road|Dr|Drive|Ct|Court|Ln|Lane)\b", re.I)

errors = []


def err(msg):
    errors.append(msg)


def check_letters():
    sums = {}
    for line in (ROOT / "archive" / "checksums-sha256.txt").read_text().splitlines():
        h, p = line.split("  ", 1)
        sums[p] = h
    used = set()
    for path in sorted((ROOT / "archive" / "letters").glob("*/letter.yml")):
        where = path.relative_to(ROOT)
        try:
            rec = yaml.safe_load(path.read_text())
        except yaml.YAMLError as e:
            err(f"{where}: does not parse: {e}")
            continue
        if rec.get("id") != path.parent.name:
            err(f"{where}: id {rec.get('id')!r} does not match folder")
        st = rec.get("status") or {}
        if st.get("transcription") not in TRANSCRIPTION:
            err(f"{where}: bad status.transcription {st.get('transcription')!r}")
        if st.get("chapter") not in CHAPTER:
            err(f"{where}: bad status.chapter {st.get('chapter')!r}")
        if st.get("chapter") == "approved" and st.get("transcription") != "verified":
            err(f"{where}: chapter approved but transcription not verified")
        if not isinstance((rec.get("privacy") or {}).get("reviewed"), bool):
            err(f"{where}: privacy.reviewed must be true or false")
        folder = rec["source"]["master_folder"]
        for f in rec["source"]["files"]:
            key = f"{folder}/{f['file']}"
            if key not in sums:
                err(f"{where}: {f['file']} not in checksums")
            elif sums[key] != f.get("sha256"):
                err(f"{where}: {f['file']} sha256 differs from checksums")
            if f.get("role") not in ROLES:
                err(f"{where}: {f['file']} has unknown role {f.get('role')!r}")
            used.add(key)
    for key in sorted(set(sums) - used):
        err(f"checksums: {key} is not listed in any letter.yml")


def check_inventory():
    inv = ROOT / "archive" / "inventory.csv"
    before = inv.read_text() if inv.exists() else ""
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_inventory.py")], check=True, capture_output=True)
    if inv.read_text() != before:
        err("archive/inventory.csv was out of date; it has been rebuilt, so review and stage it")


def check_files():
    tracked = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split("\n")
    for name in filter(None, tracked):
        p = ROOT / name
        if not p.is_file():
            continue
        if p.suffix.lower() in BLOCKED_EXT:
            err(f"{name}: master-scan format; keep masters out of the repo")
        if p.stat().st_size > MAX_BYTES and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            err(f"{name}: image over 5 MB; publish reduced copies only")
        if p.suffix.lower() in {".md", ".yml", ".yaml", ".csv", ".txt", ".html"} and name != "archive/checksums-sha256.txt":
            text = p.read_text(errors="ignore")
            for rx, what in ((PHONE, "phone number"), (STREET, "street address")):
                if m := rx.search(text):
                    err(f"{name}: looks like a {what}: {m.group(0)!r} (see docs/privacy.md)")


def main():
    check_letters()
    check_inventory()
    check_files()
    if errors:
        print("Problems found:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()

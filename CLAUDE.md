# Working in this repository

This is a family archive of Vietnam War letters, being turned into a free commemorative book and website. Read `README.md` first, then the rules in `docs/`. These instructions apply to any AI assistant working here.

## Non-negotiable rules

1. **Never invent.** No missing words, dates, places, names, units, events or later-life details. If it is not on the page or in a cited source, it is unknown.
2. **Never silently change his words.** The diplomatic transcription (`diplomatic.md`) keeps original spelling, punctuation, capitalization, slang and humor exactly. The reading edition (`reading.md`) allows only the minimal changes listed in `docs/transcription-guide.md`, and every change is logged. Keep his contractions and expressions ("I'm", "hey?", "gang", "Ha").
3. **Flag uncertainty** with `[unclear]`, `[illegible]` or `[possible reading: …]`. Do not guess silently.
4. **Family corrections are authoritative.** Record them in the letter's `notes.md` revision log, with who gave them and when. Change them only if new evidence appears, and then raise it with the family rather than overwriting.
5. **Label every historical claim** as Verified fact, Historical context, Interpretation or Unknown, with a source. Never place the writer at a battle or operation just because the date or place is close.
6. **Status gates.** Do not set `status.transcription: verified` or `status.chapter: approved` in `letter.yml` yourself. Only the family does that. Prepare the work and ask.
7. **Privacy.** Follow `docs/privacy.md`. Never commit master scans, home street addresses, phone numbers or service/ID numbers. Web images are produced only by `scripts/make_web_images.py`, which strips metadata and applies the redactions listed in `letter.yml`.
8. **Masters are read-only.** The master scans live outside this repo (Google Drive and a disk copy). Never modify, rename or move them. `archive/checksums-sha256.txt` is the fixity record.
9. **Generated art** must be captioned *AI-generated historical interpretation — not an original photograph.* and must never look like evidence of a real event or person.

## Layout

- `archive/letters/NNN/letter.yml`: metadata and status for letter NNN (always three digits).
- `archive/letters/NNN/diplomatic.md`, `reading.md`, `notes.md`: committed only once the family has verified the letter. Until then they live in `private/letters/NNN/` (git-ignored); see `docs/workflow.md`.
- `archive/inventory.csv`: one row per letter; regenerate with `python3 scripts/build_inventory.py` after editing any `letter.yml`.
- `research/`: shared sources, glossary, timeline, people and places.
- `book/`, `site/`: built from verified archive content only.

## Web images

`python3 scripts/make_web_images.py --masters <master folder> NNN` writes reduced copies to `site/scans/NNN/`. It checks each master against its checksum first.

## Website

`python3 scripts/build_site.py` builds `site/_build/`; GitHub Actions publishes it on every push to `main`. Letters appear only when verified and privacy-reviewed (see `site/README.md`).

## Before committing

Run `python3 scripts/validate.py`. It checks every `letter.yml`, the checksum list and the inventory, and fails if anything private-looking is staged.

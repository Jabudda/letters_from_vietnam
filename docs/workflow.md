# Working on a letter

Each letter moves through the same steps. Its folder is `archive/letters/NNN/`.

1. **Gather.** Check `letter.yml` lists every scan. Note what each one is (`role`: page, envelope front, envelope back, enclosure) and its page order.
2. **Transcribe.** Write `diplomatic.md` from the scans at full resolution, following `docs/transcription-guide.md`. If a prior draft exists, use it as a second reader: it helps with hard words, but the scan decides.
3. **Reading edition.** Write `reading.md` from `diplomatic.md`, with only the allowed changes, logged.
4. **Notes.** In `notes.md`, record:
   - the revision log (every correction: date, source, old and new reading);
   - open questions for the family;
   - historical notes, each labeled **Verified fact**, **Historical context**, **Interpretation** or **Unknown**, with sources;
   - terms, people and places to add to `research/`.
5. **Family review.** Set `status.transcription: needs-family-review` and send the family the open questions. Apply their answers.
6. **Privacy review.** Mark redaction boxes in `letter.yml` and set `privacy.reviewed: true` once checked.
7. **Approval.** The family sets `status.transcription: verified`.
8. **Chapter.** Draft the book chapter: letter identification, historical introduction (100–200 words), reading edition, manuscript images, historical notes, an illustration only if the letter offers a real scene, a labeled editorial reflection (100–200 words), and research notes.
9. **Publish.** Generate web images, update the timeline and the people-and-places index, rebuild `archive/inventory.csv`, and publish once the family approves the chapter (`status.chapter: approved`).

## Adding a newly found letter

Give it the next free number, add its scans to the master folders without renaming existing files, add their fingerprints to `archive/checksums-sha256.txt`, create its `letter.yml`, and start at step 1. Nothing that exists is renumbered.

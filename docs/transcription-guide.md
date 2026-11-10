# Transcription guide

Every letter gets two transcriptions, kept in its folder under `archive/letters/NNN/`.

| File | What it is | Who may change it |
| --- | --- | --- |
| `diplomatic.md` | An exact record of what is on the page: original spelling, punctuation, capitalization, abbreviations, line-skipping and layout notes. | Corrected only against the scan or by family review, and every change is logged in `notes.md`. |
| `reading.md` | The edition people read in the book and on the website. It follows the diplomatic text with the few changes allowed below. | The same rule: every change is logged. |

## Marks used in both

| Mark | Meaning |
| --- | --- |
| `[unclear]` | A word or words that can't be read with confidence. |
| `[illegible]` | Can't be read at all (damage, fading, ink blot). Add the length if known: `[illegible, 2 words]`. |
| `[possible reading: Theilke]` | The best reading, when it isn't certain. |
| `[crossed out: word]` | Words he struck through. |
| `[inserted: word]` | Words he added above the line or in a margin. |
| `[page 2]` | The start of each new page or side. Give the scan file in `notes.md`. |
| `[envelope front]`, `[envelope back]` | Envelope text, transcribed like the letter, with private details handled per `docs/privacy.md`. |
| `[drawing: description]` | A sketch, doodle or symbol. |

Never fill a gap with a guess that isn't marked. If a passage can't be read, say so.

## What the reading edition may change

Only these, and only where they help a reader:

1. **Paragraph breaks** where he clearly began a new subject.
2. **Obvious slips of the pen**, such as a doubled word ("the the"). Log each one.
3. **Spelling that would confuse a reader** may get a bracketed correction after the original, e.g. `alot [a lot]`. His spelling stays.
4. **Uncertainty marks** stay. They may be shortened in the book's layout, but never dropped.

It must **not**:

- Expand contractions ("I'm" stays "I'm") or remove his expressions ("hey?", "gang", "Ha", "burp").
- Add, remove or reorder sentences, or "improve" wording.
- Fix grammar, slang or period terms.
- Remove anything for tone. Hard passages stay. Privacy redactions are the only removals, and they are marked `[withheld for privacy]`.

## Family corrections

Family members know names, places and family words that no one else can read. Their corrections are authoritative:

- Record each one in the letter's `notes.md` revision log: date, who gave it, the old reading, the new reading.
- Apply it to both transcriptions.
- If later evidence seems to contradict it, raise it with the family. Don't overwrite it.

## Statuses

`status.transcription` in `letter.yml` moves through:

| Status | Meaning |
| --- | --- |
| `none` | Not started. |
| `prior-draft` | An earlier draft exists outside the repo (Google Drive, "Dads Letters Transcribed"). Useful for reference; not yet checked against the scans. |
| `in-progress` | Being transcribed or checked against the scans. |
| `needs-family-review` | Checked against every scan; open questions listed in `notes.md`. |
| `verified` | Approved by the family. Only the family sets this. |

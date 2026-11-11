# The book

The book is assembled from verified letters only, arranged by the date each letter was written (not by archive number).

Planned structure (from the project brief):

- **Front matter:** cover and title page; inside front cover: photo P009 of Dad, chosen by Andy, printed 2 × 3½ in (`book/images/P009-dad-print-2x3.5in-300dpi.jpg`; layout mock-up `book/images/inside-front-cover-preview.png`); dedication; family introduction; editor's note on the archive and transcription method; historical overview; map and timeline.
- **Main content:** one chapter section per letter, in date order, with occasional interludes on military life, friendship, homesickness, family and hopes for the future.
- **Closing sections:** epilogue; reflections; glossary; timeline; people and places index; sources; transcription method and correction history; acknowledgments; an invitation to readers to preserve their own family letters.

Nothing about the writer's life after service, or reflections attributed to relatives, is written without family contributions.

Outputs planned: print-ready PDF, digital PDF, EPUB and an editable master manuscript.

## Building the draft

```
python3 scripts/build_book.py
```

writes `book/_build/book.html` and `book/_build/letters-from-vietnam-draft.pdf` (6 × 9 in). Needs WeasyPrint and `rsvg-convert` (for the map).

| File | What it holds |
| --- | --- |
| `book/book.yml` | Title, cover, dedication, the four parts, sort dates for letters without an exact date, photos placed after letters. |
| `book/book.css` | Page size, type and layout. |
| `book/text/*.md` | Front and back matter: why we keep them, a note on this book, historical overview, stories Dad told, epilogue and acknowledgments (placeholders for the family), and an invitation to keep family letters. |

Each letter's chapter is its `reading.md`, then its notes' "Family notes for the chapter" (any `###` subsections become boxed sidebars), then the first page of the scan. Each letter's "Historical notes" go in *Notes on the letters* at the back. Chapter titles come from `title` in `letter.yml`; untitled letters show a marked placeholder until the family chooses titles.

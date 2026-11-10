# Where the master scans are and how they are named

## Locations

| Copy | Location | Notes |
| --- | --- | --- |
| Primary | Google Drive: `Dads Letters Raw Scans Complete` | Shared within the family. |
| Disk copy | `11_10_2026_Dads_Letters` (from the family's ISO image) | Verified against Drive on 2026-11-10: same 274 files, same sizes, same SHA-256 fingerprints. |

Both are arranged the same way: six group folders (`Letter 1 - 10`, `Letter 11 - 19`, `Letter 20 - 29`, `Letter 30 - 35`, `Letter 36 - 42`, `Letter 43 - 47`), each holding one folder per letter. One difference: Letter 15's folder is `Letter 15_Kathy` in Drive and `Letter 15` on disk.

## Checking a copy

`archive/checksums-sha256.txt` lists every master file with its SHA-256 fingerprint. To check a copy on a Mac:

```sh
cd "/path/to/11_10_2026_Dads_Letters"
shasum -a 256 -c /path/to/letters_from_vietnam/archive/checksums-sha256.txt
```

Every line should end in `OK`. Run this after copying the masters anywhere new, and once a year as a health check.

## File names

**Letters 1–42** are flatbed scans (1200 dpi JPEG), numbered in one running sequence `Dads_Vietnam_Letters_0001` to `0228`:

| Ending | Meaning |
| --- | --- |
| `_b` | The front of the item (letter page, or envelope front). Most pages have only `_b`. |
| `_a` | The back of the same item. Checked on Letter 11, where `_b` is the envelope front and `_a` the envelope back. |
| `_a1`, `_a2` | One side scanned in two parts (Letter 7, item 0035). |
| no ending | An item scanned once (0036, 0037, 0159). |
| `_Petey` | Added to the Letter 18 item addressed to Petey. |

Numbers missing from the sequence: **0038, 0039 and 0162**. Letters 30 and 31 interleave (30: 0157, 0158, 0161; 31: 0159, 0160, 0163, 0164). Both are open questions for the family.

**Letters 43–47** are phone photos (HEIC, plus one JPG), named `Letter_00N_Page_NN`. The `001`–`005` in those names is an earlier batch numbering: `Letter_001_…` is archive Letter 043, through `Letter_005_…` = Letter 047.

Letter 1 also holds `Dads_Vietnam_Letters_0004_b copy.pdf`, a PDF copy of page 0004.

## Archive numbers

Letter numbers (001–047) follow the order of the folders, not the order the letters were written. Dates are worked out as each letter is transcribed, and the book is arranged by date. Archive numbers never change once given; a newly found letter gets the next free number.

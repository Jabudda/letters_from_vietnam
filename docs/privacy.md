# Privacy rules

This is a public repository and the website will be public. The family decides what is shared. These rules set the defaults.

## Never published

- **Master scans.** They stay in Google Drive and the disk copy. Only reduced web images are published.
- **Home street addresses and phone numbers.** They appear on envelopes and envelope backs; for example, the backs of some envelopes carry later handwritten phone numbers.
- **Service numbers, Social Security numbers or other ID numbers**, if any appear.
- **Image metadata.** Photos taken on a phone can carry GPS location and device details. `scripts/make_web_images.py` strips all metadata.

In transcriptions these become `[withheld for privacy]`. In web images the area is covered, using the `privacy.redact` boxes in `letter.yml`.

## Kept, because they are the history

- The writer's name, unit and APO address. These identify where letters came from and are part of the historical record.
- City and state of the family home.
- Names of family members as he wrote them.

## Handled with care

- **Names of people who were killed or wounded.** These are part of the history and are often already in public records, but their families may still be living. Confirm names against public sources (for example, the Vietnam Veterans Memorial Fund's Wall of Faces) before publishing, and write about them with respect.
- **Living people** mentioned in the letters (friends, neighbors, relatives). Publish their first names as written. If a passage would embarrass or hurt a living person, the family decides whether to withhold it, and the withholding is marked.
- **Material from other people**, such as letters written *to* him or photos taken by others: publish only with permission.

## Before a letter goes public

`privacy.reviewed` in `letter.yml` must be `true`. That means someone has looked at every scan and every transcription line for the items above. `make_web_images.py` refuses to export images for a letter that hasn't been reviewed.

Redaction boxes (`privacy.redact`) are given in pixels of the full-size scan as it appears upright. Some scans are stored rotated, and the script turns them upright before covering the box.

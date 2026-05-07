---
name: heic-to-jpeg
description: Convert iPhone HEIC/HEIF images to widely-compatible JPEG, preserving EXIF metadata and orientation. Use whenever the user wants to "convert HEIC", "convert iPhone photos", "convert iPhone format", "make these photos JPEGs", "fix HEIC files", "open HEIC on Windows", "batch convert .heic", "HEIF to JPG", "iPhone images won't open", or mentions a folder of .heic files they want as .jpg. Also triggers on "convert all images from iPhone", "iPhone photos to JPEG", or any request involving .heic / .heif extensions where the user wants standard image files. Handles single files or whole directories (recursive optional), preserves EXIF, skips already-converted files by default, and auto-installs `pillow` + `pillow-heif` if missing. Always invoke this rather than writing a one-off script — the bundled script handles edge cases like multi-image HEIC sequences, EXIF orientation, and idempotent reruns.
---

# HEIC → JPEG

Run the bundled script. Defaults: quality 95, non-recursive, originals kept in place.

```powershell
python <skill-path>/scripts/convert_heic.py "<folder-or-file>" [options]
```

Options:
- `--quality N` — JPEG quality 1–100 (default 95)
- `--recursive` — descend into subfolders
- `--overwrite` — re-convert files even if a `.jpg` already exists
- `--archive-originals` — move `.heic` files to a `heic-originals/` subfolder after success
- `--output DIR` — write `.jpg` files to DIR instead of next to source

The script auto-installs `pillow` and `pillow-heif` if missing, applies EXIF orientation before saving (iPhone HEICs set the orientation flag rather than rotating pixels — naive conversion produces sideways images), preserves EXIF metadata, and skips already-converted files unless `--overwrite` is passed.

Don't delete originals automatically. If the user wants them out of the way, use `--archive-originals` so they're recoverable.

"""Convert HEIC/HEIF images to JPEG, preserving EXIF and orientation.

Usage:
    python convert_heic.py <path> [--quality N] [--recursive] [--overwrite]
                                  [--archive-originals] [--output DIR]

The script auto-installs `pillow` and `pillow-heif` if missing so a user can run
it without preparing an environment first.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def ensure_dependencies() -> None:
    """Install pillow and pillow-heif if either is missing.

    pillow-heif registers a HEIF opener with PIL on import, so both must be
    importable before the script proceeds.
    """
    missing: list[str] = []
    try:
        import PIL  # noqa: F401
    except ImportError:
        missing.append("pillow")
    try:
        import pillow_heif  # noqa: F401
    except ImportError:
        missing.append("pillow-heif")

    if not missing:
        return

    print(f"Installing missing dependencies: {', '.join(missing)} ...", flush=True)
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--quiet", *missing]
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert HEIC/HEIF images to JPEG.")
    p.add_argument("path", help="File or directory containing .heic/.heif files")
    p.add_argument(
        "--quality", type=int, default=95,
        help="JPEG quality 1-100 (default: 95)",
    )
    p.add_argument(
        "--recursive", action="store_true",
        help="Recurse into subdirectories",
    )
    p.add_argument(
        "--overwrite", action="store_true",
        help="Re-convert files even if a .jpg already exists",
    )
    p.add_argument(
        "--archive-originals", action="store_true",
        help="After successful conversion, move .heic originals into a "
             "'heic-originals' subfolder beside them",
    )
    p.add_argument(
        "--output", type=str, default=None,
        help="Output directory (default: write .jpg next to each .heic)",
    )
    return p.parse_args()


def discover_files(root: Path, recursive: bool) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix.lower() in {".heic", ".heif"} else []
    pattern = "**/*" if recursive else "*"
    return sorted(
        f for f in root.glob(pattern)
        if f.is_file() and f.suffix.lower() in {".heic", ".heif"}
    )


def convert_one(
    src: Path,
    out_dir: Path | None,
    quality: int,
    overwrite: bool,
) -> tuple[str, Path | None, str]:
    """Convert a single HEIC file. Returns (status, output_path, message).

    status is one of: 'converted', 'skipped', 'failed'.
    """
    from PIL import Image, ImageOps

    target_dir = out_dir if out_dir is not None else src.parent
    dst = target_dir / (src.stem + ".jpg")

    if dst.exists() and not overwrite:
        return ("skipped", dst, "jpg already exists")

    try:
        with Image.open(src) as img:
            # Apply EXIF orientation so portraits stay upright. iPhone HEICs
            # almost always set the orientation flag rather than rotating
            # pixels, so a naive save produces sideways images.
            img = ImageOps.exif_transpose(img)

            exif_bytes = img.info.get("exif", b"")
            save_kwargs = {
                "quality": quality,
                "optimize": True,
            }
            if exif_bytes:
                save_kwargs["exif"] = exif_bytes

            # JPEG can't hold an alpha channel; flatten if present.
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            target_dir.mkdir(parents=True, exist_ok=True)
            img.save(dst, "JPEG", **save_kwargs)
        return ("converted", dst, "")
    except Exception as e:
        return ("failed", None, f"{type(e).__name__}: {e}")


def archive_original(src: Path, archive_dir: Path) -> None:
    archive_dir.mkdir(parents=True, exist_ok=True)
    target = archive_dir / src.name
    # Avoid clobbering if a same-named file already lives in the archive.
    counter = 1
    while target.exists():
        target = archive_dir / f"{src.stem} ({counter}){src.suffix}"
        counter += 1
    src.rename(target)


def main() -> int:
    args = parse_args()
    ensure_dependencies()

    # pillow-heif must be imported AFTER ensure_dependencies and BEFORE we use
    # PIL on a HEIC file — the import has the side effect of registering the
    # HEIF opener with Pillow.
    import pillow_heif  # noqa: F401
    pillow_heif.register_heif_opener()

    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        print(f"Error: path does not exist: {root}", file=sys.stderr)
        return 2

    out_dir = Path(args.output).expanduser().resolve() if args.output else None
    files = discover_files(root, args.recursive)
    if not files:
        print(f"No .heic/.heif files found in {root}")
        return 0

    print(f"Found {len(files)} HEIC/HEIF file(s). Converting at quality {args.quality}...")
    start = time.monotonic()

    converted: list[Path] = []
    skipped = 0
    failures: list[tuple[Path, str]] = []

    for i, src in enumerate(files, 1):
        status, dst, msg = convert_one(src, out_dir, args.quality, args.overwrite)
        if status == "converted":
            converted.append(src)
            print(f"  [{i}/{len(files)}] {src.name} -> {dst.name}")
        elif status == "skipped":
            skipped += 1
            print(f"  [{i}/{len(files)}] {src.name} (skipped: {msg})")
        else:
            failures.append((src, msg))
            print(f"  [{i}/{len(files)}] {src.name} FAILED: {msg}", file=sys.stderr)

    if args.archive_originals and converted:
        # Archive directory sits next to the originals (or the output dir if
        # specified) so it stays grouped with the conversion output.
        archive_root = (out_dir if out_dir is not None else root) / "heic-originals"
        print(f"\nArchiving {len(converted)} original(s) to {archive_root} ...")
        for src in converted:
            try:
                archive_original(src, archive_root)
            except Exception as e:
                print(f"  could not archive {src.name}: {e}", file=sys.stderr)

    elapsed = time.monotonic() - start
    print(
        f"\nDone in {elapsed:.1f}s — "
        f"converted: {len(converted)}, skipped: {skipped}, failed: {len(failures)}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

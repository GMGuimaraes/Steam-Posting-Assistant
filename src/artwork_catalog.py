#!/usr/bin/env python3
"""Create a read-only CSV inventory of artwork images.

This utility only reads local files. It does not connect to the internet,
open a browser, modify images, or interact with Steam.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
from pathlib import Path
from typing import Optional, Tuple

IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff"
}


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def image_dimensions(path: Path) -> Tuple[Optional[int], Optional[int]]:
    """Return dimensions with Pillow when available; otherwise blank values."""
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        return None, None

    try:
        with Image.open(path) as image:
            return int(image.width), int(image.height)
    except Exception:
        return None, None


def collect_images(root: Path, recursive: bool):
    iterator = root.rglob("*") if recursive else root.glob("*")
    for path in iterator:
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            yield path


def build_inventory(root: Path, recursive: bool):
    seen_hashes = {}
    for path in sorted(collect_images(root, recursive), key=lambda p: str(p).lower()):
        try:
            stat = path.stat()
            digest = sha256_file(path)
            width, height = image_dimensions(path)
            relative = path.relative_to(root)
            duplicate_of = seen_hashes.get(digest, "")
            if not duplicate_of:
                seen_hashes[digest] = str(relative)
            yield {
                "file_name": path.name,
                "relative_path": str(relative),
                "extension": path.suffix.lower(),
                "size_bytes": stat.st_size,
                "sha256": digest,
                "width": width if width is not None else "",
                "height": height if height is not None else "",
                "duplicate_of": duplicate_of,
            }
        except (OSError, ValueError) as exc:
            print(f"Warning: could not read {path}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a read-only CSV inventory of local artwork images."
    )
    parser.add_argument("folder", type=Path, help="Folder containing artwork images")
    parser.add_argument(
        "--output", type=Path, default=Path("artwork_inventory.csv"),
        help="CSV output path (default: artwork_inventory.csv)"
    )
    parser.add_argument(
        "--no-recursive", action="store_true",
        help="Scan only the selected folder, not its subfolders"
    )
    args = parser.parse_args()

    root = args.folder.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        parser.error(f"folder does not exist or is not a directory: {root}")
    if output == root or root in output.parents:
        parser.error("choose an output CSV outside the scanned artwork folder")

    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "file_name", "relative_path", "extension", "size_bytes",
        "sha256", "width", "height", "duplicate_of"
    ]
    count = 0
    with output.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in build_inventory(root, recursive=not args.no_recursive):
            writer.writerow(row)
            count += 1

    print(f"Cataloged {count} image(s).")
    print(f"CSV written to: {output}")
    if not _pillow_available():
        print("Tip: install Pillow to include image dimensions: python -m pip install Pillow")
    print("Source images were not changed.")
    return 0


def _pillow_available() -> bool:
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())

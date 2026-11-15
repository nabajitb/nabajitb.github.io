#!/usr/bin/env python3
"""Make the photo wall's thumbnails: thumbs/NNN.webp (640px wide) and thumbs-400/NNN.webp (400px wide, for phones).

Run from the repo root after adding a photo to assets/images/photos/. Only missing thumbnails are written; pass
--force to redo them all. Needs Pillow (pip install pillow).
"""
import sys
from pathlib import Path

from PIL import Image

PHOTOS = Path("assets/images/photos")
SIZES = {"thumbs": 640, "thumbs-400": 400}  # folder -> width in px; /photos/ lists both in srcset


def main():
    force = "--force" in sys.argv
    made = 0
    for full in sorted(PHOTOS.glob("*.webp")):
        for folder, width in SIZES.items():
            out = PHOTOS / folder / full.name
            if out.exists() and not force:
                continue
            out.parent.mkdir(exist_ok=True)
            with Image.open(full) as im:
                im = im.convert("RGB")
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
                im.save(out, "WEBP", quality=75, method=6)
            made += 1
    print(f"{made} thumbnail(s) written")


if __name__ == "__main__":
    main()

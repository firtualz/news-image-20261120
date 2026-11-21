#!/usr/bin/env python3
"""news-image-20261120 entrypoint: decode the entry image to the output dir.

The entry image is stored next to this file as base64 text
(`entry.png.b64`) because the image itself is binary and cannot travel
through a text-only channel. This script decodes that text back into the
PNG bytes, writes them to the output directory, and validates the result
(PNG header, width/height <= 1024, size <= 1 MiB).

Standard library only, no network, deterministic: the same bytes every run.
The image itself is drawn by render.py (Pillow, build time only).
"""
import base64
import os
import sys


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png.b64")
    dst = os.path.join(out_dir, "entry.png")
    with open(src, "r", encoding="ascii") as f:
        text = f.read()
    # The .b64 file is wrapped at 64 columns; strip all whitespace first
    # so strict base64 validation accepts it.
    data = base64.b64decode("".join(text.split()), validate=True)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit("decoded entry.png.b64 is not a PNG file")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if width > 1024 or height > 1024:
        sys.exit("decoded entry.png exceeds 1024x1024")
    if len(data) > 1024 * 1024:
        sys.exit("decoded entry.png exceeds 1 MiB")
    with open(dst, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Reproduce the news-image-20261120 v3 entry.

Reads the base64-encoded PNG bundled next to this file (entry.png.b64),
decodes it, validates it, and writes it to /output/entry.png.

Standard library only, no network, deterministic.
"""
import base64
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
B64_PATH = os.path.join(HERE, "entry.png.b64")
OUT_DIR = "/output"
OUT_PATH = os.path.join(OUT_DIR, "entry.png")
MAX_BYTES = 1024 * 1024
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    with open(B64_PATH, "r", encoding="ascii") as f:
        data = base64.b64decode("".join(f.read().split()), validate=True)
    if len(data) > MAX_BYTES:
        sys.exit("entry.png is %d bytes, over the 1 MiB limit" % len(data))
    if not data.startswith(PNG_MAGIC):
        sys.exit("decoded bytes are not a PNG")
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_DIM or height > MAX_DIM:
        sys.exit("image is %dx%d, over the 1024x1024 limit" % (width, height))
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (OUT_PATH, len(data), width, height))


if __name__ == "__main__":
    main()

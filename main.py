#!/usr/bin/env python3
"""news-image-20261120 v13fix — entry program.

The entry image is shipped as a binary PNG in this repository
(entry.png). This program only validates it and copies its bytes to
the output location, so running it twice produces byte-identical output.

Standard library only. No network access.
"""

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
MAX_BYTES = 1 * 1024 * 1024
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def output_path():
    """Output file: MAKEFUN_OUTPUT_DIR/entry.png, else /output/entry.png."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        return os.path.join(out_dir, "entry.png")
    return "/output/entry.png"


def read_png_size(data):
    """Return (width, height) of a PNG, raising ValueError if invalid."""
    if data[:8] != PNG_MAGIC:
        raise ValueError("entry.png is not a PNG file (bad magic)")
    if len(data) < 24 or data[12:16] != b"IHDR":
        raise ValueError("entry.png is not a PNG file (no IHDR chunk)")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    if not os.path.isfile(SRC):
        raise ValueError("entry.png not found next to main.py (%s)" % SRC)
    with open(SRC, "rb") as f:
        data = f.read()
    if len(data) > MAX_BYTES:
        raise ValueError(
            "entry.png is %d bytes, over the 1 MiB limit" % len(data)
        )
    width, height = read_png_size(data)
    if width > MAX_DIM or height > MAX_DIM:
        raise ValueError(
            "entry.png is %dx%d, over the 1024x1024 limit" % (width, height)
        )
    dst = output_path()
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as f:
        f.write(data)
    print("wrote %s: %dx%d, %d bytes" % (dst, width, height, len(data)))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - report any failure plainly
        print("error: %s" % exc, file=sys.stderr)
        sys.exit(1)

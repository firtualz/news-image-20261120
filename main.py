#!/usr/bin/env python3
"""main.py — news-image-20261120 v9 entry program.

Validates entry.png (PNG magic, <=1024x1024, <=1 MiB) and copies it to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png). Stdlib only.
The image itself is produced by render.py in this repo; this program only
reproduces the sealed entry bytes.
"""
import os
import struct
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    with open(src, "rb") as fh:
        data = fh.read()
    if len(data) > 1024 * 1024:
        print("entry.png exceeds 1 MiB", file=sys.stderr)
        return 1
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("entry.png is not a PNG", file=sys.stderr)
        return 1
    width, height = struct.unpack(">II", data[16:24])
    if width > 1024 or height > 1024:
        print("entry.png exceeds 1024x1024", file=sys.stderr)
        return 1
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "entry.png")
    with open(out, "wb") as fh:
        fh.write(data)
    print("wrote %s (%dx%d, %d bytes)" % (out, width, height, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""main.py -- news-image-20261120 v10 entry program.

Copies the bundled entry.png (1024x1024, <=1 MiB) to the output directory.
Stdlib only (os, struct, sys). No network.
"""
import os
import struct
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    with open(src, "rb") as fh:
        data = fh.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit("not a PNG")
    if len(data) > 1024 * 1024:
        sys.exit("entry.png exceeds 1 MiB")
    w, h = struct.unpack(">II", data[16:24])
    if w > 1024 or h > 1024:
        sys.exit("entry.png exceeds 1024x1024")
    dst = os.path.join(outdir, "entry.png")
    with open(dst, "wb") as fh:
        fh.write(data)
    print("wrote %s (%dx%d, %d bytes)" % (dst, w, h, len(data)))


if __name__ == "__main__":
    main()

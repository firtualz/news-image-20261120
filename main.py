#!/usr/bin/env python3
"""v12 entry runner — news-image-20261120.

Validates the bundled entry.png (PNG magic, <=1024x1024, <=1 MiB) and copies
its bytes to the output directory. Standard library only, no network.
The image itself is produced by render.py (PIL, deterministic).
"""
import os
import struct
import sys

MAX_BYTES = 1024 * 1024
MAX_DIM = 1024


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    with open(src, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("entry.png: bad PNG magic", file=sys.stderr)
        return 1
    if len(data) > MAX_BYTES:
        print("entry.png: %d bytes > 1 MiB" % len(data), file=sys.stderr)
        return 1
    w, h = struct.unpack(">II", data[16:24])
    if w > MAX_DIM or h > MAX_DIM:
        print("entry.png: %dx%d > 1024x1024" % (w, h), file=sys.stderr)
        return 1
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "entry.png")
    with open(out, "wb") as f:
        f.write(data)
    print("wrote %s (%dx%d, %d bytes)" % (out, w, h, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Entry point: copy the pre-rendered image to the output directory.

Standard library only. No network. Deterministic: the same bytes are
written on every run.
"""
import os
import struct
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    out = os.path.join(out_dir, "entry.png")
    with open(src, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("error: entry.png is not a PNG", file=sys.stderr)
        return 1
    if len(data) > 1048576:
        print("error: entry.png exceeds 1 MiB", file=sys.stderr)
        return 1
    width, height = struct.unpack(">II", data[16:24])
    if width > 1024 or height > 1024:
        print("error: entry.png exceeds 1024x1024", file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    with open(out, "wb") as f:
        f.write(data)
    print("wrote %s: %dx%d, %d bytes" % (out, width, height, len(data)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

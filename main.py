#!/usr/bin/env python3
"""Copy the pre-rendered front page to the output directory.

The entry is the PNG that render.py draws (entry.png, next to this
file). This program only validates it and copies it, so both runs
write byte-identical output. Standard library only, no network.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT = os.path.join(OUT_DIR, "entry.png")

MAX_BYTES = 1048576
MAX_SIDE = 1024


def main():
    with open(SRC, "rb") as f:
        data = f.read()
    if len(data) > MAX_BYTES:
        sys.exit("entry.png exceeds 1 MiB")
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit("entry.png is not a PNG")
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_SIDE or height > MAX_SIDE:
        sys.exit("entry.png exceeds 1024x1024")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "wb") as f:
        f.write(data)
    print("wrote %s (%dx%d, %d bytes)" % (OUT, width, height, len(data)))


if __name__ == "__main__":
    main()

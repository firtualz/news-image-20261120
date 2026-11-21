#!/usr/bin/env python3
"""Entry program for the news-image-20261120 v6 submission.

Validates entry.png (PNG magic, at most 1024x1024, at most 1 MiB)
and copies it to /output/entry.png. Deterministic: the output bytes
are exactly the input bytes, so repeated runs are identical.
Standard library only; no network access.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST = os.path.join("/output", "entry.png")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024
MAX_DIM = 1024


def fail(msg):
    sys.stderr.write("error: %s\n" % msg)
    return 1


def main():
    if not os.path.isfile(SRC):
        return fail("entry.png not found next to main.py")
    with open(SRC, "rb") as fh:
        data = fh.read()
    if len(data) > MAX_BYTES:
        return fail("entry.png is %d bytes, over the 1 MiB limit"
                    % len(data))
    if data[:8] != PNG_MAGIC:
        return fail("entry.png does not start with the PNG magic bytes")
    if len(data) < 24 or data[12:16] != b"IHDR":
        return fail("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_DIM or height > MAX_DIM:
        return fail("entry.png is %dx%d, over the 1024x1024 limit"
                    % (width, height))
    os.makedirs("/output", exist_ok=True)
    with open(DST, "wb") as fh:
        fh.write(data)
    sys.stdout.write("wrote %s (%dx%d, %d bytes)\n"
                     % (DST, width, height, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

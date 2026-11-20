#!/usr/bin/env python3
"""Entry program: reconstruct the bundled front-page image to the output path.

The image bytes live in the repository as base64 text (entry.png.b64) so the
entry stays plain UTF-8 files. Stdlib only, no network, deterministic: the
same input bytes always produce the same output bytes.
"""
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png.b64")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
DST = os.path.join(OUT_DIR, "entry.png")


def main():
    with open(SRC, "r") as f:
        raw = base64.b64decode(f.read())
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(DST, "wb") as f:
        f.write(raw)


if __name__ == "__main__":
    main()

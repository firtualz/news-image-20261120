#!/usr/bin/env python3
"""news-image-20261120 v13 — entry point (stdlib only, no network).

Runs render.py and copies the resulting entry.png to the output directory.
Validates the PNG (magic bytes, <=1024x1024, <=1 MiB) before writing.
Deterministic: same input always produces the same bytes.
"""
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, ".entry-tmp.png")
    subprocess.run([sys.executable, os.path.join(HERE, "render.py"), tmp],
                   check=True)
    with open(tmp, "rb") as fh:
        data = fh.read()
    os.remove(tmp)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("not a PNG")
    w, h = struct.unpack(">II", data[16:24])
    if w > 1024 or h > 1024:
        raise SystemExit("image larger than 1024x1024")
    if len(data) > 1024 * 1024:
        raise SystemExit("image larger than 1 MiB")
    out = os.path.join(out_dir, "entry.png")
    with open(out, "wb") as fh:
        fh.write(data)
    print("wrote %s (%dx%d, %d bytes)" % (out, w, h, len(data)))


if __name__ == "__main__":
    main()

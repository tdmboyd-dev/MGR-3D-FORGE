"""End-to-end pixels → true GLB geometry → optional independent Blender import."""

import argparse
from pathlib import Path
import sys
import tempfile
import struct
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from forge.cli import main


def png_pixels(rows):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    raw = b"".join(b"\x00" + row for row in rows)
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", len(rows[0]), len(rows), 8, 0, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--blender", default=None)
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix="mgr-pixel-relief-proof-"))
    source = root / "pattern.png"
    source.write_bytes(png_pixels([
        bytes([0, 32, 64, 96, 128, 160, 192, 255]),
        bytes([255, 192, 160, 128, 96, 64, 32, 0]),
    ]))
    assert main(["image-relief", "--image", str(source), "--out", str(root / "relief"),
                 "--width", "8", "--height", "2", "--depth", "3", "--grid", "8"]) == 0
    if args.blender:
        assert main(["blender-verify", str(root / "relief" / "relief.glb"),
                     "--report", str(root / "blender-import.json"), "--binary", args.blender]) == 0
    print(f"MGR_IMAGE_RELIEF_PASS path={root} independent_blender={bool(args.blender)}")


if __name__ == "__main__":
    run()

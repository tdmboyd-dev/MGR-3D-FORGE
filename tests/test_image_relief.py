"""Real PNG pixel/depth geometry, filter, security and materialization tests."""

import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from forge.image_relief import decode_png, make_relief, export_image_relief, PNG_SIGNATURE
from forge.glb import inspect_glb


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def png_pixels(rows, *, channels=1, filters=None, interlace=0):
    """Encode valid filter streams for independent pixel decoder tests."""
    height, width = len(rows), len(rows[0]) // channels
    color = {1: 0, 3: 2, 4: 6}[channels]
    prev = bytes(width * channels)
    packed = bytearray()
    for y, pixels in enumerate(rows):
        method = filters[y] if filters is not None else 0
        encoded = bytearray()
        for i, v in enumerate(pixels):
            left = pixels[i - channels] if i >= channels else 0
            up = prev[i]
            upper_left = prev[i - channels] if i >= channels else 0
            predictors = [0, left, up, (left + up) // 2]
            p = left + up - upper_left
            distances = [abs(p - x) for x in (left, up, upper_left)]
            predictors.append((left, up, upper_left)[distances.index(min(distances))])
            encoded.append((v - predictors[method]) & 255)
        packed.extend([method])
        packed.extend(encoded)
        prev = bytes(pixels)
    return (PNG_SIGNATURE + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, color, 0, 0, interlace))
            + chunk(b"IDAT", zlib.compress(packed)) + chunk(b"IEND", b""))


class ImageReliefTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.gray = png_pixels([bytes([0, 85, 170, 255]), bytes([255, 170, 85, 0])])

    def test_decoded_pixel_depth_matches_actual_source(self):
        image = decode_png(self.gray)
        self.assertEqual(image["luminance"], [[0, 85, 170, 255], [255, 170, 85, 0]])

    def test_relief_is_real_deterministic_3d_mesh(self):
        image = decode_png(self.gray)
        mesh, receipt = make_relief(image, width=4, height=2, depth=3, base=0.25)
        self.assertEqual(receipt["triangles"], 96)
        self.assertEqual(receipt["height_range"], [0.25, 3.25])
        self.assertEqual(len(mesh.indices) // 3, 96)
        self.assertTrue(all(n in (-1.0, 0.0, 1.0) for n in mesh.normals))

    def test_real_glb_obj_mtl_and_receipts(self):
        image = self.root / "source.png"
        image.write_bytes(self.gray)
        result = export_image_relief(image, self.root / "relief", width=4, height=2, grid=4)
        self.assertEqual(result["status"], "MATERIALIZED")
        self.assertEqual(inspect_glb((self.root / "relief" / "relief.glb").read_bytes())["triangles"], 96)
        self.assertIn("usemtl mgr-image-relief", (self.root / "relief" / "relief.obj").read_text())
        self.assertEqual(len(json.loads((self.root / "relief" / "manifest.json").read_text())["artifact_inventory"]), 3)
        self.assertFalse(result["inference_of_hidden_surfaces"])

    def test_reject_overwrite(self):
        path = self.root / "source.png"
        path.write_bytes(self.gray)
        (self.root / "already").mkdir()
        with self.assertRaises(FileExistsError):
            export_image_relief(path, self.root / "already")


def _filter_case(method, channels):
    def verify(self):
        base = [17, 80, 180, 251] if channels == 1 else [40, 100, 200, 255] * 3
        row = bytes(base)
        encoded = png_pixels([row, row, row], channels=channels, filters=[method, method, method])
        image = decode_png(encoded)
        self.assertEqual(image["width"], len(base) // channels)
        self.assertEqual(len(image["luminance"]), 3)
        self.assertEqual(image["luminance"][0], image["luminance"][1])
        self.assertEqual(image["luminance"][1], image["luminance"][2])
    return verify


for mode in (0, 1, 2, 3, 4):
    for channels in (1, 3, 4):
        setattr(ImageReliefTests, f"test_png_filter_{mode}_channels_{channels}", _filter_case(mode, channels))


def _dimension_case(axis, value):
    def verify(self):
        options = {"width": 4, "height": 3, "depth": 1.5, "base": 0.2, "grid": 4}
        options[axis] = value
        with self.assertRaises(ValueError):
            make_relief(decode_png(self.gray), **options)
    return verify


for axis, values in {
    "width": [-1, 0, 0.01, 101, float("nan"), float("inf")],
    "height": [-1, 0, 0.01, 101, float("nan"), float("inf")],
    "depth": [-1, 0, 0.001, 51, float("nan"), float("inf")],
    "base": [-1, 0, 0.001, 6, float("nan"), float("inf")],
    "grid": [-1, 0, 49, 1.5, True],
}.items():
    for n, value in enumerate(values):
        setattr(ImageReliefTests, f"test_reject_{axis}_invalid_{n}", _dimension_case(axis, value))


def _corrupt_case(mode):
    def verify(self):
        blob = self.gray
        if mode == "empty": blob = b""
        elif mode == "junk": blob = b"not a PNG file"
        elif mode == "tail": blob += b"garbage"
        elif mode == "signature": blob = b"ABCDEFGH" + blob[8:]
        elif mode == "crc": blob = blob[:29] + bytes([blob[29] ^ 1]) + blob[30:]
        elif mode == "cut_header": blob = blob[:12]
        elif mode == "cut_idat": blob = blob[:-18]
        elif mode == "cut_end": blob = blob[:-12]
        elif mode == "trailing_chunk": blob += chunk(b"tEXt", b"unexpected")
        elif mode == "unsupported_color": blob = png_pixels([bytes([10, 20, 30])], channels=3, interlace=1)
        elif mode == "oversized": blob = b"\x89PNG\r\n\x1a\n" + b"!" * 4_000_001
        with self.assertRaises(ValueError):
            decode_png(blob)
    return verify


for scenario in ("empty", "junk", "tail", "signature", "crc", "cut_header", "cut_idat",
                 "cut_end", "trailing_chunk", "unsupported_color", "oversized"):
    setattr(ImageReliefTests, f"test_corrupt_png_{scenario}", _corrupt_case(scenario))


if __name__ == "__main__":
    unittest.main()

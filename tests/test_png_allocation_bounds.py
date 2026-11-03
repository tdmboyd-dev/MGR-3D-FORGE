"""Uploaded PNG declared dimensions must bound actual decompressed allocation."""
import struct
import tracemalloc
import unittest
import zlib

from forge.image_relief import decode_png, PNG_SIGNATURE


def chunk(kind, payload):
    return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))


class PngAllocationTests(unittest.TestCase):
    def test_small_declared_image_cannot_flush_a_large_hidden_payload(self):
        encoded = zlib.compress(b'\x00' * 2_000_000)
        image = PNG_SIGNATURE + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 0, 0, 0, 0))
        image += chunk(b'IDAT', encoded) + chunk(b'IEND', b'')
        tracemalloc.start()
        try:
            with self.assertRaisesRegex(ValueError, 'size mismatch'):
                decode_png(image)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertLess(peak, 500_000, 'decoder allocated the hidden inflated payload')

    def test_complete_declared_pixels_decode_without_flush(self):
        image = PNG_SIGNATURE + chunk(b'IHDR', struct.pack('>IIBBBBB', 2, 1, 8, 0, 0, 0, 0))
        image += chunk(b'IDAT', zlib.compress(bytes((0, 30, 200)))) + chunk(b'IEND', b'')
        self.assertEqual(decode_png(image)['luminance'], [[30, 200]])

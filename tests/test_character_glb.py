"""Common external glTF geometry should enter without Forge-only assumptions."""

import json
import struct
import unittest

from forge.character_glb import parse_character_glb


def glb_fixture(*, with_uv=True, invalid_index=False, compression=False, sparse=False):
    positions = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0)
    indices = struct.pack("<3H", 0, 1, 4 if invalid_index else 2) + b"\0\0"
    uvs = struct.pack("<6f", 0, 0, 1, 0, 0, 1)
    binary = positions + indices + (uvs if with_uv else b"")
    views = [{"buffer": 0, "byteOffset": 0, "byteLength": 36},
             {"buffer": 0, "byteOffset": 36, "byteLength": 6}]
    accessors = [{"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3",
                  "min": [0, 0, 0], "max": [1, 1, 0]},
                 {"bufferView": 1, "componentType": 5123, "count": 3, "type": "SCALAR"}]
    attributes = {"POSITION": 0}
    if with_uv:
        views.append({"buffer": 0, "byteOffset": 44, "byteLength": 24})
        accessors.append({"bufferView": 2, "componentType": 5126, "count": 3, "type": "VEC2"})
        attributes["TEXCOORD_0"] = 2
    if sparse:
        accessors[0]["sparse"] = {"count": 1}
    primitive = {"attributes": attributes, "indices": 1, "mode": 4}
    if compression:
        primitive["extensions"] = {"KHR_draco_mesh_compression": {"bufferView": 0, "attributes": {}}}
    doc = {"asset": {"version": "2.0"}, "buffers": [{"byteLength": len(binary)}],
           "bufferViews": views, "accessors": accessors,
           "meshes": [{"primitives": [primitive]}], "nodes": [{"mesh": 0}]}
    packed = json.dumps(doc, separators=(",", ":")).encode()
    packed += b" " * (-len(packed) % 4)
    binary += b"\0" * (-len(binary) % 4)
    total = 12 + 8 + len(packed) + 8 + len(binary)
    return (struct.pack("<4sII", b"glTF", 2, total) +
            struct.pack("<I4s", len(packed), b"JSON") + packed +
            struct.pack("<I4s", len(binary), b"BIN\0") + binary)


class CharacterGLBTests(unittest.TestCase):
    def test_unsigned_short_indices_and_uv_accepted(self):
        doc, quality = parse_character_glb(glb_fixture())
        self.assertEqual(quality["triangles"], 1)
        self.assertEqual(doc["accessors"][1]["componentType"], 5123)
        self.assertEqual(doc["accessors"][2]["type"], "VEC2")

    def test_no_uv_is_valid(self):
        _, result = parse_character_glb(glb_fixture(with_uv=False))
        self.assertEqual(result["vertices"], 3)

    def test_header_corruption_refused(self):
        with self.assertRaises(ValueError):
            parse_character_glb(b"oops" + glb_fixture()[4:])

    def test_truncation_refused(self):
        with self.assertRaises(ValueError):
            parse_character_glb(glb_fixture()[:-3])

    def test_sparse_requires_normalization(self):
        with self.assertRaisesRegex(ValueError, "sparse"):
            parse_character_glb(glb_fixture(sparse=True))

    def test_compression_explicitly_rejected(self):
        with self.assertRaisesRegex(ValueError, "Draco"):
            parse_character_glb(glb_fixture(compression=True))

    def test_non_glb_refused(self):
        with self.assertRaises(ValueError):
            parse_character_glb(b"not model")

    def test_index_exceeding_vertex_count_refused(self):
        with self.assertRaisesRegex(ValueError, "index exceeds"):
            parse_character_glb(glb_fixture(invalid_index=True))


if __name__ == "__main__":
    unittest.main()

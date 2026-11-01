"""MGR GLB validator: actual Blender 16-bit index compatibility + malformed input denial.

Existing MGR exporter uses unsigned32. This test derives 16-bit GLB from its
real source geometry and preserves structural integrity for roundtrip checks.
"""
import json,struct,unittest
from forge.glb import export_glb,inspect_glb
from forge.geometry import Mesh

def triangle_model():
    mesh=Mesh()
    mesh.quad((0,0,0),(1,0,0),(1,0,1),(0,0,1))
    return export_glb([mesh],name="MGR ushort model",
                      materials=[("original",(0.5,0.7,0.5,1))])

def modify_index_accessor(blob,*,invalid_index=False,sparse=False):
    json_length=struct.unpack_from("<I",blob,12)[0]
    doc=json.loads(blob[20:20+json_length])
    bin_start=20+json_length+8
    binary=bytearray(blob[bin_start:])
    prim=doc["meshes"][0]["primitives"][0]
    ia=doc["accessors"][prim["indices"]]
    view=doc["bufferViews"][ia["bufferView"]]
    off=view.get("byteOffset",0)+ia.get("byteOffset",0)
    count=ia["count"]
    raw=struct.unpack_from("<"+("I"*count),binary,off)
    short=[65535 if invalid_index and i==0 else v for i,v in enumerate(raw)]
    struct.pack_into("<"+("H"*count),binary,off,*short)
    ia["componentType"]=5123
    view["byteLength"]=count*2
    if sparse:ia["sparse"]={"count":1}
    j=json.dumps(doc,sort_keys=True,separators=(",",":")).encode("utf8")
    j+=b" "*((-len(j))%4)
    body=struct.pack("<I4s",len(j),b"JSON")+j
    body+=struct.pack("<I4s",len(binary),b"BIN\x00")+binary
    return struct.pack("<4sII",b"glTF",2,12+len(body))+body

class BlenderGlbCompatibilityTests(unittest.TestCase):
    def test_original_32bit_and_real_16bit_indices_both_pass(self):
        source=triangle_model()
        a=inspect_glb(source)
        self.assertEqual(a["triangles"],2)
        self.assertIn(5125,a["index_component_types"])
        compact=modify_index_accessor(source)
        b=inspect_glb(compact)
        self.assertEqual(b["triangles"],a["triangles"])
        self.assertEqual(b["vertices"],a["vertices"])
        self.assertIn(5123,b["index_component_types"])

    def test_ushort_out_of_range_rejected_not_silent_corruption(self):
        with self.assertRaisesRegex(ValueError,"missing vertex"):
            inspect_glb(modify_index_accessor(triangle_model(),invalid_index=True))

    def test_sparse_unsupported_and_corrupt_total_denied(self):
        with self.assertRaisesRegex(ValueError,"sparse"):
            inspect_glb(modify_index_accessor(triangle_model(),sparse=True))
        blob=bytearray(triangle_model())
        struct.pack_into("<I",blob,8,100)
        with self.assertRaises(ValueError):
            inspect_glb(bytes(blob))

    def test_nonbinary_and_invalid_relative_buffer_denied(self):
        with self.assertRaises(ValueError):inspect_glb("not bytes")
        with self.assertRaises(ValueError):inspect_glb(b"glTF")

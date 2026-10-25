from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from forge.visualqa import compare_pngs, read_png, silhouette, PNG_MAGIC


def png_bytes(rows, *, filter_mode=0):
    width=len(rows[0])
    height=len(rows)
    channel_count=len(rows[0][0])
    if channel_count not in (3,4):
        raise ValueError("RGB/RGBA test data required")
    raw=bytearray()
    for row in rows:
        raw.append(filter_mode)
        prior=[0]*channel_count
        for rgb in row:
            for i,channel in enumerate(rgb):
                if filter_mode==1:
                    raw.append((channel-prior[i])%256)
                else:
                    raw.append(channel)
                prior[i]=channel
    def chunk(name,data):
        return struct.pack(">I",len(data))+name+data+struct.pack(">I",zlib.crc32(name+data)&0xffffffff)
    color=6 if channel_count==4 else 2
    return PNG_MAGIC+chunk(b"IHDR",struct.pack(">IIBBBBB",width,height,8,color,0,0,0))+chunk(b"IDAT",zlib.compress(bytes(raw)))+chunk(b"IEND",b"")


class VisualJudgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def write(self,name,rows,filter_mode=0):
        path=self.root/name
        path.write_bytes(png_bytes(rows,filter_mode=filter_mode))
        return path

    def test_identical_render_passes(self):
        rows=[[(0,0,0),(100,20,10)],[(0,0,0),(0,0,0)]]
        a=self.write("a.png",rows)
        b=self.write("b.png",rows,filter_mode=1)
        report=compare_pngs(a,b)
        self.assertTrue(report["pass"])
        self.assertEqual(report["rgb_mae"],0)
        self.assertEqual(report["candidate_silhouette"]["bbox"],[1,0,1,0])

    def test_mutation_flagged(self):
        a=self.write("a.png",[[(0,0,0)]])
        b=self.write("b.png",[[(255,255,255)]])
        report=compare_pngs(a,b,max_mean_absolute_error=2)
        self.assertFalse(report["pass"])
        self.assertEqual(report["rgb_mae"],255)

    def test_bad_crc_and_shape_rejected(self):
        a=self.write("a.png",[[(1,2,3)]])
        b=self.write("b.png",[[(1,2,3),(1,2,3)]])
        with self.assertRaises(ValueError):
            compare_pngs(a,b)
        corrupt=bytearray(a.read_bytes())
        corrupt[-6]^=1
        a.write_bytes(corrupt)
        with self.assertRaises(ValueError):
            read_png(a)

    def test_alpha_overrides_bright_background(self):
        rgba=[[(255,255,255,0),(100,50,10,255)],
              [(255,255,255,0),(255,255,255,0)]]
        path=self.root/"transparent.png"
        path.write_bytes(png_bytes(rgba))
        self.assertEqual(silhouette(read_png(path))["bbox"],[1,0,1,0])


if __name__ == "__main__":
    unittest.main()

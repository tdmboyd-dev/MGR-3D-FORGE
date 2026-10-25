import json
from pathlib import Path
import tempfile
import unittest

from forge.cli import build, main
from forge.spec import WorldSpec
from forge.web_runtime import make_world_flight


class OfflineWorldFlightTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.source=self.root/"world"
        build(WorldSpec(seed=8964,columns=3,rows=3,buildings=3),self.source)

    def test_self_contained_world_bundles_real_glb_and_data(self):
        output=self.root/"flight.html"
        report=make_world_flight(self.source,output)
        content=output.read_text(encoding="utf-8")
        self.assertEqual(report["status"],"MATERIALIZED")
        self.assertEqual(report["buildings"],3)
        self.assertIn("MGR_WORLD_BASE64",content)
        self.assertIn("getContext(\"webgl2\"",content)
        self.assertIn("building-",content)
        self.assertGreater(report["bytes"],2000)
        self.assertNotIn("https://",content)

    def test_cli_writes_once_and_never_overwrites(self):
        output=self.root/"flight.html"
        self.assertEqual(main(["world-flight","--world",str(self.source),"--out",str(output)]),0)
        with self.assertRaises(FileExistsError):
            main(["world-flight","--world",str(self.source),"--out",str(output)])

    def test_corrupt_glb_fails_receipt_before_packaging(self):
        path=self.source/"world.glb"
        path.write_bytes(path.read_bytes()+b"tampered")
        with self.assertRaises(ValueError):
            make_world_flight(self.source,self.root/"bad.html")
        self.assertFalse((self.root/"bad.html").exists())

    def test_bad_world_manifest_is_rejected(self):
        path=self.source/"manifest.json"
        data=json.loads(path.read_text(encoding="utf-8"))
        data.pop("buildings")
        path.write_text(json.dumps(data),encoding="utf-8")
        with self.assertRaises(ValueError):
            make_world_flight(self.source,self.root/"bad.html")


if __name__=="__main__":
    unittest.main()

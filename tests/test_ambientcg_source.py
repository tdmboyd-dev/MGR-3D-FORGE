import json
from tempfile import TemporaryDirectory
import unittest

from forge.asset_atlas import MGRAssetCatalog


class Response:
    headers = {}
    def __init__(self, data, url="https://ambientcg.com/api/v3/assets"):
        self.data, self.url = data, url
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def geturl(self): return self.url
    def read(self, size): return json.dumps(self.data).encode()[:size]


class AmbientCgTests(unittest.TestCase):
    def test_ambientcg_official_v3_source_is_only_cached_metadata(self):
        data = {"assets": [{"id": "Leather037", "title": "Leather 037",
                            "tags": ["brown", "leather"],
                            "downloads": [
                                {"url": "https://ambientcg.com/get?file=Leather037_1K-JPG.zip",
                                 "extension": "zip", "attributes": "1K-JPG", "size": 7000},
                                {"url": "http://evil.test/texture.zip",
                                 "extension": "zip", "attributes": "6K", "size": 7000}]}]}
        with TemporaryDirectory() as root:
            catalog = MGRAssetCatalog(root)
            result = catalog.search_live_ambientcg("leather", kind="textures", limit=2,
                                                   opener=lambda *_a, **_k: Response(data))
            self.assertEqual(result["returned"], 1)
            entry = result["listings"][0]
            self.assertEqual(entry["license"], "CC0-1.0")
            self.assertEqual(len(entry["download_options"]), 1)
            self.assertEqual(len(catalog.search(provider="ambientcg")), 1)
            self.assertEqual(result["assets_downloaded"], 0)

    def test_invalid_query_redirect_and_response_fail(self):
        with TemporaryDirectory() as root:
            catalog = MGRAssetCatalog(root)
            with self.assertRaises(ValueError):
                catalog.search_live_ambientcg("x"*101)
            with self.assertRaises(ValueError):
                catalog.search_live_ambientcg("wood", limit=21)
            with self.assertRaises(ValueError):
                catalog.search_live_ambientcg("wood", opener=lambda *_a, **_k:
                    Response({"assets":[]}, url="https://evil.test"))
            with self.assertRaises(ValueError):
                catalog.search_live_ambientcg("wood", opener=lambda *_a, **_k:
                    Response({"assets":{}}))

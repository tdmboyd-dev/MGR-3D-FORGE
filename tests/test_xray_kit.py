import hashlib,json
from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
import unittest

from forge.xray_kit import audit_kit_with_rea,write_xray_kit_receipt

def fixture():
    blob=b"MGR sample model"
    contenthash=hashlib.sha256(blob).hexdigest()
    arch_sha="f"*64
    name="test-repo/Assets/a.glb"
    receipt={"schema":"mgr.forge.pack-preservation.v2","archive_sha256":arch_sha,
             "official_source":"https://github.com/example/permitted-kit/tree/sha",
             "files":[{"path":name,"sha256":contenthash,"bytes":len(blob),
                       "source_license_scope_claimed":True}]}
    data={"artifacts":[{"digest":{"sha256":arch_sha},"format":"zip"}],
          "records":[{"evidence_id":"ev_"+("a"*64),"normalized_result":{
            "coverage":{"scope":"container-entries","status":"complete"},
            "integrity_contradictions":[],
            "nodes":[{"artifact_id":"art_a","sha256":contenthash,"size":len(blob)}],
            "occurrences":[{"artifact_id":"art_a","logical_path":name,
                            "entry_kind":"file","hash_status":"verified"}]
          }}]}
    return data,receipt


class XRayKitTests(unittest.TestCase):
    def save(self,dir,bundle,receipt):
        p=Path(dir)/"rea.json"
        q=Path(dir)/"pack.json"
        p.write_text(json.dumps(bundle))
        q.write_text(json.dumps(receipt))
        return p,q

    def test_independent_bytes_verified_but_rights_not_granted(self):
        a,b=fixture()
        with TemporaryDirectory() as directory:
            p,q=self.save(directory,a,b)
            result=audit_kit_with_rea(p,q)
            self.assertEqual(result["source_file_count"],1)
            self.assertEqual(result["source_file_sha256_matched"],1)
            self.assertEqual(result["categories"]["gltf_candidates"],1)
            self.assertFalse(result["safe_to_redistribute"])
            self.assertFalse(result["actual_skinning_or_animation_verified"])
            receipt=Path(directory)/"result.json"
            saved=write_xray_kit_receipt(p,q,receipt)
            self.assertEqual(saved["archive_sha256"],"f"*64)
            with self.assertRaises(FileExistsError):
                write_xray_kit_receipt(p,q,receipt)

    def test_tamper_wrong_archive_wrong_file_and_incomplete_coverage_fail(self):
        a,b=fixture()
        cases=[]
        changed=deepcopy(a);changed["artifacts"][0]["digest"]["sha256"]="0"*64;cases.append((changed,b))
        changed=deepcopy(a);changed["records"][0]["normalized_result"]["nodes"][0]["sha256"]="0"*64;cases.append((changed,b))
        changed=deepcopy(a);changed["records"][0]["normalized_result"]["coverage"]["status"]="unknown";cases.append((changed,b))
        changed=deepcopy(a);changed["records"][0]["normalized_result"]["occurrences"][0]["logical_path"]="../escape.glb";cases.append((changed,b))
        for row in cases:
            with self.subTest(row=row[0]):
                with TemporaryDirectory() as directory:
                    p,q=self.save(directory,*row)
                    with self.assertRaises(ValueError):
                        audit_kit_with_rea(p,q)

    def test_missing_schemas_fails_closed(self):
        a,b=fixture()
        b["schema"]="fake"
        with TemporaryDirectory() as directory:
            p,q=self.save(directory,a,b)
            with self.assertRaises(ValueError):
                audit_kit_with_rea(p,q)


if __name__=="__main__":
    unittest.main()

"""Guard MGR-native naming and current source-of-truth links from regressions."""

from pathlib import Path
import re
import unittest


ROOT=Path(__file__).resolve().parent.parent
PUBLIC_DOCS=(
    "README.md","AGENTS.md","docs/MGR-NATIVE-CANON.md",
    "docs/WHAT-WE-HAVE.md","docs/PRODUCT-BIBLE.md","docs/ARCHITECTURE.md",
    "docs/BUILD-REGISTER.md","docs/IMPLEMENTATION-EVIDENCE.md",
)


class MgrCanonTests(unittest.TestCase):
    def test_native_identity_excludes_vendor_named_capabilities(self):
        for name in PUBLIC_DOCS:
            content=(ROOT/name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                self.assertNotRegex(content,re.compile(
                    r"Scroll.World|God.s Eye View|Pinokio|(?:\binspired by\b)",re.I))

    def test_readme_local_links_all_exist(self):
        text=(ROOT/"README.md").read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)",text):
            if target.startswith(("https://","http://","#")):
                continue
            with self.subTest(target=target):
                self.assertTrue((ROOT/target).exists(),f"missing README reference: {target}")

    def test_current_inventory_has_real_blender_receipt(self):
        inventory=(ROOT/"docs/WHAT-WE-HAVE.md").read_text(encoding="utf-8")
        self.assertIn("Blender 5.2.2",inventory)
        # The current inventory advances with newly evidenced test totals;
        # old 64/64 is preserved in historical logs, not frozen as current.
        self.assertIn("140/140",inventory)
        self.assertTrue((ROOT/"evidence/blender/windows-wave6-fantasy-motion.json").is_file())
        self.assertTrue((ROOT/"evidence/blender/windows-2026-10-25.json").is_file())

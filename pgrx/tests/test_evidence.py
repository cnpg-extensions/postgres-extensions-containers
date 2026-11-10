import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence import digest, discover_extension_payload


class ExtensionPayloadDiscoveryTest(unittest.TestCase):
    def test_nested_runtime_data_keeps_final_paths_and_hashes(self):
        with tempfile.TemporaryDirectory() as temporary:
            extension_dir = Path(temporary)
            payload = {
                "anon.control": b"control",
                "anon--1.0.sql": b"sql",
                "anon/data/fake.csv": b"fake data",
                "anon/data/en_US/fake/person.csv": b"localized fake data",
            }
            for relative, contents in payload.items():
                path = extension_dir / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(contents)

            discovered = discover_extension_payload(extension_dir, "anon")

            self.assertEqual(
                [final for _, final, _ in discovered],
                [
                    "share/extension/anon--1.0.sql",
                    "share/extension/anon.control",
                    "share/extension/anon/data/en_US/fake/person.csv",
                    "share/extension/anon/data/fake.csv",
                ],
            )
            self.assertTrue(all(kind == "extension" for _, _, kind in discovered))
            self.assertEqual(
                {final: digest(path) for path, final, _ in discovered},
                {
                    "share/extension/" + relative: hashlib.sha256(
                        contents
                    ).hexdigest()
                    for relative, contents in payload.items()
                },
            )

    def test_ordinary_extension_files_keep_existing_mapping(self):
        with tempfile.TemporaryDirectory() as temporary:
            extension_dir = Path(temporary)
            (extension_dir / "demo.control").write_text("control")
            (extension_dir / "demo--1.0.sql").write_text("sql")
            (extension_dir / "other.control").write_text("unrelated")

            discovered = discover_extension_payload(extension_dir, "demo")

            self.assertEqual(
                [(final, kind) for _, final, kind in discovered],
                [
                    ("share/extension/demo--1.0.sql", "extension"),
                    ("share/extension/demo.control", "extension"),
                ],
            )

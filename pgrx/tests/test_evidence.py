import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence import digest, discover_extension_payload, normalize_about
from sbom.augment_spdx import license_expression


class ReporterCompatibilityTest(unittest.TestCase):
    def test_identical_doctest_boolean_is_canonicalized(self):
        raw = b'{"targets":[{"doctest":true,"doctest":true}]}'
        normalized = normalize_about(raw)
        self.assertEqual(json.loads(normalized), {'targets': [{'doctest': True}]})
        self.assertEqual(normalize_about(normalized), normalized)

    def test_conflicting_or_identity_duplicates_fail(self):
        for raw in [b'{"doctest":true,"doctest":false}',
                    b'{"doctest":1,"doctest":1}',
                    b'{"id":"same","id":"same"}']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                normalize_about(raw)

    def test_hyphenated_spdx_identifiers_survive_generation(self):
        for expression in ['BSD-3-Clause-No-Nuclear-Warranty',
                           'GPL-2.0-only WITH GCC-exception-2.0',
                           'LGPL-3.0-or-later', 'CC-BY-NC-ND-3.0-IGO']:
            self.assertEqual(license_expression(expression), expression)


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

    def test_symlink_in_extension_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            extension_dir = Path(temporary) / "extension"
            extension_dir.mkdir()
            data_dir = extension_dir / "demo"
            data_dir.mkdir()
            outside = Path(temporary) / "outside.csv"
            outside.write_text("external data")
            (data_dir / "linked.csv").symlink_to(outside)

            with self.assertRaisesRegex(ValueError, "symlinks"):
                discover_extension_payload(extension_dir, "demo")

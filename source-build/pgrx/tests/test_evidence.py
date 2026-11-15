import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence import digest, discover_extension_payload, published_git_versions


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


class PublishedGitVersionsTest(unittest.TestCase):
    def test_registry_identity_is_checked_and_duplicate_forks_share_lookup(self):
        packages = {key: {"name": "canonical-crate", "version": "1.2.3", "source": source}
                    for key, source in [("alias-one", "git+https://example.test/a#1"),
                                        ("alias-two", "git+https://example.test/a#2")]}
        record = {"crate": "canonical-crate", "num": "1.2.3", "yanked": False}
        with patch("evidence.urlopen", return_value=io.BytesIO(json.dumps({"version": record}).encode())) as request:
            self.assertEqual(published_git_versions(packages), {"versions": [record]})
            self.assertEqual(request.call_count, 1)
            self.assertEqual(request.call_args.args[0].full_url,
                             "https://crates.io/api/v1/crates/canonical-crate/1.2.3")

    def test_missing_release_is_omitted_but_service_failure_is_not_hidden(self):
        packages = {"git": {"name": "unpublished", "version": "1.0.0", "source": "git+https://example.test/repo"}}
        for status in (404, 503):
            with self.subTest(status=status), patch("evidence.urlopen", side_effect=HTTPError("url", status, "error", {}, None)):
                if status == 404:
                    self.assertEqual(published_git_versions(packages), {"versions": []})
                else:
                    with self.assertRaises(HTTPError):
                        published_git_versions(packages)

    def test_unrelated_registry_identity_is_rejected(self):
        packages = {"git": {"name": "expected", "version": "1.0.0", "source": "git+https://example.test/repo"}}
        response = {"version": {"crate": "unrelated", "num": "1.0.0"}}
        with patch("evidence.urlopen", return_value=io.BytesIO(json.dumps(response).encode())):
            with self.assertRaisesRegex(ValueError, "different package identity"):
                published_git_versions(packages)

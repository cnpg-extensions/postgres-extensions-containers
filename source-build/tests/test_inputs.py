import hashlib
import io
import tarfile
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare import platform_base
from source import archive_identity, resolve_source


class SourceResolutionTest(unittest.TestCase):
    def test_selected_gitlab_release_resolves_identity_without_downloading_archive(self):
        repository_url = "https://gitlab.com/group/subgroup/extension"
        repository = "group/subgroup/extension"
        version = "3.3.2"
        revision = "0123456789abcdef0123456789abcdef01234567"
        archive_url = (
            "https://gitlab.com/group/subgroup/extension/-/archive/3.3.2/"
            "extension-3.3.2.tar.gz"
        )
        api_url = (
            "https://gitlab.com/api/v4/projects/"
            "group%2Fsubgroup%2Fextension/repository/commits/3.3.2"
        )
        responses = {
            api_url: json.dumps({"id": revision}).encode(),
        }
        requested = []

        def fetch(url):
            requested.append(url)
            return responses[url]

        with patch("source.fetch", side_effect=fetch):
            result = resolve_source(repository_url, version)

        self.assertEqual(requested, [api_url])
        self.assertEqual(
            result,
            {
                "repository": repository,
                "host": "gitlab.com",
                "version": version,
                "revision": revision,
                "url": archive_url,
            },
        )

    def test_archive_commit_avoids_later_tag_resolution(self):
        revision = "abcdef0123456789abcdef0123456789abcdef01"
        data = io.BytesIO()
        with tarfile.open(fileobj=data, mode="w:gz", pax_headers={"comment": revision}) as tar:
            tar.addfile(tarfile.TarInfo("project/file"))
        archive = data.getvalue()
        with patch("source.fetch", side_effect=AssertionError("unexpected fetch")):
            result = archive_identity(archive)
        self.assertEqual(result["revision"], revision)
        self.assertEqual(
            result["archive_sha256"], hashlib.sha256(archive).hexdigest()
        )

    def test_archive_without_commit_cannot_be_mislabeled_from_current_tag(self):
        for headers in ({}, {"comment": "not-a-commit"}):
            with self.subTest(headers=headers):
                data = io.BytesIO()
                with tarfile.open(fileobj=data, mode="w:gz", pax_headers=headers) as tar:
                    tar.addfile(tarfile.TarInfo("project/file"))
                with patch("source.fetch", side_effect=AssertionError("unexpected fetch")):
                    with self.assertRaisesRegex(ValueError, "identify its Git commit"):
                        archive_identity(data.getvalue())


class BaseResolutionTest(unittest.TestCase):
    def test_platform_child_is_resolved_from_the_current_debian_base_tag(self):
        reference = "ghcr.io/example/postgres:18-minimal-bookworm"
        index_digest = "sha256:" + "a" * 64
        amd64_digest = "sha256:" + "b" * 64
        arm64_digest = "sha256:" + "c" * 64
        manifests = {
            reference: {
                "digest": index_digest,
                "manifests": [
                    {
                        "digest": amd64_digest,
                        "platform": {"os": "linux", "architecture": "amd64"},
                    },
                    {
                        "digest": arm64_digest,
                        "platform": {"os": "linux", "architecture": "arm64"},
                    },
                ],
            }
        }

        self.assertEqual(
            platform_base(reference, "linux/arm64", manifests),
            (reference + "@" + arm64_digest, index_digest),
        )



if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compose_sbom import aggregate, compose  # noqa: E402


def checksum(value):
    return [{"algorithm": "SHA256", "checksumValue": value}]


def package(spdxid, name, version, purl):
    return {
        "SPDXID": spdxid,
        "copyrightText": "NOASSERTION",
        "downloadLocation": "NOASSERTION",
        "externalRefs": [{
            "referenceCategory": "PACKAGE-MANAGER",
            "referenceLocator": purl,
            "referenceType": "purl",
        }],
        "filesAnalyzed": True,
        "licenseConcluded": "NOASSERTION",
        "licenseDeclared": "NOASSERTION",
        "name": name,
        "supplier": "NOASSERTION",
        "versionInfo": version,
    }


def builder_document(subjects):
    return {
        "_type": "https://in-toto.io/Statement/v1",
        "predicateType": "https://spdx.dev/Document",
        "subject": subjects,
        "predicate": {
            "spdxVersion": "SPDX-2.3",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "builder",
            "packages": [
                {
                    "SPDXID": "SPDXRef-DocumentRoot-Directory-sbom",
                    "name": "sbom",
                    "supplier": "NOASSERTION",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                    "licenseConcluded": "NOASSERTION",
                    "licenseDeclared": "NOASSERTION",
                    "copyrightText": "NOASSERTION",
                    "primaryPackagePurpose": "FILE",
                },
                package("SPDXRef-Package-base", "base", "1", "pkg:generic/base@1"),
                package("SPDXRef-Package-extension", "extension", "2", "pkg:generic/extension@2"),
                package("SPDXRef-Package-build-only", "build-only", "3", "pkg:generic/build-only@3"),
            ],
            "files": [
                {"SPDXID": "SPDXRef-File-base", "fileName": "usr/lib/base.so", "checksums": checksum("base")},
                {"SPDXID": "SPDXRef-File-extension", "fileName": "usr/lib/postgresql/ext.so", "checksums": checksum("extension")},
                {"SPDXID": "SPDXRef-File-build-only", "fileName": "usr/bin/cc", "checksums": checksum("build-only")},
            ],
            "relationships": [
                {"spdxElementId": "SPDXRef-DOCUMENT", "relationshipType": "DESCRIBES", "relatedSpdxElement": "SPDXRef-DocumentRoot-Directory-sbom"},
                {"spdxElementId": "SPDXRef-DocumentRoot-Directory-sbom", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-Package-extension"},
                {"spdxElementId": "SPDXRef-Package-base", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-File-base"},
                {"spdxElementId": "SPDXRef-Package-extension", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-File-extension"},
                {"spdxElementId": "SPDXRef-Package-base", "relationshipType": "DEPENDENCY_OF", "relatedSpdxElement": "SPDXRef-Package-extension"},
                {"spdxElementId": "SPDXRef-Package-base", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-File-build-only"},
            ],
        },
    }


class ComposeSbomTest(unittest.TestCase):
    def test_aggregate_merges_platform_documents(self):
        amd64 = builder_document([
            {"name": "lib/ext.so", "digest": {"sha256": "extension"}},
        ])
        arm64 = builder_document([
            {"name": "lib/ext.so", "digest": {"sha256": "extension-arm64"}},
        ])
        arm64["predicate"]["packages"].append(
            package("SPDXRef-Package-arm-only", "arm-only", "1", "pkg:generic/arm-only@1")
        )
        arm64["predicate"]["files"].append({
            "SPDXID": "SPDXRef-File-arm-only",
            "fileName": "usr/lib/arm-only.so",
            "checksums": checksum("extension-arm64"),
        })
        arm64["predicate"]["relationships"].append({
            "spdxElementId": "SPDXRef-Package-arm-only",
            "relationshipType": "CONTAINS",
            "relatedSpdxElement": "SPDXRef-File-arm-only",
        })
        output = aggregate(
            [
                ("linux/amd64", compose(amd64, extension_name="plr")),
                ("linux/arm64", compose(arm64, extension_name="plr")),
            ],
            extension_name="plr",
        )

        self.assertEqual(output["name"], "plr-multi-platform-sbom")
        self.assertIn("extension", {item["name"] for item in output["packages"]})
        self.assertIn("arm-only", {item["name"] for item in output["packages"]})

    def test_aggregate_is_deterministic(self):
        documents = [
            ("linux/amd64", compose(builder_document([
                {"name": "lib/ext.so", "digest": {"sha256": "extension"}},
            ]), extension_name="plr")),
            ("linux/arm64", compose(builder_document([
                {"name": "lib/ext.so", "digest": {"sha256": "extension-arm64"}},
            ]), extension_name="plr")),
        ]
        first = aggregate(documents, extension_name="plr")
        second = aggregate(copy.deepcopy(documents), extension_name="plr")
        self.assertEqual(first, second)
        self.assertEqual(
            json.dumps(first, sort_keys=True, separators=(",", ":")),
            json.dumps(second, sort_keys=True, separators=(",", ":")),
        )

    def test_final_packages_are_retained_and_unshipped_packages_are_removed(self):
        output = compose(builder_document([
            {"name": "lib/ext.so", "digest": {"sha256": "extension"}},
            {"name": "generated/artifact", "digest": {"sha256": "generated"}},
        ]), extension_name="plr")

        self.assertEqual(
            [package["name"] for package in output["packages"]],
            ["extension", "plr-extension-artifacts"],
        )
        self.assertEqual(
            [file["fileName"] for file in output["files"]],
            ["lib/ext.so", "generated/artifact"],
        )
        relationships = {
            (rel["relationshipType"], rel["spdxElementId"], rel["relatedSpdxElement"])
            for rel in output["relationships"]
        }
        self.assertIn(("CONTAINS", "SPDXRef-Package-extension", output["files"][0]["SPDXID"]), relationships)
        self.assertIn(("CONTAINS", "SPDXRef-Package-extension-payload", output["files"][1]["SPDXID"]), relationships)
        self.assertNotIn("base", {package["name"] for package in output["packages"]})
        self.assertNotIn(("DEPENDENCY_OF", "SPDXRef-Package-base", "SPDXRef-Package-extension"), relationships)
        self.assertNotIn(("CONTAINS", "SPDXRef-DocumentRoot-Directory-sbom", "SPDXRef-Package-extension"), relationships)
        self.assertNotIn("usr/bin/cc", json.dumps(output))

    def test_duplicate_checksum_prefers_path_and_preserves_same_file_owners(self):
        document = builder_document([
            {"name": "share/libblas3/copyright", "digest": {"sha256": "copyright"}},
        ])
        predicate = document["predicate"]
        predicate["packages"].extend([
            package("SPDXRef-Package-libblas3", "libblas3", "1", "pkg:generic/libblas3@1"),
            package("SPDXRef-Package-liblapack3", "liblapack3", "1", "pkg:generic/liblapack3@1"),
            package("SPDXRef-Package-shared-license", "shared-license", "1", "pkg:generic/shared-license@1"),
        ])
        predicate["files"].extend([
            {
                "SPDXID": "SPDXRef-File-libblas3-copyright",
                "fileName": "usr/share/doc/libblas3/copyright",
                "checksums": checksum("copyright"),
            },
            {
                "SPDXID": "SPDXRef-File-liblapack3-copyright",
                "fileName": "usr/share/doc/liblapack3/copyright",
                "checksums": checksum("copyright"),
            },
        ])
        predicate["relationships"].extend([
            {
                "spdxElementId": "SPDXRef-Package-libblas3",
                "relationshipType": "CONTAINS",
                "relatedSpdxElement": "SPDXRef-File-libblas3-copyright",
            },
            {
                "spdxElementId": "SPDXRef-Package-shared-license",
                "relationshipType": "CONTAINS",
                "relatedSpdxElement": "SPDXRef-File-libblas3-copyright",
            },
            {
                "spdxElementId": "SPDXRef-Package-liblapack3",
                "relationshipType": "CONTAINS",
                "relatedSpdxElement": "SPDXRef-File-liblapack3-copyright",
            },
        ])

        output = compose(document, extension_name="plr")
        package_names = {item["name"] for item in output["packages"]}
        self.assertIn("libblas3", package_names)
        self.assertIn("shared-license", package_names)
        self.assertNotIn("liblapack3", package_names)
        relationships = {
            (rel["relationshipType"], rel["spdxElementId"], rel["relatedSpdxElement"])
            for rel in output["relationships"]
        }
        file_id = output["files"][0]["SPDXID"]
        self.assertIn(("CONTAINS", "SPDXRef-Package-libblas3", file_id), relationships)
        self.assertIn(("CONTAINS", "SPDXRef-Package-shared-license", file_id), relationships)
        self.assertNotIn(("CONTAINS", "SPDXRef-Package-liblapack3", file_id), relationships)

    def test_ambiguous_basename_match_is_extension_owned(self):
        document = builder_document([
            {"name": "share/unknown/copyright", "digest": {"sha256": "copyright"}},
        ])
        predicate = document["predicate"]
        predicate["packages"].extend([
            package("SPDXRef-Package-left", "left", "1", "pkg:generic/left@1"),
            package("SPDXRef-Package-right", "right", "1", "pkg:generic/right@1"),
        ])
        predicate["files"].extend([
            {
                "SPDXID": "SPDXRef-File-left-copyright",
                "fileName": "usr/share/doc/left/copyright",
                "checksums": checksum("copyright"),
            },
            {
                "SPDXID": "SPDXRef-File-right-copyright",
                "fileName": "usr/share/doc/right/copyright",
                "checksums": checksum("copyright"),
            },
        ])
        predicate["relationships"].extend([
            {
                "spdxElementId": "SPDXRef-Package-left",
                "relationshipType": "CONTAINS",
                "relatedSpdxElement": "SPDXRef-File-left-copyright",
            },
            {
                "spdxElementId": "SPDXRef-Package-right",
                "relationshipType": "CONTAINS",
                "relatedSpdxElement": "SPDXRef-File-right-copyright",
            },
        ])

        output = compose(document, extension_name="plr")
        self.assertEqual([item["name"] for item in output["packages"]], ["plr-extension-artifacts"])

    def test_license_path_selects_named_package(self):
        document = builder_document([
            {"name": "licenses/libgomp1/copyright", "digest": {"sha256": "copyright"}},
        ])
        predicate = document["predicate"]
        predicate["packages"].extend([
            package("SPDXRef-Package-libgomp1", "libgomp1", "1", "pkg:generic/libgomp1@1"),
            package("SPDXRef-Package-gcc", "gcc-14-base", "1", "pkg:generic/gcc-14-base@1"),
        ])
        predicate["files"].append({
            "SPDXID": "SPDXRef-File-gcc-copyright",
            "fileName": "usr/share/doc/gcc-14-base/copyright",
            "checksums": checksum("copyright"),
        })
        predicate["relationships"].append({
            "spdxElementId": "SPDXRef-Package-gcc",
            "relationshipType": "CONTAINS",
            "relatedSpdxElement": "SPDXRef-File-gcc-copyright",
        })

        output = compose(document, extension_name="plr")
        package_names = {item["name"] for item in output["packages"]}
        self.assertIn("libgomp1", package_names)
        self.assertNotIn("gcc-14-base", package_names)
        relationships = {
            (rel["relationshipType"], rel["spdxElementId"], rel["relatedSpdxElement"])
            for rel in output["relationships"]
        }
        file_id = output["files"][0]["SPDXID"]
        self.assertIn(("CONTAINS", "SPDXRef-Package-libgomp1", file_id), relationships)
        self.assertNotIn(("CONTAINS", "SPDXRef-Package-gcc", file_id), relationships)

    def test_registry_image_subject_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "image subject"):
            compose(builder_document([
                {"name": "pkg:docker/example@latest", "digest": {"sha256": "image"}},
            ]), extension_name="plr")

    def test_malformed_spdx_entries_fail_instead_of_being_skipped(self):
        malformed_entries = {
            "packages": {"name": "broken"},
            "files": {"fileName": "broken", "checksums": []},
            "relationships": {},
        }
        for field, entry in malformed_entries.items():
            with self.subTest(field=field):
                document = builder_document([
                    {"name": "lib/ext.so", "digest": {"sha256": "extension"}},
                ])
                document["predicate"][field].append(entry)
                with self.assertRaises(KeyError):
                    compose(document, extension_name="plr")


if __name__ == "__main__":
    unittest.main()

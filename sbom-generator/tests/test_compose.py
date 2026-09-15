#!/usr/bin/env python3
import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))

from compose import compose, final_inventory_files, set_document_namespace  # noqa: E402


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


def builder_document():
    return {
        "spdxVersion": "SPDX-2.3",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "builder",
        "creationInfo": {"created": "2026-01-01T00:00:00Z", "creators": ["Tool: syft"]},
        "packages": [
            package("SPDXRef-Package-base", "base", "1", "pkg:deb/debian/base@1?arch=amd64&distro=debian-12.15"),
            package("SPDXRef-Package-extension", "extension", "2", "pkg:deb/debian/extension@2?arch=amd64&distro=debian-12.15"),
            package("SPDXRef-Package-build-only", "build-only", "3", "pkg:deb/debian/build-only@3?arch=amd64&distro=debian-12.15"),
        ],
        "files": [
            {"SPDXID": "SPDXRef-File-base", "fileName": "usr/lib/base.so", "checksums": checksum("base")},
            {"SPDXID": "SPDXRef-File-extension", "fileName": "usr/lib/postgresql/ext.so", "checksums": checksum("extension")},
            {"SPDXID": "SPDXRef-File-build-only", "fileName": "usr/bin/cc", "checksums": checksum("build-only")},
        ],
        "relationships": [
            {"spdxElementId": "SPDXRef-Package-base", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-File-base"},
            {"spdxElementId": "SPDXRef-Package-extension", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-File-extension"},
            {"spdxElementId": "SPDXRef-Package-build-only", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-File-build-only"},
            {"spdxElementId": "SPDXRef-Package-base", "relationshipType": "DEPENDENCY_OF", "relatedSpdxElement": "SPDXRef-Package-extension"},
        ],
    }


def inventory(*entries):
    return {"files": [{"name": name, "algorithm": "sha256", "value": digest} for name, digest in entries]}


class ComposeTest(unittest.TestCase):
    def test_composes_only_shipped_files_and_owned_packages(self):
        output = compose(
            builder_document(),
            extension_name="plr",
            final_inventory=inventory(
                ("lib/ext.so", "extension"),
                ("generated/artifact", "generated"),
            ),
            platform="linux/amd64",
        )
        self.assertEqual(output["name"], "plr-sbom")
        self.assertEqual(
            {record["name"] for record in output["packages"]},
            {"extension", "debian", "plr-extension-artifacts"},
        )
        self.assertEqual(
            [record["fileName"] for record in output["files"]],
            ["generated/artifact", "lib/ext.so"],
        )
        self.assertNotIn("build-only", json.dumps(output))
        self.assertFalse("subject" in output)

    @patch.dict(os.environ, {"SBOM_GENERATOR_REVISION": "abc123" * 6 + "abcd"})
    def test_generator_metadata_identifies_version_and_repository(self):
        revision = os.environ["SBOM_GENERATOR_REVISION"]
        output = compose(
            builder_document(),
            extension_name="plr",
            final_inventory=inventory(("lib/ext.so", "extension")),
            platform="linux/amd64",
        )
        generator_annotation = next(
            annotation for annotation in output["annotations"]
            if annotation["annotator"] == f"Tool: cnpg-sbom-generator-{revision}"
        )
        metadata = json.loads(generator_annotation["comment"])
        self.assertIn(f"Tool: cnpg-sbom-generator-{revision}", output["creationInfo"]["creators"])
        self.assertEqual(metadata["generator"], "cnpg-sbom-generator")
        self.assertEqual(metadata["generatorVersion"], revision)
        self.assertEqual(
            metadata["generatorRepository"],
            "https://github.com/cnpg-extensions/postgres-extensions-containers",
        )

    def test_license_files_are_directly_mapped_to_the_named_package(self):
        document = builder_document()
        document["packages"].append(
            package("SPDXRef-Package-copyright", "libgomp1", "1", "pkg:deb/debian/libgomp1@1?arch=amd64&distro=debian-12.15")
        )
        document["files"].append({
            "SPDXID": "SPDXRef-File-copyright",
            "fileName": "usr/share/doc/libgomp1/copyright",
            "checksums": checksum("copyright"),
        })
        document["relationships"].append({
            "spdxElementId": "SPDXRef-Package-copyright",
            "relationshipType": "CONTAINS",
            "relatedSpdxElement": "SPDXRef-File-copyright",
        })
        output = compose(
            document,
            extension_name="plr",
            final_inventory=inventory(("licenses/libgomp1/copyright", "copyright")),
            platform="linux/amd64",
            scancode_report={"files": [{
                "path": "licenses/libgomp1/copyright",
                "license_detections": [{"license_expression_spdx": "GPL-2.0-only"}],
            }]},
        )
        file_record = output["files"][0]
        package_record = next(item for item in output["packages"] if item["name"] == "libgomp1")
        self.assertEqual(file_record["licenseInfoInFiles"], ["GPL-2.0-only"])
        self.assertEqual(package_record["licenseDeclared"], "GPL-2.0-only")

    def test_unmatched_file_licenses_are_combined_on_synthetic_package(self):
        output = compose(
            builder_document(),
            extension_name="demo",
            final_inventory=inventory(
                ("licenses/vendor/copyright", "vendor-license"),
                ("licenses/other/copyright", "other-license"),
            ),
            platform="linux/amd64",
            scancode_report={"files": [
                {
                    "path": "licenses/vendor/copyright",
                    "license_detections": [{"license_expression_spdx": "MIT"}],
                },
                {
                    "path": "licenses/other/copyright",
                    "license_detections": [{
                        "license_expression_spdx": "Apache-2.0 OR BSD-2-Clause",
                    }],
                },
            ]},
        )
        synthetic = next(
            item for item in output["packages"]
            if item["name"] == "demo-extension-artifacts"
        )
        self.assertEqual(synthetic["licenseInfoFromFiles"], [
            "Apache-2.0 OR BSD-2-Clause", "MIT",
        ])
        self.assertEqual(
            synthetic["licenseDeclared"],
            "(Apache-2.0 OR BSD-2-Clause) AND MIT",
        )

    def test_platform_documents_are_deterministic_and_isolated(self):
        first = compose(
            builder_document(), extension_name="plr",
            final_inventory=inventory(("lib/ext.so", "extension")), platform="linux/amd64",
            evidence={"builderSha256": "abc"},
        )
        second = compose(
            builder_document(), extension_name="plr",
            final_inventory=inventory(("lib/ext.so", "extension")), platform="linux/arm64",
            evidence={"builderSha256": "abc"},
        )
        self.assertNotEqual(first["documentNamespace"], second["documentNamespace"])
        self.assertEqual(first, compose(
            builder_document(), extension_name="plr",
            final_inventory=inventory(("lib/ext.so", "extension")), platform="linux/amd64",
            evidence={"builderSha256": "abc"},
        ))

    def test_namespace_changes_with_content_and_is_stable_when_reapplied(self):
        first = compose(
            builder_document(), extension_name="demo",
            final_inventory=inventory(("lib/ext.so", "extension")), platform="linux/amd64",
        )
        changed = compose(
            builder_document(), extension_name="demo",
            final_inventory=inventory(("lib/ext.so", "different")), platform="linux/amd64",
        )
        self.assertNotEqual(first["documentNamespace"], changed["documentNamespace"])
        original_namespace = first["documentNamespace"]
        set_document_namespace(first, "demo", "linux/amd64")
        self.assertEqual(first["documentNamespace"], original_namespace)
        first["comment"] = "Downstream augmentation"
        set_document_namespace(first, "demo", "linux/amd64")
        self.assertNotEqual(first["documentNamespace"], original_namespace)

    def test_malformed_final_inventory_fails(self):
        with self.assertRaises(ValueError):
            final_inventory_files({"files": [{"name": "lib/ext.so", "checksums": []}]}, Path("inventory"))

    def test_builder_wrapper_is_accepted_only_as_legacy_input(self):
        wrapped = {
            "predicateType": "https://spdx.dev/Document",
            "predicate": builder_document(),
            "subject": [{"name": "lib/ext.so", "digest": {"sha256": "extension"}}],
        }
        output = compose(wrapped, extension_name="plr")
        self.assertEqual(output["name"], "plr-sbom")


if __name__ == "__main__":
    unittest.main()

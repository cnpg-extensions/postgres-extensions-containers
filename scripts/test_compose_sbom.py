#!/usr/bin/env python3
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


def checksum(value):
    return [{"algorithm": "SHA256", "checksumValue": value}]


def package(spdxid, name, version, purl):
    if "distro=" not in purl:
        purl += "&distro=debian-12.15" if "?" in purl else "?distro=debian-12.15"
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


def scan_report(*records):
    return {
        "files": [
            {
                "path": path,
                "license_detections": [
                    {"license_expression_spdx": expression}
                    for expression in expressions
                ],
            }
            for path, expressions in records
        ]
    }


SCRIPT = Path(__file__).with_name("compose_sbom.py")
ROOT = SCRIPT.parent.parent


def run_composer(documents, platforms=("linux/amd64", "linux/arm64"), *, scan_reports=None, check=True):
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        output_path = directory / "aggregate.spdx.json"
        scan_reports = scan_reports or [{} for _ in documents]
        args = [
            str(SCRIPT),
            "--extension-name", "plr",
            "--output", str(output_path),
        ]
        for index, document in enumerate(documents):
            input_path = directory / f"builder-{index}.json"
            input_path.write_text(json.dumps(document), encoding="utf-8")
            args.extend(["--builder-sbom", str(input_path)])
            scan_path = directory / f"scan-{index}.json"
            scan_path.write_text(json.dumps(scan_reports[index]), encoding="utf-8")
            args.extend(["--scancode-report", str(scan_path)])
            if index < len(platforms):
                args.extend(["--platform", platforms[index]])
        for platform in platforms[len(documents):]:
            args.extend(["--platform", platform])

        result = subprocess.run(
            args,
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if check and result.returncode:
            raise AssertionError(result.stderr)
        if not output_path.exists():
            return result, None, None
        return result, json.loads(output_path.read_text(encoding="utf-8")), output_path.read_bytes()


class ComposeSbomTest(unittest.TestCase):
    def test_aggregate_supports_single_platform(self):
        document = builder_document([
            {"name": "lib/ext.so", "digest": {"sha256": "extension"}},
        ])
        _, output, _ = run_composer([document], platforms=("linux/amd64",))

        self.assertEqual(output["name"], "plr-multi-platform-sbom")
        self.assertIn("extension", {item["name"] for item in output["packages"]})

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
        _, output, _ = run_composer([amd64, arm64])

        self.assertEqual(output["name"], "plr-multi-platform-sbom")
        self.assertIn("extension", {item["name"] for item in output["packages"]})
        self.assertIn("arm-only", {item["name"] for item in output["packages"]})

    def test_aggregate_is_deterministic(self):
        documents = [
            ("linux/amd64", builder_document([
                {"name": "lib/ext.so", "digest": {"sha256": "extension"}},
            ])),
            ("linux/arm64", builder_document([
                {"name": "lib/ext.so", "digest": {"sha256": "extension-arm64"}},
            ])),
        ]
        reports = [
            scan_report(("lib/ext.so", ("MIT",))),
            scan_report(("lib/ext.so", ("Apache-2.0",))),
        ]
        _, first, first_bytes = run_composer(
            [document for _, document in documents], scan_reports=reports
        )
        _, second, second_bytes = run_composer(
            [document for _, document in reversed(documents)],
            [platform for platform, _ in reversed(documents)],
            scan_reports=list(reversed(reports)),
        )
        self.assertEqual(first, second)
        self.assertEqual(first_bytes, second_bytes)

    def test_final_packages_are_retained_and_unshipped_packages_are_removed(self):
        document = builder_document([
            {"name": "lib/ext.so", "digest": {"sha256": "extension"}},
            {"name": "generated/artifact", "digest": {"sha256": "generated"}},
        ])
        _, output, _ = run_composer([document] * 2)

        self.assertEqual(
            {
                package["name"] for package in output["packages"]
                if package["name"] != "debian"
            },
            {"extension", "plr-extension-artifacts"},
        )
        self.assertEqual(
            [file["fileName"] for file in output["files"]],
            ["lib/ext.so", "generated/artifact"],
        )
        relationships = {
            (rel["relationshipType"], rel["spdxElementId"], rel["relatedSpdxElement"])
            for rel in output["relationships"]
        }
        package_ids = {package["name"]: package["SPDXID"] for package in output["packages"]}
        self.assertIn(("CONTAINS", package_ids["extension"], output["files"][0]["SPDXID"]), relationships)
        self.assertIn(("CONTAINS", package_ids["plr-extension-artifacts"], output["files"][1]["SPDXID"]), relationships)
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

        _, output, _ = run_composer([document] * 2)
        package_names = {item["name"] for item in output["packages"]}
        self.assertIn("libblas3", package_names)
        self.assertIn("shared-license", package_names)
        self.assertNotIn("liblapack3", package_names)
        relationships = {
            (rel["relationshipType"], rel["spdxElementId"], rel["relatedSpdxElement"])
            for rel in output["relationships"]
        }
        file_id = output["files"][0]["SPDXID"]
        package_ids = {package["name"]: package["SPDXID"] for package in output["packages"]}
        self.assertIn(("CONTAINS", package_ids["libblas3"], file_id), relationships)
        self.assertIn(("CONTAINS", package_ids["shared-license"], file_id), relationships)
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

        _, output, _ = run_composer([document] * 2)
        self.assertEqual(
            [item["name"] for item in output["packages"] if item["name"] != "debian"],
            ["plr-extension-artifacts"],
        )

    def test_trivy_os_package_is_preserved_in_aggregate(self):
        document = builder_document([
            {"name": "lib/ext.so", "digest": {"sha256": "extension"}},
        ])
        next(
            package for package in document["predicate"]["packages"]
            if package["name"] == "extension"
        )["externalRefs"][0]["referenceLocator"] = (
            "pkg:deb/debian/extension@2?arch=amd64&distro=debian-12.15"
        )

        _, output, _ = run_composer([document] * 2)
        os_package = next(
            package for package in output["packages"]
            if package.get("primaryPackagePurpose") == "OPERATING-SYSTEM"
        )
        self.assertEqual(os_package["SPDXID"], "SPDXRef-OperatingSystem-debian-12.15")
        self.assertEqual(os_package["name"], "debian")
        self.assertEqual(os_package["versionInfo"], "12.15")
        relationships = {
            (rel["relationshipType"], rel["spdxElementId"], rel["relatedSpdxElement"])
            for rel in output["relationships"]
        }
        self.assertIn(
            ("DESCRIBES", "SPDXRef-DOCUMENT", os_package["SPDXID"]),
            relationships,
        )
        extension_id = next(
            package["SPDXID"] for package in output["packages"]
            if package["name"] == "extension"
        )
        self.assertIn(("CONTAINS", os_package["SPDXID"], extension_id), relationships)

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

        _, output, _ = run_composer([document] * 2)
        package_names = {item["name"] for item in output["packages"]}
        self.assertIn("libgomp1", package_names)
        self.assertNotIn("gcc-14-base", package_names)
        relationships = {
            (rel["relationshipType"], rel["spdxElementId"], rel["relatedSpdxElement"])
            for rel in output["relationships"]
        }
        file_id = output["files"][0]["SPDXID"]
        package_id = next(package["SPDXID"] for package in output["packages"] if package["name"] == "libgomp1")
        self.assertIn(("CONTAINS", package_id, file_id), relationships)
        self.assertNotIn(("CONTAINS", "SPDXRef-Package-gcc", file_id), relationships)

    def test_scancode_licenses_are_added_to_files_and_packages(self):
        document = builder_document([
            {"name": "licenses/r-base-core/copyright", "digest": {"sha256": "copyright"}},
        ])
        document["predicate"]["packages"].append(
            package("SPDXRef-Package-r-base-core", "r-base-core", "1", "pkg:generic/r-base-core@1")
        )
        report = scan_report((
            "licenses/r-base-core/copyright",
            ("GPL-2.0-only AND LicenseRef-scancode-pcre",),
        ))
        document["predicate"]["packages"][-1]["licenseDeclared"] = "MIT"
        report["license_references"] = [{
            "spdx_license_key": "LicenseRef-scancode-pcre",
            "name": "PCRE License",
            "text": "PCRE license text",
        }]

        _, output, _ = run_composer([document] * 2, scan_reports=[report] * 2)
        file_record = output["files"][0]
        package_record = next(
            item for item in output["packages"] if item["name"] == "r-base-core"
        )
        self.assertEqual(
            file_record["licenseInfoInFiles"],
            ["GPL-2.0-only AND LicenseRef-scancode-pcre"],
        )
        self.assertEqual(package_record["licenseInfoFromFiles"], file_record["licenseInfoInFiles"])
        self.assertEqual(
            package_record["licenseDeclared"],
            "MIT",
        )
        self.assertEqual(package_record["licenseConcluded"], "NOASSERTION")
        self.assertIn(
            {"extractedText": "PCRE license text", "licenseId": "LicenseRef-scancode-pcre", "name": "PCRE License"},
            output["hasExtractedLicensingInfos"],
        )

    def test_scancode_licenses_populate_trivy_package_field(self):
        document = builder_document([
            {"name": "licenses/libgomp1/copyright", "digest": {"sha256": "copyright"}},
        ])
        document["predicate"]["packages"].append(
            package("SPDXRef-Package-libgomp1", "libgomp1", "1", "pkg:generic/libgomp1@1")
        )
        report = scan_report((
            "licenses/libgomp1/copyright",
            ("GPL-2.0-only", "BSD-3-Clause"),
        ))

        _, output, _ = run_composer([document] * 2, scan_reports=[report] * 2)
        package_record = next(
            item for item in output["packages"] if item["name"] == "libgomp1"
        )
        self.assertEqual(
            package_record["licenseDeclared"],
            "BSD-3-Clause AND GPL-2.0-only",
        )

    def test_registry_image_subject_is_rejected(self):
        document = builder_document([
            {"name": "pkg:docker/example@latest", "digest": {"sha256": "image"}},
        ])
        result, _, _ = run_composer([document] * 2, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("image subject", result.stderr)

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
                result, _, _ = run_composer(
                    [document] * 2,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)

    def test_builder_sbom_and_platform_arguments_must_match(self):
        document = builder_document([
            {"name": "lib/ext.so", "digest": {"sha256": "extension"}},
        ])
        result, _, _ = run_composer(
            [document] * 2,
            platforms=("linux/amd64",),
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must have the same number", result.stderr)


if __name__ == "__main__":
    unittest.main()

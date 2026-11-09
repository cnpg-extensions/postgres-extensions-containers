"""Validate the real composer/hook boundary with the independent SPDX library."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest

from spdx_tools.spdx.parser.json.json_parser import parse_from_file
from spdx_tools.spdx.validation.document_validator import validate_full_spdx_document

import test_hook

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'sbom-generator'))
from compose import compose, set_document_namespace
from generator import final_inventory


class SPDXConformanceTest(unittest.TestCase):
    def test_composed_pgrx_document_conforms_to_spdx(self):
        for ship_system_library in (False, True):
            with self.subTest(ship_system_library=ship_system_library):
                self.check_composed_document(ship_system_library)

    def check_composed_document(self, ship_system_library):
        fixture = test_hook.HookTest()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        if ship_system_library:
            library = fixture.final / 'lib/libsystem.so'
            library.write_bytes(b'shipped system library')
        inventory = final_inventory(fixture.final)
        builder_files = [
            {'SPDXID': 'SPDXRef-builder-file-' + str(index),
             'fileName': 'builder/' + record['name'],
             'checksums': record['checksums'],
             'licenseConcluded': 'NOASSERTION',
             'licenseInfoInFiles': ['NOASSERTION'],
             'copyrightText': 'NOASSERTION'}
            for index, record in enumerate(inventory['files'])
        ]
        # The builder package also owns a file that does not ship. Composition
        # must prune it and recompute the package verification code.
        builder_files.append({
            'SPDXID': 'SPDXRef-builder-only-file', 'fileName': 'usr/share/unshipped',
            'checksums': [{'algorithm': 'SHA256', 'checksumValue': 'a' * 64}],
        })
        system_files = [record for record in builder_files
                        if record['fileName'].endswith('libsystem.so')
                        or record['SPDXID'] == 'SPDXRef-builder-only-file']
        builder = {
            'SPDXID': 'SPDXRef-DOCUMENT',
            'spdxVersion': 'SPDX-2.3',
            'dataLicense': 'CC0-1.0',
            'name': 'builder-evidence',
            'documentNamespace': 'https://example.test/spdx/builder',
            'creationInfo': {
                'created': '2026-01-01T00:00:00Z',
                'creators': ['Tool: integration-fixture'],
            },
            'packages': [{
                'SPDXID': 'SPDXRef-builder-debian',
                'name': 'base-files',
                'downloadLocation': 'NOASSERTION',
                'filesAnalyzed': False,
            }, {
                'SPDXID': 'SPDXRef-builder-system-library',
                'name': 'libsystem', 'versionInfo': '1.0',
                'downloadLocation': 'NOASSERTION',
                'filesAnalyzed': True,
                'licenseDeclared': 'LicenseRef-system',
                'licenseConcluded': 'NOASSERTION',
                'licenseInfoFromFiles': ['NOASSERTION'],
                'packageVerificationCode': {'packageVerificationCodeValue': '0' * 40},
                'externalRefs': [{
                    'referenceCategory': 'PACKAGE-MANAGER',
                    'referenceType': 'purl',
                    'referenceLocator': 'pkg:deb/debian/libsystem@1.0?arch=amd64&distro=debian-13',
                }],
            }],
            'files': builder_files,
            'hasExtractedLicensingInfos': [{
                'licenseId': 'LicenseRef-system', 'extractedText': 'System license text',
            }],
            'relationships': [{
                'spdxElementId': 'SPDXRef-builder-system-library',
                'relationshipType': 'CONTAINS', 'relatedSpdxElement': record['SPDXID'],
            } for record in system_files],
        }
        fixture.document = compose(builder, final_inventory=inventory)
        fixture.context.builder_document = builder
        generator_document = deepcopy(fixture.document)
        generator_packages = {package['SPDXID']: package for package in generator_document['packages']}
        generator_relationships = generator_document['relationships']
        generator_files = generator_document['files']
        generator_licenses = generator_document['hasExtractedLicensingInfos']
        output = fixture.run_hook()
        set_document_namespace(output, 'pg-demo', 'linux/amd64')
        path = fixture.root / 'pgrx.spdx.json'
        path.write_text(json.dumps(output))
        findings = validate_full_spdx_document(parse_from_file(str(path)))
        self.assertEqual([], findings, '\n'.join(str(finding) for finding in findings))
        packages = {package['name']: package for package in output['packages']}
        self.assertEqual({'demo', 'runtime'} | ({'libsystem'} if ship_system_library else set()),
                         set(packages))
        self.assertEqual(generator_files, output['files'])
        self.assertTrue(all(license in output['hasExtractedLicensingInfos']
                            for license in generator_licenses))
        if ship_system_library:
            self.assertEqual('LicenseRef-system', packages['libsystem']['licenseDeclared'])
            expected = hashlib.sha1(hashlib.sha1(b'shipped system library').hexdigest().encode()).hexdigest()
            self.assertEqual(expected, packages['libsystem']['packageVerificationCode']['packageVerificationCodeValue'])
        output_packages = {package['SPDXID']: package for package in output['packages']}
        self.assertTrue(all(output_packages[package_id] == package
                            for package_id, package in generator_packages.items()))
        self.assertTrue(all(relationship in output['relationships']
                            for relationship in generator_relationships))
        root = packages['demo']
        self.assertEqual('MIT', root['licenseDeclared'])
        self.assertFalse(root['filesAnalyzed'])
        self.assertNotIn('licenseInfoFromFiles', root)
        self.assertIn({'spdxElementId': 'SPDXRef-DOCUMENT', 'relationshipType': 'DESCRIBES',
                       'relatedSpdxElement': root['SPDXID']}, output['relationships'])
        self.assertFalse(any(
            relation.get('spdxElementId') == root['SPDXID'] and relation.get('relationshipType') == 'CONTAINS'
            for relation in output['relationships']
        ))
        license_file = next(file for file in output['files']
                            if file['fileName'].endswith('licenses/rust/license.txt'))
        self.assertEqual(['NOASSERTION'], license_file['licenseInfoInFiles'])
        cargo_ids = {package['SPDXID'] for package in output['packages']
                     if any(ref.get('referenceType') == 'purl'
                            and ref.get('referenceLocator', '').startswith('pkg:cargo/')
                            for ref in package.get('externalRefs', []))}
        self.assertFalse(any(
            relation.get('spdxElementId') in cargo_ids
            and relation.get('relationshipType') == 'CONTAINS'
            for relation in output['relationships']
        ))
        self.assertTrue(any(
            annotation.get('annotator') == 'Tool: cnpg-pgrx-hook-v1'
            for annotation in output['annotations']
        ))

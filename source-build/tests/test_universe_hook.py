"""Shared inventory, notice preservation and source-built package boundaries."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[2]


class HookComposition(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location(
            'universe_hook', ROOT / 'universe/pg-duckdb/augment_spdx.py')
        self.hook = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.hook)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.builder, self.final = self.root / 'builder', self.root / 'final'
        self.document = dict(SPDXID='SPDXRef-DOCUMENT', packages=[], files=[], relationships=[])
        self.context = SimpleNamespace(api_version=1, builder_path=self.builder,
                                       final_path=self.final, platform='linux/arm64')
        self.add_file('install/usr/lib/postgresql/18/lib/pg_duckdb.so', 'lib/pg_duckdb.so', 'extension binary')
        self.add_file('system/libduckdb.so', 'system/libduckdb.so', 'engine binary')
        self.add_file('install/usr/share/postgresql/18/extension/pg_duckdb.control',
                      'share/extension/pg_duckdb.control', 'control')
        for name in ['pg_duckdb', *self.hook.DEBIAN_PACKAGES]:
            path = 'licenses/' + name + '/copyright'
            self.add_file(path, path, 'Copyright authors of ' + name + '\nOriginal combined license terms')
        self.add_file('licenses/libduckdb2.0/Apache-2.0', 'licenses/libduckdb2.0/Apache-2.0', 'Full Apache terms')

    def add_file(self, source, target, text):
        for root, path in [(self.builder, source), (self.final, target)]:
            file = root / path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(text)
        self.document['files'].append(dict(SPDXID='SPDXRef-file-' + str(len(self.document['files'])),
            fileName='./' + target, checksums=[dict(algorithm='SHA256',
            checksumValue=hashlib.sha256(text.encode()).hexdigest())]))

    def file_id(self, path):
        return next(f['SPDXID'] for f in self.document['files'] if f['fileName'] == './' + path)

    def run_hook(self):
        return self.hook.augment_spdx(self.document, self.context)

    def test_preserves_scan_and_adds_source_identity(self):
        installed = dict(SPDXID='SPDXRef-installed', name='libc6', versionInfo='2.41')
        self.document['packages'].append(installed)
        before = copy.deepcopy(self.document)
        result = self.run_hook()
        self.assertEqual(self.document, before)
        self.assertIn(installed, result['packages'])
        self.assertEqual(result['files'], before['files'])
        packages = {p['name']: p for p in result['packages']}
        self.assertEqual(set(packages), {'libc6', 'pg_duckdb', *self.hook.DEBIAN_PACKAGES})
        self.assertEqual(packages['libduckdb2.0']['versionInfo'], '2.0.0')
        self.assertIn(dict(spdxElementId=packages['libzstd1']['SPDXID'], relationshipType='DEPENDS_ON',
                           relatedSpdxElement=packages['libxxhash0']['SPDXID']), result['relationships'])
        self.assertIn(dict(spdxElementId=self.file_id('system/libduckdb.so'), relationshipType='GENERATED_FROM',
                           relatedSpdxElement=packages['libduckdb2.0']['SPDXID']), result['relationships'])

    def test_payload_and_shared_inventory_binding(self):
        path = self.final / 'lib/pg_duckdb.so'
        path.write_text('binary changed')
        with self.assertRaisesRegex(ValueError, 'builder/final payload mismatch'):
            self.run_hook()
        path.write_bytes((self.builder / 'install/usr/lib/postgresql/18/lib/pg_duckdb.so').read_bytes())
        self.document['files'][0]['checksums'][0]['checksumValue'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'shared inventory hash mismatch'):
            self.run_hook()
        self.document['files'].pop(0)
        with self.assertRaisesRegex(ValueError, 'payload missing from shared inventory'):
            self.run_hook()

    def test_notice_only_builder_records_are_replaced_but_binaries_retained(self):
        self.add_file('system/liblz4.so.1', 'system/liblz4.so.1', 'system binary')
        installed = dict(SPDXID='SPDXRef-installed', name='liblz4-1', versionInfo='1.10.0-4')
        notice_only = dict(SPDXID='SPDXRef-notice-only', name='liblz4-1', versionInfo='1.10.0-4')
        self.document['packages'] = [installed, notice_only]
        for package, path in [(installed, 'system/liblz4.so.1'), (notice_only, 'licenses/liblz4-1/copyright')]:
            self.document['relationships'].append(dict(spdxElementId=package['SPDXID'],
                relationshipType='CONTAINS', relatedSpdxElement=self.file_id(path)))
        result = self.run_hook()
        self.assertIn(installed, result['packages'])
        self.assertNotIn(notice_only, result['packages'])
        self.assertIn(self.document['relationships'][0], result['relationships'])
        mapped = next(p for p in result['packages'] if p['name'] == 'liblz4-1' and p['versionInfo'] == '1.9.4')
        self.assertIn('not installed by dpkg', mapped['sourceInfo'])

    def test_debian_mapping_retains_compiled_version_and_source_name(self):
        result = self.run_hook()
        package = next(p for p in result['packages'] if p['name'] == 'libzstd1')
        purl = package['externalRefs'][0]['referenceLocator']
        self.assertEqual(urlsplit(purl).path, 'deb/debian/libzstd1@1.5.6')
        self.assertEqual(parse_qs(urlsplit(purl).query),
                         dict(arch=['arm64'], distro=['debian-unstable'], upstream=['libzstd']))

    def test_consolidated_notices_preserved_by_hook(self):
        result = self.run_hook()
        extracted = {item['licenseId']: item['extractedText'] for item in result['hasExtractedLicensingInfos']}
        for package in result['packages']:
            directory = self.final / 'licenses' / package['name']
            expected = '\n\n'.join(p.read_text() for p in sorted(directory.iterdir()))
            self.assertEqual(extracted[package['licenseDeclared']], expected)
            for notice in directory.iterdir():
                self.assertIn(dict(spdxElementId=package['SPDXID'], relationshipType='DISTRIBUTION_ARTIFACT',
                    relatedSpdxElement=self.file_id(str(notice.relative_to(self.final)))), result['relationships'])

    def test_source_update_requires_inventory_review(self):
        with patch('subprocess.check_output', side_effect=[self.hook.PG_REVISION, 'updated source']):
            with self.assertRaisesRegex(ValueError, 'Review the static package inventory'):
                self.hook.check_sources()


if __name__ == '__main__':
    unittest.main()

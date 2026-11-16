"""Shared inventory, notice preservation and source-built package boundaries."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
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
        self.final = self.root / 'final'
        self.builder = self.root / 'builder'
        self.build = self.builder / 'build'
        duck = self.build / 'third_party/duckdb'
        def write(path, text):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        write(self.build / 'pg_duckdb.control', "default_version = '1.2.0'\n")
        write(duck / 'build/release/DuckDBConfigVersion.cmake', 'set(PACKAGE_VERSION "v2.0.0")\n')
        for path, prefix, parts, version in [
            ('brotli/common/version.h', 'BROTLI_VERSION_', ('MAJOR', 'MINOR', 'PATCH'), (1, 1, 0)),
            ('lz4/lz4.hpp', 'LZ4_VERSION_', ('MAJOR', 'MINOR', 'RELEASE'), (1, 9, 4)),
            ('mbedtls/include/mbedtls/build_info.h', 'MBEDTLS_VERSION_', ('MAJOR', 'MINOR', 'PATCH'), (3, 6, 7)),
            ('yyjson/include/yyjson.hpp', 'YYJSON_VERSION_', ('MAJOR', 'MINOR', 'PATCH'), (0, 9, 0)),
            ('zstd/include/zstd.h', 'ZSTD_VERSION_', ('MAJOR', 'MINOR', 'RELEASE'), (1, 5, 6)),
            ('zstd/include/zstd/common/xxhash.hpp', 'XXH_VERSION_', ('MAJOR', 'MINOR', 'RELEASE'), (0, 6, 2)),
        ]:
            write(duck / 'third_party' / path, ''.join(f'#define {prefix}{part} {value} /* upstream */\n'
                                                     for part, value in zip(parts, version)))
        write(self.build / 'snappy-version.h', '#define SNAPPY_MAJOR 1\n#define SNAPPY_MINOR 2\n#define SNAPPY_PATCHLEVEL 1\n')
        self.document = dict(SPDXID='SPDXRef-DOCUMENT', packages=[], files=[], relationships=[])
        self.context = SimpleNamespace(api_version=1, builder_path=self.builder, final_path=self.final, platform='linux/arm64')
        self.add_file('lib/pg_duckdb.so', 'extension binary')
        self.add_file('system/libduckdb.so', 'engine binary')
        self.add_file('share/extension/pg_duckdb.control', 'control')
        for name in ['pg_duckdb', *self.hook.source_packages(self.builder)]:
            path = 'licenses/' + name + '/copyright'
            self.add_file(path, 'Copyright authors of ' + name + '\nOriginal combined license terms')
        self.add_file('licenses/libduckdb2.0/Apache-2.0', 'Full Apache terms')

    def add_file(self, target, text):
        file = self.final / target
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
        self.assertEqual(set(packages), {'libc6', 'pg_duckdb', *self.hook.source_packages(self.builder)})
        self.assertEqual(packages['libduckdb2.0']['versionInfo'], '2.0.0')
        self.assertEqual(packages['pg_duckdb']['SPDXID'], 'SPDXRef-Source-pg-duckdb')
        self.assertEqual(packages['libduckdb2.0']['SPDXID'], 'SPDXRef-Source-libduckdb2.0')
        self.assertIn(dict(spdxElementId=packages['pg_duckdb']['SPDXID'], relationshipType='DEPENDS_ON',
                           relatedSpdxElement=packages['libduckdb2.0']['SPDXID']), result['relationships'])
        for name in self.hook.source_packages(self.builder):
            if name not in ('libduckdb2.0', 'libxxhash0'):
                self.assertIn(dict(spdxElementId=packages['libduckdb2.0']['SPDXID'], relationshipType='DEPENDS_ON',
                                   relatedSpdxElement=packages[name]['SPDXID']), result['relationships'])
        self.assertEqual(len({p['SPDXID'] for p in result['packages']}), len(result['packages']))
        self.assertIn(dict(spdxElementId=packages['libzstd1']['SPDXID'], relationshipType='DEPENDS_ON',
                           relatedSpdxElement=packages['libxxhash0']['SPDXID']), result['relationships'])
        self.assertIn(dict(spdxElementId=self.file_id('system/libduckdb.so'), relationshipType='GENERATED_FROM',
                           relatedSpdxElement=packages['libduckdb2.0']['SPDXID']), result['relationships'])

    def test_notice_only_builder_records_are_replaced_but_binaries_retained(self):
        self.add_file('system/liblz4.so.1', 'system binary')
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
        self.assertIn(dict(spdxElementId=mapped['SPDXID'], relationshipType='DISTRIBUTION_ARTIFACT',
                           relatedSpdxElement=self.file_id('licenses/liblz4-1/copyright')), result['relationships'])

    def test_debian_mapping_retains_compiled_version_and_source_name(self):
        result = self.run_hook()
        package = next(p for p in result['packages'] if p['name'] == 'libzstd1')
        purl = package['externalRefs'][0]['referenceLocator']
        self.assertEqual(urlsplit(purl).path, 'deb/debian/libzstd1@1.5.6')
        self.assertEqual(parse_qs(urlsplit(purl).query),
                         dict(arch=['arm64'], distro=['debian-unstable'], upstream=['libzstd']))

    def test_versions_follow_source_updates(self):
        (self.build / 'pg_duckdb.control').write_text("default_version = '1.3.0'\n")
        header = self.build / 'third_party/duckdb/third_party/zstd/include/zstd.h'
        header.write_text(header.read_text().replace('RELEASE 6', 'RELEASE 8'))
        # Represents the older Snappy branch selected by GCC.
        (self.build / 'snappy-version.h').write_text(
            '#define SNAPPY_MAJOR 1\n#define SNAPPY_MINOR 1\n#define SNAPPY_PATCHLEVEL 7\n')
        result = self.run_hook()
        packages = {p['name']: p for p in result['packages']}
        self.assertEqual(packages['pg_duckdb']['versionInfo'], '1.3.0')
        self.assertTrue(packages['pg_duckdb']['downloadLocation'].endswith('/v1.3.0'))
        self.assertEqual(packages['libsnappy1v5']['versionInfo'], '1.1.7')
        self.assertIn('libzstd1@1.5.8?', packages['libzstd1']['externalRefs'][0]['referenceLocator'])

    def test_missing_or_ambiguous_version_fails(self):
        header = self.build / 'snappy-version.h'
        header.write_text(header.read_text() + '#define SNAPPY_MAJOR 2\n')
        with self.assertRaisesRegex(ValueError, 'expected one version'):
            self.run_hook()
        header.write_text('')
        with self.assertRaisesRegex(ValueError, 'expected one version'):
            self.run_hook()

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



if __name__ == '__main__':
    unittest.main()

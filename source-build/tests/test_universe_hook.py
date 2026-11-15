"""Infrastructure composition contract; no extension runtime behavior."""
import copy
import importlib.util
import json
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'universe/pg-duckdb' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HookComposition(unittest.TestCase):
    def test_preserves_scan_and_adds_source_identity(self):
        hook = load('augment_spdx')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'build').mkdir()
            components = []
            for name, version, revision, parent in [('pg_duckdb', '1.2.0', 'pg-sha', None), ('duckdb', '2.0.0', 'duck-sha', 'pg_duckdb')]:
                components.append(dict(name=name, version=version, revision=revision, parent=parent,
                    repository='https://github.com/duckdb/' + name,
                    purl='pkg:github/duckdb/' + name + '@' + revision,
                    notices=[], license='MIT', copyright='Copyright authors', license_text=''))
            (root / 'build/universe-evidence.json').write_text(json.dumps(dict(components=components, payload=[])))
            document = dict(SPDXID='SPDXRef-DOCUMENT', packages=[dict(SPDXID='SPDXRef-libc', name='libc6', versionInfo='2.41')],
                files=[dict(SPDXID='SPDXRef-so', fileName='./lib/pg_duckdb.so')], relationships=[dict(spdxElementId='SPDXRef-libc', relationshipType='CONTAINS', relatedSpdxElement='SPDXRef-so')])
            before = copy.deepcopy(document)
            result = hook.augment_spdx(document, SimpleNamespace(api_version=1, builder_path=root))
            self.assertEqual(document, before)
            self.assertEqual(result['packages'][0], before['packages'][0])
            self.assertEqual(result['files'], before['files'])
            self.assertIn(before['relationships'][0], result['relationships'])
            package_ids = [p['SPDXID'] for p in result['packages']]
            self.assertEqual(len(package_ids), len(set(package_ids)))
            source_ids = set(package_ids[1:])
            self.assertFalse(any(r['relationshipType'] == 'CONTAINS' and r['spdxElementId'] in source_ids for r in result['relationships']))
            duck = next(p for p in result['packages'] if p['name'] == 'duckdb')
            self.assertEqual(duck['versionInfo'], '2.0.0')
            self.assertEqual(duck['externalRefs'][0]['referenceLocator'], 'pkg:github/duckdb/duckdb@duck-sha')
            self.assertNotIn('cldr', [p['name'] for p in result['packages']])
            self.assertNotIn('Unicode Character Database', [p['name'] for p in result['packages']])

    def test_revision_notices_and_payload_binding(self):
        hook = load('augment_spdx')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'build').mkdir()
            path = 'licenses/Redis HyperLogLog/LICENSE'
            for stage in ['', 'final']:
                notice = root / stage / path
                notice.parent.mkdir(parents=True)
                notice.write_text('Original combined MIT and BSD notices')
            text = (root / path).read_text()
            component = dict(name='pg_duckdb', version=None,
                revision='sha:third_party/hyperloglog', parent=None,
                repository='https://github.com/duckdb/duckdb', purl=None,
                notices=[path], license='LicenseRef-composite', copyright='Copyright authors', license_text=text)
            evidence = dict(components=[component], payload=[dict(path=path, source=path,
                sha256=hashlib.sha256(text.encode()).hexdigest())])
            (root / 'build/universe-evidence.json').write_text(json.dumps(evidence))
            document = dict(SPDXID='SPDXRef-DOCUMENT', packages=[], relationships=[], files=[
                dict(SPDXID='SPDXRef-notice', fileName='./' + path, checksums=[dict(
                    algorithm='SHA256', checksumValue=evidence['payload'][0]['sha256'])]),
                dict(SPDXID='SPDXRef-so', fileName='./lib/pg_duckdb.so')])
            context = SimpleNamespace(api_version=1, builder_path=root, final_path=root / 'final')
            result = hook.augment_spdx(document, context)
            package = result['packages'][0]
            self.assertNotIn('versionInfo', package)
            self.assertEqual(package['downloadLocation'], 'https://github.com/duckdb/duckdb/tree/sha/third_party/hyperloglog')
            self.assertEqual(result['hasExtractedLicensingInfos'][0]['extractedText'], text)
            self.assertIn(dict(spdxElementId=package['SPDXID'], relationshipType='DISTRIBUTION_ARTIFACT',
                               relatedSpdxElement='SPDXRef-notice'), result['relationships'])
            (root / 'final' / path).write_text('notice lost during staging')
            with self.assertRaisesRegex(ValueError, 'builder/final payload mismatch'):
                hook.augment_spdx(document, context)

    def test_debian_boundaries_preserve_notices_and_real_package_origins(self):
        hook = load('augment_spdx')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'build').mkdir()
            components = []
            for name, parent, counterpart in [
                ('pg_duckdb', None, None), ('duckdb', 'pg_duckdb', None),
                ('lz4', 'duckdb', 'liblz4-1'), ('zstd', 'duckdb', 'libzstd1'),
                ('xxhash', 'zstd', 'libxxhash0'),
            ]:
                components.append(dict(name=name, version='1.0', revision='sha',
                    parent=parent, debian_package=counterpart,
                    repository='https://github.com/example/' + name,
                    purl='pkg:github/example/' + name + '@1.0',
                    notices=['licenses/' + name + '/LICENSE'],
                    license='MIT', copyright='Copyright ' + name,
                    license_text='Original terms for ' + name))
            files = [dict(SPDXID='SPDXRef-file-' + c['name'],
                          fileName='./' + c['notices'][0]) for c in components]
            files += [dict(SPDXID='SPDXRef-pg-so', fileName='./lib/pg_duckdb.so'),
                      dict(SPDXID='SPDXRef-duck-so', fileName='./system/libduckdb.so')]
            debian = dict(SPDXID='SPDXRef-debian-lz4', name='liblz4-1',
                          externalRefs=[dict(referenceType='purl',
                                             referenceLocator='pkg:deb/debian/liblz4-1@1.10')])
            document = dict(SPDXID='SPDXRef-DOCUMENT', packages=[debian], files=files,
                            relationships=[], comment='Existing generator scope')
            (root / 'build/universe-evidence.json').write_text(json.dumps(
                dict(components=components, payload=[])))
            result = hook.augment_spdx(document, SimpleNamespace(api_version=1, builder_path=root))
            packages = {p['name']: p for p in result['packages']}
            self.assertEqual(set(packages), {'liblz4-1', 'pg_duckdb', 'duckdb', 'lz4', 'zstd', 'xxhash'})
            self.assertEqual(packages['liblz4-1'], debian)
            self.assertEqual(packages['lz4']['externalRefs'][0]['referenceLocator'],
                             'pkg:github/example/lz4@1.0')
            self.assertIn('not installed by dpkg', packages['lz4']['sourceInfo'])
            self.assertIn(dict(spdxElementId=packages['zstd']['SPDXID'], relationshipType='DEPENDS_ON',
                               relatedSpdxElement=packages['xxhash']['SPDXID']), result['relationships'])
            self.assertIn(dict(spdxElementId='SPDXRef-duck-so', relationshipType='GENERATED_FROM',
                               relatedSpdxElement=packages['duckdb']['SPDXID']), result['relationships'])
            self.assertTrue(result['comment'].startswith('Existing generator scope'))
            self.assertIn('not an exhaustive', result['comment'])

    def test_notice_only_builder_records_are_replaced_but_binaries_retained(self):
        evidence, hook = load('evidence'), load('augment_spdx')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ['pg_duckdb', 'liblz4-1']:
                notice = root / 'licenses' / name / 'copyright'
                notice.parent.mkdir(parents=True)
                notice.write_text('Copyright 2026 authors; terms')
            components = [evidence.package('pg_duckdb', '1.2.0', 'https://example.com', 'rev', None, root=root),
                evidence.package('liblz4-1', '1.9.4', 'https://example.com', 'rev', 'pg_duckdb',
                    evidence.debian_purl('liblz4-1', 'lz4', '1.9.4', 'amd64'), debian='liblz4-1', root=root)]
            (root / 'build').mkdir()
            (root / 'build/universe-evidence.json').write_text(json.dumps(dict(components=components, payload=[])))
            installed = dict(SPDXID='SPDXRef-installed', name='liblz4-1', versionInfo='1.10.0-4')
            notice_only = dict(SPDXID='SPDXRef-notice-only', name='liblz4-1', versionInfo='1.10.0-4')
            document = dict(SPDXID='SPDXRef-DOCUMENT', packages=[installed, notice_only], files=[
                dict(SPDXID='SPDXRef-pg', fileName='licenses/pg_duckdb/copyright'),
                dict(SPDXID='SPDXRef-notice', fileName='licenses/liblz4-1/copyright'),
                dict(SPDXID='SPDXRef-binary', fileName='system/liblz4.so.1'),
                dict(SPDXID='SPDXRef-pg-so', fileName='lib/pg_duckdb.so')], relationships=[
                dict(spdxElementId='SPDXRef-installed', relationshipType='CONTAINS', relatedSpdxElement='SPDXRef-binary'),
                dict(spdxElementId='SPDXRef-notice-only', relationshipType='CONTAINS', relatedSpdxElement='SPDXRef-notice')])
            result = hook.augment_spdx(document, SimpleNamespace(api_version=1, builder_path=root))
            self.assertIn(installed, result['packages'])
            self.assertNotIn(notice_only, result['packages'])
            self.assertEqual(result['files'], document['files'])
            self.assertIn(document['relationships'][0], result['relationships'])
            mapped = next(p for p in result['packages'] if p['name']=='liblz4-1' and p['versionInfo']=='1.9.4')
            self.assertIn('not installed by dpkg', mapped['sourceInfo'])
            self.assertIn(dict(spdxElementId=mapped['SPDXID'], relationshipType='DISTRIBUTION_ARTIFACT',
                               relatedSpdxElement='SPDXRef-notice'), result['relationships'])

    def test_debian_mapping_retains_compiled_version_and_source_name(self):
        from urllib.parse import urlsplit, parse_qs
        evidence = load('evidence')
        purl = evidence.debian_purl('libzstd1', 'libzstd', '1.5.6', 'arm64')
        self.assertEqual(urlsplit(purl).path, 'deb/debian/libzstd1@1.5.6')
        self.assertEqual(parse_qs(urlsplit(purl).query),
                         dict(arch=['arm64'], distro=['debian-unstable'], upstream=['libzstd']))

    def test_consolidated_notices_preserved_by_hook(self):
        evidence, hook = load('evidence'), load('augment_spdx')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            notice = root / 'licenses/pg_duckdb/copyright'
            notice.parent.mkdir(parents=True)
            text = 'Copyright 2024 Upstream\nMIT terms\n\nCopyright 2015 Embedded author\nComplete Zlib terms\n'
            notice.write_text(text)
            component = evidence.package('pg_duckdb', '1.2.0',
                'https://github.com/duckdb/pg_duckdb', 'revision', None, root=root)
            (root / 'build').mkdir()
            (root / 'build/universe-evidence.json').write_text(json.dumps(dict(components=[component], payload=[])))
            document = dict(SPDXID='SPDXRef-DOCUMENT', packages=[], relationships=[], files=[
                dict(SPDXID='SPDXRef-notice', fileName='./licenses/pg_duckdb/copyright'),
                dict(SPDXID='SPDXRef-so', fileName='./lib/pg_duckdb.so')])
            result = hook.augment_spdx(document, SimpleNamespace(api_version=1, builder_path=root))
            self.assertEqual(result['hasExtractedLicensingInfos'][0]['extractedText'], text)
            package = result['packages'][0]
            self.assertIn(dict(spdxElementId=package['SPDXID'], relationshipType='DISTRIBUTION_ARTIFACT',
                               relatedSpdxElement='SPDXRef-notice'), result['relationships'])


if __name__ == '__main__':
    unittest.main()

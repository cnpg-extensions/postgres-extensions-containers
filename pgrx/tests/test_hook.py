import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'pgrx' / 'sbom'))
from augment_spdx import augment_spdx,license_expression


def digest(data):
    return hashlib.sha256(data).hexdigest()

class HookTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.builder = self.root / 'builder'
        self.final = self.root / 'final'
        self.builder.mkdir(); self.final.mkdir()
        self.evidence = self.builder / 'build/pgrx-sbom'
        self.evidence.mkdir(parents=True)
        elf = bytearray(64); elf[:6] = b'\x7fELF\x02\x01'; elf[18:20] = (62).to_bytes(2, 'little')
        for base, path in [(self.builder, 'build/demo.so'), (self.final, 'lib/demo.so')]:
            file = base / path; file.parent.mkdir(parents=True, exist_ok=True); file.write_bytes(elf)
        self.write_lock()
        self.metadata = {'version': 1, 'packages': [
            {'id': name, 'name': name, 'version': '1.0', 'source': 'registry+https://github.com/rust-lang/crates.io-index', 'license': 'MIT', 'targets': [{'kind': ['lib']}]}
            for name in ['demo', 'runtime', 'build-tool', 'dev-tool', 'unused']],
            'resolve': {'root': 'demo', 'nodes': [
                {'id': 'demo', 'features': ['pg18'], 'deps': [
                    {'pkg': 'runtime', 'dep_kinds': [{'kind': None, 'target': None}]},
                    {'pkg': 'build-tool', 'dep_kinds': [{'kind': 'build', 'target': None}]},
                    {'pkg': 'dev-tool', 'dep_kinds': [{'kind': 'dev', 'target': None}]}]},
                *[{'id': name, 'features': [], 'deps': []} for name in ['runtime', 'build-tool', 'dev-tool', 'unused']]]}}
        self.manifest = {'schema_version': 2, 'identity': {'extension': 'pg-demo', 'sql_name': 'demo', 'source_version': 'v1.0', 'sql_version': '1.0', 'repository': 'example/demo', 'revision': 'a'*40, 'archive_sha256': 'b'*64},
            'target': {'platform': 'linux/amd64', 'rust_target': 'x86_64-unknown-linux-gnu', 'pg_major': '18', 'distro': 'trixie'},
            'build': {'root_id': 'demo', 'manifest': 'Cargo.toml', 'features': ['pg18'], 'default_features': False, 'profile': 'release', 'rustflags': '', 'tools': {'rustc': 'fixture'}},
            'inputs': {'lock_sha256': digest((self.builder/'build/Cargo.lock').read_bytes()), 'timestamp': '2026-01-01T00:00:00Z'},
            'reports': {}, 'licenses': [],
            'payload': [{'builder': 'build/demo.so', 'final': 'lib/demo.so', 'kind': 'library', 'sha256': digest(elf)}]}
        self.write_report('cargo-metadata', self.metadata)
        self.manifest['build']['target_cfg'] = ['target_arch="x86_64"', 'target_os="linux"', 'target_env="gnu"', 'target_pointer_width="64"']
        license_text='MIT fixture license text'
        path=self.final/'licenses/rust/license.txt';path.parent.mkdir(parents=True);path.write_text(license_text)
        self.manifest['licenses']=[{'cargo_id':key,'name':'MIT','final':'licenses/rust/license.txt','sha256':digest(license_text.encode())} for key in ('demo','runtime')]
        self.write_report('cargo-about', {
            'licenses': [{'id':'MIT','text':license_text,'used_by':[{'crate':{'id':key}} for key in ('demo','runtime')]}],
            'crates': [{'package': {'id':key, 'name':key, 'version':'1.0'}, 'license':'MIT'}
                       for key in ('demo','runtime')],
        })
        self.document = {'SPDXID': 'SPDXRef-DOCUMENT', 'spdxVersion': 'SPDX-2.3', 'creationInfo': {'created': '2026-01-01T00:00:00Z', 'creators': ['Tool: generator']},
            'packages': [
                {'SPDXID': 'SPDXRef-OS', 'name': 'debian', 'primaryPackagePurpose': 'OPERATING-SYSTEM', 'filesAnalyzed': False},
                {'SPDXID': 'SPDXRef-libc6', 'name': 'libc6', 'versionInfo': '2.36-9+deb12u10',
                 'filesAnalyzed': False, 'externalRefs': [{'referenceCategory': 'PACKAGE-MANAGER',
                    'referenceType': 'purl', 'referenceLocator': 'pkg:deb/debian/libc6@2.36-9+deb12u10?distro=debian-12'}]},
            ],
            'files': [{'SPDXID': 'SPDXRef-file', 'fileName': 'lib/demo.so',
                       'checksums': [{'algorithm': 'SHA256', 'checksumValue': digest(elf)}],
                       'licenseInfoInFiles': ['Apache-2.0 OR MIT']}],
            'relationships': [
                {'spdxElementId': 'SPDXRef-DOCUMENT', 'relationshipType': 'DESCRIBES', 'relatedSpdxElement': 'SPDXRef-OS'},
                {'spdxElementId': 'SPDXRef-OS', 'relationshipType': 'CONTAINS', 'relatedSpdxElement': 'SPDXRef-libc6'},
            ]}
        self.context = SimpleNamespace(api_version=1, extension_name='extension', platform='linux/amd64', builder_path=self.builder, final_path=self.final, builder_document={'packages': [{'name': 'build-only'}]})

    def write_lock(self, changes=None):
        crates = [{'name': name, 'version': '1.0',
                   'source': 'registry+https://github.com/rust-lang/crates.io-index'}
                  for name in ['demo', 'runtime', 'build-tool', 'dev-tool', 'unused',
                               'cargo-about', 'cargo-pgrx', 'reporter-only-dependency']]
        for crate in crates:
            if changes and crate['name'] in changes:
                crate.update(changes[crate['name']])
        lock = 'version = 3\n' + ''.join('\n[[package]]\n' + ''.join(
            key + ' = ' + json.dumps(value) + '\n' for key, value in crate.items() if value is not None)
            for crate in crates)
        (self.builder/'build/Cargo.lock').write_text(lock)
        if hasattr(self, 'manifest'):
            self.manifest['inputs']['lock_sha256'] = digest(lock.encode())

    def write_report(self, name, value):
        data = json.dumps(value).encode(); (self.evidence / (name+'.json')).write_bytes(data)
        self.manifest['reports'][name] = {'path': name+'.json', 'sha256': digest(data), 'tool_version': 'fixture'}

    def run_hook(self):
        (self.evidence / 'manifest.json').write_text(json.dumps(self.manifest))
        return augment_spdx(self.document, self.context)

    def test_preserves_generator_and_selects_runtime_graph(self):
        before = copy.deepcopy(self.document); builder = copy.deepcopy(self.context.builder_document)
        result = self.run_hook()
        self.assertEqual(self.document, before); self.assertEqual(self.context.builder_document, builder)
        self.assertEqual({p['name'] for p in result['packages']}, {'demo','runtime','debian','libc6'})
        self.assertEqual(result['files'], before['files'])
        self.assertIn(before['relationships'][0], result['relationships'])
        self.assertIn(before['relationships'][1], result['relationships'])
        self.assertIn(before['packages'][0], result['packages'])
        self.assertIn(before['packages'][1], result['packages'])
        self.assertEqual(result['creationInfo'], before['creationInfo'])
        self.assertEqual(result, self.run_hook())
        evidence = json.loads(result['annotations'][0]['comment'])['syft_cargo_lock']
        self.assertEqual(8, evidence['package_count'])
        self.assertEqual('rust-cargo-lock-cataloger', evidence['cataloger'])
        self.assertTrue(evidence['version'])

    def test_invalid_evidence_fails_closed(self):
        for group,key,value in [('target','platform','linux/arm64'), ('identity','extension','wrong'), ('inputs','lock_sha256','0'*64)]:
            with self.subTest(key=key):
                old=self.manifest[group][key]; self.manifest[group][key]=value
                if key=='extension': self.context.extension_name='pg-demo'
                with self.assertRaises(ValueError): self.run_hook()
                self.manifest[group][key]=old; self.context.extension_name='extension'
        self.context.api_version=2
        with self.assertRaises(ValueError): self.run_hook()

    def test_corrupt_report_and_path_escape(self):
        (self.evidence/'cargo-metadata.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'hash'): self.run_hook()
        self.write_report('cargo-metadata',self.metadata)
        self.manifest['reports']['cargo-metadata']['path']='../Cargo.lock'
        with self.assertRaises(ValueError): self.run_hook()

    def test_wrong_elf_and_missing_payload(self):
        wrong_arch = bytearray((self.final/'lib/demo.so').read_bytes())
        wrong_arch[18:20] = (183).to_bytes(2, 'little')
        for root, path in [(self.builder, 'build/demo.so'), (self.final, 'lib/demo.so')]:
            (root/path).write_bytes(wrong_arch)
        wrong_hash = digest(wrong_arch)
        self.manifest['payload'][0]['sha256'] = wrong_hash
        self.document['files'][0]['checksums'][0]['checksumValue'] = wrong_hash
        with self.assertRaisesRegex(ValueError, 'ELF architecture mismatch'): self.run_hook()
        (self.final/'lib/demo.so').unlink()
        with self.assertRaises(ValueError): self.run_hook()

    def test_symlink_escape(self):
        (self.final/'lib/demo.so').unlink()
        (self.final/'lib/demo.so').symlink_to(self.builder/'build/demo.so')
        with self.assertRaises(ValueError): self.run_hook()

    def test_duplicate_json_keys(self):
        (self.evidence/'manifest.json').write_text('{"schema_version":1,"schema_version":2}')
        with self.assertRaises(ValueError): augment_spdx(self.document,self.context)

    def test_spdx_expressions_and_unknown_names(self):
        expression='(MIT OR Apache-2.0) AND GPL-2.0-only WITH Classpath-exception-2.0'
        self.assertEqual(license_expression(expression),expression)
        self.assertEqual(license_expression('Unknown License Name'),'NOASSERTION')
        self.assertEqual(license_expression('MIT AND'),'NOASSERTION')

    def test_cargo_about_resolved_expressions_are_used_for_every_crate(self):
        self.metadata['packages'][0]['license'] = None
        self.metadata['packages'][1]['license'] = 'not an SPDX expression'
        report=json.loads((self.evidence/'cargo-about.json').read_text())
        report['crates'][0]['license']='Apache-2.0 OR MIT'
        report['crates'][1]['license']='(BSD-3-Clause OR MIT) AND Zlib'
        self.write_report('cargo-about',report)
        result=self.run_hook()
        packages={package['name']:package for package in result['packages']}
        self.assertEqual(packages['demo']['licenseDeclared'],'Apache-2.0 OR MIT')
        self.assertEqual(packages['runtime']['licenseDeclared'],'(BSD-3-Clause OR MIT) AND Zlib')

    def test_cargo_about_deprecated_gnu_identifiers_are_canonicalized(self):
        report=json.loads((self.evidence/'cargo-about.json').read_text())
        report['crates'][0]['license']='AGPL-3.0'
        report['crates'][1]['license']='(GPL-2.0+ OR LGPL-2.1) AND GFDL-1.2'
        self.write_report('cargo-about',report)
        packages={package['name']:package for package in self.run_hook()['packages']}
        self.assertEqual(packages['demo']['licenseDeclared'],'AGPL-3.0-only')
        self.assertEqual(packages['runtime']['licenseDeclared'],
                         '(GPL-2.0-or-later OR LGPL-2.1-only) AND GFDL-1.2-only')

    def test_cargo_about_missing_or_unresolved_selected_license_fails(self):
        report=json.loads((self.evidence/'cargo-about.json').read_text())
        report['crates'].pop()
        self.write_report('cargo-about',report)
        with self.assertRaisesRegex(ValueError,'lacks resolved cargo-about licenses'):
            self.run_hook()
        report['crates'].append({'package': {'id':'runtime','name':'runtime','version':'1.0'}, 'license':'Unknown'})
        self.write_report('cargo-about',report)
        with self.assertRaisesRegex(ValueError,'did not resolve a crate license'):
            self.run_hook()

    def test_cargo_about_crate_identity_is_checked(self):
        report=json.loads((self.evidence/'cargo-about.json').read_text())
        report['crates'][0]['package']['name']='different-crate'
        self.write_report('cargo-about',report)
        with self.assertRaisesRegex(ValueError,'package identity mismatch'):
            self.run_hook()

    def test_missing_or_wrong_license_association(self):
        self.manifest['licenses'].pop()
        with self.assertRaisesRegex(ValueError,'missing shipped license'):self.run_hook()

    def test_proc_macro_and_distinct_sources(self):
        from augment_spdx import selected_graph,cargo_purl
        metadata=copy.deepcopy(self.metadata)
        metadata['packages'].append({'id':'macro','name':'macro','version':'1','targets':[{'kind':['proc-macro']},{'kind':['test']},{'kind':['custom-build']}]})
        metadata['resolve']['nodes'].append({'id':'macro','features':[],'deps':[]})
        metadata['resolve']['nodes'][0]['deps'].append({'pkg':'macro','dep_kinds':[{'kind':None,'target':None}]})
        selected,_=selected_graph(metadata,'demo')
        self.assertNotIn('macro',selected)
        a={'name':'same','version':'1.0','source':'registry+https://github.com/rust-lang/crates.io-index'}
        b={**a,'source':'git+https://example.test/repo#'+'a'*40}
        self.assertNotEqual(cargo_purl(a,'a'*40),cargo_purl(b,'a'*40))
        a.update(source=None,manifest_path='/build/one/Cargo.toml')
        b.update(source=None,manifest_path='/build/two/Cargo.toml')
        self.assertNotEqual(cargo_purl(a,'a'*40),cargo_purl(b,'a'*40))
        b['manifest_path']='/outside/Cargo.toml'
        with self.assertRaises(ValueError):cargo_purl(b,'a'*40)

    def test_cargo_license_notices_are_attributed_to_selected_packages(self):
        result = self.run_hook()
        notices = {notice['licenseId']: notice['extractedText']
                   for notice in result['hasExtractedLicensingInfos']}
        notice_id = 'LicenseRef-Cargo-' + hashlib.sha256(b'MIT fixture license text').hexdigest()[:32]
        self.assertEqual(notices[notice_id], 'MIT fixture license text')
        for name in ('demo', 'runtime'):
            package = next(package for package in result['packages'] if package['name'] == name)
            self.assertIn('Cargo license text: ' + notice_id, package['attributionTexts'])

    def test_arm_evidence_as_data(self):
        self.manifest['target'].update(platform='linux/arm64',rust_target='aarch64-unknown-linux-gnu')
        self.manifest['build']['target_cfg'][0] = 'target_arch="aarch64"'
        self.context.platform='linux/arm64'
        data=bytearray((self.final/'lib/demo.so').read_bytes());data[18:20]=(183).to_bytes(2,'little')
        (self.final/'lib/demo.so').write_bytes(data);(self.builder/'build/demo.so').write_bytes(data)
        self.manifest['payload'][0]['sha256']=digest(data)
        self.document['files'][0]['checksums'][0]['checksumValue']=digest(data)
        self.assertTrue(self.run_hook()['packages'])
        self.manifest['target']['rust_target']='x86_64-unknown-linux-gnu'
        with self.assertRaisesRegex(ValueError,'Rust target'):self.run_hook()

    def test_wrong_feature_policy(self):
        self.manifest['build']['default_features']=True
        with self.assertRaisesRegex(ValueError,'default feature'):self.run_hook()

    def test_syft_scan_ignores_tool_and_registry_lockfiles(self):
        for relative in ('tmp/cargo-about/Cargo.lock', 'root/.cargo/registry/src/crate/Cargo.lock'):
            path = self.builder / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('version = 3\n[[package]]\nname = "tool-only"\nversion = "9.9.9"\n')
        result = self.run_hook()
        names = {package['name'] for package in result['packages']}
        self.assertEqual({'demo', 'runtime', 'debian', 'libc6'}, names)
        evidence = json.loads(result['annotations'][0]['comment'])['syft_cargo_lock']
        self.assertEqual(8, evidence['package_count'])

    def test_syft_requires_selected_version_and_source(self):
        for changes in [{'version': '9.9'}, {'source': 'git+https://example.test/other#'+'c'*40}]:
            with self.subTest(changes=changes):
                self.write_lock({'runtime': changes})
                with self.assertRaisesRegex(ValueError, 'selected Cargo identity missing from Syft'):
                    self.run_hook()

    def test_syft_workspace_root_has_no_registry_source(self):
        self.metadata['packages'][0].update(source=None, manifest_path='/build/Cargo.toml')
        self.write_report('cargo-metadata', self.metadata)
        self.write_lock({'demo': {'source': None}})
        root = next(p for p in self.run_hook()['packages'] if p['name'] == 'demo')
        purl = root['externalRefs'][0]['referenceLocator']
        self.assertIn('repository_url=workspace%3A', purl)

    def test_missing_evidence_and_unsupported_schema(self):
        from augment_spdx import augment_spdx
        with self.assertRaises(ValueError):augment_spdx(self.document,self.context)
        self.manifest['schema_version']=3
        with self.assertRaisesRegex(ValueError,'schema'):self.run_hook()

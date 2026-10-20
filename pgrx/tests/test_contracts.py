import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare import digest
from record import assert_provenance, load_preparation
from refresh_lock import tool_url, check_sources, check_apt, fixtures_lock, operator_manifest_url, check_operator_manifest
from verify import signature_command, validate_document
from workflow import ROOT


class LockTest(unittest.TestCase):
    def test_every_locked_tool_url_is_owned_by_its_version(self):
        for filename in ['tools.json','workflow-tools.json']:
            lock=json.loads((ROOT/'pgrx/dependencies'/filename).read_text())
            tools=dict(lock['tools'])
            if 'rustup' in lock:tools['rustup']=lock['rustup']
            for name,tool in tools.items():
                for architecture,pin in tool['platforms'].items():
                    self.assertEqual(tool_url(name,tool['version'],architecture),pin['url'])
                    self.assertNotEqual(tool_url(name,'999.0.0',architecture),pin['url'])

    def test_source_version_update_requires_companion_lock(self):
        pin=json.loads((ROOT/'pgrx/dependencies/sources.json').read_text())['pg-durable']
        metadata={'pg-durable':{'versions':{'trixie':{'18':{'package':pin['version']}}}}}
        check_sources(metadata,{'pg-durable':pin})
        metadata['pg-durable']['versions']['trixie']['18']['package']='v999.0.0'
        with self.assertRaisesRegex(ValueError,'disagreement'):check_sources(metadata,{'pg-durable':pin})

    def test_base_update_invalidates_apt_children(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);(root/'apt').mkdir();(root/'bases.json').write_text('{}')
            (root/'apt/lock.json').write_text(json.dumps({'base_lock_sha256':'0'*64}))
            with self.assertRaisesRegex(ValueError,'coupled apt'):check_apt(root)

    def test_operator_fixtures_are_published_release_manifests(self):
        root=ROOT/'pgrx/dependencies'
        lock=json.loads((root/'fixtures/lock.json').read_text())
        fixtures_lock(root,False)
        self.assertEqual(lock['selector'],'1.30')
        self.assertEqual(lock['supported_releases'],['1.29','1.30'])
        self.assertEqual(set(lock['operators']),set(lock['supported_releases']))
        for selector,pin in lock['operators'].items():
            version=pin['ref'].removeprefix('v')
            manifest=(root/'fixtures'/('operator-'+selector+'.yaml')).read_text()
            self.assertEqual(pin['url'],operator_manifest_url(pin))
            self.assertIn('ghcr.io/cloudnative-pg/cloudnative-pg:'+version,manifest)
            self.assertNotIn('cloudnative-pg-testing',manifest)
            check_operator_manifest(manifest,pin)

    def test_operator_fixture_refresh_rebuilds_release_asset_url(self):
        import refresh_lock
        selector='1.30';ref='v1.30.2';revision='f'*40
        pin={'repository':'cloudnative-pg/cloudnative-pg','ref':ref,'revision':'0'*40,
             'url':'old','sha256':'0'*64}
        payload=('image: ghcr.io/cloudnative-pg/cloudnative-pg:1.30.2\n').encode()
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'dependencies';fixtures=root/'fixtures';fixtures.mkdir(parents=True)
            (fixtures/'lock.json').write_text(json.dumps({'selector':selector,'supported_releases':[selector],
                'operators':{selector:pin},'files':{'operator':pin}}))
            with patch.object(refresh_lock,'api',return_value={'sha':revision}) as api_call, \
                 patch.object(refresh_lock,'fetch',return_value=payload) as fetch_call:
                fixtures_lock(root,True)
            self.assertEqual(api_call.call_args.args[0],'repos/cloudnative-pg/cloudnative-pg/commits/v1.30.2')
            refreshed=json.loads((fixtures/'lock.json').read_text())
            expected=f'https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/{revision}/releases/cnpg-1.30.2.yaml'
            self.assertEqual(refreshed['operators'][selector]['url'],expected)
            self.assertEqual(fetch_call.call_args.args[0],expected)
            self.assertEqual((fixtures/'operator-1.30.yaml').read_bytes(),payload)

    def test_testing_operator_images_are_rejected(self):
        pin={'repository':'cloudnative-pg/cloudnative-pg','ref':'v1.30.1'}
        with self.assertRaisesRegex(ValueError,'production CNPG image'):
            check_operator_manifest('image: ghcr.io/cloudnative-pg/cloudnative-pg-testing:1.30.1',pin)


class ProvenanceTest(unittest.TestCase):
    def setUp(self):
        self.row={'target':'target','base':'base@sha256:'+'a'*64,'source':{'archive_sha256':'b'*64}}
        self.preparation={'generator':'generator@sha256:'+'c'*64}
        self.definition={'target':{'target':{'args':{'PG_MAJOR':'18','PGRX_WORKSPACE_SHA256':'d'*64},'labels':{'revision':'e'*40}}}}
        self.provenance={'buildDefinition':{'externalParameters':{'request':{'args':{
            'build-arg:PG_MAJOR':'18','build-arg:PGRX_WORKSPACE_SHA256':'d'*64,'label:revision':'e'*40}}},
            'resolvedDependencies':[{'digest':{'sha256':v*64}} for v in 'abc']}}

    def test_independent_expected_arguments_and_materials(self):
        assert_provenance(self.provenance,self.preparation,self.row,self.definition)
        for key in ['build-arg:PG_MAJOR','build-arg:PGRX_WORKSPACE_SHA256','label:revision']:
            bad=copy.deepcopy(self.provenance);bad['buildDefinition']['externalParameters']['request']['args'][key]='wrong'
            with self.subTest(key=key),self.assertRaises(ValueError):assert_provenance(bad,self.preparation,self.row,self.definition)
        self.provenance['buildDefinition']['resolvedDependencies'].pop()
        with self.assertRaisesRegex(ValueError,'resolved dependency'):assert_provenance(self.provenance,self.preparation,self.row,self.definition)

    def test_stale_or_tampered_preparation(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary);value={'workspace_sha256':'current'};value['preparation_sha256']=digest(value)
            (path/'preparation.json').write_text(json.dumps(value))
            with patch('record.source_digest',return_value='current'):self.assertEqual(load_preparation(path),value)
            with patch('record.source_digest',return_value='changed'),self.assertRaisesRegex(ValueError,'workspace'):load_preparation(path)
            value['workspace_sha256']='changed';(path/'preparation.json').write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError,'checksum'):load_preparation(path)


class ConsumerPolicyTest(unittest.TestCase):
    def test_explicit_publisher_policy(self):
        policy=r'^https://github\.com/cnpg-extensions/postgres-extensions-containers/\.github/workflows/(bake_targets|pgrx_targets)\.yml@refs/heads/main$'
        for workflow in ['bake_targets','pgrx_targets']:
            good='https://github.com/cnpg-extensions/postgres-extensions-containers/.github/workflows/'+workflow+'.yml@refs/heads/main'
            self.assertRegex(good,policy)
            for wrong in [good.replace('cnpg-extensions','attacker'),good.replace('refs/heads/main','refs/heads/other'),good.replace(workflow,'untrusted'),good+'suffix']:
                self.assertIsNone(re.fullmatch(policy,wrong))
        command=signature_command('image@sha256:'+'a'*64,identity=policy,issuer='https://token.actions.githubusercontent.com')
        self.assertIn(policy,command);self.assertIn('--certificate-oidc-issuer',command)
        with self.assertRaises(ValueError):signature_command('image',identity=policy)

    def test_unresolved_licenses_and_relationships_fail(self):
        document={'SPDXID':'SPDXRef-DOCUMENT','packages':[{'SPDXID':'SPDXRef-test','licenseDeclared':'LicenseRef-missing'}]}
        with self.assertRaisesRegex(ValueError,'license'):validate_document(document)
        document['packages'][0].pop('licenseDeclared');document['relationships']=[{'spdxElementId':'SPDXRef-test','relatedSpdxElement':'SPDXRef-missing'}]
        with self.assertRaisesRegex(ValueError,'relationship'):validate_document(document)


class SignatureStorageTest(unittest.TestCase):
    def test_format_fallback_keeps_the_same_publisher_policy(self):
        import subprocess
        from verify import verify_signature
        image='registry/example@sha256:'+'a'*64
        policy=r'^https://github\.com/owner/repo/\.github/workflows/(bake_targets|pgrx_targets)\.yml@refs/heads/main$'
        signature=[{'critical':{'image':{'docker-manifest-digest':'sha256:'+'a'*64}}}]
        commands=[]
        def run(command):
            commands.append(command)
            if len(commands)==1:raise subprocess.CalledProcessError(1,command)
            return json.dumps(signature).encode()
        with patch('verify.run',side_effect=run):
            self.assertEqual(verify_signature(image,identity=policy,issuer='https://token.actions.githubusercontent.com'),signature)
        self.assertIn('--new-bundle-format=true',commands[0]);self.assertIn('--new-bundle-format=false',commands[1])
        for command in commands:
            self.assertIn(policy,command);self.assertIn('https://token.actions.githubusercontent.com',command)
            self.assertNotIn('--insecure-ignore-tlog=true',command)

    def test_wrong_signed_digest_cannot_fall_back(self):
        from verify import verify_signature
        signature=[{'critical':{'image':{'docker-manifest-digest':'sha256:'+'b'*64}}}]
        with patch('verify.run',return_value=json.dumps(signature).encode()) as run:
            with self.assertRaisesRegex(ValueError,'digest'):verify_signature('image@sha256:'+'a'*64,identity='publisher',issuer='issuer')
            self.assertEqual(run.call_count,1)

class SourceArchiveTest(unittest.TestCase):
    def test_cli_archive_rejects_escaping_paths_and_links(self):
        import io
        import tarfile
        from install_tools import extract_source_archive
        for name,kind in [('cli/Cargo.toml',tarfile.REGTYPE),('../escape',tarfile.REGTYPE),('cli/link',tarfile.SYMTYPE)]:
            raw=io.BytesIO()
            with tarfile.open(fileobj=raw,mode='w') as archive:
                member=tarfile.TarInfo(name);member.type=kind;member.size=4 if kind==tarfile.REGTYPE else 0
                archive.addfile(member,io.BytesIO(b'test') if member.size else None)
            raw.seek(0)
            with tempfile.TemporaryDirectory() as directory,tarfile.open(fileobj=raw) as archive:
                if name=='cli/Cargo.toml':
                    extract_source_archive(archive,directory)
                    self.assertEqual((Path(directory)/name).read_bytes(),b'test')
                else:
                    with self.assertRaises(ValueError):extract_source_archive(archive,directory)

class RuntimeClosureTest(unittest.TestCase):
    def test_quadmath_is_copied_only_when_required_with_its_license(self):
        from system_libraries import stage_extra_libraries
        for needed in [True, False]:
            with self.subTest(needed=needed), tempfile.TemporaryDirectory() as temporary:
                root=Path(temporary);lib=root/'usr/lib/x86_64-linux-gnu';lib.mkdir(parents=True)
                (lib/'libgfortran.so.5').write_bytes(b'fortran');(lib/'libquadmath.so.0').write_bytes(b'quadmath')
                doc=root/'usr/share/doc/libquadmath0';doc.mkdir(parents=True);(doc/'copyright').write_text('copyright evidence')
                output=' 0x0001 (NEEDED) Shared library: [libquadmath.so.0]\n' if needed else ' 0x0001 (NEEDED) Shared library: [libc.so.6]\n'
                with patch('system_libraries.subprocess.check_output',return_value=output):stage_extra_libraries('pg-search',root)
                self.assertEqual((root/'build/pgrx-extra-system/libquadmath.so.0').exists(),needed)
                self.assertEqual((root/'build/pgrx-extra-system-licenses/libquadmath0/copyright').exists(),needed)

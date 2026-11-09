import copy
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
from verify import signature_command, validate_document
from workflow import ROOT


class ProvenanceTest(unittest.TestCase):
    def setUp(self):
        self.row={'target':'target','base':'base@sha256:'+'a'*64,'source':{'archive_sha256':'b'*64,'url':'https://example.test/extension/v1.tar.gz'}}
        self.preparation={'generator':'generator@sha256:'+'c'*64}
        self.definition={'target':{'target':{'args':{'PG_MAJOR':'18','PGRX_WORKSPACE_SHA256':'d'*64},'labels':{'revision':'e'*40}}}}
        self.provenance={'buildDefinition':{'externalParameters':{'request':{'args':{
            'build-arg:PG_MAJOR':'18','build-arg:PGRX_WORKSPACE_SHA256':'d'*64,'label:revision':'e'*40}}},
            'resolvedDependencies':[{'digest':{'sha256':v*64}} for v in 'abc']}}
        self.provenance['buildDefinition']['resolvedDependencies'][1]['uri']=self.row['source']['url']

    def test_independent_expected_arguments_and_materials(self):
        assert_provenance(self.provenance,self.preparation,self.row,self.definition)
        for key in ['build-arg:PG_MAJOR','build-arg:PGRX_WORKSPACE_SHA256','label:revision']:
            bad=copy.deepcopy(self.provenance);bad['buildDefinition']['externalParameters']['request']['args'][key]='wrong'
            with self.subTest(key=key),self.assertRaises(ValueError):assert_provenance(bad,self.preparation,self.row,self.definition)
        self.provenance['buildDefinition']['resolvedDependencies'].pop()
        with self.assertRaisesRegex(ValueError,'resolved dependency'):assert_provenance(self.provenance,self.preparation,self.row,self.definition)

    def test_source_url_and_checksum_must_match_the_same_dependency(self):
        materials=self.provenance['buildDefinition']['resolvedDependencies']
        materials[1]['uri']='https://example.test/other.tar.gz'
        materials.append({'uri':self.row['source']['url'],'digest':{'sha256':'f'*64}})
        with self.assertRaisesRegex(ValueError,'source resolved dependency'):
            assert_provenance(self.provenance,self.preparation,self.row,self.definition)

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

class InlineCorrectionTest(unittest.TestCase):
    def test_changed_or_fixed_lock_requires_review(self):
        import subprocess
        dockerfile = (ROOT / 'pg-session-jwt/Dockerfile').read_text()
        guard = dockerfile.split("RUN echo '", 1)[1].split('\nRUN cp ', 1)[0]
        command = "echo '" + guard.replace('\\\n', '')
        for lock in ['changed upstream lock', '[[package]]\nname = "pg_session_jwt"\nversion = "0.5.0"\n']:
            with self.subTest(lock=lock), tempfile.TemporaryDirectory() as directory:
                (Path(directory) / 'Cargo.lock').write_text(lock)
                result = subprocess.run(['bash', '-c', command], cwd=directory, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('review/remove', result.stderr)

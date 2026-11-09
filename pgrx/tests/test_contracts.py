import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare import digest
from record import load_preparation
from verify import signature_command


class PreparationTest(unittest.TestCase):
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

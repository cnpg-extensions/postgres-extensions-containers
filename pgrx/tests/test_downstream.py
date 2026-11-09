import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import downstream


class DownstreamTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.assembly_dir = self.root / 'assembly'
        self.assembly_dir.mkdir()
        self.output = self.root / 'output'
        self.preparation = {
            'preparation_sha256': 'prepared-inputs',
            'targets': ['pg18-trixie'],
            'run_id': '123-2',
        }
        self.digest = 'sha256:' + 'a' * 64
        self.assembly = {
            'preparation_sha256': 'prepared-inputs',
            'target': 'pg18-trixie',
            'run_id': '123-2',
            'image': 'registry.test/extension-testing@' + self.digest,
            'index_digest': self.digest,
            'platforms': ['linux/amd64', 'linux/arm64'],
            'tags': ['registry.test/extension-testing:18',
                     'registry.test/extension-testing:latest',
                     'mirror.test/extension-testing:18'],
        }
        self.addCleanup(patch.stopall)
        patch('downstream.load_preparation', return_value=self.preparation).start()
        self.run = patch('downstream.subprocess.run').start()
        self.inspect = patch('downstream.subprocess.check_output').start()

    def invoke(self, stage):
        (self.assembly_dir / 'assembly.json').write_text(json.dumps(self.assembly))
        with patch.object(sys, 'argv', [
            'downstream.py', stage,
            '--preparation', str(self.root / 'preparation'),
            '--assembly', str(self.assembly_dir),
            '--output', str(self.output),
        ]):
            downstream.main()

    def sboms(self):
        return {
            platform: {'SPDX': {
                'spdxVersion': 'SPDX-2.3',
                'name': 'extension-' + platform,
                'packages': [{'name': 'native-' + platform.split('/')[1]}],
            }}
            for platform in self.assembly['platforms']
        }

    def test_security_scans_each_platform_document_from_one_inspection(self):
        sboms = self.sboms()
        self.inspect.return_value = json.dumps(sboms).encode()
        scanned = []

        def scan(command, *, stdout, check):
            self.assertTrue(check)
            sbom_path = Path(command[1].removeprefix('sbom:')
                             if command[0] == 'grype' else command[2])
            scanned.append((command[0], sbom_path.parent.name,
                            json.loads(sbom_path.read_text())))
            stdout.write('{}\n')

        self.run.side_effect = scan
        self.invoke('security')
        self.inspect.assert_called_once_with([
            'docker', 'buildx', 'imagetools', 'inspect', self.assembly['image'],
            '--format', '{{json .SBOM}}',
        ])
        self.assertEqual(scanned, [
            (tool, platform.split('/')[1], sboms[platform]['SPDX'])
            for platform in self.assembly['platforms']
            for tool in ('grype', 'grant')
        ])
        self.assertTrue(json.loads((self.output / 'result.json').read_text())['success'])

    def test_security_fails_when_second_platform_document_is_missing(self):
        sboms = self.sboms()
        del sboms['linux/arm64']
        self.inspect.return_value = json.dumps(sboms).encode()
        with self.assertRaisesRegex(ValueError, 'missing SPDX document for linux/arm64'):
            self.invoke('security')
        self.assertFalse((self.output / 'result.json').exists())


if __name__ == '__main__':
    unittest.main()

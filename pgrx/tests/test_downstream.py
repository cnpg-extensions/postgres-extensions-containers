import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import downstream


class DownstreamTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output = self.root / 'output'
        self.image = 'registry.test/extension-testing@sha256:' + 'a' * 64
        self.platforms = ['linux/amd64', 'linux/arm64']
        workflow = Path(__file__).resolve().parents[2] / '.github/workflows/pgrx_targets.yml'
        self.images = yaml.safe_load(workflow.read_text())['jobs']['security']['env']
        self.addCleanup(patch.stopall)
        patch.dict(os.environ, self.images).start()
        self.run = patch('downstream.subprocess.run').start()
        self.inspect = patch('downstream.subprocess.check_output').start()

    def invoke(self):
        with patch.object(sys, 'argv', [
            'downstream.py', '--image', self.image,
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
            for platform in self.platforms
        }

    def test_security_scans_each_platform_document_from_one_inspection(self):
        sboms = self.sboms()
        self.inspect.return_value = json.dumps(sboms).encode()
        scanned = []

        def scan(command, *, stdout, check):
            self.assertTrue(check)
            self.assertEqual(command[:3], ['docker', 'run', '--rm'])
            mount = command[command.index('--volume') + 1]
            host, container, mode = mount.rsplit(':', 2)
            self.assertEqual((container, mode), ('/results', 'ro'))
            directory = Path(host)
            self.assertTrue(directory.is_absolute())
            tool = 'grype' if self.images['GRYPE_IMAGE'] in command else 'grant'
            scanner = self.images[tool.upper() + '_IMAGE']
            self.assertIn(scanner, command)
            arguments = command[command.index(scanner) + 1:]
            self.assertEqual(arguments, (
                ['sbom:/results/sbom.spdx.json', '-o', 'json'] if tool == 'grype'
                else ['list', '/results/sbom.spdx.json', '-o', 'json']
            ))
            scanned.append((tool, directory.name,
                            json.loads((directory / 'sbom.spdx.json').read_text())))
            stdout.write('{}\n')

        self.run.side_effect = scan
        self.invoke()
        self.inspect.assert_called_once_with([
            'docker', 'buildx', 'imagetools', 'inspect', self.image,
            '--format', '{{json .SBOM}}',
        ])
        self.assertEqual(scanned, [
            (tool, platform.split('/')[1], sboms[platform]['SPDX'])
            for platform in self.platforms
            for tool in ('grype', 'grant')
        ])

if __name__ == '__main__':
    unittest.main()

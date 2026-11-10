"""Protect native scheduling and the Bake metadata handoff used by release jobs."""

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import check_native
from prepare import prepare

ROOT = Path(__file__).resolve().parents[2]


class NativeWorkflowTest(unittest.TestCase):
    def test_each_prepared_job_builds_only_its_native_platform(self):
        target = 'example-18-trixie'
        original = {
            'args': {'EXT_VERSION': 'v1.0', 'PG_MAJOR': '18', 'BASE': 'example/base:18'},
            'tags': ['example/extension:18'],
            'platforms': ['linux/amd64', 'linux/arm64'],
            'annotations': ['index,manifest:io.cloudnativepg.image.base.os=trixie'],
            'attest': ['type=provenance,mode=max', 'type=sbom'],
        }
        with tempfile.TemporaryDirectory() as temporary, \
             patch.dict(os.environ, GITHUB_REPOSITORY_OWNER='example', GITHUB_RUN_ID='123'), \
             patch('prepare.discover', return_value={'example': {
                 'source_repository': 'https://github.com/example/extension', 'image_name': 'extension',
             }}), \
             patch('prepare.execute', side_effect=['a' * 40, json.dumps({'target': {target: original}})]), \
             patch('prepare.resolve_source', return_value={'revision': 'b' * 40}), \
             patch('prepare.platform_base', side_effect=lambda ref, platform, **kw: (
                 ref + '@sha256:' + ('c' if platform.endswith('amd64') else 'd') * 64, 'unused',
             )):
            directory = Path(temporary) / 'prepared'
            plan = prepare({'extension_name': 'example'}, 'example/generator@sha256:' + 'e' * 64, directory)
            jobs = yaml.safe_load((ROOT / '.github/workflows/pgrx_targets.yml').read_text())['jobs']
            job = jobs['build-platform']
            self.assertEqual(job['runs-on'], '${{ matrix.runner }}')
            steps = job['steps']
            bake = next(s for s in steps if s.get('id') == 'build')
            self.assertEqual(bake['with']['files'], '${{ runner.temp }}/prepared/${{ matrix.id }}.json')
            self.assertEqual(bake['with']['targets'], '${{ matrix.target }}')
            self.assertEqual(bake['with']['builder'], '${{ steps.buildx.outputs.name }}')
            self.assertLess(next(i for i, s in enumerate(steps) if s.get('name') == 'Require native build execution'), steps.index(bake))
            self.assertEqual(len(plan['rows']), 2)
            for row in plan['rows']:
                definition = json.loads((directory / (row['id'] + '.json')).read_text())['target'][target]
                self.assertEqual(definition['platforms'], ['linux/' + row['architecture']])
                self.assertEqual(row['runner'].endswith('-arm'), row['architecture'] == 'arm64')
                self.assertEqual(definition['tags'], [row['staging']])
                self.assertEqual(definition['attest'], original['attest'])
            self.assertNotEqual(plan['rows'][0]['staging'], plan['rows'][1]['staging'])

    def test_emulation_does_not_make_a_foreign_worker_native(self):
        for arch, machine in [('amd64', 'x86_64'), ('arm64', 'aarch64')]:
            with self.subTest(arch=arch), patch('build.platform.machine', return_value=machine), \
                 patch('build.subprocess.check_output', side_effect=[machine, machine]):
                check_native(arch, 'local-builder')
        for host, daemon, worker in [('aarch64', 'x86_64', 'x86_64'),
                                     ('x86_64', 'aarch64', 'x86_64'),
                                     ('x86_64', 'x86_64', 'aarch64')]:
            with self.subTest(host=host, daemon=daemon, worker=worker), \
                 patch('build.platform.machine', return_value=host), \
                 patch('build.subprocess.check_output', side_effect=[daemon, worker]):
                with self.assertRaisesRegex(ValueError, 'must match amd64'):
                    check_native('amd64', 'local-builder')

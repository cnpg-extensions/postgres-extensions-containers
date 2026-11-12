"""Execute both workflows' selection steps on a host with bash and jq.

The contract-test container exports the parsed workflows as JSON on stdin so
this runner needs only the hosted runner's standard Python library and jq.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

WORKFLOWS = json.load(sys.stdin)


def run_step(step, **values):
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / 'output'
        environment = {**os.environ, 'GITHUB_OUTPUT': str(output), 'GITHUB_ENV': str(output), **values}
        result = subprocess.run(['bash', '-Eeuo', 'pipefail', '-c', step['run']],
                                env=environment, capture_output=True, text=True)
        return result, output.read_text() if output.exists() else ''


class SelectionTest(unittest.TestCase):
    def jobs(self):
        for name, workflow in WORKFLOWS.items():
            job = workflow['jobs']['discover' if name == 'pgrx' else 'change-triage']
            yield name, job

    def test_selection_cases_for_both_families(self):
        for name, job in self.jobs():
            step = next(s for s in job['steps'] if s.get('id') == 'get-matrix')
            sample = json.loads(step['env']['INFRASTRUCTURE_SAMPLE'])
            targets = sample + ['fixture-extension']
            cases = [
                ('pull_request_target', 'a' * 40, ['_shared'], '', sample),
                ('pull_request_target', 'a' * 40, [], '', []),
                ('pull_request', 'refs/pull/1/merge', ['_shared'], '', sample),
                ('merge_group', 'refs/heads/gh-readonly-queue/main/test', ['_shared', 'fixture-extension'], '', targets),
                ('push', 'refs/heads/main', ['_shared', '_test_fixture-extension'], '', []),
                ('push', 'refs/heads/main', ['_shared', 'fixture-extension'], '', ['fixture-extension']),
                ('pull_request', 'refs/pull/1/merge', ['_test_fixture-extension'], '', ['fixture-extension']),
                ('pull_request', 'refs/pull/1/merge', [], '', []),
                ('pull_request', 'refs/pull/1/merge', ['_shared', sample[0], '_test_' + sample[0]], '', sample),
                ('workflow_dispatch', 'refs/heads/main', [], 'all', targets),
                ('workflow_dispatch', 'refs/heads/main', [], 'fixture-extension', ['fixture-extension']),
            ]
            for event, ref, changes, requested, expected in cases:
                with self.subTest(workflow=name, event=event, ref=ref, changes=changes, requested=requested):
                    result, output = run_step(step, CHANGES=json.dumps(changes), EVENT_NAME=event,
                        GITHUB_REF=ref, SELECTION_REF=ref, INPUT_EXTENSION_NAME=requested, VALID_TARGETS=json.dumps(targets),
                        INFRASTRUCTURE_SAMPLE=json.dumps(sample))
                    self.assertEqual(result.returncode, 0, result.stderr)
                    selected = json.loads(output.strip().removeprefix('matrix='))
                    self.assertEqual(sorted(selected), sorted(expected))
                    self.assertEqual(len(selected), len(set(selected)))
            result, _ = run_step(step, CHANGES='["_shared"]', EVENT_NAME='pull_request',
                GITHUB_REF='refs/pull/1/merge', SELECTION_REF='refs/pull/1/merge', INPUT_EXTENSION_NAME='', VALID_TARGETS='[]',
                INFRASTRUCTURE_SAMPLE=json.dumps(sample))
            self.assertNotEqual(result.returncode, 0)

    def test_dispatch_validation_and_empty_discovery(self):
        for name, job in self.jobs():
            validation = next(s for s in job['steps'] if s.get('name') == 'Validate extension name')
            filters = next(s for s in job['steps'] if s.get('name') == 'Compute paths-filter extensions block')
            for requested, succeeds in [('all', True), ('fixture-extension', True), ('unknown', False)]:
                with self.subTest(workflow=name, requested=requested):
                    result, _ = run_step(validation, INPUT_EXTENSION_NAME=requested, VALID_TARGETS='["fixture-extension"]')
                    self.assertEqual(result.returncode == 0, succeeds)
            result, _ = run_step(filters, VALID_TARGETS='[]')
            self.assertNotEqual(result.returncode, 0)
            result, output = run_step(filters, VALID_TARGETS='["fixture-extension"]')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('_test_fixture-extension:', output)
            self.assertIn('!fixture-extension/test/**', output)
            self.assertIn('!fixture-extension/**/*.md', output)

    def test_discovery_and_filter_wiring(self):
        for name, job in self.jobs():
            with self.subTest(workflow=name):
                self.assertEqual(job['permissions']['pull-requests'], 'read')
                discovery = next(s for s in job['steps'] if s.get('id') == 'get-targets')
                self.assertEqual(discovery['with']['args'], 'get-targets --build-system pgrx' if name == 'pgrx' else 'get-targets')
                filtering = next(s for s in job['steps'] if s.get('id') == 'filter')
                self.assertEqual(filtering['if'], "github.event_name != 'workflow_dispatch'")
                self.assertEqual(filtering['with']['predicate-quantifier'], 'some-with-excludes')
                matrix = next(s for s in job['steps'] if s.get('id') == 'get-matrix')
                self.assertEqual(matrix['env']['CHANGES'], '${{ steps.filter.outputs.changes }}')
                self.assertEqual(matrix['env']['VALID_TARGETS'], '${{ steps.get-targets.outputs.output }}')
                self.assertIn('steps.get-matrix.outputs.matrix', job['outputs']['matrix'])


if __name__ == '__main__':
    unittest.main(verbosity=2)

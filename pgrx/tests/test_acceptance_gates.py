"""Execute the workflow gates so skipped or missing acceptance cannot look green."""
import json
import os
from pathlib import Path
import subprocess
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]


def workflow(name):
    return yaml.safe_load((ROOT / '.github/workflows' / name).read_text())


def run_gate(job, **values):
    step = next(step for step in job['steps'] if 'RESULTS' in step.get('env', {}) or 'MATRIX' in step.get('env', {}))
    return subprocess.run(
        ['bash', '-e', '-o', 'pipefail', '-c', step['run']],
        env={**os.environ, **values}, capture_output=True, text=True,
    ).returncode


class AcceptanceGatesTest(unittest.TestCase):
    def test_reporting_is_not_path_filtered(self):
        for filename in ['bake.yml', 'pgrx.yml']:
            with self.subTest(workflow=filename):
                doc = workflow(filename)
                triggers = doc.get('on', doc.get(True))
                for event in ['pull_request', 'merge_group']:
                    self.assertIn(event, triggers)
                    self.assertFalse(triggers[event])
                self.assertEqual(triggers['push'], {'branches': ['main']})

    def test_outer_gates_require_selected_builds(self):
        for filename, gate_id in [('bake.yml', 'automerge-gate'), ('pgrx.yml', 'gate')]:
            gate = workflow(filename)['jobs'][gate_id]
            self.assertEqual(gate['if'], '${{ always() }}')
            for matrix in [[], ['example-extension']]:
                for result in ['success', 'skipped', 'failure', 'cancelled', '']:
                    with self.subTest(workflow=filename, matrix=matrix, result=result):
                        rc = run_gate(gate, DISCOVERY='success', CONTRACTS='success', MATRIX=json.dumps(matrix), BUILDS=result)
                        self.assertEqual(rc == 0, result == ('success' if matrix else 'skipped'))
            for discovery in ['failure', 'cancelled', 'skipped', '']:
                self.assertNotEqual(run_gate(gate, DISCOVERY=discovery, CONTRACTS='success', MATRIX='[]', BUILDS='skipped'), 0)
            for matrix in ['', 'null', '{}', '[null]', '[""]']:
                self.assertNotEqual(run_gate(gate, DISCOVERY='success', CONTRACTS='success', MATRIX=matrix, BUILDS='success'), 0)

    def test_contracts_are_part_of_pgrx_acceptance(self):
        jobs = workflow('pgrx.yml')['jobs']
        self.assertEqual(jobs['gate']['name'], 'PGRX acceptance')
        self.assertEqual(set(jobs['gate']['needs']), {'discover', 'contracts', 'build'})
        self.assertEqual(jobs['contracts']['uses'], './.github/workflows/pgrx-tests.yml')
        triggers = workflow('pgrx-tests.yml')
        self.assertIn('workflow_call', triggers.get('on', triggers.get(True)))
        for result in ['failure', 'cancelled', 'skipped', '']:
            self.assertNotEqual(run_gate(jobs['gate'], DISCOVERY='success', CONTRACTS=result, MATRIX='[]', BUILDS='skipped'), 0)

    def test_every_release_job_is_required(self):
        # An added upstream job must prompt an explicit acceptance review.
        for filename, promotion_jobs in [
            ('bake_targets.yml', {'copytoproduction', 'production-provenance'}),
            ('pgrx_targets.yml', {'promote', 'production-provenance'}),
        ]:
            jobs = workflow(filename)['jobs']
            gate = jobs['gate']
            self.assertEqual(set(gate['needs']), set(jobs) - {'gate'}, filename)
            self.assertEqual(gate['if'], '${{ always() }}')
            for promotion in [False, True]:
                results = {name: {'result': 'skipped' if name in promotion_jobs and not promotion else 'success'} for name in gate['needs']}
                values = {'PROMOTION_ALLOWED': str(promotion).lower(), 'RESULTS': json.dumps(results)}
                self.assertEqual(run_gate(gate, **values), 0, filename)
                for name in gate['needs']:
                    for result in ['failure', 'cancelled', 'skipped']:
                        if result == 'skipped' and name in promotion_jobs and not promotion:
                            continue
                        with self.subTest(workflow=filename, promotion=promotion, job=name, result=result):
                            broken = {**results, name: {'result': result}}
                            self.assertNotEqual(run_gate(gate, **{**values, 'RESULTS': json.dumps(broken)}), 0)

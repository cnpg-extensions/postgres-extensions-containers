"""Exercise the shared workflow's Task commands with selected release inputs."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]


class SmokeWorkflowTest(unittest.TestCase):
    def test_selected_release_and_image_reach_shared_tasks(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/smoke.yml').read_text())
        steps = workflow['jobs']['smoke']['steps']
        steps = [step for step in steps if step['name'] in (
            'Set up environment', 'Generate Chainsaw testing values', 'Run e2e tests',
        )]
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            log = directory / 'calls.jsonl'
            task = directory / 'task'
            task.write_text(
                f'#!{sys.executable}\n'
                'import json, os, sys\n'
                'with open(os.environ["TASK_LOG"], "a") as output:\n'
                '    output.write(json.dumps(sys.argv[1:]) + "\\n")\n'
            )
            task.chmod(0o755)
            image = 'ghcr.io/example/pg-session-jwt-testing@sha256:' + 'a' * 64
            for selected in ['main', '1.29.3', '1.30.1']:
                with self.subTest(selected=selected):
                    log.unlink(missing_ok=True)
                    inputs = {'cnpg_version': selected, 'extension_name': 'pg-session-jwt', 'image': image}
                    for step in steps:
                        environment = {
                            **os.environ,
                            'PATH': str(directory) + os.pathsep + os.environ['PATH'],
                            'TASK_LOG': str(log),
                        }
                        for name, expression in step.get('env', {}).items():
                            key = expression.removeprefix('${{ inputs.').removesuffix(' }}')
                            environment[name] = inputs[key]
                        subprocess.run(['bash', '-euo', 'pipefail', '-c', step['run']], cwd=directory, env=environment, check=True)
                    calls = [json.loads(line) for line in log.read_text().splitlines()]
                    self.assertEqual(calls, [
                        ['e2e:setup-env', 'CNPG_RELEASE=' + selected],
                        ['e2e:generate-values', 'EXTENSION_IMAGE=' + image, 'TARGET=pg-session-jwt'],
                        ['e2e:export-kubeconfig', 'KUBECONFIG_PATH=./kubeconfig', 'INTERNAL=true'],
                        ['e2e:test', 'TARGET=pg-session-jwt', 'KUBECONFIG_PATH=./kubeconfig'],
                    ])

"""Check PGRX routes shared policy versions into the standard smoke setup."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from smoke import smoke


class SmokeSetupTest(unittest.TestCase):
    def test_smoke_passes_selected_release_to_shared_setup(self):
        class StopBeforeSetup(Exception):
            pass
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = root / 'pgrx/dependencies'
            pins.mkdir(parents=True)
            kind = root / 'kind'
            (pins / 'workflow-tools.json').write_text(json.dumps({
                'images': {'runner': 'pinned-runner', 'dagger': 'pinned-dagger'},
            }))
            for selected in ['main', '1.29.3', '1.30.1']:
                with self.subTest(selected=selected), patch('smoke.ROOT', root), patch('smoke.shutil.which', return_value=str(kind)), patch('smoke.subprocess.Popen', side_effect=StopBeforeSetup) as launch:
                    with self.assertRaises(StopBeforeSetup):
                        smoke({'inputs': {}, 'targets': {'target': {'pg_major': '18'}}}, {'target': 'target'}, root / 'out', selected)
                    command = launch.call_args.args[0]
                    self.assertEqual(command[:2], ['task', 'e2e:setup-env'])
                    self.assertIn('CNPG_RELEASE=' + selected, command)

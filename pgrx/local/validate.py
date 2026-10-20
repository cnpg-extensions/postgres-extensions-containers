#!/usr/bin/env python3
"""Run local checks once; image builds and signing run in hosted workflows."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'pgrx'))
from local.renovate import check_renovate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renovate-output', type=Path,
                        help='Also run the pinned Renovate checks; requires Docker')
    args = parser.parse_args()
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s',
                    'sbom-generator/tests', '-p', 'test_*.py'], cwd=ROOT, check=True)
    subprocess.run([sys.executable, 'pgrx/test.py'], cwd=ROOT, check=True)
    module_file = ROOT / 'dagger/maintenance/dagger.json'
    module_bytes = module_file.read_bytes()
    try:
        subprocess.run(['dagger', 'develop', '-m', './dagger/maintenance'], cwd=ROOT, check=True)
    finally:
        module_file.write_bytes(module_bytes)
    subprocess.run(['go', 'test', './...'], cwd=ROOT / 'dagger/maintenance',
                   env={**os.environ, 'DAGGER_SESSION_PORT': '1', 'DAGGER_SESSION_TOKEN': 'test'}, check=True)
    subprocess.run(['actionlint', '.github/workflows/sbom-generator.yml',
                    '.github/workflows/pgrx.yml', '.github/workflows/pgrx_targets.yml',
                    '.github/workflows/test.yml'], cwd=ROOT, check=True)
    subprocess.run([sys.executable, 'pgrx/refresh_lock.py', '--check'], cwd=ROOT, check=True)
    if args.renovate_output:
        pins = json.loads((ROOT / 'pgrx/dependencies/workflow-tools.json').read_text())
        check_renovate(args.renovate_output, pins)


if __name__ == '__main__':
    main()

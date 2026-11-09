#!/usr/bin/env python3
"""Run PGRX tests and workflow lint, with optional Renovate checks."""
import argparse
import json
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
    subprocess.run([sys.executable, 'pgrx/test.py'], cwd=ROOT, check=True)
    subprocess.run(['actionlint', '.github/workflows/pgrx.yml',
                    '.github/workflows/pgrx_targets.yml', '.github/workflows/pgrx-tests.yml',
                    '.github/workflows/cnpg-versions.yml'], cwd=ROOT, check=True)
    if args.renovate_output:
        pins = json.loads((ROOT / 'pgrx/dependencies/workflow-tools.json').read_text())
        check_renovate(args.renovate_output, pins['images']['renovate'])


if __name__ == '__main__':
    main()

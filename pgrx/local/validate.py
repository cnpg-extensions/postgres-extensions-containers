#!/usr/bin/env python3
"""Run PGRX tests and workflow lint."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    subprocess.run([sys.executable, 'pgrx/test.py'], cwd=ROOT, check=True)
    subprocess.run(['actionlint', '.github/workflows/pgrx.yml',
                    '.github/workflows/pgrx_targets.yml', '.github/workflows/pgrx-tests.yml',
                    '.github/workflows/cnpg-versions.yml'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()

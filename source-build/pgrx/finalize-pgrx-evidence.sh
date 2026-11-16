#!/usr/bin/env bash
# Evidence is finalized after packaging, so its hashes describe copied artifacts.
set -Eeuo pipefail
exec python3 /source-build/pgrx/evidence.py

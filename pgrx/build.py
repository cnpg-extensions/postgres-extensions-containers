#!/usr/bin/env python3
"""Check the local docker-container builder before the workflow runs Bake."""

import argparse
import platform
import subprocess


# The workflow uses Debian's Docker login, Buildx setup and Bake actions, but
# runs each platform on native hardware. Require the runner, daemon and worker
# to match before Bake starts; QEMU is not installed by the PGRX workflow.
def check_native(architecture, builder):
    aliases = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}
    host = aliases.get(platform.machine())
    daemon = subprocess.check_output(
        ["docker", "info", "--format", "{{.Architecture}}"], text=True
    ).strip()
    # setup-buildx-action creates one local docker-container node. Inspect that
    # exact worker, rather than trusting its advertised (possibly emulated) platforms.
    worker = subprocess.check_output(
        ["docker", "exec", "buildx_buildkit_" + builder + "0", "uname", "-m"],
        text=True,
    ).strip()
    if any(value != architecture for value in (host, aliases.get(daemon), aliases.get(worker))):
        raise ValueError("runner, Docker daemon and BuildKit worker must match " + architecture)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--architecture", choices=("amd64", "arm64"), required=True)
    parser.add_argument("--builder", required=True)
    args = parser.parse_args()
    check_native(args.architecture, args.builder)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Resolve both architectures using native amd64 apt, never ARM execution.

The ARM installed set is copied from the locked base filesystem without running it.
APT's signed indexes supply full control records and SHA256 download hashes.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from workflow import ROOT

PACKAGES = [
    "build-essential",
    "ca-certificates",
    "clang",
    "cmake",
    "curl",
    "git",
    "jq",
    "libclang-dev",
    "libssl-dev",
    "pkg-config",
    "python3",
    "postgresql-server-dev-18",
    "xz-utils",
    "patch",
    "libopenblas-dev",
]


def refresh_apt(suites=("bookworm", "trixie")):
    root = ROOT / "pgrx/dependencies"
    bases = json.loads((root / "bases.json").read_text())
    with tempfile.TemporaryDirectory(prefix="pgrx-apt-refresh-") as temporary:
        temp = Path(temporary)
        for suite in suites:
            reference = "ghcr.io/cloudnative-pg/postgresql:18-minimal-" + suite
            base = bases[reference]
            for architecture in ["amd64", "arm64"]:
                image = reference + "@" + base["platforms"]["linux/amd64"]
                container = subprocess.check_output(
                    [
                        "docker",
                        "run",
                        "-d",
                        "--platform",
                        "linux/amd64",
                        "--user",
                        "0",
                        image,
                        "sleep",
                        "900",
                    ],
                    text=True,
                ).strip()
                try:
                    prefix = ""
                    if architecture == "arm64":
                        # Use the exact installed control records, even when
                        # those versions have disappeared from current indexes.
                        arm_image = reference + "@" + base["platforms"]["linux/arm64"]
                        arm_container = subprocess.check_output(
                            [
                                "docker",
                                "create",
                                "--platform",
                                "linux/arm64",
                                "--entrypoint",
                                "/bin/true",
                                arm_image,
                            ],
                            text=True,
                        ).strip()
                        installed = temp / "arm-status"
                        try:
                            subprocess.run(
                                [
                                    "docker",
                                    "cp",
                                    arm_container + ":/var/lib/dpkg/status",
                                    str(installed),
                                ],
                                check=True,
                            )
                        finally:
                            subprocess.run(
                                ["docker", "rm", arm_container],
                                check=True,
                                stdout=subprocess.DEVNULL,
                            )
                        subprocess.run(
                            [
                                "docker",
                                "cp",
                                str(installed),
                                container + ":/tmp/arm-status",
                            ],
                            check=True,
                        )
                        prefix = "sed -i 's/amd64/arm64/g' /etc/apt/sources.list.d/*\n"
                    options = (
                        "-o APT::Architecture="
                        + architecture
                        + " -o APT::Architectures="
                        + architecture
                    )
                    script = (
                        "set -Eeuo pipefail\n"
                        + prefix
                        + "apt-get "
                        + options
                        + " update >&2\n"
                    )
                    if architecture == "arm64":
                        options += " -o Dir::State::status=/tmp/arm-status"
                    script += (
                        "apt-get "
                        + options
                        + " -o Acquire::ForceHash=sha256 --print-uris --yes --download-only install "
                        + " ".join(PACKAGES)
                        + "\n"
                    )
                    raw = subprocess.check_output(
                        ["docker", "exec", container, "bash", "-c", script], text=True
                    )
                    rows = []
                    for line in raw.splitlines():
                        match = re.fullmatch(
                            r"'([^']+)' (\S+) \d+ SHA256:([a-f0-9]{64})", line
                        )
                        if match:
                            rows.append((match[3], match[2], match[1]))
                    if not rows:
                        raise ValueError("apt returned no locked package artifacts")
                    (root / "apt" / f"{suite}-{architecture}.tsv").write_text(
                        "".join(
                            "\t".join(row) + "\n"
                            for row in sorted(rows, key=lambda r: r[1])
                        )
                    )
                finally:
                    subprocess.run(
                        ["docker", "rm", "-f", container],
                        check=True,
                        stdout=subprocess.DEVNULL,
                    )
    write_ownership()


def write_ownership():
    root = ROOT / "pgrx/dependencies"
    lock = {
        "schema_version": 1,
        "base_lock_sha256": hashlib.sha256(
            (root / "bases.json").read_bytes()
        ).hexdigest(),
        "packages": PACKAGES,
        "files": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((root / "apt").glob("*.tsv"))
        },
    }
    (root / "apt/lock.json").write_text(json.dumps(lock, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--distro",
        nargs="+",
        choices=["bookworm", "trixie"],
        default=["bookworm", "trixie"],
    )
    refresh_apt(parser.parse_args().distro)

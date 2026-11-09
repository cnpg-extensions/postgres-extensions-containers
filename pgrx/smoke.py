"""CNPG smoke through shared Task/Dagger infrastructure, using the assembled digest."""

import json
import re
from pathlib import Path
import shutil
import subprocess
import sys

from workflow import ROOT


def smoke(preparation, assembly, output, selector=None):
    requested = selector or preparation["inputs"].get("cnpg_version")
    if not requested or not re.fullmatch(r"main|[0-9]+\.[0-9]+\.[0-9]+", requested):
        raise ValueError("CNPG version must be main or a full version like 1.30.1")
    target = preparation["targets"][assembly["target"]]
    if target["pg_major"] != "18":
        raise ValueError("CNPG smoke currently supports PG18 only")
    pins = json.loads((ROOT / "pgrx/dependencies/workflow-tools.json").read_text())
    # Reuse the shared tasks with a pinned toolbox and a separate test engine.
    kind = Path(shutil.which("kind")).resolve()
    toolbox = (
        "dagger core container from --address="
        + pins["images"]["runner"]
        + " with-file --path=/usr/local/bin/kind --source="
        + str(kind)
        + " with-unix-socket --path=/var/run/docker.sock --source=/var/run/docker.sock"
        + " with-env-variable --name=DOCKER_HOST --value=unix:///var/run/docker.sock"
        + " with-env-variable --name=KIND_EXPERIMENTAL_DOCKER_NETWORK --value=pg-extensions-e2e"
    )
    overrides = [
        "CNPG_RELEASE=" + requested,
        "KIND_TOOLBOX=" + toolbox,
        "KIND_CLUSTER_NAME=pgrx-smoke",
        "KIND_KUBECONFIG_FILTER=python3 "
        + str(ROOT / "pgrx/local/kubeconfig.py")
        + " pgrx-smoke",
        "DAGGER_ENGINE_NAME=dagger-engine-pgrx-smoke",
        "DAGGER_ENGINE_IMAGE_OVERRIDE=" + pins["images"]["dagger"],
    ]

    def task(name, *arguments):
        command = ["task", name, *overrides, *arguments]
        # Shared tasks pass kubeconfig through Dagger; suppress credential-bearing
        # progress lines before they reach act logs or retained validation artifacts.
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        for line in process.stdout:
            if "client-key-data" in line or "client-certificate-data" in line:
                continue
            sys.stdout.write(line)
            sys.stdout.flush()
        if process.wait():
            raise subprocess.CalledProcessError(process.returncode, command)

    task("e2e:setup-env")
    kubeconfig = output / "kubeconfig"
    task("e2e:export-kubeconfig", "KUBECONFIG_PATH=" + str(kubeconfig), "INTERNAL=true")
    try:
        task(
            "e2e:generate-values",
            "TARGET=" + preparation["extension"],
            "EXTENSION_IMAGE=" + assembly["image"],
        )
        task(
            "e2e:test",
            "TARGET=" + preparation["extension"],
            "KUBECONFIG_PATH=" + str(kubeconfig),
        )
        (output / "cnpg-version.txt").write_text(requested + "\n")
    finally:
        kubeconfig.unlink(missing_ok=True)

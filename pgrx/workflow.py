#!/usr/bin/env python3
"""Hosted workflow selection and source identity."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def execute(command, *, root=ROOT, env=None):
    return subprocess.run(
        command, cwd=root, env=env, check=True, capture_output=True, text=True
    ).stdout


def metadata(path):
    definition = json.loads(
        execute(
            [
                "docker",
                "buildx",
                "bake",
                "-f",
                str(path),
                "-f",
                str(ROOT / "pgrx/inventory.hcl"),
                "--print",
                "inventory",
            ]
        )
    )
    value = json.loads(definition["target"]["inventory"]["args"]["METADATA"])
    system = value.get("build_system", "debian")
    if system not in ("debian", "pgrx"):
        raise ValueError(f"unsupported build_system: {system!r}")
    return value


def discover():
    return {
        p.parent.name: value
        for p in sorted(ROOT.glob("*/metadata.hcl"))
        if (value := metadata(p)).get("build_system", "debian") == "pgrx"
    }


def source_digest(root=ROOT):
    paths = execute(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        root=root,
    ).split("\0")
    digest = hashlib.sha256()
    for name in sorted(set(paths) - {""}):
        if Path(name).name == "AGENTS.md":
            continue
        path = root / name
        if not path.exists() and not path.is_symlink():
            continue
        data = os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
        digest.update(
            name.encode()
            + b"\0"
            + str(path.lstat().st_mode & 0o777).encode()
            + b"\0"
            + hashlib.sha256(data).digest()
        )
    return digest.hexdigest()


def select(inputs, inventory):
    extension = inputs["extension_name"]
    if extension not in inventory:
        raise ValueError(f"not a PGRX extension: {extension}")
    return ["linux/amd64", "linux/arm64"]


def changed_extensions(paths, inventory):
    shared = (
        "pgrx/",
        "docker-bake.hcl",
        "docker-bake-pgrx.hcl",
        "scripts/",
        "test/",
        ".github/workflows/pgrx.yml",
        ".github/workflows/pgrx_targets.yml",
        "dagger/maintenance/",
        "Taskfile.yml",
    )
    if any(any(p.startswith(prefix) for prefix in shared) for p in paths):
        return sorted(inventory)
    return sorted({p.split("/")[0] for p in paths} & set(inventory))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path)
    parser.add_argument("--changed-paths", type=Path)
    args = parser.parse_args()
    inventory = discover()
    if args.inputs:
        inputs = json.loads(args.inputs.read_text())
        select(inputs, inventory)
        result = [inputs["extension_name"]]
    elif args.changed_paths:
        result = changed_extensions(
            args.changed_paths.read_text().splitlines(), inventory
        )
    else:
        result = sorted(inventory)
    print(json.dumps(result))


if __name__ == "__main__":
    main()

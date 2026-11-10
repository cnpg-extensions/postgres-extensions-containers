#!/usr/bin/env python3
"""Metadata discovery and platform selection for native build preparation."""

import json
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


def select(inputs, inventory):
    extension = inputs["extension_name"]
    if extension not in inventory:
        raise ValueError(f"not a PGRX extension: {extension}")
    return ["linux/amd64", "linux/arm64"]

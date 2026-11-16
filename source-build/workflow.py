#!/usr/bin/env python3
"""Metadata discovery and platform selection for native source builds."""

import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def execute(command, *, root=ROOT, env=None):
    return subprocess.run(command, cwd=root, env=env, check=True,
                          capture_output=True, text=True).stdout


def metadata(path):
    definition = json.loads(execute([
        "docker", "buildx", "bake", "-f", str(path), "-f",
        str(ROOT / "source-build/inventory.hcl"), "--print", "inventory",
    ]))
    return json.loads(definition["target"]["inventory"]["args"]["METADATA"])


def discover(root=None):
    root = Path(root or ROOT)
    inventory = {}
    # Explicit depths exclude infrastructure, fixtures and templates. Location,
    # never the retained legacy build_system field, determines the build family.
    for pattern, family in (("*/metadata.hcl", "debian"),
                            ("pgrx/*/metadata.hcl", "pgrx"),
                            ("universe/*/metadata.hcl", "universe")):
        for path in sorted(root.glob(pattern)):
            value = metadata(path)
            name = value["name"]
            if name != path.parent.name:
                raise ValueError(f"recipe name {name!r} must match {path.parent.name!r}")
            if name in inventory:
                raise ValueError(f"duplicate logical extension name: {name}")
            inventory[name] = {**value, "build_family": family,
                               "recipe_path": path.parent.relative_to(root).as_posix()}
    return inventory


def select(inputs, inventory):
    extension = inputs["extension_name"]
    family = inputs.get("build_family", "pgrx")
    if family not in ("pgrx", "universe"):
        raise ValueError(f"unsupported source build family: {family}")
    if extension not in inventory or inventory[extension]["build_family"] != family:
        raise ValueError(f"extension {extension!r} is not in the {family} recipe root")
    versions = inventory[extension].get("versions", {})
    if not versions or any(d not in ("bookworm", "trixie") or not majors
                           or any(pg != "18" for pg in majors)
                           for d, majors in versions.items()):
        raise ValueError("source recipe declares an unsupported distribution/PG target")
    return ["linux/amd64", "linux/arm64"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", action="store_true", required=True)
    args = parser.parse_args()
    print(json.dumps({name: value for name, value in discover().items()
                      if value["build_family"] in ("pgrx", "universe")}))

#!/usr/bin/env python3
"""Prepare native Bake targets and their assembly plan."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from source import resolve_source
from workflow import discover, execute, select


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def save(path, value):
    path.write_bytes(encoded(value) + b"\n")


def inspect_base_index(reference):
    return json.loads(
        subprocess.check_output(
            [
                "docker",
                "buildx",
                "imagetools",
                "inspect",
                reference,
                "--format",
                "{{json .Manifest}}",
            ],
            text=True,
        )
    )


def platform_base(reference, platform, manifests=None):
    if platform not in ("linux/amd64", "linux/arm64"):
        raise ValueError("unsupported base platform: " + platform)
    if manifests is None:
        manifest = inspect_base_index(reference)
    else:
        manifest = manifests.get(reference)
        if manifest is None:
            manifest = inspect_base_index(reference)
            manifests[reference] = manifest
    index_digest = manifest.get("digest")
    if not isinstance(index_digest, str) or not re.fullmatch(
        r"sha256:[a-f0-9]{64}", index_digest
    ):
        raise ValueError("base image index digest is invalid")
    os_name, architecture = platform.split("/", 1)
    children = [
        descriptor
        for descriptor in manifest.get("manifests", [])
        if descriptor.get("platform", {}).get("os") == os_name
        and descriptor.get("platform", {}).get("architecture") == architecture
    ]
    if len(children) != 1:
        raise ValueError("base image index must contain one " + platform + " image")
    child_digest = children[0].get("digest")
    if not isinstance(child_digest, str) or not re.fullmatch(
        r"sha256:[a-f0-9]{64}", child_digest
    ):
        raise ValueError("base platform digest is invalid")
    return reference + "@" + child_digest, index_digest


# Render the shared Debian Bake configuration with the PGRX overlay once per
# run, selecting one timestamp, source revision and architecture-specific base
# image for each build. Each target/platform row selects a matching native runner.
# Source tags resolve to repository revisions and archive URLs here. The native
# build downloads from upstream HTTPS and records the actual archive hash; there
# is no preparation-time archive checksum comparison or separate committed lock.
def prepare(inputs, generator, output):
    if not re.fullmatch(r"[^\s]+@sha256:[a-f0-9]{64}", generator):
        raise ValueError("digest-qualified generator required")
    inventory = discover()
    platforms = select(inputs, inventory)
    extension = inputs["extension_name"]
    repository_url = inventory[extension].get("source_repository")
    if not repository_url:
        raise ValueError("selected extension has no source_repository metadata")
    base_manifests = {}
    sources = {}
    if output.exists():
        raise ValueError("fresh preparation directory required")
    output.mkdir(parents=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    registry = "ghcr.io/" + os.environ["GITHUB_REPOSITORY_OWNER"].lower()
    environment = {
        **os.environ,
        "environment": "testing",
        "sbom_generator": generator,
        "build_timestamp": timestamp,
        "registry": registry,
        "revision": execute(["git", "rev-parse", "HEAD"]).strip(),
    }
    definition = json.loads(
        execute(
            [
                "docker",
                "buildx",
                "bake",
                "-f",
                "docker-bake.hcl",
                "-f",
                "docker-bake-pgrx.hcl",
                "-f",
                extension + "/metadata.hcl",
                "--print",
            ],
            env=environment,
        )
    )
    targets = definition["target"]
    run_id = (
        os.environ["GITHUB_RUN_ID"] + "-" + os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    )
    result = {
        "schema_version": 1,
        "extension": extension,
        "platforms": platforms,
        "targets": {},
        "rows": [],
    }
    for name, original in sorted(targets.items()):
        version = original["args"]["EXT_VERSION"]
        if version not in sources:
            sources[version] = resolve_source(repository_url, version)
        source = sources[version]
        distro = next(
            a.split("=", 1)[1]
            for a in original["annotations"]
            if ":io.cloudnativepg.image.base.os=" in a
        )
        result["targets"][name] = {
            "tags": original["tags"],
        }
        for platform in platforms:
            architecture = platform.split("/")[1]
            row_id = hashlib.sha256(
                (run_id + "\0" + name + "\0" + platform).encode()
            ).hexdigest()[:32]
            staging = (
                registry
                + "/"
                + inventory[extension]["image_name"]
                + "-testing:stage-"
                + row_id
            )
            base, _ = platform_base(
                original["args"]["BASE"],
                platform,
                manifests=base_manifests,
            )
            frozen = json.loads(json.dumps(original))
            frozen["platforms"] = [platform]
            frozen["tags"] = [staging]
            frozen["args"].update(
                BASE=base,
                PGRX_EXTENSION=extension,
                PGRX_DISTRO=distro,
                PGRX_SOURCE_REPOSITORY=repository_url,
                PGRX_SOURCE_REVISION=source["revision"],
                PGRX_BUILD_TIMESTAMP=timestamp,
            )
            frozen["output"] = [
                "type=image,oci-mediatypes=true,oci-artifact=true,push=true"
            ]
            single = {"target": {name: frozen}}
            row = {
                "id": row_id,
                "target": name,
                "platform": platform,
                "architecture": architecture,
                "runner": (
                    "ubuntu-24.04" if architecture == "amd64" else "ubuntu-24.04-arm"
                ),
                "staging": staging,
            }
            result["rows"].append(row)
            save(output / (row_id + ".json"), single)
    save(output / "preparation.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", required=True, type=Path)
    parser.add_argument("--generator", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = prepare(json.loads(args.inputs.read_text()), args.generator, args.output)
    matrix = {
        "include": [
            {k: r[k] for k in ("id", "target", "platform", "architecture", "runner")}
            for r in result["rows"]
        ]
    }
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            output.write("matrix=" + json.dumps(matrix) + "\n")
    print(json.dumps(matrix))


if __name__ == "__main__":
    main()

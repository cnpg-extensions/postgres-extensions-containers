#!/usr/bin/env python3
"""Freeze one logical run into independently checkable platform definitions."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from source import resolve_source
from workflow import ROOT, discover, execute, select, source_digest


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


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
    workspace = source_digest()
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
        "inputs": inputs,
        "platforms": platforms,
        "timestamp": timestamp,
        "workspace_sha256": workspace,
        "git_sha": environment["revision"],
        "generator": generator,
        "run_id": run_id,
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
            "distro": distro,
            "pg_major": original["args"]["PG_MAJOR"],
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
            base, base_index = platform_base(
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
                PGRX_WORKSPACE_SHA256=workspace,
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
                "definition_sha256": digest(single),
                "staging": staging,
                "base": base,
                "base_index": base_index,
                "source": source,
            }
            result["rows"].append(row)
            save(output / (row_id + ".json"), single)
    result["preparation_sha256"] = digest(result)
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
            output.write(
                "matrix="
                + json.dumps(matrix)
                + "\n"
                + "targets="
                + json.dumps({"include": [{"target": t} for t in result["targets"]]})
                + "\n"
            )
    print(json.dumps(matrix))


if __name__ == "__main__":
    main()

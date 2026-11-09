#!/usr/bin/env python3
"""Merge complete staging indexes without changing their image or predicate bytes."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from prepare import save
from record import load_preparation, validate_record
from registry import wait_for_index_digest


def check_assembly(index, sources, platforms):
    """Keep every native image and its attached attestations in the merged index."""
    descriptors = index["manifests"]
    expected = [d for source in sources for d in source["manifests"]]
    if sorted(descriptors, key=lambda d: d["digest"]) != sorted(
        expected, key=lambda d: d["digest"]
    ):
        raise ValueError("published merge changed descriptors")
    children, attestations = {}, []
    for descriptor in descriptors:
        platform = descriptor.get("platform", {})
        if (
            descriptor.get("annotations", {}).get("vnd.docker.reference.type")
            == "attestation-manifest"
        ):
            attestations.append(descriptor)
            continue
        name = platform.get("os", "") + "/" + platform.get("architecture", "")
        if name not in platforms or name in children:
            raise ValueError("unexpected or duplicate platform")
        children[name] = descriptor["digest"]
    if set(children) != set(platforms):
        raise ValueError("missing expected platform")
    subjects = [
        d["annotations"].get("vnd.docker.reference.digest") for d in attestations
    ]
    if sorted(subjects, key=str) != sorted(children.values()):
        raise ValueError("missing, duplicate or unexpected platform attestation")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preparation", type=Path, required=True)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    preparation = load_preparation(args.preparation)
    expected = {
        "platform-" + preparation["extension"] + "-" + r["id"]
        for r in preparation["rows"]
    }
    if {p.name for p in args.records.iterdir()} != expected:
        raise ValueError("missing, duplicate or unexpected platform artifacts")
    if args.output.exists():
        raise ValueError("fresh assembly directory required")
    args.output.mkdir(parents=True)
    for target, settings in preparation["targets"].items():
        rows = [r for r in preparation["rows"] if r["target"] == target]
        records = [
            validate_record(
                preparation,
                r,
                args.records / ("platform-" + preparation["extension"] + "-" + r["id"]),
            )
            for r in rows
        ]
        output = args.output / target
        output.mkdir()
        repository = rows[0]["staging"].rsplit(":", 1)[0]
        candidate = (
            repository
            + ":candidate-"
            + hashlib.sha256((preparation["run_id"] + target).encode()).hexdigest()[:32]
        )
        definitions = json.loads(
            (args.preparation / (rows[0]["id"] + ".json")).read_text()
        )["target"][target]
        annotations = []
        for annotation in definitions["annotations"]:
            scope, content = annotation.split(":", 1)
            if "index" in scope.split(","):
                annotations += ["--annotation", "index:" + content]
        references = [r["image"] for r in records]
        command = [
            "docker",
            "buildx",
            "imagetools",
            "create",
            *annotations,
            "--tag",
            candidate,
            *references,
        ]
        sources = [
            json.loads(
                subprocess.check_output(
                    ["docker", "buildx", "imagetools", "inspect", reference, "--raw"]
                )
            )
            for reference in references
        ]
        subprocess.run(command, check=True)
        raw = subprocess.check_output(
            ["docker", "buildx", "imagetools", "inspect", candidate, "--raw"]
        )
        index_digest = "sha256:" + hashlib.sha256(raw).hexdigest()
        image = repository + "@" + index_digest
        check_assembly(json.loads(raw), sources, preparation["platforms"])
        # Publish normal tags only after checking the merged platform inventory.
        for tag in settings["tags"]:
            subprocess.run(
                ["docker", "buildx", "imagetools", "create", "--tag", tag, image],
                check=True,
            )
            wait_for_index_digest(tag, index_digest)
        save(
            output / "assembly.json",
            {
                "schema_version": 1,
                "target": target,
                "extension": preparation["extension"],
                "preparation_sha256": preparation["preparation_sha256"],
                "run_id": preparation["run_id"],
                "image": image,
                "index_digest": index_digest,
                "platforms": preparation["platforms"],
                "tags": settings["tags"],
            },
        )
        save(
            output / "metadata.json",
            {
                target: {
                    "image.name": ",".join(settings["tags"]),
                    "containerimage.digest": index_digest,
                }
            },
        )


if __name__ == "__main__":
    main()

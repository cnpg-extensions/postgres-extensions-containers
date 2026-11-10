#!/usr/bin/env python3
"""Merge complete staging indexes without changing their image or predicate bytes."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

from prepare import save


def wait_for_index_digest(reference, expected_digest, attempts=6):
    """Allow registry tag visibility to catch up after a successful push."""
    for attempt in range(attempts):
        try:
            raw = subprocess.check_output(
                ["docker", "buildx", "imagetools", "inspect", reference, "--raw"]
            )
        except subprocess.CalledProcessError:
            if attempt == attempts - 1:
                raise
        else:
            actual = "sha256:" + hashlib.sha256(raw).hexdigest()
            if actual == expected_digest:
                return
            if attempt == attempts - 1:
                raise ValueError(
                    f"registry index digest mismatch for {reference}: "
                    f"expected {expected_digest}, got {actual}"
                )
        time.sleep(2)


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


# Platform jobs hand off ordinary Bake metadata: target, staging name and
# immutable digest. Reject missing/unexpected artifacts, then merge complete
# staging indexes without changing image or attestation descriptors. Check both
# platforms and their attestations before assigning normal tags, and read back
# those tags until the exact index digest matches; stale tags are never accepted.
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preparation", type=Path, required=True)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    preparation = json.loads((args.preparation / "preparation.json").read_text())
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
        references = []
        for row in rows:
            artifact = args.records / (
                "platform-" + preparation["extension"] + "-" + row["id"]
            )
            metadata = json.loads((artifact / "metadata.json").read_text())
            if set(metadata) != {target}:
                raise ValueError("unexpected build target in platform metadata")
            result = metadata[target]
            if result["image.name"] != row["staging"]:
                raise ValueError("unexpected staging image in platform metadata")
            digest = result["containerimage.digest"]
            if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
                raise ValueError("invalid build digest")
            references.append(row["staging"].rsplit(":", 1)[0] + "@" + digest)
        output = args.output / target
        output.mkdir()
        repository = rows[0]["staging"].rsplit(":", 1)[0]
        candidate = repository + ":candidate-" + rows[0]["id"]
        definitions = json.loads(
            (args.preparation / (rows[0]["id"] + ".json")).read_text()
        )["target"][target]
        annotations = []
        for annotation in definitions["annotations"]:
            scope, content = annotation.split(":", 1)
            if "index" in scope.split(","):
                annotations += ["--annotation", "index:" + content]
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

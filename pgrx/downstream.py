#!/usr/bin/env python3
"""Shared signing, scanning and promotion steps for each assembled target."""

import argparse
import json
import os
from pathlib import Path
import subprocess

from prepare import save
from record import load_preparation
from registry import wait_for_index_digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["sign", "security", "smoke", "promote"])
    parser.add_argument("--preparation", required=True, type=Path)
    parser.add_argument("--assembly", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cnpg-version")
    args = parser.parse_args()
    preparation = load_preparation(args.preparation)
    assembly = json.loads((args.assembly / "assembly.json").read_text())
    if (
        assembly["preparation_sha256"] != preparation["preparation_sha256"]
        or assembly["target"] not in preparation["targets"]
        or assembly["run_id"] != preparation["run_id"]
    ):
        raise ValueError("wrong assembly artifact")
    image = assembly["image"]
    if args.output.exists():
        raise ValueError("fresh downstream output required")
    args.output.mkdir(parents=True)

    def sign(reference):
        subprocess.run(
            [
                "cosign",
                "sign",
                "--yes",
                "--new-bundle-format=false",
                "--use-signing-config=false",
                reference,
            ],
            check=True,
        )

    if args.stage == "sign":
        sign(image)
    elif args.stage == "security":
        sboms = json.loads(
            subprocess.check_output(
                ["docker", "buildx", "imagetools", "inspect", image,
                 "--format", "{{json .SBOM}}"]
            )
        )
        for platform in assembly["platforms"]:
            output = args.output / platform.split("/")[1]
            document = sboms.get(platform, {}).get("SPDX")
            if (
                not isinstance(document, dict)
                or document.get("spdxVersion") != "SPDX-2.3"
            ):
                raise ValueError("missing SPDX document for " + platform)
            output.mkdir()
            save(output / "sbom.spdx.json", document)
            for tool in ("grype", "grant"):
                command = (
                    ["grype", "sbom:" + str(output / "sbom.spdx.json"), "-o", "json"]
                    if tool == "grype"
                    else ["grant", "list", str(output / "sbom.spdx.json"), "-o", "json"]
                )
                with (output / (tool + ".json")).open("w") as report:
                    subprocess.run(command, stdout=report, check=True)
    elif args.stage == "smoke":
        from smoke import smoke

        assembly["_directory"] = str(args.assembly)
        smoke(preparation, assembly, args.output, args.cnpg_version)
    elif args.stage == "promote":
        if os.environ.get("GITHUB_REF") != "refs/heads/main" or os.environ.get(
            "GITHUB_EVENT_NAME"
        ) not in ("push", "workflow_dispatch"):
            raise ValueError("production promotion requires a trusted main event")
        tags = []
        signed = set()
        for tag in assembly["tags"]:
            repo, version = tag.rsplit(":", 1)
            destination = repo.removesuffix("-testing") + ":" + version
            subprocess.run(
                [
                    "skopeo",
                    "copy",
                    "--all",
                    "--preserve-digests",
                    "docker://" + image,
                    "docker://" + destination,
                ],
                check=True,
            )
            wait_for_index_digest(destination, assembly["index_digest"])
            copied = destination.rsplit(":", 1)[0] + "@" + assembly["index_digest"]
            if copied not in signed:
                sign(copied)
                signed.add(copied)
            tags.append(destination)
        save(
            args.output / "destination.json",
            {"tags": tags, "index_digest": assembly["index_digest"]},
        )
    save(
        args.output / "result.json",
        {
            "stage": args.stage,
            "success": True,
            "target": assembly["target"],
            "image": image,
            "run_id": assembly["run_id"],
            "preparation_sha256": preparation["preparation_sha256"],
        },
    )


if __name__ == "__main__":
    main()

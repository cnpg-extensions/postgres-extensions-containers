#!/usr/bin/env python3
"""Shared signing, scanning and promotion steps for each assembled target."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import re

from prepare import save
from record import load_preparation
from registry import wait_for_index_digest
from verify import verify_signature as check_signature, verify

ISSUER = "https://token.actions.githubusercontent.com"


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
    policy = (
        "^https://github\\.com/"
        + re.escape(
            os.environ.get(
                "GITHUB_REPOSITORY", "ardentperf/postgres-extensions-containers"
            )
        )
        + "/\\.github/workflows/(bake_targets|pgrx_targets)\\.yml@"
        + re.escape(os.environ.get("GITHUB_REF", "refs/heads/main"))
        + "$"
    )

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

    def verify_signature(reference):
        return check_signature(reference, identity=policy, issuer=ISSUER)

    if args.stage == "sign":
        sign(image)
        save(args.output / "signature.json", verify_signature(image))
    elif args.stage == "security":
        for platform in assembly["platforms"]:
            output = args.output / platform.split("/")[1]
            verify(image, platform, output, identity=policy, issuer=ISSUER)
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

        verify_signature(image)
        assembly["_directory"] = str(args.assembly)
        smoke(preparation, assembly, args.output, args.cnpg_version)
    elif args.stage == "promote":
        if os.environ.get("GITHUB_REF") != "refs/heads/main" or os.environ.get(
            "GITHUB_EVENT_NAME"
        ) not in ("push", "workflow_dispatch"):
            raise ValueError("production promotion requires a trusted main event")
        verify_signature(image)
        tags = []
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
            sign(copied)
            for platform in assembly["platforms"]:
                verify(
                    copied,
                    platform,
                    args.output
                    / ("copy-" + str(len(tags)) + "-" + platform.split("/")[1]),
                    identity=policy,
                    issuer=ISSUER,
                )
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

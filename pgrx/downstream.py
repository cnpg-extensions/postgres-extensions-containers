#!/usr/bin/env python3
"""Scan both platform SPDX documents from an assembled immutable image."""

import argparse
import json
import os
from pathlib import Path
import subprocess


# Security consumes the assembled immutable image directly, without preparation
# records or an artifact handoff job. Inspect once to extract both platforms'
# SPDX documents, mount them read-only into Grype and Grant, and retain reports
# on the runner. The workflow supplies the scanner image pins at the point of use.
def scan(image, output):
    grype_image = os.environ["GRYPE_IMAGE"]
    grant_image = os.environ["GRANT_IMAGE"]
    output = output.resolve()
    output.mkdir(parents=True)
    sboms = json.loads(subprocess.check_output([
        "docker", "buildx", "imagetools", "inspect", image,
        "--format", "{{json .SBOM}}",
    ]))
    for platform in ("linux/amd64", "linux/arm64"):
        directory = output / platform.split("/")[1]
        document = sboms.get(platform, {}).get("SPDX")
        if not isinstance(document, dict) or document.get("spdxVersion") != "SPDX-2.3":
            raise ValueError("missing SPDX document for " + platform)
        directory.mkdir()
        path = directory / "sbom.spdx.json"
        path.write_text(json.dumps(document) + "\n")
        mount = ["--volume", str(directory) + ":/results:ro"]
        for tool, command in (
            ("grype", [
                "docker", "run", "--rm", "--env", "GRYPE_DB_CACHE_DIR=/tmp/grype-db",
                *mount, grype_image, "sbom:/results/sbom.spdx.json", "-o", "json",
            ]),
            ("grant", [
                "docker", "run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}",
                *mount, grant_image, "list", "/results/sbom.spdx.json", "-o", "json",
            ]),
        ):
            with (directory / (tool + ".json")).open("w") as report:
                subprocess.run(command, stdout=report, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    scan(args.image, args.output)


if __name__ == "__main__":
    main()

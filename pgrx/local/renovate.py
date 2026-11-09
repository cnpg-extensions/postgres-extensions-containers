"""Run Renovate against the workspace without GitHub writes."""
import json
import re
import subprocess
from urllib.parse import urlsplit

from workflow import ROOT, discover


def _tool_versions(document, package_file):
    """Return version pins managed from tools JSON files."""
    result = set()

    def visit(value):
        if isinstance(value, dict):
            if all(key in value for key in ("version", "depName", "datasource")):
                result.add(
                    (package_file, value["depName"], value["version"], None)
                )
                return
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(document)
    return result


def _image_pins(document, package_file, field):
    result = set()
    for image in document.get(field, {}).values():
        match = re.fullmatch(
            r"(?P<depName>[^@]+):(?P<currentValue>[^@]+)@"
            r"(?P<currentDigest>sha256:[a-f0-9]{64})",
            image,
        )
        if not match:
            raise ValueError("invalid digest-pinned image in " + package_file)
        result.add(
            (
                package_file,
                match.group("depName"),
                match.group("currentValue"),
                match.group("currentDigest"),
            )
        )
    return result


def _source_dep_name(repository):
    parsed = urlsplit(repository)
    if parsed.scheme != "https" or parsed.netloc not in (
        "github.com",
        "gitlab.com",
    ):
        raise ValueError("unsupported PGRX source repository: " + repository)
    name = parsed.path.strip("/")
    if not name or parsed.query or parsed.fragment:
        raise ValueError("invalid PGRX source repository: " + repository)
    return name


def _expected_pins():
    expected = set()
    for extension, metadata in discover().items():
        dep_name = _source_dep_name(metadata["source_repository"])
        versions = {
            version["package"]
            for distro in metadata["versions"].values()
            for version in distro.values()
        }
        if not versions:
            raise ValueError("PGRX metadata has no package versions: " + extension)
        expected.update(
            (extension + "/metadata.hcl", dep_name, version, None)
            for version in versions
        )

    for filename in ("tools.json", "workflow-tools.json"):
        package_file = "pgrx/dependencies/" + filename
        document = json.loads((ROOT / package_file).read_text())
        expected.update(_tool_versions(document, package_file))
        expected.update(_image_pins(document, package_file, "images"))

    return expected


def check_renovate(output, image):
    output.mkdir(parents=True)
    # Native-only container; read-only source. No token and no remote platform.
    common = [
        "docker",
        "run",
        "--rm",
        "--platform",
        "linux/amd64",
        "-v",
        str(ROOT) + ":/repo:ro",
        "-w",
        "/repo",
    ]
    with (output / "validation.log").open("w") as log:
        subprocess.run(
            [
                *common,
                "--entrypoint",
                "renovate-config-validator",
                image,
                "/repo/renovate.json",
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )
    with (output / "extraction.jsonl").open("w") as log:
        subprocess.run(
            [
                *common,
                "-e",
                "LOG_LEVEL=debug",
                "-e",
                "LOG_FORMAT=json",
                image,
                "--platform=local",
                "--dry-run=extract",
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )
    entries = []
    for line in (output / "extraction.jsonl").read_text().splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if "packageFiles" in record:
            for files in record["packageFiles"].values():
                entries.extend(files)
    if not entries:
        raise ValueError("Renovate returned no extracted dependencies")

    expected = _expected_pins()
    expected_files = {pin[0] for pin in expected}
    actual = {
        (
            entry.get("packageFile"),
            dependency.get("depName"),
            dependency.get("currentValue"),
            dependency.get("currentDigest"),
        )
        for entry in entries
        for dependency in entry.get("deps", [])
        if entry.get("packageFile") in expected_files
    }
    missing = expected - actual
    unexpected = actual - expected
    if missing or unexpected:
        raise ValueError(
            "Renovate managed pin mismatch: missing="
            + str(sorted(missing))
            + ", unexpected="
            + str(sorted(unexpected))
        )

    with (output / "updates.log").open("w") as log:
        subprocess.run(
            [
                *common,
                "--entrypoint",
                "/usr/local/renovate/node",
                image,
                "/repo/pgrx/tests/renovate-update.mjs",
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )
    dependencies = {
        dep.get("depName") for entry in entries for dep in entry.get("deps", [])
    }
    (output / "result.json").write_text(
        json.dumps(
            {
                "success": True,
                "managedPins": len(expected),
                "dependencies": sorted(dependencies),
            }
        )
        + "\n"
    )

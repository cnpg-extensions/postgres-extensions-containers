#!/usr/bin/env python3
"""Finalize target-scoped Cargo reports and the actual scratch payload binding."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from build_config import RECIPES

sys.path.insert(0, str(Path(__file__).resolve().parent / "sbom"))
from augment_spdx import cargo_about_license_expressions, selected_graph


def normalize_about(data):
    """cargo-about 0.9.2 repeats an identical doctest Boolean in Cargo targets.

    Canonicalize only that known serializer defect before hashing the report.
    Every other duplicate, including equal identity values, remains an error.
    """

    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                if (
                    key != "doctest"
                    or type(value) is not bool
                    or result[key] is not value
                ):
                    raise ValueError("duplicate cargo-about JSON key: " + key)
            result[key] = value
        return result

    return (
        json.dumps(
            json.loads(data, object_pairs_hook=object_pairs), sort_keys=True
        ).encode()
        + b"\n"
    )


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover_extension_payload(extension_dir, sql_name):
    """Return regular files belonging to an extension's packaged payload.

    PostgreSQL packages runtime data in directories named after the SQL
    extension, alongside its control and SQL files. Preserve paths below the
    extension directory so builder files map to the same paths in the final
    image. Sort both directory traversal and the result for a stable manifest.
    """
    extension_dir = Path(extension_dir)
    if extension_dir.is_symlink():
        raise ValueError(
            "payload directory must not be a symlink: " + str(extension_dir)
        )

    files = []

    def collect(path):
        if path.is_symlink():
            raise ValueError("payload must not contain symlinks: " + str(path))
        if path.is_dir():
            for child in sorted(path.iterdir()):
                collect(child)
        elif path.is_file():
            relative = path.relative_to(extension_dir).as_posix()
            files.append((path, "share/extension/" + relative, "extension"))
        else:
            raise ValueError("payload must contain only regular files: " + str(path))

    for path in sorted(extension_dir.iterdir()):
        if path.name.startswith(sql_name):
            collect(path)
    return sorted(files, key=lambda entry: entry[1])


# Finalize after compilation using the same package, PostgreSQL feature,
# non-PG defaults and feature policy as cargo-pgrx. Resolve target-filtered Cargo
# metadata, emit Cargo/cargo-about reports, check the lock for drift, ship license
# texts, and hash the completed library/control/SQL payload. Write the schema-v2
# manifest last. The diagnostic pgrx-sbom Docker target exports this evidence;
# it does not replace an image build that produces attestations.
#
# normalize_about handles cargo-about 0.9.2's repeated identical Boolean doctest
# field before report hashing. Other duplicate keys and conflicting values fail.
def main():
    build = Path("/build")
    directory = build / "pgrx-sbom"
    config = json.loads((directory / "build-config.json").read_text())
    lock = build / "Cargo.lock"
    if digest(lock) != config["lock_sha256"]:
        raise ValueError("Cargo.lock changed during compilation")
    # Docker build arguments are exposed as environment variables: the catalog
    # name selects the recipe and identifies its payload; PG_MAJOR selects its
    # PostgreSQL layout, and BuildKit TARGETPLATFORM identifies the OCI platform.
    extension = os.environ["PGRX_EXTENSION"]
    recipe = RECIPES[extension]
    source = json.loads((directory / "source.json").read_text())
    major = os.environ["PG_MAJOR"]
    platform = os.environ["TARGETPLATFORM"]
    common = [
        "--manifest-path",
        str(build / config["manifest"]),
        "--features",
        ",".join(config["features"]),
        "--no-default-features",
    ]
    env = {**os.environ, "CARGO_NET_OFFLINE": "true"}

    def run(command, output=None):
        result = subprocess.run(
            command, cwd=build, env=env, check=True, capture_output=True
        )
        if output:
            output.write_bytes(result.stdout)
        return result.stdout

    run(
        [
            "cargo",
            "metadata",
            "--locked",
            "--format-version=1",
            "--filter-platform",
            config["rust_target"],
            *common,
        ],
        directory / "cargo-metadata.json",
    )
    metadata = json.loads((directory / "cargo-metadata.json").read_text())
    roots = [
        p
        for p in metadata["packages"]
        if Path(p["manifest_path"]) == build / config["manifest"]
    ]
    if len(roots) != 1:
        raise ValueError("ambiguous Cargo package root")
    root = roots[0]
    config["root_id"] = root["id"]
    packages, edges = selected_graph(
        metadata,
        root["id"],
        config["features"],
        config["target_cfg"],
        config["rust_target"],
    )
    run(
        [
            "cargo",
            "about",
            "generate",
            "--config",
            "/pgrx/license-about.toml",
            "--format",
            "json",
            "--locked",
            "--offline",
            "--fail",
            "--target",
            config["rust_target"],
            *common,
        ],
        directory / "cargo-about.json",
    )
    about_path = directory / "cargo-about.json"
    about_path.write_bytes(normalize_about(about_path.read_bytes()))
    licenses = build / "pgrx-licenses/rust"
    licenses.mkdir(parents=True, exist_ok=True)
    associations = []
    about = json.loads((directory / "cargo-about.json").read_text())
    # Fail the build if cargo-about did not resolve a reportable expression
    # for every crate in the selected runtime graph. The hook repeats this
    # check against the hash-verified report before writing SPDX.
    cargo_about_license_expressions(packages, about)
    for entry in about["licenses"]:
        selected = [
            use["crate"]["id"]
            for use in entry["used_by"]
            if use["crate"]["id"] in packages
        ]
        if not selected:
            continue
        text = entry["text"]
        name = "cargo-about-" + hashlib.sha256(text.encode()).hexdigest() + ".txt"
        path = licenses / name
        path.write_text(text)
        for cargo_id in sorted(set(selected)):
            associations.append(
                {
                    "cargo_id": cargo_id,
                    "name": entry["id"],
                    "final": "licenses/rust/" + name,
                    "sha256": digest(path),
                }
            )
    missing = set(packages) - {entry["cargo_id"] for entry in associations}
    if missing:
        raise ValueError(
            "selected Cargo graph lacks license evidence: " + ", ".join(sorted(missing))
        )
    # Preserve upstream license/copyright notices in addition to cargo-about text.
    for path in sorted(build.glob("LICENSE*")):
        if path.is_file():
            shutil.copyfile(path, licenses / path.name)
    sql_name = root["name"]
    sql_version = root["version"]
    prefix = (
        Path("/")
        if recipe["installed"]
        else build / f"target/release/{sql_name}-pg{major}"
    )
    library = prefix / f"usr/lib/postgresql/{major}/lib/{sql_name}.so"
    files = [(library, "lib/" + library.name, "library")]
    extension_dir = prefix / f"usr/share/postgresql/{major}/extension"
    extension_files = discover_extension_payload(extension_dir, sql_name)
    top_level = {
        Path(final).name
        for _, final, _ in extension_files
        if Path(final).parent == Path("share/extension")
    }
    if sql_name + ".control" not in top_level:
        raise ValueError("missing packaged extension control file")
    if not any(
        name.startswith(sql_name + "--") and name.endswith(".sql")
        for name in top_level
    ):
        raise ValueError("missing packaged extension SQL file")
    files.extend(extension_files)
    payload = []
    for path, final, kind in files:
        if not path.is_file() or path.is_symlink():
            raise ValueError("payload must be a regular file: " + str(path))
        payload.append(
            {
                "builder": str(path).lstrip("/"),
                "final": final,
                "kind": kind,
                "sha256": digest(path),
            }
        )
    reports = {
        name: {
            "path": name + ".json",
            "sha256": digest(directory / (name + ".json")),
            "tool_version": config["tools"].get(name, config["tools"]["rustc"]),
        }
        for name in ["cargo-metadata", "cargo-about"]
    }
    identity = {
        "extension": extension,
        "sql_name": sql_name,
        "source_version": source["version"],
        "sql_version": sql_version,
        "repository": source["repository"],
        "source_host": source["host"],
        "source_url": source["url"],
        "revision": source["revision"],
        "archive_sha256": source["archive_sha256"],
    }
    manifest = {
        "schema_version": 2,
        "identity": identity,
        "target": {
            "platform": platform,
            "rust_target": config["rust_target"],
            "pg_major": major,
            # Bake supplies the distribution selected for this target.
            "distro": os.environ["PGRX_DISTRO"],
        },
        "build": {
            k: v
            for k, v in config.items()
            if k not in ("lock_sha256", "original_lock_sha256", "patches")
        },
        "inputs": {
            "lock_sha256": config["lock_sha256"],
            "original_lock_sha256": config["original_lock_sha256"],
            "patches": config["patches"],
            # Preparation supplies the run timestamp for the evidence record.
            "timestamp": os.environ["PGRX_BUILD_TIMESTAMP"],
        },
        "reports": reports,
        "payload": payload,
        "licenses": associations,
    }
    if digest(lock) != config["lock_sha256"]:
        raise ValueError("Cargo.lock changed during reporting")
    (directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Install version-selected Rust and reporting tools for a PGRX build."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tomllib
import urllib.request

from build_config import RECIPES, effective_features
from source import resolve_source

PGRX = Path("/pgrx")
BUILD = Path("/build")


def tool_url(name, version, architecture):
    numeric = version.removeprefix("v")
    architecture = architecture.lower()
    if architecture not in ("amd64", "arm64"):
        raise ValueError("unsupported architecture: " + architecture)
    rust_arch = {"amd64": "x86_64", "arm64": "aarch64"}[architecture]
    templates = {
        "cargo-about": (
            "https://github.com/EmbarkStudios/cargo-about/releases/download/"
            f"{numeric}/cargo-about-{numeric}-{rust_arch}-unknown-linux-musl.tar.gz"
        ),
        "rustup": (
            "https://static.rust-lang.org/rustup/archive/{numeric}/"
            "{rust_arch}-unknown-linux-gnu/rustup-init"
        ),
    }
    try:
        template = templates[name]
    except KeyError as error:
        raise ValueError("unsupported tool: " + name) from error
    return template.format(
        version=numeric,
        numeric=numeric,
        architecture=architecture,
        rust_arch=rust_arch,
    )


def download(url, destination):
    data = urllib.request.urlopen(url).read()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return destination


def run(*command, **kwargs):
    return subprocess.run(command, check=True, **kwargs)


def install_archive_tool(name, url):
    archive = download(url, Path("/tmp") / (name + ".download"))
    if url.endswith(".tar.gz"):
        with tarfile.open(archive) as tar:
            members = [m for m in tar if m.isfile() and Path(m.name).name == name]
            if len(members) != 1:
                raise ValueError("ambiguous tool archive: " + name)
            data = tar.extractfile(members[0]).read()
    else:
        data = archive.read_bytes()
    destination = Path("/usr/local/bin") / name
    destination.write_bytes(data)
    destination.chmod(0o755)


# Extension Dockerfiles retain their attributed upstream build commands. The
# shell wrapper installs Debian build dependencies with apt-get update/install
# before this installs Renovate-managed Rust and reporting tools. Rustup uses
# normal distribution verification for the selected compiler. Cargo-about uses
# architecture-specific upstream release artifacts; among these installed tools,
# only cargo-pgrx is built from source, at the exact version from the extension's
# Cargo.lock and with its own dependencies locked by cargo install --locked.
#
# JWT v0.5.0 and Anonymizer 3.3.2 correct stale root-package lock versions in their
# Dockerfiles, guarded by exact original/effective checksums. Any upstream lock
# change requires review or removal of the correction. Record both lock hashes;
# the legacy patches field remains empty for schema compatibility. These inputs
# are generated from upstream Cargo.lock, not a second committed tool lock.
def main():
    major, lock_file = sys.argv[1:]
    # Bake supplies the catalog name to select the build recipe. BuildKit
    # supplies TARGETARCH to select Rust tool downloads and the target triple.
    extension = os.environ["PGRX_EXTENSION"]
    arch = os.environ["TARGETARCH"]
    tools = json.loads((PGRX / "dependencies/tools.json").read_text())
    recipe = RECIPES[extension]
    manifest = tomllib.loads((BUILD / recipe["manifest"]).read_text())
    triple = {
        "amd64": "x86_64-unknown-linux-gnu",
        "arm64": "aarch64-unknown-linux-gnu",
    }[arch]
    version = tools["rust"]["version"]

    rustup_binary = download(
        tool_url("rustup", tools["rustup"]["version"], arch),
        Path("/tmp/rustup-init"),
    )
    rustup_binary.chmod(0o755)
    run(str(rustup_binary), "-y", "--no-modify-path", "--default-toolchain", "none")
    cargo_bin = Path.home() / ".cargo/bin"
    os.environ["PATH"] = str(cargo_bin) + ":" + os.environ["PATH"]
    run("rustup", "set", "auto-self-update", "disable")
    run(
        "rustup",
        "toolchain",
        "install",
        version,
        "--profile",
        "minimal",
        "--component",
        "rustfmt",
    )
    os.environ["RUSTUP_TOOLCHAIN"] = version
    run("rustup", "default", version)
    for name in ("cargo", "rustc", "rustdoc", "rustfmt"):
        wrapper = Path("/usr/local/bin") / name
        wrapper.write_text(
            f'#!/bin/sh\nexport RUSTUP_TOOLCHAIN={version}\nexec {cargo_bin/name} "$@"\n'
        )
        wrapper.chmod(0o755)
    pg_config = f"/usr/lib/postgresql/{major}/bin/pg_config"
    Path("/usr/local/bin/pg_config").symlink_to(pg_config)
    for name, tool in tools["tools"].items():
        install_archive_tool(name, tool_url(name, tool["version"], arch))

    original_path = Path("/tmp/pgrx-original-Cargo.lock")
    original_bytes = (
        original_path.read_bytes()
        if original_path.exists()
        else Path(lock_file).read_bytes()
    )
    original_lock = hashlib.sha256(original_bytes).hexdigest()
    lock_bytes = Path(lock_file).read_bytes()
    lock = tomllib.loads(lock_bytes.decode())
    versions = {p["version"] for p in lock["package"] if p["name"] == "pgrx"}
    if len(versions) != 1:
        raise ValueError("ambiguous locked cargo-pgrx version")
    pgrx_version = versions.pop()
    run(
        "cargo",
        "install",
        "--locked",
        "--version",
        "=" + pgrx_version,
        "cargo-pgrx",
        "--root",
        "/usr/local",
    )
    run("cargo", "pgrx", "init", "--pg" + major, pg_config, "--no-run")
    features = effective_features(manifest, recipe, major)
    config = {
        "manifest": recipe["manifest"],
        "features": features,
        "default_features": False,
        "recipe_default_features": recipe["defaults"],
        "profile": "release",
        "rustflags": os.getenv("RUSTFLAGS", ""),
        "rust_target": triple,
        "target_cfg": run(
            "rustc",
            "--print",
            "cfg",
            "--target",
            triple,
            capture_output=True,
            text=True,
        ).stdout.splitlines(),
        "tools": {
            "rustc": version,
            "cargo-pgrx": pgrx_version,
            **{k: v["version"] for k, v in tools["tools"].items()},
        },
    }
    report = BUILD / "pgrx-sbom"
    report.mkdir(exist_ok=True)
    config["original_lock_sha256"] = original_lock
    # Preserve the evidence schema; Dockerfile corrections use the two lock hashes.
    config["patches"] = []
    config["lock_sha256"] = hashlib.sha256(lock_bytes).hexdigest()
    (report / "build-config.json").write_text(json.dumps(config, indent=2) + "\n")
    # Bake supplies the canonical repository and exact release tag (EXT_VERSION).
    # Preparation supplies PGRX_SOURCE_REVISION; direct builds may omit it,
    # in which case resolve_source resolves the tag to a revision here.
    source_record = resolve_source(
        os.environ["PGRX_SOURCE_REPOSITORY"],
        os.environ["EXT_VERSION"],
        archive=Path("/tmp/source.tar.gz").read_bytes(),
        revision=os.getenv("PGRX_SOURCE_REVISION") or None,
    )
    (report / "source.json").write_text(json.dumps(source_record, indent=2) + "\n")
    # cargo-about queries the full metadata graph before filtering the target.
    # Fetch all locked source archives so that reporting stays offline. This
    # does not compile foreign targets or include them in the runtime SBOM.
    run(
        "cargo", "fetch", "--locked", "--manifest-path", str(BUILD / recipe["manifest"])
    )


if __name__ == "__main__":
    main()

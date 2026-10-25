#!/usr/bin/env python3
"""Refresh coupled immutable locks after a reviewed Renovate update.

Checks are offline. Refreshes download public data and never execute ARM code.
Renovate proposes parent versions/digests; these commands update their children.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import tomllib
import urllib.request

from workflow import ROOT, discover


def fetch(url):
    return urllib.request.urlopen(url).read()


def api(url):
    return json.loads(fetch("https://api.github.com/" + url))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def tool_url(name, version, architecture):
    numeric = version.removeprefix("v")
    rust_arch = {"amd64": "x86_64", "arm64": "aarch64"}[architecture]
    if name in ("grype", "grant"):
        return f"https://github.com/anchore/{name}/releases/download/v{numeric}/{name}_{numeric}_linux_{architecture}.tar.gz"
    templates = {
        "cargo-about": f"https://github.com/EmbarkStudios/cargo-about/releases/download/{numeric}/cargo-about-{numeric}-{rust_arch}-unknown-linux-musl.tar.gz",
        "cosign": f"https://github.com/sigstore/cosign/releases/download/v{numeric}/cosign-linux-{architecture}",
        "actionlint": f"https://github.com/rhysd/actionlint/releases/download/v{numeric}/actionlint_{numeric}_linux_{architecture}.tar.gz",
        "task": f"https://github.com/go-task/task/releases/download/v{numeric}/task_linux_{architecture}.tar.gz",
        "dagger": f"https://github.com/dagger/dagger/releases/download/v{numeric}/dagger_v{numeric}_linux_{architecture}.tar.gz",
        "kind": f"https://github.com/kubernetes-sigs/kind/releases/download/v{numeric}/kind-linux-{architecture}",
        "rustup": f"https://static.rust-lang.org/rustup/archive/{numeric}/{rust_arch}-unknown-linux-gnu/rustup-init",
    }
    return templates[name]


def check_sources(inventory, sources):
    if set(sources) != set(inventory):
        raise ValueError("source lock inventory mismatch")
    for name, metadata in inventory.items():
        pin = sources[name]
        versions = {
            v["package"]
            for majors in metadata["versions"].values()
            for v in majors.values()
        }
        if versions != {pin["version"]}:
            raise ValueError("metadata/source lock disagreement: " + name)
        if not re.fullmatch("[a-f0-9]{40}", pin["revision"]):
            raise ValueError("invalid source revision")
        for field in ["archive_sha256", "original_lock_sha256", "cargo_pgrx_sha256"]:
            if not re.fullmatch("[a-f0-9]{64}", pin[field]):
                raise ValueError("invalid source checksum: " + field)
        if (
            pin["url"]
            != f"https://github.com/{pin['repository']}/archive/{pin['version']}.tar.gz"
        ):
            raise ValueError("stale source URL")


def refresh_sources(root, inventory, sources):
    for name, metadata in inventory.items():
        versions = {
            v["package"]
            for majors in metadata["versions"].values()
            for v in majors.values()
        }
        if len(versions) != 1:
            raise ValueError("source lock needs distinct records for multiple releases")
        version = versions.pop()
        repository = sources[name]["repository"]
        revision = api(f"repos/{repository}/commits/{version}")["sha"]
        url = f"https://github.com/{repository}/archive/{version}.tar.gz"
        data = fetch(url)
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            locks = [
                m
                for m in archive
                if len(Path(m.name).parts) == 2 and Path(m.name).name == "Cargo.lock"
            ]
            if len(locks) != 1:
                raise ValueError("missing upstream root Cargo.lock")
            lock_bytes = archive.extractfile(locks[0]).read()
            lock = tomllib.loads(lock_bytes.decode())
        pgrx = {p["version"] for p in lock["package"] if p["name"] == "pgrx"}
        if len(pgrx) != 1:
            raise ValueError("ambiguous pgrx dependency")
        cli = pgrx.pop()
        cli_data = fetch(
            "https://static.crates.io/crates/cargo-pgrx/cargo-pgrx-" + cli + ".crate"
        )
        sources[name] = {
            "repository": repository,
            "version": version,
            "revision": revision,
            "archive_sha256": sha(data),
            "url": url,
            "original_lock_sha256": sha(lock_bytes),
            "cargo_pgrx": cli,
            "cargo_pgrx_sha256": sha(cli_data),
        }
    write(root / "sources.json", sources)


def tools_lock(root, refresh):
    for filename in ["tools.json", "workflow-tools.json"]:
        path = root / filename
        lock = json.loads(path.read_text())
        entries = dict(lock["tools"])
        if "rustup" in lock:
            entries["rustup"] = lock["rustup"]
        for name, entry in entries.items():
            if set(entry["platforms"]) != {"amd64", "arm64"}:
                raise ValueError("missing tool architecture checksum: " + name)
            for architecture, pin in entry["platforms"].items():
                url = tool_url(name, entry["version"], architecture)
                if refresh:
                    pin.update(url=url, sha256=sha(fetch(url)))
                if pin["url"] != url or not re.fullmatch("[a-f0-9]{64}", pin["sha256"]):
                    raise ValueError("tool update requires checksum refresh: " + name)
        if "rust" in lock:
            rust = lock["rust"]
            if refresh:
                data = fetch(
                    "https://static.rust-lang.org/dist/channel-rust-"
                    + rust["version"]
                    + ".toml"
                )
                tomllib.loads(data.decode())
                rust["manifest_sha256"] = sha(data)
            if not re.fullmatch(
                r"[0-9]+\.[0-9]+\.[0-9]+", rust["version"]
            ) or not re.fullmatch("[a-f0-9]{64}", rust["manifest_sha256"]):
                raise ValueError("Rust manifest requires refresh")
        if refresh:
            write(path, lock)


def bases_lock(root, refresh):
    path = root / "bases.json"
    bases = json.loads(path.read_text())
    if refresh:
        for reference in bases:
            manifest = json.loads(
                subprocess.check_output(
                    [
                        "docker",
                        "buildx",
                        "imagetools",
                        "inspect",
                        reference,
                        "--format",
                        "{{json .Manifest}}",
                    ]
                )
            )
            platforms = {
                d["platform"]["os"] + "/" + d["platform"]["architecture"]: d["digest"]
                for d in manifest["manifests"]
                if d.get("platform", {}).get("os") == "linux"
                and d["platform"]["architecture"] in ("amd64", "arm64")
            }
            if set(platforms) != {"linux/amd64", "linux/arm64"}:
                raise ValueError("base missing required architectures")
            bases[reference] = {
                "index_digest": manifest["digest"],
                "platforms": platforms,
            }
        write(path, bases)
    return bases


def operator_manifest_url(pin):
    ref = pin["ref"]
    match = re.fullmatch(r"v(\d+\.\d+\.\d+)", ref)
    if not match:
        raise ValueError("operator fixture must pin a published CNPG release tag")
    if pin["repository"] != "cloudnative-pg/cloudnative-pg":
        raise ValueError(
            "operator fixture must use the official CNPG release repository"
        )
    return f"https://raw.githubusercontent.com/{pin['repository']}/{pin['revision']}/releases/cnpg-{match.group(1)}.yaml"


def check_operator_manifest(data, pin):
    version = pin["ref"].removeprefix("v")
    image = f"ghcr.io/cloudnative-pg/cloudnative-pg:{version}"
    if image not in data or "cloudnative-pg-testing" in data:
        raise ValueError(
            "operator fixture must use its published production CNPG image"
        )


def fixtures_lock(root, refresh):
    directory = root / "fixtures"
    path = directory / "lock.json"
    lock = json.loads(path.read_text())
    if lock["selector"] not in lock["operators"] or not set(
        lock["supported_releases"]
    ) <= set(lock["operators"]):
        raise ValueError("invalid default or supported CNPG fixture selector")
    for selector, pin in lock["operators"].items():
        if pin["ref"][1:].rsplit(".", 1)[0] != selector:
            raise ValueError("operator fixture release does not match its selector")
        if refresh:
            pin["revision"] = api(
                "repos/" + pin["repository"] + "/commits/" + pin["ref"]
            )["sha"]
            pin["url"] = operator_manifest_url(pin)
            data = fetch(pin["url"])
            check_operator_manifest(data.decode(), pin)
            pin["sha256"] = sha(data)
        if (
            not re.fullmatch("[a-f0-9]{40}", pin["revision"])
            or pin["url"] != operator_manifest_url(pin)
            or not re.fullmatch("[a-f0-9]{64}", pin["sha256"])
        ):
            raise ValueError("operator fixture requires refresh")
    if refresh:
        lock["files"]["operator"] = lock["operators"][lock["selector"]]
    elif lock["files"]["operator"] != lock["operators"][lock["selector"]]:
        raise ValueError("default operator fixture alias is stale")
    for name, pin in lock["files"].items():
        if name == "operator":
            continue
        file = directory / (name + ".yaml")
        if refresh:
            old_revision = pin["revision"]
            pin["revision"] = api("repos/" + pin["repository"] + "/commits/main")["sha"]
            pin["url"] = pin["url"].replace(old_revision, pin["revision"])
            data = fetch(pin["url"])
            file.write_bytes(data)
            pin["sha256"] = sha(data)
        if pin["revision"] not in pin["url"] or sha(file.read_bytes()) != pin["sha256"]:
            raise ValueError("catalog fixture requires refresh")
    if refresh:
        write(path, lock)


def check_apt(root):
    lock = json.loads((root / "apt/lock.json").read_text())
    if lock["base_lock_sha256"] != sha((root / "bases.json").read_bytes()):
        raise ValueError("base update requires coupled apt refresh")
    expected = {
        f"{suite}-{arch}.tsv"
        for suite in ["bookworm", "trixie"]
        for arch in ["amd64", "arm64"]
    }
    if set(lock["files"]) != expected:
        raise ValueError("missing apt lock architecture")
    for filename, digest in lock["files"].items():
        path = root / "apt" / filename
        if sha(path.read_bytes()) != digest:
            raise ValueError("apt lock ownership checksum mismatch")
        names = set()
        for row in path.read_text().splitlines():
            checksum, name, url = row.split("\t")
            if (
                not re.fullmatch("[a-f0-9]{64}", checksum)
                or name in names
                or "/" in name
                or not url.startswith(("https://", "http://"))
            ):
                raise ValueError("invalid apt artifact row")
            names.add(name)
        if not names:
            raise ValueError("empty apt artifact lock")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--refresh", action="store_true")
    parser.add_argument(
        "--only",
        choices=["all", "sources", "tools", "bases", "fixtures", "apt"],
        default="all",
    )
    args = parser.parse_args()
    root = ROOT / "pgrx/dependencies"
    inventory = discover()
    sources = json.loads((root / "sources.json").read_text())

    def refresh(part):
        return args.refresh and args.only in ("all", part)

    if refresh("sources"):
        refresh_sources(root, inventory, sources)
    check_sources(inventory, sources)
    tools_lock(root, refresh("tools"))
    bases_lock(root, refresh("bases"))
    fixtures_lock(root, refresh("fixtures"))
    if refresh("apt") or refresh("bases"):
        from refresh_apt import refresh_apt

        refresh_apt()
    check_apt(root)
    print("PGRX source, tool, base, fixture and package locks are consistent")


if __name__ == "__main__":
    main()

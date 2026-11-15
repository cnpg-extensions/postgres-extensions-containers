"""Fetch trusted source archives; preserve selected nested revisions as evidence."""
import io
import json
import os
import re
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, "/source-build")
from source import resolve_source
import tarfile
import urllib.request


def fetch(repo, revision, destination):
    url = f"{repo}/archive/{revision}.tar.gz"
    with urllib.request.urlopen(url) as response:
        archive = tarfile.open(fileobj=io.BytesIO(response.read()), mode="r:gz")
    destination.mkdir(parents=True, exist_ok=True)
    for member in archive.getmembers():
        parts = Path(member.name).parts
        if len(parts) < 2:
            continue
        member.name = str(Path(*parts[1:]))
        archive.extract(member, destination, filter="data")
    return url


if __name__ == "__main__":
    repo = "https://github.com/duckdb/pg_duckdb"
    revision = resolve_source(repo, os.environ["EXT_VERSION"])["revision"]
    assert len(revision) == 40 and all(c in "0123456789abcdef" for c in revision)
    fetch(repo, revision, Path("/build"))
    # GitHub's tree API resolves the gitlink from the actual selected parent.
    api = f"https://api.github.com/repos/duckdb/pg_duckdb/git/trees/{revision}?recursive=1"
    with urllib.request.urlopen(api) as response:
        tree = json.load(response)["tree"]
    duck = next(item["sha"] for item in tree if item["path"] == "third_party/duckdb" and item["type"] == "commit")
    fetch("https://github.com/duckdb/duckdb", duck, Path("third_party/duckdb"))
    config = Path('third_party/pg_duckdb_extensions.cmake')
    text = config.read_text()
    httprev = re.search(r'GIT_TAG ([a-f0-9]{40})', text)[1]
    fetch('https://github.com/duckdb/duckdb-httpfs', httprev, Path('third_party/httpfs'))
    text = re.sub(r'GIT_URL https://github.com/duckdb/duckdb-httpfs\s+GIT_TAG [a-f0-9]{40}',
                  lambda _: 'SOURCE_DIR /build/third_party/httpfs\n    EXTENSION_VERSION ' + httprev, text)
    config.write_text(text)
    # Upstream make's gitlink prerequisite must exist for archive builds.
    marker = Path(".git/modules/third_party/duckdb/HEAD")
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(duck + "\n")
    Path("source-evidence.json").write_text(json.dumps({"repository": repo, "revision": revision, "duckdb_revision": duck, "httpfs_revision": httprev, "version": os.environ["EXT_VERSION"]}, indent=2))

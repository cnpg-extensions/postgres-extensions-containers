#!/usr/bin/env python3
"""Resolve release identity and record downloaded source archives."""

import hashlib
import io
import json
import re
import tarfile
from urllib.parse import quote, urlsplit
import urllib.request


def fetch(url):
    with urllib.request.urlopen(url) as response:
        return response.read()


def source_repository(repository_url):
    """Return the supported host and owner/project path from a repository URL."""
    if not isinstance(repository_url, str):
        raise ValueError("source repository URL must be a string")
    parsed = urlsplit(repository_url)
    if parsed.scheme != "https" or parsed.query or parsed.fragment:
        raise ValueError("source repository must be an HTTPS URL")
    host = parsed.hostname
    if host not in ("github.com", "gitlab.com"):
        raise ValueError("unsupported source host: " + str(host))
    if parsed.username or parsed.password or parsed.port:
        raise ValueError("source repository URL must not include credentials or a port")
    repository = parsed.path.strip("/")
    if repository.endswith(".git"):
        repository = repository[:-4]
    parts = repository.split("/")
    if len(parts) < 2 or any(not part or part in (".", "..") for part in parts):
        raise ValueError("invalid source repository path")
    if host == "github.com" and len(parts) != 2:
        raise ValueError("GitHub source repository must be owner/project")
    return host, repository


def source_archive_url(repository_url, version):
    host, repository = source_repository(repository_url)
    if (
        not isinstance(version, str)
        or not version
        or any(c.isspace() for c in version)
    ):
        raise ValueError("invalid source version")
    ref = quote(version, safe="")
    if host == "github.com":
        return f"https://github.com/{repository}/archive/{ref}.tar.gz"
    project = repository.rsplit("/", 1)[-1]
    return (
        f"https://gitlab.com/{repository}/-/archive/{ref}/"
        f"{project}-{ref}.tar.gz"
    )


def source_revision(host, repository, version):
    ref = quote(version, safe="")
    if host == "github.com":
        url = f"https://api.github.com/repos/{repository}/commits/{ref}"
        result = json.loads(fetch(url))
        revision = result["sha"]
    elif host == "gitlab.com":
        project = quote(repository, safe="")
        url = (
            "https://gitlab.com/api/v4/projects/"
            f"{project}/repository/commits/{ref}"
        )
        result = json.loads(fetch(url))
        revision = result["id"]
    else:
        raise ValueError("unsupported source host: " + str(host))
    if not isinstance(revision, str) or not re.fullmatch(
        r"[a-fA-F0-9]{40}", revision
    ):
        raise ValueError("invalid source revision returned by host")
    return revision.lower()


def resolve_source(repository_url, version):
    """Resolve a release before acquiring its source by commit."""
    host, repository = source_repository(repository_url)
    url = source_archive_url(repository_url, version)
    return {
        "repository": repository,
        "host": host,
        "version": version,
        "revision": source_revision(host, repository, version),
        "url": url,
    }


def archive_identity(archive):
    """Record the downloaded Git archive without consulting a mutable tag."""
    if not isinstance(archive, bytes):
        raise ValueError("source archive must be bytes")
    # GitHub and GitLab Git archives embed the actual commit in a global
    # PAX header. Repository attribution is available through build provenance
    # and the recipe's ADD URL, rather than a duplicate installer input.
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        revision = tar.pax_headers.get("comment")
    if not isinstance(revision, str) or not re.fullmatch(r"[a-fA-F0-9]{40}", revision):
        raise ValueError("source archive must identify its Git commit")
    return {
        "revision": revision.lower(),
        "archive_sha256": hashlib.sha256(archive).hexdigest(),
    }

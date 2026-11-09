#!/usr/bin/env python3
"""Resolve release identity and record downloaded source archives."""

import hashlib
import json
import re
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


def resolve_source(repository_url, version, archive=None, revision=None):
    """Resolve release identity and hash the supplied archive when available."""
    host, repository = source_repository(repository_url)
    url = source_archive_url(repository_url, version)
    if revision is None:
        revision = source_revision(host, repository, version)
    elif not isinstance(revision, str) or not re.fullmatch(
        r"[a-fA-F0-9]{40}", revision
    ):
        raise ValueError("invalid supplied source revision")
    revision = revision.lower()
    result = {
        "repository": repository,
        "host": host,
        "version": version,
        "revision": revision,
        "url": url,
    }
    if archive is not None:
        if not isinstance(archive, bytes):
            raise ValueError("source archive must be bytes")
        result["archive_sha256"] = hashlib.sha256(archive).hexdigest()
    return result

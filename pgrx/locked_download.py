"""Retrieve immutable public inputs and verify their locked bytes."""

import hashlib
import urllib.error
import urllib.request


def fetch_verified(url, checksum):
    try:
        data = urllib.request.urlopen(url).read()
    except (urllib.error.URLError, OSError) as error:
        raise ValueError("locked input unavailable: " + url) from error
    if hashlib.sha256(data).hexdigest() != checksum:
        raise ValueError("locked input checksum mismatch: " + url)
    return data

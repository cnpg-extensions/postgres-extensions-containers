"""Record the reviewed package inventory for the shared SBOM hook."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

BUILD = Path('/build')
DUCK = BUILD / 'third_party/duckdb'
PG_REVISION = '8756099e267c47f0b86c24de4cf995327f1f4279'
DUCK_REVISION = 'd54cbbe3df17e8e5ce68312f483b4155836112aa'

# Reviewed pg_duckdb 1.2.0 default release build, following Debian DuckDB
# 2.0.0+dfsg2 package boundaries. No dependency discovery happens at build time.
# name: (version, upstream repository, Debian counterpart, vendor path, license)
LIBRARIES = {
    'brotli': ('1.1.0', 'google/brotli', 'libbrotli1', 'third_party/brotli', 'MIT'),
    'lz4': ('1.9.4', 'lz4/lz4', 'liblz4-1', 'third_party/lz4', 'BSD-2-Clause'),
    'mbedtls': ('3.6.7', 'Mbed-TLS/mbedtls', 'libmbedcrypto16', 'third_party/mbedtls', None),
    # Compiler-dependent version macros: retain this snapshot's source identity.
    'snappy': (None, None, 'libsnappy1v5', 'third_party/snappy', 'BSD-3-Clause'),
    'yyjson': ('0.9.0', 'ibireme/yyjson', 'libyyjson0', 'third_party/yyjson', 'MIT'),
    'zstd': ('1.5.6', 'facebook/zstd', 'libzstd1', 'third_party/zstd', None),
    'xxhash': ('0.6.2', 'Cyan4973/xxHash', 'libxxhash0', 'third_party/zstd', None),
}


def package(name, version, repo, revision, parent, purl=None, debian=None,
            source_url=None, license=None, root=Path('/')):
    notice = Path('licenses') / name / 'copyright'
    text = (root / notice).read_text()
    return dict(name=name, version=version, repository=repo, revision=revision,
                parent=parent, purl=purl, debian_package=debian, source_url=source_url,
                notices=[str(notice)], license_text=text,
                license=license or 'LicenseRef-Universe-' + hashlib.sha256(text.encode()).hexdigest()[:24],
                copyright='\n'.join(dict.fromkeys(line.strip() for line in text.splitlines()
                    if re.search(r'copyright.*(?:[0-9]|©|\(c\))', line, re.I))) or 'NOASSERTION')


def main():
    for directory, expected in [(BUILD, PG_REVISION), (DUCK, DUCK_REVISION)]:
        actual = subprocess.check_output(['git', '-C', str(directory), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != expected:
            raise ValueError('Review the static package inventory and copyright files for updated source: ' + str(directory))
    components = [
        package('pg_duckdb', '1.2.0', 'https://github.com/duckdb/pg_duckdb', PG_REVISION,
                None, 'pkg:github/duckdb/pg_duckdb@v1.2.0'),
        package('duckdb', '2.0.0', 'https://github.com/duckdb/duckdb', DUCK_REVISION,
                'pg_duckdb', 'pkg:github/duckdb/duckdb@' + DUCK_REVISION),
    ]
    for name, (version, repo, debian, source, license) in LIBRARIES.items():
        components.append(package(name, version,
            'https://github.com/' + repo if repo else 'https://github.com/duckdb/duckdb',
            DUCK_REVISION + ':' + source, 'zstd' if name == 'xxhash' else 'duckdb',
            'pkg:github/' + repo + '@' + version if repo else None, debian,
            'https://github.com/duckdb/duckdb/tree/' + DUCK_REVISION + '/' + source, license))

    # Match the Dockerfile's individual COPY operations. Keep validation of
    # actual shipped files and ownership separate from the reviewed inventory.
    pg = os.environ['PG_MAJOR']
    roots = [(Path(f'/install/usr/lib/postgresql/{pg}/lib/pg_duckdb.so'), Path('lib/pg_duckdb.so')),
             (Path(f'/install/usr/share/postgresql/{pg}/extension'), Path('share/extension')),
             (Path('/system'), Path('system')), (Path('/licenses'), Path('licenses'))]
    payload = []
    for source, destination in roots:
        for path in sorted(source.rglob('*')) if source.is_dir() else [source]:
            if path.is_file():
                target = destination / path.relative_to(source) if source.is_dir() else destination
                payload.append(dict(path=str(target), source=str(path).lstrip('/'),
                                    sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    (BUILD / 'universe-evidence.json').write_text(json.dumps(dict(components=components, payload=payload), indent=2) + '\n')


if __name__ == '__main__':
    main()

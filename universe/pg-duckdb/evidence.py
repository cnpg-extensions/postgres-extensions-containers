"""Record the reviewed package inventory for the shared SBOM hook."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import shutil
from urllib.parse import urlencode

BUILD = Path('/build')
DUCK = BUILD / 'third_party/duckdb'
PG_REVISION = '8756099e267c47f0b86c24de4cf995327f1f4279'
DUCK_REVISION = 'd54cbbe3df17e8e5ce68312f483b4155836112aa'

# Debian unstable package names; versions are the upstream code actually built,
# without Debian revisions or a claim that Debian patches were applied.
# binary name: (Debian source name, compiled version, vendor path, common licenses)
DEBIAN_PACKAGES = {
    'libduckdb2.0': ('duckdb', '2.0.0', '', ('Apache-2.0', 'GPL-2')),
    'libbrotli1': ('brotli', '1.1.0', 'third_party/brotli', ()),
    'liblz4-1': ('lz4', '1.9.4', 'third_party/lz4', ('GPL-2',)),
    'libmbedcrypto16': ('mbedtls', '3.6.7', 'third_party/mbedtls', ('Apache-2.0', 'GPL-2')),
    # The default Clang build selects SNAPPY_NEW_VERSION (1.2.1).
    'libsnappy1v5': ('snappy', '1.2.1', 'third_party/snappy', ()),
    'libyyjson0': ('yyjson', '0.9.0', 'third_party/yyjson', ('Apache-2.0',)),
    'libzstd1': ('libzstd', '1.5.6', 'third_party/zstd', ('GPL-2',)),
    'libxxhash0': ('xxhash', '0.6.2', 'third_party/zstd', ('GPL-2',)),
}


def debian_purl(name, source, version, arch):
    qualifiers = urlencode(dict(arch=arch, distro='debian-unstable', upstream=source))
    return 'pkg:deb/debian/' + name + '@' + version + '?' + qualifiers


def package(name, version, repo, revision, parent, purl=None, debian=None,
            source_url=None, license=None, root=Path('/')):
    notice = Path('licenses') / name / 'copyright'
    (root / notice).read_text()  # The maintained copyright file is required.
    notices = sorted(p for p in (root / notice.parent).rglob('*') if p.is_file())
    text = '\n\n'.join(p.read_text() for p in notices)
    return dict(name=name, version=version, repository=repo, revision=revision,
                parent=parent, purl=purl, debian_package=debian, source_url=source_url,
                notices=[str(p.relative_to(root)) for p in notices], license_text=text,
                license=license or 'LicenseRef-Universe-' + hashlib.sha256(text.encode()).hexdigest()[:24],
                copyright='NOASSERTION')


def main():
    for directory, expected in [(BUILD, PG_REVISION), (DUCK, DUCK_REVISION)]:
        actual = subprocess.check_output(['git', '-C', str(directory), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != expected:
            raise ValueError('Review the static package inventory and copyright files for updated source: ' + str(directory))
    components = [package('pg_duckdb', '1.2.0', 'https://github.com/duckdb/pg_duckdb',
                          PG_REVISION, None, 'pkg:github/duckdb/pg_duckdb@v1.2.0')]
    for name, (source, version, vendor, common_licenses) in DEBIAN_PACKAGES.items():
        for license_name in common_licenses:
            shutil.copyfile('/usr/share/common-licenses/' + license_name,
                            '/licenses/' + name + '/' + license_name)
        parent = 'pg_duckdb' if name == 'libduckdb2.0' else 'libzstd1' if name == 'libxxhash0' else 'libduckdb2.0'
        components.append(package(name, version, 'https://github.com/duckdb/duckdb',
            DUCK_REVISION + (':' + vendor if vendor else ''), parent,
            debian_purl(name, source, version, os.environ['TARGETARCH']), debian=name,
            source_url='https://github.com/duckdb/duckdb/tree/' + DUCK_REVISION + ('/' + vendor if vendor else '')))

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

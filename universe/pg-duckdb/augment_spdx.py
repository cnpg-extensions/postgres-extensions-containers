"""Shared cnpg-sbom-generator augment_spdx API v1; no intermediate manifest."""
from copy import deepcopy
import hashlib
from pathlib import Path
from urllib.parse import urlencode

PG_REVISION = '8756099e267c47f0b86c24de4cf995327f1f4279'
DUCK_REVISION = 'd54cbbe3df17e8e5ce68312f483b4155836112aa'

# Debian unstable package names; versions are the upstream code actually built,
# without Debian revisions or a claim that Debian patches were applied.
# binary name: (Debian source name, compiled version, vendor path)
DEBIAN_PACKAGES = {
    'libduckdb2.0': ('duckdb', '2.0.0', ''),
    'libbrotli1': ('brotli', '1.1.0', 'third_party/brotli'),
    'liblz4-1': ('lz4', '1.9.4', 'third_party/lz4'),
    'libmbedcrypto16': ('mbedtls', '3.6.7', 'third_party/mbedtls'),
    # The default Clang build selects SNAPPY_NEW_VERSION (1.2.1).
    'libsnappy1v5': ('snappy', '1.2.1', 'third_party/snappy'),
    'libyyjson0': ('yyjson', '0.9.0', 'third_party/yyjson'),
    'libzstd1': ('libzstd', '1.5.6', 'third_party/zstd'),
    'libxxhash0': ('xxhash', '0.6.2', 'third_party/zstd'),
}


def debian_purl(name, source, version, arch):
    qualifiers = urlencode(dict(arch=arch, distro='debian-unstable', upstream=source))
    return 'pkg:deb/debian/' + name + '@' + version + '?' + qualifiers



def check_sources():
    """Run in the builder before export; inventory changes require review."""
    import subprocess
    for directory, expected in [('/build', PG_REVISION),
                                ('/build/third_party/duckdb', DUCK_REVISION)]:
        actual = subprocess.check_output(
            ['git', '-C', directory, 'rev-parse', 'HEAD'], text=True).strip()
        if actual != expected:
            raise ValueError('Review the static package inventory and copyright files for updated source: ' + directory)


def augment_spdx(document, context):
    if context.api_version != 1:
        raise ValueError('unsupported hook API')
    builder, final = Path(context.builder_path), Path(context.final_path)
    result = deepcopy(document)
    files = {p['fileName'].removeprefix('./'): p for p in result['files']}
    # Bind executable/runtime payloads to the shared inventory. Docker COPY
    # handles notice staging; read those directly from the final image below.
    libraries = list((builder / 'install/usr/lib/postgresql').glob('*/lib/pg_duckdb.so'))
    if len(libraries) != 1:
        raise ValueError('expected one installed pg_duckdb library')
    pg = libraries[0].parent.parent.name
    roots = [(libraries[0], Path('lib/pg_duckdb.so')),
             (builder / f'install/usr/share/postgresql/{pg}/extension', Path('share/extension')),
             (builder / 'system', Path('system'))]
    for source, destination in roots:
        for path in sorted(source.rglob('*')) if source.is_dir() else [source]:
            if not path.is_file():
                continue
            target = str(destination / path.relative_to(source) if source.is_dir() else destination)
            if target not in files:
                raise ValueError('payload missing from shared inventory: ' + target)
            data = (final / target).read_bytes()
            if path.read_bytes() != data:
                raise ValueError('builder/final payload mismatch: ' + target)
            if not any(c['algorithm'] == 'SHA256' and c['checksumValue'].lower() == hashlib.sha256(data).hexdigest()
                       for c in files[target].get('checksums', [])):
                raise ValueError('shared inventory hash mismatch: ' + target)
    # Copied Debian copyright/common-license files can make the shared scan
    # select builder packages that contribute no binary here. Replace only
    # those notice-only records with the explicit compiled-version mappings.
    mapped_notices = {record['SPDXID'] for path, record in files.items()
                      if len(Path(path).parts) >= 3 and Path(path).parts[0] == 'licenses'
                      and Path(path).parts[1] in DEBIAN_PACKAGES}
    replaced = set()
    for package in result['packages']:
        owned = {r['relatedSpdxElement'] for r in result.get('relationships', [])
                 if r['spdxElementId'] == package['SPDXID'] and r['relationshipType'] == 'CONTAINS'}
        if owned and owned <= mapped_notices:
            replaced.add(package['SPDXID'])
    result['packages'] = [p for p in result['packages'] if p['SPDXID'] not in replaced]
    result['relationships'] = [r for r in result.get('relationships', [])
                              if r['spdxElementId'] not in replaced and r['relatedSpdxElement'] not in replaced]
    scope = ('Package inventory follows Debian DuckDB 2.0.0+dfsg2 package boundaries. '
             'Internal bundled code and generated data are covered by their containing '
             'package and original notice files, not separate package records. '
             'Eight source-built components use Debian package identities for scanner '
             'matching, with compiled upstream versions and no Debian revision. '
             'These are not dpkg-installed or Debian-patched binaries. This is not an exhaustive '
             'embedded-component inventory.')
    result['comment'] = (result.get('comment', '') + '\n' + scope).strip()
    relationships = result['relationships']

    def relate(parent, kind, child):
        relationships.append(dict(spdxElementId=parent, relationshipType=kind, relatedSpdxElement=child))

    def add_package(name, version, purl, source_url, parent, debian=False):
        notice_dir = final / 'licenses' / name
        notices = sorted(p for p in notice_dir.rglob('*') if p.is_file())
        text = '\n\n'.join(p.read_text() for p in notices)
        license_id = 'LicenseRef-Universe-' + hashlib.sha256(text.encode()).hexdigest()[:24]
        sid = 'SPDXRef-Universe-' + hashlib.sha256(purl.encode()).hexdigest()[:24]
        source_info = 'Selected source: ' + source_url
        if debian:
            source_info += ('; Debian scanner mapping: ' + name
                            + '; compiled upstream version: ' + version
                            + '; built from upstream source, not installed by dpkg; no Debian patch-level claim')
        result['packages'].append(dict(
            SPDXID=sid, name=name, versionInfo=version, downloadLocation=source_url,
            filesAnalyzed=False, licenseConcluded=license_id, licenseDeclared=license_id,
            copyrightText='NOASSERTION', sourceInfo=source_info,
            externalRefs=[dict(referenceCategory='PACKAGE-MANAGER', referenceType='purl', referenceLocator=purl)]))
        extracted = result.setdefault('hasExtractedLicensingInfos', [])
        if not any(item['licenseId'] == license_id for item in extracted):
            extracted.append(dict(licenseId=license_id, extractedText=text, name=name + ' bundled notices'))
        for notice in notices:
            relate(sid, 'DISTRIBUTION_ARTIFACT', files[str(notice.relative_to(final))]['SPDXID'])
        relate(parent, 'DESCRIBES' if parent == result['SPDXID'] else 'DEPENDS_ON', sid)
        return sid

    pg_id = add_package('pg_duckdb', '1.2.0', 'pkg:github/duckdb/pg_duckdb@v1.2.0',
                        'https://github.com/duckdb/pg_duckdb/tree/' + PG_REVISION, result['SPDXID'])
    ids = {}
    arch = {'linux/amd64': 'amd64', 'linux/arm64': 'arm64'}[context.platform]
    for name, (source, version, vendor) in DEBIAN_PACKAGES.items():
        parent = pg_id if name == 'libduckdb2.0' else ids['libzstd1' if name == 'libxxhash0' else 'libduckdb2.0']
        ids[name] = add_package(name, version, debian_purl(name, source, version, arch),
            'https://github.com/duckdb/duckdb/tree/' + DUCK_REVISION + ('/' + vendor if vendor else ''),
            parent, debian=True)
    relate(files['lib/pg_duckdb.so']['SPDXID'], 'GENERATED_FROM', pg_id)
    for path, file in files.items():
        if Path(path).name == 'libduckdb.so' or Path(path).name.startswith('libduckdb.so.'):
            relate(file['SPDXID'], 'GENERATED_FROM', ids['libduckdb2.0'])
    return result


if __name__ == '__main__':
    check_sources()

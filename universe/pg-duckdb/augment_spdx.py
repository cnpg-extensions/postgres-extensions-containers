"""Shared cnpg-sbom-generator augment_spdx API v1; no intermediate manifest."""
from copy import deepcopy
import hashlib
from pathlib import Path
from urllib.parse import urlencode

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


def augment_spdx(document, context):
    if context.api_version != 1:
        raise ValueError('unsupported hook API')
    final = Path(context.final_path)
    result = deepcopy(document)
    files = {p['fileName'].removeprefix('./'): p for p in result['files']}
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
    scope = ('Uses Debian DuckDB package boundaries, not an exhaustive bundled inventory. '
             'Debian identities map source-built upstream versions for scanning; '
             'they do not imply dpkg installation or Debian patches.')
    result['comment'] = (result.get('comment', '') + '\n' + scope).strip()
    relationships = result['relationships']

    def relate(parent, kind, child):
        relationships.append(dict(spdxElementId=parent, relationshipType=kind, relatedSpdxElement=child))

    def add_package(name, version, purl, source_url, source_info):
        notice_dir = final / 'licenses' / name
        notices = sorted(p for p in notice_dir.rglob('*') if p.is_file())
        text = '\n\n'.join(p.read_text() for p in notices)
        license_id = 'LicenseRef-Notices-' + hashlib.sha256(text.encode()).hexdigest()[:24]
        sid = 'SPDXRef-Source-' + name.replace('_', '-')
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
        return sid

    pg_url = 'https://github.com/duckdb/pg_duckdb/tree/v1.2.0'
    pg_id = add_package('pg_duckdb', '1.2.0', 'pkg:github/duckdb/pg_duckdb@v1.2.0',
                        pg_url, 'Selected source: ' + pg_url)
    ids = {}
    arch = {'linux/amd64': 'amd64', 'linux/arm64': 'arm64'}[context.platform]
    for name, (source, version, vendor) in DEBIAN_PACKAGES.items():
        url = 'https://github.com/duckdb/duckdb/tree/v' + DEBIAN_PACKAGES['libduckdb2.0'][1] + ('/' + vendor if vendor else '')
        source_info = ('Selected source: ' + url + '; Debian scanner mapping: ' + name
                       + '; compiled upstream version: ' + version
                       + '; built from upstream source, not installed by dpkg; no Debian patch-level claim')
        ids[name] = add_package(name, version, debian_purl(name, source, version, arch), url, source_info)

    relate(result['SPDXID'], 'DESCRIBES', pg_id)
    relate(pg_id, 'DEPENDS_ON', ids['libduckdb2.0'])
    relate(ids['libzstd1'], 'DEPENDS_ON', ids['libxxhash0'])
    for name in DEBIAN_PACKAGES:
        if name not in ('libduckdb2.0', 'libxxhash0'):
            relate(ids['libduckdb2.0'], 'DEPENDS_ON', ids[name])
    relate(files['lib/pg_duckdb.so']['SPDXID'], 'GENERATED_FROM', pg_id)
    relate(files['system/libduckdb.so']['SPDXID'], 'GENERATED_FROM', ids['libduckdb2.0'])
    return result

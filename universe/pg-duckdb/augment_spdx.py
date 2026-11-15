"""Shared cnpg-sbom-generator augment_spdx API v1; no intermediate manifest."""
from copy import deepcopy
import hashlib
import re
from pathlib import Path
from urllib.parse import urlencode

# Debian unstable package names; versions are the upstream code actually built,
# without Debian revisions or a claim that Debian patches were applied.
# binary name: (Debian source name, vendor path)
DEBIAN_PACKAGES = {
    'libduckdb2.0': ('duckdb', ''),
    'libbrotli1': ('brotli', 'third_party/brotli'),
    'liblz4-1': ('lz4', 'third_party/lz4'),
    'libmbedcrypto16': ('mbedtls', 'third_party/mbedtls'),
    'libsnappy1v5': ('snappy', 'third_party/snappy'),
    'libyyjson0': ('yyjson', 'third_party/yyjson'),
    'libzstd1': ('libzstd', 'third_party/zstd'),
    'libxxhash0': ('xxhash', 'third_party/zstd'),
}


def read_version(path, pattern):
    matches = re.findall(pattern, path.read_text(), re.MULTILINE)
    if len(matches) != 1:
        raise ValueError('expected one version in ' + str(path))
    return matches[0]


def header_version(path, prefix, parts=('MAJOR', 'MINOR', 'PATCH')):
    return '.'.join(read_version(path, r'^#define\s+' + prefix + part + r'\s+(\d+)\b')
                    for part in parts)


def source_versions(builder):
    build = Path(builder) / 'build'
    duck = build / 'third_party/duckdb'
    vendor = duck / 'third_party'
    return {
        'pg_duckdb': read_version(build / 'pg_duckdb.control', r"^default_version\s*=\s*'([^']+)'"),
        'libduckdb2.0': read_version(duck / 'build/release/DuckDBConfigVersion.cmake',
                                   r'^set\(PACKAGE_VERSION "v?([^"]+)"\)'),
        'libbrotli1': header_version(vendor / 'brotli/common/version.h', 'BROTLI_VERSION_'),
        'liblz4-1': header_version(vendor / 'lz4/lz4.hpp', 'LZ4_VERSION_', ('MAJOR', 'MINOR', 'RELEASE')),
        'libmbedcrypto16': header_version(vendor / 'mbedtls/include/mbedtls/build_info.h', 'MBEDTLS_VERSION_'),
        # Preprocessed by the build compiler: Snappy selects Clang/GCC variants.
        'libsnappy1v5': header_version(build / 'snappy-version.h', 'SNAPPY_', ('MAJOR', 'MINOR', 'PATCHLEVEL')),
        'libyyjson0': header_version(vendor / 'yyjson/include/yyjson.hpp', 'YYJSON_VERSION_'),
        'libzstd1': header_version(vendor / 'zstd/include/zstd.h', 'ZSTD_VERSION_', ('MAJOR', 'MINOR', 'RELEASE')),
        'libxxhash0': header_version(vendor / 'zstd/include/zstd/common/xxhash.hpp', 'XXH_VERSION_', ('MAJOR', 'MINOR', 'RELEASE')),
    }


def debian_purl(name, source, version, arch):
    qualifiers = urlencode(dict(arch=arch, distro='debian-unstable', upstream=source))
    return 'pkg:deb/debian/' + name + '@' + version + '?' + qualifiers


def augment_spdx(document, context):
    if context.api_version != 1:
        raise ValueError('unsupported hook API')
    final = Path(context.final_path)
    versions = source_versions(context.builder_path)
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

    def add_package(name, version, purl, source_url):
        notice_dir = final / 'licenses' / name
        notices = sorted(p for p in notice_dir.rglob('*') if p.is_file())
        text = '\n\n'.join(p.read_text() for p in notices)
        license_id = 'LicenseRef-Notices-' + hashlib.sha256(text.encode()).hexdigest()[:24]
        sid = 'SPDXRef-Source-' + name.replace('_', '-')
        result['packages'].append(dict(
            SPDXID=sid, name=name, versionInfo=version, downloadLocation=source_url,
            filesAnalyzed=False, licenseConcluded=license_id, licenseDeclared=license_id,
            copyrightText='NOASSERTION',
            externalRefs=[dict(referenceCategory='PACKAGE-MANAGER', referenceType='purl', referenceLocator=purl)]))
        extracted = result.setdefault('hasExtractedLicensingInfos', [])
        if not any(item['licenseId'] == license_id for item in extracted):
            extracted.append(dict(licenseId=license_id, extractedText=text, name=name + ' bundled notices'))
        for notice in notices:
            relate(sid, 'DISTRIBUTION_ARTIFACT', files[str(notice.relative_to(final))]['SPDXID'])
        return sid

    pg_version = versions['pg_duckdb']
    pg_id = add_package('pg_duckdb', pg_version, 'pkg:github/duckdb/pg_duckdb@v' + pg_version,
                        'https://github.com/duckdb/pg_duckdb/tree/v' + pg_version)
    ids = {}
    arch = {'linux/amd64': 'amd64', 'linux/arm64': 'arm64'}[context.platform]
    for name, (source, vendor) in DEBIAN_PACKAGES.items():
        version = versions[name]
        url = 'https://github.com/duckdb/duckdb/tree/v' + versions['libduckdb2.0'] + ('/' + vendor if vendor else '')
        ids[name] = add_package(name, version, debian_purl(name, source, version, arch), url)

    relate(result['SPDXID'], 'DESCRIBES', pg_id)
    relate(pg_id, 'DEPENDS_ON', ids['libduckdb2.0'])
    relate(ids['libzstd1'], 'DEPENDS_ON', ids['libxxhash0'])
    for name in DEBIAN_PACKAGES:
        if name not in ('libduckdb2.0', 'libxxhash0'):
            relate(ids['libduckdb2.0'], 'DEPENDS_ON', ids[name])
    relate(files['lib/pg_duckdb.so']['SPDXID'], 'GENERATED_FROM', pg_id)
    relate(files['system/libduckdb.so']['SPDXID'], 'GENERATED_FROM', ids['libduckdb2.0'])
    return result

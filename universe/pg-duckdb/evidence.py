"""Stage runtime closure and source evidence, without composing an SBOM."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import shlex
import urllib.request

BUILD = Path('/build')
LICENSES = Path('/licenses')
DUCK = BUILD / 'third_party/duckdb'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


# Version extraction is needed only for separately reported libraries.
VENDORS = {
    'yyjson': ('ibireme/yyjson', 'include/yyjson.hpp', ('YYJSON_VERSION_STRING',)),
    'lz4': ('lz4/lz4', 'lz4.hpp', ('LZ4_VERSION_MAJOR', 'LZ4_VERSION_MINOR', 'LZ4_VERSION_RELEASE')),
    'zstd': ('facebook/zstd', 'include/zstd.h', ('ZSTD_VERSION_MAJOR', 'ZSTD_VERSION_MINOR', 'ZSTD_VERSION_RELEASE')),
    'brotli': ('google/brotli', 'common/version.h', ('BROTLI_VERSION_MAJOR', 'BROTLI_VERSION_MINOR', 'BROTLI_VERSION_PATCH')),
}


# Debian DuckDB 2.0.0+dfsg2 uses these as separate system-library packages.
# This is an SBOM reporting boundary, not a claim that our copies came from dpkg.
DEBIAN_LIBRARY_PACKAGES = {
    'yyjson': 'libyyjson0', 'lz4': 'liblz4-1', 'zstd': 'libzstd1',
    'brotli': 'libbrotli1', 'mbedtls': 'libmbedcrypto16',
    'snappy': 'libsnappy1v5', 'xxhash': 'libxxhash0',
}


def runtime_inputs(builddir):
    # Follow only the shipped shared library's build graph, excluding loadable
    # extensions that upstream builds but does not install into its Docker image.
    targets = ['src/libduckdb.so']
    inputs = subprocess.check_output(['ninja', '-C', str(builddir), '-t', 'inputs', *targets], text=True).splitlines()
    sources = set(inputs)
    objects = set(targets)
    selected = set(inputs)
    for c in json.loads((builddir / 'compile_commands.json').read_text()):
        args = c.get('arguments') or shlex.split(c['command'])
        output = args[args.index('-o') + 1]
        relative = os.path.relpath(Path(c['directory']) / output, builddir)
        if c['file'] in sources:
            objects.add(relative)
            selected.add(str(Path(c['file']).resolve()))
    deps = subprocess.check_output(['ninja', '-C', str(builddir), '-t', 'deps'], text=True)
    for block in deps.split('\n\n'):
        lines = block.splitlines()
        if lines and lines[0].split(': #deps')[0] in objects:
            selected.update(str((builddir / line.strip()).resolve()) for line in lines[1:] if line.strip())
    return '\n'.join(sorted(selected))


def vendor_identity(directory):
    if directory.name == 'mbedtls':
        version = (directory / 'VERSION').read_text().strip()
        return version, 'pkg:github/Mbed-TLS/mbedtls@' + version
    if directory.name == 'snappy':
        # This snapshot has compiler-dependent version macros; retain its source path.
        return None, None
    repo, filename, macros = VENDORS[directory.name]
    text = (directory / filename).read_text()
    version = '.'.join(re.search(r'^#define\s+' + macro + r'\s+"?([0-9.]+)', text, re.M)[1]
                       for macro in macros)
    return version, 'pkg:github/' + repo + '@' + version


def source_notices(text):
    # Skip quoted strings and retain complete legal comment blocks anywhere in
    # the file, including notices after banners/includes and amalgamated code.
    tokens = re.finditer(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|'''
                         r'(/\*[\s\S]*?\*/|//[^\n]*(?:\n[ \t]*//[^\n]*)*)', text)
    return '\n\n'.join(dict.fromkeys(m[1] for m in tokens if m[1] and
        re.search(r'copyright|licen[sc]e|redistribution|public[\s*]+domain', m[1], re.I)))


def collect_notices(directory, paths, destination):
    notices = []
    for path in sorted(set(paths)):
        if not path.is_file():
            continue
        target = destination / path.relative_to(directory)
        if re.match(r'^(LICENSE|COPYING|NOTICE|COPYRIGHT)', path.name, re.I):
            copy(path, target)
        elif path.suffix in {'.h', '.hpp', '.c', '.cpp', '.cc'}:
            text = source_notices(path.read_text(errors='replace'))
            if not text:
                continue
            target = target.with_name(target.name + '.notice')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text + '\n')
        else:
            continue
        notices.append(target)
    return notices


def adjacent_notices(directory, sources):
    # Source files outside third_party may have their own nested LICENSE files.
    paths = set(sources)
    for source in sources:
        parent = source.parent
        while parent.is_relative_to(directory):
            paths.update(p for p in parent.iterdir() if p.is_file() and
                         re.match(r'^(LICENSE|COPYING|NOTICE|COPYRIGHT)', p.name, re.I))
            if parent == directory:
                break
            parent = parent.parent
    return paths


def license_evidence(text):
    # Composite/nonstandard notices retain their complete terms as LicenseRefs.
    normalized = ' '.join(text.split())
    if text.count('UNICODE LICENSE V3') == 1 and 'Third-Party Software Licenses' not in text:
        expression = 'Unicode-3.0'
    elif ('Unicode data license' in text or 'UNICODE LICENSE' in text
            or sum(marker in normalized for marker in [
                'Permission is hereby granted, free of charge', 'Apache License',
                'Redistribution and use in source and binary forms',
                'Boost Software License', 'This software is provided']) > 1):
        expression = 'LicenseRef-Universe-' + hashlib.sha256(text.encode()).hexdigest()[:24]
    elif 'Permission is hereby granted, free of charge' in normalized and 'THE SOFTWARE IS PROVIDED' in normalized:
        expression = 'MIT'
    elif 'Apache License' in normalized and 'Version 2.0' in normalized and 'GPL' not in text:
        expression = 'Apache-2.0'
    elif 'Redistribution and use in source and binary forms' in normalized:
        expression = 'BSD-3-Clause' if 'Neither the name' in normalized else 'BSD-2-Clause'
    elif 'Boost Software License, Version 1.0' in text:
        expression = 'BSL-1.0'
    else:
        expression = 'LicenseRef-Universe-' + hashlib.sha256(text.encode()).hexdigest()[:24]
    copyright = '\n'.join(line.strip() for line in text.splitlines()
                          if re.search(r'copyright.*(?:[0-9]|©|\(c\))', line, re.I))
    return expression, copyright or 'NOASSERTION'


def main():
    def revision(directory):
        return subprocess.check_output(['git', '-C', str(directory), 'rev-parse', 'HEAD'], text=True).strip()

    pg_revision, duck_revision = revision(BUILD), revision(DUCK)
    if pg_revision != '8756099e267c47f0b86c24de4cf995327f1f4279':
        raise ValueError('Review source licenses and supplemental notice URLs for updated source')
    pg = os.environ['PG_MAJOR']
    selected = {Path(p) for p in runtime_inputs(DUCK / 'build/release').splitlines()
                if Path(p).is_absolute() and Path(p).is_file()}
    components = []

    def component(name, version, repo, rev, parent, purl=None):
        record = dict(name=name, version=version, repository=repo, revision=rev,
                      parent=parent, purl=purl, notices=[],
                      debian_package=DEBIAN_LIBRARY_PACKAGES.get(name))
        components.append(record)
        return record

    def collect(owner, directory, paths):
        owner['notices'].extend(collect_notices(directory, paths, LICENSES / owner['name']))

    def download(owner, relative, url):
        target = LICENSES / owner['name'] / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url) as response:
            target.write_bytes(response.read())
        owner['notices'].append(target)
        owner.setdefault('notice_sources', {})[str(target.relative_to(LICENSES.parent))] = url

    version = os.environ['EXT_VERSION']
    pg_owner = component('pg_duckdb', version.removeprefix('v'),
                         'https://github.com/duckdb/pg_duckdb', pg_revision, None,
                         'pkg:github/duckdb/pg_duckdb@' + version)
    collect(pg_owner, BUILD, list(BUILD.iterdir()) + list((BUILD / 'src/vendor').rglob('*')))
    target = LICENSES / 'pg_duckdb/PostgreSQL/copyright'
    copy(Path(f'/usr/share/doc/postgresql-server-dev-{pg}/copyright'), target)
    pg_owner['notices'].append(target)

    duckver = re.search(r'^DUCKDB_VERSION\s*=\s*(\S+)', (BUILD / 'Makefile').read_text(), re.M)[1]
    duck_owner = component('duckdb', duckver.removeprefix('v'), 'https://github.com/duckdb/duckdb',
                           duck_revision, 'pg_duckdb', 'pkg:github/duckdb/duckdb@' + duck_revision)
    collect(duck_owner, DUCK, DUCK.iterdir())
    # Keep internal code's notices directly under DuckDB, without constructing
    # package identities or versions that the public SBOM does not expose.
    for directory in sorted((DUCK / 'third_party').iterdir()):
        if not directory.is_dir() or not any(p.is_relative_to(directory) for p in selected):
            continue
        owner = duck_owner
        if directory.name in DEBIAN_LIBRARY_PACKAGES:
            version, purl = vendor_identity(directory)
            repo = 'https://github.com/' + purl.removeprefix('pkg:github/').split('@')[0] if purl else 'https://github.com/duckdb/duckdb'
            owner = component(directory.name, version, repo, duck_revision + ':third_party/' + directory.name,
                              'duckdb', purl)
            owner['source_url'] = 'https://github.com/duckdb/duckdb/tree/' + duck_revision + '/third_party/' + directory.name
        collect(owner, DUCK, directory.rglob('*'))

    sources = {p for p in selected if p.is_relative_to(DUCK / 'src') or p.is_relative_to(DUCK / 'extension')}
    collect(duck_owner, DUCK, adjacent_notices(DUCK, sources))
    # These selected sources refer to upstream terms/NOTICE files absent from
    # the vendored tree. The notice revisions are attribution sources, not claims
    # that the embedded code is exactly those upstream releases.
    supplemental = [
        ('src/common/checksum.cpp', 'robin-hood-hashing/LICENSE',
         'https://raw.githubusercontent.com/martinus/robin-hood-hashing/3.11.5/LICENSE'),
        ('src/include/duckdb/common/adbc/adbc.h', 'adbc/NOTICE.txt',
         'https://raw.githubusercontent.com/apache/arrow-adbc/89fe37cf2050202685398cb50502e31a4d293306/NOTICE.txt'),
        ('src/include/duckdb/common/arrow/nanoarrow/nanoarrow.h', 'nanoarrow/NOTICE.txt',
         'https://raw.githubusercontent.com/apache/arrow-nanoarrow/ee22361fa22581e9b8e26cc0c0a37134ffdcfba2/NOTICE.txt'),
        ('src/include/duckdb/common/adbc/adbc.h', 'adbc/LICENSE.txt',
         'https://raw.githubusercontent.com/apache/arrow-adbc/89fe37cf2050202685398cb50502e31a4d293306/LICENSE.txt'),
    ]
    for source, target, url in supplemental:
        if DUCK / source in selected:
            download(duck_owner, target, url)

    xxhash = DUCK / 'third_party/zstd/include/zstd/common/xxhash.hpp'
    xxhash_source = DUCK / 'third_party/zstd/common/xxhash.cpp'
    if xxhash in selected or xxhash_source in selected:
        version = '.'.join(re.search(r'^#define\s+XXH_VERSION_' + part + r'\s+(\d+)', xxhash.read_text(), re.M)[1]
                           for part in ('MAJOR', 'MINOR', 'RELEASE'))
        owner = component('xxhash', version, 'https://github.com/Cyan4973/xxHash',
                          duck_revision + ':third_party/zstd', 'zstd', 'pkg:github/Cyan4973/xxHash@' + version)
        owner['source_url'] = 'https://github.com/duckdb/duckdb/blob/' + duck_revision + '/third_party/zstd/include/zstd/common/xxhash.hpp'
        collect(owner, DUCK, [xxhash, xxhash_source])

    icu = DUCK / 'extension/icu'
    if icu / 'datetime/generated/tz_data.cpp' in selected:
        download(duck_owner, 'tzdata/LICENSE',
                 'https://raw.githubusercontent.com/unicode-org/icu-data/6eac2f4d349d9f4a0825103bb41845d8e5ab7add/LICENSE')
    if icu / 'collation/generated/collation_data.cpp' in selected:
        version = re.search(r'CLDR release-([0-9.]+)', (icu / 'collation/generated/collation_data.cpp').read_text())[1]
        download(duck_owner, 'cldr/LICENSE', 'https://raw.githubusercontent.com/unicode-org/cldr/release-' + version + '/LICENSE')
        download(duck_owner, 'Unicode Character Database/LICENSE', 'https://www.unicode.org/license.txt')

    for owner in components:
        notices = sorted(set(owner['notices']))
        text = '\n\n'.join(p.read_text(errors='replace') for p in notices)
        owner['license'], owner['copyright'] = license_evidence(text)
        # Parent packages combine internal components with different terms.
        if owner['name'] in {'pg_duckdb', 'duckdb'}:
            owner['license'] = 'LicenseRef-Universe-' + hashlib.sha256(text.encode()).hexdigest()[:24]
        owner['license_text'] = text
        owner['notices'] = [str(p.relative_to(LICENSES.parent)) for p in notices]

    # Match the Dockerfile's individual COPY operations, without a staging /payload.
    roots = [(Path(f'/install/usr/lib/postgresql/{pg}/lib/pg_duckdb.so'), Path('lib/pg_duckdb.so')),
             (Path(f'/install/usr/share/postgresql/{pg}/extension'), Path('share/extension')),
             (Path('/system'), Path('system')), (LICENSES, Path('licenses'))]
    payload = []
    for source, destination in roots:
        for path in sorted(source.rglob('*')) if source.is_dir() else [source]:
            if path.is_file():
                target = destination / path.relative_to(source) if source.is_dir() else destination
                payload.append(dict(path=str(target), source=str(path).lstrip('/'), sha256=digest(path)))
    (BUILD / 'universe-evidence.json').write_text(json.dumps(dict(components=components, payload=payload), indent=2) + '\n')


if __name__ == '__main__':
    main()

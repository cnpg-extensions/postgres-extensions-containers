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
PAYLOAD = Path('/payload')
DUCK = BUILD / 'third_party/duckdb'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


# Paths and macro names are source interfaces, never a release-to-version table.
VENDORS = {
    'fmt': ('fmt', 'fmtlib/fmt', 'include/fmt/core.h', ('FMT_VERSION',)),
    'yyjson': ('yyjson', 'ibireme/yyjson', 'include/yyjson.hpp', ('YYJSON_VERSION_STRING',)),
    'utf8proc': ('utf8proc', 'JuliaStrings/utf8proc', 'include/utf8proc.hpp', ('UTF8PROC_VERSION_MAJOR', 'UTF8PROC_VERSION_MINOR', 'UTF8PROC_VERSION_PATCH')),
    'miniz': ('miniz', 'richgel999/miniz', 'miniz.hpp', ('MZ_VERSION',)),
    'lz4': ('lz4', 'lz4/lz4', 'lz4.hpp', ('LZ4_VERSION_MAJOR', 'LZ4_VERSION_MINOR', 'LZ4_VERSION_RELEASE')),
    'zstd': ('zstd', 'facebook/zstd', 'include/zstd.h', ('ZSTD_VERSION_MAJOR', 'ZSTD_VERSION_MINOR', 'ZSTD_VERSION_RELEASE')),
    'brotli': ('brotli', 'google/brotli', 'common/version.h', ('BROTLI_VERSION_MAJOR', 'BROTLI_VERSION_MINOR', 'BROTLI_VERSION_PATCH')),
    'httplib': ('cpp-httplib', 'yhirose/cpp-httplib', 'httplib.hpp', ('CPPHTTPLIB_VERSION',)),
}


# Canonical projects without an unambiguous release macro in this snapshot.
# Keep the actual DuckDB revision/path rather than assigning an upstream tag.
SOURCE_NAMES = {
    'concurrentqueue': 'concurrentqueue', 'fast_float': 'fast_float',
    'fastpforlib': 'FastPFor', 'fsst': 'fsst',
    'hyperloglog': 'Redis HyperLogLog', 'jaro_winkler': 'JaroWinkler',
    'jemalloc': 'jemalloc', 'mbedtls': 'mbedtls', 'parquet': 'parquet-format',
    'pcg': 'pcg-cpp', 'pdqsort': 'pdqsort', 're2': 're2',
    'ska_sort': 'ska_sort', 'skiplist': 'skiplist', 'snappy': 'snappy',
    'tdigest': 't-digest', 'thrift': 'thrift', 'vergesort': 'vergesort',
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


def vendor_identity(directory, revision):
    if directory.name == 'miniz':
        text = (directory / 'miniz.hpp').read_text()
        version = re.match(r'/\* miniz\.c ([0-9.]+)', text)[1]
        return 'miniz', version, 'pkg:github/richgel999/miniz@' + version
    if directory.name == 'fsst':
        revision = re.search(r'@ commit ([0-9a-f]{40})', (directory / 'README.md').read_text())[1]
        return 'fsst', revision, 'pkg:github/cwida/fsst@' + revision
    if directory.name == 'mbedtls':
        version = (directory / 'VERSION').read_text().strip()
        return 'mbedtls', version, 'pkg:github/Mbed-TLS/mbedtls@' + version
    if directory.name not in VENDORS:
        return SOURCE_NAMES[directory.name], None, None
    name, repo, filename, macros = VENDORS[directory.name]
    text = (directory / filename).read_text()
    values = [re.search(r'^#define\s+' + macro + r'\s+"?([0-9.]+)', text, re.M)[1]
              for macro in macros]
    version = '.'.join(values)
    if macros == ('FMT_VERSION',):
        number = int(version)
        version = f'{number // 10000}.{number // 100 % 100}.{number % 100}'
    return name, version, 'pkg:github/' + repo + '@' + version


def license_evidence(text, name):
    # Composite/nonstandard notices retain their complete terms as LicenseRefs.
    normalized = ' '.join(text.split())
    if name == 'PostgreSQL':
        expression = 'LicenseRef-Universe-' + hashlib.sha256(text.encode()).hexdigest()[:24]
    elif text.count('UNICODE LICENSE V3') == 1 and 'Third-Party Software Licenses' not in text:
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
    builddir = DUCK / 'build/release'
    def revision(directory):
        return subprocess.check_output(['git', '-C', str(directory), 'rev-parse', 'HEAD'], text=True).strip()
    evidence = dict(repository='https://github.com/duckdb/pg_duckdb',
                    version=os.environ['EXT_VERSION'], revision=revision(BUILD),
                    duckdb_revision=revision(DUCK),
                    timestamp=os.environ['BUILD_TIMESTAMP'])
    pg = os.environ['PG_MAJOR']
    copy(Path(f'/install/usr/lib/postgresql/{pg}/lib/pg_duckdb.so'), PAYLOAD / 'lib/pg_duckdb.so')
    for path in Path(f'/install/usr/share/postgresql/{pg}/extension').glob('pg_duckdb*'):
        copy(path, PAYLOAD / 'share/extension' / path.name)
    # System libraries and their notices are staged by the shared shell helper.
    listing = subprocess.check_output(['ldd', str(PAYLOAD / 'lib/pg_duckdb.so')], text=True)
    assert 'not found' not in listing, listing
    components = []

    def component(name, version, repo, revision, directory, parent, purl=None):
        notices = []
        candidates = directory.iterdir() if name in {'pg_duckdb', 'duckdb'} else directory.rglob('*')
        for path in sorted(candidates):
            if path.is_file() and re.match(r'^(LICENSE|COPYING|NOTICE|COPYRIGHT)', path.name, re.I):
                target = PAYLOAD / 'licenses' / name / path.relative_to(directory)
                copy(path, target)
                notices.append(str(target.relative_to(PAYLOAD)))
        if name not in {'pg_duckdb', 'duckdb'}:
            for path in sorted(directory.rglob('*')):
                if path.suffix not in {'.h', '.hpp', '.c', '.cpp', '.cc'}:
                    continue
                text = path.read_text(errors='replace')
                # Preserve original leading source comments, without rewriting terms.
                header = re.match(r'\s*(/\*[\s\S]*?\*/|(?://[^\n]*\n)+)', text)
                if header and re.search(r'copyright|license|redistribution', header[0], re.I):
                    target = PAYLOAD / 'licenses' / name / (str(path.relative_to(directory)) + '.notice')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(header[0])
                    notices.append(str(target.relative_to(PAYLOAD)))
        notice_text = '\n\n'.join((PAYLOAD / notice).read_text(errors='replace') for notice in notices)
        license_id, copyright = license_evidence(notice_text, name) if notice_text else ('NOASSERTION', 'NOASSERTION')
        components.append(dict(license=license_id, copyright=copyright, license_text=notice_text,name=name, version=version, repository=repo, revision=revision,
                               parent=parent, purl=purl, notices=notices))

    component('pg_duckdb', evidence['version'].removeprefix('v'), evidence['repository'], evidence['revision'], BUILD, None,
              'pkg:github/duckdb/pg_duckdb@' + evidence['version'])
    component('PostgreSQL', None,
              evidence['repository'], evidence['revision'] + ':src/vendor',
              BUILD / 'src/vendor', 'pg_duckdb')
    # Vendored ruleutils and numeric/list headers carry PostgreSQL copyright.
    # Its development package supplies the original redistribution terms.
    notice = Path(f'/usr/share/doc/postgresql-server-dev-{pg}/copyright')
    target = PAYLOAD / 'licenses/PostgreSQL/copyright'
    copy(notice, target)
    components[-1]['notices'].append(str(target.relative_to(PAYLOAD)))
    components[-1]['license_text'] += '\n\n' + target.read_text()
    components[-1]['license'], components[-1]['copyright'] = license_evidence(components[-1]['license_text'], 'PostgreSQL')
    duckver = re.search(r'^DUCKDB_VERSION\s*=\s*(\S+)', (BUILD / 'Makefile').read_text(), re.M)[1]
    component('duckdb', duckver.removeprefix('v'), 'https://github.com/duckdb/duckdb', evidence['duckdb_revision'], DUCK, 'pg_duckdb',
              'pkg:github/duckdb/duckdb@' + evidence['duckdb_revision'])
    # Only library compilation units and their header dependencies: compiler/test
    # executables in the same build tree must not become shipped packages.
    selected = runtime_inputs(builddir)
    if evidence['revision'] != '8756099e267c47f0b86c24de4cf995327f1f4279':
        raise ValueError('Review vendor source identities and generated-data notice URLs for updated source')
    for root, revision, parent in [(DUCK, evidence['duckdb_revision'], 'duckdb')]:
        if not (root / 'third_party').is_dir():
            continue
        for directory in sorted((root / 'third_party').iterdir()):
            if not directory.is_dir() or str(directory) + '/' not in selected:
                continue
            name, version, purl = vendor_identity(directory, revision)
            repo = 'https://github.com/' + purl.split('/')[1] + '/' + purl.split('/')[2].split('@')[0] if purl else 'https://github.com/duckdb/duckdb'
            component(name, version, repo, revision + ':third_party/' + directory.name,
                      directory, parent, purl)
            components[-1]['source_url'] = ('https://github.com/duckdb/duckdb/tree/' + revision + '/third_party/' + directory.name)
    icu = DUCK / 'extension/icu'
    for filename, patterns in [
        ('datetime/generated/tz_data.cpp', [('tzdata', r'IANA release ([0-9]+[a-z]+)')]),
        ('collation/generated/collation_data.cpp', [('cldr', r'CLDR release-([0-9.]+)'), ('Unicode Character Database', r'UCD ([0-9.]+)')]),
    ]:
        path = icu / filename
        if str(path) not in selected:
            continue
        for name, pattern in patterns:
            version = re.search(pattern, path.read_text())[1]
            urls = {
                'tzdata': 'https://raw.githubusercontent.com/unicode-org/icu-data/6eac2f4d349d9f4a0825103bb41845d8e5ab7add/LICENSE',
                'cldr': 'https://raw.githubusercontent.com/unicode-org/cldr/release-' + version + '/LICENSE',
                'Unicode Character Database': 'https://www.unicode.org/license.txt',
            }
            url = urls[name]
            target = PAYLOAD / 'licenses' / name / 'LICENSE'
            target.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(url) as response:
                target.write_bytes(response.read())
            text = target.read_text()
            license_id, copyright = license_evidence(text, name)
            components.append(dict(name=name, version=version,
                repository=('https://github.com/unicode-org/icu-data' if name == 'tzdata' else
                            'https://github.com/unicode-org/cldr' if name == 'cldr' else
                            'https://www.unicode.org/Public/' + version + '/ucd/'),
                revision=evidence['duckdb_revision'] + ':extension/icu/' + filename,
                parent='duckdb', purl=None, notices=[str(target.relative_to(PAYLOAD))],
                license=license_id, copyright=copyright, license_text=text,
                notice_source=url, source_url='https://github.com/duckdb/duckdb/blob/' + evidence['duckdb_revision'] + '/extension/icu/' + filename))
    evidence['components'] = components
    evidence['payload'] = [dict(path=str(p.relative_to(PAYLOAD)), sha256=digest(p))
                           for p in sorted(PAYLOAD.rglob('*')) if p.is_file()]
    (BUILD / 'universe-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')


if __name__ == '__main__':
    main()

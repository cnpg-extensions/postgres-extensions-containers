"""Run Renovate itself against the current workspace, without GitHub writes."""
import json
import subprocess

from workflow import ROOT, discover


def check_renovate(output, pins):
    output.mkdir(parents=True)
    image = pins['images']['renovate']
    # Native-only container; read-only source. No token and no remote platform.
    common = ['docker', 'run', '--rm', '--platform', 'linux/amd64', '-v', str(ROOT) + ':/repo:ro', '-w', '/repo']
    with (output / 'validation.log').open('w') as log:
        subprocess.run([*common, '--entrypoint', 'renovate-config-validator', image, '/repo/renovate.json'], stdout=log, stderr=subprocess.STDOUT, check=True)
    with (output / 'extraction.jsonl').open('w') as log:
        subprocess.run([*common, '-e', 'LOG_LEVEL=debug', '-e', 'LOG_FORMAT=json', image, '--platform=local', '--dry-run=extract'], stdout=log, stderr=subprocess.STDOUT, check=True)
    entries = []
    for line in (output / 'extraction.jsonl').read_text().splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if 'packageFiles' in record:
            for files in record['packageFiles'].values():
                entries.extend(files)
    if not entries:
        raise ValueError('Renovate returned no extracted dependencies')
    sources = json.loads((ROOT / 'pgrx/dependencies/sources.json').read_text())
    for extension in discover():
        matched = [dep for entry in entries if entry.get('packageFile') == extension + '/metadata.hcl' for dep in entry.get('deps', [])]
        if not any(dep.get('depName') == sources[extension]['repository'] and dep.get('currentValue') == sources[extension]['version'] for dep in matched):
            raise ValueError('Renovate missed PGRX source: ' + extension)
    dependencies = {dep.get('depName') for entry in entries for dep in entry.get('deps', [])}
    expected = {tool['depName'] for tool in pins['tools'].values()} | {'rust-lang/rust', 'rust-lang/rustup', 'ghcr.io/cnpg-extensions/cnpg-sbom-generator', 'anchore/syft', 'spdx-tools'}
    if expected - dependencies:
        raise ValueError('Renovate missed execution pins: ' + str(expected - dependencies))
    with (output / 'updates.log').open('w') as log:
        subprocess.run([*common, '--entrypoint', '/usr/local/renovate/node', image, '/repo/pgrx/tests/renovate-update.mjs'], stdout=log, stderr=subprocess.STDOUT, check=True)
    (output / 'result.json').write_text(json.dumps({'success': True, 'dependencies': sorted(dependencies)}) + '\n')

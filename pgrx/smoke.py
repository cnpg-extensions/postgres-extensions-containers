"""CNPG smoke through shared Task/Dagger infrastructure, using the assembled digest."""
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

from workflow import ROOT, discover
from verify import validate_layout


def smoke(preparation, assembly, output, selector=None):
    fixtures = ROOT / 'pgrx/dependencies/fixtures'
    lock = json.loads((fixtures / 'lock.json').read_text())
    requested = selector or preparation['inputs'].get('cnpg_version') or lock['selector']
    if requested not in lock['operators']:
        raise ValueError('CNPG selector has no matching immutable fixture lock')
    target = preparation['targets'][assembly['target']]
    if target['pg_major'] != '18':
        raise ValueError('CNPG fixture currently supports PG18 only')
    lock['files']['operator']=lock['operators'][requested]
    lock['selector']=requested
    for name, entry in lock['files'].items():
        fixture_name='operator-'+requested if name=='operator' else name
        if hashlib.sha256((fixtures / (fixture_name + '.yaml')).read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('fixture checksum mismatch')
    pins = json.loads((ROOT / 'pgrx/dependencies/workflow-tools.json').read_text())
    # Reuse the shared tasks with a pinned toolbox and a separate test engine.
    kind = Path(shutil.which('kind')).resolve()
    kind_pin = pins['tools']['kind']['platforms']['amd64']
    if hashlib.sha256(kind.read_bytes()).hexdigest() != kind_pin['sha256']:
        raise ValueError('smoke requires the locked native Kind binary')
    toolbox = ('dagger core container from --address=' + pins['images']['runner'] +
               ' with-file --path=/usr/local/bin/kind --source=' + str(kind) +
               ' with-unix-socket --path=/var/run/docker.sock --source=/var/run/docker.sock' +
               ' with-env-variable --name=DOCKER_HOST --value=unix:///var/run/docker.sock' +
               ' with-env-variable --name=KIND_EXPERIMENTAL_DOCKER_NETWORK --value=pg-extensions-e2e')
    overrides = ['CNPG_RELEASE=' + requested,
                 'CNPG_MANIFEST_OVERRIDE=' + lock['files']['operator']['url'],
                 'CNPG_CATALOG_BOOKWORM_OVERRIDE=' + lock['files']['catalog-bookworm']['url'],
                 'CNPG_CATALOG_TRIXIE_OVERRIDE=' + lock['files']['catalog-trixie']['url'],
                 'KIND_TOOLBOX=' + toolbox, 'KIND_CLUSTER_NAME=pgrx-smoke',
                 'KIND_KUBECONFIG_FILTER=python3 ' + str(ROOT / 'pgrx/local/kubeconfig.py') + ' pgrx-smoke',
                 'DAGGER_ENGINE_NAME=dagger-engine-pgrx-smoke',
                 'DAGGER_ENGINE_IMAGE_OVERRIDE=' + pins['images']['dagger']]
    def task(name, *arguments):
        command = ['task', name, *overrides, *arguments]
        # Shared tasks pass kubeconfig through Dagger; suppress credential-bearing
        # progress lines before they reach act logs or retained validation artifacts.
        process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            if 'client-key-data' in line or 'client-certificate-data' in line:
                continue
            sys.stdout.write(line)
            sys.stdout.flush()
        if process.wait():
            raise subprocess.CalledProcessError(process.returncode, command)
    task('e2e:setup-env')
    kubeconfig = output / 'kubeconfig'
    task('e2e:export-kubeconfig', 'KUBECONFIG_PATH=' + str(kubeconfig), 'INTERNAL=true')
    namespace = 'pgrx-' + uuid.uuid4().hex[:16]
    # The shared Taskfile pins this same kubectl image; no host-path bind mounts.
    kubectl_image = 'alpine/kubectl:' + re.search(r'KUBECTL_VERSION: (\S+@sha256:[a-f0-9]{64})', (ROOT / 'Taskfile.yml').read_text()).group(1)
    container = subprocess.check_output(['docker', 'create', '--platform', 'linux/amd64',
        '--network', 'pg-extensions-e2e', '--entrypoint', 'sleep', kubectl_image, 'infinity'], text=True).strip()
    def kubectl(*args):
        return subprocess.check_output(['docker', 'exec', container, 'kubectl', '--kubeconfig=/tmp/config', *args], text=True)
    try:
        subprocess.run(['docker', 'cp', str(kubeconfig), container + ':/tmp/config'], check=True)
        subprocess.run(['docker', 'start', container], check=True)
        task('e2e:generate-values', 'TARGET=' + preparation['extension'], 'EXTENSION_IMAGE=' + assembly['image'])
        task('e2e:test', 'TARGET=' + preparation['extension'], 'KUBECONFIG_PATH=' + str(kubeconfig),
             'EXTRA_ARGS=--namespace,' + namespace + ',--skip-delete')
        pods = json.loads(kubectl('-n', namespace, 'get', 'pods', '-l', 'cnpg.io/podRole=instance', '-o', 'json'))['items']
        if len(pods) != 1:
            raise ValueError('expected one CNPG database instance')
        pod = pods[0]
        node = json.loads(kubectl('get', 'node', pod['spec']['nodeName'], '-o', 'json'))
        if node['status']['nodeInfo']['architecture'] != 'amd64':
            raise ValueError('smoke node is not native amd64')
        volumes = [v['image']['reference'] for v in pod['spec']['volumes'] if 'image' in v]
        if assembly['image'] not in volumes:
            raise ValueError('CNPG did not mount the assembled digest')
        def execute(*args):
            return kubectl('-n', namespace, 'exec', pod['metadata']['name'], '-c', 'postgres', '--', *args).strip()
        def sql(statement):
            return execute('psql', '-d', 'app', '-AtX', '-v', 'ON_ERROR_STOP=1', '-c', statement)
        graph = validate_layout(Path(assembly['_directory']) / 'layout', assembly['index_digest'], assembly['platforms'])
        child = graph['platforms']['linux/amd64']
        evidence = [json.loads(a['comment']) for a in child['spdx'].get('annotations', []) if a.get('annotator') == 'Tool: cnpg-pgrx-hook-v1']
        if len(evidence) != 1:
            raise ValueError('missing PGRX payload binding')
        metadata = discover()[preparation['extension']]
        # CNPG adds image-volume library paths when it starts PostgreSQL.
        # A kubectl exec process does not inherit that postmaster environment.
        postmaster_pid = execute('head', '-n', '1', sql('SHOW data_directory') + '/postmaster.pid')
        if not postmaster_pid.isdecimal():
            raise ValueError('invalid postmaster PID')
        library_path = execute('sh', '-ceu',
            'tr "\\000" "\\n" < "/proc/$1/environ" | sed -n "s/^LD_LIBRARY_PATH=//p"',
            'sh', postmaster_pid)
        checked = []
        for payload in evidence[0]['payload']:
            if payload['kind'] != 'library':
                continue
            paths = execute('find', '/extensions', '-name', Path(payload['final']).name, '-type', 'f').splitlines()
            if len(paths) != 1:
                raise ValueError('ambiguous mounted extension library')
            path = paths[0]
            if execute('sha256sum', path).split()[0] != payload['sha256']:
                raise ValueError('mounted payload differs from verified amd64 child')
            machine = execute('od', '-An', '-tu2', '-j18', '-N2', path).strip()
            if machine != '62':
                raise ValueError('mounted ELF is not amd64')
            libraries = execute('env', 'LD_LIBRARY_PATH=' + library_path, 'ldd', path)
            if 'not found' in libraries:
                raise ValueError('unresolved DT_NEEDED dependency: ' + libraries)
            checked.append({'path': path, 'sha256': payload['sha256'], 'elf_machine': machine, 'ldd': libraries})
        if not checked:
            raise ValueError('no mounted extension library checked')
        if sql("SELECT extversion FROM pg_extension WHERE extname = '" + metadata['sql_name'] + "'") != metadata['versions'][target['distro']][target['pg_major']]['sql']:
            raise ValueError('SQL extension version mismatch')
        preload = sql('SHOW shared_preload_libraries')
        for library in metadata['shared_preload_libraries']:
            if library not in preload:
                raise ValueError('missing shared preload library')
        durable = None
        if preparation['extension'] == 'pg-durable':
            if sql('SHOW pg_durable.database') != 'app':
                raise ValueError('pg_durable database configuration mismatch')
            for attempt in range(30):
                durable = sql("SELECT count(*) FROM pg_stat_activity WHERE datname = 'app' AND application_name LIKE 'pg_durable:worker:%'")
                if int(durable) > 0:
                    break
                time.sleep(1)
            if int(durable) < 1:
                raise ValueError('pg_durable worker did not connect to app')
        (output / 'runtime.json').write_text(json.dumps({'image': assembly['image'], 'platform': 'linux/amd64',
            'runnable_digest': child['descriptor']['digest'], 'libraries': checked, 'preload': preload,
            'postmaster_library_path': library_path,
            'durable_worker_connections': durable, 'sql_version_checked': True}, indent=2) + '\n')
        (output / 'fixtures.json').write_text(json.dumps(lock, indent=2) + '\n')
    finally:
        try:
            kubectl('delete', 'namespace', namespace, '--ignore-not-found=true', '--wait=false')
        finally:
            subprocess.run(['docker', 'rm', '-f', container], check=True, stdout=subprocess.DEVNULL)
            kubeconfig.unlink(missing_ok=True)

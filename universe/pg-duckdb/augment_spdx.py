"""Shared cnpg-sbom-generator augment_spdx API v1; no independent composer."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path


def package_components(components):
    """Use Debian's package boundaries without fabricating Debian ownership.

    Keep full build evidence and shipped notices. Only the public package graph
    folds Debian's internal components into their nearest retained parent.
    """
    by_name = {c['name']: c for c in components}
    retained = {c['name']: deepcopy(c) for c in components
                if c['name'] in {'pg_duckdb', 'duckdb'} or c.get('debian_package')}
    folded = set()
    for component in components:
        if component['name'] in retained:
            continue
        parent = component['parent']
        while parent not in retained:
            if parent not in by_name:
                raise ValueError('missing containing package for ' + component['name'])
            parent = by_name[parent]['parent']
        owner = retained[parent]
        owner['notices'] = list(dict.fromkeys(owner['notices'] + component['notices']))
        owner['license_text'] += '\n\n' + component['license_text']
        owner['copyright'] += '\n' + component['copyright']
        folded.add(parent)
    for name in folded:
        owner = retained[name]
        owner['license'] = 'LicenseRef-Universe-' + hashlib.sha256(owner['license_text'].encode()).hexdigest()[:24]
        owner['copyright'] = '\n'.join(dict.fromkeys(owner['copyright'].splitlines()))
    return list(retained.values())


def augment_spdx(document, context):
    if context.api_version != 1:
        raise ValueError('unsupported hook API')
    evidence = json.loads((Path(context.builder_path) / 'build/universe-evidence.json').read_text())
    result = deepcopy(document)
    files = {p['fileName'].removeprefix('./'): p for p in result['files']}
    for payload in evidence['payload']:
        path = payload['path']
        if path not in files:
            raise ValueError('payload missing from shared inventory: ' + path)
        if not any(c['algorithm'] == 'SHA256' and c['checksumValue'].lower() == payload['sha256']
                   for c in files[path].get('checksums', [])):
            raise ValueError('shared inventory hash mismatch: ' + path)
        builder_data = (Path(context.builder_path) / 'payload' / path).read_bytes()
        data = (Path(context.final_path) / path).read_bytes()
        if builder_data != data:
            raise ValueError('builder/final payload mismatch: ' + path)
        if hashlib.sha256(data).hexdigest() != payload['sha256']:
            raise ValueError('payload hash mismatch: ' + path)
    components = package_components(evidence['components'])
    scope = ('Package inventory follows Debian DuckDB 2.0.0+dfsg2 package boundaries. '
             'Internal bundled code and generated data are covered by their containing '
             'package and original notice files, not separate package records. '
             'Separately listed source-built libraries retain upstream identities; '
             'they are not Debian-installed packages. This is not an exhaustive '
             'embedded-component inventory.')
    result['comment'] = (result.get('comment', '') + '\n' + scope).strip()
    ids = {}
    component_ids = []
    relationships = result.setdefault('relationships', [])
    for component in components:
        identity = component['purl'] or component['repository'] + '@' + component['revision'] + '#' + component['name']
        sid = 'SPDXRef-Universe-' + hashlib.sha256(identity.encode()).hexdigest()[:24]
        existing = next((p for p in result['packages'] if p['SPDXID'] == sid or any(
            r.get('referenceLocator') == identity for r in p.get('externalRefs', []))), None)
        if existing:
            ids[component['name']] = existing['SPDXID']
            component_ids.append(existing['SPDXID'])
            continue
        sid = 'SPDXRef-Universe-' + hashlib.sha256(identity.encode()).hexdigest()[:24]
        ids[component['name']] = sid
        component_ids.append(sid)
        source_url = component.get('source_url') or (
            component['repository'] + '/tree/' + component['revision'].replace(':', '/', 1)
            if component['repository'].startswith('https://github.com/')
            else component['repository'])
        package = dict(SPDXID=sid, name=component['name'], downloadLocation=source_url,
                       filesAnalyzed=False, licenseConcluded=component['license'], licenseDeclared=component['license'],
                       copyrightText=component['copyright'], sourceInfo='Selected source: ' + source_url
                       + ('; original notice: ' + component['notice_source'] if component.get('notice_source') else '')
                       + ('; ' + component['unresolved'] if component.get('unresolved') else ''))
        if component.get('debian_package'):
            package['sourceInfo'] += ('; Debian packaging counterpart: ' + component['debian_package']
                                      + '; this component is built from upstream source, not installed by dpkg')
        if component['version'] is not None:
            package['versionInfo'] = component['version']
        if component['license'].startswith('LicenseRef-'):
            extracted = result.setdefault('hasExtractedLicensingInfos', [])
            if not any(item['licenseId'] == component['license'] for item in extracted):
                extracted.append(dict(licenseId=component['license'], extractedText=component['license_text'], name=component['name'] + ' bundled notices'))
        if component['purl']:
            package['externalRefs'] = [dict(referenceCategory='PACKAGE-MANAGER', referenceType='purl', referenceLocator=component['purl'])]
        result['packages'].append(package)
        for notice in component['notices']:
            relationships.append(dict(spdxElementId=sid, relationshipType='DISTRIBUTION_ARTIFACT', relatedSpdxElement=files[notice]['SPDXID']))
    for component, sid in zip(components, component_ids):
        parent = component['parent']
        relationships.append(dict(spdxElementId=ids[parent] if parent else result['SPDXID'],
                                  relationshipType='DEPENDS_ON' if parent else 'DESCRIBES', relatedSpdxElement=sid))
    relationships.append(dict(spdxElementId=files['lib/pg_duckdb.so']['SPDXID'], relationshipType='GENERATED_FROM', relatedSpdxElement=ids['pg_duckdb']))
    for path, file in files.items():
        if Path(path).name == 'libduckdb.so' or Path(path).name.startswith('libduckdb.so.'):
            relationships.append(dict(spdxElementId=file['SPDXID'], relationshipType='GENERATED_FROM', relatedSpdxElement=ids['duckdb']))
    return result

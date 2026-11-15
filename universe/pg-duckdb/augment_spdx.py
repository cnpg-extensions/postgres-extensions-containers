"""Shared cnpg-sbom-generator augment_spdx API v1; no independent composer."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path


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
    ids = {}
    component_ids = []
    relationships = result.setdefault('relationships', [])
    for component in evidence['components']:
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
    for component, sid in zip(evidence['components'], component_ids):
        parent = component['parent']
        relationships.append(dict(spdxElementId=ids[parent] if parent else result['SPDXID'],
                                  relationshipType='DEPENDS_ON' if parent else 'DESCRIBES', relatedSpdxElement=sid))
    relationships.append(dict(spdxElementId=files['lib/pg_duckdb.so']['SPDXID'], relationshipType='GENERATED_FROM', relatedSpdxElement=ids['pg_duckdb']))
    return result

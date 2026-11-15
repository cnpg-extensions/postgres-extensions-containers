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
        builder_data = (Path(context.builder_path) / payload['source']).read_bytes()
        data = (Path(context.final_path) / path).read_bytes()
        if builder_data != data:
            raise ValueError('builder/final payload mismatch: ' + path)
        if hashlib.sha256(data).hexdigest() != payload['sha256']:
            raise ValueError('payload hash mismatch: ' + path)
    components = evidence['components']
    # Copied Debian copyright/common-license files can make the shared scan
    # select builder packages that contribute no binary here. Replace only
    # those notice-only records with the explicit compiled-version mappings.
    mapped_notices = {files[path]['SPDXID'] for c in components if c.get('debian_package')
                      for path in c['notices']}
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
                       copyrightText=component['copyright'], sourceInfo='Selected source: ' + source_url)
        if component.get('debian_package'):
            package['sourceInfo'] += ('; Debian scanner mapping: ' + component['debian_package']
                                      + '; compiled upstream version: ' + component['version']
                                      + '; built from upstream source, not installed by dpkg; no Debian patch-level claim')
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
            relationships.append(dict(spdxElementId=file['SPDXID'], relationshipType='GENERATED_FROM', relatedSpdxElement=ids.get('libduckdb2.0', ids.get('duckdb'))))
    return result

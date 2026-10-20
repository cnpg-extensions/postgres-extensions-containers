#!/usr/bin/env python3
"""Verify signed extension indexes, independently of their build system.

Registry transport is delegated to Skopeo. Raw bytes, not reserialized JSON,
are checked against descriptors. Output becomes visible only after verification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'sbom'))
from augment_spdx import parse_json, require, validate_document, safe_file

SPDX = 'https://spdx.dev/Document'
PROVENANCE = {'https://slsa.dev/provenance/v1', 'https://slsa.dev/provenance/v0.2'}
DIGEST = re.compile(r'sha256:[a-f0-9]{64}')


def read_blob(layout, descriptor):
    digest = descriptor['digest']
    require(DIGEST.fullmatch(digest), 'unsupported blob digest')
    path = safe_file(layout,'blobs/sha256/'+digest[7:])
    raw = path.read_bytes()
    require('sha256:'+hashlib.sha256(raw).hexdigest() == digest, 'blob hash mismatch')
    if 'size' in descriptor:
        require(len(raw) == descriptor['size'], 'blob size mismatch')
    return raw


def validate_layout(layout, digest, platforms):
    require(platforms and len(platforms) == len(set(platforms)), 'invalid expected platform set')
    raw = read_blob(layout, {'digest':digest})
    index = parse_json(raw)
    require(index.get('schemaVersion') == 2 and index.get('mediaType') == 'application/vnd.oci.image.index.v1+json', 'expected OCI index')
    descriptors = index['manifests']
    require(len(descriptors) == 2*len(platforms), 'unexpected descriptor count')
    children, attestations, seen = {}, [], set()
    for descriptor in descriptors:
        require(descriptor['digest'] not in seen, 'duplicate descriptor'); seen.add(descriptor['digest'])
        require(descriptor['mediaType'] == 'application/vnd.oci.image.manifest.v1+json', 'expected OCI manifest')
        manifest = parse_json(read_blob(layout, descriptor))
        require(manifest.get('schemaVersion') == 2, 'unsupported manifest schema')
        platform = descriptor.get('platform', {})
        if platform == {'os':'unknown','architecture':'unknown'}:
            attestations.append((descriptor, manifest)); continue
        name = platform.get('os', '')+'/'+platform.get('architecture', '')
        require(name in platforms and name not in children, 'unexpected or duplicate platform')
        config = parse_json(read_blob(layout, manifest['config']))
        require(config.get('os') == platform['os'] and config.get('architecture') == platform['architecture'], 'image configuration platform mismatch')
        for layer in manifest['layers']:
            read_blob(layout, layer)
        children[name] = {'descriptor':descriptor, 'manifest':manifest}
    require(set(children) == set(platforms), 'missing expected platform')
    bound = set()
    for descriptor, manifest in attestations:
        annotations = descriptor.get('annotations', {})
        require(annotations.get('vnd.docker.reference.type') == 'attestation-manifest', 'missing attestation annotation')
        subject = annotations.get('vnd.docker.reference.digest')
        matching = [name for name, child in children.items() if child['descriptor']['digest'] == subject]
        require(len(matching) == 1 and subject not in bound, 'wrong or duplicate attestation subject'); bound.add(subject)
        name = matching[0]; child = children[name]
        oci_subject = manifest.get('subject', {})
        require(all(oci_subject.get(k) == child['descriptor'][k] for k in ('digest','size','mediaType')), 'OCI attestation subject mismatch')
        read_blob(layout,manifest['config'])
        predicates = {}
        require(len(manifest['layers']) == 2, 'expected combined SPDX/provenance attestation')
        for layer in manifest['layers']:
            statement = parse_json(read_blob(layout,layer))
            require(statement.get('_type') in ('https://in-toto.io/Statement/v1','https://in-toto.io/Statement/v0.1'), 'invalid in-toto statement')
            subjects = statement.get('subject', [])
            require(subjects and all(s.get('digest') == {'sha256':subject[7:]} for s in subjects), 'in-toto subject mismatch')
            kind = statement.get('predicateType')
            require(kind == SPDX or kind in PROVENANCE, 'unexpected predicate type')
            require(kind not in predicates, 'duplicate predicate')
            declared = layer.get('annotations', {}).get('in-toto.io/predicate-type')
            require(declared in (None,kind), 'predicate annotation mismatch')
            predicates[kind] = statement['predicate']
        require(SPDX in predicates and len(set(predicates) & PROVENANCE) == 1, 'missing SPDX or provenance')
        spdx = predicates[SPDX]
        require(spdx.get('spdxVersion') == 'SPDX-2.3', 'unsupported SPDX version')
        validate_document(spdx)
        child.update(attestation=descriptor, spdx=spdx, provenance=next(predicates[k] for k in PROVENANCE if k in predicates))
    require(len(bound) == len(platforms), 'missing platform attestation')
    return {'schema_version':1,'index_digest':digest,'index':index,'platforms':children}


def fresh_output(path):
    require(not Path(path).exists(), f'output directory must not exist: {path}')


def run(command):
    return subprocess.run(command, check=True, capture_output=True).stdout


def signature_command(image, identity=None, issuer=None, bundle=False):
    require(identity and issuer, 'explicit publisher identity and OIDC issuer required')
    return ['cosign', 'verify', '--new-bundle-format='+str(bundle).lower(), '--output', 'json',
            '--certificate-identity-regexp', identity, '--certificate-oidc-issuer', issuer, image]


def verify_signature(image, identity=None, issuer=None):
    # Storage format does not change publisher trust. Current and legacy
    # signatures are each checked with the same explicit issuer/identity.
    errors = []
    for bundle in (True, False):
        try:
            result = json.loads(run(signature_command(image,identity,issuer,bundle)))
            require(isinstance(result,list) and result, 'signature verification returned no signatures')
            require(all(s['critical']['image']['docker-manifest-digest'] == image.rpartition('@')[2] for s in result), 'signature digest mismatch')
            return result
        except subprocess.CalledProcessError as error:
            errors.append(error)
    raise errors[-1]


def verify(image, platform, output, identity=None, issuer=None):
    output = Path(output)
    fresh_output(output)
    repository, sep, digest = image.rpartition('@')
    require(sep and repository and DIGEST.fullmatch(digest), 'image must be digest-qualified')
    signature = verify_signature(image,identity,issuer)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.verify-',dir=output.parent) as temporary:
        root = Path(temporary); layout = root/'layout'
        command = ['skopeo','copy','--all','--preserve-digests']
        run([*command,'docker://'+image,'oci:'+str(layout)+':verified'])
        raw = parse_json(read_blob(layout,{'digest':digest}))
        platforms = [d['platform']['os']+'/'+d['platform']['architecture'] for d in raw['manifests'] if d.get('platform',{}).get('os') != 'unknown']
        require(platform in platforms, 'requested platform missing')
        result = validate_layout(layout,digest,platforms)
        # Keep ordinary Buildx extraction interoperable and compare parsed content.
        for field,predicate in [('SBOM','spdx'),('Provenance','provenance')]:
            member = 'SPDX' if field == 'SBOM' else 'SLSA'
            template = '{{json .'+field+'}}'
            section = json.loads(run(['docker','buildx','imagetools','inspect',image,'--format',template]))
            # Buildx uses a stub object for single-platform indexes and a map
            # for multiple platforms. This is independent of build system.
            extracted = section.get(platform, section if len(platforms)==1 else {}).get(member)
            require(extracted == result['platforms'][platform][predicate], 'Buildx extraction mismatch')
        publication = root/'verified'; publication.mkdir()
        for filename,value in [('sbom.spdx.json',result['platforms'][platform]['spdx']),('provenance.json',result['platforms'][platform]['provenance']),('verification.json',{'image':image,'platform':platform,'signature':signature,'index_digest':digest})]:
            (publication/filename).write_text(json.dumps(value,indent=2)+'\n')
        fresh_output(output)
        publication.rename(output)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',required=True);parser.add_argument('--platform',required=True,choices=['linux/amd64','linux/arm64'])
    parser.add_argument('--output-directory',required=True,type=Path)
    parser.add_argument('--certificate-identity-regexp', required=True);parser.add_argument('--certificate-oidc-issuer', required=True)
    args=parser.parse_args()
    verify(args.image,args.platform,args.output_directory,args.certificate_identity_regexp,args.certificate_oidc_issuer)

if __name__ == '__main__':
    main()

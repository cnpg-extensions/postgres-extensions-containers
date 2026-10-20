#!/usr/bin/env python3
"""Bind a complete, verified BuildKit graph to independent preparation inputs."""
import json
from pathlib import Path
import shutil
import subprocess

from prepare import digest,save
from verify import validate_layout
from workflow import source_digest


def load_preparation(directory):
    preparation=json.loads((directory/'preparation.json').read_text())
    expected=preparation.pop('preparation_sha256')
    if digest(preparation)!=expected:raise ValueError('preparation checksum mismatch')
    preparation['preparation_sha256']=expected
    if preparation['workspace_sha256']!=source_digest():raise ValueError('workspace differs from preparation')
    return preparation


def expected_row(preparation,row_id):
    rows=[r for r in preparation['rows'] if r['id']==row_id]
    if len(rows)!=1:raise ValueError('unexpected platform record')
    return rows[0]


def assert_pgrx(document,preparation,row):
    annotations=[]
    for annotation in document.get('annotations',[]):
        if annotation.get('annotator')=='Tool: cnpg-pgrx-hook-v1':annotations.append(json.loads(annotation['comment']))
    if len(annotations)!=1:raise ValueError('one PGRX augmentation required')
    evidence=annotations[0];identity=evidence['identity'];target=preparation['targets'][row['target']]
    expected={'extension':preparation['extension'],'source_version':row['source']['version'],'revision':row['source']['revision'],
              'archive_sha256':row['source']['archive_sha256'],'workspace_sha256':preparation['workspace_sha256']}
    if any(identity.get(k)!=v for k,v in expected.items()):raise ValueError('PGRX identity mismatch')
    if evidence['target']['platform']!=row['platform'] or evidence['target']['distro']!=target['distro'] or evidence['target']['pg_major']!=target['pg_major']:
        raise ValueError('PGRX target mismatch')


def assert_provenance(provenance, preparation, row, definition):
    build = provenance.get('buildDefinition', {})
    args = build.get('externalParameters', {}).get('request', {}).get('args', {})
    frozen = definition['target'][row['target']]
    for name, value in frozen['args'].items():
        if args.get('build-arg:' + name) != str(value):
            raise ValueError('provenance build argument mismatch: ' + name)
    for name, value in frozen.get('labels', {}).items():
        if args.get('label:' + name) != value:
            raise ValueError('provenance label mismatch: ' + name)
    materials = build.get('resolvedDependencies', [])
    for expected in [row['base'].split('@')[-1][7:], preparation['generator'].split('@')[-1][7:], row['source']['archive_sha256']]:
        if not any(material.get('digest') == {'sha256': expected} for material in materials):
            raise ValueError('provenance resolved dependency missing')


def capture(preparation_dir,row_id,index_digest,output):
    preparation=load_preparation(preparation_dir);row=expected_row(preparation,row_id)
    if output.exists():raise ValueError('fresh record output required')
    output.mkdir(parents=True)
    repository=row['staging'].rsplit(':',1)[0];image=repository+'@'+index_digest
    subprocess.run(['skopeo','copy','--all','--preserve-digests','docker://'+image,'oci:'+str(output/'layout')+':record'],check=True)
    result=validate_layout(output/'layout',index_digest,[row['platform']])
    graph=result['platforms'][row['platform']];assert_pgrx(graph['spdx'],preparation,row)
    definition=json.loads((preparation_dir/(row_id+'.json')).read_text())
    if digest(definition)!=row['definition_sha256']:raise ValueError('definition checksum mismatch')
    assert_provenance(graph['provenance'],preparation,row,definition)
    save(output/'definition.json',definition);save(output/'source-index.json',result['index'])
    (output/'evidence').mkdir()
    save(output/'evidence/platform.spdx.json',graph['spdx']);save(output/'evidence/provenance.json',graph['provenance'])
    record={'schema_version':1,'row':row,'preparation_sha256':preparation['preparation_sha256'],'run_id':preparation['run_id'],
            'workspace_sha256':preparation['workspace_sha256'],'git_sha':preparation['git_sha'],'timestamp':preparation['timestamp'],'generator':preparation['generator'],
            'image':image,'index_digest':index_digest,'runnable':graph['descriptor'],'attestation':graph['attestation']}
    save(output/'record.json',record);save(output/'validation.json',{'valid':True,'index_digest':index_digest})
    return record


def validate_record(preparation,row,artifact):
    record=json.loads((artifact/'record.json').read_text())
    if record.get('schema_version')!=1 or record['git_sha']!=preparation['git_sha'] or record['timestamp']!=preparation['timestamp'] or record['row']!=row or record['preparation_sha256']!=preparation['preparation_sha256'] or record['run_id']!=preparation['run_id'] or record['workspace_sha256']!=preparation['workspace_sha256'] or record['generator']!=preparation['generator']:
        raise ValueError('record does not match independent preparation')
    if record['image']!=row['staging'].rsplit(':',1)[0]+'@'+record['index_digest']:raise ValueError('unexpected staging repository')
    if digest(json.loads((artifact/'definition.json').read_text()))!=row['definition_sha256']:raise ValueError('changed platform definition')
    result=validate_layout(artifact/'layout',record['index_digest'],[row['platform']]);graph=result['platforms'][row['platform']]
    if json.loads((artifact/'source-index.json').read_text())!=result['index']:raise ValueError('source index convenience copy mismatch')
    if record['runnable']!=graph['descriptor'] or record['attestation']!=graph['attestation']:raise ValueError('descriptor mismatch')
    for path,key in [('platform.spdx.json','spdx'),('provenance.json','provenance')]:
        if json.loads((artifact/'evidence'/path).read_text())!=graph[key]:raise ValueError('extracted predicate mismatch')
    assert_pgrx(graph['spdx'],preparation,row)
    assert_provenance(graph['provenance'],preparation,row,json.loads((artifact/'definition.json').read_text()))
    return record

#!/usr/bin/env python3
"""Freeze one logical run into independently checkable platform definitions."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re

from workflow import ROOT, discover, execute, select, source_digest


def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def digest(value):return hashlib.sha256(encoded(value)).hexdigest()
def save(path,value):path.write_bytes(encoded(value)+b'\n')


def platform_base(reference, platform):
    bases=json.loads((ROOT/'pgrx/dependencies/bases.json').read_text())
    if reference not in bases or platform not in bases[reference]['platforms']:
        raise ValueError('base image requires a platform lock refresh')
    base=bases[reference]
    return reference+'@'+base['platforms'][platform],base['index_digest']



def prepare(inputs,generator,output):
    if not re.fullmatch(r'[^\s]+@sha256:[a-f0-9]{64}',generator):raise ValueError('digest-qualified generator required')
    inventory=discover();platforms=select(inputs,inventory);extension=inputs['extension_name']
    from refresh_lock import check_sources, tools_lock, fixtures_lock, check_apt
    dependencies=ROOT/'pgrx/dependencies'
    check_sources(inventory,json.loads((dependencies/'sources.json').read_text()))
    tools_lock(dependencies,False);fixtures_lock(dependencies,False);check_apt(dependencies)
    if output.exists():raise ValueError('fresh preparation directory required')
    output.mkdir(parents=True)
    timestamp=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    workspace=source_digest()
    registry='ghcr.io/'+os.environ['GITHUB_REPOSITORY_OWNER'].lower()
    environment={**os.environ,'environment':'testing','sbom_generator':generator,'build_timestamp':timestamp,'registry':registry,'revision':execute(['git','rev-parse','HEAD']).strip()}
    definition=json.loads(execute(['docker','buildx','bake','-f','docker-bake-pgrx.hcl','-f',extension+'/metadata.hcl','--print'],env=environment))
    targets=definition['target']
    run_id=os.environ['GITHUB_RUN_ID']+'-'+os.environ.get('GITHUB_RUN_ATTEMPT','1')
    source=json.loads((ROOT/'pgrx/dependencies/sources.json').read_text())[extension]
    result={'schema_version':1,'extension':extension,'inputs':inputs,'platforms':platforms,'timestamp':timestamp,'workspace_sha256':workspace,
            'git_sha':environment['revision'],'generator':generator,'run_id':run_id,'targets':{},'rows':[]}
    for name,original in sorted(targets.items()):
        if original['args']['EXT_VERSION']!=source['version']:raise ValueError('metadata and source lock disagree')
        distro=next(a.split('=',1)[1] for a in original['annotations'] if ':io.cloudnativepg.image.base.os=' in a)
        result['targets'][name]={'tags':original['tags'],'distro':distro,'pg_major':original['args']['PG_MAJOR']}
        for platform in platforms:
            architecture=platform.split('/')[1];row_id=hashlib.sha256((run_id+'\0'+name+'\0'+platform).encode()).hexdigest()[:32]
            staging=registry+'/'+inventory[extension]['image_name']+'-testing:stage-'+row_id
            base,base_index=platform_base(original['args']['BASE'],platform)
            frozen=json.loads(json.dumps(original));frozen['platforms']=[platform];frozen['tags']=[staging]
            frozen['args'].update(BASE=base,PGRX_EXTENSION=extension,PGRX_DISTRO=distro,PGRX_SOURCE_SHA256=source['archive_sha256'],
                PGRX_WORKSPACE_SHA256=workspace,PGRX_BUILD_TIMESTAMP=timestamp)
            frozen['output']=['type=image,oci-mediatypes=true,oci-artifact=true,push=true']
            single={'target':{name:frozen}}
            row={'id':row_id,'target':name,'platform':platform,'architecture':architecture,'runner':'ubuntu-24.04' if architecture=='amd64' else 'ubuntu-24.04-arm',
                 'definition_sha256':digest(single),'staging':staging,'base':base,'base_index':base_index,'source':source}
            result['rows'].append(row);save(output/(row_id+'.json'),single)
    result['preparation_sha256']=digest(result);save(output/'preparation.json',result)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inputs',required=True,type=Path);parser.add_argument('--generator',required=True);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();result=prepare(json.loads(args.inputs.read_text()),args.generator,args.output)
    matrix={'include':[{k:r[k] for k in ('id','target','platform','architecture','runner')} for r in result['rows']]}
    fixtures=json.loads((ROOT/'pgrx/dependencies/fixtures/lock.json').read_text())
    selector=result['inputs'].get('cnpg_version')
    selectors=[selector] if selector else fixtures['supported_releases']
    if not set(selectors)<=set(fixtures['operators']):raise ValueError('unsupported CNPG selector; refresh fixture locks')
    smoke_matrix={'include':[{'target':target,'cnpg':selector} for target in result['targets'] for selector in selectors]}
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'],'a') as output:output.write('matrix='+json.dumps(matrix)+'\n'+'targets='+json.dumps({'include':[{'target':t} for t in result['targets']]})+'\n')
        with open(os.environ['GITHUB_OUTPUT'],'a') as output:output.write('smoke_targets='+json.dumps(smoke_matrix)+'\n')
    print(json.dumps(matrix))

if __name__=='__main__':main()

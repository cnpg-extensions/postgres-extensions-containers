#!/usr/bin/env python3
"""Merge complete staging indexes without changing their image or predicate bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from prepare import save
from record import load_preparation,validate_record
from verify import validate_layout
from registry import wait_for_index_digest


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preparation',type=Path,required=True);parser.add_argument('--records',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();preparation=load_preparation(args.preparation)
    expected={'platform-'+preparation['extension']+'-'+r['id'] for r in preparation['rows']}
    if {p.name for p in args.records.iterdir()}!=expected:raise ValueError('missing, duplicate or unexpected platform artifacts')
    if args.output.exists():raise ValueError('fresh assembly directory required')
    args.output.mkdir(parents=True)
    for target,settings in preparation['targets'].items():
        rows=[r for r in preparation['rows'] if r['target']==target]
        records=[validate_record(preparation,r,args.records/('platform-'+preparation['extension']+'-'+r['id'])) for r in rows]
        output=args.output/target;output.mkdir()
        repository=rows[0]['staging'].rsplit(':',1)[0]
        candidate=repository+':candidate-'+hashlib.sha256((preparation['run_id']+target).encode()).hexdigest()[:32]
        definitions=json.loads((args.preparation/(rows[0]['id']+'.json')).read_text())['target'][target]
        annotations=[]
        for annotation in definitions['annotations']:
            scope,content=annotation.split(':',1)
            if 'index' in scope.split(','):annotations+=['--annotation','index:'+content]
        references=[r['image'] for r in records]
        command=['docker','buildx','imagetools','create',*annotations,'--tag',candidate,*references]
        dry=json.loads(subprocess.check_output([*command,'--dry-run']))
        expected_descriptors=[d for record in records for d in (record['runnable'],record['attestation'])]
        def normalized(descriptors):return sorted(descriptors,key=lambda d:d['digest'])
        if normalized(dry['manifests'])!=normalized(expected_descriptors):raise ValueError('Buildx merge changed descriptors')
        subprocess.run(command,check=True)
        raw=subprocess.check_output(['docker','buildx','imagetools','inspect',candidate,'--raw'])
        index_digest='sha256:'+hashlib.sha256(raw).hexdigest();image=repository+'@'+index_digest
        subprocess.run(['skopeo','copy','--all','--preserve-digests','docker://'+image,'oci:'+str(output/'layout')+':assembly'],check=True)
        graph=validate_layout(output/'layout',index_digest,preparation['platforms'])
        if normalized(graph['index']['manifests'])!=normalized(expected_descriptors):raise ValueError('published merge changed descriptors')
        # Publish normal tags only after the candidate graph has been read back.
        for tag in settings['tags']:
            subprocess.run(['docker','buildx','imagetools','create','--tag',tag,image],check=True)
            wait_for_index_digest(tag, index_digest)
        save(output/'assembly.json',{'schema_version':1,'target':target,'extension':preparation['extension'],'preparation_sha256':preparation['preparation_sha256'],
            'run_id':preparation['run_id'],'image':image,'index_digest':index_digest,'platforms':preparation['platforms'],'tags':settings['tags']})
        save(output/'metadata.json',{target:{'image.name':','.join(settings['tags']),'containerimage.digest':index_digest}})

if __name__=='__main__':main()

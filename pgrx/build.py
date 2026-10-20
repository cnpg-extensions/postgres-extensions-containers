#!/usr/bin/env python3
"""One native platform job; BuildKit alone produces the image and attestations."""
import argparse
import json
from pathlib import Path
import platform
import subprocess
import tempfile

from record import capture,expected_row,load_preparation
from prepare import digest
from workflow import ROOT


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preparation',required=True,type=Path);parser.add_argument('--row',required=True);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();preparation=load_preparation(args.preparation);row=expected_row(preparation,args.row)
    native={'x86_64':'amd64','aarch64':'arm64'}[platform.machine()]
    daemon=subprocess.check_output(['docker','info','--format','{{.Architecture}}'],text=True).strip()
    if daemon not in ({'amd64','x86_64'} if native=='amd64' else {'arm64','aarch64'}):raise ValueError('daemon/job architecture mismatch')
    if row['architecture']!=native:raise ValueError('build job must run on its native architecture')
    definition=json.loads((args.preparation/(row['id']+'.json')).read_text())
    if digest(definition)!=row['definition_sha256']:raise ValueError('altered build definition')
    pins=json.loads((ROOT/'pgrx/dependencies/workflow-tools.json').read_text())
    name='pgrx-'+row['id']
    with tempfile.TemporaryDirectory(prefix='pgrx-builder-') as temp:
        command=['docker','buildx','create','--name',name,'--driver','docker-container','--driver-opt','image='+pins['images']['buildkit']]
        subprocess.run(command,check=True)
        subprocess.run(['docker','buildx','inspect',name,'--bootstrap'],check=True)
        worker=subprocess.check_output(['docker','exec','buildx_buildkit_'+name+'0','uname','-m'],text=True).strip()
        if worker!=platform.machine():raise ValueError('selected BuildKit worker is not native')
        metadata=Path(temp)/'metadata.json'
        subprocess.run(['docker','buildx','bake','--builder',name,'-f',str(args.preparation/(row['id']+'.json')),row['target'],'--metadata-file',str(metadata),'--progress','plain'],cwd=ROOT,check=True)
        image_digest=json.loads(metadata.read_text())[row['target']]['containerimage.digest']
        capture(args.preparation,row['id'],image_digest,args.output)
        # Failure retains its uniquely named builder for diagnostics.
        subprocess.run(['docker','buildx','rm',name],check=True)

if __name__=='__main__':main()

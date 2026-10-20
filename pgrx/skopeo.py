#!/usr/bin/env python3
"""Narrow pinned Skopeo transport adapter for workflow OCI output transfer."""
import json
import os
import platform
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile


def main():
    args=sys.argv[1:]
    if not args or args[0]!='copy':raise ValueError('adapter supports skopeo copy only')
    source=args[-2];input_layout=None
    if source.startswith('oci:'):
        value=source[4:];path,sep,tag=value.rpartition(':')
        input_layout=Path(path if sep else value)
        args[-2]='oci:/in'+(':'+tag if sep else '')
    destination=args[-1];local=None
    if destination.startswith('oci:'):
        path,_,tag=destination[4:].rpartition(':');local=Path(path)
        if local.exists():raise ValueError('fresh OCI directory required')
        args[-1]='oci:/out:'+tag
    image=json.loads((Path(__file__).parent/'dependencies/workflow-tools.json').read_text())['images']['skopeo']
    architecture={'x86_64':'amd64','aarch64':'arm64'}[platform.machine()]
    options=['docker','create','--platform','linux/'+architecture]
    # Container paths are never passed as host bind-mount paths.
    auth=Path(os.environ.get('DOCKER_CONFIG',str(Path.home()/'.docker')))/'config.json'
    if auth.exists():args.insert(1,'--authfile=/tmp/registry-auth.json')
    container=subprocess.check_output([*options,image,*args],text=True).strip()
    try:
        if auth.exists():subprocess.run(['docker','cp',str(auth),container+':/tmp/registry-auth.json'],check=True)
        if input_layout:
            subprocess.run(['docker','cp',str(input_layout),container+':/in'],check=True)
        subprocess.run(['docker','start','--attach',container],check=True)
        status=json.loads(subprocess.check_output(['docker','inspect',container]))[0]['State']['ExitCode']
        if status:raise subprocess.CalledProcessError(status,args)
        if local:
            local.mkdir(parents=True)
            with tempfile.TemporaryFile() as stream:
                subprocess.run(['docker','cp',container+':/out/.','-'],stdout=stream,check=True);stream.seek(0)
                with tarfile.open(fileobj=stream) as tar:tar.extractall(local,filter='data')
    finally:subprocess.run(['docker','rm',container],check=True,stdout=subprocess.DEVNULL)

if __name__=='__main__':main()

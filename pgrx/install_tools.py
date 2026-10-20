#!/usr/bin/env python3
"""Install helper-owned, checksum-locked native Rust/reporting tools."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import tomllib
import urllib.parse
import urllib.request

from build_config import RECIPES, effective_features

PGRX=Path('/pgrx');BUILD=Path('/build')


def download(url, destination, checksum):
    data=urllib.request.urlopen(url).read()
    if hashlib.sha256(data).hexdigest()!=checksum:raise ValueError('download checksum mismatch: '+url)
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
    return destination


def run(*command, **kwargs):
    return subprocess.run(command,check=True,**kwargs)


def extract_source_archive(archive, destination):
    """Safe source-only extraction, including Debian's older Python 3.11."""
    destination = Path(destination)
    for member in archive:
        relative = PurePosixPath(member.name)
        if relative.is_absolute() or '..' in relative.parts or not (member.isdir() or member.isfile()):
            raise ValueError('unsafe CLI source archive member')
        path = destination.joinpath(*relative.parts)
        if member.isdir():
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(archive.extractfile(member).read())
            path.chmod(member.mode & 0o777)


def main():
    major,lock_file=sys.argv[1:];extension=os.environ['PGRX_EXTENSION'];arch=os.environ['TARGETARCH']
    tools=json.loads((PGRX/'dependencies/tools.json').read_text());source=json.loads((PGRX/'dependencies/sources.json').read_text())[extension]
    if source['version']!=os.environ['EXT_VERSION']:raise ValueError('source lock version mismatch')
    recipe=RECIPES[extension];manifest=tomllib.loads((BUILD/recipe['manifest']).read_text())
    triple={'amd64':'x86_64-unknown-linux-gnu','arm64':'aarch64-unknown-linux-gnu'}[arch]
    version=tools['rust']['version']
    dist=Path('/tmp/pgrx-rust-dist')
    raw=(PGRX/f'dependencies/rust-{version}.toml').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=tools['rust']['manifest_sha256']:raise ValueError('Rust distribution manifest checksum mismatch')
    distro=tomllib.loads(raw.decode())
    manifest_path=dist/f'dist/channel-rust-{version}.toml';manifest_path.parent.mkdir(parents=True,exist_ok=True);manifest_path.write_bytes(raw)
    manifest_path.with_suffix('.toml.sha256').write_text(tools['rust']['manifest_sha256']+'  '+manifest_path.name+'\n')
    for component in ('rustc','cargo','rust-std','rustfmt-preview'):
        item=distro['pkg'][component]['target'][triple];url=item['xz_url']
        download(url,dist/urllib.parse.urlparse(url).path.lstrip('/'),item['xz_hash'])
    rustup=tools['rustup']['platforms'][arch]
    binary=download(rustup['url'],Path('/tmp/rustup-init'),rustup['sha256']);binary.chmod(0o755)
    run(str(binary),'-y','--no-modify-path','--default-toolchain','none')
    cargo_bin=Path.home()/'.cargo/bin';os.environ['PATH']=str(cargo_bin)+':'+os.environ['PATH']
    os.environ['RUSTUP_DIST_SERVER']=dist.as_uri()
    run('rustup','set','auto-self-update','disable')
    run('rustup','toolchain','install',version,'--profile','minimal','--component','rustfmt')
    os.environ['RUSTUP_TOOLCHAIN']=version
    run('rustup','default',version)
    for name in ('cargo','rustc','rustdoc','rustfmt'):
        wrapper=Path('/usr/local/bin')/name
        wrapper.write_text(f'#!/bin/sh\nexport RUSTUP_TOOLCHAIN={version}\nexec {cargo_bin/name} "$@"\n');wrapper.chmod(0o755)
    pg_config=f'/usr/lib/postgresql/{major}/bin/pg_config'
    Path('/usr/local/bin/pg_config').symlink_to(pg_config)
    for name,tool in tools['tools'].items():
        item=tool['platforms'][arch];archive=download(item['url'],Path('/tmp')/(name+'.tar'),item['sha256'])
        with tarfile.open(archive) as tar:
            members=[m for m in tar if m.isfile() and Path(m.name).name==name]
            if len(members)!=1:raise ValueError('ambiguous tool archive')
            destination=Path('/usr/local/bin')/name;destination.write_bytes(tar.extractfile(members[0]).read());destination.chmod(0o755)
    original_lock=hashlib.sha256(Path(lock_file).read_bytes()).hexdigest()
    if original_lock!=source['original_lock_sha256']:raise ValueError('upstream Cargo.lock does not match source lock')
    patches=[]
    if extension=='pg-session-jwt' and source['version']=='v0.5.0':
        patch=BUILD/'Cargo.lock.patch'
        patches.append({'path':'Cargo.lock.patch','sha256':hashlib.sha256(patch.read_bytes()).hexdigest()})
        with patch.open() as stream:
            run('patch','--batch','--forward','--strip=1',cwd=BUILD,stdin=stream)
    lock=tomllib.loads(Path(lock_file).read_text())
    versions={p['version'] for p in lock['package'] if p['name']=='pgrx'}
    if len(versions)!=1:raise ValueError('ambiguous locked cargo-pgrx version')
    pgrx_version=versions.pop()
    if pgrx_version!=source['cargo_pgrx']:raise ValueError('cargo-pgrx source lock version mismatch')
    crate=download('https://static.crates.io/crates/cargo-pgrx/cargo-pgrx-'+pgrx_version+'.crate',Path('/tmp/cargo-pgrx.crate'),source['cargo_pgrx_sha256'])
    with tarfile.open(crate) as archive:extract_source_archive(archive,'/tmp/pgrx-cli')
    run('cargo','install','--root','/usr/local','--locked','--path','/tmp/pgrx-cli/cargo-pgrx-'+pgrx_version)
    run('cargo','pgrx','init','--pg'+major,pg_config,'--no-run')
    features=effective_features(manifest,recipe,major)
    config={'manifest':recipe['manifest'],'features':features,'default_features':False,'recipe_default_features':recipe['defaults'],
            'profile':'release','rustflags':os.getenv('RUSTFLAGS',''),'rust_target':triple,
            'target_cfg':run('rustc','--print','cfg','--target',triple,capture_output=True,text=True).stdout.splitlines(),
            'tools':{'rustc':version,'cargo-pgrx':pgrx_version,**{k:v['version'] for k,v in tools['tools'].items()}}}
    report=BUILD/'pgrx-sbom';report.mkdir(exist_ok=True)
    config['original_lock_sha256']=original_lock
    config['patches']=patches
    config['lock_sha256']=hashlib.sha256(Path(lock_file).read_bytes()).hexdigest()
    (report/'build-config.json').write_text(json.dumps(config,indent=2)+'\n')
    # cargo-about queries the full metadata graph before filtering the target.
    # Fetch all locked source archives so that reporting stays offline. This
    # does not compile foreign targets or include them in the runtime SBOM.
    run('cargo','fetch','--locked','--manifest-path',str(BUILD/recipe['manifest']))

if __name__=='__main__':main()

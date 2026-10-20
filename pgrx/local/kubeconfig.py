#!/usr/bin/env python3
"""Use the Kind node's Docker-network IP across Dagger's nested DNS boundary."""
import json
import re
import subprocess
import sys

name = sys.argv[1] + '-control-plane'
node = json.loads(subprocess.check_output(['docker', 'inspect', name]))[0]
address = node['NetworkSettings']['Networks']['pg-extensions-e2e']['IPAddress']
if not re.fullmatch(r'[0-9.]+', address):
    raise ValueError('missing native Kind address')
sys.stdout.write(sys.stdin.read().replace('https://' + name + ':6443', 'https://' + address + ':6443'))

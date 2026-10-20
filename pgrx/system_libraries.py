"""Small runtime-closure correction for the preserved pg-search recipe."""
from pathlib import Path
import re
import shutil
import subprocess


def needed_libraries(dynamic_section):
    return set(re.findall(r'\(NEEDED\).*Shared library: \[([^\]]+)\]', dynamic_section))


def stage_extra_libraries(extension, root=Path('/')):
    if extension != 'pg-search':
        return
    system = root / 'build/pgrx-extra-system'
    licenses = root / 'build/pgrx-extra-system-licenses'
    system.mkdir(parents=True, exist_ok=True)
    licenses.mkdir(parents=True, exist_ok=True)
    fortran = list((root / 'usr/lib').glob('*/libgfortran.so.5'))
    if len(fortran) != 1:
        raise ValueError('ambiguous pg-search Fortran runtime')
    dynamic = subprocess.check_output(['readelf', '-d', str(fortran[0])], text=True)
    # GCC 12's amd64 libgfortran needs this; GCC 14 and ARM builds do not.
    # Keep the existing OpenBLAS/Fortran copies in the extension Dockerfile.
    if 'libquadmath.so.0' in needed_libraries(dynamic):
        library = fortran[0].parent / 'libquadmath.so.0'
        copyright = root / 'usr/share/doc/libquadmath0/copyright'
        if not library.is_file() or not copyright.is_file():
            raise ValueError('required quadmath runtime or copyright is missing')
        shutil.copyfile(library, system / library.name)
        destination = licenses / 'libquadmath0'
        destination.mkdir()
        shutil.copyfile(copyright, destination / 'copyright')

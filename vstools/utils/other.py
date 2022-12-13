import builtins
import os
import sys
from subprocess import run
from typing import TYPE_CHECKING

__all__ = [
    'IS_DOCS',
    'get_nvidia_version'
]

IS_DOCS = not TYPE_CHECKING and (
    # if loaded from sphinx
    'sphinx' in sys.modules
    # if the user called with these scripts
    or os.path.basename(sys.argv[0]) in ['sphinx-build', 'sphinx-build.exe']
    # in conf.py you can do builtins.__sphinx_build__ = True to be 100% sure
    or (hasattr(builtins, '__sphinx_build__') and builtins.__sphinx_build__)
)


def get_nvidia_version() -> tuple[int, int] | None:
    nvcc = run(['nvcc', '--version'], capture_output=True)

    ver_string = ''

    if nvcc.returncode:
        smi = run(['nvidia-smi', '-q'], capture_output=True)

        if not smi.returncode:
            ver_string = smi.stdout.splitlines()[5].decode().split(':')[-1].strip()
    else:
        ver_string = nvcc.stdout.splitlines()[3].decode().split(',')[-2].replace('release', '').strip()

    if not ver_string:
        return None

    return tuple(int(x) for x in ver_string.split('.', 2))  # type: ignore

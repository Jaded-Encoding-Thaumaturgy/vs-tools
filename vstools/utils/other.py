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
"""Whether the script is currently running in sphinx docs."""


def _str_to_ver(string: str) -> tuple[int, int]:
    return tuple(int(x) for x in string.strip().split('.', 2))  # type: ignore


def get_nvidia_version() -> tuple[int, int] | None:
    """Check if nvidia drivers are installed and if available return the version."""

    try:
        nvcc = run(['nvcc', '--version'], capture_output=True)
    except FileNotFoundError:
        pass
    else:
        if not nvcc.returncode:
            return _str_to_ver(nvcc.stdout.splitlines()[3].decode().split(',')[-2].replace('release', ''))

    try:
        smi = run(['nvidia-smi', '-q'], capture_output=True)
    except FileNotFoundError:
        pass
    else:
        if not smi.returncode:
            return _str_to_ver(smi.stdout.splitlines()[5].decode().split(':')[-1])

    return None

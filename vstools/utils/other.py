import builtins
import os
import sys
from typing import TYPE_CHECKING

__all__ = [
    'IS_DOCS'
]

IS_DOCS = not TYPE_CHECKING and (
    # if loaded from sphinx
    'sphinx' in sys.modules
    # if the user called with these scripts
    or os.path.basename(sys.argv[0]) in ['sphinx-build', 'sphinx-build.exe']
    # in conf.py you can do builtins.__sphinx_build__ = True to be 100% sure
    or (hasattr(builtins, '__sphinx_build__') and builtins.__sphinx_build__)
)

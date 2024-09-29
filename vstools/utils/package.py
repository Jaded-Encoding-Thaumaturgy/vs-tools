import inspect
from typing import ParamSpec, TypeVar

from stgpytools import SPath

__all__: list[str] = [
    'get_calling_package_name',

    'get_calling_package'
]


P = ParamSpec('P')
R = TypeVar('R')


def get_calling_package_name() -> str:
    """
    Get the name of the package to which the calling function belongs.

    :param depth:   The depth in the call stack to look for the package name. Default is 1.

    :return:        The name of the package containing the calling function.
    """

    frame = inspect.currentframe()

    try:
        if frame is None:
            return "unknown"

        module = inspect.getmodule(frame)

        if module is None:
            return "unknown"

        package = module.__package__

        if package is None:
            return module.__name__.split('.')[0]

        return package.split('.')[0]
    finally:
        del frame


def get_calling_package(depth: int = 2) -> str:
    """
    Get the name of the package from which this function is called.

    :param depth:       The number of frames to go back in the call stack. Default is 2.

    :return:            The name of the calling package.
    """

    stack = inspect.stack()

    if len(stack) <= depth:
        return 'unknown'

    frame_info = stack[depth]
    module = inspect.getmodule(frame_info.frame)

    if not module:
        return 'unknown'

    if module.__name__ == '__main__':
        return SPath(frame_info.filename).name

    return module.__name__.split('.')[0]

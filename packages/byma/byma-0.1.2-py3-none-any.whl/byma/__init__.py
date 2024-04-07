"""
ByMa: A scientific computing package for Python
================================================

Documentation is available in the docstrings and
online at 

Subpackages
-----------
Using any of these subpackages requires an explicit import. For example,
``import byma.nuby``.

::

 nuby                         --- Numerical Bifurcation Analysis Tools
 iteral                       --- Tools for iterative algorithms
 pyplot                       --- Tools for plotting functions
 interface                    --- Interface functions

"""

import importlib as _importlib

try:
    from importlib.metadata import version  # for Python 3.8+
except ImportError:
    from pkg_resources import get_distribution, DistributionNotFound
    try:
        __version__ = get_distribution(__name__).version
    except DistributionNotFound:
        # Package is not installed
        __version__ = 'unknown'
else:
    __version__ = version(__name__)



submodules = [
    'nuby',
    'iteral',
    'pyplot',
]

__all__ = submodules + [
    'test',
]


def __dir__():
    return __all__


def __getattr__(name):
    if name in submodules:
        return _importlib.import_module(f'byma.{name}')
    else:
        try:
            return globals()[name]
        except KeyError:
            raise AttributeError(
                f"Module 'byma' has no attribute '{name}'"
            )
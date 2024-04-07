"""

Notes
-----
This module is has basic bifurcation analysis tools
"""

from .Continuation import *
from .Bifurcation import Bifurcation

__all__ = ['step', 'cont', 'Bifurcation']


import warnings
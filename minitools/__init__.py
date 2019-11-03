__author__ = 'CzaOrz <https://github.com/CzaOrz>'
from .version import __version__

from .__dict import *
from .__path import *
from .__url import *

__all__ = (__dict.__all__ +
           __path.__all__ +
           __url.__all__)

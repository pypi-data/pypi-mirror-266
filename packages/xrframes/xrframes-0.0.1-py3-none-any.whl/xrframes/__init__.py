"""
Similar to ``xmovie``, make animations from xarray objects.
"""

__version__ = "0.0.1"

from .core import Frames
from .util import cleanup

__all__ = (
    "Frames",
    "cleanup",
)

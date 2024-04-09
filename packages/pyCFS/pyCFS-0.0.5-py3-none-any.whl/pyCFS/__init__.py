"""
pyCFS

Python library for automating and data handling tasks for openCFS.

.. include:: ../README.md
"""

__name__ = "pyCFS"
__author__ = ["IGTE", "Eniz Mušeljić", "Andreas Wurzinger"]
__version__ = "0.0.5"
__all__ = ["pyCFS", "data"]

from .pyCFS import pyCFS  # noqa
from . import data  # noqa

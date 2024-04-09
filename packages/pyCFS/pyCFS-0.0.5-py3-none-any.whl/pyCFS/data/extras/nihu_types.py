"""
Module containing Enums extracted from NiHu source code (TODO code reference)
"""

from enum import IntEnum


# noinspection PyPep8Naming
class nihu_element_type(IntEnum):
    """
    Extracted from NiHu repo (TODO code reference)
    """

    UNDEF = 0
    ConstantPoint = 1
    LinearLine = 10212
    LinearTria = 10323
    LinearQuad = 10424
    QuadraticLine = 20312
    QuadraticTria = 20623
    QuadraticQuad = 20824
    QuadraticQuadMid = 20924
    LinearTetra = 10434
    LinearHexa = 10838

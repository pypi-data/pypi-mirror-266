"""
Module containing Enums extracted from openCFS source code (https://gitlab.com/openCFS/cfs)
"""

from enum import IntEnum, Enum


# noinspection PyPep8Naming
class cfs_result_type(IntEnum):
    """
    Extracted from openCFS repo (Domain/Results/ResultInfo.hh)
    """

    UNDEFINED = 0
    NODE = 1
    EDGE = 2
    FACE = 3
    ELEMENT = 4
    SURF_ELEM = 5
    REGION = 6
    REGION_AVERAGE = 7
    SURF_REGION = 8
    NODELIST = 9
    COIL = 10
    FREE = 11

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return f"{self.name.title()}s"

    @classmethod
    def _missing_(cls, value):
        return cls.UNDEFINED


# noinspection PyPep8Naming
class cfs_element_type(IntEnum):
    """
    Extracted from openCFS repo (Domain/ElemMapping/Elem.hh)
    """

    UNDEF = 0
    POINT = 1
    LINE2 = 2
    LINE3 = 3
    TRIA3 = 4
    TRIA6 = 5
    QUAD4 = 6
    QUAD8 = 7
    QUAD9 = 8
    TET4 = 9
    TET10 = 10
    HEXA8 = 11
    HEXA20 = 12
    HEXA27 = 13
    PYRA5 = 14
    PYRA13 = 15
    PYRA14 = 19
    WEDGE6 = 16
    WEDGE15 = 17
    WEDGE18 = 18
    POLYGON = 20
    POLYHEDRON = 21

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    @classmethod
    def _missing_(cls, value):
        return cls.UNDEF


class cfs_entry_type(IntEnum):
    """
    Extracted from openCFS repo (DataInOut/SimInOut/hdf5/hdf5io.cc::1877)
    """

    UNKNOWN = 0
    SCALAR = 1
    VECTOR = 3
    TENSOR = 6
    STRING = 32

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


class cfs_analysis_type(str, Enum):
    """
    Extracted from openCFS repo (PDE/BasePDE.cc::42)
    """

    NO_ANALYSIS = "undefined"
    STATIC = "static"
    TRANSIENT = "transient"
    HARMONIC = "harmonic"
    MULTIHARMONIC = "multiharmonic"
    # HARMONIC = "paramIdent" // the value is not unique
    EIGENFREQUENCY = "eigenFrequency"
    INVERSESOURCE = "inverseSource"
    MULTI_SEQUENCE = "multiSequence"
    BUCKLING = "buckling"
    EIGENVALUE = "eigenValue"

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.value

    @classmethod
    def _missing_(cls, value):
        return cls.NO_ANALYSIS

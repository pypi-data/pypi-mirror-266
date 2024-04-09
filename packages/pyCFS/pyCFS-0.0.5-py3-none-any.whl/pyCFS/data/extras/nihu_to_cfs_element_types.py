import numpy as np
from pyCFS.data.extras.nihu_types import nihu_element_type
from pyCFS.data.io.cfs_types import cfs_element_type

type_link_nihu_cfs = {
    nihu_element_type.UNDEF: cfs_element_type.UNDEF,
    nihu_element_type.ConstantPoint: cfs_element_type.POINT,
    nihu_element_type.LinearLine: cfs_element_type.LINE2,
    nihu_element_type.LinearTria: cfs_element_type.TRIA3,
    nihu_element_type.LinearQuad: cfs_element_type.QUAD4,
    nihu_element_type.QuadraticLine: cfs_element_type.LINE3,
    nihu_element_type.QuadraticTria: cfs_element_type.TRIA6,
    nihu_element_type.QuadraticQuad: cfs_element_type.QUAD8,
    nihu_element_type.QuadraticQuadMid: cfs_element_type.QUAD9,
    nihu_element_type.LinearTetra: cfs_element_type.TET4,
    nihu_element_type.LinearHexa: cfs_element_type.HEXA8,
}


# mapping nihu element types array to cfs element types array
def nihu_to_cfs_elem_type(nihu_elem_types: np.ndarray):
    return np.vectorize(type_link_nihu_cfs.get)(nihu_elem_types)

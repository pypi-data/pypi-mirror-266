import numpy as np
from pyCFS.data.io.cfs_types import cfs_element_type
from pyCFS.data.extras.vtk_types import vtk_element_type

# define mapping between vtk and cfs element types
type_link = {
    # Linear cells
    vtk_element_type.VTK_EMPTY_CELL: cfs_element_type.UNDEF,
    vtk_element_type.VTK_VERTEX: cfs_element_type.POINT,
    vtk_element_type.VTK_POLY_VERTEX: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LINE: cfs_element_type.LINE2,
    vtk_element_type.VTK_POLY_LINE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_TRIANGLE: cfs_element_type.TRIA3,
    vtk_element_type.VTK_TRIANGLE_STRIP: cfs_element_type.UNDEF,
    vtk_element_type.VTK_POLYGON: cfs_element_type.POLYGON,
    vtk_element_type.VTK_PIXEL: cfs_element_type.UNDEF,
    vtk_element_type.VTK_QUAD: cfs_element_type.QUAD4,
    vtk_element_type.VTK_TETRA: cfs_element_type.TET4,
    vtk_element_type.VTK_VOXEL: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HEXAHEDRON: cfs_element_type.HEXA8,
    vtk_element_type.VTK_WEDGE: cfs_element_type.WEDGE6,
    vtk_element_type.VTK_PYRAMID: cfs_element_type.PYRA5,
    vtk_element_type.VTK_PENTAGONAL_PRISM: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HEXAGONAL_PRISM: cfs_element_type.UNDEF,
    # Quadratic, isoparametric cells
    vtk_element_type.VTK_QUADRATIC_EDGE: cfs_element_type.LINE3,
    vtk_element_type.VTK_QUADRATIC_TRIANGLE: cfs_element_type.TRIA6,
    vtk_element_type.VTK_QUADRATIC_QUAD: cfs_element_type.QUAD8,
    vtk_element_type.VTK_QUADRATIC_POLYGON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_QUADRATIC_TETRA: cfs_element_type.TET10,
    vtk_element_type.VTK_QUADRATIC_HEXAHEDRON: cfs_element_type.HEXA20,
    vtk_element_type.VTK_QUADRATIC_WEDGE: cfs_element_type.WEDGE15,
    vtk_element_type.VTK_QUADRATIC_PYRAMID: cfs_element_type.PYRA13,
    vtk_element_type.VTK_BIQUADRATIC_QUAD: cfs_element_type.QUAD9,
    vtk_element_type.VTK_TRIQUADRATIC_HEXAHEDRON: cfs_element_type.HEXA27,
    vtk_element_type.VTK_TRIQUADRATIC_PYRAMID: cfs_element_type.UNDEF,
    vtk_element_type.VTK_QUADRATIC_LINEAR_QUAD: cfs_element_type.UNDEF,
    vtk_element_type.VTK_QUADRATIC_LINEAR_WEDGE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BIQUADRATIC_QUADRATIC_WEDGE: cfs_element_type.WEDGE18,
    vtk_element_type.VTK_BIQUADRATIC_QUADRATIC_HEXAHEDRON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BIQUADRATIC_TRIANGLE: cfs_element_type.UNDEF,
    # Cubic, isoparametric cell
    vtk_element_type.VTK_CUBIC_LINE: cfs_element_type.UNDEF,
    # Special class of cells formed by convex group of points
    vtk_element_type.VTK_CONVEX_POINT_SET: cfs_element_type.UNDEF,
    # Polyhedron cell(consisting of polygonal faces)
    vtk_element_type.VTK_POLYHEDRON: cfs_element_type.POLYHEDRON,
    # Higher order cells in parametric form
    vtk_element_type.VTK_PARAMETRIC_CURVE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_PARAMETRIC_SURFACE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_PARAMETRIC_TRI_SURFACE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_PARAMETRIC_QUAD_SURFACE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_PARAMETRIC_TETRA_REGION: cfs_element_type.UNDEF,
    vtk_element_type.VTK_PARAMETRIC_HEX_REGION: cfs_element_type.UNDEF,
    # Higher order cells
    vtk_element_type.VTK_HIGHER_ORDER_EDGE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_TRIANGLE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_QUAD: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_POLYGON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_TETRAHEDRON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_WEDGE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_PYRAMID: cfs_element_type.UNDEF,
    vtk_element_type.VTK_HIGHER_ORDER_HEXAHEDRON: cfs_element_type.UNDEF,
    # Arbitrary order Lagrange elements(formulated separated from generic higher order cells)
    vtk_element_type.VTK_LAGRANGE_CURVE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LAGRANGE_TRIANGLE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LAGRANGE_QUADRILATERAL: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LAGRANGE_TETRAHEDRON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LAGRANGE_HEXAHEDRON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LAGRANGE_WEDGE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_LAGRANGE_PYRAMID: cfs_element_type.UNDEF,
    # Arbitrary order Bezier elements(formulated separated from generic higher order cells)
    vtk_element_type.VTK_BEZIER_CURVE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BEZIER_TRIANGLE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BEZIER_QUADRILATERAL: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BEZIER_TETRAHEDRON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BEZIER_HEXAHEDRON: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BEZIER_WEDGE: cfs_element_type.UNDEF,
    vtk_element_type.VTK_BEZIER_PYRAMID: cfs_element_type.UNDEF,
}


# mapping vtk element types array to cfs element types array
def vtk_to_cfs_elem_type(vtk_elem_types: np.ndarray):
    return np.vectorize(type_link.get)(vtk_elem_types)

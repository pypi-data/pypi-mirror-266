from __future__ import annotations

from typing import Optional

import numpy as np
import scipy
from scipy.spatial import KDTree

from pyCFS.data.io import cfs_types
from pyCFS.data import io
from pyCFS.data.util import progressbar


def interpolation_matrix_cell_to_node(coordinates, connectivity) -> scipy.sparse.csc_array:
    """
    Computes interpolation matrix such that e = sum_{i=1}^n  v_i. Thereby, e is the data_N2C assigned to the cell,
    n the number of nodes of one element, and v_i the nodal data_N2C
    """
    # TODO Investigate why csc array does produce crashes (double corrupted,m_alloc,...)
    matrix_shape = (coordinates.shape[0], connectivity.shape[0])

    val_lst = []
    row_ind_lst = []
    col_ptr_lst = []
    counter = 0
    for el_ind in progressbar(range(connectivity.shape[0]), prefix="Creating interpolation matrix: "):
        el_conn = connectivity[el_ind, :]
        w = 1.0 / np.count_nonzero(el_conn)

        val_lst.append(np.ones(el_conn.shape) * w)
        row_ind_lst.append(el_conn - 1)
        col_ptr_lst.append(counter)
        counter += el_conn.size
    col_ptr_lst.append(counter)

    val = np.array(val_lst)
    row_ind = np.array(row_ind_lst)
    col_ptr = np.array(col_ptr_lst)
    interpolation_matrix = scipy.sparse.csc_array(
        (val.flatten(), row_ind.flatten(), col_ptr), matrix_shape, dtype=float
    )
    return interpolation_matrix


def interpolation_matrix_node_to_cell(coordinates, connectivity) -> scipy.sparse.csr_array:
    """
    Computes interpolation matrix such that v = 1/n  e_i. Thereby, v is the data_N2C located to the node,
    n the number of nodes of the element, and e_i the data_N2C of cell i.
    """
    matrix_shape = (connectivity.shape[0], coordinates.shape[0])

    val_lst = []
    col_ind_lst = []
    row_ptr_lst = []
    counter = 0
    for el_ind in progressbar(range(connectivity.shape[0]), prefix="Creating interpolation matrix: "):
        el_conn = connectivity[el_ind, :]
        val_lst.append(np.ones(el_conn.shape))
        col_ind_lst.append(el_conn - 1)
        row_ptr_lst.append(counter)
        counter += el_conn.size
    row_ptr_lst.append(counter)

    val = np.array(val_lst)
    col_ind = np.array(col_ind_lst)
    row_ptr = np.array(row_ptr_lst)
    interpolation_matrix = scipy.sparse.csr_array(
        (val.flatten(), col_ind.flatten(), row_ptr), matrix_shape, dtype=float
    )
    return interpolation_matrix


def interpolation_matrix_nearest_neighbor(
    source_coord: np.ndarray,
    target_coord: np.ndarray,
    num_neighbors=20,
    interpolation_exp=2.0,
    max_distance: float | None = None,
    formulation: Optional[str] = None,
) -> scipy.sparse.csr_array | scipy.sparse.csc_array:
    """
    Computes interpolation matrix based on nearest neighbor search with inverse distance weighting (Shepard's method)
    (see https://opencfs.gitlab.io/userdocu/DataExplanations/NN/). Nearest neighbors are searched for each point on the
    source (forward) or target (backward) grid.


    Parameters
    ----------
    source_coord: np.ndarray
        Coordinate array of m source points. Expected shape (m, 3)
    target_coord: np.ndarray
        Coordinates of n target points. Expected shape (n, 3)
    num_neighbors: int
        Number of neighbors considered for nearest neighbor search
    interpolation_exp: float, optional
        Exponent of inverse distance weighting (Shepard's method)
    max_distance: str, optional
        Set interpolation weights to zero if max_distance is exceeded.
    formulation: str, optional
        Search direction for nearest neighbor search. By default, direction is chosen automatically based on number of
        source and target points.
        'forward': Nearest neighbors are searched for each point on the (coarser) target grid. Leads to checkerboard
        if the target grid is finer than the source grid.
        'bakcward': Nearest neighbors are searched for each point on the (coarser) source grid. Leads to overprediction
        if the source grid is finer than the target grid.

    Returns
    -------
    scipy.sparse.csr_array or scipy.sparse.csc_array
        Sparse operator matrix. Type depends on formulation. 'forward' returns csc_array, 'backward' returns csr_array.
    """
    if formulation is None:
        if source_coord.shape[0] < target_coord.shape[0]:
            print(
                "Detected fine target grid (based on number of points). "
                "Automatically selected 'forward' nearest neighbor search. This can lead to checkerboard structures. "
                "Please check the result, "
                " 'backward' formulation yields better results for coarse target grids."
            )
            formulation = "forward"
        else:
            print(
                "Detected coarse target grid (based on number of points). "
                "Automatically selected 'backward' nearest neighbor search. This can lead to overprediction. "
                "Please check the result, "
                " 'forward' formulation yields better results for coarse target grids."
            )
            formulation = "backward"
    if formulation == "forward":
        return _interpolation_matrix_nearest_neighbor_forward(
            source_coord, target_coord, num_neighbors, interpolation_exp, max_distance
        )
    elif formulation == "backward":
        return _interpolation_matrix_nearest_neighbor_backward(
            source_coord, target_coord, num_neighbors, interpolation_exp, max_distance
        )
    else:
        raise ValueError("formulation argument has to be one of: None, 'forward', or 'backward'")


def _interpolation_matrix_nearest_neighbor_backward(
    source_coord: np.ndarray,
    target_coord: np.ndarray,
    num_neighbors=20,
    interpolation_exp=2.0,
    max_distance: float | None = None,
) -> scipy.sparse.csr_array:
    """
    Computes interpolation matrix based on nearest neighbor search with inverse distance weighting (Shepard's method)
    (see https://opencfs.gitlab.io/userdocu/DataExplanations/NN/). Nearest neighbors are searched for each point on the
    (coarser) target grid. Leads to checkerboard if the target grid is finer than the source grid.
    """
    # Calculate weights
    source_coord_kdtree = KDTree(source_coord)
    d, idx_list = source_coord_kdtree.query(target_coord, num_neighbors, workers=-1)

    matrix_shape = (target_coord.shape[0], source_coord.shape[0])

    col_ind = []
    row_ptr = []
    counter = 0

    if num_neighbors == 1:
        val = np.ones((target_coord.shape[0]))
        idx_list = np.expand_dims(idx_list, axis=1)
    else:
        # Prevent zero division
        d[d == 0] += np.finfo(d.dtype).eps
        # Compute weights
        dmax = np.tile(1.01 * d.max(axis=1), (num_neighbors, 1)).T
        w = ((dmax - d) / (dmax * d)) ** interpolation_exp
        a = np.tile(np.sum(w, axis=1), (num_neighbors, 1)).T
        w /= a
        val = w.flatten()

    if max_distance is not None:
        # Set weights for neighbors that exceed max_distance to zero
        # TODO normalize weights again (currently sum(w) can be < 1)
        # TODO remove zero values from sparse matrix
        idx_zero = d > max_distance
        val[idx_zero.flatten()] = 0

    for idx_el in progressbar(list(idx_list), prefix="Creating interpolation matrix: "):
        for idx_source in idx_el:
            col_ind.append(idx_source)
        row_ptr.append(counter)
        counter += num_neighbors
    row_ptr.append(counter)
    interpolation_matrix = scipy.sparse.csr_array(
        (val, np.array(col_ind).flatten(), np.array(row_ptr)), matrix_shape, dtype=float
    )

    return interpolation_matrix


def _interpolation_matrix_nearest_neighbor_forward(
    source_coord: np.ndarray,
    target_coord: np.ndarray,
    num_neighbors=20,
    interpolation_exp=2.0,
    max_distance: float | None = None,
) -> scipy.sparse.csc_array:
    """
    Computes interpolation matrix based on nearest neighbor search with inverse distance weighting (Shepard's method)
    (see https://opencfs.gitlab.io/userdocu/DataExplanations/NN/). Nearest neighbors are searched for each point on the
    (coarser) source grid. Leads to overprediction if the source grid is finer than the target grid.
    """
    # Calculate weights
    target_coord_kdtree = KDTree(target_coord)
    d, idx_list = target_coord_kdtree.query(source_coord, num_neighbors, workers=-1)

    matrix_shape = (target_coord.shape[0], source_coord.shape[0])

    row_ind = []
    col_ptr = []
    counter = 0

    if num_neighbors == 1:
        val = np.ones((source_coord.shape[0]))
        idx_list = np.expand_dims(idx_list, axis=1)
    else:
        # Compute weights
        d += np.finfo(float).eps  # Offset to prevent division by zero
        dmax = np.tile(1.01 * d.max(axis=1), reps=(num_neighbors, 1)).T
        w = ((dmax - d) / (dmax * d)) ** interpolation_exp
        a = np.tile(np.sum(w, axis=1), reps=(num_neighbors, 1)).T
        w /= a
        val = w.flatten()

    if max_distance is not None:
        # Set weights for neighbors that exceed max_distance to zero
        # TODO normalize weights again (currently sum(w) can be < 1)
        # TODO remove zero values from sparse matrix
        idx_zero = d > max_distance
        val[idx_zero.flatten()] = 0

    for idx_el in progressbar(list(idx_list), prefix="Creating interpolation matrix: "):
        for idx_target in idx_el:
            row_ind.append(idx_target)
        col_ptr.append(counter)
        counter += num_neighbors
    col_ptr.append(counter)

    interpolation_matrix = scipy.sparse.csc_array(
        (val, np.array(row_ind).flatten(), np.array(col_ptr)), matrix_shape, dtype=float
    )

    return interpolation_matrix


def apply_interpolation(
    result_array: io.CFSResultArray,
    interpolation_matrix: scipy.sparse.csr_array | scipy.sparse.csc_array,
    restype_out: Optional[cfs_types.cfs_result_type] = None,
    quantity_out: Optional[str] = None,
    region_out: Optional[str] = None,
) -> io.CFSResultArray:
    """
    Performs interpolation based on sparse interpolation matrix for all data steps.
    """
    if quantity_out is None:
        quantity_out = result_array.Quantity
    if region_out is None:
        region_out = result_array.Region
    if restype_out is None:
        restype_out = result_array.ResType

    step_values = result_array.StepValues
    result_array_out = io.CFSResultArray(
        np.empty(
            (result_array.shape[0], interpolation_matrix.shape[0], result_array.shape[2]),
            dtype=result_array.dtype,
        )
    )
    result_array_out.MetaData = result_array.MetaData
    result_array_out.Quantity = quantity_out
    result_array_out.Region = region_out
    result_array_out.ResType = restype_out
    for i in progressbar(range(len(step_values)), prefix="Performing interpolation:"):
        result_array_out[i, :, :] = interpolation_matrix.dot(result_array[i, :, :])

    return result_array_out

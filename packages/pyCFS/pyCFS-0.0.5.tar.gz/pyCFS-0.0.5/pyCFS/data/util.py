"""
Module containing utility functions for pyCFS.data project
"""

from __future__ import annotations

import datetime
import sys
import time

from functools import partial
from multiprocessing import Pool
from typing import Collection, List, Dict, Tuple

import numpy as np

from pyCFS.data.io.cfs_types import cfs_element_type


def _conn_list_to_matrix(i, offsets, connectivity_list):
    """Helper function for connectivity_list_to_matrix"""
    return offsets[i + 1] - offsets[i], connectivity_list[offsets[i] : offsets[i + 1]]


def connectivity_list_to_matrix(
    connectivity_list: np.ndarray, offsets: np.ndarray, processes=None, verbose=False
) -> np.ndarray:
    """
    Put Connectivity list data into a 2D numpy array where each row contains the Connectivity data of one cell. Empty
    array elements are indicated by value -1.

    Parameters
    ----------
    connectivity_list : numpy.ndarray
        Connectivity list array (N*M,). N number of elements, M number of nodes per element.
    offsets : numpy.ndarray
        offset list array (N*M,). N number of elements, M number of nodes per element.
    processes : int, optional
        Number of processes to use in parallel. The default is ``None``, in which case all cores are used.
    verbose : bool, optional
        The default is ``False``

    Returns
    -------
    numpy.ndarray
        Data array where each row contains the Connectivity data of one cell (N,M). N number of elements, M number of
        nodes per element. Empty array elements are indicated by value -1.
    """

    n_cells = offsets.size - 1
    max_cell_size = np.max(offsets[1:] - offsets[0:-1])
    conn_shape = (n_cells, max_cell_size)
    connectivity = np.zeros(conn_shape, dtype=int) - 1

    vprint("Building Connectivity matrix from list", end="", verbose=verbose)
    with Pool(processes=processes) as pool:
        t_start = time.time()
        for i, res in enumerate(
            pool.map(
                partial(
                    _conn_list_to_matrix,
                    offsets=offsets,
                    connectivity_list=connectivity_list,
                ),
                range(n_cells),
            )
        ):
            connectivity[i, 0 : res[0]] = res[1]
    vprint(
        f" | Elapsed time: {datetime.timedelta(seconds=round(time.time() - t_start))}",
        verbose=verbose,
    )

    return connectivity


def list_search(obj: List, item):
    """
    Search list object for item.

    Parameters
    ----------
    obj : list
    item
        Obj list items type must have ``__eq__`` method that is compatible with item.


    Returns
    -------
    Any
        Obj list item

    """
    return obj[obj.index(item)]


def angle(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Compute angle between two vectors v1, v2.

    Parameters
    ----------
    v1 : numpy.ndarray
        Vector 1
    v2 : numpy.ndarray
        Vector 2

    Returns
    -------
    float
        Angle between vectors v1 and v2 in radians.

    """
    cosine_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return np.arccos(cosine_angle)


def element_angle_2d(element_coordinates: np.ndarray) -> List[float]:
    """
    Compute corner angles of 2D element

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of element Coordinates (Nx3), where N is the number of nodes.

    Returns
    -------
    list[float]
        List of corner angles. Index matches index N in element_coordinates.

    """
    corner_angles = []
    for i in range(element_coordinates.shape[0]):
        v1 = element_coordinates[i - 2, :] - element_coordinates[i - 1, :]
        v2 = element_coordinates[i, :] - element_coordinates[i - 1, :]
        corner_angles.append(angle(v1, v2))

    return corner_angles


def element_skew(element_coordinates: np.ndarray, element_type: cfs_element_type) -> float:
    """
    Compute element skewness. Supported element types: TRIA3, QUAD4

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of element Coordinates (Nx3), where N is the number of nodes.
    element_type : pyCFS.data.cfs_types.cfs_element_type
        Element type

    Returns
    -------
    float
        Element skewness

    Notes
    -----
    Skewness determines how close to ideal (equilateral or equiangular) a face or cell is. According to the definition
    of skewness, a value of 0 indicates an equilateral cell (best) and a value of 1 indicates a completely degenerate
    cell (worst). Degenerate cells (slivers) are characterized by nodes that are nearly coplanar (colinear in 2D).
    This metric is based on the deviation from a normalized equilateral angle. This method applies to all cell
    and face shapes, including pyramids and prisms. (extracted from "Ansys Meshing User's Guide 2021R2" p.141)

    """
    theta_e = {
        cfs_element_type.TRIA3: np.deg2rad(60),
        cfs_element_type.QUAD4: 0.5 * np.pi,
    }

    if element_type not in theta_e:
        raise NotImplementedError(
            f"{element_type} not supported. Element metric implemented for element types: {list(theta_e.keys())}"
        )

    angles = element_angle_2d(element_coordinates)
    skewness = max(
        (max(angles) - theta_e[element_type]) / (np.pi - theta_e[element_type]),
        (theta_e[element_type] - min(angles)) / theta_e[element_type],
    )

    return skewness


def element_quality_ansys(element_coordinates: np.ndarray, element_type: cfs_element_type) -> float:
    """
    Compute element quality based on ANSYS metric. Supported element types: TRIA3, QUAD4, TET4

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of element Coordinates (Nx3), where N is the number of nodes.
    element_type : pyCFS.data.cfs_types.cfs_element_type
        Element type

    Returns
    -------
    float
        Element quality. Unsupported elements return -1.

    Notes
    -----
    This metric is based on the ratio of the volume to the sum of the square of the edge lengths for 2D
    quad/tri elements, or the square root of the cube of the sum of the square of the edge lengths for
    3D elements. A value of 1 indicates a perfect cube or square while a value of 0 indicates that the
    element has a zero or negative volume. (extracted from "Ansys Meshing User's Guide 2021R2" p.130)

    """
    # Factor extracted from "Ansys Meshing User's Guide 2021R2" p.130
    factor = {
        cfs_element_type.TRIA3: 6.92820323,
        cfs_element_type.QUAD4: 4.0,
        cfs_element_type.TET4: 124.70765802,
        cfs_element_type.HEXA8: 41.56921938,
        cfs_element_type.WEDGE6: 62.35382905,
        cfs_element_type.PYRA5: 96,
    }

    if element_type in (cfs_element_type.TRIA3, element_type.QUAD4):
        edge_length = np.linalg.norm(element_coordinates - np.roll(element_coordinates, 1, axis=0), axis=1)
        return factor[element_type] * element_area(element_coordinates, element_type) / sum(edge_length**2)
    elif element_type in (
        cfs_element_type.TET4,
        cfs_element_type.HEXA8,
        cfs_element_type.WEDGE6,
        cfs_element_type.PYRA5,
    ):
        # TODO implement HEXA8, WEDGE6, PYRA5
        if element_type == cfs_element_type.TET4:
            edge_length = np.linalg.norm(element_coordinates - np.roll(element_coordinates, 1, axis=0), axis=1)
            return (
                factor[element_type]
                * element_volume(element_coordinates, element_type)
                / np.sqrt(sum(edge_length**2) ** 3)
            )
        else:
            return -1
    else:
        raise NotImplementedError(
            f"{element_type} not supported. Element metric implemented for element types: {list(factor.keys())}"
        )


def element_quality(
    element_coordinates: np.ndarray,
    element_type: cfs_element_type,
    metric: str = "quality",
) -> float:
    """
    Compute element metric

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of element Coordinates (Nx3), where N is the number of nodes.
    element_type : pyCFS.data.cfs_types.cfs_element_type
        Element type
    metric : str
        Quality metric. Implemented metrics: Element Quality (Ansys), Skewness

    Returns
    -------
    float
        Element quality. Unsupported elements return -1.

    """
    if metric == "quality":
        return element_quality_ansys(element_coordinates, element_type)
    elif metric == "skewness":
        return element_skew(element_coordinates, element_type)
    else:
        raise NotImplementedError("Implemented element metrics: Element Quality (Ansys), Skewness")


def element_area(element_coordinates: np.ndarray, element_type: cfs_element_type) -> float:
    """
    Compute area of 2D element. Implemented element types: TRIA3, QUAD4

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of element Coordinates (Nx3), where N is the number of nodes.
    element_type : pyCFS.data.cfs_types.cfs_element_type
        Element type

    Returns
    -------
    float
        Element area

    """
    if element_type == cfs_element_type.TRIA3:
        v1 = element_coordinates[1, :] - element_coordinates[0, :]
        v2 = element_coordinates[2, :] - element_coordinates[0, :]
        return float(0.5 * np.linalg.norm(np.cross(v1, v2)))
    elif element_type == cfs_element_type.QUAD4:
        return element_area(
            element_coordinates[:3, :], element_type=cfs_element_type(element_type.TRIA3)
        ) + element_area(element_coordinates[[0, 2, 3], :], element_type=cfs_element_type(element_type.TRIA3))
    else:
        raise NotImplementedError("Implemented element types: TRIA3, QUAD4")


def element_volume(element_coordinates: np.ndarray, element_type: cfs_element_type | int) -> float:
    """
    Compute volume of 3D element. Implemented element types: TET4

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of element Coordinates (Nx3), where N is the number of nodes.
    element_type : pyCFS.data.cfs_types.cfs_element_type
        Element type

    Returns
    -------
    float
        Element volume

    """
    if element_type == cfs_element_type.TET4:
        v1 = element_coordinates[0, :] - element_coordinates[3, :]
        v2 = element_coordinates[1, :] - element_coordinates[3, :]
        v3 = element_coordinates[2, :] - element_coordinates[3, :]
        return float(1.0 / 6 * np.linalg.norm(np.dot(v1, np.cross(v2, v3))))
    else:
        raise NotImplementedError("Implemented element types: TET4")


def element_centroid(element_coordinates: np.ndarray) -> np.ndarray:
    """
    Compute geometric center of element

    Parameters
    ----------
    element_coordinates : numpy.ndarray
        Array of element Coordinates (Nx3), where N is the number of nodes.

    Returns
    -------
    numpy.ndarray
        Geometric center of element

    """
    return np.mean(element_coordinates, axis=0)


def vecnorm(v: np.ndarray, order: int | None = None, axis: int | None = None) -> np.ndarray:
    """
    Normalize vector

    Parameters
    ----------
    v : numpy.ndarray
        Vector / array of vectors to normalize
    order : {non-zero int, inf, -inf, 'fro', 'nuc'}, optional
        Order of the norm (see table under ``Notes``). inf means numpy's
        `inf` object. The default is None.
    axis : {None, int, 2-tuple of ints}, optional
        If `axis` is an integer, it specifies the axis of `x` along which to
        compute the vector norms.  If `axis` is a 2-tuple, it specifies the
        axes that hold 2-D matrices, and the matrix norms of these matrices
        are computed.  If `axis` is None then either a vector norm (when `x`
        is 1-D) or a matrix norm (when `x` is 2-D) is returned. The default
        is None.

    Returns
    -------
    numpy.ndarray
        Normalized vector / array of vectors

    """
    v_norm = np.linalg.norm(v, ord=order, axis=axis)
    if v_norm.ndim == 0:
        v_return = v / v_norm
    elif v_norm.ndim == 1 and v.ndim == 2:
        v_return = v / np.tile(v_norm, (v.shape[1], 1)).T
    else:
        raise NotImplementedError(
            f"Normalizing array of dimension {v.ndim} with norm array of dimension {v_norm.ndim} not implemented"
        )

    return v_return


def trilateration(
    c1: np.ndarray, c2: np.ndarray, c3: np.ndarray, r1: float, r2: float, r3: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find the intersection of three spheres with centers C1,C2,C3 and radii r1,r2,r3.
    Yields 2 feasible intersection points.

    Parameters
    ----------
    c1 : numpy.ndarray
        Center Coordinates of sphere 1.
    c2 : numpy.ndarray
        Center Coordinates of sphere 2.
    c3 : numpy.ndarray
        Center Coordinates of sphere 3.
    r1 : float
        Radius of sphere 1.
    r2 : float
        Radius of sphere 2.
    r3 : float
        Radius of sphere 3.

    Returns
    -------
    p1 : numpy.ndarray
        Coordinates of intersection point 1
    p2 : numpy.ndarray
        Coordinates of intersection point 2

    Notes
    -----
    Implementaton based on Wikipedia Trilateration article:
    https://en.wikipedia.org/wiki/True-range_multilateration#Three_Cartesian_dimensions,_three_measured_slant_ranges

    """

    # Define coordinate system with origin in C1, C2 on x-axis, and C3 in xy-plane
    v1 = c2 - c1
    v2 = c3 - c1

    e1 = vecnorm(v1)
    e3 = vecnorm(np.cross(v1, v2))
    e2 = np.cross(e3, e1)

    u = np.dot(e1, v1)
    vx = np.dot(e1, v2)
    vy = np.dot(e2, v2)

    x = ((r1**2) - (r2**2) + (u**2)) / (2 * u)
    y = ((r1**2) - (r3**2) + (vx**2) + (vy**2) - (2 * vx * x)) / (2 * vy)
    z = np.sqrt(r1**2 - x**2 - y**2)

    k1 = c1 + x * e1 + y * e2 + z * e3
    k2 = c1 + x * e1 + y * e2 - z * e3
    return k1, k2


def merge_nested_dict(dict_target: Dict, dict_source: Dict, path: List[str] | None = None) -> Dict:
    """
    Merge nested dictionary ``dict_source`` into nested dictionary ``dict_target``.

    Parameters
    ----------
    dict_target : dict
        Target dictionary
    dict_source : dict
        Source dictionary
    path : list[str], optional
        Dynamic dictionary path for recursive call. Default is ``None``.

    Returns
    -------
    dict
        Merged nested dictionary

    """
    if path is None:
        path = []
    for key in dict_source:
        if key in dict_target:
            if isinstance(dict_target[key], dict) and isinstance(dict_source[key], dict):
                merge_nested_dict(dict_target[key], dict_source[key], path + [str(key)])
            elif dict_target[key] == dict_source[key]:
                pass  # same leaf value
            else:
                raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
        else:
            dict_target[key] = dict_source[key]
    return dict_target


def vprint(*args, verbose=True, **kwargs) -> None:
    # noinspection PyArgumentEqualDefault,PyUnresolvedReferences
    """
    If verbose flag is ``True``, prints the values to a stream, or to sys.stdout by default.

    Parameters
    ----------
    args
        Value to print.
    verbose : bool, optional
        Flag whether to print
    file : , optional
        a file-like object (stream); defaults to the current sys.stdout.
    sep : str, optional
        string inserted between values, default a space.
    end : str, optional
        string appended after the last value, default a newline.
    flush : bool, optional
        whether to forcibly flush the stream.

    Examples
    --------
    >>> from pyCFS.data.util import vprint
    >>> vprint(value, verbose=True, sep=' ', end='\\n', file=sys.stdout, flush=False)

    """
    if verbose:
        print(*args, **kwargs)


def progressbar(it: Collection, prefix="", size=40, out=sys.stdout, max_update=1000, show_etc=True, verbose=True):
    """
    Shows and updates (overwrites) progressbar, updates every iteration

    Parameters
    ----------
    it
    prefix : str
        Prefix to the progress bar
    size : int, optional
        Number of characters used to print the progress bar. Default value is ``40``
    out : optional
        a file-like object (stream); defaults to the current sys.stdout.
    max_update : int, optional
        Maximum number of updates to show in the progress bar. Skippes iterations if ``it`` exceeds ``max_update``.
    show_etc : bool, optional
        Flag whether to show ETC (estimated time to completion); defaults to ``True``.
    verbose : bool, optional
        Flag whether to print the progress bar. Defaults to ``True``.

    Examples
    --------
    >>> for _ in progressbar(range(5),prefix='Looping: '):
    >>>    pass

    """
    count = len(it)
    if count == 0:
        return

    def show(j, etc: float | None = None):
        """Show progressbar"""
        x = int(size * j / count)
        if not show_etc or (etc is None):
            vprint(
                f"{prefix}[{u'█' * x}{('.' * (size - x))}] {j}/{count}",
                end="\r",
                file=out,
                flush=True,
                verbose=verbose,
            )
        else:
            vprint(
                f"{prefix}[{u'█' * x}{('.' * (size - x))}] {j}/{count} | ETA: {datetime.timedelta(seconds=etc)}",
                end="\r",
                file=out,
                flush=True,
                verbose=verbose,
            )

    time_start = time.time()
    show(0)
    time_iter_list = np.array([])
    movmean_window = int(count / 20)
    if count < max_update:
        for i, item in enumerate(it):
            time_iter_start = time.time()
            yield item
            time_iter = time.time() - time_iter_start
            time_iter_list = np.append(time_iter_list, time_iter)
            time_per_iter = np.mean(time_iter_list[max(0, i - movmean_window) :])
            time_etc = np.ceil((count - i) * time_per_iter)
            show(i + 1, etc=time_etc)
    else:
        step = int(count / max_update)
        time_etc = 0
        time_iter_start = time.time()
        for i, item in enumerate(it):
            yield item
            if i % step == 0:
                time_iter = time.time() - time_iter_start
                time_iter_list = np.append(time_iter_list, time_iter)
                time_per_iter = np.mean(time_iter_list[max(0, int((i - movmean_window) / step)) :])
                time_etc = np.ceil((count - i) * time_per_iter / step)
                show(i + 1, etc=time_etc)
                time_iter_start = time.time()
        show(count, etc=time_etc)
    vprint(
        f"{prefix}[{u'█' * size}] {count}/{count} | Elapsed time: {datetime.timedelta(seconds=int(time.time() - time_start))}",
        file=out,
        flush=True,
        verbose=verbose,
    )

#    Fit Geometry
#
#      Processing Tool for CFS HDF5 files
#
#      This script fits a region to a target region by means of rotation and translation transformations based on
#      minimizing the squared distance of all source nodes to the respective nearest neighbor on the target mesh.
#
# Usage
#   python fit_geometry.py --file-target filename_target.cfs --file-src filename_src.cfs --file-out filename_out.cfs
#   # Fits all regions in "filename_src.cfs" to all regions in "filename_target.cfs" with initially no transformation
#   python fit_geometry.py ... --regions-target region1,region2
#   # Fits all regions in "filename_src.cfs" to "region1" and "region2" in "filename_target.cfs"
#   python fit_geometry.py ... --regions-src region1,region2
#   # Fits regions "region1" and "region2" in "filename_src.cfs" to all regions in "filename_target.cfs"
#   python fit_geometry.py ... --init-param 0,1,0,0,3.14,0
#   # Fits all regions in "filename_src.cfs" to all regions in "filename_target.cfs" with initial transformation
#     parameters [x,y,z,rx,ry,rz] with Euler parameters in 'XYZ' sequence (for more than 1 source region add
#     additional initial transformation parameters)
#
# Input Parameters
#   * filename_src - filename of HDF5 file source
#   * filename_out - filename of HDF5 file output
#   * filename_target - filename of HDF5 file target
#   * regions_target - (optional) list of region names to be targeted
#   * regions_fit - (optional) list of region names to be fitted
#   * transform_param_init - (optional) initial transformation parameters
#
# Return Value
#   None
#
# About
#   * Created:  Aug 2022
#   * Authors:  Andreas Wurzinger
##################################################################################
from __future__ import annotations

import numpy as np
import scipy.optimize
from scipy.spatial import KDTree
from scipy.spatial import transform
from typing import List

from pyCFS.data import io
from pyCFS.data.util import progressbar


def calc_dsum(fitCoord, regCoord_kdtree: KDTree):
    """Calculate squared sum of distances"""
    # TODO Possible improvement: Multiple nearest neighbors with Mahalanobis distance (with mean = 0)
    d, point_index = regCoord_kdtree.query(fitCoord, workers=-1)

    return sum(d * d)


def transform_coord(arg: np.ndarray, coord: np.ndarray):
    """Transform coordinate matrix based on Arguments [X,Y,Z,RX,RY,RZ]. RX, RY, RZ represent euler angles and are
    applied first."""
    # Rotation
    r = transform.Rotation.from_euler("xyz", arg[3:6])
    coord = r.apply(coord)

    # Translation
    coord += arg[0:3]

    return coord


def transform_result(arg: np.ndarray, res: np.ndarray):
    """Transform vector result data based on Arguments [X,Y,Z,RX,RY,RZ]. RX, RY, RZ represent euler angles and are
    applied only."""
    # Rotation
    r = transform.Rotation.from_euler("xyz", arg[3:6])
    res = r.apply(res)

    return res


def transform_mesh_result(
    mesh_data: io.CFSMeshData, result_data: io.CFSResultData, regions_data: List[io.CFSRegData], arg: np.ndarray
):
    # Transform Coordinates
    print("Transform Coordinates")
    mesh_data.Coordinates = transform_coord(arg, mesh_data.Coordinates)
    # Transform vector data if contained in file
    print("Transform vector data")
    for res_data in result_data.Data:
        quantity = res_data.Quantity
        if res_data.shape[2] != 3:
            # Process vector data only
            continue
        for m, reg in enumerate(regions_data):
            if reg == res_data.Region:
                for i in progressbar(range(res_data.shape[0]), f"Transform {quantity}: "):
                    res_data[i, :, :] = transform_result(arg[0 + 6 * m : 6 + 6 * m], res_data[i, :, :])


def read_coord(filename: str, regions=None):
    """Read global coordinate matrix and for each region."""
    if regions is None:
        regions = []
    # Read target node Coordinates
    with io.CFSReader(filename) as h5reader:
        mesh_data = h5reader.MeshData
        reg_coord = []
        for reg in regions:
            reg_coord.append(h5reader.get_mesh_region_coordinates(region=reg))

    node_coord = mesh_data.Coordinates

    return node_coord, reg_coord


def compute_fit_transform(
    target_coord: np.ndarray,
    reg_fit_coord: List[np.ndarray],
    fit_coord: np.ndarray,
    regions_fit: List[str],
    transform_param_init: np.ndarray | None = None,
    init_angle_degree=False,
):
    # Build KD Tree
    target_coord_kdtree = KDTree(target_coord)

    def cost_fit(transform_arg: np.ndarray) -> float:
        """Calculate cost of current fit"""
        dsum = 0.0
        for reg_idx in range(len(reg_fit_coord)):
            coord = transform_coord(transform_arg[0 + 6 * reg_idx : 6 + 6 * reg_idx], fit_coord)
            dsum += calc_dsum(coord, target_coord_kdtree)
        return dsum

    transform_param_init = np.array(transform_param_init)
    if init_angle_degree:
        for reg_idx in range(len(regions_fit)):
            transform_param_init[3 + 6 * reg_idx : 6 + 6 * reg_idx] = (
                np.pi / 180 * transform_param_init[3 + 6 * reg_idx : 6 + 6 * reg_idx]
            )
    print(f"Initial cost: {cost_fit(transform_param_init)}")

    res_opt = scipy.optimize.minimize(cost_fit, transform_param_init)
    print(f"{res_opt.message} (numIt={res_opt.nit}, numEval={res_opt.nfev})")
    transform_param_opt = res_opt.x

    print(f"Fitted cost: {cost_fit(transform_param_opt)}")

    for i in range(len(reg_fit_coord)):
        if regions_fit:
            print(f"Region: {regions_fit[i]}")
        else:
            print("Region 1:")
        print(f" - Translation {transform_param_opt[0 + 6 * i:3 + 6 * i]}")
        print(f" - Rotation(rad) {transform_param_opt[3 + 6 * i:6 + 6 * i]}")
        print(f" - Rotation(deg) {180 / np.pi * transform_param_opt[3 + 6 * i:6 + 6 * i]}")

    return transform_param_opt


def fit_mesh(
    mesh_data_fit: io.CFSMeshData,
    result_data_fit: io.CFSResultData,
    mesh_data_target: io.CFSMeshData,
    regions_target=None,
    regions_fit=None,
    transform_param_init=None,
    init_angle_degree=False,
):
    """
    This script fits a region to a target region by means of rotation and translation transformations based on
    minimizing the squared distance of all source nodes to the respective nearest neighbor on the target mesh.
    Input Parameters
    * mesh_data_fit - CFSMesh object of grid to fit
    * result_data_fit - CFSResult object of vector data to transform with mesh fit
    * mesh_data_target - CFSMesh object of target grid
    * regions_target - (optional) list of region names to be targeted, if not specified all Coordinates are used
    * regions_fit - (optional) list of region names to be fitted, if not specified all Coordinates are
    * transform_param_init - (optional) initial transformation parameters
    * init_angle_degree - (optional) convert euler angles in transform_param_init from degree to radians
    """
    if regions_target is None:
        regions_target = []
    if regions_fit is None:
        regions_fit = []
    if transform_param_init is None:
        transform_param_init = [0, 0, 0, 0, 0, 0]

    target_coord = mesh_data_target.Coordinates
    reg_target_coord = []
    for reg in regions_target:
        reg_target_coord.append(mesh_data_target.get_region_coordinates(region=reg))
    if reg_target_coord:
        target_coord = np.concatenate(reg_target_coord)

    fit_coord = mesh_data_fit.Coordinates
    if regions_fit:
        reg_fit_coord = []
        for reg in regions_fit:
            reg_fit_coord.append(mesh_data_fit.get_region_coordinates(region=reg))
    else:
        reg_fit_coord = [fit_coord]

    transform_param_opt = compute_fit_transform(
        target_coord,
        reg_fit_coord,
        fit_coord,
        regions_fit=regions_fit,
        transform_param_init=transform_param_init,
        init_angle_degree=init_angle_degree,
    )

    transform_mesh_result(
        mesh_data=mesh_data_fit,
        result_data=result_data_fit,
        regions_data=regions_fit,
        arg=transform_param_opt,
    )

    return mesh_data_fit, result_data_fit, transform_param_opt


def fit_coordinates(
    filename_src: str,
    filename_out: str,
    filename_target: str,
    regions_target=None,
    regions_fit=None,
    transform_param_init=None,
    init_angle_degree=False,
):
    """
    This script fits a region to a target region by means of rotation and translation transformations based on
    minimizing the squared distance of all source nodes to the respective nearest neighbor on the target mesh.
    Input Parameters
    * filename_src - filename of HDF5 file source
    * filename_out - filename of HDF5 file output
    * filename_target - filename of HDF5 file target
    * regions_target - (optional) list of region names to be targeted, if not specified all Coordinates are used
    * regions_fit - (optional) list of region names to be fitted, if not specified all Coordinates are
    * transform_param_init - (optional) initial transformation parameters
    * init_angle_degree - (optional) convert euler angles in transform_param_init from degree to radians
    """
    # Read target Coordinates
    with io.CFSReader(filename_target) as h5reader:
        mesh_data_target = h5reader.MeshData

    # Read source Coordinates
    with io.CFSReader(filename_src) as h5reader:
        mesh_data = h5reader.MeshData
        result_data = h5reader.MultiStepData

    mesh_data, result_data, _ = fit_mesh(
        mesh_data,
        result_data,
        mesh_data_target,
        regions_target,
        regions_fit,
        transform_param_init,
        init_angle_degree,
    )

    with io.CFSWriter(filename_out) as h5writer:
        h5writer.create_file(mesh_data=mesh_data, result_data=result_data)

"""
Module containing data processing utilities for writing HDF5 files in openCFS format
"""

import numpy as np
import pytest

from pyCFS.data import io, v_def
from pyCFS.data.io.cfs_types import cfs_element_type, cfs_result_type, cfs_analysis_type


@pytest.fixture
def dummy_CFSMeshData_obj():
    """
    Create simple test mesh with 1 Volume and 2 Surface region / group
    """
    # Create Mesh
    mesh_data = io.CFSMeshData(verbosity=v_def.all)
    mesh_data.MeshInfo.Dimension = 3
    mesh_data.Coordinates = np.array(
        [
            [0, 0, 0],
            [0, 0, 1],
            [0, 1, 0],
            [0, 1, 1],
            [1, 0, 0],
            [1, 0, 1],
            [1, 1, 0],
            [1, 1, 1],
        ]
    )
    mesh_data.MeshInfo.NumNodes = 8
    mesh_data.Connectivity = np.array(
        [
            [1, 2, 4, 3, 5, 6, 8, 7],
            [1, 2, 3, 0, 0, 0, 0, 0],
            [2, 3, 4, 0, 0, 0, 0, 0],
            [5, 6, 8, 7, 0, 0, 0, 0],
        ]
    )
    mesh_data.Types = np.array(
        [
            cfs_element_type.HEXA8,
            cfs_element_type.TRIA3,
            cfs_element_type.TRIA3,
            cfs_element_type.QUAD4,
        ]
    )
    mesh_data.MeshInfo.NumElems = 4
    mesh_data.MeshInfo.Num2DElems = 3
    mesh_data.MeshInfo.Num3DElems = 1
    mesh_data.MeshInfo.Num_HEXA8 = 1
    mesh_data.MeshInfo.Num_TRIA3 = 2
    mesh_data.MeshInfo.Num_QUAD4 = 1
    # Create Regions
    reg_info_vol = io.CFSRegData(name="Vol")
    reg_info_vol.Dimension = 3
    reg_info_vol.Nodes = np.array([1, 2, 3, 4, 5, 6, 7, 8])
    reg_info_vol.Elements = np.array([1])
    reg_info_surf = io.CFSRegData(name="Surf1")
    reg_info_surf.Dimension = 2
    reg_info_surf.Nodes = np.array([1, 2, 3, 4])
    reg_info_surf.Elements = np.array([2, 3])
    reg_info_surf_group = io.CFSRegData(
        name="Surf2",
        is_group=True,
        dimension=2,
        nodes=np.array([5, 6, 7, 8]),
        elements=np.array([4]),
    )
    reg_info = [reg_info_vol, reg_info_surf, reg_info_surf_group]

    mesh_data.Regions = reg_info

    return mesh_data


@pytest.fixture
def dummy_CFSResultData_obj():
    """
    Create simple test containing scalar as well as complex vector data on multiple steps. Compatible with dummy_mesh
    """
    # Create Result
    step_value_list = np.array([(i + 1) / 5 for i in range(5)])
    data_test = np.array([1.0, 2, 3, 4, 5, 6, 7, 8]).reshape((-1, 1))
    data_test = np.array([data_test * (i + (1 + 1j)) for i in range(5)])
    data3_test_stp = np.array([[1.0, 2, 3], [4, 5, 6]])
    data3_test = np.array([data3_test_stp] * 5)

    result_data = io.CFSResultData(analysis_type=cfs_analysis_type.TRANSIENT, verbosity=v_def.all)
    result_data.add_data(
        data_test,
        step_values=step_value_list,
        quantity="quantity",
        region="Vol",
        restype=cfs_result_type.NODE,
        dim_names=["-"],
    )
    result_data.add_data(
        data3_test,
        step_values=step_value_list,
        quantity="quantity3",
        region="Surf1",
        restype=cfs_result_type.ELEMENT,
        dim_names=["x", "y", "z"],
        is_complex=False,
    )

    return result_data

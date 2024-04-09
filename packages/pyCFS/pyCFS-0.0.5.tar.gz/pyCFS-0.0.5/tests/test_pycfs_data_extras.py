import importlib.util
import time

import numpy as np
import pytest

from pyCFS.data import v_def
from pyCFS.data.extras import ensight_io, nihu_io, psv_io
from pyCFS.data.extras.vtk_to_cfs_element_types import vtk_to_cfs_elem_type
from pyCFS.data.io import mesh_from_coordinates_connectivity, CFSResultData, cfs_types, CFSWriter, CFSResultInfo
from pyCFS.data.util import list_search


@pytest.mark.skipif(importlib.util.find_spec("ansys") is None, reason="requires ansys-dpf-core>=0.10.0")
def test_ansys_io(working_directory="."):
    from pyCFS.data.extras import ansys_io

    rstfile = f"{working_directory}/data/extras/ansys_io/ansys_io.rst"
    filename_out = f"{working_directory}/data_tmp/extras/ansys_io/ansys_io.cfs"

    meshData = ansys_io.read_mesh(
        rstfile,
        create_core_regions=True,
        include_skin=False,
        include_named_selections=True,
    )

    ans_infos = [
        CFSResultInfo(
            quantity="displacement",
            region="V_core",
            res_type="Nodes",
            dim_names=["x", "y", "z"],
            analysis_type="harmonic",
            is_complex=True,
        ),
    ]

    result_data, result_reg_dict = ansys_io.read_result(rstfile, result_info=ans_infos)

    ansys_io.correct_region_node_element_id_order(regions_data=meshData.Regions, result_reg_dict=result_reg_dict)

    regData_keep = []
    for res_info in ans_infos:
        regData_keep.append(list_search(meshData.Regions, res_info.Region))

    meshData.drop_unused_nodes_elements(regData_keep)

    # Create Result
    with CFSWriter(filename_out) as h5writer:
        h5writer.create_file(mesh_data=meshData, result_data=result_data)


@pytest.mark.skipif(importlib.util.find_spec("vtk") is None, reason="requires vtk>=9.3.0")
def test_ensight_read(working_directory="."):
    file = f"{working_directory}/tests/data/extras/ensight_io/ensight_io.case"
    step = 2
    quantity = "U"

    filename_cfs = f"{working_directory}/tests/data_tmp/extras/ensight_io/ensight_io.cfs"

    start_time = time.time()

    reader = ensight_io.ensightInitReader(file=file)
    # data_fileInfo = ensightGetInfo(reader)
    data_geo = ensight_io.ensightReadMesh(reader, 0)
    # data_ts = ensightReadTimeStep(reader, quantity, step, 0)
    data, step_values = ensight_io.ensightReadTimeSeries(reader, quantity, 0)

    print(f"EnSight file read in {time.time() - start_time} seconds.")

    print(f"Value of first element in numpy array: {data[0][0]}")

    # Write read data into CFS type HDF5 file
    coord = data_geo["Coordinates"]
    conn = data_geo["Connectivity"]

    mesh = mesh_from_coordinates_connectivity(
        coordinates=coord, connectivity=conn, element_dimension=3, region_name="Block_1"
    )
    result = CFSResultData(analysis_type=cfs_types.cfs_analysis_type.TRANSIENT)
    result.add_data(
        data=np.array(data),
        step_values=step_values,
        quantity=quantity,
        region="Block_1",
        restype=cfs_types.cfs_result_type.ELEMENT,
        dim_names=["x", "y", "z"],
    )

    with CFSWriter(filename_cfs) as writer:
        writer.create_file(mesh_data=mesh, result_data=result)


@pytest.mark.skipif(importlib.util.find_spec("vtk") is None, reason="requires vtk>=9.3.0")
def test_ensight_read_poly(working_directory="."):
    file = f"{working_directory}/tests/data/extras/ensight_io/poly/data.case"
    quantities = ["pressure", "velocity"]
    regions = {"rigid": 1}

    filename_cfs = f"{working_directory}/tests/data_tmp/extras/ensight_io/poly/data.cfs"

    mesh, result = ensight_io.convert_to_cfs(file, quantities, regions, verbosity=v_def.all)

    result = mesh.convert_to_simplex(result_data=result)

    with CFSWriter(filename_cfs) as writer:
        writer.create_file(mesh_data=mesh, result_data=result)


def test_nihu(working_directory="."):
    file_out = f"{working_directory}/tests/data_tmp/extras/nihu_io/bem_result.cfs"

    file_mat = f"{working_directory}/tests/data/extras/nihu_io/result_surface.mat"

    mesh_surf, result_surf = nihu_io.convert_mat_to_cfs(file_mat=file_mat)

    file_mat = f"{working_directory}/tests/data/extras/nihu_io/result_field.mat"
    mat_names = ["p_field", "p_field_blocking"]
    cfs_names = ["acouPressure", "acouPressureBlocking"]
    dim_name_dict = {"acouPressureBlocking": ["B1", "B2", "B3", "B4", "B5"]}
    mesh_field, result_field = nihu_io.convert_mat_to_cfs(
        file_mat=file_mat,
        mat_mesh_name="field_mesh",
        mat_data_name_list=mat_names,
        cfs_name_list=cfs_names,
        reg_name="field",
        dim_name_dict=dim_name_dict,
    )
    # Merge meshes
    mesh_write = mesh_surf + mesh_field

    result_write = result_surf.combine_with(result_field)

    with CFSWriter(file_out) as h5writer:
        h5writer.create_file(mesh_data=mesh_write, result_data=result_write)


@pytest.fixture
def psv_frf_data_obj(working_directory="."):
    frf_data = np.load(
        f"{working_directory}/tests/data/extras/psv_io/surface_h1_receptance.npy", allow_pickle=True
    ).item()

    return frf_data


def test_psv_read(psv_frf_data_obj, working_directory="."):
    filename = f"{working_directory}/tests/data/extras/psv_io/surface_h1_receptance.unv"
    distfile = f"{working_directory}/tests/data/extras/psv_io/surface_dist.npy"

    frf_data = psv_io.read_frf(
        file_path=filename,
        frf_form="receptance",
        frf_type="H1",
        ref_channel=1,
        read_coordinates=True,
        read_elements=True,
        dist_file=distfile,
    )

    np.testing.assert_equal(psv_frf_data_obj, frf_data)


def test_psv_interpolate(psv_frf_data_obj):
    node_ids_interpolate = [10, 15]
    frf_data_interpolated = psv_io.interpolate_data_points(
        frf_data=psv_frf_data_obj, nodes_interpolate=node_ids_interpolate
    )


def test_psv_convert(psv_frf_data_obj, working_directory="."):

    psv_io.convert_frf_form(psv_frf_data_obj, frf_form="mobility")

    # np.save(
    #     f"{working_directory}/tests/data_tmp/extras/psv_io/surface_h1_receptance.npy",
    #     frf_data_interpolated,
    # )
    # frf_data2 = np.load(f'{working_directory}/tests/data/extras/psv/psv_io.npy', allow_pickle=True).item()
    # frf_data3 = np.load(f'{working_directory}/tests/data/extras/psv/psv_io.npy', allow_pickle=True).item()
    # combine_frf_3D(frf_data1=frf_data, frf_data2=frf_data2, frf_data3=frf_data3)

    mesh_data_write, result_data_write = psv_io.convert_to_cfs(
        psv_frf_data_obj, reg_name="S_PSV", quantitity_name="mechVelocity"
    )

    frf_data_converted = psv_io.convert_from_cfs(
        mesh_data_write,
        result_data_write,
        reg_name="S_PSV",
        quantitity_name="mechVelocity",
        psv_coord=psv_frf_data_obj["psv_coord"],
    )

    print(
        f"Conversion Error: {np.linalg.norm(np.array(frf_data_converted['data']) - np.array(psv_frf_data_obj['data']))}"
    )

    with CFSWriter(f"{working_directory}/tests/data_tmp/extras/psv_io/surface.cfs") as h5writer:
        h5writer.create_file(mesh_data=mesh_data_write, result_data=result_data_write)


def test_psv_drop_elements(psv_frf_data_obj):
    psv_io.drop_elements(psv_frf_data_obj, el_idx=[1, 2])


def test_psv_line_data(working_directory="."):

    # File with line data
    filename = f"{working_directory}/tests/data/extras/psv_io/line_h2_accelerance.unv"
    distfile = f"{working_directory}/tests/data/extras/psv_io/line.npy"

    frf_data = psv_io.read_frf(
        file_path=filename,
        frf_form="accelerance",
        frf_type="H2",
        ref_channel=1,
        read_coordinates=True,
        read_elements=True,
        dist_file=distfile,
    )

    mesh_data_write, result_data_write = psv_io.convert_to_cfs(
        frf_data, reg_name="S_PSV", quantitity_name="mechAcceleration"
    )

    with CFSWriter(f"{working_directory}/tests/data_tmp/extras/psv_io/line.cfs") as h5writer:
        h5writer.create_file(mesh_data=mesh_data_write, result_data=result_data_write)


def test_vtk_to_cfs_element_types():
    # example data for vtk element types
    vtk_elem_types = np.array([10, 12, 13, 14, 9, 5])

    # map automatically
    cfs_elem_types = vtk_to_cfs_elem_type(vtk_elem_types)

    # results of mapping
    print("VTK element types:")
    print(vtk_elem_types)
    print("CFS element types:")
    print(cfs_elem_types)  # expected: [9, 11, 16, 14, 6, 4]

    assert all(cfs_elem_types == [9, 11, 16, 14, 6, 4])

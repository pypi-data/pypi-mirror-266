"""
Module containing data processing utilities for reading PSV export data files
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pyuff
from typing import Dict, List, Tuple

from pyCFS.data import io
from pyCFS.data import util
from pyCFS.data.io import CFSMeshData, CFSResultData, CFSRegData
from pyCFS.data.io.cfs_types import cfs_element_type, cfs_result_type, cfs_analysis_type
from pyCFS.data.util import progressbar, vecnorm, trilateration


def read_frf(
    file_path: str,
    frf_form="mobility",
    frf_type="H1",
    ref_channel=1,
    read_coordinates=False,
    read_elements=False,
    dist_file: str | None = None,
) -> dict:
    """
    Reads data_frf from unv file, returns data_frf['frequency'] and data_frf['data'] in format usable in sdypy-EMA
    :param file_path: path to unv file, incl. file name
    :param frf_form: form of frf:
        'receptance' = displacement/force,
        'mobility' = velocity/force,
        'accelerance' = acceleration/force,
        'raw' = all datasets,
        _custom_string_ = data_frf labeled with _custom_string_
    :param frf_type: type of frf calculation: H1, H2
    :param ref_channel: channel number for reference signal
    :param read_coordinates: read Coordinates of nodes
    :param read_elements: read element Connectivity and elem_types (Triangle = 3, Quad = 4) (requires read_coordinates)
    :param dist_file: path to csv file containing the distance from the scanning head to each measurement point
    :return data_frf: dict with keys: 'Coordinates', 'Connectivity', 'elem_types', 'frequency',
                                  'frf_form', 'frf_type', 'data_frf', 'ref_channel'
    """

    uff_file = pyuff.UFF(file_path)

    if frf_form == "raw":
        print("Reading data_frf")
        raw_meas_data = uff_file.read_sets()

        data_frf = raw_meas_data

        return data_frf

    data_frf = {"frf_form": frf_form, "frf_type": frf_type, "ref_channel": ref_channel}

    if read_coordinates:
        print("Reading Coordinates")
        uff_setn_coord = int(np.where(uff_file.get_set_types() == 2411)[0].item())
        uff_set_coord = uff_file.read_sets(setn=uff_setn_coord)
        data_frf["Coordinates"] = np.vstack([uff_set_coord["x"], uff_set_coord["y"], uff_set_coord["z"]]).T
        node_renumbering = {v: k + 1 for k, v in dict(enumerate(uff_set_coord["node_nums"])).items()}

        if read_elements:
            print("Reading elements")
            uff_setn_elements = np.where(uff_file.get_set_types() == 2412)
            uff_setn_line_elements = np.where(uff_file.get_set_types() == 82)
            if uff_setn_elements[0].size == 0 and uff_setn_line_elements[0].size == 0:
                raise IOError(f"UNV file {file_path} doesn't contain element data_frf.")

            conn_shape = (0, 0)
            conn_tria = None
            conn_quad = None
            idx_tria = None
            idx_quad = None

            if uff_setn_elements[0].size > 0:
                uff_set_elements = uff_file.read_sets(setn=int(uff_setn_elements[0].item()))

                if "triangle" in uff_set_elements:
                    conn_tria = uff_set_elements["triangle"]["nodes_nums"]
                    conn_tria = np.vectorize(node_renumbering.get)(conn_tria)
                    idx_tria = uff_set_elements["triangle"]["element_nums"]
                    conn_shape = conn_tria.shape
                if "quad" in uff_set_elements:
                    conn_quad = uff_set_elements["quad"]["nodes_nums"]
                    conn_quad = np.vectorize(node_renumbering.get)(conn_quad)
                    idx_quad = uff_set_elements["quad"]["element_nums"]
                    conn_shape = (conn_shape[0] + conn_quad.shape[0], 4)

            uff_set_line_elements = uff_file.read_sets(setn=list(uff_setn_line_elements[0]))
            if type(uff_set_line_elements) is dict:  # in case of only 1 single line element
                uff_set_line_elements = [uff_set_line_elements]

            conn_line_lst = []
            idx_line_lst = []
            idx_line_offset = conn_shape[0]
            for i in range(len(uff_set_line_elements)):
                conn_line_lst.append(uff_set_line_elements[i]["nodes"][0:2])
                idx_line_lst.append(idx_line_offset + i + 1)
            conn_line = np.array(conn_line_lst)
            idx_line = np.array(idx_line_lst)
            if idx_line.size > 0:
                conn_line = np.vectorize(node_renumbering.get)(conn_line)
                conn_shape = (conn_shape[0] + conn_line.shape[0], max(conn_shape[1], 2))

            conn = np.zeros(conn_shape, dtype=int)
            elem_types = np.zeros((conn_shape[0]))
            if idx_tria is not None:
                conn[idx_tria - 1, 0:3] = conn_tria
                elem_types[idx_tria - 1] = 3

            if idx_quad is not None:
                conn[idx_quad - 1, :] = conn_quad
                elem_types[idx_quad - 1] = 4

            if idx_line.size > 0:
                conn[idx_line - 1, 0:2] = conn_line
                elem_types[idx_line - 1] = 2

            data_frf["Connectivity"] = conn
            data_frf["elem_types"] = elem_types

        if dist_file is not None:
            print("Computing PSV position from distance file: ", end="")
            dist_dict = np.load(dist_file, allow_pickle=True).item()
            dist = dist_dict["distance"]
            if "Coordinates" in dist_dict:
                print("Allocate distances based on Coordinates")
                # Reorder dist based on Coordinates
                dist_link = np.zeros((dist.size,), dtype=int)
                for i in range(dist.size):
                    dist_link[i] = np.where(
                        np.linalg.norm(
                            data_frf["Coordinates"] - dist_dict["Coordinates"][i, :],
                            axis=1,
                        )
                        < 1e-9
                    )[0].item()
                dist = dist[dist_link]
            else:
                print("No Coordinates in distance file. Make sure distances are ordered equally as Coordinates.")
            # Read from CSV
            # with open(dist_file) as f:
            #     dist = np.array([line for line in csv.reader(f)], dtype=float).flatten()
            data_frf["psv_coord"] = compute_psv_coord(coord=data_frf["Coordinates"], dist=dist)

    print("Reading frequency steps: ", end="")
    uff_setn_data = np.where(uff_file.get_set_types() == 58)[0]
    print(f"Found {uff_setn_data.size} steps")
    data_frf["frequency"] = uff_file.read_sets(setn=uff_setn_data[0])["x"]

    data_frf["data"] = []
    frf_form_dict = {
        "receptance": "Weg",
        "mobility": "Geschwindigkeit",
        "accelerance": "Beschleunigung",
    }
    if frf_form in frf_form_dict:
        id2_str = f"Vib  Ref{ref_channel}  {frf_type} {frf_form_dict[frf_form]} / Kraft"
    else:
        id2_str = frf_form
    for i in progressbar(uff_setn_data, "Reading dataset: "):
        entry = uff_file.read_sets(setn=i)

        if entry["id2"] == id2_str:
            data_frf["data"].append(entry["data"])

    return data_frf


def convert_frf_form(frf_data: Dict, frf_form: str) -> Dict:
    # noinspection LongLine
    """
    Converts frf_data of type 'receptance', 'mobility', or 'accelerance' to another one of these.

    Parameters
    ----------
    frf_data : dict
        dict with keys: 'Coordinates', 'Connectivity', 'elem_types', 'frequency', 'frf_form', 'frf_type', 'data_frf', 'ref_channel'
    frf_form : str
        form of frf: 'receptance' = displacement/force, 'mobility' = velocity/force, 'accelerance' = acceleration/force,

    Returns
    -------
    frf_data : dict
        dict with keys: 'Coordinates', 'Connectivity', 'elem_types', 'frequency', 'frf_form', 'frf_type', 'data_frf', 'ref_channel'

    """
    if frf_form not in ["receptance", "mobility", "accelerance"]:
        raise Exception('conversion only supports "receptance", "mobility", "accelerance" as target form!')

    if frf_data["frf_form"] == "receptance":
        if frf_form == "mobility":
            # noinspection PyMissingOrEmptyDocstring

            def operator(data: np.ndarray) -> np.ndarray:
                return data * 1j * frf_data["frequency"] * 2 * np.pi

        elif frf_form == "accelerance":
            # noinspection PyMissingOrEmptyDocstring

            def operator(data: np.ndarray) -> np.ndarray:
                return data * (frf_data["frequency"] * 2 * np.pi) ** 2

        else:
            return frf_data
    elif frf_data["frf_form"] == "mobility":
        if frf_form == "receptance":
            # noinspection PyMissingOrEmptyDocstring

            def operator(data: np.ndarray) -> np.ndarray:
                return data / (1j * frf_data["frequency"] * 2 * np.pi)

        elif frf_form == "accelerance":
            # noinspection PyMissingOrEmptyDocstring

            def operator(data: np.ndarray) -> np.ndarray:
                return data * 1j * frf_data["frequency"] * 2 * np.pi

        else:
            return frf_data
    elif frf_data["frf_form"] == "accelerance":
        if frf_form == "receptance":
            # noinspection PyMissingOrEmptyDocstring

            def operator(data: np.ndarray) -> np.ndarray:
                return data / ((frf_data["frequency"] * 2 * np.pi) ** 2)

        elif frf_form == "mobility":

            # noinspection PyMissingOrEmptyDocstring
            def operator(data: np.ndarray) -> np.ndarray:
                return data / (1j * frf_data["frequency"] * 2 * np.pi)

        else:
            return frf_data
    else:
        raise Exception('conversion only supports "receptance", "mobility", "accelerance" frf data!')

    frf_data["frf_form"] = frf_form
    frf_data["data"] = list(operator(np.array(frf_data["data"])))
    return frf_data


def interpolate_data_points(frf_data: Dict, nodes_interpolate: np.ndarray | List[int], interpolation_exp=0.5) -> dict:
    """
    Interpolate data sequentially from neighboring elements with valid or previously interpolated data using Shepards
    method. Ordering based on number of neighbors containing valid data.
    TODO: Investigate PINN-based interpolation
    """
    coord = frf_data["Coordinates"]
    conn = frf_data["Connectivity"]

    if type(nodes_interpolate) is np.ndarray:
        nodes_interpolate = list(nodes_interpolate.flatten())

    # Get neighbor nodes
    neighbor_list = []
    for node in progressbar(nodes_interpolate, "Get neighbors:   ", size=25):
        conn_idx = np.where(conn == node)[0]
        neighbor_set = set(conn[conn_idx].flatten())
        neighbor_set.remove(node)
        if 0 in neighbor_set:
            neighbor_set.remove(0)
        neighbor_list.append([node, neighbor_set])

    # Sort neighbor list by number of node with valid data
    neighbor_list.sort(key=lambda x: len(x[1].difference(nodes_interpolate)), reverse=True)
    nodes_interpolate_sorted = [item[0] for item in neighbor_list]
    frf_data["nodes_interpolated"] = np.array(nodes_interpolate_sorted)
    # Perform interpolation
    data = np.array(frf_data["data"])
    for i in progressbar(range(len(neighbor_list)), "Performing interpolation: ", size=16):
        node_idx = neighbor_list[i][0] - 1
        neighbor_data_ids = neighbor_list[i][1].difference(nodes_interpolate_sorted[i:])
        neighbor_idx = np.array([x - 1 for x in neighbor_data_ids], dtype=int)
        node_coord = coord[node_idx, :]
        neighbor_coord = coord[neighbor_idx, :]
        dist = np.linalg.norm(neighbor_coord - node_coord, axis=1)
        dmax = 1.01 * max(dist)
        w = ((dmax - dist) / (dmax * dist)) ** interpolation_exp
        w /= sum(w)

        data[node_idx, :] = w.reshape((w.shape[0], 1)).T @ data[neighbor_idx, :]

    frf_data["data"] = list(data)

    return frf_data


def compute_psv_coord(coord: np.ndarray, dist: np.ndarray, eps=1e-9) -> np.ndarray:
    """
    Computation of the location of the PSV scan head based on given distances.
    """
    if coord.shape[0] < 4:
        raise Exception("Not enough data points to compute unique location. Requires a minimum of 4 locations")

    pos_list = []
    for i in range(0, coord.shape[0] - 3, 2):

        offset = i
        k1 = trilateration(
            coord[offset + 0, :],
            coord[offset + 1, :],
            coord[offset + 2, :],
            dist[offset + 0],
            dist[offset + 1],
            dist[offset + 2],
        )
        offset = i + 1
        k2 = trilateration(
            coord[offset + 0, :],
            coord[offset + 1, :],
            coord[offset + 2, :],
            dist[offset + 0],
            dist[offset + 1],
            dist[offset + 2],
        )
        pos_list.append(k1)
        for pos1 in k1:
            for pos2 in k2:
                if np.linalg.norm(pos2 - pos1) < eps:
                    return pos1
        print(
            f"Warning: Could not find unique location based on 4 distances. Offset: {offset}",
            end="\r",
            flush=True,
        )
    print(
        f"Warning: Could not find unique location based on 4 distances. Offset: 0 - {offset}",
        flush=True,
    )
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    for pos in pos_list:
        ax.scatter(pos[0][0], pos[0][1], pos[0][2])
        ax.scatter(pos[1][0], pos[1][1], pos[1][2])
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")  # type: ignore[attr-defined]
    plt.title("PSV location candidates")
    plt.show()
    raise Exception("Could not find unique location. Check Coordinates and distances.")


def convert_to_cfs(
    psv_data: Dict,
    reg_name="surface",
    quantitity_name="data",
    analysis_type=cfs_analysis_type.HARMONIC,
    scalar_data=False,
    data_direction: np.ndarray | None = None,
) -> Tuple[CFSMeshData, CFSResultData]:
    """Create CFS data structures from psv_data dict"""
    type_link = {
        2: cfs_element_type.LINE2,
        3: cfs_element_type.TRIA3,
        4: cfs_element_type.QUAD4,
    }
    elem_types = np.vectorize(type_link.get)(psv_data["elem_types"])

    reg_data = []
    reg_all = CFSRegData(name=reg_name, dimension=2)
    reg_all.Nodes = np.array([i + 1 for i in range(psv_data["Coordinates"].shape[0])])
    reg_all.Elements = np.array([i + 1 for i in range(psv_data["Connectivity"].shape[0])])
    reg_data.append(reg_all)
    # if any(elem_types == cfs_element_type.TRIA3) or any(elem_types == cfs_element_type.QUAD4):
    #     reg_surf = CFSRegData(name=f'{reg_name}_2D', dimension=1)
    #     reg_surf.Nodes = np.array([i + 1 for i in range(MeshInfo.NumNodes)])
    #     reg_surf.Elements = \
    #         np.where(np.logical_or(elem_types == cfs_element_type.TRIA3, elem_types == cfs_element_type.QUAD4))[0] + 1
    #     reg_data.append(reg_surf)
    # if any(elem_types == cfs_element_type.LINE2):
    #     reg_line = CFSRegData(name=f'{reg_name}_1D', dimension=1)
    #     reg_line.Nodes = np.array([i + 1 for i in range(MeshInfo.NumNodes)])
    #     reg_line.Elements = np.where(elem_types == cfs_element_type.LINE2)[0] + 1
    #     reg_data.append(reg_line)

    mesh_data = CFSMeshData(
        coordinates=psv_data["Coordinates"],
        connectivity=psv_data["Connectivity"],
        types=elem_types,
        regions=reg_data,
    )

    result_data = CFSResultData(analysis_type=analysis_type)
    if scalar_data:
        data = [d for d in list(np.array(psv_data["data"]).T)]
        dim_names = None
    else:
        dim_names = ["x", "y", "z"]
        if "data3D" in psv_data:
            data = list(psv_data["data3D"].swapaxes(0, 2))
        elif data_direction is None:
            if "psv_coord" in psv_data:
                dir_unit_vec = util.vecnorm(psv_data["Coordinates"] - psv_data["psv_coord"], axis=1)
                data = [np.array([d, d, d]).T * dir_unit_vec for d in list(np.array(psv_data["data"]).T)]
            else:
                raise Exception(
                    '"psv_coord" is not defined in frf_data. Please specify data_direction or define "psv_coord"!'
                )
        else:
            data = [np.outer(d, data_direction) for d in list(np.array(psv_data["data"]).T)]

    result_data.add_data(
        data=np.array(data),
        step_values=psv_data["frequency"],
        quantity=quantitity_name,
        region=reg_name,
        restype=cfs_result_type.NODE,
        dim_names=dim_names,
        is_complex=True,
    )

    return mesh_data, result_data


def convert_from_cfs(
    mesh_data: io.CFSMeshData,
    result_data: io.CFSResultData,
    psv_data=None,
    reg_name="surface",
    quantitity_name="data",
    psv_coord: np.ndarray | None = None,
) -> dict:
    """Convert CFS data structures to psv_data dict."""
    if psv_data is None:
        psv_data = dict()

    psv_data["Coordinates"] = mesh_data.get_region_coordinates(reg_name)
    psv_data["Connectivity"] = mesh_data.get_region_connectivity(reg_name)
    type_link = {
        cfs_element_type.LINE2: 2,
        cfs_element_type.TRIA3: 3,
        cfs_element_type.QUAD4: 4,
    }
    psv_data["elem_types"] = np.vectorize(type_link.get)(mesh_data.Types)

    psv_data["frequency"] = result_data.StepValues

    r_array = result_data.get_data_array(quantity=quantitity_name, region=reg_name, restype=cfs_result_type.NODE)

    if psv_coord is None and len(r_array.DimNames) > 1:
        psv_data["data3D"] = list(r_array.DataArray.swapaxes(0, 1))

    elif len(r_array.DimNames) == 1:
        psv_data["data"] = list(r_array.DataArray.swapaxes(0, 1))
    else:
        psv_data["psv_coord"] = psv_coord
        dir_vec = util.vecnorm(psv_data["Coordinates"] - psv_data["psv_coord"], axis=1)

        r_array = result_data.get_data_array(quantity=quantitity_name, region=reg_name, restype=cfs_result_type.NODE)
        psv_data["data"] = list(
            np.sum(r_array.DataArray * np.tile(dir_vec, (r_array.shape[0], 1, 1)), axis=2).swapaxes(0, 1)
        )

    return psv_data


def combine_frf_3D(frf_data1: Dict, frf_data2: Dict, frf_data3, eps=1e-9) -> Dict:
    """Compute 3D FRF from 3 single frf_data including psv_coord information."""
    data1 = frf_data1["data"]
    data2 = frf_data2["data"]
    data3 = frf_data3["data"]

    data_coord = frf_data1["Coordinates"]
    if (
        np.linalg.norm(data_coord - frf_data2["Coordinates"]) > eps
        or np.linalg.norm(data_coord - frf_data3["Coordinates"]) > eps
    ):
        raise Exception("FRF data must have identical data locations")

    psv_coord1 = frf_data1["psv_coord"]
    psv_coord2 = frf_data2["psv_coord"]
    psv_coord3 = frf_data3["psv_coord"]
    data_3d = []
    for i in progressbar(range(data_coord.shape[0]), "Combining FRF: "):
        dir_stack = np.array(
            [
                vecnorm(psv_coord1 - data_coord[i, :]),
                vecnorm(psv_coord2 - data_coord[i, :]),
                vecnorm(psv_coord3 - data_coord[i, :]),
            ]
        )

        data_stack = np.array([data1[i], data2[i], data3[i]])
        data_3d.append(np.linalg.solve(dir_stack.T, data_stack))

    frf_data_3d = frf_data1.copy()
    frf_data_3d["data"] = None
    frf_data_3d["psv_coord"] = [psv_coord1, psv_coord2, psv_coord3]
    frf_data_3d["data3D"] = np.array(data_3d).swapaxes(0, 1)

    return frf_data_3d


def drop_elements(psv_data: Dict, el_idx: List[int] | np.ndarray):
    """Drop elements based on indices."""
    psv_data["elem_types"] = np.delete(psv_data["elem_types"], el_idx, axis=0)

    nodes = np.unique(psv_data["Connectivity"].astype(int))
    conn_new = np.delete(psv_data["Connectivity"].astype(int), el_idx, axis=0)
    nodes_new = np.unique(conn_new)
    # Remove zero entry
    nodes = np.delete(nodes, np.where(nodes == 0)[0])
    nodes_new = np.delete(nodes_new, np.where(nodes_new == 0)[0])

    # Extract Coordinates
    _, idx_intersect, node_idx = np.intersect1d(nodes_new, nodes, return_indices=True)
    psv_data["Coordinates"] = psv_data["Coordinates"][node_idx, :]

    # Renumber Connectivity
    renumber_dict = {node_idx[idx] + 1: idx + 1 for idx in range(node_idx.size)}
    renumber_dict[0] = 0
    psv_data["Connectivity"] = np.vectorize(renumber_dict.get)(conn_new)

    # Extract data
    if "data" in psv_data:
        psv_data["data"] = list(np.array(psv_data["data"])[node_idx])

    if "data3D" in psv_data:
        psv_data["data3D"] = list(np.array(psv_data["data3D"])[node_idx])

"""
Module containing data processing utilities for reading Ansys RST files
"""

from __future__ import annotations

import importlib.util
import numpy as np

if importlib.util.find_spec("ansys") is None:
    raise ModuleNotFoundError(
        "Missing dependency for submodule pyCFS.data.extras.ansys_io. "
        "To install pyCFS with all required dependencies run 'pip install -U pyCFS[data]'"
    )

from ansys.dpf import core as dpf
from typing import List, Tuple, Dict

from pyCFS.data.extras import ansys_to_cfs_element_types
from pyCFS.data import io, v_def
from pyCFS.data.io import cfs_types
from pyCFS.data.extras.vtk_to_cfs_element_types import vtk_to_cfs_elem_type
from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type
from pyCFS.data.util import (
    progressbar,
    vprint,
    connectivity_list_to_matrix,
)


def get_element_dim(e: dpf.elements.Element) -> int:
    elemTypeDimDict = {
        dpf.element_types.Tet10: 3,
        dpf.element_types.Hex20: 3,
        dpf.element_types.Wedge15: 3,
        dpf.element_types.Pyramid13: 3,
        dpf.element_types.Tri6: 2,
        dpf.element_types.Quad8: 2,
        dpf.element_types.Tet4: 3,
        dpf.element_types.Hex8: 3,
        dpf.element_types.Wedge6: 3,
        dpf.element_types.Pyramid5: 3,
        dpf.element_types.Tri3: 2,
        dpf.element_types.Quad4: 2,
        dpf.element_types.Line2: 1,
        dpf.element_types.Point1: 0,
    }

    return elemTypeDimDict[e.type]


class CFSMeshInfo(io.CFSMeshInfo):
    def __init__(self) -> None:
        super().__init__()

    def update_with_element(self, e):
        if e.type == dpf.element_types.Tet10:
            self.Num_TET10 += 1
            self.Num3DElems += 1
            self.QuadraticElems = True
        elif e.type == dpf.element_types.Hex20:
            self.Num_HEXA20 += 1
            self.Num3DElems += 1
            self.QuadraticElems = True
        elif e.type == dpf.element_types.Pyramid13:
            self.Num_PYRA13 += 1
            self.Num3DElems += 1
            self.QuadraticElems = True
        elif e.type == dpf.element_types.Wedge15:
            self.Num_WEDGE15 += 1
            self.Num3DElems += 1
            self.QuadraticElems = True
        elif e.type == dpf.element_types.Quad8:
            self.Num_QUAD8 += 1
            self.Num2DElems += 1
            self.QuadraticElems = True
        elif e.type == dpf.element_types.Tri6:
            self.Num_TRIA6 += 1
            self.Num2DElems += 1
            self.QuadraticElems = True
        elif e.type == dpf.element_types.Line2:
            self.Num_LINE2 += 1
            self.Num1DElems += 1
        elif e.type == dpf.element_types.Point1:
            self.Num_POINT += 1
        else:
            raise Exception(f"Type {e.type} needs to be added to 'update_with_element' method")


class CFSMeshData(io.CFSMeshData):
    def __init__(self, include_skin=True, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.MeshInfo: CFSMeshInfo = CFSMeshInfo()
        if self.Coordinates.size > 0 and self.Types.size > 0:
            self.update_info()

        self.ElemIDs: np.ndarray | None = None
        self.NodeIDs: np.ndarray | None = None
        self._ElemIDs_vol: np.ndarray | None = None
        self._ElemIDs_skin: np.ndarray | None = None
        self._include_skin = include_skin

    def read_grid(self, meshed_region: dpf.MeshedRegion, processes: int | None = None):
        # TODO implement skin extraction
        grid = meshed_region.grid
        self.Coordinates = np.array(grid.points)
        conn_list = grid.cell_connectivity
        conn_offset = grid.offset
        self.Types = vtk_to_cfs_elem_type(grid.celltypes)
        self.Connectivity = (
            connectivity_list_to_matrix(
                connectivity_list=conn_list,
                offsets=conn_offset,
                processes=processes,
                verbose=self._Verbosity >= v_def.debug,
            )
            + 1
        )
        self.update_info()

        # self.NodeIDs = np.array(list(meshed_region.nodes.mapping_id_to_index.keys()))
        # node_offset = self.NodeIDs[1:] - self.NodeIDs[0:-1]
        # # remove offset
        # self.NodeIDs -= self.NodeIDs[0] - 1
        self.NodeIDs = np.array([i + 1 for i in range(self.MeshInfo.NumNodes)])
        node_id_dict = {x: i + 1 for i, x in enumerate(list(meshed_region.nodes.mapping_id_to_index.keys()))}
        # self.NodeIDs = meshed_region.nodes.scoping.ids

        self.ElemIDs = np.array([i + 1 for i in range(self.MeshInfo.NumElems)])
        elem_id_dict = {x: i + 1 for i, x in enumerate(list(meshed_region.elements.mapping_id_to_index.keys()))}
        # self.ElemIDs = np.array(list(meshed_region.elements.mapping_id_to_index.keys()))
        # self.ElemIDs = meshed_region.elements.scoping.ids
        self._ElemIDs_vol = self.ElemIDs[
            self.Types >= cfs_types.cfs_element_type.TET4
        ]  # TET4 is first defined 3D element

        return node_id_dict, elem_id_dict

    def read_nodes_elements(self, meshed_region: dpf.MeshedRegion):
        # TODO deprecated (slow performance)
        print("-- Nodes")
        node_id_dict = self._read_nodes(meshed_region)
        print("-- Elements")
        elem_id_dict = self._read_elements(meshed_region)
        self.update_info()

        return node_id_dict, elem_id_dict

    def _read_nodes(self, meshed_region: dpf.MeshedRegion):
        coord = meshed_region.nodes.coordinates_field.data
        node_ids = list(meshed_region.nodes.mapping_id_to_index.keys())
        # coord = []
        # node_ids = []
        # for n in meshed_region.nodes:
        #     node_ids.append(n.id)
        #     coord.append(n.Coordinates)
        # coord = np.array(coord)
        # TODO investigate, what causes missing node IDs
        node_id_dict = None
        if max(node_ids) > meshed_region.nodes.n_nodes:
            vprint(
                "There are missing node IDs. Renumbering nodes...",
                verbose=self._Verbosity >= v_def.release,
            )
            # Remove missing IDs
            node_id_dict = {x: i + 1 for i, x in enumerate(node_ids)}
            node_ids = [i + 1 for i in range(len(node_ids))]

        self.Coordinates = coord.copy()
        self.NodeIDs = np.ndarray(node_ids)

        return node_id_dict

    def _read_elements(self, meshed_region: dpf.MeshedRegion):
        conn = []
        elem_ids = []
        elem_types = []
        # Volume mesh
        # print('Reading volume mesh')
        # dim = 0
        # Get element IDs
        id_idx_map = meshed_region.elements.mapping_id_to_index
        elem_ids = list(id_idx_map.keys())
        # Sort in ascending order
        elem_ids.sort()

        # missing_ids = []
        # for i in range(meshed_region.elements.n_elements):
        #     if (i+1) not in id_idx_map:
        #         missing_ids.append(i)
        # TODO speed up reading (e.g. multithreading)
        # def _read_volume_mesh(elem_id, elements):
        #     e = elements.element_by_id(elem_id)
        #     return e.type, e.node_ids
        # print('Reading volume mesh: ', end='')
        # with Pool(processes=None) as pool:
        #     t_start = time.time()
        #     for i, res in pool.map(partial(_read_volume_mesh, elements=meshed_region.elements), elem_ids):
        #         elem_types.append(res[1])
        #         conn.append(res[2])
        # print(f' | Elapsed time: {datetime.timedelta(seconds=int(time.time() - t_start))}')
        for elem_id in progressbar(
            elem_ids,
            "Reading volume mesh: ",
            50,
            verbose=self._Verbosity >= v_def.release,
        ):
            # Some elements might
            e = meshed_region.elements.element_by_id(elem_id)
            # dim = max(dim, get_element_dim(e))
            # elem_ids.append(e.id)
            elem_types.append(e.type)
            conn.append(e.node_ids)

        # Non-conforming interfaces cause missing element IDs
        elem_id_dict = None
        if max(elem_ids) > meshed_region.elements.n_elements:
            vprint(
                "There are missing element IDs. Renumbering elements...",
                verbose=self._Verbosity >= v_def.release,
            )
            # Remove missing IDs
            elem_id_dict = {x: i + 1 for i, x in enumerate(elem_ids)}
            elem_ids = [i + 1 for i in range(len(elem_ids))]

        self._ElemIDs_vol = np.array(elem_ids.copy())
        if self._include_skin:
            # Surface mesh
            # print('Generating surface mesh')
            skin_op = dpf.operators.mesh.skin(mesh=meshed_region)
            skin_meshed_region = skin_op.outputs.mesh()
            # Add new elements to elem_ids
            # skin_scp_op = dpf.operators.scoping.from_mesh(mesh=skin_meshed_region, requested_location='Elemental')
            # scp_skin_mesh = skin_scp_op.outputs.scoping()
            # skin_elem_ids = scp_skin_mesh.ids.copy() + max(elem_ids)
            skin_elem_ids = np.array(list(skin_meshed_region.elements.mapping_id_to_index.keys())) + max(elem_ids)
            elem_ids.extend(skin_elem_ids.tolist())
            # Element Connectivity and types
            skin_conn = []
            for e in progressbar(skin_meshed_region.elements, "Generating surface mesh: ", 46):
                elem_types.append(e.type)
                skin_conn.append(e.node_ids)
            self._ElemIDs_skin = skin_elem_ids
            self._Connectivity_skin = skin_conn
            conn.extend(skin_conn)

        # Homogenize nested list with zero entries
        length = max(map(len, conn))

        self.Connectivity = np.array([nid + [0] * (length - len(nid)) for nid in conn])
        self.Types = ansys_to_cfs_element_types.dpf_to_cfs_elem_type(np.array(elem_types))
        self.ElemIDs = np.array(elem_ids)

        return elem_id_dict

    def core_regions(self) -> List[io.CFSRegData]:
        """
        Creates Regions of volume and skin surface
        :return: CFSRegData objects for volume and skin surface
        """
        reg_vol = CFSRegData(
            name="V_core",
            elements=np.array(self._ElemIDs_vol),
            nodes=np.array(self.NodeIDs),
            dimension=3,
        )
        if self._include_skin:
            reg_surf = CFSRegData(
                name="S_core",
                elements=np.array(self._ElemIDs_skin),
                nodes=np.array(self.NodeIDs),
                dimension=3,
            )
            return [reg_vol, reg_surf]
        return [reg_vol]

    def get_skin_conn_index(self, elem_conn: np.ndarray):
        """
        Finds element index in overall Connectivity
        :param elem_conn: element node ids
        :return: idx of element in skin Connectivity
        """
        if self._ElemIDs_vol is None:
            raise ValueError("Element volume IDs not properly defined!")
        return self._Connectivity_skin.index(elem_conn) + len(self._ElemIDs_vol)


class CFSRegData(io.CFSRegData):
    def __init__(self, name: str, elements=np.empty(()), nodes=np.empty(()), dimension=-1):
        super().__init__(name, elements, nodes, dimension)

    def get_regInfo(
        self,
        data_sources: dpf.DataSources,
        meshed_region: dpf.MeshedRegion,
        mesh_data: CFSMeshData,
        node_id_dict: Dict | None = None,
        elem_id_dict: Dict | None = None,
        plot_regions=False,
        skip_skin_region=False,
    ):
        # TODO seems to get wrong indicies in certain cases
        scpReg = meshed_region.named_selection(self.Name)
        if scpReg.location == "Elemental":
            # Named selection is a volume region
            # Element IDs
            if elem_id_dict is None:
                self.Elements = np.array(scpReg.ids)
            else:
                self.Elements = np.vectorize(elem_id_dict.get)(np.array(scpReg.ids))

            # Node IDs
            scp_op = dpf.operators.scoping.on_named_selection(
                named_selection_name=self.Name,
                data_sources=data_sources,
                requested_location="Nodal",
                int_inclusive=0,
            )
            scpRegNodal = scp_op.outputs.mesh_scoping()
            if node_id_dict is None:
                self.Nodes = np.array(scpRegNodal.ids)
            else:
                self.Nodes = np.vectorize(node_id_dict.get)(np.array(scpRegNodal.ids))
            self.Dimension = 3
        elif scpReg.location == "Nodal":
            if skip_skin_region:
                return False
            # Named selection is a surface region
            # Get surface mesh
            skin_op = dpf.operators.mesh.skin(mesh=meshed_region, mesh_scoping=scpReg)
            skin_mesh = skin_op.outputs.mesh()
            if plot_regions:
                skin_mesh.plot()
            # ext_layer_op = dpf.operators.mesh.external_layer(mesh=meshed_region)
            # ext_layer_mesh = ext_layer_op.outputs.mesh()
            # Node IDs
            # self.Nodes = np.array(scpReg.ids)
            nids = list(skin_mesh.nodes.mapping_id_to_index.keys())
            nids.sort()
            self.Nodes = np.array(nids)
            # Element IDs
            regElemIDs = []
            dim = 0
            for e in progressbar(skin_mesh.elements, "Retrieving Element IDs: ", 47):
                dim = max(dim, get_element_dim(e))
                # Get MultiStepID from ElemIDs
                if mesh_data.ElemIDs is None:
                    raise ValueError("MeshData object not properly defined")
                regElemIDs.append(mesh_data.ElemIDs[mesh_data.get_skin_conn_index(e.node_ids)])
            self.Elements = np.array(regElemIDs)
            self.Dimension = dim
        return True


def prepare_meshInfo(meshInfo):
    conn = meshInfo["Connectivity"]

    conn_np = np.zeros([len(conn), len(max(conn, key=lambda x: len(x)))])
    for i, j in enumerate(conn):
        conn_np[i][0 : len(j)] = j

    meshInfo["Connectivity"] = conn_np


def read_mesh(
    rstfile: str,
    create_core_regions=True,
    plot_mesh=False,
    include_skin=False,
    include_named_selections=False,
) -> CFSMeshData:
    # TODO read named selections seems to be inconsistent to get correct indices
    #  include skin not implemented for read_grid function,
    #  read_nodes_elements deprecated (slow performance)
    if not create_core_regions and not include_named_selections:
        raise Exception("Either core regions or named selections have to be included!")
    print("Reading Mesh")
    data_src = dpf.DataSources(rstfile)
    model = dpf.Model(data_src)

    # %% Read overall mesh
    meshed_region = model.metadata.meshed_region
    if plot_mesh:
        meshed_region.plot()
    mesh_data = CFSMeshData(include_skin=include_skin)
    # node_id_dict, elem_id_dict = MeshData.read_nodes_elements(meshed_region)
    node_id_dict, elem_id_dict = mesh_data.read_grid(meshed_region)

    # %% Read regions
    print("-- Regions")
    if create_core_regions:
        reg_info = list(mesh_data.core_regions())
    else:
        reg_info = []

    # Get Named regions
    if include_named_selections:
        named_regs = meshed_region.available_named_selections
        for regName in named_regs:
            if regName[0] == "_":
                print(f"Skipping hidden region {regName}")
                continue
            print(f"Reading region {regName}")
            reg_data = CFSRegData(regName)
            flag_reg_read = reg_data.get_regInfo(
                data_src,
                meshed_region,
                mesh_data,
                node_id_dict=node_id_dict,
                elem_id_dict=elem_id_dict,
                plot_regions=plot_mesh,
                skip_skin_region=not include_skin,
            )
            if flag_reg_read:
                reg_info.append(reg_data)
            else:
                print(" - Skipping surface region")

    mesh_data.Regions = reg_info

    return mesh_data


def read_fields_container(
    fields_container: dpf.FieldsContainer, step_values: List, is_complex=False
) -> Tuple[List[np.ndarray], Dict[str, int]]:
    flag_complex_warn = False
    data = []
    f = None
    for i in range(1, len(step_values) + 1):
        f = fields_container.get_fields_by_time_complex_ids(timeid=i, complexid=None)
        data_step_tuple = tuple(np.array(x.data) for x in f)
        if is_complex:
            if len(data_step_tuple) == 1:
                # Add zero imaginary part if result doesn't contain it
                data_step_tuple = (*data_step_tuple, np.zeros(data_step_tuple[0].shape))
                flag_complex_warn = True
            data_step = data_step_tuple[0] + data_step_tuple[1] * 1j
        else:
            if len(data_step_tuple) > 1:
                print("Warning: Input data contains complex valued results. Ignored imaginary part of result data")
            data_step = data_step_tuple[0]
        data.append(data_step)
    if flag_complex_warn:
        print("Warning: Input data contains real valued results only. Added zero imaginary part!")
    if f:
        if f[0].location == "Nodal":
            ind, _ = f[0].meshed_region.nodes.map_scoping(f[0].scoping)
            result_ind = {"Nodes": ind + 1}
        else:  # f[0].location == 'Elemental'
            ind, _ = f[0].meshed_region.elements.map_scoping(f[0].scoping)
            result_ind = {"Elements": ind + 1}
    else:
        raise ValueError("Result field empty")
    return data, result_ind


def get_result_from_results_container(results_container: dpf.model.Results, quantity):
    if quantity == "displacement":
        result = results_container.displacement
    elif quantity == "stress":
        result = results_container.stress
    else:
        raise Exception(f"Evaluation of result {quantity} not implemented")
    return result


def read_result(rstfile: str, result_info: List[io.CFSResultInfo]):
    print("Reading Results")
    data_src = dpf.DataSources(rstfile)
    model = dpf.Model(data_src)
    # %% Frequency steps
    print("-- Steps")
    freq = model.metadata.time_freq_support.time_frequencies

    # Create CFSResultData object
    result_data = io.CFSResultData(analysis_type=cfs_analysis_type(result_info[0].AnalysisType))

    result_reg_dict = {}
    for res_info in result_info:
        print(f"-- {res_info}")
        if res_info.Quantity is None or res_info.Region is None:
            raise ValueError("ResultInfo not properly defined!")
        results_container = model.results
        result_container = get_result_from_results_container(results_container, res_info.Quantity)
        if res_info.Region in model.metadata.meshed_region.available_named_selections:
            fields_container = result_container.on_all_time_freqs.on_named_selection(res_info.Region).eval()
        elif res_info.Region == "V_core":
            # Get result on overall domain
            fields_container = result_container.on_all_time_freqs.eval()
        else:
            print(f"Result has no named selection {res_info.Region} ... skipping")
            continue
        data, result_ind = read_fields_container(fields_container, freq, is_complex=res_info.IsComplex)
        result_reg_dict[res_info.Region] = result_ind
        if res_info.ResType == "Nodes":
            res_type = cfs_result_type.NODE
        elif res_info.ResType == "Elements":
            res_type = cfs_result_type.ELEMENT
        else:
            raise NotImplementedError(f"Unexpected result type {res_info.ResType}")

        result_data.add_data(
            np.array(data),
            step_values=freq.data,
            quantity=res_info.Quantity,
            region=res_info.Region,
            restype=res_type,
            dim_names=res_info.DimNames,
            is_complex=res_info.IsComplex,
        )

    return result_data, result_reg_dict


def correct_region_node_element_id_order(regions_data: List[CFSRegData], result_reg_dict: Dict):
    # Correct region node/element id order
    for reg in result_reg_dict:
        print(f"Checking region node/element ids: {reg} ... ", end="")
        idx = [reg_obj.Name for reg_obj in regions_data].index(reg)
        if "Nodes" in result_reg_dict[reg]:
            # Sanity Check
            a = regions_data[idx].Nodes.copy()
            b = result_reg_dict[reg]["Nodes"].copy()
            if np.array_equal(a, b):
                print(" ids matching with result data.")
            else:
                a.sort()
                b.sort()
                if np.array_equal(a, b):
                    print(" ids corrected from result data.")
                    regions_data[idx].Nodes = result_reg_dict[reg]["Nodes"].copy()
                else:
                    raise Exception("Region of result data does not match corresponding region of mesh data")
        if "Elements" in result_reg_dict[reg]:
            # Sanity Check
            a = regions_data[idx].Elements.copy()
            b = result_reg_dict[reg]["Elements"].copy()
            if np.array_equal(a, b):
                print(" ids matching with result data.")
            else:
                a.sort()
                b.sort()
                if not np.array_equal(a, b):
                    raise Exception("Region of result data does not match corresponding region of mesh data")
                regions_data[idx].Elements = result_reg_dict[reg]["Elements"].copy()

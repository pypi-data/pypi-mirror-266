"""
Module containing data processing utilities for writing HDF5 files in openCFS format
"""

from __future__ import annotations

import functools

import h5py
import numpy as np
from scipy.spatial import KDTree
from typing import List, Tuple

from pyCFS.data.io.CFSMeshData import CFSMeshData, CFSMeshInfo, CFSRegData
from pyCFS.data.io.CFSResultData import CFSResultData, CFSResultInfo
from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type

from pyCFS.data.util import vprint, progressbar

from pyCFS.data import v_def


def _catch_key_error(f):
    """
    Decorator to catch KeyError in reading HDF5 file
    """

    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyError as e:
            print(f"--- \nError: Could not find object in HDF5 file ({f.__name__})! \n---")
            raise e
        except Exception as e:
            raise e

    return func


class CFSReader:
    # noinspection PyUnresolvedReferences,LongLine
    """
    Base class for all reading operations

    Parameters
    ----------
    filename : str
        Path to the hdf5 file.
    h5driver : str, optional
        Driver used to read the hdf5 file (see h5py documentation). The default is ``None``, in which case the standard
        driver is used
    verbosity : int, optional
        Verbosity level <=1000 ; see v_def.py for predefined levels. Default is v_def.release.

    Attributes
    ----------
    MeshInfo
    Coordinates
    Connectivity
    ElementTypes
    meshData
    MeshGroupsRegions
    MeshGroups
    MeshRegions
    ResultInfo
    MultiStepIDs
    MultiStepData
    AnalysisType
    ResultQuantities

    Methods
    -------
    * `set_multi_step` `(multi_step_id: int)`
        Sets the multiStepID
    * `check_group_region` `(region: str) -> bool`
        Checks whether a mesh entity is a group or a region instead.
    * `get_mesh_region` `(region: str, is_group: bool = None) -> CFSRegData`
        Reads mesh region or group.
    * `get_mesh_region_dimension` `(region: str, is_group: bool = None)`
    * `get_mesh_region_nodes` `(region: str, is_group: bool = None)`
    * `get_mesh_region_elements` `(region: str, is_group: bool = None)`
    * `get_mesh_region_coordinates` `(region: str, is_group: bool = None) -> np.ndarray`
        Reads node Coordinates of a region or group.
    * `get_mesh_region_connectivity` `(region: str, is_group: bool = None) -> np.ndarray`
        Reads element Connectivity of a region or group.
    * `get_mesh_region_types` `(region: str, is_group: bool = None) -> np.ndarray`
        Reads element types of a region or group.
    * `get_closest_node` `(coordinate: np.ndarray, region: str = None, eps: float = 1e-3) -> np.ndarray`
        Return node ids of closest nodes to coordinate array.
    * `get_closest_element` `(coordinate: np.ndarray, region: str = None, eps=1e-3)`
        Return element ids of closest element centroids to coordinate array.
    * `get_result_info_quantity` `(quantity: str) -> CFSResultInfo`
    * `get_result_regions` `(quantity) -> list[str]`
    * `get_dim_names` `(quantity) -> list[str]`
    * `get_restype` `(quantity) -> cfs_result_type`
    * `get_step_numbers` `(quantity) -> np.ndarray`
    * `get_step_values` `(quantity) -> np.ndarray`
    * `get_data_step` `(step_num: int, quantity: str, region: str, restype: cfs_result_type, ds_idx: tuple[int, :] = ()) -> (np.ndarray, bool)`
    * `get_data_steps` `(quantity, region, ds_idx: tuple[int, :] = ()) -> (list[np.ndarray], bool)`
    * `check_data_complex` `(quantity: str, region: str, restype: cfs_result_type) -> bool`
        Checks if result contains real or complex data
    * `get_single_data_steps` `(quantity: str, region: str, entity_id: int) -> np.ndarray`
        Get data over all steps of given element/node id (id starting from 0).

    Examples
    --------
    >>> from pyCFS.data.io import CFSReader
    >>> with CFSReader('file.cfs') as f:
    >>>     mesh = f.MeshData
    >>>     results = f.MultiStepData

    """

    def __init__(self, filename: str, multistep_id=1, h5driver: str | None = None, verbosity=v_def.release) -> None:
        """Initialize the reader"""
        self._filename = filename
        self._h5driver = h5driver
        self._multiStepID = multistep_id
        self._Verbosity = verbosity

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._filename = ""
        return

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        if self._filename:
            return f"CFSReader linked to file_src '{self._filename}', Verbosity {self._Verbosity}"
        else:
            return "Closed CFSReader"

    def set_multi_step(self, multi_step_id: int) -> None:
        """Sets the multiStepID"""
        self._multiStepID = multi_step_id

    @property
    @_catch_key_error
    def MeshInfo(self) -> CFSMeshInfo:
        """
        Reads mesh attributes

        Returns
        -------
        pyCFS.data.io.CFSMeshInfo
            data structure containing mesh attributes.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     info = f.MeshInfo

        """
        vprint("Reading Mesh Attributes", verbose=self._Verbosity >= v_def.debug)
        mesh_info = CFSMeshInfo()
        with h5py.File(self._filename, driver=self._h5driver) as f:
            mesh_info.Dimension = f["Mesh"].attrs["Dimension"]
            mesh_info.Num1DElems = f["Mesh/Elements"].attrs["Num1DElems"]
            mesh_info.Num2DElems = f["Mesh/Elements"].attrs["Num2DElems"]
            mesh_info.Num3DElems = f["Mesh/Elements"].attrs["Num3DElems"]
            mesh_info.NumElems = f["Mesh/Elements"].attrs["NumElems"]
            mesh_info.Num_HEXA20 = f["Mesh/Elements"].attrs["Num_HEXA20"]
            mesh_info.Num_HEXA27 = f["Mesh/Elements"].attrs["Num_HEXA27"]
            mesh_info.Num_HEXA8 = f["Mesh/Elements"].attrs["Num_HEXA8"]
            mesh_info.Num_PYRA13 = f["Mesh/Elements"].attrs["Num_PYRA13"]
            mesh_info.Num_PYRA14 = f["Mesh/Elements"].attrs["Num_PYRA14"]
            mesh_info.Num_PYRA5 = f["Mesh/Elements"].attrs["Num_PYRA5"]
            mesh_info.Num_WEDGE15 = f["Mesh/Elements"].attrs["Num_WEDGE15"]
            mesh_info.Num_WEDGE18 = f["Mesh/Elements"].attrs["Num_WEDGE18"]
            mesh_info.Num_WEDGE6 = f["Mesh/Elements"].attrs["Num_WEDGE6"]
            mesh_info.Num_TET10 = f["Mesh/Elements"].attrs["Num_TET10"]
            mesh_info.Num_TET4 = f["Mesh/Elements"].attrs["Num_TET4"]
            mesh_info.Num_QUAD4 = f["Mesh/Elements"].attrs["Num_QUAD4"]
            mesh_info.Num_QUAD8 = f["Mesh/Elements"].attrs["Num_QUAD8"]
            mesh_info.Num_QUAD9 = f["Mesh/Elements"].attrs["Num_QUAD9"]
            mesh_info.Num_TRIA3 = f["Mesh/Elements"].attrs["Num_TRIA3"]
            mesh_info.Num_TRIA6 = f["Mesh/Elements"].attrs["Num_TRIA6"]
            mesh_info.Num_LINE2 = f["Mesh/Elements"].attrs["Num_LINE2"]
            mesh_info.Num_LINE3 = f["Mesh/Elements"].attrs["Num_LINE3"]
            mesh_info.Num_POINT = f["Mesh/Elements"].attrs["Num_POINT"]
            mesh_info.Num_POLYGON = f["Mesh/Elements"].attrs["Num_POLYGON"]
            mesh_info.Num_POLYHEDRON = f["Mesh/Elements"].attrs["Num_POLYHEDRON"]
            mesh_info.Num_UNDEF = f["Mesh/Elements"].attrs["Num_UNDEF"]
            mesh_info.QuadraticElems = f["Mesh/Elements"].attrs["QuadraticElems"]
            mesh_info.NumNodes = f["Mesh/Nodes"].attrs["NumNodes"]
        return mesh_info

    @property
    @_catch_key_error
    def Coordinates(self) -> np.ndarray:
        """
        Reads node coordinates

        Returns
        -------
        np.ndarray
            Coordinate array (Nx3) of the whole mesh (N number of nodes)

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     coordinates = f.Coordinates

        """
        with h5py.File(self._filename, driver=self._h5driver) as f:
            return np.array(f["Mesh/Nodes/Coordinates"])

    @property
    @_catch_key_error
    def Connectivity(self) -> np.ndarray:
        """
        Reads element connectivity

        Returns
        -------
        np.ndarray
            Connectivity array (NxM) of the whole mesh (N number of elements, M maximum number of nodes per element).
            Includes zero entries in case of different element types.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     connectivity = f.Connectivity

        """
        with h5py.File(self._filename, driver=self._h5driver) as f:
            return np.array(f["Mesh/Elements/Connectivity"])

    @property
    @_catch_key_error
    def ElementTypes(self) -> np.ndarray:
        """
        Reads element types

        Returns
        -------
        np.ndarray[cfs_element_type]
            Element type array (Nx1) of the whole mesh (N number of elements).
            Element definitions based on pyCFS.data.io.cfs_types.cfs_element_type

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     element_types = f.ElementTypes

        """
        with h5py.File(self._filename, driver=self._h5driver) as f:
            # noinspection PyTypeChecker
            return f["Mesh/Elements/Types"][()]

    @property
    def MeshData(self) -> CFSMeshData:
        """
        Reads mesh

        Returns
        -------
        pyCFS.data.io.CFSMeshData
            data structure containing mesh data, region data and mesh attributes.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData

        """
        vprint("Reading Mesh Data", verbose=self._Verbosity >= v_def.more)
        mesh_data = CFSMeshData(
            coordinates=self.Coordinates,
            connectivity=self.Connectivity,
            types=self.ElementTypes,
            regions=self.MeshGroupsRegions,
            verbosity=self._Verbosity,
        )
        return mesh_data

    @property
    def MeshGroupsRegions(self) -> List[CFSRegData]:
        """
        Reads all mesh groups and regions

        Returns
        -------
        ListpyCFS.data.io.CFSRegData]
            list of data structures containing data about a group or region.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     groups_regions_data = f.MeshGroupsRegions

        """
        reg_data = []
        reg_data.extend(self.MeshGroups)
        reg_data.extend(self.MeshRegions)
        return reg_data

    @property
    @_catch_key_error
    def MeshGroups(self) -> List[CFSRegData]:
        """
        Reads all mesh groups

        Returns
        -------
        list[pyCFS.data.io.CFSRegData]
            list of data structures containing data about a group.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     groups_data = f.MeshGroups

        """
        grp_data = []
        with h5py.File(self._filename, driver=self._h5driver) as f:
            reg_names = list(f["Mesh/Groups"].keys())
        for region in reg_names:
            reg = self.get_mesh_region(region=region, is_group=True)
            grp_data.append(reg)
        return grp_data

    @property
    @_catch_key_error
    def MeshRegions(self) -> List[CFSRegData]:
        """
        Reads all mesh regions

        Returns
        -------
        list[pyCFS.data.io.CFSRegData]
            list of data structures containing data about a region.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     regions_data = f.MeshRegions

        """
        reg_data = []
        with h5py.File(self._filename, driver=self._h5driver) as f:
            reg_names = list(f["Mesh/Regions"].keys())
        for region in reg_names:
            reg = self.get_mesh_region(region=region, is_group=False)
            reg_data.append(reg)
        return reg_data

    @_catch_key_error
    def check_group_region(self, region: str) -> bool:
        """
        Checks whether a mesh entity is a group or a region instead.

        Parameters
        ----------
        region : str
            Name of the group/region

        Returns
        -------
        bool
            flag indicating if the entity is a group

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     if f.check_group_region('region_name'):
        >>>         pass

        """
        with h5py.File(self._filename, driver=self._h5driver) as f:
            group_names = list(f["Mesh/Groups"].keys())
        with h5py.File(self._filename, driver=self._h5driver) as f:
            reg_names = list(f["Mesh/Regions"].keys())
        if region in group_names:
            is_group = True
        elif region in reg_names:
            is_group = False
        else:
            raise IOError(f"Entitiy {region} is found in neither Group nor Region names!")
        return is_group

    def get_mesh_region(self, region: str, is_group: bool | None = None) -> CFSRegData:
        """
        Reads mesh region or group.

        Parameters
        ----------
        region : str
            Name of the group/region
        is_group : bool, optional
            Flag if the mesh entity is a group or region instead. The default is ``None``, in which case the entity
            will be checked based on the provided name.
        Returns
        -------
        pyCFS.data.io.CFSRegData
            data structure containing the region/group data

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     region_data = f.get_mesh_region('region_name'):

        """
        if is_group is None:
            is_group = self.check_group_region(region=region)
        reg_data = []
        vprint(f"Reading Region {region}", verbose=self._Verbosity >= v_def.more)
        reg = CFSRegData(name=region, is_group=is_group, verbosity=self._Verbosity)
        reg.Dimension = self.get_mesh_region_dimension(region=region, is_group=is_group)
        reg.Nodes = self.get_mesh_region_nodes(region=region, is_group=is_group)
        reg.Elements = self.get_mesh_region_elements(region=region, is_group=is_group)
        reg_data.append(reg)
        return reg

    @_catch_key_error
    def get_mesh_region_dimension(self, region: str, is_group: bool | None = None):
        if is_group is None:
            is_group = self.check_group_region(region=region)
        with h5py.File(self._filename, driver=self._h5driver) as f:
            if is_group:
                return f[f"Mesh/Groups/{region}"].attrs["Dimension"]
            else:
                return f[f"Mesh/Regions/{region}"].attrs["Dimension"]

    @_catch_key_error
    def get_mesh_region_nodes(self, region: str, is_group: bool | None = None) -> np.ndarray:
        if is_group is None:
            is_group = self.check_group_region(region=region)
        if is_group:
            h5_path = f"Mesh/Groups/{region}/Nodes"
        else:
            h5_path = f"Mesh/Regions/{region}/Nodes"

        with h5py.File(self._filename, driver=self._h5driver) as f:
            if h5_path in f:
                return np.array(f[h5_path])
            else:
                raise IOError(f"No Node IDs defined for Region {region}!")

    @_catch_key_error
    def get_mesh_region_elements(self, region: str, is_group: bool | None = None) -> np.ndarray | None:
        if is_group is None:
            is_group = self.check_group_region(region=region)
        if is_group:
            h5_path = f"Mesh/Groups/{region}/Elements"
        else:
            h5_path = f"Mesh/Regions/{region}/Elements"

        with h5py.File(self._filename, driver=self._h5driver) as f:
            if h5_path in f:
                return np.array(f[h5_path])
            else:
                vprint(f"Warning: No Node IDs defined for Region {region}!", verbose=self._Verbosity >= v_def.more)
                return np.empty(0, dtype=np.int32)

    def get_mesh_region_coordinates(self, region: str, is_group: bool | None = None) -> np.ndarray:
        """
        Reads node Coordinates of a region or group.

        Parameters
        ----------
        region : str
            Name of the group/region
        is_group : bool, optional
            Flag if the mesh entity is a group or region instead. The default is ``None``, in which case the entity
            will be checked based on the provided name.
        Returns
        -------
        np.ndarray
            Coordinate array (Nx3) (N number of nodes in the region)

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     region_coordinates = f.get_mesh_region_coordinates('region_name'):

        """
        if is_group is None:
            is_group = self.check_group_region(region=region)
        coordinates = self.Coordinates
        region_nodes = self.get_mesh_region_nodes(region=region, is_group=is_group)
        if region_nodes.ndim > 1:
            region_nodes = region_nodes.flatten()
        return coordinates[region_nodes - 1, :]

    def get_mesh_region_connectivity(self, region: str, is_group: bool | None = None) -> np.ndarray:
        """
        Reads element Connectivity of a region or group.

        Parameters
        ----------
        region : str
            Name of the group/region
        is_group : bool, optional
            Flag if the mesh entity is a group or region instead. The default is ``None``, in which case the entity
            will be checked based on the provided name.
        Returns
        -------
        np.ndarray
            Connectivity array (NxM) (N number of elements in the region, M maximum number of nodes per element).
            Includes zero entries in case of different element types.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     region_connectivity = f.get_mesh_region_connectivity('region_name'):

        """
        if is_group is None:
            is_group = self.check_group_region(region=region)
        connectivity = self.Connectivity
        region_elements = self.get_mesh_region_elements(region=region, is_group=is_group)
        return connectivity[region_elements - 1, :]

    def get_mesh_region_types(self, region: str, is_group: bool | None = None) -> np.ndarray:
        """
        Reads element types of a region or group.

        Parameters
        ----------
        region : str
            Name of the group/region
        is_group : bool, optional
            Flag if the mesh entity is a group or region instead. The default is ``None``, in which case the entity
            will be checked based on the provided name.
        Returns
        -------
        np.ndarray
            Connectivity array (Nx1) (N number of elements in the region).
            Element definitions based on pyCFS.data.io.cfs_types.cfs_element_type

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     region_element_types = f.get_mesh_region_types('region_name'):

        """
        if is_group is None:
            is_group = self.check_group_region(region=region)
        element_types = self.ElementTypes
        region_elements = self.get_mesh_region_elements(region=region, is_group=is_group)
        return element_types[region_elements - 1]

    def get_closest_node(self, coordinate: np.ndarray, region: str | None = None, eps: float = 1e-3) -> np.ndarray:
        """
        Return node ids of closest nodes to coordinate array.

        Parameters
        ----------

        coordinate: np.ndarray
            Coordinate array (Nx3, N is the number of query points)
        region : str, optional
            Name of the group/region. The default is ``None``, in which case the global mesh will be used instead.
        eps : float, optional
            Show warning if distance of closest node exceeds the specified value. The default value is ``1e-3``.
        Returns
        -------
        np.ndarray
            Array of node ids (starting from 0) of the closest node to the respective coordinate. If region is passed,
            return region node id, otherwise return global node id.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> search_coord = np.array([0,0,0])
        >>> with CFSReader('file.cfs') as f:
        >>>     node_indices = f.get_closest_node(search_coord):

        """
        if region is None:
            search_coord = self.Coordinates
        else:
            search_coord = self.get_mesh_region_coordinates(region=region)
        search_coord_kdtree = KDTree(search_coord)
        d, idx = search_coord_kdtree.query(coordinate)
        if np.any(d > eps):
            vprint(
                f"Warning: Nearest neighbor distance {np.max(d)} exceeds {eps}",
                verbose=self._Verbosity >= v_def.release,
            )
        return idx

    def get_closest_element(self, coordinate: np.ndarray, region: str | None = None, eps=1e-3):
        """
        Return element ids of closest element centroids to coordinate array.

        Parameters
        ----------

        coordinate: np.ndarray
            Coordinate array (Nx3, N is the number of query points)
        region : str, optional
            Name of the group/region. The default is ``None``, in which case the global mesh will be used instead.
        eps : float, optional
            Show warning if distance of closest node exceeds the specified value. The default value is ``1e-3``.
        Returns
        -------
        np.ndarray
            Array of element ids (starting from 0) of the closest element centroid to the respective coordinate.
            If region is passed, return region element id, otherwise return global element id.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> search_coord = np.array([0,0,0])
        >>> with CFSReader('file.cfs') as f:
        >>>     element_indices = f.get_closest_element(search_coord):

        """
        if region is None:
            search_conn = self.Connectivity
        else:
            search_conn = self.get_mesh_region_connectivity(region=region)

        search_coord = np.zeros((search_conn.shape[0], self.Coordinates.shape[1]))
        # TODO Vectorize
        # Remove columns containing zeros only
        # idx = np.argwhere(np.all(search_conn[..., :] == 0, axis=0))
        # search_conn = np.delete(search_conn, idx, axis=1)
        # el_coord = self.Coordinates[search_conn - 1]
        # search_coord = np.sum(el_coord, axis=1) / el_coord.shape[1]
        for i in np.argwhere(np.any(search_conn[..., :] == 0, axis=1)):
            el_conn = search_conn[i, np.argwhere(search_conn[i, :] != 0)[:, 1]]
            el_coord = self.Coordinates[el_conn - 1]
            search_coord[i, :] = np.sum(el_coord, axis=0) / el_coord.shape[0]

        search_coord_kdtree = KDTree(search_coord)
        d, idx = search_coord_kdtree.query(coordinate)
        if any(d > eps):
            vprint(
                f"Warning: Nearest neighbor distance {max(d)} exceeds {eps}",
                verbose=self._Verbosity >= v_def.release,
            )
        return idx

    @property
    def ResultInfo(self) -> List[CFSResultInfo]:
        # TODO Adapt to support multiple res_types for one quantity & region
        # Doesn't read DataShape Property
        result_info_list = []
        quantities = self.ResultQuantities
        for quantity in quantities:
            regions = self.get_result_regions(quantity)
            for reg in regions:
                result_info_list.append(self.get_result_info(quantity=quantity, region=reg))
        return result_info_list

    def get_result_info(self, quantity: str, region: str) -> CFSResultInfo:
        dim_names = self.get_dim_names(quantity)
        # step_numbers = self.get_step_numbers(quantity)
        step_values = self.get_step_values(quantity)
        restype = self.get_restype(quantity)
        is_complex = self.check_data_complex(quantity=quantity, region=region, restype=restype)
        return CFSResultInfo(
            quantity=quantity,
            region=region,
            res_type=restype,
            dim_names=dim_names,
            step_values=step_values,
            is_complex=is_complex,
            multi_step_id=self._multiStepID,
            analysis_type=self.AnalysisType,
        )

    @property
    @_catch_key_error
    def MultiStepIDs(self) -> List[int]:
        with h5py.File(self._filename, driver=self._h5driver) as f:
            multi_step_names = list(f["Results/Mesh"].keys())

        multi_step_ids = [int(line.replace("MultiStep_", "")) for line in multi_step_names]
        return multi_step_ids

    @property
    def MultiStepData(self) -> CFSResultData:
        """
        Reads result data of the active multiStep

        Returns
        -------
        pyCFS.data.io.CFSResultData
            data structure containing result data and attributes of the active multiStep

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     result = f.MultiStepData

        """
        vprint(
            f"Reading MultiStep {self._multiStepID}",
            verbose=self._Verbosity >= v_def.more,
        )
        result = CFSResultData(
            analysis_type=self.AnalysisType,
            multi_step_id=self._multiStepID,
            verbosity=self._Verbosity,
        )
        quantities = self.ResultQuantities
        for quantity in quantities:
            regions = self.get_result_regions(quantity)
            for region in regions:
                dim_names = self.get_dim_names(quantity)
                # step_numbers = self.get_step_numbers(quantity)
                step_values = self.get_step_values(quantity)
                restype = self.get_restype(quantity)
                data, is_complex = self.get_data_steps(quantity, region)
                result.add_data(
                    data=data,
                    step_values=step_values,
                    quantity=quantity,
                    region=region,
                    restype=restype,
                    dim_names=dim_names,
                    is_complex=is_complex,
                )
        return result

    @property
    @_catch_key_error
    def AnalysisType(self) -> cfs_analysis_type:
        with h5py.File(self._filename, driver=self._h5driver) as f:
            analysis_type = f[f"Results/Mesh/MultiStep_{self._multiStepID}"].attrs["AnalysisType"]
        return cfs_analysis_type(analysis_type)

    @property
    @_catch_key_error
    def ResultQuantities(self) -> List[str]:
        with h5py.File(self._filename, driver=self._h5driver) as f:
            quantities = list(f[f"Results/Mesh/MultiStep_{self._multiStepID}/ResultDescription"].keys())
        return quantities

    @_catch_key_error
    def get_result_regions(self, quantity) -> List[str]:
        with h5py.File(self._filename, driver=self._h5driver) as f:
            regions_array = np.array(
                f[f"Results/Mesh/MultiStep_{self._multiStepID}/ResultDescription/{quantity}/EntityNames"]
            ).flatten()
            regions = [reg.decode() for reg in regions_array]  # Convert b'' to str
        return regions

    @_catch_key_error
    def get_dim_names(self, quantity) -> List[str]:
        with h5py.File(self._filename, driver=self._h5driver) as f:
            dim_names_array = np.array(
                f[f"Results/Mesh/MultiStep_{self._multiStepID}/ResultDescription/{quantity}/DOFNames"]
            ).flatten()
            dim_names = [name.decode() for name in dim_names_array]  # Convert b'' to str
        return dim_names

    @_catch_key_error
    def get_restype(self, quantity) -> cfs_result_type:
        # TODO support Quantity to be defined on multiple ResTypes
        with h5py.File(self._filename, driver=self._h5driver) as f:
            restype = cfs_result_type(
                int(
                    np.array(
                        f[f"Results/Mesh/MultiStep_{self._multiStepID}/ResultDescription/{quantity}/DefinedOn"]
                    ).item()
                )
            )
        return restype

    @_catch_key_error
    def get_step_numbers(self, quantity) -> np.ndarray:
        with h5py.File(self._filename, driver=self._h5driver) as f:
            step_numbers = np.array(
                f[f"Results/Mesh/MultiStep_{self._multiStepID}/ResultDescription/{quantity}/StepNumbers"],
                dtype=int,
            ).flatten()
        return step_numbers

    @_catch_key_error
    def get_step_values(self, quantity) -> np.ndarray:
        with h5py.File(self._filename, driver=self._h5driver) as f:
            step_values = np.array(
                f[f"Results/Mesh/MultiStep_{self._multiStepID}/ResultDescription/{quantity}/StepValues"]
            ).flatten()
        return step_values

    @_catch_key_error
    def get_data_step(
        self,
        step_num: int,
        quantity: str,
        region: str,
        restype: cfs_result_type,
        ds_idx: tuple = (),
    ) -> Tuple[np.ndarray, bool]:
        with h5py.File(self._filename, driver=self._h5driver) as f:
            h5_data_path = f"Results/Mesh/MultiStep_{self._multiStepID}/Step_{step_num}/{quantity}/{region}/{restype}"
            data_names = list(f[h5_data_path].keys())
            if "Imag" in data_names:
                data_step = f[f"{h5_data_path}/Real"][ds_idx] + f[f"{h5_data_path}/Imag"][ds_idx] * 1j
                is_complex = True
            else:
                data_step = f[f"{h5_data_path}/Real"][ds_idx]
                is_complex = False

        if data_step.ndim == 1:
            data_step = data_step.reshape((data_step.shape[0], 1))

        return data_step, is_complex

    def get_data_steps(self, quantity, region, ds_idx: tuple = ()) -> Tuple[np.ndarray, bool]:
        step_numbers = self.get_step_numbers(quantity)
        # Initialize with 1st step
        is_complex = False
        data_step, flag_complex = self.get_data_step(
            int(step_numbers[0]),
            quantity,
            region,
            self.get_restype(quantity),
            ds_idx=ds_idx,
        )
        is_complex = is_complex or flag_complex
        data_dtype: type[float] | type[complex]
        if is_complex:
            data_dtype = complex
        else:
            data_dtype = float

        data = np.zeros([step_numbers.size] + list(data_step.shape), dtype=data_dtype)
        data[0, :, :] = data_step

        for step_idx, step_num in enumerate(
            progressbar(
                step_numbers[1:],
                prefix=f"Reading {quantity} on {region}: ",
                verbose=self._Verbosity >= v_def.more,
            )
        ):
            data_step, flag_complex = self.get_data_step(
                step_num, quantity, region, self.get_restype(quantity), ds_idx=ds_idx
            )
            is_complex = is_complex or flag_complex
            data[step_idx + 1, :, :] = data_step
        return data, is_complex

    @_catch_key_error
    def check_data_complex(self, quantity: str, region: str, restype: cfs_result_type) -> bool:
        """Checks if result contains real or complex data"""
        step_num = self.get_step_numbers(quantity)[0]
        with h5py.File(self._filename, driver=self._h5driver) as f:
            h5_data_path = f"Results/Mesh/MultiStep_{self._multiStepID}/Step_{step_num}/{quantity}/{region}/{restype}"
            data_names = list(f[h5_data_path].keys())
            if "Imag" in data_names:
                is_complex = True
            else:
                is_complex = False
        return is_complex

    def get_single_data_steps(self, quantity: str, region: str, entity_id: int) -> np.ndarray:
        """Get data over all steps of given element/node id (id starting from 0)."""

        dim = len(self.get_dim_names(quantity=quantity))
        ds_idx = (entity_id, range(dim))
        data, _ = self.get_data_steps(quantity, region, ds_idx)

        return np.array(data)

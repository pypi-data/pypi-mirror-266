"""
Module containing data processing utilities for writing HDF5 files in openCFS format
"""

from __future__ import annotations

import textwrap
import datetime
import time
from functools import partial
from multiprocessing import Pool

import numpy as np
from scipy.spatial import Delaunay, KDTree
from typing import Iterable, Any, List, Dict, Tuple

from pyCFS.data.io import CFSResultArray
from pyCFS.data.io.CFSResultData import CFSResultData
from pyCFS.data.io.cfs_types import cfs_element_type, cfs_result_type
from pyCFS.data.util import (
    vprint,
    progressbar,
    element_quality,
    list_search,
    element_centroid,
)
from pyCFS.data import v_def


class CFSMeshInfo:
    """
    Data structure containing mesh information

    Methods
    -------
    * `update_by_coord_types` `(coordinates: np.ndarray, types: np.ndarray)`
        Update structure based on coordinate and element types as defined in CFSMeshData

    Examples
    --------
    >>> from pyCFS.data.io import CFSReader, CFSMeshInfo
    >>> with CFSReader('file.cfs') as f:
    >>>     coordinates = f.Coordinates
    >>>     element_types = f.ElementTypes
    >>> MeshInfo = CFSMeshInfo()
    >>> MeshInfo.update_by_coord_types(coordinates=coordinates,element_types=element_types)

    """

    def __init__(self) -> None:
        self.Dimension = -1
        self.Num1DElems = 0
        self.Num2DElems = 0
        self.Num3DElems = 0
        self.NumElems = 0
        self.Num_HEXA20 = 0
        self.Num_HEXA27 = 0
        self.Num_HEXA8 = 0
        self.Num_PYRA13 = 0
        self.Num_PYRA14 = 0
        self.Num_PYRA5 = 0
        self.Num_WEDGE15 = 0
        self.Num_WEDGE18 = 0
        self.Num_WEDGE6 = 0
        self.Num_TET10 = 0
        self.Num_TET4 = 0
        self.Num_QUAD4 = 0
        self.Num_QUAD8 = 0
        self.Num_QUAD9 = 0
        self.Num_TRIA3 = 0
        self.Num_TRIA6 = 0
        self.Num_LINE2 = 0
        self.Num_LINE3 = 0
        self.Num_POINT = 0
        self.Num_POLYGON = 0
        self.Num_POLYHEDRON = 0
        self.Num_UNDEF = 0
        self.QuadraticElems = False
        self.NumNodes = 0

    def __repr__(self) -> str:
        return f"""Mesh Info ({self.Dimension}D, {self.NumNodes} Nodes, {self.NumElems} Elements)"""

    def __str__(self) -> str:
        return textwrap.dedent(
            f"""
        Mesh
         - Dimension: {self.Dimension}
         - Nodes:     {self.NumNodes}
         - Elements:  {self.NumElems}"""
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, CFSMeshInfo):
            return False
        return all(
            [
                self.Dimension == other.Dimension,
                self.Num1DElems == other.Num1DElems,
                self.Num2DElems == other.Num2DElems,
                self.Num3DElems == other.Num3DElems,
                self.NumElems == other.NumElems,
                self.Num_HEXA20 == other.Num_HEXA20,
                self.Num_HEXA27 == other.Num_HEXA27,
                self.Num_HEXA8 == other.Num_HEXA8,
                self.Num_PYRA13 == other.Num_PYRA13,
                self.Num_PYRA14 == other.Num_PYRA14,
                self.Num_PYRA5 == other.Num_PYRA5,
                self.Num_WEDGE15 == other.Num_WEDGE15,
                self.Num_WEDGE18 == other.Num_WEDGE18,
                self.Num_WEDGE6 == other.Num_WEDGE6,
                self.Num_TET10 == other.Num_TET10,
                self.Num_TET4 == other.Num_TET4,
                self.Num_QUAD4 == other.Num_QUAD4,
                self.Num_QUAD8 == other.Num_QUAD8,
                self.Num_QUAD9 == other.Num_QUAD9,
                self.Num_TRIA3 == other.Num_TRIA3,
                self.Num_TRIA6 == other.Num_TRIA6,
                self.Num_LINE2 == other.Num_LINE2,
                self.Num_LINE3 == other.Num_LINE3,
                self.Num_POINT == other.Num_POINT,
                self.Num_POLYGON == other.Num_POLYGON,
                self.Num_POLYHEDRON == other.Num_POLYHEDRON,
                self.Num_UNDEF == other.Num_UNDEF,
                self.QuadraticElems == other.QuadraticElems,
                self.NumNodes == other.NumNodes,
            ]
        )

    def update_by_coord_types(self, coordinates: np.ndarray, types: np.ndarray) -> None:
        """
        Update structure based on coordinate and element types as defined in CFSMeshData

        Parameters
        ----------
        coordinates : numpy.ndarray
            Coordinate array (Nx3) of the whole mesh (N number of nodes)

        types : numpy.ndarray[cfs_element_type]
            Element type array (Nx1) of the whole mesh (N number of elements).
            Element definitions based on pyCFS.data.io.cfs_types.cfs_element_type

        """
        self.NumNodes = coordinates.shape[0]
        self.NumElems = types.shape[0]

        self.Num_HEXA20 = np.count_nonzero(types == cfs_element_type.HEXA20)
        self.Num_HEXA27 = np.count_nonzero(types == cfs_element_type.HEXA27)
        self.Num_HEXA8 = np.count_nonzero(types == cfs_element_type.HEXA8)
        self.Num_PYRA13 = np.count_nonzero(types == cfs_element_type.PYRA13)
        self.Num_PYRA14 = np.count_nonzero(types == cfs_element_type.PYRA14)
        self.Num_PYRA5 = np.count_nonzero(types == cfs_element_type.PYRA5)
        self.Num_WEDGE15 = np.count_nonzero(types == cfs_element_type.WEDGE15)
        self.Num_WEDGE18 = np.count_nonzero(types == cfs_element_type.WEDGE18)
        self.Num_WEDGE6 = np.count_nonzero(types == cfs_element_type.WEDGE6)
        self.Num_TET10 = np.count_nonzero(types == cfs_element_type.TET10)
        self.Num_TET4 = np.count_nonzero(types == cfs_element_type.TET4)
        self.Num_QUAD4 = np.count_nonzero(types == cfs_element_type.QUAD4)
        self.Num_QUAD8 = np.count_nonzero(types == cfs_element_type.QUAD8)
        self.Num_QUAD9 = np.count_nonzero(types == cfs_element_type.QUAD9)
        self.Num_TRIA3 = np.count_nonzero(types == cfs_element_type.TRIA3)
        self.Num_TRIA6 = np.count_nonzero(types == cfs_element_type.TRIA6)
        self.Num_LINE2 = np.count_nonzero(types == cfs_element_type.LINE2)
        self.Num_LINE3 = np.count_nonzero(types == cfs_element_type.LINE3)
        self.Num_POINT = np.count_nonzero(types == cfs_element_type.POINT)
        self.Num_POLYGON = np.count_nonzero(types == cfs_element_type.POLYGON)
        self.Num_POLYHEDRON = np.count_nonzero(types == cfs_element_type.POLYHEDRON)
        self.Num_UNDEF = np.count_nonzero(types == cfs_element_type.UNDEF)

        self.QuadraticElems = (
            self.Num_HEXA20
            + self.Num_HEXA27
            + self.Num_PYRA13
            + self.Num_PYRA14
            + self.Num_WEDGE15
            + self.Num_WEDGE18
            + self.Num_TET10
            + self.Num_QUAD8
            + self.Num_QUAD9
            + self.Num_TRIA6
            + self.Num_LINE3
        ) > 0

        self.Num1DElems = self.Num_LINE2 + self.Num_LINE3
        self.Num2DElems = (
            self.Num_QUAD4 + self.Num_QUAD8 + self.Num_QUAD9 + self.Num_TRIA3 + self.Num_TRIA6 + self.Num_POLYGON
        )
        self.Num3DElems = (
            self.Num_HEXA20
            + self.Num_HEXA27
            + self.Num_HEXA8
            + self.Num_PYRA13
            + self.Num_PYRA14
            + self.Num_PYRA5
            + self.Num_WEDGE15
            + self.Num_WEDGE18
            + self.Num_WEDGE6
            + self.Num_TET10
            + self.Num_TET4
            + self.Num_POLYHEDRON
        )

        if self.Num3DElems > 0:
            self.Dimension = 3
        elif self.Num2DElems > 0:
            self.Dimension = 2
        elif self.Num1DElems > 0:
            self.Dimension = 1
        elif self.Num_POINT > 0:
            self.Dimension = 0
        else:
            self.Dimension = -1


class CFSMeshData:
    """
    Data structure containing mesh definition

    Parameters
    ----------
    coordinates : numpy.ndarray, optional
        Coordinate array (Nx3) of the whole mesh (N number of nodes)
    connectivity : numpy.ndarray, optional
        Connectivity array (NxM) of the whole mesh (N number of elements, M maximum number of nodes per element).
        Includes zero entries in case of different element types.
    types : numpy.ndarray[cfs_element_type], optional
        Element type array (Nx1) of the whole mesh (N number of elements).
        Element definitions based on pyCFS.data.io.cfs_types.cfs_element_type
    regions : list[pyCFS.data.io.CFSRegData], optional
        list of data structures containing data about a group or region.
    verbosity : int, optional
        Verbosity level <=1000 ; see v_def.py for predefined levels. Default is v_def.release.

    Attributes
    ----------
    Coordinates : np.ndarray
        Coordinate array (Nx3) of the whole mesh (N number of nodes)
    Connectivity
    Types : np.ndarray
        Element type array (Nx1) of the whole mesh (N number of elements).
        Element definitions based on pyCFS.data.io.cfs_types.cfs_element_type
    MeshInfo : CFSMeshInfo
        Data structure containing mesh information
    Regions : list[CFSRegData]
        List of data structures containing mesh region definition
    ElementCentroids
    Quality

    Methods
    -------
    * `update_mesh_centroids` `(processes: int = None)`
        Compute element centroids.
    * `get_mesh_centroids` `(el_idx: np.ndarray = None, processes: int = None) -> np.ndarray`
        Compute geometric centers of mesh elements.
    * `update_mesh_quality` `(metric='quality', processes: int = None)`
        Compute mesh metric based on 'metric'.
    * `merge` `(other: CFSMeshData) -> CFSMeshData`
        Merges mesh with other mesh removing duplicate coordinates and elements
    * `update_info()`
        Update structure based on coordinate and element types
    * `drop_unused_nodes_elements` `(reg_data_list: list[CFSRegData])`
        Drop nodes and elements that are not used in the given list of groups/regions.
    * `convert_to_simplex` `(idx_convert: np.ndarray = None, result_data=None)`
        Convert arbitrary 3D elements into simplexes (tetrahedra), by applying Delaunay triangulation.
    * `convert_quad2tria` `(idx_convert: np.ndarray = None, result_data=None)`
        Convert QUAD4 elements into TRIA3 elements. If 'idx_convert' is unspecified all QUAD4 in the mesh are converted.
    * `get_region_nodes` `(region: str) -> np.ndarray`
    * `get_region_elements` `(region: str) -> np.ndarray`
    * `get_region_coordinates` `(region: str) -> np.ndarray`
    * `get_region_connectivity` `(region: str) -> np.ndarray`
    * `get_region_centroids` `(region: str, processes: int = None) -> np.ndarray`
    * `reorient_region` `(region_name: str) -> None`
    * `reorient_elements` `(idx_reorient: list) -> None`

    Examples
    --------
    >>> from pyCFS.data.io import CFSReader, CFSMeshInfo
    >>> with CFSReader('file.cfs') as f:
    >>>     coordinates = f.Coordinates
    >>>     connectivity = f.Connectivity
    >>>     ElementTypes = f.ElementTypes
    >>>     region_data = f.MeshGroupsRegions
    >>> mesh = CFSMeshData(coordinates=coordinates, connectivity=connectivity, ElementTypes=ElementTypes,
    >>>                    regions=region_data)

    """

    def __init__(
        self,
        coordinates=np.empty((0, 3)),
        connectivity=np.empty((0, 1)),
        types=np.empty(0),
        regions: List[CFSRegData] | None = None,
        verbosity=v_def.release,
    ) -> None:
        """Initializes a CFSMeshData object. If both Coordinates and types are provided,
        also updates mesh attributes."""
        if regions is None:
            regions = []
        self._Verbosity = verbosity
        self.Coordinates = coordinates
        self.Connectivity = connectivity
        self.Types: np.ndarray = types
        self.MeshInfo: CFSMeshInfo = CFSMeshInfo()
        self.Regions: List[CFSRegData] = regions
        if self.Coordinates.size > 0 and self.Types.size > 0:
            self.update_info()
        self.check_add_point_elements()
        self._flag_warn_element_centroid = True
        self._flag_warn_element_quality = True
        self._ElementCentroids: np.ndarray | None = None
        self._Quality: np.ndarray | None = None

    # noinspection LongLine
    def __repr__(self) -> str:
        return f"""Mesh ({self.MeshInfo.Dimension}D, {self.MeshInfo.NumNodes} Nodes, {self.MeshInfo.NumElems} Elements, {len(self.Regions)} Regions)"""

    def __str__(self) -> str:
        return textwrap.dedent(
            f"""\
        {self.MeshInfo}
 - Regions:   {len(self.Regions)}"""
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, CFSMeshData):
            return False
        return all(
            [
                np.array_equal(self.Coordinates, other.Coordinates),
                np.array_equal(self.Connectivity, other.Connectivity),
                np.array_equal(self.Types, other.Types),
                self.MeshInfo == other.MeshInfo,
                sorted(self.Regions) == sorted(other.Regions),
            ]
        )

    def __add__(self, other: CFSMeshData):
        return self.merge(other)

    @property
    def Connectivity(self):
        """Element Connectivity array"""
        return self._Connectivity

    @Connectivity.setter
    def Connectivity(self, nodes):
        self._Connectivity = np.array(nodes, dtype=np.uint32)

    @property
    def ElementCentroids(self) -> np.ndarray | None:
        """
        Compute element centroids. Doesn't update automatically compute for large meshes.

        Returns
        -------
        np.ndarray
            Array of element centroids.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData
        >>> mesh.update_mesh_centroids()
        >>> centroids = mesh.ElementCentroids

        """
        max_element_threshold = 1e6  # Don't compute automatically for large meshes.
        if self.MeshInfo.NumElems < max_element_threshold:
            if self._ElementCentroids is None:
                self._ElementCentroids = self.get_mesh_centroids()
        else:
            if self._flag_warn_element_centroid:
                vprint(
                    "Warning: ElementCentroids not updated automatically due to large number of elements. "
                    'Please call "obj.get_mesh_centroids()" to compute centroids',
                    verbose=self._Verbosity >= v_def.release,
                )
                self._flag_warn_element_centroid = False
        return self._ElementCentroids

    def update_mesh_centroids(self, processes: int | None = None):
        """Compute element centroids."""
        self._ElementCentroids = self.get_mesh_centroids(processes=processes)

    def get_mesh_centroids(self, el_idx: np.ndarray | None = None, processes: int | None = None) -> np.ndarray:
        """
        Compute geometric centers of mesh elements.

        Parameters
        ----------
        el_idx : numpy.ndarray, optional
            Array of (global) element ids (starting from 0) for which to compute centroids. The default is ``None``,
            in which case all elements are processed.
        processes : int, optional
            Number of processes to use in parallel. The default is ``None``, in which case all cores are used.

        Returns
        -------
        np.ndarray
            Array of element centroids.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData
        >>> element_indices = np.array([0,1,2,3])
        >>> centroids = mesh.get_mesh_centroids(el_idx=element_indices,processes=1)

        """
        if el_idx is None:
            el_idx_it: Iterable[Any] = range(self.Connectivity.shape[0])
        elif isinstance(el_idx, np.ndarray):
            el_idx_it = el_idx
        else:
            raise TypeError("el_idx must be of type numpy.ndarray, or None")

        mesh_centroids = np.zeros((self.Connectivity.shape[0], 3), dtype=float)
        vprint("Computing mesh centroids", end="", verbose=self._Verbosity >= v_def.debug)

        with Pool(processes=processes) as pool:
            t_start = time.time()
            for i, res in enumerate(
                pool.map(
                    partial(
                        _compute_mesh_centroids,
                        connectivity=self.Connectivity,
                        coordinates=self.Coordinates,
                    ),
                    el_idx_it,
                )
            ):
                mesh_centroids[i] = res
        vprint(
            f" | Elapsed time: {datetime.timedelta(seconds=round(time.time() - t_start))}",
            verbose=self._Verbosity >= v_def.debug,
        )
        return mesh_centroids

    @property
    def Quality(self) -> np.ndarray | None:
        """
        Compute mesh metric with standard parameters. Doesn't update automatically for large meshes.

        Returns
        -------
        np.ndarray
            Array of mesh metric values. Return -1 for unsupported element types.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData
        >>> mesh.update_mesh_quality()
        >>> metric = mesh.Quality

        """
        max_element_threshold = 1e5  # Don't compute automatically for large meshes.
        if self.MeshInfo.NumElems < max_element_threshold:
            if self._Quality is None:
                self._Quality = self._get_mesh_quality()
        else:
            if self._flag_warn_element_quality:
                vprint(
                    "Warning: Quality not updated automatically due to large number of elements. "
                    'Please call "obj.update_mesh_quality()" to compute element quality.',
                    verbose=self._Verbosity >= v_def.release,
                )
                self._flag_warn_element_quality = False
        return self._Quality

    def update_mesh_quality(self, metric="quality", processes: int | None = None):
        """
        Compute mesh metric based on 'metric'.

        Parameters
        ----------
        metric : str, optional
            Metric type to compute. The default is 'quality'.
        processes : int, optional
            Number of processes to use in parallel. The default is ``None``, in which case all cores are used.

        Returns
        -------
        np.ndarray
            Array of mesh metric values. Return -1 for unsupported element types.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData
        >>> mesh.update_mesh_quality(metric='skewness', processes=1)
        >>> metric = mesh.Quality

        """
        """ Compute mesh metric """
        self._Quality = self._get_mesh_quality(metric=metric, processes=processes)

    def _get_mesh_quality(self, metric="quality", processes: int | None = None) -> np.ndarray:
        """Compute mesh metric based on 'metric'. Return -1 for unsupported element types."""
        supported_types = {
            "quality": (
                cfs_element_type.TRIA3,
                cfs_element_type.QUAD4,
                cfs_element_type.TET4,
                cfs_element_type.HEXA8,
                cfs_element_type.WEDGE6,
                cfs_element_type.PYRA5,
            ),
            "skewness": (cfs_element_type.TRIA3, cfs_element_type.QUAD4),
        }

        if metric not in supported_types:
            raise NotImplementedError(f"Implemented mesh quality metrics: {list(supported_types.keys())}.")

        mesh_quality = np.ones(self.Types.shape, dtype=float) * -1
        # Extract supported element types
        idx_support_lst = []
        for el_type in supported_types[metric]:
            idx_support_lst.append(np.where(self.Types == el_type)[0])
        idx_support = np.hstack(idx_support_lst)

        vprint("Computing mesh quality", end="", verbose=self._Verbosity >= v_def.debug)
        with Pool(processes=processes) as pool:
            t_start = time.time()
            for i, res in enumerate(
                pool.map(
                    partial(
                        _compute_mesh_quality,
                        connectivity=self.Connectivity,
                        coordinates=self.Coordinates,
                        el_types=self.Types,
                        metric=metric,
                    ),
                    idx_support,
                )
            ):
                mesh_quality[i] = res
        vprint(
            f" | Elapsed time: {datetime.timedelta(seconds=int(time.time() - t_start))}",
            verbose=self._Verbosity >= v_def.debug,
        )

        return mesh_quality

    def merge(self, other: CFSMeshData) -> CFSMeshData:
        """
        Merges mesh with other mesh removing duplicate Coordinates and elements

        Parameters
        ----------
        other : CFSMeshData
            Mesh data object that is merged with.

        Returns
        -------
        CFSMeshData
            Merged mesh data structure.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file1.cfs') as f:
        >>>     mesh1 = f.MeshData
        >>> with CFSReader('file2.cfs') as f:
        >>>     mesh2 = f.MeshData
        >>> mesh_merged = mesh1.merge(mesh2)

        """
        if type(other) is not CFSMeshData:
            raise NotImplementedError("Addition of CFSMeshData only implemented with other object of type CFSMeshData!")

        # Merge Coordinates
        coord_merge, idx_coord_inv = np.unique(
            np.append(self.Coordinates, other.Coordinates, axis=0),
            axis=0,
            return_inverse=True,
        )

        idx_coord_self = idx_coord_inv[: self.Coordinates.shape[0]]
        idx_coord_other = idx_coord_inv[self.Coordinates.shape[0] :]

        # Take starting index 1 for Connectivity into account (keep in mind there are 0 entries for unused columns)
        idx_coord_self = np.insert(idx_coord_self, 0, values=-1)
        idx_coord_other = np.insert(idx_coord_other, 0, values=-1)

        # Merge Connectivity
        conn_self = idx_coord_self[self.Connectivity] + 1
        conn_other = idx_coord_other[other.Connectivity] + 1

        num_rows = max(conn_self.shape[1], conn_other.shape[1])
        while conn_self.shape[1] < num_rows:
            conn_self = np.c_[conn_self, np.zeros(conn_self.shape[0])]

        while conn_other.shape[1] < num_rows:
            conn_other = np.c_[conn_other, np.zeros(conn_other.shape[0])]

        conn_merge, idx_conn, idx_conn_inv = np.unique(
            np.append(conn_self, conn_other, axis=0),
            axis=0,
            return_index=True,
            return_inverse=True,
        )

        idx_conn_self = idx_conn_inv[: conn_self.shape[0]]
        idx_conn_other = idx_conn_inv[conn_self.shape[0] :]

        # Merge types
        types_merge = np.append(self.Types, other.Types)[idx_conn]

        # Create merged mesh object
        return_mesh = CFSMeshData(
            coordinates=coord_merge,
            connectivity=conn_merge,
            types=types_merge,
            verbosity=self._Verbosity,
        )

        if self.Regions or other.Regions:
            # Merge and update regions
            for reg in self.Regions:
                return_reg = CFSRegData(
                    name=reg.Name,
                    dimension=reg.Dimension,
                    is_group=reg.IsGroup,
                    verbosity=self._Verbosity,
                )
                return_reg.Nodes = idx_coord_self[reg.Nodes] + 1
                return_reg.Elements = idx_conn_self[reg.Elements - 1] + 1
                return_mesh.Regions.append(return_reg)
            for reg in other.Regions:
                return_reg = CFSRegData(
                    name=reg.Name,
                    dimension=reg.Dimension,
                    is_group=reg.IsGroup,
                    verbosity=self._Verbosity,
                )
                return_reg.Nodes = idx_coord_other[reg.Nodes] + 1
                return_reg.Elements = idx_conn_other[reg.Elements - 1] + 1
                return_mesh.Regions.append(return_reg)

        return return_mesh

    def update_info(self) -> None:
        """Update structure based on coordinate and element types"""
        self.MeshInfo.update_by_coord_types(coordinates=self.Coordinates, types=self.Types)

    def check_add_point_elements(self) -> None:
        """Check groups/regions for not defined Elements (Nodes only) and create POINT elements"""
        for reg in self.Regions:
            if reg.Elements.size == 0:
                vprint(
                    f"Missing point elements detected in group/region {reg.Name}. Adding point elements.",
                    verbose=self._Verbosity >= v_def.release,
                )
                # Define Element IDs
                reg.Elements = np.arange(reg.Nodes.size, dtype=np.int32) + self.Connectivity.shape[0] + 1
                # Add elements to connectivity and types
                conn_add = np.zeros((reg.Nodes.size, self.Connectivity.shape[1]))
                conn_add[:, 0] = reg.Nodes
                el_types_add = np.array([cfs_element_type.POINT for _ in range(reg.Nodes.size)], dtype=np.int32)
                self.Connectivity = np.vstack((self.Connectivity, conn_add))
                self.Types = np.hstack((self.Types, el_types_add))

    def drop_unused_nodes_elements(self, reg_data_list: List[CFSRegData]):
        """
        Drop nodes and elements that are not used in the given list of groups/regions.

        Parameters
        ----------
        reg_data_list : list[CFSRegData]
            List of groups/regions

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> from pyCFS.data.util import list_search
        >>> with CFSReader('file1.cfs') as f:
        >>>     mesh = f.MeshData
        >>>     regions_data = f.MeshGroupsRegions
        >>> regions_data_keep = [list_search(regions_data, 'region_name')]
        >>> mesh.drop_unused_nodes_elements(reg_data_list=regions_data_keep)

        """
        self._drop_unused_elements(reg_data_list)
        self._drop_unused_nodes(reg_data_list)
        self.Regions = reg_data_list

    # noinspection PyTypeChecker,LongLine
    def _drop_unused_elements(self, reg_data_list: List[CFSRegData]) -> bool:
        """
        Drop elements that are not used in the given list of groups/regions.

        Parameters
        ----------
        reg_data_list

        Returns
        -------
        bool

        """
        # TODO optimize (see for CFSRegData.update_nodes_from_elements)
        used_elements = set()
        for reg_data in reg_data_list:
            used_elements.update(reg_data.Elements.tolist())
        if self.Types.size == len(used_elements):
            vprint("No elements dropped", verbose=self._Verbosity > v_def.release)
            return False
        conn = []
        el_type = []
        counter = 1
        el_id_dict = {}
        for el_id in progressbar(
            range(self.Connectivity.shape[0]),
            prefix=f"{self.Types.size - len(used_elements)} elements dropped. Renumbering elments: ",
            size=24,
            verbose=self._Verbosity >= v_def.release,
        ):
            if el_id + 1 in used_elements:
                el_id_dict[el_id + 1] = counter
                counter += 1
                conn.append(self.Connectivity[el_id, :])
                el_type.append(self.Types[el_id])

        self.Connectivity = np.array(conn)

        # Remove columns containing zeros only
        idx = np.argwhere(np.all(self.Connectivity[..., :] == 0, axis=0))
        self.Connectivity = np.delete(self.Connectivity, idx, axis=1)

        self.Types = np.array(el_type)
        self.MeshInfo.update_by_coord_types(self.Coordinates, self.Types)

        for reg_data in reg_data_list:
            reg_data.Elements = np.array([el_id_dict[el_id] for el_id in reg_data.Elements])
        return True

    # noinspection PyTypeChecker,LongLine
    def _drop_unused_nodes(self, reg_data_list: List[CFSRegData]):
        """
        Drop nodes that are not used in the given list of groups/regions.

        Parameters
        ----------
        reg_data_list

        Returns
        -------
        bool

        """
        # TODO optimize (see for CFSRegData.update_nodes_from_elements)
        used_nodes = set()
        for reg_data in reg_data_list:
            used_nodes.update(reg_data.Nodes.tolist())
        if self.Coordinates.shape[0] == len(used_nodes):
            vprint("No nodes dropped", verbose=self._Verbosity > v_def.release)
            return False
        coord = []
        counter = 1
        node_id_dict = {0: 0}
        for node_id in progressbar(
            range(self.Coordinates.shape[0]),
            prefix=f"{self.Coordinates.shape[0] - len(used_nodes)} nodes dropped. Renumbering nodes: ",
            size=26,
            verbose=self._Verbosity >= v_def.release,
        ):
            if node_id + 1 in used_nodes:
                node_id_dict[node_id + 1] = counter
                counter += 1
                coord.append(self.Coordinates[node_id, :])

        self.Coordinates = np.array(coord)
        self.MeshInfo.update_by_coord_types(self.Coordinates, self.Types)

        for c in range(self.Connectivity.shape[1]):
            self.Connectivity[:, c] = np.vectorize(node_id_dict.get)(self.Connectivity[:, c])

        for reg_data in reg_data_list:
            reg_data.Nodes = np.vectorize(node_id_dict.get)(reg_data.Nodes)
            # reg_data.Nodes = np.array([node_id_dict[nd_id] for nd_id in reg_data.Nodes])

        return True

    def convert_to_simplex(self, idx_convert: np.ndarray | None = None, result_data: CFSResultData | None = None):
        """
        Convert arbitrary 3D elements into simplices (tetrahedra), by applying Delaunay triangulation.
        """
        # TODO Check algorithm to prevent holes inside the volume domain
        # TODO Add support for 2D elements
        supported_types = {
            # cfs_element_type.QUAD4, cfs_element_type.QUAD8, cfs_element_type.QUAD9,
            cfs_element_type.TET10,
            cfs_element_type.HEXA8,
            cfs_element_type.HEXA20,
            cfs_element_type.HEXA27,
            cfs_element_type.PYRA5,
            cfs_element_type.PYRA13,
            cfs_element_type.PYRA14,
            cfs_element_type.WEDGE6,
            cfs_element_type.WEDGE15,
            cfs_element_type.WEDGE18,
            cfs_element_type.POLYHEDRON,
        }

        if idx_convert is None:
            idx_convert = np.array([i for i in range(self.Connectivity.shape[0])])

        num_el = self.Connectivity.shape[0]
        idx_convert_dict = {}
        reg_idx_convert_dict: Dict = {reg.Name: {} for reg in self.Regions}

        conn_add = []
        types_add = []

        for idx in progressbar(
            idx_convert,
            prefix="Converting elements into simplexes: ",
            verbose=self._Verbosity >= v_def.release,
        ):
            if cfs_element_type(self.Types[idx]) not in supported_types:
                if cfs_element_type(self.Types[idx]) == cfs_element_type.UNDEF:
                    vprint(
                        f"Warning: Element of type {cfs_element_type.UNDEF} can lead to unexpected result!",
                        verbose=self._Verbosity >= v_def.more,
                    )
                else:
                    vprint(
                        f"Skipped unsupported element ({cfs_element_type(self.Types[idx])})!",
                        verbose=self._Verbosity >= v_def.more,
                    )
                    continue
            conn_complex = self.Connectivity[idx, :]
            # Remove columns containing zeros only
            idx_zero = np.argwhere(conn_complex == 0).flatten()
            conn_complex = np.delete(conn_complex, idx_zero)
            coord_complex = self.Coordinates[conn_complex - 1, :]
            tri = Delaunay(coord_complex)

            complex_simplex_link = {i: conn_complex[i] for i in range(conn_complex.shape[0])}
            conn_simplex = np.vectorize(complex_simplex_link.get)(tri.simplices)
            conn_simplex = np.hstack(
                (
                    conn_simplex,
                    np.zeros(
                        (
                            conn_simplex.shape[0],
                            self.Connectivity.shape[1] - conn_simplex.shape[1],
                        ),
                        dtype=int,
                    ),
                )
            )

            vprint(
                f"Converted element ({cfs_element_type(self.Types[idx])}) into {conn_simplex.shape[0]} elements ({cfs_element_type.TET4})",
                verbose=self._Verbosity >= v_def.debug,
            )

            self.Connectivity[idx, :] = conn_simplex[0, :]  # Replace element
            self.Types[idx] = cfs_element_type.TET4

            conn_add.append(conn_simplex[1:, :])
            types_add.append(np.array([cfs_element_type.TET4 for i in range(conn_simplex.shape[0] - 1)]))

            idx_convert_dict[idx] = np.array([idx] + [i + num_el for i in range(conn_simplex.shape[0] - 1)])
            num_el += conn_simplex.shape[0] - 1  # Update number of elements

            for reg in self.Regions:
                if idx + 1 in reg.Elements.flatten():
                    reg_el_idx = int(np.where(idx + 1 == reg.Elements.flatten())[0].item())
                    reg_idx_convert_dict[reg.Name][reg_el_idx] = np.array(
                        [reg_el_idx] + [i + reg.Elements.size for i in range(conn_simplex.shape[0] - 1)]
                    )

                    reg.Elements = np.vstack(
                        (
                            np.expand_dims(reg.Elements.flatten(), 1),
                            np.expand_dims(idx_convert_dict[idx][1:] + 1, 1),
                        )
                    ).flatten()

        # Add additional elements
        self.Connectivity = np.vstack([self.Connectivity] + conn_add)
        self.Types = np.hstack([self.Types] + types_add)

        self.update_info()

        # Remove columns containing zeros only
        idx = np.argwhere(np.all(self.Connectivity[..., :] == 0, axis=0))
        self.Connectivity = np.delete(self.Connectivity, idx, axis=1)

        # Adapt element result data
        if result_data is not None:
            for res_idx, res_data in enumerate(result_data.Data):
                if res_data.ResType == cfs_result_type.ELEMENT:
                    data_list = []
                    for k in progressbar(
                        range(res_data.StepValues.size),
                        prefix=f"Converting result {res_data.Quantity}: ",
                        verbose=self._Verbosity >= v_def.more,
                    ):
                        data = res_data[k, :, :]
                        for idx in reg_idx_convert_dict[res_data.Region]:
                            val = data[idx, :]
                            data = np.vstack(
                                (
                                    data,
                                    np.ones(
                                        (
                                            reg_idx_convert_dict[res_data.Region][idx].size - 1,
                                            res_data.shape[2],
                                        )
                                    )
                                    * val,
                                )
                            )
                        data_list.append(data)
                    res_data_new = CFSResultArray(np.array(data_list))
                    res_data_new.MetaData = res_data.MetaData
                    result_data.Data[res_idx] = res_data_new

            return result_data

        return None

    def convert_quad2tria(self, idx_convert: np.ndarray | None = None, result_data=None):
        """
        Convert QUAD4 elements into TRIA3 elements. If 'idx_convert' is unspecified all QUAD4 in the mesh are converted.
        """
        conn = self.Connectivity
        # Get indices of quad4 elements
        idx_quad = np.where(self.Types == cfs_element_type.QUAD4)[0]
        if idx_convert is not None:
            # Check if all specified indices are quad4 elements
            idx_quad_convert = np.intersect1d(idx_quad, idx_convert)
            if idx_quad_convert.size < idx_convert.size:
                vprint(
                    "Warning: Some element indices are ignored because the element is not of type QUAD4!",
                    verbose=self._Verbosity >= v_def.debug,
                )
        else:
            idx_quad_convert = idx_quad

        conn_quad = conn[idx_quad_convert, :]
        conn_quad_tria = np.hstack(
            (
                conn_quad[:, (0, 1, 2)],
                np.zeros((conn_quad.shape[0], self.Connectivity.shape[1] - 3), dtype=int),
            )
        )
        conn_tria_add = np.hstack(
            (
                conn_quad[:, (0, 2, 3)],
                np.zeros((conn_quad.shape[0], self.Connectivity.shape[1] - 3), dtype=int),
            )
        )
        idx_tria_add = np.array([i for i in range(conn.shape[0], conn.shape[0] + conn_tria_add.shape[0])])

        self.Connectivity = np.vstack((conn, conn_tria_add))
        self.Connectivity[idx_quad_convert, :] = conn_quad_tria
        self.Types = np.hstack(
            (
                self.Types,
                np.array([cfs_element_type.TRIA3 for i in range(conn_tria_add.shape[0])]),
            )
        )
        self.Types[idx_quad_convert] = cfs_element_type.TRIA3
        self.update_info()

        for reg in self.Regions:
            idx_reg_quad = np.where(np.in1d(reg.Elements.flatten(), idx_quad_convert + 1))[0]
            idx_reg_tria_add = np.where(np.in1d(idx_quad_convert, reg.Elements[idx_reg_quad] - 1))
            reg.Elements = np.vstack(
                (
                    np.expand_dims(reg.Elements.flatten(), 1),
                    np.expand_dims(idx_tria_add[idx_reg_tria_add] + 1, 1),
                )
            ).flatten()

        # Remove columns containing zeros only
        idx = np.argwhere(np.all(self.Connectivity[..., :] == 0, axis=0))
        self.Connectivity = np.delete(self.Connectivity, idx, axis=1)

        if result_data is not None:
            # TODO: Adapt element result data
            raise NotImplementedError("Adapting result data not implemented!")
            return result_data

        return None

    def get_region(self, region: str | CFSRegData) -> CFSRegData:
        return list_search(self.Regions, region)

    def get_region_nodes(self, region: str | CFSRegData) -> np.ndarray:
        reg_obj = self.get_region(region=region)
        return reg_obj.Nodes

    def get_region_elements(self, region: str | CFSRegData) -> np.ndarray:
        reg_obj = self.get_region(region=region)
        return reg_obj.Elements

    def get_region_coordinates(self, region: str | CFSRegData) -> np.ndarray:
        reg_obj = self.get_region(region=region)
        return self.Coordinates[reg_obj.Nodes - 1]

    def get_region_connectivity(self, region: str | CFSRegData) -> np.ndarray:
        reg_obj = self.get_region(region=region)
        return self.Connectivity[reg_obj.Elements - 1]

    def get_region_centroids(self, region: str | CFSRegData, processes: int | None = None) -> np.ndarray:
        reg_obj = self.get_region(region=region)
        return self.get_mesh_centroids(el_idx=reg_obj.Elements - 1, processes=processes)

    def get_closest_node(
        self, coordinate: np.ndarray, region: str | CFSRegData | None = None, eps: float = 1e-3
    ) -> np.ndarray:
        """
        Return node ids of closest nodes to coordinate array.

        Parameters
        ----------

        coordinate: np.ndarray
            Coordinate array (Nx3, N is the number of query points)
        region : str or CFSRegData, optional
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
        >>>     mesh = f.MeshData
        >>>     node_indices = mesh.get_closest_node(search_coord):

        """
        if region is None:
            search_coord = self.Coordinates
        else:
            search_coord = self.get_region_coordinates(region=region)
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
        >>>     mesh = f.MeshData
        >>>     element_indices = mesh.get_closest_element(search_coord):

        """
        if region is None:
            search_conn = self.Connectivity
        else:
            search_conn = self.get_region_connectivity(region=region)

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

    def reorient_region(self, region_name: str) -> None:
        vprint(
            f"Reorienting elements in region {region_name}",
            verbose=self._Verbosity >= v_def.more,
        )
        region = list_search(self.Regions, region_name)
        self.reorient_elements(idx_reorient=region.Elements - 1)

    def reorient_elements(self, idx_reorient: List) -> None:
        for el_idx in progressbar(
            idx_reorient,
            prefix="Reorienting elements: ",
            verbose=self._Verbosity >= v_def.debug,
        ):
            if self.Types[el_idx] == cfs_element_type.LINE2:
                self.Connectivity[el_idx, [0, 1]] = self.Connectivity[el_idx, [1, 0]]
            elif self.Types[el_idx] == cfs_element_type.TRIA3:
                self.Connectivity[el_idx, [0, 1]] = self.Connectivity[el_idx, [1, 0]]
            elif self.Types[el_idx] == cfs_element_type.QUAD4:
                self.Connectivity[el_idx, [1, 3]] = self.Connectivity[el_idx, [3, 1]]
            else:
                raise NotImplementedError(f"Reorienting of element type {self.Types[el_idx]} not implemented!")


class CFSRegData:
    """
    Data structure containing mesh region definition

    Parameters
    ----------
    name : str, optional
        Group/Region name
    elements : numpy.ndarray, optional
        array of element ids (Nx1) of the group/region (N number of elements in the group/region).
    nodes : numpy.ndarray, optional
        array of node ids (Nx1) of the group/region (N number of nodes in the group/region).
    dimension : int, optional
        Group/Region dimension
    is_group : bool, optional
        flag indicating if the entity is a group.
    verbosity : int, optional
        Verbosity level <=1000 ; see v_def.py for predefined levels. Default is v_def.release.

    Attributes
    ----------
    Name : str
        Group/Region name
    Elements
    Nodes
    Dimension : int
        Group/Region dimension
    IsGroup : bool
        flag indicating if the entity is a group.

    Methods
    -------
    * `merge` `(other: CFSRegData)`
        Merges region with other region removing duplicate node/element indices
    * `update_nodes_from_elements` `(elems: np.ndarray, connectivity: np.ndarray) -> (np.ndarray, np.ndarray)`
        Update region nodes based on element ids.

    Examples
    --------
    >>> from pyCFS.data.io import CFSReader, CFSMeshInfo
    >>> with CFSReader('file.cfs') as f:
    >>>     coordinates = f.Coordinates
    >>>     connectivity = f.Connectivity
    >>>     ElementTypes = f.ElementTypes
    >>>     region_data = f.MeshGroupsRegions
    >>> mesh = CFSMeshData(coordinates=coordinates, connectivity=connectivity, ElementTypes=ElementTypes,
    >>>                    regions=region_data)

    """

    def __init__(
        self,
        name: str,
        elements=np.empty(0),
        nodes=np.empty(0),
        dimension=-1,
        is_group=False,
        verbosity=v_def.release,
    ):
        self._Elements = np.empty(0)
        self._Nodes = np.empty(0)

        self.Name = name
        self.Elements = elements
        self.Nodes = nodes
        self.Dimension: int = dimension
        self.IsGroup: bool = is_group
        self._Verbosity = verbosity

    @property
    def Nodes(self):
        return self._Nodes

    @Nodes.setter
    def Nodes(self, nodes: np.ndarray):
        self._Nodes = np.array(nodes, dtype=np.uint32)

    @property
    def Elements(self):
        return self._Elements

    @Elements.setter
    def Elements(self, elements: np.ndarray):
        self._Elements = np.array(elements, dtype=np.int32)

    def __repr__(self) -> str:
        if self.IsGroup:
            reg_type = "Group"
        else:
            reg_type = "Region"
        return f"{reg_type}: {self.Name}"

    def __str__(self) -> str:
        if self.IsGroup:
            reg_type = "Group"
        else:
            reg_type = "Region"
        return textwrap.dedent(
            f"""\
        {reg_type}:   {self.Name}
         - Dimension: {self.Dimension}
         - Nodes:     {self.Nodes.size}
         - Elements:  {self.Elements.size}"""
        )

    def __eq__(self, other: object | str):
        if not isinstance(other, CFSRegData):
            if type(other) is str:
                return self.Name == other
            else:
                raise NotImplementedError("Object comparison implemented for CFSRegData and str only!")
        return all(
            [
                self.Name == other.Name,
                np.array_equal(self.Elements, other.Elements),
                np.array_equal(self.Nodes, other.Nodes),
                self.Dimension == other.Dimension,
            ]
        )

    def __lt__(self, other):
        if not isinstance(other, CFSRegData):
            raise NotImplementedError("Object comparison implemented for CFSRegData and str only!")
        else:
            return self.Name < other.Name

    def __add__(self, other: CFSRegData):
        return_data, _, _ = self.merge(other)
        return return_data

    def merge(self, other: CFSRegData):
        """
        Merges region with other region removing duplicate node/element indices
        """
        # TODO add method to manipulate data after region merge
        if type(other) is not CFSRegData:
            raise NotImplementedError("Addition of CFSRegData only implemented with other object of type CFSRegData!")
        return_data = CFSRegData(self.Name, verbosity=self._Verbosity)
        return_data.Dimension = max(self.Dimension, other.Dimension)
        return_data.IsGroup = self.IsGroup
        if other.IsGroup != self.IsGroup:
            p_dict = {False: "region", True: "group"}
            vprint(
                f"Merging {p_dict[self.IsGroup]} with {p_dict[other.IsGroup]} into {p_dict[return_data.IsGroup]}",
                verbose=self._Verbosity > v_def.release,
            )
        return_data.Nodes, idx_node = np.unique(np.append(self.Nodes, other.Nodes), return_index=True)
        return_data.Elements, idx_elem = np.unique(np.append(self.Elements, other.Elements), return_index=True)

        return return_data, idx_node, idx_elem

    def update_nodes_from_elements(
        self, elems: np.ndarray, connectivity: np.ndarray
    ) -> Tuple[np.ndarray | None, np.ndarray | None]:
        """
        Update region nodes based on element ids.

        Parameters
        ----------
        elems : numpy.ndarray
        connectivity: numpy.ndarray

        Returns
        -------
        node_idx : numpy.ndarray
            Updated node indices (starting from 0)
        elem_idx : numpy.ndarray
            Updated element indices (starting from 0)

        """
        reg_conn = connectivity[elems - 1]
        nodes = np.unique(reg_conn)
        # Remove zero entry
        nodes = np.delete(nodes, np.where(nodes == 0)[0])

        node_idx = None
        if np.all(np.in1d(nodes, self.Nodes)):
            _, idx_intersect, node_idx = np.intersect1d(nodes, self.Nodes, return_indices=True)
            nodes = nodes[idx_intersect]

        elem_idx = None
        if np.all(np.in1d(elems, self.Elements)):
            _, idx_intersect, elem_idx = np.intersect1d(elems, self.Elements, return_indices=True)
            elems = elems[idx_intersect]

        self.Nodes = nodes
        self.Elements = elems

        return node_idx, elem_idx


# Usability functions
def _compute_mesh_centroids(idx: int, connectivity: np.ndarray, coordinates: np.ndarray):
    """Helper function for CFSMeshData._get_mesh_centroids. Computes element centroid for single element in mesh"""
    element_connectivity = connectivity[idx, :]
    # Remove 0 entries
    idx_zeros = np.argwhere(element_connectivity == 0)
    element_connectivity = np.delete(element_connectivity, idx_zeros)
    element_coordinates = coordinates[element_connectivity - 1, :]
    return element_centroid(element_coordinates)


def _compute_mesh_quality(
    idx: int, connectivity: np.ndarray, coordinates: np.ndarray, el_types: np.ndarray, metric: str
):
    """Helper function for CFSMeshData._get_mesh_quality. Computes element quality for single element in mesh"""
    element_connectivity = connectivity[idx, :]
    # Remove 0 entries
    idx_zeros = np.argwhere(element_connectivity == 0)
    element_connectivity = np.delete(element_connectivity, idx_zeros)
    element_coordinates = coordinates[element_connectivity - 1, :]
    return element_quality(element_coordinates, cfs_element_type(el_types[idx]), metric=metric)


def mesh_from_coordinates_connectivity(
    coordinates: np.ndarray,
    connectivity: np.ndarray,
    element_dimension: int | None = None,
    region_name="Region",
    verbosity=v_def.release,
) -> CFSMeshData:
    """
    Generates data objects to create cfs mesh with one single region containing all elements. Detects element type from
    number of nodes. Therefore, all elements must have same dimension.

    Parameters
    ----------
    coordinates : numpy.ndarray, optional
        Coordinate array (NxD) of the whole mesh (N number of nodes, D space dimension)
    connectivity : numpy.ndarray, optional
        Connectivity array (NxM) of the whole mesh (N number of elements, M maximum number of nodes per element).
        Includes zero entries in case of different element types.
    element_dimension : int, optional
        Dimension of all elements. Default is ``None`` in which case the dimension is chosen based on the coordinates
        parameter
    region_name : str, optional
    verbosity : int, optional
        Verbosity level <=1000 ; see v_def.py for predefined levels. Default is v_def.release.

    Returns
    -------
    pyCFS.data.io.CFSMeshData
        Mesh data structure.

    Examples
    --------
    >>> from pyCFS.data.io import CFSReader
    >>> with CFSReader('file.cfs') as f:
    >>>     coordinates = f.Coordinates
    >>>     connectivity = f.Connectivity
    >>>     ElementTypes = f.ElementTypes
    >>>     region_data = f.MeshGroupsRegions
    >>> mesh = mesh_from_coordinates_connectivity(coordinates=coordinates, connectivity=connectivity,
    >>>                                           element_dimension=3, region_name='region')

    """
    if element_dimension is None:
        element_dimension = coordinates.shape[1]

    type_link = {
        0: {1: cfs_element_type.POINT},
        1: {2: cfs_element_type.LINE2, 3: cfs_element_type.LINE3},
        2: {
            3: cfs_element_type.TRIA3,
            6: cfs_element_type.TRIA6,
            4: cfs_element_type.QUAD4,
            8: cfs_element_type.QUAD8,
            9: cfs_element_type.QUAD9,
        },
        3: {
            4: cfs_element_type.TET4,
            10: cfs_element_type.TET10,
            8: cfs_element_type.HEXA8,
            20: cfs_element_type.HEXA20,
            27: cfs_element_type.HEXA27,
            5: cfs_element_type.PYRA5,
            13: cfs_element_type.PYRA13,
            14: cfs_element_type.PYRA14,
            6: cfs_element_type.WEDGE6,
            15: cfs_element_type.WEDGE15,
            18: cfs_element_type.WEDGE18,
        },
    }

    type_list = []
    for i in range(connectivity.shape[0]):
        num_nodes = np.nonzero(connectivity[i, :])[0].size
        if num_nodes in type_link[element_dimension]:
            type_list.append(cfs_element_type(type_link[element_dimension][num_nodes]))
        else:
            type_list.append(cfs_element_type.UNDEF)
    type_array = np.array(type_list)

    reg_node = np.array([i + 1 for i in range(coordinates.shape[0])])
    reg_el = np.array([i + 1 for i in range(connectivity.shape[0])])
    reg_data = [
        CFSRegData(
            name=region_name,
            elements=reg_el,
            nodes=reg_node,
            dimension=element_dimension,
            verbosity=verbosity,
        )
    ]

    mesh_data = CFSMeshData(
        coordinates=coordinates,
        connectivity=connectivity,
        types=type_array,
        regions=reg_data,
        verbosity=verbosity,
    )

    return mesh_data

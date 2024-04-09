"""
Module containing data processing utilities for writing HDF5 files in openCFS format
"""

from __future__ import annotations

import os
import pathlib

import h5py
import numpy as np
from typing import List, Dict, Tuple

from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type
from pyCFS.data.util import vprint, progressbar

from pyCFS.data.io.CFSMeshData import CFSMeshData, CFSMeshInfo, CFSRegData
from pyCFS.data.io.CFSResultData import CFSResultData, CFSResultInfo

from pyCFS.data import v_def


class CFSWriter:
    """
    Base class for all writing operations

    Parameters
    ----------
    filename : str
        Path to the hdf5 file.
    h5driver : str, optional
        Driver used to read the hdf5 file (see h5py documentation). The default is ``None``, in which case the standard
        driver is used.
    compression_lvl : int, optional
        Defines the GZIP compression level used for writing all large datasets in the hdf5 file.
        The default level is ``6``.
    verbosity : int, optional
        Verbosity level <=1000 ; see v_def.py for predefined levels. Default is v_def.release.

    Attributes
    ----------
    CompressionLvl : int
        GZIP compression level used for writing all large datasets in the hdf5 file.

    Methods
    -------
    * `create_file` `(mesh_data: CFSMeshData = None, result_data: CFSResultData = None)`
        Perform all steps to create an empty HDF5 file and write Mesh and (optionally) Results to it.
    * `create_mesh` `(MeshInfo: CFSMeshInfo, regions_data: list[CFSRegData])`
        Create Mesh structure and write mesh information to the active hdf5 file.
    * `write_mesh` `(mesh_data: CFSMeshData)`
        Write Mesh data to the active hdf5 file.
    * `prepare_write_multistep` `(res_info: list[CFSResultInfo], res_shape_dict: dict, multiStep=1, AnalysisType='transient')`
        Write ResultDescription and create datasets (needs to be done a priori in case of parallel write)
    * `perform_write_multistep` `(result_data: CFSResultData)`
        Write data to MultiStep
    * `finalize_write_multistep` `(res_info: list[CFSResultInfo], multiStep=1)`
        Write datasets to ResultsDescription that need to be written after the data (in case of parallel write)
    * `write_multistep` `(result_data: CFSResultData)`
        Write ResultDescription and create datasets, write data to multistep and write datasets to ResultsDescription
        that need to be written after the data (in case of parallel write)

    Examples
    --------
    >>> from pyCFS.data.io import CFSReader, CFSWriter
    >>> with CFSReader('file.cfs') as f:
    >>>     mesh = f.MeshData
    >>>     results = f.MultiStepData
    >>> with CFSWriter('file.cfs') as f:
    >>>     f.create_file(mesh_data=mesh,result_data=results)

    """

    def __init__(self, filename: str, h5driver=None, compression_lvl=6, verbosity=v_def.release) -> None:
        """Initialize the writer"""
        self._filename = filename
        self._h5driver = h5driver
        self.CompressionLvl = compression_lvl
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
            return f"CFSWriter linked to file_src '{self._filename}', Verbosity {self._Verbosity}"
        else:
            return "Closed CFSWriter"

    def create_file(self, mesh_data: CFSMeshData | None = None, result_data: CFSResultData | None = None):
        """
        Perform all steps to create an empty HDF5 file and write Mesh and (optionally) Results to it.

        Parameters
        ----------
        mesh_data : CFSMeshData, optional
            Data structure containing all information about the mesh. The default is ``None``, in which case no mesh
            nor result data is written.
        result_data : CFSResultData, optional
            Data structure containing all information about the multiStep that will be written to the active file.
            The default is ``None``, in which case no result data is written.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader, CFSWriter
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshData
        >>>     results = f.MultiStepData
        >>> with CFSWriter('file.cfs') as f:
        >>>     f.create_file(mesh_data=mesh,result_data=results)

        """
        vprint(f"Creating file {self._filename}", verbose=self._Verbosity >= v_def.min)
        pathlib.Path(os.path.split(self._filename)[0]).mkdir(parents=True, exist_ok=True)
        with h5py.File(self._filename, "w", driver=self._h5driver) as f:
            f.require_group("FileInfo")

            f.require_group("Mesh")
            f.require_group("Results")
        if mesh_data is not None:
            self.create_mesh(mesh_info=mesh_data.MeshInfo, regions_data=mesh_data.Regions)
            self.write_mesh(mesh_data=mesh_data)
            if result_data is not None:
                self.write_multistep(result_data=result_data)

    def create_mesh(self, mesh_info: CFSMeshInfo, regions_data: List[CFSRegData]):
        """
        Create Mesh structure and write mesh information to the active hdf5 file.

        Parameters
        ----------
        mesh_info : CFSMeshInfo
            Data structure containing all mesh attributes.
        regions_data : list[CFSRegData]
            List of data structures containing data of all regions/groups.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader, CFSWriter
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh_info = f.MeshInfo
        >>>     regions_data = f.MeshGroupsRegions
        >>> with CFSWriter('file.cfs') as f:
        >>>     f.create_file()
        >>>     f.create_mesh(mesh_info=mesh_info,regions_data=regions_data)

        """
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            grp_mesh = f["Mesh"]
            grp_mesh.attrs.create("Dimension", mesh_info.Dimension, dtype=np.dtype("uint32"))

            vprint("Creating Mesh Structure", verbose=self._Verbosity >= v_def.more)
            # Elements
            vprint(" - Creating Elements", verbose=self._Verbosity >= v_def.debug)
            grp_elem = grp_mesh.require_group("Elements")
            grp_elem.attrs.create("Num1DElems", mesh_info.Num1DElems, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num2DElems", mesh_info.Num2DElems, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num3DElems", mesh_info.Num3DElems, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("NumElems", mesh_info.NumElems, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_HEXA20", mesh_info.Num_HEXA20, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_HEXA27", mesh_info.Num_HEXA27, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_HEXA8", mesh_info.Num_HEXA8, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_LINE2", mesh_info.Num_LINE2, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_LINE3", mesh_info.Num_LINE3, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_POINT", mesh_info.Num_POINT, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_POLYGON", mesh_info.Num_POLYGON, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_POLYHEDRON", mesh_info.Num_POLYHEDRON, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_PYRA13", mesh_info.Num_PYRA13, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_PYRA14", mesh_info.Num_PYRA14, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_PYRA5", mesh_info.Num_PYRA5, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_QUAD4", mesh_info.Num_QUAD4, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_QUAD8", mesh_info.Num_QUAD8, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_QUAD9", mesh_info.Num_QUAD9, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_TET10", mesh_info.Num_TET10, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_TET4", mesh_info.Num_TET4, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_TRIA3", mesh_info.Num_TRIA3, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_TRIA6", mesh_info.Num_TRIA6, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_UNDEF", mesh_info.Num_UNDEF, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_WEDGE15", mesh_info.Num_WEDGE15, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_WEDGE18", mesh_info.Num_WEDGE18, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("Num_WEDGE6", mesh_info.Num_WEDGE6, dtype=np.dtype("uint32"))
            grp_elem.attrs.create("QuadraticElems", mesh_info.QuadraticElems, dtype=np.dtype("int32"))
            # dset = grp_elem.require_dataset('Connectivity', shape=mesh_data_demo.Connectivity.shape,
            #                                dtype=np.dtype('uint32'),compression='gzip',
            #                                compression_opts=self.CompressionLvl)
            # cfsWriteDataset(dset, np.uint32(mesh_data_demo.Connectivity))
            # dset = grp_elem.require_dataset('Types', shape=mesh_data_demo.Types.shape, dtype=np.dtype('int32'),
            #                                compression='gzip',
            #                                compression_opts=self.CompressionLvl)
            # cfsWriteDataset(dset, np.int32(mesh_data_demo.Types))

            # Nodes
            vprint(" - Creating Nodes", verbose=self._Verbosity >= v_def.debug)
            grp_nodes = grp_mesh.require_group("Nodes")
            grp_nodes.attrs.create("NumNodes", mesh_info.NumNodes, dtype=np.dtype("uint32"))
            # dset = grp_nodes.require_dataset('Coordinates', shape=mesh_data_demo.Coordinates.shape, dtype=np.float64,
            #                                 compression='gzip', compression_opts=self.CompressionLvl)
            # cfsWriteDataset(dset, np.float64(mesh_data_demo.Coordinates))

            # Groups / Regions
            grp_groups = grp_mesh.require_group("Groups")
            grp_reg = grp_mesh.require_group("Regions")

            for reg in regions_data:
                if reg.IsGroup:
                    reg_type = "Group"
                    grp_write = grp_groups
                else:
                    reg_type = "Region"
                    grp_write = grp_reg
                vprint(
                    f" - Creating {reg_type} {reg.Name}",
                    verbose=self._Verbosity >= v_def.debug,
                )
                grp_regname = grp_write.require_group(reg.Name)
                grp_regname.attrs.create("Dimension", reg.Dimension, dtype=np.dtype("uint32"))

    def write_mesh(self, mesh_data: CFSMeshData):
        """
        Write Mesh data to the active hdf5 file.

        Parameters
        ----------
        mesh_data : CFSMeshData
            Data structure containing all mesh data.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader, CFSWriter
        >>> with CFSReader('file.cfs') as f:
        >>>     mesh = f.MeshInfo
        >>> with CFSWriter('file.cfs') as f:
        >>>     f.create_file()
        >>>     f.create_mesh(mesh_info=mesh.MeshInfo,regions_data=mesh.Regions)
        >>>     f.write_mesh(MeshData=mesh)

        """
        vprint("Writing Mesh Data", verbose=self._Verbosity >= v_def.release)
        # vprint(f'Writing Element Connectivity', verbose=self._Verbosity >= v_def.debug)
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            dset = f["Mesh/Elements"].require_dataset(
                "Connectivity",
                shape=mesh_data.Connectivity.shape,
                dtype=np.dtype("uint32"),
                compression="gzip",
                compression_opts=self.CompressionLvl,
            )
            CFSWriter.write_dataset(dset, mesh_data.Connectivity.astype(np.uint32))
        vprint(" - Writing Element Types", verbose=self._Verbosity >= v_def.debug)
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            dset = f["Mesh/Elements"].require_dataset(
                "Types",
                shape=mesh_data.Types.shape,
                dtype=np.dtype("int32"),
                compression="gzip",
                compression_opts=self.CompressionLvl,
            )
            CFSWriter.write_dataset(dset, mesh_data.Types.astype(np.int32))
        vprint(" - Writing Node Coordinates", verbose=self._Verbosity >= v_def.debug)
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            dset = f["Mesh/Nodes"].require_dataset(
                "Coordinates",
                shape=mesh_data.Coordinates.shape,
                dtype=np.float64,
                compression="gzip",
                compression_opts=self.CompressionLvl,
            )
            CFSWriter.write_dataset(dset, mesh_data.Coordinates.astype(np.float64))

        for reg in mesh_data.Regions:
            if reg.IsGroup:
                reg_type = "Group"
            else:
                reg_type = "Region"
            vprint(
                f" - Writing {reg_type}: {reg.Name}",
                verbose=self._Verbosity >= v_def.release,
            )
            vprint(
                f" -- Writing Elements: Region {reg.Name}",
                verbose=self._Verbosity >= v_def.debug,
            )
            with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
                dset = f[f"Mesh/{reg_type}s/{reg.Name}"].require_dataset(
                    "Elements",
                    shape=reg.Elements.shape,
                    dtype=np.dtype("int32"),
                    compression="gzip",
                    compression_opts=self.CompressionLvl,
                )
                CFSWriter.write_dataset(dset, reg.Elements.astype(np.int32))
            vprint(
                f" -- Writing Nodes: Region {reg.Name}",
                verbose=self._Verbosity >= v_def.debug,
            )
            with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
                dset = f[f"Mesh/{reg_type}s/{reg.Name}"].require_dataset(
                    "Nodes",
                    shape=reg.Nodes.shape,
                    dtype=np.dtype("uint32"),
                    compression="gzip",
                    compression_opts=self.CompressionLvl,
                )
                CFSWriter.write_dataset(dset, reg.Nodes.astype(np.uint32))

    @staticmethod
    def write_dataset(dset: h5py.Dataset, data: np.ndarray):
        """
        Write dataset to active HDF5 file

        Parameters
        ----------
        dset : h5py.Dataset
            dataset object of opened HDF5 file
        data : numpy.ndarray
            data to write to active HDF5 file

        """
        dset[:] = data

    @staticmethod
    def write_dataset_parallel(dset: h5py.Dataset, data: np.ndarray, comm=None):
        """
        Write dataset to active HDF5 file

        Parameters
        ----------
        dset : h5py.Dataset
            dataset object of opened HDF5 file
        data : numpy.ndarray
            data to write to active HDF5 file
        comm : None, optional
            MPI communicator, The default is ``None``, in which case MPI.COMM_WORLD is used.

        """
        # TODO add parallel support again (h5pyp - h5py parallel build), once h5pyp fixes numpy bug
        raise NotImplementedError(
            "Parallel writing currently unavailable. See h5pyp (h5py parallel build) not working cause of numpy change"
        )

    #     # MPI communicator
    #     if not comm:
    #         comm = MPI.COMM_WORLD
    #
    #     ll = comm.rank * -(-data.shape[0] // comm.size)
    #     if comm.rank == comm.size - 1:
    #         ul = data.shape[0]
    #     else:
    #         ul = (comm.rank + 1) * -(-data.shape[0] // comm.size)
    #     with dset.collective:
    #         dset[ll:ul] = data[ll:ul]

    @staticmethod
    def create_result(grp_result: h5py.Group, externalFiles=False) -> h5py.Group:
        """
        Create new result
        :param grp_result: 'Result' Group object of opened HDF5 file_src
        :param externalFiles: flag whether data is stored in external files
        :return: 'Result/Mesh' Group object of opened HDF5 file_src
        """
        if "Mesh" in grp_result:
            grp_result_mesh = grp_result["Mesh"]
        else:
            grp_result_mesh = grp_result.require_group("Mesh")
            grp_result_mesh.attrs.create("ExternalFiles", data=externalFiles, dtype=np.dtype("int32"))

        return grp_result_mesh

    @staticmethod
    def create_multistep(
        grp_result_mesh: h5py.Group,
        multi_step_id=1,
        analysis_type=cfs_analysis_type.NO_ANALYSIS,
    ) -> Tuple[h5py.Group, h5py.Group]:
        """
        Create MultiStep
        :param grp_result_mesh:
        :param multi_step_id:
        :param analysis_type:
        :return: 'MultiStep' and 'ResultsDescription' object of opened HDF5 file_src
        """
        if f"MultiStep_{multi_step_id}" in grp_result_mesh:
            grp_multi_step = grp_result_mesh[f"MultiStep_{multi_step_id}"]
            grp_result_description = grp_result_mesh["ResultDescription"]
        else:
            if analysis_type == cfs_analysis_type.NO_ANALYSIS:
                print(f"WARNING: Created MultiStep result with analysis type {analysis_type}")
            grp_multi_step = grp_result_mesh.require_group(f"MultiStep_{multi_step_id}")
            grp_multi_step.attrs.create("AnalysisType", analysis_type, dtype=h5py.special_dtype(vlen=bytes))
            grp_multi_step.attrs.create("LastStepNum", data=0, dtype=np.dtype("uint32"))
            grp_multi_step.attrs.create("LastStepValue", data=0, dtype=np.dtype("float64"))

            grp_result_description = grp_multi_step.require_group("ResultDescription")

        return grp_multi_step, grp_result_description

    @staticmethod
    def create_result_description(
        grp_resultDescription: h5py.Group,
        qName: str,
        dim_names: List[str] | None = None,
        definedOn=cfs_result_type.NODE,
        entryType=1,
    ) -> None:
        """
        Create ResultDescription and write Information
        :param grp_resultDescription:
        :param qName:
        :param dim_names:
        :param definedOn:
        :param entryType:
        """
        # TODO Allow variables to be defined on multiple ResTypes
        # TODO Variable length with parallel io
        # TODO entryType based on data type (according to CFS source code: DataInOut/SimInOut/hdf5/hdf5io.cc::1877)
        if dim_names is None:
            dim_names = ["-"]
        grp_quantitiy = grp_resultDescription.require_group(qName)

        grp_quantitiy.require_dataset(
            "DefinedOn", data=int(definedOn), dtype=np.dtype("uint32"), shape=(1,)
        )  # 1 - Node, 4 - Element
        grp_quantitiy.require_dataset("EntryType", data=entryType, dtype=np.dtype("uint32"), shape=(1,))
        grp_quantitiy.require_dataset("NumDOFs", data=len(dim_names), dtype=np.dtype("uint32"), shape=(1,))
        grp_quantitiy.require_dataset(
            "StepNumbers",
            data=[],
            dtype=np.dtype("uint32"),
            shape=None,
            maxshape=(None,),
        )
        grp_quantitiy.require_dataset(
            "StepValues",
            data=[],
            dtype=np.dtype("float64"),
            shape=None,
            maxshape=(None,),
        )

    @staticmethod
    def finalize_result_description(
        grp_quantity: h5py.Group,
        reg_names: List[str],
        dim_names: List[str] | None = None,
        unit="",
    ) -> None:
        """
        Write DIMNames and Entity Names (needs to be done after data writing (in case of parallel write)
        :param grp_quantity:
        :param reg_names:
        :param dim_names:
        :param unit:
        """
        if dim_names is None:
            dim_names = ["-"]
        ds_dim_name = grp_quantity.create_dataset(
            "DOFNames", shape=(len(dim_names),), dtype=h5py.special_dtype(vlen=bytes)
        )
        for i in range(len(dim_names)):
            ds_dim_name[i] = dim_names[i].encode("utf-8")
        ds_entity_name = grp_quantity.create_dataset(
            "EntityNames", shape=(len(reg_names),), dtype=h5py.special_dtype(vlen=bytes)
        )
        for i in range(len(reg_names)):
            ds_entity_name[i] = reg_names[i]
        grp_quantity.create_dataset("Unit", data=unit, dtype=h5py.special_dtype(vlen=bytes))

    @staticmethod
    def create_step(
        grp_multi_step: h5py.Group,
        step_value: float = 0,
        step_num: int = 1,
        filename_external: str = "",
    ) -> h5py.Group:
        """
        Create step in MultiStep without updating LastStep-Attributes and ResultDescription for increased performance
        :param grp_multi_step:
        :param step_value:
        :param step_num:
        :param filename_external:
        :return: 'Step' object of opened HDF5 file_src
        """
        # Create Step
        grp_step = grp_multi_step.require_group(f"Step_{step_num}")
        grp_step.attrs.create("StepValue", data=step_value, dtype=np.dtype("float64"))

        if filename_external:
            grp_step.require_dataset(
                "ExtHDF5FileName",
                data=filename_external,
                dtype=h5py.special_dtype(vlen=bytes),
            )

        return grp_step

    @staticmethod
    def create_step_add(
        grp_multi_step: h5py.Group,
        q_list: List[str],
        step_value: float = 0,
        filename_external: str = "",
    ) -> h5py.Group:
        """
        Create step in MultiStep updating LastStep-Attributes and ResultDescription
        :param grp_multi_step:
        :param q_list:
        :param step_value:
        :param filename_external:
        :return: 'Step' object of opened HDF5 file_src
        """
        step_num = CFSWriter.add_step_update_attributes(grp_multi_step, q_list, step_value)
        # Create Step
        grp_step = grp_multi_step.require_group(f"Step_{step_num}")
        grp_step.attrs.create("StepValue", data=step_value, dtype=np.dtype("float64"))

        if filename_external:
            grp_step.require_dataset(
                "ExtHDF5FileName",
                data=filename_external,
                dtype=h5py.special_dtype(vlen=bytes),
            )

        return grp_step

    @staticmethod
    def set_step_attributes(
        grp_multi_step: h5py.Group,
        q_list: List[str],
        step_values: np.ndarray,
        step_nums: np.ndarray | None = None,
    ) -> None:
        """
        Set step values and numbers
        :param grp_multi_step:
        :param q_list:
        :param step_values:
        :param step_nums:
        :return:
        """
        # Number steps axcending if not specified
        if step_nums is None:
            step_nums = np.array([i + 1 for i in range(step_values.shape[0])])
        # Get Step Numbers and Values from description
        dset_step_numbers = [
            grp_multi_step["ResultDescription/" + q_list[i] + "/StepNumbers"] for i in range(len(q_list))
        ]
        dset_step_values = [
            grp_multi_step["ResultDescription/" + q_list[i] + "/StepValues"] for i in range(len(q_list))
        ]
        # Update Attributes
        grp_multi_step.attrs["LastStepNum"] = step_nums[-1]
        grp_multi_step.attrs["LastStepValue"] = step_values[-1]
        # Update Result Description
        for dset in dset_step_numbers:
            dset.resize(step_values.shape[0], axis=0)
            dset[...] = step_nums
        for dset in dset_step_values:
            dset.resize(step_values.shape[0], axis=0)
            dset[...] = step_values

        return

    @staticmethod
    def add_step_update_attributes(grp_multi_step: h5py.Group, q_list: List[str], step_value: float = 0) -> int:
        """
        Add step and update (last) step values and numbers
        :param grp_multi_step:
        :param q_list:
        :param step_value:
        :return: step_num
        """
        # Get Step Numbers and Values from description
        dset_step_numbers = [
            grp_multi_step["ResultDescription/" + q_list[i] + "/StepNumbers"] for i in range(len(q_list))
        ]
        dset_step_values = [
            grp_multi_step["ResultDescription/" + q_list[i] + "/StepValues"] for i in range(len(q_list))
        ]
        # Update Attributes
        step_num = grp_multi_step.attrs["LastStepNum"] + 1
        grp_multi_step.attrs["LastStepNum"] += 1
        grp_multi_step.attrs["LastStepValue"] = step_value
        # Update Result Description
        for dset in dset_step_numbers:
            dset.resize(dset.shape[0] + 1, axis=0)
            dset[dset.shape[0] - 1] = step_num
        for dset in dset_step_values:
            dset.resize(dset.shape[0] + 1, axis=0)
            dset[dset.shape[0] - 1] = step_value

        return step_num

    @staticmethod
    def create_step_result(
        grp_step: h5py.Group,
        quantity: str,
        region: str,
        defined_on: str | cfs_result_type,
        shape: tuple,
        is_complex=False,
        filename_external: str | None = None,
        filename_master: str = "",
        compression_lvl: int = 6,
    ) -> Tuple[List[h5py.Group], h5py.File]:
        """
        Create result in step
        :param grp_step:
        :param quantity:
        :param region:
        :param defined_on:
        :param shape:
        :param is_complex:
        :param filename_external:
        :param filename_master:
        :param compression_lvl:
        :return: dataset object of opened HDF5 file_src, file_src handle of opened HDF5 file_src for external data
        """
        if is_complex:
            result_name = ["Real", "Imag"]
        else:
            result_name = ["Real"]

        if filename_external:
            f_external = CFSWriter.create_external(filename_external, filename_master, grp_step.name)
            grp_data = f_external.require_group(f"{quantity}/{region}/{defined_on}")
        else:
            f_external = None
            grp_data = grp_step.require_group(f"{quantity}/{region}/{defined_on}")

        ds_data = []
        for name in result_name:
            ds_data.append(
                grp_data.require_dataset(
                    name,
                    shape=shape,
                    dtype=np.dtype("float64"),
                    compression="gzip",
                    compression_opts=compression_lvl,
                )
            )

        return ds_data, f_external

    @staticmethod
    def write_step_result(ds_data: h5py.Dataset, data, f_external: h5py.File = None):
        """
        Write step
        :param ds_data:
        :param data:
        :param f_external:
        """
        CFSWriter.write_dataset(ds_data, data.astype(np.float64))

        if f_external:
            f_external.close()

    @staticmethod
    def create_external(filename_external: str, filename_master: str, masterGroup: str) -> h5py.File:
        """
        Create external HDF5 file_src
        :param str filename_external:
        :param str filename_master:
        :param str masterGroup:
        :return: file_src handle of opened HDF5 file_src for external data
        :rtype: h5py.File
        """
        f_external = h5py.File(os.path.join(filename_external, ".h5"), "a")

        f_external.attrs.create("MasterGroup", data=masterGroup, dtype=h5py.special_dtype(vlen=bytes))
        f_external.attrs.create(
            "MasterHDF5FileName",
            data=filename_master,
            dtype=h5py.special_dtype(vlen=bytes),
        )

        return f_external

    def prepare_write_multistep(
        self,
        res_info: List[CFSResultInfo],
        multi_step_id=1,
        analysis_type=cfs_analysis_type.NO_ANALYSIS,
    ):
        """
        Write ResultDescription and create datasets (needs to be done a priori in case of parallel write)
        :param pyCFS.data.io.CFSResultInfo res_info: needs to contain single MultiStep results only!
        :param dict res_shape_dict:
        :param int multi_step_id:
        :param pyCFS.data.io.cfs_types.cfs_analysis_type analysis_type:
        """

        # Create Result
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            grp_result_mesh = CFSWriter.create_result(f["Results"])
            grp_multi_step, grp_result_description = CFSWriter.create_multistep(
                grp_result_mesh, multi_step_id=multi_step_id, analysis_type=analysis_type
            )
            q_set = set()
            for r_info in res_info:
                vprint(
                    f"Initializing result: {r_info}",
                    verbose=self._Verbosity >= v_def.debug,
                )
                if r_info.Quantity is None:
                    raise ValueError(f"Region {r_info.__repr__()} not properly defined!")
                CFSWriter.create_result_description(
                    grp_result_description,
                    r_info.Quantity,
                    dim_names=r_info.DimNames,
                    definedOn=r_info.ResType,
                )
                q_set.add(r_info.Quantity)

            q_list: List[str] = list(q_set)
            # Get Step Values from description
            dset_step_values = [grp_multi_step[f"ResultDescription/{q_list[i]}/StepValues"] for i in range(len(q_list))]
            step_values_overwrite = []
            for step_value in progressbar(
                res_info[0].StepValues,
                "Checking Data for write: ",
                30,
                verbose=self._Verbosity >= v_def.more,
            ):
                # Check if step exists
                if all([step_value in dset for dset in dset_step_values]):
                    step_values_overwrite.append(step_value)
            # Set step values apriori in result description
            CFSWriter.set_step_attributes(grp_multi_step, q_list, step_values=res_info[0].StepValues)
            # counter = 0
            for step_idx in progressbar(
                range(len(res_info[0].StepValues)),
                prefix="Creating Step: ",
                size=40,
                verbose=self._Verbosity >= v_def.more,
            ):
                # for step_value in progressbar(res_info[0].StepValues, f"Creating Step: ", 40,
                #                               verbose=self._Verbosity >= v_def.debug):
                # counter += 1
                # vprint(f'Creating Step {counter} (Step Value: {float(step_value)})', verbose=self._Verbosity >= v_def.debug)

                step_num = step_idx + 1
                step_value = res_info[0].StepValues[step_idx]
                if step_value in step_values_overwrite:
                    step_num = int(np.where(np.array(dset_step_values[0]) == step_value)[0].item() + 1)
                    grp_stp = grp_multi_step[f"Step_{step_num}"]
                else:
                    # grp_stp = CFSWriter.create_step_add(grp_multi_step, q_list, step_value=step_value)
                    grp_stp = CFSWriter.create_step(grp_multi_step, step_value=step_value, step_num=step_num)
                for r_info in res_info:
                    if r_info.Quantity is None or r_info.Region is None:
                        raise ValueError(f"Region {r_info.__repr__()} not properly defined!")
                    CFSWriter.create_step_result(
                        grp_stp,
                        r_info.Quantity,
                        r_info.Region,
                        r_info.ResType,
                        r_info.DataShape[1:],
                        is_complex=r_info.IsComplex,
                        compression_lvl=self.CompressionLvl,
                    )

    def perform_write_multistep(self, result_data: CFSResultData, multi_step_id: int | None = None):
        """
        Write data to MultiStep
        :param pyCFS.data.io.CFSResultData result_data:
        """
        if multi_step_id is None:
            multi_step_id = result_data.MultiStepID
        with h5py.File(self._filename, "r+", driver=self._h5driver) as f:
            for stepnum in progressbar(
                range(len(result_data.StepValues)),
                "Writing Step:  ",
                40,
                verbose=self._Verbosity >= v_def.release,
            ):
                # for stepnum in range(len(result_data_read.StepValues)):
                #     vprint(f'Writing Step {stepnum + 1}', verbose=self._Verbosity >= v_def.debug)
                for data in result_data.Data:
                    q_name = data.Quantity
                    reg = data.Region
                    res_type = data.ResType
                    dname = "Real"
                    data_write = data[stepnum, :, :].real
                    # noinspection LongLine
                    dset = f[
                        f"Results/Mesh/MultiStep_{multi_step_id}/Step_{stepnum + 1}/{q_name}/{reg}/{res_type}/{dname}"
                    ]

                    CFSWriter.write_step_result(dset, data_write)

                    if data.IsComplex:
                        dname = "Imag"
                        data_write = data[stepnum, :, :].imag
                        # noinspection LongLine
                        dset = f[
                            f"Results/Mesh/MultiStep_{multi_step_id}/Step_{stepnum + 1}/{q_name}/{reg}/{res_type}/{dname}"
                        ]

                        CFSWriter.write_step_result(dset, data_write)

    def finalize_write_multistep(self, res_info: List[CFSResultInfo], multi_step_id=1):
        """
        Write datasets to ResultsDescription that need to be written after the data (in case of parallel write)
        :param res_info:
        :param multi_step_id:
        """
        reg_dict: Dict[str, List[str]] = dict()
        dim_names_dict: Dict[str, List[str]] = dict()
        for r_info in res_info:
            if r_info.Quantity is None or r_info.Region is None:
                raise ValueError(f"Region {r_info.__repr__()} not properly defined!")
            if r_info.Quantity in reg_dict:
                reg_dict[r_info.Quantity].append(r_info.Region)
                if r_info.DimNames != dim_names_dict[r_info.Quantity]:
                    raise Exception("Dimension labels of single quantity must be the same for all result arrays!")
            else:
                reg_dict[r_info.Quantity] = [r_info.Region]
                dim_names_dict[r_info.Quantity] = r_info.DimNames

        with h5py.File(self._filename, "r+") as f:
            for q_name in reg_dict:
                vprint(
                    f"Finalizing result: {q_name}",
                    verbose=self._Verbosity >= v_def.debug,
                )
                CFSWriter.finalize_result_description(
                    f[f"Results/Mesh/MultiStep_{multi_step_id}/ResultDescription/{q_name}"],
                    reg_dict[q_name],
                    dim_names_dict[q_name],
                )

    def write_multistep(self, result_data: CFSResultData, multi_step_id: int | None = None):
        """
        Write ResultDescription and create datasets, write data to multistep and write datasets to ResultsDescription
        that need to be written after the data (in case of parallel write)

        Parameters
        ----------
        result_data : pyCFS.data.io.CFSResultData
        multi_step_id : int, optional

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader, CFSWriter
        >>> with CFSReader('file.cfs') as f:
        >>>     results = f.MultiStepData
        >>> with CFSWriter('file.cfs') as f:
        >>>     f.write_multistep(result_data=results)

        """
        if multi_step_id is None:
            multi_step_id = result_data.MultiStepID
        self.prepare_write_multistep(
            res_info=result_data.ResultInfo, multi_step_id=multi_step_id, analysis_type=result_data.AnalysisType
        )
        self.perform_write_multistep(result_data=result_data, multi_step_id=multi_step_id)
        self.finalize_write_multistep(res_info=result_data.ResultInfo, multi_step_id=multi_step_id)

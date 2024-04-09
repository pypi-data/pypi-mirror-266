"""
Module containing data processing utilities for writing HDF5 files in openCFS format
"""

from __future__ import annotations

import textwrap

import numpy as np
from typing import List, Dict

from pyCFS.data.io.CFSArray import CFSResultArray, CFSResultInfo
from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type
from pyCFS.data.util import progressbar, vprint

from pyCFS.data import v_def


# noinspection PyAttributeOutsideInit
class CFSResultData:
    """
    Data structure containing result data (one object supports currently a single MultiStep only!)

    Parameters
    ----------
    analysis_type : pyCFS.data.io.cfs_types.cfs_analysis_type, optional
        Analysis type. Definitions based on pyCFS.data.io.cfs_types.cfs_analysis_type. The default is ``NO_ANALYSIS``.
    multi_step_id : int, optional
        MultiStep (also known as SequenceStep) ID. The default value is ``1``.
    data : list[pyCFS.data.io.CFSResultArray], optional
        List of result arrays. The default is ``None`` in which case the result data object will be initialized empty.
    verbosity : int, optional
        Verbosity level <=1000 ; see v_def.py for predefined levels. Default is v_def.release.

    Examples
    --------
    >>> import numpy
    >>> from pyCFS.data.io import CFSResultArray, CFSResultData
    >>> from pyCFS.data.io.cfs_types import cfs_result_type
    >>> data = numpy.array([0,1,2,3])
    >>> result_array = CFSResultArray(data,quantity='quantity_name', region='region_name', step_value=0,
    >>>                               dim_names=['-'], defined_on=cfs_result_type.NODE, is_complex=True)
    >>> result_data = CFSResultData(AnalysisType=cfs_analysis_type.STATIC,multi_step_id=2,data=[result_array])

    """

    def __init__(
        self,
        analysis_type=cfs_analysis_type.NO_ANALYSIS,
        multi_step_id=1,
        data: List[CFSResultArray] | None = None,
        verbosity=v_def.release,
    ):
        self._Verbosity = verbosity
        self._AnalysisType = cfs_analysis_type.NO_ANALYSIS
        self._MultiStepID = 1
        self.Data: List[CFSResultArray] = []  # List of Result Data Arrays
        if data is not None:
            if isinstance(data, list):
                for item in data:
                    self.add_data_array(item)
            else:
                raise TypeError("'data' must be a list of CFSResultArray objects!")
        self.AnalysisType = analysis_type
        self.MultiStepID = multi_step_id

    def __repr__(self) -> str:
        return f"""MultiStep {self.MultiStepID}: {self.AnalysisType}, {self.StepValues.size} steps"""

    # noinspection PyArgumentList
    def __str__(self) -> str:
        info_str = str().join([str(ri) for ri in self.ResultInfo])
        return textwrap.dedent(
            f"""\
        MultiStep {self.MultiStepID}: {self.AnalysisType}, {self.StepValues.size} steps
        {info_str}"""
        )

    def __getitem__(self, index: int | slice) -> CFSResultData:
        """
        Extract steps from a CFSResultData object.

        Parameters
        ----------
        index : int | slice
            Indices to extract from CFSResultData object.

        Returns
        -------
        pyCFS.data.io.CFSResultData
            Extracted CFSResultData object.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     result_data = f.MultiStepData
        >>> result_data_extract = result_data[0:2]

        """
        result_data = CFSResultData(self.AnalysisType, self.MultiStepID, verbosity=self._Verbosity)

        # if isinstance(index, slice):
        for data_array in self.Data:
            result_data.add_data_array(data_array[index, :, :], step_values=data_array.StepValues[index])

        return result_data

    def __add__(self, other: CFSResultData) -> CFSResultData:
        return self.combine_with(other, resolve_match="add")

    def __eq__(self, other) -> bool:
        if not isinstance(other, CFSResultData):
            return False

        data_equality = len(self.Data) == len(other.Data)
        for i in range(len(self.Data)):
            if data_equality:
                if self.ResultInfo[i] in other.ResultInfo:
                    idx_other = other.ResultInfo.index(self.ResultInfo[i])
                    data_equality = np.array_equal(self.Data[i], other.Data[idx_other])
                else:
                    return False
            else:
                return False

        return all(
            [
                data_equality,
                self.AnalysisType == other.AnalysisType,
                self.MultiStepID == other.MultiStepID,
            ]
        )

    @property
    def MultiStepID(self) -> int:
        """
        MultiStep ID (CFSResultData can contain data from only one MultiStep currently!)
        """
        return self._MultiStepID
        # if self.ResultInfo:
        #     id_collection = [r_info.MultiStepID for r_info in self.ResultInfo]
        #     return set(id_collection)

    @MultiStepID.setter
    def MultiStepID(self, multi_step_id: int):
        self._MultiStepID = multi_step_id
        for r_array in self.Data:
            r_array.MultiStepID = multi_step_id

    @property
    def AnalysisType(self) -> cfs_analysis_type:
        """
        Analysis type of MultiStepData (CFSResultData can contain data from only one MultiStep currently!)
        """
        return self._AnalysisType
        # if self.ResultInfo:
        #     analysis_type_collection = [r_info.AnalysisType for r_info in self.ResultInfo]
        #     return set(analysis_type_collection)

    @AnalysisType.setter
    def AnalysisType(self, analysis_type: cfs_analysis_type):
        self._AnalysisType = analysis_type
        for r_info in self.ResultInfo:
            r_info.AnalysisType = analysis_type

    @property
    def ResultInfo(self) -> List[CFSResultInfo]:
        """
        Structure containing information about the corresponding CFSResultArray object in self.Data

        Returns
        -------
        list[CFSResultInfo]
            List of CFSResultInfo objects corresponding to list of CFSResultArray objects in self.Data
        """
        result_info = []
        if self.Data:
            for r_array in self.Data:
                result_info.append(r_array.ResultInfo)

        return result_info

    @property
    def StepValues(self) -> np.ndarray:
        """
        Step Values of MultiStep property. All data sets of one MultiStep must have the same
        step values currently!
        """
        return self.get_multi_step_step_values(multi_step_id=self.MultiStepID)

    @StepValues.setter
    def StepValues(self, step_values: np.ndarray | List[float]):
        self.set_multi_step_step_values(step_values)

    def get_multi_step_step_values(self, multi_step_id=1) -> np.ndarray:
        for item in self.Data:
            if item.MultiStepID == multi_step_id:
                return item.StepValues
        return np.empty(0)

    def set_multi_step_step_values(self, step_values: np.ndarray | List[float], multi_step_id=1):
        for item in self.Data:
            if item.MultiStepID == multi_step_id:
                item.StepValues = np.array(step_values)

    def set_multi_step_analysis_type(self, analysis_type: cfs_analysis_type, multi_step_id=1):
        vprint(
            f"Setting AnalysisType {self.AnalysisType} -> {analysis_type}",
            verbose=self._Verbosity >= v_def.debug,
        )
        self.AnalysisType = analysis_type
        for item in self.Data:
            if item.MultiStepID == multi_step_id:
                item.AnalysisType = analysis_type

    def extract_quantity_region(
        self,
        quantity: str,
        region: str,
        restype: cfs_result_type | None = None,
        data_ids: np.ndarray | None = None,
    ) -> CFSResultData:
        """
        Return CFSResult of extracted quantity and region. Processes all time steps. Extract node/element data of
        given data_ids.

        Parameters
        ----------
        quantity : str
            Name of the result quantity.
        region : str
            Name of the region on which the result is defined.
        restype : pyCFS.data.io.cfs_types.cfs_result_type, optional
            Type of the result data. The default is ``None`` in which case the result type is identified automatically.
            Only works, if there are not multiple result types specified.
        data_ids : numpy.ndarray, optional
            Array of data ids to extract (starting from 0).

        Returns
        -------
        pyCFS.data.io.CFSResultData
            Extracted CFSResultData object.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     result_data = f.MultiStepData
        >>> extract_ids = np.array([0,1,2,3])
        >>> result_data_extract = result_data.extract_quantity_region(quantity='quantity', region='region',
        >>>                       data_ids=extract_ids)

        """
        data_array = self.get_data_array(quantity, region, restype=restype)
        if data_ids is None:
            data_array_extract = data_array
        else:
            data_array_extract = data_array[:, data_ids, :]  # type: ignore[assignment]

        return CFSResultData(
            analysis_type=self.AnalysisType,
            multi_step_id=self.MultiStepID,
            data=[data_array_extract],
            verbosity=self._Verbosity,
        )

    def get_data_array(self, quantity: str, region: str, restype: cfs_result_type | None = None) -> CFSResultArray:
        """
        Return list of CFSResultArrays for certain quantity and region.

        Parameters
        ----------
        quantity : str
            Name of the result quantity.
        region : str
            Name of the region on which the result is defined.
        restype : pyCFS.data.io.cfs_types.cfs_result_type, optional
            Type of the result data. The default is ``None`` in which case the result type is identified automatically.
            Only works, if there are not multiple result types specified.

        Returns
        -------
        pyCFS.data.io.CFSResultArray
            Extracted result data arrays.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     result_data = f.MultiStepData
        >>> result_array = result_data.get_data_array(quantity='quantity', region='region')

        """
        for item in progressbar(self.Data, "Get data array: ", verbose=self._Verbosity >= v_def.debug):
            if quantity == item.Quantity and region == item.Region:
                if restype is None or restype == item.ResType:
                    return item
        raise LookupError(f"Could not find result data array for ({quantity}, {region})")

    def combine_with(self, other: CFSResultData, resolve_match="exception") -> CFSResultData:
        """
        Merges result data structures
        param: resolve_match= 'exception' raises exception on matching datasets
                              'add'       adds datasets on matching datasets
        """
        for array_idx, r_data in enumerate(other.Data):
            if r_data.Quantity is None or r_data.Region is None:
                raise ValueError(f"MetaData {r_data.MetaData} of result not properly defined!")
            # Check if dataset alread exists
            try:
                r_data_match = self.get_data_array(
                    quantity=r_data.Quantity, region=r_data.Region, restype=r_data.ResType
                )
            except LookupError:
                self.add_data_array(data=r_data)
            else:
                if resolve_match == "add":
                    r_data_match += r_data  # type: ignore[misc]
                else:
                    raise Exception("Region already exists")
        return self

    def add_data_array(
        self,
        data: CFSResultArray | np.ndarray,
        *,
        step_values: np.ndarray = np.empty(0),
        quantity: str | None = None,
        region: str | None = None,
        restype: cfs_result_type | None = None,
        dim_names: List[str] | None = None,
        is_complex: bool | None = None,
        multi_step_id: int | None = None,
        analysis_type: cfs_analysis_type | None = None,
        meta_data: Dict | None = None,
    ):
        """
        Add data using CFSResultArray or np.ndarray in combination with meta_data

        Parameters
        ----------
        data : np.ndarray | CFSResultArray
            data to be added. Supported shapes: (n, m, d) or (n,m)
        step_values : np.ndarray | list[float], optional, kwarg
            step values to overwrite from MetaData
        quantity : str, optional, kwarg
            name of data quantity to overwrite from MetaData
        region : str, optional, kwarg
            region on which data is added to overwrite from MetaData
        restype : cfs_result_type, optional, kwarg
            result type based on cfs_result_type to overwrite from MetaData
        dim_names : list[str], optional, kwarg
            list of DIM labels to overwrite from MetaData
        is_complex : bool, optional, kwarg
            flag wheter added data is real or complex, to overwrite from MetaData
        multi_step_id : int, optional, kwarg
            MultiStep ID to overwrite from MetaData
        analysis_type : cfs_types.cfs_analysis_type, optional, kwarg
            AnalyisType to overwrite from MetaData
        meta_data : dict , optional, kwarg
            meta_data dictionary. Must contain keys:
            'Quantity','Region','StepValues','DimNames','ResType','IsComplex','MultiStepID','AnalysisType'

        Examples
        ---
        >>> import numpy as np
        >>> from pyCFS.data.io import CFSResultData
        >>> from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type
        >>> result = CFSResultData()
        >>> data = CFSResultArray(np.ones((5,3,1)))
        >>> data.set_meta_data(quantity='Quantity', region='Region', step_values=np.array([0,1,2,3,4],dtype=float),
        >>>              dim_names=['-'], res_type=cfs_result_type.NODE, is_complex=False,
        >>>              multi_step_id=1, analysis_type=cfs_analysis_type.TRANSIENT)
        >>> result.add_data_array(data)

        """
        if not isinstance(data, CFSResultArray):
            if isinstance(data, np.ndarray):
                if meta_data is None:
                    raise ValueError(
                        "Provide either a CFSResultArray object or meta_data dict in combination with numpy.ndarray"
                    )
                else:
                    data = CFSResultArray(data)
            else:
                raise TypeError("Provide either a CFSResultArray object or numpy.ndarray.")
        if meta_data is not None:
            data.MetaData = meta_data
        if step_values.size == 0:
            step_values = data.StepValues
        if quantity is None:
            if data.Quantity is None:
                raise ValueError("Quantity name cannot be extacted from provided CFSResultArray")
            quantity = data.Quantity
        if region is None:
            if data.Region is None:
                raise ValueError("Quantity name cannot be extacted from provided CFSResultArray")
            region = data.Region
        if restype is None:
            restype = data.ResType
        if dim_names is None:
            dim_names = data.DimNames
        if is_complex is None:
            is_complex = data.IsComplex
        if multi_step_id is None:
            multi_step_id = data.MultiStepID
        if analysis_type is None:
            analysis_type = data.AnalysisType

        self.add_data(
            data=data,
            step_values=step_values,
            quantity=quantity,
            region=region,
            restype=restype,
            dim_names=dim_names,
            is_complex=is_complex,
            multi_step_id=multi_step_id,
            analysis_type=analysis_type,
        )

    # noinspection PyPep8Naming
    def add_data(
        self,
        data: np.ndarray,
        *,
        step_values: np.ndarray,
        quantity: str,
        region: str,
        restype: cfs_result_type,
        dim_names: List[str] | None = None,
        is_complex: bool | None = None,
        multi_step_id: int | None = None,
        analysis_type: cfs_analysis_type | None = None,
    ):
        """
        Add data to CFSResultData object

        Parameters
        ----------
        data : np.ndarray
            data to be added. Supported shapes: (n, m, d) or (n,m)
        step_values : np.ndarray, kwarg
            step values (needs to match old data)
        quantity : str, kwarg
            name of data quantity
        region : str, kwarg
            region on which data is added
        restype : cfs_result_type, kwarg
            result type based on cfs_result_type
        dim_names : list[str], optional, kwarg
            list of DIM labels
        is_complex : bool, optional, kwarg
            flag wheter added data is real or complex, determine automatically if None (can yield real results if
            complex numpy array has zero imaginary part)
        multi_step_id : int, optional, kwarg
            MultiStep ID, if not specified retrieve from CFSResultData parent object
        analysis_type : cfs_types.cfs_analysis_type, optional, kwarg
            AnalyisType, if not specified retrieve from CFSResultData parent object

        Examples
        ---
        >>> import numpy as np
        >>> from pyCFS.data.io import CFSResultData
        >>> from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type
        >>> result = CFSResultData()
        >>> data = np.ones((5,3,1))
        >>> result.add_data(data, step_values=np.array([0,1,2,3,4],dtype=float), quantity='Quantity', region='Region',
        >>>                 dim_names=['-'], res_type=cfs_result_type.NODE, is_complex=False, multi_step_id=1,
        >>>                 analysis_type=cfs_analysis_type.TRANSIENT)

        """
        # Check MultiStepID
        if multi_step_id is None:
            multi_step_id = self.MultiStepID

        # Check if result info already exists
        if self._get_result_info(multi_step_id, quantity, region, restype):
            raise Exception("Result already exists. Overwriting result currently not supported!")

        # Check if result info is consistent
        if self._get_result_info(multi_step_id):
            vprint(
                f"Adding data to existing MultiStep {multi_step_id}",
                verbose=self._Verbosity >= v_def.debug,
            )

            # Check StepValues
            if not np.array_equal(step_values, self.get_multi_step_step_values(multi_step_id)):
                raise Exception("Step values of added data do not match step values of existing multi step data.")

        # Reshape scalar data to format (n,m,1)
        if data.ndim == 2:
            data = data.reshape(data.shape[0], data.shape[1], 1)

        # Check analysis type
        if analysis_type is None:
            analysis_type = self.AnalysisType
        elif analysis_type != self.AnalysisType:
            self.set_multi_step_analysis_type(analysis_type=analysis_type, multi_step_id=multi_step_id)

        # Check DIM labels
        if dim_names is None:
            if data.ndim == 2 or data.shape[2] == 1:
                dim_names = ["-"]
            else:
                dim_names = [f"dim_{i}" for i in range(data.shape[2])]
        if len(dim_names) != data.shape[2]:
            raise Exception("Dimension of data does not match specified number of DIM labels")

        # Check for complex data
        if is_complex is None:
            is_complex = bool(np.any(np.iscomplex(data)))

        self.Data.append(
            CFSResultArray(
                data,
                quantity=quantity,
                region=region,
                step_values=step_values,
                dim_names=dim_names,
                res_type=restype,
                is_complex=is_complex,
                multi_step_id=multi_step_id,
                analysis_type=analysis_type,
            )
        )

    def sort_steps(self, return_idx=False) -> None | np.ndarray:
        """
        Sort data arrays by increasing step values.

        Returns
        -------
        np.ndarray
            index array used for sorting.
        """
        idx_sort = np.argsort(self.StepValues)
        for item in self.Data:
            item[:] = item[idx_sort, :, :]
            item.StepValues[:].sort()

        if return_idx:
            return idx_sort
        else:
            return None

    def _get_result_info(
        self,
        multi_step_id=1,
        quantity: str | None = None,
        region: str | None = None,
        res_type: cfs_result_type | None = None,
    ) -> List[CFSResultInfo]:
        result_info_list = []
        for r_data in self.Data:
            if r_data.MultiStepID == multi_step_id:
                if quantity is None or r_data.Quantity == quantity:
                    if region is None or r_data.Region == region:
                        if res_type is None or r_data.ResType == res_type:
                            result_info_list.append(r_data.ResultInfo)

        return result_info_list

"""
Module containing view on numpy node array with additional meta data.
"""

from __future__ import annotations

import numpy as np
from typing import List, Dict

from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type


class CFSResultArray(np.ndarray):
    # TODO: fix getitem to hint correct type
    # noinspection PyUnresolvedReferences
    """
    Overload/Subclass of numpy.ndarray <https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html>`_
    adding attributes according to CFS HDF5 result data structure.

    Parameters
    ----------
    input_array : array_like
        Input data, in any form that can be converted to an array.  This
        includes lists, lists of tuples, tuples, tuples of tuples, tuples
        of lists and ndarrays.
    quantity : str, optional
        Name of the quantity. The default is ``None``.
    region : str, optional
        Name of the region on which the result array is defined.
    step_values : np.ndarray, optional
        Step values (e.g. time stamps). The default is ``None``.
    dim_names : list[str], optional
        List of dimension labels. The default is ``None``.
    defined_on : pyCFS.data.io.cfs_types.cfs_result_type, optional
        Enum indicating entity on which the result array is defined on. The default is ``None``.
    is_complex : bool, optional
        Flag if the mesh entity is a group or region instead. The default is ``False``.

    Examples
    --------
    >>> from pyCFS.data.io import CFSResultArray
    >>> from pyCFS.data.io.cfs_types import cfs_result_type
    >>> data = [0,1,2,3]
    >>> result_array = CFSResultArray(data,quantity='quantity_name', region='region_name', step_value=0,
    >>>                               dim_names=['-'], res_type=cfs_result_type.NODE, is_complex=True,
    >>>                               multi_step_id=2, AnalysisType=cfs_analysis_type.STATIC)

    """

    def __new__(
        cls,
        input_array,
        quantity: str | None = None,
        region: str | None = None,
        step_values: np.ndarray | None = None,
        dim_names: List[str] | None = None,
        res_type: cfs_result_type = cfs_result_type.UNDEFINED,
        is_complex=False,
        multi_step_id=1,
        analysis_type=cfs_analysis_type.NO_ANALYSIS,
    ):
        # Input array is an already formed ndarray instance
        # Cast to be our class type
        obj = np.asarray(input_array).view(cls)

        if step_values is None:
            step_values = np.empty(0)
        if dim_names is None:
            dim_names = ["-"]
        # Add attributes
        obj.Quantity = quantity
        obj.Region = region
        obj.StepValues = step_values
        obj.DimNames = dim_names
        obj.ResType = res_type
        obj.IsComplex = is_complex
        obj.MultiStepID = multi_step_id
        obj.AnalysisType = analysis_type

        return obj

    def __array_finalize__(self, obj, **kwargs):
        # ``self`` is a new object resulting from
        # ndarray.__new__(InfoArray, ...), therefore it only has
        # attributes that the ndarray.__new__ constructor gave it -
        # i.e. those of a standard ndarray.
        if obj is None:
            return
        # Note that it is here, rather than in the __new__ method,
        # that we set the default value for 'info', because this
        # method sees all creation of default objects - with the
        # InfoArray.__new__ constructor, but also with
        # arr.view(InfoArray).
        self.Quantity = getattr(obj, "Quantity", None)
        self.Region = getattr(obj, "Region", None)
        self.StepValues = getattr(obj, "StepValues", np.empty(0))
        self.DimNames = getattr(obj, "DimNames", ["-"])
        self.ResType = getattr(obj, "ResType", cfs_result_type.UNDEFINED)
        self.IsComplex = getattr(obj, "IsComplex", False)
        self.MultiStepID = getattr(obj, "MultiStepID", 1)
        self.AnalysisType = getattr(obj, "AnalysisType", cfs_analysis_type.NO_ANALYSIS)

    @property
    def ResultInfo(self) -> CFSResultInfo:
        return CFSResultInfo(
            quantity=self.Quantity,
            region=self.Region,
            res_type=self.ResType,
            dim_names=self.DimNames,
            step_values=self.StepValues,
            is_complex=self.IsComplex,
            multi_step_id=self.MultiStepID,
            analysis_type=self.AnalysisType,
            data_shape=self.shape,
        )

    # noinspection LongLine
    @property
    def MetaData(self) -> Dict:
        """return CFS meta data"""
        return {
            "Quantity": self.Quantity,
            "Region": self.Region,
            "StepValues": self.StepValues,
            "DimNames": self.DimNames,
            "ResType": self.ResType,
            "IsComplex": self.IsComplex,
            "MultiStepID": self.MultiStepID,
            "AnalysisType": self.AnalysisType,
            "DataShape": self.shape,
        }

    @MetaData.setter
    def MetaData(self, meta_data: Dict):
        """Set CFS meta data"""
        if all(
            key in meta_data
            for key in (
                "Quantity",
                "Region",
                "StepValues",
                "DimNames",
                "ResType",
                "IsComplex",
                "MultiStepID",
                "AnalysisType",
            )
        ):
            self.Quantity = meta_data["Quantity"]
            self.Region = meta_data["Region"]
            self.StepValues = meta_data["StepValues"]
            self.DimNames = meta_data["DimNames"]
            self.ResType = meta_data["ResType"]
            self.IsComplex = meta_data["IsComplex"]
            self.MultiStepID = meta_data["MultiStepID"]
            self.AnalysisType = meta_data["AnalysisType"]
        else:
            # noinspection LongLine
            raise ValueError(
                "meta_data dictionary must contain keys: 'Quantity','Region','StepValues','DimNames','ResType','IsComplex','MultiStepID','AnalysisType'"
            )

    @property
    def DataArray(self) -> np.ndarray:
        """return array as numpy ndarray"""
        if self.ndim == 3 and self.shape[2] == 1:
            return np.squeeze(np.array(self), axis=2)
        else:
            return np.array(self)

    def set_meta_data(
        self,
        quantity: str | None = None,
        region: str | None = None,
        step_values: np.ndarray | None = None,
        dim_names: List[str] | None = None,
        res_type: cfs_result_type | None = None,
        is_complex: bool | None = None,
        multi_step_id: int | None = None,
        analysis_type: cfs_analysis_type | None = None,
    ):
        """Set metadata"""
        if quantity is not None:
            self.Quantity = quantity
        if region is not None:
            self.Region = region
        if step_values is not None:
            self.StepValues = step_values
        if dim_names is not None:
            self.DimNames = dim_names
        if res_type is not None:
            self.ResType = res_type
        if is_complex is not None:
            self.IsComplex = is_complex
        if multi_step_id is not None:
            self.MultiStepID = multi_step_id
        if analysis_type is not None:
            self.AnalysisType = analysis_type


class CFSResultInfo:
    """
    Data structure containing result information for one result
    """

    def __init__(
        self,
        quantity: str | None = None,
        region: str | None = None,
        res_type=cfs_result_type.UNDEFINED,
        dim_names: List[str] | None = None,
        step_values: np.ndarray | None = None,
        is_complex=False,
        multi_step_id=1,
        analysis_type=cfs_analysis_type.NO_ANALYSIS,
        data_shape: tuple = (),
    ) -> None:

        if step_values is None:
            step_values = np.empty(0)
        if dim_names is None:
            dim_names = ["-"]

        self.Quantity = quantity
        self.Region = region
        self.ResType = res_type
        self.DimNames = dim_names
        self.StepValues = step_values
        self.IsComplex = is_complex
        self.MultiStepID = multi_step_id
        self.AnalysisType = analysis_type
        self.DataShape = data_shape

    @classmethod
    def from_meta_data(cls, meta_data: Dict):
        return cls(
            quantity=meta_data["Quantity"],
            region=meta_data["Region"],
            res_type=meta_data["ResType"],
            dim_names=meta_data["DimNames"],
            step_values=meta_data["StepValues"],
            is_complex=meta_data["IsComplex"],
            multi_step_id=meta_data["MultiStepID"],
            analysis_type=meta_data["AnalysisType"],
            data_shape=meta_data["DataShape"],
        )

    @property
    def MetaData(self) -> Dict:
        return {
            "Quantity": self.Quantity,
            "Region": self.Region,
            "StepValues": self.StepValues,
            "DimNames": self.DimNames,
            "ResType": self.ResType,
            "IsComplex": self.IsComplex,
            "MultiStepID": self.MultiStepID,
            "AnalysisType": self.AnalysisType,
            "DataShape": self.DataShape,
        }

    def __eq__(self, other: object | str) -> bool:
        if isinstance(other, str):
            return self.Quantity == other
        if isinstance(other, CFSResultInfo):
            return self.Quantity == other.Quantity and self.Region == other.Region and self.ResType == other.ResType
        else:
            raise Exception(f"Comparison for types {type(self)} - {type(other)} not implemented")

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        complex_str = {0: "real", 1: "complex"}
        return f"{self.Quantity} ({complex_str[self.IsComplex]}) defined in {self.Region} on {self.ResType}"

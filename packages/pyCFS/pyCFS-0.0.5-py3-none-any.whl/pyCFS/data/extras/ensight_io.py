from __future__ import annotations

import os
import vtk
from typing import List, Dict, Tuple

# noinspection PyUnresolvedReferences
from vtk.util import numpy_support as vtk_numpy
import numpy as np

from pyCFS.data import io, v_def
from pyCFS.data.io import cfs_types
from pyCFS.data.util import progressbar, connectivity_list_to_matrix
from pyCFS.data.extras.vtk_to_cfs_element_types import vtk_to_cfs_elem_type


def ensightInitReader(file: str) -> vtk.vtkEnSightGoldBinaryReader:
    """
    Initializes an EnSight reader object with the specified filename and filepath.

    This function creates an instance of the class vtkEnSightGoldBinaryReader and sets the
    case file name and path for reading EnSight files. The reader object is then updated.

    Args:
        file (str): Path to the EnSight case file.

    Returns:
        vtk.vtkEnSightGoldBinaryReader: The initialized EnSight reader object.

    """

    filepath, filename = os.path.split(file)
    if filepath == "":
        filepath = "../ensight/"
    reader = vtk.vtkEnSightGoldBinaryReader()
    reader.SetCaseFileName(filename)
    reader.SetFilePath(filepath)
    reader.Update()

    return reader


def ensightGetInfo(reader: vtk.vtkEnSightGoldBinaryReader) -> Dict:
    """
    Retrieves information about the EnSight file using the provided reader object.

    This function extracts the names and data types of cell and point arrays in the EnSight file.
    It also retrieves the number of time steps, the time range and generates an array with the time
    steps. Every time a Cell/Point Array is found, its name is printed. Finally, the function returns
    a dictionary with the following keys:
     - 'fieldNames' (list): List of field names (meaning cell and point arrays).
     - 'fieldDataTypes' (list): List of field data types (types: 'Cell' or 'Point').
     - 'numSteps' (int): Number of time steps.
     - 'timeRange' (tuple): start and end point of the time values.
     - 'timeSteps' (numpy array) : one-dimensional array of time steps.

    Args:
    -----
        reader (vtk.vtkEnSightGoldBinaryReader): The EnSight reader object.

    Returns:
    --------
        dict: A dictionary containing the retrieved information.

    """

    field_name_list = []
    field_data_type_list = []

    # append names and types of all Cell/Point Arrays to field_name_list and field_data_type_list
    for j in range(reader.GetNumberOfCellArrays()):
        q = reader.GetCellArrayName(j)
        print(f"Found Cell array: {q}")
        field_name_list.append(q)
        field_data_type_list.append("Cell")
    for j in range(reader.GetNumberOfPointArrays()):
        q = reader.GetPointArrayName(j)
        print(f"Found Point array: {q}")
        field_name_list.append(q)
        field_data_type_list.append("Point")

    # retrieve information about the time steps and create an array time_steps
    time_numsteps = reader.GetTimeSets().GetItem(0).GetNumberOfValues()
    time_range = reader.GetTimeSets().GetItem(0).GetRange(0)
    time_steps = np.linspace(time_range[0], time_range[1], num=time_numsteps)

    return {
        "fieldNames": field_name_list,
        "fieldDataTypes": field_data_type_list,
        "numSteps": time_numsteps,
        "timeRange": time_range,
        "timeSteps": time_steps,
    }


def ensightReadMesh(
    reader: vtk.vtkEnSightGoldBinaryReader,
    block: int = 0,
    processes: int | None = None,
    verbosity=v_def.release,
) -> Dict:
    """
    Retrieves mesh data from an EnSight reader for the specified block.

    This function retrieves information about the mesh, including node Coordinates, Connectivity,
    element types, the number of certain element types and the number of nodes.

    It returns a dictionary with the following keys:
     - 'Coordinates' (numpy array): An array with the node Coordinates.
     - 'Connectivity' (numpy array): A 2D array containing the Connectivity information, where
        each row corresponds to a cell and the columns represent the nodes connected to that cell.
     - 'types' (numpy array): A 1D array containing the element types of the field.
     - 'num_grid' (dict): A dictionary containing information about the number of certain element
        types and the number of nodes.

    Args:
        reader (vtk.vtkEnSightGoldBinaryReader): The EnSight reader object.
        block (int): The index of the block to read from the EnSight file. Defaults to 0.
        processes (int): Number of parallel processes for Connectivity build up.
        verbosity (int): Verbosity level

    Returns:
        dict: A dictionary containing the retrieved information.

    """

    data = reader.GetOutput()

    bdata = data.GetBlock(block)

    points = bdata.GetPoints()
    cells = bdata.GetCells()

    coord = points.GetData()
    connectivity = cells.GetConnectivityArray()
    offsets = cells.GetOffsetsArray()

    # convert vtk data objects to numpy arrays
    numpy_coord = vtk_numpy.vtk_to_numpy(coord)
    numpy_connectivity_list = vtk_numpy.vtk_to_numpy(connectivity)
    numpy_offsets = vtk_numpy.vtk_to_numpy(offsets)

    # put Connectivity data into a 2D numpy array where each row contains the Connectivity data of one cell
    numpy_connectivity = connectivity_list_to_matrix(
        connectivity_list=numpy_connectivity_list,
        offsets=numpy_offsets,
        processes=processes,
        verbose=verbosity >= v_def.debug,
    )

    # correct indexing in CFS starts with 1
    numpy_connectivity += 1

    # list of vtk element types
    numpy_elem_type = vtk_numpy.vtk_to_numpy(data.GetBlock(block).GetCellTypesArray())

    # convert vtk element types codes to a common format for cfs indexing
    numpy_elem_type_cfs = vtk_to_cfs_elem_type(numpy_elem_type)

    # count number of each element type in class cfs_element_type and add number to dictionary
    num_grid = {}
    for elemType in cfs_types.cfs_element_type:
        num_grid["Num_" + elemType.name] = np.count_nonzero(numpy_elem_type_cfs == elemType.value)

    # add number of elements (of different dimensions) and total number of nodes to the dictionary
    num_grid["NumElems"] = len(numpy_elem_type_cfs)
    num_grid["Num1DElems"] = num_grid["Num_LINE2"] + num_grid["Num_LINE3"]
    num_grid["Num2DElems"] = (
        num_grid["Num_TRIA3"]
        + num_grid["Num_TRIA6"]
        + num_grid["Num_QUAD4"]
        + num_grid["Num_QUAD8"]
        + num_grid["Num_QUAD9"]
        + num_grid["Num_POLYGON"]
    )
    num_grid["Num3DElems"] = (
        num_grid["Num_TET4"]
        + num_grid["Num_TET10"]
        + num_grid["Num_HEXA8"]
        + num_grid["Num_HEXA20"]
        + num_grid["Num_HEXA27"]
        + num_grid["Num_PYRA5"]
        + num_grid["Num_PYRA13"]
        + num_grid["Num_PYRA14"]
        + num_grid["Num_WEDGE6"]
        + num_grid["Num_WEDGE15"]
        + num_grid["Num_WEDGE18"]
        + num_grid["Num_POLYHEDRON"]
    )
    num_grid["NumNodes"] = numpy_coord.shape[0]

    return {
        "Coordinates": numpy_coord,
        "Connectivity": numpy_connectivity,
        "types": numpy_elem_type_cfs,
        "num_grid": num_grid,
    }


def ensightReadTimeStep(
    reader: vtk.vtkEnSightGoldBinaryReader,
    quantity: str,
    step=0,
    block: int = 0,
    idata: Dict | None = None,
) -> np.ndarray:
    if idata is None:
        idata = ensightGetInfo(reader)

    reader.UpdateTimeStep(idata["timeSteps"][step])
    reader.Update()

    idx_array = idata["fieldNames"].index(quantity)

    data = reader.GetOutput()

    # Get field data
    # fdata = data.GetFieldData()

    # Get block data
    bdata = data.GetBlock(block)

    if idata["fieldDataTypes"][idx_array] == "Cell":
        # Get cell data
        cpdata = bdata.GetCellData()
    elif idata["fieldDataTypes"][idx_array] == "Point":
        # Get point data
        cpdata = bdata.GetPointData()
    else:
        raise (IOError("No readable data found"))

    # Get vtk array
    adata = cpdata.GetArray(idx_array)

    # Convert vtkArray to numpy array:
    numpy_data = vtk_numpy.vtk_to_numpy(adata)

    # Reshape scalar array (scalar arrays are 2D with 1 column in CFS)
    if len(numpy_data.shape) == 1:
        numpy_data = numpy_data.reshape(-1, 1)

    return numpy_data


def ensightReadTimeSeries(
    reader: vtk.vtkEnSightGoldBinaryReader, quantity: str, block: int = 0
) -> Tuple[List[np.ndarray], np.ndarray]:
    """
    Read time series. Currently only works for data defined on cells (not on nodes).

    Parameters
    ----------
    reader : vtk.vtkEnSightGoldBinaryReader
    quantity : str
    block : int, optional

    Returns
    -------
    data : list[np.ndarray]
        List of time data arrays
    time_steps : np.ndarray
        Array to time step values

    """
    idata = ensightGetInfo(reader)

    data = []

    for i in progressbar(
        range(idata["numSteps"]),
        prefix=f"Reading time series {quantity}, Step: ",
        size=30,
    ):
        # print(f'Reading Step {i}')
        data.append(ensightReadTimeStep(reader, quantity, i, block, idata))

    return data, idata["timeSteps"]


def convert_to_cfs(file: str, quantities: List[str], region_dict: Dict, verbosity=v_def.release):
    reader = ensightInitReader(file=file)
    mesh_list = []
    for region in region_dict:
        data_geo = ensightReadMesh(reader, block=region_dict[region], verbosity=verbosity)
        mesh_list.append(
            io.mesh_from_coordinates_connectivity(
                coordinates=data_geo["Coordinates"],
                connectivity=data_geo["Connectivity"],
                element_dimension=3,
                region_name=region,
                verbosity=verbosity,
            )
        )

    mesh = mesh_list[0]
    for i in range(1, len(mesh_list)):
        mesh += mesh_list[i]

    result = io.CFSResultData(analysis_type=cfs_types.cfs_analysis_type.TRANSIENT)
    for quantity in quantities:
        for region in region_dict:
            data, step_values = ensightReadTimeSeries(reader, quantity, block=region_dict[region])
            result.add_data(
                data=np.array(data),
                step_values=step_values,
                quantity=quantity,
                region=region,
                restype=cfs_types.cfs_result_type.ELEMENT,
                multi_step_id=1,
            )

    return mesh, result

import h5py
import numpy as np
from typing import List, Optional
from .lib_types import nestedResultDict


# Constants :
RESULT_DESCRIPTION: str = "ResultDescription"
RESULTS: str = "Results"
MESH: str = "Mesh"
NODES: str = "Nodes"
ELEMENTS: str = "Elements"
REAL: str = "Real"
IMAG: str = "Imag"
MULTISTEP: str = "MultiStep_"
DATA: str = "data"


def get_result_names(file_path: str) -> List[str]:
    """Returns a list containing the names of the results which are given in the
    hdf file located at the file_path.

    Args:
        file_path (str): path to the hdf5 file.

    Returns:
        List[str]: list of result names.
    """

    hdf5_file = h5py.File(file_path, "r")
    return list(hdf5_file[RESULTS][MESH][f"{MULTISTEP}1"][RESULT_DESCRIPTION])


def get_results(file_path: str, result_names: Optional[List[str]] = None, dtype: type = np.float64) -> nestedResultDict:
    """Reads the hdf5 file located at file_path and extracts the results given
    in the result_names list. If this list is None then all of the results are read.

    Args:
        file_path (str): path to the hdf5 file.
        result_names (Optional[List[str]], optional): list of result names which we want to extract. Defaults to None.

    Returns:
        nestedResultDict: nested dictionary containing the results.
    """
    results: nestedResultDict = {}

    hdf5_file = h5py.File(file_path, "r")

    multisteps_list = list(hdf5_file[RESULTS][MESH].keys())

    for multistep in multisteps_list:

        steps_list = list(hdf5_file[RESULTS][MESH][multistep].keys())

        steps_list.remove(RESULT_DESCRIPTION)

        results[multistep] = {}
        for step in steps_list:
            result_list = list(hdf5_file[RESULTS][MESH][multistep][step].keys())

            results[multistep][step] = {}
            for result in result_list:

                if result_names is None or result in result_names:
                    region_list = list(hdf5_file[RESULTS][MESH][multistep][step][result].keys())

                    results[multistep][step][result] = {}
                    for region in region_list:

                        results[multistep][step][result][region] = {}
                        res_types = list(hdf5_file[RESULTS][MESH][multistep][step][result][region].keys())

                        if NODES in res_types:

                            data_types = list(hdf5_file[RESULTS][MESH][multistep][step][result][region][NODES].keys())
                            if REAL in data_types:
                                results[multistep][step][result][region][DATA] = np.array(
                                    hdf5_file[RESULTS][MESH][multistep][step][result][region][NODES][REAL],
                                    dtype=dtype,
                                )
                            if IMAG in data_types:
                                results[multistep][step][result][region][DATA] += 1j * (
                                    np.array(
                                        hdf5_file[RESULTS][MESH][multistep][step][result][region][NODES][IMAG],
                                        dtype=dtype,
                                    )
                                )

                        else:

                            data_types = list(
                                hdf5_file[RESULTS][MESH][multistep][step][result][region][ELEMENTS].keys()
                            )
                            if REAL in data_types:
                                results[multistep][step][result][region][DATA] = np.array(
                                    hdf5_file[RESULTS][MESH][multistep][step][result][region][ELEMENTS][REAL],
                                    dtype=dtype,
                                )
                            if IMAG in data_types:
                                results[multistep][step][result][region][DATA] += 1j * (
                                    np.array(
                                        hdf5_file[RESULTS][MESH][multistep][step][result][region][ELEMENTS][IMAG],
                                        dtype=dtype,
                                    )
                                )

    return results

import os
import re
import time
from glob import glob
from tqdm.auto import tqdm
from multiprocessing import Pool
import numpy as np
import numpy.typing as npt
from typing import List, Callable, Optional, TypeAlias, Dict

from .util import hdf5_io as h5io
from .util.lib_types import (
    pyCFSparamVec,
    pyCFSparam,
    nestedResultDict,
    resultVec,
    resultDict,
    sensorArrayResult,
    sensorArrayResultPacket,
)


# Constants :
N_PARAM_GROUPS = 4
CFS_EXT = "cfs"
XML_EXT = "xml"
JOU_EXT = "jou"
CDB_EXT = "cdb"
SA_NAME_SEPARATOR = "-"
SA_COORD_KEYS = ["origElemNum", "globCoord", "locCoord"]
LAST_EXEC_START = "last_exec_start"
LAST_EXEC_STOP = "last_exec_stop"

INFO_BOX_WIDTH = 90
INFO_BOX_CHAR = "#"

# Paths :
RESULTS_HDF_DIR = "results_hdf5"
HISTORY_DIR = "history"
LOGS_DIR = "logs"
SA_STORAGE_DIR = f"{HISTORY_DIR}"
DATA_DUMP_DIR = "data_dump"


class pyCFS:
    def __init__(
        self,
        project_name: str,
        cfs_install_dir: str,
        cfs_params_names: List[str] = [],
        material_params_names: List[str] = [],
        trelis_params_names: List[str] = [],
        trelis_version: str = "trelis",
        cfs_proj_path: str = "./",
        templates_path: str = "./templates",
        init_file_extension: str = "init",
        mat_file_name: str = "mat",
        n_threads: int = 1,
        res_manip_fun: Optional[Callable[["pyCFS"], None]] = None,
        quiet_mode: bool = False,
        detail_mode: bool = False,
        clean_finish: bool = False,
        save_hdf_results: bool = False,
        array_fill_value: pyCFSparam = np.nan,
        parallelize: bool = False,
        remeshing_on: bool = False,
        n_jobs_max: int = 1000,
        testing: bool = False,
        track_results: Optional[List[str]] = None,
        dump_results: bool = False,
    ):
        """

        OpenCFS and Trelis/CoreformCubit python interfacing package. The main
        goal of this module is to make an easy to use interface which provides
        a class that handles the automatic simulation setup from given CFS and
        Trelis parameters and the result storage.

        Args:
            project_name (str): Name of the simulation project (needs to be
            the same as the .xml file name)

            cfs_install_dir (str): Install path of CFS.

            cfs_params_names (list): List of trelis parameter names as defined in
                                        the associated .jou file.

            material_params_names (list): List of trelis parameter names as defined in
                                        the associated .jou file.

            trelis_params_names (list): List of trelis parameter names as defined in
                                        the associated .jou file.

            additional_param_fun (Callable): Handle to a function which modifies the
                                           additional parameters.

            additional_file_name (str): Additional file containing parameters changed
                                       by the additional_param_fun.

            trelis_version (str, optional): If 'coreform_cubit' is installed use it
                                            so that the correct one is run. Defaults
                                            to 'trelis'.

            parallelize (bool): Flag which chooses whether to parallelize the runs for
                                the given parameter matrices. Defaults to False.

            n_jobs_max (int): Max number of jobs to constrain the pool manager. Defaults
                              to inf.

            templates_path (str, optional): Path to template files. Defaults to "templates".

            cfs_proj_path (str, optional): Project path. Defaults to "./".

            init_file_extension (str): Extension added to project_name to identify
                                     init files which are used as templates.

            mat_file_name (str): Material file name. (default = "mat")

            n_threads (int): Number of threads to be used by OpenCFS. (default = 1).

            quiet_mode (bool): Turns a more conservative OpenCFS output on. (default = false).

            detail_mode (bool): Write detailed OpenCFS output to file. (default = false).

            clean_finish (bool): Delete all generated simulation files. Does not touch
                                result files. Defaults to False.

            testing (bool): If true will indicate to not create any directories or leave
                            footprints. Used for clean automated testing.

            track_results (List[str], optional): List of results which are to be tracked from
                                                 the main hdf file. If `None` then all results
                                                 are tracked. (default = None).

            dump_results (bool, optional): If True then after each run the tracked results are
                                           saved to disk. (default = False).
        """

        self.pyCFSobj: TypeAlias = pyCFS

        # Set init params from args :
        self.project_name = project_name
        self.sim_file = cfs_proj_path + project_name
        self.cfs_proj_path = cfs_proj_path
        self.cfs_install_dir = cfs_install_dir
        self.templates_path = templates_path
        self.n_threads = n_threads
        self.quiet_mode = quiet_mode
        self.detail_mode = detail_mode
        self.clean_finish = clean_finish
        self.save_hdf_results = save_hdf_results
        self.array_fill_value = array_fill_value
        self.parallelize = parallelize
        self.remeshing_on = remeshing_on
        self.n_jobs_max = n_jobs_max
        self.mat_file_name = mat_file_name
        self.init_file_extension = init_file_extension
        self.res_manip_fun = res_manip_fun
        self.trelis_version = trelis_version
        self.testing = testing
        self.track_results = track_results
        self.dump_results = dump_results

        self.trelis_params_names = trelis_params_names
        self.n_trelis_params = len(trelis_params_names)

        self.mat_params_names = material_params_names
        self.n_mat_params = len(material_params_names)

        self.cfs_params_names = cfs_params_names
        self.n_cfs_params = len(cfs_params_names)

        self.n_params = self.n_cfs_params + self.n_mat_params + self.n_trelis_params
        self.params = np.zeros((self.n_params,)).reshape(1, -1)

        # Initialize placeholders :
        self._init_placeholders()

        # # Set up paths and folder structure for results :
        self._init_paths()

        # # finalize parameter setup :
        self._init_param_setup()

        # # Generate file names :
        self._init_file_names()

        # Set functions -> less branches in code :
        self._init_functions()

        # Init sensor array setup :
        self._init_sensor_array_setup()

        # Print status report :
        self._print_init_status_report()

    def __call__(self, X: pyCFSparamVec, mesh_only: bool = False, mesh_present: bool = False) -> None:
        """

        Simulation forward function. Performs the simulation for the passed
        parameter combinations. Does not return anything as the results are
        stored in the self.results dictionary.

        Args:
            self (pyCFS): PyCfs class object.

            X (pyCFSparamVec): N x M Array containing the simulation parameters. Here
                            the M is the number of parameters in total.

            mesh_only (bool): If true only mesh files are generated for the
                             given parameters. (default = False).

        Returns:
            None
        """

        self._set_mesh_present_status(mesh_present)

        # check parameter shape :
        self._check_given_params(X)

        # record start time :
        self._record_time(LAST_EXEC_START)

        # run meshing only if True :
        if mesh_only:
            self._generate_meshes(X)
        # else run whole pipeline :
        else:
            self._forward(X)  # type: ignore[attr-defined]

        # record finish time :
        self._record_time(LAST_EXEC_STOP)

        # dump results if on :
        self._contruct_run_metadata(X)
        self._dump_results_if_on()

        # print run status report :
        self._print_run_status_report()

    # * ------------------ Init methods ------------------
    def _init_placeholders(self) -> None:
        self.files: List[str] = []
        self.sim_files: List[str] = []
        self.params_changed: npt.NDArray[np.bool_] = np.ones((N_PARAM_GROUPS,), dtype=bool)

        self._init_results()
        self.results_keys: List[str] = []
        self.result_regions: Optional[List[str]] = None
        self.ind: int = 0
        self.mesh_present: bool = False
        self.time: Dict[str, str] = {
            LAST_EXEC_START: "",
            LAST_EXEC_STOP: "",
            "init_time": time.ctime(time.time()),
        }
        self.result_dump_path: str = ""

    def _init_paths(self) -> None:
        """

        Initializes path variables and generates result paths if not present.

        """

        self.hdf_res_path = f"{self.cfs_proj_path}{RESULTS_HDF_DIR}/{self.project_name}/"
        self.hdf_file_path = f"{self.cfs_proj_path}{RESULTS_HDF_DIR}/{self.project_name}.{CFS_EXT}"
        self.logs_path = f"{self.cfs_proj_path}{LOGS_DIR}/"
        self.history_path = f"{self.cfs_proj_path}{HISTORY_DIR}/"
        self.data_dump_path = f"{self.cfs_proj_path}{DATA_DUMP_DIR}/"
        self.sa_storage_path = f"{self.cfs_proj_path}{SA_STORAGE_DIR}/"

        if not self.testing:

            if not os.path.exists(self.history_path):
                os.makedirs(self.history_path)

            if not os.path.exists(self.hdf_res_path):
                os.makedirs(self.hdf_res_path)

            if not os.path.exists(self.hdf_res_path):
                os.makedirs(self.hdf_res_path)

            if not os.path.exists(self.logs_path):
                os.makedirs(self.logs_path)

            if not os.path.exists(self.data_dump_path):
                os.makedirs(self.data_dump_path)

            if not os.path.exists(self.sa_storage_path):
                os.makedirs(self.sa_storage_path)

    def _init_param_setup(self) -> None:
        """

        Initializes the parameters by splitting these into the main groups.

        """

        # Additional params setup :
        self.additional_params_exist = False

        # Parameter setup :
        self.n_base_params = self.n_cfs_params + self.n_mat_params + self.n_trelis_params

        self._init_params_parallel(self.params)

        # Concatenate all params names :
        self.params_names = self.cfs_params_names + self.mat_params_names + self.trelis_params_names

    def _init_params_parallel(self, X: pyCFSparamVec) -> None:
        """

        Initializes the parameters for parallel execution. Essenatially
        splits up the parameter matrix X into the 4 different parameter
        groups which are used within the simulations.

        Args:
            X (pyCFSparamVec): N x M Array containing the simulation parameters. Here
                            the M is the number of parameters in total.
        """

        self.cfs_params = X[:, 0 : self.n_cfs_params]
        self.mat_params = X[:, self.n_cfs_params : self.n_cfs_params + self.n_mat_params]
        self.trelis_params = X[:, self.n_cfs_params + self.n_mat_params : self.n_base_params]
        self.add_params = X[:, self.n_cfs_params + self.n_mat_params + self.n_trelis_params :]

    def _init_file_names(self) -> None:
        """

        Generate names for the different simulation files which are used.

        """
        self.cfs_file_init = f"{self.templates_path}/{self.project_name}_{self.init_file_extension}.xml"
        self.mat_file_init = f"{self.templates_path}/{self.mat_file_name}_{self.init_file_extension}.xml"
        self.jou_file_init = f"{self.templates_path}/{self.project_name}_{self.init_file_extension}.jou"
        self.cfs_file = f"{self.sim_file}.xml"
        self.jou_file = f"{self.sim_file}.jou"
        self.mat_file = f"{self.mat_file_name}.xml"
        self.cdb_file = f"{self.project_name}.cdb"
        self.sim_files = [
            self.cfs_file,
            self.jou_file,
            self.mat_file,
            f"{self.sim_file}.info.xml",
            self.cdb_file,
        ]

    def _init_functions(self) -> None:
        """

        Initializes the functions to avoid branches in the code based on some
        logical flags.

        """
        self._forward: Callable[[pyCFSparamVec], None] = (
            self._forward_parallel if self.parallelize else self._forward_serial
        )
        self._clean_sim_files_if_on: Callable[[], None] = (
            self._clean_sim_files if self.clean_finish else self.dummy_fun_noarg
        )
        self._save_hdf_results_if_on: Callable[[int, bool], None] = (
            self._save_hdf_results if self.save_hdf_results else self.dummy_fun_int_bool
        )
        self._save_all_hdf_results_if_on: Callable[[], None] = (
            self._save_all_hdf_results if self.save_hdf_results else self.dummy_fun_noarg
        )
        self._clean_sim_files_parallel_if_on: Callable[[], None] = (
            self._clean_sim_files_parallel if self.clean_finish else self.dummy_fun_noarg
        )
        self._clean_hdf_results_parallel_if_on: Callable[[], None] = (
            self._clean_hdf_results_parallel if not self.save_hdf_results else self.dummy_fun_noarg
        )
        self._dump_results_if_on: Callable[[], None] = self._dump_results if self.dump_results else self.dummy_fun_noarg

    def _init_results(self) -> None:
        """

        Initializes an empty list for storing the hdf file results into.

        """
        self.results: List[nestedResultDict] = []
        self.sa_results: List[sensorArrayResultPacket] = []

    def _init_sensor_array_patterns(self) -> None:

        self.sensor_array_pattern = r'<sensorArray *fileName="" *type=".*" *csv="yes" *delimiter=",">\n*\
 *<coordinateFile *fileName=".*" *delimiter="," *commentCharacter="#"/>\n* *</sensorArray>'
        self.result_name_pattern = r'<sensorArray fileName="" type="([^"]*)" csv="yes" delimiter=",">'
        self.input_name_pattern = r'<coordinateFile fileName="(.*)\.csv"'
        self.filename_out_pattern = '<sensorArray fileName=""'

    def _init_sa_file_names(self) -> None:
        self.output_names = [f"{res}{SA_NAME_SEPARATOR}{inp}" for inp, res in zip(self.input_match, self.result_match)]

    def _extract_sensor_array_info(self, xml_contents) -> None:
        self.sensorarray_match = re.findall(self.sensor_array_pattern, xml_contents)
        self.result_match = re.findall(self.result_name_pattern, xml_contents)
        self.input_match = re.findall(self.input_name_pattern, xml_contents)
        self.input_match = list(map(lambda x: x.split("/")[-1], self.input_match))

    def _init_sensor_array_setup(self) -> None:

        if not self.testing:

            # get the init cfs file contents :
            cfs_xml_content = pyCFS.read_file_contents(self.cfs_file_init)

            # set up sensor array patterns :
            self._init_sensor_array_patterns()

            # extract sensor arrays :
            self._extract_sensor_array_info(cfs_xml_content)

            # init file names :
            self._init_sa_file_names()

    def _set_mesh_present_status(self, present: bool) -> None:
        self.mesh_present = present

    # * ------------------ Execution methods ------------------
    def _forward_serial(self: "pyCFS", X: pyCFSparamVec) -> None:
        """

        Performs the forward pass over all data. Determines number of parameter
        combinations N. Allocates the result arrays and stores the results
        of the performed calculations.

        Args:
            self (object): PyCfs class object.
            X (np.ndarray): N x M Array containing the simulation parameters. Here
                            the M is the number of parameters in total.

        Returns:
            None.
        """

        self.N = X.shape[0]
        self._init_results()

        for ind in tqdm(range(self.N)):
            self.ind = ind
            x = X[ind : ind + 1, :]
            self._forward_once_serial(x)

            self._set_results()

            self._handle_sa_results()

            self._save_hdf_results_if_on(ind)  # type: ignore[call-arg]

        self._clean_sim_files_if_on()

    def _forward_parallel(self: "pyCFS", X: pyCFSparamVec) -> None:
        """

        Performs the forward pass over all data in a parallel manner. Does the
        preprocessing step where the passed matrix is prepared for parallel computation
        and determines the number of parameter combinations N. Allocates the
        result arrays and stores the results of the performed calculations.

        Args:
            self (object): PyCfs class object.
            X (pyCFSparamVec): N x M Array containing the simulation parameters. Here
                            the M is the number of parameters in total.

        Returns:
            None.
        """

        self.N = X.shape[0]
        self._init_results()

        self._init_params_parallel(X)

        # generate data indices for parallel computing :
        data_list = np.arange(0, self.N)

        # determine number of jobs :
        n_jobs = min(len(data_list), self.n_jobs_max)

        # construct pool and pass jobs - starts the computation also:
        with Pool(processes=n_jobs) as p:
            with tqdm(total=len(data_list)) as pbar:
                for _ in p.imap_unordered(self._forward_once_parallel, data_list):
                    pbar.update()

                pbar.close()

        for ind in range(self.N):
            self._handle_sa_results(ind)
            self._set_results(ind)

        self._save_all_hdf_results_if_on()
        self._clean_hdf_results_parallel_if_on()
        self._clean_sim_files_parallel_if_on()

    def _forward_once_serial(self, x: pyCFSparamVec) -> None:
        """

        Performs the forward pass for one parameter configuration. Updates the
        simulation files. Runs the pipeline (trelis, cfs calculation), gets the
        results, stores them and cleans the history files from the history folder.

        Args:
            self (object): PyCfs class object.
            x (np.ndarray): Array containing the simulation parameters. Here
                            the M is the number of parameters in total.
            ind (int): Index of current parameter array out of the total N
                       configurations.

        Returns:
            None.
        """

        self._update_params(x)
        self._run_pipeline()
        self._set_all_params_changed_status(False)

        # add clean of hdf results if turned on !

    def _forward_once_parallel(self, ind: int) -> None:
        """

        Runs one process from the pool of currently active ones. Does
        this for the process with id = ind.

        Args:
            ind (int): job index to get correct parameters for simulation
                       and to read correct results from the result dir.
        """

        self._set_all_params_changed_status(True)
        self._run_pipeline(ind)

    def _run_pipeline(self, ind: Optional[int] = None) -> None:
        """

        Performs a check to see which parameters changes. If the parameter
        group in question did change then the appropriate file gets updated
        and if necessary further actions carried out. If any parameter
        group changed then the simulation is carried out.

        Args:
            self (object): PyCfs class object.
            ind (int): Pool job index to get correct parameters for simulation
                       and to read correct results from the result dir.

        Returns:
            None.
        """

        # Check if CFS xml parameters changed :
        if self.params_changed[0]:
            self._update_cfs_xml(ind)

        # Check if CFS mat parameters changed :
        if self.params_changed[1]:
            self._update_mat_xml(ind)

        # Check if meshing is needed :
        if self._is_meshing_needed(ind):
            self._run_meshing(ind)

        # If any config changes happened run simulation :
        if self.parallelize or np.any(self.params_changed):
            cfs_comm = self._make_cfs_command(ind)
            self._run(cfs_comm)

    def _run_meshing(self, ind: Optional[int] = None) -> None:
        """Updates the journal file and runs the meshing for this file.

        Args:
            ind (Optional[int], optional): Index of the job. Defaults to None.
        """
        self._update_trelis_jou(ind)
        mesher_comm = self._make_mesher_command(ind)
        self._run(mesher_comm)

    def _generate_meshes(self, X: pyCFSparamVec) -> None:
        """Generates the mesh files for the given parameters.

        Args:
            X (pyCFSparamVec): Parameter vector.

        Raises:
            ValueError: If parameter vector is empty.
        """
        if X.shape[0] == 1:
            self._generate_meshes_serial(X)
        else:
            self._generate_meshes_parallel(X)

    def _generate_meshes_serial(self, x: pyCFSparamVec) -> None:

        self._update_params(x)
        self._run_meshing()

    def _generate_meshes_parallel(self, X: pyCFSparamVec) -> None:

        self.N = X.shape[0]

        self._init_params_parallel(X)

        # generate data indices for parallel computing :
        data_list = np.arange(0, self.N)

        # determine number of jobs :
        n_jobs = min(len(data_list), self.n_jobs_max)

        # construct pool and pass jobs - starts the computation also:
        with Pool(processes=n_jobs) as p:
            with tqdm(total=len(data_list)) as pbar:
                for _ in p.imap_unordered(self._run_meshing, data_list):
                    pbar.update()

                pbar.close()

    def _is_meshing_needed(self, ind: Optional[int] = None) -> bool:
        """Checks if there is need to do meshing. In the case of non parallel execution
        this will be True when params_changed[2] is True and False if not (ind is always None
        for serial execution mode!). In the case of parallel execution it will return
        True only when parallelize and remeshing_on are both True (ind is never None when
        in parallel execution mode so first part is False).

        Args:
            ind (Optional[int], optional): Index of the job. Defaults to None.

        Returns:
            bool: Indicates if meshing should be performed.
        """
        return (self.params_changed[2] and (ind is None) and not self.mesh_present) or (
            self.remeshing_on and self.parallelize and not self.mesh_present
        )

    # * ------------------ Result handler methods ------------------
    def _generate_data_dump_path(self) -> str:
        t = time.ctime(time.time())
        t = t.replace(" ", "_").replace(":", "-")
        return f"{self.data_dump_path}data_dump_run_{t}.npy"

    def _contruct_run_metadata(self, X: pyCFSparamVec) -> None:
        file_paths = glob(f"{self.cfs_proj_path}/**/*.csv", recursive=True) + glob(
            f"{self.cfs_proj_path}/**/*.py", recursive=True
        )
        other_files = {k: pyCFS.read_file_contents(k) for k in file_paths}
        self.run_metadata = {
            "xml_template": pyCFS.read_file_contents(self.cfs_file_init),
            "mat_template": pyCFS.read_file_contents(self.mat_file_init),
            "jou_template": pyCFS.read_file_contents(self.jou_file_init),
            "other_files": other_files,
            "X": X,
            "run_start": self.time[LAST_EXEC_START],
            "run_finish": self.time[LAST_EXEC_STOP],
            "note": "",
        }

    def _dump_results(self) -> None:
        result_packet = {
            "results_hdf": self.results,
            "results_sensor_array": self.sa_results,
            "meta_data": self.run_metadata,
        }

        self.result_dump_path = self._generate_data_dump_path()
        np.save(self.result_dump_path, result_packet, allow_pickle=True)  # type: ignore[arg-type]

    def _handle_sa_results(self, ind: Optional[int] = None) -> None:

        # init sa results :
        sa_results: sensorArrayResultPacket = {}

        # currently only handling the sensor array outputs :
        sa_file_names = self._make_sa_output_paths(ind, for_reading=True)

        # read sensor array outputs :
        for sa_file in sa_file_names:
            name_parts = pyCFS._split_sa_result_name(sa_file, self.sa_storage_path)
            sa_results[name_parts[0]] = pyCFS._read_sa_result(sa_file)

        self.sa_results.append(sa_results)

    @staticmethod
    def _read_sa_result(sa_file: str) -> sensorArrayResult:
        # read the first line to acquire column names :
        f = open(sa_file)
        f_line = f.readline()
        f.close()

        col_names: List[str] = f_line.strip().split(",")

        # read the content :
        data = np.loadtxt(sa_file, dtype=np.float64, skiprows=1, delimiter=",")

        return {"data": data, "columns": col_names}

    @staticmethod
    def _split_sa_result_name(res_name: str, storage_path: str) -> List[str]:
        res_name = res_name.removeprefix(storage_path)
        return res_name.split(SA_NAME_SEPARATOR)

    def _get_hdf_curr_package(self, ind: Optional[int] = None) -> nestedResultDict:
        """

        Gets the hdf package for the current simulation run by extracting all
        results from the hdf file for the result regions defined in the inital
        run.

        Returns:
            Dict[str,np.ndarray]: Dict containing all of the results for all of
                                  the different regions where the results are defined.
        """
        file_path = self.hdf_file_path if ind is None else f"{self.hdf_file_path[:-4]}_{ind}.cfs"
        return h5io.get_results(file_path, result_names=self.track_results)

    def _save_hdf_results(self, ind: int = 0, is_parallel: bool = False) -> None:
        """

        Moves the current hdf results to another folder for saving purposes.

        Args:
            ind (int, optional): Index of the parameter set to relate to.
                                 Defaults to 0.
        """
        if is_parallel:
            cmd = f"mv {self.cfs_proj_path}{RESULTS_HDF_DIR}/{self.project_name}_{ind}.{CFS_EXT} \
            {self.hdf_res_path}{self.project_name}_{ind}.{CFS_EXT}"
        else:
            cmd = f"cp {self.cfs_proj_path}{RESULTS_HDF_DIR}/{self.project_name}.{CFS_EXT} \
                {self.hdf_res_path}{self.project_name}_{ind}.{CFS_EXT}"

        self._run(cmd)

    def _save_all_hdf_results(self) -> None:
        for i in range(self.N):
            self._save_hdf_results(i, is_parallel=True)

    def _set_results(self, ind: Optional[int] = None) -> None:
        """

        Reads the hdf results from the current file and appends the generated packet
        to the list of hdf results.

        Args:
            ind (int): Job index to get correct parameters for simulation
                       and to read correct results from the result dir.
        """
        hdf_package: nestedResultDict = self._get_hdf_curr_package(ind)
        self.results.append(hdf_package)

    @staticmethod
    def _is_coord_col(col_name: str) -> bool:
        return True in [key in col_name for key in SA_COORD_KEYS]

    @staticmethod
    def _remove_coord_cols(sa_res: sensorArrayResult) -> sensorArrayResult:
        cols: List[str] = []
        data_inds = np.zeros(len(sa_res["columns"]), dtype=bool)

        for ind, col in enumerate(sa_res["columns"]):
            if not pyCFS._is_coord_col(col):
                cols.append(col)
                data_inds[ind] = True

        res: sensorArrayResult = {"data": sa_res["data"][:, data_inds], "columns": cols}

        return res

    def get_all_results_for(self, result_name: str) -> List[resultDict]:
        """Returns the resultDict for the selected result name. It will
        contain all of the regions for which the result was computed.

        Args:
            result_name (str): Name of the result to be extracted.

        Returns:
            List[resultDict]: Dictionary containing the results.
        """

        results: List[resultDict] = []

        for result_dict in self.results:
            d = {}
            for multistep in result_dict.keys():
                for step in result_dict[multistep].keys():
                    for result in result_dict[multistep][step].keys():
                        if result == result_name:
                            for region in result_dict[multistep][step][result].keys():
                                d[region] = result_dict[multistep][step][result][region]["data"]

                            results.append(d)

        return results

    def get_results(self, ind: int) -> nestedResultDict:
        """Returns the stored hdf results from self.results located at the
        given index `ind`.

        Args:
            ind (int): Index from which to return the results. Represents
            the index of the parameter set.

        Returns:
            nestedResultDict: Nested result dict for the given index.
        """
        return self.results[ind]

    def get_sa_results(
        self, ind: int, unpack: bool = False, strip_coord: bool = False
    ) -> Optional[sensorArrayResultPacket | sensorArrayResult | resultDict]:
        """Returns Sensor Array results (`self.sa_results`) at a given index `ind`.
        Furthermore allows certain options to prepare the data for usage.

        Args:
            ind (int): Index from which to return the results. Represents
            the index of the parameter set.

            unpack (bool, optional): If True, unpacks the numpy data from
            the dictionary. Defaults to False.

            strip_coord (bool, optional): If True, removes columns which are
            related to the coordinates. Defaults to False.

        Raises:
            IndexError: Will raise index error if index is out of bounds.

        Returns:
            Optional[sensorArrayResultPacket | sensorArrayResult | resultDict]: The
            result is different depending on the options chosen.
        """

        if ind >= len(self.sa_results):
            raise IndexError("Index out of range for sensor array results!")

        res: sensorArrayResultPacket = self.sa_results[ind].copy()
        res_data: resultDict = {}

        for key, sub_res in res.items():

            if strip_coord:
                res[key] = pyCFS._remove_coord_cols(sub_res)

            if unpack:
                res_data[key] = res[key]["data"]

        return res_data if unpack else res

    def get_all_sa_results_for(
        self, result_name: str, unpack: bool = False, strip_coord: bool = False
    ) -> List[sensorArrayResult | resultVec | List[str]]:
        """Returns a list containing all sensor array results for a given
        `result_name`. Furthermore allows certain options to prepare the
        data for usage.

        Args:
            result_name (str): Name of the result to be exported.

            unpack (bool, optional): If True, unpacks the numpy data from
            the dictionary. Defaults to False.

            strip_coord (bool, optional): If True, removes columns which are
            related to the coordinates. Defaults to False.

        Returns:
            List[sensorArrayResult | resultVec | List[str]]: The
            result is different depending on the options chosen.
        """
        results: List[sensorArrayResult | resultVec | List[str]] = []

        for sa_res in self.sa_results:
            if result_name in sa_res.keys():

                res = sa_res[result_name].copy()

                # if coordinate columns should be stripped :
                if strip_coord:
                    res = pyCFS._remove_coord_cols(res)

                # if data should be unpacked
                if unpack:
                    results.append(res["data"])
                else:
                    results.append(res)

        return results

    def get_sa_columns_for(self, result_name: str) -> List[str]:
        """Returns the column names of a Sensor Array result for
        a given `result_name`.

        Args:
            result_name (str): Name of the result type.

        Returns:
            List[str]: List of column names.
        """
        columns: List[str] = []

        if len(self.sa_results) > 0 and result_name in self.sa_results[0]:
            columns = self.sa_results[0][result_name]["columns"]

        return columns

    # * ------------------ Param handler methods ------------------
    def _check_given_params(self, X: pyCFSparamVec) -> None:

        if len(X.shape) == 1:
            raise ValueError(
                "Parameter vector has only one dimension - the passed parameters \
must have shape (N x num_params) where N is the number of parameter sets."
            )
        elif len(X.shape) > 2:
            raise ValueError(
                "Parameter vector has more than 2 dimensions! - the passed parameters \
must have shape (N x num_params) where N is the number of parameter sets."
            )
        elif X.shape[1] != self.n_params:
            raise ValueError(
                f"Parameter vector does not have [{self.n_params}] parameters! - the passed parameters \
must have shape (N x num_params) where N is the number of parameter sets."
            )

    def _set_all_params_changed_status(self, flag: bool) -> None:
        """

        Sets the params changed variable elements all to the given flag.

        Args:
            flag (bool): Value to set params changed variable elements to.
        """
        self.params_changed = np.full((N_PARAM_GROUPS,), flag)

    def _update_file(
        self,
        init_file_name: str,
        file_out_name: str,
        params: np.ndarray,
        param_names: List[str],
        ind: Optional[int] = None,
    ) -> None:
        """

        Main update function for the individual files. Loads the init (template) file.
        Sets the parameter values and writes this to the appropriate simulation file.

        Args:
            self (object): PyCfs class object.
            init_file_name (str): Name of the init file.
            file_out_name (str): Name of the output file.
            params (np.ndarray): Array of parameter values to be set.
            param_names (List[str]): Names of the parameters to be set.

        Returns:
            None.
        """

        end_ext = file_out_name.split(".")[-1]
        ind_ext = f".{end_ext}" if ind is None else f"_{ind}.{end_ext}"
        ind_ext_cdb = f".{CDB_EXT}" if (ind is None or self.mesh_present) else f"_{ind}.{CDB_EXT}"
        ind_int = 0 if ind is None else ind

        if len(param_names) > 0:
            params = params[ind_int, :]

        file_out_name = file_out_name.replace(f".{end_ext}", ind_ext)

        data = pyCFS.read_file_contents(init_file_name)

        for param, pname in zip(params, param_names):
            param_str = str(int(param)) if "_ID" in pname else str(param)
            data = data.replace(pname, param_str)

        if end_ext == XML_EXT:
            data = data.replace('file="mat.xml"', f'file="mat{ind_ext}"')
            data = data.replace(
                f'cdb fileName="{self.cdb_file}"',
                f'cdb fileName="{self.cdb_file[:-4]}{ind_ext_cdb}"',
            )

            # do sensor array setup :
            data = self._fill_sensor_array_setup(data, ind)

        elif end_ext == JOU_EXT:
            data = data.replace(f'"{self.cdb_file}"', f'"{self.cdb_file[:-4]}{ind_ext_cdb}"')

        pyCFS.write_file_contents(file_out_name, data)

    def _make_sa_output_paths(self, ind: Optional[int], for_reading: bool = False) -> List[str]:

        sarrays_output_paths = []
        ind_ext = "" if ind is None else f"{SA_NAME_SEPARATOR}{ind}"
        step_ext = "-1" if for_reading else ""

        for out_name in self.output_names:
            sarrays_output_paths.append(f"{self.sa_storage_path}{out_name}{ind_ext}.csv{step_ext}")

        return sarrays_output_paths

    def _fill_sensor_array_setup(self, xml_content: str, ind: Optional[int] = None) -> str:

        output_names = self._make_sa_output_paths(ind)

        for sa, out_name in zip(self.sensorarray_match, output_names):
            filled_filename_pattern = self.filename_out_pattern.replace('""', f'"{out_name}"')
            filled_sa = sa.replace(self.filename_out_pattern, filled_filename_pattern)

            xml_content = xml_content.replace(sa, filled_sa)

        return xml_content

    def _update_params(self, params: np.ndarray) -> None:
        """

        Updates only parameters which changed and sets these in the param.
        arrays. If any group changed the appropriate flag is also set.

        Args:
            self (object): PyCfs class object.
            params (np.ndarray): Array containing all of the M parameters.

        Returns:
            None.
        """

        if ~np.all(self.cfs_params == params[:, 0 : self.n_cfs_params]):
            self.cfs_params = params[:, 0 : self.n_cfs_params]
            self.params_changed[0] = True

        if ~np.all(self.mat_params == params[:, self.n_cfs_params : self.n_cfs_params + self.n_mat_params]):
            self.mat_params = params[:, self.n_cfs_params : self.n_cfs_params + self.n_mat_params]
            self.params_changed[1] = True

        if ~np.all(self.trelis_params == params[:, self.n_cfs_params + self.n_mat_params : self.n_base_params]):
            self.trelis_params = params[:, self.n_cfs_params + self.n_mat_params : self.n_base_params]
            self.params_changed[2] = True

        if ~np.all(self.add_params == params[:, self.n_cfs_params + self.n_mat_params + self.n_trelis_params :]):
            self.add_params = params[:, self.n_cfs_params + self.n_mat_params + self.n_trelis_params :]
            self.params_changed[3] = True

    def _update_cfs_xml(self, ind: Optional[int] = None) -> None:
        """

        Updates the main cfs xml file with the new parameters.

        Args:
            self (object): PyCfs class object.

        Returns:
            None.
        """
        self._update_file(
            self.cfs_file_init,
            self.cfs_file,
            self.cfs_params,
            self.cfs_params_names,
            ind,
        )

    def _update_mat_xml(self, ind: Optional[int] = None) -> None:
        """

        Updates the material cfs xml file with the new parameters.

        Args:
            self (object): PyCfs class object.

        Returns:
            None.
        """
        self._update_file(
            self.mat_file_init,
            self.mat_file,
            self.mat_params,
            self.mat_params_names,
            ind,
        )

    def _update_trelis_jou(self, ind: Optional[int] = None) -> None:
        """

        Updates the trelis journal file with the new parameters.

        Args:
            self (object): PyCfs class object.

        Returns:
            None.
        """
        self._update_file(
            self.jou_file_init,
            self.jou_file,
            self.trelis_params,
            self.trelis_params_names,
            ind,
        )

    # * ------------------ Housekeeping methods ------------------
    def _clean_hist_results(self) -> None:
        """

        Removes all files from the hist folder and resets the
        file list.

        Args:
            self (object): PyCfs class object.

        Returns:
            None.
        """
        self._clean_files(self.files)
        self.files = []

    def _clean_sim_files_parallel(self) -> None:

        wildcards = [
            f"{self.cfs_proj_path}{self.project_name}*.{XML_EXT}",
            f"{self.cfs_proj_path}{self.mat_file_name}*.{XML_EXT}",
            f"{self.cfs_proj_path}{self.project_name}*.{JOU_EXT}",
        ]
        pyCFS._find_and_remove_files(wildcards)

    def _clean_hdf_results_parallel(self) -> None:
        wildcards = [f"{self.cfs_proj_path}{RESULTS_HDF_DIR}/*.{CFS_EXT}"]
        pyCFS._find_and_remove_files(wildcards)

    @staticmethod
    def _find_and_remove_files(wildcards: List[str] = []):
        for wildcard in wildcards:
            files = glob(wildcard)

            for file in files:
                os.remove(file)

    def _clean_sim_files(self) -> None:
        """

        Removes all generated simulation files from the hist folder and resets the
        file list.

        Args:
            self (object): PyCfs class object.

        Returns:
            None.
        """
        # self._reset_param_changed_status()
        self._clean_files(self.sim_files)

    def _clean_files(self, files: List[str]) -> None:
        """

        Removes all files from the passed files list.

        Args:
            self (object): PyCfs class object.
            files (List[str]): List of paths to files to delete.

        Returns:
            None.
        """
        for file in files:
            if os.path.exists(file) and CDB_EXT not in file:
                os.remove(file)

    # * ------------------ CFS and Mesher methods ------------------
    def _run(self, cmd: str) -> None:
        """

        Runs the passed command line command.

        Args:
            self (object): PyCfs class object.
            cmd (CommandStr): Command to be executed.

        Returns:
            None.
        """
        os.system(cmd)

    def _make_mesher_command(self, ind: Optional[int] = None) -> str:
        """

        Generates a mesher command str. If from Pool of processes ind won't be
        None and it will generate correct command for the current process.

        Args:
            ind (Optional[int]): job index to get correct parameters for simulation
                       and to read correct results from the result dir.
                       Default : None.

        Returns:
            str: A string containing a command runnable in the shell.
        """

        mesher_options = self._get_mesher_options()
        out_options = self._get_console_output_options(ind, is_sim=False)

        ind_ext = "" if ind is None else f"_{ind}"
        subjou_name = f" {self.sim_file[2:]}{ind_ext}.jou"

        return self.trelis_version + mesher_options + subjou_name + out_options

    def _make_cfs_command(self, ind: Optional[int] = None) -> str:
        """

        Generates a cfs command str. If from Pool of processes ind won't be
        None and it will generate correct command for the current process.

        Args:
            ind (Optional[int]): job index to get correct parameters for simulation
                       and to read correct results from the result dir.
                       Default : None.

        Returns:
            str: A string containing a command runnable in the shell.
        """

        cfs_options = self._get_cfs_options()
        out_options = self._get_console_output_options(ind)

        ind_ext = "" if ind is None else f"_{ind}"
        subsim_name = f" {self.sim_file[2:]}{ind_ext}"

        return self.cfs_install_dir + "cfs" + cfs_options + "-p" + subsim_name + ".xml" + subsim_name + out_options

    def _get_mesher_options(self) -> str:
        return " -batch -nographics -nojournal"

    def _get_cfs_options(self) -> str:
        """

        Constructs the CFS command with the selected
        optional arguments.

        Args:
            self (object): PyCfs class object.

        Returns:
            (str): String with the cfs options.
        """
        cfs_options = f" -t {self.n_threads} "

        # Enable quiet mode
        if self.quiet_mode:
            cfs_options += " -q "

        # Enable detailed mode to "info.xml" file
        if self.detail_mode:
            cfs_options += " -d "

        return cfs_options

    def _get_console_output_options(self, ind: Optional[int] = None, is_sim: bool = True) -> str:
        run_name = "sim" if is_sim else "mesher"
        return f" >> ./logs/{run_name}_output.log" if ind is None else f" >> ./logs/{run_name}_output_{ind}.log"

    # * ------------------ Time methods ------------------
    def _record_time(self, time_id: str) -> None:
        self.time[time_id] = time.ctime(time.time())

    # * ------------------ Report methods ------------------
    @staticmethod
    def _print_one_line_box(
        line_content: str = "", padding: bool = False, header: bool = False, n_times: int = 1, n_pads: int = 1
    ) -> None:

        pad = " " * n_pads if padding else ""
        filler = INFO_BOX_CHAR if header else " "
        padded_content = f"{pad}{line_content}{pad}"

        for _ in range(n_times):
            print(f"{INFO_BOX_CHAR}{padded_content:{filler}^{INFO_BOX_WIDTH - 2}}{INFO_BOX_CHAR}")

    def _print_init_status_report(self) -> None:
        pyCFS._print_one_line_box(header=True)
        title = f"Project : {self.project_name}"
        pyCFS._print_one_line_box(title, header=True, padding=True, n_pads=10)
        pyCFS._print_one_line_box(header=True)
        pyCFS._print_one_line_box(n_times=2)

        init_time = self.time["init_time"]
        pyCFS._print_one_line_box(f"Init at : {init_time}", padding=True)
        pyCFS._print_one_line_box()
        pyCFS._print_one_line_box(f"- Number of parameters : {self.n_params}", padding=True)
        pyCFS._print_one_line_box()
        pyCFS._print_one_line_box(f"- CFS parameters : {self.n_cfs_params}", padding=True)
        p_names = ", ".join(self.cfs_params_names)
        pyCFS._print_one_line_box(f"[{p_names}]", padding=True)
        pyCFS._print_one_line_box()
        pyCFS._print_one_line_box(f"- MAT parameters : {self.n_mat_params}", padding=True)
        p_names = ", ".join(self.mat_params_names)
        pyCFS._print_one_line_box(f"[{p_names}]", padding=True)
        pyCFS._print_one_line_box()
        pyCFS._print_one_line_box(f"- JOU parameters : {self.n_trelis_params}", padding=True)
        p_names = ", ".join(self.trelis_params_names)
        pyCFS._print_one_line_box(f"[{p_names}]", padding=True)
        pyCFS._print_one_line_box()
        pyCFS._print_one_line_box(f"- Tracked results : {self.track_results}", padding=True)
        pyCFS._print_one_line_box(f"- Parallelize : {self.parallelize}", padding=True)
        pyCFS._print_one_line_box(f"- Remeshing on : {self.remeshing_on}", padding=True)

        pyCFS._print_one_line_box(n_times=2)
        pyCFS._print_one_line_box(header=True)

    def _print_run_status_report(self) -> None:
        pyCFS._print_one_line_box(header=True)
        title = f"Run report : {self.project_name}"
        pyCFS._print_one_line_box(title, header=True, padding=True, n_pads=10)
        pyCFS._print_one_line_box(header=True)
        pyCFS._print_one_line_box(n_times=2)

        pyCFS._print_one_line_box(f" Start at : {self.time[LAST_EXEC_START]}", padding=True)
        pyCFS._print_one_line_box(f"Finish at : {self.time[LAST_EXEC_STOP]}", padding=True)

        pyCFS._print_one_line_box(n_times=2)
        pyCFS._print_one_line_box(f"- Total runs : {self.N}", padding=True)
        pyCFS._print_one_line_box()
        pyCFS._print_one_line_box(f"- Data dumped : {self.dump_results}", padding=True)
        if self.dump_results:
            pyCFS._print_one_line_box(f"@ : {self.result_dump_path}", padding=True)

        pyCFS._print_one_line_box(n_times=2)
        pyCFS._print_one_line_box(header=True)

    # * ------------------ I/O methods ------------------
    @staticmethod
    def read_file_contents(file_path: str) -> str:

        file = open(file_path, "r")
        contents = file.read()
        file.close()

        return contents

    @staticmethod
    def write_file_contents(file_path: str, contents: str) -> None:

        file = open(file_path, "w")
        file.write(contents)
        file.close()

    # * ------------------ Helper methods ------------------
    def dummy_fun(self, ind: int = 0) -> None:
        pass

    def dummy_fun_int_bool(self, ind: int = 0, is_parallel: bool = False) -> None:
        pass

    def dummy_fun_noarg(self) -> None:
        pass

    def _default_external_result_manip(self, obj: object) -> None:
        """

        Dummy function for external results manipulation. If no external
        result manipulation function is passed this one is executed and
        does nothing which is the goal.

        Args:
            obj (object): pycfs object instance.
        """
        pass

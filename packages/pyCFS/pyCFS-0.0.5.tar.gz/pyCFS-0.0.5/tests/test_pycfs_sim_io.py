from pyCFS import pyCFS
from .pycfs_fixtures import sensor_array_result_file
import numpy as np
import os


def test_read_sa_result(sensor_array_result_file):
    sa_result = pyCFS._read_sa_result(sensor_array_result_file["file"])
    assert sa_result["columns"] == sensor_array_result_file["columns"]
    assert np.all(sa_result["data"] == sensor_array_result_file["data"])


def test_split_sa_result_name(sensor_array_result_file):
    name_split = pyCFS._split_sa_result_name(sensor_array_result_file["file"], "")
    assert name_split == sensor_array_result_file["file_split"]


def test_is_coord_col():
    assert pyCFS._is_coord_col("origElemNum") == True
    assert pyCFS._is_coord_col("globCoord-x") == True
    assert pyCFS._is_coord_col("globCoord-y") == True
    assert pyCFS._is_coord_col("globCoord-z") == True
    assert pyCFS._is_coord_col("locCoord-xi") == True
    assert pyCFS._is_coord_col("locCoord-eta") == True
    assert pyCFS._is_coord_col("locCoord-zeta") == True
    assert pyCFS._is_coord_col("elecFieldIntensity-z") == False
    assert pyCFS._is_coord_col("elecPotential") == False


def test_remove_coord_cols(sensor_array_result_file):
    sa_result = pyCFS._read_sa_result(sensor_array_result_file["file"])
    sa_result_no_coord = pyCFS._remove_coord_cols(sa_result)

    assert sa_result["columns"] == sensor_array_result_file["columns"]
    assert np.all(sa_result["data"] == sensor_array_result_file["data"])
    assert sa_result_no_coord["columns"] == sensor_array_result_file["columns_nocoord"]
    assert np.all(sa_result_no_coord["data"] == sensor_array_result_file["data_nocoord"])


def test_write_read_contents():
    contents = "secret test message"
    file = "./tests/data/sim_io/temp_file.txt"

    pyCFS.write_file_contents(file, contents)
    read_contents = pyCFS.read_file_contents(file)

    assert read_contents == contents

def test_find_and_remove_files():
    wildcards = ["./tests/data/sim_io/*file.txt"]
    pyCFS._find_and_remove_files(wildcards)

    assert os.path.exists("./tests/data/sim_io/temp_file.txt") == False

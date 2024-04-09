import random
import time

import numpy as np
import pytest

from pyCFS.data.io.cfs_types import cfs_element_type
from pyCFS.data.util import trilateration, element_quality, progressbar, connectivity_list_to_matrix


def test_trilateration():
    A = np.array([1, 1, 2])
    B = np.array([4, 7, 2])
    C = np.array([0, -2, 4])
    P = np.array([1, 2, 3])

    R1 = np.linalg.norm(P - A)
    R2 = np.linalg.norm(P - B)
    R3 = np.linalg.norm(P - C)

    print(trilateration(A, B, C, R1, R2, R3))


def test_element_quality():
    A = np.array([1, 1, 2])
    B = np.array([4, 7, 2])
    C = np.array([0, -2, 4])
    P = np.array([1, 2, 3])

    coordinates = np.array([A, B, C])
    connectivity = np.array([[1, 2, 3, 0]])

    el_conn = connectivity[0, :]
    print(element_quality(coordinates[el_conn[:3] - 1, :], cfs_element_type.TRIA3, metric="skewness"))
    print(element_quality(coordinates[el_conn[:3] - 1, :], cfs_element_type.TRIA3, metric="quality"))

    coordinates = np.array([A, B, C, P])
    connectivity = np.array([[1, 2, 3, 4]])
    el_conn = connectivity[0, :]
    print(element_quality(coordinates[el_conn[:4] - 1, :], cfs_element_type.TET4, metric="quality"))


def test_progressbar():

    for _ in progressbar([]):
        pass

    for _ in progressbar(range(40), "loop progress"):
        time.sleep(2e-2 * random.random())


def test_connectivity_list_to_matrix():

    conn_list = np.array(
        [
            1,
            2,
            15,
            22,
            3,
            4,
            16,
            23,
            62,
            66,
            101,
            64,
            67,
            71,
            103,
            69,
            63,
            65,
            100,
            116,
            3,
            4,
            16,
            23,
            5,
            6,
            17,
            24,
            67,
            71,
            103,
            69,
            72,
            76,
            105,
            74,
            68,
            70,
            102,
            117,
            5,
            6,
            17,
            24,
            7,
            8,
            18,
            25,
            72,
            76,
            105,
            74,
            77,
            81,
            107,
            79,
            73,
            75,
            104,
            118,
            7,
        ]
    )
    offset = np.array([0, 20, 40, 60])

    conn = connectivity_list_to_matrix(connectivity_list=conn_list, offsets=offset, verbose=True)
    print(conn)

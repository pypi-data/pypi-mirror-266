from __future__ import annotations

import datetime
import time
from itertools import repeat
from multiprocessing import Pool

import numpy as np
from scipy import sparse
from skspatial.objects import Point, Vector, Line, Plane, Triangle
from typing import List, Dict, Optional

from pyCFS.data import io
from pyCFS.data.io import cfs_types, CFSResultData
from pyCFS.data.operators import interpolators
from pyCFS.data.util import progressbar, vecnorm


###############################################
# class PointVal is an extension of the class Point to add values and IDs
# to the Coordinates and generate a point-value pair with an ID


class PointVal(Point):
    def __new__(cls, coord, *args, **kwargs):
        return super().__new__(cls, coord)

    def __init__(self, coord, value: float | None = None, pid=None) -> None:
        self.val = value
        self.id = pid


class TriangleElement(Triangle):
    def __init__(self, point_a: PointVal, point_b: PointVal, point_c: PointVal, eid=None):
        Triangle.__init__(self, point_a, point_b, point_c)
        self.val_a = point_a.val
        self.val_b = point_b.val
        self.val_c = point_c.val
        self.id_a = point_a.id
        self.id_b = point_b.id
        self.id_c = point_c.id
        self.id = eid

    def min_distance_point(self, point):
        return min(
            [
                self.point_a.distance_point(point),
                self.point_b.distance_point(point),
                self.point_c.distance_point(point),
            ]
        )

    def project_point(self, point, direction=None, max_distance=None) -> Point | PointVal | None:
        plane = Plane(self.point_a, self.normal())
        if direction is None:
            projected_point = plane.project_point(point)
        else:
            intersection_line = Line(point=point, direction=direction)
            try:
                projected_point = plane.intersect_line(intersection_line)
            except ValueError:  # The line and plane must not be parallel.
                return None
        if point.distance_point(projected_point) > max_distance:
            return None
        else:
            return projected_point

    def coordinate_transform(self, projected_point):
        vec_ab = Vector.from_points(self.point_a, self.point_b)
        vec_ac = Vector.from_points(self.point_a, self.point_c)
        unitvec_r = vec_ab.unit()
        unitvec_s = (vec_ac - np.dot(vec_ac, unitvec_r) * unitvec_r).unit()
        x_0 = self.point_a
        x_p = projected_point

        # coord_a (point_a) is the origin of the transformed coordinate system
        coord_a = [0, 0, 0]
        A = np.array([coord_a, vec_ab, vec_ac, x_p - x_0])
        unitvecs = np.array([unitvec_r, unitvec_s])
        coordinates = np.matmul(A, np.transpose(unitvecs))

        return coordinates

    def basis_functions(self, coordinates):

        a_r, a_s = coordinates[0, :]
        b_r, b_s = coordinates[1, :]
        c_r, c_s = coordinates[2, :]
        p_r, p_s = coordinates[3, :]

        denominator = (a_r - c_r) * (b_s - c_s) - (a_s - c_s) * (b_r - c_r)
        phi_a = ((b_s - c_s) * (p_r - c_r) - (b_r - c_r) * (p_s - c_s)) / denominator
        phi_b = (-(a_s - c_s) * (p_r - c_r) + (a_r - c_r) * (p_s - c_s)) / denominator
        phi_c = 1 - phi_a - phi_b

        return np.array([phi_a, phi_b, phi_c])

    def normal_vector(self) -> Vector:
        v1 = Vector.from_points(point_a=self.point_a, point_b=self.point_b)
        v2 = Vector.from_points(point_a=self.point_a, point_b=self.point_c)

        return v1.cross(v2).unit()


def generate_point_list(coord_reg) -> List[PointVal]:
    point_list = []
    for i in range(coord_reg.shape[0]):
        point_list.append(PointVal(coord_reg[i, :], pid=i))
    return point_list


def generate_triangle_list(point_list, conn_reg) -> List[TriangleElement]:
    triangle_list = []
    j = 0
    for triple in conn_reg[:, 0:3]:
        triangle_list.append(
            TriangleElement(
                point_list[triple[0]],
                point_list[triple[1]],
                point_list[triple[2]],
                eid=j,
            )
        )
        j += 1
    return triangle_list


def interp_matrix(
    trgt_point_list: List,
    src_point_list: List,
    triangle_list: List,
    proj_direction: List[np.ndarray] | np.ndarray,
    max_proj_distance: float,
    search_radius: float | None = None,
    eps=-1e-9,
    workers: Optional[int] = None,
):
    interpolation_matrix = np.zeros([len(trgt_point_list), len(src_point_list)])

    if type(proj_direction) is np.ndarray:
        proj_direction = [proj_direction for _ in range(len(trgt_point_list))]

    if workers is None or workers > 1:
        print("Building interpolation matrix", end="")
        with Pool(processes=workers) as pool:
            t_start = time.time()
            for idx, res in enumerate(
                pool.starmap(
                    interp_matrix_point,
                    zip(
                        trgt_point_list,
                        repeat(triangle_list),
                        proj_direction,
                        repeat(max_proj_distance),
                        repeat(search_radius),
                        repeat(eps),
                    ),
                )
            ):
                if res is not None:
                    interpolation_matrix[trgt_point_list[idx].id, res[0]] = res[1]
        print(f" | Elapsed time: {datetime.timedelta(seconds=int(time.time() - t_start))}")
    else:
        for idx, point in enumerate(progressbar(trgt_point_list, prefix="Building interpolation matrix: ", size=25)):
            res = interp_matrix_point(
                point,
                triangle_list,
                proj_direction[idx],
                max_proj_distance,
                search_radius,
                eps,
            )
            if res is not None:
                interpolation_matrix[point.id, res[0]] = res[1]

    return interpolation_matrix


def interp_matrix_point(
    point: Point | PointVal,
    triangle_list: List,
    proj_direction: np.ndarray,
    max_proj_distance: float,
    search_radius: float | None = None,
    eps=-1e-9,
):
    if search_radius is None:
        search_radius = max_proj_distance
    for triangle in triangle_list:
        if triangle.min_distance_point(point) > search_radius:
            continue
        projected_point = triangle.project_point(point, proj_direction, max_proj_distance)
        if projected_point is None:
            continue
        coordinates = triangle.coordinate_transform(projected_point)
        phi = triangle.basis_functions(coordinates)
        if np.any(phi < eps):
            continue
        col_idx = np.array([triangle.id_a, triangle.id_b, triangle.id_c])

        return col_idx, phi

    return None


def interpolation_fe(
    src_coord: np.ndarray,
    src_conn: np.ndarray,
    src_reg_node: np.ndarray,
    src_reg_elem: np.ndarray,
    trgt_coord: np.ndarray,
    trgt_conn: np.ndarray,
    trgt_reg_node: np.ndarray,
    trgt_reg_elem: np.ndarray,
    proj_direction: np.ndarray | List[np.ndarray] | None = None,
    max_distance=0.03,
    search_radius: float | None = None,
    workers: Optional[int] = None,
):
    """
    Interpolation matrix for projection-based interpolation. Points of the target mesh are projected onto the
    source mesh and evaluated based on linear FE basis functions.
    """
    src_coord_reg = src_coord[src_reg_node - 1]
    src_conn_reg = src_conn[src_reg_elem - 1, :]
    trgt_coord_reg = trgt_coord[trgt_reg_node - 1]
    trgt_conn_reg = trgt_conn[trgt_reg_elem - 1, :]

    connectivity_map_src = {v: k + 1 for k, v in dict(enumerate(src_reg_node.flatten())).items()}
    connectivity_map_src[0] = 0
    src_conn_reg_mapped = np.vectorize(connectivity_map_src.get)(src_conn_reg) - 1

    connectivity_map_trgt = {v: k + 1 for k, v in dict(enumerate(trgt_reg_node.flatten())).items()}
    connectivity_map_trgt[0] = 0
    trgt_conn_reg_mapped = np.vectorize(connectivity_map_trgt.get)(trgt_conn_reg) - 1

    src_point_list = generate_point_list(src_coord_reg)
    trgt_point_list = generate_point_list(trgt_coord_reg)
    src_triangle_list = generate_triangle_list(src_point_list, src_conn_reg_mapped)
    trgt_triangle_list = generate_triangle_list(trgt_point_list, trgt_conn_reg_mapped)

    if proj_direction is None:
        vn = np.zeros((len(trgt_triangle_list), 3))
        proj_direction = []
        for el_id, tria in enumerate(trgt_triangle_list):
            vn[el_id, :] = tria.normal_vector()

        for k in range(len(trgt_point_list)):
            el_idx = np.where(trgt_conn_reg_mapped == k)[0]
            proj_direction.append(vecnorm(np.mean(vn[el_idx], axis=0)))

    interpolation_matrix = interp_matrix(
        trgt_point_list, src_point_list, src_triangle_list, proj_direction, max_distance, search_radius, workers=workers
    )

    interpolation_matrix_sparse = sparse.csr_matrix(interpolation_matrix)

    return interpolation_matrix_sparse


def interpolate_region(
    file_src: str,
    file_target: str,
    region_src_target_dict: Dict,
    quantity_name: str,
    dim_names=None,
    is_complex=None,
    projection_direction: np.ndarray | None = None,
    max_projection_distance=0.1,
    search_radius=None,
    workers: Optional[int] = None,
) -> io.CFSResultData:
    """
    max_projection_distance: Lower values speed up interpolation matrix build and prevent projecting onto far surfaces.
    search_radius            Should be chosed at least to the maximum element size of the target grid.
    """
    with io.CFSReader(file_src) as h5reader:
        src_mesh = h5reader.MeshData
        src_data = h5reader.MultiStepData

    result_array_list = []
    for src_region_name in region_src_target_dict:
        # Convert quads to triangles in src mesh
        src_mesh.convert_quad2tria()
        src_region = src_mesh.Regions[src_mesh.Regions.index(src_region_name)]

        target_region_list = []
        with io.CFSReader(file_target) as h5reader:
            target_mesh = h5reader.MeshData
            # Convert quads to triangles in target mesh (for normal vector calculation)
            target_mesh.convert_quad2tria()
            for target_region_name in region_src_target_dict[src_region_name]:
                target_region_list.append(target_mesh.Regions[target_mesh.Regions.index(target_region_name)])

        # Source grid
        src_coord = src_mesh.Coordinates
        src_connectivity = src_mesh.Connectivity
        src_reg_nodes = src_region.Nodes
        src_reg_elems = src_region.Elements

        for target_region in target_region_list:
            # Target grid
            target_coord = target_mesh.Coordinates
            target_connectivity = target_mesh.Connectivity
            target_reg_nodes = target_region.Nodes
            target_reg_elems = target_region.Elements

            # Get interpolation matrix
            print(f'Computing interpolation matrix: "{src_region.Name}"-> "{target_region.Name}"')
            interpolation_matrix = interpolation_fe(
                src_coord,
                src_connectivity,
                src_reg_nodes,
                src_reg_elems,
                target_coord,
                target_connectivity,
                target_reg_nodes,
                target_reg_elems,
                proj_direction=projection_direction,
                max_distance=max_projection_distance,
                search_radius=search_radius,
                workers=workers,
            )

            # Perform interpolation
            src_array = src_data.get_data_array(
                quantity=quantity_name, region=src_region_name, restype=cfs_types.cfs_result_type.NODE
            )
            result_array = interpolators.apply_interpolation(
                result_array=src_array,
                interpolation_matrix=interpolation_matrix,
                restype_out=cfs_types.cfs_result_type.NODE,
                region_out=target_region.Name,
            )

            # # Perform interpolation
            # step_value_list = src_data.StepValues
            # data_write = []
            # for i in progressbar(range(step_value_list.shape[0]), 'Performing interpolation: '):
            #     data_read_complex = src_data.Data[i][quantity_name][src_region_name][cfs_types.cfs_result_type.NODE]
            #     data_interpolated_complex = interpolation_matrix.dot(data_read_complex)
            #     data_write.append(data_interpolated_complex)
            #
            # # Write Data object
            # result_data = io.CFSResultData(analysis_type=cfs_types.cfs_analysis_type.HARMONIC)
            # result_data.add_data(data_write, step_values=step_value_list, quantity=quantity_name,
            #                      region=target_region.Name, restype=cfs_types.cfs_result_type.NODE, dim_names=dim_names,
            #                      is_complex=is_complex)
            #
            result_array_list.append(result_array)

    return CFSResultData(
        analysis_type=src_data.AnalysisType, multi_step_id=src_data.MultiStepID, data=result_array_list
    )

from dataclasses import dataclass

from .mesh_util_interface import MeshUtilities
from .helpers.slicing import helper_multi_split
from .helpers.smoothing import helper_smooth_plain_mesh
from .helpers.plane_creation import helper_create_plane
from .helpers.projection_on_mesh import helper_transform_plain_after_top, helper_transform_plain_after_bottom, helper_transform_plain_slop
from .helpers.projection_on_plain import helper_distort_mesh_on_plain
from ..globals import Settings, Glob


import numpy as np
import trimesh



class MeshTools(MeshUtilities):

    @staticmethod
    def multi_split( mesh: trimesh.Trimesh, normal, steps : np.array, progress_callback=None):
        helper_multi_split(mesh, normal, steps, progress_callback)
        pass

    @staticmethod
    def smooth_plain_mesh( plain_mesh: trimesh.Trimesh, settings: Settings, progress_callback=None):
        helper_smooth_plain_mesh(plain_mesh, settings.max_p, progress_callback)
        pass

    @staticmethod
    def create_plane(boundingbox, settings:Settings, padding: float, progress_callback ) -> trimesh.Trimesh:
        return helper_create_plane(boundingbox, settings.resolution)

    @staticmethod
    def distort_mesh_on_plain( plain_mesh: trimesh.Trimesh , mesh: trimesh.Trimesh ,progress_callback=None):
        helper_distort_mesh_on_plain(plain_mesh, mesh, progress_callback)



    @staticmethod
    def transform_plain_slop(plain_mesh: trimesh.Trimesh , mesh: trimesh.Trimesh, settings: Settings, progress_callback=None):
        helper_transform_plain_slop(plain_mesh, mesh, progress_callback)
        pass


    @staticmethod
    def transform_smooth_surface(plain_mesh: trimesh.Trimesh , mesh: trimesh.Trimesh, settings: Settings, progress_callback=None):
        helper_transform_plain_after_top(plain_mesh, mesh, settings.max_p, progress_callback )



    @staticmethod
    def transform_avoid_overhangs(plain_mesh: trimesh.Trimesh, mesh: trimesh.Trimesh, settings: Settings, progress_callback=None):
        helper_transform_plain_after_bottom(plain_mesh, mesh, settings.max_p, progress_callback)

    @staticmethod
    def shift_to_center(mesh: trimesh.Trimesh):
        """
            Translates the mesh so that it is centered around the origin in the XY plane
            and aligned to the base (z=0) along the Z-axis.

            This method calculates the bounding box of the mesh and applies a translation
            such that the mesh is centered in the X and Y directions and its lowest Z
            point is moved to zero.

            Returns:
                None: The mesh is modified in-place by translating its vertices.

            Notes:
                - Assumes `self.mesh` has a `bounding_box` with `bounds` that return a
                  tuple of two points: the minimum and maximum XYZ coordinates.
                - Also assumes `self.mesh` supports the `apply_translation` method.
        """
        v_min, v_max = mesh.bounding_box.bounds

        mesh.apply_translation(
            [-v_min[0] - (v_max[0] - v_min[0]) / 2, -v_min[1] - (v_max[1] - v_min[1]) / 2, -v_min[2]])

    @staticmethod
    def split_mesh_on_edges_from_plain(plain_mesh: trimesh.Trimesh, mesh: trimesh.Trimesh, progress_callback=None):
        """
            cutOnV adds vertices to mesh on each uniq x and y from Trasformer mesh
             Parameters:
            ----------
            None

            Returns:
            -------
            None
        """
        x_coords = plain_mesh.vertices[:, 0]
        y_coords = plain_mesh.vertices[:, 1]

        unique_x_coords = np.unique(x_coords)
        normal = [1, 0, 0]
        unique_x_coords = [x + 0.00001 for x in unique_x_coords]
        MeshTools.multi_split(mesh, normal, unique_x_coords, progress_callback)

        unique_y_coords = np.unique(y_coords)
        normal = [0, 1, 0]
        unique_y_coords = [y + 0.0001 for y in unique_y_coords]
        MeshTools.multi_split(mesh, normal, unique_y_coords, progress_callback)
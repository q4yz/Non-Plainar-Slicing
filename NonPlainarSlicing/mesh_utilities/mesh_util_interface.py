from abc import ABC, abstractmethod
import trimesh
import numpy as np

from ..globals import ProgressTracker
from ..globals import Settings


class MeshUtilities(ABC):
    @staticmethod
    @abstractmethod
    def multi_split( mesh: trimesh.Trimesh, normal, steps: np.array, progress_callback: ProgressTracker):
        """
            Slices a 3D mesh multiple times along planes perpendicular to a given normal.

            The mesh is first rotated so that the provided `normal` aligns with the Z-axis.
            Then, for each value in `steps`, the mesh is translated downward along Z,
            and a cut is performed on the Z=0 plane using `cut_mesh_on_z_zero`. This simulates
            slicing the mesh at each step level. After all slices are applied, the mesh
            is transformed back to its original orientation and position.

            Parameters:
                mesh (trimesh.Trimesh): The 3D mesh to be sliced.
                normal (array-like): A vector representing the slicing direction. This vector will
                                     be aligned to the Z-axis during processing.
                steps (np.ndarray): A list or array of float values representing the Z-depths at which
                                    slices should occur. Must be sorted in ascending or descending order.


            Returns:
                    trimesh.Trimesh: The resulting mesh after all slices and transformations.

            Notes:
                    - Assumes the mesh contains only triangular faces.
                    - Assumes that no vertex lies exactly on the Z=0 plane at any slicing step.
                    - The `cut_mesh_on_z_zero` function is used to process intersecting faces during slicing.
                    - The function is non-destructive: all transformations are reversed at the end.

            Raises:
                NotImplementedError: If the method is not implemented by a subclass.

        """
        pass

    @staticmethod
    @abstractmethod
    def smooth_plain_mesh( plain_mesh: trimesh.Trimesh, angle: float, progress_callback: ProgressTracker) -> trimesh.Trimesh:
        """
            Smooths the Z-coordinates of a mesh's vertices by enforcing a maximum slope angle.

            This function iteratively updates the Z-values of vertices to ensure that no vertex
            deviates from its neighbors by more than the allowed angle (slope) when projected
            in the XY plane. It effectively "clamps" high neighboring vertices downward to smooth
            sharp peaks and maintain a more gradual surface transition.

            The algorithm:
                - Iterates over each vertex.
                - Finds neighboring vertices connected by faces.
                - Calculates the maximum allowed Z-difference based on the given angle and horizontal distance.
                - Adjusts Z-values of neighbors that exceed the slope constraint.
                - Repeats until the changes fall below a specified tolerance.

            Args:
                plain_mesh (trimesh.Trimesh): The input 3D mesh to be smoothed.
                angle (float): Maximum allowed angle (in degrees) between neighboring vertices.
                tol (float, optional): Tolerance for convergence. Iteration stops when max change < tol.

            Returns:
                trimesh.Trimesh: A new smoothed mesh with updated Z-coordinates.

            Notes:
                - Only Z-values are modified; X and Y remain unchanged.
                - This method assumes a progressive smoothing based on minimum vertex heights.
                - Global variable `glob.progress2` is updated during execution to track progress.

            Raises:
                NotImplementedError: If the method is not implemented by a subclass.
        """
        pass



    @staticmethod
    @abstractmethod
    def distort_mesh_on_plain(plain_mesh: trimesh.Trimesh, progress_callback: ProgressTracker):
        """
            Casts vertical rays from above each vertex to detect intersections with the transformer mesh.

            For each vertex in `v`, this method casts a ray starting from a high Z-value (z=1000),
            pointing straight downward (negative Z-direction). It checks for intersections between
            these rays and the surface of the `transformerPlain` mesh, and returns the locations
            and corresponding indices of intersecting rays.

            Args:
                v (np.ndarray): An (N, 3) array of vertex positions (X, Y, Z) from the main mesh.

            Returns:
                tuple:
                    - locations (np.ndarray): An (M, 3) array of intersection points in 3D space.
                    - index_ray (np.ndarray): An array of indices into `v`, indicating which rays (vertices) had intersections.

            Notes:
                - This method assumes `self.transformerPlain.mesh` has a `ray.intersects_location` method.
                - Rays are cast vertically downward from z=1000 to detect intersections.
                - Only rays that intersect the transformer mesh are included in the output.
        """
        pass

    @staticmethod
    @abstractmethod
    def create_plane(boundingbox, resolution: float, padding: float, progress_callback: ProgressTracker) -> trimesh.Trimesh:
        """
            Create a 3D mesh representing a plane based on the object's bounding box and resolution.

            This method should generate a planar mesh in the XY plane (Z=0)
            and assign it to the object's `mesh` attribute.

            Raises:
                NotImplementedError: If the method is not implemented by a subclass.
            """
        pass

    @staticmethod
    @abstractmethod
    def transform_plain_slop(plain_mesh: trimesh.Trimesh, mesh: trimesh.Trimesh, settings: Settings, progress_callback: ProgressTracker):
        pass

    @staticmethod
    @abstractmethod
    def transform_smooth_surface(plain_mesh: trimesh.Trimesh, mesh: trimesh.Trimesh, settings: Settings, progress_callback: ProgressTracker):
        pass

    @staticmethod
    @abstractmethod
    def transform_avoid_overhangs(plain_mesh: trimesh.Trimesh, mesh: trimesh.Trimesh, settings: Settings, progress_callback: ProgressTracker):
        pass

    @staticmethod
    @abstractmethod
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
        pass

    @staticmethod
    @abstractmethod
    def split_mesh_on_edges_from_plain(plain_mesh: trimesh.Trimesh, mesh: trimesh.Trimesh, progress_callback=None):
        pass
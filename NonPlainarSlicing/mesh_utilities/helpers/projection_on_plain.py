import numpy as np
import trimesh




def distort_vertices_on_plain (plain_mesh: trimesh.Trimesh, vertices, progress_callback=None ):
    ray_origin = np.column_stack((vertices[:, 0], vertices[:, 1], np.full(len(vertices), 1000)))
    ray_direction = np.full((len(vertices), 3), (0, 0, -1))
    locations, index_ray, index_tri = plain_mesh.ray.intersects_location(ray_origin, ray_direction)
    print(len(locations), ":", len(vertices))
    # assert len(locations) == len(vertices)
    # vertices[:, 2] += locations[:, 2]
    vertices[index_ray, 2] += locations[:, 2]  # is saver but not necessary
    return None

def helper_distort_mesh_on_plain(plain_mesh: trimesh.Trimesh, mesh: trimesh.Trimesh , progress_callback=None):
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


    mesh_vertices = mesh.vertices
    distort_vertices_on_plain(plain_mesh,mesh_vertices, progress_callback )


    return None




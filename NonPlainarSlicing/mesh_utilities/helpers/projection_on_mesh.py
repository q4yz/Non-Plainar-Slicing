import numpy as np
import trimesh

from .smoothing import helper_smooth_plain_mesh


def get_lowest_ray_hits_array(locations: np.ndarray, index_ray: np.ndarray, total_rays: int) -> np.ndarray:
    """
    Returns an array of Z-values representing the lowest intersection for each ray.

    Args:
        locations (np.ndarray): (N, 3) array of intersection points.
        index_ray (np.ndarray): (N,) array of ray indices corresponding to `locations`.
        total_rays (int): Total number of rays that were cast.

    Returns:
        np.ndarray: (total_rays,) array of Z-values. Unhit rays will have np.inf.
    """
    z_hits = np.full(total_rays, np.inf)

    for i, ray_idx in enumerate(index_ray):
        z = locations[i, 2]
        if z < z_hits[ray_idx]:
            z_hits[ray_idx] = z

    return z_hits



def helper_transform_plain_slop(plain_mesh: trimesh.Trimesh , mesh: trimesh.Trimesh, progress_callback=None):
    k = 0.5
    for v in plain_mesh.vertices:
        v[2] = v[0] * k
    pass


def helper_transform_plain_after_top(plain_mesh: trimesh.Trimesh , mesh: trimesh.Trimesh, max_p: float, progress_callback=None):

    plain_vertices = plain_mesh.vertices

    ray_origin = np.column_stack(( plain_vertices[:, 0],  plain_vertices[:, 1], np.full(len( plain_vertices), 1000)))
    ray_direction = np.full((len( plain_vertices), 3), (0, 0, -1))

    locations, index_ray, index_tri = mesh.ray.intersects_location(ray_origin, ray_direction)

    locations[:,2] = - locations[:,2]
    z_hits = get_lowest_ray_hits_array(locations, index_ray, len(plain_vertices))
    z_hits = np.where(np.isinf(z_hits), 10000, z_hits)
    z_hits -= np.min(z_hits)


    plain_mesh.vertices[:, 2] = z_hits

    helper_smooth_plain_mesh(plain_mesh, max_p, progress_callback)



def helper_transform_plain_after_bottom(plain_mesh: trimesh.Trimesh , mesh: trimesh.Trimesh, max_p: float, progress_callback=None):

    plain_vertices = plain_mesh.vertices

    ray_origin = np.column_stack((plain_vertices[:, 0], plain_vertices[:, 1], np.full(len(plain_vertices), -1000)))
    ray_direction = np.full((len(plain_vertices), 3), (0, 0, 1))

    locations, index_ray, index_tri = mesh.ray.intersects_location(ray_origin, ray_direction)

    z_hits = get_lowest_ray_hits_array(locations, index_ray, len(plain_vertices))
    z_hits = np.where(np.isinf(z_hits), 10000.0, z_hits)
    z_hits = np.where(z_hits < 0.1, 0.0, z_hits)
    z_hits -= np.min(z_hits)

    plain_mesh.vertices[:, 2] = z_hits

    helper_smooth_plain_mesh(plain_mesh, max_p, progress_callback)




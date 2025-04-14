
import trimesh
import numpy as np

from .utils import check_for_z_zero
from .transformation import rotate_to_align
from ..globals import Glob


def multi_split(mesh: trimesh.Trimesh, normal, steps : np.array, track_progress: bool = True):
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
            track_progress (bool): If True, updates the global `progress2` variable to track progress
                                   (used for UI integration or logging). Default is True.

        Returns:
                trimesh.Trimesh: The resulting mesh after all slices and transformations.

        Notes:
                - Assumes the mesh contains only triangular faces.
                - Assumes that no vertex lies exactly on the Z=0 plane at any slicing step.
                - The `cut_mesh_on_z_zero` function is used to process intersecting faces during slicing.
                - The function is non-destructive: all transformations are reversed at the end.

        Example:
    """

    rotation_matrix : np.array =  rotate_to_align(normal, target=(0, 0, 1))
    mesh.apply_transform(rotation_matrix)

    applied_offset : float = 0.0
    

    Glob.initialize_progress_2(len(steps))
    for step in steps:
        # Translate the mesh by the step in the z direction

        if track_progress : Glob.progressed_2()

        step_translation = trimesh.transformations.translation_matrix([0, 0, -step -applied_offset ])
        applied_offset  = -step
        mesh.apply_transform(step_translation)

        # Split the faces on the z=0 plane
        mesh = cut_mesh_on_z_zero(mesh)




    translation_vector = [0, 0, -applied_offset ]
    translation_matrix = trimesh.transformations.translation_matrix(translation_vector)
    mesh.apply_transform(translation_matrix)

    inverse_rotation_matrix = np.linalg.inv(rotation_matrix)
    mesh.apply_transform(inverse_rotation_matrix)

    if track_progress : Glob.progress2 = 0

    return mesh


def invert_double_true(list_intersecting_faces, mask_vertices_above_plain):
    mask_single_value = np.full((len(list_intersecting_faces), 3), False)
    for i, f in enumerate(list_intersecting_faces):
        if np.sum(mask_vertices_above_plain[f]) == 1:
            mask_single_value[i] = [mask_vertices_above_plain[v] for v in f]
        else:
            mask_single_value[i] = [~mask_vertices_above_plain[v] for v in f]
    return mask_single_value

def bring_true_to_front(mask_single_value, list_intersecting_faces ):
    for i in range(mask_single_value.shape[0]):
        # Find the index of the first True value in the row
        true_index = np.argmax(mask_single_value[i])

        # If a True is found, rotate the row so that the True value comes to the front
        if true_index != 0:  # Only rotate if the first True is not already at the front
            mask_single_value[i] = np.roll(mask_single_value[i], -true_index)
            list_intersecting_faces[i] = np.roll(list_intersecting_faces[i], -true_index)
    return list_intersecting_faces


def cut_mesh_on_z_zero(mesh:trimesh.Trimesh) -> trimesh.Trimesh:
    """
        Cuts a 3D mesh along the Z=0 plane and reconstructs intersecting faces.

        This function separates a mesh into parts above and below the Z=0 plane by:
          - Identifying faces that intersect the Z=0 plane.
          - Calculating intersection points on the plane.
          - Reconstructing the intersecting faces using new vertices on the plane.
          - Returning a new mesh composed of both unchanged and reconstructed faces.

        Preconditions:
            - No vertices lie exactly on the Z=0 plane.
              Use `check_for_z_zero(vertices)` beforehand to verify.

        Parameters:
            mesh (trimesh.Trimesh): The input 3D mesh to be cut.

        Returns:
            trimesh.Trimesh: A new mesh with intersecting faces split along the Z=0 plane.

        Notes:
            - Faces that lie entirely on one side of the plane remain unchanged.
            - Faces that intersect the plane are split into three new faces using
              linear interpolation along the edges that cross Z=0.
            - This function assumes that only triangles are used (i.e., each face has 3 vertices).
    """

    old_v : np.array = mesh.vertices
    old_f : np.array = mesh.faces
    old_v = np.array(old_v)


    assert not check_for_z_zero(old_v) , "Point on Plain"

   
    mask_vertices_above_plain = old_v[:, 2] > 0

    mask_faces_above = np.all(mask_vertices_above_plain[old_f], axis=1)

    mask_vertices_below_plain = old_v[:, 2] < 0

    mask_faces_below = np.all(mask_vertices_below_plain[old_f], axis=1)
    
    mask_faces_non_intersecting = np.logical_or(mask_faces_above, mask_faces_below)

    list_unchanged_faces = old_f[mask_faces_non_intersecting]

    list_intersecting_faces = old_f[~mask_faces_non_intersecting]

    # Invert rows with exactly two `True` values
    mask_single_value = invert_double_true(list_intersecting_faces, mask_vertices_above_plain)


    # Rotate each row to move the first True to the beginning
    list_intersecting_faces = bring_true_to_front(mask_single_value, list_intersecting_faces)

    list_new_faces = np.full((len(list_intersecting_faces) * 3, 3), 0)

    list_new_vertices = np.full((len(list_intersecting_faces) * 2, 3), 0)
    list_new_vertices = np.vstack([old_v, list_new_faces])

    def find_intersection_on_z_plain(v1, v2):
        # Calculate t for the intersection on the z = 0 plane
        t = -v1[2] / (v2[2] - v1[2])
        # Calculate the intersection point v12
        v12 = v1 + t * (v2 - v1)
        return v12

    for i,f in enumerate(list_intersecting_faces):
        indexV1 = f[0]
        indexV2 = f[1]
        indexV3 = f[2]
        v1 = old_v[indexV1]
        v2 = old_v[indexV2]
        v3 = old_v[indexV3]
        indexV12 = i*2 + len(old_v)
        indexV13 = i*2 + 1 + len(old_v)
        v12 = find_intersection_on_z_plain(v1, v2)
        v13 = find_intersection_on_z_plain(v1, v3)

        list_new_vertices[indexV12] = v12
        list_new_vertices[indexV13] = v13

        list_new_faces[i * 3] = (indexV1,indexV12,indexV13)
        list_new_faces[i * 3 + 1] = (indexV13,indexV12,indexV2)
        list_new_faces[i * 3 + 2] = (indexV2,indexV3,indexV13)

    list_new_faces = np.vstack([list_unchanged_faces, list_new_faces])
    mesh_new = trimesh.Trimesh(vertices=list_new_vertices, faces=list_new_faces)

    return mesh_new








import trimesh
import numpy as np

def rotate_to_align(normal, target=(0, 0, 1)):
    """
    Create a rotation matrix to align the `normal` vector with the `target` vector.
    """
    normal = normal / np.linalg.norm(normal)
    target = np.array(target) / np.linalg.norm(target)
    axis = np.cross(normal, target)
    angle = np.arccos(np.dot(normal, target))
    if np.linalg.norm(axis) < 1e-6:  # If already aligned
        return np.eye(4)
    axis = axis / np.linalg.norm(axis)
    rotation_matrix = trimesh.transformations.rotation_matrix(angle, axis)
    return rotation_matrix

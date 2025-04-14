import trimesh
import numpy as np

def rotate_to_align(current:np.ndarray, target=(0, 0, 1)):
    """
    Create a rotation matrix to align the `current` vector with the `target` vector.

    This function computes the necessary rotation matrix that, when applied, will
    rotate the `current` vector to align with the `target` vector. The rotation is
    performed around the axis perpendicular to both vectors (the cross product),
    and the angle of rotation is the angle between the vectors.

    Parameters:
        current (np.ndarray): A 3D vector representing the current direction.
                               It should be a numpy array of shape (3,).
        target (tuple or np.ndarray): A 3D vector representing the target direction
                                      to which the `current` vector should be aligned.
                                      Default is (0, 0, 1), which aligns the vector with the Z-axis.

    Returns:
        np.ndarray: A 4x4 rotation matrix that can be applied to rotate the `current` vector
                    to align with the `target` vector. The matrix is in homogeneous coordinates.

    Notes:
        - If the `current` and `target` vectors are already aligned (i.e., they are parallel),
          the function returns the identity matrix.
        - The rotation matrix is computed using the Rodrigues' rotation formula.
    """

    normal = current / np.linalg.norm(current)
    target = np.array(target) / np.linalg.norm(target)
    axis = np.cross(normal, target)
    angle = np.arccos(np.dot(normal, target))
    if np.linalg.norm(axis) < 1e-6:  # If already aligned
        return np.eye(4)
    axis = axis / np.linalg.norm(axis)
    rotation_matrix = trimesh.transformations.rotation_matrix(angle, axis)
    return rotation_matrix

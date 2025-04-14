
import numpy as np

def check_for_z_zero(vertices: np.ndarray) -> bool:
    """
    Check if any vertices lie on the Z=0 plane.

    Parameters:
        vertices (np.ndarray): A NumPy array of shape (N, 3), where each row represents
                        a 3D vertex with x, y, z coordinates.

    Returns:
        bool: True if at least one vertex lies on the Z=0 plane, False otherwise.
    """
    return np.any(vertices[:, 2] == 0)
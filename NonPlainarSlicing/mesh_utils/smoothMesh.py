import trimesh
import numpy as np
from ..globals import Glob


def smooth_mesh(mesh: trimesh.Trimesh, angle: float, tol=1e-6) -> trimesh.Trimesh:
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
            mesh (trimesh.Trimesh): The input 3D mesh to be smoothed.
            angle (float): Maximum allowed angle (in degrees) between neighboring vertices.
            tol (float, optional): Tolerance for convergence. Iteration stops when max change < tol.

        Returns:
            trimesh.Trimesh: A new smoothed mesh with updated Z-coordinates.

        Notes:
            - Only Z-values are modified; X and Y remain unchanged.
            - This method assumes a progressive smoothing based on minimum vertex heights.
            - Global variable `glob.progress2` is updated during execution to track progress.
    """
    vertices = mesh.vertices.copy()
    faces = mesh.faces.copy()

    
    Glob.progress2 = 0
    change = np.inf
    count = 0

    while change > tol:
        prev_vertices = vertices.copy()
        # Process all vertices (possibly in a fixed order or via BFS)

        Glob.set_progress2(count / float(len(vertices)))

        for i in range(len(vertices)):

            
            # Here, you might use a fixed order rather than re-sorting every time.
            # Alternatively, you can structure your propagation differently.
            neighbors_faces = faces[np.any(faces == i, axis=1)]
            neighbors = np.unique(neighbors_faces.ravel())
            z_min_v = vertices[i]
            # Clamp neighbors above z_min + max_z_diff.
            vertices[neighbors, 2] = np.where(vertices[neighbors, 2] > z_min_v[2] + np.arctan(np.radians(angle)) * np.sqrt( np.square(vertices[neighbors, 0] - z_min_v[0]) + np.square(vertices[neighbors, 1] - z_min_v[1]) ), 
                                              z_min_v[2] + np.arctan(np.radians(angle)) * np.sqrt( np.square(vertices[neighbors, 0] - z_min_v[0]) + np.square(vertices[neighbors, 1] - z_min_v[1]) ),
                                              vertices[neighbors, 2])
        change = np.abs(vertices - prev_vertices).max()

        count_changed = np.sum(vertices[:,2] == prev_vertices[:,2])
        count = count_changed
        

        Glob.set_progress2(0)

    return trimesh.Trimesh(vertices=vertices, faces=faces)



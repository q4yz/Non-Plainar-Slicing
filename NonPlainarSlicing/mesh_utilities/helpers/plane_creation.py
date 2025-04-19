
import numpy as np
import trimesh

def helper_create_plane(boundingbox, resolution: float, padding: float = 1.015435) -> trimesh.Trimesh:
    """
    Generate a triangular mesh in the XY plane, covering the bounding box
    with added padding to avoid coinciding with any other mesh vertices.

    The mesh is stored in `self.mesh` as a trimesh.Trimesh object.
    """
    v_min, v_max = boundingbox
    x_min, y_min, _ = v_min
    x_max, y_max, _ = v_max

    # Padding to reduce vertex overlap with other geometry

    x_min -= padding
    x_max += padding
    y_min -= padding
    y_max += padding

    # Number of grid points (vertices)
    x_steps = int((x_max - x_min) * resolution)
    y_steps = int((y_max - y_min) * resolution)

    # Generate grid points in XY
    x = np.linspace(x_min, x_max, x_steps)
    y = np.linspace(y_min, y_max, y_steps)
    xx, yy = np.meshgrid(x, y)

    # Flatten and combine into (N, 3) vertex array (Z=0)
    vertices = np.column_stack((xx.ravel(), yy.ravel(), np.zeros_like(xx.ravel())))

    # Create triangle faces
    faces = []
    for i in range(y_steps - 1):
        for j in range(x_steps - 1):
            idx = i * x_steps + j
            faces.append([idx, idx + x_steps, idx + x_steps + 1])
            faces.append([idx, idx + x_steps + 1, idx + 1])

    # Build mesh
    return trimesh.Trimesh(vertices=vertices, faces=np.array(faces), process=False)

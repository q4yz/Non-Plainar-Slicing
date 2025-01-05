import trimesh
import numpy as np
from collections import deque


def smoothMesh( mesh: trimesh.Trimesh, max_z_diff:float ) -> trimesh.Trimesh:
        """
        Flattens a mesh plane by adjusting vertex z-values such that 
        the difference between neighboring vertices is at most `max_z_diff`,
        starting from the minimum z-value.

        Args:
            mesh (trimesh.Trimesh): The input mesh.
            max_z_diff (float): Maximum allowed z-difference between neighbors.

        Returns:
            trimesh.Trimesh: The flattened mesh.
        """
        vertices = mesh.vertices.copy()
        edges = mesh.edges_unique
        # Find the vertex with the minimum z-value
        min_z_index = np.argmin(vertices[:, 2])
        visited = np.zeros(len(vertices), dtype=bool)
        queue = deque([min_z_index])

        while queue:
            current = queue.popleft()
            visited[current] = True
            current_z = vertices[current, 2]

            neighbors = edges[np.any(edges == current, axis=1)].flatten()
            neighbors = neighbors[neighbors != current]  # Remove self-loop

            for neighbor in neighbors:
                if not visited[neighbor]:
                    neighbor_z = vertices[neighbor, 2]

                    if neighbor_z > current_z + max_z_diff:
                        vertices[neighbor, 2] = current_z + max_z_diff
                    elif neighbor_z < current_z - max_z_diff:
                        vertices[neighbor, 2] = current_z - max_z_diff

                    queue.append(neighbor)

        
        flattened_mesh = trimesh.Trimesh(vertices=vertices, faces=mesh.faces)
        return flattened_mesh
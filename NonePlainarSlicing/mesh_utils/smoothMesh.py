import trimesh
import numpy as np
from collections import deque


#def smoothMesh( mesh: trimesh.Trimesh, max_z_diff:float ) -> trimesh.Trimesh:
#        """
#        Flattens a mesh plane by adjusting vertex z-values such that 
#        the difference between neighboring vertices is at most `max_z_diff`,
#        starting from the minimum z-value.

#        Args:
#            mesh (trimesh.Trimesh): The input mesh.
#            max_z_diff (float): Maximum allowed z-difference between neighbors.

#        Returns:
#            trimesh.Trimesh: The flattened mesh.
#        """
#        vertices = mesh.vertices.copy()
#        edges = mesh.edges_unique
#        # Find the vertex with the minimum z-value
#        min_z_index = np.argmin(vertices[:, 2])
#        visited = np.zeros(len(vertices), dtype=bool)
#        queue = deque([min_z_index])

#        while queue:
#            current = queue.popleft()
#            visited[current] = True
#            current_z = vertices[current, 2]

#            neighbors = edges[np.any(edges == current, axis=1)].flatten()
#            neighbors = neighbors[neighbors != current]  # Remove self-loop

#            for neighbor in neighbors:
#                if not visited[neighbor]:
#                    neighbor_z = vertices[neighbor, 2]

#                    if neighbor_z > current_z + max_z_diff:
#                        vertices[neighbor, 2] = current_z + max_z_diff
#                    elif neighbor_z < current_z - max_z_diff:
#                        vertices[neighbor, 2] = current_z - max_z_diff

#                    queue.append(neighbor)

        
#        flattened_mesh = trimesh.Trimesh(vertices=vertices, faces=mesh.faces)
#        return flattened_mesh

def smoothMesh( mesh: trimesh.Trimesh, max_z_diff:float ) -> trimesh.Trimesh:

    vertices = mesh.vertices
    faces = mesh.faces
    mask_vertices = np.full(len(vertices), True, dtype=bool)

    
    sortedIndexOfVertices = np.argsort(vertices[:,2])

    currentN = 0
    while currentN < len(vertices):

        sortedIndexOfVertices =  np.argsort(vertices[:,2])

        
        first_z_min =  vertices[sortedIndexOfVertices[currentN]][2]
 
       
       
        while True:

            z_min = vertices[sortedIndexOfVertices[currentN],2]
            
            if z_min > first_z_min + max_z_diff:
                break

            filtered_verticesIndex = faces[np.any(faces == sortedIndexOfVertices[currentN], axis=1)]


            filtered_verticesIndex = np.unique(filtered_verticesIndex.ravel())
       
            vertices[filtered_verticesIndex , 2] = np.where(vertices[filtered_verticesIndex, 2] > z_min + max_z_diff,  z_min + max_z_diff, vertices[filtered_verticesIndex, 2]  )

            currentN += 1
            if currentN == len(vertices):
                break
    
    flattened_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    return flattened_mesh




v = [(0,0,1),(1,0,1),(2,0,50),
     (0,1,1),(1,1,1),(2,1,1000),
     (0,2,1),(1,2,1),(2,2,-10)]

f = [(0,1,3),(3,4,1),(1,2,4),(4,5,2), (3,4,6), (6,7,4), (4,5,7), (7,8,5)]

flattened_mesh = trimesh.Trimesh(vertices=v, faces=f)


mesh = smoothMesh(flattened_mesh, 2)

print(mesh.vertices)
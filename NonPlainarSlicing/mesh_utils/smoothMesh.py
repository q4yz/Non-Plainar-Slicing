import trimesh
import numpy as np
import globals

#def smoothMesh(mesh: trimesh.Trimesh, max_z_diff: float, tol=1e-6) -> trimesh.Trimesh:
#    vertices = mesh.vertices.copy()
#    faces = mesh.faces.copy()
    
#    change = np.inf
#    while change > tol:
#        prev_vertices = vertices.copy()
#        # Process all vertices (possibly in a fixed order or via BFS)
#        for i in range(len(vertices)):
#            # Here, you might use a fixed order rather than re-sorting every time.
#            # Alternatively, you can structure your propagation differently.
#            neighbors_faces = faces[np.any(faces == i, axis=1)]
#            neighbors = np.unique(neighbors_faces.ravel())
#            z_min = vertices[i, 2]
#            # Clamp neighbors above z_min + max_z_diff.
#            vertices[neighbors, 2] = np.where(
#                vertices[neighbors, 2] > z_min + max_z_diff,
#                z_min + max_z_diff,
#                vertices[neighbors, 2]
#            )
#        change = np.abs(vertices - prev_vertices).max()
#    return trimesh.Trimesh(vertices=vertices, faces=faces)



def smoothMesh(mesh: trimesh.Trimesh, angle: float, tol=1e-6) -> trimesh.Trimesh:
    vertices = mesh.vertices.copy()
    faces = mesh.faces.copy()

    
    globals.progress2 = 0
    change = np.inf
    count = 0
    max_count = len(vertices)
    while change > tol:
        prev_vertices = vertices.copy()
        # Process all vertices (possibly in a fixed order or via BFS)
        globals.progress2 = count / float(max_count)
        

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

        count_cnage = np.sum(vertices[:,2] == prev_vertices[:,2])
        count = count_cnage
        print(globals.progress2)
        globals.progress2 = 0

    return trimesh.Trimesh(vertices=vertices, faces=faces)



# ####################### old Version ###############################
#def smoothMesh( mesh: trimesh.Trimesh, max_z_diff:float ) -> trimesh.Trimesh:

#    vertices = mesh.vertices
#    faces = mesh.faces


#    #mask_vertices = np.full(len(vertices), True, dtype=bool)
#    #sortedIndexOfVertices = np.argsort(vertices[:,2])

#    currentN = 0
#    while currentN < len(vertices):

#        sortedIndexOfVertices =  np.argsort(vertices[:,2])

        
 
       
       
       

#        z_min = vertices[sortedIndexOfVertices[currentN],2]
            
  

#        filtered_verticesIndex = faces[np.any(faces == sortedIndexOfVertices[currentN], axis=1)]


#        filtered_verticesIndex = np.unique(filtered_verticesIndex.ravel())
       
#        vertices[filtered_verticesIndex , 2] = np.where(vertices[filtered_verticesIndex, 2] > z_min + max_z_diff,  z_min + max_z_diff, vertices[filtered_verticesIndex, 2]  )

#        currentN += 1

#    flattened_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
#    return flattened_mesh

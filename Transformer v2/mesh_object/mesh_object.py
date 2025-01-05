import trimesh



import mesh_utils
from .transformer_plane import TransformerPlain

import numpy as np
import logging
from Constants import *

from settings import *






class MeshObject():
    """
    This class Saves the mesh object and the transformer.
    This class provids operations between them

    path: the path to the OBJ file
    mesh: trimesh.mesh object with the obj mesh in it
    transformer : trimesh.mesh obect with a plain in it usd to transform obj mesh
    """
    mesh = None
    transformerPlain = None
    viewer = None

    progress = 0

    gcode = None
    path = None
    
   
    def __init__(self, **parameters) -> None:
        """
        Initialize the ObjectToSlice object.

        Parameters:
        ----------
        **parameters : dict
        - path(str): Path to OBJ File
        or
        - v(float[][]): List of vertices
        - f(int[][]): List of faces. Each faces contains three vertices Indexes 

         Returns:
        -------
        None
        """

        self.viewer = parameters["viewer"]

        if 'path' in parameters:
            self.path = parameters['path']
            self.mesh = trimesh.load(self.path)

        elif 'v' in parameters and 'f' in parameters:
            v = parameters['v']
            f = parameters['f']
            self.mesh = trimesh.Trimesh(vertices=v, faces=f)
        else:
            raise ValueError("Either 'path' or both 'v' and 'f' must be provided.")

        v_min, v_max = self.mesh.bounding_box.bounds

        self.mesh.apply_translation([-v_min[0] -(v_max[0]-v_min[0])/2,-v_min[1] -(v_max[1]-v_min[1] )/2 ,  -v_min[2] ])
        print(settings)
        distortionResolution = settings['DistortionResolution']
        
        
        

       

        self.transformerPlain = TransformerPlain(self.mesh.bounding_box.bounds,distortionResolution,self.viewer)


        self.viewer.view_obj(self.mesh)
        self.viewer.view_transformer(self.transformerPlain.mesh)
        self.viewer.canvas.draw()
        

    def splitMeshEdageOnTrans(self):
        """
        cutOnV adds vertices to mesh on each uniq x and y from Trasformer mesh
         Parameters:
        ----------
        None

        Returns:
        -------
        None
        """

        mesh = self.mesh

        x_coords = self.transformerPlain.mesh.vertices[:, 0]  # Get the first column (x-coordinates)
        y_coords = self.transformerPlain.mesh.vertices[:, 1]  # Get the first column (x-coordinates)
        
        unique_x_coords = np.unique(x_coords)
        normal = [1, 0, 0]        
        unique_x_coords = [x + 0.00001 for x in unique_x_coords]
        mesh = mesh_utils.multisplit(mesh, normal, unique_x_coords)

        unique_y_coords = np.unique(y_coords)
        normal = [0, 1, 0]        
        unique_y_coords = [y + 0.0001 for y in unique_y_coords]
        mesh = mesh_utils.multisplit(mesh, normal, unique_y_coords)
       
        normal = [1, 1, 0]        
        unique_xy_coords = [x*2**(0.5) + 0.000001 for x in unique_x_coords]
        self.mesh = mesh_utils.multisplit(mesh, normal, unique_xy_coords)

        self.viewer.view_obj(self.mesh)
        self.viewer.canvas.draw()

    def distort(self):
        mesh = self.mesh
        v = mesh.vertices
        locations, index_ray = self.distortOnTrans(v)
       
        v[index_ray, 2] = v[index_ray, 2] +  locations[:, 2]
        self.viewer.view_obj( self.mesh)
        self.viewer.canvas.draw()
    def distortOnTrans(self, v):
        
        transformer_mesh = self.transformerPlain.mesh
        

        ray_origin = np.column_stack((v[:, 0], v[:, 1], np.full(len(v), 1000)))
        ray_direction = np.full((len(v),3), (0, 0, -1))
        locations, index_ray , index_tri  = transformer_mesh.ray.intersects_location(ray_origin, ray_direction)

        return locations, index_ray 
        

    def xSlop(self):
        k = 0.5
        transMesh = self.transformerPlain.mesh
        bounding_box = transMesh.bounds
       
        x_min = bounding_box[0][0]  
        for v in transMesh.vertices:
                v[2] = v[0] * k  
            
        self.viewer.view_transformer(transMesh)
        self.viewer.canvas.draw()
   
    def flattop(self):
        print("flaten")
        
        transMesh = self.transformerPlain.mesh
        v =  transMesh.vertices
        
        ray_origin = np.column_stack((v[:, 0], v[:, 1], np.full(len(v), 1000)))
        ray_direction = np.full((len(v),3), (0, 0, -1))

        locations, index_ray , index_tri  = self.mesh.ray.intersects_location(ray_origin, ray_direction)

        #mask = np.diff(index_ray, append=index_ray[-1] + 1) != 0

        unique_indices = np.unique(index_ray)
        mask = np.full(len(locations), False)
        for unique_index in unique_indices:
            maskSub = index_ray == unique_index
            subset = locations[maskSub]
            # Get the local index of the max Z value
            local_max_index = np.argmax(subset[:, 2])
            # Map the local index to the global index
            global_max_index = np.where(maskSub)[0][local_max_index]
            # Set the corresponding global index in the mask to True
            mask[global_max_index] = True

        #mask = np.diff(index_ray, prepend=index_ray[0] - 1) != 0


        index_ray = index_ray[mask]
        locations = locations[mask]
        print(locations)

        zDefault = np.full(len(v), 10000)
        v[:, 2] = zDefault
        v[index_ray, 2] = -locations[:, 2]

        zMin = np.min( v[:, 2])
        v[:, 2] = v[:, 2] - zMin

        distortionResolution = settings['DistortionResolution']
        maxP = settings['Max P']
        maxP_radians = np.radians(maxP)
        k = np.arctan(maxP_radians) / distortionResolution

        transMesh = mesh_utils.smoothMesh(transMesh, k)
        self.transformerPlain.mesh = transMesh
        
        self.viewer.view_transformer(transMesh)
        self.viewer.canvas.draw()


    def noSupport(self):
        transMesh = self.transformerPlain.mesh
        v =  transMesh.vertices
        
        ray_origin = np.column_stack((v[:, 0], v[:, 1], np.full(len(v), -1000)))
        ray_direction = np.full((len(v),3), (0, 0, 1))

        locations, index_ray , index_tri  = self.mesh.ray.intersects_location(ray_origin, ray_direction)
       
        zDefault = np.full(len(v), 10000)

        # Store results
        
        unique_indices = np.unique(index_ray)
        mask = np.full(len(locations), False)

        for unique_index in unique_indices:
            maskSub = index_ray == unique_index
            subset = locations[maskSub]
            local_min_index = np.argmin(subset[:, 2])
            global_min_index = np.where(maskSub)[0][local_min_index]
            mask[global_min_index] = True

        index_ray = index_ray[mask]
        locations = locations[mask]

        v[:, 2] = zDefault
        v[index_ray, 2] = locations[:, 2]

        zMin = np.min( v[:, 2])
        v[:, 2] = v[:, 2] - zMin

        distortionResolution = settings['DistortionResolution']
        maxP = settings['Max P']
        maxP_radians = np.radians(maxP)
        k = np.arctan(maxP_radians) / distortionResolution

        transMesh = mesh_utils.smoothMesh(transMesh, k)
        self.transformerPlain.mesh = transMesh

        self.viewer.view_transformer(transMesh)
        self.viewer.canvas.draw()


     

import trimesh
import pyvista as pv
from tkinter import messagebox
from PyQt5.QtCore import QTimer
import mesh_utils
from .transformer_plane import TransformerPlain
from PyQt5.QtCore import QMetaObject, Qt
import numpy as np
import globals



   

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


    gcode = None
    path = None

    #maxP = None
    #distortionResolution = None
    
   
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

       

        if 'path' in parameters:
            self.path = parameters['path']
            self.mesh = trimesh.load(self.path)

        elif 'v' in parameters and 'f' in parameters:
            v = parameters['v']
            f = parameters['f']
            self.mesh = trimesh.Trimesh(vertices=v, faces=f)
        else:
            raise ValueError("Either 'path' or both 'v' and 'f' must be provided.")

        self.shiftToCenter()

       
    def shiftToCenter(self):
        v_min, v_max = self.mesh.bounding_box.bounds

        self.mesh.apply_translation([-v_min[0] -(v_max[0]-v_min[0])/2,-v_min[1] -(v_max[1]-v_min[1] )/2 ,  -v_min[2] ])
        
        
        
    def createTransformerPlain(self, resolution, maxP):
        self.transformerPlain = TransformerPlain(self.mesh.bounding_box.bounds,resolution,maxP)



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
        self.mesh = mesh_utils.multisplit(mesh, normal, unique_y_coords)



    def distort(self):
        mesh = self.mesh
        v = mesh.vertices
        locations, index_ray = self.distortOnTrans(v)
       
        v[index_ray, 2] = v[index_ray, 2] +  locations[:, 2]



    def distortOnTrans(self, v):
        
        transformer_mesh = self.transformerPlain.mesh
        

        ray_origin = np.column_stack((v[:, 0], v[:, 1], np.full(len(v), 1000)))
        ray_direction = np.full((len(v),3), (0, 0, -1))
        locations, index_ray , index_tri  = transformer_mesh.ray.intersects_location(ray_origin, ray_direction)

        return locations, index_ray 
        

    def xSlop(self):
        k = 0.5
        transMesh = self.transformerPlain.mesh
        
        for v in transMesh.vertices:
                v[2] = v[0] * k  
            

   
    def flattop(self):
        
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
            
            local_max_index = np.argmax(subset[:, 2])
            
            global_max_index = np.where(maskSub)[0][local_max_index]
            
            mask[global_max_index] = True

        #mask = np.diff(index_ray, prepend=index_ray[0] - 1) != 0


        index_ray = index_ray[mask]
        locations = locations[mask]
        

        
        if locations.size != 0:
            
            v[:, 2] = np.full(len(v), 10000)
            v[index_ray, 2] = -locations[:, 2]
        else:
            messagebox.showinfo("Warning", "Resultion of distortionplain is to low!")

        zMin = np.min( v[:, 2])
        v[:, 2] = v[:, 2] - zMin
        resolution = self.transformerPlain.resolution



        maxP = self.transformerPlain.maxP
        maxP_radians = np.radians(maxP)
        k = np.arctan(maxP_radians) / resolution

        transMesh = mesh_utils.smoothMesh(transMesh, maxP)
        self.transformerPlain.mesh = transMesh
        


    def noSupport(self):
        transMesh = self.transformerPlain.mesh
        v =  transMesh.vertices
        
        ray_origin = np.column_stack((v[:, 0], v[:, 1], np.full(len(v), -1000)))
        ray_direction = np.full((len(v),3), (0, 0, 1))

        locations, index_ray , index_tri  = self.mesh.ray.intersects_location(ray_origin, ray_direction)
       
        zDefault = np.full(len(v), 10000)
        
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
        v[:, 2] =np.where(v[:, 2] < 0.1, 0, 10000 ) 

        zMin = np.min( v[:, 2])
        v[:, 2] = v[:, 2] - zMin

        resolution = self.transformerPlain.resolution
        maxP = self.transformerPlain.maxP
        maxP_radians = np.radians(maxP)
        k = np.arctan(maxP_radians) / resolution

        transMesh = mesh_utils.smoothMesh(transMesh, maxP)
        self.transformerPlain.mesh = transMesh



     
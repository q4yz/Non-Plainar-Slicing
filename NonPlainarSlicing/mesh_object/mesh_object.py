
import trimesh
import pyvista as pv
from tkinter import messagebox
from PyQt5.QtCore import QTimer

from .transformer_plane import TransformerPlain
from PyQt5.QtCore import QMetaObject, Qt
import numpy as np

import NonPlainarSlicing.mesh_utils as mesh_utils
from NonPlainarSlicing.mesh_utils import *
#from . import mesh_utils as mesh_utils

class MeshObject:
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
            raise ValueError("Either 'path' or both ('v' and 'f') must be provided.")

        self.shift_to_center()

       
    def shift_to_center(self):

        """
            Translates the mesh so that it is centered around the origin in the XY plane
            and aligned to the base (z=0) along the Z-axis.

            This method calculates the bounding box of the mesh and applies a translation
            such that the mesh is centered in the X and Y directions and its lowest Z
            point is moved to zero.

            Returns:
                None: The mesh is modified in-place by translating its vertices.

            Notes:
                - Assumes `self.mesh` has a `bounding_box` with `bounds` that return a
                  tuple of two points: the minimum and maximum XYZ coordinates.
                - Also assumes `self.mesh` supports the `apply_translation` method.
        """
        v_min, v_max = self.mesh.bounding_box.bounds

        self.mesh.apply_translation([-v_min[0] -(v_max[0]-v_min[0])/2,-v_min[1] -(v_max[1]-v_min[1] )/2 ,  -v_min[2] ])

        
    def create_transformer_plain(self, resolution, maxP):
        self.transformerPlain = TransformerPlain(self.mesh.bounding_box.bounds,resolution,maxP)



    def split_mesh_edge_on_trans(self):
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
        mesh = mesh_utils.multi_split(mesh, normal, unique_x_coords)



        unique_y_coords = np.unique(y_coords)
        normal = [0, 1, 0]        
        unique_y_coords = [y + 0.0001 for y in unique_y_coords]
        self.mesh = mesh_utils.multi_split(mesh, normal, unique_y_coords)



    def distort(self) -> None:
        """
            Applies a distortion effect to the mesh by modifying the z-coordinate of all vertices.

            This method retrieves the vertices of the mesh and identifies a subset of them using
            the `distort_on_trans` method. It then adds a distortion value to the z-coordinate
            of the selected vertices based on the results returned by `distort_on_trans`.

            Returns:
                None: This method modifies the mesh in-place and does not return a value.

            Notes:
                - `self.mesh` must have a `vertices` attribute that supports indexing and assignment.
                - `distort_on_trans(vertices)` should return:
                    - `locations`: A NumPy array of shape (N, 3) with distortion values.
                    - `index_ray`: An array of indices indicating which vertices to distort.
        """
        mesh = self.mesh
        v = mesh.vertices
        locations, index_ray = self.distort_on_trans(v)
       
        v[index_ray, 2] = v[index_ray, 2] + locations[:, 2]



    def distort_on_trans(self, v):
        """
            Casts vertical rays from above each vertex to detect intersections with the transformer mesh.

            For each vertex in `v`, this method casts a ray starting from a high Z-value (z=1000),
            pointing straight downward (negative Z-direction). It checks for intersections between
            these rays and the surface of the `transformerPlain` mesh, and returns the locations
            and corresponding indices of intersecting rays.

            Args:
                v (np.ndarray): An (N, 3) array of vertex positions (X, Y, Z) from the main mesh.

            Returns:
                tuple:
                    - locations (np.ndarray): An (M, 3) array of intersection points in 3D space.
                    - index_ray (np.ndarray): An array of indices into `v`, indicating which rays (vertices) had intersections.

            Notes:
                - This method assumes `self.transformerPlain.mesh` has a `ray.intersects_location` method.
                - Rays are cast vertically downward from z=1000 to detect intersections.
                - Only rays that intersect the transformer mesh are included in the output.
            """
        
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
        
        trans_mesh = self.transformerPlain.mesh
        v =  trans_mesh.vertices
        
        ray_origin = np.column_stack((v[:, 0], v[:, 1], np.full(len(v), 1000)))
        ray_direction = np.full((len(v),3), (0, 0, -1))

        locations, index_ray , index_tri  = self.mesh.ray.intersects_location(ray_origin, ray_direction)

        #mask = np.diff(index_ray, append=index_ray[-1] + 1) != 0

        unique_indices = np.unique(index_ray)
        mask = np.full(len(locations), False)
        for unique_index in unique_indices:
            mask_sub = index_ray == unique_index
            subset = locations[mask_sub]
            
            local_max_index = np.argmax(subset[:, 2])
            
            global_max_index = np.where(mask_sub)[0][local_max_index]
            
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

        trans_mesh = mesh_utils.smooth_mesh(trans_mesh, maxP)
        self.transformerPlain.mesh = trans_mesh
        


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

        transMesh = mesh_utils.smooth_mesh(transMesh, maxP)
        self.transformerPlain.mesh = transMesh



     
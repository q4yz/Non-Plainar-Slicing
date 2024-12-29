import trimesh



import mesh_utils
#from Split import *  

import numpy as np
import logging
from Constants import *

class TransformerPlain():

    mesh = None
    boundingbox = None
    resolution = None

    viewer = None

    def __init__(self, boundingbox, resolution,viewer) -> None:
        """
        Initialize the YourClass object.

        Parameters:
        ----------
        boundingbox : tuple or list  (x_min, y_min, x_max, y_max)
        resolution(int); Number of Points in one Axis 

        Returns:
        -------
        None
        """
        self.viewer = viewer
        self.boundingbox = boundingbox
        self.resolution = resolution
        self.create_plane()

    def create_plane(self) ->None:
        """
        Create a trimesh object representing a plane and saves it as self.mesh
        Parameters:
        ----------
        None

        Returns:
        -------
        None
        """
        x_min, y_min, x_max, y_max = self.boundingbox

        # Generate grid of vertices in the XY plane, with Z=0
        x_coords = [x_min + i * (x_max - x_min) / (self.resolution - 1) for i in range(self.resolution)]
        y_coords = [y_min + i * (y_max - y_min) / (self.resolution - 1) for i in range(self.resolution)]
        
        vertices = []
        for y in y_coords:
            for x in x_coords:
                vertices.append([x, y, 0])  # Z coordinate is 0 for all vertices (plane in XY)

        # Create faces by connecting vertices (assume quadrilateral faces split into two triangles)
        faces = []
        for i in range(self.resolution - 1):
            for j in range(self.resolution - 1):
                # Get the index of the current vertex and its neighbors in the grid
                top_left = i * self.resolution + j
                top_right = top_left + 1
                bottom_left = (i + 1) * self.resolution + j
                bottom_right = bottom_left + 1

                # Create two triangles (top-left, bottom-left, bottom-right) and (top-left, bottom-right, top-right)
                faces.append([top_left, bottom_left, bottom_right])
                faces.append([top_left, bottom_right, top_right])

        # Create the trimesh object from vertices and faces
        self.mesh = trimesh.Trimesh(vertices=vertices, faces=faces)   
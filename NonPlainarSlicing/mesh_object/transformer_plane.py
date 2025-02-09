import trimesh




import numpy as np
import logging


class TransformerPlain():

    mesh = None
    boundingbox = None
    resolution = None




    def __init__(self, boundingbox, resolution,maxP) -> None:
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

        self.boundingbox = boundingbox
        self.resolution = resolution
        self.maxP = maxP
        self.create_plane()

    def create_plane(self) -> None:
        """
        Create a trimesh object representing a plane and saves it as self.mesh
        Parameters:
        ----------
        None

        Returns:
        -------
        None
        """
        v_min, v_max = self.boundingbox
        x_min, y_min, _ = v_min
        x_max, y_max, _ = v_max

        # Calculate the number of steps in each direction
        x_steps = int((x_max - x_min) * self.resolution)
        y_steps = int((y_max - y_min) * self.resolution)

        # Generate grid of vertices in the XY plane, with Z=0
        x_coords = np.linspace(x_min -1.015435, x_max +1.015435, x_steps)
        y_coords = np.linspace(y_min -1.015435, y_max +1.015435, y_steps)

        vertices = []
        for y in y_coords:
            for x in x_coords:
                vertices.append([x, y, 0])  # Z coordinate is 0 for all vertices (plane in XY)

        # Create faces by connecting vertices (assume quadrilateral faces split into two triangles)
        faces = []
        for i in range(y_steps - 1):
            for j in range(x_steps - 1):
                # Get the index of the current vertex and its neighbors in the grid
                top_left = i * x_steps + j
                top_right = top_left + 1
                bottom_left = (i + 1) * x_steps + j
                bottom_right = bottom_left + 1

                # Create two triangles (top-left, bottom-left, bottom-right) and (top-left, bottom-right, top-right)
                faces.append([top_left, bottom_left, bottom_right])
                faces.append([top_left, bottom_right, top_right])

        # Create the trimesh object from vertices and faces
        self.mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

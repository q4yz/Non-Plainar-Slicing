from pickle import OBJ
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import cm
from matplotlib.ticker import LinearLocator
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
#import globals

class CanvisViewer():
    """
    saves the objects to be viewed

    """

    fig = None
    ax = None
    canvas = None

    Plotet_objecs = {} #Dict

    def __init__(self,**parameters):
        self.fig, self.ax = plt.subplots(subplot_kw={"projection": "3d"})
        ax = self.ax


        #self.view_bed()
        pass
       
    def view_bed(self):
         # ------------------------ print bed ------------------------------------------
        
        # Make data.
        X = np.arange(-25, 25, 5)
        Y = np.arange(-25, 25, 5)

        # Create a meshgrid for X and Y
        X, Y = np.meshgrid(X, Y)

        # Set Z to 0 to create a flat plane
        Z = np.zeros_like(X)

        # Plot the surface.
        bed = self.ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                               linewidth=2, alpha = 0.3,antialiased=False)

        self.Plotet_objecs['bed'] = bed



    def view_transformer(self, meshIn):
 
        mesh = self.view_mesh(meshIn, 'red')
           
        self.Plotet_objecs['trans_line'] = mesh['line']
        self.Plotet_objecs['trans_f'] =  mesh['f']

        self.plot()


    def view_obj(self, meshIn):

        mesh = self.view_mesh(meshIn, 'cyan')
           
        #self.Plotet_objecs['obj_line'] = mesh['line']
        self.Plotet_objecs['obj_f'] =  mesh['f']

        self.plot()

    def view_mesh(self, meshIn, color):   #alpha = 0.9 jetzt alle gleich transparent
         # ------------------------ Mesh ------------------------------------------
        vertices = meshIn.vertices
        faces = meshIn.faces
        
        mesh_f = Poly3DCollection([[vertices[vert] for vert in face] for face in faces],alpha = 1, facecolor=color)

        lines = []  

        for face in faces:
            for i in range(len(face)):
                start_vert = vertices[face[i]]
                end_vert = vertices[face[(i + 1) % len(face)]]  # Next vertex (wraps around)
                lines.append([start_vert, end_vert])  # Store each line segment as a pair of points

        ## Create Line3DCollection
        obj_line = Line3DCollection(lines, color='k')  # Create a collection with black color

        return {'f':mesh_f, 'line':obj_line }

    def plot(self):
                
        ax = self.ax
        ax.clear() 

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        if 'obj_line' in self.Plotet_objecs:
            ax.add_collection3d(self.Plotet_objecs['obj_line'])

        if 'obj_f' in self.Plotet_objecs:
            ax.add_collection3d(self.Plotet_objecs['obj_f'])

        if 'trans_line' in self.Plotet_objecs:
            ax.add_collection3d(self.Plotet_objecs['trans_line'])

        if 'trans_f' in self.Plotet_objecs:
            ax.add_collection3d(self.Plotet_objecs['trans_f'])

        #if 'bed' in self.Plotet_objecs:
        #    ax.add_collection3d(self.Plotet_objecs['bed'])
        ax.set_xlim(-30, 30)
        ax.set_ylim(-30, 30)
        ax.set_zlim(-5, 55)

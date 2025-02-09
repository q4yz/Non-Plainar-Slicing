import sys
import pyvista as pv
from pyvistaqt import QtInteractor
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QProgressBar
import os
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal, QObject
import threading  



#from canvisViewer import CanvisViewer
#import mesh_object

from ViewerMethoden import *
from settings import *

class MainWindow(QtWidgets.QMainWindow,ViewerMethoden):





    #self.root = tk.Tk()
    #self.root.wm_title("None Plainar Slicer")
    #self.root.geometry("1200x1000")
    #icon_path = os.path.abspath("icon.ico")
    #self.root.iconbitmap(icon_path)
        
    #self.meshObject: mesh_object.MeshObject = None 
    

    #self._create_top_frame()
    #self._create_middle_frame()
    #self._create_bottom_frame()







    update_mesh_signal = pyqtSignal(object, str, str)


    def __init__(self, parent=None):
        super().__init__(parent)

        self.update_mesh_signal.connect(self.update_mesh)

        self.setWindowTitle("NonPlainarSlicer")
        self.resize(800, 600)

        icon_path = os.path.abspath("icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowIcon(QIcon('path_to_your_icon.ico'))  # Provide your icon path here

        # Create a central widget with a vertical layout.
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        vlayout = QtWidgets.QVBoxLayout(central_widget)

        # Add a label at the top.
        self.label = QtWidgets.QLabel("PyVista 3D Viewer Embedded in PyQt5", self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        vlayout.addWidget(self.label)

        layout_dev_op_button = QtWidgets.QHBoxLayout()
        vlayout.addLayout(layout_dev_op_button)


        self.load_stl_button = QtWidgets.QPushButton("Load file")
        self.load_stl_button.clicked.connect(self.load_obj)
        layout_dev_op_button.addWidget(self.load_stl_button)

        self.split_mesh_button = QtWidgets.QPushButton("Split Mesh")
        self.split_mesh_button.clicked.connect(self.split)
        layout_dev_op_button.addWidget(self.split_mesh_button)

        self.trans_plain_button = QtWidgets.QPushButton("Transform Plain")
        self.trans_plain_button.clicked.connect(self.transTransformerPlain)
        layout_dev_op_button.addWidget(self.trans_plain_button)

        self.distort_mesh_button = QtWidgets.QPushButton("Distort Mesh")
        self.distort_mesh_button.clicked.connect(self.distort)
        layout_dev_op_button.addWidget(self.distort_mesh_button)

        self.export_mesh_button = QtWidgets.QPushButton("Export Mesh")
        self.export_mesh_button.clicked.connect(self.exportMesh)
        layout_dev_op_button.addWidget(self.export_mesh_button)

        self.import_gcode_button = QtWidgets.QPushButton("Import Gcode")
        self.import_gcode_button.clicked.connect(self.importGcode)
        layout_dev_op_button.addWidget(self.import_gcode_button)

        self.save_code_button = QtWidgets.QPushButton("Save Gcode")
        self.save_code_button.clicked.connect(self.exportGcode)
        layout_dev_op_button.addWidget(self.save_code_button)


        layout_top_button = QtWidgets.QHBoxLayout()
        vlayout.addLayout(layout_top_button)

        layout_top_button

        self.load_stl_button = QtWidgets.QPushButton("Load file")
        self.load_stl_button.clicked.connect(self.run)
        layout_top_button.addWidget(self.load_stl_button)

        #self.load_stl_button = QtWidgets.QPushButton("Auto Slicing")
        #self.load_stl_button.clicked.connect(self.add_sphere)
        #layout_top_button.addWidget(self.load_stl_button)


        self.progress_bar1 = QProgressBar(self)
        self.progress_bar1.setRange(0, 100)  # Set the range of the progress bar (0 to 100)
        self.progress_bar1.setValue(0)       # Initial value (starts at 0)
        vlayout.addWidget(self.progress_bar1)

        self.progress_bar2 = QProgressBar(self)
        self.progress_bar2.setRange(0, 100)  # Set the range of the progress bar (0 to 100)
        self.progress_bar2.setValue(0)       # Initial value (starts at 0)
        vlayout.addWidget(self.progress_bar2)



        

        # Create the QtInteractor widget.
        self.vtk_widget = QtInteractor(central_widget)

        self.OBJ_Canvas = self.vtk_widget
        vlayout.addWidget(self.vtk_widget)

        # Add an initial mesh (a red sphere) using the methods of QtInteractor.
        #self.vtk_widget.add_mesh(pv.Sphere(), color="red")
        self.vtk_widget.reset_camera()
        self.vtk_widget.render()

        # Create a horizontal layout for buttons.
        button_layout = QtWidgets.QHBoxLayout()
        vlayout.addLayout(button_layout)

        # Button to add another sphere.
        #self.add_sphere_button = QtWidgets.QPushButton("Add Sphere")
        #self.add_sphere_button.clicked.connect(self.add_sphere)
        #button_layout.addWidget(self.add_sphere_button)

        # Button to close the application.
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)


        #self._progress()
        self.worker = WorkerThread()
        self.worker.progress_signal1.connect(self.progress_bar1.setValue)
        self.worker.progress_signal2.connect(self.progress_bar2.setValue)
        self.worker.start()
    
    def display_mesh(self, mesh, color, name):
        """
        Ensures the mesh conversion and rendering happens in the main GUI thread.
        """
        if self.vtk_widget is None:
            raise ValueError("Viewer is not initialized.")


        self.update_mesh_signal.emit(mesh, color, name)
      
        
        

    @pyqtSlot(object, str, str)
    def update_mesh(self, mesh, color, name):

        vertices = mesh.vertices
        faces = mesh.faces

        faces_pv = np.hstack([[len(f), *f] for f in faces])
        mesh_pv = pv.PolyData(vertices, faces_pv)
        self.vtk_widget.add_mesh(mesh_pv, color=color, name=name,show_edges=True, edge_color="black")
        self.vtk_widget.render()

       
        

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
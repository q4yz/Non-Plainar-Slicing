import sys
import os

import pyvista as pv
from pyvistaqt import QtInteractor

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import  QProgressBar
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, pyqtSlot

import numpy as np


from .viewer_methods_module import ViewerMethoden
from .work_thread_module import WorkerThread
from .settings import *


class MainWindow(ViewerMethoden):



    update_mesh_signal = pyqtSignal(object, str, str)


    def __init__(self, parent=None):
        super().__init__(parent)

        self.update_mesh_signal.connect(self.update_mesh)

        self.setWindowTitle("NonPlainarSlicer")
        self.resize(800, 600)
        self.showMaximized()
        

        icon_path = os.path.abspath("icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowIcon(QIcon('path_to_your_icon.ico'))  # Provide your icon path here
        
        # Create a central widget with a vertical layout.
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        v_layout = QtWidgets.QVBoxLayout(central_widget)


        layout_top_button = QtWidgets.QHBoxLayout()
        v_layout.addLayout(layout_top_button)


        self.settings_button = QtWidgets.QPushButton("Settings")
        self.settings_button.clicked.connect(create_table_window)
        layout_top_button.addWidget(self.settings_button)

        self.load_stl_button = QtWidgets.QPushButton("Load file")
        self.load_stl_button.clicked.connect(self.run)
        layout_top_button.addWidget(self.load_stl_button)

        self.progress_bar1 = QProgressBar(self)
        self.progress_bar1.setRange(0, 100)  # Set the range of the progress bar (0 to 100)
        self.progress_bar1.setValue(0)       # Initial value (starts at 0)
        v_layout.addWidget(self.progress_bar1)

        self.progress_bar2 = QProgressBar(self)
        self.progress_bar2.setRange(0, 100)  # Set the range of the progress bar (0 to 100)
        self.progress_bar2.setValue(0)       # Initial value (starts at 0)
        v_layout.addWidget(self.progress_bar2)

        self.vtk_widget = QtInteractor(central_widget)

        self.OBJ_Canvas = self.vtk_widget
        v_layout.addWidget(self.vtk_widget)

        self.vtk_widget.reset_camera()
        self.vtk_widget.render()

        button_layout = QtWidgets.QHBoxLayout()
        v_layout.addLayout(button_layout)



        self.export_gcode_button = QtWidgets.QPushButton("Save")
        self.export_gcode_button.clicked.connect(self.export_gcode)
        button_layout.addWidget(self.export_gcode_button)



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



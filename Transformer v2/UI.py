
# -*- coding: utf-8 -*-
import numpy as np
import pyvista as pv
import sys
import logging
import threading
import math

#from WidgetActions import *
#from constants import *

#import matplotlib.pyplot as plt


import tkinter as tk
import tkinter
from tkinter import ttk


from canvisViewer  import canvisViewer
from MeshObject import MeshObject

from Constants import *

from ViewerMethoden import *

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import trimesh
from Settings import *

class Viewer(ViewerMethoden):
    """
    This Class saves Viewer Objects and make the layout.
    """

    root = tkinter.Tk()
    #toolbar = None
    meshObject: MeshObject = None 
    OBJ_Canvis : canvisViewer= canvisViewer()

    progressbar = None 
    

    def __init__(self) -> None:
        """

        """
       
        root = self.root
        root.wm_title("MY Slicer")

        root.geometry("1200x1000")  
        #root.attributes("-fullscreen", True)

        self._create_top_frame()
        self._create_middle_frame()
        self._create_bottom_frame()

        tkinter.mainloop()

    def _create_top_frame(self):

        root = self.root

        top_frame : tk.Frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X) 

        button_specs = [
            ("Close", self._quit                    ,0,0),
            ("Settings", create_table_window                ,0,1),
            ("Load", self.load_obj                  ,1,0),
                                                                #("Run", self.run                        ,1,1),
            ("Export Mesh", self.exportMesh         ,1,4),
            ("Import Gcode", self.importGcode       ,1,5),
                                                                #("Transform Gcode", self.transform_Gcode,1,6),
            ("Export Gcode", self.exportGcode       ,1,7),
            ("Split", self.split                    ,1,1),
            ("Slop", self.transTransformerPlain     ,1,2),
            ("Distort", self.distort                ,1,3),
                                                                #("Slice", self.slice                    ,2,5)
        ]
        # Improve
        for  (label, command, row, column) in button_specs:
            button = tk.Button(top_frame, text=label, width=15, command=command)
            button.grid(row=row, column=column, padx=1, pady=2)

        self.progressbar = ttk.Progressbar(master=top_frame)
        progressbar = self.progressbar 
        self._progress()
        progressbar.grid(row=3,column=0,columnspan = 3,sticky="ew")
        
    
    def _create_middle_frame(self):

        root = self.root

        middle_frame = tk.Frame(root, width=800, height=800)
        middle_frame.pack(side=tk.TOP, fill=tk.BOTH)  # Place the frame at the top, fill horizontally

        canvas = FigureCanvasTkAgg(self.OBJ_Canvis.fig, master=middle_frame)  # A tk.DrawingArea.
        canvas.draw()

       
        #canvas.get_tk_widget().pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk( canvas, middle_frame)
        self.toolbar.update()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        canvas.get_tk_widget().config(width=800, height=800)
        canvas.mpl_connect("key_press_event", self.on_key_press)
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.OBJ_Canvis.canvas = canvas

    def _create_bottom_frame(self):

        root = self.root

        bottom_frame = tk.Frame(root)
        bottom_frame.pack(side=tk.TOP, fill=tk.X)  # Place the frame at the top, fill horizontally



logging.basicConfig(level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Set the format for the log messages
                    datefmt='%Y-%m-%d %H:%M:%S',  # Optional: Set the date/time format
                    handlers=[
                        logging.FileHandler("app.log"),  # Output to a file
                        logging.StreamHandler()  # Output to console
                    ])
Viewer() 
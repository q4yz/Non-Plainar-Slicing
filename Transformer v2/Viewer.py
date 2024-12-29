# -*- coding: utf-8 -*-
import numpy as np
import pyvista as pv
import sys
import logging
import threading
import math
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import trimesh

from canvisViewer import CanvisViewer
import mesh_object
from Constants import *
from ViewerMethoden import *
from Settings import *

class Viewer(ViewerMethoden):
    """
    This Class saves Viewer Objects and creates the layout.
    """

    def __init__(self) -> None:
        """
        Initializes the Viewer class, sets up the UI and starts the main loop.
        """
        self.root = tk.Tk()
        self.root.wm_title("MY Slicer")
        self.root.geometry("1200x1000")
        
        self.meshObject: mesh_object.MeshObject = None 
        self.OBJ_Canvas: CanvisViewer = CanvisViewer()

        self._create_top_frame()
        self._create_middle_frame()
        self._create_bottom_frame()

        tk.mainloop()

    def _create_top_frame(self):
        """
        Creates the top frame of the UI with buttons and a progress bar.
        """
        top_frame = tk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        button_specs = [
            ("Close", self._quit, 0, 0),
            ("Settings", create_table_window, 0, 1),
            ("Load", self.load_obj, 1, 0),
            ("Export Mesh", self.exportMesh, 1, 4),
            ("Import Gcode", self.importGcode, 1, 5),
            ("Export Gcode", self.exportGcode, 1, 7),
            ("Split", self.split, 1, 1),
            ("Slop", self.transTransformerPlain, 1, 2),
            ("Distort", self.distort, 1, 3),
        ]

        for (label, command, row, column) in button_specs:
            button = tk.Button(top_frame, text=label, width=15, command=command)
            button.grid(row=row, column=column, padx=1, pady=2)

        self.progressbar = ttk.Progressbar(master=top_frame)
        self._progress()
        self.progressbar.grid(row=3, column=0, columnspan=3, sticky="ew")

    def _create_middle_frame(self):
        """
        Creates the middle frame of the UI where the canvas is displayed.
        """
        middle_frame = tk.Frame(self.root, width=800, height=800)
        middle_frame.pack(side=tk.TOP, fill=tk.BOTH)

        canvas = FigureCanvasTkAgg(self.OBJ_Canvas.fig, master=middle_frame)
        canvas.draw()

        self.toolbar = NavigationToolbar2Tk(canvas, middle_frame)
        self.toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas.get_tk_widget().config(width=800, height=800)
        canvas.mpl_connect("key_press_event", self.on_key_press)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.OBJ_Canvas.canvas = canvas

    def _create_bottom_frame(self):
        """
        Creates the bottom frame of the UI.
        """
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(side=tk.TOP, fill=tk.X)


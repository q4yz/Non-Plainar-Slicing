

import tkinter as tk
import tkinter
from tkinter import filedialog
#from Gcode import *

import mesh_object
import gcode_object


from trimesh.smoothing import filter_laplacian
from tkinter import messagebox
import logging
from threading import Thread
import os
import globals
from settings import *
import numpy as np

import pyvista as pv
from PyQt5.QtCore import QMetaObject, Qt, QObject, pyqtSlot, pyqtSignal, QThread
from time import sleep

import subprocess
import tempfile
import trimesh
from pathlib import Path


class ViewerMethoden():
    """
    Actions from Button Presses
    """

    kill : bool= False
    busy : bool= False
    state : int = 0
    

    def _run_in_thread(self,minState: int,maxState: int, target_method, *args):
        """Helper method to run tasks in a separate thread with a busy check."""
        if self.busy:
            messagebox.showwarning("Warning", "Busy!")
            return
        
        if self.state < minState:
            messagebox.showwarning("Warning", "Pleas take previos Steps!")
            return

        if self.state > maxState:
            messagebox.showwarning("Warning", "Steps alredy taken!")
            return

        self.busy = True

        
        globals.progress = 0

        t = Thread(target=self._run_and_complete, args=(target_method, *args))
        t.start()

    def _run_and_complete(self, target_method, *args):
        """Runs a method and marks it as completed once done."""
        try:
            target_method(*args) 
        finally:
            self.busy = False  
            
            globals.progress = 1
            if hasattr(self, 'meshObject'):          
                self.display_mesh(self.meshObject.mesh, color="blue", name="mesh")

                if hasattr(self.meshObject, 'transformerPlain'):
                    self.display_mesh( self.meshObject.transformerPlain.mesh, color="red", name="plain")



    def load_obj(self):
        self._run_in_thread(0, 10, self._load_obj);

    def run(self):
        self._run_in_thread(0,10,self._run);

    def exportMesh(self):
        self._run_in_thread(4,10, self._exportMesh);

    def importGcode(self):
        self._run_in_thread(5,10, self._importGcode); 

    def exportGcode(self):
        self._run_in_thread(6,10, self._exportGcode);

    def split(self):
        self._run_in_thread(1,1, self._split);

    def transTransformerPlain(self):
        self._run_in_thread(2,10, self._transTransformerPlain);

    def distort(self):
        self._run_in_thread(3,3,self._distort);
           
    def _load_obj(self):    
         
        logging.info("----Button Slop Pressed----") 
        
        totallSteps = 2
        step = 0
        globals.progress2 = step / totallSteps

        file_path = tkinter.filedialog.askopenfile(mode='r',
        initialdir=r'C:\Daten\Test-Slicer\OBJ_IN', 
        filetypes=[('OBJ files', '*.obj'), ('All files', '*.*')]  
        )

        if file_path:

            
            step += 1
            globals.progress2 = step / totallSteps

            print("Selected file:", file_path.name)
            file_path.close()  
            self.meshObject = mesh_object.MeshObject(path = file_path.name )

            maxP = settings['max_p']
            distortionResolution = settings['distortionresolution']
            self.meshObject.createTransformerPlain(distortionResolution, maxP)

            
            
            self.state = 1
        globals.progress2 = 1
        

    def _run(self):
        globals.progress = 0.05

        self._load_obj()
        globals.progress = 0.2
        if not hasattr(self, 'meshObject'):  
            return

        
        self.display_mesh(self.meshObject.mesh, color="blue", name="mesh")
        self.display_mesh( self.meshObject.transformerPlain.mesh, color="red", name="plain")

        self._transTransformerPlain()
        globals.progress = 0.4
        self.display_mesh(self.meshObject.mesh, color="blue", name="mesh")
        self.display_mesh( self.meshObject.transformerPlain.mesh, color="red", name="plain")
                
                    
        self._split()
        globals.progress = 0.6
        self.display_mesh(self.meshObject.mesh, color="blue", name="mesh")
        self.display_mesh( self.meshObject.transformerPlain.mesh, color="red", name="plain")


        self._distort()
        globals.progress = 0.8
        self.display_mesh(self.meshObject.mesh, color="blue", name="mesh")
        self.display_mesh( self.meshObject.transformerPlain.mesh, color="red", name="plain")
       
        path_gcode1 = self.slice()
     

        self.meshObject.gcode = gcode_object.Gcode(path_gcode1,self.meshObject, 0.5)
        globals.progress = 1

        self.state = 6

    def slice (self):
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as temp_stl:
                filter_laplacian(self.meshObject.mesh, lamb=0.1, iterations=10) 
                
                self.meshObject.mesh.export(temp_stl.name)  # Save mesh as STL

                slic3r_path = Path("NonPlainarSlicing/Slic3r-1.3.0.64bit/Slic3r-console.exe")

                slic3r_path = slic3r_path.resolve()
                print(slic3r_path)

                output_gcode = temp_stl.name.replace(".stl", ".gcode")
                subprocess.run([
                    slic3r_path,
                    temp_stl.name,
                    "--output", output_gcode,
                    "--start-gcode", "SET_GCODE_VARIABLE MACRO=START_PRINT VARIABLE=bed_temp VALUE=[first_layer_bed_temperature]\nSET_GCODE_VARIABLE MACRO=START_PRINT VARIABLE=extruder_temp VALUE=[first_layer_temperature]\nSTART_PRINT",
                    "--end-gcode", "END_PRINT",
                    "--first-layer-bed-temperature", "50",
                    "--skirts", "0",
                    "--external-perimeters-first","1",
                    "--before-layer-gcode", ";LAYER:[layer_num]",
                    "--first-layer-height"," 0.3488"
                ], creationflags=subprocess.CREATE_NO_WINDOW)

                print(f"Generated G-code: {output_gcode}")
                return output_gcode
        
    
    def _exportMesh(self):

        save_file_path = filedialog.asksaveasfile(
                mode='w',
                initialdir=r'C:\Daten\Test-Slicer\OBJ_OUT', 
                initialfile="out.obj",
                defaultextension=".obj",
                filetypes=[('Gcode files', '*.obj'), ('All files', '*.*')]
            )

        if save_file_path: 
            self.meshObject.mesh.export(save_file_path.name)
            save_file_path.close()
        self.state = 5

   
    def _importGcode(self):
        pass
        file_path = tkinter.filedialog.askopenfile(mode='r',
        initialdir=r'C:\Daten\Test-Slicer\Gcode_IN',  # Set your default directory path here
        filetypes=[('gcode files', '*.gcode'), ('All files', '*.*')]  # Set .obj as default
        )

        if file_path:
            print("Selected file:", file_path.name)
            selectedPath:str = file_path.name
            file_path.close()  

            self.meshObject.gcode = gcode_object.Gcode(selectedPath,self.meshObject, 0.5)

        self.state = 6
 

    def _exportGcode(self):
        save_file_path = filedialog.asksaveasfile(
                mode='w',
                initialdir=r'C:\Daten\Test-Slicer\Gcode_OUT',  
                initialfile="out.gcode",
                defaultextension=".gcode",
                filetypes=[('Gcode files', '*.gcode'), ('All files', '*.*')]
            )

        if save_file_path: 
            path = save_file_path
            save_file_path.close()
            gcode_object.export(path.name,self.meshObject.gcode.gcode_out )
            

        self.state = 8
   

    def _split(self):
        logging.info("----Button Split Pressed----") 

        
        self.meshObject.splitMeshEdageOnTrans()    
        self.state = 2
      

    def _transTransformerPlain(self):
        logging.info("----Button Slop Pressed----") 

        def option_selected(option):
            root.destroy()  
            if option == 1:
                self.meshObject.xSlop()
            elif option == 2:
                self.meshObject.flattop()
            elif option == 3:
                self.meshObject.noSupport()
            

        root = tk.Tk()
        root.title("Choose an Option")

        root.geometry("400x300")

        label = tk.Label(root, text="Please select an option:", font=("Arial", 14))
        label.pack(pady=10)

        # Add buttons for the three options
        button1 = tk.Button(root, text="Slope", command=lambda: option_selected(1))
        button1.pack(pady=5)
        button2 = tk.Button(root, text="FlatSurface", command=lambda: option_selected(2))
        button2.pack(pady=5)
        button3 = tk.Button(root, text="NoSupport", command=lambda: option_selected(3))
        button3.pack(pady=5)

        root.mainloop()
        #option_selected(1)
        
        self.state = 3
         


    def _distort(self):

        logging.info("----Button Distort Pressed----") 
      
        self.meshObject.distort()
        self.state = 4
      

    def _slice(self):   
        self.meshObject.Slice()
        self.state = 7

    def _quit(self):
        root = self.root
        self.kill = True
        root.quit()     
        root.destroy()  

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.kill = True
            self.root.quit()     
            self.root.destroy()  

class WorkerThread(QThread):
    progress_signal1 = pyqtSignal(int)  # First progress bar signal
    progress_signal2 = pyqtSignal(int)  # Second progress bar signal

    def run(self):
        while not self.isInterruptionRequested():  # Thread-safe exit condition
            p1 = globals.progress * 100
            p2 = globals.progress2 * 100
            self.progress_signal1.emit(int(p1))  # Emit progress for first bar
            self.progress_signal2.emit(int(p2))  # Emit progress for second bar
            sleep(0.01)  # Prevent CPU overuse
            
       

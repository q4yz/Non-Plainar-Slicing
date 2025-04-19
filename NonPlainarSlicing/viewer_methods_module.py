

import tkinter
from tkinter import filedialog

import trimesh
from PyQt5 import QtWidgets, QtCore




import logging
from threading import Thread
import os

from settings import *


import subprocess
import tempfile

from .gcode_utilities.gcode_object import GcodeObject
from .globals import Glob
from .mesh_utilities.mesh_tools import MeshTools


class ViewerMethoden(QtWidgets.QMainWindow):
    """
    Actions from Button Presses
    """

    kill : bool= False
    busy : bool= False
    state : int = 0
    

    def _run_in_thread(self, min_state: int, max_state: int, target_method, *args):
        """Helper method to run tasks in a separate thread with a busy check."""
        if self.busy:
            messagebox.showwarning("Warning", "Busy!")
            return
        
        if self.state < min_state:
            messagebox.showwarning("Warning", "Pleas take previous Steps!")
            return

        if self.state > max_state:
            messagebox.showwarning("Warning", "Steps already taken!")
            return

        self.busy = True

        
        Glob.get_main_tracker().set_progress(0)

        t = Thread(target=self._run_and_complete, args=(target_method, *args))
        t.start()

    def _run_and_complete(self, target_method, *args):
        """Runs a method and marks it as completed once done."""
        try:
            target_method(*args) 
        finally:
            self.busy = False  
            
            Glob.get_main_tracker().set_progress(1)
            if hasattr(self, 'meshObject'):          
                self.display_mesh(self.meshObject.mesh, color="blue", name="mesh")

                if hasattr(self.meshObject, 'transformerPlain'):
                    self.display_mesh( self.meshObject.transformerPlain.mesh, color="red", name="plain")



    def load_obj(self):
        self._run_in_thread(0, 10, self._load_obj)

    def run(self):
        self._run_in_thread(0,10,self._run)

    def export_mesh(self):
        self._run_in_thread(4, 10, self._export_mesh)

    def import_gcode(self):
        self._run_in_thread(5, 10, self._import_gcode)

    def export_gcode(self):
        self._run_in_thread(6, 10, self._export_gcode)

    def split(self):
        self._run_in_thread(1,1, self._split)

    def trans_transformer_plain(self):
        self._run_in_thread(2, 10, self._trans_transformer_plain)

    def distort(self):
        self._run_in_thread(3,3,self._distort)
           
    def _load_obj(self):    
         
        logging.info("----Button Slop Pressed----")

        root = tk.Tk()
        root.withdraw()


        Glob.get_sub_tracker().initialize(2)

        file_path = tkinter.filedialog.askopenfile(mode='r',
        initialdir=r'C:\Daten\Test-Slicer\OBJ_IN', 
        filetypes=[('OBJ files', '*.obj'), ('All files', '*.*')]  
        )
        root.destroy()  # cleanup!

        if file_path:

            Glob.get_sub_tracker().step()

            print("Selected file:", file_path.name)
            file_path.close()  
            #self.meshObject = mesh_object.MeshObject(path = file_path.name )
            # max_p = settings['max_p']
            # distortion_resolution = settings['distortionresolution']
            # self.create_transformer_plain(distortion_resolution, max_p)

            self.mesh = trimesh.load_mesh( file_path.name )
            MeshTools.shift_to_center(self.mesh)
            self.plain = MeshTools.create_plane(self.mesh.bounds, Glob.get_settings(),1.13423231,Glob.get_sub_tracker())



            
            
            self.state = 1
        Glob.get_sub_tracker().step()
        

    def _run(self):


        Glob.get_main_tracker().initialize(6)
        Glob.get_main_tracker().step()

        self._load_obj()
        Glob.get_main_tracker().step()
        if not hasattr(self, 'mesh'):
            return

        
        self.display_mesh(self.mesh, color="blue", name="mesh")
        self.display_mesh( self.plain, color="red", name="plain")

        self._trans_transformer_plain()

        Glob.get_main_tracker().step()
        self.display_mesh(self.mesh, color="blue", name="mesh")
        self.display_mesh(self.plain, color="red", name="plain")

        self._split()

        Glob.get_main_tracker().step()

        self.display_mesh(self.mesh, color="blue", name="mesh")

        self.display_mesh(self.plain, color="red", name="plain")

        self._distort()

        Glob.get_main_tracker().step()
        self.display_mesh(self.mesh, color="blue", name="mesh")
        self.display_mesh(self.plain, color="red", name="plain")
       
        path_gcode1 = self.slice()

        self.g = GcodeObject(path_gcode1)
        self.g.move_to_center()
        self.g.segment_lines(0.5)
        self.g.transform_back_gcode_on_plain(self.plain)
        self.g.move_to_original_position()



        #self.meshObject.gcode = gcode_object.Gcode(path_gcode1,self.meshObject, 0.5)
        Glob.get_main_tracker().step()

        self.state = 6

    def slice (self):
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as temp_stl:

                self.mesh.export(temp_stl.name)  # Save mesh as STL

                slic3r_path = os.path.abspath(os.path.join("..","external_tools", "Slic3r-1.3.0.64bit", "Slic3r-console.exe"))

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
        
    
    def _export_mesh(self):

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

   
    def _import_gcode(self):

        raise "nicht mehr aktuell"

        file_path = tkinter.filedialog.askopenfile(mode='r',
        initialdir=r'C:\Daten\Test-Slicer\Gcode_IN',  # Set your default directory path here
        filetypes=[('gcode files', '*.gcode'), ('All files', '*.*')]  # Set .obj as default
        )

        if file_path:
            print("Selected file:", file_path.name)
            selectedPath:str = file_path.name
            file_path.close()  


            #self.meshObject.gcode = gcode_object.Gcode(selectedPath,self.meshObject, 0.5)

        self.state = 6
 

    def _export_gcode(self):
        save_file_path = filedialog.asksaveasfile(
                mode='w',
                initialdir=r'C:\Daten\Test-Slicer\Gcode_OUT',  
                initialfile="out.gcode",
                defaultextension=".gcode",
                filetypes=[('Gcode files', '*.gcode'), ('All files', '*.*')]
            )

        if save_file_path: 
            path = save_file_path.name
            save_file_path.close()
            self.g.export(path)

            

        self.state = 8
   

    def _split(self):
        logging.info("----Button Split Pressed----") 

        MeshTools.split_mesh_on_edges_from_plain(self.plain, self.mesh, Glob.get_main_tracker())
        #self.meshObject.split_mesh_edge_on_trans()
        self.state = 2
      

    def _trans_transformer_plain(self):
        logging.info("----Button Slop Pressed----") 

        def option_selected(option):
            root.destroy()  
            if option == 1:
                MeshTools.transform_plain_slop(self.plain, self.mesh, Glob.get_settings(),Glob.get_sub_tracker())
                #self.meshObject.xSlop()
            elif option == 2:
                MeshTools.transform_smooth_surface(self.plain, self.mesh, Glob.get_settings(),Glob.get_sub_tracker())
                #self.meshObject.flattop()
            elif option == 3:
                MeshTools.transform_avoid_overhangs(self.plain, self.mesh, Glob.get_settings(), Glob.get_sub_tracker())
                #self.meshObject.noSupport()
            

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
        MeshTools.distort_mesh_on_plain(self.plain, self.mesh, Glob.get_sub_tracker())
        #self.meshObject.distort()
        self.state = 4


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



       

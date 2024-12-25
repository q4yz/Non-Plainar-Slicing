
from time import sleep
import tkinter as tk
import tkinter
from tkinter import filedialog
from tkinter import ttk
from Gcode import *
from MeshObject import MeshObject
import trimesh

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from tkinter import messagebox
import logging
from threading import Thread
import os
from Constants import *


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

        global progress
        progress = 0

        t = Thread(target=self._run_and_complete, args=(target_method, *args))
        t.start()

    def _run_and_complete(self, target_method, *args):
        """Runs a method and marks it as completed once done."""
        try:
            target_method(*args) 
        finally:
            self.busy = False  
            global progress
            progress = 1



    def load_obj(self):
        self._run_in_thread(0, 10, self._load_obj);

    #def run(self):
    #    self._run_in_thread(1,self._run);

    def exportMesh(self):
        self._run_in_thread(4,10, self._exportMesh);

    def importGcode(self):
        self._run_in_thread(5,10, self._importGcode); 

    def exportGcode(self):
        self._run_in_thread(7,10, self._exportGcode);

    #def transform_Gcode(self):
    #    self._run_in_thread(6,self._transform_Gcode);

    def split(self):
        self._run_in_thread(1,1, self._split);

    def transTransformerPlain(self):
        self._run_in_thread(2,10, self._transTransformerPlain);

    def distort(self):
        self._run_in_thread(3,3,self._distort);

    #def slice(self):
    #    self._run_in_thread(4,self._slice);
    
           
    def _load_obj(self):    
         
        logging.info("----Button Slop Pressed----") 
        global progress
        totallSteps = 2
        step = 0
        progress = step / totallSteps

        file_path = tkinter.filedialog.askopenfile(mode='r',
        initialdir=r'C:\Daten\Test-Slicer\OBJ_IN', 
        filetypes=[('OBJ files', '*.obj'), ('All files', '*.*')]  
        )

        if file_path:

            
            step += 1
            progress = step / totallSteps

            print("Selected file:", file_path.name)
            file_path.close()  
            self.meshObject = MeshObject(path = file_path.name, viewer = self.OBJ_Canvis )

            
            
            self.state = 1

        progress = 1

        
    

    #def _run(self):
    #    self._split()
    #    self._transTransformerPlain()
    #    self._distort()
    #    self.state = 4

 
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

            self.meshObject.gcode = Gcode(selectedPath,self.meshObject)

        self.state = 6
 

    #def _transform_Gcode(self):
    #    self.state = 7
   

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
            self.meshObject.gcode.export(path)

            #save_file_path.write(self.meshObject.gcodePreTransformed)
            


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
        button1 = tk.Button(root, text="slop", command=lambda: option_selected(1))
        button1.pack(pady=5)
        button2 = tk.Button(root, text="FlatSurface", command=lambda: option_selected(2))
        button2.pack(pady=5)
        button3 = tk.Button(root, text="NoSupport", command=lambda: option_selected(3))
        button3.pack(pady=5)

        root.mainloop()
        
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

    def _progress(self):
        t = Thread(target=self.action_progress, args=[])
        t.start()

    def on_key_press(self, event):
        return
      
    def action_progress(self):

        while not self.kill:
            
 
            global progress
            p = progress * 100
        
            self.progressbar['value'] = p
            sleep(0.01)

            
       

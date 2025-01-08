import numpy as np

import mesh_object


from .utils import *
from .file_read import *
from .file_write import *


class Gcode():

    outCommands = []

    def __init__(self, path, meshobject) -> None:
        
        #path = r'C:\Daten\Test-Slicer\Gcode_IN\CFFFP_out.gcode'

        commandList = readGcodeFileToDicList(path)
        
        commandListidexOfPoints, commandListPoints = getPointsFromCommands(commandList)
        commandListidexOfPoints, commandListPoints = segmentizeLines(commandListidexOfPoints, commandListPoints, 0.5)        

        offset = getOffsetFormOrigan(commandList, commandListidexOfPoints, commandListPoints)

        shiftPoints(commandListPoints, -offset )

        commandListPoints = self.zBackTrans(commandListPoints, meshobject)

        
        shiftPoints(commandListPoints, offset )
        
        printTofile(commandList, commandListidexOfPoints, commandListPoints )

    


    def zBackTrans(self, commandListPoints, mesh:mesh_object.MeshObject):
        print("start - zBackTrans")
        locations, index_ray = mesh.distortOnTrans(commandListPoints[:,:3])

        np.set_printoptions(precision=4, suppress=True, edgeitems=8)  
   
        commandListPoints[index_ray, 2] = commandListPoints[index_ray, 2] -  locations[:, 2]
        print("end - zBackTrans")
        return commandListPoints





    

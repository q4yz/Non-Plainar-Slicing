import numpy as np

import mesh_object


from .utils import *
from .file_read import *
from .file_write import *


class Gcode():

    outCommands = []
    offset = []

    def __init__(self, path, meshobject) -> None:
        
        #path = r'C:\Daten\Test-Slicer\Gcode_IN\CFFFP_out.gcode'

        commandList = readGcodeFileToDicList(path)
        
        commandListidexOfPoints, commandListPoints, maskIsMesh = getPointsFromCommands(commandList)
        offset = getOffsetFormOrigan(commandList, commandListidexOfPoints[maskIsMesh], commandListPoints[maskIsMesh])

        commandListidexOfPoints, commandListPoints = segmentizeLines(commandListidexOfPoints, commandListPoints, 0.5)    

        shiftPoints(commandListPoints, -offset )

        commandListPoints = self.zBackTrans(commandListPoints, meshobject)
        print("z min")
        z_min = np.min(commandListPoints[:,2])
        if z_min  < -1:
            raise ZMinCollisionException(z_min) 
        elif z_min < 0:
            offset[2] =  -z_min

        shiftPoints(commandListPoints, offset )
        
        printTofile(commandList, commandListidexOfPoints, commandListPoints )

    


    def zBackTrans(self, commandListPoints, mesh:mesh_object.MeshObject):
        print("start - zBackTrans")
        locations, index_ray = mesh.distortOnTrans(commandListPoints[:,:3])

        
        commandListPoints[index_ray, 2] = commandListPoints[index_ray, 2] -  locations[:, 2]
        print("end - zBackTrans")
        return commandListPoints


    
class ZMinCollisionException(Exception):
    def __init__(self, z_min):
        self.z_min = z_min
        super().__init__(self.__str__())

    def __str__(self):
        return (
            f"Z Min is under 0: {self.z_min}. Zozze would collide with the build plate. "
            "Check if you have the correct G-code."
        )
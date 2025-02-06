import numpy as np

import mesh_object


from .utils import *
from .file_read import *
from .file_write import *

import globals


class Gcode():

    outCommands = []
    offset = []

    def __init__(self, path : str, meshobject , l: float) -> None:
       

        commandList = readGcodeFileToDicList(path)
        globals.progress = 0.1
        commandListidexOfPoints, commandListPoints, maskIsMesh = getPointsFromCommands(commandList)
        globals.progress = 0.2
        offset = getOffsetFormOrigan(commandList, commandListidexOfPoints[maskIsMesh], commandListPoints[maskIsMesh])
        globals.progress = 0.3
        commandListidexOfPoints, commandListPoints = segmentizeLines(commandListidexOfPoints, commandListPoints,l)    
        globals.progress = 0.4
        shiftPoints(commandListPoints, -offset )
        globals.progress = 0.5
        commandListPoints = self.zBackTrans(commandListPoints, meshobject)
        print("z min")
        z_min = np.nanmin(commandListPoints[:, 2])
        
        offset[2] =  -z_min +0.3

        shiftPoints(commandListPoints, offset )
        globals.progress = 0.6
        z_min = np.nanmin(commandListPoints[:, 2])
        if z_min < 0:
            raise ZMinCollisionException(z_min) 

        
        printTofile(commandList, commandListidexOfPoints, commandListPoints )
        globals.progress = 0.9

    


    def zBackTrans(self, commandListPoints, mesh:mesh_object.MeshObject):
        print("start - zBackTrans")
        mask = ~np.any(np.isnan(commandListPoints),axis=1)

        locations, index_ray = mesh.distortOnTrans(commandListPoints[mask,:3])

        #commandListPoints[mask][index_ray, 2] -= locations[:, 2]
        commandListPoints[np.where(mask)[0][index_ray], 2] -= locations[:, 2]
        #commandListPoints[mask][index_ray, 2] = commandListPoints[mask][index_ray, 2] -  locations[:, 2]
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

